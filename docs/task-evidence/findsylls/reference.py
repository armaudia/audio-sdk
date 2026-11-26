# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence model for the ``findsylls`` blocker.

The exact ``findsylls`` Python source tree, its immutable revision, LICENSE
text, dependency lock, entrypoint and measured outputs are **absent** from this
workspace and from the SDK worktree.  Nothing is downloaded, vendored,
imported, executed or fabricated as the candidate.  This module therefore only
models:

* the caller-supplied source-artifact metadata boundary (identity and geometry
  validation only, never import or execution);
* the Rate acceptance profile over an explicitly synthetic, frozen Q15 frame
  energy fixture and an exact integer syllable-nuclei proxy;
* fail-closed rejection of missing, adverse, invalid and nonfinite input.

The surrogate is **not** findsylls, does not read audio, does not run a
renderer, does not measure a device clock and can never qualify the candidate.
Every value in the generated report is an integer, string, boolean or null; no
floating-point value enters canonical JSON.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-FINDSYLLS"
TITLE = "findsylls"
SLUG = "findsylls"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "7a8d801e48ccf42da20c48dae3b0bbe6e1766e24"
BRANCH = f"swarm/{TASK}"
WORKTREE = f"/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/{TASK}"
REVIEWER = f"reviewer-{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"

SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160
FRAME_SAMPLES = 160
WINDOW_SAMPLES = 64_000
TAIL_PARTIAL_SAMPLES = 64_037
FIXTURE_SLOTS = WINDOW_SAMPLES // FRAME_SAMPLES
CLOCK_ID = "fixture-monotonic-not-device"
Q15_MAX = 32_767
NUCLEI_THRESHOLD = 1_400
NUCLEI_MIN_SEPARATION = 8
NUCLEI_PROMINENCE = 600
SEED_BASE = 2026_1126

CONDITIONS: Tuple[str, ...] = (
    "speech",
    "unfamiliar_speech",
    "music",
    "silence",
    "rebuffer",
    "drift",
    "tail_partial",
)
SPEECH_LIKE: Dict[str, bool] = {
    "speech": True,
    "unfamiliar_speech": True,
    "music": False,
    "silence": False,
    "rebuffer": True,
    "drift": True,
    "tail_partial": True,
}
CONDITION_NOTES: Dict[str, str] = {
    "speech": "frozen synthetic syllabic Q15 envelope; speech-like control",
    "unfamiliar_speech": "different deterministic seed and faster syllable period; still synthetic",
    "music": "steady periodic non-speech energy control; never scored as speech",
    "silence": "all-zero frame energy control",
    "rebuffer": "speech-like envelope with a deterministic zeroed gap; queue accounting only",
    "drift": "speech-like envelope with a deterministic level shift; not a clock drift",
    "tail_partial": "speech-like envelope with a 37-sample final partial slot",
}

RATE_CASES: Tuple[Tuple[str, int, int], ...] = (
    ("1/1", 1, 1),
    ("4/5", 4, 5),
    ("5/4", 5, 4),
)
RATE_LABELS: Tuple[str, ...] = tuple(label for label, _num, _den in RATE_CASES)

# Candidate identity.  The research note names the URL and MIT but no commit,
# byte digest, licence text, lock file, entrypoint or output.
CANDIDATE_NAME = "findsylls"
CANDIDATE_URL = "https://github.com/hjvm/findsylls"
CANDIDATE_REPORTED_LICENSE = "MIT (source-reported only)"
CANDIDATE_REPORTED_ROLE = "offline syllable segmentation/embedding toolkit for evaluation ground truth"
CANDIDATE_CHECKOUT = "data/checkouts/findsylls"
CANDIDATE_MODEL_DIR = "data/models/findsylls"
CANDIDATE_ENV_DIR = "data/envs/findsylls"
CANDIDATE_MANIFEST = "data/manifests/findsylls.json"

ARTIFACT_CONTRACT_ID = f"audio-sdk/{SLUG}/caller-supplied-source/0.1"
ARTIFACT_REQUIRED_FIELDS: Tuple[str, ...] = (
    "artifact_format",
    "channels",
    "entrypoint",
    "frame_samples",
    "license_id",
    "license_sha256",
    "operating_mode",
    "python_requires",
    "repository",
    "requirements_lock_sha256",
    "sample_rate_hz",
    "source_commit",
    "source_sha256",
)
ARTIFACT_FORMAT = "python_source_tree"
ARTIFACT_LICENSE = "MIT"
ARTIFACT_MODE = "offline_whole_utterance"

SOURCE_PINS: Dict[str, str] = {
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "audio-benchmark-platform/audio-sdk/RELEASING.md":
        "67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "docs/task-evidence/sylnet/README.md":
        "cbc7794abb6550783a03c6a70bc013d69e157bdd2a222d1ea1b905758726220c",
    "docs/task-evidence/sylnet/report.json":
        "b81b1cd8691528f4cd492deaced8a589309048cdca54ab256c7cb0926bd32331",
    "docs/task-evidence/psola-praat/report.json":
        "c8126e10ec682b6960bc379a2d5a5db9222abedcd37b6fe62d176c47e07de614",
    "docs/task-evidence/granular-tsm/report.json":
        "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138",
    "docs/task-evidence/ola-sola/report.json":
        "90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93",
    "docs/task-evidence/soundtouch/report.json":
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947",
    "docs/task-evidence/usc-mrate/report.json":
        "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246",
}

LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)

STABLE_TASK_IDENTITY: Dict[str, Any] = {
    "id": TASK,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "feasibility",
    "component": SLUG,
    "dispatch_priority": 3,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "write_scope": [
        "SDK provider, tool or evidence directory for findsylls and its own fixtures"
    ],
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry and "
        "matched evidence. Then implement or wrap a minimal reference using the "
        "relevant public adapter boundary and ship it as optional initially. "
        "Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the rate acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted investigation "
        "handoff; it does not close the conditional implementation."
    ),
    "verification_profile": PROFILE,
    "profile_source": f"plan/INVENTORY.json#components[id={SLUG}]",
    "board_selector": f"tasks[id={TASK}]",
    "board_full_file_hashed": False,
    "mutable_fields_excluded": [
        "status",
        "owner",
        "claim",
        "review",
        "handoff",
        "blocked_reason",
        "initialized_on",
        "history",
    ],
}

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "v0_frame_samples": V0_FRAME_SAMPLES,
    "analysis_frame_samples": FRAME_SAMPLES,
    "window_samples": WINDOW_SAMPLES,
    "tail_partial_samples": TAIL_PARTIAL_SAMPLES,
    "clock": CLOCK_ID,
    "surrogate_mode": "offline_frame_energy_integer_proxy_not_candidate",
}

BOUNDARY: Dict[str, bool] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
    "adapter_json_added": False,
    "readiness_json_added": False,
    "source_tree_vendored": False,
    "source_tree_downloaded": False,
    "source_tree_imported": False,
    "source_tree_executed": False,
    "dependency_installed": False,
    "sdk_data_dir_added": False,
}

CLAIMS: Dict[str, bool] = {
    "real_findsylls_runtime": False,
    "candidate_source_read": False,
    "candidate_source_imported": False,
    "candidate_source_executed": False,
    "candidate_source_vendored": False,
    "candidate_source_downloaded": False,
    "real_audio_read": False,
    "real_media_read": False,
    "real_corpus_read": False,
    "syllable_annotation_produced": False,
    "rate_output_rendered": False,
    "duration_measured": False,
    "pitch_measured": False,
    "transient_audibility_measured": False,
    "playback_buffering_measured": False,
    "device_timing_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "parity_claim": False,
    "release_claim": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The exact findsylls implementation is absent and unpinned. No checkout exists at "
    "data/checkouts/findsylls, no source tree, entrypoint, module inventory or immutable "
    "revision is staged, and no byte count or SHA-256 identifies the implementation. The "
    "only record is the pinned research note's URL https://github.com/hjvm/findsylls and "
    "'MIT'; the note also states that no local build or benchmark of findsylls was made.",
    "No licence text, dependency lock, platform statement or installer is staged. MIT is "
    "source-reported only; no LICENSE copy, attribution notice, citation, requirements "
    "lock, Python version constraint, optional dependency map, feature/model contract or "
    "training-data/corpus statement exists. No legal, redistribution, product-use or "
    "generated-output review exists; private possession would not clear those scopes.",
    "No exact reference output, API/CLI contract or task geometry exists. The candidate is "
    "recorded only as an offline whole-utterance Python toolkit for syllable "
    "segmentation/embedding; no syllable definition, frame/hop, boundary convention, "
    "language scope, confidence field or output schema is documented, and no mapping onto "
    "the installed v0 16 kHz mono float32 160-sample contract exists. No candidate output "
    "was produced.",
    "No rights-cleared speech corpus or independent syllable annotation, no permitted "
    "listening, no renderer, no rate output, no measured duration/pitch/transient "
    "audibility/playback buffering and no device clock or target-runtime timing exists. "
    "The synthetic frame-energy surrogate is not findsylls, substitutes for no gate and "
    "cannot qualify the candidate. All eight release gates remain blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen source identity only when the exact findsylls source tree is supplied as a "
    "caller-owned external artifact with an immutable commit, per-file or tree SHA-256, "
    "entrypoint, module inventory and dependency lock, and the SDK validates those bytes "
    "without import, execution or download.",
    "Reopen runtime admission only when a hash-pinned, offline-installable Python "
    "environment with a recorded dependency lock imports and executes the exact source "
    "under a recorded interpreter, and absent assets fail closed.",
    "Reopen rights only after the MIT LICENSE text, attribution/notice obligations, "
    "allowed evaluation/product/redistribution scopes, generated-output terms and any "
    "training-data or corpus statements are reviewed in writing by the rights owner.",
    "Reopen exact reference parity only with approved candidate outputs for frozen inputs "
    "from the exact caller-supplied source under the exact pinned runtime, reproducible "
    "across three cold starts.",
    "Reopen ground-truth quality only with a rights-cleared speech cohort carrying "
    "independent, audited syllable annotations, exact source timestamps, declared language "
    "and speaking-style scope, and measured false-positive/false-negative behavior.",
    "Reopen the Rate profile only with measured 1x, rate-change, unfamiliar-speech, music, "
    "silence, rebuffer, drift and final-partial-window results, including duration, pitch, "
    "transient audibility, playback buffering and speech preservation.",
    "Reopen timing only with target-device clock, callback deadline, availability, compute, "
    "memory and pacing measurements for the exact runtime and workload.",
    "Reopen provider/default only after the prior gates clear and an opt-in analysis or "
    "tool intake with OFF default, descriptor review and an explicit owner decision is "
    "approved.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "exact findsylls source tree with immutable commit, tree/file SHA-256 and entrypoint",
    "MIT LICENSE text plus attribution, redistribution, product-use and generated-output decisions",
    "hash-pinned offline Python runtime and dependency lock with a recorded interpreter",
    "documented API/CLI, syllable definition, frame/hop, boundary convention, language scope and output schema",
    "approved candidate outputs for frozen inputs, reproducible across three cold starts",
    "rights-cleared speech cohort with independent audited syllable annotations and source timestamps",
    "measured 1x/rate-change/unfamiliar/music/silence/rebuffer/drift/final-partial rate evidence",
    "target-device timing, memory, pacing and permitted listening evidence",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_upstream_source_and_license",
        "status": "blocked",
        "evidence": (
            "No findsylls checkout, commit, tree/file digest, LICENSE text, entrypoint, "
            "module inventory or dependency lock is staged; only a URL and an 'MIT' label "
            "are recorded."
        ),
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "name": "isolated_runtime_admission",
        "status": "blocked",
        "evidence": (
            "No pinned Python interpreter, dependency lock, offline environment or "
            "candidate import/execute path exists; no absent-asset fail-closed run was made."
        ),
        "reopen": REOPEN_CONDITIONS[1],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": (
            "MIT is source-reported only; no LICENSE copy, notice, training-data statement "
            "or written evaluation/redistribution/product-use/generated-output decision exists."
        ),
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": (
            "No candidate output, API contract or frozen-input parity vector exists; the "
            "surrogate is not findsylls and cannot produce parity."
        ),
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "syllable_ground_truth_quality",
        "status": "blocked",
        "evidence": (
            "No rights-cleared speech cohort, independent syllable annotation, language "
            "scope or false-positive/false-negative measurement exists."
        ),
        "reopen": REOPEN_CONDITIONS[4],
    },
    {
        "name": "rate_profile_qualification",
        "status": "blocked",
        "evidence": (
            "Duration, pitch, transient audibility, playback buffering and speech "
            "preservation are unmeasured; only exact synthetic target-duration arithmetic "
            "and fixture queue accounting exist."
        ),
        "reopen": REOPEN_CONDITIONS[5],
    },
    {
        "name": "target_runtime_timing_and_memory",
        "status": "blocked",
        "evidence": (
            "No device clock, callback deadline, availability, compute, memory or pacing "
            "measurement exists for any runtime."
        ),
        "reopen": REOPEN_CONDITIONS[6],
    },
    {
        "name": "provider_intake_and_default_selection",
        "status": "blocked",
        "evidence": "No opt-in provider or analysis intake, descriptor or default decision exists.",
        "reopen": REOPEN_CONDITIONS[7],
    },
)

RATE_REQUIREMENTS: Dict[str, Dict[str, str]] = {
    "source_output_mapping": {
        "status": "synthetic_only",
        "evidence": "Exact integer source-sample to output-sample mapping with recorded remainder; no rendered output.",
    },
    "duration": {
        "status": "synthetic_only",
        "evidence": "Target output duration is exact arithmetic only; no measured duration.",
    },
    "pitch": {
        "status": "blocked",
        "evidence": "No renderer and no pitch analysis; pitch is explicitly unmeasured.",
    },
    "transient_audibility": {
        "status": "blocked",
        "evidence": "No renderer, listening or transient analysis exists.",
    },
    "playback_buffering": {
        "status": "fixture_accounting_only",
        "evidence": "Source/output slot counts and final partial slots are fixture accounting; no device queue or deadline.",
    },
    "one_x_and_rate_changes": {
        "status": "synthetic_only",
        "evidence": "1/1, 4/5 and 5/4 target-duration cases over frozen synthetic frame energies.",
    },
    "unfamiliar_speech": {
        "status": "synthetic_only",
        "evidence": "A differently seeded, faster synthetic envelope; not a real unfamiliar speaker.",
    },
    "music": {
        "status": "synthetic_only",
        "evidence": "A periodic non-speech energy control; never scored as speech.",
    },
    "silence": {
        "status": "synthetic_only",
        "evidence": "All-zero frame-energy control with undefined rate.",
    },
    "rebuffer": {
        "status": "fixture_accounting_only",
        "evidence": "One deterministic zeroed gap and queue counts; no device rebuffer or clock.",
    },
    "drift": {
        "status": "synthetic_only",
        "evidence": "A deterministic level shift across frames; it is not a clock drift.",
    },
    "final_partial_window": {
        "status": "synthetic_only",
        "evidence": "A 37-sample final partial source slot and exact output partial coordinates.",
    },
    "pause_filler_source_timestamps": {
        "status": "not_applicable",
        "evidence": "No pause or filler decision is made; source intervals remain sample-anchored.",
    },
    "speech_preservation": {
        "status": "blocked",
        "evidence": "No real speech, renderer, intelligibility measure or listening exists.",
    },
    "listening": {
        "status": "not_run",
        "evidence": "No listener, protocol or permitted audio exists.",
    },
    "device_timing": {
        "status": "blocked",
        "evidence": "All coordinates are fixture sample coordinates, not a device clock.",
    },
    "benchmark": {
        "status": "blocked",
        "evidence": "No benchmark, workload, corpus or target runtime was run.",
    },
}

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, pooled or used as a threshold.",
    "candidate_row": {
        "source": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 885,
        "record_name": "findsylls",
        "finding": "Offline only; use for evaluation",
        "table_role": "Offline syllable ground truth",
        "table_license": "MIT",
        "table_description": "Python toolkit for syllable segmentation/embedding",
    },
    "url_reference": {
        "source": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 1043,
        "url": CANDIDATE_URL,
        "license": "MIT",
    },
    "no_local_build": (
        "The pinned note states that no local build or benchmark of findsylls was made; "
        "this package adds none."
    ),
    "speech_rate_note": (
        "The pinned note lists findsylls as a reference for syllable/rate estimation and "
        "warns against linking Praat (GPL) only for its syllable script."
    ),
    "sibling_results_are_not_transferable": (
        "The merged sylnet, psola-praat, granular-tsm, ola-sola, soundtouch and usc-mrate "
        "packages are separate references with their own assets, fixtures and results. "
        "Nothing is imported, pooled, scored or reused here."
    ),
    "disclaimer": (
        "These values are quoted from pinned research files. They are not reproduced, not "
        "device timing, not a listening result and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "findsylls source, LICENSE, dependency lock, checkpoint/feature artefact and runtime are absent from this package; nothing was downloaded, imported, executed or vendored.",
    "The URL, MIT label, offline-only role and the absence of a local build/benchmark are quoted from the pinned research note.",
    "All fixture energies, nuclei-proxy counts and target durations are generated by stdlib integer code in reference.py; no audio, corpus, media or candidate output is read.",
    "The board is referenced by stable linked-row fields only; the mutable full plan/swarm/TASKS.json is never hashed or pinned.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No findsylls source tree, LICENSE, dependency environment, model/feature artefact, corpus or media was downloaded, copied, imported, executed or bundled.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No duration, pitch, transient, playback-buffer, device-timing, listening, benchmark, quality, parity or release result is claimed for the candidate.",
    "The synthetic frame-energy nuclei proxy is not findsylls and no missing result ever qualifies the candidate.",
)


# ---------------------------------------------------------------------------
# Canonical JSON, digests and stable board identity
# ---------------------------------------------------------------------------


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError("nonfinite float in canonical JSON")
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def stable_identity_digest(identity: Dict[str, Any] | None = None) -> str:
    payload = dict(identity or STABLE_TASK_IDENTITY)
    payload.pop("stable_sha256", None)
    payload.pop("board_full_file_hashed", None)
    payload.pop("mutable_fields_excluded", None)
    return sha256(canonical_bytes(payload))


def task_identity() -> Dict[str, Any]:
    identity = dict(STABLE_TASK_IDENTITY)
    identity["stable_sha256"] = stable_identity_digest()
    identity["board_full_file_hashed"] = False
    identity["mutable_fields_excluded"] = list(STABLE_TASK_IDENTITY["mutable_fields_excluded"])
    return identity


# ---------------------------------------------------------------------------
# Frozen synthetic frame-energy fixture (Q15 integers; no audio)
# ---------------------------------------------------------------------------


def _seed(name: str) -> int:
    return (SEED_BASE + int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big")) & 0xFFFFFFFF


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF

    def nxt() -> int:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state

    return nxt


def _triangle(i: int, period: int) -> int:
    phase = i % period
    if phase < period // 3:
        return 3 * phase * 1000 // period
    return (period - phase) * 1000 // period


def _slot_energy(condition: str, index: int, rng) -> int:
    jitter = int(rng() % 241) - 120
    if condition == "silence":
        return 0
    if condition == "music":
        value = 600 + 2200 * _triangle(index, 10) // 1000
        return max(0, min(Q15_MAX, value + jitter // 2))
    if condition == "unfamiliar_speech":
        value = 260 + 2400 * _triangle(index, 16) // 1000
        return max(0, min(Q15_MAX, value + jitter))
    if condition == "rebuffer":
        if 160 <= index < 180:
            return 0
        value = 300 + 2600 * _triangle(index, 20) // 1000
        return max(0, min(Q15_MAX, value + jitter))
    if condition == "drift":
        value = 300 + 2600 * _triangle(index, 20) // 1000 + index * 600 // FIXTURE_SLOTS
        return max(0, min(Q15_MAX, value + jitter))
    value = 300 + 2600 * _triangle(index, 20) // 1000
    return max(0, min(Q15_MAX, value + jitter))


def source_samples(condition: str) -> int:
    if condition not in CONDITIONS:
        raise ValueError("unknown_condition")
    return TAIL_PARTIAL_SAMPLES if condition == "tail_partial" else WINDOW_SAMPLES


def slot_count(condition: str) -> int:
    samples = source_samples(condition)
    return (samples + FRAME_SAMPLES - 1) // FRAME_SAMPLES


def fixture(condition: str) -> List[int]:
    if condition not in CONDITIONS:
        raise ValueError("unknown_condition")
    slots = slot_count(condition)
    rng = _lcg(_seed(condition))
    return [_slot_energy(condition, index, rng) for index in range(slots)]


def detect_nuclei(
    energies: Sequence[int],
    threshold: int = NUCLEI_THRESHOLD,
    min_separation: int = NUCLEI_MIN_SEPARATION,
    prominence: int = NUCLEI_PROMINENCE,
) -> List[int]:
    """Deterministic syllable-nuclei proxy peak picker over Q15 frame energies."""
    if not isinstance(energies, (list, tuple)):
        raise ValueError("slot_type_invalid")
    values: List[int] = []
    for value in energies:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("slot_type_invalid")
        if value < 0 or value > Q15_MAX:
            raise ValueError("slot_out_of_range")
        values.append(value)
    peaks: List[int] = []
    last = -10**9
    total = len(values)
    for index, value in enumerate(values):
        if value < threshold:
            continue
        left = values[index - 1] if index > 0 else -1
        right = values[index + 1] if index + 1 < total else -1
        if value < left or value <= right:
            continue
        start = max(0, index - min_separation)
        end = min(total, index + min_separation + 1)
        if value - min(values[start:end]) < prominence:
            continue
        if index - last < min_separation:
            continue
        peaks.append(index)
        last = index
    return peaks


def fixture_digest(condition: str) -> str:
    return sha256(canonical_bytes(fixture(condition)))


# ---------------------------------------------------------------------------
# Exact rate mapping and synthetic Rate-profile cases
# ---------------------------------------------------------------------------


def map_duration(source_count: int, numerator: int, denominator: int) -> Tuple[int, int]:
    if isinstance(source_count, bool) or not isinstance(source_count, int) or source_count <= 0:
        raise ValueError("source_samples_invalid")
    if isinstance(numerator, bool) or not isinstance(numerator, int) or numerator <= 0:
        raise ValueError("rate_numerator_invalid")
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator <= 0:
        raise ValueError("rate_denominator_invalid")
    return divmod(source_count * denominator, numerator)


def _rate_case(condition: str, label: str, numerator: int, denominator: int) -> Dict[str, Any]:
    samples = source_samples(condition)
    slots = slot_count(condition)
    output, remainder = map_duration(samples, numerator, denominator)
    energies = fixture(condition)
    peaks = detect_nuclei(energies)
    count = len(peaks)
    per_second_milli: int | None = None
    if condition != "silence":
        per_second_milli = count * 1000 * SAMPLE_RATE_HZ // samples
    partial_source = samples % FRAME_SAMPLES
    partial_output = output % FRAME_SAMPLES
    rebuffer_slots = 20 if condition == "rebuffer" else 0
    return {
        "rate": {"label": label, "numerator": numerator, "denominator": denominator},
        "source_samples": samples,
        "source_slots": slots,
        "source_interval": [0, samples],
        "final_partial_source_samples": partial_source,
        "final_partial_source_interval": ([samples - partial_source, samples] if partial_source else []),
        "target_output_samples": output,
        "computed_output_samples": output,
        "mapping_remainder": remainder,
        "output_full_slots": output // FRAME_SAMPLES,
        "output_final_partial_samples": partial_output,
        "mapped_output_interval": [0, output],
        "nuclei_proxy_count": count,
        "nuclei_proxy_per_second_milli": per_second_milli,
        "speech_like": SPEECH_LIKE[condition],
        "rebuffer_events": 1 if condition == "rebuffer" else 0,
        "rebuffer_gap_slots": rebuffer_slots,
        "fixture_available_through_sample": samples,
        "pause_or_filler_decisions": 0,
        "renderer_executed": False,
        "duration_measured": False,
        "pitch_measured": False,
        "transient_audibility_measured": False,
        "playback_buffering_measured": False,
        "device_timing_measured": False,
        "listening": False,
    }


def rate_results() -> Dict[str, Any]:
    conditions: Dict[str, Any] = {}
    cases = 0
    total_source = 0
    for condition in CONDITIONS:
        energies = fixture(condition)
        peaks = detect_nuclei(energies)
        rates: Dict[str, Any] = {}
        for label, numerator, denominator in RATE_CASES:
            rates[label] = _rate_case(condition, label, numerator, denominator)
            cases += 1
        conditions[condition] = {
            "note": CONDITION_NOTES[condition],
            "speech_like": SPEECH_LIKE[condition],
            "source_samples": source_samples(condition),
            "source_slots": len(energies),
            "energy_sha256": fixture_digest(condition),
            "nuclei_proxy_indices": peaks,
            "nuclei_proxy_count": len(peaks),
            "rates": rates,
        }
        total_source += source_samples(condition)
    return {
        "conditions": conditions,
        "condition_count": len(CONDITIONS),
        "rate_case_count": cases,
        "total_source_samples": total_source,
        "fixture_slot_count": sum(slot_count(condition) for condition in CONDITIONS),
    }


def controls(results: Dict[str, Any]) -> Dict[str, Any]:
    conditions = results["conditions"]
    identity_exact = all(
        condition["rates"]["1/1"]["computed_output_samples"] == condition["source_samples"]
        for condition in conditions.values()
    )
    duration_exact = all(
        case["computed_output_samples"] == case["target_output_samples"]
        for condition in conditions.values()
        for case in condition["rates"].values()
    )
    silence_zero = all(
        case["nuclei_proxy_count"] == 0
        for case in conditions["silence"]["rates"].values()
    )
    constant = 20
    speech_errors: Dict[str, int | None] = {}
    for name, condition in conditions.items():
        if not condition["speech_like"]:
            speech_errors[name] = None
            continue
        count = condition["nuclei_proxy_count"]
        speech_errors[name] = abs(int(count) - constant) if count is not None else None
    remainders = {
        f"{name}:{label}": case["mapping_remainder"]
        for name, condition in conditions.items()
        for label, case in condition["rates"].items()
        if case["mapping_remainder"] != 0
    }
    return {
        "identity_echo_exact": identity_exact,
        "target_duration_exact": duration_exact,
        "silence_zero_nuclei": silence_zero,
        "constant_count_control": {
            "constant": constant,
            "scope": "speech_like_conditions",
            "absolute_errors": speech_errors,
            "note": "A frozen synthetic constant-count control, not a reproduction of any research baseline.",
        },
        "nonzero_mapping_remainders": remainders,
        "note": "Controls describe the synthetic surrogate only and qualify nothing.",
    }


# ---------------------------------------------------------------------------
# Configuration and slot validation (fail closed)
# ---------------------------------------------------------------------------


CONFIG_KEYS: Tuple[str, ...] = (
    "channels",
    "clock",
    "condition",
    "epoch",
    "first_input_sample",
    "frame_samples",
    "nuclei_min_separation",
    "nuclei_prominence",
    "nuclei_threshold",
    "opt_in_surrogate",
    "rate_label",
    "sample_format",
    "sample_rate_hz",
    "source_samples",
    "window_samples",
)


def default_config() -> Dict[str, Any]:
    return {
        "channels": CHANNELS,
        "clock": CLOCK_ID,
        "condition": "speech",
        "epoch": 1,
        "first_input_sample": 0,
        "frame_samples": FRAME_SAMPLES,
        "nuclei_min_separation": NUCLEI_MIN_SEPARATION,
        "nuclei_prominence": NUCLEI_PROMINENCE,
        "nuclei_threshold": NUCLEI_THRESHOLD,
        "opt_in_surrogate": True,
        "rate_label": "1/1",
        "sample_format": SAMPLE_FORMAT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_samples": WINDOW_SAMPLES,
        "window_samples": WINDOW_SAMPLES,
    }


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_config(config: Any) -> List[str]:
    if config is None:
        return ["config_missing"]
    if not isinstance(config, dict):
        return ["config_type_invalid"]
    reasons: List[str] = []
    if set(config) != set(CONFIG_KEYS):
        reasons.append("config_field_set_invalid")
    if config.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_unsupported")
    if config.get("channels") != CHANNELS:
        reasons.append("channels_unsupported")
    if config.get("sample_format") != SAMPLE_FORMAT:
        reasons.append("sample_format_unsupported")
    if config.get("frame_samples") != FRAME_SAMPLES:
        reasons.append("frame_samples_unsupported")
    if config.get("window_samples") != WINDOW_SAMPLES:
        reasons.append("window_samples_unsupported")
    if config.get("clock") != CLOCK_ID:
        reasons.append("clock_domain_unsupported")
    condition = config.get("condition")
    if condition not in CONDITIONS:
        reasons.append("condition_unknown")
    source = config.get("source_samples")
    if not _is_int(source) or source <= 0 or source > WINDOW_SAMPLES:
        reasons.append("source_samples_invalid")
    if condition == "tail_partial" and source != TAIL_PARTIAL_SAMPLES:
        reasons.append("tail_partial_source_mismatch")
    if condition in CONDITIONS and condition != "tail_partial" and source != WINDOW_SAMPLES:
        reasons.append("source_samples_mismatch")
    if config.get("rate_label") not in RATE_LABELS:
        reasons.append("rate_unsupported")
    epoch = config.get("epoch")
    if not _is_int(epoch) or epoch <= 0:
        reasons.append("epoch_invalid")
    first = config.get("first_input_sample")
    if not _is_int(first) or first < 0:
        reasons.append("first_input_sample_invalid")
    threshold = config.get("nuclei_threshold")
    if not _is_int(threshold) or threshold < 0 or threshold > Q15_MAX:
        reasons.append("nuclei_threshold_invalid")
    separation = config.get("nuclei_min_separation")
    if not _is_int(separation) or separation < 1 or separation > 400:
        reasons.append("nuclei_min_separation_invalid")
    prominence = config.get("nuclei_prominence")
    if not _is_int(prominence) or prominence < 0 or prominence > Q15_MAX:
        reasons.append("nuclei_prominence_invalid")
    if config.get("opt_in_surrogate") is not True:
        reasons.append("surrogate_opt_in_required")
    return reasons


def admit_config(config: Any) -> Dict[str, Any]:
    reasons = validate_config(config)
    if reasons:
        return {
            "status": "rejected",
            "reason_codes": reasons,
            "processing_attempted": False,
            "qualification_effect": "none",
        }
    return {
        "status": "admitted_synthetic_control",
        "reason_codes": [],
        "processing_attempted": False,
        "qualification_effect": "none",
        "note": "Explicitly synthetic fixture branch; not findsylls and not a qualification result.",
    }


def _mutate(**changes: Any) -> Dict[str, Any]:
    config = default_config()
    config.update(changes)
    return config


def config_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}
    cases["missing"] = admit_config(None)
    cases["not_object"] = admit_config([])
    missing = default_config()
    del missing["clock"]
    cases["missing_field"] = admit_config(missing)
    extra = default_config()
    extra["unexpected"] = 1
    cases["extra_field"] = admit_config(extra)
    cases["wrong_sample_rate"] = admit_config(_mutate(sample_rate_hz=8_000))
    cases["wrong_channels"] = admit_config(_mutate(channels=2))
    cases["wrong_sample_format"] = admit_config(_mutate(sample_format="i16"))
    cases["wrong_frame_samples"] = admit_config(_mutate(frame_samples=256))
    cases["wrong_window_samples"] = admit_config(_mutate(window_samples=32_000))
    cases["unknown_condition"] = admit_config(_mutate(condition="noise"))
    cases["unsupported_rate"] = admit_config(_mutate(rate_label="1/3"))
    cases["rate_numerator_zero"] = admit_config(_mutate(rate_label="0/1"))
    cases["rate_denominator_zero"] = admit_config(_mutate(rate_label="1/0"))
    cases["boolean_epoch"] = admit_config(_mutate(epoch=True))
    cases["negative_epoch"] = admit_config(_mutate(epoch=-1))
    cases["negative_first_input_sample"] = admit_config(_mutate(first_input_sample=-1))
    cases["nonfinite_threshold"] = admit_config(_mutate(nuclei_threshold=float("nan")))
    cases["string_threshold"] = admit_config(_mutate(nuclei_threshold="1400"))
    cases["oversized_source"] = admit_config(_mutate(source_samples=64_001))
    cases["zero_source"] = admit_config(_mutate(source_samples=0))
    cases["surrogate_not_opted_in"] = admit_config(_mutate(opt_in_surrogate=False))
    cases["valid_control"] = admit_config(default_config())
    return cases


SLOT_KEYS: Tuple[str, ...] = ("condition", "energies", "epoch", "first_input_sample")


def validate_slots(payload: Any) -> List[str]:
    if payload is None:
        return ["slots_missing"]
    if not isinstance(payload, dict):
        return ["slots_type_invalid"]
    if set(payload) != set(SLOT_KEYS):
        return ["slots_field_set_invalid"]
    condition = payload.get("condition")
    if condition not in CONDITIONS:
        return ["condition_unknown"]
    epoch = payload.get("epoch")
    if not _is_int(epoch) or epoch <= 0:
        return ["epoch_invalid"]
    first = payload.get("first_input_sample")
    if not _is_int(first) or first < 0:
        return ["first_input_sample_invalid"]
    energies = payload.get("energies")
    if not isinstance(energies, list):
        return ["slots_type_invalid"]
    if len(energies) != slot_count(condition):
        return ["slots_length_mismatch"]
    for value in energies:
        if isinstance(value, bool):
            return ["slot_type_invalid"]
        if not isinstance(value, int):
            return ["slot_type_invalid"]
        if value < 0 or value > Q15_MAX:
            return ["slot_out_of_range"]
    return []


def _slot_payload(energies: Any, condition: str = "speech", epoch: Any = 1) -> Dict[str, Any]:
    return {
        "condition": condition,
        "energies": energies,
        "epoch": epoch,
        "first_input_sample": 0,
    }


def slot_rejection_matrix() -> Dict[str, Any]:
    good = fixture("speech")
    cases: Dict[str, Any] = {}
    cases["missing"] = validate_slots(None)
    cases["not_object"] = validate_slots([])
    cases["empty"] = validate_slots(_slot_payload([]))
    cases["short"] = validate_slots(_slot_payload(good[:-1]))
    cases["long"] = validate_slots(_slot_payload(good + [0]))
    missing = _slot_payload(good)
    del missing["energies"]
    cases["missing_field"] = validate_slots(missing)
    cases["boolean_slot"] = validate_slots(_slot_payload([True] + good[1:]))
    cases["string_slot"] = validate_slots(_slot_payload(["1"] + good[1:]))
    cases["float_slot"] = validate_slots(_slot_payload([1.0] + good[1:]))
    cases["negative_slot"] = validate_slots(_slot_payload([-1] + good[1:]))
    cases["out_of_range_slot"] = validate_slots(_slot_payload([Q15_MAX + 1] + good[1:]))
    cases["nonfinite_slot"] = validate_slots(_slot_payload([float("nan")] + good[1:]))
    cases["stale_epoch"] = validate_slots(_slot_payload(good, epoch=0))
    cases["boolean_epoch"] = validate_slots(_slot_payload(good, epoch=True))
    cases["negative_epoch"] = validate_slots(_slot_payload(good, epoch=-1))
    cases["unknown_condition"] = validate_slots(_slot_payload(good, condition="noise"))
    cases["wrong_condition_length"] = validate_slots(_slot_payload(good, condition="tail_partial"))
    cases["valid_control"] = validate_slots(_slot_payload(good))
    rendered: Dict[str, Any] = {}
    for name, reasons in cases.items():
        rendered[name] = {
            "status": "accepted_synthetic_control" if not reasons else "rejected",
            "reason_codes": reasons,
            "processed_slots": 0,
            "state_unchanged": True,
        }
    return rendered


# ---------------------------------------------------------------------------
# Caller-supplied source-artifact metadata boundary (never imported)
# ---------------------------------------------------------------------------


def _hexlen(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and re.fullmatch(r"[0-9a-f]+", value) is not None


def validate_artifact_manifest(manifest: Any) -> List[str]:
    if manifest is None:
        return ["source_tree_absent"]
    if not isinstance(manifest, dict):
        return ["artifact_manifest_type_invalid"]
    reasons: List[str] = []
    if set(manifest) != set(ARTIFACT_REQUIRED_FIELDS):
        reasons.append("artifact_field_set_invalid")
    if manifest.get("artifact_format") != ARTIFACT_FORMAT:
        reasons.append("artifact_format_invalid")
    if manifest.get("license_id") != ARTIFACT_LICENSE:
        reasons.append("artifact_license_invalid")
    if manifest.get("operating_mode") != ARTIFACT_MODE:
        reasons.append("artifact_mode_invalid")
    if not _hexlen(manifest.get("source_commit"), 40):
        reasons.append("source_commit_invalid")
    if not _hexlen(manifest.get("source_sha256"), 64):
        reasons.append("source_sha256_invalid")
    if not _hexlen(manifest.get("license_sha256"), 64):
        reasons.append("license_sha256_invalid")
    if not _hexlen(manifest.get("requirements_lock_sha256"), 64):
        reasons.append("requirements_lock_sha256_invalid")
    repository = manifest.get("repository")
    if not isinstance(repository, str) or not repository or "://" in repository or ".." in repository:
        reasons.append("repository_invalid")
    for field in ("entrypoint", "python_requires"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value or ".." in value:
            reasons.append(field + "_invalid")
    if manifest.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_unsupported")
    if manifest.get("channels") != CHANNELS:
        reasons.append("channels_unsupported")
    if manifest.get("frame_samples") != FRAME_SAMPLES:
        reasons.append("frame_samples_unsupported")
    return reasons


def synthetic_artifact_manifest() -> Dict[str, Any]:
    return {
        "artifact_format": ARTIFACT_FORMAT,
        "channels": CHANNELS,
        "entrypoint": "findsylls/cli.py",
        "frame_samples": FRAME_SAMPLES,
        "license_id": ARTIFACT_LICENSE,
        "license_sha256": "0" * 64,
        "operating_mode": ARTIFACT_MODE,
        "python_requires": ">=3.10",
        "repository": "synthetic-control-not-findsylls",
        "requirements_lock_sha256": "0" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_commit": "0123456789abcdef0123456789abcdef01234567",
        "source_sha256": "0" * 64,
    }


def artifact_admission(manifest: Any = None) -> Dict[str, Any]:
    if manifest is None:
        reasons = [
            "source_tree_absent",
            "source_identity_unpinned",
            "license_text_absent",
            "reference_output_absent",
            "rights_review_absent",
        ]
    else:
        reasons = validate_artifact_manifest(manifest)
    if reasons:
        return {
            "status": "blocked",
            "reason_codes": reasons,
            "candidate_asset": False,
            "imported": False,
            "executed": False,
            "download_attempted": False,
            "qualification_effect": "none",
        }
    return {
        "status": "validated_metadata_only",
        "reason_codes": [],
        "candidate_asset": False,
        "imported": False,
        "executed": False,
        "download_attempted": False,
        "qualification_effect": "none",
        "note": "Explicitly synthetic metadata control; not findsylls, never imported or executed.",
    }


def artifact_cases() -> Dict[str, Any]:
    cases: Dict[str, Any] = {"absent": artifact_admission(None)}
    cases["synthetic_metadata_control"] = artifact_admission(synthetic_artifact_manifest())
    missing = synthetic_artifact_manifest()
    del missing["entrypoint"]
    cases["missing_field"] = artifact_admission(missing)
    cases["not_object"] = artifact_admission([])
    cases["wrong_format"] = artifact_admission({**synthetic_artifact_manifest(), "artifact_format": "binary"})
    cases["bad_commit"] = artifact_admission({**synthetic_artifact_manifest(), "source_commit": "abc"})
    cases["bad_hash"] = artifact_admission({**synthetic_artifact_manifest(), "source_sha256": "z" * 64})
    cases["wrong_license"] = artifact_admission({**synthetic_artifact_manifest(), "license_id": "GPL-3.0"})
    cases["wrong_sample_rate"] = artifact_admission({**synthetic_artifact_manifest(), "sample_rate_hz": 8_000})
    cases["wrong_channels"] = artifact_admission({**synthetic_artifact_manifest(), "channels": 2})
    cases["wrong_frame"] = artifact_admission({**synthetic_artifact_manifest(), "frame_samples": 256})
    cases["wrong_mode"] = artifact_admission({**synthetic_artifact_manifest(), "operating_mode": "streaming"})
    cases["extra_field"] = artifact_admission({**synthetic_artifact_manifest(), "extra": 1})
    return cases


def validate_use_scope(scope: Any) -> List[str]:
    if scope == "research_evaluation":
        return []
    if scope in ("commercial_product", "redistribution", "public_playback", "customer_deployment"):
        return ["license_scope_not_permitted"]
    return ["use_scope_unknown"]


def use_scope_cases() -> Dict[str, Any]:
    rendered: Dict[str, Any] = {}
    for scope in (
        "research_evaluation",
        "commercial_product",
        "redistribution",
        "public_playback",
        "customer_deployment",
        "unknown_scope",
    ):
        reasons = validate_use_scope(scope)
        rendered[scope] = {
            "status": "accepted_research_evaluation_control" if not reasons else "rejected",
            "reason_codes": reasons,
            "qualification_effect": "none",
        }
    return rendered


# ---------------------------------------------------------------------------
# Candidate, rights and reference status
# ---------------------------------------------------------------------------


def _candidate_probes() -> List[str]:
    probes = (
        CANDIDATE_CHECKOUT,
        CANDIDATE_MODEL_DIR,
        CANDIDATE_ENV_DIR,
        CANDIDATE_MANIFEST,
    )
    present: List[str] = []
    for raw in probes:
        path = SOURCE_ROOT / raw
        if path.exists() or path.is_symlink():
            present.append(raw)
    return present


def candidate_status() -> Dict[str, Any]:
    probes = _candidate_probes()
    return {
        "name": CANDIDATE_NAME,
        "reported_url": CANDIDATE_URL,
        "reported_license": CANDIDATE_REPORTED_LICENSE,
        "reported_role": CANDIDATE_REPORTED_ROLE,
        "reported_language": "Python",
        "reported_offline_whole_utterance": True,
        "reported_streaming": False,
        "reported_sample_rate_hz": None,
        "reported_frame_samples": None,
        "reported_dependency_lock": None,
        "geometry_documented": False,
        "source_present": False,
        "implementation_present": False,
        "pinned_revision": None,
        "source_sha256": None,
        "license_text_present": False,
        "requirements_lock_present": False,
        "entrypoint_present": False,
        "exact_numeric_output_present": False,
        "runtime_present": False,
        "checkout_path": CANDIDATE_CHECKOUT,
        "workspace_probe_paths": [
            CANDIDATE_CHECKOUT,
            CANDIDATE_MODEL_DIR,
            CANDIDATE_ENV_DIR,
            CANDIDATE_MANIFEST,
        ],
        "workspace_probes_present": probes,
        "workspace_probes_checked": list(
            (CANDIDATE_CHECKOUT, CANDIDATE_MODEL_DIR, CANDIDATE_ENV_DIR, CANDIDATE_MANIFEST)
        ),
        "reported_upstream_metrics": {
            "source": "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "values": None,
            "note": "The pinned note records no numeric findsylls quality or timing result and states that no local build or benchmark was made.",
        },
    }


def reference_status() -> Dict[str, Any]:
    return {
        "implementation_present": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "adapter_present": False,
        "license_text_present": False,
        "requirements_lock_present": False,
        "entrypoint_present": False,
        "exact_numeric_output_present": False,
        "pinned_revision": None,
        "source_sha256": None,
        "license_identity": CANDIDATE_REPORTED_LICENSE,
        "status": "blocked",
        "surrogate_is_candidate": False,
    }


def rights_status() -> Dict[str, Any]:
    return {
        "recorded_license": CANDIDATE_REPORTED_LICENSE,
        "license_text_staged": False,
        "attribution_required": True,
        "attribution_notice_staged": False,
        "commercial_use_permitted": False,
        "redistribution_permitted": False,
        "product_use_reviewed": False,
        "training_data_statement_staged": False,
        "corpus_terms_staged": False,
        "generated_output_terms_staged": False,
        "permitted_scope_here": "research_evaluation_only",
        "qualifies": False,
        "rejection_code": "license_scope_not_permitted",
        "status": "unverified",
        "review_status": "blocked",
        "review_date": None,
        "reviewer": None,
        "note": (
            "MIT is source-reported only; no LICENSE text, notice bundle, training-data "
            "statement or written scope decision is staged. Possession would not clear "
            "redistribution, product use or generated-output terms."
        ),
    }


def rate_profile_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "profile_source": "plan/swarm/VERIFICATION.md",
        "requirement_text": (
            "Measure source/output mapping, duration, pitch, transient audibility and "
            "playback buffering. Include 1x, rate changes, unfamiliar speech, music, "
            "silence, rebuffer, drift and the final partial window. Keep pause or filler "
            "decisions tied to source timestamps and measure speech preservation."
        ),
        "requirements": {key: dict(value) for key, value in RATE_REQUIREMENTS.items()},
        "rate_cases": [
            {"label": label, "numerator": numerator, "denominator": denominator}
            for label, numerator, denominator in RATE_CASES
        ],
        "conditions": list(CONDITIONS),
        "source_output_mapping": {
            "exact_integer": True,
            "rounding": "floor",
            "remainder_recorded": True,
            "formula": "output_samples = floor(source_samples * denominator / numerator)",
        },
        "measured": {
            "duration": False,
            "pitch": False,
            "transient_audibility": False,
            "playback_buffering": False,
            "device_clock": False,
            "listening": False,
            "speech_preservation": False,
        },
        "rate_case_count": results["rate_case_count"],
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Report and contract builders
# ---------------------------------------------------------------------------


def build_report() -> Dict[str, Any]:
    results = rate_results()
    config_cases = config_rejection_matrix()
    slot_cases = slot_rejection_matrix()
    artifact_matrix = artifact_cases()
    scope_matrix = use_scope_cases()
    identity = task_identity()
    gates = [dict(gate) for gate in GATES]
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "findsylls offline syllable ground-truth toolkit (exact source absent and unpinned)",
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "incomplete": True,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": (
                "No exact findsylls source identity, LICENSE text, pinned runtime, "
                "reference output, rights clearance, ground-truth cohort or measured "
                "Rate evidence exists."
            ),
        },
        "scope": (
            "Task-local synthetic frame-energy Rate-profile fixture and source-artifact "
            "metadata boundary only; the candidate was not run and no claim is made."
        ),
        "task_identity": identity,
        "format": dict(FORMAT),
        "candidate_status": candidate_status(),
        "reference_evidence": reference_status(),
        "artifact_contract": {
            "contract_id": ARTIFACT_CONTRACT_ID,
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_identity_and_geometry_only; do not import_or_execute",
            "required_fields": list(ARTIFACT_REQUIRED_FIELDS),
        },
        "artifact_admission": artifact_admission(None),
        "artifact_cases": artifact_matrix,
        "use_scope_cases": scope_matrix,
        "rights": rights_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": gates,
        "release_gate_count": len(GATES),
        "rate_profile": rate_profile_summary(results),
        "rate_results": results,
        "controls": controls(results),
        "adverse": {
            "config_cases": config_cases,
            "config_rejections": sum(1 for case in config_cases.values() if case["status"] == "rejected"),
            "slot_cases": slot_cases,
            "slot_rejections": sum(1 for case in slot_cases.values() if case["status"] == "rejected"),
            "artifact_cases": artifact_matrix,
            "artifact_rejections": sum(1 for case in artifact_matrix.values() if case["status"] == "blocked"),
            "use_scope_cases": scope_matrix,
            "nonfinite_and_invalid_rejected": all(
                config_cases[name]["status"] == "rejected"
                for name in ("nonfinite_threshold", "string_threshold", "wrong_sample_rate", "unknown_condition")
            ) and all(
                slot_cases[name]["status"] == "rejected"
                for name in ("nonfinite_slot", "boolean_slot", "string_slot", "out_of_range_slot")
            ),
            "source_absent_blocked": artifact_matrix["absent"]["status"] == "blocked",
        },
        "state": {
            "deterministic_fixture_digest": True,
            "deterministic_mapping": True,
            "valid_control_accepted": config_cases["valid_control"]["status"] == "admitted_synthetic_control",
            "valid_slot_control_accepted": slot_cases["valid_control"]["status"] == "accepted_synthetic_control",
            "silence_has_undefined_rate": all(
                case["nuclei_proxy_per_second_milli"] is None
                for case in results["conditions"]["silence"]["rates"].values()
            ),
        },
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
        "pins": {
            "source": dict(SOURCE_PINS),
            "boundary": dict(BOUNDARY_PINS),
            "local_files": list(LOCAL_FILES),
            "board_full_file_hashed": False,
            "board_file_pinned": False,
        },
        "counts": {
            "conditions": len(CONDITIONS),
            "rate_cases": len(RATE_CASES),
            "rate_case_results": results["rate_case_count"],
            "fixture_slot_count": results["fixture_slot_count"],
            "synthetic_source_samples": results["total_source_samples"],
            "config_adverse_cases": len(config_cases),
            "slot_adverse_cases": len(slot_cases),
            "artifact_adverse_cases": len(artifact_matrix),
            "release_gates": len(GATES),
            "release_gates_blocked": sum(1 for gate in gates if gate["status"] == "blocked"),
        },
    }
    return report


def build_contract(artifact_pins: Dict[str, str] | None = None) -> Dict[str, Any]:
    gates = [dict(gate) for gate in GATES]
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "findsylls offline syllable ground-truth toolkit (exact source absent and unpinned)",
        "verification_profile": PROFILE,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "worktree": WORKTREE,
            "reviewer": REVIEWER,
            "mutable_claim_not_hashed": True,
        },
        "task_identity": task_identity(),
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "qualified": False,
        "scope": (
            "Writes are limited to " + TASK_PREFIX + "**; no public API/ABI, provider, "
            "registry, installed default, shared build, dependency lock, CI, board or "
            "handoff change."
        ),
        "format": dict(FORMAT),
        "candidate_status": candidate_status(),
        "reference_evidence": reference_status(),
        "artifact_contract": {
            "contract_id": ARTIFACT_CONTRACT_ID,
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_identity_and_geometry_only; do not import_or_execute",
            "required_fields": list(ARTIFACT_REQUIRED_FIELDS),
        },
        "artifact_admission": artifact_admission(None),
        "rights": rights_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": gates,
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic frame-energy Rate-profile arithmetic and rejection tests",
            "read-only documentation of the caller-supplied source-artifact metadata contract",
        ],
        "not_allowed": [
            "downloading, reading, importing, executing, vendoring or bundling the findsylls source tree",
            "installing or invoking any candidate dependency or runtime",
            "registering a provider, changing defaults or claiming duration/pitch/timing/quality/release",
        ],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "local_files": list(LOCAL_FILES),
        "artifact_pins": dict(artifact_pins or {}),
        "board_policy": {
            "selector": f"tasks[id={TASK}]",
            "full_file_hashed": False,
            "mutable_file": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "stable_fields_only": True,
            "mutable_fields_excluded": list(STABLE_TASK_IDENTITY["mutable_fields_excluded"]),
        },
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
    }
