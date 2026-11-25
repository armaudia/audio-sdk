# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-SPK-02.

This module builds a bounded taxonomy/comparison evidence map for the
target-speaker extraction and personalized enhancement category (inventory
category ``SPK-02``, legacy family ``F05``). It reads only pinned, read-only
documents from the enclosing ``audioml`` workspace and the SDK worktree. It
does not load audio, media, weights, runtimes or the network, and it does not
register, expose, enable or qualify any extractor, separator or processor.

All curated records below are documentation mappings, not new measurements.
Adjacent historical local values and source-reported candidate claims are
transcribed verbatim from the pinned documents and labelled with their original
scope. Generic source separation, competing-speaker suppression, personalized
VAD and speaker identification are mapped only as boundaries: none of them is
target-speaker extraction.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-SPK-02"
TITLE = "Review coverage for Target-speaker extraction and personalized enhancement"
CATEGORY_ID = "SPK-02"
LEGACY_FAMILY = "F05"
BRANCH = "swarm/SDK-SURVEY-SPK-02"
BASE_COMMIT = "ba77ffbae0b879c1b4099ccace5065ffb31fffdb"
PROFILE = "Spatial"
COMPONENT = "target-speaker-extraction-personalized-enhancement-evidence-map"
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
# verifies media, weights or annotations that are not present in this task
# directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/cpp-lib-market-benchmark-20261109.md": "d1a4edbf72257ebb989d9639e542cf2c50152e323dc9081f2af868708064a3e7",
    "research/noise_suppression_candidate_census.md": "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md": "d9285694209a54b26db0aa89a27a11b004fa0159d7ee08fc5fff0728c0869545",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/evaluation_records.md": "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "research/voice-enhancement-20261101/findings.md": "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
}

# SDK-worktree-relative public-boundary and merged-evidence pins. They are read
# only to prove that no public surface was touched and to ground curated
# boundaries; no header, contract or report is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/hush/README.md": "0426a592204381138e7fa7ba04f37f4aff92eee6ac75b6bda31f0861c485e76f",
    "docs/task-evidence/survey-det-03/README.md": "672e7a380230f4a1e13e88404deb92b052052bdb05b029a67672fe655ff9593e",
    "docs/task-evidence/survey-det-05/README.md": "69d1e024790a78a6b0e1edc8b94ddfb2d98f88258bc48ff2d839f52052da1f2e",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Speakers and separation",
    "name": "Target-speaker extraction and personalized enhancement",
    "scope": "requested",
    "output_kind": "waveform",
    "purpose": "Recover a selected speaker from a mixture.",
    "method_families": {
        "classic": "Cue-based filtering; statistical family search remains open",
        "ml": "Speaker-conditioned masks/filters; other cue-conditioned extraction",
    },
    "input_output": "Mixture + target cue \u2192 selected speech",
    "live_or_comparison_boundary": (
        "Enrollment, spatial or visual cues are input facets. Identity matching "
        "does not define who the user wants to hear."
    ),
    "source_ids": ["S07", "S50"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "SPK",
    "meaning": "Speakers and separation",
    "category_id": CATEGORY_ID,
    "selected_speaker_waveform_only": True,
    "enrollment_spatial_and_visual_cues_are_input_facets": True,
    "identity_match_does_not_define_desired_speaker": True,
    "not_generic_source_separation": "SPK-01",
    "not_speaker_change_detection": "SPK-03",
    "not_anonymous_diarization": "SPK-04",
    "not_speaker_identification_or_verification": "SPK-05",
    "not_personalized_vad_or_target_activity": "DET-05",
    "not_overlap_detection_or_speaker_count": "DET-03",
    "not_beamforming_or_spatial_filtering_category": "CLN-07",
    "not_background_noise_suppression": "CLN-01",
    "note": (
        "SPK-01 separates sources without deciding which one to keep; SPK-03 "
        "finds change points; SPK-04 labels anonymous speakers; SPK-05 compares "
        "identities. DET-05 emits target-activity scores without a waveform. "
        "Beamforming and spatial filtering (CLN-07) are cue mechanisms, not "
        "identity-conditioned extraction. None of those rows is pooled into an "
        "SPK-02 selected-speech claim."
    ),
}

TSE_BOUNDARY: Dict[str, Any] = {
    "selected_speaker_waveform_recovery_only": True,
    "enrollment_is_an_input_facet_not_a_target_definition": True,
    "spatial_cue_is_an_input_facet_not_an_identity": True,
    "visual_cue_is_an_input_facet_not_an_identity": True,
    "identity_matching_does_not_define_preferred_speaker": True,
    "generic_separation_is_not_target_selection": True,
    "competing_speaker_suppression_is_not_target_extraction": True,
    "target_mask_ratio_without_target_quality_is_insufficient": True,
    "personal_vad_activity_is_not_a_waveform": True,
    "enrollment_conditioned_execution_present": False,
    "clean_target_reference_corpus_present": False,
    "real_overlap_corpus_present": False,
    "impostor_or_target_absent_negative_set_present": False,
    "ml_weights_present": False,
    "ml_runtime_present": False,
    "target_selected_output_measured": False,
    "human_listening_result_present": False,
    "device_timing_present": False,
    "independent_heldout_benchmark_present": False,
    "public_default_present": False,
    "release_approved": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S07",
        "title": "VoiceFilter target-speaker extraction paper",
        "url": (
            "https://research.google/pubs/voicefilter-targeted-voice-separation-by-"
            "speaker-conditioned-spectrogram-masking/"
        ),
        "access_scope": "direct",
        "mapped_components": ["voicefilter", "voicefilter-lite-personal-vad"],
        "gap_ids": ["G01", "G02"],
        "finding": (
            "Direct paper lead for a speaker-conditioned spectrogram-mask system "
            "that uses a reference utterance or embedding to recover a known "
            "speaker from a mixture. The pinned candidate matrix records the "
            "original Google weights/runtime as not open, so the `voicefilter` "
            "and `voicefilter-lite-personal-vad` rows are blocked. No reference "
            "encoder, enrollment protocol, mixture cohort, clean target "
            "reference or local extraction score is present here."
        ),
    },
    {
        "source_id": "S50",
        "title": "Audio-visual target-speaker enhancement paper",
        "url": "https://arxiv.org/abs/2507.21448",
        "access_scope": "search excerpt in prior brainstorm",
        "mapped_components": ["target-speaker-extraction-family"],
        "gap_ids": ["G03", "G04"],
        "finding": (
            "A search excerpt from a prior brainstorm, not a direct paper read "
            "or a local execution. It describes cue-conditioned extraction that "
            "can include a visual facet. No video track, visual encoder, "
            "checkpoint, multimodal corpus, license review or result is staged; "
            "the visual facet remains separate from audio-only enrollment."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Cue-based filtering with spatial or statistical filters",
        "components": [
            "delay-and-sum-beamformer",
            "mvdr-beamforming",
            "auxiva",
            "3d-microphone-spatial-time-alignment",
        ],
        "gap_ids": ["G05", "G06"],
        "status": "spatial_cue_filtering_only_no_target_selection_execution",
        "boundary": (
            "Delay-and-sum, MVDR, AuxIVA and 3D alignment are catalogued "
            "reference or considered rows. They filter a spatial direction or "
            "separate sources; they do not consume an enrolled voice cue and do "
            "not emit a selected-speaker waveform. No calibrated array, target "
            "direction truth, target-selected output or matched extraction "
            "cohort exists."
        ),
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Statistical target-speaker family search (open)",
        "components": [],
        "gap_ids": ["G07"],
        "status": "no_local_component_or_execution_in_reviewed_records",
        "boundary": (
            "The catalogued classic string explicitly leaves the statistical "
            "family search open. No GMM/HMM/PLDA-conditioned extractor, "
            "selected statistical family, target model, cohort or execution is "
            "catalogued, so the open search is recorded instead of being filled "
            "with a generic denoiser."
        ),
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Speaker-conditioned masks/filters (VoiceFilter family, S07)",
        "components": ["voicefilter", "voicefilter-lite-personal-vad"],
        "gap_ids": ["G01", "G02"],
        "status": "candidate_only_blocked_no_local_execution",
        "boundary": (
            "Both catalogued dedicated rows are blocked. Original VoiceFilter "
            "weights/runtime are not open; VoiceFilter-Lite is vendor-reported "
            "and no deployable checkpoint or enrolled-speaker mixture with a "
            "clean target reference is staged. Personal VAD is an activity "
            "decision, not a waveform extractor."
        ),
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Other cue-conditioned extraction (spatial or visual, S50)",
        "components": ["target-speaker-extraction-family"],
        "gap_ids": ["G03", "G04"],
        "status": "candidate_only_blocked_no_local_execution",
        "boundary": (
            "The family-level row is blocked: no selected extraction model or "
            "test corpus with enrollment, overlapping speakers and clean target "
            "references. S50 is only a search excerpt, and a spatial or visual "
            "cue modality cannot be conflated with audio-only enrollment."
        ),
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Adjacent generic separation and multichannel extraction",
        "components": ["conv-tasnet", "beam-tasnet-beam-guided-tasnet", "spatialnet"],
        "gap_ids": ["G08", "G09"],
        "status": "candidate_only_or_blocked_no_target_selection_execution",
        "boundary": (
            "Conv-TasNet is considered; Beam-TasNet and SpatialNet are blocked. "
            "Separation returns several sources with permutation, source-order "
            "and source-count questions, and it does not decide which source is "
            "the requested speaker. No weights, array, target cue or "
            "target-selected result is staged."
        ),
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Adjacent causal competing-speaker suppression without enrollment",
        "components": ["hush"],
        "gap_ids": ["G10"],
        "status": "adjacent_local_suppression_only",
        "boundary": (
            "Hush is a causal competing-speaker suppressor with no enrollment "
            "prompt. On the EARS synthetic screen and the AMI speaker-dominant "
            "diagnostic it raised the target/masker projection ratio while "
            "lowering target SI-SDR and STOI. That is target damage under "
            "primary/background suppression, not reference-conditioned "
            "extraction."
        ),
    },
    {
        "family_id": "MF-M5",
        "branch": "ml",
        "family": "Adjacent speaker-embedding and similarity cue suppliers",
        "components": [
            "x-vector-speaker-embeddings",
            "resemblyzer-speaker-similarity-proxy",
            "speechbrains-ecapa-speaker-similarity",
        ],
        "gap_ids": ["G11"],
        "status": "adjacent_cue_supplier_only_no_extraction_execution",
        "boundary": (
            "Embeddings and similarity scores can supply an enrollment cue, but "
            "an identity score is not a selected waveform. In-model cosines are "
            "encoder-specific diagnostics, and no shared enrolled cohort, "
            "calibrated threshold or extractor is evaluated."
        ),
    },
    {
        "family_id": "MF-M6",
        "branch": "ml",
        "family": "Adjacent vendor voice-isolation output scoring",
        "components": ["krisp-voice-isolation-public-output-scoring"],
        "gap_ids": ["G12"],
        "status": "source_reported_vendor_output_only",
        "boundary": (
            "The pinned vendor benchmark scores its own Voice Isolation feature "
            "on target-speaker segments. It is a company-produced external "
            "comparison with no local runtime, no matched local corpus and no "
            "independent reproduction, so no result transfers to this map."
        ),
    },
]

# component_id, task and evidence_status are checked against plan/INVENTORY.json.
# Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "voicefilter", "evidence_status": "blocked", "task": "SDK-VOICEFILTER"},
    {"component_id": "target-speaker-extraction-family", "evidence_status": "blocked", "task": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"},
    {"component_id": "voicefilter-lite-personal-vad", "evidence_status": "blocked", "task": "SDK-VOICEFILTER-LITE-PERSONAL-VAD"},
    {"component_id": "hush", "evidence_status": "partial", "task": "SDK-HUSH"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "resemblyzer-speaker-similarity-proxy", "evidence_status": "partial", "task": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"},
    {"component_id": "speechbrains-ecapa-speaker-similarity", "evidence_status": "partial", "task": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY"},
    {"component_id": "conv-tasnet", "evidence_status": "considered", "task": "SDK-CONV-TASNET"},
    {"component_id": "beam-tasnet-beam-guided-tasnet", "evidence_status": "blocked", "task": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET"},
    {"component_id": "spatialnet", "evidence_status": "blocked", "task": "SDK-SPATIALNET"},
    {"component_id": "delay-and-sum-beamformer", "evidence_status": "considered", "task": "SDK-DELAY-AND-SUM-BEAMFORMER"},
    {"component_id": "mvdr-beamforming", "evidence_status": "considered", "task": "SDK-MVDR-BEAMFORMING"},
    {"component_id": "auxiva", "evidence_status": "considered", "task": "SDK-AUXIVA"},
    {"component_id": "3d-microphone-spatial-time-alignment", "evidence_status": "considered", "task": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT"},
    {"component_id": "pyannote-diarization", "evidence_status": "considered", "task": "SDK-PYANNOTE-DIARIZATION"},
    {"component_id": "krisp-voice-isolation-public-output-scoring", "evidence_status": "partial", "task": "SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING"},
    {"component_id": "si-sdr-sdr-and-snr", "evidence_status": "evaluated", "task": "SDK-SI-SDR-SDR-AND-SNR"},
    {"component_id": "stoi-estoi", "evidence_status": "evaluated", "task": "SDK-STOI-ESTOI"},
    {"component_id": "dnsmos-p-835-and-dnsmos-c", "evidence_status": "evaluated", "task": "SDK-DNSMOS-P-835-AND-DNSMOS-C"},
    {"component_id": "vctk-dns2020-ami-ears-and-smard-evidence-manifests", "evidence_status": "evaluated", "task": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS"},
    {"component_id": "ears-preservation-screen-and-scorer-harness", "evidence_status": "evaluated", "task": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS"},
    {"component_id": "vadtoolkit-and-ami-scoring-tooling", "evidence_status": "partial", "task": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "VoiceFilter speaker-conditioned spectrogram-mask paper (S07)",
        "class": "source_only_tse_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Method context only: a reference utterance/embedding conditions a mask for a known speaker; original weights/runtime are not open and no local reference encoder, mixture or score is staged.",
    },
    {
        "id": "CI-2",
        "input": "Audio-visual target-speaker enhancement paper (S50) search excerpt",
        "class": "source_excerpt_audiovisual_tse_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "A prior-brainstorm search excerpt, not a direct read or execution; no video track, visual encoder, checkpoint, multimodal corpus or result exists.",
    },
    {
        "id": "CI-3",
        "input": "VoiceFilter catalogued candidate row",
        "class": "source_reported_tse_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Unavailable/blocked: original Google weights/runtime are not open; third-party substitutes are separate candidates and none is staged.",
    },
    {
        "id": "CI-4",
        "input": "VoiceFilter-Lite / personal VAD catalogued candidate row",
        "class": "source_reported_tse_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Unavailable/blocked: no deployable local checkpoint and no enrolled-speaker mixtures with clean target references; personal VAD is activity, not a waveform.",
    },
    {
        "id": "CI-5",
        "input": "Target-speaker extraction family catalogued candidate row",
        "class": "source_reported_tse_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Unavailable/blocked: no selected extraction model or test corpus with enrollment, overlapping speakers and clean target references.",
    },
    {
        "id": "CI-6",
        "input": "Adjacent Hush EARS primary/background suppression screen, 30 pairs x 3 SIR = 90 mixtures",
        "class": "adjacent_local_primary_background_suppression",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "boundary": "Adjacent suppression only: target/masker ratio +8.14/+8.08/+8.46 dB, target SI-SDR -9.33/-14.54/-20.23 dB, STOI -.141/-.176/-.197; no speaker IDs, no enrollment prompt and no clean target extraction.",
    },
    {
        "id": "CI-7",
        "input": "Adjacent Hush AMI ES2004a speaker-dominant diagnostic, 7 directed pairs x 3 SIR = 21 mixtures",
        "class": "adjacent_local_speaker_dominant_suppression",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "boundary": "Constructed non-overlap turn proxies from one mono meeting: target SI-SDR -13.17/-18.41/-24.18 dB, STOI -.193/-.200/-.207; ratio gains +3.70/+7.33/+3.37 dB with intervals including zero and no isolated references.",
    },
    {
        "id": "CI-8",
        "input": "Adjacent in-model speaker-similarity cosines from voice-conversion evaluations",
        "class": "adjacent_local_in_model_speaker_similarity_diagnostic",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "Encoder-specific identity diagnostics (0.890 OpenVoice; 0.669 and 0.702 target encoder), not verification, not comparable across encoders and not extraction.",
    },
    {
        "id": "CI-9",
        "input": "Krisp Voice Isolation 2026 public vendor benchmark",
        "class": "source_reported_vendor_voice_isolation_benchmark",
        "source_pin": "research/cpp-lib-market-benchmark-20261109.md",
        "boundary": "Company-produced test of its own feature: 265 real recordings, 47 speakers, WER 23.24%->6.24% and DNSMOS-C 3.40->3.81 on target-speaker segments; no local runtime, matched cohort or independent reproduction.",
    },
    {
        "id": "CI-10",
        "input": "Adjacent spatial, separation and suppression components without a target-selected execution",
        "class": "adjacent_spatial_and_generic_separation",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Delay-and-sum, MVDR, AuxIVA, Conv-TasNet, Beam-TasNet and SpatialNet are considered/blocked rows with no target cue, weights or selected-speaker output; Hush is partial but unenrolled.",
    },
    {
        "id": "CI-11",
        "input": "Missing rights-qualified enrolled-speaker corpus with clean target references, real overlap and target-absent negatives",
        "class": "missing_spk02_enrollment_cohort",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Absence is recorded as missing, not as an empty negative set; no extraction accuracy, leakage or target false-rejection claim follows.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "identity / untouched mixture",
        "role": "The mixture itself is the preservation baseline; a selected-output claim must justify target gain without unexplained target damage.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "id": "CT-2",
        "name": "generic denoiser control (DeepFilterNet3)",
        "role": "A matched generic enhancement control shows what ordinary denoising does to target SI-SDR/STOI; it has no speaker cue and is not extraction.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "id": "CT-3",
        "name": "unenrolled competing-speaker suppressor (Hush)",
        "role": "Hush attenuates a primary/background mixture without an enrollment prompt; it is a suppression control, not a target-selection candidate.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "id": "CT-4",
        "name": "degenerate target-only and target-absent diagnostics",
        "role": "Always-emit-target and always-emit-non-target behaviour must expose target false acceptance and target false rejection; neither is a product candidate.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-5",
        "name": "target/masker ratio versus target-quality separation",
        "role": "A better target/masker projection ratio does not compensate for lower target SI-SDR or STOI; the two outcomes are reported separately.",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "id": "CT-6",
        "name": "cue-facet separation (enrollment / spatial / visual)",
        "role": "Enrollment, spatial and visual cues are distinct input facets and cannot be compared or pooled without a declared protocol.",
        "source_pin": "audio_categories.md",
    },
    {
        "id": "CT-7",
        "name": "unknown and unenrolled region handling",
        "role": "Time without an enrolled target or annotation is unknown, never automatically non-target; an unenrolled region is not a negative label.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-8",
        "name": "sample-count, finite-output and identity preservation",
        "role": "Every extracted output must keep the declared sample count, stay finite and avoid hidden audio mutation; identity PCM remains the fallback.",
        "source_pin": "docs/task-evidence/hush/README.md",
    },
    {
        "id": "CT-9",
        "name": "generic separation permutation and source-count control",
        "role": "Separation output order, permutation and source count must be resolved before any source can be called the requested speaker.",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "VoiceFilter target-speaker extraction paper (S07)",
        "class": "external_documentation",
        "status": "Method documentation only; no official weights, runtime, reference encoder or code license is staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Audio-visual target-speaker enhancement paper (S50)",
        "class": "external_search_excerpt",
        "status": "Search excerpt from a prior brainstorm only; no paper read, visual encoder, video track or corpus",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Original VoiceFilter weights and runtime",
        "class": "missing_restricted",
        "status": "Not open and not staged; a third-party substitute would be a different candidate with its own identity and terms",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "VoiceFilter-Lite / personal VAD deployable checkpoint",
        "class": "missing_restricted",
        "status": "No deployable local checkpoint, mobile runtime or enrolled-speaker mixture is staged; vendor size/latency claims only",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "Adjacent Hush checkpoint and deployment library",
        "class": "research_model_partial",
        "status": "Apache-2.0 source commit and model/runtime hashes are recorded in the pinned report; no enrollment input exists and the row stays partial",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "asset": "EARS blind audio subset used for synthetic target/masker pairs",
        "class": "research_audio_noncommercial",
        "status": "CC BY-NC 4.0 per the pinned report; 30 target/masker source pairs, no speaker metadata and no isolated enrolled target",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
    },
    {
        "asset": "AMI ES2004a mono headset mix and participant-turn annotations",
        "class": "research_audio",
        "status": "CC BY 4.0 per the pinned report; one meeting, no isolated participant tracks, turn proxies only",
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
    },
    {
        "asset": "Krisp Voice Isolation public benchmark outputs",
        "class": "external_vendor_benchmark",
        "status": "Vendor-published dataset and outputs; usable only within its terms and never a local extraction result",
        "source_pin": "research/cpp-lib-market-benchmark-20261109.md",
    },
    {
        "asset": "Rights-qualified enrolled-speaker corpus with clean target references, real overlap and target-absent negatives",
        "class": "missing",
        "status": "Not present; absence is explicit and is not an empty negative set",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Hush EARS primary/background suppression screen",
        "outcome_class": "adjacent_primary_background_suppression_local",
        "component_ids": ["hush", "si-sdr-sdr-and-snr", "stoi-estoi"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "values": {
            "target_source_pairs": 30,
            "sir_strata": 3,
            "mixtures": 90,
            "target_masker_ratio_gain_db": [8.14, 8.08, 8.46],
            "delta_target_si_sdr_db": [-9.33, -14.54, -20.23],
            "delta_target_stoi": [-0.141, -0.176, -0.197],
            "mean_transform_rtf": [0.0282, 0.0278, 0.0276],
            "observed_delay_ms": 10.0,
            "finite_hash_verified_outputs": 90,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent primary/background suppression on 30 EARS source pairs at "
            "+12/+18/+24 dB SIR; the exact C API accepts no enrollment or "
            "reference waveform, EARS has no speaker identities and the mix is "
            "synthetic with no room or natural overlap. It does not measure "
            "target-speaker extraction; not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Hush AMI ES2004a speaker-dominant turn diagnostic",
        "outcome_class": "adjacent_speaker_dominant_suppression_local",
        "component_ids": ["hush", "si-sdr-sdr-and-snr", "stoi-estoi"],
        "source_pin": "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "values": {
            "directed_speaker_pairs": 7,
            "sir_strata": 3,
            "mixtures": 21,
            "delta_target_si_sdr_db": [-13.17, -18.41, -24.18],
            "delta_target_stoi": [-0.193, -0.200, -0.207],
            "target_masker_ratio_gain_db": [3.70, 7.33, 3.37],
            "ratio_interval_includes_zero": True,
            "mean_transform_rtf": 0.0292,
            "p95_transform_rtf": 0.0334,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent speaker-dominant diagnostic built from seven directed "
            "participant-turn pairs in one mono AMI meeting; crops are not "
            "isolated clean references, the mixture is constructed rather than "
            "naturally simultaneous, and Hush receives no speaker prompt. It "
            "does not test enrollment-conditioned target-speaker extraction; "
            "not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "VoiceFilter conditions a spectrogram mask on a reference utterance/embedding to recover a known speaker from a mixture",
        "class": "source_reported_tse_candidate",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Paper method only; original Google weights/runtime are not open, and no reference encoder, mixture cohort or local score is staged.",
    },
    {
        "id": "RO-2",
        "claim": "Audio-visual target-speaker enhancement can use a visual cue in addition to audio",
        "class": "source_excerpt_audiovisual_tse_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Prior-brainstorm search excerpt only; no paper read, video track, visual encoder, checkpoint, corpus or result follows.",
    },
    {
        "id": "RO-3",
        "claim": "VoiceFilter-Lite is described as a roughly 2.2 MB quantized on-device model, and personal VAD is speech/activity detection conditioned on an enrolled speaker",
        "class": "source_reported_tse_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Vendor-reported size claim and method distinction only; no deployable checkpoint, runtime or enrolled mixture is staged, and an activity decision is not a waveform.",
    },
    {
        "id": "RO-4",
        "claim": "Target-speaker extraction may condition on an enrollment voice, spatial direction or visual cue and is a different task from denoising",
        "class": "source_reported_tse_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Task-family context only; no concrete cue-conditioned model, corpus or local result is selected.",
    },
    {
        "id": "RO-5",
        "claim": "Krisp reports a 2026 Voice Isolation benchmark with WER 23.24%->6.24% and DNSMOS-C 3.40->3.81 on target-speaker segments",
        "class": "source_reported_vendor_voice_isolation_benchmark",
        "source_pin": "research/cpp-lib-market-benchmark-20261109.md",
        "boundary": "Company-produced self-benchmark over 265 recordings and 47 speakers; no local runtime, matched local cohort or independent reproduction, so the result is not transferred.",
    },
    {
        "id": "RO-6",
        "claim": "Hush is a causal 16 kHz competing-speaker suppressor with an Apache-2.0 checkpoint described as about 8 MB and CPU-capable",
        "class": "source_reported_candidate_documentation",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Candidate documentation and local partial suppression evidence only; no enrollment prompt, speaker IDs, natural overlap or target extraction result.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "geometry_layout_and_permissions": "No synchronized array, geometry, layout or permission record is staged; the EARS screen is mono synthetic and the AMI diagnostic is one mono headset mix.",
        "source_target_reference_conditions": "EARS has known clean target and masker waveforms but no speaker identities; AMI has turn labels but only speaker-dominant proxies. Neither has an enrolled target or isolated clean reference.",
        "task_matched_heldout_labels": "No enrolled-speaker held-out labels, target-absent set or clean target reference cohort exists.",
        "extraction_vs_localization_and_activity": "Beamformers, Conv-TasNet and Hush rows are considered or adjacent suppression evidence; none produces a target-selected waveform on a matched cohort.",
        "leakage": "No off-target leakage, residual masker or target over-suppression measurement exists for any candidate.",
        "target_damage": "Hush lowers target SI-SDR by 9.33-20.23 dB and STOI by .141-.197 on EARS, and by 13.17-24.18 dB / .193-.207 on AMI; target damage is the measured outcome, not a pass.",
        "channel_loss_and_reference_changes": "No channel loss, room change, microphone change or reference-condition change is measured.",
        "exact_source_intervals": "No source intervals, sample-aligned target masks, clock or extraction state are pinned.",
        "state_memory_and_content_timing": "Only desktop transform RTF about .028, model load and process RSS are recorded for Hush; extraction availability, lookahead, memory and device timing are unmeasured.",
        "preserved_pcm_identity": "No extracted output is staged; any future extractor must preserve declared sample count, finite values and the identity fallback.",
    },
    "blocked": [
        "Rights-qualified enrolled-speaker corpus with clean target references, real overlap and target-absent negatives",
        "Frozen cue-conditioned protocol (enrollment/spatial/visual) with exact checkpoint, weights, runtime and per-weight terms",
        "Matched identity, generic-denoiser and unenrolled-suppressor controls with target preservation, off-target suppression, target false rejection and uncertainty",
        "Synchronized multichannel array, geometry, reference timing and channel calibration wherever spatial cues are claimed",
        "Paced extraction latency, memory, sample-count preservation, nonfinite handling and target-device timing",
        "Independent listening or authorized perceptual/speech-recognition evaluation of extracted target speech and over-suppression",
        "Explicit public default selection and provider/opt-in intake approval",
        "Release approval; DEFER remains in force until every gate is closed",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "source_only_tse_protocol": True,
    "source_excerpt_audiovisual_tse_protocol": True,
    "source_reported_tse_candidate": True,
    "source_reported_candidate_documentation": True,
    "source_reported_vendor_voice_isolation_benchmark": True,
    "adjacent_primary_background_suppression_local": True,
    "adjacent_speaker_dominant_suppression_local": True,
    "adjacent_in_model_speaker_similarity_diagnostic": True,
    "adjacent_spatial_and_generic_separation": True,
    "spk02_local_extraction_execution": False,
    "enrollment_conditioned_execution": False,
    "target_speaker_extraction_accuracy_claim": False,
    "clean_target_reference_accuracy_claim": False,
    "real_enrolled_corpus": False,
    "impostor_or_target_absent_negative_set": False,
    "real_overlap_corpus": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "public_default_claim": False,
    "release_claim": False,
}

# True evidence classes must be backed by at least one row class; false classes
# must not be backed. This keeps a missing result from being promoted.
CLASS_BACKING: Dict[str, List[str]] = {
    "source_only_tse_protocol": ["source_only_tse_protocol"],
    "source_excerpt_audiovisual_tse_protocol": ["source_excerpt_audiovisual_tse_protocol"],
    "source_reported_tse_candidate": ["source_reported_tse_candidate"],
    "source_reported_candidate_documentation": ["source_reported_candidate_documentation"],
    "source_reported_vendor_voice_isolation_benchmark": [
        "source_reported_vendor_voice_isolation_benchmark"
    ],
    "adjacent_primary_background_suppression_local": [
        "adjacent_local_primary_background_suppression",
        "adjacent_primary_background_suppression_local",
    ],
    "adjacent_speaker_dominant_suppression_local": [
        "adjacent_local_speaker_dominant_suppression",
        "adjacent_speaker_dominant_suppression_local",
    ],
    "adjacent_in_model_speaker_similarity_diagnostic": [
        "adjacent_local_in_model_speaker_similarity_diagnostic"
    ],
    "adjacent_spatial_and_generic_separation": ["adjacent_spatial_and_generic_separation"],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Select and pin one concrete target-speaker extractor with an exact checkpoint, cue modality and runtime",
        "evidence_gap": "The three dedicated SPK-02 rows are blocked: original VoiceFilter weights/runtime are not open, VoiceFilter-Lite has no deployable checkpoint, and the extraction family has no selected model or cohort.",
        "follow_up_ids": [
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
            "SDK-VOICEFILTER",
            "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The three feasibility rows are scoping leads only; none is enabled, staged or qualified by this map.",
    },
    {
        "id": "G02",
        "actionable_gap": "Resolve VoiceFilter/VoiceFilter-Lite artifact availability, license and reference-encoder terms",
        "evidence_gap": "VoiceFilter's original Google weights/runtime are not open and VoiceFilter-Lite is vendor-reported; no reference encoder, checkpoint digest, runtime or per-weight terms is staged.",
        "follow_up_ids": ["SDK-VOICEFILTER", "SDK-VOICEFILTER-LITE-PERSONAL-VAD"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are scoping leads; a third-party substitute would be a distinct candidate with its own identity and terms.",
    },
    {
        "id": "G03",
        "actionable_gap": "Obtain a rights-qualified enrolled-speaker corpus with clean target references, real overlap and target-absent negatives",
        "evidence_gap": "No enrolled mixture, clean target reference, natural overlap label or impostor/target-absent set exists; the EARS set lacks speaker IDs and the AMI crops are not isolated references.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-02 enrollment-corpus owner exists; the linked evidence-manifest and foundation rows own manifests and asset rules, not an enrolled extraction cohort.",
    },
    {
        "id": "G04",
        "actionable_gap": "Freeze cue-conditioned protocols separately for enrollment, spatial and visual cues",
        "evidence_gap": "The category names all three cue facets, but no protocol separates them and S50 supplies only a visual-cue search excerpt with no multimodal material.",
        "follow_up_ids": [
            "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY",
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are cue and geometry scoping leads; none freezes an SPK-02 cue protocol or stages a multimodal cohort.",
    },
    {
        "id": "G05",
        "actionable_gap": "Assemble and calibrate a spatial cue-filtering baseline on synchronized channels",
        "evidence_gap": "Delay-and-sum, MVDR, AuxIVA and 3D alignment are considered only; no calibrated array, reference timing, target direction truth or target-selected output exists.",
        "follow_up_ids": [
            "SDK-DELAY-AND-SUM-BEAMFORMER",
            "SDK-MVDR-BEAMFORMING",
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-SURVEY-CLN-07",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility and taxonomy rows are spatial-cue scoping leads; a beamformer filters direction and is not identity-conditioned extraction.",
    },
    {
        "id": "G06",
        "actionable_gap": "Search and select the open classic statistical target-extraction family",
        "evidence_gap": "The catalogued classic string explicitly leaves the statistical family search open; no GMM/HMM/PLDA-conditioned extractor, target model, cohort or execution exists.",
        "follow_up_ids": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-02 statistical-extraction owner exists; the linked foundation rows own provider intake and evidence rules, not a target extractor.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure target preservation, off-target suppression and target false rejection with a frozen scorer",
        "evidence_gap": "No matched extraction score exists; Hush rows report target damage under suppression, and no target-absent or impostor false-acceptance rate is measured.",
        "follow_up_ids": [
            "SDK-SI-SDR-SDR-AND-SNR",
            "SDK-STOI-ESTOI",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-02 extraction scorer exists; the linked research-control rows own paired metrics, preservation scoring and AMI tooling, not a target-extraction protocol.",
    },
    {
        "id": "G08",
        "actionable_gap": "Separate generic separation and permutation from target selection and score leakage",
        "evidence_gap": "Conv-TasNet, Beam-TasNet and SpatialNet separate or enhance without deciding which source is the requested speaker; no permutation, source-count or target-leakage test exists.",
        "follow_up_ids": [
            "SDK-CONV-TASNET",
            "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET",
            "SDK-SPATIALNET",
            "SDK-SURVEY-SPK-01",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked separation feasibility rows are scoping leads; generic separation is a boundary, not an inherited SPK-02 result.",
    },
    {
        "id": "G09",
        "actionable_gap": "Establish a synchronized multichannel array and reference timing for spatial-cue claims",
        "evidence_gap": "No array geometry, channel calibration, reference channel or synchronized recording exists; Beam-TasNet and SpatialNet are blocked for exactly this reason.",
        "follow_up_ids": [
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-DELAY-AND-SUM-BEAMFORMER",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are geometry and reference-beamforming leads; neither stages an SPK-02 array or target-selected result.",
    },
    {
        "id": "G10",
        "actionable_gap": "Do not present competing-speaker suppression as enrollment-conditioned extraction; keep Hush partial",
        "evidence_gap": "Hush has no enrollment prompt and no speaker identities; it improved target/masker ratio while lowering target SI-SDR and STOI on both adjacent screens.",
        "follow_up_ids": ["SDK-HUSH", "SDK-SURVEY-SPK-01"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-02 suppression-analysis owner exists; the linked Hush implementation and separation taxonomy rows keep suppression partial and separate from extraction.",
    },
    {
        "id": "G11",
        "actionable_gap": "Calibrate speaker-embedding similarity as a cue and keep it distinct from identity verification",
        "evidence_gap": "X-vector is considered and the two similarity rows are partial research controls; no shared enrolled cohort, calibrated threshold, cue-to-extractor handoff or identity verification exists.",
        "follow_up_ids": [
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY",
            "SDK-SURVEY-SPK-05",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked embedding and similarity rows are cue-supplier leads; an identity score is not a selected waveform and in-model cosines are not verification.",
    },
    {
        "id": "G12",
        "actionable_gap": "Keep vendor voice-isolation benchmark claims external and untransferred",
        "evidence_gap": "The Krisp benchmark is company-produced over its own feature and outputs; no local runtime, matched local cohort or independent reproduction exists.",
        "follow_up_ids": ["SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-02 vendor-evaluation owner exists; the linked research-control and foundation rows own permitted output scoring and evidence rules, not a local extraction claim.",
    },
    {
        "id": "G13",
        "actionable_gap": "Measure paced extraction latency, memory, sample-count preservation and nonfinite behavior on target devices",
        "evidence_gap": "Only desktop Hush transform RTF about .028, model load and process RSS exist; no extraction availability, lookahead, sample-count check, nonfinite handling or device timing is measured.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated SPK-02 timing owner exists; the linked foundation rows own fixed-frame lifecycle and evidence acceptance, not an extraction runtime.",
    },
    {
        "id": "G14",
        "actionable_gap": "Keep target extraction separate from muting, generic denoising, personalized VAD, diarization and identity policy",
        "evidence_gap": "The category boundary says identity matching does not define who the user wants to hear; no component owns both selected extraction and an audio-mutating or identity decision.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-05",
            "SDK-SURVEY-SPK-01",
            "SDK-SURVEY-SPK-04",
            "SDK-SURVEY-SPK-05",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No single component owns both extraction and a policy decision; the linked taxonomy rows keep personalized VAD, separation, diarization and identity separate.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER", "title": "VoiceFilter", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD", "title": "VoiceFilter-Lite / personal VAD", "mode": "feasibility"},
    {"task_id": "SDK-HUSH", "title": "Hush", "mode": "implementation"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
    {"task_id": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY", "title": "Resemblyzer speaker-similarity proxy", "mode": "research-control"},
    {"task_id": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY", "title": "SpeechBrains ECAPA / speaker similarity", "mode": "research-control"},
    {"task_id": "SDK-CONV-TASNET", "title": "Conv-TasNet", "mode": "feasibility"},
    {"task_id": "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET", "title": "Beam-TasNet / Beam-Guided TasNet", "mode": "feasibility"},
    {"task_id": "SDK-SPATIALNET", "title": "SpatialNet", "mode": "feasibility"},
    {"task_id": "SDK-DELAY-AND-SUM-BEAMFORMER", "title": "Delay-and-sum beamformer", "mode": "feasibility"},
    {"task_id": "SDK-MVDR-BEAMFORMING", "title": "MVDR beamforming", "mode": "feasibility"},
    {"task_id": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT", "title": "3D microphone spatial / time alignment", "mode": "feasibility"},
    {"task_id": "SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING", "title": "Krisp Voice Isolation public output scoring", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE", "title": "LibriSpeech and Common Voice evidence intake", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-SI-SDR-SDR-AND-SNR", "title": "SI-SDR, SDR and SNR", "mode": "research-control"},
    {"task_id": "SDK-STOI-ESTOI", "title": "STOI / ESTOI", "mode": "research-control"},
    {"task_id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING", "title": "VADToolkit and AMI scoring tooling", "mode": "research-control"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-SURVEY-SPK-01", "title": "Review coverage for Generic speech/source separation", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-04", "title": "Review coverage for Anonymous speaker diarization", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-05", "title": "Review coverage for Speaker representation, identification and verification", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-DET-05", "title": "Review coverage for Target-speaker / personalized VAD", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-CLN-07", "title": "Review coverage for Beamforming and spatial filtering", "mode": "taxonomy"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "RG-01",
        "blocked": True,
        "requirement": "Rights-qualified enrolled-speaker corpus with clean target references, real overlap and target-absent negatives",
    },
    {
        "id": "RG-02",
        "blocked": True,
        "requirement": "Frozen cue-conditioned protocol (enrollment/spatial/visual) with exact checkpoint, weights, runtime and per-weight terms",
    },
    {
        "id": "RG-03",
        "blocked": True,
        "requirement": "Matched identity, generic-denoiser and unenrolled-suppressor controls with target preservation, off-target suppression, target false rejection and uncertainty",
    },
    {
        "id": "RG-04",
        "blocked": True,
        "requirement": "Synchronized multichannel array, geometry, reference timing and channel calibration wherever spatial cues are claimed",
    },
    {
        "id": "RG-05",
        "blocked": True,
        "requirement": "Paced extraction latency, memory, sample-count preservation, nonfinite handling and target-device timing",
    },
    {
        "id": "RG-06",
        "blocked": True,
        "requirement": "Independent listening or authorized perceptual/speech-recognition evaluation of extracted target speech and over-suppression",
    },
    {
        "id": "RG-07",
        "blocked": True,
        "requirement": "Explicit public default selection and provider/opt-in intake approval",
    },
    {
        "id": "RG-08",
        "blocked": True,
        "requirement": "Release approval; DEFER remains in force until every gate is closed",
    },
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **SPK-02 \u2014 Target-speaker extraction and personalized enhancement** | Recover a selected speaker from a mixture. Scope: requested. | Cue-based filtering; statistical family search remains open | Speaker-conditioned masks/filters; other cue-conditioned extraction | Mixture + target cue \u2192 selected speech | Enrollment, spatial or visual cues are input facets. Identity matching does not define who the user wants to hear. | [S07](https://research.google/pubs/voicefilter-targeted-voice-separation-by-speaker-conditioned-spectrogram-masking/), [S50](https://arxiv.org/abs/2507.21448) |",
    ],
    "research/category_survey/sources.md": [
        "| S07 | [VoiceFilter target-speaker extraction paper](https://research.google/pubs/voicefilter-targeted-voice-separation-by-speaker-conditioned-spectrogram-masking/) | analysis | direct |",
        "| S50 | [Audio-visual target-speaker enhancement paper](https://arxiv.org/abs/2507.21448) | root | search excerpt in prior brainstorm |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Spatial and speaker,VoiceFilter,unavailable/blocked,Original Google weights/runtime are not open; third-party substitutes are separate candidates,Multichannel reference; target extraction metrics,research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "Spatial and speaker,VoiceFilter-Lite / personal VAD,unavailable/blocked,No deployable local checkpoint and no enrolled-speaker mixtures with clean target references for fair extraction scoring.,Speaker-conditioned VAD; TSE baseline,research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md; research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "Spatial and speaker,Target-speaker extraction family,unavailable/blocked,\"No selected extraction model or test corpus with enrollment, overlapping speakers and clean target references.\",Non-target suppression; target preservation,research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md; research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "No speaker IDs, room simulation, or enrollment prompt; not reference-conditioned TSE.",
    ],
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md": [
        "It does not evaluate reference-conditioned target-speaker extraction: the exact C API accepts no enrollment/reference waveform.",
        "Every Hush output had an observed 10 ms correlation delay; all DeepFilterNet3 outputs had zero estimated delay.",
    ],
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md": [
        "It is not a natural overlap recording and it does not test enrollment-conditioned target-speaker extraction.",
        "| +12 dB | \u221213.17 dB [\u221217.40, \u22128.83] | \u2212.193 [\u2212.294, \u2212.093] | +3.70 dB [\u22125.49, +14.33] | \u221219.99 dB [\u221229.66, \u221210.35] | \u2212.401 [\u2212.573, \u2212.217] | +5.19 dB [\u221210.95, +20.41] |",
    ],
    "research/cpp-lib-market-benchmark-20261109.md": [
        "| Voice Isolation 2.5, 11-configuration WER aggregate | 23.24% raw \u2192 6.24% default VI (\u221273% relative) | 265 real recordings; WER is pooled over files per STT configuration, with the benchmark's 11-configuration aggregate reported. |",
        "| DNSMOS-C on primary-speaker speech | 3.40 \u2192 3.81 mean across scenarios | Reference-free perceptual score, scored only on target-speaker speech segments. Work 3.43\u21923.96; call center 3.65\u21924.02; phone 3.11\u21923.45. |",
    ],
    "research/voice-enhancement-20261101/findings.md": [
        "Original VoiceFilter weights are not open. VoiceFilter-Lite evidence is vendor-reported and no local artifact was evaluated.",
    ],
    "research/noise_suppression_candidate_census.md": [
        "| **Hush** | Causal 16 kHz speech enhancer explicitly trained to suppress competing speakers in conversational audio |",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "cosine 0.890 between converted output and p360 using OpenVoice's own reference encoder.",
        "target-encoder cosine was 0.669 (40+40) and 0.702 (120+40).",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/survey-det-05/README.md": [
        "It is not a waveform extractor, not a source separator, not",
    ],
    "docs/task-evidence/hush/README.md": [
        "weights or checkpoint, and accepts no enrollment prompt.",
    ],
    "docs/task-evidence/survey-det-03/README.md": [
        "target-speaker VAD (`DET-05`), source separation (`SPK-01`), target-speaker",
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
    "historical_real_speech_transcribed_only": True,
    "historical_real_corpus_transcribed_only": True,
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
    "audio_mutation_or_deletion": False,
    "target_speaker_extraction_claim": False,
    "source_separation_claim": False,
    "identity_or_verification_claim": False,
    "personalized_vad_claim": False,
    "enrollment_conditioning_claim": False,
}

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "extraction_claim_without_enrollment": "rejected; state unchanged",
    "separation_claim_promoted_to_extraction": "rejected; state unchanged",
    "suppression_claim_promoted_to_extraction": "rejected; state unchanged",
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
        raise MapError("SPK-02 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("SPK-02 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F05 / SPK-02 is not unique")
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
            raise MapError("legacy backlog mismatch: F05/SPK-02/%s" % key)


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
    census = {row["component_id"] for row in COMPONENT_CENSUS}
    if not mapped <= census:
        raise MapError("mapped component is not censused: " + ",".join(sorted(mapped - census)))


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
            raise MapError("historical execution is not labelled adjacent: " + row["id"])
        if "not rerun by this survey" not in row.get("scope", ""):
            raise MapError("historical execution scope is not bounded: " + row["id"])


def _check_evidence_classes() -> None:
    observed = set()
    for row in COMPARISON_INPUTS:
        observed.add(row["class"])
    for row in HISTORICAL_EXECUTIONS:
        observed.add(row["outcome_class"])
    for row in REPORTED_OUTCOMES:
        observed.add(row["class"])
    for key, value in EVIDENCE_CLASSES.items():
        backed = bool(observed & set(CLASS_BACKING.get(key, [])))
        if value is True and not backed:
            raise MapError("supported evidence class has no mapped row: " + key)
        if value is False and backed:
            raise MapError("evidence class is contradicted by a mapped row: " + key)
    critical_false = {
        "spk02_local_extraction_execution",
        "enrollment_conditioned_execution",
        "target_speaker_extraction_accuracy_claim",
        "clean_target_reference_accuracy_claim",
        "real_enrolled_corpus",
        "impostor_or_target_absent_negative_set",
        "real_overlap_corpus",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "public_default_claim",
        "release_claim",
    }
    for key in critical_false:
        if EVIDENCE_CLASSES.get(key) is not False:
            raise MapError("unsupported evidence class is not false: " + key)


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
        "category_scope": dict(CATEGORY_SCOPE),
        "tse_boundary": dict(TSE_BOUNDARY),
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
    for key in (
        "real_speech",
        "real_corpus",
        "weights",
        "runtime_invocation",
        "listening",
        "device_timing",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "audio_mutation_or_deletion",
        "target_speaker_extraction_claim",
        "source_separation_claim",
        "identity_or_verification_claim",
        "personalized_vad_claim",
        "enrollment_conditioning_claim",
    ):
        if report["scope"][key] is not False:
            raise MapError("unsupported scope claim: " + key)
    for key in (
        "task_local_only",
        "documentation_and_metadata_only",
        "no_new_execution",
        "synthetic_only_where_cited",
        "historical_real_speech_transcribed_only",
        "historical_real_corpus_transcribed_only",
    ):
        if report["scope"][key] is not True:
            raise MapError("scope support flag is not true: " + key)
    if any(row.get("adjacent") is not True for row in report["historical_executions"]):
        raise MapError("a historical execution is not labelled adjacent")
    for key, value in report["tse_boundary"].items():
        if not isinstance(value, bool):
            raise MapError("tse boundary value is not boolean: " + key)
    if report["tse_boundary"]["enrollment_conditioned_execution_present"] is not False:
        raise MapError("enrollment-conditioned execution is claimed")
    if report["tse_boundary"]["target_selected_output_measured"] is not False:
        raise MapError("target-selected output is claimed")
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
