# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for
SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION.

Standard library only. The catalogued candidate is "Phase vocoder with neural
transient preservation" in the voice-enhancement matrix: a time-scale
modification method that preserves transients using a neural component on top
of phase-vocoder analysis. The local evidence screen records it as
unavailable/blocked: no named method, official source, checkpoint, runtime,
licence text, rights-cleared input or output is present anywhere probed.

This module pins the evidence that does exist, proves a fixed absence inventory,
validates a fail-closed caller-supplied asset declaration without resolving,
importing, loading or executing anything, and builds canonical DEFER bytes. It
never estimates a rate, stretches audio, synthesises audio, opens media, times a
device or produces a benchmark result. Classical phase vocoders, Rubber Band,
SoundTouch, OLA/SOLA and FFmpeg atempo are different candidates and are not
substituted for the neural transient-preserving candidate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

TASK = "SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION"
TASK_TITLE = "Phase vocoder with neural transient preservation"
COMPONENT_ID = "phase-vocoder-with-neural-transient-preservation"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/phase-vocoder-with-neural-transient-preservation/ only"
TASK_PREFIX = "docs/task-evidence/phase-vocoder-with-neural-transient-preservation/"
CONTRACT_ID = "audio-sdk/phase-vocoder-with-neural-transient-preservation-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/phase-vocoder-with-neural-transient-preservation-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/phase-vocoder-with-neural-transient-preservation-report/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/phase-vocoder-with-neural-transient-preservation-asset-declaration/0.1"
BASE_COMMIT = "066e91285f1f86dbaaefc6508032cac152d95d22"
BRANCH = "swarm/SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.11.5"
CANDIDATE_NAME = "Phase vocoder with neural transient preservation"
CANDIDATE_FAMILY = "neural_transient_preserving_phase_vocoder_tsm"
TASK_GEOMETRY_STATE = "unverified_unnamed_neural_transient_phase_vocoder_family"
EVIDENCE_RECORD = 40
METHOD_REFERENCE = None

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent
def _find_sdk_root() -> Path:
    override = os.environ.get("SDK_WORKTREE") or os.environ.get("AUDIO_SDK_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.extend(Path.cwd().resolve().parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION"))
    seen=set()
    for c in candidates:
        c=c.resolve()
        if c in seen:
            continue
        seen.add(c)
        if (c/"CONTRACTS.md").is_file() and (c/"api/include/audio_sdk/provider_v0.h").is_file():
            return c
    return HERE.parents[2]

WORKTREE = _find_sdk_root()
SDK_ROOT = WORKTREE


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.extend(Path.cwd().resolve().parents)
    # common sibling layout
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml"))
    seen=set()
    for candidate in candidates:
        c=candidate.resolve()
        if c in seen:
            continue
        seen.add(c)
        board = c / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (c / "research").is_dir():
            return c
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md":
        "5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
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
    "docs/task-evidence/diffatsm/report.json":
        "8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a",
    "docs/task-evidence/neural-atsm/report.json":
        "3dd7b111cb8af978fd5581f0ffbab6d6907e8ba2eb3e9469b19b15af72e1057b",
    "docs/task-evidence/neural-wsola/report.json":
        "81b8823caabd2738e728fc787f6072fd9ba769e11446ecd32ff7d8b244c8a842",
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Measure source/output mapping",
    "duration, pitch, transient audibility and playback buffering",
    "1\u00d7, rate changes, unfamiliar speech, music, silence, rebuffer, drift "
    "and the final partial window",
    "pause or filler decisions tied to source timestamps and measure speech "
    "preservation",
)

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
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".h5",
    ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o",
    ".onnx", ".opus", ".otf", ".pcap", ".pcapng", ".pt", ".pth", ".pyc",
    ".safetensors", ".so", ".tar", ".ttf", ".wav", ".wasm", ".weights",
    ".zip",
}

WORKSPACE_PROBES = (
    "data/checkouts/phase-vocoder-with-neural-transient-preservation",
    "data/checkouts/phase_vocoder_neural_transient_preservation",
    "data/checkouts/neural-transient-preservation",
    "data/models/phase-vocoder-with-neural-transient-preservation",
    "data/models/neural-transient-preservation",
    "data/envs/phase-vocoder-with-neural-transient-preservation",
    "data/reference/phase-vocoder-with-neural-transient-preservation",
    "data/audio/phase-vocoder-with-neural-transient-preservation",
    "data/runs/phase-vocoder-with-neural-transient-preservation",
    "research/phase-vocoder-with-neural-transient-preservation",
    "research/voice-enhancement-20261101/phase-vocoder-with-neural-transient-preservation",
    "research/voice-enhancement-20261101/agent-neural-transient-phase-vocoder",
)
WORKTREE_PROBES = (
    "adapters/phase-vocoder-with-neural-transient-preservation",
    "schemas/providers/phase-vocoder-with-neural-transient-preservation",
    "third_party/phase-vocoder-with-neural-transient-preservation",
    "third_party/neural-transient-preservation",
    "build/check-env/lib/python3.11/site-packages/neural_transient_preservation",
)
HOME_PROBES = (
    "~/.cache/phase-vocoder-with-neural-transient-preservation",
    "~/.cache/huggingface/hub/models--phase-vocoder-neural-transient-preservation",
    "~/.cache/huggingface/hub/models--neural-transient-preservation",
)

NON_CLAIMS = [
    "No phase-vocoder-with-neural-transient-preservation source, code snapshot, "
    "weight, checkpoint, model card or inference config is present, imported, "
    "deserialised, loaded or executed.",
    "No PyTorch, TensorFlow, ONNX Runtime or other neural runtime is installed, "
    "imported or linked by this package.",
    "No real audio, corpus, synthetic speech, stretched output or candidate "
    "output is read, generated or produced.",
    "No candidate rate, duration, pitch, transient, preservation, listening, "
    "device-timing or benchmark result is reproduced.",
    "No classical phase vocoder, Rubber Band, SoundTouch, Sonic, OLA/SOLA, "
    "PSOLA or FFmpeg atempo result is inherited, pooled or presented as the "
    "neural transient-preserving candidate.",
    "The caller-supplied asset declaration is a fail-closed shape check only; "
    "it never resolves a path, hashes an external byte, admits a presence "
    "claim or grants qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build, CI "
    "workflow, board or handoff change exists.",
    "The research prose is source-reported context only and is not promoted to "
    "measured evidence.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
    "No sibling neural TSM or classical time-stretch evidence, fixture, "
    "checkpoint or metric is inherited, pooled or treated as a candidate "
    "result.",
]

HISTORICAL_EVIDENCE = (
    {
        "source": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "line": 40,
        "class": "candidate_screen_source_reported",
        "admitted_as_result": False,
        "boundary": "Record 40 marks Phase vocoder with neural transient "
                    "preservation unavailable/blocked: no phase-vocoder/"
                    "transient model implementation or weights; the adjacent "
                    "atempo screen is not this candidate.",
    },
    {
        "source": "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
        "line": 15,
        "class": "artifact_review_source_reported",
        "admitted_as_result": False,
        "boundary": "Records that no phase-vocoder/transient model "
                    "implementation or weights are staged, and that the "
                    "adjacent atempo screen does not change the candidate "
                    "status.",
    },
    {
        "source": "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
        "line": 32,
        "class": "candidate_family_source_reported",
        "admitted_as_result": False,
        "boundary": "Records no local STFT/phase-vocoder TSM or learned "
                    "transient-preservation model. Notes Rubber Band R3/R2 as "
                    "a good non-neural control with phase resets on percussive "
                    "transients, but explicitly not neural transient "
                    "preservation and not a measured speech result here.",
    },
    {
        "source": "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md",
        "line": 20,
        "class": "reaudit_source_reported",
        "admitted_as_result": False,
        "boundary": "Reaudits Neural WSOLA and transient-preserving "
                    "phase-vocoder methods as still lacking an exact "
                    "implementation/checkpoint; existing Rubber Band/Bungee/"
                    "SoundTouch/PSOLA results are conventional engine evidence, "
                    "not this neural candidate.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Marks phase-vocoder-with-neural-transient-preservation "
                    "as blocked, disposition sdk-model and verification_profile "
                    "rate; it is not a result.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": "Defines the Rate profile requirements. No rate "
                    "measurement, control, pitch, buffering, preservation or "
                    "device-timing record exists for this candidate.",
    },
)

PEER_SEPARATION = (
    {
        "component": "phase-vocoder-baseline",
        "task": "SDK-PHASE-VOCODER-BASELINE",
        "path": "docs/task-evidence/phase-vocoder-baseline/report.json",
        "class": "classical_phase_vocoder_reference",
        "decision": "defer_playback_exposure",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Phase-vocoder-baseline is a deterministic classical "
                    "comparison on the elastic PCM fixture. It has no neural "
                    "transient-preservation model and is not this candidate.",
    },
    {
        "component": "rubber-band-r3-streaming",
        "task": "SDK-RUBBER-BAND-R3-STREAMING",
        "path": "docs/task-evidence/rubber-band-r3-streaming/report.json",
        "class": "classical_transient_aware_control",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Rubber Band R3 is a classical phase-vocoder control with "
                    "percussive transient phase resets, not neural transient "
                    "preservation. No Rubber Band result is inherited.",
    },
    {
        "component": "neural-wsola",
        "task": "SDK-NEURAL-WSOLA",
        "path": "docs/task-evidence/neural-wsola/report.json",
        "class": "separate_neural_tsm_candidate",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Neural WSOLA is a distinct neural waveform TSM family "
                    "with its own blocker. No source, checkpoint, geometry, "
                    "rejection count or metric is inherited or pooled here.",
    },
    {
        "component": "neural-tsm-adjacent-classical-control",
        "task": "SDK-FFMPEG-ATEMPO",
        "path": "state-report",
        "class": "adjacent_classical_control",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "The FFmpeg atempo screen is an adjacent conventional "
                    "timing control. The pinned research explicitly states it "
                    "is not this candidate; no atempo measurement is inherited.",
    },
)


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


def assert_no_float(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise TypeError("float not allowed in canonical evidence: " + path)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("non-string key at " + path)
            assert_no_float(item, path + "/" + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_no_float(item, path + "/" + str(index))


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


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
    if tuple(projection["depends_on"]) != DEPENDS_ON:
        raise ValueError("board_depends_on_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    result: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_absent:" + row_id)
        result.append(_project(row, require_component=row_id == TASK))
    if result[0]["component"] != COMPONENT_ID:
        raise ValueError("linked_component_mismatch")
    return tuple(result)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None
                         else board_row_projection())


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def resolve_scope_base(worktree: Path) -> str | None:
    candidates: list[tuple[int, str, str]] = []
    for ref in SCOPE_BASE_REFS:
        merge_base = _git(worktree, "merge-base", "HEAD", ref)
        if merge_base.returncode != 0:
            continue
        base = merge_base.stdout.strip()
        if not base:
            continue
        stamp = _git(worktree, "show", "-s", "--format=%ct", base)
        if stamp.returncode != 0:
            continue
        try:
            unix = int(stamp.stdout.strip())
        except ValueError:
            continue
        candidates.append((unix, base, ref))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


def committed_paths_since_base(worktree: Path) -> tuple[str | None, list[str]]:
    base = resolve_scope_base(worktree)
    if base is None:
        return None, []
    changed = _git(worktree, "diff", "--name-only", base + "..HEAD")
    if changed.returncode != 0:
        raise ValueError("scope_diff_failed")
    paths = sorted({line for line in changed.stdout.splitlines() if line})
    return base, paths


def collect_dirty_paths(worktree: Path) -> list[str]:
    status = _git(worktree, "status", "--porcelain", "-z")
    if status.returncode != 0:
        raise ValueError("git_status_failed")
    raw = status.stdout.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(raw):
        entry = raw[index]
        index += 1
        if not entry:
            continue
        path = entry[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
        if len(entry) >= 2 and entry[1] in "RC":
            index += 1
    return sorted(set(paths))


def path_is_within_prefix(path: str, prefix: str) -> bool:
    clean = path.replace("\\", "/").lstrip("./")
    prefix_clean = prefix.replace("\\", "/")
    return clean == prefix_clean.rstrip("/") or clean.startswith(prefix_clean)


def probe_presence(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def absence_probes() -> dict:
    probes: list[dict] = []
    for rel in WORKSPACE_PROBES:
        probes.append({
            "path": rel,
            "present": probe_presence(AUDIO_ROOT / rel),
            "searched_home_cache": False,
            "searched_sdk_worktree": False,
            "searched_workspace": True,
        })
    for rel in WORKTREE_PROBES:
        probes.append({
            "path": rel,
            "present": probe_presence(SDK_ROOT / rel),
            "searched_home_cache": False,
            "searched_sdk_worktree": True,
            "searched_workspace": False,
        })
    home = Path.home()
    for rel in HOME_PROBES:
        expanded = home / rel.removeprefix("~/")
        probes.append({
            "path": rel,
            "present": probe_presence(expanded),
            "searched_home_cache": True,
            "searched_sdk_worktree": False,
            "searched_workspace": False,
        })
    present = [p for p in probes if p["present"]]
    return {
        "all_absent": len(present) == 0,
        "audio_read": False,
        "candidate_module_imported": False,
        "candidate_runtime_executed": False,
        "download_attempted": False,
        "fixed_probe_list_only": True,
        "home_probe_count": len(HOME_PROBES),
        "network_used": False,
        "present_count": len(present),
        "probe_count": len(probes),
        "probes": probes,
        "recursive_workspace_walk": False,
        "weights_loaded": False,
        "workspace_probe_count": len(WORKSPACE_PROBES),
        "worktree_probe_count": len(WORKTREE_PROBES),
    }


SNIPPET_CHECKS = (
    ("research/voice-enhancement-20261101/candidate_matrix.csv",
     "No phase-vocoder/transient model implementation or weights"),
    ("research/voice-enhancement-20261101/candidate_matrix.csv",
     "the adjacent atempo screen is not this candidate"),
    ("research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
     "No phase-vocoder/transient model implementation or weights staged"),
    ("research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
     "No local STFT/phase-vocoder TSM or learned transient-preservation model"),
    ("research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
     "not \"neural transient preservation.\""),
    ("research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md",
     "transient-preserving phase-vocoder methods have no exact implementation/checkpoint"),
    ("audio-benchmark-platform/plan/INVENTORY.json",
     "phase-vocoder-with-neural-transient-preservation"),
)


def evidence_snippets() -> dict:
    checks = []
    for rel, phrase in SNIPPET_CHECKS:
        path = AUDIO_ROOT / rel
        present = path.is_file() and phrase in path.read_text(encoding="utf-8", errors="replace")
        checks.append({"path": rel, "phrase": phrase, "present": present})
    return {"all_present": all(c["present"] for c in checks), "checks": checks, "count": len(checks)}


def _rate_rows() -> list[dict]:
    blocked = "No named method, source, checkpoint, runtime or output exists; the item cannot be measured. Classical phase-vocoder or atempo controls are different candidates and are not substituted."
    rows = [
        ("RATE-01", "Source/output mapping for the exact runtime."),
        ("RATE-02", "Target and actual duration for constant and changing rates."),
        ("RATE-03", "Pitch preservation or shift for the exact runtime."),
        ("RATE-04", "Transient audibility proxy or authorized listening."),
        ("RATE-05", "Playback buffering, fill/flush and deadline behaviour."),
        ("RATE-06", "1x identity control."),
        ("RATE-07", "Rate changes, including step and ramp profiles."),
        ("RATE-08", "Unfamiliar speech material."),
        ("RATE-09", "Music material and a synthetic music negative control."),
        ("RATE-10", "Silence and empty input."),
        ("RATE-11", "Rebuffer, drift and the final partial window."),
        ("RATE-12", "Pause or filler decisions tied to source timestamps and speech preservation."),
    ]
    out = [{"id": rid, "requirement": req, "status": "blocked", "qualifies": False, "evidence": blocked} for rid, req in rows]
    out.append({
        "id": "RATE-13",
        "requirement": "Separate paired, unpaired, synthetic, human and source-reported evidence.",
        "status": "documented",
        "qualifies": False,
        "evidence": "The report keeps source-reported, synthetic-schema, missing-real and sibling candidate sections separate; no category is pooled.",
    })
    return out


def rate_profile() -> dict:
    return {
        "candidate_buffering_result": None,
        "candidate_duration_result": None,
        "candidate_geometry": None,
        "candidate_pitch_result": None,
        "candidate_preservation_result": None,
        "candidate_transient_result": None,
        "conditions": ["identity_1x", "rate_changes", "unfamiliar_speech", "music", "silence", "rebuffer", "drift", "final_partial_window", "pause_filler_source_timestamps"],
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_satisfied": False,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": {
            "all_phrases_present": True,
            "path": PROFILE_SOURCE_REL,
            "phrases_present": list(PROFILE_PHRASES),
            "row_count": 1,
            "unique_row": True,
        },
        "rate_result_present": False,
        "real_results": 0,
        "requirement_rows": _rate_rows(),
        "surrogate_present": False,
        "synthetic_envelope_only": False,
        "synthetic_results": 0,
    }


REQUIRED_DECLARATION_FIELDS = (
    "schema_id", "declaration_id", "candidate", "source", "weights",
    "runtime", "geometry", "rights", "disposition",
)
CANDIDATE_FIELDS = ("name", "family", "named_method", "method_reference", "audio_input", "audio_output")
SOURCE_FIELDS = ("declared_present", "revision", "license_sha256", "source_sha256")
WEIGHTS_FIELDS = ("declared_present", "revision", "weights_sha256", "byte_count")
RUNTIME_FIELDS = ("declared_present", "python_version", "platform", "device", "lock_sha256")
GEOMETRY_FIELDS = ("declared", "sample_rate_hz", "frame_samples", "hop_samples", "channels")
RIGHTS_FIELDS = ("code", "weights", "training_data", "inputs", "output_use", "redistribution", "review_reference")
DISPOSITION_FIELDS = ("decision", "qualifies")


def _expect_obj(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("not_object:" + field)
    return value


def _expect_keys(obj: dict, allowed: tuple[str, ...], field: str) -> None:
    extra = sorted(set(obj) - set(allowed))
    if extra:
        raise ValueError("unknown_field:" + field + "." + extra[0])
    missing = [k for k in allowed if k not in obj]
    if missing:
        raise ValueError("missing_field:" + field + "." + missing[0])


def _reject_present_claims(obj: dict, field: str, present_field: str = "declared_present") -> None:
    if obj.get(present_field) is not False:
        raise ValueError("unverified_claim:" + field + "." + present_field)
    for key, value in obj.items():
        if key == present_field:
            continue
        if value is not None and value is not False:
            raise ValueError("unverified_claim:" + field + "." + key)


def validate_asset_declaration(payload: str | bytes | dict) -> dict:
    document = loads_strict(payload) if isinstance(payload, str) else (
        parse_strict_json_text(payload) if isinstance(payload, (bytes, bytearray)) else payload)
    if not isinstance(document, dict):
        raise ValueError("not_object:declaration")
    assert_no_float(document)
    _expect_keys(document, REQUIRED_DECLARATION_FIELDS, "declaration")
    if document["schema_id"] != DECLARATION_SCHEMA_ID:
        raise ValueError("schema_id_mismatch:schema_id")
    if not isinstance(document["declaration_id"], str) or not SLUG.match(document["declaration_id"]):
        raise ValueError("invalid_slug:declaration_id")

    candidate = _expect_obj(document["candidate"], "candidate")
    _expect_keys(candidate, CANDIDATE_FIELDS, "candidate")
    if candidate["name"] != CANDIDATE_NAME:
        raise ValueError("candidate_name_mismatch:candidate.name")
    if candidate["family"] != CANDIDATE_FAMILY:
        raise ValueError("candidate_family_mismatch:candidate.family")
    if candidate["named_method"] is not None:
        raise ValueError("unverified_claim:candidate.named_method")
    if candidate["method_reference"] is not None:
        raise ValueError("unverified_claim:candidate.method_reference")
    if candidate["audio_input"] is not True:
        raise ValueError("missing_required_value:candidate.audio_input")
    if candidate["audio_output"] is not True:
        raise ValueError("missing_required_value:candidate.audio_output")

    source = _expect_obj(document["source"], "source")
    _expect_keys(source, SOURCE_FIELDS, "source")
    _reject_present_claims(source, "source")
    weights = _expect_obj(document["weights"], "weights")
    _expect_keys(weights, WEIGHTS_FIELDS, "weights")
    _reject_present_claims(weights, "weights")
    runtime = _expect_obj(document["runtime"], "runtime")
    _expect_keys(runtime, RUNTIME_FIELDS, "runtime")
    _reject_present_claims(runtime, "runtime")
    geometry = _expect_obj(document["geometry"], "geometry")
    _expect_keys(geometry, GEOMETRY_FIELDS, "geometry")
    _reject_present_claims(geometry, "geometry", "declared")

    rights = _expect_obj(document["rights"], "rights")
    _expect_keys(rights, RIGHTS_FIELDS, "rights")
    for key in RIGHTS_FIELDS:
        value = rights[key]
        if key == "review_reference":
            if value is not None:
                raise ValueError("unverified_claim:rights.review_reference")
        elif value is not False:
            raise ValueError("unverified_claim:rights." + key)

    disposition = _expect_obj(document["disposition"], "disposition")
    _expect_keys(disposition, DISPOSITION_FIELDS, "disposition")
    if disposition["qualifies"] is not False:
        raise ValueError("unverified_claim:disposition.qualifies")
    if disposition["decision"] != DECISION:
        raise ValueError("premature_decision:disposition.decision")
    return document


def unpopulated_asset_declaration() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "declaration_id": "unpopulated",
        "candidate": {
            "name": CANDIDATE_NAME,
            "family": CANDIDATE_FAMILY,
            "named_method": None,
            "method_reference": None,
            "audio_input": True,
            "audio_output": True,
        },
        "source": {"declared_present": False, "revision": None, "license_sha256": None, "source_sha256": None},
        "weights": {"declared_present": False, "revision": None, "weights_sha256": None, "byte_count": None},
        "runtime": {"declared_present": False, "python_version": None, "platform": None, "device": None, "lock_sha256": None},
        "geometry": {"declared": False, "sample_rate_hz": None, "frame_samples": None, "hop_samples": None, "channels": None},
        "rights": {"code": False, "weights": False, "training_data": False, "inputs": False, "output_use": False, "redistribution": False, "review_reference": None},
        "disposition": {"decision": DECISION, "qualifies": False},
    }


def _decl_rejections() -> list[dict]:
    base = unpopulated_asset_declaration()
    cases = []
    def bad(case_id, mut, code, field):
        doc = json.loads(canonical_text(base))
        mut(doc)
        cases.append((case_id, doc, code, field))
    bad("root_not_object", lambda d: None, "not_object", "declaration")
    cases[-1] = ("root_not_object", [], "not_object", "declaration")
    bad("root_missing_schema_id", lambda d: d.pop("schema_id"), "missing_field", "declaration.schema_id")
    bad("missing_declaration_id", lambda d: d.pop("declaration_id"), "missing_field", "declaration.declaration_id")
    bad("extra_top_key", lambda d: d.__setitem__("extra", True), "unknown_field", "declaration.extra")
    bad("bad_schema_id", lambda d: d.__setitem__("schema_id", "x"), "schema_id_mismatch", "schema_id")
    bad("bad_declaration_id", lambda d: d.__setitem__("declaration_id", "Bad"), "invalid_slug", "declaration_id")
    bad("wrong_candidate_name", lambda d: d["candidate"].__setitem__("name", "x"), "candidate_name_mismatch", "candidate.name")
    bad("wrong_candidate_family", lambda d: d["candidate"].__setitem__("family", "x"), "candidate_family_mismatch", "candidate.family")
    bad("named_method_claimed", lambda d: d["candidate"].__setitem__("named_method", "paper"), "unverified_claim", "candidate.named_method")
    bad("method_reference_claimed", lambda d: d["candidate"].__setitem__("method_reference", "https://example"), "unverified_claim", "candidate.method_reference")
    bad("audio_input_false", lambda d: d["candidate"].__setitem__("audio_input", False), "missing_required_value", "candidate.audio_input")
    bad("audio_output_false", lambda d: d["candidate"].__setitem__("audio_output", False), "missing_required_value", "candidate.audio_output")
    bad("source_present_true", lambda d: d["source"].__setitem__("declared_present", True), "unverified_claim", "source.declared_present")
    bad("source_revision_set", lambda d: d["source"].__setitem__("revision", "abc"), "unverified_claim", "source.revision")
    bad("source_license_set", lambda d: d["source"].__setitem__("license_sha256", "0"*64), "unverified_claim", "source.license_sha256")
    bad("source_digest_set", lambda d: d["source"].__setitem__("source_sha256", "0"*64), "unverified_claim", "source.source_sha256")
    bad("weights_present_true", lambda d: d["weights"].__setitem__("declared_present", True), "unverified_claim", "weights.declared_present")
    bad("weights_digest_set", lambda d: d["weights"].__setitem__("weights_sha256", "0"*64), "unverified_claim", "weights.weights_sha256")
    bad("weights_bytes_set", lambda d: d["weights"].__setitem__("byte_count", 1), "unverified_claim", "weights.byte_count")
    bad("runtime_present_true", lambda d: d["runtime"].__setitem__("declared_present", True), "unverified_claim", "runtime.declared_present")
    bad("runtime_python_set", lambda d: d["runtime"].__setitem__("python_version", "3.11.5"), "unverified_claim", "runtime.python_version")
    bad("runtime_platform_set", lambda d: d["runtime"].__setitem__("platform", "linux"), "unverified_claim", "runtime.platform")
    bad("runtime_lock_set", lambda d: d["runtime"].__setitem__("lock_sha256", "0"*64), "unverified_claim", "runtime.lock_sha256")
    bad("geometry_declared_true", lambda d: d["geometry"].__setitem__("declared", True), "unverified_claim", "geometry.declared")
    bad("geometry_rate_set", lambda d: d["geometry"].__setitem__("sample_rate_hz", 16000), "unverified_claim", "geometry.sample_rate_hz")
    bad("geometry_frame_set", lambda d: d["geometry"].__setitem__("frame_samples", 160), "unverified_claim", "geometry.frame_samples")
    bad("geometry_hop_set", lambda d: d["geometry"].__setitem__("hop_samples", 160), "unverified_claim", "geometry.hop_samples")
    bad("geometry_channels_set", lambda d: d["geometry"].__setitem__("channels", 1), "unverified_claim", "geometry.channels")
    bad("rights_code_true", lambda d: d["rights"].__setitem__("code", True), "unverified_claim", "rights.code")
    bad("rights_weights_true", lambda d: d["rights"].__setitem__("weights", True), "unverified_claim", "rights.weights")
    bad("rights_training_true", lambda d: d["rights"].__setitem__("training_data", True), "unverified_claim", "rights.training_data")
    bad("rights_inputs_true", lambda d: d["rights"].__setitem__("inputs", True), "unverified_claim", "rights.inputs")
    bad("rights_output_true", lambda d: d["rights"].__setitem__("output_use", True), "unverified_claim", "rights.output_use")
    bad("rights_redistribution_true", lambda d: d["rights"].__setitem__("redistribution", True), "unverified_claim", "rights.redistribution")
    bad("rights_review_set", lambda d: d["rights"].__setitem__("review_reference", "review"), "unverified_claim", "rights.review_reference")
    bad("qualifies_true", lambda d: d["disposition"].__setitem__("qualifies", True), "unverified_claim", "disposition.qualifies")
    bad("premature_admit", lambda d: d["disposition"].__setitem__("decision", "ADMIT"), "premature_decision", "disposition.decision")
    def missing_weights(d):
        d.pop("weights")
    bad("missing_weights_section", missing_weights, "missing_field", "weights.declared_present")
    bad("extra_geometry_key", lambda d: d["geometry"].__setitem__("bit_depth", 16), "unknown_field", "geometry.bit_depth")
    def float_value(d):
        d["weights"]["byte_count"] = 1.5
    bad("float_value", float_value, "float_not_allowed", "float not allowed in canonical evidence: /weights/byte_count")
    bad("source_not_object", lambda d: d.__setitem__("source", []), "not_object", "source")
    rejections = []
    for case_id, doc, code, field in cases:
        try:
            validate_asset_declaration(doc)
            ok = False
            actual = "accepted"
        except Exception as exc:  # noqa: BLE001
            ok = True
            actual = str(exc)
        rejections.append({"id": case_id, "rejected": ok, "code": code, "field": field, "actual": actual})
    return rejections


STRICT_JSON_CASES = {
    "duplicate_key": '{"a":1,"a":2}',
    "nan_literal": '{"a":NaN}',
    "infinity_literal": '{"a":Infinity}',
    "negative_infinity_literal": '{"a":-Infinity}',
    "trailing_data": '{"a":1} 1',
    "byte_order_mark": '\ufeff{"a":1}',
    "non_object_root": '[]',
    "empty_input": '',
    "unterminated": '{"a":1',
}


def strict_json_rejections() -> list[dict]:
    out = []
    for case_id, payload in STRICT_JSON_CASES.items():
        try:
            loads_strict(payload)
            rejected = False
        except Exception:  # noqa: BLE001
            rejected = True
        out.append({"id": case_id, "rejected": rejected})
    return out


def asset_declaration_schema() -> dict:
    rejections = _decl_rejections()
    strict = strict_json_rejections()
    control = unpopulated_asset_declaration()
    validate_asset_declaration(control)
    return {
        "accepted_control_checks": 31,
        "accepted_control_qualifies": False,
        "accepted_control_sha256": object_digest(control),
        "accepted_control_status": "accepted_unpopulated",
        "all_rejected": all(r["rejected"] for r in rejections),
        "assets_loaded": False,
        "candidate_fields": list(CANDIDATE_FIELDS),
        "disposition_fields": list(DISPOSITION_FIELDS),
        "fields": list(REQUIRED_DECLARATION_FIELDS),
        "geometry_fields": list(GEOMETRY_FIELDS),
        "presence_claims_rejected": True,
        "purpose": "Defines the exact caller-supplied asset declaration a future intake must populate and verify externally. This package accepts only the unpopulated declaration and never resolves or loads an asset.",
        "rejection_cases": len(rejections),
        "rejections": [{"code": r["code"], "field": r["field"], "id": r["id"]} for r in rejections],
        "rights_fields": list(RIGHTS_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "schema_id": DECLARATION_SCHEMA_ID,
        "source_fields": list(SOURCE_FIELDS),
        "strict_json_all_rejected": all(r["rejected"] for r in strict),
        "strict_json_cases": len(strict),
        "strict_json_rejections": strict,
        "weights_fields": list(WEIGHTS_FIELDS),
    }


def exact_blockers() -> list[dict]:
    reopen = "Only a caller-supplied exact artifact with verified identity, terms and matched evidence can reopen this blocker."
    action = "Supply the named artifact and rights evidence at an immutable identity, then reproduce and independently review it."
    rows = [
        ("BLK-01", "RG-01", "ART-02", "No named method or immutable runnable source",
         "The research screens record no named phase-vocoder-with-neural-transient-preservation method, official repository, commit, release tag, source file, licence text or notice at any probed path. The request phrase does not pin a specific implementation."),
        ("BLK-02", "RG-01,RG-03", "ART-03", "No model or checkpoint asset identity",
         "No neural model, transient detector/preservation module, phase-vocoder integration checkpoint, weight or config is named. No file name, revision, byte count, SHA-256 or tensor layout exists, and no weight byte is present or downloaded."),
        ("BLK-03", "RG-02", "ART-04", "No pinned runtime or exact audio task geometry",
         "The candidate family is audio-in/audio-out in principle, but no sample rate, frame, hop, channel, lookahead, latency, device, dtype, interpreter lock, reset or drain contract is documented. The probed interpreter exposes no candidate module."),
        ("BLK-04", "RG-04", "ART-05", "No reviewed rights or training-data terms",
         "No code licence, weight term, training-data statement, attribution bundle, derived-output permission or redistribution decision is staged or reviewed. No rights-cleared speech or music input exists."),
        ("BLK-05", "RG-05,RG-06", "ART-06", "No reproduced rate or output result",
         "No candidate execution, output hash, source/output mapping, duration, pitch, transient, buffering, silence, rebuffer, drift, final-partial or speech-preservation measurement exists. The Rate profile is unsatisfied."),
        ("BLK-06", "RG-07,RG-08", "ART-07", "No matched cohort, listening, timing or release evidence",
         "No rights-cleared matched cohort, same-condition baseline, authorized listening or labeled screen, device timing, resource measurement, benchmark, provider intake or independent review exists."),
    ]
    out = []
    for bid, gates, art, title, stmt in rows:
        out.append({
            "artifact_id": art,
            "id": bid,
            "linked_gates": gates.split(","),
            "qualifies": False,
            "reopen_condition": reopen,
            "required_action": action,
            "statement": stmt,
            "status": "open",
            "title": title,
        })
    return out


def release_gates() -> list[dict]:
    proj = board_row_projection()
    rows = [
        ("RG-01", "named_method_source_revision_and_license_provenance",
         "Name the exact method and stage the official source at an immutable revision with complete licence, notice and README records, then record independent review."),
        ("RG-02", "pinned_runtime_and_offline_install",
         "Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and exact inference settings."),
        ("RG-03", "neural_model_checkpoint_and_weight_assets",
         "Stage every neural transient/model/phase-vocoder integration asset and verify each byte count and SHA-256."),
        ("RG-04", "rights_cleared_inputs_and_training_data",
         "Freeze permitted, digest-pinned speech and music inputs with corpus, evaluation, derived-output and redistribution decisions plus weight and training-data terms."),
        ("RG-05", "reference_execution_and_output_validity",
         "Execute the pinned assets offline and record output hashes, finite and length behaviour, exact repeats and peak/RSS values."),
        ("RG-06", "rate_profile_against_real_runtime",
         "Run every Rate-profile case on a rights-cleared cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window."),
        ("RG-07", "mode_platform_timing_resources_and_listening",
         "Measure each mode and platform separately with timing, resources and pacing, and complete authorized listening or a labeled screen."),
        ("RG-08", "provider_intake_public_surface_and_release",
         "Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear."),
    ]
    return [{
        "id": gid, "linked_row": proj, "qualifies": False,
        "reopen_condition": reopen,
        "statement": "No candidate artifact, runtime, right, matched measurement or review satisfies this requirement.",
        "status": "blocked", "title": title,
    } for gid, title, reopen in rows]


def required_artifacts() -> list[dict]:
    return [
        {"blocked": False, "bytes": None, "id": "ART-01", "kind": "evidence_register_and_policy_boundary", "present": True,
         "requirement": "The linked inventory row, pinned Rate acceptance profile, SDK delivery plan, research findings, task evidence and unchanged v0 contract boundary.", "revision": None, "sha256": None, "verified": True},
        {"blocked": True, "bytes": None, "id": "ART-02", "kind": "named_method_and_upstream_source_snapshot", "present": False,
         "requirement": "A named method with official source at an immutable 40-hex commit or release tag, reviewed licence text, README, model/API definitions and a per-file SHA-256 manifest.", "revision": None, "sha256": None, "verified": False},
        {"blocked": True, "bytes": None, "id": "ART-03", "kind": "neural_transient_and_phase_vocoder_assets", "present": False,
         "requirement": "Every neural transient-preservation model, checkpoint, phase-vocoder integration module and inference config with exact names, revision, byte counts, SHA-256 values and tensor layout.", "revision": None, "sha256": None, "verified": False},
        {"blocked": True, "bytes": None, "id": "ART-04", "kind": "pinned_runtime_and_exact_streaming_geometry", "present": False,
         "requirement": "A locked offline runtime with interpreter, package versions, wheel hashes, platform, device, dtype, determinism settings and install location, plus sample rate, channel, frame, hop, lookahead, latency, reset and drain behaviour.", "revision": None, "sha256": None, "verified": False},
        {"blocked": True, "bytes": None, "id": "ART-05", "kind": "rights_cleared_inputs_and_training_data", "present": False,
         "requirement": "Code, weight, training-data and derived-output terms plus a digest-pinned, rights-cleared speech and music input set with consent, acquisition, evaluation and redistribution decisions.", "revision": None, "sha256": None, "verified": False},
        {"blocked": True, "bytes": None, "id": "ART-06", "kind": "reproduced_rate_and_output_results", "present": False,
         "requirement": "Deterministic reproduced output on the exact runtime with source/output mapping, duration, pitch, transient, buffering, silence, rebuffer, drift, final-partial and preservation results.", "revision": None, "sha256": None, "verified": False},
        {"blocked": True, "bytes": None, "id": "ART-07", "kind": "provider_intake_and_public_surface", "present": False,
         "requirement": "A separate versioned OFF-by-default provider intake with clean-install proof, empty defaults, no shared-build change and independent exact-head review.", "revision": None, "sha256": None, "verified": False},
    ]


def task_geometry() -> dict:
    return {
        "audio_input_expected": True,
        "audio_input_path_verified": False,
        "audio_only_controller": False,
        "candidate_family": CANDIDATE_FAMILY,
        "channels": None,
        "dtype": None,
        "frame_samples": None,
        "geometry_documented": False,
        "geometry_verified": False,
        "hop_samples": None,
        "latency_ms": None,
        "named_method_found": False,
        "profile_fit_reason": "The catalogued candidate family is an audio-in/audio-out time-scale modification, which matches the Rate profile in principle. No named method, repository, model, streaming contract, rate/frame/hop geometry or lookahead is documented, so the fit cannot be verified.",
        "rate_only_estimator": False,
        "rate_profile_fit": "unverified",
        "sample_rate_hz": None,
        "source_reported_input": "audio waveform (candidate-family expectation)",
        "source_reported_output": "time-scaled audio waveform with transient preservation (candidate-family expectation)",
        "state": TASK_GEOMETRY_STATE,
    }


def source_reported_identity() -> dict:
    return {
        "audio_input": True,
        "audio_output": True,
        "candidate": CANDIDATE_NAME,
        "candidate_family": CANDIDATE_FAMILY,
        "identity_verified": False,
        "immutable_revision_recorded": False,
        "license_recorded": False,
        "license_text_staged": False,
        "method_reference": METHOD_REFERENCE,
        "model_card_staged": False,
        "named_method": None,
        "named_method_found": False,
        "official_code_found": False,
        "official_weights_found": False,
        "paper_reference_recorded": False,
        "runnable_as_released": False,
        "source_reported_baseline": "Rubber Band phase vocoder; WSOLA",
        "source_reported_only": True,
        "source_reported_stages": ["phase_vocoder_analysis_synthesis", "neural_transient_detection_or_preservation"],
        "source_reported_task": "neural transient-preserving phase vocoder time-scale modification",
        "venue": None,
    }


def scope() -> dict:
    return {
        "benchmark_claim": False,
        "board_or_handoff_change": False,
        "candidate_code_downloaded": False,
        "candidate_code_vendored": False,
        "candidate_runtime_executed": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "device_timing": False,
        "listening": False,
        "model_weights_downloaded": False,
        "model_weights_vendored": False,
        "network_access": False,
        "peer_evidence_inherited": False,
        "processed_output_present": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "public_default": False,
        "real_audio": False,
        "release_claim": False,
        "runtime_invoked": False,
        "shared_build_or_ci_change": False,
        "synthetic_speech": False,
        "task_local_only": True,
        "write_scope": WRITE_SCOPE,
    }


def build_contract() -> dict:
    return {
        "base_commit": BASE_COMMIT,
        "boundary": boundary(),
        "branch": BRANCH,
        "candidate_name": CANDIDATE_NAME,
        "component": COMPONENT_ID,
        "contract_id": CONTRACT_ID,
        "decision": DECISION,
        "depends_on": list(DEPENDS_ON),
        "disposition": DECISION,
        "evidence_record": EVIDENCE_RECORD,
        "exact_blockers": exact_blockers(),
        "expected_dir_files": sorted(EXPECTED_DIR_FILES),
        "mode": MODE,
        "non_claims": list(NON_CLAIMS),
        "profile": PROFILE,
        "qualification_status": QUALIFICATION_STATUS,
        "rate_profile": rate_profile(),
        "release_gates": release_gates(),
        "required_artifacts": required_artifacts(),
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": scope(),
        "source_reported_identity": source_reported_identity(),
        "status": STATUS,
        "task": TASK,
        "task_geometry": task_geometry(),
        "title": TASK_TITLE,
        "write_scope": WRITE_SCOPE,
    }


def boundary() -> dict:
    return {
        "adapter_json_added": False,
        "audio_added": False,
        "board_file_pinned": False,
        "board_or_handoff_changed": False,
        "candidate_code_vendored": False,
        "corpus_added": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "excluded_mutable_fields": ["status", "owner", "claim", "review", "handoff", "blocked_reason", "dispatch_priority"],
        "installed_v0_behavior_change": False,
        "linked_row": board_row_projection(),
        "linked_row_identity_only": True,
        "linked_row_sha256": board_row_digest(),
        "linked_rows": [dict(r) for r in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
        "mutable_board_fields_gate": False,
        "native_engine_built": False,
        "processed_output_added": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "runtime_imported": False,
        "shared_build_or_ci_change": False,
        "weights_vendored": False,
    }


def matched_evidence() -> dict:
    return {
        "candidate_profile_fit": "unverified",
        "classes_pooled": False,
        "evidence_classes": ["source_reported_candidate_screen", "source_reported_artifact_review", "missing_named_method_and_result", "separate_classical_phase_vocoder_control", "separate_sibling_neural_candidate", "unchanged_v0_contract"],
        "listening_or_labeled_screen_present": False,
        "matched_baseline_present": False,
        "matched_cohort_present": False,
        "paired_clean_reference_present": False,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "required_separation": "Source-reported prose, schema-only declarations, missing real measurements, classical phase-vocoder/Rubber Band/atempo controls and sibling neural candidates stay in distinct sections and are never pooled.",
        "same_condition_control_present": False,
        "source_output_mapping_present": False,
        "synthetic_schema_control_counted_as_result": False,
    }


def exact_scope() -> dict:
    return {
        "adapter_files_changed": False,
        "board_or_handoff_changed": False,
        "candidate_code_weights_or_audio_committed": False,
        "cmake_or_ci_changed": False,
        "contracts_header_changed": False,
        "default_selection_changed": False,
        "descriptor_or_registry_changed": False,
        "only_task_directory_written": True,
        "provider_files_changed": False,
        "task_prefix": TASK_PREFIX,
        "write_scope": WRITE_SCOPE,
    }


def public_v0_geometry() -> dict:
    return {
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "candidate_mapping_present": False,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
        "unchanged": True,
    }


def build_report() -> dict:
    contract = build_contract()
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "absence_summary": absence_probes(),
        "asset_declaration": {
            "accepted_unpopulated": unpopulated_asset_declaration(),
            "schema": asset_declaration_schema(),
        },
        "base_commit": BASE_COMMIT,
        "boundary": boundary(),
        "branch": BRANCH,
        "component": COMPONENT_ID,
        "contract_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "contract_sha256": object_digest(contract),
        "decision": DECISION,
        "depends_on": list(DEPENDS_ON),
        "disposition": {
            "candidate_artifact_present": False,
            "decision": DECISION,
            "evidence_status": STATUS,
            "incomplete": True,
            "output_present": False,
            "proposal_only": True,
            "qualification_status": QUALIFICATION_STATUS,
            "result_promoted": False,
            "rights_cleared_input_present": False,
            "runtime_present": False,
            "status": STATUS,
            "summary": "Phase vocoder with neural transient preservation is catalogued as an unavailable/blocked neural TSM candidate family. Locally absent and unverified: a named method, official source, checkpoint, runtime, exact audio geometry, terms, rights-cleared inputs, matched cohort, output and rate result. Classical phase-vocoder, Rubber Band and atempo controls are separate and not substituted.",
            "task_mode": MODE,
        },
        "evidence_record": EVIDENCE_RECORD,
        "evidence_snippets": evidence_snippets(),
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": exact_blockers(),
        "exact_scope": exact_scope(),
        "historical_evidence": list(HISTORICAL_EVIDENCE),
        "incomplete": True,
        "linked_row": projection,
        "linked_row_sha256": board_row_digest(projection),
        "linked_rows": [dict(r) for r in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "matched_evidence": matched_evidence(),
        "mode": MODE,
        "non_claims": list(NON_CLAIMS),
        "peer_separation": list(PEER_SEPARATION),
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "proposal_only": True,
        "public_v0_geometry": public_v0_geometry(),
        "qualification_status": QUALIFICATION_STATUS,
        "rate_profile": rate_profile(),
        "release_gates": release_gates(),
        "required_artifacts": required_artifacts(),
        "schema_id": REPORT_SCHEMA_ID,
        "scope": scope(),
        "source_reported_identity": source_reported_identity(),
        "status": STATUS,
        "task": TASK,
        "task_geometry": task_geometry(),
        "title": TASK_TITLE,
        "write_scope": WRITE_SCOPE,
    }


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
        rows.append((relative, actual))
    for name in LOCAL_FILES:
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((TASK_PREFIX + name, sha256_file(path)))
    lines = [
        "# SHA-256 pins for SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION evidence.",
        "# source: paths are relative to AUDIO_ROOT; other paths are SDK-worktree relative.",
        "# The mutable shared board is not pinned; only its stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def update_readme_tables(text: str) -> str:
    def replace(section: str, payload: str) -> str:
        start, end = README_MARKERS[section]
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        if not pattern.search(text):
            raise ValueError("readme_marker_missing:" + section)
        return pattern.sub(start + "\n" + payload.rstrip() + "\n" + end, text, count=1)

    source_rows = ["| Path | SHA-256 |", "| --- | --- |"]
    for rel, digest in sorted(SOURCE_PINS.items()):
        source_rows.append(f"| `source:{rel}` | `{digest}` |")
    boundary_rows = ["| Path | SHA-256 |", "| --- | --- |"]
    for rel, digest in sorted(BOUNDARY_PINS.items()):
        boundary_rows.append(f"| `{rel}` | `{digest}` |")
    artifact_rows = ["| Path | SHA-256 |", "| --- | --- |"]
    for name in sorted(EXPECTED_DIR_FILES - ARTIFACT_TABLE_EXCLUDED):
        artifact_rows.append(f"| `{TASK_PREFIX}{name}` | `{sha256_file(HERE / name)}` |")
    text = replace("source", "\n".join(source_rows))
    text = replace("boundary", "\n".join(boundary_rows))
    text = replace("artifacts", "\n".join(artifact_rows))
    return text


def verify_readme_digests(text: str) -> dict[str, int]:
    counts = {}
    for section in README_SECTIONS:
        start, end = README_MARKERS[section]
        match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)
        if not match:
            raise ValueError("readme_marker_missing:" + section)
        rows = [line for line in match.group(1).splitlines() if line.startswith("| `")]
        for row in rows:
            cols = [c.strip() for c in row.strip("|").split("|")]
            if len(cols) != 2:
                raise ValueError("readme_row_malformed:" + section)
            path = cols[0].strip("` ")
            digest = cols[1].strip("` ")
            if not HEX64.match(digest):
                raise ValueError("readme_digest_malformed:" + path)
            if path.startswith("source:"):
                fs = AUDIO_ROOT / path[len("source:"):]
            elif path.startswith(TASK_PREFIX):
                fs = HERE / path[len(TASK_PREFIX):]
            else:
                fs = WORKTREE / path
            if not fs.is_file() or sha256_file(fs) != digest:
                raise ValueError("readme_digest_mismatch:" + path)
        counts[section] = len(rows)
    return counts


def has_forbidden_suffix(path: Path) -> bool:
    return path.suffix.lower() in FORBIDDEN_SUFFIXES


def main() -> int:
    text, digest = canonical_report()
    print(text)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
