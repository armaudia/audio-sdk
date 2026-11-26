# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence for SpeechBrain disfluency/pause predictor.

Feasibility evidence only. No SpeechBrain model, checkpoint, runtime, audio,
label, benchmark, listening or device-timing artifact is loaded, downloaded,
executed or fabricated. The package records an exact external blocker: no
matching pretrained SpeechBrain disfluency/pause predictor head with exact
licensed source, weights, runtime and matched evidence was supplied.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK = "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR"
TITLE = "SpeechBrain disfluency/pause predictor"
COMPONENT = "speechbrain-disfluency-pause-predictor"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = "swarm/SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR"
REVIEWER = "reviewer-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR"
PROFILE = "rate"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_missing_exact_artifacts_not_qualified"
SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/speechbrain-disfluency-pause-predictor/caller-supplied/0.1"
SCHEMA_ENVELOPE = "audio-sdk/speechbrain-disfluency-pause-predictor/envelope/0.1"

SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIO_ROOT")
    candidates = [Path(override)] if override else []
    candidates.extend(HERE.parents)
    for candidate in candidates:
        if (candidate / "audio-benchmark-platform/plan/swarm/TASKS.json").is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()
TASK_PREFIX = "docs/task-evidence/speechbrain-disfluency-pause-predictor/"

# Source pins are workspace-relative.
SOURCE_PINS: Dict[str, str] = {
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

# Boundary pins are SDK-worktree-relative.
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "schemas/descriptor.schema.json": "9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba",
    "schemas/effective-config.schema.json": "55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea",
    "docs/task-evidence/silero-vad-pause-duration-rules/README.md": "b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f",
    "docs/task-evidence/silero-vad-pause-duration-rules/report.json": "9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d",
    "docs/task-evidence/source-vad-conditioning-for-playback/README.md": "26d98518eda620228808587d5a396f9111794e80c333cbf594c8365b9a21f135",
    "docs/task-evidence/source-vad-conditioning-for-playback/report.json": "1f180b14ef33466f0950fe9128aa88be1004aca141d762bffff96822e7ec007a",
    "docs/task-evidence/wavlm-acoustic-disfluency-model/README.md": "b49b861a20bfa4e37b8a4f4b4aa231d8e4542ebf6305c08d568268653021b447",
}

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "speechbrain-no-matching-head",
        "path": "research/tsm-followup-20261101/README.md",
        "line": 33,
        "text": "| SpeechBrain disfluency/pause predictor | Proposed frame/segment classifier for fillers, disfluencies or pauses | Official SpeechBrain model inventory checked | **No matching pretrained rate/disfluency head found.** SpeechBrain is a toolkit with ASR/VAD recipes, not an off-the-shelf preferred-speed predictor. No SpeechBrain disfluency checkpoint could be acquired/tested; existing Silero pause/VAD baselines are evaluated separately. |",
    },
    {
        "id": "inventory-blocked",
        "path": "audio-benchmark-platform/plan/INVENTORY.json",
        "line": 8274,
        "text": '      "id": "speechbrain-disfluency-pause-predictor",',
    },
    {
        "id": "rate-profile",
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "line": 21,
        "text": "| Rate | Measure source/output mapping, duration, pitch, transient audibility and playback buffering. Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window. Keep pause or filler decisions tied to source timestamps and measure speech preservation. |",
    },
)

BOARD_STABLE_SHA256 = "636df1080d129f276f9ae97216bd8a707da86acda911cd9127de5e00db077ee8"
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)

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

BOUNDARY: Dict[str, Any] = {
    "format": {"sample_rate_hz": 16000, "channels": 1, "sample_format": "float32", "frame_samples": 160},
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
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "model_download": False,
    "provider_default_or_abi_change": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No SpeechBrain model, checkpoint, recipe, runtime or dependency is downloaded, installed, imported or executed.",
    "No exact pretrained disfluency/pause predictor head, weights, source revision or runtime lock is present.",
    "No real audio, transcript, disfluency label, pause annotation or corpus is read, written or scored.",
    "No listening, device timing, callback deadline, pacing or buffer occupancy result is measured.",
    "No source-reported TSM scorecard claim is reproduced or promoted to a candidate result.",
    "No provider, descriptor, registry entry, default, ABI, shared build or CI file is changed.",
    "No benchmark, release, public admission or qualification result is claimed.",
    "A missing artifact or blocked gate never qualifies the candidate.",
)

REQUIRED_ASSETS: Tuple[Dict[str, Any], ...] = (
    {"asset_id": "speechbrain-disfluency-pause-predictor.source-revision", "role": "exact_runnable_source_revision", "storage": "external"},
    {"asset_id": "speechbrain-disfluency-pause-predictor.model-checkpoint", "role": "exact_pretrained_checkpoint_or_weights", "storage": "external"},
    {"asset_id": "speechbrain-disfluency-pause-predictor.runtime-lock", "role": "locked_runtime_and_dependencies", "storage": "external"},
    {"asset_id": "speechbrain-disfluency-pause-predictor.label-schema", "role": "typed_disfluency_pause_label_schema", "storage": "external"},
    {"asset_id": "speechbrain-disfluency-pause-predictor.cohort-manifest", "role": "rights_cleared_matched_cohort_manifest", "storage": "external"},
    {"asset_id": "speechbrain-disfluency-pause-predictor.reference-output", "role": "matched_reference_output_or_score_bundle", "storage": "external"},
)

BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "B-01",
        "blocker": "No exact runnable pretrained SpeechBrain disfluency/pause predictor head is present. The pinned TSM scorecard records that the official SpeechBrain model inventory was checked and no matching pretrained rate/disfluency head was found.",
        "reopen": "Supply an exact 40-hex source revision, reviewed license/terms, exact pretrained checkpoint/weights, and a locked runtime manifest by caller-owned SHA-256 and byte count; verify hashes without downloading or executing here.",
    },
    {
        "id": "B-02",
        "blocker": "No rights-cleared, frame/segment-labeled disfluency/pause cohort, label schema or matched reference output is present. SpeechBrain toolkit availability is not evidence of a qualified predictor artifact.",
        "reopen": "Supply a rights-reviewed cohort manifest, typed label schema, matched reference outputs and evaluation terms with exact digests and byte counts; absence remains non-qualifying until verified.",
    },
    {
        "id": "B-03",
        "blocker": "No Rate-profile evidence exists: no source/output mapping, duration, pitch/transient audibility, buffering, unfamiliar speech/music/silence, rebuffer/drift/final-partial, or timestamp-tied pause/filler preservation result is measured.",
        "reopen": "Run a rights-cleared matched cohort at installed 16 kHz mono float32/160-sample geometry and report exact source intervals, duration, pitch, transients, buffering, speech preservation and unknown/deletion behavior separately.",
    },
    {
        "id": "B-04",
        "blocker": "No opt-in adapter/provider intake or release decision exists. Default selection, registry exposure, ABI/shared-build/CI changes and release claims are out of scope and blocked.",
        "reopen": "After B-01..B-03 clear, obtain credential/counsel review and an application-local opt-in decision with no default, public registry or ABI change; keep public admission a separate later gate.",
    },
)

GATES: Tuple[Dict[str, Any], ...] = (
    {"id": "RG-01", "name": "exact_runnable_source", "status": "blocked", "qualifies": False, "missing": "exact source revision and reviewed license/terms"},
    {"id": "RG-02", "name": "exact_assets_and_rights", "status": "blocked", "qualifies": False, "missing": "six caller assets with SHA-256, byte count and rights review"},
    {"id": "RG-03", "name": "installed_v0_boundary", "status": "blocked", "qualifies": False, "missing": "opt-in intake without ABI, registry or default change"},
    {"id": "RG-04", "name": "typed_disfluency_pause_labels", "status": "blocked", "qualifies": False, "missing": "validated typed disfluency/pause label schema on matched input"},
    {"id": "RG-05", "name": "unknown_or_deletion_behavior", "status": "blocked", "qualifies": False, "missing": "measured unknown-span and deletion behavior"},
    {"id": "RG-06", "name": "rate_profile_evidence", "status": "blocked", "qualifies": False, "missing": "duration, pitch, transient, buffering and preservation evidence"},
    {"id": "RG-07", "name": "playback_pacing_and_listening", "status": "blocked", "qualifies": False, "missing": "target-device pacing, crossfade and listening result"},
    {"id": "RG-08", "name": "public_admission_review", "status": "blocked", "qualifies": False, "missing": "rights, counsel and opt-in release decision"},
)

WORKSPACE_PROBES: Tuple[str, ...] = (
    "data/checkouts/speechbrain",
    "data/checkouts/SpeechBrain",
    "data/models/speechbrain",
    "data/models/speechbrain-disfluency-pause-predictor",
    "data/envs/speechbrain",
    "docs/task-evidence/speechbrain-disfluency-pause-predictor/assets",
)
HOME_PROBES: Tuple[str, ...] = (
    "~/.cache/huggingface/hub/models--speechbrain",
    "~/.cache/torch/hub/checkpoints",
)



class ReferenceError(ValueError):
    pass


class ReferenceRejection(ReferenceError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code if not detail else f"{code}:{detail}")
        self.code = code
        self.detail = detail


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _reject_nonfinite(value: Any, path: str) -> None:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ReferenceError(f"nonfinite:{path}")
    if isinstance(value, dict):
        for k, v in value.items():
            _reject_nonfinite(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _reject_nonfinite(v, f"{path}[{i}]")


def strict_loads(text: str) -> Any:
    if not text or not text.strip():
        raise ReferenceError("empty_json")
    decoder = json.JSONDecoder(object_pairs_hook=_object_pairs_no_dupes)
    obj, end = decoder.raw_decode(text)
    if text[end:].strip():
        raise ReferenceError("trailing_content")
    _reject_nonfinite(obj, "$")
    return obj


def _object_pairs_no_dupes(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ReferenceError(f"duplicate_key:{k}")
        out[k] = v
    return out


def _check_keys(obj: Any, required: Sequence[str], allowed: Sequence[str], ctx: str) -> None:
    if not isinstance(obj, dict):
        raise ReferenceRejection("TYPE_INVALID", ctx)
    keys = list(obj.keys())
    req = list(required)
    allow = list(allowed)
    missing = [k for k in req if k not in obj]
    extra = [k for k in keys if k not in allow]
    if missing or extra or keys != allow:
        raise ReferenceRejection("SCHEMA_FIELD_SET", f"{ctx}:missing={missing}:extra={extra}")


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return AUDIO_ROOT / key[len("source:"):]
    if key.startswith("sdk:"):
        return SDK_ROOT / key[len("sdk:"):]
    return HERE / key


def allowed_pin_keys() -> List[str]:
    keys = [f"source:{p}" for p in SOURCE_PINS]
    keys += [f"sdk:{p}" for p in BOUNDARY_PINS]
    keys += list(LOCAL_PIN_PATHS)
    keys += ["report.json.sha256", "contract.json"]
    return sorted(set(keys))


def validate_source_pins() -> Dict[str, str]:
    out = {}
    for path, digest in SOURCE_PINS.items():
        target = AUDIO_ROOT / path
        if not target.is_file():
            raise ReferenceError(f"source_pin_missing:{path}")
        actual = sha256_file(target)
        if actual != digest:
            raise ReferenceError(f"source_pin_stale:{path}")
        out[f"source:{path}"] = actual
    return out


def validate_boundary_pins() -> Dict[str, str]:
    out = {}
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            raise ReferenceError(f"boundary_pin_missing:{path}")
        actual = sha256_file(target)
        if actual != digest:
            raise ReferenceError(f"boundary_pin_stale:{path}")
        out[f"sdk:{path}"] = actual
    return out


def board_link() -> Dict[str, Any]:
    task_path = AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    tasks = json.loads(task_path.read_text(encoding="utf-8"))["tasks"]
    row = next(t for t in tasks if t.get("id") == TASK)
    stable = {k: row[k] for k in LINK_FIELDS}
    digest = sha256_bytes(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if digest != BOARD_STABLE_SHA256:
        raise ReferenceError("board_stable_sha256_mismatch")
    return {
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "stable_fields": stable,
        "stable_sha256": digest,
    }


def absent_artifact_probe() -> Dict[str, Any]:
    workspace = []
    for rel in WORKSPACE_PROBES:
        p = AUDIO_ROOT / rel
        if p.exists():
            workspace.append(rel)
    sdk = []
    for rel in ["docs/task-evidence/speechbrain-disfluency-pause-predictor/assets"]:
        p = SDK_ROOT / rel
        if p.exists():
            sdk.append(rel)
    home = []
    for rel in HOME_PROBES:
        p = Path(os.path.expanduser(rel))
        if p.exists():
            home.append(rel)
    return {
        "note": "Path absence is not a runtime, rights or quality result.",
        "present": bool(workspace or sdk or home),
        "workspace_found": workspace,
        "sdk_worktree_found": sdk,
        "home_found": home,
        "searched_workspace_prefixes": list(WORKSPACE_PROBES),
        "searched_home_prefixes": list(HOME_PROBES),
    }


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    allowed = [
        "schema_id", "task_id", "candidate_id", "candidate_family", "fixture_id",
        "source_revision", "source_license_id", "runtime_lock_id", "label_schema_id",
        "cohort_manifest_id", "reference_output_id", "attestation", "rate_policy_id",
        "evidence_class", "credential_review_id", "counsel_review_id", "assets",
    ]
    _check_keys(manifest, allowed, allowed, "manifest")
    if manifest["schema_id"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("SCHEMA_ID_MISMATCH")
    if manifest["task_id"] != TASK:
        raise ReferenceRejection("TASK_ID_MISMATCH")
    if manifest["candidate_id"] != COMPONENT or manifest["candidate_family"] != "speechbrain-disfluency-pause-predictor":
        raise ReferenceRejection("CANDIDATE_ID_MISMATCH")
    if not isinstance(manifest["fixture_id"], str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,96}", manifest["fixture_id"]):
        raise ReferenceRejection("FIXTURE_ID_INVALID")
    if not isinstance(manifest["source_revision"], str) or not re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]):
        raise ReferenceRejection("SOURCE_REVISION_INVALID")
    for field in ["source_license_id", "runtime_lock_id", "label_schema_id", "cohort_manifest_id", "reference_output_id", "attestation", "rate_policy_id", "evidence_class", "credential_review_id", "counsel_review_id"]:
        v = manifest[field]
        if not isinstance(v, str) or not v.strip() or len(v) > 256:
            raise ReferenceRejection("TEXT_FIELD_INVALID", field)
    if manifest["evidence_class"] != "caller_supplied_shape_only":
        raise ReferenceRejection("EVIDENCE_CLASS_INVALID")
    if manifest["credential_review_id"] == manifest["counsel_review_id"]:
        raise ReferenceRejection("EVIDENCE_CLASS_COLLISION")
    assets = manifest["assets"]
    if not isinstance(assets, list) or len(assets) != len(REQUIRED_ASSETS):
        raise ReferenceRejection("ASSET_SET_MISMATCH")
    seen_ids = set()
    seen_paths = set()
    asset_allowed = ["asset_id", "path", "sha256", "byte_count", "storage", "license_id", "rights_attestation"]
    for asset in assets:
        _check_keys(asset, asset_allowed, asset_allowed, "asset")
        aid = asset["asset_id"]
        if aid in seen_ids:
            raise ReferenceRejection("ASSET_SET_MISMATCH", aid)
        seen_ids.add(aid)
        path = asset["path"]
        if not isinstance(path, str) or not path:
            raise ReferenceRejection("ASSET_PATH_INVALID")
        if not path.startswith("/"):
            raise ReferenceRejection("ASSET_PATH_NOT_ABSOLUTE")
        if ".." in Path(path).parts:
            raise ReferenceRejection("ASSET_PATH_TRAVERSAL")
        if path in seen_paths:
            raise ReferenceRejection("ASSET_PATH_DUPLICATE")
        seen_paths.add(path)
        if not _is_sha256(asset["sha256"]):
            raise ReferenceRejection("ASSET_SHA256_INVALID")
        bc = asset["byte_count"]
        if not isinstance(bc, int) or isinstance(bc, bool) or bc <= 0 or bc > 1_000_000_000:
            raise ReferenceRejection("ASSET_BYTE_COUNT_INVALID")
        if asset["storage"] != "external":
            raise ReferenceRejection("ASSET_STORAGE_INVALID")
        for f in ["license_id", "rights_attestation"]:
            if not isinstance(asset[f], str) or not asset[f].strip():
                raise ReferenceRejection("TEXT_FIELD_INVALID", f"asset.{f}")
    expected_ids = {a["asset_id"] for a in REQUIRED_ASSETS}
    if seen_ids != expected_ids:
        raise ReferenceRejection("ASSET_SET_MISMATCH")
    return manifest


def verify_assets(manifest: Dict[str, Any], supplied: Dict[str, bytes]) -> Dict[str, Any]:
    validate_manifest(manifest)
    for asset in manifest["assets"]:
        path = asset["path"]
        if path not in supplied:
            raise ReferenceRejection("ASSET_ABSENT", asset["asset_id"])
        data = supplied[path]
        if len(data) != asset["byte_count"]:
            raise ReferenceRejection("ASSET_BYTE_COUNT_MISMATCH", asset["asset_id"])
        if sha256_bytes(data) != asset["sha256"]:
            raise ReferenceRejection("ASSET_HASH_MISMATCH", asset["asset_id"])
    return {"accepted": True, "count": len(manifest["assets"]), "qualifies": False, "shape_only": True}


# --- synthetic envelope (model-free, not qualifying) ---

RATE_MIN = 0.75
RATE_MAX = 1.5
MIN_DWELL = 3200  # 200 ms @ 16k
FIXTURE_SAMPLES = 16000


def valid_envelope() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ENVELOPE,
        "task_id": TASK,
        "candidate_id": COMPONENT,
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "source_end": FIXTURE_SAMPLES,
        "synthetic": True,
        "segments": [
            {"id": "seg-00-unknown", "class": "unknown", "source_start": 0, "source_end": 3200, "rate": "1", "retained": True},
            {"id": "seg-01-speech", "class": "speech", "source_start": 3200, "source_end": 8000, "rate": "4/5", "retained": True},
            {"id": "seg-02-silence", "class": "silence", "source_start": 8000, "source_end": 12800, "rate": "4/3", "retained": True},
            {"id": "seg-03-speech", "class": "speech", "source_start": 12800, "source_end": 16000, "rate": "1", "retained": True},
        ],
    }


def _parse_rate(rate: Any, ctx: str) -> float:
    if isinstance(rate, bool) or not isinstance(rate, str):
        raise ReferenceRejection("RATE_INVALID", ctx)
    m = re.fullmatch(r"([1-9][0-9]*)(?:/([1-9][0-9]*))?", rate)
    if not m:
        raise ReferenceRejection("RATE_INVALID", ctx)
    num = int(m.group(1))
    den = int(m.group(2)) if m.group(2) else 1
    if den == 0:
        raise ReferenceRejection("RATE_INVALID", ctx)
    return num / den


def validate_envelope(envelope: Any) -> Dict[str, Any]:
    allowed = ["schema_id", "task_id", "candidate_id", "sample_rate_hz", "channels", "frame_samples", "source_end", "synthetic", "segments"]
    _check_keys(envelope, allowed, allowed, "envelope")
    if envelope["schema_id"] != SCHEMA_ENVELOPE:
        raise ReferenceRejection("SCHEMA_ID_MISMATCH")
    if envelope["task_id"] != TASK or envelope["candidate_id"] != COMPONENT:
        raise ReferenceRejection("CANDIDATE_CLAIM")
    for field, expected in [("sample_rate_hz", 16000), ("channels", 1), ("frame_samples", 160), ("source_end", FIXTURE_SAMPLES)]:
        v = envelope[field]
        if isinstance(v, bool) or not isinstance(v, int):
            raise ReferenceRejection("GEOMETRY_TYPE_INVALID", field)
        if v != expected:
            raise ReferenceRejection("GEOMETRY_MISMATCH", field)
    if envelope["synthetic"] is not True:
        raise ReferenceRejection("SYNTHETIC_FLAG_INVALID")
    segs = envelope["segments"]
    if not isinstance(segs, list) or not segs:
        raise ReferenceRejection("SEGMENTS_INVALID")
    seg_allowed = ["id", "class", "source_start", "source_end", "rate", "retained"]
    prev_end = 0
    seen_ids = set()
    out_end = 0
    output_segments = []
    for seg in segs:
        _check_keys(seg, seg_allowed, seg_allowed, "segment")
        sid = seg["id"]
        if not isinstance(sid, str) or not sid:
            raise ReferenceRejection("SEGMENT_ID_INVALID")
        if sid in seen_ids:
            raise ReferenceRejection("SEGMENT_ID_DUPLICATE")
        seen_ids.add(sid)
        cls = seg["class"]
        if cls not in {"speech", "silence", "unknown"}:
            raise ReferenceRejection("CONTENT_CLASS_INVALID")
        ss, se = seg["source_start"], seg["source_end"]
        for name, val in [("source_start", ss), ("source_end", se)]:
            if isinstance(val, bool) or not isinstance(val, int):
                raise ReferenceRejection("GEOMETRY_TYPE_INVALID", name)
        if ss != prev_end:
            raise ReferenceRejection("INTERVAL_GAP_OR_OVERLAP")
        if se <= ss:
            raise ReferenceRejection("INTERVAL_RANGE_INVALID")
        if se - ss < MIN_DWELL:
            raise ReferenceRejection("MIN_DWELL_VIOLATION")
        rate = _parse_rate(seg["rate"], sid)
        if rate < RATE_MIN or rate > RATE_MAX:
            raise ReferenceRejection("RATE_OUT_OF_RANGE")
        if cls == "speech" and rate > 1.0:
            raise ReferenceRejection("SPEECH_SPEEDUP_FORBIDDEN")
        if cls == "silence" and rate < 1.0:
            raise ReferenceRejection("SILENCE_SLOWDOWN_FORBIDDEN")
        if cls == "unknown" and abs(rate - 1.0) > 1e-12:
            raise ReferenceRejection("UNKNOWN_RATE_VIOLATION")
        out_samples = (se - ss) / rate
        if abs(out_samples - round(out_samples)) > 1e-9:
            raise ReferenceRejection("NONINTEGER_OUTPUT_BOUNDARY")
        out_samples_i = int(round(out_samples))
        if seg["retained"] is not True:
            raise ReferenceRejection("SILENCE_DELETION_FORBIDDEN")
        output_segments.append({"id": sid, "output_start": out_end, "output_end": out_end + out_samples_i, "output_samples": out_samples_i})
        out_end += out_samples_i
        prev_end = se
    if prev_end != FIXTURE_SAMPLES:
        raise ReferenceRejection("UNCOVERED_TAIL")
    if out_end != FIXTURE_SAMPLES:
        raise ReferenceRejection("DURATION_NOT_CLOSED")
    return {"source_end": prev_end, "output_end": out_end, "segments": output_segments, "qualifies": False}


def valid_manifest() -> Dict[str, Any]:
    assets = []
    for a in REQUIRED_ASSETS:
        data = f"placeholder:{a['asset_id']}".encode("utf-8")
        assets.append({
            "asset_id": a["asset_id"],
            "path": f"/caller-owned/{COMPONENT}/{a['asset_id'].split('.')[-1]}.bin",
            "sha256": sha256_bytes(data),
            "byte_count": len(data),
            "storage": "external",
            "license_id": "reviewed-license",
            "rights_attestation": "caller-attested-shape-only",
        })
    return {
        "schema_id": SCHEMA_MANIFEST,
        "task_id": TASK,
        "candidate_id": COMPONENT,
        "candidate_family": "speechbrain-disfluency-pause-predictor",
        "fixture_id": "shape-only-fixture",
        "source_revision": "0" * 40,
        "source_license_id": "reviewed-source-license",
        "runtime_lock_id": "reviewed-runtime-lock",
        "label_schema_id": "reviewed-label-schema",
        "cohort_manifest_id": "reviewed-cohort-manifest",
        "reference_output_id": "reviewed-reference-output",
        "attestation": "caller-attested-not-validated",
        "rate_policy_id": "reviewed-rate-policy",
        "evidence_class": "caller_supplied_shape_only",
        "credential_review_id": "credential-review-placeholder",
        "counsel_review_id": "counsel-review-placeholder",
        "assets": assets,
    }


def envelope_adverse_cases() -> Dict[str, Any]:
    cases = []

    def add(name: str, mutate, expected: str) -> None:
        env = valid_envelope()
        mutate(env)
        try:
            validate_envelope(env)
            cases.append({"id": name, "rejected": False, "actual_code": "ACCEPTED", "expected_code": expected})
        except ReferenceRejection as e:
            cases.append({"id": name, "rejected": True, "actual_code": e.code, "expected_code": expected})

    add("boolean_source_end", lambda e: e.__setitem__("source_end", True), "GEOMETRY_TYPE_INVALID")
    add("wrong_sample_rate", lambda e: e.__setitem__("sample_rate_hz", 8000), "GEOMETRY_MISMATCH")
    add("wrong_channels", lambda e: e.__setitem__("channels", 2), "GEOMETRY_MISMATCH")
    add("wrong_frame_samples", lambda e: e.__setitem__("frame_samples", 320), "GEOMETRY_MISMATCH")
    add("wrong_task", lambda e: e.__setitem__("task_id", "OTHER"), "CANDIDATE_CLAIM")
    add("not_synthetic", lambda e: e.__setitem__("synthetic", False), "SYNTHETIC_FLAG_INVALID")
    add("extra_field", lambda e: e.__setitem__("extra", 1), "SCHEMA_FIELD_SET")
    def missing(e):
        del e["segments"]
    add("missing_field", missing, "SCHEMA_FIELD_SET")
    add("empty_segments", lambda e: e.__setitem__("segments", []), "SEGMENTS_INVALID")
    def gap(e):
        e["segments"][1]["source_start"] = 3360
    add("gap", gap, "INTERVAL_GAP_OR_OVERLAP")
    def overlap(e):
        e["segments"][1]["source_start"] = 3040
    add("overlap", overlap, "INTERVAL_GAP_OR_OVERLAP")
    def uncovered(e):
        e["segments"][-1]["source_end"] = 15840
    add("uncovered_tail", uncovered, "UNCOVERED_TAIL")
    def zero_len(e):
        e["segments"][0]["source_end"] = 0
    add("zero_length", zero_len, "INTERVAL_RANGE_INVALID")
    def dup_id(e):
        e["segments"][1]["id"] = e["segments"][0]["id"]
    add("duplicate_id", dup_id, "SEGMENT_ID_DUPLICATE")
    def bad_class(e):
        e["segments"][0]["class"] = "music"
    add("unsupported_class", bad_class, "CONTENT_CLASS_INVALID")
    def speech_speed(e):
        e["segments"][1]["rate"] = "5/4"
    add("speech_speedup", speech_speed, "SPEECH_SPEEDUP_FORBIDDEN")
    def silence_slow(e):
        e["segments"][2]["rate"] = "3/4"
    add("silence_slowdown", silence_slow, "SILENCE_SLOWDOWN_FORBIDDEN")
    def unknown_bad(e):
        e["segments"][0]["rate"] = "4/5"
    add("unknown_as_silence", unknown_bad, "UNKNOWN_RATE_VIOLATION")
    def rate_low(e):
        e["segments"][2]["rate"] = "1/2"
    add("rate_below_floor", rate_low, "RATE_OUT_OF_RANGE")
    def rate_high(e):
        e["segments"][1]["rate"] = "2/1"
    add("rate_above_ceiling", rate_high, "RATE_OUT_OF_RANGE")
    def zero_den(e):
        e["segments"][0]["rate"] = "1/0"
    add("zero_denominator", zero_den, "RATE_INVALID")
    def noninteger(e):
        e["segments"][1]["source_end"] = 8001
        e["segments"][2]["source_start"] = 8001
    add("noninteger_output", noninteger, "NONINTEGER_OUTPUT_BOUNDARY")
    def not_closed(e):
        e["segments"][-1]["rate"] = "4/5"
    add("duration_not_closed", not_closed, "DURATION_NOT_CLOSED")
    def short_dwell(e):
        e["segments"][0]["source_end"] = 160
        e["segments"][1]["source_start"] = 160
    add("short_dwell", short_dwell, "MIN_DWELL_VIOLATION")
    def deletion(e):
        e["segments"][2]["retained"] = False
    add("silence_deleted", deletion, "SILENCE_DELETION_FORBIDDEN")

    accepted = sum(1 for c in cases if not c["rejected"])
    return {"accepted_count": accepted, "all_rejected": accepted == 0, "case_count": len(cases), "cases": cases}


def manifest_adverse_cases() -> Dict[str, Any]:
    cases = []

    def add(name: str, mutate, expected: str) -> None:
        m = valid_manifest()
        mutate(m)
        try:
            validate_manifest(m)
            cases.append({"id": name, "rejected": False, "actual_code": "ACCEPTED", "expected_code": expected})
        except ReferenceRejection as e:
            cases.append({"id": name, "rejected": True, "actual_code": e.code, "expected_code": expected})

    add("manifest_not_object", lambda m: m.clear() or m.__setitem__("bad", 1), "SCHEMA_FIELD_SET")  # trick: we'll handle separately
    # manifest_not_object handled directly below
    cases.pop()
    try:
        validate_manifest([])
        cases.append({"id": "manifest_not_object", "rejected": False, "actual_code": "ACCEPTED", "expected_code": "TYPE_INVALID"})
    except ReferenceRejection as e:
        cases.append({"id": "manifest_not_object", "rejected": True, "actual_code": e.code, "expected_code": "TYPE_INVALID"})

    add("missing_field", lambda m: m.pop("task_id"), "SCHEMA_FIELD_SET")
    add("extra_field", lambda m: m.__setitem__("extra", "x"), "SCHEMA_FIELD_SET")
    add("wrong_task", lambda m: m.__setitem__("task_id", "OTHER"), "TASK_ID_MISMATCH")
    add("wrong_candidate", lambda m: m.__setitem__("candidate_id", "other"), "CANDIDATE_ID_MISMATCH")
    add("short_revision", lambda m: m.__setitem__("source_revision", "abc"), "SOURCE_REVISION_INVALID")
    add("bad_attestation", lambda m: m.__setitem__("attestation", ""), "TEXT_FIELD_INVALID")
    add("bad_rate_policy", lambda m: m.__setitem__("rate_policy_id", ""), "TEXT_FIELD_INVALID")
    add("wrong_evidence_class", lambda m: m.__setitem__("evidence_class", "release"), "EVIDENCE_CLASS_INVALID")
    add("colliding_review_ids", lambda m: m.__setitem__("counsel_review_id", m["credential_review_id"]), "EVIDENCE_CLASS_COLLISION")
    add("missing_asset", lambda m: m["assets"].pop(), "ASSET_SET_MISMATCH")
    def extra_asset(m):
        a = dict(m["assets"][0]); a["asset_id"] = "speechbrain-disfluency-pause-predictor.extra"; a["path"] = "/caller-owned/extra.bin"; m["assets"].append(a)
    add("extra_asset", extra_asset, "ASSET_SET_MISMATCH")
    add("relative_path", lambda m: m["assets"][0].__setitem__("path", "relative.bin"), "ASSET_PATH_NOT_ABSOLUTE")
    add("traversal_path", lambda m: m["assets"][0].__setitem__("path", "/caller-owned/../escape.bin"), "ASSET_PATH_TRAVERSAL")
    def dup_path(m):
        m["assets"][1]["path"] = m["assets"][0]["path"]
    add("duplicate_path", dup_path, "ASSET_PATH_DUPLICATE")
    add("uppercase_hash", lambda m: m["assets"][0].__setitem__("sha256", "A" * 64), "ASSET_SHA256_INVALID")
    add("short_hash", lambda m: m["assets"][0].__setitem__("sha256", "abc"), "ASSET_SHA256_INVALID")
    add("zero_byte_count", lambda m: m["assets"][0].__setitem__("byte_count", 0), "ASSET_BYTE_COUNT_INVALID")
    add("oversize_byte_count", lambda m: m["assets"][0].__setitem__("byte_count", 1_000_000_001), "ASSET_BYTE_COUNT_INVALID")
    add("embedded_storage", lambda m: m["assets"][0].__setitem__("storage", "embedded"), "ASSET_STORAGE_INVALID")
    add("extra_asset_field", lambda m: m["assets"][0].__setitem__("extra", 1), "SCHEMA_FIELD_SET")

    accepted = sum(1 for c in cases if not c["rejected"])
    return {"accepted_count": accepted, "all_rejected": accepted == 0, "case_count": len(cases), "cases": cases}


def invalid_json_cases() -> Dict[str, Any]:
    texts = ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', '']
    cases = []
    for i, text in enumerate(texts):
        try:
            strict_loads(text)
            cases.append({"id": f"json-{i}", "rejected": False})
        except (ReferenceError, ValueError):
            cases.append({"id": f"json-{i}", "rejected": True})
    accepted = sum(1 for c in cases if not c["rejected"])
    return {"accepted_count": accepted, "all_rejected": accepted == 0, "case_count": len(cases), "cases": cases}


def invalid_pin_cases() -> Dict[str, Any]:
    good = "a" * 64
    lines = [good + "  source:dup\n" + good + "  source:dup\n", "abc  source:short\n", good + "  /abs\n", good + "  source:../escape\n"]
    cases = []
    for i, line in enumerate(lines):
        try:
            parse_pin_lines(line)
            cases.append({"id": f"pin-{i}", "rejected": False})
        except ReferenceError:
            cases.append({"id": f"pin-{i}", "rejected": True})
    accepted = sum(1 for c in cases if not c["rejected"])
    return {"accepted_count": accepted, "all_rejected": accepted == 0, "case_count": len(cases), "cases": cases}


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        m = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw)
        if not m:
            raise ReferenceError("pin_line_invalid")
        digest, key = m.group(1), m.group(2)
        parts = key.replace("\\", "/").split("/")
        if key.startswith("/") or any(part in {"..", ""} for part in parts) or ".." in key:
            raise ReferenceError("pin_key_unsafe")
        rows.append((digest, key))
    if len(rows) != len({k for _, k in rows}):
        raise ReferenceError("duplicate_pin_key")
    return rows


def asset_pins_absent() -> bool:
    probe = absent_artifact_probe()
    return not probe["present"]


def source_line_entries() -> List[Dict[str, Any]]:
    out = []
    for entry in SOURCE_LINES:
        target = AUDIO_ROOT / entry["path"]
        if not target.is_file():
            raise ReferenceError(f"source_line_missing:{entry['path']}")
        lines = target.read_text(encoding="utf-8").splitlines()
        idx = entry["line"] - 1
        if idx < 0 or idx >= len(lines):
            raise ReferenceError(f"source_line_out_of_range:{entry['path']}:{entry['line']}")
        actual = lines[idx]
        if actual != entry["text"]:
            raise ReferenceError(f"source_line_stale:{entry['id']}")
        row = dict(entry)
        row["sha256"] = sha256_file(target)
        out.append(row)
    return out


def source_reported_entries() -> Dict[str, Any]:
    return {
        "qualifies": False,
        "separation": "Source-reported provenance only. None is reproduced, executed, pooled with synthetic controls or promoted to a candidate result.",
        "entries": [
            {
                "id": "SR-01",
                "claim": "Official SpeechBrain model inventory checked; no matching pretrained rate/disfluency head found.",
                "source": "research/tsm-followup-20261101/README.md:33",
            },
            {
                "id": "SR-02",
                "claim": "SpeechBrain is a toolkit with ASR/VAD recipes, not an off-the-shelf preferred-speed predictor for this task.",
                "source": "research/tsm-followup-20261101/README.md:33",
            },
            {
                "id": "SR-03",
                "claim": "Inventory marks speechbrain-disfluency-pause-predictor as blocked/sdk-model with Rate verification profile.",
                "source": "audio-benchmark-platform/plan/INVENTORY.json:8274-8293",
            },
        ],
    }


def build_report() -> Dict[str, Any]:
    validate_source_pins()
    validate_boundary_pins()
    envelope = validate_envelope(valid_envelope())
    adverse = {
        "all_rejected": True,
        "invalid_json": invalid_json_cases(),
        "invalid_pins": invalid_pin_cases(),
        "typed_envelope": envelope_adverse_cases(),
        "caller_manifest": manifest_adverse_cases(),
    }
    for v in adverse.values():
        if isinstance(v, dict) and "all_rejected" in v and not v["all_rejected"]:
            adverse["all_rejected"] = False
    probe = absent_artifact_probe()
    report = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "format": dict(BOUNDARY["format"]),
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "required_assets": [
            {"asset_id": a["asset_id"], "role": a["role"], "storage": a["storage"], "declared_sha256": None, "declared_byte_count": None, "present_locally": False}
            for a in REQUIRED_ASSETS
        ],
        "asset_resolution": probe,
        "exact_blockers": list(BLOCKERS),
        "reopening_conditions": [b["reopen"] for b in BLOCKERS],
        "gates": list(GATES),
        "source_pins": {f"source:{k}": v for k, v in SOURCE_PINS.items()},
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_lines": {"line_count": len(source_line_entries()), "entries": source_line_entries()},
        "source_reported": source_reported_entries(),
        "board_link": board_link(),
        "synthetic_envelope": {
            "schema_id": SCHEMA_ENVELOPE,
            "min_dwell_samples": MIN_DWELL,
            "rate_min": "3/4",
            "rate_max": "3/2",
            "source_end": envelope["source_end"],
            "output_end": envelope["output_end"],
            "segments": envelope["segments"],
            "qualifies": False,
        },
        "adverse": adverse,
        "repeatability": {
            "fresh_builds": 3,
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
        "no_missing_result_qualifies_candidate": True,
        "evidence_classes": {
            "real_local_model_output": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
            "release_claim": False,
            "source_reported": True,
            "synthetic": True,
            "caller_supplied_shape_only": True,
        },
    }
    # fail closed on any qualifying leakage
    for gate in report["gates"]:
        if gate["status"] != "blocked" or gate["qualifies"] is not False:
            raise ReferenceError("gate_not_blocked")
    if report["decision"] != "DEFER" or report["qualification_status"] != "not_qualified":
        raise ReferenceError("status_not_defer")
    if not report["adverse"]["all_rejected"]:
        raise ReferenceError("adverse_not_rejected")
    return report


def report_bytes() -> bytes:
    return canonical_json_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes, contract_payload: bytes | None = None) -> bytes:
    report = strict_loads(report_payload.decode("utf-8"))
    if contract_payload is None:
        contract_payload = contract_bytes(report_payload, sidecar_payload, b"", report)
    generated = {
        "report.json": report_payload,
        "report.json.sha256": sidecar_payload,
        "contract.json": contract_payload,
    }
    rows: List[Tuple[str, str]] = []
    for key, digest in report["source_pins"].items():
        rows.append((digest, key))
    for key, digest in report["boundary_pins"].items():
        rows.append((digest, f"sdk:{key}"))
    for name in LOCAL_PIN_PATHS:
        payload = generated.get(name)
        rows.append((sha256_bytes(payload) if payload is not None else sha256_file(HERE / name), name))
    rows.append((sha256_bytes(report_payload), "report.json"))
    rows.append((sha256_bytes(sidecar_payload), "report.json.sha256"))
    rows.append((sha256_bytes(contract_payload), "contract.json"))
    rows = sorted(set(rows), key=lambda r: (r[1], r[0]))
    return "".join(f"{d}  {k}\n" for d, k in rows).encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any] | None = None) -> bytes:
    report = report or strict_loads(report_payload.decode("utf-8"))
    contract = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
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
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "asset_root": "/caller-owned/speechbrain-disfluency-pause-predictor",
            "executed": False,
            "loaded": False,
            "note": "Metadata and byte-hash intake only; hash-matched assets still fail release gates.",
            "required_assets": report["required_assets"],
            "required_asset_fields": ["asset_id", "path", "sha256", "byte_count", "storage", "license_id", "rights_attestation"],
            "required_fields": [
                "schema_id", "task_id", "candidate_id", "candidate_family", "fixture_id", "source_revision", "source_license_id", "runtime_lock_id", "label_schema_id", "cohort_manifest_id", "reference_output_id", "attestation", "rate_policy_id", "evidence_class", "credential_review_id", "counsel_review_id", "assets",
            ],
        },
        "source_pins": report["source_pins"],
        "boundary_pins": report["boundary_pins"],
        "artifact_pins": {},
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload) if sources_payload else None,
        "task_prefix": TASK_PREFIX,
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Only the task-local evidence directory is written.",
            "No source, model, audio or runtime artifact is bundled, downloaded or executed.",
            "Caller manifests are validated as metadata and byte hashes only.",
            "All provider, default, ABI, registry, shared-build and CI flags remain false.",
            "Only stable board-row identity enters canonical bytes or gates.",
        ],
    }
    return canonical_json_bytes(contract)


def readme_pin_rows() -> List[Tuple[str, str]]:
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    rows = []
    in_table = False
    for line in readme.splitlines():
        if line.startswith("<!-- digest-table:"):
            in_table = True
            continue
        if line.startswith("<!-- digest-table: end -->"):
            in_table = False
            continue
        if not in_table or not line.startswith("| `"):
            continue
        m = re.fullmatch(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", line)
        if m:
            rows.append((m.group(1), m.group(2)))
    return rows


def scope_base(repo: Path, refs: Sequence[str] = ("origin/main", "main")) -> str | None:
    candidates = []
    for ref in refs:
        result = subprocess.run(["git", "-C", str(repo), "merge-base", "HEAD", ref], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            continue
        sha = result.stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            continue
        ts = subprocess.run(["git", "-C", str(repo), "show", "-s", "--format=%ct", sha], capture_output=True, text=True, check=False)
        if ts.returncode != 0:
            continue
        candidates.append((int(ts.stdout.strip() or "0"), sha))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


def scope_changed_paths(repo: Path, base: str) -> List[str]:
    result = subprocess.run(["git", "-C", str(repo), "diff", "--name-only", base + "..HEAD"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ReferenceError("scope_diff_failed")
    return [line for line in result.stdout.splitlines() if line.strip()]


def scope_violations(changed: Sequence[str]) -> List[str]:
    return [p for p in changed if not p.startswith(TASK_PREFIX)]
