# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for
SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ.

The exact differentiable-biquad neural parametric EQ candidate is a
literature family only.  This workspace has no reviewed upstream
implementation, immutable revision, checkpoint/weights digest, runtime lock,
training recipe, parameter contract, rights record, frozen oracle or
rights-cleared held-out device/speaker cohort.  This module therefore never
downloads, reads audio, imports a neural runtime, loads weights or executes a
model.

It provides three verifiable, fail-closed pieces:

* a caller-supplied-reference admission schema that validates exact file
  hashes, geometry, gain bounds, device response, splits and oracle records
  without ever executing the candidate;
* a bounded synthetic DSP-profile control based on analytic RBJ peaking
  biquads, a deterministic complex-step gradient check, exact and
  device-response gain recovery, frame/whole equality, reset and rejection
  behaviour;
* explicit adverse controls (clustered bands, extreme gain, out-of-band
  amplification, nonfinite input and gain-limited fitting) that never
  qualify anything.

Every measured value here is a synthetic contract observation.  Nothing in
this package qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import cmath
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ"
TITLE = "Differentiable-biquad neural parametric EQ"
SLUG = "differentiable-biquad-neural-parametric-eq"
COMPONENT = "differentiable-biquad-neural-parametric-eq"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "708b9a4197ed35fd2528fad425832c55ef393eb7"
BRANCH = "swarm/SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ"
REVIEWER = "reviewer-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ")
REPORT_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
ADMISSION_SCHEMA_ID = f"audio-sdk/{COMPONENT}/admission/0.1"
ADMISSION_CONTRACT_ID = (
    f"audio-sdk/{COMPONENT}/caller-supplied-reference/0.1")
PROFILE = "dsp"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62_500

# A source-reported synthetic screen value, not a candidate metric.
SOURCE_REPORTED_INVERSE_EQ_RMSE_DB = 2.577
SOURCE_REPORTED_IDENTITY_RMSE_DB = 4.414

STABLE_TASK_FIELDS = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason",
    "dispatch_priority",
    "handoff",
    "owner",
    "review",
    "status",
)

SOURCE_PINS: Dict[str, str] = {
    "research/level_tone_control_20261028.md":
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/check.py":
        "5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
}
BOUNDARY_PINS: Dict[str, str] = {
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
LOCAL_PIN_PATHS = (
    "README.md",
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

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "candidate_geometry": "unresolved",
    "candidate_sample_rate_hz": None,
    "candidate_hop_samples": None,
    "candidate_biquad_count": None,
    "candidate_gain_limit_db": None,
    "surrogate_sample_rate_hz": SAMPLE_RATE_HZ,
    "surrogate_channels": CHANNELS,
    "surrogate_hop_samples": SDK_FRAME_SAMPLES,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_device_response": False,
    "real_corpus": False,
    "real_weights": False,
    "release_claim": False,
    "runtime_imported": False,
    "task_local_only": True,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No differentiable-biquad neural EQ source, checkpoint, weight, graph or parameter is loaded or executed.",
    "No PyTorch, ONNX Runtime, TensorFlow or other neural runtime is imported.",
    "No network request, download, staging, cloning or asset redistribution occurs.",
    "No real audio, device response, corpus, split or device clock is consumed.",
    "No neural parametric-EQ accuracy, device-recovery quality, latency, RTF or listening result is measured here.",
    "The source-reported synthetic inversion values are provenance only and are not reproduced.",
    "The synthetic RBJ biquad control is a contract control, never model output.",
    "The synthetic frequency holdout is not a real device or speaker split.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

# ---------------------------------------------------------------------------
# Synthetic DSP control constants.
# ---------------------------------------------------------------------------

SURROGATE_LABEL = "synthetic_differentiable_biquad_control_not_candidate"
EXACT_TRUTH = (
    (125.0, 0.9, 4.5),
    (1000.0, 0.9, -3.0),
    (4000.0, 0.9, 2.0),
)
DEVICE_RESPONSE = (
    (100.0, 1.1, 3.0),
    (630.0, 0.8, -4.0),
    (2500.0, 1.3, 2.5),
    (7000.0, 0.9, 1.5),
)
MODEL_BANDS = (
    (125.0, 0.9),
    (1000.0, 0.9),
    (4000.0, 0.9),
)
FIT_PROBES = (62.5, 100.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0)
HELDOUT_PROBES = (5000.0, 6000.0, 7000.0, 7900.0)
ALL_PROBES = FIT_PROBES + HELDOUT_PROBES
GAIN_LIMIT_DB = 6.0
EXACT_ITERS = 320
DEVICE_ITERS = 300
EXACT_LR = 0.6
DEVICE_LR = 0.45
FD_STEP = 1e-5
CS_STEP = 1e-7
LCG_SEED = 0x5EEDB10C


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


# ---------------------------------------------------------------------------
# Strict JSON and canonical encoding.
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(data: bytes) -> str:
    return sha256_bytes(data)


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Reject("non-finite canonical value")
        if value == 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(_normalize_negzero(value), sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("value is not canonical-JSON serializable") from error


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    payload = canonical_bytes(report) + b"\n"
    return payload.decode("utf-8"), sha256_bytes(payload)


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse JSON while rejecting non-finite constants and duplicate keys."""

    def reject(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    try:
        value = json.loads(text, parse_constant=reject,
                           object_pairs_hook=pairs)
    except json.JSONDecodeError as error:
        raise Reject("invalid strict JSON: " + str(error)) from error
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def q(value: float, digits: int = 6) -> float:
    rounded = round(float(value), digits)
    return 0.0 if rounded == 0.0 else rounded


# ---------------------------------------------------------------------------
# Task-row identity: stable linked-row fields only; never the whole file.
# ---------------------------------------------------------------------------

def task_row_identity() -> Dict[str, Any]:
    relative = "audio-benchmark-platform/plan/swarm/TASKS.json"
    path = SOURCE_ROOT / relative
    if not path.is_file():
        raise Reject("task board is unavailable at " + relative)
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("task board unreadable") from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise Reject("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise Reject("linked task row identity mismatch")
    if stable["repository"] != "audio-sdk" or stable["mode"] != "feasibility":
        raise Reject("linked task row repository/mode mismatch")
    if stable["title"] != TITLE:
        raise Reject("linked task row title mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise Reject("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise Reject("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise Reject("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise Reject("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise Reject("claim reviewer mismatch")
    return {
        "source": relative,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Fixed-path artifact audit.  No network, no download, no symlink following.
# ---------------------------------------------------------------------------

AUDIT_PATHS: Tuple[Tuple[str, str], ...] = (
    ("implementation_checkout",
     f"data/checkouts/{COMPONENT}"),
    ("weights_directory", f"data/models/{COMPONENT}"),
    ("runtime_environment", f"data/envs/{COMPONENT}"),
    ("wheel_cache",
     "data/wheels/neural-parametric-eq/differentiable-biquad"),
    ("device_response_cohort", "data/datasets/device-response-eq"),
    ("frozen_run", f"data/runs/{COMPONENT}"),
    ("adapter", f"adapters/{COMPONENT}"),
    ("rights_record", "licensing/third_party/differentiable-biquad-neural-eq"),
)


def _observe_path(relative: str) -> Dict[str, Any]:
    path = SOURCE_ROOT / relative
    observation: Dict[str, Any] = {
        "path": relative,
        "present": path.exists(),
        "kind": None,
        "entries": None,
        "bytes": None,
        "sha256": None,
    }
    if not observation["present"]:
        return observation
    if path.is_symlink():
        observation["kind"] = "symlink"
        return observation
    if path.is_dir():
        observation["kind"] = "directory"
        observation["entries"] = sum(1 for _ in path.iterdir())
        return observation
    if path.is_file():
        observation["kind"] = "file"
        data = path.read_bytes()
        observation["bytes"] = len(data)
        observation["sha256"] = sha256_bytes(data)
    return observation


def audit_assets() -> Dict[str, Any]:
    observations = [dict(_observe_path(relative), id=name)
                    for name, relative in AUDIT_PATHS]
    by_id = {item["id"]: item for item in observations}
    any_present = any(item["present"] for item in observations)
    return {
        "observations": observations,
        "any_present": any_present,
        "implementation_present": by_id["implementation_checkout"]["present"],
        "weights_present": by_id["weights_directory"]["present"],
        "runtime_present": by_id["runtime_environment"]["present"],
        "cohort_present": by_id["device_response_cohort"]["present"],
        "frozen_run_present": by_id["frozen_run"]["present"],
        "rights_present": by_id["rights_record"]["present"],
        "audit_scope": (
            "fixed workspace paths only; no network, no download, no model "
            "load or execution"),
    }


# ---------------------------------------------------------------------------
# Bounded synthetic DSP control: RBJ peaking biquads.
# ---------------------------------------------------------------------------

def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Reject(label + " must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise Reject(label + " must be finite")
    return number


def validate_band(freq_hz: Any, q_value: Any, gain_db: Any,
                  sample_rate_hz: int = SAMPLE_RATE_HZ) -> Tuple[float, float, float]:
    frequency = _finite(freq_hz, "frequency")
    quality = _finite(q_value, "q")
    gain = _finite(gain_db, "gain")
    if sample_rate_hz != SAMPLE_RATE_HZ:
        raise Reject("unsupported sample rate")
    nyquist = sample_rate_hz / 2.0
    if not (0.0 < frequency < nyquist):
        raise Reject("frequency outside (0, Nyquist)")
    if not (0.0 < quality <= 40.0):
        raise Reject("q outside (0, 40]")
    if not (-24.0 <= gain <= 24.0):
        raise Reject("gain outside [-24, 24] dB")
    return frequency, quality, gain


def biquad_coefficients(freq_hz: float, q_value: float, gain_db: float,
                        sample_rate_hz: int = SAMPLE_RATE_HZ,
                        ) -> Tuple[float, float, float, float, float]:
    """Normalized RBJ peaking-EQ coefficients (b0,b1,b2,a1,a2)."""
    frequency, quality, gain = validate_band(
        freq_hz, q_value, gain_db, sample_rate_hz)
    amplitude = 10.0 ** (gain / 40.0)
    omega = 2.0 * math.pi * frequency / sample_rate_hz
    alpha = math.sin(omega) / (2.0 * quality)
    cosine = math.cos(omega)
    b0 = 1.0 + alpha * amplitude
    b1 = -2.0 * cosine
    b2 = 1.0 - alpha * amplitude
    a0 = 1.0 + alpha / amplitude
    a1 = -2.0 * cosine
    a2 = 1.0 - alpha / amplitude
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def complex_coefficients(freq_hz: float, q_value: float, gain_complex: complex,
                         sample_rate_hz: int = SAMPLE_RATE_HZ,
                         ) -> Tuple[complex, complex, complex, complex, complex]:
    """Analytic continuation of the RBJ coefficients in the gain variable."""
    amplitude = cmath.exp(math.log(10.0) * gain_complex / 40.0)
    omega = 2.0 * math.pi * freq_hz / sample_rate_hz
    alpha = math.sin(omega) / (2.0 * q_value)
    cosine = math.cos(omega)
    b0 = 1.0 + alpha * amplitude
    b1 = -2.0 * cosine
    b2 = 1.0 - alpha * amplitude
    a0 = 1.0 + alpha / amplitude
    a1 = -2.0 * cosine
    a2 = 1.0 - alpha / amplitude
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def response_at(freq_hz: float, bands: Sequence[Tuple[float, float, float]],
                sample_rate_hz: int = SAMPLE_RATE_HZ) -> complex:
    if not (0.0 <= freq_hz <= sample_rate_hz / 2.0):
        raise Reject("probe frequency outside [0, Nyquist]")
    z = cmath.exp(-1j * 2.0 * math.pi * freq_hz / sample_rate_hz)
    z2 = z * z
    value = 1.0 + 0.0j
    for frequency, quality, gain in bands:
        b0, b1, b2, a1, a2 = biquad_coefficients(
            frequency, quality, gain, sample_rate_hz)
        value *= (b0 + b1 * z + b2 * z2) / (1.0 + a1 * z + a2 * z2)
    return value


def response_db(freq_hz: float, bands: Sequence[Tuple[float, float, float]],
                sample_rate_hz: int = SAMPLE_RATE_HZ) -> float:
    magnitude = abs(response_at(freq_hz, bands, sample_rate_hz))
    if magnitude <= 0.0 or not math.isfinite(magnitude):
        raise Reject("degenerate response magnitude")
    return 20.0 * math.log10(magnitude)


def filter_samples(samples: Sequence[float],
                   bands: Sequence[Tuple[float, float, float]],
                   state: Optional[Dict[str, float]] = None,
                   sample_rate_hz: int = SAMPLE_RATE_HZ,
                   ) -> Tuple[List[float], Dict[str, float]]:
    """Direct-form-I cascade with explicit per-section state."""
    if not isinstance(samples, (list, tuple)) or not samples:
        raise Reject("samples must be a nonempty sequence")
    coefficients = [biquad_coefficients(*band, sample_rate_hz)
                    for band in bands]
    sections: List[Dict[str, float]] = []
    if state is None:
        sections = [{"x1": 0.0, "x2": 0.0, "y1": 0.0, "y2": 0.0}
                    for _ in coefficients]
    else:
        if not isinstance(state, dict) or set(state) != {"sections"}:
            raise Reject("invalid filter state")
        saved = state.get("sections")
        if not isinstance(saved, list) or len(saved) != len(coefficients):
            raise Reject("filter state shape mismatch")
        for item in saved:
            if not isinstance(item, dict) or set(item) != {"x1", "x2",
                                                           "y1", "y2"}:
                raise Reject("invalid filter section state")
            section = {}
            for key in ("x1", "x2", "y1", "y2"):
                section[key] = _finite(item[key], "state." + key)
            sections.append(section)
    output: List[float] = []
    for sample in samples:
        value = _finite(sample, "sample")
        for section, (b0, b1, b2, a1, a2) in zip(sections, coefficients):
            x1, x2 = section["x1"], section["x2"]
            y1, y2 = section["y1"], section["y2"]
            filtered = b0 * value + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            if not math.isfinite(filtered):
                raise Reject("non-finite filter output")
            section["x2"], section["x1"] = x1, value
            section["y2"], section["y1"] = y1, filtered
            value = filtered
        output.append(value)
    return output, {"sections": sections}


def pole_radius(freq_hz: float, q_value: float, gain_db: float,
                sample_rate_hz: int = SAMPLE_RATE_HZ) -> float:
    _, _, _, a1, a2 = biquad_coefficients(
        freq_hz, q_value, gain_db, sample_rate_hz)
    discriminant = a1 * a1 - 4.0 * a2
    if discriminant >= 0.0:
        root = math.sqrt(discriminant)
        return max(abs((-a1 + root) / 2.0), abs((-a1 - root) / 2.0))
    magnitude = math.sqrt(a2)
    return magnitude


def _filter_db_loss(model_centers: Sequence[Tuple[float, float]],
                    gains: Sequence[float], probes: Sequence[float],
                    target_db: Sequence[float]) -> float:
    bands = [(model_centers[index][0], model_centers[index][1], gains[index])
             for index in range(len(model_centers))]
    return sum((response_db(freq, bands) - target) ** 2
               for freq, target in zip(probes, target_db)) / len(probes)


def _gain_gradient(model_centers: Sequence[Tuple[float, float]],
                   gains: Sequence[float], probes: Sequence[float],
                   target_db: Sequence[float]) -> List[float]:
    """Complex-step derivative of the mean squared dB response loss."""
    bands = [(model_centers[index][0], model_centers[index][1], gains[index])
             for index in range(len(model_centers))]
    gradient: List[float] = []
    for band_index in range(len(model_centers)):
        total = 0.0
        perturbation = [(frequency, quality,
                         gain + (1j * CS_STEP if index == band_index else 0.0))
                        for index, (frequency, quality, gain)
                        in enumerate(bands)]
        for freq, target in zip(probes, target_db):
            base = response_at(freq, bands)
            step = response_at_complex(freq, perturbation)
            derivative = (step - base) / (1j * CS_STEP)
            magnitude_sq = abs(base) ** 2
            if magnitude_sq <= 0.0:
                raise Reject("degenerate gradient response")
            d_db = ((20.0 / math.log(10.0))
                    * (base.conjugate() * derivative).real / magnitude_sq)
            base_db = 20.0 * math.log10(abs(base))
            total += 2.0 * (base_db - target) * d_db
        gradient.append(total / len(probes))
    return gradient


def response_at_complex(freq_hz: float,
                        bands: Sequence[Tuple[float, float, complex]],
                        sample_rate_hz: int = SAMPLE_RATE_HZ) -> complex:
    z = cmath.exp(-1j * 2.0 * math.pi * freq_hz / sample_rate_hz)
    z2 = z * z
    value = 1.0 + 0.0j
    for frequency, quality, gain in bands:
        b0, b1, b2, a1, a2 = complex_coefficients(
            frequency, quality, gain, sample_rate_hz)
        value *= (b0 + b1 * z + b2 * z2) / (1.0 + a1 * z + a2 * z2)
    return value


def _finite_difference_gradient(model_centers: Sequence[Tuple[float, float]],
                                gains: Sequence[float],
                                probes: Sequence[float],
                                target_db: Sequence[float]) -> List[float]:
    gradient: List[float] = []
    for index in range(len(model_centers)):
        up = list(gains)
        down = list(gains)
        up[index] += FD_STEP
        down[index] -= FD_STEP
        gradient.append((_filter_db_loss(model_centers, up, probes, target_db)
                         - _filter_db_loss(model_centers, down, probes, target_db))
                        / (2.0 * FD_STEP))
    return gradient


def _fit(model_centers: Sequence[Tuple[float, float]],
         probes: Sequence[float], target_db: Sequence[float],
         iterations: int, learning_rate: float,
         gain_limit_db: float) -> Dict[str, Any]:
    gains = [0.0 for _ in model_centers]
    initial = _filter_db_loss(model_centers, gains, probes, target_db)
    clamp_events = 0
    for _ in range(iterations):
        gradient = _gain_gradient(model_centers, gains, probes, target_db)
        for index in range(len(gains)):
            candidate = gains[index] - learning_rate * gradient[index]
            bounded = max(-gain_limit_db, min(gain_limit_db, candidate))
            if bounded != candidate:
                clamp_events += 1
            gains[index] = bounded
    final = _filter_db_loss(model_centers, gains, probes, target_db)
    return {
        "gains_db": [q(value) for value in gains],
        "initial_rmse_db": q(math.sqrt(initial)),
        "final_rmse_db": q(math.sqrt(final)),
        "iterations": iterations,
        "learning_rate": learning_rate,
        "gain_limit_db": gain_limit_db,
        "clamp_events": clamp_events,
        "gain_min_db": q(min(gains)),
        "gain_max_db": q(max(gains)),
    }


def _target_db(bands: Sequence[Tuple[float, float, float]],
               probes: Sequence[float]) -> List[float]:
    return [response_db(freq, bands) for freq in probes]


def _rmse(values: Sequence[float], targets: Sequence[float]) -> float:
    return math.sqrt(sum((value - target) ** 2
                         for value, target in zip(values, targets))
                     / len(values))


def _lcg(state: int) -> Tuple[int, int]:
    next_state = (1103515245 * state + 12345) & 0x7FFFFFFF
    return next_state, next_state


def _synthetic_speech(length: int = SAMPLE_RATE_HZ) -> List[float]:
    """Deterministic harmonic/formant-like signal with a syllable envelope."""
    samples: List[float] = []
    state = LCG_SEED
    for index in range(length):
        time = index / SAMPLE_RATE_HZ
        envelope = 0.55 + 0.45 * math.sin(2.0 * math.pi * 3.0 * time) ** 2
        value = 0.0
        for harmonic in range(1, 9):
            value += (1.0 / harmonic) * math.sin(
                2.0 * math.pi * 160.0 * harmonic * time
                + 0.17 * harmonic)
        for center, width, weight in ((520.0, 120.0, 0.35),
                                      (1350.0, 220.0, 0.22),
                                      (2600.0, 350.0, 0.12)):
            value += weight * math.sin(
                2.0 * math.pi * center * time * (1.0 + 0.02 * harmonic))
            value += 0.05 * width / 1000.0 * math.sin(
                2.0 * math.pi * (center + width) * time)
        state, draw = _lcg(state)
        noise = ((draw / 0x7FFFFFFF) * 2.0 - 1.0) * 0.01
        samples.append(0.22 * envelope * value / 3.0 + noise)
    return samples


def _log_sweep(length: int = SAMPLE_RATE_HZ,
               start_hz: float = 50.0,
               end_hz: float = 7800.0) -> List[float]:
    duration = (length - 1) / SAMPLE_RATE_HZ
    ratio = math.log(end_hz / start_hz)
    scale = 2.0 * math.pi * start_hz * duration / ratio
    samples = []
    for index in range(length):
        time = index / SAMPLE_RATE_HZ
        phase = scale * (math.exp(ratio * time / duration) - 1.0)
        samples.append(0.25 * math.sin(phase))
    return samples


def _first_significant(samples: Sequence[float], threshold: float = 1e-9) -> int:
    for index, value in enumerate(samples):
        if abs(value) > threshold:
            return index
    return -1


def _peak(samples: Sequence[float]) -> float:
    return max(abs(value) for value in samples)


def _clipped(samples: Sequence[float]) -> int:
    return sum(1 for value in samples if abs(value) > 1.0)


def dsp_control() -> Dict[str, Any]:
    exact_truth = tuple(EXACT_TRUTH)
    model_centers = tuple(MODEL_BANDS)
    model_bands = tuple((frequency, quality, 0.0)
                        for frequency, quality in model_centers)
    device = tuple(DEVICE_RESPONSE)

    exact_target = _target_db(exact_truth, ALL_PROBES)
    exact = _fit(model_centers, ALL_PROBES, exact_target,
                 EXACT_ITERS, EXACT_LR, 12.0)
    exact_error = max(abs(recovered - truth[2]) for recovered, truth
                      in zip(exact["gains_db"], exact_truth))

    fit_target = _target_db(device, FIT_PROBES)
    heldout_target = _target_db(device, HELDOUT_PROBES)
    device_fit = _fit(model_centers, FIT_PROBES, fit_target,
                      DEVICE_ITERS, DEVICE_LR, GAIN_LIMIT_DB)
    recovered_bands = tuple(
        (model_centers[index][0], model_centers[index][1],
         device_fit["gains_db"][index])
        for index in range(len(model_centers)))
    train_rmse = _rmse([response_db(freq, recovered_bands)
                        for freq in FIT_PROBES], fit_target)
    heldout_rmse = _rmse([response_db(freq, recovered_bands)
                          for freq in HELDOUT_PROBES], heldout_target)

    check_gains = (0.7, -1.2, 0.4)
    check_target = _target_db(exact_truth, ALL_PROBES)
    cs = _gain_gradient(model_centers, check_gains, ALL_PROBES, check_target)
    fd = _finite_difference_gradient(model_centers, check_gains, ALL_PROBES,
                                     check_target)
    gradient_error = max(abs(a - b) for a, b in zip(cs, fd))

    # Time-domain sweep, response and impulse checks.
    sweep = _log_sweep()
    sweep_out, _ = filter_samples(sweep, device)
    sweep_rms_gain = 10.0 * math.log10(
        sum(value * value for value in sweep_out)
        / sum(value * value for value in sweep))
    duration = (len(sweep) - 1) / SAMPLE_RATE_HZ
    ratio = math.log(7800.0 / 50.0)
    predicted_power = 0.0
    for index in range(len(sweep)):
        time = index / SAMPLE_RATE_HZ
        instantaneous = 50.0 * math.exp(ratio * time / duration)
        predicted_power += abs(response_at(instantaneous, device)) ** 2
    predicted_rms_gain = 10.0 * math.log10(predicted_power / len(sweep))

    impulse = [1.0] + [0.0] * (SAMPLE_RATE_HZ - 1)
    impulse_out, _ = filter_samples(impulse, device)
    dft_errors = []
    for freq in ALL_PROBES:
        omega = 2.0 * math.pi * freq / SAMPLE_RATE_HZ
        real = sum(value * math.cos(omega * index)
                   for index, value in enumerate(impulse_out))
        imaginary = -sum(value * math.sin(omega * index)
                         for index, value in enumerate(impulse_out))
        measured = 20.0 * math.log10(math.hypot(real, imaginary))
        analytic = response_db(freq, device)
        dft_errors.append(abs(measured - analytic))

    step = [0.5] * (4 * SAMPLE_RATE_HZ)
    step_out, _ = filter_samples(step, device)
    step_settled = sum(step_out[-320:]) / 320.0
    step_error = abs(20.0 * math.log10(abs(step_settled) / 0.5))

    silence = [0.0] * 1600
    silence_out, _ = filter_samples(silence, device)

    speech = _synthetic_speech()
    speech_out, speech_state = filter_samples(speech, device)
    framewise: List[float] = []
    state = None
    for start in range(0, len(speech), SDK_FRAME_SAMPLES):
        chunk = speech[start:start + SDK_FRAME_SAMPLES]
        chunk_out, state = filter_samples(chunk, device, state)
        framewise.extend(chunk_out)
    framewise_max_diff = max(abs(a - b)
                             for a, b in zip(speech_out, framewise))

    reset_out, _ = filter_samples(impulse, device)
    reset_repeat, _ = filter_samples(impulse, device)
    reset_max_diff = max(abs(a - b)
                         for a, b in zip(reset_out, reset_repeat))

    near_clip = [1.4 * value / max(1e-9, _peak(speech)) for value in speech]
    near_clip_out, _ = filter_samples(near_clip, device)
    near_clip_peak = _peak(near_clip_out)
    near_clip_clipped = _clipped(near_clip_out)

    nonlinear: List[float] = []
    nonlinear_state = None
    for start in range(0, len(speech), SDK_FRAME_SAMPLES):
        chunk, nonlinear_state = filter_samples(
            speech[start:start + SDK_FRAME_SAMPLES], exact_truth,
            nonlinear_state)
        nonlinear.extend(math.tanh(1.5 * value) for value in chunk)
    nonlinear_out, _ = filter_samples(nonlinear, device)
    nonlinear_peak = _peak(nonlinear_out)
    nonlinear_finite = all(math.isfinite(value) for value in nonlinear_out)

    stability = []
    for gain in (-24.0, -12.0, 0.0, 12.0, 24.0):
        radii = [pole_radius(frequency, quality, gain) for frequency, quality
                 in model_centers]
        stability.append({"gain_db": gain, "max_pole_radius": q(max(radii))})

    clustered = ((1000.0, 0.9, 6.0), (1000.0, 0.9, 6.0),
                 (1000.0, 0.9, 6.0))
    clustered_response = response_db(1000.0, clustered)
    clustered_stable = max(pole_radius(*band) for band in clustered) < 1.0
    extreme = ((1000.0, 0.9, 24.0),)
    out_of_band = response_db(7900.0, recovered_bands)

    adverse_fit = _fit(model_centers, FIT_PROBES,
                       [value + 8.0 for value in fit_target],
                       DEVICE_ITERS, DEVICE_LR, 2.0)

    rejection_cases = [
        ("nonfinite_sample", lambda: filter_samples([float("nan")],
                                                    model_bands)),
        ("infinite_sample", lambda: filter_samples([float("inf")],
                                                   model_bands)),
        ("string_sample", lambda: filter_samples(["0.1"], model_bands)),
        ("empty_samples", lambda: filter_samples([], model_bands)),
        ("zero_q", lambda: biquad_coefficients(1000.0, 0.0, 0.0)),
        ("negative_q", lambda: biquad_coefficients(1000.0, -1.0, 0.0)),
        ("zero_frequency", lambda: biquad_coefficients(0.0, 1.0, 0.0)),
        ("nyquist_frequency",
         lambda: biquad_coefficients(8000.0, 1.0, 0.0)),
        ("nan_gain", lambda: biquad_coefficients(1000.0, 1.0, float("nan"))),
        ("infinite_gain",
         lambda: biquad_coefficients(1000.0, 1.0, float("inf"))),
        ("gain_above_limit",
         lambda: biquad_coefficients(1000.0, 1.0, 24.5)),
        ("bad_state", lambda: filter_samples(
            [0.1], model_bands, {"sections": []})),
    ]
    rejections = []
    for name, callback in rejection_cases:
        try:
            callback()
        except Reject as error:
            rejections.append({"case": name, "result": "rejected",
                               "reason": str(error)})
        else:
            rejections.append({"case": name, "result": "accepted"})

    return {
        "label": SURROGATE_LABEL,
        "qualification_effect": "none",
        "candidate_model_executed": False,
        "parameterization": {
            "biquad": "RBJ peaking EQ",
            "coefficients": "b0,b1,b2,a1,a2 normalized by a0",
            "differentiation": "complex-step derivative in band gain (dB)",
            "gradient_check": "central finite difference",
            "delay_samples": 0,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
        },
        "exact_recovery": {
            **exact,
            "truth_gains_db": [truth[2] for truth in exact_truth],
            "max_abs_gain_error_db": q(exact_error),
            "qualifies": False,
        },
        "device_recovery": {
            **device_fit,
            "device_label": "synthetic_four_band_device_response",
            "model_bands": [{"freq_hz": frequency, "q": quality}
                            for frequency, quality in model_centers],
            "fit_probe_frequencies_hz": list(FIT_PROBES),
            "heldout_probe_frequencies_hz": list(HELDOUT_PROBES),
            "train_rmse_db": q(train_rmse),
            "heldout_rmse_db": q(heldout_rmse),
            "split_label": "synthetic_frequency_holdout_not_device_or_speaker_split",
            "qualifies": False,
        },
        "gradient_check": {
            "point_gains_db": list(check_gains),
            "complex_step": CS_STEP,
            "finite_difference_step": FD_STEP,
            "complex_step_gradient": [q(value) for value in cs],
            "finite_difference_gradient": [q(value) for value in fd],
            "max_abs_difference": q(gradient_error, 9),
            "passes": gradient_error < 1e-4,
        },
        "dsp_measurements": {
            "sweep": {
                "length_samples": len(sweep),
                "start_hz": 50.0,
                "end_hz": 7800.0,
                "measured_rms_gain_db": q(sweep_rms_gain),
                "predicted_rms_gain_db": q(predicted_rms_gain),
                "rmse_gain_db": q(abs(sweep_rms_gain - predicted_rms_gain)),
                "peak": q(_peak(sweep_out)),
                "finite": all(math.isfinite(value) for value in sweep_out),
            },
            "step": {
                "length_samples": len(step),
                "settled_output": q(step_settled, 9),
                "expected_output": 0.5,
                "gain_error_db": q(step_error, 9),
            },
            "impulse": {
                "length_samples": len(impulse),
                "first_significant_sample": _first_significant(impulse_out),
                "delay_samples": _first_significant(impulse_out),
                "peak": q(_peak(impulse_out)),
                "max_analytic_dft_error_db": q(max(dft_errors)),
            },
            "silence": {
                "length_samples": len(silence),
                "peak": q(_peak(silence_out)),
                "all_zero": all(value == 0.0 for value in silence_out),
            },
            "clean_speech_surrogate": {
                "length_samples": len(speech),
                "peak": q(_peak(speech_out)),
                "rms_gain_db": q(10.0 * math.log10(
                    sum(value * value for value in speech_out)
                    / sum(value * value for value in speech))),
                "finite": all(math.isfinite(value) for value in speech_out),
            },
            "frame_vs_whole": {
                "frame_samples": SDK_FRAME_SAMPLES,
                "max_abs_difference": q(framewise_max_diff, 12),
                "identical": framewise_max_diff == 0.0,
            },
            "reset": {
                "max_abs_difference": q(reset_max_diff, 12),
                "isolated": reset_max_diff == 0.0,
            },
            "headroom": {
                "near_clip_input_peak": q(_peak(near_clip)),
                "near_clip_output_peak": q(near_clip_peak),
                "near_clip_headroom_db": q(-20.0 * math.log10(near_clip_peak)),
                "near_clip_clipped_samples": near_clip_clipped,
            },
            "nonlinear_interaction": {
                "chain": "peaking_eq -> tanh(1.5x) -> device_eq",
                "peak": q(nonlinear_peak),
                "finite": nonlinear_finite,
                "bounded_by_one": nonlinear_peak <= 1.0,
            },
            "stability": stability,
        },
        "adverse": [
            {
                "id": "clustered_bands",
                "description": "three identical +6 dB peaking bands at 1 kHz",
                "response_db_at_1khz": q(clustered_response),
                "stable": clustered_stable,
                "qualifies": False,
            },
            {
                "id": "extreme_gain",
                "description": "single +24 dB peaking band at 1 kHz",
                "pole_radius": q(pole_radius(*extreme[0])),
                "stable": pole_radius(*extreme[0]) < 1.0,
                "qualifies": False,
            },
            {
                "id": "out_of_band",
                "description": "7.9 kHz response of the fitted model bands",
                "response_db": q(out_of_band),
                "qualifies": False,
            },
            {
                "id": "gain_limited_fit",
                "description": "target needs +8 dB but fit is limited to 2 dB",
                **adverse_fit,
                "qualifies": False,
            },
        ],
        "rejections": {
            "cases": rejections,
            "all_rejected": all(item["result"] == "rejected"
                                for item in rejections),
            "count": len(rejections),
        },
        "gain_limits": {
            "control_limit_db": GAIN_LIMIT_DB,
            "admission_limit_db": 24,
            "enforced": True,
        },
        "controls": {
            "synthetic_control_never_qualifies": True,
            "nonfinite_never_counted_as_valid": True,
            "missing_result_never_qualifies": True,
            "real_device_or_speaker_split_present": False,
            "frame_vs_whole_identical": framewise_max_diff == 0.0,
            "reset_isolated": reset_max_diff == 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Caller-supplied-reference admission schema.
# ---------------------------------------------------------------------------

ADMISSION_FIELDS = (
    "band_count",
    "biquad_count",
    "candidate_id",
    "channels",
    "claims_qualified",
    "controls_passed",
    "corpus_record_path",
    "corpus_record_sha256",
    "deterministic_settings",
    "device_response_path",
    "device_response_sha256",
    "device_split_path",
    "device_split_sha256",
    "frame_samples",
    "frozen_case_count",
    "frozen_oracle_path",
    "frozen_oracle_sha256",
    "gain_limit_db",
    "model_hop_samples",
    "model_parameter_count",
    "nonfinite_count",
    "parameterization",
    "q_max_milli",
    "q_min_milli",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_name",
    "runtime_path",
    "runtime_version",
    "sample_rate_hz",
    "schema_id",
    "source_license",
    "source_revision",
    "speaker_split_path",
    "speaker_split_sha256",
    "weights_bytes",
    "weights_format",
    "weights_path",
    "weights_sha256",
)

ADMISSION_SCHEMA: Dict[str, Any] = {
    "schema_id": ADMISSION_SCHEMA_ID,
    "contract_id": ADMISSION_CONTRACT_ID,
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "executed_in_this_package": False,
    "upstream_identity_verified": False,
    "accepted_manifest_qualifies": False,
    "absent_behavior": "reject_before_processing",
    "synthetic_schema_control_label": "synthetic_schema_control_not_evidence",
    "required_fields": list(ADMISSION_FIELDS),
    "rules": {
        "schema_id": ADMISSION_SCHEMA_ID,
        "candidate_id": COMPONENT,
        "source_revision": "full 40 lowercase hex commit",
        "source_license": "nonempty SPDX-style identifier",
        "weights_format": ["pytorch_state_dict", "safetensors", "onnx"],
        "runtime_name": ["pytorch", "onnxruntime"],
        "runtime_version": "nonempty canonical version token",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "model_hop_samples": "integer 1..160",
        "band_count": "integer 2..32",
        "biquad_count": "equals band_count",
        "parameterization": [
            "peaking_gain_db_cascade",
            "peaking_gain_q_cascade",
            "shelf_peaking_gain_cascade",
        ],
        "gain_limit_db": "number 0 < limit <= 24",
        "q_min_milli": "integer 1..2000",
        "q_max_milli": "integer >= q_min_milli and <= 40000",
        "model_parameter_count": "positive integer",
        "frozen_case_count": ">= 8",
        "nonfinite_count": 0,
        "controls_passed": True,
        "claims_qualified": "must be false; a manifest cannot qualify the candidate",
        "file_checks": (
            "absolute regular files; every declared SHA-256 must match the "
            "actual bytes; weights byte count must match"),
        "split_checks": (
            "device and speaker splits each have disjoint nonempty fit and "
            "held-out ID lists"),
        "oracle_checks": (
            "frozen oracle records 16 kHz mono 160-sample geometry, at least "
            "eight cases, zero nonfinite outputs and an output digest"),
        "rights_checks": (
            "rights and corpus records are present, have a license and never "
            "claim qualification"),
    },
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source revision is a full 40-hex commit and license is recorded",
        "weights, runtime, runtime lock, device response, splits, oracle, "
        "rights and corpus records are absolute present files with matching digests",
        "weights byte count matches the declared value",
        "geometry is 16 kHz mono 160-sample SDK frames with a bounded hop",
        "band and biquad counts, parameterization and gain/Q limits are bounded",
        "device and speaker fit/held-out ID lists are nonempty and disjoint",
        "oracle values are finite, geometry-matched and non-qualifying",
        "no download, copy, import, model load or execution occurs here",
        "schema acceptance never qualifies the candidate",
    ],
}

REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")
LICENSE_PATTERN = re.compile(r"[A-Za-z0-9.+-]{1,64}")
VERSION_PATTERN = re.compile(r"[A-Za-z0-9.+_-]{1,64}")
SHA_PATTERN = re.compile(r"[0-9a-f]{64}")
PARAMETERIZATIONS = ("peaking_gain_db_cascade", "peaking_gain_q_cascade",
                     "shelf_peaking_gain_cascade")
WEIGHTS_FORMATS = ("pytorch_state_dict", "safetensors", "onnx")
RUNTIME_NAMES = ("pytorch", "onnxruntime")


def _absolute_file(root: Dict[str, Any], field: str) -> Path:
    raw = root.get(field)
    if not isinstance(raw, str) or not raw:
        raise Reject(field + " must be a nonempty path")
    path = Path(raw)
    if not path.is_absolute():
        raise Reject(field + " must be absolute")
    if not path.is_file():
        raise Reject(field + " is not a regular file")
    if path.is_symlink():
        raise Reject(field + " must not be a symlink")
    return path


def _file_digest(root: Dict[str, Any], path_field: str,
                 digest_field: str) -> Tuple[Path, str]:
    path = _absolute_file(root, path_field)
    declared = root.get(digest_field)
    if not isinstance(declared, str) or not SHA_PATTERN.fullmatch(declared):
        raise Reject(digest_field + " must be a lowercase SHA-256")
    actual = sha256_bytes(path.read_bytes())
    if actual != declared:
        raise Reject(digest_field + " does not match the file")
    return path, actual


def _json_file(path: Path, label: str) -> Dict[str, Any]:
    value = strict_loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Reject(label + " must be an object")
    return value


def _int(root: Dict[str, Any], field: str, low: int, high: int) -> int:
    value = root.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(field + " must be an integer")
    if not (low <= value <= high):
        raise Reject(field + " outside range")
    return value


def _record_nonqualifying(record: Dict[str, Any], label: str) -> None:
    if record.get("claims_qualified") is True:
        raise Reject(label + " record claims qualification")


def _split_ids(record: Dict[str, Any], label: str) -> Tuple[set, set]:
    fit = record.get("fit")
    held_out = record.get("held_out")
    for name, values in (("fit", fit), ("held_out", held_out)):
        if (not isinstance(values, list) or not values
                or not all(isinstance(item, str) and item for item in values)):
            raise Reject(f"{label} {name} must be a nonempty string list")
        if len(set(values)) != len(values):
            raise Reject(f"{label} {name} contains duplicates")
    fit_set, held_set = set(fit), set(held_out)
    if fit_set & held_set:
        raise Reject(label + " fit and held-out IDs overlap")
    return fit_set, held_set


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("manifest must be an object")
    if set(manifest) != set(ADMISSION_FIELDS):
        missing = sorted(set(ADMISSION_FIELDS) - set(manifest))
        extra = sorted(set(manifest) - set(ADMISSION_FIELDS))
        raise Reject(f"manifest field set mismatch missing={missing} extra={extra}")
    for key, value in manifest.items():
        if isinstance(value, float) and not math.isfinite(value):
            raise Reject(key + " must be finite")

    if manifest["schema_id"] != ADMISSION_SCHEMA_ID:
        raise Reject("schema_id mismatch")
    if manifest["candidate_id"] != COMPONENT:
        raise Reject("candidate_id mismatch")
    if (not isinstance(manifest["source_revision"], str)
            or not REVISION_PATTERN.fullmatch(manifest["source_revision"])):
        raise Reject("source_revision must be a full 40-hex commit")
    if (not isinstance(manifest["source_license"], str)
            or not LICENSE_PATTERN.fullmatch(manifest["source_license"])):
        raise Reject("source_license must be an SPDX-style token")
    if manifest["claims_qualified"] is not False:
        raise Reject("claims_qualified must be false")
    if manifest["controls_passed"] is not True:
        raise Reject("controls_passed must be true")
    if manifest["nonfinite_count"] != 0:
        raise Reject("nonfinite_count must be zero")
    if (not isinstance(manifest["deterministic_settings"], str)
            or not manifest["deterministic_settings"].strip()):
        raise Reject("deterministic_settings must be nonempty")

    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise Reject("sample_rate_hz must be 16000")
    if manifest["channels"] != CHANNELS:
        raise Reject("channels must be 1")
    if manifest["frame_samples"] != SDK_FRAME_SAMPLES:
        raise Reject("frame_samples must be 160")
    _int(manifest, "model_hop_samples", 1, SDK_FRAME_SAMPLES)
    band_count = _int(manifest, "band_count", 2, 32)
    if manifest["biquad_count"] != band_count:
        raise Reject("biquad_count must equal band_count")
    if manifest["parameterization"] not in PARAMETERIZATIONS:
        raise Reject("unsupported parameterization")
    limit = _finite(manifest["gain_limit_db"], "gain_limit_db")
    if not (0.0 < limit <= 24.0):
        raise Reject("gain_limit_db outside (0, 24]")
    q_min = _int(manifest, "q_min_milli", 1, 2000)
    q_max = _int(manifest, "q_max_milli", q_min, 40000)
    if q_max < q_min:
        raise Reject("q_max_milli below q_min_milli")
    _int(manifest, "model_parameter_count", 1, 1_000_000_000)
    cases = _int(manifest, "frozen_case_count", 8, 10_000_000)

    weights_path, _ = _file_digest(manifest, "weights_path", "weights_sha256")
    weights_bytes = _int(manifest, "weights_bytes", 1, 1_000_000_000)
    if weights_bytes != weights_path.stat().st_size:
        raise Reject("weights_bytes does not match the file size")
    if manifest["weights_format"] not in WEIGHTS_FORMATS:
        raise Reject("unsupported weights_format")
    if manifest["runtime_name"] not in RUNTIME_NAMES:
        raise Reject("unsupported runtime_name")
    if (not isinstance(manifest["runtime_version"], str)
            or not VERSION_PATTERN.fullmatch(manifest["runtime_version"])):
        raise Reject("runtime_version must be a canonical token")
    _absolute_file(manifest, "runtime_path")
    _, _ = _file_digest(manifest, "runtime_lock_path", "runtime_lock_sha256")

    device_response_path, _ = _file_digest(
        manifest, "device_response_path", "device_response_sha256")
    device_response = _json_file(device_response_path, "device response")
    _record_nonqualifying(device_response, "device response")
    if device_response.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise Reject("device response sample rate mismatch")
    frequencies = device_response.get("probe_frequencies_hz")
    response = device_response.get("response_db")
    if (not isinstance(frequencies, list) or len(frequencies) < 4
            or not all(isinstance(item, (int, float))
                       and not isinstance(item, bool)
                       and math.isfinite(float(item))
                       and 0.0 < float(item) < SAMPLE_RATE_HZ / 2.0
                       for item in frequencies)):
        raise Reject("device response probe frequencies invalid")
    if [float(item) for item in frequencies] != sorted(
            float(item) for item in frequencies):
        raise Reject("device response probe frequencies are not increasing")
    if (not isinstance(response, list) or len(response) != len(frequencies)
            or not all(isinstance(item, (int, float))
                       and not isinstance(item, bool)
                       and math.isfinite(float(item))
                       for item in response)):
        raise Reject("device response values invalid")
    if not isinstance(device_response.get("device_id"), str):
        raise Reject("device response device_id missing")

    device_path, _ = _file_digest(
        manifest, "device_split_path", "device_split_sha256")
    speaker_path, _ = _file_digest(
        manifest, "speaker_split_path", "speaker_split_sha256")
    device_split = _json_file(device_path, "device split")
    speaker_split = _json_file(speaker_path, "speaker split")
    _record_nonqualifying(device_split, "device split")
    _record_nonqualifying(speaker_split, "speaker split")
    device_fit, device_held = _split_ids(device_split, "device split")
    speaker_fit, speaker_held = _split_ids(speaker_split, "speaker split")
    if device_fit & speaker_fit or device_fit & speaker_held:
        raise Reject("device and speaker groups are not independent")
    if device_held & speaker_fit or device_held & speaker_held:
        raise Reject("device and speaker groups are not independent")
    if device_response.get("device_id") not in (device_fit | device_held):
        raise Reject("device response device_id is not in a device split")

    oracle_path, _ = _file_digest(
        manifest, "frozen_oracle_path", "frozen_oracle_sha256")
    oracle = _json_file(oracle_path, "frozen oracle")
    _record_nonqualifying(oracle, "frozen oracle")
    if oracle.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise Reject("oracle sample rate mismatch")
    if oracle.get("channels") != CHANNELS:
        raise Reject("oracle channel mismatch")
    if oracle.get("frame_samples") != SDK_FRAME_SAMPLES:
        raise Reject("oracle frame mismatch")
    if oracle.get("case_count") != cases:
        raise Reject("oracle case count mismatch")
    if oracle.get("nonfinite_count") != 0:
        raise Reject("oracle nonfinite count is not zero")
    if oracle.get("executed") is not True:
        raise Reject("oracle is not marked executed")
    if (not isinstance(oracle.get("output_sha256"), str)
            or not SHA_PATTERN.fullmatch(oracle["output_sha256"])):
        raise Reject("oracle output digest invalid")
    if oracle.get("claims_qualified") is True:
        raise Reject("oracle claims qualification")

    rights_path, _ = _file_digest(
        manifest, "rights_record_path", "rights_record_sha256")
    rights = _json_file(rights_path, "rights record")
    _record_nonqualifying(rights, "rights record")
    if (not isinstance(rights.get("spdx_license"), str)
            or not LICENSE_PATTERN.fullmatch(rights["spdx_license"])):
        raise Reject("rights record license invalid")

    corpus_path, _ = _file_digest(
        manifest, "corpus_record_path", "corpus_record_sha256")
    corpus = _json_file(corpus_path, "corpus record")
    _record_nonqualifying(corpus, "corpus record")
    if corpus.get("frozen_case_count") != cases:
        raise Reject("corpus case count mismatch")
    if corpus.get("nonfinite_count") != 0:
        raise Reject("corpus nonfinite count is not zero")
    if sorted(corpus.get("device_ids", [])) != sorted(device_fit | device_held):
        raise Reject("corpus device IDs do not match the device split")
    if sorted(corpus.get("speaker_ids", [])) != sorted(speaker_fit | speaker_held):
        raise Reject("corpus speaker IDs do not match the speaker split")

    return {
        "accepted": True,
        "qualifies": False,
        "candidate_id": COMPONENT,
        "files_checked": 8,
        "weights_sha256": manifest["weights_sha256"],
        "source_revision": manifest["source_revision"],
    }


# ---------------------------------------------------------------------------
# Admission schema positive and adverse controls.
# ---------------------------------------------------------------------------

def _synthetic_admission_tree(root: Path) -> Dict[str, Any]:
    files = {
        "weights.bin": bytes(range(64)) * 2,
        "runtime.lock": b'{"runtime":"pytorch","version":"2.4.0"}\n',
        "device_response.json": canonical_bytes({
            "device_id": "synthetic-device-a",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "probe_frequencies_hz": [100.0, 1000.0, 4000.0, 7900.0],
            "response_db": [1.0, -2.0, 1.5, 0.5],
            "claims_qualified": False,
        }) + b"\n",
        "device_split.json": canonical_bytes({
            "fit": ["synthetic-device-a"],
            "held_out": ["synthetic-device-b"],
            "claims_qualified": False,
        }) + b"\n",
        "speaker_split.json": canonical_bytes({
            "fit": ["synthetic-speaker-a"],
            "held_out": ["synthetic-speaker-b"],
            "claims_qualified": False,
        }) + b"\n",
        "frozen_oracle.json": canonical_bytes({
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
            "case_count": 8,
            "nonfinite_count": 0,
            "executed": True,
            "output_sha256": "0" * 64,
            "claims_qualified": False,
        }) + b"\n",
        "rights_record.json": canonical_bytes({
            "spdx_license": "Apache-2.0",
            "claims_qualified": False,
        }) + b"\n",
        "corpus_record.json": canonical_bytes({
            "frozen_case_count": 8,
            "nonfinite_count": 0,
            "device_ids": ["synthetic-device-a", "synthetic-device-b"],
            "speaker_ids": ["synthetic-speaker-a", "synthetic-speaker-b"],
            "claims_qualified": False,
        }) + b"\n",
    }
    for name, data in files.items():
        (root / name).write_bytes(data)
    manifest: Dict[str, Any] = {
        "schema_id": ADMISSION_SCHEMA_ID,
        "candidate_id": COMPONENT,
        "source_revision": "0" * 40,
        "source_license": "Apache-2.0",
        "weights_path": str(root / "weights.bin"),
        "weights_sha256": sha256_bytes(files["weights.bin"]),
        "weights_bytes": len(files["weights.bin"]),
        "weights_format": "pytorch_state_dict",
        "model_parameter_count": 1024,
        "band_count": 4,
        "biquad_count": 4,
        "parameterization": "peaking_gain_db_cascade",
        "gain_limit_db": 12.0,
        "q_min_milli": 100,
        "q_max_milli": 4000,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "model_hop_samples": 160,
        "runtime_name": "pytorch",
        "runtime_version": "2.4.0",
        "runtime_path": str(root / "runtime.lock"),
        "runtime_lock_path": str(root / "runtime.lock"),
        "runtime_lock_sha256": sha256_bytes(files["runtime.lock"]),
        "device_response_path": str(root / "device_response.json"),
        "device_response_sha256": sha256_bytes(files["device_response.json"]),
        "device_split_path": str(root / "device_split.json"),
        "device_split_sha256": sha256_bytes(files["device_split.json"]),
        "speaker_split_path": str(root / "speaker_split.json"),
        "speaker_split_sha256": sha256_bytes(files["speaker_split.json"]),
        "frozen_oracle_path": str(root / "frozen_oracle.json"),
        "frozen_oracle_sha256": sha256_bytes(files["frozen_oracle.json"]),
        "rights_record_path": str(root / "rights_record.json"),
        "rights_record_sha256": sha256_bytes(files["rights_record.json"]),
        "corpus_record_path": str(root / "corpus_record.json"),
        "corpus_record_sha256": sha256_bytes(files["corpus_record.json"]),
        "frozen_case_count": 8,
        "nonfinite_count": 0,
        "controls_passed": True,
        "claims_qualified": False,
        "deterministic_settings": "torch.use_deterministic_algorithms(True); seed=0",
    }
    return manifest


def _write_named(root: Path, name: str, value: Any) -> Dict[str, Any]:
    path = root / name
    path.write_bytes(canonical_bytes(value) + b"\n")
    return {"path": str(path), "sha256": sha256_bytes(path.read_bytes())}


def _adverse_manifest_operations() -> List[Tuple[str, Any]]:
    operations: List[Tuple[str, Any]] = []

    def add(name: str, mutator: Any) -> None:
        operations.append((name, mutator))

    add("missing_schema_id", lambda root, item: item.pop("schema_id"))
    add("extra_field", lambda root, item: item.update(extra="x"))
    add("wrong_schema_id", lambda root, item: item.update(schema_id="wrong"))
    add("wrong_candidate_id",
        lambda root, item: item.update(candidate_id="other"))
    add("short_source_revision",
        lambda root, item: item.update(source_revision="abc"))
    add("uppercase_source_revision",
        lambda root, item: item.update(source_revision="A" * 40))
    add("nonhex_source_revision",
        lambda root, item: item.update(source_revision="g" * 40))
    add("empty_source_license",
        lambda root, item: item.update(source_license=""))
    add("relative_weights_path",
        lambda root, item: item.update(weights_path="weights.bin"))
    add("missing_weights_file",
        lambda root, item: item.update(weights_path=str(root / "absent.bin")))
    add("bad_weights_digest_format",
        lambda root, item: item.update(weights_sha256="xyz"))
    add("wrong_weights_digest",
        lambda root, item: item.update(weights_sha256="0" * 64))
    add("zero_weights_bytes", lambda root, item: item.update(weights_bytes=0))
    add("wrong_weights_bytes", lambda root, item: item.update(weights_bytes=1))
    add("bad_weights_format",
        lambda root, item: item.update(weights_format="pickle"))
    add("bad_runtime_name",
        lambda root, item: item.update(runtime_name="tensorflow"))
    add("empty_runtime_version",
        lambda root, item: item.update(runtime_version=""))
    add("missing_runtime_file",
        lambda root, item: item.update(
            runtime_path=str(root / "absent-runtime")))
    add("missing_lock_file",
        lambda root, item: item.update(
            runtime_lock_path=str(root / "absent.lock")))
    add("wrong_lock_digest",
        lambda root, item: item.update(runtime_lock_sha256="0" * 64))
    add("empty_deterministic_settings",
        lambda root, item: item.update(deterministic_settings=""))
    add("stereo", lambda root, item: item.update(channels=2))
    add("wrong_sample_rate",
        lambda root, item: item.update(sample_rate_hz=8000))
    add("wrong_frame_samples",
        lambda root, item: item.update(frame_samples=128))
    add("zero_hop", lambda root, item: item.update(model_hop_samples=0))
    add("hop_too_large",
        lambda root, item: item.update(model_hop_samples=161))
    add("too_few_bands", lambda root, item: item.update(band_count=1))
    add("too_many_bands", lambda root, item: item.update(band_count=33))
    add("biquad_count_mismatch",
        lambda root, item: item.update(biquad_count=5))
    add("bad_parameterization",
        lambda root, item: item.update(parameterization="freeform"))
    add("zero_gain_limit",
        lambda root, item: item.update(gain_limit_db=0))
    add("gain_limit_too_large",
        lambda root, item: item.update(gain_limit_db=25))
    add("zero_q_min", lambda root, item: item.update(q_min_milli=0))
    add("q_max_below_min", lambda root, item: item.update(q_max_milli=1))
    add("zero_parameters",
        lambda root, item: item.update(model_parameter_count=0))
    add("too_few_cases",
        lambda root, item: item.update(frozen_case_count=7))
    add("nonfinite_count_nonzero",
        lambda root, item: item.update(nonfinite_count=1))
    add("controls_not_passed",
        lambda root, item: item.update(controls_passed=False))
    add("claims_qualified",
        lambda root, item: item.update(claims_qualified=True))
    add("device_response_missing",
        lambda root, item: item.update(
            device_response_path=str(root / "absent.json")))
    add("device_response_wrong_digest",
        lambda root, item: item.update(device_response_sha256="0" * 64))
    add("device_response_claims_qualified",
        lambda root, item: _mutate_json(
            root, item, "device_response_path", "device_response_sha256",
            {"claims_qualified": True}))
    add("device_response_nonfinite",
        lambda root, item: _mutate_json(
            root, item, "device_response_path", "device_response_sha256",
            {"response_db": [1.0, float("nan"), 1.0, 1.0]}))
    add("device_response_length_mismatch",
        lambda root, item: _mutate_json(
            root, item, "device_response_path", "device_response_sha256",
            {"response_db": [1.0, 2.0]}))
    add("device_split_overlap",
        lambda root, item: _mutate_json(
            root, item, "device_split_path", "device_split_sha256",
            {"fit": ["same"], "held_out": ["same"]}))
    add("device_split_empty_heldout",
        lambda root, item: _mutate_json(
            root, item, "device_split_path", "device_split_sha256",
            {"held_out": []}))
    add("speaker_split_overlap",
        lambda root, item: _mutate_json(
            root, item, "speaker_split_path", "speaker_split_sha256",
            {"fit": ["same"], "held_out": ["same"]}))
    add("oracle_wrong_sample_rate",
        lambda root, item: _mutate_json(
            root, item, "frozen_oracle_path", "frozen_oracle_sha256",
            {"sample_rate_hz": 8000}))
    add("oracle_too_few_cases",
        lambda root, item: _mutate_json(
            root, item, "frozen_oracle_path", "frozen_oracle_sha256",
            {"case_count": 7}))
    add("oracle_bad_digest",
        lambda root, item: _mutate_json(
            root, item, "frozen_oracle_path", "frozen_oracle_sha256",
            {"output_sha256": "short"}))
    add("oracle_not_executed",
        lambda root, item: _mutate_json(
            root, item, "frozen_oracle_path", "frozen_oracle_sha256",
            {"executed": False}))
    add("rights_missing",
        lambda root, item: item.update(
            rights_record_path=str(root / "absent.json")))
    add("rights_claims_qualified",
        lambda root, item: _mutate_json(
            root, item, "rights_record_path", "rights_record_sha256",
            {"claims_qualified": True}))
    add("corpus_missing",
        lambda root, item: item.update(
            corpus_record_path=str(root / "absent.json")))
    add("corpus_wrong_case_count",
        lambda root, item: _mutate_json(
            root, item, "corpus_record_path", "corpus_record_sha256",
            {"frozen_case_count": 9}))
    add("corpus_claims_qualified",
        lambda root, item: _mutate_json(
            root, item, "corpus_record_path", "corpus_record_sha256",
            {"claims_qualified": True}))
    add("corpus_device_ids_mismatch",
        lambda root, item: _mutate_json(
            root, item, "corpus_record_path", "corpus_record_sha256",
            {"device_ids": ["synthetic-device-a"]}))
    add("frozen_oracle_missing",
        lambda root, item: item.update(
            frozen_oracle_path=str(root / "absent.json")))
    add("split_missing",
        lambda root, item: item.update(
            device_split_path=str(root / "absent.json")))
    add("weights_file_empty",
        lambda root, item: _empty_file(root, item, "weights.bin"))
    return operations


def _mutate_json(root: Path, manifest: Dict[str, Any], path_field: str,
                 digest_field: str, patch: Dict[str, Any]) -> None:
    path = Path(manifest[path_field])
    value = strict_loads(path.read_text(encoding="utf-8"))
    value.update(patch)
    # allow_nan only for the deliberately nonfinite adverse case; the strict
    # loader rejects it before validation.
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=True)
    path.write_bytes(text.encode("utf-8") + b"\n")
    manifest[digest_field] = sha256_bytes(path.read_bytes())


def _empty_file(root: Path, manifest: Dict[str, Any], name: str) -> None:
    path = root / name
    path.write_bytes(b"")
    manifest["weights_sha256"] = sha256_bytes(b"")
    manifest["weights_bytes"] = 1


def run_admission_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="dbq-admission-") as directory:
        root = Path(directory)
        manifest = _synthetic_admission_tree(root)
        accepted = validate_manifest(manifest)
        adverse = []
        for name, mutate in _adverse_manifest_operations():
            # Recreate the pristine tree for each mutation because some
            # cases rewrite shared JSON files.
            for path in root.iterdir():
                if path.is_file():
                    path.unlink()
            manifest = _synthetic_admission_tree(root)
            candidate = json.loads(json.dumps(manifest))
            try:
                mutate(root, candidate)
                validate_manifest(candidate)
            except Reject as error:
                adverse.append({"id": name, "result": "rejected",
                                "reason": str(error)})
            else:
                adverse.append({"id": name, "result": "accepted"})

    strict_cases = []
    bad_documents = [
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("non_object_root", '[1,2,3]'),
        ("empty_text", ""),
    ]
    for name, text in bad_documents:
        try:
            strict_loads(text)
        except Reject as error:
            strict_cases.append({"case": name, "result": "rejected",
                                 "reason": str(error)})
        else:
            strict_cases.append({"case": name, "result": "accepted"})

    return {
        "positive_control": {
            "accepted": accepted["accepted"],
            "qualifies": accepted["qualifies"],
            "label": "synthetic_schema_control_not_evidence",
            "executed": False,
            "upstream_identity_verified": False,
            "files_checked": accepted["files_checked"],
        },
        "adverse": adverse,
        "adverse_count": len(adverse),
        "adverse_all_rejected": all(item["result"] == "rejected"
                                    for item in adverse),
        "strict_json": strict_cases,
        "strict_json_all_rejected": all(item["result"] == "rejected"
                                        for item in strict_cases),
    }


# ---------------------------------------------------------------------------
# Static report material.
# ---------------------------------------------------------------------------

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("RG-01",
     "Exact differentiable-biquad neural parametric-EQ source revision, "
     "checkpoint digest, byte count, weight format, parameter count and "
     "biquad tensor schema are pinned to immutable artifacts."),
    ("RG-02",
     "An isolated hash-pinned runtime reproduces an approved exact-runtime "
     "gain/response vector on frozen device response and PCM, including "
     "fresh-session reset, deterministic gradients and nonfinite rejection."),
    ("RG-03",
     "Code, weight, training-data, runtime-dependency, device-response, "
     "corpus, redistribution, derivative-output and product-use rights are "
     "cleared with complete notices."),
    ("RG-04",
     "The parameterization, band count, frequency/Q/gain bounds, hop, "
     "update cadence, device-response definition and gain limits are "
     "documented; the network output is never presented as a stable filter "
     "without coefficient validation."),
    ("RG-05",
     "A rights-cleared held-out device and speaker split recovers a frozen "
     "known device response before real speech and is scored for response "
     "error, gain-limit violation, speech preservation and peaks."),
    ("RG-06",
     "Streaming state, independent sessions, reset, exact sample intervals, "
     "coefficient updates, frame/whole equivalence and nonfinite output are "
     "verified at the exact runtime."),
    ("RG-07",
     "Target-device pacing, inference-plus-filter availability delay, "
     "deadline misses, memory and finite drain are measured on the intended "
     "workload with controls."),
    ("RG-08",
     "Explicit opt-in provider intake, descriptor/license review, resource "
     "bounds and independent exact-head release or default-selection "
     "approval are complete; the package remains off by default."),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "no_reviewed_implementation_or_revision",
        "gate_id": "RG-01",
        "requirement": (
            "Provide a reviewed runnable differentiable-biquad neural "
            "parametric-EQ implementation and a full 40-hex immutable "
            "source revision."),
        "state": (
            "The pinned research note names the DAFx 2020 and DAFx 2025 "
            "neural parametric-EQ families as literature, not a runnable "
            "implementation; no repository, commit, release or parameter "
            "layout exists in the workspace."),
    },
    {
        "id": "no_checkpoint_or_weights",
        "gate_id": "RG-01",
        "requirement": (
            "Provide the exact inference checkpoint with SHA-256, byte "
            "count, weight format, parameter count and biquad tensor schema."),
        "state": (
            "No differentiable-biquad checkpoint, weight file, tensor "
            "archive, parameter count or digest exists at any fixed "
            "workspace path; no placeholder is accepted as the pinned "
            "artifact."),
    },
    {
        "id": "no_runtime_lock",
        "gate_id": "RG-02",
        "requirement": (
            "Provide an isolated hash-pinned neural runtime, Python version, "
            "wheel hashes, platform and deterministic settings."),
        "state": (
            "No runtime environment or lock exists, and no neural runtime "
            "is imported by this package."),
    },
    {
        "id": "no_rights_record",
        "gate_id": "RG-03",
        "requirement": (
            "Clear code, weight, training-data, device-response, corpus, "
            "redistribution, derivative-output and product-use rights with "
            "complete notices."),
        "state": (
            "No candidate license, model card, per-weight terms, "
            "training-data statement or product-use decision is staged."),
    },
    {
        "id": "no_geometry_parameterization_or_gain_contract",
        "gate_id": "RG-04",
        "requirement": (
            "Document the parameterization, band count, frequency/Q/gain "
            "bounds, hop, update cadence, device-response definition and "
            "gain limits."),
        "state": (
            "The research note describes a learned EQ-parameter family but "
            "records no candidate geometry, coefficient contract, gain limit "
            "or update cadence; this package fixes only its own synthetic "
            "RBJ control."),
    },
    {
        "id": "no_frozen_oracle_or_parity",
        "gate_id": "RG-02",
        "requirement": (
            "Freeze caller-supplied device response and PCM, predicted "
            "parameters, filtered output and digests and reproduce them "
            "byte-for-byte on the exact runtime."),
        "state": (
            "No candidate parameter vector, filtered oracle, fresh-session "
            "trace or exact-runtime parity record exists."),
    },
    {
        "id": "no_rights_cleared_device_speaker_split",
        "gate_id": "RG-05",
        "requirement": (
            "Freeze a rights-cleared held-out device and speaker split with "
            "a known device response and paired clean speech, and score gain "
            "limits, response recovery, preservation and peaks."),
        "state": (
            "No real device response or rights-cleared corpus exists; the "
            "control uses a synthetic frequency holdout, not a device or "
            "speaker split."),
    },
    {
        "id": "no_target_timing_or_provider_intake",
        "gate_id": "RG-07",
        "requirement": (
            "Measure target-device pacing, availability, resources and "
            "finite drain, then complete opt-in provider intake, descriptor "
            "review and independent exact-head release approval."),
        "state": (
            "No device timing, availability, resource or drain measurement "
            "exists, and no provider intake or independent release review "
            "has occurred."),
    },
)

CANDIDATE_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "upstream_source_and_revision",
        "kind": "source",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-01"],
        "observed": (
            "Only literature-family mentions in the pinned research note; "
            "no repository, commit, release or parameter layout."),
        "requirement": (
            "Supply the exact reviewed implementation repository, a full "
            "40-hex immutable commit, the build/training recipe and the "
            "architecture/parameter layout."),
    },
    {
        "id": "checkpoint_weights_identity",
        "kind": "weights",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-01"],
        "observed": (
            "No checkpoint, weight file, tensor archive, parameter count or "
            "digest exists at any fixed workspace path."),
        "requirement": (
            "Supply the exact inference checkpoint as a caller-owned file "
            "with SHA-256, byte count, weight format, parameter count and "
            "tensor schema."),
    },
    {
        "id": "pinned_runtime",
        "kind": "runtime",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-02"],
        "observed": (
            "No runtime environment, lock file, wheel hash or platform "
            "record exists; no neural runtime is imported here."),
        "requirement": (
            "Supply an isolated hash-pinned neural runtime with exact name, "
            "version, Python version, wheel hashes, platform, deterministic "
            "settings and offline execution."),
    },
    {
        "id": "artifact_and_training_rights",
        "kind": "rights",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-03"],
        "observed": (
            "No license, model card, per-weight terms, training-data "
            "statement, notice bundle or product-use decision is staged."),
        "requirement": (
            "Clear upstream code, weight, training-data, device-response, "
            "corpus, redistribution, derivative-output and product-use "
            "rights with complete license and notice records."),
    },
    {
        "id": "parameterization_and_inference_contract",
        "kind": "contract",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-04"],
        "observed": (
            "The note records a learned EQ-parameter family but no band "
            "count, frequency/Q/gain bounds, hop, coefficient update cadence, "
            "device-response definition or gain limit."),
        "requirement": (
            "Document the parameterization, band count, frequency/Q/gain "
            "bounds, hop, update cadence, coefficient stability check, "
            "device-response definition and gain limits, and separate the "
            "network prediction from the validated biquad filter."),
    },
    {
        "id": "frozen_reference_oracle",
        "kind": "oracle",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-02", "RG-06"],
        "observed": (
            "No candidate parameter vector, filtered output, fresh-session "
            "trace or exact-runtime parity record exists."),
        "requirement": (
            "Freeze caller-supplied device response and PCM, predicted "
            "parameters, filtered output and digests for the exact runtime, "
            "with nonfinite count zero and byte-level reproduction."),
    },
    {
        "id": "rights_cleared_device_and_speaker_split",
        "kind": "corpus",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-05"],
        "observed": (
            "No real device response or rights-cleared held-out corpus "
            "exists; the control uses a synthetic frequency holdout."),
        "requirement": (
            "Freeze a rights-cleared known device response and a held-out "
            "device and speaker split with clean speech, gain-limit cases, "
            "response probes, peaks and paired controls."),
    },
    {
        "id": "target_timing_and_provider_intake",
        "kind": "timing_and_intake",
        "required": True,
        "state": "absent",
        "gate_ids": ["RG-07", "RG-08"],
        "observed": (
            "No device timing, availability, resource or drain measurement "
            "exists, and no provider intake or independent release review "
            "has occurred."),
        "requirement": (
            "Measure target-device pacing, availability, resources and "
            "finite drain for the exact runtime, then complete opt-in "
            "provider intake, descriptor review and independent exact-head "
            "release approval."),
    },
)

DSP_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "sweeps",
        "requirement": "Logarithmic sweep response, RMS gain and finite output.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "steps",
        "requirement": "Level-step DC settling and steady-state gain error.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "impulses",
        "requirement": "Impulse response, delay and analytic magnitude comparison.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "silence",
        "requirement": "All-zero input yields silent finite output.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "clean_speech",
        "requirement": "Synthetic speech-like stimulus preservation and peaks.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "level_or_load_control",
        "requirement": "Gain-limited device-response fitting control.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "gain",
        "requirement": "Measured band and cascade gain with exact gain limits.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "response",
        "requirement": "Analytic and measured response on sweep, impulse and probes.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "attack_release",
        "requirement": "Attack/release or adaptation dynamics of the candidate.",
        "package_status": "blocked_no_candidate_contract",
    },
    {
        "id": "headroom",
        "requirement": "Peak, headroom and clipping behavior on near-clip input.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "delay",
        "requirement": "Content delay of the candidate and wrapper.",
        "package_status": "blocked_no_candidate_runtime",
    },
    {
        "id": "numerical_behavior",
        "requirement": "Stability, nonfinite rejection and invalid-input controls.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "state_transitions",
        "requirement": "Reset, independent sessions and frame/whole equality.",
        "package_status": "control_only_structurally_verified",
    },
    {
        "id": "interacting_nonlinearities",
        "requirement": "Bounded cascade with interacting nonlinear configuration.",
        "package_status": "control_only_structurally_verified",
    },
)


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
    control = dsp_control()
    admission = run_admission_controls()

    gates = [{"id": gate_id, "requirement": requirement, "status": "blocked"}
             for gate_id, requirement in GATE_REQUIREMENTS]
    exact_blockers = [dict(item) for item in EXACT_BLOCKERS]
    requirements = []
    for item in CANDIDATE_REQUIREMENTS:
        entry = dict(item)
        entry["gate_ids"] = list(entry["gate_ids"])
        requirements.append(entry)

    missing_artifacts = [observation["path"]
                         for observation in audit["observations"]]
    dsp_items = []
    for item in DSP_REQUIREMENTS:
        entry = dict(item)
        entry["qualification_effect"] = "none"
        entry["satisfied_for_qualification"] = False
        dsp_items.append(entry)

    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "format": FORMAT,
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "no_missing_result_qualifies_candidate": True,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "reason": (
                "The exact implementation, checkpoint, runtime lock, rights "
                "record, parameterization, frozen oracle, rights-cleared "
                "device/speaker split and target timing are absent."),
        },
        "gates": gates,
        "exact_blockers": exact_blockers,
        "candidate_requirements": requirements,
        "candidate_metrics": None,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "path": "research/level_tone_control_20261028.md",
            "sha256": SOURCE_PINS["research/level_tone_control_20261028.md"],
            "dafx_2020_neural_parametric_eq": {
                "role": "relevant tone-control family; literature lead only",
                "reported": "learned prediction of EQ parameters with differentiable biquads",
                "usable_as_candidate_metric": False,
            },
            "dafx_2025_neural_multiband": {
                "role": "relevant self-supervised automatic EQ family; literature lead only",
                "usable_as_candidate_metric": False,
            },
            "synthetic_inverse_eq_screen": {
                "learned_inverse_eq_rmse_db": SOURCE_REPORTED_INVERSE_EQ_RMSE_DB,
                "identity_rmse_db": SOURCE_REPORTED_IDENTITY_RMSE_DB,
                "scope": "controlled synthetic EQ perturbations, not real speech",
                "usable_as_candidate_metric": False,
            },
            "note": (
                "The source note states that content, room and speaker "
                "variation were not represented and that the results do not "
                "support model selection for real speech; no value is "
                "reproduced or promoted by this package."),
        },
        "dsp_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "plan_note": (
                "Recover known device response before real speech. Apply "
                "held-out device/speaker split and gain limits."),
            "required_items": dsp_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [item["id"] for item in dsp_items],
            "real_model_metrics": None,
            "note": (
                "The bounded synthetic RBJ control exercises the DSP profile "
                "structurally, but no candidate, real device response, "
                "rights-cleared cohort, target runtime or approved parity "
                "exists, so the profile is not satisfied for qualification."),
        },
        "reference_protocol": {
            "executor": "absent",
            "model_executed": False,
            "surrogate": True,
            "surrogate_label": SURROGATE_LABEL,
            "qualification_effect": "none",
            "parameterization": (
                "causal RBJ peaking-biquad gain cascade, direct form I, "
                "zero buffering delay"),
            "differentiation": (
                "complex-step derivative in band gain (dB), independently "
                "checked by central finite difference"),
            "device_recovery_before_real_speech": True,
            "device_recovery_label": (
                "synthetic known-device response; no real speech is used"),
            "availability": {
                "buffering_delay_samples": 0,
                "candidate_delay_measured": False,
                "separation_declared": True,
                "synthetic_control_is_not_model_latency": True,
            },
            "synthetic_control": control,
        },
        "admission_schema": ADMISSION_SCHEMA,
        "admission_controls": admission,
        "controls": {
            "missing_result_never_qualifies": True,
            "nonfinite_never_counted_as_valid": True,
            "synthetic_control_never_qualifies": True,
            "adverse_all_rejected": admission["adverse_all_rejected"],
            "strict_json_all_rejected": admission["strict_json_all_rejected"],
            "gain_limit_enforced": control["gain_limits"]["enforced"],
            "reset_isolated": control["controls"]["reset_isolated"],
            "frame_vs_whole_identical": control["controls"][
                "frame_vs_whole_identical"],
            "real_device_or_speaker_split_present": False,
        },
        "asset_audit": {
            **audit,
            "audit_result": "absent" if not audit["any_present"] else "present",
            "qualified": False,
            "note": (
                "No candidate source, weights, runtime, device response, "
                "cohort, frozen run, adapter or rights record is present; a "
                "present artifact would require re-evaluation, not "
                "automatic qualification."),
        },
        "missing_historical_artifacts": missing_artifacts,
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "non_claims": list(NON_CLAIMS),
    }


def build_contract(report: Dict[str, Any], report_digest: str) -> Dict[str, Any]:
    gates = report["gates"]
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": "feasibility",
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "decision": DECISION,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "no_missing_result_qualifies_candidate": True,
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "task_row_identity": report["task_row_identity"],
        "gates": [dict(gate) for gate in gates],
        "exact_blockers": [dict(item) for item in report["exact_blockers"]],
        "candidate_requirements": report["candidate_requirements"],
        "reopen_conditions": [
            {"gate_id": gate["id"], "condition": gate["requirement"]}
            for gate in gates
        ],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "contract_id": ADMISSION_CONTRACT_ID,
            "accepted_manifest_qualifies": False,
            "executed_in_this_package": False,
            "upstream_identity_verified": False,
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "required_fields": list(ADMISSION_FIELDS),
        },
        "surrogate_protocol": {
            "label": SURROGATE_LABEL,
            "qualification_effect": "none",
            "model_executed": False,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
            "buffering_delay_samples": 0,
            "biquad": "RBJ peaking EQ, direct form I",
            "differentiation": "complex-step band-gain derivative",
            "synthetic_frequency_holdout": {
                "fit": list(FIT_PROBES),
                "held_out": list(HELDOUT_PROBES),
                "label": (
                    "synthetic_frequency_holdout_not_device_or_speaker_split"),
            },
            "gain_limit_db": GAIN_LIMIT_DB,
            "real_device_or_speaker_split": False,
        },
        "non_claims": list(NON_CLAIMS),
        "reproduction": {
            "generator": "run.py",
            "command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py",
            "cold_start_regenerations": 3,
            "byte_identical_required": True,
            "report_sha256": report_digest,
        },
    }


def sources_bytes(generated: Dict[str, bytes]) -> bytes:
    lines = [
        "# SHA-256 pins for " + TASK + ".",
        "# source: paths are relative to SOURCE_ROOT; worktree: paths are",
        "# relative to the SDK checkout; pkg: paths are relative to this",
        "# task-evidence directory. The mutable full plan/swarm/TASKS.json is",
        "# never hashed; only the linked-row stable identity is gated.",
        "",
    ]
    for path, digest in SOURCE_PINS.items():
        lines.append(f"{digest}  source:{path}")
    for path, digest in BOUNDARY_PINS.items():
        lines.append(f"{digest}  worktree:{path}")
    for name in LOCAL_PIN_PATHS:
        data = generated.get(name)
        if data is None:
            path = HERE / name
            if not path.is_file():
                raise Reject("missing local pin target: " + name)
            data = path.read_bytes()
        lines.append(f"{sha256_bytes(data)}  pkg:{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
