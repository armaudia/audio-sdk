# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-FASTCONFORMER-STREAMING-ASR.

This module is standard-library only and deterministic. It contains no
FastConformer/Conformer checkpoint, NeMo source, CUDA runtime, tokenizer,
transcript, audio signal, ASR inference path or recognition result.

The candidate label in the research record, "Streaming Conformer-TED /
FastConformer", is underspecified and has no exact checkpoint. The pinned
evidence says a different Conformer would silently change the candidate, so
this package records the exact missing artifacts and a fail-closed admission
boundary instead of substituting a model or fabricating a result.

The only executable control is a deterministic streaming *scheduler* surrogate.
It models SDK v0 frame/chunk accounting (160-sample frames, 1280-sample = 80 ms
chunks) and cache-epoch/reset/flush bookkeeping. It performs no feature
extraction, no encoder pass, no decoding, no token or transcript emission and no
accuracy, latency or quality measurement.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import struct
from collections.abc import Sequence
from pathlib import Path
from typing import Any

TASK = "SDK-FASTCONFORMER-STREAMING-ASR"
COMPONENT_ID = "fastconformer-streaming-asr"
TASK_TITLE = "FastConformer streaming ASR"
CONTRACT_ID = "audio-sdk/fastconformer-streaming-asr-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/fastconformer-streaming-asr-candidate-manifest/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "feasibility"
BASE_COMMIT = "9cf118bc32ff5ac801318158d97d5bb8dd947374"
BRANCH = "swarm/SDK-FASTCONFORMER-STREAMING-ASR"
WRITE_SCOPE = "docs/task-evidence/fastconformer-streaming-asr/ only"
TASK_PREFIX = "docs/task-evidence/fastconformer-streaming-asr/"
STATUS = "proposal_only_synthetic_incomplete"
DECISION = "DEFER"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DISPOSITION = (
    "FastConformer/Conformer-TED streaming-ASR readiness blocker; no exact "
    "candidate, checkpoint, runtime, corpus, inference, result or release.")

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
CHUNK_SAMPLES = 1280
CHUNK_MS = 80
SAMPLE_FORMAT = "f32"

CANDIDATE_MATRIX = "research/voice-enhancement-20261101/candidate_matrix.csv"
CANDIDATE_RECORD = 35
CANDIDATE_RECORD_NAME = "Streaming Conformer-TED / FastConformer"
CANDIDATE_RECORD_STATUS = "unavailable/blocked"
CANDIDATE_RECORD_FINDING = (
    "No exact TED checkpoint, streaming config or local ASR runtime; using "
    "another Conformer would change candidate identity.")
CANDIDATE_COMPARISON = "Whisper streaming ASR; fixed transcript"
CANDIDATE_REPORT_PATHS = (
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
)

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

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable linked-row identity may gate anything.
SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/asr-word-timestamps/contract.json":
        "65361e29cf8a04fd64ad4a25b4fd3094fffaf2f56ad911ea6076e7fef592822a",
    "docs/task-evidence/dpdfnet-2-streaming/contract.json":
        "225e0072f021bd592cd5a4685ded735063423c1dda730f065b56652457360ad5",
    "docs/task-evidence/whisper-tiny-en-mfa/contract.json":
        "fddc819bdcbb34a4d47f605efa8c0632573eaa2b77d0681d2a82f5c58e98687e",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

# Fixed probes only; no recursive workspace walk. These are the recorded
# candidate/runtime locations for this task and remain absent.
WORKSPACE_ABSENCE_PROBES = (
    "data/models/nemo-fastconformer",
    "data/models/fastconformer-streaming",
    "data/checkouts/NeMo",
    "data/checkouts/nemo",
    "data/envs/nemo",
    "data/wheels/nemo_toolkit.whl",
    "data/manifests/fastconformer-streaming-asr.json",
    "data/runs/fastconformer-streaming-asr",
)
EXTERNAL_ABSENCE_PROBES = (
    "/private/tmp/nemo-env",
    "/private/tmp/nemo-model",
    "/private/tmp/fastconformer",
    "/private/tmp/nemo-cache",
)

RUNTIME_MODULES = (
    "nemo",
    "nemo_toolkit",
    "torch",
    "torchaudio",
    "onnxruntime",
    "sherpa_onnx",
    "transformers",
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/+:-]{0,127}$")


# ---------------------------------------------------------------------------
# Canonical JSON and file digests
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def canonical_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json_constant:" + token)


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def read_strict_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=_reject_constant,
                      object_pairs_hook=_strict_pairs)


def _no_floats(value: Any, path: str = "document") -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed:" + path)
    if isinstance(value, dict):
        for key, child in value.items():
            _no_floats(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _no_floats(child, path + f"[{index}]")


# ---------------------------------------------------------------------------
# Board identity (stable projection only)
# ---------------------------------------------------------------------------

def board_row_projection(board_path: Path, task: str = TASK) -> dict:
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_not_a_list")
    matches = [row for row in tasks
               if isinstance(row, dict) and row.get("id") == task]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    row = matches[0]
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(row: dict) -> str:
    return object_digest(row)


def linked_rows() -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW
    rows = [board_row_projection(board, task) for task in LINKED_ROW_IDS]
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


# ---------------------------------------------------------------------------
# Absence and runtime presence
# ---------------------------------------------------------------------------

def _present(path: Path) -> bool:
    try:
        return path.exists() or path.is_symlink()
    except OSError:
        return True


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    for relative in WORKSPACE_ABSENCE_PROBES:
        rows.append({"path": relative, "scope": "workspace",
                     "kind": "recorded_candidate_path",
                     "present": _present(AUDIO_ROOT / relative)})
    for absolute in EXTERNAL_ABSENCE_PROBES:
        rows.append({"path": absolute, "scope": "external",
                     "kind": "recorded_runtime_path",
                     "present": _present(Path(absolute))})
    return rows


def absence_summary() -> dict:
    rows = absence_probes()
    present = [row for row in rows if row["present"]]
    return {
        "probe_count": len(rows),
        "workspace_probe_count": sum(1 for row in rows
                                     if row["scope"] == "workspace"),
        "external_probe_count": sum(1 for row in rows
                                    if row["scope"] == "external"),
        "present_count": len(present),
        "all_probes_absent": not present,
        "download_attempted": False,
        "network_used": False,
        "recursive_workspace_walk": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
    }


def runtime_modules() -> list[dict]:
    rows: list[dict] = []
    for module in RUNTIME_MODULES:
        try:
            available = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            available = False
        rows.append({"module": module, "available": available})
    return rows


def runtime_presence() -> dict:
    rows = runtime_modules()
    by_name = {row["module"]: row["available"] for row in rows}
    nemo_present = bool(by_name.get("nemo") or by_name.get("nemo_toolkit"))
    return {
        "modules": rows,
        "import_attempted": False,
        "nemo_present": nemo_present,
        "torch_present": bool(by_name.get("torch")),
        "cuda_runtime_present": False,
        "exact_runtime_artifact_present": False,
        "runtime_present": nemo_present,
    }


def source_presence() -> dict:
    summary = absence_summary()
    runtime = runtime_presence()
    return {
        "research_report_and_matrix_present": True,
        "research_report_and_matrix_verified": True,
        "exact_candidate_identity_recorded": False,
        "checkpoint_bytes_present": False,
        "weights_present": False,
        "runtime_present": runtime["runtime_present"],
        "cuda_runtime_present": False,
        "corpus_present": False,
        "transcripts_present": False,
        "reference_outputs_present": False,
        "exact_source_weights_runtime_conjunction_present": False,
        "weights_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "model_executed": False,
        "network_used": False,
        "provenance_rows": len(SOURCE_PINS) + len(BOUNDARY_PINS),
        "absence_present_count": summary["present_count"],
    }


# ---------------------------------------------------------------------------
# Streaming scheduler surrogate (no ASR)
# ---------------------------------------------------------------------------

class SchedulerError(ValueError):
    """Fail-closed scheduler rejection with a stable code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _validate_samples(samples: Any) -> list[float]:
    if isinstance(samples, (str, bytes, bytearray)) or not isinstance(
            samples, Sequence):
        raise SchedulerError("not_a_sample_sequence")
    values: list[float] = []
    for value in samples:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SchedulerError("invalid_sample_type")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise SchedulerError("nonfinite_sample")
        if numeric < -1.0 or numeric > 1.0:
            raise SchedulerError("sample_out_of_range")
        values.append(numeric)
    return values


class StreamingScheduler:
    """Deterministic chunk/cache scheduler; no model or signal processing."""

    def __init__(self, chunk_samples: int = CHUNK_SAMPLES,
                 frame_samples: int = FRAME_SAMPLES) -> None:
        if (type(chunk_samples) is not int or type(frame_samples) is not int
                or frame_samples != FRAME_SAMPLES
                or chunk_samples % frame_samples != 0
                or chunk_samples <= 0):
            raise SchedulerError("invalid_chunk_geometry")
        self._chunk_samples = chunk_samples
        self._frame_samples = frame_samples
        self._buffer: list[float] = []
        self._events: list[dict] = []
        self._consumed = 0
        self._real_samples = 0
        self._padding = 0
        self._cache_samples = 0
        self._cache_epoch = 0
        self._flushed = False
        self._closed = False

    @property
    def chunk_samples(self) -> int:
        return self._chunk_samples

    def _event(self, kind: str, real_samples: int) -> dict:
        start = self._consumed
        end = start + real_samples
        frames = (real_samples + self._frame_samples - 1) // self._frame_samples
        padding = self._chunk_samples - real_samples if kind == "final_partial" \
            else 0
        self._consumed = end
        if kind == "chunk":
            self._cache_samples = self._chunk_samples
        event = {
            "index": len(self._events),
            "kind": kind,
            "chunk_samples": self._chunk_samples,
            "real_samples": real_samples,
            "source_start_sample": start,
            "source_end_sample": end,
            "frames": frames,
            "internal_padding_samples": padding,
            "cache_samples_retained": self._cache_samples,
            "cache_epoch": self._cache_epoch,
        }
        self._events.append(event)
        return event

    def push(self, samples: Any) -> list[dict]:
        if self._closed:
            raise SchedulerError("scheduler_closed")
        if self._flushed:
            raise SchedulerError("scheduler_flushed")
        values = _validate_samples(samples)
        self._buffer.extend(values)
        self._real_samples += len(values)
        emitted: list[dict] = []
        while len(self._buffer) >= self._chunk_samples:
            del self._buffer[:self._chunk_samples]
            emitted.append(self._event("chunk", self._chunk_samples))
        return emitted

    def flush(self) -> list[dict]:
        if self._closed:
            raise SchedulerError("scheduler_closed")
        if self._flushed:
            return []
        self._flushed = True
        remaining = len(self._buffer)
        if not remaining:
            return []
        self._padding += self._chunk_samples - remaining
        self._buffer.clear()
        return [self._event("final_partial", remaining)]

    def reset(self) -> None:
        if self._closed:
            raise SchedulerError("scheduler_closed")
        self._buffer.clear()
        self._events.clear()
        self._consumed = 0
        self._real_samples = 0
        self._padding = 0
        self._cache_samples = 0
        self._cache_epoch += 1
        self._flushed = False

    def close(self) -> None:
        self._closed = True

    def _buffer_digest(self) -> str:
        digest = hashlib.sha256()
        for value in self._buffer:
            digest.update(struct.pack(">d", value))
        return digest.hexdigest()

    def fingerprint(self) -> str:
        payload = {
            "chunk_samples": self._chunk_samples,
            "frame_samples": self._frame_samples,
            "buffer_length": len(self._buffer),
            "buffer_digest": self._buffer_digest(),
            "consumed": self._consumed,
            "real_samples": self._real_samples,
            "padding": self._padding,
            "cache_samples": self._cache_samples,
            "flushed": self._flushed,
            "closed": self._closed,
        }
        return object_digest(payload)

    def state_digest(self) -> str:
        payload = {
            "fingerprint": self.fingerprint(),
            "cache_epoch": self._cache_epoch,
            "events": self._events,
        }
        return object_digest(payload)

    def events(self) -> list[dict]:
        return copy.deepcopy(self._events)

    def counters(self) -> dict:
        return {
            "input_samples": self._real_samples,
            "valid_source_samples": self._real_samples,
            "consumed_source_samples": self._consumed,
            "internal_padding_samples": self._padding,
            "scheduled_chunk_samples": self._consumed + self._padding,
            "event_count": len(self._events),
            "completed_chunk_count": sum(1 for event in self._events
                                         if event["kind"] == "chunk"),
            "final_partial_chunk_count": sum(
                1 for event in self._events
                if event["kind"] == "final_partial"),
            "cache_epoch": self._cache_epoch,
            "flushed": self._flushed,
            "closed": self._closed,
        }


def structural_event_digest(events: list[dict]) -> str:
    stripped = [{key: value for key, value in event.items()
                 if key != "cache_epoch"} for event in events]
    return object_digest(stripped)


def synthetic_signal(kind: str, count: int) -> list[float]:
    if type(count) is not int or count < 0:
        raise SchedulerError("invalid_signal_length")
    if kind == "zeros":
        return [0.0] * count
    if kind == "ramp":
        return [(((index * 37) % 2001) - 1000) / 2000.0
                for index in range(count)]
    if kind == "impulse":
        values = [0.0] * count
        if count:
            values[count // 2] = 0.5
        return values
    raise SchedulerError("unknown_signal_kind")


def _run_signal(kind: str, count: int, chunk_size: int) -> dict:
    scheduler = StreamingScheduler()
    signal = synthetic_signal(kind, count)
    emitted = 0
    calls = 0
    for offset in range(0, count, chunk_size):
        calls += 1
        emitted += len(scheduler.push(signal[offset:offset + chunk_size]))
    emitted += len(scheduler.flush())
    counters = scheduler.counters()
    events = scheduler.events()
    return {
        "chunk_size": chunk_size,
        "push_calls": calls,
        "event_count": counters["event_count"],
        "emitted_event_count": emitted,
        "completed_chunk_count": counters["completed_chunk_count"],
        "final_partial_chunk_count": counters["final_partial_chunk_count"],
        "final_partial_real_samples": (
            events[-1]["real_samples"]
            if events and events[-1]["kind"] == "final_partial" else 0),
        "internal_padding_samples": counters["internal_padding_samples"],
        "valid_source_samples": counters["valid_source_samples"],
        "consumed_source_samples": counters["consumed_source_samples"],
        "scheduled_chunk_samples": counters["scheduled_chunk_samples"],
        "event_digest": structural_event_digest(events),
    }


def scheduler_control() -> dict:
    conditions = (
        {"id": "SIL-32000", "kind": "zeros", "samples": 32000},
        {"id": "RAMP-32000", "kind": "ramp", "samples": 32000},
        {"id": "IMP-32000", "kind": "impulse", "samples": 32000},
        {"id": "PARTIAL-32037", "kind": "ramp", "samples": 32037},
    )
    rows: list[dict] = []
    for condition in conditions:
        run = _run_signal(condition["kind"], condition["samples"],
                          CHUNK_SAMPLES)
        rows.append({"id": condition["id"], **run})
    chunk_sizes = (1, 7, 80, 159, 160, 161, 320, 1280, 32000)
    digests: list[str] = []
    chunks_total = 0
    for size in chunk_sizes:
        chunks_total += (32000 + size - 1) // size
        digests.append(_run_signal("ramp", 32000, size)["event_digest"])
    chunk_independence = {
        "chunk_sizes": list(chunk_sizes),
        "digests": digests,
        "all_equal": len(set(digests)) == 1,
        "caller_chunks_total": chunks_total,
        "input_samples": 32000,
    }

    lifecycle = StreamingScheduler()
    initial = lifecycle.fingerprint()
    lifecycle.push(synthetic_signal("ramp", 5001))
    mid = lifecycle.fingerprint()
    lifecycle.reset()
    after_reset = lifecycle.fingerprint()
    replay = StreamingScheduler()
    replay_events = replay.push(synthetic_signal("ramp", 32037))
    replay_final = replay.flush()
    first = StreamingScheduler()
    first_events = first.push(synthetic_signal("ramp", 32037))
    first_final = first.flush()
    second_final = first.flush()
    first.close()
    first.close()
    lifecycle_checks = {
        "reset_restores_initial_fingerprint": initial == after_reset,
        "pre_reset_fingerprint_differs": initial != mid,
        "replay_event_digest_matches": structural_event_digest(
            first_events + first_final) == structural_event_digest(
                replay_events + replay_final),
        "second_flush_is_empty": second_final == [],
        "close_is_idempotent": True,
        "fresh_cache_epoch": 0,
        "reset_cache_epoch": lifecycle._cache_epoch,
    }

    adverse_cases = (
        ("EMPTY-TYPE", "not_a_sample_sequence", None),
        ("STRING", "not_a_sample_sequence", "abc"),
        ("BOOL-ELEMENT", "invalid_sample_type", [True]),
        ("NAN", "nonfinite_sample", [float("nan")]),
        ("INF", "nonfinite_sample", [float("inf")]),
        ("OUT-OF-RANGE", "sample_out_of_range", [1.5]),
        ("DICT", "not_a_sample_sequence", {"x": 1}),
    )
    adverse_rows: list[dict] = []
    for case_id, expected, value in adverse_cases:
        scheduler = StreamingScheduler()
        scheduler.push(synthetic_signal("ramp", 777))
        before = scheduler.state_digest()
        try:
            scheduler.push(value)
            observed = "accepted"
        except SchedulerError as error:
            observed = error.code
        after = scheduler.state_digest()
        adverse_rows.append({
            "id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "rejected": observed == expected,
            "state_unchanged": before == after,
            "qualifies": False,
        })

    return {
        "kind": "deterministic stdlib streaming scheduler surrogate",
        "performs_asr": False,
        "uses_model_or_weights": False,
        "signal_processing": False,
        "geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "chunk_samples": CHUNK_SAMPLES,
            "chunk_ms": CHUNK_MS,
            "sample_format": SAMPLE_FORMAT,
        },
        "conditions": rows,
        "chunk_independence": chunk_independence,
        "lifecycle": lifecycle_checks,
        "adverse": adverse_rows,
        "synthetic_signal_control_only": True,
        "substitutes_for_candidate": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed admission for a future exact candidate manifest
# ---------------------------------------------------------------------------

class AdmissionError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _object(value: Any, expected: tuple[str, ...], code: str) -> dict:
    if not isinstance(value, dict):
        raise AdmissionError(code)
    if set(value) != set(expected):
        raise AdmissionError(code)
    return value


def _text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise AdmissionError(code)
    return value


def _int(value: Any, minimum: int, maximum: int, code: str) -> int:
    if type(value) is not int or value < minimum or value > maximum:
        raise AdmissionError(code)
    return value


def _bool(value: Any, expected: bool, code: str) -> bool:
    if type(value) is not bool or value is not expected:
        raise AdmissionError(code)
    return value


def _hex(value: Any, length: int, code: str) -> str:
    if not isinstance(value, str):
        raise AdmissionError(code)
    pattern = HEX40 if length == 40 else HEX64
    if not pattern.fullmatch(value) or value == ("0" * length):
        raise AdmissionError(code)
    return value


def validate_manifest(manifest: Any) -> None:
    top = _object(manifest, ("schema_id", "candidate", "runtime", "streaming",
                             "assets", "evaluation", "provider"),
                  "manifest_fields")
    if top["schema_id"] != ADMISSION_SCHEMA_ID:
        raise AdmissionError("manifest_schema")

    candidate = _object(top["candidate"], (
        "candidate_id", "family", "model_id", "source_revision",
        "checkpoint_files", "config_sha256", "tokenizer_sha256", "license"),
        "candidate_fields")
    candidate_id = _text(candidate["candidate_id"], "candidate_id")
    if candidate_id.lower() in {"schema-control", "synthetic",
                                "family-only", "fastconformer-family"}:
        raise AdmissionError("candidate_not_exact")
    if candidate["family"] != "cache_aware_fastconformer_streaming":
        raise AdmissionError("candidate_family")
    _text(candidate["model_id"], "model_id")
    _hex(candidate["source_revision"], 40, "source_revision_mutable")
    _hex(candidate["config_sha256"], 64, "config_sha256")
    _hex(candidate["tokenizer_sha256"], 64, "tokenizer_sha256")
    files = candidate["checkpoint_files"]
    if not isinstance(files, list) or not 1 <= len(files) <= 64:
        raise AdmissionError("checkpoint_files")
    names: set[str] = set()
    for item in files:
        row = _object(item, ("name", "byte_count", "sha256"),
                      "checkpoint_file_fields")
        name = _text(row["name"], "checkpoint_name")
        if name in names:
            raise AdmissionError("checkpoint_duplicate")
        names.add(name)
        _int(row["byte_count"], 1, 1 << 40, "checkpoint_byte_count")
        _hex(row["sha256"], 64, "checkpoint_sha256")
    license_row = _object(candidate["license"], (
        "spdx", "terms_reviewed", "redistribution_approved",
        "output_use_approved"), "license_fields")
    _text(license_row["spdx"], "license_spdx")
    _bool(license_row["terms_reviewed"], True, "license_terms")
    _bool(license_row["redistribution_approved"], True,
          "license_redistribution")
    _bool(license_row["output_use_approved"], True, "license_output_use")

    runtime = _object(top["runtime"], (
        "name", "version", "artifact_sha256", "offline_load", "device_class"),
        "runtime_fields")
    _text(runtime["name"], "runtime_name")
    _text(runtime["version"], "runtime_version")
    _hex(runtime["artifact_sha256"], 64, "runtime_sha256")
    _bool(runtime["offline_load"], True, "runtime_offline_load")
    if runtime["device_class"] not in {"gpu", "cpu"}:
        raise AdmissionError("runtime_device")

    streaming = _object(top["streaming"], (
        "transport_ms", "chunk_ms", "cache_frames", "lookahead_ms"),
        "streaming_fields")
    _int(streaming["transport_ms"], 1, 1000, "streaming_transport_ms")
    _int(streaming["chunk_ms"], 1, 10000, "streaming_chunk_ms")
    _int(streaming["cache_frames"], 0, 4096, "streaming_cache_frames")
    _int(streaming["lookahead_ms"], 0, 60000, "streaming_lookahead_ms")

    assets = _object(top["assets"], (
        "storage", "download_permitted", "caller_owned"), "assets_fields")
    if assets["storage"] != "external":
        raise AdmissionError("asset_storage")
    _bool(assets["download_permitted"], False, "asset_download")
    _bool(assets["caller_owned"], True, "asset_caller_owned")

    evaluation = _object(top["evaluation"], (
        "corpus_id", "split_id", "transcript_sha256", "scorer_id",
        "reference_outputs_sha256", "rights_reviewed",
        "listening_permitted"), "evaluation_fields")
    _text(evaluation["corpus_id"], "corpus_id")
    _text(evaluation["split_id"], "split_id")
    _hex(evaluation["transcript_sha256"], 64, "transcript_sha256")
    _text(evaluation["scorer_id"], "scorer_id")
    _hex(evaluation["reference_outputs_sha256"], 64,
         "reference_outputs_sha256")
    _bool(evaluation["rights_reviewed"], True, "corpus_rights")
    _bool(evaluation["listening_permitted"], True, "listening_permission")

    provider = _object(top["provider"], (
        "registered", "default_selected", "opt_in"), "provider_fields")
    _bool(provider["registered"], False, "provider_registered")
    _bool(provider["default_selected"], False, "provider_default")
    _bool(provider["opt_in"], True, "provider_opt_in")


def control_manifest() -> dict:
    """Schema-only control. It is not the candidate and never qualifies."""
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "candidate": {
            "candidate_id": "schema-control-not-qualifying",
            "family": "cache_aware_fastconformer_streaming",
            "model_id": "schema-control/not-a-candidate",
            "source_revision": "1" * 40,
            "checkpoint_files": [{
                "name": "schema-control.bin",
                "byte_count": 1,
                "sha256": "2" * 64,
            }],
            "config_sha256": "3" * 64,
            "tokenizer_sha256": "4" * 64,
            "license": {
                "spdx": "NOASSERTION",
                "terms_reviewed": True,
                "redistribution_approved": True,
                "output_use_approved": True,
            },
        },
        "runtime": {
            "name": "schema-control-runtime",
            "version": "0",
            "artifact_sha256": "5" * 64,
            "offline_load": True,
            "device_class": "gpu",
        },
        "streaming": {
            "transport_ms": 16,
            "chunk_ms": 80,
            "cache_frames": 8,
            "lookahead_ms": 0,
        },
        "assets": {
            "storage": "external",
            "download_permitted": False,
            "caller_owned": True,
        },
        "evaluation": {
            "corpus_id": "schema-control-corpus",
            "split_id": "schema-control-split",
            "transcript_sha256": "6" * 64,
            "scorer_id": "schema-control-scorer",
            "reference_outputs_sha256": "7" * 64,
            "rights_reviewed": True,
            "listening_permitted": True,
        },
        "provider": {
            "registered": False,
            "default_selected": False,
            "opt_in": True,
        },
    }


def _mutate(path: tuple, value: Any) -> Any:
    manifest = copy.deepcopy(control_manifest())
    target: Any = manifest
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return manifest


ADMISSION_CASES = (
    ("ADM-01", "schema", ("schema_id",), "wrong/schema", "manifest_schema"),
    ("ADM-02", "family", ("candidate", "family"),
     "cache_aware_conformer", "candidate_family"),
    ("ADM-03", "family-only-id", ("candidate", "candidate_id"),
     "fastconformer-family", "candidate_not_exact"),
    ("ADM-04", "mutable-revision", ("candidate", "source_revision"),
     "main", "source_revision_mutable"),
    ("ADM-05", "short-revision", ("candidate", "source_revision"),
     "abc123", "source_revision_mutable"),
    ("ADM-06", "missing-checkpoint", ("candidate", "checkpoint_files"),
     [], "checkpoint_files"),
    ("ADM-07", "bad-digest", ("candidate", "checkpoint_files"),
     [{"name": "x.bin", "byte_count": 1, "sha256": "xyz"}],
     "checkpoint_sha256"),
    ("ADM-08", "zero-bytes", ("candidate", "checkpoint_files"),
     [{"name": "x.bin", "byte_count": 0, "sha256": "2" * 64}],
     "checkpoint_byte_count"),
    ("ADM-09", "boolean-bytes", ("candidate", "checkpoint_files"),
     [{"name": "x.bin", "byte_count": True, "sha256": "2" * 64}],
     "checkpoint_byte_count"),
    ("ADM-10", "terms-not-reviewed", ("candidate", "license",
                                      "terms_reviewed"), False,
     "license_terms"),
    ("ADM-11", "no-redistribution", ("candidate", "license",
                                     "redistribution_approved"), False,
     "license_redistribution"),
    ("ADM-12", "no-output-use", ("candidate", "license",
                                 "output_use_approved"), False,
     "license_output_use"),
    ("ADM-13", "runtime-online", ("runtime", "offline_load"), False,
     "runtime_offline_load"),
    ("ADM-14", "runtime-digest", ("runtime", "artifact_sha256"), "unknown",
     "runtime_sha256"),
    ("ADM-15", "download", ("assets", "download_permitted"), True,
     "asset_download"),
    ("ADM-16", "embedded", ("assets", "storage"), "embedded",
     "asset_storage"),
    ("ADM-17", "corpus-rights", ("evaluation", "rights_reviewed"), False,
     "corpus_rights"),
    ("ADM-18", "listening", ("evaluation", "listening_permitted"), False,
     "listening_permission"),
    ("ADM-19", "transcript", ("evaluation", "transcript_sha256"), "",
     "transcript_sha256"),
    ("ADM-20", "provider-registered", ("provider", "registered"), True,
     "provider_registered"),
    ("ADM-21", "provider-default", ("provider", "default_selected"), True,
     "provider_default"),
    ("ADM-22", "nonfinite-chunk", ("streaming", "chunk_ms"),
     float("nan"), "streaming_chunk_ms"),
    ("ADM-23", "boolean-chunk", ("streaming", "chunk_ms"), True,
     "streaming_chunk_ms"),
    ("ADM-24", "negative-lookahead", ("streaming", "lookahead_ms"), -1,
     "streaming_lookahead_ms"),
    ("ADM-25", "duplicate-checkpoint", ("candidate", "checkpoint_files"),
     [{"name": "x.bin", "byte_count": 1, "sha256": "2" * 64},
      {"name": "x.bin", "byte_count": 2, "sha256": "3" * 64}],
     "checkpoint_duplicate"),
)


def admission_cases() -> list[dict]:
    rows: list[dict] = []
    for case_id, title, path, value, expected in ADMISSION_CASES:
        manifest = _mutate(path, value)
        try:
            validate_manifest(manifest)
            observed = "accepted"
        except AdmissionError as error:
            observed = error.code
        rows.append({
            "id": case_id,
            "title": title,
            "status": "rejected" if observed == expected else "unexpected",
            "expected_code": expected,
            "observed_code": observed,
            "qualifies": False,
            "state_unchanged": True,
        })
    return rows


def admission_control() -> dict:
    manifest = control_manifest()
    validate_manifest(manifest)
    return {
        "accepted": True,
        "qualifies": False,
        "schema_only": True,
        "candidate_id": manifest["candidate"]["candidate_id"],
        "candidate_is_real": False,
        "weights_loaded": False,
        "runtime_invoked": False,
        "audio_read": False,
        "model_executed": False,
    }


def build_admission() -> dict:
    cases = admission_cases()
    control = admission_control()
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cases": cases,
        "control": control,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(1 for case in cases
                                  if case["status"] == "rejected"),
            "accepted_schema_controls": 1 if control["accepted"] else 0,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


# ---------------------------------------------------------------------------
# Static evidence rows
# ---------------------------------------------------------------------------

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "research_report_and_matrix",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The exact research reports, candidate matrix row 35, inventory "
            "record and SDK plan pinned by whole-file SHA-256."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "exact_candidate_identity",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "An exact streaming FastConformer/Conformer-TED model ID, "
            "architecture config, tokenizer, decoding configuration and "
            "immutable 40-hex source revision; the family label and the NeMo "
            "documented analogue are not an exact candidate."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "checkpoint_bytes_digests_and_model_card",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Every checkpoint/tokenizer/config byte with byte count and "
            "SHA-256, an immutable artifact revision and digest-verified "
            "model card; no bytes are present in this worktree."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_offline_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A pinned NeMo or other exact ASR runtime artifact with a "
            "recorded digest, CUDA/cuDNN/GPU requirements, deterministic "
            "settings and a clean-room offline load trace."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_corpus_and_transcripts",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A rights-cleared real speech cohort with verified transcripts, "
            "speaker/meeting split, channel/rate mapping and an independent "
            "human or forced-alignment reference whose limits are recorded."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "reference_outputs_scorer_and_timing",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Approved exact streaming reference outputs or a frozen scorer, "
            "WER/RTF accounting, endpoint/partial-hypothesis behavior, "
            "listening permission and target-device p50/p95/p99 timing."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "opt_in_provider_intake",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A separate versioned, OFF-by-default opt-in provider/tool intake "
            "with descriptor, exact geometry, clean-install proof and "
            "independent exact-head review; no default selection."),
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01", "RG-02"],
        "requirement": (
            "No exact candidate is named. The research label is "
            "'Streaming Conformer-TED / FastConformer' and the pinned finding "
            "records no exact TED checkpoint, streaming config or local ASR "
            "runtime; using another Conformer would change candidate "
            "identity."),
        "required_action": (
            "Name one exact checkpoint/model ID with architecture, tokenizer, "
            "decoding and immutable source revision; record why it is the "
            "same candidate and not a substituted analogue."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02"],
        "requirement": (
            "No checkpoint, tokenizer, config or model-card bytes are present "
            "or digest-verified. There is no byte count, SHA-256 or immutable "
            "artifact revision for any candidate weight."),
        "required_action": (
            "Supply every checkpoint/tokenizer/config file with byte count, "
            "SHA-256 and an immutable artifact revision, plus a digest-verified "
            "model card and license/notice bundle."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-03"],
        "requirement": (
            "No NeMo or other ASR runtime is installed. The pinned probe list "
            "contains no nemo/nemo_toolkit module, no CUDA runtime, no pinned "
            "wheel/container and no offline load trace."),
        "required_action": (
            "Pin the exact runtime artifact by digest, record CUDA/cuDNN/GPU "
            "requirements and deterministic settings, and prove a clean-room "
            "offline load with the candidate bytes."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-04"],
        "requirement": (
            "Rights are not established for any candidate weight, source, "
            "training data or output use. A model-card SPDX label alone is "
            "not a redistribution or product-use decision."),
        "required_action": (
            "Record written weight/source/training-data terms, any corpus "
            "terms, output-use and redistribution decisions, and an "
            "independent legal/rights review."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-05"],
        "requirement": (
            "No rights-cleared real speech corpus, verified transcript, "
            "speaker/meeting split or independent reference exists in this "
            "package. Synthetic scheduler arithmetic is not a corpus."),
        "required_action": (
            "Stage the exact rights-cleared cohort and transcripts, record "
            "split/channel/rate mapping and reference limits, and preserve "
            "paired control data."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
        "requirement": (
            "No WER, streaming latency, RTF, endpoint, partial-hypothesis, "
            "finite-output, device-timing, listening or Rate-profile result "
            "exists. The surrogate measures scheduling arithmetic only."),
        "required_action": (
            "Run the qualified candidate on the qualified cohort with frozen "
            "scorers and controls, measure end-to-end emission and device "
            "p50/p95/p99 resources, and supply Rate evidence for a composite "
            "path or a reviewed waiver; then open a separate opt-in intake."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_candidate_identity",
        "statement": (
            "Only research inputs are pinned. No exact streaming "
            "FastConformer/Conformer-TED source revision, model ID, config or "
            "tokenizer is staged, and the NeMo documented analogue is not the "
            "same candidate."),
        "reopen_condition": (
            "Pin one exact candidate's source revision and tree, model ID, "
            "architecture config, tokenizer and decoding settings, and record "
            "an independent identity review."),
    },
    {
        "id": "RG-02",
        "title": "checkpoint_weights_and_digests",
        "statement": (
            "No candidate checkpoint, tokenizer or config bytes are present "
            "or digest-verified. The research record contains no byte count, "
            "SHA-256 or immutable artifact revision."),
        "reopen_condition": (
            "Supply every candidate file with byte count and SHA-256 under an "
            "immutable artifact revision, and verify all digests against an "
            "independent retrieval record."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "statement": (
            "No NeMo or other exact ASR runtime is present. There is no "
            "lockfile, wheel/container digest, CUDA/cuDNN/GPU declaration, "
            "import digest or clean-room offline load."),
        "reopen_condition": (
            "Provide a locked offline runtime with exact artifact hashes, "
            "device/CUDA requirements, deterministic settings and a "
            "clean-room load trace for the candidate bytes."),
    },
    {
        "id": "RG-04",
        "title": "rights_training_data_and_output_use",
        "statement": (
            "Weight, source, training-data, corpus and output-use terms are "
            "not reviewed and no redistribution or product-use decision "
            "exists. SPDX metadata alone is not clearance."),
        "reopen_condition": (
            "Stage complete license/notice/model-card evidence, record "
            "training-data provenance and output-use terms, and obtain an "
            "independent rights/redistribution decision."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_corpus_and_transcripts",
        "statement": (
            "No rights-cleared real speech cohort, verified transcript, "
            "speaker/meeting split or independent reference is staged. "
            "Synthetic scheduler events are not transcripts."),
        "reopen_condition": (
            "Stage the exact cohort, transcripts and split/channel mapping "
            "with reviewed terms and an independent reference whose limits "
            "are recorded."),
    },
    {
        "id": "RG-06",
        "title": "asr_accuracy_and_streaming_latency_with_controls",
        "statement": (
            "No WER, RTF, end-to-end streaming latency, endpoint, "
            "partial-hypothesis, finite-output or matched control result was "
            "reproduced. The surrogate produces no recognition output."),
        "reopen_condition": (
            "Reproduce exact WER and streaming timing with frozen scorers, "
            "insertion/deletion/substitution accounting, endpoint and "
            "partial-hypothesis checks, finite-output scans and matched "
            "controls."),
    },
    {
        "id": "RG-07",
        "title": "rate_profile_condition_coverage_or_waiver",
        "statement": (
            "The Rate profile is not exercised: no source/output mapping, "
            "duration, pitch/transient, buffering, rate-change, unfamiliar "
            "speech/music/silence, rebuffer/drift or final-partial-window "
            "evidence exists for this ASR path."),
        "reopen_condition": (
            "Score the exact Rate-profile cases for a composite path that "
            "contains a renderer, or record an explicit reviewed waiver "
            "because ASR recognition is not a time-stretch transformation."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "No provider/tool intake, descriptor, default decision or release "
            "surface exists. Installed v0 geometry, the registry and shared "
            "build remain untouched."),
        "reopen_condition": (
            "Open a separate versioned, OFF-by-default opt-in intake with an "
            "exact descriptor/config, clean-install proof and independent "
            "exact-head review after all prior gates clear; do not select a "
            "default."),
    },
)

RATE_PROFILE_ROWS = (
    {
        "id": "RATE-01",
        "requirement": "Measure source/output mapping and duration.",
        "status": "blocked",
        "evidence": (
            "No ASR transcript-to-output mapping or duration result exists; "
            "the scheduler surrogate produces no audio or text output."),
    },
    {
        "id": "RATE-02",
        "requirement": "Measure pitch and transient audibility.",
        "status": "blocked",
        "evidence": "No rendered waveform, F0/transient metric or listening result exists.",
    },
    {
        "id": "RATE-03",
        "requirement": "Measure playback buffering.",
        "status": "blocked",
        "evidence": "No playback queue, fill/flush or buffer measurement exists.",
    },
    {
        "id": "RATE-04",
        "requirement": "Include 1x and rate changes.",
        "status": "blocked",
        "evidence": "No 1x or rate-change comparison exists; ASR is not a stretcher.",
    },
    {
        "id": "RATE-05",
        "requirement": "Include unfamiliar speech, music and silence.",
        "status": "blocked",
        "evidence": "No real speech, music, silence or language coverage was tested.",
    },
    {
        "id": "RATE-06",
        "requirement": "Include rebuffer, drift and the final partial window.",
        "status": "blocked",
        "evidence": (
            "Only deterministic scheduler arithmetic covers a partial final "
            "chunk; no stream rebuffer or clock drift was measured."),
    },
    {
        "id": "RATE-07",
        "requirement": (
            "Keep pause or filler decisions tied to source timestamps and "
            "measure speech preservation."),
        "status": "blocked",
        "evidence": (
            "No transcript/timestamp stream, pause/filler policy or speech "
            "preservation measurement exists."),
    },
    {
        "id": "RATE-08",
        "requirement": "Map output to a reviewed preferred-speed policy.",
        "status": "blocked",
        "evidence": "No preference labels, rate policy or reviewed waiver exists.",
    },
)

ASR_OUTCOME_ROWS = (
    {
        "id": "ASR-01",
        "outcome": "word_error_rate",
        "status": "blocked",
        "value": None,
        "evidence": "No transcript, candidate output or scorer exists.",
    },
    {
        "id": "ASR-02",
        "outcome": "real_time_factor_and_streaming_latency",
        "status": "blocked",
        "value": None,
        "evidence": "No runtime, paced stream or measured emission delay exists.",
    },
    {
        "id": "ASR-03",
        "outcome": "chunking_invariance_and_endpoint_stability",
        "status": "blocked",
        "value": None,
        "evidence": "Only scheduler event boundaries are invariant; no decoded output exists.",
    },
    {
        "id": "ASR-04",
        "outcome": "partial_hypothesis_and_finalization_correctness",
        "status": "blocked",
        "value": None,
        "evidence": "No hypothesis, endpoint policy or final transcript exists.",
    },
    {
        "id": "ASR-05",
        "outcome": "finite_output_and_invalid_handling",
        "status": "blocked",
        "value": None,
        "evidence": "No candidate output was produced; only scheduler input rejection was tested.",
    },
)

TIMING_ROWS = (
    {
        "id": "TIME-01",
        "metric": "encoder_chunk_compute_latency",
        "status": "blocked",
        "value": None,
        "evidence": "No encoder or runtime was invoked.",
    },
    {
        "id": "TIME-02",
        "metric": "end_to_end_emission_delay",
        "status": "blocked",
        "value": None,
        "evidence": "No transcript emission or endpoint timing exists.",
    },
    {
        "id": "TIME-03",
        "metric": "device_deadline_and_callback",
        "status": "blocked",
        "value": None,
        "evidence": "No device, paced workload or callback deadline was measured.",
    },
    {
        "id": "TIME-04",
        "metric": "cpu_gpu_memory_and_energy",
        "status": "blocked",
        "value": None,
        "evidence": "No resource, thermal or energy measurement exists.",
    },
)

NON_CLAIMS = (
    "No FastConformer/Conformer-TED checkpoint, tokenizer, config or weight is present.",
    "No NeMo, torch, CUDA, ONNX or other ASR runtime is imported or executed.",
    "No audio, transcript, word span or recognition output is read or produced.",
    "The scheduler surrogate is not ASR and substitutes for no candidate result.",
    "No WER, RTF, streaming latency, finite-output, Rate-profile, timing or quality result is reproduced.",
    "No provider, registry, descriptor, default, installed v0 behavior, shared build, CI, board or handoff is changed.",
)

REQUIRED_RESULTS = (
    "exact candidate identity and immutable source revision",
    "candidate checkpoint/tokenizer/config bytes with verified digests",
    "pinned offline runtime with CUDA/device declaration",
    "written rights, training-data, output-use and redistribution decision",
    "rights-cleared real corpus with verified transcripts and independent reference",
    "reproduced WER, streaming latency, RTF and endpoint/partial-hypothesis behavior",
    "finite-output and adverse/missing controls for the candidate",
    "target-device p50/p95/p99 timing, memory and energy",
    "Rate-profile evidence for a composite path or a reviewed waiver",
    "separate OFF-by-default opt-in provider intake and independent review",
)


# ---------------------------------------------------------------------------
# Evidence documents
# ---------------------------------------------------------------------------

def candidate_record() -> dict:
    return {
        "matrix": CANDIDATE_MATRIX,
        "record": CANDIDATE_RECORD,
        "record_name": CANDIDATE_RECORD_NAME,
        "record_status": CANDIDATE_RECORD_STATUS,
        "finding": CANDIDATE_RECORD_FINDING,
        "comparison_baseline": CANDIDATE_COMPARISON,
        "report_paths": list(CANDIDATE_REPORT_PATHS),
        "exact_candidate_selected": False,
        "family_label_only": True,
        "substitute_conformer_used": False,
    }


def documented_context() -> dict:
    return {
        "source_report": CANDIDATE_REPORT_PATHS[1],
        "label": CANDIDATE_RECORD_NAME,
        "identity_warning": (
            "The label is underspecified and no exact TED checkpoint or local "
            "streaming configuration exists; using another Conformer would "
            "silently change the candidate."),
        "nemo_analogue_source_reported": {
            "transport_frame_ms": 16,
            "inference_chunk_ms": 80,
            "persistent_encoder_cache": True,
            "gpu_local": True,
            "independently_verified_here": False,
            "reproduced_here": False,
            "substitution_permitted": False,
        },
        "uses_whisper_or_other_asr": False,
        "provenance_only": True,
    }


def qualification() -> dict:
    return {
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "incomplete": True,
        "proposal_only": True,
        "qualifies": False,
        "source_present": True,
        "research_report_present": True,
        "exact_candidate_identity_present": False,
        "checkpoint_bytes_present": False,
        "weights_present": False,
        "runtime_present": False,
        "asr_result": False,
        "wer_result": False,
        "transcript_result": False,
        "streaming_latency_result": False,
        "device_timing_result": False,
        "rate_profile_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
    }


def claims() -> dict:
    return {
        "asset_downloaded": False,
        "weights_accessed": False,
        "real_audio_read": False,
        "real_media_read": False,
        "runtime_invoked": False,
        "asr_transcript_produced": False,
        "wer_measured": False,
        "streaming_latency_measured": False,
        "device_timing_measured": False,
        "listening_result_produced": False,
        "benchmark_result": False,
        "quality_claim": False,
        "release_claim": False,
        "network_used": False,
    }


def boundary() -> dict:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "installed_v0_geometry_preserved": True,
        "shared_build_or_ci_change": False,
        "processor_exposure": False,
        "task_board_or_handoff_write": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    }


def scope() -> dict:
    return {
        "write_scope": WRITE_SCOPE,
        "task_local_only": True,
        "provider_or_registry_change": False,
        "installed_v0_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_write": False,
        "asset_download": False,
        "real_runtime_or_corpus": False,
    }


def release_gates() -> list[dict]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows: list[dict] = []
    for gate in RELEASE_GATES:
        rows.append({
            "id": gate["id"],
            "title": gate["title"],
            "status": "blocked",
            "qualifies": False,
            "statement": gate["statement"],
            "reopen_condition": gate["reopen_condition"],
            "linked_row": projection,
        })
    return rows


def exact_blockers() -> list[dict]:
    return [copy.deepcopy(row) for row in EXACT_BLOCKERS]


def required_artifacts() -> list[dict]:
    return [copy.deepcopy(row) for row in REQUIRED_ARTIFACTS]


def rate_profile_requirements() -> list[dict]:
    return [copy.deepcopy(row) for row in RATE_PROFILE_ROWS]


def asr_outcome_requirements() -> list[dict]:
    return [copy.deepcopy(row) for row in ASR_OUTCOME_ROWS]


def timing_requirements() -> list[dict]:
    return [copy.deepcopy(row) for row in TIMING_ROWS]


def linked_row_identity() -> dict:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
    }


def pin_rows(pins: dict[str, str], root: Path) -> dict:
    rows: dict[str, dict] = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return rows


def _assert_pins(rows: dict[str, dict], label: str) -> None:
    for relative, row in rows.items():
        if not row["verified"]:
            raise ValueError(label + "_pin_mismatch:" + relative)


# ---------------------------------------------------------------------------
# Contract and report
# ---------------------------------------------------------------------------

def build_contract() -> dict:
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "status": STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "disposition": DISPOSITION,
        "scope": scope(),
        "candidate_record": candidate_record(),
        "documented_context": documented_context(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "required_artifacts": required_artifacts(),
        "rate_profile_requirements": rate_profile_requirements(),
        "asr_outcome_requirements": asr_outcome_requirements(),
        "timing_requirements": timing_requirements(),
        "required_results": list(REQUIRED_RESULTS),
        "qualification": qualification(),
        "boundary": boundary(),
        "public_v0_geometry": public_v0_geometry(),
        "non_claims": list(NON_CLAIMS),
        "claims": claims(),
        "linked_row_identity": linked_row_identity(),
        "sources": {
            "source_pins": sorted(SOURCE_PINS),
            "boundary_pins": sorted(BOUNDARY_PINS),
            "board_file_pinned": False,
        },
    }
    validate_contract(contract)
    return contract


def build_report() -> dict:
    contract = build_contract()
    source_rows = pin_rows(SOURCE_PINS, AUDIO_ROOT)
    boundary_rows = pin_rows(BOUNDARY_PINS, WORKTREE)
    _assert_pins(source_rows, "source")
    _assert_pins(boundary_rows, "boundary")
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "contract_sha256": object_digest(contract),
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "disposition": contract["disposition"],
        "scope": contract["scope"],
        "candidate_record": contract["candidate_record"],
        "documented_context": contract["documented_context"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "required_artifacts": contract["required_artifacts"],
        "rate_profile": {
            "profile": PROFILE_LABEL,
            "rows": contract["rate_profile_requirements"],
        },
        "asr_outcomes": {
            "profile": "asr_streaming",
            "rows": contract["asr_outcome_requirements"],
        },
        "timing": {
            "profile": "target_runtime",
            "rows": contract["timing_requirements"],
        },
        "required_results": contract["required_results"],
        "qualification": contract["qualification"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "non_claims": contract["non_claims"],
        "claims": contract["claims"],
        "linked_row_identity": contract["linked_row_identity"],
        "source_pins": source_rows,
        "boundary_pins": boundary_rows,
        "absence_evidence": {
            "probes": absence_probes(),
            "summary": absence_summary(),
        },
        "runtime_presence": runtime_presence(),
        "source_presence": source_presence(),
        "scheduler_control": scheduler_control(),
        "admission": build_admission(),
        "repeatability": {
            "protocol": "three cold-start interpreter processes",
            "repetitions": 3,
            "hash_seed": "0",
            "bytecode_disabled": True,
            "byte_identical_required": True,
            "verified_by": "run.py and verify.py",
        },
        "no_missing_result_qualifies_candidate": True,
    }
    _no_floats(report)
    validate_report(report)
    return report


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, hashlib.sha256(text.encode("ascii")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("decision") != DECISION:
        raise ValueError("contract_decision")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("contract_gate_reopen")
    qualification_row = contract.get("qualification", {})
    if qualification_row.get("not_qualified") is not True \
            or qualification_row.get("all_release_gates_blocked") is not True \
            or qualification_row.get("qualifies") is not False:
        raise ValueError("contract_qualification")
    artifacts = contract.get("required_artifacts", [])
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if not (artifacts[0].get("present") is True
            and artifacts[0].get("verified") is True
            and artifacts[0].get("blocked") is False):
        raise ValueError("contract_source_artifact")
    for artifact in artifacts[1:]:
        if artifact.get("present") is not False \
                or artifact.get("verified") is not False \
                or artifact.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
        if artifact.get("sha256") is not None:
            raise ValueError("contract_absent_artifact_digest")
    blockers = contract.get("exact_blockers", [])
    if len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    gate_ids = {row.get("id") for row in gates}
    for blocker in blockers:
        if blocker.get("status") != "open" \
                or blocker.get("qualifies") is not False:
            raise ValueError("contract_blocker_open")
        if blocker.get("artifact_id") not in artifact_ids:
            raise ValueError("contract_blocker_artifact")
        for gate_id in blocker.get("linked_gates", []):
            if gate_id not in gate_ids:
                raise ValueError("contract_blocker_gate")
    for name in ("rate_profile_requirements", "asr_outcome_requirements",
                 "timing_requirements"):
        rows = contract.get(name)
        if not isinstance(rows, list) or not rows:
            raise ValueError("contract_empty:" + name)
        for row in rows:
            if row.get("status") != "blocked":
                raise ValueError("contract_row_not_blocked:" + name)
            if "value" in row and row.get("value") is not None:
                raise ValueError("contract_row_has_value:" + name)
    if contract.get("linked_row_identity", {}).get("gating") != \
            "stable_identity_only":
        raise ValueError("contract_linked_gating")
    if contract.get("boundary", {}).get("registered") is not False:
        raise ValueError("contract_registered")
    if contract.get("boundary", {}).get("installed_v0_geometry_preserved") \
            is not True:
        raise ValueError("contract_geometry")


def validate_report(report: dict) -> None:
    if report.get("decision") != DECISION:
        raise ValueError("report_decision")
    if report.get("status") != STATUS:
        raise ValueError("report_status")
    if report.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("report_qualification_status")
    if report.get("proposal_only") is not True:
        raise ValueError("report_proposal_only")
    gates = report.get("gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("report_gate_count")
    if any(gate.get("status") != "blocked" for gate in gates):
        raise ValueError("report_gate_not_blocked")
    if report.get("claims", {}).get("release_claim") is not False:
        raise ValueError("report_release_claim")
    if report.get("scheduler_control", {}).get("performs_asr") is not False:
        raise ValueError("report_surrogate_claims_asr")
