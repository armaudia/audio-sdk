# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-TD-PSOLA.

Standard library only. TD-PSOLA is a classic speech time/pitch modification
method (Moulines & Charpentier, 1990). This package records a bounded DEFER
blocker: no exact licensed source snapshot, pinned runtime, rights-cleared
inputs, reproduced output or matched Rate-profile evidence is staged for
qualification. It never downloads, imports candidate code, loads weights,
reads audio, runs device timing, or claims a result.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-TD-PSOLA"
TASK_TITLE = "TD-PSOLA"
COMPONENT_ID = "td-psola"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
TASK_PREFIX = "docs/task-evidence/td-psola/"
WRITE_SCOPE = "docs/task-evidence/td-psola/ only"
CONTRACT_SCHEMA_ID = "audio-sdk/td-psola-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/td-psola-readiness/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/td-psola-asset-declaration/0.1"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = "swarm/SDK-TD-PSOLA"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.11.5"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
MUTABLE_BOARD_FIELDS = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        if (candidate / BOARD_TASK_ROW).is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/psola-praat/README.md":
        "7e64ec614937533168ef31c34d4c8ec4aa7d6d52670e663f0f88ce5f4ec7a6ef",
    "docs/task-evidence/psola-praat/report.json":
        "c8126e10ec682b6960bc379a2d5a5db9222abedcd37b6fe62d176c47e07de614",
}

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

WORKSPACE_PROBES = (
    "data/checkouts/td-psola",
    "data/checkouts/TD-PSOLA",
    "data/checkouts/praat",
    "data/checkouts/parselmouth",
    "data/models/td-psola",
    "data/reference/td-psola",
    "data/audio/td-psola",
    "data/runs/td-psola",
    "research/td-psola",
)
WORKTREE_PROBES = (
    "adapters/td-psola",
    "schemas/providers/td-psola",
    "third_party/td-psola",
    "third_party/praat",
    "third_party/parselmouth",
)
HOME_PROBES = (
    "~/.cache/td-psola",
    "~/.cache/praat",
    "~/.cache/parselmouth",
)

NON_CLAIMS = [
    "No TD-PSOLA source, Praat/Parselmouth runtime, checkpoint, model, license text or executable artifact is present, imported, loaded or executed.",
    "No real audio, corpus, synthetic speech, music, candidate output or listening result is read, generated or produced.",
    "No TD-PSOLA rate, duration, pitch, transient, preservation, device-timing or benchmark result is reproduced.",
    "The caller-supplied asset declaration is a fail-closed shape check only; it never resolves a path, hashes external bytes, admits a presence claim or grants qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build, CI workflow, board or handoff change exists.",
    "Research prose, candidate matrices and sibling evidence are source-reported context only and are not promoted to measured evidence.",
    "No network access or download is attempted; absent artifacts are not fabricated, reconstructed, mirrored or substituted.",
    "Sibling PSOLA/Praat, DiffATSM, Neural ATSM, STSM-FiLM or other rate evidence is not inherited, pooled or treated as a TD-PSOLA result.",
]

HISTORICAL_EVIDENCE = (
    {
        "source": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "class": "candidate_screen_source_reported",
        "admitted_as_result": False,
        "boundary": "Playback-speed candidate note describes TD-PSOLA as speech-only/reference context and records local Praat/PSOLA stack as slow/heavy; it is not a qualified SDK result.",
    },
    {
        "source": "REALTIME_COMPONENT_CANDIDATES.md",
        "class": "component_candidate_source_reported",
        "admitted_as_result": False,
        "boundary": "Component candidate registry mentions PSOLA/TD-PSOLA context only; it is not a reproduced TD-PSOLA run, runtime or qualification.",
    },
    {
        "source": "research/tsm-followup-20261101/README.md",
        "class": "tsm_followup_context_source_reported",
        "admitted_as_result": False,
        "boundary": "TSM follow-up records adjacent evaluated stretchers and blocked neural candidates; no TD-PSOLA runnable artifact, output or measurement is present in this package.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Inventory marks td-psola as considered, sdk-reference, rate profile; it is not a result.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": "Defines the Rate profile requirements. No rate measurement, control, pitch, buffering, preservation or device-timing record exists for TD-PSOLA.",
    },
)

PEER_SEPARATION = (
    {
        "component": "psola-praat",
        "task": "SDK-PSOLA-PRAAT",
        "path": "docs/task-evidence/psola-praat/report.json",
        "class": "separate_task_local_reference",
        "decision": "task-local-reference",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "PSOLA/Praat is a separate task-local synthetic reference with its own blockers and synthetic-fixture-only status. No metric, digest, fixture or qualification is inherited or pooled here.",
    },
    {
        "component": "diffatsm",
        "task": "SDK-DIFFATSM",
        "path": "docs/task-evidence/diffatsm/report.json",
        "class": "separate_neural_tsm_candidate",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "DiffATSM is a distinct diffusion-based raw-audio TSM candidate. No source, checkpoint, rejection, metric or gate outcome is inherited or pooled here.",
    },
)

BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "title": "No exact licensed source snapshot or runtime",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01", "RG-02"],
        "statement": "No exact TD-PSOLA/Praat/Parselmouth source snapshot, immutable revision, reviewed license text, pinned offline runtime or install digest is staged at any probed path.",
        "required_action": "Supply an immutable source/runtime snapshot with reviewed license/notice records, wheel hashes, platform, interpreter and clean-room install proof.",
        "reopen_condition": "Only caller-supplied exact artifacts with verified identity, rights and matched evidence can reopen this blocker.",
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "title": "No exact audio task geometry and causal contract",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-06"],
        "statement": "No exact audio-in/audio-out geometry, sample rate, frame/hop, lookahead, latency, reset/drain, epoch/pitch-mark policy or causal streaming contract is verified for an SDK-facing TD-PSOLA reference.",
        "required_action": "Record exact geometry and causal/streaming semantics, or explicitly separate offline reference from causal streaming work as required by the inventory note.",
        "reopen_condition": "Only caller-supplied exact artifacts with verified identity, rights and matched evidence can reopen this blocker.",
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "title": "No reviewed rights or rights-cleared inputs",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-04"],
        "statement": "No code license review, Praat/Parselmouth redistribution decision, rights-cleared speech/music inputs, consent, or derived-output terms are staged or reviewed.",
        "required_action": "Provide reviewed code terms and a digest-pinned rights-cleared input set with consent, evaluation and redistribution decisions.",
        "reopen_condition": "Only caller-supplied exact artifacts with verified identity, rights and matched evidence can reopen this blocker.",
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "title": "No reproduced TD-PSOLA rate result",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-05", "RG-06"],
        "statement": "No deterministic candidate execution, output hash, source/output mapping, duration, pitch, transient, buffering, rebuffer/drift/final-partial or speech-preservation measurement exists.",
        "required_action": "Execute the pinned runtime offline and record deterministic outputs and all Rate-profile measurements on a rights-cleared cohort.",
        "reopen_condition": "Only caller-supplied exact artifacts with verified identity, rights and matched evidence can reopen this blocker.",
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "title": "No matched cohort, timing, listening or release evidence",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-07", "RG-08"],
        "statement": "No matched same-condition cohort, device timing/resources, authorized listening/labeled screen, provider intake, clean-install proof or independent review exists.",
        "required_action": "Provide matched evidence, separate mode/platform timing and listening/screen evidence, then open a separate OFF-by-default intake with independent review.",
        "reopen_condition": "Only caller-supplied exact artifacts with verified identity, rights and matched evidence can reopen this blocker.",
    },
)

GATES = (
    {"id": "RG-01", "title": "source_revision_and_license_provenance", "statement": "No exact TD-PSOLA source/runtime revision or reviewed license provenance is staged.", "reopen_condition": "Stage immutable source/runtime revisions with complete license, notice and README records and record independent review."},
    {"id": "RG-02", "title": "pinned_runtime_and_task_geometry", "statement": "No pinned offline runtime or exact audio/casual task geometry is verified.", "reopen_condition": "Provide a locked offline runtime and exact geometry with deterministic settings, install location and clean-room import digest."},
    {"id": "RG-03", "title": "assets_and_dependency_manifest", "statement": "No exact asset/dependency manifest with byte counts and SHA-256 values is staged.", "reopen_condition": "Stage every required source, model/asset or dependency file with immutable revision, byte counts and SHA-256 values."},
    {"id": "RG-04", "title": "rights_cleared_inputs_and_terms", "statement": "No reviewed rights or rights-cleared inputs are staged.", "reopen_condition": "Freeze permitted, digest-pinned inputs with consent, corpus, evaluation, derived-output and redistribution decisions plus code/data terms."},
    {"id": "RG-05", "title": "reference_execution_and_output_validity", "statement": "No deterministic TD-PSOLA execution or output-validity evidence exists.", "reopen_condition": "Execute the pinned runtime offline and record output hashes, finite/length behavior, exact repeats and peak/RSS values."},
    {"id": "RG-06", "title": "rate_profile_against_real_runtime", "statement": "The Rate profile is unsatisfied: no real runtime rate evidence exists.", "reopen_condition": "Run every Rate-profile case on a rights-cleared cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window."},
    {"id": "RG-07", "title": "mode_platform_timing_resources_and_listening", "statement": "No mode/platform timing, resources, pacing or listening/labeled screen evidence exists.", "reopen_condition": "Measure each mode/platform separately with timing/resources/pacing and complete authorized listening or a labeled screen."},
    {"id": "RG-08", "title": "provider_intake_public_surface_and_release", "statement": "No provider intake, public surface decision or independent review exists.", "reopen_condition": "Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear."},
)

RATE_ROWS = (
    ("RATE-01", "Source/output mapping for the exact runtime.", "No TD-PSOLA runtime, output or exact audio geometry exists; source/output mapping cannot be measured."),
    ("RATE-02", "Target and actual duration for constant and changing rates.", "No TD-PSOLA runtime or candidate output exists; duration cannot be measured."),
    ("RATE-03", "Pitch preservation or shift for the exact runtime.", "No TD-PSOLA output or listening/analysis result exists; pitch cannot be measured."),
    ("RATE-04", "Transient audibility proxy or authorized listening.", "No candidate output and no authorized listening/labeled screen exists."),
    ("RATE-05", "Playback buffering, fill/flush and deadline behaviour.", "No device, scheduler, fill/flush or deadline measurement exists."),
    ("RATE-06", "1x identity control.", "No runtime exists, so no identity/passthrough control was run."),
    ("RATE-07", "Rate changes, including step and ramp profiles.", "No runtime exists, so no step/ramp execution was run."),
    ("RATE-08", "Unfamiliar speech material.", "No rights-cleared unfamiliar speech input exists."),
    ("RATE-09", "Music material and a synthetic music negative control.", "No rights-cleared music and no synthetic music negative control execution exists."),
    ("RATE-10", "Silence and empty input.", "No candidate runtime execution exists for silence/empty input."),
    ("RATE-11", "Rebuffer, drift and the final partial window.", "No playback, buffer or final-partial execution exists."),
    ("RATE-12", "Pause or filler decisions tied to source timestamps and speech preservation.", "No timestamped pause/filler policy or speech-preservation measurement exists."),
    ("RATE-13", "Separate paired, unpaired, synthetic, human and source-reported evidence.", "The report keeps source-reported, schema-only, missing-real and sibling sections distinct; no category is pooled."),
)

EVIDENCE_SNIPPETS = (
    ("cpp-library/pipeline-validation/playback-speed-candidates.md", "TD-PSOLA"),
    ("cpp-library/pipeline-validation/playback-speed-candidates.md", "Praat's implementation is GPL"),
    ("REALTIME_COMPONENT_CANDIDATES.md", "PSOLA"),
    ("research/tsm-followup-20261101/README.md", "PSOLA"),
    ("audio-benchmark-platform/plan/INVENTORY.json", "td-psola"),
    ("audio-benchmark-platform/plan/INVENTORY.json", "SDK-TD-PSOLA"),
    ("audio-benchmark-platform/plan/swarm/VERIFICATION.md", "Measure source/output mapping"),
)

# ---------------------------------------------------------------------------
# Strict JSON / hashing
# ---------------------------------------------------------------------------

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
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


def loads_strict(text: str) -> dict:
    if text.startswith("\ufeff"):
        raise ValueError("byte_order_mark")
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
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
    value = loads_strict(text)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


# ---------------------------------------------------------------------------
# Board identity and scope
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


def linked_rows(path: Path | None = None) -> list[dict]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    result: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_absent:" + row_id)
        result.append(_project(row, require_component=row_id == TASK))
    return result


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None
                         else board_row_projection())


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *args],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path, refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


def _probe(path: Path, label: str, workspace: bool, worktree: bool, home: bool) -> dict:
    return {
        "path": label,
        "present": path.exists(),
        "searched_workspace": workspace,
        "searched_sdk_worktree": worktree,
        "searched_home_cache": home,
    }


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    for path in WORKSPACE_PROBES:
        rows.append(_probe(AUDIO_ROOT / path, path, True, False, False))
    for path in WORKTREE_PROBES:
        rows.append(_probe(WORKTREE / path, path, False, True, False))
    for path in HOME_PROBES:
        expanded = Path(os.path.expanduser(path))
        rows.append(_probe(expanded, path, False, False, True))
    return rows


def absence_summary() -> dict:
    probes = absence_probes()
    return {
        "all_absent": all(not row["present"] for row in probes),
        "audio_read": False,
        "candidate_module_imported": False,
        "candidate_runtime_executed": False,
        "download_attempted": False,
        "fixed_probe_list_only": True,
        "home_probe_count": len(HOME_PROBES),
        "network_used": False,
        "present_count": sum(1 for row in probes if row["present"]),
        "probe_count": len(probes),
        "probes": probes,
        "recursive_workspace_walk": False,
        "weights_loaded": False,
        "workspace_probe_count": len(WORKSPACE_PROBES),
        "worktree_probe_count": len(WORKTREE_PROBES),
    }

# ---------------------------------------------------------------------------
# Evidence checks and admission
# ---------------------------------------------------------------------------

class AdmissionError(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code + (":" + detail if detail else ""))
        self.code = code
        self.detail = detail


def evidence_snippet_check() -> dict:
    checks = []
    for relative, phrase in EVIDENCE_SNIPPETS:
        path = AUDIO_ROOT / relative
        present = path.is_file() and phrase in path.read_text(encoding="utf-8", errors="replace")
        checks.append({"path": relative, "phrase": phrase, "present": present})
    return {"all_present": all(row["present"] for row in checks), "checks": checks, "count": len(checks)}


def evidence_presence() -> dict:
    snippets = evidence_snippet_check()
    return {
        "all_snippets_present": snippets["all_present"],
        "snippet_checks": snippets["checks"],
        "snippet_count": snippets["count"],
        "source_snapshot_present": False,
        "runtime_present": False,
        "license_text_present": False,
        "weights_present": False,
        "paper_reference_recorded": False,
        "candidate_output_present": False,
    }


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise AdmissionError(code, detail)


def _expect_dict(value: Any, code: str) -> dict:
    if not isinstance(value, dict):
        raise AdmissionError(code)
    return value


def _expect_bool(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise AdmissionError(code)
    return value


def _expect_str(value: Any, code: str) -> str:
    if not isinstance(value, str):
        raise AdmissionError(code)
    return value


def _expect_int(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError(code)
    return value


def _canonical_decimal(value: Any, label: str) -> str:
    text = _expect_str(value, "peak_not_string:" + label)
    _require(DECIMAL.match(text) is not None, "peak_not_canonical", label)
    if "." in text:
        whole, frac = text.split(".", 1)
        _require(frac != "" and not frac.endswith("0"), "peak_not_canonical", label)
    else:
        whole = text
    _require(whole == "0" or not whole.startswith("0"), "peak_not_canonical", label)
    _require(float(text) <= 1.0, "peak_out_of_range", label)
    return text


def declaration_schema() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "accepted_control_checks": 20,
        "accepted_control_qualifies": False,
        "accepted_control_sha256": object_digest(accepted_declaration()),
        "accepted_control_status": "accepted_unpopulated",
        "all_rejected": True,
        "assets_loaded": False,
        "candidate_fields": ["name", "family", "paper_reference", "audio_only", "rate_only_estimator"],
        "disposition_fields": ["decision", "qualifies"],
        "fields": ["schema_id", "declaration_id", "candidate", "source", "runtime", "geometry", "rights", "disposition"],
        "geometry_fields": ["declared", "sample_rate_hz", "frame_samples", "hop_samples", "channels"],
        "presence_claims_rejected": True,
        "purpose": "Defines the exact caller-supplied asset declaration a future intake must populate and verify externally. This package accepts only the unpopulated declaration and never resolves or loads an asset.",
        "rejection_cases": 41,
        "rights_fields": ["code", "weights_or_assets", "training_data", "inputs", "output_use", "redistribution", "review_reference"],
        "runtime_fields": ["declared_present", "python_version", "platform", "device", "lock_sha256"],
        "source_fields": ["declared_present", "revision", "license_sha256", "source_sha256"],
        "strict_json_all_rejected": True,
        "strict_json_cases": 9,
    }


def accepted_declaration() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "declaration_id": "unpopulated",
        "candidate": {
            "name": "TD-PSOLA",
            "family": "classical_tsm",
            "paper_reference": "Moulines and Charpentier 1990",
            "audio_only": True,
            "rate_only_estimator": False,
        },
        "source": {
            "declared_present": False,
            "revision": None,
            "license_sha256": None,
            "source_sha256": None,
        },
        "runtime": {
            "declared_present": False,
            "python_version": None,
            "platform": None,
            "device": None,
            "lock_sha256": None,
        },
        "geometry": {
            "declared": False,
            "sample_rate_hz": None,
            "frame_samples": None,
            "hop_samples": None,
            "channels": None,
        },
        "rights": {
            "code": False,
            "weights_or_assets": False,
            "training_data": False,
            "inputs": False,
            "output_use": False,
            "redistribution": False,
            "review_reference": None,
        },
        "disposition": {
            "decision": "DEFER",
            "qualifies": False,
        },
    }


def validate_declaration(value: Any) -> dict:
    doc = _expect_dict(value, "not_object")
    expected_keys = set(declaration_schema()["fields"])
    _require(set(doc.keys()) == expected_keys, "unknown_or_missing_field")
    _require(doc["schema_id"] == DECLARATION_SCHEMA_ID, "schema_id_mismatch")
    _require(doc["declaration_id"] == "unpopulated", "declaration_id_mismatch")

    candidate = _expect_dict(doc["candidate"], "candidate_not_object")
    _require(set(candidate.keys()) == set(declaration_schema()["candidate_fields"]), "candidate_fields_mismatch")
    _require(candidate["name"] == "TD-PSOLA", "candidate_name_mismatch")
    _require(candidate["family"] == "classical_tsm", "candidate_family_mismatch")
    _require(candidate["paper_reference"] == "Moulines and Charpentier 1990", "paper_reference_mismatch")
    _require(candidate["audio_only"] is True, "audio_only_mismatch")
    _require(candidate["rate_only_estimator"] is False, "rate_only_estimator_mismatch")

    source = _expect_dict(doc["source"], "source_not_object")
    _require(set(source.keys()) == set(declaration_schema()["source_fields"]), "source_fields_mismatch")
    _require(source["declared_present"] is False, "unverified_claim")
    _require(source["revision"] is None, "unverified_claim")
    _require(source["license_sha256"] is None, "unverified_claim")
    _require(source["source_sha256"] is None, "unverified_claim")

    runtime = _expect_dict(doc["runtime"], "runtime_not_object")
    _require(set(runtime.keys()) == set(declaration_schema()["runtime_fields"]), "runtime_fields_mismatch")
    _require(runtime["declared_present"] is False, "unverified_claim")
    _require(runtime["python_version"] is None, "unverified_claim")
    _require(runtime["platform"] is None, "unverified_claim")
    _require(runtime["device"] is None, "unverified_claim")
    _require(runtime["lock_sha256"] is None, "unverified_claim")

    geometry = _expect_dict(doc["geometry"], "geometry_not_object")
    _require(set(geometry.keys()) == set(declaration_schema()["geometry_fields"]), "geometry_fields_mismatch")
    _require(geometry["declared"] is False, "unverified_claim")
    _require(geometry["sample_rate_hz"] is None, "unverified_claim")
    _require(geometry["frame_samples"] is None, "unverified_claim")
    _require(geometry["hop_samples"] is None, "unverified_claim")
    _require(geometry["channels"] is None, "unverified_claim")

    rights = _expect_dict(doc["rights"], "rights_not_object")
    _require(set(rights.keys()) == set(declaration_schema()["rights_fields"]), "rights_fields_mismatch")
    for key in ["code", "weights_or_assets", "training_data", "inputs", "output_use", "redistribution"]:
        _require(rights[key] is False, "unverified_claim")
    _require(rights["review_reference"] is None, "unverified_claim")

    disposition = _expect_dict(doc["disposition"], "disposition_not_object")
    _require(set(disposition.keys()) == set(declaration_schema()["disposition_fields"]), "disposition_fields_mismatch")
    _require(disposition["decision"] == "DEFER", "premature_decision")
    _require(disposition["qualifies"] is False, "unverified_claim")
    return doc

def declaration_rejections() -> dict:
    base = accepted_declaration()
    cases = []

    def add(case_id: str, mutate, code: str, field: str) -> None:
        item = copy.deepcopy(base)
        mutated = mutate(item)
        candidate = item if mutated is None else mutated
        try:
            validate_declaration(candidate)
        except AdmissionError as error:
            cases.append({"id": case_id, "rejected": True, "code": error.code, "field": field})
            return
        except Exception as error:  # noqa: BLE001
            cases.append({"id": case_id, "rejected": True, "code": type(error).__name__, "field": field})
            return
        cases.append({"id": case_id, "rejected": False, "code": "accepted", "field": field})

    add("root_not_object", lambda d: [], "not_object", "declaration")
    add("missing_schema_id", lambda d: d.pop("schema_id"), "unknown_or_missing_field", "declaration.schema_id")
    add("missing_declaration_id", lambda d: d.pop("declaration_id"), "unknown_or_missing_field", "declaration.declaration_id")
    add("extra_top_key", lambda d: d.__setitem__("extra", True), "unknown_or_missing_field", "declaration.extra")
    add("bad_schema_id", lambda d: d.__setitem__("schema_id", "bad"), "schema_id_mismatch", "schema_id")
    add("bad_declaration_id", lambda d: d.__setitem__("declaration_id", "caller"), "declaration_id_mismatch", "declaration_id")
    add("wrong_candidate_name", lambda d: d["candidate"].__setitem__("name", "Praat"), "candidate_name_mismatch", "candidate.name")
    add("wrong_candidate_family", lambda d: d["candidate"].__setitem__("family", "neural"), "candidate_family_mismatch", "candidate.family")
    add("wrong_paper", lambda d: d["candidate"].__setitem__("paper_reference", "x"), "paper_reference_mismatch", "candidate.paper_reference")
    add("audio_only_false", lambda d: d["candidate"].__setitem__("audio_only", False), "audio_only_mismatch", "candidate.audio_only")
    add("rate_only_true", lambda d: d["candidate"].__setitem__("rate_only_estimator", True), "rate_only_estimator_mismatch", "candidate.rate_only_estimator")
    add("source_present_true", lambda d: d["source"].__setitem__("declared_present", True), "unverified_claim", "source.declared_present")
    add("source_revision_set", lambda d: d["source"].__setitem__("revision", "deadbeef"), "unverified_claim", "source.revision")
    add("source_license_set", lambda d: d["source"].__setitem__("license_sha256", "0" * 64), "unverified_claim", "source.license_sha256")
    add("source_digest_set", lambda d: d["source"].__setitem__("source_sha256", "0" * 64), "unverified_claim", "source.source_sha256")
    add("runtime_present_true", lambda d: d["runtime"].__setitem__("declared_present", True), "unverified_claim", "runtime.declared_present")
    add("runtime_python_set", lambda d: d["runtime"].__setitem__("python_version", "3.11.5"), "unverified_claim", "runtime.python_version")
    add("runtime_platform_set", lambda d: d["runtime"].__setitem__("platform", "linux"), "unverified_claim", "runtime.platform")
    add("runtime_lock_set", lambda d: d["runtime"].__setitem__("lock_sha256", "0" * 64), "unverified_claim", "runtime.lock_sha256")
    add("geometry_declared_true", lambda d: d["geometry"].__setitem__("declared", True), "unverified_claim", "geometry.declared")
    add("geometry_rate_set", lambda d: d["geometry"].__setitem__("sample_rate_hz", 16000), "unverified_claim", "geometry.sample_rate_hz")
    add("geometry_frame_set", lambda d: d["geometry"].__setitem__("frame_samples", 160), "unverified_claim", "geometry.frame_samples")
    add("geometry_hop_set", lambda d: d["geometry"].__setitem__("hop_samples", 160), "unverified_claim", "geometry.hop_samples")
    add("geometry_channels_set", lambda d: d["geometry"].__setitem__("channels", 1), "unverified_claim", "geometry.channels")
    add("rights_code_true", lambda d: d["rights"].__setitem__("code", True), "unverified_claim", "rights.code")
    add("rights_assets_true", lambda d: d["rights"].__setitem__("weights_or_assets", True), "unverified_claim", "rights.weights_or_assets")
    add("rights_training_true", lambda d: d["rights"].__setitem__("training_data", True), "unverified_claim", "rights.training_data")
    add("rights_inputs_true", lambda d: d["rights"].__setitem__("inputs", True), "unverified_claim", "rights.inputs")
    add("rights_output_true", lambda d: d["rights"].__setitem__("output_use", True), "unverified_claim", "rights.output_use")
    add("rights_redistribution_true", lambda d: d["rights"].__setitem__("redistribution", True), "unverified_claim", "rights.redistribution")
    add("rights_review_set", lambda d: d["rights"].__setitem__("review_reference", "ok"), "unverified_claim", "rights.review_reference")
    add("qualifies_true", lambda d: d["disposition"].__setitem__("qualifies", True), "unverified_claim", "disposition.qualifies")
    add("premature_admit", lambda d: d["disposition"].__setitem__("decision", "ADMIT"), "premature_decision", "disposition.decision")
    add("missing_runtime_section", lambda d: d.pop("runtime"), "unknown_or_missing_field", "declaration.runtime")
    add("extra_geometry_key", lambda d: d["geometry"].__setitem__("bit_depth", 16), "geometry_fields_mismatch", "geometry.bit_depth")
    add("float_value", lambda d: d["geometry"].__setitem__("sample_rate_hz", 16000.0), "unverified_claim", "geometry.sample_rate_hz")
    add("source_not_object", lambda d: d.__setitem__("source", []), "source_not_object", "source")
    add("runtime_not_object", lambda d: d.__setitem__("runtime", []), "runtime_not_object", "runtime")
    add("geometry_not_object", lambda d: d.__setitem__("geometry", []), "geometry_not_object", "geometry")
    add("rights_not_object", lambda d: d.__setitem__("rights", []), "rights_not_object", "rights")
    add("disposition_not_object", lambda d: d.__setitem__("disposition", []), "disposition_not_object", "disposition")

    # Keep exactly 41 cases for stable report shape.
    assert len(cases) == 41, len(cases)
    return {
        "all_rejected": all(row["rejected"] for row in cases),
        "rejection_cases": len(cases),
        "rejections": cases,
    }


def strict_json_rejections() -> dict:
    payloads = [
        ("duplicate_key", b'{"a":1,"a":2}'),
        ("nan_literal", b'{"a":NaN}'),
        ("infinity_literal", b'{"a":Infinity}'),
        ("negative_infinity_literal", b'{"a":-Infinity}'),
        ("trailing_data", b'{"a":1} 1'),
        ("byte_order_mark", b'\xef\xbb\xbf{"a":1}'),
        ("non_object_root", b'[1,2,3]'),
        ("empty_input", b'   '),
        ("unterminated", b'{"a":1'),
    ]
    rows = []
    for case_id, payload in payloads:
        try:
            parse_strict_json_text(payload)
        except Exception:  # noqa: BLE001
            rows.append({"id": case_id, "rejected": True})
            continue
        rows.append({"id": case_id, "rejected": False})
    return {
        "all_rejected": all(row["rejected"] for row in rows),
        "rejection_cases": len(rows),
        "rejections": rows,
    }

# ---------------------------------------------------------------------------
# Contract / report builders
# ---------------------------------------------------------------------------


def source_reported_identity() -> dict:
    return {
        "candidate": "TD-PSOLA",
        "candidate_family": "classical_tsm",
        "paper_reference": "Moulines and Charpentier 1990, Speech Communication 9(5-6):453-467",
        "source_reported_only": True,
        "audio_only_controller": True,
        "rate_only_estimator": False,
        "text_conditioned": False,
        "input_is_audio": True,
        "output_is_audio": True,
        "exact_method_source_present": False,
        "official_code_found": False,
        "official_weights_found": False,
        "task_matched_checkpoint_present": False,
        "runtime_present": False,
        "license_recorded": False,
        "license_text_staged": False,
        "immutable_revision_recorded": False,
        "identity_verified": False,
        "runnable_as_released": False,
        "source_reported_task": "pitch-synchronous time-domain time-scale modification / pitch modification for speech",
    }


def task_geometry() -> dict:
    return {
        "audio_input_path_verified": False,
        "audio_only_controller": True,
        "channels": None,
        "dtype": None,
        "frame_samples": None,
        "geometry_documented": False,
        "geometry_verified": False,
        "hop_samples": None,
        "latency_ms": None,
        "lookahead_samples": None,
        "pitch_mark_policy_verified": False,
        "profile_fit_reason": "TD-PSOLA is an audio-in/audio-out TSM method in principle, but no exact SDK-facing source snapshot, geometry, runtime, rights-cleared cohort or reproduced Rate-profile evidence is present in this package.",
        "rate_only_estimator": False,
        "rate_profile_fit": "plausible_unverified",
        "sample_rate_hz": None,
        "source_reported_input": "speech/audio waveform",
        "source_reported_output": "time-scaled and/or pitch-modified speech/audio waveform",
        "source_reported_reconstruction": "pitch-synchronous overlap-add grains",
        "state": "absent_unverified_audio_tsm_geometry",
    }


def public_v0_geometry() -> dict:
    return {
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
        "td_psola_mapping_present": False,
        "unchanged": True,
    }


def required_artifacts() -> list[dict]:
    return [
        {"id": "ART-01", "kind": "evidence_register_and_policy_boundary", "requirement": "Pinned inventory row, Rate acceptance profile, SDK delivery plan, research context and unchanged v0 contract boundary.", "present": True, "verified": True, "blocked": False, "revision": None, "sha256": None, "bytes": None},
        {"id": "ART-02", "kind": "exact_source_snapshot_and_license", "requirement": "Exact TD-PSOLA/Praat/Parselmouth or equivalent licensed implementation snapshot at immutable revision with reviewed license, notice and README records.", "present": False, "verified": False, "blocked": True, "revision": None, "sha256": None, "bytes": None},
        {"id": "ART-03", "kind": "pinned_runtime_and_geometry", "requirement": "Locked offline runtime and exact audio geometry/casual contract with interpreter, packages, wheel hashes, platform, device, dtype, determinism and reset/drain behavior.", "present": False, "verified": False, "blocked": True, "revision": None, "sha256": None, "bytes": None},
        {"id": "ART-04", "kind": "rights_cleared_inputs_and_terms", "requirement": "Reviewed code/data terms and digest-pinned rights-cleared speech/music/silence inputs with consent, evaluation and redistribution decisions.", "present": False, "verified": False, "blocked": True, "revision": None, "sha256": None, "bytes": None},
        {"id": "ART-05", "kind": "reproduced_rate_and_output_results", "requirement": "Deterministic reproduced output with source/output mapping, duration, pitch, transient, buffering, silence, rebuffer, drift, final-partial and preservation results.", "present": False, "verified": False, "blocked": True, "revision": None, "sha256": None, "bytes": None},
        {"id": "ART-06", "kind": "matched_cohort_timing_listening_and_review", "requirement": "Matched same-condition cohort, mode/platform timing/resources, authorized listening or labeled screen, and independent exact-head review.", "present": False, "verified": False, "blocked": True, "revision": None, "sha256": None, "bytes": None},
        {"id": "ART-07", "kind": "provider_intake_and_public_surface", "requirement": "Separate versioned OFF-by-default provider intake with clean-install proof, empty defaults, no shared-build change and independent review.", "present": False, "verified": False, "blocked": True, "revision": None, "sha256": None, "bytes": None},
    ]


def release_gates() -> list[dict]:
    linked = board_row_projection()
    rows = []
    for gate in GATES:
        rows.append({
            "id": gate["id"],
            "title": gate["title"],
            "status": "blocked",
            "qualifies": False,
            "statement": gate["statement"],
            "reopen_condition": gate["reopen_condition"],
            "linked_row": linked,
        })
    return rows


def exact_blockers() -> list[dict]:
    rows = []
    for blocker in BLOCKERS:
        rows.append(dict(blocker))
    return rows


def rate_profile() -> dict:
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": {
            "all_phrases_present": evidence_snippet_check()["all_present"],
            "path": PROFILE_SOURCE_REL,
            "phrases_present": list(PROFILE_PHRASES),
            "row_count": 1,
            "unique_row": True,
        },
        "profile_satisfied": False,
        "rate_result_present": False,
        "real_results": 0,
        "synthetic_results": 0,
        "synthetic_envelope_only": False,
        "surrogate_present": False,
        "candidate_geometry": None,
        "candidate_duration_result": None,
        "candidate_pitch_result": None,
        "candidate_transient_result": None,
        "candidate_buffering_result": None,
        "candidate_preservation_result": None,
        "requirement_rows": [
            {
                "id": row_id,
                "requirement": requirement,
                "status": "documented" if row_id == "RATE-13" else "blocked",
                "qualifies": False,
                "evidence": evidence,
            }
            for row_id, requirement, evidence in RATE_ROWS
        ],
    }


def matched_evidence() -> dict:
    return {
        "candidate_profile_fit": "plausible_unverified",
        "classes_pooled": False,
        "evidence_classes": [
            "source_reported_candidate_screen",
            "schema_only_declaration_control",
            "missing_real_candidate_result",
            "separate_sibling_reference",
            "unchanged_v0_contract",
        ],
        "listening_or_labeled_screen_present": False,
        "matched_baseline_present": False,
        "matched_cohort_present": False,
        "paired_clean_reference_present": False,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "required_separation": "Source-reported prose, schema-only declarations, missing real measurements and sibling evidence stay in distinct sections and are never pooled.",
        "same_condition_control_present": False,
        "source_output_mapping_present": False,
        "synthetic_schema_control_counted_as_result": False,
    }


def qualification() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "real_result_present": False,
        "candidate_present": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "source_present": False,
        "source_identity_recorded": False,
        "rights_cleared": False,
        "geometry_verified": False,
        "reference_execution_result": False,
        "rate_profile_result": False,
        "duration_result": False,
        "pitch_result": False,
        "transient_result": False,
        "buffering_result": False,
        "preservation_result": False,
        "listening_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "peer_result_inherited": False,
        "reason": "No exact licensed TD-PSOLA source/runtime, rights-cleared inputs, deterministic outputs, matched cohort, timing, listening or independent review is present. No result qualifies.",
    }


def scope() -> dict:
    return {
        "task_local_only": True,
        "write_scope": WRITE_SCOPE,
        "board_or_handoff_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "installed_v0_behavior_change": False,
        "candidate_code_downloaded": False,
        "candidate_code_vendored": False,
        "candidate_runtime_executed": False,
        "model_weights_downloaded": False,
        "model_weights_vendored": False,
        "real_audio": False,
        "synthetic_speech": False,
        "processed_output_present": False,
        "device_timing": False,
        "listening": False,
        "benchmark_claim": False,
        "release_claim": False,
        "network_access": False,
        "peer_evidence_inherited": False,
    }

def boundary_block() -> dict:
    row = board_row_projection()
    rows = linked_rows()
    return {
        "adapter_json_added": False,
        "audio_added": False,
        "board_file_pinned": False,
        "board_or_handoff_changed": False,
        "candidate_code_vendored": False,
        "corpus_added": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "excluded_mutable_fields": list(MUTABLE_BOARD_FIELDS),
        "installed_v0_behavior_change": False,
        "linked_row": row,
        "linked_row_identity_only": True,
        "linked_row_sha256": board_row_digest(row),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "mutable_board_fields_gate": False,
        "native_engine_built": False,
        "processed_output_added": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "runtime_imported": False,
        "shared_build_or_ci_change": False,
        "weights_vendored": False,
    }


def required_results() -> list[str]:
    return [
        "Exact upstream URL, immutable revision, source snapshot, license text and notice for the TD-PSOLA implementation/runtime.",
        "Locked offline runtime with interpreter, package versions, wheel hashes, platform, device, dtype and deterministic settings.",
        "Exact audio task geometry and causal/streaming contract, including sample rate, channels, frame/hop, lookahead, latency, reset and drain behavior.",
        "Rights-cleared, digest-pinned speech/music/silence inputs with consent, evaluation, derived-output and redistribution decisions.",
        "Deterministic reproduced outputs with hashes, finite/length behavior, exact repeats and peak/RSS values.",
        "Rate-profile measurements: source/output mapping, duration, pitch, transient audibility, buffering, 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial and speech preservation.",
        "Separate mode/platform timing, resource and pacing measurements, plus authorized listening or labeled screen.",
        "Separate versioned OFF-by-default provider intake with clean-install proof and independent exact-head review.",
    ]


def reopening_conditions() -> list[str]:
    return [
        "Publish and pin an exact TD-PSOLA source/runtime snapshot with reviewed license and notice records.",
        "Pin an offline runtime and exact audio geometry/casual contract with deterministic settings and clean-room install proof.",
        "Provide rights-cleared digest-pinned inputs and reviewed code/data/output terms.",
        "Reproduce deterministic outputs and complete the Rate profile on a matched rights-cleared cohort.",
        "Measure mode/platform timing, resources, pacing and complete authorized listening or a labeled screen.",
        "Open a separate OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear.",
    ]


def build_contract() -> dict:
    row = board_row_projection()
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "scope": scope(),
        "boundary": boundary_block(),
        "linked_row": row,
        "source_pins": dict(sorted(SOURCE_PINS.items())),
        "boundary_pins": dict(sorted(BOUNDARY_PINS.items())),
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "public_v0_geometry": public_v0_geometry(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "rate_profile": rate_profile(),
        "matched_evidence": matched_evidence(),
        "asset_declaration_schema": declaration_schema(),
        "accepted_declaration": accepted_declaration(),
        "admission": declaration_rejections(),
        "strict_json": strict_json_rejections(),
        "absence_evidence": absence_summary(),
        "evidence_presence": evidence_presence(),
        "historical_evidence": list(HISTORICAL_EVIDENCE),
        "peer_separation": list(PEER_SEPARATION),
        "required_results": required_results(),
        "reopening_conditions": reopening_conditions(),
        "non_claims": list(NON_CLAIMS),
        "qualification": qualification(),
    }
    assert_no_float(contract)
    return contract


def build_report() -> dict:
    contract = build_contract()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "contract_sha256": object_digest(contract),
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "source_reported_identity": contract["source_reported_identity"],
        "task_geometry": contract["task_geometry"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": contract["rate_profile"],
        "matched_evidence": contract["matched_evidence"],
        "asset_declaration_schema": contract["asset_declaration_schema"],
        "admission": {
            "accepted_control_digest": object_digest(accepted_declaration()),
            "accepted_control_qualifies": False,
            "accepted_control_status": "accepted_unpopulated",
            "manifest_cases": contract["admission"]["rejection_cases"],
            "all_rejected": contract["admission"]["all_rejected"],
            "rejections": contract["admission"]["rejections"],
            "strict_json_cases": contract["strict_json"]["rejection_cases"],
            "strict_json_all_rejected": contract["strict_json"]["all_rejected"],
            "strict_json_rejections": contract["strict_json"]["rejections"],
            "assets_never_loaded": True,
            "presence_claims_rejected": True,
        },
        "absence_evidence": contract["absence_evidence"],
        "evidence_presence": contract["evidence_presence"],
        "historical_evidence": contract["historical_evidence"],
        "peer_separation": contract["peer_separation"],
        "required_results": contract["required_results"],
        "reopening_conditions": contract["reopening_conditions"],
        "non_claims": contract["non_claims"],
        "qualification": contract["qualification"],
        "reproduction": {
            "byte_identical": True,
            "canonical_json": True,
            "interpreter": REQUIRED_INTERPRETER,
            "repeat_count": 3,
            "report_sha256_sidecar": "report.json.sha256",
            "sorted_keys": True,
            "trailing_newline": False,
        },
        "generated_by": TASK_PREFIX + "run.py",
    }
    assert_no_float(report)
    return report


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


def check_interpreter() -> None:
    observed = platform.python_version()
    if observed != REQUIRED_INTERPRETER:
        raise RuntimeError(
            f"interpreter_mismatch: required={REQUIRED_INTERPRETER} observed={observed}")


def local_pin_rows() -> list[tuple[str, str]]:
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
    return rows
