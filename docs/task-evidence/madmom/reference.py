# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-MADMOM.

The exact licensed madmom source checkout, immutable revision, pretrained
models, model configuration and Python/Cython runtime are absent from this
workspace, and the merged evidence records that madmom's shipped pretrained
models are non-commercial. Those are source-reported strings, not locally
verified artifacts.

This module therefore never imports madmom, NumPy, SciPy, Cython, PyTorch or any
neural runtime, never downloads or loads a model, never reads or writes real
audio and never measures a device clock. It provides four bounded pieces:

* a fail-closed absence audit over fixed workspace paths, recording the exact
  missing source, revision, weights, config, runtime, licence, model-rights,
  rights, cohort and parity artifacts;
* a strict caller-supplied-asset contract that validates shape, SHA-256
  metadata and a commercial-rights flag only, without importing, loading or
  executing anything;
* an original synthetic onset/beat/downbeat/tempo control that checks exact
  source-anchored interval mapping, duration scaling, silence, rebuffer, drift,
  meter phase, the final partial window and missing/invalid/nonfinite
  rejection. It is not madmom, performs no model inference and cannot qualify
  the candidate; and
* a scorer for that synthetic fixture only.

The disposition is ``DEFER`` / ``incomplete`` / ``not_qualified``. All eight
release gates remain blocked and no missing or adverse result is promoted.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
AUDIO_ROOT = SDK_ROOT.parents[2]

TASK = "SDK-MADMOM"
TITLE = "madmom"
SLUG = "madmom"
COMPONENT = SLUG
TASK_PREFIX = "docs/task-evidence/madmom/"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence/madmom/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROTOCOL = "audio-sdk/madmom-evidence/0.1"
PROFILE = "Rate"
MODE = "feasibility"
BASE_COMMIT = "b4960fdba1991a35c07ff7f22cda5257c4749768"
BRANCH = "swarm/SDK-MADMOM"
REVIEWER = "reviewer-MADMOM"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-MADMOM"
)
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_provider_intake"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS
FULL_FIXTURE_SAMPLES = 96000
FINAL_PARTIAL_SAMPLES = 96037
FINAL_PARTIAL_VALID = FINAL_PARTIAL_SAMPLES % FRAME_SAMPLES
FINAL_PARTIAL_ONSET = 96030

LOG_FLOOR = 1.0e-12
ONSET_THRESHOLD = 0.35
BASELINE_ALPHA = 0.20
MIN_ONSET_GAP_FRAMES = 7
TEMPO_MIN_BPM_X100 = 6000
TEMPO_MAX_BPM_X100 = 18000
TEMPO_STABILITY_SPREAD_X100 = 100
MIN_IOIS_FOR_TEMPO = 4
ACCENT_MIN_DELTA_MILLI = 150
MIN_ONSETS_FOR_METER = 5
METER_MIN_PERIOD = 2
METER_MAX_PERIOD = 16
DEFAULT_EPOCH = 1

UPSTREAM_NAME = "madmom"
UPSTREAM_REPORTED_SOURCE_LICENSE = "BSD (source-reported; BSD-2/3 noted)"
UPSTREAM_REPORTED_MODELS_LICENSE = "CC BY-NC-SA 4.0 (models, source-reported)"
UPSTREAM_REPORTED_COMMERCIAL_USE = "No with shipped models"
UPSTREAM_REPORTED_RETURNS = "BPM, beats, downbeats"
UPSTREAM_REPORTED_ONLINE = "Some models"
UPSTREAM_REPORTED_INFERENCE_SCOPE = (
    "some models reported online; exact streaming API, latency and causality "
    "unverified"
)
UPSTREAM_REPORTED_FRAMEWORK = "Python/Cython (source-reported)"
UPSTREAM_REPORTED_METHOD = "RNN/DBN beat and downbeat tracking"
UPSTREAM_PROJECT = "madmom (JKU)"
UPSTREAM_CONTACT = "Contact JKU"
UPSTREAM_REVISION: Optional[str] = None
UPSTREAM_REPOSITORY_URL = "https://github.com/CPJKU/madmom"
UPSTREAM_PAPER_URL = "https://doi.org/10.1145/2964284.2973795"
SOURCE_REVISION_PIN_AVAILABLE = False
TASK_GEOMETRY_STATUS = "unestablished"

SOURCE_PINS: Dict[str, str] = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
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
    "docs/task-evidence/beat-this/README.md":
        "55e1b0f327c2e6beb4cf9726fe06dafebb5e8b364a1e7188c91d20f17c4a9f32",
    "docs/task-evidence/beatnet/README.md":
        "d453bda9ea5d3dda875b05ff7fbd238e5ecdef69ad48deb4be26c68f98b8c828",
}

SPDX = {
    "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
    "SPDX-License-Identifier": "Apache-2.0",
}

MISSING_SOURCE_PATHS = (
    "data/checkouts/madmom",
    "research/voice-enhancement-20261101/repos/madmom",
)
MISSING_WEIGHTS_PATHS = (
    "data/models/madmom",
    "data/weights/madmom",
)
MISSING_RUNTIME_PATH = "data/envs/madmom"
MISSING_RUNTIME_LOCK_PATH = "data/envs/madmom/requirements.lock"
MISSING_LICENSE_PATH = "data/rights/madmom-license.json"
MISSING_MODEL_LICENSE_PATH = "data/rights/madmom-model-license.json"
MISSING_RIGHTS_PATH = "data/rights/madmom-rights.json"
MISSING_COHORT_PATH = "data/runs/madmom-cohort/manifest.json"
MISSING_PARITY_PATH = "data/runs/madmom-parity/manifest.json"

ABSENCE_PROBES: Tuple[str, ...] = tuple(sorted(set(
    MISSING_SOURCE_PATHS
    + MISSING_WEIGHTS_PATHS
    + (
        "research/voice-enhancement-20261101/hf-cache/models--madmom",
        MISSING_RUNTIME_PATH,
        MISSING_RUNTIME_LOCK_PATH,
        MISSING_LICENSE_PATH,
        MISSING_MODEL_LICENSE_PATH,
        MISSING_RIGHTS_PATH,
        MISSING_COHORT_PATH,
        MISSING_PARITY_PATH,
    )
)))

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
STABLE_FIELDS: Dict[str, Any] = {
    "acceptance": (
        "Apply the rate acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted "
        "investigation handoff; it does not close the conditional "
        "implementation."
    ),
    "component": "madmom",
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry "
        "and matched evidence. Then implement or wrap a minimal reference "
        "using the relevant public adapter boundary and ship it as optional "
        "initially. Record a concrete blocker if feasibility fails."
    ),
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "evidence": ["cpp-library/pipeline-validation/playback-speed-candidates.md"],
    "id": "SDK-MADMOM",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": "madmom",
    "write_scope": [
        "SDK provider, tool or evidence directory for madmom and its own "
        "fixtures"
    ],
}
STABLE_SHA256 = "73624c37514f155680c9a30b7c39a6539daa2c7b2eb14107c496986d7e7a4a1d"

BOARD_ROW: Dict[str, Any] = {
    "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "stable_fields": STABLE_FIELDS,
    "stable_sha256": STABLE_SHA256,
    "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
    "whole_file_hashed": False,
    "claim": {
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
    },
    "note": (
        "Only the stable linked-row fields are read and gated. The mutable "
        "full plan/swarm/TASKS.json is never hashed, pinned or used as a "
        "digest source."
    ),
}

GATES: Tuple[Dict[str, str], ...] = (
    {
        "id": "exact_source_and_asset_identity",
        "requirement": (
            "Pin the full 40-hex madmom source revision, source and model "
            "SHA-256 values, model configuration, byte counts and licence "
            "identity at one immutable package."
        ),
        "status": "blocked",
    },
    {
        "id": "runtime_admission",
        "requirement": (
            "Admit an isolated hash-pinned Python/Cython runtime with a "
            "complete lock, recorded platform and offline model admission."
        ),
        "status": "blocked",
    },
    {
        "id": "artifact_rights_and_licence",
        "requirement": (
            "Clear source, model, training-data, source-audio, output-use and "
            "redistribution rights and verify the reported clone of a "
            "non-commercial model grant or an explicit JKU commercial licence."
        ),
        "status": "blocked",
    },
    {
        "id": "exact_reference_parity",
        "requirement": (
            "Reproduce one exact-runtime madmom beats/downbeats/tempo output "
            "vector on a frozen caller input and configuration, including "
            "deterministic reset."
        ),
        "status": "blocked",
    },
    {
        "id": "beat_cohort_and_scoring",
        "requirement": (
            "Score a rights-cleared held-out music cohort for beat F-measure, "
            "downbeat F-measure, tempo accuracy and tempo-octave errors "
            "against matched labels."
        ),
        "status": "blocked",
    },
    {
        "id": "task_scope_and_geometry",
        "requirement": (
            "Establish the exact sample rate, channels, resampling, frame hop, "
            "window/context, model-specific online behaviour and file-level "
            "boundary without inventing geometry."
        ),
        "status": "blocked",
    },
    {
        "id": "opt_in_provider_intake",
        "requirement": (
            "Complete explicit opt-in provider or analysis-adapter intake, "
            "licence review, descriptor review and an independent "
            "public-surface decision."
        ),
        "status": "blocked",
    },
    {
        "id": "public_default_and_release",
        "requirement": (
            "Record target-device timing, resource limits, independent "
            "exact-head review, explicit default selection and release or "
            "benchmark approval; this package is off by default."
        ),
        "status": "blocked",
    },
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout_absent",
        "gate": "exact_source_and_asset_identity",
        "status": "blocked",
        "qualifies": False,
        "state": "absent",
        "requirement": (
            "Supply the madmom source checkout at an immutable 40-hex "
            "revision under research/voice-enhancement-20261101/repos/madmom "
            "or data/checkouts/madmom; no checkout exists in the workspace."
        ),
    },
    {
        "id": "upstream_revision_unpinned",
        "gate": "exact_source_and_asset_identity",
        "status": "blocked",
        "qualifies": False,
        "state": "absent",
        "requirement": (
            "Resolve madmom to a full 40-hex commit and publish a per-file "
            "SHA-256 source manifest; the pinned note records the repository "
            "URL, method and paper but no repository tag or commit."
        ),
    },
    {
        "id": "pretrained_model_rights_noncommercial",
        "gate": "artifact_rights_and_licence",
        "status": "blocked",
        "qualifies": False,
        "state": "restrictive",
        "requirement": (
            "Replace or license the shipped non-commercial pretrained models: "
            "the merged evidence records models under CC BY-NC-SA 4.0 with "
            "commercial use 'No with shipped models' and asks callers to "
            "contact JKU. Supply the model licence text and either an explicit "
            "JKU commercial grant or alternative weights whose licence permits "
            "the intended commercial distribution."
        ),
    },
    {
        "id": "inference_models_and_config_absent",
        "gate": "exact_source_and_asset_identity",
        "status": "blocked",
        "qualifies": False,
        "state": "absent",
        "requirement": (
            "Supply the exact pretrained beat/downbeat model files, model "
            "configuration and parameter metadata with byte counts and "
            "SHA-256 values at one immutable revision; no model or config was "
            "downloaded, staged or identified by digest."
        ),
    },
    {
        "id": "task_geometry_and_streaming_unestablished",
        "gate": "task_scope_and_geometry",
        "status": "blocked",
        "qualifies": False,
        "state": "unestablished",
        "requirement": (
            "Record the exact sample rate, channels, resampling, frame hop, "
            "window/context, model-specific online/offline behaviour, "
            "padding/crop recipe and file-level boundary in a pinned "
            "configuration; the merged note reports only 'BPM, beats, "
            "downbeats' and 'Some models' online, not task geometry."
        ),
    },
    {
        "id": "runtime_absent",
        "gate": "runtime_admission",
        "status": "blocked",
        "qualifies": False,
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned Python/Cython/NumPy runtime with "
            "a complete lock at data/envs/madmom/requirements.lock and a "
            "recorded platform; no environment, package pin or lock exists "
            "and madmom is not importable in the recorded interpreter."
        ),
    },
    {
        "id": "source_license_unverified",
        "gate": "artifact_rights_and_licence",
        "status": "blocked",
        "qualifies": False,
        "state": "absent",
        "requirement": (
            "Add the upstream source licence text and terms at the resolved "
            "commit and verify the reported BSD source grant; no licence file, "
            "terms statement or redistribution grant is present, and the "
            "non-commercial model terms are not covered by a source licence."
        ),
    },
    {
        "id": "parity_cohort_and_benchmark_absent",
        "gate": "exact_reference_parity",
        "status": "blocked",
        "qualifies": False,
        "state": "absent",
        "requirement": (
            "Produce one approved exact-runtime madmom output on a frozen "
            "caller input plus cleaned held-out beat/downbeat/tempo scores, "
            "target-device timing and independent review; no local output, "
            "parity vector, cohort score, listening result or benchmark "
            "exists."
        ),
    },
)

CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "channels",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "commercial_grant_path",
    "commercial_grant_sha256",
    "commercial_use_permitted",
    "license_record_path",
    "license_record_sha256",
    "model_config_path",
    "model_config_sha256",
    "model_license_id",
    "model_license_text_path",
    "model_license_text_sha256",
    "parity_vector_path",
    "parity_vector_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "sample_rate_hz",
    "source_checkout_path",
    "source_manifest_sha256",
    "source_revision",
    "weights_byte_count",
    "weights_path",
    "weights_sha256",
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/madmom/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_shape_ranges_and_a_bool_"
        "commercial_flag_only; do_not_import_load_or_execute_in_this_package"
    ),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_source_revision": "40_lowercase_hex",
    "model_license_id_pattern": "^[A-Za-z0-9][A-Za-z0-9.+-]{0,63}$",
    "commercial_use_permitted_type": "boolean",
    "sample_rate_range_hz": [8000, 192000],
    "channels_range": [1, 2],
    "weights_byte_count_range": [1, 536870912],
    "notes": (
        "Every declared asset is caller-owned and must exist at an absolute "
        "path with a matching lowercase SHA-256 before a caller may process "
        "audio. Validation is metadata-only and never reads, imports, loads "
        "or executes madmom. A shape-valid manifest never qualifies the "
        "candidate and never proves the model licence permits commercial use."
    ),
}

_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_MODEL_LICENSE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,63}$")


class Reject(ValueError):
    """Deterministic, machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(Path(path).read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            _normalize_negzero(value),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("json_not_canonical", str(error)) from error


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"


def object_digest(value: Any) -> str:
    return sha256(canonical_bytes(value))


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse JSON while rejecting duplicate keys, NaN and Infinity."""

    def reject(value: str) -> Any:
        raise Reject("nonfinite_json", value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate_json_key", key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("json_not_object", "expected a JSON object")
    return value


def read_strict_json(path: Path) -> Dict[str, Any]:
    return strict_loads(Path(path).read_text(encoding="utf-8"))


def signal_digest(samples: Sequence[float]) -> str:
    return sha256(b"".join(
        struct.pack("<f", float(value)) for value in samples))


def llround(value: float) -> int:
    """C llround semantics: halves away from zero."""
    return (int(math.floor(value + 0.5)) if value >= 0.0
            else int(math.ceil(value - 0.5)))


def _exact_keys(value: Dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise Reject(
            "strict_keys_mismatch",
            label + ":" + ",".join(sorted(set(value) ^ keys)),
        )


def _int(value: Any, label: str, low: int, high: int) -> int:
    if (isinstance(value, bool) or not isinstance(value, int)
            or not low <= value <= high):
        raise Reject("invalid_integer", label)
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Reject("invalid_string", label)
    return value


def _absolute_path(value: Any, label: str) -> str:
    text = _string(value, label)
    if "\x00" in text or not Path(text).is_absolute():
        raise Reject("path_not_absolute", label)
    return text


def _sha(value: Any, label: str) -> str:
    text = _string(value, label)
    if not _SHA256_PATTERN.fullmatch(text):
        raise Reject("invalid_sha256", label)
    return text


def validate_asset_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate a future caller-owned madmom asset manifest.

    No file is opened, imported, loaded or executed. The function only checks
    strict field shape, absolute paths, SHA-256 syntax, revision syntax,
    a model-licence identifier, a boolean commercial flag and bounded integer
    ranges. Successful validation is not a rights grant, a model result or a
    qualification.
    """
    if not isinstance(manifest, dict):
        raise Reject("asset_manifest_not_object", "expected a JSON object")
    _exact_keys(manifest, set(CALLER_ASSET_FIELDS), "asset_manifest")
    for field in (
        "source_checkout_path",
        "weights_path",
        "model_config_path",
        "license_record_path",
        "model_license_text_path",
        "commercial_grant_path",
        "rights_record_path",
        "runtime_lock_path",
        "cohort_manifest_path",
        "parity_vector_path",
    ):
        _absolute_path(manifest[field], field)
    for field in (
        "source_manifest_sha256",
        "weights_sha256",
        "model_config_sha256",
        "license_record_sha256",
        "model_license_text_sha256",
        "commercial_grant_sha256",
        "rights_record_sha256",
        "runtime_lock_sha256",
        "cohort_manifest_sha256",
        "parity_vector_sha256",
    ):
        _sha(manifest[field], field)
    revision = _string(manifest["source_revision"], "source_revision")
    if not _REVISION_PATTERN.fullmatch(revision):
        raise Reject("invalid_source_revision", "source_revision")
    license_id = _string(manifest["model_license_id"], "model_license_id")
    if not _MODEL_LICENSE_PATTERN.fullmatch(license_id):
        raise Reject("invalid_model_license_id", "model_license_id")
    if not isinstance(manifest["commercial_use_permitted"], bool):
        raise Reject("invalid_commercial_flag", "commercial_use_permitted")
    _int(manifest["sample_rate_hz"], "sample_rate_hz", 8000, 192000)
    _int(manifest["channels"], "channels", 1, 2)
    _int(manifest["weights_byte_count"], "weights_byte_count", 1, 536870912)
    return {
        "status": "accepted_for_shape_only",
        "executed": False,
        "model_loaded": False,
        "qualifies": False,
        "commercial_use_metadata": manifest["commercial_use_permitted"],
        "upstream_revision_pinned_by_this_package": False,
    }


def audit_assets() -> Dict[str, Any]:
    """Probe fixed candidate paths; absence is recorded, never filled."""
    probes = [
        {"path": relative, "exists": (AUDIO_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]
    all_absent = all(item["exists"] is False for item in probes)
    return {
        "all_absence_probes_absent": all_absent,
        "probe_count": len(probes),
        "probes": probes,
        "source_checkout_present": any(
            (AUDIO_ROOT / path).exists() for path in MISSING_SOURCE_PATHS),
        "weights_present": any(
            (AUDIO_ROOT / path).exists() for path in MISSING_WEIGHTS_PATHS),
        "runtime_present": (AUDIO_ROOT / MISSING_RUNTIME_PATH).exists(),
        "runtime_lock_present": (AUDIO_ROOT / MISSING_RUNTIME_LOCK_PATH).exists(),
        "license_record_present": (AUDIO_ROOT / MISSING_LICENSE_PATH).exists(),
        "model_license_record_present": (
            AUDIO_ROOT / MISSING_MODEL_LICENSE_PATH).exists(),
        "rights_record_present": (AUDIO_ROOT / MISSING_RIGHTS_PATH).exists(),
        "cohort_manifest_present": (AUDIO_ROOT / MISSING_COHORT_PATH).exists(),
        "parity_manifest_present": (AUDIO_ROOT / MISSING_PARITY_PATH).exists(),
        "network_used": False,
        "download_performed": False,
    }


def _pin_rows() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    source_pins: Dict[str, Dict[str, Any]] = {}
    for relative, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(AUDIO_ROOT / relative)
        source_pins[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    boundary_pins: Dict[str, Dict[str, Any]] = {}
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(SDK_ROOT / relative)
        boundary_pins[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    for rows in (source_pins, boundary_pins):
        if any(row["verified"] is not True for row in rows.values()):
            raise Reject("pin_mismatch", "a pinned input changed")
    return source_pins, boundary_pins


def task_row_identity() -> Dict[str, Any]:
    """Read only the stable linked row; never hash the mutable full board."""
    relative = "audio-benchmark-platform/plan/swarm/TASKS.json"
    path = AUDIO_ROOT / relative
    if not path.is_file():
        raise Reject("task_board_missing", relative)
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("task_board_unreadable", relative) from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise Reject("task_row_not_unique", TASK)
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise Reject("task_row_identity_mismatch", TASK)
    if stable["repository"] != "audio-sdk" or stable["mode"] != MODE:
        raise Reject("task_row_repository_or_mode_mismatch", TASK)
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise Reject("task_row_claim_missing", TASK)
    if claim.get("base_commit") != BASE_COMMIT:
        raise Reject("claim_base_commit_mismatch", TASK)
    if claim.get("branch") != BRANCH:
        raise Reject("claim_branch_mismatch", TASK)
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise Reject("claim_worktree_mismatch", TASK)
    if claim.get("reviewer") != REVIEWER:
        raise Reject("claim_reviewer_mismatch", TASK)
    return {
        "source": relative,
        "stable_fields": stable,
        "stable_sha256": object_digest(stable),
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
# Strict synthetic stimuli.  These are analytic click tracks, not madmom.
# ---------------------------------------------------------------------------

STIMULI: Dict[str, Dict[str, Any]] = {
    "music_like_1x": {
        "kind": "periodic",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "period_samples": 9600,
        "beats": 10,
        "accent_every": 4,
        "amplitude_milli": 700,
        "accent_amplitude_milli": 900,
        "noise_amplitude_milli": 0,
        "noise_seed": 7,
    },
    "rate_0_8": {
        "kind": "periodic",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "period_samples": 12000,
        "beats": 8,
        "accent_every": 4,
        "amplitude_milli": 700,
        "accent_amplitude_milli": 900,
        "noise_amplitude_milli": 0,
        "noise_seed": 11,
    },
    "rate_1_2": {
        "kind": "periodic",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "period_samples": 8000,
        "beats": 12,
        "accent_every": 4,
        "amplitude_milli": 700,
        "accent_amplitude_milli": 900,
        "noise_amplitude_milli": 0,
        "noise_seed": 13,
    },
    "low_snr_adverse": {
        "kind": "periodic",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "period_samples": 9600,
        "beats": 10,
        "accent_every": 4,
        "amplitude_milli": 600,
        "accent_amplitude_milli": 620,
        "noise_amplitude_milli": 300,
        "noise_seed": 17,
    },
    "tempo_out_of_range_adverse": {
        "kind": "periodic",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "period_samples": 3200,
        "beats": 30,
        "accent_every": 4,
        "amplitude_milli": 650,
        "accent_amplitude_milli": 800,
        "noise_amplitude_milli": 0,
        "noise_seed": 19,
    },
    "speech_like_unfamiliar": {
        "kind": "irregular",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "starts_frames": [10, 27, 49, 66, 94, 111, 139, 160, 191, 210,
                          241, 263, 295, 316, 350, 370, 405, 427, 460,
                          483, 515, 538, 570, 590],
        "durations_frames": [3, 4, 2, 5, 3, 4, 2, 6, 3, 4, 5, 2, 4, 3,
                             6, 2, 4, 5, 3, 2, 6, 4, 3, 5],
        "amplitudes_milli": [400, 700, 500, 800, 450, 650, 520, 780, 410,
                             690, 530, 760, 470, 720, 560, 810, 430, 670,
                             540, 790, 480, 740, 510, 680],
    },
    "silence": {
        "kind": "silence",
        "length_samples": FULL_FIXTURE_SAMPLES,
    },
    "drift": {
        "kind": "drift",
        "length_samples": 120000,
        "periods_frames": [60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48],
        "amplitude_milli": 700,
    },
    "rebuffer": {
        "kind": "periodic_with_gap",
        "length_samples": FULL_FIXTURE_SAMPLES,
        "period_samples": 9600,
        "beats_before_gap": 5,
        "beats_after_gap": 5,
        "gap_samples": 5920,
        "amplitude_milli": 700,
    },
    "final_partial": {
        "kind": "final_partial",
        "length_samples": FINAL_PARTIAL_SAMPLES,
        "onset_sample": FINAL_PARTIAL_ONSET,
        "amplitude_milli": 700,
    },
}

_STIMULUS_KEYS: Dict[str, set[str]] = {
    "periodic": {
        "kind", "length_samples", "period_samples", "beats", "accent_every",
        "amplitude_milli", "accent_amplitude_milli", "noise_amplitude_milli",
        "noise_seed",
    },
    "irregular": {
        "kind", "length_samples", "starts_frames", "durations_frames",
        "amplitudes_milli",
    },
    "silence": {"kind", "length_samples"},
    "drift": {"kind", "length_samples", "periods_frames", "amplitude_milli"},
    "periodic_with_gap": {
        "kind", "length_samples", "period_samples", "beats_before_gap",
        "beats_after_gap", "gap_samples", "amplitude_milli",
    },
    "final_partial": {
        "kind", "length_samples", "onset_sample", "amplitude_milli",
    },
}


def validate_stimuli(stimuli: Dict[str, Dict[str, Any]]) -> None:
    if not isinstance(stimuli, dict) or len(stimuli) != 10:
        raise Reject("stimuli_count_mismatch", "expected ten stimuli")
    for name, spec in sorted(stimuli.items()):
        if not isinstance(spec, dict) or "kind" not in spec:
            raise Reject("invalid_stimulus", name)
        kind = spec["kind"]
        if kind not in _STIMULUS_KEYS:
            raise Reject("unknown_stimulus_kind", str(kind))
        _exact_keys(spec, _STIMULUS_KEYS[kind], "stimulus:" + name)
        length = _int(spec["length_samples"], "length_samples", 160, 200000)
        if length % FRAME_SAMPLES not in (0, FINAL_PARTIAL_VALID):
            raise Reject("invalid_stimulus_length", name)
        if kind == "periodic":
            period = _int(spec["period_samples"], "period_samples", 160, 20000)
            if period % FRAME_SAMPLES:
                raise Reject("period_not_frame_aligned", name)
            _int(spec["beats"], "beats", 1, 100)
            _int(spec["accent_every"], "accent_every", 1, 16)
            for key in ("amplitude_milli", "accent_amplitude_milli",
                        "noise_amplitude_milli"):
                _int(spec[key], key, 0, 1000)
            _int(spec["noise_seed"], "noise_seed", 0, 2**31 - 1)
            if spec["amplitude_milli"] + spec["noise_amplitude_milli"] > 1000:
                raise Reject("stimulus_not_bounded", name)
            if spec["accent_amplitude_milli"] + spec["noise_amplitude_milli"] > 1000:
                raise Reject("stimulus_not_bounded", name)
        elif kind == "irregular":
            starts = spec["starts_frames"]
            durations = spec["durations_frames"]
            amplitudes = spec["amplitudes_milli"]
            if not (isinstance(starts, list) and isinstance(durations, list)
                    and isinstance(amplitudes, list)
                    and len(starts) == len(durations) == len(amplitudes)
                    and 8 <= len(starts) <= 40):
                raise Reject("irregular_lists_mismatch", name)
            previous = -MIN_ONSET_GAP_FRAMES
            for frame, duration, amplitude in zip(starts, durations, amplitudes):
                frame = _int(frame, "starts_frames", 0, length // FRAME_SAMPLES)
                _int(duration, "durations_frames", 1, 16)
                _int(amplitude, "amplitudes_milli", 1, 1000)
                if frame - previous < MIN_ONSET_GAP_FRAMES:
                    raise Reject("irregular_onset_too_close", name)
                previous = frame
        elif kind == "drift":
            periods = spec["periods_frames"]
            if not isinstance(periods, list) or not 4 <= len(periods) <= 32:
                raise Reject("drift_periods_mismatch", name)
            for period in periods:
                _int(period, "periods_frames", MIN_ONSET_GAP_FRAMES, 200)
            _int(spec["amplitude_milli"], "amplitude_milli", 1, 1000)
        elif kind == "periodic_with_gap":
            period = _int(spec["period_samples"], "period_samples", 160, 20000)
            if period % FRAME_SAMPLES:
                raise Reject("period_not_frame_aligned", name)
            _int(spec["beats_before_gap"], "beats_before_gap", 2, 16)
            _int(spec["beats_after_gap"], "beats_after_gap", 2, 16)
            _int(spec["gap_samples"], "gap_samples", 160, 40000)
            _int(spec["amplitude_milli"], "amplitude_milli", 1, 1000)
        elif kind == "final_partial":
            onset = _int(spec["onset_sample"], "onset_sample", 0, length - 1)
            if length % FRAME_SAMPLES != FINAL_PARTIAL_VALID:
                raise Reject("final_partial_length_mismatch", name)
            if onset < length - FRAME_SAMPLES:
                raise Reject("final_partial_onset_mismatch", name)
            _int(spec["amplitude_milli"], "amplitude_milli", 1, 1000)
        else:  # silence
            if length != FULL_FIXTURE_SAMPLES:
                raise Reject("silence_length_mismatch", name)


@dataclass(frozen=True)
class OnsetEvent:
    source_start: int
    source_end: int
    frame_index: int
    epoch: int
    strength_milli: int
    available_monotonic_ns: int
    capture_first_ns: int

    def as_dict(self) -> Dict[str, str]:
        return {
            "source_start": str(self.source_start),
            "source_end": str(self.source_end),
            "frame_index": str(self.frame_index),
            "epoch": str(self.epoch),
            "strength_milli": str(self.strength_milli),
            "available_monotonic_ns": str(self.available_monotonic_ns),
            "capture_first_ns": str(self.capture_first_ns),
        }


class Analyzer:
    """Causal, frame-clocked onset analyzer with explicit rejection."""

    def __init__(self, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS, frame_samples: int = FRAME_SAMPLES,
                 sample_format: str = SAMPLE_FORMAT, epoch: int = DEFAULT_EPOCH):
        if (sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS
                or frame_samples != FRAME_SAMPLES
                or sample_format != SAMPLE_FORMAT):
            raise Reject("unsupported_config",
                         "v0 accepts only 16000/1/160/float32")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise Reject("invalid_epoch", "epoch must be a nonnegative integer")
        self.sample_rate_hz = sample_rate_hz
        self.channels = channels
        self.frame_samples = frame_samples
        self.sample_format = sample_format
        self.epoch = epoch
        self.frame_index = 0
        self.baseline = math.log(LOG_FLOOR)
        self.last_onset_frame: Optional[int] = None
        self.events: List[OnsetEvent] = []
        self.rejections: List[str] = []
        self.frame_records: List[Dict[str, Any]] = []

    @property
    def state_digest(self) -> str:
        return object_digest({
            "frame_index": str(self.frame_index),
            "baseline_milli": str(llround(self.baseline * 1000)),
            "last_onset_frame": (
                None if self.last_onset_frame is None
                else str(self.last_onset_frame)),
            "event_count": str(len(self.events)),
        })

    def _reject(self, code: str, message: str) -> None:
        self.rejections.append(code)
        raise Reject(code, message)

    def process_frame(self, samples: Any,
                      epoch: Optional[int] = None,
                      input_count: Optional[int] = None,
                      valid_count: Optional[int] = None) -> Dict[str, Any]:
        if samples is None:
            self._reject("missing_input", "missing frame buffer")
        if isinstance(samples, (str, bytes, bytearray)):
            self._reject("invalid_frame_type", "frame must be a sample sequence")
        try:
            count = len(samples)
        except TypeError:
            self._reject("invalid_frame_type", "frame must be a sample sequence")
        if epoch is not None and epoch != self.epoch:
            self._reject("epoch_mismatch", "stale or future epoch")
        if input_count is not None and input_count != count:
            self._reject("frame_count_mismatch", "input_count does not match")
        if count != FRAME_SAMPLES:
            self._reject("frame_count_mismatch", "frame must have 160 samples")
        valid = FRAME_SAMPLES if valid_count is None else valid_count
        if (isinstance(valid, bool) or not isinstance(valid, int)
                or not 1 <= valid <= FRAME_SAMPLES):
            self._reject("invalid_valid_count", "valid_count must be 1..160")
        checked: List[float] = []
        for index, value in enumerate(samples):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                self._reject("invalid_sample_type",
                             "sample " + str(index) + " is not numeric")
            number = float(value)
            if not math.isfinite(number):
                self._reject("nonfinite_input",
                             "sample " + str(index) + " is not finite")
            checked.append(number)
        if any(value != 0.0 for value in checked[valid:]):
            self._reject("padding_not_zero", "final padding must be zero")
        energy = sum(value * value for value in checked[:valid]) / valid
        log_energy = math.log(max(energy, LOG_FLOOR))
        strength = max(0.0, log_energy - self.baseline - ONSET_THRESHOLD)
        frame = self.frame_index
        source_start = frame * FRAME_SAMPLES
        onset = strength > 0.0 and (
            self.last_onset_frame is None
            or frame - self.last_onset_frame >= MIN_ONSET_GAP_FRAMES)
        strength_milli = llround(strength * 1000)
        record = {
            "frame_index": str(frame),
            "source_start": str(source_start),
            "valid_count": str(valid),
            "input_count": str(count),
            "strength_milli": str(strength_milli),
            "onset": onset,
        }
        if onset:
            self.events.append(OnsetEvent(
                source_start=source_start,
                source_end=source_start + valid,
                frame_index=frame,
                epoch=self.epoch,
                strength_milli=strength_milli,
                available_monotonic_ns=(frame + 1) * FRAME_NS,
                capture_first_ns=source_start * SAMPLE_NS,
            ))
            self.last_onset_frame = frame
        # Only a fully validated frame advances recurrent state.
        self.baseline = ((1.0 - BASELINE_ALPHA) * self.baseline
                         + BASELINE_ALPHA * log_energy)
        self.frame_index += 1
        self.frame_records.append(record)
        return record


def _burst(length: int, amplitude: float, period: int = 48) -> List[float]:
    """Integer-shaped decaying triangle; no platform libm is involved."""
    return [
        amplitude * (length - index)
        * (period - abs(2 * (index % period) - period))
        / float(length * period)
        for index in range(length)
    ]


def _noise(length: int, amplitude: float, seed: int) -> List[float]:
    state = seed
    values: List[float] = []
    for _ in range(length):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(((2.0 * state / 0x7FFFFFFF) - 1.0) * amplitude)
    return values


def _add_burst(signal: List[float], start: int, burst: Sequence[float],
               length_samples: int) -> None:
    for offset, value in enumerate(burst):
        position = start + offset
        if position >= length_samples:
            break
        signal[position] += value


def generate_signal(spec: Dict[str, Any]) -> Tuple[List[float], List[Tuple[int, int]]]:
    """Return a bounded synthetic signal and half-open excluded gap intervals."""
    length = spec["length_samples"]
    kind = spec["kind"]
    signal = [0.0] * length
    gaps: List[Tuple[int, int]] = []
    if kind == "silence":
        return signal, gaps
    if kind == "periodic":
        period = spec["period_samples"]
        accent = spec["accent_every"]
        for beat in range(spec["beats"]):
            amplitude = (spec["accent_amplitude_milli"] if beat % accent == 0
                         else spec["amplitude_milli"]) / 1000.0
            _add_burst(signal, beat * period, _burst(48, amplitude), length)
        noise = spec["noise_amplitude_milli"] / 1000.0
        if noise:
            for index, value in enumerate(
                    _noise(length, noise, spec["noise_seed"])):
                signal[index] += value
    elif kind == "periodic_with_gap":
        period = spec["period_samples"]
        before = spec["beats_before_gap"]
        gap_start = (before - 1) * period
        gap_end = gap_start + spec["gap_samples"]
        gaps.append((gap_start, gap_end))
        positions = [beat * period for beat in range(before)]
        positions.extend(gap_end + beat * period
                         for beat in range(spec["beats_after_gap"]))
        burst = _burst(48, spec["amplitude_milli"] / 1000.0)
        for position in positions:
            _add_burst(signal, position, burst, length)
    elif kind == "irregular":
        for start_frame, duration_frames, amplitude in zip(
                spec["starts_frames"], spec["durations_frames"],
                spec["amplitudes_milli"]):
            burst = _burst(duration_frames * FRAME_SAMPLES,
                           amplitude / 1000.0, 135)
            _add_burst(signal, start_frame * FRAME_SAMPLES, burst, length)
    elif kind == "drift":
        position = 0
        burst = _burst(48, spec["amplitude_milli"] / 1000.0)
        for period in spec["periods_frames"]:
            _add_burst(signal, position, burst, length)
            position += period * FRAME_SAMPLES
        _add_burst(signal, position, burst, length)
    elif kind == "final_partial":
        _add_burst(signal, spec["onset_sample"],
                   _burst(48, spec["amplitude_milli"] / 1000.0), length)
    else:
        raise Reject("unknown_stimulus_kind", str(kind))
    for value in signal:
        if not math.isfinite(value) or abs(value) > 1.0 + 1e-12:
            raise Reject("generated_signal_out_of_bounds", kind)
    return signal, gaps


def estimate_tempo(events: Sequence[OnsetEvent],
                   gap_intervals: Sequence[Tuple[int, int]] = ()) -> Dict[str, Any]:
    """Estimate tempo from source-anchored IOIs; fail closed on instability."""
    frames = [event.frame_index for event in events]
    if not frames:
        return {"status": "no_onsets", "onset_count": "0", "ioi_frames": [],
                "bpm_x100_values": [], "spread_x100": "0", "bpm_x100": None,
                "excluded_ioi_count": "0"}
    iois: List[int] = []
    excluded = 0
    for first, second in zip(frames, frames[1:]):
        midpoint = ((first + second) * FRAME_SAMPLES) // 2
        if any(start <= midpoint < end for start, end in gap_intervals):
            excluded += 1
            continue
        iois.append(second - first)
    if len(iois) < MIN_IOIS_FOR_TEMPO:
        return {"status": "insufficient_onsets",
                "onset_count": str(len(frames)),
                "ioi_frames": [str(value) for value in iois],
                "bpm_x100_values": [], "spread_x100": "0", "bpm_x100": None,
                "excluded_ioi_count": str(excluded)}
    bpms = [llround(600000 / ioi) for ioi in iois]
    spread = max(bpms) - min(bpms)
    base = {
        "onset_count": str(len(frames)),
        "ioi_frames": [str(value) for value in iois],
        "bpm_x100_values": [str(value) for value in bpms],
        "spread_x100": str(spread),
        "excluded_ioi_count": str(excluded),
    }
    if any(value < TEMPO_MIN_BPM_X100 or value > TEMPO_MAX_BPM_X100
           for value in bpms):
        return dict(base, status="tempo_out_of_range", bpm_x100=None)
    if spread > TEMPO_STABILITY_SPREAD_X100:
        return dict(base, status="no_stable_tempo", bpm_x100=None)
    return dict(base, status="stable",
                bpm_x100=str(llround(sum(bpms) / len(bpms))))


def estimate_meter(events: Sequence[OnsetEvent]) -> Dict[str, Any]:
    """Derive a synthetic accent period (downbeat surrogate) from strengths.

    This is an offline analytic label on the synthetic fixture. It is not a
    musical downbeat detector, not a madmom model and not a listening result.
    """
    count = len(events)
    strengths = [event.strength_milli for event in events]
    base = {
        "onset_count": str(count),
        "accent_indices": [],
        "accent_period_onsets": [],
        "meter_beats": None,
        "downbeat_count": "0",
        "downbeat_phase_onset_frame": None,
        "strength_spread_milli": (
            str(max(strengths) - min(strengths)) if strengths else "0"),
    }
    if count < MIN_ONSETS_FOR_METER:
        return dict(base, status="insufficient_onsets")
    ordered = sorted(strengths)
    median = ordered[(len(ordered) - 1) // 2]
    threshold = median + ACCENT_MIN_DELTA_MILLI
    accents = [index for index, value in enumerate(strengths)
               if value >= threshold]
    periods = [later - earlier
               for earlier, later in zip(accents, accents[1:])]
    result = dict(
        base,
        accent_indices=[str(index) for index in accents],
        accent_period_onsets=[str(value) for value in periods],
        downbeat_count=str(len(accents)),
        downbeat_phase_onset_frame=(
            str(events[accents[0]].frame_index) if accents else None),
    )
    if len(accents) < 2:
        return dict(result, status="no_accented_downbeats")
    if any(value < METER_MIN_PERIOD or value > METER_MAX_PERIOD
           for value in periods):
        return dict(result, status="accent_period_out_of_range")
    if len(set(periods)) != 1:
        return dict(result, status="irregular_meter")
    return dict(result, status="stable_meter", meter_beats=str(periods[0]))


def analyze(spec: Dict[str, Any], epoch: int = DEFAULT_EPOCH) -> Dict[str, Any]:
    signal, gaps = generate_signal(spec)
    analyzer = Analyzer(epoch=epoch)
    for start in range(0, len(signal), FRAME_SAMPLES):
        block = signal[start:start + FRAME_SAMPLES]
        valid = len(block)
        padded = block + [0.0] * (FRAME_SAMPLES - valid)
        analyzer.process_frame(padded, epoch=epoch,
                               input_count=FRAME_SAMPLES, valid_count=valid)
    tempo = estimate_tempo(analyzer.events, gaps)
    meter = estimate_meter(analyzer.events)
    return {
        "signal": signal,
        "gaps": gaps,
        "analyzer": analyzer,
        "tempo": tempo,
        "meter": meter,
        "onset_frames": [event.frame_index for event in analyzer.events],
        "events": analyzer.events,
        "source_end": len(signal),
        "final_valid_count": len(signal) % FRAME_SAMPLES or FRAME_SAMPLES,
    }


def fixture_catalog(stimuli: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    catalog: Dict[str, Dict[str, str]] = {}
    for name, spec in sorted(stimuli.items()):
        catalog[name] = {
            "kind": spec["kind"],
            "length_samples": str(spec["length_samples"]),
            "full_frames": str(spec["length_samples"] // FRAME_SAMPLES),
            "final_valid_count": str(
                spec["length_samples"] % FRAME_SAMPLES or FRAME_SAMPLES),
        }
    return catalog


def _adverse_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def reject_case(case_id: str, description: str, call: Any) -> None:
        analyzer = Analyzer()
        before = analyzer.state_digest
        try:
            call(analyzer)
        except Reject as error:
            cases.append({
                "id": case_id,
                "input": description,
                "status": "rejected",
                "code": error.code,
                "qualifies": False,
                "state_unchanged": analyzer.state_digest == before,
                "onset_count": str(len(analyzer.events)),
            })
            return
        raise Reject("adverse_case_not_rejected", case_id)

    reject_case("MISS-01", "missing frame buffer (None)",
                lambda analyzer: analyzer.process_frame(None))
    reject_case("INV-01", "input_count=159 for a 160-sample buffer",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * FRAME_SAMPLES, input_count=159))
    reject_case("INV-02", "nonfinite NaN in one input sample",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * 80 + [float("nan")] + [0.0] * 79))
    reject_case("INV-03", "nonfinite +Infinity in one input sample",
                lambda analyzer: analyzer.process_frame(
                    [float("inf")] + [0.0] * 159))
    reject_case("INV-04", "short frame (159 samples)",
                lambda analyzer: analyzer.process_frame([0.0] * 159))
    reject_case("INV-05", "stale epoch 0 on an epoch-1 analyzer",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * FRAME_SAMPLES, epoch=0))
    reject_case("INV-06", "invalid final valid_count=0",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * FRAME_SAMPLES, valid_count=0))
    reject_case("INV-07", "nonzero final padding sample",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * 37 + [0.5] + [0.0] * 122, valid_count=37))
    reject_case("INV-08", "non-numeric string sample",
                lambda analyzer: analyzer.process_frame(
                    ["0.0"] + [0.0] * 159))
    reject_case("INV-09", "boolean sample value",
                lambda analyzer: analyzer.process_frame(
                    [True] + [0.0] * 159))
    reject_case("INV-10", "frame buffer is a string",
                lambda analyzer: analyzer.process_frame("0" * FRAME_SAMPLES))
    for case_id, description, kwargs in (
            ("CFG-01", "sample_rate_hz=44100", {"sample_rate_hz": 44100}),
            ("CFG-02", "channels=2", {"channels": 2}),
            ("CFG-03", "frame_samples=512", {"frame_samples": 512}),
            ("CFG-04", "sample_format=float64", {"sample_format": "float64"}),
            ("CFG-05", "negative epoch", {"epoch": -1})):
        try:
            Analyzer(**kwargs)
        except Reject as error:
            cases.append({
                "id": case_id,
                "input": description,
                "status": "rejected",
                "code": error.code,
                "qualifies": False,
                "state_unchanged": True,
                "onset_count": "0",
            })
        else:
            raise Reject("config_case_not_rejected", case_id)

    for name in ("low_snr_adverse", "tempo_out_of_range_adverse",
                 "speech_like_unfamiliar", "silence", "drift", "rebuffer",
                 "final_partial"):
        cases.append({
            "id": "ADV-" + name,
            "input": "strict synthetic stimulus " + name,
            "status": "recorded",
            "result": STIMULI[name]["kind"],
            "qualifies": False,
            "note": (
                "Adverse, control or surrogate outcome is retained; it never "
                "qualifies a candidate."
            ),
        })
    return cases


def _score(report: Dict[str, Any]) -> Dict[str, Any]:
    """Score only the synthetic fixture; passing is not release evidence."""
    checks: List[Dict[str, Any]] = []

    def check(check_id: str, expected: Any, observed: Any,
              note: str) -> None:
        checks.append({
            "id": check_id,
            "expected": expected,
            "observed": observed,
            "passed": expected == observed,
            "note": note,
        })

    tempo = report["tempo"]
    meter = report["meter"]
    rate = report["rate_profile"]
    final = rate["final_partial_window"]
    check("identity_1x_bpm", "10000",
          tempo["music_like_1x"]["bpm_x100"],
          "100 BPM at 1x, exactly 60 frames per beat")
    check("rate_0_8_bpm", "8000", tempo["rate_0_8"]["bpm_x100"],
          "event-time scaling by 0.8 gives 80 BPM")
    check("rate_1_2_bpm", "12000", tempo["rate_1_2"]["bpm_x100"],
          "event-time scaling by 1.2 gives 120 BPM")
    check("rate_duration_error", "0",
          str(rate["duration"]["max_error_samples"]),
          "exact source-sample span under each rate")
    check("meter_stable_1x", "stable_meter",
          meter["music_like_1x"]["status"],
          "accent period is stable on the 1x music surrogate")
    check("meter_beats_1x", "4",
          meter["music_like_1x"]["meter_beats"],
          "accent every four beats in the synthetic meter")
    check("downbeat_count_1x", "3",
          meter["music_like_1x"]["downbeat_count"],
          "three accented downbeats across ten beats")
    check("downbeat_phase_zero", "0",
          meter["music_like_1x"]["downbeat_phase_onset_frame"],
          "first accented downbeat starts at source frame zero")
    check("meter_stable_0_8", "4", meter["rate_0_8"]["meter_beats"],
          "rate-changed surrogate keeps the synthetic meter")
    check("speech_no_stable_tempo", True,
          tempo["speech_like_unfamiliar"]["bpm_x100"] is None
          and tempo["speech_like_unfamiliar"]["status"] != "stable",
          "unfamiliar speech surrogate has no stable beat period")
    check("speech_meter_not_stable", True,
          meter["speech_like_unfamiliar"]["status"] != "stable_meter",
          "unfamiliar speech surrogate has no stable meter")
    check("silence_no_onsets", "no_onsets", tempo["silence"]["status"],
          "silence produces no onset event")
    check("music_stable", "stable", tempo["music_like_1x"]["status"],
          "music surrogate produces a stable tempo")
    check("tempo_out_of_range", "tempo_out_of_range",
          tempo["tempo_out_of_range_adverse"]["status"],
          "300 BPM surrogate is rejected by the 60-180 BPM window")
    check("low_snr_nonqualifying", False,
          rate["low_snr_adverse"]["qualifies"],
          "adverse low-SNR result is recorded but never promoted")
    check("rebuffer_gap_suppressed", True,
          rate["rebuffer"]["cross_gap_ioi_suppressed"],
          "no tempo is estimated across the rebuffer gap")
    check("rebuffer_stable", "stable", rate["rebuffer"]["status"],
          "post-gap beat sequence is stable after suppression")
    check("rebuffer_bpm", "10000", rate["rebuffer"]["bpm_x100"],
          "rebuffer keeps the 100 BPM synthetic tempo")
    check("drift_recorded", True,
          rate["drift"]["monotonic_ioi_decrease"],
          "drift is recorded as a source-anchored IOI sequence")
    check("drift_nonqualifying", True,
          tempo["drift"]["status"] != "stable"
          and tempo["drift"]["bpm_x100"] is None,
          "drift is not promoted to a stable tempo")
    check("final_partial_valid", "37", final["valid_count"],
          "final partial frame is explicit")
    check("final_partial_event_within", False,
          final["event_beyond_source_end"],
          "final event does not extend beyond the source end")
    check("mapping_nonnegative", True,
          rate["source_output_mapping"]["min_availability_margin_ns"] >= 0,
          "no event is available before its source capture time")
    check("mapping_exact", "10000000",
          str(rate["source_output_mapping"]["min_availability_margin_ns"]),
          "one 160-sample frame of exact availability margin")
    check("transient_proxy", "-30",
          str(rate["transient_proxy"]["final_partial_error_samples"]),
          "frame-quantized onset error in the final partial frame")
    check("all_cases_explicit", True,
          all(case["qualifies"] is False
              and case["status"] in ("rejected", "recorded")
              for case in report["adverse_cases"]),
          "every adverse, missing, invalid or nonfinite case is explicit")
    check("eight_blocked_gates", True,
          len(report["gates"]) == 8
          and all(gate["status"] == "blocked" for gate in report["gates"]),
          "eight release gates remain blocked")
    check("all_gates_blocked", True,
          report["qualification"]["all_release_gates_blocked"],
          "no release gate is opened by synthetic evidence")
    check("candidate_not_qualified", True,
          report["qualification"]["status"] == "not_qualified"
          and report["qualification"]["candidate_qualified"] is False,
          "the candidate is not qualified")
    check("no_source_or_runtime", True,
          report["synthetic_reference"]["not_upstream_madmom"] is True
          and report["synthetic_reference"][
              "upstream_source_weights_or_runtime_present"] is False,
          "no madmom source, models or runtime is present")
    check("noncommercial_model_blocker_present", True,
          any(row["id"] == "pretrained_model_rights_noncommercial"
              and row["status"] == "blocked"
              and row["qualifies"] is False
              for row in report["blockers"]),
          "the non-commercial pretrained-model restriction stays blocked")
    failed = [row["id"] for row in checks if not row["passed"]]
    return {
        "passed": not failed,
        "checks": checks,
        "failed_checks": failed,
        "scope": "synthetic fixture only; not release qualification",
    }


def _qualification(checks_passed: bool = False) -> Dict[str, Any]:
    return {
        "status": QUALIFICATION,
        "candidate_qualified": False,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": 8,
        "blocked_gate_ids": [gate["id"] for gate in GATES],
        "all_release_gates_blocked": True,
        "release_results_present": False,
        "missing_result_promoted": False,
        "real_source_or_runtime_used": False,
        "listening_or_device_timing_claim": False,
        "no_missing_result_qualifies_candidate": True,
        "synthetic_profile_checks_passed": checks_passed,
        "reason": (
            "The madmom source checkout, full upstream revision, pretrained "
            "models, model configuration, exact Python/Cython runtime, "
            "verified licence, commercial model grant, rights record, "
            "held-out beat/downbeat cohort and parity vector are absent, and "
            "the merged evidence records the shipped pretrained models as "
            "non-commercial. No model output, benchmark, listening or device "
            "timing result exists."
        ),
    }


def _upstream_identity() -> Dict[str, Any]:
    return {
        "name": UPSTREAM_NAME,
        "project": UPSTREAM_PROJECT,
        "reported_source_license": UPSTREAM_REPORTED_SOURCE_LICENSE,
        "reported_models_license": UPSTREAM_REPORTED_MODELS_LICENSE,
        "reported_commercial_use": UPSTREAM_REPORTED_COMMERCIAL_USE,
        "reported_returns": UPSTREAM_REPORTED_RETURNS,
        "reported_online": UPSTREAM_REPORTED_ONLINE,
        "reported_inference_scope": UPSTREAM_REPORTED_INFERENCE_SCOPE,
        "reported_framework": UPSTREAM_REPORTED_FRAMEWORK,
        "reported_method": UPSTREAM_REPORTED_METHOD,
        "reported_contact": UPSTREAM_CONTACT,
        "license_verified": False,
        "license_file_present": False,
        "model_license_file_present": False,
        "repository_url": UPSTREAM_REPOSITORY_URL,
        "paper_url": UPSTREAM_PAPER_URL,
        "revision": UPSTREAM_REVISION,
        "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "task_geometry_status": TASK_GEOMETRY_STATUS,
        "reported_geometry_asserted": False,
        "reported_sample_rate_hz": None,
        "reported_channels": None,
    }


def _exact_scope() -> Dict[str, Any]:
    return {
        "write_scope": TASK_PREFIX + " only",
        "task_local_only": True,
        "shared_files_changed": False,
        "public_api_or_abi_changed": False,
        "headers_changed": False,
        "descriptor_registry_changed": False,
        "descriptor_default_changed": False,
        "provider_registration_changed": False,
        "installed_v0_changed": False,
        "board_handoff_ruleset_or_main_changed": False,
        "other_task_changed": False,
        "ci_changed": False,
        "shared_build_changed": False,
        "network_used": False,
        "download_performed": False,
        "real_audio_used": False,
        "weights_vendored": False,
    }


def _installed_v0() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "abi_major": ABI_MAJOR,
        "abi_minor": ABI_MINOR,
        "changed": False,
    }


def _licensing() -> Dict[str, Any]:
    return {
        "reported_source_license": UPSTREAM_REPORTED_SOURCE_LICENSE,
        "reported_models_license": UPSTREAM_REPORTED_MODELS_LICENSE,
        "reported_commercial_use": UPSTREAM_REPORTED_COMMERCIAL_USE,
        "license_verified": False,
        "source_license_text_present": False,
        "model_license_text_present": False,
        "commercial_grant_present": False,
        "commercial_use_permitted": False,
        "upstream_source_present": False,
        "upstream_weights_present": False,
        "upstream_runtime_present": False,
        "rights_cleared": False,
        "review": "blocked",
        "vendored_license_file": False,
        "task_file_spdx": "Apache-2.0",
        "reuse_aggregate_path": "docs/**",
        "note": (
            "The merged evidence reports BSD source and CC BY-NC-SA 4.0 "
            "pretrained models with commercial use 'No with shipped models' "
            "and asks callers to contact JKU. No licence text, model grant, "
            "JKU commercial permission or rights record is present. The "
            "strings are provenance only, never a task-file licence."
        ),
    }


def _scope() -> Dict[str, Any]:
    return {
        "task_local_only": True,
        "provider_registration": False,
        "processor_exposure": False,
        "public_default": False,
        "registered": False,
        "default_enabled": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "network_used": False,
        "download_performed": False,
        "real_audio_used": False,
        "real_corpus": False,
        "weights_present": False,
        "runtime_invoked": False,
        "model_executed": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
        "numeric_parity_claim": False,
    }


NON_CLAIMS: Tuple[str, ...] = (
    "No madmom source, pretrained model, model configuration or runtime is loaded or executed.",
    "No madmom, NumPy, SciPy, Cython, PyTorch or neural runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, beat/downbeat label, clean reference or listener is used.",
    "No beat F-measure, downbeat F-measure, tempo accuracy, latency, memory or RTF is measured here.",
    "The synthetic click-track/onset/meter surrogate is not madmom and cannot qualify the candidate.",
    "The reported CC BY-NC-SA 4.0 model terms are not resolved by this package; no commercial use is claimed.",
    "No provider, descriptor, registry, installed v0 path, shared build, dependency lock or CI is changed.",
    "No listening, device timing, benchmark, parity or release approval is claimed.",
)


def _reproduction() -> Dict[str, Any]:
    return {
        "cold_start_regenerations": 3,
        "run": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
        "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
        "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        "report_sha256_sidecar": "report.json.sha256",
        "sources_manifest": "SOURCES.sha256",
    }


def _artifact_requirements() -> List[Dict[str, Any]]:
    rows = (
        ("source_checkout", "source", MISSING_SOURCE_PATHS[0],
         "madmom source checkout at an immutable 40-hex revision."),
        ("upstream_revision", "source", None,
         "Full 40-hex upstream commit and per-file SHA-256 source manifest."),
        ("inference_models", "weights", MISSING_WEIGHTS_PATHS[0],
         "Exact pretrained beat/downbeat model files with byte counts and SHA-256."),
        ("model_config", "config", "data/models/madmom/model_config.json",
         "Exact model configuration and parameter metadata with SHA-256."),
        ("exact_runtime", "runtime", MISSING_RUNTIME_LOCK_PATH,
         "Isolated hash-pinned Python/Cython runtime lock on a recorded platform."),
        ("source_license_record", "rights", MISSING_LICENSE_PATH,
         "Upstream source licence text and terms at the resolved commit."),
        ("model_license_or_grant", "rights", MISSING_MODEL_LICENSE_PATH,
         "CC BY-NC-SA 4.0 model terms or an explicit JKU commercial grant."),
        ("rights_record", "rights", MISSING_RIGHTS_PATH,
         "Training-data, source-audio, label, output-use and redistribution rights."),
        ("beat_cohort", "corpus", MISSING_COHORT_PATH,
         "Rights-cleared held-out music cohort with beat, downbeat and tempo labels."),
        ("parity_vector", "evidence", MISSING_PARITY_PATH,
         "Frozen exact-runtime output vector and reference configuration."),
    )
    return [
        {
            "id": identifier,
            "kind": kind,
            "path": path,
            "required": True,
            "status": "absent",
            "sha256": None,
            "revision": None,
            "requirement": requirement,
        }
        for identifier, kind, path, requirement in rows
    ]


def build_contract() -> Dict[str, Any]:
    return {
        "spdx": dict(SPDX),
        "schema_id": CONTRACT_SCHEMA_ID,
        "protocol": PROTOCOL,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "verification_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "status": STATUS,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "qualification": _qualification(False),
        "exact_scope": _exact_scope(),
        "installed_v0": _installed_v0(),
        "licensing": _licensing(),
        "upstream_identity": _upstream_identity(),
        "artifact_requirements": _artifact_requirements(),
        "absence_probes": list(ABSENCE_PROBES),
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "board_row": dict(BOARD_ROW),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "reopen_condition": (
            "Pin the exact madmom source and immutable revision, admit "
            "hash-pinned pretrained models and an isolated Python/Cython "
            "runtime, resolve the CC BY-NC-SA 4.0 model restriction with an "
            "explicit JKU commercial grant or permissively licensed "
            "replacement weights, clear all corpus and output rights, "
            "reproduce exact beat/downbeat/tempo outputs, score a "
            "rights-cleared held-out cohort, measure target timing and "
            "complete opt-in provider intake. Until then the candidate stays "
            "DEFER, incomplete and not qualified."
        ),
        "scope": _scope(),
        "non_claims": list(NON_CLAIMS),
        "remaining_gates": [gate["requirement"] for gate in GATES],
        "reproduction": _reproduction(),
    }


_CONTRACT_KEYS = {
    "spdx", "schema_id", "protocol", "task", "title", "component",
    "repository", "mode", "verification_profile", "base_commit", "branch",
    "reviewer", "worktree", "status", "decision", "evidence_status",
    "defer_before", "proposal_only", "qualification", "exact_scope",
    "installed_v0", "licensing", "upstream_identity", "artifact_requirements",
    "absence_probes", "caller_asset_contract", "board_row", "gates",
    "exact_blockers", "reopen_condition", "scope", "non_claims",
    "remaining_gates", "reproduction",
}
_QUALIFICATION_KEYS = {
    "status", "candidate_qualified", "decision", "evidence_status",
    "defer_before", "blocked_gate_count", "blocked_gate_ids",
    "all_release_gates_blocked", "release_results_present",
    "missing_result_promoted", "real_source_or_runtime_used",
    "listening_or_device_timing_claim",
    "no_missing_result_qualifies_candidate", "synthetic_profile_checks_passed",
    "reason",
}
_SCOPE_FALSE_FLAGS = (
    "shared_files_changed", "public_api_or_abi_changed", "headers_changed",
    "descriptor_registry_changed", "descriptor_default_changed",
    "provider_registration_changed", "installed_v0_changed",
    "board_handoff_ruleset_or_main_changed", "other_task_changed",
    "ci_changed", "shared_build_changed", "network_used",
    "download_performed", "real_audio_used", "weights_vendored",
)


def validate_contract(contract: Dict[str, Any]) -> None:
    _exact_keys(contract, _CONTRACT_KEYS, "contract")
    if contract["spdx"] != SPDX or contract["schema_id"] != CONTRACT_SCHEMA_ID:
        raise Reject("contract_identity_mismatch", "spdx/schema")
    if contract["protocol"] != PROTOCOL:
        raise Reject("contract_identity_mismatch", "protocol")
    expected = {
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "verification_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "status": STATUS,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
    }
    for key, value in expected.items():
        if contract[key] != value:
            raise Reject("contract_field_mismatch", key)
    qualification = contract["qualification"]
    _exact_keys(qualification, _QUALIFICATION_KEYS, "contract.qualification")
    if (qualification["status"] != QUALIFICATION
            or qualification["candidate_qualified"] is not False
            or qualification["decision"] != DECISION
            or qualification["evidence_status"] != EVIDENCE_STATUS
            or qualification["blocked_gate_count"] != 8
            or qualification["blocked_gate_ids"] != [gate["id"] for gate in GATES]
            or qualification["all_release_gates_blocked"] is not True
            or qualification["synthetic_profile_checks_passed"] is not False
            or any(qualification[key] is not False for key in
                   ("release_results_present", "missing_result_promoted",
                    "real_source_or_runtime_used",
                    "listening_or_device_timing_claim"))
            or qualification["no_missing_result_qualifies_candidate"] is not True):
        raise Reject("contract_qualification_mismatch", "qualification")
    scope = contract["exact_scope"]
    if scope["write_scope"] != TASK_PREFIX + " only":
        raise Reject("contract_write_scope_mismatch", "write_scope")
    if scope["task_local_only"] is not True:
        raise Reject("contract_scope_mismatch", "task_local_only")
    for key in _SCOPE_FALSE_FLAGS:
        if scope[key] is not False:
            raise Reject("contract_scope_mismatch", key)
    installed = contract["installed_v0"]
    if installed != _installed_v0():
        raise Reject("contract_installed_v0_mismatch", "installed_v0")
    upstream = contract["upstream_identity"]
    if (upstream != _upstream_identity()
            or upstream["revision"] is not None
            or upstream["revision_pin_available"] is not False
            or upstream["license_verified"] is not False
            or upstream["task_geometry_status"] != TASK_GEOMETRY_STATUS
            or upstream["reported_geometry_asserted"] is not False):
        raise Reject("contract_upstream_overclaim", "upstream_identity")
    if contract["licensing"] != _licensing():
        raise Reject("contract_licensing_mismatch", "licensing")
    requirements = contract["artifact_requirements"]
    if (len(requirements) != 10
            or any(row["required"] is not True or row["status"] != "absent"
                   or row["sha256"] is not None or row["revision"] is not None
                   for row in requirements)):
        raise Reject("contract_artifact_requirements_mismatch", "artifacts")
    if contract["absence_probes"] != list(ABSENCE_PROBES):
        raise Reject("contract_absence_probes_mismatch", "absence_probes")
    caller = contract["caller_asset_contract"]
    if (caller != CALLER_ASSET_CONTRACT
            or caller["asset_is_vendored"] is not False
            or caller["asset_is_caller_owned"] is not True):
        raise Reject("contract_caller_asset_mismatch", "caller_asset_contract")
    board = contract["board_row"]
    if (board["stable_sha256"] != STABLE_SHA256
            or board["stable_fields"] != STABLE_FIELDS
            or board["whole_file_hashed"] is not False
            or board["excluded_mutable_fields"] != list(MUTABLE_TASK_FIELDS)):
        raise Reject("contract_board_row_mismatch", "board_row")
    gates = contract["gates"]
    if (len(gates) != 8
            or [gate["id"] for gate in gates] != [gate["id"] for gate in GATES]
            or any(gate["status"] != "blocked" for gate in gates)):
        raise Reject("contract_gates_mismatch", "gates")
    blockers = contract["exact_blockers"]
    if (len(blockers) != 8
            or [row["id"] for row in blockers] != [row["id"] for row in EXACT_BLOCKERS]
            or any(row["status"] != "blocked" or row["qualifies"] is not False
                   for row in blockers)):
        raise Reject("contract_blockers_mismatch", "exact_blockers")
    if contract["scope"] != _scope():
        raise Reject("contract_scope_claim_mismatch", "scope")
    if contract["remaining_gates"] != [gate["requirement"] for gate in GATES]:
        raise Reject("contract_remaining_gates_mismatch", "remaining_gates")
    if contract["non_claims"] != list(NON_CLAIMS):
        raise Reject("contract_non_claims_mismatch", "non_claims")
    if not isinstance(contract["reopen_condition"], str) or not contract["reopen_condition"]:
        raise Reject("contract_reopen_condition_missing", "reopen_condition")
    if contract["reproduction"] != _reproduction():
        raise Reject("contract_reproduction_mismatch", "reproduction")


def build_report() -> Dict[str, Any]:
    """Build the canonical blocker report from pinned, read-only inputs."""
    contract = build_contract()
    validate_contract(contract)
    validate_stimuli(STIMULI)
    audit = audit_assets()
    if audit["all_absence_probes_absent"] is not True:
        raise Reject("unexpected_candidate_asset_present",
                     "an absence probe now exists; re-evaluate the candidate")
    source_pins, boundary_pins = _pin_rows()
    analyses = {name: analyze(spec) for name, spec in sorted(STIMULI.items())}
    tempo = {name: value["tempo"] for name, value in sorted(analyses.items())}
    meter = {name: value["meter"] for name, value in sorted(analyses.items())}

    stimuli: Dict[str, Dict[str, Any]] = {}
    for name, value in sorted(analyses.items()):
        stimuli[name] = {
            "length_samples": str(len(value["signal"])),
            "frames": str(
                (len(value["signal"]) + FRAME_SAMPLES - 1) // FRAME_SAMPLES),
            "final_valid_count": str(value["final_valid_count"]),
            "float32_sha256": signal_digest(value["signal"]),
            "finite": all(math.isfinite(sample) for sample in value["signal"]),
            "bounded": all(abs(sample) <= 1.0 for sample in value["signal"]),
            "excluded_gap_samples": [
                [str(start), str(end)] for start, end in value["gaps"]],
        }

    durations: Dict[str, Dict[str, str]] = {}
    for name in ("music_like_1x", "rate_0_8", "rate_1_2"):
        frames = analyses[name]["onset_frames"]
        period = STIMULI[name]["period_samples"]
        expected_span = (len(frames) - 1) * period
        observed_span = (frames[-1] - frames[0]) * FRAME_SAMPLES
        durations[name] = {
            "onset_count": str(len(frames)),
            "period_samples": str(period),
            "expected_span_samples": str(expected_span),
            "observed_span_samples": str(observed_span),
            "error_samples": str(observed_span - expected_span),
        }
    rate_changes = [
        {"stimulus": name, "expected_bpm_x100": expected_bpm,
         "observed_bpm_x100": tempo[name]["bpm_x100"]}
        for name, expected_bpm in (
            ("rate_0_8", "8000"),
            ("music_like_1x", "10000"),
            ("rate_1_2", "12000"),
        )
    ]
    drift_iois = [int(value) for value in tempo["drift"]["ioi_frames"]]
    drift_decreasing = len(drift_iois) >= 4 and all(
        later < earlier for earlier, later in zip(drift_iois, drift_iois[1:]))
    rebuffer_onsets = analyses["rebuffer"]["onset_frames"]
    rebuffer_gap = analyses["rebuffer"]["gaps"][0]
    cross_gap = [
        (first, second)
        for first, second in zip(rebuffer_onsets, rebuffer_onsets[1:])
        if rebuffer_gap[0]
        <= (first + second) * FRAME_SAMPLES // 2
        < rebuffer_gap[1]
    ]
    final_events = analyses["final_partial"]["events"]
    margins = [
        event.available_monotonic_ns - event.capture_first_ns
        for events in (value["events"] for value in analyses.values())
        for event in events
    ]
    rate_profile = {
        "identity_1x": {
            "stimulus": "music_like_1x",
            "bpm_x100": tempo["music_like_1x"]["bpm_x100"],
        },
        "rate_changes": rate_changes,
        "duration": {
            "cases": durations,
            "max_error_samples": max(
                abs(int(row["error_samples"])) for row in durations.values()),
        },
        "source_output_mapping": {
            "audio_output_produced": False,
            "analysis_event_source_anchor": True,
            "frame_hop_samples": str(FRAME_SAMPLES),
            "available_ns_per_frame": str(FRAME_NS),
            "min_availability_margin_ns": min(margins) if margins else 0,
            "note": (
                "No audio output, playback actuator, device clock or wall "
                "clock is claimed."
            ),
        },
        "pitch": {
            "status": "not_measurable_analysis_only",
            "qualifies": False,
            "note": (
                "Beat/downbeat analysis does not alter pitch; no pitch-shift "
                "claim is made."
            ),
        },
        "transient_proxy": {
            "final_partial_error_samples": (
                final_events[0].source_start - STIMULI["final_partial"]["onset_sample"]
                if final_events else None),
            "note": (
                "Frame-quantized onset timing proxy only; not transient "
                "audibility or listening."
            ),
        },
        "playback_buffering": {
            "device_buffer_measured": False,
            "sdk_worker_count": "0",
            "sdk_queue_depth": "0",
            "analysis_frame_aggregation_samples": str(FRAME_SAMPLES),
            "final_partial_valid_count": str(FINAL_PARTIAL_VALID),
            "final_padding_zero_verified": True,
        },
        "speech_unfamiliar": {
            "stimulus": "speech_like_unfamiliar",
            "status": tempo["speech_like_unfamiliar"]["status"],
            "qualifies": False,
        },
        "speech_preservation": {
            "status": "not_measured",
            "qualifies": False,
            "note": "No real speech, listening or speech-preservation measurement exists.",
        },
        "music": {
            "stimulus": "music_like_1x",
            "status": tempo["music_like_1x"]["status"],
            "bpm_x100": tempo["music_like_1x"]["bpm_x100"],
        },
        "silence": {
            "stimulus": "silence",
            "status": tempo["silence"]["status"],
        },
        "meter": {
            "stimulus": "music_like_1x",
            "status": meter["music_like_1x"]["status"],
            "meter_beats": meter["music_like_1x"]["meter_beats"],
            "downbeat_count": meter["music_like_1x"]["downbeat_count"],
            "downbeat_phase_onset_frame": meter["music_like_1x"][
                "downbeat_phase_onset_frame"],
            "accent_period_onsets": meter["music_like_1x"][
                "accent_period_onsets"],
            "note": (
                "Analytic accent-period surrogate on a synthetic click track; "
                "not a musical downbeat detection or model output."
            ),
        },
        "rebuffer": {
            "gap_samples": [
                [str(start), str(end)] for start, end in analyses["rebuffer"]["gaps"]],
            "excluded_ioi_count": tempo["rebuffer"]["excluded_ioi_count"],
            "cross_gap_ioi_suppressed": (
                bool(cross_gap)
                and int(tempo["rebuffer"]["excluded_ioi_count"]) == len(cross_gap)),
            "status": tempo["rebuffer"]["status"],
            "bpm_x100": tempo["rebuffer"]["bpm_x100"],
        },
        "drift": {
            "ioi_frames": tempo["drift"]["ioi_frames"],
            "monotonic_ioi_decrease": drift_decreasing,
            "status": tempo["drift"]["status"],
            "note": "Source-anchored IOI sequence, not a fixed global BPM claim.",
        },
        "final_partial_window": {
            "length_samples": str(len(analyses["final_partial"]["signal"])),
            "valid_count": str(analyses["final_partial"]["final_valid_count"]),
            "event_source_end": (
                str(final_events[0].source_end) if final_events else None),
            "event_beyond_source_end": bool(
                final_events
                and final_events[0].source_end
                > len(analyses["final_partial"]["signal"])),
            "event_digest": object_digest(
                [event.as_dict() for event in final_events]),
        },
        "low_snr_adverse": {
            "stimulus": "low_snr_adverse",
            "status": tempo["low_snr_adverse"]["status"],
            "qualifies": False,
        },
    }

    adverse = _adverse_cases()
    report: Dict[str, Any] = {
        "spdx": dict(SPDX),
        "schema_id": REPORT_SCHEMA_ID,
        "protocol": PROTOCOL,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "verification_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "status": STATUS,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "exact_scope": dict(contract["exact_scope"]),
        "installed_v0": dict(contract["installed_v0"]),
        "licensing": dict(contract["licensing"]),
        "scope": dict(contract["scope"]),
        "upstream_identity": dict(contract["upstream_identity"]),
        "artifact_requirements": [dict(row) for row in contract["artifact_requirements"]],
        "absence_audit": audit,
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "board_row": dict(contract["board_row"]),
        "contract_sha256": object_digest(contract),
        "synthetic_reference": {
            "algorithm": (
                "original deterministic log-energy onset detector with EWMA "
                "baseline, source-anchored IOI tempo, analytic accent-period "
                "meter and synthetic click-track stimuli"
            ),
            "not_upstream_madmom": True,
            "upstream_source_weights_or_runtime_present": False,
            "real_audio_or_corpus_used": False,
            "listening_or_device_timing_claim": False,
            "network_used": False,
            "sample_rate_hz": str(SAMPLE_RATE_HZ),
            "frame_samples": str(FRAME_SAMPLES),
            "onset_threshold": str(ONSET_THRESHOLD),
            "min_onset_gap_frames": str(MIN_ONSET_GAP_FRAMES),
            "accent_min_delta_milli": str(ACCENT_MIN_DELTA_MILLI),
            "tempo_window_bpm": [
                str(TEMPO_MIN_BPM_X100 // 100),
                str(TEMPO_MAX_BPM_X100 // 100),
            ],
        },
        "caller_asset_contract": dict(contract["caller_asset_contract"]),
        "fixtures": fixture_catalog(STIMULI),
        "stimuli": stimuli,
        "tempo": tempo,
        "meter": meter,
        "rate_profile": rate_profile,
        "adverse_cases": adverse,
        "gates": [dict(gate) for gate in contract["gates"]],
        "blockers": [dict(row) for row in contract["exact_blockers"]],
        "remaining_gates": list(contract["remaining_gates"]),
        "non_claims": list(contract["non_claims"]),
        "reproduction": dict(contract["reproduction"]),
        "qualification": _qualification(False),
    }
    report["profile_scoring"] = _score(report)
    report["qualification"] = _qualification(
        report["profile_scoring"]["passed"])
    if not report["profile_scoring"]["passed"]:
        raise Reject("profile_scoring_failed",
                     ",".join(report["profile_scoring"]["failed_checks"]))
    return report


if object_digest(STABLE_FIELDS) != STABLE_SHA256:
    raise RuntimeError("stable linked-row identity drift")
