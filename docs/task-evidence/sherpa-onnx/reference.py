# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict, stdlib-only readiness record for SDK-SHERPA-ONNX.

This module never imports, loads, executes, copies or downloads sherpa-onnx,
ONNX Runtime, a model, tokenizer, audio, a corpus or a network client. It pins
the research census and the exact bytes that happen to exist in a mutable
scratch area, proves that runnable source identity and per-model rights are
absent, validates a caller-supplied asset manifest without acting on it, and
records a DEFER conclusion with exact blockers and reopen conditions. Nothing
here qualifies a model or changes the installed SDK surface.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
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

TASK = "SDK-SHERPA-ONNX"
COMPONENT_ID = "sherpa-onnx"
TASK_TITLE = "sherpa-onnx"
CONTRACT_ID = "audio-sdk/sherpa-onnx/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
MANIFEST_SCHEMA_ID = "audio-sdk/sherpa-onnx/caller-asset-manifest/0.1"
BASE_COMMIT = "f93d25f3d455a4278030d1bf0a3338dc6f8b95fe"
BRANCH = "swarm/SDK-SHERPA-ONNX"
REVIEWER = "reviewer-SHERPA-ONNX"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
DECISION = "DEFER"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
REQUIRED_INTERPRETER = "3.12.16"
TASK_PREFIX = "docs/task-evidence/sherpa-onnx/"
WRITE_SCOPE = (
    "SDK provider, tool or evidence directory for sherpa-onnx and its own "
    "fixtures")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "repository", "mode", "depends_on",
                    "component", "evidence")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "source/output mapping, duration, pitch, transient audibility",
    "1×, rate changes",
    "unfamiliar speech, music, silence, rebuffer, drift and the final partial window",
    "Keep pause or filler decisions tied to source timestamps",
)

MODEL_PREFIX = (
    "cpp-library/pipeline-validation/playback-speed/models/"
    "sherpa-onnx-whisper-tiny.en")
VENV_PREFIX = (
    "cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/"
    "site-packages")
MODEL_TREE_SHA256 = (
    "fae72e5493c2c9d09e1f2725332ba278952ba2489923fe695e040ecd6ee08da5")
MODEL_FILE_COUNT = 9
MODEL_TREE_BYTES = 256603197
MODEL_FILE_BYTES = {
    "test_wavs/0.wav": 212044,
    "test_wavs/1.wav": 534924,
    "test_wavs/8k.wav": 77244,
    "test_wavs/trans.txt": 449,
    "tiny.en-decoder.int8.onnx": 89853865,
    "tiny.en-decoder.onnx": 114504265,
    "tiny.en-encoder.int8.onnx": 12937772,
    "tiny.en-encoder.onnx": 37647080,
    "tiny.en-tokens.txt": 835554,
}

# Read-only inputs. "source:" paths are audioml-workspace relative; the rest
# are SDK-worktree relative. The mutable board file is never hashed.
SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "cpp-library/pipeline-validation/playback-speed/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    MODEL_PREFIX + "/test_wavs/0.wav":
        "6bc58a4efdf20daac252b6b1502632601a71efe0308f6757dc1eda34891a7e4f",
    MODEL_PREFIX + "/test_wavs/1.wav":
        "5143a6ba93c4b274e2c4ac22deb75c2c48936c853f0519add1de828b6c79cc5a",
    MODEL_PREFIX + "/test_wavs/8k.wav":
        "f6f3c8b33e2534cdc154fe773ad2750f1f6a2ca5096179cdf037ae782456613e",
    MODEL_PREFIX + "/test_wavs/trans.txt":
        "b9ac44e7b794abb1a2d5faf0005e98a665971e7ac2ed15435832cc34edaa9100",
    MODEL_PREFIX + "/tiny.en-decoder.int8.onnx":
        "06c0e6ff6348d427e51839219d1c886c18cfdf411e629e33f5e1679bff9c1527",
    MODEL_PREFIX + "/tiny.en-decoder.onnx":
        "54d5a5fd2a757175aeb70a837a8404fc9c31b659610724694f5a0e2c51715f94",
    MODEL_PREFIX + "/tiny.en-encoder.int8.onnx":
        "0ce578b827c94a961aacb8fa14b02f096504b337e5c94be37c36238cbe3e8bc6",
    MODEL_PREFIX + "/tiny.en-encoder.onnx":
        "dc7de696432d97a3d64387800b230ac69d18e5e4efea0eec0613209dd8b7b0c9",
    MODEL_PREFIX + "/tiny.en-tokens.txt":
        "306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930",
    VENV_PREFIX + "/sherpa_onnx-2.0.1.dist-info/METADATA":
        "7f0a256489f0705f53f93ec9e85381ba05d7993625198e73afefc506a38cd97d",
    VENV_PREFIX + "/sherpa_onnx-2.0.1.dist-info/RECORD":
        "4c2fda5d01068e258a034b42c65f7cb1b5c68c894c7e0d7d5d238772abbc6479",
    VENV_PREFIX + "/sherpa_onnx-2.0.1.dist-info/WHEEL":
        "632a756fb02f4b7e2e52739240510251e3a147bd72a1e0f3a139f8395c193af8",
    VENV_PREFIX + "/sherpa_onnx-2.0.1.dist-info/licenses/LICENSE":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    VENV_PREFIX + "/sherpa_onnx_core-2.0.1.dist-info/METADATA":
        "f1af234dcfeca76f7ab4e16bdc903311e76069419b8b67c1806a7bf149d8945d",
    VENV_PREFIX + "/sherpa_onnx/__init__.py":
        "f99e43cc249dbfef58acaa02348892984e4c7dfa07923d9144bec5b51639d8ef",
    VENV_PREFIX + "/sherpa_onnx/online_recognizer.py":
        "a80620a5eb35e06a190584c2c643e5210bff672410283e5a8f106655c1519c9e",
}

BOUNDARY_PINS: dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
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
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/asr-word-timestamps/README.md":
        "30915db04b0229d03729b8dd03bac8e0eb88ad285781069de1607ff2c4559de4",
    "docs/task-evidence/asr-word-timestamps/report.json":
        "318bec24c9d388fa122e80974cfc6772b144f7f651e87d5e88ac0677975d437e",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/README.md":
        "1ccece1085e1d6e821891feffb0c19fc494227bfd5e8a656657ffd7081cf959c",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
    "docs/task-evidence/whisper-tiny-en-mfa/README.md":
        "7c24422f782bf934d22e2a752e2be2ead2d184cfd8728452c7f7a5dd68f25c7f",
}

LOCAL_FILES = (
    "LICENSES.md",
    "README.md",
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
)
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights",
}

# Fixed absence probes only; no recursive walk. The present scratch bytes are
# handled by SOURCE_PINS, not by these probes.
WORKSPACE_PROBES = (
    "data/checkouts/sherpa-onnx",
    "data/checkouts/k2-fsa-sherpa-onnx",
    "data/checkouts/sherpa-onnx-whisper-tiny.en",
    "data/models/sherpa-onnx",
    "data/wheels/sherpa_onnx",
    "data/envs/sherpa-onnx",
    "research/sherpa-onnx",
    "reports/sherpa-onnx",
)
WORKTREE_PROBES = (
    "adapters/sherpa-onnx",
    "schemas/providers/sherpa-onnx",
    "third_party/sherpa-onnx",
    "third_party/sherpa",
    "build/check-env/lib/python3.12/site-packages/sherpa_onnx",
)
HOME_PROBES = (
    "~/.cache/huggingface/hub/models--k2-fsa--sherpa-onnx-whisper-tiny.en",
    "~/.pyenv/versions/3.12.16/lib/python3.12/site-packages/sherpa_onnx",
)

NON_CLAIMS = [
    "No sherpa-onnx source checkout at an immutable revision, ONNX Runtime "
    "archive, wheel/sdist archive, lockfile or clean-room offline load is "
    "present, imported, loaded or executed.",
    "No model, tokenizer, audio sample, transcript, timestamp, WER or speech "
    "rate is inferred, decoded, scored or reported.",
    "The nine pinned Whisper tiny.en files are provenance bytes only; their "
    "test wavs are never read as audio and no model output exists.",
    "No installed Python 3.12 environment imports the Python 3.11 scratch "
    "runtime; the wheel metadata only pins what is present.",
    "No streaming capability, token-timestamp capability, content delay, "
    "availability, device timing, memory or deadline result is claimed.",
    "No Rate profile requirement is satisfied; all eight rows stay blocked "
    "and no synthetic control or manifest case opens a gate.",
    "No provider, adapter, descriptor, registry, default, public header, ABI, "
    "shared CMake, CI workflow, installed-v0 behavior, board or handoff is "
    "changed.",
    "No download, network access, listening, benchmark or release claim is "
    "made; DEFER remains in force.",
]

HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")
REV_RE = re.compile(r"[0-9a-f]{40}\Z")
DECIMAL_RE = re.compile(r"(?:0|-?[1-9][0-9]*)\Z")
SHA = hashlib.sha256


def sha256_file(path: Path) -> str:
    digest = SHA()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(root: Path) -> tuple[str, int, int]:
    rows: list[tuple[str, str, int]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rows.append((path.relative_to(root).as_posix(), sha256_file(path),
                     path.stat().st_size))
    digest = SHA()
    for relative, file_sha, size in rows:
        digest.update((relative + "\0" + file_sha + "\0" + str(size)
                       + "\n").encode("utf-8"))
    return digest.hexdigest(), len(rows), sum(size for _, _, size in rows)


def canonical_text(document: dict) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: dict) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: dict) -> str:
    return SHA(canonical_bytes(document)).hexdigest()


def _no_floats(value: Any, path: str = "document") -> None:
    if isinstance(value, float):
        raise ValueError("float:" + path)
    if isinstance(value, dict):
        for key, item in value.items():
            _no_floats(item, path + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, path + "[" + str(index) + "]")


def assert_no_float(value: Any) -> None:
    _no_floats(value)


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, item in pairs:
        if key in result:
            raise ValueError("duplicate_key:" + key)
        result[key] = item
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json:" + token)


def read_strict_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"),
                       object_pairs_hook=_strict_pairs,
                       parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError("json_not_object")
    return value


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative, expected in sorted(pins.items()):
        actual = sha256_file(root / relative)
        if actual != expected:
            raise ValueError("pin_mismatch:" + relative)
        rows[relative] = {"sha256": expected, "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(board_path: Path, task: str = TASK) -> dict:
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in tasks if isinstance(row, dict)
               and row.get("id") == task]
    if len(matches) != 1:
        raise ValueError("board_row_count:" + task)
    return {field: copy.deepcopy(matches[0].get(field))
            for field in BOARD_ROW_FIELDS}


def linked_rows() -> list[dict]:
    document = read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    index = {row.get("id"): row for row in tasks if isinstance(row, dict)}
    rows: list[dict] = []
    for task_id in LINKED_ROW_IDS:
        row = index.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        rows.append({field: copy.deepcopy(row.get(field))
                     for field in BOARD_ROW_FIELDS})
    return rows


def linked_identity_block() -> dict:
    rows = linked_rows()
    return {
        "board_path": BOARD_TASK_ROW,
        "mutable_board_bytes_hashed": False,
        "projected_fields": list(BOARD_ROW_FIELDS),
        "rows": rows,
        "rows_sha256": object_digest({"rows": rows}),
    }


def profile_row_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if line.startswith("| " + PROFILE_LABEL + " |")]
    if len(lines) != 1:
        raise ValueError("profile_row_not_unique")
    for phrase in PROFILE_PHRASES:
        if phrase not in lines[0]:
            raise ValueError("profile_phrase_missing:" + phrase)
    return {
        "path": PROFILE_SOURCE_REL,
        "sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
        "row_count": 1,
        "phrases": list(PROFILE_PHRASES),
        "phrases_present": True,
    }


def workspace_probes() -> list[dict]:
    return [{"path": path, "present": (AUDIO_ROOT / path).exists()}
            for path in WORKSPACE_PROBES]


def worktree_probes() -> list[dict]:
    return [{"path": path, "present": (WORKTREE / path).exists()}
            for path in WORKTREE_PROBES]


def home_probes() -> list[dict]:
    return [{"path": path,
             "present": (Path(path).expanduser()).exists()}
            for path in HOME_PROBES]


def absence_summary() -> dict:
    workspace = workspace_probes()
    worktree = worktree_probes()
    home = home_probes()
    all_rows = workspace + worktree + home
    return {
        "workspace_probe_count": len(workspace),
        "worktree_probe_count": len(worktree),
        "home_probe_count": len(home),
        "probe_count": len(all_rows),
        "present_count": sum(1 for row in all_rows if row["present"]),
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


def absence_evidence() -> dict:
    summary = absence_summary()
    if (summary["present_count"] != 0
            or summary["all_probes_absent"] is not True):
        raise ValueError("absence_probe_present")
    return {
        "workspace_probes": workspace_probes(),
        "worktree_probes": worktree_probes(),
        "home_probes": home_probes(),
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# README digest tables
# ---------------------------------------------------------------------------

def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), start=1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError("malformed_pin_line:" + str(number))
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:")
                or path.startswith(TASK_PREFIX)):
            raise ValueError("unknown_pin_prefix:" + str(number))
        if path in seen:
            raise ValueError("duplicate_pin:" + str(number))
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in _local_manifest_paths()
                      if name not in ARTIFACT_TABLE_EXCLUDED},
    }


def _local_manifest_paths() -> list[str]:
    return sorted(LOCAL_FILES)


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
            if HEX64.fullmatch(digest) is None:
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
            raise ValueError("readme_key_mismatch:" + section)
        for key, digest in parsed[section]:
            if section == "source":
                path = AUDIO_ROOT / key[len("source:"):]
            elif section == "boundary":
                path = WORKTREE / key[len("sdk:"):]
            else:
                path = HERE / key
            if not path.is_file() or sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
            line = ("| `" + key + "` | `" + digest + "` | "
                    + str(path.stat().st_size) + " |"
                    if section == "artifacts"
                    else "| `" + key + "` | `" + digest + "` |")
            if section == "artifacts" and line not in text:
                raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = ["| `source:" + name + "` | `" + digest + "` |"
                for name, digest in sorted(SOURCE_PINS.items())]
    elif section == "boundary":
        rows = ["| `sdk:" + name + "` | `" + digest + "` |"
                for name, digest in sorted(BOUNDARY_PINS.items())]
    elif section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in _local_manifest_paths():
            if name in ARTIFACT_TABLE_EXCLUDED:
                continue
            path = HERE / name
            rows.append("| `" + name + "` | `" + sha256_file(path)
                        + "` | " + str(path.stat().st_size) + " |")
    else:
        raise ValueError("unknown_readme_section:" + section)
    return "\n".join(rows)


def update_readme_table(text: str, section: str) -> str:
    block = render_digest_table(section)
    start, end = README_MARKERS[section]
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return (text[:start_index] + start + "\n" + block + "\n" + end
            + text[end_index:])


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Caller-supplied asset manifest: structural validation only
# ---------------------------------------------------------------------------

ASSET_FIELDS = ("asset_id", "sha256", "byte_count", "storage",
                "rights_reference")
MANIFEST_FIELDS = (
    "schema_id", "task_id", "source", "runtime", "assets", "model",
    "controls", "rights", "claims_qualified")
SOURCE_FIELDS = ("repository", "revision", "license_text_sha256",
                 "notice_sha256", "third_party_notice_sha256")
RUNTIME_FIELDS = ("package", "version", "archive_sha256", "wheel_sha256",
                  "lock_sha256", "install_root", "offline_trace_sha256",
                  "interpreter")
MODEL_FIELDS = ("model_card_sha256", "license_id", "commercial_use",
                "output_use", "streaming", "token_timestamps_verified",
                "sample_rate_hz", "channels", "sample_format",
                "frame_samples", "native_hop_samples",
                "buffering_delay_samples", "max_drain_calls",
                "source_timestamped")
CONTROL_FIELDS = ("identity", "silence", "adverse", "baseline",
                  "nonfinite_scan")
RIGHTS_FIELDS = ("consent", "corpus_review", "output_use",
                 "redistribution")
MAX_ASSETS = 16
MAX_TOTAL_BYTES = 512 * 1024 * 1024
ALLOWED_LICENSES = ("Apache-2.0", "MIT", "BSD-3-Clause")


def _object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("not_object:" + path)
    return value


def _exact_keys(value: Any, expected: Iterable[str], path: str) -> dict:
    obj = _object(value, path)
    if set(obj) != set(expected):
        raise ValueError("key_set:" + path)
    return obj


def _text(value: Any, path: str, pattern: re.Pattern | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("not_text:" + path)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ValueError("text_pattern:" + path)
    return value


def _sha(value: Any, path: str) -> str:
    return _text(value, path, HEX64)


def _integer(value: Any, path: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("not_integer:" + path)
    if value < low or value > high:
        raise ValueError("integer_range:" + path)
    return value


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError("not_boolean:" + path)
    return value


def _relative_path(value: Any, path: str) -> str:
    text = _text(value, path)
    if text.startswith("/") or text.startswith("~") or "\\" in text:
        raise ValueError("absolute_path:" + path)
    parts = text.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("unsafe_path:" + path)
    return text


def validate_manifest(manifest: Any) -> dict:
    """Validate shape and bounds; never load an asset or invoke a runtime."""
    top = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if _text(top["schema_id"], "schema_id") != MANIFEST_SCHEMA_ID:
        raise ValueError("schema_id")
    if _text(top["task_id"], "task_id") != TASK:
        raise ValueError("task_id")
    source = _exact_keys(top["source"], SOURCE_FIELDS, "source")
    if _text(source["repository"], "source.repository") != \
            "https://github.com/k2-fsa/sherpa-onnx":
        raise ValueError("repository")
    _text(source["revision"], "source.revision", REV_RE)
    _sha(source["license_text_sha256"], "source.license_text_sha256")
    _sha(source["notice_sha256"], "source.notice_sha256")
    _sha(source["third_party_notice_sha256"],
         "source.third_party_notice_sha256")

    runtime = _exact_keys(top["runtime"], RUNTIME_FIELDS, "runtime")
    if _text(runtime["package"], "runtime.package") != "sherpa_onnx":
        raise ValueError("runtime_package")
    _text(runtime["version"], "runtime.version",
          re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\Z"))
    _sha(runtime["archive_sha256"], "runtime.archive_sha256")
    _sha(runtime["wheel_sha256"], "runtime.wheel_sha256")
    _sha(runtime["lock_sha256"], "runtime.lock_sha256")
    _relative_path(runtime["install_root"], "runtime.install_root")
    _sha(runtime["offline_trace_sha256"], "runtime.offline_trace_sha256")
    if _text(runtime["interpreter"], "runtime.interpreter") != \
            REQUIRED_INTERPRETER:
        raise ValueError("runtime_interpreter")

    assets = top["assets"]
    if not isinstance(assets, list) or not 1 <= len(assets) <= MAX_ASSETS:
        raise ValueError("asset_count")
    ids: set[str] = set()
    hashes: set[str] = set()
    total = 0
    for index, raw in enumerate(assets):
        path = "assets[" + str(index) + "]"
        asset = _exact_keys(raw, ASSET_FIELDS, path)
        asset_id = _text(asset["asset_id"], path + ".asset_id", ID_RE)
        digest = _sha(asset["sha256"], path + ".sha256")
        size = _integer(asset["byte_count"], path + ".byte_count", 1,
                        MAX_TOTAL_BYTES)
        if _text(asset["storage"], path + ".storage") != "external":
            raise ValueError("asset_storage:" + path)
        _relative_path(asset["rights_reference"], path + ".rights_reference")
        if asset_id in ids or digest in hashes:
            raise ValueError("asset_duplicate:" + path)
        ids.add(asset_id)
        hashes.add(digest)
        total += size
    if total > MAX_TOTAL_BYTES:
        raise ValueError("asset_total_bytes")

    model = _exact_keys(top["model"], MODEL_FIELDS, "model")
    _sha(model["model_card_sha256"], "model.model_card_sha256")
    if _text(model["license_id"], "model.license_id") not in ALLOWED_LICENSES:
        raise ValueError("model_license")
    for flag in ("commercial_use", "output_use", "streaming",
                 "token_timestamps_verified", "source_timestamped"):
        if _boolean(model[flag], "model." + flag) is not True:
            raise ValueError("model_flag:" + flag)
    if _integer(model["sample_rate_hz"], "model.sample_rate_hz", 16000,
                16000) != 16000:
        raise ValueError("sample_rate")
    if _integer(model["channels"], "model.channels", 1, 1) != 1:
        raise ValueError("channels")
    if _text(model["sample_format"], "model.sample_format") != "f32":
        raise ValueError("sample_format")
    if _integer(model["frame_samples"], "model.frame_samples", 160, 160) != 160:
        raise ValueError("frame_samples")
    if _integer(model["native_hop_samples"], "model.native_hop_samples", 160,
                160) != 160:
        raise ValueError("native_hop_samples")
    _integer(model["buffering_delay_samples"], "model.buffering_delay_samples",
             0, 16000)
    _integer(model["max_drain_calls"], "model.max_drain_calls", 1, 1024)

    controls = _exact_keys(top["controls"], CONTROL_FIELDS, "controls")
    for name in CONTROL_FIELDS:
        if _boolean(controls[name], "controls." + name) is not True:
            raise ValueError("control:" + name)
    rights = _exact_keys(top["rights"], RIGHTS_FIELDS, "rights")
    for name in RIGHTS_FIELDS:
        if _boolean(rights[name], "rights." + name) is not True:
            raise ValueError("right:" + name)
    if _boolean(top["claims_qualified"], "claims_qualified") is not False:
        raise ValueError("claims_qualified")
    return copy.deepcopy(top)


def _synthetic_digest(label: str) -> str:
    return SHA(("synthetic:" + label).encode("utf-8")).hexdigest()


def control_manifest() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "task_id": TASK,
        "source": {
            "repository": "https://github.com/k2-fsa/sherpa-onnx",
            "revision": "0" * 40,
            "license_text_sha256": _synthetic_digest("source-license"),
            "notice_sha256": _synthetic_digest("source-notice"),
            "third_party_notice_sha256": _synthetic_digest("third-party"),
        },
        "runtime": {
            "package": "sherpa_onnx",
            "version": "2.0.1",
            "archive_sha256": _synthetic_digest("archive"),
            "wheel_sha256": _synthetic_digest("wheel"),
            "lock_sha256": _synthetic_digest("lock"),
            "install_root": "fixtures/offline-runtime",
            "offline_trace_sha256": _synthetic_digest("offline-trace"),
            "interpreter": REQUIRED_INTERPRETER,
        },
        "assets": [
            {
                "asset_id": "synthetic.model.int8",
                "sha256": _synthetic_digest("model-int8"),
                "byte_count": 1024,
                "storage": "external",
                "rights_reference": "fixtures/model-rights.json",
            },
            {
                "asset_id": "synthetic.tokens",
                "sha256": _synthetic_digest("tokens"),
                "byte_count": 512,
                "storage": "external",
                "rights_reference": "fixtures/tokens-rights.json",
            },
        ],
        "model": {
            "model_card_sha256": _synthetic_digest("model-card"),
            "license_id": "Apache-2.0",
            "commercial_use": True,
            "output_use": True,
            "streaming": True,
            "token_timestamps_verified": True,
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "native_hop_samples": 160,
            "buffering_delay_samples": 160,
            "max_drain_calls": 64,
            "source_timestamped": True,
        },
        "controls": {name: True for name in CONTROL_FIELDS},
        "rights": {name: True for name in RIGHTS_FIELDS},
        "claims_qualified": False,
    }


def _mutate(base: dict, path: tuple[str, ...], value: Any) -> dict:
    result = copy.deepcopy(base)
    cursor = result
    for key in path[:-1]:
        cursor = cursor[key]
    if value is _DELETE:
        del cursor[path[-1]]
    else:
        cursor[path[-1]] = value
    return result


_DELETE = object()


def admission_cases() -> dict:
    base = control_manifest()
    validate_manifest(base)
    mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("missing_schema_id", ("schema_id",), _DELETE),
        ("wrong_schema_id", ("schema_id",), "audio-sdk/other/0.1"),
        ("missing_task_id", ("task_id",), _DELETE),
        ("wrong_task_id", ("task_id",), "SDK-VOSK"),
        ("short_revision", ("source", "revision"), "0" * 39),
        ("upper_revision", ("source", "revision"), "A" * 40),
        ("wrong_repository", ("source", "repository"),
         "https://example.invalid/sherpa"),
        ("missing_notice", ("source", "notice_sha256"), _DELETE),
        ("uppercase_digest", ("runtime", "wheel_sha256"), "A" * 64),
        ("wrong_interpreter", ("runtime", "interpreter"), "3.11.5"),
        ("absolute_install_root", ("runtime", "install_root"), "/tmp/runtime"),
        ("traversal_install_root", ("runtime", "install_root"),
         "../runtime"),
        ("empty_install_root", ("runtime", "install_root"), ""),
        ("missing_lock", ("runtime", "lock_sha256"), _DELETE),
        ("nonfinite_digest", ("runtime", "lock_sha256"), "NaN"),
        ("stereo", ("model", "channels"), 2),
        ("wrong_rate", ("model", "sample_rate_hz"), 48000),
        ("wrong_format", ("model", "sample_format"), "s16"),
        ("wrong_frame", ("model", "frame_samples"), 512),
        ("wrong_hop", ("model", "native_hop_samples"), 80),
        ("delay_too_large", ("model", "buffering_delay_samples"), 16001),
        ("drain_too_large", ("model", "max_drain_calls"), 1025),
        ("negative_delay", ("model", "buffering_delay_samples"), -1),
        ("bool_as_integer", ("model", "max_drain_calls"), True),
        ("timestamp_unproven", ("model", "token_timestamps_verified"), False),
        ("batch_only", ("model", "streaming"), False),
        ("wall_time_events", ("model", "source_timestamped"), False),
        ("unknown_license", ("model", "license_id"), "Proprietary"),
        ("missing_card", ("model", "model_card_sha256"), _DELETE),
        ("no_consent", ("rights", "consent"), False),
        ("no_output_rights", ("rights", "output_use"), False),
        ("rights_as_integer", ("rights", "redistribution"), 1),
        ("missing_control", ("controls", "baseline"), _DELETE),
        ("false_control", ("controls", "silence"), False),
        ("claims_qualified", ("claims_qualified",), True),
        ("asset_zero_bytes", ("assets", 0, "byte_count"), 0),
        ("asset_negative_bytes", ("assets", 0, "byte_count"), -1),
        ("asset_duplicate_id", ("assets", 1, "asset_id"),
         "synthetic.model.int8"),
        ("asset_embedded", ("assets", 0, "storage"), "embedded"),
        ("asset_absolute_rights", ("assets", 0, "rights_reference"),
         "/rights.json"),
        ("asset_total_too_large", ("assets", 0, "byte_count"),
         MAX_TOTAL_BYTES),
        ("asset_missing_rights", ("assets", 0, "rights_reference"), _DELETE),
        ("nonfinite_outcome", ("model", "buffering_delay_samples"),
         float("inf")),
    ]
    cases: list[dict] = [{
        "id": "AC-00",
        "class": "synthetic_schema_control_not_evidence",
        "status": "accepted",
        "code": "schema_shape_valid",
        "state_unchanged": True,
        "runtime_invoked": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "network_used": False,
        "qualifies": False,
    }]
    for index, (name, path, value) in enumerate(mutations, start=1):
        candidate = _mutate(base, path, value)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            code = str(error)
        else:
            raise AssertionError("admission_case_accepted:" + name)
        cases.append({
            "id": "AC-%02d" % index,
            "class": "fail_closed_negative_control",
            "status": "rejected",
            "code": code,
            "state_unchanged": True,
            "runtime_invoked": False,
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
            "qualifies": False,
        })
    rejected = sum(1 for row in cases if row["status"] == "rejected")
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "controls": list(CONTROL_FIELDS),
        "rights": list(RIGHTS_FIELDS),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "accepted_schema_controls": 1,
            "rejected_count": rejected,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
    }


def geometry_control() -> dict:
    """Exact integer frame arithmetic; no audio, delay estimate or model."""
    cases: list[dict] = []
    for length in range(1, 160):
        cases.append({
            "accepted_valid_samples": length,
            "padded_frame_samples": 160,
            "final_padding_samples": 160 - length,
            "valid_offset": 0,
            "valid_count": length,
            "conserved": length == min(length, 160),
        })
    cases.append({
        "accepted_valid_samples": 320,
        "padded_frame_samples": "2x160",
        "final_padding_samples": 0,
        "valid_offset": 0,
        "valid_count": 320,
        "conserved": True,
    })
    if not all(row["conserved"] for row in cases):
        raise AssertionError("geometry_control_not_conserved")
    return {
        "class": "synthetic_integer_geometry_control_not_evidence",
        "assumed_buffering_delay_samples": 0,
        "sample_format": "f32",
        "sample_rate_hz": 16000,
        "frame_samples": 160,
        "nanoseconds_per_sample": 62500,
        "nanoseconds_per_frame": 10000000,
        "cases": cases,
        "case_count": len(cases),
        "qualifies": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "hop_samples": 160,
        "nanoseconds_per_sample": 62500,
        "preserved": True,
        "sherpa_onnx_mapping_present": False,
        "streaming_model_path_present": False,
        "installed_wheel_tests_in_scripts_ci": True,
        "evidence": [
            "CONTRACTS.md pin (16 kHz/1/160, exact 160 process input)",
            "api/include/audio_sdk/provider_v0.h pin",
            "api/include/audio_sdk/session_v0.h pin",
            "scripts/ci.py pin (installed-python-wheel check)",
        ],
    }


def task_geometry() -> dict:
    return {
        "reported_task": "Rate and content gate: streaming ASR token "
                         "timestamps / VAD / keyword spotting / tagging",
        "sample_rate_hz": None,
        "channels": None,
        "sample_format": None,
        "frame_samples": None,
        "native_hop_samples": None,
        "buffering_delay_samples": None,
        "right_context_samples": None,
        "endpoint_policy": None,
        "decoding_state": None,
        "token_timestamp_capability_verified": False,
        "exact_geometry_verified": False,
        "installed_v0_mapping_present": False,
    }


def upstream_record() -> dict:
    return {
        "repository": "https://github.com/k2-fsa/sherpa-onnx",
        "census_line": 877,
        "reported_capabilities": [
            "streaming ASR", "VAD", "keyword spotting", "audio tagging",
            "token timestamps", "endpointing",
        ],
        "code_license_reported": "Apache-2.0",
        "immutable_revision": None,
        "source_files_present": False,
        "license_identity_verified": False,
        "notice_bundle_verified": False,
        "no_local_build_or_benchmark_reported": True,
        "timestamps_model_dependent": True,
        "per_model_license_caution": "Each model has its own licence; verify "
                                     "the card",
        "streaming_audit_note": "earlier VAD/ASR audit recorded sherpa-onnx "
                                "absent in the checked runtime",
    }


def present_assets() -> dict:
    digest, count, size = tree_digest(AUDIO_ROOT / MODEL_PREFIX)
    if (digest != MODEL_TREE_SHA256 or count != MODEL_FILE_COUNT
            or size != MODEL_TREE_BYTES):
        raise ValueError("present_model_tree_drift")
    files = [{
        "path": relative,
        "sha256": SOURCE_PINS[MODEL_PREFIX + "/" + relative],
        "byte_count": MODEL_FILE_BYTES[relative],
        "read_as_audio": False,
    } for relative in sorted(MODEL_FILE_BYTES)]
    runtime_version = "2.0.1"
    return {
        "model_tree": {
            "prefix": MODEL_PREFIX,
            "tree_sha256": digest,
            "file_count": count,
            "byte_count": size,
            "files": files,
            "license_file_present": False,
            "model_card_present": False,
            "official_archive_identity_present": False,
            "output_use_decision_present": False,
            "streaming_token_timestamp_model": False,
        },
        "runtime": {
            "package": "sherpa_onnx",
            "version": runtime_version,
            "core_package": "sherpa-onnx-core",
            "wheel_dist_info_license_text_present": True,
            "wheel_archive_present": False,
            "lockfile_present": False,
            "offline_load_trace_present": False,
            "source_revision_present": False,
            "third_party_notice_bundle_verified": False,
            "python311_scratch_only": True,
            "imported_or_executed": False,
        },
        "network_used": False,
        "audio_read": False,
    }


def evidence_inputs() -> list[dict]:
    rows: list[dict] = []
    for relative, digest in sorted(SOURCE_PINS.items()):
        if relative.startswith(MODEL_PREFIX + "/"):
            asset_class = "present_unlicensed_model_bytes"
        elif relative.startswith(VENV_PREFIX + "/"):
            asset_class = "present_wheel_metadata_not_provenance"
        else:
            asset_class = "research_or_plan_source"
        rows.append({
            "path": relative,
            "sha256": digest,
            "class": asset_class,
            "is_result": False,
            "qualifies": False,
        })
    return rows


REQUIRED_ARTIFACTS = [
    ("ART-01", "upstream_source_revision_license_and_notices"),
    ("ART-02", "wheel_or_sdist_archive_and_lockfile"),
    ("ART-03", "clean_room_offline_load_and_deterministic_runtime"),
    ("ART-04", "streaming_model_card_license_and_output_use_decision"),
    ("ART-05", "token_timestamp_capability_at_installed_geometry"),
    ("ART-06", "rights_cleared_matched_cohort_and_reference"),
    ("ART-07", "rate_profile_result_set_with_controls"),
    ("ART-08", "target_device_timing_resources_and_deadlines"),
    ("ART-09", "independent_scorer_and_failure_controls"),
    ("ART-10", "opt_in_off_by_default_provider_intake_review"),
]


def required_artifacts() -> list[dict]:
    return [{
        "id": artifact_id,
        "name": name,
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "qualifies": False,
    } for artifact_id, name in REQUIRED_ARTIFACTS]


EXACT_BLOCKERS = [
    ("BLK-01", "ART-01",
     "Exact k2-fsa/sherpa-onnx source at an immutable 40-hex revision with "
     "reviewed Apache-2.0 license, notice and bundled-third-party attribution."),
    ("BLK-02", "ART-02",
     "Pinned wheel/sdist archives, hashes, lockfile and an isolated offline "
     "install for the exact 2.0.1 runtime including sherpa-onnx-core."),
    ("BLK-03", "ART-03",
     "A deterministic clean-room load trace, thread policy and "
     "availability/first-output evidence at 16 kHz mono f32 160-sample frames."),
    ("BLK-04", "ART-04",
     "An exact streaming model with model card, per-model license, commercial "
     "and output-use rights; the present offline Whisper tiny.en tree has none."),
    ("BLK-05", "ART-05",
     "Proof that the chosen streaming model emits source-timestamped tokens at "
     "the installed geometry with bounded right-context and endpoint/reset "
     "behavior; the census says timestamps are model-dependent."),
    ("BLK-06", "ART-06",
     "A consented, rights-cleared matched cohort with independent references, "
     "controls, Rate-profile results, device timing and separate OFF-by-default "
     "provider intake with exact-head review."),
]


def exact_blockers() -> list[dict]:
    gate_ids = ["RG-%02d" % number for number in range(1, 9)]
    artifact_ids = {row[0] for row in REQUIRED_ARTIFACTS}
    rows: list[dict] = []
    for index, (blocker_id, artifact_id, action) in enumerate(EXACT_BLOCKERS):
        rows.append({
            "id": blocker_id,
            "status": "open",
            "qualifies": False,
            "artifact_id": artifact_id,
            "required_action": action,
            "linked_gates": gate_ids[index:index + 2],
            "reopen_condition": action + " Supply the artifact with verified "
                                "identity and rights before reconsideration.",
        })
    if not all(row["artifact_id"] in artifact_ids for row in rows):
        raise AssertionError("blocker_artifact_link")
    return rows


GATE_TITLES = (
    "source_revision_and_license_provenance",
    "pinned_runtime_archive_lock_and_offline_load",
    "streaming_model_identity_card_and_output_rights",
    "token_timestamps_and_installed_geometry_proof",
    "rights_cleared_cohort_and_independent_reference",
    "rate_profile_source_mapping_and_controls",
    "availability_device_timing_and_failure_controls",
    "provider_intake_off_default_and_release",
)


def release_gates() -> list[dict]:
    rows: list[dict] = []
    for index, title in enumerate(GATE_TITLES, start=1):
        rows.append({
            "id": "RG-%02d" % index,
            "title": title,
            "status": "blocked",
            "qualifies": False,
            "linked_row": TASK,
            "reopen_condition": "Supply the exact " + title.replace("_", " ")
                                + " evidence on caller-supplied, "
                                "rights-cleared assets with independent review.",
        })
    return rows


RATE_REQUIREMENTS = (
    "source_output_mapping_and_duration",
    "pitch_and_transient_audibility",
    "playback_buffering_and_drift",
    "identity_1x_control",
    "rate_changes",
    "unfamiliar_speech_music_and_silence",
    "rebuffer_and_final_partial_window",
    "pause_filler_tied_to_source_timestamps",
)


def rate_profile() -> dict:
    return {
        "profile": PROFILE_LABEL,
        "source_check": profile_row_check(),
        "requirement_rows": [{
            "id": "RP-%02d" % index,
            "name": name,
            "status": "blocked",
            "qualifies": False,
        } for index, name in enumerate(RATE_REQUIREMENTS, start=1)],
        "row_summary": {
            "requirement_count": len(RATE_REQUIREMENTS),
            "satisfied_count": 0,
            "real_result_count": 0,
            "profile_satisfied": False,
        },
    }


def disposition_block() -> dict:
    return {
        "task_mode": MODE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "source_present": False,
        "runtime_archive_present": False,
        "model_rights_verified": False,
        "streaming_result_present": False,
        "result_promoted": False,
        "summary": "sherpa-onnx is a considered Rate/content candidate. Exact "
                   "runnable source identity, wheel provenance, per-model "
                   "rights and a streaming token-timestamp run at installed "
                   "16 kHz mono f32 160-sample geometry are absent.",
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "network_access": False,
        "weights_downloaded": False,
        "weights_vendored": False,
        "source_vendored": False,
        "runtime_invoked": False,
        "model_executed": False,
        "real_audio": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_default": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "peer_result_inherited": False,
    }


def exact_scope_block() -> dict:
    return {
        "write_scope": WRITE_SCOPE,
        "task_prefix": TASK_PREFIX,
        "only_task_directory_written": True,
        "provider_files_changed": False,
        "adapter_files_changed": False,
        "descriptor_or_registry_changed": False,
        "contracts_header_changed": False,
        "cmake_or_ci_changed": False,
        "board_or_handoff_changed": False,
        "default_selection_changed": False,
        "weights_or_audio_committed": False,
    }


def boundary_block() -> dict:
    return {
        "provider_registration": False,
        "adapter_json_added": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "native_engine_built": False,
        "runtime_imported": False,
        "weights_vendored": False,
        "audio_added": False,
        "corpus_added": False,
    }


def rights_gap() -> list[dict]:
    return [
        {"id": "RGAP-01", "name": "upstream_code_license_and_notices",
         "status": "unreviewed", "qualifies": False},
        {"id": "RGAP-02", "name": "per_model_license_and_model_card",
         "status": "absent", "qualifies": False},
        {"id": "RGAP-03", "name": "commercial_and_output_use_decision",
         "status": "absent", "qualifies": False},
        {"id": "RGAP-04", "name": "consented_matched_cohort",
         "status": "absent", "qualifies": False},
        {"id": "RGAP-05", "name": "independent_reference_and_scorer",
         "status": "absent", "qualifies": False},
    ]


def qualification() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "all_release_gates_blocked": True,
        "real_result_present": False,
        "source_present": False,
        "exact_source_identity": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "weights_present": False,
        "weights_identified": False,
        "asset_registry_entry_present": False,
        "rights_cleared_cohort": False,
        "streaming_geometry_verified": False,
        "token_timestamps_verified": False,
        "implementation_present": False,
        "rate_profile_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "peer_result_inherited": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "write_scope": WRITE_SCOPE,
        "disposition": disposition_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "boundary": boundary_block(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "evidence_inputs": evidence_inputs(),
        "linked_row_identity": linked_identity_block(),
        "rate_profile": rate_profile(),
        "task_geometry": task_geometry(),
        "upstream_record": upstream_record(),
        "present_assets": present_assets(),
        "public_v0_geometry": public_v0_geometry(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "rights_gap": rights_gap(),
        "caller_manifest": {
            "schema_id": MANIFEST_SCHEMA_ID,
            "asset_storage": "external",
            "asset_count_max": MAX_ASSETS,
            "total_asset_bytes_max": MAX_TOTAL_BYTES,
            "accepted_without_execution": True,
            "qualifies": False,
        },
        "admission": admission_cases(),
        "geometry_control": geometry_control(),
        "qualification": qualification(),
        "non_claims": list(NON_CLAIMS),
    }


def validate_contract(contract: dict) -> None:
    expected = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise ValueError("contract_field:" + key)
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if len(contract.get("exact_blockers", [])) != 6:
        raise ValueError("contract_blocker_count")
    if len(contract.get("required_artifacts", [])) != 10:
        raise ValueError("contract_artifact_count")
    assert_no_float(contract)


def build_report() -> dict:
    contract = build_contract()
    validate_contract(contract)
    absence = absence_evidence()
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
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "contract_sha256": object_digest(contract),
        "disposition": contract["disposition"],
        "boundary": contract["boundary"],
        "scope": contract["scope"],
        "exact_scope": contract["exact_scope"],
        "rate_profile": contract["rate_profile"],
        "task_geometry": contract["task_geometry"],
        "upstream_record": contract["upstream_record"],
        "present_assets": contract["present_assets"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rights_gap": contract["rights_gap"],
        "qualification": contract["qualification"],
        "admission": contract["admission"],
        "geometry_control": contract["geometry_control"],
        "non_claims": contract["non_claims"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "evidence_inputs": contract["evidence_inputs"],
        "linked_row_identity": contract["linked_row_identity"],
        "absence_evidence": absence,
    }


def canonical_report(document: dict) -> tuple[str, str]:
    text = canonical_text(document)
    return text, SHA(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Newest-merge-base branch-diff scope enforcement
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
    """Newest merge-base between HEAD and an available PR base ref."""
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
        elif best != base and _git(
                worktree, "merge-base", "--is-ancestor", best,
                base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base,
                  "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


def scope_error_codes(worktree: Path,
                      prefix: str = TASK_PREFIX) -> list[str]:
    """Fail-closed scope codes used by the verifier and regression tests."""
    base = scope_base(worktree)
    if base is None:
        return ["scope_base_unavailable"]
    try:
        paths = scope_changed_paths(worktree, base)
    except ValueError as error:
        return [str(error)]
    return ["base_out_of_scope_change:" + path
            for path in scope_violations(paths, prefix)]
