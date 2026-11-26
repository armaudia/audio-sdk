# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only ai-coustics Rook boundary reference (DEFER).

This is a *proposal-only* enhancement-profile evidence package.  It does not
contain, link, download, install, import, execute or emulate the proprietary
ai-coustics Rook SDK, its model artifacts, its runtimes or any vendor tool.
The licensed artifact, its own terms, a pinned SDK runtime, a rights-cleared
cohort and calibrated reference outputs are absent, so every candidate result
is ``None`` with an explicit status and no result qualifies.

Rook is documented by the pinned census as the multi-speaker listening /
broad-enhancement variant of the product family.  It is a commercial product
comparator, not a pure stationary-noise baseline, and no Rook output exists
here.

What is reproduced mechanically is only the *declared external boundary*:

* the installed v0 grid (16 kHz, mono, float32, 160 samples per frame);
* the vendor-declared rate variants (8/16/48 kHz) and the source-reported
  30 ms latency claim, converted to samples arithmetically and explicitly not
  measured;
* a strict caller-supplied artifact-manifest contract that validates shape,
  geometry, absolute caller-owned paths, full SHA-256 and provider checksum
  prefix, but never parses, loads or executes the artifact; and
* deterministic synthetic identity and fixed high-pass controls on a seeded
  harmonic/noise fixture, labelled as local controls, not Rook output.

No synthetic number here is a Rook prediction, a quality score, a STOI, a
human rating, a device measurement, a benchmark or a release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-AI-COUSTICS-ROOK"
COMPONENT = "ai-coustics-rook"
TITLE = "ai-coustics Rook"
BASE_COMMIT = "2249c0662275966f31c2fe3c7e5b2c04b72f2ff2"
BRANCH = "swarm/SDK-AI-COUSTICS-ROOK"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_incomplete_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
PROPOSAL_ONLY = True
LOCAL_IDENTITY = "ai-coustics-rook-external-boundary-reference-v1"

# Installed v0 stays untouched; these constants are boundary facts only.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
MAX_ABS_INPUT = 8.0

# Vendor-declared values from the pinned census.  None is reproduced here.
VENDOR_MODEL_LOCATOR = "https://huggingface.co/ai-coustics/speech-enhancement"
VENDOR_FAMILY = "Rook"
VENDOR_SPEAKER_FOCUS = "multi_speaker_listening_broad_enhancement"
VENDOR_ROLE = "commercial_product_comparator_not_pure_noise_only_baseline"
VENDOR_RATES_HZ = (8000, 16000, 48000)
VENDOR_CLAIMED_LATENCY_MS = 30
VENDOR_CHECKSUM_POLICY = "versioned_hash_prefixes_only"
VENDOR_INFERENCE_SURFACE = "vendor_sdk"
VENDOR_PRODUCT_TYPE = "proprietary_sdk_and_versioned_downloadable_artifacts"
VENDOR_TERMS_STATUS = "proprietary_terms_require_account_review"

# Deterministic synthetic fixture, not speech and not a corpus.
FIXTURE_SAMPLES = 32000
FIXTURE_FRAMES = FIXTURE_SAMPLES // FRAME_SAMPLES
SINE_BINS = 256
NOISE_SEED = 20261127
FIXTURE_RATE_HZ = 16000
CLEAN_SEGMENTS: Tuple[Tuple[int, int, float, Tuple[float, ...]], ...] = (
    (0, 3200, 0.0, ()),
    (3200, 11200, 0.04, (200.0, 400.0, 600.0)),
    (11200, 19200, 0.15, (240.0, 480.0, 960.0)),
    (19200, 27200, 0.28, (160.0, 480.0, 640.0)),
    (27200, 32000, 0.0, ()),
)
NOISE_SEGMENTS: Tuple[Tuple[int, int, float], ...] = (
    (0, 3200, 0.0),
    (3200, 11200, 0.015),
    (11200, 19200, 0.045),
    (19200, 27200, 0.09),
    (27200, 32000, 0.0),
)
CLICK_START = 19240
CLICK_PERIOD = 1280
CLICK_AMPLITUDE = 0.40
HIGHPASS_CUTOFF_HZ = 80.0
HIGHPASS_Q = 0.7071067811865476

MANIFEST_FIELDS: Tuple[str, ...] = (
    "artifact_id",
    "artifact_path",
    "artifact_sha256",
    "artifact_version",
    "caller_attestation",
    "candidate_id",
    "channels",
    "license_path",
    "license_sha256",
    "model_family",
    "provider_checksum_prefix",
    "rights_approval_path",
    "rights_approval_sha256",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "sdk_version",
    "terms_accepted",
)
CALLER_ATTESTATION = "caller_owned_and_rights_reviewed"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
PREFIX_RE = re.compile(r"^[0-9a-f]{8,64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,95}$")

SOURCE_PINS: Dict[str, str] = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/evidence/pilot-discovery-20261027/source.txt":
        "3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590",
    "research/store/HEAD.json":
        "0f94611fa99911ac1624a3b1eedb576a671fb63a6d8797167e40bfeb7b36fe02",
    "research/store/snapshots/"
    "90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f6669b2c8.jsonl":
        "90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f6669b2c8",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/aecmos/contract.json":
        "cb16dc243891446e987be5aac771cebe3af087582d635d8fc7366dbb8de5367c",
    "docs/task-evidence/aecmos/report.json":
        "8055f6627d462c124182743469109a850087c11773899a6f64b02309be16c320",
    "docs/task-evidence/hush/contract.json":
        "dff969f74ebb1e7627bebe90aa73e8e40eb18efca99b44d5a956be4208a04d03",
    "docs/task-evidence/hush/report.json":
        "deaa6ff7bf89bb2727619e69cd41ce40b481ae7db93d25a007cb04b3a218cac4",
    "docs/task-evidence/deepfilternet3-local-listening-preset/contract.json":
        "71dce6d33ba03312245abce828a5aa864461ef4376d15a0846eb95decd928a18",
    "docs/task-evidence/deepfilternet3-local-listening-preset/report.json":
        "66398406770227f04c6d6ab6780bd5f479a3790f5be973a3023e3d9b42e1b95a",
    "docs/task-evidence/stoi-estoi/contract.json":
        "aa42da4c71b6eee281fca1ccc52f394c32d85cb2c65e31d1bc0a814a7726f7f5",
    "docs/task-evidence/stoi-estoi/report.json":
        "a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82",
    "docs/task-evidence/fastenhancer-small-reference/contract.json":
        "b14d6c657c0ba74b120dc9b8e84c34f381ccef41d52a59e6a7f2434d542e7ce0",
    "docs/task-evidence/fastenhancer-small-reference/report.json":
        "ecb188b4a1f0d929bd8ddcc19aa1fdb81a7d42892e6dc7aef3ed81aa37bc456e",
}
# The ai-coustics Quail package is the sibling branch package for this task.
# At this base commit it is committed on its own swarm branch and is not on
# main, so these digests are recorded provenance only and are not required to
# be present in this worktree.
QUAIL_SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/ai-coustics-quail/contract.json":
        "39c0b277fdff552bacb53dfee86614cfc5273b747800cfacbbbce6330fd95d23",
    "docs/task-evidence/ai-coustics-quail/report.json":
        "77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0",
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "external-adapter",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "evidence": ["research/noise_suppression_candidate_census.md"],
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}
MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "mutable": True,
    "gate": False,
    "hashed": False,
    "note": (
        "Only the stable linked-row identity above is compared. The mutable "
        "full board file is never read into, hashed by or pinned to this "
        "package."
    ),
}
SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "installed_v0_format": "16 kHz mono float32, 160 samples",
    "vendor_artifact": False,
    "vendor_sdk_runtime": False,
    "licensed_source_or_binary": False,
    "model_runtime_executed": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "downloads": False,
    "network_used": False,
    "provider_registered": False,
    "device_timing": False,
    "listening": False,
    "benchmark_claim": False,
    "release_claim": False,
}
PUBLIC_SURFACE: Dict[str, bool] = {
    "abi_change": False,
    "benchmark_claim": False,
    "ci_change": False,
    "descriptor_default_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_change": False,
    "registry_change": False,
    "release_claim": False,
    "shared_cmakelists_change": False,
}
QUALIFICATION: Dict[str, Any] = {
    "status": QUALIFICATION_STATUS,
    "qualifies": False,
    "incomplete": True,
    "proposal_only": True,
    "missing_result_promoted": False,
    "vendor_artifact_present": False,
    "vendor_runtime_present": False,
    "source_licensed": False,
    "rights_cleared_cohort_present": False,
    "paired_quality_result_present": False,
    "stoi_result_present": False,
    "listening_present": False,
    "measured_timing_present": False,
    "device_timing_present": False,
    "release_claim": False,
    "all_release_gates_blocked": True,
    "local_control_is_candidate": False,
}
REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "vendor_sdk_and_model_artifact",
        "artifact": (
            "The exact ai-coustics Rook vendor SDK and model artifact for at "
            "least one declared rate, identified by an immutable version and a "
            "full SHA-256 rather than a checksum prefix."
        ),
        "present": False,
        "rights_requirement": (
            "The artifact-specific proprietary terms, redistribution and "
            "derivative-output permissions, and written approval to execute."
        ),
        "why_blocked": (
            "No ai-coustics checkout, SDK package or model artifact exists in "
            "the workspace; no download, copy or substitute was attempted."
        ),
    },
    {
        "id": "proprietary_license_and_rights_approval",
        "artifact": (
            "The exact vendor licence text and a signed rights decision for "
            "local execution, benchmarking, redistribution and output use."
        ),
        "present": False,
        "rights_requirement": (
            "Vendor account terms, model-use terms, redistribution terms and "
            "output-use permissions for the named artifact version."
        ),
        "why_blocked": (
            "The pinned census records only that proprietary service/model "
            "terms require account review; no licence text or approval exists."
        ),
    },
    {
        "id": "pinned_sdk_runtime_environment",
        "artifact": (
            "A locked runtime environment with exact versions, install digest "
            "and an approved import/link route for the vendor SDK."
        ),
        "present": False,
        "rights_requirement": (
            "Runtime and dependency licences plus approval for the exact "
            "versions on the target host."
        ),
        "why_blocked": (
            "No environment, package lock or installed SDK was found; no "
            "import or execution was attempted."
        ),
    },
    {
        "id": "official_geometry_and_process_contract",
        "artifact": (
            "The official channel, frame/hop, resampling, reset, drain, state, "
            "content-delay and availability contract for the exact runtime."
        ),
        "present": False,
        "rights_requirement": (
            "Vendor documentation admitted under the reviewed terms."
        ),
        "why_blocked": (
            "The pinned record declares 8/16/48 kHz variants and a 30 ms "
            "latency claim only; no frame, hop, reset, drain or delay contract "
            "is established."
        ),
    },
    {
        "id": "rights_cleared_paired_cohort",
        "artifact": (
            "A rights-cleared paired noisy/clean speech cohort with consent, "
            "device metadata, alignment and a frozen utterance list."
        ),
        "present": False,
        "rights_requirement": (
            "Corpus, participant, device and redistribution rights for every "
            "recording used."
        ),
        "why_blocked": (
            "No cohort, consent, pairing, alignment or metadata exists for "
            "this task; no real audio is used here."
        ),
    },
    {
        "id": "calibrated_reference_outputs_and_scorer",
        "artifact": (
            "Approved exact-runtime reference outputs and a pinned approved "
            "SI-SDR/STOI and preservation scoring implementation."
        ),
        "present": False,
        "rights_requirement": (
            "Scorer and reference-output terms plus approval for the exact "
            "implementation revisions."
        ),
        "why_blocked": (
            "No reference output, clean-reference oracle or approved STOI "
            "implementation is present; all quality slots are null."
        ),
    },
    {
        "id": "measured_content_and_device_timing",
        "artifact": (
            "Measured content delay, availability delay, memory, state "
            "isolation and callback suitability on the target device."
        ),
        "present": False,
        "rights_requirement": (
            "Device, host and timing-harness approval for the exact runtime."
        ),
        "why_blocked": (
            "The 30 ms value is a source-reported claim converted to samples; "
            "no timing, memory, state or callback measurement exists."
        ),
    },
    {
        "id": "opt_in_adapter_intake_and_release_review",
        "artifact": (
            "An OFF-by-default opt-in adapter intake, independent exact-head "
            "review, listening/quality authorization and explicit release "
            "approval."
        ),
        "present": False,
        "rights_requirement": (
            "Reviewer, panel and release-authority approval for the declared "
            "scope."
        ),
        "why_blocked": (
            "No adapter, registration, default, review, listening panel or "
            "release decision exists; none is added here."
        ),
    },
]
RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "exact_vendor_artifact_and_full_checksum",
        "requirement": (
            "The exact ai-coustics Rook artifact for a declared rate, with an "
            "immutable version and a full SHA-256; a provider checksum prefix "
            "alone is not an identity."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "proprietary_license_and_distribution_terms",
        "requirement": (
            "The artifact-specific proprietary licence, redistribution, "
            "derivative-output and execution permissions, reviewed and "
            "approved in writing."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "pinned_sdk_runtime_and_environment",
        "requirement": (
            "A locked vendor SDK runtime with exact dependency versions, "
            "install/import digest and approval for the target host."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "official_geometry_content_and_availability_delay",
        "requirement": (
            "The official rate, channels, frame/hop, resampling, reset, drain, "
            "state and content/availability delay are pinned and reproduced "
            "for the exact runtime; the 30 ms claim is not a measurement."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "rights_cleared_paired_cohort",
        "requirement": (
            "A rights-cleared paired noisy/clean speech cohort with consent, "
            "device metadata, alignment and a frozen utterance list."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "independent_paired_quality_and_preservation",
        "requirement": (
            "Independent paired SI-SDR/STOI, clean-speech preservation, peak "
            "and invalid-output scoring on the exact runtime, with uncertainty "
            "and retained failures."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "measured_state_memory_and_target_timing",
        "requirement": (
            "Measured state isolation, memory, content/availability timing, "
            "callback suitability and adverse/nonfinite behavior on the target "
            "device."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "opt_in_adapter_intake_listening_and_release_review",
        "requirement": (
            "An OFF-by-default opt-in adapter intake, independent exact-head "
            "review, authorized listening/quality assessment and explicit "
            "release approval."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]
NON_CLAIMS: List[str] = [
    "No ai-coustics Rook SDK, model artifact, weight, runtime or emulator is present, linked, imported, executed or reproduced.",
    "No licensed artifact, corpus or recording is downloaded, copied, vendored or substituted.",
    "No Rook prediction, quality score, SI-SDR, STOI, MOS, ranking or threshold is claimed; every candidate result is null.",
    "The 30 ms latency is a source-reported claim converted arithmetically to samples; it is not a measurement.",
    "No synthetic control, digest or diagnostic is a Rook output, a human rating or a quality score.",
    "No listening, device-timing, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No provider or processor is registered, exposed or default-enabled.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --report",
    "python3 run.py --contract",
    "python3 run.py --sources",
    "python3 run.py --inspect",
    "python3 verify.py",
]
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
REPORT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "schema_id",
    "task",
    "component",
    "title",
    "profile",
    "status",
    "completeness",
    "decision",
    "proposal_only",
    "base_commit",
    "branch",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "quail_sibling_pins",
    "scope",
    "public_surface",
    "vendor_record",
    "declared_contract",
    "manifest_contract",
    "required_artifacts",
    "fixture",
    "controls",
    "manifest_controls",
    "adverse_results",
    "missing_results",
    "qualification_slots",
    "failure_controls",
    "acceptance_profile",
    "observed_provenance",
    "artifact_assessment",
    "ranking",
    "release_gates",
    "non_claims",
    "reproduction",
    "regeneration",
}
CONTRACT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "schema_id",
    "task",
    "component",
    "title",
    "profile",
    "status",
    "completeness",
    "decision",
    "proposal_only",
    "base_commit",
    "branch",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "quail_sibling_pins",
    "scope",
    "public_surface",
    "vendor_record",
    "declared_contract",
    "manifest_contract",
    "required_artifacts",
    "release_gates",
    "artifact_pins",
    "local_files",
    "reproduction",
    "non_claims",
}


class ReferenceError(ValueError):
    """Explicit rejection; no rejected value is scored or promoted."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    """Parse strict JSON; duplicate keys, NaN and Infinity are rejected."""
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"),
                       parse_constant=_reject_constant,
                       object_pairs_hook=unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("json_root_is_not_an_object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True,
                      allow_nan=False)
    payload = (text + "\n").encode("utf-8")
    return text, sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _r9(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 9)


# ---------------------------------------------------------------------------
# Deterministic synthetic fixture and local controls
# ---------------------------------------------------------------------------

def _sine_table() -> List[float]:
    return [math.sin(2.0 * math.pi * index / SINE_BINS)
            for index in range(SINE_BINS)]


SINE_TABLE = _sine_table()


def _quantize(value: float) -> float:
    scaled = int(round(float(value) * 32767.0))
    if scaled > 32767:
        scaled = 32767
    if scaled < -32768:
        scaled = -32768
    return scaled / 32768.0


def _phase(frequency_hz: float, sample_index: int) -> int:
    return (sample_index * int(round(frequency_hz * SINE_BINS))
            // FIXTURE_RATE_HZ) % SINE_BINS


def build_clean() -> List[float]:
    values: List[float] = []
    for start, end, amplitude, frequencies in CLEAN_SEGMENTS:
        for index in range(start, end):
            if amplitude == 0.0 or not frequencies:
                sample = 0.0
            else:
                total = 0.0
                for order, frequency in enumerate(frequencies):
                    weight = 1.0 / float(order + 1)
                    total += weight * SINE_TABLE[_phase(frequency, index)]
                sample = amplitude * total / 1.8333333333333333
            if (CLICK_START <= index < 27200
                    and (index - CLICK_START) % CLICK_PERIOD == 0):
                sample += CLICK_AMPLITUDE
            values.append(_quantize(sample))
    return values


def build_noise() -> List[float]:
    state = NOISE_SEED & 0x7FFFFFFF
    values: List[float] = []
    levels = _noise_levels()
    for index in range(FIXTURE_SAMPLES):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        unit = ((state >> 8) / float(1 << 23)) - 1.0
        values.append(_quantize(unit * levels[index]))
    return values


def _noise_levels() -> List[float]:
    levels: List[float] = []
    for start, end, level in NOISE_SEGMENTS:
        levels.extend([level] * (end - start))
    return levels


def build_mixture() -> List[float]:
    clean = build_clean()
    noise = build_noise()
    return [_quantize(clean[index] + noise[index])
            for index in range(FIXTURE_SAMPLES)]


def _highpass_coefficients() -> Tuple[float, float, float, float, float]:
    w0 = 2.0 * math.pi * HIGHPASS_CUTOFF_HZ / FIXTURE_RATE_HZ
    alpha = math.sin(w0) / (2.0 * HIGHPASS_Q)
    cos_w0 = math.cos(w0)
    b0 = (1.0 + cos_w0) / 2.0
    b1 = -(1.0 + cos_w0)
    b2 = b0
    a0 = 1.0 + alpha
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


HIGHPASS_COEFFICIENTS = _highpass_coefficients()


def apply_fixed_highpass(values: Sequence[float]) -> List[float]:
    b0, b1, b2, a1, a2 = HIGHPASS_COEFFICIENTS
    output: List[float] = []
    x1 = 0.0
    x2 = 0.0
    y1 = 0.0
    y2 = 0.0
    for value in values:
        sample = float(value)
        result = b0 * sample + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        output.append(result)
        x2 = x1
        x1 = sample
        y2 = y1
        y1 = result
    return output


def _energy(values: Sequence[float]) -> float:
    return sum(float(value) * float(value) for value in values)


def _rms(values: Sequence[float]) -> float:
    if not values:
        raise ReferenceError("empty_signal")
    return math.sqrt(_energy(values) / float(len(values)))


def _peak(values: Sequence[float]) -> float:
    return max(abs(float(value)) for value in values)


def _si_sdr_db(reference: Sequence[float],
               estimate: Sequence[float]) -> Optional[float]:
    if len(reference) != len(estimate) or not reference:
        raise ReferenceError("length_mismatch")
    reference_energy = _energy(reference)
    if reference_energy <= 1e-30:
        return None
    scale = sum(float(r) * float(e)
                for r, e in zip(reference, estimate)) / reference_energy
    target = [scale * float(r) for r in reference]
    residual = [float(e) - t for e, t in zip(estimate, target)]
    residual_energy = _energy(residual)
    if residual_energy <= 1e-30:
        return None
    return 10.0 * math.log10(_energy(target) / residual_energy)


def _snr_db(reference: Sequence[float],
            estimate: Sequence[float]) -> Optional[float]:
    if len(reference) != len(estimate) or not reference:
        raise ReferenceError("length_mismatch")
    signal = _energy(reference)
    residual = _energy([float(e) - float(r)
                        for r, e in zip(reference, estimate)])
    if residual <= 1e-30:
        return None
    if signal <= 0.0:
        return None
    return 10.0 * math.log10(signal / residual)


def _digest_f32(values: Sequence[float]) -> str:
    payload = struct.pack("<%df" % len(values), *[float(v) for v in values])
    return sha256_bytes(payload)


def fixture_payload() -> Dict[str, Any]:
    clean = build_clean()
    noise = build_noise()
    mixture = build_mixture()
    segments = []
    for start, end, amplitude, frequencies in CLEAN_SEGMENTS:
        segments.append({
            "start_sample": start,
            "end_sample_exclusive": end,
            "start_frame": start // FRAME_SAMPLES,
            "end_frame_exclusive": end // FRAME_SAMPLES,
            "clean_amplitude": amplitude,
            "harmonic_hz": list(frequencies),
        })
    return {
        "fixture_id": "ai-coustics-rook-synthetic-boundary-fixture-v1",
        "sample_rate_hz": FIXTURE_RATE_HZ,
        "channels": CHANNELS,
        "samples": FIXTURE_SAMPLES,
        "frames": FIXTURE_FRAMES,
        "sample_format": "float32_from_int16_quantized",
        "noise_seed": NOISE_SEED,
        "segments": segments,
        "clean_sha256": _digest_f32(clean),
        "noise_sha256": _digest_f32(noise),
        "mixture_sha256": _digest_f32(mixture),
        "is_speech": False,
        "is_corpus": False,
        "is_candidate_output": False,
        "qualifies": False,
    }


def _control_row(control_id: str, reference: Sequence[float],
                 estimate: Sequence[float], status: str) -> Dict[str, Any]:
    clipped = sum(1 for value in estimate if abs(float(value)) > 1.0)
    nonfinite = sum(1 for value in estimate if not math.isfinite(float(value)))
    return {
        "control_id": control_id,
        "status": status,
        "samples": len(estimate),
        "output_sha256": _digest_f32(estimate),
        "rms": _r9(_rms(estimate)),
        "peak_abs": _r9(_peak(estimate)),
        "clipped_samples": clipped,
        "nonfinite_samples": nonfinite,
        "si_sdr_db_vs_synthetic_clean": _r9(_si_sdr_db(reference, estimate)),
        "snr_db_vs_synthetic_clean": _r9(_snr_db(reference, estimate)),
        "is_candidate_result": False,
        "qualifies": False,
    }


def controls_payload() -> Dict[str, Any]:
    clean = build_clean()
    mixture = build_mixture()
    highpass_mixture = apply_fixed_highpass(mixture)
    highpass_clean = apply_fixed_highpass(clean)
    silence = [0.0] * FIXTURE_SAMPLES
    highpass_silence = apply_fixed_highpass(silence)
    return {
        "design": {
            "identity": "exact passthrough",
            "fixed_highpass": {
                "cutoff_hz": HIGHPASS_CUTOFF_HZ,
                "q": HIGHPASS_Q,
                "order": 2,
                "coefficients_b0_b1_b2_a1_a2": [
                    _r9(value) for value in HIGHPASS_COEFFICIENTS
                ],
            },
            "is_ai_coustics_rook": False,
            "is_candidate_result": False,
        },
        "rows": {
            "identity_noisy": _control_row(
                "identity_noisy", clean, mixture,
                "local_control_only_not_rook"),
            "fixed_highpass_noisy": _control_row(
                "fixed_highpass_noisy", clean, highpass_mixture,
                "local_control_only_not_rook"),
            "identity_clean": _control_row(
                "identity_clean", clean, clean,
                "local_control_only_not_rook"),
            "fixed_highpass_clean": _control_row(
                "fixed_highpass_clean", clean, highpass_clean,
                "local_control_only_not_rook"),
            "identity_silence": _control_row(
                "identity_silence", silence, silence,
                "degenerate_silence_control_not_rook"),
            "fixed_highpass_silence": _control_row(
                "fixed_highpass_silence", silence, highpass_silence,
                "degenerate_silence_control_not_rook"),
        },
        "silence": {
            "identity_exact_zero": all(value == 0.0 for value in silence),
            "fixed_highpass_exact_zero": all(
                value == 0.0 for value in highpass_silence),
            "qualifies": False,
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Declared external boundary
# ---------------------------------------------------------------------------

def declared_latency_samples(rate_hz: int) -> int:
    if type(rate_hz) is not int:
        raise ReferenceError("latency_rate_is_not_an_integer")
    if rate_hz not in VENDOR_RATES_HZ:
        raise ReferenceError("unsupported_declared_rate")
    return rate_hz * VENDOR_CLAIMED_LATENCY_MS // 1000


def validate_geometry(rate_hz: Any, channels: Any, frame_samples: Any,
                      sample_format: Any) -> Dict[str, Any]:
    if type(rate_hz) is not int:
        raise ReferenceError("sample_rate_is_not_an_integer")
    if rate_hz not in VENDOR_RATES_HZ:
        raise ReferenceError("unsupported_sample_rate")
    if type(channels) is not int:
        raise ReferenceError("channels_is_not_an_integer")
    if channels != CHANNELS:
        raise ReferenceError("unsupported_channels")
    if type(frame_samples) is not int:
        raise ReferenceError("frame_samples_is_not_an_integer")
    if frame_samples != FRAME_SAMPLES:
        raise ReferenceError("unsupported_frame_samples")
    if sample_format not in ("f32", "float32"):
        raise ReferenceError("unsupported_sample_format")
    return {
        "sample_rate_hz": rate_hz,
        "channels": channels,
        "frame_samples": frame_samples,
        "sample_format": "f32",
        "v0_compatible": rate_hz == SAMPLE_RATE_HZ
        and frame_samples == FRAME_SAMPLES,
        "resampling_required": rate_hz != SAMPLE_RATE_HZ,
        "declared_latency_samples": declared_latency_samples(rate_hz),
        "geometry_measured": False,
        "qualifies": False,
    }


def declared_contract() -> Dict[str, Any]:
    return {
        "contract_id": "ai-coustics-rook-external-adapter-proposal/0.1",
        "adapter_status": "proposal_only_no_vendor_runtime",
        "host_grid": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "vendor_rates_hz": list(VENDOR_RATES_HZ),
        "declared_latency_ms": VENDOR_CLAIMED_LATENCY_MS,
        "declared_latency_samples_by_rate": {
            str(rate): declared_latency_samples(rate) for rate in VENDOR_RATES_HZ
        },
        "declared_latency_is_measured": False,
        "declared_latency_note": (
            "The 30 ms value is a source-reported claim; the sample counts are "
            "arithmetic conversions, not measurements."
        ),
        "comparator_role": VENDOR_ROLE,
        "speaker_focus": VENDOR_SPEAKER_FOCUS,
        "multi_speaker_listening": True,
        "pure_noise_only_baseline": False,
        "resampling_required_for_non_16k": True,
        "resampling_policy": "not_established",
        "process_contract": "not_established",
        "reset_contract": "not_established",
        "drain_contract": "not_established",
        "state_isolation_contract": "not_established",
        "channel_layout_contract": "not_established",
        "official_geometry_verified": False,
        "vendor_runtime_verified": False,
        "installed_v0_unchanged": True,
        "qualifies": False,
    }


def vendor_record() -> Dict[str, Any]:
    return {
        "candidate": "ai-coustics Rook",
        "family": VENDOR_FAMILY,
        "component": COMPONENT,
        "product_type": VENDOR_PRODUCT_TYPE,
        "model_locator": VENDOR_MODEL_LOCATOR,
        "speaker_focus": VENDOR_SPEAKER_FOCUS,
        "role": VENDOR_ROLE,
        "claimed_latency_ms": VENDOR_CLAIMED_LATENCY_MS,
        "sample_rates_hz": list(VENDOR_RATES_HZ),
        "artifact_checksum_policy": VENDOR_CHECKSUM_POLICY,
        "inference_surface": VENDOR_INFERENCE_SURFACE,
        "terms_status": VENDOR_TERMS_STATUS,
        "artifact_present": False,
        "runtime_present": False,
        "license_reviewed": False,
        "source_reported_only": True,
        "reproduced_here": False,
        "source_reported_scores_present": False,
        "qualifies": False,
    }


def _path_present(relative: str) -> bool:
    return (WORKSPACE / relative).exists()


def artifact_assessment() -> Dict[str, Any]:
    checked = (
        "data/checkouts/ai-coustics",
        "data/checkouts/rook",
        "data/models/ai-coustics",
        "data/models/rook",
        "data/sources/ai-coustics-rook",
        "data/licenses/ai-coustics-rook",
        "data/envs/ai-coustics-rook",
        "data/reference/ai-coustics-rook",
        "adapters/ai-coustics-rook",
        "adapters/rook",
    )
    presence = {path: _path_present(path) for path in checked}
    all_absent = not any(presence.values())
    return {
        "checked_paths": presence,
        "all_required_absent": all_absent,
        "vendor_artifact_present": any(
            presence[path] for path in checked
            if "models" in path or "sources" in path or "checkouts" in path),
        "vendor_runtime_present": any(
            presence[path] for path in checked if "envs" in path),
        "rights_approval_present": any(
            presence[path] for path in checked if "licenses" in path),
        "corpus_present": any(
            presence[path] for path in checked if "reference" in path),
        "package_assets_present": False,
        "conclusion": (
            "BLOCKED: no licensed ai-coustics Rook artifact, vendor SDK "
            "runtime, rights approval, clean-reference oracle or calibrated "
            "output exists locally; nothing was downloaded, copied or executed."
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied artifact manifest (shape only; never executed)
# ---------------------------------------------------------------------------

def _valid_manifest_document() -> Dict[str, Any]:
    return {
        "artifact_id": "rook-16k-artifact",
        "artifact_path": "/caller/ai-coustics/rook-16k.artifact",
        "artifact_sha256": "a" * 64,
        "artifact_version": "2026.1.0",
        "caller_attestation": CALLER_ATTESTATION,
        "candidate_id": "ai-coustics-rook",
        "channels": 1,
        "license_path": "/caller/ai-coustics/LICENSE.txt",
        "license_sha256": "b" * 64,
        "model_family": VENDOR_FAMILY,
        "provider_checksum_prefix": "a" * 12,
        "rights_approval_path": "/caller/ai-coustics/APPROVAL.txt",
        "rights_approval_sha256": "c" * 64,
        "runtime_path": "/caller/ai-coustics/sdk",
        "runtime_sha256": "d" * 64,
        "sample_rate_hz": 16000,
        "sdk_version": "1.2.3",
        "terms_accepted": True,
    }


def validate_manifest_path(key: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ReferenceError("path_is_not_a_nonempty_string:" + key)
    if "\\" in value:
        raise ReferenceError("path_is_not_posix:" + key)
    if not os.path.isabs(value):
        raise ReferenceError("path_is_not_absolute:" + key)
    parts = [part for part in value.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise ReferenceError("path_has_traversal_component:" + key)
    if not parts:
        raise ReferenceError("path_has_no_components:" + key)
    return value


def parse_manifest(document: Any) -> Dict[str, Any]:
    """Validate manifest shape; never open, parse or execute an artifact."""
    if not isinstance(document, dict):
        raise ReferenceError("manifest_is_not_an_object")
    keys = set(document)
    if keys != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - keys)
        extra = sorted(keys - set(MANIFEST_FIELDS))
        if missing:
            raise ReferenceError("manifest_missing_fields:" + ",".join(missing))
        raise ReferenceError("manifest_extra_fields:" + ",".join(extra))
    if document["candidate_id"] != COMPONENT:
        raise ReferenceError("manifest_candidate_id_mismatch")
    if document["model_family"] != VENDOR_FAMILY:
        raise ReferenceError("manifest_model_family_mismatch")
    for key in ("artifact_id", "artifact_version", "sdk_version"):
        value = document[key]
        if not isinstance(value, str) or not ID_RE.match(value):
            raise ReferenceError("manifest_invalid_identifier:" + key)
    for key in ("artifact_sha256", "license_sha256", "rights_approval_sha256",
                "runtime_sha256"):
        value = document[key]
        if not isinstance(value, str) or not HASH_RE.match(value):
            raise ReferenceError("manifest_invalid_sha256:" + key)
    prefix = document["provider_checksum_prefix"]
    if not isinstance(prefix, str) or not PREFIX_RE.match(prefix):
        raise ReferenceError("manifest_invalid_checksum_prefix")
    if not document["artifact_sha256"].startswith(prefix):
        raise ReferenceError("manifest_checksum_prefix_mismatch")
    rate = document["sample_rate_hz"]
    if type(rate) is not int:
        raise ReferenceError("manifest_sample_rate_is_not_an_integer")
    if rate not in VENDOR_RATES_HZ:
        raise ReferenceError("manifest_unsupported_sample_rate")
    channels = document["channels"]
    if type(channels) is not int:
        raise ReferenceError("manifest_channels_is_not_an_integer")
    if channels != CHANNELS:
        raise ReferenceError("manifest_unsupported_channels")
    if type(document["terms_accepted"]) is not bool:
        raise ReferenceError("manifest_terms_accepted_is_not_a_boolean")
    if document["terms_accepted"] is not True:
        raise ReferenceError("manifest_terms_not_accepted")
    if document["caller_attestation"] != CALLER_ATTESTATION:
        raise ReferenceError("manifest_caller_attestation_mismatch")
    paths = {}
    for key in ("artifact_path", "license_path", "rights_approval_path",
                "runtime_path"):
        paths[key] = validate_manifest_path(key, document[key])
    if len(set(paths.values())) != len(paths):
        raise ReferenceError("manifest_paths_are_not_distinct")
    normalized = dict(document)
    normalized["paths"] = paths
    normalized["shape_valid"] = True
    normalized["files_verified"] = False
    normalized["loaded"] = False
    normalized["executed"] = False
    normalized["official_identity"] = False
    normalized["qualifies"] = False
    return normalized


def verify_manifest_files(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Hash caller-owned files only; never parse, import or execute them."""
    if not manifest.get("shape_valid"):
        raise ReferenceError("manifest_shape_not_validated")
    for path_key, sha_key in (
            ("artifact_path", "artifact_sha256"),
            ("license_path", "license_sha256"),
            ("rights_approval_path", "rights_approval_sha256"),
            ("runtime_path", "runtime_sha256")):
        path = Path(manifest[path_key])
        if not path.is_file():
            raise ReferenceError("manifest_missing_file:" + path_key)
        if digest_file(path) != manifest[sha_key]:
            raise ReferenceError("manifest_hash_mismatch:" + path_key)
    return {
        "files_verified": True,
        "bytes_hashed_only": True,
        "loaded": False,
        "executed": False,
        "official_identity": False,
        "rights_review_required": True,
        "qualifies": False,
    }


def manifest_controls() -> List[Dict[str, Any]]:
    def run(control_id: str,
            mutate: Optional[Callable[[Dict[str, Any]], None]]) -> Dict[str, Any]:
        document = _valid_manifest_document()
        if mutate is not None:
            mutate(document)
        try:
            parse_manifest(document)
        except ReferenceError as error:
            return {
                "control_id": control_id,
                "accepted": False,
                "reason": str(error),
                "shape_only": True,
                "qualifies": False,
            }
        return {
            "control_id": control_id,
            "accepted": True,
            "reason": "shape_valid_files_not_verified",
            "shape_only": True,
            "files_verified": False,
            "official_identity": False,
            "qualifies": False,
        }

    def remove(key: str) -> Callable[[Dict[str, Any]], None]:
        def mutate(document: Dict[str, Any]) -> None:
            document.pop(key)
        return mutate

    def set_value(key: str, value: Any) -> Callable[[Dict[str, Any]], None]:
        def mutate(document: Dict[str, Any]) -> None:
            document[key] = value
        return mutate

    def duplicate_paths(document: Dict[str, Any]) -> None:
        document["license_path"] = document["artifact_path"]

    controls = [
        run("valid_shape", None),
        run("missing_artifact_id", remove("artifact_id")),
        run("extra_field", set_value("extra", 1)),
        run("wrong_candidate", set_value("candidate_id", "ai-coustics-quail")),
        run("wrong_family", set_value("model_family", "Quail")),
        run("relative_artifact_path",
            set_value("artifact_path", "rook-16k.artifact")),
        run("parent_traversal",
            set_value("artifact_path", "/caller/../rook-16k.artifact")),
        run("bad_hash_length", set_value("artifact_sha256", "a" * 63)),
        run("uppercase_hash", set_value("artifact_sha256", "A" * 64)),
        run("checksum_prefix_mismatch",
            set_value("provider_checksum_prefix", "f" * 12)),
        run("unsupported_rate", set_value("sample_rate_hz", 44100)),
        run("boolean_rate", set_value("sample_rate_hz", True)),
        run("stereo", set_value("channels", 2)),
        run("terms_not_accepted", set_value("terms_accepted", False)),
        run("wrong_attestation", set_value("caller_attestation", "trust_me")),
        run("duplicate_paths", duplicate_paths),
        run("empty_sdk_version", set_value("sdk_version", "")),
    ]
    return controls


def manifest_contract() -> Dict[str, Any]:
    return {
        "contract_id": "ai-coustics-rook/caller-supplied-licensed-artifact/0.1",
        "required_fields": list(MANIFEST_FIELDS),
        "checksum_policy": (
            "full_sha256_required_and_provider_checksum_prefix_must_match"
        ),
        "caller_owned": True,
        "vendored": False,
        "loaded": False,
        "executed": False,
        "official_identity_requires_vendor_review": True,
        "files_behavior": (
            "hash caller-owned bytes and geometry only; never parse, import, "
            "link or execute the artifact"
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Audio validation and adverse controls
# ---------------------------------------------------------------------------

def validate_audio(values: Any) -> int:
    if isinstance(values, (str, bytes, bytearray, dict)):
        raise ReferenceError("audio_is_not_a_sample_sequence")
    if not isinstance(values, (list, tuple)):
        raise ReferenceError("audio_is_not_a_list_or_tuple")
    if len(values) != FRAME_SAMPLES:
        raise ReferenceError("audio_frame_is_not_160_samples")
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceError("audio_sample_is_not_a_real_number")
        number = float(value)
        if not math.isfinite(number):
            raise ReferenceError("audio_sample_is_nonfinite")
        if abs(number) > MAX_ABS_INPUT:
            raise ReferenceError("audio_sample_out_of_range")
    return len(values)


def _adverse_vectors() -> List[Tuple[str, Any, str]]:
    base = [0.0] * FRAME_SAMPLES
    nan = list(base)
    nan[17] = float("nan")
    posinf = list(base)
    posinf[23] = float("inf")
    boolean = list(base)
    boolean[5] = True
    text = list(base)
    text[9] = "0.25"
    nested = list(base)
    nested[11] = [0.0]
    out_of_range = list(base)
    out_of_range[31] = 8.5
    return [
        ("nan_sample", nan, "audio_sample_is_nonfinite"),
        ("positive_infinity_sample", posinf, "audio_sample_is_nonfinite"),
        ("boolean_sample", boolean, "audio_sample_is_not_a_real_number"),
        ("string_sample", text, "audio_sample_is_not_a_real_number"),
        ("nested_sample", nested, "audio_sample_is_not_a_real_number"),
        ("short_frame_159", [0.0] * 159, "audio_frame_is_not_160_samples"),
        ("long_frame_161", [0.0] * 161, "audio_frame_is_not_160_samples"),
        ("empty_frame", [], "audio_frame_is_not_160_samples"),
        ("out_of_range_sample", out_of_range, "audio_sample_out_of_range"),
        ("mapping_container", {"samples": base},
         "audio_is_not_a_sample_sequence"),
    ]


def adverse_results() -> List[Dict[str, Any]]:
    rows = []
    for result_id, values, expected in _adverse_vectors():
        try:
            validate_audio(values)
        except ReferenceError as error:
            rows.append({
                "result_id": result_id,
                "status": "rejected",
                "error": str(error),
                "expected": expected,
                "matches_expected": str(error) == expected,
                "qualifies": False,
            })
        else:
            rows.append({
                "result_id": result_id,
                "status": "unexpected_acceptance",
                "error": None,
                "expected": expected,
                "matches_expected": False,
                "qualifies": False,
            })
    return rows


def missing_results() -> List[Dict[str, Any]]:
    items = (
        ("vendor_artifact", "Exact Rook artifact and full digest"),
        ("vendor_sdk_runtime", "Pinned executable vendor runtime"),
        ("proprietary_license", "Reviewed proprietary terms and approval"),
        ("rights_cleared_cohort", "Paired noisy/clean cohort with consent"),
        ("candidate_output", "Rook output on any declared rate"),
        ("paired_si_sdr", "Paired SI-SDR on a rights-cleared cohort"),
        ("paired_stoi", "Paired STOI with an approved implementation"),
        ("clean_speech_preservation", "Candidate clean-input preservation"),
        ("measured_content_delay", "Measured content/availability delay"),
        ("device_timing_and_memory", "Target-device timing and memory"),
        ("listening_or_quality", "Authorized listening or quality assessment"),
        ("release_decision", "Independent exact-head release approval"),
    )
    return [{
        "result_id": result_id,
        "requirement": requirement,
        "value": None,
        "status": "blocked",
        "qualifies": False,
    } for result_id, requirement in items]


def qualification_slots() -> Dict[str, Any]:
    return {
        "candidate_output": {
            "value": None,
            "status": "unavailable_vendor_artifact_and_runtime_absent",
            "qualifies": False,
        },
        "paired_si_sdr_db": {
            "value": None,
            "status": "unavailable_rights_cleared_cohort_absent",
            "qualifies": False,
        },
        "paired_stoi": {
            "value": None,
            "status": "unavailable_approved_scorer_and_cohort_absent",
            "qualifies": False,
        },
        "clean_speech_preservation": {
            "value": None,
            "status": "unavailable_candidate_runtime_absent",
            "qualifies": False,
        },
        "measured_content_delay_samples": {
            "value": None,
            "status": "unavailable_runtime_and_timing_harness_absent",
            "qualifies": False,
        },
        "measured_availability_delay_ms": {
            "value": None,
            "status": "unavailable_runtime_and_timing_harness_absent",
            "qualifies": False,
        },
        "device_timing": {
            "value": None,
            "status": "unavailable_target_device_and_runtime_absent",
            "qualifies": False,
        },
        "memory_and_resources": {
            "value": None,
            "status": "unavailable_runtime_absent",
            "qualifies": False,
        },
        "listening_quality": {
            "value": None,
            "status": "unavailable_panel_authorization_and_assets_absent",
            "qualifies": False,
        },
        "release": {
            "value": None,
            "status": "blocked",
            "qualifies": False,
        },
    }


def failure_controls() -> Dict[str, Any]:
    rejected_audio = sum(
        1 for _, values, _ in _adverse_vectors()
        if _rejects(lambda values=values: validate_audio(values))
    )
    controls = manifest_controls()
    rejected_manifests = sum(1 for row in controls if not row["accepted"])
    valid = parse_manifest(_valid_manifest_document())
    missing_file_rejected = _rejects(
        lambda: verify_manifest_files(valid))
    invalid_geometry_rejected = all((
        _rejects(lambda: validate_geometry(44100, 1, 160, "f32")),
        _rejects(lambda: validate_geometry(16000, 2, 160, "f32")),
        _rejects(lambda: validate_geometry(16000, 1, 320, "f32")),
        _rejects(lambda: validate_geometry(16000, 1, 160, "int16")),
        _rejects(lambda: validate_geometry(True, 1, 160, "f32")),
    ))
    checks = {
        "nan_sample_rejected": _rejects(
            lambda: validate_audio(_with_sample(float("nan")))),
        "infinity_sample_rejected": _rejects(
            lambda: validate_audio(_with_sample(float("inf")))),
        "boolean_sample_rejected": _rejects(
            lambda: validate_audio(_with_sample(True))),
        "string_sample_rejected": _rejects(
            lambda: validate_audio(_with_sample("0.1"))),
        "out_of_range_rejected": _rejects(
            lambda: validate_audio(_with_sample(8.5))),
        "short_frame_rejected": _rejects(
            lambda: validate_audio([0.0] * 159)),
        "long_frame_rejected": _rejects(
            lambda: validate_audio([0.0] * 161)),
        "invalid_geometry_rejected": invalid_geometry_rejected,
        "missing_manifest_field_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("artifact_id", None))),
        "extra_manifest_field_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("extra", 1))),
        "relative_manifest_path_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest("artifact_path", "relative.artifact"))),
        "prefix_mismatch_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest("provider_checksum_prefix", "f" * 12))),
        "unsupported_rate_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("sample_rate_hz", 44100))),
        "stereo_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("channels", 2))),
        "unapproved_terms_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("terms_accepted", False))),
        "missing_manifest_files_rejected": missing_file_rejected,
    }
    return {
        "all_explicit": True,
        "rejected_audio_vectors": rejected_audio,
        "rejected_manifest_documents": rejected_manifests,
        "blocked_release_gates": len(RELEASE_GATES),
        "checks": checks,
        "qualifies": False,
    }


def _rejects(call: Callable[[], Any]) -> bool:
    try:
        call()
    except ReferenceError:
        return True
    return False


def _with_sample(value: Any) -> List[Any]:
    frame: List[Any] = [0.0] * FRAME_SAMPLES
    frame[0] = value
    return frame


def _mutated_manifest(key: str, value: Any) -> Dict[str, Any]:
    document = _valid_manifest_document()
    if value is None:
        document.pop(key, None)
    else:
        document[key] = value
    return document


# ---------------------------------------------------------------------------
# Evidence reporting
# ---------------------------------------------------------------------------

def acceptance_profile() -> Dict[str, Any]:
    items = [
        {
            "item": "identity_and_noisy_control",
            "status": "synthetic_control_only",
            "evidence": "deterministic identity passthrough on synthetic mixture",
            "qualifies": False,
        },
        {
            "item": "established_task_matched_baseline",
            "status": "blocked",
            "evidence": "no approved task-matched baseline or vendor reference",
            "qualifies": False,
        },
        {
            "item": "paired_si_sdr",
            "status": "synthetic_control_only",
            "evidence": "control SI-SDR against the synthetic clean signal only",
            "qualifies": False,
        },
        {
            "item": "paired_stoi",
            "status": "blocked",
            "evidence": "no approved STOI implementation or rights-cleared cohort",
            "qualifies": False,
        },
        {
            "item": "clean_speech_preservation",
            "status": "synthetic_control_only",
            "evidence": "fixed high-pass on synthetic clean signal only",
            "qualifies": False,
        },
        {
            "item": "peaks_and_invalid_outputs",
            "status": "synthetic_control_only",
            "evidence": "control peaks and clipped-sample counts only",
            "qualifies": False,
        },
        {
            "item": "content_and_availability_timing",
            "status": "blocked",
            "evidence": "30 ms is a source-reported claim, not a measurement",
            "qualifies": False,
        },
        {
            "item": "state_memory_and_independent_instances",
            "status": "blocked",
            "evidence": "no vendor runtime or stateful measurement",
            "qualifies": False,
        },
        {
            "item": "rights_cleared_cohort",
            "status": "blocked",
            "evidence": "no cohort, consent or redistribution rights",
            "qualifies": False,
        },
        {
            "item": "listening_or_authorized_quality",
            "status": "blocked",
            "evidence": "no panel, authorization or listening result",
            "qualifies": False,
        },
        {
            "item": "adverse_missing_nonfinite_controls",
            "status": "synthetic_control_only",
            "evidence": "explicit rejection of invalid, nonfinite and blocked cases",
            "qualifies": False,
        },
        {
            "item": "release_and_distribution_terms",
            "status": "blocked",
            "evidence": "proprietary terms, redistribution and output use unapproved",
            "qualifies": False,
        },
    ]
    return {
        "profile": PROFILE,
        "items": items,
        "all_qualify": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def observed_provenance() -> Dict[str, Any]:
    return {
        "documented_context": [
            {
                "claim_id": "candidate_scope",
                "statement": (
                    "Production speech-to-speech enhancement; Quail has a "
                    "single-speaker focus and Rook targets multi-speaker "
                    "listening / broad enhancement."
                ),
                "source": "research/noise_suppression_candidate_census.md:55",
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "artifact_and_rates",
                "statement": (
                    "The official model hub exposes versioned downloadable "
                    "artifacts with checksum prefixes, SDK inference and "
                    "8/16/48 kHz variants."
                ),
                "source": "research/noise_suppression_candidate_census.md:55",
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "latency_claim",
                "statement": "A 30 ms latency is stated for the product family.",
                "source": "research/noise_suppression_candidate_census.md:55",
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "terms_status",
                "statement": (
                    "Proprietary service/model terms require account review."
                ),
                "source": "research/noise_suppression_candidate_census.md:55",
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "discovery_state",
                "statement": (
                    "The discovery record marks eligibility blocked, weights "
                    "located_unverified and benchmark_state not_run."
                ),
                "source": (
                    "research/store/snapshots/"
                    "90d8ef52996098cb779a7acfef2e07a3337f6627da94ef7beab9315f"
                    "6669b2c8.jsonl:251-252"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "baseline_separation",
                "statement": (
                    "Rook is a multi-speaker listening / broad-enhancement "
                    "product comparator and is not a pure noise-only baseline."
                ),
                "source": "research/noise_suppression_candidate_census.md:55",
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
        ],
        "reproduced_here": False,
        "qualifies": False,
    }


def ranking_payload() -> Dict[str, Any]:
    return {
        "order": "not_ranked",
        "recommendation": None,
        "reason": (
            "No licensed artifact, runtime, rights-cleared cohort or "
            "independent score exists; local controls cannot rank the candidate."
        ),
        "qualifies": False,
    }


def build_report_core() -> Dict[str, Any]:
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "qualification": QUALIFICATION,
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "quail_sibling_pins": QUAIL_SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "vendor_record": vendor_record(),
        "declared_contract": declared_contract(),
        "manifest_contract": manifest_contract(),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "fixture": fixture_payload(),
        "controls": controls_payload(),
        "manifest_controls": manifest_controls(),
        "adverse_results": adverse_results(),
        "missing_results": missing_results(),
        "qualification_slots": qualification_slots(),
        "failure_controls": failure_controls(),
        "acceptance_profile": acceptance_profile(),
        "observed_provenance": observed_provenance(),
        "artifact_assessment": artifact_assessment(),
        "ranking": ranking_payload(),
        "release_gates": RELEASE_GATES,
        "non_claims": NON_CLAIMS,
        "reproduction": REPRODUCTION,
    }


def build_report() -> Dict[str, Any]:
    first = build_report_core()
    second = build_report_core()
    third = build_report_core()
    digests = [sha256_bytes(canonical_bytes(item))
               for item in (first, second, third)]
    if len(set(digests)) != 1:
        raise ReferenceError("non_deterministic_report")
    report = dict(first)
    report["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": digests,
        "mode": "three_in_process_canonical_builds_plus_cold_start_verify",
    }
    return report


def render_report() -> Tuple[bytes, str, str]:
    report = build_report()
    text, file_digest = canonical_report(report)
    payload = (text + "\n").encode("utf-8")
    canonical_digest = sha256_bytes(canonical_bytes(report))
    return payload, file_digest, canonical_digest


def _local_artifact_names() -> List[str]:
    names: List[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        names.append(path.relative_to(ROOT).as_posix())
    return names


def contract_payload() -> Dict[str, Any]:
    pins: Dict[str, str] = {}
    for name in _local_artifact_names():
        if name in ("contract.json", "SOURCES.sha256"):
            continue
        pins[name] = digest_file(ROOT / name)
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "qualification": QUALIFICATION,
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "quail_sibling_pins": QUAIL_SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "vendor_record": vendor_record(),
        "declared_contract": declared_contract(),
        "manifest_contract": manifest_contract(),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "release_gates": RELEASE_GATES,
        "artifact_pins": pins,
        "local_files": list(LOCAL_FILES),
        "reproduction": REPRODUCTION,
        "non_claims": NON_CLAIMS,
    }


def inspect_payload() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "qualification": QUALIFICATION,
        "declared_contract": declared_contract(),
        "vendor_record": vendor_record(),
        "required_artifacts": [
            {"id": item["id"], "present": item["present"]}
            for item in REQUIRED_ARTIFACTS
        ],
        "release_gates": [
            {"id": gate["id"], "status": gate["status"],
             "qualifies": gate["qualifies"]}
            for gate in RELEASE_GATES
        ],
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "qualifies": False,
    }
