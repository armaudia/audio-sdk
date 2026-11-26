# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence contract for the Krisp public-output row.

This is a *proposal-only*, **incomplete** and **not qualified** Evidence-profile
package for ``SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING``.  It does
**not** contain, download, copy, link, execute or emulate the licensed/restricted
cohort, the DNSMOS-C scorer, the NISQA checkpoint, the PyTorch runtime or the
Krisp processed-output set.  It reproduces only documented *metadata
validation*, *segment/window arithmetic* and *scenario-balanced aggregation*
over declared synthetic inputs, plus fail-closed admission contracts for
caller-supplied artefacts.

Every real result slot is ``None``.  Nothing here is a measured DNSMOS-C score,
a WER value, a human rating, a listening result, a device measurement, a
benchmark or a release claim.  The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING"
COMPONENT = "krisp-voice-isolation-public-output-scoring"
BASE_COMMIT = "cb3d9812875b741a320c6cfe22de8043952fdd16"
BRANCH = "swarm/SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
STATUS = "proposal_only_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
LOCAL_IDENTITY = "krisp-vi-public-output-scoring-evidence-contract-v1"

INSTALLED_V0 = "16 kHz mono float32, 160 samples per frame"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1

# ---- Documented cohort identity (from research/cpp-library-krisp-benchmark) --
DATASET_REPOSITORY = "Krisp-AI/VoiceIsolation-Benchmark-Dataset"
DATASET_REVISION = "626bac8ca07fb9b4846d4f62d27c321753160b36"
PROCESSED_REPOSITORY = "Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed"
PROCESSED_REVISION = "8759715197e39e0356125e3f3197a9854c38fa60"
PROCESSED_SUBSET = "vi_2_5_default"
ITEM_COUNT = 265
PROCESSED_TOTAL_BYTES = 647_960_782
SOURCE_SAMPLE_RATE_HZ = 32000
COHORT_LICENSE = "CC-BY-NC-4.0"
SCENARIOS = ("work", "call_center", "phone_calls")

# ---- Documented DNSMOS-C protocol ------------------------------------------
DNSC_SAMPLE_RATE_HZ = 16000
DNSC_SEGMENT_KINDS = ("primary", "mix")
DNSC_MIN_SEGMENT_MS = 1000
DNSC_WINDOW_MS = 10000
DNSC_HOP_MS = 5000
DNSC_MAX_DURATION_MS = 86_400_000
DNSC_OUTPUT = "DNSMOS_C"
DNSC_CHECKPOINT = "model_best.pt"
DNSC_SOURCE = "https://github.com/Hope-Liang/DNSMOS-C"
DNSC_PROTOCOL = (
    "16 kHz; score primary and mix segments only; drop segments shorter than "
    "1 s; repeat shorter-than-10 s segments to 10 s; 10 s windows with 5 s "
    "hops and an end-aligned tail; average segments within a scenario, then "
    "average the three scenarios with equal weight"
)
DNSC_METRIC_MIN = 1.0
DNSC_METRIC_MAX = 5.0
MAX_DURATION_MS = DNSC_MAX_DURATION_MS

# ---- Documented WER ensemble (explicitly unrun locally) --------------------
WER_CONFIG_COUNT = 11
WER_TOOL = "jiwer"
WER_TOOL_VERSION = "4.0.0"
WER_TEXT_NORMALIZATION = "nemo_wfst"
WER_PERCENT_MIN = 0.0
WER_PERCENT_MAX = 100.0

# ---- Source-reported comparison values (NOT reproduced here) ---------------
DOCUMENTED_SCORES: Dict[str, Dict[str, Any]] = {
    "raw": {
        "work": 3.374, "call_center": 3.600, "phone_calls": 3.133,
        "scenario_average": 3.369,
    },
    "krisp_vi_2_5_default": {
        "work": 3.944, "call_center": 4.018, "phone_calls": 3.482,
        "scenario_average": 3.815,
    },
    "audio_enhance_basic_v1": {
        "work": 3.575, "call_center": 3.794, "phone_calls": 3.189,
        "scenario_average": 3.519,
    },
    "audio_enhance_voice_focus_v1": {
        "work": 3.636, "call_center": 3.829, "phone_calls": 3.457,
        "scenario_average": 3.641,
    },
}
DOCUMENTED_CHANGES: Dict[str, Dict[str, float]] = {
    "krisp_vi_2_5_default": {
        "work": 0.571, "call_center": 0.418, "phone_calls": 0.348,
        "scenario_average": 0.446,
    },
    "audio_enhance_basic_v1": {
        "work": 0.202, "call_center": 0.194, "phone_calls": 0.055,
        "scenario_average": 0.150,
    },
    "audio_enhance_voice_focus_v1": {
        "work": 0.262, "call_center": 0.229, "phone_calls": 0.323,
        "scenario_average": 0.272,
    },
}
DOCUMENTED_PUBLISHED_KRISP = {
    "work": 3.96, "call_center": 4.02, "phone_calls": 3.45,
    "overall_raw_baseline": 3.40,
}
DOCUMENTED_WER = {
    "raw_percent": {
        "work": 31.84, "call_center": 23.83, "phone_calls": 3.48,
        "all_265_files": 23.24,
    },
    "krisp_vi_2_5_default_percent": {
        "work": 6.30, "call_center": 6.86, "phone_calls": 3.91,
        "all_265_files": 6.24,
    },
    "audio_enhance_percent": None,
    "config_count": WER_CONFIG_COUNT,
    "tool": WER_TOOL,
    "tool_version": WER_TOOL_VERSION,
    "text_normalization": WER_TEXT_NORMALIZATION,
    "measured_here": False,
}

# ---- Exact pins ------------------------------------------------------------
SOURCE_PINS: Dict[str, str] = {
    "research/cpp-library-krisp-benchmark-20261109.md":
        "7f3c80a2a9f266bbf112fb6ea89bda0bf9ccb1a9045e39cf42fdc5d49496a8e2",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/dnsmos-p-835-and-dnsmos-c/README.md":
        "eb7d069cc402aa37210dd2ebd43e45e840bc600693a947684e5341eb28fbd579",
    "docs/task-evidence/dnsmos-p-835-and-dnsmos-c/report.json":
        "f36074f915c3ad94c9441cebc221a23bd7f865969b7fab3009c2baa48ba92bc0",
    "docs/task-evidence/ears-preservation-screen-and-scorer-harness/README.md":
        "711da725fbddb7ab06272e6e2644a5b960cfb3da42d66748fddf147058dd8ff3",
    "docs/task-evidence/ears-preservation-screen-and-scorer-harness/report.json":
        "077f6acfb253dfc7d0de6a72b77d1c977fdf5289ec6333d1a3620dd372f45a1f",
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": "Krisp Voice Isolation public output scoring",
    "repository": "audio-sdk",
    "mode": "research-control",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "deliverable": (
        "Retain or reproduce the comparison as an optional SDK developer/"
        "evidence adapter alongside audio-bench, with a documented proceed/defer "
        "decision before exposing it as a processor. Use the pinned 265-output "
        "set only if permitted. Preserve scenario-balanced DNSMOS-C and the "
        "separate unrun WER ensemble."
    ),
    "acceptance": (
        "Apply the evidence acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates."
    ),
    "evidence": ["research/cpp-library-krisp-benchmark-20261109.md"],
    "write_scope": [
        "SDK provider, tool or evidence directory for "
        "krisp-voice-isolation-public-output-scoring and its own fixtures"
    ],
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}
MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "mutable": True,
    "gate": False,
    "hashed": False,
    "note": (
        "Only the stable linked-row fields above are compared. The mutable full "
        "board file is never hashed into canonical bytes or SOURCES.sha256."
    ),
}
SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "evidence_only": True,
    "installed_v0_format": INSTALLED_V0,
    "real_processed_outputs": False,
    "real_raw_corpus": False,
    "real_transcripts_or_labels": False,
    "real_dnsmos_c_checkpoint": False,
    "real_dnsmos_c_source": False,
    "licensed_source_or_binary": False,
    "model_runtime_executed": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "downloads": False,
    "network_requests": False,
    "device_timing": False,
    "listening": False,
    "benchmark_claim": False,
    "release_claim": False,
    "predicted_scores_kept_separate_from_subjective_mos": True,
    "wer_ensemble_run": False,
}
PUBLIC_SURFACE: Dict[str, bool] = {
    "abi_change": False,
    "benchmark_claim": False,
    "ci_change": False,
    "descriptor_default_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_change": False,
    "registry_change": False,
    "release_claim": False,
    "shared_cmakelists_change": False,
}
QUALIFICATION: Dict[str, Any] = {
    "status": QUALIFICATION_STATUS,
    "qualifies": False,
    "incomplete": True,
    "proposal_only": True,
    "missing_result_promoted": False,
    "processor_exposure": False,
    "release_claim": False,
    "all_release_gates_blocked": True,
}

RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "exact_processed_output_identity_and_rights",
        "requirement": (
            "The exact processed WAV bytes for the 265-item "
            "Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed "
            "vi_2_5_default subset at revision "
            "8759715197e39e0356125e3f3197a9854c38fa60, 647,960,782 bytes in "
            "total, with per-file SHA-256 digests, immutable retrieval and "
            "written permission to score and redistribute derived bundles."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "raw_corpus_transcripts_labels_and_rights",
        "requirement": (
            "The exact 265 mono 32 kHz PCM16 raw recordings, transcripts, "
            "scenario metadata and target-speech labels at dataset revision "
            "626bac8ca07fb9b4846d4f62d27c321753160b36, with item-level "
            "CC-BY-NC-4.0 scope and a redistribution/derived-score decision."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "dnsmos_c_checkpoint_source_and_terms",
        "requirement": (
            "The exact NISQA checkpoint runs/NISQA/model_best.pt with an "
            "immutable revision, byte count, SHA-256 digest, model card and "
            "training-data statement, plus the pinned DNSMOS-C feature-"
            "extraction source revision and its code and weight terms. The "
            "recorded report names no checkpoint digest and no scorer revision."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "approved_scoring_runtime_and_platform",
        "requirement": (
            "A pinned and approved torch/NISQA/librosa/numpy environment with a "
            "lock file, recorded host, accelerator and seeds; an incidental "
            "importable environment is not a qualification."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "scenario_balanced_aggregation_parity",
        "requirement": (
            "Numerical parity against the official DNSMOS-C implementation for "
            "the 1 s minimum, 10 s repeat, 10 s window / 5 s hop, end-aligned "
            "tail, the 2,352-window / 604-target-segment accounting and the "
            "equal-weight three-scenario aggregation."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "unrun_wer_ensemble_separation",
        "requirement": (
            "A separately labelled, locally executed WER protocol if any WER "
            "claim is made; the source-reported 11-configuration aggregate "
            "using jiwer 4.0.0 and NeMo WFST normalization must remain "
            "explicitly unrun and must never be merged with DNSMOS-C."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "valid_invalid_item_validation_and_evidence_separation",
        "requirement": (
            "One representative valid item and one invalid/missing item "
            "validated end to end through the reported bundle, with predicted "
            "DNSMOS-C values kept separate from human listening, intelligibility "
            "and any device/timing measurement."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "evidence_adapter_intake_and_release_review",
        "requirement": (
            "Opt-in developer/evidence-adapter intake, licence and public-"
            "surface review, independent exact-head approval and explicit "
            "release admission before any processor or SDK exposure."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]

ABSENCE_PROBES: List[Dict[str, str]] = [
    {
        "id": "processed_outputs",
        "path": "data/krisp-vi-benchmark/processed/vi_2_5_default",
        "kind": "directory",
        "role": "265 processed WAV outputs",
    },
    {
        "id": "raw_corpus",
        "path": "data/krisp-vi-benchmark/raw",
        "kind": "directory",
        "role": "265 raw 32 kHz recordings",
    },
    {
        "id": "transcripts_and_labels",
        "path": "data/krisp-vi-benchmark/transcripts",
        "kind": "directory",
        "role": "transcripts, scenario metadata and target-speech labels",
    },
    {
        "id": "dnsmos_c_checkpoint",
        "path": "data/models/nisqa/model_best.pt",
        "kind": "file",
        "role": "NISQA checkpoint used by DNSMOS-C",
    },
    {
        "id": "scoring_runtime",
        "path": "data/envs/krisp-dnsmos-c",
        "kind": "directory",
        "role": "pinned DNSMOS-C/NISQA runtime environment",
    },
    {
        "id": "score_bundle",
        "path": "data/score-bundles/krisp-vi-2-5-default",
        "kind": "directory",
        "role": "per-item and per-scenario score bundle",
    },
    {
        "id": "run_directory",
        "path": "data/runs/krisp-vi-2-5-default",
        "kind": "directory",
        "role": "recorded scoring run and logs",
    },
]

REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "processed_outputs",
        "artifact": (
            "265 processed vi_2_5_default WAVs, 16 kHz mono PCM16, "
            "647,960,782 bytes total, per-file SHA-256."
        ),
        "expected_paths": ["data/krisp-vi-benchmark/processed/vi_2_5_default"],
        "present": False,
        "rights_requirement": (
            "CC-BY-NC-4.0 item-level terms plus written approval for the exact "
            "scoring, retention and derived-bundle use."
        ),
        "why_blocked": (
            "No processed-output directory or item manifest is present; nothing "
            "was downloaded, copied or substituted."
        ),
    },
    {
        "id": "raw_corpus_and_labels",
        "artifact": (
            "265 raw 32 kHz mono PCM16 recordings with transcripts, scenario "
            "metadata and target-speech labels at revision "
            "626bac8ca07fb9b4846d4f62d27c321753160b36."
        ),
        "expected_paths": [
            "data/krisp-vi-benchmark/raw",
            "data/krisp-vi-benchmark/transcripts",
        ],
        "present": False,
        "rights_requirement": (
            "Item-level CC-BY-NC-4.0 scope and a redistribution/derived-score "
            "decision; the licence is non-commercial research media."
        ),
        "why_blocked": (
            "The raw corpus, transcripts and labels are absent from the "
            "workspace and no rights review is recorded."
        ),
    },
    {
        "id": "dnsmos_c_scorer_identity",
        "artifact": (
            "NISQA checkpoint model_best.pt with immutable revision and digest, "
            "plus the pinned DNSMOS-C feature-extraction source revision."
        ),
        "expected_paths": ["data/models/nisqa/model_best.pt"],
        "present": False,
        "rights_requirement": (
            "Checkpoint licence, model card, training-data statement and "
            "redistribution/execution approval for the exact files."
        ),
        "why_blocked": (
            "No checkpoint or DNSMOS-C checkout is present; the report records "
            "no checkpoint digest and no immutable scorer revision."
        ),
    },
    {
        "id": "approved_runtime",
        "artifact": (
            "Pinned torch/NISQA/librosa/numpy runtime with lock, host and seeds."
        ),
        "expected_paths": ["data/envs/krisp-dnsmos-c"],
        "present": False,
        "rights_requirement": "Runtime licences and execution approval for the exact pins.",
        "why_blocked": (
            "No approved scoring environment or lock exists for this task."
        ),
    },
    {
        "id": "score_bundle_and_rights",
        "artifact": (
            "Per-item and per-scenario DNSMOS-C bundle with aggregation, "
            "failed-item retention and a redistribution decision."
        ),
        "expected_paths": ["data/score-bundles/krisp-vi-2-5-default"],
        "present": False,
        "rights_requirement": (
            "Derived-score redistribution and publication policy for the "
            "non-commercial corpus."
        ),
        "why_blocked": (
            "No score bundle exists and no derived-score publication right is "
            "granted."
        ),
    },
    {
        "id": "wer_ensemble",
        "artifact": (
            "Independent local 11-configuration WER run if a WER claim is made."
        ),
        "expected_paths": [],
        "present": False,
        "rights_requirement": "ASR model, corpus and derived-hypothesis terms.",
        "why_blocked": (
            "The WER ensemble is explicitly unrun; only the source-reported "
            "aggregate is preserved and it is never merged with DNSMOS-C."
        ),
    },
    {
        "id": "evidence_adapter_review",
        "artifact": (
            "Evidence-adapter intake, predicted-versus-human labelling review, "
            "aggregation/uncertainty policy and release approval."
        ),
        "expected_paths": [],
        "present": False,
        "rights_requirement": "Independent reviewer and release approval.",
        "why_blocked": "No intake, review or release decision is in scope here.",
    },
]
NON_CLAIMS: List[str] = [
    "No Krisp processed output, raw recording, transcript, label or score bundle is present, downloaded, copied, bundled or regenerated.",
    "No NISQA checkpoint, DNSMOS-C source, torch/NISQA runtime or emulator is present, linked or executed.",
    "No DNSMOS-C score, WER value, ranking, threshold or oracle is claimed; every real result slot is null.",
    "Segment counts, window counts and equal-weight arithmetic on declared values are geometry, not measured quality.",
    "The source-reported comparison and WER tables are preserved as source-reported context, not reproduced here.",
    "No listening, device-timing, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No provider or processor is registered, exposed or default-enabled.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --all",
    "python3 run.py --check",
    "python3 verify.py",
]

SPDX_COPYRIGHT_KEY = "SPDX-FileCopyright" "Text"
SPDX_LICENSE_KEY = "SPDX-License-" "Identifier"

REPORT_KEYS = {
    SPDX_COPYRIGHT_KEY,
    SPDX_LICENSE_KEY,
    "schema_id",
    "task",
    "component",
    "profile",
    "base_commit",
    "branch",
    "status",
    "completeness",
    "decision",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "scope",
    "public_surface",
    "cohort",
    "scorer",
    "wer",
    "documented_scores",
    "documented_changes",
    "documented_published_context",
    "aggregation_reference",
    "geometry_reference",
    "fixtures",
    "absence_probes",
    "artifact_assessment",
    "runs",
    "controls",
    "adverse_results",
    "missing_results",
    "failure_controls",
    "acceptance_profile",
    "observed_provenance",
    "separation_from_siblings",
    "release_gates",
    "non_claims",
    "reproduction",
    "regeneration",
}

CONTRACT_KEYS = {
    "schema_id",
    "task",
    "component",
    "profile",
    "base_commit",
    "branch",
    "status",
    "completeness",
    "decision",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "scope",
    "public_surface",
    "cohort_contract_summary",
    "scorer_contract_summary",
    "required_artifacts",
    "release_gates",
    "artifact_pins",
    "reproduction",
    "non_claims",
}


class ReferenceError(ValueError):
    """Explicit rejection; no rejected value is scored or promoted."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    return parse_strict_json_text(path.read_text(encoding="utf-8"))


def parse_strict_json_text(text: str) -> Any:
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    if not text.strip():
        raise ValueError("empty_document")
    if text.startswith("\ufeff"):
        raise ValueError("utf8_bom_rejected")
    try:
        value = json.loads(
            text,
            object_pairs_hook=unique_pairs,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError:
        raise ValueError("invalid_json") from None
    if not isinstance(value, dict):
        raise ValueError("top_level_document_must_be_object")
    return value


def strict_error_code(text: str) -> str:
    try:
        parse_strict_json_text(text)
    except ValueError as error:
        message = str(error)
        if message.startswith(("duplicate_json_key:", "non_json_constant:")):
            return message
        if message.startswith("json_"):
            return "invalid_json"
        return message
    raise ReferenceError("strict_text_was_accepted")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_bytes(report).decode("utf-8")
    payload = (text + "\n").encode("utf-8")
    return text, sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_int(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReferenceError(code)
    return value


def _as_finite(value: Any, code: str,
               minimum: Optional[float] = None,
               maximum: Optional[float] = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceError(code)
    number = float(value)
    if not math.isfinite(number):
        raise ReferenceError(code)
    if minimum is not None and number < minimum:
        raise ReferenceError(code)
    if maximum is not None and number > maximum:
        raise ReferenceError(code)
    return number


def _as_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReferenceError(code)
    return value


def _is_hex(text: str, length: int) -> bool:
    return len(text) == length and all(
        character in "0123456789abcdef" for character in text
    )


def _scenario(value: Any) -> str:
    text = _as_text(value, "scenario_requires_text")
    if text not in SCENARIOS:
        raise ReferenceError("unsupported_scenario")
    return text


# ---------------------------------------------------------------------------
# DNSMOS-C segment/window arithmetic
# ---------------------------------------------------------------------------


def segment_kind_accepted(kind: Any) -> str:
    text = _as_text(kind, "segment_kind_requires_text")
    if text not in DNSC_SEGMENT_KINDS:
        raise ReferenceError("unsupported_segment_kind")
    return text


def _interval_union_ms(intervals: Sequence[Tuple[int, int]]) -> int:
    if not intervals:
        return 0
    ordered = sorted(intervals)
    total = 0
    start, end = ordered[0]
    for next_start, next_end in ordered[1:]:
        if next_start > end:
            total += end - start
            start, end = next_start, next_end
        elif next_end > end:
            end = next_end
    total += end - start
    return total


def dnsmos_c_segment_plan(duration_ms: int, kind: str = "primary") -> Dict[str, Any]:
    """Reproduce only the documented DNSMOS-C segment/window policy."""
    accepted_kind = segment_kind_accepted(kind)
    duration = _as_int(duration_ms, "segment_plan_requires_int_ms")
    if duration <= 0:
        raise ReferenceError("segment_plan_requires_positive_ms")
    if duration > MAX_DURATION_MS:
        raise ReferenceError("segment_plan_duration_exceeds_bound")
    if duration < DNSC_MIN_SEGMENT_MS:
        return {
            "segment_kind": accepted_kind,
            "duration_ms": duration,
            "dropped": True,
            "drop_reason": "segment_shorter_than_1s",
            "repeated": False,
            "repeat_count": 0,
            "tiled_ms": duration,
            "tiling_truncated_ms": 0,
            "windows": [],
            "window_count": 0,
            "distinct_coverage_ms": 0,
            "end_aligned_tail": False,
            "scored": False,
            "qualifies": False,
        }
    if duration < DNSC_WINDOW_MS:
        repeat_count = -(-DNSC_WINDOW_MS // duration)
        tiled = duration * repeat_count
        return {
            "segment_kind": accepted_kind,
            "duration_ms": duration,
            "dropped": False,
            "drop_reason": None,
            "repeated": True,
            "repeat_count": repeat_count,
            "tiled_ms": tiled,
            "tiling_truncated_ms": tiled - DNSC_WINDOW_MS,
            "windows": [{"start_ms": 0, "end_ms": DNSC_WINDOW_MS,
                         "end_aligned_tail": False}],
            "window_count": 1,
            "distinct_coverage_ms": DNSC_WINDOW_MS,
            "end_aligned_tail": False,
            "scored": False,
            "qualifies": False,
        }
    starts = list(range(0, duration - DNSC_WINDOW_MS + 1, DNSC_HOP_MS))
    tail = False
    if starts[-1] != duration - DNSC_WINDOW_MS:
        starts.append(duration - DNSC_WINDOW_MS)
        tail = True
    windows = [
        {
            "start_ms": start,
            "end_ms": start + DNSC_WINDOW_MS,
            "end_aligned_tail": tail and start == starts[-1],
        }
        for start in starts
    ]
    coverage = _interval_union_ms(
        [(window["start_ms"], window["end_ms"]) for window in windows]
    )
    return {
        "segment_kind": accepted_kind,
        "duration_ms": duration,
        "dropped": False,
        "drop_reason": None,
        "repeated": False,
        "repeat_count": 1,
        "tiled_ms": duration,
        "tiling_truncated_ms": 0,
        "windows": windows,
        "window_count": len(windows),
        "distinct_coverage_ms": coverage,
        "end_aligned_tail": tail,
        "scored": False,
        "qualifies": False,
    }


def dnsmos_c_plan(segments: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(segments, (list, tuple)) or not segments:
        raise ReferenceError("segment_list_requires_non_empty_list")
    rows: List[Dict[str, Any]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ReferenceError("segment_requires_object")
        if set(segment) != {"kind", "duration_ms"}:
            raise ReferenceError("segment_field_set_mismatch")
        rows.append(dnsmos_c_segment_plan(segment["duration_ms"], segment["kind"]))
        rows[-1]["segment_index"] = index
    return {
        "segments": rows,
        "segment_count": len(rows),
        "scored_segment_count": sum(1 for row in rows if not row["dropped"]),
        "dropped_segment_count": sum(1 for row in rows if row["dropped"]),
        "window_count": sum(row["window_count"] for row in rows),
        "protocol": DNSC_PROTOCOL,
        "scored": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def equal_weight_average(per_scenario: Dict[str, Any]) -> float:
    """Exact equal-weight mean over exactly the three declared scenarios."""
    if not isinstance(per_scenario, dict):
        raise ReferenceError("scenario_map_requires_object")
    if set(per_scenario) != set(SCENARIOS):
        raise ReferenceError("scenario_map_requires_exactly_three_declared")
    values = [
        _as_finite(per_scenario[name], "scenario_value_requires_finite_number",
                   DNSC_METRIC_MIN, DNSC_METRIC_MAX)
        for name in SCENARIOS
    ]
    return math.fsum(values) / 3.0


def validate_metric_value(value: Any) -> Dict[str, Any]:
    number = _as_finite(value, "metric_requires_finite_number",
                        DNSC_METRIC_MIN, DNSC_METRIC_MAX)
    return {
        "accepted_metadata": True,
        "value": number,
        "is_prediction": True,
        "is_human_rating": False,
        "is_mos": False,
        "measured_here": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied cohort and scorer manifests (metadata validation only)
# ---------------------------------------------------------------------------

COHORT_MANIFEST_KEYS = {
    "schema_id",
    "dataset_repository",
    "dataset_revision",
    "processed_repository",
    "processed_revision",
    "subset",
    "item_count",
    "total_bytes",
    "sample_rate_hz",
    "channels",
    "license",
    "items",
}
COHORT_ITEM_KEYS = {
    "id",
    "scenario",
    "sha256",
    "bytes",
    "target_speech",
    "transcript_sha256",
    "rights_cleared",
}
SCORER_MANIFEST_KEYS = {
    "schema_id",
    "metric",
    "sample_rate_hz",
    "channels",
    "checkpoint",
    "source_revision",
    "license",
    "runtime",
}
CHECKPOINT_KEYS = {"name", "sha256", "bytes", "license_id"}
RUNTIME_KEYS = {"name", "version", "license_id"}
UNKNOWN_LICENSES = {"", "unknown", "UNKNOWN", "none", "NOASSERTION", "unlicensed"}


def validate_cohort_manifest(value: Any) -> Dict[str, Any]:
    """Validate cohort identity and rights metadata; nothing is loaded."""
    if not isinstance(value, dict):
        raise ReferenceError("cohort_manifest_requires_object")
    if set(value) != COHORT_MANIFEST_KEYS:
        raise ReferenceError("cohort_manifest_field_set_mismatch")
    if value["schema_id"] != "audio-sdk/krisp-vi-public-output-cohort/0.1":
        raise ReferenceError("cohort_manifest_schema_mismatch")
    if value["dataset_repository"] != DATASET_REPOSITORY:
        raise ReferenceError("cohort_dataset_repository_mismatch")
    if value["processed_repository"] != PROCESSED_REPOSITORY:
        raise ReferenceError("cohort_processed_repository_mismatch")
    for field in ("dataset_revision", "processed_revision"):
        revision = value[field]
        if not isinstance(revision, str) or not _is_hex(revision, 40):
            raise ReferenceError("cohort_revision_must_be_40_hex")
    if value["dataset_revision"] != DATASET_REVISION:
        raise ReferenceError("cohort_dataset_revision_mismatch")
    if value["processed_revision"] != PROCESSED_REVISION:
        raise ReferenceError("cohort_processed_revision_mismatch")
    if value["subset"] != PROCESSED_SUBSET:
        raise ReferenceError("cohort_subset_mismatch")
    if _as_int(value["item_count"], "cohort_item_count_requires_int") != ITEM_COUNT:
        raise ReferenceError("cohort_item_count_must_be_265")
    if _as_int(value["total_bytes"],
               "cohort_total_bytes_requires_int") != PROCESSED_TOTAL_BYTES:
        raise ReferenceError("cohort_total_bytes_mismatch")
    if _as_int(value["sample_rate_hz"],
               "cohort_sample_rate_requires_int") != SAMPLE_RATE_HZ:
        raise ReferenceError("cohort_sample_rate_must_be_16000")
    if _as_int(value["channels"], "cohort_channels_requires_int") != CHANNELS:
        raise ReferenceError("cohort_channels_must_be_1")
    if value["license"] != COHORT_LICENSE:
        raise ReferenceError("cohort_license_must_be_cc_by_nc_4_0")
    items = value["items"]
    if not isinstance(items, list):
        raise ReferenceError("cohort_items_requires_list")
    if len(items) != ITEM_COUNT:
        raise ReferenceError("cohort_items_count_mismatch")
    identifiers: List[str] = []
    total = 0
    for item in items:
        if not isinstance(item, dict) or set(item) != COHORT_ITEM_KEYS:
            raise ReferenceError("cohort_item_field_set_mismatch")
        identifier = _as_text(item["id"], "cohort_item_id_requires_text")
        if identifier in identifiers:
            raise ReferenceError("cohort_duplicate_item_id")
        identifiers.append(identifier)
        _scenario(item["scenario"])
        if not isinstance(item["sha256"], str) or not _is_hex(item["sha256"], 64):
            raise ReferenceError("cohort_item_sha256_must_be_64_lower_hex")
        size = _as_int(item["bytes"], "cohort_item_bytes_requires_int")
        if size <= 0:
            raise ReferenceError("cohort_item_bytes_must_be_positive")
        total += size
        if not isinstance(item["target_speech"], bool):
            raise ReferenceError("cohort_item_target_speech_requires_bool")
        if not isinstance(item["transcript_sha256"], str) \
                or not _is_hex(item["transcript_sha256"], 64):
            raise ReferenceError("cohort_item_transcript_sha256_requires_64_hex")
        if item["rights_cleared"] is not True:
            raise ReferenceError("cohort_item_rights_not_cleared")
    if total != PROCESSED_TOTAL_BYTES:
        raise ReferenceError("cohort_item_bytes_do_not_sum_to_total")
    return {
        "accepted_metadata": True,
        "schema_id": value["schema_id"],
        "subset": PROCESSED_SUBSET,
        "item_count": ITEM_COUNT,
        "total_bytes": PROCESSED_TOTAL_BYTES,
        "license": COHORT_LICENSE,
        "admitted_for_scoring": False,
        "admission_blocker": (
            "no scorer checkpoint, pinned DNSMOS-C revision, approved runtime "
            "or item-level derived-score permission exists in this package"
        ),
        "qualifies": False,
    }


def validate_scorer_manifest(value: Any) -> Dict[str, Any]:
    """Validate scorer identity and rights metadata; nothing is executed."""
    if not isinstance(value, dict):
        raise ReferenceError("scorer_manifest_requires_object")
    if set(value) != SCORER_MANIFEST_KEYS:
        raise ReferenceError("scorer_manifest_field_set_mismatch")
    if value["schema_id"] != "audio-sdk/krisp-dnsmos-c-scorer-manifest/0.1":
        raise ReferenceError("scorer_manifest_schema_mismatch")
    if value["metric"] != "dnsmos_c":
        raise ReferenceError("scorer_manifest_unknown_metric")
    if _as_int(value["sample_rate_hz"],
               "scorer_sample_rate_requires_int") != SAMPLE_RATE_HZ:
        raise ReferenceError("scorer_sample_rate_must_be_16000")
    if _as_int(value["channels"], "scorer_channels_requires_int") != CHANNELS:
        raise ReferenceError("scorer_channels_must_be_1")
    revision = value["source_revision"]
    if not isinstance(revision, str) or not _is_hex(revision, 40):
        raise ReferenceError("scorer_source_revision_must_be_40_hex")
    license_id = value["license"]
    if not isinstance(license_id, str) or license_id in UNKNOWN_LICENSES:
        raise ReferenceError("scorer_license_requires_identified_terms")
    checkpoint = value["checkpoint"]
    if not isinstance(checkpoint, dict) or set(checkpoint) != CHECKPOINT_KEYS:
        raise ReferenceError("scorer_checkpoint_field_set_mismatch")
    if checkpoint["name"] != DNSC_CHECKPOINT:
        raise ReferenceError("scorer_checkpoint_name_must_be_model_best_pt")
    if not isinstance(checkpoint["sha256"], str) \
            or not _is_hex(checkpoint["sha256"], 64):
        raise ReferenceError("scorer_checkpoint_sha256_must_be_64_lower_hex")
    if _as_int(checkpoint["bytes"],
               "scorer_checkpoint_bytes_requires_int") <= 0:
        raise ReferenceError("scorer_checkpoint_bytes_must_be_positive")
    checkpoint_license = checkpoint["license_id"]
    if not isinstance(checkpoint_license, str) \
            or checkpoint_license in UNKNOWN_LICENSES:
        raise ReferenceError("scorer_checkpoint_license_requires_identified_terms")
    runtime = value["runtime"]
    if not isinstance(runtime, dict) or set(runtime) != RUNTIME_KEYS:
        raise ReferenceError("scorer_runtime_field_set_mismatch")
    for field in ("name", "version"):
        _as_text(runtime[field], "scorer_runtime_" + field + "_requires_text")
    runtime_license = runtime["license_id"]
    if not isinstance(runtime_license, str) \
            or runtime_license in UNKNOWN_LICENSES:
        raise ReferenceError("scorer_runtime_license_requires_identified_terms")
    return {
        "accepted_metadata": True,
        "metric": "dnsmos_c",
        "checkpoint": DNSC_CHECKPOINT,
        "admitted_for_execution": False,
        "admission_blocker": (
            "metadata acceptance is not execution rights; no approved runtime, "
            "recorded checkpoint digest in the source report or runner exists"
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# WER record (source-reported only)
# ---------------------------------------------------------------------------

WER_RECORD_KEYS = {
    "config_count",
    "tool",
    "tool_version",
    "text_normalization",
    "raw_percent",
    "processed_percent",
    "library_percent",
    "scope",
}


def validate_wer_record(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ReferenceError("wer_record_requires_object")
    if set(value) != WER_RECORD_KEYS:
        raise ReferenceError("wer_record_field_set_mismatch")
    if _as_int(value["config_count"], "wer_config_count_requires_int") \
            != WER_CONFIG_COUNT:
        raise ReferenceError("wer_config_count_must_be_11")
    if value["tool"] != WER_TOOL:
        raise ReferenceError("wer_tool_must_be_jiwer")
    if value["tool_version"] != WER_TOOL_VERSION:
        raise ReferenceError("wer_tool_version_must_be_4_0_0")
    if value["text_normalization"] != WER_TEXT_NORMALIZATION:
        raise ReferenceError("wer_text_normalization_must_be_nemo_wfst")
    _as_finite(value["raw_percent"], "wer_raw_percent_requires_finite_percent",
               WER_PERCENT_MIN, WER_PERCENT_MAX)
    _as_finite(value["processed_percent"],
               "wer_processed_percent_requires_finite_percent",
               WER_PERCENT_MIN, WER_PERCENT_MAX)
    if value["library_percent"] is not None:
        raise ReferenceError("wer_library_must_stay_unmeasured")
    _as_text(value["scope"], "wer_scope_requires_text")
    return {
        "accepted_metadata": True,
        "config_count": WER_CONFIG_COUNT,
        "library_measured": False,
        "measured_here": False,
        "merged_with_dnsmos_c": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Documented context, geometry and fixtures
# ---------------------------------------------------------------------------


def documented_scores() -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for condition in (
        "raw",
        "krisp_vi_2_5_default",
        "audio_enhance_basic_v1",
        "audio_enhance_voice_focus_v1",
    ):
        values = DOCUMENTED_SCORES[condition]
        row: Dict[str, Any] = {
            "condition": condition,
            "work": values["work"],
            "call_center": values["call_center"],
            "phone_calls": values["phone_calls"],
            "scenario_average": values["scenario_average"],
            "change": None,
        }
        if condition in DOCUMENTED_CHANGES:
            change = DOCUMENTED_CHANGES[condition]
            row["change"] = {
                "work": change["work"],
                "call_center": change["call_center"],
                "phone_calls": change["phone_calls"],
                "scenario_average": change["scenario_average"],
            }
        rows.append(row)
    return {
        "metric": "dnsmos_c",
        "scale": [DNSC_METRIC_MIN, DNSC_METRIC_MAX],
        "labels": "source_reported_predicted_dnsmos_c",
        "is_human_rating": False,
        "is_mos": False,
        "reproduced_here": False,
        "conditions": rows,
        "change_note": (
            "change values are source-reported; recomputing them from the "
            "3-decimal table would not reproduce the report's rounding"
        ),
        "scenario_average_rule": "unweighted mean of the three scenario values",
        "qualifies": False,
    }


def documented_changes() -> Dict[str, Any]:
    return {
        "labels": "source_reported_change_vs_rescored_raw",
        "reproduced_here": False,
        "changes": {
            condition: dict(values)
            for condition, values in DOCUMENTED_CHANGES.items()
        },
        "qualifies": False,
    }


def documented_published_context() -> Dict[str, Any]:
    return {
        "labels": "vendor_published_not_measured_here",
        "per_scenario_krisp": dict(DOCUMENTED_PUBLISHED_KRISP),
        "note": (
            "The re-scored Krisp outputs were reported close to these vendor "
            "values; the differences were attributed to scorer implementation "
            "details. They are not reproduced here."
        ),
        "reproduced_here": False,
        "qualifies": False,
    }


def wer_record() -> Dict[str, Any]:
    return {
        "status": "source_reported_not_run_here",
        "raw_percent": dict(DOCUMENTED_WER["raw_percent"]),
        "krisp_vi_2_5_default_percent": dict(
            DOCUMENTED_WER["krisp_vi_2_5_default_percent"]
        ),
        "audio_enhance_percent": None,
        "audio_enhance_status": "not_measured",
        "config_count": WER_CONFIG_COUNT,
        "tool": WER_TOOL,
        "tool_version": WER_TOOL_VERSION,
        "text_normalization": WER_TEXT_NORMALIZATION,
        "measured_here": False,
        "merged_with_dnsmos_c": False,
        "reason": (
            "one local ASR engine cannot reproduce an 11-configuration "
            "corpus-level aggregate; the local attempt was stopped"
        ),
        "qualifies": False,
    }


def cohort_record() -> Dict[str, Any]:
    return {
        "dataset_repository": DATASET_REPOSITORY,
        "dataset_revision": DATASET_REVISION,
        "processed_repository": PROCESSED_REPOSITORY,
        "processed_revision": PROCESSED_REVISION,
        "processed_subset": PROCESSED_SUBSET,
        "item_count": ITEM_COUNT,
        "processed_total_bytes": PROCESSED_TOTAL_BYTES,
        "source_sample_rate_hz": SOURCE_SAMPLE_RATE_HZ,
        "processed_sample_rate_hz": DNSC_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "license": COHORT_LICENSE,
        "scenarios": list(SCENARIOS),
        "scenario_item_counts": {name: None for name in SCENARIOS},
        "target_references": "target-speech labels recorded as present in the corpus; absent here",
        "permitted_use_here": False,
        "present": False,
        "reason": (
            "the 265 processed outputs, raw recordings, transcripts and labels "
            "are not staged in this workspace and no written permission covers "
            "scoring, retention or derived-score redistribution"
        ),
        "qualifies": False,
    }


def scorer_record() -> Dict[str, Any]:
    return {
        "id": "dnsmos_c",
        "protocol": DNSC_PROTOCOL,
        "sample_rate_hz": DNSC_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "segment_kinds": list(DNSC_SEGMENT_KINDS),
        "min_segment_ms": DNSC_MIN_SEGMENT_MS,
        "window_ms": DNSC_WINDOW_MS,
        "hop_ms": DNSC_HOP_MS,
        "output": DNSC_OUTPUT,
        "checkpoint_path": "runs/NISQA/" + DNSC_CHECKPOINT,
        "checkpoint_sha256": None,
        "source_url": DNSC_SOURCE,
        "source_revision": None,
        "runtime_pinned": False,
        "documented_accounting": {
            "windows_per_condition": 2352,
            "scored_target_segments": 604,
            "labels": "source_reported",
        },
        "status": "blocked",
        "score_slots": {
            "raw": None,
            "krisp_vi_2_5_default": None,
            "audio_enhance_basic_v1": None,
            "audio_enhance_voice_focus_v1": None,
        },
        "measured_here": False,
        "is_human_rating": False,
        "is_mos": False,
        "qualifies": False,
    }


def aggregation_reference() -> Dict[str, Any]:
    synthetic = equal_weight_average(
        {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0}
    )
    recomputed: Dict[str, Any] = {}
    for condition in DOCUMENTED_SCORES:
        values = DOCUMENTED_SCORES[condition]
        averaged = equal_weight_average(
            {name: values[name] for name in SCENARIOS}
        )
        recomputed[condition] = {
            "recomputed": round(averaged, 10),
            "source_reported": values["scenario_average"],
            "matches_at_three_decimals":
                round(averaged, 3) == values["scenario_average"],
        }
    return {
        "synthetic_inputs": {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0},
        "synthetic_average": synthetic,
        "rule": "equal weight across exactly the three declared scenarios",
        "documented_recomputation": recomputed,
        "recomputation_is_not_score_reproduction": True,
        "scores_reproduced": False,
        "qualifies": False,
    }


def geometry_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for kind, duration in (
        ("primary", 999),
        ("mix", 1000),
        ("primary", 4000),
        ("mix", 10000),
        ("primary", 12345),
        ("mix", 15000),
        ("primary", 20000),
    ):
        plan = dnsmos_c_segment_plan(duration, kind)
        cases.append({
            "segment_kind": kind,
            "duration_ms": duration,
            "dropped": plan["dropped"],
            "repeated": plan["repeated"],
            "repeat_count": plan["repeat_count"],
            "window_count": plan["window_count"],
            "end_aligned_tail": plan["end_aligned_tail"],
            "first_window": None if not plan["windows"] else [
                plan["windows"][0]["start_ms"], plan["windows"][0]["end_ms"]
            ],
            "last_window": None if not plan["windows"] else [
                plan["windows"][-1]["start_ms"], plan["windows"][-1]["end_ms"]
            ],
            "scored": False,
            "qualifies": False,
        })
    return cases


def fixture_payload() -> Dict[str, Any]:
    """Declared synthetic arithmetic values; no audio is written or read."""
    values = [3.0, 3.5, 4.0]
    payload = ("|".join("%.1f" % value for value in values)).encode("ascii")
    return {
        "kind": "declared_synthetic_scenario_values",
        "scenarios": dict(zip(SCENARIOS, values)),
        "average": equal_weight_average(dict(zip(SCENARIOS, values))),
        "digest": sha256_bytes(payload),
        "contains_audio": False,
        "scored": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Absence probes and assessment
# ---------------------------------------------------------------------------


def absence_probes() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for probe in ABSENCE_PROBES:
        path = WORKSPACE / probe["path"]
        rows.append({
            "id": probe["id"],
            "path": probe["path"],
            "kind": probe["kind"],
            "role": probe["role"],
            "present": path.exists(),
        })
    return rows


def artifact_assessment() -> Dict[str, Any]:
    probes = absence_probes()
    any_present = any(row["present"] for row in probes)
    return {
        "all_required_absent": not any_present,
        "probe_root": "workspace-relative",
        "probes": probes,
        "checkpoint_identity": {
            "path_recorded": True,
            "digest_recorded": False,
            "source_revision_recorded": False,
            "note": (
                "the source report names runs/NISQA/model_best.pt but records "
                "no checkpoint digest and no immutable DNSMOS-C revision"
            ),
        },
        "processed_output_identity": {
            "count_recorded": ITEM_COUNT,
            "total_bytes_recorded": PROCESSED_TOTAL_BYTES,
            "revision_recorded": PROCESSED_REVISION,
            "per_file_digests_recorded": False,
            "note": "aggregate bytes and revision only; no per-file manifest",
        },
        "runtime_presence": {
            "present": not any(
                row["present"] for row in probes if row["id"] == "scoring_runtime"
            ),
            "note": (
                "no approved torch/NISQA/librosa runtime, lock or host record "
                "exists for this task; an incidental import would not qualify"
            ),
        },
        "package_assets": {
            "present": False,
            "note": "no audio, checkpoint, transcript or score bundle is written here.",
        },
        "substitution": {
            "performed": False,
            "synthetic_values_used_as_scores": False,
            "source_reported_values_relabelled_as_measured": False,
            "unrelated_checkpoint_or_runtime_used": False,
        },
        "conclusion": (
            "BLOCKED: the exact 265 processed outputs, raw corpus, transcripts "
            "and labels, NISQA checkpoint, DNSMOS-C source revision, approved "
            "runtime and any scored bundle are absent; no substitute is "
            "admitted."
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Runs, controls, adverse and missing results
# ---------------------------------------------------------------------------


def runs() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for condition in (
        "raw",
        "krisp_vi_2_5_default",
        "audio_enhance_basic_v1",
        "audio_enhance_voice_focus_v1",
    ):
        for scenario in SCENARIOS:
            rows.append({
                "run_id": condition + ":" + scenario,
                "condition": condition,
                "scenario": scenario,
                "status": "not_executed_artifact_and_rights_absent",
                "scores": {"dnsmos_c": None, "wer_percent": None},
                "measured_here": False,
                "is_human_rating": False,
                "qualifies": False,
            })
    return rows


CONTROL_STATUS: Dict[str, str] = {
    "scenario_balanced_aggregation": "synthetic_control_only",
    "invalid_item_admission": "synthetic_control_only",
    "identity_control": "blocked",
    "noisy_input_control": "blocked",
    "missing_artifact_control": "blocked",
    "wer_ensemble_control": "blocked",
}


def controls() -> Dict[str, Dict[str, Any]]:
    notes = {
        "scenario_balanced_aggregation": (
            "equal-weight mean on declared synthetic values only"
        ),
        "invalid_item_admission": (
            "invalid manifests, digests, revisions and metrics are rejected"
        ),
        "identity_control": (
            "an identity/noisy control requires the raw and processed audio, "
            "which are absent"
        ),
        "noisy_input_control": (
            "the raw baseline requires the raw corpus, which is absent"
        ),
        "missing_artifact_control": (
            "missing checkpoint and runtime fail closed; no score is produced"
        ),
        "wer_ensemble_control": (
            "the 11-configuration WER ensemble is explicitly unrun"
        ),
    }
    return {
        name: {
            "status": CONTROL_STATUS[name],
            "scores": {"dnsmos_c": None, "wer_percent": None},
            "note": notes[name],
            "measured_here": False,
            "qualifies": False,
        }
        for name in CONTROL_STATUS
    }


def _expect(code: str, call: Callable[[], Any]) -> str:
    try:
        call()
    except ValueError as error:
        observed = str(error)
    else:
        observed = "accepted"
    if observed != code:
        raise ReferenceError(
            "adverse_expectation_mismatch:" + code + "!=" + observed
        )
    return observed


def _cohort_template() -> Dict[str, Any]:
    items = []
    per_item = PROCESSED_TOTAL_BYTES // ITEM_COUNT
    remainder = PROCESSED_TOTAL_BYTES - per_item * ITEM_COUNT
    for index in range(ITEM_COUNT):
        items.append({
            "id": "item-%03d" % index,
            "scenario": SCENARIOS[index % 3],
            "sha256": ("%064x" % (index + 1)),
            "bytes": per_item + (1 if index < remainder else 0),
            "target_speech": index % 2 == 0,
            "transcript_sha256": ("%064x" % (index + 1001)),
            "rights_cleared": True,
        })
    return {
        "schema_id": "audio-sdk/krisp-vi-public-output-cohort/0.1",
        "dataset_repository": DATASET_REPOSITORY,
        "dataset_revision": DATASET_REVISION,
        "processed_repository": PROCESSED_REPOSITORY,
        "processed_revision": PROCESSED_REVISION,
        "subset": PROCESSED_SUBSET,
        "item_count": ITEM_COUNT,
        "total_bytes": PROCESSED_TOTAL_BYTES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "license": COHORT_LICENSE,
        "items": items,
    }


def _cohort_with(**changes: Any) -> Dict[str, Any]:
    value = _cohort_template()
    value.update(changes)
    return value


def _scorer_template() -> Dict[str, Any]:
    return {
        "schema_id": "audio-sdk/krisp-dnsmos-c-scorer-manifest/0.1",
        "metric": "dnsmos_c",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "checkpoint": {
            "name": DNSC_CHECKPOINT,
            "sha256": "ab" * 32,
            "bytes": 12345678,
            "license_id": "CC-BY-4.0",
        },
        "source_revision": "cd" * 20,
        "license": "MIT",
        "runtime": {
            "name": "torch",
            "version": "2.1.0",
            "license_id": "BSD-3-Clause",
        },
    }


def _scorer_with(**changes: Any) -> Dict[str, Any]:
    value = _scorer_template()
    value.update(changes)
    return value


def _wer_template() -> Dict[str, Any]:
    return {
        "config_count": WER_CONFIG_COUNT,
        "tool": WER_TOOL,
        "tool_version": WER_TOOL_VERSION,
        "text_normalization": WER_TEXT_NORMALIZATION,
        "raw_percent": DOCUMENTED_WER["raw_percent"]["all_265_files"],
        "processed_percent":
            DOCUMENTED_WER["krisp_vi_2_5_default_percent"]["all_265_files"],
        "library_percent": None,
        "scope": "corpus-level, 265 files, 11 configurations",
    }


def _wer_with(**changes: Any) -> Dict[str, Any]:
    value = _wer_template()
    value.update(changes)
    return value


def adverse_results() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def add(result_id: str, category: str, code: str,
            call: Callable[[], Any]) -> None:
        observed = _expect(code, call)
        rows.append({
            "result_id": result_id,
            "category": category,
            "expected_code": code,
            "observed_code": observed,
            "rejected": True,
            "state_unchanged": True,
            "qualifies": False,
        })

    add("json_duplicate_key", "strict_json", "duplicate_json_key:a",
        lambda: parse_strict_json_text('{"a":1,"a":2}'))
    add("json_nan", "strict_json", "non_json_constant:NaN",
        lambda: parse_strict_json_text('{"a":NaN}'))
    add("json_infinity", "strict_json", "non_json_constant:Infinity",
        lambda: parse_strict_json_text('{"a":Infinity}'))
    add("json_malformed", "strict_json", "invalid_json",
        lambda: parse_strict_json_text('{"a":'))
    add("json_top_level_list", "strict_json",
        "top_level_document_must_be_object",
        lambda: parse_strict_json_text("[1,2]"))
    add("json_empty", "strict_json", "empty_document",
        lambda: parse_strict_json_text("   "))
    add("json_bom", "strict_json", "utf8_bom_rejected",
        lambda: parse_strict_json_text("\ufeff{}"))

    add("cohort_missing_field", "cohort", "cohort_manifest_field_set_mismatch",
        lambda: validate_cohort_manifest(
            {key: value for key, value in _cohort_template().items()
             if key != "license"}))
    add("cohort_extra_field", "cohort", "cohort_manifest_field_set_mismatch",
        lambda: validate_cohort_manifest(_cohort_with(extra=True)))
    add("cohort_wrong_schema", "cohort", "cohort_manifest_schema_mismatch",
        lambda: validate_cohort_manifest(_cohort_with(schema_id="other")))
    add("cohort_short_revision", "cohort", "cohort_revision_must_be_40_hex",
        lambda: validate_cohort_manifest(
            _cohort_with(dataset_revision="626bac8")))
    add("cohort_uppercase_revision", "cohort",
        "cohort_revision_must_be_40_hex",
        lambda: validate_cohort_manifest(
            _cohort_with(processed_revision="A" * 40)))
    add("cohort_wrong_dataset_revision", "cohort",
        "cohort_dataset_revision_mismatch",
        lambda: validate_cohort_manifest(_cohort_with(dataset_revision="0" * 40)))
    add("cohort_wrong_processed_revision", "cohort",
        "cohort_processed_revision_mismatch",
        lambda: validate_cohort_manifest(
            _cohort_with(processed_revision="0" * 40)))
    add("cohort_wrong_subset", "cohort", "cohort_subset_mismatch",
        lambda: validate_cohort_manifest(_cohort_with(subset="hd")))
    add("cohort_wrong_item_count", "cohort", "cohort_item_count_must_be_265",
        lambda: validate_cohort_manifest(_cohort_with(item_count=264)))
    add("cohort_wrong_total", "cohort", "cohort_total_bytes_mismatch",
        lambda: validate_cohort_manifest(_cohort_with(total_bytes=1)))
    add("cohort_wrong_rate", "cohort", "cohort_sample_rate_must_be_16000",
        lambda: validate_cohort_manifest(_cohort_with(sample_rate_hz=32000)))
    add("cohort_wrong_channels", "cohort", "cohort_channels_must_be_1",
        lambda: validate_cohort_manifest(_cohort_with(channels=2)))
    add("cohort_unknown_license", "cohort",
        "cohort_license_must_be_cc_by_nc_4_0",
        lambda: validate_cohort_manifest(_cohort_with(license="NOASSERTION")))
    items = _cohort_template()["items"]
    add("cohort_items_count", "cohort", "cohort_items_count_mismatch",
        lambda: validate_cohort_manifest(_cohort_with(items=items[:10])))
    bad = _cohort_template()
    bad["items"][5] = dict(bad["items"][5], sha256="zz")
    add("cohort_bad_item_digest", "cohort",
        "cohort_item_sha256_must_be_64_lower_hex",
        lambda: validate_cohort_manifest(bad))
    bad = _cohort_template()
    bad["items"][7] = dict(bad["items"][7], bytes=0)
    add("cohort_zero_item_bytes", "cohort",
        "cohort_item_bytes_must_be_positive",
        lambda: validate_cohort_manifest(bad))
    bad = _cohort_template()
    bad["items"][9] = dict(bad["items"][9], rights_cleared=False)
    add("cohort_item_rights_missing", "cohort",
        "cohort_item_rights_not_cleared",
        lambda: validate_cohort_manifest(bad))
    bad = _cohort_template()
    bad["items"][11] = dict(bad["items"][11], scenario="studio")
    add("cohort_unknown_scenario", "cohort", "unsupported_scenario",
        lambda: validate_cohort_manifest(bad))
    bad = _cohort_template()
    bad["items"][13] = dict(bad["items"][13], id=bad["items"][12]["id"])
    add("cohort_duplicate_item", "cohort", "cohort_duplicate_item_id",
        lambda: validate_cohort_manifest(bad))
    bad = _cohort_template()
    bad["items"][15] = dict(bad["items"][15], bytes=bad["items"][15]["bytes"] + 1)
    add("cohort_item_sum_mismatch", "cohort",
        "cohort_item_bytes_do_not_sum_to_total",
        lambda: validate_cohort_manifest(bad))

    add("scorer_missing_field", "scorer",
        "scorer_manifest_field_set_mismatch",
        lambda: validate_scorer_manifest(
            {key: value for key, value in _scorer_template().items()
             if key != "runtime"}))
    add("scorer_wrong_schema", "scorer", "scorer_manifest_schema_mismatch",
        lambda: validate_scorer_manifest(_scorer_with(schema_id="other")))
    add("scorer_unknown_metric", "scorer", "scorer_manifest_unknown_metric",
        lambda: validate_scorer_manifest(_scorer_with(metric="dnsmos_p835")))
    add("scorer_wrong_rate", "scorer", "scorer_sample_rate_must_be_16000",
        lambda: validate_scorer_manifest(_scorer_with(sample_rate_hz=8000)))
    add("scorer_wrong_channels", "scorer", "scorer_channels_must_be_1",
        lambda: validate_scorer_manifest(_scorer_with(channels=2)))
    add("scorer_bad_revision", "scorer",
        "scorer_source_revision_must_be_40_hex",
        lambda: validate_scorer_manifest(_scorer_with(source_revision="x" * 40)))
    add("scorer_unknown_license", "scorer",
        "scorer_license_requires_identified_terms",
        lambda: validate_scorer_manifest(_scorer_with(license="unknown")))
    add("scorer_wrong_checkpoint_name", "scorer",
        "scorer_checkpoint_name_must_be_model_best_pt",
        lambda: validate_scorer_manifest(_scorer_with(
            checkpoint=dict(_scorer_template()["checkpoint"],
                            name="sig.onnx"))))
    add("scorer_bad_checkpoint_digest", "scorer",
        "scorer_checkpoint_sha256_must_be_64_lower_hex",
        lambda: validate_scorer_manifest(_scorer_with(
            checkpoint=dict(_scorer_template()["checkpoint"], sha256="AB"))))
    add("scorer_zero_checkpoint_bytes", "scorer",
        "scorer_checkpoint_bytes_must_be_positive",
        lambda: validate_scorer_manifest(_scorer_with(
            checkpoint=dict(_scorer_template()["checkpoint"], bytes=0))))
    add("scorer_unknown_checkpoint_license", "scorer",
        "scorer_checkpoint_license_requires_identified_terms",
        lambda: validate_scorer_manifest(_scorer_with(
            checkpoint=dict(_scorer_template()["checkpoint"],
                            license_id="NOASSERTION"))))
    add("scorer_missing_runtime_field", "scorer",
        "scorer_runtime_field_set_mismatch",
        lambda: validate_scorer_manifest(_scorer_with(
            runtime={"name": "torch", "license_id": "BSD-3-Clause"})))
    add("scorer_empty_runtime_version", "scorer",
        "scorer_runtime_version_requires_text",
        lambda: validate_scorer_manifest(_scorer_with(
            runtime={"name": "torch", "version": "", "license_id": "MIT"})))
    add("scorer_unknown_runtime_license", "scorer",
        "scorer_runtime_license_requires_identified_terms",
        lambda: validate_scorer_manifest(_scorer_with(
            runtime={"name": "torch", "version": "2.1.0",
                     "license_id": "unknown"})))

    add("metric_bool", "metric", "metric_requires_finite_number",
        lambda: validate_metric_value(True))
    add("metric_text", "metric", "metric_requires_finite_number",
        lambda: validate_metric_value("3.5"))
    add("metric_nan", "metric", "metric_requires_finite_number",
        lambda: validate_metric_value(float("nan")))
    add("metric_infinity", "metric", "metric_requires_finite_number",
        lambda: validate_metric_value(float("inf")))
    add("metric_below_scale", "metric", "metric_requires_finite_number",
        lambda: validate_metric_value(0.99))
    add("metric_above_scale", "metric", "metric_requires_finite_number",
        lambda: validate_metric_value(5.01))

    add("wer_wrong_config_count", "wer", "wer_config_count_must_be_11",
        lambda: validate_wer_record(_wer_with(config_count=10)))
    add("wer_wrong_tool", "wer", "wer_tool_must_be_jiwer",
        lambda: validate_wer_record(_wer_with(tool="whisper")))
    add("wer_wrong_tool_version", "wer", "wer_tool_version_must_be_4_0_0",
        lambda: validate_wer_record(_wer_with(tool_version="3.0.0")))
    add("wer_wrong_normalization", "wer",
        "wer_text_normalization_must_be_nemo_wfst",
        lambda: validate_wer_record(_wer_with(text_normalization="none")))
    add("wer_nan", "wer", "wer_raw_percent_requires_finite_percent",
        lambda: validate_wer_record(_wer_with(raw_percent=float("nan"))))
    add("wer_out_of_range", "wer",
        "wer_processed_percent_requires_finite_percent",
        lambda: validate_wer_record(_wer_with(processed_percent=101.0)))
    add("wer_library_measured", "wer", "wer_library_must_stay_unmeasured",
        lambda: validate_wer_record(_wer_with(library_percent=5.0)))

    add("aggregation_empty", "aggregation",
        "scenario_map_requires_exactly_three_declared",
        lambda: equal_weight_average({}))
    add("aggregation_two_scenarios", "aggregation",
        "scenario_map_requires_exactly_three_declared",
        lambda: equal_weight_average({"work": 3.0, "call_center": 3.5}))
    add("aggregation_extra_scenario", "aggregation",
        "scenario_map_requires_exactly_three_declared",
        lambda: equal_weight_average(
            {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0,
             "studio": 2.0}))
    add("aggregation_nan", "aggregation",
        "scenario_value_requires_finite_number",
        lambda: equal_weight_average(
            {"work": float("nan"), "call_center": 3.5, "phone_calls": 4.0}))
    add("aggregation_out_of_scale", "aggregation",
        "scenario_value_requires_finite_number",
        lambda: equal_weight_average(
            {"work": 3.0, "call_center": 3.5, "phone_calls": 9.0}))
    add("aggregation_bool", "aggregation",
        "scenario_value_requires_finite_number",
        lambda: equal_weight_average(
            {"work": True, "call_center": 3.5, "phone_calls": 4.0}))
    return rows


def _check_all_rejected(rows: Sequence[Dict[str, Any]]) -> bool:
    return all(
        row["rejected"] is True
        and row["state_unchanged"] is True
        and row["expected_code"] == row["observed_code"]
        and row["qualifies"] is False
        for row in rows
    )


def missing_results() -> List[Dict[str, Any]]:
    rows = [
        ("processed_265_outputs", "cohort",
         "265 processed vi_2_5_default WAVs and per-file digests"),
        ("raw_265_inputs", "cohort", "265 raw 32 kHz PCM16 recordings"),
        ("transcripts_and_scenario_metadata", "cohort",
         "transcripts and per-item scenario metadata"),
        ("target_speech_labels", "cohort", "primary/mix target-speech labels"),
        ("nisqa_checkpoint", "scorer",
         "NISQA model_best.pt with immutable revision and digest"),
        ("dnsmos_c_source_revision", "scorer",
         "pinned DNSMOS-C feature-extraction source revision"),
        ("approved_runtime", "runtime",
         "pinned torch/NISQA/librosa/numpy environment"),
        ("scenario_balanced_scores", "result",
         "per-item and per-scenario DNSMOS-C values"),
        ("wer_ensemble", "wer",
         "locally executed 11-configuration WER aggregate"),
        ("human_listening", "human",
         "authorized listening or subjective MOS assessment"),
        ("device_timing", "timing",
         "measured target-device timing, memory and availability"),
        ("derived_score_rights", "rights",
         "redistribution policy for derived scores from CC-BY-NC-4.0 media"),
        ("evidence_adapter_review", "review",
         "opt-in adapter intake and independent exact-head review"),
    ]
    return [
        {
            "result_id": result_id,
            "scope": scope,
            "requirement": requirement,
            "status": "blocked",
            "scores": None,
            "reason": "artifact, right or review is absent; nothing was substituted",
            "qualifies": False,
        }
        for result_id, scope, requirement in rows
    ]


def acceptance_profile() -> Dict[str, Any]:
    items = [
        {
            "id": "pin_scorer",
            "status": "blocked",
            "evidence": (
                "protocol described; checkpoint digest and DNSMOS-C source "
                "revision are not recorded and no runtime is approved"
            ),
            "qualifies": False,
        },
        {
            "id": "pin_corpus_and_cohort",
            "status": "blocked",
            "evidence": (
                "dataset and processed revisions are recorded, but the 265 "
                "outputs, raw recordings, transcripts and labels are not staged "
                "and item-level rights are absent"
            ),
            "qualifies": False,
        },
        {
            "id": "freeze_aggregation",
            "status": "synthetic_control_only",
            "evidence": (
                "equal-weight three-scenario mean and documented recomputation "
                "are arithmetic over declared/source-reported values only"
            ),
            "qualifies": False,
        },
        {
            "id": "retain_failed_items_and_controls",
            "status": "synthetic_control_only",
            "evidence": (
                "invalid/missing/nonfinite inputs are retained with exact codes; "
                "no real failed item is available"
            ),
            "qualifies": False,
        },
        {
            "id": "separate_evidence_kinds",
            "status": "proposal_only",
            "evidence": (
                "source-reported predicted scores, unrun WER, human listening "
                "and device timing are distinct empty or labelled fields"
            ),
            "qualifies": False,
        },
        {
            "id": "validate_one_valid_and_one_invalid",
            "status": "blocked",
            "evidence": (
                "invalid/missing cases are machine-checked, but no representative "
                "real valid result exists to validate end to end"
            ),
            "qualifies": False,
        },
    ]
    return {
        "profile": PROFILE,
        "source": "plan/swarm/VERIFICATION.md",
        "items": items,
        "all_qualify": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def observed_provenance() -> Dict[str, Any]:
    return {
        "reproduced_here": False,
        "documented_context": [
            {
                "id": "OP-1",
                "owner_task": TASK_ID,
                "source_pin": "research/cpp-library-krisp-benchmark-20261109.md",
                "scope": (
                    "265-item CC BY-NC 4.0 corpus; raw, Krisp VI 2.5 Default "
                    "and audio_enhance v1.1.0; DNSMOS-C via the NISQA checkpoint"
                ),
                "claims": {
                    "scenario_average": {
                        condition: values["scenario_average"]
                        for condition, values in DOCUMENTED_SCORES.items()
                    },
                },
                "labels": "source_reported_predicted_dnsmos_c",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "artifact_status": "corpus, outputs, checkpoint and runtime absent",
            },
            {
                "id": "OP-2",
                "owner_task": TASK_ID,
                "source_pin": "research/cpp-library-krisp-benchmark-20261109.md",
                "scope": "WER table",
                "claims": {
                    "config_count": WER_CONFIG_COUNT,
                    "raw_all_265_files": DOCUMENTED_WER["raw_percent"]["all_265_files"],
                    "krisp_all_265_files":
                        DOCUMENTED_WER["krisp_vi_2_5_default_percent"][
                            "all_265_files"],
                    "audio_enhance": None,
                },
                "labels": "source_reported_wer_not_run_here",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "artifact_status": "no local WER run or corpus exists",
            },
            {
                "id": "OP-3",
                "owner_task": "SDK-DNSMOS-P-835-AND-DNSMOS-C",
                "source_pin": "docs/task-evidence/dnsmos-p-835-and-dnsmos-c/report.json",
                "scope": (
                    "sibling blocker that preserves the same report's DNSMOS-C "
                    "protocol and records the absent NISQA checkpoint"
                ),
                "claims": {
                    "checkpoint_path": "runs/NISQA/model_best.pt",
                    "checkpoint_digest": None,
                    "source_revision": None,
                },
                "labels": "read_only_boundary_reference",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "artifact_status": "boundary reference only; not reused as evidence",
            },
        ],
        "qualifies": False,
    }


def separation_from_siblings() -> Dict[str, Any]:
    return {
        "reused_source_fixtures_metrics_or_results": False,
        "packages": [
            {
                "package": "docs/task-evidence/dnsmos-p-835-and-dnsmos-c",
                "boundary": (
                    "protects both P.835 and DNSMOS-C scorer identity; its "
                    "DNSMOS-C rows are pinned read-only and not rescored here"
                ),
                "reused": False,
            },
            {
                "package": "docs/task-evidence/ears-preservation-screen-and-scorer-harness",
                "boundary": (
                    "743-item EARS preservation screen and scorer harness; "
                    "different corpus, protocol and rights"
                ),
                "reused": False,
            },
        ],
        "note": (
            "Sibling README/report files are pinned read-only for boundary "
            "clarity only. No sibling fixture, source, corpus, metric or result "
            "is imported, pooled, rescored or reused."
        ),
        "qualifies": False,
    }


def _failure_controls() -> Dict[str, Any]:
    adverse = adverse_results()
    missing = missing_results()
    return {
        "all_explicit": True,
        "checks": {
            "every_rejection_observed": _check_all_rejected(adverse),
            "no_adverse_result_qualifies": all(
                row["qualifies"] is False for row in adverse
            ),
            "every_missing_result_blocked": all(
                row["status"] == "blocked" and row["scores"] is None
                and row["qualifies"] is False for row in missing
            ),
            "all_real_score_slots_null": all(
                value is None
                for row in runs()
                for value in row["scores"].values()
            ),
            "no_source_reported_value_relabelled": (
                documented_scores()["reproduced_here"] is False
                and documented_scores()["is_human_rating"] is False
                and wer_record()["measured_here"] is False
            ),
            "artifact_absence_explicit":
                artifact_assessment()["all_required_absent"] is True,
            "no_substitution_admitted": (
                artifact_assessment()["substitution"]["performed"] is False
            ),
            "public_surface_unchanged": all(
                value is False for value in PUBLIC_SURFACE.values()
            ),
        },
        "rejected_count": len(adverse),
        "blocked_count": len(missing),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Report and contract assembly
# ---------------------------------------------------------------------------


def build_report_core() -> Dict[str, Any]:
    return {
        SPDX_COPYRIGHT_KEY: "2026 Tsakanyan Hovhannes",
        SPDX_LICENSE_KEY: "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "qualification": dict(QUALIFICATION),
        "task_row": dict(TASK_ROW_IDENTITY),
        "mutable_provenance": dict(MUTABLE_PROVENANCE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "scope": dict(SCOPE),
        "public_surface": dict(PUBLIC_SURFACE),
        "cohort": cohort_record(),
        "scorer": scorer_record(),
        "wer": wer_record(),
        "documented_scores": documented_scores(),
        "documented_changes": documented_changes(),
        "documented_published_context": documented_published_context(),
        "aggregation_reference": aggregation_reference(),
        "geometry_reference": {
            "segment_cases": geometry_cases(),
            "protocol": DNSC_PROTOCOL,
            "bits_reproduced": False,
            "scored": False,
            "qualifies": False,
        },
        "fixtures": fixture_payload(),
        "absence_probes": absence_probes(),
        "artifact_assessment": artifact_assessment(),
        "runs": runs(),
        "controls": controls(),
        "adverse_results": adverse_results(),
        "missing_results": missing_results(),
        "failure_controls": _failure_controls(),
        "acceptance_profile": acceptance_profile(),
        "observed_provenance": observed_provenance(),
        "separation_from_siblings": separation_from_siblings(),
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "non_claims": list(NON_CLAIMS),
        "reproduction": list(REPRODUCTION),
    }


def build_report() -> Dict[str, Any]:
    return build_report_core()


def render_report() -> Tuple[bytes, str, str]:
    cores = [canonical_bytes(build_report_core()) for _ in range(3)]
    if len(set(cores)) != 1:
        raise ReferenceError("non_deterministic_report_core")
    core = build_report_core()
    core_digest = sha256_bytes(canonical_bytes(core))
    report = dict(core)
    report["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": [core_digest, core_digest, core_digest],
        "process": "three in-process builds, exact canonical bytes",
    }
    text, digest = canonical_report(report)
    return (text + "\n").encode("utf-8"), digest, core_digest


def cohort_contract_summary() -> Dict[str, Any]:
    return {
        "dataset_repository": DATASET_REPOSITORY,
        "dataset_revision": DATASET_REVISION,
        "processed_repository": PROCESSED_REPOSITORY,
        "processed_revision": PROCESSED_REVISION,
        "processed_subset": PROCESSED_SUBSET,
        "item_count": ITEM_COUNT,
        "processed_total_bytes": PROCESSED_TOTAL_BYTES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "license": COHORT_LICENSE,
        "scenarios": list(SCENARIOS),
        "permitted_here": False,
        "present": False,
        "qualifies": False,
    }


def scorer_contract_summary() -> Dict[str, Any]:
    return {
        "id": "dnsmos_c",
        "output": DNSC_OUTPUT,
        "sample_rate_hz": DNSC_SAMPLE_RATE_HZ,
        "segment_kinds": list(DNSC_SEGMENT_KINDS),
        "min_segment_ms": DNSC_MIN_SEGMENT_MS,
        "window_ms": DNSC_WINDOW_MS,
        "hop_ms": DNSC_HOP_MS,
        "checkpoint": "runs/NISQA/" + DNSC_CHECKPOINT,
        "checkpoint_sha256": None,
        "source_revision": None,
        "source_url": DNSC_SOURCE,
        "runtime_pinned": False,
        "score_status": "unavailable_checkpoint_source_runtime_and_cohort_absent",
        "scores_reproduced": False,
        "scores_are_human_ratings": False,
        "qualifies": False,
    }


def contract_payload(artifact_pins: Dict[str, str]) -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "qualification": dict(QUALIFICATION),
        "task_row": dict(TASK_ROW_IDENTITY),
        "mutable_provenance": dict(MUTABLE_PROVENANCE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "scope": dict(SCOPE),
        "public_surface": dict(PUBLIC_SURFACE),
        "cohort_contract_summary": cohort_contract_summary(),
        "scorer_contract_summary": scorer_contract_summary(),
        "required_artifacts": [dict(item) for item in REQUIRED_ARTIFACTS],
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "artifact_pins": dict(sorted(artifact_pins.items())),
        "reproduction": list(REPRODUCTION),
        "non_claims": list(NON_CLAIMS),
    }
