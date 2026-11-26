# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local blocker evidence for SDK-SPEECH-RATE-METER-INTON-CORE.

The pinned playback-speed research note records speech-rate-meter / inton-core as
an MIT C++ reference reporting wpm, articulation rate and pause statistics, with
desktop/Qt heritage and low maintenance. It also records the repository locator
``https://github.com/zhitko/speech-rate-meter``. No immutable source revision,
reviewed license/notice bundle, build/runtime, model asset, test fixture, audio
corpus, timing measurement or matched rate evidence is present in this workspace.

This module emits an explicit ``DEFER`` / ``incomplete`` /
``not_qualified`` blocker package. It includes a deterministic stdlib-only
synthetic boundary surrogate that exercises rate/timestamp accounting and
fail-closed validation only. The surrogate is not speech-rate-meter, not
inton-core, not a speech recognizer, and no surrogate observation qualifies the
candidate.

Nothing here downloads, copies, imports, loads or executes speech-rate-meter,
inton-core, a runtime, a corpus or a device clock. It does not register a
provider, change installed v0, a descriptor, a registry, a default, a shared
build, a dependency lock or CI, and it makes no benchmark, listening, timing or
release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-SPEECH-RATE-METER-INTON-CORE"
TITLE = "speech-rate-meter / inton-core"
SLUG = "speech-rate-meter-inton-core"
COMPONENT = "speech-rate-meter-inton-core"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-SPEECH-RATE-METER-INTON-CORE"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-SPEECH-RATE-METER-INTON-CORE"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "source_revision_rights_and_runtime_admission"

UPSTREAM_REPOSITORY = "https://github.com/zhitko/speech-rate-meter"
UPSTREAM_COMMIT: str | None = None
UPSTREAM_LICENSE_CLAIM = "MIT (reported by pinned research note; unverified here)"
UPSTREAM_LICENSE_STATUS = "reported_unverified"
UPSTREAM_SOURCE_PRESENT = False

SOURCE_CHECKOUT_PATH = "data/checkouts/speech-rate-meter"
RUNTIME_ENV_PATH = "data/envs/speech-rate-meter-inton-core"

PLAYBACK_CANDIDATES_PATH = "cpp-library/pipeline-validation/playback-speed-candidates.md"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
AUDIO_SDK_README_PATH = "audio-benchmark-platform/plan/audio-sdk/README.md"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "id": TASK,
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "40861c923d39b839bff199b0d5144db9e2b160d5c2be8fdd71cf462be6864d6e"
)

FORMAT: Dict[str, Any] = {
    "channels": 1,
    "clock": "synthetic-sample-coordinate-not-device",
    "frame_samples": 160,
    "input_format": "float32",
    "sample_rate_hz": 16000,
}

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "speech-a", "kind": "speech", "duration_ms": 1200, "syllables": 4, "words": 3},
    {"id": "pause-a", "kind": "pause", "duration_ms": 300, "syllables": 0, "words": 0},
    {"id": "speech-b", "kind": "speech", "duration_ms": 900, "syllables": 3, "words": 2},
    {"id": "pause-b", "kind": "pause", "duration_ms": 200, "syllables": 0, "words": 0},
    {"id": "speech-c", "kind": "speech", "duration_ms": 600, "syllables": 2, "words": 2},
)

REQUIRED_ASSET_FIELDS = {
    "algorithmic_latency_samples",
    "channels",
    "frame_samples",
    "input_format",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_commit",
    "source_path",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "present_behavior": "validate_identity_and_geometry_only; do_not_load_or_execute_in_this_package",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source_path and runtime_path are caller-owned absolute existing paths",
        "runtime_sha256 matches the runtime artifact",
        "source_commit is a 40-hex revision with reviewed license/notice evidence",
        "channels is 1, sample_rate_hz is 16000, frame_samples is 160, input_format is float32",
        "algorithmic_latency_samples is a non-negative integer",
        "no download, copy, build, import, load or execution occurs here",
    ],
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_unpinned_unverified",
        "requirement": "Supply the exact speech-rate-meter / inton-core source at an immutable 40-hex commit with reviewed license and notice evidence, verified locally without a network download.",
        "state": "The pinned research note records the repository and an MIT claim, but no immutable commit, reviewed license text, notice bundle, source digest or local checkout is present. Nothing was downloaded or fabricated.",
    },
    {
        "id": "runtime_and_build_absent",
        "requirement": "Provide a pinned, offline, reproducible build/runtime environment for the exact candidate, including dependency versions and deterministic execution instructions.",
        "state": "No local checkout, build artifact, runtime environment or deterministic execution trace exists. Desktop/Qt heritage is reported, but no pinned runtime was admitted.",
    },
    {
        "id": "rights_and_scope_unresolved",
        "requirement": "Provide written rights/scope evidence for source, dependencies, evaluation corpora and any derived outputs before any external or product-facing use.",
        "state": "MIT is reported by the research note but not verified here; dependency and corpus rights are unknown. No rights record is admitted.",
    },
    {
        "id": "task_geometry_and_metrics_unmapped",
        "requirement": "Map candidate outputs to exact source timestamps, WPM/articulation-rate/pause definitions, units, windowing and invalid/nonfinite behavior at the declared audio geometry.",
        "state": "The note names reported metrics but provides no pinned geometry, timestamp contract, window definition or machine-readable output schema.",
    },
    {
        "id": "matched_rate_evidence_absent",
        "requirement": "Provide rights-cleared matched evidence covering 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial windows, with independent controls and failure cases.",
        "state": "No candidate output, corpus, control, listening, timing or device evidence exists. Synthetic surrogate rows in this package do not qualify.",
    },
    {
        "id": "provider_intake_not_ready",
        "requirement": "Before any provider/default/shared-build/CI/registry change, supply opt-in provider intake evidence, exact-head review and target-runtime timing.",
        "state": "No provider, descriptor, registry, default, ABI, shared build or CI change is made. This package is task-local evidence only.",
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_revision_and_license", "Immutable 40-hex source revision with reviewed license, notice bundle and clean checkout."),
    ("pinned_runtime_and_deterministic_build", "Pinned offline runtime/build with dependency digests and deterministic execution trace."),
    ("rights_and_scope_cleared", "Written rights/scope for source, dependencies, corpora and outputs."),
    ("timestamp_and_metric_contract", "Exact source-timestamp mapping, WPM/articulation/pause definitions, units and windowing."),
    ("matched_rate_cohort", "Rights-cleared matched cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial windows."),
    ("independent_controls_and_failures", "Independent controls, invalid/missing/nonfinite rejection and adverse-case evidence."),
    ("target_runtime_timing", "Target-runtime first-output/tail/availability/pacing/deadline/memory measurements."),
    ("opt_in_provider_intake", "OFF-by-default opt-in provider intake, descriptor/catalog review and explicit owner default decision."),
)

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_run": False,
    "device_timing_measured": False,
    "downloaded": False,
    "implementation_added": False,
    "listening_performed": False,
    "network_used": False,
    "provider_registered": False,
    "public_abi_changed": False,
    "real_assets_used": False,
    "registry_or_default_changed": False,
    "release_claim": False,
    "runtime_executed": False,
    "shared_build_or_ci_changed": False,
    "source_imported": False,
    "task_local_only": True,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX + " only",
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No speech-rate-meter or inton-core source, binary, weight, runtime or corpus was downloaded, built, loaded or executed.",
    "No WPM, articulation-rate, pause, timing, benchmark, listening or release result is claimed for the candidate.",
    "The synthetic boundary surrogate is not speech-rate-meter / inton-core and cannot qualify the candidate.",
    "No provider, descriptor, registry, installed v0 path, default, public ABI, shared build, dependency lock or CI was changed.",
    "A missing or hash-matched placeholder is never admitted as a pinned candidate artifact.",
)

SOURCE_PINS: Dict[str, str] = {
    AUDIO_SDK_README_PATH: "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    INVENTORY_PATH: "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    PLAYBACK_CANDIDATES_PATH: "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    VERIFICATION_PATH: "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "LICENSES/Apache-2.0.txt": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES: Tuple[str, ...] = (
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

README_MARKERS = {
    "source": ("<!-- DIGEST_TABLE_SOURCE_START -->", "<!-- DIGEST_TABLE_SOURCE_END -->"),
    "boundary": ("<!-- DIGEST_TABLE_BOUNDARY_START -->", "<!-- DIGEST_TABLE_BOUNDARY_END -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->", "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
README_SECTIONS = ("source", "boundary", "artifacts")
ARTIFACT_TABLE_EXCLUDED = {"SOURCES.sha256", "SOURCES.sha256.license"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def strict_loads(text: str) -> Any:
    def _reject(token: str) -> Any:
        raise ValueError("nonfinite_json_constant:" + token)

    def _object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate_json_key:" + key)
            obj[key] = value
        return obj

    value = json.loads(text, parse_constant=_reject, object_pairs_hook=_object)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return math.copysign(1.0, value) < 0.0 and value == 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_negative_zero(v) for v in value)
    return False


def board_row_digest() -> str:
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def workspace_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    if override:
        return Path(override).resolve()
    for parent in HERE.parents:
        if (parent / "audio-benchmark-platform").is_dir() and (parent / "worktrees").is_dir():
            return parent
    return SDK_ROOT.parents[1]


def resolve_source_path(name: str) -> Path:
    root = workspace_root()
    candidate = root / name
    if candidate.exists():
        return candidate
    return SDK_ROOT / name


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_not_object")
    keys = set(manifest.keys())
    if keys != REQUIRED_ASSET_FIELDS:
        raise ValueError("manifest_key_set_mismatch")
    source_commit = manifest["source_commit"]
    if not isinstance(source_commit, str) or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
        raise ValueError("source_commit_invalid")
    for key in ("source_path", "runtime_path", "input_format"):
        if not isinstance(manifest[key], str) or not manifest[key]:
            raise ValueError(key + "_invalid")
    if manifest["input_format"] != "float32":
        raise ValueError("input_format_invalid")
    for key in ("channels", "sample_rate_hz", "frame_samples", "algorithmic_latency_samples"):
        if not _is_int(manifest[key]) or manifest[key] < 0:
            raise ValueError(key + "_invalid")
    if manifest["channels"] != 1:
        raise ValueError("channels_invalid")
    if manifest["sample_rate_hz"] != 16000:
        raise ValueError("sample_rate_hz_invalid")
    if manifest["frame_samples"] != 160:
        raise ValueError("frame_samples_invalid")
    sha = manifest["runtime_sha256"]
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
        raise ValueError("runtime_sha256_invalid")
    source_path = Path(manifest["source_path"])
    runtime_path = Path(manifest["runtime_path"])
    if not source_path.is_absolute() or not runtime_path.is_absolute():
        raise ValueError("path_not_absolute")
    if not source_path.exists() or not runtime_path.exists():
        raise ValueError("path_missing")
    actual = sha256_file(runtime_path)
    if actual != sha:
        raise ValueError("runtime_sha256_mismatch")
    return {
        "accepted": False,
        "reason": "candidate_blocked_source_unverified_and_no_execution",
        "runtime_sha256_actual": actual,
        "validated_identity_only": True,
    }


def _rejected_asset_cases() -> Dict[str, Any]:
    base = {
        "algorithmic_latency_samples": 0,
        "channels": 1,
        "frame_samples": 160,
        "input_format": "float32",
        "runtime_path": str(HERE / "reference.py"),
        "runtime_sha256": sha256_file(HERE / "reference.py"),
        "sample_rate_hz": 16000,
        "source_commit": "0123456789abcdef0123456789abcdef01234567",
        "source_path": str(HERE),
    }
    bad_missing = dict(base)
    del bad_missing["source_commit"]
    bad_key = dict(base)
    bad_key["extra"] = True
    bad_nonfinite = dict(base)
    bad_nonfinite["algorithmic_latency_samples"] = math.nan
    bad_float = dict(base)
    bad_float["frame_samples"] = 160.0
    bad_sha = dict(base)
    bad_sha["runtime_sha256"] = "0" * 63
    bad_path = dict(base)
    bad_path["runtime_path"] = str(HERE / "missing-runtime.bin")
    bad_rel = dict(base)
    bad_rel["source_path"] = "relative/path"
    bad_geom = dict(base)
    bad_geom["sample_rate_hz"] = 48000
    cases = {
        "missing_field": bad_missing,
        "unknown_field": bad_key,
        "nonfinite": bad_nonfinite,
        "float_field": bad_float,
        "bad_sha": bad_sha,
        "missing_path": bad_path,
        "relative_path": bad_rel,
        "bad_geometry": bad_geom,
    }
    out: Dict[str, Any] = {}
    for name, manifest in cases.items():
        try:
            validate_caller_asset(manifest)
            out[name] = {"rejected": False}
        except Exception as exc:  # noqa: BLE001
            out[name] = {"rejected": True, "error": type(exc).__name__, "message": str(exc)}
    try:
        out["schema_control"] = validate_caller_asset(base)
    except Exception as exc:  # noqa: BLE001
        out["schema_control"] = {"rejected": True, "error": type(exc).__name__, "message": str(exc)}
    return out


def synthetic_rate_accounting(segments: Sequence[Dict[str, Any]] = SEGMENTS) -> Dict[str, Any]:
    total_ms = 0
    speech_ms = 0
    pause_ms = 0
    syllables = 0
    words = 0
    for seg in segments:
        kind = seg["kind"]
        dur = int(seg["duration_ms"])
        if dur < 0:
            raise ValueError("negative_duration")
        total_ms += dur
        if kind == "speech":
            speech_ms += dur
            syllables += int(seg["syllables"])
            words += int(seg["words"])
        elif kind == "pause":
            pause_ms += dur
        else:
            raise ValueError("unknown_kind")
    articulation_wpm = (words * 60000 / speech_ms) if speech_ms else 0.0
    speaking_wpm = (words * 60000 / total_ms) if total_ms else 0.0
    syllables_per_s = (syllables * 1000 / speech_ms) if speech_ms else 0.0
    return {
        "articulation_wpm": round(articulation_wpm, 9),
        "pause_ms": pause_ms,
        "segments": [dict(s) for s in segments],
        "speaking_wpm": round(speaking_wpm, 9),
        "speech_ms": speech_ms,
        "syllables_per_s": round(syllables_per_s, 9),
        "total_ms": total_ms,
        "total_syllables": syllables,
        "total_words": words,
    }


def deterministic_surrogate(frames: Sequence[Sequence[float]], config: Dict[str, Any]) -> Dict[str, Any]:
    validate_config(config)
    if not isinstance(frames, list) or not frames:
        raise ValueError("frames_invalid")
    emitted: List[List[float]] = []
    accepted = 0
    for i, frame in enumerate(frames):
        validate_frame(frame)
        accepted += len(frame)
        # boundary surrogate: copy with fixed gain 1.0 and timestamp accounting only
        emitted.append([float(x) for x in frame])
    metrics = synthetic_rate_accounting()
    return {
        "accepted_samples": accepted,
        "emitted_frames": len(emitted),
        "emitted_samples": sum(len(f) for f in emitted),
        "first_output_sample": 0,
        "last_output_sample": accepted - 1 if accepted else -1,
        "metrics_surrogate_only": metrics,
        "qualified": False,
        "surrogate": True,
    }


def validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ValueError("config_not_object")
    required = {"channels", "clock", "frame_samples", "input_format", "sample_rate_hz"}
    if set(config.keys()) != required:
        raise ValueError("config_key_set_mismatch")
    if config["channels"] != 1 or config["sample_rate_hz"] != 16000 or config["frame_samples"] != 160:
        raise ValueError("config_geometry_invalid")
    if config["input_format"] != "float32":
        raise ValueError("config_input_format_invalid")
    if not isinstance(config["clock"], str) or not config["clock"]:
        raise ValueError("config_clock_invalid")


def validate_frame(frame: Any) -> None:
    if not isinstance(frame, list) or len(frame) != 160:
        raise ValueError("frame_shape_invalid")
    for x in frame:
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise ValueError("frame_value_type_invalid")
        xf = float(x)
        if not math.isfinite(xf):
            raise ValueError("frame_nonfinite")
        if abs(xf) > 1.0:
            raise ValueError("frame_out_of_range")


def adverse_control() -> Dict[str, Any]:
    cfg = dict(FORMAT)
    good_frame = [0.0] * 160
    cases: Dict[str, Any] = {}
    def record(name: str, fn):
        try:
            fn()
            cases[name] = {"rejected": False}
        except Exception as exc:  # noqa: BLE001
            cases[name] = {"rejected": True, "error": type(exc).__name__, "message": str(exc)}
    record("missing_config_key", lambda: validate_config({"channels": 1, "sample_rate_hz": 16000, "frame_samples": 160}))
    record("bad_geometry", lambda: validate_config({"channels": 2, "sample_rate_hz": 16000, "frame_samples": 160, "input_format": "float32"}))
    record("nan", lambda: validate_frame([float('nan')] + [0.0] * 159))
    record("inf", lambda: validate_frame([float('inf')] + [0.0] * 159))
    record("bool", lambda: validate_frame([True] + [0.0] * 159))
    record("out_of_range", lambda: validate_frame([1.5] + [0.0] * 159))
    record("wrong_length", lambda: validate_frame([0.0] * 159))
    record("bad_frames_container", lambda: deterministic_surrogate([], cfg))
    ok = deterministic_surrogate([good_frame, good_frame], cfg)
    cases["valid_control"] = {"rejected": False, "qualified": ok["qualified"], "surrogate": ok["surrogate"]}
    return cases


def acceptance_profile() -> Dict[str, Any]:
    return {
        "blocked_cases": [
            "no exact upstream source, runtime or rights record admitted",
            "no WPM/articulation/pause output reproduced against candidate",
            "no 1x, rate-change, unfamiliar-speech, music, silence, rebuffer, drift or final-partial candidate measurement",
            "no target-device timing, pacing or deadline evidence",
            "no independent listening or task-matched scoring",
        ],
        "mapped_cases": [
            "deterministic synthetic speech/pause timestamp accounting surrogate",
            "source/output sample mapping and final-partial accounting in surrogate",
            "fail-closed config/frame/asset validation",
            "explicit missing-result and not-qualified reporting",
        ],
        "name": PROFILE,
        "not_applicable": [
            "no real candidate artifact exists to evaluate",
            "surrogate is not speech-rate-meter or inton-core",
            "no rights-cleared corpus, device clock or listener available",
        ],
        "source": VERIFICATION_PATH,
    }


def qualification_block() -> Dict[str, Any]:
    return {
        "status": QUALIFICATION,
        "not_qualified": True,
        "readiness": "incomplete",
        "release_claim": False,
        "missing_result_promoted": False,
        "source_present": False,
        "runtime_present": False,
        "rights_cleared": False,
    }


def report_body() -> Dict[str, Any]:
    controls = {
        "asset": _rejected_asset_cases(),
        "adverse": adverse_control(),
        "synthetic_rate_accounting": synthetic_rate_accounting(),
        "surrogate_run": deterministic_surrogate([[0.0] * 160, [0.1] * 160], dict(FORMAT)),
    }
    return {
        "acceptance_profile": acceptance_profile(),
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "reviewer": REVIEWER,
            "worktree": CLAIM_WORKTREE,
        },
        "component_id": COMPONENT,
        "controls": controls,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": req, "status": "blocked"}
            for gate, req in GATE_REQUIREMENTS
        ],
        "missing_results": [
            "exact source revision and reviewed license/notice",
            "pinned offline runtime/build and deterministic trace",
            "rights/scope decisions for source, dependencies, corpora and outputs",
            "timestamp/metric contract mapped to candidate outputs",
            "rights-cleared matched rate cohort with required strata",
            "independent controls, adverse/failure and invalid/nonfinite evidence",
            "target-runtime timing and memory/deadline measurements",
            "opt-in provider intake and explicit default decision",
        ],
        "no_missing_result_qualifies_candidate": True,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the exact source revision and reviewed license/notice, a pinned offline "
            "runtime/build, written rights/scope, a mapped timestamp/metric contract, rights-"
            "cleared matched rate evidence with required strata and controls, target-runtime "
            "timing, and OFF-by-default opt-in provider intake with independent exact-head "
            "review. Until then the candidate stays DEFER, incomplete and not qualified."
        ),
        "scenario": {
            "id": "speech-rate-meter-inton-core-rate-blocker-v1",
            "task_geometry": "speech-rate/WPM/articulation/pause estimation from audio timestamps",
            "is_mono_baseline": True,
            "upstream_geometry_verified": False,
        },
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "status": STATUS,
        "surrogate": {
            "candidate_result": False,
            "is_speech_rate_meter": False,
            "is_inton_core": False,
            "model_free": True,
            "runtime_free": True,
            "note": "Deterministic boundary surrogate only; no candidate output, audio, model or runtime.",
        },
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "license_claim": UPSTREAM_LICENSE_CLAIM,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "note": "Pinned research note names repository and MIT claim; no immutable revision, reviewed license bundle or checkout is present.",
            "repository": UPSTREAM_REPOSITORY,
            "source_present": UPSTREAM_SOURCE_PRESENT,
        },
    }


def contract_payload() -> Dict[str, Any]:
    return {
        "acceptance_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "note": "Only the stable linked-row identity is gated. The mutable full plan/swarm/TASKS.json is never read into, hashed by or pinned to this package.",
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [{"id": g, "qualifies": False, "requirement": r, "status": "blocked"} for g, r in GATE_REQUIREMENTS],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked or rejected result is promoted to a pass",
            "no source, runtime, corpus or asset is downloaded, copied, imported, loaded or executed",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": sorted(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
        "Supply the exact source revision and reviewed license/notice, a pinned offline "
        "runtime/build, written rights/scope, a mapped timestamp/metric contract, rights-"
        "cleared matched rate evidence with required strata and controls, target-runtime "
        "timing, and OFF-by-default opt-in provider intake with independent exact-head "
        "review. Until then the candidate stays DEFER, incomplete and not qualified."
    ),
        "reviewer": REVIEWER,
        "scenario": {
            "id": "speech-rate-meter-inton-core-rate-blocker-v1",
            "task_geometry": "speech-rate/WPM/articulation/pause estimation from audio timestamps",
            "is_mono_baseline": True,
            "upstream_geometry_verified": False,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "license_claim": UPSTREAM_LICENSE_CLAIM,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "note": "Pinned research note names repository and MIT claim; no immutable revision, reviewed license bundle or checkout is present.",
            "repository": UPSTREAM_REPOSITORY,
            "source_present": UPSTREAM_SOURCE_PRESENT,
        },
    }


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def build_report() -> Dict[str, Any]:
    report = _plain(report_body())
    report["contract_sha256"] = sha256(contract_bytes())
    if has_negative_zero(report):
        raise ValueError("negative_zero_in_report")
    return report


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report)


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def _local_manifest_paths() -> List[str]:
    return sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: List[Tuple[str, str]] = []
    for name, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + name))
    for name, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + name))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned workspace/repo root.",
        "# sdk: paths are relative to this SDK worktree.",
        f"# Full mutable plan/swarm/TASKS.json is never hashed; only board_row.stable_sha256={BOARD_ROW_STABLE_SHA256} is gated.",
    ]
    for digest, path in rows:
        lines.append(f"{digest}  {path}")
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for n, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError(f"malformed_pin_line:{n}")
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:") or path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{n}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{n}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + n for n in SOURCE_PINS}
            | {"sdk:" + n for n in BOUNDARY_PINS}
            | {TASK_PREFIX + n for n in _local_manifest_paths()})


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + n for n in SOURCE_PINS},
        "boundary": {"sdk:" + n for n in BOUNDARY_PINS},
        "artifacts": {n for n in _local_manifest_paths() if n not in ARTIFACT_TABLE_EXCLUDED},
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    result: Dict[str, List[Tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: List[Tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({k for k, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def render_artifact_table() -> str:
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        path = HERE / name
        digest = "0" * 64 if name == "README.md" else sha256_file(path)
        rows.append(f"| `{name}` | `{digest}` | {path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start = text.index(README_MARKERS["artifacts"][0])
    end = text.index(README_MARKERS["artifacts"][1], start) + len(README_MARKERS["artifacts"][1])
    return text[:start] + block + text[end:]


def verify_readme_digests(text: str) -> Dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {k for k, _ in parsed[section]}
        if actual_keys != expected[section]:
            raise ValueError(f"readme_key_mismatch:{section}")
        for key, digest in parsed[section]:
            if section == "source":
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = resolve_source_path(key[len("source:"):])
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = SDK_ROOT / key[len("sdk:"):]
            else:
                expected_digest = "0" * 64 if key == "README.md" else sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if key != "README.md" and path.is_file() and sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        digest = "0" * 64 if key == "README.md" else sha256_file(HERE / key)
        line = f"| `{key}` | `{digest}` | {(HERE / key).stat().st_size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = ['{"a":1,"a":2}', '{"a": NaN}', '{"a": Infinity}', '[]', '{"a":1} trailing']
    bad_pins = ["not-a-pin", "0" * 64 + " source:one", "0" * 63 + "  source:one", "0" * 64 + "  other:one"]
    bad_readme = ["# no tables", "<!-- DIGEST_TABLE_SOURCE_START -->\n| `source:x` | `zz` |\n<!-- DIGEST_TABLE_SOURCE_END -->"]
    def count(items, fn):
        n = 0
        for item in items:
            try:
                fn(item)
            except Exception:  # noqa: BLE001
                n += 1
        return n
    return {
        "bad_json_rejected": count(bad_json, strict_loads),
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": count(bad_pins, parse_pin_lines),
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": count(bad_readme, parse_readme_digest_tables),
        "bad_readme_total": len(bad_readme),
    }
