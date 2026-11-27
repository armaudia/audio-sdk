# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local WORLD vocoder blocker evidence for SDK-WORLD-VOCODER.

Stdlib-only, deterministic, fail-closed. No WORLD source import, build,
execution, model, weights, runtime, feature tensor, audio, corpus, listening,
device timing, benchmark, or release claim. Missing evidence never qualifies.
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

TASK = "SDK-WORLD-VOCODER"
COMPONENT_ID = "world-vocoder"
TASK_TITLE = "WORLD vocoder"
CONTRACT_ID = "audio-sdk/world-vocoder-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "feasibility"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-WORLD-VOCODER"
WRITE_SCOPE = "docs/task-evidence/world-vocoder/ only"
TASK_PREFIX = "docs/task-evidence/world-vocoder/"
REQUIRED_INTERPRETER = "3.12.16"

SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml"))
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        inventory = candidate / "audio-benchmark-platform/plan/INVENTORY.json"
        if board.is_file() and inventory.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-FND-AUDIT",
        "title": "Public provider intake and asset boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-EVIDENCE",
        "title": "Task-matched conformance and reproducible benchmark evidence",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-PROVIDER",
        "title": "Provider interface and minimal engine",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
)

ABSENCE_PROBES = (
    "third_party/world-vocoder",
    "third_party/WORLD",
    "adapters/world-vocoder",
    "adapters/world",
    "data/assets/world-vocoder",
    "data/assets/world",
    "docs/task-evidence/world-vocoder/source",
    "docs/task-evidence/world-vocoder/assets",
    "docs/task-evidence/world-vocoder/runtime",
    "docs/task-evidence/world-vocoder/weights",
    "research/voice-enhancement-20261101/repos/world",
    "research/voice-conversion-eval-20261101/repos/world",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/world-vocoder",
    "~/.cache/WORLD",
)

SCOPE_BASE_REFS = ("origin/main", "main")

PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker groups.",
    "Preserve text and semantic content, identity/similarity and naturalness as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target condition.",
    "Consent, reference availability and output use are independent gates.",
)

REQUIRED_ARTIFACTS = (
    {"id": "ART-01", "kind": "pinned_task_identity_and_sources", "present": True, "verified": True, "blocked": False, "sha256": None,
     "requirement": "Pinned task identity, source digests, and Voice profile phrases for this task-local blocker package."},
    {"id": "ART-02", "kind": "exact_world_source_snapshot", "present": False, "verified": False, "blocked": True, "sha256": None,
     "requirement": "Exact WORLD source checkout/archive at a 40-hex revision with license/notice files and immutable digest."},
    {"id": "ART-03", "kind": "pinned_build_or_runtime", "present": False, "verified": False, "blocked": True, "sha256": None,
     "requirement": "Pinned deterministic build/runtime for WORLD analysis/synthesis with recorded host/toolchain and install digest."},
    {"id": "ART-04", "kind": "rights_cleared_input_cohort", "present": False, "verified": False, "blocked": True, "sha256": None,
     "requirement": "Rights-cleared input audio/features with consent, language/speaker groups, exact geometry, and controls."},
    {"id": "ART-05", "kind": "reviewed_terms_and_output_use", "present": False, "verified": False, "blocked": True, "sha256": None,
     "requirement": "Reviewed upstream license/notice/redistribution/output-use terms covering selected WORLD revision and artifacts."},
    {"id": "ART-06", "kind": "voice_profile_measurements", "present": False, "verified": False, "blocked": True, "sha256": None,
     "requirement": "Voice-profile quality, alignment, timing, resource, and listening measurements with controls."},
)

EXACT_BLOCKERS = (
    {"id": "BLK-01", "artifact_id": "ART-02", "status": "open", "qualifies": False, "linked_gates": ["RG-01"],
     "statement": "No exact WORLD source snapshot at immutable revision with license/notice digest is staged in this task.",
     "required_action": "Stage exact mmorise/World revision/archive with license/notice files and immutable digests; do not import or execute source in this blocker package."},
    {"id": "BLK-02", "artifact_id": "ART-03", "status": "open", "qualifies": False, "linked_gates": ["RG-02", "RG-07"],
     "statement": "No pinned deterministic WORLD build/runtime, toolchain, or host profile is present.",
     "required_action": "Provide pinned offline deterministic build/runtime and record exact toolchain, host profile, and install/build digests."},
    {"id": "BLK-03", "artifact_id": "ART-04", "status": "open", "qualifies": False, "linked_gates": ["RG-03", "RG-05"],
     "statement": "No rights-cleared audio/feature cohort with consent, language/speaker groups, or controls is present.",
     "required_action": "Provide rights-cleared frozen cohort with consent, exact geometry, language/speaker groups, and matched/mismatched/zero controls."},
    {"id": "BLK-04", "artifact_id": "ART-05", "status": "open", "qualifies": False, "linked_gates": ["RG-04"],
     "statement": "No reviewed upstream WORLD license/notice/redistribution/output-use terms are recorded for a selected revision.",
     "required_action": "Review and record exact revision terms for source, build artifacts, redistribution, and output use before any intake."},
    {"id": "BLK-05", "artifact_id": "ART-06", "status": "open", "qualifies": False, "linked_gates": ["RG-06", "RG-08"],
     "statement": "No Voice-profile quality, alignment, timing, resource, or listening result exists.",
     "required_action": "Run Voice-profile measurements on target conditions with controls; keep any result separate from this blocker package until gates pass."},
)

RELEASE_GATES = (
    {"id": "RG-01", "title": "Exact source revision and notices",
     "reopen_condition": "Exact WORLD source revision/archive with license/notice files and immutable digests is staged and reviewed."},
    {"id": "RG-02", "title": "Pinned deterministic build/runtime",
     "reopen_condition": "Pinned offline deterministic build/runtime with toolchain, host profile, and install/build digests is recorded."},
    {"id": "RG-03", "title": "Rights-cleared cohort and controls",
     "reopen_condition": "Rights-cleared frozen cohort with consent, exact geometry, language/speaker groups, and controls is supplied."},
    {"id": "RG-04", "title": "Reviewed terms and output use",
     "reopen_condition": "Reviewed source/build/redistribution/output-use terms for the exact selected revision are recorded."},
    {"id": "RG-05", "title": "Consent, reference availability and output use",
     "reopen_condition": "Signed consent, input/reference availability, output-use and commercial terms are recorded for every input/output."},
    {"id": "RG-06", "title": "Separate content, conditioning, naturalness and listening",
     "reopen_condition": "Pinned scorers and approved blinded listening produce reviewed intelligibility, conditioning, naturalness, and conditional identity results."},
    {"id": "RG-07", "title": "Alignment, first-output/tail, and device resources",
     "reopen_condition": "Target-device paced runs record alignment, first-output/tail, peaks, nonfinite behavior, CPU, memory, and deadlines."},
    {"id": "RG-08", "title": "Intake boundary and release review",
     "reopen_condition": "Separate versioned intake with OFF-by-default/opt-in boundary and exact-head independent review passes; no release claim before then."},
)

VOICE_PROFILE_ROWS = (
    {"id": "VP-01", "requirement": "Freeze permitted input and target references, task and language/speaker groups.", "status": "blocked", "evidence": "No rights-cleared cohort, consent record, language/speaker group, or exact target/reference condition is present."},
    {"id": "VP-02", "requirement": "Preserve content: intelligibility, semantic content and feature conditioning.", "status": "blocked", "evidence": "No generated waveform, transcript, intelligibility score, or conditioning result exists."},
    {"id": "VP-03", "requirement": "Identity/similarity as a separate outcome, only when explicitly speaker-conditioned.", "status": "blocked", "evidence": "No speaker-conditioned model, reference target, or human identity/similarity result exists."},
    {"id": "VP-04", "requirement": "Naturalness as a separate outcome.", "status": "blocked", "evidence": "No naturalness rating, blinded listening, or preference panel exists."},
    {"id": "VP-05", "requirement": "Record alignment.", "status": "blocked", "evidence": "No frame/sample alignment, onset mapping, or feature-output content mapping exists."},
    {"id": "VP-06", "requirement": "Record first-output/tail timing.", "status": "blocked", "evidence": "No streaming run, chunk boundary, first-output, or tail measurement exists."},
    {"id": "VP-07", "requirement": "Record the exact target condition.", "status": "blocked", "evidence": "No exact source revision, build/runtime, feature geometry, sample rate, hop, precision, or device target is recorded."},
    {"id": "VP-08", "requirement": "Consent, reference availability and output use as independent gates.", "status": "blocked", "evidence": "No consent, input/reference availability, or output-use record exists; no terms review clears them."},
)

QUALITY_OUTCOME_ROWS = (
    {"id": "QO-01", "outcome": "content/intelligibility preservation", "status": "blocked", "value": None, "evidence": "No qualified waveform, transcript, or intelligibility score."},
    {"id": "QO-02", "outcome": "pitch/prosody conditioning fidelity", "status": "blocked", "value": None, "evidence": "No qualified WORLD analysis/synthesis run or conditioning metric."},
    {"id": "QO-03", "outcome": "naturalness", "status": "blocked", "value": None, "evidence": "No qualified waveform, blinded listening, or panel."},
    {"id": "QO-04", "outcome": "identity/similarity (conditional)", "status": "blocked", "value": None, "evidence": "No speaker-conditioned setup, reference target, or identity/similarity result."},
)

TIMING_ROWS = (
    {"id": "TR-01", "metric": "alignment", "status": "blocked", "value": None, "evidence": "No run, frame/sample alignment, or content mapping."},
    {"id": "TR-02", "metric": "first-output/tail", "status": "blocked", "value": None, "evidence": "No streaming run or content-delay measurement."},
    {"id": "TR-03", "metric": "device timing/resources", "status": "blocked", "value": None, "evidence": "No target-device paced run, CPU/memory, or deadline data."},
    {"id": "TR-04", "metric": "benchmark/real-time factor", "status": "blocked", "value": None, "evidence": "No pinned runtime or benchmark result."},
)

NON_CLAIMS = (
    "No WORLD source, binary, model, runtime, feature tensor, waveform, or vendor output is bundled.",
    "No upstream source was imported, built, loaded, or executed; no model was run.",
    "No audio or feature tensor was read, decoded, played, listened to, or scored.",
    "No content, conditioning, identity, similarity, naturalness, alignment, first-output, tail, peak, device-timing, resource, benchmark, or release result exists.",
    "No consent, input/reference availability, or output-use clearance is asserted.",
    "No upstream license/notice/redistribution/output-use term is asserted as reviewed clearance.",
    "No provider was registered, enabled by default, described in a registry, or exposed through installed-v0, ABI, shared build, or CI.",
    "A readiness conclusion with an exact external blocker is not a qualification or release pass.",
)

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "frame_samples": 160,
    "sample_format": "f32",
    "preserved": True,
    "sdk_callback_invoked": False,
    "sdk_compatible": False,
    "model_io_claimed": False,
}


def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate_key:" + k)
        out[k] = v
    return out


def loads_strict(text: str) -> Any:
    if text.startswith("\ufeff"):
        raise ValueError("bom_not_allowed")
    value = json.loads(text, parse_constant=_reject_constant, object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise ValueError("root_must_be_object")
    return value


def read_strict_json(path: Path) -> Any:
    return loads_strict(path.read_text(encoding="utf-8"))


def canonical_text(value: Any) -> str:
    _no_floats(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return
    if isinstance(value, list):
        for item in value:
            _no_floats(item)
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("non_string_key")
            _no_floats(v)
        return
    raise ValueError("unsupported_type:" + type(value).__name__)


def board_row_projection(board_path: Path | None = None) -> dict:
    path = board_path or (AUDIO_ROOT / BOARD_TASK_ROW)
    rows = read_strict_json(path)
    if not isinstance(rows, list):
        raise ValueError("board_not_list")
    for row in rows:
        if isinstance(row, dict) and row.get("id") == TASK:
            proj = {f: row.get(f) for f in BOARD_ROW_FIELDS}
            if proj != BOARD_ROW_PROJECTION:
                raise ValueError("board_projection_mismatch")
            return proj
    raise ValueError("board_row_missing")


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection or BOARD_ROW_PROJECTION)


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([dict(r) for r in rows])


def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows = []
    for rel, expected in sorted(pins.items()):
        path = root / rel
        actual = sha256_file(path) if path.is_file() else None
        rows.append({"path": rel, "sha256": expected, "actual": actual, "verified": actual == expected})
    return rows


def _git(worktree: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *args], capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    r = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = r.stdout.strip()
    return sha if r.returncode == 0 and sha else None


def scope_base(worktree: Path = WORKTREE, refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        r = _git(worktree, "merge-base", "HEAD", ref)
        base = r.stdout.strip()
        if r.returncode != 0 or not base:
            continue
        if best is None or (_git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0 and best != base):
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    r = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if r.returncode != 0:
        raise ValueError("scope_diff_failed:" + r.stderr.strip())
    return [line for line in r.stdout.splitlines() if line.strip()]


def scope_violations(paths: list[str]) -> list[str]:
    return [p for p in paths if not p.startswith(TASK_PREFIX)]


def absence_probes(root: Path) -> list[dict]:
    rows = []
    for rel in ABSENCE_PROBES:
        path = root / rel
        exists = path.exists()
        rows.append({"path": rel, "exists": exists, "is_file": path.is_file(), "is_dir": path.is_dir(), "verified_absent": not exists})
    return rows


def home_absence_probes() -> list[dict]:
    rows = []
    for rel in HOME_ABSENCE_PROBES:
        path = Path(os.path.expanduser(rel))
        exists = path.exists()
        rows.append({"path": rel, "exists": exists, "verified_absent": not exists})
    return rows


def absence_summary(workspace_rows: list[dict], home_rows: list[dict]) -> dict:
    all_rows = workspace_rows + home_rows
    present = [r["path"] for r in all_rows if r.get("exists")]
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(workspace_rows),
        "home_probe_count": len(home_rows),
        "present_count": len(present),
        "present_paths": present,
        "all_probes_absent": len(present) == 0,
        "download_attempted": False,
        "network_used": False,
        "recursive_workspace_walk": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "feature_input_read": False,
    }


# ---- Admission boundary (metadata-only, no runtime) ----
MANIFEST_SCHEMA_ID = "audio-sdk/world-vocoder-qualification/0.1"
MANIFEST_FIELDS = ("schema_id", "cohort_id", "source", "runtime", "features", "controls", "outcomes", "rights")
SOURCE_FIELDS = ("revision", "path", "license_id", "license_path", "license_sha256", "notice_sha256")
RUNTIME_FIELDS = ("build_digest", "toolchain", "host_profile", "deterministic_algorithms", "seed")
FEATURE_FIELDS = ("id", "path", "sha256", "sample_rate_hz", "frame_period_ms", "frame_count", "feature_kind", "consent_id", "rights_reference", "language", "speaker_group")
CONTROL_FIELDS = ("id", "kind", "feature_id", "feature_sha256")
OUTCOME_FIELDS = ("intelligibility_wer", "stoi", "naturalness_mos", "identity_similarity_cosine", "alignment_samples", "first_output_ms", "tail_ms", "peak_abs", "clipped_fraction", "nonfinite_count", "sample_count", "output_sample_rate_hz")
RIGHTS_FIELDS = ("consent_reference", "input_availability", "output_use", "commercial_terms_review", "terms_review", "listening_protocol", "listening_panel_size")
CONTROL_KINDS = ("matched_features", "mismatched_features", "zero_features")
FEATURE_KINDS = ("f0_sp_ap", "mel", "log_mel")
OUTPUT_SAMPLE_RATES = (8000, 16000, 22050, 24000, 44100, 48000)
INPUT_SAMPLE_RATES = (8000, 16000, 22050, 24000, 44100, 48000)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
LANGUAGE = re.compile(r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")
MAX_SEED = 2 ** 31 - 1
MAX_FRAME_COUNT = 1_000_000
MAX_ALIGNMENT = 96_000
MAX_PEAK = 4
MAX_PANEL = 1000
MAX_SAMPLE_COUNT = 1_000_000_000


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "world-cohort-control",
        "source": {
            "revision": "0" * 40,
            "path": "/caller/world/source",
            "license_id": "BSD-3-Clause",
            "license_path": "/caller/world/LICENSE",
            "license_sha256": "1" * 64,
            "notice_sha256": "2" * 64,
        },
        "runtime": {
            "build_digest": "3" * 64,
            "toolchain": "clang-18",
            "host_profile": "linux-x86_64",
            "deterministic_algorithms": True,
            "seed": 1729,
        },
        "features": [
            {"id": "feat-a", "path": "/caller/world/feat-a.npz", "sha256": "4" * 64, "sample_rate_hz": 16000, "frame_period_ms": 5, "frame_count": 200, "feature_kind": "f0_sp_ap", "consent_id": "consent-a", "rights_reference": "rights-a", "language": "en-US", "speaker_group": "spk-a"},
            {"id": "feat-b", "path": "/caller/world/feat-b.npz", "sha256": "5" * 64, "sample_rate_hz": 16000, "frame_period_ms": 5, "frame_count": 200, "feature_kind": "f0_sp_ap", "consent_id": "consent-b", "rights_reference": "rights-b", "language": "en-US", "speaker_group": "spk-b"},
        ],
        "controls": [
            {"id": "ctl-matched", "kind": "matched_features", "feature_id": "feat-a", "feature_sha256": "4" * 64},
            {"id": "ctl-mismatch", "kind": "mismatched_features", "feature_id": "feat-b", "feature_sha256": "5" * 64},
            {"id": "ctl-zero", "kind": "zero_features", "feature_id": None, "feature_sha256": None},
        ],
        "outcomes": {
            "intelligibility_wer": 0.0, "stoi": 0.9, "naturalness_mos": 3.0, "identity_similarity_cosine": 0.5,
            "alignment_samples": 0, "first_output_ms": 1.0, "tail_ms": 1.0, "peak_abs": 0.5, "clipped_fraction": 0.0,
            "nonfinite_count": 0, "sample_count": 16000, "output_sample_rate_hz": 16000,
        },
        "rights": {
            "consent_reference": "consent-a", "input_availability": "caller-supplied", "output_use": "research-only",
            "commercial_terms_review": "review-commercial-a", "terms_review": "review-a", "listening_protocol": "protocol-a", "listening_panel_size": 3,
        },
    }


def _rej(code: str, field: str, checks: int) -> dict:
    return {"accepted": False, "code": code, "field": field, "checks": checks, "qualifies": False, "state_unchanged": True}


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v: Any) -> bool:
    return (isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v)))


def validate_manifest(doc: Any, probe_paths: bool = False) -> dict:
    checks = 0
    if not isinstance(doc, dict):
        return _rej("invalid_type", "$", checks)
    checks += 1
    if set(doc) != set(MANIFEST_FIELDS):
        return _rej("missing_field" if set(MANIFEST_FIELDS) - set(doc) else "unknown_field", "$", checks)
    checks += 1
    if doc["schema_id"] != MANIFEST_SCHEMA_ID:
        return _rej("invalid_value", "schema_id", checks)
    checks += 1
    cid = doc["cohort_id"]
    if not isinstance(cid, str) or not SLUG.match(cid):
        return _rej("invalid_value", "cohort_id", checks)

    src = doc["source"]
    checks += 1
    if not isinstance(src, dict) or set(src) != set(SOURCE_FIELDS):
        return _rej("invalid_value", "source", checks)
    for f in SOURCE_FIELDS:
        checks += 1
        v = src[f]
        if f in ("revision",):
            if not isinstance(v, str) or not HEX40.match(v):
                return _rej("invalid_value", f"source.{f}", checks)
        elif f.endswith("_sha256"):
            if not isinstance(v, str) or not HEX64.match(v):
                return _rej("invalid_value", f"source.{f}", checks)
        elif f in ("path", "license_path"):
            if not isinstance(v, str) or not v.startswith("/") or ".." in Path(v).parts or "\x00" in v:
                return _rej("invalid_path", f"source.{f}", checks)
        else:
            if not isinstance(v, str) or not v:
                return _rej("invalid_value", f"source.{f}", checks)

    rt = doc["runtime"]
    checks += 1
    if not isinstance(rt, dict) or set(rt) != set(RUNTIME_FIELDS):
        return _rej("invalid_value", "runtime", checks)
    checks += 1
    if not isinstance(rt["build_digest"], str) or not HEX64.match(rt["build_digest"]):
        return _rej("invalid_value", "runtime.build_digest", checks)
    checks += 1
    if not isinstance(rt["toolchain"], str) or not rt["toolchain"]:
        return _rej("invalid_value", "runtime.toolchain", checks)
    checks += 1
    if not isinstance(rt["host_profile"], str) or not rt["host_profile"]:
        return _rej("invalid_value", "runtime.host_profile", checks)
    checks += 1
    if rt["deterministic_algorithms"] is not True:
        return _rej("invalid_value", "runtime.deterministic_algorithms", checks)
    checks += 1
    if not _is_int(rt["seed"]) or not (0 <= rt["seed"] <= MAX_SEED):
        return _rej("invalid_value", "runtime.seed", checks)

    feats = doc["features"]
    checks += 1
    if not isinstance(feats, list) or not feats:
        return _rej("invalid_value", "features", checks)
    seen = set()
    feat_digests = {}
    for i, f in enumerate(feats):
        checks += 1
        if not isinstance(f, dict) or set(f) != set(FEATURE_FIELDS):
            return _rej("invalid_value", f"features[{i}]", checks)
        fid = f["id"]
        if not isinstance(fid, str) or not SLUG.match(fid) or fid in seen:
            return _rej("invalid_value", f"features[{i}].id", checks)
        seen.add(fid)
        if not isinstance(f["path"], str) or not f["path"].startswith("/") or ".." in Path(f["path"]).parts or "\x00" in f["path"]:
            return _rej("invalid_path", f"features[{i}].path", checks)
        if not isinstance(f["sha256"], str) or not HEX64.match(f["sha256"]):
            return _rej("invalid_value", f"features[{i}].sha256", checks)
        if not _is_int(f["sample_rate_hz"]) or f["sample_rate_hz"] not in INPUT_SAMPLE_RATES:
            return _rej("invalid_value", f"features[{i}].sample_rate_hz", checks)
        if not _is_num(f["frame_period_ms"]) or not (0 < float(f["frame_period_ms"]) <= 100):
            return _rej("invalid_value", f"features[{i}].frame_period_ms", checks)
        if not _is_int(f["frame_count"]) or not (1 <= f["frame_count"] <= MAX_FRAME_COUNT):
            return _rej("invalid_value", f"features[{i}].frame_count", checks)
        if f["feature_kind"] not in FEATURE_KINDS:
            return _rej("invalid_value", f"features[{i}].feature_kind", checks)
        for k in ("consent_id", "rights_reference", "speaker_group"):
            if not isinstance(f[k], str) or not f[k]:
                return _rej("invalid_value", f"features[{i}].{k}", checks)
        if not isinstance(f["language"], str) or not LANGUAGE.match(f["language"]):
            return _rej("invalid_value", f"features[{i}].language", checks)
        feat_digests[fid] = f["sha256"]

    ctrls = doc["controls"]
    checks += 1
    if not isinstance(ctrls, list) or not ctrls:
        return _rej("invalid_value", "controls", checks)
    kinds = set()
    cids = set()
    for i, c in enumerate(ctrls):
        if not isinstance(c, dict) or set(c) != set(CONTROL_FIELDS):
            return _rej("invalid_value", f"controls[{i}]", checks)
        if not isinstance(c["id"], str) or not SLUG.match(c["id"]) or c["id"] in cids:
            return _rej("invalid_value", f"controls[{i}].id", checks)
        cids.add(c["id"])
        kind = c["kind"]
        if kind not in CONTROL_KINDS or kind in kinds:
            return _rej("invalid_value", f"controls[{i}].kind", checks)
        kinds.add(kind)
        fid, fd = c["feature_id"], c["feature_sha256"]
        if kind == "zero_features":
            if fid is not None or fd is not None:
                return _rej("invalid_value", f"controls[{i}]", checks)
        else:
            if not isinstance(fid, str) or fid not in feat_digests:
                return _rej("invalid_value", f"controls[{i}].feature_id", checks)
            if not isinstance(fd, str) or fd != feat_digests[fid]:
                return _rej("invalid_value", f"controls[{i}].feature_sha256", checks)
    if set(CONTROL_KINDS) - kinds:
        return _rej("invalid_value", "controls", checks)

    out = doc["outcomes"]
    checks += 1
    if not isinstance(out, dict) or set(out) != set(OUTCOME_FIELDS):
        return _rej("invalid_value", "outcomes", checks)
    if not _is_num(out["intelligibility_wer"]) or not (0 <= float(out["intelligibility_wer"]) <= 1):
        return _rej("invalid_value", "outcomes.intelligibility_wer", checks)
    if not _is_num(out["stoi"]) or not (0 <= float(out["stoi"]) <= 1):
        return _rej("invalid_value", "outcomes.stoi", checks)
    if not _is_num(out["naturalness_mos"]) or not (1 <= float(out["naturalness_mos"]) <= 5):
        return _rej("invalid_value", "outcomes.naturalness_mos", checks)
    if not _is_num(out["identity_similarity_cosine"]) or not (-1 <= float(out["identity_similarity_cosine"]) <= 1):
        return _rej("invalid_value", "outcomes.identity_similarity_cosine", checks)
    if not _is_int(out["alignment_samples"]) or not (0 <= out["alignment_samples"] <= MAX_ALIGNMENT):
        return _rej("invalid_value", "outcomes.alignment_samples", checks)
    for k in ("first_output_ms", "tail_ms"):
        if not _is_num(out[k]) or float(out[k]) < 0:
            return _rej("invalid_value", f"outcomes.{k}", checks)
    if not _is_num(out["peak_abs"]) or not (0 <= float(out["peak_abs"]) <= MAX_PEAK):
        return _rej("invalid_value", "outcomes.peak_abs", checks)
    if not _is_num(out["clipped_fraction"]) or not (0 <= float(out["clipped_fraction"]) <= 1):
        return _rej("invalid_value", "outcomes.clipped_fraction", checks)
    if not _is_int(out["nonfinite_count"]) or out["nonfinite_count"] != 0:
        return _rej("invalid_value", "outcomes.nonfinite_count", checks)
    if not _is_int(out["sample_count"]) or not (1 <= out["sample_count"] <= MAX_SAMPLE_COUNT):
        return _rej("invalid_value", "outcomes.sample_count", checks)
    if not _is_int(out["output_sample_rate_hz"]) or out["output_sample_rate_hz"] not in OUTPUT_SAMPLE_RATES:
        return _rej("invalid_value", "outcomes.output_sample_rate_hz", checks)

    rights = doc["rights"]
    checks += 1
    if not isinstance(rights, dict) or set(rights) != set(RIGHTS_FIELDS):
        return _rej("invalid_value", "rights", checks)
    for f in RIGHTS_FIELDS:
        if f == "listening_panel_size":
            if not _is_int(rights[f]) or not (1 <= rights[f] <= MAX_PANEL):
                return _rej("invalid_value", f"rights.{f}", checks)
        else:
            if not isinstance(rights[f], str) or not rights[f]:
                return _rej("invalid_value", f"rights.{f}", checks)

    return {"accepted": True, "code": "accepted_schema_control", "field": None, "checks": checks, "qualifies": False, "state_unchanged": True}


def admission_controls() -> dict:
    control = _manifest_control()
    accepted = validate_manifest(control, probe_paths=False)
    cases: list[dict] = []

    def add(cid: str, doc: Any) -> None:
        r = validate_manifest(doc, probe_paths=False)
        cases.append({"id": cid, "status": "rejected" if not r["accepted"] else "accepted", "code": r["code"], "field": r["field"], "qualifies": False, "state_unchanged": r["state_unchanged"]})

    def mutate(cid: str, fn) -> None:
        d = _manifest_control()
        fn(d)
        add(cid, d)

    def set_top(k, v):
        return lambda d: d.__setitem__(k, v)

    def del_top(k):
        return lambda d: d.__delitem__(k)

    def set_nested(path, v):
        def fn(d):
            t = d
            for p in path[:-1]:
                t = t[p]
            t[path[-1]] = v
        return fn

    def del_nested(path):
        def fn(d):
            t = d
            for p in path[:-1]:
                t = t[p]
            del t[path[-1]]
        return fn

    for cid, payload in (("root-list", []), ("root-null", None), ("root-string", "x"), ("root-int", 7), ("root-bool", True)):
        add(cid, payload)
    for f in MANIFEST_FIELDS:
        mutate("missing-" + f, del_top(f))
    mutate("unknown-top", set_top("extra", 1))
    mutate("wrong-schema", set_top("schema_id", "wrong"))
    mutate("cohort-bad", set_top("cohort_id", "Bad"))
    mutate("cohort-empty", set_top("cohort_id", ""))

    for f in SOURCE_FIELDS:
        mutate("missing-source-" + f, del_nested(("source", f)))
    mutate("unknown-source", set_nested(("source", "extra"), 1))
    mutate("source-rev-short", set_nested(("source", "revision"), "a" * 39))
    mutate("source-rev-upper", set_nested(("source", "revision"), "A" * 40))
    mutate("source-path-rel", set_nested(("source", "path"), "rel"))
    mutate("source-path-trav", set_nested(("source", "path"), "/a/../b"))
    mutate("source-license-empty", set_nested(("source", "license_id"), ""))
    mutate("source-license-sha", set_nested(("source", "license_sha256"), "bad"))
    mutate("source-notice-sha", set_nested(("source", "notice_sha256"), "bad"))

    for f in RUNTIME_FIELDS:
        mutate("missing-runtime-" + f, del_nested(("runtime", f)))
    mutate("unknown-runtime", set_nested(("runtime", "extra"), 1))
    mutate("runtime-digest", set_nested(("runtime", "build_digest"), "bad"))
    mutate("runtime-toolchain-empty", set_nested(("runtime", "toolchain"), ""))
    mutate("runtime-host-empty", set_nested(("runtime", "host_profile"), ""))
    mutate("runtime-nondet", set_nested(("runtime", "deterministic_algorithms"), False))
    mutate("runtime-seed-neg", set_nested(("runtime", "seed"), -1))
    mutate("runtime-seed-bool", set_nested(("runtime", "seed"), True))

    mutate("features-empty", set_nested(("features",), []))
    for f in FEATURE_FIELDS:
        mutate("missing-feature-" + f, del_nested(("features", 0, f)))
    mutate("unknown-feature", set_nested(("features", 0, "extra"), 1))
    mutate("feature-id-bad", set_nested(("features", 0, "id"), "Bad"))
    mutate("feature-dup-id", lambda d: d["features"].append(dict(d["features"][0], sha256="6" * 64, path="/caller/world/feat-c.npz", id="feat-a")))
    mutate("feature-path-rel", set_nested(("features", 0, "path"), "rel.npy"))
    mutate("feature-path-trav", set_nested(("features", 0, "path"), "/a/../b.npy"))
    mutate("feature-sha", set_nested(("features", 0, "sha256"), "bad"))
    mutate("feature-rate-bad", set_nested(("features", 0, "sample_rate_hz"), 12345))
    mutate("feature-rate-bool", set_nested(("features", 0, "sample_rate_hz"), True))
    mutate("feature-period-zero", set_nested(("features", 0, "frame_period_ms"), 0))
    mutate("feature-period-high", set_nested(("features", 0, "frame_period_ms"), 101))
    mutate("feature-frames-zero", set_nested(("features", 0, "frame_count"), 0))
    mutate("feature-frames-bool", set_nested(("features", 0, "frame_count"), True))
    mutate("feature-kind", set_nested(("features", 0, "feature_kind"), "unknown"))
    mutate("feature-consent-empty", set_nested(("features", 0, "consent_id"), ""))
    mutate("feature-rights-empty", set_nested(("features", 0, "rights_reference"), ""))
    mutate("feature-lang", set_nested(("features", 0, "language"), "English"))
    mutate("feature-speaker-empty", set_nested(("features", 0, "speaker_group"), ""))

    mutate("controls-empty", set_nested(("controls",), []))
    for f in CONTROL_FIELDS:
        mutate("missing-control-" + f, del_nested(("controls", 0, f)))
    mutate("unknown-control", set_nested(("controls", 0, "extra"), 1))
    mutate("control-id-bad", set_nested(("controls", 0, "id"), "Bad"))
    mutate("control-kind-bad", set_nested(("controls", 0, "kind"), "bad"))
    mutate("control-dup-kind", set_nested(("controls", 1, "kind"), "matched_features"))
    mutate("control-missing-kind", lambda d: d.__setitem__("controls", [c for c in d["controls"] if c["kind"] != "zero_features"]))
    mutate("control-matched-unknown", set_nested(("controls", 0, "feature_id"), "missing"))
    mutate("control-matched-digest", set_nested(("controls", 0, "feature_sha256"), "0" * 64))
    mutate("control-zero-with-id", set_nested(("controls", 2, "feature_id"), "feat-a"))

    for f in OUTCOME_FIELDS:
        mutate("missing-outcome-" + f, del_nested(("outcomes", f)))
    mutate("unknown-outcome", set_nested(("outcomes", "extra"), 1))
    mutate("outcome-wer-high", set_nested(("outcomes", "intelligibility_wer"), 1.1))
    mutate("outcome-wer-neg", set_nested(("outcomes", "intelligibility_wer"), -0.1))
    mutate("outcome-stoi-high", set_nested(("outcomes", "stoi"), 1.1))
    mutate("outcome-mos-low", set_nested(("outcomes", "naturalness_mos"), 0.9))
    mutate("outcome-cos-low", set_nested(("outcomes", "identity_similarity_cosine"), -1.1))
    mutate("outcome-align-neg", set_nested(("outcomes", "alignment_samples"), -1))
    mutate("outcome-first-neg", set_nested(("outcomes", "first_output_ms"), -1.0))
    mutate("outcome-tail-neg", set_nested(("outcomes", "tail_ms"), -1.0))
    mutate("outcome-peak-high", set_nested(("outcomes", "peak_abs"), 5.0))
    mutate("outcome-clip-high", set_nested(("outcomes", "clipped_fraction"), 1.1))
    mutate("outcome-nonfinite", set_nested(("outcomes", "nonfinite_count"), 1))
    mutate("outcome-sample-zero", set_nested(("outcomes", "sample_count"), 0))
    mutate("outcome-sample-bool", set_nested(("outcomes", "sample_count"), True))
    mutate("outcome-rate-bad", set_nested(("outcomes", "output_sample_rate_hz"), 12345))

    for f in RIGHTS_FIELDS:
        mutate("missing-rights-" + f, del_nested(("rights", f)))
    mutate("unknown-rights", set_nested(("rights", "extra"), 1))
    mutate("rights-consent-empty", set_nested(("rights", "consent_reference"), ""))
    mutate("rights-availability-empty", set_nested(("rights", "input_availability"), ""))
    mutate("rights-output-empty", set_nested(("rights", "output_use"), ""))
    mutate("rights-commercial-empty", set_nested(("rights", "commercial_terms_review"), ""))
    mutate("rights-terms-empty", set_nested(("rights", "terms_review"), ""))
    mutate("rights-listening-empty", set_nested(("rights", "listening_protocol"), ""))
    mutate("rights-panel-zero", set_nested(("rights", "listening_panel_size"), 0))
    mutate("rights-panel-bool", set_nested(("rights", "listening_panel_size"), True))

    summary = {
        "case_count": len(cases),
        "rejected_count": sum(1 for c in cases if c["status"] == "rejected"),
        "accepted_schema_controls": 1 if accepted["accepted"] else 0,
        "qualifying_results": 0,
        "state_advanced_on_rejection": False,
        "runtime_invoked": False,
        "audio_read": False,
        "feature_input_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "network_used": False,
    }
    return {"control": {"id": "schema-control", "status": "accepted_schema_control", "evidence_class": "synthetic_schema_control_not_evidence", "qualifies": False, "accepted": accepted["accepted"], "checks": accepted["checks"]}, "cases": cases, "summary": summary}


def admission_contract_block() -> dict:
    return {
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "source_fields": list(SOURCE_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "feature_fields": list(FEATURE_FIELDS),
        "control_fields": list(CONTROL_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "feature_kinds": list(FEATURE_KINDS),
        "input_sample_rates_hz": list(INPUT_SAMPLE_RATES),
        "output_sample_rates_hz": list(OUTPUT_SAMPLE_RATES),
        "max_seed": MAX_SEED,
        "max_frame_count": MAX_FRAME_COUNT,
        "max_alignment_samples": MAX_ALIGNMENT,
        "max_peak": MAX_PEAK,
        "max_panel": MAX_PANEL,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "audio_read": False,
        "feature_input_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "network_used": False,
    }


def _disposition() -> dict:
    return {
        "decision": "DEFER", "default_enabled": False, "expose_as_processor": False,
        "incomplete": True, "missing_result_qualifies": False, "not_qualified": True,
        "production_exposure": "DEFER", "promotion": "defer", "proposal_only": True,
        "qualification_status": "not_qualified", "registered": False, "status": "incomplete",
    }


def _qualification() -> dict:
    return {
        "status": "not_qualified", "readiness": "incomplete", "not_qualified": True,
        "real_result_present": False, "quality_result": False, "intelligibility_result": False,
        "conditioning_result": False, "identity_similarity_result": False, "naturalness_result": False,
        "listening_result": False, "alignment_result": False, "first_output_or_tail_result": False,
        "device_timing_result": False, "benchmark_result": False, "release_claim": False,
        "source_present": False, "exact_source_present": False, "weights_present": False,
        "runtime_present": False, "all_release_gates_blocked": True, "missing_result_promoted": False,
    }


def _required_results() -> dict:
    return {
        "quality_result_present": False, "intelligibility_result_present": False,
        "conditioning_result_present": False, "identity_similarity_result_present": False,
        "naturalness_result_present": False, "listening_result_present": False,
        "alignment_result_present": False, "first_output_or_tail_result_present": False,
        "device_timing_result_present": False, "benchmark_result_present": False,
        "reference_consent_present": False, "exact_source_present": False,
        "weights_present": False, "runtime_present": False, "release_claim": False,
        "no_result_qualifies": True,
    }


def _scope() -> dict:
    return {
        "task_local_only": True, "source_present": False, "exact_source_present": False,
        "weights_present": False, "runtime_present": False, "real_corpus": False,
        "weights_loaded": False, "model_executed": False, "audio_read": False,
        "feature_input_read": False, "quality_scored": False, "intelligibility_scored": False,
        "conditioning_scored": False, "identity_scored": False, "naturalness_scored": False,
        "listening": False, "device_timing": False, "benchmark": False, "release_claim": False,
        "download_attempted": False, "network_used": False,
    }


def _boundary() -> dict:
    return {
        "task_local_only": True, "enabled_by_default": False, "default_selected": False,
        "registered": False, "provider_registration": False, "processor_exposure": False,
        "descriptor_registry_change": False, "installed_v0_behavior_change": False,
        "public_api_abi_change": False, "shared_cmakelists_change": False,
        "ci_workflow_change": False, "files_outside_task_directory_written": False,
        "real_weights_or_runtime": False, "listening": False,
    }


def build_contract() -> dict:
    gates = [dict(g, status="blocked", qualifies=False, linked_row=dict(BOARD_ROW_PROJECTION)) for g in RELEASE_GATES]
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "profile_phrases": list(PROFILE_PHRASES),
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "write_scope": WRITE_SCOPE,
        "exact_scope": "Task-local WORLD vocoder feasibility blocker evidence: pinned sources, absence probes, fail-closed Voice admission, blocked profile accounting, and eight blocked release gates. No source/build/runtime/audio/result.",
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_file_pinned": False,
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(r) for r in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_status_is_observation_only": True,
        "absence_policy": {"any_present_probe_blocks_shipping": True, "download_attempted": False, "network_used": False, "fixed_probe_list_only": True, "recursive_workspace_walk": False},
        "absence_probes": list(ABSENCE_PROBES),
        "home_absence_probes": list(HOME_ABSENCE_PROBES),
        "required_artifacts": [dict(a) for a in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "release_gates": gates,
        "voice_profile_requirements": [dict(r) for r in VOICE_PROFILE_ROWS],
        "quality_outcomes": [dict(r) for r in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(r) for r in TIMING_ROWS],
        "admission_contract": admission_contract_block(),
        "non_claims": list(NON_CLAIMS),
        "scope": _scope(),
        "boundary": _boundary(),
        "disposition": _disposition(),
        "qualification": _qualification(),
        "required_results": _required_results(),
        "reproduction": {
            "interpreter": f"Python {REQUIRED_INTERPRETER}, standard library only",
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 -m unittest -v test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 verify.py",
            ],
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
        },
    }


CONTRACT_FIELDS = tuple(build_contract().keys())


def validate_contract(document: dict) -> None:
    if set(document) != set(CONTRACT_FIELDS):
        missing = sorted(set(CONTRACT_FIELDS) - set(document))
        extra = sorted(set(document) - set(CONTRACT_FIELDS))
        raise ValueError("contract_field_mismatch:" + (missing[0] if missing else extra[0]))
    _no_floats(document)
    if document["schema_id"] != CONTRACT_SCHEMA_ID or document["contract_id"] != CONTRACT_ID:
        raise ValueError("contract_schema_mismatch")
    if document["task"] != TASK or document["component"] != COMPONENT_ID or document["mode"] != MODE:
        raise ValueError("contract_identity_mismatch")
    if document["decision"] != "DEFER" or document["status"] != "incomplete" or document["qualification_status"] != "not_qualified":
        raise ValueError("contract_disposition_mismatch")
    if document["proposal_only"] is not True or document["board_file_pinned"] is not False:
        raise ValueError("contract_policy_mismatch")
    if document["board_row_projection"] != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_projection_mismatch")
    if document["board_row_sha256"] != board_row_digest(BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_digest_mismatch")
    if document["linked_rows_sha256"] != linked_rows_digest():
        raise ValueError("contract_linked_rows_mismatch")
    if len(document["release_gates"]) != 8:
        raise ValueError("contract_gate_count")
    for i, g in enumerate(document["release_gates"], 1):
        if g["id"] != f"RG-{i:02d}" or g["status"] != "blocked" or g["qualifies"] is not False or not g["reopen_condition"]:
            raise ValueError("contract_gate_invalid")
        if g["linked_row"] != BOARD_ROW_PROJECTION:
            raise ValueError("contract_gate_linked_row")
    if len(document["required_artifacts"]) != 6 or document["required_artifacts"][0]["present"] is not True:
        raise ValueError("contract_artifacts")
    for a in document["required_artifacts"][1:]:
        if a["present"] is not False or a["verified"] is not False or a["blocked"] is not True:
            raise ValueError("contract_artifact_blocked")
    if len(document["exact_blockers"]) != 5:
        raise ValueError("contract_blockers")
    for b in document["exact_blockers"]:
        if b["status"] != "open" or b["qualifies"] is not False or not b["required_action"]:
            raise ValueError("contract_blocker")
    for rows, n in (("voice_profile_requirements", 8), ("quality_outcomes", 4), ("timing_requirements", 4)):
        if len(document[rows]) != n:
            raise ValueError("contract_row_count:" + rows)
    for row in document["voice_profile_requirements"]:
        if row["status"] != "blocked":
            raise ValueError("contract_voice_row")
    for row in document["quality_outcomes"] + document["timing_requirements"]:
        if row["status"] != "blocked" or row["value"] is not None:
            raise ValueError("contract_outcome_row")
    if document["admission_contract"] != admission_contract_block():
        raise ValueError("contract_admission_contract_mismatch")
    if document["source_pins"] != SOURCE_PINS or document["boundary_pins"] != BOUNDARY_PINS:
        raise ValueError("contract_pins_mismatch")
    if document["scope"] != _scope() or document["boundary"] != _boundary():
        raise ValueError("contract_scope_boundary_mismatch")


def build_report() -> dict:
    contract = build_contract()
    workspace_rows = absence_probes(AUDIO_ROOT)
    home_rows = home_absence_probes()
    admission = admission_controls()
    if not admission["control"]["accepted"]:
        raise ValueError("schema_control_not_accepted")
    for case in admission["cases"]:
        if case["status"] != "rejected":
            raise ValueError("admission_case_not_rejected:" + case["id"])
    source_rows = pin_rows(SOURCE_PINS, AUDIO_ROOT)
    boundary_rows = pin_rows(BOUNDARY_PINS, WORKTREE)
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "required_results": contract["required_results"],
        "source_pins": {r["path"]: {"sha256": r["sha256"], "actual": r["actual"], "verified": r["verified"]} for r in source_rows},
        "boundary_pins": {r["path"]: {"sha256": r["sha256"], "actual": r["actual"], "verified": r["verified"]} for r in boundary_rows},
        "absence_evidence": {"summary": absence_summary(workspace_rows, home_rows), "probes": workspace_rows, "home_probes": home_rows},
        "admission": admission,
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "voice_profile": {"profile": PROFILE_LABEL, "rows": contract["voice_profile_requirements"]},
        "quality_outcomes": {"rows": contract["quality_outcomes"]},
        "timing": {"rows": contract["timing_requirements"]},
        "linked_row_identity": {
            "projection": BOARD_ROW_PROJECTION,
            "sha256": board_row_digest(BOARD_ROW_PROJECTION),
            "linked_rows": [dict(r) for r in LINKED_ROWS],
            "linked_rows_sha256": linked_rows_digest(),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
    }
    _no_floats(report)
    return report


def canonical_report(document: dict | None = None) -> tuple[str, str]:
    report = build_report() if document is None else document
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


LOCAL_PIN_FILES = (
    "LICENSES.md", "README.md", "SOURCES.sha256.license", "contract.json",
    "contract.json.license", "reference.py", "report.json",
    "report.json.license", "report.json.sha256", "report.json.sha256.license",
    "run.py", "test_reference.py", "verify.py",
)


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for rel, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(AUDIO_ROOT / rel)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + rel)
        rows.append(("source:" + rel, actual))
    for rel, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(WORKTREE / rel)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + rel)
        rows.append((rel, actual))
    for name in LOCAL_PIN_FILES:
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((TASK_PREFIX + name, sha256_file(path)))
    lines = [
        "# SHA-256 pins for SDK-WORLD-VOCODER task-local blocker evidence.",
        "# source: paths are relative to AUDIO_ROOT; other paths are SDK-worktree relative.",
        "# The mutable shared board is not pinned; only stable row identity is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


README_DIGEST_KEYS = ("contract.json", "report.json", "report.json.sha256")


def readme_digests() -> dict[str, str]:
    return {k: sha256_file(HERE / k) for k in README_DIGEST_KEYS}


def update_readme_digests(text: str) -> str:
    digests = readme_digests()
    for key, digest in digests.items():
        pattern = re.compile(rf"(`{re.escape(key)}` SHA-256: `)[0-9a-f]{{64}}(`)")
        repl = rf"\g<1>{digest}\g<2>"
        new_text, n = pattern.subn(repl, text, count=1)
        if n != 1:
            raise ValueError("readme_digest_marker_missing:" + key)
        text = new_text
    return text


def verify_readme_digests(text: str) -> None:
    digests = readme_digests()
    for key, digest in digests.items():
        marker = f"`{key}` SHA-256: `{digest}`"
        if marker not in text:
            raise ValueError("readme_digest_mismatch:" + key)
