# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-WAV2VEC-2-0-BASE-FACEBOOK-WAV2VEC2-BASE-960H-RIDGE.

This module is standard-library only and deterministic. It contains no
wav2vec2 weight, tokenizer asset, PyTorch/Transformers/scikit-learn runtime,
audio signal, transcript, syllable label, inference path or model result. It
records the exact upstream snapshot and FP32 encoder-plus-ridge recipe that the
historical pilot used, probes a fixed list of workspace/environment/home-cache
paths to evidence that the weights, runtime and head artifact are absent,
validates a caller-supplied FP32 rate-cohort manifest with a fail-closed
admission boundary, and builds the canonical report.

The historical pilot ran frozen `facebook/wav2vec2-base-960h` features (mean
pool of the last hidden state) through a per-fold StandardScaler + Ridge
(alpha=10) head at revision
`22aad52d435eb6dbaf354bdad9b0da84ce7d6156`. That result is recorded as
provenance only. This package does not reproduce, confirm or extend it, and no
result here qualifies the candidate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-WAV2VEC-2-0-BASE-FACEBOOK-WAV2VEC2-BASE-960H-RIDGE"
COMPONENT_ID = "wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge"
TASK_TITLE = "wav2vec 2.0 base (`facebook/wav2vec2-base-960h`) + ridge"
CONTRACT_ID = "audio-sdk/wav2vec2-base-960h-ridge-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/wav2vec2-base-960h-ridge-rate-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "8bd03e2d9d08d550bb4b2ac28425c71eaf8a0ba9"
BRANCH = "swarm/SDK-WAV2VEC-2-0-BASE-FACEBOOK-WAV2VEC2-BASE-960H-RIDGE"
WRITE_SCOPE = (
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/ "
    "only")
TASK_PREFIX = (
    "docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/")
DISPOSITION = (
    "Caller-supplied FP32 wav2vec2-base-960h encoder plus ridge rate-head "
    "readiness blocker; no implementation, adapter, asset or result.")

UPSTREAM_REPO = "facebook/wav2vec2-base-960h"
UPSTREAM_REVISION = "22aad52d435eb6dbaf354bdad9b0da84ce7d6156"
UPSTREAM_LICENSE = "apache-2.0"
UPSTREAM_PARAMETERS = 94371712
UPSTREAM_SERIALIZED_BYTES = 377614784
MODEL_WEIGHT_BYTES = 377607901
MODEL_WEIGHT_SHA256 = (
    "8aa76ab2243c81747a1f832954586bc566090c83a0ac167df6f31f0fa917d74a")
HEAD_KIND = "ridge"
HEAD_ALPHA = "10"
HEAD_SCALER = "standard"
HEAD_FOLDS = 5
FEATURE_POOLING = "mean_last_hidden_state"
COHORT_WINDOW_COUNT = 210
COHORT_WINDOW_SAMPLES = 64000
COHORT_WINDOW_SECONDS = "4.0"
COHORT_MEETING_ID = "EN2003a"
SAMPLE_RATE_HZ = 16000
RUNTIME_PYTHON = "3.10.13"
RUNTIME_TORCH = "2.2.2"
RUNTIME_TRANSFORMERS = "4.40.2"
CMUDICT_VERSION = "1.1.1"

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
    "research/tsm-followup-20261101/agent-neural/REPORT.md":
        "f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73",
    "research/tsm-followup-20261101/agent-neural/run/"
    "run_ssl_encoder_cv.py":
        "09b7e3cc4ff5fa01768cd925f38d972b555f9864feaf38036fafac7c6350f660",
    "research/tsm-followup-20261101/agent-neural/run/"
    "score_nonnegative_heads.py":
        "201f88580dfc3f0fe46d063d48a1fa306e1345c60c90581eac7a012c97512790",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_source.json":
        "6d56532312237861170b63bcecaa8d9071b30f80e6be1195ff9dfc1436b436d6",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_results.json":
        "11c0aef3121857f71e037acbca64a2546d1f206a9271fd95922530b85267d9d1",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_fp32_embeddings.npz":
        "8e5a4aadd0b7d88b363658e82e72c087950dd40a378e6ebcdc451c1db9ad8c92",
    "research/tsm-followup-20261101/agent-neural/run/syl_eval_manifest.json":
        "3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2",
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
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/README.md":
        "adb751885024bcaab88a373602f3d19326cee356559d62b0cc334cbc25afceca",
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json":
        "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/README.md":
        "3da6772383eb9b44ccd8eeab4272bf69e4dbd2640f045e42c4fa6ed24f275533",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/contract.json":
        "ccc997cb695fde535c5408a91cd9f0e5ecdbd6cc1687f5abf82530944c5ef509",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-ELASTIC", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

UPSTREAM_FILES = {
    "README.md": {
        "byte_count": 4431,
        "sha256": "fc52a0adfa64e446800f9944c6cf9b90da3127aba548860ea5714516ec8c18c7",
    },
    "config.json": {
        "byte_count": 1596,
        "sha256": "d3ec255c063d9f95057b553b19c20135b259875834a4fe9deb218a6be25b4cf3",
    },
    "feature_extractor_config.json": {
        "byte_count": 158,
        "sha256": "d3de0c797bf9b65f90bc65c30cb7b303ebeda341f6fc80af33628c4b26b95632",
    },
    "model.safetensors": {
        "byte_count": MODEL_WEIGHT_BYTES,
        "sha256": MODEL_WEIGHT_SHA256,
    },
    "preprocessor_config.json": {
        "byte_count": 159,
        "sha256": "b225d617c025463b9e157e06afea8b90dc7078fc70b013c533328423e0486b4a",
    },
    "special_tokens_map.json": {
        "byte_count": 85,
        "sha256": "bb7068de1150661a10b55f9e4b12a0e77af8bf91f5e45e1b58afaf1d0e17f675",
    },
    "tokenizer_config.json": {
        "byte_count": 163,
        "sha256": "dc790594f5bc351a4311c6624f40acd95850d4aaf2a5cb3c656c9b610720b608",
    },
    "vocab.json": {
        "byte_count": 291,
        "sha256": "19727f8944fe6459fc3f240ae2c198395b740f6a029bd23e06656266b83bcf64",
    },
}

# Required artifact IDs. ART-01 is the only present/verified artifact: the
# research runner, source record, results and derived FP32 embedding archive.
# It is provenance only and never a weight, runtime, head, reproduction or
# qualification.
REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "research_runner_and_source_metadata",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The exact historical neural-rate runner, nonnegative scoring "
            "script, upstream source record, results JSON, cohort manifest and "
            "derived FP32 embedding archive pinned by SHA-256."),
        "revision": UPSTREAM_REVISION,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "weights_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The immutable facebook/wav2vec2-base-960h snapshot at revision "
            "22aad52d435eb6dbaf354bdad9b0da84ce7d6156 with model.safetensors, "
            "config.json, preprocessor/feature-extractor configs and tokenizer "
            "assets, plus per-file byte counts and SHA-256."),
        "revision": UPSTREAM_REVISION,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A locked, offline runtime with Python 3.10.13, torch 2.2.2, "
            "transformers 4.40.2, scikit-learn and numpy versions, wheel "
            "hashes, one intra-op and one inter-op thread, and an "
            "install/import digest."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "ridge_head_artifact",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The fitted mean-pooled-feature ridge head (StandardScaler plus "
            "Ridge alpha=10) per fold, or a reproducible head-training record "
            "with exact fold boundaries, feature dims, seeds and a serialized "
            "artifact SHA-256."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_rate_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A rights-cleared, held-out speech-rate cohort with permitted AMI "
            "audio, checked transcript-derived syllable labels, language and "
            "speaker/meeting groups, and more than one meeting."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "fp32_reference_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A fresh FP32 run on the qualified cohort with a frozen scorer, "
            "exact folds, finite-output checks, constant-fold-mean and "
            "zero-rate baselines, and adverse/missing-input controls."),
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
            "A separate versioned opt-in SDK provider intake with OFF default, "
            "empty descriptor settings, no registry/default/build change and "
            "independent exact-head review after every other gate clears."),
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
            "The exact facebook/wav2vec2-base-960h weight snapshot is absent. "
            "The research source record pins model.safetensors at 377,607,901 "
            "bytes and SHA-256 8aa76ab2..., but no local file exists at the "
            "model checkpoint directory, data/checkouts, data/models or the "
            "Hugging Face cache. The smallest verifiable encoder reference "
            "cannot be built from metadata alone, and no weight was downloaded "
            "or reconstructed."),
        "required_action": (
            "Supply the immutable upstream snapshot at revision "
            "22aad52d435eb6dbaf354bdad9b0da84ce7d6156 with every file's byte "
            "count and SHA-256, the reviewed model card and license/notice "
            "bundle, and a redistribution/product-use decision."),
        "linked_gates": ["RG-01", "RG-02"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No pinned runtime is present. Python 3.10.13 with torch 2.2.2, "
            "transformers 4.40.2, scikit-learn and numpy is required, but the "
            "available 3.11.5 interpreter exposes no torch, transformers or "
            "scikit-learn build for this task, and the historical "
            "data/envs/sylnet-py310 environment is absent. No import, load or "
            "inference was attempted."),
        "required_action": (
            "Supply a locked offline environment with exact Python/torch/"
            "transformers/scikit-learn/numpy versions, wheel hashes, "
            "install/import digest, deterministic settings and one intra-op/"
            "one inter-op thread, then record a clean-room import and load."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No ridge-head artifact is present. The historical pilot fitted a "
            "StandardScaler plus Ridge(alpha=10) head inside each of five "
            "chronological folds and saved only predictions in the results "
            "JSON; no joblib/npz head, scaler parameters, fold index or feature "
            "inventory was serialized. The FP32 embedding NPZ is a derived "
            "feature archive, not a head."),
        "required_action": (
            "Supply a serialized per-fold head artifact with SHA-256/byte "
            "count, or a reproducible head-training record that pins fold "
            "boundaries, feature dims, scaler statistics, alpha, library "
            "versions and the resulting artifact digest."),
        "linked_gates": ["RG-02", "RG-03", "RG-05"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "statement": (
            "The historical cohort is one AMI EN2003a meeting (210 four-second "
            "windows), not a rights-cleared multi-meeting rate corpus. "
            "Reference syllables come from AMI orthographic transcripts plus "
            "CMUdict 1.1.1 first pronunciations, not human syllable-nucleus "
            "labels. AMI audio/annotation and CMUdict terms have not been "
            "reviewed here, and no audio byte was read for this package."),
        "required_action": (
            "Freeze a permitted, speaker/meeting-disjoint rate cohort with "
            "reviewed AMI/corpus and CMUdict terms, independently checked "
            "syllable labels, language/speaker groups and source-timestamp "
            "provenance."),
        "linked_gates": ["RG-04", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No FP32 accuracy, nonnegative-rate, finite-output or baseline "
            "comparison was reproduced. The pilot's recorded MAE/RMSE/r, "
            "negative prediction count and timing are quoted context only; the "
            "archived FP32 embeddings are not loaded, scored or promoted, and "
            "no adverse, missing, invalid or nonfinite control was exercised "
            "against a real encoder."),
        "required_action": (
            "Run the FP32 encoder plus fitted ridge head on the qualified "
            "cohort with a frozen scorer, exact folds, finite-output checks, "
            "constant-fold-mean and zero-rate baselines, and adverse/missing "
            "controls."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider, adapter, descriptor or intake exists. The candidate "
            "has no SDK registration, no public ABI/registry/default/build or "
            "CI change, no target-device timing or resource measurement, and no "
            "reviewed rate-to-speed policy. The recorded 184 ms p95 is a "
            "historical CPU context, not a device or product result."),
        "required_action": (
            "After model/data/runtime/quality gates clear, measure the exact "
            "target-device paced workload and complete the Rate profile, then "
            "open a separate OFF-by-default versioned provider intake with "
            "independent exact-head review."),
        "linked_gates": ["RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "The upstream model revision is recorded from the research source "
            "record, but the immutable source archive/tree, complete model "
            "card, license and notice bundle are not staged or reviewed."),
        "reopen_condition": (
            "Pin the exact source archive/tree and 40-hex revision, stage the "
            "complete model card and Apache-2.0 license/notice set, and record "
            "an independent terms review."),
        "linked_row": None,
    },
    {
        "id": "RG-02",
        "title": "weights_assets_and_head_artifact",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "No weight file or ridge-head artifact is present; only documented "
            "upstream digests and an in-memory per-fold fitting recipe exist."),
        "reopen_condition": (
            "Supply the immutable weight snapshot with per-file digests and a "
            "reproducible/pinned ridge head, then verify both against the "
            "recorded source record."),
        "linked_row": None,
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "The exact Python/torch/transformers/scikit-learn/numpy runtime is "
            "absent and no offline load, head fit or inference was executed."),
        "reopen_condition": (
            "Provide a locked offline runtime and install/import digest, load "
            "the pinned snapshot with networking disabled, fit or load the "
            "ridge head, and record deterministic repeat outputs."),
        "linked_row": None,
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_rate_corpus_and_labels",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "No rights-cleared multi-meeting rate cohort or human-checked "
            "syllable labels are staged; the historical pilot is one meeting "
            "with transcript-derived labels."),
        "reopen_condition": (
            "Freeze a permitted, speaker/meeting-disjoint cohort with reviewed "
            "corpus and dictionary terms, independent syllable labels and "
            "source-timestamp provenance."),
        "linked_row": None,
    },
    {
        "id": "RG-05",
        "title": "fp32_accuracy_finite_output_and_baselines",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "No FP32 reproduction, finite-output scan, nonnegative-rate check "
            "or constant/zero baseline comparison is available; recorded "
            "numbers are not local results."),
        "reopen_condition": (
            "Reproduce the FP32 path on the qualified cohort with fixed folds "
            "and a frozen scorer, including accuracy/bias/correlation, "
            "finite-output and constant-fold-mean/zero-rate baselines."),
        "linked_row": None,
    },
    {
        "id": "RG-06",
        "title": "rate_profile_condition_coverage",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "The Rate profile is not exercised: no source/output mapping, "
            "duration, pitch/transient, buffering, rate-change, unfamiliar "
            "speech/music/silence, rebuffer/drift, final-partial-window or "
            "pause/filler decision evidence exists."),
        "reopen_condition": (
            "Score the exact Rate-profile cases with separate source "
            "references and a timestamp-tied pause/filler policy, preserving "
            "speech and reporting duration/alignment."),
        "linked_row": None,
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_resources_and_deadlines",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "No target-device timing, CPU/memory/energy, queue, deadline or "
            "rebuffer measurement exists. The historical FP32 CPU p95 is "
            "context only and not a device result."),
        "reopen_condition": (
            "Measure the exact installed candidate under paced workload with "
            "p95/p99 callback/deadline, resource, thermal/energy and "
            "fill/flush behavior on the intended device."),
        "linked_row": None,
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "qualifies": False,
        "statement": (
            "No provider/intake/public-surface/release decision exists; the "
            "installed v0 geometry and shared build remain untouched."),
        "reopen_condition": (
            "Open a separate versioned, OFF-by-default opt-in provider intake "
            "with an exact asset/descriptor/config, clean-install proof and "
            "independent exact-head review after all prior gates clear."),
        "linked_row": None,
    },
)

RATE_PROFILE_ROWS = (
    {
        "id": "RATE-01",
        "requirement": "Measure source/output mapping and duration.",
        "status": "blocked",
        "evidence": (
            "The candidate is a rate estimator, not a TSM renderer, and no "
            "source/output mapping or duration result exists."),
    },
    {
        "id": "RATE-02",
        "requirement": "Measure pitch and transient audibility.",
        "status": "blocked",
        "evidence": (
            "No rendered output, F0/transient metric or listening result "
            "exists for a wav2vec2 plus ridge rate path."),
    },
    {
        "id": "RATE-03",
        "requirement": "Measure playback buffering.",
        "status": "blocked",
        "evidence": (
            "No playback chain, queue, fill/flush or buffering measurement "
            "exists."),
    },
    {
        "id": "RATE-04",
        "requirement": "Include 1x and rate changes.",
        "status": "blocked",
        "evidence": (
            "No 1x or rate-change comparison exists; a syllables/second "
            "estimate is not a speed factor."),
    },
    {
        "id": "RATE-05",
        "requirement": "Include unfamiliar speech, music and silence.",
        "status": "blocked",
        "evidence": (
            "The historical pilot is one AMI meeting of speech; no unfamiliar "
            "speech, music, silence or language coverage was tested."),
    },
    {
        "id": "RATE-06",
        "requirement": "Include rebuffer, drift and the final partial window.",
        "status": "blocked",
        "evidence": (
            "No stream, rebuffer, clock-drift or partial-window behavior was "
            "measured."),
    },
    {
        "id": "RATE-07",
        "requirement": (
            "Keep pause or filler decisions tied to source timestamps and "
            "measure speech preservation."),
        "status": "blocked",
        "evidence": (
            "No pause/filler controller, source-timestamp mapping or speech-"
            "preservation measurement exists."),
    },
    {
        "id": "RATE-08",
        "requirement": (
            "Map estimated rate to a reviewed preferred-speed policy."),
        "status": "blocked",
        "evidence": (
            "No preference/acceptability labels or rate-to-speed policy "
            "exists; none is inferred from the historical syllable-rate "
            "score."),
    },
)

QUALITY_ROWS = (
    {
        "id": "QUAL-01",
        "outcome": "fp32_reference_accuracy",
        "status": "blocked",
        "value": None,
        "evidence": (
            "Recorded pilot FP32 CV is provenance only; no local score was "
            "reproduced."),
    },
    {
        "id": "QUAL-02",
        "outcome": "nonnegative_clipped_rate_accuracy",
        "status": "blocked",
        "value": None,
        "evidence": (
            "The recorded post-hoc clip is not a locally reproduced result and "
            "does not define a product floor."),
    },
    {
        "id": "QUAL-03",
        "outcome": "finite_output_and_output_bounds",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No nonfinite scan, minimum/maximum prediction bound or "
            "invalid/missing-input control was run against the real head."),
    },
    {
        "id": "QUAL-04",
        "outcome": "constant_baseline_comparison",
        "status": "blocked",
        "value": None,
        "evidence": (
            "The recorded training-fold-mean baseline is context only; no "
            "paired local comparison or zero-rate control exists."),
    },
)

TIMING_ROWS = (
    {
        "id": "TIME-01",
        "metric": "encoder_latency_p95",
        "status": "blocked",
        "value": None,
        "evidence": "No local encoder timing was measured.",
    },
    {
        "id": "TIME-02",
        "metric": "real_time_factor",
        "status": "blocked",
        "value": None,
        "evidence": "No local RTF was measured.",
    },
    {
        "id": "TIME-03",
        "metric": "device_deadline_and_callback",
        "status": "blocked",
        "value": None,
        "evidence": "No device, pacing or callback deadline was measured.",
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
    "No wav2vec2 weight, tokenizer asset or ridge-head artifact is present.",
    "No torch, transformers, scikit-learn or numpy runtime is imported or executed.",
    "No audio, transcript, syllable label or derived embedding is read or scored.",
    "No FP32 accuracy, finite-output, baseline or timing result is reproduced.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "A syllables/second estimate is not a preferred speed factor or a TSM setting.",
)

REQUIRED_RESULTS = (
    "Exact upstream snapshot revision, per-file byte counts and SHA-256.",
    "Reviewed model-card, weight and notice terms plus product-use decision.",
    "Serialized or reproducibly pinned per-fold ridge-head artifact.",
    "Locked offline Python 3.10.13/torch 2.2.2/transformers 4.40.2 runtime.",
    "Rights-cleared multi-meeting rate cohort with checked syllable labels.",
    "Reproduced FP32 accuracy, finite-output and constant/zero baseline controls.",
    "Exact Rate-profile mapping, buffering, condition and preservation evidence.",
    "Target-device p95/p99 timing, resources and deadline behavior.",
    "Separate OFF-by-default provider intake and independent exact-head review.",
)

PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility and "
    "playback buffering",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation",
)

ABSENCE_PROBES = (
    "data/models/speech-rate-encoders",
    "data/models/speech-rate-encoders/wav2vec2-base-960h",
    "data/models/speech-rate-encoders/wav2vec2-base-960h/model.safetensors",
    "data/models/speech-rate-encoders/wav2vec2-base-960h/config.json",
    "data/models/speech-rate-encoders/wav2vec2-base-960h/ridge_head.joblib",
    "data/models/speech-rate-encoders/wav2vec2-base-960h/model_head.json",
    "data/models/wav2vec2-base-960h",
    "data/checkouts/wav2vec2-base-960h",
    "data/envs",
    "data/envs/sylnet-py310",
    "data/envs/sylnet-py310/bin/python",
    "data/envs/sylnet-py310/lib/python3.10/site-packages/torch/__init__.py",
    "data/envs/sylnet-py310/lib/python3.10/site-packages/transformers/"
    "__init__.py",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_model.safetensors",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_fp32_model.pt",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_ridge_head.joblib",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_ridge_head.json",
    "research/tsm-followup-20261101/agent-neural/run/"
    "wav2vec2-base-960h_head.npz",
)

HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--facebook--wav2vec2-base-960h",
    "~/.cache/huggingface/hub/models--facebook--wav2vec2-base-960h/snapshots",
    "~/.cache/huggingface/hub/models--facebook--wav2vec2-base-960h/blobs",
    "~/.cache/torch/hub/checkpoints",
)

RECIPE_SNIPPETS = (
    "torch.set_num_threads(1)",
    "torch.set_num_interop_threads(1)",
    "make_pipeline(StandardScaler(), Ridge(alpha=10.0))",
    "out.last_hidden_state.mean(dim=1)",
    "local_files_only=True",
    "revision=revision",
)

SCORE_SNIPPETS = (
    "np.maximum(pred, 0.0)",
)

MANIFEST_FIELDS = ("schema_id", "cohort_id", "encoder", "weights", "runtime",
                   "feature_extractor", "head", "audio", "labels", "controls",
                   "outcomes", "rights")
ENCODER_FIELDS = ("repo_id", "revision", "license_id", "model_card_sha256")
WEIGHT_FIELDS = ("sha256", "byte_count", "terms_sha256")
RUNTIME_FIELDS = ("python", "torch", "transformers", "device",
                  "intra_op_threads", "interop_op_threads",
                  "deterministic_algorithms", "offline")
FEATURE_FIELDS = ("sample_rate_hz", "window_samples", "normalize",
                  "config_sha256")
HEAD_FIELDS = ("kind", "alpha", "scaler", "folds", "seed", "artifact_sha256")
AUDIO_FIELDS = ("id", "path", "sha256", "language", "speaker_group",
                "meeting_id", "start_s", "end_s", "active_s",
                "reference_rate_sps")
LABEL_FIELDS = ("source", "cmudict_version", "transcript_source",
                "human_syllable_nuclei", "coverage_min")
CONTROL_FIELDS = ("id", "kind")
OUTCOME_FIELDS = ("mae_syllables_per_second", "rmse_syllables_per_second",
                  "bias_syllables_per_second", "pearson_r", "p95_encoder_ms",
                  "nonfinite_count", "sample_count")
RIGHTS_FIELDS = ("dataset_terms_reference", "model_terms_reference",
                 "dictionary_terms_reference", "output_use_reference",
                 "review_reference", "claims_qualified")

REQUIRED_WEIGHT_NAMES = (
    "config.json", "feature_extractor_config.json", "model.safetensors",
    "preprocessor_config.json", "tokenizer_config.json", "vocab.json")
CONTROL_KINDS = ("fp32_candidate", "constant_fold_mean_baseline",
                 "zero_rate_baseline")

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ABSOLUTE = re.compile(r"^/[A-Za-z0-9._/-]+$")
MAX_RATE = 20.0
MAX_TIMING_MS = 60000.0


# --------------------------------------------------------------------------
# Strict JSON and canonical serialization
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def loads_strict(text: str) -> dict:
    """Parse a strict JSON object; reject duplicate keys, NaN and Infinity."""
    if text.startswith("\ufeff"):
        raise ValueError("json_byte_order_mark")
    parsed = json.loads(text, object_pairs_hook=_unique_object,
                        parse_constant=_reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict:
    return loads_strict(Path(path).read_text(encoding="utf-8"))


def canonical_text(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: Any) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _no_floats(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_report:" + (path or "<root>"))
    if isinstance(value, dict):
        for key in sorted(value):
            _no_floats(value[key], (path + "." + str(key)).lstrip("."))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, f"{path}[{index}]")


def _decimal_string(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("nonfinite_decimal")
    text = repr(float(value))
    if "e" in text or "E" in text:
        text = format(float(value), ".17f").rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        text = "0"
    if text.startswith("+"):
        text = text[1:]
    return text


# --------------------------------------------------------------------------
# Pins, board identity and absence probes
# --------------------------------------------------------------------------
def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative in sorted(pins):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != pins[relative]:
            raise ValueError("pin_digest_mismatch:" + relative)
        rows[relative] = {"sha256": pins[relative], "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(path: Path) -> dict:
    board = read_strict_json(path)
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ValueError("board_row_not_unique:" + TASK)
    return {field: rows[0].get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows(path: Path | None = None) -> list[dict]:
    board = read_strict_json(path or (AUDIO_ROOT / BOARD_TASK_ROW))
    by_id = {row.get("id"): row for row in board.get("tasks", [])
             if isinstance(row, dict)}
    rows: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_missing:" + row_id)
        rows.append({field: row.get(field) for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def absence_probes(audio_root: Path, probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory; any present path blocks shipping."""
    sdk_root = WORKTREE if worktree is None else worktree
    rows: list[dict] = []
    for relative in probes:
        workspace_path = Path(audio_root) / relative
        sdk_candidate = sdk_root / relative
        if workspace_path.exists() or sdk_candidate.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def home_absence_probes(
        probes: tuple[str, ...] = HOME_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    home = Path.home()
    for relative in probes:
        path = (home / relative[2:] if relative.startswith("~/")
                else Path(relative))
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_home_cache": True,
                     "present": False})
    return rows


def absence_summary(rows: list[dict], home_rows: list[dict]) -> dict:
    all_rows = rows + home_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(rows),
        "home_probe_count": len(home_rows),
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


def recipe_provenance() -> dict:
    """Verify the pinned runner contains the exact historical FP32 recipe."""
    relative = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "run_ssl_encoder_cv.py")
    score_relative = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "score_nonnegative_heads.py")
    text = (AUDIO_ROOT / relative).read_text(encoding="utf-8")
    score_text = (AUDIO_ROOT / score_relative).read_text(encoding="utf-8")
    found = {snippet: (snippet in text) for snippet in RECIPE_SNIPPETS}
    missing = [snippet for snippet, present in found.items() if not present]
    if missing:
        raise ValueError("recipe_snippet_missing:" + missing[0])
    score_found = {snippet: (snippet in score_text)
                   for snippet in SCORE_SNIPPETS}
    score_missing = [snippet for snippet, present in score_found.items()
                     if not present]
    if score_missing:
        raise ValueError("score_snippet_missing:" + score_missing[0])
    return {
        "source": relative,
        "sha256": SOURCE_PINS[relative],
        "score_source": score_relative,
        "score_sha256": SOURCE_PINS[score_relative],
        "feature_pooling": FEATURE_POOLING,
        "head_kind": HEAD_KIND,
        "head_alpha": HEAD_ALPHA,
        "head_scaler": HEAD_SCALER,
        "folds": HEAD_FOLDS,
        "threads": "1 intra-op / 1 inter-op",
        "recipe_snippets_present": len(found),
        "recipe_snippets_required": len(RECIPE_SNIPPETS),
        "score_snippets_present": len(score_found),
        "score_snippets_required": len(SCORE_SNIPPETS),
        "saved_head_artifact": False,
        "recorded_only": True,
        "executed_here": False,
    }


def documented_metrics() -> dict:
    """Read the pinned results JSON and return provenance-only decimal strings."""
    relative = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "wav2vec2-base-960h_results.json")
    data = read_strict_json(AUDIO_ROOT / relative)
    source = data.get("model_source", {})
    if source.get("repo_id") != UPSTREAM_REPO \
            or source.get("revision") != UPSTREAM_REVISION \
            or source.get("license") != UPSTREAM_LICENSE:
        raise ValueError("documented_model_source_mismatch")
    files = source.get("files", {})
    weight = files.get("model.safetensors", {})
    if weight.get("bytes") != MODEL_WEIGHT_BYTES \
            or weight.get("sha256") != MODEL_WEIGHT_SHA256:
        raise ValueError("documented_weight_record_mismatch")
    runtime = data.get("runtime", {})
    if runtime.get("python", "").split()[0] != RUNTIME_PYTHON \
            or runtime.get("torch") != RUNTIME_TORCH \
            or runtime.get("transformers") != RUNTIME_TRANSFORMERS:
        raise ValueError("documented_runtime_mismatch")
    fp32 = data.get("fp32", {})
    cv = fp32.get("cross_validation", {})
    clipped = fp32.get("nonnegative_clipped", {})
    clipped_metrics = clipped.get("metrics", {})
    baseline = fp32.get("training_fold_mean_baseline", {})
    if cv.get("n") != COHORT_WINDOW_COUNT \
            or clipped_metrics.get("n") != COHORT_WINDOW_COUNT \
            or baseline.get("n") != COHORT_WINDOW_COUNT:
        raise ValueError("documented_cohort_mismatch")
    if data.get("feature_and_head") != (
            "mean pool last hidden layer across time; standard scaling + "
            "sklearn Ridge(alpha=10), re-fit in each of five chronological "
            "folds"):
        raise ValueError("documented_feature_head_mismatch")
    return {
        "source_path": relative,
        "source_sha256": SOURCE_PINS[relative],
        "repo_id": source["repo_id"],
        "revision": source["revision"],
        "license": source["license"],
        "weight_bytes": str(MODEL_WEIGHT_BYTES),
        "weight_sha256": MODEL_WEIGHT_SHA256,
        "runtime_python": RUNTIME_PYTHON,
        "runtime_torch": RUNTIME_TORCH,
        "runtime_transformers": RUNTIME_TRANSFORMERS,
        "device": "cpu",
        "parameter_count": str(UPSTREAM_PARAMETERS),
        "serialized_model_bytes": str(UPSTREAM_SERIALIZED_BYTES),
        "feature_pooling": FEATURE_POOLING,
        "head_kind": HEAD_KIND,
        "head_alpha": HEAD_ALPHA,
        "head_scaler": HEAD_SCALER,
        "head_folds": str(HEAD_FOLDS),
        "mean_encoder_ms_per_clip": _decimal_string(
            float(fp32["mean_encoder_ms_per_clip"])),
        "p50_encoder_ms_per_clip": _decimal_string(
            float(fp32["p50_encoder_ms_per_clip"])),
        "p95_encoder_ms_per_clip": _decimal_string(
            float(fp32["p95_encoder_ms_per_clip"])),
        "mean_encoder_rtf": _decimal_string(float(fp32["mean_encoder_rtf"])),
        "raw_mae_syllables_per_second": _decimal_string(
            float(cv["mae_syllables_per_second"])),
        "raw_rmse_syllables_per_second": _decimal_string(
            float(cv["rmse_syllables_per_second"])),
        "raw_bias_syllables_per_second": _decimal_string(
            float(cv["bias_syllables_per_second"])),
        "raw_pearson_r": _decimal_string(float(cv["pearson_r"])),
        "nonnegative_negative_prediction_count": str(
            int(clipped["negative_prediction_count"])),
        "nonnegative_minimum_unclipped_sps": _decimal_string(
            float(clipped["minimum_unclipped_prediction_sps"])),
        "nonnegative_maximum_unclipped_sps": _decimal_string(
            float(clipped["maximum_unclipped_prediction_sps"])),
        "nonnegative_mae_syllables_per_second": _decimal_string(
            float(clipped_metrics["mae_syllables_per_second"])),
        "nonnegative_rmse_syllables_per_second": _decimal_string(
            float(clipped_metrics["rmse_syllables_per_second"])),
        "nonnegative_bias_syllables_per_second": _decimal_string(
            float(clipped_metrics["bias_syllables_per_second"])),
        "nonnegative_pearson_r": _decimal_string(
            float(clipped_metrics["pearson_r"])),
        "baseline_mae_syllables_per_second": _decimal_string(
            float(baseline["mae_syllables_per_second"])),
        "baseline_rmse_syllables_per_second": _decimal_string(
            float(baseline["rmse_syllables_per_second"])),
        "baseline_pearson_r": _decimal_string(
            float(baseline["pearson_r"])),
        "cohort_windows": str(COHORT_WINDOW_COUNT),
        "window_samples": str(COHORT_WINDOW_SAMPLES),
        "window_seconds": COHORT_WINDOW_SECONDS,
        "sample_rate_hz": str(SAMPLE_RATE_HZ),
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
    }


def source_presence() -> dict:
    runner = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "run_ssl_encoder_cv.py")
    score = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "score_nonnegative_heads.py")
    source_record = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "wav2vec2-base-960h_source.json")
    results = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "wav2vec2-base-960h_results.json")
    fp32_npz = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "wav2vec2-base-960h_fp32_embeddings.npz")
    manifest = (
        "research/tsm-followup-20261101/agent-neural/run/"
        "syl_eval_manifest.json")
    rows = []
    for relative in (runner, score, source_record, results, fp32_npz,
                     manifest):
        path = AUDIO_ROOT / relative
        rows.append(pin_rows({relative: SOURCE_PINS[relative]},
                             AUDIO_ROOT)[relative] | {
            "path": relative,
            "byte_count": path.stat().st_size,
            "role": "provenance_only_not_signal_weights_or_head",
        })
    return {
        "research_runner_present": True,
        "upstream_source_record_present": True,
        "results_record_present": True,
        "derived_embedding_archive_present": True,
        "exact_weights_present": False,
        "exact_runtime_present": False,
        "ridge_head_artifact_present": False,
        "exact_source_weights_head_runtime_conjunction_present": False,
        "weights_used": False,
        "runtime_imported": False,
        "head_loaded": False,
        "audio_read": False,
        "model_executed": False,
        "derived_artifacts": rows,
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
    """Validate a caller-supplied FP32 rate cohort; never mutate it."""
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != ADMISSION_SCHEMA_ID:
        raise ValueError("value:manifest.schema_id")
    _text(root, "cohort_id", "manifest", SLUG, 64)

    encoder = _exact_keys(root["encoder"], ENCODER_FIELDS, "encoder")
    if encoder["repo_id"] != UPSTREAM_REPO:
        raise ValueError("value:encoder.repo_id")
    if encoder["revision"] != UPSTREAM_REVISION:
        raise ValueError("value:encoder.revision")
    if encoder["license_id"] != UPSTREAM_LICENSE:
        raise ValueError("value:encoder.license_id")
    if encoder["model_card_sha256"] != UPSTREAM_FILES["README.md"]["sha256"]:
        raise ValueError("value:encoder.model_card_sha256")

    weights = _exact_keys(root["weights"], ("files",), "weights")
    files = _exact_keys(weights["files"], REQUIRED_WEIGHT_NAMES,
                        "weights.files")
    for name in REQUIRED_WEIGHT_NAMES:
        record = _exact_keys(files[name], WEIGHT_FIELDS,
                             "weights.files." + name)
        expected = UPSTREAM_FILES[name]
        if record["sha256"] != expected["sha256"]:
            raise ValueError("value:weights.files." + name + ".sha256")
        if record["byte_count"] != expected["byte_count"]:
            raise ValueError("value:weights.files." + name + ".byte_count")
        _hex(record, "terms_sha256", "weights.files." + name)

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    if runtime["python"] != RUNTIME_PYTHON:
        raise ValueError("value:runtime.python")
    if runtime["torch"] != RUNTIME_TORCH:
        raise ValueError("value:runtime.torch")
    if runtime["transformers"] != RUNTIME_TRANSFORMERS:
        raise ValueError("value:runtime.transformers")
    if runtime["device"] != "cpu":
        raise ValueError("value:runtime.device")
    _int(runtime, "intra_op_threads", "runtime", 1, 1)
    _int(runtime, "interop_op_threads", "runtime", 1, 1)
    _boolean(runtime, "deterministic_algorithms", "runtime", True)
    _boolean(runtime, "offline", "runtime", True)

    feature = _exact_keys(root["feature_extractor"], FEATURE_FIELDS,
                          "feature_extractor")
    if feature["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("value:feature_extractor.sample_rate_hz")
    if feature["window_samples"] != COHORT_WINDOW_SAMPLES:
        raise ValueError("value:feature_extractor.window_samples")
    _boolean(feature, "normalize", "feature_extractor", True)
    if feature["config_sha256"] != \
            UPSTREAM_FILES["preprocessor_config.json"]["sha256"]:
        raise ValueError("value:feature_extractor.config_sha256")

    head = _exact_keys(root["head"], HEAD_FIELDS, "head")
    if head["kind"] != HEAD_KIND:
        raise ValueError("value:head.kind")
    alpha = head["alpha"]
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) \
            or float(alpha) != float(HEAD_ALPHA):
        raise ValueError("value:head.alpha")
    if head["scaler"] != HEAD_SCALER:
        raise ValueError("value:head.scaler")
    _int(head, "folds", "head", HEAD_FOLDS, HEAD_FOLDS)
    _int(head, "seed", "head", 0, 4294967295)
    _hex(head, "artifact_sha256", "head")

    audio = root["audio"]
    if not isinstance(audio, list) or len(audio) != COHORT_WINDOW_COUNT:
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
        if row["meeting_id"] != COHORT_MEETING_ID:
            raise ValueError("value:" + path + ".meeting_id")
        start = _number(row, "start_s", path, 0.0, 86400.0)
        end = _number(row, "end_s", path, 0.0, 86400.0)
        if abs((end - start) - float(COHORT_WINDOW_SECONDS)) > 1e-9:
            raise ValueError("span:" + path)
        _number(row, "active_s", path, 0.000001, 4.0)
        _number(row, "reference_rate_sps", path, 0.0, MAX_RATE)

    labels = _exact_keys(root["labels"], LABEL_FIELDS, "labels")
    if labels["source"] != "cmudict-first-pronunciation":
        raise ValueError("value:labels.source")
    if labels["cmudict_version"] != CMUDICT_VERSION:
        raise ValueError("value:labels.cmudict_version")
    if labels["transcript_source"] != "ami-orthographic":
        raise ValueError("value:labels.transcript_source")
    _boolean(labels, "human_syllable_nuclei", "labels", False)
    coverage = labels["coverage_min"]
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)) \
            or float(coverage) != 0.75:
        raise ValueError("value:labels.coverage_min")

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
    _number(outcomes, "mae_syllables_per_second", "outcomes", 0.0, 10.0)
    _number(outcomes, "rmse_syllables_per_second", "outcomes", 0.0, 10.0)
    _number(outcomes, "bias_syllables_per_second", "outcomes", -10.0, 10.0)
    _number(outcomes, "pearson_r", "outcomes", -1.0, 1.0)
    _number(outcomes, "p95_encoder_ms", "outcomes", 0.0, MAX_TIMING_MS)
    _int(outcomes, "nonfinite_count", "outcomes", 0, 0)
    _int(outcomes, "sample_count", "outcomes", COHORT_WINDOW_COUNT,
         COHORT_WINDOW_COUNT)

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for key in ("dataset_terms_reference", "model_terms_reference",
                "dictionary_terms_reference", "output_use_reference",
                "review_reference"):
        _text(rights, key, "rights", None, 1024)
    _boolean(rights, "claims_qualified", "rights", False)


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-control:" + label).encode()).hexdigest()


def control_manifest() -> dict:
    """Build the one structural control; it is not evidence of any result."""
    audio = []
    for index in range(COHORT_WINDOW_COUNT):
        start = float(index * 4)
        audio.append({
            "id": f"synthetic-window-{index:04d}",
            "path": f"/synthetic/ami-en2003a/{index:04d}.wav",
            "sha256": f"{index + 1:064x}",
            "language": "en",
            "speaker_group": f"group-{index % 4}",
            "meeting_id": COHORT_MEETING_ID,
            "start_s": start,
            "end_s": start + 4.0,
            "active_s": 3.5,
            "reference_rate_sps": 4.5 + (index % 5) / 10.0,
        })
    files = {}
    for name in REQUIRED_WEIGHT_NAMES:
        files[name] = {
            "sha256": UPSTREAM_FILES[name]["sha256"],
            "byte_count": UPSTREAM_FILES[name]["byte_count"],
            "terms_sha256": _synthetic_digest("terms:" + name),
        }
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cohort_id": "synthetic-ami-en2003a-210",
        "encoder": {
            "repo_id": UPSTREAM_REPO,
            "revision": UPSTREAM_REVISION,
            "license_id": UPSTREAM_LICENSE,
            "model_card_sha256": UPSTREAM_FILES["README.md"]["sha256"],
        },
        "weights": {"files": files},
        "runtime": {
            "python": RUNTIME_PYTHON,
            "torch": RUNTIME_TORCH,
            "transformers": RUNTIME_TRANSFORMERS,
            "device": "cpu",
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
        },
        "feature_extractor": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "window_samples": COHORT_WINDOW_SAMPLES,
            "normalize": True,
            "config_sha256": UPSTREAM_FILES[
                "preprocessor_config.json"]["sha256"],
        },
        "head": {
            "kind": HEAD_KIND,
            "alpha": 10.0,
            "scaler": HEAD_SCALER,
            "folds": HEAD_FOLDS,
            "seed": 20261126,
            "artifact_sha256": _synthetic_digest("ridge-head"),
        },
        "audio": audio,
        "labels": {
            "source": "cmudict-first-pronunciation",
            "cmudict_version": CMUDICT_VERSION,
            "transcript_source": "ami-orthographic",
            "human_syllable_nuclei": False,
            "coverage_min": 0.75,
        },
        "controls": [
            {"id": "control-fp32", "kind": "fp32_candidate"},
            {"id": "control-mean", "kind": "constant_fold_mean_baseline"},
            {"id": "control-zero", "kind": "zero_rate_baseline"},
        ],
        "outcomes": {
            "mae_syllables_per_second": 0.6,
            "rmse_syllables_per_second": 0.75,
            "bias_syllables_per_second": 0.0,
            "pearson_r": 0.85,
            "p95_encoder_ms": 184.0,
            "nonfinite_count": 0,
            "sample_count": COHORT_WINDOW_COUNT,
        },
        "rights": {
            "dataset_terms_reference": "synthetic://rights/ami-not-reviewed",
            "model_terms_reference": "synthetic://rights/model-not-reviewed",
            "dictionary_terms_reference": "synthetic://rights/cmudict",
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

    def duplicate_audio_id(document: dict) -> None:
        document["audio"][1]["id"] = document["audio"][0]["id"]

    def duplicate_control_kind(document: dict) -> None:
        document["controls"][1]["kind"] = document["controls"][0]["kind"]

    def extra_weight(document: dict) -> None:
        document["weights"]["files"]["extra.safetensors"] = copy.deepcopy(
            document["weights"]["files"]["model.safetensors"])

    def short_audio(document: dict) -> None:
        document["audio"].pop()

    def relative_path(document: dict) -> None:
        document["audio"][0]["path"] = "synthetic/ami-en2003a/0000.wav"

    def span_mismatch(document: dict) -> None:
        document["audio"][0]["end_s"] = 3.0

    def extra_field(document: dict) -> None:
        document["extra"] = True

    def missing_field(document: dict) -> None:
        del document["encoder"]

    def wrong_schema(document: dict) -> None:
        document["schema_id"] = "audio-sdk/other/0.1"

    def nonfinite_rate(document: dict) -> None:
        document["audio"][0]["reference_rate_sps"] = float("nan")

    def nonfinite_mae(document: dict) -> None:
        document["outcomes"]["mae_syllables_per_second"] = float("inf")

    def bool_as_int(document: dict) -> None:
        document["runtime"]["intra_op_threads"] = True

    def bool_as_byte_count(document: dict) -> None:
        document["weights"]["files"]["model.safetensors"]["byte_count"] = True

    mutations = [
        ("ADM-01", "missing_encoder", missing_field),
        ("ADM-02", "extra_top_level_field", extra_field),
        ("ADM-03", "wrong_schema_id", wrong_schema),
        ("ADM-04", "cohort_id_not_slug",
         set_path(("cohort_id",), "Not A Slug")),
        ("ADM-05", "wrong_repo_id", set_path(("encoder", "repo_id"),
                                            "other/model")),
        ("ADM-06", "revision_not_40_hex",
         set_path(("encoder", "revision"), UPSTREAM_REVISION[:39])),
        ("ADM-07", "revision_uppercase",
         set_path(("encoder", "revision"), UPSTREAM_REVISION.upper())),
        ("ADM-08", "wrong_license", set_path(("encoder", "license_id"), "mit")),
        ("ADM-09", "wrong_model_card_digest",
         set_path(("encoder", "model_card_sha256"), "0" * 64)),
        ("ADM-10", "missing_model_weights",
         del_path(("weights", "files", "model.safetensors"))),
        ("ADM-11", "missing_config",
         del_path(("weights", "files", "config.json"))),
        ("ADM-12", "missing_preprocessor",
         del_path(("weights", "files", "preprocessor_config.json"))),
        ("ADM-13", "extra_weight_file", extra_weight),
        ("ADM-14", "wrong_weight_sha",
         set_path(("weights", "files", "model.safetensors", "sha256"),
                  "0" * 64)),
        ("ADM-15", "short_weight_sha",
         set_path(("weights", "files", "model.safetensors", "sha256"),
                  "abc")),
        ("ADM-16", "wrong_weight_bytes",
         set_path(("weights", "files", "model.safetensors", "byte_count"),
                  1)),
        ("ADM-17", "bool_weight_bytes", bool_as_byte_count),
        ("ADM-18", "missing_terms_digest",
         del_path(("weights", "files", "config.json", "terms_sha256"))),
        ("ADM-19", "wrong_python",
         set_path(("runtime", "python"), "3.12.16")),
        ("ADM-20", "wrong_torch", set_path(("runtime", "torch"), "2.4.0")),
        ("ADM-21", "wrong_transformers",
         set_path(("runtime", "transformers"), "4.44.0")),
        ("ADM-22", "cuda_device", set_path(("runtime", "device"), "cuda")),
        ("ADM-23", "wrong_intra_threads",
         set_path(("runtime", "intra_op_threads"), 2)),
        ("ADM-24", "wrong_interop_threads",
         set_path(("runtime", "interop_op_threads"), 2)),
        ("ADM-25", "determinism_off",
         set_path(("runtime", "deterministic_algorithms"), False)),
        ("ADM-26", "offline_off", set_path(("runtime", "offline"), False)),
        ("ADM-27", "bool_as_int_threads", bool_as_int),
        ("ADM-28", "wrong_sample_rate",
         set_path(("feature_extractor", "sample_rate_hz"), 8000)),
        ("ADM-29", "wrong_window_samples",
         set_path(("feature_extractor", "window_samples"), 32000)),
        ("ADM-30", "normalize_off",
         set_path(("feature_extractor", "normalize"), False)),
        ("ADM-31", "wrong_feature_digest",
         set_path(("feature_extractor", "config_sha256"), "0" * 64)),
        ("ADM-32", "wrong_head_kind", set_path(("head", "kind"), "mlp")),
        ("ADM-33", "wrong_head_alpha", set_path(("head", "alpha"), 5.0)),
        ("ADM-34", "wrong_head_folds", set_path(("head", "folds"), 4)),
        ("ADM-35", "wrong_head_scaler",
         set_path(("head", "scaler"), "minmax")),
        ("ADM-36", "wrong_head_seed", set_path(("head", "seed"), -1)),
        ("ADM-37", "missing_head_artifact",
         del_path(("head", "artifact_sha256"))),
        ("ADM-38", "short_head_artifact",
         set_path(("head", "artifact_sha256"), "abc")),
        ("ADM-39", "short_audio", short_audio),
        ("ADM-40", "duplicate_audio_id", duplicate_audio_id),
        ("ADM-41", "relative_audio_path", relative_path),
        ("ADM-42", "short_audio_sha",
         set_path(("audio", 0, "sha256"), "abc")),
        ("ADM-43", "nonfinite_audio_rate", nonfinite_rate),
        ("ADM-44", "negative_audio_rate",
         set_path(("audio", 0, "reference_rate_sps"), -1.0)),
        ("ADM-45", "zero_active_s", set_path(("audio", 0, "active_s"), 0.0)),
        ("ADM-46", "negative_start", set_path(("audio", 0, "start_s"), -4.0)),
        ("ADM-47", "span_mismatch", span_mismatch),
        ("ADM-48", "wrong_language", set_path(("audio", 0, "language"), "fr")),
        ("ADM-49", "wrong_meeting",
         set_path(("audio", 0, "meeting_id"), "ES2004a")),
        ("ADM-50", "empty_speaker_group",
         set_path(("audio", 0, "speaker_group"), "")),
        ("ADM-51", "wrong_label_source",
         set_path(("labels", "source"), "human-annotated")),
        ("ADM-52", "wrong_cmudict_version",
         set_path(("labels", "cmudict_version"), "1.0.0")),
        ("ADM-53", "human_nuclei_claim",
         set_path(("labels", "human_syllable_nuclei"), True)),
        ("ADM-54", "wrong_transcript_source",
         set_path(("labels", "transcript_source"), "manual")),
        ("ADM-55", "low_coverage",
         set_path(("labels", "coverage_min"), 0.5)),
        ("ADM-56", "missing_control", lambda d: d["controls"].pop()),
        ("ADM-57", "duplicate_control_kind", duplicate_control_kind),
        ("ADM-58", "unknown_control_kind",
         set_path(("controls", 0, "kind"), "identity_passthrough")),
        ("ADM-59", "extra_control",
         lambda d: d["controls"].append(
             {"id": "control-extra", "kind": "fp32_candidate"})),
        ("ADM-60", "nonfinite_mae", nonfinite_mae),
        ("ADM-61", "mae_out_of_range",
         set_path(("outcomes", "mae_syllables_per_second"), 11.0)),
        ("ADM-62", "pearson_r_out_of_range",
         set_path(("outcomes", "pearson_r"), 1.01)),
        ("ADM-63", "negative_p95",
         set_path(("outcomes", "p95_encoder_ms"), -1.0)),
        ("ADM-64", "nonfinite_count_nonzero",
         set_path(("outcomes", "nonfinite_count"), 1)),
        ("ADM-65", "wrong_sample_count",
         set_path(("outcomes", "sample_count"), 209)),
        ("ADM-66", "missing_pearson_r",
         del_path(("outcomes", "pearson_r"))),
        ("ADM-67", "missing_dataset_terms",
         del_path(("rights", "dataset_terms_reference"))),
        ("ADM-68", "empty_output_use",
         set_path(("rights", "output_use_reference"), "")),
        ("ADM-69", "qualified_claim",
         set_path(("rights", "claims_qualified"), True)),
        ("ADM-70", "extra_rights_field",
         set_path(("rights", "extra"), "x")),
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
        "weights_present": False,
        "runtime_present": False,
        "head_artifact_present": False,
        "fp32_result": False,
        "accuracy_result": False,
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
        "exact_model": {
            "repo_id": UPSTREAM_REPO,
            "revision": UPSTREAM_REVISION,
            "license": UPSTREAM_LICENSE,
            "parameter_count": str(UPSTREAM_PARAMETERS),
            "serialized_model_bytes": str(UPSTREAM_SERIALIZED_BYTES),
            "weight_bytes": str(MODEL_WEIGHT_BYTES),
            "weight_sha256": MODEL_WEIGHT_SHA256,
            "files_documented_locally_verified": False,
            "files": {name: dict(record)
                      for name, record in sorted(UPSTREAM_FILES.items())},
            "locally_present": False,
            "downloaded_or_reconstructed": False,
        },
        "exact_head": {
            "kind": HEAD_KIND,
            "alpha": HEAD_ALPHA,
            "scaler": HEAD_SCALER,
            "folds": HEAD_FOLDS,
            "feature_pooling": FEATURE_POOLING,
            "artifact_present": False,
            "artifact_sha256": None,
            "trained_in_fold_only": True,
            "serialized": False,
        },
        "historical_recipe": {
            "source": (
                "research/tsm-followup-20261101/agent-neural/run/"
                "run_ssl_encoder_cv.py"),
            "score_source": (
                "research/tsm-followup-20261101/agent-neural/run/"
                "score_nonnegative_heads.py"),
            "feature_pooling": FEATURE_POOLING,
            "head_kind": HEAD_KIND,
            "head_alpha": HEAD_ALPHA,
            "head_scaler": HEAD_SCALER,
            "folds": HEAD_FOLDS,
            "saved_head_artifact": False,
            "executed_here": False,
        },
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "release_gates": gates,
        "rate_profile_requirements": [dict(row) for row in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "encoder_fields": list(ENCODER_FIELDS),
            "weight_names": list(REQUIRED_WEIGHT_NAMES),
            "runtime_fields": list(RUNTIME_FIELDS),
            "feature_fields": list(FEATURE_FIELDS),
            "head_fields": list(HEAD_FIELDS),
            "audio_fields": list(AUDIO_FIELDS),
            "label_fields": list(LABEL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "outcome_fields": list(OUTCOME_FIELDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "cohort_window_count": COHORT_WINDOW_COUNT,
            "window_samples": COHORT_WINDOW_SAMPLES,
            "cohort_window_seconds": COHORT_WINDOW_SECONDS,
            "exact_revision_required": UPSTREAM_REVISION,
            "exact_weight_sha256_required": MODEL_WEIGHT_SHA256,
            "exact_weight_bytes_required": str(MODEL_WEIGHT_BYTES),
            "head_required": {
                "kind": HEAD_KIND,
                "alpha": HEAD_ALPHA,
                "scaler": HEAD_SCALER,
                "folds": HEAD_FOLDS,
            },
            "runtime_required": {
                "python": RUNTIME_PYTHON,
                "torch": RUNTIME_TORCH,
                "transformers": RUNTIME_TRANSFORMERS,
                "device": "cpu",
                "intra_op_threads": 1,
                "interop_op_threads": 1,
                "deterministic_algorithms": True,
                "offline": True,
            },
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "upstream_license_reviewed": False,
            "weight_terms_reviewed": False,
            "corpus_terms_reviewed": False,
            "dictionary_terms_reviewed": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
    }
    workspace_probes = absence_probes(AUDIO_ROOT)
    home_probes = home_absence_probes()
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
        "exact_model": contract["exact_model"],
        "exact_head": contract["exact_head"],
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
            "derived_archive_note": (
                "The FP32 NPZ file is a mean-pooled derived feature archive "
                "from the historical run, not weights or a trained head. Only "
                "its file digest is pinned; its arrays are not read or "
                "scored."),
            "why_not_reproduced": [
                "Upstream weight files are absent.",
                "The Python 3.10.13/torch 2.2.2/transformers 4.40.2 runtime "
                "with scikit-learn is absent.",
                "No serialized ridge-head artifact or fold index exists.",
                "AMI audio, annotations and CMUdict terms are not reviewed "
                "for this package.",
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
            "home_probes": home_probes,
            "summary": absence_summary(workspace_probes, home_probes),
        },
        "admission": build_admission(),
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
    head = contract.get("exact_head", {})
    if head.get("artifact_present") is not False \
            or head.get("serialized") is not False \
            or head.get("trained_in_fold_only") is not True:
        raise ValueError("contract_head_flags")
