# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-SPK-01.

This module builds a bounded taxonomy/comparison evidence map for the generic
speech/source separation category (inventory category ``SPK-01``). It reads
only pinned, read-only documents from the enclosing ``audioml`` workspace and
the SDK worktree. It does not load audio, weights, codecs, runtimes, media or
the network, and it does not register, expose, enable or qualify any
processor.

All curated records below are documentation mappings, not new measurements.
Adjacent historical local or source-reported values are transcribed verbatim
from the pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-SPK-01"
TITLE = "Review coverage for Generic speech/source separation"
CATEGORY_ID = "SPK-01"
LEGACY_FAMILY = "F05"
BRANCH = "swarm/SDK-SURVEY-SPK-01"
BASE_COMMIT = "3ba7466f644111318a71693900e4262e25b92176"
PROFILE = "Spatial"
COMPONENT = "generic-speech-source-separation-evidence-map"
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
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md": "d9285694209a54b26db0aa89a27a11b004fa0159d7ee08fc5fff0728c0869545",
    "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md": "b7a1e214d0fa402c971e39a4742d54589ce5bd25bd3de4a5bc72be843ec997f4",
    "research/voice-enhancement-20261101/agent-sepformer-result-audit/REPORT.md": "dca9253460fb95c6085433e0508504cc9c7b8e7db15676af85e7008e74260177",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md": "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/evaluation_records.md": "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/hush/README.md": "0426a592204381138e7fa7ba04f37f4aff92eee6ac75b6bda31f0861c485e76f",
    "docs/task-evidence/survey-cln-01/README.md": "3dbdf88a57e7d3836d9327f0a79eccf7b9b24b70273c4a42eb6701e631d81237",
    "docs/task-evidence/survey-det-03/README.md": "672e7a380230f4a1e13e88404deb92b052052bdb05b029a67672fe655ff9593e",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Speakers and separation",
    "name": "Generic speech/source separation",
    "scope": "requested",
    "output_kind": "waveform",
    "purpose": "Recover multiple sources from a mixture.",
    "method_families": {
        "classic": "Statistical/source-factorization families; candidates to enumerate",
        "ml": "Time-frequency masking; learned time-domain encoder/mask/decoder",
    },
    "input_output": "Mixture \u2192 multiple source estimates",
    "live_or_comparison_boundary": (
        "Source order, continuity and source count require handling; "
        "separation does not decide which sources to keep."
    ),
    "source_ids": ["S08"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S08",
        "title": "Conv-TasNet paper",
        "url": "https://arxiv.org/abs/1809.07454",
        "access_scope": "direct",
        "researcher": "analysis",
        "mapped_components": [
            "conv-tasnet",
            "beam-tasnet-beam-guided-tasnet",
        ],
        "gap_ids": ["G01", "G05"],
        "finding": (
            "The named source lead is the Conv-TasNet paper: a learned "
            "time-domain encoder, mask and decoder trained with permutation-"
            "invariant separation objectives. It defines the ML method family "
            "and the need to score source permutation, but no exact code "
            "revision, checkpoint, two- or three-source cohort or local "
            "separation run exists in the reviewed records. Its multichannel "
            "descendants remain separate blocked candidates."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Statistical/source-factorization families (independent component analysis and multichannel iterative source modelling)",
        "components": ["auxiva", "h-gtcrn"],
        "gap_ids": ["G02"],
        "status": "candidate_considered_no_local_separation_execution",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Spatial filtering, beamforming and localization boundary (not a generic waveform separator)",
        "components": [
            "delay-and-sum-beamformer",
            "mvdr-beamforming",
            "source-localization-direction-of-arrival",
        ],
        "gap_ids": ["G05"],
        "status": "adjacent_spatial_boundary_not_spk01_separation",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Speaker segmentation, diarization and embedding boundary (annotation or identity, not multi-source waveforms)",
        "components": [
            "pyannote-diarization",
            "bayesian-information-criterion-speaker-segmentation",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G07"],
        "status": "adjacent_spk03_to_spk05_boundary_not_separation",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Learned time-domain encoder/mask/decoder separation (Conv-TasNet, S08)",
        "components": ["conv-tasnet"],
        "gap_ids": ["G01"],
        "status": "source_documented_candidate_not_staged_or_run",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Time-frequency masking and dual-path transformer boundary, represented locally by a single-output DNS4 enhancer (SpeechBrain SepFormer DNS4)",
        "components": ["speechbrain-sepformer-dns4"],
        "gap_ids": ["G08"],
        "status": "adjacent_single_output_enhancement_not_multi_source_separation",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Multichannel or beam-guided neural separation and neural beamforming (Beam-TasNet, SpatialNet, neural beamforming)",
        "components": [
            "beam-tasnet-beam-guided-tasnet",
            "spatialnet",
            "neural-beamforming",
        ],
        "gap_ids": ["G05"],
        "status": "blocked_no_staged_weights_or_synchronised_array_data",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Speaker-conditioned extraction and personal VAD boundary (SPK-02, not generic separation)",
        "components": [
            "target-speaker-extraction-family",
            "voicefilter",
            "voicefilter-lite-personal-vad",
        ],
        "gap_ids": ["G06"],
        "status": "adjacent_spk02_candidates_blocked_not_generic_separation",
    },
    {
        "family_id": "MF-M5",
        "branch": "ml-adjacent",
        "family": "Single-channel competing-speaker suppression (Hush), evaluated only as primary/background attenuation",
        "components": ["hush"],
        "gap_ids": ["G08"],
        "status": "adjacent_partially_evaluated_suppression_not_separation",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "conv-tasnet", "evidence_status": "considered", "task": "SDK-CONV-TASNET"},
    {"component_id": "auxiva", "evidence_status": "considered", "task": "SDK-AUXIVA"},
    {"component_id": "h-gtcrn", "evidence_status": "considered", "task": "SDK-H-GTCRN"},
    {"component_id": "speechbrain-sepformer-dns4", "evidence_status": "evaluated", "task": "SDK-SPEECHBRAIN-SEPFORMER-DNS4"},
    {"component_id": "hush", "evidence_status": "partial", "task": "SDK-HUSH"},
    {"component_id": "beam-tasnet-beam-guided-tasnet", "evidence_status": "blocked", "task": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET"},
    {"component_id": "spatialnet", "evidence_status": "blocked", "task": "SDK-SPATIALNET"},
    {"component_id": "neural-beamforming", "evidence_status": "blocked", "task": "SDK-NEURAL-BEAMFORMING"},
    {"component_id": "target-speaker-extraction-family", "evidence_status": "blocked", "task": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"},
    {"component_id": "voicefilter", "evidence_status": "blocked", "task": "SDK-VOICEFILTER"},
    {"component_id": "voicefilter-lite-personal-vad", "evidence_status": "blocked", "task": "SDK-VOICEFILTER-LITE-PERSONAL-VAD"},
    {"component_id": "delay-and-sum-beamformer", "evidence_status": "considered", "task": "SDK-DELAY-AND-SUM-BEAMFORMER"},
    {"component_id": "mvdr-beamforming", "evidence_status": "considered", "task": "SDK-MVDR-BEAMFORMING"},
    {"component_id": "source-localization-direction-of-arrival", "evidence_status": "considered", "task": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"},
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "bayesian-information-criterion-speaker-segmentation", "evidence_status": "considered", "task": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Conv-TasNet learned time-domain encoder/mask/decoder protocol with permutation-invariant separation objective (named source lead S08)",
        "class": "source_documented_candidate_not_staged_or_run",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Paper-level method definition only; no pinned code revision, checkpoint, two/three-source cohort, source-count policy or local output exists.",
    },
    {
        "id": "CI-2",
        "input": "SpeechBrain SepFormer DNS4 offline single-output enhancement screen on 30 paired DNS2020 files plus 30 clean diagnostics",
        "class": "adjacent_single_output_enhancement_historical_local",
        "source_pin": "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md",
        "boundary": "A dual-path name is not a source separator here: the pinned model exposes one output stream and whole-utterance inference. It is adjacent enhancement evidence, not SPK-01 separation.",
    },
    {
        "id": "CI-3",
        "input": "Hush primary/background suppression on 30 EARS target/masker pairs x three SIR strata (90 synthetic mixtures)",
        "class": "adjacent_competing_speaker_suppression_historical_local",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "boundary": "Single-output, no enrollment prompt and no speaker IDs; target/masker ratio gain is relative suppression, not recovered source waveforms.",
    },
    {
        "id": "CI-4",
        "input": "Hush supplemental AMI speaker-dominant proxy diagnostic, seven directed pairs and 21 synthetic mixtures",
        "class": "adjacent_speaker_dominant_proxy_historical_local",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "boundary": "Non-overlap AMI turn crops from one mono meeting mix; no isolated speaker references, natural overlap or source-count result.",
    },
    {
        "id": "CI-5",
        "input": "AuxIVA statistical source-factorization lead and the H-GTCRN bundle that mentions AuxIVA in a two-microphone pipeline",
        "class": "classic_source_factorization_considered",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Census and plan notes only; no staged checkpoint, multichannel geometry, permutation policy or local run.",
    },
    {
        "id": "CI-6",
        "input": "Beam-TasNet, SpatialNet and neural-beamforming multichannel separation leads",
        "class": "multichannel_or_array_candidate_blocked",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Exact architecture/checkpoint and synchronised multichannel target data are unresolved; mono evidence cannot score array separation.",
    },
    {
        "id": "CI-7",
        "input": "Target-speaker extraction, VoiceFilter and VoiceFilter-Lite/personal-VAD enrollment-conditioned leads",
        "class": "enrollment_conditioned_extraction_blocked",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "SPK-02 boundary only: a speaker cue selects a target, while generic separation must recover multiple sources without deciding which to keep.",
    },
    {
        "id": "CI-8",
        "input": "Rights-qualified multi-source speech cohort with isolated references, natural overlap and scored permutation-invariant metrics",
        "class": "missing_multi_source_separation_cohort",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Absence is recorded explicitly; no missing cohort result is reported as a negative separation result.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "same-mixture identity",
        "role": "Task-matched damaged baseline for the Hush EARS and AMI synthetic mixtures; it preserves all sources and is not a separated output.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "id": "CT-2",
        "name": "generic DeepFilterNet3 denoiser",
        "role": "Adjacent single-output denoiser control on the same Hush mixtures; it is neither a separator nor a speaker-selector.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "id": "CT-3",
        "name": "noisy DNS2020 identity",
        "role": "Paired enhancement baseline for the SepFormer screen; no clean multi-source reference exists in that protocol.",
        "source_pin": "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md",
    },
    {
        "id": "CT-4",
        "name": "DeepFilterNet3, FastEnhancer Small and ClearVoice FRCRN comparison set",
        "role": "Single-output enhancer comparators for SepFormer; none produces multiple source estimates.",
        "source_pin": "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md",
    },
    {
        "id": "CT-5",
        "name": "target/masker projection ratio",
        "role": "Relative suppression diagnostic that can improve while absolute target SI-SDR and STOI fall; relative gain is not separation quality.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "id": "CT-6",
        "name": "permutation-invariant separation objective",
        "role": "The S08 method family requires source permutation handling; no local scorer, source-count policy or label permutation was applied.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "id": "CT-7",
        "name": "nonfinite-input adverse case",
        "role": "NaN/Inf input produces no serialized output and cannot count as a pass.",
        "source_pin": "docs/task-evidence/hush/README.md",
    },
    {
        "id": "CT-8",
        "name": "speaker-dominant proxy versus isolated reference",
        "role": "AMI turn crops can contain room and other-speaker bleed; they cannot substitute for isolated clean sources.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "EARS 30 target plus 30 masker source recordings",
        "class": "research_audio",
        "status": "CC BY-NC 4.0 research media in the cited record; bytes not staged or verified in this task",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "asset": "Deterministic synthetic Hush mixtures at +12/+18/+24 dB SIR",
        "class": "generated_fixture",
        "status": "Derived from the EARS subset; no external download, room, microphone or natural-overlap condition",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "asset": "AMI ES2004a Mix-Headset single meeting mix",
        "class": "research_audio",
        "status": "CC BY 4.0 annotations and one mono 17.49-minute headset mix; no isolated participant tracks",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "asset": "SpeechBrain SepFormer DNS4 checkpoint at pinned Hub revision",
        "class": "external_code_and_weights",
        "status": "Apache-2.0, 16 kHz one-output enhancement checkpoint; not staged or loaded in this task",
        "source_pin": "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md",
    },
    {
        "asset": "Hush source commit and ONNX deployment bundle",
        "class": "external_code_and_weights",
        "status": "Apache-2.0 identity pinned; no caller asset manifest or copy exists in this task",
        "source_pin": "docs/task-evidence/hush/README.md",
    },
    {
        "asset": "Conv-TasNet paper and method description (S08)",
        "class": "source_and_metadata_only",
        "status": "No exact code revision, checkpoint, license review or multi-source cohort staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "SpatialNet, Beam-TasNet and neural-beamforming source leads",
        "class": "source_and_metadata_only",
        "status": "No weights, adapter, array geometry or synchronised multichannel corpus",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
    },
    {
        "asset": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests",
        "class": "prepared_manifest_only",
        "status": "Prepared research manifests; no rights-qualified multi-source separation cohort and no collected rating",
        "source_pin": "research/voice-enhancement-20261101/evaluation_records.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Adjacent SpeechBrain SepFormer DNS4 single-output enhancement screen",
        "outcome_class": "adjacent_single_output_enhancement_historical_local",
        "component_ids": ["speechbrain-sepformer-dns4"],
        "source_pin": "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "noisy_pairs": 30,
            "clean_pairs": 30,
            "valid_outputs": 30,
            "delta_snr_db": -19.432,
            "delta_si_sdr_db": 8.525,
            "delta_stoi": 0.03313,
            "mean_rtf": 0.693,
            "p95_rtf": 0.819,
            "peak_rss_bytes": 1894531072,
            "clean_stoi": 0.99985,
            "clean_delta_stoi": -0.000150,
            "clean_si_sdr_db": 41.59,
            "raw_output_peak_min": 30.8364,
            "raw_output_peak_max": 273.3707,
        },
        "scope": "30 paired DNS2020 no-reverb files plus 30 clean diagnostics, mono 16 kHz, one whole waveform per call; one output stream, not multi-source separation; adjacent enhancement evidence and not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Adjacent Hush EARS primary/background suppression screen",
        "outcome_class": "adjacent_competing_speaker_suppression_historical_local",
        "component_ids": ["hush"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "target_pairs": 30,
            "masker_sources": 30,
            "mixtures": 90,
            "sir_strata_db": [12, 18, 24],
            "target_masker_ratio_gain_db_min": 8.08,
            "target_masker_ratio_gain_db_max": 8.46,
            "target_si_sdr_delta_db_12": -9.33,
            "target_si_sdr_delta_db_18": -14.54,
            "target_si_sdr_delta_db_24": -20.23,
            "target_stoi_delta_12": -0.141,
            "target_stoi_delta_18": -0.176,
            "target_stoi_delta_24": -0.197,
            "observed_delay_ms": 10,
            "mean_transform_rtf": 0.0278,
            "process_high_water_rss_mb": 96,
        },
        "scope": "30 distinct target and 30 distinct masker EARS recordings, first 4 s, mono 16 kHz, three SIR strata; synthetic non-overlap mixture, no speaker IDs, no enrollment prompt and no isolated multi-source output; adjacent suppression evidence and not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Adjacent Hush AMI speaker-dominant proxy diagnostic",
        "outcome_class": "adjacent_speaker_dominant_proxy_historical_local",
        "component_ids": ["hush"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "meeting": "ES2004a",
            "directed_pairs": 7,
            "mixtures": 21,
            "sir_strata_db": [12, 18, 24],
            "target_si_sdr_delta_db_12": -13.17,
            "target_si_sdr_delta_db_18": -18.41,
            "target_si_sdr_delta_db_24": -24.18,
            "target_stoi_delta_12": -0.193,
            "target_stoi_delta_18": -0.200,
            "target_stoi_delta_24": -0.207,
            "ratio_ci_includes_zero_all_strata": True,
            "mean_transform_rtf": 0.0292,
            "process_high_water_rss_mb": 92.2,
        },
        "scope": "One AMI mono meeting mix, seven directed speaker pairs, 21 synthetic additive mixtures; speaker-dominant proxies with bleed, not natural overlap or isolated clean references; adjacent suppression evidence and not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Conv-TasNet learns a time-domain encoder, mask and decoder for speech separation with permutation-invariant training",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Paper-level method claim; no exact code revision, checkpoint, cohort, source-count policy or local metric was reproduced.",
    },
    {
        "id": "RO-2",
        "claim": "SpeechBrain SepFormer DNS4 reports DNS4 2022 dev DNSMOS SIG 2.999, BAK 3.076 and OVRL 2.437",
        "class": "source_reported",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Upstream DNS4 challenge scope, not comparable to the local DNS2020 subset; the checkpoint is a single-output enhancer.",
    },
    {
        "id": "RO-3",
        "claim": "Hush is a causal 16 kHz enhancer trained to suppress competing speakers and is described as about 8 MB with CPU real-time inference",
        "class": "source_reported",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Vendor/upstream description; local EARS and AMI screens damaged the designated target and produced no isolated source estimate.",
    },
    {
        "id": "RO-4",
        "claim": "H-GTCRN combines GTCRN, FD-WPE, AuxIVA and spatial features in a two-microphone low-SNR pipeline",
        "class": "source_reported_census",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Census note only; no checkpoint, multichannel data, permutation policy or AuxIVA separation result is staged.",
    },
    {
        "id": "RO-5",
        "claim": "SpatialNet and Beam-TasNet address multichannel joint separation, denoising and dereverberation",
        "class": "source_reported",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Architecture/availability research only; no local weights, array geometry or synchronised target corpus.",
    },
    {
        "id": "RO-6",
        "claim": "VoiceFilter and the target-speaker extraction family require a speaker cue and target a known speaker in a mixture",
        "class": "source_reported_adjacent_boundary",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Enrollment-conditioned SPK-02 boundary; not generic separation, and no official local weights or score exist.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "geometry_layout_calibration": "No array geometry, layout, timestamp calibration or reference channel exists; every local adjacent row is mono 16 kHz.",
        "source_target_reference_conditions": "Hush rows use synthetic target/masker or speaker-dominant turn crops; SepFormer has one clean DNS reference per pair and one output stream.",
        "permissions": "EARS is CC BY-NC research media and AMI is CC BY 4.0; no rights-qualified multi-source separation cohort or redistribution grant exists.",
        "held_out_labels": "No held-out multi-source labels, isolated speaker references or task-matched separation split is staged.",
        "leakage_and_reference_changes": "No channel loss, room-change, source-count-change or reference-change measurement exists.",
        "task_matched_quality": "Only adjacent single-output SI-SDR/STOI and target/masker ratio rows; no permutation-invariant separation metric.",
        "target_damage": "Hush lowers designated-target SI-SDR and STOI in every stratum; SepFormer measures one enhanced stream, not per-source damage.",
        "source_count_and_order": "Unaddressed: no two/three-source count policy, permutation assignment or continuity tracking was executed.",
        "missing_result_accounting": "No SPK-01 multi-source separation execution exists; the absence is recorded, not promoted to a pass.",
        "listening": "No blinded listening or per-stream intelligibility rating exists.",
        "timing": "No target-device, streaming-state or callback-deadline measurement exists for a separator.",
    },
    "blocked": [
        "Rights-qualified multi-source speech cohort with isolated references, natural overlap and variable source count",
        "Frozen permutation-invariant separation metrics with source-order, continuity and count accounting",
        "Independent blinded listening and per-stream content/intelligibility analysis",
        "Pinned target-device real-time separator timing, memory, latency and streaming-state evidence",
        "Staged exact separator and classic-baseline weights under a locked runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "adjacent_single_output_enhancement_historical_local": True,
    "adjacent_competing_speaker_suppression_historical_local": True,
    "adjacent_speaker_dominant_proxy_historical_local": True,
    "classic_source_factorization_considered": True,
    "multichannel_or_array_candidate_blocked": True,
    "enrollment_conditioned_extraction_blocked": True,
    "source_documented_candidate_not_staged_or_run": True,
    "generated_synthetic_mixture_fixture": True,
    "prepared_manifest_only": True,
    "missing_multi_source_separation_cohort": True,
    "generic_multi_source_separation_execution": False,
    "permutation_invariant_separation_metric": False,
    "real_overlap_two_speaker_corpus": False,
    "real_corpus": False,
    "weights": False,
    "runtime_invocation": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

CATEGORY_SCOPE: Dict[str, bool] = {
    "multiple_source_waveform_output_only": True,
    "source_order_continuity_and_count_require_handling": True,
    "separation_does_not_choose_sources_to_keep": True,
    "separation_is_not_detection_or_diarization": True,
    "separation_is_not_target_speaker_extraction": True,
    "separation_is_not_noise_suppression": True,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Stage and evaluate Conv-TasNet (S08) with pinned weights and permutation-invariant two- and three-source scoring",
        "evidence_gap": "Conv-TasNet is a paper lead and a considered inventory row only; no exact revision, checkpoint, cohort, source-count policy or local separation output exists.",
        "follow_up_ids": ["SDK-CONV-TASNET", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a local three-source separation execution; the linked feasibility row is a bounded scoping lead, not an enabled separator.",
    },
    {
        "id": "G02",
        "actionable_gap": "Establish a classic statistical/source-factorization baseline (AuxIVA/ICA/NMF) with permutation and mono-versus-multichannel conditions",
        "evidence_gap": "AuxIVA is mentioned inside the H-GTCRN census note; no staged implementation, geometry, initialization, permutation policy or local separation score exists.",
        "follow_up_ids": ["SDK-AUXIVA", "SDK-H-GTCRN"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has an isolated AuxIVA separation result; the linked rows cover a candidate and a bundled multichannel pipeline only.",
    },
    {
        "id": "G03",
        "actionable_gap": "Freeze a rights-qualified multi-source mixed-speech cohort with isolated references, natural overlap and variable source count",
        "evidence_gap": "Fixtures are synthetic EARS/AMI mixtures or single-output DNS pairs; no rights-qualified cohort with isolated sources, natural overlap or held-out speakers exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a multi-source separation cohort; the linked research-control rows own manifests and preservation scoring, and the foundation row owns evidence rules.",
    },
    {
        "id": "G04",
        "actionable_gap": "Frozen permutation-invariant separation metrics with source-order, continuity, source-count and missing-source accounting",
        "evidence_gap": "No local scorer assigns estimated sources to references or records an unknown-count outcome; SI-SDR/STOI single-stream scores and projection ratios cannot substitute.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a permutation-invariant separation scorer; the linked foundation and research-control rows own evidence rules and a preservation harness, not a separation metric.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate multichannel neural separation and beamforming with calibrated array geometry and synchronised clean targets",
        "evidence_gap": "Beam-TasNet, SpatialNet and neural beamforming are blocked or considered; delay-and-sum, MVDR and localization have no executed array separation result.",
        "follow_up_ids": [
            "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET",
            "SDK-SPATIALNET",
            "SDK-NEURAL-BEAMFORMING",
            "SDK-DELAY-AND-SUM-BEAMFORMER",
            "SDK-MVDR-BEAMFORMING",
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a local multichannel separation execution; the linked feasibility rows are scoping leads that all lack weights, geometry or synchronised array data.",
    },
    {
        "id": "G06",
        "actionable_gap": "Keep target-speaker extraction and personal VAD (SPK-02) separate from generic separation",
        "evidence_gap": "TSE, VoiceFilter and VoiceFilter-Lite are blocked and require an enrollment cue; no generic multi-source separation result can inherit from a target-selection task.",
        "follow_up_ids": [
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
            "SDK-VOICEFILTER",
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner mixes target-conditioned extraction with generic separation; the linked feasibility rows own the adjacent SPK-02 boundary only.",
    },
    {
        "id": "G07",
        "actionable_gap": "Keep speaker-change segmentation, diarization and identity (SPK-03/04/05) separate from waveform separation",
        "evidence_gap": "Pyannote, BIC segmentation and x-vector embeddings are considered annotation or identity rows; no separated waveform or source-count result exists.",
        "follow_up_ids": [
            "SDK-PYANNOTE-DIARIZATION",
            "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION",
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner converts diarization or identity labels into separated waveforms; the linked feasibility rows cover annotation and identity boundaries only.",
    },
    {
        "id": "G08",
        "actionable_gap": "Keep single-output enhancement and competing-speaker suppression adjacent, not a SPK-01 separation result",
        "evidence_gap": "SepFormer DNS4 and Hush are evaluated single-output systems; both damage or cannot report per-source recovery, and neither exposes a multi-source waveform output.",
        "follow_up_ids": [
            "SDK-HUSH",
            "SDK-SPEECHBRAIN-SEPFORMER-DNS4",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a multi-source separation result from these adjacent rows; the linked implementation rows own single-output enhancement and suppression, and the foundation row owns evidence rules.",
    },
    {
        "id": "G09",
        "actionable_gap": "Run independent blinded listening and per-stream content/intelligibility analysis for separated outputs",
        "evidence_gap": "No human rating exists; Hush and SepFormer report signal metrics only, so per-source naturalness, leakage perception and intelligibility after separation remain unmeasured.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-DNSMOS-P-835-AND-DNSMOS-C",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner collected SPK-01 ratings; the linked research-control rows own listening design, preservation scoring and model-free quality proxies, not a separation result.",
    },
    {
        "id": "G10",
        "actionable_gap": "Measure target-device separator timing, memory, streaming state, source-count latency and deadline behavior",
        "evidence_gap": "Only offline whole-utterance or frame-based desktop compute exists; no callback-path, separator delay, memory bound, streaming state or device timing was measured.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
            "SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has device or separator timing evidence; the linked foundation rows own lifecycle/timing and exact-head rules, and the implementation row owns the offline adapter boundary.",
    },
    {
        "id": "G11",
        "actionable_gap": "Define an opt-in provider intake and public exposure path for a separator",
        "evidence_gap": "No SPK-01 provider descriptor, installed-archive comparison, default selection or independent review exists.",
        "follow_up_ids": ["SDK-FND-PROVIDER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake; the linked foundation rows own provider boundaries and exact-head evidence.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-CONV-TASNET", "title": "Conv-TasNet", "mode": "feasibility"},
    {"task_id": "SDK-AUXIVA", "title": "AuxIVA", "mode": "feasibility"},
    {"task_id": "SDK-H-GTCRN", "title": "H-GTCRN", "mode": "feasibility"},
    {"task_id": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET", "title": "Beam-TasNet / Beam-Guided TasNet", "mode": "feasibility"},
    {"task_id": "SDK-SPATIALNET", "title": "SpatialNet", "mode": "feasibility"},
    {"task_id": "SDK-NEURAL-BEAMFORMING", "title": "Neural beamforming", "mode": "feasibility"},
    {"task_id": "SDK-DELAY-AND-SUM-BEAMFORMER", "title": "Delay-and-sum beamformer", "mode": "feasibility"},
    {"task_id": "SDK-MVDR-BEAMFORMING", "title": "MVDR beamforming", "mode": "feasibility"},
    {"task_id": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL", "title": "Source localization / direction-of-arrival", "mode": "feasibility"},
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER", "title": "VoiceFilter", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-PYANNOTE-DIARIZATION", "title": "pyannote diarization", "mode": "feasibility"},
    {"task_id": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION", "title": "Bayesian information criterion speaker segmentation", "mode": "feasibility"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
    {"task_id": "SDK-HUSH", "title": "Hush", "mode": "implementation"},
    {"task_id": "SDK-SPEECHBRAIN-SEPFORMER-DNS4", "title": "SpeechBrain SepFormer DNS4", "mode": "implementation"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-DNSMOS-P-835-AND-DNSMOS-C", "title": "DNSMOS P.835 and DNSMOS-C", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
    {"task_id": "SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS", "title": "PyTorch and SpeechBrain adapters", "mode": "implementation"},
]

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
)

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified multi-source speech cohort with isolated references, natural overlap, variable source count and held-out speakers"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen permutation-invariant separation metrics with source-order, continuity, source-count and missing-source accounting"},
    {"id": "RG-03", "blocked": True, "requirement": "Independent blinded listening and per-stream content/intelligibility analysis"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned target-device real-time separator timing, memory, latency, streaming state and deadline evidence"},
    {"id": "RG-05", "blocked": True, "requirement": "Staged exact separator and classic-baseline weights under a locked runtime with approved reference parity"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **SPK-01 — Generic speech/source separation** | Recover multiple sources from a mixture. Scope: requested. |",
        "Source order, continuity and source count require handling; separation does not decide which sources to keep.",
    ],
    "research/category_survey/sources.md": [
        "| S08 | [Conv-TasNet paper](https://arxiv.org/abs/1809.07454) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    ],
    "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md": [
        "**+8.525 dB**",
        "offline whole-utterance model without phone or streaming measurements",
        "one full waveform per call, mono 16 kHz",
    ],
    "research/voice-enhancement-20261101/agent-sepformer-result-audit/REPORT.md": [
        "30.8364 to 273.3707",
        "ΔSI-SDR +8.52509 dB, ΔSTOI +0.0331316",
    ],
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md": [
        "raised the relative target-to-masker ratio but damaged the designated target across all three SIR strata",
        "It does not evaluate reference-conditioned target-speaker extraction",
        "+8.14 [+5.67, +10.38]",
    ],
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": [
        "their intervals include zero in all strata",
        "Keep the matrix status **partially evaluated**",
        "seven distinct directed speaker pairs",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "SpatialNet,unavailable/blocked",
        "SpeechBrain SepFormer DNS4,evaluated",
        "Spatial and speaker,Hush,partially evaluated",
    ],
    "research/noise_suppression_candidate_census.md": [
        "| **H-GTCRN** | Two-microphone low-SNR enhancement combining GTCRN, FD-WPE, AuxIVA and spatial features |",
        "| **Hush** | Causal 16 kHz speech enhancer explicitly trained to suppress competing speakers in conversational audio |",
        "| **SpeechBrain SepFormer DNS4** | Dual-path transformer, 16 kHz DNS-4 enhancement reference |",
    ],
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": [
        "Beam-TasNet combines multichannel Conv-TasNet separation and MVDR",
        "No official weights/runtime; no local score",
        "No SpatialNet weights, multichannel adapter or local evaluation found",
    ],
    "research/pilot_source_research.md": [
        "guided source separation",
        "CHiME-7 UDASE",
    ],
    "research/voice-enhancement-20261101/evaluation_records.md": [
        "not reference-conditioned target-speaker extraction or real-room acceptance.",
        "No mobile or streaming score exists.",
    ],
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md": [
        "I found no staged model/checkpoint for the named voice-conversion, spatial extraction, or neural BWE candidates",
        "no compatible multichannel speaker target corpus for spatial/TSE scoring",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/hush/README.md": [
        "`component_id=hush`, `SPK-01`",
        "Decision: **DEFER**",
        "does not load the ONNX bundle",
    ],
    "docs/task-evidence/survey-det-03/README.md": [
        "source separation (`SPK-01`)",
        "Detection neither separates",
        "waveforms nor identifies unwanted speech.",
    ],
    "docs/task-evidence/survey-cln-01/README.md": [
        "keeps stationary noise, changing noise and competing",
        "boundary with `SPK-01/02`",
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
    "source_separation_claim": False,
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
        raise MapError("SPK-01 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("SPK-01 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F05 / SPK-01 is not unique")
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
            raise MapError("legacy backlog mismatch: F05/SPK-01/%s" % key)


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
        if row.get("adjacent") is not True or row.get("not_component_evidence") is not True:
            raise MapError("historical execution is not marked adjacent: " + row["id"])


def _check_evidence_classes() -> None:
    classes = [row["class"] for row in COMPARISON_INPUTS]
    classes += [row["outcome_class"] for row in HISTORICAL_EXECUTIONS]
    enhancement = any("adjacent_single_output_enhancement" in c for c in classes)
    suppression = any("adjacent_competing_speaker_suppression" in c for c in classes)
    proxy = any("adjacent_speaker_dominant_proxy" in c for c in classes)
    classic = any(c == "classic_source_factorization_considered" for c in classes)
    blocked_array = any(c == "multichannel_or_array_candidate_blocked" for c in classes)
    enrollment = any(c == "enrollment_conditioned_extraction_blocked" for c in classes)
    documented = any(c == "source_documented_candidate_not_staged_or_run" for c in classes)
    missing = any(c == "missing_multi_source_separation_cohort" for c in classes)
    generated = any("generated_fixture" in row["class"] for row in ASSETS)
    prepared = any("prepared" in row["class"].lower() for row in ASSETS)
    if EVIDENCE_CLASSES["adjacent_single_output_enhancement_historical_local"] != enhancement:
        raise MapError("adjacent-enhancement evidence class does not match mapped records")
    if EVIDENCE_CLASSES["adjacent_competing_speaker_suppression_historical_local"] != suppression:
        raise MapError("adjacent-suppression evidence class does not match mapped records")
    if EVIDENCE_CLASSES["adjacent_speaker_dominant_proxy_historical_local"] != proxy:
        raise MapError("adjacent-proxy evidence class does not match mapped records")
    if EVIDENCE_CLASSES["classic_source_factorization_considered"] != classic:
        raise MapError("classic-source-factorization class does not match mapped records")
    if EVIDENCE_CLASSES["multichannel_or_array_candidate_blocked"] != blocked_array:
        raise MapError("multichannel-array evidence class does not match mapped records")
    if EVIDENCE_CLASSES["enrollment_conditioned_extraction_blocked"] != enrollment:
        raise MapError("enrollment-extraction evidence class does not match mapped records")
    if EVIDENCE_CLASSES["source_documented_candidate_not_staged_or_run"] != documented:
        raise MapError("documented-candidate evidence class does not match mapped records")
    if EVIDENCE_CLASSES["missing_multi_source_separation_cohort"] != missing:
        raise MapError("missing-cohort evidence class does not match mapped records")
    if EVIDENCE_CLASSES["generated_synthetic_mixture_fixture"] != generated:
        raise MapError("generated-fixture evidence class does not match assets")
    if EVIDENCE_CLASSES["prepared_manifest_only"] != prepared:
        raise MapError("prepared-manifest evidence class does not match assets")
    for key in (
        "generic_multi_source_separation_execution",
        "permutation_invariant_separation_metric",
        "real_overlap_two_speaker_corpus",
        "real_corpus",
        "weights",
        "runtime_invocation",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported evidence class is true: " + key)


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
        if not gap.get("owner_note"):
            raise MapError("gap has no owner note: " + gap["id"])
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
        "category_scope": dict(CATEGORY_SCOPE),
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
