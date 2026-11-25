# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-REC-01.

This module builds a bounded taxonomy/comparison evidence map for the speech
recognition / transcription category (inventory category ``REC-01``, legacy
family ``F11``). It reads only pinned, read-only documents from the enclosing
``audioml`` workspace and the SDK worktree. It does not load audio, weights,
models, runtimes, media or the network, and it does not register, expose,
enable or qualify any recognizer.

All curated records below are documentation mappings, not new measurements.
Historical research or source-reported values are transcribed verbatim from the
pinned documents and labelled with their original scope. A transcript is not an
independent human reference; a word-timestamp comparison against another forced
alignment is not timing gold; a content gate is not a recognizer.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-REC-01"
TITLE = "Review coverage for Speech recognition / transcription (ASR/STT)"
CATEGORY_ID = "REC-01"
LEGACY_FAMILY = "F11"
BRANCH = "swarm/SDK-SURVEY-REC-01"
BASE_COMMIT = "871201c187c42291410245344aacee5c80051b48"
PROFILE = "Analysis"
COMPONENT = "speech-recognition-transcription-evidence-map"
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
# verifies media, weights or transcripts that are not present in this task
# directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "cpp-library/pipeline-validation/playback-speed/README.md": "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-text/REPORT.md": "86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
}

# SDK-worktree-relative boundary pins. They are read only to prove that no
# public surface was touched and to ground the cited task-local evidence.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/rubber-band-r3-offline/README.md": "de528246089b9f0d2a1ea597ac0cbbb119d5541b2b22a0a383b4d03b7a85aeab",
    "docs/task-evidence/soundtouch/README.md": "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/survey-det-02/README.md": "40c05936132ed4add0d1a97a9139f42c170711130c447f18d36b11c7669221b1",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Recognition and language",
    "name": "Speech recognition / transcription (ASR/STT)",
    "scope": "requested_optional",
    "output_kind": "annotation",
    "purpose": "Produce words and optional timestamps/confidence.",
    "method_families": {
        "classic": "Traditional statistical recognition families to enumerate",
        "ml": "Encoder-decoder, CTC/transducer and joint recognition families",
    },
    "input_output": "Audio \u2192 transcript and optional timing",
    "live_or_comparison_boundary": (
        "File transcription is not proof of causal streaming. Keep "
        "partial/final timing and word preservation distinct from listening "
        "quality."
    ),
    "source_ids": ["S09", "S11", "S47"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "REC",
    "meaning": "Recognition and language",
    "category_id": CATEGORY_ID,
    "words_and_optional_timestamps_confidence_only": True,
    "file_transcription_is_not_causal_streaming": True,
    "partial_and_final_timing_are_distinct": True,
    "word_preservation_is_not_listening_quality": True,
    "not_language_identification_or_code_switch": "REC-02",
    "not_speaker_diarization": "SPK-04",
    "not_utterance_endpointing_or_turn_completion": "DET-02",
    "not_speech_activity_detection": "DET-01",
    "not_speech_enhancement": "CLN-01",
    "not_translation": "boundary",
    "not_listening_quality_assessment": "OBS-01",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S09",
        "title": "Whisper official implementation",
        "url": "https://github.com/openai/whisper",
        "access_scope": "direct",
        "mapped_components": [
            "whisper-transcription",
            "whisper-tiny-en-int8-via-sherpa-onnx",
            "whisper-tiny-en-mfa",
            "crisperwhisper",
        ],
        "gap_ids": ["G01", "G04", "G07", "G10"],
        "finding": (
            "Direct documentation lead for an encoder-decoder file-transcription "
            "family. The pinned research notes describe one 15 s crop and a "
            "ten-clip fixed-scorer screen using openai-whisper tiny.en and "
            "sherpa-onnx int8 exports. No exact upstream revision, runtime, "
            "weight terms, streaming configuration or broad WER result is "
            "present in this task; the model is never loaded here."
        ),
    },
    {
        "source_id": "S11",
        "title": "Code-switching speech recognition study",
        "url": "https://www.isca-archive.org/interspeech_2019/zeng19_interspeech.html",
        "access_scope": "direct",
        "mapped_components": ["speech-recognition-translation-controls"],
        "gap_ids": ["G06", "G10"],
        "finding": (
            "Direct external study lead for code-switch handling. No local "
            "code-switched audio, language boundary labels, script/normalization "
            "policy or recognizer execution exists; the study defines candidate "
            "scope only and is not parsed into a local result."
        ),
    },
    {
        "source_id": "S47",
        "title": "CHiME-8 meeting transcription pipeline",
        "url": "https://www.chimechallenge.org/challenges/chime8/task1/index",
        "access_scope": "direct",
        "mapped_components": [
            "whisper-transcription",
            "speech-recognition-translation-controls",
        ],
        "gap_ids": ["G05", "G08", "G12"],
        "finding": (
            "Direct evaluation-protocol lead for meeting transcription with "
            "overlap and diarization. No CHiME-8 corpus, array/headset layout, "
            "reference transcript, diarization output, scorer or local pipeline "
            "is staged; meeting transcription is not claimed from a file-level "
            "Whisper crop."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "HMM/DNN-HMM acoustic modeling with a pronunciation lexicon and "
            "n-gram decoding (traditional statistical recognition)"
        ),
        "components": ["vosk", "vosk-small-en-us-0-15-playback-gate"],
        "gap_ids": ["G01", "G02", "G05", "G10", "G11"],
        "status": "historical_local_content_gate_only_no_asr_evaluation",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Feature front end, pronunciation lexicon and forced alignment used "
            "as a timing reference, not as recognition"
        ),
        "components": [
            "whisper-timestamp-and-mfa-tooling",
            "whisper-tiny-en-mfa",
        ],
        "gap_ids": ["G02", "G07"],
        "status": "historical_local_alignment_reference_only",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Encoder-decoder attention recognition with offline file "
            "transcription (Whisper-style)"
        ),
        "components": [
            "whisper-transcription",
            "whisper-tiny-en-int8-via-sherpa-onnx",
            "whisper-tiny-en-mfa",
            "crisperwhisper",
        ],
        "gap_ids": ["G01", "G02", "G04", "G07", "G09", "G10"],
        "status": "historical_local_single_crop_and_fixed_scorer_only",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "CTC, transducer and Conformer streaming recognition",
        "components": [
            "whisper-streaming",
            "simulstreaming",
            "streaming-conformer-ted",
            "fastconformer-streaming-asr",
        ],
        "gap_ids": ["G03", "G11", "G12"],
        "status": "blocked_no_checkpoint_runtime_or_adapter",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": (
            "Meeting transcription with diarization and overlap handling "
            "(named source lead S47)"
        ),
        "components": [
            "speech-recognition-translation-controls",
            "whisper-transcription",
        ],
        "gap_ids": ["G05", "G08"],
        "status": "documented_pipeline_no_local_execution",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": (
            "Code-switching and multilingual recognition (named source lead "
            "S11)"
        ),
        "components": ["speech-recognition-translation-controls"],
        "gap_ids": ["G06", "G10"],
        "status": "documented_study_no_local_execution",
    },
]

# component_id, task and evidence_status are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "vosk", "role": "classic_statistical_recognizer_lead", "evidence_status": "considered", "task": "SDK-VOSK"},
    {"component_id": "vosk-small-en-us-0-15-playback-gate", "role": "adjacent_content_gate_and_word_boundaries", "evidence_status": "partial", "task": "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE"},
    {"component_id": "whisper-timestamp-and-mfa-tooling", "role": "alignment_and_timestamp_tooling", "evidence_status": "partial", "task": "SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING"},
    {"component_id": "whisper-tiny-en-mfa", "role": "historical_asr_and_alignment_reference", "evidence_status": "evaluated", "task": "SDK-WHISPER-TINY-EN-MFA"},
    {"component_id": "whisper-transcription", "role": "offline_asr_research_control", "evidence_status": "partial", "task": "SDK-WHISPER-TRANSCRIPTION"},
    {"component_id": "whisper-tiny-en-int8-via-sherpa-onnx", "role": "offline_asr_fixed_scorer", "evidence_status": "partial", "task": "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX"},
    {"component_id": "crisperwhisper", "role": "noncommercial_asr_lead", "evidence_status": "considered", "task": "SDK-CRISPERWHISPER"},
    {"component_id": "whisper-streaming", "role": "streaming_asr_lead", "evidence_status": "blocked", "task": "SDK-WHISPER-STREAMING"},
    {"component_id": "simulstreaming", "role": "streaming_asr_lead", "evidence_status": "blocked", "task": "SDK-SIMULSTREAMING"},
    {"component_id": "streaming-conformer-ted", "role": "streaming_asr_lead", "evidence_status": "blocked", "task": "SDK-STREAMING-CONFORMER-TED"},
    {"component_id": "fastconformer-streaming-asr", "role": "streaming_asr_lead", "evidence_status": "blocked", "task": "SDK-FASTCONFORMER-STREAMING-ASR"},
    {"component_id": "speech-recognition-translation-controls", "role": "typed_transcript_tool_boundary", "evidence_status": "considered", "task": "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS"},
    {"component_id": "asr-word-timestamps", "role": "word_timing_boundary", "evidence_status": "considered", "task": "SDK-ASR-WORD-TIMESTAMPS"},
    {"component_id": "aix-speed-asr-guided-planner", "role": "adjacent_rate_control", "evidence_status": "considered", "task": "SDK-AIX-SPEED-ASR-GUIDED-PLANNER"},
]

EXCLUDED_BOUNDARIES: List[Dict[str, str]] = [
    {
        "boundary": "Language identification and code-switch handling (REC-02)",
        "reason": "A recognition transcript is not a language label, a code-switch point or a language-boundary segment.",
    },
    {
        "boundary": "Speaker diarization and speaker change (SPK-04 / SPK-03)",
        "reason": "A word stream with timestamps does not identify who spoke or resolve overlapped speech.",
    },
    {
        "boundary": "Utterance endpointing, ASR segmentation and turn completion (DET-02)",
        "reason": "ASR segmentation and streaming endpointing are not a conversational turn decision.",
    },
    {
        "boundary": "Speech activity detection (DET-01)",
        "reason": "Framewise activity is an upstream trigger, never a word or transcript.",
    },
    {
        "boundary": "Listening quality, translation and speech enhancement (OBS-01 / CLN-01)",
        "reason": "Word error or transcript drift is not comprehension, naturalness, translation quality or an enhanced waveform.",
    },
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "One 15 s AMI EN2003a channel-0 crop with a 34-word reference transcript",
        "class": "historical_research_single_crop_asr_alignment",
        "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md",
        "boundary": "One English meeting crop, one model revision and one reference transcript; not a broad accuracy, accent, language, noise or device result.",
    },
    {
        "id": "CI-2",
        "input": "Ten 4 s AMI crops, 136 reference words and 90 paired Whisper decode conditions",
        "class": "historical_research_fixed_scorer_asr",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "Whisper is a fixed scorer for stretched audio; the paired WER deltas do not rank ASR models or measure comprehension.",
    },
    {
        "id": "CI-3",
        "input": "Two synthetic TTS clips with exact transcripts and one 39.2 s real AMI stitched clip without a reference transcript",
        "class": "historical_research_transcript_drift_scorer",
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
        "boundary": "The int8 Whisper scorer runs offline on source and output; TTS dominates the corpus and the real clip has no reference transcript.",
    },
    {
        "id": "CI-4",
        "input": "Two TTS clips with construction-time speech/filler/pause labels for a Vosk content gate",
        "class": "historical_research_vosk_gate_boundaries",
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
        "boundary": "Block-level gate IoU only; the gate is a poor production boundary source and is not a transcript, speaker or recognition result.",
    },
    {
        "id": "CI-5",
        "input": "Whisper official implementation documentation (S09)",
        "class": "source_reported_model_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation describes the family; no local runtime, exact revision, weight terms, cohort or numeric parity follows.",
    },
    {
        "id": "CI-6",
        "input": "CHiME-8 meeting transcription pipeline (S47)",
        "class": "source_reported_external_pipeline",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "External protocol lead only; no corpus, array layout, diarization output, scorer or local meeting-transcription run.",
    },
    {
        "id": "CI-7",
        "input": "Code-switching speech recognition study (S11)",
        "class": "source_reported_external_study",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "External study lead only; no code-switched audio, language labels, normalization policy or local execution.",
    },
    {
        "id": "CI-8",
        "input": "Rights-qualified multi-domain ASR corpus with independent human transcripts, word timestamps and confidence",
        "class": "missing_required_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Not present in this task or the pinned research; no local asset, annotation, split or normalization is staged.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "source/identity transcript", "role": "Whisper decode of the unmodified source crop; the fixed reference for paired WER deltas.", "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md"},
    {"id": "CT-2", "name": "oracle transcript plus MFA alignment", "role": "Upper-bound timing control using the reference text; MFA is not an audio-only recognizer.", "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md"},
    {"id": "CT-3", "name": "paired per-clip WER delta", "role": "Uses the same scorer and reference for each source/output pair so pooled source errors are separated.", "source_pin": "research/tsm-followup-20261101/README.md"},
    {"id": "CT-4", "name": "fixed_1.25 and slow_only playback controls", "role": "Adjacent duration controls; their WER is transcript-drift context, not a recognition control.", "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md"},
    {"id": "CT-5", "name": "construction-time Vosk gate labels", "role": "Block labels expose false-speech and missed-speech behaviour; the gate alone is not a production boundary source.", "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md"},
    {"id": "CT-6", "name": "blocked streaming rows without substitution", "role": "Candidate identity is preserved; no other Conformer or Whisper runtime is silently substituted.", "source_pin": "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "15 s AMI EN2003a channel-0 crop",
        "class": "research_audio",
        "status": "CC BY 4.0 per the cited report; local only and not redistributed; 34-word reference transcript is corpus text",
        "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md",
    },
    {
        "asset": "Ten 4 s AMI EN2003a speech-heavy crops",
        "class": "research_audio",
        "status": "CC BY 4.0 per the cited report; local only; 136 reference words; no redistributed audio",
        "source_pin": "research/tsm-followup-20261101/README.md",
    },
    {
        "asset": "Two synthetic TTS playback clips",
        "class": "workspace_synthetic_audio",
        "status": "macOS say Samantha at 300/285 wpm with exact construction-time words, fillers and pause spans; not real speech",
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
    },
    {
        "asset": "39.2 s real AMI stitched playback clip",
        "class": "workspace_research_audio",
        "status": "Eight real AMI EN2003a 4 s crops with 0.9 s gaps; no reference transcript",
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
    },
    {
        "asset": "OpenAI Whisper tiny.en weights",
        "class": "external_weights_metadata_only",
        "status": "MIT code and OpenAI model terms; weight SHA-256 recorded in the pinned report; not staged, loaded or redistributed here",
        "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md",
    },
    {
        "asset": "MFA 3.4.3 English US ARPA acoustic model and dictionary",
        "class": "external_model_metadata_only",
        "status": "Model card states CC-BY-4.0; hashes recorded in the pinned report; not staged or loaded here",
        "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md",
    },
    {
        "asset": "Vosk vosk-model-small-en-us-0.15",
        "class": "external_model_metadata_only",
        "status": "Apache-2.0 code with model terms to check separately; not staged or loaded here",
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
    },
    {
        "asset": "Rights-qualified multi-domain ASR corpus with independent human transcripts and confidence",
        "class": "missing_asset",
        "status": "No rights-qualified corpus, independent reference, speaker/domain split or confidence label is staged",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Whisper tiny.en plus MFA on one 15 s AMI crop",
        "outcome_class": "historical_research_single_crop_asr_alignment",
        "component_ids": [
            "whisper-tiny-en-mfa",
            "whisper-timestamp-and-mfa-tooling",
        ],
        "source_pin": "research/tsm-followup-20261101/agent-text/REPORT.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "asr_candidate_and_alignment_reference",
        "values": {
            "crop_start_s": 16,
            "crop_duration_s": 15,
            "reference_words": 34,
            "whisper_word_errors": 4,
            "whisper_wer_percent": 11.76,
            "whisper_cpu_inference_s": 1.445,
            "whisper_model_load_s": 0.839,
            "whisper_rtf_excluding_load": 0.096,
            "oracle_words_matched": 33,
            "oracle_missing_oov": 1,
            "oracle_boundary_mae_ms": 23.79,
            "oracle_boundary_median_ms": 10,
            "oracle_within_50ms_percent": 89.4,
            "asr_words_matched": 30,
            "asr_boundary_mae_ms": 23.17,
            "asr_boundary_median_ms": 10,
            "asr_within_50ms_percent": 91.7,
            "audio_sha256": "a8fcab8547e24376367f97ce5967318e18cc6e052fe3f89934ff037dc90bd9ca",
        },
        "scope": (
            "One English meeting crop evaluated once; the AMI timing reference is "
            "itself forced alignment and was not manually corrected. The reported "
            "11.76% WER is four errors over 34 words and is not a general ASR "
            "accuracy, accent, language, noise or device result. No audio, weight "
            "or runtime is loaded here; not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Paired Whisper tiny.en fixed-scorer screen on ten AMI crops",
        "outcome_class": "historical_research_fixed_scorer_asr",
        "component_ids": ["whisper-transcription"],
        "source_pin": "research/tsm-followup-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "asr_fixed_scorer",
        "values": {
            "clips": 10,
            "clip_duration_s": 4,
            "reference_words": 136,
            "paired_conditions": 90,
            "rate_factors": 2,
            "source_wer_percent_tsm_summary": 30.15,
            "source_wer_percent_agent_text": 30.1,
            "source_word_errors": 41,
            "bungee_delta_1_25_pp": 0.0,
            "bungee_delta_1_5_pp": 2.9,
            "soundtouch_delta_1_25_pp": 0.0,
            "soundtouch_delta_1_5_pp": 7.4,
            "rubber_band_delta_1_25_pp": 0.7,
            "rubber_band_delta_1_5_pp": 3.7,
            "psola_delta_1_25_pp": 0.7,
            "psola_delta_1_5_pp": 1.5,
        },
        "scope": (
            "Ten short clips from one meeting and 136 reference words; Whisper is "
            "the fixed scorer for time-scaled audio. The high source WER and "
            "per-clip variation limit interpretation, and no confidence interval "
            "or listening panel exists. not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Whisper tiny.en int8 sherpa-onnx transcript-drift scorer",
        "outcome_class": "historical_research_transcript_drift_scorer",
        "component_ids": ["whisper-tiny-en-int8-via-sherpa-onnx"],
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "asr_fixed_scorer",
        "values": {
            "clips": 3,
            "synthetic_tts_clips": 2,
            "real_ami_clip": 1,
            "source_median_wer_percent_low": 3.5,
            "source_median_wer_percent_high": 6.1,
            "d1_median_wer_percent": 3.5,
            "d2_median_wer_percent": 3.9,
            "d1_oracle_median_wer_percent": 6.5,
            "fixed_1_25_median_wer_percent": 7.4,
            "slow_only_median_wer_percent": 5.2,
            "block_ms": 100,
            "total_blocks": 15708,
            "deadline_misses": 0,
            "real_clip_reference_transcript": False,
        },
        "scope": (
            "Offline scoring only; the scorer is outside the playback chain. Two "
            "of three clips are synthetic TTS and the real clip has no reference "
            "transcript, so the WER proxy does not establish comprehension, "
            "naturalness or a recognition result. not rerun by this survey."
        ),
    },
    {
        "id": "HE-4",
        "label": "Vosk small-en-us-0.15 content-gate boundary screen",
        "outcome_class": "historical_research_vosk_gate_boundaries",
        "component_ids": [
            "vosk-small-en-us-0-15-playback-gate",
            "vosk",
        ],
        "source_pin": "cpp-library/pipeline-validation/playback-speed/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "adjacent_content_gate",
        "values": {
            "synthetic_tts_clips": 2,
            "gate_iou_low": 0.94,
            "gate_iou_high": 0.95,
            "false_speech_blocks": 12,
            "missed_speech_blocks": 24,
            "labeled_blocks_clip_a": 345,
            "labeled_blocks_clip_b": 467,
            "batch_gate_rtf": 0.056,
            "production_boundary_source": False,
        },
        "scope": (
            "Construction-time block labels on two TTS clips; the gate is "
            "adequate only for coarse 100 ms policy and would be a poor "
            "production boundary source. There is no reference transcript, "
            "speaker label or recognition score. not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Whisper official implementation and its file-transcription family",
        "class": "source_reported_model_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct documentation scope; no local runtime, exact upstream revision, weight terms, cohort or numeric parity.",
    },
    {
        "id": "RO-2",
        "claim": "CHiME-8 meeting transcription pipeline",
        "class": "source_reported_external_pipeline",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "External challenge protocol only; no local CHiME corpus, array/headset layout, diarization or scorer.",
    },
    {
        "id": "RO-3",
        "claim": "Code-switching speech recognition study",
        "class": "source_reported_external_study",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "External paper only; no local code-switched audio, language labels, script mapping or execution.",
    },
    {
        "id": "RO-4",
        "claim": "CrisperWhisper candidate",
        "class": "source_reported_licence_constraint",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Inventory row records non-commercial weights and an offline annotation lead; no checkpoint, runtime or permission is present.",
    },
    {
        "id": "RO-5",
        "claim": "Whisper-Streaming, SimulStreaming, Streaming Conformer-TED and FastConformer leads",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
        "boundary": "Blocked rows with no local checkpoint, streaming runtime or adapter; no substitute model was used and no WER/latency result exists.",
    },
    {
        "id": "RO-6",
        "claim": "Whisper Tiny English WER on voice-conversion outputs",
        "class": "source_reported_cross_task_asr_scoring",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "Cross-task scoring of one short converted utterance; it is recognition context, not an ASR benchmark or a naturalness/speaker result.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "timestamped_probabilities_and_events": "HE-1 transcribes word boundaries from one crop; no calibrated word, segment or confidence probability exists",
        "quiet_and_active_speech": "Historical rows use AMI meeting speech and synthetic TTS; no quiet, far-field, overlapping, accented or multilingual stratum is staged",
        "known_positives_and_negatives": "CI-1 and CI-2 have narrow reference transcripts; no speaker/domain-disjoint known-negative set or confidence-labelled non-speech exists",
        "onset_offset_delay": "HE-1 reports MFA boundary deviation against AMI forced alignment, not independent human gold; streaming partial/final commit delay is unmeasured",
        "stratified_fn_fp": "Only pooled WER and per-clip WER deltas exist; substitutions, deletions, insertions, entity errors and confidence-stratified FN/FP are absent",
        "validity_vs_nonspeech": "Unlabelled or missing audio is unknown, never an empty transcript or non-speech; no local validity flag or abstention policy is staged",
        "exact_source_intervals": "Historical word spans come from MFA and AMI alignments; no task-local half-open sample interval or cross-hop parity is produced",
        "independent_state": "Offline single-shot inference only; streaming decoder state, chunk reset, partial hypotheses and failover are untested",
        "availability_and_dropped_stale_events": "Historical offline runs expose no capture/decoder availability clock, dropped chunk, stale partial or maximum-wait audit",
        "cross_hop_behavior": "Offline 15 s and 4 s crops are not aligned to 160-sample v0 frames or a paced 100 ms stream; no cross-hop parity is claimed",
    },
    "blocked": [
        "Rights-qualified multi-domain ASR corpus with independent human transcripts, word timestamps, confidence and explicit unknown/non-speech regions",
        "Frozen speaker/session/domain-disjoint development and held-out partitions with a documented text-normalization policy",
        "Matched identity/source-transcript, oracle-alignment, fixed-decoder and alternative-model controls with stratified WER/CER and uncertainty",
        "Pinned real ASR runtimes, weights and exact revisions with per-weight terms for Whisper, Vosk, MFA and CrisperWhisper",
        "Paced causal streaming state, partial/final commit, maximum-wait, dropped/stale chunk and target-device availability evidence",
        "Confidence calibration, abstention/unknown policy and independent word-preservation review on frozen cohorts",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class is
# true only when a mapped row backs it; absence is recorded as false instead of
# being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "historical_research_single_crop_asr_alignment": True,
    "historical_research_fixed_scorer_asr": True,
    "historical_research_transcript_drift_scorer": True,
    "historical_research_vosk_gate_boundaries": True,
    "source_reported_model_documentation": True,
    "source_reported_external_pipeline": True,
    "source_reported_external_study": True,
    "source_reported_licence_constraint": True,
    "source_reported_blocked_candidate": True,
    "source_reported_cross_task_asr_scoring": True,
    "real_asr_corpus_benchmark": False,
    "human_reference_transcript_review": False,
    "streaming_asr_execution": False,
    "word_timestamp_gold": False,
    "confidence_calibration": False,
    "multi_domain_or_language_coverage": False,
    "code_switch_execution": False,
    "meeting_transcription_execution": False,
    "entity_error_evaluation": False,
    "human_listening_result": False,
    "device_timing": False,
    "latency_claim": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "asr_accuracy_claim": False,
}

# True evidence classes must be backed by at least one row class; false classes
# must not be backed. This keeps a missing result from being promoted.
CLASS_BACKING: Dict[str, List[str]] = {
    "historical_research_single_crop_asr_alignment": [
        "historical_research_single_crop_asr_alignment"
    ],
    "historical_research_fixed_scorer_asr": [
        "historical_research_fixed_scorer_asr"
    ],
    "historical_research_transcript_drift_scorer": [
        "historical_research_transcript_drift_scorer"
    ],
    "historical_research_vosk_gate_boundaries": [
        "historical_research_vosk_gate_boundaries"
    ],
    "source_reported_model_documentation": [
        "source_reported_model_documentation"
    ],
    "source_reported_external_pipeline": [
        "source_reported_external_pipeline"
    ],
    "source_reported_external_study": [
        "source_reported_external_study"
    ],
    "source_reported_licence_constraint": [
        "source_reported_licence_constraint"
    ],
    "source_reported_blocked_candidate": [
        "source_reported_blocked_candidate"
    ],
    "source_reported_cross_task_asr_scoring": [
        "source_reported_cross_task_asr_scoring"
    ],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a rights-qualified multi-domain ASR corpus with independent human transcripts, word timestamps, confidence and explicit unknown regions",
        "evidence_gap": "Historical rows use one 15 s crop, ten 4 s crops and synthetic TTS; no independent reference, speaker/domain split or confidence label is staged.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-VOSK",
            "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked evidence foundation and Vosk feasibility rows own scoring rules and a classical recognizer lead; neither supplies a rights-qualified corpus or independent transcript here.",
    },
    {
        "id": "G02",
        "actionable_gap": "Define and score recognition beyond pooled WER: stratified WER/CER, substitutions/deletions/insertions, entity errors, word preservation and uncertainty",
        "evidence_gap": "Only pooled WER and four-engine paired deltas over 136 words exist; no stratified, entity, uncertainty or word-preservation result is present.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-ASR-WORD-TIMESTAMPS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked evidence foundation and word-timestamp feasibility row own acceptance rules and timing proxies; neither defines a complete recognition metric.",
    },
    {
        "id": "G03",
        "actionable_gap": "Establish causal streaming ASR chunking, decoder state, partial/final commit, maximum wait and dropped-stale chunk behaviour",
        "evidence_gap": "Whisper-Streaming, SimulStreaming, Streaming Conformer-TED and FastConformer are blocked; no checkpoint, streaming runtime, adapter or partial-hypothesis trace exists.",
        "follow_up_ids": [
            "SDK-WHISPER-STREAMING",
            "SDK-SIMULSTREAMING",
            "SDK-STREAMING-CONFORMER-TED",
            "SDK-FASTCONFORMER-STREAMING-ASR",
            "SDK-FND-TIMING",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked streaming-ASR feasibility rows own the exact candidates; file transcription is not treated as causal streaming.",
    },
    {
        "id": "G04",
        "actionable_gap": "Pin the Whisper source lead and reproduce one bounded offline run with exact revision, runtime, weight terms and normalization",
        "evidence_gap": "S09 is documentation only; the historical runs cite a local environment and a weight hash but no upstream revision or reproducible task-local bundle.",
        "follow_up_ids": [
            "SDK-WHISPER-TRANSCRIPTION",
            "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX",
            "SDK-WHISPER-TINY-EN-MFA",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No feasibility row owns a Whisper offline runtime intake; the linked research-control, implementation and audit rows own tooling, reference execution and asset boundary.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate a meeting-transcription pipeline with array/headset conditions, overlap and diarization against a frozen protocol",
        "evidence_gap": "S47 is an external protocol lead; no CHiME-8 corpus, layout, overlap handling, diarization output or local pipeline exists.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-FND-EVIDENCE",
            "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked audit/evidence foundations and transcript-control feasibility row own asset boundaries, scoring and typed transcripts; no meeting pipeline runs here.",
    },
    {
        "id": "G06",
        "actionable_gap": "Handle code-switched and multilingual speech without collapsing language identification, script mapping and recognition",
        "evidence_gap": "S11 is an external study lead; no code-switched audio, language boundary, script/normalization policy or execution exists, and REC-02 remains a separate category.",
        "follow_up_ids": [
            "SDK-SURVEY-REC-02",
            "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked REC-02 taxonomy and transcript-control feasibility rows own language/code-switch scope and typed transcripts; neither is a code-switch result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Obtain independent word-timestamp gold and keep forced alignment from being reported as recognition timing accuracy",
        "evidence_gap": "HE-1 compares MFA output with AMI's own forced alignment; the reference is not manually corrected and no streaming partial/final timing exists.",
        "follow_up_ids": [
            "SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING",
            "SDK-WHISPER-TINY-EN-MFA",
            "SDK-ASR-WORD-TIMESTAMPS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked timestamp and MFA rows own alignment tooling and the one-crop smoke test; the word-timestamp feasibility row owns the timing boundary, not independent gold.",
    },
    {
        "id": "G08",
        "actionable_gap": "Calibrate confidence and define abstention/unknown handling before a transcript can drive any policy",
        "evidence_gap": "No reviewed record contains confidence labels, calibration curves, abstention thresholds or an unknown/empty-transcript policy.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked evidence foundation and transcript-control feasibility row own acceptance and typed-unknown rules; no calibrated confidence result exists.",
    },
    {
        "id": "G09",
        "actionable_gap": "Keep transcripts from gating, deleting or re-ranking audio and keep word preservation distinct from listening quality",
        "evidence_gap": "Historical ASR scoring is a proxy for transcript drift only; no policy links a transcript to deletion, duration control or a listening claim.",
        "follow_up_ids": [
            "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS",
            "SDK-AIX-SPEED-ASR-GUIDED-PLANNER",
            "SDK-SURVEY-TRN-01",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked transcript-control feasibility, ASR-guided planner and TRN-01 taxonomy rows own typed text, adjacent rate policy and listening boundaries; none authorizes transcript-driven deletion.",
    },
    {
        "id": "G10",
        "actionable_gap": "Resolve weights, licence terms and exact revisions for every recognized ASR family before any comparison",
        "evidence_gap": "CrisperWhisper is non-commercial, Whisper uses OpenAI model terms, Vosk model terms are separate from code and MFA model cards need review; no permitted weight bundle is staged.",
        "follow_up_ids": [
            "SDK-CRISPERWHISPER",
            "SDK-VOSK",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked CrisperWhisper and Vosk rows own the candidates; the audit foundation owns the asset boundary. No weight is downloaded, loaded or cleared here.",
    },
    {
        "id": "G11",
        "actionable_gap": "Collect target-device availability, memory, energy, first-output and deadline evidence for offline and streaming ASR",
        "evidence_gap": "Only offline desktop CPU context exists; no phone callback path, memory ceiling, energy result or deadline-miss distribution is measured for a recognizer.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No device-timing owner for recognition exists; the linked foundation rows own timing and evidence rules.",
    },
    {
        "id": "G12",
        "actionable_gap": "Keep ASR segmentation and streaming endpointing distinct from speech activity, utterance endpointing and conversational turn completion",
        "evidence_gap": "No reviewed ASR row carries a turn label; VAD activity and ASR word boundaries are not turn truth, and DET-02 remains a separate category.",
        "follow_up_ids": [
            "SDK-SURVEY-DET-02",
            "SDK-WHISPER-STREAMING",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked DET-02 taxonomy and Whisper-Streaming feasibility rows own turn-boundary scope and streaming ASR; ASR segmentation is not promoted to a turn result.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-WHISPER-TRANSCRIPTION", "title": "Whisper transcription", "mode": "research-control"},
    {"task_id": "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX", "title": "Whisper tiny.en int8 via sherpa-onnx", "mode": "research-control"},
    {"task_id": "SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING", "title": "Whisper-timestamp and MFA tooling", "mode": "research-control"},
    {"task_id": "SDK-WHISPER-TINY-EN-MFA", "title": "Whisper tiny.en + MFA", "mode": "implementation"},
    {"task_id": "SDK-VOSK", "title": "Vosk", "mode": "feasibility"},
    {"task_id": "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE", "title": "Vosk small-en-us-0.15 playback gate", "mode": "implementation"},
    {"task_id": "SDK-CRISPERWHISPER", "title": "CrisperWhisper", "mode": "research-control"},
    {"task_id": "SDK-WHISPER-STREAMING", "title": "Whisper-Streaming", "mode": "feasibility"},
    {"task_id": "SDK-SIMULSTREAMING", "title": "SimulStreaming", "mode": "feasibility"},
    {"task_id": "SDK-STREAMING-CONFORMER-TED", "title": "Streaming Conformer-TED", "mode": "feasibility"},
    {"task_id": "SDK-FASTCONFORMER-STREAMING-ASR", "title": "FastConformer streaming ASR", "mode": "feasibility"},
    {"task_id": "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS", "title": "Speech recognition / translation controls", "mode": "feasibility"},
    {"task_id": "SDK-ASR-WORD-TIMESTAMPS", "title": "ASR word timestamps", "mode": "feasibility"},
    {"task_id": "SDK-AIX-SPEED-ASR-GUIDED-PLANNER", "title": "AIx Speed ASR-guided planner", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-SURVEY-DET-02", "title": "Review coverage for Utterance endpointing and turn completion", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-TRN-01", "title": "Review coverage for Pitch-preserving speed / time-scale modification", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-REC-02", "title": "Review coverage for Language identification and code-switch handling", "mode": "taxonomy"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified multi-domain ASR corpus with independent human transcripts, word timestamps, confidence and explicit unknown/non-speech regions"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen speaker/session/domain-disjoint development and held-out partitions with a documented text-normalization policy"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched identity/source-transcript, oracle-alignment, fixed-decoder and alternative-model controls with stratified WER/CER and uncertainty"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned real ASR runtimes, weights and exact revisions with per-weight terms for Whisper, Vosk, MFA and CrisperWhisper"},
    {"id": "RG-05", "blocked": True, "requirement": "Paced causal streaming state, partial/final commit, maximum wait, dropped/stale chunk and target-device availability evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Confidence calibration, abstention/unknown policy and independent word-preservation review on frozen cohorts"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "REC-01 \u2014 Speech recognition / transcription (ASR/STT)",
        "File transcription is not proof of causal streaming.",
        "Keep partial/final timing and word preservation distinct from listening quality.",
    ],
    "research/category_survey/sources.md": [
        "| S09 | [Whisper official implementation](https://github.com/openai/whisper) | analysis | direct |",
        "| S11 | [Code-switching speech recognition study](https://www.isca-archive.org/interspeech_2019/zeng19_interspeech.html) | analysis | direct |",
        "| S47 | [CHiME-8 meeting transcription pipeline](https://www.chimechallenge.org/challenges/chime8/task1/index) | root | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Analysis | Score timestamped probabilities, event boundaries and detections.",
        "| Evidence | Pin the scorer, corpus and cohort, aggregation, failed items and controls.",
    ],
    "research/tsm-followup-20261101/README.md": [
        "Whisper tiny.en + MFA",
        "WER 11.8% (4/34 words)",
        "boundary MAE 23.2 ms and 91.7% within 50 ms",
        "Source WER was 30.15%.",
        "paired Whisper screen provides a noisy ASR proxy",
    ],
    "research/tsm-followup-20261101/agent-text/REPORT.md": [
        "11.76% WER (4 errors / 34 reference words)",
        "Mean absolute boundary deviation 23.79 ms",
        "91.7% within 50 ms",
        "Observed pooled source WER was 30.1% (41 errors / 136 reference words).",
    ],
    "cpp-library/pipeline-validation/playback-speed/README.md": [
        "content gate      Vosk small-en-us-0.15 (streaming word boundaries)",
        "Whisper tiny.en int8 via sherpa-onnx",
        "0 deadline misses in 15 708 blocks",
        "IoU **0.94\u20130.95**",
        "12 false-speech blocks and 24 missed-speech blocks (of 345 and 467 blocks)",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "Whisper Tiny English WER 0.00%",
    ],
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": [
        "No local ASR checkpoint or streaming adapter",
        "No TED checkpoint or exact local streaming configuration.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/soundtouch/README.md": [
        "paired Whisper context; historical, not re-measured here.",
        "paired Whisper deltas) are historical",
    ],
    "docs/task-evidence/rubber-band-r3-offline/README.md": [
        "real VAD/ASR gate.",
    ],
    "docs/task-evidence/survey-det-02/README.md": [
        "ASR segmentation, disfluency editing",
        "ASR endpointing is not conversational turn completion",
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
    "historical_citations_include_real_transcripts": True,
    "real_speech_used_here": False,
    "real_corpus_used_here": False,
    "weights_loaded_here": False,
    "runtime_invoked_here": False,
    "model_inference_here": False,
    "streaming_inference_here": False,
    "human_transcript_review_here": False,
    "confidence_calibration_here": False,
    "listening_here": False,
    "device_timing_here": False,
    "latency_claim": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "asr_accuracy_claim": False,
    "code_switch_claim": False,
    "meeting_transcription_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

NON_CLAIMS: List[str] = [
    "no ASR accuracy, WER parity or model ranking is measured by this survey",
    "no human reference transcript review or independent timing gold exists",
    "no streaming, causal partial/final or endpointing execution is performed",
    "no confidence calibration, abstention or code-switch result is produced",
    "no real corpus, weights or runtime is loaded in this task",
    "no listening, device timing or latency result exists",
    "no translation, diarization, meeting-transcription or provider claim is made",
    "no provider, default, ABI, build, CI, board or release change is made",
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
    "human_reference_promoted": "rejected; state unchanged",
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
        raise MapError("REC-01 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("REC-01 taxonomy mismatch: %s" % key)
    if inventory_hit[0].get("task") != TASK:
        raise MapError("REC-01 inventory task mismatch")
    if inventory_hit[0].get("legacy_family") != LEGACY_FAMILY:
        raise MapError("REC-01 legacy family mismatch")
    if inventory_hit[0].get("legacy_backlog_state") != "catalogued":
        raise MapError("REC-01 legacy backlog state mismatch")
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
        raise MapError("legacy family F11 / REC-01 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "family_id": LEGACY_FAMILY,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "requested_optional",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F11/REC-01/%s" % key)


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
        "real_asr_corpus_benchmark",
        "human_reference_transcript_review",
        "streaming_asr_execution",
        "word_timestamp_gold",
        "confidence_calibration",
        "multi_domain_or_language_coverage",
        "code_switch_execution",
        "meeting_transcription_execution",
        "entity_error_evaluation",
        "human_listening_result",
        "device_timing",
        "latency_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "asr_accuracy_claim",
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
        "human_transcript_review_here",
        "confidence_calibration_here",
        "listening_here",
        "device_timing_here",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "asr_accuracy_claim",
        "code_switch_claim",
        "meeting_transcription_claim",
        "network_access",
    ):
        if SCOPE.get(key) is not False:
            raise MapError("scope must stay closed: " + key)
    for key in (
        "task_local_only",
        "documentation_and_metadata_only",
        "no_new_execution",
        "historical_citations_include_real_speech",
        "historical_citations_include_real_transcripts",
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
    by_id = {t["id"]: t for t in board["tasks"]}
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
            "asr_corpus_evaluation_present": False,
            "streaming_asr_execution_present": False,
            "human_transcript_review_present": False,
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
    if report["scope"]["asr_accuracy_claim"] is not False:
        raise MapError("ASR accuracy is claimed")
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
