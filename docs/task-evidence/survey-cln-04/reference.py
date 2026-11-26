# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-04.

This module builds a bounded taxonomy/comparison evidence map for the
dereverberation category (inventory category ``CLN-04``). It reads only pinned,
read-only documents from the enclosing ``audioml`` workspace and the SDK
worktree. It does not load audio, weights, runtimes, media or the network, and
it does not register, expose, enable or qualify any processor.

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
TASK = "SDK-SURVEY-CLN-04"
TITLE = "Review coverage for Dereverberation"
CATEGORY_ID = "CLN-04"
LEGACY_FAMILY = "F03"
BRANCH = "swarm/SDK-SURVEY-CLN-04"
BASE_COMMIT = "711c5c2a419edf258d6858fa90293c5900faad82"
PROFILE = "Room"
COMPONENT = "dereverberation-evidence-map"
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
    "research/dereverberation_candidates_20261028.md": "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary and component-evidence pins. They are
# read only to prove that no public surface was touched and to ground the
# transcribed values; no component is copied, edited or generated here.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/offline-mono-wpe/README.md": "c57df3412bd9e491e5bb4a32b20cf834ecee41da25ce68130d728b48b8877819",
    "docs/task-evidence/offline-multichannel-wpe/README.md": "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/online-mono-wpe-reference/README.md": "81db3b15f99c3662085923227c38fe0c84a9eedd2331094d5c0c89c10eb9f16e",
    "docs/task-evidence/online-multichannel-wpe/README.md": "3615f6fc66d3c8d15a4cd77ccdc1f8a2e5f9c6cd9a1a20b9263814bfb2c34013",
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": "16c7643cc5550cd7358ee48f7dec62eb4045a3384364246cd357269ce0c28da9",
    "docs/task-evidence/srmr-and-reverb-metrics/README.md": "e1fb6ba0828da8550dd826ea5921cb204f0a23c16d004bf38c5009efdace772c",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Dereverberation",
    "scope": "requested",
    "output_kind": "waveform",
    "purpose": "Reduce reverberant smearing.",
    "method_families": {
        "classic": "Delayed linear prediction; weighted prediction error (WPE)",
        "ml": "DNN-supported prediction; nonlinear masks/postfilters and restoration",
    },
    "input_output": "Mono or synchronized microphones \u2192 dereverberated speech",
    "live_or_comparison_boundary": (
        "Reverberation is not playback echo; distinguish offline, block-online "
        "and incremental variants."
    ),
    "source_ids": ["S20", "S31"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "dereverberation_only": True,
    "not_playback_echo_or_aec_category": "CLN-04 boundary",
    "not_generic_denoising_category": "CLN-01 boundary",
    "mono_and_synchronized_multichannel_are_separate": True,
    "offline_block_online_and_incremental_are_separate": True,
    "note": (
        "Reverberation is a room-smearing target, not a playback echo return. "
        "AEC/echo-suppression rows are named only as adjacent controls and are "
        "never pooled into a CLN-04 dereverberation result."
    ),
}

REVERBERATION_BOUNDARY: Dict[str, Any] = {
    "dereverberation_is_not_playback_echo": True,
    "offline_block_online_and_incremental_distinguished": True,
    "mono_and_synchronized_multichannel_separate": True,
    "early_reflection_target_must_be_declared": True,
    "real_room_cohort_staged": False,
    "real_speech_or_listening_result": False,
    "dereverb_weights_staged": False,
    "dereverb_specific_benchmark_result": False,
    "joint_aec_result_pooled_as_dereverb": False,
    "source_reported_results_promoted": False,
    "noncausal_offline_result_used_as_causal_evidence": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S20",
        "title": "NARA-WPE dereverberation implementation",
        "url": "https://github.com/fgnt/nara_wpe",
        "access_scope": "search excerpt",
        "mapped_components": ["nara-wpe-reference-tools"],
        "gap_ids": ["G09"],
        "finding": (
            "Registry access is a search excerpt, not a pinned checkout. The "
            "local WPE implementations follow the delayed-linear-prediction "
            "family, but no NARA-WPE source revision, installation, matched "
            "early-reflection target or executable comparison was found in the "
            "reviewed records."
        ),
    },
    {
        "source_id": "S31",
        "title": "VoiceFixer restoration implementation",
        "url": "https://github.com/haoheliu/voicefixer",
        "access_scope": "search excerpt",
        "mapped_components": ["voicefixer"],
        "gap_ids": ["G09", "G04"],
        "finding": (
            "Registry access is a search excerpt, not a pinned checkout. "
            "VoiceFixer is catalogued as a restoration implementation and is "
            "not a dereverberation-specific model; no checkpoint, revision, "
            "runtime or matched dereverberation cohort is staged in the "
            "reviewed records."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Delayed linear prediction and offline whole-utterance weighted prediction error",
        "components": ["offline-mono-wpe", "offline-multichannel-wpe"],
        "gap_ids": ["G02", "G03"],
        "status": "historical_local_synthetic_and_measured_rir_direct_dominated",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Frame-causal and block-online WPE with stateful recursive updates",
        "components": ["online-mono-wpe-reference", "online-multichannel-wpe"],
        "gap_ids": ["G02", "G03", "G07"],
        "status": "historical_local_synthetic_and_measured_rir_nonpositive_gain",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "NARA-WPE reference delayed-linear-prediction tools (named source lead S20)",
        "components": ["nara-wpe-reference-tools"],
        "gap_ids": ["G09"],
        "status": "catalogued_only_no_local_execution_or_checkout",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Adjacent playback-echo and adaptive-filter boundary (not dereverberation)",
        "components": ["speexdsp-mdf-reference", "speex-mdf-residual-postfilter"],
        "gap_ids": ["G05"],
        "status": "adjacent_aec_boundary_not_pooled_as_dereverb",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "DNN-supported prediction and nonlinear postfilters for dereverberation",
        "components": [
            "2s-dereverb",
            "nemo-schr-dinger-bridge-dereverberation",
            "localvqe-dereverberation-probe",
            "localvqe-compact-full",
        ],
        "gap_ids": ["G04", "G05"],
        "status": "mixed_local_misuse_and_source_reported_no_fair_local_model",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Restoration, flow-matching and generative resynthesis models (named source lead S31)",
        "components": [
            "stream-fm-dereverberation",
            "rose-cd-ears-reverb-configuration",
            "voicefixer",
        ],
        "gap_ids": ["G04", "G08"],
        "status": "source_reported_or_considered_no_staged_weights",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Generic streaming speech enhancer applied as a cross-domain dereverb probe",
        "components": ["gtcrn-streaming-onnx"],
        "gap_ids": ["G04"],
        "status": "historical_local_cross_domain_negative_result",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "offline-mono-wpe", "evidence_status": "evaluated", "task": "SDK-OFFLINE-MONO-WPE"},
    {"component_id": "offline-multichannel-wpe", "evidence_status": "evaluated", "task": "SDK-OFFLINE-MULTICHANNEL-WPE"},
    {"component_id": "online-mono-wpe-reference", "evidence_status": "evaluated", "task": "SDK-ONLINE-MONO-WPE-REFERENCE"},
    {"component_id": "online-multichannel-wpe", "evidence_status": "evaluated", "task": "SDK-ONLINE-MULTICHANNEL-WPE"},
    {"component_id": "nara-wpe-reference-tools", "evidence_status": "considered", "task": "SDK-NARA-WPE-REFERENCE-TOOLS"},
    {"component_id": "speexdsp-mdf-reference", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-MDF-REFERENCE"},
    {"component_id": "speex-mdf-residual-postfilter", "evidence_status": "evaluated", "task": "SDK-SPEEX-MDF-RESIDUAL-POSTFILTER"},
    {"component_id": "2s-dereverb", "evidence_status": "considered", "task": "SDK-2S-DEREVERB"},
    {"component_id": "nemo-schr-dinger-bridge-dereverberation", "evidence_status": "blocked", "task": "SDK-NEMO-SCHR-DINGER-BRIDGE-DEREVERBERATION"},
    {"component_id": "localvqe-dereverberation-probe", "evidence_status": "partial", "task": "SDK-LOCALVQE-DEREVERBERATION-PROBE"},
    {"component_id": "localvqe-compact-full", "evidence_status": "evaluated", "task": "SDK-LOCALVQE-COMPACT-FULL"},
    {"component_id": "stream-fm-dereverberation", "evidence_status": "considered", "task": "SDK-STREAM-FM-DEREVERBERATION"},
    {"component_id": "rose-cd-ears-reverb-configuration", "evidence_status": "source-only", "task": "SDK-ROSE-CD-EARS-REVERB-CONFIGURATION"},
    {"component_id": "voicefixer", "evidence_status": "considered", "task": "SDK-VOICEFIXER"},
    {"component_id": "gtcrn-streaming-onnx", "evidence_status": "partial", "task": "SDK-GTCRN-STREAMING-ONNX"},
    {"component_id": "srmr-and-reverb-metrics", "evidence_status": "considered", "task": "SDK-SRMR-AND-REVERB-METRICS"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Six EARS excerpts convolved with 12 measured SMARD RIRs (72 paired cases) for offline and online mono WPE",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Synthetic convolution with measured direct-dominated RIRs; no captured microphone speech, blind listening or ASR.",
    },
    {
        "id": "CI-2",
        "input": "Six fixed EARS excerpts and three measured SMARD configurations on channels 4X/4Y/4Z (18 paired trials)",
        "class": "historical_local_measured_rir",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Controlled measured-RIR test, not captured array speech; reference and target use channel 4X and remain direct-dominated.",
    },
    {
        "id": "CI-3",
        "input": "Sixteen held-out synthetic speech/room pairs with early-to-late energy controlled to 0 dB and measured RT60 0.45-1.01 s",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Synthetic severe-room stress only; no real room, listening, ASR or device result.",
    },
    {
        "id": "CI-4",
        "input": "Seventy-two paired LocalVQE streaming cases with a zero far-end reference",
        "class": "historical_local_paired_synthetic_misuse",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Outside the model's intended AEC condition; an engineering misuse screen, not a fair joint-AEC or dereverb benchmark.",
    },
    {
        "id": "CI-5",
        "input": "Seventy-two paired GTCRN streaming ONNX cross-domain cases",
        "class": "historical_local_paired_synthetic_cross_domain",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "DNS/VCTK-DEMAND enhancer used as a cross-domain probe; not a dereverberation-trained model and STOI was not measured.",
    },
    {
        "id": "CI-6",
        "input": "Task-local causal online WPE fixture at pinned RT60 250/550/900 ms with noisy and clean-preservation controls",
        "class": "historical_local_paired_synthetic_clean_preservation",
        "source_pin": "docs/task-evidence/online-mono-wpe-reference/README.md",
        "boundary": "Seeded analytic source and synthetic RIRs; no real speech, real room, listening or target-device timing.",
    },
    {
        "id": "CI-7",
        "input": "Task-local analytic source and three synthetic RIRs scored by SRMR and a C50-style early-to-late proxy",
        "class": "historical_local_metric_control",
        "source_pin": "docs/task-evidence/srmr-and-reverb-metrics/README.md",
        "boundary": "Complementary non-intrusive metric control; never a selection criterion alone and not a human quality score.",
    },
    {
        "id": "CI-8",
        "input": "Model-card and paper results for NeMo, ROSE-CD, Stream.FM and SB-UFOGen",
        "class": "source_reported_only",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "No local runtime, exact checkpoint, matched cohort or numeric parity follows from a reported score.",
    },
    {
        "id": "CI-9",
        "input": "Rights-qualified real-room or standard REVERB-style paired cohort with clean reference",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Not staged: WSJ/REVERB access and SMARD terms are unresolved, and no captured microphone-speech cohort exists here.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity / no-processing", "role": "Mandatory paired baseline; identity remained the best measured CPU choice on direct-dominated rooms.", "source_pin": "research/dereverberation_candidates_20261028.md"},
    {"id": "CT-2", "name": "noisy identity", "role": "Paired noisy-input baseline for the task-local synthetic WPE fixture.", "source_pin": "docs/task-evidence/online-mono-wpe-reference/README.md"},
    {"id": "CT-3", "name": "declared early-reflection target", "role": "Direct response plus 50 ms after the direct peak; an engineering convention, not a perceptual optimum.", "source_pin": "research/dereverberation_candidates_20261028.md"},
    {"id": "CT-4", "name": "noncausal offline WPE upper-bound control", "role": "Whole-clip prediction uses future frames and is never evidence for a causal implementation.", "source_pin": "docs/task-evidence/offline-mono-wpe/README.md"},
    {"id": "CT-5", "name": "SRMR and C50-style early-to-late proxy", "role": "Complementary non-intrusive reverberation control, not a standalone selection score.", "source_pin": "docs/task-evidence/srmr-and-reverb-metrics/README.md"},
    {"id": "CT-6", "name": "clean-source preservation control", "role": "Synthetic clean-reference preservation; no real-speech listening or human rating is mapped.", "source_pin": "docs/task-evidence/online-mono-wpe-reference/README.md"},
    {"id": "CT-7", "name": "adjacent playback-echo / AEC boundary", "role": "Speex MDF and residual-postfilter rows are echo-cancellation controls only and are never pooled into a dereverb result.", "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "EARS 743-recording blind archive and synthetic excerpts used in the WPE screens",
        "class": "research_audio",
        "status": "CC BY-NC 4.0; split/provenance bundle absent; bytes not staged or verified in this task",
        "source_pin": "research/dereverberation_candidates_20261028.md",
    },
    {
        "asset": "SMARD estimated RIRs for configurations 0000/1000/2000 and the single microphone",
        "class": "measured_rir",
        "status": "Local research only; upstream terms unclear and no redistribution right is asserted",
        "source_pin": "research/dereverberation_candidates_20261028.md",
    },
    {
        "asset": "REVERB Challenge and WSJ simulated/real material",
        "class": "external_corpus",
        "status": "Not staged; WSJ corpora require LDC access and no rights transfer is created here",
        "source_pin": "research/dereverberation_candidates_20261028.md",
    },
    {
        "asset": "NeMo, ROSE-CD, Stream.FM, 2S-Dereverb and VoiceFixer checkpoints",
        "class": "research_model_assets",
        "status": "No weights staged; licenses include CC BY-NC-SA 4.0, AGPL-3.0 and unresolved per-checkpoint terms",
        "source_pin": "research/dereverberation_candidates_20261028.md",
    },
    {
        "asset": "SRMRpy and Gammatone pinned scorer archives",
        "class": "metric_scorer",
        "status": "Provenance and archive digests recorded in the cited evidence; runtime is a stdlib port and no download occurs here",
        "source_pin": "docs/task-evidence/srmr-and-reverb-metrics/README.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Offline and online mono WPE 72-case synthetic EARS/SMARD screen",
        "outcome_class": "historical_local_synthetic",
        "component_ids": ["offline-mono-wpe", "online-mono-wpe-reference"],
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "values": {
            "paired_cases": 72,
            "identity_median_si_sdr_db": 16.49,
            "identity_median_stoi": 0.9853,
            "offline_median_si_sdr_db": 13.35,
            "offline_median_stoi": 0.9699,
            "offline_median_rtf": 0.0089,
            "offline_si_sdr_wins": 2,
            "offline_stoi_wins": 0,
            "online_median_si_sdr_db": 12.28,
            "online_median_stoi": 0.9760,
            "online_median_rtf": 0.2604,
            "online_rtf_p90": 0.267,
            "online_rtf_max": 0.318,
            "online_si_sdr_wins": 1,
            "online_stoi_wins": 0,
            "estimated_algorithmic_delay_ms": 80,
            "rir_early_to_late_ratio_min_db": 17.66,
            "rir_early_to_late_ratio_max_db": 22.78,
        },
        "scope": "Six EARS excerpts convolved with 12 measured SMARD RIRs; direct-dominated rooms, one early-reflection definition; no real-room or listening result; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Measured-SMARD mono and three-channel WPE screen",
        "outcome_class": "historical_local_measured_rir",
        "component_ids": ["offline-multichannel-wpe", "online-multichannel-wpe"],
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "values": {
            "paired_trials": 18,
            "identity_median_si_sdr_db": 18.390,
            "identity_median_stoi": 0.99052,
            "mono_online_median_si_sdr_db": 18.431,
            "mono_online_median_stoi": 0.99052,
            "mono_online_median_rtf": 0.0345,
            "mono_online_si_sdr_wins": 15,
            "mono_online_stoi_wins": 15,
            "three_channel_online_median_si_sdr_db": 18.443,
            "three_channel_online_median_stoi": 0.99052,
            "three_channel_online_median_rtf": 0.0440,
            "three_channel_online_si_sdr_wins": 15,
            "three_channel_online_stoi_wins": 13,
            "mono_offline_median_si_sdr_db": 13.582,
            "mono_offline_median_stoi": 0.96829,
            "mono_offline_median_rtf": 0.0205,
            "three_channel_offline_median_si_sdr_db": 12.762,
            "three_channel_offline_median_stoi": 0.96548,
            "three_channel_offline_median_rtf": 0.0269,
        },
        "scope": "Channels 4X/4Y/4Z across three measured SMARD configurations; controlled measured-RIR test, not captured array speech; gains effectively zero; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Severe synthetic-room online WPE stress screen",
        "outcome_class": "historical_local_synthetic",
        "component_ids": ["online-mono-wpe-reference"],
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "values": {
            "paired_pairs": 16,
            "identity_median_stoi": 0.597,
            "default_wpe_median_stoi": 0.619,
            "default_stoi_wins": 16,
            "identity_median_si_sdr_db": 2.41,
            "default_wpe_median_si_sdr_db": 0.74,
            "default_si_sdr_wins": 0,
            "tuned_wpe_median_si_sdr_db": 1.26,
            "tuned_wpe_median_stoi": 0.608,
            "tuned_si_sdr_wins": 0,
            "measured_rt60_min_s": 0.45,
            "measured_rt60_max_s": 1.01,
        },
        "scope": "Early-to-late energy controlled to 0 dB; synthetic severe-room metric tradeoff only; not overall superiority and not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "LocalVQE zero-far-end streaming misuse screen",
        "outcome_class": "historical_local_synthetic_misuse",
        "component_ids": ["localvqe-dereverberation-probe", "localvqe-compact-full"],
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "values": {
            "paired_cases": 72,
            "identity_median_si_sdr_db": 16.49,
            "identity_median_stoi": 0.9853,
            "localvqe_median_si_sdr_db": -0.99,
            "localvqe_median_stoi": 0.6389,
            "localvqe_si_sdr_wins": 0,
            "localvqe_stoi_wins": 0,
            "localvqe_median_rtf": 0.0649,
            "localvqe_rtf_p90": 0.0671,
            "localvqe_rtf_max": 0.0759,
            "measured_output_delay_samples": 256,
            "measured_output_delay_ms": 16,
        },
        "scope": "LocalVQE source revision 7f61cd0 and pinned model hash; zero far-end reference is outside intended AEC use; engineering misuse screen, not a fair model benchmark; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "GTCRN streaming ONNX cross-domain dereverb probe",
        "outcome_class": "historical_local_synthetic_cross_domain",
        "component_ids": ["gtcrn-streaming-onnx"],
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "values": {
            "paired_cases": 72,
            "identity_median_si_sdr_db": 16.49,
            "gtcrn_median_si_sdr_db": 5.66,
            "gtcrn_si_sdr_wins": 0,
            "gtcrn_median_rtf": 0.0459,
            "gtcrn_rtf_p90": 0.0489,
            "gtcrn_rtf_max": 0.0723,
            "frame_kernel_median_ms": 0.71,
            "frame_kernel_p95_ms": 1.38,
            "frame_kernel_p99_ms": 5.36,
            "estimated_stft_lookahead_ms": 16,
        },
        "scope": "DNS speech-enhancement ONNX model used cross-domain; STOI not measured; negative evidence against a generic enhancer, not a dereverb-trained model verdict; not rerun by this survey.",
    },
    {
        "id": "HE-6",
        "label": "Causal online WPE synthetic fixture with clean-preservation control",
        "outcome_class": "historical_local_synthetic_clean_preservation",
        "component_ids": ["online-mono-wpe-reference"],
        "source_pin": "docs/task-evidence/online-mono-wpe-reference/README.md",
        "values": {
            "rooms": 3,
            "short_rt60_identity_si_sdr_db": 17.180000,
            "short_rt60_wpe_si_sdr_db": 9.247946,
            "short_rt60_delta_si_sdr_db": -7.895549,
            "medium_rt60_identity_si_sdr_db": 5.695038,
            "medium_rt60_wpe_si_sdr_db": 5.369194,
            "medium_rt60_delta_si_sdr_db": -0.275546,
            "long_rt60_identity_si_sdr_db": 0.317238,
            "long_rt60_wpe_si_sdr_db": 0.367169,
            "long_rt60_delta_si_sdr_db": 0.105803,
            "short_rt60_identity_stoi": 0.993442,
            "short_rt60_wpe_stoi": 0.968823,
            "medium_rt60_identity_stoi": 0.925421,
            "medium_rt60_wpe_stoi": 0.906599,
            "long_rt60_identity_stoi": 0.802410,
            "long_rt60_wpe_stoi": 0.798267,
            "clean_preservation_si_sdr_db": 11.071693,
            "clean_preservation_stoi": 0.977112,
            "content_delay_samples": 480,
            "content_delay_ms": 30,
            "output_duration_samples": 25600,
            "partial_final_frame_samples": 5157,
            "measured_early_to_late_ratios_db": [20.465145, 11.506049, 4.749543],
        },
        "scope": "Seeded analytic vowel-like source and synthetic RIRs at pinned RT60/D-R; identity and clean-preservation controls; no real speech or room; not rerun by this survey.",
    },
    {
        "id": "HE-7",
        "label": "SRMR and C50-style reverb metric control fixture",
        "outcome_class": "historical_local_metric_control",
        "component_ids": ["srmr-and-reverb-metrics"],
        "source_pin": "docs/task-evidence/srmr-and-reverb-metrics/README.md",
        "values": {
            "synthetic_rooms": 3,
            "short_rt60_ms": 250,
            "medium_rt60_ms": 550,
            "long_rt60_ms": 900,
            "short_c50_proxy_db": 15.872107323614,
            "medium_c50_proxy_db": 7.379982952271,
            "long_c50_proxy_db": 3.502427779020,
            "short_full_rir_srmr": 8.841079147552,
            "medium_full_rir_srmr": 5.875231208862,
            "long_full_rir_srmr": 3.925665600942,
            "short_early_target_srmr": 11.391122657889,
            "medium_early_target_srmr": 15.087643725732,
            "long_early_target_srmr": 8.175056584125,
            "dry_source_srmr": 5.937336690169,
            "max_upstream_crosscheck_delta": 1.1546e-14,
            "crosscheck_tolerance": 1e-9,
        },
        "scope": "Analytic synthetic source and synthetic RIRs; metric control only, not a dereverb output score or selection result; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "NARA-WPE project provides a dereverberation implementation in the delayed-linear-prediction family",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt source scope; no pinned checkout, local NARA run or matched early-reflection comparison is created here.",
    },
    {
        "id": "RO-2",
        "claim": "VoiceFixer provides a restoration implementation relevant to degraded speech",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt source scope; it is not a dereverberation-specific model and no checkpoint or local dereverb run is staged here.",
    },
    {
        "id": "RO-3",
        "claim": "NeMo se_der_sb_16k_small model card reports PESQ 2.79, ESTOI .89, SI-SDR 7.4 dB and WER 4.27%",
        "class": "source_reported",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Utterance-level V100 model card on WSJ0-Reverb, CC BY-NC-SA 4.0; weights and PyTorch/NeMo are missing locally.",
    },
    {
        "id": "RO-4",
        "claim": "ROSE-CD upstream reports EARS-Reverb PESQ 2.69, ESTOI .82 and WER 15.78%",
        "class": "source_reported_cross_domain",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Upstream cross-domain values are not from the local VoiceBank-DEMAND checkpoint; the local CPU screen was too slow to qualify.",
    },
    {
        "id": "RO-5",
        "claim": "Stream.FM paper reports EARS-Reverb PESQ 1.32 to 2.05, ESTOI .58 to .79 and SI-SDR -16.6 to -13.5 dB at 32 ms algorithmic / 48 ms total latency",
        "class": "source_reported",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Paper and public checkpoint lead only (AGPL-3.0, 27.9M parameters); no local hardware check or staged model is claimed here.",
    },
    {
        "id": "RO-6",
        "claim": "SB-UFOGen one-step EARS-Reverb results report PESQ 3.36, SI-SDR 8.73 dB, ESTOI .88 and MOS Reverb 4.71",
        "class": "source_reported",
        "source_pin": "research/dereverberation_candidates_20261028.md",
        "boundary": "Paper result measured on an RTX A6000; no verified official checkpoint or causal streaming implementation exists locally.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "frozen_rir_or_render_reference": "CI-1 / CI-2 / CI-3 / CI-6; measured SMARD RIRs and seeded synthetic RIRs with a declared 50 ms early-reflection target",
        "channel_rate_hop_excitation_delay": "CI-1 / CI-2 / CI-6; mono and three-channel 16 kHz fixtures with stated hop and 80 ms predictor delay or 30 ms content delay",
        "movement_noise_reset_schedule": "CI-6; synthetic movement, noisy-identity and reset controls, no real room",
        "identity_control": "CT-1 / CT-2; identity remained best on direct-dominated measured rooms",
        "echo_only_near_end_overlap_no_reference": "CT-7; only an adjacent AEC boundary is named; no CLN-04 echo/near-end/overlap case is executed",
        "paired_objective_scores": "HE-1..HE-6; transcribed SI-SDR/STOI values, not rerun here",
        "clean_preservation": "CT-6 / HE-6; synthetic clean-source preservation only, no real-speech or listening result",
        "peaks_and_invalid_outputs": "HE-6 finiteness/peak checks and adverse controls; no new real-room invalid-output study",
        "nonfinite_failures_and_alignment": "HE-1..HE-6; reported alignment and finite-output context, not device measurements",
        "unpaired_predictive_screen": "No CLN-04-specific predictive score in reviewed records",
        "metric_control": "CT-5 / HE-7; SRMR and C50-style proxy are complementary only",
        "listening": "No dereverb listening items, ratings or playback clearance",
        "alignment_state_memory_timing": "HE-1 / HE-6 offline transform or synthetic causal RTF; no target-device timing, memory or deadlines",
        "delayed_or_missing_render": "Not applicable to a no-playback-reference dereverb fixture; remains an AEC-scope gate",
    },
    "blocked": [
        "Rights-qualified real-room or standard paired cohort with frozen RIR provenance and clean reference",
        "Declared early-reflection target plus clean-preservation and independent listening protocol",
        "Target-device causal/streaming timing, memory, content delay, state reset/tail and deadline evidence",
        "Task-matched external baseline under a locked runtime with offline/block-online/incremental variants separated",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Exact approved reference parity at frozen revision and settings",
        "Release approval; DEFER remains in force until every gate is closed",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "measured_rir_historical_local": True,
    "metric_control_historical_local": True,
    "clean_preservation_diagnostic_historical_local": True,
    "unpaired_predictive_historical_local": False,
    "prepared_listening_without_ratings": False,
    "human_listening_result": False,
    "vendor_or_source_reported": True,
    "real_room_or_standard_cohort": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified real-room or standard paired dereverberation cohort with clean reference",
        "evidence_gap": "The screen uses an EARS blind archive plus measured SMARD RIRs; no real captured microphone-speech cohort or REVERB-style paired set is staged, and SMARD terms remain unclear.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-04 feasibility row was found for a real-room cohort; the linked research-control and foundation rows own cohort and evidence rules, not a dereverb capability.",
    },
    {
        "id": "G02",
        "actionable_gap": "Compare offline, block-online and incremental WPE under one frozen early-reflection target",
        "evidence_gap": "Offline WPE is noncausal, online WPE uses future-free recursive updates, and no block-online or incremental variant has a matched local result on the same cohort and target definition.",
        "follow_up_ids": [
            "SDK-NARA-WPE-REFERENCE-TOOLS",
            "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "NARA-WPE reference tools are a bounded feasibility lead for a matched delayed-linear-prediction comparison; the research-control row owns frozen controls. No processor is enabled.",
    },
    {
        "id": "G03",
        "actionable_gap": "Evaluate measured multichannel and array dereverberation beyond direct-dominated three-channel SMARD trials",
        "evidence_gap": "Only 18 controlled SMARD trials on channels 4X/4Y/4Z exist; gains over identity were effectively zero, and no captured array speech, geometry sweep or microphone mismatch case is mapped.",
        "follow_up_ids": [
            "SDK-2S-DEREVERB",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "2S-Dereverb is a conditional multi-microphone feasibility lead, not an implemented or enabled CLN-04 component; the research-control row owns cohort metadata.",
    },
    {
        "id": "G04",
        "actionable_gap": "Evaluate a dereverberation-trained DNN or nonlinear postfilter with a pinned checkpoint and rights",
        "evidence_gap": "NeMo is blocked, 2S-Dereverb is considered, Stream.FM and ROSE-CD are source-reported or cross-domain, VoiceFixer is a generic restoration lead, and LocalVQE was run outside its intended AEC condition.",
        "follow_up_ids": [
            "SDK-2S-DEREVERB",
            "SDK-STREAM-FM-DEREVERBERATION",
            "SDK-NEMO-SCHR-DINGER-BRIDGE-DEREVERBERATION",
            "SDK-ROSE-CD-EARS-REVERB-CONFIGURATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked rows are bounded feasibility leads, not enabled processors, staged weights or a dereverb quality claim.",
    },
    {
        "id": "G05",
        "actionable_gap": "Separate dereverberation from playback-echo cancellation and joint AEC evidence",
        "evidence_gap": "LocalVQE was evaluated with a zero far-end reference, Speex MDF rows are AEC controls, and no paired-reference echo/near-end/overlap case exists for a dereverb claim.",
        "follow_up_ids": [
            "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-04 feasibility row owns the echo/dereverb split; the research-control and foundation rows own preservation and evidence rules.",
    },
    {
        "id": "G06",
        "actionable_gap": "Collect independent listening, ASR and non-intrusive metric evidence under a fixed protocol",
        "evidence_gap": "There is no blind listening, ASR or live-microphone test; SRMR is a synthetic complementary control and no human rating or transcript-normalized result is mapped.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-SRMR-AND-REVERB-METRICS",
            "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-04 listening feasibility row was found; the linked research-control rows own preservation, metric and control design, not a listening result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure target-device causal streaming timing, content delay, state reset, tail and deadlines",
        "evidence_gap": "Only offline transform RTF, batch RTF and a synthetic causal-kernel RTF are documented; no callback-path, memory, warm-up or end-of-stream measurement exists for dereverberation.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-04 timing feasibility row was found; the foundation rows own lifecycle, acceptance and timing-evidence rules.",
    },
    {
        "id": "G08",
        "actionable_gap": "Secure rights-qualified dereverb weights and data with per-asset provenance",
        "evidence_gap": "EARS is CC BY-NC, SMARD terms are unclear, NeMo is CC BY-NC-SA, Stream.FM is AGPL-3.0, and no checkpoint or corpus is staged in this task.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-STREAM-FM-DEREVERBERATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The evidence-manifest control owns rights metadata, while the Stream.FM feasibility row is a candidate-discovery lead; neither grants rights or stages assets.",
    },
    {
        "id": "G09",
        "actionable_gap": "Resolve the S20 and S31 source leads to exact revisions and executable comparisons",
        "evidence_gap": "Both leads are search excerpts; NARA-WPE has no pinned checkout and VoiceFixer is a generic restoration model with no dereverb-specific checkpoint or run.",
        "follow_up_ids": [
            "SDK-NARA-WPE-REFERENCE-TOOLS",
            "SDK-VOICEFIXER",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are source-resolution leads only; no NARA-WPE or VoiceFixer component is installed, enabled or promoted by this map.",
    },
    {
        "id": "G10",
        "actionable_gap": "Calibrate the early-reflection target convention and non-intrusive metrics against reference conditions",
        "evidence_gap": "The 50 ms target is an engineering convention, SRMR/C50 are synthetic complementary controls, and no perceptual optimum or reference calibration is established.",
        "follow_up_ids": [
            "SDK-SRMR-AND-REVERB-METRICS",
            "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-04 target-definition feasibility row was found; the linked research-control rows own metric and control calibration, not a perceptual optimum.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-NARA-WPE-REFERENCE-TOOLS", "title": "NARA-WPE reference tools", "mode": "feasibility"},
    {"task_id": "SDK-2S-DEREVERB", "title": "2S-Dereverb", "mode": "feasibility"},
    {"task_id": "SDK-STREAM-FM-DEREVERBERATION", "title": "Stream.FM dereverberation", "mode": "feasibility"},
    {"task_id": "SDK-NEMO-SCHR-DINGER-BRIDGE-DEREVERBERATION", "title": "NeMo Schr\u00f6dinger-bridge dereverberation", "mode": "feasibility"},
    {"task_id": "SDK-ROSE-CD-EARS-REVERB-CONFIGURATION", "title": "ROSE-CD EARS-Reverb configuration", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFIXER", "title": "VoiceFixer", "mode": "feasibility"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS", "title": "CCF AATC unified restoration controls", "mode": "research-control"},
    {"task_id": "SDK-SRMR-AND-REVERB-METRICS", "title": "SRMR and REVERB metrics", "mode": "research-control"},
    {"task_id": "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION", "title": "ERLE and double-talk preservation", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified real-room or standard paired cohort with frozen RIR provenance, clean reference and declared early-reflection target"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent authorized listening with declared perceived-reverberation and clean-preservation analysis"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device causal/streaming timing, memory, content delay, state reset/tail and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched external baseline under a locked runtime with offline, block-online and incremental variants separated"},
    {"id": "RG-05", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-07", "blocked": True, "requirement": "Exact approved reference parity at frozen revision and settings"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-04 — Dereverberation** | Reduce reverberant smearing. Scope: requested.",
        "Reverberation is not playback echo; distinguish offline, block-online and incremental variants.",
    ],
    "research/category_survey/sources.md": [
        "| S20 | [NARA-WPE dereverberation implementation](https://github.com/fgnt/nara_wpe) | acoustics | search excerpt |",
        "| S31 | [VoiceFixer restoration implementation](https://github.com/haoheliu/voicefixer) | acoustics | search excerpt |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Room | Freeze render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise and reset schedule.",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| Online single-channel WPE | Dereverberation | Stateful frame-causal implementation. On measured SMARD RIRs, median RTF 0.260, estimated 80 ms algorithmic delay, but negligible gains over identity; stronger synthetic reverberation produced mixed STOI/SI-SDR tradeoffs. |",
        "| GTCRN streaming ONNX | Streaming speech enhancement / cross-domain dereverb probe | Stateful spectrum-frame path, median RTF 0.0459, estimated 16 ms STFT lookahead. Local dereverb screen lost to identity, so do not treat it as a selected dereverberator. |",
    ],
    "research/dereverberation_candidates_20261028.md": [
        "| Identity | 16.49 dB | .9853 | — | — |",
        "| Offline WPE | 13.35 dB | .9699 | .0089 | 2 / 0 |",
        "| Online WPE | 12.28 dB | .9760 | .2604 | 1 / 0 |",
        "| Three-channel online WPE | 18.443 dB | .99052 | .0440 | 15 | 13 |",
        "On 16 held-out speech/room pairs, default online WPE raised median STOI from .597 to .619 (16/16 wins) but lowered median SI-SDR from 2.41 to 0.74 dB (0/16 wins).",
        "LocalVQE scored median SI-SDR −0.99 dB and STOI .6389",
        "median SI-SDR 5.66 dB versus 16.49 dB for identity, winning 0/72 pairs",
        "The reported timing is the causal-kernel RTF, not an end-to-end streaming audio-pipeline measurement.",
        "**Best measured CPU choice: identity for direct-dominated rooms.**",
        "no blind listening, ASR, SRMR, or live-microphone test",
        "Model card reports SDE: PESQ 2.79",
        "upstream reports an EARS-Reverb dereverberation comparison (PESQ 2.69",
        "input PESQ 1.32 / ESTOI .58 / SI-SDR −16.6 dB",
        "PESQ 3.36 / SI-SDR 8.73 dB / ESTOI .88 / MOS Reverb 4.71",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/offline-mono-wpe/README.md": [
        "**Whole-clip WPE is noncausal**",
    ],
    "docs/task-evidence/offline-multichannel-wpe/README.md": [
        "**Status: `proposal_only_not_qualified` · completeness `incomplete` · decision `DEFER`.**",
    ],
    "docs/task-evidence/online-multichannel-wpe/README.md": [
        "**frame-causal**: each emitted 160-sample mono frame is computed from the",
    ],
    "docs/task-evidence/online-mono-wpe-reference/README.md": [
        "Clean-source preservation is explicit: identity is bit-exact (STOI `1.0`,",
        "SI-SDR `11.071693` dB and STOI `0.977112` against the aligned clean source.",
        "frozen v0 behavior and main are unchanged. No real room impulse, device,",
        "content delay is 480 samples (30 ms)",
    ],
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": [
        "A **paired synthetic reference tool**, not an AEC, double-talk, quality, device,",
    ],
    "docs/task-evidence/srmr-and-reverb-metrics/README.md": [
        "SRMR is reported as **complementary, non-intrusive dereverb evidence** alongside",
        "Dry-source control SRMR: `5.937336690169`.",
        "Two upstream cross-checks on the",
        "pinned synthetic cohort agree with a maximum absolute delta of `1.1546e-14` against a",
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
    "real_reverb_audio": False,
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
    "dereverb_claim_without_room_execution": "rejected; state unchanged",
    "playback_echo_pooled_as_dereverb": "rejected; state unchanged",
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
    if BOARD_PATH in SOURCE_PINS or BOARD_PATH in WORKTREE_PINS:
        raise MapError("mutable board file is pinned")
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
        raise MapError("CLN-04 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-04 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F03 / CLN-04 is not unique")
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
            raise MapError("legacy backlog mismatch: F03/CLN-04/%s" % key)


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
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
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
    text = " ".join(comparison + labels)
    checks = {
        "paired_synthetic_historical_local": "paired_synthetic" in text,
        "measured_rir_historical_local": "measured_rir" in text,
        "metric_control_historical_local": "metric_control" in text,
        "clean_preservation_diagnostic_historical_local": "clean_preservation" in text,
        "unpaired_predictive_historical_local": "predictive" in text,
        "prepared_listening_without_ratings": "prepared_listening" in text,
        "vendor_or_source_reported": "source_reported" in text,
        "real_room_or_standard_cohort": "real_room_cohort" in text,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    if EVIDENCE_CLASSES["human_listening_result"] is not False:
        raise MapError("human listening result is not backed by a mapped rating record")
    if EVIDENCE_CLASSES["new_execution_in_this_survey"] is not False:
        raise MapError("new-execution claim is not allowed")
    if EVIDENCE_CLASSES["parity_or_qualification_claim"] is not False:
        raise MapError("parity or qualification claim is not allowed")


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
        "qualification_status": QUALIFICATION_STATUS,
        "readiness": READINESS,
        "decision": DECISION,
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "reverberation_boundary": dict(REVERBERATION_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "dereverb_model_weights_staged": False,
            "real_room_corpus_staged": False,
            "real_speech_staged": False,
            "note": "Local WPE implementations exist, but rights-qualified real-room dereverb evidence and model weights remain absent.",
        },
        "legacy_backlog": {
            "family_id": LEGACY_FAMILY,
            "activation_state": "catalogued",
            "state": "catalogued",
            "scope": "requested",
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
    if report["reverberation_boundary"]["real_room_cohort_staged"] is not False:
        raise MapError("a real-room cohort is claimed")
    if report["reverberation_boundary"]["dereverb_weights_staged"] is not False:
        raise MapError("dereverb weights are claimed")
    if report["reverberation_boundary"]["joint_aec_result_pooled_as_dereverb"] is not False:
        raise MapError("playback echo is pooled as dereverberation")
    if report["discovery"]["dereverb_model_weights_staged"] is not False:
        raise MapError("dereverb weights are staged")
    if report["discovery"]["real_room_corpus_staged"] is not False:
        raise MapError("real-room corpus is staged")
    if BOARD_PATH in report["source_pins"] or BOARD_PATH in report["boundary_pins"]:
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
