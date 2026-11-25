# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-02.

This module builds a bounded taxonomy/comparison evidence map for the
transient-interference and click-repair category (inventory category ``CLN-02``). It reads only
pinned, read-only documents from the enclosing ``audioml`` workspace and the
SDK worktree. It does not load audio, weights, runtimes, media or the network,
and it does not register, expose, enable or qualify any processor.

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
TASK = "SDK-SURVEY-CLN-02"
TITLE = "Review coverage for Transient interference and click repair"
CATEGORY_ID = "CLN-02"
LEGACY_FAMILY = "F08"
BRANCH = "swarm/SDK-SURVEY-CLN-02"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
PROFILE = "Enhancement"
COMPONENT = "transient-click-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media/weights that are not present in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "REALTIME_COMPONENT_CANDIDATES.md": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/findings.md": "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
    "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md": "ae4b0065eabbb62fe8880c7a04dee146415d463c5ae6676db6329147a901e1cc",
    "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md": "b8a42f9b0b782ad3aaa0be64da0d23b37c3c54b65a31caf252a4cd2ace88841e",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/median-residual-click-gate/README.md": "86561ef9f77bc62bcf0f1a090e33908c815d3f6bf09935a1798eb92e4123a389",
    "docs/task-evidence/quality-impairment-taxonomy/README.md": "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Transient interference and click repair",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Handle typing/impulsive acoustic noise or corrupted samples.",
    "method_families": {
        "classic": "Transient detection; interpolation; gating",
        "ml": "Transient-aware suppression or restoration",
    },
    "input_output": "Audio \u2192 suppressed event or repaired samples",
    "live_or_comparison_boundary": (
        "Acoustic keyboard noise and a corrupted digital sample are different "
        "subcases. Preserve speech consonants."
    ),
    "source_ids": ["S17", "S19"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S17",
        "title": "RNNoise implementation",
        "url": "https://github.com/xiph/rnnoise",
        "access_scope": "search excerpt; also inspected in prior brainstorm searches",
        "mapped_components": ["rnnoise-v0-2", "rnnoise-speech-probability"],
        "gap_ids": ["G06"],
        "finding": (
            "Registry access is a search excerpt, not a pinned checkout. Local "
            "RNNoise evidence is a 30-pair noise-suppression pilot (mean "
            "delta SI-SDR +3.14 dB, delta STOI +0.0215, process-frame RTF "
            "0.0662 at 48 kHz) and a separate activity-output diagnostic. "
            "No click-specific or frame-causal native execution was found."
        ),
    },
    {
        "source_id": "S19",
        "title": "FFmpeg audio filters",
        "url": "https://ffmpeg.org/ffmpeg-filters.html",
        "access_scope": "direct",
        "mapped_components": ["ffmpeg-afwtdn", "ffmpeg-afftdn"],
        "gap_ids": ["G07"],
        "finding": (
            "Registry access is direct documentation, with no pinned filter "
            "revision in the reviewed records. Historical afftdn/afwtdn runs "
            "were noise-suppression batch tests with negative quality in the "
            "tested configuration; no transient/click filter invocation or "
            "natural keyboard recording screen was found."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Transient detection and fixed-threshold gating",
        "components": ["median-residual-click-gate"],
        "gap_ids": ["G01", "G02"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Neighbor interpolation and sample-run repair",
        "components": ["linear-interpolation-plc", "linear-interpolation-declipping"],
        "gap_ids": ["G03"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Band-limited projection and sparse constrained restoration",
        "components": [
            "band-limited-pocs-declipping",
            "spade-and-social-sparsity-declipping",
            "c-omp-declipping",
            "matlab-ltfat-cvx-sparse-declipping-tools",
        ],
        "gap_ids": ["G04"],
        "status": "pocs_local_synthetic_only_sparse_tools_not_run",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Packet-loss concealment and damaged-input controls",
        "components": [
            "zero-fill-plc",
            "pitch-period-repeat-plc",
            "autoregressive-plc",
            "opus-1-4-standard-decoder-plc",
        ],
        "gap_ids": ["G03"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-C5",
        "branch": "classic",
        "family": "FFmpeg conventional denoising filters (named source lead S19)",
        "components": ["ffmpeg-afwtdn", "ffmpeg-afftdn"],
        "gap_ids": ["G07"],
        "status": "historical_noise_suppression_only_no_click_execution",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "RNNoise recurrent network and speech-probability gating (named source lead S17)",
        "components": ["rnnoise-v0-2", "rnnoise-speech-probability"],
        "gap_ids": ["G06"],
        "status": "historical_noise_suppression_only_no_click_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Transient-aware suppression or preservation for time-scale modification",
        "components": [
            "transient-aware-phase-vocoder",
            "phase-vocoder-with-neural-transient-preservation",
        ],
        "gap_ids": ["G07"],
        "status": "no_local_click_execution_in_reviewed_records",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Generative or codec-aware PLC and restoration networks",
        "components": [
            "complex-bin2bin-generative-plc",
            "opus-deep-plc",
            "lyra-ii-v2-codec-plc",
        ],
        "gap_ids": ["G05"],
        "status": "no_local_execution_in_reviewed_records",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "median-residual-click-gate", "evidence_status": "partial", "task": "SDK-MEDIAN-RESIDUAL-CLICK-GATE"},
    {"component_id": "linear-interpolation-plc", "evidence_status": "evaluated", "task": "SDK-LINEAR-INTERPOLATION-PLC"},
    {"component_id": "linear-interpolation-declipping", "evidence_status": "evaluated", "task": "SDK-LINEAR-INTERPOLATION-DECLIPPING"},
    {"component_id": "band-limited-pocs-declipping", "evidence_status": "evaluated", "task": "SDK-BAND-LIMITED-POCS-DECLIPPING"},
    {"component_id": "spade-and-social-sparsity-declipping", "evidence_status": "considered", "task": "SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING"},
    {"component_id": "c-omp-declipping", "evidence_status": "blocked", "task": "SDK-C-OMP-DECLIPPING"},
    {"component_id": "matlab-ltfat-cvx-sparse-declipping-tools", "evidence_status": "blocked", "task": "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS"},
    {"component_id": "zero-fill-plc", "evidence_status": "evaluated", "task": "SDK-ZERO-FILL-PLC"},
    {"component_id": "pitch-period-repeat-plc", "evidence_status": "evaluated", "task": "SDK-PITCH-PERIOD-REPEAT-PLC"},
    {"component_id": "autoregressive-plc", "evidence_status": "evaluated", "task": "SDK-AUTOREGRESSIVE-PLC"},
    {"component_id": "opus-1-4-standard-decoder-plc", "evidence_status": "evaluated", "task": "SDK-OPUS-1-4-STANDARD-DECODER-PLC"},
    {"component_id": "ffmpeg-afwtdn", "evidence_status": "evaluated", "task": "SDK-FFMPEG-AFWTDN"},
    {"component_id": "ffmpeg-afftdn", "evidence_status": "evaluated", "task": "SDK-FFMPEG-AFFTDN"},
    {"component_id": "rnnoise-v0-2", "evidence_status": "evaluated", "task": "SDK-RNNOISE-V0-2"},
    {"component_id": "rnnoise-speech-probability", "evidence_status": "partial", "task": "SDK-RNNOISE-SPEECH-PROBABILITY"},
    {"component_id": "transient-aware-phase-vocoder", "evidence_status": "considered", "task": "SDK-TRANSIENT-AWARE-PHASE-VOCODER"},
    {"component_id": "phase-vocoder-with-neural-transient-preservation", "evidence_status": "blocked", "task": "SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION"},
    {"component_id": "complex-bin2bin-generative-plc", "evidence_status": "blocked", "task": "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC"},
    {"component_id": "opus-deep-plc", "evidence_status": "considered", "task": "SDK-OPUS-DEEP-PLC"},
    {"component_id": "lyra-ii-v2-codec-plc", "evidence_status": "blocked", "task": "SDK-LYRA-II-V2-CODEC-PLC"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "12 EARS clips with 15 deterministic isolated one-sample impulses each",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md",
        "boundary": "Generated clicks only; no natural keyboard or consonant-overlap labels.",
    },
    {
        "id": "CI-2",
        "input": "Same 12 clips with square-pulse widths 1/2/3/5 and amplitudes 0.20/0.40/0.75",
        "class": "historical_local_paired_synthetic_stress",
        "source_pin": "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md",
        "boundary": "Fixed threshold, no retuning; STOI unavailable in that runtime.",
    },
    {
        "id": "CI-3",
        "input": "12-clip EARS hard-clipping and supplied-loss-mask screen",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Corruption masks are supplied to the algorithms; blind detection is not tested.",
    },
    {
        "id": "CI-4",
        "input": "12-clip stateful Opus 1.4 packet-erasure comparison",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/voice-enhancement-20261101/findings.md",
        "boundary": "Deterministic erasures; no captured network trace or phone result.",
    },
    {
        "id": "CI-5",
        "input": "30 paired DNS2020 noise-suppression clips used for RNNoise and FFmpeg filters",
        "class": "historical_local_adjacent_noise_suppression",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Adjacent task context only; not a click or corrupted-sample cohort.",
    },
    {
        "id": "CI-6",
        "input": "Vendor or source-reported transient/click removal claims",
        "class": "source_reported_only",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "No local runtime, exact revision, matched cohort or numeric parity follows from a claim.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "corrupted-input identity", "role": "Paired baseline for synthetic click, clipping and erasure inputs.", "source_pin": "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md"},
    {"id": "CT-2", "name": "known-mask oracle interpolation", "role": "Upper bound only; supplied click/loss masks are not blind detection.", "source_pin": "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md"},
    {"id": "CT-3", "name": "clipped / band-limited / decoded identities", "role": "Task-matched damaged-input baselines for restoration subcases.", "source_pin": "research/distortion_restoration_20261028.md"},
    {"id": "CT-4", "name": "zero-fill, linear, pitch-repeat and AR concealment", "role": "Conventional PLC controls with metric-dependent rankings.", "source_pin": "research/distortion_restoration_20261028.md"},
    {"id": "CT-5", "name": "clean speech and consonant-preservation control", "role": "Registry-required preservation boundary; no executed consonant-specific result is mapped here.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "EARS 12-clip synthetic click and restoration subsets",
        "class": "research_audio",
        "status": "CC BY-NC in cited reports; bytes not staged or verified in this task",
        "source_pin": "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md",
    },
    {
        "asset": "FFmpeg audio-filter documentation (direct source scope)",
        "class": "external_documentation",
        "status": "No pinned revision, binary, invocation or GPL rights transfer in this task",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "RNNoise source lead and noise-suppression pilot context",
        "class": "source_and_metadata_only",
        "status": "Search excerpt scope; no weights, runtime or exact checkout loaded here",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "VCTK v3 prepared listening items",
        "class": "research_audio",
        "status": "Prepared only; zero collected ratings and no playback clearance",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "One-sample synthetic click-gate screen",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md",
        "values": {
            "inserted_click_samples": 180,
            "true_positives_at_0_35": 180,
            "false_positives_at_0_35": 0,
            "identity_mean_si_sdr_db": 8.19,
            "repaired_mean_si_sdr_db": 51.52,
            "click_sample_rmse": 0.00650,
            "median_transform_rtf": 0.000290,
        },
        "scope": "12 peak-scaled EARS clips with injected one-sample impulses; STOI unavailable; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Fixed-threshold width and amplitude stress screen",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md",
        "values": {
            "recall_width1_amp0_20_percent": 0.0,
            "recall_width1_amp0_75_percent": 100.0,
            "recall_width5_amp0_75_percent": 0.0,
            "largest_mean_delta_si_sdr_db": 43.33,
            "false_positive_samples_all_conditions": 0,
            "median_transform_rtf": 0.000268,
        },
        "scope": "Square-pulse widths 1/2/3/5 at amplitudes 0.20/0.40/0.75; offline host timing, no natural clicks or consonants; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Declipping and supplied-mask restoration screen",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/distortion_restoration_20261028.md",
        "values": {
            "pocs_threshold0_35_mean_si_sdr_db": 15.05,
            "linear_interpolation_threshold0_35_mean_si_sdr_db": 10.99,
            "pocs_threshold0_55_mean_si_sdr_db": 23.32,
            "pocs_gain_over_clipped_input_threshold0_35_db": 0.25,
        },
        "scope": "12 clips per task; pilot effects with low clip occupancy, no human evaluation and no learned restorer; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Packet-loss concealment screen",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/distortion_restoration_20261028.md",
        "values": {
            "ar_isolated_mean_si_sdr_db": 10.35,
            "ar_burst_mean_si_sdr_db": 7.43,
            "pitch_repeat_isolated_stoi": 0.9207,
            "pitch_repeat_burst_stoi": 0.8690,
        },
        "scope": "Masks supplied to algorithms; metric-dependent ranking; not a network-trace or click event result; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "RNNoise and click-gate context values",
        "outcome_class": "historical_local_adjacent_noise_suppression",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "values": {
            "rnnoise_mean_delta_si_sdr_db": 3.14,
            "rnnoise_mean_delta_stoi": 0.0215,
            "rnnoise_process_frame_rtf": 0.0662,
            "click_gate_transform_rtf": 0.000290,
        },
        "scope": "Noise-suppression pilot and synthetic gate context; RTF excludes resampling/setup/I/O and is not device availability; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "RNNoise source-project quality and runtime claims",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt source scope; no exact checkout, local click run or matched cohort is created here.",
    },
    {
        "id": "RO-2",
        "claim": "FFmpeg audio-filter documentation for transient/denoising filters",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct documentation scope is recorded; no filter binary, pinned revision or invocation is verified here.",
    },
    {
        "id": "RO-3",
        "claim": "Historical CPU/wall/RTF values for click, PLC and denoiser adapters",
        "class": "source_reported_runtime_context",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Batch or transform timing on research hosts is not callback availability or target-device timing.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "identity_control": "CT-1; corrupted-input identity on synthetic cohorts only",
        "matched_baseline": "CT-3 / CT-4; damaged-input and conventional concealment controls",
        "modality_split": "CI-1..CI-4 are digital/impulse proxies; acoustic keyboard noise remains unmapped",
        "paired_objective_scores": "HE-1..HE-4; transcribed values, not rerun here",
        "clean_preservation": "CT-5; required by the registry, no executed consonant-specific result mapped",
        "peaks_and_invalid_outputs": "No new invalid-output or full-scale run; existing scorer rules are context only",
        "unpaired_predictive_screen": "No CLN-02-specific predictive score in reviewed records",
        "listening": "CI-6 and ASSETS VCTK items are prepared or source-reported only; no ratings",
        "alignment_state_memory_timing": "HE-5 transform/batch RTF transcribed as context, not measured here",
    },
    "blocked": [
        "Annotated natural keyboard/impulsive event cohort with clean reference",
        "Separate acoustic-event and corrupted-sample protocols with frozen masks",
        "Consonant-preservation control with declared analysis and independent listening",
        "Target-device content/availability timing, memory and deadline evidence",
        "Task-matched external baseline under a locked runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Exact approved reference parity at frozen revision and settings",
    ],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Detect and gate natural impulsive/keyboard clicks with labeled events",
        "evidence_gap": "The mapped click gate was screened only on generated one-sample and square-pulse EARS fixtures; no natural-click labels or acoustic keyboard recordings were found.",
        "follow_up_ids": ["SDK-TRANSIENT-AWARE-PHASE-VOCODER", "SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION"],
        "feasibility_task_exists": True,
        "owner_note": "The median-residual click component is partial for synthetic pulses only; no component owner exists for natural keyboard clicks. Linked rows are bounded transient-handling feasibility leads, not a click-suppression capability.",
    },
    {
        "id": "G02",
        "actionable_gap": "Characterize the fixed gate's width/amplitude failure envelope with frozen controls",
        "evidence_gap": "No recall at amplitude 0.20 or width 5, while louder 1-3 sample events were detected with zero observed false positives; no natural operating point was established.",
        "follow_up_ids": ["SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row owns this screen; the existing component and research-control rows own gate and cohort controls.",
    },
    {
        "id": "G03",
        "actionable_gap": "Separate blind event localization from repair with supplied masks",
        "evidence_gap": "Restoration and PLC screens supplied known click, clipping or erasure masks to the algorithms; blind detection and false-positive cost were not measured.",
        "follow_up_ids": ["SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row was found; research-control and foundation rows own the frozen-mask and evidence boundaries.",
    },
    {
        "id": "G04",
        "actionable_gap": "Assess sparse constrained declipping and codec-aware restoration families",
        "evidence_gap": "Band-limited POCS has a local 12-clip screen; SPADE/social sparsity is considered, C-OMP is blocked and MATLAB/LTFAT/CVX is an unrun external adapter.",
        "follow_up_ids": ["SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING", "SDK-C-OMP-DECLIPPING", "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally executed sparse-constrained declipper; links are scoping rows, not implemented capabilities.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate transient-aware or generative restoration networks with pinned assets",
        "evidence_gap": "No local execution or rights-cleared asset was found for neural transient preservation, complex-bin2bin PLC, Opus deep PLC or Lyra II/V2.",
        "follow_up_ids": ["SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION", "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC", "SDK-OPUS-DEEP-PLC", "SDK-LYRA-II-V2-CODEC-PLC"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally evaluated model in these ML families; linked rows are bounded feasibility leads, not enabled processors or checkpoints.",
    },
    {
        "id": "G06",
        "actionable_gap": "Establish frame-causal RNNoise gating and speech-probability evidence for this category",
        "evidence_gap": "Only noise-suppression pilot and activity-output diagnostics were found; the local adapter is offline at 48 kHz and RTF excludes setup, resampling and I/O.",
        "follow_up_ids": ["SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": True,
        "owner_note": "RNNoise implementation rows exist for noise suppression; no CLN-02 component owner or native click-path execution was found.",
    },
    {
        "id": "G07",
        "actionable_gap": "Find a pinned FFmpeg filter revision and transient-specific comparison",
        "evidence_gap": "The S19 lead is direct documentation only; afftdn/afwtdn runs were noise-suppression tests with negative quality in the tested configuration and no click-specific invocation.",
        "follow_up_ids": ["SDK-FND-EVIDENCE", "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row for transient FFmpeg filters was found; the mapped components own denoising, not click repair.",
    },
    {
        "id": "G08",
        "actionable_gap": "Keep acoustic keyboard noise and corrupted digital samples as separate subcases with consonant preservation",
        "evidence_gap": "The registry requires the split; generated impulses, clipping thresholds and supplied erasure masks do not model acoustic keyboard events or consonant overlap.",
        "follow_up_ids": ["SDK-FND-EVIDENCE", "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS"],
        "feasibility_task_exists": False,
        "owner_note": "No single component owns both subcases; research-control and foundation rows own separate cohorts and preservation rules.",
    },
    {
        "id": "G09",
        "actionable_gap": "Acquire rights-qualified annotated transient cohorts and listening results",
        "evidence_gap": "EARS click screens are CC BY-NC synthetic fixtures; VCTK listening items were prepared with zero collected ratings; no natural-click playback clearance exists.",
        "follow_up_ids": ["SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row was found; cohort, rights and listening-control rows own this gate.",
    },
    {
        "id": "G10",
        "actionable_gap": "Collect target-device content/availability timing, memory and deadline evidence",
        "evidence_gap": "Only offline transform/batch RTF and RSS values are documented; no callback-path or device measurement exists for click repair.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row was found; foundation rows own acceptance rules.",
    },
    {
        "id": "G11",
        "actionable_gap": "Define breath, filler and stutter policy separately from disposable clicks",
        "evidence_gap": "Reviewed records explicitly treat breaths and disfluencies as non-disposable events; no local removal execution or label set was mapped.",
        "follow_up_ids": ["SDK-BREATH-DETECTOR-REMOVAL", "SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION"],
        "feasibility_task_exists": True,
        "owner_note": "No CLN-02 component owner covers breath/filler removal; these feasibility rows are separate target definitions, not implemented click repair.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-TRANSIENT-AWARE-PHASE-VOCODER", "title": "Transient-aware phase vocoder", "mode": "feasibility"},
    {"task_id": "SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION", "title": "Phase vocoder with neural transient preservation", "mode": "feasibility"},
    {"task_id": "SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING", "title": "SPADE and social-sparsity declipping", "mode": "feasibility"},
    {"task_id": "SDK-C-OMP-DECLIPPING", "title": "C-OMP declipping", "mode": "research-control"},
    {"task_id": "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS", "title": "MATLAB/LTFAT/CVX sparse declipping tools", "mode": "external-adapter"},
    {"task_id": "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC", "title": "Complex-Bin2bin generative PLC", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-DEEP-PLC", "title": "Opus deep PLC", "mode": "feasibility"},
    {"task_id": "SDK-LYRA-II-V2-CODEC-PLC", "title": "Lyra II / V2 codec PLC", "mode": "feasibility"},
    {"task_id": "SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO", "title": "RNNoise INT8 (Arm ML Model Zoo)", "mode": "feasibility"},
    {"task_id": "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS", "title": "CCF AATC unified restoration controls", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-BREATH-DETECTOR-REMOVAL", "title": "Breath detector / removal", "mode": "feasibility"},
    {"task_id": "SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION", "title": "Text-aware filler and stutter annotation", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified natural transient/click cohort with annotated events and clean reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent authorized listening with declared consonant-preservation analysis"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched external baseline with acoustic and digital subcases separated under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-07", "blocked": True, "requirement": "Exact approved reference parity at frozen revision and settings"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-02 — Transient interference and click repair** |",
        "Acoustic keyboard noise and a corrupted digital sample are different subcases. Preserve speech consonants.",
    ],
    "research/category_survey/sources.md": [
        "| S17 | [RNNoise implementation](https://github.com/xiph/rnnoise) | acoustics | search excerpt; also inspected in prior brainstorm searches |",
        "| S19 | [FFmpeg audio filters](https://ffmpeg.org/ffmpeg-filters.html) | acoustics | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Enhancement | Run identity/noisy control and an established task-matched baseline.",
    ],
    "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md": [
        "At threshold 0.35, the detector found all 180 inserted samples with zero false-positive samples on these 12 clips.",
        "threshold 0.35 repair scored 51.52 dB / 51.52 dB",
        "Mean click-sample RMSE after repair was 0.00650",
        "median transform-only CPU RTF was 0.000290",
        "STOI could not be measured because `pystoi` was absent",
    ],
    "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md": [
        "| 1 | 0.20 | 0.0% | — | 0 / 0 / 180 | 0.00 dB [0.00, 0.00] |",
        "| 1 | 0.75 | 100% | 100% | 180 / 0 / 0 | +43.33 dB [39.86, 46.89] |",
        "| 5 | 0.75 | 0.0% | — | 0 / 0 / 900 | 0.00 dB [0.00, 0.00] |",
        "There were **zero false-positive samples** across all conditions",
        "was **0.000268** (p95 0.000325, maximum 0.000729)",
    ],
    "research/distortion_restoration_20261028.md": [
        "| Declipping, threshold 0.35 (2.74% of samples clipped) | Band-limited POCS | 15.05 dB SI-SDR | +0.25 dB vs clipped input; linear interpolation drops to 10.99 dB |",
        "| 10% isolated packet loss | AR prediction by SI-SDR/RMSE; pitch repeat by STOI | AR: 10.35 dB SI-SDR, 0.1136 damaged-region RMSE; pitch repeat: 0.9207 STOI | Different metrics favor different concealment behavior |",
        "PLC masks are provided to the algorithms, so this screen does not test loss detection.",
        "No neural restoration checkpoint was evaluated in the screen.",
    ],
    "research/voice-enhancement-20261101/findings.md": [
        "missed every ±0.20 event and all five-sample pulses",
        "A 12-clip packet-erasure comparison now measures bundled libopus 1.4 standard decoder PLC against same-codec waveform controls",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "DNS pilot mean ΔSI-SDR +3.14 dB, ΔSTOI +0.0215, RTF 0.0662 for `rnnoise_process_frame` only (excludes resampling/setup/I/O).",
        "| Fixed median-residual click gate | Short impulse suppression | Synthetic click screen; transform RTF 0.000290. Missed some click widths/amplitudes; natural clicks and breaths untested. |",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/median-residual-click-gate/README.md": [
        "**Status: synthetic, deterministic, opt-in, developer-only; not qualified.**",
    ],
    "docs/task-evidence/quality-impairment-taxonomy/README.md": [
        "Fixed threshold 0.35 detected many loud 1–3-sample events but missed all ±0.20 events and all five-sample events; no natural-click validation.",
        "zero collected ratings",
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
        raise MapError("CLN-02 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-02 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F08 / CLN-02 is not unique")
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
            raise MapError("legacy backlog mismatch: F08/CLN-02/%s" % key)


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
        "qualification_status": QUALIFICATION_STATUS,
        "readiness": READINESS,
        "decision": DECISION,
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
        "evidence_classes": {
            "paired_synthetic_historical_local": True,
            "unpaired_predictive_historical_local": True,
            "clean_preservation_diagnostic_historical_local": True,
            "prepared_listening_without_ratings": True,
            "human_listening_result": False,
            "vendor_or_source_reported": True,
            "new_execution_in_this_survey": False,
            "parity_or_qualification_claim": False,
        },
        "acceptance_profile": dict(ACCEPTANCE_PROFILE),
        "gaps": [dict(gap) for gap in GAPS],
        "board_links": links,
        "board_link_projection_sha256": board_digest,
        "mutable_provenance": {
            "gate": False,
            "path": BOARD_PATH,
            "sha256_at_read": sha256_file(ws / BOARD_PATH),
            "note": "Board status is mutable; only id/title/mode of linked rows are gated by board_link_projection_sha256.",
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
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for key, value in report["boundary"].items() if key != "release_approval"):
        raise MapError("boundary is not closed")
    if report["boundary"]["release_approval"] is not False:
        raise MapError("release approval is not false")
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
