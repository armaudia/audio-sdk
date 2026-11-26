# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-SPIKING-FULLSUBNET.

Standard library only. The catalogued candidate is Spiking-FullSubNet: a
spiking-neural-network FullSubNet variant for low-power real-time denoising.
The pinned census names an official MIT repository reporting the Intel N-DNS
Challenge Track 1 winning solution with pretrained models and a validation set,
but no source snapshot, checkpoint byte, neuromorphic/runtime artifact,
licence-reviewed weight bundle, rights-cleared cohort or local result is
present anywhere probed.

This module pins the evidence that does exist, validates a fail-closed
caller-supplied asset declaration without resolving, importing, loading or
executing anything, and builds canonical DEFER bytes. It never runs a model,
enhances audio, synthesises a waveform, opens media, performs listening, times
a device or produces a benchmark result.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

TASK = "SDK-SPIKING-FULLSUBNET"
TASK_TITLE = "Spiking-FullSubNet"
COMPONENT_ID = "spiking-fullsubnet"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"
WRITE_SCOPE = "docs/task-evidence/spiking-fullsubnet/ only"
TASK_PREFIX = "docs/task-evidence/spiking-fullsubnet/"
CONTRACT_ID = "audio-sdk/spiking-fullsubnet-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/spiking-fullsubnet-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/spiking-fullsubnet-report/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/spiking-fullsubnet-caller-asset/0.1"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = "swarm/SDK-SPIKING-FULLSUBNET"
OWNER = "agent-SPIKING-FULLSUBNET"
REVIEWER = "reviewer-SPIKING-FULLSUBNET"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
SOURCE_REPOSITORY = "https://github.com/haoxiangsnr/spiking-fullsubnet"
CANDIDATE_FAMILY = "spiking_fullsubnet_snn_enhancement"
TASK_GEOMETRY_STATE = "unverified_spiking_fullsubnet_geometry_and_runtime"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PACKAGE = re.compile(r"^[A-Za-z0-9_.+-]+==[A-Za-z0-9_.+-]+$")
SAFE_BASENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
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
SDK_ROOT = WORKTREE

SOURCE_PINS = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

BOUNDARY_PINS = {
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
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
CENSUS_REL = "research/noise_suppression_candidate_census.md"
INVENTORY_MD_REL = "audio-benchmark-platform/plan/INVENTORY.md"
INVENTORY_JSON_REL = "audio-benchmark-platform/plan/INVENTORY.json"
CONTRACT_SOURCE_REL = "audio-benchmark-platform/audio-sdk/CONTRACTS.md"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PROFILE_PHRASES = (
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
)

EVIDENCE_SNIPPETS = (
    {
        "id": "SNP-01",
        "path": CENSUS_REL,
        "line": 35,
        "contains": (
            "Spiking-FullSubNet",
            "Spiking-neural-network FullSubNet for low-power real-time denoising",
            "Intel N-DNS Challenge Track 1",
            "pretrained models and a validation set",
            "released checkpoint's input domain, code revision, inference contract and licensing of its weights",
        ),
    },
    {
        "id": "SNP-02",
        "path": INVENTORY_MD_REL,
        "line": 213,
        "contains": ("Spiking-FullSubNet", TASK),
    },
    {
        "id": "SNP-03",
        "path": PROFILE_SOURCE_REL,
        "line": 16,
        "contains": PROFILE_PHRASES,
    },
    {
        "id": "SNP-04",
        "path": CONTRACT_SOURCE_REL,
        "line": 15,
        "contains": (
            "as_asset_v0",
            "The descriptor declares every external asset",
            "caller supplies exactly those assets",
            "Embedded assets are not supported by contract 0.1",
        ),
    },
)

LOCAL_FILES = (
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
)
EXPECTED_DIR_FILES = frozenset(LOCAL_FILES)
FORBIDDEN_SUFFIXES = frozenset((
    ".7z", ".a", ".bin", ".ckpt", ".dll", ".dylib", ".flac", ".gz", ".h5",
    ".mp3", ".npy", ".npz", ".o", ".ogg", ".onnx", ".pth", ".pt",
    ".safetensors", ".so", ".tar", ".tflite", ".tgz", ".wav", ".whl", ".zip",
))
SOURCE_ARTIFACT_FILES = tuple(
    name for name in LOCAL_FILES if name not in ("README.md", "SOURCES.sha256"))

# Fixed absence probes only; no recursive walk.
ABSENCE_PROBES = (
    {"kind": "source", "label": "official_repo_checkout", "path": "research/voice-enhancement-20261101/repos/spiking-fullsubnet"},
    {"kind": "source", "label": "official_repo_checkout_alt", "path": "research/voice-enhancement-20261101/repos/Spiking-FullSubNet"},
    {"kind": "source", "label": "source_tree", "path": "research/spiking-fullsubnet"},
    {"kind": "weights", "label": "weights_dir", "path": "research/voice-enhancement-20261101/models/spiking-fullsubnet"},
    {"kind": "weights", "label": "weights_dir_alt", "path": "research/models/spiking-fullsubnet"},
    {"kind": "weights", "label": "checkpoint_tar", "path": "research/voice-enhancement-20261101/models/spiking-fullsubnet/checkpoints.tar"},
    {"kind": "runtime", "label": "env_dir", "path": "research/voice-enhancement-20261101/envs/spiking-fullsubnet"},
    {"kind": "runtime", "label": "venv_dir", "path": "research/voice-enhancement-20261101/.venv-spiking-fullsubnet"},
    {"kind": "runtime", "label": "lock_file", "path": "research/voice-enhancement-20261101/locks/spiking-fullsubnet.lock"},
    {"kind": "home", "label": "home_cache", "path": "~/.cache/spiking-fullsubnet"},
    {"kind": "home", "label": "home_models", "path": "~/.local/share/spiking-fullsubnet"},
    {"kind": "home", "label": "home_venv", "path": "~/.venvs/spiking-fullsubnet"},
)

NON_CLAIMS = [
    "No Spiking-FullSubNet source copy, checkpoint, weight fragment, SNN runtime, neuromorphic runtime, corpus, clean reference, enhanced waveform or vendor result is present, loaded or executed.",
    "No model inference, audio read or write, listening, paired SI-SDR or STOI scoring, clean-speech preservation, peak, alignment, content-delay, first-output, device-timing or power measurement is performed.",
    "No real or synthetic waveform is scored; the admission control is a schema object only and is marked synthetic_schema_control.",
    "No Spiking-FullSubNet checkpoint identity, byte count, SHA-256, input domain, inference contract, parameter count or released-weight licence is recorded as verified local fact.",
    "No local DNS2020, VoiceBank, Intel N-DNS, FullSubNet, FullSubNet+, DiffSE, NASE or other peer result is inherited or pooled.",
    "No benchmark, quality, latency, resource, power, neuromorphic, streaming, provider or release claim is made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; absent artifacts are not fabricated, reconstructed, mirrored or substituted.",
]


# ---------------------------------------------------------------------------
# Canonical bytes and strict JSON.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


class _RejectDuplicate(dict):
    pass


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    seen: set[str] = set()
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError("duplicate_json_key:" + key)
        seen.add(key)
        out[key] = value
    return out


def _reject_constant(value: str) -> Any:
    raise ValueError("nonfinite_json:" + value)


def assert_no_float(value: Any, path: str = "$") -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, float):
        raise TypeError("float_value_not_allowed:" + path)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("non_string_key:" + path)
            assert_no_float(item, path + "." + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_no_float(item, path + "[" + str(index) + "]")


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
    return parse_strict_json_text(Path(path).read_bytes())


def strict_json_rejections() -> dict:
    texts = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_constant": '{"a":NaN}',
        "infinity_constant": '{"a":Infinity}',
        "negative_infinity_constant": '{"a":-Infinity}',
        "trailing_data": '{"a":1} trailing',
        "invalid_syntax": '{"a":}',
        "empty_text": "",
        "float_value": '{"a":1.5}',
        "root_array": '[1,2]',
        "nested_float": '{"a":{"b":2.25}}',
    }
    cases = []
    for name, text in texts.items():
        try:
            loads_strict(text)
            observed = "UNEXPECTED_ACCEPT"
        except (ValueError, TypeError):
            observed = "REJECTED"
        cases.append({"id": name, "observed": observed,
                      "rejected": observed == "REJECTED"})
    return {"case_count": len(cases), "cases": cases,
            "rejection_cases": sum(1 for c in cases if c["rejected"])}


# ---------------------------------------------------------------------------
# Stable board identity. Mutable board file is read, never pinned/gated.
# ---------------------------------------------------------------------------


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if missing:
        raise ValueError("board_row_missing_fields:" + ",".join(missing))
    component = row.get("component")
    if require_component:
        if component != COMPONENT_ID:
            raise ValueError("board_component_mismatch:" + str(component))
    elif component is not None and not isinstance(component, str):
        raise ValueError("board_component_not_string")
    depends_on = row["depends_on"]
    if not isinstance(depends_on, list) or any(
            not isinstance(item, str) for item in depends_on):
        raise ValueError("board_depends_on_not_string_list")
    return {
        "component": component,
        "depends_on": list(depends_on),
        "id": row["id"],
        "mode": row["mode"],
        "repository": row["repository"],
        "title": row["title"],
    }


def board_row_projection(path: Path | None = None) -> dict:
    board = Path(path) if path is not None else AUDIO_ROOT / BOARD_TASK_ROW
    document = json.loads(board.read_text(encoding="utf-8"))
    rows = document.get("tasks") if isinstance(document, dict) else document
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    for row in rows:
        if isinstance(row, dict) and row.get("id") == TASK:
            return _project(row, require_component=True)
    raise ValueError("board_row_not_found:" + TASK)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(board_row_projection() if projection is None else projection)


def linked_rows(path: Path | None = None) -> list[dict]:
    board = Path(path) if path is not None else AUDIO_ROOT / BOARD_TASK_ROW
    document = json.loads(board.read_text(encoding="utf-8"))
    rows = document.get("tasks") if isinstance(document, dict) else document
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    by_id = {row["id"]: row for row in rows
             if isinstance(row, dict) and isinstance(row.get("id"), str)}
    missing = [identifier for identifier in LINKED_ROW_IDS if identifier not in by_id]
    if missing:
        raise ValueError("board_rows_missing:" + ",".join(missing))
    out = []
    for identifier in LINKED_ROW_IDS:
        out.append(_project(by_id[identifier], require_component=(identifier == TASK)))
    return out


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(linked_rows() if rows is None else rows)


# ---------------------------------------------------------------------------
# Scope and merge-base gate.
# ---------------------------------------------------------------------------


def _git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *arguments],
                          capture_output=True, text=True, check=False)


def scope_base(worktree: Path, refs: tuple[str, ...] = ("origin/main", "main")) -> str | None:
    candidates: list[tuple[int, str]] = []
    for ref in refs:
        base = _git(worktree, "merge-base", "HEAD", ref)
        if base.returncode != 0:
            continue
        base_sha = base.stdout.strip()
        if not HEX40.match(base_sha):
            continue
        tip = _git(worktree, "rev-parse", "--verify", ref)
        if tip.returncode != 0:
            continue
        tip_sha = tip.stdout.strip()
        count = _git(worktree, "rev-list", "--count", base_sha + "..HEAD")
        if count.returncode != 0:
            continue
        try:
            distance = int(count.stdout.strip())
        except ValueError:
            continue
        candidates.append((distance, base_sha, tip_sha))
    if not candidates:
        return None
    # newest merge-base by minimal distance; tie-break on tip freshness by rev-list
    candidates.sort(key=lambda item: (item[0],))
    return candidates[0][1]


def scope_changed_paths(worktree: Path, base: str | None) -> list[str]:
    if base is None:
        return []
    result = _git(worktree, "diff", "--name-only", base + "..HEAD")
    if result.returncode != 0:
        raise RuntimeError("git_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: list[str]) -> list[str]:
    return sorted(path for path in paths if not path.startswith(TASK_PREFIX))


def scope_status(worktree: Path = WORKTREE) -> dict:
    base = scope_base(worktree)
    if base is None:
        return {
            "base": None,
            "base_out_of_scope_changes": [],
            "ok": False,
            "reason": "scope_base_unavailable",
        }
    paths = scope_changed_paths(worktree, base)
    violations = scope_violations(paths)
    return {
        "base": base,
        "base_out_of_scope_changes": ["base_out_of_scope_change:" + p for p in violations],
        "changed_paths": paths,
        "ok": not violations,
        "reason": "ok" if not violations else "base_out_of_scope_change",
    }


# ---------------------------------------------------------------------------
# Pinned source/boundary presence.
# ---------------------------------------------------------------------------


def pin_presence() -> dict[str, dict[str, Any]]:
    out = {}
    for rel, expected in SOURCE_PINS.items():
        path = AUDIO_ROOT / rel
        present = path.is_file()
        actual = sha256_file(path) if present else None
        out["source:" + rel] = {"expected": expected, "actual": actual, "present": present, "ok": present and actual == expected}
    for rel, expected in BOUNDARY_PINS.items():
        path = WORKTREE / rel
        present = path.is_file()
        actual = sha256_file(path) if present else None
        out["sdk:" + rel] = {"expected": expected, "actual": actual, "present": present, "ok": present and actual == expected}
    return out


def evidence_presence() -> dict:
    snippets = []
    for item in EVIDENCE_SNIPPETS:
        path = AUDIO_ROOT / item["path"]
        text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        line_text = ""
        if path.is_file():
            lines = text.splitlines()
            if 1 <= item["line"] <= len(lines):
                line_text = lines[item["line"] - 1]
        contains = {needle: (needle in text) for needle in item["contains"]}
        snippets.append({
            "id": item["id"],
            "path": item["path"],
            "line": item["line"],
            "line_text_present": bool(line_text),
            "contains": contains,
            "all_present": all(contains.values()),
        })
    return {"snippet_count": len(snippets), "snippets": snippets,
            "all_present": all(s["all_present"] for s in snippets)}


def absence_summary(probes: list[dict] | None = None) -> dict:
    rows = []
    for probe in (ABSENCE_PROBES if probes is None else probes):
        raw = probe["path"]
        expanded = Path(os.path.expanduser(raw))
        if not expanded.is_absolute():
            expanded = AUDIO_ROOT / expanded
        present = expanded.exists()
        rows.append({
            "kind": probe["kind"],
            "label": probe["label"],
            "path": raw,
            "present": bool(present) if probes is None else bool(probe.get("present", present)),
        })
    present = [r for r in rows if r["present"]]
    return {
        "probe_count": len(rows),
        "probes": rows,
        "present": present,
        "all_absent": len(present) == 0,
    }


# ---------------------------------------------------------------------------
# Declaration / admission.
# ---------------------------------------------------------------------------


class DeclarationError(ValueError):
    pass


REQUIRED_TOP_LEVEL = (
    "schema_id", "manifest_id", "source", "checkpoint", "runtime", "geometry",
    "input", "controls", "rights",
)
SOURCE_FIELDS = ("repository", "revision", "license_spdx", "license_sha256", "tree_sha256")
CHECKPOINT_FIELDS = ("variant", "filename", "revision", "byte_count", "sha256", "terms_sha256")
RUNTIME_FIELDS = ("python_version", "framework", "framework_version", "device", "lock_sha256", "offline_load", "deterministic", "packages")
GEOMETRY_FIELDS = ("mode", "channels", "sample_rate_hz", "frame_samples", "sample_format", "hop_samples", "lookahead_samples", "whole_utterance", "state_reset")
INPUT_FIELDS = ("corpus_id", "split", "pair_count", "channels", "sample_rate_hz", "clean_reference", "consent", "rights_sha256")
RIGHTS_FIELDS = ("source_terms", "checkpoint_terms", "training_data_terms", "corpus_rights", "clean_reference_permission", "output_use", "redistribution", "review_reference")
CONTROL_KEYS = ("identity_passthrough", "noisy_control", "task_matched_baseline", "nonfinite_rejection", "content_preservation_protocol")


def _control_document() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "manifest_id": "synthetic-spiking-fullsubnet-control",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": "0" * 40,
            "license_spdx": "MIT",
            "license_sha256": "1" * 64,
            "tree_sha256": "2" * 64,
        },
        "checkpoint": {
            "variant": "synthetic-control",
            "filename": "checkpoint.tar",
            "revision": "3" * 40,
            "byte_count": 1024,
            "sha256": "4" * 64,
            "terms_sha256": "5" * 64,
        },
        "runtime": {
            "python_version": "3.10.14",
            "framework": "torch",
            "framework_version": "1.13.1+cpu",
            "device": "cpu",
            "lock_sha256": "6" * 64,
            "offline_load": True,
            "deterministic": True,
            "packages": ["torch==1.13.1+cpu"],
        },
        "geometry": {
            "mode": "offline_whole_utterance",
            "channels": 1,
            "sample_rate_hz": 16000,
            "frame_samples": 160,
            "sample_format": "float32",
            "hop_samples": 160,
            "lookahead_samples": 0,
            "whole_utterance": True,
            "state_reset": True,
        },
        "input": {
            "corpus_id": "synthetic-control-corpus",
            "split": "test",
            "pair_count": 1,
            "channels": 1,
            "sample_rate_hz": 16000,
            "clean_reference": True,
            "consent": True,
            "rights_sha256": "7" * 64,
        },
        "controls": {k: True for k in CONTROL_KEYS},
        "rights": {k: "synthetic-control" for k in RIGHTS_FIELDS},
    }


def _require_exact_keys(obj: dict, expected: tuple[str, ...], label: str) -> None:
    if not isinstance(obj, dict):
        raise DeclarationError(label + "_not_object")
    keys = tuple(obj.keys())
    if keys != expected:
        raise DeclarationError(label + "_keys_mismatch")


def validate_asset_declaration(document: Any) -> dict:
    if not isinstance(document, dict):
        raise DeclarationError("declaration_not_object")
    assert_no_float(document)
    _require_exact_keys(document, REQUIRED_TOP_LEVEL, "top_level")
    if document["schema_id"] != DECLARATION_SCHEMA_ID:
        raise DeclarationError("schema_id_mismatch")
    if not isinstance(document["manifest_id"], str) or not SLUG.match(document["manifest_id"]):
        raise DeclarationError("manifest_id_invalid")

    src = document["source"]
    _require_exact_keys(src, SOURCE_FIELDS, "source")
    if src["repository"] != SOURCE_REPOSITORY:
        raise DeclarationError("source_repository_mismatch")
    if not isinstance(src["revision"], str) or not HEX40.match(src["revision"]):
        raise DeclarationError("source_revision_invalid")
    if src["license_spdx"] != "MIT":
        raise DeclarationError("source_license_invalid")
    for k in ("license_sha256", "tree_sha256"):
        if not isinstance(src[k], str) or not HEX64.match(src[k]):
            raise DeclarationError("source_" + k + "_invalid")

    ck = document["checkpoint"]
    _require_exact_keys(ck, CHECKPOINT_FIELDS, "checkpoint")
    if not isinstance(ck["variant"], str) or not SLUG.match(ck["variant"]):
        raise DeclarationError("checkpoint_variant_invalid")
    if not isinstance(ck["filename"], str) or not SAFE_BASENAME.match(ck["filename"]):
        raise DeclarationError("checkpoint_filename_invalid")
    if not isinstance(ck["revision"], str) or not HEX40.match(ck["revision"]):
        raise DeclarationError("checkpoint_revision_invalid")
    if not isinstance(ck["byte_count"], int) or isinstance(ck["byte_count"], bool) or ck["byte_count"] <= 0:
        raise DeclarationError("checkpoint_byte_count_invalid")
    for k in ("sha256", "terms_sha256"):
        if not isinstance(ck[k], str) or not HEX64.match(ck[k]):
            raise DeclarationError("checkpoint_" + k + "_invalid")

    rt = document["runtime"]
    _require_exact_keys(rt, RUNTIME_FIELDS, "runtime")
    if not isinstance(rt["python_version"], str) or not re.match(r"^3\.\d+\.\d+$", rt["python_version"]):
        raise DeclarationError("runtime_python_invalid")
    if rt["framework"] != "torch":
        raise DeclarationError("runtime_framework_invalid")
    if not isinstance(rt["framework_version"], str) or not rt["framework_version"]:
        raise DeclarationError("runtime_framework_version_invalid")
    if rt["device"] not in ("cpu", "cuda", "mps"):
        raise DeclarationError("runtime_device_invalid")
    if not isinstance(rt["lock_sha256"], str) or not HEX64.match(rt["lock_sha256"]):
        raise DeclarationError("runtime_lock_sha256_invalid")
    for k in ("offline_load", "deterministic"):
        if rt[k] is not True:
            raise DeclarationError("runtime_" + k + "_must_be_true")
    pkgs = rt["packages"]
    if not isinstance(pkgs, list) or not pkgs or any(not isinstance(p, str) or not PACKAGE.match(p) for p in pkgs):
        raise DeclarationError("runtime_packages_invalid")
    if pkgs != sorted(set(pkgs)):
        raise DeclarationError("runtime_packages_not_sorted_unique")

    geo = document["geometry"]
    _require_exact_keys(geo, GEOMETRY_FIELDS, "geometry")
    if geo["mode"] != "offline_whole_utterance":
        raise DeclarationError("geometry_mode_invalid")
    if geo["channels"] != 1 or geo["sample_rate_hz"] != 16000 or geo["frame_samples"] != 160:
        raise DeclarationError("geometry_mismatch")
    if geo["sample_format"] != "float32":
        raise DeclarationError("geometry_sample_format_invalid")
    for k in ("hop_samples", "lookahead_samples"):
        if not isinstance(geo[k], int) or isinstance(geo[k], bool) or geo[k] < 0:
            raise DeclarationError("geometry_" + k + "_invalid")
    for k in ("whole_utterance", "state_reset"):
        if geo[k] is not True:
            raise DeclarationError("geometry_" + k + "_must_be_true")

    inp = document["input"]
    _require_exact_keys(inp, INPUT_FIELDS, "input")
    if not isinstance(inp["corpus_id"], str) or not SLUG.match(inp["corpus_id"]):
        raise DeclarationError("input_corpus_id_invalid")
    if inp["split"] not in ("dev", "test", "eval"):
        raise DeclarationError("input_split_invalid")
    if not isinstance(inp["pair_count"], int) or isinstance(inp["pair_count"], bool) or inp["pair_count"] <= 0:
        raise DeclarationError("input_pair_count_invalid")
    if inp["channels"] != 1 or inp["sample_rate_hz"] != 16000:
        raise DeclarationError("input_geometry_mismatch")
    for k in ("clean_reference", "consent"):
        if inp[k] is not True:
            raise DeclarationError("input_" + k + "_must_be_true")
    if not isinstance(inp["rights_sha256"], str) or not HEX64.match(inp["rights_sha256"]):
        raise DeclarationError("input_rights_sha256_invalid")

    controls = document["controls"]
    _require_exact_keys(controls, CONTROL_KEYS, "controls")
    for k in CONTROL_KEYS:
        if controls[k] is not True:
            raise DeclarationError("control_" + k + "_must_be_true")

    rights = document["rights"]
    _require_exact_keys(rights, RIGHTS_FIELDS, "rights")
    for k in RIGHTS_FIELDS:
        if not isinstance(rights[k], str) or not rights[k].strip():
            raise DeclarationError("rights_" + k + "_invalid")

    return document


def declaration_control() -> dict:
    doc = _control_document()
    validate_asset_declaration(doc)
    return {
        "accepted": True,
        "manifest_id": doc["manifest_id"],
        "note": "Synthetic schema control only. It proves the validator accepts a well-formed declaration and is not evidence, not an asset and not a result.",
        "opens_asset_bytes": False,
        "qualifies": False,
        "runtime_or_weights_invoked": False,
        "schema_id": DECLARATION_SCHEMA_ID,
        "synthetic_schema_control": True,
    }


def declaration_rejections() -> dict:
    base = _control_document()
    cases = []

    def add(name, mutate, expected_code=None):
        doc = json.loads(canonical_text(base))
        mutate(doc)
        try:
            validate_asset_declaration(doc)
            cases.append({"id": name, "rejected": False, "error": "UNEXPECTED_ACCEPT"})
        except Exception as e:  # noqa: BLE001
            cases.append({"id": name, "rejected": True, "error": type(e).__name__ + ":" + str(e)})

    add("schema_id_mismatch", lambda d: d.__setitem__("schema_id", "wrong"))
    add("missing_top_level", lambda d: d.pop("rights"))
    add("unknown_top_level", lambda d: d.__setitem__("extra", 1))
    add("manifest_id_invalid", lambda d: d.__setitem__("manifest_id", "BAD ID"))
    add("source_repo_mismatch", lambda d: d["source"].__setitem__("repository", "https://example.invalid/x"))
    add("source_revision_invalid", lambda d: d["source"].__setitem__("revision", "abc"))
    add("source_license_invalid", lambda d: d["source"].__setitem__("license_spdx", "Apache-2.0"))
    add("source_sha_invalid", lambda d: d["source"].__setitem__("license_sha256", "x"))
    add("checkpoint_variant_invalid", lambda d: d["checkpoint"].__setitem__("variant", "Bad"))
    add("checkpoint_filename_unsafe", lambda d: d["checkpoint"].__setitem__("filename", "../ckpt.pt"))
    add("checkpoint_revision_invalid", lambda d: d["checkpoint"].__setitem__("revision", "1"))
    add("checkpoint_byte_count_zero", lambda d: d["checkpoint"].__setitem__("byte_count", 0))
    add("checkpoint_byte_count_bool", lambda d: d["checkpoint"].__setitem__("byte_count", True))
    add("checkpoint_sha_invalid", lambda d: d["checkpoint"].__setitem__("sha256", "123"))
    add("runtime_python_invalid", lambda d: d["runtime"].__setitem__("python_version", "2.7.18"))
    add("runtime_framework_invalid", lambda d: d["runtime"].__setitem__("framework", "tensorflow"))
    add("runtime_device_invalid", lambda d: d["runtime"].__setitem__("device", "tpu"))
    add("runtime_lock_invalid", lambda d: d["runtime"].__setitem__("lock_sha256", "bad"))
    add("runtime_offline_false", lambda d: d["runtime"].__setitem__("offline_load", False))
    add("runtime_packages_unsorted", lambda d: d["runtime"].__setitem__("packages", ["z==1.0.0", "a==1.0.0"]))
    add("geometry_rate_mismatch", lambda d: d["geometry"].__setitem__("sample_rate_hz", 48000))
    add("geometry_frame_mismatch", lambda d: d["geometry"].__setitem__("frame_samples", 320))
    add("geometry_channels_mismatch", lambda d: d["geometry"].__setitem__("channels", 2))
    add("geometry_format_invalid", lambda d: d["geometry"].__setitem__("sample_format", "int16"))
    add("geometry_lookahead_negative", lambda d: d["geometry"].__setitem__("lookahead_samples", -1))
    add("geometry_whole_utterance_false", lambda d: d["geometry"].__setitem__("whole_utterance", False))
    add("input_corpus_invalid", lambda d: d["input"].__setitem__("corpus_id", "BAD"))
    add("input_split_invalid", lambda d: d["input"].__setitem__("split", "train"))
    add("input_pair_count_zero", lambda d: d["input"].__setitem__("pair_count", 0))
    add("input_clean_reference_false", lambda d: d["input"].__setitem__("clean_reference", False))
    add("input_rights_sha_invalid", lambda d: d["input"].__setitem__("rights_sha256", "nope"))
    add("controls_missing_key", lambda d: d["controls"].pop("identity_passthrough"))
    add("controls_false", lambda d: d["controls"].__setitem__("task_matched_baseline", False))
    add("rights_missing_key", lambda d: d["rights"].pop("review_reference"))
    add("rights_empty", lambda d: d["rights"].__setitem__("output_use", ""))
    add("top_level_not_object", lambda d: d.clear() or d.update({"not":"object"}))
    # strict json cases are separate; add some structural ones
    add("source_missing_key", lambda d: d["source"].pop("repository"))
    add("checkpoint_terms_invalid", lambda d: d["checkpoint"].__setitem__("terms_sha256", "zz"))
    add("runtime_deterministic_false", lambda d: d["runtime"].__setitem__("deterministic", False))

    # top_level_not_object mutation above made it weird; fix by explicit case
    cases = [c for c in cases if c["id"] != "top_level_not_object"]
    try:
        validate_asset_declaration([])
        cases.append({"id": "top_level_not_object", "rejected": False, "error": "UNEXPECTED_ACCEPT"})
    except Exception as e:  # noqa: BLE001
        cases.append({"id": "top_level_not_object", "rejected": True, "error": type(e).__name__ + ":" + str(e)})

    # ensure >=30
    return {
        "case_count": len(cases),
        "cases": cases,
        "rejection_cases": sum(1 for c in cases if c["rejected"]),
        "all_rejected": all(c["rejected"] for c in cases),
    }


def admission() -> dict:
    control = declaration_control()
    rej = declaration_rejections()
    return {
        "status": "DEFER",
        "admissible": False,
        "synthetic_control": control,
        "rejections": rej,
        "runtime_or_weights_invoked": False,
        "opens_asset_bytes": False,
        "blockers": [b["id"] for b in exact_blockers()],
    }


# ---------------------------------------------------------------------------
# Blockers, gates, artifacts, profile.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    return [
        {"id": "ART-01", "kind": "source_snapshot", "present": False, "blocked": True, "bytes": None, "revision": None, "sha256": None, "verified": False,
         "requirement": "Exact haoxiangsnr/spiking-fullsubnet source at an immutable 40-hex commit with reviewed MIT licence text, NOTICE/README provenance, per-file SHA-256 and a map from model, inference, training/config and weight-loading code to source files."},
        {"id": "ART-02", "kind": "checkpoint_bundle", "present": False, "blocked": True, "bytes": None, "revision": None, "sha256": None, "verified": False,
         "requirement": "Exact released Spiking-FullSubNet checkpoint(s) and validation-set metadata at immutable identity with file names, byte counts, SHA-256, tensor/schema/config mapping, intended input domain, sample rate and checkpoint-specific terms."},
        {"id": "ART-03", "kind": "runtime_lock", "present": False, "blocked": True, "bytes": None, "revision": None, "sha256": None, "verified": False,
         "requirement": "Locked offline runtime with exact interpreter, package versions, lock SHA-256, device profile, deterministic inference policy and any SNN/neuromorphic dependency pins; CPU feasibility measured before any power claim."},
        {"id": "ART-04", "kind": "rights_bundle", "present": False, "blocked": True, "bytes": None, "revision": None, "sha256": None, "verified": False,
         "requirement": "Reviewed source licence, pretrained-weight terms, training-data provenance including Intel N-DNS/validation-set terms where applicable, corpus rights, clean-reference permission, output use, redistribution and attribution."},
        {"id": "ART-05", "kind": "geometry_and_cohort", "present": False, "blocked": True, "bytes": None, "revision": None, "sha256": None, "verified": False,
         "requirement": "Frozen 16 kHz mono task geometry mapped to SDK 160-sample frames, exact input domain/inference contract, state/reset semantics, and a rights-cleared paired noisy/clean cohort with identity/noisy controls and task-matched baseline."},
        {"id": "ART-06", "kind": "enhancement_results", "present": False, "blocked": True, "bytes": None, "revision": None, "sha256": None, "verified": False,
         "requirement": "Independent Enhancement results for paired SI-SDR and STOI, clean-speech preservation, peaks and invalid outputs, authorized listening or predictive screen, alignment, content delay, state, memory, availability timing, resources and uncertainty on the exact runtime."},
    ]


def exact_blockers() -> list[dict]:
    return [
        {"id": "BLK-01", "artifact_id": "ART-01", "status": "open", "qualifies": False,
         "linked_gates": ["RG-01", "RG-04"],
         "title": "Exact source identity and reviewed licence text",
         "state": "The census names haoxiangsnr/spiking-fullsubnet and reports an MIT implementation, but no immutable 40-hex commit, reviewed MIT licence text bytes, per-file SHA-256 manifest or local source checkout is present.",
         "required_action": "Supply the exact source checkout at an immutable 40-hex revision with reviewed MIT licence text and per-file SHA-256 pins; do not substitute mirrors.",
         "reopen_condition": "Only a caller-supplied exact artifact with verified identity and rights can reopen this blocker."},
        {"id": "BLK-02", "artifact_id": "ART-02", "status": "open", "qualifies": False,
         "linked_gates": ["RG-01", "RG-03", "RG-05"],
         "title": "Exact released checkpoint identity, input domain and weight terms",
         "state": "The census reports pretrained models and a validation set, but no released checkpoint filename, byte count, SHA-256, config mapping, input-domain contract, checkpoint-specific terms or local bytes are present.",
         "required_action": "Supply the exact released checkpoint(s) with immutable identity, byte counts, SHA-256, config/input-domain mapping and separately reviewed weight terms.",
         "reopen_condition": "Only a caller-supplied exact artifact with verified identity and rights can reopen this blocker."},
        {"id": "BLK-03", "artifact_id": "ART-03", "status": "open", "qualifies": False,
         "linked_gates": ["RG-02", "RG-06"],
         "title": "Locked runtime and CPU feasibility",
         "state": "No locked interpreter/package runtime, SNN dependency pin, deterministic inference policy, CPU feasibility measurement or neuromorphic/power measurement is present. Power claims are prohibited until supported hardware evidence exists.",
         "required_action": "Supply a locked offline runtime and measure deterministic CPU feasibility on the exact target before any power or latency claim.",
         "reopen_condition": "Only a caller-supplied exact artifact with verified identity and rights can reopen this blocker."},
        {"id": "BLK-04", "artifact_id": "ART-04", "status": "open", "qualifies": False,
         "linked_gates": ["RG-03", "RG-04"],
         "title": "Rights, provenance and redistribution",
         "state": "Source MIT status is reported but not locally reviewed as bytes; pretrained-weight terms, Intel N-DNS/validation-set provenance, training-data rights, corpus rights, clean-reference permission, output use and redistribution are unresolved.",
         "required_action": "Provide reviewed code/weight/data rights, provenance, clean-reference permission, output use and redistribution approval.",
         "reopen_condition": "Only a caller-supplied exact artifact with verified identity and rights can reopen this blocker."},
        {"id": "BLK-05", "artifact_id": "ART-05", "status": "open", "qualifies": False,
         "linked_gates": ["RG-04", "RG-05", "RG-07"],
         "title": "Frozen geometry, SDK mapping and rights-cleared cohort",
         "state": "No verified 16 kHz mono input domain, frame/hop/lookahead/state contract, 160-sample SDK mapping, or rights-cleared paired noisy/clean cohort with controls is present.",
         "required_action": "Freeze exact geometry/input-domain mapping to SDK v0 16 kHz mono 160-sample frames and admit a rights-cleared matched cohort with controls.",
         "reopen_condition": "Only a caller-supplied exact artifact with verified identity and rights can reopen this blocker."},
        {"id": "BLK-06", "artifact_id": "ART-06", "status": "open", "qualifies": False,
         "linked_gates": ["RG-06", "RG-07", "RG-08"],
         "title": "Enhancement, listening and target-runtime evidence",
         "state": "No paired SI-SDR/STOI, clean-speech preservation, peak/invalid, listening/predictive screen, alignment, content delay, state, memory, availability timing, resource or uncertainty result exists.",
         "required_action": "Run and preserve the independent Enhancement protocol and target-runtime timing on the exact pinned source, checkpoint and runtime.",
         "reopen_condition": "Only a caller-supplied exact artifact with verified identity and rights can reopen this blocker."},
    ]


def release_gates() -> list[dict]:
    rows = [
        ("RG-01", "Exact source and checkpoint identity", "Supply exact immutable source and released checkpoint identities with reviewed terms and digests."),
        ("RG-02", "Locked runtime and deterministic CPU feasibility", "Provide locked offline runtime and deterministic CPU feasibility on the recorded target; no unmeasured power claim."),
        ("RG-03", "Rights and provenance", "Resolve source, checkpoint, training-data, corpus, clean-reference, output-use and redistribution rights."),
        ("RG-04", "Frozen geometry and cohort", "Freeze 16 kHz mono geometry, 160-sample SDK mapping, state/reset contract and rights-cleared cohort with controls."),
        ("RG-05", "Input domain and inference contract", "Verify released-checkpoint input domain, inference contract, normalization and state behavior on exact assets."),
        ("RG-06", "Enhancement profile evidence", "Produce paired SI-SDR/STOI, preservation, peaks/invalid, alignment/content-delay, state, memory, availability timing and uncertainty."),
        ("RG-07", "Listening or predictive screen and independent review", "Complete authorized listening or labeled predictive screen and obtain independent exact-head review."),
        ("RG-08", "Opt-in intake and release approval", "Add default-off opt-in intake only after prior gates pass and obtain release approval."),
    ]
    return [
        {
            "id": gid,
            "linked_row": TASK,
            "name": name,
            "qualifies": False,
            "status": "blocked",
            "reason": "Required exact artifact, rights, runtime, geometry or evidence is missing.",
            "reopen_condition": reopen,
        }
        for gid, name, reopen in rows
    ]


def enhancement_profile() -> dict:
    rows = [
        ("ENH-01", "blocked", "Run an identity/noisy control and an established task-matched baseline.", "No deterministic identity/noisy control or task-matched baseline exists on exact Spiking-FullSubNet assets."),
        ("ENH-02", "blocked", "Score paired SI-SDR and STOI where permitted clean references exist.", "No rights-cleared paired cohort and no SI-SDR/STOI measurement exists."),
        ("ENH-03", "blocked", "Measure clean-speech preservation, peaks and invalid outputs.", "No clean-speech preservation, peak, clipping or invalid-output record exists."),
        ("ENH-04", "blocked", "For unpaired speech use a separately labeled predictive screen or authorized listening.", "No predictive screen or authorized listening exists."),
        ("ENH-05", "blocked", "Report alignment, state, memory and measured content/availability timing for the exact runtime.", "No alignment, content delay, state, memory or availability timing measurement exists."),
        ("ENH-06", "blocked", "Keep corpus rights, clean-reference permission and output use as independent gates.", "Rights and permissions are unresolved."),
        ("ENH-07", "blocked", "Freeze input domain, sample rate and frame geometry before comparing results.", "No verified input domain or SDK mapping is present."),
        ("ENH-08", "documented", "Record source-reported context without promoting it to a result.", "Census reports Intel N-DNS Track 1 win, pretrained models and validation set; not reproduced locally."),
    ]
    return {
        "profile": PROFILE_LABEL,
        "row_summary": {
            "requirement_count": len(rows),
            "blocked_count": sum(1 for r in rows if r[1] == "blocked"),
            "documented_count": sum(1 for r in rows if r[1] == "documented"),
            "profile_satisfied": False,
        },
        "rows": [
            {"id": rid, "status": status, "requirement": req, "evidence": ev}
            for rid, status, req, ev in rows
        ],
    }


# ---------------------------------------------------------------------------
# Build contract/report.
# ---------------------------------------------------------------------------


def _pin_table() -> list[dict]:
    return [{"path": k, "sha256": v} for k, v in sorted(SOURCE_PINS.items())]


def _boundary_table() -> list[dict]:
    return [{"path": k, "sha256": v} for k, v in sorted(BOUNDARY_PINS.items())]


def public_v0_geometry() -> dict:
    return {
        "channels": 1,
        "descriptor_sample_format": "f32",
        "frame_samples": 160,
        "hop_samples": 160,
        "preserved": True,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
        "candidate_mapping_present": False,
    }


def build_contract() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "owner": OWNER,
        "reviewer": REVIEWER,
        "write_scope": WRITE_SCOPE,
        "task_prefix": TASK_PREFIX,
        "depends_on": list(DEPENDS_ON),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "incomplete": True,
        "proposal_only": True,
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "board_row_projection": projection,
        "board_row_sha256": board_row_digest(projection),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "source_pins": dict(sorted(SOURCE_PINS.items())),
        "boundary_pins": dict(sorted(BOUNDARY_PINS.items())),
        "profile_source": {
            "path": PROFILE_SOURCE_REL,
            "label": PROFILE_LABEL,
            "phrases": list(PROFILE_PHRASES),
        },
        "scope": {
            "task_local_only": True,
            "network_access": False,
            "download_attempted": False,
            "real_audio": False,
            "real_corpus": False,
            "source_present": False,
            "weights_present_locally": False,
            "weights_vendored": False,
            "runtime_present": False,
            "runtime_invoked": False,
            "model_executed": False,
            "listening": False,
            "device_timing": False,
            "benchmark_claim": False,
            "release_claim": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "board_or_handoff_change": False,
        },
        "boundary": {
            "task_local_only": True,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "installed_v0_behavior_change": False,
            "runtime_imported": False,
            "weights_vendored": False,
            "audio_added": False,
        },
        "public_v0_geometry": public_v0_geometry(),
        "admission_contract": {
            "schema_id": DECLARATION_SCHEMA_ID,
            "contract_id": "audio-sdk/spiking-fullsubnet-caller-asset/0.1",
            "required_top_level_fields": list(REQUIRED_TOP_LEVEL),
            "source_fields": list(SOURCE_FIELDS),
            "checkpoint_fields": list(CHECKPOINT_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "geometry_fields": list(GEOMETRY_FIELDS),
            "input_fields": list(INPUT_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "control_keys": list(CONTROL_KEYS),
            "required_sample_rate_hz": 16000,
            "required_channels": 1,
            "required_frame_samples": 160,
            "required_sample_format": "float32",
            "accepted_control_is_synthetic_only": True,
            "accepted_control_qualifies": False,
            "runtime_or_weights_invoked": False,
            "manifest_validation_only": True,
            "strict_json_rejected": True,
            "floats_rejected": True,
            "unknown_fields_rejected": True,
            "unresolved_values_rejected": True,
        },
        "candidate": {
            "name": TASK_TITLE,
            "family": CANDIDATE_FAMILY,
            "source_repository": SOURCE_REPOSITORY,
            "source_reported_license": "MIT (reported, not locally verified as bytes)",
            "reported_context": "Official MIT implementation reports Intel N-DNS Challenge Track 1 winning solution and includes pretrained models and a validation set.",
            "locally_present": False,
            "admitted_as_result": False,
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "enhancement_profile": enhancement_profile(),
        "non_claims": list(NON_CLAIMS),
        "disposition": {
            "decision": DECISION,
            "status": STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "incomplete": True,
            "proposal_only": True,
            "defer_before": DEFER_BEFORE,
            "result_promoted": False,
            "missing_result_qualifies": False,
            "registered": False,
            "default_enabled": False,
            "production_exposure": "DEFER",
        },
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "all_release_gates_blocked": True,
            "exact_source_present": False,
            "exact_weights_present": False,
            "exact_runtime_present": False,
            "rights_cleared": False,
            "frozen_geometry_present": False,
            "enhancement_evaluation_present": False,
            "listening_result": False,
            "timing_result": False,
            "release_qualification_present": False,
            "real_result_present": False,
            "missing_result_promoted": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    presence = pin_presence()
    evidence = evidence_presence()
    absence = absence_summary()
    strict = strict_json_rejections()
    control = declaration_control()
    rej = declaration_rejections()
    scope = scope_status(WORKTREE)
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "owner": OWNER,
        "reviewer": REVIEWER,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "incomplete": True,
        "proposal_only": True,
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "board_row_projection": contract["board_row_projection"],
        "board_row_sha256": contract["board_row_sha256"],
        "linked_rows": contract["linked_rows"],
        "linked_rows_sha256": contract["linked_rows_sha256"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "pin_presence": presence,
        "evidence_presence": evidence,
        "absence_evidence": absence,
        "strict_json": strict,
        "admission_contract": contract["admission_contract"],
        "admission": admission(),
        "declaration_control": control,
        "declaration_rejections": rej,
        "scope_gate": scope,
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "candidate": contract["candidate"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "release_gates": contract["release_gates"],
        "enhancement_profile": contract["enhancement_profile"],
        "non_claims": contract["non_claims"],
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "reported_metrics": {
            "admitted_as_result": False,
            "qualifies": False,
            "local_si_sdr": None,
            "local_stoi": None,
            "local_pesq": None,
            "local_dns_mos": None,
            "source_reported_claim": "Intel N-DNS Challenge Track 1 winning solution (source-reported only, not reproduced here)",
            "status": "source_reported_only_not_measured_here",
        },
        "reproduction": {
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            ],
            "cold_start_repeats": 3,
            "interpreter": "Python 3.12.16, standard library only",
        },
    }


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# SOURCES/readme helpers.
# ---------------------------------------------------------------------------


def _iter_source_artifacts() -> list[Path]:
    return [HERE / name for name in SOURCE_ARTIFACT_FILES]


def sources_bytes() -> bytes:
    for relative, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(AUDIO_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(WORKTREE / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
    lines = [
        "# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
        "# SPDX-License-" "Identifier: Apache-2.0",
        "# Deterministic digest manifest for SDK-SPIKING-FULLSUBNET evidence.",
        "# Source/boundary pins are read-only inputs; task files are this package only.",
        "",
    ]
    for rel, digest in sorted(SOURCE_PINS.items()):
        lines.append(f"{digest}  source:{rel}")
    for rel, digest in sorted(BOUNDARY_PINS.items()):
        lines.append(f"{digest}  sdk:{rel}")
    for name in sorted(LOCAL_FILES):
        if name == "SOURCES.sha256":
            continue
        path = HERE / name
        lines.append(f"{sha256_file(path)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


def readme_table_rows() -> dict[str, list[tuple[str, str]]]:
    src = [(f"source:{k}", v) for k, v in sorted(SOURCE_PINS.items())]
    bnd = [(f"sdk:{k}", v) for k, v in sorted(BOUNDARY_PINS.items())]
    art = []
    for path in sorted(_iter_source_artifacts(), key=lambda x: x.name):
        art.append((path.name, sha256_file(path)))
    return {"source": src, "boundary": bnd, "artifacts": art}


def _render_table(rows: list[tuple[str, str]]) -> str:
    out = ["| Path | SHA-256 |", "| --- | --- |"]
    for path, digest in rows:
        out.append(f"| `{path}` | `{digest}` |")
    return "\n".join(out)


def update_readme_tables(text: str) -> str:
    tables = readme_table_rows()
    replacements = {
        "<!-- DIGEST_TABLE_SOURCE_START -->": "<!-- DIGEST_TABLE_SOURCE_END -->",
        "<!-- DIGEST_TABLE_BOUNDARY_START -->": "<!-- DIGEST_TABLE_BOUNDARY_END -->",
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->": "<!-- DIGEST_TABLE_ARTIFACTS_END -->",
    }
    mapping = {
        "<!-- DIGEST_TABLE_SOURCE_START -->": _render_table(tables["source"]),
        "<!-- DIGEST_TABLE_BOUNDARY_START -->": _render_table(tables["boundary"]),
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->": _render_table(tables["artifacts"]),
    }
    for start, end in replacements.items():
        if start not in text or end not in text:
            raise ValueError("readme_missing_marker:" + start)
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + start + "\n" + mapping[start] + "\n" + end + after
    return text


def verify_readme_digests(text: str) -> dict[str, int]:
    tables = readme_table_rows()
    def parse(start: str, end: str) -> list[tuple[str, str]]:
        if start not in text or end not in text:
            raise ValueError("readme_missing_marker:" + start)
        block = text.split(start, 1)[1].split(end, 1)[0]
        rows = []
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("| `"):
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) != 2:
                continue
            path = parts[0].strip("`")
            digest = parts[1].strip("`")
            rows.append((path, digest))
        return rows
    src = parse("<!-- DIGEST_TABLE_SOURCE_START -->", "<!-- DIGEST_TABLE_SOURCE_END -->")
    bnd = parse("<!-- DIGEST_TABLE_BOUNDARY_START -->", "<!-- DIGEST_TABLE_BOUNDARY_END -->")
    art = parse("<!-- DIGEST_TABLE_ARTIFACTS_START -->", "<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    if src != tables["source"]:
        raise ValueError("readme_source_table_mismatch")
    if bnd != tables["boundary"]:
        raise ValueError("readme_boundary_table_mismatch")
    if art != tables["artifacts"]:
        raise ValueError("readme_artifacts_table_mismatch")
    return {"source": len(src), "boundary": len(bnd), "artifacts": len(art)}
