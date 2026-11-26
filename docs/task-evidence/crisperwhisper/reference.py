# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-CRISPERWHISPER.

Standard-library only and deterministic. This module contains no CrisperWhisper
source checkout, model weight, tokenizer, inference path, audio signal,
verbatim transcript, filler span, runtime import or model result. It records
the exact research inputs, proves that the candidate source/weights/runtime are
absent from fixed probe paths, defines a fail-closed admission boundary for a
future verbatim annotation run, implements the exact verbatim-token and
boundary arithmetic that boundary would use, and builds the canonical
contract/report.

The pinned candidate note records CrisperWhisper as a verbatim/filler
transcription lead: code MIT, model weights CC-BY-NC-4.0, `[um]`, `[uh]` and
`[laughter]` tags and ~30-41 ms word boundaries. It also says the non-commercial
weights cannot ship in a commercial product without a separate licence and
must be used only as an offline oracle. No weight, runtime or result is present
or produced here. Every result remains blocked.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-CRISPERWHISPER"
COMPONENT_ID = "crisperwhisper"
TASK_TITLE = "CrisperWhisper"
CONTRACT_ID = "audio-sdk/crisperwhisper-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/crisperwhisper-verbatim-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "research-control"
BASE_COMMIT = "c07f8540b4c32d2add5c6e0c1baddf625d9d9312"
BRANCH = "swarm/SDK-CRISPERWHISPER"
WRITE_SCOPE = "docs/task-evidence/crisperwhisper/ only"
TASK_PREFIX = "docs/task-evidence/crisperwhisper/"
DISPOSITION = (
    "CrisperWhisper non-commercial-weights verifier blocker; no source, "
    "weight, runtime, adapter, annotation or result.")

CRISPER_REPOSITORY = "https://github.com/nyrahealth/CrisperWhisper"
CRISPER_CODE_LICENSE = "MIT"
CRISPER_WEIGHTS_LICENSE = "CC-BY-NC-4.0"
CRISPER_WEIGHTS_HOST = "Hugging Face"
CRISPER_TAGS = ("[um]", "[uh]", "[laughter]")
CRISPER_BOUNDARY_RANGE_MS = "30-41"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
COHORT_ITEM_COUNT = 1
MAX_AUDIO_SAMPLES = 60 * SAMPLE_RATE_HZ
MAX_TIMING_MS = 60000.0

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "cpp-library").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable read-only inputs. `source:` rows are workspace-relative; boundary
# and sibling rows are SDK-worktree relative. The mutable shared board is
# deliberately excluded from the pin set; only its stable row identity gates.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/asr-word-timestamps/README.md":
        "30915db04b0229d03729b8dd03bac8e0eb88ad285781069de1607ff2c4559de4",
    "docs/task-evidence/asr-word-timestamps/contract.json":
        "65361e29cf8a04fd64ad4a25b4fd3094fffaf2f56ad911ea6076e7fef592822a",
    "docs/task-evidence/asr-word-timestamps/report.json":
        "318bec24c9d388fa122e80974cfc6772b144f7f651e87d5e88ac0677975d437e",
    "docs/task-evidence/whisper-tiny-en-mfa/README.md":
        "7c24422f782bf934d22e2a752e2be2ead2d184cfd8728452c7f7a5dd68f25c7f",
    "docs/task-evidence/whisper-tiny-en-mfa/contract.json":
        "fddc819bdcbb34a4d47f605efa8c0632573eaa2b77d0681d2a82f5c58e98687e",
    "docs/task-evidence/whisper-tiny-en-mfa/report.json":
        "6b9cc69ea2be5cd5cad9509021b7b5e7fb972a4c32c62721f07be995b582710c",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")

# Fixed probes only; no recursive workspace walk. No historical CrisperWhisper
# run path is recorded, so these are the exact candidate intake/cache paths a
# future run would have to fill, plus the plausible recipe file names.
WORKSPACE_ABSENCE_PROBES = (
    "data/models/crisperwhisper",
    "data/models/crisperwhisper-hf",
    "data/runs/crisperwhisper-verbatim-20261126",
    "cpp-library/pipeline-validation/playback-speed/models/crisperwhisper",
    "research/tsm-followup-20261101/agent-text/run_crisperwhisper.py",
    "research/tsm-followup-20261101/agent-text/crisperwhisper_report.md",
)
EXTERNAL_ABSENCE_PROBES = (
    "/private/tmp/crisperwhisper",
    "/private/tmp/crisperwhisper-env",
    "/private/tmp/crisperwhisper-venv",
    "/private/tmp/crisperwhisper-model",
    "~/.cache/huggingface/hub/models--nyrahealth--CrisperWhisper",
    "~/.cache/huggingface/hub/models--nyrahealth--crisperwhisper",
)

# Required artifact IDs. ART-01 is the only present/verified artifact: the
# pinned candidate note and inventory row. It is provenance only and never a
# source, weight, runtime, reproduction or qualification.
REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "pinned_candidate_note",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The exact pinned candidate note, inventory row, plan and "
            "verification profile that record the CrisperWhisper licence and "
            "verbatim/filler claim."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "crisperwhisper_source_and_code_license",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact nyrahealth/CrisperWhisper source revision (40-hex "
            "commit), package/archive digest and the complete MIT license and "
            "notice bundle."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "crisperwhisper_weights_and_model_card",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact CrisperWhisper weight/model ID, revision, byte count and "
            "verified SHA-256, the model card and the complete CC-BY-NC-4.0 "
            "terms, plus a written commercial output-use decision."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_offline_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A locked offline Python/torch/transformers (or equivalent) "
            "runtime with exact wheel hashes, install/import digests, one "
            "thread per pool, deterministic settings and no network."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_audio_and_independent_verbatim_reference",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Rights-cleared/consented 16 kHz mono audio and an independent "
            "adjudicated verbatim reference with fillers/laughter from at "
            "least two annotators, plus reviewed dataset and output-use terms."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "reproduced_verbatim_and_boundary_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A fresh offline CrisperWhisper run with frozen lexical, filler, "
            "laughter and boundary scoring, finite-output checks, matched-token "
            "accounting and uniform-timing/filler-stripped controls."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "provider_intake",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A separate versioned opt-in SDK developer/evidence adapter with "
            "OFF default, empty settings, no registry/default/build change and "
            "independent exact-head review after every other gate clears."),
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No CrisperWhisper source checkout exists at an exact 40-hex "
            "revision, and no MIT license/notice bundle is staged. The pinned "
            "note only records the GitHub URL and 'code MIT'; it records no "
            "source revision, package archive, digest or notice text. No "
            "source was downloaded, cloned or reconstructed."),
        "required_action": (
            "Supply the exact nyrahealth/CrisperWhisper source revision, "
            "package/archive digest and the complete MIT license and notice "
            "bundle with an independent terms review."),
        "linked_gates": ["RG-01"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No CrisperWhisper weight is present or identified exactly. The "
            "pinned note records only 'weights CC-BY-NC-4.0 on Hugging Face' "
            "and no model ID, revision, byte count, digest or model card. The "
            "non-commercial CC-BY-NC-4.0 weights cannot be a commercial SDK "
            "runtime without a separate, reviewed licence. No weight was "
            "downloaded or reconstructed."),
        "required_action": (
            "Supply the exact weight model ID, revision, byte count and "
            "SHA-256, the model card and complete CC-BY-NC-4.0 terms, and a "
            "written commercial/output-use decision (or a separate negotiated "
            "commercial licence) reviewed independently."),
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No pinned offline runtime is present. The fixed candidate "
            "environment paths are absent and no lockfile, wheel digest, "
            "import digest, deterministic thread policy or offline-load trace "
            "exists. No CrisperWhisper, torch or transformers module was "
            "imported and no model was loaded."),
        "required_action": (
            "Supply a locked offline runtime with exact package/wheel hashes, "
            "install and import digests, single-thread deterministic settings "
            "and a clean-room offline load trace."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared audio or independent verbatim reference exists. "
            "There is no audio, transcript, filler/laughter span set, second "
            "annotator, adjudication or agreement statistic, and no reviewed "
            "dataset or output-use terms. CrisperWhisper output cannot be its "
            "own gold reference."),
        "required_action": (
            "Freeze rights-cleared or consented 16 kHz mono audio and an "
            "independent human verbatim reference with fillers/laughter from "
            "at least two annotators, adjudication, agreement and reviewed "
            "dataset/output-use terms."),
        "linked_gates": ["RG-04"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No CrisperWhisper result was reproduced. The pinned note's "
            "`[um]`, `[uh]`, `[laughter]` tags and ~30-41 ms word boundaries "
            "are source-reported claims, not a measured result. There is no "
            "local lexical WER, filler/laughter recall, boundary error, "
            "finite-output scan or matched-token accounting."),
        "required_action": (
            "Run CrisperWhisper offline on the qualified cohort with frozen "
            "lexical, filler, laughter and boundary scorers, exact token "
            "accounting, finite-output checks and uniform-timing plus "
            "filler-stripped baselines."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider, tool, adapter or intake exists, and the task row's "
            "Rate profile is a mismatch for a verbatim annotation tool. There "
            "is no target-device timing, no preferred-speed policy and no "
            "separate commercial-licence decision. No registry, default, "
            "public ABI, shared build or CI change was made."),
        "required_action": (
            "After model/data/runtime/quality gates clear, measure the exact "
            "target-device paced workload, complete or explicitly waive the "
            "Rate profile with independent review, and open a separate "
            "OFF-by-default versioned intake with exact-head review."),
        "linked_gates": ["RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_code_license_provenance",
        "status": "blocked",
        "statement": (
            "Only the candidate note and inventory row are pinned. The exact "
            "nyrahealth/CrisperWhisper source revision, package archive and "
            "complete MIT license/notice bundle are not staged or reviewed."),
        "reopen_condition": (
            "Pin the exact CrisperWhisper source revision and package digest, "
            "stage the complete MIT license/notice set, and record an "
            "independent terms review."),
    },
    {
        "id": "RG-02",
        "title": "weights_model_card_and_noncommercial_terms",
        "status": "blocked",
        "statement": (
            "No weight model ID, revision, byte count or digest is recorded and "
            "no weight is staged. The weights are CC-BY-NC-4.0, so a separate "
            "reviewed licence is mandatory before any commercial use."),
        "reopen_condition": (
            "Supply the exact weight model ID/revision/byte count/SHA-256, the "
            "model card and complete CC-BY-NC-4.0 terms, and a written "
            "commercial/output-use decision or negotiated licence."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "statement": (
            "No CrisperWhisper runtime is present. There is no lockfile, wheel "
            "digest, import digest, deterministic thread policy or "
            "offline-load trace."),
        "reopen_condition": (
            "Provide a locked offline runtime with exact package hashes, "
            "install/import digests, deterministic settings and a clean-room "
            "offline load."),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_audio_and_independent_verbatim_reference",
        "status": "blocked",
        "statement": (
            "No audio, verbatim transcript, filler/laughter span set, second "
            "annotator or reviewed dataset/output-use term exists. Model output "
            "is not independent gold."),
        "reopen_condition": (
            "Stage rights-cleared audio and a two-annotator adjudicated "
            "verbatim reference with agreement, plus reviewed dataset and "
            "output-use terms."),
    },
    {
        "id": "RG-05",
        "title": "verbatim_filler_and_boundary_accuracy_with_controls",
        "status": "blocked",
        "statement": (
            "No lexical WER, filler/laughter recall, boundary MAE/median/"
            "within-50 ms, matched-token accounting, finite-output scan or "
            "baseline was reproduced."),
        "reopen_condition": (
            "Reproduce lexical, filler, laughter and boundary scores on the "
            "qualified cohort with frozen scorers, exact token accounting, "
            "finite checks and matched controls."),
    },
    {
        "id": "RG-06",
        "title": "rate_profile_condition_coverage",
        "status": "blocked",
        "statement": (
            "The Rate profile is not exercised: no source/output mapping, "
            "duration, pitch/transient, buffering, rate-change, unfamiliar "
            "speech/music/silence, rebuffer/drift, final-partial-window or "
            "timestamp-tied pause/filler preservation evidence exists."),
        "reopen_condition": (
            "Score the exact Rate-profile cases with separate source references "
            "and a timestamp-tied pause/filler policy, or record a reviewed "
            "waiver because this is not a renderer."),
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_resources_and_deadlines",
        "status": "blocked",
        "statement": (
            "No target-device load/inference latency, RTF, CPU/memory/energy, "
            "queue or deadline measurement exists."),
        "reopen_condition": (
            "Measure the exact installed candidate under paced workload with "
            "p50/p95/p99 latency, resource, thermal/energy and fill/flush "
            "behavior on the intended device."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "statement": (
            "No provider/tool intake or public-surface decision exists. The "
            "installed v0 geometry, registry, default and shared build remain "
            "untouched, and no commercial licence decision exists."),
        "reopen_condition": (
            "Open a separate versioned, OFF-by-default opt-in intake with an "
            "exact descriptor/config, clean-install proof and independent "
            "exact-head review after all prior gates clear."),
    },
)

RATE_PROFILE_ROWS = (
    {
        "id": "RATE-01",
        "requirement": "Measure source/output mapping and duration.",
        "status": "blocked",
        "evidence": (
            "CrisperWhisper emits transcript, tags and word boundaries, not "
            "rendered audio; no mapping or duration result exists."),
    },
    {
        "id": "RATE-02",
        "requirement": "Measure pitch and transient audibility.",
        "status": "blocked",
        "evidence": "No rendered waveform, F0/transient metric or listening result exists.",
    },
    {
        "id": "RATE-03",
        "requirement": "Measure playback buffering.",
        "status": "blocked",
        "evidence": "No playback chain, queue, fill/flush or buffering measurement exists.",
    },
    {
        "id": "RATE-04",
        "requirement": "Include 1x and rate changes.",
        "status": "blocked",
        "evidence": "No 1x or rate-change comparison exists; the tool is not a stretcher.",
    },
    {
        "id": "RATE-05",
        "requirement": "Include unfamiliar speech, music and silence.",
        "status": "blocked",
        "evidence": (
            "No cohort exists at all; no unfamiliar speech, music, silence or "
            "language coverage was tested."),
    },
    {
        "id": "RATE-06",
        "requirement": "Include rebuffer, drift and the final partial window.",
        "status": "blocked",
        "evidence": "No stream, rebuffer, clock-drift or partial-window behavior was measured.",
    },
    {
        "id": "RATE-07",
        "requirement": (
            "Keep pause or filler decisions tied to source timestamps and "
            "measure speech preservation."),
        "status": "blocked",
        "evidence": (
            "Verbatim filler/laughter tags could inform a pause/filler "
            "controller, but no controller, source-timestamp policy or "
            "preservation measurement exists."),
    },
    {
        "id": "RATE-08",
        "requirement": "Map output to a reviewed preferred-speed policy.",
        "status": "blocked",
        "evidence": (
            "No preference/acceptability labels or rate-to-speed policy exists; "
            "tag recall and boundary error are not a preferred speed factor."),
    },
)

QUALITY_ROWS = (
    {
        "id": "QUAL-01",
        "outcome": "lexical_word_error_rate",
        "status": "blocked",
        "value": None,
        "evidence": "No CrisperWhisper transcript exists and no lexical WER was reproduced.",
    },
    {
        "id": "QUAL-02",
        "outcome": "filler_tag_recall_and_precision",
        "status": "blocked",
        "value": None,
        "evidence": (
            "The `[um]`/`[uh]` tag claim is source-reported; no labelled "
            "filler spans exist to score recall or precision."),
    },
    {
        "id": "QUAL-03",
        "outcome": "laughter_tag_recall_and_false_alarms",
        "status": "blocked",
        "value": None,
        "evidence": "The `[laughter]` claim is source-reported; no labelled laughter spans exist.",
    },
    {
        "id": "QUAL-04",
        "outcome": "word_boundary_error_and_within_50ms",
        "status": "blocked",
        "value": None,
        "evidence": (
            "The ~30-41 ms boundary claim is source-reported; no local "
            "boundary score or matched-token accounting exists."),
    },
    {
        "id": "QUAL-05",
        "outcome": "uniform_timing_and_filler_stripped_baselines",
        "status": "blocked",
        "value": None,
        "evidence": "Only a synthetic token/boundary arithmetic control exists; no real baseline exists.",
    },
)

TIMING_ROWS = (
    {
        "id": "TIME-01",
        "metric": "model_load_and_inference_latency",
        "status": "blocked",
        "value": None,
        "evidence": "No model load, inference p50/p95 or RTF was measured.",
    },
    {
        "id": "TIME-02",
        "metric": "annotation_and_scoring_wall_time",
        "status": "blocked",
        "value": None,
        "evidence": "No local annotation or scoring wall time was measured.",
    },
    {
        "id": "TIME-03",
        "metric": "device_deadline_and_callback",
        "status": "blocked",
        "value": None,
        "evidence": "No device, pacing, callback deadline or availability measurement exists.",
    },
    {
        "id": "TIME-04",
        "metric": "cpu_memory_energy",
        "status": "blocked",
        "value": None,
        "evidence": "No resource, thermal or energy measurement exists.",
    },
)

NON_CLAIMS = (
    "No CrisperWhisper source checkout, weight, tokenizer or model card is present in this package.",
    "No CrisperWhisper, torch, transformers or equivalent runtime is imported or executed.",
    "No audio, transcript, filler span, laughter span or annotation is read or scored.",
    "No lexical WER, filler/laughter recall, boundary error, finite-output, baseline or timing result is reproduced.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "Non-commercial CC-BY-NC-4.0 weights are not a runtime or rights basis.",
    "Source-reported ~30-41 ms boundaries are not independent timing gold or a preferred speed factor.",
)

REQUIRED_RESULTS = (
    "Exact nyrahealth/CrisperWhisper source revision and complete MIT notice bundle.",
    "Exact weight model ID, revision, byte count, SHA-256, model card and CC-BY-NC-4.0 terms.",
    "A written commercial/output-use decision or negotiated commercial licence.",
    "A locked offline runtime with install/import digests.",
    "Rights-cleared audio and a two-annotator adjudicated verbatim reference with filler/laughter spans.",
    "Reproduced lexical WER, filler/laughter recall and boundary error with matched-token accounting.",
    "Uniform-timing and filler-stripped controls plus finite/adverse/missing-input rejection.",
    "Rate-profile evidence or a reviewed waiver plus target-device timing.",
    "Separate OFF-by-default provider/tool intake and independent exact-head review.",
)

# Admission is a strict, task-local schema check only. It never reads audio,
# loads weights or invokes CrisperWhisper.
MANIFEST_FIELDS = (
    "schema_id", "cohort_id", "crisperwhisper", "runtime", "audio",
    "reference", "controls", "outcomes", "rights")
CRISPERWHISPER_FIELDS = (
    "repository", "code_revision", "code_license_id", "weights_source",
    "weights_model_id", "weights_revision", "weights_sha256",
    "weights_byte_count", "weights_license_id", "commercial_use_granted",
    "license_review_reference")
RUNTIME_FIELDS = (
    "python", "torch", "transformers", "device", "intra_op_threads",
    "interop_op_threads", "deterministic_algorithms", "offline")
AUDIO_FIELDS = (
    "id", "path", "sha256", "language", "speaker_group", "sample_rate_hz",
    "channels", "samples")
REFERENCE_FIELDS = (
    "source", "sha256", "annotator_count", "token_count", "has_filler_spans")
CONTROL_FIELDS = ("id", "kind")
CONTROL_KINDS = (
    "independent_second_annotator",
    "uniform_word_timing_baseline",
    "filler_stripped_transcript_baseline",
)
OUTCOME_FIELDS = (
    "lexical_wer", "filler_recall", "laughter_recall", "boundary_mae_ms",
    "boundary_median_abs_error_ms", "boundary_within_50ms_fraction",
    "matched_tokens", "reference_tokens", "nonfinite_count", "sample_count")
RIGHTS_FIELDS = (
    "dataset_terms_reference", "weights_terms_reference",
    "output_use_reference", "commercial_use_decision_reference",
    "review_reference", "claims_qualified")

HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
SLUG = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
MODEL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,47}/[A-Za-z0-9][A-Za-z0-9._-]{0,47}")
ABSOLUTE = re.compile(r"/[^\x00]+")
ASCII_TEXT = re.compile(r"[\x20-\x7e]{1,96}")
KINDS = ("filler", "laughter", "lexical")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text(document: dict) -> str:
    text = json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text + "\n"


def canonical_bytes(document: dict) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: dict) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def _no_floats(value: Any, path: str = "document") -> None:
    if isinstance(value, float):
        raise ValueError("float:" + path)
    if isinstance(value, dict):
        for key, item in value.items():
            _no_floats(item, path + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, path + f"[{index}]")


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json:" + token)


def read_strict_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    document = json.loads(text, object_pairs_hook=_strict_pairs,
                          parse_constant=_reject_constant)
    if not isinstance(document, dict):
        raise ValueError("json_not_object")
    return document


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative, expected in sorted(pins.items()):
        actual = sha256_file(root / relative)
        if actual != expected:
            raise ValueError("pin_mismatch:" + relative)
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": True,
        }
    return rows


def _board_document() -> dict:
    return read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)


def board_row_projection(board_path: Path, task: str = TASK) -> dict:
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in tasks if isinstance(row, dict)
               and row.get("id") == task]
    if len(matches) != 1:
        raise ValueError("board_row_count:" + task)
    row = matches[0]
    return {field: copy.deepcopy(row.get(field)) for field in BOARD_ROW_FIELDS}


def board_row_digest(row: dict) -> str:
    return hashlib.sha256(canonical_bytes(row)).hexdigest()


def linked_rows() -> list[dict]:
    document = _board_document()
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    index = {row.get("id"): row for row in tasks if isinstance(row, dict)}
    rows = []
    for task_id in LINKED_ROW_IDS:
        row = index.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        rows.append({field: copy.deepcopy(row.get(field))
                     for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(rows if rows is not None
                                          else linked_rows())).hexdigest()


def _present(path: Path) -> bool:
    return path.exists()


def _expanded(path: str) -> Path:
    return Path(os.path.expanduser(path))


def absence_probes() -> list[dict]:
    rows = []
    for relative in WORKSPACE_ABSENCE_PROBES:
        rows.append({
            "scope": "workspace",
            "path": relative,
            "present": _present(AUDIO_ROOT / relative),
            "kind": "candidate_intake_or_recipe_path",
        })
    return rows


def external_absence_probes() -> list[dict]:
    rows = []
    for path in EXTERNAL_ABSENCE_PROBES:
        rows.append({
            "scope": "external",
            "path": path,
            "present": _present(_expanded(path)),
            "kind": "candidate_weight_runtime_or_cache_path",
        })
    return rows


def absence_summary(rows: list[dict], external_rows: list[dict]) -> dict:
    all_rows = rows + external_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(rows),
        "external_probe_count": len(external_rows),
        "present_count": sum(1 for row in all_rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


def source_presence() -> dict:
    note = "cpp-library/pipeline-validation/playback-speed-candidates.md"
    inventory = "audio-benchmark-platform/plan/INVENTORY.json"
    rows = []
    for relative, role in ((note, "candidate_licence_and_claim_note"),
                           (inventory, "crisperwhisper_inventory_row")):
        path = AUDIO_ROOT / relative
        rows.append({
            "path": relative,
            "sha256": SOURCE_PINS[relative],
            "byte_count": path.stat().st_size,
            "role": role,
        })
    source = AUDIO_ROOT / "data/models/crisperwhisper"
    weights = AUDIO_ROOT / "data/models/crisperwhisper-hf"
    runtime = Path("/private/tmp/crisperwhisper-env")
    run_tree = AUDIO_ROOT / "data/runs/crisperwhisper-verbatim-20261126"
    return {
        "candidate_note_and_inventory_present": True,
        "source_repository_present": source.exists(),
        "weights_present": weights.exists(),
        "weights_model_id_recorded": False,
        "weights_digest_recorded": False,
        "runtime_present": runtime.exists(),
        "run_artifacts_present": run_tree.exists(),
        "rights_cleared_audio_present": False,
        "exact_source_weights_runtime_conjunction_present": (
            source.exists() and weights.exists() and runtime.exists()),
        "weights_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "model_executed": False,
        "provenance_rows": rows,
    }


def _require_substring(text: str, needle: str, code: str) -> None:
    if needle not in text:
        raise ValueError(code)


def recipe_provenance() -> dict:
    """Verify the pinned note/inventory contain the exact recorded claims."""
    note_path = AUDIO_ROOT / (
        "cpp-library/pipeline-validation/playback-speed-candidates.md")
    inventory_path = AUDIO_ROOT / "audio-benchmark-platform/plan/INVENTORY.json"
    note = note_path.read_text(encoding="utf-8")
    inventory = inventory_path.read_text(encoding="utf-8")
    checks = (
        (note,
         "| Verbatim/filler timestamps | **CrisperWhisper** | Code MIT, "
         "**weights CC-BY-NC-4.0** | Emits `[um]`, `[uh]`, `[laughter]` and "
         "~30\u201341 ms word boundaries | **Non-commercial weights**; "
         "benchmark/oracle only |",
         "note_candidate_row"),
        (note,
         "so it cannot ship in a commercial product without a separate "
         "licence. Use it as an offline oracle to label evaluation data, not "
         "as a runtime dependency.",
         "note_offline_oracle_boundary"),
        (note, "Do **not** start with CrisperWhisper (non-commercial weights)",
         "note_do_not_start"),
        (note,
         "- CrisperWhisper \u2014 <https://github.com/nyrahealth/CrisperWhisper> "
         "(code MIT; weights CC-BY-NC-4.0 on Hugging Face)",
         "note_source_and_weights_host"),
        (note,
         "| CC BY-NC-4.0 | **No** | Non-commercial only | CrisperWhisper "
         "**model weights** (code is MIT) |",
         "note_licence_table"),
        (inventory, '"id": "crisperwhisper"', "inventory_row"),
        (inventory, '"verification_profile": "rate"', "inventory_profile"),
        (inventory, "Treat reported noncommercial weights as an offline "
                    "annotation lead subject to terms.",
         "inventory_plan_note"),
    )
    for text, needle, code in checks:
        _require_substring(text, needle, code)
    return {
        "note_sha256": SOURCE_PINS[
            "cpp-library/pipeline-validation/playback-speed-candidates.md"],
        "inventory_sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/INVENTORY.json"],
        "checks_present": len(checks),
        "checks_required": len(checks),
        "repository": CRISPER_REPOSITORY,
        "code_license_recorded": CRISPER_CODE_LICENSE,
        "weights_license_recorded": CRISPER_WEIGHTS_LICENSE,
        "weights_host_recorded": CRISPER_WEIGHTS_HOST,
        "verbatim_tags_recorded": list(CRISPER_TAGS),
        "word_boundary_range_ms_recorded": CRISPER_BOUNDARY_RANGE_MS,
        "recorded_only": True,
        "saved_run_artifacts": False,
        "executed_here": False,
    }


def documented_claims() -> dict:
    """Quote the pinned note; verify every claim is present, never rerun it."""
    note_path = AUDIO_ROOT / (
        "cpp-library/pipeline-validation/playback-speed-candidates.md")
    note = note_path.read_text(encoding="utf-8")
    checks = (
        "CrisperWhisper",
        "Code MIT, **weights CC-BY-NC-4.0**",
        "`[um]`, `[uh]`, `[laughter]`",
        "~30\u201341 ms word boundaries",
        "**Non-commercial weights**; benchmark/oracle only",
        "cannot ship in a commercial product without a separate licence",
        "Use it as an offline oracle to label evaluation data, not as a "
        "runtime dependency",
    )
    for needle in checks:
        _require_substring(note, needle, "documented_claim_missing")
    return {
        "source_path": "cpp-library/pipeline-validation/"
                       "playback-speed-candidates.md",
        "source_sha256": SOURCE_PINS[
            "cpp-library/pipeline-validation/playback-speed-candidates.md"],
        "repository": CRISPER_REPOSITORY,
        "code_license_recorded": CRISPER_CODE_LICENSE,
        "weights_license_recorded": CRISPER_WEIGHTS_LICENSE,
        "weights_host_recorded": CRISPER_WEIGHTS_HOST,
        "verbatim_tags_recorded": list(CRISPER_TAGS),
        "word_boundary_range_ms_recorded": CRISPER_BOUNDARY_RANGE_MS,
        "commercial_use_permitted": False,
        "intended_use_recorded": "offline_oracle_annotation_benchmark_only",
        "recommendation_recorded": "do_not_start_component_with_it",
        "source_revision_recorded": False,
        "weights_model_id_recorded": False,
        "weights_digest_recorded": False,
        "runtime_version_recorded": False,
        "measured_result_recorded": False,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
    }


def exact_models() -> dict:
    return {
        "crisperwhisper": {
            "repository": CRISPER_REPOSITORY,
            "code_license_recorded": CRISPER_CODE_LICENSE,
            "weights_license_recorded": CRISPER_WEIGHTS_LICENSE,
            "weights_host_recorded": CRISPER_WEIGHTS_HOST,
            "verbatim_tags_recorded": list(CRISPER_TAGS),
            "word_boundary_range_ms_recorded": CRISPER_BOUNDARY_RANGE_MS,
            "source_revision": None,
            "weights_model_id": None,
            "weights_revision": None,
            "weights_sha256": None,
            "weights_byte_count": None,
            "source_present": False,
            "weights_present": False,
            "digest_verified": False,
            "model_card_present": False,
            "license_bundle_reviewed": False,
            "commercial_use_granted": False,
            "downloaded_or_reconstructed": False,
        },
        "reference_transcript": {
            "present": False,
            "source": None,
            "sha256": None,
            "annotator_count": None,
            "filler_span_count": None,
            "laughter_span_count": None,
            "terms_reviewed": False,
        },
        "runtime": {
            "present": False,
            "python_version": None,
            "torch_version": None,
            "transformers_version": None,
            "lockfile_sha256": None,
            "offline_load_verified": False,
        },
    }


def historical_recipe() -> dict:
    return {
        "candidate_note": (
            "cpp-library/pipeline-validation/playback-speed-candidates.md"),
        "source_repository_recorded": CRISPER_REPOSITORY,
        "weights_host_recorded": CRISPER_WEIGHTS_HOST,
        "code_license_recorded": CRISPER_CODE_LICENSE,
        "weights_license_recorded": CRISPER_WEIGHTS_LICENSE,
        "tag_recipe_recorded": list(CRISPER_TAGS),
        "boundary_range_ms_recorded": CRISPER_BOUNDARY_RANGE_MS,
        "crop_recipe_recorded": False,
        "runtime_recipe_recorded": False,
        "scoring_recipe_recorded": False,
        "saved_run_artifacts": False,
        "executed_here": False,
    }


# --------------------------------------------------------------------------
# Deterministic verbatim-token and boundary arithmetic control
# (synthetic; no model, runtime or audio)
# --------------------------------------------------------------------------
def _format_fraction(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 28
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal.quantize(Decimal("0.000001")), "f")


def normalize_token(text: str) -> str:
    """ASCII-only verbatim token normalisation; deterministic and total."""
    if not isinstance(text, str) or not text:
        raise ValueError("token_not_string")
    if ASCII_TEXT.fullmatch(text) is None:
        raise ValueError("token_not_ascii_printable")
    normalized = text.casefold().strip(".,!?;:\"'")
    if not normalized:
        raise ValueError("token_empty_after_normalisation")
    return normalized


def _token_cost(reference: str, hypothesis: str, reference_kind: str,
                hypothesis_kind: str) -> int:
    if reference == hypothesis and reference_kind == hypothesis_kind:
        return 0
    if reference_kind != hypothesis_kind:
        # A filler replaced by a lexical word is a deletion plus an insertion,
        # never a same-position substitution.
        return 3
    return 1


def align_verbatim(reference: list[dict], hypothesis: list[dict]) -> list[dict]:
    """Levenshtein-align verbatim tokens; kinds are part of identity."""
    for row in reference + hypothesis:
        if row.get("kind") not in KINDS:
            raise ValueError("token_kind")
        start = row.get("start_ms")
        end = row.get("end_ms")
        if isinstance(start, bool) or isinstance(end, bool) \
                or not isinstance(start, int) or not isinstance(end, int):
            raise ValueError("token_time")
        if start < 0 or end < start or end > int(MAX_TIMING_MS):
            raise ValueError("token_time_range")
    n, m = len(reference), len(hypothesis)
    cost = [[0] * (m + 1) for _ in range(n + 1)]
    back: list[list[str | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost[i][0], back[i][0] = i, "D"
    for j in range(1, m + 1):
        cost[0][j], back[0][j] = j, "I"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            ref = reference[i - 1]
            hyp = hypothesis[j - 1]
            substitute = cost[i - 1][j - 1] + _token_cost(
                normalize_token(ref["text"]), normalize_token(hyp["text"]),
                ref["kind"], hyp["kind"])
            delete = cost[i - 1][j] + 1
            insert = cost[i][j - 1] + 1
            best = min(substitute, delete, insert)
            cost[i][j] = best
            if substitute == best and delete != best and insert != best:
                back[i][j] = "M"
            elif delete == best:
                back[i][j] = "D"
            else:
                back[i][j] = "I"
    operations: list[dict] = []
    i, j = n, m
    while i or j:
        operation = back[i][j]
        if operation == "M":
            ref = reference[i - 1]
            hyp = hypothesis[j - 1]
            matched = (normalize_token(ref["text"]) ==
                       normalize_token(hyp["text"])
                       and ref["kind"] == hyp["kind"])
            operations.append({
                "op": "M" if matched else "S",
                "reference": copy.deepcopy(ref),
                "hypothesis": copy.deepcopy(hyp),
            })
            i -= 1
            j -= 1
        elif operation == "D":
            operations.append({
                "op": "D",
                "reference": copy.deepcopy(reference[i - 1]),
                "hypothesis": None,
            })
            i -= 1
        else:
            operations.append({
                "op": "I",
                "reference": None,
                "hypothesis": copy.deepcopy(hypothesis[j - 1]),
            })
            j -= 1
    operations.reverse()
    return operations


def score_verbatim(reference: list[dict], hypothesis: list[dict]) -> dict:
    operations = align_verbatim(reference, hypothesis)
    lexical_reference = sum(1 for row in reference if row["kind"] == "lexical")
    filler_reference = sum(1 for row in reference if row["kind"] == "filler")
    laughter_reference = sum(
        1 for row in reference if row["kind"] == "laughter")
    tag_reference = filler_reference + laughter_reference
    lexical_substitutions = lexical_deletions = lexical_insertions = 0
    filler_matched = laughter_matched = 0
    matches = substitutions = deletions = insertions = 0
    errors: list[int] = []
    for operation in operations:
        operator = operation["op"]
        ref = operation["reference"]
        if operator == "M":
            matches += 1
            if ref["kind"] == "filler":
                filler_matched += 1
            elif ref["kind"] == "laughter":
                laughter_matched += 1
            hyp = operation["hypothesis"]
            errors.append(abs(int(hyp["start_ms"]) - int(ref["start_ms"])))
            errors.append(abs(int(hyp["end_ms"]) - int(ref["end_ms"])))
        elif operator == "S":
            substitutions += 1
            if ref["kind"] == "lexical":
                lexical_substitutions += 1
        elif operator == "D":
            deletions += 1
            if ref["kind"] == "lexical":
                lexical_deletions += 1
        else:
            insertions += 1
            hyp = operation["hypothesis"]
            if hyp["kind"] == "lexical":
                lexical_insertions += 1
    tag_matched = filler_matched + laughter_matched
    if errors:
        ordered = sorted(errors)
        count = len(ordered)
        middle = count // 2
        median = (Fraction(ordered[middle]) if count % 2
                  else Fraction(ordered[middle - 1] + ordered[middle], 2))
        mae_text = _format_fraction(Fraction(sum(ordered), count))
        median_text = _format_fraction(median)
        within_text = _format_fraction(
            Fraction(sum(1 for error in ordered if error <= 50), count))
    else:
        mae_text = median_text = within_text = "0.000000"
    lexical_errors = (lexical_substitutions + lexical_deletions
                      + lexical_insertions)
    return {
        "reference_tokens": len(reference),
        "hypothesis_tokens": len(hypothesis),
        "matched_tokens": matches,
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "lexical_reference": lexical_reference,
        "lexical_substitutions": lexical_substitutions,
        "lexical_deletions": lexical_deletions,
        "lexical_insertions": lexical_insertions,
        "lexical_wer": (_format_fraction(Fraction(lexical_errors,
                                                  lexical_reference))
                        if lexical_reference else "0.000000"),
        "filler_reference": filler_reference,
        "filler_matched": filler_matched,
        "filler_recall": (_format_fraction(Fraction(filler_matched,
                                                    filler_reference))
                          if filler_reference else "0.000000"),
        "laughter_reference": laughter_reference,
        "laughter_matched": laughter_matched,
        "laughter_recall": (_format_fraction(Fraction(laughter_matched,
                                                      laughter_reference))
                            if laughter_reference else "0.000000"),
        "tag_reference": tag_reference,
        "tag_matched": tag_matched,
        "tag_recall": (_format_fraction(Fraction(tag_matched, tag_reference))
                       if tag_reference else "0.000000"),
        "boundary_error_count": len(errors),
        "boundary_mae_ms": mae_text,
        "boundary_median_abs_error_ms": median_text,
        "boundary_within_50ms_fraction": within_text,
    }


def _token(text: str, kind: str, start_ms: int, end_ms: int) -> dict:
    return {"text": text, "kind": kind, "start_ms": start_ms,
            "end_ms": end_ms}


SYNTHETIC_REFERENCE = (
    _token("so", "lexical", 0, 200),
    _token("[um]", "filler", 200, 420),
    _token("we", "lexical", 420, 600),
    _token("should", "lexical", 610, 820),
    _token("[uh]", "filler", 820, 980),
    _token("start", "lexical", 980, 1200),
    _token("now", "lexical", 1200, 1340),
    _token("[laughter]", "laughter", 1340, 1750),
    _token("right", "lexical", 1750, 1920),
    _token("[um]", "filler", 1920, 2100),
)
SYNTHETIC_HYPOTHESIS = (
    _token("so", "lexical", 10, 195),
    _token("[um]", "filler", 205, 415),
    _token("we", "lexical", 430, 595),
    _token("should", "lexical", 600, 815),
    _token("start", "lexical", 985, 1195),
    _token("now", "lexical", 1205, 1345),
    _token("[laughter]", "laughter", 1350, 1740),
    _token("right", "lexical", 1745, 1915),
    _token("[um]", "filler", 1925, 2105),
    _token("okay", "lexical", 2105, 2200),
)


def scorer_control() -> dict:
    reference = [dict(row) for row in SYNTHETIC_REFERENCE]
    hypothesis = [dict(row) for row in SYNTHETIC_HYPOTHESIS]
    result = score_verbatim(reference, hypothesis)
    expected = {
        "reference_tokens": 10,
        "hypothesis_tokens": 10,
        "matched_tokens": 9,
        "substitutions": 0,
        "deletions": 1,
        "insertions": 1,
        "lexical_reference": 6,
        "lexical_substitutions": 0,
        "lexical_deletions": 0,
        "lexical_insertions": 1,
        "lexical_wer": "0.166667",
        "filler_reference": 3,
        "filler_matched": 2,
        "filler_recall": "0.666667",
        "laughter_reference": 1,
        "laughter_matched": 1,
        "laughter_recall": "1.000000",
        "tag_reference": 4,
        "tag_matched": 3,
        "tag_recall": "0.750000",
        "boundary_error_count": 18,
        "boundary_mae_ms": "6.388889",
        "boundary_median_abs_error_ms": "5.000000",
        "boundary_within_50ms_fraction": "1.000000",
    }
    if result != expected:
        raise RuntimeError("scorer_control_mismatch")
    return {
        "id": "SCORE-CONTROL-01",
        "kind": "synthetic_verbatim_token_and_boundary_arithmetic",
        "synthetic": True,
        "label": "synthetic_verbatim_control_not_evidence",
        "reference_tokens": len(reference),
        "hypothesis_tokens": len(hypothesis),
        "result": result,
        "audio_read": False,
        "model_invoked": False,
        "runtime_imported": False,
        "qualifies": False,
    }


# --------------------------------------------------------------------------
# Fail-closed caller-supplied manifest admission (task-local only)
# --------------------------------------------------------------------------
def _type_name(value: Any) -> str:
    return type(value).__name__


def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("type:" + path)
    return value


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> dict:
    obj = _require_object(value, path)
    if set(obj) != set(expected):
        raise ValueError("keys:" + path)
    return obj


def _text(obj: dict, key: str, path: str, pattern: re.Pattern | None = None,
          max_length: int = 512) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise ValueError("string:" + path + "." + key)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ValueError("format:" + path + "." + key)
    return value


def _int(obj: dict, key: str, path: str, minimum: int, maximum: int) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("integer:" + path + "." + key)
    if value < minimum or value > maximum:
        raise ValueError("range:" + path + "." + key)
    return value


def _number(obj: dict, key: str, path: str, minimum: float,
            maximum: float) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("number:" + path + "." + key)
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite:" + path + "." + key)
    if number < minimum or number > maximum:
        raise ValueError("range:" + path + "." + key)
    return number


def _boolean(obj: dict, key: str, path: str,
             expected: bool | None = None) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise ValueError("boolean:" + path + "." + key)
    if expected is not None and value is not expected:
        raise ValueError("value:" + path + "." + key)
    return value


def _hex(obj: dict, key: str, path: str, pattern: re.Pattern) -> str:
    return _text(obj, key, path, pattern, 64)


def validate_manifest(manifest: dict) -> None:
    """Validate a future verbatim annotation manifest; never mutate or run."""
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("value:manifest.schema_id")
    _text(root, "cohort_id", "manifest", SLUG, 64)

    crisper = _exact_keys(root["crisperwhisper"], CRISPERWHISPER_FIELDS,
                          "crisperwhisper")
    if crisper["repository"] != CRISPER_REPOSITORY:
        raise ValueError("value:crisperwhisper.repository")
    _hex(crisper, "code_revision", "crisperwhisper", HEX40)
    if crisper["code_license_id"] != "mit":
        raise ValueError("value:crisperwhisper.code_license_id")
    _text(crisper, "weights_source", "crisperwhisper", SLUG, 64)
    _text(crisper, "weights_model_id", "crisperwhisper", MODEL_ID, 96)
    _hex(crisper, "weights_revision", "crisperwhisper", HEX40)
    _hex(crisper, "weights_sha256", "crisperwhisper", HEX64)
    _int(crisper, "weights_byte_count", "crisperwhisper", 1, 1 << 40)
    if crisper["weights_license_id"] != "cc-by-nc-4.0":
        raise ValueError("value:crisperwhisper.weights_license_id")
    _boolean(crisper, "commercial_use_granted", "crisperwhisper", False)
    _text(crisper, "license_review_reference", "crisperwhisper", None, 1024)

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    for key in ("python", "torch", "transformers"):
        _text(runtime, key, "runtime", None, 32)
    if runtime["device"] != "cpu":
        raise ValueError("value:runtime.device")
    _int(runtime, "intra_op_threads", "runtime", 1, 1)
    _int(runtime, "interop_op_threads", "runtime", 1, 1)
    _boolean(runtime, "deterministic_algorithms", "runtime", True)
    _boolean(runtime, "offline", "runtime", True)

    audio = root["audio"]
    if not isinstance(audio, list) or len(audio) != COHORT_ITEM_COUNT:
        raise ValueError("length:audio")
    for index, record in enumerate(audio):
        path = f"audio[{index}]"
        row = _exact_keys(record, AUDIO_FIELDS, path)
        _text(row, "id", path, SLUG, 64)
        _text(row, "path", path, ABSOLUTE, 512)
        _hex(row, "sha256", path, HEX64)
        if row["language"] != "en":
            raise ValueError("value:" + path + ".language")
        _text(row, "speaker_group", path, SLUG, 64)
        if row["sample_rate_hz"] != SAMPLE_RATE_HZ:
            raise ValueError("value:" + path + ".sample_rate_hz")
        if row["channels"] != CHANNELS:
            raise ValueError("value:" + path + ".channels")
        _int(row, "samples", path, 1, MAX_AUDIO_SAMPLES)

    reference = _exact_keys(root["reference"], REFERENCE_FIELDS, "reference")
    _text(reference, "source", "reference", None, 64)
    _hex(reference, "sha256", "reference", HEX64)
    _int(reference, "annotator_count", "reference", 2, 8)
    _int(reference, "token_count", "reference", 1, 100000)
    _boolean(reference, "has_filler_spans", "reference", True)

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("length:controls")
    kinds: list[str] = []
    control_ids: set[str] = set()
    for index, record in enumerate(controls):
        path = f"controls[{index}]"
        row = _exact_keys(record, CONTROL_FIELDS, path)
        control_id = _text(row, "id", path, SLUG, 64)
        if control_id in control_ids:
            raise ValueError("duplicate:" + path + ".id")
        control_ids.add(control_id)
        kind = row["kind"]
        if kind not in CONTROL_KINDS:
            raise ValueError("value:" + path + ".kind")
        kinds.append(kind)
    if sorted(kinds) != sorted(CONTROL_KINDS):
        raise ValueError("set:controls.kind")

    outcomes = _exact_keys(root["outcomes"], OUTCOME_FIELDS, "outcomes")
    _number(outcomes, "lexical_wer", "outcomes", 0.0, 1.0)
    _number(outcomes, "filler_recall", "outcomes", 0.0, 1.0)
    _number(outcomes, "laughter_recall", "outcomes", 0.0, 1.0)
    _number(outcomes, "boundary_mae_ms", "outcomes", 0.0, MAX_TIMING_MS)
    _number(outcomes, "boundary_median_abs_error_ms", "outcomes", 0.0,
            MAX_TIMING_MS)
    _number(outcomes, "boundary_within_50ms_fraction", "outcomes", 0.0, 1.0)
    _int(outcomes, "matched_tokens", "outcomes", 0, 100000)
    _int(outcomes, "reference_tokens", "outcomes", 1, 100000)
    _int(outcomes, "nonfinite_count", "outcomes", 0, 0)
    _int(outcomes, "sample_count", "outcomes", COHORT_ITEM_COUNT,
         COHORT_ITEM_COUNT)

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for key in ("dataset_terms_reference", "weights_terms_reference",
                "output_use_reference", "commercial_use_decision_reference",
                "review_reference"):
        _text(rights, key, "rights", None, 1024)
    _boolean(rights, "claims_qualified", "rights", False)


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-control:" + label).encode()).hexdigest()


def control_manifest() -> dict:
    """Build the one structural control; it is not evidence of any result."""
    outcome = scorer_control()["result"]
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cohort_id": "synthetic-verbatim-annotation",
        "crisperwhisper": {
            "repository": CRISPER_REPOSITORY,
            "code_revision": _synthetic_digest("code")[:40],
            "code_license_id": "mit",
            "weights_source": "hugging-face",
            "weights_model_id": "synthetic/crisperwhisper",
            "weights_revision": _synthetic_digest("weight-revision")[:40],
            "weights_sha256": _synthetic_digest("weights"),
            "weights_byte_count": 1048576,
            "weights_license_id": "cc-by-nc-4.0",
            "commercial_use_granted": False,
            "license_review_reference": "synthetic://review/not-performed",
        },
        "runtime": {
            "python": "3.12.0",
            "torch": "2.7.0",
            "transformers": "4.53.0",
            "device": "cpu",
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
        },
        "audio": [
            {
                "id": "synthetic-verbatim-crop",
                "path": "/synthetic/audio/verbatim-16k-mono.wav",
                "sha256": _synthetic_digest("audio"),
                "language": "en",
                "speaker_group": "speaker-a",
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "samples": 160000,
            },
        ],
        "reference": {
            "source": "adjudicated-human-verbatim",
            "sha256": _synthetic_digest("reference"),
            "annotator_count": 2,
            "token_count": outcome["reference_tokens"],
            "has_filler_spans": True,
        },
        "controls": [
            {"id": "control-second-annotator",
             "kind": "independent_second_annotator"},
            {"id": "control-uniform", "kind": "uniform_word_timing_baseline"},
            {"id": "control-stripped",
             "kind": "filler_stripped_transcript_baseline"},
        ],
        "outcomes": {
            "lexical_wer": 0.166667,
            "filler_recall": 0.666667,
            "laughter_recall": 1.0,
            "boundary_mae_ms": 6.388889,
            "boundary_median_abs_error_ms": 5.0,
            "boundary_within_50ms_fraction": 1.0,
            "matched_tokens": outcome["matched_tokens"],
            "reference_tokens": outcome["reference_tokens"],
            "nonfinite_count": 0,
            "sample_count": COHORT_ITEM_COUNT,
        },
        "rights": {
            "dataset_terms_reference": "synthetic://rights/dataset",
            "weights_terms_reference": "synthetic://rights/noncommercial",
            "output_use_reference": "synthetic://rights/output-use",
            "commercial_use_decision_reference": "synthetic://rights/no-commercial-grant",
            "review_reference": "synthetic://review/not-performed",
            "claims_qualified": False,
        },
    }


def admission_cases() -> list[dict]:
    """Enumerate adverse mutations; every one must be rejected."""
    base = control_manifest()

    def set_path(path: tuple[Any, ...], value: Any):
        def apply(document: dict) -> None:
            target: Any = document
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        return apply

    def del_path(path: tuple[Any, ...]):
        def apply(document: dict) -> None:
            target: Any = document
            for key in path[:-1]:
                target = target[key]
            if isinstance(target, dict):
                del target[path[-1]]
            else:
                target.pop(path[-1])
        return apply

    def duplicate_control_kind(document: dict) -> None:
        document["controls"][1]["kind"] = document["controls"][0]["kind"]

    def extra_top_level(document: dict) -> None:
        document["extra"] = True

    def missing_encoder(document: dict) -> None:
        del document["crisperwhisper"]

    def duplicate_audio(document: dict) -> None:
        document["audio"].append(copy.deepcopy(document["audio"][0]))

    def bool_as_threads(document: dict) -> None:
        document["runtime"]["intra_op_threads"] = True

    def bool_as_byte_count(document: dict) -> None:
        document["crisperwhisper"]["weights_byte_count"] = True

    def bool_as_annotators(document: dict) -> None:
        document["reference"]["annotator_count"] = True

    def nonfinite_wer(document: dict) -> None:
        document["outcomes"]["lexical_wer"] = float("nan")

    def nonfinite_mae(document: dict) -> None:
        document["outcomes"]["boundary_mae_ms"] = float("inf")

    mutations = [
        ("ADM-01", "missing_crisperwhisper", missing_encoder),
        ("ADM-02", "extra_top_level_field", extra_top_level),
        ("ADM-03", "wrong_schema_id",
         set_path(("schema_id",), "audio-sdk/other/0.1")),
        ("ADM-04", "cohort_id_not_slug",
         set_path(("cohort_id",), "Not A Slug")),
        ("ADM-05", "wrong_repository",
         set_path(("crisperwhisper", "repository"),
                  "https://github.com/other/CrisperWhisper")),
        ("ADM-06", "short_code_revision",
         set_path(("crisperwhisper", "code_revision"), "abc")),
        ("ADM-07", "uppercase_code_revision",
         set_path(("crisperwhisper", "code_revision"), "A" * 40)),
        ("ADM-08", "wrong_code_license",
         set_path(("crisperwhisper", "code_license_id"), "apache-2.0")),
        ("ADM-09", "weights_source_not_slug",
         set_path(("crisperwhisper", "weights_source"), "Hugging Face")),
        ("ADM-10", "empty_weights_model_id",
         set_path(("crisperwhisper", "weights_model_id"), "")),
        ("ADM-11", "weights_model_id_no_namespace",
         set_path(("crisperwhisper", "weights_model_id"), "crisperwhisper")),
        ("ADM-12", "short_weights_revision",
         set_path(("crisperwhisper", "weights_revision"), "abc")),
        ("ADM-13", "uppercase_weights_revision",
         set_path(("crisperwhisper", "weights_revision"), "B" * 40)),
        ("ADM-14", "short_weights_sha",
         set_path(("crisperwhisper", "weights_sha256"), "abc")),
        ("ADM-15", "uppercase_weights_sha",
         set_path(("crisperwhisper", "weights_sha256"), "F" * 64)),
        ("ADM-16", "zero_weight_bytes",
         set_path(("crisperwhisper", "weights_byte_count"), 0)),
        ("ADM-17", "bool_weight_bytes", bool_as_byte_count),
        ("ADM-18", "wrong_weights_license",
         set_path(("crisperwhisper", "weights_license_id"), "mit")),
        ("ADM-19", "commercial_use_claimed",
         set_path(("crisperwhisper", "commercial_use_granted"), True)),
        ("ADM-20", "empty_license_review",
         set_path(("crisperwhisper", "license_review_reference"), "")),
        ("ADM-21", "missing_crisperwhisper_field",
         del_path(("crisperwhisper", "weights_sha256"))),
        ("ADM-22", "empty_runtime_python",
         set_path(("runtime", "python"), "")),
        ("ADM-23", "cuda_device", set_path(("runtime", "device"), "cuda")),
        ("ADM-24", "wrong_intra_threads",
         set_path(("runtime", "intra_op_threads"), 2)),
        ("ADM-25", "zero_interop_threads",
         set_path(("runtime", "interop_op_threads"), 0)),
        ("ADM-26", "determinism_off",
         set_path(("runtime", "deterministic_algorithms"), False)),
        ("ADM-27", "offline_off", set_path(("runtime", "offline"), False)),
        ("ADM-28", "bool_as_int_threads", bool_as_threads),
        ("ADM-29", "missing_runtime_field",
         del_path(("runtime", "torch"))),
        ("ADM-30", "short_audio", duplicate_audio),
        ("ADM-31", "empty_audio",
         set_path(("audio",), [])),
        ("ADM-32", "relative_audio_path",
         set_path(("audio", 0, "path"), "synthetic/audio/crop.wav")),
        ("ADM-33", "short_audio_sha",
         set_path(("audio", 0, "sha256"), "abc")),
        ("ADM-34", "wrong_language",
         set_path(("audio", 0, "language"), "fr")),
        ("ADM-35", "empty_speaker_group",
         set_path(("audio", 0, "speaker_group"), "")),
        ("ADM-36", "wrong_sample_rate",
         set_path(("audio", 0, "sample_rate_hz"), 8000)),
        ("ADM-37", "stereo_audio",
         set_path(("audio", 0, "channels"), 2)),
        ("ADM-38", "zero_samples",
         set_path(("audio", 0, "samples"), 0)),
        ("ADM-39", "too_many_samples",
         set_path(("audio", 0, "samples"), MAX_AUDIO_SAMPLES + 1)),
        ("ADM-40", "missing_audio_field",
         del_path(("audio", 0, "samples"))),
        ("ADM-41", "audio_id_not_slug",
         set_path(("audio", 0, "id"), "Not A Slug")),
        ("ADM-42", "empty_reference_source",
         set_path(("reference", "source"), "")),
        ("ADM-43", "short_reference_sha",
         set_path(("reference", "sha256"), "abc")),
        ("ADM-44", "single_annotator",
         set_path(("reference", "annotator_count"), 1)),
        ("ADM-45", "bool_as_annotators", bool_as_annotators),
        ("ADM-46", "zero_reference_tokens",
         set_path(("reference", "token_count"), 0)),
        ("ADM-47", "no_filler_spans",
         set_path(("reference", "has_filler_spans"), False)),
        ("ADM-48", "missing_reference", del_path(("reference",))),
        ("ADM-49", "missing_control", lambda d: d["controls"].pop()),
        ("ADM-50", "duplicate_control_kind", duplicate_control_kind),
        ("ADM-51", "unknown_control_kind",
         set_path(("controls", 0, "kind"), "identity_passthrough")),
        ("ADM-52", "extra_control",
         lambda d: d["controls"].append(
             {"id": "control-extra",
              "kind": "independent_second_annotator"})),
        ("ADM-53", "lexical_wer_out_of_range",
         set_path(("outcomes", "lexical_wer"), 1.01)),
        ("ADM-54", "nonfinite_lexical_wer", nonfinite_wer),
        ("ADM-55", "filler_recall_out_of_range",
         set_path(("outcomes", "filler_recall"), -0.1)),
        ("ADM-56", "laughter_recall_out_of_range",
         set_path(("outcomes", "laughter_recall"), 1.1)),
        ("ADM-57", "negative_mae",
         set_path(("outcomes", "boundary_mae_ms"), -1.0)),
        ("ADM-58", "nonfinite_mae", nonfinite_mae),
        ("ADM-59", "negative_median",
         set_path(("outcomes", "boundary_median_abs_error_ms"), -1.0)),
        ("ADM-60", "fraction_out_of_range",
         set_path(("outcomes", "boundary_within_50ms_fraction"), 1.01)),
        ("ADM-61", "negative_matched_tokens",
         set_path(("outcomes", "matched_tokens"), -1)),
        ("ADM-62", "zero_reference_outcome_tokens",
         set_path(("outcomes", "reference_tokens"), 0)),
        ("ADM-63", "nonfinite_count_nonzero",
         set_path(("outcomes", "nonfinite_count"), 1)),
        ("ADM-64", "wrong_sample_count",
         set_path(("outcomes", "sample_count"), 2)),
        ("ADM-65", "missing_wer", del_path(("outcomes", "lexical_wer"))),
        ("ADM-66", "missing_dataset_terms",
         del_path(("rights", "dataset_terms_reference"))),
        ("ADM-67", "empty_output_use",
         set_path(("rights", "output_use_reference"), "")),
        ("ADM-68", "empty_commercial_decision",
         set_path(("rights", "commercial_use_decision_reference"), "")),
        ("ADM-69", "qualified_claim",
         set_path(("rights", "claims_qualified"), True)),
        ("ADM-70", "extra_rights_field",
         set_path(("rights", "extra"), "x")),
    ]

    cases: list[dict] = []
    for case_id, name, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        snapshot = copy.deepcopy(candidate)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            code = str(error)
        except Exception as error:  # pragma: no cover - defensive
            code = "unexpected:" + _type_name(error)
        else:
            raise RuntimeError("admission_mutation_accepted:" + case_id)
        if candidate != snapshot:
            raise RuntimeError("admission_state_mutated:" + case_id)
        cases.append({
            "id": case_id,
            "name": name,
            "status": "rejected",
            "code": code,
            "qualifies": False,
            "state_unchanged": True,
        })
    return cases


def build_admission() -> dict:
    control = copy.deepcopy(control_manifest())
    before = copy.deepcopy(control)
    validate_manifest(control)
    if control != before:
        raise RuntimeError("admission_control_mutated")
    cases = admission_cases()
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "boundary": "task_local_manifest_admission_only_not_a_runtime",
        "control": {
            "id": "ADM-ACCEPT-01",
            "accepted": True,
            "qualifies": False,
            "label": "synthetic_schema_control_not_evidence",
            "state_unchanged": True,
            "audio_records": len(control["audio"]),
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(1 for case in cases
                                  if case["status"] == "rejected"),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


# --------------------------------------------------------------------------
# Contract and report
# --------------------------------------------------------------------------
def build_contract() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    qualification = {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": True,
        "crisperwhisper_source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "model_card_present": False,
        "commercial_license_granted": False,
        "verbatim_result": False,
        "filler_result": False,
        "lexical_wer_result": False,
        "boundary_result": False,
        "finite_output_result": False,
        "baseline_result": False,
        "device_timing_result": False,
        "rate_profile_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }
    gates = [dict(gate, qualifies=False, linked_row=row)
             for gate in RELEASE_GATES]
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": qualification,
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "scope": {
            "write_scope": WRITE_SCOPE,
            "task_local_only": True,
            "provider_registered": False,
            "adapter_implemented": False,
            "processor_exposed": False,
            "public_abi_changed": False,
            "registry_or_default_changed": False,
            "shared_build_or_ci_changed": False,
            "real_assets_used": False,
            "weights_used": False,
            "network_used": False,
            "listening_performed": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "release_claim": False,
        },
        "boundary": {
            "linked_row_identity_only": True,
            "board_file_pinned": False,
            "mutable_board_fields_gate": False,
            "projected_fields": list(BOARD_ROW_FIELDS),
            "linked_row": row,
            "linked_row_sha256": board_row_digest(row),
            "linked_rows_sha256": linked_rows_digest(rows),
            "linked_rows": rows,
        },
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "changed": False,
        },
        "exact_models": exact_models(),
        "historical_recipe": historical_recipe(),
        "required_artifacts": [dict(artifact) for artifact in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "release_gates": gates,
        "rate_profile_requirements": [dict(row_) for row_ in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(row_) for row_ in QUALITY_ROWS],
        "timing_requirements": [dict(row_) for row_ in TIMING_ROWS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "crisperwhisper_fields": list(CRISPERWHISPER_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "audio_fields": list(AUDIO_FIELDS),
            "reference_fields": list(REFERENCE_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "outcome_fields": list(OUTCOME_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "cohort_item_count": COHORT_ITEM_COUNT,
            "max_audio_samples": MAX_AUDIO_SAMPLES,
            "repository_required": CRISPER_REPOSITORY,
            "weights_license_required": CRISPER_WEIGHTS_LICENSE,
            "minimum_annotators": 2,
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "code_license_recorded": CRISPER_CODE_LICENSE,
            "code_terms_reviewed": False,
            "weights_license_recorded": CRISPER_WEIGHTS_LICENSE,
            "weights_terms_reviewed": False,
            "commercial_use_granted": False,
            "output_use_defined": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
    }
    workspace_probes = absence_probes()
    external_probes = external_absence_probes()
    claims = documented_claims()
    presence = source_presence()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "mode": MODE,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": contract["qualification"],
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "contract_sha256": object_digest(contract),
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "exact_models": contract["exact_models"],
        "historical_recipe": contract["historical_recipe"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {
            "profile": PROFILE,
            "label": PROFILE_LABEL,
            "rows": contract["rate_profile_requirements"],
            "blocked_rows": len(contract["rate_profile_requirements"]),
        },
        "quality_outcomes": {
            "rows": contract["quality_outcomes"],
            "blocked_rows": len(contract["quality_outcomes"]),
        },
        "timing": {
            "rows": contract["timing_requirements"],
            "blocked_rows": len(contract["timing_requirements"]),
        },
        "documented_context": {
            "source_reported_claims_not_reproduced": claims,
            "why_not_reproduced": [
                "No CrisperWhisper source checkout exists at an exact revision.",
                "The exact weight model ID, revision and digest are not "
                "recorded and no weight is present.",
                "The weights are CC-BY-NC-4.0 and no separate commercial "
                "licence or output-use decision exists.",
                "No pinned offline runtime, lockfile or import digest exists.",
                "No rights-cleared audio, verbatim reference, second annotator "
                "or target-device measurement exists.",
                "The task row's Rate profile is a mismatch for a verbatim "
                "annotation tool and remains blocked.",
            ],
            "provenance_only": True,
            "reproduced_here": False,
            "used_for_evidence": False,
            "qualifies": False,
        },
        "recipe_provenance": recipe_provenance(),
        "source_presence": presence,
        "absence_evidence": {
            "workspace_probes": workspace_probes,
            "external_probes": external_probes,
            "summary": absence_summary(workspace_probes, external_probes),
        },
        "admission": build_admission(),
        "scorer_control": scorer_control(),
        "source_pins": pins["source"],
        "boundary_pins": pins["boundary"],
        "linked_row_identity": {
            "projection": board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW),
            "sha256": board_row_digest(
                board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)),
            "linked_rows": linked_rows(),
            "linked_rows_sha256": linked_rows_digest(),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "non_claims": contract["non_claims"],
        "required_results": contract["required_results"],
        "reproduction": {
            "regeneration": "run.py all (repeat=3, byte-identical)",
            "tests": "python3 -m unittest -v test_reference.py",
            "verifier": "python3 verify.py",
            "stdlib_only": True,
            "network_used": False,
        },
    }


def canonical_report(document: dict) -> tuple[str, str]:
    text = canonical_text(document)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    gates = contract.get("release_gates", [])
    if len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("contract_gate_reopen")
    artifacts = contract.get("required_artifacts", [])
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if sum(1 for row in artifacts if row.get("present")) != 1:
        raise ValueError("contract_artifact_presence")
    for row in artifacts[1:]:
        if row.get("present") is not False or row.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
    blockers = contract.get("exact_blockers", [])
    if len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
    for section, expected in (
            ("rate_profile_requirements", RATE_PROFILE_ROWS),
            ("quality_outcomes", QUALITY_ROWS),
            ("timing_requirements", TIMING_ROWS)):
        rows = contract.get(section, [])
        if len(rows) != len(expected):
            raise ValueError("contract_section_count:" + section)
        for row in rows:
            if row.get("status") != "blocked":
                raise ValueError("contract_section_not_blocked:" + section)
    qualification = contract.get("qualification", {})
    for key in ("real_result_present", "crisperwhisper_source_present",
                "weights_present", "runtime_present", "model_card_present",
                "commercial_license_granted", "verbatim_result",
                "filler_result", "lexical_wer_result", "boundary_result",
                "finite_output_result", "baseline_result",
                "device_timing_result", "rate_profile_result",
                "listening_result", "benchmark_result", "release_claim",
                "missing_result_promoted"):
        if qualification.get(key) is not False:
            raise ValueError("contract_qualification_flag:" + key)
    if qualification.get("not_qualified") is not True:
        raise ValueError("contract_not_qualified")
    if qualification.get("all_release_gates_blocked") is not True:
        raise ValueError("contract_gate_flag")
    if qualification.get("source_present") is not True:
        raise ValueError("contract_source_present")
    models = contract.get("exact_models", {})
    if models.get("crisperwhisper", {}).get("weights_present") is not False:
        raise ValueError("contract_weights")
    if models.get("crisperwhisper", {}).get("source_present") is not False:
        raise ValueError("contract_source")
    if models.get("crisperwhisper", {}).get(
            "commercial_use_granted") is not False:
        raise ValueError("contract_commercial")
    if models.get("runtime", {}).get("present") is not False:
        raise ValueError("contract_runtime")
    if contract.get("licensing", {}).get("commercial_use_granted") is not False:
        raise ValueError("contract_license_commercial")
