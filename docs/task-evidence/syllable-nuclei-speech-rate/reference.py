# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER blocker evidence for SDK-SYLLABLE-NUCLEI-SPEECH-RATE.

The pinned playback-speed candidate note records "Syllable nuclei" as the
de Jong & Wempe 2009 speech-rate method, with a note that it needs tuning per
language and that the original Praat script is GPL; the matrix recommends
reimplementing the peak-picking method rather than copying the GPL script.

No exact runnable reimplementation, tuned language configuration, annotated
reference corpus, rights-cleared audio, target runtime, listening result, or
device timing evidence is present in this workspace. This package emits an
explicit DEFER / incomplete / not_qualified blocker record. It includes a
deterministic stdlib-only synthetic boundary surrogate that exercises
source-timestamp and syllable-rate arithmetic only. The surrogate is not the
de Jong & Wempe method, not a Praat implementation, not a speech-rate detector,
and no surrogate observation qualifies the candidate.

Nothing here downloads, copies, imports, loads or executes a Praat script,
speech-rate detector, runtime, corpus or device clock. It does not register a
provider, change installed v0, a descriptor, a registry, a default, a shared
build, a dependency lock or CI, and it makes no benchmark, listening, timing,
device, or release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")

TASK = "SDK-SYLLABLE-NUCLEI-SPEECH-RATE"
TITLE = "Syllable-nuclei speech rate"
SLUG = "syllable-nuclei-speech-rate"
COMPONENT = "syllable-nuclei-speech-rate"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-SYLLABLE-NUCLEI-SPEECH-RATE"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
PROFILE = "Rate"
STATUS = "proposal_only_blocked_incomplete_not_qualified"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

BOARD_ROW_STABLE_FIELDS: dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "id": TASK,
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = "6075e8188040d129d5ae876914eba6cec13358b27ca10ea3bf6fc5d09984dc09"

FORMAT: dict[str, Any] = {
    "channels": 1,
    "frame_samples": 160,
    "sample_format": "float32",
    "sample_rate_hz": 16000,
}

SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/audio-bench/EVIDENCE_SPEC.md": "f37ff1c0083f99387548b5369cdad0f55c2d31a9b75e422073b570cd80ca009c",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS: dict[str, str] = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "schemas/descriptor.schema.json": "9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba",
    "schemas/effective-config.schema.json": "55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES: tuple[str, ...] = (
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

PINNED_LOCAL_FILES: tuple[str, ...] = tuple(name for name in LOCAL_FILES if name != "SOURCES.sha256")

LICENSE_SIDECARS: tuple[str, ...] = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)

SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"

EXACT_BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "B-01",
        "blocker": "No exact runnable syllable-nuclei implementation exists locally. The pinned note names the de Jong & Wempe 2009 method and warns the original Praat script is GPL; no permissive reimplementation, source revision, dependency lock or runtime is pinned.",
        "reopen": "Supply an exact caller-owned reimplementation/source revision with reviewed license/notice evidence, dependency/runtime lock, and deterministic execution instructions; verify hashes without downloading or executing the source in this package.",
    },
    {
        "id": "B-02",
        "blocker": "No exact tuned language/configuration contract exists. The method needs per-language tuning (intensity/silence/pitch/voicing thresholds, minimum pause, minimum dip) and no pinned config, schema, or validation fixture is present.",
        "reopen": "Provide a typed, versioned tuning/config schema with pinned defaults per declared language/speaking-style scope and fail-closed validation on missing/invalid/nonfinite fields.",
    },
    {
        "id": "B-03",
        "blocker": "No rights-cleared matched syllable/rate evidence exists. There is no annotated corpus, reference syllable-nuclei output, speech-rate ground truth, or independent control/failure cohort.",
        "reopen": "Run a rights-cleared matched cohort with independent syllable annotations, exact source timestamps, 1x/rate-change/unfamiliar speech/music/silence/rebuffer/drift/final-partial cases, and report false positives/negatives separately.",
    },
    {
        "id": "B-04",
        "blocker": "No target-runtime timing, listening, or opt-in intake evidence exists. No device clock, callback deadline, pacing, memory, listener result, descriptor, or release decision is present.",
        "reopen": "Provide target-runtime timing/memory/availability evidence, any required listening/preservation evidence for rate use, and an OFF-by-default opt-in intake decision with no default/ABI/shared-build/CI change.",
    },
)

GATES: tuple[dict[str, Any], ...] = (
    {"id": "RG-01", "name": "exact_runnable_source", "missing": "exact permissive reimplementation/source revision and runtime lock", "qualifies": False, "status": "blocked"},
    {"id": "RG-02", "name": "rights_and_license", "missing": "reviewed license/notice for source, dependencies, corpus and outputs; GPL Praat script not copied", "qualifies": False, "status": "blocked"},
    {"id": "RG-03", "name": "tuning_and_config_contract", "missing": "typed per-language tuning/config schema and deterministic validation", "qualifies": False, "status": "blocked"},
    {"id": "RG-04", "name": "source_timestamp_mapping", "missing": "exact source-interval/syllable timestamp mapping at declared geometry", "qualifies": False, "status": "blocked"},
    {"id": "RG-05", "name": "matched_rate_evidence", "missing": "rights-cleared matched cohort covering rate profile strata and controls", "qualifies": False, "status": "blocked"},
    {"id": "RG-06", "name": "failure_and_control_evidence", "missing": "invalid/missing/nonfinite rejection, identity/mismatch controls, and adverse cases", "qualifies": False, "status": "blocked"},
    {"id": "RG-07", "name": "target_runtime_timing", "missing": "target-device timing, pacing, memory and availability evidence", "qualifies": False, "status": "blocked"},
    {"id": "RG-08", "name": "opt_in_provider_intake", "missing": "OFF-by-default opt-in intake/release review with no default/ABI/shared-build/CI change", "qualifies": False, "status": "blocked"},
)

NEGATIVE_CLAIMS: tuple[str, ...] = (
    "No de Jong & Wempe Praat script, reimplementation, syllable detector, ASR, runtime, corpus or audio asset was downloaded, copied, imported, loaded or executed.",
    "No syllable count, speech-rate, WPM, pause, timing, benchmark, listening, device or release result is claimed for the candidate.",
    "The synthetic boundary surrogate is not syllable-nuclei speech-rate and cannot qualify the candidate.",
    "No provider, descriptor, registry, installed v0 path, default, public ABI, shared build, dependency lock or CI was changed.",
    "A missing, placeholder, or hash-matched metadata-only asset never qualifies as runnable evidence.",
)

BOUNDARY: dict[str, Any] = {
    "adapter_exposure": False,
    "asset_bundled": False,
    "board_or_handoff_change": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "format": dict(FORMAT),
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "shared_build_change": False,
}

SCOPE: dict[str, Any] = {
    "benchmark": False,
    "caller_assets_present": False,
    "device_timing": False,
    "listening": False,
    "model_download": False,
    "provider_default_or_abi_change": False,
    "real_audio": False,
    "release_claim": False,
    "synthetic_only": True,
    "task_local_only": True,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": str(path), "exists": path.is_file(), "bytes": len(data), "sha256": sha256_bytes(data)}


def strict_loads(text: str) -> Any:
    if not isinstance(text, str):
        raise ValueError("json_input_must_be_text")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite_json_constant:" + token)

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json:" + str(error)) from error

    def check(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError("nonfinite_float")
        if isinstance(item, dict):
            for child in item.values():
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
        elif not isinstance(item, (str, int, float, bool)) and item is not None:
            raise ValueError("unsupported_json_type")

    check(value)
    return value


def strict_load(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(k) or has_negative_zero(v) for k, v in value.items())
    if isinstance(value, list):
        return any(has_negative_zero(v) for v in value)
    return False


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        relative = key.split(":", 1)[1] if key.startswith("source:") else key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen.add(key)
        result.append((digest, key))
    return result


def allowed_pin_keys() -> set[str]:
    keys = {f"source:{k}" for k in SOURCE_PINS}
    keys |= set(BOUNDARY_PINS)
    keys |= {TASK_PREFIX + name for name in PINNED_LOCAL_FILES}
    return keys


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def _local_manifest_paths() -> tuple[str, ...]:
    return LOCAL_FILES


def board_row_digest() -> str:
    return sha256_bytes(canonical_bytes(BOARD_ROW_STABLE_FIELDS))


# ---- Synthetic boundary surrogate (not candidate) ----

def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def validate_surrogate_config(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config_not_object")
    required = {"channels", "frame_samples", "sample_rate_hz", "segments"}
    if set(config.keys()) != required:
        raise ValueError("config_key_set")
    if config["channels"] != 1 or config["sample_rate_hz"] != 16000 or config["frame_samples"] != 160:
        raise ValueError("config_geometry")
    segments = config["segments"]
    if not isinstance(segments, list) or not segments:
        raise ValueError("segments_invalid")
    seen: set[str] = set()
    last_end = 0
    validated: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, dict):
            raise ValueError("segment_not_object")
        req = {"id", "kind", "start_sample", "end_sample", "syllable_count"}
        if set(seg.keys()) != req:
            raise ValueError("segment_key_set")
        sid = seg["id"]
        if not isinstance(sid, str) or not sid:
            raise ValueError("segment_id")
        if sid in seen:
            raise ValueError("segment_id_duplicate")
        seen.add(sid)
        kind = seg["kind"]
        if kind not in {"speech", "pause"}:
            raise ValueError("segment_kind")
        start = seg["start_sample"]
        end = seg["end_sample"]
        count = seg["syllable_count"]
        for name, val in (("start", start), ("end", end), ("count", count)):
            if isinstance(val, bool) or not isinstance(val, int):
                raise ValueError(f"{name}_not_int")
        if start < 0 or end <= start or start < last_end:
            raise ValueError("segment_bounds")
        if kind == "pause" and count != 0:
            raise ValueError("pause_count")
        if kind == "speech" and count < 0:
            raise ValueError("speech_count")
        last_end = end
        validated.append({"id": sid, "kind": kind, "start_sample": start, "end_sample": end, "syllable_count": count})
    return {"channels": 1, "frame_samples": 160, "sample_rate_hz": 16000, "segments": validated}


def run_synthetic_surrogate(config: dict[str, Any]) -> dict[str, Any]:
    cfg = validate_surrogate_config(config)
    sr = cfg["sample_rate_hz"]
    rows = []
    speech_samples = 0
    speech_syllables = 0
    total_samples = 0
    for seg in cfg["segments"]:
        dur_samples = seg["end_sample"] - seg["start_sample"]
        dur_s = dur_samples / sr
        row = {
            "id": seg["id"],
            "kind": seg["kind"],
            "source_start_sample": seg["start_sample"],
            "source_end_sample": seg["end_sample"],
            "duration_s": round(dur_s, 9),
            "syllable_count": seg["syllable_count"],
        }
        if seg["kind"] == "speech":
            speech_samples += dur_samples
            speech_syllables += seg["syllable_count"]
            row["syllables_per_speech_second"] = round((seg["syllable_count"] / dur_s), 9) if dur_s > 0 else 0.0
        else:
            row["syllables_per_speech_second"] = None
        total_samples = max(total_samples, seg["end_sample"])
        rows.append(row)
    speech_s = speech_samples / sr
    total_s = total_samples / sr
    return {
        "surrogate": True,
        "candidate_is_syllable_nuclei": False,
        "qualified": False,
        "format": dict(FORMAT),
        "segments": rows,
        "summary": {
            "total_samples": total_samples,
            "total_seconds": round(total_s, 9),
            "speech_samples": speech_samples,
            "speech_seconds": round(speech_s, 9),
            "speech_syllables": speech_syllables,
            "syllables_per_speech_second": round((speech_syllables / speech_s), 9) if speech_s > 0 else 0.0,
            "syllables_per_total_second": round((speech_syllables / total_s), 9) if total_s > 0 else 0.0,
            "final_partial_samples": total_samples % 160,
        },
    }


def valid_surrogate_config() -> dict[str, Any]:
    return {
        "channels": 1,
        "frame_samples": 160,
        "sample_rate_hz": 16000,
        "segments": [
            {"id": "speech-a", "kind": "speech", "start_sample": 0, "end_sample": 19200, "syllable_count": 4},
            {"id": "pause-a", "kind": "pause", "start_sample": 19200, "end_sample": 24000, "syllable_count": 0},
            {"id": "speech-b", "kind": "speech", "start_sample": 24000, "end_sample": 38400, "syllable_count": 3},
            {"id": "pause-b", "kind": "pause", "start_sample": 38400, "end_sample": 41600, "syllable_count": 0},
            {"id": "speech-c-tail", "kind": "speech", "start_sample": 41600, "end_sample": 51237, "syllable_count": 2},
        ],
    }


# ---- Asset contract / adverse cases ----

REQUIRED_ASSET_FIELDS = {
    "algorithmic_latency_samples",
    "channels",
    "config_sha256",
    "entrypoint",
    "frame_samples",
    "license_id",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_commit",
    "source_path",
}


def validate_asset_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_not_object")
    if set(manifest.keys()) != REQUIRED_ASSET_FIELDS:
        raise ValueError("manifest_key_set")
    commit = manifest["source_commit"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("source_commit")
    for key in ("runtime_sha256", "config_sha256"):
        digest = manifest[key]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"{key}_digest")
    for key in ("channels", "sample_rate_hz", "frame_samples", "algorithmic_latency_samples"):
        val = manifest[key]
        if isinstance(val, bool) or not isinstance(val, int):
            raise ValueError(f"{key}_not_int")
        if val < 0:
            raise ValueError(f"{key}_negative")
    if manifest["channels"] != 1 or manifest["sample_rate_hz"] != 16000 or manifest["frame_samples"] != 160:
        raise ValueError("geometry_mismatch")
    if manifest["license_id"] not in {"MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause"}:
        raise ValueError("license_not_permissive_allowlist")
    for key in ("source_path", "runtime_path", "entrypoint"):
        val = manifest[key]
        if not isinstance(val, str) or not val:
            raise ValueError(f"{key}_empty")
    for key in ("source_path", "runtime_path"):
        p = Path(manifest[key])
        if not p.is_absolute():
            raise ValueError(f"{key}_not_absolute")
        if ".." in p.parts:
            raise ValueError(f"{key}_traversal")
        if not p.exists():
            raise ValueError(f"{key}_missing")
    runtime = Path(manifest["runtime_path"]).read_bytes()
    if sha256_bytes(runtime) != manifest["runtime_sha256"]:
        raise ValueError("runtime_sha256_mismatch")
    return {
        "accepted": False,
        "validated_identity_only": True,
        "qualifies": False,
        "reason": "metadata_and_hash_shape_only_no_execution",
    }


def adverse_cases() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def add(name: str, fn) -> None:
        rejected = False
        reason = ""
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            rejected = True
            reason = type(exc).__name__ + ":" + str(exc)
        cases.append({"id": name, "rejected": rejected, "reason": reason})

    base = valid_surrogate_config()
    add("missing_config_key", lambda: validate_surrogate_config({k: v for k, v in base.items() if k != "segments"}))
    add("unknown_config_key", lambda: validate_surrogate_config({**base, "extra": 1}))
    add("bad_geometry_channels", lambda: validate_surrogate_config({**base, "channels": 2}))
    add("bad_geometry_rate", lambda: validate_surrogate_config({**base, "sample_rate_hz": 8000}))
    add("nan_count", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][0], "syllable_count": float("nan")}]}))
    add("inf_count", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][0], "syllable_count": float("inf")}]}))
    add("bool_count", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][0], "syllable_count": True}]}))
    add("negative_count", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][0], "syllable_count": -1}]}))
    add("pause_nonzero", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][1], "syllable_count": 1}]}))
    add("overlap", lambda: validate_surrogate_config({**base, "segments": [base["segments"][0], {**base["segments"][1], "start_sample": 100}]}))
    add("bad_kind", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][0], "kind": "music"}]}))
    add("unknown_segment_key", lambda: validate_surrogate_config({**base, "segments": [{**base["segments"][0], "extra": 1}]}))

    # asset manifest adverse
    tmp_runtime = HERE / ".tmp_runtime_asset_probe"
    tmp_runtime.write_bytes(b"runtime")
    try:
        good_manifest = {
            "algorithmic_latency_samples": 0,
            "channels": 1,
            "config_sha256": "0" * 64,
            "entrypoint": "syllable_nuclei:estimate",
            "frame_samples": 160,
            "license_id": "MIT",
            "runtime_path": str(tmp_runtime.resolve()),
            "runtime_sha256": sha256_bytes(b"runtime"),
            "sample_rate_hz": 16000,
            "source_commit": "0" * 40,
            "source_path": str(HERE.resolve()),
        }
        add("asset_missing_field", lambda: validate_asset_manifest({k: v for k, v in good_manifest.items() if k != "license_id"}))
        add("asset_unknown_field", lambda: validate_asset_manifest({**good_manifest, "extra": "x"}))
        add("asset_bad_sha", lambda: validate_asset_manifest({**good_manifest, "runtime_sha256": "abc"}))
        add("asset_bad_commit", lambda: validate_asset_manifest({**good_manifest, "source_commit": "HEAD"}))
        add("asset_relative_path", lambda: validate_asset_manifest({**good_manifest, "source_path": "relative/path"}))
        add("asset_traversal", lambda: validate_asset_manifest({**good_manifest, "runtime_path": str(HERE.resolve() / ".." / "x")}))
        add("asset_bad_geometry", lambda: validate_asset_manifest({**good_manifest, "sample_rate_hz": 44100}))
        add("asset_nonfinite_via_float_field", lambda: validate_asset_manifest({**good_manifest, "channels": 1.5}))
        add("asset_hash_mismatch", lambda: validate_asset_manifest({**good_manifest, "runtime_sha256": "1" * 64}))
        add("asset_missing_path", lambda: validate_asset_manifest({**good_manifest, "runtime_path": str(HERE.resolve() / "nope.bin")}))
        add("asset_gpl_license", lambda: validate_asset_manifest({**good_manifest, "license_id": "GPL-2.0"}))
    finally:
        try:
            tmp_runtime.unlink()
        except FileNotFoundError:
            pass

    return {
        "cases": cases,
        "case_count": len(cases),
        "rejected_count": sum(1 for c in cases if c["rejected"]),
        "accepted_count": sum(1 for c in cases if not c["rejected"]),
        "all_rejected": all(c["rejected"] for c in cases),
    }


def strict_rejection_examples() -> dict[str, Any]:
    bad_json = ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '']
    json_rejected = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except ValueError:
            json_rejected += 1
    digest = "a" * 64
    bad_pins = [
        digest + "  source:dup\n" + digest + "  source:dup\n",
        "abc  source:short\n",
        digest + "  /abs\n",
        digest + "  source:../escape\n",
    ]
    pins_rejected = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            pins_rejected += 1
    bad_readme = [
        "<!-- digest-table: source --><!-- digest-table: boundary --><!-- digest-table: end --><!-- digest-table: end -->",
        "<!-- digest-table: source -->\n| Pin key | SHA-256 |\n| --- | --- |\n| bad | `abc` |\n<!-- digest-table: end -->\n<!-- digest-table: boundary -->\n| Pin key | SHA-256 |\n| --- | --- |\n<!-- digest-table: end -->",
    ]
    readme_rejected = 0
    for text in bad_readme:
        try:
            verify_readme_digests(text)
        except Exception:  # noqa: BLE001
            readme_rejected += 1
    return {
        "bad_json_rejected": json_rejected,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": pins_rejected,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": readme_rejected,
        "bad_readme_total": len(bad_readme),
    }


# ---- Report / contract / pins ----

def build_report() -> dict[str, Any]:
    probe_workspace = [
        "data/checkouts/syllable-nuclei-speech-rate",
        "data/models/syllable-nuclei-speech-rate",
        "data/envs/syllable-nuclei-speech-rate",
        "data/reference/syllable-nuclei-speech-rate",
    ]
    found = [p for p in probe_workspace if (SOURCE_ROOT / p).exists() or (SDK_ROOT / p).exists()]
    adverse = adverse_cases()
    surrogate = run_synthetic_surrogate(valid_surrogate_config())
    invalid_json = 0
    for text in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '']:
        try:
            strict_loads(text)
        except ValueError:
            invalid_json += 1
    invalid_pins = 0
    digest = "a" * 64
    for text in [digest + "  source:dup\n" + digest + "  source:dup\n", "abc  source:short\n", digest + "  /abs\n", digest + "  source:../escape\n"]:
        try:
            parse_pin_lines(text)
        except ValueError:
            invalid_pins += 1
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "proposal_only": True,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row": {
            "stable_fields": dict(BOARD_ROW_STABLE_FIELDS),
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
            "full_tasks_json_hashed": False,
            "mutable_fields_excluded": ["status", "owner", "claim", "review", "handoff", "blocked_reason", "dispatch_priority", "history", "write_scope", "deliverable", "acceptance", "evidence"],
        },
        "candidate_source_reported": {
            "method": "de Jong & Wempe 2009 syllable nuclei / Praat-style peak picking",
            "note": "Original Praat script is GPL; pinned matrix recommends reimplementation, not copying GPL script. Needs tuning per language.",
            "source": "cpp-library/pipeline-validation/playback-speed-candidates.md:95,193-211",
            "qualifies": False,
            "reproduced": False,
        },
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "gates": [dict(g) for g in GATES],
        "missing_evidence": [
            "exact permissive reimplementation/source revision and dependency/runtime lock",
            "reviewed license/notice evidence; GPL Praat script excluded from copying",
            "typed per-language tuning/config schema and validation fixture",
            "rights-cleared matched syllable/rate cohort with independent annotations",
            "rate-profile evidence: duration, pitch, transient audibility, playback buffering, speech preservation",
            "target-runtime timing/memory/availability and OFF-by-default intake review",
        ],
        "reopen_conditions": [b["reopen"] for b in EXACT_BLOCKERS],
        "caller_supplied_asset_contract": {
            "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_identity_and_geometry_only; do_not_load_or_execute_in_this_package",
            "required_fields": sorted(REQUIRED_ASSET_FIELDS),
        },
        "asset_probe": {"present": False, "searched_prefixes": probe_workspace, "found": found},
        "controls": {
            "synthetic_surrogate": surrogate,
            "adverse": adverse,
            "invalid_json_rejected": invalid_json,
            "invalid_json_total": 5,
            "invalid_pins_rejected": invalid_pins,
            "invalid_pins_total": 4,
        },
    }


def canonical_report_bytes(report: dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report) + b"\n"


def contract_payload(report: dict[str, Any] | None = None) -> dict[str, Any]:
    report = report or build_report()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "format": dict(FORMAT),
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "board_row": {
            "stable_fields": dict(BOARD_ROW_STABLE_FIELDS),
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
            "full_tasks_json_hashed": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "proposal_only": True,
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload()) + b"\n"


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for path in sorted(SOURCE_PINS):
        rows.append((f"source:{path}", sha256_file(SOURCE_ROOT / path)))
    for path in sorted(BOUNDARY_PINS):
        rows.append((path, sha256_file(SDK_ROOT / path)))
    for name in sorted(LOCAL_FILES):
        if name == "SOURCES.sha256":
            continue
        rows.append((TASK_PREFIX + name, sha256_file(HERE / name)))
    return ("".join(f"{digest}  {key}\n" for key, digest in rows)).encode("ascii")


README_START_SOURCE = "<!-- digest-table: source -->"
README_START_BOUNDARY = "<!-- digest-table: boundary -->"
README_START_ARTIFACT = "<!-- digest-table: artifacts -->"
README_END = "<!-- digest-table: end -->"


def _render_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Pin key | SHA-256 |", "| --- | --- |"]
    for key, digest in rows:
        lines.append(f"| `{key}` | `{digest}` |")
    return "\n".join(lines)


def readme_expected_tables(readme_text: str | None = None) -> dict[str, list[tuple[str, str]]]:
    src = [(f"source:{k}", v) for k, v in sorted(SOURCE_PINS.items())]
    bnd = sorted(BOUNDARY_PINS.items())
    art = []
    for n in sorted(LOCAL_FILES):
        if n == "SOURCES.sha256":
            continue
        if n == "README.md" and readme_text is not None:
            art.append((TASK_PREFIX + n, "0" * 64))
        else:
            art.append((TASK_PREFIX + n, sha256_file(HERE / n)))
    tables = {"source": src, "boundary": bnd, "artifacts": art}
    if readme_text is not None:
        # fixed-point self hash
        text = readme_text
        start = README_START_ARTIFACT
        if start in text and README_END in text.split(start, 1)[1]:
            before, rest = text.split(start, 1)
            _, after = rest.split(README_END, 1)
            rows = tables["artifacts"]
            for _ in range(8):
                candidate = before + start + "\n" + _render_table(rows) + "\n" + README_END + after
                readme_digest = sha256_bytes(candidate.encode("utf-8"))
                new_rows = [(k, readme_digest if k == TASK_PREFIX + "README.md" else d) for k, d in rows]
                if new_rows == rows:
                    break
                rows = new_rows
            tables["artifacts"] = rows
    return tables


def verify_readme_digests(text: str) -> dict[str, int]:
    tables = readme_expected_tables(text)
    markers = [("source", README_START_SOURCE), ("boundary", README_START_BOUNDARY), ("artifacts", README_START_ARTIFACT)]
    counts: dict[str, int] = {}
    for key, start in markers:
        if start not in text or README_END not in text.split(start, 1)[1]:
            raise ValueError(f"missing_marker:{key}")
        block = text.split(start, 1)[1].split(README_END, 1)[0]
        lines = [l for l in block.splitlines() if l.strip().startswith("| `")]
        rows: list[tuple[str, str]] = []
        for line in lines:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) != 2:
                raise ValueError(f"bad_row:{key}")
            k = parts[0].strip("`")
            d = parts[1].strip("`")
            if not re.fullmatch(r"[0-9a-f]{64}", d):
                raise ValueError(f"bad_digest:{key}:{k}")
            rows.append((k, d))
        if rows != tables[key]:
            raise ValueError(f"table_mismatch:{key}")
        counts[key] = len(rows)
    return counts


def update_readme_artifact_table(text: str) -> str:
    for _ in range(4):
        old = text
        tables = readme_expected_tables(text)
        for key, start in [("source", README_START_SOURCE), ("boundary", README_START_BOUNDARY), ("artifacts", README_START_ARTIFACT)]:
            if start not in text or README_END not in text.split(start, 1)[1]:
                raise ValueError(f"missing_marker:{key}")
            before, rest = text.split(start, 1)
            _, after = rest.split(README_END, 1)
            text = before + start + "\n" + _render_table(tables[key]) + "\n" + README_END + after
        if text == old:
            return text
    return text
