# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-F5-TTS.

This module never loads a model, imports an upstream package, reads audio, runs
inference, scores quality, performs listening, measures a device or produces a
release claim. The exact F5-TTS source, weights and runtime are absent. The
module pins stable read-only inputs, proves the fixed absence probes, exercises
a fail-closed synthetic cohort-admission contract and emits canonical JSON.
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
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/f5-tts/"

TASK = "SDK-F5-TTS"
TASK_TITLE = "F5-TTS"
COMPONENT_ID = "f5-tts"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "voice"
PROFILE_KEY = "Voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/f5-tts-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/f5-tts-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/f5-tts-report/0.1"
BASE_COMMIT = "23526250a3a0a66c1f93089ff6fb697b5e776965"
BRANCH = "swarm/SDK-F5-TTS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to AUDIO_ROOT; boundary
# paths are SDK-worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
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
    "Freeze permitted input and target references",
    "Preserve text and semantic content",
    "identity/similarity",
    "naturalness as separate outcomes",
    "Record alignment, first-output/tail timing",
    "exact target condition",
    "Consent, reference availability and output use are independent gates",
)

# ---------------------------------------------------------------------------
# Exact upstream identity requirements. No revision, digest or file name is
# asserted as present or verified; these are the missing-artifact requirements.
# ---------------------------------------------------------------------------

SOURCE_REPOSITORY = "https://github.com/SWivid/F5-TTS"
MODEL_REPOSITORY = "https://huggingface.co/SWivid/F5-TTS"
MODEL_VARIANT_EXAMPLE = "F5TTS_v1_Base"
UPSTREAM_SAMPLE_RATE_HZ = 24_000

SOURCE_PROBE_PATHS = (
    "research/voice-conversion-eval-20261101/repos/f5-tts",
    "research/voice-conversion-eval-20261101/repos/F5-TTS",
    "research/voice-conversion-eval-20261101/repos/f5_tts",
    "research/f5-tts",
    "research/F5-TTS",
)
WEIGHTS_PROBE_PATHS = (
    "research/voice-conversion-eval-20261101/models/f5-tts",
    "research/voice-conversion-eval-20261101/models/F5-TTS",
    "research/models/f5-tts",
)
RUNTIME_PROBE_PATHS = (
    "research/voice-conversion-eval-20261101/envs/f5-tts",
    "research/voice-conversion-eval-20261101/.venv-f5-tts",
    ".venv-f5-tts",
)
HOME_PROBE_PATHS = (
    "~/.cache/huggingface/hub/models--SWivid--F5-TTS",
    "~/.cache/huggingface/hub/models--SWivid--F5-TTS-v1-Base",
    "~/.cache/huggingface/hub/models--SWivid--F5-TTS-Base",
    "~/.cache/huggingface/hub/models--SWivid--E2-TTS",
    "~/.venvs/f5-tts",
    "~/.local/share/f5-tts",
)
SOURCE_ROOT_REL = "research/voice-conversion-eval-20261101/repos"

NON_CLAIMS = [
    "No F5-TTS source copy, checkpoint, weight fragment, config, vocab or "
    "tokenizer asset, runtime, reference voice, generated waveform or vendor "
    "result is present, loaded, linked or executed by this package.",
    "No model inference, text normalization, audio read, audio write, "
    "listening, reference-similarity scoring, naturalness scoring, alignment, "
    "first-output/tail measurement or device timing is performed.",
    "No real corpus, consented reference voice, manual transcript, language or "
    "speaker group, target condition or held-out split is used here.",
    "No missing, invalid, nonfinite or adverse manifest case qualifies; the "
    "single accepted synthetic schema control is not evidence.",
    "No adjacent chatterbox-nano, CosyVoice, Kokoro, NeuTTS, vocoder or survey "
    "result is inherited, pooled or promoted to F5-TTS.",
    "No benchmark, quality, latency, resource, streaming or release claim is "
    "made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; the absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "chatterbox-nano",
        "task": "SDK-CHATTERBOX-NANO",
        "path": "docs/task-evidence/chatterbox-nano/report.json",
        "class": "adjacent_reference_conditioned_tts",
        "decision": "DEFER",
        "status": "incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Adjacent reference-conditioned whole-utterance TTS on a "
                    "different model; no weights, runtime, consent, identity, "
                    "naturalness or device timing is inherited.",
    },
    {
        "component": "cosyvoice-2-0-5b",
        "task": "SDK-COSYVOICE-2-0-5B",
        "path": "docs/task-evidence/cosyvoice-2-0-5b/report.json",
        "class": "adjacent_zero_shot_streaming_tts",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Adjacent zero-shot streaming TTS with absent weights; its "
                    "historical chunk timing is provenance only and is not an "
                    "F5-TTS first-output or device result.",
    },
    {
        "component": "kokoro-82m",
        "task": "SDK-KOKORO-82M",
        "path": "docs/task-evidence/kokoro-82m/report.json",
        "class": "fixed_voice_tts_control",
        "decision": "DEFER",
        "status": "incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A fixed-preset text-only control, not reference-conditioned "
                    "cloning; no identity, naturalness or timing is inherited.",
    },
    {
        "component": "neutts-nano-q4",
        "task": "SDK-NEUTTS-NANO-Q4",
        "path": "docs/task-evidence/neutts-nano-q4/report.json",
        "class": "gated_checkpoint_tts",
        "decision": "DEFER",
        "status": "incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A gated checkpoint lead with no authenticated access or "
                    "inference; it is not a substitute F5-TTS checkpoint.",
    },
    {
        "component": "phase-vocoder-baseline",
        "task": "SDK-PHASE-VOCODER-BASELINE",
        "path": "docs/task-evidence/phase-vocoder-baseline/report.json",
        "class": "vocoder_component_control",
        "decision": "defer",
        "status": "component_control_report",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A vocoder component needs acoustic features and does not "
                    "independently synthesize reference-conditioned speech.",
    },
    {
        "component": "reference-conditioned-voice-cloning-tts-evidence-map",
        "task": "SDK-SURVEY-TRN-05",
        "path": "docs/task-evidence/survey-trn-05/report.json",
        "class": "merged_survey_map",
        "decision": "DEFER",
        "status": "proposal_only_survey_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "The merged survey records F5-TTS as a considered source "
                    "lead only; it supplies no checkpoint, runtime, cohort or "
                    "measured result.",
    },
)

VOICE_REQUIREMENTS = (
    {
        "id": "VOI-01",
        "requirement": "Freeze permitted input and target references, task and "
                       "language/speaker groups.",
        "status": "blocked",
        "evidence": "No F5-TTS source, checkpoint, consent record, reference "
                    "voice, language group or speaker group is present.",
    },
    {
        "id": "VOI-02",
        "requirement": "Preserve text and semantic content.",
        "status": "blocked",
        "evidence": "No manual transcript, semantic-content adjudication or "
                    "reproduced content-preservation result exists.",
    },
    {
        "id": "VOI-03",
        "requirement": "Measure identity/similarity as a separate outcome.",
        "status": "blocked",
        "evidence": "No reference-voice similarity score, independent speaker "
                    "encoder or human identity rating exists.",
    },
    {
        "id": "VOI-04",
        "requirement": "Measure naturalness as a separate outcome.",
        "status": "blocked",
        "evidence": "No naturalness rating, blinded listening or preference "
                    "panel exists.",
    },
    {
        "id": "VOI-05",
        "requirement": "Record alignment.",
        "status": "blocked",
        "evidence": "No word, phoneme, onset or reference-content alignment "
                    "measurement exists.",
    },
    {
        "id": "VOI-06",
        "requirement": "Record first-output and tail timing.",
        "status": "blocked",
        "evidence": "No pinned runtime or causal output path exists, so no "
                    "first-output, tail or sample-count result is measured.",
    },
    {
        "id": "VOI-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": "No reference-voice specification, reference-text policy, "
                    "language condition or target condition is cleared.",
    },
    {
        "id": "VOI-08",
        "requirement": "Keep consent, reference availability and output use as "
                       "independent gates.",
        "status": "blocked",
        "evidence": "Weight terms, training-data provenance, reference-voice "
                    "consent, reference availability and output use are "
                    "unresolved.",
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


# The scope comparison uses the newest merge-base between HEAD and an available
# PR base ref, so unrelated packages merged into main after this branch forked do
# not count as this branch's edits. Uncommitted changes are still caught by the
# dirty/untracked status gate and this diff still catches committed edits.
SCOPE_BASE_REFS = ("origin/main", "main")


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
        "candidates": _workspace_rows(SOURCE_PROBE_PATHS, "source"),
    }


def weights_probe() -> dict:
    home_cache = "~/.cache/huggingface/hub/models--SWivid--F5-TTS"
    cache_path = Path(os.path.expanduser(home_cache))
    if cache_path.exists():
        raise ValueError("artifact_present_reopen_required:" + home_cache)
    return {
        "status": "blocked_exact_model_bundle_absent",
        "pinned_model_present": False,
        "admitted_model": None,
        "present_file_count": 0,
        "model_repository": MODEL_REPOSITORY,
        "model_variant_requirement": MODEL_VARIANT_EXAMPLE,
        "candidates": _workspace_rows(WEIGHTS_PROBE_PATHS, "weights"),
        "hf_cache": {
            "path": home_cache,
            "present": False,
            "admitted": False,
            "opened": False,
        },
        "files": [
            {"kind": "checkpoint_weights", "present": False, "admitted": False},
            {"kind": "config", "present": False, "admitted": False},
            {"kind": "vocab_tokenizer", "present": False, "admitted": False},
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
        "required_runtime": "caller-supplied locked interpreter; exact version "
                            "and package set are not asserted here",
        "candidates": _workspace_rows(RUNTIME_PROBE_PATHS, "runtime"),
        "home_candidates": _home_rows(
            ("~/.venvs/f5-tts", "~/.local/share/f5-tts")),
    }


def absence_probes() -> list[dict]:
    rows = []
    rows.extend(_workspace_rows(SOURCE_PROBE_PATHS, "source"))
    rows.extend(_workspace_rows(WEIGHTS_PROBE_PATHS, "weights"))
    rows.extend(_workspace_rows(RUNTIME_PROBE_PATHS, "runtime"))
    rows.extend(_home_rows(HOME_PROBE_PATHS))
    return rows


def absence_summary(probes: list[dict]) -> dict:
    return {
        "probe_count": len(probes),
        "present_count": sum(1 for row in probes if row.get("present") is not False),
        "all_probes_absent": all(row.get("present") is False for row in probes),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed synthetic cohort-admission contract.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = "audio-sdk/f5-tts-voice-cohort/0.1"
MANIFEST_TOP_KEYS = (
    "schema_id", "cohort_id", "source", "weights", "runtime", "references",
    "texts", "controls", "outcomes", "rights",
)
MAX_MANIFEST_FILES = 32
MAX_MANIFEST_FILE_BYTES = 8 * 1024 * 1024 * 1024
MAX_REFERENCES = 1000
MAX_TEXTS = 10_000
MAX_TEXT_CHARS = 2_000
MAX_PACKAGES = 128
MAX_DURATION_MS = 3_600_000
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

        runtime_fields = ("python_version", "lock_sha256", "offline_load",
                          "packages")
        runtime = _exact_object(document["runtime"], runtime_fields, "runtime")
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

        references = _list(document["references"], "references", 1,
                           MAX_REFERENCES)
        for index, item in enumerate(references):
            prefix = "references[" + str(index) + "]"
            _exact_object(item, ("id", "sha256", "duration_ms", "consent",
                                 "permitted_use", "language", "speaker_group"),
                          prefix)
            _slug(item["id"], prefix + ".id")
            _sha(item["sha256"], prefix + ".sha256")
            _bounded_int(item["duration_ms"], 1, MAX_DURATION_MS,
                         prefix + ".duration_ms")
            _boolean(item["consent"], prefix + ".consent")
            _text(item["permitted_use"], prefix + ".permitted_use", 120)
            _text(item["language"], prefix + ".language", 80)
            _text(item["speaker_group"], prefix + ".speaker_group", 120)
            if not item["consent"]:
                raise _Invalid("rights_not_cleared", prefix + ".consent")
            checks += 7
        _sorted_unique(references, "id", "references")
        checks += 1

        texts = _list(document["texts"], "texts", 1, MAX_TEXTS)
        for index, item in enumerate(texts):
            prefix = "texts[" + str(index) + "]"
            _exact_object(item, ("id", "text", "language", "split"), prefix)
            _slug(item["id"], prefix + ".id")
            _text(item["text"], prefix + ".text", MAX_TEXT_CHARS)
            _text(item["language"], prefix + ".language", 80)
            if item["split"] not in ("dev", "test", "heldout"):
                raise _Invalid("invalid_split", prefix + ".split")
            checks += 4
        _sorted_unique(texts, "id", "texts")
        checks += 1

        controls = _exact_object(
            document["controls"],
            ("fixed_voice", "mismatched_reference", "ignore_reference",
             "content_preservation"),
            "controls")
        for name in ("fixed_voice", "mismatched_reference", "ignore_reference",
                     "content_preservation"):
            _boolean(controls[name], "controls." + name)
            if not controls[name]:
                raise _Invalid("missing_required_value", "controls." + name)
            checks += 1

        outcomes = _exact_object(
            document["outcomes"],
            ("content_preservation", "identity_similarity", "naturalness",
             "independent_listening", "alignment", "first_output",
             "device_timing"),
            "outcomes")
        for name in ("content_preservation", "identity_similarity",
                     "naturalness", "independent_listening", "alignment",
                     "first_output", "device_timing"):
            _boolean(outcomes[name], "outcomes." + name)
            if not outcomes[name]:
                raise _Invalid("missing_required_value", "outcomes." + name)
            checks += 1

        rights = _exact_object(
            document["rights"],
            ("weights_terms", "training_data_provenance", "reference_consent",
             "reference_availability", "output_use"),
            "rights")
        for name in ("weights_terms", "training_data_provenance",
                     "reference_consent", "reference_availability",
                     "output_use"):
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
        "cohort_id": "f5-tts-synthetic-schema-control",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": "0" * 40,
            "license_spdx": "Apache-2.0",
            "license_sha256": "1" * 64,
        },
        "weights": {
            "model_id": MODEL_VARIANT_EXAMPLE,
            "revision": "2" * 40,
            "files": [
                {
                    "path": MODEL_VARIANT_EXAMPLE + "/model.safetensors",
                    "sha256": "3" * 64,
                    "bytes": 1024,
                }
            ],
            "terms_reviewed": True,
        },
        "runtime": {
            "python_version": "3.12.0",
            "lock_sha256": "4" * 64,
            "offline_load": True,
            "packages": [{"name": "torch", "version": "2.6.0"}],
        },
        "references": [
            {
                "id": "ref-01",
                "sha256": "5" * 64,
                "duration_ms": 1000,
                "consent": True,
                "permitted_use": "synthetic-schema-control",
                "language": "en",
                "speaker_group": "control",
            }
        ],
        "texts": [
            {
                "id": "text-01",
                "text": "Synthetic schema control text, not evidence.",
                "language": "en",
                "split": "dev",
            }
        ],
        "controls": {
            "fixed_voice": True,
            "mismatched_reference": True,
            "ignore_reference": True,
            "content_preservation": True,
        },
        "outcomes": {
            "content_preservation": True,
            "identity_similarity": True,
            "naturalness": True,
            "independent_listening": True,
            "alignment": True,
            "first_output": True,
            "device_timing": True,
        },
        "rights": {
            "weights_terms": True,
            "training_data_provenance": True,
            "reference_consent": True,
            "reference_availability": True,
            "output_use": True,
        },
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


def admission_controls() -> dict:
    accepted = _case_row("accepted-schema-control",
                         validate_manifest(_manifest_control()), True,
                         accepted=True)
    cases = [accepted]
    cases.append(_case_row("root-list",
                           validate_manifest(["not", "a", "manifest"]), False))
    cases.append(_case_row("root-null", validate_manifest(None), False))
    cases.append(_raw_case(
        "duplicate-json-key",
        '{"schema_id":"audio-sdk/f5-tts-voice-cohort/0.1",'
        '"schema_id":"duplicate"}',
        "duplicate_json_key"))
    cases.append(_raw_case(
        "nonfinite-nan",
        '{"schema_id":"audio-sdk/f5-tts-voice-cohort/0.1","value":NaN}',
        "nonfinite_json"))
    cases.append(_raw_case(
        "nonfinite-infinity",
        '{"schema_id":"audio-sdk/f5-tts-voice-cohort/0.1","value":Infinity}',
        "nonfinite_json"))
    cases.append(_mutation_case(
        "missing-source", lambda m: m.pop("source"), "missing_field"))
    cases.append(_mutation_case(
        "unknown-top-key", lambda m: m.update({"extra": True}),
        "unknown_field"))
    cases.append(_mutation_case(
        "invalid-source-revision",
        lambda m: m["source"].update({"revision": "abc"}), "invalid_revision"))
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
            {"path": "b/model.safetensors", "sha256": "6" * 64, "bytes": 2},
            {"path": "a/model.safetensors", "sha256": "7" * 64, "bytes": 1},
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
            {"path": "../model.safetensors"}),
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
        "missing-runtime-lock",
        lambda m: m["runtime"].pop("lock_sha256"), "missing_field"))
    cases.append(_mutation_case(
        "non-offline-runtime",
        lambda m: m["runtime"].update({"offline_load": False}),
        "non_offline_runtime"))
    cases.append(_mutation_case(
        "empty-text", lambda m: m["texts"][0].update({"text": ""}),
        "empty_text"))
    cases.append(_mutation_case(
        "unresolved-language",
        lambda m: m["texts"][0].update({"language": "unknown"}),
        "unresolved_value"))
    cases.append(_mutation_case(
        "unconsented-reference",
        lambda m: m["references"][0].update({"consent": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "missing-outcome",
        lambda m: m["outcomes"].pop("naturalness"), "missing_field"))
    cases.append(_mutation_case(
        "false-right",
        lambda m: m["rights"].update({"output_use": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "duplicate-reference-id",
        lambda m: m["references"].append(dict(
            m["references"][0], sha256="8" * 64)),
        "duplicate_value"))
    cases.append(_mutation_case(
        "duplicate-package-name",
        lambda m: m["runtime"]["packages"].append(
            {"name": "torch", "version": "2.6.1"}),
        "duplicate_value"))

    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted_cases = [case for case in cases if case["status"] == "accepted"]
    summary = {
        "case_count": len(cases),
        "rejected_count": len(rejected),
        "accepted_schema_controls": len(accepted_cases),
        "qualifying_results": 0,
        "state_advanced_on_rejection": False,
        "accepted_control_qualifies": False,
        "all_adverse_cases_rejected": len(rejected) == len(cases) - len(accepted_cases),
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
        "contract_id": "audio-sdk/f5-tts-voice-cohort-contract/0.1",
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "max_files": MAX_MANIFEST_FILES,
        "max_file_bytes": MAX_MANIFEST_FILE_BYTES,
        "max_references": MAX_REFERENCES,
        "max_texts": MAX_TEXTS,
        "max_duration_ms": MAX_DURATION_MS,
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


# ---------------------------------------------------------------------------
# Report blocks.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "source_snapshot",
         "The exact SWivid/F5-TTS source checkout at an immutable 40-hex "
         "commit, with reviewed upstream license text and per-file SHA-256."),
        ("ART-02", "checkpoint_bundle",
         "The caller-selected F5-TTS checkpoint bundle such as " +
         MODEL_VARIANT_EXAMPLE + " at an immutable 40-hex model revision, "
         "including every weight, config, vocab/tokenizer asset, model card "
         "and terms file with byte count and SHA-256."),
        ("ART-03", "runtime_lock",
         "A reproducible isolated Python runtime with exact interpreter and "
         "package versions, a lock SHA-256, an offline load path and a "
         "recorded host profile."),
        ("ART-04", "rights_bundle",
         "Reviewed weight and model-card terms, training-data provenance, "
         "reference-voice consent, reference availability and output-use "
         "approval for every voice."),
        ("ART-05", "voice_cohort",
         "A frozen rights-cleared text and reference-voice cohort with manual "
         "transcripts, language/speaker groups, exact target conditions, "
         "held-out splits and matched controls."),
        ("ART-06", "voice_results",
         "Independent Voice results for content preservation, identity/"
         "similarity, naturalness, listening, alignment, first-output/tail, "
         "nonfinite and peak behavior, device timing, resources and "
         "uncertainty."),
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
         "The exact SWivid/F5-TTS source checkout is absent. No reviewable "
         "tree at a 40-hex commit, upstream license text or per-file SHA-256 "
         "pin exists in the workspace.",
         "Supply the SWivid/F5-TTS source at an immutable 40-hex commit with "
         "its reviewed license text and per-file SHA-256 pins; do not "
         "substitute a mirror."),
        ("BLK-02", "ART-02", ["RG-01", "RG-04", "RG-07"],
         "The exact pretrained F5-TTS checkpoint bundle is absent. For "
         "example " + MODEL_VARIANT_EXAMPLE + " weights, config, "
         "vocab/tokenizer assets, model card and terms files are not present "
         "at an immutable 40-hex model revision with SHA-256 and byte counts.",
         "Supply the caller-selected exact checkpoint bundle at an immutable "
         "40-hex Hugging Face revision, every file with SHA-256 and byte "
         "count, and the reviewed model card and weight terms."),
        ("BLK-03", "ART-03", ["RG-04", "RG-07"],
         "The pinned isolated Python runtime is absent. No interpreter, "
         "package lock, offline load path or environment digest matching an "
         "F5-TTS runtime is present, so a torch import and inference cannot "
         "be reproduced.",
         "Supply a locked, reproducible Python runtime with exact interpreter "
         "and package versions, lock SHA-256, offline load path and host "
         "profile."),
        ("BLK-04", "ART-04", ["RG-01", "RG-06"],
         "Weight terms, training-data provenance, reference-voice consent, "
         "reference availability and output use are unresolved. No reviewed "
         "rights bundle clears cloning or generated-speech use.",
         "Provide reviewed weight and model-card terms, training-data "
         "provenance, explicit reference-voice consent, reference "
         "availability and output use approval for every voice."),
        ("BLK-05", "ART-05", ["RG-02", "RG-03", "RG-05"],
         "No rights-cleared, consented frozen text and reference-voice cohort "
         "exists. Manual transcripts, language/speaker groups, exact target "
         "conditions, held-out splits and fixed-voice, mismatched-reference, "
         "ignore-reference and content-preservation controls are absent.",
         "Supply the frozen permitted cohort with manual transcripts, "
         "language and speaker groups, exact target conditions, held-out "
         "splits and matched controls."),
        ("BLK-06", "ART-06", ["RG-02", "RG-03", "RG-05", "RG-07", "RG-08"],
         "No Voice evidence exists. Content preservation, identity/similarity, "
         "naturalness, independent listening, alignment, first-output/tail, "
         "nonfinite and peak behavior, device timing, resources and "
         "uncertainty are all unmeasured.",
         "Run and preserve the independent Voice protocol, listening panel "
         "and target-device timing on the exact pinned source, weights and "
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
         "The exact source, checkpoint, per-file digests and license terms "
         "are absent.",
         "Supply and pin the exact source and caller-selected checkpoint "
         "bundle with reviewed terms."),
        ("RG-02", "rights-cleared frozen cohort and independent listening",
         "No rights-cleared cohort, held-out partition, naturalness rating "
         "or independent listening result exists.",
         "Freeze the permitted cohort and complete independent listening."),
        ("RG-03", "matched controls and uncertainty",
         "No fixed-voice, mismatched-reference, ignore-reference or "
         "content-preservation control result exists.",
         "Run matched controls with uncertainty on the frozen cohort."),
        ("RG-04", "pinned source, checkpoint, runtime and per-weight terms",
         "No exact source revision, model revision, runtime lock or "
         "per-weight terms are pinned.",
         "Pin the source, checkpoint, runtime and terms with exact digests."),
        ("RG-05", "causal output, timing and numerical behavior",
         "No causal chunk/lookahead, first-output/tail, sample-count, "
         "nonfinite, peak or target-device timing measurement exists.",
         "Measure causal output, numerical behavior and timing on the exact "
         "target."),
        ("RG-06", "independent consent, reference availability and output use",
         "Consent, reference availability and output use are unresolved and "
         "independent of model quality.",
         "Obtain explicit consent, availability and output-use approvals."),
        ("RG-07", "opt-in provider intake and independent review",
         "No adapter, descriptor, default-off intake decision or independent "
         "exact-head review exists.",
         "Add a task-local opt-in adapter only after RG-01 to RG-06 pass, "
         "then obtain independent exact-head review."),
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
        "candidate": "F5-TTS",
        "entries": [],
        "searched_pins": [
            "research/category_registry.json",
            "research/category_survey/sources.md",
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "research/voice-conversion-eval-20261101/README.md",
        ],
        "not_reproduced_here": True,
        "no_values_inferred_from_adjacent_tasks": True,
        "note": "The pinned read-only records contain only an F5-TTS source "
                "lead. No F5-TTS run, output, metric, reference voice or "
                "runtime is recorded locally, and no adjacent TTS or vocoder "
                "value is inherited.",
    }


def voice_profile_block() -> dict:
    return {
        "profile": PROFILE_KEY,
        "status": "blocked",
        "rows": [dict(row) for row in VOICE_REQUIREMENTS],
        "permitted_input_and_target_references": False,
        "task_and_language_speaker_groups": False,
        "text_and_semantic_preservation_measured": False,
        "identity_similarity_measured": False,
        "naturalness_measured": False,
        "alignment_measured": False,
        "first_output_or_tail_measured": False,
        "exact_target_condition_qualified": False,
        "consent_cleared": False,
        "reference_availability_cleared": False,
        "output_use_cleared": False,
        "independent_listening_present": False,
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
            if line.startswith("| Voice |")]
    if len(rows) != 1:
        raise ValueError("voice_profile_row_not_unique")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("voice_profile_phrase_missing:" + phrase)
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
        "real_corpus": False,
        "audio_read": False,
        "tts_performed": False,
        "voice_conversion_performed": False,
        "quality_scored": False,
        "reference_similarity_scored": False,
        "naturalness_scored": False,
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
        "task_kind": "reference_conditioned_text_to_speech",
        "inputs": ["text", "reference_audio", "optional_reference_text"],
        "output": "generated_waveform",
        "sample_rate_hz": UPSTREAM_SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_format": "f32",
        "text_source_mapping": "text_plus_reference_audio_to_waveform",
        "not_voice_conversion": True,
        "installed_v0": False,
        "provider_registered": False,
        "streaming_geometry_pinned": False,
        "generated_length_not_identity": True,
    }


def upstream_record() -> dict:
    return {
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": None,
        "source_revision_requirement":
            "immutable 40-hex upstream commit, verified from a reviewable "
            "checkout",
        "source_license": None,
        "source_license_requirement":
            "reviewed upstream license with exact SPDX identifier and license "
            "SHA-256",
        "model_repository": MODEL_REPOSITORY,
        "model_variant_requirement":
            "caller-selected F5-TTS checkpoint (for example " +
            MODEL_VARIANT_EXAMPLE + "), recorded exactly",
        "model_revision": None,
        "model_revision_requirement": "immutable 40-hex snapshot revision",
        "model_file_requirement":
            "every weight, config, vocab/tokenizer and terms file with byte "
            "count and SHA-256",
        "sample_rate_hz": UPSTREAM_SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_format": "f32",
        "task_kind": "reference_conditioned_text_to_speech",
        "is_tts_not_voice_conversion": True,
        "present": False,
        "executed": False,
        "digest_asserted": False,
    }


def rights_gap() -> dict:
    return {
        "code_license": "unverified_source_absent",
        "weight_terms": "unresolved",
        "training_data_provenance": "unresolved",
        "reference_voice_consent": "unresolved",
        "reference_availability": "unresolved",
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
        "voice_cohort_present": False,
        "reference_conditioned_tts_evaluation_present": False,
        "content_preservation_result": False,
        "identity_similarity_result": False,
        "naturalness_result": False,
        "listening_result": False,
        "alignment_result": False,
        "first_output_or_tail_result": False,
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
        "voice_profile": voice_profile_block(),
        "voice_profile_requirements": [dict(row) for row in VOICE_REQUIREMENTS],
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
        "voice_profile": voice_profile_block(),
        "voice_profile_requirements": [dict(row) for row in VOICE_REQUIREMENTS],
        "qualification": qualification_block(),
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": "Python 3.12, standard library only",
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
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    if [row.get("id") for row in gates] != ["RG-0" + str(i) for i in range(1, 9)]:
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
            or qualification.get("all_release_gates_blocked") is not True):
        raise ValueError("contract_qualification_invalid")
    assert_no_float(contract)
