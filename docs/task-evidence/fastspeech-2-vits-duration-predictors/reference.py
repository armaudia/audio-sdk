# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for the FastSpeech 2 / VITS
duration-predictor feasibility row (SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS).

This module never loads a model, imports an upstream package, reads audio, runs
duration prediction, scores duration accuracy, performs listening, measures a
device or produces a release claim. The exact FastSpeech 2 and VITS source
trees, checkpoint bundles and runtimes are absent. The module pins stable
read-only inputs, proves the fixed absence probes, exercises a fail-closed
synthetic cohort-admission contract, records the text-conditioned interface
mismatch against the Rate profile and emits canonical JSON.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/fastspeech-2-vits-duration-predictors/"

TASK = "SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS"
TASK_TITLE = "FastSpeech 2 / VITS duration predictors"
COMPONENT_ID = "fastspeech-2-vits-duration-predictors"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_KEY = "Rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = ("audio-sdk/fastspeech-2-vits-duration-predictors-readiness/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/fastspeech-2-vits-duration-predictors-contract/0.1")
REPORT_SCHEMA_ID = (
    "audio-sdk/fastspeech-2-vits-duration-predictors-report/0.1")
BASE_COMMIT = "01ab6b53b2e435ce85b67b6c5d5551eabb877352"
BRANCH = "swarm/SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SYMBOL = re.compile(r"^[A-Za-z0-9_.'\-]{1,32}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to AUDIO_ROOT; boundary
# paths are SDK-worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-text/REPORT.md":
        "86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
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
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Measure source/output mapping",
    "duration",
    "pitch",
    "transient audibility",
    "playback buffering",
    "1\u00d7",
    "rate changes",
    "unfamiliar speech",
    "music",
    "silence",
    "rebuffer",
    "drift",
    "final partial window",
    "pause or filler decisions tied to source timestamps",
    "measure speech preservation",
)

# ---------------------------------------------------------------------------
# Exact upstream identity requirements. No revision, digest, file name or
# license is asserted as present or verified; these are requirements for the
# missing artifacts.
# ---------------------------------------------------------------------------

FASTSPEECH2_SOURCE_REPOSITORY = "https://github.com/espnet/espnet"
FASTSPEECH2_MODULE = "espnet2/tts/fastspeech2/fastspeech2.py"
FASTSPEECH2_UPSTREAM_LEAD = "https://github.com/ming024/FastSpeech2"
VITS_SOURCE_REPOSITORY = "https://github.com/jaywalnut310/vits"
CHECKPOINT_REQUIREMENT_EXAMPLE = (
    "caller-selected FastSpeech 2 and VITS checkpoints (for example an LJSpeech "
    "FastSpeech2 model and an LJSpeech VITS model)")
DURATION_UNIT = "acoustic_frames"

SOURCE_PROBE_PATHS = (
    "research/tsm-followup-20261101/repos/fastspeech2",
    "research/tsm-followup-20261101/repos/FastSpeech2",
    "research/tsm-followup-20261101/repos/vits",
    "research/tsm-followup-20261101/repos/VITS",
    "research/voice-conversion-eval-20261101/repos/vits",
    "research/fastspeech2",
    "research/vits",
)
WEIGHTS_PROBE_PATHS = (
    "research/tsm-followup-20261101/checkpoints/fastspeech2",
    "research/tsm-followup-20261101/checkpoints/vits",
    "research/voice-conversion-eval-20261101/checkpoints/vits",
    "research/models/fastspeech2",
    "research/models/vits",
)
RUNTIME_PROBE_PATHS = (
    "research/tsm-followup-20261101/envs/tts",
    "research/tsm-followup-20261101/.venv-tts",
    ".venv-tts",
)
HOME_PROBE_PATHS = (
    "~/.cache/huggingface/hub/models--facebook--mms-tts-eng",
    "~/.cache/huggingface/hub/models--espnet--espnet2_ljspeech_fastspeech2",
    "~/.cache/huggingface/hub/models--coqui--tts",
    "~/.venvs/tts",
    "~/.local/share/fastspeech2",
    "~/.local/share/vits",
)
SOURCE_ROOT_REL = "research/tsm-followup-20261101"
SECONDARY_SOURCE_ROOT_REL = "research/voice-conversion-eval-20261101/repos"

NON_CLAIMS = [
    "No FastSpeech 2 or VITS source copy, checkpoint, weight fragment, config, "
    "phoneme set, duration statistic, runtime or vendor result is present, "
    "loaded, linked or executed by this package.",
    "No duration prediction, text normalization, audio read, audio write, "
    "pitch measurement, transient measurement, playback buffering measurement, "
    "listening, device timing or benchmark is performed.",
    "No real corpus, training text, phoneme alignment, reference duration "
    "label, language group, rate-change case or held-out split is used here.",
    "No missing, invalid, nonfinite or adverse manifest case qualifies; the "
    "single accepted synthetic schema control is not evidence.",
    "No adjacent TTS model, duration planner, VAD pause rule, syllable-rate "
    "estimator or time-stretch result is inherited, pooled or promoted to "
    "either predictor.",
    "No duration accuracy, speech preservation, pitch, buffering, latency, "
    "resource, streaming or release claim is made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; the absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "f5-tts",
        "task": "SDK-F5-TTS",
        "path": "docs/task-evidence/f5-tts/report.json",
        "class": "adjacent_tts_model_blocker",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Adjacent reference-conditioned TTS blocker. It contains no "
                    "duration predictor, checkpoint, runtime, duration label or "
                    "measured duration, and nothing is inherited.",
    },
    {
        "component": "d1-whole-clip-duration-planner",
        "task": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER",
        "path": "docs/task-evidence/d1-whole-clip-duration-planner/README.md",
        "class": "adjacent_synthetic_rate_planner",
        "decision": "not_qualified",
        "status": "synthetic_proposal_only",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A synthetic exact-rational source-to-playback schedule "
                    "planner with no model and no text-conditioned duration "
                    "predictor; no schedule, rate or timing value is inherited.",
    },
    {
        "component": "silero-vad-pause-duration-rules",
        "task": "SDK-SILERO-VAD-PAUSE-DURATION-RULES",
        "path": "docs/task-evidence/silero-vad-pause-duration-rules/report.json",
        "class": "adjacent_pause_duration_policy",
        "decision": "DEFER",
        "status": "proposal_only_synthetic_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A pause/silence duration policy over VAD timelines, not a "
                    "phoneme duration predictor; no pause threshold, label or "
                    "timing is inherited.",
    },
    {
        "component": "usc-mrate",
        "task": "SDK-USC-MRATE",
        "path": "docs/task-evidence/usc-mrate/report.json",
        "class": "adjacent_audio_side_rate_estimator",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "An audio-side syllable-rate estimator with an unlicensed "
                    "source archive. It estimates incoming-audio rate instead of "
                    "predicting synthesized phoneme durations, and no metric is "
                    "inherited.",
    },
    {
        "component": "bungee-basic",
        "task": "SDK-BUNGEE-BASIC",
        "path": "docs/task-evidence/bungee-basic/report.json",
        "class": "adjacent_rate_actuator",
        "decision": "not_recorded",
        "status": "proposal_only_synthetic_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A time-stretch actuator that changes playback duration. It "
                    "neither predicts phoneme durations nor supplies duration "
                    "labels, and no rate or timing value is inherited.",
    },
)

RATE_REQUIREMENTS = (
    {
        "id": "RATE-01",
        "requirement": "Measure source/output mapping.",
        "status": "blocked",
        "evidence": "No predictor, checkpoint or runtime is present, so no "
                    "source interval, token or frame maps to an output.",
    },
    {
        "id": "RATE-02",
        "requirement": "Measure duration.",
        "status": "blocked",
        "evidence": "No predicted or reference phoneme duration exists; no "
                    "integer frame count is produced or scored.",
    },
    {
        "id": "RATE-03",
        "requirement": "Measure pitch.",
        "status": "blocked",
        "evidence": "No synthesized or played waveform exists, so no pitch "
                    "trajectory or shift is measured.",
    },
    {
        "id": "RATE-04",
        "requirement": "Measure transient audibility.",
        "status": "blocked",
        "evidence": "No rendering or playback path exists, so no transient is "
                    "generated, retained or heard.",
    },
    {
        "id": "RATE-05",
        "requirement": "Measure playback buffering.",
        "status": "blocked",
        "evidence": "No buffer, scheduler, callback or device queue is present "
                    "or exercised.",
    },
    {
        "id": "RATE-06",
        "requirement": "Cover 1\u00d7, rate changes, unfamiliar speech, music, "
                       "silence, rebuffer, drift and the final partial window.",
        "status": "blocked",
        "evidence": "No frozen permitted cohort and no predictor output exist, "
                    "so none of the required conditions is covered.",
    },
    {
        "id": "RATE-07",
        "requirement": "Keep pause or filler decisions tied to source "
                       "timestamps.",
        "status": "blocked",
        "evidence": "No source-timestamped pause or filler decision is made; "
                    "the text-side predictor has no incoming-audio timestamps.",
    },
    {
        "id": "RATE-08",
        "requirement": "Measure speech preservation.",
        "status": "blocked",
        "evidence": "No audio is produced, transformed or compared, so no "
                    "speech-preservation result exists.",
    },
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
        "title": TASK_TITLE,
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
        present = ((AUDIO_ROOT / relative).exists()
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
        "source_root_present": (AUDIO_ROOT / SOURCE_ROOT_REL).is_dir(),
        "secondary_source_root": SECONDARY_SOURCE_ROOT_REL,
        "secondary_source_root_present":
            (AUDIO_ROOT / SECONDARY_SOURCE_ROOT_REL).is_dir(),
        "candidates": _workspace_rows(SOURCE_PROBE_PATHS, "source"),
    }


def weights_probe() -> dict:
    return {
        "status": "blocked_exact_model_bundle_absent",
        "pinned_model_present": False,
        "admitted_model": None,
        "present_file_count": 0,
        "checkpoint_requirement": CHECKPOINT_REQUIREMENT_EXAMPLE,
        "candidates": _workspace_rows(WEIGHTS_PROBE_PATHS, "weights"),
        "files": [
            {"kind": "fastspeech2_weights", "present": False, "admitted": False},
            {"kind": "vits_weights", "present": False, "admitted": False},
            {"kind": "config", "present": False, "admitted": False},
            {"kind": "phoneme_set", "present": False, "admitted": False},
            {"kind": "duration_statistics", "present": False, "admitted": False},
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
        "required_runtime": "caller-supplied locked interpreter with torch and "
                            "the checkpoint package set; exact version and "
                            "packages are not asserted here",
        "candidates": _workspace_rows(RUNTIME_PROBE_PATHS, "runtime"),
        "home_candidates": _home_rows(
            ("~/.venvs/tts", "~/.local/share/fastspeech2",
             "~/.local/share/vits")),
    }


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    rows.extend(_workspace_rows(SOURCE_PROBE_PATHS, "source"))
    rows.extend(_workspace_rows(WEIGHTS_PROBE_PATHS, "weights"))
    rows.extend(_workspace_rows(RUNTIME_PROBE_PATHS, "runtime"))
    rows.extend(_home_rows(HOME_PROBE_PATHS))
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
# Task geometry. Both named modules consume text-side representations and
# predict synthesized phoneme durations; neither has an incoming-audio path.
# ---------------------------------------------------------------------------


def task_geometry() -> dict:
    return {
        "status": "blocked_interface_mismatch",
        "profile": PROFILE_KEY,
        "task_kind": "tts_phoneme_duration_predictor",
        "predictor_inputs": ["text", "phoneme_ids", "text_encoder_states"],
        "predictor_output": "per_token_duration_frames",
        "duration_unit": DURATION_UNIT,
        "duration_to_time":
            "token_duration_frames * checkpoint_hop_length / "
            "checkpoint_sample_rate",
        "consumes_incoming_audio": False,
        "input_audio_rate_controller": False,
        "text_conditioned_not_audio_conditioned": True,
        "public_v0_provider_accepts_text": False,
        "adapter_boundary_available": False,
        "adapter_boundary_requirement":
            "No installed v0 provider boundary accepts text, phoneme ids or "
            "encoder states; the v0 callback consumes float32 audio frames.",
        "blocked_reason_code":
            "duration_predictor_is_text_conditioned_not_audio_conditioned",
        "qualifies": False,
    }


def model_geometry() -> dict:
    return {
        "task_kind": "tts_phoneme_duration_predictor",
        "inputs": ["text", "phoneme_ids", "text_encoder_states"],
        "output": "per_token_duration_frames",
        "duration_unit": DURATION_UNIT,
        "consumes_incoming_audio": False,
        "input_audio_rate_estimator": False,
        "sample_rate_hz": None,
        "sample_rate_requirement":
            "checkpoint-specific acoustic sample rate and hop length recorded "
            "with the exact bundle",
        "channels": None,
        "sample_format": None,
        "installed_v0": False,
        "provider_registered": False,
        "streaming_geometry_pinned": False,
        "generated_length_not_identity": True,
    }


# ---------------------------------------------------------------------------
# Fail-closed synthetic duration-cohort admission contract.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = (
    "audio-sdk/fastspeech-2-vits-duration-predictors-cohort/0.1")
MANIFEST_CONTRACT_ID = (
    "audio-sdk/fastspeech-2-vits-duration-predictors-cohort-contract/0.1")
MANIFEST_TOP_KEYS = (
    "schema_id", "cohort_id", "predictors", "runtime", "items", "controls",
    "outcomes", "rights",
)
MAX_PREDICTORS = 4
MAX_ITEMS = 10_000
MAX_TOKENS_PER_ITEM = 2_000
MAX_TOKEN_FRAMES = 100_000
MAX_ITEM_FRAMES = 10_000_000
MAX_PACKAGES = 128
MAX_CHECKPOINT_BYTES = 8 * 1024 * 1024 * 1024
MAX_TEXT_CHARS = 2_000
ALLOWED_FAMILIES = ("fastspeech2", "vits")
ALLOWED_INPUT_KINDS = (
    "phoneme_ids", "phoneme_ids_encoder_states", "text_token_ids",
)
ALLOWED_DURATION_UNITS = (DURATION_UNIT,)
REQUIRED_FAMILIES = ("fastspeech2", "vits")
UNRESOLVED_VALUES = {
    "unknown", "pending", "unspecified", "not specified", "not-specified",
    "tbd", "none", "null", "n/a", "noassertion",
}
CONTROL_NAMES = (
    "identity_baseline", "constant_duration", "shuffled_tokens", "rate_change",
    "silence_and_partial_window", "unfamiliar_speech_and_music",
)
OUTCOME_NAMES = (
    "duration_error", "duration_sum_consistency", "source_output_mapping",
    "speech_preservation", "pitch", "transient_audibility",
    "playback_buffering", "nonfinite_rejection", "device_timing",
)
RIGHT_NAMES = (
    "code_license", "weight_terms", "training_data_provenance",
    "corpus_license", "output_use", "redistribution",
)


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


def _check_geometry(predictor: dict, prefix: str) -> None:
    """Reject any manifest that pretends a duration predictor reads audio."""
    if predictor["consumes_incoming_audio"] is not False:
        raise _Invalid("geometry_mismatch",
                       prefix + ".consumes_incoming_audio")
    if predictor["duration_unit"] not in ALLOWED_DURATION_UNITS:
        raise _Invalid("geometry_mismatch", prefix + ".duration_unit")


def validate_manifest(document: Any) -> dict:
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object", "")
    try:
        _exact_object(document, MANIFEST_TOP_KEYS, "")
        checks += 1
        if document["schema_id"] != MANIFEST_SCHEMA_ID:
            raise _Invalid("invalid_schema_id", "schema_id")
        checks += 1
        _slug(document["cohort_id"], "cohort_id")
        checks += 1

        predictors = _list(document["predictors"], "predictors", 2,
                           MAX_PREDICTORS)
        for index, item in enumerate(predictors):
            prefix = "predictors[" + str(index) + "]"
            _exact_object(item, (
                "id", "family", "repository", "revision", "license_spdx",
                "license_sha256", "checkpoint_sha256", "checkpoint_bytes",
                "input_kind", "consumes_incoming_audio", "duration_unit",
            ), prefix)
            _slug(item["id"], prefix + ".id")
            if item["family"] not in ALLOWED_FAMILIES:
                raise _Invalid("invalid_value", prefix + ".family")
            _text(item["repository"], prefix + ".repository", 200)
            _hex40(item["revision"], prefix + ".revision")
            _text(item["license_spdx"], prefix + ".license_spdx", 80)
            _sha(item["license_sha256"], prefix + ".license_sha256")
            _sha(item["checkpoint_sha256"], prefix + ".checkpoint_sha256")
            _bounded_int(item["checkpoint_bytes"], 1, MAX_CHECKPOINT_BYTES,
                         prefix + ".checkpoint_bytes")
            if item["input_kind"] not in ALLOWED_INPUT_KINDS:
                raise _Invalid("invalid_value", prefix + ".input_kind")
            _boolean(item["consumes_incoming_audio"],
                     prefix + ".consumes_incoming_audio")
            _check_geometry(item, prefix)
            checks += 9
        _sorted_unique(predictors, "id", "predictors")
        checks += 1
        families = [item["family"] for item in predictors]
        for family in REQUIRED_FAMILIES:
            if families.count(family) != 1:
                raise _Invalid("missing_required_value", "predictors")
        checks += 1

        runtime = _exact_object(
            document["runtime"],
            ("python_version", "lock_sha256", "offline_load", "packages"),
            "runtime")
        _version(runtime["python_version"], "runtime.python_version")
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
        checks += 3
        if not runtime["offline_load"]:
            raise _Invalid("non_offline_runtime", "runtime.offline_load")

        items = _list(document["items"], "items", 1, MAX_ITEMS)
        for index, item in enumerate(items):
            prefix = "items[" + str(index) + "]"
            _exact_object(item, (
                "id", "text", "language", "split", "tokens",
                "reference_total_frames", "predicted_total_frames",
            ), prefix)
            _slug(item["id"], prefix + ".id")
            _text(item["text"], prefix + ".text", MAX_TEXT_CHARS)
            _text(item["language"], prefix + ".language", 80)
            if item["split"] not in ("dev", "test", "heldout"):
                raise _Invalid("invalid_value", prefix + ".split")
            tokens = _list(item["tokens"], prefix + ".tokens", 1,
                           MAX_TOKENS_PER_ITEM)
            reference_total = 0
            predicted_total = 0
            for token_index, token in enumerate(tokens):
                token_prefix = prefix + ".tokens[" + str(token_index) + "]"
                _exact_object(token, ("symbol", "reference_frames",
                                      "predicted_frames"), token_prefix)
                symbol = token["symbol"]
                if not isinstance(symbol, str) or not SYMBOL.fullmatch(symbol):
                    raise _Invalid("invalid_value", token_prefix + ".symbol")
                _bounded_int(token["reference_frames"], 1, MAX_TOKEN_FRAMES,
                             token_prefix + ".reference_frames")
                _bounded_int(token["predicted_frames"], 1, MAX_TOKEN_FRAMES,
                             token_prefix + ".predicted_frames")
                reference_total += token["reference_frames"]
                predicted_total += token["predicted_frames"]
                checks += 3
            _bounded_int(item["reference_total_frames"], 1, MAX_ITEM_FRAMES,
                         prefix + ".reference_total_frames")
            _bounded_int(item["predicted_total_frames"], 1, MAX_ITEM_FRAMES,
                         prefix + ".predicted_total_frames")
            if item["reference_total_frames"] != reference_total:
                raise _Invalid("duration_sum_mismatch",
                               prefix + ".reference_total_frames")
            if item["predicted_total_frames"] != predicted_total:
                raise _Invalid("duration_sum_mismatch",
                               prefix + ".predicted_total_frames")
            checks += 3
        _sorted_unique(items, "id", "items")
        checks += 1

        controls = _exact_object(document["controls"], CONTROL_NAMES,
                                 "controls")
        for name in CONTROL_NAMES:
            _boolean(controls[name], "controls." + name)
            if not controls[name]:
                raise _Invalid("missing_required_value", "controls." + name)
            checks += 1

        outcomes = _exact_object(document["outcomes"], OUTCOME_NAMES,
                                 "outcomes")
        for name in OUTCOME_NAMES:
            _boolean(outcomes[name], "outcomes." + name)
            if not outcomes[name]:
                raise _Invalid("missing_required_value", "outcomes." + name)
            checks += 1

        rights = _exact_object(document["rights"], RIGHT_NAMES, "rights")
        for name in RIGHT_NAMES:
            _boolean(rights[name], "rights." + name)
            if not rights[name]:
                raise _Invalid("rights_not_cleared", "rights." + name)
            checks += 1
    except _Invalid as error:
        return _reject(error.code, error.field)
    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "duration-synthetic-schema-control",
        "predictors": [
            {
                "id": "fastspeech2-control",
                "family": "fastspeech2",
                "repository": FASTSPEECH2_SOURCE_REPOSITORY,
                "revision": "0" * 40,
                "license_spdx": "Apache-2.0",
                "license_sha256": "1" * 64,
                "checkpoint_sha256": "2" * 64,
                "checkpoint_bytes": 1024,
                "input_kind": "phoneme_ids_encoder_states",
                "consumes_incoming_audio": False,
                "duration_unit": DURATION_UNIT,
            },
            {
                "id": "vits-control",
                "family": "vits",
                "repository": VITS_SOURCE_REPOSITORY,
                "revision": "3" * 40,
                "license_spdx": "MIT",
                "license_sha256": "4" * 64,
                "checkpoint_sha256": "5" * 64,
                "checkpoint_bytes": 2048,
                "input_kind": "phoneme_ids",
                "consumes_incoming_audio": False,
                "duration_unit": DURATION_UNIT,
            },
        ],
        "runtime": {
            "python_version": "3.11.0",
            "lock_sha256": "6" * 64,
            "offline_load": True,
            "packages": [{"name": "torch", "version": "2.6.0"}],
        },
        "items": [
            {
                "id": "item-01",
                "text": "Synthetic schema control text, not evidence.",
                "language": "en",
                "split": "dev",
                "tokens": [
                    {"symbol": "AH0", "reference_frames": 4,
                     "predicted_frames": 4},
                    {"symbol": "B", "reference_frames": 3,
                     "predicted_frames": 5},
                ],
                "reference_total_frames": 7,
                "predicted_total_frames": 9,
            }
        ],
        "controls": {name: True for name in CONTROL_NAMES},
        "outcomes": {name: True for name in OUTCOME_NAMES},
        "rights": {name: True for name in RIGHT_NAMES},
    }


def _mutation_case(case_id: str, mutate: Any, code: str) -> dict:
    manifest = copy.deepcopy(_manifest_control())
    mutate(manifest)
    result = validate_manifest(manifest)
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


def _mutation_cases() -> list[dict]:
    def set_family(manifest: dict) -> None:
        manifest["predictors"][0]["family"] = "tacotron"

    def single_family(manifest: dict) -> None:
        manifest["predictors"] = [manifest["predictors"][0]]

    def audio_consuming(manifest: dict) -> None:
        manifest["predictors"][0]["consumes_incoming_audio"] = True

    def wrong_unit(manifest: dict) -> None:
        manifest["predictors"][0]["duration_unit"] = "samples"

    def boolean_bytes(manifest: dict) -> None:
        manifest["predictors"][0]["checkpoint_bytes"] = True

    def zero_bytes(manifest: dict) -> None:
        manifest["predictors"][0]["checkpoint_bytes"] = 0

    def empty_tokens(manifest: dict) -> None:
        item = manifest["items"][0]
        item["tokens"] = []
        item["reference_total_frames"] = 1
        item["predicted_total_frames"] = 1

    def zero_duration(manifest: dict) -> None:
        manifest["items"][0]["tokens"][0]["predicted_frames"] = 0

    def non_integer(manifest: dict) -> None:
        manifest["items"][0]["tokens"][0]["predicted_frames"] = 4.5

    def sum_mismatch(manifest: dict) -> None:
        manifest["items"][0]["predicted_total_frames"] += 1

    def duplicate_item(manifest: dict) -> None:
        duplicate = copy.deepcopy(manifest["items"][0])
        duplicate["text"] = "Second synthetic control text, not evidence."
        manifest["items"].append(duplicate)

    def duplicate_package(manifest: dict) -> None:
        manifest["runtime"]["packages"].append(
            {"name": "torch", "version": "2.6.1"})

    operations = (
        ("missing-predictors", lambda m: m.pop("predictors"), "missing_field"),
        ("unknown-top-key", lambda m: m.update({"extra": True}),
         "unknown_field"),
        ("invalid-source-revision",
         lambda m: m["predictors"][0].update({"revision": "abc"}),
         "invalid_revision"),
        ("invalid-license-sha",
         lambda m: m["predictors"][0].update({"license_sha256": "1" * 63}),
         "invalid_sha256"),
        ("single-family-only", single_family, "missing_required_value"),
        ("invalid-family", set_family, "invalid_value"),
        ("unsorted-predictors",
         lambda m: m["predictors"].reverse(), "noncanonical_order"),
        ("duplicate-predictor-id",
         lambda m: m["predictors"][1].update(
             {"id": m["predictors"][0]["id"]}), "duplicate_value"),
        ("boolean-checkpoint-bytes", boolean_bytes, "invalid_integer"),
        ("zero-checkpoint-bytes", zero_bytes, "out_of_range"),
        ("audio-consuming-predictor", audio_consuming, "geometry_mismatch"),
        ("wrong-duration-unit", wrong_unit, "geometry_mismatch"),
        ("missing-runtime-lock",
         lambda m: m["runtime"].pop("lock_sha256"), "missing_field"),
        ("non-offline-runtime",
         lambda m: m["runtime"].update({"offline_load": False}),
         "non_offline_runtime"),
        ("empty-text",
         lambda m: m["items"][0].update({"text": ""}), "empty_text"),
        ("unresolved-language",
         lambda m: m["items"][0].update({"language": "unknown"}),
         "unresolved_value"),
        ("invalid-split",
         lambda m: m["items"][0].update({"split": "train"}), "invalid_value"),
        ("empty-tokens", empty_tokens, "missing_required_value"),
        ("zero-token-duration", zero_duration, "out_of_range"),
        ("non-integer-duration", non_integer, "invalid_integer"),
        ("duration-sum-mismatch", sum_mismatch, "duration_sum_mismatch"),
        ("false-code-license",
         lambda m: m["rights"].update({"code_license": False}),
         "rights_not_cleared"),
        ("missing-outcome",
         lambda m: m["outcomes"].pop("playback_buffering"), "missing_field"),
        ("duplicate-item-id", duplicate_item, "duplicate_value"),
        ("duplicate-package-name", duplicate_package, "duplicate_value"),
    )
    return [_mutation_case(case_id, mutate, code)
            for case_id, mutate, code in operations]


def admission_controls() -> dict:
    accepted = _case_row("accepted-schema-control",
                         validate_manifest(_manifest_control()), False,
                         accepted=True)
    accepted["synthetic_schema_control"] = True
    cases = [accepted]
    cases.append(_case_row("root-list",
                           validate_manifest(["not", "a", "manifest"]), False))
    cases.append(_case_row("root-null", validate_manifest(None), False))
    cases.append(_raw_case(
        "duplicate-json-key",
        '{"schema_id":"' + MANIFEST_SCHEMA_ID + '",'
        '"schema_id":"duplicate"}',
        "duplicate_json_key"))
    cases.append(_raw_case(
        "nonfinite-nan",
        '{"schema_id":"' + MANIFEST_SCHEMA_ID + '","value":NaN}',
        "nonfinite_json"))
    cases.append(_raw_case(
        "nonfinite-infinity",
        '{"schema_id":"' + MANIFEST_SCHEMA_ID + '","value":Infinity}',
        "nonfinite_json"))
    cases.extend(_mutation_cases())

    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted_cases = [case for case in cases if case["status"] == "accepted"]
    summary = {
        "case_count": len(cases),
        "rejected_count": len(rejected),
        "accepted_schema_controls": len(accepted_cases),
        "qualifying_results": 0,
        "state_advanced_on_rejection": False,
        "accepted_control_qualifies": False,
        "all_adverse_cases_rejected":
            len(rejected) == len(cases) - len(accepted_cases),
        "runtime_invoked": False,
        "weights_loaded": False,
        "audio_read": False,
        "inference_performed": False,
        "duration_prediction_performed": False,
    }
    return {"cases": cases, "controls": admission_contract_block(),
            "summary": summary}


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "contract_id": MANIFEST_CONTRACT_ID,
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "required_predictor_families": list(REQUIRED_FAMILIES),
        "max_predictors": MAX_PREDICTORS,
        "max_items": MAX_ITEMS,
        "max_tokens_per_item": MAX_TOKENS_PER_ITEM,
        "max_token_frames": MAX_TOKEN_FRAMES,
        "max_checkpoint_bytes": MAX_CHECKPOINT_BYTES,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "incoming_audio_predictor_rejected": True,
        "duration_sum_consistency_required": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "runtime_or_weights_invoked": False,
    }


# ---------------------------------------------------------------------------
# Report blocks.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "fastspeech2_source_snapshot",
         "The exact FastSpeech 2 source checkout at an immutable 40-hex "
         "commit, with reviewed upstream license text and per-file SHA-256; "
         "the reviewed module is " + FASTSPEECH2_MODULE + "."),
        ("ART-02", "vits_source_snapshot",
         "The exact VITS source checkout at an immutable 40-hex commit, with "
         "reviewed upstream license text and per-file SHA-256."),
        ("ART-03", "checkpoint_bundle",
         CHECKPOINT_REQUIREMENT_EXAMPLE + " at immutable 40-hex model "
         "revisions, including every weight, config, phoneme set, duration "
         "statistic, hop length, model card and terms file, each with byte "
         "count and SHA-256."),
        ("ART-04", "runtime_lock",
         "A reproducible isolated Python runtime with exact interpreter and "
         "package versions including torch, a lock SHA-256, an offline load "
         "path and a recorded host profile."),
        ("ART-05", "rights_bundle",
         "Reviewed code licenses, weight and model-card terms, training-data "
         "provenance, corpus license, output use and redistribution approval "
         "for both sources and every checkpoint."),
        ("ART-06", "duration_cohort",
         "A frozen permitted text and phoneme cohort with reference phoneme "
         "duration labels, language groups, 1x, rate-change, unfamiliar "
         "speech, music, silence, rebuffer, drift and final-partial-window "
         "cases, held-out splits and matched controls."),
        ("ART-07", "rate_results",
         "Independent Rate results for duration error and sum consistency, "
         "source/output mapping, speech preservation, pitch, transient "
         "audibility, playback buffering, nonfinite and peak behavior, device "
         "timing, resources and uncertainty, plus the explicit text-side "
         "versus incoming-audio scope decision."),
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
         "The exact FastSpeech 2 source checkout is absent. No reviewable tree "
         "at a 40-hex commit, upstream license text or per-file SHA-256 pin "
         "for " + FASTSPEECH2_MODULE + " or " + FASTSPEECH2_UPSTREAM_LEAD +
         " exists in the workspace.",
         "Supply the reviewed FastSpeech 2 source at an immutable 40-hex "
         "commit with its license text and per-file SHA-256 pins; do not "
         "substitute a mirror."),
        ("BLK-02", "ART-02", ["RG-01", "RG-04"],
         "The exact VITS source checkout is absent. No reviewable tree at a "
         "40-hex commit, upstream license text or per-file SHA-256 pin exists "
         "in the workspace.",
         "Supply the reviewed VITS source at an immutable 40-hex commit with "
         "its license text and per-file SHA-256 pins."),
        ("BLK-03", "ART-03", ["RG-01", "RG-04", "RG-07"],
         "The FastSpeech 2 and VITS checkpoint bundles are absent. No weight "
         "file, config, phoneme set, duration statistic, hop length, model "
         "card or terms file is present at an immutable 40-hex revision with "
         "SHA-256 and byte counts.",
         "Supply the caller-selected exact FastSpeech 2 and VITS checkpoint "
         "bundles with every file pinned by SHA-256 and byte count, including "
         "the phoneme set, duration statistics and hop length."),
        ("BLK-04", "ART-04", ["RG-04", "RG-07"],
         "The pinned isolated Python runtime is absent. No interpreter, "
         "package lock, offline load path or environment digest with torch is "
         "present, so a checkpoint load and duration forward pass cannot be "
         "reproduced.",
         "Supply a locked, reproducible Python runtime with exact interpreter "
         "and package versions, lock SHA-256, offline load path and host "
         "profile."),
        ("BLK-05", "ART-05", ["RG-01", "RG-06"],
         "Code licenses, weight terms, training-data provenance, corpus "
         "license, output use and redistribution are unresolved. No reviewed "
         "rights bundle clears either source, either checkpoint or any "
         "duration label.",
         "Provide reviewed code licenses, weight and model-card terms, "
         "training-data provenance, corpus license, output use and "
         "redistribution approval."),
        ("BLK-06", "ART-06", ["RG-02", "RG-03", "RG-05"],
         "No permitted text and phoneme cohort with reference duration labels "
         "exists. Language groups, 1x, rate changes, unfamiliar speech, music, "
         "silence, rebuffer, drift, the final partial window, held-out splits "
         "and matched controls are absent.",
         "Supply the frozen permitted cohort with reference phoneme duration "
         "labels, every required rate condition, held-out splits and matched "
         "controls."),
        ("BLK-07", "ART-07", ["RG-02", "RG-03", "RG-05", "RG-07", "RG-08"],
         "No Rate evidence exists. Duration error and sum consistency, "
         "source/output mapping, speech preservation, pitch, transient "
         "audibility, playback buffering, nonfinite and peak behavior, device "
         "timing, resources and uncertainty are unmeasured. The named modules "
         "consume phoneme or encoder inputs, so no incoming audio path exists "
         "and no input-audio rate controller is produced.",
         "Run and preserve the independent Rate protocol on the exact pinned "
         "source, checkpoints and runtime, and record an explicit decision on "
         "text-conditioned duration priors versus an incoming-audio rate "
         "controller."),
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
        ("RG-01", "exact licensed FastSpeech 2 and VITS source and checkpoints "
                  "pinned",
         "The exact sources, checkpoints, per-file digests and license terms "
         "are absent.",
         "Supply and pin both sources and the caller-selected checkpoints with "
         "reviewed terms."),
        ("RG-02", "rate acceptance protocol on a frozen permitted cohort",
         "No permitted cohort, held-out partition or 1x, rate-change, "
         "unfamiliar-speech, music, silence, rebuffer, drift, final-partial-"
         "window or speech-preservation result exists.",
         "Freeze the permitted cohort and run the Rate protocol end to end."),
        ("RG-03", "task geometry and adapter-boundary validity",
         "The named modules are text-conditioned duration predictors with no "
         "incoming-audio path, and no public v0 adapter boundary accepts "
         "text, phoneme ids or encoder states.",
         "Record an explicit text-conditioned duration-prior scope with a "
         "separate input-audio controller comparison before any integration."),
        ("RG-04", "pinned source, checkpoints, runtime and per-file terms",
         "No exact source revision, checkpoint revision, runtime lock or "
         "per-file terms are pinned.",
         "Pin both sources, both checkpoints, the runtime and the terms with "
         "exact digests."),
        ("RG-05", "duration arithmetic, numerical behavior and timing",
         "No integer duration sum consistency, nonfinite or peak behavior, "
         "frame/hop mapping, playback buffering or target-device timing "
         "measurement exists.",
         "Measure duration arithmetic, numerical behavior, buffering and "
         "timing on the exact target."),
        ("RG-06", "code license, training-data provenance, corpus license and "
                  "output use",
         "Code licenses, weight terms, training-data provenance, corpus "
         "license, redistribution and output use are unresolved and "
         "independent of model quality.",
         "Obtain reviewed code, weight, corpus and output-use approvals."),
        ("RG-07", "opt-in intake and independent review",
         "No adapter, descriptor, default-off intake decision or independent "
         "exact-head review exists.",
         "Add a task-local opt-in adapter only after RG-01 to RG-06 pass, then "
         "obtain independent exact-head review."),
        ("RG-08", "release approval",
         "Release approval is absent and DEFER remains in force.",
         "Close every preceding gate and obtain release approval."),
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
        "candidate": "FastSpeech 2 / VITS duration predictors",
        "entries": [],
        "searched_pins": [
            "research/tsm-followup-20261101/README.md",
            "research/tsm-followup-20261101/agent-text/REPORT.md",
            "research/category_registry.json",
            "research/category_survey/sources.md",
        ],
        "not_reproduced_here": True,
        "no_values_inferred_from_adjacent_tasks": True,
        "note": "The pinned read-only records contain an architecture "
                "inspection only: both predictors require text or encoder "
                "representations and predict synthesized phoneme durations, "
                "with no module or checkpoint run. No duration value, rate, "
                "timing or metric is recorded locally, and no adjacent "
                "TTS, planner, VAD or stretcher value is inherited.",
    }


def rate_profile_block() -> dict:
    return {
        "profile": PROFILE_KEY,
        "status": "blocked",
        "rows": [dict(row) for row in RATE_REQUIREMENTS],
        "source_output_mapping_measured": False,
        "duration_measured": False,
        "pitch_measured": False,
        "transient_audibility_measured": False,
        "playback_buffering_measured": False,
        "rate_conditions_covered": False,
        "pause_or_filler_timestamp_tied": False,
        "speech_preservation_measured": False,
        "independent_device_timing_present": False,
        "text_conditioned_scope_qualified": False,
        "qualifies": False,
    }


def profile_source() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    expected = SOURCE_PINS[PROFILE_SOURCE_REL]
    if not path.is_file():
        raise ValueError("profile_source_missing")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError("profile_source_unpinned")
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Rate |")]
    if len(rows) != 1:
        raise ValueError("rate_profile_row_not_unique")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("rate_profile_phrase_missing:" + phrase)
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
        "duration_prediction_performed": False,
        "duration_scored": False,
        "real_corpus": False,
        "audio_read": False,
        "audio_written": False,
        "tts_performed": False,
        "quality_scored": False,
        "pitch_shift_measured": False,
        "transient_audibility_measured": False,
        "playback_buffering_measured": False,
        "speech_preservation_measured": False,
        "listening": False,
        "device_timing": False,
        "first_output_timing": False,
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
        "duration_prediction": False,
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


def upstream_record() -> dict:
    return {
        "fastspeech2_source_repository": FASTSPEECH2_SOURCE_REPOSITORY,
        "fastspeech2_module": FASTSPEECH2_MODULE,
        "fastspeech2_upstream_lead": FASTSPEECH2_UPSTREAM_LEAD,
        "vits_source_repository": VITS_SOURCE_REPOSITORY,
        "source_revision": None,
        "source_revision_requirement":
            "immutable 40-hex upstream commit for each checkout, verified from "
            "a reviewable tree",
        "source_license": None,
        "source_license_requirement":
            "reviewed upstream license text with exact SPDX identifier and "
            "license SHA-256 for each source; no license is asserted here",
        "checkpoint_revision": None,
        "checkpoint_revision_requirement":
            "immutable 40-hex model revision for every checkpoint bundle",
        "checkpoint_file_requirement":
            "every weight, config, phoneme set, duration statistic, hop "
            "length and terms file with byte count and SHA-256",
        "checkpoint_requirement": CHECKPOINT_REQUIREMENT_EXAMPLE,
        "sample_rate_hz": None,
        "sample_rate_requirement":
            "checkpoint-specific acoustic sample rate and hop length, "
            "recorded with the exact bundle",
        "task_kind": "tts_phoneme_duration_predictor",
        "consumes_incoming_audio": False,
        "is_input_audio_rate_estimator": False,
        "present": False,
        "executed": False,
        "digest_asserted": False,
    }


def rights_gap() -> dict:
    return {
        "code_license": "unverified_source_absent",
        "weight_terms": "unresolved",
        "training_data_provenance": "unresolved",
        "corpus_license": "unresolved",
        "output_use": "unresolved",
        "redistribution": "unresolved",
        "all_resolved": False,
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "exact_source_present": False,
        "exact_weights_present": False,
        "exact_runtime_present": False,
        "exact_licensed_conjunction_present": False,
        "rights_cleared": False,
        "duration_cohort_present": False,
        "task_geometry_qualified": False,
        "duration_prediction_evaluation_present": False,
        "duration_error_result": False,
        "duration_sum_consistency_result": False,
        "source_output_mapping_result": False,
        "speech_preservation_result": False,
        "pitch_result": False,
        "transient_audibility_result": False,
        "playback_buffering_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_qualification_present": False,
        "missing_result_promoted": False,
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
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
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
        "profile_source": profile_source(),
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
        "geometry": model_geometry(),
        "task_geometry": task_geometry(),
        "upstream_record": upstream_record(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
        "board_row_projection": board_row_projection(),
        "board_row_sha256": board_row_digest(board_row_projection()),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "rights_gap": rights_gap(),
        "rate_profile": rate_profile_block(),
        "rate_profile_requirements": [dict(row) for row in RATE_REQUIREMENTS],
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "admission_contract": admission_contract_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": list(NON_CLAIMS),
        "write_scope": WRITE_SCOPE,
        "qualification": qualification_block(),
    }


def build_report() -> dict:
    contract = build_contract()
    probes = absence_probes()
    _assert_absence(probes)
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
        "profile_source": profile_source(),
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
        "geometry": model_geometry(),
        "task_geometry": task_geometry(),
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
        "linked_row_identity": linked_identity_block(),
        "rate_profile": rate_profile_block(),
        "rate_profile_requirements": [dict(row) for row in RATE_REQUIREMENTS],
        "qualification": qualification_block(),
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": "Python 3.11, standard library only",
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
            "commands": [
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
        },
        "write_scope": WRITE_SCOPE,
    }


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_mismatch")
    if contract.get("contract_id") != CONTRACT_ID:
        raise ValueError("contract_id_mismatch")
    if contract.get("task") != TASK:
        raise ValueError("contract_task_mismatch")
    if contract.get("title") != TASK_TITLE:
        raise ValueError("contract_title_mismatch")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component_mismatch")
    if contract.get("mode") != MODE:
        raise ValueError("contract_mode_mismatch")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch_mismatch")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_mismatch")
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
    if contract.get("task_geometry") != task_geometry():
        raise ValueError("contract_task_geometry_mismatch")
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
    if not isinstance(blockers, list) or len(blockers) != 7:
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open:" + str(row.get("id")))
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 7:
        raise ValueError("contract_artifact_count")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True):
            raise ValueError("contract_artifact_not_blocked:" +
                             str(row.get("id")))
    qualification = contract.get("qualification", {})
    if (qualification.get("status") != QUALIFICATION_STATUS
            or qualification.get("readiness") != "incomplete"
            or qualification.get("all_release_gates_blocked") is not True):
        raise ValueError("contract_qualification_invalid")
    assert_no_float(contract)
