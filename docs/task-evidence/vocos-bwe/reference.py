# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local Vocos-BWE blocker evidence for SDK-VOCOS-BWE.

Stdlib-only, deterministic, fail-closed. No Vocos-BWE source, weights, runtime,
audio, feature tensor, corpus, listening, timing, benchmark, or release claim.
This package records absent exact artifacts and a Restoration-profile admission
boundary. Missing evidence never qualifies.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-VOCOS-BWE"
COMPONENT_ID = "vocos-bwe"
TASK_TITLE = "Vocos-BWE"
CONTRACT_ID = "audio-sdk/vocos-bwe-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "restoration"
PROFILE_LABEL = "Restoration"
MODE = "feasibility"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = "swarm/SDK-VOCOS-BWE"
WRITE_SCOPE = "docs/task-evidence/vocos-bwe/ only"
TASK_PREFIX = "docs/task-evidence/vocos-bwe/"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml"))
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-denoise/REPORT.md":
        "eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "docs/task-evidence/vocos/report.json":
        "3f961e3fbffb63af701e38dd16914711288facb7f1285b054a2ffc1a5ad3b059",
}
# Fix vocos report pin - compute dynamically? better pin known hash from file.

BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
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
        "id": "SDK-FND-PROVIDER",
        "title": "Provider integration boundaries and build fragments",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"],
    },
)

ABSENCE_PROBES = (
    "research/voice-enhancement-20261101/repos/vocos-bwe",
    "research/voice-enhancement-20261101/repos/Vocos-BWE",
    "research/voice-enhancement-20261101/repos/vocos2",
    "research/voice-enhancement-20261101/models/vocos-bwe",
    "research/voice-enhancement-20261101/checkpoints/vocos-bwe",
    "data/checkouts/vocos-bwe",
    "data/models/vocos-bwe",
    "data/assets/vocos-bwe",
    "third_party/vocos-bwe",
    "adapters/vocos-bwe",
    "docs/task-evidence/vocos-bwe/weights",
    "docs/task-evidence/vocos-bwe/runtime",
    "docs/task-evidence/vocos-bwe/assets",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--cisco-ai--vocos-bwe",
    "~/.cache/huggingface/hub/models--gemelo-ai--vocos-bwe",
)

PROFILE_PHRASES = (
    "Freeze corruption, metadata and corresponding clean/audio packet baseline.",
    "Stratify by degradation, erasure burst and bandwidth.",
    "Report discrete concealment/validity, decoded intervals, task-specific quality and bounds on output peaks and timing.",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "exact_model_source_and_license",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": "Exact Vocos-BWE upstream source at a 40-hex revision with reviewed LICENSE/NOTICE and immutable archive digest.",
    },
    {
        "id": "ART-02",
        "kind": "pinned_weights_or_checkpoint",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": "Immutable Vocos-BWE checkpoint/weights with filename, byte count, SHA-256, format and expected input/output bandwidth geometry.",
    },
    {
        "id": "ART-03",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": "Locked offline runtime with install digest, deterministic settings, fixed seed and recorded host profile.",
    },
    {
        "id": "ART-04",
        "kind": "rights_and_terms_review",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": "Reviewed source/weight/model-card/output terms covering attribution, redistribution, commercial and output use.",
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": "Rights-cleared frozen narrowband/degraded/clean cohort with consent, exact geometry, hashes, degradation/bandwidth strata and controls.",
    },
    {
        "id": "ART-06",
        "kind": "approved_reference_parity_and_protocol",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": "Approved reference outputs and Restoration-profile quality/timing protocol with agreed margins and baselines.",
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "status": "open",
        "qualifies": False,
        "statement": "No exact Vocos-BWE model/checkpoint/adapter source, 40-hex revision, LICENSE/NOTICE bundle or immutable archive digest is present; generic Vocos vocoder evidence is not bandwidth extension.",
        "required_action": "Supply exact Vocos-BWE upstream source at a 40-hex revision with reviewed LICENSE/NOTICE and immutable archive digest.",
        "linked_gates": ["RG-01"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "status": "open",
        "qualifies": False,
        "statement": "No Vocos-BWE checkpoint/weights, filename, byte count, SHA-256, format or input/output bandwidth geometry is present.",
        "required_action": "Supply immutable checkpoint/weights with exact digests, format and declared narrowband/BWE geometry.",
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "status": "open",
        "qualifies": False,
        "statement": "No pinned offline runtime, install digest, deterministic settings or host profile is present.",
        "required_action": "Supply locked runtime with install digest, deterministic settings, fixed seed and recorded host profile.",
        "linked_gates": ["RG-04"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "status": "open",
        "qualifies": False,
        "statement": "No reviewed source/weight/model-card/output rights decision is staged for Vocos-BWE.",
        "required_action": "Record reviewed attribution, redistribution, commercial and output-use terms for intended artifacts.",
        "linked_gates": ["RG-03", "RG-05"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "status": "open",
        "qualifies": False,
        "statement": "No rights-cleared frozen narrowband/degraded/clean cohort, consent, degradation/bandwidth strata or controls are present.",
        "required_action": "Supply rights-cleared frozen cohort with consent, exact geometry, hashes, degradation/bandwidth strata and controls.",
        "linked_gates": ["RG-06", "RG-07"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "status": "open",
        "qualifies": False,
        "statement": "No approved reference parity vectors or Restoration-profile quality/timing protocol is present.",
        "required_action": "Supply approved parity vectors and independent Restoration-profile protocol with agreed margins and baselines.",
        "linked_gates": ["RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {"id": "RG-01", "title": "Source revision and license provenance", "status": "blocked", "qualifies": False, "reopen_condition": "Exact Vocos-BWE source, 40-hex revision, LICENSE/NOTICE and immutable archive digest are supplied and reviewed."},
    {"id": "RG-02", "title": "Checkpoint identity and geometry", "status": "blocked", "qualifies": False, "reopen_condition": "Immutable checkpoint/weights with filename, byte count, SHA-256, format and narrowband/BWE geometry are supplied and verified offline."},
    {"id": "RG-03", "title": "Rights and output terms", "status": "blocked", "qualifies": False, "reopen_condition": "Reviewed source/weight/model-card/output terms settle attribution, redistribution, commercial and output use."},
    {"id": "RG-04", "title": "Pinned runtime and deterministic load", "status": "blocked", "qualifies": False, "reopen_condition": "Locked offline runtime with install digest loads pinned assets deterministically with fixed seed and recorded host profile."},
    {"id": "RG-05", "title": "Consent, reference availability and output use", "status": "blocked", "qualifies": False, "reopen_condition": "Signed consent, reference-availability, output-use and commercial-terms records exist for every input/output use."},
    {"id": "RG-06", "title": "Frozen cohort and controls", "status": "blocked", "qualifies": False, "reopen_condition": "Rights-cleared frozen cohort with exact geometry, hashes, degradation/bandwidth strata and matched controls is supplied."},
    {"id": "RG-07", "title": "Separate restoration quality and timing", "status": "blocked", "qualifies": False, "reopen_condition": "Approved protocol produces reviewed restoration quality, concealment/validity, peak/timing and baseline comparisons on frozen strata."},
    {"id": "RG-08", "title": "Independent review and release boundary", "status": "blocked", "qualifies": False, "reopen_condition": "Exact-head independent review confirms no default/ABI/shared-build/CI/provider/registry change and no unqualified release claim."},
)

RESTORATION_PROFILE_ROWS = (
    {"id": "RP-01", "requirement": PROFILE_PHRASES[0], "status": "blocked", "evidence": "No exact Vocos-BWE model, corruption metadata, clean/audio packet baseline or cohort is present."},
    {"id": "RP-02", "requirement": PROFILE_PHRASES[1], "status": "blocked", "evidence": "No degradation, erasure burst or bandwidth stratification is available."},
    {"id": "RP-03", "requirement": PROFILE_PHRASES[2], "status": "blocked", "evidence": "No concealment/validity, decoded interval, task-specific quality, peak or timing measurement exists."},
)

QUALITY_OUTCOME_ROWS = (
    {"id": "QO-01", "outcome": "task-specific restoration quality", "status": "blocked", "value": None, "evidence": "No qualified restored output, clean reference or paired metric."},
    {"id": "QO-02", "outcome": "discrete concealment/validity", "status": "blocked", "value": None, "evidence": "No decoded interval/concealment validity result."},
    {"id": "QO-03", "outcome": "content preservation/baseline comparison", "status": "blocked", "value": None, "evidence": "No low-pass identity/interpolation or matched baseline comparison run."},
    {"id": "QO-04", "outcome": "peak/nonfinite safety", "status": "blocked", "value": None, "evidence": "No output peak or nonfinite measurement."},
)

TIMING_ROWS = (
    {"id": "TR-01", "metric": "decoded intervals/alignment", "status": "blocked", "value": None, "evidence": "No run, decoded interval map or alignment record."},
    {"id": "TR-02", "metric": "output peak/timing bounds", "status": "blocked", "value": None, "evidence": "No output peak bound or timing measurement."},
    {"id": "TR-03", "metric": "device timing/resources", "status": "blocked", "value": None, "evidence": "No target-device paced run, CPU/memory or deadline data."},
    {"id": "TR-04", "metric": "benchmark/real-time factor", "status": "blocked", "value": None, "evidence": "No current run; generic Vocos vocoder provenance is not BWE evidence."},
)

NON_CLAIMS = (
    "No Vocos-BWE source, checkpoint, runtime, feature tensor, generated waveform or vendor output is bundled.",
    "No model was imported, built, loaded, executed, downloaded or benchmarked.",
    "No audio or feature tensor was read, decoded, played, listened to or scored.",
    "No restoration quality, concealment/validity, peak, alignment, timing, device-resource, benchmark or release result exists.",
    "No consent, reference-availability or output-use clearance is asserted.",
    "No provider was registered, enabled by default, described in a registry or exposed through installed-v0, an ABI, the shared build or CI.",
    "Generic Vocos vocoder evidence is not Vocos-BWE bandwidth-extension evidence.",
    "Missing or blocked evidence does not qualify this component.",
)

ADMISSION_SCHEMA = {
    "manifest_schema_id": "audio-sdk/vocos-bwe-qualification/0.1",
    "policy": "task_local_fail_closed_admission_not_runtime_behavior",
    "manifest_fields": ["schema_id", "cohort_id", "source", "weights", "runtime", "inputs", "controls", "outcomes", "rights"],
    "source_fields": ["revision", "path", "license_id", "license_path", "license_sha256"],
    "weight_fields": ["name", "path", "sha256", "byte_count", "format", "terms_sha256"],
    "runtime_fields": ["python_version", "torch_version", "device", "threads", "deterministic_algorithms", "seed", "install_digest"],
    "input_fields": ["id", "path", "sha256", "sample_rate_hz", "input_bandwidth_hz", "target_bandwidth_hz", "frame_count", "degradation", "consent_id", "rights_reference"],
    "control_fields": ["id", "kind", "input_id", "input_sha256"],
    "outcome_fields": ["task_metric", "stoi", "pesq", "log_spectral_distance", "alignment_samples", "first_output_ms", "tail_ms", "peak_abs", "clipped_fraction", "nonfinite_count", "sample_count", "output_sample_rate_hz"],
    "rights_fields": ["consent_reference", "input_availability", "output_use", "commercial_terms_review", "terms_review", "baseline_protocol"],
    "weight_formats": ["jit_torchscript", "pytorch_state_dict", "safetensors", "onnx"],
    "weight_suffixes": [".pt", ".pth", ".safetensors", ".onnx"],
    "control_kinds": ["matched_baseline", "mismatched_degradation", "zero_input"],
    "degradations": ["low_pass", "codec_bandlimit", "packet_loss_bandlimit", "narrowband_capture"],
    "input_sample_rates_hz": [8000, 16000, 22050, 24000, 44100, 48000],
    "output_sample_rates_hz": [16000, 22050, 24000, 44100, 48000],
    "required_weight_token": "vocos-bwe",
    "python_version_pattern": r"^3\.(10|11|12|13)\.[0-9]+$",
    "torch_version_policy": "pinned_semver_recorded_by_caller",
    "device": "cpu",
    "max_threads": 64,
    "max_seed": 2147483647,
    "max_weight_bytes": 8 * 1024 * 1024 * 1024,
    "max_frame_count": 1_000_000,
    "max_alignment_samples": 96000,
    "max_peak": 4.0,
    "model_executed": False,
    "weights_loaded": False,
    "feature_input_read": False,
    "audio_read": False,
    "network_used": False,
}

REQUIRED_RESULTS = {
    "exact_model_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "reference_consent_present": False,
    "quality_result_present": False,
    "restoration_result_present": False,
    "alignment_result_present": False,
    "peak_or_timing_result_present": False,
    "device_timing_result_present": False,
    "benchmark_result_present": False,
    "listening_result_present": False,
    "release_claim": False,
    "no_result_qualifies": True,
}

SCOPE = {
    "task_local_only": True,
    "exact_model_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "model_executed": False,
    "weights_loaded": False,
    "audio_read": False,
    "feature_input_read": False,
    "network_used": False,
    "download_attempted": False,
    "quality_scored": False,
    "restoration_scored": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "real_corpus": False,
    "release_claim": False,
}

BOUNDARY = {
    "task_local_only": True,
    "provider_registration": False,
    "default_selected": False,
    "enabled_by_default": False,
    "processor_exposure": False,
    "descriptor_registry_change": False,
    "public_api_abi_change": False,
    "installed_v0_behavior_change": False,
    "shared_cmakelists_change": False,
    "ci_workflow_change": False,
    "real_weights_or_runtime": False,
    "listening": False,
    "files_outside_task_directory_written": False,
}

QUALIFICATION = {
    "status": "not_qualified",
    "not_qualified": True,
    "readiness": "incomplete",
    "real_result_present": False,
    "all_release_gates_blocked": True,
    "exact_model_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "quality_result": False,
    "restoration_result": False,
    "alignment_result": False,
    "peak_or_timing_result": False,
    "device_timing_result": False,
    "benchmark_result": False,
    "listening_result": False,
    "release_claim": False,
    "missing_result_promoted": False,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    body = dict(report)
    body.pop("report_sha256", None)
    text = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_strict_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    value, index = decoder.raw_decode(text)
    if text[index:].strip():
        raise ValueError("trailing_content")
    reject_nonfinite(value)
    return value


def reject_nonfinite(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            reject_nonfinite(child)
        return
    if isinstance(value, list):
        for child in value:
            reject_nonfinite(child)
        return
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError("nonfinite")


def source_path(relative: str) -> Path:
    return AUDIO_ROOT / relative


def boundary_path(relative: str) -> Path:
    return WORKTREE / relative


def board_row_identity() -> dict[str, Any]:
    board = read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = board.get("tasks", []) if isinstance(board, dict) else []
    for row in rows:
        if isinstance(row, dict) and row.get("id") == TASK:
            projection = {field: row.get(field) for field in BOARD_ROW_FIELDS}
            return {
                "projection": projection,
                "sha256": object_digest(projection),
                "board_file_pinned": False,
                "board_status_gates_anything": False,
                "gating": "stable_identity_only",
                "linked_rows": [dict(row) for row in LINKED_ROWS],
                "linked_rows_sha256": object_digest([dict(row) for row in LINKED_ROWS]),
            }
    raise RuntimeError("board_row_missing:" + TASK)


def probe_absence() -> dict[str, Any]:
    probes = []
    for relative in ABSENCE_PROBES:
        workspace_path = AUDIO_ROOT / relative
        worktree_path = WORKTREE / relative
        probes.append({
            "path": relative,
            "present": workspace_path.exists() or worktree_path.exists(),
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    home_probes = []
    for raw in HOME_ABSENCE_PROBES:
        expanded = Path(os.path.expanduser(raw))
        home_probes.append({
            "path": raw,
            "present": expanded.exists(),
            "searched_home_cache": True,
        })
    present = [p["path"] for p in probes + home_probes if p["present"]]
    return {
        "probes": probes,
        "home_probes": home_probes,
        "summary": {
            "all_probes_absent": len(present) == 0,
            "present_count": len(present),
            "present_paths": present,
            "probe_count": len(probes) + len(home_probes),
            "workspace_probe_count": len(probes),
            "home_probe_count": len(home_probes),
            "download_attempted": False,
            "network_used": False,
            "recursive_workspace_walk": False,
            "model_executed": False,
            "weights_loaded": False,
            "audio_read": False,
            "feature_input_read": False,
            "source_or_runtime_imported": False,
        },
    }


def check_pins() -> dict[str, Any]:
    source = {}
    for relative, expected in sorted(SOURCE_PINS.items()):
        path = source_path(relative)
        actual = sha256_file(path) if path.is_file() else None
        source[relative] = {"sha256": expected, "actual": actual, "verified": actual == expected}
    boundary = {}
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        path = boundary_path(relative)
        actual = sha256_file(path) if path.is_file() else None
        boundary[relative] = {"sha256": expected, "actual": actual, "verified": actual == expected}
    return {"source_pins": source, "boundary_pins": boundary}


def _reject(code: str, field: str, case_id: str) -> dict[str, Any]:
    return {"id": case_id, "status": "rejected", "code": code, "field": field, "qualifies": False, "state_unchanged": True}


def _is_hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % length, value) is not None


def _is_slug(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", value) is not None


def _is_canonical_abs(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("/") or "\x00" in value:
        return False
    parts = [p for p in value.split("/") if p]
    return value == "/" + "/".join(parts)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def valid_manifest() -> dict[str, Any]:
    return {
        "schema_id": ADMISSION_SCHEMA["manifest_schema_id"],
        "cohort_id": "vocos-bwe-bwe-synthetic-control",
        "source": {
            "revision": "0123456789abcdef0123456789abcdef01234567",
            "path": "/opt/vocos-bwe",
            "license_id": "MIT",
            "license_path": "/opt/vocos-bwe/LICENSE",
            "license_sha256": "0" * 64,
        },
        "weights": [
            {
                "name": "vocos-bwe-24k.pt",
                "path": "/opt/vocos-bwe/vocos-bwe-24k.pt",
                "sha256": "1" * 64,
                "byte_count": 1024,
                "format": "jit_torchscript",
                "terms_sha256": "2" * 64,
            }
        ],
        "runtime": {
            "python_version": "3.12.3",
            "torch_version": "2.4.1",
            "device": "cpu",
            "threads": 4,
            "deterministic_algorithms": True,
            "seed": 0,
            "install_digest": "3" * 64,
        },
        "inputs": [
            {
                "id": "nb-001",
                "path": "/data/nb-001.wav",
                "sha256": "4" * 64,
                "sample_rate_hz": 16000,
                "input_bandwidth_hz": 8000,
                "target_bandwidth_hz": 16000,
                "frame_count": 16000,
                "degradation": "low_pass",
                "consent_id": "consent-a",
                "rights_reference": "rights-a",
            },
            {
                "id": "nb-002",
                "path": "/data/nb-002.wav",
                "sha256": "5" * 64,
                "sample_rate_hz": 16000,
                "input_bandwidth_hz": 8000,
                "target_bandwidth_hz": 16000,
                "frame_count": 16000,
                "degradation": "codec_bandlimit",
                "consent_id": "consent-b",
                "rights_reference": "rights-b",
            },
        ],
        "controls": [
            {"id": "c-match", "kind": "matched_baseline", "input_id": "nb-001", "input_sha256": "4" * 64},
            {"id": "c-mismatch", "kind": "mismatched_degradation", "input_id": "nb-002", "input_sha256": "5" * 64},
            {"id": "c-zero", "kind": "zero_input", "input_id": None, "input_sha256": None},
        ],
        "outcomes": {
            "task_metric": 0.1,
            "stoi": 0.9,
            "pesq": 3.0,
            "log_spectral_distance": 0.5,
            "alignment_samples": 0,
            "first_output_ms": 0.0,
            "tail_ms": 0.0,
            "peak_abs": 0.9,
            "clipped_fraction": 0.0,
            "nonfinite_count": 0,
            "sample_count": 16000,
            "output_sample_rate_hz": 16000,
        },
        "rights": {
            "consent_reference": "consent://signed",
            "input_availability": "rights-cleared",
            "output_use": "evaluation-only",
            "commercial_terms_review": "reviewed",
            "terms_review": "reviewed",
            "baseline_protocol": "approved-restoration-protocol",
        },
    }


def validate_manifest(manifest: Any) -> tuple[bool, str, str]:
    if not isinstance(manifest, dict):
        return False, "manifest_not_object", ""
    expected_fields = set(ADMISSION_SCHEMA["manifest_fields"])
    if set(manifest.keys()) != expected_fields:
        for field in ADMISSION_SCHEMA["manifest_fields"]:
            if field not in manifest:
                return False, "missing_field", field
        extra = sorted(set(manifest.keys()) - expected_fields)
        return False, "unknown_field", extra[0] if extra else ""
    if manifest["schema_id"] != ADMISSION_SCHEMA["manifest_schema_id"]:
        return False, "invalid_schema", "schema_id"
    cohort = manifest["cohort_id"]
    if not isinstance(cohort, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", cohort):
        return False, "invalid_value", "cohort_id"

    source = manifest["source"]
    if not isinstance(source, dict) or set(source.keys()) != set(ADMISSION_SCHEMA["source_fields"]):
        for f in ADMISSION_SCHEMA["source_fields"]:
            if not isinstance(source, dict) or f not in source:
                return False, "missing_field", f"source.{f}"
        extra = sorted(set(source.keys()) - set(ADMISSION_SCHEMA["source_fields"]))
        return False, "unknown_field", f"source.{extra[0]}"
    if not _is_hex(source["revision"], 40):
        return False, "invalid_value", "source.revision"
    if not _is_canonical_abs(source["path"]):
        return False, "invalid_path", "source.path"
    if not isinstance(source["license_id"], str) or not source["license_id"]:
        return False, "invalid_value", "source.license_id"
    if not _is_canonical_abs(source["license_path"]):
        return False, "invalid_path", "source.license_path"
    if not _is_hex(source["license_sha256"], 64):
        return False, "invalid_value", "source.license_sha256"

    weights = manifest["weights"]
    if not isinstance(weights, list) or not weights:
        return False, "invalid_value", "weights"
    names = set()
    has_token = False
    for item in weights:
        if not isinstance(item, dict) or set(item.keys()) != set(ADMISSION_SCHEMA["weight_fields"]):
            for f in ADMISSION_SCHEMA["weight_fields"]:
                if not isinstance(item, dict) or f not in item:
                    return False, "missing_field", f"weights.{f}"
            extra = sorted(set(item.keys()) - set(ADMISSION_SCHEMA["weight_fields"]))
            return False, "unknown_field", f"weights.{extra[0]}"
        name = item["name"]
        if not _is_slug(name):
            return False, "invalid_value", "weights.name"
        if name in names:
            return False, "invalid_value", "weights.name"
        names.add(name)
        if ADMISSION_SCHEMA["required_weight_token"] in name:
            has_token = True
        if not any(name.endswith(s) for s in ADMISSION_SCHEMA["weight_suffixes"]):
            return False, "invalid_value", "weights.suffix_required"
        if not _is_canonical_abs(item["path"]):
            return False, "invalid_path", "weights.path"
        if not _is_hex(item["sha256"], 64):
            return False, "invalid_value", "weights.sha256"
        bc = item["byte_count"]
        if not _is_int(bc) or bc < 1 or bc > ADMISSION_SCHEMA["max_weight_bytes"]:
            return False, "invalid_value", "weights.byte_count"
        if item["format"] not in ADMISSION_SCHEMA["weight_formats"]:
            return False, "invalid_value", "weights.format"
        if not _is_hex(item["terms_sha256"], 64):
            return False, "invalid_value", "weights.terms_sha256"
    if not has_token:
        return False, "invalid_value", "weights.vocos_bwe_required"

    runtime = manifest["runtime"]
    if not isinstance(runtime, dict) or set(runtime.keys()) != set(ADMISSION_SCHEMA["runtime_fields"]):
        for f in ADMISSION_SCHEMA["runtime_fields"]:
            if not isinstance(runtime, dict) or f not in runtime:
                return False, "missing_field", f"runtime.{f}"
        extra = sorted(set(runtime.keys()) - set(ADMISSION_SCHEMA["runtime_fields"]))
        return False, "unknown_field", f"runtime.{extra[0]}"
    if not isinstance(runtime["python_version"], str) or not re.fullmatch(ADMISSION_SCHEMA["python_version_pattern"], runtime["python_version"]):
        return False, "invalid_value", "runtime.python_version"
    tv = runtime["torch_version"]
    if not isinstance(tv, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+([A-Za-z0-9.+-]*)?", tv):
        return False, "invalid_value", "runtime.torch_version"
    if runtime["device"] != ADMISSION_SCHEMA["device"]:
        return False, "invalid_value", "runtime.device"
    threads = runtime["threads"]
    if not _is_int(threads) or threads < 1 or threads > ADMISSION_SCHEMA["max_threads"]:
        return False, "invalid_value", "runtime.threads"
    if runtime["deterministic_algorithms"] is not True:
        return False, "invalid_value", "runtime.deterministic_algorithms"
    seed = runtime["seed"]
    if not _is_int(seed) or seed < 0 or seed > ADMISSION_SCHEMA["max_seed"]:
        return False, "invalid_value", "runtime.seed"
    if not _is_hex(runtime["install_digest"], 64):
        return False, "invalid_value", "runtime.install_digest"

    inputs = manifest["inputs"]
    if not isinstance(inputs, list) or not inputs:
        return False, "invalid_value", "inputs"
    input_index: dict[str, dict[str, Any]] = {}
    for item in inputs:
        if not isinstance(item, dict) or set(item.keys()) != set(ADMISSION_SCHEMA["input_fields"]):
            for f in ADMISSION_SCHEMA["input_fields"]:
                if not isinstance(item, dict) or f not in item:
                    return False, "missing_field", f"inputs.{f}"
            extra = sorted(set(item.keys()) - set(ADMISSION_SCHEMA["input_fields"]))
            return False, "unknown_field", f"inputs.{extra[0]}"
        iid = item["id"]
        if not _is_slug(iid) or iid in input_index:
            return False, "invalid_value", "inputs.id"
        if not _is_canonical_abs(item["path"]):
            return False, "invalid_path", "inputs.path"
        if not _is_hex(item["sha256"], 64):
            return False, "invalid_value", "inputs.sha256"
        for field, allowed in (("sample_rate_hz", ADMISSION_SCHEMA["input_sample_rates_hz"]),):
            if not _is_int(item[field]) or item[field] not in allowed:
                return False, "invalid_value", f"inputs.{field}"
        for field, lo, hi in (("input_bandwidth_hz", 1000, 48000), ("target_bandwidth_hz", 1000, 48000), ("frame_count", 1, ADMISSION_SCHEMA["max_frame_count"])):
            if not _is_int(item[field]) or item[field] < lo or item[field] > hi:
                return False, "invalid_value", f"inputs.{field}"
        if item["target_bandwidth_hz"] <= item["input_bandwidth_hz"]:
            return False, "invalid_value", "inputs.target_bandwidth_hz"
        if item["degradation"] not in ADMISSION_SCHEMA["degradations"]:
            return False, "invalid_value", "inputs.degradation"
        for field in ("consent_id", "rights_reference"):
            if not isinstance(item[field], str) or not item[field]:
                return False, "invalid_value", f"inputs.{field}"
        input_index[iid] = item

    controls = manifest["controls"]
    if not isinstance(controls, list) or not controls:
        return False, "invalid_value", "controls"
    kinds = set()
    control_ids = set()
    for item in controls:
        if not isinstance(item, dict) or set(item.keys()) != set(ADMISSION_SCHEMA["control_fields"]):
            for f in ADMISSION_SCHEMA["control_fields"]:
                if not isinstance(item, dict) or f not in item:
                    return False, "missing_field", f"controls.{f}"
            extra = sorted(set(item.keys()) - set(ADMISSION_SCHEMA["control_fields"]))
            return False, "unknown_field", f"controls.{extra[0]}"
        cid = item["id"]
        if not _is_slug(cid) or cid in control_ids:
            return False, "invalid_value", "controls.id"
        control_ids.add(cid)
        kind = item["kind"]
        if kind not in ADMISSION_SCHEMA["control_kinds"]:
            return False, "invalid_value", "controls.kind"
        if kind in kinds:
            return False, "invalid_value", "controls.kind"
        kinds.add(kind)
        if kind == "zero_input":
            if item["input_id"] is not None or item["input_sha256"] is not None:
                return False, "invalid_value", "controls.zero_input"
        else:
            if item["input_id"] not in input_index:
                return False, "invalid_value", "controls.input_id"
            if item["input_sha256"] != input_index[item["input_id"]]["sha256"]:
                return False, "invalid_value", "controls.input_sha256"
    if kinds != set(ADMISSION_SCHEMA["control_kinds"]):
        return False, "invalid_value", "controls.required"

    outcomes = manifest["outcomes"]
    if not isinstance(outcomes, dict) or set(outcomes.keys()) != set(ADMISSION_SCHEMA["outcome_fields"]):
        for f in ADMISSION_SCHEMA["outcome_fields"]:
            if not isinstance(outcomes, dict) or f not in outcomes:
                return False, "missing_field", f"outcomes.{f}"
        extra = sorted(set(outcomes.keys()) - set(ADMISSION_SCHEMA["outcome_fields"]))
        return False, "unknown_field", f"outcomes.{extra[0]}"
    for f in ("task_metric", "stoi", "pesq", "log_spectral_distance", "first_output_ms", "tail_ms", "peak_abs", "clipped_fraction"):
        if not _is_number(outcomes[f]):
            return False, "nonfinite_value" if isinstance(outcomes[f], float) and not math.isfinite(outcomes[f]) else "invalid_value", f"outcomes.{f}"
    if not (0.0 <= float(outcomes["task_metric"]) <= 1.0):
        return False, "invalid_value", "outcomes.task_metric"
    if not (0.0 <= float(outcomes["stoi"]) <= 1.0):
        return False, "invalid_value", "outcomes.stoi"
    if not (0.0 <= float(outcomes["pesq"]) <= 5.0):
        return False, "invalid_value", "outcomes.pesq"
    if not (0.0 <= float(outcomes["log_spectral_distance"]) <= 100.0):
        return False, "invalid_value", "outcomes.log_spectral_distance"
    for f in ("alignment_samples", "nonfinite_count", "sample_count"):
        if not _is_int(outcomes[f]) or outcomes[f] < 0:
            return False, "invalid_value", f"outcomes.{f}"
    if outcomes["alignment_samples"] > ADMISSION_SCHEMA["max_alignment_samples"]:
        return False, "invalid_value", "outcomes.alignment_samples"
    if outcomes["nonfinite_count"] != 0:
        return False, "invalid_value", "outcomes.nonfinite_count"
    if outcomes["sample_count"] < 1:
        return False, "invalid_value", "outcomes.sample_count"
    if float(outcomes["first_output_ms"]) < 0.0 or float(outcomes["tail_ms"]) < 0.0:
        return False, "invalid_value", "outcomes.timing"
    if not (0.0 <= float(outcomes["peak_abs"]) <= ADMISSION_SCHEMA["max_peak"]):
        return False, "invalid_value", "outcomes.peak_abs"
    if not (0.0 <= float(outcomes["clipped_fraction"]) <= 1.0):
        return False, "invalid_value", "outcomes.clipped_fraction"
    if not _is_int(outcomes["output_sample_rate_hz"]) or outcomes["output_sample_rate_hz"] not in ADMISSION_SCHEMA["output_sample_rates_hz"]:
        return False, "invalid_value", "outcomes.output_sample_rate_hz"

    rights = manifest["rights"]
    if not isinstance(rights, dict) or set(rights.keys()) != set(ADMISSION_SCHEMA["rights_fields"]):
        for f in ADMISSION_SCHEMA["rights_fields"]:
            if not isinstance(rights, dict) or f not in rights:
                return False, "missing_field", f"rights.{f}"
        extra = sorted(set(rights.keys()) - set(ADMISSION_SCHEMA["rights_fields"]))
        return False, "unknown_field", f"rights.{extra[0]}"
    for f in ADMISSION_SCHEMA["rights_fields"]:
        if not isinstance(rights[f], str) or not rights[f]:
            return False, "invalid_value", f"rights.{f}"

    return True, "accepted", ""


def admission_cases() -> list[dict[str, Any]]:
    cases = []

    def add(case_id: str, manifest: Any, expected_ok: bool = False, expected_code: str = "invalid_value", expected_field: str = ""):
        ok, code, field = validate_manifest(manifest)
        if expected_ok:
            if ok:
                cases.append({"id": case_id, "status": "accepted_schema_control", "code": "accepted", "field": "", "qualifies": False, "state_unchanged": True, "evidence_class": "synthetic_schema_control_not_evidence"})
            else:
                cases.append({"id": case_id, "status": "rejected", "code": code, "field": field, "qualifies": False, "state_unchanged": True, "unexpected": "expected_accept"})
        else:
            cases.append(_reject(code if code else expected_code, field if field else expected_field, case_id))

    # malformed roots
    add("root-list", [], False)
    add("root-null", None, False)
    add("root-string", "x", False)
    add("root-int", 1, False)
    add("root-bool", True, False)

    base = valid_manifest()
    for field in ADMISSION_SCHEMA["manifest_fields"]:
        m = valid_manifest(); m.pop(field); add(f"missing-{field}", m)
    m = valid_manifest(); m["extra"] = 1; add("unknown-top-field", m)
    m = valid_manifest(); m["schema_id"] = "wrong"; add("wrong-schema", m)
    m = valid_manifest(); m["cohort_id"] = "Bad"; add("cohort-uppercase", m)
    m = valid_manifest(); m["cohort_id"] = ""; add("cohort-empty", m)

    # source
    for field in ADMISSION_SCHEMA["source_fields"]:
        m = valid_manifest(); m["source"].pop(field); add(f"missing-source-{field}", m)
    m = valid_manifest(); m["source"]["extra"] = 1; add("unknown-source-field", m)
    m = valid_manifest(); m["source"]["revision"] = "abc"; add("source-revision-short", m)
    m = valid_manifest(); m["source"]["path"] = "relative"; add("source-path-relative", m)
    m = valid_manifest(); m["source"]["license_sha256"] = "Z"*64; add("source-license-sha", m)

    # weights
    m = valid_manifest(); m["weights"] = []; add("weights-empty", m)
    m = valid_manifest(); m["weights"] = "x"; add("weights-not-list", m)
    for field in ADMISSION_SCHEMA["weight_fields"]:
        m = valid_manifest(); m["weights"][0].pop(field); add(f"missing-weight-{field}", m)
    m = valid_manifest(); m["weights"][0]["extra"] = 1; add("unknown-weight-field", m)
    m = valid_manifest(); m["weights"].append(dict(m["weights"][0])); add("weights-duplicate-name", m)
    m = valid_manifest(); m["weights"][0]["name"] = "other.pt"; add("weights-missing-token", m)
    m = valid_manifest(); m["weights"][0]["name"] = "vocos-bwe.bin"; add("weights-bad-suffix", m)
    m = valid_manifest(); m["weights"][0]["path"] = "rel.pt"; add("weights-path-relative", m)
    m = valid_manifest(); m["weights"][0]["sha256"] = "G"*64; add("weights-sha-bad", m)
    m = valid_manifest(); m["weights"][0]["byte_count"] = 0; add("weights-byte-zero", m)
    m = valid_manifest(); m["weights"][0]["byte_count"] = True; add("weights-byte-bool", m)
    m = valid_manifest(); m["weights"][0]["byte_count"] = 1.5; add("weights-byte-float", m)
    m = valid_manifest(); m["weights"][0]["byte_count"] = 9 * 1024 * 1024 * 1024; add("weights-byte-huge", m)
    m = valid_manifest(); m["weights"][0]["format"] = "pickle"; add("weights-format", m)
    m = valid_manifest(); m["weights"][0]["terms_sha256"] = "x"; add("weights-terms-sha", m)

    # runtime
    for field in ADMISSION_SCHEMA["runtime_fields"]:
        m = valid_manifest(); m["runtime"].pop(field); add(f"missing-runtime-{field}", m)
    m = valid_manifest(); m["runtime"]["extra"] = 1; add("unknown-runtime-field", m)
    m = valid_manifest(); m["runtime"]["python_version"] = "3.9.0"; add("runtime-python-old", m)
    m = valid_manifest(); m["runtime"]["torch_version"] = "latest"; add("runtime-torch-bad", m)
    m = valid_manifest(); m["runtime"]["device"] = "cuda"; add("runtime-device-cuda", m)
    m = valid_manifest(); m["runtime"]["threads"] = 0; add("runtime-threads-zero", m)
    m = valid_manifest(); m["runtime"]["threads"] = 65; add("runtime-threads-huge", m)
    m = valid_manifest(); m["runtime"]["threads"] = True; add("runtime-threads-bool", m)
    m = valid_manifest(); m["runtime"]["deterministic_algorithms"] = False; add("runtime-deterministic-false", m)
    m = valid_manifest(); m["runtime"]["seed"] = -1; add("runtime-seed-negative", m)
    m = valid_manifest(); m["runtime"]["seed"] = 2**31; add("runtime-seed-huge", m)
    m = valid_manifest(); m["runtime"]["seed"] = True; add("runtime-seed-bool", m)
    m = valid_manifest(); m["runtime"]["install_digest"] = "z"; add("runtime-install-digest", m)

    # inputs
    m = valid_manifest(); m["inputs"] = []; add("inputs-empty", m)
    for field in ADMISSION_SCHEMA["input_fields"]:
        m = valid_manifest(); m["inputs"][0].pop(field); add(f"missing-input-{field}", m)
    m = valid_manifest(); m["inputs"][0]["extra"] = 1; add("unknown-input-field", m)
    m = valid_manifest(); m["inputs"][1]["id"] = m["inputs"][0]["id"]; add("inputs-duplicate-id", m)
    m = valid_manifest(); m["inputs"][0]["path"] = "rel"; add("inputs-path-relative", m)
    m = valid_manifest(); m["inputs"][0]["sha256"] = "x"; add("inputs-sha-bad", m)
    m = valid_manifest(); m["inputs"][0]["sample_rate_hz"] = 12345; add("inputs-rate-bad", m)
    m = valid_manifest(); m["inputs"][0]["input_bandwidth_hz"] = 0; add("inputs-inbw-zero", m)
    m = valid_manifest(); m["inputs"][0]["target_bandwidth_hz"] = 8000; add("inputs-target-not-greater", m)
    m = valid_manifest(); m["inputs"][0]["frame_count"] = 0; add("inputs-frames-zero", m)
    m = valid_manifest(); m["inputs"][0]["frame_count"] = 1_000_001; add("inputs-frames-huge", m)
    m = valid_manifest(); m["inputs"][0]["degradation"] = "unknown"; add("inputs-degradation", m)
    m = valid_manifest(); m["inputs"][0]["consent_id"] = ""; add("inputs-consent-empty", m)

    # controls
    m = valid_manifest(); m["controls"] = []; add("controls-empty", m)
    for field in ADMISSION_SCHEMA["control_fields"]:
        m = valid_manifest(); m["controls"][0].pop(field); add(f"missing-control-{field}", m)
    m = valid_manifest(); m["controls"][0]["extra"] = 1; add("unknown-control-field", m)
    m = valid_manifest(); m["controls"][0]["id"] = m["controls"][1]["id"]; add("controls-duplicate-id", m)
    m = valid_manifest(); m["controls"][0]["kind"] = "bad"; add("controls-bad-kind", m)
    m = valid_manifest(); m["controls"][1]["kind"] = "matched_baseline"; add("controls-duplicate-kind", m)
    m = valid_manifest(); m["controls"] = [c for c in m["controls"] if c["kind"] != "zero_input"]; add("controls-missing-zero", m)
    m = valid_manifest(); m["controls"][0]["input_id"] = "missing"; add("controls-input-missing", m)
    m = valid_manifest(); m["controls"][0]["input_sha256"] = "0"*64; add("controls-input-sha-mismatch", m)
    m = valid_manifest();
    for c in m["controls"]:
        if c["kind"] == "zero_input": c["input_id"] = "nb-001"
    add("controls-zero-with-id", m)

    # outcomes
    for field in ADMISSION_SCHEMA["outcome_fields"]:
        m = valid_manifest(); m["outcomes"].pop(field); add(f"missing-outcome-{field}", m)
    m = valid_manifest(); m["outcomes"]["extra"] = 1; add("unknown-outcome-field", m)
    m = valid_manifest(); m["outcomes"]["task_metric"] = float('nan'); add("outcome-metric-nan", m)
    m = valid_manifest(); m["outcomes"]["task_metric"] = float('inf'); add("outcome-metric-inf", m)
    m = valid_manifest(); m["outcomes"]["task_metric"] = -0.1; add("outcome-metric-neg", m)
    m = valid_manifest(); m["outcomes"]["task_metric"] = 1.1; add("outcome-metric-high", m)
    m = valid_manifest(); m["outcomes"]["stoi"] = 1.1; add("outcome-stoi-high", m)
    m = valid_manifest(); m["outcomes"]["pesq"] = 5.1; add("outcome-pesq-high", m)
    m = valid_manifest(); m["outcomes"]["log_spectral_distance"] = -1; add("outcome-lsd-neg", m)
    m = valid_manifest(); m["outcomes"]["alignment_samples"] = -1; add("outcome-alignment-neg", m)
    m = valid_manifest(); m["outcomes"]["alignment_samples"] = 96001; add("outcome-alignment-high", m)
    m = valid_manifest(); m["outcomes"]["first_output_ms"] = -1; add("outcome-first-neg", m)
    m = valid_manifest(); m["outcomes"]["peak_abs"] = 4.1; add("outcome-peak-high", m)
    m = valid_manifest(); m["outcomes"]["clipped_fraction"] = 1.1; add("outcome-clipped-high", m)
    m = valid_manifest(); m["outcomes"]["nonfinite_count"] = 1; add("outcome-nonfinite-count", m)
    m = valid_manifest(); m["outcomes"]["sample_count"] = 0; add("outcome-sample-zero", m)
    m = valid_manifest(); m["outcomes"]["output_sample_rate_hz"] = 123; add("outcome-output-rate", m)

    # rights
    for field in ADMISSION_SCHEMA["rights_fields"]:
        m = valid_manifest(); m["rights"].pop(field); add(f"missing-rights-{field}", m)
    m = valid_manifest(); m["rights"]["extra"] = 1; add("unknown-rights-field", m)
    for field in ADMISSION_SCHEMA["rights_fields"]:
        m = valid_manifest(); m["rights"][field] = ""; add(f"rights-{field}-empty", m)

    # positive schema control
    add("schema-control", valid_manifest(), expected_ok=True)

    return cases


def admission_summary() -> dict[str, Any]:
    cases = admission_cases()
    rejected = [c for c in cases if c["status"] == "rejected"]
    accepted = [c for c in cases if c["status"] == "accepted_schema_control"]
    control = accepted[0] if accepted else {"accepted": False}
    if accepted:
        control = dict(accepted[0])
        control["accepted"] = True
        control["checks"] = len(ADMISSION_SCHEMA["manifest_fields"])
    return {
        "cases": cases,
        "control": control,
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(rejected),
            "accepted_schema_controls": len(accepted),
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "network_used": False,
            "model_executed": False,
            "weights_loaded": False,
            "audio_read": False,
            "feature_input_read": False,
            "runtime_invoked": False,
        },
    }


def build_contract() -> dict[str, Any]:
    identity = board_row_identity()
    absence = probe_absence()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "profile_phrases": list(PROFILE_PHRASES),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "not_qualified": True,
            "qualification_status": "not_qualified",
            "promotion": "defer",
            "production_exposure": "DEFER",
            "registered": False,
            "default_enabled": False,
            "expose_as_processor": False,
            "incomplete": True,
            "missing_result_qualifies": False,
        },
        "exact_scope": "Task-local Vocos-BWE blocker evidence: source/absence pins, fail-closed Restoration admission, blocked profile accounting and eight blocked release gates. No model, weights, runtime, cohort or result.",
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": identity["projection"],
        "board_row_sha256": identity["sha256"],
        "linked_rows": identity["linked_rows"],
        "linked_rows_sha256": identity["linked_rows_sha256"],
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "network_used": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "home_absence_probes": list(HOME_ABSENCE_PROBES),
        "required_artifacts": [dict(a) for a in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "release_gates": [dict(g) for g in RELEASE_GATES],
        "restoration_profile_requirements": [dict(r) for r in RESTORATION_PROFILE_ROWS],
        "quality_outcomes": [dict(r) for r in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(r) for r in TIMING_ROWS],
        "admission_contract": ADMISSION_SCHEMA,
        "required_results": REQUIRED_RESULTS,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "qualification": QUALIFICATION,
        "non_claims": list(NON_CLAIMS),
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "preserved": True,
            "sdk_compatible": False,
            "model_io_claimed": False,
            "sdk_callback_invoked": False,
        },
        "reproduction": {
            "commands": ["python3 run.py all", "python3 -m unittest -v test_reference.py", "python3 verify.py"],
            "cold_start_repeats": 3,
            "interpreter": "Python 3.12, standard library only",
            "network_required": False,
            "runtime_required": False,
        },
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    identity = board_row_identity()
    absence = probe_absence()
    pins = check_pins()
    admission = admission_summary()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "contract_sha256": object_digest(contract),
        "linked_row_identity": identity,
        "boundary_pins": pins["boundary_pins"],
        "source_pins": pins["source_pins"],
        "absence_evidence": absence,
        "admission": admission,
        "disposition": contract["disposition"],
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "qualification": QUALIFICATION,
        "required_results": REQUIRED_RESULTS,
        "required_artifacts": [dict(a) for a in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "gates": [dict(g) for g in RELEASE_GATES],
        "restoration_profile": {"profile": PROFILE_LABEL, "rows": [dict(r) for r in RESTORATION_PROFILE_ROWS]},
        "quality_outcomes": {"rows": [dict(r) for r in QUALITY_OUTCOME_ROWS]},
        "timing": {"rows": [dict(r) for r in TIMING_ROWS]},
        "non_claims": list(NON_CLAIMS),
        "public_v0_geometry": contract["public_v0_geometry"],
        "reproduction": contract["reproduction"],
    }
    # determinism guard
    absence_ok = absence["summary"]["all_probes_absent"]
    report["qualification"]["all_release_gates_blocked"] = all(g["status"] == "blocked" for g in report["gates"])
    report["qualification"]["missing_result_promoted"] = False
    report["absence_evidence"]["summary"]["all_probes_absent"] = absence_ok
    return report


def validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
    }
    for key, value in required.items():
        if contract.get(key) != value:
            raise ValueError(f"contract_field:{key}")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    if contract.get("board_status_is_observation_only") is not True:
        raise ValueError("contract_board_status")
    if contract.get("profile_key") != PROFILE:
        raise ValueError("contract_profile")
    for name in ("release_gates", "exact_blockers", "required_artifacts", "restoration_profile_requirements"):
        if not isinstance(contract.get(name), list) or not contract.get(name):
            raise ValueError(f"contract_missing:{name}")
    if len(contract["release_gates"]) != 8:
        raise ValueError("gate_count")
    for gate in contract["release_gates"]:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("gate_not_blocked")
    for blocker in contract["exact_blockers"]:
        if blocker.get("status") != "open" or blocker.get("qualifies") is not False:
            raise ValueError("blocker_not_open")
