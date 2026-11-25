# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-DET-05.

This module builds a bounded taxonomy/comparison evidence map for the
target-speaker / personalized-VAD category (inventory category ``DET-05``,
legacy family ``F05``). It reads only pinned, read-only documents from the
enclosing ``audioml`` workspace and the SDK worktree. It does not load audio,
weights, runtimes, media or the network, and it does not register, expose,
enable or qualify any detector.

Curated values are transcribed from pinned documents and labelled with their
original scope. None of them is a personalized-VAD execution, an enrollment-
conditioned accuracy result, a listening result, a device measurement, a
benchmark or a release decision.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-DET-05"
TITLE = "Review coverage for Target-speaker / personalized VAD"
CATEGORY_ID = "DET-05"
LEGACY_FAMILY = "F05"
BRANCH = "swarm/SDK-SURVEY-DET-05"
BASE_COMMIT = "c4419d1ce9783b552d662bd7cd524b20ce48feaa"
PROFILE = "Analysis"
COMPONENT = "target-speaker-personalized-vad-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

# Modes that may appear on a linked board row. "taxonomy" is allowed because
# sibling surveys are the correct owner for cross-category boundaries; no new
# task id is invented and no mode is inferred.
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
    "REALTIME_COMPONENT_CANDIDATES.md": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/vad-research/chaining-evaluation.md": "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/omissions_review.md": "9a62fbce90afe84b9d0a9d248f5b72a9b168783533d5cfd8fa3d82d2dea01147",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/plans/F02/vad_accuracy_contract.md": "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
    "research/plans/F02/vad_sources.md": "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md": "d9285694209a54b26db0aa89a27a11b004fa0159d7ee08fc5fff0728c0869545",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/findings.md": "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
}

# SDK-worktree-relative public-boundary and merged-sibling pins. They are read
# only to prove that no public surface was touched and to ground the survey in
# merged evidence; no header, report or component is copied or edited.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/survey-cln-11/README.md": "6291bf2ef86c1e16ab89fe26348e9f594e2975d51a03b2cc3aed14401a3075d7",
    "docs/task-evidence/survey-det-01/README.md": "88430878409af7a5cdb74dbc4422724b78f4c0610463fed9d5d4f29d16fffacb",
    "docs/task-evidence/survey-det-01/report.json": "93e4488ece1ce06b5cbb37bb57f9241161cfd97d68ad3bab09c9a998e5e549bf",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Detection and control",
    "name": "Target-speaker / personalized VAD",
    "scope": "discovered_extension",
    "output_kind": "annotation/control",
    "purpose": "Detect activity of a selected speaker without extracting a waveform.",
    "method_families": {
        "classic": "Standard VAD plus speaker-scoring pipeline baseline",
        "ml": "Speaker-conditioned neural activity classification",
    },
    "input_output": (
        "Mixture + enrolled/reference speaker cue \u2192 "
        "target/non-target/non-speech frame scores or intervals"
    ),
    "live_or_comparison_boundary": (
        "Not source separation or a mandate to mute; measure target false "
        "rejection and changing speakers."
    ),
    "source_ids": ["S52", "S53"],
    "related_category_ids": ["DET-01", "SPK-02", "SPK-05"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "DET",
    "meaning": "Detection and control",
    "category_id": CATEGORY_ID,
    "target_speaker_activity_only": True,
    "requires_enrolled_or_reference_speaker_cue": True,
    "not_general_any_speaker_vad_category": "DET-01",
    "not_target_speaker_extraction_category": "SPK-02",
    "not_speaker_representation_identification_or_verification_category": "SPK-05",
    "not_overlapping_speech_or_speaker_count_category": "DET-03",
    "note": (
        "General speech activity (DET-01), target-speaker extraction and "
        "personalized enhancement (SPK-02), speaker representation, "
        "identification and verification (SPK-05) and overlapping-speech / "
        "speaker-count analysis (DET-03) are separate catalogued categories. "
        "They are named only to prevent scope inflation; their rows are not "
        "pooled into a DET-05 personalized-VAD claim."
    ),
}

PERSONAL_VAD_BOUNDARY: Dict[str, Any] = {
    "target_speaker_activity_only": True,
    "three_way_classes_required": True,
    "enrollment_or_reference_cue_required": True,
    "not_source_separation": True,
    "not_mute_or_gate_mandate": True,
    "not_speaker_identification_or_verification": True,
    "not_general_any_speaker_vad": True,
    "not_diarization_or_speaker_change_truth": True,
    "changing_speakers_and_target_false_rejection_are_material_strata": True,
    "enrollment_condition_must_travel_with_every_number": True,
    "author_reported_numbers_are_not_local": True,
    "pcm_output_is_identity_where_a_waveform_is_emitted": True,
    "compatible_checkpoint_or_weights_staged": False,
    "enrolled_mixture_or_clean_target_reference_staged": False,
    "personal_vad_local_execution_present": False,
    "device_timing_measured": False,
    "listening_or_human_validation_result": False,
    "benchmark_or_release_qualification_present": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S52",
        "title": "Personal VAD primary paper",
        "url": "https://research.google/pubs/personal-vad-speaker-conditioned-voice-activity-detection/",
        "access_scope": "direct",
        "mapped_components": [
            "voicefilter-lite-personal-vad",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G02", "G04", "G05"],
        "finding": (
            "Direct documentation lead for speaker-conditioned voice activity "
            "detection with target-speaker, other-speaker and non-speech frame "
            "scores. The paper's method, enrollment assumptions and author-"
            "reported numbers are reviewed only as a protocol; no checkpoint, "
            "runtime, enrolled mixture or local execution is present, and no "
            "accuracy is transferred from the paper."
        ),
    },
    {
        "source_id": "S53",
        "title": "Personal VAD existing reproduction and checkpoint leads",
        "url": "https://github.com/wq2012/personal_vad",
        "access_scope": "direct README; no execution/checkpoint access",
        "mapped_components": ["voicefilter-lite-personal-vad"],
        "gap_ids": ["G02", "G09"],
        "finding": (
            "README-level reproduction and external-checkpoint lead only. No "
            "compatible checkpoint was retrieved, no license review was "
            "completed and no code was executed; the repository does not "
            "establish a runnable or eligible personal-VAD candidate."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "Standard VAD plus independent speaker-scoring pipeline baseline "
            "(enroll, score each speech frame, threshold)"
        ),
        "components": [
            "silero-vad-6-2-3-reference",
            "webrtc-vad",
            "resemblyzer-speaker-similarity-proxy",
            "speechbrains-ecapa-speaker-similarity",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G03", "G04", "G05"],
        "status": "catalogued_baseline_not_executed_as_personal_vad",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Statistical speaker segmentation or BIC change detection used as "
            "a target-turn proxy"
        ),
        "components": ["bayesian-information-criterion-speaker-segmentation"],
        "gap_ids": ["G08"],
        "status": "considered_only_no_personal_vad_truth",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Speaker-conditioned neural activity classification (Personal VAD "
            "family; target / other-speech / non-speech frame scores)"
        ),
        "components": [
            "voicefilter-lite-personal-vad",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G02", "G05", "G09"],
        "status": "blocked_no_checkpoint_or_enrollment_conditioned_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": (
            "Speaker-conditioned neural extraction used only as an adjacent "
            "activity or target-dominance proxy"
        ),
        "components": [
            "voicefilter",
            "target-speaker-extraction-family",
            "hush",
        ],
        "gap_ids": ["G07", "G09"],
        "status": "adjacent_suppression_only_not_personal_vad",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": (
            "Neural diarization or segmentation supplying speaker turns without "
            "an enrolled target cue"
        ),
        "components": ["pyannote-diarization", "pyannote-segmentation-vad"],
        "gap_ids": ["G08"],
        "status": "considered_or_blocked_turn_labels_are_not_target_activity",
    },
]

ADJACENT_BOUNDARIES: List[Dict[str, str]] = [
    {
        "category_id": "DET-01",
        "name": "Speech activity detection (VAD/SAD)",
        "relationship": "Any-speaker speech activity is a front end or comparator, never target-speaker truth.",
        "source_pin": "docs/task-evidence/survey-det-01/README.md",
    },
    {
        "category_id": "SPK-02",
        "name": "Target-speaker extraction and personalized enhancement",
        "relationship": "A waveform extractor must not be relabelled as a target-activity decision.",
        "source_pin": "audio_categories.md",
    },
    {
        "category_id": "SPK-05",
        "name": "Speaker representation, identification and verification",
        "relationship": "Enrollment embeddings and identity scores are inputs or controls, not activity truth.",
        "source_pin": "audio_categories.md",
    },
    {
        "category_id": "DET-03",
        "name": "Overlapping speech detection and speaker count",
        "relationship": "Overlap and speaker-count labels are a stress stratum, not a target/non-target class.",
        "source_pin": "audio_categories.md",
    },
]

# component_id and task/evidence_status are checked against plan/INVENTORY.json.
# Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "fixed-rms-vad", "evidence_status": "evaluated", "task": "SDK-FIXED-RMS-VAD"},
    {"component_id": "adaptive-energy-vad", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-ENERGY-VAD"},
    {"component_id": "webrtc-vad", "evidence_status": "evaluated", "task": "SDK-WEBRTC-VAD"},
    {"component_id": "speexdsp-vad", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-VAD"},
    {"component_id": "fast-vad-0-2-1", "evidence_status": "evaluated", "task": "SDK-FAST-VAD-0-2-1"},
    {"component_id": "earshot-1-2-2", "evidence_status": "evaluated", "task": "SDK-EARSHOT-1-2-2"},
    {"component_id": "silero-vad-6-2-3-reference", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-6-2-3-REFERENCE"},
    {"component_id": "silero-vad-v5-onnx-reference", "evidence_status": "source-local", "task": "SDK-SILERO-VAD-V5-ONNX-REFERENCE"},
    {"component_id": "rnnoise-speech-probability", "evidence_status": "partial", "task": "SDK-RNNOISE-SPEECH-PROBABILITY"},
    {"component_id": "pyannote-segmentation-vad", "evidence_status": "blocked", "task": "SDK-PYANNOTE-SEGMENTATION-VAD"},
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "resemblyzer-speaker-similarity-proxy", "evidence_status": "partial", "task": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"},
    {"component_id": "speechbrains-ecapa-speaker-similarity", "evidence_status": "partial", "task": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY"},
    {"component_id": "bayesian-information-criterion-speaker-segmentation", "evidence_status": "considered", "task": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION"},
    {"component_id": "voicefilter", "evidence_status": "blocked", "task": "SDK-VOICEFILTER"},
    {"component_id": "voicefilter-lite-personal-vad", "evidence_status": "blocked", "task": "SDK-VOICEFILTER-LITE-PERSONAL-VAD"},
    {"component_id": "target-speaker-extraction-family", "evidence_status": "blocked", "task": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"},
    {"component_id": "hush", "evidence_status": "partial", "task": "SDK-HUSH"},
    {"component_id": "vadtoolkit-and-ami-scoring-tooling", "evidence_status": "partial", "task": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING"},
    {"component_id": "si-sdr-sdr-and-snr", "evidence_status": "evaluated", "task": "SDK-SI-SDR-SDR-AND-SNR"},
    {"component_id": "stoi-estoi", "evidence_status": "evaluated", "task": "SDK-STOI-ESTOI"},
]

DEDICATED_PERSONAL_VAD_COMPONENTS = (
    "voicefilter-lite-personal-vad",
    "voicefilter",
    "target-speaker-extraction-family",
)
ANY_SPEAKER_VAD_COMPONENTS = (
    "fixed-rms-vad",
    "adaptive-energy-vad",
    "webrtc-vad",
    "speexdsp-vad",
    "fast-vad-0-2-1",
    "earshot-1-2-2",
    "silero-vad-6-2-3-reference",
    "silero-vad-v5-onnx-reference",
    "rnnoise-speech-probability",
)

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Three speaker-disjoint held-out AMI Mix-Headset meetings scored by seven any-speaker VADs",
        "class": "historical_local_any_speaker_vad_baseline",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "boundary": "Any-speaker speech/nonspeech only; no target cue, no speaker identity, no target/other-speech class; a comparator for a classifier that does not exist here.",
    },
    {
        "id": "CI-2",
        "input": "EARS 30-pair primary/background synthetic mixture screen at +12/+18/+24 dB SIR",
        "class": "historical_local_adjacent_speaker_dominant_suppression",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "boundary": "EARS has no speaker metadata and Hush accepts no enrollment prompt; distinct recordings are not verified distinct speakers, so this is not speaker discrimination or target-activity truth.",
    },
    {
        "id": "CI-3",
        "input": "AMI ES2004a seven directed speaker pairs at +12/+18/+24 dB target-over-masker SIR",
        "class": "historical_local_adjacent_speaker_dominant_suppression",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "boundary": "Constructed non-overlap turns from one mono meeting mix without isolated references or an enrollment prompt; speaker-dominant proxies, not natural overlap or personalized VAD.",
    },
    {
        "id": "CI-4",
        "input": "In-model speaker-similarity cosines from voice-conversion evaluations (OpenVoice 0.890; MeanVC2 0.669 and 0.702)",
        "class": "historical_local_in_model_speaker_similarity_diagnostic",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "Encoder-specific diagnostics for conversion identity; they are not activity scores, do not measure target false rejection and cannot be compared across different encoders.",
    },
    {
        "id": "CI-5",
        "input": "Personal VAD paper/reproduction leads and the Interspeech 2024 three-class protocol",
        "class": "source_only_personal_vad_protocol",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Method and protocol descriptions only; no paper checkpoint, no staged LibriSpeech/MUSAN mixture and no author number is treated as a local result.",
    },
    {
        "id": "CI-6",
        "input": "REAL-PS4 target-speaker activity labels and the Open Yap discovery lead",
        "class": "source_reported_dataset_lead",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Utterance clips expose target-speaker labels but not continuous recording truth; terms, label provenance and any split require independent review and nothing is staged.",
    },
    {
        "id": "CI-7",
        "input": "Enrolled-speaker mixture corpus with clean target reference, target/other/nonspeech labels and a speaker-disjoint split",
        "class": "missing_enrollment_conditioned_corpus",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Absent. No such corpus, consent record, enrollment cue, clean reference or held-out partition exists in the reviewed material; the gap is recorded rather than filled.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "always-target, always-other-speech and always-nonspeech diagnostics", "role": "Required degenerate three-class controls that expose metric behavior; not product candidates.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
    {"id": "CT-2", "name": "generic any-speaker VAD baseline (Silero and WebRTC)", "role": "Shows what plain speech activity already achieves; a comparator, never target-speaker truth.", "source_pin": "reports/vad-research/chaining-evaluation.md"},
    {"id": "CT-3", "name": "VAD plus independent speaker-scoring baseline", "role": "The catalogued classic pipeline; it must be built and matched before any neural claim.", "source_pin": "research/category_registry.json"},
    {"id": "CT-4", "name": "target-absent and impostor-only negatives", "role": "Required to measure false target acceptance; absent from every reviewed execution.", "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv"},
    {"id": "CT-5", "name": "enrollment-duration and channel-mismatch sensitivity", "role": "Enrollment length, noise and channel must travel with the score; no local sweep exists.", "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"},
    {"id": "CT-6", "name": "speaker-change and overlap strata", "role": "Changing speakers and overlapping speech are explicit stress strata, not unknown time relabelled nontarget.", "source_pin": "research/plans/F02/vad_sources.md"},
    {"id": "CT-7", "name": "unknown-region masking", "role": "Unannotated or invalid time is excluded, never scored as non-target or nonspeech.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
    {"id": "CT-8", "name": "preserved PCM identity", "role": "A DET-05 decision annotates; it does not mute, gate or alter audio in any local fixture.", "source_pin": "audio_categories.md"},
    {"id": "CT-9", "name": "task-matched scorer controls for adjacent extraction", "role": "SI-SDR and STOI may describe an adjacent suppressor but cannot substitute for target-activity labels.", "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Personal VAD primary paper (S52)",
        "class": "external_documentation",
        "status": "Direct documentation scope; no checkpoint, runtime, enrollment cue or local execution",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Personal VAD reproduction repository (S53)",
        "class": "external_code_lead",
        "status": "README-level lead; no compatible checkpoint retrieved, license unreviewed, no execution",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "EARS blind audio, 30 target plus 30 masker recordings selected from 743 files",
        "class": "research_audio",
        "status": "CC BY-NC 4.0 per the cited record; no speaker metadata and not redistributed in this task",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "asset": "AMI ES2004a Mix-Headset mono meeting with participant turn labels",
        "class": "research_audio",
        "status": "CC BY 4.0; one 17.49-minute mono mix, no isolated participant tracks and no enrollment cue",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "asset": "REAL-PS4 target-speaker activity labels and Open Yap discovery lead",
        "class": "source_and_metadata_only",
        "status": "Not staged; utterance-level target labels are not continuous truth and terms are unreviewed",
        "source_pin": "research/plans/F02/vad_sources.md",
    },
    {
        "asset": "Interspeech 2024 personalized-VAD protocol (synthetic LibriSpeech concatenations plus MUSAN)",
        "class": "source_reported_protocol",
        "status": "Protocol description only; no audio, enrollment split or scorer is staged",
        "source_pin": "research/plans/F02/vad_sources.md",
    },
    {
        "asset": "Compatible Personal VAD or VoiceFilter-Lite checkpoint and runtime",
        "class": "missing_model_artifact",
        "status": "Absent; no weights, exact revision, license or runtime is present in this task",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "Enrolled-speaker mixture corpus with clean target references",
        "class": "missing_corpus",
        "status": "Absent; no consent, enrollment audio, clean target waveform or speaker-disjoint split exists",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Hush EARS primary/background synthetic mixture screen",
        "outcome_class": "historical_local_adjacent_speaker_dominant_suppression",
        "component_ids": ["hush", "si-sdr-sdr-and-snr", "stoi-estoi"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "values": {
            "source_pairs": 30,
            "mixtures": 90,
            "sir_db": [12, 18, 24],
            "hush_target_masker_gain_db": [8.14, 8.08, 8.46],
            "hush_target_si_sdr_delta_db": [-9.33, -14.54, -20.23],
            "hush_target_stoi_delta": [-0.141, -0.176, -0.197],
            "deepfilternet3_target_si_sdr_delta_db": [-8.73, -14.23, -19.92],
            "deepfilternet3_target_stoi_delta": [-0.172, -0.196, -0.212],
            "hush_mean_transform_rtf": 0.0278,
            "hush_observed_delay_ms": 10,
        },
        "scope": (
            "Adjacent primary/background suppression only: EARS has no speaker "
            "metadata, the pairs are distinct recordings rather than verified "
            "distinct speakers, and the exact Hush API accepts no enrollment "
            "prompt. It raises the target/masker ratio while damaging the "
            "designated target, so it is not target-speaker extraction, not "
            "personalized VAD, not a physical-device or listening result, and "
            "not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Hush AMI speaker-dominant turn-mixture diagnostic",
        "outcome_class": "historical_local_adjacent_speaker_dominant_suppression",
        "component_ids": ["hush", "si-sdr-sdr-and-snr", "stoi-estoi"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "values": {
            "directed_speaker_pairs": 7,
            "mixtures": 21,
            "sir_db": [12, 18, 24],
            "hush_target_si_sdr_delta_db": [-13.17, -18.41, -24.18],
            "hush_target_stoi_delta": [-0.193, -0.200, -0.207],
            "hush_target_masker_ratio_gain_db": [3.70, 7.33, 3.37],
            "ratio_gain_ci_includes_zero": True,
            "hush_mean_transform_rtf": 0.0292,
            "meeting_minutes": 17.49,
        },
        "scope": (
            "Adjacent suppression diagnostic only: one AMI mono mix, seven "
            "constructed non-overlap directed pairs, no isolated references "
            "and no enrollment prompt. Positive ratio changes have intervals "
            "that include zero, so speaker separation is not established; not "
            "personalized VAD, not natural overlap, not a device result, and "
            "not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Seven-candidate held-out AMI any-speaker VAD comparison",
        "outcome_class": "historical_local_any_speaker_vad_baseline",
        "component_ids": [
            "webrtc-vad",
            "silero-vad-6-2-3-reference",
            "fast-vad-0-2-1",
            "earshot-1-2-2",
            "speexdsp-vad",
            "adaptive-energy-vad",
            "fixed-rms-vad",
        ],
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "values": {
            "heldout_meetings": 3,
            "scored_frame_ms": 20,
            "web_rtc_fn_percent": 7.31,
            "web_rtc_fp_percent": 49.54,
            "silero_fn_percent": 19.43,
            "silero_fp_percent": 8.20,
            "fast_vad_fn_percent": 17.20,
            "fast_vad_fp_percent": 25.21,
            "earshot_fn_percent": 24.32,
            "earshot_fp_percent": 10.30,
            "speexdsp_fn_percent": 2.45,
            "speexdsp_fp_percent": 77.03,
            "adaptive_energy_fn_percent": 33.15,
            "adaptive_energy_fp_percent": 21.58,
            "rms_fn_percent": 62.95,
            "rms_fp_percent": 25.35,
        },
        "scope": (
            "Any-speaker VAD baseline on three speaker-disjoint held-out AMI "
            "meetings projected onto 20 ms frames. These rows identify speech, "
            "not a selected speaker's activity, and contain no enrollment cue, "
            "target/other-speech class or impostor control. They are a "
            "comparator for a personal-VAD classifier that does not exist here, "
            "not personalized-VAD evidence, not a device or broad natural-call "
            "result, and not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Personal VAD paper distinguishes target, other-speaker and non-speech frame scores under speaker conditioning",
        "class": "source_reported_personal_vad_protocol",
        "source_pin": "research/category_survey/omissions_review.md",
        "boundary": "Method and class definition only; no paper checkpoint, dataset revision, enrollment cue or local number is verified here.",
    },
    {
        "id": "RO-2",
        "claim": "Personal VAD reproduction repository is an implementation and external-checkpoint lead",
        "class": "source_reported_reproduction_lead",
        "source_pin": "research/category_survey/omissions_review.md",
        "boundary": "README-level lead; source execution, compatible checkpoint retrieval and eligibility remain unverified.",
    },
    {
        "id": "RO-3",
        "claim": "VoiceFilter-Lite / personal VAD row has no deployable local checkpoint and no enrolled-speaker mixtures",
        "class": "source_reported_candidate_gap",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "A recorded blocker, not a capability claim; no model, weight or enrollment-conditioned score is staged.",
    },
    {
        "id": "RO-4",
        "claim": "Interspeech 2024 personalized-VAD task uses three classes and synthetic LibriSpeech concatenations plus MUSAN noise with EER and utterance latency",
        "class": "source_reported_protocol",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "A different task and protocol from conversational any-speaker VAD; no audio, split, scorer or author number is reproduced.",
    },
    {
        "id": "RO-5",
        "claim": "REAL-PS4 exposes target-speaker activity labels for clipped overlapping utterances",
        "class": "source_reported_dataset_lead",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Utterance clips are not continuous recording truth; label provenance, license and split need independent review and nothing is downloaded.",
    },
    {
        "id": "RO-6",
        "claim": "Original VoiceFilter weights and runtime are not open; third-party substitutes are separate candidates",
        "class": "source_reported_candidate_gap",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "No exact original artifact can be run fairly; a substitute would be a different candidate with its own hash, license and result.",
    },
]

EXECUTION_COVERAGE: Dict[str, Any] = {
    "historical_execution_count": 3,
    "historical_local_any_speaker_vad_execution_count": 1,
    "historical_local_adjacent_suppression_execution_count": 2,
    "personal_vad_local_execution_count": 0,
    "speaker_conditioned_neural_execution_count": 0,
    "enrollment_conditioned_execution_count": 0,
    "target_label_benchmark_execution_count": 0,
    "dedicated_personal_vad_component_count": len(DEDICATED_PERSONAL_VAD_COMPONENTS),
    "locally_evaluated_personal_vad_component_count": 0,
    "any_speaker_vad_component_count": len(ANY_SPEAKER_VAD_COMPONENTS),
    "adjacent_suppression_component_count": 1,
    "missing_enrollment_conditioned_corpus": True,
    "missing_checkpoint_or_weights": True,
    "missing_target_label_benchmark": True,
    "missing_benchmark_scorer": True,
    "note": (
        "No dedicated DET-05 component has a local execution. The only "
        "historical rows are two adjacent speaker-dominant suppression "
        "diagnostics and one any-speaker VAD baseline; none supplies an "
        "enrolled target cue, a target/other/nonspeech label set, an impostor "
        "control or a personalized-VAD score."
    ),
}

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "timestamped_probabilities_and_events": "No personalized-VAD posterior or interval exists; HE-3 transcribes any-speaker frame decisions and HE-1/HE-2 transcribe adjacent suppression scores",
        "quiet_and_active_speech": "CI-1/CI-3 include active and idle/other-speaker regions, but no quiet target-speech stratum is labelled for DET-05",
        "known_positives_and_negatives": "CI-7 is the missing enrolled corpus; target-absent and impostor negatives do not exist in any reviewed execution",
        "onset_offset_delay": "HE-3 transcribes any-speaker onset/offset delays; HE-1 records a 10 ms adjacent waveform delay; neither is target-activity latency",
        "stratified_fn_fp": "Only any-speaker recording-level and adjacent SIR strata exist; target false rejection, impostor acceptance and enrollment-length strata are absent",
        "validity_vs_nonspeech": "CT-7; unknown or invalid time is never relabelled non-target or nonspeech",
        "exact_source_intervals": "HE-3 uses exact 20 ms scored frames; no target-label interval or enrollment window is staged",
        "independent_state": "No personalized-VAD session or stateful enrollment cache exists to test",
        "availability_and_dropped_stale_events": "No DET-05 runtime, callback path or event stream exists",
        "cross_hop_behavior": "160-sample v0 geometry versus any-speaker native cadences is an adjacent engineering boundary only; no parity is claimed",
        "three_way_confusion": "target/other-speech/nonspeech confusion, EER and target false-rejection are specified but unmeasured",
    },
    "blocked": [
        "Rights-qualified enrolled-speaker mixture corpus with clean target references, target/other/nonspeech labels and consent",
        "Frozen speaker-disjoint development and held-out partitions with independent label and identity review",
        "Matched degenerate, any-speaker VAD, VAD-plus-scoring, target-absent and impostor controls with EER, target false rejection, false acceptance and uncertainty",
        "Pinned real personal-VAD checkpoint, exact revision, license and runtime with safe fallback",
        "Enrollment-duration, channel-mismatch, speaker-change and overlap strata",
        "Paced target-device latency, enrollment cost, memory and deadline evidence",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A true
# class must be backed by at least one named row; absence is explicit.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "historical_local_any_speaker_vad_baseline": True,
    "historical_local_adjacent_speaker_dominant_suppression": True,
    "historical_local_in_model_speaker_similarity_diagnostic": True,
    "source_only_personal_vad_protocol": True,
    "source_reported_candidate_gap": True,
    "source_reported_dataset_lead": True,
    "missing_enrollment_conditioned_execution": True,
    "missing_target_label_benchmark": True,
    "missing_checkpoint_or_weights": True,
    "missing_clean_target_reference": True,
    "missing_benchmark_protocol": True,
    "personal_vad_local_execution": False,
    "speaker_conditioned_neural_execution": False,
    "target_label_accuracy_claim": False,
    "speaker_identification_or_verification_claim": False,
    "source_separation_or_enhancement_claim": False,
    "device_timing": False,
    "human_validation_result": False,
    "listening_result": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

EVIDENCE_BACKING: Dict[str, List[str]] = {
    "historical_local_any_speaker_vad_baseline": ["CI-1", "HE-3"],
    "historical_local_adjacent_speaker_dominant_suppression": ["CI-2", "CI-3", "HE-1", "HE-2"],
    "historical_local_in_model_speaker_similarity_diagnostic": ["CI-4"],
    "source_only_personal_vad_protocol": ["CI-5", "RO-1", "RO-4"],
    "source_reported_candidate_gap": ["RO-3", "RO-6"],
    "source_reported_dataset_lead": ["CI-6", "RO-5"],
    "missing_enrollment_conditioned_execution": ["CI-7"],
    "missing_target_label_benchmark": ["CI-7"],
    "missing_checkpoint_or_weights": ["RO-3"],
    "missing_clean_target_reference": ["CI-7"],
    "missing_benchmark_protocol": ["CI-7"],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a rights-qualified enrolled-speaker mixture corpus with clean target references, target/other-speech/nonspeech labels, consent and a speaker-disjoint split",
        "evidence_gap": "No enrolled mixture, consent record, clean target waveform or speaker-disjoint partition exists; AMI/EARS have no enrollment cue and REAL-PS4 is a lead only.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-FND-EVIDENCE",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-05 corpus-owner task exists; the asset-boundary and evidence foundations plus the two research-control intake rows own rules and manifests, not a corpus or consent grant.",
    },
    {
        "id": "G02",
        "actionable_gap": "Pin one exact Personal VAD / VoiceFilter-Lite checkpoint and runtime with license, compatible enrollment embedding, input contract and safe fallback",
        "evidence_gap": "The catalogued ML rows are blocked; the reproduction lead exposes no compatible checkpoint and no license review; nothing is staged or executable.",
        "follow_up_ids": [
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
            "SDK-VOICEFILTER",
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
        ],
        "feasibility_task_exists": True,
        "owner_note": "All three linked rows are feasibility scoping leads; none enables a model, stages weights or establishes a personalized-VAD result.",
    },
    {
        "id": "G03",
        "actionable_gap": "Build the catalogued classic baseline: any-speaker VAD plus independent speaker scoring and threshold calibration",
        "evidence_gap": "The classic pipeline is catalogued but never assembled; VAD and speaker-similarity evidence exist separately with no shared enrolled cohort, threshold or score.",
        "follow_up_ids": [
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-SILERO-VAD-6-2-3-REFERENCE",
            "SDK-WEBRTC-VAD",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-05 baseline task exists; the linked research-control and implementation rows own scoring tooling and component references only, not a combined personal-VAD baseline.",
    },
    {
        "id": "G04",
        "actionable_gap": "Calibrate an enrollment/speaker-scoring component with threshold, EER and channel/enrollment-length sensitivity separate from activity classification",
        "evidence_gap": "Speaker-similarity evidence is limited to in-model conversion cosines; no enrollment embedding, calibration set, EER or threshold is tied to activity.",
        "follow_up_ids": [
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The x-vector row is a feasibility lead and the two similarity rows are research controls; none is a calibrated enrollment scorer and none supplies activity truth.",
    },
    {
        "id": "G05",
        "actionable_gap": "Define a frozen three-class benchmark with target false rejection, impostor acceptance, EER, utterance latency, unknown masking and uncertainty",
        "evidence_gap": "No shared scorer, label policy, threshold, stratification or held-out split exists; any-speaker FN/FP and adjacent SI-SDR/STOI cannot substitute.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-SURVEY-DET-01",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-05 benchmark task exists; the evidence foundation, scoring tooling and completed DET-01 survey own protocol and comparison rules only, not a personalized-VAD benchmark.",
    },
    {
        "id": "G06",
        "actionable_gap": "Measure target-device latency, enrollment cost, memory, deadline and clock behavior for the intended host",
        "evidence_gap": "Only desktop accelerated or batch adjacent values exist; no enrolled-target callback path, enrollment cost or deadline distribution is measured.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-05 device task exists; the timing and evidence foundations own lifecycle and acceptance rules, not a device measurement.",
    },
    {
        "id": "G07",
        "actionable_gap": "Keep personalized VAD separate from waveform extraction, muting, speaker identification and diarization and require an independent control for each output",
        "evidence_gap": "Adjacent suppression rows change waveforms and speaker similarity rows score identity; none produces target activity, and no cross-category ablation exists.",
        "follow_up_ids": [
            "SDK-SURVEY-SPK-02",
            "SDK-SURVEY-SPK-05",
            "SDK-SURVEY-DET-01",
            "SDK-SURVEY-DET-03",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No single component owns the DET-05 boundary; the linked taxonomy rows are scoping owners for extraction, identity, general VAD and overlap, not personalized-VAD results.",
    },
    {
        "id": "G08",
        "actionable_gap": "Test whether speaker segmentation or diarization turn labels can supply a target proxy without being mislabelled as personalized activity",
        "evidence_gap": "BIC segmentation and pyannote diarization are considered or blocked and have no local target-labelled evaluation; turn labels do not identify an enrolled speaker.",
        "follow_up_ids": [
            "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION",
            "SDK-PYANNOTE-DIARIZATION",
            "SDK-PYANNOTE-SEGMENTATION-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The three linked rows are feasibility scoping leads; none is a personalized-VAD system and none establishes target activity.",
    },
    {
        "id": "G09",
        "actionable_gap": "Resolve rights and license eligibility for the paper reproduction, VoiceFilter-Lite artifacts and REAL-PS4/Open Yap labels before any adapter or release evidence",
        "evidence_gap": "Checkpoint terms are unverified, original VoiceFilter weights are not open, and dataset terms, label provenance and redistribution rights are unreviewed.",
        "follow_up_ids": ["SDK-FND-AUDIT", "SDK-VOICEFILTER-LITE-PERSONAL-VAD"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-05 rights task exists; the asset-boundary foundation and the feasibility lead own intake scoping, not a license grant or redistribution permission.",
    },
    {
        "id": "G10",
        "actionable_gap": "Require independent exact-head review before any benchmark, public default or release claim",
        "evidence_gap": "This proposal-only map has no independent reviewer, no personalized-VAD benchmark and no default-selection approval.",
        "follow_up_ids": ["SDK-FND-EVIDENCE", "SDK-FND-AUDIT"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-05 review task exists; the evidence and asset-boundary foundations own protocol and intake rules, not independent approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE", "title": "LibriSpeech and Common Voice evidence intake", "mode": "research-control"},
    {"task_id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING", "title": "VADToolkit and AMI scoring tooling", "mode": "research-control"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER", "title": "VoiceFilter", "mode": "feasibility"},
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
    {"task_id": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY", "title": "Resemblyzer speaker-similarity proxy", "mode": "research-control"},
    {"task_id": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY", "title": "SpeechBrains ECAPA / speaker similarity", "mode": "research-control"},
    {"task_id": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION", "title": "Bayesian information criterion speaker segmentation", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-DIARIZATION", "title": "pyannote diarization", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-SEGMENTATION-VAD", "title": "pyannote segmentation / VAD", "mode": "feasibility"},
    {"task_id": "SDK-SILERO-VAD-6-2-3-REFERENCE", "title": "Silero VAD 6.2.3 reference", "mode": "implementation"},
    {"task_id": "SDK-WEBRTC-VAD", "title": "WebRTC VAD", "mode": "implementation"},
    {"task_id": "SDK-SURVEY-DET-01", "title": "Review coverage for Speech activity detection (VAD/SAD)", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-DET-03", "title": "Review coverage for Overlapping speech detection and speaker count", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-02", "title": "Review coverage for Target-speaker extraction and personalized enhancement", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-05", "title": "Review coverage for Speaker representation, identification and verification", "mode": "taxonomy"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified enrolled-speaker mixture corpus with clean target references, target/other-speech/nonspeech labels, consent and a speaker-disjoint split"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen speaker-disjoint development and held-out partitions with independent label and identity review"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched always-target, always-other-speech, always-nonspeech, any-speaker VAD, VAD-plus-scoring, target-absent and impostor controls with EER, target false rejection, false acceptance and uncertainty"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned real personal-VAD checkpoint, exact revision, license and runtime with a safe fallback"},
    {"id": "RG-05", "blocked": True, "requirement": "Enrollment-duration, channel, speaker-change and overlap strata plus measured target-device latency, enrollment cost, memory and deadline behavior"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **DET-05 \u2014 Target-speaker / personalized VAD** |",
        "Not source separation or a mandate to mute; measure target false rejection and changing speakers.",
    ],
    "research/category_survey/sources.md": [
        "| S52 | [Personal VAD primary paper](https://research.google/pubs/personal-vad-speaker-conditioned-voice-activity-detection/) | omissions reviewer and root | direct |",
        "| S53 | [Personal VAD existing reproduction and checkpoint leads](https://github.com/wq2012/personal_vad) | omissions reviewer | direct README; no execution/checkpoint access |",
    ],
    "research/category_survey/omissions_review.md": [
        "Ordinary VAD detects speech activity; target extraction returns a waveform.",
        "explicitly distinguishes target speech, other speech, and non-speech frame scores.",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Analysis | Score timestamped probabilities, event boundaries and detections.",
    ],
    "research/plans/F02/vad_sources.md": [
        "Target-speaker detection with three classes (target user, other speech, nonspeech)",
        "REAL-PS4 exposes target-speaker activity for clipped overlapping utterances",
    ],
    "research/plans/F02/vad_accuracy_contract.md": [
        "Unknown or unannotated time is never nonspeech.",
    ],
    "reports/vad-research/chaining-evaluation.md": [
        "| WebRTC | 7.31% | 49.54% | 226.0s | 486.6s | 6.38\u00b5s | 20 / 70ms |",
        "| Silero | 19.43% | 8.20% | 601.0s | 80.5s | 68.35\u00b5s | 280 / -220ms |",
    ],
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md": [
        "The improved relative ratio therefore does not mean useful target preservation",
        "the exact C API accepts no enrollment/reference waveform",
    ],
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": [
        "This is one meeting, seven directed speaker pairs, synthetically combined non-overlap turns",
        "Hush's exact interface is primary/background attenuation rather than reference-conditioned target selection.",
    ],
    "research/voice-enhancement-20261101/findings.md": [
        "Hush's exact API accepts no enrollment prompt, so this measures synthetic primary/background suppression rather than reference-conditioned target-speaker extraction.",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "No deployable local checkpoint and no enrolled-speaker mixtures with clean target references for fair extraction scoring.",
        "Original Google weights/runtime are not open; third-party substitutes are separate candidates",
    ],
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": [
        "Personal VAD is speech/activity detection conditioned on enrolled speaker; it does not itself output isolated speech enhancement.",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "target-encoder cosine was 0.669 (40+40) and 0.702 (120+40)",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/survey-det-01/README.md": [
        "bounded, deterministic **taxonomy and comparison map**",
    ],
    "docs/task-evidence/survey-det-01/report.json": [
        '"decision":"DEFER"',
    ],
    "docs/task-evidence/survey-cln-11/README.md": [
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
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
    "enrollment_cue": False,
    "listening": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "nonpersonal_row_promoted_to_personal_vad": "rejected; state unchanged",
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
            root = None
            for candidate in [here.parent] + list(here.parents):
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
        raise MapError("DET-05 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("DET-05 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F05 / DET-05 is not unique")
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
            raise MapError("legacy backlog mismatch: F05/DET-05/%s" % key)


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


def _check_method_families() -> None:
    branches = {row["branch"] for row in METHOD_FAMILIES}
    if branches != {"classic", "ml"}:
        raise MapError("both catalogued method branches must be covered")
    families = " ".join(row["family"] for row in METHOD_FAMILIES)
    for keyword in (
        "Standard VAD plus independent speaker-scoring",
        "Speaker-conditioned neural activity classification",
    ):
        if keyword not in families:
            raise MapError("catalogued family missing: " + keyword)
    gap_ids = {gap["id"] for gap in GAPS}
    for row in METHOD_FAMILIES:
        if not row["components"]:
            raise MapError("method family has no component: " + row["family_id"])
        if not row["gap_ids"]:
            raise MapError("method family has no gap: " + row["family_id"])
        for gap_id in row["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("method family links unknown gap: " + gap_id)


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
        if "not rerun by this survey" not in row["scope"]:
            raise MapError("historical execution is not labelled as not rerun: " + row["id"])
        if row["outcome_class"] not in {
            "historical_local_any_speaker_vad_baseline",
            "historical_local_adjacent_speaker_dominant_suppression",
        }:
            raise MapError("historical execution has an unsupported class: " + row["id"])


def _check_comparison_inputs() -> None:
    allowed = {
        "historical_local_any_speaker_vad_baseline",
        "historical_local_adjacent_speaker_dominant_suppression",
        "historical_local_in_model_speaker_similarity_diagnostic",
        "source_only_personal_vad_protocol",
        "source_reported_dataset_lead",
        "missing_enrollment_conditioned_corpus",
    }
    for row in COMPARISON_INPUTS:
        if row["class"] not in allowed:
            raise MapError("comparison input has an unsupported class: " + row["id"])


def _check_evidence_classes() -> None:
    true_keys = {key for key, value in EVIDENCE_CLASSES.items() if value}
    false_keys = {key for key, value in EVIDENCE_CLASSES.items() if not value}
    if true_keys != set(EVIDENCE_BACKING):
        raise MapError("evidence backing does not cover every true class")
    if true_keys & false_keys:
        raise MapError("evidence class is both true and false")
    required_false = {
        "personal_vad_local_execution",
        "speaker_conditioned_neural_execution",
        "target_label_accuracy_claim",
        "speaker_identification_or_verification_claim",
        "source_separation_or_enhancement_claim",
        "device_timing",
        "human_validation_result",
        "listening_result",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    }
    if false_keys != required_false:
        raise MapError("unsupported evidence classes changed")
    for key in (
        "personal_vad_local_execution",
        "speaker_conditioned_neural_execution",
        "target_label_accuracy_claim",
        "speaker_identification_or_verification_claim",
        "source_separation_or_enhancement_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported evidence class is true: " + key)
    rows: Dict[str, str] = {}
    for row in COMPARISON_INPUTS:
        rows[row["id"]] = row["class"]
    for row in HISTORICAL_EXECUTIONS:
        rows[row["id"]] = row["outcome_class"]
    for row in REPORTED_OUTCOMES:
        rows[row["id"]] = row["class"]
    row_classes = set(rows.values())
    for key, ids in EVIDENCE_BACKING.items():
        if not ids:
            raise MapError("evidence class has no backing row: " + key)
        for row_id in ids:
            if row_id not in rows:
                raise MapError("evidence backing names an unknown row: %s/%s" % (key, row_id))
        # Missing-evidence classes are backed by an explicit "missing_..." row;
        # every other true class must appear verbatim as a row class.
        if not key.startswith("missing_") and key not in row_classes:
            raise MapError("true evidence class has no matching row class: " + key)
    for key in false_keys:
        for row_class in row_classes:
            if key in row_class:
                raise MapError("false evidence class is claimed by a row: " + key)


def _check_personal_vad_boundary() -> None:
    expected_true = (
        "target_speaker_activity_only",
        "three_way_classes_required",
        "enrollment_or_reference_cue_required",
        "not_source_separation",
        "not_mute_or_gate_mandate",
        "not_speaker_identification_or_verification",
        "not_general_any_speaker_vad",
        "not_diarization_or_speaker_change_truth",
        "changing_speakers_and_target_false_rejection_are_material_strata",
        "enrollment_condition_must_travel_with_every_number",
        "author_reported_numbers_are_not_local",
        "pcm_output_is_identity_where_a_waveform_is_emitted",
    )
    expected_false = (
        "compatible_checkpoint_or_weights_staged",
        "enrolled_mixture_or_clean_target_reference_staged",
        "personal_vad_local_execution_present",
        "device_timing_measured",
        "listening_or_human_validation_result",
        "benchmark_or_release_qualification_present",
    )
    for key in expected_true:
        if PERSONAL_VAD_BOUNDARY.get(key) is not True:
            raise MapError("personal-VAD boundary flag is not true: " + key)
    for key in expected_false:
        if PERSONAL_VAD_BOUNDARY.get(key) is not False:
            raise MapError("personal-VAD boundary flag is not false: " + key)


def _check_execution_coverage() -> None:
    by_class: Dict[str, List[str]] = {}
    for row in HISTORICAL_EXECUTIONS:
        by_class.setdefault(row["outcome_class"], []).append(row["id"])
    checks = {
        "historical_execution_count": len(HISTORICAL_EXECUTIONS),
        "historical_local_any_speaker_vad_execution_count": len(by_class.get("historical_local_any_speaker_vad_baseline", [])),
        "historical_local_adjacent_suppression_execution_count": len(by_class.get("historical_local_adjacent_speaker_dominant_suppression", [])),
        "personal_vad_local_execution_count": 0,
        "speaker_conditioned_neural_execution_count": 0,
        "enrollment_conditioned_execution_count": 0,
        "target_label_benchmark_execution_count": 0,
        "dedicated_personal_vad_component_count": len(DEDICATED_PERSONAL_VAD_COMPONENTS),
        "locally_evaluated_personal_vad_component_count": 0,
        "any_speaker_vad_component_count": len(ANY_SPEAKER_VAD_COMPONENTS),
        "adjacent_suppression_component_count": 1,
    }
    for key, value in checks.items():
        if EXECUTION_COVERAGE.get(key) != value:
            raise MapError("execution coverage mismatch: " + key)
    for key in (
        "missing_enrollment_conditioned_corpus",
        "missing_checkpoint_or_weights",
        "missing_target_label_benchmark",
        "missing_benchmark_scorer",
    ):
        if EXECUTION_COVERAGE.get(key) is not True:
            raise MapError("missing-evidence flag is not true: " + key)


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
            raise MapError("linked board task mode is not allowed: " + link["task_id"])
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


def _check_pins_cover_rows() -> None:
    pins = set(SOURCE_PINS) | set(WORKTREE_PINS)
    for row in COMPARISON_INPUTS:
        if row["source_pin"] not in pins:
            raise MapError("comparison input is not pinned: " + row["id"])
    for row in CONTROLS:
        if row["source_pin"] not in pins:
            raise MapError("control is not pinned: " + row["id"])
    for row in ASSETS:
        if row["source_pin"] not in pins:
            raise MapError("asset is not pinned: " + row["name"])
    for row in HISTORICAL_EXECUTIONS:
        if row["source_pin"] not in pins:
            raise MapError("historical execution is not pinned: " + row["id"])
    for row in REPORTED_OUTCOMES:
        if row["source_pin"] not in pins:
            raise MapError("reported outcome is not pinned: " + row["id"])
    if BOARD_PATH in SOURCE_PINS or BOARD_PATH in WORKTREE_PINS:
        raise MapError("mutable board file is pinned")


def _build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    ws = find_workspace(workspace)
    sdk = find_sdk_root(sdk_root)
    _check_document_pins(ws, sdk)
    _check_anchors(ws, sdk)
    _check_taxonomy(ws)
    _check_backlog(ws)
    _check_component_census(ws)
    _check_method_families()
    _check_historical_execution_components()
    _check_comparison_inputs()
    _check_evidence_classes()
    _check_personal_vad_boundary()
    _check_execution_coverage()
    _check_pins_cover_rows()
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
        "qualification_status": QUALIFICATION_STATUS,
        "readiness": READINESS,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "readiness": READINESS,
            "survey_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
            "personal_vad_local_execution_present": False,
            "speaker_conditioned_neural_execution_present": False,
            "enrollment_conditioned_execution_present": False,
            "target_label_benchmark_present": False,
            "release_qualification_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "personal_vad_boundary": dict(PERSONAL_VAD_BOUNDARY),
        "discovery": {
            "catalog_record_present": True,
            "source_leads_reviewed": True,
            "any_speaker_vad_baseline_present": True,
            "adjacent_suppression_diagnostic_present": True,
            "in_model_speaker_similarity_diagnostic_present": True,
            "personal_vad_local_execution_present": False,
            "speaker_conditioned_neural_execution_present": False,
            "enrollment_conditioned_corpus_present": False,
            "compatible_checkpoint_or_weights_present": False,
            "target_label_benchmark_present": False,
            "clean_target_reference_present": False,
            "runnable_host_adapter_present": False,
            "device_timing_or_listening_present": False,
        },
        "legacy_backlog": {
            "family_id": LEGACY_FAMILY,
            "activation_state": "catalogued",
            "state": "catalogued",
            "next_action": "Plan discovery across required source buckets",
            "source_pin": "research/task_backlog.json",
        },
        "source_leads": [dict(lead) for lead in SOURCE_LEADS],
        "method_families": [dict(family) for family in METHOD_FAMILIES],
        "adjacent_boundaries": [dict(row) for row in ADJACENT_BOUNDARIES],
        "component_census": [dict(row) for row in COMPONENT_CENSUS],
        "comparison_inputs": [dict(row) for row in COMPARISON_INPUTS],
        "controls": [dict(row) for row in CONTROLS],
        "assets": [dict(row) for row in ASSETS],
        "historical_executions": [dict(row) for row in HISTORICAL_EXECUTIONS],
        "reported_outcomes": [dict(row) for row in REPORTED_OUTCOMES],
        "execution_coverage": dict(EXECUTION_COVERAGE),
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
