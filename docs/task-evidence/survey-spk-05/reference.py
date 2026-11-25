# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-SPK-05.

This module builds a bounded taxonomy/comparison evidence map for the speaker
representation, identification and verification category (inventory category
``SPK-05``). It reads only pinned, read-only documents from the enclosing
``audioml`` workspace and the SDK worktree. It does not load audio, weights,
codecs, runtimes, media or the network, and it does not register, expose, enable
or qualify any processor.

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
TASK = "SDK-SURVEY-SPK-05"
TITLE = "Review coverage for Speaker representation, identification and verification"
CATEGORY_ID = "SPK-05"
LEGACY_FAMILY = "F06"
BRANCH = "swarm/SDK-SURVEY-SPK-05"
BASE_COMMIT = "87a8107a0b495378f5fb5ead55cf32a0f222ad56"
PROFILE = "Spatial"
COMPONENT = "speaker-representation-identification-verification-evidence-map"
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
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/results/tokan-metrics.json": "e4eddb01575ef102d820605d17378913cb9552fbb69ab9b97667c6e4eb90bde3",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md": "ef093eee8c8cd68984d3a7f5602fcc44c9a0262990e7c90c9bd34ecc3d8fadc2",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md": "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
    "research/voice-conversion-eval-20261101/results/meanvc2/speaker_similarity.json": "c5091816b099280490ac8742a94dafe5421deefbe40791add8a57efc350244a0",
    "research/voice-conversion-eval-20261101/results/openvoice/metrics.json": "322d49984ff5599b74bb18833517a5ca0a2b636d93d3a81b5fe7d6a0177557f9",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
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
    "docs/task-evidence/survey-spk-01/README.md": "554a9fcc044e89c35ba761bf1fa8f7fed172ba22f797e44bdd64a753c00adc9d",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Speakers and separation",
    "name": "Speaker representation, identification and verification",
    "scope": "discovered_extension",
    "output_kind": "representation/annotation",
    "purpose": "Compare speech with enrolled people or a claimed identity.",
    "method_families": {
        "classic": "Statistical speaker models and likelihood scoring",
        "ml": "Speaker embeddings; x-vectors/TDNN; cosine/PLDA scoring",
    },
    "input_output": "Speech \u2192 embedding, gallery match or verification score",
    "live_or_comparison_boundary": (
        "Identification and verification need separate outputs/metrics. "
        "An identity is not a policy for preserving speech."
    ),
    "source_ids": ["S05"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S05",
        "title": "X-vector speaker recognition study",
        "url": "https://www.isca-archive.org/interspeech_2019/snyder19b_interspeech.html",
        "access_scope": "direct",
        "researcher": "analysis",
        "mapped_components": ["x-vector-speaker-embeddings"],
        "gap_ids": ["G01", "G04"],
        "finding": (
            "The named source lead is the x-vector speaker-recognition study: "
            "a deep TDNN speaker-embedding family with statistical backend "
            "scoring. It defines the ML embedding and verification method "
            "family, but no exact code revision, checkpoint, trial list, "
            "score calibration, open-set impostor protocol or local "
            "identification/verification execution exists in the reviewed "
            "records. The classic statistical likelihood-scoring family has "
            "no component row at all."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Statistical speaker models and likelihood scoring (GMM-UBM, MAP adaptation and likelihood-ratio scoring)",
        "components": [],
        "gap_ids": ["G02"],
        "status": "classic_speaker_model_candidate_not_staged_or_run",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Speaker-change segmentation and anonymous clustering boundary (BIC and diarization, not identity verification)",
        "components": [
            "bayesian-information-criterion-speaker-segmentation",
            "pyannote-diarization",
        ],
        "gap_ids": ["G06"],
        "status": "annotation_boundary_not_spk05_identity",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Speaker-conditioned extraction and personal VAD boundary (enrollment cue, not identity verification)",
        "components": [
            "target-speaker-extraction-family",
            "voicefilter",
            "voicefilter-lite-personal-vad",
        ],
        "gap_ids": ["G07"],
        "status": "enrollment_conditioned_extraction_boundary_not_identity",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Speaker embeddings; x-vectors/TDNN representation learning (S05)",
        "components": ["x-vector-speaker-embeddings"],
        "gap_ids": ["G01"],
        "status": "source_documented_candidate_not_staged_or_run",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Cosine/PLDA scoring over deep speaker embeddings for verification and gallery matching",
        "components": ["x-vector-speaker-embeddings"],
        "gap_ids": ["G04"],
        "status": "scoring_family_documented_no_local_trial_list_or_calibration",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Research-control deep embedding similarity proxies (Resemblyzer and SpeechBrain ECAPA), not identity verifiers",
        "components": [
            "resemblyzer-speaker-similarity-proxy",
            "speechbrains-ecapa-speaker-similarity",
        ],
        "gap_ids": ["G05"],
        "status": "embedding_similarity_research_control_not_verification",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml-adjacent",
        "family": "In-model speaker-embedding cosines inside voice conversion (TokAN, MeanVC2, OpenVoice, RVC), not identification or verification",
        "components": ["tokan", "meanvc2", "openvoice-v2", "rvc-v2-vctk-p226"],
        "gap_ids": ["G08"],
        "status": "adjacent_identity_provenance_unverified",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "resemblyzer-speaker-similarity-proxy", "evidence_status": "partial", "task": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"},
    {"component_id": "speechbrains-ecapa-speaker-similarity", "evidence_status": "partial", "task": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY"},
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "bayesian-information-criterion-speaker-segmentation", "evidence_status": "considered", "task": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION"},
    {"component_id": "target-speaker-extraction-family", "evidence_status": "blocked", "task": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"},
    {"component_id": "voicefilter", "evidence_status": "blocked", "task": "SDK-VOICEFILTER"},
    {"component_id": "voicefilter-lite-personal-vad", "evidence_status": "blocked", "task": "SDK-VOICEFILTER-LITE-PERSONAL-VAD"},
    {"component_id": "tokan", "evidence_status": "partial", "task": "SDK-TOKAN"},
    {"component_id": "meanvc2", "evidence_status": "partial", "task": "SDK-MEANVC2"},
    {"component_id": "openvoice-v2", "evidence_status": "partial", "task": "SDK-OPENVOICE-V2"},
    {"component_id": "rvc-v2-vctk-p226", "evidence_status": "partial", "task": "SDK-RVC-V2-VCTK-P226"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "X-vector/TDNN speaker-recognition study with deep embedding and statistical backend scoring (named source lead S05)",
        "class": "source_documented_candidate_not_staged_or_run",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Paper-level method definition only; no exact code revision, checkpoint, trial list, score calibration or local output exists.",
    },
    {
        "id": "CI-2",
        "input": "TokAN accent conversion on three accent-labelled Arabic/Hindi/Korean utterances with the same source clip as the speaker reference, scored by a Resemblyzer cosine proxy",
        "class": "adjacent_same_clip_similarity_proxy_historical_local",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Same-clip reference makes speaker retention easy; Resemblyzer cosine is a quick similarity proxy, not identification or verification, and only three utterances were run.",
    },
    {
        "id": "CI-3",
        "input": "MeanVC2 40+40 ms and 120+40 ms voice-conversion runs scored by the in-model WavLM+ECAPA target encoder",
        "class": "adjacent_in_model_speaker_similarity_historical_local",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "One source and one p360 target; the cosine is an in-model diagnostic that compares only within this pair, not an independent identity score.",
    },
    {
        "id": "CI-4",
        "input": "OpenVoice V2 offline tone-color conversion scored by its own reference encoder",
        "class": "adjacent_in_model_speaker_similarity_historical_local",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "One fixed source/target pair and a model-internal cosine; it is not perceptual, independent or a verification metric.",
    },
    {
        "id": "CI-5",
        "input": "RVC VCTK p226 fixed-pair conversion whose target speaker ID is presumed but unverified",
        "class": "adjacent_identity_provenance_unverified",
        "source_pin": "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md",
        "boundary": "An unverified presumed target identity is not an enrolment record; no speaker metric and no real-time/device run exist.",
    },
    {
        "id": "CI-6",
        "input": "Resemblyzer speaker-embedding similarity encoder as an evaluation control",
        "class": "embedding_similarity_research_control",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Encoder revision, enrolment geometry and score calibration are not pinned; a similarity proxy is not a verification decision.",
    },
    {
        "id": "CI-7",
        "input": "SpeechBrain ECAPA speaker-similarity control",
        "class": "embedding_similarity_research_control",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "The reviewed record contains in-model cosines, not an external ECAPA verification run with genuine and impostor trials.",
    },
    {
        "id": "CI-8",
        "input": "Pyannote diarization and BIC speaker-change segmentation considered as annotation boundaries",
        "class": "diarization_or_segmentation_boundary",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Anonymous cluster labels and change boundaries are not enrolled identities; no local diarization or identity run exists.",
    },
    {
        "id": "CI-9",
        "input": "Target-speaker extraction, VoiceFilter and VoiceFilter-Lite/personal VAD enrolment-conditioned leads",
        "class": "enrollment_conditioned_extraction_boundary",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "A speaker cue selects or gates a target; it does not verify a claimed identity and cannot inherit a verification result.",
    },
    {
        "id": "CI-10",
        "input": "Rights-qualified, consent-cleared speaker trial list with enrolled and impostor speakers, speaker-disjoint held-out trials and separate identification/verification labels",
        "class": "missing_speaker_verification_trial_list",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Absence is recorded explicitly; no missing trial-list result is reported as a negative verification result.",
    },
    {
        "id": "CI-11",
        "input": "Classic GMM-UBM/MAP statistical speaker model with likelihood-ratio scoring",
        "class": "classic_speaker_model_candidate_not_staged_or_run",
        "source_pin": "audio_categories.md",
        "boundary": "The catalogued classic family has no component row, staged model, enrolment set, likelihood calibration or local score.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "same-clip speaker reference",
        "role": "Identity control for the TokAN rows. The source clip is also the reference, so it tests retention on an easy pair and cannot test verification.",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "id": "CT-2",
        "name": "source identity in a fixed source/target pair",
        "role": "Baseline that preserves the source voice; a successful conversion is not an identity decision.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-3",
        "name": "in-model speaker cosine",
        "role": "Model-specific diagnostic that is not comparable across encoders and is not a calibrated verification score.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-4",
        "name": "fixed threshold or score calibration",
        "role": "Absent; no genuine/impostor score distributions, normalisation or operating point exist.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-5",
        "name": "impostor and negative trials",
        "role": "Absent; every reviewed similarity row uses a designated target or the same clip, so open-set false accepts are unmeasured.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-6",
        "name": "nonfinite-input adverse case",
        "role": "NaN/Inf input produces no serialized output and cannot count as a pass.",
        "source_pin": "docs/task-evidence/hush/README.md",
    },
    {
        "id": "CT-7",
        "name": "presumed target identity",
        "role": "RVC speaker ID 1 is presumed p226 but unverified; a guessed identity cannot serve as an enrolment record.",
        "source_pin": "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md",
    },
    {
        "id": "CT-8",
        "name": "human identity judgement",
        "role": "Absent; no blinded listener judged whether two recordings are the same enrolled person.",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Three accent-labelled Arabic/Hindi/Korean utterances used as TokAN source and speaker reference",
        "class": "research_audio",
        "status": "Research media in the cited record; media bytes, speaker consent and redistribution terms are not staged or verified in this task",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "Resemblyzer speaker-embedding encoder",
        "class": "external_code_and_weights",
        "status": "Similarity-proxy dependency; exact revision, checkpoint digest and licence are not pinned here and no weights are staged",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "MeanVC2 WavLM+ECAPA speaker checkpoint (1.21 GB)",
        "class": "external_code_and_weights",
        "status": "Hash-verified during the cited run and then removed; no checkpoint is staged in this task",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "p360 target reference and LJ Speech source utterance",
        "class": "research_audio",
        "status": "Fixed one-pair research fixture; p360 upstream-demo provenance and independent licence remain unconfirmed",
        "source_pin": "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md",
    },
    {
        "asset": "OpenVoice V2 tone-color converter and its reference encoder",
        "class": "external_code_and_weights",
        "status": "Offline whole-file model; the reported cosine comes from the converter's own encoder and is not independent",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "RVC VCTK p226 target index",
        "class": "external_code_and_weights",
        "status": "Target identity is presumed, not verified; exact target provenance and consent are unresolved",
        "source_pin": "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md",
    },
    {
        "asset": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests",
        "class": "prepared_manifest_only",
        "status": "Prepared research manifests; no consent-cleared speaker-verification trial list, enrolment set or gallery split exists",
        "source_pin": "research/voice-enhancement-20261101/evaluation_records.md",
    },
    {
        "asset": "X-vector speaker-recognition paper and method description (S05)",
        "class": "source_and_metadata_only",
        "status": "No exact code revision, checkpoint, trial list, licence review or trained model staged",
        "source_pin": "research/category_survey/sources.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Adjacent TokAN same-clip accent conversion with a Resemblyzer similarity proxy",
        "outcome_class": "adjacent_same_clip_similarity_proxy_historical_local",
        "component_ids": ["tokan", "resemblyzer-speaker-similarity-proxy"],
        "source_pin": "research/accent-conversion-20261101/README.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "utterances": 3,
            "l1_accents": ["Arabic", "Hindi", "Korean"],
            "speaker_embedding_cosine_arabic": 0.8377127647399902,
            "speaker_embedding_cosine_hindi": 0.7982522249221802,
            "speaker_embedding_cosine_korean": 0.8736226558685303,
            "whisper_tiny_wer_all": 0.0,
            "duration_ratio_arabic": 0.6609976417922379,
            "duration_ratio_hindi": 0.9111688649210579,
            "duration_ratio_korean": 0.9072180316627411,
            "same_clip_as_speaker_reference": True,
            "output_sample_rate_hz": 24000,
        },
        "scope": "Three accent-labelled Arabic/Hindi/Korean utterances, same source clip used as the speaker reference, CPU offline conversion; Resemblyzer cosine is a quick similarity proxy, not an identity rating or verification decision; adjacent evidence and not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Adjacent MeanVC2 in-model WavLM+ECAPA target-similarity diagnostic",
        "outcome_class": "adjacent_in_model_speaker_similarity_historical_local",
        "component_ids": ["meanvc2"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "source_utterances": 1,
            "target_references": 1,
            "configs": ["40+40 ms", "120+40 ms"],
            "cosine_40_40": 0.6685560345649719,
            "cosine_120_40": 0.7017126083374023,
            "file_rtf_40_40": 0.959,
            "file_rtf_120_40": 0.396,
            "whisper_tiny_wer_both": 0.0,
            "in_model_diagnostic": True,
        },
        "scope": "One LJ Speech source and one p360 target reference, two streaming configurations in file mode; the WavLM+ECAPA cosine is an in-model diagnostic that compares only within this pair, not independent verification; adjacent evidence and not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Adjacent OpenVoice V2 in-model target-similarity diagnostic",
        "outcome_class": "adjacent_in_model_speaker_similarity_historical_local",
        "component_ids": ["openvoice-v2"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "adjacent": True,
        "not_component_evidence": True,
        "values": {
            "source_utterances": 1,
            "target_references": 1,
            "openvoice_speaker_embedding_cosine_to_target": 0.8901664018630981,
            "conversion_rtf": 0.3412188421905178,
            "speaker_embedding_seconds": 0.9023486669757403,
            "whisper_tiny_wer": 0.0,
            "in_model_diagnostic": True,
        },
        "scope": "One fixed LJ Speech source and p360 target pair, offline whole-file conversion; the cosine uses OpenVoice's own reference encoder and is not perceptual or independent identity evidence; adjacent evidence and not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "S05 defines the x-vector/TDNN speaker-recognition study lead",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "The source index gives a paper title and URL; no exact code revision, checkpoint, trial list, calibration or local metric was reproduced.",
    },
    {
        "id": "RO-2",
        "claim": "Resemblyzer cosine is a quick similarity proxy, not a human identity rating",
        "class": "source_reported",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "The cited author states this limitation for the same-clip TokAN screen; it remains true for any downstream interpretation.",
    },
    {
        "id": "RO-3",
        "claim": "MeanVC2's WavLM+ECAPA speaker checkpoint was 1.21 GB, hash-verified and removed after the cited runs",
        "class": "source_reported",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "Asset availability only; no checkpoint is staged and no verification score was produced.",
    },
    {
        "id": "RO-4",
        "claim": "Diarization should keep anonymous speaker IDs separate from verification",
        "class": "source_reported_plan_note",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Inventory plan note only; no local diarization or identity result exists.",
    },
    {
        "id": "RO-5",
        "claim": "VoiceFilter requires a reference utterance or embedding and targets a known speaker in a mixture",
        "class": "source_reported_adjacent_boundary",
        "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "boundary": "Speaker-conditioned extraction boundary; no official local weights, runtime or verification result.",
    },
    {
        "id": "RO-6",
        "claim": "BIC speaker-change segmentation and diarization are annotation boundaries, not identity verification",
        "class": "source_reported_adjacent_boundary",
        "source_pin": "docs/task-evidence/survey-det-03/README.md",
        "boundary": "Adjacent detection/segmentation evidence; anonymous labels cannot be promoted to enrolled identities.",
    },
    {
        "id": "RO-7",
        "claim": "The RVC VCTK p226 target speaker ID is presumed but unverified",
        "class": "source_reported_local_limitation",
        "source_pin": "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md",
        "boundary": "A local provenance limitation, not a negative identity result; no enrolment record or verification score exists.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "geometry_layout_calibration": "No enrolment/reference channel, device, room or timestamp geometry is recorded; the available rows are fixed-file or same-clip pairs.",
        "source_target_reference_conditions": "TokAN uses the same source clip as its reference; MeanVC2 and OpenVoice use one LJ Speech source and one p360 target whose provenance is unconfirmed.",
        "permissions": "No consent-cleared biometric enrolment, gallery retention policy or speaker-disjoint redistribution grant exists.",
        "held_out_labels": "No speaker-disjoint held-out identification or verification trial list, genuine/impostor labels or open-set protocol is staged.",
        "leakage_and_reference_changes": "No speaker overlap, same-session leakage, channel-change or reference-change measurement exists.",
        "task_matched_quality": "Only in-model cosine diagnostics; no rank-1 identification accuracy, mAP, EER, minDCF or calibrated threshold.",
        "target_damage": "No identity-preservation damage was measured; the TokAN Arabic output lost 34% of source duration.",
        "source_count_and_order": "Gallery size, open-set impostors, score normalisation and trial order are unaddressed.",
        "missing_result_accounting": "No SPK-05 identification or verification execution exists; the absence is recorded, not promoted to a pass.",
        "listening": "No blinded human same/different identity judgement exists.",
        "timing": "No target-device embedding-extraction, gallery-search or callback-deadline measurement exists.",
    },
    "blocked": [
        "Rights-qualified, consent-cleared speaker trial list with genuine and impostor trials and speaker-disjoint held-out speakers",
        "Separate frozen identification (rank-1/mAP) and verification (EER/minDCF) metrics with calibration and an operating point",
        "Independent blinded human identity/similarity judgement",
        "Pinned target-device embedding, gallery-search timing, memory and streaming-state evidence",
        "Staged exact x-vector/TDNN and classic statistical-baseline weights under a locked runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "adjacent_same_clip_similarity_proxy_historical_local": True,
    "adjacent_in_model_speaker_similarity_historical_local": True,
    "adjacent_identity_provenance_unverified": True,
    "source_documented_candidate_not_staged_or_run": True,
    "classic_speaker_model_candidate_not_staged_or_run": True,
    "embedding_similarity_research_control": True,
    "diarization_or_segmentation_boundary": True,
    "enrollment_conditioned_extraction_boundary": True,
    "missing_speaker_verification_trial_list": True,
    "prepared_manifest_only": True,
    "speaker_identification_execution": False,
    "speaker_verification_execution": False,
    "verification_metric_eer_mindcf": False,
    "open_set_trial_list": False,
    "score_calibration": False,
    "consent_cleared_biometric_enrollment": False,
    "real_corpus": False,
    "weights": False,
    "runtime_invocation": False,
    "human_listening_result": False,
    "device_timing": False,
    "privacy_approval": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

CATEGORY_SCOPE: Dict[str, bool] = {
    "representation_embedding_gallery_or_verification_score_only": True,
    "identification_and_verification_need_separate_outputs_and_metrics": True,
    "identity_is_not_a_policy_for_preserving_speech": True,
    "identity_is_not_diarization_or_segmentation": True,
    "identity_is_not_speaker_conditioned_extraction": True,
    "identity_is_not_speech_separation_or_enhancement": True,
    "verification_is_not_speech_preservation": True,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Stage and evaluate the S05 x-vector/TDNN embedding family with pinned weights on separate identification and verification protocols",
        "evidence_gap": "X-vector embeddings are a considered inventory row and a paper lead only; no exact revision, checkpoint, trial list, gallery or local score exists.",
        "follow_up_ids": ["SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a local speaker identification or verification execution; the linked feasibility row is a bounded scoping lead, not an enabled verifier.",
    },
    {
        "id": "G02",
        "actionable_gap": "Establish a classic statistical speaker-model baseline (GMM-UBM/MAP) with likelihood-ratio scoring and the same trials as the embedding candidate",
        "evidence_gap": "The catalogued classic family has no component row, staged model, enrolment set, likelihood calibration or local score.",
        "follow_up_ids": ["SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a classic speaker-model execution; the linked feasibility row owns embeddings, and the foundation row owns evidence rules, so a classic baseline still needs a new owner.",
    },
    {
        "id": "G03",
        "actionable_gap": "Freeze a rights-qualified, consent-cleared speaker trial list with enrolment, speaker-disjoint held-out speakers and open-set impostors",
        "evidence_gap": "Fixtures are fixed one-pair voice-conversion files, same-clip references or prepared manifests; no consent-cleared identification/verification trial list exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a speaker-verification trial list; the linked research-control rows own manifests and preservation scoring, and the foundation row owns evidence rules.",
    },
    {
        "id": "G04",
        "actionable_gap": "Freeze separate identification and verification metrics with score calibration, gallery size, open-set impostors and an explicit operating point",
        "evidence_gap": "No local rank-1/mAP, EER or minDCF calculation, score distribution, normalisation or threshold policy exists; in-model cosines cannot substitute.",
        "follow_up_ids": ["SDK-FND-EVIDENCE", "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a speaker-verification scorer; the linked foundation and research-control rows own evidence rules and a preservation harness, not identity metrics.",
    },
    {
        "id": "G05",
        "actionable_gap": "Keep Resemblyzer and SpeechBrain ECAPA similarity controls as evidence adapters and calibrate them against a real verification trial list",
        "evidence_gap": "Both controls exist only as partial research-control rows and in-model cosines; no encoder revision, enrolment geometry, impostor distribution or external verification score exists.",
        "follow_up_ids": [
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY",
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has an independent identity score; the linked research-control rows own similarity proxies and the feasibility row owns the embedding candidate.",
    },
    {
        "id": "G06",
        "actionable_gap": "Keep diarization and speaker-change segmentation separate; anonymous cluster IDs must not become enrolled identities",
        "evidence_gap": "Pyannote and BIC are considered annotation rows with no local run, and no mapping from anonymous labels to verified identities exists.",
        "follow_up_ids": [
            "SDK-PYANNOTE-DIARIZATION",
            "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner converts diarization or change boundaries into a verification decision; the linked feasibility rows cover annotation boundaries only.",
    },
    {
        "id": "G07",
        "actionable_gap": "Keep target-speaker extraction and personal VAD separate from identity verification",
        "evidence_gap": "TSE, VoiceFilter and VoiceFilter-Lite are blocked and require an enrollment or target cue; no verification result can inherit from a target-selection task.",
        "follow_up_ids": [
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
            "SDK-VOICEFILTER",
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "No component owner mixes target-conditioned extraction with identity verification; the linked feasibility rows own the adjacent extraction boundary only.",
    },
    {
        "id": "G08",
        "actionable_gap": "Keep in-model voice-conversion speaker cosines adjacent and resolve the unverified RVC target identity before any identity use",
        "evidence_gap": "TokAN, MeanVC2, OpenVoice and RVC report similarity or provenance inside conversion screens; none is an identification or verification execution.",
        "follow_up_ids": [
            "SDK-TOKAN",
            "SDK-MEANVC2",
            "SDK-OPENVOICE-V2",
            "SDK-RVC-V2-VCTK-P226",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a speaker-identity result; the linked implementation rows own conversion models and report only in-model or presumed-identity diagnostics.",
    },
    {
        "id": "G09",
        "actionable_gap": "Run independent blinded human same/different identity judgement on enrolled and impostor pairs",
        "evidence_gap": "No human identity rating exists; the reviewed rows use automated cosines only, so perceptual identity and false acceptance remain unmeasured.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-DNSMOS-P-835-AND-DNSMOS-C",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner collected SPK-05 identity ratings; the linked research-control rows own listening design, preservation scoring and model-free quality proxies, not identity truth.",
    },
    {
        "id": "G10",
        "actionable_gap": "Measure target-device embedding extraction, gallery search, memory, streaming state and deadline behavior",
        "evidence_gap": "Only offline fixed-file or file-mode conversion compute exists; no device embedding latency, gallery-search budget, memory bound or streaming state was measured.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has device or gallery timing evidence; the linked foundation rows own lifecycle/timing and exact-head rules, not a speaker runtime.",
    },
    {
        "id": "G11",
        "actionable_gap": "Define an opt-in provider intake and public exposure path for a speaker-verification component",
        "evidence_gap": "No SPK-05 provider descriptor, installed-archive comparison, default selection or independent review exists.",
        "follow_up_ids": ["SDK-FND-PROVIDER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake; the linked foundation rows own provider boundaries and exact-head evidence.",
    },
    {
        "id": "G12",
        "actionable_gap": "Define consent, retention and biometric-data governance for enrolment, gallery storage and score use before any identity feature",
        "evidence_gap": "No consent record, retention policy, revocation path, privacy review or permitted-use statement covers speaker embeddings or voiceprints.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-FND-EVIDENCE",
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers biometric consent or retention; the linked research-control and foundation rows own manifests, listening design and evidence rules, not privacy approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
    {"task_id": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY", "title": "Resemblyzer speaker-similarity proxy", "mode": "research-control"},
    {"task_id": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY", "title": "SpeechBrains ECAPA / speaker similarity", "mode": "research-control"},
    {"task_id": "SDK-PYANNOTE-DIARIZATION", "title": "pyannote diarization", "mode": "feasibility"},
    {"task_id": "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION", "title": "Bayesian information criterion speaker segmentation", "mode": "feasibility"},
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER", "title": "VoiceFilter", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-TOKAN", "title": "TokAN", "mode": "implementation"},
    {"task_id": "SDK-MEANVC2", "title": "MeanVC2", "mode": "implementation"},
    {"task_id": "SDK-OPENVOICE-V2", "title": "OpenVoice V2", "mode": "implementation"},
    {"task_id": "SDK-RVC-V2-VCTK-P226", "title": "RVC v2 VCTK p226", "mode": "implementation"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-DNSMOS-P-835-AND-DNSMOS-C", "title": "DNSMOS P.835 and DNSMOS-C", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
]

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
)

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified, consent-cleared speaker trial list with genuine/impostor trials, enrolment/gallery splits and speaker-disjoint held-out speakers"},
    {"id": "RG-02", "blocked": True, "requirement": "Separate frozen identification (rank-1/mAP) and verification (EER/minDCF) metrics with score calibration, normalisation and an operating point"},
    {"id": "RG-03", "blocked": True, "requirement": "Independent blinded human identity/similarity judgement on enrolled and impostor pairs"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned target-device embedding extraction, gallery-search timing, memory, streaming state and deadline evidence"},
    {"id": "RG-05", "blocked": True, "requirement": "Staged exact x-vector/TDNN and classic statistical-baseline weights under a locked runtime with approved reference parity"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **SPK-05 — Speaker representation, identification and verification** | Compare speech with enrolled people or a claimed identity. Scope: discovered_extension. |",
        "Identification and verification need separate outputs/metrics. An identity is not a policy for preserving speech.",
    ],
    "research/category_survey/sources.md": [
        "| S05 | [X-vector speaker recognition study](https://www.isca-archive.org/interspeech_2019/snyder19b_interspeech.html) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    ],
    "audio-benchmark-platform/plan/INVENTORY.json": [
        "Evaluate diarization on scored regions and keep anonymous speaker IDs separate from verification.",
    ],
    "research/accent-conversion-20261101/README.md": [
        "| L1 accent | Utterance | Input → output duration | Runtime | RTF | Whisper tiny WER | Resemblyzer cosine |",
        "Speaker cosine is a quick similarity proxy",
        "| Arabic | ABA a0046 | 4.539 → 3.000 s | 78.89 s | 17.38 | 0.00 vs supplied prompt | 0.838 |",
        "| Hindi | RRBI a0391 | 3.490 → 3.180 s | 63.74 s | 18.26 | 0.00 vs source Whisper transcript | 0.798 |",
        "| Korean | HJK a0103 | 3.042 → 2.760 s | 62.55 s | 20.56 | 0.00 vs source Whisper transcript | 0.874 |",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "cosine 0.890 between converted output and p360 using OpenVoice's own reference encoder",
        "target-encoder cosine was 0.669 (40+40) and 0.702 (120+40)",
        "This is an in-model diagnostic; compare only within this pair",
    ],
    "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md": [
        "The cosine score is an in-model diagnostic, not perceptual speaker similarity.",
        "p360 target reference is `data/target_rtvc_p360.flac`",
    ],
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md": [
        "speaker ID 1 presumed to be p226 but unverified",
        "target similarity is unscored",
    ],
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": [
        "It requires a reference utterance/embedding and targets a known speaker in a mixture.",
        "Personal VAD is speech/activity detection conditioned on enrolled speaker",
        "No official weights/runtime; no local score.",
    ],
    "research/voice-enhancement-20261101/evaluation_records.md": [
        "not reference-conditioned target-speaker extraction or real-room acceptance.",
        "No mobile or streaming score exists.",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "RVC VCTK p226 target conversion,partially evaluated",
        "OpenVoice V2 offline tone-color VC,partially evaluated",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/hush/README.md": [
        "Decision: **DEFER**",
        "does not load the ONNX bundle",
    ],
    "docs/task-evidence/survey-det-03/README.md": [
        "source separation (`SPK-01`)",
        "diarization is adjacent, not overlap detection",
    ],
    "docs/task-evidence/survey-spk-01/README.md": [
        "not speaker identity (`SPK-05`)",
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
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
    "identity_claim": False,
    "verification_claim": False,
    "privacy_approval": False,
}

SCOPE: Dict[str, bool] = {
    "task_local_only": True,
    "documentation_and_metadata_only": True,
    "no_new_execution": True,
    "synthetic_only_where_cited": False,
    "real_speech": False,
    "real_corpus": False,
    "weights": False,
    "runtime_invocation": False,
    "listening": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "speaker_identity_claim": False,
    "speaker_identification_claim": False,
    "speaker_verification_claim": False,
    "privacy_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

PRIVACY_GOVERNANCE: Dict[str, bool] = {
    "biometric_enrollment": False,
    "consent_evidence": False,
    "retention_policy": False,
    "revocation_path": False,
    "privacy_approval": False,
    "identity_claim": False,
    "verification_claim": False,
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
        raise MapError("SPK-05 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("SPK-05 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F06 / SPK-05 is not unique")
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
            raise MapError("legacy backlog mismatch: F06/SPK-05/%s" % key)


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
    same_clip = any(c == "adjacent_same_clip_similarity_proxy_historical_local" for c in classes)
    in_model = any(c == "adjacent_in_model_speaker_similarity_historical_local" for c in classes)
    provenance = any(c == "adjacent_identity_provenance_unverified" for c in classes)
    documented = any(c == "source_documented_candidate_not_staged_or_run" for c in classes)
    classic = any(c == "classic_speaker_model_candidate_not_staged_or_run" for c in classes)
    control = any(c == "embedding_similarity_research_control" for c in classes)
    boundary = any(c == "diarization_or_segmentation_boundary" for c in classes)
    extraction = any(c == "enrollment_conditioned_extraction_boundary" for c in classes)
    missing = any(c == "missing_speaker_verification_trial_list" for c in classes)
    prepared = any("prepared" in row["class"].lower() for row in ASSETS)
    expected = {
        "adjacent_same_clip_similarity_proxy_historical_local": same_clip,
        "adjacent_in_model_speaker_similarity_historical_local": in_model,
        "adjacent_identity_provenance_unverified": provenance,
        "source_documented_candidate_not_staged_or_run": documented,
        "classic_speaker_model_candidate_not_staged_or_run": classic,
        "embedding_similarity_research_control": control,
        "diarization_or_segmentation_boundary": boundary,
        "enrollment_conditioned_extraction_boundary": extraction,
        "missing_speaker_verification_trial_list": missing,
        "prepared_manifest_only": prepared,
    }
    for key, value in expected.items():
        if EVIDENCE_CLASSES[key] != value:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "speaker_identification_execution",
        "speaker_verification_execution",
        "verification_metric_eer_mindcf",
        "open_set_trial_list",
        "score_calibration",
        "consent_cleared_biometric_enrollment",
        "real_corpus",
        "weights",
        "runtime_invocation",
        "human_listening_result",
        "device_timing",
        "privacy_approval",
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
        "privacy_and_governance": dict(PRIVACY_GOVERNANCE),
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
    if any(value is not False for value in report["privacy_and_governance"].values()):
        raise MapError("privacy or identity claim is open")
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
