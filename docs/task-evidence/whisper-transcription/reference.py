# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence for SDK-WHISPER-TRANSCRIPTION.

Standard library only. This package records a developer/evidence-only
comparison boundary for Whisper transcription scoring in the voice-conversion
evaluation: frozen decoding and transcript normalization for WER, no streaming
ASR claim, no processor exposure, no provider registration, no public API/ABI
change, no real audio, no listening, no device timing, no benchmark and no
release claim.

It pins the cited research artifacts by SHA-256, validates absence of
task-local runtime/model/audio execution claims, enforces fail-closed scope and
README digest checks, and emits canonical DEFER/incomplete/not_qualified
report bytes.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-WHISPER-TRANSCRIPTION"
TASK_TITLE = "Whisper transcription"
COMPONENT_ID = "whisper-transcription"
REPOSITORY = "audio-sdk"
MODE = "research-control"
PROFILE = "evidence"
PROFILE_LABEL = "Evidence"
STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/whisper-transcription/ only"
TASK_PREFIX = "docs/task-evidence/whisper-transcription/"
CONTRACT_ID = "audio-sdk/whisper-transcription-evidence/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/whisper-transcription-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/whisper-transcription-report/0.1"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-WHISPER-TRANSCRIPTION"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
REQUIRED_INTERPRETER = "3.12.16"

HEX64 = re.compile(r"^[0-9a-f]{64}$")

HERE = Path(__file__).resolve().parent
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
WORKTREE = Path(os.environ.get("SDK_WORKTREE", str(HERE.parents[2]))).resolve()
SDK_ROOT = WORKTREE

# Read-only inputs. source: paths are workspace-relative; sdk: paths are
# SDK-worktree-relative. The mutable shared board is never pinned.
SOURCE_PINS = {
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/scripts/score_conversion.py":
        "d5e351c7e33645eb54ec30c23fa14f8c228bb628898856eaa94a4263c6cfbdbd",
    "research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py":
        "d268eb6dca48f88ae03802efd566f7053ac375be82555bd3dac343d750a5488c",
    "research/voice-conversion-eval-20261101/results/source_asr.json":
        "890e2e5c5000a9251142881645eb1fc406861e740cd84e12d556b3830999035c",
    "research/voice-conversion-eval-20261101/results/llvc_asr.json":
        "2d8f31e91ea06efed6611a0aa41edf2babb08625a2da22fe30f4333554115c41",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md":
        "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
}

# Fixed absence probes. No recursive walk, no network, no download.
WORKSPACE_PROBES = (
    "data/models/whisper-transcription",
    "data/models/openai-whisper",
    "data/runs/whisper-transcription",
    "research/voice-conversion-eval-20261101/data/tmp-whisper-transcription",
)

WORKTREE_PROBES = (
    "adapters/whisper-transcription",
    "schemas/providers/whisper-transcription",
    "third_party/whisper-transcription",
    "tools/whisper-transcription",
)

HOME_PROBES = (
    "~/.cache/whisper",
    "~/.cache/huggingface/hub/models--openai--whisper-tiny.en",
)

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".joblib", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".tar", ".tar.gz", ".tgz", ".wasm", ".wav", ".weights", ".zip",
}

EXPECTED_DIR_FILES = {
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
}

LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
SCOPE_BASE_REFS = ("origin/main", "main")


# ---------------------------------------------------------------------------
# Strict JSON/canonical helpers
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text(value: Any) -> str:
    assert_no_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def assert_no_float(value: Any, path: str = "$") -> None:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, float):
        raise TypeError("float_forbidden:" + path)
    if isinstance(value, int):
        return
    if isinstance(value, str):
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            assert_no_float(item, path + "[" + str(i) + "]")
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise TypeError("key_not_string:" + path)
            assert_no_float(v, path + "." + k)
        return
    raise TypeError("unsupported_type:" + path + ":" + type(value).__name__)


class _StrictDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["parse_float"] = self._reject_float
        kwargs["parse_constant"] = self._reject_constant
        kwargs["object_pairs_hook"] = self._reject_duplicates
        super().__init__(*args, **kwargs)

    @staticmethod
    def _reject_float(value: str) -> Any:
        raise ValueError("float_not_allowed:" + value)

    @staticmethod
    def _reject_constant(value: str) -> Any:
        raise ValueError("nonfinite_not_allowed:" + value)

    @staticmethod
    def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate_key:" + key)
            out[key] = value
        return out


def loads_strict(text: str) -> Any:
    if text.startswith("\ufeff"):
        raise ValueError("bom_not_allowed")
    if not text.strip():
        raise ValueError("empty_json")
    value = json.loads(text, cls=_StrictDecoder)
    if not isinstance(value, dict):
        raise ValueError("top_level_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> Any:
    return loads_strict(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Git/scope helpers
# ---------------------------------------------------------------------------

def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


# ---------------------------------------------------------------------------
# Stable board identity
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
    return tuple(result)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None
                         else board_row_projection())


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


# ---------------------------------------------------------------------------
# Probes and evidence
# ---------------------------------------------------------------------------

def _probe(path: Path, label: str, workspace: bool, worktree: bool,
           home: bool) -> dict:
    return {
        "path": label,
        "present": path.exists(),
        "searched_workspace": workspace,
        "searched_sdk_worktree": worktree,
        "searched_home_cache": home,
    }


def all_probes() -> list[dict]:
    rows = [_probe(AUDIO_ROOT / p, p, True, False, False) for p in WORKSPACE_PROBES]
    rows += [_probe(WORKTREE / p, p, False, True, False) for p in WORKTREE_PROBES]
    rows += [_probe(Path(p).expanduser(), p, False, False, True) for p in HOME_PROBES]
    return rows


def absence_summary(probes: list[dict] | None = None) -> dict:
    rows = all_probes() if probes is None else probes
    return {
        "probe_count": len(rows),
        "workspace_probe_count": sum(1 for r in rows if r["searched_workspace"]),
        "worktree_probe_count": sum(1 for r in rows if r["searched_sdk_worktree"]),
        "home_probe_count": sum(1 for r in rows if r["searched_home_cache"]),
        "present_count": sum(1 for r in rows if r["present"] is not False),
        "all_absent": all(r["present"] is False for r in rows),
        "probes": rows,
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "model_executed": False,
        "weights_loaded": False,
        "audio_read": False,
        "listening_performed": False,
        "device_timing_measured": False,
        "benchmark_claimed": False,
    }


def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows: list[dict] = []
    for relative in sorted(pins):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        rows.append({
            "path": relative,
            "sha256": pins[relative],
            "actual": actual,
            "verified": actual == pins[relative],
        })
    return rows


def _read_json_loose(path: Path) -> Any:
    # Source-pinned research artifacts may contain floats; evidence checks only.
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_snippet_check() -> dict:
    checks = []
    readme = (AUDIO_ROOT / "research/voice-conversion-eval-20261101/README.md").read_text(encoding="utf-8")
    scorer = (AUDIO_ROOT / "research/voice-conversion-eval-20261101/scripts/score_conversion.py").read_text(encoding="utf-8")
    llvc = (AUDIO_ROOT / "research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py").read_text(encoding="utf-8")
    source_asr = _read_json_loose(AUDIO_ROOT / "research/voice-conversion-eval-20261101/results/source_asr.json")
    llvc_asr = _read_json_loose(AUDIO_ROOT / "research/voice-conversion-eval-20261101/results/llvc_asr.json")
    inv = _read_json_loose(AUDIO_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
    ver = (AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md").read_text(encoding="utf-8")

    checks.append({"id": "readme_whisper_tiny_en", "present": "openai/whisper-tiny.en" in readme})
    checks.append({"id": "readme_frozen_wer_note", "present": "frozen decoding and transcript normalization for WER; no streaming ASR claim from scoring" in json.dumps(inv)})
    checks.append({"id": "scorer_normalize", "present": "re.findall(r\"[a-z0-9']+\", text.lower())" in scorer})
    checks.append({"id": "scorer_wer", "present": "def word_error_rate(reference: str, hypothesis: str) -> float:" in scorer})
    checks.append({"id": "scorer_whisper_pipeline", "present": 'model="openai/whisper-tiny.en"' in scorer})
    checks.append({"id": "llvc_eval_runs_infer", "present": "infer.main()" in llvc and "--stream" in llvc})
    checks.append({"id": "source_asr_wer_recorded", "present": source_asr.get("wer") == 0.037037037037037035})
    checks.append({"id": "llvc_asr_wer_recorded", "present": llvc_asr.get("wer") == 0.0})
    checks.append({"id": "evidence_profile_present", "present": "| Evidence |" in ver})
    checks.append({"id": "inventory_profile_evidence", "present": any(
        r.get("id") == "whisper-transcription" and r.get("verification_profile") == "evidence"
        for r in (inv.get("records", inv.get("components", [])) if isinstance(inv, dict) else []))})
    return {"count": len(checks), "all_present": all(c["present"] for c in checks), "checks": checks}


# ---------------------------------------------------------------------------
# README digest validation
# ---------------------------------------------------------------------------

def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    tables: dict[str, list[tuple[str, str]]] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            current = line[3:].strip().lower()
            tables.setdefault(current, [])
            continue
        if not line.startswith("|") or current is None:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if all(set(cell) <= {"-", ":"} and cell for cell in cells):
            continue
        if cells[0].lower() in {"path", "input", "file"}:
            continue
        digest = cells[-1].strip("` ")
        if HEX64.fullmatch(digest):
            tables[current].append((cells[0].strip("` "), digest))
    return tables


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    counts: dict[str, int] = {}
    for section, key in (("source pins", "source"), ("boundary pins", "boundary")):
        rows = parsed.get(section, [])
        if not rows:
            raise ValueError("readme_digest_table_missing:" + section)
        counts[key] = len(rows)
        for path_text, digest in rows:
            if key == "source":
                path = AUDIO_ROOT / path_text
            else:
                path = SDK_ROOT / path_text
            if not path.is_file():
                raise ValueError("readme_digest_missing_file:" + path_text)
            actual = sha256_file(path)
            if actual != digest:
                raise ValueError("readme_digest_mismatch:" + path_text)
    return counts


# ---------------------------------------------------------------------------
# Report/contract build
# ---------------------------------------------------------------------------

def _local_manifest_paths() -> list[str]:
    return sorted(p.name for p in HERE.iterdir()
                  if p.is_file() and p.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for rel, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + rel))
    for rel, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + rel))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable linked-row projection is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for digest, name in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def build_contract() -> dict:
    projection = board_row_projection()
    linked = linked_rows()
    absence = absence_summary()
    snippets = evidence_snippet_check()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "depends_on": list(DEPENDS_ON),
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "status": STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "write_scope": WRITE_SCOPE,
        "linked_row": projection,
        "linked_row_sha256": board_row_digest(projection),
        "linked_rows": list(linked),
        "linked_rows_sha256": linked_rows_digest(linked),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, SDK_ROOT),
        "absence_summary": absence,
        "evidence_snippets": snippets,
        "gates": [
            {"id": "RG-01", "status": "blocked", "qualifies": False,
             "summary": "No frozen Whisper transcription adapter/runtime is staged in this task-local package; cited ASR use remains external research evidence only.",
             "reopen_condition": "Stage a reviewed, pinned, opt-in Whisper transcription developer/evidence adapter with frozen decoding, transcript normalization, and exact-head review; keep it OFF/unregistered."},
            {"id": "RG-02", "status": "blocked", "qualifies": False,
             "summary": "No rights-cleared, pinned audio/corpus/license bundle for Whisper transcription scoring is present.",
             "reopen_condition": "Provide pinned rights-reviewed inputs/corpus/license metadata and deterministic fixture manifests."},
            {"id": "RG-03", "status": "blocked", "qualifies": False,
             "summary": "No deterministic task-local conformance run or invalid/missing-case bundle for Whisper transcription scoring is present.",
             "reopen_condition": "Add deterministic valid/invalid/missing conformance cases with exact command, digest, and fail-closed handling."},
            {"id": "RG-04", "status": "blocked", "qualifies": False,
             "summary": "No device/runtime timing, streaming ASR, or real-time claim evidence is present; this package records scoring evidence only.",
             "reopen_condition": "Add separate measured runtime/timing evidence with explicit scope; do not infer streaming behavior from WER scoring."},
            {"id": "RG-05", "status": "blocked", "qualifies": False,
             "summary": "No independent review, hosted CI evidence, or release decision is present.",
             "reopen_condition": "Obtain exact-head independent review, hosted CI, and explicit release decision before any exposure."},
        ],
        "blockers": [
            {"id": "BLK-01", "status": "open", "qualifies": False, "gate": "RG-01",
             "summary": "No in-worktree Whisper transcription adapter/runtime package; evidence is external research-only."},
            {"id": "BLK-02", "status": "open", "qualifies": False, "gate": "RG-02",
             "summary": "No rights-cleared pinned audio/corpus/license bundle for transcription scoring."},
            {"id": "BLK-03", "status": "open", "qualifies": False, "gate": "RG-03",
             "summary": "No deterministic task-local conformance bundle for valid/invalid/missing transcription scoring cases."},
            {"id": "BLK-04", "status": "open", "qualifies": False, "gate": "RG-04",
             "summary": "No measured device/runtime timing or streaming-ASR evidence; WER scoring is not a streaming claim."},
            {"id": "BLK-05", "status": "open", "qualifies": False, "gate": "RG-05",
             "summary": "No independent review/hosted CI/release decision."},
        ],
        "non_claims": [
            "no provider registration",
            "no default enablement",
            "no public API/ABI change",
            "no CONTRACTS change",
            "no shared build/CI behavior change",
            "no real audio processed by this package",
            "no listening claim",
            "no device timing claim",
            "no benchmark claim",
            "no streaming ASR claim",
            "no release claim",
        ],
    }


def build_report(contract: dict | None = None) -> dict:
    contract = build_contract() if contract is None else contract
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "status": STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "claim_eligible": False,
        "release_claim_eligible": False,
        "contract_digest": object_digest(contract),
        "linked_row": contract["linked_row"],
        "linked_row_sha256": contract["linked_row_sha256"],
        "linked_rows": contract["linked_rows"],
        "linked_rows_sha256": contract["linked_rows_sha256"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "absence_summary": contract["absence_summary"],
        "evidence_snippets": contract["evidence_snippets"],
        "gates": contract["gates"],
        "blockers": contract["blockers"],
        "non_claims": contract["non_claims"],
        "scope": {
            "task_write_scope_only": True,
            "task_local_only": True,
            "provider_registered": False,
            "default_enabled": False,
            "public_api_changed": False,
            "abi_changed": False,
            "contracts_changed": False,
            "shared_build_changed": False,
            "ci_behavior_changed": False,
        },
    }
    assert_no_float(report)
    return report


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))
