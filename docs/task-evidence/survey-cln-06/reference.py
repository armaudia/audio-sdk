# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-06.

This module builds a bounded taxonomy/comparison evidence map for the
residual-echo-suppression category (inventory category ``CLN-06``). It reads
only pinned, read-only documents from the enclosing ``audioml`` workspace and
the SDK worktree. It does not load audio, weights, runtimes, media or the
network, and it does not register, expose, enable or qualify any processor.

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
TASK = "SDK-SURVEY-CLN-06"
TITLE = "Review coverage for Residual echo suppression"
CATEGORY_ID = "CLN-06"
LEGACY_FAMILY = "F04"
BRANCH = "swarm/SDK-SURVEY-CLN-06"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
PROFILE = "Room"
COMPONENT = "residual-echo-suppression-evidence-map"
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
    "research/aec_research_20261028.md": "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header or component is copied, edited or
# generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER.md": "b9efbe044c002485d4b5dbcc87ef8bf040daead08f9284f3ce19f61e6a32cc45",
    "docs/task-evidence/erle-and-double-talk-preservation/report.json": "6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50",
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": "16c7643cc5550cd7358ee48f7dec62eb4045a3384364246cd357269ce0c28da9",
    "docs/task-evidence/speex-mdf-residual-postfilter/report.json": "ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6",
    "docs/task-evidence/speexdsp-mdf-reference/evidence/REPORT.md": "a5b1a6e91203d18eac546e130bf02515eea22139b222e0b4c52dd4bab2dc0eb6",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Residual echo suppression",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Reduce echo remaining after cancellation.",
    "method_families": {
        "classic": "Echo-aware spectral attenuation/nonlinear postfiltering",
        "ml": "Echo-aware masks or postfilters",
    },
    "input_output": "AEC output + method-specific echo/reference information \u2192 waveform",
    "live_or_comparison_boundary": (
        "Distinguish cancellation from attenuation. Near-end speech can be harmed "
        "during double talk."
    ),
    "source_ids": ["S23"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "residual_echo_suppression_only": True,
    "not_reference_based_aec_category": "CLN-05",
    "not_background_noise_suppression_category": "CLN-01",
    "not_transient_click_repair_category": "CLN-02",
    "cancellation_and_attenuation_are_distinct": True,
    "near_end_speech_can_be_harmed_during_double_talk": True,
    "note": (
        "Reference-based acoustic echo cancellation is CLN-05, background noise "
        "suppression is CLN-01 and transient click repair is CLN-02. Those rows "
        "are named only as boundaries; their results are not pooled into a "
        "CLN-06 residual-echo claim."
    ),
}

RESIDUAL_BOUNDARY: Dict[str, Any] = {
    "operates_after_cancellation": True,
    "requires_aec_output_and_method_specific_echo_or_reference_information": True,
    "cancellation_and_attenuation_are_distinct": True,
    "blind_one_input_route_is_not_reference_aec": True,
    "non_echo_aware_noise_suppression_is_adjacent_only": True,
    "residual_specific_candidates_and_weights_discovered": False,
    "residual_specific_cohort_staged": False,
    "residual_specific_execution_performed": False,
    "residual_specific_benchmark_or_listening_result": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S23",
        "title": "Speex preprocessor and residual echo suppression",
        "url": "https://www.speex.org/docs/api/speex-api-reference/group__SpeexPreprocessState.html",
        "access_scope": "search excerpt",
        "mapped_components": [
            "speex-mdf-residual-postfilter",
            "speexdsp-mdf-reference",
        ],
        "gap_ids": ["G01", "G02"],
        "finding": (
            "The catalogued source is an API-reference search excerpt for the "
            "Speex preprocessor residual-echo-suppression path, not a runnable "
            "candidate, pinned upstream revision, trained mask or residual-echo "
            "cohort. The local optional SpeexDSP MDF postfilter is the only "
            "component-specific execution found, and it did not recover near-end "
            "preservation against MDF alone. No residual-echo-specific mask, "
            "checkpoint or benchmark is staged in this task."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Echo-aware spectral attenuation and nonlinear postfiltering bound to adaptive canceller state",
        "components": [
            "speex-mdf-residual-postfilter",
            "speexdsp-mdf-reference",
        ],
        "gap_ids": ["G01", "G02"],
        "status": "historical_local_synthetic_and_adjacent_pilot_no_residual_benchmark",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Post-AEC broadband noise suppression used as an adjacent, non-echo-aware attenuation control",
        "components": [
            "webrtc-aec3",
            "webrtc-aec3-plus-apm-ns-levels-1-3",
        ],
        "gap_ids": ["G02", "G03"],
        "status": "historical_local_adjacent_non_echo_aware_suppression_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Blind one-input decaying-tail suppression without a far-end reference",
        "components": ["native-blind-residual-echo-suppression"],
        "gap_ids": ["G06"],
        "status": "native_source_only_no_local_sdk_execution_no_reference_comparison",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural residual echo suppression with an explicit paired reference",
        "components": [
            "dual-branch-residual-echo-suppressor",
            "cagcrn-joint-aec-and-ns",
            "neural-kalman-filtering-nkf",
        ],
        "gap_ids": ["G02", "G04"],
        "status": "catalogued_or_blocked_no_local_execution_no_weights",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "End-to-end or jointly trained neural AEC models with internal echo-aware postfilters",
        "components": [
            "localvqe-compact-echo-only",
            "localvqe-compact-full",
            "dtln-aec-128-256-512",
            "deepaec",
            "dual-path-echo-net",
        ],
        "gap_ids": ["G03", "G05"],
        "status": "historical_local_adjacent_aec_pilot_and_blocked_candidates",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "speex-mdf-residual-postfilter", "evidence_status": "evaluated", "task": "SDK-SPEEX-MDF-RESIDUAL-POSTFILTER"},
    {"component_id": "speexdsp-mdf-reference", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-MDF-REFERENCE"},
    {"component_id": "webrtc-aec3", "evidence_status": "evaluated", "task": "SDK-WEBRTC-AEC3"},
    {"component_id": "webrtc-aec3-plus-apm-ns-levels-1-3", "evidence_status": "evaluated", "task": "SDK-WEBRTC-AEC3-PLUS-APM-NS-LEVELS-1-3"},
    {"component_id": "native-blind-residual-echo-suppression", "evidence_status": "native-local", "task": "PRO-NATIVE-BLIND-RESIDUAL-ECHO-SUPPRESSION"},
    {"component_id": "dual-branch-residual-echo-suppressor", "evidence_status": "considered", "task": "SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR"},
    {"component_id": "cagcrn-joint-aec-and-ns", "evidence_status": "considered", "task": "SDK-CAGCRN-JOINT-AEC-AND-NS"},
    {"component_id": "neural-kalman-filtering-nkf", "evidence_status": "considered", "task": "SDK-NEURAL-KALMAN-FILTERING-NKF"},
    {"component_id": "localvqe-compact-echo-only", "evidence_status": "evaluated", "task": "SDK-LOCALVQE-COMPACT-ECHO-ONLY"},
    {"component_id": "localvqe-compact-full", "evidence_status": "evaluated", "task": "SDK-LOCALVQE-COMPACT-FULL"},
    {"component_id": "dtln-aec-128-256-512", "evidence_status": "blocked", "task": "SDK-DTLN-AEC-128-256-512"},
    {"component_id": "deepaec", "evidence_status": "blocked", "task": "SDK-DEEPAEC"},
    {"component_id": "dual-path-echo-net", "evidence_status": "blocked", "task": "SDK-DUAL-PATH-ECHO-NET"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "SpeexDSP MDF with and without the optional residual postfilter on five frozen paired synthetic render/capture conditions at 16 kHz",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md",
        "boundary": "Five synthetic conditions and two variants; 20 ms overlap near ratio includes residual echo; no real speech, double-talk quality, listening or device timing.",
    },
    {
        "id": "CI-2",
        "input": "Twelve training-only Microsoft AEC Challenge synthetic scenarios comparing MDF alone with MDF plus residual echo suppression",
        "class": "historical_local_adjacent_aec_pilot",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Training split only, 20 ms frames; suppressor left ERLE unchanged and lowered near-reference SNR; not an independent residual benchmark.",
    },
    {
        "id": "CI-3",
        "input": "Twelve recorded AEC Challenge real training device groups scored with predicted AECMOS v4",
        "class": "historical_local_adjacent_real_training_pilot",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Recorded training corpus, no clean near-end references and no human ratings; AECMOS is a learned metric and the subset is not cleared for redistribution.",
    },
    {
        "id": "CI-4",
        "input": "Seeded Gaussian and text-to-speech double-talk fixtures with a short synthetic echo path and the Speex residual suppressor",
        "class": "historical_local_synthetic_stress",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Short artificial echo paths and one local TTS voice; near-reference SNR penalizes residual echo and speech distortion; not real speech or a quality result.",
    },
    {
        "id": "CI-5",
        "input": "WebRTC AEC3 with APM noise-suppression levels 1-3 as an adjacent post-cancellation attenuation control",
        "class": "historical_local_adjacent_non_echo_aware",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "APM NS is broadband noise suppression, not an echo-aware residual postfilter; the ablation is adjacent context only and predicted AECMOS is not a human rating.",
    },
    {
        "id": "CI-6",
        "input": "Dual-branch residual echo suppressor, CAGCRN, neural Kalman, DTLN-AEC, DeepAEC and Dual-Path Echo Net publications and model-card claims",
        "class": "source_reported_only",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "No exact code, checkpoint, revision, runtime, cohort or numeric parity was verified locally; considered or blocked rows only.",
    },
    {
        "id": "CI-7",
        "input": "Dedicated residual-echo cohort with far-end reference, clean near-end target, double-talk, echo-path change and no-reference cases",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "The registry still places dedicated residual-echo candidates and their weights in discovery; none is staged here.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "MDF alone with residual postfilter OFF", "role": "Exact paired baseline for the optional Speex residual postfilter; the postfilter must beat this control without losing near-end speech.", "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md"},
    {"id": "CT-2", "name": "zero-render bit-exact passthrough", "role": "Near-end-only and no-reference control; proves passthrough behavior, not suppression.", "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/report.json"},
    {"id": "CT-3", "name": "converged far-end-only ERLE window", "role": "ERLE is valid only on far-end-only frames; a one-frame misaligned reference did not reduce ERLE, so ERLE is not an alignment detector.", "source_pin": "docs/task-evidence/speexdsp-mdf-reference/evidence/REPORT.md"},
    {"id": "CT-4", "name": "20 ms overlap near ratio", "role": "Preservation proxy that includes residual echo; it is an upper bound and not a double-talk pass.", "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md"},
    {"id": "CT-5", "name": "identity and fixed attenuation baselines", "role": "Research-control baselines separating attenuation from adaptive cancellation and near-end damage.", "source_pin": "docs/task-evidence/erle-and-double-talk-preservation/report.json"},
    {"id": "CT-6", "name": "paired noisy-input identity and per-scenario baseline", "role": "Synthetic and real training pilot baselines; keeps each stratum and device group separate.", "source_pin": "research/aec_research_20261028.md"},
    {"id": "CT-7", "name": "AECMOS predicted versus human-rating separation", "role": "Keeps learned AECMOS echo/degradation scores out of listening and qualification claims.", "source_pin": "REALTIME_COMPONENT_CANDIDATES.md"},
    {"id": "CT-8", "name": "non-echo-aware APM NS ablation", "role": "Adjacent suppression control only; WebRTC NS has no echo-aware postfilter state and cannot be relabelled as residual echo suppression.", "source_pin": "research/aec_research_20261028.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Vendored SpeexDSP 1.2.1 MDF and preprocess sources plus the optional task-local residual postfilter adapter",
        "class": "sdk_vendored_source",
        "status": "Optional adapter is default OFF and unregistered; only a frozen synthetic fixture exists",
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md",
    },
    {
        "asset": "Microsoft AEC Challenge synthetic and real training subsets",
        "class": "local_research_corpus",
        "status": "Training-only subsets retained locally; source-component rights and recording privacy remain unresolved and nothing is redistributed",
        "source_pin": "research/aec_research_20261028.md",
    },
    {
        "asset": "Microsoft AECMOS v4 16 kHz ONNX weights",
        "class": "research_metric_weights",
        "status": "Predicted metric weights only; not human ratings; exact hash is cited in the research ledger",
        "source_pin": "research/aec_research_20261028.md",
    },
    {
        "asset": "Dual-branch residual echo suppressor, CAGCRN, neural Kalman, DTLN-AEC, DeepAEC and Dual-Path Echo Net source or checkpoints",
        "class": "research_model_assets",
        "status": "No exact code, checkpoint, runtime or per-weight rights verified or staged here; considered or blocked only",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "Native Pro blind one-input residual suppressor source",
        "class": "pro_native_source",
        "status": "Source-local in audio-pro; no local SDK execution, weights, cohort, independent comparison or rights clearance",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
    {
        "asset": "Dedicated residual-echo cohort with paired far-end reference and clean near-end target",
        "class": "missing_no_local_cohort",
        "status": "Not present; the category remains catalogued with candidate census and benchmark not_started",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Speex MDF optional residual postfilter frozen paired synthetic oracle",
        "outcome_class": "historical_local_synthetic_paired",
        "component_ids": ["speex-mdf-residual-postfilter"],
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md",
        "values": {
            "conditions": 5,
            "variants": 2,
            "repeats": 3,
            "external_pins": 20,
            "legacy_blobs": 9,
            "far_end_erle_mdf_only_db": 15.675997,
            "far_end_erle_postfilter_db": 15.590018,
            "overlap_near_ratio_mdf_only": 0.968517,
            "overlap_near_ratio_postfilter": 0.687357,
            "overlap_near_ratio_delta": -0.28116,
            "withheld_metric_count": 20,
        },
        "scope": "16 kHz mono 160-sample paired synthetic render/capture, five conditions and two variants; far-end ERLE and the 20 ms overlap near ratio include residual echo; no real speech, double-talk quality, listening or device timing; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "SpeexDSP MDF plus residual echo suppressor on the AEC Challenge synthetic train subset",
        "outcome_class": "historical_local_adjacent_aec_pilot",
        "component_ids": ["speexdsp-mdf-reference", "speex-mdf-residual-postfilter"],
        "source_pin": "research/aec_research_20261028.md",
        "values": {
            "paired_scenarios": 12,
            "far_end_erle_mdf_db": 7.22,
            "far_end_erle_postfilter_db": 7.22,
            "near_reference_snr_mdf_db": 4.74,
            "near_reference_snr_postfilter_db": -3.65,
            "compute_rtf_mdf": 401.0,
            "compute_rtf_postfilter": 307.0,
        },
        "scope": "Twelve training-only synthetic scenarios with 20 ms frames; the suppressor left far-end ERLE unchanged and lowered double-talk near-reference SNR by about 8.4 dB; no real room, human rating or independent benchmark; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Speex residual suppressor direct stress on Gaussian and TTS near-end fixtures",
        "outcome_class": "historical_local_synthetic_stress",
        "component_ids": ["speex-mdf-residual-postfilter"],
        "source_pin": "research/aec_research_20261028.md",
        "values": {
            "gaussian_near_reference_snr_mdf_db": 15.28,
            "gaussian_near_reference_snr_postfilter_db": -2.95,
            "gaussian_far_end_erle_mdf_db": 23.71,
            "gaussian_far_end_erle_postfilter_db": 23.62,
            "tts_near_reference_snr_mdf_db": 6.98,
            "tts_near_reference_snr_postfilter_db": -3.66,
            "tts_far_end_erle_mdf_db": 12.77,
            "tts_far_end_erle_postfilter_db": 12.76,
        },
        "scope": "Short seeded synthetic echo paths and one local text-to-speech voice; near-reference SNR penalizes residual echo and speech distortion; not real speech, listening or a quality result; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "SpeexDSP MDF plus residual suppression on the AEC Challenge real training pilot",
        "outcome_class": "historical_local_adjacent_predicted_metric",
        "component_ids": ["speexdsp-mdf-reference", "speex-mdf-residual-postfilter"],
        "source_pin": "research/aec_research_20261028.md",
        "values": {
            "device_groups": 12,
            "double_talk_echo_mos": 3.23,
            "double_talk_degradation_mos": 3.91,
            "movement_double_talk_echo_mos": 3.14,
            "movement_double_talk_degradation_mos": 3.86,
            "near_end_only_degradation_mos": 3.58,
            "median_rtf": 298.0,
        },
        "scope": "Twelve recorded training device groups scored with predicted AECMOS v4; no clean near-end references, clock-drift test or human listening; learned MOS-like scores are not subjective ratings; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "WebRTC AEC3 with APM noise-suppression levels as an adjacent post-cancellation attenuation control",
        "outcome_class": "historical_local_adjacent_non_echo_aware",
        "component_ids": ["webrtc-aec3", "webrtc-aec3-plus-apm-ns-levels-1-3"],
        "source_pin": "research/aec_research_20261028.md",
        "values": {
            "paired_synthetic_scenarios": 12,
            "synthetic_erle_aec3_db": 20.97,
            "synthetic_erle_ns1_db": 23.26,
            "synthetic_erle_ns3_db": 23.68,
            "synthetic_near_snr_aec3_db": 2.00,
            "synthetic_near_snr_ns1_db": -2.32,
            "synthetic_compute_rtf_aec3": 60.86,
            "real_device_groups": 12,
            "real_double_talk_echo_mos_aec3": 4.06,
            "real_double_talk_echo_mos_ns3": 4.51,
            "real_double_talk_degradation_mos_aec3": 2.51,
            "real_double_talk_degradation_mos_ns3": 2.38,
        },
        "scope": "APM noise suppression is broadband and not echo-aware; the ablation is an adjacent suppression control, not a residual echo suppressor; predicted AECMOS is not human listening; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "The Speex preprocessor API documents a residual echo suppression path",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt API documentation only; no exact upstream revision, tuned configuration, runtime or residual-echo cohort is pinned here.",
    },
    {
        "id": "RO-2",
        "claim": "SpeexDSP residual suppression damaged near-end speech in tested settings and should not be enabled by default",
        "class": "source_reported",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Recorded pilot caveat, not a component-isolated residual benchmark; no real-speech rating, listening result or default decision follows.",
    },
    {
        "id": "RO-3",
        "claim": "Residual suppression left ERLE unchanged while lowering double-talk near-reference SNR by about 8.4 dB on the AEC Challenge synthetic train pilot",
        "class": "historical_local_reported",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Training-only synthetic subset, 12 paired scenarios; not an independent benchmark or production ranking; not rerun by this survey.",
    },
    {
        "id": "RO-4",
        "claim": "Upstream LocalVQE reports an 800-clip AEC Challenge 2022 blind-set evaluation",
        "class": "source_reported",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Upstream claim only; not reproduced locally and end-to-end AEC rather than a separable residual postfilter.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "render_reference_freeze": "CI-1/CI-2/CI-5; frozen synthetic delay/path and 20 ms frames, but no measured RIR, drift or real render history",
        "echo_only": "HE-1; converged far-end-only ERLE 15.675997 dB with MDF alone versus 15.590018 dB with the postfilter",
        "near_end_only": "CT-2; bit-exact zero-render passthrough control, not a suppressor result",
        "overlap_double_talk": "HE-1 20 ms overlap near ratio 0.968517 -> 0.687357 including residual echo; HE-2/HE-4 near-reference SNR and predicted degradation",
        "no_reference": "CT-2 zero-render passthrough; the blind one-input route has no independent local comparison or reference-based AEC label",
        "alignment": "HE-1 zero content delay; a one-frame misaligned reference still measured higher ERLE, so ERLE is not an alignment detector",
        "nonfinite_failures": "HE-1 rejects nonfinite capture and missing render; no residual-chain nonfinite sweep on real or long double-talk audio",
        "predicted_quality": "HE-4/HE-5 AECMOS v4 predicted echo and degradation scores; not human ratings",
        "listening": "No residual-specific listening items, ratings, playback clearance or human preference result",
        "alignment_state_memory_timing": "Only synthetic offline fixtures; no target-device content/availability timing, memory or deadline evidence",
        "clean_preservation": "CT-4 20 ms overlap near ratio only; no clean near-end reference under double talk",
    },
    "blocked": [
        "Rights-qualified paired residual-echo cohort with clean near-end reference and echo-path change",
        "Separate double-talk, near-only, no-reference, delayed and missing-render protocols with frozen metadata",
        "Independent authorized listening and clean-speech preservation under double talk",
        "Pinned target-device content/availability timing, memory and deadline evidence",
        "Task-matched external residual-echo baseline under a locked runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Exact approved reference parity at frozen revision and settings",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "adjacent_aec_pilot_historical_local": True,
    "predicted_metric_historical_local": True,
    "adjacent_non_echo_aware_suppression_historical_local": True,
    "source_reported_only": True,
    "residual_specific_benchmark": False,
    "clean_near_reference_double_talk": False,
    "human_listening_result": False,
    "ml_residual_local_execution": False,
    "target_device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified residual-echo cohort with far-end reference, clean near-end target, double talk, echo-path change and no-reference cases",
        "evidence_gap": "No residual-specific cohort is staged; the category remains catalogued with candidate census and benchmark not_started, and current rows are training-only synthetic or recorded pilot subsets.",
        "follow_up_ids": [
            "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-06 feasibility row exists for a residual-echo cohort; the research-control fixture and foundation evidence rows own fixtures and rules, not a residual capability.",
    },
    {
        "id": "G02",
        "actionable_gap": "Establish near-end preservation and double-talk safety for residual suppression on valid paired real speech",
        "evidence_gap": "The only component-specific execution is five synthetic conditions where the 20 ms overlap near ratio fell from 0.968517 to 0.687357; pilot near-reference SNR fell by about 8.4 dB. No clean near-end reference under double talk exists.",
        "follow_up_ids": [
            "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION",
            "SDK-AECMOS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-06 feasibility row was found; the research-control rows own ERLE/preservation protocol and predicted scoring, not a residual suppressor or a preservation pass.",
    },
    {
        "id": "G03",
        "actionable_gap": "Run independent authorized listening and human quality ratings for residual suppression under double talk",
        "evidence_gap": "AECMOS echo/degradation values are learned predictions, not human ratings; no residual-specific listening items, playback clearance or preference result was found.",
        "follow_up_ids": [
            "SDK-AECMOS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-06 listening feasibility row exists; the linked rows govern predicted scoring and evidence rules, not human listening.",
    },
    {
        "id": "G04",
        "actionable_gap": "Acquire and pin runnable neural residual-suppression code, checkpoints and a locked runtime",
        "evidence_gap": "The dual-branch residual echo suppressor, CAGCRN joint AEC/NS and neural Kalman leads are considered only; no exact repository, checkpoint, revision or runtime was verified locally.",
        "follow_up_ids": [
            "SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR",
            "SDK-CAGCRN-JOINT-AEC-AND-NS",
            "SDK-NEURAL-KALMAN-FILTERING-NKF",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked ML feasibility rows are discovery leads only; none is enabled, installed or a residual-echo quality claim.",
    },
    {
        "id": "G05",
        "actionable_gap": "Resolve blocked end-to-end and joint AEC checkpoints before making any internal-postfilter claim",
        "evidence_gap": "DTLN-AEC, DeepAEC and Dual-Path Echo Net are blocked; only mock or generic TFLite coverage exists, no paired-reference checkpoint or residual-specific result is available.",
        "follow_up_ids": [
            "SDK-DTLN-AEC-128-256-512",
            "SDK-DEEPAEC",
            "SDK-DUAL-PATH-ECHO-NET",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked end-to-end AEC feasibility rows are blocked discovery leads; no model is staged or promoted by this map.",
    },
    {
        "id": "G06",
        "actionable_gap": "Give the blind one-input residual route an independent comparison and never label it as reference-based AEC",
        "evidence_gap": "The native blind suppressor is source-local in audio-pro with no local SDK execution, identity comparison, cohort or rights clearance; its one-input route cannot use a far-end reference.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-06 feasibility row exists for the blind route; the foundation rows own evidence and asset-boundary rules, not a suppressor implementation.",
    },
    {
        "id": "G07",
        "actionable_gap": "Collect target-device content/availability timing, memory and deadline evidence for a residual-suppression chain",
        "evidence_gap": "Only offline synthetic and training-pilot RTF values exist; no callback-path, memory, deadline or device timing was measured for a suppressor chain.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-06 timing feasibility row was found; the foundation rows own lifecycle, acceptance and timing evidence rules.",
    },
    {
        "id": "G08",
        "actionable_gap": "Secure rights-qualified paired render/capture audio and model weights with provenance",
        "evidence_gap": "AEC Challenge subsets remain local with unresolved source-component and recording-privacy terms; ML model weights are not acquired or rights-cleared.",
        "follow_up_ids": [
            "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-06 rights feasibility row exists; the fixture and foundation rows own rights-aware manifests and public-boundary intake, not a rights grant.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES", "title": "AEC Challenge paired render/capture fixtures", "mode": "research-control"},
    {"task_id": "SDK-AECMOS", "title": "AECMOS", "mode": "research-control"},
    {"task_id": "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION", "title": "ERLE and double-talk preservation", "mode": "research-control"},
    {"task_id": "SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR", "title": "Dual-branch residual echo suppressor", "mode": "feasibility"},
    {"task_id": "SDK-CAGCRN-JOINT-AEC-AND-NS", "title": "CAGCRN joint AEC and NS", "mode": "feasibility"},
    {"task_id": "SDK-NEURAL-KALMAN-FILTERING-NKF", "title": "Neural Kalman filtering (NKF)", "mode": "feasibility"},
    {"task_id": "SDK-DTLN-AEC-128-256-512", "title": "DTLN-AEC 128/256/512", "mode": "feasibility"},
    {"task_id": "SDK-DEEPAEC", "title": "DeepAEC", "mode": "feasibility"},
    {"task_id": "SDK-DUAL-PATH-ECHO-NET", "title": "Dual-Path Echo Net", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified paired residual-echo cohort with clean near-end reference and echo-path change"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent authorized listening and declared clean-speech preservation under double talk"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched external residual-echo baseline with double-talk, near-only, no-reference and path-change subcases under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-07", "blocked": True, "requirement": "Exact approved reference parity at frozen revision and settings"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-06 \u2014 Residual echo suppression** | Reduce echo remaining after cancellation.",
        "Distinguish cancellation from attenuation. Near-end speech can be harmed during double talk.",
    ],
    "research/category_survey/sources.md": [
        "| S23 | [Speex preprocessor and residual echo suppression](https://www.speex.org/docs/api/speex-api-reference/group__SpeexPreprocessState.html) | acoustics | search excerpt |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Room | Freeze render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise and reset schedule.",
        "A no-reference suppressor gets its own independent comparison.",
    ],
    "research/aec_research_20261028.md": [
        "On the Gaussian near-end stress signal it lowered near-reference SNR from 15.28 dB to -2.95 dB while leaving far-end ERLE nearly unchanged (23.71 to 23.62 dB).",
        "SpeexDSP residual suppression left ERLE unchanged and lowered near-end SNR by about 8.4 dB.",
        "SpeexDSP residual suppression ranked highest for double-talk degradation MOS, but had much lower echo MOS",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "Residual suppression damaged near-end speech in tested settings and should not be enabled by default.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": [
        "Near-end preservation against MDF alone was **not recovered**:",
    ],
    "docs/task-evidence/speexdsp-mdf-reference/evidence/REPORT.md": [
        "A one-frame reference shift did **not** reduce measured ERLE",
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
    "real_residual_echo_audio": False,
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
    "residual_claim_without_residual_execution": "rejected; state unchanged",
    "residual_claim_without_clean_near_reference": "rejected; state unchanged",
    "non_echo_aware_suppression_labeled_residual": "rejected; state unchanged",
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
        raise MapError("CLN-06 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-06 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F04 / CLN-06 is not unique")
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
            raise MapError("legacy backlog mismatch: F04/CLN-06/%s" % key)


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
    outcome_classes = " ".join(row["outcome_class"] for row in HISTORICAL_EXECUTIONS).lower()
    labels = " ".join(row["label"].lower() for row in HISTORICAL_EXECUTIONS)
    scopes = " ".join(row["scope"].lower() for row in HISTORICAL_EXECUTIONS)
    comparison_classes = " ".join(row["class"] for row in COMPARISON_INPUTS).lower()
    ml_components = {
        "dual-branch-residual-echo-suppressor",
        "cagcrn-joint-aec-and-ns",
        "neural-kalman-filtering-nkf",
        "dtln-aec-128-256-512",
        "deepaec",
        "dual-path-echo-net",
    }
    checks = {
        "paired_synthetic_historical_local": "synthetic_paired" in outcome_classes
        or "paired_synthetic" in comparison_classes,
        "adjacent_aec_pilot_historical_local": "adjacent_aec_pilot" in outcome_classes,
        "predicted_metric_historical_local": "predicted_metric" in outcome_classes
        or "predicted" in scopes,
        "adjacent_non_echo_aware_suppression_historical_local": "non_echo_aware" in outcome_classes,
        "residual_specific_benchmark": "residual_specific" in outcome_classes
        or "residual_specific" in comparison_classes
        or "residual_specific" in labels,
        "clean_near_reference_double_talk": "clean_near_reference" in outcome_classes
        or "clean_near_reference" in comparison_classes,
        "human_listening_result": "listening" in outcome_classes,
        "ml_residual_local_execution": any(
            set(row.get("component_ids", ())) & ml_components for row in HISTORICAL_EXECUTIONS
        ),
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    if EVIDENCE_CLASSES["source_reported_only"] is not any(
        row["class"] == "source_reported" for row in REPORTED_OUTCOMES
    ):
        raise MapError("source-reported class is not backed by a reported outcome")
    if EVIDENCE_CLASSES["target_device_timing"] is not False:
        raise MapError("target-device timing claim is not allowed")
    if EVIDENCE_CLASSES["new_execution_in_this_survey"] is not False:
        raise MapError("new-execution claim is not allowed")
    if EVIDENCE_CLASSES["parity_or_qualification_claim"] is not False:
        raise MapError("parity or qualification claim is not allowed")
    if EVIDENCE_CLASSES["human_listening_result"] is not False:
        raise MapError("human listening result is not backed by a mapped rating record")
    if EVIDENCE_CLASSES["ml_residual_local_execution"] is not False:
        raise MapError("an ML residual-suppressor execution is claimed without one")
    if EVIDENCE_CLASSES["clean_near_reference_double_talk"] is not False:
        raise MapError("a clean near-end double-talk reference is claimed without one")
    non_echo_aware = [row for row in METHOD_FAMILIES if row["family_id"] == "MF-C2"]
    if len(non_echo_aware) != 1 or "adjacent" not in non_echo_aware[0]["family"].lower():
        raise MapError("non-echo-aware suppression is not labelled adjacent")


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
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "residual_boundary": dict(RESIDUAL_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "residual_specific_component_ids": [],
            "residual_specific_weights_present": False,
            "residual_specific_corpus_present": False,
            "note": "Only the optional SpeexDSP postfilter has a component-specific local execution; residual-specific masks, checkpoints, cohorts and runtimes remain undiscovered, and mapped ML rows are considered or blocked.",
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
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if report["residual_boundary"]["residual_specific_candidates_and_weights_discovered"] is not False:
        raise MapError("residual candidate discovery is not closed")
    if report["residual_boundary"]["residual_specific_execution_performed"] is not False:
        raise MapError("residual-specific execution is not closed")
    if report["discovery"]["residual_specific_component_ids"]:
        raise MapError("a residual-specific component is claimed")
    if report["discovery"]["residual_specific_weights_present"] is not False:
        raise MapError("residual-specific weights are claimed")
    if report["discovery"]["residual_specific_corpus_present"] is not False:
        raise MapError("a residual-specific corpus is claimed")
    if EVIDENCE_CLASSES["residual_specific_benchmark"] is not False:
        raise MapError("a residual-specific benchmark is claimed")
    if EVIDENCE_CLASSES["human_listening_result"] is not False:
        raise MapError("a human listening result is claimed")
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
