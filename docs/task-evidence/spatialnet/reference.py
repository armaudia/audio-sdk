# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence for SpatialNet (SDK-SPATIALNET).

This package is feasibility evidence only. It does not import, load, link,
execute, copy, vendor, or download SpatialNet source, weights, runtime, or any
synchronized multichannel corpus. It records exact blockers and a tiny
deterministic synthetic geometry/control only to keep the package verifiable;
synthetic controls do not qualify SpatialNet.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
from typing import Any, Dict, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
TASK_ID = "SDK-SPATIALNET"
TITLE = "SpatialNet"
COMPONENT = "spatialnet"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = "swarm/SDK-SPATIALNET"
REVIEWER = "reviewer-SPATIALNET"
PROFILE = "Spatial"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_asset_intake_incomplete_not_qualified"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "schemas/descriptor.schema.json":
        "9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba",
    "schemas/effective-config.schema.json":
        "55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
BOARD_STABLE_SHA256 = (
    "1f19a90b7997f2f245d32319a58259d1f93e6694d1110f4ee7352a28b2a809f9"
)
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)
TASK_PREFIX = "docs/task-evidence/spatialnet/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

BOUNDARY: Dict[str, Any] = {
    "format": {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
    },
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "processor_exposure": False,
    "adapter_exposure": False,
    "shared_build_change": False,
    "ci_change": False,
    "board_or_handoff_change": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "caller_assets_present": False,
    "real_audio": False,
    "real_multichannel_corpus": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "model_download": False,
    "weights_present": False,
    "runtime_present": False,
    "provider_default_or_abi_change": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No SpatialNet source, weights, runtime, adapter or synchronized multichannel corpus is present, loaded or executed.",
    "No real audio, multichannel recording, listening, device timing or benchmark result is produced.",
    "No source-reported quality, separation, dereverberation or RTF number is reproduced or promoted.",
    "No provider registration, descriptor, registry entry, default, ABI, shared-build or CI file is changed.",
    "No release, public admission or qualification result is claimed.",
    "Synthetic geometry/control outputs are deterministic controls only and never qualify SpatialNet.",
)

GATES: Tuple[Dict[str, Any], ...] = (
    {"id": "RG-01", "name": "exact_runnable_source", "status": "blocked", "qualifies": False, "missing": "exact pinned SpatialNet source revision and build/runtime lock"},
    {"id": "RG-02", "name": "exact_assets_and_rights", "status": "blocked", "qualifies": False, "missing": "exact weights, license/rights grant, and redistribution/usage permission"},
    {"id": "RG-03", "name": "synchronized_multichannel_corpus", "status": "blocked", "qualifies": False, "missing": "rights-cleared synchronized multichannel clean-target corpus with geometry metadata"},
    {"id": "RG-04", "name": "installed_v0_boundary", "status": "blocked", "qualifies": False, "missing": "opt-in intake without ABI, registry or default change"},
    {"id": "RG-05", "name": "task_matched_evidence", "status": "blocked", "qualifies": False, "missing": "task-matched held-out localization/activity/extraction/array enhancement evidence"},
    {"id": "RG-06", "name": "spatial_profile_evidence", "status": "blocked", "qualifies": False, "missing": "geometry, timestamp calibration, leakage, target damage, channel loss and room/reference change evidence"},
    {"id": "RG-07", "name": "device_timing_and_pacing", "status": "blocked", "qualifies": False, "missing": "target-device timing, pacing, clock sync and deadline evidence"},
    {"id": "RG-08", "name": "public_admission_review", "status": "blocked", "qualifies": False, "missing": "independent review and explicit opt-in release decision"},
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "B-01",
        "blocker": "No exact runnable SpatialNet source revision, build lock or runtime is present in this workspace/worktree.",
        "reopen": "Supply a pinned source revision, exact build/runtime lock, and reproducible execution instructions with immutable hashes.",
    },
    {
        "id": "B-02",
        "blocker": "No exact SpatialNet weights, model license, redistribution terms or rights-cleared usage grant are present.",
        "reopen": "Supply exact weights with SHA-256, byte count, license terms, and rights/redistribution review allowing the intended use.",
    },
    {
        "id": "B-03",
        "blocker": "No synchronized multichannel clean-target corpus with array geometry/timestamp metadata is present; mono evidence cannot score array enhancement.",
        "reopen": "Supply a rights-cleared synchronized multichannel corpus with geometry, calibration, source/target/reference conditions, and clean targets.",
    },
    {
        "id": "B-04",
        "blocker": "No Spatial-profile matched evidence, device timing, or opt-in/public admission review exists.",
        "reopen": "Run task-matched held-out Spatial-profile evaluation with measured timing, leakage/target-damage/channel-loss reporting, and independent opt-in review.",
    },
)

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "inventory-blocker",
        "path": "audio-benchmark-platform/plan/INVENTORY.json",
        "needle": '"finding": "No local SpatialNet weights/adapter and no synchronized multichannel clean-target corpus; mono evidence cannot score array enhancement."',
    },
    {
        "id": "candidate-matrix",
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "needle": "Spatial and speaker,SpatialNet,unavailable/blocked,No local SpatialNet weights/adapter and no synchronized multichannel clean-target corpus; mono evidence cannot score array enhancement.,Multichannel WPE; identity,research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md; research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
    },
    {
        "id": "spatial-trials",
        "path": "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md",
        "needle": "| SpatialNet | No SpatialNet weights/adapter; staged EARS files are mono. Existing WPE multichannel evidence is a different DSP task. | Not run; requires synchronized multi-mic recordings with geometry and clean target references. |",
    },
    {
        "id": "spatial-profile",
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "needle": "| Spatial | Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions. Compare localization/activity/extraction with task-matched held-out labels. Report leakage, target damage, channel loss, and changes in room/reference conditions. |",
    },
)


class ReferenceRejection(ValueError):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
    if not isinstance(text, str):
        raise ValueError("json_input_must_be_text")

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
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


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: Dict[str, str] = {}
    result: List[Tuple[str, str]] = []
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
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(sorted(BOUNDARY_PINS)) + local_pin_keys()


README_PATH = TASK_DIR / "README.md"


def readme_pin_rows() -> List[Tuple[str, str]]:
    text = README_PATH.read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0], text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            if not line.startswith("| `") or not line.endswith("` |"):
                raise ValueError("digest_table_row_malformed")
            key, digest = [part.strip() for part in line.strip("|").split("|")]
            if not (key.startswith("`") and key.endswith("`")):
                raise ValueError("digest_table_key_malformed")
            if not (digest.startswith("`") and digest.endswith("`")):
                raise ValueError("digest_table_digest_malformed")
            rows.append((key[1:-1], digest[1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"] if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ValueError("task_row_not_unique")
    stable = {field: rows[0][field] for field in LINK_FIELDS}
    digest = object_digest(stable)
    if digest != BOARD_STABLE_SHA256:
        raise ValueError("unexpected_stable_board_identity")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
    }


def source_lines() -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for item in SOURCE_LINES:
        path = SOURCE_ROOT / item["path"]
        text = path.read_text(encoding="utf-8")
        if item["needle"] not in text:
            raise ValueError("source_line_mismatch:" + item["id"])
        line_no = text.splitlines().index(next(line for line in text.splitlines() if item["needle"] in line)) + 1
        entries.append({
            "id": item["id"],
            "path": item["path"],
            "line": line_no,
            "sha256": sha256_file(path),
            "text": item["needle"],
        })
    return {"entries": entries, "line_count": len(entries)}


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("source_pin_stale:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("boundary_pin_stale:" + path)
    source_lines()


def stable_board_row() -> Dict[str, Any]:
    # Stable identity only. Never hash the mutable full TASKS.json.
    return {
        "component": COMPONENT,
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        "id": TASK_ID,
        "mode": "feasibility",
        "repository": REPOSITORY,
        "title": TITLE,
    }


def synthetic_control() -> Dict[str, Any]:
    # Deterministic synthetic geometry/control only. Not SpatialNet.
    mics_nm = [(-50000000, 0, 0), (0, 0, 0), (50000000, 0, 0)]
    speed = 343000000000  # nm/s
    sr = SAMPLE_RATE_HZ
    source = (1, 0, 0)
    ref = mics_nm[1]
    delays = []
    for mic in mics_nm:
        d = (mic[0] - ref[0]) * source[0] + (mic[1] - ref[1]) * source[1] + (mic[2] - ref[2]) * source[2]
        t = -d / speed
        delays.append(round(t * sr))
    # impulse at sample 10 in ref channel
    length = 64
    channels = [[0.0] * length for _ in mics_nm]
    for ch, delay in zip(channels, delays):
        idx = 10 - delay
        if 0 <= idx < length:
            ch[idx] = 1.0
    # align by subtracting delay (shift back)
    aligned = []
    for ch, delay in zip(channels, delays):
        out = [0.0] * length
        for i, v in enumerate(ch):
            j = i + delay
            if 0 <= j < length:
                out[j] = v
        aligned.append(out)
    peaks = [max(range(length), key=lambda i: abs(ch[i])) for ch in aligned]
    return {
        "kind": "deterministic_synthetic_geometry_delay_control",
        "qualifies": False,
        "not_spatialnet": True,
        "sample_rate_hz": sr,
        "microphones_nm": [list(m) for m in mics_nm],
        "source_direction_unit": list(source),
        "reference_mic_index": 1,
        "expected_sample_delays": delays,
        "aligned_peak_indices": peaks,
        "all_peaks_aligned": len(set(peaks)) == 1,
    }


def scope_base(worktree: Path) -> str | None:
    for ref in SCOPE_BASE_REFS:
        proc = subprocess.run(["git", "-C", str(worktree), "rev-parse", "--verify", ref], capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            return ref
    return None


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    proc = subprocess.run(["git", "-C", str(worktree), "diff", "--name-only", base + "...HEAD"], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise ValueError("scope_diff_failed:" + proc.stderr.strip())
    return [line for line in proc.stdout.splitlines() if line.strip()]


def scope_violations(changed: Sequence[str]) -> List[str]:
    return [path for path in changed if not path.startswith(TASK_PREFIX)]



def invalid_json_cases() -> Dict[str, Any]:
    samples = ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', "")
    results = []
    for index, sample in enumerate(samples):
        rejected = False
        try:
            strict_loads(sample)
        except ValueError:
            rejected = True
        results.append({"id": "json-" + str(index), "rejected": rejected})
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for row in results if not row["rejected"]), "all_rejected": all(row["rejected"] for row in results)}


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        digest + "  source:duplicate\n" + digest + "  source:duplicate\n",
        "abc  source:short\n",
        digest + "  /absolute\n",
        digest + "  source:../escape\n",
    )
    results = []
    for index, sample in enumerate(samples):
        rejected = False
        try:
            parse_pin_lines(sample)
        except ValueError:
            rejected = True
        results.append({"id": "pin-" + str(index), "rejected": rejected})
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for row in results if not row["rejected"]), "all_rejected": all(row["rejected"] for row in results)}


def missing_asset_adverse() -> Dict[str, Any]:
    probes = [
        {"id": "missing-source", "path": "data/sources/spatialnet/model.bin"},
        {"id": "missing-weights", "path": "data/models/spatialnet/weights.pt"},
        {"id": "missing-corpus", "path": "data/corpora/spatialnet/multichannel.wav"},
    ]
    results = []
    for probe in probes:
        present = (SOURCE_ROOT / probe["path"]).exists() or (SDK_ROOT / probe["path"]).exists()
        results.append({"id": probe["id"], "path": probe["path"], "present": present, "rejected_as_qualification": not present})
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for r in results if not r["rejected_as_qualification"]), "all_rejected": all(r["rejected_as_qualification"] for r in results), "note": "Missing assets block qualification; absence is not a runtime/rights/quality result."}


def report_payload() -> Dict[str, Any]:
    validate_asset_pins()
    control = synthetic_control()
    board = board_link()
    json_adv = invalid_json_cases()
    pin_adv = invalid_pin_cases()
    missing_asset = missing_asset_adverse()
    adverse_all = json_adv["all_rejected"] and pin_adv["all_rejected"] and missing_asset["all_rejected"]
    return {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "format": dict(BOUNDARY["format"]),
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "board_link": board,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_lines": source_lines(),
        "source_reported": {
            "entries": [
                {"id": "SR-01", "claim": "SpatialNet unavailable/blocked: no local weights/adapter and no synchronized multichannel clean-target corpus", "source": "research/voice-enhancement-20261101/candidate_matrix.csv:59"},
                {"id": "SR-02", "claim": "No SpatialNet weights/adapter; staged EARS files are mono; WPE evidence is different DSP task", "source": "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md"},
            ],
            "qualifies": False,
            "separation": "Source-reported provenance only. None reproduced, promoted, or qualified.",
        },
        "synthetic_control": control,
        "adverse": {
            "all_rejected": adverse_all,
            "invalid_json": json_adv,
            "invalid_pins": pin_adv,
            "missing_asset_probe": missing_asset,
        },
        "asset_resolution": {
            "present": False,
            "required_asset_count": 0,
            "note": "No caller assets present; absence is not a runtime, rights or quality result.",
            "workspace_found": [],
            "sdk_worktree_found": [],
            "searched_prefixes": [
                "data/sources/spatialnet",
                "data/models/spatialnet",
                "data/envs/spatialnet",
                "data/corpora/spatialnet",
            ],
        },
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "caller_supplied_shape_only": False,
            "real_local_model_output": False,
            "real_audio": False,
            "real_multichannel_corpus": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
            "release_claim": False,
        },
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "comparison": "exact SHA-256 over bytes; no tolerance",
            "fresh_builds": 3,
        },
        "identity_control": {
            "label": "synthetic geometry delay alignment control, not SpatialNet",
            "qualifies": False,
            "all_peaks_aligned": control["all_peaks_aligned"],
        },
        "no_missing_result_qualifies_candidate": True,
        "reopening_conditions": [b["reopen"] for b in EXACT_BLOCKERS],
        "missing_evidence": [g["missing"] for g in GATES],
        "rate_profile": {
            "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "applies": False,
            "note": "Spatial profile applies; Rate profile not selected for this task row.",
        },
        "spatial_profile": {
            "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md:20",
            "qualifies": False,
            "items": [
                {"id": "geometry_layout", "status": "blocked", "qualifies": False, "synthetic_control": "integer mic positions; no real array"},
                {"id": "timestamp_calibration", "status": "blocked", "qualifies": False, "synthetic_control": "no device clock"},
                {"id": "source_target_reference_permissions", "status": "blocked", "qualifies": False, "synthetic_control": "no real recording/permissions"},
                {"id": "task_matched_labels", "status": "blocked", "qualifies": False, "synthetic_control": "no localization/activity/extraction labels"},
                {"id": "leakage_target_damage_channel_loss", "status": "blocked", "qualifies": False, "synthetic_control": "no real target/interferer"},
                {"id": "room_reference_changes", "status": "blocked", "qualifies": False, "synthetic_control": "no room/reference change strata"},
            ],
        },
    }


def report_bytes() -> bytes:
    return canonical_bytes(report_payload())


def sidecar_bytes(report_payload_bytes: bytes) -> bytes:
    return (sha256_bytes(report_payload_bytes) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload_bytes: bytes, sidecar_payload: bytes) -> bytes:
    items: List[Tuple[str, str]] = []
    for path, digest in sorted(SOURCE_PINS.items()):
        items.append((digest, "source:" + path))
    for path, digest in sorted(BOUNDARY_PINS.items()):
        items.append((digest, path))
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            digest = sha256_bytes(report_payload_bytes)
        elif name == "report.json.sha256":
            digest = sha256_bytes(sidecar_payload)
        else:
            digest = sha256_file(TASK_DIR / name)
        items.append((digest, TASK_PREFIX + name))
    items.sort(key=lambda row: row[1])
    return ("".join(d + "  " + k + "\n" for d, k in items)).encode("utf-8")


def contract_payload(report_payload_bytes: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any]) -> Dict[str, Any]:
    local_pins = {k.split("/", 3)[-1]: d for d, k in parse_pin_lines(sources_payload.decode("utf-8")) if k.startswith(TASK_PREFIX)}
    return {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "format": report["format"],
        "boundary": report["boundary"],
        "scope": report["scope"],
        "gates": report["gates"],
        "exact_blockers": report["exact_blockers"],
        "negative_claims": report["negative_claims"],
        "board_link": report["board_link"],
        "source_reported": report["source_reported"],
        "source_pins": report["source_pins"],
        "boundary_pins": report["boundary_pins"],
        "artifact_pins": local_pins,
        "report_sha256": sha256_bytes(report_payload_bytes),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
    }


def contract_bytes(report_payload_bytes: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = strict_loads(report_payload_bytes.decode("utf-8"))
    return canonical_bytes(contract_payload(report_payload_bytes, sidecar_payload, sources_payload, report))
