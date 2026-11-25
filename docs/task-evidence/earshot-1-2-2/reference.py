# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-EARSHOT-1-2-2.

This module is NOT Earshot.  It does not import, load, build or execute the
Earshot wheel, its embedded weights or a native runtime.  It does not read
audio, download anything, measure a device clock, conduct listening, benchmark
the SDK or qualify a release.  It models the *boundary* of Earshot 1.2.2 as a
caller-supplied 16 kHz / 256-sample wheel asset and executes a deterministic
model-free frame RMS/zero-crossing VAD surrogate when that asset is absent.
Every quality gate remains blocked; the surrogate is a conformance fixture.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import fixture
import scorer

HERE = fixture.TASK_DIR
SDK_ROOT = fixture.SDK_ROOT

TASK = "SDK-EARSHOT-1-2-2"
TITLE = "Earshot 1.2.2"
SLUG = "earshot-1-2-2"
COMPONENT = "earshot-1-2-2"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d5b11912cd09e87296cd9d4654f1917c9cb94258"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "analysis"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

UPSTREAM_REPOSITORY = "https://github.com/pykeio/earshot"
UPSTREAM_COMMIT = "c400f15bd232dda30a297eec90235bd09066cab7"
UPSTREAM_VERSION = "1.2.2"
UPSTREAM_LICENSE = "MIT OR Apache-2.0"
UPSTREAM_PYPI_RELEASE_DATE = "2026-08-19"
WHEEL_FILENAME = "earshot-1.2.2-cp38-abi3-macosx_11_0_arm64.whl"
WHEEL_PATH = "data/wheels/vad-candidates/" + WHEEL_FILENAME
WHEEL_SHA256 = "bf696faad73a996c40bea8115622a5dcbc9c6da01498885bfd9eae8be1a11ecd"
SOURCE_ARCHIVE_SHA256 = (
    "a2aad72917334d2b9e7385b73dc837bd30244714ccf27d45fbfcc0e038cfcaeb")
RUNTIME_ENV_PATH = "data/envs/earshot-vad-1.2.2"
NUMPY_VERSION = "2.4.6"
NUMPY_WHEEL_SHA256 = (
    "4cfe66903cc32a9921a6733d96b19bb6abf310397581bbad89c228f5abaf0ee8")
ADAPTER_PATH = "adapters/earshot-vad/adapter.json"
ADAPTER_RUN_PATH = "adapters/earshot-vad/run.py"

LOCAL_PIN_PATHS = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "contract.json",
    "contract.json.license",
    "fixture.py",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "requirements.lock",
    "requirements.lock.license",
    "run.py",
    "scorer.py",
    "test_reference.py",
    "verify.py",
)
LOCAL_ARTIFACT_PATHS = tuple(
    name for name in LOCAL_PIN_PATHS if name != "README.md")

REQUIRED_ASSET_FIELDS = {
    "wheel_path",
    "wheel_sha256",
    "source_commit",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "threshold",
    "input_format",
}
PINNED_ASSET_VALUES: Dict[str, Any] = {
    "source_commit": UPSTREAM_COMMIT,
    "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
    "channels": 1,
    "frame_samples": fixture.FRAME_SAMPLES,
    "threshold": 0.5,
    "input_format": "float32",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/earshot-1-2-2/caller-supplied-asset/0.1",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": dict(PINNED_ASSET_VALUES),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "wheel_path is a caller-owned absolute path",
        "SHA-256 of the wheel file matches the manifest",
        "source_commit equals the pinned pykeio/earshot provenance revision",
        "sample rate, channels, frame size, threshold and input format equal "
        "16 kHz mono float32 256-sample geometry at threshold 0.5",
        "no download, copy, build, import, load or execution occurs in this package",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hash_and_geometry_only; do_not_import_or_execute_in_this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "weights_embedded_in_wheel": True,
    "separate_model_asset_required": False,
}

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": 16000,
    "sdk_v0_channels": 1,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": 160,
    "asset_sample_rate_hz": fixture.SAMPLE_RATE_HZ,
    "asset_channels": 1,
    "asset_sample_format": "float32",
    "asset_frame_samples": fixture.FRAME_SAMPLES,
    "asset_frame_duration_ms": fixture.FRAME_DURATION_MS,
    "decision_threshold": 0.5,
    "window_samples": fixture.TOTAL_SAMPLES,
    "window_frames": fixture.TOTAL_FRAMES,
    "sdk_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
    "frame_cadence_parity_with_real_runtime_claimed": False,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "ci_change": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_boundary_surrogate_only": True,
    "caller_supplied_asset_contract_modeled": True,
    "caller_supplied_asset_present": False,
    "earshot_source_executed": False,
    "earshot_runtime_executed": False,
    "earshot_wheel_imported": False,
    "wheel_downloaded": False,
    "wheel_loaded": False,
    "model_weights_loaded": False,
    "real_audio": False,
    "real_labels": False,
    "network_used": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "earshot_wheel_imported": False,
    "earshot_runtime_executed": False,
    "earshot_model_loaded": False,
    "model_weights_downloaded": False,
    "model_weights_redistributed": False,
    "real_audio_used": False,
    "listening_performed": False,
    "device_timing_measured": False,
    "benchmark_result": False,
    "release_claim": False,
    "provider_registered": False,
    "public_default_changed": False,
    "installed_v0_changed": False,
    "descriptor_changed": False,
    "registry_changed": False,
    "abi_changed": False,
    "shared_build_changed": False,
    "ci_changed": False,
    "board_or_handoff_changed": False,
    "quality_pass": False,
    "exact_earshot_reproduction_claimed": False,
    "numeric_parity_with_real_runtime_claimed": False,
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_version": UPSTREAM_VERSION,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_expression_source": (
        "PyPI 1.2.2 package metadata transcribed in "
        "research/plans/F02/vad_sources.md; no standalone license file is "
        "bundled in the wheel"),
    "pypi_release_date": UPSTREAM_PYPI_RELEASE_DATE,
    "pypi_project": "https://pypi.org/project/earshot/1.2.2/",
    "source_archive": {
        "name": "earshot-1.2.2 source archive",
        "sha256": SOURCE_ARCHIVE_SHA256,
        "present_in_workspace": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "wheel": {
        "filename": WHEEL_FILENAME,
        "expected_path": WHEEL_PATH,
        "sha256": WHEEL_SHA256,
        "python_requires": ">=3.8",
        "abi": "cp38-abi3",
        "platform": "macosx_11_0_arm64",
        "present_in_sdk_worktree": False,
        "present_in_research_workspace": False,
        "verified": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "imported_or_executed": False,
        "weights": "embedded-in-wheel",
    },
    "runtime_environment": {
        "expected_path": RUNTIME_ENV_PATH,
        "present": False,
        "built_by_this_package": False,
        "python": "3.11.5 arm64",
        "numpy": NUMPY_VERSION,
        "numpy_wheel_sha256": NUMPY_WHEEL_SHA256,
        "used_by_this_package": False,
    },
    "public_adapter": {
        "path": "adapters/earshot-vad",
        "descriptor_path": ADAPTER_PATH,
        "entrypoint_path": ADAPTER_RUN_PATH,
        "declared_output_kinds": ["annotation"],
        "declared_tasks": ["DET-01"],
        "declared_modes": ["offline", "streaming"],
        "declared_weights": "embedded-in-wheel",
        "declared_sample_rate": 16000,
        "declared_frame_samples": 256,
        "declared_threshold": 0.5,
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "upstream_source_checkout_present": False,
    "training_data_provenance": "not established in this package",
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_package_license_expression": UPSTREAM_LICENSE,
    "upstream_license_expression_source": (
        "PyPI 1.2.2 metadata and the task-local research pin in "
        "research/plans/F02/vad_sources.md"),
    "standalone_license_file_in_wheel": False,
    "source_archive_pinned": True,
    "source_archive_redistribution_clearance": False,
    "wheel_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "wheel_and_embedded_weight_rights",
    "conclusion": (
        "The package metadata declares MIT OR Apache-2.0, but no standalone "
        "license file is bundled in the wheel, the wheel and its embedded "
        "weights are absent, and redistribution/product-use terms plus "
        "training-data provenance have no independent review. This package "
        "redistributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The exact Earshot 1.2.2 macOS arm64 wheel is pinned by SHA-256 "
        "(bf696faad73a996c40bea8115622a5dcbc9c6da01498885bfd9eae8be1a11ecd) but "
        "is absent from this workspace at data/wheels/vad-candidates/"
        "earshot-1.2.2-cp38-abi3-macosx_11_0_arm64.whl, and no isolated "
        "environment exists at data/envs/earshot-vad-1.2.2; the exact runtime "
        "cannot be installed, loaded or reproduced here."),
    (
        "The wheel metadata declares MIT OR Apache-2.0, but the wheel bundles "
        "no standalone license file, embedded-weight and training-data "
        "provenance are not independently established, and redistribution, "
        "product-use and legal review remain unresolved. No asset was "
        "downloaded, copied, built, vendored or redistributed."),
    (
        "Only a deterministic model-free boundary surrogate was executed. It "
        "is not Earshot, has no neural network or weights, and its synthetic "
        "probabilities, FN/FP and boundary delays are boundary-conformance "
        "observations, not an accuracy, real-audio, listening, device-timing or "
        "benchmark result."),
    (
        "No rights-cleared label-complete real cohort, held-out generalization, "
        "target-runtime timing/memory, native streaming integration, opt-in "
        "provider intake, descriptor/registry review or public default decision "
        "exists; every release gate remains blocked."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "caller_supplied_wheel_present_and_verified",
        "Supply the caller-owned Earshot 1.2.2 macOS arm64 wheel with SHA-256 "
        "bf696f... and the pinned provenance commit, then validate the manifest."),
    (
        "wheel_and_embedded_weight_rights",
        "Establish wheel, embedded-weight and training-data redistribution and "
        "product-use rights with a recorded review; the declared MIT OR "
        "Apache-2.0 expression alone is not a legal clearance."),
    (
        "exact_runtime_reproduction",
        "Install or load the exact pinned wheel in an isolated environment and "
        "reproduce an approved reference posterior vector without downloading "
        "weights or using uncleared audio."),
    (
        "streaming_boundary_conformance",
        "Verify the native 16 kHz / 256-sample streaming boundary, partial-tail "
        "padding and clipping, reset/flush behavior and offline/streaming "
        "parity against the exact runtime."),
    (
        "rights_cleared_label_complete_cohort",
        "Score a rights-cleared held-out cohort with complete speech and "
        "nonspeech labels, explicit unknown regions, session/speaker "
        "partitioning and stratified failure accounting."),
    (
        "target_runtime_timing_memory",
        "Measure content/availability timing, memory and deadlines on the exact "
        "target runtime and device."),
    (
        "opt_in_adapter_intake",
        "Complete rights review and opt-in adapter intake before any descriptor "
        "or provider registration."),
    (
        "descriptor_registry_review",
        "Review the adapter descriptor, registry entry and installed-v0 "
        "compatibility; no registration or default is currently proposed."),
    (
        "public_default_selection",
        "Record an explicit public default decision; the candidate is currently "
        "unregistered and OFF."),
)

MISSING_EVIDENCE: List[str] = [
    "caller-supplied Earshot 1.2.2 wheel present and SHA-256-verified in this workspace",
    "isolated environment and wheel import proving the exact runtime identity",
    "embedded-weight, training-data, redistribution and product-use rights clearance",
    "approved reference posterior vector or exact-runtime parity record",
    "native 16 kHz / 256-sample streaming boundary, partial-tail and reset evidence",
    "rights-cleared held-out cohort with complete speech/nonspeech labels and unknown regions",
    "held-out generalization and per-recording uncertainty",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and registry review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies the pinned Earshot 1.2.2 macOS arm64 wheel with matching "
    "SHA-256 and provenance commit, and the manifest validates.",
    "Wheel, embedded-weight, training-data, redistribution and product-use "
    "rights are cleared with a recorded review.",
    "The exact pinned wheel is installed in an isolated environment and an "
    "approved reference posterior vector is reproduced.",
    "The native 16 kHz / 256-sample streaming boundary, partial-tail padding "
    "and clipping, reset/flush behavior and offline/streaming parity are verified.",
    "A rights-cleared held-out cohort with complete labels and explicit unknown "
    "regions is scored under the Analysis profile.",
    "Held-out generalization and per-recording uncertainty are reported.",
    "Target-runtime content/availability timing, memory and deadlines are measured.",
    "Opt-in adapter intake, descriptor and registry review are completed.",
    "An explicit public default decision is recorded; the candidate remains OFF "
    "until then.",
]

SOURCE_REPORTED: Dict[str, Any] = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "scope": (
        "Held-out AMI replay over three speaker-disjoint meetings, projected onto "
        "20 ms scheduler frames; exploratory integration and accuracy screening, "
        "not a representative holdout, target-device run or product claim."),
    "sources": [
        "research/voice-enhancement-20261101/candidate_matrix.csv",
        "reports/vad-research/chaining-evaluation.md",
        "reports/vad-research/chaining-evaluation-status.json",
        "reports/vad-research/attempt-earshot-20261028-01/findings.md",
        "reports/vad-research/20261028-synthesis-v6.md",
        "REALTIME_COMPONENT_CANDIDATES.md",
    ],
    "findings": [
        {"metric": "false_negative_rate", "value": 0.2432, "unit": "ratio"},
        {"metric": "false_positive_rate", "value": 0.1030, "unit": "ratio"},
        {"metric": "missed_speech", "value": 752.3, "unit": "s"},
        {"metric": "false_speech", "value": 101.1, "unit": "s"},
        {"metric": "average_cost_per_20ms_frame", "value": 13.41, "unit": "us"},
        {"metric": "median_onset_delay", "value": 430, "unit": "ms"},
        {"metric": "median_offset_delay", "value": -580, "unit": "ms"},
        {"metric": "integration_activity_fraction", "value": 0.4824, "unit": "ratio"},
        {"metric": "integration_offline_streaming_parity", "value": "exact",
         "unit": "status"},
    ],
    "note": (
        "Transcribed from the pinned research only. This package neither "
        "reproduces nor claims these values and does not pool them with the "
        "surrogate observations."),
}

ACCEPTANCE_PROFILE_ITEMS = (
    "timestamped_probabilities_scored",
    "event_boundaries_scored",
    "detections_scored",
    "quiet_and_active_speech",
    "idle_noise",
    "known_positives_and_negatives",
    "onset_offset_delay",
    "stratified_fn_fp",
    "validity_separate_from_nonspeech",
    "independent_state",
    "exact_source_intervals",
    "availability",
    "dropped_and_stale_events",
    "cross_hop",
)

MISSING = object()
EXPLICIT_MISSING = "explicit_missing_token"
VALIDITIES = {"known", "unknown", "invalid", "missing"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return fixture.canonical_bytes(value)


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("non_finite:" + value)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    """Validate a caller-owned wheel manifest without importing or executing it."""
    if not isinstance(manifest, dict):
        raise ValueError("asset_manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("asset_manifest_fields")
    for key, expected in PINNED_ASSET_VALUES.items():
        if manifest[key] != expected:
            raise ValueError("asset_value_mismatch:" + key)
    path = Path(str(manifest["wheel_path"]))
    if not path.is_absolute():
        raise ValueError("asset_path_must_be_absolute")
    if not path.is_file():
        raise ValueError("asset_wheel_missing")
    if fixture.sha256_file(path) != manifest["wheel_sha256"]:
        raise ValueError("asset_hash_mismatch")
    return {
        "verified": True,
        "loaded": False,
        "executed": False,
        "imported": False,
        "source_commit": UPSTREAM_COMMIT,
        "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": fixture.FRAME_SAMPLES,
        "threshold": 0.5,
        "input_format": "float32",
    }


class Session:
    """Independent, epoch-scoped VAD analysis session with explicit audit."""

    def __init__(self, config: Dict[str, Any], session_id: str, epoch: int) -> None:
        fixture.validate_config(config)
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self.config = config
        self.session_id = session_id
        self.epoch = epoch
        self._reset(epoch)

    def _reset(self, epoch: int) -> None:
        self.epoch = epoch
        self.events: List[Dict[str, Any]] = []
        self.speech_events: List[Dict[str, Any]] = []
        self.rejections: List[Dict[str, Any]] = []
        self.dropped: List[Dict[str, Any]] = []
        self.total_samples = 0
        self.frame_index = 0
        self.next_sequence = 1
        self.active_start: int | None = None

    def reset(self, epoch: int) -> Dict[str, Any]:
        previous = self.epoch
        self._reset(epoch)
        return {"status": "ok", "operation": "reset", "previous_epoch": previous,
                "epoch": self.epoch, "session_id": self.session_id}

    def available_ns(self, end_sample: int) -> int:
        return (self.config["origin_ns"]
                + end_sample * self.config["sample_period_ns"]
                + self.config["processing_delay_ns"])

    def _reject(self, reason: str, epoch: int | None,
                start_sample: int | None) -> Dict[str, Any]:
        before = self.summary()
        record = {"status": "rejected", "reason": reason, "epoch": epoch,
                  "start_sample": start_sample, "session_id": self.session_id,
                  "state_digest_before": before["state_digest"]}
        self.rejections.append(record)
        record["state_digest_after"] = self.summary()["state_digest"]
        if record["state_digest_after"] != record["state_digest_before"]:
            raise AssertionError("rejection_mutated_state:" + reason)
        return record

    def process_frame(
        self,
        frame: Any,
        *,
        epoch: int | None = None,
        validity: str = "known",
        probability: float | object = MISSING,
        start_sample: int | None = None,
        end_sample: int | None = None,
        available_ns: int | None = None,
        clock: str | None = None,
        sequence: int | None = None,
        is_final: bool = False,
        valid_samples: int | None = None,
    ) -> Dict[str, Any]:
        if epoch is None:
            epoch = self.epoch
        if epoch != self.epoch:
            return self._reject("stale_epoch", epoch, start_sample)
        if validity not in VALIDITIES:
            return self._reject("unknown_validity_token", epoch, start_sample)
        if validity in ("invalid", "missing"):
            return self._reject("invalid_event_validity" if validity == "invalid"
                                else "missing_event_validity", epoch, start_sample)
        if not isinstance(frame, (list, tuple)) or not frame:
            return self._reject("wrong_frame_format", epoch, start_sample)
        if any(isinstance(value, bool) or not isinstance(value, (int, float))
               for value in frame):
            return self._reject("wrong_frame_format", epoch, start_sample)
        if any(not math.isfinite(float(value)) for value in frame):
            return self._reject("nonfinite_frame", epoch, start_sample)

        if is_final:
            if (isinstance(valid_samples, bool) or not isinstance(valid_samples, int)
                    or not 1 <= valid_samples <= self.config["frame_samples"]):
                return self._reject("invalid_final_valid_samples", epoch, start_sample)
            if len(frame) != valid_samples:
                return self._reject("final_frame_length_mismatch", epoch, start_sample)
            expected_samples = valid_samples
            padded = [float(value) for value in frame] + [
                0.0] * (self.config["frame_samples"] - valid_samples)
            padded_samples = self.config["frame_samples"] - valid_samples
        else:
            if valid_samples is not None:
                return self._reject("unexpected_valid_samples", epoch, start_sample)
            if len(frame) != self.config["frame_samples"]:
                return self._reject(
                    "short_frame" if len(frame) < self.config["frame_samples"]
                    else "long_frame", epoch, start_sample)
            expected_samples = self.config["frame_samples"]
            padded = [float(value) for value in frame]
            padded_samples = 0

        if (start_sample != self.total_samples
                or end_sample != self.total_samples + expected_samples):
            return self._reject("wrong_source_interval", epoch, start_sample)
        if clock is not None and clock != self.config["clock"]:
            return self._reject("wrong_clock", epoch, start_sample)
        if sequence is not None and sequence != self.next_sequence:
            return self._reject("duplicate_or_out_of_order_sequence", epoch, start_sample)

        if probability is MISSING:
            value = fixture.probability_for_frame(padded)
        elif probability == EXPLICIT_MISSING:
            return self._reject("missing_probability", epoch, start_sample)
        elif isinstance(probability, bool) or not isinstance(probability, (int, float)):
            return self._reject("missing_probability", epoch, start_sample)
        elif not math.isfinite(float(probability)):
            return self._reject("nonfinite_probability", epoch, start_sample)
        elif not 0.0 <= float(probability) <= 1.0:
            return self._reject("probability_out_of_range", epoch, start_sample)
        else:
            value = float(probability)

        computed_available = (None if validity == "unknown"
                              else self.available_ns(end_sample))
        if available_ns is not None and available_ns != computed_available:
            return self._reject("stale_availability", epoch, start_sample)

        decision: bool | None = None
        if validity == "known":
            decision = value >= self.config["decision_threshold"]
        event = {
            "sequence": self.next_sequence,
            "session_id": self.session_id,
            "epoch": self.epoch,
            "validity": validity,
            "event_type": "speech_probability",
            "start_sample": start_sample,
            "end_sample": end_sample,
            "probability": round(value, 12),
            "decision": decision,
            "padded_samples": padded_samples,
            "clock": self.config["clock"] if validity != "unknown" else None,
            "available_ns": computed_available,
            "advisory_only": True,
        }
        self.events.append(event)
        self.next_sequence += 1
        self.total_samples = end_sample
        self.frame_index += 1

        emitted = None
        if decision is True:
            if self.active_start is None:
                self.active_start = start_sample
        elif decision is False and self.active_start is not None:
            emitted = self._close_run(start_sample, "inactive_frame")
        elif decision is None and self.active_start is not None:
            emitted = self._close_run(start_sample, "closed_at_unknown")
        return {"status": "ok", "probability_event": event, "speech_event": emitted}

    def _close_run(self, close_at: int, reason: str) -> Dict[str, Any]:
        if self.active_start is None:
            raise AssertionError("close_without_run")
        run = {
            "sequence": len(self.speech_events) + 1,
            "session_id": self.session_id,
            "epoch": self.epoch,
            "event_type": "speech_event",
            "start_sample": self.active_start,
            "end_sample": close_at,
            "available_sample": self.total_samples,
            "available_ns": self.available_ns(self.total_samples),
            "clock": self.config["clock"],
            "close_reason": reason,
            "advisory_only": True,
        }
        self.speech_events.append(run)
        self.active_start = None
        return run

    def drain(self) -> Dict[str, Any]:
        emitted = (self._close_run(self.total_samples, "drain")
                   if self.active_start is not None else None)
        return {"status": "ok", "operation": "drain", "speech_event": emitted,
                "total_samples": self.total_samples}

    def drop_sequence(self, sequence: int,
                      reason: str = "synthetic_bus_drop") -> Dict[str, Any]:
        self.dropped.append({"sequence": sequence, "reason": reason,
                             "session_id": self.session_id, "epoch": self.epoch})
        return self.dropped[-1]

    def state_digest_payload(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "epoch": self.epoch,
            "total_samples": self.total_samples,
            "frame_index": self.frame_index,
            "next_sequence": self.next_sequence,
            "active_start": self.active_start,
            "events_digest": sha256(canonical_bytes(self.events)),
            "speech_events_digest": sha256(canonical_bytes(self.speech_events)),
        }

    def summary(self) -> Dict[str, Any]:
        payload = self.state_digest_payload()
        return {
            "session_id": self.session_id,
            "epoch": self.epoch,
            "probability_events": len(self.events),
            "speech_events": len(self.speech_events),
            "rejections": len(self.rejections),
            "dropped": len(self.dropped),
            "total_samples": self.total_samples,
            "probability_event_digest": payload["events_digest"],
            "speech_event_digest": payload["speech_events_digest"],
            "state_digest": sha256(canonical_bytes(payload)),
        }


def _validity_for_frame(index: int) -> str:
    return ("unknown" if fixture.segment_for_frame(index)["truth"] == "unknown"
            else "known")


def drive(session: Session, frames: List[List[float]], start: int = 0,
          end: int | None = None) -> List[Dict[str, Any]]:
    end = len(frames) if end is None else end
    records = []
    for index in range(start, end):
        record = session.process_frame(
            frames[index], validity=_validity_for_frame(index),
            start_sample=index * fixture.FRAME_SAMPLES,
            end_sample=(index + 1) * fixture.FRAME_SAMPLES)
        if record["status"] != "ok":
            raise AssertionError("unexpected_rejection:" + record["reason"])
        records.append(record)
    return records


def drive_streaming(session: Session, pcm: List[float],
                    chunk_sizes: Sequence[int] = (160, 480, 800),
                    start: int = 0, end: int | None = None
                    ) -> List[Dict[str, Any]]:
    """Buffer arbitrary source chunks into exact 256-sample frames."""
    end = len(pcm) if end is None else end
    offset = start
    buffer: List[float] = []
    records: List[Dict[str, Any]] = []
    chunk_index = 0
    frame_index = 0
    while offset < end:
        size = min(chunk_sizes[chunk_index % len(chunk_sizes)], end - offset)
        buffer.extend(pcm[offset:offset + size])
        offset += size
        chunk_index += 1
        while len(buffer) >= fixture.FRAME_SAMPLES:
            frame = buffer[:fixture.FRAME_SAMPLES]
            buffer = buffer[fixture.FRAME_SAMPLES:]
            record = session.process_frame(
                frame, validity=_validity_for_frame(frame_index),
                start_sample=frame_index * fixture.FRAME_SAMPLES,
                end_sample=(frame_index + 1) * fixture.FRAME_SAMPLES)
            if record["status"] != "ok":
                raise AssertionError("unexpected_rejection:" + record["reason"])
            records.append(record)
            frame_index += 1
    if buffer:
        record = session.process_frame(
            buffer, validity=_validity_for_frame(frame_index),
            start_sample=frame_index * fixture.FRAME_SAMPLES,
            end_sample=frame_index * fixture.FRAME_SAMPLES + len(buffer),
            is_final=True, valid_samples=len(buffer))
        if record["status"] != "ok":
            raise AssertionError("unexpected_rejection:" + record["reason"])
        records.append(record)
    return records


def event_bus_control(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Explicit dropped/stale/missing/nonfinite event cases; nothing fabricated."""
    dropped_sequences = [2, 5, 17]
    delivered_sequences = [event["sequence"] for event in events
                           if event["sequence"] not in dropped_sequences]
    gaps = []
    cursor = 1
    for sequence in delivered_sequences:
        if sequence > cursor:
            gaps.append([cursor, sequence - 1])
        cursor = sequence + 1
    session = Session(fixture.CONFIG, "event-bus", 4)
    frame = fixture.build_frames()[0]
    first = session.process_frame(frame, epoch=4, validity="known",
                                  start_sample=0,
                                  end_sample=fixture.FRAME_SAMPLES)
    base = first["probability_event"]["available_ns"]
    cases: Dict[str, Any] = {}
    checks = (
        ("stale_epoch", {"epoch": 3}, "stale_epoch"),
        ("missing_probability", {"probability": EXPLICIT_MISSING}, "missing_probability"),
        ("nonfinite_probability", {"probability": float("nan")},
         "nonfinite_probability"),
        ("infinite_probability", {"probability": float("inf")},
         "nonfinite_probability"),
        ("out_of_range_probability", {"probability": 1.4},
         "probability_out_of_range"),
        ("invalid_validity", {"validity": "invalid"}, "invalid_event_validity"),
        ("missing_validity", {"validity": "missing"}, "missing_event_validity"),
        ("wrong_clock", {"clock": "other-clock"}, "wrong_clock"),
        ("stale_availability", {"available_ns": 0}, "stale_availability"),
        ("wrong_interval", {"start_sample": 1}, "wrong_source_interval"),
        ("duplicate_sequence", {"sequence": 1},
         "duplicate_or_out_of_order_sequence"),
        ("nonfinite_frame", {"frame": [float("nan")] * fixture.FRAME_SAMPLES},
         "nonfinite_frame"),
        ("short_frame", {"frame": [0.0] * 128}, "short_frame"),
    )
    for name, kwargs, expected in checks:
        options: Dict[str, Any] = {
            "epoch": 4, "validity": "known",
            "start_sample": fixture.FRAME_SAMPLES,
            "end_sample": 2 * fixture.FRAME_SAMPLES,
            "probability": 0.25,
        }
        options.update(kwargs)
        if name == "wrong_clock":
            options["available_ns"] = session.available_ns(2 * fixture.FRAME_SAMPLES)
        if name == "stale_availability":
            options["available_ns"] = 0
        if name == "duplicate_sequence":
            options["sequence"] = 1
        record = session.process_frame(options.pop("frame", frame), **options)
        cases[name] = {"status": record["status"], "reason": record["reason"],
                       "expected_reason": expected,
                       "accepted": record["status"] == "ok",
                       "state_unchanged": record.get("state_digest_before")
                       == record.get("state_digest_after")}
        if cases[name]["reason"] != expected or not cases[name]["state_unchanged"]:
            raise AssertionError("event_control_failed:" + name)
    return {
        "total_sequences": len(events),
        "delivered_sequences": delivered_sequences,
        "dropped_sequences": dropped_sequences,
        "gaps": gaps,
        "fabricated_events": 0,
        "availability_example_ns": base,
        "adverse_cases": cases,
        "all_rejected_without_state_change": all(
            case["state_unchanged"] and not case["accepted"]
            for case in cases.values()),
    }


def independent_state_control(frames: List[List[float]]) -> Dict[str, Any]:
    left = Session(fixture.CONFIG, "left", 3)
    right = Session(fixture.CONFIG, "right", 8)
    drive(left, frames, 0, 8)
    drive(right, frames, 0, 8)
    before = {"left": left.summary(), "right": right.summary()}
    if before["left"]["probability_event_digest"] == \
            before["right"]["probability_event_digest"]:
        raise AssertionError("sessions_are_not_independent")
    left.reset(4)
    drive(left, frames, 0, 2)
    after = {"left": left.summary(), "right": right.summary()}
    if after["right"] != before["right"] or after["left"]["epoch"] != 4:
        raise AssertionError("reset_leaked_across_sessions")
    fresh = Session(fixture.CONFIG, "left", 4)
    drive(fresh, frames, 0, 2)
    same_epoch_fresh = Session(fixture.CONFIG, "left", 3)
    drive(same_epoch_fresh, frames, 0, 8)
    return {
        "before": before,
        "after_reset": after,
        "reset_matches_fresh_digest":
            after["left"]["probability_event_digest"]
            == fresh.summary()["probability_event_digest"],
        "same_epoch_fresh_session_matches":
            same_epoch_fresh.summary()["probability_event_digest"]
            == before["left"]["probability_event_digest"],
        "old_epoch_event_rejected": left.process_frame(
            frames[2], epoch=3, validity="known",
            start_sample=2 * fixture.FRAME_SAMPLES,
            end_sample=3 * fixture.FRAME_SAMPLES)["reason"],
    }


def streaming_parity_control(frames: List[List[float]],
                             pcm: List[float]) -> Dict[str, Any]:
    offline = Session(fixture.CONFIG, "parity", 1)
    drive(offline, frames)
    offline.drain()
    streaming = Session(fixture.CONFIG, "parity", 1)
    drive_streaming(streaming, pcm)
    streaming.drain()
    fresh = Session(fixture.CONFIG, "parity", 1)
    drive(fresh, frames)
    fresh.drain()
    identical = (offline.events == streaming.events
                 and offline.speech_events == streaming.speech_events)
    if not identical:
        raise AssertionError("offline_streaming_parity_failed")
    if fresh.events != offline.events or fresh.speech_events != offline.speech_events:
        raise AssertionError("fresh_session_parity_failed")
    return {
        "offline_events": len(offline.events),
        "streaming_events": len(streaming.events),
        "offline_speech_events": len(offline.speech_events),
        "streaming_speech_events": len(streaming.speech_events),
        "events_identical": identical,
        "fresh_session_identical": True,
        "offline_digest": offline.summary()["probability_event_digest"],
        "streaming_digest": streaming.summary()["probability_event_digest"],
        "chunk_sizes": [160, 480, 800],
        "chunk_buffering": "exact 256-sample frames; no frame is split or dropped",
    }


def partial_tail_control(pcm: List[float]) -> Dict[str, Any]:
    session = Session(fixture.CONFIG, "partial-tail", 1)
    records = drive_streaming(session, pcm, chunk_sizes=(160, 480), start=0, end=384)
    if len(records) != 2:
        raise AssertionError("partial_tail_frame_count")
    final = records[-1]["probability_event"]
    if (final["end_sample"] != 384 or final["padded_samples"] != 128
            or final["available_ns"] != session.available_ns(384)):
        raise AssertionError("partial_tail_coordinates")
    return {
        "stream_samples": 384,
        "full_frames": 1,
        "final_valid_samples": 128,
        "final_padded_samples": 128,
        "final_end_sample": 384,
        "final_available_ns": final["available_ns"],
        "frame_interval_clipped_to_real_samples": True,
        "inference_frame_zero_padded": True,
    }


def cross_hop_control() -> Dict[str, Any]:
    interval = (150, 330)
    projected = scorer.project_interval(*interval,
                                        frame_samples=fixture.FRAME_SAMPLES)
    expected = [[0, 106], [1, 74]]
    if [list(item) for item in projected] != expected:
        raise AssertionError("cross_hop_projection_mismatch")
    truth_projection = scorer.project_interval(
        2048, 6144, frame_samples=fixture.FRAME_SAMPLES)
    return {
        "interval": list(interval),
        "frames": [list(item) for item in projected],
        "overlap_samples": sum(overlap for _, overlap in projected),
        "truth_interval": [2048, 6144],
        "truth_hops": len(truth_projection),
        "truth_overlap_samples": sum(overlap for _, overlap in truth_projection),
        "source_time_mapping": fixture.CONFIG["source_time_mapping"],
        "declared_analysis_delay_samples":
            fixture.CONFIG["declared_analysis_delay_samples"],
    }


def frame_adverse_control() -> Dict[str, Any]:
    session = Session(fixture.CONFIG, "frame-adverse", 1)
    frame = fixture.build_frames()[0]
    session.process_frame(frame, validity="known", start_sample=0,
                          end_sample=fixture.FRAME_SAMPLES)
    before = session.summary()["state_digest"]
    cases = {}
    variants = (
        ("nan", [float("nan")] * fixture.FRAME_SAMPLES, "nonfinite_frame"),
        ("infinite", [float("inf")] * fixture.FRAME_SAMPLES, "nonfinite_frame"),
        ("short", [0.0] * 128, "short_frame"),
        ("long", [0.0] * (fixture.FRAME_SAMPLES + 1), "long_frame"),
        ("empty", [], "wrong_frame_format"),
        ("boolean", [True] * fixture.FRAME_SAMPLES, "wrong_frame_format"),
    )
    for name, data, expected in variants:
        record = session.process_frame(
            data, validity="known",
            start_sample=fixture.FRAME_SAMPLES,
            end_sample=2 * fixture.FRAME_SAMPLES, probability=0.1)
        cases[name] = {"reason": record["reason"], "expected": expected,
                       "state_unchanged":
                           session.summary()["state_digest"] == before}
        if cases[name]["reason"] != expected or not cases[name]["state_unchanged"]:
            raise AssertionError("frame_control_failed:" + name)
    for name, valid_samples in (("zero_final", 0), ("long_final", 257)):
        record = session.process_frame(
            [0.0] * max(1, min(valid_samples, 256)), validity="known",
            start_sample=fixture.FRAME_SAMPLES,
            end_sample=fixture.FRAME_SAMPLES + 1, probability=0.1,
            is_final=True, valid_samples=valid_samples)
        cases[name] = {"reason": record["reason"],
                       "expected": "invalid_final_valid_samples",
                       "state_unchanged":
                           session.summary()["state_digest"] == before}
        if cases[name]["reason"] != cases[name]["expected"] \
                or not cases[name]["state_unchanged"]:
            raise AssertionError("frame_control_failed:" + name)
    final = session.process_frame(
        [0.0] * 128, validity="known",
        start_sample=fixture.FRAME_SAMPLES,
        end_sample=fixture.FRAME_SAMPLES + 128, probability=0.1,
        is_final=True, valid_samples=128)
    return {
        "cases": cases,
        "all_present": True,
        "all_fail_closed": True,
        "final_partial_status": final["status"],
        "final_partial_end_sample": final["probability_event"]["end_sample"],
        "final_partial_padded_samples": final["probability_event"]["padded_samples"],
        "final_partial_available_ns": final["probability_event"]["available_ns"],
        "state_unchanged_after_rejections": all(
            case["state_unchanged"] for case in cases.values()),
    }


def config_adverse_control() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}
    mutations = (
        ("sample_rate_hz", 48000),
        ("channels", 2),
        ("sample_format", "s16"),
        ("frame_samples", 320),
        ("decision_threshold", 0.6),
        ("real_runtime", True),
        ("wheel_or_licensed_runtime_used", True),
    )
    for key, value in mutations:
        config = dict(fixture.CONFIG)
        config[key] = value
        try:
            fixture.validate_config(config)
        except ValueError as error:
            cases[key] = {"status": "rejected", "reason": str(error)}
        else:
            raise AssertionError("config_control_failed:" + key)
    try:
        Session(dict(fixture.CONFIG), "", 1)
    except ValueError as error:
        cases["missing_session_id"] = {"status": "rejected", "reason": str(error)}
    else:
        raise AssertionError("missing_session_id_accepted")
    return cases


def interval_and_availability_control(events: List[Dict[str, Any]],
                                      runs: List[Dict[str, Any]]
                                      ) -> Dict[str, Any]:
    boundaries = [event["start_sample"] for event in events] + \
        [events[-1]["end_sample"]]
    expected_boundaries = list(
        range(0, fixture.TOTAL_SAMPLES + 1, fixture.FRAME_SAMPLES))
    if boundaries != expected_boundaries:
        raise AssertionError("probability_intervals_not_exact")
    known = [event for event in events if event["validity"] == "known"]
    availability = [event["available_ns"] for event in known]
    if any(right <= left for left, right in zip(availability, availability[1:])):
        raise AssertionError("availability_not_strictly_monotonic")
    for event in known:
        expected = (fixture.ORIGIN_NS
                    + event["end_sample"] * fixture.SAMPLE_NS
                    + fixture.PROCESSING_DELAY_NS)
        if event["available_ns"] != expected:
            raise AssertionError("availability_formula_mismatch")
    for run in runs:
        if run["start_sample"] < 0 or run["end_sample"] > fixture.TOTAL_SAMPLES \
                or run["start_sample"] >= run["end_sample"]:
            raise AssertionError("speech_event_out_of_bounds")
        if run["available_ns"] != (fixture.ORIGIN_NS
                                   + run["available_sample"] * fixture.SAMPLE_NS
                                   + fixture.PROCESSING_DELAY_NS):
            raise AssertionError("speech_event_availability_mismatch")
    return {
        "frame_boundaries_exact": boundaries == expected_boundaries,
        "probability_events_cover_samples": [boundaries[0], boundaries[-1]],
        "speech_events_cover_samples": [
            min((run["start_sample"] for run in runs), default=None),
            max((run["end_sample"] for run in runs), default=None),
        ],
        "known_availability_strictly_increasing": True,
        "unknown_events_have_no_availability": all(
            event["available_ns"] is None for event in events
            if event["validity"] == "unknown"),
        "clock": fixture.CLOCK,
        "availability_formula": (
            "origin_ns + end_sample * 62500 + processing_delay_ns"),
        "measured": False,
    }


def _asset_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="earshot-122-asset-") as directory:
        root = Path(directory)
        wheel = root / WHEEL_FILENAME
        wheel.write_bytes(
            b"synthetic caller wheel placeholder; never imported or executed\n")
        base = {
            "wheel_path": str(wheel),
            "wheel_sha256": fixture.sha256_file(wheel),
            "source_commit": UPSTREAM_COMMIT,
            "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": fixture.FRAME_SAMPLES,
            "threshold": 0.5,
            "input_format": "float32",
        }
        valid = validate_caller_asset(dict(base))

        def rejected(manifest: Dict[str, Any]) -> Dict[str, Any]:
            try:
                validate_caller_asset(manifest)
            except ValueError as error:
                return {"status": "rejected", "reason": str(error)}
            return {"status": "unexpectedly_accepted", "reason": None}

        hash_manifest = dict(base)
        hash_manifest["wheel_sha256"] = "0" * 64
        absent_manifest = dict(base)
        absent_manifest["wheel_path"] = str(root / "absent.whl")
        relative_manifest = dict(base)
        relative_manifest["wheel_path"] = WHEEL_FILENAME
        commit_manifest = dict(base)
        commit_manifest["source_commit"] = "0" * 40
        rate_manifest = dict(base)
        rate_manifest["sample_rate_hz"] = 48000
        channels_manifest = dict(base)
        channels_manifest["channels"] = 2
        frame_manifest = dict(base)
        frame_manifest["frame_samples"] = 512
        threshold_manifest = dict(base)
        threshold_manifest["threshold"] = 0.6
        format_manifest = dict(base)
        format_manifest["input_format"] = "int16"
        extra_manifest = dict(base)
        extra_manifest["model_archive_path"] = str(root / "model.tar.gz")
        return {
            "all_present": True,
            "all_fail_closed": True,
            "valid_manifest": {
                "status": "validated",
                "verified": valid["verified"],
                "loaded": valid["loaded"],
                "executed": valid["executed"],
                "imported": valid["imported"],
            },
            "missing_manifest": rejected({}),
            "absent_file": rejected(absent_manifest),
            "relative_path": rejected(relative_manifest),
            "hash_mismatch": rejected(hash_manifest),
            "wrong_source_commit": rejected(commit_manifest),
            "wrong_sample_rate": rejected(rate_manifest),
            "wrong_channels": rejected(channels_manifest),
            "wrong_frame_size": rejected(frame_manifest),
            "wrong_threshold": rejected(threshold_manifest),
            "wrong_input_format": rejected(format_manifest),
            "unexpected_field": rejected(extra_manifest),
        }


def _regressions(conditions: Dict[str, Any],
                 boundaries: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    strata = conditions["detections"]["strata"]
    if strata["quiet-a"]["FN"]:
        regressions.append({
            "condition": "quiet-a",
            "metric": "missed_speech_samples",
            "value": strata["quiet-a"]["FN"],
            "note": "surrogate misses the low-amplitude start of the quiet run",
        })
    if strata["quiet-b"]["FN"]:
        regressions.append({
            "condition": "quiet-b",
            "metric": "missed_speech_samples",
            "value": strata["quiet-b"]["FN"],
            "note": "surrogate misses the entire below-threshold quiet run",
        })
    if strata["noise-burst"]["FP"]:
        regressions.append({
            "condition": "noise-burst",
            "metric": "false_speech_samples",
            "value": strata["noise-burst"]["FP"],
            "note": "surrogate admits the loud part of the nonspeech burst",
        })
    for match in boundaries["matches"]:
        if match["matched"] and (match["onset_delay_samples"] or
                                 match["offset_delay_samples"]):
            regressions.append({
                "condition": "quiet-a" if match["truth"][0] == 2048 else "active-a",
                "metric": "boundary_delay_samples",
                "value": [match["onset_delay_samples"],
                          match["offset_delay_samples"]],
                "note": "synthetic source-coordinate delay; not device timing",
            })
    return regressions


def _report_core() -> Dict[str, Any]:
    frames = fixture.build_frames()
    pcm = [sample for frame in frames for sample in frame]
    session = Session(fixture.CONFIG, "primary", 1)
    drive(session, frames)
    session.drain()
    events = session.events
    runs = session.speech_events
    results = scorer.score_stream(events, runs)
    controls = {
        "invalid_vs_nonspeech": scorer.invalid_vs_nonspeech_control(),
        "caller_asset": _asset_controls(),
        "frame": frame_adverse_control(),
        "config_adverse": config_adverse_control(),
        "event_bus": event_bus_control(events),
        "independent_state": independent_state_control(frames),
        "streaming_parity": streaming_parity_control(frames, pcm),
        "partial_tail": partial_tail_control(pcm),
        "cross_hop": cross_hop_control(),
        "interval_and_availability": interval_and_availability_control(events, runs),
    }
    regressions = _regressions(results, results["boundaries"])
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "asset_resolution": {
            "requested": False,
            "manifest_present": False,
            "wheel_present_in_sdk_worktree": False,
            "wheel_present_in_research_workspace": False,
            "environment_present": False,
            "source_archive_present": False,
            "runtime_library_present": False,
            "weights_embedded_in_wheel": True,
            "verified": False,
            "loaded": False,
            "executed": False,
            "imported": False,
            "surrogate_used": True,
            "expected_wheel_path": WHEEL_PATH,
            "expected_wheel_sha256": WHEEL_SHA256,
            "expected_environment_path": RUNTIME_ENV_PATH,
            "reason": "caller_supplied_wheel_absent_and_rights_unreviewed",
        },
        "surrogate": {
            "identity": "earshot-1-2-2-boundary-surrogate-v1",
            "is_earshot": False,
            "is_neural_network": False,
            "weights": False,
            "checkpoint": False,
            "model_archive": False,
            "quality_claim": False,
            "method": (
                "deterministic per-frame RMS and zero-crossing logistic gate on "
                "frozen integer-synthesised waveforms; threshold 0.5; no "
                "smoothing, hangover or postprocessing"),
            "frame_samples": fixture.FRAME_SAMPLES,
            "decision_threshold": 0.5,
            "probability_gain": fixture.CONFIG["probability_gain"],
            "probability_offset": fixture.CONFIG["probability_offset"],
            "probability_zcr_weight": fixture.CONFIG["probability_zcr_weight"],
            "deterministic": True,
            "pure_synthetic": True,
        },
        "availability": {
            "clock_id": fixture.CLOCK,
            "origin_ns": str(fixture.ORIGIN_NS),
            "ns_per_sample": fixture.SAMPLE_NS,
            "processing_delay_ns": fixture.PROCESSING_DELAY_NS,
            "frame_samples": fixture.FRAME_SAMPLES,
            "first_available_ns": str(
                fixture.ORIGIN_NS + fixture.FRAME_SAMPLES * fixture.SAMPLE_NS
                + fixture.PROCESSING_DELAY_NS),
            "last_available_ns": str(
                fixture.ORIGIN_NS + fixture.TOTAL_SAMPLES * fixture.SAMPLE_NS
                + fixture.PROCESSING_DELAY_NS),
            "formula": (
                "available_ns = origin_ns + end_sample * ns_per_sample + "
                "processing_delay_ns"),
            "monotonic_nondecreasing": True,
            "measured": False,
            "device_timing": False,
            "signal_timestamp_is_not_availability": True,
            "availability_serialization": "decimal string",
            "synthetic_decision_allowance": True,
        },
        "strata": results["detections"]["strata"],
        "detections": {
            key: results["detections"][key] for key in (
                "overall", "speech_samples", "nonspeech_samples",
                "speech_miss_rate", "false_alarm_rate", "unknown_excluded_samples",
                "invalid_excluded_samples", "frame_resolution_samples",
                "denominator_note")
        },
        "probabilities": results["probabilities"],
        "boundaries": results["boundaries"],
        "baselines": scorer.baseline_metrics(),
        "alignment": {
            "frame_grid_exact": True,
            "frame_samples": fixture.FRAME_SAMPLES,
            "frame_duration_ms": fixture.FRAME_DURATION_MS,
            "declared_analysis_delay_samples":
                fixture.CONFIG["declared_analysis_delay_samples"],
            "deterministic_decision_available_after_frame": True,
            "content_delay_compensation": "not_applicable_frame_cadence",
            "onset_offset_delay_unit": (
                "samples; positive onset = late start, negative offset = early stop"),
            "matched_boundary_count": results["boundaries"]["matched_count"],
            "source_interval_mapping": fixture.CONFIG["source_time_mapping"],
            "measured": False,
        },
        "state": {
            "independent_sessions_uncoupled": bool(
                controls["independent_state"]["before"]["left"][
                    "probability_event_digest"]
                != controls["independent_state"]["before"]["right"][
                    "probability_event_digest"]),
            "reset_bit_identical": controls["independent_state"][
                "reset_matches_fresh_digest"],
            "reset_epoch_propagated": controls["independent_state"]["after_reset"][
                "left"]["epoch"] == 4,
            "same_epoch_fresh_deterministic": controls["independent_state"][
                "same_epoch_fresh_session_matches"],
            "offline_streaming_identical": controls["streaming_parity"][
                "events_identical"],
            "different_stimuli_differ": bool(
                fixture.probability_for_frame(frames[32])
                != fixture.probability_for_frame(frames[0])),
            "processed_outputs_finite": True,
        },
        "controls": controls,
        "adverse": {
            "all_rejected": True,
            "all_invalid_cases_rejected": True,
            "caller_asset_fail_closed": True,
            "frame_fail_closed": True,
            "event_bus_fail_closed": True,
            "config_rejections": controls["config_adverse"],
            "frame_rejections": controls["frame"]["cases"],
            "caller_asset_rejections": controls["caller_asset"],
            "event_bus_cases": controls["event_bus"]["adverse_cases"],
        },
        "comparison": {
            "candidate": "earshot-1-2-2-boundary-surrogate-v1",
            "identity_control": (
                "always_speech_and_always_nonspeech_diagnostic_baselines"),
            "established_task_matched_baseline_reproduced": False,
            "source_reported_used_for_qualification": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No Earshot wheel, embedded weights or rights-cleared real "
                "cohort; the surrogate is a boundary conformance fixture and "
                "its synthetic metrics are not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "reason": (
                "No Earshot wheel, runtime or target device; the surrogate is "
                "unpaced and no wall-clock, memory or deadline result is claimed."),
            "frame_duration_ms": fixture.FRAME_DURATION_MS,
            "content_delay_samples_modeled": 0,
            "source_reported_cost_us_per_20ms_frame": 13.41,
            "source_reported_cost_used_for_qualification": False,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(fixture.SOURCE_PINS),
        "asset_pins": {
            key: dict(value) for key, value in fixture.EXTERNAL_ASSET_PINS.items()
        },
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "gates": [
            {"name": name, "status": "blocked", "reopen_condition": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "exact_blockers": list(EXACT_BLOCKERS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "evidence_classes": {
            "synthetic_surrogate": (
                "Deterministic model-free boundary surrogate on frozen synthetic "
                "stimuli; no Earshot asset, real audio or device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
            "independent_listening": (
                "not required by the Analysis profile and not performed"),
            "target_runtime": "none",
        },
        "acceptance_profile": {
            "profile": PROFILE,
            "source": "plan/swarm/VERIFICATION.md",
            **{item: True for item in ACCEPTANCE_PROFILE_ITEMS},
            "scorer_sha256": fixture.sha256_file(HERE / "scorer.py"),
            "fixture_sha256": fixture.sha256_file(HERE / "fixture.py"),
        },
        "contract_sha256": sha256(contract_bytes()),
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Dict[str, Any] | None = None
    for _ in range(3):
        core = _report_core()
        digests.append(sha256(canonical_bytes(core)))
    if core is None:
        raise RuntimeError("report_core_missing")
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding the repeatability block",
    }
    return core


REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "base_commit", "branch",
    "profile", "status", "evidence_status", "qualification_status", "decision",
    "defer_before", "no_missing_result_qualifies_candidate", "scope",
    "negative_claims", "boundary", "format", "caller_supplied_asset_contract",
    "asset_resolution", "surrogate", "availability", "strata", "detections",
    "probabilities", "boundaries", "baselines", "alignment", "state", "controls",
    "adverse", "comparison", "regressions", "timing", "source_reported",
    "model_provenance", "licensing_analysis", "source_pins", "asset_pins",
    "boundary_pins", "gates", "exact_blockers", "missing_evidence",
    "reopening_conditions", "evidence_classes", "acceptance_profile",
    "contract_sha256", "repeatability",
}


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def contract_payload() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": fixture.SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "timestamped probabilities on exact half-open source intervals",
                "sample-weighted detection confusion with stratified FN/FP",
                "quiet and active speech, idle noise and a loud noise burst",
                "contact boundaries matched by overlap with exact onset/offset delay",
                "validity separated from nonspeech with an explicit unknown span",
                "independent state, availability, dropped/stale events and cross-hop",
                "fail-closed caller-asset, frame, config and event-bus controls",
            ],
            "not_applicable": [
                "no Earshot wheel, so exact posteriors and source-reported values "
                "are not reproduced",
                "no real cohort, so no accuracy, generalization or quality claim is made",
                "no target device, so no timing, memory or deadline result is claimed",
                "no listening is required by the Analysis profile or performed",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(fixture.SOURCE_PINS),
        "asset_pins": {
            key: dict(value) for key, value in fixture.EXTERNAL_ASSET_PINS.items()
        },
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": [
            {"name": name, "status": "blocked", "reopen_condition": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "scope": dict(SCOPE),
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, "
            "contract, header, registry, default, board, handoff or CI file changes.",
            "The surrogate is opt-in, unregistered, disabled by default and not a "
            "provider or production callback.",
            "No Earshot wheel, source archive, embedded weight or runtime is "
            "copied, downloaded, built, imported, loaded or executed.",
            "All stimuli are frozen deterministic synthetic floats; no real audio, "
            "labels, device or network is used.",
            "Caller-supplied wheel manifests fail closed on missing, relative, "
            "hash-mismatched, wrong-geometry or extra-field inputs.",
            "Source-reported Earshot metrics are provenance only and are never "
            "reproduced, pooled or used as thresholds.",
            "Missing evidence never qualifies the candidate; decision remains DEFER.",
        ],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def adapter_payload() -> Dict[str, Any]:
    return {
        "schema_id": ADAPTER_SCHEMA_ID,
        "task_id": TASK,
        "task_local": True,
        "implemented": False,
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "input_kind": "waveform",
        "output_kinds": ["annotation"],
        "tasks": ["DET-01"],
        "modes": ["offline", "streaming"],
        "weights": "caller_supplied_asset_required_not_present",
        "caller_supplied_asset_required": True,
        "asset_present": False,
        "activation": "deferred_until_gates_clear",
        "entrypoint": None,
        "note": (
            "Proposal-only task-local descriptor. It is not the shipped adapter, "
            "not a provider registration and not a public default."),
    }


def adapter_bytes() -> bytes:
    return canonical_bytes(adapter_payload())


def readiness_payload() -> Dict[str, Any]:
    report = build_report()
    report_bytes = canonical_bytes(report)
    contract_digest = sha256(contract_bytes())
    return {
        "schema_id": READINESS_SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "profile": PROFILE,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "defer_before": DEFER_BEFORE,
        "ready_for_opt_in_adapter": False,
        "ready_for_provider_registration": False,
        "ready_for_release": False,
        "quality_pass": False,
        "report_sha256": sha256(report_bytes),
        "contract_sha256": contract_digest,
        "blocked_gates": [name for name, _ in GATE_DEFINITIONS],
        "exact_blocker": EXACT_BLOCKERS[0],
        "reopen_condition": REOPENING_CONDITIONS[0],
        "external_asset": {
            "required": True,
            "present": False,
            "loaded": False,
            "executed": False,
            "imported": False,
            "expected_wheel_path": WHEEL_PATH,
            "expected_wheel_sha256": WHEEL_SHA256,
            "expected_source_archive_sha256": SOURCE_ARCHIVE_SHA256,
            "expected_environment_path": RUNTIME_ENV_PATH,
            "weights_embedded_in_wheel": True,
        },
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
    }


def readiness_bytes() -> bytes:
    return canonical_bytes(readiness_payload())


def allowed_pin_keys() -> set[str]:
    keys = {"source:" + path for path in fixture.SOURCE_PINS}
    keys.update(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)
    return keys


PIN_RE = re.compile(r"([a-f0-9]{64})  (.+)")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    allowed = allowed_pin_keys()
    result: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            if not (line.startswith("# SHA-256 pins")
                    or line.startswith("# source:")):
                raise ValueError("unexpected_comment:" + repr(line))
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError("malformed_pin:" + repr(line))
        digest, raw = match.groups()
        if raw in seen:
            raise ValueError("duplicate_pin:" + raw)
        relative = raw.split(":", 1)[1] if raw.startswith("source:") else raw
        if any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("traversing_pin:" + raw)
        if raw not in allowed:
            raise ValueError("unexpected_pin:" + raw)
        seen.add(raw)
        result.append((digest, raw))
    return result


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-EARSHOT-1-2-2 task-local evidence.",
        "# source: paths are relative to the pinned research workspace root",
    ]
    for path in sorted(fixture.SOURCE_PINS):
        lines.append(f"{fixture.SOURCE_PINS[path]}  source:{path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


README_SECTIONS = ("source", "boundary", "artifacts", "external-absent")
README_MARKER_RE = re.compile(r"<!-- digest-table: ([a-z-]+) -->")
README_ROW_RE = re.compile(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|")
README_TABLE_HEADER = "| Key | SHA-256 |"
README_TABLE_SEPARATOR = "| --- | --- |"


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + path for path in fixture.SOURCE_PINS},
        "boundary": {"sdk:" + path for path in fixture.BOUNDARY_PINS},
        "artifacts": set(LOCAL_ARTIFACT_PATHS),
        "external-absent": set(fixture.EXTERNAL_ASSET_PINS),
    }


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    sections: Dict[str, List[Tuple[str, str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        marker = README_MARKER_RE.fullmatch(line.strip())
        if marker:
            name = marker.group(1)
            if name == "end":
                if current is None:
                    raise ValueError("unmatched_end_marker")
                current = None
                continue
            if name not in README_SECTIONS:
                raise ValueError("unknown_readme_section:" + name)
            if name in sections:
                raise ValueError("duplicate_readme_section:" + name)
            sections[name] = []
            current = name
            continue
        if not line.startswith("|"):
            continue
        if current is None:
            continue
        if line.strip() in (README_TABLE_HEADER, README_TABLE_SEPARATOR):
            continue
        match = README_ROW_RE.fullmatch(line.strip())
        if not match:
            raise ValueError("malformed_readme_row:" + line)
        key, digest = match.groups()
        if any(existing == key for existing, _ in sections[current]):
            raise ValueError("duplicate_readme_key:" + key)
        sections[current].append((key, digest))
    return sections


def verify_readme_digests(text: str) -> Dict[str, int]:
    sections = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    if set(sections) != set(expected):
        raise ValueError("readme_section_set_mismatch")
    counts: Dict[str, int] = {}
    for name in README_SECTIONS:
        keys = {key for key, _ in sections[name]}
        if keys != expected[name]:
            raise ValueError("readme_key_set_mismatch:" + name)
        for key, digest in sections[name]:
            if name == "source":
                path = fixture.resolve_source_path(key.split(":", 1)[1])
                actual = fixture.sha256_file(path)
            elif name == "boundary":
                path = fixture.SDK_ROOT / key.split(":", 1)[1]
                actual = fixture.sha256_file(path)
            elif name == "artifacts":
                path = HERE / key
                actual = fixture.sha256_file(path)
            else:
                meta = fixture.EXTERNAL_ASSET_PINS[key]
                if digest != meta["sha256"]:
                    raise ValueError("readme_external_digest_mismatch:" + key)
                if meta["expected_path"] is not None:
                    candidate = fixture.workspace_root() / meta["expected_path"]
                    if candidate.is_file():
                        raise ValueError("external_asset_present:" + key)
                counts[name] = counts.get(name, 0) + 1
                continue
            if actual != digest:
                raise ValueError("readme_digest_mismatch:" + key)
            counts[name] = counts.get(name, 0) + 1
    return counts


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = (
        '{"a":1,"a":2}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":-Infinity}',
        '[1,2]',
    )
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except (ValueError, TypeError):
            rejected_json += 1
    bad_pins = (
        "not-a-line",
        "a" * 64 + "  ../escape",
        "a" * 64 + "  docs/task-evidence/earshot-1-2-2/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md", "0" * 64 + "  CONTRACTS.md"]),
    )
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except (ValueError, TypeError):
            rejected_pins += 1
    duplicate = (
        "<!-- digest-table: artifacts -->\n"
        f"| `report.json` | `{'0' * 64}` |\n"
        f"| `report.json` | `{'0' * 64}` |\n")
    bad_readme = (
        "<!-- digest-table: end -->\n",
        "<!-- digest-table: unknown -->\n",
        "<!-- digest-table: artifacts -->\n| report.json | short |\n",
        duplicate,
    )
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except (ValueError, TypeError):
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }
