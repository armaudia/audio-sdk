# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-DET-01.

This module builds a bounded taxonomy/comparison evidence map for the
speech-activity-detection category (inventory category ``DET-01``, legacy
family ``F02``). It reads only pinned, read-only documents from the enclosing
``audioml`` workspace and the SDK worktree. It does not load audio, weights,
runtimes, media or the network, and it does not register, expose, enable or
qualify any detector.

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
TASK = "SDK-SURVEY-DET-01"
TITLE = "Review coverage for Speech activity detection (VAD/SAD)"
CATEGORY_ID = "DET-01"
LEGACY_FAMILY = "F02"
BRANCH = "swarm/SDK-SURVEY-DET-01"
BASE_COMMIT = "245d9ad3854d5dcddb223d686a45f2230a9dc5c3"
PROFILE = "Analysis"
COMPONENT = "speech-activity-detection-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

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
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "reports/vad-research/20261028-synthesis-v7.md": "2bc353e9d6d648a7e58204e202a5f4a03b75859b58f3fd515ec37216168a5a6c",
    "reports/vad-research/chaining-evaluation.md": "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/plans/F02/readiness_review.md": "c29741e8e5885e4c4ec7daa7c85be9d3362c99721010a05d9b4532876bcff28a",
    "research/plans/F02/vad_accuracy_contract.md": "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
    "research/plans/F02/vad_plan.md": "d1310765159c70db08fd7c2c3ed29d57ecc64cd670c6bde778ba66ec84c0c8dc",
    "research/plans/F02/vad_sources.md": "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-vad-chain-followup/REPORT.md": "4e1de799b62ab7fee1a0def421ed9d152d1ccdb0c966141e9bc09ddb5e6e10b2",
    "research/voice-enhancement-20261101/agent-vad-expanded/REPORT.md": "40cae724ba1f607e67cc89a1fda16d744cdf66ace305395fed649c6d3507660c",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/findings.md": "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/adaptive-energy-to-silero-cascade/README.md": "1e2632185f1e90d208958d2e49a1c2efc6eda5909e75e695d215cbea83d4b8a9",
    "docs/task-evidence/adaptive-energy-vad/README.md": "2de4b185d679f031c80625bd64e195cbabb69c62ea9499ef99f9868752ed86a2",
    "docs/task-evidence/fast-vad-0-2-1/README.md": "950bedaaa33b47cca85238f9398db10d8408da81f8034fd97687de1e61a0cc76",
    "docs/task-evidence/fixed-rms-vad/README.md": "05ad47c5f2746cb5d5d5b1bbc898796b00ea4f84db9f17560869d42556d58751",
    "docs/task-evidence/rnnoise-speech-probability/README.md": "968ca6cdf8cf59345aa015bc05d216c2800497b667b2eaa4aae31073bd2f4730",
    "docs/task-evidence/speexdsp-vad/README.md": "803b1893ac75c8f2c452d2a28c02dc979ba65c23e67af3079b148fb1f80a3177",
    "docs/task-evidence/webrtc-vad/README.md": "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Detection and control",
    "name": "Speech activity detection (VAD/SAD)",
    "scope": "requested",
    "output_kind": "annotation/control",
    "purpose": "Find speech regions without identifying the speaker.",
    "method_families": {
        "classic": "Energy/band statistics; GMM likelihoods; thresholds and hangover",
        "ml": "Neural frame classification or segmentation",
    },
    "input_output": "Audio \u2192 speech scores and intervals",
    "live_or_comparison_boundary": (
        "Do not equate VAD with muting or with target-speaker selection. "
        "Measure onset/offset misses and quiet speech."
    ),
    "source_ids": ["S01", "S02"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S01",
        "title": "WebRTC speech activity detector source",
        "url": (
            "https://webrtc.googlesource.com/src/+/refs/heads/main/"
            "common_audio/vad/vad_core.c"
        ),
        "access_scope": "direct",
        "mapped_components": ["webrtc-vad"],
        "gap_ids": ["G02", "G10"],
        "finding": (
            "Direct source lead for the GMM-likelihood, hangover-based classic "
            "detector. A task-local synthetic 160-sample surrogate and a "
            "historical seven-candidate held-out AMI comparison exist; the "
            "historical WebRTC row reports FN 7.31% and FP 49.54% at 6.38 "
            "microseconds per 20 ms frame on a desktop. No local WebRTC runtime, "
            "native parity, real corpus or target-device timing is present here."
        ),
    },
    {
        "source_id": "S02",
        "title": "pyannote segmentation model card",
        "url": "https://huggingface.co/pyannote/segmentation",
        "access_scope": "direct",
        "mapped_components": ["pyannote-segmentation-vad"],
        "gap_ids": ["G05"],
        "finding": (
            "Direct documentation lead only. The inventory row is blocked: no "
            "weights, exact revision, runtime, adapter or local execution was "
            "found, and no segmentation accuracy is transferred from the card."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Energy/band-statistics thresholds with fixed or adaptive noise floor",
        "components": ["fixed-rms-vad", "adaptive-energy-vad"],
        "gap_ids": ["G01", "G02"],
        "status": "historical_local_heldout_and_synthetic_fixture",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "GMM likelihood with threshold and hangover (named source lead S01)",
        "components": ["webrtc-vad"],
        "gap_ids": ["G02", "G10"],
        "status": "historical_local_heldout_and_synthetic_fixture",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Voice-focused SpeexDSP adaptive preprocessor VAD",
        "components": ["speexdsp-vad"],
        "gap_ids": ["G02"],
        "status": "historical_local_heldout_and_synthetic_fixture",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Cheap classical gate with expensive-neural scheduler or cascade",
        "components": [
            "adaptive-energy-to-silero-cascade",
            "adaptive-energy-silero-scheduler-implementation",
        ],
        "gap_ids": ["G03", "G11"],
        "status": "historical_policy_replay_and_local_model_free_fixture",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Small causal neural frame classifiers and stateful streaming detectors",
        "components": [
            "fast-vad-0-2-1",
            "earshot-1-2-2",
            "silero-vad-6-2-3-reference",
            "silero-vad-v5-onnx-reference",
        ],
        "gap_ids": ["G04", "G07"],
        "status": "historical_local_heldout_and_local_synthetic_surrogate",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Neural segmentation and larger frame-classification families",
        "components": [
            "pyannote-segmentation-vad",
            "wav2vec2-xls-r-transformer-vad",
            "cnn-bilstm-vad",
            "crnn-vad",
            "marblenet-vad",
            "fsmn-vad",
            "fireredvad",
            "pulsevad",
            "ten-vad",
        ],
        "gap_ids": ["G05", "G06"],
        "status": "no_local_execution_in_reviewed_records",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Speech probability as a collateral output of suppression or AGC",
        "components": [
            "rnnoise-speech-probability",
            "speex-agc-and-activity-output",
            "native-speex-ns-activity-shared-preprocessing",
        ],
        "gap_ids": ["G02", "G09"],
        "status": "historical_adjacent_diagnostic_and_synthetic_fixture",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "VAD-conditioned downstream pause, regression or playback policy",
        "components": [
            "silero-vad-pause-duration-rules",
            "silero-vad-opensmile-small-regression-head",
            "source-vad-conditioning-for-playback",
        ],
        "gap_ids": ["G08", "G09"],
        "status": "local_rate_profile_and_considered_only",
    },
]

# component_id and task/evidence_status are checked against plan/INVENTORY.json.
# Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "fixed-rms-vad", "evidence_status": "evaluated", "task": "SDK-FIXED-RMS-VAD"},
    {"component_id": "adaptive-energy-vad", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-ENERGY-VAD"},
    {"component_id": "webrtc-vad", "evidence_status": "evaluated", "task": "SDK-WEBRTC-VAD"},
    {"component_id": "speexdsp-vad", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-VAD"},
    {"component_id": "speex-agc-and-activity-output", "evidence_status": "partial", "task": "SDK-SPEEX-AGC-AND-ACTIVITY-OUTPUT"},
    {"component_id": "adaptive-energy-to-silero-cascade", "evidence_status": "partial", "task": "SDK-ADAPTIVE-ENERGY-TO-SILERO-CASCADE"},
    {"component_id": "adaptive-energy-silero-scheduler-implementation", "evidence_status": "native-local", "task": "PRO-ADAPTIVE-ENERGY-SILERO-SCHEDULER-IMPLEMENTATION"},
    {"component_id": "fast-vad-0-2-1", "evidence_status": "evaluated", "task": "SDK-FAST-VAD-0-2-1"},
    {"component_id": "earshot-1-2-2", "evidence_status": "evaluated", "task": "SDK-EARSHOT-1-2-2"},
    {"component_id": "silero-vad-6-2-3-reference", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-6-2-3-REFERENCE"},
    {"component_id": "silero-vad-v5-onnx-reference", "evidence_status": "source-local", "task": "SDK-SILERO-VAD-V5-ONNX-REFERENCE"},
    {"component_id": "silero-vad-pause-duration-rules", "evidence_status": "partial", "task": "SDK-SILERO-VAD-PAUSE-DURATION-RULES"},
    {"component_id": "silero-vad-opensmile-small-regression-head", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD"},
    {"component_id": "rnnoise-speech-probability", "evidence_status": "partial", "task": "SDK-RNNOISE-SPEECH-PROBABILITY"},
    {"component_id": "native-speex-ns-activity-shared-preprocessing", "evidence_status": "native-local", "task": "PRO-NATIVE-SPEEX-NS-ACTIVITY-SHARED-PREPROCESSING"},
    {"component_id": "pyannote-segmentation-vad", "evidence_status": "blocked", "task": "SDK-PYANNOTE-SEGMENTATION-VAD"},
    {"component_id": "wav2vec2-xls-r-transformer-vad", "evidence_status": "considered", "task": "SDK-WAV2VEC2-XLS-R-TRANSFORMER-VAD"},
    {"component_id": "cnn-bilstm-vad", "evidence_status": "considered", "task": "SDK-CNN-BILSTM-VAD"},
    {"component_id": "crnn-vad", "evidence_status": "blocked", "task": "SDK-CRNN-VAD"},
    {"component_id": "marblenet-vad", "evidence_status": "blocked", "task": "SDK-MARBLENET-VAD"},
    {"component_id": "fsmn-vad", "evidence_status": "blocked", "task": "SDK-FSMN-VAD"},
    {"component_id": "fireredvad", "evidence_status": "blocked", "task": "SDK-FIREREDVAD"},
    {"component_id": "pulsevad", "evidence_status": "blocked", "task": "SDK-PULSEVAD"},
    {"component_id": "ten-vad", "evidence_status": "blocked", "task": "SDK-TEN-VAD"},
    {"component_id": "source-vad-conditioning-for-playback", "evidence_status": "considered", "task": "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK"},
    {"component_id": "vadtoolkit-and-ami-scoring-tooling", "evidence_status": "partial", "task": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING"},
    {"component_id": "historical-mobile-vad-fastenhancer-wpe-chain", "evidence_status": "partial", "task": "PRO-HISTORICAL-MOBILE-VAD-FASTENHANCER-WPE-CHAIN"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Three speaker-disjoint held-out AMI Mix-Headset meetings (ES2008a, IS1003a, EN2003a)",
        "class": "historical_local_heldout_real_meeting",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "boundary": "Word-interval union with explicit unknown gaps; boundaries are forced-alignment timings, not hand-measured onsets; desktop only.",
    },
    {
        "id": "CI-2",
        "input": "Six synthetic cross-environment recordings (vad-chaining-fixture-v1, 517.75 s)",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/voice-enhancement-20261101/agent-vad-expanded/REPORT.md",
        "boundary": "Generated noise-only negatives and reused audEERING speech excerpts; not independent speakers or natural conversation.",
    },
    {
        "id": "CI-3",
        "input": "Four audEERING vadtoolkit 1.1.0 recordings scored only inside 588 positive spans",
        "class": "historical_local_positive_span_only",
        "source_pin": "reports/vad-research/20261028-synthesis-v7.md",
        "boundary": "Complement is unknown, so false alarms and full accuracy are not computable; zero miss rate can mean overtriggering.",
    },
    {
        "id": "CI-4",
        "input": "Three label-balanced 60 s AMI windows for an RNNoise speech-probability side diagnostic",
        "class": "historical_local_adjacent_speech_probability",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Exploratory adjacent diagnostic through a separate native path; not a general VAD accuracy result.",
    },
    {
        "id": "CI-5",
        "input": "Deterministic synthetic 160-sample analysis fixtures in merged task-local packages",
        "class": "historical_local_synthetic_fixture",
        "source_pin": "docs/task-evidence/webrtc-vad/README.md",
        "boundary": "Uncalibrated analytic/logistic surrogates, not real detector posteriors; no real speech, corpus or accuracy claim.",
    },
    {
        "id": "CI-6",
        "input": "WebRTC source, pyannote model card and candidate-register project claims",
        "class": "source_reported_only",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "No exact checkout, weights, matched cohort or numeric parity follows from a source or vendor claim.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "always-speech and always-nonspeech diagnostics", "role": "Required degenerate controls that expose metric behavior; not product candidates.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
    {"id": "CT-2", "name": "Silero-alone baseline", "role": "Most balanced measured held-out baseline; a comparison point, not ground truth.", "source_pin": "reports/vad-research/chaining-evaluation.md"},
    {"id": "CT-3", "name": "fixed RMS and adaptive RMS simple baselines", "role": "Registry-required classical energy controls for every comparison.", "source_pin": "reports/vad-research/chaining-evaluation.md"},
    {"id": "CT-4", "name": "unknown-region masking", "role": "Unannotated time is excluded, never scored as nonspeech or silence.", "source_pin": "research/plans/F02/vad_accuracy_contract.md"},
    {"id": "CT-5", "name": "50 ms boundary sensitivity collar", "role": "Separate boundary-delay sensitivity; never changes primary sample counts.", "source_pin": "reports/vad-research/chaining-evaluation.md"},
    {"id": "CT-6", "name": "preserved PCM identity", "role": "Advisory decisions never gate, mute or alter audio in the local fixtures.", "source_pin": "docs/task-evidence/speexdsp-vad/README.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "AMI Mix-Headset six-recording speech/non-speech reference",
        "class": "research_audio",
        "status": "CC BY 4.0 per the cited manifest; local only and not redistributed in this task",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
    },
    {
        "asset": "audEERING vadtoolkit 1.1.0 metadata, annotations and four public WAVs",
        "class": "research_audio",
        "status": "GPLv3/commercial package staged under prior authorization; publication terms not inferred",
        "source_pin": "reports/vad-research/20261028-synthesis-v7.md",
    },
    {
        "asset": "vad-chaining-fixture-v1 synthetic environment fixture",
        "class": "research_audio_derived",
        "status": "Generated noise-only negatives with reused positive spans; controlled probe only",
        "source_pin": "research/voice-enhancement-20261101/agent-vad-chain-followup/REPORT.md",
    },
    {
        "asset": "WebRTC VAD source lead (S01)",
        "class": "external_documentation",
        "status": "Direct documentation/source scope; no pinned runtime or binary in this task",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "pyannote segmentation model card (S02)",
        "class": "external_documentation",
        "status": "Direct documentation scope; no weights, token, runtime or exact revision",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "VAD dataset and source register (F02)",
        "class": "source_and_metadata_only",
        "status": "Lead register only; no source passes the current coverage, rights and suitability gates",
        "source_pin": "research/plans/F02/vad_sources.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Seven-candidate held-out AMI standalone comparison",
        "outcome_class": "historical_local_heldout_real_meeting",
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
            "web_rtc_fn_percent": 7.31,
            "web_rtc_fp_percent": 49.54,
            "web_rtc_cost_microseconds_per_frame": 6.38,
            "silero_fn_percent": 19.43,
            "silero_fp_percent": 8.20,
            "silero_cost_microseconds_per_frame": 68.35,
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
            "heldout_meetings": 3,
            "scored_frame_ms": 20,
        },
        "scope": "Three speaker-disjoint held-out AMI meetings projected onto 20 ms frames; desktop accelerated replay with unknown-region masking; not rerun by this survey and not a target-device or broad natural-call result.",
    },
    {
        "id": "HE-2",
        "label": "Frozen adaptive-energy-to-Silero and WebRTC-to-Silero policy replay",
        "outcome_class": "historical_local_heldout_real_meeting",
        "component_ids": [
            "adaptive-energy-to-silero-cascade",
            "webrtc-vad",
            "silero-vad-6-2-3-reference",
        ],
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "values": {
            "adaptive_chain_fn_percent": 19.83,
            "adaptive_chain_fp_percent": 7.92,
            "adaptive_chain_missed_speech_s": 613.3,
            "adaptive_chain_false_speech_s": 77.7,
            "adaptive_chain_compute_saved_percent": 16.37,
            "adaptive_chain_silero_call_rate_percent": 73.2,
            "webrtc_chain_fn_percent": 19.52,
            "webrtc_chain_fp_percent": 8.13,
            "webrtc_chain_compute_saved_percent": 7.57,
            "silero_fn_percent": 19.43,
            "silero_fp_percent": 8.20,
        },
        "scope": "Policy selected on AMI development and replayed on saved held-out decision timelines; not a live state-preservation, startup, latency or deadline test; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "audEERING positive-span-only diagnostic",
        "outcome_class": "historical_local_positive_span_only",
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
            "adaptive_rms_room_miss_percent": 16.9724,
            "earshot_bus_stop_miss_percent": 4.4739,
            "earshot_construction_miss_percent": 3.6120,
            "earshot_park_miss_percent": 2.8250,
            "earshot_room_miss_percent": 8.0992,
            "fast_vad_max_miss_percent": 0.0,
            "fixed_rms_room_miss_percent": 16.8733,
            "fixed_rms_park_miss_percent": 0.0124,
            "silero_bus_stop_miss_percent": 10.4176,
            "silero_construction_miss_percent": 2.4973,
            "silero_park_miss_percent": 3.6100,
            "silero_room_miss_percent": 4.2647,
            "speexdsp_max_miss_percent": 0.0,
            "web_rtc_bus_stop_miss_percent": 0.0332,
            "web_rtc_construction_miss_percent": 0.0004,
            "web_rtc_park_miss_percent": 0.2731,
            "web_rtc_room_miss_percent": 0.9662,
        },
        "scope": "Missed/annotated-positive sample ratios only; unannotated gaps are unknown, so false alarms, full accuracy, boundary scores, intervals and rankings are unavailable; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Frozen chain on synthetic cross-environment evaluation split",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": [
            "adaptive-energy-vad",
            "adaptive-energy-to-silero-cascade",
            "silero-vad-6-2-3-reference",
        ],
        "source_pin": "research/voice-enhancement-20261101/agent-vad-chain-followup/REPORT.md",
        "values": {
            "recordings": 6,
            "scored_seconds": 517.75,
            "speech_samples": 5763840,
            "nonspeech_samples": 2520160,
            "adaptive_energy_only_fn_percent": 93.86,
            "adaptive_energy_only_fp_percent": 0.0,
            "silero_only_fn_percent": 100.0,
            "chain_fn_percent": 100.0,
            "chain_fp_percent": 0.0,
            "chain_projected_compute_saved_percent": 53.1,
        },
        "scope": "Saved-decision replay of a policy frozen on AMI development, applied to generated noisy speech; project is strongly adverse and is not pooled with AMI; not a live paced test; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "fast-vad cross-environment diagnostic",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["fast-vad-0-2-1"],
        "source_pin": "research/voice-enhancement-20261101/agent-vad-expanded/REPORT.md",
        "values": {
            "pooled_fn_percent": 48.87,
            "pooled_fp_percent": 9.85,
            "per_recording_min_fn_percent": 1.00,
            "per_recording_max_fn_percent": 100.0,
            "median_inter_output_microseconds": 1.584,
            "startup_to_first_output_ms": 74.7,
            "recordings": 6,
        },
        "scope": "Same six synthetic recordings; condition-dependent misses from 1% to 100%; accelerated offline replay with reused speech excerpts, not speaker-independent or target-device evidence; not rerun by this survey.",
    },
    {
        "id": "HE-6",
        "label": "RNNoise speech-probability side diagnostic on AMI windows",
        "outcome_class": "historical_local_adjacent_speech_probability",
        "component_ids": ["rnnoise-speech-probability", "silero-vad-6-2-3-reference"],
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "values": {
            "rnnoise_side_vad_fn_percent": 25.64,
            "rnnoise_side_vad_fp_percent": 5.44,
            "silero_fn_percent": 22.91,
            "silero_fp_percent": 7.64,
            "windows": 3,
            "window_seconds": 60,
        },
        "scope": "Exploratory label-balanced AMI window diagnostic at one threshold through a separate native path; not a general accuracy result and not the CLN-01 denoising pilot; not rerun by this survey.",
    },
    {
        "id": "HE-7",
        "label": "Merged task-local synthetic analysis fixtures",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": [
            "webrtc-vad",
            "fixed-rms-vad",
            "adaptive-energy-vad",
            "adaptive-energy-to-silero-cascade",
            "fast-vad-0-2-1",
            "rnnoise-speech-probability",
        ],
        "source_pin": "docs/task-evidence/adaptive-energy-to-silero-cascade/README.md",
        "values": {
            "cascade_generated_frames": 330,
            "cascade_scored_frames": 300,
            "cascade_unknown_tail_frames": 30,
            "rnnoise_evidence_window_samples": 480,
            "v0_frame_samples": 160,
            "native_adapter_frame_samples": 320,
        },
        "scope": "Deterministic model-free/synthetic surrogates at the 160-sample v0 boundary; uncalibrated probabilities; no real speech, corpus, weights, runtime or accuracy measurement; not rerun by this survey.",
    },
    {
        "id": "HE-8",
        "label": "Historical mobile VAD-FastEnhancer-WPE paced desktop chain",
        "outcome_class": "historical_local_adjacent_pipeline_context",
        "component_ids": ["historical-mobile-vad-fastenhancer-wpe-chain", "silero-vad-6-2-3-reference"],
        "source_pin": "research/voice-enhancement-20261101/findings.md",
        "values": {
            "dns_pairs": 30,
            "median_compute_rtf": 0.149,
            "p95_compute_rtf": 0.212,
            "paced_frames": 30210,
            "frames_over_10_ms": 100,
            "max_frame_ms": 32.3,
            "vad_gate_si_sdr_delta_db": -0.51,
            "ami_clean_load_rtf": 0.1535,
            "ami_clean_load_misses": 80,
            "ami_clean_load_frames": 90913,
            "ami_clean_load_p95_ms": 3.42,
        },
        "scope": "Desktop macOS arm64 paced/offline chain context; several AMI timings were load-distorted and two retries did not complete; not phone, device, thermal or end-to-end latency evidence; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "WebRTC speech activity detector source and project claims",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct source/documentation scope; no exact checkout, binary, local parity or matched cohort is created here.",
    },
    {
        "id": "RO-2",
        "claim": "pyannote segmentation model-card capability claims",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct documentation scope; no weights, token, runtime, adapter or local execution is verified here.",
    },
    {
        "id": "RO-3",
        "claim": "audEERING vadtoolkit corpus size, annotation and environment metadata",
        "class": "source_reported_dataset_metadata",
        "source_pin": "reports/vad-research/20261028-synthesis-v7.md",
        "boundary": "Corpus metadata as cited; approximate duration and positive spans do not establish exhaustive coverage or known nonspeech.",
    },
    {
        "id": "RO-4",
        "claim": "Candidate shortlist and timing trade-offs from the pinned research register",
        "class": "source_reported_runtime_context",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Batch or accelerated desktop values on research hosts are not callback availability or target-device deadline evidence.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "timestamped_probabilities_and_events": "HE-1/HE-3/HE-7 transcribe timestamped decision and event evidence; no probability calibration is claimed",
        "quiet_and_active_speech": "CI-1..CI-3 include speech and idle regions; quiet-speech strata remain unavailable in the cited recordings",
        "known_positives_and_negatives": "CI-1/CI-2 have known speech and nonspeech; CI-3 keeps the complement unknown rather than negative",
        "onset_offset_delay": "HE-1/HE-2 transcribe median onset/offset delays; 50 ms collar sensitivity is a separate diagnostic",
        "stratified_fn_fp": "Only recording-level or environment-level strata exist; no within-recording quiet/overlap/noise strata",
        "validity_vs_nonspeech": "CT-4; unknown or invalid time is never relabelled nonspeech",
        "exact_source_intervals": "HE-7 and the local fixtures use exact half-open 160-sample source intervals",
        "independent_state": "Historical replays used fresh sessions; live pause/resume state preservation is untested",
        "availability_and_dropped_stale_events": "Synthetic fixtures expose availability clocks and drop audit; no device availability measurement",
        "cross_hop_behavior": "Native 16/20/32 ms cadences versus 160-sample v0 geometry are recorded as divergence; no parity claim",
    },
    "blocked": [
        "Rights-qualified continuous speech/nonspeech corpus with explicit scored and unknown regions",
        "Frozen speaker/session-disjoint development and held-out partitions",
        "Full miss, false-alarm, onset/offset and uncertainty evidence with matched controls",
        "Pinned real ML runtimes, weights and exact revisions for neural candidates",
        "Paced live state-preservation, startup, warm-up and target-device deadline evidence",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Exact external reference parity at a frozen revision and setting",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "heldout_real_meeting_historical_local": True,
    "paired_synthetic_historical_local": True,
    "positive_span_only_historical_local": True,
    "adjacent_speech_probability_historical_local": True,
    "source_reported_only": True,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "clean_reference_accuracy_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a rights-qualified continuous speech/nonspeech reference with explicit unknown regions",
        "evidence_gap": "AMI covers three held-out meetings in one corpus and one language; audEERING gaps are unknown; no source passes the current coverage, rights and suitability gates.",
        "follow_up_ids": [
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated dataset-owner task exists; the linked research-control rows own scoring tooling, manifests and evidence intake, not a new corpus.",
    },
    {
        "id": "G02",
        "actionable_gap": "Add quiet-speech, onset/offset and false-alarm strata with degenerate controls",
        "evidence_gap": "Current strata are recording-level or environment-level; quiet speech, overlap and noise are not separately labeled, and always-speech/always-nonspeech diagnostics are specified but not run on a validated cohort.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers within-recording strata; the linked research-control rows own the scorer controls and reference tooling.",
    },
    {
        "id": "G03",
        "actionable_gap": "Validate live pause/resume state, warm-up and scheduler gating with paced streaming",
        "evidence_gap": "The selected chain was replayed from saved decision timelines; pausing/resuming a live adapter and its transition delay are untested, and the periodic cross-check leaves a bounded blind interval.",
        "follow_up_ids": [
            "PRO-ADAPTIVE-ENERGY-SILERO-SCHEDULER-IMPLEMENTATION",
            "SDK-FND-TIMING",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No queued feasibility row owns live state preservation; the linked implementation and foundation rows own scheduler code and timing rules.",
    },
    {
        "id": "G04",
        "actionable_gap": "Pin and run the real Silero runtime instead of model-free surrogates",
        "evidence_gap": "Local Silero evidence is a logistic or analytic surrogate at the 160-sample boundary; the queued real reference and ONNX paths have no merged task-local accuracy evidence.",
        "follow_up_ids": [
            "SDK-SILERO-VAD-6-2-3-REFERENCE",
            "SDK-SILERO-VAD-V5-ONNX-REFERENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No feasibility row is needed because queued implementation tasks already own the real runtime; neither is enabled or qualified here.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate neural segmentation and large frame-classification families",
        "evidence_gap": "pyannote segmentation is blocked and Wav2Vec2/CNN-BiLSTM/CRNN have no selected checkpoint, adapter or local run; no capability is inferred from a model card.",
        "follow_up_ids": [
            "SDK-PYANNOTE-SEGMENTATION-VAD",
            "SDK-WAV2VEC2-XLS-R-TRANSFORMER-VAD",
            "SDK-CNN-BILSTM-VAD",
            "SDK-CRNN-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally evaluated segmentation model; linked rows are bounded feasibility leads, not enabled detectors or checkpoints.",
    },
    {
        "id": "G06",
        "actionable_gap": "Assess blocked small-model and commercial-gated VAD families",
        "evidence_gap": "TEN VAD, PulseVAD, FSMN, MarbleNet and FireRedVAD lack staged weights, exact source checkouts or adapters in the checked local stores.",
        "follow_up_ids": [
            "SDK-TEN-VAD",
            "SDK-PULSEVAD",
            "SDK-FSMN-VAD",
            "SDK-MARBLENET-VAD",
            "SDK-FIREREDVAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a runnable candidate in these families; linked rows are feasibility leads with unresolved weights and terms.",
    },
    {
        "id": "G07",
        "actionable_gap": "Bring the distinct Earshot cadence into a pinned local runtime comparison",
        "evidence_gap": "Earshot has held-out AMI and positive-span rows but no merged task-local package or exact runtime pin at the SDK boundary.",
        "follow_up_ids": ["SDK-EARSHOT-1-2-2"],
        "feasibility_task_exists": False,
        "owner_note": "No feasibility row is needed because the queued implementation row already owns the candidate; it is neither enabled nor qualified here.",
    },
    {
        "id": "G08",
        "actionable_gap": "Keep VAD separate from endpointing, turn completion and disfluency policy",
        "evidence_gap": "Pause-duration and turn-taking packages consume VAD output, but a speech-activity decision is not an endpoint or a semantic turn decision.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-02",
            "SDK-LIVEKIT-TURN-DETECTION",
            "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No single component owns both task definitions; linked taxonomy and feasibility rows keep endpointing and disfluency policy separate.",
    },
    {
        "id": "G09",
        "actionable_gap": "Prevent VAD from becoming muting, target-speaker selection or source separation",
        "evidence_gap": "Advisory decisions never gate audio in the local fixtures; no local screen establishes target-speaker selection, and personalized VAD is a distinct task.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-05",
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
            "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No VAD component owns speaker identity or playback gating; linked taxonomy and feasibility rows keep those capabilities distinct.",
    },
    {
        "id": "G10",
        "actionable_gap": "Collect target-device content/availability timing, memory and deadline evidence",
        "evidence_gap": "Only desktop, accelerated or batch values exist; no phone callback path, memory ceiling, energy or deadline-miss distribution is measured for a VAD.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row was found; foundation rows own the lifecycle, timing and evidence acceptance rules.",
    },
    {
        "id": "G11",
        "actionable_gap": "Gate chains on continuous cross-condition regression, not projected compute alone",
        "evidence_gap": "The frozen adaptive-energy-to-Silero chain saved projected compute but missed 100% of speech on the synthetic cross-environment split while staying near Silero on AMI.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "PRO-HISTORICAL-MOBILE-VAD-FASTENHANCER-WPE-CHAIN",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner owns a cross-condition regression gate; the linked foundation and implementation rows own evidence rules and the historical chain.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING", "title": "VADToolkit and AMI scoring tooling", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE", "title": "LibriSpeech and Common Voice evidence intake", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "PRO-ADAPTIVE-ENERGY-SILERO-SCHEDULER-IMPLEMENTATION", "title": "Adaptive-energy / Silero scheduler implementation", "mode": "implementation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-SILERO-VAD-6-2-3-REFERENCE", "title": "Silero VAD 6.2.3 reference", "mode": "implementation"},
    {"task_id": "SDK-SILERO-VAD-V5-ONNX-REFERENCE", "title": "Silero VAD v5 ONNX reference", "mode": "implementation"},
    {"task_id": "SDK-PYANNOTE-SEGMENTATION-VAD", "title": "pyannote segmentation / VAD", "mode": "feasibility"},
    {"task_id": "SDK-WAV2VEC2-XLS-R-TRANSFORMER-VAD", "title": "Wav2Vec2 XLS-R transformer VAD", "mode": "feasibility"},
    {"task_id": "SDK-CNN-BILSTM-VAD", "title": "CNN-BiLSTM VAD", "mode": "feasibility"},
    {"task_id": "SDK-CRNN-VAD", "title": "CRNN VAD", "mode": "feasibility"},
    {"task_id": "SDK-TEN-VAD", "title": "TEN VAD", "mode": "feasibility"},
    {"task_id": "SDK-PULSEVAD", "title": "PulseVAD", "mode": "feasibility"},
    {"task_id": "SDK-FSMN-VAD", "title": "FSMN VAD", "mode": "feasibility"},
    {"task_id": "SDK-MARBLENET-VAD", "title": "MarbleNet VAD", "mode": "feasibility"},
    {"task_id": "SDK-FIREREDVAD", "title": "FireRedVAD", "mode": "feasibility"},
    {"task_id": "SDK-EARSHOT-1-2-2", "title": "Earshot 1.2.2", "mode": "implementation"},
    {"task_id": "SDK-SURVEY-DET-02", "title": "Review coverage for Utterance endpointing and turn completion", "mode": "taxonomy"},
    {"task_id": "SDK-LIVEKIT-TURN-DETECTION", "title": "LiveKit turn detection", "mode": "feasibility"},
    {"task_id": "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR", "title": "SpeechBrain disfluency/pause predictor", "mode": "feasibility"},
    {"task_id": "SDK-SURVEY-DET-05", "title": "Review coverage for Target-speaker / personalized VAD", "mode": "taxonomy"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK", "title": "Source/VAD conditioning for playback", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "PRO-HISTORICAL-MOBILE-VAD-FASTENHANCER-WPE-CHAIN", "title": "Historical mobile VAD\u2013FastEnhancer\u2013WPE chain", "mode": "implementation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified continuous speech/nonspeech corpus with explicit scored and unknown regions"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen speaker/session-disjoint development and held-out partitions with independent label review"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched always-speech, always-nonspeech, RMS and Silero controls with full miss, false-alarm, onset/offset and uncertainty evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned real ML runtimes, weights and exact revisions for every claimed neural candidate"},
    {"id": "RG-05", "blocked": True, "requirement": "Paced live state-preservation and target-device availability, memory and deadline evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **DET-01 \u2014 Speech activity detection (VAD/SAD)** |",
        "Do not equate VAD with muting or with target-speaker selection. Measure onset/offset misses and quiet speech.",
    ],
    "research/category_survey/sources.md": [
        "| S01 | [WebRTC speech activity detector source](https://webrtc.googlesource.com/src/+/refs/heads/main/common_audio/vad/vad_core.c) | analysis | direct |",
        "| S02 | [pyannote segmentation model card](https://huggingface.co/pyannote/segmentation) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Analysis | Score timestamped probabilities, event boundaries and detections.",
    ],
    "reports/vad-research/chaining-evaluation.md": [
        "| WebRTC | 7.31% | 49.54% | 226.0s | 486.6s | 6.38\u00b5s | 20 / 70ms |",
        "| Silero | 19.43% | 8.20% | 601.0s | 80.5s | 68.35\u00b5s | 280 / -220ms |",
        "used **16.4% less measured compute** than Silero alone.",
        "| adaptive-energy \u2192 Silero, agreement_sleep (3 frames; 10 Silero-silence calls; 50-frame cross-check) | 19.83% / 7.92% | 613.3s / 77.7s | 108.4 | 57.17 / 9,326.82\u00b5s | 16.37% | 73.2% | 280 / -220ms |",
    ],
    "reports/vad-research/20261028-synthesis-v7.md": [
        "| Adaptive RMS | 0.0000% | 0.0000% | 0.0000% | 16.9724% | 20 ms |",
        "| Silero 6.2.3 ONNX streaming | 10.4176% | 2.4973% | 3.6100% | 4.2647% | 32 ms |",
        "**No best VAD is selected.**",
    ],
    "research/voice-enhancement-20261101/agent-vad-chain-followup/REPORT.md": [
        "| Adaptive-energy\u2192Silero, frozen AMI policy | 100.00% | 0.00% | 0 / 5,763,840 / 2,520,160 / 0 | 0.00201 | 53.1% lower |",
        "it cut projected Silero compute by 53.1% but missed all speech",
    ],
    "research/voice-enhancement-20261101/agent-vad-expanded/REPORT.md": [
        "Pooled sample-weighted false-negative rate was **48.87%**",
        "WebRTC's pooled FN/FP rates are 4.34% / 41.09%.",
    ],
    "research/plans/F02/vad_accuracy_contract.md": [
        "**Status: proposed contract, blocked on selection and verification of a suitable labeled dataset.**",
        "Unknown or unannotated time is never nonspeech.",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| WebRTC VAD | Frame-based speech detection | 6.38 \u00b5s per 20 ms frame; held-out AMI FN 7.31%, FP 49.54%. |",
        "A separate noisy synthetic fixture yielded 100% FN for the frozen policy",
    ],
    "research/voice-enhancement-20261101/findings.md": [
        "Standalone VAD now has held-out accuracy and desktop compute evidence, but no broad winner.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/webrtc-vad/README.md": [
        "This package is a deterministic, fully synthetic VAD *surrogate* at a",
    ],
    "docs/task-evidence/speexdsp-vad/README.md": [
        "This is **not** an accuracy measurement, model qualification, native runtime",
    ],
    "docs/task-evidence/fixed-rms-vad/README.md": [
        "**Status: proposal-only, model-free, synthetic; qualification `incomplete`.**",
    ],
    "docs/task-evidence/adaptive-energy-vad/README.md": [
        "**Status: proposal-only / synthetic; qualification `incomplete`.**",
    ],
    "docs/task-evidence/adaptive-energy-to-silero-cascade/README.md": [
        "Silero stage is a **MODEL-FREE STUB**: a smoothed analytic sigmoid on frame RMS.",
        "generates 330 deterministic frames (52,800 samples)",
        "- 330 frames / 52,800 samples; 300 known scored frames / 48,000 samples;",
    ],
    "docs/task-evidence/fast-vad-0-2-1/README.md": [
        "This is a deterministic, fully",
        "synthetic VAD *surrogate* at a task-local, protocol-v1-shaped analysis",
    ],
    "docs/task-evidence/rnnoise-speech-probability/README.md": [
        "The reference is **model-free**: a deterministic logistic transform of RMS over",
        "modeled evidence window is 480 samples",
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
}

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
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
        raise MapError("DET-01 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("DET-01 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F02 / DET-01 is not unique")
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
            raise MapError("legacy backlog mismatch: F02/DET-01/%s" % key)


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


def _check_evidence_classes() -> None:
    blob = " ".join(
        [row["class"] for row in COMPARISON_INPUTS]
        + [row["outcome_class"] for row in HISTORICAL_EXECUTIONS]
        + [row["class"] for row in REPORTED_OUTCOMES]
    )
    expected = {
        "heldout_real_meeting_historical_local": "heldout_real_meeting" in blob,
        "paired_synthetic_historical_local": "synthetic" in blob,
        "positive_span_only_historical_local": "positive_span" in blob,
        "adjacent_speech_probability_historical_local": "adjacent" in blob,
        "source_reported_only": "source_reported" in blob,
        "human_listening_result": "listening" in blob,
        "device_timing": "device_timing" in blob,
        "new_execution_in_this_survey": "new_execution" in blob,
        "parity_or_qualification_claim": "qualification" in blob or "parity" in blob,
        "clean_reference_accuracy_claim": "accuracy_claim" in blob,
    }
    if set(expected) != set(EVIDENCE_CLASSES):
        raise MapError("evidence-class keys do not match the checked set")
    for key, value in expected.items():
        if EVIDENCE_CLASSES[key] is not value:
            raise MapError("evidence class does not match mapped records: " + key)


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
