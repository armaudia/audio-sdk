# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-SPK-04.

This module builds a bounded taxonomy/comparison evidence map for anonymous
speaker diarization (inventory category ``SPK-04``, legacy family ``F06``). It
reads only pinned, read-only documents from the enclosing ``audioml`` workspace
and the SDK worktree. It does not load audio, weights, runtimes, media or the
network, and it does not register, expose, enable or qualify any diarization
system.

All curated records below are documentation mappings, not new measurements.
Historical local or source-reported values are transcribed verbatim from the
pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-SPK-04"
TITLE = "Review coverage for Anonymous speaker diarization"
CATEGORY_ID = "SPK-04"
LEGACY_FAMILY = "F06"
BRANCH = "swarm/SDK-SURVEY-SPK-04"
BASE_COMMIT = "af941fdf40195d4b4893c5c0f361d636f5f2510d"
PROFILE = "Spatial"
COMPONENT = "anonymous-speaker-diarization-evidence-map"
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
# verifies media, weights or annotations that are not present in this task
# directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/vad-research/20261028-synthesis-v7.md": "2bc353e9d6d648a7e58204e202a5f4a03b75859b58f3fd515ec37216168a5a6c",
    "reports/vad-research/chaining-evaluation.md": "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/pilot_evaluation_progress.md": "7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf",
    "research/plans/F02/vad_accuracy_contract.md": "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
    "research/plans/F02/vad_sources.md": "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/evaluation_records.md": "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header or component is copied, edited or
# generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/hush/README.md": "0426a592204381138e7fa7ba04f37f4aff92eee6ac75b6bda31f0861c485e76f",
    "docs/task-evidence/survey-det-03/README.md": "672e7a380230f4a1e13e88404deb92b052052bdb05b029a67672fe655ff9593e",
    "docs/task-evidence/survey-rec-01/README.md": "01e54b306313f13f97e1c9f4a08f5ebd98cbf570617644a028ae2bca3d4f4acb",
    "docs/task-evidence/survey-spk-01/README.md": "554a9fcc044e89c35ba761bf1fa8f7fed172ba22f797e44bdd64a753c00adc9d",
    "docs/task-evidence/webrtc-vad/README.md": "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Speakers and separation",
    "name": "Anonymous speaker diarization",
    "scope": "requested",
    "output_kind": "annotation",
    "purpose": "Label who spoke when within the recording/session.",
    "method_families": {
        "classic": "Segmentation + statistical representations/clustering",
        "ml": "Neural segmentation/embeddings + clustering; end-to-end families to search",
    },
    "input_output": "Audio \u2192 timestamped anonymous speaker labels",
    "live_or_comparison_boundary": (
        "Represent overlap and possible online revisions; anonymous labels are not "
        "enrolled identities."
    ),
    "source_ids": ["S06", "S47"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "SPK",
    "meaning": "Speakers and separation",
    "category_id": CATEGORY_ID,
    "anonymous_labels_only": True,
    "anonymous_labels_are_not_enrolled_identities": True,
    "diarization_is_not_speech_activity_detection": True,
    "diarization_is_not_overlap_detection_or_speaker_count": True,
    "diarization_is_not_speaker_change_segmentation": True,
    "diarization_is_not_speaker_identity": True,
    "diarization_is_not_source_separation": True,
    "diarization_is_not_target_speaker_extraction": True,
    "diarization_is_not_transcription_or_language_identification": True,
    "overlap_and_online_revisions_must_be_represented": True,
    "note": (
        "Speech activity detection (DET-01), endpointing (DET-02), sound-event "
        "analysis (DET-04), target-speaker VAD (DET-05), overlapping-speech "
        "detection and speaker count (DET-03), generic separation (SPK-01), "
        "target-speaker extraction (SPK-02), speaker-change segmentation "
        "(SPK-03), speaker identity (SPK-05), beamforming (CLN-07), source "
        "localization (CLN-08), transcription and language identification are "
        "separate catalogued categories. They are named only to prevent scope "
        "inflation; their results are not pooled into an SPK-04 diarization "
        "claim."
    ),
}

DIARIZATION_BOUNDARY: Dict[str, Any] = {
    "anonymous_labels_only": True,
    "anonymous_labels_are_not_enrolled_identities": True,
    "diarization_is_not_speech_activity_detection": True,
    "diarization_is_not_overlap_detection": True,
    "diarization_is_not_speaker_identity": True,
    "diarization_is_not_source_separation": True,
    "diarization_is_not_target_speaker_extraction": True,
    "diarization_is_not_transcription_or_language_identification": True,
    "overlap_must_be_represented": True,
    "online_revisions_must_be_explicit": True,
    "speaker_level_truth_and_any_speaker_union_kept_separate": True,
    "unknown_time_is_never_nonspeech": True,
    "synthetic_mixture_is_not_natural_diarization": True,
    "author_reported_is_not_local": True,
    "diarization_execution_present": False,
    "der_execution_present": False,
    "natural_meeting_diarization_execution_present": False,
    "pyannote_runtime_or_weights_present": False,
    "rights_qualified_diarization_corpus_present": False,
    "speaker_level_truth_present": False,
    "speaker_identity_execution_present": False,
    "online_revision_execution_present": False,
    "calibrated_array_geometry_present": False,
    "device_timing_present": False,
    "human_listening_result_present": False,
    "benchmark_or_release_qualification_present": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S06",
        "title": "pyannote speaker analysis metric documentation",
        "url": "https://pyannote.github.io/pyannote-metrics/reference.html",
        "access_scope": "direct",
        "researcher": "analysis",
        "mapped_components": ["pyannote-diarization", "pyannote-segmentation-vad"],
        "gap_ids": ["G02", "G03"],
        "finding": (
            "The catalogued source is speaker-analysis metric documentation, not "
            "a pinned pyannote checkpoint, exact revision, access token, runtime, "
            "adapter, corpus or DER/JER result. The inventory records pyannote "
            "diarization as considered and pyannote segmentation/VAD as blocked; "
            "the candidate register reports no staged weights, source checkout or "
            "adapter. The documentation is not promoted to a local metric "
            "implementation or a diarization capability claim."
        ),
    },
    {
        "source_id": "S47",
        "title": "CHiME-8 meeting transcription pipeline",
        "url": "https://www.chimechallenge.org/challenges/chime8/task1/index",
        "access_scope": "direct",
        "researcher": "root",
        "mapped_components": [
            "vctk-dns2020-ami-ears-and-smard-evidence-manifests",
            "vadtoolkit-and-ami-scoring-tooling",
            "pyannote-diarization",
        ],
        "gap_ids": ["G01", "G06"],
        "finding": (
            "The catalogued source is a meeting-transcription challenge pipeline, "
            "not a staged diarization system. The pinned source register says "
            "CHiME-8 supplies per-session UEM scoring bounds and SegLST "
            "transcript/utterance spans; UEM defines where scoring occurs, "
            "utterance spans are not validated continuous speech or diarization "
            "truth, and DiPCo/NOTSOFAR partitions and rights remain unresolved. "
            "No audio, RTTM, weights or local DER/JER result is staged."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Segmentation plus statistical speaker representations and clustering",
        "components": [
            "bayesian-information-criterion-speaker-segmentation",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G04", "G05"],
        "status": "catalogued_considered_no_local_segmentation_clustering_or_der_execution",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural segmentation and speaker embeddings followed by clustering",
        "components": [
            "pyannote-segmentation-vad",
            "pyannote-diarization",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G03", "G05"],
        "status": "blocked_or_considered_no_weights_runtime_or_local_diarization_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "End-to-end diarization and meeting-transcription families to search",
        "components": [
            "pyannote-diarization",
            "vctk-dns2020-ami-ears-and-smard-evidence-manifests",
        ],
        "gap_ids": ["G01", "G06"],
        "status": "search_only_no_dedicated_end_to_end_component_or_local_execution",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml-adjacent",
        "family": "Speaker-representation and similarity proxies adjacent to clustering",
        "components": [
            "resemblyzer-speaker-similarity-proxy",
            "speechbrains-ecapa-speaker-similarity",
        ],
        "gap_ids": ["G05", "G08"],
        "status": "partial_similarity_proxies_not_anonymous_diarization",
    },
    {
        "family_id": "MF-M4",
        "branch": "adjacent",
        "family": "Separation, target-speaker extraction and personal-VAD boundary",
        "components": [
            "conv-tasnet",
            "target-speaker-extraction-family",
            "voicefilter-lite-personal-vad",
            "hush",
        ],
        "gap_ids": ["G07", "G08"],
        "status": "catalogued_considered_or_blocked_not_diarization_not_pooled",
    },
    {
        "family_id": "MF-M5",
        "branch": "adjacent",
        "family": "Speech activity and speaker-change segmentation boundary",
        "components": [
            "webrtc-vad",
            "silero-vad-6-2-3-reference",
            "bayesian-information-criterion-speaker-segmentation",
            "pyannote-segmentation-vad",
        ],
        "gap_ids": ["G03", "G07"],
        "status": "adjacent_activity_or_change_detection_not_diarization",
    },
]

# Adjacent components are named to keep scope boundaries explicit. They are not
# SPK-04 diarizers and none of their results is pooled here.
ADJACENT_BOUNDARIES: List[Dict[str, Any]] = [
    {
        "component_id": "webrtc-vad",
        "category_boundary": "DET-01 speech activity detection",
        "relation": "Any-speech frame classification merges overlapping participants into one activity decision; it emits no timestamped anonymous speaker labels.",
        "not_diarization_evidence": True,
    },
    {
        "component_id": "bayesian-information-criterion-speaker-segmentation",
        "category_boundary": "SPK-03 speaker change detection and segmentation",
        "relation": "A change point or locally homogeneous segment does not link a speaker's later turns into a session-wide anonymous label map.",
        "not_diarization_evidence": True,
    },
    {
        "component_id": "pyannote-segmentation-vad",
        "category_boundary": "SPK-03 neural segmentation / SPK-04 candidate",
        "relation": "Frame or local speaker segmentation is only one stage; without pinned embeddings, clustering and a label-linking policy it is not a diarization result.",
        "not_diarization_evidence": True,
    },
    {
        "component_id": "x-vector-speaker-embeddings",
        "category_boundary": "SPK-05 speaker representation and identity",
        "relation": "An embedding or similarity score is not a timestamped speaker-label map and does not establish anonymous session clusters.",
        "not_diarization_evidence": True,
    },
    {
        "component_id": "hush",
        "category_boundary": "SPK-01/02 separation and competing-speaker suppression",
        "relation": "The historical Hush rows use AMI speaker IDs only to construct speaker-dominant mixtures; the output is one enhanced waveform, not labels.",
        "not_diarization_evidence": True,
    },
    {
        "component_id": "target-speaker-extraction-family",
        "category_boundary": "SPK-02 target-speaker extraction",
        "relation": "Enrollment-conditioned extraction selects a known target; anonymous diarization clusters unenrolled speakers within a session.",
        "not_diarization_evidence": True,
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "pyannote-segmentation-vad", "evidence_status": "blocked", "task": "SDK-PYANNOTE-SEGMENTATION-VAD"},
    {"component_id": "bayesian-information-criterion-speaker-segmentation", "evidence_status": "considered", "task": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "resemblyzer-speaker-similarity-proxy", "evidence_status": "partial", "task": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"},
    {"component_id": "speechbrains-ecapa-speaker-similarity", "evidence_status": "partial", "task": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY"},
    {"component_id": "vctk-dns2020-ami-ears-and-smard-evidence-manifests", "evidence_status": "evaluated", "task": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS"},
    {"component_id": "vadtoolkit-and-ami-scoring-tooling", "evidence_status": "partial", "task": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING"},
    {"component_id": "hush", "evidence_status": "partial", "task": "SDK-HUSH"},
    {"component_id": "webrtc-vad", "evidence_status": "evaluated", "task": "SDK-WEBRTC-VAD"},
    {"component_id": "silero-vad-6-2-3-reference", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-6-2-3-REFERENCE"},
    {"component_id": "fast-vad-0-2-1", "evidence_status": "evaluated", "task": "SDK-FAST-VAD-0-2-1"},
    {"component_id": "earshot-1-2-2", "evidence_status": "evaluated", "task": "SDK-EARSHOT-1-2-2"},
    {"component_id": "speexdsp-vad", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-VAD"},
    {"component_id": "fixed-rms-vad", "evidence_status": "evaluated", "task": "SDK-FIXED-RMS-VAD"},
    {"component_id": "adaptive-energy-vad", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-ENERGY-VAD"},
    {"component_id": "conv-tasnet", "evidence_status": "considered", "task": "SDK-CONV-TASNET"},
    {"component_id": "target-speaker-extraction-family", "evidence_status": "blocked", "task": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"},
    {"component_id": "voicefilter-lite-personal-vad", "evidence_status": "blocked", "task": "SDK-VOICEFILTER-LITE-PERSONAL-VAD"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Six AMI Mix-Headset recordings, three speaker-disjoint development and three held-out, comparing seven any-speech VAD candidates on 20 ms frames",
        "class": "historical_local_adjacent_any_speech",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "boundary": "Any-speaker speech activity only; no speaker labels, anonymous clusters, overlap intervals, DER/JER or natural-meeting diarization claim.",
    },
    {
        "id": "CI-2",
        "input": "Four audEERING VADToolkit recordings scored only inside 588 annotated positive spans",
        "class": "historical_local_adjacent_positive_only",
        "source_pin": "reports/vad-research/20261028-synthesis-v7.md",
        "boundary": "Positive-span-only VAD diagnostic; the source register states no speaker IDs or overlap convention, and the complement is unknown rather than nonspeech.",
    },
    {
        "id": "CI-3",
        "input": "Seven directed AMI speaker pairs combined into 21 synthetic additive mixtures at +12, +18 and +24 dB target-over-masker ratio",
        "class": "historical_local_adjacent_synthetic_speaker_pair",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "boundary": "Constructed additive examples from non-overlap turns in one mono meeting; the known speaker IDs are used only for mixture construction, and no diarization label map, natural overlap or DER/JER result exists.",
    },
    {
        "id": "CI-4",
        "input": "pyannote speaker-analysis metric documentation (S06)",
        "class": "source_only_metric_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation scope only; no scorer implementation, collar, UEM policy, label-permutation handling, value or local reproduction is staged.",
    },
    {
        "id": "CI-5",
        "input": "CHiME-8 DASR, DiPCo and NOTSOFAR1 meeting-pipeline metadata with UEM scored bounds and SegLST transcript/utterance spans (S47)",
        "class": "source_reported_meeting_pipeline_metadata",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Metadata only; UEM defines where scoring occurs, utterance spans are not validated continuous speech or diarization truth, partitions/rights are unresolved, and no audio or RTTM is staged.",
    },
    {
        "id": "CI-6",
        "input": "Catalogued pyannote diarization and pyannote segmentation/VAD rows",
        "class": "source_only_catalogued_ml_components",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; diarization is considered, segmentation/VAD is blocked, and no exact checkpoint, token, revision, runtime, adapter or local inference exists.",
    },
    {
        "id": "CI-7",
        "input": "Catalogued Bayesian-information-criterion speaker segmentation and x-vector representation rows",
        "class": "source_only_catalogued_classic_components",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; no local BIC segmentation, clustering, embedding extraction, session linking or DER/JER result exists.",
    },
    {
        "id": "CI-8",
        "input": "VCTK, DNS2020, AMI, EARS and SMARD prepared evidence manifests",
        "class": "prepared_manifest_only",
        "source_pin": "research/voice-enhancement-20261101/evaluation_records.md",
        "boundary": "Prepared manifests and source/group hash policy only; no rights-qualified diarization corpus, RTTM/UEM reference or held-out speaker-level split is staged.",
    },
    {
        "id": "CI-9",
        "input": "Rights-qualified natural meeting or conversation corpus with speaker-level RTTM, UEM/scored regions, overlap truth, anonymous labels and explicit unknown regions",
        "class": "missing_rights_qualified_diarization_corpus",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
        "boundary": "Missing. AMI provides any-speech word intervals and four participant turn files for one meeting only; audEERING supplies no speaker IDs; no corpus rights, RTTM/UEM reference or held-out partition is staged.",
    },
    {
        "id": "CI-10",
        "input": "Exact runnable pyannote diarization or segmentation candidate with pinned revision, weights, token, runtime and adapter",
        "class": "missing_pyannote_runtime_and_weights",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Missing. The candidate register and VAD/segmentation audit report no staged weights, source checkout, adapter or inference for pyannote.",
    },
    {
        "id": "CI-11",
        "input": "Frozen DER/JER benchmark with collar, UEM masking, overlap-aware scoring, label permutation, degenerate controls and failed-item accounting",
        "class": "missing_diarization_benchmark_protocol",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Missing. No DER/JER scorer, collar/UEM policy, speaker-error metric, label-permutation assignment, held-out split or failed-item accounting is implemented or applied.",
    },
    {
        "id": "CI-12",
        "input": "Paced target-device online-diarization timing and label-revision evidence",
        "class": "missing_online_revision_and_device_timing",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Missing. No availability clock, deadline, memory, dropped/stale event, online revision, latency or target-device measurement exists for a diarizer.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "DER/JER and speaker-error metric with collar and UEM",
        "role": "Required diarization metric family; no implementation, collar policy, UEM mask or scored value exists in this task.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-2",
        "name": "always-one-speaker and oracle-speaker-count degenerate controls",
        "role": "Required degenerate baselines that expose clustering and count failure; neither was run on a valid diarization cohort.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
    {
        "id": "CT-3",
        "name": "speaker-level truth versus any-speaker union",
        "role": "Both representations must be preserved; a union-only score cannot establish anonymous speaker labels or cluster identity.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
    {
        "id": "CT-4",
        "name": "unknown-region masking",
        "role": "Unannotated time is excluded, never relabelled nonspeech, non-speech or a new speaker.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
    {
        "id": "CT-5",
        "name": "overlap-aware versus exclusive-label scoring",
        "role": "Speaker-level overlap truth and an any-speaker union must remain separate; exclusive-label scoring silently discards simultaneous speech.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
    {
        "id": "CT-6",
        "name": "anonymous-label permutation and online revision",
        "role": "Anonymous cluster names are arbitrary and may be revised online; no label-permutation assignment or revision policy exists locally.",
        "source_pin": "audio_categories.md",
    },
    {
        "id": "CT-7",
        "name": "identity / passthrough audio",
        "role": "Diarization is annotation and never modifies PCM; an identity control guards against a gate or separator being credited as a diarizer.",
        "source_pin": "docs/task-evidence/hush/README.md",
    },
    {
        "id": "CT-8",
        "name": "synthetic speaker-pair mixture versus natural meeting",
        "role": "Constructed additive turns test robustness but do not substitute for naturally simultaneous speech, natural turn-taking or speaker-label truth.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "id": "CT-9",
        "name": "anonymous session cluster versus enrolled identity",
        "role": "A session label is not a person, gallery match or verification decision; identity and diarization require separate outputs and metrics.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "id": "CT-10",
        "name": "missing, invalid, nonfinite and out-of-range interval rejection",
        "role": "Missing or malformed labels are blocked, not scored; no missing result may qualify a candidate or produce a diarization claim.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "AMI ES2004a Mix-Headset single meeting mix and four participant turn files",
        "class": "research_speech_corpus_reference",
        "status": "CC BY 4.0 per the cited report; one mono 17.49-minute mix with speaker IDs and turn timing, no isolated participant tracks, no RTTM/UEM reference and no local DER/JER result.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "asset": "audEERING VADToolkit 1.1.0 metadata, annotations and four public WAVs",
        "class": "research_audio_positive_only",
        "status": "GPLv3/commercial package staged under prior authorization; no speaker IDs or overlap convention and the complement is unknown.",
        "source_pin": "reports/vad-research/20261028-synthesis-v7.md",
    },
    {
        "asset": "Hush synthetic AMI speaker-pair mixtures (one meeting, seven pairs, 21 additive examples)",
        "class": "research_audio_derived_adjacent",
        "status": "Constructed from non-overlap turns in a mono meeting with speaker-dominant proxies; no isolated clean references, natural overlap, anonymous label map or redistribution grant.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "asset": "pyannote speaker-analysis metric documentation (S06)",
        "class": "external_documentation",
        "status": "Direct documentation scope; no scorer, collar/UEM policy, weights, token, exact revision, runtime or adapter.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "CHiME-8 DASR, DiPCo and NOTSOFAR1 meeting-pipeline metadata (S47)",
        "class": "source_and_metadata_only",
        "status": "UEM scored bounds and SegLST utterance spans only; no audio, RTTM/UEM diarization reference, speaker-level held-out split or local score is staged.",
        "source_pin": "research/plans/F02/vad_sources.md",
    },
    {
        "asset": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests",
        "class": "prepared_manifest_only",
        "status": "Prepared research manifests and hash/group policy; no rights-qualified diarization corpus or speaker-level annotated partition.",
        "source_pin": "research/voice-enhancement-20261101/evaluation_records.md",
    },
    {
        "asset": "Rights-qualified natural meeting or conversation corpus with speaker-level RTTM/UEM and anonymous labels",
        "class": "missing_corpus_assets",
        "status": "Not present; no consent, annotation protocol, overlap/unknown-region policy, speaker-level truth or independent split is available.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
    {
        "asset": "pyannote diarization/segmentation checkpoint, access token, runtime and adapter",
        "class": "missing_model_assets",
        "status": "Not staged; segmentation is blocked and diarization is considered, with no weights or inference.",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "Frozen DER/JER benchmark and online-revision/device-timing protocol",
        "class": "missing_benchmark_assets",
        "status": "Not present; no scorer, collar/UEM policy, held-out split, failed-item accounting, revision policy or target-device timing.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Six-recording AMI any-speech VAD comparison with three speaker-disjoint held-out meetings (adjacent activity only)",
        "outcome_class": "historical_local_adjacent_any_speech",
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
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "recordings": 6,
            "heldout_meetings": 3,
            "candidates": 7,
            "scored_frame_ms": 20,
            "speaker_label_rows": 0,
            "der_metric_rows": 0,
        },
        "scope": (
            "Historical local any-speaker VAD comparison on six AMI Mix-Headset "
            "recordings, three development and three speaker-disjoint held-out; "
            "it is not a diarization or speaker-label result, not a natural-meeting "
            "DER/JER measurement, not a target-device result and not rerun by this "
            "survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "audEERING positive-span-only VAD diagnostic (adjacent activity only)",
        "outcome_class": "historical_local_adjacent_positive_only",
        "component_ids": [
            "adaptive-energy-vad",
            "earshot-1-2-2",
            "fast-vad-0-2-1",
            "fixed-rms-vad",
            "silero-vad-6-2-3-reference",
            "speexdsp-vad",
            "webrtc-vad",
        ],
        "source_pin": "reports/vad-research/20261028-synthesis-v7.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "recordings": 4,
            "annotated_positive_spans": 588,
            "speaker_ids_supplied": False,
            "speaker_label_rows": 0,
            "der_metric_rows": 0,
        },
        "scope": (
            "Historical positive-span-only VAD diagnostic; the complement is "
            "unknown, no speaker IDs or overlap convention exist, and it is not a "
            "diarization result and not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Hush AMI speaker-labeled turn mixtures (adjacent speaker-pair construction only)",
        "outcome_class": "historical_local_adjacent_synthetic_speaker_pair",
        "component_ids": ["hush"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "meetings": 1,
            "speaker_pairs": 7,
            "synthetic_mixtures": 21,
            "sir_strata_db": [12, 18, 24],
            "speaker_ids_used_for_mixture_construction": True,
            "speaker_label_output_segments": 0,
            "natural_overlap": False,
            "isolated_clean_references": False,
            "der_metric_rows": 0,
        },
        "scope": (
            "Historical adjacent synthetic speaker-pair construction from "
            "non-overlap AMI turns in one mono meeting; it uses turn speaker IDs "
            "only to build mixtures, is not a diarization result, not natural "
            "meeting overlap, not a DER/JER measurement and not rerun by this "
            "survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "pyannote speaker-analysis metric documentation describes diarization metric families and scoring conventions",
        "class": "source_reported_metric_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation scope only; no scorer implementation, collar/UEM policy, label-permutation handling, numeric value or local reproduction is staged.",
    },
    {
        "id": "RO-2",
        "claim": "CHiME-8 meeting-transcription pipeline reports UEM scored bounds and SegLST transcript/utterance spans for meeting sessions",
        "class": "source_reported_meeting_pipeline_metadata",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Metadata only; UEM is a scoring mask, utterance spans are not validated continuous speech or diarization truth, and no audio, RTTM or local score is staged.",
    },
    {
        "id": "RO-3",
        "claim": "pyannote diarization is catalogued as considered and pyannote segmentation/VAD as blocked",
        "class": "source_reported_plan_row",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; no local diarization execution, anonymous label map, DER/JER metric or identity result exists.",
    },
    {
        "id": "RO-4",
        "claim": "Bayesian-information-criterion speaker segmentation and x-vector speaker embeddings are catalogued classic/representation leads",
        "class": "source_reported_plan_row",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; no local BIC segmentation, clustering, embedding extraction, session linking or diarization score.",
    },
    {
        "id": "RO-5",
        "claim": "Resemblyzer and SpeechBrains ECAPA rows are partial speaker-similarity proxies",
        "class": "source_reported_research_control",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Identity/similarity scope only; they do not provide timestamped anonymous speaker labels, cluster count or DER/JER and are not pooled here.",
    },
    {
        "id": "RO-6",
        "claim": "Diarization and meeting corpora leads include DIHARD, CHiME-8/DiPCo, AMI, EAR-1 and VoxConverse with published annotation and access conditions",
        "class": "source_reported_corpus_metadata",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Metadata and access-register entries only; no audio, RTTM/UEM reference, permissions, scored regions or held-out split is staged, and several leads are gated or noncommercial.",
    },
    {
        "id": "RO-7",
        "claim": "The historical AMI VAD evaluation is not broad multilingual, accent, overlap or device validation",
        "class": "source_reported_adjacent_scope",
        "source_pin": "research/voice-enhancement-20261101/evaluation_records.md",
        "boundary": "Scope statement transcribed from the pinned evaluation record; it explicitly excludes overlap, speaker-label and device validation.",
    },
]

EXECUTION_COVERAGE: Dict[str, Any] = {
    "catalogued_diarization_component_count": 1,
    "locally_evaluated_diarization_component_count": 0,
    "diarization_execution_count": 0,
    "der_execution_count": 0,
    "pyannote_execution_count": 0,
    "neural_diarization_execution_count": 0,
    "natural_meeting_diarization_execution_count": 0,
    "rights_qualified_diarization_execution_count": 0,
    "online_revision_execution_count": 0,
    "device_timing_execution_count": 0,
    "adjacent_any_speech_execution_count": 2,
    "adjacent_synthetic_speaker_pair_execution_count": 1,
    "note": (
        "One dedicated pyannote diarization row is catalogued but only as "
        "considered; no diarization, DER/JER, neural clustering, natural-meeting, "
        "rights-qualified, online-revision or device-timing execution exists. Two "
        "historical local rows are any-speech VAD diagnostics and one constructs "
        "synthetic speaker-pair mixtures from non-overlap turns. None produces an "
        "anonymous speaker-label map."
    ),
}

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "geometry_layout_calibration": "No array geometry, layout, timestamp calibration or reference channel exists; every local adjacent row is mono 16 kHz.",
        "source_target_reference_conditions": "AMI supplies one mono meeting mix and participant turn files; Hush uses synthetic speaker-dominant turn crops; no isolated speaker tracks or natural overlap reference exist.",
        "permissions": "AMI is CC BY 4.0 and audEERING is GPLv3/commercial; no rights-qualified diarization corpus, RTTM/UEM reference or redistribution grant exists.",
        "held_out_labels": "No speaker-level held-out RTTM/UEM labels, anonymous cluster truth or diarization split is staged.",
        "leakage_and_reference_changes": "No channel loss, room-change or reference-change measurement exists; the only AMI meeting is a single mono mix.",
        "task_matched_quality": "No DER, JER, speaker error, cluster purity or overlap-aware diarization metric was executed.",
        "target_damage": "Not applicable: diarization is an annotation output and no waveform is modified; no passthrough check was run.",
        "speaker_count_and_identity": "No active-speaker count or identity execution exists; anonymous session labels are not enrolled identities.",
        "online_revisions": "No streaming cadence, label revision, dropped/stale event or online scoring policy was measured.",
        "missing_result_accounting": "No SPK-04 diarization execution exists; the absence is recorded, not promoted to a pass.",
        "listening": "No blinded listening or label-quality rating exists.",
        "timing": "No target-device, streaming-state or availability-deadline measurement exists for a diarizer.",
    },
    "blocked": [
        "Rights-qualified natural meeting or conversation corpus with speaker-level RTTM/UEM, overlap truth, anonymous labels and explicit unknown regions",
        "Frozen speaker/session/group-disjoint development and held-out partitions with independent label review",
        "DER/JER scorer with collar, UEM masking, overlap-aware scoring, label permutation and degenerate controls",
        "Pinned pyannote segmentation/diarization and embedding runtimes, weights, tokens, exact revisions and adapters",
        "Natural meeting/overlap reference with speaker-level truth and any-speaker union preserved separately",
        "Paced target-device online-diarization availability, memory, deadline, clock and label-revision evidence",
        "Opt-in provider intake, independent exact-head review, and separation from VAD/overlap/separation/extraction/identity/transcription",
        "Explicit public default selection and release approval; DEFER remains in force until every gate is closed",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "adjacent_any_speech_historical_local": True,
    "adjacent_positive_only_historical_local": True,
    "adjacent_synthetic_speaker_pair_historical_local": True,
    "source_only_metric_documentation": True,
    "source_reported_meeting_pipeline_metadata": True,
    "source_only_catalogued_classic_components": True,
    "source_only_catalogued_ml_components": True,
    "prepared_manifest_only": True,
    "missing_rights_qualified_diarization_corpus": True,
    "missing_pyannote_runtime_and_weights": True,
    "missing_diarization_benchmark_protocol": True,
    "missing_online_revision_and_device_timing": True,
    "diarization_execution": False,
    "der_execution": False,
    "pyannote_local_execution": False,
    "neural_diarization_execution": False,
    "natural_meeting_diarization_execution": False,
    "speaker_label_output": False,
    "speaker_identity_execution": False,
    "online_revision_execution": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified natural meeting or conversation corpus with speaker-level RTTM/UEM, overlap truth, anonymous labels and explicit unknown regions",
        "evidence_gap": "AMI provides any-speech word intervals and four participant turn files for one meeting only; audEERING has no speaker IDs; Hush uses synthetic speaker-pair mixtures; no rights, RTTM/UEM reference or held-out split is staged.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a rights-qualified diarization corpus; the linked research-control and foundation rows own manifests, VAD scoring and evidence rules, not a new corpus or rights grant.",
    },
    {
        "id": "G02",
        "actionable_gap": "Define and validate DER/JER, speaker-error, collar/UEM, overlap-aware and label-permutation metrics with degenerate controls",
        "evidence_gap": "No DER, JER, speaker error, cluster-purity, collar, UEM mask, label-permutation assignment or failed-item accounting is implemented or scored.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a diarization scorer; the linked foundation and research-control rows own general evidence rules and VAD scoring tooling, not DER/JER.",
    },
    {
        "id": "G03",
        "actionable_gap": "Pin pyannote segmentation and diarization with exact revision, weights, token, runtime, adapter and output semantics",
        "evidence_gap": "Pyannote segmentation is blocked and diarization is considered; the candidate register and audit report no staged weights, source checkout, adapter or inference.",
        "follow_up_ids": [
            "SDK-PYANNOTE-DIARIZATION",
            "SDK-PYANNOTE-SEGMENTATION-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "Both pyannote rows are feasibility scoping leads; neither enables a model, stages weights or establishes diarization capability.",
    },
    {
        "id": "G04",
        "actionable_gap": "Evaluate classic BIC speaker-change segmentation plus statistical clustering as a diarization baseline without treating a change point as a speaker label",
        "evidence_gap": "The BIC row is considered only; no local implementation, change-boundary score, session clustering, anonymous label map or DER/JER result exists.",
        "follow_up_ids": [
            "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION",
            "SDK-SURVEY-SPK-03",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The BIC feasibility row and speaker-change taxonomy row are scoping leads only; no boundary, cluster or DER/JER result is claimed.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate speaker embeddings and clustering for anonymous session labels without identity, verification or enrollment claims",
        "evidence_gap": "X-vector is considered and the Resemblyzer/ECAPA rows are partial similarity proxies; no embedding extraction, session clustering, label map or DER/JER execution exists.",
        "follow_up_ids": [
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY",
            "SDK-SURVEY-SPK-05",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The embedding row is a feasibility lead and the identity taxonomy row keeps anonymous clustering, verification and enrollment separate.",
    },
    {
        "id": "G06",
        "actionable_gap": "Search and pin end-to-end diarization and meeting-transcription families, including the S47 pipeline, before claiming a candidate",
        "evidence_gap": "The catalogued ML family says end-to-end families remain to search; no dedicated end-to-end component, pipeline revision, checkpoint or local output exists.",
        "follow_up_ids": [
            "SDK-PYANNOTE-DIARIZATION",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The pyannote feasibility row is the nearest catalogued candidate and the manifest row owns source/group hashes; neither is an end-to-end search result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Keep anonymous diarization separate from VAD, overlap detection, speaker count, speaker change and speaker identity",
        "evidence_gap": "Adjacent rows declare different outputs; no local component exposes a stable anonymous speaker-label contract with overlap and online-revision semantics.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-03",
            "SDK-SURVEY-SPK-03",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner merges these tasks; the linked taxonomy rows keep activity, overlap/count, change detection and diarization definitions separate.",
    },
    {
        "id": "G08",
        "actionable_gap": "Keep diarization separate from separation, target-speaker extraction, personal VAD, identity and transcription",
        "evidence_gap": "Hush, Conv-TasNet, target-speaker extraction and VoiceFilter-Lite rows have different outputs or require enrollment; no diarization label map can inherit from them.",
        "follow_up_ids": [
            "SDK-SURVEY-SPK-01",
            "SDK-SURVEY-SPK-02",
            "SDK-SURVEY-SPK-05",
            "SDK-HUSH",
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The extraction rows are feasibility leads; the separation, extraction, identity and implementation rows keep their outputs separate and none is a diarizer.",
    },
    {
        "id": "G09",
        "actionable_gap": "Collect paced target-device online-diarization timing, memory, availability, deadline and label-revision evidence",
        "evidence_gap": "No diarization runtime exists; adjacent VAD numbers are desktop, accelerated or batch values and cannot establish a live diarizer.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has diarization device or revision evidence; the foundation rows own lifecycle/timing and evidence rules, not a device measurement.",
    },
    {
        "id": "G10",
        "actionable_gap": "Require independent exact-head review and explicit release approval before any benchmark, default or release claim",
        "evidence_gap": "This proposal-only map has no independent reviewer, no diarization benchmark and no default-selection or release approval.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "BENCH-FND-CHECK",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-04 review task exists; the foundation rows own evidence and acceptance templates, not independent approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "BENCH-FND-CHECK", "title": "Benchmark acceptance and rights-safe evidence templates", "mode": "foundation"},
    {"task_id": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION", "title": "Bayesian information criterion speaker segmentation", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-HUSH", "title": "Hush", "mode": "implementation"},
    {"task_id": "SDK-PYANNOTE-DIARIZATION", "title": "pyannote diarization", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-SEGMENTATION-VAD", "title": "pyannote segmentation / VAD", "mode": "feasibility"},
    {"task_id": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY", "title": "Resemblyzer speaker-similarity proxy", "mode": "research-control"},
    {"task_id": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY", "title": "SpeechBrains ECAPA / speaker similarity", "mode": "research-control"},
    {"task_id": "SDK-SURVEY-DET-03", "title": "Review coverage for Overlapping speech detection and speaker count", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-01", "title": "Review coverage for Generic speech/source separation", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-02", "title": "Review coverage for Target-speaker extraction and personalized enhancement", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-03", "title": "Review coverage for Speaker change detection and segmentation", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-05", "title": "Review coverage for Speaker representation, identification and verification", "mode": "taxonomy"},
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING", "title": "VADToolkit and AMI scoring tooling", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified natural meeting or conversation corpus with speaker-level RTTM/UEM, overlap truth, anonymous labels, explicit unknown regions and permissions"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen speaker/session/group-disjoint development and held-out partitions with independent label review"},
    {"id": "RG-03", "blocked": True, "requirement": "DER/JER scorer with collar, UEM masking, overlap-aware scoring, label permutation, degenerate controls and failed-item accounting"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned pyannote segmentation/diarization and embedding runtimes, weights, tokens, exact revisions and adapters for every claimed candidate"},
    {"id": "RG-05", "blocked": True, "requirement": "Natural meeting or overlap reference that preserves speaker-level truth and any-speaker union separately, with explicit online-revision semantics"},
    {"id": "RG-06", "blocked": True, "requirement": "Paced target-device online-diarization availability, memory, deadline and clock evidence with revision accounting"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake, independent exact-head review, and separation from VAD/overlap/separation/extraction/identity/transcription"},
    {"id": "RG-08", "blocked": True, "requirement": "Explicit public default selection and release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated facts and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **SPK-04 \u2014 Anonymous speaker diarization** | Label who spoke when within the recording/session. Scope: requested. |",
        "Represent overlap and possible online revisions; anonymous labels are not enrolled identities.",
    ],
    "research/category_survey/sources.md": [
        "| S06 | [pyannote speaker analysis metric documentation](https://pyannote.github.io/pyannote-metrics/reference.html) | analysis | direct |",
        "| S47 | [CHiME-8 meeting transcription pipeline](https://www.chimechallenge.org/challenges/chime8/task1/index) | root | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    ],
    "audio-benchmark-platform/plan/INVENTORY.json": [
        '"id": "SPK-04",',
        '"id": "pyannote-diarization",',
        '"id": "bayesian-information-criterion-speaker-segmentation",',
        '"id": "x-vector-speaker-embeddings",',
    ],
    "research/category_registry.json": [
        '"id": "SPK-04",',
        '"id": "S06",',
        '"id": "S47",',
    ],
    "research/task_backlog.json": [
        '"category_id":"SPK-04","dependencies":[],"family_id":"F06"',
    ],
    "research/plans/F02/vad_sources.md": [
        "11.38% mean overlap",
        "overlap scoring and no forgiveness collar",
        "UEM defines where scoring occurs, not speech labels.",
        "SegLST transcript/utterance spans (example 370 ms phrase) are not validated continuous VAD boundaries",
        "per-speaker RTTM activity",
    ],
    "research/plans/F02/vad_accuracy_contract.md": [
        "For overlap, define and preserve speaker-level truth and any-speaker union separately.",
        "Unknown or unannotated time is never nonspeech.",
    ],
    "reports/vad-research/chaining-evaluation.md": [
        "On three speaker-disjoint held-out AMI meetings",
        "The split has disjoint participant IDs.",
        "Boundary-delay matching uses overlap with annotated word intervals, not hand-labeled turn boundaries.",
    ],
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": [
        "Four participant segment files provide speaker IDs and turn timing.",
        "These are constructed additive examples rather than naturally simultaneous overlap.",
        "seven distinct directed speaker pairs",
        "speaker-dominant proxies",
    ],
    "research/voice-enhancement-20261101/evaluation_records.md": [
        "not broad multilingual/accent/overlap/device validation",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "VAD,Additional TEN VAD / PulseVAD / FSMN / MarbleNet / FireRedVAD / pyannote,unavailable/blocked",
    ],
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": [
        "pyannote | researched but not run",
    ],
    "research/pilot_evaluation_progress.md": [
        "Preserve separate speaker activity and any-speaker union when overlap labels exist",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/hush/README.md": [
        "Task-local, **proposal-only**, **incomplete** and **not qualified** evidence",
    ],
    "docs/task-evidence/survey-det-03/README.md": [
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
        "diarization (`SPK-04`)",
    ],
    "docs/task-evidence/survey-spk-01/README.md": [
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
        "not anonymous diarization (`SPK-04`)",
    ],
    "docs/task-evidence/survey-rec-01/README.md": [
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
    ],
    "docs/task-evidence/webrtc-vad/README.md": [
        "This package is a deterministic, fully synthetic VAD *surrogate* at a",
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
    "real_diarization_audio": False,
    "weights": False,
    "runtime_invocation": False,
    "listening": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "diarization_claim": False,
    "speaker_identity_claim": False,
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
    "unknown_component": "rejected; state unchanged",
    "diarization_claim_without_diarization_execution": "rejected; state unchanged",
    "der_claim_without_der_execution": "rejected; state unchanged",
    "pyannote_claim_without_weights_or_runtime": "rejected; state unchanged",
    "any_speech_vad_promoted_to_diarization": "rejected; state unchanged",
    "overlap_detection_promoted_to_diarization": "rejected; state unchanged",
    "speaker_count_promoted_to_diarization": "rejected; state unchanged",
    "speaker_identity_promoted_to_diarization": "rejected; state unchanged",
    "synthetic_mixture_relabelled_natural_diarization": "rejected; state unchanged",
    "author_reported_promoted_to_local_execution": "rejected; state unchanged",
    "heldout_benchmark_claim_without_labelled_split": "rejected; state unchanged",
    "online_revision_claim_without_revision_evidence": "rejected; state unchanged",
    "release_claim_without_closed_gates": "rejected; state unchanged",
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
        raise MapError("SPK-04 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("SPK-04 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F06 / SPK-04 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "requested",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F06/SPK-04/%s" % key)


def _check_component_census(workspace: Path) -> None:
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    by_id = {c["id"]: c for c in inventory["components"]}
    seen = set()
    for row in COMPONENT_CENSUS:
        component_id = row["component_id"]
        if component_id in seen:
            raise MapError("duplicate component in census: " + component_id)
        seen.add(component_id)
        component = by_id.get(component_id)
        if component is None:
            raise MapError("inventory component missing: " + component_id)
        if component.get("task") != row["task"]:
            raise MapError("inventory task mismatch: " + component_id)
        if component.get("evidence_status") != row["evidence_status"]:
            raise MapError("inventory evidence_status mismatch: " + component_id)
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    mapped.update(row["component_id"] for row in ADJACENT_BOUNDARIES)
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    uncensused = sorted(mapped - seen)
    if uncensused:
        raise MapError("mapped component is not censused: " + ",".join(uncensused))


def _check_historical_execution_components() -> None:
    known = {row["component_id"] for row in COMPONENT_CENSUS}
    allowed_classes = {
        "historical_local_adjacent_any_speech",
        "historical_local_adjacent_positive_only",
        "historical_local_adjacent_synthetic_speaker_pair",
    }
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
            raise MapError("historical execution is not marked adjacent: " + row["id"])
        if row.get("outcome_class") not in allowed_classes:
            raise MapError("historical execution is not explicitly adjacent: " + row["id"])
        scope = row.get("scope", "")
        if "not rerun by this survey" not in scope:
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])
        if "not a diarization" not in scope:
            raise MapError("historical execution is not labelled non-diarization: " + row["id"])
        if not row.get("values"):
            raise MapError("historical execution has no values: " + row["id"])
        if row.get("source_pin") not in SOURCE_PINS:
            raise MapError("historical execution is not pinned to a source report: " + row["id"])


def _check_evidence_classes() -> None:
    input_classes = {row["class"] for row in COMPARISON_INPUTS}
    outcome_classes = {row["outcome_class"] for row in HISTORICAL_EXECUTIONS}
    reported_classes = {row["class"] for row in REPORTED_OUTCOMES}
    asset_classes = {row["class"] for row in ASSETS}
    checks = {
        "adjacent_any_speech_historical_local": "historical_local_adjacent_any_speech" in outcome_classes,
        "adjacent_positive_only_historical_local": "historical_local_adjacent_positive_only" in outcome_classes,
        "adjacent_synthetic_speaker_pair_historical_local": "historical_local_adjacent_synthetic_speaker_pair" in outcome_classes,
        "source_only_metric_documentation": "source_only_metric_documentation" in input_classes,
        "source_reported_meeting_pipeline_metadata": "source_reported_meeting_pipeline_metadata" in reported_classes,
        "source_only_catalogued_classic_components": "source_only_catalogued_classic_components" in input_classes,
        "source_only_catalogued_ml_components": "source_only_catalogued_ml_components" in input_classes,
        "prepared_manifest_only": "prepared_manifest_only" in asset_classes,
        "missing_rights_qualified_diarization_corpus": "missing_rights_qualified_diarization_corpus" in input_classes,
        "missing_pyannote_runtime_and_weights": "missing_pyannote_runtime_and_weights" in input_classes,
        "missing_diarization_benchmark_protocol": "missing_diarization_benchmark_protocol" in input_classes,
        "missing_online_revision_and_device_timing": "missing_online_revision_and_device_timing" in input_classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "diarization_execution",
        "der_execution",
        "pyannote_local_execution",
        "neural_diarization_execution",
        "natural_meeting_diarization_execution",
        "speaker_label_output",
        "speaker_identity_execution",
        "online_revision_execution",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported claim is not closed: " + key)
    if not any(row["class"].startswith("source_reported") for row in REPORTED_OUTCOMES):
        raise MapError("source-reported class has no backing row")


def _check_execution_coverage() -> None:
    if EXECUTION_COVERAGE.get("catalogued_diarization_component_count") != 1:
        raise MapError("catalogued diarization component count changed")
    zero_counts = (
        "locally_evaluated_diarization_component_count",
        "diarization_execution_count",
        "der_execution_count",
        "pyannote_execution_count",
        "neural_diarization_execution_count",
        "natural_meeting_diarization_execution_count",
        "rights_qualified_diarization_execution_count",
        "online_revision_execution_count",
        "device_timing_execution_count",
    )
    for key in zero_counts:
        if EXECUTION_COVERAGE.get(key) != 0:
            raise MapError("execution coverage claim changed: " + key)
    any_speech = [r for r in HISTORICAL_EXECUTIONS if r["outcome_class"] == "historical_local_adjacent_any_speech"]
    positive = [r for r in HISTORICAL_EXECUTIONS if r["outcome_class"] == "historical_local_adjacent_positive_only"]
    synthetic = [
        r
        for r in HISTORICAL_EXECUTIONS
        if r["outcome_class"] == "historical_local_adjacent_synthetic_speaker_pair"
    ]
    if len(any_speech) + len(positive) != EXECUTION_COVERAGE["adjacent_any_speech_execution_count"]:
        raise MapError("adjacent any-speech execution count is inconsistent")
    if len(synthetic) != EXECUTION_COVERAGE["adjacent_synthetic_speaker_pair_execution_count"]:
        raise MapError("synthetic speaker-pair construction count is inconsistent")
    if any("diarization" in row["outcome_class"] for row in HISTORICAL_EXECUTIONS):
        raise MapError("an adjacent execution is relabelled as diarization")
    if any("der" in row["outcome_class"] for row in HISTORICAL_EXECUTIONS):
        raise MapError("an adjacent execution is relabelled as DER")


def _check_diarization_boundary() -> None:
    required_true = (
        "anonymous_labels_only",
        "anonymous_labels_are_not_enrolled_identities",
        "diarization_is_not_speech_activity_detection",
        "diarization_is_not_overlap_detection",
        "diarization_is_not_speaker_identity",
        "diarization_is_not_source_separation",
        "diarization_is_not_target_speaker_extraction",
        "diarization_is_not_transcription_or_language_identification",
        "overlap_must_be_represented",
        "online_revisions_must_be_explicit",
        "speaker_level_truth_and_any_speaker_union_kept_separate",
        "unknown_time_is_never_nonspeech",
        "synthetic_mixture_is_not_natural_diarization",
        "author_reported_is_not_local",
    )
    required_false = (
        "diarization_execution_present",
        "der_execution_present",
        "natural_meeting_diarization_execution_present",
        "pyannote_runtime_or_weights_present",
        "rights_qualified_diarization_corpus_present",
        "speaker_level_truth_present",
        "speaker_identity_execution_present",
        "online_revision_execution_present",
        "calibrated_array_geometry_present",
        "device_timing_present",
        "human_listening_result_present",
        "benchmark_or_release_qualification_present",
    )
    if set(DIARIZATION_BOUNDARY) != set(required_true) | set(required_false):
        raise MapError("diarization boundary keys changed")
    for key in required_true:
        if DIARIZATION_BOUNDARY[key] is not True:
            raise MapError("diarization boundary rule is not enforced: " + key)
    for key in required_false:
        if DIARIZATION_BOUNDARY[key] is not False:
            raise MapError("diarization boundary claim is not closed: " + key)


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
    gap_ids = {gap["id"] for gap in GAPS}
    used = set()
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
            used.add(task_id)
        if gap.get("feasibility_task_exists"):
            modes = {next(t["mode"] for t in BOARD_LINKS if t["task_id"] == tid) for tid in gap["follow_up_ids"]}
            if "feasibility" not in modes:
                raise MapError("gap claims a feasibility follow-up without one: " + gap["id"])
        if not gap.get("owner_note"):
            raise MapError("gap has no owner note: " + gap["id"])
    orphan = sorted(known - used)
    if orphan:
        raise MapError("board link is not referenced by any gap: " + ",".join(orphan))
    for source in SOURCE_LEADS:
        for gap_id in source["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("source lead links unknown gap: " + gap_id)
    for family in METHOD_FAMILIES:
        for gap_id in family["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("method family links unknown gap: " + gap_id)
    for row in COMPONENT_CENSUS:
        if row["task"] not in by_id:
            raise MapError("census task is not on the board: " + row["task"])
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
    _check_execution_coverage()
    _check_diarization_boundary()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
    by_id = {t["id"]: t for t in board["tasks"]}
    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
        linked_gaps = sorted(g["id"] for g in GAPS if link["task_id"] in g["follow_up_ids"])
        if not linked_gaps:
            raise MapError("board link is not referenced by any gap: " + link["task_id"])
        if by_id[link["task_id"]].get("title") != link["title"]:
            raise MapError("linked board title changed: " + link["task_id"])
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
        "qualification_status": QUALIFICATION_STATUS,
        "readiness": READINESS,
        "decision": DECISION,
        "qualification": {
            "decision": DECISION,
            "status": QUALIFICATION_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "readiness": READINESS,
            "survey_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
            "adjacent_local_execution_present": True,
            "diarization_execution_present": False,
            "der_execution_present": False,
            "pyannote_execution_present": False,
            "release_qualification_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "diarization_boundary": dict(DIARIZATION_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "catalogued_diarization_component_ids": ["pyannote-diarization"],
            "locally_evaluated_diarization_component_ids": [],
            "adjacent_any_speech_component_ids": [
                "fixed-rms-vad",
                "adaptive-energy-vad",
                "webrtc-vad",
                "speexdsp-vad",
                "silero-vad-6-2-3-reference",
                "fast-vad-0-2-1",
                "earshot-1-2-2",
            ],
            "adjacent_representation_component_ids": [
                "bayesian-information-criterion-speaker-segmentation",
                "x-vector-speaker-embeddings",
                "resemblyzer-speaker-similarity-proxy",
                "speechbrains-ecapa-speaker-similarity",
            ],
            "adjacent_local_execution_present": True,
            "diarization_execution_present": False,
            "der_execution_present": False,
            "natural_meeting_corpus_present": False,
            "pyannote_weights_present": False,
            "speaker_level_truth_present": False,
            "heldout_diarization_split_present": False,
            "benchmark_protocol_present": False,
            "online_revision_evidence_present": False,
            "note": (
                "One pyannote diarization row is catalogued as considered, but no "
                "diarization, DER/JER, session-clustering or online-revision "
                "execution exists. AMI VAD and Hush speaker-pair construction are "
                "adjacent local evidence only; pyannote, BIC and embedding rows "
                "have no staged weights, runtime, token, corpus or label map."
            ),
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
        "execution_coverage": dict(EXECUTION_COVERAGE),
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
    if report["decision"] != DECISION or report["qualification_status"] != QUALIFICATION_STATUS:
        raise MapError("disposition changed")
    if report["readiness"] != READINESS or report["status"] != STATUS:
        raise MapError("status changed")
    if report["qualification"]["status"] != QUALIFICATION_STATUS:
        raise MapError("nested qualification status changed")
    if report["qualification"]["diarization_execution_present"] is not False:
        raise MapError("a diarization execution is claimed")
    if report["qualification"]["der_execution_present"] is not False:
        raise MapError("a DER execution is claimed")
    if report["qualification"]["pyannote_execution_present"] is not False:
        raise MapError("a pyannote execution is claimed")
    if report["qualification"]["release_qualification_present"] is not False:
        raise MapError("release qualification is claimed")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    for key in (
        "task_local_only",
        "documentation_and_metadata_only",
        "no_new_execution",
        "synthetic_only_where_cited",
    ):
        if report["scope"][key] is not True:
            raise MapError("scope rule is not enforced: " + key)
    for key in (
        "real_speech",
        "real_corpus",
        "real_diarization_audio",
        "weights",
        "runtime_invocation",
        "listening",
        "device_timing",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "diarization_claim",
        "speaker_identity_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    ):
        if report["scope"][key] is not False:
            raise MapError("scope claim is not closed: " + key)
    if report["discovery"]["adjacent_local_execution_present"] is not True:
        raise MapError("adjacent local execution is not recorded")
    for key in (
        "diarization_execution_present",
        "der_execution_present",
        "natural_meeting_corpus_present",
        "pyannote_weights_present",
        "speaker_level_truth_present",
        "heldout_diarization_split_present",
        "benchmark_protocol_present",
        "online_revision_evidence_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    for key in (
        "diarization_execution",
        "der_execution",
        "pyannote_local_execution",
        "neural_diarization_execution",
        "natural_meeting_diarization_execution",
        "speaker_label_output",
        "speaker_identity_execution",
        "online_revision_execution",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    ):
        if report["evidence_classes"][key] is not False:
            raise MapError("unsupported evidence class is open: " + key)
    for key in (
        "adjacent_any_speech_historical_local",
        "adjacent_positive_only_historical_local",
        "adjacent_synthetic_speaker_pair_historical_local",
        "source_only_metric_documentation",
        "source_reported_meeting_pipeline_metadata",
        "source_only_catalogued_classic_components",
        "source_only_catalogued_ml_components",
        "prepared_manifest_only",
        "missing_rights_qualified_diarization_corpus",
        "missing_pyannote_runtime_and_weights",
        "missing_diarization_benchmark_protocol",
        "missing_online_revision_and_device_timing",
    ):
        if report["evidence_classes"][key] is not True:
            raise MapError("supported evidence class is missing: " + key)
    if BOARD_PATH in report["source_pins"]:
        raise MapError("mutable board file is pinned")
    if BOARD_PATH in report["boundary_pins"]:
        raise MapError("mutable board file is pinned as boundary")
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
