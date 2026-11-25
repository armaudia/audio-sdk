# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-TRN-03.

This module builds a bounded taxonomy/comparison evidence map for the accent
conversion category (inventory category ``TRN-03``, legacy family ``F14``). It
reads only pinned, read-only documents from the enclosing ``audioml`` workspace
and the SDK worktree. It does not load audio, weights, models, runtimes, media
or the network, and it does not register, expose, enable or qualify any accent
converter.

All curated records below are documentation mappings, not new measurements.
Historical research values are transcribed from the pinned accent-conversion
report and its result JSON files and labelled with their original scope. Accent
classifier output is a directional proxy, not target-accent gold; a speaker
cosine is not a human identity rating; one 240 ms block is not sustained
streaming; and a decoder-only benchmark is not end-to-end conversion.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-TRN-03"
TITLE = "Review coverage for Accent conversion"
CATEGORY_ID = "TRN-03"
LEGACY_FAMILY = "F14"
BRANCH = "swarm/SDK-SURVEY-TRN-03"
BASE_COMMIT = "b4ccacaff0e82dbfc027404fbb7ac81d4885f768"
PROFILE = "Voice"
COMPONENT = "accent-conversion-evidence-map"
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
    "pipeline",
)

# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media, weights, transcripts or consent that are not present in this
# task directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/results/accent-classifier.json": "c1f2146f8b7a665bcb8e8cf42b14e2bd31e042d225653f467fef7f692e1d6d2b",
    "research/accent-conversion-20261101/results/tokan-metrics.json": "e4eddb01575ef102d820605d17378913cb9552fbb69ab9b97667c6e4eb90bde3",
    "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json": "1948ef27a8ff6f1ddeb24312b0a75ff0303dc6ef05bb2c659c014651cb480741",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
}

# SDK-worktree-relative boundary pins. They are read only to prove that no
# public surface was touched and to ground the cited adjacent task-local
# evidence. Sibling survey READMEs are pinned as templates, not as results.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/psola-praat/README.md": "7e64ec614937533168ef31c34d4c8ec4aa7d6d52670e663f0f88ce5f4ec7a6ef",
    "docs/task-evidence/rubber-band-r3-streaming/README.md": "04583e07678079f1ed179a1b15f50599693a7bc6f6a813237a71d0005d810d97",
    "docs/task-evidence/soundtouch/README.md": "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/survey-cln-12/README.md": "5f608d1d0dc4d0cf577e484765a6cfc8c9605c574b069dc00e15bd1aea5264ac",
    "docs/task-evidence/survey-rec-01/README.md": "01e54b306313f13f97e1c9f4a08f5ebd98cbf570617644a028ae2bca3d4f4acb",
    "docs/task-evidence/survey-trn-01/README.md": "20503c685e57ba2b6d15a677cfad1ea7e6f22b391010af61bb4fd6dc63ea8972",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Playback and voice transformations",
    "name": "Accent conversion",
    "scope": "requested_transform",
    "output_kind": "waveform",
    "purpose": "Modify pronunciation toward a designated accent.",
    "method_families": {
        "classic": "Formant/phonetic mapping; duration/pitch modification",
        "ml": "Content-feature/PPG conversion with neural resynthesis",
    },
    "input_output": "Speech + target accent and method-specific cues \u2192 converted speech",
    "live_or_comparison_boundary": (
        "Declare intended pronunciation changes and preserve content/identity. "
        "Streaming labels do not establish low conversational delay."
    ),
    "source_ids": ["S36", "S37"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "TRN",
    "meaning": "Playback and voice transformations",
    "category_id": CATEGORY_ID,
    "waveform_transformation_only": True,
    "pronunciation_change_is_not_speaker_identity_or_timbre": True,
    "accent_difference_is_not_audio_defect": True,
    "content_and_identity_preservation_are_separate": True,
    "streaming_label_is_not_low_conversational_delay": True,
    "not_voice_conversion": "TRN-04",
    "not_tts_or_voice_cloning": "TRN-05",
    "not_pitch_or_prosody_only": "TRN-02",
    "not_time_scale_modification": "TRN-01",
    "not_quality_assessment": "OBS-01",
    "not_speech_enhancement": "CLN-01",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S36",
        "title": "Classical accent conversion study",
        "url": "https://www.isca-archive.org/eurospeech_2003/yan03d_eurospeech.html",
        "access_scope": "direct",
        "mapped_components": [
            "ppg-foreign-accent-conversion",
            "soundtouch",
            "psola-praat",
        ],
        "gap_ids": ["G09", "G11"],
        "finding": (
            "Direct documentation lead for the classical formant/phonetic "
            "mapping family and its duration/pitch manipulation component. No "
            "local code, checkpoint, target-accent corpus or execution of this "
            "study exists. The adjacent TSM components are evaluation evidence "
            "for TRN-01 and are not accent converters."
        ),
    },
    {
        "source_id": "S37",
        "title": "Streaming accent conversion study",
        "url": "https://arxiv.org/html/2506.16580v1",
        "access_scope": "direct",
        "mapped_components": [
            "streaming-non-autoregressive-accent-conversion",
            "seed-vc-v2-accent-aware-path",
            "streamvc",
            "dualvc-3",
        ],
        "gap_ids": ["G06", "G10"],
        "finding": (
            "Direct paper/demo lead for streaming accent conversion. The pinned "
            "accent report says no public runnable checkpoint or implementation "
            "was located and the paper itself reports about 0.8 s latency that "
            "still needs reduction. No local streaming conversion, checkpoint or "
            "target-accent evaluation exists."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "Formant/phonetic mapping of source pronunciation toward a "
            "designated target accent (classical accent conversion, S36)"
        ),
        "components": ["ppg-foreign-accent-conversion"],
        "gap_ids": ["G09", "G10"],
        "status": "documented_lead_no_runnable_local_system",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Duration and pitch modification used as an accent-adjacent "
            "classical control, not as accent conversion by itself"
        ),
        "components": ["soundtouch", "psola-praat", "rubber-band-r3-streaming"],
        "gap_ids": ["G11", "G04"],
        "status": "adjacent_tsm_evidence_only_not_accent_conversion",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Content-feature/PPG conversion with neural resynthesis "
            "(WavLM/VQ tokens plus autoregressive model and neural decoder)"
        ),
        "components": [
            "tokan",
            "wavlm-large-in-tokan",
            "meanvc2",
            "seed-vc-25m",
            "seed-vc-xls-r-300m-content-encoder",
            "rvc-v2-vctk-p226",
        ],
        "gap_ids": ["G04", "G05", "G06", "G07", "G08", "G15"],
        "status": "historical_three_clip_smoke_and_blocked_generic_vc_only",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": (
            "Accent-aware streaming content-feature conversion and generic "
            "zero-shot streaming voice conversion (S37)"
        ),
        "components": [
            "seed-vc-v2-accent-aware-path",
            "streaming-non-autoregressive-accent-conversion",
            "streamvc",
            "dualvc-3",
            "convert-and-speak",
            "psdn-zero-shot-ac",
            "voice-preserving-zero-shot-multiple-accent-conversion",
        ],
        "gap_ids": ["G06", "G10"],
        "status": "considered_or_blocked_no_accent_conversion_execution",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": (
            "Neural resynthesis and vocoder component inside a "
            "content-feature conversion pipeline"
        ),
        "components": [
            "vocos",
            "univnet",
            "micro-hifi-gan",
            "ms-istft-generator",
            "fregan",
        ],
        "gap_ids": ["G14", "G10"],
        "status": "decoder_component_only_no_end_to_end_conversion",
    },
]

# component_id, task and evidence_status are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "soundtouch", "role": "adjacent_duration_pitch_control", "evidence_status": "evaluated", "task": "SDK-SOUNDTOUCH"},
    {"component_id": "psola-praat", "role": "adjacent_pitch_synchronous_control", "evidence_status": "evaluated", "task": "SDK-PSOLA-PRAAT"},
    {"component_id": "rubber-band-r3-streaming", "role": "adjacent_streaming_time_scale_control", "evidence_status": "evaluated", "task": "SDK-RUBBER-BAND-R3-STREAMING"},
    {"component_id": "ppg-foreign-accent-conversion", "role": "classical_ppg_accent_conversion_lead", "evidence_status": "considered", "task": "SDK-PPG-FOREIGN-ACCENT-CONVERSION"},
    {"component_id": "tokan", "role": "open_weight_accent_normalization_candidate", "evidence_status": "partial", "task": "SDK-TOKAN"},
    {"component_id": "wavlm-large-in-tokan", "role": "content_encoder_inside_tokan", "evidence_status": "partial", "task": "SDK-WAVLM-LARGE-IN-TOKAN"},
    {"component_id": "meanvc2", "role": "generic_streaming_vc_candidate_blocked", "evidence_status": "partial", "task": "SDK-MEANVC2"},
    {"component_id": "seed-vc-25m", "role": "generic_streaming_vc_candidate", "evidence_status": "partial", "task": "SDK-SEED-VC-25M"},
    {"component_id": "seed-vc-xls-r-300m-content-encoder", "role": "content_encoder_for_seed_vc_path", "evidence_status": "partial", "task": "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER"},
    {"component_id": "vocos", "role": "neural_vocoder_decoder_component", "evidence_status": "partial", "task": "SDK-VOCOS"},
    {"component_id": "rvc-v2-vctk-p226", "role": "generic_target_voice_conversion_candidate", "evidence_status": "partial", "task": "SDK-RVC-V2-VCTK-P226"},
    {"component_id": "seed-vc-v2-accent-aware-path", "role": "accent_aware_streaming_path_lead", "evidence_status": "considered", "task": "SDK-SEED-VC-V2-ACCENT-AWARE-PATH"},
    {"component_id": "streaming-non-autoregressive-accent-conversion", "role": "streaming_accent_conversion_paper_lead", "evidence_status": "considered", "task": "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION"},
    {"component_id": "streamvc", "role": "unofficial_streaming_vc_lead_blocked", "evidence_status": "blocked", "task": "SDK-STREAMVC"},
    {"component_id": "dualvc-3", "role": "streaming_generic_vc_lead", "evidence_status": "considered", "task": "SDK-DUALVC-3"},
    {"component_id": "convert-and-speak", "role": "autoregressive_accent_conversion_research_lead", "evidence_status": "considered", "task": "SDK-CONVERT-AND-SPEAK"},
    {"component_id": "psdn-zero-shot-ac", "role": "zero_shot_accent_conversion_research_lead", "evidence_status": "considered", "task": "SDK-PSDN-ZERO-SHOT-AC"},
    {"component_id": "voice-preserving-zero-shot-multiple-accent-conversion", "role": "multi_accent_zero_shot_research_lead", "evidence_status": "considered", "task": "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION"},
    {"component_id": "yourtts", "role": "generic_tts_cloning_lead_blocked", "evidence_status": "blocked", "task": "SDK-YOURTTS"},
    {"component_id": "vits-streaming-adaptation", "role": "generic_streaming_synthesis_lead", "evidence_status": "considered", "task": "SDK-VITS-STREAMING-ADAPTATION"},
    {"component_id": "contentvec", "role": "content_encoder_component_lead", "evidence_status": "considered", "task": "SDK-CONTENTVEC"},
    {"component_id": "quickvc", "role": "generic_vc_component_lead", "evidence_status": "considered", "task": "SDK-QUICKVC"},
    {"component_id": "hubert-conversion-encoder", "role": "content_encoder_component_blocked", "evidence_status": "blocked", "task": "SDK-HUBERT-CONVERSION-ENCODER"},
    {"component_id": "wavlm-conversion-encoder", "role": "content_encoder_component_blocked", "evidence_status": "blocked", "task": "SDK-WAVLM-CONVERSION-ENCODER"},
    {"component_id": "univnet", "role": "vocoder_component_lead", "evidence_status": "considered", "task": "SDK-UNIVNET"},
    {"component_id": "micro-hifi-gan", "role": "vocoder_component_lead", "evidence_status": "considered", "task": "SDK-MICRO-HIFI-GAN"},
    {"component_id": "ms-istft-generator", "role": "vocoder_component_lead", "evidence_status": "considered", "task": "SDK-MS-ISTFT-GENERATOR"},
    {"component_id": "fregan", "role": "vocoder_component_lead", "evidence_status": "considered", "task": "SDK-FREGAN"},
    {"component_id": "accentbox", "role": "accent_controlled_tts_lead", "evidence_status": "considered", "task": "SDK-ACCENTBOX"},
    {"component_id": "genaid", "role": "accent_embedding_tts_lead", "evidence_status": "considered", "task": "SDK-GENAID"},
    {"component_id": "accentcl", "role": "accent_classifier_lead", "evidence_status": "considered", "task": "SDK-ACCENTCL"},
    {"component_id": "taltech-accent-classifier-proxy", "role": "accent_classifier_proxy_control", "evidence_status": "partial", "task": "SDK-TALTECH-ACCENT-CLASSIFIER-PROXY"},
    {"component_id": "resemblyzer-speaker-similarity-proxy", "role": "speaker_similarity_proxy_control", "evidence_status": "partial", "task": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"},
    {"component_id": "lj-speech-and-consented-accent-evaluation-manifests", "role": "evaluation_manifest_control", "evidence_status": "partial", "task": "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS"},
    {"component_id": "krisp-accent-conversion", "role": "closed_external_product_lead", "evidence_status": "blocked", "task": "SDK-KRISP-ACCENT-CONVERSION"},
    {"component_id": "sanas-accent-translation", "role": "closed_external_product_lead", "evidence_status": "considered", "task": "SDK-SANAS-ACCENT-TRANSLATION"},
]

EXCLUDED_BOUNDARIES: List[Dict[str, str]] = [
    {
        "boundary": "Time-scale and pitch-preserving speed modification (TRN-01)",
        "reason": "A duration or rate change is not a pronunciation change and does not move speech toward a target accent.",
    },
    {
        "boundary": "Pitch and limited prosody control (TRN-02)",
        "reason": "Pitch, duration and energy controls are not phoneme-level pronunciation mapping.",
    },
    {
        "boundary": "Speech-to-speech voice conversion (TRN-04)",
        "reason": "Changing timbre or target speaker identity is not changing the source speaker's accent.",
    },
    {
        "boundary": "Reference-conditioned voice cloning and TTS (TRN-05)",
        "reason": "Text-to-speech or voice cloning generates speech rather than converting the supplied utterance.",
    },
    {
        "boundary": "Quality and impairment assessment (OBS-01) and enhancement (CLN-01)",
        "reason": "An accent difference is not an audio defect, and a converted waveform is not a quality score or denoised signal.",
    },
    {
        "boundary": "Recognition, translation and language identification (REC)",
        "reason": "A transcript, translation or language label is not a converted waveform or target-accent gold.",
    },
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Three authors' accent-labeled English L2-ARCTIC utterances (Arabic, Hindi, Korean) converted by TokAN with the same clip as the speaker reference",
        "class": "historical_research_three_accent_tokan_conversion",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Three short smoke clips from three speakers; same-clip reference, one model revision and no independent target-accent or identity gold.",
    },
    {
        "id": "CI-2",
        "input": "MilesPurvis six-class English accent classifier applied to the three source/TokAN output pairs",
        "class": "historical_research_accent_classifier_proxy",
        "source_pin": "research/accent-conversion-20261101/results/accent-classifier.json",
        "boundary": "The classifier's added Latin class has about 100 samples, it has no Korean class and its prediction is a directional proxy, not target-accent ground truth.",
    },
    {
        "id": "CI-3",
        "input": "One 240 ms Arabic L2-ARCTIC block through upstream Seed-VC Realtime custom_infer with 2.2 s left context, 0.2 s right context and 10 diffusion steps",
        "class": "historical_research_seedvc_single_block",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "One first block from a generic VC streaming path, not the accent-aware V2 path and not a sustained-stream measurement.",
    },
    {
        "id": "CI-4",
        "input": "MeanVC2 40 ms public bundle with 80 ms and 160 ms ASR checkpoints and a Vocos decoder; end-to-end inference attempted",
        "class": "historical_research_meanvc2_blocked_attempt",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Failed before conversion on missing WavLM checkpoints; no converted audio, end-to-end latency or quality result exists.",
    },
    {
        "id": "CI-5",
        "input": "Synthetic 1 s 80-bin mel input through the MeanVC2-bundled Vocos JIT decoder on CPU",
        "class": "historical_research_vocos_decoder_timing",
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
        "boundary": "Decoder-only timing on synthetic features; no acoustic model, accent conversion, quality or end-to-end latency.",
    },
    {
        "id": "CI-6",
        "input": "Classical (S36) and streaming (S37) accent-conversion source leads",
        "class": "source_reported_accent_conversion_lead",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation and paper leads only; no local code, checkpoint, corpus, target accent or numeric parity follows.",
    },
    {
        "id": "CI-7",
        "input": "Krisp Accent Conversion and Sanas Accent Translation public product documentation",
        "class": "source_reported_product_documentation",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Closed/proprietary products; weights, exact model revisions and comparable local runs are unavailable.",
    },
    {
        "id": "CI-8",
        "input": "Rights-cleared multi-accent speech cohort with consented target-accent references, manual transcripts and independent listening labels",
        "class": "missing_required_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Not present in this task or the pinned research; no consent, split, target-accent reference, manual transcript or listening label is staged.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "source/identity clip", "role": "The unmodified source utterance is the content/identity reference for every historical pair; it is not an accent-conversion control system.", "source_pin": "research/accent-conversion-20261101/README.md"},
    {"id": "CT-2", "name": "Whisper tiny transcript preservation", "role": "Same-transcript preservation proxy on three clips; it is not comprehension, manual transcription or pronunciation correctness.", "source_pin": "research/accent-conversion-20261101/results/tokan-metrics.json"},
    {"id": "CT-3", "name": "Resemblyzer speaker cosine", "role": "Quick speaker-similarity proxy, not a human identity rating and not a target-accent measure.", "source_pin": "research/accent-conversion-20261101/results/tokan-metrics.json"},
    {"id": "CT-4", "name": "six-class accent classifier", "role": "Directional source/converted probability comparison; uncalibrated, without a Korean class and not target-accent gold.", "source_pin": "research/accent-conversion-20261101/results/accent-classifier.json"},
    {"id": "CT-5", "name": "duration ratio", "role": "Input/output duration ratio exposes loss or expansion; it is not a pronunciation or intelligibility result.", "source_pin": "research/accent-conversion-20261101/results/tokan-metrics.json"},
    {"id": "CT-6", "name": "blocked rows without substitution", "role": "MeanVC2 is not replaced by an unverified or differently licensed mirror; candidate identity is preserved.", "source_pin": "research/accent-conversion-20261101/README.md"},
    {"id": "CT-7", "name": "decoder-only synthetic input", "role": "Vocos timing uses synthetic mel features; it does not stand in for an end-to-end accent converter.", "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "L2-ARCTIC accent-labeled demo clips (Arabic, Hindi, Korean)",
        "class": "research_audio",
        "status": "CC BY-NC 4.0 per the cited report; local only and not redistributed; a three-clip noncommercial research slice",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "TokAN converted WAV outputs",
        "class": "workspace_research_output",
        "status": "Three finite 24 kHz mono WAVs under the pinned research results directory; not staged or played in this task",
        "source_pin": "research/accent-conversion-20261101/results/tokan-metrics.json",
    },
    {
        "asset": "TokAN inference bundle (ARLM 690 MB, quantizer/flow 393 MB, HiFT 83 MB)",
        "class": "external_weights_metadata_only",
        "status": "Metadata only; no visible repository license and no staged checkpoint in this task",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "WavLM-Large content encoder (1.2 GB)",
        "class": "external_weights_metadata_only",
        "status": "Metadata only; used by TokAN and required by MeanVC2; not staged or loaded here",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "Seed-VC Realtime checkpoint bundle plus XLS-R-300M encoder",
        "class": "external_weights_metadata_only",
        "status": "Metadata only; downloaded and removed after the historical run; no weight terms or exact revision is recorded in this task",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "MeanVC2 40 ms public bundle",
        "class": "external_weights_metadata_only",
        "status": "Partially acquired historically; required wavlm_large.pt and wavlm_large_finetune.pth are missing and no substitute was used",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "MilesPurvis english-accent-classifier",
        "class": "external_model_metadata_only",
        "status": "Metadata only; six English classes, no Korean class, added Latin class about 100 samples; not staged here",
        "source_pin": "research/accent-conversion-20261101/results/accent-classifier.json",
    },
    {
        "asset": "Vocos JIT decoder bundled with MeanVC2",
        "class": "external_model_metadata_only",
        "status": "Metadata only; decoder-level timing on synthetic mel, not an end-to-end converter",
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
    },
    {
        "asset": "Rights-cleared multi-accent cohort with consented target references, manual transcripts and listening labels",
        "class": "missing_asset",
        "status": "No rights-cleared cohort, consent record, target-accent reference, speaker/accent split or listening label is staged",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "TokAN accent normalization on three L1-accented English clips",
        "outcome_class": "historical_research_three_accent_tokan_conversion",
        "component_ids": ["tokan", "wavlm-large-in-tokan"],
        "source_pin": "research/accent-conversion-20261101/results/tokan-metrics.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "open_weight_accent_normalization_smoke",
        "values": {
            "clips": 3,
            "l1_groups": ["Arabic", "Hindi", "Korean"],
            "source_duration_s": [4.53859410430839, 3.4900226757369612, 3.042267573696145],
            "output_duration_s": [3.0, 3.18, 2.76],
            "duration_ratio": [0.6609976417922379, 0.9111688649210579, 0.9072180316627411],
            "runtime_s": [78.89, 63.74, 62.55],
            "rtf": [17.38, 18.26, 20.56],
            "wer_converted_vs_source_asr": [0.0, 0.0, 0.0],
            "speaker_embedding_cosine": [0.8377127647399902, 0.7982522249221802, 0.8736226558685303],
            "output_sample_rate_hz": 24000,
            "output_channels": 1,
            "finite_output": True,
            "same_clip_as_speaker_reference": True,
            "streaming": False,
        },
        "scope": (
            "Three short demo clips, three speakers and three L1 groups, run "
            "offline on one Apple M1 CPU with the same clip as the speaker "
            "reference. Whisper-tiny transcript equality and Resemblyzer cosine "
            "are proxies; there is no blinded listening, manual transcript, "
            "target-accent gold or sustained-stream timing. not rerun by this "
            "survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Six-class accent classifier on source and TokAN output",
        "outcome_class": "historical_research_accent_classifier_proxy",
        "component_ids": ["tokan"],
        "source_pin": "research/accent-conversion-20261101/results/accent-classifier.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "directional_accent_classifier_proxy",
        "values": {
            "pairs": 3,
            "source_predicted_labels": ["latin", "indian", "canada"],
            "converted_predicted_labels": ["canada", "latin", "canada"],
            "us_probability_delta": [0.169649, 0.00873, -0.051463],
            "us_probability_increase_count": 2,
            "material_us_increase_count": 1,
            "classifier_has_korean_class": False,
            "calibrated": False,
        },
        "scope": (
            "A six-class English accent classifier over three source/output "
            "pairs. Training is primarily native-speaker Common Voice, the added "
            "Latin class has about 100 samples and Korean is absent, so the "
            "prediction is a directional proxy, not target-accent ground truth. "
            "not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Seed-VC Realtime one 240 ms block",
        "outcome_class": "historical_research_seedvc_single_block",
        "component_ids": ["seed-vc-xls-r-300m-content-encoder"],
        "source_pin": "research/accent-conversion-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "generic_vc_streaming_block_smoke",
        "values": {
            "block_ms": 240,
            "left_context_s": 2.2,
            "right_context_s": 0.2,
            "diffusion_steps": 10,
            "model_load_s": 254.01,
            "block_compute_s": 22.21,
            "block_realtime_factor": 92.55,
            "output_sample_rate_hz": 22050,
            "output_channels": 1,
            "finite_output": True,
            "asr_comparison_meaningful": False,
            "accent_aware_v2_path": False,
            "sustained_stream": False,
        },
        "scope": (
            "One first block through upstream Seed-VC Realtime custom_infer on "
            "CPU. It is a generic VC path, not the accent-aware V2 path; the "
            "output is too short for meaningful ASR, WER or speaker comparison "
            "and the block is not a warmed-up sustained-stream measurement. not "
            "rerun by this survey."
        ),
    },
    {
        "id": "HE-4",
        "label": "MeanVC2 40 ms end-to-end inference attempt",
        "outcome_class": "historical_research_meanvc2_blocked_attempt",
        "component_ids": ["meanvc2"],
        "source_pin": "research/accent-conversion-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "blocked_asset_dependency_attempt",
        "values": {
            "public_bundle_acquired": True,
            "asr_checkpoint_loads": True,
            "end_to_end_inference": False,
            "missing_checkpoint_count": 2,
            "missing_checkpoints": ["wavlm_large.pt", "wavlm_large_finetune.pth"],
            "converted_audio_produced": False,
            "end_to_end_latency_s": None,
            "substitute_asset_used": False,
        },
        "scope": (
            "The 40 ms bundle was acquired and the ASR checkpoint loaded, but "
            "inference failed before conversion with FileNotFoundError for the "
            "WavLM speaker checkpoints. No converted audio, quality score or "
            "end-to-end latency exists; no unverified mirror was substituted. "
            "not rerun by this survey."
        ),
    },
    {
        "id": "HE-5",
        "label": "Vocos JIT decoder CPU timing on synthetic mel",
        "outcome_class": "historical_research_vocos_decoder_timing",
        "component_ids": ["vocos"],
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "decoder_only_timing_component",
        "values": {
            "device": "cpu",
            "input_mel_shape": [1, 80, 100],
            "output_shape": [1, 15840],
            "output_duration_s": 0.99,
            "mean_decode_s": 0.17284687500214205,
            "rtf": 0.17459280303246671,
            "finite_output": True,
            "end_to_end_conversion": False,
            "quality_assessed": False,
        },
        "scope": (
            "Decoder-only CPU timing on a synthetic 1 s 80-bin mel input, mean "
            "over five post-warm-up calls. It is not accent conversion, not an "
            "end-to-end pipeline latency and not a quality assessment. not rerun "
            "by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Classical accent conversion study (S36)",
        "class": "source_reported_accent_conversion_lead",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Published study lead for formant/phonetic mapping; no local code, corpus, checkpoint or numeric parity.",
    },
    {
        "id": "RO-2",
        "claim": "Streaming non-autoregressive accent conversion (S37)",
        "class": "source_reported_accent_conversion_lead",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Paper/demo only; about 0.8 s reported latency that still needs reduction, not a sub-100 ms deployment result.",
    },
    {
        "id": "RO-3",
        "claim": "Convert and Speak accent-conversion research comparison",
        "class": "source_reported_research_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Paper/demo inspected with no runnable local checkpoint; autoregressive generation is not a strict low-latency candidate.",
    },
    {
        "id": "RO-4",
        "claim": "PSDN zero-shot accent conversion",
        "class": "source_reported_research_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Paper and samples only; no official runnable checkpoint or repository was located.",
    },
    {
        "id": "RO-5",
        "claim": "Voice-Preserving Zero-Shot Multiple Accent Conversion",
        "class": "source_reported_research_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Paper only; no official weights or repository located, so it remains a research comparison.",
    },
    {
        "id": "RO-6",
        "claim": "MeanVC2 paper 80 ms chunk-plus-lookahead design figure",
        "class": "source_reported_research_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "A generic VC design-latency claim, not an accent-conversion result and not reproduced on this host.",
    },
    {
        "id": "RO-7",
        "claim": "AccentCL seven-class classifier",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "About 2.56 GB per checkpoint plus Whisper-Large-v3; not practical on the historical host and not run.",
    },
    {
        "id": "RO-8",
        "claim": "Krisp Accent Conversion product",
        "class": "source_reported_product_documentation",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Closed/proprietary model documented at roughly 180 ms; no weights or comparable local run.",
    },
    {
        "id": "RO-9",
        "claim": "Sanas Accent Translation product",
        "class": "source_reported_product_documentation",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Closed/proprietary product; latency and weights are not public and no local run exists.",
    },
    {
        "id": "RO-10",
        "claim": "AccentBox and GenAID accent-controlled TTS",
        "class": "source_reported_research_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Accent-controlled synthesis or embeddings, not audio-to-audio conversion; inference weights were not downloaded.",
    },
    {
        "id": "RO-11",
        "claim": "StreamVC unofficial implementation",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "No trained checkpoint and incomplete paper-style streaming inference; cannot run as a pretrained model.",
    },
    {
        "id": "RO-12",
        "claim": "DualVC 3 streaming generic voice conversion",
        "class": "source_reported_research_candidate",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": "Paper/demo only with no official runnable checkpoint; streaming generic VC is not dedicated accent normalization.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "permitted_input_and_target_references": "Three L2-ARCTIC demo clips and same-clip references exist historically; no rights-cleared target-accent reference or consent record is staged.",
        "task_and_language_speaker_groups": "Three speakers and three L1 groups (Arabic, Hindi, Korean) form a tiny noncommercial slice; no target General American cohort exists.",
        "preserve_text_and_semantic_content": "Whisper-tiny transcript equality (0.00 WER against source ASR) is a proxy only; no manual transcript or comprehension check exists.",
        "identity_and_similarity": "Resemblyzer cosine 0.798-0.874 is a quick proxy, not a human identity rating and not a target-accent measure.",
        "naturalness": "No blinded listening, naturalness rating or accent-reduction panel was run.",
        "alignment": "Duration ratios 0.661-0.911 expose large shortening; no sample-level alignment or onset/offset measurement exists.",
        "first_output_and_tail_timing": "One 240 ms Seed-VC block took 22.21 s after 254.01 s model load; no first-output/tail distribution or sustained stream exists.",
        "exact_target_condition": "The target is only a classifier's US probability and a general American proxy; no explicit target accent specification or pronunciation-change policy exists.",
        "consent_reference_availability_output_use": "L2-ARCTIC is CC BY-NC 4.0 research data; output use, target-reference consent and redistribution rights are uncleared.",
    },
    "blocked": [
        "Rights-cleared multi-accent corpus with consented target-accent references, manual transcripts and explicit output-use terms",
        "Independent blinded listening for accent movement, naturalness, content and speaker identity on frozen cohorts",
        "Matched identity, generic-VC, duration/pitch-only and accent-classifier controls with uncertainty",
        "Pinned model bundles, exact revisions, per-weight terms and reproducible runtimes for TokAN, MeanVC2, Seed-VC and Vocos",
        "Causal streaming chunk/lookahead, first-output/tail, sustained CPU/accelerator and target-device timing evidence",
        "Explicit pronunciation-change policy that separates intended accent changes from content, identity and consent",
        "Opt-in provider or external-adapter intake with independent exact-head review",
        "Release approval; DEFER remains in force until every gate is closed",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class is
# true only when a mapped row backs it; absence is recorded as false instead of
# being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "historical_research_three_accent_tokan_conversion": True,
    "historical_research_accent_classifier_proxy": True,
    "historical_research_seedvc_single_block": True,
    "historical_research_meanvc2_blocked_attempt": True,
    "historical_research_vocos_decoder_timing": True,
    "source_reported_accent_conversion_lead": True,
    "source_reported_research_candidate": True,
    "source_reported_product_documentation": True,
    "source_reported_blocked_candidate": True,
    "real_accent_conversion_corpus_benchmark": False,
    "human_listening_result": False,
    "independent_human_transcript_review": False,
    "target_accent_gold": False,
    "speaker_identity_gold": False,
    "accent_classifier_calibration": False,
    "streaming_accent_conversion_execution": False,
    "sustained_stream_latency": False,
    "device_timing": False,
    "cpu_accelerator_parity": False,
    "latency_claim": False,
    "quality_claim": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "provider_enablement": False,
    "release_approval": False,
}

CLASS_BACKING: Dict[str, List[str]] = {
    "historical_research_three_accent_tokan_conversion": [
        "historical_research_three_accent_tokan_conversion"
    ],
    "historical_research_accent_classifier_proxy": [
        "historical_research_accent_classifier_proxy"
    ],
    "historical_research_seedvc_single_block": [
        "historical_research_seedvc_single_block"
    ],
    "historical_research_meanvc2_blocked_attempt": [
        "historical_research_meanvc2_blocked_attempt"
    ],
    "historical_research_vocos_decoder_timing": [
        "historical_research_vocos_decoder_timing"
    ],
    "source_reported_accent_conversion_lead": [
        "source_reported_accent_conversion_lead"
    ],
    "source_reported_research_candidate": [
        "source_reported_research_candidate"
    ],
    "source_reported_product_documentation": [
        "source_reported_product_documentation"
    ],
    "source_reported_blocked_candidate": [
        "source_reported_blocked_candidate"
    ],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a rights-cleared multi-accent speech cohort with consented target-accent references, manual transcripts and explicit output-use terms",
        "evidence_gap": "The historical evidence is three L2-ARCTIC demo clips under CC BY-NC 4.0 with same-clip references; no consent, target reference or output-use clearance exists.",
        "follow_up_ids": [
            "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS",
            "SDK-PIPE-VOICE",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked manifest, pipeline and evidence foundations own consented manifests and acceptance rules; none supplies a rights-cleared cohort here.",
    },
    {
        "id": "G02",
        "actionable_gap": "Run independent blinded listening and manual transcript verification for accent movement, naturalness, content and identity",
        "evidence_gap": "Accent classifier output is a proxy and no blinded panel, manual transcript review or naturalness rating was run.",
        "follow_up_ids": [
            "SDK-PIPE-VOICE",
            "SDK-FND-EVIDENCE",
            "SDK-TALTECH-ACCENT-CLASSIFIER-PROXY",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked pipeline, evidence and classifier-control rows own protocol and proxies; no listening result exists and none is inherited from an adjacent survey.",
    },
    {
        "id": "G03",
        "actionable_gap": "Calibrate an accent classifier and cover the tested accent groups before using it as a target-accent measure",
        "evidence_gap": "The six-class classifier has no Korean class, an about-100-sample added Latin class and uncalibrated US probabilities; AccentCL was not run.",
        "follow_up_ids": [
            "SDK-TALTECH-ACCENT-CLASSIFIER-PROXY",
            "SDK-ACCENTCL",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked classifier-control and AccentCL feasibility rows own classifier evaluation; neither provides target-accent calibration for these speakers.",
    },
    {
        "id": "G04",
        "actionable_gap": "Define content and pronunciation preservation metrics beyond Whisper-tiny transcript equality and duration ratio",
        "evidence_gap": "Only same-transcript equality and input/output duration ratios exist; manual words, phoneme changes, intelligibility and semantic preservation are unmeasured.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked evidence, similarity-proxy and manifest rows own metric acceptance and proxies; no pronunciation-preservation metric exists.",
    },
    {
        "id": "G05",
        "actionable_gap": "Measure speaker identity preservation with independent human ratings rather than a speaker-embedding cosine",
        "evidence_gap": "Resemblyzer cosine 0.798-0.874 is a quick proxy; no human identity rating, embedding calibration or target-speaker confusion audit exists.",
        "follow_up_ids": [
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-WAVLM-LARGE-IN-TOKAN",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked similarity-proxy and WavLM encoder rows own proxy and encoder scope; neither is a human identity result.",
    },
    {
        "id": "G06",
        "actionable_gap": "Establish causal streaming chunking, lookahead, first-output/tail and sustained-stream latency for an accent-aware path",
        "evidence_gap": "Seed-VC Realtime is a generic VC path with one 240 ms block at 92.55x real-time; no accent-aware V2 run, sustained stream or device timing exists.",
        "follow_up_ids": [
            "SDK-SEED-VC-V2-ACCENT-AWARE-PATH",
            "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION",
            "SDK-STREAMVC",
            "SDK-DUALVC-3",
            "SDK-FND-TIMING",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked accent-aware and streaming-VC feasibility rows own candidates; the timing foundation owns the fixed-frame clock. No streaming accent conversion was executed.",
    },
    {
        "id": "G07",
        "actionable_gap": "Resolve TokAN weights, licence terms and exact revision before any comparison",
        "evidence_gap": "The TokAN repository has placeholder paper metadata and no visible license; the inference bundle was deleted after the historical run and no revision is pinned.",
        "follow_up_ids": [
            "SDK-TOKAN",
            "SDK-WAVLM-LARGE-IN-TOKAN",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked TokAN implementation, WavLM research-control and audit foundation rows own provenance; no weight is downloaded, loaded or cleared here.",
    },
    {
        "id": "G08",
        "actionable_gap": "Resolve the MeanVC2 WavLM checkpoint dependency and licence before retrying",
        "evidence_gap": "MeanVC2 stopped before conversion on missing wavlm_large.pt and wavlm_large_finetune.pth; the public URL returned 404 and the mirror had mixed-source licensing.",
        "follow_up_ids": [
            "SDK-MEANVC2",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked MeanVC2 implementation and audit foundation rows own the candidate and asset boundary; no substitute asset was used.",
    },
    {
        "id": "G09",
        "actionable_gap": "Build or acquire a runnable classical formant/phonetic mapping baseline for accent conversion",
        "evidence_gap": "S36 is a paper lead and the PPG foreign-accent row is considered only; no local code, checkpoint or execution of classical formant/phonetic mapping exists.",
        "follow_up_ids": [
            "SDK-PPG-FOREIGN-ACCENT-CONVERSION",
            "SDK-CONTENTVEC",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked PPG and ContentVec feasibility rows own classical/content-feature candidates; neither is a runnable accent converter.",
    },
    {
        "id": "G10",
        "actionable_gap": "Separate accent-aware conversion from generic voice conversion in every ML comparison",
        "evidence_gap": "Seed-VC Realtime, RVC and MeanVC2 are generic VC; Convert-and-Speak, PSDN and multiple-accent conversion are paper-only and no accent-aware local run exists.",
        "follow_up_ids": [
            "SDK-CONVERT-AND-SPEAK",
            "SDK-PSDN-ZERO-SHOT-AC",
            "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION",
            "SDK-YOURTTS",
            "SDK-VITS-STREAMING-ADAPTATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked accent-conversion and synthesis feasibility rows own candidate scoping; generic VC or TTS is never promoted to accent conversion.",
    },
    {
        "id": "G11",
        "actionable_gap": "Keep duration/pitch modification and time-scale evidence from being reported as accent conversion",
        "evidence_gap": "SoundTouch, PSOLA and Rubber Band are TRN-01 controls; they change duration or pitch but do not map pronunciation to a target accent.",
        "follow_up_ids": [
            "SDK-SURVEY-TRN-01",
            "SDK-PIPE-VOICE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked TRN-01 taxonomy and voice pipeline rows own the rate boundary; a duration/pitch control is not an accent result.",
    },
    {
        "id": "G12",
        "actionable_gap": "Treat closed accent products as external-adapter leads only, without vendor-output promotion",
        "evidence_gap": "Krisp documents roughly 180 ms and Sanas documents comparable latency, but weights, revisions and comparable local outputs are unavailable.",
        "follow_up_ids": [
            "SDK-KRISP-ACCENT-CONVERSION",
            "SDK-SANAS-ACCENT-TRANSLATION",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked external-adapter rows own vendor scope; no closed runtime, credential or vendor output is used here.",
    },
    {
        "id": "G13",
        "actionable_gap": "Declare the intended pronunciation changes and separate accent-controlled synthesis from audio-to-audio conversion",
        "evidence_gap": "AccentBox and GenAID are synthesis/embedding leads; no explicit target-accent definition or pronunciation-change policy exists for conversion.",
        "follow_up_ids": [
            "SDK-ACCENTBOX",
            "SDK-GENAID",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked synthesis feasibility rows own accent-controlled generation; synthesis is not a converted source utterance.",
    },
    {
        "id": "G14",
        "actionable_gap": "Evaluate a neural resynthesis/vocoder component only inside a complete converter with matched acoustic features",
        "evidence_gap": "Vocos timing uses synthetic mel and output-shape checks; UnivNet, Micro-HiFi-GAN, MS-iSTFT and FreGAN have no matched acoustic model or checkpoint.",
        "follow_up_ids": [
            "SDK-VOCOS",
            "SDK-UNIVNET",
            "SDK-MICRO-HIFI-GAN",
            "SDK-MS-ISTFT-GENERATOR",
            "SDK-FREGAN",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked vocoder implementation and feasibility rows own components; a decoder-only timing is not an end-to-end accent converter.",
    },
    {
        "id": "G15",
        "actionable_gap": "Pin exact revisions and terms for Seed-VC, RVC and content-encoder bundles and add a dedicated Seed-VC Realtime row",
        "evidence_gap": "The Seed-VC Realtime bundle has no inventory component, RVC is a target-voice baseline and HuBERT/WavLM/QuickVC encoder rows are blocked or considered; no exact revision or weight terms exist.",
        "follow_up_ids": [
            "SDK-SEED-VC-25M",
            "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER",
            "SDK-RVC-V2-VCTK-P226",
            "SDK-HUBERT-CONVERSION-ENCODER",
            "SDK-WAVLM-CONVERSION-ENCODER",
            "SDK-QUICKVC",
        ],
        "feasibility_task_exists": False,
        "owner_note": "The linked implementation and encoder rows own the candidates; none is an accent-aware bundle with pinned terms, and no new task is invented here.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS", "title": "LJ Speech and consented accent evaluation manifests", "mode": "research-control"},
    {"task_id": "SDK-PIPE-VOICE", "title": "Consented offline voice and accent experiments", "mode": "pipeline"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-TALTECH-ACCENT-CLASSIFIER-PROXY", "title": "TalTech accent classifier proxy", "mode": "research-control"},
    {"task_id": "SDK-ACCENTCL", "title": "AccentCL", "mode": "feasibility"},
    {"task_id": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY", "title": "Resemblyzer speaker-similarity proxy", "mode": "research-control"},
    {"task_id": "SDK-WAVLM-LARGE-IN-TOKAN", "title": "WavLM-Large in TokAN", "mode": "research-control"},
    {"task_id": "SDK-SEED-VC-V2-ACCENT-AWARE-PATH", "title": "Seed-VC V2 accent-aware path", "mode": "feasibility"},
    {"task_id": "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION", "title": "Streaming non-autoregressive Accent Conversion", "mode": "feasibility"},
    {"task_id": "SDK-STREAMVC", "title": "StreamVC", "mode": "feasibility"},
    {"task_id": "SDK-DUALVC-3", "title": "DualVC 3", "mode": "feasibility"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-TOKAN", "title": "TokAN", "mode": "implementation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-MEANVC2", "title": "MeanVC2", "mode": "implementation"},
    {"task_id": "SDK-PPG-FOREIGN-ACCENT-CONVERSION", "title": "PPG foreign-accent conversion", "mode": "feasibility"},
    {"task_id": "SDK-SURVEY-TRN-01", "title": "Review coverage for Pitch-preserving speed / time-scale modification", "mode": "taxonomy"},
    {"task_id": "SDK-KRISP-ACCENT-CONVERSION", "title": "Krisp Accent Conversion", "mode": "external-adapter"},
    {"task_id": "SDK-SANAS-ACCENT-TRANSLATION", "title": "Sanas Accent Translation", "mode": "external-adapter"},
    {"task_id": "SDK-ACCENTBOX", "title": "AccentBox", "mode": "feasibility"},
    {"task_id": "SDK-GENAID", "title": "GenAID", "mode": "feasibility"},
    {"task_id": "SDK-SEED-VC-25M", "title": "Seed-VC 25M", "mode": "implementation"},
    {"task_id": "SDK-CONVERT-AND-SPEAK", "title": "Convert and Speak", "mode": "feasibility"},
    {"task_id": "SDK-PSDN-ZERO-SHOT-AC", "title": "PSDN zero-shot AC", "mode": "feasibility"},
    {"task_id": "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION", "title": "Voice-Preserving Zero-Shot Multiple Accent Conversion", "mode": "feasibility"},
    {"task_id": "SDK-VOCOS", "title": "Vocos", "mode": "implementation"},
    {"task_id": "SDK-CONTENTVEC", "title": "ContentVec", "mode": "feasibility"},
    {"task_id": "SDK-QUICKVC", "title": "QuickVC", "mode": "feasibility"},
    {"task_id": "SDK-HUBERT-CONVERSION-ENCODER", "title": "HuBERT conversion encoder", "mode": "feasibility"},
    {"task_id": "SDK-WAVLM-CONVERSION-ENCODER", "title": "WavLM conversion encoder", "mode": "feasibility"},
    {"task_id": "SDK-YOURTTS", "title": "YourTTS", "mode": "feasibility"},
    {"task_id": "SDK-VITS-STREAMING-ADAPTATION", "title": "VITS streaming adaptation", "mode": "feasibility"},
    {"task_id": "SDK-RVC-V2-VCTK-P226", "title": "RVC v2 VCTK p226", "mode": "implementation"},
    {"task_id": "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER", "title": "Seed-VC XLS-R-300M content encoder", "mode": "implementation"},
    {"task_id": "SDK-UNIVNET", "title": "UnivNet", "mode": "feasibility"},
    {"task_id": "SDK-MICRO-HIFI-GAN", "title": "Micro-HiFi-GAN", "mode": "feasibility"},
    {"task_id": "SDK-MS-ISTFT-GENERATOR", "title": "MS-iSTFT-Generator", "mode": "feasibility"},
    {"task_id": "SDK-FREGAN", "title": "FreGAN", "mode": "feasibility"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-cleared multi-accent speech cohort with consented target-accent references, manual transcripts and explicit output-use terms"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen development/held-out accent and speaker partitions with independent blinded listening and manual transcript review"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched identity, generic-VC, duration/pitch-only and accent-classifier controls with uncertainty"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned TokAN, MeanVC2, Seed-VC and Vocos bundles, exact revisions, runtime and per-weight terms"},
    {"id": "RG-05", "blocked": True, "requirement": "Causal streaming chunk/lookahead, first-output/tail, sustained CPU/accelerator and target-device timing evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit pronunciation-change policy separating intended accent change from content, identity, naturalness and consent"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider or external-adapter intake with independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "TRN-03 \u2014 Accent conversion",
        "Declare intended pronunciation changes and preserve content/identity.",
        "Streaming labels do not establish low conversational delay.",
    ],
    "research/category_survey/sources.md": [
        "| S36 | [Classical accent conversion study](https://www.isca-archive.org/eurospeech_2003/yan03d_eurospeech.html) | transformations | direct |",
        "| S37 | [Streaming accent conversion study](https://arxiv.org/html/2506.16580v1) | transformations | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Voice | Freeze permitted input and target references, task and language/speaker groups.",
        "Consent, reference availability and output use are independent gates.",
    ],
    "research/accent-conversion-20261101/README.md": [
        "Status: **local runnable-model smoke tests and objective checks complete**",
        "Three authors' accent-labeled English utterances were downloaded",
        "All three generated finite 24 kHz mono WAVs.",
        "The results do **not** show consistent movement toward General American.",
        "254.01 s; conversion of the first block took 22.21 s, or 92.55\u00d7 real-time.",
        "`FileNotFoundError` for `wavlm_large.pt`, confirming the asset blocker.",
        "was 173 ms (RTF 0.175); output was finite and 0.99 s long.",
        "L2-ARCTIC is a non-native English research corpus",
        "The paper's 80 ms chunk-plus-lookahead figure",
        "Human listening remains outstanding",
        "separate Seed-VC V2 accent-conversion path.",
        "no blanket license for its mixed-source",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "| RVC | Practical trained-target real-time VC | `repos/rvc` | Public VCTK multi-speaker checkpoint | Partial |",
        "target-speaker index mapping is inferred",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/soundtouch/README.md": [
        "paired Whisper context; historical, not re-measured here.",
    ],
    "docs/task-evidence/survey-trn-01/README.md": [
        "read-only survey map",
        "pitch preservation, transient audibility, listening, device timing, public",
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
    "historical_citations_include_real_speech": True,
    "historical_citations_include_research_outputs": True,
    "real_speech_used_here": False,
    "real_corpus_used_here": False,
    "weights_loaded_here": False,
    "runtime_invoked_here": False,
    "model_inference_here": False,
    "streaming_inference_here": False,
    "listening_here": False,
    "device_timing_here": False,
    "latency_claim": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "accent_conversion_quality_claim": False,
    "accent_reduction_claim": False,
    "content_preservation_claim": False,
    "identity_preservation_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

NON_CLAIMS: List[str] = [
    "no accent conversion quality, accent-reduction or model-ranking result is measured by this survey",
    "no independent listening panel, manual transcript review or target-accent gold exists",
    "no sustained streaming, first-output/tail or device timing is measured",
    "no speaker identity rating, content-preservation certificate or consent clearance is produced",
    "no real corpus, weights or runtime is loaded in this task",
    "no benchmark, latency, quality or release claim is made",
    "no provider, default, ABI, build, CI, board or handoff change is made",
]

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "missing_required_cohort_promoted": "rejected; state unchanged",
    "streaming_execution_promoted": "rejected; state unchanged",
    "listening_or_identity_result_promoted": "rejected; state unchanged",
    "generic_vc_promoted_to_accent_conversion": "rejected; state unchanged",
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
        raise MapError("TRN-03 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("TRN-03 taxonomy mismatch: %s" % key)
    if inventory_hit[0].get("task") != TASK:
        raise MapError("TRN-03 inventory task mismatch")
    if inventory_hit[0].get("legacy_family") != LEGACY_FAMILY:
        raise MapError("TRN-03 legacy family mismatch")
    if inventory_hit[0].get("legacy_backlog_state") != "catalogued":
        raise MapError("TRN-03 legacy backlog state mismatch")
    source_index = {s["id"]: s for s in registry["sources"]}
    for lead in SOURCE_LEADS:
        source = source_index.get(lead["source_id"])
        if source is None:
            raise MapError("registry source lead is missing: " + lead["source_id"])
        for key in ("title", "url", "access_scope"):
            if source.get(key) != lead[key]:
                raise MapError("source lead mismatch: %s/%s" % (lead["source_id"], key))
    if set(CATEGORY_FACTS["source_ids"]) != {lead["source_id"] for lead in SOURCE_LEADS}:
        raise MapError("category source ids and mapped source leads differ")


def _check_backlog(workspace: Path) -> None:
    backlog = strict_json_load(workspace / "research/task_backlog.json")
    hits = [
        e
        for e in backlog["entries"]
        if e.get("family_id") == LEGACY_FAMILY and e.get("category_id") == CATEGORY_ID
    ]
    if len(hits) != 1:
        raise MapError("legacy family F14 / TRN-03 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "family_id": LEGACY_FAMILY,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "requested_transform",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F14/TRN-03/%s" % key)


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
        if not row.get("role"):
            raise MapError("census row has no role: " + row["component_id"])
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    uncensused = sorted(mapped - {row["component_id"] for row in COMPONENT_CENSUS})
    if uncensused:
        raise MapError("mapped component is not censused: " + ",".join(uncensused))


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
        if row.get("scope_class") != "historical_research_execution":
            raise MapError("historical execution is not labelled research: " + row["id"])
        if row.get("merged_task_evidence") is not False:
            raise MapError("historical execution is promoted to merged evidence: " + row["id"])
        if row.get("not_rerun") is not True:
            raise MapError("historical execution is not marked unrerun: " + row["id"])
        if not row.get("evidence_role"):
            raise MapError("historical execution has no evidence role: " + row["id"])
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
        "real_accent_conversion_corpus_benchmark",
        "human_listening_result",
        "independent_human_transcript_review",
        "target_accent_gold",
        "speaker_identity_gold",
        "accent_classifier_calibration",
        "streaming_accent_conversion_execution",
        "sustained_stream_latency",
        "device_timing",
        "cpu_accelerator_parity",
        "latency_claim",
        "quality_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "provider_enablement",
        "release_approval",
    }
    for key in critical_false:
        if EVIDENCE_CLASSES.get(key) is not False:
            raise MapError("unsupported evidence class is not false: " + key)


def _check_scope_integrity() -> None:
    if DECISION != "DEFER" or STATUS != "proposal_only_survey_incomplete":
        raise MapError("disposition constants changed")
    if QUALIFICATION_STATUS != "not_qualified" or READINESS != "incomplete":
        raise MapError("qualification constants changed")
    if len(RELEASE_GATES) != 8:
        raise MapError("release gate count is not eight")
    if [gate["id"] for gate in RELEASE_GATES] != ["RG-0%d" % k for k in range(1, 9)]:
        raise MapError("release gate ids changed")
    if any(gate["blocked"] is not True for gate in RELEASE_GATES):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in BOUNDARY.values()):
        raise MapError("boundary is not closed")
    for key in (
        "real_speech_used_here",
        "real_corpus_used_here",
        "weights_loaded_here",
        "runtime_invoked_here",
        "model_inference_here",
        "streaming_inference_here",
        "listening_here",
        "device_timing_here",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "accent_conversion_quality_claim",
        "accent_reduction_claim",
        "content_preservation_claim",
        "identity_preservation_claim",
        "network_access",
    ):
        if SCOPE.get(key) is not False:
            raise MapError("scope must stay closed: " + key)
    for key in (
        "task_local_only",
        "documentation_and_metadata_only",
        "no_new_execution",
        "historical_citations_include_real_speech",
        "historical_citations_include_research_outputs",
    ):
        if SCOPE.get(key) is not True:
            raise MapError("scope must stay true: " + key)
    if not NON_CLAIMS:
        raise MapError("non-claims are missing")


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
    gap_ids = {gap["id"] for gap in GAPS}
    if len(gap_ids) != len(GAPS):
        raise MapError("duplicate gap id")
    linked_gaps = set()
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
            linked_gaps.add(task_id)
        if gap.get("feasibility_task_exists"):
            modes = {next(t["mode"] for t in BOARD_LINKS if t["task_id"] == tid) for tid in gap["follow_up_ids"]}
            if "feasibility" not in modes:
                raise MapError("gap claims a feasibility follow-up without one: " + gap["id"])
        elif not gap.get("owner_note"):
            raise MapError("gap without feasibility task has no owner note: " + gap["id"])
    for source in SOURCE_LEADS:
        for gap_id in source["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("source lead links unknown gap: " + gap_id)
    for family in METHOD_FAMILIES:
        for gap_id in family["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("method family links unknown gap: " + gap_id)
    for link in BOARD_LINKS:
        if link["task_id"] not in linked_gaps:
            raise MapError("board link has no gap: " + link["task_id"])
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
    _check_scope_integrity()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
        linked = sorted(g["id"] for g in GAPS if link["task_id"] in g["follow_up_ids"])
        links.append(
            {
                "task_id": link["task_id"],
                "title": link["title"],
                "mode": link["mode"],
                "linked_gaps": linked,
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
            "qualification_status": QUALIFICATION_STATUS,
            "readiness": READINESS,
            "survey_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "decision": DECISION,
            "processor_exposure": False,
            "missing_result_promoted": False,
            "release_qualification_present": False,
            "accent_conversion_evaluation_present": False,
            "streaming_accent_conversion_present": False,
            "human_listening_present": False,
            "identity_gold_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "category_scope": dict(CATEGORY_SCOPE),
        "non_claims": list(NON_CLAIMS),
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
        "excluded_boundaries": [dict(row) for row in EXCLUDED_BOUNDARIES],
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
            "check": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py check",
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
    if report["qualification"]["qualification_status"] != QUALIFICATION_STATUS:
        raise MapError("qualification_status changed")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count is not eight")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if report["scope"]["no_new_execution"] is not True:
        raise MapError("survey claims a new execution")
    if report["scope"]["accent_conversion_quality_claim"] is not False:
        raise MapError("accent conversion quality is claimed")
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
