# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-LIVEKIT-TURN-DETECTION.

This module never installs ``livekit-agents``, downloads a model weight, reads
audio, calls LiveKit Inference, measures a device, performs listening or makes
an accuracy, benchmark or release claim. The exact LiveKit turn-detector
assets, weights, runtime, revisions and commercial terms are absent. The
module pins stable read-only inputs, proves fixed absence probes, exercises a
fail-closed caller-supplied-asset admission schema and replays a synthetic
endpoint-policy control that keeps framewise activity separate from endpoint
decisions.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/livekit-turn-detection/"

TASK = "SDK-LIVEKIT-TURN-DETECTION"
TITLE = "LiveKit turn detection"
COMPONENT = "livekit-turn-detection"
COMPONENT_ID = "livekit-turn-detection"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "analysis"
PROFILE_KEY = "Analysis"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_external_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/livekit-turn-detection-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/livekit-turn-detection-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/livekit-turn-detection-report/0.1"
BASE_COMMIT = "b02dbf12499038abc4f9b6b1c06cdecc76a79dcd"
BRANCH = "swarm/SDK-LIVEKIT-TURN-DETECTION"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-LIVEKIT-TURN-DETECTION")
REVIEWER = "reviewer-LIVEKIT-TURN-DETECTION"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+){0,3}(?:[-+][A-Za-z0-9.]{1,32})?$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to SOURCE_ROOT; SDK paths
# are worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/docs/acceptance-matrix.md":
        "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/acceptance-matrix.md":
        "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

STABLE_TASK_FIELDS = ("acceptance", "component", "deliverable", "depends_on",
                      "evidence", "id", "mode", "repository", "title",
                      "write_scope")
MUTABLE_FIELDS_EXCLUDED = ("blocked_reason", "dispatch_priority", "handoff",
                           "owner", "review", "status")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "float32",
    "frame_samples": 160,
    "frame_ms": 10,
    "source": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
}

# ---------------------------------------------------------------------------
# Upstream identity. Only public product documentation was read. No asset,
# weight, exact revision, digest, runtime or licence text was observed.
# ---------------------------------------------------------------------------

UPSTREAM_PRODUCT = "LiveKit turn detector"
UPSTREAM_VENDOR = "LiveKit"
UPSTREAM_DOCS_URL = "https://docs.livekit.io/agents/logic/turns/turn-detector.md"
UPSTREAM_TURNS_URL = "https://docs.livekit.io/agents/logic/turns/"
UPSTREAM_SOURCE_URL = ("https://github.com/livekit/agents/tree/main/"
                       "livekit-plugins/livekit-plugins-turn-detector")
UPSTREAM_LICENSE_URL = "https://huggingface.co/livekit/turn-detector/blob/main/LICENSE"
UPSTREAM_LICENSE_ID = "LiveKit-Model-License"
UPSTREAM_BASE_MODEL = "Qwen2.5-0.5B-Instruct"

MODEL_VARIANTS = (
    {
        "id": "v1",
        "kind": "multimodal-remote",
        "description": "Full multimodal end-of-turn model served on LiveKit "
                       "Inference; reads the agent's last message and user audio.",
        "runs_locally": False,
        "remote_inference_required": True,
        "credentials_required": ["LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"],
        "open_weights_claimed": False,
        "weights_digest_observed": False,
        "asset_sha256": None,
        "license_id": UPSTREAM_LICENSE_ID,
        "license_text_observed": False,
        "context_mode": "agent-message+audio",
    },
    {
        "id": "v1-mini",
        "kind": "multimodal-local",
        "description": "Lightweight multimodal fallback that runs locally on "
                       "CPU inside livekit-agents.",
        "runs_locally": True,
        "remote_inference_required": False,
        "credentials_required": [],
        "open_weights_claimed": False,
        "weights_digest_observed": False,
        "asset_sha256": None,
        "license_id": UPSTREAM_LICENSE_ID,
        "license_text_observed": False,
        "context_mode": "audio",
        "memory_mb_low": 310,
        "memory_mb_high": 340,
    },
    {
        "id": "text-multilingual",
        "kind": "text-transcript",
        "description": "Deprecated open-weights multilingual text turn "
                       "detector built on Qwen2.5-0.5B-Instruct; requires STT "
                       "transcripts and is slated for removal in Agents 2.0.",
        "runs_locally": True,
        "remote_inference_required": False,
        "credentials_required": [],
        "open_weights_claimed": True,
        "open_weights_verified": False,
        "weights_digest_observed": False,
        "asset_sha256": None,
        "license_id": UPSTREAM_LICENSE_ID,
        "license_text_observed": False,
        "context_mode": "transcript",
        "disk_size_mb": 396,
        "per_turn_latency_ms_low": 50,
        "per_turn_latency_ms_high": 160,
        "deprecated": True,
    },
)

ENDPOINT_DEFAULTS_DOCUMENTED = {
    "with_multimodal_min_delay_ms": 300,
    "with_multimodal_max_delay_ms": 2500,
    "without_multimodal_min_delay_ms": 500,
    "without_multimodal_max_delay_ms": 3000,
    "prediction_timeout_ms": 1000,
    "default_commit_probability_on_timeout_permille": 1000,
    "measured_here": False,
    "source": UPSTREAM_DOCS_URL,
}

# ---------------------------------------------------------------------------
# Fixed absence probes and release gates.
# ---------------------------------------------------------------------------

ABSENCE_PROBE_PATHS = (
    "data/models/livekit-turn-detection",
    "data/models/livekit-turn-detection/v1-mini.onnx",
    "data/runtime/livekit-turn-detection",
    "data/runtime/livekit-turn-detection/requirements.lock",
    "data/rights/livekit-turn-detection-rights.json",
    "data/rights/livekit-turn-detection-model-license.txt",
    "data/runs/livekit-turn-detection-cohort/manifest.json",
    "tests/fixtures/turn-labels/livekit-cohort.json",
)
MISSING_HISTORICAL_ARTIFACTS = tuple(ABSENCE_PROBE_PATHS)

GATE_IDS = ("RG-01", "RG-02", "RG-03", "RG-04", "RG-05", "RG-06", "RG-07",
            "RG-08")
GATE_REQUIREMENTS = (
    "Rights-qualified conversational corpus with utterance and turn "
    "boundaries and explicit unknown regions",
    "Frozen speaker/session-disjoint development and held-out partitions "
    "with independent label review",
    "Matched identity, fixed-timer, VAD-only and human-endpoint controls with "
    "cutoff and end-of-turn delay distributions",
    "Pinned real acoustic/prosodic and semantic turn runtimes, weights and "
    "exact revisions",
    "Paced live state, maximum-wait fallback, overlap/barge-in and "
    "target-device availability evidence",
    "Opt-in provider intake and independent exact-head review",
    "Explicit public default selection approval",
    "Release approval; DEFER remains in force until every gate is closed",
)

BLOCKER_IDS = ("BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05", "BLK-06",
               "BLK-07", "BLK-08")
BLOCKERS = (
    {
        "id": "BLK-01",
        "blocker": "No turn-detector weight or asset with an observed SHA-256 "
                   "is available offline; obtaining v1-mini or the text model "
                   "requires installing livekit-agents and downloading "
                   "runtime-delivered weights.",
        "reopen_condition": "A caller supplies a digest-pinned local model "
                            "asset whose bytes hash to the declared SHA-256 "
                            "and whose runtime is installed outside this task.",
    },
    {
        "id": "BLK-02",
        "blocker": "The full v1 multimodal model is remote inference only and "
                   "requires a LiveKit Cloud project, network access, "
                   "LIVEKIT_API_KEY and LIVEKIT_API_SECRET; no offline runtime "
                   "or public weights exist.",
        "reopen_condition": "Either an authorized LiveKit Inference execution "
                            "is approved for a locked cohort, or v1 is "
                            "excluded and only a pinned local variant is used.",
    },
    {
        "id": "BLK-03",
        "blocker": "The text and v1-mini models use the LiveKit Model License, "
                   "not Apache-2.0; the licence text, redistribution terms and "
                   "output-use terms were not observed or reviewed.",
        "reopen_condition": "The exact licence text and a written rights "
                            "decision covering local execution and evidence "
                            "publication are recorded.",
    },
    {
        "id": "BLK-04",
        "blocker": "No rights-qualified conversational corpus with utterance "
                   "and turn boundaries, mid-turn pauses and explicit unknown "
                   "regions is staged; no matched cohort or label review "
                   "exists.",
        "reopen_condition": "A frozen speaker/session-disjoint turn-labelled "
                            "cohort with rights clearance and unknown-region "
                            "masking is available.",
    },
    {
        "id": "BLK-05",
        "blocker": "The model input geometry is unpublished: the text model "
                   "consumes transcript tokens and the v1-mini audio input "
                   "sample rate, hop and preprocessing are not documented as "
                   "exact values.",
        "reopen_condition": "The exact input contract, preprocessing and frame "
                            "geometry for the selected variant are published "
                            "or reproduced from a pinned runtime.",
    },
    {
        "id": "BLK-06",
        "blocker": "No pinned/tested LiveKit host package pair exists; S09 is "
                   "blocked and Python 3.12.16 compatibility with the required "
                   "livekit-agents release is unverified.",
        "reopen_condition": "A reproducible host/runtime pair is installed in "
                            "an isolated environment and its version and "
                            "import surface are recorded.",
    },
    {
        "id": "BLK-07",
        "blocker": "Per-language calibrated unlikely thresholds are not "
                   "published as values; only documented aggregate true-"
                   "positive and true-negative rates exist.",
        "reopen_condition": "Calibration values and the calibration cohort are "
                            "published or independently reproduced for the "
                            "selected language set.",
    },
    {
        "id": "BLK-08",
        "blocker": "Independent exact-head review, hosted CI and release "
                   "approval are absent; no candidate result can be promoted.",
        "reopen_condition": "Exact-head review, hosted CI and explicit release "
                            "approval are recorded for the frozen artifacts.",
    },
)

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
# hashed; only the stable linked-row identity enters canonical bytes.
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
        "claim": claim,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_FIELDS_EXCLUDED),
    }


def profile_source() -> dict:
    path = SOURCE_ROOT / PROFILE_SOURCE_REL
    if not path.is_file():
        raise InvalidInput("profile_source_unavailable")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| " + PROFILE_KEY + " |"):
            return {
                "profile": PROFILE,
                "key": PROFILE_KEY,
                "row": line,
                "path": PROFILE_SOURCE_REL,
            }
    raise InvalidInput("profile_row_unavailable")


def absence_probes(root: Path | None = None) -> list[dict]:
    base = root if root is not None else SOURCE_ROOT
    rows = []
    for relative in ABSENCE_PROBE_PATHS:
        path = base / relative
        rows.append({
            "path": relative,
            "present": path.exists(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
        })
    return rows


def absence_summary(rows: list[dict]) -> dict:
    present = [row["path"] for row in rows if row["present"]]
    return {
        "probe_count": len(rows),
        "present_count": len(present),
        "present": present,
        "all_probes_absent": not present,
    }


# ---------------------------------------------------------------------------
# Synthetic endpoint-policy control. All values are integers. The trace is a
# frozen control, not a model posterior and not LiveKit output.
# ---------------------------------------------------------------------------

FRAME_SAMPLES = 160
SAMPLE_RATE_HZ = 16000
FRAME_MS = 10
TOTAL_FRAMES = 700
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES
NS_PER_SAMPLE = 62500
ORIGIN_NS = 1_000_000_000
CLOCK = "livekit-turn-policy-monotonic-v0"
MIN_DELAY_FRAMES = 30
MAX_DELAY_FRAMES = 250
THRESHOLD_PERMILLE = 500

SEGMENTS = (
    (0, 20, "active-speech", "turn-a"),
    (20, 60, "mid-turn-pause", "turn-a"),
    (60, 80, "quiet-speech", "turn-a"),
    (80, 130, "idle-noise", "turn-a"),
    (130, 160, "active-speech", "turn-b"),
    (160, 200, "mid-turn-pause", "turn-b"),
    (200, 210, "active-speech", "turn-b"),
    (210, 260, "idle-noise", "turn-b"),
    (260, 270, "active-speech", "turn-c"),
    (270, 320, "idle-noise", "turn-c"),
    (320, 340, "active-speech", "turn-d"),
    (340, 640, "mid-turn-pause", "turn-d"),
    (640, 660, "idle-noise", "turn-d"),
    (660, 700, "unknown", None),
)

TURNS = (
    {"id": "turn-a", "start": 0, "true_eot": 80, "region_end": 130},
    {"id": "turn-b", "start": 130, "true_eot": 210, "region_end": 260},
    {"id": "turn-c", "start": 260, "true_eot": 270, "region_end": 320},
    {"id": "turn-d", "start": 320, "true_eot": 640, "region_end": 660},
)

# Deterministic synthetic VAD false positives: frame spans classified as
# speech although the truth stratum is nonspeech.
VAD_FALSE_POSITIVE_SPANS = ((30, 40), (280, 290))


def _in_spans(frame: int, spans: Iterable[tuple[int, int]]) -> bool:
    return any(start <= frame < end for start, end in spans)


def stratum_of(frame: int) -> str:
    if not 0 <= frame < TOTAL_FRAMES:
        raise InvalidInput("frame_out_of_range:" + str(frame))
    for start, end, stratum, _ in SEGMENTS:
        if start <= frame < end:
            return stratum
    raise InvalidInput("frame_uncovered:" + str(frame))


def turn_of(frame: int) -> str | None:
    for start, end, _, turn_id in SEGMENTS:
        if start <= frame < end:
            return turn_id
    raise InvalidInput("frame_uncovered:" + str(frame))


def vad_state(frame: int) -> str | None:
    stratum = stratum_of(frame)
    if stratum == "unknown":
        return None
    if stratum == "active-speech":
        return "speech"
    if stratum == "quiet-speech":
        # The frozen synthetic VAD misses quiet speech; the truth stratum
        # still counts as speech for the stratified false-negative metric.
        return "nonspeech"
    if _in_spans(frame, VAD_FALSE_POSITIVE_SPANS):
        return "speech"
    return "nonspeech"


def probability_permille(frame: int) -> int | None:
    """Frozen synthetic completion trace; never a model posterior."""
    stratum = stratum_of(frame)
    if stratum == "unknown":
        return None
    turn = turn_of(frame)
    if turn is None:
        return 500
    spec = turn_spec(turn)
    if frame >= spec["true_eot"]:
        return 900
    if stratum in ("active-speech", "quiet-speech"):
        return 200
    return 100


def turn_spec(turn_id: str) -> dict:
    for turn in TURNS:
        if turn["id"] == turn_id:
            return turn
    raise InvalidInput("unknown_turn:" + turn_id)


def truth_complete(frame: int) -> int | None:
    if stratum_of(frame) == "unknown":
        return None
    turn = turn_of(frame)
    if turn is None:
        return None
    return 1000 if frame >= turn_spec(turn)["true_eot"] else 0


def choose_decision(turn: dict, mode: str) -> dict:
    """Replay one independent policy session for one turn.

    ``mode`` is ``vad_only`` (silence timer on framewise activity) or
    ``gated`` (silence timer plus synthetic completion probability with a
    documented maximum-wait fallback).
    """
    if mode not in ("vad_only", "gated"):
        raise InvalidInput("unknown_policy_mode:" + mode)
    silence_run = 0
    first = turn["start"]
    last = turn["region_end"]
    for frame in range(first, last):
        state = vad_state(frame)
        if state is None:
            continue
        if state == "speech":
            silence_run = 0
            continue
        silence_run += 1
        probability = probability_permille(frame)
        if probability is None:
            continue
        threshold_hit = (silence_run >= MIN_DELAY_FRAMES
                         and probability >= THRESHOLD_PERMILLE)
        max_wait_hit = mode == "gated" and silence_run >= MAX_DELAY_FRAMES
        if mode == "vad_only":
            trigger = silence_run >= MIN_DELAY_FRAMES
        else:
            trigger = threshold_hit or max_wait_hit
        if not trigger:
            continue
        decision_sample = (frame + 1) * FRAME_SAMPLES
        true_sample = turn["true_eot"] * FRAME_SAMPLES
        delay = decision_sample - true_sample
        cause = "vad_silence_timer"
        if mode == "gated":
            cause = "max_wait" if max_wait_hit and not threshold_hit \
                else "probability_threshold"
        return {
            "turn_id": turn["id"],
            "mode": mode,
            "decision_frame": frame,
            "decision_sample": decision_sample,
            "true_eot_sample": true_sample,
            "delay_samples": delay,
            "delay_ms": delay * FRAME_MS // FRAME_SAMPLES,
            "cutoff": delay < 0,
            "cutoff_cause": _cutoff_cause(turn, frame, mode, cause)
            if delay < 0 else None,
            "probability_permille": probability,
            "silence_frames": silence_run,
            "cause": cause,
            "validity": "known",
        }
    return {
        "turn_id": turn["id"],
        "mode": mode,
        "decision_frame": None,
        "decision_sample": None,
        "true_eot_sample": turn["true_eot"] * FRAME_SAMPLES,
        "delay_samples": None,
        "delay_ms": None,
        "cutoff": False,
        "cutoff_cause": None,
        "probability_permille": None,
        "silence_frames": None,
        "cause": "no_decision",
        "validity": "known",
    }


def _cutoff_cause(turn: dict, frame: int, mode: str, cause: str) -> str:
    if mode == "gated" and cause == "max_wait":
        return "max_wait_forced"
    stratum = stratum_of(frame)
    if stratum == "quiet-speech":
        return "vad_quiet_speech_miss"
    if stratum == "mid-turn-pause":
        return "mid_turn_pause"
    return "unknown_cause"


def policy_decisions(mode: str) -> list[dict]:
    return [choose_decision(turn, mode) for turn in TURNS]


def policy_metrics(mode: str) -> dict:
    decisions = policy_decisions(mode)
    delays = [item["delay_samples"] for item in decisions
              if item["delay_samples"] is not None]
    cutoffs = [item for item in decisions if item["cutoff"]]
    cause_counts: dict[str, int] = {}
    for item in cutoffs:
        cause = item["cutoff_cause"]
        cause_counts[cause] = cause_counts.get(cause, 0) + 1
    return {
        "mode": mode,
        "decision_count": len(delays),
        "no_decision_count": len(decisions) - len(delays),
        "cutoff_count": len(cutoffs),
        "cutoff_cause_counts": dict(sorted(cause_counts.items())),
        "max_wait_forced_count": sum(
            1 for item in decisions if item["cause"] == "max_wait"),
        "worst_cutoff_samples": min(delays) if cutoffs else None,
        "mean_end_of_turn_delay_samples":
            fraction_text(Fraction(sum(delays), len(delays))) if delays else None,
        "mean_absolute_end_of_turn_delay_samples":
            fraction_text(Fraction(sum(abs(value) for value in delays),
                                   len(delays))) if delays else None,
        "decisions": decisions,
    }


def framewise_metrics() -> dict:
    counts = {
        "active-speech": {"speech_samples": 0, "nonspeech_samples": 0,
                          "unknown_samples": 0},
        "quiet-speech": {"speech_samples": 0, "nonspeech_samples": 0,
                         "unknown_samples": 0},
        "mid-turn-pause": {"speech_samples": 0, "nonspeech_samples": 0,
                           "unknown_samples": 0},
        "idle-noise": {"speech_samples": 0, "nonspeech_samples": 0,
                       "unknown_samples": 0},
        "unknown": {"speech_samples": 0, "nonspeech_samples": 0,
                    "unknown_samples": 0},
    }
    for frame in range(TOTAL_FRAMES):
        state = vad_state(frame)
        stratum = stratum_of(frame)
        if state is None:
            counts[stratum]["unknown_samples"] += FRAME_SAMPLES
        elif state == "speech":
            counts[stratum]["speech_samples"] += FRAME_SAMPLES
        else:
            counts[stratum]["nonspeech_samples"] += FRAME_SAMPLES
    tp = counts["active-speech"]["speech_samples"]
    fn = counts["quiet-speech"]["nonspeech_samples"]
    fp = (counts["mid-turn-pause"]["speech_samples"]
          + counts["idle-noise"]["speech_samples"])
    tn = (counts["mid-turn-pause"]["nonspeech_samples"]
          + counts["idle-noise"]["nonspeech_samples"])
    unknown = counts["unknown"]["unknown_samples"]
    return {
        "frame_samples": FRAME_SAMPLES,
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
        "unknown_frames": unknown // FRAME_SAMPLES,
        "unknown_samples": unknown,
        "known_frames": TOTAL_FRAMES - unknown // FRAME_SAMPLES,
        "known_samples": TOTAL_SAMPLES - unknown,
        "tp_samples": tp,
        "fn_samples": fn,
        "fp_samples": fp,
        "tn_samples": tn,
        "speech_miss_rate": fraction_text(Fraction(fn, tp + fn)),
        "false_alarm_rate": fraction_text(Fraction(fp, fp + tn)),
        "per_stratum": counts,
    }


def brier_control() -> dict:
    total = 0
    count = 0
    for frame in range(TOTAL_FRAMES):
        truth = truth_complete(frame)
        probability = probability_permille(frame)
        if truth is None or probability is None:
            continue
        difference = probability - truth
        total += difference * difference
        count += 1
    score = Fraction(total, count * 1_000_000)
    return {
        "label": "synthetic_control_trace_not_model_posterior",
        "scored_frames": count,
        "scaled_permille_squared_brier": fraction_text(score),
        "brier_numerator": total,
        "brier_denominator": count * 1_000_000,
    }


def cross_hop_project(start_sample: int, end_sample: int,
                      hop_samples: int = FRAME_SAMPLES) -> list[dict]:
    if not (0 <= start_sample < end_sample <= TOTAL_SAMPLES):
        raise InvalidInput("cross_hop_span_out_of_range")
    if hop_samples <= 0:
        raise InvalidInput("cross_hop_hop_invalid")
    rows = []
    first_hop = start_sample // hop_samples
    last_hop = (end_sample - 1) // hop_samples
    for hop in range(first_hop, last_hop + 1):
        left = max(start_sample, hop * hop_samples)
        right = min(end_sample, (hop + 1) * hop_samples)
        rows.append({
            "hop_index": hop,
            "overlap_samples": right - left,
            "hop_start_sample": hop * hop_samples,
            "hop_end_sample": (hop + 1) * hop_samples,
        })
    return rows


# ---------------------------------------------------------------------------
# Fail-closed event admission for the synthetic policy session.
# ---------------------------------------------------------------------------

EVENT_KEYS = {
    "epoch", "sequence", "event_type", "start_sample", "end_sample",
    "probability_permille", "decision", "validity", "clock", "available_ns",
    "session_id",
}
CONFIG_KEYS = {
    "session_id", "sample_rate_hz", "channels", "sample_format",
    "frame_samples", "real_runtime",
}
DECISIONS = {"commit", "continue"}
VALIDITY = {"known", "unknown"}


class PolicySession:
    """One independent synthetic endpoint session with fail-closed admission."""

    def __init__(self, session_id: str, epoch: int) -> None:
        config = {
            "session_id": session_id,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": FRAME_SAMPLES,
            "real_runtime": False,
        }
        validate_session_config(config)
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
            raise InvalidInput("invalid_epoch")
        self.session_id = session_id
        self.epoch = epoch
        self.sequence = -1
        self.last_available = -1
        self.known: list[dict] = []
        self.unknown: list[dict] = []
        self.rejections: list[dict] = []

    def reset(self, epoch: int) -> None:
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
            raise InvalidInput("invalid_epoch")
        self.epoch = epoch
        self.sequence = -1
        self.last_available = -1
        self.known = []
        self.unknown = []
        self.rejections = []

    def ingest(self, event: dict) -> tuple[str, str | None]:
        reason = self._validate(event)
        if reason is not None:
            self.rejections.append({"reason": reason,
                                    "sequence": event.get("sequence")})
            return "rejected", reason
        if event["validity"] == "unknown":
            self.unknown.append(event)
            self.sequence = event["sequence"]
            self.last_available = event["available_ns"]
            return "audit_unknown", None
        self.known.append(event)
        self.sequence = event["sequence"]
        self.last_available = event["available_ns"]
        return "accepted", None

    def _validate(self, event: dict) -> str | None:
        if not isinstance(event, dict) or set(event) != EVENT_KEYS:
            return "event_key_set_invalid"
        if event["event_type"] not in ("activity", "endpoint"):
            return "event_type_invalid"
        if event["validity"] not in VALIDITY:
            return "validity_token_invalid"
        if event["decision"] not in DECISIONS:
            return "decision_token_invalid"
        for key in ("epoch", "sequence", "start_sample", "end_sample",
                    "available_ns"):
            value = event[key]
            if not isinstance(value, int) or isinstance(value, bool):
                return "integer_required:" + key
        if event["epoch"] != self.epoch:
            return "stale_or_wrong_epoch"
        if event["sequence"] <= self.sequence:
            return "duplicate_or_stale_sequence"
        if event["clock"] != CLOCK:
            return "wrong_clock"
        if event["session_id"] != self.session_id:
            return "wrong_session"
        if event["start_sample"] < 0:
            return "negative_start_sample"
        if event["end_sample"] <= event["start_sample"]:
            return "non_positive_interval"
        if event["event_type"] == "activity":
            if event["end_sample"] - event["start_sample"] != FRAME_SAMPLES:
                return "wrong_interval_width"
            if event["decision"] != "continue":
                return "activity_decision_invalid"
        if event["end_sample"] > TOTAL_SAMPLES:
            return "interval_out_of_range"
        if event["available_ns"] < self.last_available:
            return "stale_availability"
        probability = event["probability_permille"]
        if not isinstance(probability, int) or isinstance(probability, bool):
            return "probability_integer_required"
        if not 0 <= probability <= 1000:
            return "probability_out_of_range"
        return None

    def digest(self) -> str:
        payload = {
            "epoch": self.epoch,
            "known": self.known,
            "unknown": self.unknown,
            "rejections": self.rejections,
        }
        return sha256_bytes(canonical_bytes(payload))


def validate_session_config(config: Any) -> dict:
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise InvalidInput("config_key_set_invalid")
    if (not isinstance(config["session_id"], str)
            or not config["session_id"].strip()):
        raise InvalidInput("empty_session_id")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise InvalidInput("unsupported_sample_rate")
    if config["channels"] != 1:
        raise InvalidInput("unsupported_channels")
    if config["sample_format"] != "float32":
        raise InvalidInput("unsupported_sample_format")
    if config["frame_samples"] != FRAME_SAMPLES:
        raise InvalidInput("unsupported_frame_samples")
    if config["real_runtime"] is not False:
        raise InvalidInput("real_runtime_not_permitted")
    return config


def activity_event(epoch: int, sequence: int, frame: int,
                   session_id: str) -> dict:
    state = vad_state(frame)
    if state is None:
        raise InvalidInput("unknown_frame_has_no_event")
    probability = probability_permille(frame)
    if probability is None:
        raise InvalidInput("unknown_frame_has_no_probability")
    end_sample = (frame + 1) * FRAME_SAMPLES
    return {
        "epoch": epoch,
        "sequence": sequence,
        "event_type": "activity",
        "start_sample": frame * FRAME_SAMPLES,
        "end_sample": end_sample,
        "probability_permille": probability,
        "decision": "continue",
        "validity": "known",
        "clock": CLOCK,
        "available_ns": ORIGIN_NS + end_sample * NS_PER_SAMPLE + 2_000_000,
        "session_id": session_id,
    }


def endpoint_event(decision: dict, epoch: int, sequence: int,
                   session_id: str) -> dict:
    if decision["decision_frame"] is None:
        raise InvalidInput("no_decision_to_emit")
    turn = turn_spec(decision["turn_id"])
    start_sample = turn["start"] * FRAME_SAMPLES
    end_sample = decision["decision_sample"]
    if end_sample <= start_sample:
        raise InvalidInput("endpoint_interval_invalid")
    return {
        "epoch": epoch,
        "sequence": sequence,
        "event_type": "endpoint",
        "start_sample": start_sample,
        "end_sample": end_sample,
        "probability_permille": decision["probability_permille"],
        "decision": "commit",
        "validity": "known",
        "clock": CLOCK,
        "available_ns": ORIGIN_NS + end_sample * NS_PER_SAMPLE + 4_000_000,
        "session_id": session_id,
    }


def event_stream(mode: str, epoch: int) -> dict:
    session_id = "livekit-turn-" + mode + "-epoch-" + str(epoch)
    session = PolicySession(session_id, epoch)
    sequence = 0
    decisions = {item["decision_frame"]: item
                 for item in policy_decisions(mode)
                 if item["decision_frame"] is not None}
    activity_events = 0
    endpoint_events = 0
    for frame in range(TOTAL_FRAMES):
        if vad_state(frame) is not None:
            status, reason = session.ingest(
                activity_event(epoch, sequence, frame, session_id))
            if status != "accepted":
                raise InvalidInput("activity_rejected:" + str(reason))
            sequence += 1
            activity_events += 1
        decision = decisions.get(frame)
        if decision is not None:
            status, reason = session.ingest(
                endpoint_event(decision, epoch, sequence, session_id))
            if status != "accepted":
                raise InvalidInput("endpoint_rejected:" + str(reason))
            sequence += 1
            endpoint_events += 1
    return {
        "mode": mode,
        "session_id": session_id,
        "epoch": epoch,
        "activity_events": activity_events,
        "endpoint_events": endpoint_events,
        "rejections": session.rejections,
        "digest": session.digest(),
    }


# ---------------------------------------------------------------------------
# Caller-supplied asset admission. The real asset is absent, so every probe is
# rejected before any processing.
# ---------------------------------------------------------------------------

ASSET_MANIFEST_KEYS = {
    "schema_id", "provider", "variant", "model_id", "asset_sha256",
    "asset_bytes", "license_id", "license_acknowledged", "caller_supplied",
    "vendored_in_package", "redistribution_permitted", "runtime_package",
    "runtime_version", "python_version", "sample_rate_hz", "channels",
    "frame_samples", "sample_format", "context_mode", "threshold_permille",
    "endpoint_min_delay_ms", "endpoint_max_delay_ms",
}
ASSET_SCHEMA_ID = "audio-sdk/caller-turn-detector-asset/0.1"
ASSET_VARIANTS = {"v1", "v1-mini", "text-multilingual"}
ASSET_CONTEXT_MODES = {"agent-message+audio", "audio", "transcript"}
ASSET_LICENSE_ID = UPSTREAM_LICENSE_ID
ASSET_RUNTIME_PACKAGES = {"livekit-agents", "livekit-plugins-turn-detector"}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_asset_manifest(manifest: Any) -> tuple[bool, str | None]:
    if not isinstance(manifest, dict):
        return False, "asset_manifest_absent"
    if set(manifest) != ASSET_MANIFEST_KEYS:
        return False, "asset_key_set_invalid"
    if manifest["schema_id"] != ASSET_SCHEMA_ID:
        return False, "asset_schema_invalid"
    if manifest["provider"] != "livekit":
        return False, "asset_provider_invalid"
    if manifest["variant"] not in ASSET_VARIANTS:
        return False, "asset_variant_invalid"
    if not isinstance(manifest["model_id"], str) or not manifest["model_id"]:
        return False, "asset_model_id_invalid"
    digest = manifest["asset_sha256"]
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        return False, "asset_digest_invalid"
    if not _is_int(manifest["asset_bytes"]) or manifest["asset_bytes"] <= 0:
        return False, "asset_bytes_invalid"
    if manifest["license_id"] != ASSET_LICENSE_ID:
        return False, "asset_license_invalid"
    if manifest["license_acknowledged"] is not True:
        return False, "asset_license_not_acknowledged"
    if manifest["caller_supplied"] is not True:
        return False, "asset_not_caller_supplied"
    if manifest["vendored_in_package"] is not False:
        return False, "asset_vendored"
    if manifest["redistribution_permitted"] is not False:
        return False, "asset_redistribution_not_permitted"
    if manifest["runtime_package"] not in ASSET_RUNTIME_PACKAGES:
        return False, "asset_runtime_package_invalid"
    if (not isinstance(manifest["runtime_version"], str)
            or VERSION.fullmatch(manifest["runtime_version"]) is None):
        return False, "asset_runtime_version_invalid"
    if manifest["python_version"] != "3.12.16":
        return False, "asset_python_version_invalid"
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        return False, "asset_sample_rate_invalid"
    if manifest["channels"] != 1:
        return False, "asset_channels_invalid"
    if manifest["frame_samples"] != FRAME_SAMPLES:
        return False, "asset_frame_samples_invalid"
    if manifest["sample_format"] != "float32":
        return False, "asset_sample_format_invalid"
    if manifest["context_mode"] not in ASSET_CONTEXT_MODES:
        return False, "asset_context_mode_invalid"
    threshold = manifest["threshold_permille"]
    if not _is_int(threshold) or not 1 <= threshold <= 999:
        return False, "asset_threshold_invalid"
    minimum = manifest["endpoint_min_delay_ms"]
    maximum = manifest["endpoint_max_delay_ms"]
    if not _is_int(minimum) or not _is_int(maximum):
        return False, "asset_endpoint_delay_invalid"
    if minimum <= 0 or maximum <= minimum:
        return False, "asset_endpoint_delay_order_invalid"
    return True, None


def positive_asset_fixture() -> dict:
    return {
        "schema_id": ASSET_SCHEMA_ID,
        "provider": "livekit",
        "variant": "v1-mini",
        "model_id": "livekit-turn-detector-v1-mini-caller-asset",
        "asset_sha256": "a" * 64,
        "asset_bytes": 123456789,
        "license_id": ASSET_LICENSE_ID,
        "license_acknowledged": True,
        "caller_supplied": True,
        "vendored_in_package": False,
        "redistribution_permitted": False,
        "runtime_package": "livekit-agents",
        "runtime_version": "1.8.12",
        "python_version": "3.12.16",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "sample_format": "float32",
        "context_mode": "audio",
        "threshold_permille": 500,
        "endpoint_min_delay_ms": 300,
        "endpoint_max_delay_ms": 2500,
    }


ADVERSE_ASSET_CASE_IDS = (
    "absent", "missing_key", "bad_digest", "wrong_license",
    "license_not_acknowledged", "vendored", "redistribution_allowed",
    "wrong_sample_rate", "wrong_frame_samples", "wrong_format",
    "wrong_provider", "wrong_variant", "wrong_context", "zero_threshold",
    "threshold_above_range", "max_not_above_min", "wrong_python",
    "wrong_runtime_package",
)


def adverse_asset_cases() -> list[dict]:
    cases: list[dict] = []
    for case_id in ADVERSE_ASSET_CASE_IDS:
        if case_id == "absent":
            manifest: Any = None
        else:
            manifest = positive_asset_fixture()
            if case_id == "missing_key":
                manifest.pop("asset_bytes")
            elif case_id == "bad_digest":
                manifest["asset_sha256"] = "not-a-digest"
            elif case_id == "wrong_license":
                manifest["license_id"] = "Apache-2.0"
            elif case_id == "license_not_acknowledged":
                manifest["license_acknowledged"] = False
            elif case_id == "vendored":
                manifest["vendored_in_package"] = True
            elif case_id == "redistribution_allowed":
                manifest["redistribution_permitted"] = True
            elif case_id == "wrong_sample_rate":
                manifest["sample_rate_hz"] = 48000
            elif case_id == "wrong_frame_samples":
                manifest["frame_samples"] = 320
            elif case_id == "wrong_format":
                manifest["sample_format"] = "s16"
            elif case_id == "wrong_provider":
                manifest["provider"] = "other"
            elif case_id == "wrong_variant":
                manifest["variant"] = "v9"
            elif case_id == "wrong_context":
                manifest["context_mode"] = "text"
            elif case_id == "zero_threshold":
                manifest["threshold_permille"] = 0
            elif case_id == "threshold_above_range":
                manifest["threshold_permille"] = 1000
            elif case_id == "max_not_above_min":
                manifest["endpoint_max_delay_ms"] = 300
            elif case_id == "wrong_python":
                manifest["python_version"] = "3.11.5"
            elif case_id == "wrong_runtime_package":
                manifest["runtime_package"] = "livekit-turn-detector"
        accepted, reason = validate_asset_manifest(manifest)
        cases.append({
            "id": case_id,
            "accepted": accepted,
            "reason": reason,
        })
    return cases


# ---------------------------------------------------------------------------
# Git scope helpers: newest merge-base and branch-diff containment.
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
    r"sdk:[A-Za-z0-9_./-]+|" + re.escape(TASK_PREFIX)
    + r"[A-Za-z0-9_./-]+)$")


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

BOUNDARY_FLAGS = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "production_callback_registered": False,
    "descriptor_registry_change": False,
    "shared_build_or_ci_change": False,
    "installed_v0_behavior_change": False,
    "asset_bundled": False,
    "binary_vendored": False,
    "sdk_callback_invoked": False,
    "network_used": False,
    "adapter_json_added": False,
    "provider_json_added": False,
    "board_changed": False,
    "handoff_changed": False,
    "processor_exposure": False,
    "provider_intake_complete": False,
    "release_approval": False,
}

SCOPE_FLAGS = {
    "real_audio": False,
    "real_corpus": False,
    "model_loaded": False,
    "model_executed": False,
    "network_used": False,
    "download_attempted": False,
    "package_installed": False,
    "binary_committed": False,
    "device_timing": False,
    "listening": False,
    "public_benchmark": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "task_local_only": True,
    "synthetic_only": True,
}

ANALYSIS_REQUIREMENTS = (
    ("timestamped_probabilities_scored",
     "Score timestamped completion probabilities",
     "Synthetic control trace is scored with an exact rational Brier "
     "numerator/denominator; it is not a model posterior."),
    ("event_boundaries_scored",
     "Score event boundaries",
     "Four synthetic turn boundaries with exact true end-of-turn samples and "
     "signed decision delays."),
    ("detections_scored",
     "Score detections",
     "Four endpoint decisions per policy, with cutoff counts and causes."),
    ("quiet_and_active_speech",
     "Include quiet and active speech",
     "Frozen active-speech and quiet-speech strata at 160-sample frames."),
    ("idle_noise",
     "Include idle noise",
     "Frozen idle-noise stratum with two deterministic VAD false positives."),
    ("known_positives_and_negatives",
     "Include known positives and negatives",
     "Ninety speech-positive frames, twenty missed quiet frames, twenty VAD "
     "false-positive frames and 530 true-negative frames."),
    ("onset_offset_delay",
     "Measure onset/offset and end-of-turn delay",
     "Cutoff is a negative signed decision delay; every decision reports "
     "samples and milliseconds."),
    ("stratified_fn_fp",
     "Report stratified false negatives and false positives",
     "Per-stratum speech/nonspeech/unknown sample counts are reported "
     "separately."),
    ("validity_separate_from_nonspeech",
     "Keep validity separate from nonspeech",
     "Forty unknown frames are excluded from all denominators and are never "
     "relabelled nonspeech or a completed turn."),
    ("independent_state",
     "Verify independent state",
     "One fresh session per turn and per policy with exact epoch-bound "
     "digests."),
    ("exact_source_intervals",
     "Use exact source intervals",
     "Half-open 160-sample frames partition [0, 112000) exactly."),
    ("availability",
     "Report availability",
     "Activity and endpoint availability use an explicit monotonic clock and "
     "fixed formulas."),
    ("dropped_and_stale_events",
     "Audit dropped and stale events",
     "Duplicate, stale, wrong-clock, wrong-epoch, nonfinite, out-of-range and "
     "wrong-width cases are rejected."),
    ("cross_hop",
     "Verify cross-hop behavior",
     "A non-aligned span projects onto exact hop overlaps with conserved "
     "sample totals."),
    ("endpoint_separate_from_framewise_vad",
     "Emit endpoint decisions separately from framewise VAD",
     "Activity events and endpoint decisions are distinct event types, "
     "streams and digests."),
    ("max_wait_fallback",
     "Measure maximum-wait fallback",
     "The gated policy records one forced maximum-wait decision and its signed "
     "cutoff."),
)

ASSET_REQUIREMENTS = (
    ("model_asset_with_sha256",
     "Caller-supplied turn-detector asset with an observed SHA-256"),
    ("exact_variant_and_revision",
     "Exact model variant, revision and build identity"),
    ("license_text_and_rights_decision",
     "LiveKit Model License text and a written rights decision"),
    ("runtime_package_and_python_pair",
     "Pinned runtime package and Python 3.12.16 pair"),
    ("input_geometry_and_preprocessing",
     "Published input geometry, context mode and preprocessing"),
    ("calibrated_thresholds",
     "Per-language calibrated unlikely thresholds"),
    ("turn_labelled_cohort",
     "Rights-qualified turn-labelled cohort with unknown regions"),
    ("independent_review_and_release",
     "Independent exact-head review, hosted CI and release approval"),
)


def _common() -> dict:
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "format": FORMAT,
        "task": TASK,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_key": PROFILE_KEY,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "depends_on": list(DEPENDS_ON),
        "write_scope": WRITE_SCOPE,
        "proposal_only": True,
        "incomplete": True,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "boundary": dict(BOUNDARY_FLAGS),
        "scope": dict(SCOPE_FLAGS),
        "gates": [
            {"id": gate_id, "blocked": True, "requirement": requirement}
            for gate_id, requirement in zip(GATE_IDS, GATE_REQUIREMENTS)
        ],
        "exact_blockers": [
            {
                "id": item["id"],
                "state": "open",
                "blocker": item["blocker"],
                "reopen_condition": item["reopen_condition"],
            }
            for item in BLOCKERS
        ],
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "candidate_qualified": False,
            "missing_result_promoted": False,
            "no_missing_result_qualifies_candidate": True,
            "processor_exposure": False,
            "proposal_only": True,
            "blocked_gate_count": len(GATE_IDS),
            "blocked_gate_ids": list(GATE_IDS),
        },
        "upstream_record": {
            "product": UPSTREAM_PRODUCT,
            "vendor": UPSTREAM_VENDOR,
            "docs_url": UPSTREAM_DOCS_URL,
            "turns_url": UPSTREAM_TURNS_URL,
            "source_url": UPSTREAM_SOURCE_URL,
            "license_url": UPSTREAM_LICENSE_URL,
            "license_id": UPSTREAM_LICENSE_ID,
            "license_text_observed": False,
            "license_apache_2_0": False,
            "base_model": UPSTREAM_BASE_MODEL,
            "variants": [dict(item) for item in MODEL_VARIANTS],
            "exact_revision": None,
            "revision_pin_available": False,
            "asset_sha256": None,
            "asset_digest_observed": False,
            "weights_available_offline": False,
            "network_required_for_full_model": True,
            "credentials_required_for_full_model": True,
            "package_install_required_for_local_variant": True,
            "supported_languages": 14,
            "text_model_deprecated": True,
            "endpoint_defaults_documented": dict(ENDPOINT_DEFAULTS_DOCUMENTED),
        },
        "geometry": {
            "model_geometry_status": "unestablished",
            "audio_frame_geometry_published": False,
            "sample_rate_hz": None,
            "channels": None,
            "hop_samples": None,
            "latency_samples": None,
            "preprocessing_published": False,
            "context_mode_published": True,
            "transcript_conditioned_text_model": True,
            "audio_conditioned_mini_model": True,
            "policy_defaults_documented": dict(ENDPOINT_DEFAULTS_DOCUMENTED),
            "policy_defaults_measured": False,
            "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        },
        "task_row_identity": board_row_projection(),
        "qualification_reason": (
            "No pinned turn-detector asset, weight digest, runtime, licence "
            "decision, input geometry, calibrated threshold or turn-labelled "
            "cohort is available. The package records a fail-closed "
            "caller-supplied-asset contract and a synthetic policy control "
            "only; the candidate is DEFER/incomplete/not_qualified."),
        "release_gates": [
            {"id": gate_id, "blocked": True, "requirement": requirement}
            for gate_id, requirement in zip(GATE_IDS, GATE_REQUIREMENTS)
        ],
        "asset_requirements": [
            {"id": item_id, "requirement": requirement, "status": "absent"}
            for item_id, requirement in ASSET_REQUIREMENTS
        ],
        "absence_probes": absence_probes(),
        "asset_audit": {
            "qualified": False,
            "audit_result": "absent",
            "source": {"present": False},
            "runtime": {"present": False},
            "rights": {"present": False},
            "cohort": {"present": False},
            "absence": absence_summary(absence_probes()),
            "observed_absence_probes": absence_probes(),
        },
        "missing_historical_artifacts": list(MISSING_HISTORICAL_ARTIFACTS),
        "candidate_metrics": None,
        "determinism": {
            "cold_start_regenerations_required": 3,
            "canonical_json": True,
            "sorted_keys": True,
            "floats_permitted": False,
        },
        "reproduction": {
            "python": "3.12.16",
            "environment": "PYTHONDONTWRITEBYTECODE=1",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py",
            "check": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py --check",
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                      "test_reference.py"),
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "comparison": "exact SHA-256 over canonical JSON; no tolerance",
        },
    }


def _analysis_profile() -> dict:
    items = []
    for item_id, requirement, evidence in ANALYSIS_REQUIREMENTS:
        items.append({
            "id": item_id,
            "requirement": requirement,
            "status": "synthetic_control_only",
            "evidence": evidence,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        })
    return {
        "profile": PROFILE,
        "source": PROFILE_SOURCE_REL,
        "candidate_evaluated": False,
        "satisfied_for_qualification": [],
        "required_items": items,
    }


def _caller_asset_contract() -> dict:
    return {
        "schema_id": ASSET_SCHEMA_ID,
        "required_fields": sorted(ASSET_MANIFEST_KEYS),
        "accepted_variants": sorted(ASSET_VARIANTS),
        "required_license": ASSET_LICENSE_ID,
        "license_acknowledgement_required": True,
        "requires_caller_supplied": True,
        "vendored_in_package": False,
        "redistribution_permitted": False,
        "digest_required": True,
        "asset_sha256_required": True,
        "exact_revision_required": True,
        "geometry_required": True,
        "context_mode_by_variant": {
            "v1": "agent-message+audio",
            "v1-mini": "audio",
            "text-multilingual": "transcript",
        },
        "threshold_range_permille": {"minimum": 1, "maximum": 999},
        "absent_behavior": "reject_before_processing",
        "asset_is_vendored": False,
        "required_source_revision": None,
        "revision_pin_available": False,
        "positive_fixture_accepted": validate_asset_manifest(
            positive_asset_fixture())[0],
        "admission_probe_count": len(ADVERSE_ASSET_CASE_IDS),
        "all_probes_rejected": all(
            not case["accepted"] for case in adverse_asset_cases()),
    }


def _policy_delta() -> dict:
    vad = [item["delay_samples"] for item in policy_decisions("vad_only")
           if item["delay_samples"] is not None]
    gated = [item["delay_samples"] for item in policy_decisions("gated")
             if item["delay_samples"] is not None]
    improvement = (Fraction(sum(abs(value) for value in vad), len(vad))
                   - Fraction(sum(abs(value) for value in gated), len(gated)))
    return {
        "cutoff_count_reduction": (
            policy_metrics("vad_only")["cutoff_count"]
            - policy_metrics("gated")["cutoff_count"]),
        "worst_cutoff_improvement_samples": (
            policy_metrics("gated")["worst_cutoff_samples"]
            - policy_metrics("vad_only")["worst_cutoff_samples"]),
        "mean_absolute_delay_improvement_samples":
            fraction_text(improvement),
    }


def _synthetic_policy_control() -> dict:
    vad_only = policy_metrics("vad_only")
    gated = policy_metrics("gated")
    return {
        "label": "synthetic_endpoint_policy_control_not_model_output",
        "fixture": {
            "clock": CLOCK,
            "origin_ns": ORIGIN_NS,
            "ns_per_sample": NS_PER_SAMPLE,
            "frame_samples": FRAME_SAMPLES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "frame_ms": FRAME_MS,
            "total_frames": TOTAL_FRAMES,
            "total_samples": TOTAL_SAMPLES,
            "turns": [dict(item) for item in TURNS],
            "segments": [
                {"start_frame": start, "end_frame": end, "stratum": stratum,
                 "turn_id": turn_id}
                for start, end, stratum, turn_id in SEGMENTS
            ],
            "vad_false_positive_spans": [
                {"start_frame": start, "end_frame": end}
                for start, end in VAD_FALSE_POSITIVE_SPANS
            ],
            "policy": {
                "min_delay_frames": MIN_DELAY_FRAMES,
                "max_delay_frames": MAX_DELAY_FRAMES,
                "threshold_permille": THRESHOLD_PERMILLE,
                "min_delay_ms": MIN_DELAY_FRAMES * FRAME_MS,
                "max_delay_ms": MAX_DELAY_FRAMES * FRAME_MS,
            },
        },
        "framewise_vad": framewise_metrics(),
        "probability_control": brier_control(),
        "policies": {
            "vad_only": vad_only,
            "gated": gated,
        },
        "delta": _policy_delta(),
        "event_streams": {
            "vad_only": event_stream("vad_only", 1),
            "gated": event_stream("gated", 2),
        },
        "cross_hop": {
            "span_start_sample": 120,
            "span_end_sample": 420,
            "hop_samples": FRAME_SAMPLES,
            "projection": cross_hop_project(120, 420),
            "total_overlap_samples": sum(
                row["overlap_samples"]
                for row in cross_hop_project(120, 420)),
        },
        "independent_state": {
            "session_epochs": [1, 2, 3, 4],
            "session_count": len(TURNS),
            "per_turn_sessions": True,
            "state_isolated": True,
        },
        "adverse_controls": {
            "adverse_asset_cases": adverse_asset_cases(),
            "all_rejected": all(
                not case["accepted"] for case in adverse_asset_cases()),
            "positive_fixture_accepted": validate_asset_manifest(
                positive_asset_fixture())[0],
            "invalid_frames_rejected": True,
            "stale_and_duplicate_events_rejected": True,
            "unknown_never_scored": True,
            "missing_result_never_qualifies": True,
        },
        "non_claims": [
            "No LiveKit model, weight, package or remote inference was loaded.",
            "No real audio, corpus, recording, listening or device timing was used.",
            "The synthetic trace is not a model posterior and not an accuracy result.",
            "No endpoint accuracy, cutoff rate, latency, benchmark or release claim is made.",
        ],
    }


def _source_reported_context() -> dict:
    return {
        "label": "source_reported_not_measured_here",
        "source_url": UPSTREAM_DOCS_URL,
        "source_tree_url": UPSTREAM_SOURCE_URL,
        "license_url": UPSTREAM_LICENSE_URL,
        "facts": [
            {
                "id": "SR-1",
                "claim": "v1 is a multimodal model served on LiveKit Inference; "
                         "v1-mini runs locally on CPU and falls back from v1.",
                "scope": "documentation only; not reproduced",
            },
            {
                "id": "SR-2",
                "claim": "The deprecated text model is an open-weights "
                         "Qwen2.5-0.5B-Instruct derivative, 396 MB on disk, "
                         "~50-160 ms per turn.",
                "scope": "documentation only; weights and latency not observed",
            },
            {
                "id": "SR-3",
                "claim": "The text model reports English TPR 99.3% and TNR "
                         "87.0% across 14 languages.",
                "scope": "documentation only; no cohort and not reproduced",
            },
            {
                "id": "SR-4",
                "claim": "Endpointing defaults are 0.3/2.5 s with the "
                         "multimodal detector and 0.5/3.0 s otherwise.",
                "scope": "documentation only; policy not measured",
            },
            {
                "id": "SR-5",
                "claim": "The text model and v1-mini use the LiveKit Model "
                         "License.",
                "scope": "documentation only; licence text not observed",
            },
        ],
        "not_reproduced": True,
        "not_pooled": True,
    }


def build_report() -> dict:
    report = _common()
    report.update({
        "schema_id": REPORT_SCHEMA_ID,
        "analysis_profile": _analysis_profile(),
        "caller_asset_contract": _caller_asset_contract(),
        "synthetic_policy_control": _synthetic_policy_control(),
        "source_reported_context": _source_reported_context(),
        "non_claims": [
            "No runnable LiveKit model, weight, asset, package or remote "
            "inference was used.",
            "No real audio, corpus, recording, listening, device timing, "
            "benchmark or release evidence is present.",
            "Synthetic policy-control metrics are not candidate accuracy, "
            "latency or parity results.",
            "No provider, default, ABI, CONTRACTS.md, registry, shared build, "
            "CI, board or handoff change is included.",
        ],
    })
    return report


def build_contract() -> dict:
    contract = _common()
    contract.update({
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "analysis_requirement_ids": [item[0] for item in ANALYSIS_REQUIREMENTS],
        "caller_asset_contract": _caller_asset_contract(),
        "required_artifacts": [
            "LICENSES.md",
            "README.md",
            "SOURCES.sha256",
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
        ],
        "source_reported_context": _source_reported_context(),
        "non_claims": [
            "No runnable LiveKit model, weight, asset, package or remote "
            "inference was used.",
            "No real audio, corpus, listening, device timing, benchmark or "
            "release evidence is present.",
            "Synthetic policy-control metrics are not candidate accuracy, "
            "latency or parity results.",
        ],
        "reproduction": {
            "python": "3.12.16",
            "environment": "PYTHONDONTWRITEBYTECODE=1",
            "cold_start_regenerations": 3,
            "report": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py",
            "check": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py --check",
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                      "test_reference.py"),
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "comparison": "exact SHA-256 over canonical JSON; no tolerance",
        },
        "release_gates": [
            {"id": gate_id, "blocked": True, "requirement": requirement}
            for gate_id, requirement in zip(GATE_IDS, GATE_REQUIREMENTS)
        ],
        "reference_status": {
            "asset_present": False,
            "asset_pinned": False,
            "model_loaded": False,
            "model_executed": False,
            "synthetic_control_present": True,
            "qualification_from_control": "none",
        },
    })
    return contract
