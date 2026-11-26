# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-WHISPER-TINY-EN-MFA.

This module is standard-library only and deterministic. It contains no Whisper
weight, MFA acoustic model, dictionary, PyTorch/Whisper/MFA runtime, audio
signal, transcript, word span, inference path or model result. It records the
exact Whisper tiny.en and Montreal Forced Aligner (MFA 3.4.3) artifacts that the
historical pilot used, probes a fixed list of recorded workspace and temporary
paths to evidence that the weights, runtime and run artifacts are absent,
validates a caller-supplied Whisper+MFA alignment manifest with a fail-closed
admission boundary, and builds the canonical report.

The historical pilot ran OpenAI Whisper tiny.en
(`openai-whisper==20250625`, weight SHA-256 d3dd57d3...) on one 15 s AMI crop
and aligned the oracle and ASR transcripts with MFA 3.4.3. Its recorded WER and
boundary errors are provenance only. This package does not reproduce, confirm
or extend them, and no result here qualifies the candidate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-WHISPER-TINY-EN-MFA"
COMPONENT_ID = "whisper-tiny-en-mfa"
TASK_TITLE = "Whisper tiny.en + MFA"
CONTRACT_ID = "audio-sdk/whisper-tiny-en-mfa-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/whisper-tiny-en-mfa-alignment-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "c58c907576576d06fc5d0f3aa046ca4cb29e8ea0"
BRANCH = "swarm/SDK-WHISPER-TINY-EN-MFA"
WRITE_SCOPE = "docs/task-evidence/whisper-tiny-en-mfa/ only"
TASK_PREFIX = "docs/task-evidence/whisper-tiny-en-mfa/"
DISPOSITION = (
    "Whisper tiny.en plus MFA 3.4.3 text-aware transcription/alignment "
    "readiness blocker; no implementation, adapter, asset, runtime or result.")

WHISPER_PACKAGE = "openai-whisper"
WHISPER_PACKAGE_VERSION = "20250625"
WHISPER_MODEL = "openai/whisper tiny.en"
WHISPER_WEIGHT_NAME = "tiny.en.pt"
WHISPER_WEIGHT_SHA256 = (
    "d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03")
WHISPER_LICENSE = "MIT"

MFA_VERSION = "3.4.3"
MFA_DISTRIBUTION = "conda-forge"
MFA_ACOUSTIC_MODEL = "english_us_arpa"
MFA_DICTIONARY = "english_us_arpa"
MFA_ACOUSTIC_SHA256 = (
    "d35ce271ded357d833d2f4b8d1041dc3748b9538567ba13f2c697f4e4126711b")
MFA_DICTIONARY_SHA256 = (
    "e8c6c7b036ae2b7c78d2768b8dc6b1f9359175b842956d00b48c53c9c332e6b0")
MFA_LICENSE_RECORDED = "CC-BY-4.0"
MFA_DICTIONARY_ENTRIES = 266823

AMI_LICENSE = "CC BY 4.0"
AMI_AUDIO_SHA256 = (
    "a8fcab8547e24376367f97ce5967318e18cc6e052fe3f89934ff037dc90bd9ca")
AMI_CROP_SECONDS = "15.0"
AMI_CROP_SAMPLES = 240000
SAMPLE_RATE_HZ = 16000

COHORT_ITEM_COUNT = 1
MAX_TIMING_MS = 60000.0

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-text/REPORT.md":
        "86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93",
    "research/tsm-followup-20261101/agent-text/run_mfa_alignment_smoke.py":
        "245f05c557cb7b93ba14887b71fa93ef8098d94478fee4cd9baa1910dac7fa66",
    "research/tsm-followup-20261101/agent-text/run_whisper_asr.py":
        "7fb7a94b6117b7694ec04d3bb1f6491527c802651135fcf5f05eae8b0782bbd4",
    "research/tsm-followup-20261101/agent-text/score_asr_alignment.py":
        "0294e7681af9b6491bed6501bd1d7154b6809a9231101209187412c6f5b9c6bf",
    "research/tsm-followup-20261101/agent-text/score_mfa_alignment_smoke.py":
        "f6b99e3fb0864eea4dab999b875e88a7214fda1142f40e7cc8118c303225bd0a",
    "research/tsm-followup-20261101/agent-text/score_whisper_asr.py":
        "624558e2835dfb25f2321c6ba3b505107536539164159e461a7c250bee6a27a8",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/README.md":
        "1ccece1085e1d6e821891feffb0c19fc494227bfd5e8a656657ffd7081cf959c",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/contract.json":
        "ee23e6cc21f9f3293a48dab7008a4c41f129074cafa3eb6b273f2f3ef413d694",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/README.md":
        "870a665c5da0f75dea01de767388cd40fdd45a0cd5d55f07fa1010861e9dd371",
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/contract.json":
        "f4429f3afde1096d29068f51ddace56c591a290d793097a671a125f4ff7a9a68",
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/report.json":
        "1ce7faa0b87faa8a8782083bd23ba6dd5803f9bd45ae5ef2db9a8692b0858f48",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-ELASTIC", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

# Fixed probes only; no recursive workspace walk. These are the exact paths
# recorded by the historical run's report and scripts.
WORKSPACE_ABSENCE_PROBES = (
    "data/runs/tsm-followup-20261101-mfa",
    "data/runs/tsm-followup-20261101-mfa/manifest.json",
    "data/runs/tsm-followup-20261101-mfa/EN2003a_A_16s_31s.wav",
    "data/runs/tsm-followup-20261101-mfa/EN2003a_A_16s_31s.lab",
    "data/runs/tsm-followup-20261101-mfa/score.json",
    "data/runs/tsm-followup-20261101-mfa/aligned/EN2003a_A_16s_31s.TextGrid",
    "data/runs/tsm-followup-20261101-mfa/aligned_asr/EN2003a_A_16s_31s.TextGrid",
    "data/runs/tsm-followup-20261101-mfa/asr/whisper_tiny_en.lab",
    "data/runs/tsm-followup-20261101-mfa/asr/whisper_tiny_en.json",
    "data/runs/tsm-followup-20261101-mfa/asr/whisper_tiny_en_run.json",
    "data/runs/tsm-followup-20261101-mfa/asr/whisper_tiny_en_wer.json",
    "data/runs/tsm-followup-20261101-mfa/asr/whisper_mfa_alignment_score.json",
    "data/tmp/ami/vad-verified-ami-archive/words/EN2003a.A.words.xml",
)
EXTERNAL_ABSENCE_PROBES = (
    "/private/tmp/whisper-model/tiny.en.pt",
    "/private/tmp/asr-mfa-env",
    "/private/tmp/mfa-env",
    "/private/tmp/mfa-root",
    "/private/tmp/EN2003a.Headset-0.wav",
    "/private/tmp/ffmpeg-bin",
)

# Required artifact IDs. ART-01 is the only present/verified artifact: the
# research report, crop/alignment scripts and scoring scripts. It is provenance
# only and never a weight, runtime, reproduction or qualification.
REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "research_report_and_scripts",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The exact historical Whisper/MFA report, crop, ASR, alignment and "
            "scoring scripts pinned by SHA-256."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "whisper_weight_and_source",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact OpenAI Whisper tiny.en weight (tiny.en.pt, SHA-256 "
            "d3dd57d3...) plus the exact openai-whisper source revision, "
            "package archive and complete MIT license/notice bundle."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "mfa_acoustic_dictionary_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact MFA 3.4.3 English US ARPA acoustic archive and "
            "dictionary with byte counts and verified SHA-256, the MFA source "
            "revision, license/notice text and a pinned offline runtime."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Locked offline environments for openai-whisper 20250625 (torch, "
            "ffmpeg) and MFA 3.4.3 (conda/whisperx) with wheel/package hashes, "
            "install/import digests, deterministic threads and no network."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_ami_crop_and_annotations",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact 15 s AMI EN2003a channel-0 crop, A.words annotation, "
            "meeting/channel mapping and reviewable AMI CC BY 4.0 terms."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "reproduced_whisper_mfa_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A fresh offline Whisper tiny.en ASR run and MFA oracle/ASR "
            "alignments on the qualified crop with frozen scoring, finite "
            "outputs, matched-word accounting and control baselines."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "provider_intake",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A separate versioned opt-in SDK provider/tool intake with OFF "
            "default, empty descriptor settings, no registry/default/build "
            "change and independent exact-head review after every other gate "
            "clears."),
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "statement": (
            "The exact Whisper tiny.en weight is absent. The research record "
            "pins openai-whisper==20250625, tiny.en.pt and SHA-256 d3dd57d3..., "
            "but /private/tmp/whisper-model/tiny.en.pt is absent and no weight "
            "exists at a reviewed workspace or cache path. The upstream source "
            "revision, package archive digest and complete MIT notice bundle "
            "are not staged. No weight was downloaded or reconstructed."),
        "required_action": (
            "Supply tiny.en.pt with byte count and SHA-256 d3dd57d3..., the "
            "exact openai-whisper 20250625 source revision/package archive and "
            "the complete MIT license/notice bundle with an independent terms "
            "review."),
        "linked_gates": ["RG-01", "RG-02"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No verified MFA asset or runtime is staged. The research report "
            "records MFA 3.4.3 with english_us_arpa acoustic and dictionary "
            "archive SHA-256 values and a CC-BY-4.0 model card, but those "
            "installed paths are outside this worktree and are not readable by "
            "this session; no digest was verified here, no MFA source "
            "revision/notice bundle is staged, and /private/tmp/mfa-env is "
            "absent."),
        "required_action": (
            "Supply the exact MFA 3.4.3 acoustic archive and dictionary with "
            "byte counts and SHA-256, the MFA source revision and license/"
            "notice text, a written CC-BY-4.0 attribution/output-use decision, "
            "and a pinned offline Conda environment."),
        "linked_gates": ["RG-01", "RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No pinned runtime is present. The historical ASR environment "
            "/private/tmp/asr-mfa-env, the MFA environment /private/tmp/mfa-env "
            "and /private/tmp/mfa-root are absent; the available Python 3.11.5 "
            "interpreter exposes no whisper, torch, transformers or soundfile "
            "module. No lockfile, wheel/conda digest, import digest, thread "
            "policy or offline-load proof exists. No import, load or inference "
            "was attempted."),
        "required_action": (
            "Supply locked offline environments for openai-whisper 20250625 and "
            "MFA 3.4.3 with exact package/wheel/conda hashes, install and "
            "import digests, deterministic thread settings and a clean-room "
            "offline load trace."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "statement": (
            "The exact crop and annotation are absent. /private/tmp/"
            "EN2003a.Headset-0.wav, data/tmp/ami/.../EN2003a.A.words.xml and "
            "the entire data/runs/tsm-followup-20261101-mfa tree are absent, so "
            "the recorded crop SHA-256 a8fcab85... and the reference word spans "
            "cannot be verified. AMI terms are not reviewed and the AMI "
            "timings are themselves forced alignment, not independent timing "
            "gold."),
        "required_action": (
            "Freeze the exact AMI EN2003a channel-0 crop, A.words annotation, "
            "meeting/channel mapping, source and annotation digests, reviewable "
            "AMI CC BY 4.0 terms, and an independent human-checked timing "
            "reference rather than reusing AMI forced alignment as gold."),
        "linked_gates": ["RG-04", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No ASR or alignment result was reproduced. The recorded 11.76% "
            "WER (4/34), 1.445 s CPU inference, 23.79 ms oracle boundary MAE, "
            "23.17 ms ASR boundary MAE and 91.7% within-50 ms figures are "
            "quoted context only. No local WER, boundary score, matched-word "
            "accounting, finite-output scan or control baseline exists."),
        "required_action": (
            "Run Whisper tiny.en and MFA 3.4.3 offline on the qualified crop "
            "with frozen ASR and boundary scorers, explicit token/substitution/"
            "deletion accounting, finite-output checks, a uniform-timing "
            "baseline and adverse/missing controls."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider, tool, adapter or intake exists. The candidate has no "
            "SDK registration, no public ABI/registry/default/build or CI "
            "change, no target-device timing or resource measurement, and no "
            "reviewed rate-to-speed policy. The task row's Rate profile is a "
            "mismatch for a transcript/alignment tool, and every Rate row "
            "remains blocked."),
        "required_action": (
            "After model/data/runtime/quality gates clear, measure the exact "
            "target-device paced workload, complete or explicitly waive the "
            "Rate profile with an independent review, and open a separate "
            "OFF-by-default versioned intake with exact-head review."),
        "linked_gates": ["RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "status": "blocked",
        "statement": (
            "Only the research report and scripts are pinned. The exact "
            "openai-whisper source revision/package archive and the MFA 3.4.3 "
            "source revision with complete MIT/CC-BY-4.0 license and notice "
            "sets are not staged or reviewed."),
        "reopen_condition": (
            "Pin the exact source/package revisions and trees for Whisper and "
            "MFA, stage the complete license/notice/model-card set, and record "
            "an independent terms review."),
    },
    {
        "id": "RG-02",
        "title": "weights_assets_and_digests",
        "status": "blocked",
        "statement": (
            "tiny.en.pt is absent; the MFA acoustic archive and dictionary are "
            "not staged or digest-verified in this package. Only documented "
            "SHA-256 values are recorded."),
        "reopen_condition": (
            "Supply tiny.en.pt, the MFA acoustic archive and dictionary with "
            "byte counts and SHA-256, and verify every digest against an "
            "immutable source record."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "statement": (
            "No openai-whisper or MFA runtime is present. There is no lockfile, "
            "wheel/conda digest, import digest, deterministic thread policy or "
            "offline-load trace."),
        "reopen_condition": (
            "Provide locked offline Whisper and MFA environments with exact "
            "package hashes, install/import digests, deterministic settings and "
            "a clean-room offline load."),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_audio_annotations_and_terms",
        "status": "blocked",
        "statement": (
            "The AMI crop and annotation are absent and AMI/MFA terms are not "
            "reviewed. AMI timings are forced alignment, not independent timing "
            "gold."),
        "reopen_condition": (
            "Stage the exact crop, annotation and meeting/channel mapping, "
            "review AMI and MFA terms, and provide an independent human-checked "
            "timing reference."),
    },
    {
        "id": "RG-05",
        "title": "asr_and_alignment_accuracy_with_controls",
        "status": "blocked",
        "statement": (
            "No WER, boundary MAE/median/within-50 ms, matched-word accounting, "
            "finite-output scan or uniform-timing baseline was reproduced."),
        "reopen_condition": (
            "Reproduce Whisper ASR and MFA alignment on the qualified crop with "
            "frozen scorers, exact token accounting, finite-output checks and "
            "matched control baselines."),
    },
    {
        "id": "RG-06",
        "title": "rate_profile_condition_coverage",
        "status": "blocked",
        "statement": (
            "The Rate profile is not exercised: no source/output mapping, "
            "duration, pitch/transient, buffering, rate-change, unfamiliar "
            "speech/music/silence, rebuffer/drift, final-partial-window or "
            "timestamp-tied pause/filler preservation evidence exists."),
        "reopen_condition": (
            "Score the exact Rate-profile cases with separate source references "
            "and a timestamp-tied pause/filler policy, or record a reviewed "
            "waiver because this tool is not a renderer."),
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_resources_and_deadlines",
        "status": "blocked",
        "statement": (
            "No target-device timing, CPU/memory/energy, queue, deadline or "
            "rebuffer measurement exists. The historical 1.445 s CPU inference "
            "is context only and not a device result."),
        "reopen_condition": (
            "Measure the exact installed candidate under paced workload with "
            "p50/p95/p99 latency, resource, thermal/energy and fill/flush "
            "behavior on the intended device."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "statement": (
            "No provider/tool intake or public-surface decision exists. The "
            "installed v0 geometry and shared build remain untouched."),
        "reopen_condition": (
            "Open a separate versioned, OFF-by-default opt-in intake with an "
            "exact descriptor/config, clean-install proof and independent "
            "exact-head review after all prior gates clear."),
    },
)

RATE_PROFILE_ROWS = (
    {
        "id": "RATE-01",
        "requirement": "Measure source/output mapping and duration.",
        "status": "blocked",
        "evidence": (
            "Whisper+MFA emits transcript and word boundaries, not rendered "
            "audio; no mapping or duration result exists."),
    },
    {
        "id": "RATE-02",
        "requirement": "Measure pitch and transient audibility.",
        "status": "blocked",
        "evidence": "No rendered waveform, F0/transient metric or listening result exists.",
    },
    {
        "id": "RATE-03",
        "requirement": "Measure playback buffering.",
        "status": "blocked",
        "evidence": "No playback chain, queue, fill/flush or buffering measurement exists.",
    },
    {
        "id": "RATE-04",
        "requirement": "Include 1x and rate changes.",
        "status": "blocked",
        "evidence": "No 1x or rate-change comparison exists; the tool is not a stretcher.",
    },
    {
        "id": "RATE-05",
        "requirement": "Include unfamiliar speech, music and silence.",
        "status": "blocked",
        "evidence": (
            "The historical evidence is one 15 s English AMI speech crop; no "
            "unfamiliar speech, music, silence or language coverage was tested."),
    },
    {
        "id": "RATE-06",
        "requirement": "Include rebuffer, drift and the final partial window.",
        "status": "blocked",
        "evidence": "No stream, rebuffer, clock-drift or partial-window behavior was measured.",
    },
    {
        "id": "RATE-07",
        "requirement": (
            "Keep pause or filler decisions tied to source timestamps and "
            "measure speech preservation."),
        "status": "blocked",
        "evidence": (
            "Word boundaries could inform a pause/filler controller, but no "
            "controller, source-timestamp policy or preservation measurement "
            "exists."),
    },
    {
        "id": "RATE-08",
        "requirement": "Map output to a reviewed preferred-speed policy.",
        "status": "blocked",
        "evidence": (
            "No preference/acceptability labels or rate-to-speed policy exists; "
            "WER and boundary error are not a preferred speed factor."),
    },
)

QUALITY_ROWS = (
    {
        "id": "QUAL-01",
        "outcome": "whisper_asr_word_error_rate",
        "status": "blocked",
        "value": None,
        "evidence": "Recorded 11.76% WER is provenance only; no local score was reproduced.",
    },
    {
        "id": "QUAL-02",
        "outcome": "oracle_transcript_boundary_error",
        "status": "blocked",
        "value": None,
        "evidence": "Recorded 23.79 ms MAE is provenance only; no local alignment was reproduced.",
    },
    {
        "id": "QUAL-03",
        "outcome": "asr_transcript_boundary_error_and_within_50ms",
        "status": "blocked",
        "value": None,
        "evidence": "Recorded 23.17 ms MAE and 91.7% within 50 ms are provenance only.",
    },
    {
        "id": "QUAL-04",
        "outcome": "matched_word_and_token_accounting",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No local substitution/deletion/insertion accounting, OOV audit or "
            "finite-boundary scan exists."),
    },
    {
        "id": "QUAL-05",
        "outcome": "uniform_timing_and_no_alignment_baselines",
        "status": "blocked",
        "value": None,
        "evidence": "Only a synthetic scorer-arithmetic control exists; no real baseline comparison exists.",
    },
)

TIMING_ROWS = (
    {
        "id": "TIME-01",
        "metric": "whisper_load_and_inference_latency",
        "status": "blocked",
        "value": None,
        "evidence": "No local model load, inference p50/p95 or RTF was measured.",
    },
    {
        "id": "TIME-02",
        "metric": "mfa_alignment_wall_time",
        "status": "blocked",
        "value": None,
        "evidence": "No local MFA alignment or scoring wall time was measured.",
    },
    {
        "id": "TIME-03",
        "metric": "device_deadline_and_callback",
        "status": "blocked",
        "value": None,
        "evidence": "No device, pacing, callback deadline or availability measurement exists.",
    },
    {
        "id": "TIME-04",
        "metric": "cpu_memory_energy",
        "status": "blocked",
        "value": None,
        "evidence": "No resource, thermal or energy measurement exists.",
    },
)

NON_CLAIMS = (
    "No Whisper weight, MFA acoustic model or MFA dictionary is present in this package.",
    "No torch, openai-whisper, transformers, soundfile or MFA runtime is imported or executed.",
    "No audio, transcript, word span, TextGrid or alignment artifact is read or scored.",
    "No WER, boundary error, finite-output, baseline or timing result is reproduced.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "Recorded WER and boundary error are not independent timing gold or a preferred speed factor.",
)

REQUIRED_RESULTS = (
    "Exact openai-whisper 20250625 source/package revision and MIT notice bundle.",
    "tiny.en.pt with byte count and SHA-256 d3dd57d3...",
    "Exact MFA 3.4.3 acoustic archive and dictionary with verified SHA-256.",
    "Reviewed MFA CC-BY-4.0 and AMI CC BY 4.0 attribution/output-use decisions.",
    "Locked offline Whisper and MFA environments with import digests.",
    "The exact AMI 15 s crop, A.words annotation and meeting/channel mapping.",
    "Reproduced WER, oracle and ASR boundary errors with matched-word accounting.",
    "Uniform-timing/no-alignment controls and finite/adverse/missing-input rejection.",
    "Rate-profile evidence or a reviewed waiver plus target-device timing.",
    "Separate OFF-by-default provider intake and independent exact-head review.",
)

# Admission is a strict, task-local schema check only. It never reads audio,
# loads weights or invokes Whisper/MFA.
MANIFEST_FIELDS = (
    "schema_id", "cohort_id", "whisper", "mfa", "runtime", "audio",
    "transcripts", "controls", "outcomes", "rights")
WHISPER_FIELDS = (
    "model", "package", "package_version", "weight_name", "weight_sha256",
    "weight_byte_count", "license_id")
MFA_FIELDS = (
    "version", "distribution", "acoustic_model", "dictionary",
    "acoustic_sha256", "dictionary_sha256", "acoustic_byte_count",
    "dictionary_byte_count", "license_id")
RUNTIME_FIELDS = (
    "python", "torch", "whisper", "mfa", "device", "intra_op_threads",
    "interop_op_threads", "deterministic_algorithms", "offline")
AUDIO_FIELDS = (
    "id", "path", "sha256", "language", "speaker_group", "meeting_id",
    "channel", "sample_rate_hz", "channels", "samples", "start_s", "end_s")
TRANSCRIPT_FIELDS = ("source", "sha256", "word_count")
CONTROL_FIELDS = ("id", "kind")
CONTROL_KINDS = (
    "oracle_transcript_mfa_alignment",
    "asr_transcript_mfa_alignment",
    "uniform_word_timing_baseline",
)
OUTCOME_FIELDS = (
    "wer", "boundary_mae_ms", "boundary_median_abs_error_ms",
    "boundary_within_50ms_fraction", "matched_words", "reference_words",
    "nonfinite_count", "sample_count")
RIGHTS_FIELDS = (
    "dataset_terms_reference", "whisper_terms_reference",
    "mfa_terms_reference", "output_use_reference", "review_reference",
    "claims_qualified")

HEX64 = re.compile(r"[0-9a-f]{64}")
SLUG = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
ABSOLUTE = re.compile(r"/[^\x00]+")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text(document: dict) -> str:
    text = json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text + "\n"


def canonical_bytes(document: dict) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: dict) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def _no_floats(value: Any, path: str = "document") -> None:
    if isinstance(value, float):
        raise ValueError("float:" + path)
    if isinstance(value, dict):
        for key, item in value.items():
            _no_floats(item, path + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, path + f"[{index}]")


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json:" + token)


def read_strict_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text, object_pairs_hook=_strict_pairs,
                           parse_constant=_reject_constant)
    except ValueError:
        raise
    except Exception as error:  # pragma: no cover - defensive
        raise ValueError("json_parse:" + type(error).__name__) from error
    if not isinstance(value, dict):
        raise ValueError("json_not_object")
    return value


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative, expected in sorted(pins.items()):
        actual = sha256_file(root / relative)
        if actual != expected:
            raise ValueError("pin_mismatch:" + relative)
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": True,
        }
    return rows


def board_row_projection(board_path: Path, task: str = TASK) -> dict:
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in tasks if isinstance(row, dict)
               and row.get("id") == task]
    if len(matches) != 1:
        raise ValueError("board_row_count:" + task)
    row = matches[0]
    return {field: copy.deepcopy(row.get(field)) for field in BOARD_ROW_FIELDS}


def board_row_digest(row: dict) -> str:
    return hashlib.sha256(canonical_bytes(row)).hexdigest()


def linked_rows() -> list[dict]:
    board_path = AUDIO_ROOT / BOARD_TASK_ROW
    document = read_strict_json(board_path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    index = {row.get("id"): row for row in tasks if isinstance(row, dict)}
    rows = []
    for task_id in LINKED_ROW_IDS:
        row = index.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        rows.append({field: copy.deepcopy(row.get(field))
                     for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(rows if rows is not None
                                          else linked_rows())).hexdigest()


def _present(path: Path) -> bool:
    return path.exists()


def absence_probes() -> list[dict]:
    rows = []
    for relative in WORKSPACE_ABSENCE_PROBES:
        path = AUDIO_ROOT / relative
        rows.append({
            "scope": "workspace",
            "path": relative,
            "present": _present(path),
            "kind": "whisper_mfa_run_or_ami_artifact",
        })
    return rows


def external_absence_probes() -> list[dict]:
    rows = []
    for absolute in EXTERNAL_ABSENCE_PROBES:
        path = Path(absolute)
        rows.append({
            "scope": "external",
            "path": absolute,
            "present": _present(path),
            "kind": "whisper_weight_or_mfa_runtime_or_ami_audio",
        })
    return rows


def absence_summary(rows: list[dict], external_rows: list[dict]) -> dict:
    all_rows = rows + external_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(rows),
        "external_probe_count": len(external_rows),
        "present_count": sum(1 for row in all_rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


def source_presence() -> dict:
    roles = {
        "research/tsm-followup-20261101/README.md":
            "candidate_scorecard",
        "research/tsm-followup-20261101/agent-text/REPORT.md":
            "detailed_whisper_mfa_report",
        "research/tsm-followup-20261101/agent-text/run_mfa_alignment_smoke.py":
            "crop_and_manifest_recipe",
        "research/tsm-followup-20261101/agent-text/run_whisper_asr.py":
            "whisper_cpu_asr_recipe",
        "research/tsm-followup-20261101/agent-text/score_asr_alignment.py":
            "asr_boundary_scoring_recipe",
        "research/tsm-followup-20261101/agent-text/score_mfa_alignment_smoke.py":
            "oracle_boundary_scoring_recipe",
        "research/tsm-followup-20261101/agent-text/score_whisper_asr.py":
            "wer_scoring_recipe",
    }
    rows = []
    for relative, role in roles.items():
        path = AUDIO_ROOT / relative
        rows.append({
            "path": relative,
            "sha256": SOURCE_PINS[relative],
            "byte_count": path.stat().st_size,
            "role": role,
        })
    external = external_absence_probes()
    whisper_weight_present = Path(
        "/private/tmp/whisper-model/tiny.en.pt").exists()
    mfa_runtime_present = Path("/private/tmp/mfa-env").exists()
    asr_runtime_present = Path("/private/tmp/asr-mfa-env").exists()
    run_tree_present = (AUDIO_ROOT /
                        "data/runs/tsm-followup-20261101-mfa").exists()
    return {
        "research_report_and_scripts_present": True,
        "whisper_weight_present": whisper_weight_present,
        "mfa_acoustic_and_dictionary_staged_and_verified": False,
        "mfa_runtime_present": mfa_runtime_present,
        "whisper_runtime_present": asr_runtime_present,
        "run_artifacts_present": run_tree_present,
        "exact_source_weights_runtime_conjunction_present": (
            whisper_weight_present and mfa_runtime_present
            and asr_runtime_present),
        "weights_used": False,
        "runtime_imported": False,
        "mfa_assets_loaded": False,
        "audio_read": False,
        "model_executed": False,
        "provenance_rows": rows,
    }


def _require_substring(text: str, needle: str, code: str) -> None:
    if needle not in text:
        raise ValueError(code)


def recipe_provenance() -> dict:
    """Verify the pinned scripts contain the exact recorded recipe."""
    report_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/REPORT.md")
    asr_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/run_whisper_asr.py")
    mfa_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/run_mfa_alignment_smoke.py")
    score_asr_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/score_asr_alignment.py")
    score_mfa_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/score_mfa_alignment_smoke.py")
    score_wer_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/score_whisper_asr.py")
    report = report_path.read_text(encoding="utf-8")
    asr = asr_path.read_text(encoding="utf-8")
    mfa = mfa_path.read_text(encoding="utf-8")
    score_asr = score_asr_path.read_text(encoding="utf-8")
    score_mfa = score_mfa_path.read_text(encoding="utf-8")
    score_wer = score_wer_path.read_text(encoding="utf-8")
    checks = (
        (report, "`openai-whisper==20250625`", "report_package_version"),
        (report, WHISPER_WEIGHT_SHA256, "report_whisper_weight_sha"),
        (report, "MFA 3.4.3", "report_mfa_version"),
        (report, MFA_ACOUSTIC_SHA256, "report_mfa_acoustic_sha"),
        (report, MFA_DICTIONARY_SHA256, "report_mfa_dictionary_sha"),
        (report, AMI_AUDIO_SHA256, "report_ami_audio_sha"),
        (asr, 'whisper.load_model("tiny.en", device="cpu"',
         "asr_tiny_en_cpu"),
        (asr, 'language="en", fp16=False', "asr_language_fp16"),
        (mfa, "START_S = 16.0", "mfa_crop_start"),
        (mfa, "END_S = 31.0", "mfa_crop_end"),
        (mfa, 'sf.read(SOURCE, dtype="float32")', "mfa_read"),
        (score_asr, "boundary_mae_ms_on_matched_words",
         "score_asr_boundary"),
        (score_mfa, "boundary_mae_ms", "score_mfa_boundary"),
        (score_wer, "word_error_rate", "score_wer"),
    )
    for text, needle, code in checks:
        _require_substring(text, needle, code)
    return {
        "report_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-text/REPORT.md"],
        "asr_script_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-text/run_whisper_asr.py"],
        "mfa_script_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-text/"
            "run_mfa_alignment_smoke.py"],
        "score_scripts": 3,
        "checks_present": len(checks),
        "checks_required": len(checks),
        "whisper_model": WHISPER_MODEL,
        "whisper_package_version": WHISPER_PACKAGE_VERSION,
        "whisper_weight_sha256": WHISPER_WEIGHT_SHA256,
        "mfa_version": MFA_VERSION,
        "mfa_distribution": MFA_DISTRIBUTION,
        "crop_start_s": "16.0",
        "crop_end_s": "31.0",
        "crop_seconds": AMI_CROP_SECONDS,
        "recorded_only": True,
        "saved_run_artifacts": False,
        "executed_here": False,
    }


def documented_metrics() -> dict:
    """Quote the pinned report; verify every value is present, never rerun it."""
    report_path = AUDIO_ROOT / (
        "research/tsm-followup-20261101/agent-text/REPORT.md")
    report = report_path.read_text(encoding="utf-8")
    checks = (
        "1.445 s (RTF .096 excluding 0.839 s model load)",
        "11.76% WER (4 errors / 34 reference words)",
        "Mean absolute boundary deviation 23.79 ms, median 10 ms, 89.4% "
        "boundaries within 50 ms",
        "Whisper text: 30 words matched; boundary MAE 23.17 ms, median 10 ms, "
        "91.7% within 50 ms",
        "33/34 words matched (one `Mm` OOV)",
        "Crop starts at 16 s and lasts 15 s",
    )
    for needle in checks:
        _require_substring(report, needle, "documented_metric_missing")
    return {
        "source_path": (
            "research/tsm-followup-20261101/agent-text/REPORT.md"),
        "source_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-text/REPORT.md"],
        "whisper_package": WHISPER_PACKAGE,
        "whisper_package_version": WHISPER_PACKAGE_VERSION,
        "whisper_model": WHISPER_MODEL,
        "whisper_weight_sha256": WHISPER_WEIGHT_SHA256,
        "whisper_license": WHISPER_LICENSE,
        "whisper_load_seconds": "0.839",
        "whisper_inference_seconds": "1.445",
        "whisper_inference_rtf_excluding_load": "0.096",
        "wer": "0.1176",
        "wer_errors": "4",
        "wer_reference_words": "34",
        "mfa_version": MFA_VERSION,
        "mfa_distribution": MFA_DISTRIBUTION,
        "mfa_acoustic_model": MFA_ACOUSTIC_MODEL,
        "mfa_dictionary": MFA_DICTIONARY,
        "mfa_acoustic_sha256": MFA_ACOUSTIC_SHA256,
        "mfa_dictionary_sha256": MFA_DICTIONARY_SHA256,
        "mfa_dictionary_entries": str(MFA_DICTIONARY_ENTRIES),
        "mfa_license_recorded": MFA_LICENSE_RECORDED,
        "oracle_matched_words": "33",
        "oracle_reference_words": "34",
        "oracle_boundary_mae_ms": "23.79",
        "oracle_boundary_median_abs_error_ms": "10",
        "oracle_boundary_within_50ms_fraction": "0.894",
        "asr_matched_words": "30",
        "asr_boundary_mae_ms": "23.17",
        "asr_boundary_median_abs_error_ms": "10",
        "asr_boundary_within_50ms_fraction": "0.917",
        "ami_license": AMI_LICENSE,
        "ami_audio_sha256": AMI_AUDIO_SHA256,
        "crop_start_s": "16.0",
        "crop_seconds": AMI_CROP_SECONDS,
        "timing_reference": "AMI forced-alignment timestamps, not independent gold",
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
    }


def exact_models() -> dict:
    return {
        "whisper": {
            "model": WHISPER_MODEL,
            "package": WHISPER_PACKAGE,
            "package_version": WHISPER_PACKAGE_VERSION,
            "weight_name": WHISPER_WEIGHT_NAME,
            "weight_sha256": WHISPER_WEIGHT_SHA256,
            "weight_byte_count": None,
            "license": WHISPER_LICENSE,
            "source_revision": None,
            "package_archive_present": False,
            "weight_present": False,
            "digest_verified": False,
            "license_bundle_reviewed": False,
            "downloaded_or_reconstructed": False,
        },
        "mfa": {
            "version": MFA_VERSION,
            "distribution": MFA_DISTRIBUTION,
            "acoustic_model": MFA_ACOUSTIC_MODEL,
            "dictionary": MFA_DICTIONARY,
            "acoustic_sha256_documented": MFA_ACOUSTIC_SHA256,
            "dictionary_sha256_documented": MFA_DICTIONARY_SHA256,
            "dictionary_entries_documented": MFA_DICTIONARY_ENTRIES,
            "license_recorded": MFA_LICENSE_RECORDED,
            "source_revision": None,
            "assets_staged": False,
            "digests_verified": False,
            "license_bundle_reviewed": False,
            "runtime_present": False,
        },
        "ami": {
            "audio_sha256_documented": AMI_AUDIO_SHA256,
            "crop_seconds": AMI_CROP_SECONDS,
            "crop_samples": AMI_CROP_SAMPLES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "license_recorded": AMI_LICENSE,
            "crop_present": False,
            "annotation_present": False,
            "terms_reviewed": False,
        },
    }


def historical_recipe() -> dict:
    return {
        "whisper_source": (
            "research/tsm-followup-20261101/agent-text/run_whisper_asr.py"),
        "mfa_align_command": (
            "mfa align_one --output_format json --no_tokenization "
            "--num_jobs 1 --overwrite"),
        "oracle_score_source": (
            "research/tsm-followup-20261101/agent-text/"
            "score_mfa_alignment_smoke.py"),
        "asr_score_source": (
            "research/tsm-followup-20261101/agent-text/"
            "score_asr_alignment.py"),
        "wer_score_source": (
            "research/tsm-followup-20261101/agent-text/score_whisper_asr.py"),
        "crop_start_s": "16.0",
        "crop_end_s": "31.0",
        "crop_seconds": AMI_CROP_SECONDS,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channel": "AMI EN2003a Headset-0 (speaker A)",
        "whisper_device": "cpu",
        "whisper_fp16": False,
        "torch_threads": 4,
        "mfa_jobs": 1,
        "saved_run_artifacts": False,
        "executed_here": False,
    }


# --------------------------------------------------------------------------
# Deterministic boundary-score arithmetic control (synthetic; no model/audio)
# --------------------------------------------------------------------------
def _format_fraction(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 28
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal.quantize(Decimal("0.000001")), "f")


def align_words(reference: list[dict], hypothesis: list[dict]) -> list[tuple[dict, dict]]:
    """Levenshtein-align word spans; unmatched tokens never shift matches."""
    n, m = len(reference), len(hypothesis)
    cost = [[0] * (m + 1) for _ in range(n + 1)]
    back: list[list[str | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost[i][0], back[i][0] = i, "D"
    for j in range(1, m + 1):
        cost[0][j], back[0][j] = j, "I"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            same = reference[i - 1]["word"].casefold() == \
                hypothesis[j - 1]["word"].casefold()
            substitute = cost[i - 1][j - 1] + (0 if same else 1)
            delete = cost[i - 1][j] + 1
            insert = cost[i][j - 1] + 1
            best = min(substitute, delete, insert)
            cost[i][j] = best
            back[i][j] = ("M" if substitute == best else
                          ("D" if delete == best else "I"))
    matches: list[tuple[dict, dict]] = []
    i, j = n, m
    while i or j:
        operation = back[i][j]
        if operation == "M":
            if reference[i - 1]["word"].casefold() == \
                    hypothesis[j - 1]["word"].casefold():
                matches.append((reference[i - 1], hypothesis[j - 1]))
            i -= 1
            j -= 1
        elif operation == "D":
            i -= 1
        else:
            j -= 1
    matches.reverse()
    return matches


def score_boundaries(reference: list[dict], hypothesis: list[dict]) -> dict:
    matches = align_words(reference, hypothesis)
    errors: list[int] = []
    for ref, hyp in matches:
        errors.append(abs(int(hyp["start_ms"]) - int(ref["start_ms"])))
        errors.append(abs(int(hyp["end_ms"]) - int(ref["end_ms"])))
    if errors:
        ordered = sorted(errors)
        count = len(ordered)
        middle = count // 2
        median = (Fraction(ordered[middle]) if count % 2
                  else Fraction(ordered[middle - 1] + ordered[middle], 2))
        mae = Fraction(sum(ordered), count)
        within = Fraction(sum(1 for error in ordered if error <= 50), count)
        mae_text = _format_fraction(mae)
        median_text = _format_fraction(median)
        within_text = _format_fraction(within)
    else:
        mae_text = median_text = within_text = "0.000000"
    return {
        "matched_words": len(matches),
        "boundary_error_count": len(errors),
        "boundary_mae_ms": mae_text,
        "boundary_median_abs_error_ms": median_text,
        "boundary_within_50ms_fraction": within_text,
    }


SYNTHETIC_REFERENCE = (
    {"word": "alpha", "start_ms": 0, "end_ms": 400},
    {"word": "beta", "start_ms": 400, "end_ms": 800},
    {"word": "gamma", "start_ms": 800, "end_ms": 1200},
    {"word": "delta", "start_ms": 1200, "end_ms": 1500},
)
SYNTHETIC_HYPOTHESIS = (
    {"word": "alpha", "start_ms": 10, "end_ms": 390},
    {"word": "beta", "start_ms": 410, "end_ms": 790},
    {"word": "xgamma", "start_ms": 810, "end_ms": 1190},
    {"word": "delta", "start_ms": 1215, "end_ms": 1480},
    {"word": "stray", "start_ms": 1500, "end_ms": 1600},
)


def scorer_control() -> dict:
    reference = [dict(row) for row in SYNTHETIC_REFERENCE]
    hypothesis = [dict(row) for row in SYNTHETIC_HYPOTHESIS]
    result = score_boundaries(reference, hypothesis)
    if result != {
            "matched_words": 3,
            "boundary_error_count": 6,
            "boundary_mae_ms": "12.500000",
            "boundary_median_abs_error_ms": "10.000000",
            "boundary_within_50ms_fraction": "1.000000"}:
        raise RuntimeError("scorer_control_mismatch")
    return {
        "id": "SCORE-CONTROL-01",
        "kind": "synthetic_boundary_score_arithmetic",
        "synthetic": True,
        "label": "synthetic_scorer_control_not_evidence",
        "reference_words": len(reference),
        "hypothesis_words": len(hypothesis),
        "result": result,
        "audio_read": False,
        "model_invoked": False,
        "runtime_imported": False,
        "qualifies": False,
    }


# --------------------------------------------------------------------------
# Fail-closed caller-supplied manifest admission (task-local only)
# --------------------------------------------------------------------------
def _type_name(value: Any) -> str:
    return type(value).__name__


def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("type:" + path)
    return value


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> dict:
    obj = _require_object(value, path)
    if set(obj) != set(expected):
        raise ValueError("keys:" + path)
    return obj


def _text(obj: dict, key: str, path: str, pattern: re.Pattern | None = None,
          max_length: int = 512) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise ValueError("string:" + path + "." + key)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ValueError("format:" + path + "." + key)
    return value


def _int(obj: dict, key: str, path: str, minimum: int, maximum: int) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("integer:" + path + "." + key)
    if value < minimum or value > maximum:
        raise ValueError("range:" + path + "." + key)
    return value


def _number(obj: dict, key: str, path: str, minimum: float,
            maximum: float) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("number:" + path + "." + key)
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite:" + path + "." + key)
    if number < minimum or number > maximum:
        raise ValueError("range:" + path + "." + key)
    return number


def _boolean(obj: dict, key: str, path: str,
             expected: bool | None = None) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise ValueError("boolean:" + path + "." + key)
    if expected is not None and value is not expected:
        raise ValueError("value:" + path + "." + key)
    return value


def _hex(obj: dict, key: str, path: str) -> str:
    return _text(obj, key, path, HEX64, 64)


def validate_manifest(manifest: dict) -> None:
    """Validate a caller-supplied single-crop Whisper+MFA manifest; never mutate."""
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("value:manifest.schema_id")
    _text(root, "cohort_id", "manifest", SLUG, 64)

    whisper = _exact_keys(root["whisper"], WHISPER_FIELDS, "whisper")
    if whisper["model"] != WHISPER_MODEL:
        raise ValueError("value:whisper.model")
    if whisper["package"] != WHISPER_PACKAGE:
        raise ValueError("value:whisper.package")
    if whisper["package_version"] != WHISPER_PACKAGE_VERSION:
        raise ValueError("value:whisper.package_version")
    if whisper["weight_name"] != WHISPER_WEIGHT_NAME:
        raise ValueError("value:whisper.weight_name")
    if whisper["weight_sha256"] != WHISPER_WEIGHT_SHA256:
        raise ValueError("value:whisper.weight_sha256")
    _int(whisper, "weight_byte_count", "whisper", 1, 1 << 40)
    if whisper["license_id"] != "mit":
        raise ValueError("value:whisper.license_id")

    mfa = _exact_keys(root["mfa"], MFA_FIELDS, "mfa")
    if mfa["version"] != MFA_VERSION:
        raise ValueError("value:mfa.version")
    if mfa["distribution"] != MFA_DISTRIBUTION:
        raise ValueError("value:mfa.distribution")
    if mfa["acoustic_model"] != MFA_ACOUSTIC_MODEL:
        raise ValueError("value:mfa.acoustic_model")
    if mfa["dictionary"] != MFA_DICTIONARY:
        raise ValueError("value:mfa.dictionary")
    if mfa["acoustic_sha256"] != MFA_ACOUSTIC_SHA256:
        raise ValueError("value:mfa.acoustic_sha256")
    if mfa["dictionary_sha256"] != MFA_DICTIONARY_SHA256:
        raise ValueError("value:mfa.dictionary_sha256")
    _int(mfa, "acoustic_byte_count", "mfa", 1, 1 << 40)
    _int(mfa, "dictionary_byte_count", "mfa", 1, 1 << 33)
    if mfa["license_id"] != "cc-by-4.0":
        raise ValueError("value:mfa.license_id")

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    for key in ("python", "torch", "whisper", "mfa"):
        _text(runtime, key, "runtime", None, 32)
    if runtime["device"] != "cpu":
        raise ValueError("value:runtime.device")
    _int(runtime, "intra_op_threads", "runtime", 1, 1)
    _int(runtime, "interop_op_threads", "runtime", 1, 1)
    _boolean(runtime, "deterministic_algorithms", "runtime", True)
    _boolean(runtime, "offline", "runtime", True)

    audio = root["audio"]
    if not isinstance(audio, list) or len(audio) != COHORT_ITEM_COUNT:
        raise ValueError("length:audio")
    seen_ids: set[str] = set()
    for index, record in enumerate(audio):
        path = f"audio[{index}]"
        row = _exact_keys(record, AUDIO_FIELDS, path)
        record_id = _text(row, "id", path, SLUG, 64)
        if record_id in seen_ids:
            raise ValueError("duplicate:" + path + ".id")
        seen_ids.add(record_id)
        _text(row, "path", path, ABSOLUTE, 512)
        _hex(row, "sha256", path)
        if row["language"] != "en":
            raise ValueError("value:" + path + ".language")
        _text(row, "speaker_group", path, SLUG, 64)
        if row["meeting_id"] != "EN2003a":
            raise ValueError("value:" + path + ".meeting_id")
        if row["channel"] != "Headset-0":
            raise ValueError("value:" + path + ".channel")
        if row["sample_rate_hz"] != SAMPLE_RATE_HZ:
            raise ValueError("value:" + path + ".sample_rate_hz")
        if row["channels"] != 1:
            raise ValueError("value:" + path + ".channels")
        if row["samples"] != AMI_CROP_SAMPLES:
            raise ValueError("value:" + path + ".samples")
        start = _number(row, "start_s", path, 0.0, 86400.0)
        end = _number(row, "end_s", path, 0.0, 86400.0)
        if abs((end - start) - float(AMI_CROP_SECONDS)) > 1e-9:
            raise ValueError("span:" + path)

    transcripts = _exact_keys(root["transcripts"], ("oracle", "asr"),
                              "transcripts")
    oracle = _exact_keys(transcripts["oracle"], TRANSCRIPT_FIELDS,
                         "transcripts.oracle")
    if oracle["source"] != "ami-orthographic":
        raise ValueError("value:transcripts.oracle.source")
    _hex(oracle, "sha256", "transcripts.oracle")
    _int(oracle, "word_count", "transcripts.oracle", 1, 100000)
    asr = _exact_keys(transcripts["asr"], TRANSCRIPT_FIELDS,
                      "transcripts.asr")
    if asr["source"] != "openai-whisper-tiny.en":
        raise ValueError("value:transcripts.asr.source")
    _hex(asr, "sha256", "transcripts.asr")
    _int(asr, "word_count", "transcripts.asr", 1, 100000)

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("length:controls")
    kinds: list[str] = []
    control_ids: set[str] = set()
    for index, record in enumerate(controls):
        path = f"controls[{index}]"
        row = _exact_keys(record, CONTROL_FIELDS, path)
        control_id = _text(row, "id", path, SLUG, 64)
        if control_id in control_ids:
            raise ValueError("duplicate:" + path + ".id")
        control_ids.add(control_id)
        kind = row["kind"]
        if kind not in CONTROL_KINDS:
            raise ValueError("value:" + path + ".kind")
        kinds.append(kind)
    if sorted(kinds) != sorted(CONTROL_KINDS):
        raise ValueError("set:controls.kind")

    outcomes = _exact_keys(root["outcomes"], OUTCOME_FIELDS, "outcomes")
    _number(outcomes, "wer", "outcomes", 0.0, 1.0)
    _number(outcomes, "boundary_mae_ms", "outcomes", 0.0, MAX_TIMING_MS)
    _number(outcomes, "boundary_median_abs_error_ms", "outcomes", 0.0,
            MAX_TIMING_MS)
    _number(outcomes, "boundary_within_50ms_fraction", "outcomes", 0.0, 1.0)
    _int(outcomes, "matched_words", "outcomes", 0, 100000)
    _int(outcomes, "reference_words", "outcomes", 1, 100000)
    _int(outcomes, "nonfinite_count", "outcomes", 0, 0)
    _int(outcomes, "sample_count", "outcomes", COHORT_ITEM_COUNT,
         COHORT_ITEM_COUNT)

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for key in ("dataset_terms_reference", "whisper_terms_reference",
                "mfa_terms_reference", "output_use_reference",
                "review_reference"):
        _text(rights, key, "rights", None, 1024)
    _boolean(rights, "claims_qualified", "rights", False)


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-control:" + label).encode()).hexdigest()


def control_manifest() -> dict:
    """Build the one structural control; it is not evidence of any result."""
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cohort_id": "synthetic-ami-en2003a-crop",
        "whisper": {
            "model": WHISPER_MODEL,
            "package": WHISPER_PACKAGE,
            "package_version": WHISPER_PACKAGE_VERSION,
            "weight_name": WHISPER_WEIGHT_NAME,
            "weight_sha256": WHISPER_WEIGHT_SHA256,
            "weight_byte_count": 1048576,
            "license_id": "mit",
        },
        "mfa": {
            "version": MFA_VERSION,
            "distribution": MFA_DISTRIBUTION,
            "acoustic_model": MFA_ACOUSTIC_MODEL,
            "dictionary": MFA_DICTIONARY,
            "acoustic_sha256": MFA_ACOUSTIC_SHA256,
            "dictionary_sha256": MFA_DICTIONARY_SHA256,
            "acoustic_byte_count": 1048576,
            "dictionary_byte_count": 1048576,
            "license_id": "cc-by-4.0",
        },
        "runtime": {
            "python": "3.12.0",
            "torch": "2.7.0",
            "whisper": WHISPER_PACKAGE_VERSION,
            "mfa": MFA_VERSION,
            "device": "cpu",
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
        },
        "audio": [
            {
                "id": "synthetic-ami-en2003a-crop",
                "path": "/synthetic/ami/EN2003a_A_16s_31s.wav",
                "sha256": AMI_AUDIO_SHA256,
                "language": "en",
                "speaker_group": "speaker-a",
                "meeting_id": "EN2003a",
                "channel": "Headset-0",
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "samples": AMI_CROP_SAMPLES,
                "start_s": 16.0,
                "end_s": 31.0,
            },
        ],
        "transcripts": {
            "oracle": {
                "source": "ami-orthographic",
                "sha256": _synthetic_digest("oracle-transcript"),
                "word_count": 34,
            },
            "asr": {
                "source": "openai-whisper-tiny.en",
                "sha256": _synthetic_digest("asr-transcript"),
                "word_count": 30,
            },
        },
        "controls": [
            {"id": "control-oracle", "kind": "oracle_transcript_mfa_alignment"},
            {"id": "control-asr", "kind": "asr_transcript_mfa_alignment"},
            {"id": "control-uniform", "kind": "uniform_word_timing_baseline"},
        ],
        "outcomes": {
            "wer": 0.1176,
            "boundary_mae_ms": 23.17,
            "boundary_median_abs_error_ms": 10.0,
            "boundary_within_50ms_fraction": 0.917,
            "matched_words": 30,
            "reference_words": 34,
            "nonfinite_count": 0,
            "sample_count": COHORT_ITEM_COUNT,
        },
        "rights": {
            "dataset_terms_reference": "synthetic://rights/ami-not-reviewed",
            "whisper_terms_reference": "synthetic://rights/whisper-mit",
            "mfa_terms_reference": "synthetic://rights/mfa-cc-by",
            "output_use_reference": "synthetic://rights/output-use",
            "review_reference": "synthetic://review/not-performed",
            "claims_qualified": False,
        },
    }


def admission_cases() -> list[dict]:
    """Enumerate adverse mutations; every one must be rejected."""
    base = control_manifest()

    def set_path(path: tuple[Any, ...], value: Any):
        def apply(document: dict) -> None:
            target: Any = document
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        return apply

    def del_path(path: tuple[Any, ...]):
        def apply(document: dict) -> None:
            target: Any = document
            for key in path[:-1]:
                target = target[key]
            if isinstance(target, dict):
                del target[path[-1]]
            else:
                target.pop(path[-1])
        return apply

    def duplicate_control_kind(document: dict) -> None:
        document["controls"][1]["kind"] = document["controls"][0]["kind"]

    def extra_top_level(document: dict) -> None:
        document["extra"] = True

    def missing_encoder(document: dict) -> None:
        del document["whisper"]

    def bool_as_int(document: dict) -> None:
        document["runtime"]["intra_op_threads"] = True

    def bool_as_byte_count(document: dict) -> None:
        document["whisper"]["weight_byte_count"] = True

    def short_audio(document: dict) -> None:
        document["audio"].append(copy.deepcopy(document["audio"][0]))

    def invalid_audio_id(document: dict) -> None:
        document["audio"][0]["id"] = "Not A Slug"

    def span_mismatch(document: dict) -> None:
        document["audio"][0]["end_s"] = 30.0

    def nonfinite_rate(document: dict) -> None:
        document["outcomes"]["boundary_mae_ms"] = float("nan")

    def nonfinite_wer(document: dict) -> None:
        document["outcomes"]["wer"] = float("inf")

    mutations = [
        ("ADM-01", "missing_whisper", missing_encoder),
        ("ADM-02", "extra_top_level_field", extra_top_level),
        ("ADM-03", "wrong_schema_id",
         set_path(("schema_id",), "audio-sdk/other/0.1")),
        ("ADM-04", "cohort_id_not_slug",
         set_path(("cohort_id",), "Not A Slug")),
        ("ADM-05", "wrong_whisper_model",
         set_path(("whisper", "model"), "openai/whisper base.en")),
        ("ADM-06", "wrong_whisper_package",
         set_path(("whisper", "package"), "whisper")),
        ("ADM-07", "wrong_whisper_version",
         set_path(("whisper", "package_version"), "20240930")),
        ("ADM-08", "wrong_weight_name",
         set_path(("whisper", "weight_name"), "base.en.pt")),
        ("ADM-09", "wrong_weight_sha",
         set_path(("whisper", "weight_sha256"), "0" * 64)),
        ("ADM-10", "short_weight_sha",
         set_path(("whisper", "weight_sha256"), "abc")),
        ("ADM-11", "zero_weight_bytes",
         set_path(("whisper", "weight_byte_count"), 0)),
        ("ADM-12", "bool_weight_bytes", bool_as_byte_count),
        ("ADM-13", "wrong_whisper_license",
         set_path(("whisper", "license_id"), "apache-2.0")),
        ("ADM-14", "missing_whisper_field",
         del_path(("whisper", "weight_sha256"))),
        ("ADM-15", "wrong_mfa_version", set_path(("mfa", "version"), "3.3.7")),
        ("ADM-16", "wrong_mfa_distribution",
         set_path(("mfa", "distribution"), "pypi")),
        ("ADM-17", "wrong_acoustic_model",
         set_path(("mfa", "acoustic_model"), "english_mfa")),
        ("ADM-18", "wrong_dictionary",
         set_path(("mfa", "dictionary"), "english_us_mfa")),
        ("ADM-19", "wrong_acoustic_sha",
         set_path(("mfa", "acoustic_sha256"), "0" * 64)),
        ("ADM-20", "wrong_dictionary_sha",
         set_path(("mfa", "dictionary_sha256"), "0" * 64)),
        ("ADM-21", "zero_acoustic_bytes",
         set_path(("mfa", "acoustic_byte_count"), 0)),
        ("ADM-22", "zero_dictionary_bytes",
         set_path(("mfa", "dictionary_byte_count"), 0)),
        ("ADM-23", "wrong_mfa_license",
         set_path(("mfa", "license_id"), "mit")),
        ("ADM-24", "missing_mfa_field",
         del_path(("mfa", "acoustic_sha256"))),
        ("ADM-25", "empty_runtime_python",
         set_path(("runtime", "python"), "")),
        ("ADM-26", "cuda_device", set_path(("runtime", "device"), "cuda")),
        ("ADM-27", "wrong_intra_threads",
         set_path(("runtime", "intra_op_threads"), 2)),
        ("ADM-28", "wrong_interop_threads",
         set_path(("runtime", "interop_op_threads"), 2)),
        ("ADM-29", "determinism_off",
         set_path(("runtime", "deterministic_algorithms"), False)),
        ("ADM-30", "offline_off", set_path(("runtime", "offline"), False)),
        ("ADM-31", "bool_as_int_threads", bool_as_int),
        ("ADM-32", "missing_runtime_field",
         del_path(("runtime", "torch"))),
        ("ADM-33", "short_audio", short_audio),
        ("ADM-34", "relative_audio_path",
         set_path(("audio", 0, "path"), "synthetic/ami/crop.wav")),
        ("ADM-35", "short_audio_sha",
         set_path(("audio", 0, "sha256"), "abc")),
        ("ADM-36", "wrong_language",
         set_path(("audio", 0, "language"), "fr")),
        ("ADM-37", "empty_speaker_group",
         set_path(("audio", 0, "speaker_group"), "")),
        ("ADM-38", "wrong_meeting",
         set_path(("audio", 0, "meeting_id"), "ES2004a")),
        ("ADM-39", "wrong_channel",
         set_path(("audio", 0, "channel"), "Mix-Headset")),
        ("ADM-40", "wrong_sample_rate",
         set_path(("audio", 0, "sample_rate_hz"), 8000)),
        ("ADM-41", "stereo_audio",
         set_path(("audio", 0, "channels"), 2)),
        ("ADM-42", "wrong_samples",
         set_path(("audio", 0, "samples"), 120000)),
        ("ADM-43", "span_mismatch", span_mismatch),
        ("ADM-44", "negative_start",
         set_path(("audio", 0, "start_s"), -16.0)),
        ("ADM-45", "missing_audio_field",
         del_path(("audio", 0, "samples"))),
        ("ADM-46", "wrong_oracle_source",
         set_path(("transcripts", "oracle", "source"), "manual")),
        ("ADM-47", "short_oracle_sha",
         set_path(("transcripts", "oracle", "sha256"), "abc")),
        ("ADM-48", "zero_oracle_words",
         set_path(("transcripts", "oracle", "word_count"), 0)),
        ("ADM-49", "wrong_asr_source",
         set_path(("transcripts", "asr", "source"), "vosk")),
        ("ADM-50", "zero_asr_words",
         set_path(("transcripts", "asr", "word_count"), 0)),
        ("ADM-51", "missing_transcripts",
         del_path(("transcripts",))),
        ("ADM-52", "missing_control", lambda d: d["controls"].pop()),
        ("ADM-53", "duplicate_control_kind", duplicate_control_kind),
        ("ADM-54", "unknown_control_kind",
         set_path(("controls", 0, "kind"), "identity_passthrough")),
        ("ADM-55", "extra_control",
         lambda d: d["controls"].append(
             {"id": "control-extra",
              "kind": "oracle_transcript_mfa_alignment"})),
        ("ADM-56", "wer_out_of_range", set_path(("outcomes", "wer"), 1.01)),
        ("ADM-57", "nonfinite_wer", nonfinite_wer),
        ("ADM-58", "negative_mae",
         set_path(("outcomes", "boundary_mae_ms"), -1.0)),
        ("ADM-59", "nonfinite_mae", nonfinite_rate),
        ("ADM-60", "negative_median",
         set_path(("outcomes", "boundary_median_abs_error_ms"), -1.0)),
        ("ADM-61", "fraction_out_of_range",
         set_path(("outcomes", "boundary_within_50ms_fraction"), 1.01)),
        ("ADM-62", "negative_matched_words",
         set_path(("outcomes", "matched_words"), -1)),
        ("ADM-63", "zero_reference_words",
         set_path(("outcomes", "reference_words"), 0)),
        ("ADM-64", "nonfinite_count_nonzero",
         set_path(("outcomes", "nonfinite_count"), 1)),
        ("ADM-65", "wrong_sample_count",
         set_path(("outcomes", "sample_count"), 2)),
        ("ADM-66", "missing_wer", del_path(("outcomes", "wer"))),
        ("ADM-67", "missing_dataset_terms",
         del_path(("rights", "dataset_terms_reference"))),
        ("ADM-68", "empty_output_use",
         set_path(("rights", "output_use_reference"), "")),
        ("ADM-69", "qualified_claim",
         set_path(("rights", "claims_qualified"), True)),
        ("ADM-70", "extra_rights_field",
         set_path(("rights", "extra"), "x")),
        ("ADM-71", "audio_id_not_slug", invalid_audio_id),
    ]

    cases: list[dict] = []
    for case_id, name, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        snapshot = copy.deepcopy(candidate)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            code = str(error)
        except Exception as error:  # pragma: no cover - defensive
            code = "unexpected:" + _type_name(error)
        else:
            raise RuntimeError("admission_mutation_accepted:" + case_id)
        if candidate != snapshot:
            raise RuntimeError("admission_state_mutated:" + case_id)
        cases.append({
            "id": case_id,
            "name": name,
            "status": "rejected",
            "code": code,
            "qualifies": False,
            "state_unchanged": True,
        })
    return cases


def build_admission() -> dict:
    control = copy.deepcopy(control_manifest())
    before = copy.deepcopy(control)
    validate_manifest(control)
    if control != before:
        raise RuntimeError("admission_control_mutated")
    cases = admission_cases()
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "boundary": "task_local_manifest_admission_only_not_a_runtime",
        "control": {
            "id": "ADM-ACCEPT-01",
            "accepted": True,
            "qualifies": False,
            "label": "synthetic_schema_control_not_evidence",
            "state_unchanged": True,
            "audio_records": len(control["audio"]),
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(1 for case in cases
                                  if case["status"] == "rejected"),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "mfa_assets_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


# --------------------------------------------------------------------------
# Contract and report
# --------------------------------------------------------------------------
def build_contract() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    qualification = {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": True,
        "whisper_weight_present": False,
        "mfa_assets_present": False,
        "runtime_present": False,
        "asr_result": False,
        "alignment_result": False,
        "wer_result": False,
        "boundary_result": False,
        "finite_output_result": False,
        "device_timing_result": False,
        "rate_profile_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }
    gates = [dict(gate, qualifies=False, linked_row=row)
             for gate in RELEASE_GATES]
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": qualification,
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "scope": {
            "write_scope": WRITE_SCOPE,
            "task_local_only": True,
            "provider_registered": False,
            "adapter_implemented": False,
            "public_abi_changed": False,
            "registry_or_default_changed": False,
            "shared_build_or_ci_changed": False,
            "real_assets_used": False,
            "network_used": False,
            "listening_performed": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "release_claim": False,
        },
        "boundary": {
            "linked_row_identity_only": True,
            "board_file_pinned": False,
            "mutable_board_fields_gate": False,
            "projected_fields": list(BOARD_ROW_FIELDS),
            "linked_row": row,
            "linked_row_sha256": board_row_digest(row),
            "linked_rows_sha256": linked_rows_digest(rows),
            "linked_rows": rows,
        },
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "changed": False,
        },
        "exact_models": exact_models(),
        "historical_recipe": historical_recipe(),
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "release_gates": gates,
        "rate_profile_requirements": [dict(row) for row in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "whisper_fields": list(WHISPER_FIELDS),
            "mfa_fields": list(MFA_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "audio_fields": list(AUDIO_FIELDS),
            "transcript_fields": list(TRANSCRIPT_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "outcome_fields": list(OUTCOME_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "cohort_item_count": COHORT_ITEM_COUNT,
            "crop_samples": AMI_CROP_SAMPLES,
            "crop_seconds": AMI_CROP_SECONDS,
            "exact_whisper_weight_sha256_required": WHISPER_WEIGHT_SHA256,
            "exact_mfa_acoustic_sha256_required": MFA_ACOUSTIC_SHA256,
            "exact_mfa_dictionary_sha256_required": MFA_DICTIONARY_SHA256,
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "whisper_license_recorded": WHISPER_LICENSE,
            "whisper_terms_reviewed": False,
            "mfa_license_recorded": MFA_LICENSE_RECORDED,
            "mfa_terms_reviewed": False,
            "ami_license_recorded": AMI_LICENSE,
            "ami_terms_reviewed": False,
            "output_use_defined": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
    }
    workspace_probes = absence_probes()
    external_probes = external_absence_probes()
    metrics = documented_metrics()
    presence = source_presence()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "mode": MODE,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": contract["qualification"],
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "contract_sha256": object_digest(contract),
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "exact_models": contract["exact_models"],
        "historical_recipe": contract["historical_recipe"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {
            "profile": PROFILE,
            "label": PROFILE_LABEL,
            "rows": contract["rate_profile_requirements"],
            "blocked_rows": len(contract["rate_profile_requirements"]),
        },
        "quality_outcomes": {
            "rows": contract["quality_outcomes"],
            "blocked_rows": len(contract["quality_outcomes"]),
        },
        "timing": {
            "rows": contract["timing_requirements"],
            "blocked_rows": len(contract["timing_requirements"]),
        },
        "historical_context": {
            "documented_context_not_reproduced": metrics,
            "why_not_reproduced": [
                "The tiny.en.pt weight is absent.",
                "The openai-whisper 20250625 and MFA 3.4.3 offline runtimes "
                "are absent.",
                "The MFA acoustic/dictionary assets are not staged or "
                "digest-verified here.",
                "The AMI crop, A.words annotation and run artifacts are absent "
                "and AMI/MFA terms are not reviewed.",
                "No target-device, listening or Rate-profile run exists.",
            ],
            "provenance_only": True,
            "reproduced_here": False,
            "used_for_evidence": False,
            "qualifies": False,
        },
        "recipe_provenance": recipe_provenance(),
        "source_presence": presence,
        "absence_evidence": {
            "workspace_probes": workspace_probes,
            "external_probes": external_probes,
            "summary": absence_summary(workspace_probes, external_probes),
        },
        "admission": build_admission(),
        "scorer_control": scorer_control(),
        "source_pins": pins["source"],
        "boundary_pins": pins["boundary"],
        "linked_row_identity": {
            "projection": board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW),
            "sha256": board_row_digest(
                board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)),
            "linked_rows": linked_rows(),
            "linked_rows_sha256": linked_rows_digest(),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "non_claims": contract["non_claims"],
        "required_results": contract["required_results"],
        "reproduction": {
            "regeneration": "run.py all (repeat=3, byte-identical)",
            "tests": "python3 -m unittest -v test_reference.py",
            "verifier": "python3 verify.py",
            "stdlib_only": True,
            "network_used": False,
        },
    }


def canonical_report(document: dict) -> tuple[str, str]:
    text = canonical_text(document)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    gates = contract.get("release_gates", [])
    if len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("contract_gate_reopen")
    artifacts = contract.get("required_artifacts", [])
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if sum(1 for row in artifacts if row.get("present")) != 1:
        raise ValueError("contract_artifact_presence")
    for row in artifacts[1:]:
        if row.get("present") is not False or row.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
    blockers = contract.get("exact_blockers", [])
    if len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
    for section, expected in (
            ("rate_profile_requirements", RATE_PROFILE_ROWS),
            ("quality_outcomes", QUALITY_ROWS),
            ("timing_requirements", TIMING_ROWS)):
        rows = contract.get(section, [])
        if len(rows) != len(expected):
            raise ValueError("contract_section_count:" + section)
        for row in rows:
            if row.get("status") != "blocked":
                raise ValueError("contract_section_not_blocked:" + section)
    qualification = contract.get("qualification", {})
    if qualification.get("not_qualified") is not True \
            or qualification.get("missing_result_promoted") is not False \
            or qualification.get("release_claim") is not False:
        raise ValueError("contract_qualification_flags")
    if qualification.get("all_release_gates_blocked") is not True:
        raise ValueError("contract_gate_flag")
    models = contract.get("exact_models", {})
    if models.get("whisper", {}).get("weight_present") is not False:
        raise ValueError("contract_whisper_weight")
    if models.get("mfa", {}).get("assets_staged") is not False:
        raise ValueError("contract_mfa_assets")
    if models.get("mfa", {}).get("runtime_present") is not False:
        raise ValueError("contract_mfa_runtime")
