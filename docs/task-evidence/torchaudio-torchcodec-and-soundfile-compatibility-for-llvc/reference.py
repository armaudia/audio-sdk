# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the LLVC audio-I/O shim task.

This module is NOT TorchAudio, TorchCodec, SoundFile or LLVC. It contains no
runtime import, wheel, checkpoint, real corpus audio, model output or network
access. The pinned LLVC source checkout and the local evaluation wrapper
(``scripts/run_llvc_eval.py``) are present, but the exact playback stack they
need -- CPython 3.11.5, torch 2.15.0 CPU, torchaudio 2.11.1 CPU, the TorchCodec
build that torchaudio 2.11.1 requires and soundfile 0.12.1 -- is absent and was
never pinned by wheel name, byte count or SHA-256.

The module therefore builds a bounded blocker report:

* strict request validation with fail-closed rejection of missing, invalid,
  nonfinite, out-of-range and unsupported-pin inputs;
* bounded read-only probes of the exact runtime, known interpreters and
  workspace paths;
* static source checks of the pinned LLVC calls and the pinned evaluation
  wrapper's four compatibility overrides;
* a standard-library model of the wrapper's declared WAV contract
  (``sf.read(..., dtype="float32", always_2d=True)`` then transpose to
  channels-first, and ``sf.write`` from a channels-first array) with exact
  synthetic fixtures, quantization bounds, clipping counts and malformed-WAV
  rejections -- labelled harness evidence, not a runtime substitute;
* exact source-reported timing arithmetic kept separate from measurement;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json``.

No result here qualifies the task, the runtime, the shim or LLVC.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import struct
import wave
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

TASK = "SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC"
COMPONENT = "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc"
TITLE = "TorchAudio, TorchCodec and SoundFile compatibility for LLVC"
MODE = "implementation"
BRANCH = (
    "swarm/SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC")
BASE_COMMIT = "8bd03e2d9d08d550bb4b2ac28425c71eaf8a0ba9"
TASK_PREFIX = (
    "docs/task-evidence/"
    "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc/")
WRITE_SCOPE = TASK_PREFIX + " only"

SCHEMA_ID = (
    "audio-sdk/"
    "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc/0.1")
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "tool"
PROFILE_LABEL = "Tool"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FRAME_MS = 10.0
MAX_ABS_SAMPLE = 1.0
PCM16_FULL_SCALE = 32768.0
PCM16_MAX = 32767
PCM16_MIN = -32768

SOURCE_REVISION = "1627c5d358cf9bb2b92b0ccc513d8b36807c923d"
SOURCE_REPOSITORY = "KoeAI/LLVC"
SOURCE_LICENSE = "MIT"

RECORDED_RUNTIME = {
    "python": "3.11.5",
    "torch": "2.15.0",
    "torchaudio": "2.11.1",
    "torchcodec": None,
    "soundfile_requirements_pin": "0.12.1",
    "soundfile_observed_unqualified": "0.14.0",
    "speechbrain": "1.0.3",
    "auraloss": "0.4.0",
    "device": "cpu",
    "mps_available": False,
    "host": "MacBook Air M1, 8 GB unified memory, macOS 27.2",
    "environment": ".venv-eval (absent)",
    "lockfile": None,
    "wheel_digests": None,
}

RUNTIME_REQUIRED = (
    "CPython 3.11.5",
    "torch 2.15.0 CPU-only wheel",
    "torchaudio 2.11.1 CPU-only wheel",
    "the TorchCodec build required by torchaudio 2.11.1 (exact version not "
    "recorded locally)",
    "soundfile 0.12.1 wheel (upstream requirements.txt pin)",
    "SpeechBrain 1.0.3",
    "Auraloss 0.4.0",
    "a hash-pinned .venv-eval lockfile and wheel set",
)

RUNTIME_MODULES = (
    "torch", "torchaudio", "torchcodec", "soundfile", "speechbrain",
    "auraloss", "numpy", "scipy",
)
EXACT_MODULES = ("torchaudio", "torchcodec", "soundfile")

HISTORICAL_RTF = 0.123
HISTORICAL_E2E_MS = 120.785
HISTORICAL_AVG_INFER_MS = 106.0
HISTORICAL_COLD_RUN_S = 78.836
HISTORICAL_WER = 0.0
HISTORICAL_RTF_SLOWDOWN = 8.1

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
EVAL_ROOT = WORKSPACE / "research/voice-conversion-eval-20261101"
LLVC_ROOT = EVAL_ROOT / "repos/llvc"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py":
        "d268eb6dca48f88ae03802efd566f7053ac375be82555bd3dac343d750a5488c",
    "research/voice-conversion-eval-20261101/repos/llvc/LICENSE":
        "718657c20ba7035b25bb447d80a53304115b44fea7e684df2a1ca240555eae4b",
    "research/voice-conversion-eval-20261101/repos/llvc/infer.py":
        "88c47703bcd52e70b8d45887828353be7b8b742fe3d08f81448808ce3b06934b",
    "research/voice-conversion-eval-20261101/repos/llvc/model.py":
        "b01626c0b0def1aac3c07c597a15529d9eac98f7bd17b241c1a08b88b92dc4b9",
    "research/voice-conversion-eval-20261101/repos/llvc/requirements.txt":
        "e2063e6455751a18895c5daa628a8dc728853f8dd5444c0ce766526bf0418825",
    "research/voice-conversion-eval-20261101/repos/llvc/experiments/llvc/"
    "config.json":
        "b5e488ada5267a8c09dd843a547fef8f95e39a49764b99f9bccf6a39be2f256c",
    "research/voice-conversion-eval-20261101/results/llvc_asr.json":
        "2d8f31e91ea06efed6611a0aa41edf2babb08625a2da22fe30f4333554115c41",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    # Merged sibling evidence boundaries only; never reused as a result.
    "docs/task-evidence/llvc/README.md":
        "f6d663bc171026181107a6e9ddcf1356fa9eb9e2fd16625267b35a5bc3bda717",
    "docs/task-evidence/llvc/report.json":
        "22d30a3c4f70143ba38f099019c3fcc6b123f4f4f3120f6ee73932d82fed342f",
    "docs/task-evidence/pytorch-and-speechbrain-adapters/report.json":
        "7754c9647064f89c7d831fd9bd7d3a9f3560c51c00a22bfc8dc9da3aa59e349c",
    "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/report.json":
        "091b57f366c1c5d4d395f955da7d237848bdc7564c970e1a087d423fb702f225",
}

# Stable linked-row identity only. Status, owner, depends_on, review, handoff,
# timestamps, dispatch priority, history and claim are excluded and never gated.
EXPECTED_LINK = {
    "task_id": TASK,
    "title": TITLE,
    "mode": MODE,
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

TOOL_ID = "llvc_torchaudio_compat"
OPERATIONS = ("load", "save", "list_audio_backends", "round_trip")
LIFECYCLES = ("prepared", "processing")
TORCHCODEC_STATUS = "required_unpinned"
REQUEST_KEYS = frozenset({
    "tool", "operation", "python_version", "torch_version",
    "torchaudio_version", "soundfile_version", "torchcodec_status",
    "sample_rate_hz", "channels", "frame_samples", "samples", "dtype",
    "source", "lifecycle",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth",
    ".ckpt", ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip",
    ".tar", ".gz", ".whl",
}

SHIM_WRAPPER_PATH = "research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py"
INFE_R_PATH = "research/voice-conversion-eval-20261101/repos/llvc/infer.py"

SHIM_CHECKS = (
    {
        "id": "legacy_backend_symbol",
        "needle": 'torchaudio.list_audio_backends = lambda: ["soundfile"]',
        "purpose": "Restore the backend-list symbol removed in torchaudio 2.11.",
    },
    {
        "id": "load_float32_always_2d",
        "needle": 'sf.read(path, dtype="float32", always_2d=True)',
        "purpose": "Read caller WAV as float32 in (samples, channels) form.",
    },
    {
        "id": "load_channel_transpose",
        "needle": "torch.from_numpy(samples.T.copy())",
        "purpose": "Return channels-first (channels, samples) torch tensor.",
    },
    {
        "id": "save_channel_transpose",
        "needle": "sf.write(path, np.asarray(values).T, sample_rate)",
        "purpose": "Write channels-first waveform as interleaved WAV.",
    },
)

UPSTREAM_CHECKS = (
    {"id": "upstream_load", "needle": "audio, sr = torchaudio.load(audio_path)"},
    {"id": "upstream_save",
     "needle": "torchaudio.save(audio_path, audio, sample_rate)"},
    {"id": "upstream_resample",
     "needle":
     "audio = torchaudio.transforms.Resample(sr, sample_rate)(audio)"},
)

API_SURFACE = (
    {
        "api": "torchaudio.list_audio_backends",
        "state_in_2_11": "source_reported_removed",
        "shim": 'lambda: ["soundfile"]',
        "executed_here": False,
    },
    {
        "api": "torchaudio.load",
        "state_in_2_11": "source_reported_requires_torchcodec",
        "shim": ('sf.read(dtype="float32", always_2d=True) -> '
                 "torch.from_numpy(samples.T.copy())"),
        "executed_here": False,
    },
    {
        "api": "torchaudio.save",
        "state_in_2_11": "source_reported_requires_torchcodec",
        "shim": "sf.write(path, np.asarray(values).T, sample_rate)",
        "executed_here": False,
    },
    {
        "api": "torchaudio.transforms.Resample",
        "state_in_2_11": "not_reported_changed_but_unverified",
        "shim": "not overridden; relies on torchaudio internals",
        "executed_here": False,
    },
)

GATES = (
    {
        "id": "RG-01",
        "title": "exact_runtime_artifact_pins",
        "statement": (
            "The recorded CPython 3.11.5 / torch 2.15.0 / torchaudio 2.11.1 / "
            "SoundFile 0.12.1 stack is absent. No torchaudio or TorchCodec "
            "wheel exists locally, the TorchCodec version required by "
            "torchaudio 2.11.1 is unrecorded, and no wheel byte count or "
            "SHA-256 is pinned."),
        "reopen_condition": (
            "Stage every exact wheel (CPython 3.11.5, CPU, target platform) "
            "with file name, byte count and SHA-256, then record the install "
            "location and a clean-room import digest."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-02",
        "title": "licence_notice_and_libsndfile_review",
        "statement": (
            "Torch/TorchAudio/TorchCodec wheel licence and notice terms, "
            "SoundFile's BSD-3-Clause terms and the separate libsndfile terms "
            "for any bundled native library are not reviewed. No "
            "redistribution decision for wheel bytes, native libraries or "
            "derived WAV output is recorded."),
        "reopen_condition": (
            "Record the wheel licence/notice bundle, bundled native-library "
            "terms (including libsndfile), and an explicit redistribution/use "
            "decision for the runtime and any generated audio."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-03",
        "title": "clean_runtime_build_install_parity",
        "statement": (
            "There is no lockfile, wheel set, clean environment, install "
            "record or import/version parity check for the historical "
            "``.venv-eval`` stack. The environment was removed."),
        "reopen_condition": (
            "Create a frozen offline environment from the staged wheels, "
            "install it in a clean prefix, and prove interpreter, package and "
            "native-library versions match the recorded stack."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-04",
        "title": "shim_api_semantics_parity",
        "statement": (
            "The four wrapper overrides and three upstream TorchAudio calls "
            "are only text-checked. No real ``list_audio_backends``, "
            "``load``, ``save`` or ``Resample`` call was executed, and no "
            "signature, dtype, shape, backend or TorchCodec behaviour was "
            "observed."),
        "reopen_condition": (
            "Execute each API and override against the exact runtime with "
            "caller-owned fixtures and record signatures, dtypes, shapes, "
            "exceptions and output hashes."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-05",
        "title": "pinned_io_fixture_parity",
        "statement": (
            "Only a standard-library model of the declared WAV contract "
            "exists. No real SoundFile read/write, TorchAudio Transpose, "
            "default WAV subtype or libsndfile conversion was exercised, and "
            "no rights-cleared caller-owned WAV fixture is staged."),
        "reopen_condition": (
            "Stage a rights-cleared caller-owned WAV set and prove byte-level "
            "and sample-level parity for the real shim, including subtype, "
            "clipping and channel order."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-06",
        "title": "adverse_malformed_nonfinite_runtime_behaviour",
        "statement": (
            "Malformed, missing, nonfinite and out-of-range cases are rejected "
            "only by the stdlib request validator and WAV model. The real "
            "runtime's exceptions, partial writes, backend errors and "
            "nonfinite propagation are unmeasured."),
        "reopen_condition": (
            "Run the same adverse matrix against the exact runtime, record "
            "exception types/messages, process state, file effects and "
            "nonfinite handling."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-07",
        "title": "source_timing_and_deadline_impact",
        "statement": (
            "The historical source-reported RTF 0.123 and 120.785 ms "
            "end-to-end estimate are provenance only. The shim's file-level "
            "load/save overhead, import time, cold start and per-chunk "
            "deadline impact were not measured here."),
        "reopen_condition": (
            "Measure import, cold start, per-file I/O and per-chunk deadline "
            "behaviour on the exact runtime and target host, separately from "
            "model compute."),
        "status": "blocked",
        "qualifies": False,
    },
    {
        "id": "RG-08",
        "title": "tool_intake_optional_packaging_review_release",
        "statement": (
            "No versioned OFF-by-default developer tool, optional package, "
            "provider intake, public-surface decision, independent exact-head "
            "review or release approval exists."),
        "reopen_condition": (
            "Ship a separate versioned OFF-by-default optional tool or "
            "adapter, complete Tool-profile verification, then obtain "
            "independent exact-head review and release approval."),
        "status": "blocked",
        "qualifies": False,
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_runtime_absent_and_unpinned",
    "artifact": (
        "The exact LLVC audio-I/O stack: CPython 3.11.5, torch 2.15.0 CPU, "
        "torchaudio 2.11.1 CPU, the TorchCodec build required by torchaudio "
        "2.11.1, soundfile 0.12.1 and the removed .venv-eval lock."),
    "present": {
        "source": "present_pinned",
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "source_license": SOURCE_LICENSE,
        "shim_wrapper": "present_pinned",
        "partial_unqualified": [
            "torch 2.15.0 in an unrelated playback-speed virtualenv",
            "soundfile 0.14.0 in an unrelated pyenv 3.12.16 and the same "
            "playback-speed virtualenv",
            "numpy 2.5.4 in the unrelated pyenv 3.12.16",
        ],
    },
    "missing": {
        "torchaudio": {
            "version": "2.11.1",
            "status": "absent",
            "sha256": None,
            "byte_count": None,
        },
        "torchcodec": {
            "version": None,
            "status": "absent_and_version_unrecorded",
            "sha256": None,
            "byte_count": None,
        },
        "soundfile": {
            "version": "0.12.1",
            "status": "absent",
            "sha256": None,
            "byte_count": None,
            "observed_unqualified": "0.14.0",
        },
        "speechbrain": {"version": "1.0.3", "status": "absent"},
        "auraloss": {"version": "0.4.0", "status": "absent"},
        "venv": {
            "path": ".venv-eval",
            "status": "absent",
            "lockfile": None,
            "runtime_digest": None,
        },
    },
    "exact_error": (
        "ModuleNotFoundError: No module named 'torchaudio' in the required "
        "CPython 3.11.5 interpreter; torchcodec, soundfile, SpeechBrain and "
        "Auraloss are likewise absent from that interpreter."),
    "expected_license": (
        "Apache-2.0 for this evidence package. Torch/TorchAudio/TorchCodec "
        "wheels carry PyTorch BSD-style terms; SoundFile metadata declares "
        "BSD-3-Clause and its libsndfile dependency carries separate terms. "
        "No wheel licence or notice review is recorded."),
    "rights_requirement": (
        "A recorded wheel licence/notice review, a libsndfile and native "
        "library redistribution decision, approval to install and execute the "
        "runtime, and a rights-cleared caller-owned WAV fixture with recorded "
        "consent (where applicable) and an explicit derived-output and "
        "redistribution decision are required before any reproduction, "
        "optional tool or release claim."),
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "not_attempted": [
        "no package installation or download",
        "no wheel, native library or runtime reconstruction",
        "no fabricated TorchCodec version or digest",
        "no copied upstream source, test audio or licence text",
        "no real SoundFile, TorchAudio or LLVC execution",
    ],
    "reopen": (
        "Stage the exact wheels with byte counts and SHA-256, record the "
        "TorchCodec version and native-library terms, install offline in a "
        "clean environment, reproduce the pinned I/O and timing checks with a "
        "rights-cleared fixture, and obtain independent exact-head review."),
}

NON_CLAIMS = (
    "No TorchAudio, TorchCodec, SoundFile, torch or LLVC runtime is included, "
    "installed, imported or executed.",
    "No wheel, native library, checkpoint, weight, corpus or model output is "
    "included.",
    "No compatibility shim result, API parity or byte-level parity is claimed.",
    "No installed v0, public API, C ABI, descriptor, registry or default "
    "change is made.",
    "No provider is registered or enabled by default.",
    "No device timing, callback, memory, listening, benchmark or release "
    "claim is made.",
    "No missing, rejected, synthetic or historical result qualifies the task.",
    "Historical RTF, WER and latency values remain source-reported provenance.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only the task-local evidence directory is written.",
    "The reference is a stdlib evidence builder, not the audio-I/O runtime.",
    "The WAV contract model is synthetic harness evidence, not SoundFile.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed.",
)

TOOL_REQUIREMENTS = (
    {
        "id": "TOOL-01",
        "requirement": "Record version, install location and provenance.",
        "status": "blocked",
        "evidence": (
            "The recorded CPython 3.11.5 / torch 2.15.0 / torchaudio 2.11.1 / "
            "soundfile 0.12.1 stack and .venv-eval are absent; only unrelated "
            "torch 2.15.0 and soundfile 0.14.0 installations were found."),
    },
    {
        "id": "TOOL-02",
        "requirement": "Verify a clean checkout or extracted package.",
        "status": "not_run",
        "evidence": (
            "This is an evidence-only directory. No wheel, package, extracted "
            "archive or clean-install fixture is built, installed or opened."),
    },
    {
        "id": "TOOL-03",
        "requirement": "Exercise one typical CLI/API use.",
        "status": "synthetic_pass",
        "evidence": (
            "A stdlib model exercises the wrapper's declared load/save data "
            "path on generated 16 kHz WAV bytes: float32, always_2d, "
            "channels-first transpose and interleaved write. It never imports "
            "or executes the real runtime."),
    },
    {
        "id": "TOOL-04",
        "requirement": "Verify caller-owned inputs.",
        "status": "synthetic_pass",
        "evidence": (
            "The model copies caller-shaped sample lists, validates finite "
            "mono 16 kHz float32 geometry and never searches for or downloads "
            "an asset. It is not a real caller-owned fixture."),
    },
    {
        "id": "TOOL-05",
        "requirement": "Verify malformed inputs.",
        "status": "synthetic_pass",
        "evidence": (
            "Strict JSON, request and WAV rejection matrices fail closed on "
            "duplicate, missing, extra, nonfinite, out-of-range, truncated, "
            "wrong-width, empty and multi-channel cases."),
    },
    {
        "id": "TOOL-06",
        "requirement": "Verify missing optional selections.",
        "status": "synthetic_pass",
        "evidence": (
            "Missing runtime, missing TorchCodec, missing SoundFile, wrong "
            "versions, wrong operation and closed lifecycle are explicit "
            "rejections; no value is defaulted into an admissible run."),
    },
    {
        "id": "TOOL-07",
        "requirement": "Separate compile/build evidence.",
        "status": "not_run",
        "evidence": (
            "No build, link, CMake target, native extension or packaging step "
            "is attempted or claimed."),
    },
    {
        "id": "TOOL-08",
        "requirement": "Separate synthetic runtime evidence.",
        "status": "not_run",
        "evidence": (
            "The WAV model proves declared I/O plumbing only. No tensor "
            "operation, SoundFile call, TorchCodec backend, import or model "
            "forward occurs."),
    },
    {
        "id": "TOOL-09",
        "requirement": "Measured workload support.",
        "status": "not_run",
        "evidence": (
            "No host/device timing, resource, callback, memory, listening or "
            "benchmark result is collected."),
    },
)

REQUIRED_RESULTS = {
    "exact_wheel_set_version_hashes_and_install": "blocked_runtime_absent",
    "clean_install_import_and_version_parity": "blocked_runtime_absent",
    "list_audio_backends_parity": "blocked_runtime_absent",
    "load_float32_always_2d_transpose_parity": "blocked_runtime_absent",
    "save_transpose_subtype_parity": "blocked_runtime_absent",
    "torchcodec_version_and_backend_parity": "blocked_version_unrecorded",
    "caller_owned_wav_fixture_parity": "blocked_no_rights_cleared_fixture",
    "malformed_missing_nonfinite_runtime_behaviour": "partial_stdlib_only",
    "source_timing_and_deadline_impact": "blocked_not_measured",
    "licence_notice_and_libsndfile_review": "blocked_not_reviewed",
    "independent_review_and_release": "blocked_not_reviewed",
    "candidate_output": "blocked_runtime_absent",
}

REOPENING_CONDITIONS = (
    "Pin every exact wheel with file name, byte count and SHA-256, including "
    "the TorchCodec version required by torchaudio 2.11.1.",
    "Record wheel licence/notice terms and the separate libsndfile/native "
    "library redistribution decision.",
    "Install the frozen stack offline in a clean prefix and record an "
    "import/version/native-library digest.",
    "Stage a rights-cleared caller-owned WAV fixture and approve derived "
    "output use.",
    "Execute the four shim overrides and three upstream TorchAudio calls, "
    "including malformed, missing, nonfinite and subtype cases.",
    "Measure import, cold-start, per-file I/O and per-chunk deadline impact, "
    "then apply the Tool profile and obtain independent exact-head review.",
)

DISPOSITION = (
    "Caller-supplied runtime compatibility blocker: the pinned LLVC source and "
    "the local evaluation wrapper are present, but the exact TorchAudio 2.11.1 "
    "/ TorchCodec / SoundFile 0.12.1 runtime is absent and unpinned. No shim, "
    "I/O parity, timing, benchmark or release result is claimed.")

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "float32",
    "frame_samples": FRAME_SAMPLES,
    "changed": False,
}

SOURCE_EVIDENCE_STATEMENTS = (
    "research/voice-conversion-eval-20261101/README.md records the LLVC run "
    "with PyTorch 2.15.0 / TorchAudio 2.11.1 CPU, notes that TorchAudio 2.11 "
    "removed list_audio_backends and its load now requires TorchCodec, and "
    "states that the evaluation wrapper supplied a local soundfile I/O shim "
    "and legacy backend-list symbol without changing upstream files.",
    "research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py pins the "
    "actual four-line compatibility wrapper: the legacy backend list, a "
    "soundfile float32 always_2d load, a channels-first tensor transpose and "
    "an interleaved soundfile save.",
    "research/voice-conversion-eval-20261101/repos/llvc/infer.py pins the "
    "upstream calls that need the shim: torchaudio.load, "
    "torchaudio.transforms.Resample and torchaudio.save.",
    "research/voice-conversion-eval-20261101/repos/llvc/requirements.txt pins "
    "soundfile==0.12.1; the evaluation environment's resolved version and "
    "the required TorchCodec version were not recorded.",
    "plan/INVENTORY.json assigns the Tool verification profile to "
    "'torchaudio-torchcodec-and-soundfile-compatibility-for-llvc' and asks "
    "for pinned I/O and compatibility shims in optional tooling with source "
    "timing checks.",
    "The merged llvc evidence package records that the checkpoint and the "
    "historical evaluation runtime are absent; this package neither reuses "
    "nor upgrades that blocker.",
)


class EvidenceError(ValueError):
    """Base error with a stable machine-readable code."""

    code = "EVIDENCE_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class JsonError(EvidenceError):
    code = "INVALID_JSON"


class WavContractError(EvidenceError):
    code = "INVALID_WAV"


class RuntimeAbsent(EvidenceError):
    code = "RUNTIME_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("INVALID_JSON: " + str(error), "INVALID_JSON")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _r(value: float, places: int = 9) -> float:
    return round(float(value), places)


def sample_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


def _require_int(value: Any, code: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def _validate_sample_list(samples: Any, expected: int) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if len(samples) != expected:
        raise InputError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("NONFINITE_SAMPLE: " + str(index), "NONFINITE")
        if abs(number) > MAX_ABS_SAMPLE:
            raise InputError("SAMPLE_OUT_OF_RANGE: " + str(index),
                             "OUT_OF_RANGE")
        result.append(number)
    return result


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
    if request["tool"] != TOOL_ID:
        raise ConfigError("UNKNOWN_TOOL", "UNKNOWN_TOOL")
    operation = request["operation"]
    if operation not in OPERATIONS:
        raise ConfigError("UNKNOWN_OPERATION", "UNKNOWN_OPERATION")
    pins = (
        ("python_version", "3.11.5"),
        ("torch_version", "2.15.0"),
        ("torchaudio_version", "2.11.1"),
        ("soundfile_version", "0.12.1"),
        ("torchcodec_status", TORCHCODEC_STATUS),
        ("dtype", "float32"),
        ("source", "caller_owned"),
    )
    for key, expected in pins:
        if request[key] != expected:
            raise ConfigError("UNSUPPORTED_PIN: " + key,
                              "UNSUPPORTED_PIN_" + key.upper())
    if _require_int(request["sample_rate_hz"], "WRONG_RATE") != SAMPLE_RATE_HZ:
        raise ConfigError("WRONG_RATE", "WRONG_RATE")
    if _require_int(request["channels"], "WRONG_CHANNELS") != CHANNELS:
        raise ConfigError("WRONG_CHANNELS", "WRONG_CHANNELS")
    if _require_int(request["frame_samples"], "WRONG_FRAME") != FRAME_SAMPLES:
        raise ConfigError("WRONG_FRAME", "WRONG_FRAME")
    samples = _validate_sample_list(request["samples"], FRAME_SAMPLES)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    return {
        "tool": TOOL_ID,
        "operation": operation,
        "python_version": "3.11.5",
        "torch_version": "2.15.0",
        "torchaudio_version": "2.11.1",
        "soundfile_version": "0.12.1",
        "torchcodec_status": TORCHCODEC_STATUS,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "samples": tuple(samples),
        "dtype": "float32",
        "source": "caller_owned",
        "lifecycle": lifecycle,
    }


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise RuntimeAbsent(
        "RUNTIME_ABSENT: " + validated["tool"] + " requires torchaudio 2.11.1 "
        "and the matching TorchCodec build, which are absent; no shim call is "
        "performed", "RUNTIME_ABSENT")


def _base_request() -> Dict[str, Any]:
    return {
        "tool": TOOL_ID,
        "operation": "load",
        "python_version": "3.11.5",
        "torch_version": "2.15.0",
        "torchaudio_version": "2.11.1",
        "soundfile_version": "0.12.1",
        "torchcodec_status": TORCHCODEC_STATUS,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "dtype": "float32",
        "source": "caller_owned",
        "lifecycle": "prepared",
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    def with_samples(samples):
        return variant(samples=samples)

    short = [0.0] * (FRAME_SAMPLES - 1)
    nan_samples = [0.0] * FRAME_SAMPLES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * FRAME_SAMPLES
    inf_samples[9] = float("inf")
    return (
        ("unknown_tool", variant(tool="llvc_runtime")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "torchcodec_status"}),
        ("wrong_python", variant(python_version="3.12.16")),
        ("wrong_torch", variant(torch_version="2.14.1")),
        ("wrong_torchaudio", variant(torchaudio_version="2.11.0")),
        ("wrong_soundfile", variant(soundfile_version="0.14.0")),
        ("torchcodec_claimed_present", variant(torchcodec_status="present")),
        ("unknown_operation", variant(operation="stream")),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("wrong_dtype", variant(dtype="float64")),
        ("wrong_source", variant(source="downloaded")),
        ("short_samples", with_samples(short)),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
        ("out_of_range", with_samples([1.5] * FRAME_SAMPLES)),
        ("bool_sample", with_samples([True] + [0.0] * (FRAME_SAMPLES - 1))),
        ("string_sample", with_samples(["0.0"] + [0.0] * (FRAME_SAMPLES - 1))),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("request_not_object", "not-an-object"),
    )


def _adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, request in _adverse_request_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_request(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
        "note": ("Invalid requests are rejected before any runtime call; no "
                 "metrics exist."),
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            strict_json_loads(text)
            accepted = True
        except JsonError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "runtime_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _float_to_pcm16(value: Any) -> Tuple[int, bool]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WavContractError("NON_NUMERIC_SAMPLE", "INVALID_SAMPLE_TYPE")
    number = float(value)
    if not math.isfinite(number):
        raise WavContractError("NONFINITE_SAMPLE", "NONFINITE")
    clipped = min(1.0, max(-1.0, number))
    quantum = int(round(clipped * PCM16_FULL_SCALE))
    limited = quantum > PCM16_MAX or quantum < PCM16_MIN
    quantum = max(PCM16_MIN, min(PCM16_MAX, quantum))
    return quantum, (clipped != number) or limited


def encode_wav_pcm16(channels: Sequence[Sequence[Any]],
                     sample_rate_hz: int) -> Tuple[bytes, int]:
    """Model ``sf.write`` default WAV output for a channels-first waveform."""
    if not isinstance(sample_rate_hz, int) or isinstance(sample_rate_hz, bool) \
            or sample_rate_hz <= 0:
        raise WavContractError("INVALID_RATE", "INVALID_RATE")
    if not isinstance(channels, (list, tuple)) or not channels:
        raise WavContractError("EMPTY_CHANNELS", "EMPTY_CHANNELS")
    channel_count = len(channels)
    if channel_count not in (1, 2):
        raise WavContractError("UNSUPPORTED_CHANNELS", "UNSUPPORTED_CHANNELS")
    lengths = {len(channel) for channel in channels}
    if len(lengths) != 1:
        raise WavContractError("RAGGED_CHANNELS", "RAGGED_CHANNELS")
    sample_count = lengths.pop()
    if sample_count <= 0:
        raise WavContractError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    frames = bytearray()
    clipped = 0
    for index in range(sample_count):
        for channel in channels:
            quantum, was_clipped = _float_to_pcm16(channel[index])
            clipped += int(was_clipped)
            frames += struct.pack("<h", quantum)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(channel_count)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate_hz)
        handle.setnframes(sample_count)
        handle.writeframes(bytes(frames))
    return buffer.getvalue(), clipped


def decode_wav_float32(payload: bytes) -> Dict[str, Any]:
    """Model ``sf.read(dtype='float32', always_2d=True)`` plus ``.T``."""
    if not isinstance(payload, (bytes, bytearray)) or not payload:
        raise WavContractError("EMPTY_PAYLOAD", "EMPTY_PAYLOAD")
    if len(payload) < 12 or payload[:4] != b"RIFF" or payload[8:12] != b"WAVE":
        raise WavContractError("BAD_RIFF_HEADER", "BAD_RIFF_HEADER")
    try:
        with wave.open(io.BytesIO(bytes(payload)), "rb") as handle:
            channel_count = handle.getnchannels()
            sample_width = handle.getsampwidth()
            sample_rate_hz = handle.getframerate()
            sample_count = handle.getnframes()
            compression = handle.getcomptype()
            frames = handle.readframes(sample_count)
    except (wave.Error, EOFError, struct.error) as error:
        raise WavContractError("UNREADABLE_WAV: " + str(error),
                               "UNREADABLE_WAV")
    if compression != "NONE":
        raise WavContractError("COMPRESSED_WAV", "COMPRESSED_WAV")
    if sample_width != 2:
        raise WavContractError("UNSUPPORTED_SAMPLE_WIDTH",
                               "UNSUPPORTED_SAMPLE_WIDTH")
    if channel_count not in (1, 2):
        raise WavContractError("UNSUPPORTED_CHANNELS", "UNSUPPORTED_CHANNELS")
    if sample_rate_hz <= 0:
        raise WavContractError("INVALID_RATE", "INVALID_RATE")
    if sample_count <= 0:
        raise WavContractError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    expected = sample_count * channel_count * 2
    if len(frames) != expected:
        raise WavContractError("TRUNCATED_FRAMES", "TRUNCATED_FRAMES")
    values = struct.unpack("<" + "h" * (sample_count * channel_count), frames)
    channels: List[List[float]] = [[] for _ in range(channel_count)]
    for index in range(sample_count):
        for channel in range(channel_count):
            channels[channel].append(
                values[index * channel_count + channel] / PCM16_FULL_SCALE)
    return {
        "sample_rate_hz": sample_rate_hz,
        "channels": channel_count,
        "sample_count": sample_count,
        "samples": tuple(tuple(channel) for channel in channels),
        "dtype": "float32-model",
    }


def _stimulus(name: str) -> Tuple[Tuple[float, ...], ...]:
    length = FRAME_SAMPLES
    if name == "silence":
        return ((0.0,) * length,)
    if name == "impulse":
        values = [0.0] * length
        values[80] = 0.5
        return (tuple(values),)
    if name == "full_scale":
        return (tuple(1.0 if index % 2 == 0 else -1.0
                      for index in range(length)),)
    if name == "ramp":
        return (tuple((index / float(length - 1)) * 0.9
                      for index in range(length)),)
    if name == "stereo":
        left = tuple((index / float(length - 1)) * 0.8
                     for index in range(length))
        right = tuple(-0.5 * (index / float(length - 1))
                      for index in range(length))
        return (left, right)
    raise ConfigError("unknown stimulus", "INVALID_STIMULUS")


def _model_case(name: str) -> Dict[str, Any]:
    channels = _stimulus(name)
    encoded, clipped = encode_wav_pcm16(channels, SAMPLE_RATE_HZ)
    decoded = decode_wav_float32(encoded)
    decoded_channels = decoded["samples"]
    max_error = 0.0
    for channel_index, source in enumerate(channels):
        decoded_channel = decoded_channels[channel_index]
        for index, value in enumerate(source):
            clipped_value = min(1.0, max(-1.0, float(value)))
            max_error = max(
                max_error, abs(decoded_channel[index] - clipped_value))
    reencoded, _ = encode_wav_pcm16(decoded_channels, SAMPLE_RATE_HZ)
    flat = tuple(value for channel in decoded_channels for value in channel)
    return {
        "name": name,
        "channel_count": len(channels),
        "sample_count": len(channels[0]),
        "byte_count": len(encoded),
        "encoded_sha256": sha256_bytes(encoded),
        "decoded_sample_digest": sample_digest(flat),
        "peak_abs": _r(peak_abs(flat)),
        "rms": _r(rms(flat)),
        "clipped_count": clipped,
        "max_abs_quantization_error": _r(max_error),
        "quantization_bound": _r(1.0 / PCM16_FULL_SCALE),
        "exact_sample_count": (
            decoded["sample_count"] == len(channels[0]) and
            decoded["channels"] == len(channels)),
        "channel_orientation_ok": all(
            max(abs(decoded_channels[channel][index] -
                    min(1.0, max(-1.0, float(value))))
                for index, value in enumerate(channels[channel]))
            <= 1.0 / PCM16_FULL_SCALE
            for channel in range(len(channels))),
        "roundtrip_byte_identical": reencoded == encoded,
        "header_ok": (encoded[:4] == b"RIFF" and
                      encoded[8:12] == b"WAVE"),
    }


def _wav_bytes(channel_count: int, sample_width: int, frame_count: int,
               sample_rate_hz: int = SAMPLE_RATE_HZ) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(channel_count)
        handle.setsampwidth(sample_width)
        handle.setframerate(sample_rate_hz)
        handle.setnframes(frame_count)
        handle.writeframes(b"\x00" * frame_count * channel_count *
                           sample_width)
    return buffer.getvalue()


def _wav_rejection_cases() -> Dict[str, Any]:
    specs: List[Tuple[str, Any]] = [
        ("truncated_riff",
         lambda: decode_wav_float32(b"RIFF\x04\x00\x00\x00WAVE")),
        ("bad_magic",
         lambda: decode_wav_float32(b"RIFX\x00\x00\x00\x00WAVEfmt ")),
        ("not_a_wav", lambda: decode_wav_float32(b"not a wav payload")),
        ("pcm8", lambda: decode_wav_float32(_wav_bytes(1, 1, 8))),
        ("pcm24", lambda: decode_wav_float32(_wav_bytes(1, 3, 8))),
        ("empty_frames", lambda: decode_wav_float32(_wav_bytes(1, 2, 0))),
        ("three_channels",
         lambda: decode_wav_float32(_wav_bytes(3, 2, 8))),
        ("zero_rate",
         lambda: decode_wav_float32(_wav_bytes(1, 2, 8, 0))),
        ("encode_nonfinite_nan",
         lambda: encode_wav_pcm16(((float("nan"),),), SAMPLE_RATE_HZ)),
        ("encode_nonfinite_inf",
         lambda: encode_wav_pcm16(((float("inf"),),), SAMPLE_RATE_HZ)),
        ("encode_non_numeric",
         lambda: encode_wav_pcm16((("0.0",),), SAMPLE_RATE_HZ)),
        ("encode_ragged",
         lambda: encode_wav_pcm16(((0.0,), (0.0, 0.0)), SAMPLE_RATE_HZ)),
        ("encode_three_channels",
         lambda: encode_wav_pcm16(((0.0,), (0.0,), (0.0,)), SAMPLE_RATE_HZ)),
        ("encode_zero_rate",
         lambda: encode_wav_pcm16(((0.0,),), 0)),
    ]
    cases: List[Dict[str, Any]] = []
    for name, factory in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            factory()
            accepted = True
        except WavContractError as exception:
            error = exception.code
        except (wave.Error, struct.error, EOFError, ValueError) as exception:
            error = "UNREADABLE_WAV"
            del exception
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "cases": cases,
    }


def wav_contract_probe() -> Dict[str, Any]:
    cases = [_model_case(name) for name in
             ("silence", "impulse", "full_scale", "ramp", "stereo")]
    rejection = _wav_rejection_cases()
    silence = encode_wav_pcm16(_stimulus("silence"), SAMPLE_RATE_HZ)[0]
    replay = encode_wav_pcm16(_stimulus("silence"), SAMPLE_RATE_HZ)[0]
    decoded_once = decode_wav_float32(silence)["samples"]
    decoded_twice = decode_wav_float32(silence)["samples"]
    return {
        "purpose": (
            "Standard-library model of the pinned wrapper's declared WAV "
            "contract only; not SoundFile, TorchAudio or TorchCodec and not a "
            "candidate result."),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "cases": cases,
        "rejections": rejection,
        "identity_control": {
            "encode_byte_identical": silence == replay,
            "decode_digest_identical": decoded_once == decoded_twice,
            "digest": sample_digest(
                tuple(value for channel in decoded_once for value in channel)),
        },
        "all_sample_counts_exact": all(case["exact_sample_count"]
                                       for case in cases),
        "all_channel_orientations_ok": all(case["channel_orientation_ok"]
                                           for case in cases),
        "all_roundtrips_byte_identical": all(
            case["roundtrip_byte_identical"] for case in cases),
        "all_quantization_within_bound": all(
            case["max_abs_quantization_error"] <= case["quantization_bound"]
            for case in cases),
        "all_rejections_closed": rejection["all_rejected"],
        "real_soundfile_used": False,
        "real_torchaudio_used": False,
        "candidate_processing": False,
    }


def _module_spec_found(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _site_packages_snapshot(label: str, path: Path) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {
        "id": label,
        "present": path.is_dir(),
        "packages": {},
    }
    if not path.is_dir():
        return snapshot
    for name in RUNTIME_MODULES:
        entries: List[Dict[str, Any]] = []
        for dist_info in sorted(path.glob(name + "-*.dist-info")):
            version = None
            metadata = dist_info / "METADATA"
            if metadata.is_file():
                for line in metadata.read_text(
                        encoding="utf-8", errors="replace").splitlines():
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        break
            entries.append({"dist_info": dist_info.name,
                            "version": version})
        snapshot["packages"][name] = {
            "dist_info": entries,
            "module_dir": (path / name).is_dir(),
        }
    return snapshot


def absence_probe() -> Dict[str, Any]:
    candidates = (
        ("evaluation_venv", EVAL_ROOT / ".venv-eval"),
        ("evaluation_lockfile", EVAL_ROOT / "requirements.lock"),
        ("evaluation_pyvenv", EVAL_ROOT / ".venv-eval/pyvenv.cfg"),
        ("llvc_data_env", WORKSPACE / "data/envs/llvc"),
        ("llvc_models", LLVC_ROOT / "llvc_models"),
        ("workspace_lockfile", WORKSPACE / "requirements.lock"),
    )
    rows: List[Dict[str, Any]] = []
    for name, path in candidates:
        rows.append({"id": name, "present": path.exists()})
    found = [row["id"] for row in rows if row["present"]]
    exact_found = [name for name in found
                   if name not in ("workspace_lockfile",)]
    return {
        "candidates": rows,
        "found": found,
        "exact_runtime_artifacts_found": exact_found,
        "all_exact_runtime_artifacts_absent": not exact_found,
        "note": (
            "Bounded fixed-path checks only. No cache, archive or installed "
            "package is opened, downloaded or reconstructed."),
    }


def runtime_readiness() -> Dict[str, Any]:
    modules = []
    for name in RUNTIME_MODULES:
        found = _module_spec_found(name)
        modules.append({
            "module": name,
            "module_spec_found": found,
            "import_error": None if found else (
                "ModuleNotFoundError: No module named '" + name + "'"),
            "installed_version": None,
        })
    pyenv_site = Path.home() / ".pyenv/versions/3.12.16/lib/python3.12/site-packages"
    playback_site = (
        WORKSPACE / "cpp-library/pipeline-validation/playback-speed/.venv/"
        "lib/python3.11/site-packages")
    snapshots = (
        _site_packages_snapshot("pyenv:3.12.16", pyenv_site),
        _site_packages_snapshot("workspace:playback-speed-venv",
                                playback_site),
    )
    partial: List[Dict[str, Any]] = []
    for snapshot in snapshots:
        for name, entry in snapshot["packages"].items():
            for row in entry["dist_info"]:
                partial.append({
                    "interpreter": snapshot["id"],
                    "package": name,
                    "dist_info": row["dist_info"],
                    "version": row["version"],
                    "qualified": False,
                })
    availability = {name: any(
        row["package"] == name for row in partial) for name in RUNTIME_MODULES}
    interpreter_observed = platform.python_version()
    interpreter_matches = interpreter_observed == "3.11.5"
    exact_present = (
        interpreter_matches and
        availability.get("torchaudio") is True and
        availability.get("torchcodec") is True and
        availability.get("soundfile") is True and
        (EVAL_ROOT / ".venv-eval").is_dir() and
        (EVAL_ROOT / "requirements.lock").is_file()
    )
    return {
        "status": ("runtime_present_unqualified" if exact_present
                   else "blocked_runtime_absent_unpinned"),
        "blocked": not exact_present,
        "exact_runtime_present": exact_present,
        "pinned": False,
        "interpreter_observed": interpreter_observed,
        "interpreter_required": "3.11.5",
        "interpreter_matches": interpreter_matches,
        "runtime_imported": False,
        "model_executed": False,
        "install_location": None,
        "installed_version": None,
        "module_specs": modules,
        "partial_installations": partial,
        "package_availability_any_interpreter": availability,
        "records_runtime": dict(RECORDED_RUNTIME),
        "required": list(RUNTIME_REQUIRED),
        "exact_error": (
            "RUNTIME_ABSENT: no torchaudio 2.11.1, TorchCodec, soundfile "
            "0.12.1, SpeechBrain 1.0.3 or Auraloss 0.4.0 in the required "
            "CPython 3.11.5 interpreter; .venv-eval is absent."),
        "note": (
            "Only importlib.util.find_spec and dist-info metadata reads are "
            "used. Nothing is imported, installed or executed."),
    }


def shim_source_probe() -> Dict[str, Any]:
    wrapper = WORKSPACE / SHIM_WRAPPER_PATH
    upstream = WORKSPACE / INFE_R_PATH
    checks: List[Dict[str, Any]] = []
    if wrapper.is_file():
        text = wrapper.read_text(encoding="utf-8")
        for check in SHIM_CHECKS:
            count = text.count(check["needle"])
            checks.append({
                "id": check["id"],
                "needle": check["needle"],
                "purpose": check["purpose"],
                "count": count,
                "present": count == 1,
            })
        wrapper_digest = sha256_file(wrapper)
        line_count = len(text.splitlines())
    else:
        wrapper_digest = None
        line_count = 0
    upstream_checks: List[Dict[str, Any]] = []
    if upstream.is_file():
        upstream_text = upstream.read_text(encoding="utf-8")
        for check in UPSTREAM_CHECKS:
            count = upstream_text.count(check["needle"])
            upstream_checks.append({
                "id": check["id"],
                "needle": check["needle"],
                "count": count,
                "present": count == 1,
            })
    all_checks = checks + upstream_checks
    status = ("pinned_source_checks_pass"
              if all_checks and all(item["present"] for item in all_checks)
              else "source_check_failed")
    return {
        "status": status,
        "wrapper_path": SHIM_WRAPPER_PATH,
        "wrapper_sha256": wrapper_digest,
        "wrapper_line_count": line_count,
        "checks": checks,
        "upstream_checks": upstream_checks,
        "executed": False,
        "note": (
            "Exact text checks of the pinned sources only. No Python source "
            "is imported, evaluated or executed."),
    }


def historical_timing() -> Dict[str, Any]:
    config = strict_json_loads(
        (LLVC_ROOT / "experiments/llvc/config.json").read_text(
            encoding="utf-8"))
    params = config.get("model_params", {})
    data = config.get("data", {})
    lookahead = _require_int(params.get("L"), "CONFIG_INVALID")
    dec_chunk = _require_int(params.get("dec_chunk_size"), "CONFIG_INVALID")
    sample_rate = _require_int(data.get("sr"), "CONFIG_INVALID")
    if sample_rate != SAMPLE_RATE_HZ:
        raise ConfigError("config rate mismatch", "CONFIG_INVALID")
    chunk_samples = lookahead * dec_chunk
    chunk_ms = chunk_samples * 1000.0 / sample_rate
    algorithmic_samples = 2 * lookahead + chunk_samples
    algorithmic_ms = algorithmic_samples * 1000.0 / sample_rate
    asr = strict_json_loads(
        (EVAL_ROOT / "results/llvc_asr.json").read_text(encoding="utf-8"))
    duration_seconds = float(asr["duration_seconds"])
    source_samples = int(round(duration_seconds * sample_rate))
    chunk_count = (source_samples + chunk_samples - 1) // chunk_samples
    average_from_rtf_ms = chunk_ms / HISTORICAL_RTF
    e2e_from_rtf_ms = algorithmic_ms + average_from_rtf_ms
    return {
        "status": "source_reported_not_reproduced",
        "source": "experiments/llvc/config.json + results/llvc_asr.json",
        "chunk_samples": chunk_samples,
        "chunk_ms": _r(chunk_ms),
        "lookahead_samples": 2 * lookahead,
        "algorithmic_latency_samples": algorithmic_samples,
        "algorithmic_latency_ms": _r(algorithmic_ms),
        "source_duration_seconds": duration_seconds,
        "source_duration_samples": source_samples,
        "chunk_count": chunk_count,
        "source_reported": {
            "rtf": HISTORICAL_RTF,
            "rtf_slowdown": HISTORICAL_RTF_SLOWDOWN,
            "e2e_latency_ms": HISTORICAL_E2E_MS,
            "average_inference_ms": HISTORICAL_AVG_INFER_MS,
            "cold_run_seconds": HISTORICAL_COLD_RUN_S,
            "wer": HISTORICAL_WER,
        },
        "derived_from_source_reported_rtf": {
            "average_inference_ms": _r(average_from_rtf_ms),
            "e2e_latency_ms": _r(e2e_from_rtf_ms),
            "deadline_miss_ratio": _r(HISTORICAL_E2E_MS / chunk_ms),
            "note": (
                "Arithmetic on source-reported values from the pinned "
                "evaluation README; not a local measurement."),
        },
        "shim_io_placement": (
            "The wrapper overrides file-level load/save only. It adds no "
            "per-chunk I/O to the streaming loop, so it does not change the "
            "per-chunk model compute that misses the deadline."),
        "shim_overhead_measured": False,
        "measured_here": False,
        "reproduced_here": False,
    }


def qualification() -> Dict[str, Any]:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "proposal_only": True,
        "candidate_qualified": False,
        "real_result_present": False,
        "runtime_present": False,
        "source_present": True,
        "shim_source_present": True,
        "shim_executed": False,
        "api_parity_result": False,
        "io_parity_result": False,
        "timing_result": False,
        "tool_profile_result": False,
        "benchmark_result": False,
        "device_timing_result": False,
        "listening_result": False,
        "release_claim": False,
        "all_release_gates_blocked": True,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def scope() -> Dict[str, Any]:
    return {
        "task_local_only": True,
        "write_scope": WRITE_SCOPE,
        "runtime_installed": False,
        "runtime_imported": False,
        "runtime_executed": False,
        "shim_executed": False,
        "shim_implemented_as_runtime": False,
        "stdlib_contract_model_only": True,
        "network_used": False,
        "real_assets_used": False,
        "real_corpus_used": False,
        "provider_registered": False,
        "public_abi_changed": False,
        "registry_or_default_changed": False,
        "shared_build_or_ci_changed": False,
        "benchmark_run": False,
        "device_timing_measured": False,
        "listening_performed": False,
        "release_claim": False,
    }


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    task = None
    for row in board["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            task = row
            break
    if task is None:
        raise ConfigError("linked task row is missing", "BOARD_ROW_MISSING")
    stable = {
        "task_id": task.get("id"),
        "title": task.get("title"),
        "mode": task.get("mode"),
        "repository": task.get("repository"),
        "component": task.get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    rows = [stable]
    digest = sha256_bytes(canonical_bytes(rows))
    return rows, digest


def boundary() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    return {
        "linked_row": dict(links[0]),
        "linked_rows": links,
        "linked_row_sha256": link_digest,
        "projected_fields": list(LINK_FIELDS),
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "linked_row_identity_only": True,
        "board_file_pinned": False,
        "mutable_board_fields_gate": False,
    }


def artifact_pins(names: Sequence[str] = SOURCE_ARTIFACT_FILES) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in names:
        path = HERE / name
        if not path.is_file():
            raise ConfigError("missing package artifact: " + name,
                              "MISSING_ARTIFACT")
        pins[name] = sha256_file(path)
    return pins


def required_artifacts(readiness: Mapping[str, Any]) -> List[Dict[str, Any]]:
    def row(identifier, kind, requirement, present, verified, blocked,
            revision=None, sha256=None):
        return {
            "id": identifier,
            "kind": kind,
            "requirement": requirement,
            "present": present,
            "verified": verified,
            "blocked": blocked,
            "revision": revision,
            "sha256": sha256,
        }

    return [
        row("ART-01", "pinned_llvc_source_and_shim_wrapper",
            "The pinned LLVC source at commit " + SOURCE_REVISION +
            " and the pinned evaluation wrapper run_llvc_eval.py with its "
            "four documented overrides.",
            True, True, False, SOURCE_REVISION,
            SOURCE_PINS[SHIM_WRAPPER_PATH]),
        row("ART-02", "torchaudio_cpu_wheel",
            "torchaudio 2.11.1 CPU wheel for CPython 3.11.5 and the target "
            "platform, with file name, byte count, SHA-256 and install record.",
            False, False, True),
        row("ART-03", "torchcodec_wheel",
            "The exact TorchCodec wheel required by torchaudio 2.11.1; the "
            "version was not recorded, so no exact artifact can be pinned.",
            False, False, True),
        row("ART-04", "soundfile_wheel",
            "soundfile 0.12.1 wheel (upstream requirements.txt pin) with file "
            "name, byte count, SHA-256 and native libsndfile provenance.",
            False, False, True),
        row("ART-05", "locked_evaluation_runtime",
            "The removed .venv-eval stack: CPython 3.11.5, torch 2.15.0, "
            "torchaudio 2.11.1, TorchCodec, soundfile, SpeechBrain 1.0.3, "
            "Auraloss 0.4.0 and a hash-pinned lockfile.",
            False, False, True),
        row("ART-06", "licence_and_notice_review",
            "Wheel licence/notice bundle and the separate libsndfile/native "
            "library redistribution decision.",
            False, False, True),
        row("ART-07", "rights_cleared_caller_owned_wav_fixture",
            "A permitted caller-owned WAV fixture with provenance, digest, "
            "derived-output and redistribution decisions.",
            False, False, True),
        row("ART-08", "executed_parity_and_timing_evidence",
            "Executed load/save/backend/Resample parity, malformed-input "
            "behaviour and import/cold-start/per-chunk timing on the exact "
            "runtime.",
            False, False, True),
    ]


def exact_blockers() -> List[Dict[str, Any]]:
    return [
        {
            "id": "BLK-01",
            "title": "exact_runtime_wheels_absent",
            "statement": (
                "No torchaudio 2.11.1, TorchCodec, soundfile 0.12.1, "
                "SpeechBrain 1.0.3 or Auraloss 0.4.0 wheel exists for the "
                "required CPython 3.11.5 runtime."),
            "missing": list(RUNTIME_REQUIRED),
            "rights_requirement": (
                "Wheel acquisition, licence/notice review and approval to "
                "install and execute."),
            "qualifies": False,
        },
        {
            "id": "BLK-02",
            "title": "torchcodec_version_unrecorded",
            "statement": (
                "The evaluation README says TorchAudio 2.11 load/save require "
                "TorchCodec, but records no TorchCodec version, byte count or "
                "SHA-256. A fabricated version or digest is not admissible."),
            "missing": [
                "TorchCodec version required by torchaudio 2.11.1",
                "TorchCodec wheel byte count and SHA-256",
                "backend/native-library dependency inventory",
            ],
            "rights_requirement": (
                "The TorchCodec wheel and native-library terms must be "
                "reviewed with the exact version pinned."),
            "qualifies": False,
        },
        {
            "id": "BLK-03",
            "title": "soundfile_version_and_native_terms",
            "statement": (
                "Upstream requirements pin soundfile==0.12.1, while the "
                "observed unrelated installations are 0.14.0. The evaluation "
                "environment's resolved version is unrecorded, and the "
                "libsndfile terms for bundled native bytes were not reviewed."),
            "missing": [
                "soundfile 0.12.1 wheel and SHA-256",
                "the exact evaluation-env soundfile version",
                "libsndfile/native library provenance and terms",
            ],
            "rights_requirement": (
                "Record SoundFile and libsndfile terms, including binary "
                "redistribution obligations."),
            "qualifies": False,
        },
        {
            "id": "BLK-04",
            "title": "shim_and_api_parity_unexecuted",
            "statement": (
                "The wrapper overrides and upstream calls are text-checked "
                "only. list_audio_backends, load, save and Resample were not "
                "executed, so dtype, shape, backend, exception and subtype "
                "parity are unknown."),
            "missing": [
                "executed API parity for load/save/list_audio_backends",
                "executed Resample compatibility check",
                "byte/sample parity against the real shim",
            ],
            "rights_requirement": (
                "Caller-owned fixture and approval to execute the runtime."),
            "qualifies": False,
        },
        {
            "id": "BLK-05",
            "title": "rights_cleared_fixture_and_output_use",
            "statement": (
                "The stdlib model uses generated synthetic WAV bytes. No "
                "permitted caller-owned WAV fixture, corpus provenance or "
                "derived-output decision exists."),
            "missing": [
                "rights-cleared mono 16 kHz float32 WAV fixture",
                "provenance, digest and consent record",
                "derived-output and redistribution decision",
            ],
            "rights_requirement": (
                "Record corpus provenance, consent (where applicable), "
                "evaluation use and redistribution."),
            "qualifies": False,
        },
        {
            "id": "BLK-06",
            "title": "timing_and_independent_review_absent",
            "statement": (
                "No import, cold-start, per-file I/O or per-chunk timing was "
                "measured. The historical RTF and latency remain "
                "source-reported, and no independent exact-head review or "
                "release approval exists."),
            "missing": [
                "import and cold-start timing",
                "per-file shim I/O timing",
                "per-chunk deadline impact",
                "independent exact-head review",
            ],
            "rights_requirement": (
                "Measured evidence on the target host and independent review."),
            "qualifies": False,
        },
    ]


def licensing() -> Dict[str, Any]:
    return {
        "package_license": "Apache-2.0",
        "upstream_llvc_license": "MIT",
        "upstream_license_reviewed": False,
        "wheel_license_reviewed": False,
        "libsndfile_terms_reviewed": False,
        "input_terms_reviewed": False,
        "output_terms_reviewed": False,
        "vendored_third_party_bytes": False,
        "note": (
            "The LLVC checkout LICENSE is MIT and pinned. No wheel, native "
            "library, model or corpus licence text is copied. SoundFile "
            "metadata declares BSD-3-Clause; libsndfile terms are separate "
            "and unreviewed."),
    }


def controls() -> Dict[str, Any]:
    return {
        "harness_wav_roundtrip": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
            "qualifies_candidate": False,
        },
        "runtime_identity_control": {
            "status": "not_run_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "historical_llvc_output_control": {
            "status": "not_run_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
        },
    }


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    readiness = runtime_readiness()
    absence = absence_probe()
    shim = shim_source_probe()
    wav = wav_contract_probe()
    adverse_requests = _adverse_cases()
    adverse_json = _json_adverse_cases()
    artifacts = required_artifacts(readiness)
    blockers = exact_blockers()
    gates = [dict(gate) for gate in GATES]
    timing = historical_timing()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task_schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_label": PROFILE_LABEL,
        "status": "incomplete",
        "decision": "DEFER",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "disposition": DISPOSITION,
        "scope": scope(),
        "boundary": boundary(),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "linked_row_identity": dict(links[0]),
        "linked_row_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(),
        "recorded_runtime": dict(RECORDED_RUNTIME),
        "runtime_readiness": readiness,
        "absence_evidence": absence,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "shim_reference": shim,
        "api_surface": [dict(item) for item in API_SURFACE],
        "wav_contract_probe": wav,
        "adverse": {
            "invalid_requests": adverse_requests,
            "invalid_json": adverse_json,
            "wav_rejections": wav["rejections"],
            "missing_result": missing_result("llvc_shim_synthetic_placeholder"),
        },
        "controls": controls(),
        "tool_profile": {
            "label": PROFILE_LABEL,
            "profile": PROFILE,
            "requirements": [dict(item) for item in TOOL_REQUIREMENTS],
            "satisfied": False,
        },
        "required_results": dict(REQUIRED_RESULTS),
        "historical_timing": timing,
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": list(SOURCE_EVIDENCE_STATEMENTS),
        "release_gates": gates,
        "gates": [gate["id"] for gate in gates],
        "remaining_gates": [gate["id"] for gate in gates],
        "reproduction": {
            "regeneration": "run.py --all (repeat=3, byte-identical)",
            "tests": "python3 -m unittest -v test_reference.py",
            "verifier": "python3 verify.py",
            "stdlib_only": True,
            "network_used": False,
        },
        "counts": {
            "request_rejections": adverse_requests["case_count"],
            "json_rejections": adverse_json["case_count"],
            "wav_rejections": wav["rejections"]["case_count"],
            "wav_model_cases": len(wav["cases"]),
            "required_artifacts": len(artifacts),
            "present_artifacts": sum(1 for row in artifacts
                                     if row["present"]),
            "blocked_artifacts": sum(1 for row in artifacts
                                     if row["blocked"]),
            "exact_blockers": len(blockers),
            "tool_requirements": len(TOOL_REQUIREMENTS),
            "release_gates": len(gates),
            "qualifying_results": 0,
        },
        "no_missing_result_qualifies_candidate": True,
        "regressions": [],
        "regression_count": 0,
        "generated_by": "run.py --all",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
