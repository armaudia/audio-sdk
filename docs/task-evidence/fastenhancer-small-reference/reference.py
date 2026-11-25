# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-FASTENHANCER-SMALL-REFERENCE.

This module is standard-library only and deterministic. It contains no
FastEnhancer weight, ONNX Runtime package, real speech, corpus, vendor result or
candidate output. It records the exact external blocker, verifies the one
pinned MIT source checkout, hashes fixed local artifact probes, validates a
caller-supplied asset manifest with a fail-closed admission boundary, and
builds the canonical report.

Nothing here is a FastEnhancer Small implementation, an upstream-parity result,
a quality measurement, a listening result, a device-timing result, a benchmark
or a release claim. No local ONNX file is loaded into a runtime or executed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-FASTENHANCER-SMALL-REFERENCE"
COMPONENT_ID = "fastenhancer-small-reference"
TASK_TITLE = "FastEnhancer Small reference"
MODE = "implementation"
PROFILE = "enhancement"
BASE_COMMIT = "6b9c959ca694f01a481f6259aa7e2697b474c280"
BRANCH = "swarm/SDK-FASTENHANCER-SMALL-REFERENCE"
WRITE_SCOPE = "docs/task-evidence/fastenhancer-small-reference/ only"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
CONTRACT_ID = "audio-sdk/fastenhancer-small-reference-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/fastenhancer-small-reference-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/fastenhancer-small-reference-report/0.1"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/fastenhancer-small-reference/"

# Immutable inputs. ``source:`` rows are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/voice-enhancement-20261101/agent-ears-preservation-743/REPORT.md":
        "d3a2206056eac182f62e3c7d3ea6f249b65ecdb001d5b847142d87ccc5627467",
    "research/native-fastenhancer-alone-20261109/REPORT.md":
        "84a29240c66f4e8095aa379b607d70386803b686b0f507d7d2b991130df10d05",
    "research/native-fastenhancer-alone-20261109/results.json":
        "35c7abc33e42913e895adf4a7e93eddabd283431cade6e0b4d3fa93f990e46c6",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/fastenhancer/adapter.json":
        "2a42cef166dc514488f4fdfe9b37c87427183444bcc19a2f6a4e96e77f87026b",
    "adapters/fastenhancer/README.md":
        "32a856af0f7f32efb35b0b00c6551564f6383cf6446285c060294504cdf341ea",
    "adapters/fastenhancer/requirements.lock":
        "1195f7e838fd20dc1fff30b3808324131c9f7acbedf63f9bf4084de78aa6a86c",
    "adapters/fastenhancer/run.py":
        "7c34889410f7ac144d73f2c141686243e70ea057eeacd1e947917199fdebf50f",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/README.md":
        "d47d0ce64bfbe85f9b099cac422c180481da646a7f5d392e98c174582463d8f6",
    "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/provider.json":
        "3000d76b0ef5b668e2ecbf41b4d1a12681a1c9ecdc80a30fa8f9b5d8f07fcbc0",
    "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/report.json":
        "34edd5dffed3f5a5eef0aa72675b8efe0fd89403d7a5356cf51c8a0e5e9ef84d",
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
GATE_LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                   "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-FND-AUDIT",
        "title": "Public provider intake and asset boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-EVIDENCE",
        "title": "Task-matched conformance and reproducible benchmark evidence",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-NN",
        "title": "Optional neural and offline runtime boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-FND-PROVIDER",
        "title": "Provider integration boundaries and build fragments",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"],
    },
)

# Exact pinned identity from the research ledgers, census, adapter and release.
SOURCE_ROOT_REL = "data/checkouts/FastEnhancer"
SOURCE_REPOSITORY = "https://github.com/aask1357/fastenhancer"
SOURCE_REVISION = "49ab55a57e3a064d94c6412cd0f0a383a55ca0f8"
SOURCE_RELEASE_TAG = "onnx-dns-v1.0.0"
SOURCE_LICENSE = "MIT"
SOURCE_TREE_DIGEST = (
    "30e6a40df543545c1d16d77031db1135e4201acae27dca356c752799d0737ad0"
)
SOURCE_FILE_COUNT = 85
SOURCE_LICENSE_SHA256 = (
    "38164c22720cdccceb5f0dbb8f7218dcf17bac97ac536cad2e77c33dfbc45a18"
)
MODEL_ID = "FastEnhancer-DNS-16k-Small"
MODEL_VARIANT = "small_16khz_dns3"
MODEL_PATH = "data/models/fastenhancer/fastenhancer_s.onnx"
MODEL_SHA256 = (
    "d7c937d6b475dbe89a6e6a69853b685fe62d629f4c96077559c556ac6f8aaa2d"
)
MODEL_BYTES = 832_813
MODEL_WEIGHT_TERMS = "not specified separately; retain local only"
MODEL_TRAINING_DATA_NOTE = (
    "DNS Challenge 3 16 kHz DNS data and VCTK speakers excluding p232/p257; "
    "possible relationship to the DNS2020 test subset is unresolved")
MODEL_EXECUTION_PROVIDER = "CPUExecutionProvider"
MODEL_THREADS = 1

# Installed v0 geometry is restated, never changed.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SDK_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
}

# Documented FastEnhancer 16 kHz streaming geometry from the pinned adapter and
# its pinned requirements lock. These are declared facts, not measurements.
N_FFT = 512
HOP_SAMPLES = 256
CHUNK_SAMPLES = 256
DELAY_COMPENSATION_SAMPLES = 256
OUTPUT_LENGTH = "identity"
SOURCE_TIME_MAPPING = "identity"
MAX_FRAME_SAMPLE_COUNT = SAMPLE_RATE_HZ * 600

PINNED_PYTHON_VERSION = "3.10"
PINNED_ONNXRUNTIME_VERSION = "1.20.1"
PINNED_ONNXRUNTIME_WHEEL_SHA256 = (
    "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439"
)
PINNED_NUMPY_VERSION = "1.26.4"
PINNED_SOUNDFILE_VERSION = "0.13.1"
RUNTIME_MODULES = ("onnxruntime",)
RUNTIME_CANDIDATE_PATHS = (
    "data/envs/dtln-onnx",
    "data/envs/dtln-onnx/bin/python",
    "data/envs/fastenhancer",
    "data/envs/fastenhancer/bin/python",
)
LOCAL_CPP_RUNTIME = "cpp-library/.deps/onnxruntime-osx-arm64-1.31.1"
LOCAL_CPP_RUNTIME_VERSION = LOCAL_CPP_RUNTIME + "/VERSION_NUMBER"
LOCAL_CPP_RUNTIME_COMMIT = LOCAL_CPP_RUNTIME + "/GIT_COMMIT_ID"
LOCAL_CPP_RUNTIME_LICENSE = LOCAL_CPP_RUNTIME + "/LICENSE"
LOCAL_CPP_RUNTIME_LIBRARY = (
    LOCAL_CPP_RUNTIME + "/lib/libonnxruntime.1.31.1.dylib")
LOCAL_CPP_RUNTIME_ARCHIVE = "cpp-library/.deps/onnxruntime.tgz"

# Fixed, bounded artifact probes. The exact 16 kHz Small release graph, the
# pinned Python runtime environment and any caller reference output must all be
# absent for this blocker package to remain truthful. Any present probe blocks
# shipping and forces a reopen.
ABSENCE_PROBES = (
    MODEL_PATH,
    "data/models/fastenhancer",
    "data/envs/fastenhancer",
    "data/envs/dtln-onnx",
    "data/wheels/onnxruntime-1.20.1-cp310-cp310-macosx_11_0_arm64.whl",
    "research/voice-enhancement-20261101/agent-fastenhancer-small",
    "research/voice-enhancement-20261101/agent-fastenhancer-small/reference_outputs",
    "research/voice-enhancement-20261101/agent-fastenhancer-small/cohort",
    "docs/task-evidence/fastenhancer-small-reference/reference_output.wav",
    "docs/task-evidence/fastenhancer-small-reference/cohort",
)

WEIGHT_PROBES = (
    {
        "path": MODEL_PATH,
        "role": "pinned_exact_16khz_small_release",
        "expected": "exact_16khz_small",
    },
    {
        "path": "cpp-library/.deps/fastenhancer_s.onnx",
        "role": "local_nonadmitted_small_variant",
        "expected": "nonadmitted",
    },
    {
        "path": "cpp-library/.deps/fastenhancer_t_16k.onnx",
        "role": "local_nonadmitted_tiny_16khz_control",
        "expected": "nonadmitted",
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "exact_16khz_small_weights",
        "requirement": (
            "The exact FastEnhancer DNS 16 kHz Small ONNX release graph at "
            "data/models/fastenhancer/fastenhancer_s.onnx, 832,813 bytes, "
            "SHA-256 d7c937d6b475dbe89a6e6a69853b685fe62d629f4c96077559c556ac6f8aaa2d, "
            "from repository aask1357/fastenhancer at commit "
            "49ab55a57e3a064d94c6412cd0f0a383a55ca0f8 and release tag "
            "onnx-dns-v1.0.0, supplied by the caller without a download."),
    },
    {
        "id": "ART-02",
        "kind": "pinned_python_runtime",
        "requirement": (
            "The exact pinned CPython 3.10, macOS arm64 environment with "
            "onnxruntime 1.20.1 (wheel SHA-256 "
            "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439), "
            "numpy 1.26.4, soundfile 0.13.1 and the complete hash-pinned "
            "requirements.lock installed in an approved isolated environment."),
    },
    {
        "id": "ART-03",
        "kind": "rights_bundle",
        "requirement": (
            "Artifact-specific model-weight terms, exact training-data "
            "provenance, third-party notices and a written redistribution and "
            "product-use decision for the exact ONNX graph and runtime."),
    },
    {
        "id": "ART-04",
        "kind": "reference_parity",
        "requirement": (
            "Approved exact reference outputs for frozen inputs under the "
            "pinned graph and runtime, with finite same-length output, exact "
            "256-sample chunk framing, zero-pad flush and identity source "
            "mapping."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_paired_cohort",
        "requirement": (
            "A rights-cleared task-matched paired clean/noisy cohort with "
            "independent SI-SDR and STOI scoring, clean-speech preservation "
            "checks and permitted listening."),
    },
    {
        "id": "ART-06",
        "kind": "timing_and_intake_harness",
        "requirement": (
            "Target-runtime timing, memory and throughput measurements, "
            "content/availability delay, streaming-state parity and a separate "
            "opt-in provider intake with OFF default."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "The exact 16 kHz Small ONNX release graph is absent. "
            "data/models/fastenhancer/fastenhancer_s.onnx does not exist. The "
            "external ledger pins 832,813 bytes and SHA-256 "
            "d7c937d6b475dbe89a6e6a69853b685fe62d629f4c96077559c556ac6f8aaa2d "
            "at release commit 49ab55a57e3a064d94c6412cd0f0a383a55ca0f8 / "
            "onnx-dns-v1.0.0. A different local export at "
            "cpp-library/.deps/fastenhancer_s.onnx is 875,885 bytes, SHA-256 "
            "f04ece2beed330da367264c54cedded62f65a117fbde5c005d3a88fc796d0ba3 "
            "and declares wav_in [1,512], consistent with the 48 kHz "
            "512-sample-chunk variant. It is not the pinned 16 kHz artifact, "
            "no equivalence is proven and it is not admitted."),
        "required_action": (
            "Supply the exact caller-held 16 kHz Small ONNX graph bytes at the "
            "pinned byte count and SHA-256 from the pinned release, verified "
            "without a network download."),
        "linked_gates": ["RG-01", "RG-04"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "The pinned Python inference runtime is absent. onnxruntime is not "
            "importable in the evidence interpreter, no CPython 3.10 "
            "environment with onnxruntime 1.20.1 (wheel SHA-256 "
            "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439) "
            "exists at any fixed probe path, and the hash-pinned "
            "requirements.lock is not installed. A "
            "local C++ onnxruntime 1.31.1 prebuilt tree exists at "
            "cpp-library/.deps/onnxruntime-osx-arm64-1.31.1 but it is not the "
            "pinned Python runtime, was not imported, loaded or executed, and "
            "is not admitted."),
        "required_action": (
            "Install the exact CPython 3.10 / onnxruntime 1.20.1 / numpy "
            "1.26.4 / soundfile 0.13.1 environment from the hash-pinned lock "
            "in an approved isolated runner and record every artifact digest."),
        "linked_gates": ["RG-02", "RG-07"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "The upstream repository is MIT-licensed, but the release page does "
            "not state separate pretrained-model terms; the ledger records "
            "'not specified separately; retain local only'. Exact training-data "
            "provenance, third-party notices and a redistribution/product-use "
            "decision for the ONNX graph and runtime are not established."),
        "required_action": (
            "Supply written model-weight, training-data and runtime terms plus "
            "the complete notice bundle and an explicit legal/redistribution "
            "decision for the exact graph and runtime."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No approved exact reference output, frozen input vector or "
            "pinned output digest exists, and no candidate output was "
            "produced. The documented 256-sample chunk / 512-point FFT / "
            "256-sample compensation boundary was not exercised. Historical "
            "research outputs were not reproduced here."),
        "required_action": (
            "Produce approved reference outputs on frozen inputs with the "
            "pinned graph and runtime and record exact output digests, "
            "finiteness, peaks, length, state reset and source mapping."),
        "linked_gates": ["RG-04", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared paired real-speech cohort, independent "
            "SI-SDR/STOI scorer, clean-speech preservation result or permitted "
            "listening result is present. The historical 30-clip DNS2020 pilot "
            "and 743-item EARS input-preservation screen are research evidence, "
            "not a frozen benchmark or a qualification result."),
        "required_action": (
            "Supply a rights-cleared paired cohort with clean references, a "
            "pinned independent scorer and an approved listening protocol, "
            "then report all controls and adverse cases."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No target-runtime timing, memory, throughput, content or "
            "availability measurement and no streaming/runtime parity exists. "
            "No opt-in provider, descriptor or intake was created. Historical "
            "batch RTF, RSS and the 256-versus-512-sample delay discrepancy are "
            "provenance, not local measurements."),
        "required_action": (
            "Measure the exact runtime under a paced workload, record content "
            "and availability timing and resource limits, prove or reject "
            "streaming parity, and open a separate versioned intake with an "
            "OFF default."),
        "linked_gates": ["RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "exact_16khz_small_graph_and_source_revision_pin",
        "statement": (
            "The exact 16 kHz Small ONNX graph, release revision, byte count "
            "and SHA-256 are pinned before any implementation claim."),
        "reopen_condition": (
            "The caller supplies fastenhancer_s.onnx at 832,813 bytes and "
            "SHA-256 d7c937d6b475dbe89a6e6a69853b685fe62d629f4c96077559c556ac6f8aaa2d "
            "from release commit 49ab55a57e3a064d94c6412cd0f0a383a55ca0f8, "
            "read from caller storage without a download."),
    },
    {
        "id": "RG-02",
        "title": "pinned_python_runtime_admission",
        "statement": (
            "The pinned CPython 3.10, onnxruntime 1.20.1, numpy 1.26.4 and "
            "soundfile 0.13.1 environment is installed and importable."),
        "reopen_condition": (
            "Install the hash-pinned requirements.lock in an approved isolated "
            "environment, record every wheel digest and prove one deterministic "
            "CPU forward pass."),
    },
    {
        "id": "RG-03",
        "title": "artifact_rights_and_training_data",
        "statement": (
            "Artifact-specific code, model-weight, training-data and notice "
            "terms are reviewed with an explicit redistribution and "
            "product-use decision."),
        "reopen_condition": (
            "Supply written terms for the exact graph and runtime, resolve "
            "training-data provenance and third-party notices, and record the "
            "legal/product-use decision."),
    },
    {
        "id": "RG-04",
        "title": "exact_reference_parity",
        "statement": (
            "Approved FastEnhancer Small reference outputs are reproduced by "
            "the pinned graph and runtime on frozen inputs."),
        "reopen_condition": (
            "Publish approved output digests for frozen inputs and reproduce "
            "them byte-exactly, including finite same-length output, peaks, "
            "cache reset and identity source mapping."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_paired_cohort",
        "statement": (
            "A rights-cleared task-matched paired cohort with clean references "
            "is frozen before any quality result."),
        "reopen_condition": (
            "Supply the immutable paired cohort, provenance, fidelity metadata "
            "and clean references with permission for the intended use."),
    },
    {
        "id": "RG-06",
        "title": "independent_scoring_and_permitted_listening",
        "statement": (
            "Independent SI-SDR/STOI scoring, clean-speech preservation and "
            "permitted listening are completed for the exact conditions."),
        "reopen_condition": (
            "Pin the scorer, report paired and unpaired evidence separately "
            "and complete an approved listening protocol on the frozen cohort."),
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_memory_and_streaming_parity",
        "statement": (
            "Target-runtime timing, memory, throughput, content delay and "
            "streaming-state behaviour are measured, not inferred."),
        "reopen_condition": (
            "Run a paced target-runtime workload and record timing, memory, "
            "throughput, output peaks and content/availability delay, and prove "
            "or explicitly reject streaming parity."),
    },
    {
        "id": "RG-08",
        "title": "opt_in_provider_intake_and_release",
        "statement": (
            "A separate opt-in provider intake with OFF default, an explicit "
            "public-surface decision, independent review and release approval "
            "is complete."),
        "reopen_condition": (
            "Open a new versioned intake task, keep registration and default "
            "selection OFF, record the public-surface decision and pass "
            "independent exact-head review."),
    },
)

ENHANCEMENT_PROFILE_ROWS = (
    {
        "id": "ENH-01",
        "requirement": (
            "Run identity/noisy control and an established task-matched "
            "baseline."),
        "status": "blocked",
        "evidence": (
            "No candidate output exists; the historical DNS2020 pilot names "
            "identity, DeepFilterNet3 and DPDFNet baselines but is not "
            "reproduced here."),
    },
    {
        "id": "ENH-02",
        "requirement": (
            "Score paired SI-SDR and STOI where permitted clean references "
            "exist."),
        "status": "blocked",
        "evidence": (
            "No rights-cleared clean references, pinned scorer or candidate "
            "output exists."),
    },
    {
        "id": "ENH-03",
        "requirement": (
            "Measure clean-speech preservation, peaks and invalid outputs."),
        "status": "blocked",
        "evidence": (
            "No output samples exist, so preservation, peak and invalid-output "
            "checks cannot be run."),
    },
    {
        "id": "ENH-04",
        "requirement": (
            "For unpaired speech use a separately labeled predictive screen or "
            "authorized listening."),
        "status": "blocked",
        "evidence": (
            "No predictive screen and no authorized listening result exists; "
            "the historical 743-item EARS screen is an alteration proxy, not "
            "clean-reference quality or listening."),
    },
    {
        "id": "ENH-05",
        "requirement": "Report alignment, state and memory.",
        "status": "blocked",
        "evidence": (
            "The adapter documents 256-sample compensation and per-utterance "
            "cache reset, but no runtime state or memory was measured; the "
            "native screen measured a different 512-sample lag."),
    },
    {
        "id": "ENH-06",
        "requirement": (
            "Report measured content/availability timing for the exact "
            "runtime."),
        "status": "blocked",
        "evidence": (
            "No device clock, pacing, deadline, throughput or availability "
            "measurement was made; historical batch RTF is not a local "
            "measurement."),
    },
)

NON_CLAIMS = (
    "No exact FastEnhancer Small 16 kHz graph, caller weight bytes, model "
    "output or vendor result is loaded, executed or reproduced.",
    "No real speech, clean reference, corpus, media file or audio sample is "
    "present or read.",
    "No denoiser or FastEnhancer layer is implemented, approximated, "
    "substituted or compared; no generic filter stands in for the candidate.",
    "No quality, intelligibility, naturalness, speech-preservation, listening, "
    "device-timing, benchmark or release result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, installed-v0, shared "
    "build or CI change is made.",
    "No missing, synthetic or schema-control result is promoted or treated as "
    "evidence for the candidate.",
)

PROFILE_PHRASES = (
    "Run identity/noisy control and an established task-matched baseline.",
    "Score paired SI-SDR and STOI where permitted clean references exist.",
    "Measure clean-speech preservation, peaks and invalid outputs.",
    "For unpaired speech use a separately labeled predictive screen or "
    "authorized listening.",
    "Report alignment, state, memory and measured content/availability "
    "timing for the exact runtime.",
)

# Admission manifest is a task-local schema, not an SDK or FastEnhancer
# contract. A schema control is structural only and never qualifies.
MANIFEST_SCHEMA_ID = (
    "audio-sdk/fastenhancer-small-reference-asset-admission/0.1")
MANIFEST_FIELDS = ("component_id", "format", "model", "reference_output",
                   "rights", "runtime", "schema_id")
MODEL_FIELDS = ("byte_count", "license_path", "license_sha256", "model_id",
                "path", "revision", "sha256")
RUNTIME_FIELDS = ("numpy_version", "onnxruntime_version",
                  "onnxruntime_wheel_sha256", "python_version", "runtime_path",
                  "runtime_sha256", "soundfile_version")
RIGHTS_FIELDS = ("code_license", "model_license",
                 "redistribution_decision_reference", "training_data_reference")
FORMAT_FIELDS = ("channels", "delay_compensation_samples", "hop_size", "n_fft",
                 "output_length", "sample_format", "sample_rate_hz",
                 "source_time_mapping")
REFERENCE_FIELDS = ("finite", "path", "sample_count", "scorer", "sha256")
MAX_REFERENCE_SAMPLES = SAMPLE_RATE_HZ * 60 * 60
MAX_ONNX_BYTES = 16 * 1024 * 1024
MAX_SOURCE_FILES = 512
MAX_SOURCE_BYTES = 64 * 1024 * 1024
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
UNRESOLVED_RIGHTS = frozenset({"", "none", "unknown", "unresolved",
                               "not specified", "not specified separately"})


# --------------------------------------------------------------------------
# Strict JSON and digests
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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


# --------------------------------------------------------------------------
# Pins, board identity and source/artifact probes
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


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([{field: row.get(field) for field in BOARD_ROW_FIELDS}
                          for row in rows])


def _git_head(root: Path) -> str | None:
    head_path = root / ".git/HEAD"
    if not head_path.is_file():
        return None
    head = head_path.read_text(encoding="ascii").strip()
    if head.startswith("ref: "):
        ref_path = root / ".git" / head[5:]
        if not ref_path.is_file():
            return None
        value = ref_path.read_text(encoding="ascii").strip()
        return value if HEX40.fullmatch(value) else None
    return head if HEX40.fullmatch(head) else None


def _release_tag_ref(root: Path) -> bool:
    packed = root / ".git/packed-refs"
    if not packed.is_file():
        return False
    suffix = " refs/tags/" + SOURCE_RELEASE_TAG
    for line in packed.read_text(encoding="ascii").splitlines():
        if line.startswith(SOURCE_REVISION + suffix):
            return True
    return False


def source_probe(root: Path | None = None) -> dict:
    """Read-only digest over every non-.git file in the pinned checkout."""
    workspace = AUDIO_ROOT if root is None else Path(root)
    source = workspace / SOURCE_ROOT_REL
    if not source.is_dir():
        return {"status": "source_absent", "present": False, "path":
                SOURCE_ROOT_REL}
    rows: list[str] = []
    total_bytes = 0
    for directory, directory_names, file_names in os.walk(source):
        directory_names[:] = sorted(
            name for name in directory_names if name != ".git")
        for name in sorted(file_names):
            path = Path(directory) / name
            relative = path.relative_to(source).as_posix()
            payload = path.read_bytes()
            total_bytes += len(payload)
            if len(rows) >= MAX_SOURCE_FILES or total_bytes > MAX_SOURCE_BYTES:
                return {"status": "source_too_large", "present": False,
                        "path": SOURCE_ROOT_REL}
            rows.append(relative + " " + sha256_bytes(payload) + " " +
                        str(len(payload)) + "\n")
    tree_digest = sha256_bytes("".join(rows).encode("utf-8"))
    revision = _git_head(source)
    license_path = source / "LICENSE"
    license_sha256 = (sha256_file(license_path)
                      if license_path.is_file() else None)
    present = (
        revision == SOURCE_REVISION
        and tree_digest == SOURCE_TREE_DIGEST
        and len(rows) == SOURCE_FILE_COUNT
        and license_sha256 == SOURCE_LICENSE_SHA256
    )
    return {
        "status": "present_pinned" if present else "source_mismatch",
        "present": present,
        "path": SOURCE_ROOT_REL,
        "repository": SOURCE_REPOSITORY,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "release_tag": SOURCE_RELEASE_TAG,
        "release_tag_ref_present": _release_tag_ref(source),
        "tree_digest": tree_digest,
        "expected_tree_digest": SOURCE_TREE_DIGEST,
        "file_count": len(rows),
        "expected_file_count": SOURCE_FILE_COUNT,
        "byte_count": total_bytes,
        "license": SOURCE_LICENSE,
        "license_sha256": license_sha256,
        "expected_license_sha256": SOURCE_LICENSE_SHA256,
        "executed": False,
        "note": (
            "Read-only digest over every non-.git file in the local checkout; "
            "no upstream file is copied, imported or executed."),
    }


def _varint(payload: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while True:
        if offset >= len(payload):
            raise ValueError("protobuf_truncated_varint")
        byte = payload[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
        if shift > 63:
            raise ValueError("protobuf_varint_too_long")


def _pb_fields(payload: bytes) -> list[tuple[int, int, Any]]:
    fields: list[tuple[int, int, Any]] = []
    offset = 0
    while offset < len(payload):
        key, offset = _varint(payload, offset)
        field, wire = key >> 3, key & 7
        if field == 0:
            raise ValueError("protobuf_field_zero")
        if wire == 0:
            value, offset = _varint(payload, offset)
        elif wire == 1:
            if offset + 8 > len(payload):
                raise ValueError("protobuf_truncated_fixed64")
            value = payload[offset:offset + 8]
            offset += 8
        elif wire == 2:
            length, offset = _varint(payload, offset)
            if length > len(payload) - offset:
                raise ValueError("protobuf_truncated_bytes")
            value = payload[offset:offset + length]
            offset += length
        elif wire == 5:
            if offset + 4 > len(payload):
                raise ValueError("protobuf_truncated_fixed32")
            value = payload[offset:offset + 4]
            offset += 4
        else:
            raise ValueError("protobuf_unsupported_wire_type")
        fields.append((field, wire, value))
    return fields


def _pb_shape(type_proto: bytes) -> list[Any] | None:
    for field, _wire, value in _pb_fields(type_proto):
        if field != 1:
            continue
        for inner, _inner_wire, inner_value in _pb_fields(value):
            if inner != 2:
                continue
            dims: list[Any] = []
            for dim_field, _dim_wire, dim_value in _pb_fields(inner_value):
                if dim_field != 1:
                    continue
                dim: Any = None
                for item_field, _item_wire, item_value in _pb_fields(dim_value):
                    if item_field == 1:
                        dim = int(item_value)
                    elif item_field == 2:
                        dim = item_value.decode("utf-8", "strict")
                dims.append(dim)
            return dims
    return None


def _pb_value_info(payload: bytes) -> tuple[str | None, list[Any] | None]:
    name: str | None = None
    shape: list[Any] | None = None
    for field, _wire, value in _pb_fields(payload):
        if field == 1:
            name = value.decode("utf-8", "strict")
        elif field == 2:
            shape = _pb_shape(value)
    return name, shape


def onnx_summary(path: Path) -> dict:
    """Extract only producer strings and graph input/output shape metadata."""
    try:
        size = path.stat().st_size
    except OSError:
        return {"parsed": False, "reason": "unreadable"}
    if size > MAX_ONNX_BYTES:
        return {"parsed": False, "reason": "size_bound_exceeded"}
    try:
        payload = path.read_bytes()
        top = _pb_fields(payload)
        producer = None
        producer_version = None
        graph = None
        for field, _wire, value in top:
            if field == 2:
                producer = value.decode("utf-8", "strict")
            elif field == 3:
                producer_version = value.decode("utf-8", "strict")
            elif field == 7:
                graph = value
        if graph is None:
            return {"parsed": False, "reason": "graph_missing"}
        inputs: list[dict] = []
        outputs: list[dict] = []
        for field, _wire, value in _pb_fields(graph):
            if field not in (11, 12):
                continue
            name, shape = _pb_value_info(value)
            row = {"name": name, "shape": shape}
            (inputs if field == 11 else outputs).append(row)
        wav_in = next((row for row in inputs if row["name"] == "wav_in"),
                      None)
        wav_out = next((row for row in outputs if row["name"] == "wav_out"),
                       None)
        return {
            "parsed": True,
            "byte_count": size,
            "producer": producer,
            "producer_version": producer_version,
            "input_count": len(inputs),
            "output_count": len(outputs),
            "wav_in_shape": wav_in["shape"] if wav_in else None,
            "wav_out_shape": wav_out["shape"] if wav_out else None,
            "cache_in_count": sum(1 for row in inputs
                                  if str(row["name"]).startswith("cache_in_")),
            "cache_out_count": sum(1 for row in outputs
                                   if str(row["name"]).startswith("cache_out_")),
        }
    except (OSError, ValueError, UnicodeError, IndexError):
        return {"parsed": False, "reason": "malformed_onnx_protobuf"}


def _variant_hint(shape: Any) -> str:
    if shape == [1, CHUNK_SAMPLES]:
        return "16khz_256_sample_chunk"
    if shape == [1, 512]:
        return "shape_consistent_with_48khz_512_sample_chunk"
    if shape == [1, 320]:
        return "other_320_sample_chunk"
    return "unclassified"


def weights_probe(root: Path | None = None) -> dict:
    workspace = AUDIO_ROOT if root is None else Path(root)
    candidates: list[dict] = []
    for spec in WEIGHT_PROBES:
        relative = spec["path"]
        path = workspace / relative
        if not path.is_file():
            candidates.append({
                "path": relative,
                "role": spec["role"],
                "present": False,
                "sha256": None,
                "byte_count": None,
                "matches_pinned_exact": False,
                "admitted": False,
                "admission_reason": "artifact_absent",
            })
            continue
        digest = sha256_file(path)
        size = path.stat().st_size
        exact = (relative == MODEL_PATH and digest == MODEL_SHA256
                 and size == MODEL_BYTES)
        summary = onnx_summary(path) if path.suffix.lower() == ".onnx" else {}
        reason = "probe_only_not_admitted"
        if exact:
            reason = "identity_verified_runtime_and_rights_gates_open"
        elif relative == MODEL_PATH:
            reason = "sha256_or_byte_count_does_not_match_pin"
        elif relative.endswith("fastenhancer_s.onnx"):
            reason = ("different_local_export_not_the_pinned_16khz_release; "
                      "wav_in shape is not the 16 kHz 256-sample contract")
        elif relative.endswith("fastenhancer_t_16k.onnx"):
            reason = "different_model_size_tiny_not_small"
        candidates.append({
            "path": relative,
            "role": spec["role"],
            "present": True,
            "sha256": digest,
            "byte_count": size,
            "matches_pinned_exact": exact,
            "variant_hint": _variant_hint(summary.get("wav_in_shape")),
            "graph_metadata": summary,
            "admitted": False,
            "admission_reason": reason,
            "loaded_into_runtime": False,
            "inference_performed": False,
        })
    exact_rows = [row for row in candidates
                  if row["path"] == MODEL_PATH and row["matches_pinned_exact"]]
    local_small = next((row for row in candidates
                        if row["path"] == "cpp-library/.deps/fastenhancer_s.onnx"
                        ), None)
    return {
        "status": ("exact_pinned_model_present_unqualified" if exact_rows
                   else "blocked_exact_pinned_model_absent"),
        "pinned_model_id": MODEL_ID,
        "pinned_variant": MODEL_VARIANT,
        "pinned_path": MODEL_PATH,
        "pinned_sha256": MODEL_SHA256,
        "pinned_byte_count": MODEL_BYTES,
        "pinned_model_present": bool(exact_rows),
        "local_nonadmitted_small_present": bool(
            local_small and local_small["present"]),
        "local_nonadmitted_small_sha256": (
            local_small["sha256"] if local_small else None),
        "local_nonadmitted_small_byte_count": (
            local_small["byte_count"] if local_small else None),
        "candidates": candidates,
        "admitted_model": None,
        "downloaded": False,
        "note": (
            "Present local ONNX files are hashed and their graph metadata is "
            "parsed with a bounded standard-library protobuf reader. No file "
            "is loaded into a runtime and no inference is performed."),
    }


def _module_importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def runtime_probe(root: Path | None = None) -> dict:
    workspace = AUDIO_ROOT if root is None else Path(root)
    modules = {name: _module_importable(name) for name in RUNTIME_MODULES}
    found_envs = [relative for relative in RUNTIME_CANDIDATE_PATHS
                  if (workspace / relative).exists()]
    local_cpp: dict | None = None
    cpp_root = workspace / LOCAL_CPP_RUNTIME
    if cpp_root.is_dir():
        version_path = workspace / LOCAL_CPP_RUNTIME_VERSION
        commit_path = workspace / LOCAL_CPP_RUNTIME_COMMIT
        license_path = workspace / LOCAL_CPP_RUNTIME_LICENSE
        library_path = workspace / LOCAL_CPP_RUNTIME_LIBRARY
        local_cpp = {
            "path": LOCAL_CPP_RUNTIME,
            "present": True,
            "version": (version_path.read_text(encoding="ascii").strip()
                        if version_path.is_file() else None),
            "git_commit": (commit_path.read_text(encoding="ascii").strip()
                           if commit_path.is_file() else None),
            "license_sha256": (sha256_file(license_path)
                               if license_path.is_file() else None),
            "library_sha256": (sha256_file(library_path)
                               if library_path.is_file() else None),
            "library_byte_count": (library_path.stat().st_size
                                   if library_path.is_file() else None),
            "pinned_python_runtime_match": False,
            "admitted": False,
            "imported_or_executed": False,
            "admission_reason": (
                "C++ prebuilt tree is not the pinned CPython 3.10 "
                "onnxruntime 1.20.1 environment"),
        }
    archive: dict | None = None
    archive_path = workspace / LOCAL_CPP_RUNTIME_ARCHIVE
    if archive_path.is_file():
        archive = {
            "path": LOCAL_CPP_RUNTIME_ARCHIVE,
            "present": True,
            "sha256": sha256_file(archive_path),
            "byte_count": archive_path.stat().st_size,
            "opened": False,
            "admitted": False,
        }
    pinned_present = modules.get("onnxruntime", False)
    return {
        "status": ("runtime_module_present_unqualified" if pinned_present
                   else "blocked_pinned_runtime_absent"),
        "pinned_python_version": PINNED_PYTHON_VERSION,
        "pinned_onnxruntime_version": PINNED_ONNXRUNTIME_VERSION,
        "pinned_onnxruntime_wheel_sha256": PINNED_ONNXRUNTIME_WHEEL_SHA256,
        "pinned_numpy_version": PINNED_NUMPY_VERSION,
        "pinned_soundfile_version": PINNED_SOUNDFILE_VERSION,
        "modules": modules,
        "module_present": modules,
        "pinned_environment_paths_checked": list(RUNTIME_CANDIDATE_PATHS),
        "pinned_environment_paths_found": found_envs,
        "pinned_runtime_present": pinned_present and bool(found_envs),
        "pinned_runtime_version_verified": False,
        "pinned_runtime_complete": False,
        "local_cpp_runtime": local_cpp,
        "local_runtime_archive": archive,
        "imported_or_executed": False,
        "note": (
            "Import probes report the evidence interpreter only. No package is "
            "installed, imported, opened or downloaded."),
    }


def absence_probes(audio_root: Path | None = None,
                   probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    workspace = AUDIO_ROOT if audio_root is None else Path(audio_root)
    sdk_root = WORKTREE if worktree is None else Path(worktree)
    rows: list[dict] = []
    for relative in probes:
        present = (workspace / relative).exists() or (
            sdk_root / relative).exists()
        rows.append({
            "path": relative,
            "present": present,
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    return rows


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
        "all_probes_absent": all(not row["present"] for row in rows),
    }


def frame_plan(sample_count: int) -> dict:
    """Declared 16 kHz streaming call arithmetic from the pinned adapter."""
    if not _is_int(sample_count) or sample_count <= 0 \
            or sample_count > MAX_FRAME_SAMPLE_COUNT:
        raise ValueError("invalid_sample_count")
    right_pad = N_FFT
    horizon = sample_count + right_pad - HOP_SAMPLES
    calls = (horizon + HOP_SAMPLES - 1) // HOP_SAMPLES
    consumed = calls * HOP_SAMPLES
    output_start = N_FFT - HOP_SAMPLES
    return {
        "sample_count": sample_count,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "chunk_samples": CHUNK_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "n_fft_samples": N_FFT,
        "right_pad_samples": right_pad,
        "padded_input_samples": sample_count + right_pad,
        "calls": calls,
        "consumed_samples": consumed,
        "leading_samples_discarded": output_start,
        "output_length": OUTPUT_LENGTH,
        "output_samples": sample_count,
        "measured": False,
    }


# --------------------------------------------------------------------------
# Admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    return os.path.normpath(value) == value


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "invalid_object"
    if set(value) != set(fields):
        return ("missing_field" if set(fields) - set(value) else "unknown_field")
    return ""


def _reference_text(value: Any) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and len(value) <= 200
            and not any(ord(char) < 32 for char in value))


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed asset admission. No weight is loaded and no model runs."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object")

    if set(document) != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - set(document))
        extra = sorted(set(document) - set(MANIFEST_FIELDS))
        return _reject("missing_field" if missing else "unknown_field",
                       missing[0] if missing else extra[0])
    checks += 1

    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema", "schema_id")
    if document["component_id"] != COMPONENT_ID:
        return _reject("invalid_value", "component_id")

    model = document["model"]
    code = _exact_object(model, MODEL_FIELDS)
    if code:
        return _reject(code, "model")
    if model["model_id"] != MODEL_ID:
        return _reject("invalid_value", "model.model_id")
    if not isinstance(model["revision"], str) \
            or not HEX40.match(model["revision"]) \
            or model["revision"] != SOURCE_REVISION:
        return _reject("invalid_value", "model.revision")
    if not isinstance(model["sha256"], str) \
            or not HEX64.match(model["sha256"]) \
            or model["sha256"] != MODEL_SHA256:
        return _reject("invalid_value", "model.sha256")
    if not _is_int(model["byte_count"]) \
            or model["byte_count"] != MODEL_BYTES:
        return _reject("invalid_value", "model.byte_count")
    if not _path_is_canonical(model["path"]):
        return _reject("invalid_path", "model.path")
    if not _path_is_canonical(model["license_path"]):
        return _reject("invalid_path", "model.license_path")
    if not isinstance(model["license_sha256"], str) \
            or not HEX64.match(model["license_sha256"]):
        return _reject("invalid_value", "model.license_sha256")
    checks += 7

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if runtime["python_version"] != PINNED_PYTHON_VERSION:
        return _reject("invalid_value", "runtime.python_version")
    if runtime["onnxruntime_version"] != PINNED_ONNXRUNTIME_VERSION:
        return _reject("invalid_value", "runtime.onnxruntime_version")
    if runtime["onnxruntime_wheel_sha256"] != PINNED_ONNXRUNTIME_WHEEL_SHA256:
        return _reject("invalid_value", "runtime.onnxruntime_wheel_sha256")
    if runtime["numpy_version"] != PINNED_NUMPY_VERSION:
        return _reject("invalid_value", "runtime.numpy_version")
    if runtime["soundfile_version"] != PINNED_SOUNDFILE_VERSION:
        return _reject("invalid_value", "runtime.soundfile_version")
    if not _path_is_canonical(runtime["runtime_path"]):
        return _reject("invalid_path", "runtime.runtime_path")
    if not isinstance(runtime["runtime_sha256"], str) \
            or not HEX64.match(runtime["runtime_sha256"]):
        return _reject("invalid_value", "runtime.runtime_sha256")
    checks += 7

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    if rights["code_license"] != SOURCE_LICENSE:
        return _reject("invalid_value", "rights.code_license")
    if not _reference_text(rights["model_license"]) \
            or rights["model_license"].strip().lower() in UNRESOLVED_RIGHTS:
        return _reject("invalid_value", "rights.model_license")
    if not _reference_text(rights["training_data_reference"]):
        return _reject("invalid_value", "rights.training_data_reference")
    if not _reference_text(rights["redistribution_decision_reference"]):
        return _reject("invalid_value",
                       "rights.redistribution_decision_reference")
    checks += 4

    fmt = document["format"]
    code = _exact_object(fmt, FORMAT_FIELDS)
    if code:
        return _reject(code, "format")
    if not _is_int(fmt["sample_rate_hz"]) \
            or fmt["sample_rate_hz"] != SAMPLE_RATE_HZ:
        return _reject("invalid_value", "format.sample_rate_hz")
    if not _is_int(fmt["channels"]) or fmt["channels"] != CHANNELS:
        return _reject("invalid_value", "format.channels")
    if fmt["sample_format"] != SAMPLE_FORMAT:
        return _reject("invalid_value", "format.sample_format")
    if not _is_int(fmt["n_fft"]) or fmt["n_fft"] != N_FFT:
        return _reject("invalid_value", "format.n_fft")
    if not _is_int(fmt["hop_size"]) or fmt["hop_size"] != HOP_SAMPLES:
        return _reject("invalid_value", "format.hop_size")
    if fmt["output_length"] != OUTPUT_LENGTH:
        return _reject("invalid_value", "format.output_length")
    if fmt["source_time_mapping"] != SOURCE_TIME_MAPPING:
        return _reject("invalid_value", "format.source_time_mapping")
    if not _is_int(fmt["delay_compensation_samples"]) \
            or fmt["delay_compensation_samples"] != DELAY_COMPENSATION_SAMPLES:
        return _reject("invalid_value", "format.delay_compensation_samples")
    checks += 8

    reference = document["reference_output"]
    code = _exact_object(reference, REFERENCE_FIELDS)
    if code:
        return _reject(code, "reference_output")
    if not _path_is_canonical(reference["path"]):
        return _reject("invalid_path", "reference_output.path")
    if not isinstance(reference["sha256"], str) \
            or not HEX64.match(reference["sha256"]):
        return _reject("invalid_value", "reference_output.sha256")
    if not _is_int(reference["sample_count"]) \
            or not 0 < reference["sample_count"] <= MAX_REFERENCE_SAMPLES:
        return _reject("invalid_value", "reference_output.sample_count")
    if reference["finite"] is not True:
        return _reject("invalid_value", "reference_output.finite")
    if not _reference_text(reference["scorer"]):
        return _reject("invalid_value", "reference_output.scorer")
    checks += 5

    if probe_paths:
        probes = (
            (model["path"], model["sha256"], "model.path"),
            (model["license_path"], model["license_sha256"],
             "model.license_path"),
            (runtime["runtime_path"], runtime["runtime_sha256"],
             "runtime.runtime_path"),
            (reference["path"], reference["sha256"],
             "reference_output.path"),
        )
        for raw_path, digest, field in probes:
            path = Path(raw_path)
            if not path.is_file():
                return _reject("probe_missing", field)
            if sha256_file(path) != digest:
                return _reject("probe_digest_mismatch", field)
        checks += 4
    return _accept(checks)


def _manifest_control() -> dict:
    """Structural schema control. It is not evidence and never qualifies."""
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "component_id": COMPONENT_ID,
        "model": {
            "model_id": MODEL_ID,
            "revision": SOURCE_REVISION,
            "path": "/caller/models/fastenhancer/fastenhancer_s.onnx",
            "sha256": MODEL_SHA256,
            "byte_count": MODEL_BYTES,
            "license_path": "/caller/models/fastenhancer/LICENSE",
            "license_sha256": "1" * 64,
        },
        "runtime": {
            "python_version": PINNED_PYTHON_VERSION,
            "onnxruntime_version": PINNED_ONNXRUNTIME_VERSION,
            "onnxruntime_wheel_sha256": PINNED_ONNXRUNTIME_WHEEL_SHA256,
            "numpy_version": PINNED_NUMPY_VERSION,
            "soundfile_version": PINNED_SOUNDFILE_VERSION,
            "runtime_path": "/caller/env/bin/python3.10",
            "runtime_sha256": "2" * 64,
        },
        "rights": {
            "code_license": SOURCE_LICENSE,
            "model_license": "caller-cleared-model-terms",
            "training_data_reference": "caller-rights-record-training-data",
            "redistribution_decision_reference": "caller-rights-decision-001",
        },
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "n_fft": N_FFT,
            "hop_size": HOP_SAMPLES,
            "output_length": OUTPUT_LENGTH,
            "source_time_mapping": SOURCE_TIME_MAPPING,
            "delay_compensation_samples": DELAY_COMPENSATION_SAMPLES,
        },
        "reference_output": {
            "path": "/caller/evidence/reference.wav",
            "sha256": "3" * 64,
            "sample_count": SAMPLE_RATE_HZ,
            "finite": True,
            "scorer": "paired_si_sdr_stoi",
        },
    }


def _without_nested(section: str, field: str) -> dict:
    document = _manifest_control()
    del document[section][field]
    return document


def _with_nested(section: str, field: str, value: Any) -> dict:
    document = _manifest_control()
    document[section][field] = value
    return document


def admission_controls() -> dict:
    """Build the frozen adverse matrix plus one structural schema control."""
    cases: list[dict] = []

    def manifest_case(case_id: str, mutate, kind: str = "manifest") -> None:
        document = _manifest_control()
        result = mutate(document)
        if result["accepted"]:
            raise ValueError("control_not_rejected:" + case_id)
        cases.append({
            "id": case_id,
            "kind": kind,
            "status": "rejected",
            "code": result["code"],
            "field": result["field"],
            "state_unchanged": result["state_unchanged"],
            "qualifies": False,
            "evidence_class": "synthetic_admission_control",
        })

    def drop(document, field):
        del document[field]
        return validate_manifest(document, probe_paths=False)

    def put(document, field, value):
        document[field] = value
        return validate_manifest(document, probe_paths=False)

    def nested(document, section, field, value):
        document[section][field] = value
        return validate_manifest(document, probe_paths=False)

    cases.append({
        "id": "MISS-01", "kind": "manifest", "status": "rejected",
        "code": validate_manifest(None, probe_paths=False)["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    manifest_case("INV-01", lambda doc: drop(doc, "model"))
    manifest_case("INV-02", lambda doc: put(doc, "extra", "value"))
    manifest_case("INV-03", lambda doc: put(doc, "schema_id", "wrong"))
    manifest_case("INV-04", lambda doc: put(doc, "component_id", "other"))
    manifest_case("INV-05", lambda doc: validate_manifest(
        _without_nested("model", "model_id"), probe_paths=False))
    manifest_case("INV-06", lambda doc: nested(
        doc, "model", "model_id", "other/model"))
    manifest_case("INV-07", lambda doc: nested(
        doc, "model", "revision", SOURCE_REVISION.upper()))
    manifest_case("INV-08", lambda doc: nested(
        doc, "model", "revision", SOURCE_REVISION[:39]))
    manifest_case("INV-09", lambda doc: nested(
        doc, "model", "sha256", "0" * 63))
    manifest_case("INV-10", lambda doc: nested(
        doc, "model", "sha256", "g" * 64))
    manifest_case("INV-11", lambda doc: nested(
        doc, "model", "byte_count", -1))
    manifest_case("INV-12", lambda doc: nested(
        doc, "model", "byte_count", True))
    manifest_case("INV-13", lambda doc: nested(
        doc, "model", "byte_count", float("nan")))
    manifest_case("INV-14", lambda doc: nested(
        doc, "model", "byte_count", float("inf")))
    manifest_case("INV-15", lambda doc: nested(
        doc, "model", "byte_count", MODEL_BYTES + 1))
    manifest_case("INV-16", lambda doc: nested(
        doc, "model", "path", "relative/fastenhancer_s.onnx"))
    manifest_case("INV-17", lambda doc: nested(
        doc, "model", "path", "/caller/../fastenhancer_s.onnx"))
    manifest_case("INV-18", lambda doc: nested(
        doc, "model", "path", "/caller/\x00fastenhancer_s.onnx"))
    manifest_case("INV-19", lambda doc: nested(
        doc, "model", "license_sha256", "1" * 63))
    manifest_case("INV-20", lambda doc: nested(
        doc, "runtime", "python_version", "3.12"))
    manifest_case("INV-21", lambda doc: nested(
        doc, "runtime", "onnxruntime_version", "1.21.0"))
    manifest_case("INV-22", lambda doc: nested(
        doc, "runtime", "onnxruntime_wheel_sha256", "0" * 64))
    manifest_case("INV-23", lambda doc: nested(
        doc, "runtime", "numpy_version", "2.0.0"))
    manifest_case("INV-24", lambda doc: nested(
        doc, "runtime", "soundfile_version", "0.12.1"))
    manifest_case("INV-25", lambda doc: nested(
        doc, "runtime", "runtime_path", "bin/python"))
    manifest_case("INV-26", lambda doc: nested(
        doc, "runtime", "runtime_sha256", "x" * 64))
    manifest_case("INV-27", lambda doc: nested(
        doc, "rights", "code_license", "Apache-2.0"))
    manifest_case("INV-28", lambda doc: nested(
        doc, "rights", "model_license", ""))
    manifest_case("INV-29", lambda doc: nested(
        doc, "rights", "training_data_reference", ""))
    manifest_case("INV-30", lambda doc: nested(
        doc, "rights", "redistribution_decision_reference", ""))
    manifest_case("INV-31", lambda doc: nested(
        doc, "rights", "model_license", "unresolved"))
    manifest_case("INV-32", lambda doc: nested(
        doc, "rights", "training_data_reference", 7))
    manifest_case("INV-33", lambda doc: nested(
        doc, "format", "sample_rate_hz", 48000))
    manifest_case("INV-34", lambda doc: nested(
        doc, "format", "channels", 2))
    manifest_case("INV-35", lambda doc: nested(
        doc, "format", "sample_format", "i16"))
    manifest_case("INV-36", lambda doc: nested(
        doc, "format", "n_fft", 256))
    manifest_case("INV-37", lambda doc: nested(
        doc, "format", "hop_size", 512))
    manifest_case("INV-38", lambda doc: nested(
        doc, "format", "output_length", "streaming"))
    manifest_case("INV-39", lambda doc: nested(
        doc, "format", "source_time_mapping", "guessed"))
    manifest_case("INV-40", lambda doc: nested(
        doc, "format", "delay_compensation_samples", 160))
    manifest_case("INV-41", lambda doc: validate_manifest(
        _without_nested("reference_output", "sha256"), probe_paths=False))
    manifest_case("INV-42", lambda doc: nested(
        doc, "reference_output", "sha256", "z" * 64))
    manifest_case("INV-43", lambda doc: nested(
        doc, "reference_output", "sample_count", 0))
    manifest_case("INV-44", lambda doc: nested(
        doc, "reference_output", "sample_count", float("nan")))
    manifest_case("INV-45", lambda doc: nested(
        doc, "reference_output", "finite", False))
    manifest_case("INV-46", lambda doc: nested(
        doc, "reference_output", "scorer", ""))
    manifest_case("INV-47", lambda doc: nested(
        doc, "reference_output", "path", "reference.wav"))
    manifest_case("INV-48", lambda doc: put(doc, "model", "fastenhancer_s.onnx"))
    manifest_case("INV-49", lambda doc: validate_manifest(
        {**_manifest_control(), "format": {"bad": True}}, probe_paths=False))
    manifest_case("PRS-01", lambda doc: validate_manifest(doc,
                                                          probe_paths=True))

    for case_id, text, code in (
            ("JSON-01", '{"a":1,"a":2}', "duplicate_json_key:a"),
            ("JSON-02", '{"a":NaN}', "nonfinite_json_constant:NaN"),
            ("JSON-03", '{"a":Infinity}', "nonfinite_json_constant:Infinity"),
            ("JSON-04", '{"a":-Infinity}',
             "nonfinite_json_constant:-Infinity"),
            ("JSON-05", "[]", "json_root_not_object"),
            ("JSON-06", "\ufeff{}", "json_byte_order_mark")):
        try:
            loads_strict(text)
        except ValueError as error:
            message = str(error)
        else:  # pragma: no cover - the fixtures are malformed by design
            message = "accepted"
        cases.append({
            "id": case_id, "kind": "strict_json", "status": "rejected",
            "code": code, "field": "",
            "message_matches": message == code,
            "state_unchanged": True, "qualifies": False,
            "evidence_class": "synthetic_admission_control",
        })

    control = validate_manifest(_manifest_control(), probe_paths=False)
    controls = [{
        "id": "CTL-01",
        "kind": "manifest",
        "status": "accepted_schema_control",
        "code": control["code"],
        "checks": control["checks"],
        "artifacts_probed": False,
        "runtime_loaded": False,
        "weights_loaded": False,
        "audio_read": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "qualifies": False,
    }]
    return {"cases": cases, "controls": controls}


# --------------------------------------------------------------------------
# Canonical contract and report blocks
# --------------------------------------------------------------------------
def _artifact_rows() -> list[dict]:
    return [{
        "id": artifact["id"],
        "kind": artifact["kind"],
        "requirement": artifact["requirement"],
        "present": False,
        "verified": False,
        "sha256": None,
        "blocked": True,
    } for artifact in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict]:
    return [{
        "id": blocker["id"],
        "artifact_id": blocker["artifact_id"],
        "statement": blocker["statement"],
        "required_action": blocker["required_action"],
        "linked_gates": list(blocker["linked_gates"]),
        "status": "open",
        "qualifies": False,
    } for blocker in EXACT_BLOCKERS]


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TASK_TITLE,
        "mode": MODE,
        "repository": "audio-sdk",
        "component": COMPONENT_ID,
    }


def _gate_rows() -> list[dict]:
    link = _gate_link()
    return [{
        "id": gate["id"],
        "title": gate["title"],
        "statement": gate["statement"],
        "reopen_condition": gate["reopen_condition"],
        "status": "blocked",
        "qualifies": False,
        "linked_row": link,
    } for gate in RELEASE_GATES]


def linked_row_identity() -> dict:
    projection = {field: BOARD_ROW_PROJECTION[field]
                  for field in BOARD_ROW_FIELDS}
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "selector": "stable-row-identity/0.1:" + ",".join(BOARD_ROW_FIELDS),
        "gating": "stable_identity_only",
        "mutable_fields_excluded": [
            "status", "owner", "history", "depends_on", "write_scope",
            "deliverable", "acceptance", "evidence", "claim", "review",
            "handoff", "blocked_reason", "dispatch_priority"],
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "exact_source_present": True,
        "exact_pinned_model_present": False,
        "exact_runtime_present": False,
        "weight_rights_cleared": False,
        "real_cohort_present": False,
        "real_result_present": False,
        "reference_parity_result": False,
        "quality_result": False,
        "listening_result": False,
        "timing_or_peak_result": False,
        "benchmark_result": False,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def disposition_block() -> dict:
    return {
        "status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "promotion": "defer",
        "production_exposure": "DEFER",
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "installed_v0_behavior_change": False,
        "processor_exposure": False,
        "task_local_only": True,
        "files_outside_task_directory_written": False,
    }


def scope_block() -> dict:
    return {
        "source_present": True,
        "source_executed": False,
        "pinned_weights_present": False,
        "pinned_weights_read": False,
        "nonadmitted_local_onnx_hashed": True,
        "nonadmitted_local_onnx_loaded": False,
        "runtime_present": False,
        "runtime_executed": False,
        "inference_performed": False,
        "real_corpus": False,
        "audio_read": False,
        "denoising_performed": False,
        "reference_parity_result": False,
        "quality_scored": False,
        "listening": False,
        "device_timing": False,
        "peak_bound_measured": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "single_component": COMPONENT_ID,
        "provider_work": False,
        "runtime_work": False,
        "release_work": False,
        "write_scope": WRITE_SCOPE,
    }


def profile_source_block() -> dict:
    return {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "row": "Enhancement",
        "phrases": list(PROFILE_PHRASES),
    }


def upstream_record_block() -> dict:
    return {
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "release_tag": SOURCE_RELEASE_TAG,
        "source_license": SOURCE_LICENSE,
        "model_id": MODEL_ID,
        "model_variant": MODEL_VARIANT,
        "model_path": MODEL_PATH,
        "model_sha256": MODEL_SHA256,
        "model_byte_count": MODEL_BYTES,
        "model_weight_terms": MODEL_WEIGHT_TERMS,
        "training_data_note": MODEL_TRAINING_DATA_NOTE,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "n_fft": N_FFT,
        "hop_samples": HOP_SAMPLES,
        "chunk_samples": CHUNK_SAMPLES,
        "delay_compensation_samples": DELAY_COMPENSATION_SAMPLES,
        "execution_provider": MODEL_EXECUTION_PROVIDER,
        "threads": MODEL_THREADS,
        "adapter_identity": "fastenhancer-onnx-v1",
        "adapter_lock": "adapters/fastenhancer/requirements.lock",
        "pinned_python_version": PINNED_PYTHON_VERSION,
        "pinned_onnxruntime_version": PINNED_ONNXRUNTIME_VERSION,
        "pinned_onnxruntime_wheel_sha256":
            PINNED_ONNXRUNTIME_WHEEL_SHA256,
        "pinned_numpy_version": PINNED_NUMPY_VERSION,
        "pinned_soundfile_version": PINNED_SOUNDFILE_VERSION,
        "historical_values_are_provenance_only": True,
        "not_reproduced_here": True,
    }


def geometry_block() -> dict:
    return {
        "public_v0": public_v0_geometry(),
        "reference": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "n_fft": N_FFT,
            "hop_samples": HOP_SAMPLES,
            "chunk_samples": CHUNK_SAMPLES,
            "delay_compensation_samples": DELAY_COMPENSATION_SAMPLES,
            "output_length": OUTPUT_LENGTH,
            "source_time_mapping": SOURCE_TIME_MAPPING,
            "stateful": True,
            "cache_reset_per_utterance": True,
            "execution_provider": MODEL_EXECUTION_PROVIDER,
            "threads": MODEL_THREADS,
            "final_frame_zero_padded": True,
            "frame_plans": [frame_plan(value) for value in
                            (1600, 3200, 16000)],
            "measured": False,
            "note": (
                "Declared adapter geometry only. The adapter documents "
                "n_fft - hop_size = 256 samples of compensation, while a "
                "historical native screen measured 512 samples for Tiny 16 kHz; "
                "the exact 16 kHz Small delay is not measured here."),
        },
    }


def historical_evidence_block() -> dict:
    return {
        "status": "historical_research_not_reproduced_not_qualified",
        "qualifies": False,
        "entries": [
            {
                "id": "HIST-01",
                "source": "REALTIME_COMPONENT_CANDIDATES.md",
                "scope": "30 paired DNS2020 no-reverb clips, 16 kHz Small",
                "values": [
                    "delta SI-SDR +8.11 dB",
                    "delta STOI +0.0324",
                    "batch RTF 0.0359",
                ],
                "note": (
                    "Historical exploratory pilot; not a frozen benchmark, not "
                    "reproduced here, and not a qualification result."),
            },
            {
                "id": "HIST-02",
                "source": (
                    "research/voice-enhancement-20261101/"
                    "agent-ears-preservation-743/REPORT.md"),
                "scope": (
                    "743 EARS recordings, 16 kHz Small, input-preservation "
                    "screen without clean references"),
                "values": [
                    "mean STOI versus input 0.7453",
                    "mean SI-SDR versus input 5.704 dB",
                    "per-item transform RTF 0.03059",
                    "process peak RSS 67.4 MB",
                ],
                "note": (
                    "Alteration proxy only; not clean-reference quality, not "
                    "human MOS, not intelligibility and not reproduced here."),
            },
            {
                "id": "HIST-03",
                "source": "research/native-fastenhancer-alone-20261109/REPORT.md",
                "scope": (
                    "824 VoiceBank+DEMAND pairs, native Small 48 kHz f32, "
                    "different variant from the 16 kHz DNS release"),
                "values": [
                    "WB-PESQ 2.839",
                    "STOI 0.9428",
                    "SI-SDR 15.68 dB",
                    "measured alignment lag 341 samples at 16 kHz",
                ],
                "note": (
                    "Different native 48 kHz variant and different evaluation "
                    "scope; not transferable to the 16 kHz Small reference."),
            },
        ],
    }


def rights_gap_block() -> dict:
    return {
        "blocked": True,
        "code_license": SOURCE_LICENSE,
        "model_license": MODEL_WEIGHT_TERMS,
        "training_data_reference": None,
        "redistribution_decision_reference": None,
        "note": (
            "MIT covers the pinned source checkout only. Separate pretrained-"
            "weight terms, training-data provenance and product/redistribution "
            "clearance are not established."),
    }


def admission_contract_block() -> dict:
    return {
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "model_fields": list(MODEL_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "format_fields": list(FORMAT_FIELDS),
        "reference_fields": list(REFERENCE_FIELDS),
        "pinned_model_id": MODEL_ID,
        "pinned_revision": SOURCE_REVISION,
        "pinned_model_sha256": MODEL_SHA256,
        "pinned_model_byte_count": MODEL_BYTES,
        "pinned_python_version": PINNED_PYTHON_VERSION,
        "pinned_onnxruntime_version": PINNED_ONNXRUNTIME_VERSION,
        "pinned_onnxruntime_wheel_sha256":
            PINNED_ONNXRUNTIME_WHEEL_SHA256,
        "pinned_numpy_version": PINNED_NUMPY_VERSION,
        "pinned_soundfile_version": PINNED_SOUNDFILE_VERSION,
        "max_onnx_bytes": MAX_ONNX_BYTES,
        "max_reference_samples": MAX_REFERENCE_SAMPLES,
        "output_length": OUTPUT_LENGTH,
        "source_time_mapping": SOURCE_TIME_MAPPING,
        "delay_compensation_samples": DELAY_COMPENSATION_SAMPLES,
        "sdk_geometry": dict(SDK_GEOMETRY),
        "empty_payload_sha256": EMPTY_SHA256,
        "audio_read": False,
        "runtime_invoked": False,
        "weights_loaded": False,
        "inference_performed": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "upstream_record": upstream_record_block(),
        "geometry": geometry_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "admission_contract": admission_contract_block(),
        "enhancement_profile_requirements": [dict(row)
                                             for row in ENHANCEMENT_PROFILE_ROWS],
        "profile_source": profile_source_block(),
        "historical_evidence": historical_evidence_block(),
        "rights_gap": rights_gap_block(),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    contract = read_strict_json(HERE / "contract.json")
    probes = absence_probes(AUDIO_ROOT)
    controls = admission_controls()
    rejected = [case for case in controls["cases"]
                if case["status"] == "rejected"]
    accepted_controls = [case for case in controls["controls"]
                         if case["status"] == "accepted_schema_control"]
    gates = _gate_rows()
    artifacts = _artifact_rows()
    blockers = _blocker_rows()
    source = source_probe(AUDIO_ROOT)
    weights = weights_probe(AUDIO_ROOT)
    runtime = runtime_probe(AUDIO_ROOT)
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "task_id": TASK,
        "task_title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "upstream_record": upstream_record_block(),
        "source_probe": source,
        "weights_probe": weights,
        "runtime_probe": runtime,
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "conclusion": (
                "The exact 16 kHz Small graph, pinned Python runtime, caller "
                "cohort and caller reference output are absent at every fixed "
                "probe location."),
        },
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "enhancement_profile": {
            "profile": PROFILE,
            "rows": [dict(row) for row in ENHANCEMENT_PROFILE_ROWS],
            "identity_control": False,
            "noisy_control": False,
            "task_matched_baseline": False,
            "paired_clean_references": False,
            "paired_si_sdr": False,
            "paired_stoi": False,
            "clean_speech_preservation": False,
            "peak_and_invalid_output_checks": False,
            "unpaired_predictive_screen": False,
            "authorized_listening": False,
            "alignment_reported": False,
            "state_reported": False,
            "memory_reported": False,
            "content_availability_timing_measured": False,
            "status": "blocked",
        },
        "geometry": geometry_block(),
        "historical_evidence": historical_evidence_block(),
        "rights_gap": rights_gap_block(),
        "admission": {
            "policy": "task_local_fail_closed_admission_not_runtime_behavior",
            "cases": controls["cases"],
            "schema_controls": controls["controls"],
            "summary": {
                "case_count": len(controls["cases"]),
                "rejected_count": len(rejected),
                "accepted_schema_controls": len(accepted_controls),
                "qualifying_results": 0,
                "state_advanced_on_rejection": any(
                    case["state_unchanged"] is not True for case in rejected),
                "runtime_invoked": False,
                "weights_loaded": False,
                "audio_read": False,
                "inference_performed": False,
            },
        },
        "qualification": qualification_block(),
        "prohibited_claims": list(NON_CLAIMS),
        "gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "linked_row_identity": linked_row_identity(),
        "profile_source": profile_source_block(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": {
            "runs": 3,
            "byte_identical": True,
            "cold_start_processes": True,
            "canonical_json": True,
            "sorted_keys": True,
            "compact_separators": True,
            "trailing_newline": True,
        },
        "reproduction": {
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                      "test_reference.py"),
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract.get("profile") != PROFILE or contract.get("mode") != MODE:
        raise ValueError("contract_profile_or_mode")
    if contract.get("decision") != DECISION:
        raise ValueError("contract_decision")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status")
    if contract.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("contract_evidence_status")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("incomplete") is not True:
        raise ValueError("contract_incomplete")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked"
           for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    if contract.get("board_row_sha256") != board_row_digest(
            BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_row_digest")
    if contract.get("linked_rows") != [dict(row) for row in LINKED_ROWS]:
        raise ValueError("contract_linked_rows")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
