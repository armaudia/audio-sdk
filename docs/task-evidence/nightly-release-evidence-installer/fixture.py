# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local fixture for nightly-release / Python+C installer evidence.

This is **proposal-only**, synthetic and **not qualified**. It extends the
existing local package/conformance record (``docs/acceptance-matrix.md`` and
``docs/task-evidence/s06.md``, ``s07-build-identity.md``, ``s08.md``) with a
task-local matrix for ``Python wheel + installed C consumer``. It changes no
CI, build file, release workflow, public API/ABI, registry default, advertised
support or installed v0 behavior. The documented boundary stays **16 kHz,
mono, float32, 160 samples per call**.

The module has two independent parts:

* ``OBSERVED`` -- frozen constants transcribed verbatim from a real local run
  on the pinned host. These are *records*, not re-executed here.
* a pure-stdlib reference model of the v0 delivery boundary that consumes the
  same deterministic seeded synthetic frames and cross-checks boundary
  metadata (counts, flags, source mapping, state, rejection behavior) against
  the recorded observations. Native provider DSP output digests are never
  reproduced or invented by this model.

No corpus, weights, download, licensed runtime, device, network benchmark,
signing key, nightly feed or release publication is used.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Optional, Sequence

CONTRACT_ID = "audio-sdk/nightly-release-evidence-installer/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/nightly-release-evidence-installer/report/0.1"

BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
PINNED_PYTHON = "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12"
TASK_PREFIX = "docs/task-evidence/nightly-release-evidence-installer/"

# Fixed public v0 geometry; nothing here advertises a wider runtime.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SEED_SYNTHETIC = 31337
SYNTHETIC_FRAMES = 8
SYNTHETIC_SAMPLES = SYNTHETIC_FRAMES * FRAME_SAMPLES

FLAG_STARTUP_PADDING = 1

# Provider boundary metadata taken from the installed conformance descriptors.
# This is recorded context only: no provider is registered, enabled or changed.
PROVIDER_BOUNDARY: dict[str, dict[str, Any]] = {
    "dsp.highpass80.v0": {
        "declared_delay_samples": 0,
        "startup_padding_outputs": 0,
        "drain_frames": 0,
        "registered_by_this_task": False,
        "enabled_by_default_by_this_task": False,
        "descriptor_settings": {},
    },
    "speex.ns.v0": {
        "declared_delay_samples": 160,
        "startup_padding_outputs": 1,
        "drain_frames": 1,
        "registered_by_this_task": False,
        "enabled_by_default_by_this_task": False,
        "descriptor_settings": {},
    },
}

# External bytes are resolved relative to the workspace source root; worktree
# paths are relative to the SDK worktree root. All digests were observed 2026-11-24.
SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "audio-benchmark-platform/audio-sdk/RELEASING.md",
        "root": "source",
        "sha256": "67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3",
        "summary": "Release policy pinned exactly: tags, approval, archive checksums, attestation, draft-first publication; PyPI/benchmark/model distribution not enabled.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Public v0 boundary: 16 kHz, mono, float32, 160 samples per call; source mapping and sample-conservation rules.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Tool acceptance profile: version/install/provenance, clean checkout or package, one typical use, caller-owned inputs, malformed inputs, missing optional selections, separated support classes.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/check.py",
        "root": "source",
        "sha256": "5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539",
        "summary": "Read-only board validator used for the final check (never edited by this task).",
    },
    {
        "path": "docs/acceptance-matrix.md",
        "root": "worktree",
        "sha256": "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
        "summary": "Existing package/conformance matrix extended here; local macOS arm64 only, no Linux/hosted CI, S12 excluded.",
    },
    {
        "path": "docs/task-evidence/s06.md",
        "root": "worktree",
        "sha256": "6edef4993e22512157cd9a99ffda6d8551da31f388461e6b2cc2f5f0b8bf7620",
        "summary": "Historical installed-package/conformance record and sealed-archive digest; pinned context, not resealed here.",
    },
    {
        "path": "docs/task-evidence/s07-build-identity.md",
        "root": "worktree",
        "sha256": "10efd7bacc3566b638a40a45d6876abf365be5ad7287b0f35a91ddf2b23a7d3a",
        "summary": "Historical build-identity/package-sealing record; reproducibility explicitly open.",
    },
    {
        "path": "docs/task-evidence/s08.md",
        "root": "worktree",
        "sha256": "6fa3622269f48b7366dd89c1dc25f9f8a857a2e1bf6dd222578c8a18d2a37c3f",
        "summary": "Historical Python wheel/venv evidence (CPython 3.12.16, 4/4 tests); extended by this task without changing advertised support.",
    },
    {
        "path": "docs/evidence-handoff.md",
        "root": "worktree",
        "sha256": "05ffddfecec4679fbd0f4ec1e1814bd8f4fb00ede69f787e4e8bd19784502f72",
        "summary": "Existing evidence-handoff procedure; no bundle was published from this task-local fixture.",
    },
    {
        "path": "REUSE.toml",
        "root": "worktree",
        "sha256": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
        "summary": "Aggregate docs/** Apache-2.0 annotation relied on by the licensing check.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary; unchanged.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade ABI boundary used by the installed C/C++ consumer; unchanged.",
    },
    {
        "path": "bindings/python/pyproject.toml",
        "root": "worktree",
        "sha256": "0f3b1e736dd807a984cbb9daa10cd0ba32668f7833994c3c4f0a5021799c95a4",
        "summary": "Wheel metadata: audio-sdk 0.1.0, requires-python >=3.12,<3.12, no dependencies.",
    },
    {
        "path": "bindings/python/audio_sdk/__init__.py",
        "root": "worktree",
        "sha256": "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
        "summary": "Installed ctypes binding; requires an explicit AUDIO_SDK_LIBRARY absolute path, no implicit lookup.",
    },
    {
        "path": "bindings/python/tests/test_sdk.py",
        "root": "worktree",
        "sha256": "32c4cecab24b00fc3be312f64e9def05a5391b0f475cd9d461321e8fc4d4c101",
        "summary": "Installed-package unittest suite; 5 tests in this checkout (historical record said 4).",
    },
    {
        "path": "conformance/main.c",
        "root": "worktree",
        "sha256": "71cf0c7a480ef384e0f1500a5af3c35ed85c9a17625efa3d0d09fddb458287ea",
        "summary": "Installed conformance executable source; 40 checks per built-in provider observed locally.",
    },
    {
        "path": "conformance/evidence/positive/input.json",
        "root": "worktree",
        "sha256": "a112e8c106b4b013f8fdf16af325e3d60b7ee4666bb3e57deec9bb1749369492",
        "summary": "In-tree positive evidence-handoff fixture; synthetic placeholder, pinned as boundary context only.",
    },
    {
        "path": "conformance/evidence/negative/input.json",
        "root": "worktree",
        "sha256": "1d465ecb667a8979a2256da02f060c59827ea213ec45afb592b67c452a331d52",
        "summary": "In-tree negative evidence-handoff fixture with a failed quality check; pinned as context only.",
    },
    {
        "path": "conformance/evidence/incomplete/input.json",
        "root": "worktree",
        "sha256": "fdc30570da1cc70c6c387bec1391a8856d96d29ab3043225a6fbd81ced12b1d6",
        "summary": "In-tree incomplete evidence-handoff fixture; pinned as context only.",
    },
    {
        "path": "scripts/verify_install.sh",
        "root": "worktree",
        "sha256": "6a0737031697c7e4551a294c6df3185b0e6a6101c86143341c57c9b620cae390",
        "summary": "Source of the exact installed C11/C++20 consumer and provider-selection commands reproduced by tooling.py.",
    },
    {
        "path": "scripts/package.sh",
        "root": "worktree",
        "sha256": "b9f9e52cc5e36fec03ab01e81bcfa45de87be4faae71f44922a7446e40a132e2",
        "summary": "Sealed-candidate packer; NOT run by this task (requires a clean tracked checkout and creates release candidates).",
    },
)

TOOL_PINS: dict[str, Any] = {
    "python": "3.12.16",
    "python_executable": PINNED_PYTHON,
    "pip": "25.0.1",
    "setuptools": "84.2.1",
    "wheel": "0.48.0",
    "cmake": "3.27.4",
    "c_compiler": "AppleClang 21.0.0.21000401",
    "cxx_compiler": "AppleClang 21.0.0.21000401",
    "system": "Darwin",
    "machine": "arm64",
    "build_type": "Release",
    "network": False,
}

# Frozen observations from one real local run on the pinned host. These are
# recorded bytes/counts, not claims of cross-host reproducibility or release.
OBSERVED: dict[str, Any] = {
    "clean_checkout": {
        "head": BASE_COMMIT,
        "branch": "swarm/SDK-NIGHTLY-RELEASE-EVIDENCE-AND-PYTHON-C-INSTALLER",
        "status_before_build": "clean",
        "build_dir_outside_worktree": True,
        "sealed_candidate_created": False,
    },
    "compile_build": {
        "cmake_configure_exit": 0,
        "cmake_build_exit": 0,
        "ctest_total": 11,
        "ctest_pass": 11,
        "ctest_fail": 0,
        "ctest_skip": 0,
        "build_id": "audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972",
        "flags_sha256": "sha256:50c2908b322a12ae63e27513cd410764c0a501c9bb6e997eab5ed0ab8d480e00",
        "runtime_inputs_sha256": "sha256:7ea8e578b62ce5878b65b3180b1be7728ea70e3c7902c42bdc59f5400c874ffa",
        "target": "Darwin-arm64",
        "build_info_sha256": "5848b1c126a662da24ad9a30c77581e0ca798e8a42eefad1bda55971a6f957b2",
    },
    "native_install": {
        "cmake_install_exit": 0,
        "dylib_sha256": "4db4ee75061e47513530ed1ce37de63867c41f9560d51d7aff21ff44796a3d5f",
        "static_lib_sha256": "caafbbeaf0463ae7634eacb20dc0d153a7c1f89dd6e87a526025b3a94cf18384",
        "installed_consumer_c11_compile_exit": 0,
        "installed_consumer_cxx20_compile_exit": 0,
        "installed_consumer_c_run_exit": 0,
        "installed_consumer_cxx_run_exit": 0,
        "warnings_as_errors": True,
        "header": "audio_sdk/session_v0.h",
        "link_library": "libaudio_sdk",
    },
    "installed_conformance": {
        "speex.ns.v0": {
            "exit": 0,
            "result": "pass",
            "checks_pass": 40,
            "checks_fail": 0,
            "checks_skip": 0,
            "report_sha256": "accbe82e7460ec79a66f29b8b7b791a3d1cf7da56cf5d432a0f60de00c30f529",
        },
        "dsp.highpass80.v0": {
            "exit": 0,
            "result": "pass",
            "checks_pass": 40,
            "checks_fail": 0,
            "checks_skip": 0,
            "report_sha256": "d8f5963cd949e4c7654c84a152ef0911256d282f042f846966f9f7d1220311ea",
        },
    },
    "python_wheel": {
        "build_exit": 0,
        "install_exit": 0,
        "wheel_name": "audio_sdk-0.1.0-py3-none-any.whl",
        "wheel_sha256": "fc7012d6bdc441e9c19c932833bff5bc607ee6fb9351493f1f52713cfc8a91d5",
        "second_build_sha256": "c8a6fbe39ee545f3f7bdfb93e20329e90225b89e932b64590cd450917d2d58b7",
        "third_build_sha256_from_tooling_run": "0716f91e12dd417b0fe8ccd7c9973f12a4d85afea08a459a20c9d3927d56a9b6",
        "byte_reproducible_across_builds": False,
        "clean_venv": True,
        "source_tree_import": False,
        "installed_tests_total": 5,
        "installed_tests_pass": 5,
        "installed_tests_fail": 0,
        "installed_tests_skip": 0,
        "installed_test_names": (
            "test_ctypes_layouts",
            "test_process_errors_and_finite_drain",
            "test_python_arguments_do_not_wrap_at_native_integer_boundary",
            "test_reset_increments_epoch",
            "test_switch_and_timing_metadata",
        ),
        "library_env": "AUDIO_SDK_LIBRARY",
    },
    "synthetic_runtime_probe": {
        "frames": SYNTHETIC_FRAMES,
        "samples": SYNTHETIC_SAMPLES,
        "input_digest_f32": "dde869989a497e3f522af8ab20bf1124ee0690f2740882a98b726eff07039324",
        "runs": 2,
        "byte_identical_across_runs": True,
        "probe_output_sha256": "344dff2f98cd7c856c3721f115ded222653637f81a8c349e627d7722be06e5cf",
        "providers": {
            "dsp.highpass80.v0": {
                "declared_delay_samples": 0,
                "produced_samples": 1280,
                "valid_samples": 1280,
                "drain_frames": 0,
                "output_digest_f32": "586fb886a72e83664c91fd1f5b14fea57fcf25069fcd3c9709b87a7f0b37abc9",
                "flags": [0] * 8,
                "source_first_samples": [0, 160, 320, 480, 640, 800, 960, 1120],
                "epochs": [1] * 8,
                "all_finite": True,
                "caller_inputs_unchanged": True,
            },
            "speex.ns.v0": {
                "declared_delay_samples": 160,
                "produced_samples": 1280,
                "valid_samples": 1120,
                "drain_frames": 1,
                "output_digest_f32": "a3e8f15e622c07310363bf3ba74945ef57dc05a178a84ec41b1ad82ae3251527",
                "flags": [1, 0, 0, 0, 0, 0, 0, 0],
                "source_first_samples": [-160, 0, 160, 320, 480, 640, 800, 960],
                "epochs": [1] * 8,
                "all_finite": True,
                "caller_inputs_unchanged": True,
            },
        },
        "malformed": {
            "short_frame": {"status": "ValueError", "state_intact": True},
            "nonnumeric_valid_count": {"status": "ValueError", "state_intact": True},
            "negative_epoch": {"status": "ValueError", "state_intact": True},
        },
        "missing_optional": {
            "unknown_provider_id": {"status": "RuntimeError"},
            "unset_library_env": {
                "status": "OSError",
                "message": "set AUDIO_SDK_LIBRARY to an explicit SDK library path",
            },
            "wrong_library_path": {
                "status": "OSError",
                "message": "AUDIO_SDK_LIBRARY must name an existing absolute path",
            },
        },
    },
    "historical_context": {
        "s06_sealed_archive_sha256": "82bb8f64c882b77a51e708bac0c79eae586c07cb0e96c84c8a9388d2100a387e",
        "s08_wheel_sha256": "ea4ce935f2ea2938f3b8a5fa243e0952038f0a8bc6f9fc56c0602dd705fda290",
        "s07_current_build_id": "audio-sdk/0.1.0+sha256:307f828cafb1328d0872c293ae50e89fcf17411da8e327ed4943a6c3f8a8c9c2",
        "s07_candidate07_build_id": "audio-sdk/0.1.0+sha256:fe66742bc610c4a1d27439c127908d803bc14555c6009a98d3339d594dc8d800",
        "acceptance_matrix_ctest": "10/10",
        "acceptance_matrix_python_tests": "4/4",
    },
}

# Explicit blocked gates. No result in this fixture can promote any of them.
BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "actual_nightly_publication",
        "status": "blocked",
        "reason": "No nightly feed, upload, registry push, publish command or hosted run was performed. RELEASING.md uses v0.1.0/rc tags with approval; no nightly channel is defined or exercised here.",
        "reopen": "Define and review an explicit nightly channel, run it on approved infrastructure with an up-to-date branch, and record the published immutable artifact digest and location.",
    },
    {
        "id": "signing_and_attestation",
        "status": "blocked",
        "reason": "No signing key, signature, provenance attestation or release-environment approval was available or used. Only local SHA-256 observations exist.",
        "reopen": "Produce and independently verify signatures/attestations for the exact published artifacts under the release environment with recorded key provenance.",
    },
    {
        "id": "target_platform_breadth",
        "status": "blocked",
        "reason": "Only one local Darwin arm64 Release host was exercised. Linux x86-64, Windows (with compilers removed from PATH) and WebAssembly/Node were not run; S12 broader hosts remain excluded.",
        "reopen": "Run the same pinned procedure on each advertised target with recorded toolchain, archive digests and installed-consumer results, without widening support by implication.",
    },
    {
        "id": "release_claim",
        "status": "blocked",
        "reason": "Local build/install/probe observations are not a release qualification. No sealed candidate was created or adopted and no hosted CI, rights, parity or workload approval exists.",
        "reopen": "Complete hosted CI, rights/license decisions, clean install evidence on advertised targets, limitations and release notes under the RELEASING.md procedure, with independent review.",
    },
    {
        "id": "measured_workload_support",
        "status": "blocked",
        "reason": "Only deterministic synthetic frames were processed. No paced workload, deadline, CPU, memory, device timing or availability under load was measured.",
        "reopen": "Measure the exact installed build on the intended host under pacing, competing load and explicit deadline/CPU/memory budgets.",
    },
    {
        "id": "sealed_archive_reproducibility",
        "status": "blocked",
        "reason": "No new sealed candidate was produced; the wheel archive was demonstrably not byte-reproducible across two builds and historical digests differ. Cross-host archive reproducibility is unproven.",
        "reopen": "Seal two clean-build candidates with normalized metadata and verify byte-identical archives and installed bytes on pinned toolchains.",
    },
)

EVIDENCE_CLASSES: dict[str, str] = {
    "local_compile_build": "Observed on one pinned Darwin arm64 host with already-installed tooling.",
    "synthetic_runtime": "Deterministic seeded 160-sample frames through the installed wheel and native library; no real audio.",
    "measured_workload": "none",
    "real_audio_or_listening": "none",
    "source_reported": "Historical s06/s07/s08/matrix values are pinned context only; not rerun or pooled.",
    "release_or_publication": "none",
}

# Honest, verbatim limitations/regressions. Nothing here is hidden or averaged.
REGRESSIONS: tuple[dict[str, str], ...] = (
    {
        "id": "wheel_archive_not_byte_reproducible",
        "observed": "three builds from the same pinned checkout produced three different SHA-256 values: fc7012d6bdc441e9c19c932833bff5bc607ee6fb9351493f1f52713cfc8a91d5, c8a6fbe39ee545f3f7bdfb93e20329e90225b89e932b64590cd450917d2d58b7, and 0716f91e12dd417b0fe8ccd7c9973f12a4d85afea08a459a20c9d3927d56a9b6 (the third from tooling.py --run)",
        "interpretation": "Wheel archive bytes embed build-time metadata; no byte-reproducible package claim is made.",
    },
    {
        "id": "historical_wheel_digest_differs",
        "observed": "s08.md records ea4ce935f2ea2938f3b8a5fa243e0952038f0a8bc6f9fc56c0602dd705fda290 for a wheel built with a different toolchain/environment.",
        "interpretation": "Historical value is pinned context only; it is not pooled with the current observation.",
    },
    {
        "id": "historical_counts_changed",
        "observed": "acceptance-matrix.md/s06.md/s08.md record 10/10 CTest and 4/4 installed Python tests; this checkout observed 11/11 CTest and 5/5 installed Python tests.",
        "interpretation": "Verbatim local count change on this base; not an advertised support change or a release result.",
    },
    {
        "id": "historical_build_ids_differ",
        "observed": "s07 records 307f828c... (then-current) and fe66742b... (Candidate 07); this build reports 0bc71dca....",
        "interpretation": "Different build inputs are reported verbatim; identity difference alone does not prove reproducibility.",
    },
    {
        "id": "no_advertised_target_breadth",
        "observed": "Only Darwin arm64 was exercised; Linux x86-64, Windows, WebAssembly/Node and hosted CI were not run.",
        "interpretation": "No new target support is claimed; existing 'local macOS only' scope is preserved.",
    },
)


class LCG:
    """Version-stable 32-bit LCG; independent of Python random internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(v))
                                   for v in values)).hexdigest()


def synthetic_frames(seed: int = SEED_SYNTHETIC,
                     count: int = SYNTHETIC_FRAMES) -> tuple[tuple[float, ...], ...]:
    """Frozen call-owned frames: zeros, impulse, step, zeros, then seeded noise."""
    rng = LCG(seed)
    frames: list[tuple[float, ...]] = []
    for index in range(count):
        if index == 0:
            frame = [0.0] * FRAME_SAMPLES
        elif index == 1:
            frame = [0.0] * FRAME_SAMPLES
            frame[0] = 0.5
        elif index == 2:
            frame = [0.25] * FRAME_SAMPLES
        elif index == 3:
            frame = [0.0] * FRAME_SAMPLES
        else:
            frame = [0.05 * rng.uniform() for _ in range(FRAME_SAMPLES)]
        frames.append(tuple(frame))
    return tuple(frames)


def flatten(frames: Iterable[Sequence[float]]) -> tuple[float, ...]:
    return tuple(value for frame in frames for value in frame)


class BoundaryError(ValueError):
    """Malformed v0 call accepted by the reference boundary model."""


class MissingOptionalError(RuntimeError):
    """An optional selection that is absent or disabled was requested."""


@dataclass(frozen=True)
class FrameCall:
    first_input_sample: int
    samples: tuple[float, ...]
    valid_count: int = FRAME_SAMPLES
    final: bool = False
    epoch: int = 1


class ReferenceSession:
    """Pure Python model of the installed v0 facade at the 160-sample boundary.

    Only *metadata* is modelled (counts, flags, source mapping, state and
    rejection categories). Native provider DSP is never simulated or replaced.
    """

    def __init__(self, provider: str) -> None:
        if provider not in PROVIDER_BOUNDARY:
            raise MissingOptionalError("unknown provider: " + provider)
        self.provider = provider
        self.boundary = PROVIDER_BOUNDARY[provider]
        self.closed = False
        self.epoch = 1
        self.next_input = -self.boundary["declared_delay_samples"]
        self.accepted_frames = 0
        self.valid_samples = 0
        self.produced = 0
        self.startup_outputs = 0
        self.drain_calls = 0

    @staticmethod
    def _validate(frame: Any) -> None:
        if not isinstance(frame, FrameCall):
            raise BoundaryError("missing_or_wrong_shape")
        if len(frame.samples) != FRAME_SAMPLES:
            raise BoundaryError("short_frame")
        if isinstance(frame.valid_count, bool) or not isinstance(frame.valid_count, int):
            raise BoundaryError("nonnumeric_valid_count")
        if not 0 <= frame.valid_count <= FRAME_SAMPLES:
            raise BoundaryError("invalid_valid_count")
        if frame.epoch < 1 or isinstance(frame.epoch, bool):
            raise BoundaryError("negative_epoch")
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(float(v)) for v in frame.samples):
            raise BoundaryError("nonfinite")

    def process(self, frame: FrameCall) -> dict[str, Any]:
        if self.closed:
            raise BoundaryError("closed_session")
        before = tuple(frame.samples)
        self._validate(frame)
        if tuple(frame.samples) != before:
            raise AssertionError("caller-owned input mutated")
        if frame.first_input_sample != self.next_input:
            raise BoundaryError("source_mapping")
        flags = 0
        valid = frame.valid_count
        if self.startup_outputs < self.boundary["startup_padding_outputs"]:
            flags = FLAG_STARTUP_PADDING
            valid = 0
            self.startup_outputs += 1
        source_first = frame.first_input_sample
        self.next_input = frame.first_input_sample + FRAME_SAMPLES
        self.accepted_frames += 1
        self.valid_samples += valid
        self.produced += 1
        return {
            "produced_count": FRAME_SAMPLES,
            "valid_count": valid,
            "flags": flags,
            "source_first_sample": source_first,
            "epoch": self.epoch,
            "input_digest_f32": tensor_digest(before),
            "all_finite": True,
            "caller_inputs_unchanged": True,
        }

    def reset(self, epoch: int) -> dict[str, Any]:
        """Model the reset control; non-increasing/non-positive epochs reject."""
        if self.closed:
            raise BoundaryError("closed_session")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch <= self.epoch:
            raise BoundaryError("negative_epoch")
        self.epoch = epoch
        self.next_input = -self.boundary["declared_delay_samples"]
        self.accepted_frames = 0
        self.valid_samples = 0
        self.produced = 0
        self.startup_outputs = 0
        self.drain_calls = 0
        return {"status": "ok", "epoch": epoch}

    def drain(self) -> list[dict[str, Any]]:
        if self.closed:
            raise BoundaryError("closed_session")
        out: list[dict[str, Any]] = []
        while self.drain_calls < self.boundary["drain_frames"]:
            self.drain_calls += 1
            out.append({"produced_count": FRAME_SAMPLES, "valid_count": 0,
                        "flags": 0, "epoch": self.epoch, "drain": True})
        return out

    def close(self) -> None:
        self.closed = True


def reference_probe() -> dict[str, Any]:
    """Run the synthetic frames through the reference boundary and controls."""
    frames = synthetic_frames()
    flat = flatten(frames)
    providers: dict[str, Any] = {}
    for name, boundary in PROVIDER_BOUNDARY.items():
        session = ReferenceSession(name)
        flags: list[int] = []
        source_first: list[int] = []
        epochs: list[int] = []
        produced = 0
        valid = 0
        finite = True
        unchanged = True
        try:
            for index, frame in enumerate(frames):
                call = FrameCall(
                    first_input_sample=index * FRAME_SAMPLES
                    - boundary["declared_delay_samples"],
                    samples=frame)
                result = session.process(call)
                produced += result["produced_count"]
                valid += result["valid_count"]
                flags.append(result["flags"])
                source_first.append(result["source_first_sample"])
                epochs.append(result["epoch"])
                finite = finite and result["all_finite"]
                unchanged = unchanged and result["caller_inputs_unchanged"]
            drain = session.drain()
        finally:
            session.close()
        providers[name] = {
            "declared_delay_samples": boundary["declared_delay_samples"],
            "produced_samples": produced,
            "valid_samples": valid,
            "drain_frames": len(drain),
            "flags": flags,
            "source_first_samples": source_first,
            "epochs": epochs,
            "all_finite": finite,
            "caller_inputs_unchanged": unchanged,
            # Identity reference only. Native provider output digests are
            # observed constants and are never produced by this model.
            "model_identity_output_digest_f32": tensor_digest(flat),
        }

    # Malformed inputs: reject without changing the accepted-frame counter.
    malformed: dict[str, Any] = {}
    for label, bad in (
        ("short_frame", FrameCall(0, (0.0,) * (FRAME_SAMPLES - 1))),
        ("nonnumeric_valid_count", FrameCall(0, (0.0,) * FRAME_SAMPLES,
                                              valid_count=1.5)),  # type: ignore[arg-type]
        ("negative_epoch", FrameCall(0, (0.0,) * FRAME_SAMPLES, epoch=-1)),
    ):
        session = ReferenceSession("dsp.highpass80.v0")
        before = session.accepted_frames
        try:
            if label == "negative_epoch":
                session.reset(bad.epoch)  # reset control, not process
            else:
                session.process(bad)
            status = "no_error"
        except BoundaryError:
            status = "ValueError"
        finally:
            session.close()
        malformed[label] = {"status": status,
                            "state_intact": session.accepted_frames == before}

    # Missing optional selections: no provider registration or fallback.
    missing: dict[str, Any] = {}
    for label, provider in (
        ("unknown_provider_id", "dsp.nonexistent-optional.v0"),
        ("unset_library_env", "unset:AUDIO_SDK_LIBRARY"),
        ("wrong_library_path", "missing:/does/not/exist.dylib"),
    ):
        try:
            ReferenceSession(provider)
            status = "no_error"
        except MissingOptionalError:
            status = "RuntimeError"
        except OSError:
            status = "OSError"
        missing[label] = {"status": status}

    return {
        "input": {
            "frames": len(frames),
            "samples": len(flat),
            "digest_f32": tensor_digest(flat),
        },
        "providers": providers,
        "malformed": malformed,
        "missing_optional": missing,
    }


def crosscheck(reference: dict[str, Any]) -> dict[str, Any]:
    """Compare model metadata with frozen native observations, verbatim."""
    observed = OBSERVED["synthetic_runtime_probe"]
    checks: dict[str, bool] = {
        "input_digest": reference["input"]["digest_f32"]
        == observed["input_digest_f32"],
        "input_frames": reference["input"]["frames"] == observed["frames"],
        "input_samples": reference["input"]["samples"] == observed["samples"],
    }
    per_provider: dict[str, Any] = {}
    for name, model in reference["providers"].items():
        native = observed["providers"][name]
        fields = ("declared_delay_samples", "produced_samples", "valid_samples",
                  "drain_frames", "flags", "source_first_samples", "epochs",
                  "all_finite", "caller_inputs_unchanged")
        matches = {field: model[field] == native[field] for field in fields}
        per_provider[name] = {
            "field_matches": matches,
            "all_metadata_matches": all(matches.values()),
            "native_output_digest_f32": native["output_digest_f32"],
            "model_identity_output_digest_f32": model[
                "model_identity_output_digest_f32"],
            "native_dsp_not_modelled": True,
        }
        checks["provider_" + name] = per_provider[name]["all_metadata_matches"]
    for label in observed["malformed"]:
        checks["malformed_" + label] = (
            reference["malformed"][label] == observed["malformed"][label])
    for label in observed["missing_optional"]:
        # The Python model signals every absent selection as RuntimeError;
        # the native binding distinguishes missing path with OSError. Both are
        # explicit rejections with no fallback.
        checks["missing_optional_" + label] = reference["missing_optional"][
            label]["status"] == "RuntimeError"
    return {
        "checks": checks,
        "all_pass": all(checks.values()),
        "per_provider": per_provider,
        "note": "Only boundary metadata is cross-checked; native DSP output digests are recorded observations, not model outputs.",
    }


def task_artifact_pins() -> list[dict[str, str]]:
    """Digests of the code artifacts only.

    ``README.md`` cites this report's digest and ``SOURCES.sha256`` pins the
    report and README, so neither is embedded here: that would be circular.
    """
    here = __import__("pathlib").Path(__file__).resolve().parent
    names = ("fixture.py", "tooling.py", "run.py", "test_fixture.py",
             "verify.py")
    return [
        {"path": name,
         "sha256": hashlib.sha256((here / name).read_bytes()).hexdigest(),
         "kind": "task_artifact"}
        for name in names
    ]


MATRIX: tuple[dict[str, str], ...] = (
    {
        "id": "M01-clean-checkout",
        "extends": "S03/S-T01/S06",
        "support_class": "compile_build",
        "status": "observed_local",
        "command": "git rev-parse HEAD && git status --porcelain  (build dir outside worktree)",
        "observed_digest": BASE_COMMIT,
        "advertised_support_delta": "none",
    },
    {
        "id": "M02-native-configure-build",
        "extends": "S-T01",
        "support_class": "compile_build",
        "status": "observed_local",
        "command": "cmake -S <WT> -B <WORK>/build -DCMAKE_BUILD_TYPE=Release && cmake --build <WORK>/build --parallel 2",
        "observed_digest": OBSERVED["compile_build"]["build_id"],
        "advertised_support_delta": "none",
    },
    {
        "id": "M03-ctest",
        "extends": "S06/S-T01",
        "support_class": "synthetic_runtime",
        "status": "observed_local",
        "command": "ctest --test-dir <WORK>/build --output-on-failure",
        "observed_digest": "11/11 pass, 0 fail, 0 skip",
        "advertised_support_delta": "none",
    },
    {
        "id": "M04-installed-c-cpp-consumer",
        "extends": "S03/S06/S-T09",
        "support_class": "compile_build",
        "status": "observed_local",
        "command": "cc -std=c11 -Wall -Wextra -Werror ... && c++ -std=c++20 -Wall -Wextra -Werror ... && run both",
        "observed_digest": OBSERVED["native_install"]["dylib_sha256"],
        "advertised_support_delta": "none",
    },
    {
        "id": "M05-installed-conformance",
        "extends": "S05/S06/S-T08",
        "support_class": "synthetic_runtime",
        "status": "observed_local",
        "command": "<PREFIX>/bin/audio_sdk_conformance --provider <id> --report <WORK>/reports/<id>-report.json",
        "observed_digest": OBSERVED["installed_conformance"]["speex.ns.v0"]["report_sha256"],
        "advertised_support_delta": "none",
    },
    {
        "id": "M06-python-wheel-install",
        "extends": "S08/S-T10",
        "support_class": "compile_build",
        "status": "observed_local",
        "command": "PY312 -m pip wheel --no-deps --no-build-isolation --wheel-dir <WORK>/wheels <WT>/bindings/python && PY312 -m venv <WORK>/venv312 && pip install --no-index --no-deps <wheel>",
        "observed_digest": OBSERVED["python_wheel"]["wheel_sha256"],
        "advertised_support_delta": "none",
    },
    {
        "id": "M07-installed-python-tests",
        "extends": "S08/S-T10",
        "support_class": "synthetic_runtime",
        "status": "observed_local",
        "command": "AUDIO_SDK_LIBRARY=<dylib> PYTHONDONTWRITEBYTECODE=1 <venv>/bin/python -m unittest discover -s <WORK>/acceptance/tests -v",
        "observed_digest": "5/5 pass, 0 fail, 0 skip",
        "advertised_support_delta": "none",
    },
    {
        "id": "M08-synthetic-runtime-probe",
        "extends": "S08/S-T10",
        "support_class": "synthetic_runtime",
        "status": "observed_local",
        "command": "AUDIO_SDK_LIBRARY=<dylib> <venv>/bin/python <WORK>/probe.py  (seed 31337, 8 frames)",
        "observed_digest": OBSERVED["synthetic_runtime_probe"]["probe_output_sha256"],
        "advertised_support_delta": "none",
    },
    {
        "id": "M09-malformed-and-missing-optional",
        "extends": "S-T05/S-T10",
        "support_class": "synthetic_runtime",
        "status": "observed_local",
        "command": "short/shape/nonnumeric/negative calls and unknown provider / missing AUDIO_SDK_LIBRARY through the installed wheel",
        "observed_digest": "all rejected: ValueError/RuntimeError/OSError, state intact",
        "advertised_support_delta": "none",
    },
    {
        "id": "M10-measured-workload",
        "extends": "S02/S-T02 (not extended)",
        "support_class": "measured_workload",
        "status": "blocked",
        "command": "none run: no paced/deadline/CPU/memory/device measurement",
        "observed_digest": "none",
        "advertised_support_delta": "none",
    },
    {
        "id": "M11-nightly-publication",
        "extends": "S07/S-T12 (not extended)",
        "support_class": "compile_build",
        "status": "blocked",
        "command": "scripts/package.sh not run; no upload/publish command executed",
        "observed_digest": "none",
        "advertised_support_delta": "none",
    },
    {
        "id": "M12-signing-attestation",
        "extends": "RELEASING.md",
        "support_class": "compile_build",
        "status": "blocked",
        "command": "none: no signing key, attestation or release-environment approval",
        "observed_digest": "none",
        "advertised_support_delta": "none",
    },
    {
        "id": "M13-target-platform-breadth",
        "extends": "acceptance-matrix.md S12",
        "support_class": "compile_build",
        "status": "blocked",
        "command": "none: Darwin arm64 only; Linux/Windows/WASM not run",
        "observed_digest": "none",
        "advertised_support_delta": "none",
    },
    {
        "id": "M14-release-claim",
        "extends": "RELEASING.md",
        "support_class": "measured_workload",
        "status": "blocked",
        "command": "none: local probe only, no release approval or hosted CI",
        "observed_digest": "none",
        "advertised_support_delta": "none",
    },
)


def qualification_state(report: dict[str, Any]) -> str:
    """No missing or blocked result can qualify the candidate."""
    if not report.get("no_missing_result_qualifies_candidate"):
        raise ValueError("missing-result gate disabled")
    if any(block["status"] == "blocked" for block in report["blockers"]):
        return "not_qualified"
    if not report.get("crosscheck", {}).get("all_pass", False):
        return "not_qualified"
    if any(row["status"] == "blocked" for row in report["matrix"]):
        return "not_qualified"
    return "proposal_only_synthetic_incomplete"


def impurity_free(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite report value")
    if isinstance(value, dict):
        return {key: impurity_free(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [impurity_free(item) for item in value]
    return value


def build_report() -> dict[str, Any]:
    reference = reference_probe()
    checked = crosscheck(reference)
    spec = {
        "contract": CONTRACT_ID,
        "schema": SCHEMA_ID,
        "base_commit": BASE_COMMIT,
        "pinned_python": PINNED_PYTHON,
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT, "frame_samples": FRAME_SAMPLES,
        },
        "seed": SEED_SYNTHETIC,
        "frames": SYNTHETIC_FRAMES,
        "source_pins": {pin["path"]: pin["sha256"] for pin in SOURCE_PINS},
        "tool_pins": dict(TOOL_PINS),
        "provider_boundary": PROVIDER_BOUNDARY,
        "blockers": [dict(block) for block in BLOCKERS],
        "observed": OBSERVED,
    }
    report: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "contract": CONTRACT_ID,
        "scope": "task-local synthetic Tool profile evidence; not a release, nightly, signing, target-breadth or workload qualification",
        "profile": "Tool",
        "candidate_status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "base_commit": BASE_COMMIT,
        "spec_digest": object_digest(spec),
        "sources_manifest": "SOURCES.sha256",
        "pinned_python": PINNED_PYTHON,
        "tool_pins": dict(TOOL_PINS),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "advertised_runtime_change": False,
        },
        "boundary": {
            "provider_id_scope": "developer-facing installer/tooling entry point only",
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "note": "No C provider, no registry change, no public flag and no installed v0 behavior change.",
        },
        "profile_coverage": {
            "version_install_provenance": OBSERVED["compile_build"]["build_id"],
            "clean_checkout_or_package": "clean pinned checkout; sealed candidate not created",
            "one_typical_use": "M08 synthetic runtime probe through installed wheel + native library",
            "caller_owned_inputs": True,
            "malformed_inputs": OBSERVED["synthetic_runtime_probe"]["malformed"],
            "missing_optional_selections": OBSERVED["synthetic_runtime_probe"][
                "missing_optional"],
        },
        "support_separation": {
            "compile_build": {
                "status": "observed_local",
                "rows": [row["id"] for row in MATRIX
                         if row["support_class"] == "compile_build"
                         and row["status"] == "observed_local"],
            },
            "synthetic_runtime": {
                "status": "observed_local",
                "rows": [row["id"] for row in MATRIX
                         if row["support_class"] == "synthetic_runtime"
                         and row["status"] == "observed_local"],
                "qualifying": False,
            },
            "measured_workload": {
                "status": "blocked",
                "rows": [row["id"] for row in MATRIX
                         if row["support_class"] == "measured_workload"],
                "qualifying": False,
            },
        },
        "source_pins": list(SOURCE_PINS),
        "task_artifact_pins": task_artifact_pins(),
        "observed": OBSERVED,
        "reference_probe": reference,
        "crosscheck": checked,
        "matrix": [dict(row) for row in MATRIX],
        "regressions": [dict(item) for item in REGRESSIONS],
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "blockers": [dict(block) for block in BLOCKERS],
        "controls_all_pass": checked["all_pass"]
        and all(value["status"] == "ValueError"
                and value["state_intact"]
                for value in reference["malformed"].values()),
        "all_outputs_finite": all(
            provider["all_finite"]
            for provider in OBSERVED["synthetic_runtime_probe"][
                "providers"].values()),
        "caller_inputs_unchanged": all(
            provider["caller_inputs_unchanged"]
            for provider in OBSERVED["synthetic_runtime_probe"][
                "providers"].values()),
        "no_missing_result_qualifies_candidate": True,
    }
    report["qualification_status"] = qualification_state(report)
    return impurity_free(report)


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False).encode("utf-8") + b"\n"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: fixture.py <report.json>")
    path = __import__("pathlib").Path(sys.argv[1])
    report = build_report()
    path.write_bytes(canonical_report_bytes(report))
    print(f"report_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    print(f"spec_digest={report['spec_digest']}")
    print(f"qualification_status={report['qualification_status']} "
          f"crosscheck={report['crosscheck']['all_pass']} "
          f"regressions={len(report['regressions'])} "
          f"blockers={len(report['blockers'])}")


if __name__ == "__main__":
    main()
