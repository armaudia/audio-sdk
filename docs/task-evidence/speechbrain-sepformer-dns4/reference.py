# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-SPEECHBRAIN-SEPFORMER-DNS4.

Standard-library only and deterministic. This module contains no PyTorch,
torchaudio, SpeechBrain, HyperPyYAML, checkpoint, model weight, config,
hyperparams file, corpus, audio signal or model output. It pins the existing
project research/evaluation sources and SDK boundaries by SHA-256, records that
the exact six-file checkpoint revision and the exact runtime are absent, probes
a fixed path inventory for absence, exercises a synthetic enhancement
*envelope* (identity and bounded unit-peak variants only), re-computes the
recorded per-item provenance aggregates with exact decimal arithmetic, validates
a caller-supplied enhancement-run manifest with a fail-closed admission
boundary, and builds the canonical report.

The recorded SepFormer DNS4 screen is provenance only. Nothing here reproduces
it, and no result qualifies the component.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import struct
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

TASK = "SDK-SPEECHBRAIN-SEPFORMER-DNS4"
COMPONENT_ID = "speechbrain-sepformer-dns4"
TASK_TITLE = "SpeechBrain SepFormer DNS4"
CONTRACT_ID = "audio-sdk/speechbrain-sepformer-dns4-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = (
    "audio-sdk/speechbrain-sepformer-dns4-enhancement-run/0.1")
ENVELOPE_SCHEMA_ID = "audio-sdk/speechbrain-sepformer-dns4-envelope/0.1"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
MODE = "implementation"
BASE_COMMIT = "acefdd1df870fd19f990eba92fd15bf38f171f75"
BRANCH = "swarm/SDK-SPEECHBRAIN-SEPFORMER-DNS4"
WRITE_SCOPE = "docs/task-evidence/speechbrain-sepformer-dns4/ only"
TASK_PREFIX = "docs/task-evidence/speechbrain-sepformer-dns4/"
DISPOSITION = (
    "DEFER: caller-supplied-asset reference. The exact pinned checkpoint "
    "revision, runtime and rights-cleared corpus are absent; the package is an "
    "explicit blocker with no qualifying result."
)

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FRAME_BYTES = FRAME_SAMPLES * 4
PROTOCOL_ID = "audioml-enhancer/1"
ENVELOPE_VARIANTS = ("identity", "unit_peak")
RUN_MODES = ("offline",)

MODEL_ID = "speechbrain/sepformer-dns4-16k-enhancement"
MODEL_REVISION = "e8c258546300102a240fa2595854d473cbfee49a"
MODEL_LICENSE = "Apache-2.0"
MODEL_CARD_DNS4_2022 = {
    "sig": "2.999",
    "bak": "3.076",
    "ovrl": "2.437",
    "source": "upstream_model_card_claim_not_a_local_score",
}
CHECKPOINT_FILES = {
    "brain.ckpt":
        "33809a026a2c1febce7b03c8aafaee4ddfc851b2c70f180f8c06bf1017f4df5c",
    "encoder.ckpt":
        "33de46bbf0b55031f92346827723137478cf2f77204fd1360ba8833b5915e0ee",
    "masknet.ckpt":
        "cfba4276bf051fc48b1d49350ef0612845328c1999cefb4c637fc02cdbabbbdd",
    "decoder.ckpt":
        "ab10ab1aac337bbe77ad0cbdf75acb1fba952e2d34474d515de2f41ddfd9a24c",
    "config.json":
        "2aa99b583295cfdbf0d3409bc78186ad1b136d84490711ea586bb149d9ecdfe2",
    "hyperparams.yaml":
        "c69879126990b54562499f61d0264213b8bc4f0b0b4f750e55d4d13ca544db3f",
}
CHECKPOINT_BYTE_COUNTS_RECORDED = False
CHECKPOINT_TOTAL_BYTES_RECORDED = None
HUB_REPOSITORY_REPORTED_BYTES = 113_000_000
HUB_REPORTED_SIZE_IS_EXACT = False

SPEECHBRAIN_WHEEL_SHA256 = (
    "9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9")

REQUIRED_INTERPRETER = "3.12.16"
RECORDED_RUNTIME = {
    "python": "3.11.5",
    "torch": "2.14.1",
    "torchaudio": "2.11.0",
    "speechbrain": "1.0.3",
    "hyperpyyaml": "1.2.3",
    "device": "cpu",
    "intra_op_threads": 4,
    "interop_op_threads": None,
    "deterministic_algorithms": None,
    "offline": True,
    "mps_available": False,
    "cuda_available": False,
    "npu_available": False,
    "wheel_digests_recorded": False,
}
RUNTIME_OVERLAY = (
    ("speechbrain", "1.0.3"),
    ("hyperpyyaml", "1.2.3"),
    ("sentencepiece", "0.2.2"),
    ("PyYAML", "6.0.3"),
    ("ruamel.yaml", "0.18.17"),
    ("ruamel.yaml.clib", "0.2.15"),
    ("torch", "2.14.1"),
    ("torchaudio", "2.11.0"),
    ("huggingface_hub", "2.3.0"),
    ("numpy", "1.26.4"),
    ("scipy", "1.17.1"),
    ("soundfile", "0.12.1"),
)
RUNTIME_MODULES = ("torch", "torchaudio", "speechbrain", "hyperpyyaml")
REFERENCE_EXECUTION_POLICY = {
    "python": "3.11.5",
    "torch": "2.14.1",
    "torchaudio": "2.11.0",
    "speechbrain": "1.0.3",
    "hyperpyyaml": "1.2.3",
    "device": "cpu",
    "intra_op_threads": 1,
    "interop_op_threads": 1,
    "deterministic_algorithms": True,
    "offline": True,
    "mode": "offline",
    "streaming_supported": False,
    "reference_policy_is_not_a_recorded_run": True,
}

PROTOCOL_RECORDED = {
    "id": "CLN-01-exploratory",
    "pair_count": 30,
    "item_seconds": "10.0",
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_count_per_item": 160000,
    "total_seconds": "300.0",
    "total_samples": 4800000,
    "expected_sample_ids": (
        0, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17, 19, 20, 21, 23, 26, 33,
        34, 35, 37, 38, 42, 43, 44, 45, 47, 48, 49, 50,
    ),
    "noisy_manifest_sha256":
        "d6a1de74f028d3bb435422b6f386b59a96127d2fc4493c101d307ba811518175",
    "clean_manifest_sha256":
        "d016c7140d79cfe5c51ffe614c4d7ee56be4298f9a986a622ed6a7f73a1e6b21",
    "manifests_present_here": False,
    "outputs_present_here": False,
}

CONTROL_KINDS = (
    "identity_noisy",
    "task_matched_baseline",
    "clean_preservation",
    "adverse_missing",
    "nonfinite_rejection",
)

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
    "research/voice-enhancement-20261101/README.md":
        "1c138af71f5f1667cd98335b4650b1ee6d248d72c8c0a4481f361829c2353640",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md":
        "b7a1e214d0fa402c971e39a4742d54589ce5bd25bd3de4a5bc72be843ec997f4",
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.py":
        "9e85412481780ad9b917428bc36d5cf407cfe9c0842a96de8953706041ad3327",
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.json":
        "b6135146118e303ff335a4418a8906234c9b85d9031836d96b27a524ab0871e5",
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.lock.json":
        "631685078d2218cb0bdd656be622e6953679e1c51c1662d6a858cf214451aac1",
    "research/voice-enhancement-20261101/agent-sepformer-eval/run_sepformer.py":
        "7e19d5c205c373256d0d9fbf913b095065ddbc527e7cdb4428f720394b98302f",
    "research/voice-enhancement-20261101/agent-sepformer-eval/sepformer_results.json":
        "3ca2cf232704d1c48dd048187f17810eaecdc3b5bee8966a2660878e26162416",
    "research/voice-enhancement-20261101/agent-sepformer-eval/"
    "sepformer_clean_results.json":
        "c0d53803de6aed95f67e53c41efb7fa53f4c7de89071106ee0cf18c06bd316c9",
    "research/voice-enhancement-20261101/agent-sepformer-eval/"
    "sepformer_rms_matched.json":
        "9a3b593150e365dc34c08382c62f4e994dffd14c3580325bb9b0b83510ddc76f",
    "research/voice-enhancement-20261101/agent-metricgan-eval/requirements.lock":
        "22b5283ab4f920dc16017d545552a46d2706cbade14e1cfa1209f28c255ddc20",
    "research/voice-enhancement-20261101/agent-sepformer-readiness/REPORT.md":
        "1ff9c12cf3b4120d0ac7424ab2718f8a3ec2dc067c1e1564a0aaafc026a339d7",
    "research/voice-enhancement-20261101/agent-sepformer-result-audit/REPORT.md":
        "dca9253460fb95c6085433e0508504cc9c7b8e7db15676af85e7008e74260177",
    "scripts/evaluate_noise_suppression.py":
        "761f0519829cbdf7680f9c7bc780bbaaff2d231c45c23a2c6306d47c8f4eb0de",
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
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/metricgan-speechbrain-voicebank/README.md":
        "0ce5593cda4ed6412d755ecd013c4ef65f3e1c50c4f264a1abb4782b57990f22",
    "docs/task-evidence/metricgan-speechbrain-voicebank/report.json":
        "8f04d6f06cea71f6497277131d3b4adcb7b5381c5fc25b4fa646fe91476935e2",
    "docs/task-evidence/pytorch-and-speechbrain-adapters/report.json":
        "7754c9647064f89c7d831fd9bd7d3a9f3560c51c00a22bfc8dc9da3aa59e349c",
    "docs/task-evidence/mobilenetv3-small-on-log-mels/report.json":
        "2f179b4b49afcf9fd866e0a6339f0ede60a85192d04ba5d2629984b3d6828f50",
    "docs/task-evidence/small-log-mel-gru/report.json":
        "619a4bf03655c3d49afd666ee8eaabaef3e452c98dfab1c36202d6ae44d7091c",
    "docs/task-evidence/gtcrn-dns3-offline/report.json":
        "b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

MANIFEST_FIELDS = ("schema_id", "run_id", "model", "runtime", "assets",
                   "corpus", "outputs", "metrics", "controls", "rights")
MODEL_FIELDS = ("identity", "revision", "license", "license_review_sha256",
                "mode", "streaming_supported")
RUNTIME_FIELDS = ("python", "torch", "torchaudio", "speechbrain",
                  "hyperpyyaml", "device", "intra_op_threads",
                  "interop_op_threads", "deterministic_algorithms", "offline",
                  "install_reference", "wheel_digests")
ASSET_FIELDS = ("asset_id", "name", "byte_count", "sha256", "terms_sha256",
                "present_at_review")
CORPUS_FIELDS = ("cohort_id", "pair_count", "sample_rate_hz", "channels",
                 "sample_count_per_item", "items_sha256",
                 "noisy_manifest_sha256", "clean_manifest_sha256",
                 "clean_reference", "terms_sha256")
OUTPUT_FIELDS = ("row_count", "items_sha256", "finite", "length_preserving",
                 "peak_max", "raw_peak_max", "delay_compensation_samples",
                 "normalization")
METRICS_FIELDS = ("protocol", "pair_count", "si_sdr_delta_db_mean",
                  "stoi_delta_mean", "clean_stoi_mean", "baseline_count",
                  "bootstrap_replicates", "nonfinite_count",
                  "invalid_output_count", "scorer_sha256")
CONTROL_FIELDS = ("id", "kind")
RIGHTS_FIELDS = ("weight_terms", "runtime_terms", "training_data_terms",
                 "data_terms", "output_use", "review_reference",
                 "claims_qualified")

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX64 = re.compile(r"^(?=.*[1-9a-f])[0-9a-f]{64}$")
DECIMAL = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$")
OUTPUT_NORMALIZATION = "per_utterance_peak_divide_by_max_abs"

PROFILE_PHRASES = (
    "Run identity/noisy control and an established task-matched baseline",
    "Score paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "separately labeled predictive screen or authorized listening",
    "Report alignment, state, memory and measured content/availability timing",
)

ENHANCEMENT_REQUIREMENTS = (
    {
        "id": "ENH-01",
        "requirement": "identity/noisy control",
        "status": "blocked",
        "evidence": "none",
        "reason": "No caller-supplied pair or reproduced output exists; the "
                  "synthetic envelope is protocol plumbing, not an identity "
                  "control over audio.",
        "reopen_condition": "Run a digest-pinned noisy identity control on the "
                            "cleared corpus with the exact runtime.",
    },
    {
        "id": "ENH-02",
        "requirement": "established task-matched baseline",
        "status": "blocked",
        "evidence": "recorded comparator names only",
        "reason": "DeepFilterNet3, FastEnhancer Small and ClearVoice FRCRN "
                  "are recorded provenance; no comparator runtime, asset or "
                  "matched rerun is present.",
        "reopen_condition": "Install rights-cleared pinned comparators and "
                            "rerun both sides on the same frozen inputs.",
    },
    {
        "id": "ENH-03",
        "requirement": "paired SI-SDR and STOI",
        "status": "blocked",
        "evidence": "recorded per-item rows only",
        "reason": "No reproduced metric exists here; recorded aggregates are "
                  "checked for arithmetic consistency only.",
        "reopen_condition": "Score reproduced candidate and control outputs "
                            "with a frozen permitted scorer.",
    },
    {
        "id": "ENH-04",
        "requirement": "clean-speech preservation",
        "status": "blocked",
        "evidence": "none",
        "reason": "The 30-item clean diagnostic is provenance only; no clean "
                  "reference, reproduced output or preservation metric is "
                  "present.",
        "reopen_condition": "Measure preservation on permitted clean speech "
                            "with a declared statistic.",
    },
    {
        "id": "ENH-05",
        "requirement": "peaks and invalid outputs",
        "status": "blocked",
        "evidence": "synthetic envelope peak bounds only",
        "reason": "No real output was produced; nonfinite, clipping, length "
                  "and gain-policy behavior are unmeasured for the model.",
        "reopen_condition": "Record per-item peaks, invalid counts, length and "
                            "the gain policy on reproduced outputs.",
    },
    {
        "id": "ENH-06",
        "requirement": "unpaired predictive screen or authorized listening",
        "status": "blocked",
        "evidence": "none",
        "reason": "No unpaired real speech, predictive scorer result or "
                  "authorized listening protocol exists.",
        "reopen_condition": "Run a separately labeled predictive screen on "
                            "permitted data or authorized listening.",
    },
    {
        "id": "ENH-07",
        "requirement": "alignment and state",
        "status": "blocked",
        "evidence": "declared whole-utterance behavior only",
        "reason": "SepFormer is a whole-utterance non-causal model with no "
                  "streaming state; content delay is not measured.",
        "reopen_condition": "Measure impulse/speech alignment and declared "
                            "state for the exact runtime.",
    },
    {
        "id": "ENH-08",
        "requirement": "memory and measured content/availability timing",
        "status": "blocked",
        "evidence": "recorded shared-host provenance only",
        "reason": "No per-call CPU, peak RSS, first-output delay, availability "
                  "deadline or target-device measurement was made here.",
        "reopen_condition": "Measure resources and availability on the "
                            "declared target with the exact checkpoint.",
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "name": "source revision and license/notice provenance",
        "status": "blocked",
        "blocked_by": "The six pinned model files and the complete "
                      "license/notice/model-card bundle are absent; the "
                      "Apache-2.0 card line is not an artifact-specific "
                      "clearance or training-data review.",
        "reopen_condition": "Stage the exact revision with a complete "
                            "license/notice/model-card and training-data "
                            "review recorded by an independent reviewer.",
    },
    {
        "id": "RG-02",
        "name": "checkpoint files and per-file digests",
        "status": "blocked",
        "blocked_by": "brain.ckpt, encoder.ckpt, masknet.ckpt, decoder.ckpt, "
                      "config.json and hyperparams.yaml are absent; the lock "
                      "records SHA-256 only and no byte counts.",
        "reopen_condition": "Stage all six files, verify every SHA-256 and "
                            "newly record every byte count.",
    },
    {
        "id": "RG-03",
        "name": "pinned offline runtime",
        "status": "blocked",
        "blocked_by": "CPython 3.11.5 with torch 2.14.1, torchaudio 2.11.0, "
                      "SpeechBrain 1.0.3 and the recorded overlay is absent; "
                      "no wheel digest, install location or import digest "
                      "exists.",
        "reopen_condition": "Provide the locked offline environment with "
                            "wheel digests, install location, deterministic "
                            "algorithms and a clean-room import/load digest.",
    },
    {
        "id": "RG-04",
        "name": "rights-cleared corpus",
        "status": "blocked",
        "blocked_by": "No noisy/clean pair, manifest payload or output file is "
                      "present; corpus, evaluation, derived-output and "
                      "redistribution terms are unreviewed.",
        "reopen_condition": "Freeze a digest-pinned permitted corpus with "
                            "reviewed rights and attribution.",
    },
    {
        "id": "RG-05",
        "name": "reproduced deterministic inference",
        "status": "blocked",
        "blocked_by": "No checkpoint was loaded and no output was produced; "
                      "finite, length-preserving, peak and three-repeat "
                      "behavior are unverified.",
        "reopen_condition": "Run the exact runtime offline on the cleared "
                            "corpus and record per-item output digests and "
                            "finite/length/peak checks.",
    },
    {
        "id": "RG-06",
        "name": "Enhancement-profile metrics and controls",
        "status": "blocked",
        "blocked_by": "No paired SI-SDR/STOI, baseline, clean-preservation or "
                      "adverse/missing/nonfinite control result was produced.",
        "reopen_condition": "Score reproduced candidate and control outputs "
                            "with a frozen permitted scorer and declared "
                            "coverage and margins.",
    },
    {
        "id": "RG-07",
        "name": "listening, alignment, memory and timing",
        "status": "blocked",
        "blocked_by": "No unpaired predictive screen, authorized listening, "
                      "alignment, state, memory, availability or target-device "
                      "measurement exists.",
        "reopen_condition": "Measure alignment, state, memory, availability "
                            "and device timing separately, and run authorized "
                            "listening if claimed.",
    },
    {
        "id": "RG-08",
        "name": "provider intake, public surface and release",
        "status": "blocked",
        "blocked_by": "No OFF-by-default provider intake, descriptor, "
                      "registration, public-surface change or independent "
                      "exact-head review exists.",
        "reopen_condition": "Open a separate versioned OFF-by-default intake "
                            "after all prior gates clear and complete "
                            "independent exact-head review.",
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "name": "pinned project research and evidence sources",
        "present": True,
        "verified": True,
        "blocked": False,
        "sha256": None,
        "scope": "source pins listed in SOURCES.sha256",
    },
    {
        "id": "ART-02",
        "name": "SepFormer DNS4 six-file checkpoint revision",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": MODEL_REVISION,
    },
    {
        "id": "ART-03",
        "name": "locked offline PyTorch/SpeechBrain runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": "CPython 3.11.5 + torch 2.14.1 + SpeechBrain 1.0.3",
    },
    {
        "id": "ART-04",
        "name": "rights-cleared paired DNS corpus and manifests",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": "30-pair CLN-01-exploratory or a reviewed replacement",
    },
    {
        "id": "ART-05",
        "name": "reproduced per-item enhancement outputs",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": "finite, length-preserving, digest-pinned outputs",
    },
    {
        "id": "ART-06",
        "name": "qualification scorer, baselines and adverse controls",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": "frozen SI-SDR/STOI scorer plus identity and comparators",
    },
    {
        "id": "ART-07",
        "name": "alignment, listening and target-device evidence",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": "separately labeled listening and timing evidence",
    },
    {
        "id": "ART-08",
        "name": "OFF-by-default provider intake and exact-head review",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "scope": "separate intake after all prior gates",
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01", "RG-02"],
        "missing": "The six files at revision e8c258546300102a240fa2595854d473"
                   "cbfee49a with recorded SHA-256 values and byte counts.",
        "required_action": "Stage brain.ckpt, encoder.ckpt, masknet.ckpt, "
                           "decoder.ckpt, config.json and hyperparams.yaml; "
                           "verify each digest; record each byte count; add a "
                           "reviewed license/notice/model-card and "
                           "training-data decision.",
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-03"],
        "missing": "A locked offline CPython 3.11.5 environment with torch "
                   "2.14.1, torchaudio 2.11.0, SpeechBrain 1.0.3, HyperPyYAML "
                   "1.2.3 and the recorded overlay.",
        "required_action": "Record wheel names/versions/byte counts/SHA-256, "
                           "install location, one intra-op and one inter-op "
                           "thread, deterministic algorithms, offline mode and "
                           "a clean-room import plus checkpoint-load digest.",
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-04"],
        "missing": "A rights-cleared 30-pair noisy/clean corpus with frozen "
                   "manifests and per-item input digests.",
        "required_action": "Freeze permitted audio, record corpus/acquisition,"
                           " evaluation, derived-output and redistribution "
                           "terms, attribution and noisy/clean digests.",
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-05"],
        "missing": "Reproduced offline per-item outputs from the exact "
                   "checkpoint and runtime.",
        "required_action": "Run offline with network and downloads denied; "
                           "record per-item output digests, finite and "
                           "length-preserving checks, peaks, the gain policy "
                           "and three byte-identical repeats.",
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-06"],
        "missing": "A frozen permitted scorer with identity/noisy and "
                   "task-matched baseline controls and clean-preservation "
                   "metrics.",
        "required_action": "Declare coverage, metric margins, pairing and "
                           "bootstrap protocol; score candidate and controls "
                           "on the same frozen item IDs; include missing, "
                           "adverse and nonfinite rejection cases.",
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-07"],
        "missing": "Unpaired predictive screen or authorized listening and "
                   "measured alignment, state, memory, availability and "
                   "target-device timing.",
        "required_action": "Label each evidence class separately; measure "
                           "whole-utterance content delay, per-call CPU, peak "
                           "RSS and availability on the declared target; do "
                           "not infer streaming support.",
    },
    {
        "id": "BLK-07",
        "artifact_id": "ART-08",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-08"],
        "missing": "An OFF-by-default provider intake and independent "
                   "exact-head review.",
        "required_action": "Open a separate versioned intake after all prior "
                           "gates clear; prove clean installability with media "
                           "and weights absent; do not touch the shared "
                           "registry, defaults, ABI, build or CI in this task.",
    },
)

NON_CLAIMS = (
    "No checkpoint file, model weight, config or hyperparams file is "
    "present, downloaded, loaded or executed.",
    "No PyTorch, torchaudio, SpeechBrain or HyperPyYAML module is imported or "
    "installed.",
    "No audio signal, corpus payload, manifest or output WAV is read or "
    "written.",
    "No SepFormer inference, separation, enhancement or scoring run is "
    "performed.",
    "Recorded per-item rows are checked for arithmetic consistency only; that "
    "is provenance, not a reproduced result.",
    "The synthetic envelope is protocol plumbing with no audio, model, "
    "quality, timing or release meaning.",
    "No listening, device-timing, benchmark, pipeline or release claim is "
    "made.",
    "No provider, descriptor, registry, default, public ABI, shared build or "
    "CI change exists.",
    "The upstream DNS4 2022 DNSMOS values are source-reported and are not "
    "local scores.",
    "Whole-utterance processing is not streaming and no content delay, state "
    "or availability result is inferred.",
)

REQUIRED_RESULTS = (
    "Exact six-file checkpoint bytes with verified SHA-256 and recorded byte "
    "counts.",
    "Locked offline runtime with wheel digests and clean-room import/load "
    "digest.",
    "Rights-cleared paired corpus and clean diagnostics with file digests.",
    "Reproduced per-item outputs with finite, length and peak checks.",
    "Paired SI-SDR/STOI against identity and task-matched baselines.",
    "Clean-speech preservation, peaks and invalid-output results.",
    "Separately labeled unpaired screen or authorized listening result.",
    "Measured alignment, state, memory and content/availability timing.",
    "A separate OFF-by-default provider intake after the prior results.",
)

REOPENING_CONDITIONS = (
    "Stage the exact e8c258546300102a240fa2595854d473cbfee49a six-file "
    "revision and record byte counts, SHA-256 and reviewed terms.",
    "Provide the locked offline CPython 3.11.5 / torch 2.14.1 / SpeechBrain "
    "1.0.3 runtime with wheel digests and deterministic one-thread policy.",
    "Freeze a rights-cleared paired corpus with noisy/clean digests and "
    "output-use decisions.",
    "Reproduce per-item inference offline with three byte-identical repeats.",
    "Apply the Enhancement profile with identity/baseline controls, paired "
    "SI-SDR/STOI, clean preservation, peaks and adverse controls.",
    "Measure alignment, memory, availability and target-device timing and run "
    "authorized listening only if claimed.",
    "Open a separate OFF-by-default provider intake with independent "
    "exact-head review.",
)

ABSENCE_PROBES = (
    "data/models/speechbrain-sepformer",
    "data/models/speechbrain-sepformer/brain.ckpt",
    "data/models/speechbrain-sepformer/encoder.ckpt",
    "data/models/speechbrain-sepformer/masknet.ckpt",
    "data/models/speechbrain-sepformer/decoder.ckpt",
    "data/envs/clearvoice",
    "data/envs/metricgan-speechbrain",
    "data/runs/noise-suppression-20261101-sepformer",
    "research/voice-enhancement-20261101/agent-sepformer-eval/outputs",
    "research/voice-enhancement-20261101/agent-sepformer-eval/sepformer_outputs",
    "adapters/sepformer",
    "adapters/speechbrain",
)
WORKTREE_ABSENCE_PROBES = (
    "docs/task-evidence/speechbrain-sepformer-dns4/brain.ckpt",
    "api/include/audio_sdk/provider_speechbrain_sepformer_dns4.h",
    "core/provider_speechbrain_sepformer_dns4.c",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--speechbrain--sepformer-dns4-16k-enhancement",
    "~/.cache/torch/hub/checkpoints",
    "~/.cache/speechbrain",
    "~/Library/Caches/huggingface/hub/models--speechbrain--sepformer-dns4-16k-enhancement",
)

HISTORICAL_RUN = {
    "candidate": "SpeechBrain SepFormer DNS4 (sepformer-dns4-16k-enhancement)",
    "revision": MODEL_REVISION,
    "scope": "exploratory 30-pair DNS2020 no-reverb subset plus 30 clean "
             "diagnostics; shared Apple M1 CPU host",
    "protocol": PROTOCOL_RECORDED["id"],
    "valid_outputs": "30/30",
    "mean_delta_snr_db": "-19.431604",
    "mean_delta_si_sdr_db": "8.525086",
    "mean_delta_stoi": "0.033132",
    "mean_rtf": "0.692796",
    "median_rtf": "0.661214",
    "p95_rtf": "0.819204",
    "max_rtf": "0.828810",
    "noisy_peak_child_rss_bytes": 1894531072,
    "clean_peak_child_rss_bytes": 1970847744,
    "noisy_worker_wall_seconds": "228.032528",
    "clean_worker_wall_seconds": "225.534259",
    "intra_op_threads": 4,
    "device": "cpu",
    "streaming_supported": False,
    "listening_result": False,
    "device_timing_result": False,
    "benchmark_result": False,
    "provenance_only": True,
    "reproduced_here": False,
    "used_for_evidence": False,
    "qualifies": False,
}


class AdmissionError(ValueError):
    """A fail-closed task-local admission or envelope rejection."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


# --------------------------------------------------------------------------
# Strict JSON, canonical serialization and digests
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


def _quantize(value: Decimal | str | float, places: int = 6) -> str:
    decimal = value if isinstance(value, Decimal) else Decimal(repr(value))
    exponent = Decimal(1).scaleb(-places)
    return str(decimal.quantize(exponent))


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


def absence_probes(audio_root: Path,
                   probes: tuple[str, ...] = ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    for relative in probes:
        path = Path(audio_root) / relative
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": False, "present": False})
    return rows


def worktree_absence_probes(
        probes: tuple[str, ...] = WORKTREE_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    for relative in probes:
        path = WORKTREE / relative
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": False,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def home_absence_probes(
        probes: tuple[str, ...] = HOME_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    home = Path.home()
    for relative in probes:
        path = home / relative[2:] if relative.startswith("~/") else Path(
            relative)
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_home_cache": True,
                     "present": False})
    return rows


def absence_summary(workspace_rows: list[dict],
                    worktree_rows: list[dict],
                    home_rows: list[dict]) -> dict:
    all_rows = workspace_rows + worktree_rows + home_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(workspace_rows),
        "worktree_probe_count": len(worktree_rows),
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


# --------------------------------------------------------------------------
# Runtime readiness and source presence
# --------------------------------------------------------------------------
def _module_spec(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def runtime_readiness() -> dict:
    found = [name for name in RUNTIME_MODULES if _module_spec(name)]
    blocked = not found
    missing = [name for name in RUNTIME_MODULES if name not in found]
    return {
        "required_interpreter": REQUIRED_INTERPRETER,
        "observed_interpreter": platform.python_version(),
        "interpreter_matches": platform.python_version() == REQUIRED_INTERPRETER,
        "recorded_python": RECORDED_RUNTIME["python"],
        "recorded_torch": RECORDED_RUNTIME["torch"],
        "recorded_torchaudio": RECORDED_RUNTIME["torchaudio"],
        "recorded_speechbrain": RECORDED_RUNTIME["speechbrain"],
        "recorded_hyperpyyaml": RECORDED_RUNTIME["hyperpyyaml"],
        "required_modules": list(RUNTIME_MODULES),
        "found_modules": found,
        "missing_modules": missing,
        "module_spec_found": bool(found),
        "importable": False,
        "blocked": blocked,
        "exact_error": ("ModuleNotFoundError: No module named 'torch'"
                        if "torch" in missing else "runtime_matrix_incomplete"),
        "install_location_recorded": False,
        "wheel_digests_recorded": False,
        "runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "network_used": False,
    }


def source_presence() -> dict:
    required_sources = (
        "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md",
        "research/voice-enhancement-20261101/agent-sepformer-eval/"
        "adapter.lock.json",
        "research/voice-enhancement-20261101/agent-sepformer-eval/"
        "sepformer_results.json",
        "research/voice-enhancement-20261101/agent-sepformer-eval/"
        "sepformer_clean_results.json",
        "research/voice-enhancement-20261101/agent-sepformer-eval/"
        "sepformer_rms_matched.json",
        "research/voice-enhancement-20261101/agent-sepformer-readiness/"
        "REPORT.md",
        "research/voice-enhancement-20261101/agent-sepformer-result-audit/"
        "REPORT.md",
    )
    reports_present = all((AUDIO_ROOT / relative).is_file()
                          for relative in required_sources)
    lock_present = (
        AUDIO_ROOT /
        "research/voice-enhancement-20261101/agent-sepformer-eval/"
        "adapter.lock.json").is_file()
    weights_dir = AUDIO_ROOT / "data/models/speechbrain-sepformer"
    weights_present = weights_dir.is_dir() and any(
        weights_dir.glob("*.ckpt"))
    corpus_present = (
        (AUDIO_ROOT / "data/runs/noise-suppression-20261101-sepformer").is_dir()
        or (AUDIO_ROOT /
            "research/voice-enhancement-20261101/agent-sepformer-eval/"
            "outputs").is_dir())
    return {
        "research_reports_present": reports_present,
        "checkpoint_lock_present": lock_present,
        "recorded_result_rows_present": all(
            (AUDIO_ROOT / relative).is_file()
            for relative in (
                "research/voice-enhancement-20261101/agent-sepformer-eval/"
                "sepformer_results.json",
                "research/voice-enhancement-20261101/agent-sepformer-eval/"
                "sepformer_clean_results.json",
                "research/voice-enhancement-20261101/agent-sepformer-eval/"
                "sepformer_rms_matched.json",
            )),
        "scorer_source_present": (
            AUDIO_ROOT / "scripts/evaluate_noise_suppression.py").is_file(),
        "runtime_present": False,
        "weights_present": weights_present,
        "corpus_present": corpus_present,
        "outputs_present": corpus_present,
        "exact_source_runtime_weights_conjunction_present": False,
        "runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "network_used": False,
        "download_attempted": False,
    }


# --------------------------------------------------------------------------
# Recorded provenance arithmetic (exact decimal, no model execution)
# --------------------------------------------------------------------------
def _read_recorded(name: str) -> dict:
    return read_strict_json(
        AUDIO_ROOT / "research/voice-enhancement-20261101/"
        "agent-sepformer-eval" / name)


def _dec(value: Any) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError("recorded_non_decimal")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, str):
        return Decimal(value)
    return Decimal(repr(value))


def _mean(values: list[Decimal]) -> Decimal:
    return sum(values, Decimal(0)) / Decimal(len(values))


def _median(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    count = len(ordered)
    if count % 2:
        return ordered[count // 2]
    return (ordered[count // 2 - 1] + ordered[count // 2]) / 2


def _percentile95(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    index = (Decimal(len(ordered)) - 1) * Decimal("0.95")
    low = int(index)
    high = math.ceil(index)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (
        index - Decimal(low))


def _agrees(observed: Any, expected: Any, places: int = 6) -> bool:
    return _quantize(_dec(observed), places) == _quantize(_dec(expected),
                                                          places)


def _row_stats(rows: list[dict], field: str) -> dict:
    values = [_dec(row[field]) for row in rows if row.get(field) is not None]
    if not values:
        raise ValueError("recorded_field_missing:" + field)
    return {
        "count": len(values),
        "mean": _mean(values),
        "median": _median(values),
        "p95": _percentile95(values),
        "max": max(values),
        "min": min(values),
    }


def _stats_strings(stats: dict) -> dict:
    return {
        "count": stats["count"],
        "mean": _quantize(stats["mean"]),
        "median": _quantize(stats["median"]),
        "p95": _quantize(stats["p95"]),
        "max": _quantize(stats["max"]),
        "min": _quantize(stats["min"]),
    }


def recorded_provenance() -> dict:
    """Recompute aggregates from recorded rows; never runs a model."""
    noisy = _read_recorded("sepformer_results.json")
    clean = _read_recorded("sepformer_clean_results.json")
    matched = _read_recorded("sepformer_rms_matched.json")
    noisy_rows = noisy["rows"]
    clean_rows = clean["rows"]
    matched_rows = matched["rows"]
    expected_ids = set(PROTOCOL_RECORDED["expected_sample_ids"])

    ids = [row["sample_id"] for row in noisy_rows]
    clean_ids = [row["sample_id"] for row in clean_rows]
    matched_ids = [row["sample_id"] for row in matched_rows]
    identity = {
        "row_count": len(noisy_rows),
        "clean_row_count": len(clean_rows),
        "rms_matched_row_count": len(matched_rows),
        "expected_pair_count": PROTOCOL_RECORDED["pair_count"],
        "ids_match_recorded_set": (len(ids) == len(set(ids))
                                   and set(ids) == expected_ids),
        "clean_ids_match_recorded_set": (len(clean_ids) == len(set(clean_ids))
                                         and set(clean_ids) == expected_ids),
        "matched_ids_match_recorded_set": (
            len(matched_ids) == len(set(matched_ids))
            and set(matched_ids) == expected_ids),
        "unique_output_hashes": len({row["output_sha256"]
                                     for row in noisy_rows}),
        "all_rows_ten_seconds": all(
            _dec(row["duration_seconds"]) == Decimal(10)
            for row in noisy_rows),
        "all_normalized_peak_unit": all(
            _dec(row["output_peak"]) == Decimal(1) for row in noisy_rows),
        "candidate": noisy.get("candidate"),
        "revision": noisy.get("revision"),
    }

    noisy_stats = {
        field: _row_stats(noisy_rows, field)
        for field in ("snr_db", "si_sdr_db", "stoi", "snr_improvement_db",
                      "inference_seconds", "adapter_rtf")
    }
    clean_stats = {
        field: _row_stats(clean_rows, field)
        for field in ("si_sdr_db", "stoi", "snr_db", "adapter_rtf")
    }
    matched_stats = {
        field: _row_stats(matched_rows, field)
        for field in ("snr_improvement_db", "si_sdr_db", "stoi",
                      "postprocess_seconds", "output_peak")
    }
    rtf_deviations = [
        abs(_dec(row["adapter_rtf"]) -
            _dec(row["inference_seconds"]) / _dec(row["duration_seconds"]))
        for row in noisy_rows
    ]
    rtf_definition_consistent = max(rtf_deviations) <= Decimal("1e-12")
    clean_rtf_deviations = [
        abs(_dec(row["adapter_rtf"]) -
            _dec(row["inference_seconds"]) / _dec(row["duration_seconds"]))
        for row in clean_rows
    ]
    clean_rtf_definition_consistent = (
        max(clean_rtf_deviations) <= Decimal("1e-12"))

    wins = sum(1 for row in noisy_rows
               if _dec(row["snr_improvement_db"]) > 0)
    losses = sum(1 for row in noisy_rows
                 if _dec(row["snr_improvement_db"]) < 0)
    ties = len(noisy_rows) - wins - losses

    recomputed = {
        "noisy": {
            "n": len(noisy_rows),
            "snr_db_mean": _quantize(noisy_stats["snr_db"]["mean"]),
            "si_sdr_db_mean": _quantize(noisy_stats["si_sdr_db"]["mean"]),
            "stoi_mean": _quantize(noisy_stats["stoi"]["mean"]),
            "snr_improvement_db_mean": _quantize(
                noisy_stats["snr_improvement_db"]["mean"]),
            "inference_seconds_mean": _quantize(
                noisy_stats["inference_seconds"]["mean"]),
            "inference_seconds_median": _quantize(
                noisy_stats["inference_seconds"]["median"]),
            "inference_seconds_p95": _quantize(
                noisy_stats["inference_seconds"]["p95"]),
            "inference_seconds_max": _quantize(
                noisy_stats["inference_seconds"]["max"]),
            "rtf_mean": _quantize(noisy_stats["adapter_rtf"]["mean"]),
            "rtf_median": _quantize(noisy_stats["adapter_rtf"]["median"]),
            "rtf_p95": _quantize(noisy_stats["adapter_rtf"]["p95"]),
            "rtf_max": _quantize(noisy_stats["adapter_rtf"]["max"]),
            "snr_improvement_wins": wins,
            "snr_improvement_ties": ties,
            "snr_improvement_losses": losses,
        },
        "clean": {
            "n": len(clean_rows),
            "snr_db_mean": _quantize(clean_stats["snr_db"]["mean"]),
            "si_sdr_db_mean": _quantize(clean_stats["si_sdr_db"]["mean"]),
            "stoi_mean": _quantize(clean_stats["stoi"]["mean"]),
            "rtf_mean": _quantize(clean_stats["adapter_rtf"]["mean"]),
        },
        "rms_matched": {
            "n": len(matched_rows),
            "snr_improvement_db_mean": _quantize(
                matched_stats["snr_improvement_db"]["mean"]),
            "si_sdr_db_mean": _quantize(matched_stats["si_sdr_db"]["mean"]),
            "stoi_mean": _quantize(matched_stats["stoi"]["mean"]),
            "postprocess_seconds_mean": _quantize(
                matched_stats["postprocess_seconds"]["mean"]),
            "output_peak_mean": _quantize(matched_stats["output_peak"]["mean"]),
        },
    }
    reported = {
        "noisy": {
            "n": noisy["summary"]["n"],
            "snr_db_mean": _quantize(noisy["summary"]["snr_db"]["mean"]),
            "si_sdr_db_mean": _quantize(
                noisy["summary"]["si_sdr_db"]["mean"]),
            "stoi_mean": _quantize(noisy["summary"]["stoi"]["mean"]),
            "snr_improvement_db_mean": _quantize(
                noisy["summary"]["snr_db"]["delta_vs_identity"]["mean"]),
            "inference_seconds_mean": _quantize(
                noisy["summary"]["inference_seconds"]["mean"]),
            "inference_seconds_median": _quantize(
                noisy["summary"]["inference_seconds"]["median"]),
            "inference_seconds_p95": _quantize(
                noisy["summary"]["inference_seconds"]["p95"]),
            "inference_seconds_max": _quantize(
                noisy["summary"]["inference_seconds"]["max"]),
            "rtf_mean": _quantize(noisy["summary"]["adapter_rtf"]["mean"]),
            "rtf_median": _quantize(noisy["summary"]["adapter_rtf"]["median"]),
            "rtf_p95": _quantize(noisy["summary"]["adapter_rtf"]["p95"]),
            "rtf_max": _quantize(noisy["summary"]["adapter_rtf"]["max"]),
            "snr_improvement_wins": noisy["summary"]["snr_db"][
                "delta_vs_identity"]["wins"],
            "snr_improvement_ties": noisy["summary"]["snr_db"][
                "delta_vs_identity"]["ties"],
            "snr_improvement_losses": noisy["summary"]["snr_db"][
                "delta_vs_identity"]["losses"],
        },
        "clean": {
            "n": clean["clean_summary"]["n"],
            "snr_db_mean": _quantize(clean["clean_summary"]["mean_snr_db"]),
            "si_sdr_db_mean": _quantize(
                clean["clean_summary"]["mean_si_sdr_db"]),
            "stoi_mean": _quantize(clean["clean_summary"]["mean_stoi"]),
            "rtf_mean": _quantize(clean["clean_summary"]["mean_rtf"]),
        },
        "rms_matched": {
            "n": matched["summary"]["n"],
            "snr_improvement_db_mean": _quantize(
                matched["summary"]["mean_snr_improvement_db"]),
            "si_sdr_db_mean": _quantize(
                matched["summary"]["mean_si_sdr_db"]),
            "stoi_mean": _quantize(matched["summary"]["mean_stoi"]),
            "postprocess_seconds_mean": _quantize(
                matched["summary"]["mean_postprocess_seconds"]),
            "output_peak_mean": _quantize(
                matched["summary"]["mean_output_peak"]),
        },
    }
    agreement = {
        section: {
            key: recomputed[section][key] == reported[section][key]
            for key in recomputed[section]
        }
        for section in ("noisy", "clean", "rms_matched")
    }
    clean_identity_stoi_consistent = _agrees(
        _dec(clean["clean_summary"]["mean_stoi"]) -
        _dec(clean["clean_summary"]["delta_stoi_vs_clean_identity"]["mean"]),
        Decimal(1))
    return {
        "boundary": "recorded_rows_arithmetic_consistency_only",
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "model_executed": False,
        "weights_loaded": False,
        "audio_read": False,
        "network_used": False,
        "tolerance_decimal_places": 6,
        "identity": identity,
        "recomputed": recomputed,
        "reported": reported,
        "agreement": agreement,
        "all_agree": all(all(section.values())
                         for section in agreement.values()),
        "rtf_definition_consistent": rtf_definition_consistent,
        "clean_rtf_definition_consistent": clean_rtf_definition_consistent,
        "clean_identity_stoi_consistent": clean_identity_stoi_consistent,
        "note": "Aggregates are recomputed from recorded per-item rows with "
                "exact decimal arithmetic. This is provenance consistency, "
                "not a reproduced run, quality result or qualification.",
    }


# --------------------------------------------------------------------------
# Synthetic protocol envelope (no runtime, no model, no real audio)
# --------------------------------------------------------------------------
def synthetic_frame() -> list[float]:
    return [((index * 17) % 51 - 25) / 32 for index in range(FRAME_SAMPLES)]


def frame_bytes(values: list[float]) -> bytes:
    return struct.pack("<%df" % len(values), *values)


def frame_from_bytes(payload: bytes) -> list[float]:
    return list(struct.unpack("<%df" % (len(payload) // 4), payload))


def _payload_from_hex(text: Any) -> bytes:
    if not isinstance(text, str) or len(text) % 2:
        raise AdmissionError("payload_hex_invalid")
    try:
        return bytes.fromhex(text)
    except ValueError as error:
        raise AdmissionError("payload_hex_invalid") from error


def _envelope_input() -> dict:
    payload = frame_bytes(synthetic_frame())
    values = frame_from_bytes(payload)
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_count": FRAME_SAMPLES,
        "dtype": "f32",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
        "payload_hex": payload.hex(),
        "finite": True,
        "peak": _decimal_string(max(abs(value) for value in values)),
    }


def protocol_request() -> dict:
    return {
        "protocol": PROTOCOL_ID,
        "request_id": "envelope-0001",
        "mode": "offline",
        "variant": "identity",
        "input": _envelope_input(),
        "options": {
            "network": "denied",
            "downloads": "denied",
            "writes": "attempt_only",
        },
    }


ENVELOPE_INPUT_FIELDS = ("sample_rate_hz", "channels", "sample_count", "dtype",
                         "sha256", "byte_count", "payload_hex", "finite",
                         "peak")
ENVELOPE_OPTION_FIELDS = ("network", "downloads", "writes")
ENVELOPE_FIELDS = ("protocol", "request_id", "mode", "variant", "input",
                   "options")


def validate_protocol_request(request: Any) -> bytes:
    if not isinstance(request, dict):
        raise AdmissionError("request_not_object")
    if tuple(sorted(request)) != tuple(sorted(ENVELOPE_FIELDS)):
        raise AdmissionError("request_fields_invalid")
    if request["protocol"] != PROTOCOL_ID:
        raise AdmissionError("protocol_invalid")
    if not isinstance(request["request_id"], str) or not SLUG.match(
            request["request_id"]):
        raise AdmissionError("request_id_invalid")
    if request["mode"] not in RUN_MODES:
        raise AdmissionError("mode_invalid")
    if request["variant"] not in ENVELOPE_VARIANTS:
        raise AdmissionError("variant_invalid")
    options = request["options"]
    if not isinstance(options, dict) or tuple(sorted(options)) != tuple(
            sorted(ENVELOPE_OPTION_FIELDS)):
        raise AdmissionError("options_invalid")
    if options["network"] != "denied":
        raise AdmissionError("network_not_denied")
    if options["downloads"] != "denied":
        raise AdmissionError("downloads_not_denied")
    if options["writes"] != "attempt_only":
        raise AdmissionError("writes_not_bounded")
    payload = validate_envelope_input(request["input"])
    return payload


def validate_envelope_input(block: Any) -> bytes:
    if not isinstance(block, dict):
        raise AdmissionError("input_not_object")
    if tuple(sorted(block)) != tuple(sorted(ENVELOPE_INPUT_FIELDS)):
        raise AdmissionError("input_fields_invalid")
    if block["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise AdmissionError("sample_rate_invalid")
    if block["channels"] != CHANNELS:
        raise AdmissionError("channels_invalid")
    if block["sample_count"] != FRAME_SAMPLES:
        raise AdmissionError("sample_count_invalid")
    if block["dtype"] != "f32":
        raise AdmissionError("dtype_invalid")
    if not isinstance(block["finite"], bool) or block["finite"] is not True:
        raise AdmissionError("finite_flag_invalid")
    payload = _payload_from_hex(block["payload_hex"])
    if len(payload) != FRAME_BYTES:
        raise AdmissionError("byte_count_invalid")
    if block["byte_count"] != len(payload):
        raise AdmissionError("byte_count_invalid")
    if not isinstance(block["sha256"], str) or not HEX64.match(
            block["sha256"]):
        raise AdmissionError("sha256_invalid")
    if hashlib.sha256(payload).hexdigest() != block["sha256"]:
        raise AdmissionError("sha256_mismatch")
    values = frame_from_bytes(payload)
    if not all(math.isfinite(value) for value in values):
        raise AdmissionError("input_nonfinite")
    peak = max(abs(value) for value in values)
    if not isinstance(block["peak"], str) or block["peak"] != _decimal_string(
            peak):
        raise AdmissionError("peak_mismatch")
    return payload


class SyntheticEnhancementEnvelope:
    """Protocol-envelope stand-in. Never imports or executes a runtime."""

    def __init__(self) -> None:
        self.closed = False
        self.call_count = 0

    def _ensure_open(self) -> None:
        if self.closed:
            raise AdmissionError("enhancer_closed")

    def process(self, request: Any) -> dict:
        self._ensure_open()
        payload = validate_protocol_request(request)
        values = frame_from_bytes(payload)
        if request["variant"] == "identity":
            output = bytes(bytearray(payload))
        else:
            peak = max(abs(value) for value in values)
            scale = 1.0 / peak if peak else 0.0
            scaled = [max(-1.0, min(1.0, value * scale)) for value in values]
            output = frame_bytes(scaled)
        self.call_count += 1
        output_values = frame_from_bytes(output)
        return {
            "protocol": PROTOCOL_ID,
            "request_id": request["request_id"],
            "status": "ok",
            "call_index": self.call_count,
            "variant": request["variant"],
            "output": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": CHANNELS,
                "sample_count": len(output_values),
                "dtype": "f32",
                "sha256": hashlib.sha256(output).hexdigest(),
                "byte_count": len(output),
                "peak": _decimal_string(
                    max(abs(value) for value in output_values)),
                "payload_hex": output.hex(),
            },
            "timing_measured": False,
            "runtime_invoked": False,
            "weights_loaded": False,
            "network_used": False,
        }

    def reset(self) -> None:
        self._ensure_open()
        self.call_count = 0

    def close(self) -> None:
        self.closed = True


def _envelope_case(case_id: str, mutate: Any) -> dict:
    request = copy.deepcopy(protocol_request())
    before = copy.deepcopy(request)
    mutate(request)
    adapter = SyntheticEnhancementEnvelope()
    try:
        adapter.process(request)
    except AdmissionError as error:
        return {
            "id": case_id,
            "status": "rejected",
            "code": error.code,
            "qualifies": False,
            "calls_after_rejection": adapter.call_count,
            "state_unchanged": adapter.call_count == 0 and request != before,
        }
    raise AssertionError("envelope case accepted: " + case_id)


def envelope_cases() -> list[dict]:
    def delete_option(row):
        del row["options"]["writes"]

    def network_allowed(row):
        row["options"]["network"] = "allowed"

    def downloads_allowed(row):
        row["options"]["downloads"] = "allowed"

    def writes_anywhere(row):
        row["options"]["writes"] = "anywhere"

    def protocol_wrong(row):
        row["protocol"] = "audioml-enhancer/2"

    def mode_streaming(row):
        row["mode"] = "streaming"

    def variant_unknown(row):
        row["variant"] = "model_inference"

    def request_id_bad(row):
        row["request_id"] = "Bad Run"

    def rate_wrong(row):
        row["input"]["sample_rate_hz"] = 8000

    def channels_wrong(row):
        row["input"]["channels"] = 2

    def dtype_wrong(row):
        row["input"]["dtype"] = "f64"

    def sha_wrong(row):
        row["input"]["sha256"] = "1" * 64

    def nonfinite(row):
        payload = frame_bytes(synthetic_frame())
        mutated = bytearray(payload)
        mutated[0:4] = struct.pack("<f", float("nan"))
        mutated_bytes = bytes(mutated)
        row["input"]["payload_hex"] = mutated_bytes.hex()
        row["input"]["sha256"] = hashlib.sha256(mutated_bytes).hexdigest()

    def byte_count_wrong(row):
        row["input"]["byte_count"] = FRAME_BYTES - 4

    def extra_key(row):
        row["input"]["extra"] = 1

    def payload_invalid(row):
        row["input"]["payload_hex"] = "zz" * FRAME_BYTES

    def sample_count_wrong(row):
        row["input"]["sample_count"] = FRAME_SAMPLES + 1

    def peak_wrong(row):
        row["input"]["peak"] = "0.5"

    cases = (
        ("EV-01", delete_option),
        ("EV-02", network_allowed),
        ("EV-03", downloads_allowed),
        ("EV-04", writes_anywhere),
        ("EV-05", protocol_wrong),
        ("EV-06", mode_streaming),
        ("EV-07", variant_unknown),
        ("EV-08", request_id_bad),
        ("EV-09", rate_wrong),
        ("EV-10", channels_wrong),
        ("EV-11", dtype_wrong),
        ("EV-12", sha_wrong),
        ("EV-13", nonfinite),
        ("EV-14", byte_count_wrong),
        ("EV-15", extra_key),
        ("EV-16", payload_invalid),
        ("EV-17", sample_count_wrong),
        ("EV-18", peak_wrong),
    )
    return [_envelope_case(case_id, mutate) for case_id, mutate in cases]


def _envelope_variant(variant: str) -> dict:
    request = protocol_request()
    request["variant"] = variant
    payload = validate_protocol_request(copy.deepcopy(request))
    adapter = SyntheticEnhancementEnvelope()
    first = adapter.process(copy.deepcopy(request))
    second = adapter.process(copy.deepcopy(request))
    adapter.reset()
    replay = adapter.process(copy.deepcopy(request))
    adapter.close()
    first_payload = bytes.fromhex(first["output"]["payload_hex"])
    second_payload = bytes.fromhex(second["output"]["payload_hex"])
    replay_payload = bytes.fromhex(replay["output"]["payload_hex"])
    values = frame_from_bytes(first_payload)
    return {
        "variant": variant,
        "input_sha256": hashlib.sha256(payload).hexdigest(),
        "output_sha256": first["output"]["sha256"],
        "output_byte_count": first["output"]["byte_count"],
        "output_sample_count": first["output"]["sample_count"],
        "output_peak": _decimal_string(max(abs(value) for value in values)),
        "identity_exact": first_payload == payload,
        "replay_identical": first_payload == second_payload,
        "reset_replay_identical": first_payload == replay_payload,
        "finite_output": all(math.isfinite(value) for value in values),
        "length_preserving": len(first_payload) == len(payload),
        "peak_within_unit": max(abs(value) for value in values) <= 1.0,
        "changed": first_payload != payload,
    }


def synthetic_envelope_probe() -> dict:
    """Execute the deterministic envelope only; no runtime or model."""
    identity = _envelope_variant("identity")
    unit_peak = _envelope_variant("unit_peak")

    request = protocol_request()
    adapter = SyntheticEnhancementEnvelope()
    adapter.process(copy.deepcopy(request))
    adapter.close()
    adapter.close()
    lifecycle_rejected = False
    lifecycle_code = ""
    try:
        adapter.process(copy.deepcopy(request))
    except AdmissionError as error:
        lifecycle_rejected = True
        lifecycle_code = error.code

    cases = envelope_cases()
    return {
        "schema_id": ENVELOPE_SCHEMA_ID,
        "boundary": "synthetic_protocol_envelope_only_not_a_runtime",
        "frame_samples": FRAME_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "variants": [identity, unit_peak],
        "typical_api_use": {
            "status": "synthetic_pass",
            "calls": 3,
            "request_sha256": identity["input_sha256"],
            "output_sha256": identity["output_sha256"],
            "output_byte_count": identity["output_byte_count"],
            "output_sample_count": identity["output_sample_count"],
            "output_peak": identity["output_peak"],
            "identity_exact": identity["identity_exact"],
            "replay_identical": identity["replay_identical"],
            "reset_replay_identical": identity["reset_replay_identical"],
            "close_idempotent": True,
            "run_after_close_rejected": lifecycle_rejected,
            "timing_measured": False,
            "runtime_invoked": False,
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
            "qualifies": False,
        },
        "mechanism_note": "The unit_peak variant is a bounded synthetic gain "
                          "control. It shows a level change with unchanged "
                          "length; it is not SepFormer output and says nothing "
                          "about model content or quality.",
        "lifecycle": {
            "id": "EV-LC-01",
            "status": "rejected" if lifecycle_rejected else "accepted",
            "code": lifecycle_code,
            "qualifies": False,
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
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
        "qualifies": False,
    }


# --------------------------------------------------------------------------
# Admission control and rejection matrix
# --------------------------------------------------------------------------
def control_manifest() -> dict:
    assets = []
    for index, name in enumerate(sorted(CHECKPOINT_FILES), start=1):
        assets.append({
            "asset_id": "sepformer-asset-%02d" % index,
            "name": name,
            "byte_count": 1,
            "sha256": CHECKPOINT_FILES[name],
            "terms_sha256": ("%064x" % index),
            "present_at_review": True,
        })
    digest = "0123456789abcdef" * 4
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "run_id": "synthetic-run-0001",
        "model": {
            "identity": MODEL_ID,
            "revision": MODEL_REVISION,
            "license": MODEL_LICENSE,
            "license_review_sha256": digest,
            "mode": "offline",
            "streaming_supported": False,
        },
        "runtime": {
            "python": REFERENCE_EXECUTION_POLICY["python"],
            "torch": REFERENCE_EXECUTION_POLICY["torch"],
            "torchaudio": REFERENCE_EXECUTION_POLICY["torchaudio"],
            "speechbrain": REFERENCE_EXECUTION_POLICY["speechbrain"],
            "hyperpyyaml": REFERENCE_EXECUTION_POLICY["hyperpyyaml"],
            "device": REFERENCE_EXECUTION_POLICY["device"],
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
            "install_reference": "synthetic-schema-control-no-install",
            "wheel_digests": {
                "hyperpyyaml": digest,
                "speechbrain": SPEECHBRAIN_WHEEL_SHA256,
                "torch": digest,
                "torchaudio": digest,
            },
        },
        "assets": assets,
        "corpus": {
            "cohort_id": "synthetic-schema-control",
            "pair_count": 30,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_count_per_item": 160000,
            "items_sha256": digest,
            "noisy_manifest_sha256": digest,
            "clean_manifest_sha256": digest,
            "clean_reference": True,
            "terms_sha256": digest,
        },
        "outputs": {
            "row_count": 30,
            "items_sha256": digest,
            "finite": True,
            "length_preserving": True,
            "peak_max": "1",
            "raw_peak_max": "1",
            "delay_compensation_samples": 0,
            "normalization": OUTPUT_NORMALIZATION,
        },
        "metrics": {
            "protocol": PROTOCOL_RECORDED["id"],
            "pair_count": 30,
            "si_sdr_delta_db_mean": "0",
            "stoi_delta_mean": "0",
            "clean_stoi_mean": "1",
            "baseline_count": 3,
            "bootstrap_replicates": 1000,
            "nonfinite_count": 0,
            "invalid_output_count": 0,
            "scorer_sha256": digest,
        },
        "controls": [
            {"id": "control-identity-noisy", "kind": "identity_noisy"},
            {"id": "control-baseline", "kind": "task_matched_baseline"},
            {"id": "control-clean", "kind": "clean_preservation"},
            {"id": "control-adverse", "kind": "adverse_missing"},
            {"id": "control-nonfinite", "kind": "nonfinite_rejection"},
        ],
        "rights": {
            "weight_terms": "not_reviewed_synthetic_control",
            "runtime_terms": "not_reviewed_synthetic_control",
            "training_data_terms": "not_reviewed_synthetic_control",
            "data_terms": "synthetic_schema_control_only",
            "output_use": "synthetic_schema_control_only",
            "review_reference": "pending_task_local_schema_control",
            "claims_qualified": False,
        },
    }


def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise AdmissionError("wrong_type:" + path)
    return value


def _exact_keys(value: dict, expected: tuple[str, ...], path: str) -> dict:
    if tuple(sorted(value)) != tuple(sorted(expected)):
        raise AdmissionError("field_set_invalid:" + path)
    return value


def _text(value: Any, path: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value) < minimum:
        raise AdmissionError("text_invalid:" + path)
    return value


def _int_field(value: Any, path: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError("int_invalid:" + path)
    if value < minimum or value > maximum:
        raise AdmissionError("int_out_of_range:" + path)
    return value


def _decimal_field(value: Any, path: str, minimum: str,
                   maximum: str) -> Decimal:
    if not isinstance(value, str) or not DECIMAL.match(value):
        raise AdmissionError("decimal_invalid:" + path)
    if value in {"-0", "-0.0"} or value.startswith("-0.") and set(
            value[3:]) == {"0"}:
        raise AdmissionError("decimal_non_canonical:" + path)
    if "." in value:
        fraction = value.split(".", 1)[1]
        if not fraction or fraction.endswith("0") or len(fraction) > 9:
            raise AdmissionError("decimal_non_canonical:" + path)
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise AdmissionError("decimal_invalid:" + path) from error
    if parsed < Decimal(minimum) or parsed > Decimal(maximum):
        raise AdmissionError("decimal_out_of_range:" + path)
    return parsed


def _bool_field(value: Any, path: str, expected: bool | None = None) -> bool:
    if not isinstance(value, bool):
        raise AdmissionError("bool_invalid:" + path)
    if expected is not None and value is not expected:
        raise AdmissionError("bool_constant_invalid:" + path)
    return value


def _hex_field(value: Any, path: str) -> str:
    if not isinstance(value, str) or not HEX64.match(value):
        raise AdmissionError("digest_invalid:" + path)
    return value


def validate_manifest(manifest: dict) -> None:
    row = _require_object(manifest, "root")
    _exact_keys(row, MANIFEST_FIELDS, "root")
    if row["schema_id"] != ADMISSION_SCHEMA_ID:
        raise AdmissionError("schema_id_invalid")
    if not isinstance(row["run_id"], str) or not SLUG.match(row["run_id"]):
        raise AdmissionError("run_id_invalid")

    model = _exact_keys(_require_object(row["model"], "model"), MODEL_FIELDS,
                        "model")
    if model["identity"] != MODEL_ID:
        raise AdmissionError("model_identity_invalid")
    if model["revision"] != MODEL_REVISION:
        raise AdmissionError("model_revision_invalid")
    if model["license"] != MODEL_LICENSE:
        raise AdmissionError("model_license_invalid")
    _hex_field(model["license_review_sha256"], "model.license_review_sha256")
    if model["mode"] not in RUN_MODES:
        raise AdmissionError("model_mode_invalid")
    _bool_field(model["streaming_supported"], "model.streaming_supported",
                False)

    runtime = _exact_keys(_require_object(row["runtime"], "runtime"),
                          RUNTIME_FIELDS, "runtime")
    for key in ("python", "torch", "torchaudio", "speechbrain",
                "hyperpyyaml", "device"):
        if runtime[key] != REFERENCE_EXECUTION_POLICY[key]:
            raise AdmissionError("runtime_constant_invalid:" + key)
    _int_field(runtime["intra_op_threads"], "runtime.intra_op_threads", 1, 1)
    _int_field(runtime["interop_op_threads"], "runtime.interop_op_threads",
               1, 1)
    _bool_field(runtime["deterministic_algorithms"],
                "runtime.deterministic_algorithms", True)
    _bool_field(runtime["offline"], "runtime.offline", True)
    _text(runtime["install_reference"], "runtime.install_reference", 1)
    wheels = _require_object(runtime["wheel_digests"],
                             "runtime.wheel_digests")
    _exact_keys(wheels, ("hyperpyyaml", "speechbrain", "torch", "torchaudio"),
                "runtime.wheel_digests")
    for name in sorted(wheels):
        _hex_field(wheels[name], "runtime.wheel_digests." + name)
    if wheels["speechbrain"] != SPEECHBRAIN_WHEEL_SHA256:
        raise AdmissionError("speechbrain_wheel_digest_mismatch")

    assets = row["assets"]
    if not isinstance(assets, list) or len(assets) != len(CHECKPOINT_FILES):
        raise AdmissionError("asset_count_invalid")
    names = []
    asset_ids = []
    for index, asset in enumerate(assets):
        item = _exact_keys(_require_object(
            asset, "assets[%d]" % index), ASSET_FIELDS, "assets[%d]" % index)
        asset_ids.append(item["asset_id"])
        names.append(item["name"])
        if not isinstance(item["asset_id"], str) or not SLUG.match(
                item["asset_id"]):
            raise AdmissionError("asset_id_invalid")
        _int_field(item["byte_count"], "assets[%d].byte_count" % index, 1,
                   4 * 1024 * 1024 * 1024)
        _hex_field(item["sha256"], "assets[%d].sha256" % index)
        _hex_field(item["terms_sha256"], "assets[%d].terms_sha256" % index)
        _bool_field(item["present_at_review"],
                    "assets[%d].present_at_review" % index, True)
    if len(set(asset_ids)) != len(asset_ids):
        raise AdmissionError("asset_id_duplicate")
    if sorted(names) != sorted(CHECKPOINT_FILES):
        raise AdmissionError("asset_set_invalid")
    for index, name in enumerate(names):
        if assets[index]["sha256"] != CHECKPOINT_FILES[name]:
            raise AdmissionError("asset_digest_mismatch:" + name)

    corpus = _exact_keys(_require_object(row["corpus"], "corpus"),
                         CORPUS_FIELDS, "corpus")
    if not isinstance(corpus["cohort_id"], str) or not SLUG.match(
            corpus["cohort_id"]):
        raise AdmissionError("cohort_id_invalid")
    _int_field(corpus["pair_count"], "corpus.pair_count",
               PROTOCOL_RECORDED["pair_count"], PROTOCOL_RECORDED["pair_count"])
    _int_field(corpus["sample_rate_hz"], "corpus.sample_rate_hz",
               SAMPLE_RATE_HZ, SAMPLE_RATE_HZ)
    _int_field(corpus["channels"], "corpus.channels", CHANNELS, CHANNELS)
    _int_field(corpus["sample_count_per_item"],
               "corpus.sample_count_per_item", 160000, 160000)
    _hex_field(corpus["items_sha256"], "corpus.items_sha256")
    _hex_field(corpus["noisy_manifest_sha256"],
               "corpus.noisy_manifest_sha256")
    _hex_field(corpus["clean_manifest_sha256"],
               "corpus.clean_manifest_sha256")
    _bool_field(corpus["clean_reference"], "corpus.clean_reference", True)
    _hex_field(corpus["terms_sha256"], "corpus.terms_sha256")

    outputs = _exact_keys(_require_object(row["outputs"], "outputs"),
                          OUTPUT_FIELDS, "outputs")
    _int_field(outputs["row_count"], "outputs.row_count",
               PROTOCOL_RECORDED["pair_count"], PROTOCOL_RECORDED["pair_count"])
    _hex_field(outputs["items_sha256"], "outputs.items_sha256")
    _bool_field(outputs["finite"], "outputs.finite", True)
    _bool_field(outputs["length_preserving"],
                "outputs.length_preserving", True)
    peak_max = _decimal_field(outputs["peak_max"], "outputs.peak_max", "0", "1")
    raw_peak = _decimal_field(outputs["raw_peak_max"], "outputs.raw_peak_max",
                              "0.000001", "1000")
    if raw_peak < peak_max:
        raise AdmissionError("raw_peak_below_normalized_peak")
    _int_field(outputs["delay_compensation_samples"],
               "outputs.delay_compensation_samples", 0, 0)
    if outputs["normalization"] != OUTPUT_NORMALIZATION:
        raise AdmissionError("normalization_invalid")

    metrics = _exact_keys(_require_object(row["metrics"], "metrics"),
                          METRICS_FIELDS, "metrics")
    if metrics["protocol"] != PROTOCOL_RECORDED["id"]:
        raise AdmissionError("metrics_protocol_invalid")
    _int_field(metrics["pair_count"], "metrics.pair_count",
               PROTOCOL_RECORDED["pair_count"], PROTOCOL_RECORDED["pair_count"])
    _decimal_field(metrics["si_sdr_delta_db_mean"],
                   "metrics.si_sdr_delta_db_mean", "-60", "60")
    _decimal_field(metrics["stoi_delta_mean"], "metrics.stoi_delta_mean",
                   "-1", "1")
    _decimal_field(metrics["clean_stoi_mean"], "metrics.clean_stoi_mean",
                   "0", "1")
    _int_field(metrics["baseline_count"], "metrics.baseline_count", 3, 8)
    _int_field(metrics["bootstrap_replicates"],
               "metrics.bootstrap_replicates", 1000, 1000000)
    _int_field(metrics["nonfinite_count"], "metrics.nonfinite_count", 0, 0)
    _int_field(metrics["invalid_output_count"],
               "metrics.invalid_output_count", 0, 0)
    _hex_field(metrics["scorer_sha256"], "metrics.scorer_sha256")

    controls = row["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise AdmissionError("control_count_invalid")
    control_ids = []
    control_kinds = []
    for index, control in enumerate(controls):
        item = _exact_keys(_require_object(
            control, "controls[%d]" % index), CONTROL_FIELDS,
            "controls[%d]" % index)
        if not isinstance(item["id"], str) or not SLUG.match(item["id"]):
            raise AdmissionError("control_id_invalid")
        control_ids.append(item["id"])
        control_kinds.append(item["kind"])
    if len(set(control_ids)) != len(control_ids):
        raise AdmissionError("control_id_duplicate")
    if sorted(control_kinds) != sorted(CONTROL_KINDS):
        raise AdmissionError("control_kinds_invalid")

    rights = _exact_keys(_require_object(row["rights"], "rights"),
                         RIGHTS_FIELDS, "rights")
    for key in ("weight_terms", "runtime_terms", "training_data_terms",
                "data_terms", "output_use", "review_reference"):
        _text(rights[key], "rights." + key, 1)
    _bool_field(rights["claims_qualified"], "rights.claims_qualified", False)


def _manifest_case(case_id: str, group: str, mutate: Any) -> dict:
    manifest = control_manifest()
    before = copy.deepcopy(manifest)
    mutate(manifest)
    snapshot = copy.deepcopy(manifest)
    try:
        validate_manifest(manifest)
    except AdmissionError as error:
        return {
            "id": case_id,
            "group": group,
            "status": "rejected",
            "code": error.code,
            "qualifies": False,
            "state_unchanged": manifest == snapshot and manifest != before,
        }
    raise AssertionError("manifest case accepted: " + case_id)


def _normalise_parse_code(error: ValueError) -> str:
    raw = str(error).split(":", 1)[0]
    if raw.startswith("duplicate_json_key"):
        return "duplicate_json_key"
    if raw.startswith("nonfinite_json_constant"):
        return "nonfinite_json_constant"
    if raw == "json_root_not_object":
        return "json_root_not_object"
    if raw == "json_byte_order_mark":
        return "json_byte_order_mark"
    if raw == "Extra data":
        return "strict_json_trailing_data"
    return "strict_json_rejected"


def _parse_case(case_id: str, text: str) -> dict:
    try:
        loads_strict(text)
    except ValueError as error:
        return {
            "id": case_id,
            "group": "document",
            "status": "rejected",
            "code": _normalise_parse_code(error),
            "qualifies": False,
            "state_unchanged": True,
        }
    raise AssertionError("parse case accepted: " + case_id)


def admission_cases() -> list[dict]:
    parse_cases = (
        _parse_case("DOC-01", '{"a":1,"a":2}'),
        _parse_case("DOC-02", '{"a":NaN}'),
        _parse_case("DOC-03", '{"a":Infinity}'),
        _parse_case("DOC-04", "[]"),
        _parse_case("DOC-05", '{"a":1} trailing'),
        _parse_case("DOC-06", "\ufeff{\"a\":1}"),
    )

    def drop(key):
        def mutate(row):
            del row[key]
        return mutate

    def set_key(key, value):
        def mutate(row):
            row[key] = value
        return mutate

    def nested(section, key, value):
        def mutate(row):
            row[section][key] = value
        return mutate

    def drop_nested(section, key):
        def mutate(row):
            del row[section][key]
        return mutate

    def extra_nested(section, key, value):
        def mutate(row):
            row[section][key] = value
        return mutate

    def asset_field(index, key, value):
        def mutate(row):
            row["assets"][index][key] = value
        return mutate

    def assets_mutate(fn):
        def mutate(row):
            fn(row["assets"])
        return mutate

    def pop_asset(name):
        def mutate(rows):
            rows[:] = [asset for asset in rows if asset["name"] != name]
        return mutate

    def duplicate_asset_id(rows):
        rows[1]["asset_id"] = rows[0]["asset_id"]

    def unknown_asset_name(rows):
        rows[0]["name"] = "weights.safetensors"

    def extra_asset(rows):
        rows.append({
            "asset_id": "sepformer-extra",
            "name": "encoder.ckpt",
            "byte_count": 1,
            "sha256": CHECKPOINT_FILES["encoder.ckpt"],
            "terms_sha256": "2" * 64,
            "present_at_review": True,
        })

    def control_duplicate_kind(row):
        row["controls"][1]["kind"] = row["controls"][0]["kind"]

    def control_unknown_kind(row):
        row["controls"][0]["kind"] = "runtime_candidate"

    def control_extra(row):
        row["controls"][0]["extra"] = 1

    def control_bad_id(row):
        row["controls"][0]["id"] = "Bad Id"

    def output_peak_nan(row):
        row["outputs"]["peak_max"] = float("nan")

    def input_decimal_float(row):
        row["metrics"]["stoi_delta_mean"] = 0.1

    def corpus_pair_count(row):
        row["corpus"]["pair_count"] = 29

    def output_row_count(row):
        row["outputs"]["row_count"] = 31

    def metrics_pair_count(row):
        row["metrics"]["pair_count"] = 29

    def peak_out_of_range(row):
        row["outputs"]["peak_max"] = "1.5"

    def delay_nonzero(row):
        row["outputs"]["delay_compensation_samples"] = 1

    def raw_below_peak(row):
        row["outputs"]["peak_max"] = "0.9"
        row["outputs"]["raw_peak_max"] = "0.5"

    def noncanonical_decimal(row):
        row["metrics"]["stoi_delta_mean"] = "0.10"

    def null_metric(row):
        row["metrics"]["stoi_delta_mean"] = None

    cases = parse_cases + (
        _manifest_case("ST-01", "structure", drop("runtime")),
        _manifest_case("ST-02", "structure", set_key("extra", 1)),
        _manifest_case("ST-03", "structure", lambda row: row.clear()),
        _manifest_case("ST-04", "structure", set_key("schema_id", "x")),
        _manifest_case("ST-05", "structure", set_key("run_id", "Bad Run")),
        _manifest_case("ST-06", "structure", set_key("run_id", 7)),
        _manifest_case("ST-07", "structure", set_key("model", [])),
        _manifest_case("ST-08", "structure", set_key("rights", "x")),
        _manifest_case("MD-01", "model", nested(
            "model", "identity", "speechbrain/other-model")),
        _manifest_case("MD-02", "model", nested(
            "model", "revision", "0" * 40)),
        _manifest_case("MD-03", "model", nested(
            "model", "license", "MIT")),
        _manifest_case("MD-04", "model", nested(
            "model", "license_review_sha256", "not-a-digest")),
        _manifest_case("MD-05", "model", nested(
            "model", "mode", "streaming")),
        _manifest_case("MD-06", "model", nested(
            "model", "streaming_supported", True)),
        _manifest_case("MD-07", "model", extra_nested("model", "extra", 1)),
        _manifest_case("MD-08", "model", drop_nested("model", "license")),
        _manifest_case("RT-01", "runtime", nested(
            "runtime", "python", "3.12.16")),
        _manifest_case("RT-02", "runtime", nested(
            "runtime", "torch", "2.2.2")),
        _manifest_case("RT-03", "runtime", nested(
            "runtime", "torchaudio", "2.0.0")),
        _manifest_case("RT-04", "runtime", nested(
            "runtime", "speechbrain", "1.0.2")),
        _manifest_case("RT-05", "runtime", nested(
            "runtime", "hyperpyyaml", "1.2.2")),
        _manifest_case("RT-06", "runtime", nested("runtime", "device", "mps")),
        _manifest_case("RT-07", "runtime", nested(
            "runtime", "intra_op_threads", 0)),
        _manifest_case("RT-08", "runtime", nested(
            "runtime", "interop_op_threads", 2)),
        _manifest_case("RT-09", "runtime", nested(
            "runtime", "deterministic_algorithms", False)),
        _manifest_case("RT-10", "runtime", nested("runtime", "offline", False)),
        _manifest_case("RT-11", "runtime", nested(
            "runtime", "install_reference", "")),
        _manifest_case("RT-12", "runtime", lambda row: row["runtime"][
            "wheel_digests"].pop("torch")),
        _manifest_case("RT-13", "runtime", nested(
            "runtime", "wheel_digests", {"torch": "x"})),
        _manifest_case("RT-14", "runtime", nested(
            "runtime", "wheel_digests",
            {"hyperpyyaml": "0123456789abcdef" * 4,
             "speechbrain": "1" * 64,
             "torch": "0123456789abcdef" * 4,
             "torchaudio": "0123456789abcdef" * 4})),
        _manifest_case("RT-15", "runtime", extra_nested("runtime", "extra", 1)),
        _manifest_case("AS-01", "assets", assets_mutate(
            lambda rows: rows.clear())),
        _manifest_case("AS-02", "assets", assets_mutate(duplicate_asset_id)),
        _manifest_case("AS-03", "assets", assets_mutate(unknown_asset_name)),
        _manifest_case("AS-04", "assets", assets_mutate(pop_asset("config.json"))),
        _manifest_case("AS-05", "assets", asset_field(1, "byte_count", 0)),
        _manifest_case("AS-06", "assets", asset_field(0, "sha256", "1" * 64)),
        _manifest_case("AS-07", "assets", asset_field(
            0, "terms_sha256", "not-a-digest")),
        _manifest_case("AS-08", "assets", asset_field(
            0, "present_at_review", False)),
        _manifest_case("AS-09", "assets", assets_mutate(extra_asset)),
        _manifest_case("AS-10", "assets", assets_mutate(
            lambda rows: rows.append(dict(rows[0])))),
        _manifest_case("CO-01", "corpus", nested(
            "corpus", "cohort_id", "Bad Cohort")),
        _manifest_case("CO-02", "corpus", corpus_pair_count),
        _manifest_case("CO-03", "corpus", nested(
            "corpus", "sample_rate_hz", 8000)),
        _manifest_case("CO-04", "corpus", nested("corpus", "channels", 2)),
        _manifest_case("CO-05", "corpus", nested(
            "corpus", "sample_count_per_item", 159999)),
        _manifest_case("CO-06", "corpus", nested(
            "corpus", "items_sha256", "0" * 64)),
        _manifest_case("CO-07", "corpus", nested(
            "corpus", "noisy_manifest_sha256", "x")),
        _manifest_case("CO-08", "corpus", nested(
            "corpus", "clean_reference", False)),
        _manifest_case("CO-09", "corpus", nested("corpus", "terms_sha256", "")),
        _manifest_case("CO-10", "corpus", extra_nested("corpus", "extra", 1)),
        _manifest_case("OU-01", "outputs", output_row_count),
        _manifest_case("OU-02", "outputs", nested(
            "outputs", "items_sha256", "x")),
        _manifest_case("OU-03", "outputs", nested("outputs", "finite", False)),
        _manifest_case("OU-04", "outputs", nested(
            "outputs", "length_preserving", False)),
        _manifest_case("OU-05", "outputs", peak_out_of_range),
        _manifest_case("OU-06", "outputs", delay_nonzero),
        _manifest_case("OU-07", "outputs", nested(
            "outputs", "normalization", "none")),
        _manifest_case("OU-08", "outputs", raw_below_peak),
        _manifest_case("OU-09", "outputs", extra_nested("outputs", "extra", 1)),
        _manifest_case("ME-01", "metrics", nested(
            "metrics", "protocol", "CLN-99")),
        _manifest_case("ME-02", "metrics", metrics_pair_count),
        _manifest_case("ME-03", "metrics", nested(
            "metrics", "si_sdr_delta_db_mean", "60.5")),
        _manifest_case("ME-04", "metrics", nested(
            "metrics", "stoi_delta_mean", "-1.5")),
        _manifest_case("ME-05", "metrics", nested(
            "metrics", "clean_stoi_mean", "1.5")),
        _manifest_case("ME-06", "metrics", nested(
            "metrics", "baseline_count", 2)),
        _manifest_case("ME-07", "metrics", nested(
            "metrics", "bootstrap_replicates", 999)),
        _manifest_case("ME-08", "metrics", nested(
            "metrics", "nonfinite_count", 1)),
        _manifest_case("ME-09", "metrics", nested(
            "metrics", "invalid_output_count", 1)),
        _manifest_case("ME-10", "metrics", nested(
            "metrics", "scorer_sha256", "not-a-digest")),
        _manifest_case("ME-11", "metrics", noncanonical_decimal),
        _manifest_case("ME-12", "metrics", null_metric),
        _manifest_case("ME-13", "metrics", input_decimal_float),
        _manifest_case("ME-14", "metrics", extra_nested("metrics", "extra", 1)),
        _manifest_case("CT-01", "controls", set_key("controls", [])),
        _manifest_case("CT-02", "controls", control_duplicate_kind),
        _manifest_case("CT-03", "controls", control_unknown_kind),
        _manifest_case("CT-04", "controls", control_extra),
        _manifest_case("CT-05", "controls", control_bad_id),
        _manifest_case("RI-01", "rights", nested(
            "rights", "claims_qualified", True)),
        _manifest_case("RI-02", "rights", nested("rights", "runtime_terms", "")),
        _manifest_case("RI-03", "rights", nested(
            "rights", "review_reference", "")),
        _manifest_case("RI-04", "rights", nested("rights", "data_terms", "")),
        _manifest_case("RI-05", "rights", nested(
            "rights", "weight_terms", "")),
        _manifest_case("RI-06", "rights", nested("rights", "output_use", "")),
        _manifest_case("RI-07", "rights", nested(
            "rights", "training_data_terms", "")),
        _manifest_case("RI-08", "rights", extra_nested("rights", "extra", 1)),
        _manifest_case("NF-01", "nonfinite", output_peak_nan),
        _manifest_case("NF-02", "nonfinite", nested(
            "metrics", "si_sdr_delta_db_mean", float("inf"))),
    )
    return list(cases)


def build_admission() -> dict:
    control = control_manifest()
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
            "asset_records": len(control["assets"]),
            "control_records": len(control["controls"]),
            "manifest_sha256": object_digest(control),
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
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
    }


# --------------------------------------------------------------------------
# Contract and report
# --------------------------------------------------------------------------
def qualification() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": True,
        "runtime_present": False,
        "weights_present": False,
        "corpus_present": False,
        "outputs_present": False,
        "reproduced_inference_result": False,
        "enhancement_profile_result": False,
        "alignment_state_result": False,
        "timing_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }


def build_contract() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
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
        "qualification": qualification(),
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "scope": {
            "write_scope": WRITE_SCOPE,
            "task_local_only": True,
            "provider_registered": False,
            "adapter_implemented": False,
            "descriptor_or_registry_changed": False,
            "default_changed": False,
            "public_abi_changed": False,
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
            "channels": CHANNELS,
            "sample_format": "float32",
            "frame_samples": FRAME_SAMPLES,
            "changed": False,
        },
        "model_identity": {
            "identity": MODEL_ID,
            "revision": MODEL_REVISION,
            "license": MODEL_LICENSE,
            "license_is_model_card_claim_not_clearance": True,
            "checkpoint_files": dict(CHECKPOINT_FILES),
            "checkpoint_byte_counts_recorded": CHECKPOINT_BYTE_COUNTS_RECORDED,
            "checkpoint_total_bytes_recorded": CHECKPOINT_TOTAL_BYTES_RECORDED,
            "hub_repository_reported_bytes": HUB_REPOSITORY_REPORTED_BYTES,
            "hub_reported_size_is_exact": HUB_REPORTED_SIZE_IS_EXACT,
            "upstream_dns4_2022_dnsmos": dict(MODEL_CARD_DNS4_2022),
        },
        "recorded_runtime": dict(RECORDED_RUNTIME),
        "runtime_overlay": [{"name": name, "version": version}
                            for name, version in RUNTIME_OVERLAY],
        "reference_execution_policy": dict(REFERENCE_EXECUTION_POLICY),
        "speechbrain_wheel_sha256": SPEECHBRAIN_WHEEL_SHA256,
        "protocol": dict(PROTOCOL_RECORDED),
        "required_artifacts": [dict(item) for item in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "release_gates": gates,
        "enhancement_requirements": [dict(item)
                                     for item in ENHANCEMENT_REQUIREMENTS],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "model_fields": list(MODEL_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "asset_fields": list(ASSET_FIELDS),
            "corpus_fields": list(CORPUS_FIELDS),
            "output_fields": list(OUTPUT_FIELDS),
            "metrics_fields": list(METRICS_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "run_modes": list(RUN_MODES),
            "exact_protocol": PROTOCOL_ID,
            "exact_model": MODEL_ID,
            "exact_revision": MODEL_REVISION,
            "exact_normalization": OUTPUT_NORMALIZATION,
            "admission_only": True,
            "qualifies": False,
        },
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "upstream_license_reviewed": False,
            "weight_terms_reviewed": False,
            "training_data_terms_reviewed": False,
            "corpus_terms_reviewed": False,
            "output_use_reviewed": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "reopening_conditions": list(REOPENING_CONDITIONS),
    }


def historical_execution() -> dict:
    return {
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "why_not_reproduced": [
            "The exact six-file checkpoint revision is absent.",
            "The exact torch/torchaudio/SpeechBrain runtime is absent.",
            "No rights-cleared corpus, manifest payload or output file is "
            "present.",
            "The recorded run used four intra-op threads, not the one-thread "
            "reference policy.",
            "No target-device, listening or benchmark run exists.",
        ],
        "run": dict(HISTORICAL_RUN),
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
    }
    workspace_probes = absence_probes(AUDIO_ROOT)
    worktree_probes = worktree_absence_probes()
    home_probes = home_absence_probes()
    requirements = contract["enhancement_requirements"]
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_label": PROFILE_LABEL,
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
        "model_identity": contract["model_identity"],
        "recorded_runtime": contract["recorded_runtime"],
        "runtime_overlay": contract["runtime_overlay"],
        "reference_execution_policy": contract["reference_execution_policy"],
        "speechbrain_wheel_sha256": contract["speechbrain_wheel_sha256"],
        "protocol": contract["protocol"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "enhancement_profile": {
            "profile": PROFILE,
            "label": PROFILE_LABEL,
            "profile_source": "plan/swarm/VERIFICATION.md#Enhancement",
            "requirements": requirements,
            "summary": {
                "requirement_count": len(requirements),
                "blocked_count": sum(1 for row in requirements
                                     if row["status"] == "blocked"),
                "not_run_count": sum(1 for row in requirements
                                     if row["status"] == "not_run"),
                "measured_real_result_count": 0,
                "profile_satisfied": False,
                "values_inferred": False,
            },
        },
        "runtime_readiness": runtime_readiness(),
        "source_presence": source_presence(),
        "recorded_provenance": recorded_provenance(),
        "historical_execution": historical_execution(),
        "protocol_envelope": synthetic_envelope_probe(),
        "admission": build_admission(),
        "absence_evidence": {
            "workspace_probes": workspace_probes,
            "worktree_probes": worktree_probes,
            "home_probes": home_probes,
            "summary": absence_summary(workspace_probes, worktree_probes,
                                       home_probes),
        },
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
        "reopening_conditions": contract["reopening_conditions"],
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
        raise ValueError("contract_proposal_only")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    gates = contract.get("release_gates", [])
    if len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-%02d" % index:
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
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
    requirements = contract.get("enhancement_requirements", [])
    if len(requirements) != len(ENHANCEMENT_REQUIREMENTS):
        raise ValueError("contract_enhancement_count")
    for row in requirements:
        if row.get("status") != "blocked" or not row.get("reopen_condition"):
            raise ValueError("contract_enhancement_not_blocked")
    flags = contract.get("qualification", {})
    if flags.get("not_qualified") is not True \
            or flags.get("all_release_gates_blocked") is not True \
            or flags.get("missing_result_promoted") is not False \
            or flags.get("release_claim") is not False:
        raise ValueError("contract_qualification_flags")
