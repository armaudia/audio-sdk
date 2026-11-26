# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence for SDK-MOONSHINE.

The exact Moonshine source checkout, model/streaming-model bundle and pinned
runtime are absent. This module never imports, loads, executes, copies or
downloads Moonshine, ONNX Runtime, a tokenizer, a weight file, audio, a corpus
or a network client. It pins stable read-only inputs, proves a fixed absence
probe list, computes exact word/token-to-rate arithmetic on caller-supplied
integer sample spans, exposes the timestamp-granularity sensitivity that the
candidate record leaves untested, and enforces a fail-closed admission contract
for a future qualified run. Every mechanism result is explicitly synthetic and
can never qualify.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Optional

TASK = "SDK-MOONSHINE"
TASK_TITLE = "Moonshine"
COMPONENT_ID = "moonshine"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
OWNER = "agent-MOONSHINE"
REVIEWER = "reviewer-MOONSHINE"
BASE_COMMIT = "7dc9c84b2ed963ecda895194b19e8d8979a2f748"
BRANCH = "swarm/SDK-MOONSHINE"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
TASK_PREFIX = "docs/task-evidence/moonshine/"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/moonshine-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/moonshine-timestamp-cohort/0.1"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "evidence", "deliverable", "acceptance",
    "write_scope",
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(WORKTREE.parents[2]))).resolve()

# ---------------------------------------------------------------------------
# Stable, read-only pins. ``source:`` rows are AUDIO_ROOT relative; all other
# rows are SDK-worktree relative. Nothing pinned here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS: dict[str, str] = {
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
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    # Merged sibling evidence is pinned read-only and never inherited as result.
    "docs/task-evidence/asr-word-timestamps/report.json":
        "318bec24c9d388fa122e80974cfc6772b144f7f651e87d5e88ac0677975d437e",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
    "docs/task-evidence/fastconformer-streaming-asr/report.json":
        "c649329e90bfa8dee8ea155e06a07a8b86af4580ef90fb0c51abd88a2f37dbf2",
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "docs/task-evidence/survey-rec-01/report.json":
        "b89364422f6e2796d0fd6d955417066d7f01da59420e817f0a781e4e69c20ac5",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
    "docs/task-evidence/whisper-tiny-en-mfa/report.json":
        "6b9cc69ea2be5cd5cad9509021b7b5e7fb972a4c32c62721f07be995b582710c",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "source/output mapping",
    "duration",
    "pitch",
    "transient audibility",
    "playback buffering",
    "1×",
    "rate changes",
    "unfamiliar speech, music, silence",
    "rebuffer, drift",
    "final partial window",
    "source timestamps",
    "speech preservation",
)
SCOPE_BASE_REFS = ("origin/main", "main")

# ---------------------------------------------------------------------------
# Exact upstream identity requirements. The pinned census records a repository
# URL and source-reported licence strings; it records no revision, digest,
# weight file, tokenizer, runtime or model card. None is asserted as present.
# ---------------------------------------------------------------------------

CENSUS_PATH = "cpp-library/pipeline-validation/playback-speed-candidates.md"
SOURCE_REPOSITORY = "https://github.com/moonshine-ai/moonshine"
MODEL_REPOSITORY = None
PAPER_URL = None
REPORTED_LICENSE = "MIT code + MIT streaming models"
REPORTED_ROLE = (
    "low-latency English STT content-gate candidate; very low latency, C API, "
    "streaming models"
)
REPORTED_FINDING = "English-first; timestamp granularity needs testing"
REPORTED_CAVEAT = (
    "Moonshine is worth a look if the product is English-only and the lookahead "
    "budget is tight: MIT code and MIT streaming models, low latency, C API. "
    "Confirm token/word timing before relying on it."
)
REPORTED_PRECEDENCE = (
    "add Moonshine only if the Vosk/sherpa gate is too heavy"
)

SOURCE_PROBE_PATHS = (
    "cpp-library/pipeline-validation/playback-speed/vendor/moonshine",
    "cpp-library/pipeline-validation/playback-speed/vendor/moonshine-ai",
    "cpp-library/pipeline-validation/playback-speed/deps/moonshine",
    "cpp-library/pipeline-validation/playback-speed/models/moonshine",
    "research/moonshine",
    "research/asr-20261101/moonshine",
    "data/checkouts/moonshine",
    "third_party/moonshine",
    "deps/moonshine",
)
WEIGHTS_PROBE_PATHS = (
    "cpp-library/pipeline-validation/playback-speed/models/moonshine-tiny",
    "cpp-library/pipeline-validation/playback-speed/models/moonshine-base",
    "cpp-library/pipeline-validation/playback-speed/models/"
    "moonshine-streaming",
    "cpp-library/pipeline-validation/playback-speed/models/"
    "usefulsensors-moonshine",
    "research/models/moonshine",
    "data/models/moonshine",
    "data/weights/moonshine",
)
RUNTIME_PROBE_PATHS = (
    "cpp-library/pipeline-validation/playback-speed/.venv/lib/"
    "python3.11/site-packages/moonshine",
    "cpp-library/pipeline-validation/playback-speed/.venv-moonshine",
    ".venv-moonshine",
    "data/envs/moonshine",
)
HOME_PROBE_PATHS = (
    "~/.cache/huggingface/hub/models--moonshine-ai--moonshine",
    "~/.cache/huggingface/hub/models--UsefulSensors--moonshine",
    "~/.cache/huggingface/hub/models--moonshine",
    "~/.venvs/moonshine",
    "~/.local/share/moonshine",
)
SOURCE_ROOT_REL = "cpp-library/pipeline-validation/playback-speed/vendor"

NON_CLAIMS = [
    "No Moonshine source copy, model, streaming checkpoint, tokenizer, weight "
    "fragment, ONNX graph, runtime, audio, transcript or corpus is present, "
    "loaded, linked, imported or executed by this package.",
    "No recognition, token extraction, word timing, rate scoring, listening, "
    "device timing, buffering or benchmark run is performed here.",
    "No real audio, consented cohort, human-verified token/word span, language "
    "or speaker group, matched control or held-out split is used here.",
    "No missing, invalid, nonfinite or adverse manifest case qualifies; the "
    "accepted synthetic schema control and every arithmetic control are "
    "explicitly non-evidence.",
    "No Vosk, sherpa-onnx, Whisper, FastConformer, wav2vec2, CrisperWhisper or "
    "survey result is inherited, pooled or promoted to Moonshine.",
    "No source-reported MIT licence string is treated as a verified grant, and "
    "no benchmark, quality, latency, WER, timestamp or release claim is made.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "asr-word-timestamps",
        "task": "SDK-ASR-WORD-TIMESTAMPS",
        "path": "docs/task-evidence/asr-word-timestamps/report.json",
        "class": "adjacent_asr_timestamp_proxy_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Same Rate-profile proxy role but different engines, "
                    "cohort, spans and rights; no Moonshine timestamp, rate or "
                    "transcript is inherited.",
    },
    {
        "component": "fastconformer-streaming-asr",
        "task": "SDK-FASTCONFORMER-STREAMING-ASR",
        "path": "docs/task-evidence/fastconformer-streaming-asr/report.json",
        "class": "adjacent_streaming_asr_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Different model family, geometry and terms; its scheduler "
                    "surrogate does not transfer to Moonshine.",
    },
    {
        "component": "vosk-small-en-us-0-15-playback-gate",
        "task": "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE",
        "path": "docs/task-evidence/"
                "vosk-small-en-us-0-15-playback-gate/report.json",
        "class": "adjacent_playback_gate_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different gate engine with its own unlicensed present "
                    "bytes; its IoU and RTF are source-reported only and are "
                    "not Moonshine evidence.",
    },
    {
        "component": "whisper-tiny-en-mfa",
        "task": "SDK-WHISPER-TINY-EN-MFA",
        "path": "docs/task-evidence/whisper-tiny-en-mfa/report.json",
        "class": "adjacent_asr_alignment_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different recognition and forced-alignment stack; no "
                    "Moonshine timing or content result is inherited.",
    },
    {
        "component": "dynamic-int8-wav2vec2-base",
        "task": "SDK-DYNAMIC-INT8-WAV2VEC2-BASE",
        "path": "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json",
        "class": "adjacent_asr_encoder_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "An encoder representation track, not an English streaming "
                    "recognizer; no token boundary or WER result transfers.",
    },
    {
        "component": "survey-rec-01",
        "task": "SDK-SURVEY-REC-01",
        "path": "docs/task-evidence/survey-rec-01/report.json",
        "class": "merged_recognition_survey_map",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A merged recognition coverage survey; it supplies no "
                    "Moonshine source, weight, runtime, cohort or measured "
                    "result.",
    },
)

RATE_REQUIREMENTS = (
    {
        "id": "RATE-01",
        "requirement": "1× control",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No measured Moonshine gate at 1× on a qualifying cohort.",
    },
    {
        "id": "RATE-02",
        "requirement": "rate changes and source/output mapping",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No gate run over altered rates; no source/output map.",
    },
    {
        "id": "RATE-03",
        "requirement": "duration and playback buffering",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No rendered waveform, buffer occupancy or duration run.",
    },
    {
        "id": "RATE-04",
        "requirement": "pitch",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No stretched output and no pitch measurement.",
    },
    {
        "id": "RATE-05",
        "requirement": "transient audibility",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No waveform, listening or transient analysis exists.",
    },
    {
        "id": "RATE-06",
        "requirement": "unfamiliar speech, music, silence",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No rights-cleared stratified English corpus exists.",
    },
    {
        "id": "RATE-07",
        "requirement": "rebuffer and drift",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No device clock, rebuffer, fill/flush or drift run.",
    },
    {
        "id": "RATE-08",
        "requirement": "final partial window, timestamps and speech preservation",
        "status": "blocked",
        "qualifies": False,
        "evidence": "No real final partial window; granularity and pause/filler "
                    "decisions remain uncalibrated.",
    },
)

# ---------------------------------------------------------------------------
# Strict JSON and canonical bytes.
# ---------------------------------------------------------------------------

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")
DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
MAX_WORDS = 100_000
MAX_FILES = 64
MAX_PACKAGES = 64
MAX_DURATION_MS = 3_600_000
ADMISSIBLE_SAMPLE_RATES = (16_000, 48_000)
ADMISSIBLE_GRANULARITY_MS = (5, 10, 20, 40, 80)
DEVICES = ("cpu", "cuda", "metal", "coreml")
BLOCK_SAMPLES = 1600
CONTROL_KINDS = (
    "drift",
    "final_partial_window",
    "identity_1x",
    "rate_change",
    "rebuffer",
    "unfamiliar_speech_or_music_or_silence",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a",
    ".mdl", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus",
    ".ort", ".pt", ".pth", ".pyc", ".safetensors", ".so", ".tflite", ".wav",
    ".wasm", ".weights",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("nonstring_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def canonical_bytes(value: Any) -> bytes:
    _no_floats(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json:" + token)


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def parse_strict_json(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("json_not_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_strict_pairs,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("json_malformed") from error
    if not isinstance(value, dict):
        raise ValueError("manifest_not_object")
    _no_floats(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json(path.read_bytes())


def loads_strict(payload: str) -> dict:
    return parse_strict_json(payload.encode("utf-8"))


def canonical_report(report: Optional[dict] = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    payload = canonical_bytes(value)
    return payload.decode("ascii"), sha256_bytes(payload)


# ---------------------------------------------------------------------------
# Stable board identity. The mutable board file is read, never pinned. Only
# stable identity fields enter canonical bytes and gate anything.
# ---------------------------------------------------------------------------


def _project(row: dict) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if missing:
        raise ValueError("board_row_field_missing:" + missing[0])
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


def _board_rows(path: Optional[Path] = None) -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Optional[Path] = None) -> dict:
    rows = _board_rows(path)
    matches = [row for row in rows
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0])
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    return projection


def linked_rows(path: Optional[Path] = None) -> list[dict]:
    rows = _board_rows(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    root = by_id.get(TASK)
    if root is None:
        raise ValueError("board_row_absent")
    projection = _project(root)
    result = [projection]
    for dependency in projection["depends_on"]:
        row = by_id.get(dependency)
        if row is None:
            raise ValueError("linked_row_absent:" + dependency)
        result.append(_project(row))
    return result


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: Optional[list[dict]] = None) -> str:
    value = linked_rows() if rows is None else rows
    return object_digest([dict(row) for row in value])


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "repository": REPOSITORY,
    }


# ---------------------------------------------------------------------------
# Fixed absence probes. A later artifact reopens the claim instead of silently
# leaving a stale "absent" evidence package.
# ---------------------------------------------------------------------------


def _workspace_rows(paths: tuple[str, ...], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        if (AUDIO_ROOT / relative).exists() or (WORKTREE / relative).exists():
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
        "network_used": False,
        "source_or_runtime_imported": False,
    }


# ---------------------------------------------------------------------------
# Exact word/token-to-rate arithmetic. Pure integer/Fraction/Decimal work on
# caller-supplied spans; no recognizer, audio or model is involved.
# ---------------------------------------------------------------------------


def _fixed3(value: Fraction) -> str:
    if value < 0:
        raise ValueError("negative_value")
    decimal = Decimal(value.numerator) / Decimal(value.denominator)
    return format(decimal.quantize(Decimal("0.001"),
                                   rounding=ROUND_HALF_EVEN), "f")


def _exact_int(value: Any, label: str, minimum: int = 0,
               maximum: Optional[int] = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(label + "_not_int")
    if value < minimum:
        raise ValueError(label + "_below_minimum")
    if maximum is not None and value > maximum:
        raise ValueError(label + "_above_maximum")
    return value


def _span_list(words: Any, total_samples: int) -> list[dict]:
    if not isinstance(words, list) or not 1 <= len(words) <= MAX_WORDS:
        raise ValueError("word_count_range")
    result: list[dict] = []
    previous_end = 0
    for index, word in enumerate(words):
        if not isinstance(word, dict):
            raise ValueError("word_type")
        start = _exact_int(word.get("start_sample"), "word_start", 0,
                           total_samples)
        end = _exact_int(word.get("end_sample"), "word_end", 0, total_samples)
        if end <= start:
            raise ValueError("word_order")
        if start < previous_end:
            raise ValueError("word_overlap")
        previous_end = end
        result.append({"start_sample": start, "end_sample": end})
    return result


def word_rate(words: list[dict], total_samples: Any,
              sample_rate_hz: Any) -> dict:
    """Exact words/min, speech rate and pause ratio from sample spans."""
    total = _exact_int(total_samples, "total_samples", 1, 1 << 40)
    rate = _exact_int(sample_rate_hz, "sample_rate_hz", 1, 192_000)
    if rate not in ADMISSIBLE_SAMPLE_RATES:
        raise ValueError("sample_rate_unsupported")
    spans = _span_list(words, total)
    speech = sum(row["end_sample"] - row["start_sample"] for row in spans)
    if speech <= 0:
        raise ValueError("speech_duration_zero")
    count = len(spans)
    total_rate = Fraction(count * 60 * rate, total)
    speech_rate = Fraction(count * 60 * rate, speech)
    pause = Fraction(total - speech, total)
    return {
        "word_count": count,
        "total_samples": total,
        "sample_rate_hz": rate,
        "duration_ms": _fixed3(Fraction(total * 1000, rate)),
        "speech_samples": speech,
        "speech_ms": _fixed3(Fraction(speech * 1000, rate)),
        "words_per_minute_total": _fixed3(total_rate),
        "words_per_minute_speech": _fixed3(speech_rate),
        "pause_ratio": _fixed3(pause),
    }


def granularity_samples(sample_rate_hz: int, granularity_ms: int) -> int:
    _exact_int(granularity_ms, "granularity_ms", 1, 1_000)
    if granularity_ms not in ADMISSIBLE_GRANULARITY_MS:
        raise ValueError("granularity_unsupported")
    product = sample_rate_hz * granularity_ms
    if product % 1000:
        raise ValueError("granularity_not_integral")
    return product // 1000


def quantize_spans(spans: list[dict], granularity: int,
                   total_samples: int) -> dict:
    """Round each half-open span outwards to the declared granularity."""
    _exact_int(granularity, "granularity", 1, 1 << 30)
    _exact_int(total_samples, "total_samples", 1, 1 << 40)
    rows: list[dict] = []
    previous_end = 0
    overlap = False
    changed = 0
    for span in spans:
        start = span["start_sample"]
        end = span["end_sample"]
        q_start = (start // granularity) * granularity
        q_end = ((end + granularity - 1) // granularity) * granularity
        q_end = min(q_end, total_samples)
        if q_end <= q_start:
            q_end = min(q_start + granularity, total_samples)
        if q_start < previous_end:
            overlap = True
        previous_end = q_end
        if (q_start, q_end) != (start, end):
            changed += 1
        rows.append({
            "original_start_sample": start,
            "original_end_sample": end,
            "quantized_start_sample": q_start,
            "quantized_end_sample": q_end,
        })
    return {
        "spans": rows,
        "changed_span_count": changed,
        "overlap": overlap,
        "boundary_stable": changed == 0,
    }


def block_labels(spans: list[dict], total_samples: int,
                 block_samples: int = BLOCK_SAMPLES) -> list[str]:
    _exact_int(total_samples, "total_samples", 1, 1 << 40)
    _exact_int(block_samples, "block_samples", 160, 16_000)
    count = (total_samples + block_samples - 1) // block_samples
    labels = ["silence"] * count
    for span in spans:
        first = span["start_sample"] // block_samples
        last = (span["end_sample"] - 1) // block_samples
        for index in range(first, last + 1):
            labels[index] = "speech"
    return labels


def _quantized_rate(quantized: dict, total_samples: int,
                    sample_rate_hz: int) -> Optional[dict]:
    if quantized["overlap"]:
        return None
    spans = [{"start_sample": row["quantized_start_sample"],
              "end_sample": row["quantized_end_sample"]}
             for row in quantized["spans"]]
    return word_rate(spans, total_samples, sample_rate_hz)


def granularity_control() -> dict:
    """Synthetic granularity sensitivity arithmetic. Never evidence."""
    sample_rate = 16_000
    cases: list[dict] = []

    def add(case_id: str, total: int, spans: list[dict],
            granularity_ms: int) -> None:
        granularity = granularity_samples(sample_rate, granularity_ms)
        original = word_rate(spans, total, sample_rate)
        quantized = quantize_spans(spans, granularity,
                                   total)
        computed = _quantized_rate(quantized, total, sample_rate)
        labels = block_labels(spans, total)
        q_labels: Optional[list[str]] = None
        if not quantized["overlap"]:
            q_labels = block_labels(
                [{"start_sample": row["quantized_start_sample"],
                  "end_sample": row["quantized_end_sample"]}
                 for row in quantized["spans"]], total)
        cases.append({
            "id": case_id,
            "evidence_class": "synthetic_contract_control_not_evidence",
            "total_samples": total,
            "block_samples": BLOCK_SAMPLES,
            "granularity_ms": granularity_ms,
            "granularity_samples": granularity,
            "spans": [dict(span) for span in spans],
            "quantization": quantized,
            "block_labels": labels,
            "quantized_block_labels": q_labels,
            "block_labels_changed": (q_labels is not None
                                     and q_labels != labels),
            "original_rate": original,
            "quantized_rate": computed,
            "rate_changed": (computed is None
                             or computed != original),
            "block_count": len(labels),
            "final_partial_samples": (total % BLOCK_SAMPLES
                                      if total % BLOCK_SAMPLES else
                                      BLOCK_SAMPLES),
            "qualifies": False,
        })

    fine_spans = [
        {"start_sample": 0, "end_sample": 1000},
        {"start_sample": 1120, "end_sample": 1200},
        {"start_sample": 2000, "end_sample": 2500},
    ]
    add("fine_5ms", 16_000, fine_spans, 5)
    add("coarse_80ms", 16_000, fine_spans, 80)
    add("aligned_80ms", 8_000, [
        {"start_sample": 0, "end_sample": 1280},
        {"start_sample": 2560, "end_sample": 3840},
        {"start_sample": 5120, "end_sample": 6400},
    ], 80)
    add("final_partial_window", 16_065, [
        {"start_sample": 0, "end_sample": 1040},
        {"start_sample": 11_040, "end_sample": 12_000},
    ], 5)

    by_id = {case["id"]: case for case in cases}
    stable = sum(1 for case in cases
                 if case["quantization"]["boundary_stable"])
    sensitive = sum(1 for case in cases
                    if not case["quantization"]["boundary_stable"]
                    or case["rate_changed"])
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": "exact word/token-to-rate and granularity accounting only",
        "sample_rate_hz": sample_rate,
        "block_samples": BLOCK_SAMPLES,
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "boundary_stable_cases": stable,
            "granularity_sensitive_cases": sensitive,
            "overlapping_quantizations":
                sum(1 for case in cases if case["quantization"]["overlap"]),
            "final_partial_cases":
                sum(1 for case in cases
                    if case["id"] == "final_partial_window"),
            "qualifying_results": 0,
            "model_executed": False,
            "runtime_imported": False,
            "audio_read": False,
            "network_used": False,
        },
        "observed": {
            "fine_vs_coarse_rate_differ":
                (by_id["fine_5ms"]["quantized_rate"]
                 != by_id["coarse_80ms"]["quantized_rate"]),
            "aligned_identity":
                by_id["aligned_80ms"]["quantized_rate"]
                == by_id["aligned_80ms"]["original_rate"],
            "final_partial_samples":
                by_id["final_partial_window"]["final_partial_samples"],
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed admission boundary for a future qualified Moonshine run.
# ---------------------------------------------------------------------------

MANIFEST_FIELDS = (
    "schema_id", "run_id", "source", "weights", "runtime", "audio",
    "reference", "hypothesis", "controls", "outcomes", "rights",
)
SOURCE_FIELDS = ("repository", "revision", "license_spdx", "license_sha256")
WEIGHTS_FIELDS = ("model_id", "revision", "files", "terms_reviewed")
WEIGHT_FILE_FIELDS = ("path", "sha256", "bytes")
RUNTIME_FIELDS = ("name", "version", "python", "device", "lock_sha256",
                  "offline", "deterministic", "packages")
PACKAGE_FIELDS = ("name", "version")
AUDIO_FIELDS = ("id", "path", "sha256", "sample_rate_hz", "channels",
                "samples", "duration_ms")
REFERENCE_FIELDS = ("kind", "path", "sha256", "word_count", "annotator_count",
                    "independent_of_asr")
HYPOTHESIS_FIELDS = ("words", "word_count")
WORD_FIELDS = ("text", "start_sample", "end_sample")
CONTROL_FIELDS = ("id", "kind", "passes")
OUTCOME_FIELDS = (
    "wer", "boundary_mae_ms", "boundary_p95_abs_error_ms",
    "boundary_within_granularity_fraction", "timestamp_granularity_ms",
    "words_per_minute_total", "words_per_minute_speech", "pause_ratio",
    "content_preservation", "pitch_measured", "transient_measured",
    "buffering_measured", "drift_measured", "first_output_ms", "tail_ms",
    "nonfinite_count", "deadline_misses", "sample_count", "qualified",
)
RIGHTS_FIELDS = (
    "consent_recorded", "model_terms_reviewed", "runtime_license_reviewed",
    "output_use_defined", "commercial_use_approved",
    "redistribution_approved", "listening_protocol_approved",
    "claims_qualified",
)
RIGHTS_TRUE_FIELDS = RIGHTS_FIELDS[:-1]


def _exact(value: Any, fields: tuple[str, ...], path: str) -> dict:
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError("keys:" + (path or "root"))
    return value


def _text(value: Any, path: str, pattern: Optional[re.Pattern] = None,
          maximum: int = 1024) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError("text:" + path)
    if CONTROL_CHARS.search(value):
        raise ValueError("text:" + path)
    if pattern is not None and not pattern.match(value):
        raise ValueError("text_pattern:" + path)
    return value


def _integer(value: Any, path: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("integer:" + path)
    if value < minimum or value > maximum:
        raise ValueError("integer_range:" + path)
    return value


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError("boolean:" + path)
    return value


def _sha(value: Any, path: str) -> str:
    return _text(value, path, HEX64, 64)


def _revision(value: Any, path: str) -> str:
    return _text(value, path, HEX40, 40)


def _relative(value: Any, path: str) -> str:
    text = _text(value, path, None, 512)
    if text.startswith("/") or "\\" in text:
        raise ValueError("relative_path:" + path)
    parts = text.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("relative_path:" + path)
    return text


def _decimal(value: Any, path: str, low: str, high: str) -> Decimal:
    if not isinstance(value, str) or not DECIMAL.match(value):
        raise ValueError("decimal_format:" + path)
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise ValueError("decimal_format:" + path) from None
    if not number.is_finite():
        raise ValueError("decimal_format:" + path)
    if number < Decimal(low) or number > Decimal(high):
        raise ValueError("decimal_range:" + path)
    return number


def _sorted_unique(rows: list[dict], key: str, order: str,
                   duplicate: str) -> None:
    values = [row[key] for row in rows]
    if len(set(values)) != len(values):
        raise ValueError(duplicate)
    if values != sorted(values):
        raise ValueError(order)


def validate_manifest(manifest: Any) -> None:
    document = _exact(manifest, MANIFEST_FIELDS, "manifest")
    if document["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("schema_id")
    _text(document["run_id"], "run_id", SLUG, 64)

    source = _exact(document["source"], SOURCE_FIELDS, "source")
    _text(source["repository"], "source.repository", None, 240)
    _revision(source["revision"], "source.revision")
    _text(source["license_spdx"], "source.license_spdx", None, 80)
    _sha(source["license_sha256"], "source.license_sha256")

    weights = _exact(document["weights"], WEIGHTS_FIELDS, "weights")
    _text(weights["model_id"], "weights.model_id", SLUG, 96)
    _revision(weights["revision"], "weights.revision")
    files = weights["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise ValueError("weights_count")
    for index, entry in enumerate(files):
        prefix = "weights.files[" + str(index) + "]"
        row = _exact(entry, WEIGHT_FILE_FIELDS, prefix)
        _relative(row["path"], prefix + ".path")
        _sha(row["sha256"], prefix + ".sha256")
        _integer(row["bytes"], prefix + ".bytes", 1, 1 << 33)
    _sorted_unique(files, "path", "weights_order", "weights_duplicate")
    if not _boolean(weights["terms_reviewed"], "weights.terms_reviewed"):
        raise ValueError("terms_not_reviewed")

    runtime = _exact(document["runtime"], RUNTIME_FIELDS, "runtime")
    _text(runtime["name"], "runtime.name", SLUG, 64)
    _text(runtime["version"], "runtime.version", VERSION, 32)
    _text(runtime["python"], "runtime.python", VERSION, 16)
    if runtime["device"] not in DEVICES:
        raise ValueError("device")
    _sha(runtime["lock_sha256"], "runtime.lock_sha256")
    if not _boolean(runtime["offline"], "runtime.offline"):
        raise ValueError("runtime_not_offline")
    if not _boolean(runtime["deterministic"], "runtime.deterministic"):
        raise ValueError("runtime_not_deterministic")
    packages = runtime["packages"]
    if not isinstance(packages, list) or not 1 <= len(packages) <= MAX_PACKAGES:
        raise ValueError("packages_count")
    for index, entry in enumerate(packages):
        prefix = "runtime.packages[" + str(index) + "]"
        row = _exact(entry, PACKAGE_FIELDS, prefix)
        _text(row["name"], prefix + ".name", SLUG, 96)
        _text(row["version"], prefix + ".version", VERSION, 32)
    _sorted_unique(packages, "name", "package_order", "package_duplicate")

    audio = _exact(document["audio"], AUDIO_FIELDS, "audio")
    _text(audio["id"], "audio.id", SLUG, 64)
    _relative(audio["path"], "audio.path")
    _sha(audio["sha256"], "audio.sha256")
    if isinstance(audio["sample_rate_hz"], bool) \
            or audio["sample_rate_hz"] not in ADMISSIBLE_SAMPLE_RATES:
        raise ValueError("sample_rate")
    if audio["channels"] != 1:
        raise ValueError("channels")
    samples = _integer(audio["samples"], "audio.samples", 1, 1 << 40)
    duration_ms = _integer(audio["duration_ms"], "audio.duration_ms", 1,
                           MAX_DURATION_MS)
    if samples != duration_ms * (audio["sample_rate_hz"] // 1000):
        raise ValueError("samples_mismatch")

    reference = _exact(document["reference"], REFERENCE_FIELDS, "reference")
    if reference["kind"] != "adjudicated_human":
        raise ValueError("reference_kind")
    _relative(reference["path"], "reference.path")
    _sha(reference["sha256"], "reference.sha256")
    reference_words = _integer(reference["word_count"],
                               "reference.word_count", 1, MAX_WORDS)
    if _integer(reference["annotator_count"],
                "reference.annotator_count", 1, 64) < 2:
        raise ValueError("reference_annotators")
    if not _boolean(reference["independent_of_asr"],
                    "reference.independent_of_asr"):
        raise ValueError("reference_not_independent")

    hypothesis = _exact(document["hypothesis"], HYPOTHESIS_FIELDS,
                        "hypothesis")
    words = hypothesis["words"]
    if not isinstance(words, list) or not 1 <= len(words) <= MAX_WORDS:
        raise ValueError("word_count_range")
    if _integer(hypothesis["word_count"], "hypothesis.word_count", 1,
                MAX_WORDS) != len(words):
        raise ValueError("word_count_mismatch")
    previous_end = 0
    seen: set[tuple[str, int, int]] = set()
    for index, word in enumerate(words):
        prefix = "words[" + str(index) + "]"
        row = _exact(word, WORD_FIELDS, prefix)
        text = _text(row["text"], prefix + ".text", None, 128)
        start = _integer(row["start_sample"], prefix + ".start_sample", 0,
                         samples)
        end = _integer(row["end_sample"], prefix + ".end_sample", 0, samples)
        if end <= start:
            raise ValueError("word_order")
        if start < previous_end:
            raise ValueError("word_overlap")
        identity = (text, start, end)
        if identity in seen:
            raise ValueError("word_duplicate")
        seen.add(identity)
        previous_end = end
    if reference_words != len(words):
        raise ValueError("reference_word_count_mismatch")

    controls = document["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("controls_count")
    kinds: list[str] = []
    ids: set[str] = set()
    for index, entry in enumerate(controls):
        prefix = "controls[" + str(index) + "]"
        row = _exact(entry, CONTROL_FIELDS, prefix)
        control_id = _text(row["id"], prefix + ".id", SLUG, 64)
        if control_id in ids:
            raise ValueError("controls_duplicate")
        ids.add(control_id)
        if row["kind"] not in CONTROL_KINDS:
            raise ValueError("controls_kind")
        kinds.append(row["kind"])
        if not _boolean(row["passes"], prefix + ".passes"):
            raise ValueError("control_not_passed")
    if len(set(kinds)) != len(kinds):
        raise ValueError("controls_duplicate")
    if kinds != sorted(kinds):
        raise ValueError("controls_order")
    if set(kinds) != set(CONTROL_KINDS):
        raise ValueError("controls_kinds")

    outcomes = _exact(document["outcomes"], OUTCOME_FIELDS, "outcomes")
    _decimal(outcomes["wer"], "outcomes.wer", "0", "1")
    mae = _decimal(outcomes["boundary_mae_ms"],
                   "outcomes.boundary_mae_ms", "0", "10000")
    p95 = _decimal(outcomes["boundary_p95_abs_error_ms"],
                   "outcomes.boundary_p95_abs_error_ms", "0", "10000")
    _decimal(outcomes["boundary_within_granularity_fraction"],
             "outcomes.boundary_within_granularity_fraction", "0", "1")
    granularity_ms = _integer(outcomes["timestamp_granularity_ms"],
                              "outcomes.timestamp_granularity_ms", 1, 1000)
    if granularity_ms not in ADMISSIBLE_GRANULARITY_MS:
        raise ValueError("granularity_unsupported")
    total_rate = _decimal(outcomes["words_per_minute_total"],
                          "outcomes.words_per_minute_total", "0.001", "600")
    speech_rate = _decimal(outcomes["words_per_minute_speech"],
                           "outcomes.words_per_minute_speech", "0.001",
                           "1200")
    _decimal(outcomes["pause_ratio"], "outcomes.pause_ratio", "0", "1")
    _decimal(outcomes["content_preservation"],
             "outcomes.content_preservation", "0", "1")
    for field in ("pitch_measured", "transient_measured",
                  "buffering_measured", "drift_measured"):
        if not _boolean(outcomes[field], "outcomes." + field):
            raise ValueError("outcome_not_measured:" + field)
    _integer(outcomes["first_output_ms"], "outcomes.first_output_ms", 0,
             600_000)
    _integer(outcomes["tail_ms"], "outcomes.tail_ms", 0, 600_000)
    if _integer(outcomes["nonfinite_count"], "outcomes.nonfinite_count", 0,
                MAX_WORDS) != 0:
        raise ValueError("outcome_nonfinite")
    if _integer(outcomes["deadline_misses"], "outcomes.deadline_misses", 0,
                MAX_WORDS) != 0:
        raise ValueError("outcome_deadline")
    if _integer(outcomes["sample_count"], "outcomes.sample_count", 1,
                1 << 40) != samples:
        raise ValueError("outcome_sample_count")
    if outcomes["qualified"] is not False:
        raise ValueError("outcome_self_qualified")
    if mae > Decimal(granularity_ms):
        raise ValueError("outcome_mae_vs_granularity")
    if p95 < mae:
        raise ValueError("outcome_p95_below_mae")

    computed = word_rate(
        [{"start_sample": word["start_sample"],
          "end_sample": word["end_sample"]} for word in words],
        samples, audio["sample_rate_hz"])
    if total_rate != Decimal(computed["words_per_minute_total"]):
        raise ValueError("outcome_rate_total")
    if speech_rate != Decimal(computed["words_per_minute_speech"]):
        raise ValueError("outcome_rate_speech")
    if _decimal(outcomes["pause_ratio"], "outcomes.pause_ratio", "0", "1") \
            != Decimal(computed["pause_ratio"]):
        raise ValueError("outcome_pause_ratio")

    rights = _exact(document["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_TRUE_FIELDS:
        if not _boolean(rights[field], "rights." + field):
            raise ValueError("rights_not_cleared:" + field)
    if _boolean(rights["claims_qualified"], "rights.claims_qualified"):
        raise ValueError("rights_claims_qualified")


def _synthetic_digest(label: str) -> str:
    return sha256_bytes(("synthetic-control:" + label).encode("ascii"))


def _control_manifest() -> dict:
    spans = []
    for index in range(8):
        start = index * 1840
        spans.append({"text": "token" + str(index + 1),
                      "start_sample": start, "end_sample": start + 1600})
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "run_id": "synthetic-schema-control",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": "0" * 40,
            "license_spdx": "MIT",
            "license_sha256": _synthetic_digest("source-license"),
        },
        "weights": {
            "model_id": "moonshine-synthetic-control",
            "revision": "1" * 40,
            "files": [
                {"path": "model/decoder.onnx",
                 "sha256": _synthetic_digest("decoder"), "bytes": 1024},
                {"path": "model/encoder.onnx",
                 "sha256": _synthetic_digest("encoder"), "bytes": 2048},
                {"path": "model/tokenizer.bin",
                 "sha256": _synthetic_digest("tokenizer"), "bytes": 512},
            ],
            "terms_reviewed": True,
        },
        "runtime": {
            "name": "moonshine",
            "version": "0.0.1",
            "python": "3.12.0",
            "device": "cpu",
            "lock_sha256": _synthetic_digest("lock"),
            "offline": True,
            "deterministic": True,
            "packages": [
                {"name": "onnxruntime", "version": "1.20.0"},
                {"name": "tokenizers", "version": "0.21.0"},
            ],
        },
        "audio": {
            "id": "synthetic-tone",
            "path": "synthetic/tone.wav",
            "sha256": _synthetic_digest("audio"),
            "sample_rate_hz": 16_000,
            "channels": 1,
            "samples": 64_000,
            "duration_ms": 4000,
        },
        "reference": {
            "kind": "adjudicated_human",
            "path": "synthetic/reference.json",
            "sha256": _synthetic_digest("reference"),
            "word_count": 8,
            "annotator_count": 2,
            "independent_of_asr": True,
        },
        "hypothesis": {"words": spans, "word_count": len(spans)},
        "controls": [
            {"id": "c-" + str(index + 1), "kind": kind, "passes": True}
            for index, kind in enumerate(CONTROL_KINDS)
        ],
        "outcomes": {
            "wer": "0.0",
            "boundary_mae_ms": "10.0",
            "boundary_p95_abs_error_ms": "16.0",
            "boundary_within_granularity_fraction": "0.95",
            "timestamp_granularity_ms": 20,
            "words_per_minute_total": "120.000",
            "words_per_minute_speech": "600.000",
            "pause_ratio": "0.800",
            "content_preservation": "0.98",
            "pitch_measured": True,
            "transient_measured": True,
            "buffering_measured": True,
            "drift_measured": True,
            "first_output_ms": 120,
            "tail_ms": 80,
            "nonfinite_count": 0,
            "deadline_misses": 0,
            "sample_count": 64_000,
            "qualified": False,
        },
        "rights": {
            "consent_recorded": True,
            "model_terms_reviewed": True,
            "runtime_license_reviewed": True,
            "output_use_defined": True,
            "commercial_use_approved": True,
            "redistribution_approved": True,
            "listening_protocol_approved": True,
            "claims_qualified": False,
        },
    }


def _case_row(case_id: str, status: str, code: str,
              synthetic: bool) -> dict:
    return {
        "id": case_id,
        "status": status,
        "code": code,
        "qualifies": False,
        "state_unchanged": status != "accepted",
        "synthetic_schema_control": synthetic,
    }


def _mutation_case(case_id: str, mutate: Any, code: str) -> dict:
    manifest = json.loads(json.dumps(_control_manifest()))
    mutate(manifest)
    try:
        validate_manifest(manifest)
    except ValueError as error:
        observed = str(error).split(":", 1)[0]
        if observed != code:
            raise ValueError("mutation_case_code_mismatch:" + case_id + ":" +
                             observed + "!=" + code) from error
        return _case_row(case_id, "rejected", observed, False)
    raise ValueError("mutation_case_did_not_reject:" + case_id)


def _raw_case(case_id: str, raw: str, code: str) -> dict:
    try:
        loads_strict(raw)
    except ValueError as error:
        observed = str(error).split(":", 1)[0]
        if observed != code:
            raise ValueError("raw_case_code_mismatch:" + case_id + ":" +
                             observed + "!=" + code) from error
        return _case_row(case_id, "rejected", observed, False)
    raise ValueError("raw_case_did_not_reject:" + case_id)


def _set(path: tuple, value: Any) -> Any:
    def apply(manifest: dict) -> None:
        target: Any = manifest
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return apply


def _drop(path: tuple) -> Any:
    def apply(manifest: dict) -> None:
        target: Any = manifest
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    return apply


def admission_controls() -> dict:
    try:
        validate_manifest(_control_manifest())
    except ValueError as error:
        raise ValueError("accepted_control_invalid:" + str(error)) from error
    cases = [_case_row("accepted-schema-control", "accepted", "none", True)]
    cases.extend([
        _case_row("root-list", "rejected",
                  str(_reject_root(["not", "a", "manifest"])), False),
        _case_row("root-null", "rejected", str(_reject_root(None)), False),
        _raw_case("duplicate-json-key",
                  '{"schema_id":"' + ADMISSION_SCHEMA_ID +
                  '","schema_id":"duplicate"}', "duplicate_json_key"),
        _raw_case("nonfinite-nan",
                  '{"schema_id":"' + ADMISSION_SCHEMA_ID + '","v":NaN}',
                  "nonfinite_json"),
        _raw_case("nonfinite-infinity",
                  '{"schema_id":"' + ADMISSION_SCHEMA_ID + '","v":Infinity}',
                  "nonfinite_json"),
        _mutation_case("missing-rights", _drop(("rights",)), "keys"),
        _mutation_case("unknown-top-field", _set(("extra",), True), "keys"),
        _mutation_case("wrong-schema-id",
                       _set(("schema_id",), "audio-sdk/other/0.1"),
                       "schema_id"),
        _mutation_case("invalid-run-id", _set(("run_id",), "Bad Run"),
                       "text_pattern"),
        _mutation_case("short-source-revision",
                       _set(("source", "revision"), "a" * 39), "text_pattern"),
        _mutation_case("uppercase-license-sha",
                       _set(("source", "license_sha256"),
                            _synthetic_digest("source-license").upper()),
                       "text_pattern"),
        _mutation_case("empty-weight-files",
                       _set(("weights", "files"), []), "weights_count"),
        _mutation_case("unsorted-weight-files",
                       lambda m: m["weights"]["files"].reverse(),
                       "weights_order"),
        _mutation_case(
            "duplicate-weight-path",
            lambda m: m["weights"]["files"][1].update(
                {"path": m["weights"]["files"][0]["path"]}),
            "weights_duplicate"),
        _mutation_case("traversal-weight-path",
                       _set(("weights", "files", 0, "path"), "../model.onnx"),
                       "relative_path"),
        _mutation_case("zero-weight-bytes",
                       _set(("weights", "files", 0, "bytes"), 0),
                       "integer_range"),
        _mutation_case("boolean-weight-bytes",
                       _set(("weights", "files", 0, "bytes"), True),
                       "integer"),
        _mutation_case("unreviewed-weight-terms",
                       _set(("weights", "terms_reviewed"), False),
                       "terms_not_reviewed"),
        _mutation_case("non-offline-runtime",
                       _set(("runtime", "offline"), False),
                       "runtime_not_offline"),
        _mutation_case("nondeterministic-runtime",
                       _set(("runtime", "deterministic"), False),
                       "runtime_not_deterministic"),
        _mutation_case("unknown-runtime-device",
                       _set(("runtime", "device"), "tpu"), "device"),
        _mutation_case("invalid-runtime-python",
                       _set(("runtime", "python"), "3"), "text_pattern"),
        _mutation_case("unsorted-runtime-packages",
                       lambda m: m["runtime"]["packages"].reverse(),
                       "package_order"),
        _mutation_case(
            "duplicate-runtime-package",
            lambda m: m["runtime"]["packages"][1].update(
                {"name": m["runtime"]["packages"][0]["name"]}),
            "package_duplicate"),
        _mutation_case("unsupported-audio-rate",
                       _set(("audio", "sample_rate_hz"), 8000),
                       "sample_rate"),
        _mutation_case("stereo-audio", _set(("audio", "channels"), 2),
                       "channels"),
        _mutation_case("sample-count-mismatch",
                       _set(("audio", "samples"), 16_000),
                       "samples_mismatch"),
        _mutation_case("absolute-audio-path",
                       _set(("audio", "path"), "/tmp/tone.wav"),
                       "relative_path"),
        _mutation_case("single-annotator",
                       _set(("reference", "annotator_count"), 1),
                       "reference_annotators"),
        _mutation_case("reference-not-independent",
                       _set(("reference", "independent_of_asr"), False),
                       "reference_not_independent"),
        _mutation_case("construction-label-reference",
                       _set(("reference", "kind"), "construction_label"),
                       "reference_kind"),
        _mutation_case("reference-word-count-mismatch",
                       _set(("reference", "word_count"), 7),
                       "reference_word_count_mismatch"),
        _mutation_case("hypothesis-word-count-mismatch",
                       _set(("hypothesis", "word_count"), 9),
                       "word_count_mismatch"),
        _mutation_case("boolean-word-start",
                       _set(("hypothesis", "words", 0, "start_sample"), True),
                       "integer"),
        _mutation_case("negative-word-start",
                       _set(("hypothesis", "words", 0, "start_sample"), -1),
                       "integer_range"),
        _mutation_case("zero-length-word",
                       _set(("hypothesis", "words", 0, "end_sample"), 0),
                       "word_order"),
        _mutation_case("overlapping-words",
                       _set(("hypothesis", "words", 1, "start_sample"), 0),
                       "word_overlap"),
        _mutation_case("empty-word-text",
                       _set(("hypothesis", "words", 0, "text"), ""),
                       "text"),
        _mutation_case("missing-control",
                       lambda m: m["controls"].pop(), "controls_count"),
        _mutation_case("unknown-control-kind",
                       _set(("controls", 0, "kind"), "music_only"),
                       "controls_kind"),
        _mutation_case("unsorted-controls",
                       lambda m: m["controls"].reverse(), "controls_order"),
        _mutation_case("control-not-passed",
                       _set(("controls", 0, "passes"), False),
                       "control_not_passed"),
        _mutation_case("nonfinite-count",
                       _set(("outcomes", "nonfinite_count"), 1),
                       "outcome_nonfinite"),
        _mutation_case("deadline-miss",
                       _set(("outcomes", "deadline_misses"), 1),
                       "outcome_deadline"),
        _mutation_case("self-qualified",
                       _set(("outcomes", "qualified"), True),
                       "outcome_self_qualified"),
        _mutation_case("mae-exceeds-granularity",
                       _set(("outcomes", "boundary_mae_ms"), "40.0"),
                       "outcome_mae_vs_granularity"),
        _mutation_case("p95-below-mae",
                       _set(("outcomes", "boundary_p95_abs_error_ms"), "4.0"),
                       "outcome_p95_below_mae"),
        _mutation_case("wer-out-of-range",
                       _set(("outcomes", "wer"), "1.5"), "decimal_range"),
        _mutation_case("wer-nan", _set(("outcomes", "wer"), "NaN"),
                       "decimal_format"),
        _mutation_case("wer-float", _set(("outcomes", "wer"), 0.1),
                       "decimal_format"),
        _mutation_case("rate-total-mismatch",
                       _set(("outcomes", "words_per_minute_total"), "12.000"),
                       "outcome_rate_total"),
        _mutation_case("rate-speech-mismatch",
                       _set(("outcomes", "words_per_minute_speech"),
                            "300.000"),
                       "outcome_rate_speech"),
        _mutation_case("pause-ratio-mismatch",
                       _set(("outcomes", "pause_ratio"), "0.500"),
                       "outcome_pause_ratio"),
        _mutation_case("sample-count-outcome-mismatch",
                       _set(("outcomes", "sample_count"), 32_000),
                       "outcome_sample_count"),
        _mutation_case("pitch-not-measured",
                       _set(("outcomes", "pitch_measured"), False),
                       "outcome_not_measured"),
        _mutation_case("consent-false",
                       _set(("rights", "consent_recorded"), False),
                       "rights_not_cleared"),
        _mutation_case("commercial-not-approved",
                       _set(("rights", "commercial_use_approved"), False),
                       "rights_not_cleared"),
        _mutation_case("claims-qualified",
                       _set(("rights", "claims_qualified"), True),
                       "rights_claims_qualified"),
    ])
    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted = [case for case in cases if case["status"] == "accepted"]
    return {
        "cases": cases,
        "controls": admission_contract(),
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(rejected),
            "accepted_schema_controls": len(accepted),
            "all_adverse_cases_rejected": len(rejected) == len(cases) - 1,
            "qualifying_results": 0,
            "accepted_control_qualifies": False,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "weights_loaded": False,
            "audio_read": False,
            "inference_performed": False,
            "network_used": False,
        },
    }


def _reject_root(value: Any) -> str:
    try:
        validate_manifest(value)
    except ValueError as error:
        code = str(error).split(":", 1)[0]
        if code != "keys":
            raise ValueError("root_case_code:" + code) from error
        return code
    raise ValueError("root_case_did_not_reject")


def admission_contract() -> dict:
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "contract_id": "audio-sdk/moonshine-timestamp-cohort-contract/0.1",
        "required_top_level_fields": list(MANIFEST_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "admissible_sample_rates_hz": list(ADMISSIBLE_SAMPLE_RATES),
        "admissible_granularity_ms": list(ADMISSIBLE_GRANULARITY_MS),
        "max_files": MAX_FILES,
        "max_packages": MAX_PACKAGES,
        "max_words": MAX_WORDS,
        "max_duration_ms": MAX_DURATION_MS,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "offline_deterministic_runtime_required": True,
        "two_independent_annotators_required": True,
        "self_qualification_rejected": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "runtime_or_weights_invoked": False,
    }


# ---------------------------------------------------------------------------
# Readiness record.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = (
        ("A01", "source_snapshot",
         "The exact moonshine-ai/moonshine source checkout at an immutable "
         "40-hex commit with reviewed MIT license text, NOTICE and per-file "
         "SHA-256. The pinned census supplies the repository URL only."),
        ("A02", "model_bundle",
         "The caller-selected exact Moonshine model and streaming-model "
         "bundle at an immutable revision: every ONNX or native weight, "
         "tokenizer, config, model card and terms file with byte count and "
         "SHA-256. The census asserts 'MIT streaming models' as a reported "
         "string only."),
        ("A03", "runtime_lock",
         "A locked, reproducible, offline Moonshine C-API or Python runtime "
         "with exact interpreter, package, ONNX Runtime and accelerator "
         "versions, device profile, lock SHA-256 and recorded host."),
        ("A04", "rights_bundle",
         "Reviewed code and weight terms, training-data provenance, output "
         "use, commercial use, redistribution and per-language derivative "
         "rights for the exact assets."),
        ("A05", "timestamp_cohort",
         "A frozen rights-cleared English cohort with exact sample rate and "
         "duration, language/speaker groups, held-out splits, two-annotator "
         "adjudicated token/word/filler/pause spans, and 1x, rate-change, "
         "rebuffer, drift, final-partial, unfamiliar-speech, music and "
         "silence controls."),
        ("A06", "acceptance_results",
         "Independent recognition and timing results: WER, boundary error at "
         "the declared granularity, words/min, pause ratio, content "
         "preservation, pitch, transient, buffering, drift, first-output and "
         "tail timing, resources and uncertainty on the exact runtime."),
        ("A07", "provider_intake",
         "A separate opt-in, OFF-by-default provider or tool intake record "
         "with an independent exact-head review. Not created here."),
        ("A08", "release_approval",
         "A release decision that closes every preceding gate. Absent."),
    )
    return [{
        "id": artifact_id,
        "kind": kind,
        "requirement": requirement,
        "present": False,
        "verified": False,
        "licensed": False,
        "admitted": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "bytes": None,
    } for artifact_id, kind, requirement in rows]


def exact_blockers() -> list[dict]:
    rows = (
        ("BLK-01", "A01", ["RG-01"],
         "The exact moonshine-ai/moonshine source checkout is absent. No "
         "reviewable tree at an immutable 40-hex commit, MIT license text, "
         "NOTICE or per-file SHA-256 pin exists in the workspace; the pinned "
         "census supplies the repository URL and a source-reported licence "
         "string only.",
         "Supply the exact source at an immutable 40-hex commit with reviewed "
         "MIT license text, complete NOTICE and per-file SHA-256; do not "
         "substitute a mirror or reconstructed tree."),
        ("BLK-02", "A02", ["RG-02"],
         "The exact Moonshine model/streaming-model bundle is absent. No ONNX "
         "or native weight, tokenizer, config, model card, terms file, byte "
         "count or SHA-256 is present at an immutable revision; the 'MIT "
         "streaming models' claim is source-reported, not locally verified.",
         "Supply the caller-selected exact model and streaming bundle at an "
         "immutable revision with every weight, tokenizer, config, model card "
         "and terms file, byte counts and SHA-256, after a weights-only "
         "inspection."),
        ("BLK-03", "A03", ["RG-03"],
         "The pinned Moonshine runtime is absent. No C-API build, Python "
         "package, ONNX Runtime, tokenizer runtime, lockfile, device profile "
         "or offline load path exists, and deterministic and real-time "
         "behavior are unverified.",
         "Supply a locked offline runtime with exact versions, archives and "
         "digests, device profile, deterministic settings and a clean-room "
         "load trace."),
        ("BLK-04", "A04", ["RG-04"],
         "Upstream code and weight terms, training-data provenance, output "
         "use, commercial use, redistribution and per-language derivative "
         "rights are unresolved. No Moonshine license text or grant is "
         "present; a census MIT string is not a grant.",
         "Provide the reviewed code and weight terms, training provenance, "
         "output-use and redistribution decision, including per-language "
         "derivative-output rights."),
        ("BLK-05", "A05", ["RG-05"],
         "No rights-cleared, consented English cohort and no independent "
         "adjudicated token/word/filler/pause span set exists. Two-annotator "
         "agreement, language/speaker groups, held-out splits and the "
         "1x/rate-change/rebuffer/drift/final-partial/unfamiliar/music/silence "
         "controls are absent.",
         "Freeze a consented permitted cohort with exact geometry, matched "
         "controls and adjudicated independent spans, then obtain review."),
        ("BLK-06", "A06", ["RG-06", "RG-07"],
         "No acceptance evidence exists. WER, boundary error, timestamp "
         "granularity, words/min, pause ratio, content preservation, pitch, "
         "transient, buffering, drift, first-output/tail timing, resources, "
         "blind listening and uncertainty are all unmeasured on the exact "
         "runtime.",
         "Run and preserve the Rate and content-preservation protocols on the "
         "exact pinned source, weights and runtime, including granularity "
         "calibration and matched controls, then obtain independent review."),
    )
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": list(gates),
        "status": "open",
        "qualifies": False,
        "statement": statement,
        "required_action": action,
    } for blocker_id, artifact_id, gates, statement, action in rows]


def release_gates(projection: dict) -> list[dict]:
    rows = (
        ("RG-01", "exact licensed source revision and snapshot",
         "Supply the moonshine-ai/moonshine source at an immutable 40-hex "
         "commit with reviewed MIT license, NOTICE and per-file SHA-256."),
        ("RG-02", "exact model, streaming model and tokenizer bundle",
         "Supply every weight, tokenizer, config, card and terms file at an "
         "immutable revision with byte count and SHA-256."),
        ("RG-03", "pinned offline runtime, device and deterministic load",
         "Supply a locked offline C-API or Python runtime with archive "
         "digests, device profile and clean-room load trace."),
        ("RG-04", "rights, output use, provenance and redistribution",
         "Supply reviewed terms, training provenance, output-use, commercial "
         "and redistribution decisions."),
        ("RG-05", "rights-cleared cohort and independent adjudicated spans",
         "Supply a consented frozen cohort with two independent annotators, "
         "adjudication, agreement and matched controls."),
        ("RG-06", "Rate acceptance profile and timestamp granularity",
         "Measure 1x, rate changes, mapping, duration, buffering, pitch, "
         "transient, rebuffer, drift, final partial window and speech "
         "preservation, and calibrate token/word timing."),
        ("RG-07", "content preservation, independent scoring and listening",
         "Measure WER/semantic preservation with an independent scorer and "
         "complete authorized listening or a labelled predictive screen."),
        ("RG-08", "opt-in provider intake, independent review and release",
         "Add a separate OFF-by-default intake after RG-01 to RG-07, obtain "
         "independent exact-head review and a release decision."),
    )
    return [{"id": gate_id, "title": title, "status": "blocked",
             "qualifies": False, "reopen_condition": condition,
             "linked_row": dict(projection)}
            for gate_id, title, condition in rows]


def rate_outcomes() -> list[dict]:
    return [{
        "id": row["id"].replace("RATE", "OUT"),
        "requirement": row["requirement"],
        "status": "blocked",
        "value": None,
        "qualifies": False,
    } for row in RATE_REQUIREMENTS]


def required_results() -> dict:
    return {
        "exact_source_present": False,
        "exact_model_bundle_present": False,
        "exact_runtime_present": False,
        "licensed_conjunction_present": False,
        "rights_cleared": False,
        "cohort_present": False,
        "engine_executed": False,
        "timestamp_granularity_measured": False,
        "rate_profile_measured": False,
        "content_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def qualification() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualifying_results": 0,
        "blocked_release_gates": 8,
        "open_blockers": 6,
        "exact_source_present": False,
        "exact_model_bundle_present": False,
        "exact_runtime_present": False,
        "exact_licensed_conjunction_present": False,
        "weights_present": False,
        "runtime_present": False,
        "source_present": False,
        "rights_cleared": False,
        "cohort_present": False,
        "rate_profile_measured": False,
        "timestamp_granularity_verified": False,
        "content_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "missing_result_promoted": False,
        "no_result_qualifies": True,
        "reasons": [
            "no exact source revision, license text or per-file pin",
            "no exact model, streaming model or tokenizer bundle",
            "no pinned offline runtime or deterministic load trace",
            "code and weight rights, output use and provenance unresolved",
            "no consented cohort or independent adjudicated spans",
            "no Rate, granularity, content, listening or device result",
        ],
    }


def scope() -> dict:
    return {
        "task_local_only": True,
        "directory": TASK_PREFIX,
        "write_scope": WRITE_SCOPE,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_build_change": False,
        "ci_change": False,
        "default_selected": False,
        "network_used": False,
        "download_attempted": False,
        "real_corpus": False,
        "weights": False,
        "runtime": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
    }


def boundary() -> dict:
    return {
        "installed_v0_geometry": {
            "sample_rate_hz": 16_000,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "unchanged": True,
        },
        "provider_registration": False,
        "descriptor_or_registry_change": False,
        "default_change": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "external_assets_copied": False,
        "task_local_only": True,
    }


def upstream_record() -> dict:
    return {
        "candidate": "Moonshine",
        "source_repository": SOURCE_REPOSITORY,
        "source_repository_source": CENSUS_PATH,
        "source_revision": None,
        "source_revision_requirement": "immutable 40-hex commit",
        "source_license_reported": "MIT",
        "model_license_reported": "MIT streaming models",
        "license_text_present": False,
        "license_verified": False,
        "model_repository": MODEL_REPOSITORY,
        "model_revision": None,
        "tokenizer_pinned": False,
        "checkpoint_files": None,
        "weight_bytes": None,
        "runtime_pinned": False,
        "paper_url": PAPER_URL,
        "reported_role": REPORTED_ROLE,
        "reported_finding": REPORTED_FINDING,
        "reported_caveat": REPORTED_CAVEAT,
        "reported_precedence": REPORTED_PRECEDENCE,
        "reported_languages": "English-first",
        "reported_timestamp_granularity": "needs testing",
        "architecture_asserted": False,
        "sample_rate_hz": None,
        "sample_format": None,
        "streaming_geometry_pinned": False,
        "source_reported_only": True,
        "admitted_as_result": False,
        "qualifies": False,
    }


def reproduction() -> dict:
    return {
        "interpreter": "Python 3.11+, standard library only",
        "commands": [
            "export PYTHONDONTWRITEBYTECODE=1",
            "python3 run.py all",
            "python3 -m unittest -v test_reference.py",
            "python3 verify.py",
        ],
        "repeat_count": 3,
        "byte_identical_required": True,
        "network_required": False,
        "runtime_required": False,
    }


def _probes_block() -> dict:
    probes = absence_probes()
    return {"probes": probes, "summary": absence_summary(probes)}


def build_contract() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    pins_source, pins_boundary = verify_pins()
    probes = _probes_block()
    return {
        "contract_id": CONTRACT_ID,
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "owner": OWNER,
        "reviewer": REVIEWER,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "disposition": {
            "decision": DECISION,
            "status": STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "proposal_only": True,
            "incomplete": True,
            "not_qualified": True,
            "missing_result_qualifies": False,
            "qualifying_results": 0,
            "blocked_release_gates": 8,
            "defer_before": "implementation_or_provider_intake",
            "production_exposure": "DEFER",
            "promotion": "defer",
            "registered": False,
            "default_enabled": False,
        },
        "qualification": qualification(),
        "scope": scope(),
        "boundary": boundary(),
        "public_v0_geometry": {
            "sample_rate_hz": 16_000,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "preserved": True,
            "sdk_callback_invoked": False,
        },
        "non_claims": list(NON_CLAIMS),
        "profile_phrases": list(PROFILE_PHRASES),
        "profile_source": PROFILE_SOURCE_REL,
        "upstream_record": upstream_record(),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "source_pin_rows": pins_source,
        "boundary_pin_rows": pins_boundary,
        "absence": probes,
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(projection),
        "rate_profile_requirements": list(RATE_REQUIREMENTS),
        "rate_outcomes": rate_outcomes(),
        "required_results": required_results(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "linked_row_projection": projection,
        "linked_row_fields": list(BOARD_ROW_FIELDS),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "reproduction": reproduction(),
    }


def build_report() -> dict:
    contract = build_contract()
    contract_sha = object_digest(contract)
    pins_source, pins_boundary = verify_pins()
    probes = _probes_block()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "owner": OWNER,
        "reviewer": REVIEWER,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "contract_sha256": contract_sha,
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "non_claims": contract["non_claims"],
        "profile_source": contract["profile_source"],
        "profile_phrases": contract["profile_phrases"],
        "upstream_record": contract["upstream_record"],
        "source_pins": pins_source,
        "boundary_pins": pins_boundary,
        "absence": probes,
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "source": contract["profile_source"],
            "rows": contract["rate_profile_requirements"],
        },
        "rate_outcomes": {"rows": contract["rate_outcomes"]},
        "granularity_control": granularity_control(),
        "admission": admission_controls(),
        "required_results": contract["required_results"],
        "peer_evidence": contract["peer_evidence"],
        "linked_row_identity": {
            "projection": contract["linked_row_projection"],
            "sha256": board_row_digest(contract["linked_row_projection"]),
            "fields": contract["linked_row_fields"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": contract["linked_rows"],
            "linked_rows_sha256": contract["linked_rows_sha256"],
            "mutable_fields_excluded": contract["mutable_fields_excluded"],
        },
        "reproduction": contract["reproduction"],
    }


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "contract_id", "schema_id", "task", "title", "component", "mode",
        "profile", "profile_label", "decision", "status", "qualification_status",
        "proposal_only", "qualification", "scope", "boundary",
        "public_v0_geometry", "upstream_record", "required_artifacts",
        "exact_blockers", "release_gates", "rate_profile_requirements",
        "rate_outcomes", "required_results", "linked_row_projection",
        "linked_rows", "linked_rows_sha256", "board_file_pinned",
        "reproduction",
    )
    for field in required:
        if field not in contract:
            raise ValueError("contract_field_missing:" + field)
    if contract["task"] != TASK or contract["component"] != COMPONENT_ID:
        raise ValueError("contract_identity")
    if contract["mode"] != MODE or contract["repository"] != REPOSITORY:
        raise ValueError("contract_mode_or_repository")
    if contract["profile"] != PROFILE or contract["profile_label"] != \
            PROFILE_LABEL:
        raise ValueError("contract_profile")
    if contract["decision"] != DECISION or contract["status"] != STATUS \
            or contract["qualification_status"] != QUALIFICATION_STATUS \
            or contract["proposal_only"] is not True:
        raise ValueError("contract_disposition")
    gates = contract["release_gates"]
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gates")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-{:02d}".format(index) \
                or gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            raise ValueError("contract_gate:" + str(index))
    if len(contract["exact_blockers"]) != 6:
        raise ValueError("contract_blockers")
    if len(contract["rate_profile_requirements"]) != 8:
        raise ValueError("contract_rate_rows")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    if BOARD_TASK_ROW in contract["source_pins"] \
            or BOARD_TASK_ROW in contract["boundary_pins"]:
        raise ValueError("mutable_board_pinned")
    for key, value in contract["scope"].items():
        if key in ("task_local_only", "directory", "write_scope"):
            continue
        if value is not False:
            raise ValueError("contract_scope_overclaim:" + key)


def verify_pins() -> tuple[dict, dict]:
    def collect(pins: dict[str, str], root: Path,
                label: str) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                raise ValueError(label + "_pin_missing:" + relative)
            actual = sha256_file(path)
            if actual != expected:
                raise ValueError(label + "_pin_mismatch:" + relative)
            result[relative] = {
                "sha256": expected,
                "actual": actual,
                "verified": True,
            }
        return result

    return (collect(SOURCE_PINS, AUDIO_ROOT, "source"),
            collect(BOUNDARY_PINS, WORKTREE, "boundary"))


# ---------------------------------------------------------------------------
# Merge-base task-local scope. A merged sibling package must not be attributed
# to this branch, and an out-of-scope edit must still fail closed.
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> Optional[str]:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> Optional[str]:
    best: Optional[str] = None
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
        if _git(worktree, "merge-base", "--is-ancestor", best,
                base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--",
                  ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


def verify_sources_manifest(payload: bytes) -> None:
    lines = payload.decode("ascii").splitlines()
    if not lines or not lines[0].startswith("# SHA-256 pins for"):
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
    expected = {"source:" + name for name in SOURCE_PINS}
    expected |= set(BOUNDARY_PINS)
    expected |= {TASK_PREFIX + name for name in (
        "LICENSES.md", "README.md", "SOURCES.sha256.license",
        "contract.json", "contract.json.license", "reference.py",
        "report.json", "report.json.license", "report.json.sha256",
        "report.json.sha256.license", "run.py", "test_reference.py",
        "verify.py")}
    if seen != expected:
        raise ValueError("sources_set")
    if TASK_PREFIX + "SOURCES.sha256" in seen:
        raise ValueError("sources_self_pinned")
