# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-DET-03.

This module builds a bounded taxonomy/comparison evidence map for overlapping
speech detection and active speaker count (inventory category ``DET-03``,
legacy family ``F05``). It reads only pinned, read-only documents from the
enclosing ``audioml`` workspace and the SDK worktree. It does not load audio,
weights, runtimes, media or the network, and it does not register, expose,
enable or qualify any detector.

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
TASK = "SDK-SURVEY-DET-03"
TITLE = "Review coverage for Overlapping speech detection and speaker count"
CATEGORY_ID = "DET-03"
LEGACY_FAMILY = "F05"
BRANCH = "swarm/SDK-SURVEY-DET-03"
BASE_COMMIT = "8213704719f641582db9493788305f2cd3629354"
PROFILE = "Analysis"
COMPONENT = "overlapping-speech-and-speaker-count-evidence-map"
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
    "REALTIME_COMPONENT_CANDIDATES.md": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/vad-research/20261028-synthesis-v7.md": "2bc353e9d6d648a7e58204e202a5f4a03b75859b58f3fd515ec37216168a5a6c",
    "reports/vad-research/chaining-evaluation.md": "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/pilot_evaluation_progress.md": "7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf",
    "research/plans/F02/vad_accuracy_contract.md": "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
    "research/plans/F02/vad_sources.md": "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
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
    "docs/task-evidence/survey-cln-07/README.md": "b748f2fda2ffebf10ea5f00923dc1dc1110f0712bada2ded074def53ef682d34",
    "docs/task-evidence/survey-cln-08/README.md": "33730b2bc2a34b05bb7392d8877c498a1b9112a2d41b9e83d31fa6853f8850e7",
    "docs/task-evidence/survey-det-01/README.md": "88430878409af7a5cdb74dbc4422724b78f4c0610463fed9d5d4f29d16fffacb",
    "docs/task-evidence/webrtc-vad/README.md": "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Detection and control",
    "name": "Overlapping speech detection and speaker count",
    "scope": "discovered_extension",
    "output_kind": "annotation",
    "purpose": "Detect simultaneous speech; estimate active speaker count where supported.",
    "method_families": {
        "classic": "Activity/spatial statistics",
        "ml": "Multi-label segmentation and counting models",
    },
    "input_output": "Audio \u2192 overlap intervals/count estimates",
    "live_or_comparison_boundary": (
        "Detection neither separates waveforms nor identifies unwanted speech."
    ),
    "source_ids": ["S02"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "DET",
    "meaning": "Detection and control",
    "category_id": CATEGORY_ID,
    "overlap_detection_only": True,
    "not_speech_activity_detection_category": "DET-01",
    "not_endpointing_category": "DET-02",
    "not_sound_event_scene_category": "DET-04",
    "not_target_speaker_vad_category": "DET-05",
    "not_generic_separation_category": "SPK-01",
    "not_target_speaker_extraction_category": "SPK-02",
    "not_speaker_change_segmentation_category": "SPK-03",
    "not_anonymous_diarization_category": "SPK-04",
    "not_speaker_identity_category": "SPK-05",
    "not_beamforming_category": "CLN-07",
    "not_source_localization_category": "CLN-08",
    "note": (
        "Speech activity detection (DET-01), endpointing (DET-02), sound-event "
        "analysis (DET-04), target-speaker VAD (DET-05), source separation "
        "(SPK-01), target-speaker extraction (SPK-02), speaker-change "
        "segmentation (SPK-03), anonymous diarization (SPK-04), speaker "
        "identity (SPK-05), beamforming (CLN-07) and source localization "
        "(CLN-08) are separate catalogued categories. They are named only to "
        "prevent scope inflation; their results are not pooled into a DET-03 "
        "overlap or speaker-count claim."
    ),
}

OVERLAP_BOUNDARY: Dict[str, Any] = {
    "overlap_detection_only": True,
    "not_source_separation": True,
    "not_target_speaker_extraction": True,
    "not_muting_or_unwanted_speech_identification": True,
    "diarization_is_adjacent_not_overlap_detection": True,
    "speaker_count_is_not_speaker_identity": True,
    "energy_vad_is_not_overlap_detection": True,
    "spatial_statistics_require_calibrated_array_geometry": True,
    "speaker_level_truth_and_any_speaker_union_kept_separate": True,
    "unknown_time_is_never_nonspeech": True,
    "synthetic_mixture_is_not_natural_overlap": True,
    "author_reported_is_not_local": True,
    "overlap_detection_execution_present": False,
    "speaker_count_execution_present": False,
    "natural_overlap_local_execution_present": False,
    "pyannote_runtime_or_weights_present": False,
    "rights_qualified_overlap_corpus_present": False,
    "speaker_level_truth_present": False,
    "calibrated_array_geometry_present": False,
    "device_timing_present": False,
    "human_listening_result_present": False,
    "benchmark_or_release_qualification_present": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S02",
        "title": "pyannote segmentation model card",
        "url": "https://huggingface.co/pyannote/segmentation",
        "access_scope": "direct",
        "mapped_components": ["pyannote-segmentation-vad", "pyannote-diarization"],
        "gap_ids": ["G05", "G06", "G07"],
        "finding": (
            "The catalogued source is a model card for pyannote segmentation, "
            "not a pinned checkpoint, exact revision, token, runtime, adapter or "
            "overlap/speaker-count result. The inventory records pyannote "
            "segmentation as blocked and pyannote diarization as considered; "
            "the candidate register reports no staged weights, source checkout "
            "or adapter, and no inference was run. The card's description is "
            "not promoted to a local capability claim."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Energy and spectral activity statistics with thresholds or adaptive noise floors",
        "components": [
            "fixed-rms-vad",
            "adaptive-energy-vad",
            "webrtc-vad",
            "speexdsp-vad",
        ],
        "gap_ids": ["G01", "G02", "G09"],
        "status": "historical_local_adjacent_any_speech_only_no_overlap_or_speaker_count_result",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Spatial statistics from calibrated microphone arrays, beamforming and direction-of-arrival",
        "components": [
            "delay-and-sum-beamformer",
            "mvdr-beamforming",
            "source-localization-direction-of-arrival",
            "auxiva",
            "spatialnet",
        ],
        "gap_ids": ["G03", "G04"],
        "status": "catalogued_considered_or_blocked_no_multichannel_overlap_execution",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Statistical speaker-change segmentation such as the Bayesian information criterion",
        "components": ["bayesian-information-criterion-speaker-segmentation"],
        "gap_ids": ["G05", "G08"],
        "status": "considered_only_no_local_execution_no_overlap_or_count_metric",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Multi-label neural segmentation for overlap intervals and local speaker activity",
        "components": ["pyannote-segmentation-vad"],
        "gap_ids": ["G06", "G08"],
        "status": "blocked_no_weights_checkpoint_runtime_or_local_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Speaker diarization and clustering for active speaker count",
        "components": ["pyannote-diarization"],
        "gap_ids": ["G06", "G07"],
        "status": "considered_no_local_execution_no_active_speaker_count_result",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Speaker-representation and embedding similarity controls adjacent to counting",
        "components": [
            "x-vector-speaker-embeddings",
            "resemblyzer-speaker-similarity-proxy",
            "speechbrains-ecapa-speaker-similarity",
        ],
        "gap_ids": ["G07", "G08"],
        "status": "considered_or_partial_identity_controls_no_overlap_or_count_execution",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Separation, target-speaker extraction and personal-VAD boundary, not overlap detection",
        "components": [
            "conv-tasnet",
            "beam-tasnet-beam-guided-tasnet",
            "target-speaker-extraction-family",
            "voicefilter",
            "voicefilter-lite-personal-vad",
        ],
        "gap_ids": ["G04", "G08"],
        "status": "catalogued_considered_or_blocked_not_overlap_detection_not_pooled",
    },
]

# Adjacent components are named to keep scope boundaries explicit. They are not
# DET-03 overlap detectors and none of their results is pooled here.
ADJACENT_BOUNDARIES: List[Dict[str, Any]] = [
    {
        "component_id": "webrtc-vad",
        "category_boundary": "DET-01 speech activity detection",
        "relation": "Any-speech frame classification has no simultaneous-speech label or active-speaker count; speech from overlapping participants is merged into one activity decision.",
        "not_overlap_evidence": True,
    },
    {
        "component_id": "rnnoise-speech-probability",
        "category_boundary": "DET-01 adjacent speech probability",
        "relation": "A collateral speech-probability diagnostic is not an overlap detector and cannot estimate speaker count.",
        "not_overlap_evidence": True,
    },
    {
        "component_id": "hush",
        "category_boundary": "SPK-01 generic separation / enhancement",
        "relation": "The historical Hush AMI diagnostic constructs additive mixtures from non-overlap turns; it neither detects natural overlap nor counts speakers, and its target damage is a separation result.",
        "not_overlap_evidence": True,
    },
    {
        "component_id": "vctk-dns2020-ami-ears-and-smard-evidence-manifests",
        "category_boundary": "evidence foundation for manifests and rights",
        "relation": "The manifest row owns source/pair/group hashes and overlap prevention for other tasks; it is not an overlap-labeled reference or a detector.",
        "not_overlap_evidence": True,
    },
    {
        "component_id": "vadtoolkit-and-ami-scoring-tooling",
        "category_boundary": "DET-01 VAD scoring tooling",
        "relation": "The scorer and AMI word-interval tooling compute any-speech rates and boundary diagnostics; they do not compute overlap intervals or speaker-count error.",
        "not_overlap_evidence": True,
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "fixed-rms-vad", "evidence_status": "evaluated", "task": "SDK-FIXED-RMS-VAD"},
    {"component_id": "adaptive-energy-vad", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-ENERGY-VAD"},
    {"component_id": "webrtc-vad", "evidence_status": "evaluated", "task": "SDK-WEBRTC-VAD"},
    {"component_id": "speexdsp-vad", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-VAD"},
    {"component_id": "silero-vad-6-2-3-reference", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-6-2-3-REFERENCE"},
    {"component_id": "fast-vad-0-2-1", "evidence_status": "evaluated", "task": "SDK-FAST-VAD-0-2-1"},
    {"component_id": "earshot-1-2-2", "evidence_status": "evaluated", "task": "SDK-EARSHOT-1-2-2"},
    {"component_id": "rnnoise-speech-probability", "evidence_status": "partial", "task": "SDK-RNNOISE-SPEECH-PROBABILITY"},
    {"component_id": "hush", "evidence_status": "partial", "task": "SDK-HUSH"},
    {"component_id": "vctk-dns2020-ami-ears-and-smard-evidence-manifests", "evidence_status": "evaluated", "task": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS"},
    {"component_id": "vadtoolkit-and-ami-scoring-tooling", "evidence_status": "partial", "task": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING"},
    {"component_id": "pyannote-segmentation-vad", "evidence_status": "blocked", "task": "SDK-PYANNOTE-SEGMENTATION-VAD"},
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "bayesian-information-criterion-speaker-segmentation", "evidence_status": "considered", "task": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "resemblyzer-speaker-similarity-proxy", "evidence_status": "partial", "task": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"},
    {"component_id": "speechbrains-ecapa-speaker-similarity", "evidence_status": "partial", "task": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY"},
    {"component_id": "conv-tasnet", "evidence_status": "considered", "task": "SDK-CONV-TASNET"},
    {"component_id": "beam-tasnet-beam-guided-tasnet", "evidence_status": "blocked", "task": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET"},
    {"component_id": "target-speaker-extraction-family", "evidence_status": "blocked", "task": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"},
    {"component_id": "voicefilter", "evidence_status": "blocked", "task": "SDK-VOICEFILTER"},
    {"component_id": "voicefilter-lite-personal-vad", "evidence_status": "blocked", "task": "SDK-VOICEFILTER-LITE-PERSONAL-VAD"},
    {"component_id": "delay-and-sum-beamformer", "evidence_status": "considered", "task": "SDK-DELAY-AND-SUM-BEAMFORMER"},
    {"component_id": "mvdr-beamforming", "evidence_status": "considered", "task": "SDK-MVDR-BEAMFORMING"},
    {"component_id": "source-localization-direction-of-arrival", "evidence_status": "considered", "task": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"},
    {"component_id": "auxiva", "evidence_status": "considered", "task": "SDK-AUXIVA"},
    {"component_id": "spatialnet", "evidence_status": "blocked", "task": "SDK-SPATIALNET"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Three speaker-disjoint held-out AMI Mix-Headset meetings comparing seven any-speech VAD candidates on 20 ms frames",
        "class": "historical_local_adjacent_any_speech",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "boundary": "Any-speaker speech activity only; no overlap intervals, overlap labels, speaker-count labels or natural-overlap claim. Word-interval union with explicit unknown gaps and desktop replay.",
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
        "class": "historical_local_adjacent_synthetic_overlap_construction",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "boundary": "Constructed additive examples from non-overlap turns in one mono meeting; no natural overlap, isolated clean references, overlap detector or speaker-count estimate.",
    },
    {
        "id": "CI-4",
        "input": "pyannote segmentation model card (S02) and candidate-register descriptions",
        "class": "source_only_model_card",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Model-card/documentation scope only; no exact revision, weights, token, runtime, adapter or numeric parity is verified locally.",
    },
    {
        "id": "CI-5",
        "input": "Overlap and diarization corpus leads including DIHARD, CHiME, Basis Conversations, TurnBench, RealVAD, SmoothConv and MagicData-RAMC",
        "class": "source_reported_overlap_corpus_metadata",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Metadata and access-register entries only; no audio, labels, permissions, scored regions or development/evaluation split is staged. Some leads are gated, noncommercial or explicitly unsuitable for overlap truth.",
    },
    {
        "id": "CI-6",
        "input": "Rights-qualified natural overlap reference with speaker-level truth, any-speaker union, active-speaker count and explicit unknown regions",
        "class": "missing_rights_qualified_overlap_reference",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
        "boundary": "Missing. The contract requires speaker-level truth and any-speaker union to be preserved separately; neither artifact exists locally.",
    },
    {
        "id": "CI-7",
        "input": "Exact runnable pyannote segmentation or diarization candidate with pinned revision, weights, token, runtime and adapter",
        "class": "missing_pyannote_runtime_and_weights",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Missing. The candidate register and VAD/ASR audit report no staged weights, source checkout, adapter or inference for pyannote.",
    },
    {
        "id": "CI-8",
        "input": "Frozen overlap and speaker-count benchmark protocol with interval/time metrics, count strata and degenerate controls",
        "class": "missing_overlap_and_count_benchmark",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Missing. No overlap or count scorer, threshold policy, held-out split, failed-item accounting or submission policy is applied by this survey.",
    },
    {
        "id": "CI-9",
        "input": "Catalogued classical activity, spatial, array and BIC speaker-segmentation component rows",
        "class": "source_only_catalogued_classical_components",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata and source leads only; no calibrated array, multichannel overlap execution, BIC execution or speaker-count result exists.",
    },
    {
        "id": "CI-10",
        "input": "Catalogued ML segmentation, diarization, embedding and separation/extraction component rows",
        "class": "source_only_catalogued_ml_components",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; segmentation and extraction rows are blocked, diarization and embedding rows are considered, and no ML overlap or count execution exists.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "always-overlap and always-non-overlap diagnostics", "role": "Required degenerate detection controls that expose metric behavior; they are not product candidates and were not run on a valid overlap cohort.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-2", "name": "speaker-level truth versus any-speaker union", "role": "Both representations must be preserved; a union-only score cannot establish per-speaker overlap or active-speaker count.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
    {"id": "CT-3", "name": "unknown-region masking", "role": "Unannotated time is excluded, never relabelled nonspeech or non-overlap.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
    {"id": "CT-4", "name": "zero, one and multiple active-speaker strata", "role": "Count error must be reported by stratum including silence, single speaker, two speakers and three or more; aggregate accuracy alone hides counting failure.", "source_pin": "research/plans/F02/vad_sources.md"},
    {"id": "CT-5", "name": "identity / passthrough audio", "role": "Detection and counting never modify PCM; an identity control guards against a gate or separation being credited as detection.", "source_pin": "docs/task-evidence/hush/README.md"},
    {"id": "CT-6", "name": "calibrated array geometry and synchronized channels", "role": "Spatial statistics require a declared array, channel alignment and reference; mono activity evidence cannot validate a spatial overlap detector.", "source_pin": "docs/task-evidence/survey-cln-07/README.md"},
    {"id": "CT-7", "name": "synthetic mixture versus natural overlap", "role": "Constructed additive turns test robustness but do not substitute for naturally simultaneous speech, speaker overlap or count truth.", "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md"},
    {"id": "CT-8", "name": "any-speech VAD activity control", "role": "A speech-activity detector is a baseline for onset/offset behavior, not an overlap detector or speaker counter.", "source_pin": "docs/task-evidence/webrtc-vad/README.md"},
    {"id": "CT-9", "name": "missing, invalid, nonfinite and out-of-range interval rejection", "role": "Missing or malformed intervals are blocked, not scored; no missing result may qualify a candidate or produce a count.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "AMI Mix-Headset six-recording speech/non-speech reference used by the historical any-speech VAD comparison",
        "class": "research_speech_corpus_reference",
        "status": "CC BY 4.0 per the cited manifest; local only, not redistributed here, and it supplies any-speaker word intervals rather than overlap or speaker-count truth.",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
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
        "status": "Constructed from non-overlap turns in a mono meeting with speaker-dominant proxies; no isolated clean references, natural overlap or redistribution grant.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "asset": "pyannote segmentation model card (S02)",
        "class": "external_documentation",
        "status": "Direct documentation scope; no weights, token, exact revision, runtime or adapter.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Overlap and diarization corpus leads (DIHARD, CHiME, Basis Conversations, TurnBench, RealVAD, SmoothConv, MagicData-RAMC)",
        "class": "source_and_metadata_only",
        "status": "Lead register only; no audio, labels, rights, scored regions or partitions are staged, and several leads are gated or noncommercial.",
        "source_pin": "research/plans/F02/vad_sources.md",
    },
    {
        "asset": "Rights-qualified natural overlap corpus with speaker-level truth and active-speaker count",
        "class": "missing_corpus_assets",
        "status": "Not present; no consent, annotation protocol, unknown-region policy, count truth or independent split is available.",
        "source_pin": "research/plans/F02/vad_accuracy_contract.md",
    },
    {
        "asset": "pyannote segmentation/diarization checkpoint, token, runtime and adapter",
        "class": "missing_model_assets",
        "status": "Not staged; the segmentation row is blocked and the diarization row is considered, with no weights or inference.",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "Calibrated microphone array geometry and synchronized multichannel recordings",
        "class": "missing_spatial_assets",
        "status": "Not present; mono or uncalibrated evidence cannot support a spatial overlap family claim.",
        "source_pin": "docs/task-evidence/survey-cln-07/README.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Seven-candidate held-out AMI any-speech VAD comparison (adjacent activity only)",
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
        "values": {
            "heldout_meetings": 3,
            "candidates": 7,
            "scored_frame_ms": 20,
            "overlap_intervals_scored": 0,
            "overlap_detection_metric_rows": 0,
            "active_speaker_count_estimates": 0,
        },
        "scope": (
            "Historical local any-speaker VAD comparison on three speaker-disjoint "
            "AMI meetings; it is not an overlap or speaker-count result, not a "
            "natural-overlap measurement, not a target-device result and not "
            "rerun by this survey."
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
        "values": {
            "recordings": 4,
            "annotated_positive_spans": 588,
            "speaker_ids_supplied": False,
            "overlap_labels_supplied": False,
            "active_speaker_count_estimates": 0,
        },
        "scope": (
            "Historical positive-span-only VAD diagnostic; the complement is "
            "unknown, no speaker IDs or overlap convention exist, and it is not "
            "an overlap or speaker-count result and not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Hush synthetic AMI speaker-pair mixtures (adjacent overlap construction only)",
        "outcome_class": "historical_local_adjacent_synthetic_overlap_construction",
        "component_ids": ["hush"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "values": {
            "meetings": 1,
            "speaker_pairs": 7,
            "synthetic_mixtures": 21,
            "sir_strata_db": [12, 18, 24],
            "natural_overlap": False,
            "isolated_clean_references": False,
            "overlap_detection_components": 0,
            "active_speaker_count_estimates": 0,
        },
        "scope": (
            "Historical adjacent synthetic overlap construction from non-overlap "
            "AMI turns in one mono meeting; it is not natural overlap, not an "
            "overlap detection or speaker-count result, not a separation "
            "qualification and not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "pyannote segmentation model card describes a segmentation capability and access conditions for model files",
        "class": "source_reported_model_card",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Model-card/documentation scope only; no exact revision, weights, token, runtime, adapter or overlap/speaker-count metric is reproduced locally.",
    },
    {
        "id": "RO-2",
        "claim": "pyannote diarization is catalogued as a considered spatial/speaker row",
        "class": "source_reported_plan_row",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; no local diarization execution, active-speaker-count metric or identity result exists.",
    },
    {
        "id": "RO-3",
        "claim": "Overlap and diarization corpus leads report annotation protocols, access conditions and overlap metadata",
        "class": "source_reported_corpus_metadata",
        "source_pin": "research/plans/F02/vad_sources.md",
        "boundary": "Metadata only; no audio, labels, rights, scored regions or partitions are staged, and no source is accepted as overlap truth.",
    },
    {
        "id": "RO-4",
        "claim": "BIC speaker segmentation, beamforming and direction-of-arrival rows are catalogued classical leads",
        "class": "source_reported_plan_row",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata only; no local BIC, array, beamformer or localization execution and no overlap result.",
    },
    {
        "id": "RO-5",
        "claim": "X-vector speaker embeddings and the local Resemblyzer / ECAPA similarity proxies are adjacent identity controls",
        "class": "source_reported_research_control",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Identity and similarity scope only; they do not provide active-speaker count or overlap truth and are not pooled here.",
    },
    {
        "id": "RO-6",
        "claim": "Conv-TasNet, Beam-TasNet, VoiceFilter and target-speaker extraction family rows are catalogued separation/extraction candidates",
        "class": "source_reported_plan_row",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Separation/extraction candidates only; no overlap detector, count estimate, clean-target overlap corpus or local execution exists.",
    },
    {
        "id": "RO-7",
        "claim": "The historical AMI VAD evaluation is not broad multilingual, accent, overlap or device validation",
        "class": "source_reported_adjacent_scope",
        "source_pin": "research/voice-enhancement-20261101/evaluation_records.md",
        "boundary": "Scope statement transcribed from the pinned evaluation record; it explicitly excludes overlap and speaker-count validation.",
    },
]

EXECUTION_COVERAGE: Dict[str, Any] = {
    "dedicated_overlap_detection_component_count": 0,
    "dedicated_speaker_count_component_count": 0,
    "locally_evaluated_overlap_detection_component_count": 0,
    "locally_evaluated_speaker_count_component_count": 0,
    "adjacent_any_speech_execution_count": 2,
    "adjacent_synthetic_overlap_construction_execution_count": 1,
    "pyannote_execution_count": 0,
    "neural_overlap_or_count_execution_count": 0,
    "natural_overlap_local_execution_count": 0,
    "calibrated_array_overlap_execution_count": 0,
    "real_overlap_corpus_execution_count": 0,
    "device_timing_execution_count": 0,
    "note": (
        "No dedicated overlap or speaker-count component is catalogued or "
        "executed. Two historical local rows are any-speech VAD diagnostics and "
        "one constructs synthetic additive mixtures from non-overlap turns. "
        "Pyannote, diarization, array, BIC, embedding and extraction rows have "
        "no local execution, overlap metric or speaker-count result."
    ),
}

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "timestamped_probabilities_and_events": "No overlap probabilities or events were executed; HE-1 transcribes only 20 ms any-speech VAD decisions.",
        "quiet_and_active_speech": "AMI supplies speech and nonspeech for VAD; quiet-speech and overlap strata are unavailable and not inferred.",
        "known_positives_and_negatives": "AMI word intervals are any-speech truth; audEERING keeps the complement unknown; neither is overlap truth.",
        "onset_offset_delay": "Adjacent VAD boundary diagnostics exist; overlap onset/offset and count-transition timing are absent.",
        "stratified_fn_fp": "No overlap false-alarm/miss or count-error strata exist; VAD strata are recording-level only.",
        "validity_vs_nonspeech": "CT-3 keeps unknown time unknown; invalid or missing intervals fail closed under CT-9.",
        "exact_source_intervals": "No overlap intervals exist; adjacent VAD intervals are 20 ms projections, not hand-measured overlap boundaries.",
        "independent_state": "No streaming overlap detector, diarization state or count reset behavior was tested.",
        "availability_and_dropped_stale_events": "No availability clock or dropped/stale event measurement exists.",
        "cross_hop_behavior": "No overlap detector cadence, lookahead or cross-hop behavior was measured.",
    },
    "blocked": [
        "Rights-qualified natural overlap corpus with speaker-level truth, any-speaker union, count truth and explicit unknown regions",
        "Frozen speaker/session/group-disjoint development and held-out partitions with independent label review",
        "Matched always-overlap, always-non-overlap, any-speech and count controls with interval, time and count uncertainty",
        "Pinned pyannote segmentation/diarization weights, token, exact revision, runtime and adapter",
        "Calibrated array geometry and synchronized multichannel evidence for spatial families",
        "Paced target-device availability, memory, deadline and clock evidence",
        "Frozen overlap and active-speaker-count protocol with a held-out scorer and failed-item accounting",
        "Opt-in provider intake, independent exact-head review and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "adjacent_any_speech_historical_local": True,
    "adjacent_positive_only_historical_local": True,
    "adjacent_synthetic_overlap_construction_historical_local": True,
    "source_reported_only": True,
    "missing_rights_qualified_overlap_reference": True,
    "missing_pyannote_runtime_and_weights": True,
    "missing_overlap_and_count_benchmark": True,
    "overlap_detection_execution": False,
    "speaker_count_execution": False,
    "pyannote_local_execution": False,
    "natural_overlap_local_execution": False,
    "calibrated_array_overlap_execution": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "clean_reference_accuracy_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified natural overlap corpus with speaker-level truth, any-speaker union, active-speaker count and explicit unknown regions",
        "evidence_gap": "AMI is any-speech VAD data, audEERING is positive-only and Hush uses synthetic non-overlap turns; no overlap labels, count truth or permissions are staged.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated overlap-corpus task exists; the linked research-control and foundation rows own manifests, VAD scoring and evidence rules, not a new corpus or rights grant.",
    },
    {
        "id": "G02",
        "actionable_gap": "Define and validate overlap interval/time metrics and active-speaker-count error with degenerate controls",
        "evidence_gap": "No overlap precision/recall, overlap duration, onset/offset, count error or zero/one/two-plus strata are implemented or scored.",
        "follow_up_ids": [
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated overlap-scorer task exists; the linked research-control and foundation rows own the existing VAD scorer and general evidence protocol only.",
    },
    {
        "id": "G03",
        "actionable_gap": "Evaluate spatial-statistics overlap detection with calibrated geometry, synchronized channels and declared echo/noise conditions",
        "evidence_gap": "Delay-and-sum, MVDR, AuxIVA, SpatialNet and direction-of-arrival rows are considered or blocked; no array, geometry or multichannel overlap execution exists.",
        "follow_up_ids": [
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
            "SDK-MVDR-BEAMFORMING",
            "SDK-DELAY-AND-SUM-BEAMFORMER",
            "SDK-SPATIALNET",
        ],
        "feasibility_task_exists": True,
        "owner_note": "All five linked spatial rows are feasibility scoping leads; none stages array geometry, weights or an overlap result.",
    },
    {
        "id": "G04",
        "actionable_gap": "Keep overlap detection separate from beamforming, localization, separation and target-speaker extraction",
        "evidence_gap": "Neighboring beamforming, separation and extraction rows have no overlap output; no cross-category ablation or abstention policy exists.",
        "follow_up_ids": [
            "SDK-SURVEY-CLN-07",
            "SDK-SURVEY-CLN-08",
            "SDK-SURVEY-SPK-01",
            "SDK-SURVEY-SPK-02",
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The taxonomy rows keep the definitions separate and the extraction row is a feasibility lead; none enables a detector or separation result.",
    },
    {
        "id": "G05",
        "actionable_gap": "Assess BIC speaker-change segmentation as a boundary and count lead without treating it as overlap truth",
        "evidence_gap": "The BIC row is considered only; no local implementation, change-boundary score, overlap interval or count estimate exists.",
        "follow_up_ids": [
            "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION",
            "SDK-SURVEY-SPK-03",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The BIC feasibility row and speaker-change taxonomy row are scoping leads only; no boundary or count result is claimed.",
    },
    {
        "id": "G06",
        "actionable_gap": "Pin pyannote segmentation and diarization with exact revision, weights, token, runtime, adapter and output semantics",
        "evidence_gap": "Pyannote segmentation is blocked and diarization is considered; the candidate register and audit report no staged weights, source checkout, adapter or inference.",
        "follow_up_ids": [
            "SDK-PYANNOTE-SEGMENTATION-VAD",
            "SDK-PYANNOTE-DIARIZATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "Both pyannote rows are feasibility scoping leads; neither enables a model, stages weights or establishes overlap/count capability.",
    },
    {
        "id": "G07",
        "actionable_gap": "Evaluate speaker embeddings and clustering for active-speaker count without identity or unwanted-speech claims",
        "evidence_gap": "X-vector is considered and the Resemblyzer/ECAPA rows are partial similarity proxies; no count execution, overlap truth or calibrated clustering policy exists.",
        "follow_up_ids": [
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
            "SDK-SURVEY-SPK-04",
            "SDK-SURVEY-SPK-05",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The embedding row is a feasibility lead and the diarization/identity taxonomy rows keep count, anonymous diarization and identity separate.",
    },
    {
        "id": "G08",
        "actionable_gap": "Prevent overlap detection from becoming diarization, target-speaker VAD, separation or muting",
        "evidence_gap": "Adjacent rows declare different outputs; no local component exposes a stable overlap interval plus count contract or an abstention boundary.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-05",
            "SDK-SURVEY-SPK-02",
            "SDK-SURVEY-SPK-04",
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked taxonomy and personal-VAD feasibility rows keep detection, extraction, diarization and identity separate; none is an overlap detector.",
    },
    {
        "id": "G09",
        "actionable_gap": "Collect streaming target-device timing, memory, deadline and availability evidence for overlap detection and count",
        "evidence_gap": "No overlap or count runtime exists; adjacent VAD numbers are desktop, accelerated or batch values and cannot establish a live detector.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated overlap-device task exists; the foundation rows own lifecycle/timing and evidence rules, not a device measurement.",
    },
    {
        "id": "G10",
        "actionable_gap": "Require independent exact-head review and explicit release approval before any benchmark, default or release claim",
        "evidence_gap": "This proposal-only map has no independent reviewer, no overlap/count benchmark and no default-selection or release approval.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "BENCH-FND-CHECK",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated DET-03 review task exists; the foundation rows own evidence and acceptance templates, not independent approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "BENCH-FND-CHECK", "title": "Benchmark acceptance and rights-safe evidence templates", "mode": "foundation"},
    {"task_id": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT", "title": "3D microphone spatial / time alignment", "mode": "feasibility"},
    {"task_id": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION", "title": "Bayesian information criterion speaker segmentation", "mode": "feasibility"},
    {"task_id": "SDK-DELAY-AND-SUM-BEAMFORMER", "title": "Delay-and-sum beamformer", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-MVDR-BEAMFORMING", "title": "MVDR beamforming", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-DIARIZATION", "title": "pyannote diarization", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-SEGMENTATION-VAD", "title": "pyannote segmentation / VAD", "mode": "feasibility"},
    {"task_id": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL", "title": "Source localization / direction-of-arrival", "mode": "feasibility"},
    {"task_id": "SDK-SPATIALNET", "title": "SpatialNet", "mode": "feasibility"},
    {"task_id": "SDK-SURVEY-CLN-07", "title": "Review coverage for Beamforming and spatial filtering", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-CLN-08", "title": "Review coverage for Source localization and tracking", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-DET-05", "title": "Review coverage for Target-speaker / personalized VAD", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-01", "title": "Review coverage for Generic speech/source separation", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-02", "title": "Review coverage for Target-speaker extraction and personalized enhancement", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-03", "title": "Review coverage for Speaker change detection and segmentation", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-04", "title": "Review coverage for Anonymous speaker diarization", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-05", "title": "Review coverage for Speaker representation, identification and verification", "mode": "taxonomy"},
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING", "title": "VADToolkit and AMI scoring tooling", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified natural overlap reference with speaker-level truth, any-speaker union, count truth, explicit unknown regions and permissions"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen speaker/session/group-disjoint development and held-out partitions with independent label review"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched always-overlap, always-non-overlap, any-speech and count controls with full interval, time and uncertainty evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned pyannote segmentation/diarization, embedding and spatial runtimes, weights and exact revisions for every claimed candidate"},
    {"id": "RG-05", "blocked": True, "requirement": "Calibrated microphone-array geometry and synchronized multichannel evidence for every spatial-family claim"},
    {"id": "RG-06", "blocked": True, "requirement": "Paced target-device availability, memory, deadline and clock evidence for streaming overlap detection and count"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake, independent exact-head review, and separation from separation/extraction/diarization/muting"},
    {"id": "RG-08", "blocked": True, "requirement": "Explicit public default selection and release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated facts and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **DET-03 \u2014 Overlapping speech detection and speaker count** | Detect simultaneous speech; estimate active speaker count where supported. Scope: discovered_extension. | Activity/spatial statistics | Multi-label segmentation and counting models | Audio \u2192 overlap intervals/count estimates | Detection neither separates waveforms nor identifies unwanted speech. | [S02](https://huggingface.co/pyannote/segmentation) |",
    ],
    "research/category_survey/sources.md": [
        "| S02 | [pyannote segmentation model card](https://huggingface.co/pyannote/segmentation) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Analysis | Score timestamped probabilities, event boundaries and detections.",
    ],
    "audio-benchmark-platform/plan/INVENTORY.json": [
        '"id": "DET-03",',
        '"id": "pyannote-segmentation-vad",',
        '"id": "bayesian-information-criterion-speaker-segmentation",',
    ],
    "research/category_registry.json": [
        '"id": "DET-03",',
        '"id": "S02",',
    ],
    "research/task_backlog.json": [
        '"category_id":"DET-03","dependencies":[],"family_id":"F05"',
    ],
    "research/plans/F02/vad_sources.md": [
        "11.38% mean overlap",
        "overlap scoring and no forgiveness collar",
        "thesis states no concurrent speakers in this discussion",
        "overlap/backchannels",
    ],
    "research/plans/F02/vad_accuracy_contract.md": [
        "For overlap, define and preserve speaker-level truth and any-speaker union separately.",
        "Unknown or unannotated time is never nonspeech.",
        "**Current strata are recording-level only**",
    ],
    "research/pilot_evaluation_progress.md": [
        "Preserve separate speaker activity and any-speaker union when overlap labels exist",
    ],
    "reports/vad-research/chaining-evaluation.md": [
        "six official AMI Mix-Headset recordings",
        "overlap, non-speech vocalizations, quiet and noisy conditions",
    ],
    "reports/vad-research/20261028-synthesis-v7.md": [
        "**No best VAD is selected.**",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Additional TEN VAD / PulseVAD / FSMN / MarbleNet / FireRedVAD / pyannote",
        "No exact candidate weights, source checkout, or adapter are staged",
    ],
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": [
        "pyannote | researched but not run",
    ],
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": [
        "No corresponding model weights, checkpoint or adapter are staged",
    ],
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": [
        "No local model or result found in the workspace audit.",
        "Requires synchronized array channels and array geometry/data",
    ],
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": [
        "seven distinct directed speaker pairs",
        "constructed additive examples rather than naturally simultaneous overlap",
    ],
    "research/voice-enhancement-20261101/evaluation_records.md": [
        "not broad multilingual/accent/overlap/device validation",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/hush/README.md": [
        "Task-local, **proposal-only**, **incomplete** and **not qualified** evidence",
    ],
    "docs/task-evidence/survey-cln-07/README.md": [
        "are named only as boundaries. Their results are",
        "not pooled here",
    ],
    "docs/task-evidence/survey-cln-08/README.md": [
        "source localization and tracking",
    ],
    "docs/task-evidence/survey-det-01/README.md": [
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
    "real_overlap_audio": False,
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
    "overlap_claim_without_overlap_execution": "rejected; state unchanged",
    "speaker_count_claim_without_count_execution": "rejected; state unchanged",
    "pyannote_claim_without_weights_or_runtime": "rejected; state unchanged",
    "synthetic_mixture_relabelled_natural_overlap": "rejected; state unchanged",
    "any_speech_vad_promoted_to_overlap_detection": "rejected; state unchanged",
    "diarization_promoted_to_overlap_detection": "rejected; state unchanged",
    "author_reported_promoted_to_local_execution": "rejected; state unchanged",
    "heldout_benchmark_claim_without_labelled_split": "rejected; state unchanged",
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
        raise MapError("DET-03 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("DET-03 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F05 / DET-03 is not unique")
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
            raise MapError("legacy backlog mismatch: F05/DET-03/%s" % key)


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
        "historical_local_adjacent_synthetic_overlap_construction",
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
        if row.get("outcome_class") not in allowed_classes:
            raise MapError("historical execution is not explicitly adjacent: " + row["id"])
        scope = row.get("scope", "")
        if "not rerun by this survey" not in scope:
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])
        if "not an overlap" not in scope and "not an overlap or speaker-count" not in scope:
            raise MapError("historical execution is not labelled non-overlap: " + row["id"])
        if not row.get("values"):
            raise MapError("historical execution has no values: " + row["id"])
        if row.get("source_pin") not in SOURCE_PINS:
            raise MapError("historical execution is not pinned to a source report: " + row["id"])


def _check_evidence_classes() -> None:
    input_classes = {row["class"] for row in COMPARISON_INPUTS}
    checks = {
        "adjacent_any_speech_historical_local": "historical_local_adjacent_any_speech" in input_classes,
        "adjacent_positive_only_historical_local": "historical_local_adjacent_positive_only" in input_classes,
        "adjacent_synthetic_overlap_construction_historical_local": "historical_local_adjacent_synthetic_overlap_construction" in input_classes,
        "source_reported_only": any(row["class"].startswith("source_reported") for row in REPORTED_OUTCOMES),
        "missing_rights_qualified_overlap_reference": "missing_rights_qualified_overlap_reference" in input_classes,
        "missing_pyannote_runtime_and_weights": "missing_pyannote_runtime_and_weights" in input_classes,
        "missing_overlap_and_count_benchmark": "missing_overlap_and_count_benchmark" in input_classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "overlap_detection_execution",
        "speaker_count_execution",
        "pyannote_local_execution",
        "natural_overlap_local_execution",
        "calibrated_array_overlap_execution",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "clean_reference_accuracy_claim",
        "release_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported claim is not closed: " + key)
    if not any(row["class"].startswith("source_reported") for row in REPORTED_OUTCOMES):
        raise MapError("source-reported class has no backing row")


def _check_execution_coverage() -> None:
    zero_counts = (
        "dedicated_overlap_detection_component_count",
        "dedicated_speaker_count_component_count",
        "locally_evaluated_overlap_detection_component_count",
        "locally_evaluated_speaker_count_component_count",
        "pyannote_execution_count",
        "neural_overlap_or_count_execution_count",
        "natural_overlap_local_execution_count",
        "calibrated_array_overlap_execution_count",
        "real_overlap_corpus_execution_count",
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
        if r["outcome_class"] == "historical_local_adjacent_synthetic_overlap_construction"
    ]
    if len(any_speech) + len(positive) != EXECUTION_COVERAGE["adjacent_any_speech_execution_count"]:
        raise MapError("adjacent any-speech execution count is inconsistent")
    if len(synthetic) != EXECUTION_COVERAGE["adjacent_synthetic_overlap_construction_execution_count"]:
        raise MapError("synthetic overlap construction count is inconsistent")
    if any("overlap_detection" in row["outcome_class"] for row in HISTORICAL_EXECUTIONS):
        raise MapError("an adjacent execution is relabelled as overlap detection")
    if any("speaker_count" in row["outcome_class"] for row in HISTORICAL_EXECUTIONS):
        raise MapError("an adjacent execution is relabelled as speaker count")


def _check_overlap_boundary() -> None:
    required_true = (
        "overlap_detection_only",
        "not_source_separation",
        "not_target_speaker_extraction",
        "not_muting_or_unwanted_speech_identification",
        "diarization_is_adjacent_not_overlap_detection",
        "speaker_count_is_not_speaker_identity",
        "energy_vad_is_not_overlap_detection",
        "spatial_statistics_require_calibrated_array_geometry",
        "speaker_level_truth_and_any_speaker_union_kept_separate",
        "unknown_time_is_never_nonspeech",
        "synthetic_mixture_is_not_natural_overlap",
        "author_reported_is_not_local",
    )
    required_false = (
        "overlap_detection_execution_present",
        "speaker_count_execution_present",
        "natural_overlap_local_execution_present",
        "pyannote_runtime_or_weights_present",
        "rights_qualified_overlap_corpus_present",
        "speaker_level_truth_present",
        "calibrated_array_geometry_present",
        "device_timing_present",
        "human_listening_result_present",
        "benchmark_or_release_qualification_present",
    )
    if set(OVERLAP_BOUNDARY) != set(required_true) | set(required_false):
        raise MapError("overlap boundary keys changed")
    for key in required_true:
        if OVERLAP_BOUNDARY[key] is not True:
            raise MapError("overlap boundary rule is not enforced: " + key)
    for key in required_false:
        if OVERLAP_BOUNDARY[key] is not False:
            raise MapError("overlap boundary claim is not closed: " + key)


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
    _check_overlap_boundary()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
    by_id = {t["id"]: t for t in board["tasks"]}
    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
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
            "overlap_detection_execution_present": False,
            "speaker_count_execution_present": False,
            "pyannote_execution_present": False,
            "release_qualification_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "overlap_boundary": dict(OVERLAP_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "dedicated_overlap_component_ids": [],
            "dedicated_speaker_count_component_ids": [],
            "adjacent_any_speech_component_ids": [
                "fixed-rms-vad",
                "adaptive-energy-vad",
                "webrtc-vad",
                "speexdsp-vad",
                "silero-vad-6-2-3-reference",
                "fast-vad-0-2-1",
                "earshot-1-2-2",
            ],
            "adjacent_spatial_component_ids": [
                "delay-and-sum-beamformer",
                "mvdr-beamforming",
                "source-localization-direction-of-arrival",
                "auxiva",
                "spatialnet",
            ],
            "adjacent_ml_component_ids": [
                "pyannote-segmentation-vad",
                "pyannote-diarization",
                "x-vector-speaker-embeddings",
                "bayesian-information-criterion-speaker-segmentation",
            ],
            "adjacent_local_execution_present": True,
            "dedicated_overlap_execution_present": False,
            "speaker_count_execution_present": False,
            "natural_overlap_corpus_present": False,
            "pyannote_weights_present": False,
            "calibrated_array_present": False,
            "heldout_overlap_split_present": False,
            "benchmark_protocol_present": False,
            "note": (
                "No dedicated DET-03 overlap or speaker-count component is "
                "catalogued. Adjacent any-speech VAD has local historical "
                "evidence, but pyannote, diarization, embedding, BIC and spatial "
                "rows have no staged weights, runtime, calibrated array or "
                "natural-overlap execution."
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
    if report["qualification"]["overlap_detection_execution_present"] is not False:
        raise MapError("an overlap detection execution is claimed")
    if report["qualification"]["speaker_count_execution_present"] is not False:
        raise MapError("a speaker count execution is claimed")
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
        "real_overlap_audio",
        "weights",
        "runtime_invocation",
        "listening",
        "device_timing",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    ):
        if report["scope"][key] is not False:
            raise MapError("scope claim is not closed: " + key)
    for key in (
        "adjacent_local_execution_present",
    ):
        if report["discovery"][key] is not True:
            raise MapError("adjacent local execution is not recorded: " + key)
    for key in (
        "dedicated_overlap_execution_present",
        "speaker_count_execution_present",
        "natural_overlap_corpus_present",
        "pyannote_weights_present",
        "calibrated_array_present",
        "heldout_overlap_split_present",
        "benchmark_protocol_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    for key in (
        "overlap_detection_execution",
        "speaker_count_execution",
        "pyannote_local_execution",
        "natural_overlap_local_execution",
        "calibrated_array_overlap_execution",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "clean_reference_accuracy_claim",
        "release_claim",
    ):
        if report["evidence_classes"][key] is not False:
            raise MapError("unsupported evidence class is open: " + key)
    if report["evidence_classes"]["adjacent_any_speech_historical_local"] is not True:
        raise MapError("adjacent any-speech evidence is not recorded")
    if report["evidence_classes"]["adjacent_positive_only_historical_local"] is not True:
        raise MapError("adjacent positive-only evidence is not recorded")
    if report["evidence_classes"]["adjacent_synthetic_overlap_construction_historical_local"] is not True:
        raise MapError("adjacent synthetic overlap construction is not recorded")
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
