# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-08.

This module builds a bounded taxonomy/comparison evidence map for the source
localization and tracking category (inventory category ``CLN-08``). It reads
only pinned, read-only documents from the enclosing ``audioml`` workspace and
the SDK worktree. It does not load audio, weights, runtimes, media or the
network, and it does not register, expose, enable or qualify any processor.

All curated records below are documentation mappings, not new measurements.
Adjacent spatial execution values are transcribed verbatim from pinned merged
evidence and labelled with their original scope; none of them emits a direction
or a track.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-CLN-08"
TITLE = "Review coverage for Source localization and tracking"
CATEGORY_ID = "CLN-08"
LEGACY_FAMILY = "F07"
BRANCH = "swarm/SDK-SURVEY-CLN-08"
BASE_COMMIT = "0ff69ead80e380d758dbe03057790e62d303e284"
PROFILE = "Spatial"
COMPONENT = "source-localization-tracking-evidence-map"
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
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/search_log.jsonl": "61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/dereverberation_candidates_20261028.md": "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary and evidence pins. They are read only
# to prove that no public surface was touched and to ground curated values; no
# header, report or component is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/SDK-PIPE-DUPLEX.md": "c0a550ffafe3de25f7d37ba5eadc23ae94df347666e8212094664d1fffe20871",
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
    "name": "Source localization and tracking",
    "scope": "discovered_extension",
    "output_kind": "annotation/control",
    "purpose": "Estimate direction/location to support steering or selection.",
    "method_families": {
        "classic": "SRP-PHAT; MUSIC/NormMUSIC",
        "ml": "Learned spatial-feature estimators; candidate search pending",
    },
    "input_output": "Array audio and geometry \u2192 direction/track",
    "live_or_comparison_boundary": (
        "Localization is metadata, not a cleaned signal or proof of "
        "intended-speaker identity."
    ),
    "source_ids": ["S26"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "localization_and_tracking_only": True,
    "not_beamforming_or_spatial_filtering_category": "CLN-07",
    "not_generic_separation_category": "SPK-01",
    "not_target_speaker_extraction_category": "SPK-02",
    "not_diarization_or_identity_category": "SPK-04/SPK-05",
    "clock_alignment_is_engineering_boundary": "ENG-02",
    "note": (
        "Beamforming and spatial filtering (CLN-07), generic separation "
        "(SPK-01), target-speaker extraction (SPK-02), diarization or "
        "identity (SPK-04/SPK-05) and clock alignment (ENG-02) are separate "
        "catalogued categories. They are named only to prevent scope "
        "inflation; their results are not pooled into a CLN-08 localization "
        "claim."
    ),
}

LOCALIZATION_BOUNDARY: Dict[str, Any] = {
    "localization_output_is_metadata_not_waveform": True,
    "direction_or_track_is_not_a_cleaned_signal": True,
    "direction_is_not_intended_speaker_identity": True,
    "requires_synchronized_array_geometry_and_timestamps": True,
    "front_back_or_mirror_ambiguity_is_a_material_stratum": True,
    "moving_source_and_track_continuity_in_contract": True,
    "beamforming_and_spatial_filtering_belongs_to_cln_07": True,
    "generic_separation_belongs_to_spk_01": True,
    "target_speaker_extraction_belongs_to_spk_02": True,
    "diarization_and_identity_belongs_to_spk_04_spk_05": True,
    "clock_alignment_belongs_to_eng_02": True,
    "ml_candidate_search_pending": True,
    "classical_srp_phat_or_music_implementation_staged": False,
    "ml_spatial_estimator_weights_staged": False,
    "real_array_geometry_or_calibration_staged": False,
    "labelled_localization_corpus_staged": False,
    "device_timing_or_drift_measured": False,
    "steering_or_extraction_executed": False,
    "human_validation_result": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S26",
        "title": "Pyroomacoustics direction-of-arrival methods",
        "url": "https://pyroomacoustics.readthedocs.io/en/pypi-release/pyroomacoustics.doa.html",
        "access_scope": "search excerpt",
        "mapped_components": [
            "source-localization-direction-of-arrival",
            "3d-microphone-spatial-time-alignment",
        ],
        "gap_ids": ["G01", "G03", "G05"],
        "finding": (
            "The catalogued source is a documentation search excerpt for "
            "Pyroomacoustics direction-of-arrival classes and classical "
            "estimators. It names method families but is not a pinned package, "
            "runtime, array capture, calibrated geometry or labelled corpus. No "
            "package version, execution or numeric parity is staged in this "
            "task; the source remains a documentation lead only."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Steered response power with phase transform (SRP-PHAT) over a declared array geometry",
        "components": ["source-localization-direction-of-arrival"],
        "gap_ids": ["G01", "G03", "G05"],
        "status": "catalogued_only_no_local_implementation_no_geometry_or_labels",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Subspace direction-of-arrival estimation: MUSIC and NormMUSIC",
        "components": ["source-localization-direction-of-arrival"],
        "gap_ids": ["G01", "G05"],
        "status": "catalogued_only_no_local_implementation_no_source_count_result",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Learned spatial-feature estimators (candidate search pending)",
        "components": ["source-localization-direction-of-arrival"],
        "gap_ids": ["G04", "G05"],
        "status": "candidate_search_pending_no_catalogued_candidate_no_weights_or_execution",
    },
]

# Adjacent spatial components are named to keep scope boundaries explicit. They
# are not localization components and none of their results is pooled here.
ADJACENT_BOUNDARIES: List[Dict[str, str]] = [
    {
        "component_id": "3d-microphone-spatial-time-alignment",
        "category_boundary": "geometry and time-alignment prerequisite",
        "relation": "Provides the geometry/clock inputs a locator needs; it does not estimate a direction by itself.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "delay-and-sum-beamformer",
        "category_boundary": "CLN-07 beamforming and spatial filtering",
        "relation": "Consumes a direction or delay set to form a waveform; a beamformer output is not a localization result.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "mvdr-beamforming",
        "category_boundary": "CLN-07 beamforming and spatial filtering",
        "relation": "Mask- or covariance-driven spatial filter; no angle, track or abstinence output is defined.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "auxiva",
        "category_boundary": "SPK-01 generic separation",
        "relation": "Blind source separation; separated channels are not directions and carry permutation ambiguity.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "spatialnet",
        "category_boundary": "CLN-07/SPK-02 adjacent blocked candidate",
        "relation": "Blocked spatial-enhancement candidate with no weights and no synchronized clean-target corpus; no direction output.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "neural-beamforming",
        "category_boundary": "CLN-07 adjacent blocked candidate",
        "relation": "Blocked algorithm family without a concrete model or array geometry; not a learned locator.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "beam-tasnet-beam-guided-tasnet",
        "category_boundary": "SPK-01/SPK-02 adjacent blocked candidate",
        "relation": "Beam-guided separation with unresolved architecture and checkpoint; no direction estimate.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "pyannote-diarization",
        "category_boundary": "SPK-04 anonymous diarization",
        "relation": "Answers who spoke when, not where; anonymous speaker turns are not spatial tracks.",
        "not_localization_evidence": True,
    },
    {
        "component_id": "x-vector-speaker-embeddings",
        "category_boundary": "SPK-05 speaker representation and verification",
        "relation": "Speaker identity representation; same-direction/different-speaker cases stay outside a localization claim.",
        "not_localization_evidence": True,
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "source-localization-direction-of-arrival", "evidence_status": "considered", "task": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"},
    {"component_id": "3d-microphone-spatial-time-alignment", "evidence_status": "considered", "task": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT"},
    {"component_id": "delay-and-sum-beamformer", "evidence_status": "considered", "task": "SDK-DELAY-AND-SUM-BEAMFORMER"},
    {"component_id": "mvdr-beamforming", "evidence_status": "considered", "task": "SDK-MVDR-BEAMFORMING"},
    {"component_id": "auxiva", "evidence_status": "considered", "task": "SDK-AUXIVA"},
    {"component_id": "spatialnet", "evidence_status": "blocked", "task": "SDK-SPATIALNET"},
    {"component_id": "neural-beamforming", "evidence_status": "blocked", "task": "SDK-NEURAL-BEAMFORMING"},
    {"component_id": "beam-tasnet-beam-guided-tasnet", "evidence_status": "blocked", "task": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET"},
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "offline-multichannel-wpe", "evidence_status": "evaluated", "task": "SDK-OFFLINE-MULTICHANNEL-WPE"},
    {"component_id": "online-multichannel-wpe", "evidence_status": "evaluated", "task": "SDK-ONLINE-MULTICHANNEL-WPE"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Offline multichannel WPE frozen two-channel synthetic fixture with declared source angle, second-source angle, microphone spacing and channel delays",
        "class": "historical_local_adjacent_spatial_fixture",
        "source_pin": "docs/task-evidence/offline-multichannel-wpe/report.json",
        "boundary": "Adjacent geometry/room control only: the fixture declares a source angle but no locator is run and no direction or track is produced; synthetic only, no real array or listening result.",
    },
    {
        "id": "CI-2",
        "input": "Online multichannel WPE frozen two-channel synthetic fixture with source azimuth, microphone spacing, per-microphone delays and a content delay",
        "class": "historical_local_adjacent_spatial_fixture",
        "source_pin": "docs/task-evidence/online-multichannel-wpe/report.json",
        "boundary": "Adjacent causal room control only: geometry is fixture metadata, not a calibrated capture and not a localization estimate; no device timing or real-room claim.",
    },
    {
        "id": "CI-3",
        "input": "Pyroomacoustics direction-of-arrival documentation for SRP-PHAT, MUSIC and NormMUSIC over a declared array geometry",
        "class": "source_only_frozen_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation and method names only; no pinned package version, runtime, geometry, labelled corpus or numeric result is staged here.",
    },
    {
        "id": "CI-4",
        "input": "Labelled independent localization/tracking corpus with array geometry, channel calibration, sample timestamps, moving sources, reverberation, overlap and declared permissions",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Explicitly missing. The Spatial acceptance profile requires geometry, timestamp calibration, source/target/reference conditions and task-matched held-out labels.",
    },
    {
        "id": "CI-5",
        "input": "Pinned real microphone-array capture with calibrated positions, orientation, channel gains/delays and sample-clock relation to source annotations",
        "class": "missing_array_metadata",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Missing. Synthetic fixtures declare ideal geometry; no real array calibration, orientation or clock metadata is staged in this task.",
    },
    {
        "id": "CI-6",
        "input": "Catalogued learned spatial-feature estimators: SpatialNet, neural beamforming and Beam-TasNet/Beam-Guided TasNet rows",
        "class": "source_reported_candidate_gap",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "All three are unavailable/blocked spatial-enhancement or separation candidates with no direction output, weights or synchronized multichannel corpus; the ML localization search remains pending.",
    },
    {
        "id": "CI-7",
        "input": "Independent held-out localization split with angular-error, track-fragmentation and latency scoring",
        "class": "missing_no_local_cohort",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Missing. No held-out labels, metric implementation, threshold or independent benchmark exists for CLN-08.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "metadata-only passthrough", "role": "A localization result must not modify the audio path; identity audio is preserved while the angle/track is a separate annotation.", "source_pin": "audio_categories.md"},
    {"id": "CT-2", "name": "known synthetic azimuth and TDOA", "role": "Frozen synthetic geometry with a declared angle or delay is the minimum sanity check, not a real-array result.", "source_pin": "docs/task-evidence/offline-multichannel-wpe/report.json"},
    {"id": "CT-3", "name": "front/back and left/right mirror ambiguity", "role": "Array geometry and estimator symmetry must report the ambiguous solution or abstain; an arbitrary mirror is not a pass.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-4", "name": "silence, noise-only and single-channel abstention", "role": "A locator must abstain or report low confidence when no spatial evidence exists; a forced angle is a failure, not a valid track.", "source_pin": "audio_categories.md"},
    {"id": "CT-5", "name": "moving-source track continuity and reset", "role": "Track identity, gaps, re-entry and reset behavior are frozen separately from per-frame angle error.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-6", "name": "geometry and calibration mismatch", "role": "Wrong spacing, orientation or channel gain must degrade confidence or abstain; silently emitting a plausible angle is not accepted.", "source_pin": "docs/task-evidence/online-multichannel-wpe/README.md"},
    {"id": "CT-7", "name": "dropped frame and timestamp jitter", "role": "Stale or missing channel data must not be treated as a new direction; cross-hop and timestamp calibration are part of the Spatial profile.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-8", "name": "same direction, different speaker identity", "role": "Two speakers at the same angle must not be distinguished by a locator; identity or diarization is a separate category and is never inferred.", "source_pin": "audio_categories.md"},
    {"id": "CT-9", "name": "fixed-beam versus direction-steered ablation", "role": "Adjacent CLN-07 comparison only; steering gain cannot be relabelled as localization accuracy.", "source_pin": "audio_categories.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Source localization / direction-of-arrival inventory candidate row and plan note",
        "class": "plan_metadata",
        "status": "Considered only; no implementation, execution, checkpoint or result is attached to the row",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
    {
        "asset": "Pyroomacoustics direction-of-arrival documentation",
        "class": "external_documentation",
        "status": "Search excerpt only; no package, version, license review, runtime or local execution is staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Offline and online multichannel WPE synthetic two-channel geometry fixtures",
        "class": "sdk_adjacent_synthetic_fixture",
        "status": "Merged task-local room evidence, reused here only as declared geometry controls; it emits no direction and is not a localization result",
        "source_pin": "docs/task-evidence/offline-multichannel-wpe/README.md",
    },
    {
        "asset": "Learned spatial-feature estimator source and weights (SpatialNet, neural beamforming, Beam-TasNet)",
        "class": "missing_model_assets",
        "status": "Not staged; all catalogued rows are blocked and none is a declared direction-of-arrival estimator",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "Calibrated real microphone-array capture with geometry, orientation and clock metadata",
        "class": "missing_array_assets",
        "status": "Not present; synthetic fixtures are not a calibrated array or a device measurement",
        "source_pin": "audio_categories.md",
    },
    {
        "asset": "Labelled held-out localization/tracking corpus and metric protocol",
        "class": "missing_corpus_assets",
        "status": "Not present; no angular labels, track labels, permissions or scoring implementation exists in this task",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Adjacent offline multichannel WPE synthetic fixture with declared two-channel geometry (no direction estimate)",
        "outcome_class": "historical_local_adjacent_spatial_fixture",
        "component_ids": ["offline-multichannel-wpe", "3d-microphone-spatial-time-alignment"],
        "source_pin": "docs/task-evidence/offline-multichannel-wpe/report.json",
        "values": {
            "channels": 2,
            "mic_spacing_m": 0.06,
            "source_angle_deg": 35.0,
            "second_source_angle_deg": -50.0,
            "short_rt60_identity_si_sdr_db": 17.144701,
            "short_rt60_delta_si_sdr_db": -1.863045,
            "short_rt60_delta_stoi": -0.004987,
            "short_rt60_worst_channel_delta_si_sdr_db": -2.317771,
            "nonfinite_count": 0,
        },
        "scope": "Seeded synthetic two-channel whole-clip WPE fixture with frozen geometric TDOA; used only as an adjacent geometry/room control. It emits no direction or track and is not a localization result; no real array, listening, device timing or release claim; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Adjacent online multichannel WPE synthetic fixture with declared source azimuth (no direction estimate)",
        "outcome_class": "historical_local_adjacent_spatial_fixture",
        "component_ids": ["online-multichannel-wpe", "3d-microphone-spatial-time-alignment"],
        "source_pin": "docs/task-evidence/online-multichannel-wpe/report.json",
        "values": {
            "input_channels": 2,
            "mic_spacing_m": 0.04,
            "source_azimuth_deg": 30.0,
            "mic0_delay_samples": 0,
            "mic1_delay_samples": 5,
            "content_delay_samples": 480,
            "si_sdr_db": 11.561154,
            "stoi": 0.982843,
            "nonfinite_count": 0,
        },
        "scope": "Seeded synthetic frame-causal two-channel WPE fixture with declared azimuth and microphone delays; used only as an adjacent geometry/room control. It emits no direction or track and is not a localization result; no real array, listening, device timing or release claim; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "S26 documentation describes Pyroomacoustics direction-of-arrival classes including classical SRP-PHAT, MUSIC and NormMUSIC estimators",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation search excerpt only; no package version, runtime, geometry, label set or numeric result was executed or verified locally.",
    },
    {
        "id": "RO-2",
        "claim": "The category survey records that no dedicated runnable neural-localization candidate was established",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "A search-obligation statement, not evidence that no candidate exists; the ML candidate search remains pending.",
    },
    {
        "id": "RO-3",
        "claim": "SpatialNet, neural beamforming and Beam-TasNet/Beam-Guided TasNet are blocked spatial-enhancement or separation candidates",
        "class": "source_reported",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Blocked candidate rows with no direction output; none is a localization result and none is pooled with CLN-08.",
    },
    {
        "id": "RO-4",
        "claim": "3D microphone spatial/time alignment is a considered prerequisite for synchronized multichannel input",
        "class": "source_reported",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Inventory plan note only; no implementation, calibrated array or execution is attached to this survey.",
    },
    {
        "id": "RO-5",
        "claim": "Pyroomacoustics DOA documentation is the only catalogued source lead for this category",
        "class": "source_reported",
        "source_pin": "research/category_registry.json",
        "boundary": "One documentation lead, not a candidate census; candidate search and benchmark both remain not_started.",
    },
]

EXECUTION_COVERAGE: Dict[str, Any] = {
    "localization_component_count": 1,
    "classical_localization_implementation_count": 0,
    "ml_localization_execution_count": 0,
    "labelled_localization_execution_count": 0,
    "adjacent_spatial_execution_count": len(HISTORICAL_EXECUTIONS),
    "note": (
        "No CLN-08 component has a local implementation, run, angle output or "
        "track. The two historical rows are adjacent multichannel room fixtures "
        "that declare synthetic geometry; they are controls for what is missing, "
        "not localization evidence."
    ),
}

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "geometry_and_layout": "CT-2 / CT-6 declare synthetic geometry and reject silent mismatch; no calibrated real array",
        "timestamp_calibration": "CT-7 and the missing real-array input; fixture chunking is not a device clock",
        "source_target_reference_conditions": "HE-1 / HE-2 record a synthetic source angle only; no source/target/reference classification or permission",
        "held_out_localization_labels": "Missing; CI-4 and CI-7 record the absent labelled split",
        "leakage": "CT-9 separates fixed-beam steering from angle estimation; no steering result is claimed",
        "target_damage_and_channel_loss": "Adjacent HE-1/HE-2 room metrics only; no localization-specific damage or channel-loss result",
        "room_and_reference_changes": "CT-5 / CT-6 cover movement and geometry change as a plan; no measured track or room result",
        "human_validation": "No CLN-08 listening, annotation adjudication or human validation",
    },
    "blocked": [
        "Classical SRP-PHAT and MUSIC/NormMUSIC reference implementation with known-geometry and abstention checks",
        "Rights-qualified labelled independent localization/tracking corpus with calibrated array geometry and timestamps",
        "Learned spatial-feature candidate identification, checkpoint, licensed weights and a declared direction output",
        "Real array capture with orientation, channel calibration and sample-clock/drift evidence",
        "Task-matched metrics for angular error, track fragmentation and latency on a held-out split",
        "Separation from beamforming, separation, diarization and identity with no pooled result",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "adjacent_multichannel_fixture_historical_local": True,
    "source_only_frozen_protocol": True,
    "source_reported_candidate_gap": True,
    "missing_localization_cohort": True,
    "localization_execution_historical_local": False,
    "classical_localization_implementation": False,
    "ml_localization_execution": False,
    "labelled_heldout_localization_benchmark": False,
    "device_array_or_clock_timing": False,
    "human_validation_result": False,
    "steering_or_extraction_execution": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Implement a bounded classical SRP-PHAT and MUSIC/NormMUSIC reference with declared geometry, confidence and explicit abstention",
        "evidence_gap": "Both classic families are catalogued only; no local implementation, synthetic sanity fixture, source-count assumption or abstention behavior exists.",
        "follow_up_ids": [
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The dedicated localization feasibility row owns the scoping lead; this map creates no implementation, result or qualification.",
    },
    {
        "id": "G02",
        "actionable_gap": "Acquire a rights-qualified labelled independent localization/tracking corpus with moving sources, overlap, reverberation and declared permissions",
        "evidence_gap": "No angular or track labels, held-out split, annotation protocol or consent/permission record is staged; only synthetic geometry metadata exists.",
        "follow_up_ids": [
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The localization feasibility row and asset-boundary foundation are scoping leads; no corpus is acquired or cleared here.",
    },
    {
        "id": "G03",
        "actionable_gap": "Define and stage a synchronized real-array geometry, orientation, channel-calibration and sample-timestamp contract before any localization execution",
        "evidence_gap": "Synthetic fixtures declare ideal spacing, azimuth and delays; no measured array, orientation, gain/delay calibration or clock relation is staged.",
        "follow_up_ids": [
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-FND-DUPLEX",
            "SDK-FND-TIMING",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The 3D alignment feasibility row owns geometry and time-alignment scoping; the foundations own reference/clock and lifecycle rules, not a measurement.",
    },
    {
        "id": "G04",
        "actionable_gap": "Complete the learned spatial-feature candidate search and pin one estimator with a declared direction output, checkpoint, licence and runtime",
        "evidence_gap": "The registry says candidate search is pending; the catalogued SpatialNet, neural beamforming and Beam-TasNet rows are blocked and are not localization estimators.",
        "follow_up_ids": [
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
            "SDK-SPATIALNET",
            "SDK-NEURAL-BEAMFORMING",
            "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET",
        ],
        "feasibility_task_exists": True,
        "owner_note": "All three linked rows are feasibility leads; none enables a model or establishes an ML localization result.",
    },
    {
        "id": "G05",
        "actionable_gap": "Define task-matched metrics and a frozen evaluation protocol for angular error, ambiguity, track fragmentation, abstention and latency",
        "evidence_gap": "No CLN-08 metric implementation, threshold, stratification, adversarial case or held-out scoring protocol exists in the workspace.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The evidence foundation owns reproducible scoring rules and the localization feasibility row owns the scoping lead; no benchmark is created.",
    },
    {
        "id": "G06",
        "actionable_gap": "Keep localization metadata separate from beamforming, separation and steering and require an independent comparison for each output",
        "evidence_gap": "CLN-07 beamforming, SPK-01 separation and SPK-02 extraction are catalogued neighbors; no component declares an angle/track output or a steering ablation.",
        "follow_up_ids": [
            "SDK-DELAY-AND-SUM-BEAMFORMER",
            "SDK-MVDR-BEAMFORMING",
            "SDK-AUXIVA",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked beamforming/separation rows are feasibility leads only; no waveform output is pooled into a localization claim.",
    },
    {
        "id": "G07",
        "actionable_gap": "Keep direction/track separate from speaker identity and diarization and test same-direction/different-speaker cases explicitly",
        "evidence_gap": "Diarization and speaker-embedding rows are considered but no identity-labeled array case, same-direction control or correlation analysis is staged.",
        "follow_up_ids": [
            "SDK-PYANNOTE-DIARIZATION",
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The diarization and embedding feasibility rows are scoping leads; no identity, verification or consent result is created or implied.",
    },
    {
        "id": "G08",
        "actionable_gap": "Measure real target-device array capture, timestamp jitter, dropped channels and clock drift on the intended host",
        "evidence_gap": "Only synthetic fixture chunking and declared geometry are reviewed; no target-device content timing, channel loss, deadline or resource measurement exists.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-DUPLEX",
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The timing, duplex and alignment rows are foundation/feasibility scoping leads; none supplies a measured device loop.",
    },
    {
        "id": "G09",
        "actionable_gap": "Clear rights for array recordings, spatial annotations and any learned spatial estimator before release evidence",
        "evidence_gap": "No recording consent, annotation licence, array-fixture redistribution term or model per-weight right is staged.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-08 rights feasibility row was found; the asset-boundary foundation and localization feasibility rows own scoping, not a rights grant.",
    },
    {
        "id": "G10",
        "actionable_gap": "Require independent exact-head review before any benchmark, public default or release claim",
        "evidence_gap": "This proposal-only map has no independent reviewer, no benchmark result and no default-selection approval.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-08 review feasibility row was found; the evidence and asset-boundary foundations own protocol and intake rules, not independent approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL", "title": "Source localization / direction-of-arrival", "mode": "feasibility"},
    {"task_id": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT", "title": "3D microphone spatial / time alignment", "mode": "feasibility"},
    {"task_id": "SDK-DELAY-AND-SUM-BEAMFORMER", "title": "Delay-and-sum beamformer", "mode": "feasibility"},
    {"task_id": "SDK-MVDR-BEAMFORMING", "title": "MVDR beamforming", "mode": "feasibility"},
    {"task_id": "SDK-AUXIVA", "title": "AuxIVA", "mode": "feasibility"},
    {"task_id": "SDK-SPATIALNET", "title": "SpatialNet", "mode": "feasibility"},
    {"task_id": "SDK-NEURAL-BEAMFORMING", "title": "Neural beamforming", "mode": "feasibility"},
    {"task_id": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET", "title": "Beam-TasNet / Beam-Guided TasNet", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-DIARIZATION", "title": "pyannote diarization", "mode": "feasibility"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-DUPLEX", "title": "Reference, multichannel and clock contracts", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Classical SRP-PHAT and MUSIC/NormMUSIC reference implementation with known-geometry, ambiguity, source-count and abstention checks"},
    {"id": "RG-02", "blocked": True, "requirement": "Rights-qualified labelled independent localization/tracking corpus with calibrated array geometry and timestamps"},
    {"id": "RG-03", "blocked": True, "requirement": "Learned spatial-feature candidate identification, checkpoint, licensed weights and a declared direction output"},
    {"id": "RG-04", "blocked": True, "requirement": "Real target-device array capture with orientation, channel calibration, sample-clock and drift evidence"},
    {"id": "RG-05", "blocked": True, "requirement": "Task-matched metrics and a held-out scoring protocol for angular error, ambiguity, track fragmentation, abstention and latency"},
    {"id": "RG-06", "blocked": True, "requirement": "Separation from beamforming, separation, diarization and identity; no steering, extraction or identity claim is pooled"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Explicit public default selection approval and release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated facts and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-08 \u2014 Source localization and tracking** | Estimate direction/location to support steering or selection. Scope: discovered_extension. | SRP-PHAT; MUSIC/NormMUSIC | Learned spatial-feature estimators; candidate search pending | Array audio and geometry \u2192 direction/track | Localization is metadata, not a cleaned signal or proof of intended-speaker identity. | [S26](https://pyroomacoustics.readthedocs.io/en/pypi-release/pyroomacoustics.doa.html) |",
        "| **CLN-07 \u2014 Beamforming and spatial filtering** | Combine microphones to emphasize wanted directions or sources.",
    ],
    "research/category_survey/sources.md": [
        "| S26 | [Pyroomacoustics direction-of-arrival methods](https://pyroomacoustics.readthedocs.io/en/pypi-release/pyroomacoustics.doa.html) | acoustics | search excerpt |",
        "No dedicated runnable wind, neural-localization, learned-EQ or classical bandwidth-extension candidate was established.",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    ],
    "audio-benchmark-platform/plan/INVENTORY.json": [
        "Return angle and confidence with synchronized geometry; benchmark spatial alignment.",
    ],
    "research/task_backlog.json": [
        "{\"activation_state\":\"catalogued\",\"blockers\":[],\"category_id\":\"CLN-08\",\"dependencies\":[],\"family_id\":\"F07\"",
    ],
    "research/category_survey/search_log.jsonl": [
        "\"exact_query\":\"pyroomacoustics official documentation beamforming DOA MUSIC SRP PHAT\"",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Spatial and speaker,SpatialNet,unavailable/blocked",
        "Spatial and speaker,Neural beamforming,unavailable/blocked",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/offline-multichannel-wpe/README.md": [
        "leading prefix, two seeded synthetic RIRs per condition with frozen geometric",
    ],
    "docs/task-evidence/online-multichannel-wpe/README.md": [
        "geometry (0.04 m mic spacing, 30-degree source azimuth, 0/5-sample mic delays,",
    ],
    "docs/task-evidence/SDK-PIPE-DUPLEX.md": [
        "capture with timestamped far-end render, validates and aligns the reference,",
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
    "localization_claim_without_localization_execution": "rejected; state unchanged",
    "localization_claim_without_geometry_and_labels": "rejected; state unchanged",
    "steering_claim_without_steering_execution": "rejected; state unchanged",
    "heldout_benchmark_claim_without_test_split": "rejected; state unchanged",
    "metadata_promoted_to_clean_signal": "rejected; state unchanged",
    "identity_claim_without_speaker_labels": "rejected; state unchanged",
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
        raise MapError("CLN-08 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-08 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F07 / CLN-08 is not unique")
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
            raise MapError("legacy backlog mismatch: F07/CLN-08/%s" % key)


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
        if component.get("verification_profile") not in ("spatial", "room"):
            raise MapError("component profile is not spatial or adjacent room: " + row["component_id"])
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    mapped.update(row["component_id"] for row in ADJACENT_BOUNDARIES)
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    if not any(row["component_id"] == "source-localization-direction-of-arrival" for row in COMPONENT_CENSUS):
        raise MapError("localization component is not censused")


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
        if row.get("outcome_class") != "historical_local_adjacent_spatial_fixture":
            raise MapError("historical execution is not explicitly adjacent: " + row["id"])
        if "not a localization result" not in row.get("scope", ""):
            raise MapError("historical execution is not labelled not-a-localization: " + row["id"])
        if "not rerun by this survey" not in row.get("scope", ""):
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])
        if not row.get("values"):
            raise MapError("historical execution has no values: " + row["id"])


def _check_evidence_classes() -> None:
    classes = {row["class"] for row in COMPARISON_INPUTS}
    checks = {
        "adjacent_multichannel_fixture_historical_local": "historical_local_adjacent_spatial_fixture" in classes,
        "source_only_frozen_protocol": "source_only_frozen_protocol" in classes,
        "source_reported_candidate_gap": "source_reported_candidate_gap" in classes,
        "missing_localization_cohort": "missing_no_local_cohort" in classes,
        "localization_execution_historical_local": False,
        "classical_localization_implementation": False,
        "ml_localization_execution": False,
        "labelled_heldout_localization_benchmark": False,
        "device_array_or_clock_timing": "device_clock" in classes,
        "human_validation_result": "human_validation" in classes,
        "steering_or_extraction_execution": "steering_execution" in classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in ("new_execution_in_this_survey", "parity_or_qualification_claim", "release_claim"):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported claim is not closed: " + key)
    if not any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES):
        raise MapError("source-reported class has no backing row")


def _check_execution_coverage() -> None:
    counts = {
        "classical_localization_implementation_count": 0,
        "ml_localization_execution_count": 0,
        "labelled_localization_execution_count": 0,
    }
    for key, expected in counts.items():
        if EXECUTION_COVERAGE.get(key) != expected:
            raise MapError("execution coverage claim changed: " + key)
    if EXECUTION_COVERAGE.get("adjacent_spatial_execution_count") != len(HISTORICAL_EXECUTIONS):
        raise MapError("adjacent execution count is inconsistent")
    if any("localization" in row["outcome_class"] for row in HISTORICAL_EXECUTIONS):
        raise MapError("an adjacent execution is relabelled as localization")
    if not any(lead["access_scope"] == "search excerpt" for lead in SOURCE_LEADS):
        raise MapError("S26 access scope is not a search excerpt")


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
    _check_execution_coverage()
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
            "readiness": READINESS,
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
            "localization_execution_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "localization_boundary": dict(LOCALIZATION_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "localization_component_ids": ["source-localization-direction-of-arrival"],
            "independent_heldout_localization_split_present": False,
            "licensed_localization_corpus_staged": False,
            "ml_localization_candidate_selected": False,
            "ml_spatial_estimator_weights_present": False,
            "real_array_geometry_or_calibration_present": False,
            "classical_localization_implementation_present": False,
            "note": "The localization slot is catalogued as considered only. No independent licensed split, ML candidate, weights, calibrated array or classical implementation is staged.",
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
    if report["qualification"]["localization_execution_present"] is not False:
        raise MapError("a localization execution is claimed")
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
        "localization_output_is_metadata_not_waveform",
        "direction_or_track_is_not_a_cleaned_signal",
        "direction_is_not_intended_speaker_identity",
        "requires_synchronized_array_geometry_and_timestamps",
        "front_back_or_mirror_ambiguity_is_a_material_stratum",
        "moving_source_and_track_continuity_in_contract",
        "beamforming_and_spatial_filtering_belongs_to_cln_07",
        "generic_separation_belongs_to_spk_01",
        "target_speaker_extraction_belongs_to_spk_02",
        "diarization_and_identity_belongs_to_spk_04_spk_05",
        "clock_alignment_belongs_to_eng_02",
        "ml_candidate_search_pending",
    ):
        if report["localization_boundary"][key] is not True:
            raise MapError("localization boundary rule is not enforced: " + key)
    for key in (
        "classical_srp_phat_or_music_implementation_staged",
        "ml_spatial_estimator_weights_staged",
        "real_array_geometry_or_calibration_staged",
        "labelled_localization_corpus_staged",
        "device_timing_or_drift_measured",
        "steering_or_extraction_executed",
        "human_validation_result",
    ):
        if report["localization_boundary"][key] is not False:
            raise MapError("localization boundary claim is not closed: " + key)
    for key in (
        "independent_heldout_localization_split_present",
        "licensed_localization_corpus_staged",
        "ml_localization_candidate_selected",
        "ml_spatial_estimator_weights_present",
        "real_array_geometry_or_calibration_present",
        "classical_localization_implementation_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    if report["evidence_classes"]["localization_execution_historical_local"] is not False:
        raise MapError("localization is claimed without a localization execution")
    if report["evidence_classes"]["labelled_heldout_localization_benchmark"] is not False:
        raise MapError("held-out benchmark is claimed without a labelled split")
    if report["evidence_classes"]["human_validation_result"] is not False:
        raise MapError("human validation is claimed without annotations")
    if report["evidence_classes"]["device_array_or_clock_timing"] is not False:
        raise MapError("device timing is claimed without an array measurement")
    if report["evidence_classes"]["steering_or_extraction_execution"] is not False:
        raise MapError("steering or extraction is claimed without an execution")
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
