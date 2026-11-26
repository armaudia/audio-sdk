# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-PODCASTFILLERS.

Standard-library only and deterministic. This module contains no PodcastFillers
dataset audio, annotation, label, model weight, runtime, classifier, VAD, ASR,
download, network use or inference result. It records the exact pinned claims,
probes fixed candidate intake/cache paths to evidence absence, defines a
fail-closed admission boundary for a future rights-cleared filler-annotation
manifest, implements deterministic synthetic filler-label accounting controls,
and builds the canonical contract/report.

The pinned candidate note records PodcastFillers as a dataset whose annotations
are non-commercial and whose useful part is the VAD+ASR+classifier pipeline,
not the data. The inventory row requires documenting rights scope and keeping
research dataset acquisition outside the SDK artifact. No dataset, model or
runtime is present or produced here. Every result remains blocked.
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

TASK = "SDK-PODCASTFILLERS"
COMPONENT_ID = "podcastfillers"
TASK_TITLE = "PodcastFillers"
CONTRACT_ID = "audio-sdk/podcastfillers-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/podcastfillers-annotation-manifest/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "research-control"
BASE_COMMIT = "4e3a84719a4d5f6171b97f0ed1d77078be47dbdb"
BRANCH = "swarm/SDK-PODCASTFILLERS"
WRITE_SCOPE = "docs/task-evidence/podcastfillers/ only"
TASK_PREFIX = "docs/task-evidence/podcastfillers/"
DISPOSITION = (
    "PodcastFillers non-commercial-annotations blocker; no dataset, audio, "
    "annotation, model, runtime, adapter or result.")

PODCASTFILLERS_URL = "https://podcastfillers.github.io/"
PODCASTFILLERS_ANNOTATIONS_LICENSE = "non-commercial (separate terms; exact terms not staged)"
PODCASTFILLERS_PIPELINE_NOTE = "VAD + ASR + classifier (pipeline idea only; no data/model)"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
COHORT_ITEM_COUNT = 1
MAX_AUDIO_SAMPLES = 60 * SAMPLE_RATE_HZ
MAX_TIMING_MS = 60000.0

HERE = Path(__file__).resolve().parent


def _find_worktree() -> Path:
    override = os.environ.get("SDK_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.append(HERE.parents[2])
    candidates.extend(HERE.parents)
    for candidate in candidates:
        if (candidate / "api/include/audio_sdk/provider_v0.h").is_file() and (candidate / "CONTRACTS.md").is_file():
            return candidate.resolve()
    raise RuntimeError("sdk_root_not_found")


WORKTREE = _find_worktree()


def _find_audio_root() -> Path:
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
    "docs/task-evidence/webrtc-vad/README.md":
        "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65",
    "docs/task-evidence/webrtc-vad/contract.json":
        "74137431954f9ed1206a56fc5e5fa28003a6f78985fe8699cf500bbc981d60ef",
    "docs/task-evidence/webrtc-vad/report.json":
        "762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb",
    "docs/task-evidence/bayesian-information-criterion-speaker-segmentation/README.md":
        "973b2445df6c08180e41616896aa669c83fa9753db1ae35183332b35437fffca",
    "docs/task-evidence/bayesian-information-criterion-speaker-segmentation/contract.json":
        "16d28634d1ea0b4f1d791bc5cef7e5e3065121c1f9f5049e052b7afc87fe0422",
    "docs/task-evidence/bayesian-information-criterion-speaker-segmentation/report.json":
        "daf1213b91b1887178ef50b9be4496c9b95c1407c78701d4910529f37c844023",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")

WORKSPACE_ABSENCE_PROBES = (
    "data/datasets/podcastfillers",
    "data/datasets/PodcastFillers",
    "data/annotations/podcastfillers",
    "data/models/podcastfillers",
    "cpp-library/pipeline-validation/playback-speed/models/podcastfillers",
    "research/podcastfillers",
)
EXTERNAL_ABSENCE_PROBES = (
    "/private/tmp/podcastfillers",
    "/private/tmp/PodcastFillers",
    "~/.cache/podcastfillers",
    "~/.cache/huggingface/datasets/podcastfillers",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "pinned_candidate_note",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The exact pinned candidate note, inventory row, plan and "
            "verification profile that record PodcastFillers rights scope and "
            "non-commercial annotations."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "podcastfillers_dataset_identity_and_terms",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact PodcastFillers dataset release/package identity, "
            "version or commit, byte count and SHA-256, and the complete "
            "annotation/audio terms with an independent rights review."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "rights_cleared_audio_and_annotations",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Rights-cleared or separately licensed audio and filler "
            "annotations with explicit commercial/output-use decision; "
            "research acquisition remains outside the SDK artifact."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_offline_runtime_or_model",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A pinned, rights-reviewed offline model/runtime if a classifier "
            "or pipeline is reproduced, with exact digests, deterministic "
            "settings and no network."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "reproduced_filler_detection_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A fresh offline reproduction with frozen scorer, exact "
            "token/span accounting, finite/adverse rejection, and matched "
            "controls on a rights-cleared cohort."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "rate_profile_and_timing_evidence",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Rate-profile evidence or a reviewed waiver, plus target-device "
            "paced timing/resources if any runtime path is claimed."),
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
            "No PodcastFillers dataset release, package identity, version/"
            "commit, digest or complete terms bundle is staged. The pinned note "
            "records only that annotations are non-commercial; no exact terms "
            "text, rights review or acquisition record is present. No dataset "
            "was downloaded or reconstructed."),
        "required_action": (
            "Supply the exact PodcastFillers dataset identity, version/commit, "
            "byte count and SHA-256, complete audio/annotation terms, and an "
            "independent rights review. Keep research acquisition outside the "
            "SDK artifact."),
        "linked_gates": ["RG-01", "RG-02"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared or separately licensed audio/annotation subset "
            "exists for commercial SDK use. Non-commercial annotations cannot "
            "be used as training/evaluation data for a shipped model without a "
            "separate reviewed licence/decision."),
        "required_action": (
            "Provide a rights-cleared or separately licensed subset with "
            "explicit commercial/output-use decision, provenance, and reviewed "
            "dataset terms; do not place acquired research data in the SDK."),
        "linked_gates": ["RG-02", "RG-04"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No pinned offline runtime/model is present. The candidate note "
            "mentions a VAD+ASR+classifier pipeline idea, but no exact code, "
            "weights, lockfile, import digest or deterministic runtime is "
            "staged. No model/runtime was imported or executed."),
        "required_action": (
            "If reproducing a classifier/pipeline, supply exact source/weight/"
            "runtime identities, digests, deterministic settings, and a "
            "clean-room offline load trace."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No reproduced filler-detection or annotation result exists. There "
            "are no local precision/recall/F1/boundary metrics, no finite-output "
            "scan, no matched controls, and no rights-cleared cohort run."),
        "required_action": (
            "Run a rights-cleared reproduction with frozen scorer, exact "
            "span/token accounting, finite/adverse/missing-input rejection, and "
            "matched controls; do not promote source-reported claims."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No Rate-profile evidence or target-device timing exists. The task "
            "row's Rate profile is not exercised; no source/output mapping, "
            "duration, buffering, 1x/rate-change, rebuffer/drift, or "
            "timestamp-tied pause/filler preservation measurement is present."),
        "required_action": (
            "Provide Rate-profile evidence or a reviewed waiver, and measure "
            "paced target-device timing/resources if any runtime path is "
            "claimed."),
        "linked_gates": ["RG-06", "RG-07"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider, tool, adapter or intake exists. No registry, "
            "default, public ABI, shared build or CI change was made; any "
            "future intake must be separate, OFF by default and exact-head "
            "reviewed after all prior gates clear."),
        "required_action": (
            "Open a separate versioned, OFF-by-default opt-in intake with "
            "exact descriptor/config, clean-install proof and independent "
            "exact-head review after all prior gates clear."),
        "linked_gates": ["RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "dataset_identity_and_terms_provenance",
        "status": "blocked",
        "statement": (
            "Only the candidate note and inventory row are pinned. The exact "
            "PodcastFillers dataset identity, version/commit, digest and "
            "complete terms bundle are not staged or reviewed."),
        "reopen_condition": (
            "Pin the exact dataset identity/version/commit/digest and stage "
            "complete terms with an independent rights review."),
    },
    {
        "id": "RG-02",
        "title": "noncommercial_annotations_and_commercial_use_decision",
        "status": "blocked",
        "statement": (
            "PodcastFillers annotations are recorded as non-commercial. No "
            "separate commercial licence/output-use decision exists for SDK "
            "use."),
        "reopen_condition": (
            "Provide a written commercial/output-use decision or separately "
            "licensed rights-cleared data reviewed independently."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_model_and_offline_load",
        "status": "blocked",
        "statement": (
            "No pinned model/runtime exists for any VAD+ASR+classifier "
            "reproduction; no lockfile, digest, deterministic settings or "
            "offline-load trace is present."),
        "reopen_condition": (
            "Provide exact model/runtime identities, digests, deterministic "
            "offline settings and a clean-room load trace."),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_cohort_and_acquisition_boundary",
        "status": "blocked",
        "statement": (
            "No rights-cleared cohort or acquisition-boundary record exists; "
            "research dataset acquisition must remain outside the SDK artifact."),
        "reopen_condition": (
            "Stage a rights-reviewed cohort manifest outside SDK artifact "
            "acquisition paths with reviewed terms and provenance."),
    },
    {
        "id": "RG-05",
        "title": "filler_detection_accuracy_with_controls",
        "status": "blocked",
        "statement": (
            "No filler detection/annotation accuracy, finite-output scan, or "
            "matched-control result is reproduced."),
        "reopen_condition": (
            "Reproduce accuracy with frozen scorer, exact accounting, finite "
            "checks, and matched controls on a rights-cleared cohort."),
    },
    {
        "id": "RG-06",
        "title": "rate_profile_condition_coverage",
        "status": "blocked",
        "statement": (
            "The Rate profile is not exercised: no source/output mapping, "
            "duration, pitch/transient, buffering, rate-change, "
            "speech/music/silence, rebuffer/drift, final-partial-window, or "
            "timestamp-tied pause/filler preservation evidence exists."),
        "reopen_condition": (
            "Supply Rate-profile evidence or a reviewed waiver with separate "
            "source references and timestamp-tied preservation accounting."),
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_resources_and_deadlines",
        "status": "blocked",
        "statement": (
            "No target-device load/inference latency, RTF, CPU/memory/energy, "
            "queue or deadline measurement exists."),
        "reopen_condition": (
            "Measure exact paced target-device timing/resources on the "
            "intended workload with p50/p95/p99 and fill/flush behavior."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "statement": (
            "No provider/tool intake or public-surface decision exists. "
            "Installed v0 geometry, registry, default and shared build remain "
            "untouched."),
        "reopen_condition": (
            "Open a separate versioned, OFF-by-default opt-in intake with "
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
            "PodcastFillers is a dataset/annotation lead, not a renderer; no "
            "source/output mapping or duration result exists."),
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
        "evidence": "No 1x or rate-change comparison exists; no stretcher/runtime is present.",
    },
    {
        "id": "RATE-05",
        "requirement": "Include unfamiliar speech, music and silence.",
        "status": "blocked",
        "evidence": "No rights-cleared cohort exists; no speech/music/silence coverage was tested.",
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
            "Filler annotations could inform a controller, but no "
            "source-timestamp-tied pause/filler policy or speech-preservation "
            "measurement exists."),
    },
    {
        "id": "RATE-08",
        "requirement": "Map output to a reviewed preferred-speed policy.",
        "status": "blocked",
        "evidence": (
            "No preference/acceptability labels or rate-to-speed policy exists; "
            "dataset presence is not a preferred speed factor."),
    },
)

QUALITY_ROWS = (
    {
        "id": "QUAL-01",
        "outcome": "filler_detection_precision_recall_f1",
        "status": "blocked",
        "value": None,
        "evidence": "No rights-cleared filler detection run or scorer output exists.",
    },
    {
        "id": "QUAL-02",
        "outcome": "filler_boundary_error_and_within_tolerance",
        "status": "blocked",
        "value": None,
        "evidence": "No filler boundary annotations or boundary-error measurement exists.",
    },
    {
        "id": "QUAL-03",
        "outcome": "false_alarm_rate_on_nonfiller_speech_music_silence",
        "status": "blocked",
        "value": None,
        "evidence": "No negative/control cohort or false-alarm measurement exists.",
    },
    {
        "id": "QUAL-04",
        "outcome": "finite_output_and_adverse_input_rejection",
        "status": "blocked",
        "value": None,
        "evidence": "No runtime exists to scan outputs or reject adverse inputs.",
    },
    {
        "id": "QUAL-05",
        "outcome": "matched_controls_and_baselines",
        "status": "blocked",
        "value": None,
        "evidence": "Only synthetic arithmetic controls exist; no real baseline exists.",
    },
)

TIMING_ROWS = (
    {
        "id": "TIME-01",
        "metric": "model_load_and_inference_latency",
        "status": "blocked",
        "value": None,
        "evidence": "No model/runtime load or inference p50/p95/RTF was measured.",
    },
    {
        "id": "TIME-02",
        "metric": "annotation_or_scoring_wall_time",
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
    "No PodcastFillers dataset, audio, annotation, label file or derived asset is present in this package.",
    "No PodcastFillers model, classifier, VAD, ASR, runtime or inference path is imported or executed.",
    "No filler detection, boundary, precision/recall, listening, device timing, benchmark or release result is reproduced.",
    "No dataset acquisition occurred; research dataset acquisition remains outside the SDK artifact.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "Non-commercial annotations are not a commercial SDK runtime or rights basis.",
    "Source-reported pipeline ideas are not evidence of a qualified implementation.",
)

REQUIRED_RESULTS = (
    "Exact PodcastFillers dataset identity/version/commit/digest and complete terms.",
    "Independent rights review and written commercial/output-use decision or separately licensed data.",
    "Rights-cleared cohort manifest kept outside SDK artifact acquisition paths.",
    "Pinned offline model/runtime identities, digests and deterministic load trace if reproduced.",
    "Reproduced filler detection/boundary metrics with finite/adverse/missing-input rejection and controls.",
    "Rate-profile evidence or reviewed waiver plus target-device paced timing/resources.",
    "Separate OFF-by-default provider/tool intake and independent exact-head review.",
)

MANIFEST_FIELDS = (
    "schema_id", "cohort_id", "dataset", "runtime", "audio", "reference",
    "controls", "outcomes", "rights")
DATASET_FIELDS = (
    "name", "source_url", "version", "release_sha256", "byte_count",
    "license_id", "license_review_reference", "commercial_use_granted")
RUNTIME_FIELDS = (
    "python", "model_name", "model_revision", "device", "intra_op_threads",
    "interop_op_threads", "deterministic_algorithms", "offline")
AUDIO_FIELDS = (
    "id", "path", "sha256", "language", "speaker_group", "sample_rate_hz",
    "channels", "samples")
REFERENCE_FIELDS = (
    "source", "sha256", "annotator_count", "filler_span_count",
    "has_nonfiller_controls")
CONTROL_FIELDS = ("id", "kind")
CONTROL_KINDS = (
    "independent_second_annotator",
    "nonfiller_speech_negative_control",
    "silence_music_negative_control",
)
OUTCOME_FIELDS = (
    "precision", "recall", "f1", "boundary_mae_ms",
    "boundary_within_50ms_fraction", "false_alarm_rate",
    "matched_spans", "reference_spans", "nonfinite_count", "sample_count")
RIGHTS_FIELDS = (
    "dataset_terms_reference", "output_use_reference",
    "commercial_use_decision_reference", "review_reference",
    "claims_qualified")

HEX64 = re.compile(r"[0-9a-f]{64}")
SLUG = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
ABSOLUTE = re.compile(r"/[^\x00]+")
ASCII_TEXT = re.compile(r"[\x20-\x7e]{1,96}")


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
        rows[relative] = {"sha256": expected, "actual": actual, "verified": True}
    return rows


def _board_document() -> dict:
    return read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)


def board_row_projection(board_path: Path, task: str = TASK) -> dict:
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in tasks if isinstance(row, dict) and row.get("id") == task]
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
        rows.append({field: copy.deepcopy(row.get(field)) for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(rows if rows is not None else linked_rows())).hexdigest()


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
            "kind": "candidate_dataset_model_or_recipe_path",
        })
    return rows


def external_absence_probes() -> list[dict]:
    rows = []
    for path in EXTERNAL_ABSENCE_PROBES:
        rows.append({
            "scope": "external",
            "path": path,
            "present": _present(_expanded(path)),
            "kind": "candidate_dataset_or_cache_path",
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
        "dataset_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


def source_presence() -> dict:
    note = "cpp-library/pipeline-validation/playback-speed-candidates.md"
    inventory = "audio-benchmark-platform/plan/INVENTORY.json"
    rows = []
    for relative, role in ((note, "candidate_licence_and_claim_note"),
                           (inventory, "podcastfillers_inventory_row")):
        path = AUDIO_ROOT / relative
        rows.append({
            "path": relative,
            "sha256": SOURCE_PINS[relative],
            "byte_count": path.stat().st_size,
            "role": role,
        })
    dataset = AUDIO_ROOT / "data/datasets/podcastfillers"
    annotations = AUDIO_ROOT / "data/annotations/podcastfillers"
    model = AUDIO_ROOT / "data/models/podcastfillers"
    return {
        "candidate_note_and_inventory_present": True,
        "dataset_present": dataset.exists(),
        "annotations_present": annotations.exists(),
        "model_or_runtime_present": model.exists(),
        "terms_bundle_present": False,
        "rights_review_present": False,
        "exact_dataset_terms_conjunction_present": False,
        "dataset_used": False,
        "audio_read": False,
        "model_executed": False,
        "provenance_rows": rows,
    }


def _require_substring(text: str, needle: str, code: str) -> None:
    if needle not in text:
        raise ValueError(code)


def recipe_provenance() -> dict:
    note_path = AUDIO_ROOT / "cpp-library/pipeline-validation/playback-speed-candidates.md"
    inventory_path = AUDIO_ROOT / "audio-benchmark-platform/plan/INVENTORY.json"
    note = note_path.read_text(encoding="utf-8")
    inventory = inventory_path.read_text(encoding="utf-8")
    checks = (
        (note,
         "| Non-commercial annotations | **No** as training data for a shipped model | Separate terms | PodcastFillers dataset |",
         "note_licence_table"),
        (note,
         "same applies to **PodcastFillers** annotations (non-commercial); the useful part is its pipeline (VAD + ASR + classifier), not its data.",
         "note_pipeline_not_data"),
        (note, "PodcastFillers-trained models (non-commercial annotations)",
         "note_do_not_start"),
        (note, "- PodcastFillers \u2014 <https://podcastfillers.github.io/> (annotations non-commercial)",
         "note_source_url"),
        (inventory, '"id": "podcastfillers"', "inventory_row"),
        (inventory, '"verification_profile": "rate"', "inventory_profile"),
        (inventory,
         "Annotate the documented rights scope and keep research dataset acquisition outside the SDK artifact.",
         "inventory_plan_note"),
    )
    for text, needle, code in checks:
        _require_substring(text, needle, code)
    return {
        "note_sha256": SOURCE_PINS["cpp-library/pipeline-validation/playback-speed-candidates.md"],
        "inventory_sha256": SOURCE_PINS["audio-benchmark-platform/plan/INVENTORY.json"],
        "checks_present": len(checks),
        "checks_required": len(checks),
        "source_url_recorded": PODCASTFILLERS_URL,
        "annotations_license_recorded": "non-commercial",
        "pipeline_note_recorded": PODCASTFILLERS_PIPELINE_NOTE,
        "recorded_only": True,
        "saved_run_artifacts": False,
        "executed_here": False,
    }


def documented_claims() -> dict:
    note_path = AUDIO_ROOT / "cpp-library/pipeline-validation/playback-speed-candidates.md"
    note = note_path.read_text(encoding="utf-8")
    checks = (
        "PodcastFillers dataset",
        "Non-commercial annotations",
        "**No** as training data for a shipped model",
        "PodcastFillers** annotations (non-commercial)",
        "VAD + ASR + classifier",
        "not its data",
        "PodcastFillers-trained models (non-commercial annotations)",
    )
    for needle in checks:
        _require_substring(note, needle, "documented_claim_missing")
    return {
        "source_path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "source_sha256": SOURCE_PINS["cpp-library/pipeline-validation/playback-speed-candidates.md"],
        "source_url_recorded": PODCASTFILLERS_URL,
        "annotations_license_recorded": "non-commercial",
        "pipeline_note_recorded": PODCASTFILLERS_PIPELINE_NOTE,
        "commercial_use_permitted": False,
        "dataset_identity_recorded": False,
        "dataset_digest_recorded": False,
        "terms_bundle_recorded": False,
        "measured_result_recorded": False,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
    }


def exact_models() -> dict:
    return {
        "podcastfillers_dataset": {
            "source_url_recorded": PODCASTFILLERS_URL,
            "annotations_license_recorded": "non-commercial",
            "dataset_present": False,
            "annotations_present": False,
            "version": None,
            "release_sha256": None,
            "byte_count": None,
            "terms_bundle_reviewed": False,
            "commercial_use_granted": False,
            "downloaded_or_reconstructed": False,
        },
        "pipeline_or_model": {
            "present": False,
            "description": PODCASTFILLERS_PIPELINE_NOTE,
            "source_revision": None,
            "weights_sha256": None,
            "runtime_lock_sha256": None,
            "executed": False,
        },
        "runtime": {
            "present": False,
            "python_version": None,
            "lockfile_sha256": None,
            "offline_load_verified": False,
        },
    }


def historical_recipe() -> dict:
    return {
        "candidate_note": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "source_url_recorded": PODCASTFILLERS_URL,
        "annotations_license_recorded": "non-commercial",
        "pipeline_note_recorded": PODCASTFILLERS_PIPELINE_NOTE,
        "dataset_acquired_here": False,
        "runtime_recipe_recorded": False,
        "scoring_recipe_recorded": False,
        "saved_run_artifacts": False,
        "executed_here": False,
    }


def _format_fraction(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 28
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal.quantize(Decimal("0.000001")), "f")


def _span(label: str, start_ms: int, end_ms: int) -> dict:
    return {"label": label, "start_ms": start_ms, "end_ms": end_ms}


SYNTHETIC_REFERENCE_SPANS = (
    _span("filler", 100, 300),
    _span("filler", 900, 1100),
    _span("filler", 2000, 2300),
)
SYNTHETIC_HYPOTHESIS_SPANS = (
    _span("filler", 110, 290),
    _span("filler", 2050, 2280),
    _span("filler", 3000, 3200),
)


def score_filler_spans(reference: list[dict], hypothesis: list[dict], tolerance_ms: int = 50) -> dict:
    for row in reference + hypothesis:
        if row.get("label") != "filler":
            raise ValueError("span_label")
        start = row.get("start_ms")
        end = row.get("end_ms")
        if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
            raise ValueError("span_time")
        if start < 0 or end < start or end > int(MAX_TIMING_MS):
            raise ValueError("span_time_range")
    matched_ref: set[int] = set()
    matched_hyp: set[int] = set()
    pairs: list[tuple[int, int, int]] = []
    for i, ref in enumerate(reference):
        for j, hyp in enumerate(hypothesis):
            dist = abs(ref["start_ms"] - hyp["start_ms"]) + abs(ref["end_ms"] - hyp["end_ms"])
            pairs.append((dist, i, j))
    pairs.sort()
    boundary_errors: list[int] = []
    for dist, i, j in pairs:
        if i in matched_ref or j in matched_hyp:
            continue
        ref = reference[i]
        hyp = hypothesis[j]
        start_err = abs(ref["start_ms"] - hyp["start_ms"])
        end_err = abs(ref["end_ms"] - hyp["end_ms"])
        if start_err <= tolerance_ms and end_err <= tolerance_ms:
            matched_ref.add(i)
            matched_hyp.add(j)
            boundary_errors.extend([start_err, end_err])
    tp = len(matched_ref)
    fp = len(hypothesis) - tp
    fn = len(reference) - tp
    precision = Fraction(tp, tp + fp) if (tp + fp) else Fraction(0, 1)
    recall = Fraction(tp, tp + fn) if (tp + fn) else Fraction(0, 1)
    f1 = Fraction(2 * precision * recall, precision + recall) if (precision + recall) else Fraction(0, 1)
    if boundary_errors:
        ordered = sorted(boundary_errors)
        count = len(ordered)
        middle = count // 2
        median = Fraction(ordered[middle]) if count % 2 else Fraction(ordered[middle - 1] + ordered[middle], 2)
        mae_text = _format_fraction(Fraction(sum(ordered), count))
        median_text = _format_fraction(median)
        within_text = _format_fraction(Fraction(sum(1 for e in ordered if e <= tolerance_ms), count))
    else:
        mae_text = median_text = within_text = "0.000000"
    return {
        "reference_spans": len(reference),
        "hypothesis_spans": len(hypothesis),
        "matched_spans": tp,
        "false_positive_spans": fp,
        "false_negative_spans": fn,
        "precision": _format_fraction(precision),
        "recall": _format_fraction(recall),
        "f1": _format_fraction(f1),
        "boundary_error_count": len(boundary_errors),
        "boundary_mae_ms": mae_text,
        "boundary_median_abs_error_ms": median_text,
        "boundary_within_50ms_fraction": within_text,
        "tolerance_ms": tolerance_ms,
    }


def scorer_control() -> dict:
    reference = [dict(r) for r in SYNTHETIC_REFERENCE_SPANS]
    hypothesis = [dict(r) for r in SYNTHETIC_HYPOTHESIS_SPANS]
    result = score_filler_spans(reference, hypothesis, tolerance_ms=50)
    expected = {
        "reference_spans": 3,
        "hypothesis_spans": 3,
        "matched_spans": 2,
        "false_positive_spans": 1,
        "false_negative_spans": 1,
        "precision": "0.666667",
        "recall": "0.666667",
        "f1": "0.666667",
        "boundary_error_count": 4,
        "boundary_mae_ms": "22.500000",
        "boundary_median_abs_error_ms": "15.000000",
        "boundary_within_50ms_fraction": "1.000000",
        "tolerance_ms": 50,
    }
    if result != expected:
        raise RuntimeError("scorer_control_mismatch")
    return {
        "id": "SCORE-CONTROL-01",
        "kind": "synthetic_filler_span_arithmetic",
        "synthetic": True,
        "label": "synthetic_filler_span_control_not_evidence",
        "reference_spans": len(reference),
        "hypothesis_spans": len(hypothesis),
        "result": result,
        "audio_read": False,
        "model_invoked": False,
        "runtime_imported": False,
        "qualifies": False,
    }


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


def _text(obj: dict, key: str, path: str, pattern: re.Pattern | None = None, max_length: int = 512) -> str:
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


def _number(obj: dict, key: str, path: str, minimum: float, maximum: float) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("number:" + path + "." + key)
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite:" + path + "." + key)
    if number < minimum or number > maximum:
        raise ValueError("range:" + path + "." + key)
    return number


def _boolean(obj: dict, key: str, path: str, expected: bool | None = None) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise ValueError("boolean:" + path + "." + key)
    if expected is not None and value is not expected:
        raise ValueError("value:" + path + "." + key)
    return value


def validate_manifest(manifest: dict) -> None:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("value:manifest.schema_id")
    _text(root, "cohort_id", "manifest", SLUG, 64)

    dataset = _exact_keys(root["dataset"], DATASET_FIELDS, "dataset")
    if dataset["name"] != "PodcastFillers":
        raise ValueError("value:dataset.name")
    _text(dataset, "source_url", "dataset", ABSOLUTE, 512)
    _text(dataset, "version", "dataset", None, 64)
    _text(dataset, "release_sha256", "dataset", HEX64, 64)
    _int(dataset, "byte_count", "dataset", 1, 1 << 40)
    _text(dataset, "license_id", "dataset", SLUG, 64)
    _text(dataset, "license_review_reference", "dataset", None, 1024)
    _boolean(dataset, "commercial_use_granted", "dataset", False)

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    for key in ("python", "model_name", "model_revision"):
        _text(runtime, key, "runtime", None, 64)
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
        _text(row, "sha256", path, HEX64, 64)
        _text(row, "language", path, SLUG, 16)
        _text(row, "speaker_group", path, SLUG, 64)
        if row["sample_rate_hz"] != SAMPLE_RATE_HZ:
            raise ValueError("value:" + path + ".sample_rate_hz")
        if row["channels"] != CHANNELS:
            raise ValueError("value:" + path + ".channels")
        _int(row, "samples", path, 1, MAX_AUDIO_SAMPLES)

    reference = _exact_keys(root["reference"], REFERENCE_FIELDS, "reference")
    _text(reference, "source", "reference", None, 64)
    _text(reference, "sha256", "reference", HEX64, 64)
    _int(reference, "annotator_count", "reference", 2, 8)
    _int(reference, "filler_span_count", "reference", 1, 100000)
    _boolean(reference, "has_nonfiller_controls", "reference", True)

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("length:controls")
    kinds = []
    control_ids = set()
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
    for key in ("precision", "recall", "f1", "boundary_within_50ms_fraction", "false_alarm_rate"):
        _number(outcomes, key, "outcomes", 0.0, 1.0)
    _number(outcomes, "boundary_mae_ms", "outcomes", 0.0, MAX_TIMING_MS)
    _int(outcomes, "matched_spans", "outcomes", 0, 100000)
    _int(outcomes, "reference_spans", "outcomes", 1, 100000)
    _int(outcomes, "nonfinite_count", "outcomes", 0, 0)
    _int(outcomes, "sample_count", "outcomes", COHORT_ITEM_COUNT, COHORT_ITEM_COUNT)

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for key in ("dataset_terms_reference", "output_use_reference",
                "commercial_use_decision_reference", "review_reference"):
        _text(rights, key, "rights", None, 1024)
    _boolean(rights, "claims_qualified", "rights", False)


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-control:" + label).encode()).hexdigest()


def control_manifest() -> dict:
    outcome = scorer_control()["result"]
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cohort_id": "synthetic-podcastfillers-annotation",
        "dataset": {
            "name": "PodcastFillers",
            "source_url": "/synthetic/dataset/podcastfillers",
            "version": "synthetic-v0",
            "release_sha256": _synthetic_digest("dataset"),
            "byte_count": 1048576,
            "license_id": "separate-terms-noncommercial",
            "license_review_reference": "synthetic://review/not-performed",
            "commercial_use_granted": False,
        },
        "runtime": {
            "python": "3.12.0",
            "model_name": "synthetic-filler-classifier",
            "model_revision": "synthetic-rev",
            "device": "cpu",
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
        },
        "audio": [
            {
                "id": "synthetic-filler-crop",
                "path": "/synthetic/audio/filler-16k-mono.wav",
                "sha256": _synthetic_digest("audio"),
                "language": "en",
                "speaker_group": "speaker-a",
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "samples": 160000,
            },
        ],
        "reference": {
            "source": "adjudicated-human-filler-annotation",
            "sha256": _synthetic_digest("reference"),
            "annotator_count": 2,
            "filler_span_count": outcome["reference_spans"],
            "has_nonfiller_controls": True,
        },
        "controls": [
            {"id": "control-second-annotator", "kind": "independent_second_annotator"},
            {"id": "control-nonfiller-speech", "kind": "nonfiller_speech_negative_control"},
            {"id": "control-silence-music", "kind": "silence_music_negative_control"},
        ],
        "outcomes": {
            "precision": 0.666667,
            "recall": 0.666667,
            "f1": 0.666667,
            "boundary_mae_ms": 15.0,
            "boundary_within_50ms_fraction": 1.0,
            "false_alarm_rate": 0.333333,
            "matched_spans": outcome["matched_spans"],
            "reference_spans": outcome["reference_spans"],
            "nonfinite_count": 0,
            "sample_count": COHORT_ITEM_COUNT,
        },
        "rights": {
            "dataset_terms_reference": "synthetic://rights/dataset",
            "output_use_reference": "synthetic://rights/output-use",
            "commercial_use_decision_reference": "synthetic://rights/no-commercial-grant",
            "review_reference": "synthetic://review/not-performed",
            "claims_qualified": False,
        },
    }


def admission_cases() -> list[dict]:
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

    def bool_as_int(document: dict) -> None:
        document["runtime"]["intra_op_threads"] = True

    def nonfinite_precision(document: dict) -> None:
        document["outcomes"]["precision"] = float("nan")

    mutations = [
        ("ADM-01", "missing_dataset", del_path(("dataset",))),
        ("ADM-02", "extra_top_level_field", extra_top_level),
        ("ADM-03", "wrong_schema_id", set_path(("schema_id",), "audio-sdk/other/0.1")),
        ("ADM-04", "cohort_id_not_slug", set_path(("cohort_id",), "Not A Slug")),
        ("ADM-05", "wrong_dataset_name", set_path(("dataset", "name"), "OtherDataset")),
        ("ADM-06", "empty_dataset_url", set_path(("dataset", "source_url"), "")),
        ("ADM-07", "short_release_sha", set_path(("dataset", "release_sha256"), "abc")),
        ("ADM-08", "zero_byte_count", set_path(("dataset", "byte_count"), 0)),
        ("ADM-09", "commercial_use_claimed", set_path(("dataset", "commercial_use_granted"), True)),
        ("ADM-10", "empty_license_review", set_path(("dataset", "license_review_reference"), "")),
        ("ADM-11", "missing_runtime_field", del_path(("runtime", "python"))),
        ("ADM-12", "cuda_device", set_path(("runtime", "device"), "cuda")),
        ("ADM-13", "bool_as_int_threads", bool_as_int),
        ("ADM-14", "offline_off", set_path(("runtime", "offline"), False)),
        ("ADM-15", "short_audio", lambda d: d["audio"].append(copy.deepcopy(d["audio"][0]))),
        ("ADM-16", "empty_audio", set_path(("audio",), [])),
        ("ADM-17", "relative_audio_path", set_path(("audio", 0, "path"), "audio.wav")),
        ("ADM-18", "wrong_sample_rate", set_path(("audio", 0, "sample_rate_hz"), 8000)),
        ("ADM-19", "stereo_audio", set_path(("audio", 0, "channels"), 2)),
        ("ADM-20", "too_many_samples", set_path(("audio", 0, "samples"), MAX_AUDIO_SAMPLES + 1)),
        ("ADM-21", "missing_reference", del_path(("reference",))),
        ("ADM-22", "single_annotator", set_path(("reference", "annotator_count"), 1)),
        ("ADM-23", "no_nonfiller_controls", set_path(("reference", "has_nonfiller_controls"), False)),
        ("ADM-24", "missing_control", lambda d: d["controls"].pop()),
        ("ADM-25", "duplicate_control_kind", duplicate_control_kind),
        ("ADM-26", "unknown_control_kind", set_path(("controls", 0, "kind"), "identity_passthrough")),
        ("ADM-27", "extra_control", lambda d: d["controls"].append({"id": "x", "kind": "independent_second_annotator"})),
        ("ADM-28", "precision_out_of_range", set_path(("outcomes", "precision"), 1.01)),
        ("ADM-29", "nonfinite_precision", nonfinite_precision),
        ("ADM-30", "negative_mae", set_path(("outcomes", "boundary_mae_ms"), -1.0)),
        ("ADM-31", "false_alarm_out_of_range", set_path(("outcomes", "false_alarm_rate"), 1.1)),
        ("ADM-32", "nonfinite_count_nonzero", set_path(("outcomes", "nonfinite_count"), 1)),
        ("ADM-33", "wrong_sample_count", set_path(("outcomes", "sample_count"), 2)),
        ("ADM-34", "missing_outcome_field", del_path(("outcomes", "f1"))),
        ("ADM-35", "missing_rights_field", del_path(("rights", "dataset_terms_reference"))),
        ("ADM-36", "empty_output_use", set_path(("rights", "output_use_reference"), "")),
        ("ADM-37", "empty_commercial_decision", set_path(("rights", "commercial_use_decision_reference"), "")),
        ("ADM-38", "qualified_claim", set_path(("rights", "claims_qualified"), True)),
        ("ADM-39", "extra_rights_field", set_path(("rights", "extra"), "x")),
        ("ADM-40", "missing_audio_field", del_path(("audio", 0, "samples"))),
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
        except Exception as error:  # pragma: no cover
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
            "rejected_count": sum(1 for case in cases if case["status"] == "rejected"),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "dataset_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


def build_contract() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    qualification = {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": True,
        "dataset_present": False,
        "annotations_present": False,
        "runtime_present": False,
        "model_present": False,
        "commercial_license_granted": False,
        "filler_detection_result": False,
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
    gates = [dict(gate, qualifies=False, linked_row=row) for gate in RELEASE_GATES]
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
            "dataset_acquired": False,
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
        "rate_profile_requirements": [dict(r) for r in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(r) for r in QUALITY_ROWS],
        "timing_requirements": [dict(r) for r in TIMING_ROWS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "dataset_fields": list(DATASET_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "audio_fields": list(AUDIO_FIELDS),
            "reference_fields": list(REFERENCE_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "outcome_fields": list(OUTCOME_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "cohort_item_count": COHORT_ITEM_COUNT,
            "max_audio_samples": MAX_AUDIO_SAMPLES,
            "dataset_name_required": "PodcastFillers",
            "commercial_use_must_be_false": True,
            "minimum_annotators": 2,
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "annotations_license_recorded": "non-commercial",
            "terms_bundle_reviewed": False,
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
                "No exact PodcastFillers dataset identity, version/commit, digest or complete terms bundle is staged.",
                "PodcastFillers annotations are recorded as non-commercial; no separate commercial/output-use decision exists.",
                "No rights-cleared audio/annotation subset exists in this worktree and acquisition remains outside the SDK artifact.",
                "No pinned offline runtime/model, lockfile or import digest exists.",
                "No reproduced filler detection/boundary/finite-output/baseline result exists.",
                "The task row's Rate profile is a mismatch for a dataset/annotation lead and remains blocked or waived only by review.",
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
            "sha256": board_row_digest(board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)),
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
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
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
    for key in ("real_result_present", "dataset_present", "annotations_present",
                "runtime_present", "model_present", "commercial_license_granted",
                "filler_detection_result", "boundary_result", "finite_output_result",
                "baseline_result", "device_timing_result", "rate_profile_result",
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
    if models.get("podcastfillers_dataset", {}).get("dataset_present") is not False:
        raise ValueError("contract_dataset")
    if models.get("podcastfillers_dataset", {}).get("commercial_use_granted") is not False:
        raise ValueError("contract_commercial")
    if models.get("runtime", {}).get("present") is not False:
        raise ValueError("contract_runtime")
    if contract.get("licensing", {}).get("commercial_use_granted") is not False:
        raise ValueError("contract_license_commercial")
