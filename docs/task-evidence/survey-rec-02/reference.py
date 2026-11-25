# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-REC-02.

This module builds a bounded taxonomy/comparison evidence map for the language
identification and code-switch handling category (inventory category ``REC-02``,
legacy family ``F11``). It reads only pinned, read-only documents from the
enclosing ``audioml`` workspace and the SDK worktree. It does not load audio,
weights, runtimes, media or the network, and it does not register, expose,
enable, train or qualify any classifier, recognizer or processor.

All curated records below are documentation mappings, not new measurements.
Adjacent local values and source-reported candidate claims are transcribed
verbatim from the pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-REC-02"
TITLE = "Review coverage for Language identification and code-switch handling"
CATEGORY_ID = "REC-02"
LEGACY_FAMILY = "F11"
BRANCH = "swarm/SDK-SURVEY-REC-02"
BASE_COMMIT = "871201c187c42291410245344aacee5c80051b48"
PROFILE = "Recognition"
COMPONENT = "language-identification-and-code-switch-evidence-map"
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
# verifies media/weights that are not present in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary and merged-evidence pins. They are read
# only to prove that no public surface was touched and to ground curated
# boundaries; no header, contract or report is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/quality-impairment-taxonomy/README.md": "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
    "docs/task-evidence/survey-det-01/README.md": "88430878409af7a5cdb74dbc4422724b78f4c0610463fed9d5d4f29d16fffacb",
    "docs/task-evidence/survey-det-02/README.md": "40c05936132ed4add0d1a97a9139f42c170711130c447f18d36b11c7669221b1",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Recognition and language",
    "name": "Language identification and code-switch handling",
    "scope": "support",
    "output_kind": "annotation/control",
    "purpose": "Identify spoken languages and handle switches in recognition.",
    "method_families": {
        "classic": "Acoustic/phonotactic statistical classification",
        "ml": "Neural language encoders; joint multilingual recognition",
    },
    "input_output": "Audio \u2192 language scores/segments, optionally mixed-language transcript",
    "live_or_comparison_boundary": (
        "One language label per clip is different from detecting switches within an utterance."
    ),
    "source_ids": ["S10", "S11"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "REC",
    "meaning": "Recognition and language",
    "category_id": CATEGORY_ID,
    "language_labels_scores_and_optional_segments_only": True,
    "per_clip_label_and_switch_detection_are_distinct": True,
    "unknown_language_is_not_a_known_language": True,
    "not_asr_transcription": "REC-01",
    "not_speaker_change_detection": "SPK-03",
    "not_accent_conversion": "TRN-03",
    "not_voice_or_language_conversion": "TRN-04",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S10",
        "title": "Spoken language identification study",
        "url": "https://www.isca-archive.org/interspeech_2023/shahin23_interspeech.pdf",
        "access_scope": "direct",
        "mapped_components": [
            "wav2vec2-xls-r-transformer-vad",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G01", "G02"],
        "finding": (
            "Direct study lead for spoken language identification. It names an "
            "acoustic or phonotactic classification problem, not a staged "
            "system: the reviewed records contain no language labels, language "
            "inventory, feature extractor, GMM/SVM/i-vector head, neural LID "
            "head, checkpoint or local LID score. XLS-R and x-vector rows are "
            "adjacent encoder or speaker-embedding candidates used elsewhere."
        ),
    },
    {
        "source_id": "S11",
        "title": "Code-switching speech recognition study",
        "url": "https://www.isca-archive.org/interspeech_2019/zeng19_interspeech.html",
        "access_scope": "direct",
        "mapped_components": [
            "whisper-transcription",
            "fastconformer-streaming-asr",
        ],
        "gap_ids": ["G03", "G04", "G05"],
        "finding": (
            "Direct study lead for code-switching recognition. It motivates "
            "switch-aware decoding and mixed-language transcripts, but no "
            "code-switch corpus, language-segment annotation, switch boundary, "
            "bilingual language model, joint multilingual recognizer or local "
            "mixed-language transcript exists in the reviewed records. Whisper "
            "and FastConformer rows are ASR candidates, not code-switch results."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Acoustic/phonotactic statistical classification",
        "components": [],
        "gap_ids": ["G01"],
        "status": "no_local_component_or_execution_in_reviewed_records",
        "boundary": (
            "The catalogued classic branch has no inventory component, "
            "language-balanced feature extractor, phonotactic model, GMM/SVM "
            "or i-vector LID head, execution or result. Energy, pitch and "
            "spectral statistics are not by themselves a language classifier."
        ),
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural language encoders with a language-identification head",
        "components": [
            "wav2vec2-xls-r-transformer-vad",
            "x-vector-speaker-embeddings",
        ],
        "gap_ids": ["G02"],
        "status": "adjacent_encoder_candidates_no_lid_head_or_execution",
        "boundary": (
            "XLS-R is catalogued as a multilingual VAD candidate and x-vector "
            "as a speaker-embedding candidate. Neither row has a language head, "
            "language inventory, language labels, checkpoint review or LID "
            "score in this task, and speaker identity is not language identity."
        ),
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Joint multilingual recognition and code-switch handling with mixed-language transcripts (named source lead S11)",
        "components": [
            "whisper-transcription",
            "whisper-tiny-en-int8-via-sherpa-onnx",
            "speech-recognition-translation-controls",
        ],
        "gap_ids": ["G03", "G05"],
        "status": "candidate_only_no_multilingual_or_code_switch_execution",
        "boundary": (
            "Whisper transcription and the sherpa-onnx row are partial ASR "
            "controls, and the only locally scored Whisper checkpoint is "
            "`tiny.en`, which is English-only. No multilingual checkpoint, "
            "language token, mixed-language transcript or switch-aware decode "
            "exists here."
        ),
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Streaming or on-device multilingual recognition",
        "components": ["whisper-streaming", "fastconformer-streaming-asr"],
        "gap_ids": ["G04", "G05"],
        "status": "blocked_no_checkpoint_or_streaming_runtime",
        "boundary": (
            "Both streaming ASR rows are blocked: the pinned candidate matrix "
            "records no local ASR checkpoint, streaming runtime or adapter and "
            "no local WER/latency result. A source-reported streaming latency "
            "is not a language decision or switch-boundary measurement."
        ),
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Adjacent monolingual English ASR and encoder controls",
        "components": [
            "whisper-tiny-en-mfa",
            "whisper-timestamp-and-mfa-tooling",
            "dynamic-int8-wav2vec2-base",
            "distil-wav2vec2-bookbot-distil-wav2vec2-adult-child-cls-37m-ridge",
            "wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge",
        ],
        "gap_ids": ["G05", "G07"],
        "status": "adjacent_english_only_controls_not_language_identification",
        "boundary": (
            "Whisper tiny.en and the wav2vec2 rows are English-only ASR, "
            "word-timing or speech-rate controls. They cannot identify a "
            "language, score an out-of-set language or detect an intra-utterance "
            "switch, and their WER or rate error is not a LID accuracy result."
        ),
    },
    {
        "family_id": "MF-M5",
        "branch": "ml",
        "family": "Adjacent multilingual corpus and label intake",
        "components": ["librispeech-and-common-voice-evidence-intake"],
        "gap_ids": ["G06"],
        "status": "corpus_intake_considered_no_language_labels_or_audio_staged",
        "boundary": (
            "The LibriSpeech/Common Voice row is a considered evidence-intake "
            "entry only. Common Voice is multilingual in general, but no "
            "language-balanced split, language label, code-switch segment, "
            "consent record or audio asset is staged in this task."
        ),
    },
    {
        "family_id": "MF-M6",
        "branch": "ml",
        "family": "Adjacent restricted verbatim-annotation tooling",
        "components": ["crisperwhisper"],
        "gap_ids": ["G07"],
        "status": "rights_restricted_annotation_only",
        "boundary": (
            "CrisperWhisper emits verbatim English filler and word-boundary "
            "tags under non-commercial weights (CC BY-NC 4.0). It is an offline "
            "annotation lead at most, not a multilingual LID model, a "
            "code-switch detector, a runtime dependency or a rights basis."
        ),
    },
]

# component_id, task and evidence_status are checked against plan/INVENTORY.json.
# Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "whisper-transcription", "evidence_status": "partial", "task": "SDK-WHISPER-TRANSCRIPTION"},
    {"component_id": "whisper-tiny-en-int8-via-sherpa-onnx", "evidence_status": "partial", "task": "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX"},
    {"component_id": "whisper-timestamp-and-mfa-tooling", "evidence_status": "partial", "task": "SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING"},
    {"component_id": "whisper-tiny-en-mfa", "evidence_status": "evaluated", "task": "SDK-WHISPER-TINY-EN-MFA"},
    {"component_id": "fastconformer-streaming-asr", "evidence_status": "blocked", "task": "SDK-FASTCONFORMER-STREAMING-ASR"},
    {"component_id": "whisper-streaming", "evidence_status": "blocked", "task": "SDK-WHISPER-STREAMING"},
    {"component_id": "speech-recognition-translation-controls", "evidence_status": "considered", "task": "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS"},
    {"component_id": "asr-word-timestamps", "evidence_status": "considered", "task": "SDK-ASR-WORD-TIMESTAMPS"},
    {"component_id": "wav2vec2-xls-r-transformer-vad", "evidence_status": "considered", "task": "SDK-WAV2VEC2-XLS-R-TRANSFORMER-VAD"},
    {"component_id": "x-vector-speaker-embeddings", "evidence_status": "considered", "task": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"},
    {"component_id": "librispeech-and-common-voice-evidence-intake", "evidence_status": "considered", "task": "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE"},
    {"component_id": "crisperwhisper", "evidence_status": "considered", "task": "SDK-CRISPERWHISPER"},
    {"component_id": "dynamic-int8-wav2vec2-base", "evidence_status": "evaluated", "task": "SDK-DYNAMIC-INT8-WAV2VEC2-BASE"},
    {"component_id": "distil-wav2vec2-bookbot-distil-wav2vec2-adult-child-cls-37m-ridge", "evidence_status": "evaluated", "task": "SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE"},
    {"component_id": "wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge", "evidence_status": "evaluated", "task": "SDK-WAV2VEC-2-0-BASE-FACEBOOK-WAV2VEC2-BASE-960H-RIDGE"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Spoken language identification study (named source lead S10)",
        "class": "source_reported_lid_study",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Study-language documentation only; no language inventory, labels, model, checkpoint, audio or score is staged or verified.",
    },
    {
        "id": "CI-2",
        "input": "Code-switching speech recognition study (named source lead S11)",
        "class": "source_reported_code_switch_study",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Study-language documentation only; no code-switch corpus, segment annotation, switch boundary or mixed-language transcript exists.",
    },
    {
        "id": "CI-3",
        "input": "XLS-R and x-vector rows as adjacent multilingual-encoder and speaker-embedding candidates",
        "class": "source_reported_neural_language_encoder_candidate",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Both rows are considered only; neither has a language head, language labels, checkpoint or local score, and a speaker embedding is not a language label.",
    },
    {
        "id": "CI-4",
        "input": "Whisper transcription, Whisper tiny.en int8 via sherpa-onnx and ASR/translation control rows",
        "class": "source_reported_multilingual_asr_candidate",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "ASR candidate metadata only; the locally scored Whisper checkpoint is `tiny.en` (English-only), and no multilingual token, language inference or mixed-language transcript is present.",
    },
    {
        "id": "CI-5",
        "input": "Blocked Whisper-Streaming/SimulStreaming and FastConformer streaming ASR rows",
        "class": "blocked_streaming_asr_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Pinned candidate matrix records no local checkpoint, streaming runtime or adapter and no local WER/latency; absence is not a negative accuracy result.",
    },
    {
        "id": "CI-6",
        "input": "LibriSpeech and Common Voice evidence-intake row",
        "class": "source_reported_language_corpus_intake",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Intake record only; no language-balanced split, consent record, label manifest or audio is staged. Common Voice multilingual breadth is not local evidence.",
    },
    {
        "id": "CI-7",
        "input": "Adjacent Whisper tiny.en + MFA word-timing crop on one 15 s English AMI utterance",
        "class": "adjacent_english_asr_historical_local",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "One English-only crop; WER and boundary error measure transcription/timing, not language identity, out-of-set rejection or switch detection.",
    },
    {
        "id": "CI-8",
        "input": "Adjacent English-only wav2vec2 and Distil-Wav2Vec2 speech-rate probes on 210 windows from one AMI meeting",
        "class": "adjacent_english_encoder_historical_local",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "Speech-rate regression on one English meeting; encoder features are repurposed for rate, not trained or scored for language identification.",
    },
    {
        "id": "CI-9",
        "input": "Missing REC-02 language-identification cohort, language inventory, code-switch segmentation, LID/scorer and matched benchmark",
        "class": "missing_rec02_cohort",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Absence is recorded as missing, not as a negative result; no language, switch, transcript or accuracy claim follows.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "always-majority-language diagnostic",
        "role": "Required degenerate control for any future LID score; it exposes class imbalance and is not a language classifier.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-2",
        "name": "per-clip label versus intra-utterance switch separation",
        "role": "One label per clip and a switch boundary answer different questions; neither may be scored or described as the other.",
        "source_pin": "audio_categories.md",
    },
    {
        "id": "CT-3",
        "name": "unknown or out-of-set language",
        "role": "An unlisted language stays unknown; it is never silently mapped to the nearest known language or to a no-speech label.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-4",
        "name": "monolingual English ASR control (Whisper tiny.en)",
        "role": "Adjacent English-only ASR/timing baseline; it is not multilingual, cannot identify a language and is not a code-switch control.",
        "source_pin": "research/tsm-followup-20261101/README.md",
    },
    {
        "id": "CT-5",
        "name": "identity / no-annotation stream",
        "role": "Emitting no language label preserves audio and transcript; any language decision must justify itself against this baseline.",
        "source_pin": "docs/task-evidence/survey-det-01/README.md",
    },
    {
        "id": "CT-6",
        "name": "per-language confusion and macro-average",
        "role": "A pooled accuracy or WER hides a small-language or code-switch stratum; per-language FN/FP and macro-average are required and not run.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-7",
        "name": "switch-boundary collar and decision delay",
        "role": "Any future switch metric must fix the annotation collar, decision lag and hysteresis; no switch annotation or scorer exists.",
        "source_pin": "docs/task-evidence/survey-det-02/README.md",
    },
    {
        "id": "CT-8",
        "name": "nonfinite and adverse input",
        "role": "NaN/Inf scores, duplicate JSON keys and missing pins are rejected with state unchanged and cannot count as a pass.",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Spoken language identification study document (S10)",
        "class": "external_documentation",
        "status": "Primary-source page recorded in the survey ledger; document not downloaded, extracted or verified in this task",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Code-switching speech recognition study document (S11)",
        "class": "external_documentation",
        "status": "Primary-source page recorded in the survey ledger; no data, labels, code or checkpoint follows from the citation",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "LibriSpeech and Common Voice multilingual corpus intake",
        "class": "external_data_considered",
        "status": "Intake record only; no split, consent record, language label, code-switch segment or audio staged",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
    {
        "asset": "`openai/whisper-tiny.en` cached English-only checkpoint",
        "class": "local_research_model_english_only",
        "status": "Cached for local WER scoring in another task; English-only, not multilingual, not staged here and not a LID or code-switch model",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "XLS-R and x-vector candidate encoders",
        "class": "external_code_and_weights_considered",
        "status": "Considered inventory rows only; no weights, language head, exact revision, terms review or runtime staged",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
    {
        "asset": "CrisperWhisper verbatim English annotation tooling",
        "class": "rights_restricted_tooling",
        "status": "Code MIT, weights CC BY-NC 4.0 per the pinned note; offline English annotation lead only, not a rights basis or runtime",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
    },
    {
        "asset": "Rights-qualified multilingual and code-switch corpus with language and segment labels",
        "class": "missing",
        "status": "Not present; absence is explicit and is not an empty negative set",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Whisper tiny.en + MFA word-timing crop on one 15 s English AMI utterance",
        "outcome_class": "adjacent_english_asr_historical_local",
        "component_ids": ["whisper-tiny-en-mfa", "whisper-timestamp-and-mfa-tooling"],
        "source_pin": "research/tsm-followup-20261101/README.md",
        "values": {
            "crop_seconds": 15,
            "whisper_cpu_inference_seconds": 1.45,
            "rtf_excluding_load": 0.096,
            "wer_percent": 11.8,
            "wer_word_errors": 4,
            "wer_words": 34,
            "mfa_oracle_words_matched": 33,
            "mfa_oov_words": 1,
            "mfa_mean_boundary_error_ms": 23.8,
            "asr_transcript_words_matched": 30,
            "asr_boundary_mae_ms": 23.2,
            "asr_within_50_ms_percent": 91.7,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent English-only ASR and forced-alignment timing on one 15 s "
            "AMI crop; WER and boundary error are not language identification, "
            "out-of-set rejection or code-switch evidence; not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Paired Whisper tiny.en TSM ASR proxy screen on ten English AMI clips",
        "outcome_class": "adjacent_english_tsm_asr_proxy",
        "component_ids": ["whisper-transcription"],
        "source_pin": "research/tsm-followup-20261101/README.md",
        "values": {
            "clips": 10,
            "reference_words": 136,
            "source_wer_percent": 30.15,
            "bungee_delta_1_25_pp": 0.0,
            "bungee_delta_2_5_pp": 42.7,
            "soundtouch_delta_2_5_pp": 54.4,
            "rubber_band_delta_2_5_pp": 36.0,
            "psola_delta_2_5_pp": 37.5,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent English-only ASR proxy for time-scale engines on ten AMI "
            "clips; no language label, switch boundary, multilingual stratum or "
            "human intelligibility result; not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "English-only wav2vec2 and Distil-Wav2Vec2 speech-rate probes",
        "outcome_class": "adjacent_english_encoder_historical_local",
        "component_ids": [
            "wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge",
            "dynamic-int8-wav2vec2-base",
            "distil-wav2vec2-bookbot-distil-wav2vec2-adult-child-cls-37m-ridge",
        ],
        "source_pin": "research/tsm-followup-20261101/README.md",
        "values": {
            "windows": 210,
            "meetings": 1,
            "wav2vec2_base_rate_mae_syll_s": 0.593,
            "dynamic_int8_rate_mae_syll_s": 0.687,
            "distil_rate_mae_syll_s": 0.741,
        },
        "adjacent": True,
        "not_component_evidence": True,
        "scope": (
            "Adjacent English-only speech-rate regression from frozen encoder "
            "features on 210 windows from one AMI meeting; the heads predict "
            "rate, not language, and no language label or LID score exists; "
            "not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Spoken language identification is a studied acoustic and phonotactic classification problem",
        "class": "source_reported_lid_study",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Study citation only; it supplies no inventory language set, labels, model, checkpoint or local accuracy.",
    },
    {
        "id": "RO-2",
        "claim": "Code-switching recognition is a studied mixed-language recognition problem",
        "class": "source_reported_code_switch_study",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Study citation only; it supplies no corpus, switch annotation, decoder or local mixed-language transcript.",
    },
    {
        "id": "RO-3",
        "claim": "Whisper supports multilingual transcription in its general model family",
        "class": "source_reported_multilingual_asr_candidate",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "The only checkpoint cached and locally scored here is `tiny.en`, which is English-only; the general family claim is not a local multilingual result.",
    },
    {
        "id": "RO-4",
        "claim": "Whisper-Streaming reports low-latency streaming in its paper conditions but its README points to a successor",
        "class": "source_reported_streaming_asr_claim",
        "source_pin": "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
        "boundary": "Source-reported latency under paper conditions; no local checkpoint, adapter, language decision or switch latency exists.",
    },
    {
        "id": "RO-5",
        "claim": "Common Voice provides multilingual crowd-sourced speech at intake scope",
        "class": "source_reported_language_corpus_intake",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Intake framing only; no language-balanced split, consent, label manifest, audio or rights clearance is staged.",
    },
    {
        "id": "RO-6",
        "claim": "X-vector embeddings represent speaker identity, which is adjacent to but distinct from language identity",
        "class": "source_reported_adjacent_speaker_embedding",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Adjacent speaker-representation row only; no language head, labels or local LID score follows.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "profile_row_present": False,
    "profile_note": (
        "VERIFICATION.md defines Analysis, Enhancement, Room, DSP, Restoration, "
        "Spatial, Rate, Voice, Evidence, Tool, External and Pipeline profiles but "
        "no Recognition/language profile; REC-02 therefore has no agreed "
        "acceptance row to satisfy."
    ),
    "mapped": {
        "language_labels_and_scores": "No REC-02 language label, score, segment, inventory or execution exists in the reviewed records",
        "per_clip_lid_versus_switch_detection": "CT-2 keeps one-label-per-clip scoring separate from intra-utterance switch detection; no switch annotation exists",
        "language_set_and_out_of_set": "CT-3 keeps an unlisted language unknown; the language inventory and out-of-set policy are unpinned",
        "code_switch_boundaries_and_collar": "CT-7 fixes the requirement; no switch boundary, collar or decision delay is annotated or scored",
        "multilingual_transcript": "No multilingual model, language token, bilingual decode or mixed-language transcript is staged",
        "validity_versus_unlabelled": "Unlabelled language or segment time is unknown, never a known-language or no-speech negative",
        "per_language_fn_fp": "No per-language confusion, macro-average or code-switch stratum exists",
        "independent_state": "Streaming state, chunk, lookahead and hysteresis are unpinned for every blocked ASR row",
        "availability_and_latency": "Only offline ASR and word-timing values exist; no language-decision or switch latency is measured",
        "listening": "No bilingual listener, mixed-language transcript review or listening result exists",
        "timing": "No target-device language-decision, switch-detection or recognition deadline measurement is mapped",
    },
    "blocked": [
        "Rights-qualified multilingual and code-switch cohort with language labels, segment labels, unknown handling and consent",
        "Frozen language inventory, out-of-set policy, switch-boundary annotation and collar, per-language partitions",
        "Matched always-majority, monolingual English, identity and unknown/out-of-set controls with per-language FN/FP and uncertainty",
        "Pinned multilingual model or encoder runtimes, weights, exact revisions, language lists and per-weight terms",
        "Independent blinded bilingual listening and mixed-language transcript/content analysis",
        "Paced streaming language-decision and switch-detection latency, state, memory and target-device deadline evidence",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "source_reported_lid_study": True,
    "source_reported_code_switch_study": True,
    "source_reported_neural_language_encoder_candidate": True,
    "source_reported_multilingual_asr_candidate": True,
    "blocked_streaming_asr_candidate": True,
    "source_reported_language_corpus_intake": True,
    "adjacent_english_asr_historical_local": True,
    "adjacent_english_encoder_historical_local": True,
    "adjacent_english_tsm_asr_proxy": True,
    "rec02_language_identification_execution": False,
    "rec02_code_switch_execution": False,
    "multilingual_language_labels": False,
    "code_switch_corpus": False,
    "lid_accuracy_result": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "public_benchmark_claim": False,
}

# True evidence classes must be backed by at least one row class; false classes
# must not be backed. This keeps a missing result from being promoted.
CLASS_BACKING: Dict[str, List[str]] = {
    "source_reported_lid_study": ["source_reported_lid_study"],
    "source_reported_code_switch_study": ["source_reported_code_switch_study"],
    "source_reported_neural_language_encoder_candidate": [
        "source_reported_neural_language_encoder_candidate"
    ],
    "source_reported_multilingual_asr_candidate": [
        "source_reported_multilingual_asr_candidate",
        "source_reported_streaming_asr_claim",
    ],
    "blocked_streaming_asr_candidate": ["blocked_streaming_asr_candidate"],
    "source_reported_language_corpus_intake": [
        "source_reported_language_corpus_intake",
        "source_reported_adjacent_speaker_embedding",
    ],
    "adjacent_english_asr_historical_local": ["adjacent_english_asr_historical_local"],
    "adjacent_english_encoder_historical_local": ["adjacent_english_encoder_historical_local"],
    "adjacent_english_tsm_asr_proxy": ["adjacent_english_tsm_asr_proxy"],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Create or select a classic acoustic/phonotactic LID classifier and evaluate it on a frozen multilingual cohort",
        "evidence_gap": "The catalogued classic branch has no inventory component, feature extractor, phonotactic model, GMM/SVM or i-vector head, execution or result; candidate census and benchmark stay not_started.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated REC-02 classic LID component or feasibility task exists; the linked foundation and evidence-manifest rows own evidence and cohort rules, not a language classifier.",
    },
    {
        "id": "G02",
        "actionable_gap": "Attach a language head to a pinned multilingual encoder and score LID with a frozen language inventory",
        "evidence_gap": "XLS-R is a considered VAD row and x-vector is a considered speaker-embedding row; neither has a language head, language inventory, labels, checkpoint review or local LID score.",
        "follow_up_ids": [
            "SDK-WAV2VEC2-XLS-R-TRANSFORMER-VAD",
            "SDK-X-VECTOR-SPEAKER-EMBEDDINGS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are scoping leads for a multilingual encoder and speaker embeddings; neither is a language-identification model, and speaker identity is not language identity.",
    },
    {
        "id": "G03",
        "actionable_gap": "Stage and evaluate a multilingual or joint recognizer with a frozen language set and unknown-language policy",
        "evidence_gap": "Whisper transcription and the sherpa-onnx row are partial ASR controls; the only locally scored Whisper checkpoint is English-only `tiny.en`, and no multilingual checkpoint, language token or mixed-language transcript exists.",
        "follow_up_ids": [
            "SDK-WHISPER-TRANSCRIPTION",
            "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX",
            "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked rows are ASR controls and translation scoping only; none establishes a multilingual or language-identification capability.",
    },
    {
        "id": "G04",
        "actionable_gap": "Unblock streaming or on-device multilingual recognition with an exact checkpoint, runtime and language set",
        "evidence_gap": "Whisper-Streaming/SimulStreaming and FastConformer streaming ASR are blocked: no local checkpoint, streaming runtime, adapter or local WER/latency result; the source-reported 3.3 s latency is not local.",
        "follow_up_ids": [
            "SDK-WHISPER-STREAMING",
            "SDK-FASTCONFORMER-STREAMING-ASR",
        ],
        "feasibility_task_exists": True,
        "owner_note": "Both linked feasibility rows are blocked or scoping leads; no streaming multilingual runtime is staged or enabled by this map.",
    },
    {
        "id": "G05",
        "actionable_gap": "Add intra-utterance language-segment and code-switch boundary detection with exact intervals",
        "evidence_gap": "No component or execution emits language segments or switch boundaries; the category boundary distinguishes one clip label from switch detection, and no switch annotation, collar or delay distribution exists.",
        "follow_up_ids": [
            "SDK-ASR-WORD-TIMESTAMPS",
            "SDK-FND-ANALYSIS",
            "SDK-SURVEY-SPK-03",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated REC-02 code-switch component or feasibility task exists; the linked word-timestamp, typed-event and speaker-segmentation rows own adjacent timing or segmentation plumbing, not language-boundary detection.",
    },
    {
        "id": "G06",
        "actionable_gap": "Freeze a rights-qualified, language-balanced and code-switch corpus with consent and unknown handling",
        "evidence_gap": "The only corpus lead is a considered LibriSpeech/Common Voice intake row; no multilingual split, language labels, code-switch segments, consent record or audio asset is staged, and AMI is one English corpus.",
        "follow_up_ids": [
            "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated REC-02 corpus owner exists; the linked research-control and foundation rows own intake, manifests and evidence rules, not a rights-qualified multilingual cohort.",
    },
    {
        "id": "G07",
        "actionable_gap": "Define per-language, out-of-set and switch metrics with degenerate controls and uncertainty",
        "evidence_gap": "No LID accuracy, per-language confusion, macro-average, out-of-set rejection, switch-boundary or transcript metric exists; the only adjacent metrics are English WER and word-boundary error.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated REC-02 scorer exists; the linked foundation and research-control rows own evidence rules and preservation scoring, not a LID or switch metric.",
    },
    {
        "id": "G08",
        "actionable_gap": "Run independent blinded bilingual listening and mixed-language transcript review",
        "evidence_gap": "No human rating exists and no bilingual panel is staged; adjacent Whisper tiny.en WER is an English ASR proxy, not a language-identification or mixed-language naturalness result.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner collected REC-02 ratings; the linked research-control rows own listening design and preservation scoring, not a bilingual listening result.",
    },
    {
        "id": "G09",
        "actionable_gap": "Measure language-decision and switch-detection latency, state, memory and target-device deadlines",
        "evidence_gap": "Only offline ASR and word-timing values exist; no paced streaming language decision, switch delay, hysteresis, memory or callback deadline was measured.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated REC-02 timing row exists; the linked foundation rows own lifecycle, timing and evidence-acceptance rules, not a language-decision latency measurement.",
    },
    {
        "id": "G10",
        "actionable_gap": "Define an opt-in provider intake and public exposure path for a language-identification or multilingual recognizer",
        "evidence_gap": "No provider descriptor, installed-archive comparison, default selection or independent review exists for any REC-02 candidate.",
        "follow_up_ids": [
            "SDK-FND-PROVIDER",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake for REC-02; the linked foundation rows own provider boundaries and exact-head evidence, not a language-identification provider.",
    },
    {
        "id": "G11",
        "actionable_gap": "Keep language identification separate from ASR transcription, speaker-change detection, accent conversion and voice conversion",
        "evidence_gap": "REC-01 produces transcripts, SPK-03 segments speaker changes and TRN-03/TRN-04 convert accent or voice; none of those labels is a language label, an out-of-set decision or an intra-utterance language boundary.",
        "follow_up_ids": [
            "SDK-SURVEY-REC-01",
            "SDK-SURVEY-SPK-03",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No single component owns both language identification and transcription or conversion; the linked taxonomy and foundation rows keep those decisions separate.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-WHISPER-TRANSCRIPTION", "title": "Whisper transcription", "mode": "research-control"},
    {"task_id": "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX", "title": "Whisper tiny.en int8 via sherpa-onnx", "mode": "research-control"},
    {"task_id": "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS", "title": "Speech recognition / translation controls", "mode": "feasibility"},
    {"task_id": "SDK-WHISPER-STREAMING", "title": "Whisper-Streaming", "mode": "feasibility"},
    {"task_id": "SDK-FASTCONFORMER-STREAMING-ASR", "title": "FastConformer streaming ASR", "mode": "feasibility"},
    {"task_id": "SDK-WAV2VEC2-XLS-R-TRANSFORMER-VAD", "title": "Wav2Vec2 XLS-R transformer VAD", "mode": "feasibility"},
    {"task_id": "SDK-X-VECTOR-SPEAKER-EMBEDDINGS", "title": "X-vector speaker embeddings", "mode": "feasibility"},
    {"task_id": "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE", "title": "LibriSpeech and Common Voice evidence intake", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-ASR-WORD-TIMESTAMPS", "title": "ASR word timestamps", "mode": "feasibility"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-FND-ANALYSIS", "title": "Typed analysis events and composition taps", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
    {"task_id": "SDK-SURVEY-REC-01", "title": "Review coverage for Speech recognition / transcription (ASR/STT)", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-03", "title": "Review coverage for Speaker change detection and segmentation", "mode": "taxonomy"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified multilingual and code-switch cohort with language labels, segment labels, unknown handling and consent"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen language inventory, out-of-set policy, switch-boundary annotation and collar, and per-language partitions"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched always-majority, monolingual English, identity and unknown/out-of-set controls with per-language FN/FP and uncertainty"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned multilingual model or encoder runtimes, weights, exact revisions, language lists and per-weight terms"},
    {"id": "RG-05", "blocked": True, "requirement": "Independent blinded bilingual listening and mixed-language transcript/content analysis"},
    {"id": "RG-06", "blocked": True, "requirement": "Paced streaming language-decision and switch-detection latency, state, memory and target-device deadline evidence"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Explicit public default selection approval and release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **REC-02 \u2014 Language identification and code-switch handling** |",
        "One language label per clip is different from detecting switches within an utterance.",
    ],
    "research/category_survey/sources.md": [
        "| S10 | [Spoken language identification study](https://www.isca-archive.org/interspeech_2023/shahin23_interspeech.pdf) | analysis | direct |",
        "| S11 | [Code-switching speech recognition study](https://www.isca-archive.org/interspeech_2019/zeng19_interspeech.html) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "Use the profile named on the component's [structured inventory record](../INVENTORY.json).",
        "| Voice | Freeze permitted input and target references, task and language/speaker groups.",
    ],
    "cpp-library/pipeline-validation/playback-speed-candidates.md": [
        "an ASR WER proxy (Whisper tiny.en or a held-out ASR)",
        "| Verbatim/filler timestamps | **CrisperWhisper** | Code MIT, **weights CC-BY-NC-4.0** |",
        "**CrisperWhisper** is the best *verbatim* transcript found",
    ],
    "research/tsm-followup-20261101/README.md": [
        "**Evaluated on one crop.** Whisper CPU inference 1.45 s (RTF .096 excluding load), WER 11.8% (4/34 words).",
        "Paired Whisper tiny.en screens covered ten clips and 136 AMI reference words. Source WER was 30.15%.",
        "It is one meeting and is not representative of accents, languages, noise, or device conditions.",
    ],
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": [
        "| Whisper-Streaming / SimulStreaming | No local ASR checkpoint or streaming adapter;",
        "No model was substituted.",
        "| Streaming Conformer-TED / FastConformer | No TED checkpoint or exact local streaming configuration.",
    ],
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": [
        "generalization limited by three meetings, one language/corpus, and forced-alignment word boundaries.",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "Whisper Tiny English is cached at `models/whisper-tiny-en` for local evaluation",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Disfluency and TSM,Whisper-Streaming / SimulStreaming,unavailable/blocked,",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/survey-det-01/README.md": [
        "Keep speech-activity detection separate from muting, endpointing, turn",
    ],
    "docs/task-evidence/survey-det-02/README.md": [
        "endpointing is useful for optional",
        "recognition or voice-agent workflows",
    ],
    "docs/task-evidence/quality-impairment-taxonomy/README.md": [
        "At threshold 0.35 the reported clip occupancy was 2.74%",
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
    "language_identification_claim": False,
    "code_switch_handling_claim": False,
    "asr_transcription_claim": False,
    "accent_conversion_claim": False,
}

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "language_claim_without_labels": "rejected; state unchanged",
    "single_clip_label_as_switch_detection": "rejected; state unchanged",
    "unlisted_language_silently_mapped": "rejected; state unchanged",
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


def _check_profile_absence(workspace: Path) -> None:
    text = (workspace / "audio-benchmark-platform/plan/swarm/VERIFICATION.md").read_text(encoding="utf-8")
    if "| Recognition |" in text:
        raise MapError("a Recognition acceptance profile now exists; review the map")
    if ACCEPTANCE_PROFILE.get("profile_row_present") is not False:
        raise MapError("acceptance profile absence is not recorded")


def _check_taxonomy(workspace: Path) -> None:
    registry = strict_json_load(workspace / "research/category_registry.json")
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    registry_hit = [c for c in registry["categories"] if c.get("id") == CATEGORY_ID]
    inventory_hit = [c for c in inventory["taxonomy"] if c.get("id") == CATEGORY_ID]
    if len(registry_hit) != 1 or len(inventory_hit) != 1:
        raise MapError("REC-02 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("REC-02 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F11 / REC-02 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "support",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F11/REC-02/%s" % key)


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
        "rec02_language_identification_execution",
        "rec02_code_switch_execution",
        "multilingual_language_labels",
        "code_switch_corpus",
        "lid_accuracy_result",
        "human_listening_result",
        "device_timing",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "public_benchmark_claim",
    }
    for key in critical_false:
        if EVIDENCE_CLASSES.get(key) is not False:
            raise MapError("unsupported evidence class is not false: " + key)
    if any(not isinstance(value, bool) for value in EVIDENCE_CLASSES.values()):
        raise MapError("evidence class value must be boolean")


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
    _check_profile_absence(ws)
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
    if any(row.get("adjacent") is not True for row in report["historical_executions"]):
        raise MapError("a historical execution is not labelled adjacent")
    for key in ("language_identification_claim", "code_switch_handling_claim", "asr_transcription_claim", "accent_conversion_claim"):
        if report["scope"][key] is not False:
            raise MapError("unsupported scope claim: " + key)
    if report["category_scope"]["per_clip_label_and_switch_detection_are_distinct"] is not True:
        raise MapError("per-clip and switch detection are conflated")
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
