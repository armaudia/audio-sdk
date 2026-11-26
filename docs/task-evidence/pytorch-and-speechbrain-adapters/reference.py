# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS.

Standard-library only and deterministic. This module contains no PyTorch,
torchaudio, SpeechBrain, HyperPyYAML, checkpoint, corpus, audio signal or model
output. It pins the existing project adapter sources and protocol by SHA-256,
records that the exact runtime and checkpoint bytes are absent, probes a fixed
path inventory for absence, exercises the adapter *envelope* (request/result
identity, caller-owned input copy, fail-closed validation and idempotent close)
with synthetic bytes only, validates a caller-supplied adapter-run manifest
with a fail-closed admission boundary, and builds the canonical report.

Both recorded SpeechBrain evaluations are treated as provenance only. Nothing
here reproduces them, and no result qualifies the component.
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

TASK = "SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS"
COMPONENT_ID = "pytorch-and-speechbrain-adapters"
TASK_TITLE = "PyTorch and SpeechBrain adapters"
CONTRACT_ID = "audio-sdk/pytorch-and-speechbrain-adapters-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/pytorch-and-speechbrain-adapter-run/0.1"
ENVELOPE_SCHEMA_ID = (
    "audio-sdk/pytorch-and-speechbrain-adapters/protocol-envelope/0.1")
PROFILE = "tool"
PROFILE_LABEL = "Tool"
MODE = "implementation"
BASE_COMMIT = "55d99cc1f03d06c16012abea914e75d93160935a"
BRANCH = "swarm/SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS"
WRITE_SCOPE = "docs/task-evidence/pytorch-and-speechbrain-adapters/ only"
TASK_PREFIX = "docs/task-evidence/pytorch-and-speechbrain-adapters/"
DISPOSITION = (
    "Caller-supplied PyTorch/SpeechBrain adapter readiness blocker; the "
    "adapter sources and protocol are pinned, but the exact runtime, "
    "checkpoint bytes and rights-cleared inputs are absent. No implementation, "
    "execution or result.")

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
FRAME_BYTES = FRAME_SAMPLES * 4
MAX_SAMPLE_COUNT = 60 * SAMPLE_RATE_HZ
MAX_ASSET_BYTES = 4 * 1024 * 1024 * 1024
PROTOCOL_ID = "audioml-adapter/1"
RUN_MODES = ("offline",)
CONTROL_KINDS = ("identity_passthrough", "adapter_candidate",
                 "missing_runtime")

REQUIRED_INTERPRETER = "3.12.16"
RECORDED_RUNTIME = {
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
}
RUNTIME_MODULES = ("torch", "torchaudio", "speechbrain", "hyperpyyaml")
WHEEL_DIGEST_NAMES = ("hyperpyyaml", "speechbrain", "torch", "torchaudio")
SPEECHBRAIN_WHEEL_SHA256 = (
    "9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9")
RUNTIME_OVERLAY = (
    ("sentencepiece", "0.2.2"),
    ("PyYAML", "6.0.3"),
    ("ruamel.yaml", "0.18.17"),
    ("ruamel.yaml.clib", "0.2.15"),
    ("huggingface_hub", "2.3.0"),
    ("numpy", "1.26.4"),
    ("scipy", "1.17.1"),
    ("soundfile", "0.12.1"),
)

METRICGAN_ID = "SpeechBrain-1.0.3-MetricGAN+-VoiceBank"
SEPFORMER_ID = "SpeechBrain-1.0.3-SepFormer-DNS4"

ADAPTER_PROFILES = {
    METRICGAN_ID: {
        "mode": "offline",
        "model_repo": "speechbrain/metricgan-plus-voicebank",
        "model_revision": "be514d321f66b5352c5a8d59c44700f57aa8c8f5",
        "model_card_license": "Apache-2.0",
        "adapter_source": {
            "path": ("research/voice-enhancement-20261101/"
                     "agent-metricgan-eval/adapter.py"),
            "sha256": ("4f8934d4d83cd3a1042c950dbea1fb1d89c6248f499f2101"
                       "459ce8b28f4f1f4d"),
        },
        "adapter_descriptor": {
            "path": ("research/voice-enhancement-20261101/"
                     "agent-metricgan-eval/adapter.json"),
            "sha256": ("18c53358377bc5882fb5a175ae7084aa64b36accb5825f2c1"
                       "26612c3cbb37d67"),
        },
        "runtime_lock": {
            "path": ("research/voice-enhancement-20261101/"
                     "agent-metricgan-eval/requirements.lock"),
            "sha256": ("22b5283ab4f920dc16017d545552a46d2706cbade14e1cfa1"
                       "209f28c255ddc20"),
        },
        "assets": {
            "enhance_model.ckpt": {
                "byte_count": 7586021,
                "sha256": ("147bfb866bac8264603546e035bf283370e716ed2f4b7412"
                           "d308d2bcee88304f"),
            },
            "hyperparams.yaml": {
                "byte_count": None,
                "sha256": ("7bcc0835243c27f78907de0df27bc5f33d533a675787ab2"
                           "eff34188404ea225a"),
            },
            "config.json": {
                "byte_count": None,
                "sha256": ("18cb713936f15ae4acf84f0fab863e617bfd6faba362bcf5"
                           "752d85aa1f16f833"),
            },
        },
    },
    SEPFORMER_ID: {
        "mode": "offline",
        "model_repo": "speechbrain/sepformer-dns4-16k-enhancement",
        "model_revision": "e8c258546300102a240fa2595854d473cbfee49a",
        "model_card_license": "Apache-2.0",
        "adapter_source": {
            "path": ("research/voice-enhancement-20261101/"
                     "agent-sepformer-eval/adapter.py"),
            "sha256": ("9e85412481780ad9b917428bc36d5cf407cfe9c0842a96de8"
                       "953706041ad3327"),
        },
        "adapter_descriptor": {
            "path": ("research/voice-enhancement-20261101/"
                     "agent-sepformer-eval/adapter.json"),
            "sha256": ("b6135146118e303ff335a4418a8906234c9b85d9031836d96"
                       "b27a524ab0871e5"),
        },
        "runtime_lock": {
            "path": ("research/voice-enhancement-20261101/"
                     "agent-sepformer-eval/adapter.lock.json"),
            "sha256": ("631685078d2218cb0bdd656be622e6953679e1c51c1662d6a"
                       "858cf214451aac1"),
        },
        "assets": {
            "brain.ckpt": {
                "byte_count": None,
                "sha256": ("33809a026a2c1febce7b03c8aafaee4ddfc851b2c70f180f"
                           "8c06bf1017f4df5c"),
            },
            "encoder.ckpt": {
                "byte_count": None,
                "sha256": ("33de46bbf0b55031f92346827723137478cf2f77204fd1360"
                           "ba8833b5915e0ee"),
            },
            "masknet.ckpt": {
                "byte_count": None,
                "sha256": ("cfba4276bf051fc48b1d49350ef0612845328c1999cefb4c"
                           "637fc02cdbabbbdd"),
            },
            "decoder.ckpt": {
                "byte_count": None,
                "sha256": ("ab10ab1aac337bbe77ad0cbdf75acb1fba952e2d34474d51"
                           "5de2f41ddfd9a24c"),
            },
            "config.json": {
                "byte_count": None,
                "sha256": ("2aa99b583295cfdbf0d3409bc78186ad1b136d84490711ea"
                           "586bb149d9ecdfe2"),
            },
            "hyperparams.yaml": {
                "byte_count": None,
                "sha256": ("c69879126990b54562499f61d0264213b8bc4f0b0b4f750e"
                           "55d4d13ca544db3f"),
            },
        },
    },
}

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
    "research/voice-enhancement-20261101/evaluation_records.md":
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "research/voice-enhancement-20261101/agent-metricgan-eval/REPORT.md":
        "cae46203911914adafb007f6148ca9c1bdc5c1d9eb2875a0fb6205aca7303783",
    "research/voice-enhancement-20261101/agent-metricgan-eval/adapter.py":
        "4f8934d4d83cd3a1042c950dbea1fb1d89c6248f499f2101459ce8b28f4f1f4d",
    "research/voice-enhancement-20261101/agent-metricgan-eval/adapter.json":
        "18c53358377bc5882fb5a175ae7084aa64b36accb5825f2c126612c3cbb37d67",
    "research/voice-enhancement-20261101/agent-metricgan-eval/requirements.lock":
        "22b5283ab4f920dc16017d545552a46d2706cbade14e1cfa1209f28c255ddc20",
    "research/voice-enhancement-20261101/agent-sepformer-eval/REPORT.md":
        "b7a1e214d0fa402c971e39a4742d54589ce5bd25bd3de4a5bc72be843ec997f4",
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.py":
        "9e85412481780ad9b917428bc36d5cf407cfe9c0842a96de8953706041ad3327",
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.json":
        "b6135146118e303ff335a4418a8906234c9b85d9031836d96b27a524ab0871e5",
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.lock.json":
        "631685078d2218cb0bdd656be622e6953679e1c51c1662d6a858cf214451aac1",
    "adapters/README.md":
        "24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee",
    "adapters/controls/run.py":
        "4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66",
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
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/metricgan-speechbrain-voicebank/README.md":
        "0ce5593cda4ed6412d755ecd013c4ef65f3e1c50c4f264a1abb4782b57990f22",
    "docs/task-evidence/metricgan-speechbrain-voicebank/report.json":
        "8f04d6f06cea71f6497277131d3b4adcb7b5381c5fc25b4fa646fe91476935e2",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

MANIFEST_FIELDS = ("schema_id", "run_id", "adapter", "runtime", "command",
                   "assets", "input", "output", "controls", "rights")
ADAPTER_FIELDS = ("identity", "protocol", "mode", "adapter_sha256",
                  "descriptor_sha256")
RUNTIME_FIELDS = ("python", "torch", "torchaudio", "speechbrain",
                  "hyperpyyaml", "device", "intra_op_threads",
                  "interop_op_threads", "deterministic_algorithms", "offline",
                  "install_reference", "wheel_digests")
COMMAND_FIELDS = ("cli", "request_argument", "result_argument", "network",
                  "downloads")
ASSET_FIELDS = ("asset_id", "name", "byte_count", "sha256", "terms_sha256",
                "present_at_review")
INPUT_FIELDS = ("sample_rate_hz", "channels", "sample_count", "dtype",
                "sha256", "finite", "peak")
OUTPUT_FIELDS = ("sample_count", "sha256", "finite", "peak",
                 "delay_compensation_samples")
CONTROL_FIELDS = ("id", "kind")
RIGHTS_FIELDS = ("adapter_source_terms", "runtime_terms", "weight_terms",
                 "data_terms", "output_use", "review_reference",
                 "claims_qualified")

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX64 = re.compile(r"^(?=.*[1-9a-f])[0-9a-f]{64}$")
REQUEST_PATH = re.compile(r"^/attempt/[a-z0-9][a-z0-9._-]{0,63}/request\.json$")
RESULT_PATH = re.compile(r"^/attempt/[a-z0-9][a-z0-9._-]{0,63}/result\.json$")

PROFILE_PHRASES = (
    "Record version, install location and provenance",
    "clean checkout or extracted package",
    "one typical CLI/API use",
    "caller-owned inputs",
    "malformed inputs and missing optional selections",
    "Separate compile/build evidence, synthetic runtime evidence and "
    "measured workload support",
)

TOOL_REQUIREMENTS = (
    {
        "id": "TOOL-01",
        "requirement": "Record version, install location and provenance.",
        "status": "blocked",
        "evidence": (
            "The recorded CPython 3.11.5 / torch 2.14.1 / torchaudio 2.11.0 / "
            "SpeechBrain 1.0.3 runtime and the isolated overlay are absent from "
            "both probed interpreters; no install location or wheel set exists."),
    },
    {
        "id": "TOOL-02",
        "requirement": "Verify a clean checkout or extracted package.",
        "status": "not_run",
        "evidence": (
            "This is an evidence-only directory. No SDK package, wheel, "
            "extracted archive or clean-install fixture is built or installed."),
    },
    {
        "id": "TOOL-03",
        "requirement": "Exercise one typical CLI/API use.",
        "status": "synthetic_pass",
        "evidence": (
            "A synthetic request/result envelope exercises the documented "
            "adapter CLI shape (--request/--result, offline mode, caller-owned "
            "bytes, identity output, replay, reset and idempotent close). It "
            "does not import or execute torch or SpeechBrain."),
    },
    {
        "id": "TOOL-04",
        "requirement": "Verify caller-owned inputs.",
        "status": "synthetic_pass",
        "evidence": (
            "The synthetic envelope copies and validates caller-supplied "
            "float32 bytes, rejects a digest or byte-count mismatch, and never "
            "searches the filesystem or downloads an asset."),
    },
    {
        "id": "TOOL-05",
        "requirement": "Verify malformed inputs.",
        "status": "synthetic_pass",
        "evidence": (
            "Strict JSON, manifest and envelope rejection matrices fail closed "
            "on malformed, missing, extra, duplicate, aliased, nonfinite and "
            "out-of-range inputs without advancing state."),
    },
    {
        "id": "TOOL-06",
        "requirement": "Verify missing optional selections.",
        "status": "synthetic_pass",
        "evidence": (
            "Missing runtime, network, download, mode and asset selections are "
            "explicit rejections; no optional value is defaulted into an "
            "admissible run."),
    },
    {
        "id": "TOOL-07",
        "requirement": "Separate compile/build evidence.",
        "status": "not_run",
        "evidence": (
            "No build, link, CMake target, native runtime or packaging step is "
            "attempted or claimed."),
    },
    {
        "id": "TOOL-08",
        "requirement": "Separate synthetic runtime evidence.",
        "status": "not_run",
        "evidence": (
            "No synthetic *runtime* exists: the envelope proves protocol "
            "plumbing only. No tensor operation, model forward, checkpoint "
            "load or runtime import occurs."),
    },
    {
        "id": "TOOL-09",
        "requirement": "Separate measured workload support.",
        "status": "not_run",
        "evidence": (
            "No measured workload, host/device timing, resource, listening or "
            "benchmark result is produced. Historical RTF/RSS values are "
            "provenance only."),
    },
)

TOOL_EXPECTED_STATUS = {
    "TOOL-01": "blocked",
    "TOOL-02": "not_run",
    "TOOL-03": "synthetic_pass",
    "TOOL-04": "synthetic_pass",
    "TOOL-05": "synthetic_pass",
    "TOOL-06": "synthetic_pass",
    "TOOL-07": "not_run",
    "TOOL-08": "not_run",
    "TOOL-09": "not_run",
}

MODE_PLATFORM_ROWS = (
    {
        "id": "MP-01",
        "mode": "offline",
        "platform": "Darwin 27.2 arm64, Apple M1 CPU",
        "status": "provenance_only",
        "evidence": (
            "Both recorded adapter runs are offline whole-utterance CPU runs "
            "on one shared Apple M1 host. They are quoted from the pinned "
            "reports and were not reproduced."),
    },
    {
        "id": "MP-02",
        "mode": "streaming",
        "platform": "not_available",
        "status": "not_applicable",
        "evidence": (
            "Both pinned adapters declare modes=[offline] only and process one "
            "whole waveform per call. No streaming or chunked mode exists to "
            "measure."),
    },
    {
        "id": "MP-03",
        "mode": "offline",
        "platform": "target device and mobile",
        "status": "blocked",
        "evidence": (
            "No phone, NPU, GPU, callback-paced, thermal, battery or "
            "target-device measurement exists."),
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "adapter_sources_protocol_and_evidence_register",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The pinned project adapter sources, descriptors, runtime lock, "
            "adapter protocol and evaluation register: adapters/README.md, "
            "adapters/controls/run.py, the MetricGAN+ and SepFormer adapter "
            "directories and evaluation_records.md."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "pinned_pytorch_speechbrain_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A locked offline CPython 3.11.5 / torch 2.14.1 / torchaudio "
            "2.11.0 / SpeechBrain 1.0.3 / HyperPyYAML 1.2.3 environment with "
            "wheel names, byte counts, SHA-256 values, install location and an "
            "import/load digest."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "metricgan_checkpoint_assets",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact speechbrain/metricgan-plus-voicebank snapshot at "
            "revision be514d321f66b5352c5a8d59c44700f57aa8c8f5: "
            "enhance_model.ckpt, hyperparams.yaml and config.json with byte "
            "counts, SHA-256 values and artifact-specific terms review."),
        "revision": "be514d321f66b5352c5a8d59c44700f57aa8c8f5",
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "sepformer_checkpoint_assets",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact speechbrain/sepformer-dns4-16k-enhancement snapshot at "
            "revision e8c258546300102a240fa2595854d473cbfee49a: brain.ckpt, "
            "encoder.ckpt, masknet.ckpt, decoder.ckpt, config.json and "
            "hyperparams.yaml with byte counts, SHA-256 values and "
            "artifact-specific terms review."),
        "revision": "e8c258546300102a240fa2595854d473cbfee49a",
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_caller_input_fixture",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A rights-cleared, digest-pinned caller-owned input set with "
            "permission for evaluation and derived-output handling, plus the "
            "training-data terms for both checkpoints."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "reproduced_adapter_run_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A fresh offline run of both pinned adapters in the exact locked "
            "runtime with per-item input/output hashes, finite and "
            "length-preserving output checks, deterministic repeats, resource "
            "values and adverse/missing controls."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "provider_intake_and_public_surface",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A separate versioned, OFF-by-default developer tool or provider "
            "intake with clean-install proof, empty defaults, no registry or "
            "shared-build change and independent exact-head review after every "
            "other gate clears."),
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "linked_gates": ["RG-02"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "The exact PyTorch/SpeechBrain runtime is absent. Both probed "
            "interpreters (CPython 3.12.16 and 3.11.5) expose no torch, "
            "torchaudio, SpeechBrain or HyperPyYAML, the recorded "
            "data/envs/clearvoice environment is gone, and no wheel, lock "
            "install or import digest exists for the recorded CPython 3.11.5 / "
            "torch 2.14.1 / torchaudio 2.11.0 / SpeechBrain 1.0.3 stack."),
        "required_action": (
            "Supply a locked offline CPython 3.11.5 environment with torch "
            "2.14.1, torchaudio 2.11.0, SpeechBrain 1.0.3, HyperPyYAML 1.2.3 "
            "and the recorded overlay; include wheel names/versions/byte "
            "counts/SHA-256 values, the isolated install location, and a "
            "clean-room import plus checkpoint-load digest."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "linked_gates": ["RG-01", "RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "MetricGAN+ checkpoint bytes are absent. The pinned report records "
            "enhance_model.ckpt at 7,586,021 bytes and SHA-256 147bfb86..., "
            "hyperparams.yaml at 7bcc0835... and config.json at 18cb7139..., "
            "but no local file exists at any probed model path. The Apache-2.0 "
            "model-card line is not an artifact-specific clearance."),
        "required_action": (
            "Stage the exact revision be514d32... files with byte counts and "
            "matching SHA-256 values, a complete model card/license/notice "
            "bundle, an artifact-specific terms and training-data review, and "
            "a redistribution/product-use decision. No download is permitted "
            "inside this package."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "linked_gates": ["RG-01", "RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "SepFormer DNS4 checkpoint bytes are absent. The pinned lock "
            "records six files with SHA-256 values at revision e8c25854..., "
            "but no local file exists at any probed model path and the byte "
            "counts are not recorded in the lock."),
        "required_action": (
            "Stage the six exact revision e8c25854... files with byte counts "
            "and matching SHA-256 values, a complete model card/license/notice "
            "bundle, an artifact-specific terms and training-data review, and "
            "a redistribution/product-use decision."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "linked_gates": ["RG-04"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared caller input set is staged. The historical "
            "screens used the exploratory DNS2020 no-reverb 30-pair subset "
            "(manifests pinned in the reports), but the audio, its corpus "
            "terms and derived-output handling are not reviewed or present "
            "here. Checkpoint training-data terms are also unresolved."),
        "required_action": (
            "Provide a digest-pinned, rights-reviewed caller-owned input set "
            "with corpus, acquisition, evaluation, derived-output and "
            "redistribution decisions, plus checkpoint training-data terms "
            "and an attribution record."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "linked_gates": ["RG-05", "RG-06"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No adapter run is reproduced. The recorded 30-pair MetricGAN+ and "
            "SepFormer results cannot be re-executed without the missing "
            "runtime and checkpoint bytes; their numbers are quoted context "
            "only, and the SepFormer run used four intra-op threads rather "
            "than the one-thread reference policy."),
        "required_action": (
            "Run both pinned adapters offline in the exact runtime with one "
            "intra-op and one inter-op thread, deterministic algorithms and no "
            "network; record per-item input/output hashes, finite and "
            "length-preserving output checks, exact repeats, peak/RSS values, "
            "and negative/missing-runtime/malformed controls."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "linked_gates": ["RG-07", "RG-08"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No SDK adapter, provider intake or public surface exists. The "
            "recorded adapters are workspace research runners with global "
            "module state, and there is no mode/platform, target-device, "
            "callback, thermal, battery, listening or benchmark measurement."),
        "required_action": (
            "After the runtime, assets, input rights and reproduced-run gates "
            "clear, implement a separate versioned OFF-by-default developer "
            "tool/adapter with mode and platform measured separately, then "
            "complete provider intake and independent exact-head review."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "status": "blocked",
        "statement": (
            "The adapter sources, descriptors, runtime lock and protocol are "
            "pinned, but neither checkpoint's complete model card/license/"
            "notice bundle nor artifact-specific or training-data terms are "
            "staged or reviewed."),
        "reopen_condition": (
            "Stage both exact model revision archives with complete license, "
            "notice, model-card and training-data terms, then record an "
            "independent rights review."),
    },
    {
        "id": "RG-02",
        "title": "pinned_runtime_and_offline_install",
        "status": "blocked",
        "statement": (
            "No torch/torchaudio/SpeechBrain/HyperPyYAML runtime is installed "
            "or pinned by wheel digest in an approved environment."),
        "reopen_condition": (
            "Provide a locked offline CPython 3.11.5 environment with wheel "
            "hashes, install location and a clean-room import/load digest for "
            "the exact recorded versions."),
    },
    {
        "id": "RG-03",
        "title": "checkpoint_assets_and_per_file_digests",
        "status": "blocked",
        "statement": (
            "MetricGAN+ and SepFormer checkpoint bytes are absent; only "
            "documented SHA-256 values (and one byte count) exist."),
        "reopen_condition": (
            "Stage every checkpoint/config/hyperparams file for both exact "
            "revisions and verify each byte count and SHA-256 against the "
            "pinned lock/report."),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_caller_inputs",
        "status": "blocked",
        "statement": (
            "No rights-reviewed caller-owned evaluation input set or "
            "derived-output permission exists."),
        "reopen_condition": (
            "Freeze a permitted, digest-pinned input set with corpus, "
            "acquisition, evaluation, derived-output and redistribution "
            "decisions plus attribution."),
    },
    {
        "id": "RG-05",
        "title": "adapter_execution_and_output_validity",
        "status": "blocked",
        "statement": (
            "No real adapter inference, finite/length-preserving output check, "
            "deterministic repeat or resource measurement was performed."),
        "reopen_condition": (
            "Execute both adapters offline in the exact runtime and record "
            "per-item output hashes, finite/length preservation, exact repeats "
            "and peak/RSS values."),
    },
    {
        "id": "RG-06",
        "title": "tool_profile_against_real_runtime",
        "status": "blocked",
        "statement": (
            "The Tool profile is exercised only against a synthetic envelope; "
            "version/install provenance, clean-install, malformed handling and "
            "missing optional selections have not been demonstrated against a "
            "real PyTorch/SpeechBrain runtime."),
        "reopen_condition": (
            "Repeat every Tool-profile case against the installed runtime and "
            "both checkpoints, including malformed, missing and adverse "
            "controls, and record the results."),
    },
    {
        "id": "RG-07",
        "title": "mode_platform_timing_and_resources",
        "status": "blocked",
        "statement": (
            "Only offline whole-utterance CPU provenance exists for one shared "
            "host; no streaming mode, target device, callback, thermal, "
            "battery or energy measurement is available."),
        "reopen_condition": (
            "Measure offline and (if added) streaming modes separately on the "
            "intended platforms with p95/p99 timing, resources and pacing "
            "limits."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "statement": (
            "No registered SDK adapter/provider, descriptor, default, "
            "clean-install proof or independent review exists; installed v0 "
            "and the shared build remain untouched."),
        "reopen_condition": (
            "Open a separate versioned OFF-by-default tool/provider intake "
            "with clean-install proof, no shared default/build change and "
            "independent exact-head approval after all prior gates clear."),
    },
)

NON_CLAIMS = (
    "No PyTorch, torchaudio, SpeechBrain or HyperPyYAML module is imported, "
    "linked, installed or executed.",
    "No checkpoint, weight, config, hyperparams file or model cache is "
    "present, loaded, deserialized or reconstructed.",
    "No real audio, corpus, manifest payload or model output is read or "
    "produced.",
    "No adapter inference, quality, parity, speed, resource, listening, "
    "device or benchmark result is reproduced or claimed.",
    "The synthetic envelope is protocol plumbing only; it is not a runtime, "
    "a model, a checkpoint, a quality result or a qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build or "
    "CI change exists.",
    "Historical RTF, RSS and paired metric values are provenance only and are "
    "not promoted to evidence.",
)

REQUIRED_RESULTS = (
    "Exact runtime wheel set, byte counts, SHA-256 values and install location.",
    "Clean-room runtime import and checkpoint-load digest.",
    "MetricGAN+ and SepFormer file inventories with byte counts and SHA-256.",
    "Complete model-card, license, notice and training-data review for both.",
    "Rights-cleared, digest-pinned caller-owned evaluation inputs.",
    "Reproduced offline runs with finite/length-preserving outputs and repeats.",
    "Tool-profile cases repeated against the real runtime.",
    "Mode/platform timing and resource measurements made separately.",
    "Separate OFF-by-default provider intake and independent review.",
)

REOPENING_CONDITIONS = (
    "Pin and install the exact CPython 3.11.5 / torch 2.14.1 / torchaudio "
    "2.11.0 / SpeechBrain 1.0.3 runtime offline with wheel hashes.",
    "Stage both exact checkpoint revisions with per-file byte counts and "
    "SHA-256 values and clear their terms.",
    "Provide rights-cleared caller-owned inputs and derived-output permission.",
    "Reproduce both adapters with deterministic one-thread CPU execution and "
    "record finite, length-preserving outputs and controls.",
    "Apply the Tool profile again against the real runtime.",
    "Measure mode and platform separately, then open a separate "
    "OFF-by-default intake and independent review.",
)

PROTOCOL_SNIPPETS = {
    "adapters/README.md": (
        "--request REQUEST.json --result RESULT.json",
        "do not download assets",
        "deny-by-default/no-network profile",
        "validates result manifests",
    ),
    "research/voice-enhancement-20261101/agent-metricgan-eval/adapter.py": (
        "from speechbrain.inference.enhancement import SpectralMaskEnhancement",
        "kwargs['weights_only'] = True",
        "with torch.inference_mode():",
        "def process(request, row, source, root, chunks):",
        "protocol.main(process",
    ),
    "research/voice-enhancement-20261101/agent-sepformer-eval/adapter.py": (
        "from speechbrain.inference.separation import SepformerSeparation",
        "kwargs['weights_only'] = True",
        "with torch.inference_mode():",
        "def process(request, row, source, root, chunks):",
        "separate_batch",
    ),
}

ABSENCE_PROBES = (
    "data/envs/clearvoice",
    "data/envs/speechbrain",
    "data/models/speechbrain",
    "data/models/speechbrain/metricgan-plus-voicebank/enhance_model.ckpt",
    "data/models/speechbrain/sepformer-dns4-16k-enhancement/brain.ckpt",
    "research/voice-enhancement-20261101/agent-metricgan-eval/"
    "enhance_model.ckpt",
    "research/voice-enhancement-20261101/agent-metricgan-eval/"
    "hyperparams.yaml",
    "research/voice-enhancement-20261101/agent-sepformer-eval/brain.ckpt",
    "research/voice-enhancement-20261101/agent-sepformer-eval/encoder.ckpt",
    "research/voice-enhancement-20261101/agent-sepformer-eval/"
    "hyperparams.yaml",
    ".venv/lib/python3.11/site-packages/torch",
    ".venv/lib/python3.11/site-packages/speechbrain",
    ".venv/lib/python3.12/site-packages/torch",
    ".venv/lib/python3.12/site-packages/speechbrain",
    "data/checkouts/speechbrain",
    "data/manifests/speechbrain-runtime.lock",
)

WORKTREE_ABSENCE_PROBES = (
    "build/check-env/lib/python3.12/site-packages/torch",
    "build/check-env/lib/python3.12/site-packages/speechbrain",
    "build/all/speechbrain",
    "third_party/speechbrain",
)

HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--speechbrain--metricgan-plus-voicebank",
    "~/.cache/huggingface/hub/models--speechbrain--sepformer-dns4-16k-"
    "enhancement",
    "~/.pyenv/versions/3.11.5/lib/python3.11/site-packages/torch",
    "~/.pyenv/versions/3.12.16/lib/python3.12/site-packages/speechbrain",
)

HISTORICAL_RUNS = (
    {
        "adapter_id": METRICGAN_ID,
        "mode": "offline",
        "device": "cpu",
        "host": "Darwin 27.2 arm64 Apple M1",
        "valid_outputs": "30/30",
        "mean_delta_snr_db": "-10.505",
        "mean_delta_si_sdr_db": "-3.538",
        "mean_delta_stoi": "-0.00850",
        "mean_rtf": "0.00443",
        "peak_child_rss_bytes": 316047360,
        "intra_op_threads": None,
        "provenance_only": True,
        "reproduced_here": False,
    },
    {
        "adapter_id": SEPFORMER_ID,
        "mode": "offline",
        "device": "cpu",
        "host": "Darwin 27.2 arm64 Apple M1",
        "valid_outputs": "30/30",
        "mean_delta_snr_db": "-19.432",
        "mean_delta_si_sdr_db": "+8.525",
        "mean_delta_stoi": "+0.03313",
        "mean_rtf": "0.693",
        "peak_child_rss_bytes": 1894531072,
        "intra_op_threads": 4,
        "provenance_only": True,
        "reproduced_here": False,
    },
)


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
# Runtime readiness and source provenance
# --------------------------------------------------------------------------
def runtime_readiness() -> dict:
    modules: list[dict] = []
    for name in RUNTIME_MODULES:
        try:
            found = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            found = False
        modules.append({
            "module": name,
            "module_spec_found": found,
            "installed_version": None,
            "import_error": (None if found else
                             "ModuleNotFoundError: No module named '%s'" % name),
        })
    observed = platform.python_version()
    return {
        "blocked": True,
        "interpreter_required": REQUIRED_INTERPRETER,
        "interpreter_observed": observed,
        "interpreter_matches": observed == REQUIRED_INTERPRETER,
        "recorded_runtime": dict(RECORDED_RUNTIME),
        "runtime_overlay": [{"name": name, "version": version}
                            for name, version in RUNTIME_OVERLAY],
        "speechbrain_wheel_sha256": SPEECHBRAIN_WHEEL_SHA256,
        "modules": modules,
        "importable": False,
        "module_spec_found": any(row["module_spec_found"] for row in modules),
        "installed_version": None,
        "install_location": None,
        "exact_error": "ModuleNotFoundError: No module named 'torch'",
        "runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "historical_environment": "data/envs/clearvoice (absent)",
        "reopen_conditions": [
            "Pin wheel names, versions, byte counts and SHA-256 values for the "
            "recorded CPython 3.11.5 / torch 2.14.1 / torchaudio 2.11.0 / "
            "SpeechBrain 1.0.3 stack.",
            "Record the exact isolated install location and a clean-room "
            "import/load digest.",
            "Load both checkpoints offline with networking disabled.",
            "Record deterministic one-thread CPU repeats before any claim.",
        ],
    }


def source_presence() -> dict:
    profiles: dict[str, dict] = {}
    for identity in sorted(ADAPTER_PROFILES):
        profile = ADAPTER_PROFILES[identity]
        source_path = AUDIO_ROOT / profile["adapter_source"]["path"]
        descriptor_path = AUDIO_ROOT / profile["adapter_descriptor"]["path"]
        lock_path = AUDIO_ROOT / profile["runtime_lock"]["path"]
        rows: dict[str, dict] = {}
        for label, path, expected in (
                ("adapter_source", source_path,
                 profile["adapter_source"]["sha256"]),
                ("adapter_descriptor", descriptor_path,
                 profile["adapter_descriptor"]["sha256"]),
                ("runtime_lock", lock_path,
                 profile["runtime_lock"]["sha256"])):
            if not path.is_file():
                raise ValueError("adapter_source_missing:" + path.name)
            actual = sha256_file(path)
            if actual != expected:
                raise ValueError("adapter_source_digest_mismatch:" + path.name)
            rows[label] = {
                "path": str(path.relative_to(AUDIO_ROOT)),
                "sha256": expected,
                "byte_count": path.stat().st_size,
                "verified": True,
                "executed_here": False,
            }
        profiles[identity] = rows
    return {
        "adapter_sources_present": True,
        "protocol_source_present": True,
        "research_register_present": True,
        "adapter_sources_used_for": "static_provenance_only",
        "adapter_profiles": profiles,
        "runtime_present": False,
        "weights_present": False,
        "input_media_present": False,
        "exact_source_runtime_weights_conjunction_present": False,
        "runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "network_used": False,
    }


def protocol_snippet_check() -> dict:
    rows: dict[str, dict] = {}
    for relative, phrases in sorted(PROTOCOL_SNIPPETS.items()):
        path = AUDIO_ROOT / relative
        if not path.is_file():
            raise ValueError("protocol_source_missing:" + relative)
        text = path.read_text(encoding="utf-8")
        found = {phrase: (phrase in text) for phrase in phrases}
        missing = [phrase for phrase, present in found.items() if not present]
        if missing:
            raise ValueError("protocol_snippet_missing:" + missing[0])
        rows[relative] = {
            "sha256": sha256_file(path),
            "byte_count": path.stat().st_size,
            "snippets_required": len(phrases),
            "snippets_found": len(phrases),
            "verified": True,
        }
    return rows


# --------------------------------------------------------------------------
# Strict manifest admission (task-local; not an SDK or runtime contract)
# --------------------------------------------------------------------------
def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise AdmissionError(path + "_not_object")
    return value


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> dict:
    obj = _require_object(value, path)
    keys = tuple(sorted(obj))
    if keys != tuple(sorted(expected)):
        missing = sorted(set(expected) - set(obj))
        extra = sorted(set(obj) - set(expected))
        if missing:
            raise AdmissionError(path + "_missing_field:" + missing[0])
        raise AdmissionError(path + "_extra_field:" + extra[0])
    return obj


def _text(obj: dict, key: str, path: str, pattern: re.Pattern | None = None,
          allowed: tuple[str, ...] | None = None) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        raise AdmissionError(path + "_" + key + "_not_text")
    if allowed is not None and value not in allowed:
        raise AdmissionError(path + "_" + key + "_not_allowed")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise AdmissionError(path + "_" + key + "_invalid")
    return value


def _int_field(obj: dict, key: str, path: str, minimum: int,
               maximum: int) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError(path + "_" + key + "_not_int")
    if value < minimum or value > maximum:
        raise AdmissionError(path + "_" + key + "_out_of_range")
    return value


def _decimal_field(obj: dict, key: str, path: str, minimum: str,
                   maximum: str) -> Decimal:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise AdmissionError(path + "_" + key + "_not_decimal")
    if isinstance(value, float) and not math.isfinite(value):
        raise AdmissionError(path + "_" + key + "_nonfinite")
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise AdmissionError(path + "_" + key + "_not_decimal")
    if not number.is_finite():
        raise AdmissionError(path + "_" + key + "_nonfinite")
    if number < Decimal(minimum) or number > Decimal(maximum):
        raise AdmissionError(path + "_" + key + "_out_of_range")
    return number


def _bool_field(obj: dict, key: str, path: str,
                expected: bool | None = None) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise AdmissionError(path + "_" + key + "_not_bool")
    if expected is not None and value is not expected:
        raise AdmissionError(path + "_" + key + "_wrong_value")
    return value


def _hex_field(obj: dict, key: str, path: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise AdmissionError(path + "_" + key + "_not_sha256")
    return value


def validate_manifest(manifest: dict) -> None:
    """Validate one caller-supplied adapter-run manifest; mutate nothing."""
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root.get("schema_id") != ADMISSION_SCHEMA_ID:
        raise AdmissionError("manifest_schema_id")
    run_id = _text(root, "run_id", "manifest", SLUG)

    adapter = _exact_keys(root.get("adapter"), ADAPTER_FIELDS, "adapter")
    identity = _text(adapter, "identity", "adapter",
                     allowed=tuple(sorted(ADAPTER_PROFILES)))
    profile = ADAPTER_PROFILES[identity]
    if adapter.get("protocol") != PROTOCOL_ID:
        raise AdmissionError("adapter_protocol")
    if adapter.get("mode") not in RUN_MODES:
        raise AdmissionError("adapter_mode")
    if _hex_field(adapter, "adapter_sha256", "adapter") != \
            profile["adapter_source"]["sha256"]:
        raise AdmissionError("adapter_sha256_mismatch")
    if _hex_field(adapter, "descriptor_sha256", "adapter") != \
            profile["adapter_descriptor"]["sha256"]:
        raise AdmissionError("adapter_descriptor_sha256_mismatch")

    runtime = _exact_keys(root.get("runtime"), RUNTIME_FIELDS, "runtime")
    for key in ("python", "torch", "torchaudio", "speechbrain",
                "hyperpyyaml"):
        if _text(runtime, key, "runtime") != RECORDED_RUNTIME[key]:
            raise AdmissionError("runtime_" + key + "_mismatch")
    if runtime.get("device") != RECORDED_RUNTIME["device"]:
        raise AdmissionError("runtime_device")
    for key in ("intra_op_threads", "interop_op_threads"):
        if _int_field(runtime, key, "runtime", 1, 1) != \
                RECORDED_RUNTIME[key]:
            raise AdmissionError("runtime_" + key)
    for key in ("deterministic_algorithms", "offline"):
        if _bool_field(runtime, key, "runtime", True) is not True:
            raise AdmissionError("runtime_" + key)
    _text(runtime, "install_reference", "runtime")
    digests = _exact_keys(runtime.get("wheel_digests"), WHEEL_DIGEST_NAMES,
                          "runtime_wheel_digests")
    for name in WHEEL_DIGEST_NAMES:
        _hex_field(digests, name, "runtime_wheel_digests")
    if digests["speechbrain"] != SPEECHBRAIN_WHEEL_SHA256:
        raise AdmissionError("runtime_speechbrain_wheel_mismatch")

    command = _exact_keys(root.get("command"), COMMAND_FIELDS, "command")
    if command.get("cli") != PROTOCOL_ID:
        raise AdmissionError("command_cli")
    _text(command, "request_argument", "command", REQUEST_PATH)
    _text(command, "result_argument", "command", RESULT_PATH)
    if command.get("network") != "denied":
        raise AdmissionError("command_network")
    if command.get("downloads") != "denied":
        raise AdmissionError("command_downloads")

    assets = root.get("assets")
    if not isinstance(assets, list) or not assets:
        raise AdmissionError("assets_not_nonempty_list")
    expected_assets = profile["assets"]
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for index, raw in enumerate(assets):
        path = "assets[%d]" % index
        asset = _exact_keys(raw, ASSET_FIELDS, path)
        asset_id = _text(asset, "asset_id", path, SLUG)
        name = _text(asset, "name", path)
        if asset_id in seen_ids:
            raise AdmissionError("assets_duplicate_asset_id")
        if name in seen_names:
            raise AdmissionError("assets_duplicate_name")
        seen_ids.add(asset_id)
        seen_names.add(name)
        if name not in expected_assets:
            raise AdmissionError("assets_unknown_name")
        pinned = expected_assets[name]
        byte_count = _int_field(asset, "byte_count", path, 1,
                                MAX_ASSET_BYTES)
        if pinned["byte_count"] is not None and \
                byte_count != pinned["byte_count"]:
            raise AdmissionError("assets_byte_count_mismatch")
        if _hex_field(asset, "sha256", path) != pinned["sha256"]:
            raise AdmissionError("assets_sha256_mismatch")
        _hex_field(asset, "terms_sha256", path)
        if _bool_field(asset, "present_at_review", path, True) is not True:
            raise AdmissionError("assets_not_present")
    if seen_names != set(expected_assets):
        raise AdmissionError("assets_incomplete_set")

    input_row = _exact_keys(root.get("input"), INPUT_FIELDS, "input")
    if _int_field(input_row, "sample_rate_hz", "input", SAMPLE_RATE_HZ,
                  SAMPLE_RATE_HZ) != SAMPLE_RATE_HZ:
        raise AdmissionError("input_sample_rate_hz")
    if _int_field(input_row, "channels", "input", 1, 1) != 1:
        raise AdmissionError("input_channels")
    sample_count = _int_field(input_row, "sample_count", "input", 1,
                              MAX_SAMPLE_COUNT)
    if input_row.get("dtype") != "f32":
        raise AdmissionError("input_dtype")
    _hex_field(input_row, "sha256", "input")
    if _bool_field(input_row, "finite", "input", True) is not True:
        raise AdmissionError("input_nonfinite")
    _decimal_field(input_row, "peak", "input", "0", "1")

    output_row = _exact_keys(root.get("output"), OUTPUT_FIELDS, "output")
    if _int_field(output_row, "sample_count", "output", 1,
                  MAX_SAMPLE_COUNT) != sample_count:
        raise AdmissionError("output_length_mismatch")
    _hex_field(output_row, "sha256", "output")
    if _bool_field(output_row, "finite", "output", True) is not True:
        raise AdmissionError("output_nonfinite")
    _decimal_field(output_row, "peak", "output", "0", "1")
    if _int_field(output_row, "delay_compensation_samples", "output", 0,
                  0) != 0:
        raise AdmissionError("output_delay")

    controls = root.get("controls")
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise AdmissionError("controls_not_exact_list")
    kinds: list[str] = []
    control_ids: set[str] = set()
    for index, raw in enumerate(controls):
        path = "controls[%d]" % index
        control = _exact_keys(raw, CONTROL_FIELDS, path)
        control_id = _text(control, "id", path, SLUG)
        if control_id in control_ids:
            raise AdmissionError("controls_duplicate_id")
        control_ids.add(control_id)
        kind = _text(control, "kind", path, allowed=CONTROL_KINDS)
        kinds.append(kind)
    if sorted(kinds) != sorted(CONTROL_KINDS):
        raise AdmissionError("controls_kind_set")

    rights = _exact_keys(root.get("rights"), RIGHTS_FIELDS, "rights")
    for key in ("adapter_source_terms", "runtime_terms", "weight_terms",
                "data_terms", "output_use", "review_reference"):
        _text(rights, key, "rights")
    if _bool_field(rights, "claims_qualified", "rights", False) is not False:
        raise AdmissionError("rights_claims_qualified")

    if not isinstance(run_id, str):
        raise AdmissionError("manifest_run_id_not_text")


# --------------------------------------------------------------------------
# Synthetic protocol envelope (no runtime, no model, no audio)
# --------------------------------------------------------------------------
def synthetic_frame() -> list[float]:
    """Deterministic 160-sample float32 frame with binary-fraction values."""
    values: list[float] = []
    for index in range(FRAME_SAMPLES):
        integer = ((index * 37) % 201) - 100
        values.append(integer / 128.0)
    return values


def frame_bytes(values: list[float]) -> bytes:
    if len(values) != FRAME_SAMPLES:
        raise AdmissionError("frame_length")
    return struct.pack("<%df" % FRAME_SAMPLES, *values)


def frame_from_bytes(payload: bytes) -> list[float]:
    if len(payload) != FRAME_BYTES:
        raise AdmissionError("payload_byte_count")
    values = list(struct.unpack("<%df" % FRAME_SAMPLES, payload))
    if not all(math.isfinite(value) for value in values):
        raise AdmissionError("payload_nonfinite")
    return values


def _payload_from_hex(text: Any) -> bytes:
    if not isinstance(text, str) or len(text) != FRAME_BYTES * 2:
        raise AdmissionError("payload_hex_length")
    try:
        payload = bytes.fromhex(text)
    except ValueError:
        raise AdmissionError("payload_hex_invalid")
    if len(payload) != FRAME_BYTES:
        raise AdmissionError("payload_byte_count")
    return payload


def _request_input() -> dict:
    payload = frame_bytes(synthetic_frame())
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_count": FRAME_SAMPLES,
        "dtype": "f32",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
        "payload_hex": payload.hex(),
    }


def protocol_request() -> dict:
    return {
        "protocol": PROTOCOL_ID,
        "request_id": "synthetic-envelope-0001",
        "mode": "offline",
        "input": _request_input(),
        "options": {
            "network": "denied",
            "downloads": "denied",
            "writes": "attempt_only",
        },
    }


ENVELOPE_INPUT_FIELDS = ("sample_rate_hz", "channels", "sample_count",
                         "dtype", "sha256", "byte_count", "payload_hex")
ENVELOPE_OPTION_FIELDS = ("network", "downloads", "writes")
ENVELOPE_FIELDS = ("protocol", "request_id", "mode", "input", "options")


def validate_protocol_request(request: Any) -> bytes:
    root = _exact_keys(request, ENVELOPE_FIELDS, "request")
    if root.get("protocol") != PROTOCOL_ID:
        raise AdmissionError("envelope_protocol")
    _text(root, "request_id", "request", SLUG)
    if root.get("mode") not in RUN_MODES:
        raise AdmissionError("envelope_mode")
    input_row = _exact_keys(root.get("input"), ENVELOPE_INPUT_FIELDS,
                            "request_input")
    if input_row.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise AdmissionError("envelope_sample_rate_hz")
    if input_row.get("channels") != 1:
        raise AdmissionError("envelope_channels")
    if input_row.get("sample_count") != FRAME_SAMPLES:
        raise AdmissionError("envelope_sample_count")
    if input_row.get("dtype") != "f32":
        raise AdmissionError("envelope_dtype")
    byte_count = input_row.get("byte_count")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or \
            byte_count != FRAME_BYTES:
        raise AdmissionError("envelope_byte_count")
    payload = _payload_from_hex(input_row.get("payload_hex"))
    frame_from_bytes(payload)
    if input_row.get("sha256") != hashlib.sha256(payload).hexdigest():
        raise AdmissionError("envelope_sha256")
    options = _exact_keys(root.get("options"), ENVELOPE_OPTION_FIELDS,
                          "request_options")
    if options.get("network") != "denied":
        raise AdmissionError("envelope_network")
    if options.get("downloads") != "denied":
        raise AdmissionError("envelope_downloads")
    if options.get("writes") != "attempt_only":
        raise AdmissionError("envelope_writes")
    return payload


class SyntheticEnvelopeAdapter:
    """Protocol-envelope stand-in. Never imports or executes a runtime."""

    def __init__(self) -> None:
        self.closed = False
        self.call_count = 0

    def _ensure_open(self) -> None:
        if self.closed:
            raise AdmissionError("adapter_closed")

    def process(self, request: Any) -> dict:
        self._ensure_open()
        payload = validate_protocol_request(request)
        output_payload = bytes(bytearray(payload))
        self.call_count += 1
        return {
            "protocol": PROTOCOL_ID,
            "request_id": request["request_id"],
            "status": "ok",
            "call_index": self.call_count,
            "output": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "sample_count": FRAME_SAMPLES,
                "dtype": "f32",
                "sha256": hashlib.sha256(output_payload).hexdigest(),
                "byte_count": len(output_payload),
                "payload_hex": output_payload.hex(),
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
    adapter = SyntheticEnvelopeAdapter()
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
        row["protocol"] = "audioml-adapter/2"

    def mode_streaming(row):
        row["mode"] = "streaming"

    def rate_wrong(row):
        row["input"]["sample_rate_hz"] = 8000

    def channels_wrong(row):
        row["input"]["channels"] = 2

    def dtype_wrong(row):
        row["input"]["dtype"] = "f64"

    def sha_wrong(row):
        row["input"]["sha256"] = "1" * 64

    def nonfinite(row):
        payload = struct.pack("<%df" % FRAME_SAMPLES, *synthetic_frame())
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

    cases = (
        ("EV-01", delete_option),
        ("EV-02", network_allowed),
        ("EV-03", downloads_allowed),
        ("EV-04", writes_anywhere),
        ("EV-05", protocol_wrong),
        ("EV-06", mode_streaming),
        ("EV-07", rate_wrong),
        ("EV-08", channels_wrong),
        ("EV-09", dtype_wrong),
        ("EV-10", sha_wrong),
        ("EV-11", nonfinite),
        ("EV-12", byte_count_wrong),
        ("EV-13", extra_key),
        ("EV-14", payload_invalid),
        ("EV-15", sample_count_wrong),
    )
    return [_envelope_case(case_id, mutate) for case_id, mutate in cases]


def synthetic_envelope_probe() -> dict:
    """Execute the deterministic envelope only; no runtime or model."""
    request = protocol_request()
    payload = validate_protocol_request(copy.deepcopy(request))
    adapter = SyntheticEnvelopeAdapter()
    first = adapter.process(copy.deepcopy(request))
    second = adapter.process(copy.deepcopy(request))
    adapter.reset()
    replay = adapter.process(copy.deepcopy(request))
    adapter.close()
    adapter.close()
    lifecycle_rejected = False
    lifecycle_code = ""
    try:
        adapter.process(copy.deepcopy(request))
    except AdmissionError as error:
        lifecycle_rejected = True
        lifecycle_code = error.code
    first_payload = bytes.fromhex(first["output"]["payload_hex"])
    second_payload = bytes.fromhex(second["output"]["payload_hex"])
    replay_payload = bytes.fromhex(replay["output"]["payload_hex"])
    values = frame_from_bytes(first_payload)
    peak = max(abs(value) for value in values)
    cases = envelope_cases()
    return {
        "schema_id": ENVELOPE_SCHEMA_ID,
        "boundary": "synthetic_protocol_envelope_only_not_a_runtime",
        "request": request,
        "typical_api_use": {
            "status": "synthetic_pass",
            "calls": 3,
            "request_sha256": hashlib.sha256(payload).hexdigest(),
            "output_sha256": first["output"]["sha256"],
            "output_byte_count": first["output"]["byte_count"],
            "output_sample_count": first["output"]["sample_count"],
            "output_peak": _decimal_string(peak),
            "payload_prefix_hex": first_payload[:16].hex(),
            "identity_exact": first_payload == payload,
            "replay_identical": first_payload == second_payload,
            "reset_replay_identical": first_payload == replay_payload,
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
    payload = frame_bytes(synthetic_frame())
    profile = ADAPTER_PROFILES[METRICGAN_ID]
    assets = []
    for index, name in enumerate(sorted(profile["assets"]), start=1):
        pinned = profile["assets"][name]
        assets.append({
            "asset_id": "metricgan-asset-%02d" % index,
            "name": name,
            "byte_count": (pinned["byte_count"] if pinned["byte_count"]
                           is not None else 1024),
            "sha256": pinned["sha256"],
            "terms_sha256": ("%064x" % index),
            "present_at_review": True,
        })
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "run_id": "synthetic-run-0001",
        "adapter": {
            "identity": METRICGAN_ID,
            "protocol": PROTOCOL_ID,
            "mode": "offline",
            "adapter_sha256": profile["adapter_source"]["sha256"],
            "descriptor_sha256": profile["adapter_descriptor"]["sha256"],
        },
        "runtime": {
            "python": RECORDED_RUNTIME["python"],
            "torch": RECORDED_RUNTIME["torch"],
            "torchaudio": RECORDED_RUNTIME["torchaudio"],
            "speechbrain": RECORDED_RUNTIME["speechbrain"],
            "hyperpyyaml": RECORDED_RUNTIME["hyperpyyaml"],
            "device": RECORDED_RUNTIME["device"],
            "intra_op_threads": RECORDED_RUNTIME["intra_op_threads"],
            "interop_op_threads": RECORDED_RUNTIME["interop_op_threads"],
            "deterministic_algorithms":
                RECORDED_RUNTIME["deterministic_algorithms"],
            "offline": RECORDED_RUNTIME["offline"],
            "install_reference": "synthetic-schema-control-no-install",
            "wheel_digests": {
                "hyperpyyaml": "%064x" % 2,
                "speechbrain": SPEECHBRAIN_WHEEL_SHA256,
                "torch": "%064x" % 3,
                "torchaudio": "%064x" % 4,
            },
        },
        "command": {
            "cli": PROTOCOL_ID,
            "request_argument": "/attempt/synthetic-run-0001/request.json",
            "result_argument": "/attempt/synthetic-run-0001/result.json",
            "network": "denied",
            "downloads": "denied",
        },
        "assets": assets,
        "input": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_count": FRAME_SAMPLES,
            "dtype": "f32",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "finite": True,
            "peak": "0.78125",
        },
        "output": {
            "sample_count": FRAME_SAMPLES,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "finite": True,
            "peak": "0.78125",
            "delay_compensation_samples": 0,
        },
        "controls": [
            {"id": "control-candidate", "kind": "adapter_candidate"},
            {"id": "control-identity", "kind": "identity_passthrough"},
            {"id": "control-missing-runtime", "kind": "missing_runtime"},
        ],
        "rights": {
            "adapter_source_terms": "project Apache-2.0 evidence reference",
            "runtime_terms": "not_reviewed_synthetic_control",
            "weight_terms": "not_reviewed_synthetic_control",
            "data_terms": "synthetic_bytes_only_not_audio",
            "output_use": "synthetic_schema_control_only",
            "review_reference": "pending_task_local_schema_control",
            "claims_qualified": False,
        },
    }


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
        code = _normalise_parse_code(error)
        return {
            "id": case_id,
            "group": "document",
            "status": "rejected",
            "code": code,
            "qualifies": False,
            "state_unchanged": True,
        }
    raise AssertionError("parse case accepted: " + case_id)


def admission_cases() -> list[dict]:
    parse_cases = (
        _parse_case("DOC-01", '{"a":1,"a":2}'),
        _parse_case("DOC-02", '{"a":NaN}'),
        _parse_case("DOC-03", '{"a":Infinity}'),
        _parse_case("DOC-04", '[]'),
        _parse_case("DOC-05", '{"a":1} trailing'),
        _parse_case("DOC-06", '\ufeff{"a":1}'),
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

    def assets_mutate(fn):
        def mutate(row):
            fn(row["assets"])
        return mutate

    def asset_field(index, key, value):
        def mutate(row):
            row["assets"][index][key] = value
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
            "asset_id": "metricgan-extra",
            "name": "enhance_model.ckpt",
            "byte_count": 1,
            "sha256": "1" * 64,
            "terms_sha256": "2" * 64,
            "present_at_review": True,
        })

    def mixed_assets(rows):
        sep = ADAPTER_PROFILES[SEPFORMER_ID]["assets"]
        rows[:] = [
            {
                "asset_id": "sep-asset-%02d" % index,
                "name": name,
                "byte_count": 1024,
                "sha256": pinned["sha256"],
                "terms_sha256": "%064x" % index,
                "present_at_review": True,
            }
            for index, (name, pinned) in
            enumerate(sorted(sep.items()), start=1)
        ]

    def controls_empty(row):
        row["controls"] = []

    def controls_duplicate(row):
        row["controls"][1]["kind"] = row["controls"][0]["kind"]

    def controls_unknown(row):
        row["controls"][0]["kind"] = "runtime_candidate"

    def controls_extra(row):
        row["controls"][0]["extra"] = 1

    def controls_empty_id(row):
        row["controls"][0]["id"] = ""

    def output_peak_nan(row):
        row["output"]["peak"] = float("nan")

    def input_peak_inf(row):
        row["input"]["peak"] = float("inf")

    cases = parse_cases + (
        _manifest_case("ST-01", "structure", drop("runtime")),
        _manifest_case("ST-02", "structure", set_key("extra", 1)),
        _manifest_case("ST-03", "structure", lambda row: row.clear()),
        _manifest_case("ST-04", "structure", set_key("schema_id", "x")),
        _manifest_case("ST-05", "structure", set_key("run_id", "Bad Run")),
        _manifest_case("ST-06", "structure", set_key("run_id", 7)),
        _manifest_case("ST-07", "structure", set_key("adapter", [])),
        _manifest_case("ST-08", "structure", set_key("rights", "x")),
        _manifest_case("AD-01", "adapter", nested(
            "adapter", "identity", "SpeechBrain-9.9.9-Unknown")),
        _manifest_case("AD-02", "adapter", nested(
            "adapter", "protocol", "audioml-adapter/2")),
        _manifest_case("AD-03", "adapter", nested(
            "adapter", "mode", "streaming")),
        _manifest_case("AD-04", "adapter", nested(
            "adapter", "adapter_sha256", "1" * 64)),
        _manifest_case("AD-05", "adapter", nested(
            "adapter", "descriptor_sha256", "2" * 64)),
        _manifest_case("AD-06", "adapter", extra_nested(
            "adapter", "extra", 1)),
        _manifest_case("AD-07", "adapter", drop_nested(
            "adapter", "mode")),
        _manifest_case("AD-08", "adapter", nested(
            "adapter", "identity", 7)),
        _manifest_case("RT-01", "runtime", nested("runtime", "python", "3.12.16")),
        _manifest_case("RT-02", "runtime", nested("runtime", "torch", "2.2.2")),
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
        _manifest_case("RT-13", "runtime", nested("runtime", "wheel_digests",
                                                  {"torch": "x"})),
        _manifest_case("RT-14", "runtime", extra_nested("runtime", "extra", 1)),
        _manifest_case("CM-01", "command", nested(
            "command", "cli", "audioml-adapter/2")),
        _manifest_case("CM-02", "command", nested(
            "command", "request_argument", "/tmp/request.json")),
        _manifest_case("CM-03", "command", nested(
            "command", "result_argument", "/attempt/x/out.json")),
        _manifest_case("CM-04", "command", nested(
            "command", "network", "allowed")),
        _manifest_case("CM-05", "command", nested(
            "command", "downloads", "permitted")),
        _manifest_case("CM-06", "command", extra_nested("command", "extra", 1)),
        _manifest_case("AS-01", "assets", assets_mutate(lambda rows: rows.clear())),
        _manifest_case("AS-02", "assets", assets_mutate(duplicate_asset_id)),
        _manifest_case("AS-03", "assets", assets_mutate(unknown_asset_name)),
        _manifest_case("AS-04", "assets", assets_mutate(
            pop_asset("config.json"))),
        _manifest_case("AS-05", "assets", asset_field(
            1, "byte_count", 7586020)),
        _manifest_case("AS-06", "assets", asset_field(0, "sha256", "1" * 64)),
        _manifest_case("AS-07", "assets", asset_field(
            0, "terms_sha256", "not-a-digest")),
        _manifest_case("AS-08", "assets", asset_field(
            0, "present_at_review", False)),
        _manifest_case("AS-09", "assets", assets_mutate(extra_asset)),
        _manifest_case("AS-10", "assets", assets_mutate(mixed_assets)),
        _manifest_case("IN-01", "input", nested(
            "input", "sample_rate_hz", 8000)),
        _manifest_case("IN-02", "input", nested("input", "channels", 2)),
        _manifest_case("IN-03", "input", nested("input", "sample_count", 0)),
        _manifest_case("IN-04", "input", nested(
            "input", "sample_count", MAX_SAMPLE_COUNT + 1)),
        _manifest_case("IN-05", "input", nested("input", "dtype", "f64")),
        _manifest_case("IN-06", "input", nested("input", "sha256", "x")),
        _manifest_case("IN-07", "input", nested("input", "finite", False)),
        _manifest_case("IN-08", "input", nested("input", "peak", "1.5")),
        _manifest_case("IN-09", "input", extra_nested("input", "extra", 1)),
        _manifest_case("OUT-01", "output", nested(
            "output", "sample_count", FRAME_SAMPLES - 1)),
        _manifest_case("OUT-02", "output", nested("output", "sha256", "x")),
        _manifest_case("OUT-03", "output", nested("output", "finite", False)),
        _manifest_case("OUT-04", "output", nested("output", "peak", "-0.1")),
        _manifest_case("OUT-05", "output", nested(
            "output", "delay_compensation_samples", 1)),
        _manifest_case("OUT-06", "output", extra_nested("output", "extra", 1)),
        _manifest_case("OUT-07", "output", drop_nested("output", "peak")),
        _manifest_case("RI-01", "rights", nested(
            "rights", "claims_qualified", True)),
        _manifest_case("RI-02", "rights", nested("rights", "runtime_terms", "")),
        _manifest_case("RI-03", "rights", nested(
            "rights", "review_reference", "")),
        _manifest_case("RI-04", "rights", nested("rights", "data_terms", "")),
        _manifest_case("RI-05", "rights", nested(
            "rights", "adapter_source_terms", "")),
        _manifest_case("RI-06", "rights", nested("rights", "output_use", "")),
        _manifest_case("RI-07", "rights", extra_nested("rights", "extra", 1)),
        _manifest_case("CT-01", "controls", controls_empty),
        _manifest_case("CT-02", "controls", controls_duplicate),
        _manifest_case("CT-03", "controls", controls_unknown),
        _manifest_case("CT-04", "controls", controls_extra),
        _manifest_case("CT-05", "controls", lambda row: row.update(
            controls=[])),
        _manifest_case("CT-06", "controls", controls_empty_id),
        _manifest_case("NF-01", "nonfinite", output_peak_nan),
        _manifest_case("NF-02", "nonfinite", input_peak_inf),
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
        "adapter_execution_result": False,
        "output_validity_result": False,
        "tool_profile_result": False,
        "mode_platform_result": False,
        "device_timing_result": False,
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
            "adapter_executed": False,
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
            "frame_samples": FRAME_SAMPLES,
            "changed": False,
        },
        "required_artifacts": [dict(item) for item in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "release_gates": gates,
        "tool_requirements": [dict(item) for item in TOOL_REQUIREMENTS],
        "mode_platform_rows": [dict(item) for item in MODE_PLATFORM_ROWS],
        "adapter_profiles": copy.deepcopy(ADAPTER_PROFILES),
        "recorded_runtime": dict(RECORDED_RUNTIME),
        "runtime_overlay": [{"name": name, "version": version}
                            for name, version in RUNTIME_OVERLAY],
        "speechbrain_wheel_sha256": SPEECHBRAIN_WHEEL_SHA256,
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "adapter_fields": list(ADAPTER_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "command_fields": list(COMMAND_FIELDS),
            "asset_fields": list(ASSET_FIELDS),
            "input_fields": list(INPUT_FIELDS),
            "output_fields": list(OUTPUT_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "run_modes": list(RUN_MODES),
            "exact_protocol": PROTOCOL_ID,
            "exact_interpreter": REQUIRED_INTERPRETER,
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "adapter_source_terms_reviewed": False,
            "upstream_license_reviewed": False,
            "weight_terms_reviewed": False,
            "training_data_terms_reviewed": False,
            "input_terms_reviewed": False,
        },
    }


def historical_execution() -> dict:
    return {
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "why_not_reproduced": [
            "The exact torch/torchaudio/SpeechBrain runtime is absent.",
            "Both checkpoint byte sets are absent.",
            "No rights-cleared caller input set is present.",
            "The recorded SepFormer run used four intra-op threads, not the "
            "one-thread reference policy.",
            "No target-device, listening or benchmark run exists.",
        ],
        "runs": [dict(row) for row in HISTORICAL_RUNS],
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
    tool_rows = contract["tool_requirements"]
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
        "adapter_profiles": contract["adapter_profiles"],
        "recorded_runtime": contract["recorded_runtime"],
        "runtime_overlay": contract["runtime_overlay"],
        "speechbrain_wheel_sha256": contract["speechbrain_wheel_sha256"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "tool_profile": {
            "profile": PROFILE,
            "label": PROFILE_LABEL,
            "requirements": tool_rows,
            "summary": {
                "requirement_count": len(tool_rows),
                "blocked_count": sum(1 for row in tool_rows
                                     if row["status"] == "blocked"),
                "not_run_count": sum(1 for row in tool_rows
                                     if row["status"] == "not_run"),
                "synthetic_pass_count": sum(1 for row in tool_rows
                                            if row["status"] ==
                                            "synthetic_pass"),
                "real_runtime_verified": False,
                "measured_workload_present": False,
                "tool_profile_satisfied": False,
            },
        },
        "mode_platform": {
            "rows": contract["mode_platform_rows"],
            "offline_mode_present": True,
            "streaming_mode_present": False,
            "modes_measured": [],
            "platforms_measured": [],
            "separate_mode_platform_measurement": "blocked",
            "device_timing_measured": False,
        },
        "runtime_readiness": runtime_readiness(),
        "source_presence": source_presence(),
        "protocol_source_checks": protocol_snippet_check(),
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
    tools = contract.get("tool_requirements", [])
    if len(tools) != len(TOOL_REQUIREMENTS):
        raise ValueError("contract_tool_count")
    for row in tools:
        if row.get("status") not in ("blocked", "not_run", "synthetic_pass"):
            raise ValueError("contract_tool_status")
    flags = contract.get("qualification", {})
    if flags.get("not_qualified") is not True \
            or flags.get("all_release_gates_blocked") is not True \
            or flags.get("missing_result_promoted") is not False \
            or flags.get("release_claim") is not False:
        raise ValueError("contract_qualification_flags")
