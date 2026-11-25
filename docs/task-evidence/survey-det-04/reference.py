# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-DET-04.

This module builds a bounded taxonomy/comparison evidence map for the
sound-event, vocal-event and scene-analysis category (inventory category
``DET-04``, legacy family ``F12``). It reads only pinned, read-only documents
from the enclosing ``audioml`` workspace and the SDK worktree. It does not load
audio, weights, runtimes, media or the network, and it does not register,
expose, enable or qualify any classifier, detector or processor.

All curated records below are documentation mappings, not new measurements.
Adjacent local values and source-reported candidate claims are transcribed
verbatim from the pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-DET-04"
TITLE = "Review coverage for Sound-event, vocal-event and scene analysis"
CATEGORY_ID = "DET-04"
LEGACY_FAMILY = "F12"
BRANCH = "swarm/SDK-SURVEY-DET-04"
BASE_COMMIT = "c4419d1ce9783b552d662bd7cd524b20ce48feaa"
PROFILE = "Analysis"
COMPONENT = "sound-vocal-event-and-scene-analysis-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
    "taxonomy",
)

# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media/weights that are not present in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "cpp-library/pipeline-validation/playback-speed/README.md": "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
}

# SDK-worktree-relative public-boundary and merged-evidence pins. They are read
# only to prove that no public surface was touched and to ground curated
# boundaries; no header, contract or report is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/analysis-events/README.md": "a3c65bf53b00288ff10d9c69e64ad93f1e919b74ba9697958cdc5a197b0d6dba",
    "docs/task-evidence/analysis-events/contract.json": "d2c3f276e48394a14270aa29de868ffc355870c91f0966bfb7bd10f7563ddd32",
    "docs/task-evidence/survey-cln-11/README.md": "6291bf2ef86c1e16ab89fe26348e9f594e2975d51a03b2cc3aed14401a3075d7",
    "docs/task-evidence/survey-det-01/README.md": "88430878409af7a5cdb74dbc4422724b78f4c0610463fed9d5d4f29d16fffacb",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Detection and control",
    "name": "Sound-event, vocal-event and scene analysis",
    "scope": "discovered_extension",
    "output_kind": "annotation/control",
    "purpose": "Recognize background events or vocal sounds to inform optional policies.",
    "method_families": {
        "classic": "Signal features and statistical classifiers",
        "ml": "Spectrogram classifiers and event detectors",
    },
    "input_output": "Audio \u2192 event labels/scores, optionally intervals",
    "live_or_comparison_boundary": (
        "Tagging and temporal detection differ. This entry does not resolve ACR. "
        "Laughter/backchannels need a preservation policy."
    ),
    "source_ids": ["S12", "S13", "S15"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "DET",
    "meaning": "Detection and control",
    "category_id": CATEGORY_ID,
    "labels_scores_and_optional_intervals_only": True,
    "tagging_and_temporal_detection_are_distinct": True,
    "does_not_resolve_acr": True,
    "laughter_and_backchannels_need_preservation_policy": True,
    "not_speech_activity_detection": "DET-01",
    "not_utterance_endpointing": "DET-02",
    "not_overlap_detection_or_speaker_count": "DET-03",
    "not_target_speaker_or_personalized_vad": "DET-05",
    "not_noise_suppression": "CLN-01",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S12",
        "title": "YAMNet sound-event classification",
        "url": "https://www.tensorflow.org/hub/tutorials/yamnet",
        "access_scope": "direct",
        "mapped_components": ["yamnet-onnx"],
        "gap_ids": ["G02", "G07"],
        "finding": (
            "Direct documentation lead for a spectrogram CNN that emits "
            "AudioSet-class scores. The inventory row is considered only: the "
            "pinned candidate note records a 0.96 s window / 0.48 s hop, "
            "Apache-2.0 code terms and CC BY 4.0 labels, and says the model is "
            "generic and not podcast-tuned. No ONNX file, weights, runtime, "
            "window/hop replay, event labels or accuracy result is present here."
        ),
    },
    {
        "source_id": "S13",
        "title": "AudioSet event ontology",
        "url": "https://research.google.com/audioset/ontology/",
        "access_scope": "direct",
        "mapped_components": ["yamnet-onnx"],
        "gap_ids": ["G04", "G07"],
        "finding": (
            "Direct ontology lead only. The hierarchy supplies label names and "
            "grouping, not annotations, audio, a detector or a policy. The "
            "pinned candidate note records CC BY 4.0 for the labels. Class "
            "granularity, co-occurrence, negative sampling, ontology revision "
            "and an event-to-policy mapping are not resolved by this task."
        ),
    },
    {
        "source_id": "S15",
        "title": "Microsoft DNS challenge and paralinguistic evaluation",
        "url": (
            "https://www.microsoft.com/en-us/research/academic-program/"
            "deep-noise-suppression-challenge-icassp-2023/"
        ),
        "access_scope": "direct",
        "mapped_components": ["zencastr-laughter-detection"],
        "gap_ids": ["G06", "G09"],
        "finding": (
            "Direct evaluation-protocol lead for paralinguistic and "
            "vocal-event assessment. It motivates a separate laughter, breath "
            "and backchannel preservation policy, but no local paralinguistic "
            "corpus, annotation set, scorer, listening panel or device-timing "
            "measurement follows from the challenge page."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Signal features and statistical classifiers",
        "components": [],
        "gap_ids": ["G01"],
        "status": "no_local_component_or_execution_in_reviewed_records",
        "boundary": (
            "The catalogued classic branch has no inventory component, "
            "hand-crafted feature extractor, GMM/SVM head or local execution; "
            "energy/spectral features are not by themselves a sound-event classifier."
        ),
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Spectrogram CNN audio tagging with an AudioSet label space (named source leads S12/S13)",
        "components": ["yamnet-onnx"],
        "gap_ids": ["G02", "G07"],
        "status": "candidate_only_no_local_execution",
        "boundary": (
            "Candidate row considered only: no ONNX weights, runtime, exact "
            "revision, window/hop replay, label mapping or event score exists "
            "in this task. Clip-level tagging does not provide event intervals."
        ),
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Single-event vocal-event detection (laughter)",
        "components": ["zencastr-laughter-detection"],
        "gap_ids": ["G03", "G06"],
        "status": "candidate_only_no_local_execution",
        "boundary": (
            "Candidate row considered only: the pinned note records a "
            "single-event model, MIT base encoder and close-mic conversational "
            "scope, but window/hop, real-time cost, false alarms on speech and "
            "weight terms are unmeasured and unstaged."
        ),
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Temporal event detection and boundary localization",
        "components": [],
        "gap_ids": ["G04", "G05"],
        "status": "no_local_component_or_execution_in_reviewed_records",
        "boundary": (
            "No component turns event tags into onset/offset intervals, and no "
            "event-boundary scorer or labelled interval set exists. This is the "
            "tagging-versus-temporal-detection gap the category names."
        ),
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Adjacent multi-purpose audio-tagging host",
        "components": ["sherpa-onnx"],
        "gap_ids": ["G08"],
        "status": "candidate_only_no_local_execution",
        "boundary": (
            "sherpa-onnx is a host with an audio-tagging surface, not a selected "
            "event model. Each bundled model has its own terms, and no tagging "
            "model, runtime or event result is staged here."
        ),
    },
    {
        "family_id": "MF-M5",
        "branch": "ml",
        "family": "Adjacent vocal-event frame classifiers for disfluency",
        "components": [
            "wavlm-acoustic-disfluency-model",
            "speechbrain-disfluency-pause-predictor",
        ],
        "gap_ids": ["G10"],
        "status": "adjacent_inference_smoke_and_blocked",
        "boundary": (
            "Disfluency is a vocal-event subcase, not laughter or scene "
            "analysis. The WavLM row has a one-crop inference smoke without "
            "aligned labels or a supplied license; the SpeechBrain row is blocked."
        ),
    },
    {
        "family_id": "MF-M6",
        "branch": "ml",
        "family": "Restricted annotation and label sources",
        "components": ["crisperwhisper", "podcastfillers"],
        "gap_ids": ["G07"],
        "status": "rights_restricted_annotation_only",
        "boundary": (
            "Non-commercial weights or annotations can at most serve as an "
            "offline annotation lead under their terms; they are not runtime "
            "event detectors, staged assets or a rights basis."
        ),
    },
]

# component_id, task and evidence_status are checked against plan/INVENTORY.json.
# Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "yamnet-onnx", "evidence_status": "considered", "task": "SDK-YAMNET-ONNX"},
    {"component_id": "zencastr-laughter-detection", "evidence_status": "considered", "task": "SDK-ZENCASTR-LAUGHTER-DETECTION"},
    {"component_id": "sherpa-onnx", "evidence_status": "considered", "task": "SDK-SHERPA-ONNX"},
    {"component_id": "wavlm-acoustic-disfluency-model", "evidence_status": "partial", "task": "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL"},
    {"component_id": "speechbrain-disfluency-pause-predictor", "evidence_status": "blocked", "task": "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR"},
    {"component_id": "crisperwhisper", "evidence_status": "considered", "task": "SDK-CRISPERWHISPER"},
    {"component_id": "podcastfillers", "evidence_status": "considered", "task": "SDK-PODCASTFILLERS"},
    {"component_id": "vosk-small-en-us-0-15-playback-gate", "evidence_status": "partial", "task": "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "YAMNet ONNX candidate row and the 521-class AudioSet label space",
        "class": "source_reported_audio_tagging_candidate",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Documentation only: 0.96 s window / 0.48 s hop and Apache-2.0 / CC BY 4.0 terms are recorded from the note; no weights, runtime, replay or event accuracy exists.",
    },
    {
        "id": "CI-2",
        "input": "AudioSet event ontology hierarchy and label names",
        "class": "source_reported_event_ontology",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "An ontology is not a detector or annotation set; class granularity, co-occurrence, negatives and ontology revision are unpinned.",
    },
    {
        "id": "CI-3",
        "input": "Zencastr laughter-detection candidate row",
        "class": "source_reported_vocal_event_candidate",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Single-event, close-mic conversational scope; window/hop, real-time cost and laugh false alarms on speech are explicitly unmeasured.",
    },
    {
        "id": "CI-4",
        "input": "Microsoft DNS challenge and paralinguistic evaluation lead",
        "class": "source_reported_paralinguistic_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Protocol context only; no paralinguistic corpus, labels, scorer, listening panel or local result is staged.",
    },
    {
        "id": "CI-5",
        "input": "Merged typed-analysis-event contract and model-free fixture",
        "class": "adjacent_foundation_event_contract",
        "source_pin": "docs/task-evidence/analysis-events/README.md",
        "boundary": "Proposed speech, rate and transcript event kinds with exact intervals, clocks and explicit unknown/invalid validity; no sound-event or scene label kind and no classifier accuracy.",
    },
    {
        "id": "CI-6",
        "input": "Adjacent WavLM acoustic-disfluency inference smoke on one 4 s AMI crop",
        "class": "adjacent_vocal_event_inference_smoke",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "Adjacent vocal-event subcase only; 199 frame outputs and 180 ms model-only CPU on one crop, no aligned labels, no supplied license and no accuracy.",
    },
    {
        "id": "CI-7",
        "input": "Adjacent Vosk small-en-us-0.15 ASR content-gate pre-screen on three clips",
        "class": "adjacent_content_gate_historical_local",
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
        "boundary": "Adjacent speech/filler content gate; two exact TTS labels and one unreferenced AMI stitch; batch gate call, not block streaming and not event tagging.",
    },
    {
        "id": "CI-8",
        "input": "Missing DET-04 event/scene cohort, frozen label ontology, interval scorer and matched benchmark",
        "class": "missing_det04_event_cohort",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Absence is recorded as missing, not as a negative result; no event, scene, laughter or backchannel accuracy claim follows.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "always-event and always-no-event diagnostics",
        "role": "Required degenerate controls that expose metric behavior for any future event or interval score; not run and not product candidates.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-2",
        "name": "identity / no-event stream",
        "role": "A stream with no emitted labels preserves PCM and is the baseline against which any event decision must justify itself.",
        "source_pin": "docs/task-evidence/analysis-events/README.md",
    },
    {
        "id": "CT-3",
        "name": "speech-activity baseline (Silero or WebRTC VAD)",
        "role": "Adjacent speech/non-speech control only; speech activity is not a sound-event, laughter or scene label.",
        "source_pin": "docs/task-evidence/survey-det-01/README.md",
    },
    {
        "id": "CT-4",
        "name": "unknown-region masking",
        "role": "Unlabelled or unannotated time is unknown and is never relabelled as a no-event negative.",
        "source_pin": "docs/task-evidence/analysis-events/README.md",
    },
    {
        "id": "CT-5",
        "name": "clip-tag versus interval-detection separation",
        "role": "A clip-level tag and a timestamped event interval answer different questions; neither may be scored as the other.",
        "source_pin": "audio_categories.md",
    },
    {
        "id": "CT-6",
        "name": "preserved PCM identity",
        "role": "Event labels and scores are advisory; they never gate, mute, delete, time-scale or otherwise alter audio in this map.",
        "source_pin": "docs/task-evidence/analysis-events/README.md",
    },
    {
        "id": "CT-7",
        "name": "label-space control",
        "role": "The 521-class AudioSet ontology and a single-event laughter head are not interchangeable; scores cannot be compared without a frozen mapping.",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "YAMNet ONNX candidate (S12)",
        "class": "external_documentation_and_candidate",
        "status": "Apache-2.0 and AudioSet-label CC BY 4.0 claims recorded from the pinned note; no ONNX file, weights, exact revision or runtime staged",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
    },
    {
        "asset": "AudioSet event ontology (S13)",
        "class": "external_documentation_and_labels",
        "status": "Label vocabulary and hierarchy only; no annotations, audio or split is staged, and label terms do not grant media rights",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Zencastr laughter-detection candidate",
        "class": "external_documentation_and_candidate",
        "status": "MIT base-encoder claim recorded from the pinned note; no weights, window/hop setting, runtime or laughter labels staged",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
    },
    {
        "asset": "Microsoft DNS challenge and paralinguistic evaluation page (S15)",
        "class": "external_documentation",
        "status": "Evaluation-protocol documentation only; no corpus, paralinguistic labels, scorer or listening items",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Adjacent WavLM acoustic-disfluency checkpoint",
        "class": "research_model_unlicensed",
        "status": "Third-party repo and checkpoint with no supplied license; inference smoke only and not a rights basis",
        "source_pin": "research/tsm-followup-20261101/README.md",
    },
    {
        "asset": "Rights-qualified sound-event, vocal-event and scene corpus with annotations",
        "class": "missing",
        "status": "Not present; absence is explicit and is not an empty negative set",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "WavLM disfluency inference smoke on a 4 s AMI crop",
        "outcome_class": "adjacent_vocal_event_historical_local",
        "component_ids": ["wavlm-acoustic-disfluency-model"],
        "source_pin": "research/tsm-followup-20261101/README.md",
        "values": {
            "crop_seconds": 4,
            "frame_outputs": 199,
            "model_only_cpu_ms": 180,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent filled-pause/repetition/revision frame-classifier smoke on "
            "one crop; no aligned AMI labels, no supplied license and no "
            "accuracy or event-boundary measurement; not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Vosk small-en-us-0.15 ASR content-gate pre-screen",
        "outcome_class": "adjacent_content_gate_historical_local",
        "component_ids": ["vosk-small-en-us-0-15-playback-gate"],
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
        "values": {
            "clips": 3,
            "blocks": 15708,
            "deadline_misses": 0,
            "gate_rtf": 0.056,
            "duration_error_min_ms": -6.0,
            "duration_error_max_ms": 30.0,
            "gate_share_percent": 98.0,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent ASR/word-boundary content gate on three clips, two with "
            "exact TTS labels and one AMI stitch without reference; speech and "
            "filler policy only, batch gate call, not block streaming, not "
            "sound-event tagging or temporal event detection; not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "YAMNet ONNX is a 521-class AudioSet spectrogram classifier with a 0.96 s window / 0.48 s hop and permissive code/label terms",
        "class": "source_reported_event_candidate",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Candidate note only; no weights, runtime, replay, label mapping, event intervals or accuracy is verified here, and a generic model is not a podcast-tuned detector.",
    },
    {
        "id": "RO-2",
        "claim": "AudioSet supplies a hierarchical event ontology and label names",
        "class": "source_reported_event_candidate",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Ontology documentation only; it does not supply annotations, audio, negatives, a split or a detector.",
    },
    {
        "id": "RO-3",
        "claim": "Zencastr laughter-detection is a single-event, close-mic conversational model with an MIT base encoder",
        "class": "source_reported_event_candidate",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Candidate note only; window/hop, real-time cost, false alarms on speech and per-weight terms are unmeasured and unstaged.",
    },
    {
        "id": "RO-4",
        "claim": "The Microsoft DNS challenge page motivates paralinguistic and vocal-event evaluation",
        "class": "source_reported_paralinguistic_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Protocol context only; no local corpus, labels, scorer, listening panel or device measurement follows.",
    },
    {
        "id": "RO-5",
        "claim": "CrisperWhisper and PodcastFillers expose laughter/filler annotations or tags under restrictive terms",
        "class": "source_reported_restricted_annotation",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Non-commercial weights or annotations can be an offline annotation lead only; they are not runtime detectors, staged assets or a rights basis.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "timestamped_probabilities_and_event_boundaries": "No DET-04 event-score or event-boundary execution exists; adjacent WavLM and Vosk rows expose only coarse frame or word-boundary outputs",
        "known_positives_and_negatives": "No event corpus or annotation set is staged; always-event/no-event and identity controls are specified but not run",
        "onset_offset_delay": "No event onset/offset labels, collar or delay distribution exists for any event class",
        "stratified_fn_fp": "No within-class FN/FP, laughter-on-speech false-alarm or quiet/overlap strata exist",
        "validity_vs_nonspeech": "Unlabelled time is unknown, never a no-event negative; the merged analysis-events contract keeps unknown and invalid explicit",
        "exact_source_intervals": "The analysis-events foundation fixes half-open sample intervals and exact cross-hop overlap, but no event detector populates them",
        "independent_state": "Window, hop, lookahead and streaming state are unpinned for YAMNet and Zencastr; no event-detector state test exists",
        "availability_and_dropped_stale_events": "No event availability clock, drop audit or stale-event handling is measured; the foundation contract only defines required fields",
        "cross_hop_behavior": "A 0.96 s / 0.48 s candidate cadence and unknown Zencastr cadence are not aligned to 160-sample v0 frames; no parity is claimed",
    },
    "blocked": [
        "Rights-qualified sound-event, vocal-event and scene corpus with explicit annotated and unknown regions",
        "Frozen ontology revision, class mapping, negative sampling and speaker/session-disjoint partitions",
        "Matched always-event, no-event, identity and speech-activity controls with onset/offset, FN/FP and uncertainty evidence",
        "Pinned real event-model runtimes, weights and exact revisions with per-weight terms",
        "Paced streaming window/hop/state, lookahead and target-device availability, memory and deadline evidence",
        "Laughter/backchannel preservation policy with independent review",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "adjacent_vocal_event_historical_local": True,
    "adjacent_content_gate_historical_local": True,
    "adjacent_event_contract_fixture": True,
    "source_reported_event_candidate": True,
    "source_reported_paralinguistic_protocol": True,
    "det04_local_event_execution": False,
    "audio_tagging_execution": False,
    "temporal_event_detection_execution": False,
    "scene_analysis_execution": False,
    "real_event_corpus": False,
    "preservation_policy_evaluated": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "clean_reference_accuracy_claim": False,
}

# True evidence classes must be backed by at least one row class; false classes
# must not be backed. This keeps a missing result from being promoted.
CLASS_BACKING: Dict[str, List[str]] = {
    "adjacent_vocal_event_historical_local": ["adjacent_vocal_event_historical_local"],
    "adjacent_content_gate_historical_local": ["adjacent_content_gate_historical_local"],
    "adjacent_event_contract_fixture": ["adjacent_foundation_event_contract"],
    "source_reported_event_candidate": [
        "source_reported_audio_tagging_candidate",
        "source_reported_event_ontology",
        "source_reported_vocal_event_candidate",
    ],
    "source_reported_paralinguistic_protocol": ["source_reported_paralinguistic_protocol"],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Create or select a classic-feature sound-event classifier and evaluate it on a frozen labelled cohort",
        "evidence_gap": "The catalogued classic branch (signal features and statistical classifiers) has no inventory component, feature extractor, GMM/SVM head, execution or result; the category is catalogued with candidate census and benchmark not_started.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-04 classic-feature component or feasibility task exists; the linked foundation and evidence-manifest rows own evidence and cohort rules, not a sound-event classifier.",
    },
    {
        "id": "G02",
        "actionable_gap": "Pin and run YAMNet ONNX with an exact revision, label mapping, window/hop and matched controls",
        "evidence_gap": "The YAMNet row is considered only; no ONNX file, weights, runtime, exact revision, 0.96 s / 0.48 s replay, output schema or event/tag score exists.",
        "follow_up_ids": ["SDK-YAMNET-ONNX"],
        "feasibility_task_exists": True,
        "owner_note": "The YAMNet ONNX feasibility row is a scoping lead only; it is not enabled, installed or qualified by this map.",
    },
    {
        "id": "G03",
        "actionable_gap": "Pin and run the Zencastr laughter detector and measure window/hop, cost and false alarms on speech",
        "evidence_gap": "The Zencastr row is considered only; the pinned note explicitly leaves window/hop and real-time cost unmeasured, and no weights, labels, threshold sweep or laugh-on-speech false-alarm result exists.",
        "follow_up_ids": ["SDK-ZENCASTR-LAUGHTER-DETECTION"],
        "feasibility_task_exists": True,
        "owner_note": "The Zencastr laughter-detection feasibility row is a scoping lead only; no model is staged, enabled or qualified.",
    },
    {
        "id": "G04",
        "actionable_gap": "Resolve scene analysis and ACR as separate tasks with their own labels, ontology and scorer",
        "evidence_gap": "The category name includes scene analysis and the boundary says this entry does not resolve ACR, but no scene/ACR component, corpus, label set, scorer or execution exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated scene-analysis or ACR component or feasibility task was found; the linked evidence rows own manifests and evidence rules, not a scene capability.",
    },
    {
        "id": "G05",
        "actionable_gap": "Add temporal event detection with onset/offset labels, exact intervals and an event-boundary scorer",
        "evidence_gap": "No component turns event tags into intervals, and there is no labelled interval set, collar, boundary delay distribution or event-level FN/FP measurement; tagging and temporal detection remain undifferentiated.",
        "follow_up_ids": [
            "SDK-FND-ANALYSIS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated temporal-event component exists; the linked foundation and research-control rows own event intervals and scorer design, not event detection.",
    },
    {
        "id": "G06",
        "actionable_gap": "Define and evaluate a laughter and backchannel preservation policy before any event-conditioned action",
        "evidence_gap": "The catalogued boundary requires a preservation policy, but no local policy, preservation target, listening item or false-suppression measurement exists for laughter or backchannels.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-04 preservation-policy owner exists; the linked research-control and foundation rows own preservation scoring and evidence rules, not a laughter policy.",
    },
    {
        "id": "G07",
        "actionable_gap": "Freeze the ontology revision, label mapping, negative sampling and label rights",
        "evidence_gap": "AudioSet labels and a single-event laughter head are not interchangeable; class granularity, co-occurrence, negative sampling, ontology revision and label terms are unpinned, and restricted annotation sources cannot be runtime.",
        "follow_up_ids": [
            "SDK-YAMNET-ONNX",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked candidate and manifest rows are scoping leads for label mapping and rights metadata; neither freezes a DET-04 ontology or grants label rights.",
    },
    {
        "id": "G08",
        "actionable_gap": "Stage weights and runtimes with exact revisions and per-weight terms for every event candidate",
        "evidence_gap": "YAMNet, Zencastr and the adjacent tagging host have no staged weights or exact runtime; per-model terms differ, and no candidate revision or artifact digest is pinned.",
        "follow_up_ids": [
            "SDK-YAMNET-ONNX",
            "SDK-ZENCASTR-LAUGHTER-DETECTION",
            "SDK-SHERPA-ONNX",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility and evidence-manifest rows are scoping leads; no weight is staged, no term is cleared and no runtime is enabled.",
    },
    {
        "id": "G09",
        "actionable_gap": "Measure paced window/hop/state, lookahead and target-device availability, memory and deadlines",
        "evidence_gap": "Only a batch ASR-gate pre-screen and a one-crop model-only CPU value exist; no event-model callback path, window cadence, lookahead, memory or deadline distribution is measured.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-04 timing feasibility row was found; the foundation rows own lifecycle, timing and evidence-acceptance rules.",
    },
    {
        "id": "G10",
        "actionable_gap": "Obtain labelled vocal-event data and clear terms for the adjacent disfluency classifier",
        "evidence_gap": "The WavLM disfluency row has one unlabelled 4 s crop inference smoke and no supplied license; the SpeechBrain row is blocked with no matching checkpoint.",
        "follow_up_ids": [
            "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL",
            "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked implementation and feasibility rows are leads for a vocal-event subcase; no aligned labels, license or product candidate is established.",
    },
    {
        "id": "G11",
        "actionable_gap": "Keep event labels separate from muting, ACR, source separation, target-speaker selection and content deletion",
        "evidence_gap": "A sound-event or laughter label is not permission to remove, mute or time-scale audio; overlap detection, noise suppression and target-speaker VAD are distinct catalogued tasks.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-03",
            "SDK-SURVEY-CLN-01",
            "SDK-SURVEY-DET-05",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No single component owns both an event label and an audio-mutating decision; the linked taxonomy rows keep overlap, suppression and target-speaker tasks separate.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-YAMNET-ONNX", "title": "YAMNet ONNX", "mode": "feasibility"},
    {"task_id": "SDK-ZENCASTR-LAUGHTER-DETECTION", "title": "Zencastr laughter-detection", "mode": "feasibility"},
    {"task_id": "SDK-SHERPA-ONNX", "title": "sherpa-onnx", "mode": "feasibility"},
    {"task_id": "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL", "title": "WavLM acoustic disfluency model", "mode": "implementation"},
    {"task_id": "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR", "title": "SpeechBrain disfluency/pause predictor", "mode": "feasibility"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-FND-ANALYSIS", "title": "Typed analysis events and composition taps", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-SURVEY-DET-03", "title": "Review coverage for Overlapping speech detection and speaker count", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-CLN-01", "title": "Review coverage for Background noise suppression", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-DET-05", "title": "Review coverage for Target-speaker / personalized VAD", "mode": "taxonomy"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified sound-event, vocal-event and scene corpus with explicit annotated and unknown regions"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen ontology revision, class mapping, negative sampling and speaker/session-disjoint partitions with independent label review"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched always-event, no-event, identity and speech-activity controls with onset/offset, FN/FP and uncertainty evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned real event-model runtimes, weights and exact revisions with per-weight terms"},
    {"id": "RG-05", "blocked": True, "requirement": "Paced streaming window/hop/state, lookahead and target-device availability, memory and deadline evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Laughter/backchannel preservation policy and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **DET-04 \u2014 Sound-event, vocal-event and scene analysis** |",
        "Tagging and temporal detection differ. This entry does not resolve ACR. Laughter/backchannels need a preservation policy.",
    ],
    "research/category_survey/sources.md": [
        "| S12 | [YAMNet sound-event classification](https://www.tensorflow.org/hub/tutorials/yamnet) | analysis | direct |",
        "| S13 | [AudioSet event ontology](https://research.google.com/audioset/ontology/) | analysis | direct |",
        "| S15 | [Microsoft DNS challenge and paralinguistic evaluation](https://www.microsoft.com/en-us/research/academic-program/deep-noise-suppression-challenge-icassp-2023/) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Analysis | Score timestamped probabilities, event boundaries and detections.",
    ],
    "cpp-library/pipeline-validation/playback-speed-candidates.md": [
        "| Laughter/non-speech events | **YAMNet ONNX** | Apache-2.0 | 521 AudioSet classes, ONNX, 0.96 s window / 0.48 s hop | Generic event model, not podcast-tuned; AudioSet labels CC BY 4.0 |",
        "| Laughter, podcast domain | **Zencastr laughter-detection** | MIT | Close-mic conversational speech, ONNX, MIT base encoder | Single-event model; window/hop and real-time cost need measuring |",
        "No local build or benchmark of pbshift, sherpa-onnx, Vosk, Moonshine, YAMNet, Zencastr laughter, speech-rate-meter or findsylls.",
        "3. **S3 \u2014 laughter/noise:** add an audio-event classifier (verify its model licence separately).",
    ],
    "cpp-library/pipeline-validation/playback-speed/README.md": [
        "- **0 deadline misses in 15 708 blocks** across all runs.",
        "- Gate alone: **0.056\u00d7 real time** wall and CPU (batch call, not block streaming).",
        "- `D1` / `D2` outputs stay within **\u22126 ms to +30 ms** of the source duration on",
    ],
    "research/tsm-followup-20261101/README.md": [
        "**Inference smoke only.** Loaded all checkpoint keys; 4 s AMI crop, 199 frame outputs, CPU model-only 180 ms, positive outputs on repetition and partial-word labels. No aligned AMI labels to score, and neither repo nor checkpoint supplies a license.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/analysis-events/README.md": [
        "This closes only the versioned contract/fixture question. It does not qualify",
        "Audio bytes and digest remain unchanged after analysis publication.",
        "Known events require finite values and availability; unknown",
    ],
    "docs/task-evidence/survey-det-01/README.md": [
        "Keep speech-activity detection separate from muting, endpointing, turn",
    ],
}

BOUNDARY: Dict[str, bool] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "provider_registration": False,
    "processor_exposure": False,
    "descriptor_registry_changed": False,
    "public_api_abi_changed": False,
    "installed_v0_changed": False,
    "shared_cmakelists_changed": False,
    "ci_changed": False,
    "board_changed": False,
    "handoff_changed": False,
    "provider_intake_complete": False,
    "release_approval": False,
}

SCOPE: Dict[str, bool] = {
    "task_local_only": True,
    "documentation_and_metadata_only": True,
    "no_new_execution": True,
    "synthetic_only_where_cited": True,
    "real_speech": False,
    "real_corpus": False,
    "weights": False,
    "runtime_invocation": False,
    "listening": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
    "audio_mutation_or_deletion": False,
    "acr_resolution": False,
    "scene_analysis_claim": False,
}

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "scene_or_acr_claim_without_component": "rejected; state unchanged",
    "temporal_detection_claim_from_clip_tag": "rejected; state unchanged",
}


class MapError(ValueError):
    """Raised when a pin, input, mapping record or scope rule fails closed."""


def _reject_constant(token: str) -> None:
    raise MapError("nonfinite JSON constant is not allowed: " + token)


def _object_pairs(pairs: Iterable[tuple]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise MapError("non-string JSON key")
        if key in result:
            raise MapError("duplicate JSON key: " + key)
        result[key] = value
    return result


def strict_json_loads(text: str) -> Any:
    """Parse JSON with duplicate keys and NaN/Infinity rejected."""
    if not isinstance(text, str):
        raise MapError("JSON text must be str")
    return json.loads(text, object_pairs_hook=_object_pairs, parse_constant=_reject_constant)


def strict_json_load(path: Path) -> Any:
    """Read and strict-parse a UTF-8 JSON file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapError("cannot read JSON: %s" % path) from exc
    return strict_json_loads(text)


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON bytes: sorted keys, minimal separators, trailing LF."""
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise MapError("value is not canonical JSON: %s" % exc) from exc
    return (text + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except OSError as exc:
        raise MapError("cannot hash file: %s" % path) from exc
    return digest.hexdigest()


def task_dir() -> Path:
    return Path(__file__).resolve().parent


def find_workspace(explicit: Optional[str] = None) -> Path:
    """Locate the enclosing audioml workspace without writing to it."""
    if explicit:
        root = Path(explicit).resolve()
    else:
        env = os.environ.get("AUDIOML_WORKSPACE_ROOT")
        if env:
            root = Path(env).resolve()
        else:
            here = Path(__file__).resolve()
            candidates = [here.parent] + list(here.parents)
            root = None
            for candidate in candidates:
                if (
                    (candidate / "research/category_registry.json").is_file()
                    and (candidate / "audio-benchmark-platform/plan/INVENTORY.json").is_file()
                ):
                    root = candidate
                    break
            if root is None:
                raise MapError("workspace root not found; set AUDIOML_WORKSPACE_ROOT")
    if not (root / "research/category_registry.json").is_file():
        raise MapError("workspace marker missing: research/category_registry.json")
    if not (root / "audio-benchmark-platform/plan/INVENTORY.json").is_file():
        raise MapError("workspace marker missing: audio-benchmark-platform/plan/INVENTORY.json")
    return root


def find_sdk_root(explicit: Optional[str] = None) -> Path:
    """Locate the SDK worktree containing this task directory."""
    if explicit:
        root = Path(explicit).resolve()
    else:
        here = Path(__file__).resolve()
        root = None
        for candidate in [here.parent] + list(here.parents):
            if (candidate / "CONTRACTS.md").is_file() and (candidate / "REUSE.toml").is_file():
                root = candidate
                break
        if root is None:
            raise MapError("SDK worktree root not found")
    if not (root / "CONTRACTS.md").is_file():
        raise MapError("SDK marker missing: CONTRACTS.md")
    return root


def _validate_pin_map(pins: Mapping[str, str], label: str) -> None:
    if not isinstance(pins, Mapping):
        raise MapError(label + " pins must be a mapping")
    for path, digest in pins.items():
        if not isinstance(path, str) or not path or Path(path).is_absolute():
            raise MapError(label + " pin path is invalid")
        if ".." in Path(path).parts:
            raise MapError(label + " pin path traverses: " + path)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise MapError(label + " pin digest is invalid: " + path)


def _check_document_pins(workspace: Path, sdk_root: Path) -> None:
    _validate_pin_map(SOURCE_PINS, "source")
    _validate_pin_map(WORKTREE_PINS, "worktree")
    for relative, expected in SOURCE_PINS.items():
        actual = sha256_file(workspace / relative)
        if actual != expected:
            raise MapError("source pin mismatch: %s" % relative)
    for relative, expected in WORKTREE_PINS.items():
        actual = sha256_file(sdk_root / relative)
        if actual != expected:
            raise MapError("worktree pin mismatch: %s" % relative)


def _check_anchors(workspace: Path, sdk_root: Path) -> None:
    for relative, anchors in DOC_ANCHORS.items():
        text = (workspace / relative).read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                raise MapError("pinned document anchor missing: %s :: %s" % (relative, anchor))
    for relative, anchors in WORKTREE_DOC_ANCHORS.items():
        text = (sdk_root / relative).read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                raise MapError("worktree document anchor missing: %s :: %s" % (relative, anchor))


def _check_taxonomy(workspace: Path) -> None:
    registry = strict_json_load(workspace / "research/category_registry.json")
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    registry_hit = [c for c in registry["categories"] if c.get("id") == CATEGORY_ID]
    inventory_hit = [c for c in inventory["taxonomy"] if c.get("id") == CATEGORY_ID]
    if len(registry_hit) != 1 or len(inventory_hit) != 1:
        raise MapError("DET-04 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("DET-04 taxonomy mismatch: %s" % key)
    source_index = {s["id"]: s for s in registry["sources"]}
    for lead in SOURCE_LEADS:
        source = source_index.get(lead["source_id"])
        if source is None:
            raise MapError("registry source lead is missing: " + lead["source_id"])
        for key in ("title", "url", "access_scope"):
            if source.get(key) != lead[key]:
                raise MapError("source lead mismatch: %s/%s" % (lead["source_id"], key))


def _check_backlog(workspace: Path) -> None:
    backlog = strict_json_load(workspace / "research/task_backlog.json")
    hits = [
        e
        for e in backlog["entries"]
        if e.get("family_id") == LEGACY_FAMILY and e.get("category_id") == CATEGORY_ID
    ]
    if len(hits) != 1:
        raise MapError("legacy family F12 / DET-04 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "discovered_extension",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F12/DET-04/%s" % key)


def _check_component_census(workspace: Path) -> None:
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    by_id = {c["id"]: c for c in inventory["components"]}
    for row in COMPONENT_CENSUS:
        component = by_id.get(row["component_id"])
        if component is None:
            raise MapError("inventory component missing: " + row["component_id"])
        if component.get("task") != row["task"]:
            raise MapError("inventory task mismatch: " + row["component_id"])
        if component.get("evidence_status") != row["evidence_status"]:
            raise MapError("inventory evidence_status mismatch: " + row["component_id"])
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))


def _check_historical_execution_components() -> None:
    known = {row["component_id"] for row in COMPONENT_CENSUS}
    for row in HISTORICAL_EXECUTIONS:
        ids = row.get("component_ids")
        if not ids:
            raise MapError("historical execution has no component link: " + row["id"])
        missing = sorted(set(ids) - known)
        if missing:
            raise MapError(
                "historical execution links an uncensused component: %s/%s"
                % (row["id"], ",".join(missing))
            )
        if row.get("adjacent") is not True or row.get("not_component_evidence") is not True:
            raise MapError("historical execution is not labelled adjacent: " + row["id"])
        if "not rerun by this survey" not in row.get("scope", ""):
            raise MapError("historical execution scope is not bounded: " + row["id"])


def _check_evidence_classes() -> None:
    observed = set()
    for row in COMPARISON_INPUTS:
        observed.add(row["class"])
    for row in HISTORICAL_EXECUTIONS:
        observed.add(row["outcome_class"])
    for row in REPORTED_OUTCOMES:
        observed.add(row["class"])
    for key, value in EVIDENCE_CLASSES.items():
        backed = bool(observed & set(CLASS_BACKING.get(key, [])))
        if value is True and not backed:
            raise MapError("supported evidence class has no mapped row: " + key)
        if value is False and backed:
            raise MapError("evidence class is contradicted by a mapped row: " + key)
    critical_false = {
        "det04_local_event_execution",
        "audio_tagging_execution",
        "temporal_event_detection_execution",
        "scene_analysis_execution",
        "real_event_corpus",
        "preservation_policy_evaluated",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "clean_reference_accuracy_claim",
    }
    for key in critical_false:
        if EVIDENCE_CLASSES.get(key) is not False:
            raise MapError("unsupported evidence class is not false: " + key)


def _board_projection(board: Mapping[str, Any]) -> str:
    rows = [
        {"id": task["id"], "mode": task["mode"], "title": task["title"]}
        for task in board["tasks"]
        if task.get("id") in {link["task_id"] for link in BOARD_LINKS}
    ]
    rows.sort(key=lambda row: row["id"])
    return sha256_bytes(canonical_bytes(rows))


def _check_board(workspace: Path) -> str:
    board = strict_json_load(workspace / BOARD_PATH)
    if not isinstance(board.get("tasks"), list):
        raise MapError("board tasks is not a list")
    by_id = {t["id"]: t for t in board["tasks"]}
    for link in BOARD_LINKS:
        task = by_id.get(link["task_id"])
        if task is None:
            raise MapError("linked board task is missing: " + link["task_id"])
        if task.get("title") != link["title"] or task.get("mode") != link["mode"]:
            raise MapError("linked board task identity changed: " + link["task_id"])
        if link["mode"] not in ALLOWED_LINK_MODES:
            raise MapError("linked board task has an unexpected mode: " + link["task_id"])
    known = {link["task_id"] for link in BOARD_LINKS}
    link_ids = {gap["id"] for gap in GAPS}
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
        if gap.get("feasibility_task_exists"):
            modes = {next(t["mode"] for t in BOARD_LINKS if t["task_id"] == tid) for tid in gap["follow_up_ids"]}
            if "feasibility" not in modes:
                raise MapError("gap claims a feasibility follow-up without one: " + gap["id"])
        elif not gap.get("owner_note"):
            raise MapError("gap without feasibility task has no owner note: " + gap["id"])
    for source in SOURCE_LEADS:
        for gap_id in source["gap_ids"]:
            if gap_id not in link_ids:
                raise MapError("source lead links unknown gap: " + gap_id)
    for family in METHOD_FAMILIES:
        for gap_id in family["gap_ids"]:
            if gap_id not in link_ids:
                raise MapError("method family links unknown gap: " + gap_id)
    return _board_projection(board)


def _build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    ws = find_workspace(workspace)
    sdk = find_sdk_root(sdk_root)
    _check_document_pins(ws, sdk)
    _check_anchors(ws, sdk)
    _check_taxonomy(ws)
    _check_backlog(ws)
    _check_component_census(ws)
    _check_historical_execution_components()
    _check_evidence_classes()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
    by_id = {t["id"]: t for t in board["tasks"]}
    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
        task = by_id[link["task_id"]]
        linked_gaps = sorted(g["id"] for g in GAPS if link["task_id"] in g["follow_up_ids"])
        links.append(
            {
                "task_id": link["task_id"],
                "title": link["title"],
                "mode": link["mode"],
                "linked_gaps": linked_gaps,
            }
        )

    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "category_id": CATEGORY_ID,
        "legacy_family": LEGACY_FAMILY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "readiness": READINESS,
            "survey_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "category_scope": dict(CATEGORY_SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "legacy_backlog": {
            "family_id": LEGACY_FAMILY,
            "activation_state": "catalogued",
            "state": "catalogued",
            "next_action": "Plan discovery across required source buckets",
            "source_pin": "research/task_backlog.json",
        },
        "source_leads": [dict(lead) for lead in SOURCE_LEADS],
        "method_families": [dict(family) for family in METHOD_FAMILIES],
        "component_census": [dict(row) for row in COMPONENT_CENSUS],
        "comparison_inputs": [dict(row) for row in COMPARISON_INPUTS],
        "controls": [dict(row) for row in CONTROLS],
        "assets": [dict(row) for row in ASSETS],
        "historical_executions": [dict(row) for row in HISTORICAL_EXECUTIONS],
        "reported_outcomes": [dict(row) for row in REPORTED_OUTCOMES],
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "acceptance_profile": dict(ACCEPTANCE_PROFILE),
        "gaps": [dict(gap) for gap in GAPS],
        "board_links": links,
        "board_link_projection_sha256": board_digest,
        "mutable_provenance": {
            "gate": False,
            "path": BOARD_PATH,
            "note": "Board status is mutable and the file is never hashed into canonical bytes; only id/title/mode of linked rows are gated by board_link_projection_sha256.",
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(WORKTREE_PINS),
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "adverse_rejections": dict(ADVERSE_REJECTIONS),
        "reproduction": {
            "comparison": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py report",
            "sources": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py sources",
            "contract": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py contract",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
        },
    }
    # Final fail-closed disposition checks; no gate may be weakened.
    if report["decision"] != DECISION:
        raise MapError("decision changed")
    if report["status"] != STATUS or report["qualification"]["survey_status"] != "incomplete":
        raise MapError("status changed")
    if report["qualification"]["status"] != QUALIFICATION_STATUS:
        raise MapError("qualification changed")
    if report["qualification"]["readiness"] != READINESS:
        raise MapError("readiness changed")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count is not eight")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if any(row.get("adjacent") is not True for row in report["historical_executions"]):
        raise MapError("a historical execution is not labelled adjacent")
    if report["scope"]["scene_analysis_claim"] is not False:
        raise MapError("scene analysis is claimed")
    if report["scope"]["acr_resolution"] is not False:
        raise MapError("ACR is claimed")
    canonical_bytes(report)
    return report


class EvidenceMap:
    """Atomic holder for the built map; rejected input never changes state."""

    def __init__(self) -> None:
        self.state: Optional[Dict[str, Any]] = None

    def snapshot(self) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.state)

    def build(
        self,
        workspace: Optional[str] = None,
        sdk_root: Optional[str] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build the report; validate an optional caller payload atomically."""
        if payload is not None:
            if not isinstance(payload, Mapping):
                raise MapError("payload must be a mapping")
            for key, value in payload.items():
                if not isinstance(key, str) or not isinstance(value, (str, int, float, bool, type(None))):
                    raise MapError("invalid payload entry: %s" % key)
                if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
                    raise MapError("nonfinite payload value: %s" % key)
        candidate = _build_report(workspace=workspace, sdk_root=sdk_root)
        self.state = candidate
        return candidate


def build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    """Return a fresh canonical report without mutating any module state."""
    return _build_report(workspace=workspace, sdk_root=sdk_root)
