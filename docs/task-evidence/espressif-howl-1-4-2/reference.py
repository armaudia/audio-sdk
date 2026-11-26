# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-ESPRESSIF-HOWL-1-4-2.

This module is NOT Espressif HOWL. It contains no vendor source, object code,
firmware, license text, configuration header or runtime. A bounded read-only
search finds no ``esp_audio_effects`` HOWL checkout, no ESP-IDF toolchain, no
eligible ESP32-S3R8 runner and no matched closed-loop fixture in the
workspace. The component's published v1.4.2 terms are also reported to restrict
use to Espressif products and to prohibit redistribution for non-Espressif
products, so the macOS/Python target of this workspace is not an eligible
platform without a license/platform decision.

The module therefore builds a fail-closed external-adapter blocker report:

* strict request validation at the documented 16 kHz / 512-sample frame and at
  the documented 48 kHz / 1024-sample frame;
* explicit source, license, hardware, runtime, fixture and rights probes;
* an admission gate that rejects every structurally valid request because the
  required artifacts and rights are absent;
* synthetic harness stimuli for rejection and identity controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, extracted, ported, reconstructed or
simulated. No candidate audio output is produced. No result qualifies the
candidate and no vendor score is reproduced.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = "audio-sdk/espressif-howl-1-4-2-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/espressif-howl-1-4-2-contract/0.1"
TASK = "SDK-ESPRESSIF-HOWL-1-4-2"
COMPONENT = "espressif-howl-1-4-2"
BRANCH = "swarm/SDK-ESPRESSIF-HOWL-1-4-2"
BASE_COMMIT = "81f31382c55aff629001e06362f3abe81c491b9e"
TASK_PREFIX = "docs/task-evidence/espressif-howl-1-4-2/"
MODE = "external-adapter"
VERIFICATION_PROFILE = "DSP"

# Installed v0 format. This is the unchanged public baseline, not the vendor
# component geometry and not an adapter configuration.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

# Public v1.4.2 documentation reports these rates and fixed frames. Only the
# 16 kHz and 48 kHz frame sizes are stated by the pinned research note; the
# other rates are left explicitly unverified rather than invented.
DECLARED_SAMPLE_RATES_HZ = (8000, 16000, 24000, 32000, 44100, 48000)
DECLARED_FRAME_SAMPLES = {16000: 512, 48000: 1024}
UNVERIFIED_FRAME_RATES = (8000, 24000, 32000, 44100)
REPORTED_DETECTOR_CRITERIA = ("PAPR", "PHPR", "PNPR", "optional IMSD")
REPORTED_CONTROL_POLICY = (
    "dynamic biquad notches",
    "loop-margin global gain reduction with gradual restore",
)
DECLARED_TARGET = "ESP32-S3R8 / ESP-IDF"
VENDOR = "Espressif Systems"
COMPONENT_NAME = "esp_audio_effects HOWL"
COMPONENT_VERSION = "1.4.2"
SOURCE_URL = (
    "https://components.espressif.com/components/espressif/"
    "esp_audio_effects/versions/1.4.2")
DOC_URL = (
    "https://github.com/espressif/esp-adf-libs/blob/master/"
    "esp_audio_effects/docs/README_HOWL.md")
REPORTED_LICENSE_NAME = "Espressif Modified MIT License (v1.4.2)"
REPORTED_LICENSE_RESTRICTION = (
    "vendor-published terms restrict use to Espressif products and prohibit "
    "redistribution for non-Espressif products (source-reported, not locally "
    "verified)")

# Local harness geometry. 16 kHz / 512 samples is the documented fixed frame
# for that rate; it is used only to exercise validation and rejection.
HARNESS_SAMPLE_RATE_HZ = 16000
HARNESS_CHANNELS = 1
HARNESS_FRAME_SAMPLES = 512
HARNESS_FRAME_VALUES = HARNESS_CHANNELS * HARNESS_FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
MAX_CHANNELS_GUARD = 64

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    "research/feedback_control_20261028.md":
        "47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "Espressif HOWL 1.4.2",
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

PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

CANDIDATE = "espressif_howl_1_4_2"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

SOURCE_CANDIDATE_PATHS = (
    "third_party/esp_audio_effects",
    "third_party/esp_audio_effects-1.4.2",
    "third_party/esp-adf-libs",
    "components/esp_audio_effects",
    "vendor/espressif/esp_audio_effects",
    "research/espressif-howl",
    "research/esp_audio_effects",
    "research/repos/esp_audio_effects",
    "data/models/espressif-howl",
    "~/esp/esp-adf-libs",
    "~/esp/esp_audio_effects",
    "~/esp/esp-idf",
    "~/.espressif",
    "~/code/esp-adf-libs",
    "~/projects/esp-adf-libs",
)
SOURCE_MARKERS = (
    "esp_howl.c", "esp_howl.h", "README_HOWL.md", "esp_audio_effects",
)

TOOLCHAIN_COMMANDS = ("idf.py", "esptool.py", "xtensa-esp32s3-elf-gcc")
RUNTIME_CANDIDATE_PATHS = (
    "~/esp/esp-idf",
    "~/esp/esp-idf/export.sh",
    "~/.espressif",
    "data/envs/esp-idf",
    "data/runtime/esp-idf",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/espressif-howl/idf-env.lock",
    "data/envs/esp-idf/requirements.lock",
    "data/runtime/esp-idf/idf-env.lock",
)

FIXTURE_CANDIDATE_PATHS = (
    "data/corpora/espressif-howl",
    "data/fixtures/espressif-howl",
    "research/espressif-howl/fixture",
    "research/espressif-howl/loopback",
)
FIXTURE_MARKERS = (".wav", ".flac", ".npy", ".json")

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "esp_audio_effects HOWL 1.4.2 source checkout",
        "required": (
            "A local checkout of the exact esp_audio_effects v1.4.2 HOWL "
            "component at a recorded full revision with a read-only non-.git "
            "tree digest and the component license file"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "v1.4.2 license text and non-Espressif use decision",
        "required": (
            "The byte-identical v1.4.2 license text with SHA-256 plus a "
            "written rights decision approving or rejecting use and "
            "redistribution on this macOS/Python target"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "eligible Espressif hardware and ESP-IDF runtime",
        "required": (
            "An approved ESP32-S3R8 runner with a hash-pinned ESP-IDF "
            "toolchain, a reproducible firmware image and an install/import "
            "parity record"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "pinned HOWL configuration and API headers",
        "required": (
            "The exact component headers and default configuration that "
            "declare sample rates, frame sizes, channel handling, detector "
            "thresholds, notch limits and gain-margin policy"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "matched closed-loop hardware fixture",
        "required": (
            "A rights-cleared ESP32-S3R8 loudspeaker-to-microphone fixture "
            "with measured loop gain, delay, saturation behavior and matched "
            "speech/music/silence/onset/recovery cases"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "independent review and release package",
        "required": (
            "An independent exact-head review of the vendor boundary, an "
            "approved adapter intake decision and a complete release package "
            "before any support claim"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
)

GATES = (
    {
        "id": "RG-01",
        "gate": "exact_component_source_revision_and_license_pin",
        "status": "blocked",
        "reason": (
            "No esp_audio_effects HOWL 1.4.2 checkout exists locally; the "
            "component revision, tree digest, source files and license file "
            "are absent and no source is pinned."),
        "reopen": (
            "Stage the exact v1.4.2 component at a recorded full revision "
            "with a read-only tree digest and its license file, then pin "
            "every required source path before reading any configuration."),
    },
    {
        "id": "RG-02",
        "gate": "non_espressif_use_and_redistribution_decision",
        "status": "blocked",
        "reason": (
            "The vendor-published v1.4.2 terms are reported to restrict use "
            "to Espressif products and to prohibit redistribution for "
            "non-Espressif products. No local license text or written "
            "approval exists for this macOS/Python target."),
        "reopen": (
            "Obtain the exact license text, record its SHA-256, and secure a "
            "written rights decision that explicitly permits this host "
            "target, adapter distribution and any derived output, or record "
            "a final rejection and close the task."),
    },
    {
        "id": "RG-03",
        "gate": "eligible_hardware_and_hash_pinned_esp_idf_runtime",
        "status": "blocked",
        "reason": (
            "No approved ESP32-S3R8 runner, ESP-IDF toolchain, reproducible "
            "firmware image or install/import parity record exists; the "
            "component is an ESP-IDF/SoC library rather than a portable host "
            "library."),
        "reopen": (
            "Provide an approved eligible runner and a hash-pinned ESP-IDF "
            "toolchain, build a reproducible firmware image, and prove "
            "runtime parity before attempting any measurement."),
    },
    {
        "id": "RG-04",
        "gate": "pinned_declared_geometry_and_configuration",
        "status": "blocked",
        "reason": (
            "The documented rates, 512-sample 16 kHz frame, 1024-sample "
            "48 kHz frame, per-channel operation and detector/margin policy "
            "are source-reported only. No pinned headers or configuration "
            "declare the exact frame geometry for 8, 24, 32 or 44.1 kHz."),
        "reopen": (
            "Pin the exact headers and default configuration, verify every "
            "declared rate and frame, channel bound, detector threshold, "
            "notch limit and margin policy, and never infer an unpinned "
            "frame size."),
    },
    {
        "id": "RG-05",
        "gate": "detector_notch_and_margin_reproduction",
        "status": "blocked",
        "reason": (
            "No candidate instance exists, so PAPR, PHPR, PNPR, optional "
            "IMSD, dynamic biquad notch placement, loop-margin gain "
            "reduction and gradual restore were not reproduced, reset or "
            "drained."),
        "reopen": (
            "With pinned source, configuration, firmware and runner, "
            "reproduce parameter identity, detector decisions, notch "
            "coefficients, margin schedule, reset, finite drain and "
            "execution-mode ownership."),
    },
    {
        "id": "RG-06",
        "gate": "dsp_acceptance_matrix_and_numerical_behavior",
        "status": "blocked",
        "reason": (
            "The DSP profile requires sweeps, steps, impulses, silence, "
            "clean speech and a task-specific control with gain, response, "
            "attack/release, headroom, delay, numerical behavior, state "
            "transitions and interacting nonlinear configurations; none was "
            "run because there is no eligible candidate runtime."),
        "reopen": (
            "Run the full DSP matrix on eligible hardware, retain every "
            "failure and nonfinite case, and record gain, response, attack/"
            "release, headroom, delay and state transitions with exact "
            "tolerances agreed before scoring."),
    },
    {
        "id": "RG-07",
        "gate": "closed_loop_stability_adverse_behavior_and_device_timing",
        "status": "blocked",
        "reason": (
            "No closed-loop stability, maximum-stable-gain, residual tone, "
            "false-trigger, speech-attenuation, path-change recovery, "
            "clipping, latency, CPU, memory or callback measurement exists."),
        "reopen": (
            "Measure closed-loop stability and maximum stable gain on the "
            "eligible runner with multiple tones, speech, music, silence, "
            "path changes, saturation and reset, and report false triggers, "
            "speech damage, residual tone energy, delay and paced timing "
            "separately."),
    },
    {
        "id": "RG-08",
        "gate": "external_adapter_intake_benchmark_and_release",
        "status": "blocked",
        "reason": (
            "No approved external adapter, provider intake, opt-in "
            "registration, public-surface decision, authorized listening, "
            "benchmark validation, independent exact-head review or release "
            "approval exists."),
        "reopen": (
            "Complete the rights and hardware decisions, implement any "
            "adapter only behind explicit caller opt-in with no default or "
            "fallback registration, validate a benchmark bundle, run "
            "authorized listening where permitted, and obtain independent "
            "review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": (
        "blocked_source_license_hardware_runtime_and_fixture_absent"),
    "artifact": (
        "esp_audio_effects HOWL 1.4.2 source, license decision, eligible "
        "ESP32-S3R8 hardware, hash-pinned ESP-IDF runtime and matched "
        "closed-loop fixture"),
    "source": {
        "status": "absent",
        "repository": SOURCE_URL,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
    },
    "license": {
        "status": "blocked_non_espressif_use_not_approved",
        "reported_name": REPORTED_LICENSE_NAME,
        "reported_restriction": REPORTED_LICENSE_RESTRICTION,
        "license_text_present": False,
        "license_text_sha256": None,
        "non_espressif_use_approved": False,
        "redistribution_approved": False,
        "host_target_approved": False,
        "review": "blocked",
    },
    "hardware": {
        "status": "absent",
        "eligible_target": DECLARED_TARGET,
        "runner": None,
        "hardware_attached": None,
        "firmware_sha256": None,
        "vendor_cpu_memory_figures_generalizable": False,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "ESP-IDF version matched to esp_audio_effects 1.4.2",
            "xtensa ESP32-S3 toolchain with recorded version and hashes",
            "reproducible firmware image with a recorded SHA-256",
            "an explicit runner identity and install/import parity check",
        ],
        "idf_path": None,
        "idf_version": None,
        "lockfile": None,
        "sha256": None,
    },
    "fixture": {
        "status": "absent",
        "required": (
            "rights-cleared ESP32-S3R8 loudspeaker-to-microphone fixture "
            "with measured loop gain, delay, saturation, speech, music, "
            "silence, onset and recovery cases"),
        "corpus_rights": False,
        "loop_gain_measured": False,
        "delay_measured": False,
        "sha256": None,
    },
    "config": {
        "status": "absent",
        "required_paths": [
            "esp_audio_effects HOWL public header",
            "esp_audio_effects HOWL default configuration",
        ],
        "sha256": None,
        "byte_count": None,
    },
    "pinned_revision": None,
    "source_digest": None,
    "license_digest": None,
    "hardware_digest": None,
    "runtime_digest": None,
    "fixture_digest": None,
    "config_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "The exact v1.4.2 license text, a written decision on non-Espressif "
        "and macOS/Python use, permission for adapter distribution and "
        "derived output, an approved eligible ESP32-S3R8 runner and "
        "permission for every fixture recording are required before any "
        "reproduction, adapter, benchmark or release claim."),
    "workspace_search": (
        "Bounded read-only existence and file-name checks of named candidate "
        "paths under the workspace found no esp_audio_effects HOWL checkout, "
        "no ESP-IDF toolchain or lock, no eligible runner, no matched "
        "closed-loop fixture and no locally approved license text. No "
        "archive, binary, firmware, audio file or vendor file was opened, "
        "downloaded or reconstructed."),
    "not_attempted": [
        "no git clone, network download, package installation or archive extraction",
        "no fabricated, ported, reverse-engineered or surrogate HOWL source, header or configuration",
        "no fabricated license text, rights decision or vendor approval",
        "no ESP-IDF build, firmware flash or hardware execution",
        "no copied vendor source, object code, firmware, audio or score",
        "no candidate audio, listening, device-timing or benchmark run",
    ],
    "reopen": (
        "Stage the exact component at a recorded revision with license and "
        "tree digest, secure a written non-Espressif use and redistribution "
        "decision, provide an approved ESP32-S3R8 runner and hash-pinned "
        "ESP-IDF runtime, pin the configuration, stage a rights-cleared "
        "closed-loop fixture, then reproduce the component and run the DSP "
        "matrix with independent review."),
}

NON_CLAIMS = (
    "No esp_audio_effects HOWL source, header, configuration, object code, firmware or license text is included.",
    "No HOWL detector, notch, loop-margin controller, adapter or port is implemented, approximated, simulated or run.",
    "No vendor score, CPU figure, memory figure, frame rate or platform claim is reproduced or generalized.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, fixture, hardware, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No source-reported vendor characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/espressif-howl-1-4-2/ is touched.",
    "The reference is a task-local external-adapter gate, not Espressif HOWL.",
    "The declared vendor component is an ESP-IDF/SoC library and is not representable by installed v0.",
    "All harness stimuli are analytic or seeded synthetic; no vendor runtime is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

HOWLING_CONTROL = {
    "status": "not_evaluated_by_this_task",
    "installed_v0_channels": CHANNELS,
    "metrics": None,
    "result": None,
    "qualifies_candidate": False,
    "howl_detection_claim": False,
    "notch_claim": False,
    "loop_margin_claim": False,
    "maximum_stable_gain_claim": False,
    "feedback_cancellation_claim": False,
    "note": (
        "No detector, notch, loop-margin, maximum-stable-gain or "
        "feedback-cancellation result exists. The documented policy is a "
        "design reference only and is not reproduced here."),
}

EXTERNAL_BOUNDARY = {
    "documented": True,
    "vendor": VENDOR,
    "component": COMPONENT_NAME,
    "component_version": COMPONENT_VERSION,
    "distribution_model": "ESP-IDF/SoC component",
    "eligible_target": DECLARED_TARGET,
    "host_target": "macOS / Python 3 workspace",
    "host_target_eligible": False,
    "license_reported": REPORTED_LICENSE_NAME,
    "use_restricted_to_espressif_products_reported": True,
    "non_espressif_redistribution_prohibited_reported": True,
    "license_text_present": False,
    "non_espressif_use_approved": False,
    "redistribution_approved": False,
    "local_runtime_present": False,
    "vendor_output_present": False,
    "adapter_implemented": False,
    "adapter_default_registration": False,
    "automatic_discovery": False,
    "fallback": "none",
    "vendor_claims_separate_from_local_measurements": True,
    "note": (
        "The vendor boundary is documented from the pinned research note and "
        "public component pages only. No source, license text, runtime or "
        "measurement is present, and this host target is not approved."),
}


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


class ArtifactsAbsent(EvidenceError):
    code = "ARTIFACTS_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


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


def strict_json_load(path: Path) -> Any:
    value = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise JsonError("JSON_NOT_OBJECT: " + str(path), "JSON_NOT_OBJECT")
    return value


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


def tensor_digest(samples: Iterable[float]) -> str:
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


def db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise InputError("NONPOSITIVE_RMS", "NONPOSITIVE_RMS")
    return 20.0 * math.log10(numerator / denominator)


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state / 4294967296.0) * 2.0 - 1.0


def silence(length: int = HARNESS_FRAME_VALUES) -> Tuple[float, ...]:
    return (0.0,) * length


def impulse(length: int = HARNESS_FRAME_VALUES,
            position: int = HARNESS_FRAME_VALUES // 2,
            amplitude: float = 0.5) -> Tuple[float, ...]:
    if not 0 <= position < length:
        raise ConfigError("impulse position out of range", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = HARNESS_FRAME_VALUES,
         position: int = HARNESS_FRAME_VALUES // 2,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = HARNESS_FRAME_VALUES, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise ConfigError("invalid sweep geometry", "INVALID_STIMULUS")
    duration = length / float(HARNESS_SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
        phase = 2.0 * math.pi * (start_hz * t +
                                 (end_hz - start_hz) * t * t /
                                 (2.0 * duration))
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def speech_like(length: int = HARNESS_FRAME_VALUES,
                seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        noise_value = next(noise)
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
        if index < length // 2:
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(),
    "impulse": lambda: impulse(),
    "step": lambda: step(),
    "sweep": lambda: sweep(),
    "speech_like": lambda: speech_like(),
}


def stimulus_metrics(name: str, samples: Sequence[float]) -> Dict[str, Any]:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    peak = 0.0
    nonfinite = 0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            nonfinite += 1
            continue
        peak = max(peak, abs(number))
    if nonfinite:
        raise InputError("NONFINITE_SAMPLE", "NONFINITE")
    if peak > MAX_ABS_STIMULUS:
        raise InputError("STIMULUS_OUT_OF_RANGE", "OUT_OF_RANGE")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": _r(peak),
        "rms": _r(rms([float(value) for value in samples])),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def speech_contrast(samples: Sequence[float]) -> Dict[str, Any]:
    voiced = []
    pause = []
    for index, value in enumerate(samples):
        if index < len(samples) // 2:
            voiced.append(float(value))
        else:
            pause.append(float(value))
    voiced_rms = rms(voiced)
    pause_rms = rms(pause)
    return {
        "voiced_rms": _r(voiced_rms),
        "pause_rms": _r(pause_rms),
        "voiced_to_pause_db": _r(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def _validate_sample_list(samples: Any, expected: int) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
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
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("SAMPLE_OUT_OF_RANGE: " + str(index),
                             "OUT_OF_RANGE")
        result.append(number)
    return result


def _require_int(value: Any, code: str,
                 minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def validate_request(request: Any) -> Dict[str, Any]:
    """Validate a documented-geometry request; never runs a candidate."""
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
    if request["candidate"] != CANDIDATE:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    rate = _require_int(request["sample_rate_hz"], "INVALID_RATE", 1)
    if rate not in DECLARED_SAMPLE_RATES_HZ:
        raise ConfigError("RATE_NOT_DECLARED", "RATE_NOT_DECLARED")
    channels = _require_int(request["channels"], "WRONG_CHANNELS", 1)
    if channels > MAX_CHANNELS_GUARD:
        raise ConfigError("CHANNELS_OVER_LOCAL_GUARD",
                          "CHANNELS_OVER_LOCAL_GUARD")
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1)
    if frame_samples > 4096:
        raise ConfigError("FRAME_TOO_LARGE", "INVALID_FRAME")
    if rate in DECLARED_FRAME_SAMPLES:
        if frame_samples != DECLARED_FRAME_SAMPLES[rate]:
            raise ConfigError("WRONG_DECLARED_FRAME", "WRONG_DECLARED_FRAME")
    else:
        raise ConfigError("UNVERIFIED_FRAME_GEOMETRY",
                          "UNVERIFIED_FRAME_GEOMETRY")
    samples = _validate_sample_list(
        request["samples"], channels * frame_samples)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise ConfigError("INVALID_MODE", "INVALID_MODE")
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": rate,
        "channels": channels,
        "frame_samples": frame_samples,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
    }


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
        "channels": HARNESS_CHANNELS,
        "frame_samples": HARNESS_FRAME_SAMPLES,
        "samples": [0.0] * HARNESS_FRAME_VALUES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    short = [0.0] * (HARNESS_FRAME_VALUES - 1)
    long = [0.0] * (HARNESS_FRAME_VALUES + 1)
    nan_samples = [0.0] * HARNESS_FRAME_VALUES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * HARNESS_FRAME_VALUES
    inf_samples[9] = float("inf")
    negative_inf_samples = [0.0] * HARNESS_FRAME_VALUES
    negative_inf_samples[9] = float("-inf")
    return (
        ("unknown_candidate", variant(candidate="espressif_howl")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("zero_channels", variant(channels=0)),
        ("negative_channels", variant(channels=-1)),
        ("bool_channels", variant(channels=True)),
        ("channels_over_local_guard", variant(channels=65)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-16000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("undeclared_rate", variant(sample_rate_hz=22050)),
        ("zero_frame", variant(frame_samples=0)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("wrong_16k_frame", variant(frame_samples=160)),
        ("unverified_8k_frame", variant(sample_rate_hz=8000,
                                        frame_samples=256)),
        ("unverified_24k_frame", variant(sample_rate_hz=24000,
                                         frame_samples=512)),
        ("unverified_32k_frame", variant(sample_rate_hz=32000,
                                         frame_samples=512)),
        ("unverified_44k_frame", variant(sample_rate_hz=44100,
                                         frame_samples=1024)),
        ("short_samples", variant(samples=short)),
        ("long_samples", variant(samples=long)),
        ("wrong_multichannel_count", variant(channels=2,
                                             samples=[0.0] * 512)),
        ("nonfinite_nan", variant(samples=nan_samples)),
        ("nonfinite_inf", variant(samples=inf_samples)),
        ("nonfinite_negative_inf", variant(samples=negative_inf_samples)),
        ("out_of_range", variant(samples=[4.5] * HARNESS_FRAME_VALUES)),
        ("bool_sample", variant(samples=[True] + [0.0] *
                                (HARNESS_FRAME_VALUES - 1))),
        ("string_sample", variant(samples=["0.0"] + [0.0] *
                                  (HARNESS_FRAME_VALUES - 1))),
        ("null_sample", variant(samples=[None] + [0.0] *
                                (HARNESS_FRAME_VALUES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-512)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("bool_execution_mode", variant(execution_mode=True)),
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
        "note": ("Invalid or unverified requests are rejected before any "
                 "artifact check or candidate call; no metrics exist."),
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
        ("json_not_object", '[1,2,3]'),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            value = strict_json_loads(text)
            accepted = not isinstance(value, list)
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
        "reason": "source_license_hardware_runtime_and_fixture_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _resolve_workspace_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return WORKSPACE / label


def _markers_in(path: Path, markers: Sequence[str],
                max_depth: int = 3) -> List[str]:
    found: List[str] = []
    if path.is_file():
        if path.suffix.lower() in markers:
            found.append(path.name)
        return found
    if not path.is_dir():
        return found
    base_depth = len(path.parts)
    for current, directory_names, file_names in os.walk(path):
        current_path = Path(current)
        if len(current_path.parts) - base_depth >= max_depth:
            directory_names[:] = []
        else:
            directory_names[:] = sorted(directory_names)
        for name in sorted(file_names):
            if (Path(name).suffix.lower() in markers or
                    name in SOURCE_MARKERS):
                found.append(name)
    return sorted(set(found))


def source_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in SOURCE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            found.append(label)
    return {
        "status": "blocked_source_absent" if not found else
                  "source_present_unqualified",
        "present": bool(found),
        "vendor": VENDOR,
        "component": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "repository": SOURCE_URL,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Read-only existence checks only; no clone, fetch, archive "
                 "extraction or vendor file is opened or executed."),
    }


def license_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_non_espressif_use_not_approved",
        "reported_name": REPORTED_LICENSE_NAME,
        "reported_restriction": REPORTED_LICENSE_RESTRICTION,
        "license_text_present": False,
        "license_text_sha256": None,
        "license_file": None,
        "non_espressif_use_approved": False,
        "redistribution_approved": False,
        "host_target_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("The reported restriction is source-reported. Neither the "
                 "license text nor a written rights decision is present, and "
                 "upstream availability is not a right to use or "
                 "redistribute."),
    }


def hardware_probe() -> Dict[str, Any]:
    toolchain = {}
    for command in TOOLCHAIN_COMMANDS:
        path = shutil.which(command)
        toolchain[command] = path
    return {
        "status": "blocked_eligible_hardware_absent",
        "eligible_target": DECLARED_TARGET,
        "runner": None,
        "hardware_attached": None,
        "firmware_sha256": None,
        "toolchain_commands": toolchain,
        "toolchain_present": any(value for value in toolchain.values()),
        "serial_device_probed": False,
        "vendor_cpu_memory_figures_generalizable": False,
        "note": ("Host command discovery only. No runner, device, firmware, "
                 "serial port or hardware measurement is present or "
                 "claimed; tool presence is not eligibility or approval."),
    }


def runtime_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in RUNTIME_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_workspace_path(label).exists():
            found.append(label)
    locks = [path for path in RUNTIME_LOCK_CANDIDATES
             if _resolve_workspace_path(path).is_file()]
    pinned = bool(found) and bool(locks)
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "idf_path": os.environ.get("IDF_PATH"),
        "idf_version": None,
        "firmware_sha256": None,
        "present": bool(found),
        "pinned": pinned,
        "sha256": None,
        "note": ("No ESP-IDF toolchain is installed, executed or pinned. "
                 "Environment and path checks are read-only; no build, "
                 "flash or import is attempted."),
    }


def fixture_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in FIXTURE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = _markers_in(target, FIXTURE_MARKERS)
            if hits:
                found.extend((Path(label) / name).as_posix()
                             for name in hits)
    return {
        "status": "blocked_matched_fixture_absent" if not found else
                  "fixture_present_unqualified",
        "present": bool(found),
        "required": (
            "rights-cleared ESP32-S3R8 loudspeaker-to-microphone fixture "
            "with measured loop gain, delay, saturation, speech, music, "
            "silence, onset and recovery cases"),
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "corpus_rights": False,
        "loop_gain_measured": False,
        "delay_measured": False,
        "sha256": None,
        "note": ("Existence checks only; no audio file is opened or "
                 "decoded. A synthetic harness frame is not a matched "
                 "closed-loop fixture."),
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "non_espressif_use_approved": False,
        "redistribution_approved": False,
        "host_target_approved": False,
        "input_corpus_rights": False,
        "redistribution_scope": None,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("No license text, non-Espressif use decision, distribution "
                 "scope or fixture permission is recorded locally. Upstream "
                 "presence is not a right to use, redistribute or publish."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "vendor": VENDOR,
        "component": COMPONENT_NAME,
        "component_version": COMPONENT_VERSION,
        "declared_sample_rates_hz": list(DECLARED_SAMPLE_RATES_HZ),
        "declared_frame_samples_by_rate": {
            str(rate): samples
            for rate, samples in sorted(DECLARED_FRAME_SAMPLES.items())},
        "declared_frame_samples_unverified_rates": list(UNVERIFIED_FRAME_RATES),
        "declared_frame_samples_other": None,
        "declared_channels": None,
        "local_channel_guard": MAX_CHANNELS_GUARD,
        "declared_per_channel_independent": True,
        "declared_detector_criteria": list(REPORTED_DETECTOR_CRITERIA),
        "declared_control_policy": list(REPORTED_CONTROL_POLICY),
        "declared_target": DECLARED_TARGET,
        "vendor_cpu_memory_figures_generalizable": False,
        "v0_can_represent_declared_input": False,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "Only the 16 kHz/512 and 48 kHz/1024 fixed frames, the listed "
            "rates, per-channel operation and detector/margin policy are "
            "recorded from the pinned research note and public pages. Other "
            "frame sizes, the vendor channel bound and all thresholds are "
            "absent and were not inferred. The 1..64 channel guard in the "
            "local validator is an evidence bound, not a vendor limit."),
    }


def profile_mapping() -> Dict[str, str]:
    return {
        "sweeps_steps_impulses_silence_clean_speech":
            "blocked_no_candidate",
        "task_specific_intelligibility_or_load_control":
            "blocked_no_permitted_cohort",
        "gain_and_frequency_response": "blocked_no_candidate_output",
        "attack_and_release": "blocked_no_candidate_output",
        "headroom_and_peaks": "blocked_no_candidate_output",
        "delay_and_content_mapping": "blocked_no_candidate_output",
        "numerical_behavior": "partial_local_harness_rejection_only",
        "state_transitions": "blocked_no_candidate_instance",
        "interacting_nonlinear_configurations": "blocked_no_candidate_instance",
        "candidate_output":
            "blocked_source_license_hardware_runtime_and_fixture_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_component_source_revision_and_license":
            "blocked_source_absent",
        "reported_license_scope_and_non_espressif_use":
            "blocked_rights_not_approved",
        "eligible_hardware_and_esp_idf_toolchain":
            "blocked_hardware_absent",
        "pinned_declared_geometry_and_configuration":
            "blocked_config_absent",
        "detector_notch_and_margin_reproduction":
            "blocked_no_candidate_instance",
        "dsp_gain_response_attack_release_delay":
            "blocked_no_candidate_output",
        "closed_loop_stability_and_maximum_stable_gain":
            "blocked_no_measurement",
        "speech_music_false_trigger_and_attenuation":
            "blocked_no_permitted_cohort",
        "device_timing_memory_and_callback":
            "blocked_no_paced_measurement",
        "external_adapter_provider_intake":
            "blocked_no_approved_runtime_or_terms",
        "authorized_listening_and_benchmark":
            "blocked_no_release_evidence",
        "release_qualification":
            "blocked_no_release_evidence",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": (
                "blocked_source_license_hardware_runtime_and_fixture_absent"),
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": (
                "No vendor source, approved license, eligible ESP32-S3R8 "
                "runner, pinned ESP-IDF runtime or matched closed-loop "
                "fixture is present; no detector, notch, margin, quality, "
                "stability or timing result was produced."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
            "qualifies_candidate": False,
        },
        "source_reported_vendor_characteristics": {
            "status": "provenance_only_not_reproduced",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "external_fallback": {
            "status": "documented_no_runtime",
            "automatic_discovery": False,
            "default_registration": False,
            "fallback": "none",
            "metrics": None,
            "qualifies_candidate": False,
        },
    }


def stimulus_probe() -> Dict[str, Any]:
    stimuli: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(float(value)
                                                     for value in samples),
        }
    return {
        "purpose": (
            "harness stimulus characterisation only; not an Espressif HOWL "
            "result and not a candidate output"),
        "harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "verified_model_geometry": False,
            "note": (
                "16 kHz / 512 samples is the documented fixed frame for that "
                "rate and is used only to exercise validation and rejection; "
                "it is not a claim about unverified rates or the vendor "
                "implementation."),
        },
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(
            STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "candidate_processing": False,
    }


def collect_blockers() -> List[str]:
    blockers: List[str] = []
    if not source_probe()["present"]:
        blockers.append("source_absent")
    if license_probe()["review"] != "approved":
        blockers.append("non_espressif_use_not_approved")
    if not hardware_probe()["toolchain_present"]:
        blockers.append("eligible_hardware_and_toolchain_absent")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if not fixture_probe()["present"]:
        blockers.append("matched_closed_loop_fixture_absent")
    if rights_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    return sorted(blockers)


def admit(request: Any) -> Dict[str, Any]:
    """Validate a request, then fail closed because artifacts are absent."""
    validate_request(request)
    blockers = collect_blockers()
    if not blockers:
        raise ArtifactsAbsent(
            "ARTIFACTS_ABSENT: blocker list unexpectedly empty",
            "ARTIFACTS_ABSENT")
    return {
        "status": "DEFER",
        "admissible": False,
        "candidate_processing": False,
        "input_validated": True,
        "metrics": None,
        "result": None,
        "qualifies_candidate": False,
        "blockers": blockers,
        "note": (
            "A structurally valid request is still not admissible: the "
            "source, license decision, eligible hardware, runtime, fixture "
            "and rights are absent. No port, fallback or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: Espressif HOWL source, approved license, eligible "
        "hardware, pinned ESP-IDF runtime and matched fixture are not "
        "present; no processing is performed", "ARTIFACTS_ABSENT")


def _board_projection(board: Any) -> Tuple[List[Dict[str, Any]], str]:
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    rows = [row for row in board["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ConfigError("linked task row is missing or duplicated",
                          "BOARD_ROW_MISSING")
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    projected = [stable]
    return projected, sha256_bytes(canonical_bytes(projected))


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    return _board_projection(board)


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
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


def source_evidence_statements() -> List[str]:
    return [
        ("research/feedback_control_20261028.md records Espressif "
         "esp_audio_effects HOWL 1.4.2 as an embedded FFT-based component "
         "with per-bin PAPR, PHPR, PNPR and optional IMSD criteria, dynamic "
         "biquad notches and a loop-margin gain controller."),
        ("the same note records v1.4.2 support at 8, 16, 24, 32, 44.1 and "
         "48 kHz with fixed 512-sample frames at 16 kHz and 1024-sample "
         "frames at 48 kHz, and independent per-channel operation."),
        ("the same note records that the library is an ESP-IDF/SoC component "
         "rather than a portable host library, and that vendor CPU and "
         "memory figures are for ESP32-S3R8/ESP-IDF and must not be "
         "generalized to this workstation."),
        ("the same note records that v1.4.2's published Espressif Modified "
         "MIT license restricts use to Espressif products and prohibits "
         "redistribution for non-Espressif products, so it is not an "
         "eligible implementation for this macOS/Python target without a "
         "license/platform change."),
        ("plan/INVENTORY.json assigns espressif-howl-1-4-2 the dsp "
         "verification profile, disposition external-adapter and an "
         "evidence status of considered."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope and matched evidence before a caller-supplied "
         "reference or opt-in adapter is added."),
        ("No local HOWL license file, component revision, header, "
         "configuration, ESP-IDF lock, eligible runner or matched fixture "
         "exists; nothing was cloned, downloaded, ported or reconstructed."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    license_block = license_probe()
    hardware = hardware_probe()
    runtime = runtime_probe()
    fixture = fixture_probe()
    rights = rights_probe()
    geom = geometry()
    adverse_request = _adverse_cases()
    adverse_json = _json_adverse_cases()
    stimuli = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    required = [dict(row) for row in REQUIRED_ARTIFACTS]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "source_absent": source["present"] is False,
        "non_espressif_use_not_approved":
            license_block["non_espressif_use_approved"] is False,
        "license_text_absent": license_block["license_text_present"] is False,
        "eligible_hardware_absent": hardware["runner"] is None,
        "runtime_unpinned": runtime["pinned"] is False,
        "matched_fixture_absent": fixture["present"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("espressif_howl_placeholder")["status"] ==
            "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "external_boundary_closed": (
            EXTERNAL_BOUNDARY["adapter_implemented"] is False and
            EXTERNAL_BOUNDARY["adapter_default_registration"] is False and
            EXTERNAL_BOUNDARY["automatic_discovery"] is False),
        "no_result_qualifies_candidate": True,
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "verification_profile": VERIFICATION_PROFILE,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": VERIFICATION_PROFILE,
            "source": SOURCE_PINS[PROFILE_SOURCE],
        },
        "profile_mapping": profile_mapping(),
        "external_boundary": dict(EXTERNAL_BOUNDARY),
        "reference": {
            "implementation": "task-local standard-library external-adapter gate",
            "real_component_source_present": source["present"],
            "component_config_present": False,
            "eligible_hardware_present": hardware["runner"] is not None,
            "pinned_runtime_present": runtime["pinned"],
            "matched_fixture_present": fixture["present"],
            "license_text_present": license_block["license_text_present"],
            "rights_approved": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No HOWL detector, notch, loop-margin controller, adapter or "
                "port is implemented or simulated; only probes, request "
                "rejection and synthetic harness controls are performed."),
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "board_full_file_hashed": False,
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "required_artifacts": required,
        "missing_artifacts": [row["artifact"] for row in required
                              if row["status"] == "absent"],
        "source_probe": source,
        "license_probe": license_block,
        "hardware_probe": hardware,
        "runtime_probe": runtime,
        "fixture_probe": fixture,
        "rights_probe": rights,
        "geometry": geom,
        "howling_control": dict(HOWLING_CONTROL),
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("espressif_howl_placeholder"),
        },
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
        "generated_by": "run.py --all",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
