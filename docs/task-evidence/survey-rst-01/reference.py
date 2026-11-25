# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-RST-01.

This module builds a bounded taxonomy/comparison evidence map for the
declipping and saturation-restoration category (inventory category ``RST-01``).
It reads only pinned, read-only documents from the enclosing ``audioml``
workspace and the SDK worktree. It does not load audio, weights, runtimes,
media or the network, and it does not register, expose, enable or qualify any
processor.

All curated records below are documentation mappings, not new measurements.
Historical local-pilot or source-reported values are transcribed verbatim from
the pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-RST-01"
TITLE = "Review coverage for Declipping and saturation restoration"
CATEGORY_ID = "RST-01"
LEGACY_FAMILY = "F10"
BRANCH = "swarm/SDK-SURVEY-RST-01"
BASE_COMMIT = "711c5c2a419edf258d6858fa90293c5900faad82"
PROFILE = "Restoration"
COMPONENT = "declipping-saturation-evidence-map"
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
    "reports/distortion-restoration/20261028-synthetic-screen.json": "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "src/audioml_eval/distortion_restoration.py": "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/band-limited-pocs-declipping/README.md": "8e6bfec06db0b02321d6b6313536cf4a438204680d28240c15c9f57189dcdc65",
    "docs/task-evidence/linear-interpolation-declipping/README.md": "ab68e2a7b000f5b73e26e97e0ebb95c45ff15e1db2922d26365ac96466758a6d",
    "docs/task-evidence/peak-limiter-reference/README.md": "ee0900e6ccb51579f9aebccb0c1bedda413e65b1656fb53c6477e0251527d0c9",
    "docs/task-evidence/quality-impairment-taxonomy/README.md": "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
    "docs/task-evidence/static-target-gain-with-peak-ceiling/README.md": "692acca143160e9506cde6e40a0b692c2f400751f79734b8a8cbeb1410bd47d8",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Distortion restoration",
    "name": "Declipping and saturation restoration",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Estimate signal lost to amplitude clipping.",
    "method_families": {
        "classic": "Autoregressive interpolation; sparse constrained reconstruction; SPADE",
        "ml": "Neural restoration and resynthesis",
    },
    "input_output": "Clipped audio, optional clipping mask/model \u2192 restored waveform",
    "live_or_comparison_boundary": (
        "Limiting prevents overload but does not reconstruct lost samples. "
        "Evaluate speech fidelity, not only smoothness."
    ),
    "source_ids": ["S28", "S31"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S28",
        "title": "Author declipping implementations",
        "url": "https://github.com/rajmic/declipping2020_codes",
        "access_scope": "direct",
        "mapped_components": [
            "c-omp-declipping",
            "spade-and-social-sparsity-declipping",
            "matlab-ltfat-cvx-sparse-declipping-tools",
        ],
        "gap_ids": ["G04"],
        "finding": (
            "The author repository establishes the sparse/constrained declipping "
            "family (C-OMP, SPADE and related methods). Its open toolbox needs "
            "MATLAB, LTFAT and, for C-OMP, CVX, so it was not runnable in the "
            "Python pilot and no local execution, pinned dependency or rights "
            "review exists in the reviewed records."
        ),
    },
    {
        "source_id": "S31",
        "title": "VoiceFixer restoration implementation",
        "url": "https://github.com/haoheliu/voicefixer",
        "access_scope": "search excerpt",
        "mapped_components": ["voicefixer"],
        "gap_ids": ["G06"],
        "finding": (
            "Registry access is a search excerpt, not a pinned checkout. "
            "VoiceFixer is a general neural restoration/resynthesis lead. No "
            "local source, checkpoint, license review, matched clipped-speech "
            "cohort or numeric result was found; the component is considered, "
            "not evaluated."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Autoregressive / neighbour interpolation of clipped sample runs",
        "components": ["linear-interpolation-declipping", "autoregressive-plc"],
        "gap_ids": ["G02"],
        "status": "linear_synthetic_local_only_ar_declipping_not_executed",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Band-limited projection onto convex sets (constrained reconstruction)",
        "components": ["band-limited-pocs-declipping"],
        "gap_ids": ["G03"],
        "status": "synthetic_local_2048_sample_blocks_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Sparse constrained reconstruction, SPADE and social sparsity",
        "components": [
            "c-omp-declipping",
            "spade-and-social-sparsity-declipping",
            "matlab-ltfat-cvx-sparse-declipping-tools",
        ],
        "gap_ids": ["G04"],
        "status": "not_executed_blocked_or_considered",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Level control, overload and saturation boundary (adjacent, not reconstruction)",
        "components": ["peak-limiter-reference", "static-target-gain-with-peak-ceiling"],
        "gap_ids": ["G05"],
        "status": "adjacent_local_dsp_not_a_declipping_result",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural restoration and resynthesis (named source lead S31 VoiceFixer)",
        "components": ["voicefixer"],
        "gap_ids": ["G06"],
        "status": "source_reported_search_excerpt_not_staged",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Unified multi-distortion neural restoration benchmark material",
        "components": ["ccf-aatc-unified-restoration-controls"],
        "gap_ids": ["G07"],
        "status": "registration_and_asset_gate_not_run",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "band-limited-pocs-declipping", "evidence_status": "evaluated", "task": "SDK-BAND-LIMITED-POCS-DECLIPPING"},
    {"component_id": "linear-interpolation-declipping", "evidence_status": "evaluated", "task": "SDK-LINEAR-INTERPOLATION-DECLIPPING"},
    {"component_id": "c-omp-declipping", "evidence_status": "blocked", "task": "SDK-C-OMP-DECLIPPING"},
    {"component_id": "spade-and-social-sparsity-declipping", "evidence_status": "considered", "task": "SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING"},
    {"component_id": "matlab-ltfat-cvx-sparse-declipping-tools", "evidence_status": "blocked", "task": "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS"},
    {"component_id": "voicefixer", "evidence_status": "considered", "task": "SDK-VOICEFIXER"},
    {"component_id": "ccf-aatc-unified-restoration-controls", "evidence_status": "considered", "task": "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"},
    {"component_id": "peak-limiter-reference", "evidence_status": "source-local", "task": "SDK-PEAK-LIMITER-REFERENCE"},
    {"component_id": "static-target-gain-with-peak-ceiling", "evidence_status": "evaluated", "task": "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING"},
    {"component_id": "autoregressive-plc", "evidence_status": "evaluated", "task": "SDK-AUTOREGRESSIVE-PLC"},
    {"component_id": "linear-interpolation-plc", "evidence_status": "evaluated", "task": "SDK-LINEAR-INTERPOLATION-PLC"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "12 EARS clips hard-clipped at 0.35 and 0.55 of normalized peak (2.74% and 0.55% occupancy)",
        "class": "historical_local_pilot_not_reproduced",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Transcribed pilot means; bytes and per-clip rows are provenance only and were not rerun by this survey.",
    },
    {
        "id": "CI-2",
        "input": "Frozen 2048-sample synthetic POCS fixtures: tones, transients, speech-like bursts and saturation stress",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/band-limited-pocs-declipping/README.md",
        "boundary": "Generated stimuli and exact derived masks; no real speech or blind detection.",
    },
    {
        "id": "CI-3",
        "input": "Frozen 2048-sample synthetic linear-interpolation fixtures including leading/trailing/all-clipped runs",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/linear-interpolation-declipping/README.md",
        "boundary": "Generated stimuli and exact known masks; caller masks must match the derived mask exactly.",
    },
    {
        "id": "CI-4",
        "input": "Author declipping toolbox under MATLAB/LTFAT/CVX (named source lead S28)",
        "class": "source_reported_not_run",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "No local runtime, dependency install, revision pin or rights review; source-reported scope only.",
    },
    {
        "id": "CI-5",
        "input": "VoiceFixer neural restoration/resynthesis source lead (named source lead S31)",
        "class": "source_reported_only",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt scope; no source checkout, checkpoint, cohort or numeric result.",
    },
    {
        "id": "CI-6",
        "input": "CCF AATC 2025 unified speech-restoration challenge material",
        "class": "external_registration_gated_not_run",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Participant registration and large data gate; no local material, run or score.",
    },
    {
        "id": "CI-7",
        "input": "Adjacent level-control fixtures with a hard peak ceiling",
        "class": "historical_local_adjacent_level_control",
        "source_pin": "docs/task-evidence/static-target-gain-with-peak-ceiling/README.md",
        "boundary": "Controls the limiting boundary only; level control does not reconstruct clipped samples.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "clipped-input identity",
        "role": "Task-matched damaged-input baseline for both local and pilot clipping strata.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-2",
        "name": "exact-mask linear interpolation",
        "role": "Classical comparator on the same frozen masks; it degrades relative to clipped input at every local stratum.",
        "source_pin": "docs/task-evidence/linear-interpolation-declipping/README.md",
    },
    {
        "id": "CT-3",
        "name": "band-limit, iteration and occupancy sweep",
        "role": "POCS cutoff 2/3.5/7.6 kHz, 1 versus 60 iterations, 0.49%-98.68% occupancy; descriptive, not a tuning rule.",
        "source_pin": "docs/task-evidence/band-limited-pocs-declipping/README.md",
    },
    {
        "id": "CT-4",
        "name": "clean identity and zero-occupancy transparency",
        "role": "Bit-identical clean/identity outputs in both local packages; not general broadband transparency.",
        "source_pin": "docs/task-evidence/band-limited-pocs-declipping/README.md",
    },
    {
        "id": "CT-5",
        "name": "peak limiter / static target gain with hard ceiling",
        "role": "Adjacent level-control boundary; demonstrates overload prevention, not lost-peak reconstruction.",
        "source_pin": "docs/task-evidence/peak-limiter-reference/README.md",
    },
    {
        "id": "CT-6",
        "name": "nonfinite-input adverse case",
        "role": "NaN/Inf input produces no serialized output and cannot count as a pass.",
        "source_pin": "docs/task-evidence/band-limited-pocs-declipping/README.md",
    },
    {
        "id": "CT-7",
        "name": "supplied threshold / exact clipping mask",
        "role": "Corruption metadata is known to the methods; blind clipping detection and threshold estimation are untested.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-8",
        "name": "normative pilot declip implementations",
        "role": "Defines declip_pocs (7,600 Hz cutoff, 60 iterations) and declip_linear on the exact derived mask; read as context, not executed here.",
        "source_pin": "src/audioml_eval/distortion_restoration.py",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "EARS 12-clip hard-clipping pilot media",
        "class": "research_audio",
        "status": "CC BY-NC in the cited report; bytes not staged or verified in this task",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "asset": "Task-local frozen synthetic fixtures (POCS and linear interpolation)",
        "class": "generated_fixture",
        "status": "Derived tones, transients and speech-like bursts; no external media or download",
        "source_pin": "docs/task-evidence/band-limited-pocs-declipping/README.md",
    },
    {
        "asset": "Author declipping toolbox and data (S28)",
        "class": "external_code_and_data",
        "status": "MATLAB/LTFAT/CVX dependency; no pinned revision, local install or license review",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "asset": "VoiceFixer source and checkpoints (S31)",
        "class": "source_and_metadata_only",
        "status": "Search excerpt; no checkpoint, runtime or rights clearance staged",
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
        "label": "12-clip hard-clipping pilot means at thresholds 0.35 and 0.55",
        "outcome_class": "historical_local_pilot_not_reproduced",
        "component_ids": ["band-limited-pocs-declipping", "linear-interpolation-declipping"],
        "source_pin": "research/distortion_restoration_20261028.md",
        "values": {
            "pocs_si_sdr_threshold0_35_db": 15.05,
            "pocs_si_sdr_threshold0_55_db": 23.32,
            "pocs_gain_over_clipped_threshold0_35_db": 0.25,
            "pocs_gain_over_clipped_threshold0_55_db": 0.56,
            "pocs_stoi_threshold0_35": 0.9712,
            "pocs_stoi_threshold0_55": 0.9917,
            "linear_si_sdr_threshold0_35_db": 10.99,
            "linear_stoi_threshold0_35": 0.9469,
            "clipped_si_sdr_threshold0_35_db": 14.79,
        },
        "scope": "12 clips per task, modest 2.74%/0.55% clipping occupancy, no human evaluation; pilot means transcribed, not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Band-limited POCS synthetic cohort including clean-transparency control",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["band-limited-pocs-declipping"],
        "source_pin": "docs/task-evidence/band-limited-pocs-declipping/README.md",
        "values": {
            "cases": 18,
            "complete_cases": 17,
            "adverse_cases": 1,
            "successful_pocs_runs": 9,
            "rejected_controls": 17,
            "not_run_results": 7,
            "pocs_si_sdr_very_low_db": 8.832,
            "pocs_si_sdr_low_db": 8.865,
            "pocs_si_sdr_mid_db": 13.807,
            "pocs_si_sdr_high_db": 9.398,
            "pocs_si_sdr_saturated_db": 4.932,
            "clipped_si_sdr_very_low_db": 7.818,
            "clipped_si_sdr_low_db": 8.101,
            "clipped_si_sdr_high_db": 9.263,
            "max_output_peak": 0.9,
            "max_delta_initial": 0.00175,
            "max_delta_at_60_iterations": 0.0000713,
            "iteration_cap": 60,
        },
        "scope": "Frozen 2048-sample offline blocks, exact derived masks, generated stimuli; no real speech, streaming or device timing; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Linear-interpolation synthetic cohort with occupancy and boundary controls",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["linear-interpolation-declipping"],
        "source_pin": "docs/task-evidence/linear-interpolation-declipping/README.md",
        "values": {
            "cases": 21,
            "complete_cases": 20,
            "adverse_cases": 1,
            "rejected_controls": 22,
            "not_run_results": 8,
            "linear_si_sdr_very_low_db": 3.86,
            "linear_si_sdr_low_db": 3.771,
            "linear_si_sdr_mid_db": 12.784,
            "linear_si_sdr_high_db": 4.925,
            "linear_si_sdr_saturated_db": -34.51,
            "delta_vs_clipped_very_low_db": -3.96,
            "delta_vs_clipped_low_db": -4.33,
            "delta_vs_clipped_mid_db": -0.99,
            "delta_vs_clipped_high_db": -4.34,
            "delta_vs_clipped_saturated_db": -39.71,
            "max_output_peak": 0.9,
        },
        "scope": "Frozen 2048-sample offline blocks with exact known masks; generated stimuli and boundary cases; no real speech or listening; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Author declipping toolbox covers many sparse/constrained methods including C-OMP",
        "class": "source_reported",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Toolbox scope is documented, not locally executed; MATLAB/LTFAT/CVX and revision/rights remain unresolved.",
    },
    {
        "id": "RO-2",
        "claim": "VoiceFixer provides neural speech restoration/resynthesis",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt source scope; no local checkpoint, clipped-speech run or matched cohort is created here.",
    },
    {
        "id": "RO-3",
        "claim": "CCF AATC 2025 challenge defines unified multi-distortion restoration and its complexity assessment",
        "class": "source_reported",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Challenge framing only; data requires registration and was not staged or scored.",
    },
    {
        "id": "RO-4",
        "claim": "Band-limited POCS is the best local lightweight declipping baseline in the pilot",
        "class": "source_reported_pilot_conclusion",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Small pilot with modest occupancy and no listening; not a general best-method or release claim.",
    },
    {
        "id": "RO-5",
        "claim": "Per-clip synthetic screen ledger records the RST-01 rows behind the pilot means",
        "class": "source_reported_provenance_ledger",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
        "boundary": "Provenance only; the ledger was not rerun, re-scored or pooled with the task-local synthetic cohorts.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "frozen_corruption_and_metadata": "CI-1..CI-3: thresholds, exact masks, crop/rate policy and clean references are recorded per cohort",
        "matched_damaged_baseline": "CT-1 clipped-input identity plus CT-2 exact-mask linear interpolation",
        "degradation_strata": "CI-1 2.74%/0.55% occupancy; CI-2/CI-3 very-low to saturated occupancy strata",
        "bandwidth_strata": "CT-3 projection cutoffs 2/3.5/7.6 kHz on a fixed synthetic source",
        "task_specific_quality": "HE-1 SI-SDR/STOI pilot means; HE-2/HE-3 local SI-SDR observations; no new perceptual score",
        "speech_fidelity_not_smoothness": "CT-5 separates limiting from reconstruction; G09 keeps listening and fidelity as an open gate",
        "validity_and_peak_bounds": "CT-6 nonfinite adverse case; cohort-only output peak bound 0.900",
        "missing_result_accounting": "HE-2 seven and HE-3 eight explicit not_run results; no missing result qualifies a candidate",
        "listening": "VCTK items prepared with zero ratings; no RST-01 listening result exists",
        "timing": "No target-device content/availability, memory or deadline measurement is mapped",
    },
    "blocked": [
        "Rights-qualified paired clipped-speech cohort with frozen corruption and clean reference",
        "Blind clipping detection and threshold estimation independent of supplied masks",
        "True sparse-constrained baseline (SPADE/social sparsity/C-OMP) at matched geometry",
        "Neural restoration candidate with pinned weights, rights and a matched cohort",
        "Independent blinded listening and speech-fidelity analysis",
        "Target-device content/availability timing, memory and deadline evidence",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "historical_pilot_means_not_reproduced": True,
    "clean_transparency_diagnostic_historical_local": True,
    "unpaired_predictive_historical_local": False,
    "prepared_listening_without_ratings": True,
    "human_listening_result": False,
    "vendor_or_source_reported": True,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Detect clipping and estimate its threshold without a supplied mask",
        "evidence_gap": "Every mapped screen supplies the exact clipping mask or threshold to the algorithm; no blind detector, occupancy estimate or false-positive cost was measured.",
        "follow_up_ids": ["SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers blind clipping detection; the linked research-control and foundation rows own evidence and preservation boundaries only.",
    },
    {
        "id": "G02",
        "actionable_gap": "Evaluate autoregressive interpolation for declipping rather than adjacent PLC",
        "evidence_gap": "The classic family names autoregressive interpolation, but local declipping evidence is linear interpolation only; the AR component was evaluated for packet loss, not clipping.",
        "follow_up_ids": ["SDK-AUTOREGRESSIVE-PLC", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has an AR declipping execution; the linked implementation row owns packet-loss concealment, a different inverse problem.",
    },
    {
        "id": "G03",
        "actionable_gap": "Move POCS declipping beyond 2048-sample synthetic offline blocks",
        "evidence_gap": "POCS is evaluated only on generated 2048-sample blocks with exact masks; there is no real-speech, streaming, boundary-continuity or device result.",
        "follow_up_ids": ["SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "SDK-FND-TIMING"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a real-speech or streaming declipping protocol; linked rows own cohort preservation and timing acceptance.",
    },
    {
        "id": "G04",
        "actionable_gap": "Run sparse-constrained, SPADE and C-OMP declipping at matched geometry",
        "evidence_gap": "Sparse/constrained methods are the established next comparison, but SPADE is considered, C-OMP is blocked and the MATLAB/LTFAT/CVX toolbox was not runnable or rights-reviewed.",
        "follow_up_ids": [
            "SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING",
            "SDK-C-OMP-DECLIPPING",
            "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally executed sparse declipper; linked feasibility, research-control and external-adapter rows are scoping leads, not capabilities.",
    },
    {
        "id": "G05",
        "actionable_gap": "Separate soft saturation/overload from hard clipping and keep limiting as a control",
        "evidence_gap": "The mapped pilot models hard clipping at two thresholds only; no soft saturation, multi-stage overload or limiter-induced distortion case exists, and level control is not reconstruction.",
        "follow_up_ids": [
            "SDK-PEAK-LIMITER-REFERENCE",
            "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers saturation restoration; linked implementation rows own level control and the foundation row owns evidence rules, not lost-signal recovery.",
    },
    {
        "id": "G06",
        "actionable_gap": "Stage and evaluate a pinned neural restoration candidate (VoiceFixer)",
        "evidence_gap": "S31 is a search excerpt; no source checkout, exact checkpoint, license review, clipped-speech cohort or local output exists for the ML family.",
        "follow_up_ids": ["SDK-VOICEFIXER"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally evaluated neural declipper; the linked feasibility row is a bounded scoping lead, not an enabled processor or checkpoint.",
    },
    {
        "id": "G07",
        "actionable_gap": "Obtain registered unified-restoration material and a matched protocol",
        "evidence_gap": "CCF AATC is the relevant learned-restoration benchmark, but its data requires participant registration and no local material, split or score exists.",
        "follow_up_ids": ["SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has registered or staged the challenge data; the linked research-control row owns the comparison scope.",
    },
    {
        "id": "G08",
        "actionable_gap": "Freeze a rights-qualified paired clipped-speech cohort with manifests",
        "evidence_gap": "Local fixtures are generated; the pilot's EARS clips are CC BY-NC research media and no rights-qualified paired declipping manifest exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a rights-qualified declipping cohort; linked research-control and foundation rows own manifests and evidence rules.",
    },
    {
        "id": "G09",
        "actionable_gap": "Run independent blinded listening and speech-fidelity analysis",
        "evidence_gap": "No human rating exists; the pilot reports SI-SDR/STOI and no perceptual test, and the registry requires speech fidelity rather than smoothness.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner collected RST-01 ratings; the linked research-control rows own listening design and preservation scoring, not a result.",
    },
    {
        "id": "G10",
        "actionable_gap": "Measure target-device content, availability, memory and deadline behavior",
        "evidence_gap": "Only offline synthetic block runs exist; no callback-path, device or paced workload timing is mapped for any declipping method.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has device-timing evidence; linked foundation rows own acceptance and lifecycle rules.",
    },
    {
        "id": "G11",
        "actionable_gap": "Define an opt-in provider intake and public exposure path",
        "evidence_gap": "Both local packages are unregistered developer adapters; no provider descriptor, installed-archive comparison, default selection or independent review exists.",
        "follow_up_ids": ["SDK-FND-PROVIDER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake; linked foundation rows own provider boundaries and exact-head evidence.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING", "title": "SPADE and social-sparsity declipping", "mode": "feasibility"},
    {"task_id": "SDK-C-OMP-DECLIPPING", "title": "C-OMP declipping", "mode": "research-control"},
    {"task_id": "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS", "title": "MATLAB/LTFAT/CVX sparse declipping tools", "mode": "external-adapter"},
    {"task_id": "SDK-VOICEFIXER", "title": "VoiceFixer", "mode": "feasibility"},
    {"task_id": "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS", "title": "CCF AATC unified restoration controls", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
    {"task_id": "SDK-PEAK-LIMITER-REFERENCE", "title": "Peak limiter reference", "mode": "implementation"},
    {"task_id": "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING", "title": "Static target gain with peak ceiling", "mode": "implementation"},
    {"task_id": "SDK-AUTOREGRESSIVE-PLC", "title": "Autoregressive PLC", "mode": "implementation"},
]

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
)

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified paired clipped-speech cohort with frozen corruption, mask and clean reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent blinded listening and speech-fidelity analysis, not smoothness only"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched sparse-constrained and neural baselines under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Exact approved reference parity at a frozen revision and settings"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **RST-01 — Declipping and saturation restoration** |",
        "Limiting prevents overload but does not reconstruct lost samples. Evaluate speech fidelity, not only smoothness.",
    ],
    "research/category_survey/sources.md": [
        "| S28 | [Author declipping implementations](https://github.com/rajmic/declipping2020_codes) | acoustics | direct |",
        "| S31 | [VoiceFixer restoration implementation](https://github.com/haoheliu/voicefixer) | acoustics | search excerpt |",
        "* [Author declipping project](https://rajmic.github.io/declipping2020/) and its linked code establish a restoration family.",
    ],
    "research/distortion_restoration_20261028.md": [
        "A limiter cannot recover clipped peaks, resampling cannot infer missing high frequencies, and packet concealment benefits from codec state or redundant packets.",
        "| Declipping, threshold 0.35 (2.74% of samples clipped) | Band-limited POCS | 15.05 dB SI-SDR | +0.25 dB vs clipped input; linear interpolation drops to 10.99 dB |",
        "| Declipping, threshold 0.55 (0.55% clipped) | Band-limited POCS | 23.32 dB SI-SDR | +0.56 dB vs clipped input |",
        "No neural restoration checkpoint was evaluated in the screen.",
        "requires MATLAB, LTFAT and (for C-OMP) CVX, so it was not runnable in the current Python pilot.",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Restoration | Freeze corruption, metadata and corresponding clean/audio packet baseline. Stratify by degradation, erasure burst and bandwidth. Report discrete concealment/validity, decoded intervals, task-specific quality and bounds on output peaks and timing. |",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/band-limited-pocs-declipping/README.md": [
        "| `occupancy_mid` | 0.55 · speech_like · pocs | 9.5703 | 1.000 → 0.561 | 13.807 |",
        "The 98.68% saturation case is a control showing heavy",
        "No unconditional transparency is claimed for broadband clean input: the",
        "Seven results are recorded `not_run`",
    ],
    "docs/task-evidence/linear-interpolation-declipping/README.md": [
        "| `occupancy_very_low` | 0.35 · very_sparse_transients · linear | 0.4883 | 1.000 → 0.324 | 3.860 |",
        "linear interpolation is below the clipped-input",
        "Eight results are recorded `not_run`",
    ],
    "docs/task-evidence/peak-limiter-reference/README.md": [
        "**SDK-PEAK-LIMITER-REFERENCE · DSP acceptance profile · status: opt-in,",
        "No model, real speech, corpus, device,",
    ],
    "docs/task-evidence/static-target-gain-with-peak-ceiling/README.md": [
        "the whole reset-delimited segment and hard-clamp every output to `+/- ceiling`.",
        "There is no attack, release, lookahead, per-sample adaptation or model.",
    ],
    "docs/task-evidence/quality-impairment-taxonomy/README.md": [
        "At threshold 0.35 the reported clip occupancy was 2.74% and POCS gained only 0.25 dB SI-SDR",
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
        raise MapError("RST-01 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("RST-01 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F10 / RST-01 is not unique")
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
            raise MapError("legacy backlog mismatch: F10/RST-01/%s" % key)


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
    comparison = [row["class"] for row in COMPARISON_INPUTS]
    labels = [row["label"].lower() for row in HISTORICAL_EXECUTIONS]
    classes = comparison + labels
    predictive = any("predictive" in c for c in classes)
    transparency = any("transparency" in c for c in classes)
    pilot = any("pilot_not_reproduced" in c for c in classes)
    if EVIDENCE_CLASSES["unpaired_predictive_historical_local"] != predictive:
        raise MapError("unpaired-predictive evidence class does not match mapped records")
    if EVIDENCE_CLASSES["clean_transparency_diagnostic_historical_local"] != transparency:
        raise MapError("clean-transparency evidence class does not match mapped records")
    if EVIDENCE_CLASSES["historical_pilot_means_not_reproduced"] != pilot:
        raise MapError("pilot-means evidence class does not match mapped records")
    prepared = any("prepared" in row["status"].lower() for row in ASSETS)
    if EVIDENCE_CLASSES["prepared_listening_without_ratings"] != prepared:
        raise MapError("prepared-listening evidence class does not match assets")
    reported = any(c.startswith("source_reported") for c in classes)
    if EVIDENCE_CLASSES["vendor_or_source_reported"] != reported:
        raise MapError("source-reported evidence class does not match records")


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
        elif not gap.get("owner_note"):
            raise MapError("gap without feasibility task has no owner note: " + gap["id"])
    orphan = sorted(known - used)
    if orphan:
        raise MapError("board link is not referenced by any gap: " + ",".join(orphan))
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
        linked_gaps = sorted(g["id"] for g in GAPS if link["task_id"] in g["follow_up_ids"])
        if not linked_gaps:
            raise MapError("board link is not referenced by any gap: " + link["task_id"])
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
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
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
