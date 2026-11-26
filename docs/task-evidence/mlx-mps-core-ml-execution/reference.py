# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-MLX-MPS-CORE-ML-EXECUTION.

This module never downloads a runtime, loads a model, imports an accelerator
package, reads audio, compiles a Core ML model, runs inference, measures a
device or produces a benchmark or release claim. The exact licensed MLX, MPS
and Core ML runtimes and the exact model/assets are absent. The module pins
stable read-only inputs, records fixed absence probes, applies a fail-closed
synthetic accelerator-execution admission contract and emits canonical JSON.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/mlx-mps-core-ml-execution/"

TASK = "SDK-MLX-MPS-CORE-ML-EXECUTION"
TASK_TITLE = "MLX / MPS / Core ML execution"
COMPONENT_ID = "mlx-mps-core-ml-execution"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "tool"
PROFILE_KEY = "Tool"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/mlx-mps-core-ml-execution-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/mlx-mps-core-ml-execution-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/mlx-mps-core-ml-execution-report/0.1"
BASE_COMMIT = "7dc9c84b2ed963ecda895194b19e8d8979a2f748"
BRANCH = "swarm/SDK-MLX-MPS-CORE-ML-EXECUTION"
REVIEWER = "reviewer-MLX-MPS-CORE-ML-EXECUTION"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
URL = re.compile(r"^https://[A-Za-z0-9][A-Za-z0-9._~/-]{2,238}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to AUDIO_ROOT; boundary
# paths are SDK-worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "adapters/reuse-mlx/README.md":
        "a583f20d64a32f128640064583a531f7e5097aeb681f9ba8fb48221667012e2b",
    "adapters/reuse-mlx/adapter.json":
        "2e77df89f2b78eabd0bbb399ffe55d6561651585e7397473e632aa96ea1e89fd",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "realtime-audio-library/accelerator_options.md":
        "ed3c1204911056f26c5ab2951db7bd758fe1ff66fa32d6195f259fa7bc352f8d",
    "realtime-audio-library/evaluation/cpu_saving_20261031/README.md":
        "b29fddd8bcfdba0d953bf40e75d8cb0c330158378fa74c64129bf16992bcf73b",
    "realtime-audio-library/evaluation/cpu_saving_20261031/coreml_trial/"
    "coreml_1s.json":
        "1fa41a3d92db2dd38dd3b47f3d4876bca84112b71b8da13133ef0ca576433b45",
    "realtime-audio-library/evaluation/cpu_saving_20261031/coreml_trial/"
    "coreml_8s_8e.json":
        "a67093c3ddc46dc20eeed89792e4c858e2685df84c62e1ae52bd0bb8979763bd",
    "realtime-audio-library/evaluation/cpu_saving_20261031/coreml_trial/"
    "coreml_16s_8e.json":
        "cc83776ed66fde90b55f018e6841a68e741fd061f7ca0923e004e8c73d3a5e18",
    "realtime-audio-library/evaluation/cpu_saving_20261031/coreml_trial/"
    "dpdfnet_coreml_trial.patch":
        "2ee432b7b52ed9dac35172450d19e0a2a8c19c60d301dd8bb5b60dbba2f47a4e",
    "realtime-audio-library/evaluation/performance_investigation_20261031/"
    "decision_log.md":
        "b96e47dc9aef513b6f04c60d808baa17dc33513a6d8c68160cf2be99a4189d5b",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "evidence", "deliverable", "acceptance",
    "write_scope",
)
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Record version, install location and provenance",
    "clean checkout or extracted package",
    "one typical CLI/API use",
    "caller-owned inputs",
    "malformed inputs",
    "missing optional selections",
    "compile/build evidence, synthetic runtime evidence and measured workload",
)
SCOPE_BASE_REFS = ("origin/main", "main")

# ---------------------------------------------------------------------------
# Accelerators. Each one is a separate runtime with its own identity and its
# own CPU parity and availability requirement. Nothing is pooled.
# ---------------------------------------------------------------------------

RUNTIME_IDS = ("mlx", "mps", "coreml")
ARCHES = ("arm64", "x86_64")
MAX_MODEL_FILES = 32
MAX_MODEL_FILE_BYTES = 8 * 1024 * 1024 * 1024
MAX_DURATION_MS = 3_600_000
MAX_TOLERANCE = 1_000_000

ACCELERATORS = {
    "mlx": {
        "display": "MLX",
        "kind": "array_framework_metal",
        "upstream": "ml-explore/mlx",
        "top_level_module": "mlx",
        "required_identity":
            "ml-explore/mlx at an immutable 40-hex commit with a versioned "
            "wheel or source install root, offline load path, lock SHA-256 "
            "and reviewed license text",
        "probe_paths": (
            "data/runtimes/mlx",
            "data/envs/mlx",
            "research/runtimes/mlx",
            ".venv-mlx",
        ),
        "home_paths": (
            "~/.venvs/mlx",
            "~/.local/share/mlx",
        ),
    },
    "mps": {
        "display": "MPS",
        "kind": "metal_performance_shaders_backend",
        "upstream": "pytorch/pytorch (MPS backend)",
        "top_level_module": "torch",
        "required_identity":
            "the exact PyTorch build that provides the MPS backend at an "
            "immutable 40-hex commit, with version, wheel install root, lock "
            "SHA-256, reviewed license text and recorded Metal device profile",
        "probe_paths": (
            "data/runtimes/mps",
            "data/envs/mps",
            "research/runtimes/mps",
            ".venv-mps",
        ),
        "home_paths": (
            "~/.venvs/mps",
            "~/.local/share/mps",
        ),
    },
    "coreml": {
        "display": "Core ML",
        "kind": "apple_coreml_deployment",
        "upstream": "apple/apple (Core ML framework and toolchain)",
        "top_level_module": "coremltools",
        "required_identity":
            "an exact Core ML deployment target with a pinned toolchain and "
            "binding identity (coremltools or Swift), version, lock SHA-256, "
            "reviewed license text and a compiled model artifact with SHA-256",
        "probe_paths": (
            "data/runtimes/coreml",
            "data/envs/coreml",
            "research/runtimes/coreml",
            ".venv-coreml",
        ),
        "home_paths": (
            "~/.venvs/coreml",
            "~/.local/share/coreml",
        ),
    },
}

NON_CLAIMS = [
    "No MLX, MPS or Core ML runtime, package, wheel, toolchain binding, model "
    "file, compiled model, config or preprocessing asset is present, imported, "
    "linked or executed by this package.",
    "No inference, model load, Core ML compile, audio read, audio write, "
    "listening, quality score, CPU parity comparison, device-timing "
    "measurement, memory measurement, benchmark or workload claim is made.",
    "No real corpus, waveform, feature tensor or model input is used here.",
    "No missing, invalid, nonfinite or adverse manifest case qualifies; the "
    "single accepted synthetic schema control is not execution evidence.",
    "No adjacent Apple runtime, ONNX Runtime, RVC-MLX, NumPy/SciPy or survey "
    "result is inherited, pooled or promoted to MLX, MPS or Core ML.",
    "The earlier ONNX Runtime CoreML execution-provider screen is adverse "
    "sibling evidence. It is recorded with its original scope and is never "
    "treated as MLX, MPS or Core ML qualification, a CPU parity result or a "
    "current-runtime measurement.",
    "The presence of an operating-system Core ML framework or Xcode toolchain "
    "is an observation only; it is not a pinned runtime and does not admit "
    "Core ML.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; the absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "apple-and-browser-runtime-qualification",
        "task": "SDK-APPLE-AND-BROWSER-RUNTIME-QUALIFICATION",
        "path": "docs/task-evidence/apple-and-browser-runtime-qualification/"
                "README.md",
        "class": "adjacent_apple_native_probe",
        "decision": "DEFER",
        "status": "partial_probe",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Compiles the C11 SDK consumer for Apple native and "
                    "Emscripten/Node; it contains no MLX, MPS or Core ML "
                    "runtime, model or device-timing result.",
    },
    {
        "component": "rvc-mlx-realtime",
        "task": "SDK-RVC-MLX-REALTIME",
        "path": "docs/task-evidence/rvc-mlx-realtime/report.json",
        "class": "adjacent_mlx_voice_blocker",
        "decision": "DEFER",
        "status": "incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Records absent RVC weights and an unpinned MLX runtime as "
                    "a voice blocker; it supplies no generic MLX execution, "
                    "CPU parity or availability evidence.",
    },
    {
        "component": "onnx-runtime-reference-runtime",
        "task": "SDK-ONNX-RUNTIME-REFERENCE-RUNTIME",
        "path": "docs/task-evidence/onnx-runtime-reference-runtime/report.json",
        "class": "adjacent_cpu_runtime_blocker",
        "decision": "DEFER",
        "status": "synthetic_boundary_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A CPU ONNX Runtime boundary probe; it does not establish "
                    "MLX, MPS or Core ML execution or parity.",
    },
    {
        "component": "realtime-audio-library-coreml-trial",
        "task": "REALTIME-AUDIO-LIBRARY-CPU-SAVING-INVESTIGATION",
        "path": "realtime-audio-library/evaluation/cpu_saving_20261031/"
                "README.md",
        "class": "adjacent_adverse_coreml_execution_trial",
        "decision": "REJECT",
        "status": "adverse_trial_not_usable",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "An ONNX Runtime 1.31.1 CoreML execution-provider screen on "
                    "one DPDFNet graph. Concurrent use failed and the sibling "
                    "record rejects the configuration; its single-stream "
                    "latency has no paired CPU baseline and is not reusable.",
    },
    {
        "component": "reuse-mlx-adapter",
        "task": "AUDIOML-REUSE-MLX-ADAPTER",
        "path": "adapters/reuse-mlx/README.md",
        "class": "adjacent_adapter_reference",
        "decision": "DEFER",
        "status": "blocked_toolchain_and_weights",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "An offline protocol wrapper for one NVIDIA checkpoint "
                    "through a community Swift/MLX CLI; its unpinned runtime "
                    "and absent weights are not execution evidence and are not "
                    "inherited here.",
    },
)

TOOL_REQUIREMENTS = (
    {
        "id": "TOOL-01",
        "requirement": "Record the runtime version, install location and "
                       "provenance for each accelerator separately.",
        "status": "blocked",
        "evidence": "No MLX, MPS or Core ML runtime version, install root, "
                    "package lock or provenance record exists on this host.",
    },
    {
        "id": "TOOL-02",
        "requirement": "Verify a clean checkout or extracted runtime package.",
        "status": "blocked",
        "evidence": "No clean extracted MLX, MPS or Core ML runtime package "
                    "exists to verify.",
    },
    {
        "id": "TOOL-03",
        "requirement": "Run one typical CLI/API use.",
        "status": "blocked",
        "evidence": "No model or compiled Core ML artifact exists, so no "
                    "typical inference or compile invocation can be run.",
    },
    {
        "id": "TOOL-04",
        "requirement": "Verify caller-owned inputs.",
        "status": "blocked",
        "evidence": "No buffer or asset handoff test exists on any pinned "
                    "runtime, so caller ownership and lifetime are unverified.",
    },
    {
        "id": "TOOL-05",
        "requirement": "Reject malformed inputs.",
        "status": "blocked",
        "evidence": "No malformed-input control exists for any accelerator "
                    "runtime or adapter entry point.",
    },
    {
        "id": "TOOL-06",
        "requirement": "Report missing optional selections.",
        "status": "blocked",
        "evidence": "No missing-optional-selection control exists; absent "
                    "optional runtime or asset selection is unobserved.",
    },
    {
        "id": "TOOL-07",
        "requirement": "Separate compile/build evidence from synthetic runtime "
                       "evidence.",
        "status": "blocked",
        "evidence": "Neither compile/build evidence nor synthetic runtime "
                    "evidence exists on a pinned runtime.",
    },
    {
        "id": "TOOL-08",
        "requirement": "Produce measured workload support.",
        "status": "blocked",
        "evidence": "No paced workload, throughput, memory, resource or "
                    "availability measurement exists on an admitted runtime.",
    },
    {
        "id": "ACC-01",
        "requirement": "Treat MLX as an independent runtime with CPU parity and "
                       "availability evidence.",
        "status": "blocked",
        "evidence": "No MLX runtime, CPU reference, parity comparison or "
                    "availability observation exists.",
    },
    {
        "id": "ACC-02",
        "requirement": "Treat MPS as an independent runtime with CPU parity and "
                       "availability evidence.",
        "status": "blocked",
        "evidence": "No PyTorch MPS runtime, Metal device query, CPU "
                    "reference, parity comparison or availability observation "
                    "exists.",
    },
    {
        "id": "ACC-03",
        "requirement": "Treat Core ML as an independent runtime with CPU "
                       "parity and availability evidence.",
        "status": "blocked",
        "evidence": "No pinned Core ML deployment target, binding, compiled "
                    "model, CPU reference, parity comparison or availability "
                    "observation exists. The sibling ONNX Runtime Core ML "
                    "provider trial is rejected for concurrent use and has no "
                    "paired CPU baseline; an OS framework observation is not "
                    "admission.",
    },
    {
        "id": "ACC-04",
        "requirement": "Do not pool MLX, MPS and Core ML into one runtime "
                       "result.",
        "status": "blocked",
        "evidence": "No per-runtime result exists, so there is nothing to keep "
                    "separate and nothing to compare.",
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "runtime",
        "requirement":
            "MLX at an immutable 40-hex upstream commit: versioned wheel or "
            "source install root, offline load path, lock SHA-256, reviewed "
            "license text and provenance record.",
    },
    {
        "id": "ART-02",
        "kind": "runtime",
        "requirement":
            "The exact PyTorch build providing the MPS backend at an immutable "
            "40-hex commit: version, wheel install root, lock SHA-256, reviewed "
            "license text and recorded Metal device profile.",
    },
    {
        "id": "ART-03",
        "kind": "runtime",
        "requirement":
            "An exact Core ML deployment target with pinned toolchain and "
            "binding identity (coremltools or Swift), version, lock SHA-256, "
            "reviewed license text and a compiled model artifact with SHA-256.",
    },
    {
        "id": "ART-04",
        "kind": "model_assets",
        "requirement":
            "The exact model file set, config and preprocessing asset with "
            "per-file byte count and SHA-256, immutable revision and a "
            "weights-only inspection record.",
    },
    {
        "id": "ART-05",
        "kind": "parity_fixtures",
        "requirement":
            "A deterministic CPU reference input and output hash per "
            "accelerator with an exact declared tolerance and comparisons that "
            "are never pooled across runtimes.",
    },
    {
        "id": "ART-06",
        "kind": "availability_evidence",
        "requirement":
            "An exact host and device profile with cold/warm availability, "
            "device-timing harness, deadline budget and recorded misses for "
            "each accelerator runtime.",
    },
    {
        "id": "ART-07",
        "kind": "rights",
        "requirement":
            "Reviewed runtime licenses, model and training-data terms, output "
            "use, redistribution and per-runtime derivative-output approval.",
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "linked_gates": ["RG-01", "RG-03", "RG-04"],
        "statement":
            "The exact MLX runtime is absent. No ml-explore/mlx checkout or "
            "wheel at an immutable 40-hex revision, version, install root, "
            "package lock, offline load path or reviewed license text exists "
            "in the workspace or home cache.",
        "required_action":
            "Supply ml-explore/mlx at an immutable 40-hex commit with its "
            "version, wheel or source install root, lock SHA-256, offline load "
            "path and reviewed license text; do not substitute a system "
            "framework or an unpinned package.",
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "linked_gates": ["RG-01", "RG-03", "RG-04"],
        "statement":
            "The exact MPS runtime is absent. No PyTorch build with the MPS "
            "backend at an immutable revision, wheel install root, version, "
            "lock, Metal device profile or reviewed license text exists; no "
            "Metal device query has been executed.",
        "required_action":
            "Supply the exact PyTorch build that provides the MPS backend at "
            "an immutable 40-hex commit with version, wheel install root, lock "
            "SHA-256, reviewed license text and a recorded Metal device "
            "profile.",
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "linked_gates": ["RG-01", "RG-03", "RG-04"],
        "statement":
            "The exact Core ML runtime is not admitted. An operating-system "
            "Core ML framework and Xcode toolchain may be observed on the "
            "host, but there is no pinned deployment target, binding identity, "
            "version lock, reviewed license record or compiled model artifact. "
            "The only sibling execution record is an ONNX Runtime Core ML "
            "provider trial that failed in concurrent use and is rejected.",
        "required_action":
            "Supply an exact Core ML deployment target with a pinned "
            "toolchain and binding identity (coremltools or Swift), version, "
            "lock SHA-256, reviewed license text and a compiled model artifact "
            "with SHA-256; an OS framework observation must not be admitted as "
            "a runtime.",
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "linked_gates": ["RG-02", "RG-03", "RG-07"],
        "statement":
            "No exact model or preprocessing asset matching an admitted "
            "accelerator runtime is present. No MLX or MPS model exists, and "
            "the sibling Core ML provider trial's DPDFNet graph, local ONNX "
            "Runtime wheel and patched build are absent, so the adverse trial "
            "cannot be rebuilt or paired.",
        "required_action":
            "Supply the exact model file set, config and preprocessing asset "
            "with per-file byte count and SHA-256 at an immutable revision, "
            "plus a weights-only inspection record.",
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "linked_gates": ["RG-03", "RG-06", "RG-07"],
        "statement":
            "No CPU parity fixture exists. There is no deterministic CPU "
            "reference input or output hash and no declared exact tolerance "
            "for MLX, MPS or Core ML.",
        "required_action":
            "Supply a deterministic CPU reference input and output hash per "
            "accelerator with an exact declared tolerance and per-runtime "
            "comparisons that are never pooled.",
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "linked_gates": ["RG-04", "RG-05", "RG-06", "RG-08"],
        "statement":
            "No availability, device-timing or Tool-control evidence exists. "
            "No exact host or device profile, cold/warm availability "
            "observation, timing harness, deadline budget or miss record "
            "exists; caller-owned inputs, malformed inputs and missing "
            "optional selections are unverified for every accelerator "
            "runtime.",
        "required_action":
            "Supply an exact host and device profile with cold/warm "
            "availability, a device-timing harness, deadline budget and "
            "recorded misses for each accelerator runtime, plus caller-owned "
            "input ownership, malformed-input and missing-optional-selection "
            "controls with the exact command and observed status.",
    },
    {
        "id": "BLK-07",
        "artifact_id": "ART-07",
        "linked_gates": ["RG-02", "RG-05", "RG-07", "RG-08"],
        "statement":
            "Runtime licenses, model terms, training-data provenance, output "
            "use and redistribution rights are unresolved for all three "
            "accelerators. No license text or rights bundle is present.",
        "required_action":
            "Provide reviewed runtime licenses, model and training-data terms, "
            "explicit output use, redistribution and per-runtime "
            "derivative-output approval.",
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "requirement":
            "Exact licensed runtime identity is pinned separately for MLX, MPS "
            "and Core ML: immutable revision, version, install root, lock "
            "SHA-256, provenance and reviewed license text.",
        "reopen_condition":
            "All three runtime identities are supplied, hash-pinned and "
            "reviewed; an OS framework or unpinned package is not accepted.",
    },
    {
        "id": "RG-02",
        "requirement":
            "Exact model, config and preprocessing assets are pinned by "
            "SHA-256 with clear model and training-data rights.",
        "reopen_condition":
            "A weights-only inspection record plus per-file SHA-256 and rights "
            "record exists for the exact model used on each runtime.",
    },
    {
        "id": "RG-03",
        "requirement":
            "CPU parity is measured per accelerator with deterministic inputs, "
            "an exact declared tolerance and output comparisons.",
        "reopen_condition":
            "Per-runtime CPU reference outputs and accelerator outputs match "
            "within the declared tolerance and are reported separately.",
    },
    {
        "id": "RG-04",
        "requirement":
            "Availability and device timing are measured per runtime on the "
            "exact host and device, with cold and warm observations.",
        "reopen_condition":
            "The exact host/device profile, cold/warm availability, timing "
            "harness and miss record are supplied for each runtime.",
    },
    {
        "id": "RG-05",
        "requirement":
            "The Tool profile controls pass: clean install, typical CLI/API "
            "use, caller-owned inputs, malformed inputs and missing optional "
            "selections.",
        "reopen_condition":
            "Each control is recorded as pass or fail with the exact command "
            "and observed status for every runtime.",
    },
    {
        "id": "RG-06",
        "requirement":
            "Compile/build evidence, synthetic runtime evidence and measured "
            "workload support are kept separate and never pooled across "
            "runtimes.",
        "reopen_condition":
            "Separate, labelled evidence exists for build, synthetic runtime "
            "and paced workload, per accelerator, with no pooled result.",
    },
    {
        "id": "RG-07",
        "requirement":
            "An opt-in tool or provider intake is reviewed; nothing is "
            "registered, default-enabled or shared-build enabled.",
        "reopen_condition":
            "An opt-in intake with caller-owned inputs, failure controls and "
            "independent review is accepted without registry or default "
            "changes.",
    },
    {
        "id": "RG-08",
        "requirement":
            "Release approval for any accelerator execution claim or public "
            "adapter exposure.",
        "reopen_condition":
            "Independent exact-head review and hosted checks pass for the "
            "specific runtime and scope; no claim exceeds the evidence.",
    },
)

# ---------------------------------------------------------------------------
# Strict JSON and canonical bytes.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Stable board identity. The mutable board file is read, never pinned.
# ---------------------------------------------------------------------------


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    depends_on = row.get("depends_on")
    if not isinstance(depends_on, list):
        raise ValueError("board_depends_on_not_list")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(depends_on),
    }


def _board_tasks(path: Path | None = None) -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [row for row in _board_tasks(path)
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0], require_component=True)
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    root = by_id.get(TASK)
    if root is None:
        raise ValueError("board_row_absent")
    projection = _project(root, require_component=True)
    result = [projection]
    for dependency in projection["depends_on"]:
        row = by_id.get(dependency)
        if row is None:
            raise ValueError("linked_row_absent:" + dependency)
        result.append(_project(row))
    return tuple(result)


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    value = linked_rows() if rows is None else rows
    return object_digest([dict(row) for row in value])


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TASK_TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "component": COMPONENT_ID,
    }


# ---------------------------------------------------------------------------
# Git scope helpers. The merge-base of this branch bounds committed changes.
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


# ---------------------------------------------------------------------------
# Fixed absence probes and host observations.
# ---------------------------------------------------------------------------


def _workspace_rows(paths: tuple[str, ...], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        if ((AUDIO_ROOT / relative).exists()
                or (WORKTREE / relative).exists()):
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": kind,
            "present": False,
            "admitted": False,
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    return rows


def _home_rows(paths: tuple[str, ...], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        if Path(os.path.expanduser(relative)).exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": kind,
            "present": False,
            "admitted": False,
            "searched_home_cache": True,
        })
    return rows


def _import_available(module: str) -> bool:
    """Report import availability without importing the runtime."""
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def runtime_probe() -> dict:
    accelerators = []
    importable = 0
    for runtime_id in RUNTIME_IDS:
        spec = ACCELERATORS[runtime_id]
        module = spec["top_level_module"]
        available = _import_available(module)
        if available:
            importable += 1
        accelerators.append({
            "runtime_id": runtime_id,
            "display": spec["display"],
            "kind": spec["kind"],
            "upstream": spec["upstream"],
            "status": "blocked_exact_runtime_absent",
            "admitted": False,
            "pinned_install_present": False,
            "package_importable": available,
            "imported_or_executed": False,
            "version_verified": False,
            "lock_present": False,
            "license_verified": False,
            "device_timing_measured": False,
            "required_identity": spec["required_identity"],
            "candidates": _workspace_rows(spec["probe_paths"], runtime_id),
            "home_candidates": _home_rows(spec["home_paths"], runtime_id),
        })
    return {
        "status": "blocked_pinned_runtimes_absent",
        "required_runtime_count": len(RUNTIME_IDS),
        "admitted_runtime_count": 0,
        "any_runtime_admitted": False,
        "package_import_count": importable,
        "imported_or_executed": False,
        "device_timing_measured": False,
        "accelerators": accelerators,
        "host_observation": host_observation(),
    }


def host_observation() -> dict:
    xcrun = Path("/usr/bin/xcrun")
    xcode = Path("/Applications/Xcode.app")
    coreml_observed = xcrun.is_file() or xcode.is_dir()
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "mac_ver": platform.mac_ver()[0],
        "xcrun_present": xcrun.is_file(),
        "xcode_app_present": xcode.is_dir(),
        "coreml_toolchain_observation":
            "observed_not_admitted" if coreml_observed else "not_observed",
        "observation_is_admission": False,
        "metal_device_query_executed": False,
        "device_timing_measured": False,
        "network_used": False,
    }


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    for runtime_id in RUNTIME_IDS:
        spec = ACCELERATORS[runtime_id]
        rows.extend(_workspace_rows(spec["probe_paths"], runtime_id))
        rows.extend(_home_rows(spec["home_paths"], runtime_id))
    return rows


def absence_summary(probes: list[dict]) -> dict:
    return {
        "probe_count": len(probes),
        "admitted_count": sum(1 for row in probes
                              if row.get("admitted") is not False),
        "all_admitted_absent": all(row.get("admitted") is False
                                   for row in probes),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "runtime_imported_or_executed": False,
        "model_loaded": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed synthetic accelerator-execution admission contract.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = "audio-sdk/accelerator-execution-manifest/0.1"
MANIFEST_TOP_KEYS = (
    "schema_id", "runtime", "model", "host", "parity", "availability",
    "controls", "rights",
)
RUNTIME_KEYS = (
    "runtime_id", "version", "revision", "install_path", "install_sha256",
    "lock_sha256", "license_sha256", "provenance_url",
)
MODEL_KEYS = ("model_id", "files", "preprocessing_sha256")
MODEL_FILE_KEYS = ("path", "sha256", "bytes")
HOST_KEYS = ("os_version", "arch", "device", "accelerator_available",
             "metal_version")
PARITY_KEYS = ("cpu_reference_sha256", "accelerator_output_sha256",
               "tolerance", "exact_match")
AVAILABILITY_KEYS = ("cold_start_ms", "warm_ms", "measured")
CONTROL_KEYS = (
    "typical_use", "caller_owned_inputs", "malformed_inputs",
    "missing_optional_selection",
)
RIGHT_KEYS = ("runtime_license", "model_terms", "output_use", "redistribution")
UNRESOLVED_VALUES = {
    "unknown", "pending", "unspecified", "not specified", "not-specified",
    "tbd", "to be determined", "none", "null", "n/a", "noassertion",
}


class _Invalid(Exception):
    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _field(prefix: str, name: str) -> str:
    return prefix + "." + name if prefix else name


def _exact_object(value: Any, fields: tuple[str, ...], prefix: str) -> dict:
    if not isinstance(value, dict):
        raise _Invalid("not_object", prefix or "root")
    missing = [name for name in fields if name not in value]
    if missing:
        raise _Invalid("missing_field", _field(prefix, missing[0]))
    unknown = sorted(name for name in value if name not in fields)
    if unknown:
        raise _Invalid("unknown_field", _field(prefix, unknown[0]))
    return value


def _text(value: Any, field: str, limit: int = 240) -> None:
    if not isinstance(value, str):
        raise _Invalid("invalid_text", field)
    if not value.strip():
        raise _Invalid("empty_text", field)
    if len(value) > limit:
        raise _Invalid("out_of_range", field)
    if any(ord(character) < 32 for character in value):
        raise _Invalid("invalid_text", field)
    if value.strip().lower() in UNRESOLVED_VALUES:
        raise _Invalid("unresolved_value", field)


def _url(value: Any, field: str) -> None:
    if not isinstance(value, str) or not URL.fullmatch(value):
        raise _Invalid("invalid_url", field)


def _sha(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise _Invalid("invalid_sha256", field)


def _hex40(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise _Invalid("invalid_revision", field)


def _version(value: Any, field: str) -> None:
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise _Invalid("invalid_version", field)


def _safe_relative(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise _Invalid("unsafe_path", field)
    if value.startswith("/") or "\\" in value or ":" in value:
        raise _Invalid("unsafe_path", field)
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise _Invalid("unsafe_path", field)


def _bounded_int(value: Any, low: int, high: int, field: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _Invalid("invalid_integer", field)
    if value < low or value > high:
        raise _Invalid("out_of_range", field)


def _boolean(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise _Invalid("invalid_boolean", field)


def _list(value: Any, field: str, low: int, high: int) -> list:
    if not isinstance(value, list):
        raise _Invalid("not_list", field)
    if len(value) < low:
        raise _Invalid("missing_required_value", field)
    if len(value) > high:
        raise _Invalid("out_of_range", field)
    return value


def _rights(block: dict, prefix: str) -> None:
    for key in RIGHT_KEYS:
        _boolean(block[key], _field(prefix, key))
        if block[key] is not True:
            raise _Invalid("rights_not_cleared", _field(prefix, key))


def _controls(block: dict, prefix: str) -> None:
    for key in CONTROL_KEYS:
        _boolean(block[key], _field(prefix, key))
        if block[key] is not True:
            raise _Invalid("control_not_verified", _field(prefix, key))


def _validate_manifest(value: dict) -> str:
    if not isinstance(value, dict):
        raise _Invalid("manifest_not_object", "root")
    assert_no_float(value)
    _exact_object(value, MANIFEST_TOP_KEYS, "")
    if value["schema_id"] != MANIFEST_SCHEMA_ID:
        raise _Invalid("schema_mismatch", "schema_id")

    runtime = _exact_object(value["runtime"], RUNTIME_KEYS, "runtime")
    if runtime["runtime_id"] not in RUNTIME_IDS:
        raise _Invalid("invalid_runtime_id", "runtime.runtime_id")
    _version(runtime["version"], "runtime.version")
    _hex40(runtime["revision"], "runtime.revision")
    _safe_relative(runtime["install_path"], "runtime.install_path")
    _sha(runtime["install_sha256"], "runtime.install_sha256")
    _sha(runtime["lock_sha256"], "runtime.lock_sha256")
    _sha(runtime["license_sha256"], "runtime.license_sha256")
    _url(runtime["provenance_url"], "runtime.provenance_url")

    model = _exact_object(value["model"], MODEL_KEYS, "model")
    _text(model["model_id"], "model.model_id")
    files = _list(model["files"], "model.files", 1, MAX_MODEL_FILES)
    for index, row in enumerate(files):
        prefix = f"model.files[{index}]"
        row = _exact_object(row, MODEL_FILE_KEYS, prefix)
        _safe_relative(row["path"], prefix + ".path")
        _sha(row["sha256"], prefix + ".sha256")
        _bounded_int(row["bytes"], 1, MAX_MODEL_FILE_BYTES, prefix + ".bytes")
    paths = [row["path"] for row in files]
    if paths != sorted(paths):
        raise _Invalid("noncanonical_order", "model.files")
    if len(set(paths)) != len(paths):
        raise _Invalid("duplicate_value", "model.files")
    _sha(model["preprocessing_sha256"], "model.preprocessing_sha256")

    host = _exact_object(value["host"], HOST_KEYS, "host")
    _text(host["os_version"], "host.os_version")
    if host["arch"] not in ARCHES:
        raise _Invalid("invalid_arch", "host.arch")
    _text(host["device"], "host.device")
    _boolean(host["accelerator_available"], "host.accelerator_available")
    if host["accelerator_available"] is not True:
        raise _Invalid("accelerator_unavailable", "host.accelerator_available")
    _text(host["metal_version"], "host.metal_version")
    if runtime["runtime_id"] == "coreml" and not host["metal_version"]:
        raise _Invalid("empty_text", "host.metal_version")

    parity = _exact_object(value["parity"], PARITY_KEYS, "parity")
    _sha(parity["cpu_reference_sha256"], "parity.cpu_reference_sha256")
    _sha(parity["accelerator_output_sha256"],
         "parity.accelerator_output_sha256")
    _bounded_int(parity["tolerance"], 0, MAX_TOLERANCE, "parity.tolerance")
    _boolean(parity["exact_match"], "parity.exact_match")
    if parity["exact_match"] is not True:
        raise _Invalid("parity_not_exact", "parity.exact_match")

    availability = _exact_object(value["availability"], AVAILABILITY_KEYS,
                                 "availability")
    _bounded_int(availability["cold_start_ms"], 0, MAX_DURATION_MS,
                 "availability.cold_start_ms")
    _bounded_int(availability["warm_ms"], 0, MAX_DURATION_MS,
                 "availability.warm_ms")
    _boolean(availability["measured"], "availability.measured")
    if availability["measured"] is not True:
        raise _Invalid("availability_not_measured", "availability.measured")

    controls = _exact_object(value["controls"], CONTROL_KEYS, "controls")
    _controls(controls, "controls")

    rights = _exact_object(value["rights"], RIGHT_KEYS, "rights")
    _rights(rights, "rights")
    return runtime["runtime_id"]


def _accepted(runtime_id: str, checks: int) -> dict:
    return {
        "status": "accepted",
        "code": "accepted",
        "qualifies": False,
        "synthetic_control": True,
        "runtime_id": runtime_id,
        "checks": checks,
    }


def _rejected(code: str, field: str = "") -> dict:
    return {
        "status": "rejected",
        "code": code,
        "field": field,
        "qualifies": False,
    }


def validate_manifest(value: Any) -> dict:
    """Validate one accelerator-execution manifest; admission never qualifies."""
    try:
        runtime_id = _validate_manifest(value)
    except _Invalid as error:
        return _rejected(error.code, error.field)
    except ValueError as error:
        return _rejected(str(error).split(":", 1)[0])
    return _accepted(runtime_id, 8)


def validate_manifest_text(payload: str) -> dict:
    try:
        value = loads_strict(payload)
    except ValueError as error:
        return _rejected(str(error).split(":", 1)[0])
    return validate_manifest(value)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "runtime": {
            "runtime_id": "mlx",
            "version": "0.29.3",
            "revision": "0123456789abcdef0123456789abcdef01234567",
            "install_path": "data/runtimes/mlx/0.29.3",
            "install_sha256": "a" * 64,
            "lock_sha256": "b" * 64,
            "license_sha256": "c" * 64,
            "provenance_url": "https://example.invalid/synthetic/mlx",
        },
        "model": {
            "model_id": "synthetic-schema-control-model",
            "files": [
                {"path": "model.safetensors", "sha256": "d" * 64,
                 "bytes": 1024},
            ],
            "preprocessing_sha256": "e" * 64,
        },
        "host": {
            "os_version": "macOS 27.2.1",
            "arch": "arm64",
            "device": "synthetic schema control device",
            "accelerator_available": True,
            "metal_version": "4.0",
        },
        "parity": {
            "cpu_reference_sha256": "f" * 64,
            "accelerator_output_sha256": "f" * 64,
            "tolerance": 0,
            "exact_match": True,
        },
        "availability": {
            "cold_start_ms": 0,
            "warm_ms": 0,
            "measured": True,
        },
        "controls": {
            "typical_use": True,
            "caller_owned_inputs": True,
            "malformed_inputs": True,
            "missing_optional_selection": True,
        },
        "rights": {
            "runtime_license": True,
            "model_terms": True,
            "output_use": True,
            "redistribution": True,
        },
    }


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "duplicate_keys_rejected": True,
        "floats_rejected": True,
        "nonfinite_rejected": True,
        "unknown_fields_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "runtime_or_model_invoked": False,
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "runtime_fields": list(RUNTIME_KEYS),
        "model_fields": list(MODEL_KEYS),
        "host_fields": list(HOST_KEYS),
        "parity_fields": list(PARITY_KEYS),
        "availability_fields": list(AVAILABILITY_KEYS),
        "control_fields": list(CONTROL_KEYS),
        "right_fields": list(RIGHT_KEYS),
        "runtime_ids": list(RUNTIME_IDS),
        "arches": list(ARCHES),
        "max_model_files": MAX_MODEL_FILES,
        "max_model_file_bytes": MAX_MODEL_FILE_BYTES,
        "max_duration_ms": MAX_DURATION_MS,
        "max_tolerance": MAX_TOLERANCE,
    }


def _admission_cases() -> list[dict]:
    base = _manifest_control()
    cases: list[dict] = []

    def add(case_id: str, result: dict, mutation: str = "") -> None:
        row = {
            "id": case_id,
            "status": result["status"],
            "code": result["code"],
            "qualifies": False,
            "state_unchanged": True,
        }
        if result.get("field"):
            row["field"] = result["field"]
        if mutation:
            row["mutation"] = mutation
        cases.append(row)

    def mutated(case_id: str, mutation: str, apply) -> None:
        value = copy.deepcopy(base)
        apply(value)
        add(case_id, validate_manifest(value), mutation)

    add("accepted-schema-control", validate_manifest(copy.deepcopy(base)))
    add("root-not-object", validate_manifest(["not", "an", "object"]))
    mutated("missing-runtime", "remove runtime",
            lambda value: value.pop("runtime"))
    mutated("unknown-top-field", "add unknown field",
            lambda value: value.update({"provider": "x"}))
    mutated("wrong-schema-id", "replace schema_id",
            lambda value: value.update({"schema_id": "audio-sdk/other/0.1"}))
    mutated("invalid-runtime-id", "set runtime_id to metal",
            lambda value: value["runtime"].update({"runtime_id": "metal"}))
    mutated("invalid-version", "set version to a range",
            lambda value: value["runtime"].update({"version": ">=0.29"}))
    mutated("invalid-revision", "set short revision",
            lambda value: value["runtime"].update({"revision": "abc123"}))
    mutated("invalid-install-sha", "truncate install hash",
            lambda value: value["runtime"].update({"install_sha256": "abc"}))
    mutated("unsafe-install-path", "use an absolute install path",
            lambda value: value["runtime"].update(
                {"install_path": "/opt/mlx"}))
    mutated("invalid-provenance-url", "use an insecure URL",
            lambda value: value["runtime"].update(
                {"provenance_url": "http://example.invalid/mlx"}))
    mutated("missing-model-files", "remove model files",
            lambda value: value["model"].pop("files"))
    mutated("empty-model-files", "empty model file list",
            lambda value: value["model"].update({"files": []}))
    mutated("model-file-bytes-zero", "zero byte count",
            lambda value: value["model"]["files"][0].update({"bytes": 0}))
    mutated("model-file-bytes-not-int", "string byte count",
            lambda value: value["model"]["files"][0].update({"bytes": "1024"}))
    mutated("duplicate-model-file-path", "duplicate a file path",
            lambda value: value["model"]["files"].append(
                dict(value["model"]["files"][0])))
    mutated("unsorted-model-files", "reverse file order",
            lambda value: value["model"].update({"files": [
                {"path": "z.safetensors", "sha256": "d" * 64, "bytes": 1},
                {"path": "a.safetensors", "sha256": "d" * 64, "bytes": 1},
            ]}))
    mutated("model-path-traversal", "traverse above the install root",
            lambda value: value["model"]["files"][0].update(
                {"path": "../model.safetensors"}))
    mutated("invalid-arch", "use an unrecorded architecture",
            lambda value: value["host"].update({"arch": "ppc64"}))
    mutated("accelerator-unavailable", "mark the accelerator unavailable",
            lambda value: value["host"].update(
                {"accelerator_available": False}))
    mutated("invalid-boolean", "use an integer for availability",
            lambda value: value["host"].update(
                {"accelerator_available": 1}))
    mutated("empty-metal-version", "use an empty Metal version",
            lambda value: value["host"].update({"metal_version": ""}))
    mutated("parity-not-exact", "mark parity inexact",
            lambda value: value["parity"].update({"exact_match": False}))
    mutated("negative-tolerance", "use negative tolerance",
            lambda value: value["parity"].update({"tolerance": -1}))
    mutated("availability-not-measured", "mark timing unmeasured",
            lambda value: value["availability"].update({"measured": False}))
    mutated("negative-warm-ms", "use negative warm timing",
            lambda value: value["availability"].update({"warm_ms": -1}))
    mutated("missing-control", "remove a control",
            lambda value: value["controls"].pop("typical_use"))
    mutated("control-not-verified", "mark malformed inputs unverified",
            lambda value: value["controls"].update({"malformed_inputs": False}))
    mutated("rights-not-cleared", "mark output use unapproved",
            lambda value: value["rights"].update({"output_use": False}))
    mutated("unresolved-model-id", "use an unresolved token",
            lambda value: value["model"].update({"model_id": "tbd"}))
    mutated("float-value", "use a float tolerance",
            lambda value: value["parity"].update({"tolerance": 1.5}))

    add("duplicate-json-key",
        validate_manifest_text('{"schema_id": "a", "schema_id": "b"}'))
    add("nonfinite-nan", validate_manifest_text('{"schema_id": NaN}'))
    add("nonfinite-infinity",
        validate_manifest_text('{"schema_id": Infinity}'))
    add("invalid-json", validate_manifest_text("{"))
    add("json-root-not-object", validate_manifest_text("[]"))
    return cases


def admission_controls() -> dict:
    cases = _admission_cases()
    accepted = [case for case in cases if case["status"] == "accepted"]
    rejected = [case for case in cases if case["status"] == "rejected"]
    return {
        "controls": admission_contract_block(),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(rejected),
            "accepted_schema_controls": len(accepted),
            "qualifying_results": 0,
            "all_adverse_cases_rejected": len(rejected) == len(cases) - 1,
            "state_advanced_on_rejection": False,
            "accepted_control_qualifies": False,
            "runtime_invoked": False,
            "model_loaded": False,
            "audio_read": False,
            "device_timing_measured": False,
        },
    }


# ---------------------------------------------------------------------------
# Evidence blocks.
# ---------------------------------------------------------------------------


def profile_source() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Tool |")]
    if len(rows) != 1:
        raise ValueError("profile_row_not_unique")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("profile_phrase_missing:" + phrase)
    return {
        "profile": PROFILE_KEY,
        "key": PROFILE,
        "source": PROFILE_SOURCE_REL,
        "sha256": sha256_file(path),
        "heading": "Acceptance profiles",
        "row": row,
        "phrases": list(PROFILE_PHRASES),
    }


def disposition_block() -> dict:
    return {
        "status": "incomplete",
        "decision": "DEFER",
        "promotion": "defer",
        "production_exposure": "DEFER",
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "defer_before": "opt_in_tool_or_provider_exposure",
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "task_local_only": True,
        "provider_registration": False,
        "registered": False,
        "descriptor_registry_change": False,
        "default_enabled": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "board_changed": False,
        "handoff_changed": False,
        "files_outside_task_directory_written": False,
    }


def scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "provider_source_written": False,
        "fixture_written": False,
        "tooling_entry_point_added": False,
        "shared_registry_changed": False,
        "default_path_changed": False,
        "network_used": False,
        "model_downloaded": False,
        "runtime_installed": False,
        "audio_read": False,
        "inference_performed": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "directory": TASK_PREFIX,
        "runtimes": list(RUNTIME_IDS),
        "runtime_count": len(RUNTIME_IDS),
        "separate_runtime_reporting_required": True,
        "cpu_parity_required_per_runtime": True,
        "availability_required_per_runtime": True,
        "pooled_runtime_result_permitted": False,
        "os_framework_observation_is_admission": False,
        "provided_adapter_entry_point": False,
        "reproducible_setup_documented": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def accelerator_geometry() -> dict:
    return {
        "runtime_ids": list(RUNTIME_IDS),
        "runtime_count": len(RUNTIME_IDS),
        "separate_runtime_reporting_required": True,
        "cpu_parity_required_per_runtime": True,
        "availability_required_per_runtime": True,
        "pooled_runtime_result_permitted": False,
        "runtime_identity_pinned": False,
        "model_present": False,
        "runtime_present": False,
        "executed": False,
        "version_pinned": False,
        "device_timing_measured": False,
        "workload_support_measured": False,
        "cpu_parity_measured": False,
        "os_framework_observation_is_admission": False,
        "installed_v0": False,
        "provider_registered": False,
    }


def upstream_record() -> dict:
    return {
        "evidence_path": "adapters/reuse-mlx/README.md",
        "evidence_sha256": SOURCE_PINS["adapters/reuse-mlx/README.md"],
        "adapter_protocol_version": 1,
        "adapter_identity": "nvidia-reuse-swift-mlx-cli-v1",
        "source_reported_port": "PositiveLoss/re-use-swift-mlx",
        "source_reported_port_revision":
            "362be1ade00c3fcc534639df1d10c72d7e4a9e02",
        "source_reported_checkpoint": "nvidia/Real-time_RE-USE",
        "source_reported_checkpoint_revision":
            "4c0c186272ca853cd18d832fc5c28777b62f32d1",
        "source_reported_platform": "Swift 6.1 or newer, macOS 14 or newer, "
                                   "Apple Silicon",
        "source_reported_compute": "BF16, 16 kHz mono, exit_layer=8, zero "
                                   "look-ahead frames",
        "adapter_observed": True,
        "adapter_admitted": False,
        "runtime_pinned": False,
        "runtime_lock_sha256": None,
        "pinned_model_sha256": None,
        "model_present": False,
        "executed": False,
        "digest_asserted": False,
        "rights_cleared": False,
        "evidence_is_adjacent_adapter_only": True,
        "reproduced_here": False,
        "admitted_as_result": False,
    }


def tool_profile_block() -> dict:
    return {
        "profile": PROFILE_KEY,
        "status": "blocked",
        "qualifies": False,
        "rows": [dict(row) for row in TOOL_REQUIREMENTS],
        "version_and_install_recorded": False,
        "provenance_recorded": False,
        "clean_checkout_or_package_verified": False,
        "typical_cli_or_api_use_performed": False,
        "caller_owned_inputs_verified": False,
        "malformed_inputs_rejected": False,
        "missing_optional_selection_verified": False,
        "compile_build_evidence_separated": False,
        "synthetic_runtime_evidence_present": False,
        "measured_workload_support": False,
        "mlx_cpu_parity_measured": False,
        "mps_cpu_parity_measured": False,
        "coreml_cpu_parity_measured": False,
        "mlx_availability_measured": False,
        "mps_availability_measured": False,
        "coreml_availability_measured": False,
        "cross_runtime_pooling_prohibited": True,
    }


def required_artifacts() -> list[dict]:
    rows = []
    for row in REQUIRED_ARTIFACTS:
        rows.append({
            "id": row["id"],
            "kind": row["kind"],
            "requirement": row["requirement"],
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
        })
    return rows


def exact_blockers() -> list[dict]:
    rows = []
    for row in EXACT_BLOCKERS:
        rows.append({
            "id": row["id"],
            "artifact_id": row["artifact_id"],
            "status": "open",
            "qualifies": False,
            "linked_gates": list(row["linked_gates"]),
            "statement": row["statement"],
            "required_action": row["required_action"],
        })
    return rows


def release_gates() -> list[dict]:
    rows = []
    for row in RELEASE_GATES:
        rows.append({
            "id": row["id"],
            "requirement": row["requirement"],
            "status": "blocked",
            "qualifies": False,
            "reopen_condition": row["reopen_condition"],
            "linked_row": _gate_link(),
        })
    return rows


def rights_gap() -> dict:
    return {
        "status": "unresolved",
        "qualifies": False,
        "runtime_licenses": False,
        "model_terms": False,
        "training_data_provenance": False,
        "output_use": False,
        "redistribution": False,
        "per_runtime_output_approval": False,
        "license_texts_present": False,
        "rights_bundle_present": False,
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "required_runtime_count": len(RUNTIME_IDS),
        "admitted_runtime_count": 0,
        "qualifying_results": 0,
        "missing_result_qualifies": False,
        "external_blocker_accepted_as_investigation_handoff": True,
        "conditional_implementation_closed": False,
    }


def historical_evidence_block() -> dict:
    trial = "realtime-audio-library/evaluation/cpu_saving_20261031/"
    return {
        "status": "sibling_coreml_ep_trial_rejected_no_qualifying_execution",
        "qualifies": False,
        "no_values_inferred_from_adjacent_tasks": True,
        "entries": [
            {
                "id": "HIST-01",
                "runtime": "coreml",
                "mechanism": "onnxruntime_coreml_execution_provider",
                "path": trial + "README.md",
                "sha256": SOURCE_PINS[trial + "README.md"],
                "runtime_version_reported": "ONNX Runtime 1.31.1",
                "partitioned_nodes": 312,
                "graph_nodes": 319,
                "partitions": 4,
                "single_stream_clean": True,
                "eight_stream_clean": False,
                "sixteen_stream_clean": False,
                "paired_cpu_baseline": False,
                "reproducible_library_build": False,
                "concurrent_use_rejected": True,
                "recorded_failure": "GetElementType is not implemented",
                "admitted_as_result": False,
                "qualifies": False,
                "reason":
                    "The sibling record explicitly rejects this Core ML "
                    "provider configuration for concurrent library use. The "
                    "single-stream latency has no paired CPU baseline, and the "
                    "model, local ONNX Runtime wheel and patched build are "
                    "absent, so it cannot be rebuilt or admitted.",
                "artifacts": [
                    trial + "coreml_trial/coreml_1s.json",
                    trial + "coreml_trial/coreml_8s_8e.json",
                    trial + "coreml_trial/coreml_16s_8e.json",
                    trial + "coreml_trial/dpdfnet_coreml_trial.patch",
                ],
            },
            {
                "id": "HIST-02",
                "runtime": "mlx",
                "mechanism": "community_swift_mlx_cli_adapter",
                "path": "adapters/reuse-mlx/README.md",
                "sha256": SOURCE_PINS["adapters/reuse-mlx/README.md"],
                "adapter_protocol_version": 1,
                "port_revision_reported":
                    "362be1ade00c3fcc534639df1d10c72d7e4a9e02",
                "checkpoint_revision_reported":
                    "4c0c186272ca853cd18d832fc5c28777b62f32d1",
                "runtime_pinned": False,
                "weights_present": False,
                "single_stream_clean": None,
                "paired_cpu_baseline": False,
                "admitted_as_result": False,
                "qualifies": False,
                "reason":
                    "The adapter names an unpinned MLX runtime and absent "
                    "NVIDIA checkpoint; it supplies no generic MLX execution, "
                    "CPU parity or availability evidence.",
            },
            {
                "id": "HIST-03",
                "runtime": "mps",
                "mechanism": "none_found",
                "path": None,
                "sha256": None,
                "runtime_pinned": False,
                "single_stream_clean": None,
                "paired_cpu_baseline": False,
                "admitted_as_result": False,
                "qualifies": False,
                "reason":
                    "No MPS backend or Metal Performance Shaders execution "
                    "record exists in the reviewed workspace evidence.",
            },
        ],
        "source_reported_context": {
            "source": trial + "README.md",
            "runtime": "ONNX Runtime CoreML execution provider on DPDFNet",
            "concurrent_result": "rejected by the sibling record",
            "reproduced_here": False,
            "admitted_as_result": False,
        },
    }


def linked_identity_block() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
    }


def pin_rows(mapping: dict[str, str], root: Path) -> dict:
    rows = {}
    for relative, expected in sorted(mapping.items()):
        actual = sha256_file(root / relative)
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return rows


# ---------------------------------------------------------------------------
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": accelerator_geometry(),
        "upstream_record": upstream_record(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
        "board_row_projection": board_row_projection(),
        "board_row_sha256": board_row_digest(board_row_projection()),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "rights_gap": rights_gap(),
        "tool_profile": tool_profile_block(),
        "tool_profile_requirements": [dict(row) for row in TOOL_REQUIREMENTS],
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "admission_contract": admission_contract_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": list(NON_CLAIMS),
        "write_scope": WRITE_SCOPE,
        "qualification": qualification_block(),
    }


def build_report() -> dict:
    contract = build_contract()
    probes = absence_probes()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "component_id": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": accelerator_geometry(),
        "upstream_record": upstream_record(),
        "runtime_probe": runtime_probe(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": [row["id"] for row in release_gates()],
        "linked_row_identity": linked_identity_block(),
        "tool_profile": tool_profile_block(),
        "tool_profile_requirements": [dict(row) for row in TOOL_REQUIREMENTS],
        "qualification": qualification_block(),
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": "Python 3, standard library only",
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
            "model_required": False,
            "commands": [
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
        },
        "write_scope": WRITE_SCOPE,
    }


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_mismatch")
    if contract.get("contract_id") != CONTRACT_ID:
        raise ValueError("contract_id_mismatch")
    if contract.get("task") != TASK:
        raise ValueError("contract_task_mismatch")
    if contract.get("title") != TASK_TITLE:
        raise ValueError("contract_title_mismatch")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component_mismatch")
    if contract.get("mode") != MODE:
        raise ValueError("contract_mode_mismatch")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch_mismatch")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_mismatch")
    if contract.get("profile") != PROFILE:
        raise ValueError("contract_profile_mismatch")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status_mismatch")
    if contract.get("decision") != DECISION:
        raise ValueError("contract_decision_mismatch")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification_mismatch")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    if contract.get("source_pins") != SOURCE_PINS:
        raise ValueError("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != BOUNDARY_PINS:
        raise ValueError("contract_boundary_pins_mismatch")
    if contract.get("admission_contract") != admission_contract_block():
        raise ValueError("contract_admission_contract_mismatch")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    if [row.get("id") for row in gates] != ["RG-0" + str(i)
                                             for i in range(1, 9)]:
        raise ValueError("contract_gate_ids")
    for row in gates:
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked:" + str(row.get("id")))
        if row.get("linked_row") != _gate_link():
            raise ValueError("contract_gate_link")
    blockers = contract.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open:" + str(row.get("id")))
        if not row.get("linked_gates"):
            raise ValueError("contract_blocker_unlinked:" + str(row.get("id")))
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(
            REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True):
            raise ValueError("contract_artifact_not_blocked:" +
                             str(row.get("id")))
    qualification = contract.get("qualification", {})
    if (qualification.get("status") != QUALIFICATION_STATUS
            or qualification.get("readiness") != "incomplete"
            or qualification.get("all_release_gates_blocked") is not True
            or qualification.get("admitted_runtime_count") != 0):
        raise ValueError("contract_qualification_invalid")
    profile = contract.get("tool_profile", {})
    if profile.get("profile") != PROFILE_KEY or profile.get("status") != \
            "blocked" or profile.get("qualifies") is not False:
        raise ValueError("contract_tool_profile_invalid")
    for key, value in profile.items():
        if key in ("profile", "rows", "status", "qualifies",
                   "cross_runtime_pooling_prohibited"):
            continue
        if value is not False:
            raise ValueError("contract_tool_profile_claim:" + key)
    assert_no_float(contract)
