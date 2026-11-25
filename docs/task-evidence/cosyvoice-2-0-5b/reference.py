# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence builder for SDK-COSYVOICE-2-0-5B.

This module never loads a model, imports an upstream package, reads audio, runs
inference, scores quality, performs listening, measures a device or produces a
release claim. It verifies stable pins, probes fixed paths, exercises a
fail-closed synthetic admission contract and emits canonical JSON.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/cosyvoice-2-0-5b/"

TASK = "SDK-COSYVOICE-2-0-5B"
TASK_TITLE = "CosyVoice 2 0.5B"
COMPONENT_ID = "cosyvoice-2-0-5b"
REPOSITORY = "audio-sdk"
MODE = "implementation"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/cosyvoice-2-0-5b-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/cosyvoice-2-0-5b-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/cosyvoice-2-0-5b-report/0.1"
BASE_COMMIT = "b8ac930b88f4cb7b87e01498a838b0a0654a1aef"
BRANCH = "swarm/SDK-COSYVOICE-2-0-5B"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# ---------------------------------------------------------------------------
# Stable local pins. Every path is read-only evidence, never executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json":
        "b2465f3cbb2f52ce2e538e7d52f24f26861a22e8ce7defbf17953d9f9a3cf1ee",
    "research/voice-conversion-eval-20261101/results/cosyvoice2/asr.json":
        "71ce950cabfc2a5273dd969a48e5a1ba6df743c5b47c39b9efb7a39a0445f228",
    "research/voice-conversion-eval-20261101/results/cosyvoice2/"
    "source_prompt_streaming_tts.wav":
        "4a74fdd7fbf29c51da8c8c66f29b366605eb9d9b4b466fd753bb18b84785beb1",
    "research/voice-conversion-eval-20261101/scripts/run_cosyvoice2_eval.py":
        "84733c8732cebe130defed6859fc6a0483f1f814dac6ccb55297d15899ea21a8",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/LICENSE":
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/requirements.txt":
        "6619a7f7f95e6c7c23dc82471294ee168a4fc0e901ab4e123881fff71f38d94c",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/cosyvoice/cli/"
    "cosyvoice.py":
        "4b2a605f129d172cd031286a14a591396c2e8ed0bf53258acc7445525fdaa65b",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/cosyvoice/cli/"
    "model.py":
        "421ba52dd956505667668e0aec7fdcbcd85d733b52725b2d595bc32bcbb53ef9",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/example.py":
        "5285fe12f5a71a5225dcd06072496a8e31772d8e7fb0af5fe428c72c637691ec",
    "research/voice-conversion-eval-20261101/data/"
    "source_ljspeech_lj001-0001.wav":
        "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b",
    "research/voice-conversion-eval-20261101/data/target_rtvc_p360.flac":
        "fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md":
        "5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md":
        "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
    "research/voice-conversion-eval-20261101/agent-chatterbox-breadth/"
    "REPORT.md":
        "0ff66ba53399c495106c21c43072ff17292c9ac0be00a04fde06c312bcd73ce8",
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
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": REPOSITORY,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                   "SDK-FND-PROVIDER"],
}

# ---------------------------------------------------------------------------
# Exact upstream source, model and historical evidence identity.
# ---------------------------------------------------------------------------

SOURCE_ROOT_REL = "research/voice-conversion-eval-20261101/repos/cosyvoice"
SOURCE_REPOSITORY = "https://github.com/FunAudioLLM/CosyVoice"
SOURCE_REVISION = "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc"
SOURCE_LICENSE = "Apache-2.0"
SOURCE_LICENSE_SHA256 = (
    "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"
)
SOURCE_TREE_DIGEST = (
    "9b0d2b60b87463dfbdca55c740c422957549cd0e009810c10b27c67ceb35e3f7"
)
SOURCE_FILE_COUNT = 156
SOURCE_SYMLINK_COUNT = 8
SOURCE_BYTE_COUNT = 3_073_286
SUBMODULE_REL = "third_party/Matcha-TTS"
SUBMODULE_REPOSITORY = "https://github.com/shivammehta25/Matcha-TTS"
SUBMODULE_REVISION = "dd9105b34bf2be2230f4aa1e4769fb586a3c824e"
SUBMODULE_TREE_DIGEST = (
    "de38023574f1dc4f5626987c267dd5790347f2baf9ada07e06fae4849d301a5f"
)
SUBMODULE_FILE_COUNT = 107
SUBMODULE_SYMLINK_COUNT = 1
SUBMODULE_BYTE_COUNT = 826_391
MAX_SOURCE_FILES = 4096
MAX_SOURCE_BYTES = 64 * 1024 * 1024

MODEL_ID = "CosyVoice2-0.5B"
MODEL_REPOSITORY = "https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B"
MODEL_REVISION_REFERENCE = "eec1ae6c79877dbd9379285cf8789c9e0879293d"
MODEL_ROOT_REL = "research/voice-conversion-eval-20261101/models/cosyvoice2"
MODEL_REFERENCED_FILES = (
    "cosyvoice2.yaml",
    "campplus.onnx",
    "speech_tokenizer_v2.onnx",
    "spk2info.pt",
    "llm.pt",
    "flow.pt",
    "hift.pt",
    "CosyVoice-BlankEN",
)
MODEL_SAMPLE_RATE_HZ = 24_000
MODEL_CHANNELS = 1
MODEL_SAMPLE_FORMAT = "f32"
MODEL_TASK = "text_to_speech_reference"
MODEL_WEIGHT_TERMS = (
    "not locally evidenced; exact model-card terms and training-data "
    "provenance must accompany the caller-supplied bundle")
MAX_MODEL_HASH_BYTES = 64 * 1024 * 1024

HISTORICAL_OUTPUT_REL = (
    "research/voice-conversion-eval-20261101/results/cosyvoice2/"
    "source_prompt_streaming_tts.wav")
HISTORICAL_OUTPUT_SHA256 = (
    "4a74fdd7fbf29c51da8c8c66f29b366605eb9d9b4b466fd753bb18b84785beb1")
HISTORICAL_OUTPUT_BYTES = 480_044
HISTORICAL_METRICS_REL = (
    "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json")
HISTORICAL_ASR_REL = (
    "research/voice-conversion-eval-20261101/results/cosyvoice2/asr.json")
HF_CACHE_REL = (
    "~/.cache/huggingface/hub/models--FunAudioLLM--CosyVoice2-0.5B")
HF_REF_SHA256 = (
    "969a3cdebde21b016bd49e20024440b97b7f8b9cf93ec7b3f089627442b8a04d")

# Reported isolated evaluation environment (historical; absent now).
PINNED_PYTHON_VERSION = "3.11"
HISTORICAL_RUNTIME_PACKAGES = {
    "torch": "2.6.0",
    "torchaudio": "2.6.0",
    "numpy": "1.26.4",
    "soundfile": "0.14.0",
    "transformers": "4.51.3",
    "onnxruntime": "1.18.0",
}
REQUIRED_RUNTIME_PACKAGES = ("torch", "torchaudio", "numpy", "soundfile",
                             "transformers", "onnxruntime")
HISTORICAL_RUNTIME_REPORT = (
    "research/voice-conversion-eval-20261101/agent-chatterbox-breadth/"
    "REPORT.md")
PINNED_ENVIRONMENT_PATHS = (
    "research/voice-conversion-eval-20261101/.venv-chatterbox",
    "research/voice-conversion-eval-20261101/.venv-chatterbox/bin/python",
    "data/envs/cosyvoice",
    "data/envs/cosyvoice/bin/python",
    "data/envs/chatterbox",
    "data/envs/chatterbox/bin/python",
)

# Fixed, bounded absence probes. Any present probe forces a reopen.
ABSENCE_PROBES = (
    MODEL_ROOT_REL,
    MODEL_ROOT_REL + "/cosyvoice2.yaml",
    MODEL_ROOT_REL + "/llm.pt",
    MODEL_ROOT_REL + "/flow.pt",
    MODEL_ROOT_REL + "/hift.pt",
    MODEL_ROOT_REL + "/campplus.onnx",
    MODEL_ROOT_REL + "/speech_tokenizer_v2.onnx",
    MODEL_ROOT_REL + "/spk2info.pt",
    MODEL_ROOT_REL + "/CosyVoice-BlankEN",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/pretrained_models",
    "research/voice-conversion-eval-20261101/repos/cosyvoice/pretrained_models/"
    "CosyVoice2-0.5B",
    "data/models/cosyvoice2",
    "data/models/cosyvoice",
    "data/models/CosyVoice2-0.5B",
    "docs/task-evidence/cosyvoice-2-0-5b/reference_output.wav",
    "docs/task-evidence/cosyvoice-2-0-5b/cohort",
    "data/envs/cosyvoice",
    "data/envs/chatterbox",
    "data/wheels",
)

PEER_EVIDENCE = (
    "docs/task-evidence/chatterbox-nano/README.md",
    "docs/task-evidence/chatterbox-nano/contract.json",
    "docs/task-evidence/chatterbox-nano/report.json",
    "docs/task-evidence/llvc/README.md",
    "docs/task-evidence/fastenhancer-small-reference/README.md",
)

# ---------------------------------------------------------------------------
# Voice acceptance profile, verbatim requirement phrases.
# ---------------------------------------------------------------------------

PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker "
    "groups.",
    "Preserve text and semantic content, identity/similarity and naturalness "
    "as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target "
    "condition.",
    "Consent, reference availability and output use are independent gates.",
)
PROFILE_ROW = "Voice"

VOICE_REQUIREMENTS = (
    {
        "id": "VOI-01",
        "requirement": "Freeze permitted input and target references.",
        "status": "blocked",
        "evidence": "No exact weight bundle is present; the historical run's "
                    "prompt is one LJ Speech clip whose voice-cloning consent "
                    "and output-use terms are unresolved.",
        "qualifies": False,
    },
    {
        "id": "VOI-02",
        "requirement": "Freeze task, language and speaker groups.",
        "status": "blocked",
        "evidence": "The historical run is one English prompt/text pair. No "
                    "frozen language or speaker-group definition exists.",
        "qualifies": False,
    },
    {
        "id": "VOI-03",
        "requirement": "Preserve text and semantic content as an outcome.",
        "status": "blocked",
        "evidence": "No output is regenerated here. The historical ASR WER 0% "
                    "is one-item research provenance, not a local result.",
        "qualifies": False,
    },
    {
        "id": "VOI-04",
        "requirement": "Report identity/similarity separately from content.",
        "status": "blocked",
        "evidence": "No independent or in-model speaker-similarity result for "
                    "CosyVoice 2 0.5B exists in the pinned evidence.",
        "qualifies": False,
    },
    {
        "id": "VOI-05",
        "requirement": "Report naturalness as a separate outcome.",
        "status": "blocked",
        "evidence": "No MOS, preference panel or authorized listening result "
                    "exists.",
        "qualifies": False,
    },
    {
        "id": "VOI-06",
        "requirement": "Record alignment, first-output/tail timing and the "
                       "exact target condition.",
        "status": "blocked",
        "evidence": "The historical 23.81 s first chunk and 8.07x file RTF "
                    "are one CPU-only research observation and cannot be "
                    "reproduced; microphone/device timing was not measured.",
        "qualifies": False,
    },
    {
        "id": "VOI-07",
        "requirement": "Treat consent, reference availability and output use "
                       "as independent gates.",
        "status": "blocked",
        "evidence": "The prompt speaker's consent, the reference's permitted "
                    "use and the output's permitted use are not established.",
        "qualifies": False,
    },
)

NON_CLAIMS = (
    "No exact CosyVoice 2 0.5B weight bundle, model output or vendor result is "
    "loaded, executed or reproduced.",
    "No real speech, prompt speaker consent, corpus, reference output or audio "
    "sample is generated, copied or embedded.",
    "No listening, MOS, speaker-similarity, naturalness, WER or quality result "
    "is produced.",
    "No first-chunk, tail, device, memory, streaming or real-time-factor "
    "measurement is produced.",
    "No TTS-to-speech-conversion equivalence, benchmark or release claim is "
    "made.",
    "No provider is registered, no descriptor or registry is changed, and no "
    "installed v0, ABI, default, build or CI behaviour changes.",
)

HISTORICAL_ENTRIES = (
    {
        "id": "HIST-01",
        "scope": "One English LJ Speech prompt/text pair, CPU-only Apple M1, "
                 "official zero-shot streaming TTS path",
        "result": "10.0 s output in four chunks; first chunk 23.810076 s from "
                  "the inference call; generation 80.661524 s; file RTF "
                  "8.066152; ASR WER 0.0%; clipped fraction 0.0.",
        "status": "historical_research_not_reproduced_not_qualified",
        "qualifies": False,
        "note": "Weights were removed after the run. The result is TTS, not "
                "audio-to-audio conversion, and is not a local result.",
    },
    {
        "id": "HIST-02",
        "scope": "Model initialization and output file for the same run",
        "result": "Model initialization 22.421157 s; output 24 kHz WAV, "
                  "480044 bytes, SHA-256 "
                  "4a74fdd7fbf29c51da8c8c66f29b366605eb9d9b4b466fd753bb18b84785beb1.",
        "status": "historical_research_not_reproduced_not_qualified",
        "qualifies": False,
        "note": "The output file is retained but the exact weights and runtime "
                "are absent, so it cannot be regenerated or parity-checked.",
    },
    {
        "id": "HIST-03",
        "scope": "Prompt loading, device and transport scope",
        "result": "First-chunk timing includes prompt loading and encoding; no "
                  "microphone, transport or call-device buffering is included.",
        "status": "historical_research_not_reproduced_not_qualified",
        "qualifies": False,
        "note": "The recorded values do not establish physical availability "
                "delay or an end-to-end call latency.",
    },
)

# ---------------------------------------------------------------------------
# Canonical JSON and strict parsing.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    """Canonical compact sorted-key UTF-8 JSON with exactly one trailing LF."""
    assert_no_float(value)
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return (text + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def parse_strict_json_text(payload: bytes) -> dict:
    """Parse strict JSON: no BOM, duplicate keys, NaN/Infinity or non-object."""
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError("bom_rejected")
    try:
        text = payload.decode("utf-8", "strict")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json:" + error.msg) from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_artifact")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_no_float(item)


def canonical_report(report: dict) -> tuple[str, str]:
    assert_no_float(report)
    payload = canonical_bytes(report)
    return payload.decode("utf-8"), sha256_bytes(payload)


# ---------------------------------------------------------------------------
# Stable board identity.
# ---------------------------------------------------------------------------


def _project(row: dict) -> dict:
    missing = [field for field in ("id", "title", "mode", "repository",
                                   "depends_on") if field not in row]
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def board_row_projection(path: Path | None = None) -> dict:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    matches = [row for row in rows
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0])
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
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
    return tuple(result)


def board_row_digest(projection: dict) -> str:
    return sha256_bytes(canonical_bytes(projection))


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    value = linked_rows() if rows is None else rows
    return sha256_bytes(canonical_bytes([dict(row) for row in value]))


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TASK_TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "component": COMPONENT_ID,
    }


# ---------------------------------------------------------------------------
# Probes.
# ---------------------------------------------------------------------------


def _git_head(root: Path) -> str | None:
    git_path = root / ".git"
    if git_path.is_file():
        text = git_path.read_text(encoding="ascii").strip()
        if not text.startswith("gitdir: "):
            return None
        target = Path(text[len("gitdir: "):])
        git_path = (target if target.is_absolute()
                    else (root / target).resolve())
    if not git_path.is_dir():
        return None
    head_path = git_path / "HEAD"
    if not head_path.is_file():
        return None
    head = head_path.read_text(encoding="ascii").strip()
    if head.startswith("ref: "):
        ref_path = git_path / head[5:]
        if not ref_path.is_file():
            return None
        value = ref_path.read_text(encoding="ascii").strip()
        return value if HEX40.fullmatch(value) else None
    return head if HEX40.fullmatch(head) else None


def _tracked_files(repo: Path) -> list[str]:
    process = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        capture_output=True, check=False)
    if process.returncode != 0:
        raise ValueError("git_ls_files_failed")
    return sorted(item.decode("utf-8") for item in
                  process.stdout.split(b"\0") if item)


def _tree_pin(repo: Path, skip: tuple[str, ...] = ()) -> dict:
    rows: list[str] = []
    file_count = 0
    symlink_count = 0
    total_bytes = 0
    for relative in _tracked_files(repo):
        if relative in skip:
            continue
        path = repo / relative
        if path.is_symlink():
            rows.append(relative + " link " + os.readlink(path) + "\n")
            symlink_count += 1
            continue
        if not path.is_file():
            raise ValueError("tracked_file_absent:" + relative)
        payload = path.read_bytes()
        total_bytes += len(payload)
        file_count += 1
        if file_count > MAX_SOURCE_FILES or total_bytes > MAX_SOURCE_BYTES:
            raise ValueError("source_tree_too_large")
        rows.append(relative + " " + sha256_bytes(payload) + " " +
                    str(len(payload)) + "\n")
    return {
        "tree_digest": sha256_bytes("".join(rows).encode("utf-8")),
        "file_count": file_count,
        "symlink_count": symlink_count,
        "byte_count": total_bytes,
    }


def _clean_tracked(repo: Path) -> bool:
    process = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1",
         "--untracked-files=no"],
        capture_output=True, text=True, check=False)
    return process.returncode == 0 and not process.stdout.strip()


def source_probe(root: Path | None = None) -> dict:
    workspace = AUDIO_ROOT if root is None else Path(root)
    source = workspace / SOURCE_ROOT_REL
    if not source.is_dir():
        return {"status": "source_absent", "present": False,
                "path": SOURCE_ROOT_REL}
    try:
        main = _tree_pin(source, skip=(SUBMODULE_REL,))
        submodule = source / SUBMODULE_REL
        sub = (_tree_pin(submodule) if submodule.is_dir() else
               {"tree_digest": None, "file_count": 0, "symlink_count": 0,
                "byte_count": 0})
    except (OSError, ValueError) as error:
        return {"status": "source_unreadable", "present": False,
                "path": SOURCE_ROOT_REL, "reason": str(error)}
    revision = _git_head(source)
    sub_revision = _git_head(submodule)
    license_path = source / "LICENSE"
    license_sha256 = (sha256_file(license_path)
                      if license_path.is_file() else None)
    present = (
        revision == SOURCE_REVISION
        and main["tree_digest"] == SOURCE_TREE_DIGEST
        and main["file_count"] == SOURCE_FILE_COUNT
        and main["symlink_count"] == SOURCE_SYMLINK_COUNT
        and main["byte_count"] == SOURCE_BYTE_COUNT
        and sub_revision == SUBMODULE_REVISION
        and sub["tree_digest"] == SUBMODULE_TREE_DIGEST
        and sub["file_count"] == SUBMODULE_FILE_COUNT
        and sub["symlink_count"] == SUBMODULE_SYMLINK_COUNT
        and sub["byte_count"] == SUBMODULE_BYTE_COUNT
        and license_sha256 == SOURCE_LICENSE_SHA256
        and _clean_tracked(source)
    )
    return {
        "status": "present_pinned" if present else "source_mismatch",
        "present": present,
        "path": SOURCE_ROOT_REL,
        "repository": SOURCE_REPOSITORY,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "license": SOURCE_LICENSE,
        "license_sha256": license_sha256,
        "expected_license_sha256": SOURCE_LICENSE_SHA256,
        "tree_digest": main["tree_digest"],
        "expected_tree_digest": SOURCE_TREE_DIGEST,
        "file_count": main["file_count"],
        "expected_file_count": SOURCE_FILE_COUNT,
        "symlink_count": main["symlink_count"],
        "expected_symlink_count": SOURCE_SYMLINK_COUNT,
        "byte_count": main["byte_count"],
        "expected_byte_count": SOURCE_BYTE_COUNT,
        "clean_tracked_worktree": _clean_tracked(source),
        "submodule": {
            "path": SUBMODULE_REL,
            "repository": SUBMODULE_REPOSITORY,
            "revision": sub_revision,
            "expected_revision": SUBMODULE_REVISION,
            "tree_digest": sub["tree_digest"],
            "expected_tree_digest": SUBMODULE_TREE_DIGEST,
            "file_count": sub["file_count"],
            "expected_file_count": SUBMODULE_FILE_COUNT,
            "symlink_count": sub["symlink_count"],
            "expected_symlink_count": SUBMODULE_SYMLINK_COUNT,
            "byte_count": sub["byte_count"],
            "expected_byte_count": SUBMODULE_BYTE_COUNT,
        },
        "executed": False,
        "note": "Read-only digest over tracked non-.git files; no upstream file "
                "is copied, imported or executed.",
    }


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return -1


def weights_probe(root: Path | None = None) -> dict:
    workspace = AUDIO_ROOT if root is None else Path(root)
    model_root = workspace / MODEL_ROOT_REL
    entries = []
    present_count = 0
    for name in MODEL_REFERENCED_FILES:
        path = model_root / name
        present = path.exists()
        if present:
            present_count += 1
        byte_count = _safe_size(path) if present else None
        digest = None
        if present and path.is_file() and byte_count is not None and \
                0 <= byte_count <= MAX_MODEL_HASH_BYTES:
            digest = sha256_file(path)
        entries.append({
            "name": name,
            "path": MODEL_ROOT_REL + "/" + name,
            "present": present,
            "byte_count": byte_count,
            "sha256": digest,
            "admitted": False,
        })
    cache = Path(os.path.expanduser(HF_CACHE_REL))
    ref = cache / "refs/main"
    ref_revision = (ref.read_text(encoding="ascii").strip()
                    if ref.is_file() else None)
    ref_digest = sha256_file(ref) if ref.is_file() else None
    snapshot_present = (cache / "snapshots").exists()
    blobs_present = (cache / "blobs").exists()
    return {
        "status": ("blocked_exact_model_bundle_absent" if present_count == 0
                   else "blocked_exact_model_bundle_incomplete"),
        "model_id": MODEL_ID,
        "model_repository": MODEL_REPOSITORY,
        "model_revision_reference": MODEL_REVISION_REFERENCE,
        "weight_terms": MODEL_WEIGHT_TERMS,
        "model_root": MODEL_ROOT_REL,
        "required_file_count": len(MODEL_REFERENCED_FILES),
        "present_file_count": present_count,
        "pinned_model_present": False,
        "admitted_model": None,
        "downloaded": False,
        "files": entries,
        "hf_cache": {
            "path": "~/.cache/huggingface/hub/models--FunAudioLLM--"
                    "CosyVoice2-0.5B",
            "cache_dir_present": cache.is_dir(),
            "ref_present": ref.is_file(),
            "ref_revision": ref_revision,
            "expected_ref_revision": MODEL_REVISION_REFERENCE,
            "ref_sha256": ref_digest,
            "expected_ref_sha256": HF_REF_SHA256,
            "snapshot_dir_present": snapshot_present,
            "blobs_dir_present": blobs_present,
            "admitted": False,
            "opened": False,
        },
        "note": "No weight file is downloaded, loaded, imported or executed. "
                "The cache ref is metadata only; no snapshot or blob exists.",
    }


def runtime_probe() -> dict:
    paths_found = [relative for relative in PINNED_ENVIRONMENT_PATHS
                   if (AUDIO_ROOT / relative).exists()]
    return {
        "status": "blocked_pinned_runtime_absent",
        "pinned_python_version": PINNED_PYTHON_VERSION,
        "pinned_package_versions": dict(HISTORICAL_RUNTIME_PACKAGES),
        "historical_runtime_report": HISTORICAL_RUNTIME_REPORT,
        "historical_versions_verified_here": False,
        "pinned_environment_paths_checked": list(PINNED_ENVIRONMENT_PATHS),
        "pinned_environment_paths_found": paths_found,
        "pinned_runtime_present": False,
        "pinned_runtime_complete": False,
        "pinned_runtime_version_verified": False,
        "imported_or_executed": False,
        "note": "Fixed-path probe only. No package is installed, imported, "
                "opened or downloaded; module presence in the evidence "
                "interpreter is not recorded because it is not an admission "
                "signal.",
    }


def absence_probes(root: Path | None = None) -> list[dict]:
    workspace = AUDIO_ROOT if root is None else Path(root)
    rows = []
    for relative in ABSENCE_PROBES:
        path = workspace / relative
        rows.append({
            "path": relative,
            "present": path.exists(),
            "searched_workspace": True,
            "recursive_walk": False,
        })
    return rows


def absence_summary(probes: list[dict]) -> dict:
    present = sum(1 for row in probes if row["present"])
    return {
        "probe_count": len(probes),
        "present_count": present,
        "all_probes_absent": present == 0,
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed synthetic admission controls.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = "audio-sdk/cosyvoice-2-0-5b-asset-admission/0.1"
MANIFEST_TOP_KEYS = ("schema_id", "component_id", "task", "source", "model",
                     "runtime", "format", "rights", "reference", "cohort")
MAX_MODEL_FILES = 32
MAX_MODEL_FILE_BYTES = 8 * 1024 * 1024 * 1024
MAX_REFERENCE_SAMPLES = 24_000 * 3_600
MAX_COHORT_ITEMS = 10_000
UNRESOLVED_TOKENS = ("unknown", "pending", "unspecified", "not specified",
                     "tbd", "n/a", "none")


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _bounded_int(value: Any, low: int, high: int, field: str) -> int:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(field + "_nonfinite")
        raise ValueError(field + "_invalid")
    if not _is_int(value):
        raise ValueError(field + "_invalid")
    if value < low or value > high:
        raise ValueError(field + "_invalid")
    return value


def _hex(value: Any, length: int, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(field + "_invalid")
    pattern = HEX40 if length == 40 else HEX64
    if not pattern.fullmatch(value):
        raise ValueError(field + "_invalid")
    return value


def _safe_relative(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 255:
        raise ValueError(field + "_invalid")
    if value.startswith("/") or ".." in value.split("/") or "\\" in value:
        raise ValueError(field + "_invalid")
    return value


def _exact_keys(obj: Any, keys: tuple[str, ...], prefix: str) -> None:
    if not isinstance(obj, dict):
        raise ValueError(prefix + "_not_object")
    for key in obj:
        if key not in keys:
            raise ValueError("unexpected_field:" + prefix + "." + str(key))
    for key in keys:
        if key not in obj:
            raise ValueError("missing_field:" + prefix + "." + key)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + "_invalid")
    return value


def admit_manifest(manifest: Any) -> dict:
    """Validate one caller-supplied manifest; pure and fail-closed."""
    if not isinstance(manifest, dict):
        return {"status": "rejected", "code": "manifest_not_object"}
    try:
        _exact_keys(manifest, MANIFEST_TOP_KEYS, "manifest")
        if manifest["schema_id"] != MANIFEST_SCHEMA_ID:
            raise ValueError("schema_id_mismatch")
        if manifest["component_id"] != COMPONENT_ID:
            raise ValueError("component_id_mismatch")
        if manifest["task"] != MODEL_TASK:
            raise ValueError("task_mismatch")

        source = manifest["source"]
        _exact_keys(source, ("repository", "revision", "license"), "source")
        if source["repository"] != SOURCE_REPOSITORY:
            raise ValueError("source_repository_invalid")
        _hex(source["revision"], 40, "source_revision")
        if source["license"] != SOURCE_LICENSE:
            raise ValueError("source_license_mismatch")

        model = manifest["model"]
        _exact_keys(model, ("model_id", "repository", "revision", "files",
                            "weight_terms"), "model")
        if model["model_id"] != MODEL_ID:
            raise ValueError("model_id_mismatch")
        if model["repository"] != MODEL_REPOSITORY:
            raise ValueError("model_repository_mismatch")
        _hex(model["revision"], 40, "model_revision")
        files = model["files"]
        if not isinstance(files, list) or not 1 <= len(files) <= MAX_MODEL_FILES:
            raise ValueError("model_files_count")
        names = set()
        for item in files:
            _exact_keys(item, ("name", "byte_count", "sha256"), "model_file")
            name = _safe_relative(item["name"], "model_file_name")
            if name in names:
                raise ValueError("model_file_duplicate")
            names.add(name)
            _bounded_int(item["byte_count"], 1, MAX_MODEL_FILE_BYTES,
                         "model_file_byte_count")
            _hex(item["sha256"], 64, "model_file_sha256")
        terms = _text(model["weight_terms"], "model_weight_terms").lower()
        if any(token in terms for token in UNRESOLVED_TOKENS):
            raise ValueError("model_weight_terms_unresolved")

        runtime = manifest["runtime"]
        _exact_keys(runtime, ("python_version", "packages",
                              "environment_sha256"), "runtime")
        if runtime["python_version"] != PINNED_PYTHON_VERSION:
            raise ValueError("runtime_python_version_mismatch")
        packages = runtime["packages"]
        if not isinstance(packages, list) or not 1 <= len(packages) <= 64:
            raise ValueError("runtime_packages_count")
        versions: dict[str, str] = {}
        for item in packages:
            _exact_keys(item, ("name", "version"), "runtime_package")
            name = _text(item["name"], "runtime_package_name")
            version = item["version"]
            if not isinstance(version, str) or not version.strip():
                raise ValueError("runtime_package_version_invalid")
            versions[name] = version
        for name in REQUIRED_RUNTIME_PACKAGES:
            if name not in versions:
                raise ValueError("runtime_package_missing:" + name)
            expected = HISTORICAL_RUNTIME_PACKAGES[name]
            if versions[name] != expected:
                raise ValueError("runtime_package_version_mismatch:" + name)
        _hex(runtime["environment_sha256"], 64, "runtime_environment_sha256")

        fmt = manifest["format"]
        _exact_keys(fmt, ("sample_rate_hz", "channels", "sample_format",
                          "exact_chunk_samples"), "format")
        if _bounded_int(fmt["sample_rate_hz"], 1, 384_000,
                        "format_sample_rate") != MODEL_SAMPLE_RATE_HZ:
            raise ValueError("format_sample_rate_mismatch")
        if _bounded_int(fmt["channels"], 1, 8,
                        "format_channels") != MODEL_CHANNELS:
            raise ValueError("format_channels_mismatch")
        if fmt["sample_format"] != MODEL_SAMPLE_FORMAT:
            raise ValueError("format_sample_format_mismatch")
        chunk = fmt["exact_chunk_samples"]
        if chunk is not None:
            _bounded_int(chunk, 1, 384_000, "format_chunk_samples")

        rights = manifest["rights"]
        _exact_keys(rights, ("code_license", "model_license", "consent",
                             "redistribution", "output_use",
                             "training_data_reference"), "rights")
        if rights["code_license"] != SOURCE_LICENSE:
            raise ValueError("rights_code_license_mismatch")
        license_text = _text(rights["model_license"],
                             "rights_model_license").lower()
        if any(token in license_text for token in UNRESOLVED_TOKENS):
            raise ValueError("rights_model_license_unresolved")
        if rights["consent"] is not True:
            raise ValueError("rights_consent_missing")
        if rights["redistribution"] is not True:
            raise ValueError("rights_redistribution_missing")
        if rights["output_use"] is not True:
            raise ValueError("rights_output_use_missing")
        _text(rights["training_data_reference"],
              "rights_training_data_reference")

        reference = manifest["reference"]
        _exact_keys(reference, ("path", "sha256", "sample_count", "finite"),
                    "reference")
        _safe_relative(reference["path"], "reference_path")
        _hex(reference["sha256"], 64, "reference_sha256")
        _bounded_int(reference["sample_count"], 1, MAX_REFERENCE_SAMPLES,
                     "reference_sample_count")
        if reference["finite"] is not True:
            raise ValueError("reference_not_finite")

        cohort = manifest["cohort"]
        _exact_keys(cohort, ("items", "rights_cleared", "frozen", "languages",
                             "speaker_groups"), "cohort")
        _bounded_int(cohort["items"], 1, MAX_COHORT_ITEMS, "cohort_items")
        if cohort["rights_cleared"] is not True:
            raise ValueError("cohort_rights_not_cleared")
        if cohort["frozen"] is not True:
            raise ValueError("cohort_not_frozen")
        for language in ("languages", "speaker_groups"):
            value = cohort[language]
            if not isinstance(value, list) or not value:
                raise ValueError("cohort_" + language + "_empty")
            for entry in value:
                _text(entry, "cohort_" + language)
    except ValueError as error:
        return {"status": "rejected", "code": str(error)}
    return {"status": "accepted", "code": "ok"}


def _base_manifest() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "component_id": COMPONENT_ID,
        "task": MODEL_TASK,
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": SOURCE_REVISION,
            "license": SOURCE_LICENSE,
        },
        "model": {
            "model_id": MODEL_ID,
            "repository": MODEL_REPOSITORY,
            "revision": MODEL_REVISION_REFERENCE,
            "files": [
                {"name": "cosyvoice2.yaml", "byte_count": 1024,
                 "sha256": "a" * 64},
                {"name": "llm.pt", "byte_count": 1024,
                 "sha256": "b" * 64},
            ],
            "weight_terms": "Apache-2.0 model card with training-data notice",
        },
        "runtime": {
            "python_version": PINNED_PYTHON_VERSION,
            "packages": [
                {"name": name, "version": version}
                for name, version in sorted(HISTORICAL_RUNTIME_PACKAGES.items())
            ],
            "environment_sha256": "c" * 64,
        },
        "format": {
            "sample_rate_hz": MODEL_SAMPLE_RATE_HZ,
            "channels": MODEL_CHANNELS,
            "sample_format": MODEL_SAMPLE_FORMAT,
            "exact_chunk_samples": 960,
        },
        "rights": {
            "code_license": SOURCE_LICENSE,
            "model_license": "Apache-2.0 with training-data notice",
            "consent": True,
            "redistribution": True,
            "output_use": True,
            "training_data_reference": "model-card training-data statement",
        },
        "reference": {
            "path": "reference.json",
            "sha256": "d" * 64,
            "sample_count": 24_000,
            "finite": True,
        },
        "cohort": {
            "items": 4,
            "rights_cleared": True,
            "frozen": True,
            "languages": ["en"],
            "speaker_groups": ["consented-reference-speakers"],
        },
    }


def _nested(manifest: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    target: Any = manifest
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    if isinstance(target, list):
        target[int(parts[-1])] = value
    else:
        target[parts[-1]] = value


def _drop(manifest: dict, path: str) -> None:
    parts = path.split(".")
    target: Any = manifest
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    if isinstance(target, list):
        del target[int(parts[-1])]
    else:
        del target[parts[-1]]


def _mutation_case(case_id: str, path: str, value: Any, code: str) -> dict:
    manifest = _base_manifest()
    _nested(manifest, path, value)
    result = admit_manifest(manifest)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("admission_case_drift:" + case_id + ":" +
                         result.get("code", "accepted"))
    return {
        "id": case_id,
        "kind": "manifest",
        "field": path,
        "code": code,
        "status": "rejected",
        "qualifies": False,
        "state_unchanged": True,
        "evidence_class": "synthetic_admission_control_not_evidence",
    }


def _drop_case(case_id: str, path: str, code: str) -> dict:
    manifest = _base_manifest()
    _drop(manifest, path)
    result = admit_manifest(manifest)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("admission_case_drift:" + case_id + ":" +
                         result.get("code", "accepted"))
    return {
        "id": case_id,
        "kind": "manifest",
        "field": path,
        "code": code,
        "status": "rejected",
        "qualifies": False,
        "state_unchanged": True,
        "evidence_class": "synthetic_admission_control_not_evidence",
    }


def _strict_case(case_id: str, payload: bytes, code: str) -> dict:
    try:
        parse_strict_json_text(payload)
    except ValueError as error:
        actual = str(error).split(":", 1)[0]
        if actual != code:
            raise ValueError("strict_case_drift:" + case_id + ":" + actual)
    else:
        raise ValueError("strict_case_accepted:" + case_id)
    return {
        "id": case_id,
        "kind": "strict_json",
        "field": "document",
        "code": code,
        "status": "rejected",
        "qualifies": False,
        "state_unchanged": True,
        "evidence_class": "synthetic_admission_control_not_evidence",
    }


def _raw_manifest_case(case_id: str, value: Any, code: str) -> dict:
    result = admit_manifest(value)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("admission_case_drift:" + case_id + ":" +
                         result.get("code", "accepted"))
    return {
        "id": case_id,
        "kind": "manifest",
        "field": "manifest",
        "code": code,
        "status": "rejected",
        "qualifies": False,
        "state_unchanged": True,
        "evidence_class": "synthetic_admission_control_not_evidence",
    }


def admission_controls() -> dict:
    cases = [
        _strict_case("MISS-01", b"[]{", "invalid_json"),
        _strict_case("MISS-02", b"[]", "json_root_not_object"),
        _strict_case("MISS-03", b'{"a":1,"a":2}', "duplicate_key"),
        _strict_case("MISS-04", b'{"a":NaN}', "nonfinite_json"),
        _strict_case("MISS-05", b'{"a":Infinity}', "nonfinite_json"),
        _strict_case("MISS-06", b'\xef\xbb\xbf{"a":1}', "bom_rejected"),
        _strict_case("MISS-07", b'{"a":1} trailing', "invalid_json"),
        _mutation_case("MISS-08", "schema_id", "other/0.1",
                       "schema_id_mismatch"),
        _mutation_case("MISS-09", "component_id", "other",
                       "component_id_mismatch"),
        _mutation_case("MISS-10", "task", "voice_conversion", "task_mismatch"),
        _drop_case("MISS-11", "source", "missing_field:manifest.source"),
        _mutation_case("MISS-12", "source.revision", "ABCDEF",
                       "source_revision_invalid"),
        _mutation_case("MISS-13", "source.license", "MIT",
                       "source_license_mismatch"),
        _mutation_case("MISS-14", "source.repository", "",
                       "source_repository_invalid"),
        _drop_case("MISS-15", "model", "missing_field:manifest.model"),
        _mutation_case("MISS-16", "model.model_id", "CosyVoice-TTS",
                       "model_id_mismatch"),
        _mutation_case("MISS-17", "model.revision", "xyz",
                       "model_revision_invalid"),
        _mutation_case("MISS-18", "model.files", [], "model_files_count"),
        _mutation_case("MISS-19", "model.files",
                       [{"name": "f" + str(index), "byte_count": 1,
                         "sha256": "a" * 64} for index in range(33)],
                       "model_files_count"),
        _mutation_case("MISS-20", "model.files.0.sha256", "zz",
                       "model_file_sha256_invalid"),
        _mutation_case("MISS-21", "model.files.0.byte_count", -1,
                       "model_file_byte_count_invalid"),
        _mutation_case("MISS-22", "model.files.0.byte_count", float("nan"),
                       "model_file_byte_count_nonfinite"),
        _mutation_case("MISS-23", "model.files.0.byte_count", 2 ** 40,
                       "model_file_byte_count_invalid"),
        _mutation_case("MISS-24", "model.files.0.name", "../escape",
                       "model_file_name_invalid"),
        _mutation_case("MISS-25", "model.files.0.name", "/absolute",
                       "model_file_name_invalid"),
        _mutation_case("MISS-26", "model.weight_terms", "unknown",
                       "model_weight_terms_unresolved"),
        _drop_case("MISS-27", "runtime", "missing_field:manifest.runtime"),
        _mutation_case("MISS-28", "runtime.python_version", "3.10",
                       "runtime_python_version_mismatch"),
        _mutation_case("MISS-29", "runtime.packages", [],
                       "runtime_packages_count"),
        _mutation_case("MISS-30", "runtime.packages",
                       [{"name": "numpy", "version": "1.26.4"}],
                       "runtime_package_missing:torch"),
        _mutation_case("MISS-31", "runtime.packages.0.version", "9.9.9",
                       "runtime_package_version_mismatch:numpy"),
        _mutation_case("MISS-32", "runtime.environment_sha256", "bad",
                       "runtime_environment_sha256_invalid"),
        _mutation_case("MISS-33", "format.sample_rate_hz", 16000,
                       "format_sample_rate_mismatch"),
        _mutation_case("MISS-34", "format.channels", 2,
                       "format_channels_mismatch"),
        _mutation_case("MISS-35", "format.sample_format", "i16",
                       "format_sample_format_mismatch"),
        _mutation_case("MISS-36", "format.sample_rate_hz", float("nan"),
                       "format_sample_rate_nonfinite"),
        _mutation_case("MISS-37", "format.exact_chunk_samples", float("inf"),
                       "format_chunk_samples_nonfinite"),
        _mutation_case("MISS-38", "format.exact_chunk_samples", -1,
                       "format_chunk_samples_invalid"),
        _drop_case("MISS-39", "rights", "missing_field:manifest.rights"),
        _mutation_case("MISS-40", "rights.code_license", "MIT",
                       "rights_code_license_mismatch"),
        _mutation_case("MISS-41", "rights.model_license", "unknown",
                       "rights_model_license_unresolved"),
        _mutation_case("MISS-42", "rights.consent", False,
                       "rights_consent_missing"),
        _mutation_case("MISS-43", "rights.redistribution", False,
                       "rights_redistribution_missing"),
        _mutation_case("MISS-44", "rights.output_use", False,
                       "rights_output_use_missing"),
        _mutation_case("MISS-45", "rights.training_data_reference", "",
                       "rights_training_data_reference_invalid"),
        _drop_case("MISS-46", "reference",
                   "missing_field:manifest.reference"),
        _mutation_case("MISS-47", "reference.sha256", "bad",
                       "reference_sha256_invalid"),
        _mutation_case("MISS-48", "reference.sample_count", -1,
                       "reference_sample_count_invalid"),
        _mutation_case("MISS-49", "reference.sample_count", float("nan"),
                       "reference_sample_count_nonfinite"),
        _mutation_case("MISS-50", "reference.sample_count",
                       MAX_REFERENCE_SAMPLES + 1,
                       "reference_sample_count_invalid"),
        _mutation_case("MISS-51", "reference.finite", False,
                       "reference_not_finite"),
        _mutation_case("MISS-52", "reference.path", "../escape.json",
                       "reference_path_invalid"),
        _drop_case("MISS-53", "cohort", "missing_field:manifest.cohort"),
        _mutation_case("MISS-54", "cohort.items", 0, "cohort_items_invalid"),
        _mutation_case("MISS-55", "cohort.items", float("inf"),
                       "cohort_items_nonfinite"),
        _mutation_case("MISS-56", "cohort.rights_cleared", False,
                       "cohort_rights_not_cleared"),
        _mutation_case("MISS-57", "cohort.frozen", False, "cohort_not_frozen"),
        _mutation_case("MISS-58", "cohort.languages", [],
                       "cohort_languages_empty"),
        _mutation_case("MISS-59", "cohort.speaker_groups", [],
                       "cohort_speaker_groups_empty"),
        _mutation_case("MISS-60", "reference.finite", 0,
                       "reference_not_finite"),
        _mutation_case("MISS-61", "model.files.0", [], "model_file_not_object"),
        _mutation_case("MISS-62", "model.files.0", {"name": "x",
                       "byte_count": 1, "sha256": "a" * 64, "extra": 1},
                       "unexpected_field:model_file.extra"),
        _mutation_case("MISS-63", "cohort.items", True,
                       "cohort_items_invalid"),
        _mutation_case("MISS-64", "format.channels", True,
                       "format_channels_invalid"),
        _mutation_case("MISS-65", "manifest_extra", 1,
                       "unexpected_field:manifest.manifest_extra"),
        _raw_manifest_case("MISS-66", [], "manifest_not_object"),
    ]
    control_manifest = _base_manifest()
    control = admit_manifest(control_manifest)
    if control["status"] != "accepted":
        raise ValueError("schema_control_rejected:" + control["code"])
    controls = [{
        "id": "CTL-01",
        "kind": "manifest",
        "code": "ok",
        "status": "accepted",
        "qualifies": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "checks": len(MANIFEST_TOP_KEYS),
        "weights_loaded": False,
        "runtime_invoked": False,
        "audio_read": False,
        "artifacts_probed": False,
    }]
    return {"cases": cases, "controls": controls}


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "manifest_fields": list(MANIFEST_TOP_KEYS),
        "source_fields": ["repository", "revision", "license"],
        "model_fields": ["model_id", "repository", "revision", "files",
                         "weight_terms"],
        "model_file_fields": ["name", "byte_count", "sha256"],
        "runtime_fields": ["python_version", "packages",
                           "environment_sha256"],
        "runtime_package_fields": ["name", "version"],
        "format_fields": ["sample_rate_hz", "channels", "sample_format",
                          "exact_chunk_samples"],
        "rights_fields": ["code_license", "model_license", "consent",
                          "redistribution", "output_use",
                          "training_data_reference"],
        "reference_fields": ["path", "sha256", "sample_count", "finite"],
        "cohort_fields": ["items", "rights_cleared", "frozen", "languages",
                          "speaker_groups"],
        "pinned_python_version": PINNED_PYTHON_VERSION,
        "pinned_package_versions": dict(HISTORICAL_RUNTIME_PACKAGES),
        "pinned_source_revision": SOURCE_REVISION,
        "pinned_model_revision_reference": MODEL_REVISION_REFERENCE,
        "pinned_sample_rate_hz": MODEL_SAMPLE_RATE_HZ,
        "max_model_files": MAX_MODEL_FILES,
        "max_model_file_bytes": MAX_MODEL_FILE_BYTES,
        "max_reference_samples": MAX_REFERENCE_SAMPLES,
        "max_cohort_items": MAX_COHORT_ITEMS,
        "weights_loaded": False,
        "runtime_invoked": False,
        "audio_read": False,
        "inference_performed": False,
        "accepted_controls_are_evidence": False,
    }


# ---------------------------------------------------------------------------
# Artifacts, blockers and gates.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    return [
        {
            "id": "ART-01",
            "kind": "exact_cosyvoice2_0_5b_weights",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "byte_count": None,
            "requirement": "The exact CosyVoice2-0.5B inference bundle at "
                           "model revision " + MODEL_REVISION_REFERENCE + ": "
                           + ", ".join(MODEL_REFERENCED_FILES) + ", each with "
                           "its own SHA-256 and byte count, plus the "
                           "CosyVoice-BlankEN tokenizer/language-model files.",
        },
        {
            "id": "ART-02",
            "kind": "pinned_python_runtime",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "byte_count": None,
            "requirement": "A reproducible CPython " + PINNED_PYTHON_VERSION +
                           " environment with the exact package lock, including "
                           "the reported torch 2.6.0, torchaudio 2.6.0, numpy "
                           "1.26.4, soundfile 0.14.0, transformers 4.51.3 and "
                           "a NumPy-1.x-compatible onnxruntime, with an "
                           "environment digest.",
        },
        {
            "id": "ART-03",
            "kind": "rights_and_consent",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "byte_count": None,
            "requirement": "Model-card weight terms, training-data provenance, "
                           "prompt-speaker consent, reference-voice permitted "
                           "use and output-use/redistribution clearance.",
        },
        {
            "id": "ART-04",
            "kind": "approved_reference_parity",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "byte_count": None,
            "requirement": "An approved caller-supplied reference input vector "
                           "and output, or a regenerated exact-runtime output "
                           "with matching SHA-256 and finite-sample proof.",
        },
        {
            "id": "ART-05",
            "kind": "rights_cleared_voice_cohort",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "byte_count": None,
            "requirement": "A frozen multi-item TTS cohort with permitted "
                           "prompt audio/transcripts, language and speaker "
                           "groups, and explicit consent/use terms.",
        },
        {
            "id": "ART-06",
            "kind": "independent_voice_scoring_and_timing",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "byte_count": None,
            "requirement": "Independent content, identity/similarity and "
                           "naturalness scoring, authorized listening, and "
                           "first-output/tail/device timing on the exact "
                           "runtime.",
        },
    ]


def exact_blockers() -> list[dict]:
    return [
        {
            "id": "BLK-01",
            "artifact_id": "ART-01",
            "status": "open",
            "qualifies": False,
            "statement": "The exact CosyVoice2-0.5B weight bundle at "
                         "revision reference " + MODEL_REVISION_REFERENCE +
                         " is absent. Required files are " +
                         ", ".join(MODEL_REFERENCED_FILES) +
                         ". The Hugging Face cache has only a ref file and no "
                         "snapshots or blobs.",
            "required_action": "Supply the exact caller-held weight bundle "
                               "with per-file SHA-256, byte counts, model "
                               "revision and the CosyVoice-BlankEN files.",
            "linked_gates": ["RG-01", "RG-04"],
        },
        {
            "id": "BLK-02",
            "artifact_id": "ART-02",
            "status": "open",
            "qualifies": False,
            "statement": "The isolated CPython " + PINNED_PYTHON_VERSION +
                         " evaluation environment and exact package lock are "
                         "absent; no import, execution or version check is "
                         "possible. The historical report names torch 2.6.0, "
                         "torchaudio 2.6.0 and numpy 1.26.4.",
            "required_action": "Supply a reproducible environment lock, "
                               "interpreter identity and environment digest, "
                               "and permit read-only verification.",
            "linked_gates": ["RG-02", "RG-07"],
        },
        {
            "id": "BLK-03",
            "artifact_id": "ART-03",
            "status": "open",
            "qualifies": False,
            "statement": "The source revision " + SOURCE_REVISION + " is "
                         "Apache-2.0, but model-weight terms, training-data "
                         "provenance, prompt-speaker consent and output-use "
                         "rights are unresolved.",
            "required_action": "Provide reviewed model/training terms and "
                               "independent consent, reference-use and "
                               "output-use approvals.",
            "linked_gates": ["RG-03"],
        },
        {
            "id": "BLK-04",
            "artifact_id": "ART-04",
            "status": "open",
            "qualifies": False,
            "statement": "No approved reference vector or regenerable output is "
                         "available. The historical WAV at "
                         + HISTORICAL_OUTPUT_REL + " has SHA-256 "
                         + HISTORICAL_OUTPUT_SHA256 + " but its weights are "
                         "gone.",
            "required_action": "Supply an approved frozen input/output "
                               "reference or restore the exact weights and "
                               "runtime for parity regeneration.",
            "linked_gates": ["RG-04"],
        },
        {
            "id": "BLK-05",
            "artifact_id": "ART-05",
            "status": "open",
            "qualifies": False,
            "statement": "No frozen, rights-cleared TTS cohort exists; the "
                         "historical result is one English LJ Speech "
                         "prompt/text pair.",
            "required_action": "Provide a frozen multi-item cohort with "
                               "permitted prompts, transcripts, language and "
                               "speaker groups.",
            "linked_gates": ["RG-05", "RG-06"],
        },
        {
            "id": "BLK-06",
            "artifact_id": "ART-06",
            "status": "open",
            "qualifies": False,
            "statement": "No independent content, identity/similarity or "
                         "naturalness result, listening panel or exact-runtime "
                         "first-output/tail timing exists.",
            "required_action": "Run independent scoring and authorized "
                               "listening on the frozen cohort, then measure "
                               "first-output/tail timing, memory and streaming "
                               "on the exact runtime.",
            "linked_gates": ["RG-06", "RG-07", "RG-08"],
        },
    ]


def release_gates() -> list[dict]:
    rows = [
        ("RG-01", "exact licensed source and 0.5B weight bundle pinned",
         "The Apache-2.0 source is present and pinned, but the exact "
         "CosyVoice2-0.5B weight bundle is absent.",
         "Supply and pin the exact weights and CosyVoice-BlankEN files."),
        ("RG-02", "exact pinned Python runtime and package lock",
         "The isolated CPython " + PINNED_PYTHON_VERSION + " environment is "
         "absent and no exact lock or environment digest is available.",
         "Supply a reproducible lock, interpreter and environment digest."),
        ("RG-03", "weight terms, training data, consent and output use",
         "Model-weight terms, training-data provenance, prompt-speaker "
         "consent and output-use rights are unresolved.",
         "Provide reviewed rights, consent and permitted-use approvals."),
        ("RG-04", "exact reference parity",
         "No approved reference vector or regenerable output exists; the "
         "historical WAV cannot be regenerated.",
         "Supply an approved reference pair or restore exact weights and "
         "runtime for parity."),
        ("RG-05", "frozen rights-cleared voice/TTS cohort",
         "No frozen multi-item prompt/text cohort with language and speaker "
         "groups exists.",
         "Provide the frozen, permitted cohort and its manifest."),
        ("RG-06", "independent content, identity and naturalness results",
         "No independent WER/content, speaker-similarity, naturalness or "
         "authorized listening result exists.",
         "Run and preserve independent scoring and an authorized listening "
         "panel."),
        ("RG-07", "alignment, first-output/tail, memory and streaming",
         "No exact-runtime first-output/tail, memory or streaming measurement "
         "exists; historical values are not a local result.",
         "Measure alignment, first-output/tail, memory and streaming on the "
         "exact runtime and workload."),
        ("RG-08", "opt-in provider intake and release decision",
         "No adapter, descriptor, public-surface decision or independent "
         "review exists.",
         "Add a task-local opt-in adapter only after RG-01 to RG-07 pass, then "
         "obtain independent review."),
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
        "status": "historical_research_not_reproduced_not_qualified",
        "qualifies": False,
        "entries": [dict(row) for row in HISTORICAL_ENTRIES],
        "artifact": {
            "path": HISTORICAL_OUTPUT_REL,
            "sha256": HISTORICAL_OUTPUT_SHA256,
            "byte_count": HISTORICAL_OUTPUT_BYTES,
            "present": (AUDIO_ROOT / HISTORICAL_OUTPUT_REL).is_file(),
            "regenerable": False,
            "admitted_as_result": False,
        },
        "metrics_path": HISTORICAL_METRICS_REL,
        "asr_path": HISTORICAL_ASR_REL,
    }


def voice_profile_block() -> dict:
    rows = [dict(row) for row in VOICE_REQUIREMENTS]
    return {
        "profile": PROFILE,
        "status": "blocked",
        "rows": rows,
        "frozen_inputs_and_targets": False,
        "language_and_speaker_groups_frozen": False,
        "content_result": False,
        "identity_result": False,
        "naturalness_result": False,
        "alignment_reported": False,
        "first_output_timing_measured": False,
        "tail_timing_measured": False,
        "exact_target_condition_recorded": False,
        "consent_cleared": False,
        "reference_availability_resolved": False,
        "output_use_cleared": False,
        "authorized_listening": False,
    }


def profile_source() -> dict:
    return {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "row": PROFILE_ROW,
        "phrases": list(PROFILE_PHRASES),
    }


# ---------------------------------------------------------------------------
# Disposition, boundary and scope blocks.
# ---------------------------------------------------------------------------


def disposition_block() -> dict:
    return {
        "decision": DECISION,
        "status": "incomplete",
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "promotion": "defer",
        "production_exposure": "DEFER",
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "task_local_only": True,
        "files_outside_task_directory_written": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "default_selected": False,
        "enabled_by_default": False,
        "processor_exposure": False,
        "registered": False,
    }


def exact_scope_block() -> dict:
    return {
        "single_component": COMPONENT_ID,
        "task_local_evidence_only": True,
        "provider_work": False,
        "runtime_work": False,
        "release_work": False,
        "write_scope": WRITE_SCOPE,
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "exact_source_present": True,
        "exact_pinned_model_present": False,
        "exact_runtime_present": False,
        "weight_rights_cleared": False,
        "real_corpus_present": False,
        "real_result_present": False,
        "reference_parity_result": False,
        "quality_result": False,
        "listening_result": False,
        "timing_or_peak_result": False,
        "benchmark_result": False,
        "missing_result_promoted": False,
    }


def scope_block() -> dict:
    return {
        "source_present": True,
        "source_executed": False,
        "pinned_weights_present": False,
        "pinned_weights_read": False,
        "runtime_present": False,
        "runtime_executed": False,
        "inference_performed": False,
        "real_corpus": False,
        "audio_read": False,
        "tts_performed": False,
        "voice_conversion_performed": False,
        "quality_scored": False,
        "listening": False,
        "device_timing": False,
        "first_output_timing": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
        "historical_output_hashed": True,
        "historical_output_admitted": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def model_geometry() -> dict:
    return {
        "task": MODEL_TASK,
        "sample_rate_hz": MODEL_SAMPLE_RATE_HZ,
        "channels": MODEL_CHANNELS,
        "sample_format": MODEL_SAMPLE_FORMAT,
        "execution": "offline_and_streaming_generator",
        "exact_chunk_samples": None,
        "streaming_chunking": "provider_defined_not_pinned",
        "output_length": "generated_not_identity",
        "source_time_mapping": "not_applicable_text_to_speech",
        "measured": False,
    }


def rights_gap() -> dict:
    return {
        "blocked": True,
        "code_license": SOURCE_LICENSE,
        "model_license": MODEL_WEIGHT_TERMS,
        "training_data_reference": None,
        "consent_reference": None,
        "output_use_reference": None,
        "redistribution_decision_reference": None,
        "note": "Apache-2.0 covers the pinned source checkout. Model-weight "
                "terms, training-data provenance, prompt-speaker consent and "
                "output-use rights are not established.",
    }


def upstream_record() -> dict:
    return {
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "source_license": SOURCE_LICENSE,
        "source_tree_digest": SOURCE_TREE_DIGEST,
        "submodule_repository": SUBMODULE_REPOSITORY,
        "submodule_revision": SUBMODULE_REVISION,
        "submodule_tree_digest": SUBMODULE_TREE_DIGEST,
        "model_id": MODEL_ID,
        "model_repository": MODEL_REPOSITORY,
        "model_revision_reference": MODEL_REVISION_REFERENCE,
        "model_weight_terms": MODEL_WEIGHT_TERMS,
        "required_model_files": list(MODEL_REFERENCED_FILES),
        "sample_rate_hz": MODEL_SAMPLE_RATE_HZ,
        "task_kind": MODEL_TASK,
        "not_voice_conversion": True,
        "historical_values_are_provenance_only": True,
        "not_reproduced_here": True,
    }


def pin_rows(pins: dict[str, str], root: Path) -> dict:
    rows = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return rows


def linked_identity_block() -> dict:
    rows = linked_rows()
    return {
        "selector": "stable-row-identity/0.1:" + ",".join(BOARD_ROW_FIELDS),
        "projection": board_row_projection(),
        "sha256": board_row_digest(board_row_projection()),
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
    }


# ---------------------------------------------------------------------------
# Report and contract assembly.
# ---------------------------------------------------------------------------


def _assert_absence(probes: list[dict]) -> None:
    present = [row["path"] for row in probes if row["present"]]
    if present:
        raise ValueError("absence_probe_present:" + ",".join(present))


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "write_scope": WRITE_SCOPE,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "upstream_record": upstream_record(),
        "geometry": {"public_v0": public_v0_geometry(),
                     "model": model_geometry()},
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "voice_profile_requirements": [dict(row) for row in
                                       VOICE_REQUIREMENTS],
        "voice_profile": voice_profile_block(),
        "historical_evidence": historical_evidence_block(),
        "rights_gap": rights_gap(),
        "admission_contract": admission_contract_block(),
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "board_file_pinned": False,
        "board_row_projection": board_row_projection(),
        "board_row_sha256": board_row_digest(board_row_projection()),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
        "board_status_is_observation_only": True,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    probes = absence_probes()
    _assert_absence(probes)
    admission = admission_controls()
    contract = build_contract()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "task_id": TASK,
        "task_title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "write_scope": WRITE_SCOPE,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": {"public_v0": public_v0_geometry(),
                     "model": model_geometry()},
        "upstream_record": upstream_record(),
        "source_probe": source_probe(),
        "weights_probe": weights_probe(),
        "runtime_probe": runtime_probe(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "conclusion": "The exact CosyVoice2-0.5B weight bundle, pinned "
                          "runtime and any caller reference output are absent "
                          "at every fixed probe location.",
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": [row["id"] for row in release_gates()],
        "linked_row_identity": linked_identity_block(),
        "voice_profile": voice_profile_block(),
        "voice_profile_requirements": [dict(row) for row in
                                       VOICE_REQUIREMENTS],
        "historical_evidence": historical_evidence_block(),
        "rights_gap": rights_gap(),
        "admission": {
            "policy": "task_local_fail_closed_admission_not_runtime_behavior",
            "cases": admission["cases"],
            "schema_controls": admission["controls"],
            "summary": {
                "case_count": len(admission["cases"]),
                "rejected_count": len(admission["cases"]),
                "accepted_schema_controls": len(admission["controls"]),
                "qualifying_results": 0,
                "state_advanced_on_rejection": False,
                "runtime_invoked": False,
                "weights_loaded": False,
                "audio_read": False,
                "inference_performed": False,
            },
        },
        "peer_evidence": [{
            "path": relative,
            "read_only": True,
            "reproduced_here": False,
        } for relative in PEER_EVIDENCE],
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": {
            "runs": 3,
            "byte_identical": True,
            "cold_start_processes": True,
            "canonical_json": True,
            "sorted_keys": True,
            "compact_separators": True,
            "trailing_newline": True,
        },
        "reproduction": {
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                     "test_reference.py",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }
    assert_no_float(report)
    return report


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if contract.get("task") != TASK or contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_identity")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(row.get("status") != "blocked"
           for row in contract.get("release_gates", [])):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    assert_no_float(contract)
