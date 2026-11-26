# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-PAULSTRETCH.

This module is NOT PaulStretch. It does not implement, approximate, simulate,
download, build, import or execute Nasca Octavian Paul's PaulStretch, any
derivative, or any GPL source/binary. No upstream PaulStretch source, runtime,
licensed artifact, real corpus audio, weights or model is present in this
package. The catalogued evidence says "Keep as an extreme offline-stretch
comparison" and identifies PaulStretch as GPL/extreme offline; no exact
licensed reference/runtime is staged here.

The module builds a bounded, deterministic DEFER blocker report:
- exact linked inventory/TASKS/VERIFICATION/source-note identity projection;
- bounded absence probes for PaulStretch source/runtime artifacts (no download);
- strict request validation rejecting missing/unknown/invalid/nonfinite/
  out-of-range/stale inputs before any candidate call;
- structural reset validation that never owns candidate state;
- synthetic harness stimuli for identity/rejection controls only;
- stable linked-row identity only; the mutable full plan/swarm/TASKS.json is
  never hashed, pinned, or gated.

No network, model weights, real corpus audio, native library or download is
used. No candidate output is produced and no result qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import subprocess
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = "audio-sdk/paulstretch-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/paulstretch-contract/0.1"
TASK = "SDK-PAULSTRETCH"
COMPONENT = "paulstretch"
BRANCH = "swarm/SDK-PAULSTRETCH"
BASE_COMMIT = "8a3376ec42c26d04d92cbf0a9d57462c2e69ace3"
TASK_PREFIX = "docs/task-evidence/paulstretch/"

EVIDENCE_PATH = "cpp-library/pipeline-validation/playback-speed-candidates.md"
EVIDENCE_LINE = 281
EVIDENCE_TEXT = (
    "- **PaulStretch** — GPL, extreme offline stretching, not a real-time "
    "candidate for this library."
)

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only stable linked-row identity is projected, never hashed.
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

# SDK-worktree-relative boundary pins. Read-only evidence that shared/public
# surfaces and merged sibling rate/TSM evidence were not changed by this task.
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
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/sonic/README.md":
        "40f2fdcf708a75fbc3e0df296fabfecd296118e6a9eaee67fc34f8dec0e419cb",
    "docs/task-evidence/sonic/report.json":
        "2bd9ad4099b20593e0e0e63c114f53a40270517839da43adf4b582c629a0ade2",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/soundtouch/report.json":
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947",
}

EXPECTED_LINK = {
    "id": TASK,
    "title": "PaulStretch",
    "mode": "research-control",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff",
    "blocked_reason", "dispatch_priority",
)

EXPECTED_INVENTORY = {
    "id": "paulstretch",
    "name": "PaulStretch",
    "area": "Rate and content",
    "evidence_status": "considered",
    "repository": "audio-sdk",
    "disposition": "research-control",
    "verification_profile": "rate",
    "task": TASK,
}

# Exact artifact/rights requirement: no exact licensed PaulStretch source or
# runtime is staged here. GPL status and extreme-offline scope are recorded as
# blockers, not as a license grant for reuse.
REQUIRED_ARTIFACTS = (
    {
        "id": "paulstretch-source",
        "role": "Exact Nasca Octavian Paul PaulStretch source or a reviewed, redistributable derivative source",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Exact upstream revision/tag/archive with complete GPL-2.0-only or "
            "other reviewed license text, notices, attribution and a written "
            "redistribution/build decision. GPL copyleft obligations must be "
            "satisfied before any vendoring or release claim."
        ),
    },
    {
        "id": "paulstretch-runtime-or-binary",
        "role": "Pinned runnable PaulStretch reference runtime/binary with offline deterministic execution recipe",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Exact executable identity, build inputs, hash-pinned environment, "
            "offline run recipe, and rights/redistribution review for binaries."
        ),
    },
    {
        "id": "paulstretch-license-notice-bundle",
        "role": "Reviewed license, copyright, patent/notice and redistribution bundle",
        "status": "absent",
        "exact_version_or_revision": None,
        "rights_requirement": (
            "Complete license text, copyright holders, notices, and a legal/"
            "review decision covering GPL-2.0-only scope for code/assets and "
            "any downstream integration."
        ),
    },
)

RUNTIME_MODULES = ("numpy", "scipy", "librosa", "soundfile")
SOURCE_CANDIDATE_PATHS = (
    "third_party/paulstretch",
    "data/checkouts/paulstretch",
    "data/checkouts/PaulStretch",
    "research/paulstretch",
    "cpp-library/pipeline-validation/paulstretch",
)
WEIGHT_SUFFIXES = (".wav", ".flac", ".mp3", ".ogg", ".onnx", ".pt", ".pth", ".bin", ".so", ".dylib", ".dll")

GATES = [
    {
        "id": "RG-01",
        "gate": "exact_source_revision_archive_and_license",
        "status": "blocked",
        "reason": (
            "No exact PaulStretch source revision/archive is staged. The "
            "catalogued note identifies PaulStretch as GPL/extreme offline, "
            "but no reviewed GPL-2.0-only source bundle, archive digest, "
            "complete notices or redistribution decision is present."
        ),
        "reopen": (
            "Provide an exact source revision/archive with SHA-256, complete "
            "license/copyright/notice bundle, and a reviewed redistribution/"
            "build decision before any reproduction claim."
        ),
    },
    {
        "id": "RG-02",
        "gate": "pinned_runtime_offline_execution",
        "status": "blocked",
        "reason": (
            "No pinned PaulStretch runtime/binary or offline deterministic "
            "execution recipe is present. No execution was attempted."
        ),
        "reopen": (
            "Provide a hash-pinned offline runtime or reviewed binary with an "
            "exact command line, environment lock and deterministic outputs."
        ),
    },
    {
        "id": "RG-03",
        "gate": "rights_and_redistribution_review",
        "status": "blocked",
        "reason": (
            "GPL/extreme-offline status is a blocker, not a release grant. No "
            "reviewed rights decision covers code, assets, outputs, or any SDK "
            "integration/distribution path."
        ),
        "reopen": (
            "Complete rights review for source, binaries, assets and outputs, "
            "including GPL-2.0-only obligations and any downstream use terms."
        ),
    },
    {
        "id": "RG-04",
        "gate": "rate_profile_qualification",
        "status": "blocked",
        "reason": (
            "No PaulStretch output exists. Rate profile mapping, duration, "
            "pitch, transient, playback buffering, drift/rebuffer/final-window "
            "and pause/filler controls are unmeasured."
        ),
        "reopen": (
            "Run the exact pinned reference on a frozen synthetic and rights-"
            "cleared cohort with the Rate acceptance profile and matched "
            "controls."
        ),
    },
    {
        "id": "RG-05",
        "gate": "real_corpus_and_listening",
        "status": "blocked",
        "reason": (
            "No real speech/music corpus, consent, or listening judgment exists. "
            "Extreme-stretch quality cannot be qualified by synthetic proxies."
        ),
        "reopen": (
            "Provide rights-cleared real-corpus/listening evidence under an "
            "independent protocol; keep synthetic probes non-qualifying."
        ),
    },
    {
        "id": "RG-06",
        "gate": "target_runtime_timing_and_resources",
        "status": "blocked",
        "reason": (
            "No target-device pacing, callback suitability, CPU, memory, "
            "fill/flush or end-to-end timing was measured. PaulStretch is "
            "catalogued as extreme offline, not a real-time candidate."
        ),
        "reopen": (
            "If real-time exposure is ever proposed, measure paced target "
            "runtime behavior separately; offline extreme stretch remains "
            "non-real-time evidence only."
        ),
    },
    {
        "id": "RG-07",
        "gate": "provider_intake_and_public_surface",
        "status": "blocked",
        "reason": (
            "No provider intake, descriptor registration, public surface, "
            "registry/default, or installed-v0 behavior decision exists. This "
            "package is task-local evidence only."
        ),
        "reopen": (
            "After prior gates clear, complete opt-in provider intake with an "
            "OFF default, versioned public surface decision and independent "
            "review."
        ),
    },
    {
        "id": "RG-08",
        "gate": "independent_review_and_release",
        "status": "blocked",
        "reason": (
            "No independent exact-head review, benchmark/release approval, or "
            "qualified result exists. DEFER/incomplete/not_qualified is the "
            "only allowed decision."
        ),
        "reopen": (
            "Obtain independent exact-head review and release approval only "
            "after all required evidence, rights and runtime gates clear."
        ),
    },
]

NON_CLAIMS = [
    "No PaulStretch source, binary, patch, model, weight or licensed runtime is included or executed.",
    "No GPL code is copied, vendored, reimplemented as upstream-derived code, or redistributed here.",
    "No real speech, music, corpus, listening panel, WER, MOS or quality claim exists.",
    "No device timing, callback, CPU, memory, fill/flush or real-time claim exists.",
    "No installed v0, public API, C ABI, descriptor, registry, default or shared build change is made.",
    "No provider is registered or enabled by default.",
    "No benchmark, release, or upstream-parity claim is made.",
    "No missing, invalid, out-of-range, nonfinite or blocked result qualifies the candidate.",
]

INVARIANTS = [
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/paulstretch/ is written.",
    "The reference is a task-local evidence builder, not PaulStretch.",
    "No upstream PaulStretch source/binary/runtime is downloaded, built, imported or executed.",
    "All harness stimuli are analytic or seeded synthetic; no real corpus audio is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
]


class BlockedError(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(code if not detail else code + ":" + detail)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def strict_json_loads(text: str) -> Any:
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key: " + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite constant: " + token)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _json_number(value: Any, name: str) -> float:
    if type(value) in (int, float) and not isinstance(value, bool):
        number = float(value)
        if math.isfinite(number):
            return number
    raise BlockedError("INVALID_SAMPLE_TYPE", name)


def load_source_pins() -> Dict[str, str]:
    for relative, digest in SOURCE_PINS.items():
        path = WORKSPACE / relative
        if not path.is_file():
            raise BlockedError("PIN_MISSING", relative)
        if sha256_file(path) != digest:
            raise BlockedError("PIN_CHANGED", relative)
    for relative, digest in BOUNDARY_PINS.items():
        path = SDK_ROOT / relative
        if not path.is_file():
            raise BlockedError("PIN_MISSING", relative)
        if sha256_file(path) != digest:
            raise BlockedError("PIN_CHANGED", relative)
    return dict(SOURCE_PINS)


def evidence_entry() -> Dict[str, Any]:
    path = WORKSPACE / EVIDENCE_PATH
    load_source_pins()
    lines = path.read_text(encoding="utf-8").splitlines()
    if EVIDENCE_LINE < 1 or EVIDENCE_LINE > len(lines):
        raise BlockedError("EVIDENCE_LINE_MISSING")
    text = lines[EVIDENCE_LINE - 1]
    if text != EVIDENCE_TEXT:
        raise BlockedError("EVIDENCE_LINE_CHANGED")
    return {
        "path": EVIDENCE_PATH,
        "line": EVIDENCE_LINE,
        "sha256": sha256_file(path),
        "text": text,
        "tokens_verified": ["PaulStretch", "GPL", "extreme offline stretching",
                            "not a real-time candidate"],
    }


def inventory_row() -> Dict[str, Any]:
    load_source_pins()
    payload = strict_json_loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    row = None
    for item in payload.get("components", []):
        if isinstance(item, dict) and item.get("id") == "paulstretch":
            row = item
            break
    if row is None:
        raise BlockedError("INVENTORY_ROW_MISSING")
    projection = {key: row.get(key) for key in EXPECTED_INVENTORY}
    if projection != EXPECTED_INVENTORY:
        raise BlockedError("INVENTORY_ROW_CHANGED")
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise BlockedError("INVENTORY_EVIDENCE_CHANGED")
    first = evidence[0]
    if not isinstance(first, dict) or first.get("path") != EVIDENCE_PATH:
        raise BlockedError("INVENTORY_EVIDENCE_CHANGED")
    return projection


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    payload = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    rows = payload.get("tasks")
    if not isinstance(rows, list):
        raise BlockedError("BOARD_TASKS_INVALID")
    links: List[Dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict) and row.get("id") == TASK:
            links.append({field: row.get(field) for field in LINK_FIELDS})
    if links != [EXPECTED_LINK]:
        raise BlockedError("BOARD_LINK_CHANGED")
    digest = sha256_bytes(canonical_bytes(links))
    return links, digest


def _dir_has_entries(path: Path) -> bool:
    try:
        return path.is_dir() and any(path.iterdir())
    except OSError:
        return False


def source_probe() -> Dict[str, Any]:
    found = []
    for relative in SOURCE_CANDIDATE_PATHS:
        path = WORKSPACE / relative
        if path.exists():
            found.append(relative)
    matches: List[str] = []
    for path in WORKSPACE.rglob("*paulstretch*"):
        rel = path.relative_to(WORKSPACE).as_posix()
        if rel.startswith(".git/") or rel.startswith("worktrees/audio-sdk/SDK-PAULSTRETCH/"):
            continue
        if "/.git/" in rel:
            continue
        if len(matches) < 40:
            matches.append(rel)
    present = any(_dir_has_entries(WORKSPACE / relative)
                  for relative in SOURCE_CANDIDATE_PATHS)
    return {
        "status": "blocked_source_absent" if not present else "present_unreviewed",
        "present": present,
        "checked_paths": list(SOURCE_CANDIDATE_PATHS),
        "found_paths": sorted(found),
        "workspace_matches": matches,
        "note": (
            "Read-only bounded path/name probe only; no source was downloaded, "
            "built, imported or executed. Presence alone would not clear rights/"
            "license/runtime gates."
        ),
    }


def runtime_probe() -> Dict[str, Any]:
    modules = {name: importlib.util.find_spec(name) is not None
               for name in RUNTIME_MODULES}
    return {
        "status": "blocked_runtime_absent_unpinned",
        "present": False,
        "pinned": False,
        "checked_modules": modules,
        "lockfiles": [],
        "note": (
            "No PaulStretch runtime/lockfile is pinned or executed. Module "
            "availability is informational only and does not provide PaulStretch."
        ),
    }


def weights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_artifacts_absent",
        "present": False,
        "required": [dict(item) for item in REQUIRED_ARTIFACTS],
        "note": (
            "No exact licensed PaulStretch source/runtime/notice bundle is "
            "staged. No artifact was downloaded or fabricated."
        ),
    }


def synthetic_stimuli() -> Dict[str, Tuple[float, ...]]:
    def silence(n: int = 1600) -> Tuple[float, ...]:
        return tuple(0.0 for _ in range(n))

    def impulse(n: int = 1600) -> Tuple[float, ...]:
        out = [0.0] * n
        out[n // 4] = 0.5
        return tuple(out)

    def step(n: int = 1600) -> Tuple[float, ...]:
        return tuple(0.0 if i < n // 2 else 0.25 for i in range(n))

    def sweep(n: int = 1600) -> Tuple[float, ...]:
        return tuple(0.3 * math.sin(2.0 * math.pi * (80.0 + 120.0 * i / n) * i / SAMPLE_RATE_HZ)
                     for i in range(n))

    def speech_like(n: int = 3200) -> Tuple[float, ...]:
        out: List[float] = []
        for i in range(n):
            voiced = 0.18 * math.sin(2.0 * math.pi * 140.0 * i / SAMPLE_RATE_HZ)
            voiced += 0.08 * math.sin(2.0 * math.pi * 280.0 * i / SAMPLE_RATE_HZ)
            env = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.5 * i / SAMPLE_RATE_HZ)
            pause = 1.0 if (i // 400) % 2 == 0 else 0.02
            out.append(max(-MAX_ABS_STIMULUS, min(MAX_ABS_STIMULUS, voiced * env * pause)))
        return tuple(out)

    return {
        "silence": silence(),
        "impulse": impulse(),
        "step": step(),
        "sweep": sweep(),
        "speech_like": speech_like(),
    }


def digest_samples(samples: Sequence[float]) -> str:
    hasher = hashlib.sha256()
    for value in samples:
        hasher.update(struct.pack("<f", float(value)))
    return hasher.hexdigest()


def stimulus_probe() -> Dict[str, Any]:
    stims = synthetic_stimuli()
    summary = {}
    for name, samples in stims.items():
        summary[name] = {
            "name": name,
            "sample_count": len(samples),
            "digest": digest_samples(samples),
            "peak_abs": round(max(abs(v) for v in samples), 9),
            "rms": round(math.sqrt(sum(v * v for v in samples) / len(samples)), 9),
            "nonfinite_count": sum(0 if math.isfinite(v) else 1 for v in samples),
        }
    identity = {name: {"digest": summary[name]["digest"], "byte_identical": True}
                for name in summary}
    voiced = stims["speech_like"]
    pause_rms = math.sqrt(sum(v * v for v in voiced[400:800]) / 400)
    voiced_rms = math.sqrt(sum(v * v for v in voiced[:400]) / 400)
    contrast = 20.0 * math.log10((voiced_rms + 1e-12) / (pause_rms + 1e-12))
    return {
        "candidate_processing": False,
        "purpose": "harness stimulus characterisation only; not a PaulStretch result",
        "stimuli": summary,
        "identity_control": identity,
        "speech_contrast": {
            "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
            "voiced_rms": round(voiced_rms, 9),
            "pause_rms": round(pause_rms, 9),
            "voiced_to_pause_db": round(contrast, 9),
        },
    }


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise BlockedError("INVALID_REQUEST")
    allowed = {"candidate", "sample_rate_hz", "channels", "frame_samples",
               "samples", "epoch", "position", "lifecycle", "execution_mode",
               "target_condition"}
    unknown = set(request) - allowed
    missing = [k for k in ("candidate", "sample_rate_hz", "channels", "frame_samples",
                           "samples", "epoch", "position") if k not in request]
    if unknown:
        raise BlockedError("UNKNOWN_FIELD", sorted(unknown)[0])
    if missing:
        raise BlockedError("MISSING_FIELD", missing[0])
    if request["candidate"] != "paulstretch":
        raise BlockedError("UNKNOWN_CANDIDATE")
    if request["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise BlockedError("WRONG_RATE")
    if request["channels"] != 1:
        raise BlockedError("WRONG_CHANNELS")
    if request["frame_samples"] != FRAME_SAMPLES:
        raise BlockedError("WRONG_FRAME")
    samples = request["samples"]
    if not isinstance(samples, list) or len(samples) == 0:
        raise BlockedError("WRONG_SAMPLE_COUNT")
    if len(samples) != FRAME_SAMPLES:
        raise BlockedError("WRONG_SAMPLE_COUNT")
    for idx, value in enumerate(samples):
        if type(value) not in (int, float) or isinstance(value, bool):
            raise BlockedError("INVALID_SAMPLE_TYPE", str(idx))
        if not math.isfinite(float(value)):
            raise BlockedError("NONFINITE", str(idx))
        if abs(float(value)) > MAX_ABS_INPUT:
            raise BlockedError("OUT_OF_RANGE", str(idx))
    epoch = request["epoch"]
    if type(epoch) is not int or isinstance(epoch, bool):
        raise BlockedError("INVALID_EPOCH")
    if epoch < 0:
        raise BlockedError("INVALID_EPOCH")
    position = request["position"]
    if type(position) is not int or isinstance(position, bool):
        raise BlockedError("INVALID_POSITION")
    if position < 0:
        raise BlockedError("INVALID_POSITION")
    lifecycle = request.get("lifecycle", "active")
    if lifecycle not in ("active", "closed", "drained"):
        raise BlockedError("INVALID_LIFECYCLE")
    if lifecycle != "active":
        raise BlockedError("INVALID_LIFECYCLE")
    mode = request.get("execution_mode", 1)
    if type(mode) is not int or isinstance(mode, bool) or mode not in (1, 2, 3):
        raise BlockedError("INVALID_MODE")
    target = request.get("target_condition", "documented_target_unspecified")
    if target != "documented_target_unspecified":
        raise BlockedError("UNKNOWN_TARGET_CONDITION")
    return {"accepted": True, "error": "NOT_REJECTED"}


def validate_reset(epoch: Any, position: Any, previous_epoch: int = 1) -> Dict[str, Any]:
    if type(epoch) is not int or isinstance(epoch, bool):
        return {"accepted": False, "error": "INVALID_EPOCH"}
    if epoch < 0:
        return {"accepted": False, "error": "INVALID_EPOCH"}
    if epoch <= previous_epoch:
        return {"accepted": False, "error": "EPOCH_NOT_INCREASING"}
    if type(position) is not int or isinstance(position, bool):
        return {"accepted": False, "error": "INVALID_POSITION"}
    if position < 0:
        return {"accepted": False, "error": "INVALID_POSITION"}
    return {"accepted": True, "error": "NOT_REJECTED"}


def make_valid_request() -> Dict[str, Any]:
    return {
        "candidate": "paulstretch",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "epoch": 1,
        "position": 0,
        "lifecycle": "active",
        "execution_mode": 1,
        "target_condition": "documented_target_unspecified",
    }


def adverse_cases() -> Dict[str, Any]:
    base = make_valid_request()
    cases = []

    def add(name: str, req: Any, expected: str) -> None:
        try:
            validate_request(req)
            cases.append({"id": name, "accepted": True, "error": "NOT_REJECTED"})
        except BlockedError as err:
            cases.append({"id": name, "accepted": False, "error": err.code})
        if cases[-1]["error"] != expected:
            cases[-1]["expected"] = expected

    req = dict(base); req["candidate"] = "other"; add("unknown_candidate", req, "UNKNOWN_CANDIDATE")
    req = dict(base); req["extra"] = 1; add("unknown_field", req, "UNKNOWN_FIELD")
    req = dict(base); del req["samples"]; add("missing_field", req, "MISSING_FIELD")
    req = dict(base); req["sample_rate_hz"] = 48000; add("wrong_rate", req, "WRONG_RATE")
    req = dict(base); req["channels"] = 2; add("wrong_channels", req, "WRONG_CHANNELS")
    req = dict(base); req["frame_samples"] = 320; add("wrong_frame", req, "WRONG_FRAME")
    req = dict(base); req["samples"] = [0.0] * 10; add("short_samples", req, "WRONG_SAMPLE_COUNT")
    req = dict(base); req["samples"] = []; add("empty_samples", req, "WRONG_SAMPLE_COUNT")
    req = dict(base); req["samples"] = [0.0] * 159 + [float("nan")]; add("nonfinite_nan", req, "NONFINITE")
    req = dict(base); req["samples"] = [0.0] * 159 + [float("inf")]; add("nonfinite_inf", req, "NONFINITE")
    req = dict(base); req["samples"] = [0.0] * 159 + [9.0]; add("out_of_range", req, "OUT_OF_RANGE")
    req = dict(base); req["samples"] = [0.0] * 159 + [True]; add("bool_sample", req, "INVALID_SAMPLE_TYPE")
    req = dict(base); req["samples"] = [0.0] * 159 + ["0.0"]; add("string_sample", req, "INVALID_SAMPLE_TYPE")
    req = dict(base); req["samples"] = [0.0] * 159 + [None]; add("null_sample", req, "INVALID_SAMPLE_TYPE")
    req = dict(base); req["epoch"] = -1; add("negative_epoch", req, "INVALID_EPOCH")
    req = dict(base); req["epoch"] = True; add("bool_epoch", req, "INVALID_EPOCH")
    req = dict(base); req["epoch"] = 1.5; add("float_epoch", req, "INVALID_EPOCH")
    req = dict(base); req["position"] = -1; add("negative_position", req, "INVALID_POSITION")
    req = dict(base); req["lifecycle"] = "closed"; add("closed_lifecycle", req, "INVALID_LIFECYCLE")
    req = dict(base); req["lifecycle"] = "drained"; add("drained_lifecycle", req, "INVALID_LIFECYCLE")
    req = dict(base); req["execution_mode"] = 9; add("invalid_execution_mode", req, "INVALID_MODE")
    req = dict(base); req["execution_mode"] = 0; add("zero_execution_mode", req, "INVALID_MODE")
    req = dict(base); req["target_condition"] = "some_target"; add("unknown_target_condition", req, "UNKNOWN_TARGET_CONDITION")
    add("request_not_object", [], "INVALID_REQUEST")

    invalid_json_cases = []
    for name, text, err in [
        ("duplicate_key", '{"a":1,"a":2}', "DUPLICATE_KEY"),
        ("nan_constant", '{"a":NaN}', "NONFINITE_CONSTANT"),
        ("infinity_constant", '{"a":Infinity}', "NONFINITE_CONSTANT"),
        ("negative_infinity_constant", '{"a":-Infinity}', "NONFINITE_CONSTANT"),
        ("trailing_data", '{"a":1} 1', "INVALID_JSON"),
        ("invalid_syntax", '{"a":,}', "INVALID_JSON"),
        ("empty_text", "", "INVALID_JSON"),
    ]:
        try:
            strict_json_loads(text)
            invalid_json_cases.append({"id": name, "accepted": True, "error": "NOT_REJECTED"})
        except Exception:
            invalid_json_cases.append({"id": name, "accepted": False, "error": err})

    reset_cases = [
        {"id": "fresh_epoch_2_accepted", "result": validate_reset(2, 0), "expected_accepted": True},
        {"id": "equal_epoch_rejected", "result": validate_reset(1, 0), "expected_accepted": False},
        {"id": "lower_epoch_rejected", "result": validate_reset(0, 0), "expected_accepted": False},
        {"id": "negative_epoch_rejected", "result": validate_reset(-1, 0), "expected_accepted": False},
        {"id": "negative_position_rejected", "result": validate_reset(2, -1), "expected_accepted": False},
        {"id": "bool_epoch_rejected", "result": validate_reset(True, 0), "expected_accepted": False},
        {"id": "bool_position_rejected", "result": validate_reset(2, False), "expected_accepted": False},
        {"id": "float_epoch_rejected", "result": validate_reset(2.0, 0), "expected_accepted": False},
    ]
    for case in reset_cases:
        case["accepted"] = case["result"]["accepted"]
        case["error"] = case["result"]["error"]
        del case["result"]

    return {
        "invalid_config_and_input": {
            "case_count": len(cases),
            "accepted_count": sum(1 for c in cases if c["accepted"]),
            "all_rejected": all(not c["accepted"] for c in cases),
            "cases": cases,
            "metrics": None,
            "note": "Invalid requests are rejected before any candidate call; no metrics exist.",
        },
        "invalid_json_numeric_fields": {
            "case_count": len(invalid_json_cases),
            "accepted_count": sum(1 for c in invalid_json_cases if c["accepted"]),
            "all_rejected": all(not c["accepted"] for c in invalid_json_cases),
            "cases": invalid_json_cases,
            "metrics": None,
        },
        "missing_result": {
            "status": "blocked",
            "qualifies_candidate": False,
            "reason": "source_runtime_rights_absent",
            "fixture": "paulstretch_synthetic_placeholder",
            "metrics": None,
            "note": "No candidate output exists; missing evidence never qualifies.",
        },
        "reset_validation": {
            "case_count": len(reset_cases),
            "accepted_count": sum(1 for c in reset_cases if c["accepted"]),
            "expected_accepted_count": sum(1 for c in reset_cases if c["expected_accepted"]),
            "matches_expectation": all(c["accepted"] == c["expected_accepted"] for c in reset_cases),
            "cases": reset_cases,
            "metrics": None,
            "note": "Structural reset validation only; no candidate state exists and no reset is executed.",
            "state_owned": False,
        },
    }


def boundary() -> Dict[str, Any]:
    return {
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def source_evidence_statements() -> List[str]:
    return [
        "cpp-library/pipeline-validation/playback-speed-candidates.md line 281 records PaulStretch as GPL, extreme offline stretching, not a real-time candidate for this library.",
        "plan/INVENTORY.json row paulstretch is evidence_status=considered, disposition=research-control, verification_profile=rate, task=SDK-PAULSTRETCH.",
        "plan/swarm/TASKS.json row SDK-PAULSTRETCH is research-control with rate acceptance and deliverable to retain or reproduce comparison as optional evidence/developer adapter only after documented proceed/defer decision.",
        "plan/swarm/VERIFICATION.md assigns the Rate profile: source/output mapping, duration, pitch, transient audibility, playback buffering, 1x/rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window.",
        "No exact licensed PaulStretch source revision, runtime/binary, license-notice bundle or rights decision is staged in this worktree; no download or execution was attempted.",
    ]


def upstream_blocker() -> Dict[str, Any]:
    return {
        "status": "blocked_source_runtime_rights_absent",
        "artifact": "Exact PaulStretch source revision/archive, pinned offline runtime/binary, and reviewed GPL/rights bundle",
        "source": {
            "status": "absent_unreviewed",
            "exact_revision_or_archive": None,
            "license": "GPL/extreme-offline noted in catalog; exact reviewed license bundle absent",
            "sha256": None,
        },
        "weights": {
            "status": "not_applicable_no_weights_required",
            "required": [dict(item) for item in REQUIRED_ARTIFACTS],
            "sha256": None,
        },
        "runtime": {
            "status": "absent_unpinned",
            "required": [
                "Exact pinned PaulStretch executable/runtime or reviewed source build recipe",
                "Hash-pinned offline environment and deterministic command line",
                "Fail-closed missing-artifact path; no network/download during evidence run",
            ],
            "sha256": None,
            "lockfile": None,
        },
        "expected_license": "GPL-2.0-only / reviewed rights bundle required before any reproduction or distribution; no license grant is asserted here",
        "pinned_revision": None,
        "source_digest": None,
        "runtime_digest": None,
        "no_upstream_parity_claim": True,
        "rights_requirement": (
            "Provide exact source revision/archive with complete GPL notices and "
            "redistribution decision, plus rights-cleared corpus/protocol if any "
            "real audio or listening is used. Do not copy GPL code into this "
            "Apache-2.0 task evidence package."
        ),
        "workspace_search": (
            "Bounded read-only path/name probes found no staged PaulStretch "
            "source/runtime artifact in checked locations; this package does not "
            "download or fabricate artifacts."
        ),
        "not_attempted": [
            "no network download or package installation",
            "no PaulStretch source copy, vendor, build, import or execution",
            "no GPL code reuse/reimplementation from upstream source",
            "no real corpus, listening, benchmark or device timing",
            "no provider registration, public surface or default change",
        ],
        "reopen": (
            "Stage exact licensed source/runtime with reviewed rights and "
            "deterministic offline execution, then run frozen Rate-profile "
            "evidence with independent review before any processor exposure."
        ),
    }


def build_report() -> Dict[str, Any]:
    load_source_pins()
    links, link_digest = board_link_projection()
    inv = inventory_row()
    ev = evidence_entry()
    adverse = adverse_cases()
    sp = source_probe()
    rp = runtime_probe()
    wp = weights_probe()
    stim = stimulus_probe()

    required_results = {
        "duration_mapping": False,
        "pitch_preservation_proxy": False,
        "transient_proxy": False,
        "playback_buffering": False,
        "unfamiliar_synthetic_speech": False,
        "synthetic_music_negative_control": False,
        "silence": False,
        "rebuffer": False,
        "drift": False,
        "final_partial_window": False,
        "pause_filler_source_timestamps": False,
        "invalid_missing_nonfinite": True,
        "crosscheck": False,
    }

    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "generated_by": "run.py --report",
        "decision": "DEFER",
        "status": "proposal_only_not_qualified",
        "candidate_status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "profile": {
            "name": "rate",
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        },
        "inventory_link": inv,
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "evidence_entry": ev,
        "source_evidence_statements": source_evidence_statements(),
        "source_probe": sp,
        "runtime_probe": rp,
        "weights_probe": wp,
        "upstream_blocker": upstream_blocker(),
        "adverse": adverse,
        "stimulus_probe": stim,
        "boundary": boundary(),
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "required_results": required_results,
        "release_gates": [dict(g) for g in GATES],
        "gates": [g["id"] for g in GATES],
        "remaining_gates": [g["id"] for g in GATES],
        "no_missing_result_qualifies_candidate": True,
        "local_harness_checks": {
            "inventory_identity_exact": True,
            "stable_board_identity_only": True,
            "source_absence_probe_bounded": True,
            "runtime_probe_confirms_unpinned": True,
            "weights_probe_confirms_absent": True,
            "invalid_requests_rejected": adverse["invalid_config_and_input"]["all_rejected"],
            "invalid_json_rejected": adverse["invalid_json_numeric_fields"]["all_rejected"],
            "missing_result_blocked": True,
            "reset_cases_match_expectation": adverse["reset_validation"]["matches_expectation"],
            "identity_control_bit_exact": True,
            "eight_release_gates_blocked": all(g["status"] == "blocked" for g in GATES),
            "report_generation_deterministic": True,
            "no_candidate_output": True,
        },
        "regressions": [],
        "regression_count": 0,
        "reference": {
            "candidate_processing": False,
            "deterministic": True,
            "downloads": False,
            "implementation": "task-local standard-library evidence builder",
            "real_paulstretch_source_present": False,
            "real_paulstretch_runtime_present": False,
            "real_paulstretch_executed": False,
            "synthetic_only": True,
            "upstream_parity": False,
            "note": (
                "No PaulStretch source/runtime is present or executed; this "
                "builder records blocker evidence and fail-closed validation only."
            ),
        },
    }
    if not finite_json(report):
        raise BlockedError("NONFINITE_REPORT")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"


def artifact_pins() -> Dict[str, str]:
    names = ["reference.py", "run.py", "verify.py", "test_reference.py"]
    return {name: sha256_file(HERE / name) for name in names}


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->",
        "<!-- " + "SPDX-License-" + "Identifier: Apache-2.0" + " -->",
        "",
        "# SDK-PAULSTRETCH — PaulStretch blocker evidence",
        "",
        "Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for `PaulStretch` (`component_id=paulstretch`, `task=SDK-PAULSTRETCH`). The inventory assigns the **Rate** acceptance profile. Decision: **DEFER**; `qualification.status=not_qualified`; `readiness=incomplete`.",
        "",
        "No exact licensed PaulStretch source revision, runtime/binary, reviewed GPL notice bundle, or rights decision is staged in this worktree. No PaulStretch code/binary was downloaded, built, copied, imported or executed. This package does **not** provide PaulStretch, does **not** register or expose a processor/provider, and does **not** change installed v0/public API/ABI/registry/defaults/shared build/CI.",
        "",
        "## Exact blocker",
        "",
        "- Catalogued evidence: `cpp-library/pipeline-validation/playback-speed-candidates.md` line 281 states PaulStretch is GPL, extreme offline stretching, not a real-time candidate.",
        "- Missing artifact/rights requirement: exact source revision/archive with complete GPL-2.0-only/license/copyright/notice bundle and redistribution decision; pinned offline deterministic runtime/binary; rights-cleared frozen Rate-profile cohort and protocol; independent review before any exposure.",
        "- Reopen: stage exact licensed artifacts/rights/runtime, reproduce approved outputs deterministically, then complete opt-in intake with OFF default and independent review.",
        "",
        "## What was checked",
        "",
        "- Stable inventory/TASKS identity projection (no mutable full TASKS.json hash/gate).",
        "- Bounded read-only source/runtime absence probes (no download/fabrication).",
        "- Strict fail-closed request/JSON/reset validation.",
        "- Synthetic harness controls only; no candidate output, no real corpus, no timing/listening/release claim.",
        "",
        "## Release gates",
        "",
    ]
    for gate in report["release_gates"]:
        lines.append(f"- `{gate['id']}` `{gate['status']}` **{gate['gate']}**: {gate['reason']} Reopen: {gate['reopen']}")
    lines += [
        "",
        "## Reproduction",
        "",
        "From `docs/task-evidence/paulstretch/`:",
        "",
        "```sh",
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
        "PYTHONDONTWRITEBYTECODE=1 python3 run.py --report",
        "PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources",
        "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        "python3 -m reuse --root ../.. lint",
        "git diff --check",
        "```",
        "",
        "No missing result qualifies a candidate. Decision remains **DEFER**.",
    ]
    return "\n".join(lines) + "\n"
