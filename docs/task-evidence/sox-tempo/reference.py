# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-SOX-TEMPO.

This module is NOT SoX tempo. It does not implement, approximate, simulate,
download, build, import, link, or execute SoX, libsox, SoX tempo/WSOLA code,
or any GPL/LGPL upstream binary. No upstream SoX source revision, runtime,
binary, model, weight, or real corpus audio is present in this package.

The catalogued evidence records SoX tempo as an LGPL-2.1 effect-file reference
with libsox/GPL distribution considerations and a real-time-callback warning.
No exact pinned source revision/archive, reviewed license/notice bundle,
deterministic offline runtime, or matched Rate-profile evidence is staged here.

The module builds a bounded, deterministic DEFER blocker report:
- exact linked inventory/TASKS/VERIFICATION/source-note identity projection;
- bounded absence probes for SoX source/runtime artifacts (no download);
- strict request validation rejecting missing/unknown/invalid/nonfinite/
  out-of-range/stale inputs before any candidate call;
- structural reset validation that never owns candidate state;
- synthetic harness stimuli for identity/rejection controls only;
- stable linked-row identity only; mutable full TASKS.json is never hashed.

No network, model weights, real corpus audio, native library, or download is
used. No candidate output is produced and no result qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0

SCHEMA_ID = "audio-sdk/sox-tempo-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/sox-tempo-contract/0.1"
TASK = "SDK-SOX-TEMPO"
COMPONENT = "sox-tempo"
TITLE = "SoX tempo"
MODE = "feasibility"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-SOX-TEMPO"
BASE_COMMIT = "b369ee5b64de0493b96b3f99ede9a2560b130bb2"
TASK_PREFIX = "docs/task-evidence/sox-tempo/"

EVIDENCE_PATH = "cpp-library/pipeline-validation/playback-speed-candidates.md"
EVIDENCE_LINE = 250
EVIDENCE_TEXT = "### 3.11 SoX `tempo` (WSOLA reference)"
EVIDENCE_DETAIL_LINES = {
    252: "- **Links:** <https://sox.sourceforge.net/sox.html> · source <https://github.com/chirlu/sox/blob/master/src/tempo.c>",
    253: "- **What it is:** SoX `tempo`/`pitch` effects. The source says it is based on ideas from Olli Parviainen's SoundTouch and implements waveform-similarity overlap-add with a quick hierarchical search or a linear search.",
    254: "- **Licence:** the effect file is LGPL-2.1; the `sox` binary is GPL-2.0. Use `libsox` under LGPL, or reimplement the algorithm.",
    255: "- **Parameters:** factor > 0 (the file documents no hard cap); `-q` quick search; `-m` music, `-s` speech, `-l` linear profiles; segment/search/overlap in ms. The speech profile starts at a 35 ms segment and scales it with the factor (for example 32 ms at 1.25×), with proportional overlap/search.",
    256: "- **Use:** second reference for WSOLA; the profile table is useful for choosing segment sizes.",
    257: "- **Verdict:** good reference; avoid linking `libsox` into a real-time callback.",
}

import os

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_SOX_TEMPO_SDK_ROOT", str(HERE.parents[2]))).resolve()
_default_workspace = HERE.parents[5] if len(HERE.parents) > 5 else SDK_ROOT.parents[2]
WORKSPACE = Path(os.environ.get("SDK_SOX_TEMPO_WORKSPACE", str(_default_workspace))).resolve()
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

EXPECTED_LINK = {
    "id": TASK,
    "title": TITLE,
    "mode": MODE,
    "repository": REPOSITORY,
    "component": COMPONENT,
}
LINK_FIELDS = ("id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff",
    "blocked_reason", "dispatch_priority",
)

EXPECTED_INVENTORY = {
    "id": "sox-tempo",
    "name": "SoX tempo",
    "area": "Rate and content",
    "evidence_status": "considered",
    "repository": "audio-sdk",
    "disposition": "sdk-reference",
    "verification_profile": "rate",
    "task": TASK,
}

REQUIRED_ARTIFACTS = (
    {
        "id": "sox-tempo-source-revision",
        "role": "Exact SoX source revision/archive containing src/tempo.c and required build/license files",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Exact immutable revision/tag/archive with complete license text, "
            "copyright notices, and reviewed LGPL-2.1/GPL-2.0 obligations for "
            "the selected distribution/build path before any vendoring or "
            "release claim."
        ),
    },
    {
        "id": "sox-tempo-runtime-or-binary",
        "role": "Pinned runnable offline SoX tempo runtime/binary or reviewed build recipe",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Exact executable identity, build inputs, hash-pinned environment, "
            "offline deterministic command line, and rights/redistribution "
            "review for binaries and dependencies."
        ),
    },
    {
        "id": "sox-tempo-license-notice-bundle",
        "role": "Reviewed license/copyright/notice bundle covering tempo effect, libsox, and binary distribution choices",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Complete LGPL-2.1/GPL-2.0 texts as applicable, copyright holders, "
            "source-offer/relink obligations where relevant, and a written "
            "decision that no GPL/copyleft obligation is violated by the chosen "
            "evidence or any future integration path."
        ),
    },
    {
        "id": "matched-rate-profile-evidence",
        "role": "Matched frozen Rate-profile evidence with controls and target geometry mapping",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Rights-cleared synthetic or separately approved corpus/protocol; "
            "no real audio, listening, or device claims without explicit rights "
            "and review."
        ),
    },
)

RUNTIME_MODULES = ("numpy", "scipy", "librosa", "soundfile", "sox")
SOURCE_CANDIDATE_PATHS = (
    "third_party/sox",
    "third_party/libsox",
    "data/checkouts/sox",
    "data/checkouts/libsox",
    "research/sox-tempo",
    "cpp-library/pipeline-validation/sox-tempo",
)
ARTIFACT_SUFFIXES = (
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".aac",
    ".onnx", ".pt", ".pth", ".ckpt", ".safetensors", ".bin",
    ".so", ".dylib", ".dll", ".a", ".o", ".zip", ".tar", ".gz", ".whl",
)

GATES = [
    {
        "id": "RG-01",
        "gate": "exact_source_revision_archive_and_license",
        "status": "blocked",
        "reason": (
            "No exact SoX source revision/archive is staged. The catalogued "
            "note identifies the tempo effect as LGPL-2.1 and the sox binary "
            "as GPL-2.0, but no reviewed immutable source bundle, complete "
            "license/copyright/notice set, or redistribution decision is "
            "present in this worktree."
        ),
        "reopen": (
            "Provide an exact immutable SoX source revision/archive with "
            "SHA-256, complete applicable license/copyright/notice files, and "
            "a reviewed build/distribution decision before any reproduction "
            "claim."
        ),
    },
    {
        "id": "RG-02",
        "gate": "pinned_runtime_offline_execution",
        "status": "blocked",
        "reason": (
            "No pinned runnable SoX tempo runtime/binary or deterministic "
            "offline execution recipe is present. No execution was attempted."
        ),
        "reopen": (
            "Provide a hash-pinned offline runtime or reviewed binary/build "
            "with exact command line, environment lock, and deterministic "
            "outputs; keep execution out of the realtime callback path."
        ),
    },
    {
        "id": "RG-03",
        "gate": "rights_and_redistribution_review",
        "status": "blocked",
        "reason": (
            "LGPL/GPL scope is identified but not reviewed for this task. No "
            "rights decision covers source, binaries, dependencies, outputs, "
            "or any future SDK integration/distribution path."
        ),
        "reopen": (
            "Complete rights review for selected source/runtime path, "
            "including LGPL-2.1/GPL-2.0 obligations, source-offer/relink "
            "requirements where applicable, and output/corpus rights."
        ),
    },
    {
        "id": "RG-04",
        "gate": "installed_geometry_and_adapter_mapping",
        "status": "blocked",
        "reason": (
            "Installed v0 requires 16 kHz mono float32 160-sample frames. No "
            "SoX tempo caller-supplied-asset/reference adapter mapping has "
            "been proven for this geometry, including buffering, delay, "
            "flush/drain, and source/output timestamp mapping."
        ),
        "reopen": (
            "Demonstrate a deterministic adapter mapping on the installed "
            "geometry with exact buffering/delay/drain semantics and fail-"
            "closed invalid-input behavior; keep it opt-in and unregistered."
        ),
    },
    {
        "id": "RG-05",
        "gate": "rate_profile_qualification",
        "status": "blocked",
        "reason": (
            "No SoX tempo output exists. Rate profile mapping, duration, "
            "pitch preservation, transient audibility, playback buffering, "
            "1x/rate changes, unfamiliar speech/music, silence, rebuffer, "
            "drift, and final partial window are unmeasured."
        ),
        "reopen": (
            "Run the exact pinned reference on a frozen synthetic and rights-"
            "cleared cohort with the Rate acceptance profile and matched "
            "controls."
        ),
    },
    {
        "id": "RG-06",
        "gate": "real_corpus_and_listening",
        "status": "blocked",
        "reason": (
            "No real speech/music corpus, consent, or listening judgment "
            "exists. Synthetic controls are non-qualifying."
        ),
        "reopen": (
            "Provide rights-cleared real-corpus/listening evidence under an "
            "independent protocol; keep synthetic probes non-qualifying."
        ),
    },
    {
        "id": "RG-07",
        "gate": "target_runtime_timing_and_resources",
        "status": "blocked",
        "reason": (
            "No target-device pacing, callback suitability, CPU, memory, "
            "buffering, fill/flush, or end-to-end timing was measured. The "
            "catalogued note warns against linking libsox into a real-time "
            "callback."
        ),
        "reopen": (
            "Measure paced target runtime behavior separately if real-time "
            "exposure is ever proposed; offline evidence cannot close this "
            "gate."
        ),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_and_public_surface",
        "status": "blocked",
        "reason": (
            "No provider intake, descriptor registration, public surface, "
            "registry/default, or installed-v0 behavior decision exists. This "
            "package is task-local evidence only."
        ),
        "reopen": (
            "After prior gates clear, complete opt-in provider intake with "
            "OFF default, no ABI/registry/default/shared-build change without "
            "separate approval, and independent review."
        ),
    },
]

GATE_IDS = [gate["id"] for gate in GATES]


class ValidationError(ValueError):
    """Strict input validation error with stable field name."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8") + "\n"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _reject_nonfinite(value: Any, field: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValidationError(f"{field}:nonfinite")


def strict_load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")

    def parse_constant(token: str) -> Any:
        raise ValidationError(f"{path.name}:nonfinite:{token}")

    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValidationError(f"{path.name}:duplicate_key:{key}")
            _reject_nonfinite(value, f"{path.name}.{key}")
            obj[key] = value
        return obj

    value = json.loads(text, parse_constant=parse_constant,
                       object_pairs_hook=object_pairs_hook)
    _walk_finite(value, path.name)
    return value


def _walk_finite(value: Any, field: str) -> None:
    if isinstance(value, float):
        _reject_nonfinite(value, field)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _walk_finite(item, f"{field}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _walk_finite(item, f"{field}.{key}")


def workspace_rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE.resolve()).as_posix()


def sdk_rel(path: Path) -> str:
    return path.resolve().relative_to(SDK_ROOT.resolve()).as_posix()


def _pin_digest(root: Path, rel: str, expected: str, label: str) -> Dict[str, Any]:
    path = (root / rel).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"missing {label} pin: {rel}")
    digest = sha256_file(path)
    if digest != expected:
        raise ValueError(f"{label} pin digest mismatch: {rel}")
    return {"path": rel, "sha256": digest, "bytes": path.stat().st_size}


def source_pins() -> List[Dict[str, Any]]:
    rows = [_pin_digest(WORKSPACE, rel, digest, "source")
            for rel, digest in sorted(SOURCE_PINS.items())]
    return rows


def boundary_pins() -> List[Dict[str, Any]]:
    rows = [_pin_digest(SDK_ROOT, rel, digest, "boundary")
            for rel, digest in sorted(BOUNDARY_PINS.items())]
    return rows


def evidence_pin() -> Dict[str, Any]:
    path = WORKSPACE / EVIDENCE_PATH
    digest = sha256_file(path)
    expected = SOURCE_PINS[EVIDENCE_PATH]
    if digest != expected:
        raise ValueError("evidence pin digest mismatch")
    lines = path.read_text(encoding="utf-8").splitlines()
    line_text = lines[EVIDENCE_LINE - 1]
    if line_text != EVIDENCE_TEXT:
        raise ValueError("evidence line mismatch")
    detail = {}
    for n, expected_text in EVIDENCE_DETAIL_LINES.items():
        got = lines[n - 1]
        if got != expected_text:
            raise ValueError(f"evidence detail line mismatch: {n}")
        detail[str(n)] = got
    return {
        "path": EVIDENCE_PATH,
        "sha256": digest,
        "line": EVIDENCE_LINE,
        "text": line_text,
        "detail_lines": detail,
    }


def board_row() -> Dict[str, Any]:
    data = strict_load(BOARD_PATH)
    if isinstance(data, dict) and isinstance(data.get("tasks"), list):
        tasks = data["tasks"]
    elif isinstance(data, list):
        tasks = data
    else:
        raise ValueError("TASKS.json must be a list or {tasks:[...]}")
    for row in tasks:
        if isinstance(row, dict) and row.get("id") == TASK:
            projected = {field: row.get(field) for field in LINK_FIELDS}
            if projected != EXPECTED_LINK:
                raise ValueError("linked TASKS row projection mismatch")
            unknown = [k for k in LINK_FIELDS if k not in row]
            if unknown:
                raise ValueError(f"linked TASKS row missing fields: {unknown}")
            return {
                "path": workspace_rel(BOARD_PATH),
                "projection": projected,
                "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
                "mutable_fields_present": [k for k in MUTABLE_FIELDS_EXCLUDED if k in row],
            }
    raise ValueError("TASKS row not found")


def inventory_row() -> Dict[str, Any]:
    data = strict_load(INVENTORY_PATH)
    if isinstance(data, dict):
        rows = data.get("components") or data.get("items") or data.get("inventory")
        if isinstance(rows, list):
            data_rows = rows
        else:
            # maybe mapping by id
            data_rows = []
            for v in data.values():
                if isinstance(v, list):
                    data_rows = v
                    break
    elif isinstance(data, list):
        data_rows = data
    else:
        raise ValueError("INVENTORY.json has unsupported shape")
    for row in data_rows:
        if isinstance(row, dict) and row.get("id") == COMPONENT:
            projected = {k: row.get(k) for k in EXPECTED_INVENTORY}
            if projected != EXPECTED_INVENTORY:
                raise ValueError(f"inventory row projection mismatch: {projected}")
            return {
                "path": workspace_rel(INVENTORY_PATH),
                "projection": projected,
            }
    raise ValueError("inventory row not found")


def probe_runtime_modules() -> Dict[str, Any]:
    found = []
    for name in RUNTIME_MODULES:
        spec = importlib.util.find_spec(name)
        if spec is not None:
            found.append(name)
    return {
        "modules_checked": list(RUNTIME_MODULES),
        "modules_found": found,
        "pinned": False,
        "present": False,
        "status": "absent_unpinned",
    }


def probe_source_paths() -> Dict[str, Any]:
    hits = []
    for rel in SOURCE_CANDIDATE_PATHS:
        path = WORKSPACE / rel
        if path.exists():
            hits.append(rel)
    return {
        "paths_checked": list(SOURCE_CANDIDATE_PATHS),
        "paths_present": hits,
        "present": False if not hits else True,
        "status": "absent_unreviewed" if not hits else "unexpected_present_requires_review",
    }


def probe_artifacts() -> Dict[str, Any]:
    roots = [WORKSPACE / "third_party", WORKSPACE / "data", WORKSPACE / "research"]
    hits = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            name = path.name.lower()
            if "sox" in name and "tempo" in name and path.suffix.lower() in ARTIFACT_SUFFIXES:
                hits.append(workspace_rel(path))
    hits = sorted(set(hits))
    return {
        "roots_checked": [workspace_rel(r) for r in roots if r.exists()],
        "suffixes_checked": list(ARTIFACT_SUFFIXES),
        "matches": hits,
        "present": bool(hits),
        "status": "absent" if not hits else "unexpected_present_requires_review",
    }


def validate_request(request: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, Mapping):
        raise ValidationError("request:not_object")
    allowed = {
        "schema_id", "task", "component", "sample_rate_hz", "channels",
        "frame_samples", "sample_format", "tempo_factor", "profile",
        "input", "reset", "epoch",
    }
    unknown = sorted(set(request.keys()) - allowed)
    if unknown:
        raise ValidationError("request:unknown_field:" + ",".join(unknown))
    for field in ("schema_id", "task", "component"):
        value = request.get(field)
        if value != {"schema_id": "audio-sdk/sox-tempo-request/0.1", "task": TASK, "component": COMPONENT}[field]:
            raise ValidationError(f"{field}:mismatch")
    fmt = {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": "float32",
    }
    for field, expected in fmt.items():
        if request.get(field) != expected:
            raise ValidationError(f"{field}:unsupported")
    profile = request.get("profile")
    if profile not in {"speech", "music", "linear", "quick"}:
        raise ValidationError("profile:unsupported")
    tempo = request.get("tempo_factor")
    if not isinstance(tempo, (int, float)) or isinstance(tempo, bool) or not math.isfinite(float(tempo)):
        raise ValidationError("tempo_factor:invalid")
    tempo = float(tempo)
    if tempo <= 0.0 or tempo > 8.0:
        raise ValidationError("tempo_factor:out_of_range")
    epoch = request.get("epoch")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise ValidationError("epoch:invalid")
    reset = request.get("reset")
    if not isinstance(reset, bool):
        raise ValidationError("reset:invalid")
    audio = request.get("input")
    if not isinstance(audio, list) or len(audio) != FRAME_SAMPLES:
        raise ValidationError("input:invalid_length")
    out: List[float] = []
    for i, sample in enumerate(audio):
        if not isinstance(sample, (int, float)) or isinstance(sample, bool):
            raise ValidationError(f"input[{i}]:type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValidationError(f"input[{i}]:nonfinite")
        if abs(value) > MAX_ABS_INPUT:
            raise ValidationError(f"input[{i}]:out_of_range")
        out.append(value)
    return {
        "schema_id": request["schema_id"],
        "task": TASK,
        "component": COMPONENT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": "float32",
        "tempo_factor": tempo,
        "profile": profile,
        "reset": reset,
        "epoch": epoch,
        "input": out,
    }


def validate_request_json(text: str) -> Dict[str, Any]:
    def parse_constant(token: str) -> Any:
        raise ValidationError(f"json:nonfinite:{token}")

    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValidationError(f"json:duplicate_key:{key}")
            obj[key] = value
        return obj

    value = json.loads(text, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook)
    _walk_finite(value, "request")
    return validate_request(value)


class ResetStateMachine:
    """Structural reset validator only; no candidate/runtime state is owned."""

    def __init__(self) -> None:
        self.epoch: int | None = None
        self.last_frame_index: int | None = None

    def apply(self, request: Mapping[str, Any], frame_index: int) -> Dict[str, Any]:
        req = validate_request(request)
        if req["reset"]:
            if req["epoch"] == self.epoch:
                raise ValidationError("reset:stale_epoch")
            self.epoch = req["epoch"]
            self.last_frame_index = frame_index
            return {"accepted": True, "action": "reset", "epoch": self.epoch}
        if self.epoch is None:
            raise ValidationError("process:missing_reset")
        if req["epoch"] != self.epoch:
            raise ValidationError("process:stale_epoch")
        self.last_frame_index = frame_index
        return {"accepted": True, "action": "process", "epoch": self.epoch}


def synthetic_control_frame(case: str) -> List[float]:
    if case == "silence":
        return [0.0] * FRAME_SAMPLES
    if case == "impulse":
        out = [0.0] * FRAME_SAMPLES
        out[0] = 1.0
        return out
    if case == "sine_440":
        # deterministic, no external corpus; 440 Hz at 16 kHz
        return [0.25 * math.sin(2.0 * math.pi * 440.0 * i / SAMPLE_RATE_HZ) for i in range(FRAME_SAMPLES)]
    if case == "dc":
        return [0.1] * FRAME_SAMPLES
    raise ValueError(f"unknown synthetic case: {case}")


def adverse_cases() -> Dict[str, Any]:
    valid_base = {
        "schema_id": "audio-sdk/sox-tempo-request/0.1",
        "task": TASK,
        "component": COMPONENT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": "float32",
        "tempo_factor": 1.25,
        "profile": "speech",
        "reset": True,
        "epoch": 1,
        "input": synthetic_control_frame("silence"),
    }

    bad_requests = [
        ("missing_field", {k: v for k, v in valid_base.items() if k != "tempo_factor"}),
        ("unknown_field", dict(valid_base, extra=True)),
        ("bad_schema", dict(valid_base, schema_id="bad")),
        ("bad_task", dict(valid_base, task="bad")),
        ("bad_component", dict(valid_base, component="bad")),
        ("bad_rate", dict(valid_base, sample_rate_hz=48000)),
        ("bad_channels", dict(valid_base, channels=2)),
        ("bad_frame", dict(valid_base, frame_samples=320)),
        ("bad_format", dict(valid_base, sample_format="int16")),
        ("bad_profile", dict(valid_base, profile="fast")),
        ("tempo_zero", dict(valid_base, tempo_factor=0.0)),
        ("tempo_negative", dict(valid_base, tempo_factor=-1.0)),
        ("tempo_large", dict(valid_base, tempo_factor=9.0)),
        ("tempo_nan", dict(valid_base, tempo_factor=float("nan"))),
        ("tempo_inf", dict(valid_base, tempo_factor=float("inf"))),
        ("input_short", dict(valid_base, input=[0.0] * 159)),
        ("input_long", dict(valid_base, input=[0.0] * 161)),
        ("input_nan", dict(valid_base, input=[0.0] * 159 + [float("nan")])),
        ("input_inf", dict(valid_base, input=[0.0] * 159 + [float("inf")])),
        ("input_oor", dict(valid_base, input=[0.0] * 159 + [5.0])),
        ("epoch_bad", dict(valid_base, epoch=-1)),
        ("reset_bad", dict(valid_base, reset="true")),
    ]

    request_results = []
    for name, req in bad_requests:
        try:
            validate_request(req)
            request_results.append({"case": name, "rejected": False, "error": None})
        except Exception as err:  # noqa: BLE001
            request_results.append({"case": name, "rejected": True, "error": type(err).__name__})

    json_cases = [
        ("nan", '{"tempo_factor": NaN}'),
        ("inf", '{"tempo_factor": Infinity}'),
        ("neginf", '{"tempo_factor": -Infinity}'),
        ("duplicate", '{"a":1,"a":2}'),
    ]
    json_results = []
    for name, text in json_cases:
        try:
            validate_request_json(text)
            json_results.append({"case": name, "rejected": False, "error": None})
        except Exception as err:  # noqa: BLE001
            json_results.append({"case": name, "rejected": True, "error": type(err).__name__})

    sm = ResetStateMachine()
    reset_results = []
    try:
        sm.apply(dict(valid_base, reset=False), 0)
        reset_results.append({"case": "process_before_reset", "rejected": False, "error": None})
    except Exception as err:  # noqa: BLE001
        reset_results.append({"case": "process_before_reset", "rejected": True, "error": type(err).__name__})
    sm.apply(valid_base, 0)
    try:
        sm.apply(dict(valid_base, reset=True, epoch=1), 1)
        reset_results.append({"case": "stale_reset_epoch", "rejected": False, "error": None})
    except Exception as err:  # noqa: BLE001
        reset_results.append({"case": "stale_reset_epoch", "rejected": True, "error": type(err).__name__})
    try:
        sm.apply(dict(valid_base, reset=False, epoch=2), 2)
        reset_results.append({"case": "stale_process_epoch", "rejected": False, "error": None})
    except Exception as err:  # noqa: BLE001
        reset_results.append({"case": "stale_process_epoch", "rejected": True, "error": type(err).__name__})
    sm.apply(dict(valid_base, reset=True, epoch=2), 3)
    ok = sm.apply(dict(valid_base, reset=False, epoch=2), 4)
    reset_results.append({"case": "valid_reset_then_process", "rejected": False, "error": None, "result": ok})

    return {
        "invalid_requests": request_results,
        "invalid_requests_all_rejected": all(r["rejected"] for r in request_results),
        "invalid_json": json_results,
        "invalid_json_all_rejected": all(r["rejected"] for r in json_results),
        "reset_validation": reset_results,
        "reset_validation_matches_expectation": all(r["rejected"] for r in reset_results if r["case"] != "valid_reset_then_process") and any(r["case"] == "valid_reset_then_process" for r in reset_results),
        "missing_result_qualifies_candidate": False,
    }


def boundary_snapshot() -> Dict[str, Any]:
    return {
        "task_local_only": True,
        "provider_registered": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "opt_in_required": True,
        "public_api_abi_changed": False,
        "installed_v0_unchanged": True,
        "registry_changed": False,
        "shared_cmake_changed": False,
        "ci_changed": False,
        "board_or_handoff_changed": False,
        "real_corpus_or_weights": False,
        "benchmark_claim": False,
        "release_claim": False,
        "runtime_execution_attempted": False,
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
        },
    }


def git(*args: str, cwd: Path = SDK_ROOT) -> str:
    proc = subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def newest_merge_base(cwd: Path = SDK_ROOT) -> Tuple[str | None, str | None, List[str]]:
    tried = []
    candidates: List[Tuple[int, str, str]] = []
    for ref in ("origin/main", "main"):
        tried.append(ref)
        proc = subprocess.run(["git", "-C", str(cwd), "merge-base", "HEAD", ref], capture_output=True, text=True)
        if proc.returncode != 0:
            continue
        base = proc.stdout.strip()
        if not base:
            continue
        count = subprocess.run(["git", "-C", str(cwd), "rev-list", "--count", f"{base}..HEAD"], capture_output=True, text=True)
        if count.returncode != 0:
            continue
        try:
            distance = int(count.stdout.strip())
        except ValueError:
            continue
        candidates.append((distance, base, ref))
    if not candidates:
        return None, None, tried
    candidates.sort(key=lambda item: (item[0], item[2]))
    _, base, ref = candidates[0]
    return base, ref, tried


def diff_scope(cwd: Path = SDK_ROOT) -> Dict[str, Any]:
    base, ref, tried = newest_merge_base(cwd)
    if base is None:
        return {
            "base": None,
            "base_ref": None,
            "refs_tried": tried,
            "status": "scope_base_unavailable",
            "in_scope": False,
            "changed_files": [],
            "out_of_scope_files": [],
        }
    proc = subprocess.run(["git", "-C", str(cwd), "diff", "--name-only", f"{base}...HEAD"], check=True, capture_output=True, text=True)
    changed = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    out = [p for p in changed if not p.startswith(TASK_PREFIX)]
    return {
        "base": base,
        "base_ref": ref,
        "refs_tried": tried,
        "status": "ok" if not out else "base_out_of_scope_change",
        "in_scope": len(out) == 0,
        "changed_files": changed,
        "out_of_scope_files": out,
    }


def build_report() -> Dict[str, Any]:
    ev = evidence_pin()
    board = board_row()
    inv = inventory_row()
    source = probe_source_paths()
    runtime = probe_runtime_modules()
    artifacts = probe_artifacts()
    adverse = adverse_cases()
    scope = diff_scope()
    blockers = [gate["id"] for gate in GATES]
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": "DEFER",
        "status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "readiness": "incomplete",
        "candidate_qualified": False,
        "proposal_only": True,
        "installed_v0_unchanged": True,
        "no_missing_result_qualifies_candidate": True,
        "evidence": ev,
        "board_link": board,
        "inventory_link": inv,
        "profile": {
            "name": "rate",
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        },
        "installed_geometry": boundary_snapshot()["format"],
        "source_probe": source,
        "runtime_probe": runtime,
        "artifact_probe": artifacts,
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "release_gates": GATES,
        "gates": blockers,
        "remaining_gates": blockers,
        "adverse": adverse,
        "boundary": boundary_snapshot(),
        "scope": scope,
        "checks": {
            "real_corpus_used": False,
            "real_audio_used": False,
            "candidate_executed": False,
            "network_used": False,
            "downloads_performed": False,
            "provider_registered": False,
            "public_surface_changed": False,
        },
    }
    report["canonical_sha256"] = sha256_bytes(canonical_bytes(report))
    return report


def build_contract(report: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": report["decision"],
        "status": report["status"],
        "qualification": {
            "status": report["qualification_status"],
            "readiness": report["readiness"],
            "decision": report["decision"],
            "candidate_qualified": report["candidate_qualified"],
            "proposal_only": report["proposal_only"],
            "all_required_results_present": False,
            "no_missing_result_qualifies_candidate": True,
        },
        "installed_geometry": report["installed_geometry"],
        "boundary": report["boundary"],
        "board_link": report["board_link"]["projection"],
        "inventory_link": report["inventory_link"]["projection"],
        "evidence": report["evidence"],
        "source_pins": source_pins(),
        "boundary_pins": boundary_pins(),
        "required_artifacts": report["required_artifacts"],
        "release_gates": report["release_gates"],
        "adverse_summary": {
            "invalid_requests_all_rejected": report["adverse"]["invalid_requests_all_rejected"],
            "invalid_json_all_rejected": report["adverse"]["invalid_json_all_rejected"],
            "reset_validation_matches_expectation": report["adverse"]["reset_validation_matches_expectation"],
            "missing_result_qualifies_candidate": False,
        },
    }
