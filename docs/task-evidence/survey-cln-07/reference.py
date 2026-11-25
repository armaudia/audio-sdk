# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-07.

This module builds a bounded taxonomy/comparison evidence map for the
beamforming and spatial-filtering category (inventory category ``CLN-07``). It
reads only pinned, read-only documents from the enclosing ``audioml`` workspace
and the SDK worktree. It does not load audio, weights, runtimes, media or the
network, and it does not register, expose, enable or qualify any processor.

All curated records below are documentation mappings, not new measurements.
The only historical executions cited are adjacent two-channel dereverberation
runs; they are array-fixture controls, **not** beamforming results, and they are
never pooled into a CLN-07 outcome.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-CLN-07"
TITLE = "Review coverage for Beamforming and spatial filtering"
CATEGORY_ID = "CLN-07"
LEGACY_FAMILY = "F07"
BRANCH = "swarm/SDK-SURVEY-CLN-07"
BASE_COMMIT = "afe0d324ab5534cc45297f4c7361c87c0cc1f005"
PROFILE = "Spatial"
COMPONENT = "beamforming-spatial-filtering-evidence-map"
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
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/noise_suppression_candidate_census.md": "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/pilot_source_research.md": "c9db16172ffaa1bcf8b5cc334d9401173528c31d1ec966176d6e99a0bbe52fe5",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md": "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary and adjacent-evidence pins. They are
# read only to prove that no public surface was touched and to ground curated
# adjacent values; no header, report or component is copied, edited or
# generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/offline-multichannel-wpe/README.md": "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/offline-multichannel-wpe/report.json": "4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba",
    "docs/task-evidence/online-multichannel-wpe/README.md": "3615f6fc66d3c8d15a4cd77ccdc1f8a2e5f9c6cd9a1a20b9263814bfb2c34013",
    "docs/task-evidence/online-multichannel-wpe/report.json": "df76b6e78ab86bc21609d3a93d53bc175b9281962396cc3bf1acf8ea2d994e6f",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Beamforming and spatial filtering",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Combine microphones to emphasize wanted directions or sources.",
    "method_families": {
        "classic": "Delay-and-sum; MVDR/MPDR",
        "ml": "Learned masks/spatial statistics feeding beamformers; neural spatial filters",
    },
    "input_output": "Synchronized array channels + spatial assumptions \u2192 waveform",
    "live_or_comparison_boundary": (
        "Extra microphones and oracle masks create different comparison groups; "
        "geometry and channel mismatch matter."
    ),
    "source_ids": ["S24", "S25"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "spatial_beamforming_only": True,
    "not_localization_category": "CLN-08",
    "not_dereverberation_category": "CLN-04",
    "not_source_separation_category": "SPK-01",
    "not_target_speaker_extraction_category": "SPK-02",
    "not_aec_category": "CLN-05",
    "extra_microphones_and_oracle_masks_are_separate_comparison_groups": True,
    "note": (
        "Localization metadata, dereverberation, blind source separation, "
        "target-speaker extraction and echo cancellation are separate "
        "catalogued categories. They are named only to prevent scope inflation; "
        "their results are not pooled into a CLN-07 beamforming claim."
    ),
}

SPATIAL_BOUNDARY: Dict[str, Any] = {
    "synchronized_array_channels_required": True,
    "array_geometry_and_channel_calibration_in_contract": True,
    "steering_or_reference_direction_declared": True,
    "oracle_and_estimated_mask_groups_are_separate": True,
    "localization_metadata_is_not_a_beamformed_waveform": True,
    "adjacent_multichannel_dereverberation_is_not_beamforming": True,
    "real_array_corpus_staged": False,
    "pinned_beamformer_source_or_runtime_staged": False,
    "neural_spatial_weights_staged": False,
    "array_timing_or_geometry_measured": False,
    "human_listening_result": False,
}

# Adjacent component boundary. These runs are cited only to ground the array
# fixture, channel-influence and clean-preservation controls. WPE is
# dereverberation (CLN-04); it is not a beamformer and is never pooled here.
ADJACENT_BOUNDARY: Dict[str, Any] = {
    "category_id": "CLN-04",
    "components": ["offline-multichannel-wpe", "online-multichannel-wpe"],
    "role": (
        "Two-channel synthetic dereverberation executions used only as an "
        "array-fixture, channel-influence and clean-preservation control."
    ),
    "pooled_with_cln_07": False,
    "results_promoted": False,
}

QUALIFICATION: Dict[str, Any] = {
    "status": QUALIFICATION_STATUS,
    "decision": DECISION,
    "readiness": READINESS,
    "proposal_only": True,
    "survey_status": "incomplete",
    "qualifies": False,
    "processor_exposure": False,
    "missing_result_promoted": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S24",
        "title": "Pyroomacoustics beamforming implementation",
        "url": "https://github.com/LCAV/pyroomacoustics/blob/master/pyroomacoustics/beamforming.py",
        "access_scope": "search excerpt",
        "mapped_components": [
            "delay-and-sum-beamformer",
            "mvdr-beamforming",
            "pyroomacoustics-candidate-tools",
            "source-localization-direction-of-arrival",
        ],
        "gap_ids": ["G01", "G02", "G03"],
        "finding": (
            "The catalogued source is an inspected search excerpt of a "
            "beamforming module, not a pinned package, executable, licence "
            "grant or array recording. No source tree, installed package or "
            "synchronized array fixture is staged in this task; the classic "
            "delay-and-sum and MVDR/MPDR candidates remain considered only."
        ),
    },
    {
        "source_id": "S25",
        "title": "TorchAudio mask-based MVDR example",
        "url": "https://docs.pytorch.org/audio/main/tutorials/mvdr_tutorial.html",
        "access_scope": "search excerpt",
        "mapped_components": [
            "mvdr-beamforming",
            "neural-beamforming",
        ],
        "gap_ids": ["G03", "G06"],
        "finding": (
            "The catalogued source is tutorial documentation for mask-based "
            "MVDR with covariance estimated from time-frequency masks. It does "
            "not supply a staged tutorial model, mask estimator, array audio or "
            "licence grant, and it does not establish a local mask-quality, "
            "target-preservation or geometry result."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Delay-and-sum with explicit steering delays and equal channel weighting",
        "components": [
            "delay-and-sum-beamformer",
            "pyroomacoustics-candidate-tools",
        ],
        "gap_ids": ["G01", "G02"],
        "status": "catalogued_only_no_local_beamformer_execution",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "MVDR/MPDR with covariance estimation from noise-only or mask statistics",
        "components": [
            "mvdr-beamforming",
            "3d-microphone-spatial-time-alignment",
            "pyroomacoustics-candidate-tools",
        ],
        "gap_ids": ["G02", "G03", "G07"],
        "status": "catalogued_only_no_local_beamformer_execution",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Learned masks or spatial statistics feeding an MVDR-style beamformer",
        "components": [
            "mvdr-beamforming",
            "neural-beamforming",
            "h-gtcrn",
        ],
        "gap_ids": ["G03", "G06"],
        "status": "mask_based_family_catalogued_h_gtcrn_conditional_no_local_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Neural spatial filters and end-to-end multichannel separation-plus-beamforming",
        "components": [
            "spatialnet",
            "beam-tasnet-beam-guided-tasnet",
            "neural-beamforming",
            "auxiva",
        ],
        "gap_ids": ["G04", "G05", "G06"],
        "status": "blocked_no_exact_checkpoint_adapter_or_synchronized_array_corpus",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "delay-and-sum-beamformer", "evidence_status": "considered", "task": "SDK-DELAY-AND-SUM-BEAMFORMER"},
    {"component_id": "mvdr-beamforming", "evidence_status": "considered", "task": "SDK-MVDR-BEAMFORMING"},
    {"component_id": "neural-beamforming", "evidence_status": "blocked", "task": "SDK-NEURAL-BEAMFORMING"},
    {"component_id": "spatialnet", "evidence_status": "blocked", "task": "SDK-SPATIALNET"},
    {"component_id": "beam-tasnet-beam-guided-tasnet", "evidence_status": "blocked", "task": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET"},
    {"component_id": "source-localization-direction-of-arrival", "evidence_status": "considered", "task": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"},
    {"component_id": "3d-microphone-spatial-time-alignment", "evidence_status": "considered", "task": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT"},
    {"component_id": "pyroomacoustics-candidate-tools", "evidence_status": "considered", "task": "SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS"},
    {"component_id": "auxiva", "evidence_status": "considered", "task": "SDK-AUXIVA"},
    {"component_id": "h-gtcrn", "evidence_status": "considered", "task": "SDK-H-GTCRN"},
    {"component_id": "offline-multichannel-wpe", "evidence_status": "evaluated", "task": "SDK-OFFLINE-MULTICHANNEL-WPE"},
    {"component_id": "online-multichannel-wpe", "evidence_status": "evaluated", "task": "SDK-ONLINE-MULTICHANNEL-WPE"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Inspected search excerpt of the Pyroomacoustics beamforming module covering delay-and-sum, MVDR, MPDR and SRP-PHAT classes",
        "class": "source_only_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation only; no package, source tree, array audio, geometry metadata or execution is staged in this task.",
    },
    {
        "id": "CI-2",
        "input": "Inspected TorchAudio tutorial excerpt for mask-based MVDR covariance estimation and beamforming",
        "class": "source_only_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Tutorial description only; no tutorial mask model, audio, checkpoint or local mask-quality result is available.",
    },
    {
        "id": "CI-3",
        "input": "Adjacent frozen two-channel synthetic dereverberation fixture with declared 0.04 m spacing, 30-degree source azimuth, 0/5-sample mic delays and synthetic RIRs",
        "class": "historical_local_adjacent_multichannel",
        "source_pin": "docs/task-evidence/online-multichannel-wpe/README.md",
        "boundary": "WPE is dereverberation, not beamforming; the geometry is a synthetic fixture parameter, not a measured array calibration or a CLN-07 result.",
    },
    {
        "id": "CI-4",
        "input": "Rights-cleared synchronized microphone-array corpus with geometry, channel calibration, timestamp alignment, target/reference directions and movement",
        "class": "missing_no_local_array_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Explicitly missing; the catalogued boundary requires synchronized array channels plus declared spatial assumptions.",
    },
    {
        "id": "CI-5",
        "input": "Oracle-mask and oracle-steering comparison group separated from estimated-mask and estimated-direction groups",
        "class": "missing_no_local_array_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Explicitly missing; no mask estimator, steering oracle or matched array split is staged, so oracle and estimated groups cannot be separated locally.",
    },
    {
        "id": "CI-6",
        "input": "Source-reported SpatialNet, Beam-TasNet/Beam-Guided TasNet and neural-beamforming candidate descriptions",
        "class": "source_only_blocked_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Candidate census only; exact architectures, checkpoints, licences, array adapters and multichannel target data are unresolved and unrun.",
    },
    {
        "id": "CI-7",
        "input": "CHiME-6 multi-array WPE/guided-separation/beamforming documentation and L3DAS23 ambisonic beamforming U-Net description",
        "class": "source_only_frozen_protocol",
        "source_pin": "research/pilot_source_research.md",
        "boundary": "Separate competition scenario group with multi-array or ambisonic inputs; no data, baseline or configuration is interchangeable with a CLN-07 claim.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "reference-channel passthrough", "role": "Single-channel identity baseline so array gain and target damage are visible rather than attributed to the beamformer.", "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"},
    {"id": "CT-2", "name": "delay-and-sum baseline", "role": "Classic baseline that must precede MVDR; MVDR mask quality and distortion are compared against it.", "source_pin": "audio_categories.md"},
    {"id": "CT-3", "name": "oracle-mask and oracle-steering upper bound", "role": "Oracle groups are recorded separately; an oracle-assisted score cannot be pooled with an estimated-mask or estimated-direction score.", "source_pin": "audio_categories.md"},
    {"id": "CT-4", "name": "geometry and calibration mismatch", "role": "Wrong spacing, swapped channels or biased steering are adverse controls for declared geometry and channel calibration.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-5", "name": "channel dropout and missing channel", "role": "Channel loss must be reported as an invalid or degraded condition, not silently replaced by a mono result.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-6", "name": "target and clean near-end preservation", "role": "Beamforming gain cannot pass a claim while target speech is damaged; target leakage and target damage are separate metrics.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-7", "name": "adjacent multichannel WPE control", "role": "WPE runs are an adjacent dereverberation control with a generated early-reflection target; they are not a beamformer comparison.", "source_pin": "docs/task-evidence/offline-multichannel-wpe/README.md"},
    {"id": "CT-8", "name": "nonfinite and invalid-output rejection", "role": "NaN, infinity, channel-count and shape violations fail closed; no invalid output may be scored as a result.", "source_pin": "docs/task-evidence/online-multichannel-wpe/README.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Pyroomacoustics beamforming documentation and repository lead",
        "class": "external_documentation",
        "status": "Pinned search excerpt only; no package, beamformer source, array fixture or licence grant is staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "TorchAudio mask-based MVDR tutorial",
        "class": "external_documentation",
        "status": "Tutorial documentation only; no mask model, audio, checkpoint or runtime is staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "SpatialNet official description and repository lead",
        "class": "missing_model_assets",
        "status": "No weights, adapter, exact checkpoint or synchronized multichannel target corpus is staged",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
    },
    {
        "asset": "Beam-TasNet / Beam-Guided TasNet paper and repository leads",
        "class": "missing_model_assets",
        "status": "Architecture identity is unresolved between related families; no exact implementation or checkpoint is staged",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
    },
    {
        "asset": "H-GTCRN two-microphone checkpoint variants",
        "class": "missing_model_assets",
        "status": "Conditional multichannel candidate; checkpoint hashes, terms and compatible array data are unverified",
        "source_pin": "research/noise_suppression_candidate_census.md",
    },
    {
        "asset": "Adjacent two-channel synthetic WPE fixtures and reports",
        "class": "sdk_adjacent_evidence",
        "status": "Merged synthetic dereverberation evidence only; not a beamformer, not array calibration and not pooled with CLN-07",
        "source_pin": "docs/task-evidence/offline-multichannel-wpe/report.json",
    },
    {
        "asset": "Synchronized rights-cleared microphone-array corpus with geometry and clean target reference",
        "class": "missing_corpus",
        "status": "Not staged; no participant consent, geometry metadata, calibration or array recording exists in this task",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Adjacent offline two-channel multichannel WPE synthetic regression screen (not a beamformer)",
        "outcome_class": "historical_local_adjacent_multichannel_dereverberation",
        "component_ids": ["offline-multichannel-wpe"],
        "source_pin": "docs/task-evidence/offline-multichannel-wpe/report.json",
        "values": {
            "fixture_channels": 2,
            "fixture_samples": 16960,
            "short_rt60_delta_si_sdr_db": -1.863045,
            "medium_rt60_delta_si_sdr_db": -0.570465,
            "long_rt60_delta_si_sdr_db": -0.639980,
            "clean_near_end_si_sdr_db": 21.707406,
            "clean_near_end_stoi": 0.998243,
            "nonfinite_count": 0,
        },
        "scope": "Adjacent CLN-04 whole-clip noncausal two-channel WPE on synthetic RIRs; this is not a beamforming result, not array calibration, not a real room or listening result, and not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Adjacent causal two-channel multichannel WPE synthetic regression screen (not a beamformer)",
        "outcome_class": "historical_local_adjacent_multichannel_dereverberation",
        "component_ids": ["online-multichannel-wpe"],
        "source_pin": "docs/task-evidence/online-multichannel-wpe/report.json",
        "values": {
            "fixture_channels": 2,
            "fixture_samples": 25600,
            "short_rt60_delta_si_sdr_db": -7.257785,
            "medium_rt60_delta_si_sdr_db": -2.480089,
            "long_rt60_delta_si_sdr_db": -1.136101,
            "clean_near_end_si_sdr_db": 11.561154,
            "clean_near_end_stoi": 0.982843,
            "content_delay_samples": 480,
            "nonfinite_count": 0,
        },
        "scope": "Adjacent CLN-04 frame-causal two-channel WPE on synthetic RIR pairs; this is not a beamforming result, not a measured array timing or geometry result, and not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "S24 documents delay-and-sum, MVDR, MPDR and SRP-PHAT beamformer classes in an inspected search excerpt",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation excerpt only; no package, source tree, array data or execution is staged or verified.",
    },
    {
        "id": "RO-2",
        "claim": "S25 demonstrates mask-based MVDR with spatial covariance estimated from time-frequency masks",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Tutorial-level description; no local mask estimator, array audio or quality result is reproduced.",
    },
    {
        "id": "RO-3",
        "claim": "SpatialNet is reported as a multichannel joint separation, denoising and dereverberation system requiring synchronized arrays and geometry",
        "class": "source_reported",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Upstream/project description only; weights, exact checkpoint terms and a compatible array corpus are not staged.",
    },
    {
        "id": "RO-4",
        "claim": "Beam-TasNet combines multichannel Conv-TasNet separation with MVDR, while Beam-Guided TasNet is a distinct iterative framework",
        "class": "source_reported",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Paper/repository-level claim; the catalogue label can denote either architecture and neither is locally resolved or run.",
    },
    {
        "id": "RO-5",
        "claim": "Neural beamforming is not one concrete model and has no local array definition or multichannel target benchmark",
        "class": "source_reported",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Candidate-census finding only; no candidate-specific weight, adapter or score exists.",
    },
    {
        "id": "RO-6",
        "claim": "H-GTCRN combines GTCRN, FD-WPE, AuxIVA and spatial features for two-microphone low-SNR enhancement",
        "class": "source_reported",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Census description only; checkpoint terms/hashes and compatible stereo data remain unverified and no local run exists.",
    },
    {
        "id": "RO-7",
        "claim": "CHiME-6 documents WPE, guided source separation and beamforming for multi-array inputs, and L3DAS23 uses an ambisonic beamforming U-Net",
        "class": "source_reported",
        "source_pin": "research/pilot_source_research.md",
        "boundary": "Separate competition scenario groups; no recipe, array data or baseline is staged or interchangeable with this task.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "geometry_and_layout": "CT-4; declared spacing/steering and synthetic fixture geometry only, no measured array calibration",
        "timestamp_calibration": "CT-4 / CT-5; channel alignment is a contract item, not a measured timing result",
        "source_target_reference_conditions": "CI-4 / CI-5; missing rights-cleared array corpus and missing separated oracle groups",
        "permissions": "ASSETS missing corpus row; no consent, rights or intended-use grant is staged",
        "task_matched_heldout_labels": "No held-out array labels or benchmark split exists",
        "leakage": "No local leakage, interference-suppression or off-target score exists",
        "target_damage": "CT-6; target preservation is a required but unmeasured control",
        "channel_loss": "CT-5; channel dropout is an adverse control, not a scored result",
        "room_reference_changes": "CT-4 / CT-7; only adjacent synthetic RIR movement controls exist, no room or reference-condition stratum",
    },
    "blocked": [
        "Rights-cleared synchronized array corpus with geometry, calibration, target/reference directions and movement",
        "Pinned runnable delay-and-sum and MVDR/MPDR source or runtime with exact settings",
        "Separated oracle-mask/oracle-steering and estimated-mask comparison groups",
        "Runnable neural spatial checkpoints with licensed weights, array adapters and target definitions",
        "Measured channel synchronization, geometry mismatch, channel loss and target-device timing",
        "Human listening and target-preservation/leakage evidence on held-out array data",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "source_only_beamformer_documentation": True,
    "adjacent_multichannel_synthetic_historical_local": True,
    "source_reported_upstream_claim": True,
    "classic_beamformer_execution": False,
    "neural_spatial_model_execution": False,
    "array_geometry_or_calibration_measured": False,
    "independent_heldout_benchmark": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Implement and execute a deterministic delay-and-sum baseline on a frozen synthetic array fixture with declared geometry and steering",
        "evidence_gap": "Delay-and-sum is catalogued and described by S24 but has no local implementation, fixture, execution or metric record.",
        "follow_up_ids": [
            "SDK-DELAY-AND-SUM-BEAMFORMER",
            "SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The delay-and-sum feasibility row is a scoping lead for a bounded reference and fixture; the foundation row owns evidence-format rules, not a beamforming result.",
    },
    {
        "id": "G02",
        "actionable_gap": "Stage a rights-cleared synchronized array corpus with geometry, channel calibration, timestamp alignment, target/reference directions and movement conditions",
        "evidence_gap": "The catalogued boundary requires synchronized array channels plus spatial assumptions, but only adjacent synthetic two-channel fixtures are reviewed.",
        "follow_up_ids": [
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-FND-DUPLEX",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The alignment feasibility row and the multichannel/clock foundation rows own geometry and timestamp rules; no array corpus or consent grant is created here.",
    },
    {
        "id": "G03",
        "actionable_gap": "Execute MVDR/MPDR against delay-and-sum and keep oracle-mask/oracle-steering and estimated-mask groups separate",
        "evidence_gap": "MVDR/MPDR is catalogued through S24 and S25 only; no covariance estimator, mask model, oracle separation or local score exists.",
        "follow_up_ids": [
            "SDK-MVDR-BEAMFORMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The MVDR feasibility row already requires validation against delay-and-sum and separated mask groups; it does not enable or qualify a beamformer.",
    },
    {
        "id": "G04",
        "actionable_gap": "Resolve the exact SpatialNet checkpoint, licence, array adapter and target definition before any execution",
        "evidence_gap": "SpatialNet is blocked; the repository lead, checkpoint identity, weight terms and compatible multichannel target corpus are unresolved.",
        "follow_up_ids": [
            "SDK-SPATIALNET",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The SpatialNet feasibility row is a discovery lead only; no model is installed, adapted, scored or promoted by this map.",
    },
    {
        "id": "G05",
        "actionable_gap": "Disambiguate Beam-TasNet from Beam-Guided TasNet, then stage one exact implementation, checkpoint and synchronized target data",
        "evidence_gap": "The catalogue label covers two distinct architectures and neither has a local adapter, checkpoint or multichannel evaluation.",
        "follow_up_ids": [
            "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The Beam-TasNet feasibility row is a scoping lead for exact identity and assets; no architecture is selected by this map.",
    },
    {
        "id": "G06",
        "actionable_gap": "Specify one concrete neural beamformer or mask-based MVDR configuration with geometry, spatial loss and matched array evidence",
        "evidence_gap": "Neural beamforming is a blocked algorithm family with no concrete model, array geometry or target benchmark; H-GTCRN is a conditional two-microphone candidate only.",
        "follow_up_ids": [
            "SDK-NEURAL-BEAMFORMING",
            "SDK-H-GTCRN",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "Both feasibility rows are candidate-discovery leads; the foundation row owns evidence format, not a neural spatial result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure channel synchronization, geometry mismatch, channel loss and target-device timing on a real capture array",
        "evidence_gap": "Only adjacent synthetic fixture delays and geometry parameters are recorded; no measured array timing, calibration or device deadline exists.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-DUPLEX",
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The timing, duplex and alignment rows own clock/lifecycle/geometry rules; no measured array or device result is created by this map.",
    },
    {
        "id": "G08",
        "actionable_gap": "Add human listening plus independent held-out array scoring for target preservation, leakage and channel-loss behavior",
        "evidence_gap": "No local listening, held-out array benchmark, leakage or target-damage result exists for any beamformer candidate.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-SI-SDR-SDR-AND-SNR",
            "SDK-STOI-ESTOI",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-07 listening or array-benchmark feasibility row was found; the research-control rows own protocol and metric design, not a listening or qualification result.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-DELAY-AND-SUM-BEAMFORMER", "title": "Delay-and-sum beamformer", "mode": "feasibility"},
    {"task_id": "SDK-MVDR-BEAMFORMING", "title": "MVDR beamforming", "mode": "feasibility"},
    {"task_id": "SDK-NEURAL-BEAMFORMING", "title": "Neural beamforming", "mode": "feasibility"},
    {"task_id": "SDK-SPATIALNET", "title": "SpatialNet", "mode": "feasibility"},
    {"task_id": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET", "title": "Beam-TasNet / Beam-Guided TasNet", "mode": "feasibility"},
    {"task_id": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT", "title": "3D microphone spatial / time alignment", "mode": "feasibility"},
    {"task_id": "SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS", "title": "Pyroomacoustics candidate tools", "mode": "feasibility"},
    {"task_id": "SDK-H-GTCRN", "title": "H-GTCRN", "mode": "feasibility"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-DUPLEX", "title": "Reference, multichannel and clock contracts", "mode": "foundation"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-SI-SDR-SDR-AND-SNR", "title": "SI-SDR, SDR and SNR", "mode": "research-control"},
    {"task_id": "SDK-STOI-ESTOI", "title": "STOI / ESTOI", "mode": "research-control"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-cleared synchronized array corpus with geometry, channel calibration, timestamp alignment, target/reference directions and movement"},
    {"id": "RG-02", "blocked": True, "requirement": "Pinned runnable delay-and-sum and MVDR/MPDR source or runtime with exact settings and a delay-and-sum comparison"},
    {"id": "RG-03", "blocked": True, "requirement": "Concrete neural spatial checkpoint, licensed weights, array adapter, target definition and spatial loss"},
    {"id": "RG-04", "blocked": True, "requirement": "Human listening plus independent held-out array evidence for target preservation, leakage and channel loss"},
    {"id": "RG-05", "blocked": True, "requirement": "Measured channel synchronization, geometry mismatch, channel dropout, room/reference changes and target-device timing"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated claims and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-07 \u2014 Beamforming and spatial filtering** | Combine microphones to emphasize wanted directions or sources.",
        "| **CLN-08 \u2014 Source localization and tracking** | Estimate direction/location to support steering or selection.",
        "| **CLN-04 \u2014 Dereverberation** | Reduce reverberant smearing.",
    ],
    "research/category_survey/sources.md": [
        "| S24 | [Pyroomacoustics beamforming implementation](https://github.com/LCAV/pyroomacoustics/blob/master/pyroomacoustics/beamforming.py) | acoustics | search excerpt |",
        "| S25 | [TorchAudio mask-based MVDR example](https://docs.pytorch.org/audio/main/tutorials/mvdr_tutorial.html) | acoustics | search excerpt |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    ],
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": [
        "Existing local dereverberation work includes WPE, not SpatialNet.",
        "neural beamforming is not one concrete model",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Spatial and speaker,SpatialNet,unavailable/blocked,No local SpatialNet weights/adapter and no synchronized multichannel clean-target corpus; mono evidence cannot score array enhancement.",
        "Spatial and speaker,Neural beamforming,unavailable/blocked,\"Algorithm family lacks a concrete local model, array geometry and multichannel target benchmark.\"",
    ],
    "research/noise_suppression_candidate_census.md": [
        "Two-microphone low-SNR enhancement combining GTCRN, FD-WPE, AuxIVA and spatial features",
    ],
    "research/pilot_source_research.md": [
        "documents WPE, guided source separation, and beamforming for multi-array inputs",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/offline-multichannel-wpe/README.md": [
        "The whole-clip multichannel WPE produced a measurable **regression**",
    ],
    "docs/task-evidence/online-multichannel-wpe/README.md": [
        "**frame-causal**: each emitted 160-sample mono frame is computed from the",
        "content delay is 480 samples",
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
    "real_array_audio": False,
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
    "beamforming_claim_without_beamformer_execution": "rejected; state unchanged",
    "array_claim_without_array_corpus_or_calibration": "rejected; state unchanged",
    "oracle_group_pooled_with_estimated_group": "rejected; state unchanged",
    "adjacent_wpe_pooled_with_cln07": "rejected; state unchanged",
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
        raise MapError("CLN-07 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-07 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F07 / CLN-07 is not unique")
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
            raise MapError("legacy backlog mismatch: F07/CLN-07/%s" % key)


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
    adjacent = set(ADJACENT_BOUNDARY["components"])
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
        if not set(ids) <= adjacent:
            raise MapError("historical execution links a non-adjacent component: " + row["id"])
        if row.get("outcome_class") != "historical_local_adjacent_multichannel_dereverberation":
            raise MapError("historical execution is not labelled adjacent: " + row["id"])
        scope = row.get("scope", "")
        if "not a beamforming result" not in scope:
            raise MapError("historical execution is not bounded as non-beamforming: " + row["id"])
        if "not rerun by this survey" not in scope:
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])
        if not row.get("values"):
            raise MapError("historical execution has no values: " + row["id"])


def _check_evidence_classes() -> None:
    classes = {row["class"] for row in COMPARISON_INPUTS}
    checks = {
        "source_only_beamformer_documentation": "source_only_documentation" in classes,
        "adjacent_multichannel_synthetic_historical_local": "historical_local_adjacent_multichannel" in classes,
        "source_reported_upstream_claim": any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES),
        "classic_beamformer_execution": "historical_local_classic_beamformer" in classes,
        "neural_spatial_model_execution": "historical_local_neural_spatial" in classes,
        "array_geometry_or_calibration_measured": "measured_array_geometry" in classes,
        "independent_heldout_benchmark": "independent_heldout_benchmark" in classes,
        "human_listening_result": "human_listening_result" in classes,
        "device_timing": "device_timing" in classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in ("new_execution_in_this_survey", "parity_or_qualification_claim", "release_claim"):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported claim is not closed: " + key)


def _check_adjacent_boundary() -> None:
    if ADJACENT_BOUNDARY.get("pooled_with_cln_07") is not False:
        raise MapError("adjacent multichannel WPE is pooled with CLN-07")
    if ADJACENT_BOUNDARY.get("results_promoted") is not False:
        raise MapError("adjacent multichannel WPE result is promoted")
    adjacent = set(ADJACENT_BOUNDARY["components"])
    for family in METHOD_FAMILIES:
        overlap = set(family["components"]) & adjacent
        if overlap:
            raise MapError("adjacent WPE appears in a CLN-07 method family: " + ",".join(sorted(overlap)))


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
    _check_adjacent_boundary()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
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
        "qualification": dict(QUALIFICATION),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "spatial_boundary": dict(SPATIAL_BOUNDARY),
        "adjacent_boundary": dict(ADJACENT_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "beamforming_component_ids": [
                "delay-and-sum-beamformer",
                "mvdr-beamforming",
                "neural-beamforming",
                "spatialnet",
                "beam-tasnet-beam-guided-tasnet",
                "h-gtcrn",
            ],
            "boundary_component_ids": [
                "source-localization-direction-of-arrival",
                "3d-microphone-spatial-time-alignment",
                "pyroomacoustics-candidate-tools",
                "auxiva",
            ],
            "real_array_corpus_staged": False,
            "pinned_beamformer_source_or_runtime_staged": False,
            "neural_spatial_weights_present": False,
            "array_geometry_or_calibration_measured": False,
            "independent_heldout_array_split_present": False,
            "real_provider_runtime_parity_present": False,
            "note": (
                "Beamforming candidates are mapped, but no rights-cleared array "
                "corpus, pinned beamformer source/runtime, neural spatial "
                "weights, measured calibration or independent held-out split is "
                "staged; candidates remain considered or blocked."
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
    if report["decision"] != DECISION or report["qualification_status"] != QUALIFICATION_STATUS:
        raise MapError("disposition changed")
    if report["readiness"] != READINESS or report["status"] != STATUS:
        raise MapError("status changed")
    if report["qualification"] != QUALIFICATION:
        raise MapError("qualification object changed")
    if report["qualification"]["status"] != "not_qualified":
        raise MapError("qualification status is not not_qualified")
    if report["qualification"]["proposal_only"] is not True:
        raise MapError("qualification is not proposal-only")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for key, value in report["boundary"].items() if key != "release_approval"):
        raise MapError("boundary is not closed")
    if report["boundary"]["release_approval"] is not False:
        raise MapError("release approval is not false")
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
        "real_array_audio",
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
        "spatial_beamforming_only",
        "extra_microphones_and_oracle_masks_are_separate_comparison_groups",
    ):
        if report["category_scope"][key] is not True:
            raise MapError("category scope rule is not enforced: " + key)
    for key in (
        "synchronized_array_channels_required",
        "array_geometry_and_channel_calibration_in_contract",
        "steering_or_reference_direction_declared",
        "oracle_and_estimated_mask_groups_are_separate",
        "localization_metadata_is_not_a_beamformed_waveform",
        "adjacent_multichannel_dereverberation_is_not_beamforming",
    ):
        if report["spatial_boundary"][key] is not True:
            raise MapError("spatial boundary rule is not enforced: " + key)
    for key in (
        "real_array_corpus_staged",
        "pinned_beamformer_source_or_runtime_staged",
        "neural_spatial_weights_staged",
        "array_timing_or_geometry_measured",
        "human_listening_result",
    ):
        if report["spatial_boundary"][key] is not False:
            raise MapError("spatial boundary claim is not closed: " + key)
    for key in (
        "real_array_corpus_staged",
        "pinned_beamformer_source_or_runtime_staged",
        "neural_spatial_weights_present",
        "array_geometry_or_calibration_measured",
        "independent_heldout_array_split_present",
        "real_provider_runtime_parity_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    if report["adjacent_boundary"]["pooled_with_cln_07"] is not False:
        raise MapError("adjacent WPE is pooled")
    if report["adjacent_boundary"]["results_promoted"] is not False:
        raise MapError("adjacent WPE is promoted")
    if report["evidence_classes"]["classic_beamformer_execution"] is not False:
        raise MapError("classic beamformer execution is claimed without one")
    if report["evidence_classes"]["neural_spatial_model_execution"] is not False:
        raise MapError("neural spatial execution is claimed without one")
    if report["evidence_classes"]["array_geometry_or_calibration_measured"] is not False:
        raise MapError("array calibration is claimed without a measurement")
    if report["evidence_classes"]["independent_heldout_benchmark"] is not False:
        raise MapError("held-out benchmark is claimed without a test split")
    if report["evidence_classes"]["human_listening_result"] is not False:
        raise MapError("human listening is claimed without ratings")
    if report["evidence_classes"]["device_timing"] is not False:
        raise MapError("device timing is claimed without a device array")
    if BOARD_PATH in report["source_pins"]:
        raise MapError("mutable board file is pinned")
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
