# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local feasibility evidence for SDK-FASTENHANCER-MEDIUM-REFERENCE.

This module is a deterministic, standard-library evidence builder, not the
FastEnhancer Medium model. It pins the source, weight and runtime identities
recorded by the merged Pro evidence, probes their availability for an SDK
reference, and rejects missing, invalid and nonfinite admissions. No model is
loaded, no weight byte is read, no runtime is invoked and no audio quality,
device, benchmark, listening or release result is produced.

The exact licensed runtime is absent from this SDK worktree, the weights are a
private evaluation asset whose redistribution terms are unrecorded, and the
native backend has no scalar or SDK-consumable tier. The package therefore
reports ``DEFER`` / ``incomplete`` / ``not_qualified`` and never qualifies a
candidate. Only the stable linked task-row identity enters canonical bytes.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
WORKSPACE = Path(os.environ.get("AUDIOML_WORKSPACE", str(HERE.parents[5])))
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

TASK = "SDK-FASTENHANCER-MEDIUM-REFERENCE"
TITLE = "FastEnhancer Medium reference"
COMPONENT = "fastenhancer-medium-reference"
REFERENCE_FAMILY = "fastenhancer"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "a1e7573dc38ebd0d8efb3050dd38613ec0950941"
BRANCH = "swarm/SDK-FASTENHANCER-MEDIUM-REFERENCE"
PROFILE = "enhancement"
SCHEMA_ID = "audio-sdk/task-evidence/fastenhancer-medium-reference/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence/fastenhancer-medium-reference/contract/0.1"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"
TASK_PREFIX = "docs/task-evidence/fastenhancer-medium-reference"

SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
LICENSE_TEXT = SPDX_COPYRIGHT_LINE + "\n" + SPDX_LICENSE_LINE + "\n"

EXPECTED_FILES = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
STATIC_ARTIFACTS = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json.license",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
REPORT_ARTIFACTS = STATIC_ARTIFACTS + ("contract.json",)

# Public v0 geometry is documented only; nothing is installed or changed.
FORMAT = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "processing_mode": "offline_reference_boundary_probe",
    "installed_v0_geometry_preserved": True,
}
SAMPLE_RATE = FORMAT["sample_rate_hz"]
FRAME = FORMAT["frame_samples"]
MAX_ABS_INPUT = 2.0
VALID_MODES = (2, 3)  # processing_thread and buffered_worker; no inline callback
CONFIGURATION_KEYS = ("model",)
CONFIGURATION = {"model": "fastenhancer_medium_pinned"}

# Pinned identities from the merged Pro evidence. source: paths are
# workspace-relative; worktree: paths are SDK-worktree-relative. The mutable
# full plan/swarm/TASKS.json is deliberately absent from every pin.
SOURCE_PINS: Dict[str, str] = {
    "source:cpp-library/src/stages/fastenhancer_native.cpp":
        "75d50ad23d299a3d05b52bbe39a820521608b750e32015307115a3df7ada1326",
    "source:cpp-library/src/stages/fastenhancer.cpp":
        "b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510",
    "source:cpp-library/PIPELINE_DESIGN_REPORT.md":
        "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
    "source:REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/README.md":
        "e2752bb6b06231b10ec1adc46df84e9d70b93011a0c6c9ec409bdd5e628f9aef",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/upstream/manifest.sha256":
        "b1422bdbfc3de24e51ce5bf46a6828ac116aaa6ee897c668020f144948b7f238",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/upstream/LICENSE":
        "3cde746d8400ec5633b865a754db86d44b3fb9838314065148a07c12192a44a5",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/upstream/NOTICE":
        "e202a703551b38724917ff2e9de692dc7bd8fec5c76756450811af6d6b42a467",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/tests/legacy.freeze.json":
        "cdde3ca7341893f8066b546af820331e4b579b3e17fa8a0d4029ffd2c6d78448",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/tests/legacy-snapshot/manifest.sha256":
        "49ab91e0b6ed23c13a0fb5a00d79a50fb2dc9c8baa5e98550f82edf381f51c9c",
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/config.schema.json":
        "e92dac8d17133d9b0441b600af24a4e0074a6ebbac4f80cf88575f513a7d2b8f",
    "source:audio-benchmark-platform/audio-pro/docs/task-evidence/PRO-FASTENHANCER-MEDIUM-NATIVE-SIMD.md":
        "03b6cb6f010f42aa43bd0e0d336cc15811933981fc2cd11a065816598d320f08",
    "source:audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "source:audio-benchmark-platform/plan/swarm/handoffs/PRO-FASTENHANCER-MEDIUM-NATIVE-SIMD.md":
        "90b55394089ce89736b79d17fe245728a0b641056dbe05fc6bb1eb9480d5e2c3",
    "source:audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "source:research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "source:research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}
BOUNDARY_PINS: Dict[str, str] = {
    "worktree:CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "worktree:api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "worktree:api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "worktree:REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "worktree:LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}
PIN_RE = re.compile(
    r"^[0-9a-f]{64}  (?P<path>source:[^\s]+|worktree:[^\s]+|"
    r"docs/task-evidence/fastenhancer-medium-reference/[^\s]+)$"
)

LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
EXPECTED_LINK = {
    "task_id": TASK,
    "title": TITLE,
    "mode": "feasibility",
    "repository": REPOSITORY,
    "component": COMPONENT,
}
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

# Exact artifact identity recorded by the merged Pro evidence. The bytes are
# private and are neither read, copied, embedded nor redistributed here.
ASSET = {
    "asset_id": "fe.q8",
    "byte_count": 565108,
    "sha256": "d6f98e186bee6ed655b52a2edf5f707ccf761c755bb69de8de7f68cad42d7837",
    "git_blob": "ab6f8c711d3e23ace911c5e1e11203fadd43ca19",
    "source_revision": "3e2446fc58886fc02b099b54651adc9a10a65454",
    "storage": "private audio-pro evaluation asset",
    "present_in_sdk_worktree": False,
    "present_in_private_workspace_storage": True,
    "bytes_read_by_this_package": False,
    "download_attempted": False,
    "redistribution": "unknown",
    "evaluation": "unknown",
}
UPSTREAM_MANIFEST_SHA256 = SOURCE_PINS[
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/upstream/manifest.sha256"
]
ORACLE_SHA256 = SOURCE_PINS[
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/tests/legacy.freeze.json"
]
CONFIG_SCHEMA_SHA256 = SOURCE_PINS[
    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/config.schema.json"
]

TASK_GEOMETRY = {
    "sdk_v0": {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "hop_samples": 160,
        "frame_ms": 10.0,
    },
    "native": {
        "sample_rate_hz": 48000,
        "channels": 1,
        "analysis_chunk_samples": 480,
        "native_hop_samples": 320,
        "frame_ms": 10.0,
    },
    "delay": {
        "sdk_declared_samples": 235,
        "native_samples": 704,
        "conformance_tolerance_samples": 1,
        "note": "235 is the nearest SDK-domain integer to 704/3; not measured here.",
    },
    "execution_modes": [2, 3],
    "callback_safe": False,
    "max_drain_calls": 3,
    "cpu_admission": (
        "fe_qgemm_init() required; ARM NEON or x86 AVX2+FMA3+F16C minimum; "
        "no scalar runtime tier"
    ),
    "container": [
        "pro.fastenhancer.medium.native_simd.v0",
        "audio_pro_fastenhancer_medium_simd_tool_*",
    ],
    "note": (
        "Geometry is transcribed from the pinned Pro descriptor and evidence; "
        "no session, tool or native call is created here."
    ),
}


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _reject_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json_constant:" + token)


def strict_json_loads(text: str) -> Any:
    return json.loads(
        text,
        object_pairs_hook=_reject_pairs,
        parse_constant=_reject_constant,
    )


def strict_json(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        return WORKSPACE / raw.split(":", 1)[1]
    if raw.startswith("worktree:"):
        return SDK_ROOT / raw.split(":", 1)[1]
    return SDK_ROOT / raw


def _inside(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Fail closed on malformed, duplicated, traversing or out-of-scope pins."""
    pins: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + repr(line))
        raw_path = match.group("path")
        relative = raw_path.split(":", 1)[-1]
        if ".." in Path(relative).parts:
            raise ValueError("path_traversal_pin:" + raw_path)
        if raw_path in seen:
            raise ValueError("duplicate_pin:" + raw_path)
        seen.add(raw_path)
        target = pin_path(raw_path)
        root = WORKSPACE if raw_path.startswith("source:") else SDK_ROOT
        if not _inside(root, target):
            raise ValueError("out_of_scope_pin:" + raw_path)
        pins.append((line[:64], raw_path))
    return pins


def artifact_pins(names: Sequence[str] = STATIC_ARTIFACTS) -> Dict[str, str]:
    return {f"{TASK_PREFIX}/{name}": sha256((HERE / name).read_bytes()) for name in names}


def sources_bytes() -> bytes:
    """Deterministic manifest; SOURCES.sha256 itself is excluded."""
    pins: Dict[str, str] = dict(SOURCE_PINS)
    pins.update(BOUNDARY_PINS)
    for name in EXPECTED_FILES:
        if name == "SOURCES.sha256":
            continue
        pins[f"{TASK_PREFIX}/{name}"] = sha256((HERE / name).read_bytes())
    lines = [f"{digest}  {path}" for path, digest in sorted(pins.items())]
    header = (
        f"# SHA-256 pins for {TASK}; source: paths are workspace-relative, "
        "worktree: and plain paths are SDK-worktree-relative.\n"
        "# The mutable full plan/swarm/TASKS.json is deliberately not pinned; "
        "only the stable linked-row identity is projected.\n"
        "# No weight, model, runtime or real-corpus artifact is included or "
        "pinned as package content.\n"
    )
    return (header + "\n".join(lines) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# Stable linked-row identity (never the mutable full board)
# ---------------------------------------------------------------------------

def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ValueError("task board is missing")
    board = strict_json(BOARD_PATH)
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ValueError("task board shape is invalid")
    row = None
    for candidate in board["tasks"]:
        if isinstance(candidate, dict) and candidate.get("id") == TASK:
            row = candidate
            break
    if row is None:
        raise ValueError("linked task row is missing")
    stable = {
        "task_id": row.get("id"),
        "title": row.get("title"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "component": row.get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ValueError("stable linked-row identity changed")
    return [stable], sha256(canonical_bytes([stable]))


# ---------------------------------------------------------------------------
# Deterministic harness stimuli and identity control
# ---------------------------------------------------------------------------

def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _stimulus(name: str) -> List[float]:
    if name == "silence":
        return [0.0] * 1600
    if name == "impulse":
        values = [0.0] * 1600
        values[80] = 0.5
        return values
    if name == "step":
        return [0.0] * 800 + [0.25] * 800
    if name == "tone_noise":
        noise = _lcg(20261126)
        values = []
        for index in range(3200):
            tone = (
                0.28 * math.sin(2.0 * math.pi * 220.0 * index / 16000.0)
                + 0.12 * math.sin(2.0 * math.pi * 880.0 * index / 16000.0)
            )
            values.append(tone + (next(noise) - 0.5) * 0.04)
        return values
    if name == "sweep":
        values = []
        for index in range(1600):
            fraction = index / 1600.0
            phase = 2.0 * math.pi * (200.0 * fraction + 3000.0 * fraction * fraction / 2.0) * index / 16000.0
            values.append(0.3 * math.sin(phase))
        return values
    raise ValueError("unknown stimulus:" + name)


STIMULUS_NAMES = ("impulse", "silence", "step", "tone_noise", "sweep")


def _float_digest(values: Iterable[float]) -> str:
    items = list(values)
    return sha256(struct.pack("<%dd" % len(items), *items))


def stimuli() -> Dict[str, Any]:
    records: Dict[str, Any] = {}
    for name in STIMULUS_NAMES:
        values = _stimulus(name)
        square_sum = math.fsum(value * value for value in values)
        records[name] = {
            "sample_count": len(values),
            "digest": _float_digest(values),
            "peak_abs": round(max(abs(value) for value in values), 9),
            "rms": round(math.sqrt(square_sum / len(values)), 9),
            "nonfinite_count": sum(1 for value in values if not math.isfinite(value)),
        }
    return records


class HarnessController:
    """Fail-closed identity harness; not a candidate or model controller."""

    def __init__(self, mode: int = 2) -> None:
        self.mode = mode
        self.epoch = 1
        self.next_position = 0
        self.finished = False
        self.closed = False
        self.state_digest = self._state()

    def _state(self) -> str:
        return sha256(canonical_bytes({
            "mode": self.mode,
            "epoch": self.epoch,
            "next_position": self.next_position,
            "finished": self.finished,
            "closed": self.closed,
        }))

    def _reject(self, status: str) -> Dict[str, Any]:
        return {"status": status, "samples": None, "state_digest": self.state_digest}

    def process(self, frame: Any, epoch: int, first_sample: int) -> Dict[str, Any]:
        if self.closed or self.finished:
            return self._reject("rejected_lifecycle")
        if not isinstance(frame, (list, tuple)) or len(frame) != FRAME:
            return self._reject("rejected_tensor")
        if any(isinstance(value, bool) for value in frame):
            return self._reject("rejected_invalid_sample")
        if any(not isinstance(value, (int, float)) for value in frame):
            return self._reject("rejected_invalid_sample")
        if any(not math.isfinite(value) for value in frame):
            return self._reject("rejected_nonfinite")
        if any(abs(value) > MAX_ABS_INPUT for value in frame):
            return self._reject("rejected_out_of_range")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch != self.epoch:
            return self._reject("rejected_epoch")
        if (isinstance(first_sample, bool) or not isinstance(first_sample, int)
                or first_sample != self.next_position):
            return self._reject("rejected_position")
        output = [float(value) for value in frame]
        self.next_position += FRAME
        self.state_digest = self._state()
        return {"status": "ok", "samples": output, "state_digest": self.state_digest}

    def finish(self) -> str:
        if self.closed or self.finished:
            return "rejected_lifecycle"
        self.finished = True
        self.state_digest = self._state()
        return "ok"

    def close(self) -> None:
        self.closed = True
        self.state_digest = self._state()

    def reset(self, epoch: int, first_sample: int) -> str:
        if self.closed:
            return "rejected_lifecycle"
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch <= self.epoch:
            return "rejected_epoch"
        if isinstance(first_sample, bool) or not isinstance(first_sample, int) or first_sample < 0:
            return "rejected_position"
        self.epoch = epoch
        self.next_position = first_sample
        self.finished = False
        self.state_digest = self._state()
        return "ok"


def identity_control() -> Dict[str, Any]:
    records: Dict[str, Any] = {}
    for name in STIMULUS_NAMES:
        values = _stimulus(name)
        created = HarnessController(2)
        output: List[float] = []
        status = "ok"
        for start in range(0, len(values), FRAME):
            result = created.process(values[start:start + FRAME], 1, start)
            if result["samples"] is None:
                status = result["status"]
                break
            output.extend(result["samples"])
        if status == "ok":
            status = created.finish()
        records[name] = {
            "status": status,
            "input_digest": _float_digest(values),
            "output_digest": _float_digest(output) if len(output) == len(values) else None,
            "byte_identical": len(output) == len(values) and _float_digest(output) == _float_digest(values),
        }
    return {
        "candidate_processing": False,
        "kind": "identity_harness_control",
        "all_byte_identical": all(item["byte_identical"] for item in records.values()),
        "stimuli": records,
        "note": (
            "The harness only proves deterministic framing and rejection. It is "
            "not FastEnhancer, not a denoiser and not a quality result."
        ),
    }


# ---------------------------------------------------------------------------
# Request and asset admission (fail closed before any processing)
# ---------------------------------------------------------------------------

def _valid_request() -> Dict[str, Any]:
    return {
        "task": TASK,
        "component": COMPONENT,
        "rate_hz": SAMPLE_RATE,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": FRAME,
        "hop_samples": FRAME,
        "mode": 2,
        "epoch": 1,
        "first_sample": 0,
        "samples": [0.0] * FRAME,
    }


def admit_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return {"accepted": False, "error": "INVALID_REQUEST", "samples": None}
    required = set(_valid_request())
    if required - set(request):
        return {"accepted": False, "error": "MISSING_FIELD", "samples": None}
    if set(request) - required:
        return {"accepted": False, "error": "UNKNOWN_FIELD", "samples": None}
    if request["task"] != TASK or request["component"] != COMPONENT:
        return {"accepted": False, "error": "UNKNOWN_TARGET", "samples": None}
    if request["rate_hz"] != SAMPLE_RATE:
        return {"accepted": False, "error": "WRONG_RATE", "samples": None}
    if request["channels"] != 1:
        return {"accepted": False, "error": "WRONG_CHANNELS", "samples": None}
    if request["sample_format"] != "f32":
        return {"accepted": False, "error": "WRONG_FORMAT", "samples": None}
    if request["frame_samples"] != FRAME:
        return {"accepted": False, "error": "WRONG_FRAME", "samples": None}
    if request["hop_samples"] != FRAME:
        return {"accepted": False, "error": "WRONG_HOP", "samples": None}
    if request["mode"] not in VALID_MODES:
        return {"accepted": False, "error": "INVALID_MODE", "samples": None}
    epoch = request["epoch"]
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 1:
        return {"accepted": False, "error": "INVALID_EPOCH", "samples": None}
    position = request["first_sample"]
    if isinstance(position, bool) or not isinstance(position, int) or position < 0:
        return {"accepted": False, "error": "INVALID_POSITION", "samples": None}
    samples = request["samples"]
    if not isinstance(samples, (list, tuple)) or len(samples) != FRAME:
        return {"accepted": False, "error": "WRONG_SAMPLE_COUNT", "samples": None}
    if any(isinstance(value, bool) for value in samples):
        return {"accepted": False, "error": "INVALID_SAMPLE_TYPE", "samples": None}
    if any(not isinstance(value, (int, float)) for value in samples):
        return {"accepted": False, "error": "INVALID_SAMPLE_TYPE", "samples": None}
    if any(not math.isfinite(value) for value in samples):
        return {"accepted": False, "error": "NONFINITE", "samples": None}
    if any(abs(value) > MAX_ABS_INPUT for value in samples):
        return {"accepted": False, "error": "OUT_OF_RANGE", "samples": None}
    return {"accepted": True, "error": None, "samples": [float(value) for value in samples]}


def admission_cases() -> Dict[str, Any]:
    base = _valid_request()

    def variant(**changes: Any) -> Dict[str, Any]:
        value = dict(base)
        value.update(changes)
        return value

    cases: List[Tuple[str, Any, str]] = [
        ("request_not_object", [], "INVALID_REQUEST"),
        ("unknown_field", variant(extra=1), "UNKNOWN_FIELD"),
        ("unknown_target", variant(task="OTHER"), "UNKNOWN_TARGET"),
        ("wrong_rate", variant(rate_hz=48000), "WRONG_RATE"),
        ("wrong_channels", variant(channels=2), "WRONG_CHANNELS"),
        ("wrong_format", variant(sample_format="i16"), "WRONG_FORMAT"),
        ("wrong_frame", variant(frame_samples=480), "WRONG_FRAME"),
        ("wrong_hop", variant(hop_samples=480), "WRONG_HOP"),
        ("invalid_mode", variant(mode=1), "INVALID_MODE"),
        ("negative_epoch", variant(epoch=-1), "INVALID_EPOCH"),
        ("bool_epoch", variant(epoch=True), "INVALID_EPOCH"),
        ("negative_position", variant(first_sample=-1), "INVALID_POSITION"),
        ("short_samples", variant(samples=[0.0] * (FRAME - 1)), "WRONG_SAMPLE_COUNT"),
        ("bool_sample", variant(samples=[True] * FRAME), "INVALID_SAMPLE_TYPE"),
        ("string_sample", variant(samples=["0.0"] * FRAME), "INVALID_SAMPLE_TYPE"),
        ("nonfinite_nan", variant(samples=[float("nan")] * FRAME), "NONFINITE"),
        ("nonfinite_inf", variant(samples=[float("inf")] * FRAME), "NONFINITE"),
        ("out_of_range", variant(samples=[MAX_ABS_INPUT + 1.0] * FRAME), "OUT_OF_RANGE"),
    ]
    missing = dict(base)
    missing.pop("mode")
    cases.append(("missing_field", missing, "MISSING_FIELD"))

    results = []
    for case_id, request, expected in cases:
        outcome = admit_request(request)
        results.append({
            "id": case_id,
            "accepted": outcome["accepted"],
            "error": outcome["error"],
            "expected": expected,
            "matches": outcome["accepted"] is False and outcome["error"] == expected,
        })
    return {
        "case_count": len(results),
        "accepted_count": sum(1 for item in results if item["accepted"]),
        "all_rejected": all(item["matches"] for item in results),
        "cases": results,
        "metrics": None,
        "note": "Invalid requests are rejected before any controller exists; no metrics exist.",
    }


def admission_json_cases() -> Dict[str, Any]:
    payloads = [
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1}{"b":2}'),
        ("invalid_syntax", '{"a":}'),
    ]
    results = []
    for case_id, payload in payloads:
        try:
            strict_json_loads(payload)
            accepted = True
            error = None
        except ValueError as failure:
            accepted = False
            error = str(failure).split(":", 1)[0]
        results.append({
            "id": case_id,
            "accepted": accepted,
            "error": error,
            "matches": accepted is False,
        })
    return {
        "case_count": len(results),
        "accepted_count": sum(1 for item in results if item["accepted"]),
        "all_rejected": all(item["matches"] for item in results),
        "cases": results,
        "metrics": None,
    }


def lifecycle_cases() -> Dict[str, Any]:
    valid_frame = [0.0] * FRAME
    closed = HarnessController(2)
    closed.close()
    finished = HarnessController(2)
    finished.finish()
    resetter = HarnessController(2)
    stale_epoch = resetter.reset(1, 0)
    stale_position = resetter.reset(2, -1)
    valid_reset = resetter.reset(3, 0)
    return {
        "closed_process": closed.process(valid_frame, 1, 0)["status"],
        "finished_process": finished.process(valid_frame, 1, 0)["status"],
        "stale_reset_epoch": stale_epoch,
        "stale_reset_position": stale_position,
        "valid_reset": valid_reset,
        "invalid_never_advances_state": (
            closed.state_digest == closed._state()
            and finished.state_digest == finished._state()
        ),
    }


def admit_asset(payload: Any, spec: Optional[Mapping[str, Any]] = None) -> str:
    expected = dict(ASSET if spec is None else spec)
    if payload is None:
        return "ASSET_MISSING"
    if not isinstance(payload, (bytes, bytearray)):
        return "ASSET_INVALID"
    if len(payload) != expected["byte_count"]:
        return "ASSET_SIZE_MISMATCH"
    if sha256(bytes(payload)) != expected["sha256"]:
        return "ASSET_DIGEST_MISMATCH"
    return "ASSET_ADMITTED"


def asset_admission() -> Dict[str, Any]:
    cases = {
        "missing": admit_asset(None),
        "invalid_type": admit_asset("fe.q8"),
        "empty": admit_asset(b""),
        "wrong_size": admit_asset(b"\x00" * (ASSET["byte_count"] + 1)),
        "wrong_digest": admit_asset(b"\x00" * ASSET["byte_count"]),
    }
    return {
        "status": "blocked",
        "asset_bytes_read": False,
        "asset_bytes_present_in_package": False,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "rejection_cases": cases,
        "all_rejections_fail_closed": all(
            value.startswith("ASSET_") and value != "ASSET_ADMITTED"
            for value in cases.values()
        ),
        "admission_mechanism_verified_with_synthetic_spec": (
            admit_asset(b"abcd", {"byte_count": 4, "sha256": sha256(b"abcd")})
            == "ASSET_ADMITTED"
        ),
        "note": (
            "The exact 565108-byte fe.q8 asset is not read or admitted here. "
            "Only the mechanism is exercised; exact bytes stay in private storage."
        ),
    }


def probe_sdk_worktree_asset() -> Dict[str, Any]:
    candidates = [
        SDK_ROOT / "fe.q8",
        SDK_ROOT / "third_party/fe.q8",
        SDK_ROOT / "third_party/fastenhancer/fe.q8",
        SDK_ROOT / "models/fe.q8",
        HERE / "fe.q8",
    ]
    found = [str(path.relative_to(SDK_ROOT)) for path in candidates if path.is_file()]
    return {
        "checked_paths": [str(path.relative_to(SDK_ROOT)) for path in candidates],
        "found": found,
        "present": bool(found),
        "note": "Read-only path checks; no asset byte is opened, copied or downloaded.",
    }


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def boundary() -> Dict[str, Any]:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_change": False,
        "provider_registration": False,
        "processor_exposure": False,
        "c_public_boundary": False,
        "installed_v0_geometry_preserved": True,
        "installed_v0_behavior_changed": False,
        "descriptor_or_registry_change": False,
        "shared_build_or_ci_change": False,
        "task_board_or_handoff_change": False,
        "real_corpus_or_weights_included": False,
        "evaluation_path": "task_local_deterministic_probe",
        "production_callback_path": "not_implemented",
    }


def runtime_record() -> Dict[str, Any]:
    return {
        "status": "absent_for_sdk_reference",
        "present_in_sdk_worktree": False,
        "sdk_consumable_runtime_present": False,
        "onnx_medium_model_present": False,
        "native_simd_backend_present_in_sdk_worktree": False,
        "scalar_runtime_tier_available": False,
        "vendor_runtime_invoked": False,
        "required_backend": TASK_GEOMETRY["cpu_admission"],
        "recorded_by": "audio-pro/processors/fastenhancer_medium_native_simd/README.md",
        "recorded_sha256": SOURCE_PINS[
            "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/README.md"
        ],
        "reason": (
            "The only exact runtime is the pinned native faster-enhancer.c SIMD "
            "backend with mandatory fe_qgemm_init() admission and no scalar tier. "
            "It is absent from this SDK worktree, not buildable by a stdlib-only "
            "deterministic package, and no SDK-consumable ONNX/medium model exists."
        ),
    }


def feasibility() -> Dict[str, Any]:
    return {
        "verdict": "blocked",
        "decision": DECISION,
        "can_produce_exact_sdk_reference": False,
        "conjuncts": {
            "source_present": True,
            "source_pinned": True,
            "weights_present_in_private_storage": True,
            "weights_pinned": True,
            "weights_redistribution_cleared": False,
            "runtime_present_for_sdk": False,
            "runtime_pinned_for_sdk": False,
            "rights_cleared_for_redistribution": False,
        },
        "reason_codes": [
            "weights_private_redistribution_unknown",
            "sdk_consumable_runtime_absent",
            "native_simd_only_no_scalar_tier",
            "exact_parity_oracle_not_reproducible_here",
            "rights_register_medium48_unknown",
        ],
        "note": (
            "The conjunction required for a pinned SDK reference fails: the "
            "exact source and weights are identified, but the runtime is absent "
            "and redistribution rights are unrecorded. Implementing a stand-in "
            "model would fabricate a result, so the task defers."
        ),
    }


def reference_record() -> Dict[str, Any]:
    return {
        "kind": "task_local_deterministic_evidence_builder",
        "deterministic": True,
        "model_weights": False,
        "real_model_inference": False,
        "upstream_parity": False,
        "synthetic_only": True,
        "downloads": False,
        "runtime_invoked": False,
        "candidate_output_produced": False,
        "note": (
            "No FastEnhancer Medium network, weight loader, SIMD kernel or "
            "inference path is implemented, approximated or simulated. Only "
            "identity framing, admission rejection and determinism are exercised."
        ),
    }


def candidates() -> Dict[str, Any]:
    return {
        "fastenhancer_medium": {
            "status": "blocked_assets_and_runtime_absent",
            "metrics": None,
            "si_sdr_db": None,
            "stoi": None,
            "qualifies_candidate": False,
            "candidate_output": False,
            "reason": (
                "No exact runtime is present in the SDK worktree, the private "
                "weights are not cleared for redistribution, and no candidate "
                "output or reference parity exists. Missing evidence never qualifies."
            ),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "identity_harness_control": {
            "candidate_processing": False,
            "status": "bit_exact_synthetic_only",
            "metrics": None,
        },
        "named_noisy_input_baseline": {
            "name": "noisy_input_no_processing",
            "candidate_processing": False,
            "status": "source_reported_only_not_scored",
            "metrics": None,
        },
        "clean_speech_preservation": {
            "candidate_processing": False,
            "status": "blocked_no_candidate_output",
            "metrics": None,
        },
        "note": (
            "A harness identity control is not a denoising result. No paired "
            "quality metric, listening score or baseline comparison is reported."
        ),
    }


def missing_result() -> Dict[str, Any]:
    return {
        "status": "blocked",
        "reason": "weights_private_and_sdk_runtime_absent",
        "fixture": "fastenhancer_medium_identity_probe",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def repeatability() -> Dict[str, Any]:
    digests = []
    for _ in range(3):
        digests.append(sha256(canonical_bytes(identity_control())))
    return {
        "count": 3,
        "digests": digests,
        "byte_identical": len(set(digests)) == 1,
        "note": (
            "Three fresh in-process builders over the pinned synthetic stimuli; "
            "no tolerance, substitution or cached output is used."
        ),
    }


def acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS["source:audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "mapped_cases": {
            "identity_noisy_control": {
                "status": "harness_identity_only",
                "evidence": ["controls.identity_harness_control", "harness.identity_control"],
                "candidate_scored": False,
            },
            "established_task_matched_baseline": {
                "status": "source_reported_only_not_run",
                "evidence": ["controls.named_noisy_input_baseline"],
                "candidate_scored": False,
            },
            "paired_si_sdr_stoi": {
                "status": "blocked_no_candidate_output",
                "evidence": [],
                "candidate_scored": False,
                "note": "No candidate output exists to score; no surrogate score is reported.",
            },
            "clean_speech_preservation": {
                "status": "blocked_no_candidate_output",
                "evidence": [],
                "candidate_scored": False,
            },
            "peaks_and_invalid_outputs": {
                "status": "admission_rejections_only",
                "evidence": ["adverse.invalid_requests", "adverse.invalid_json"],
                "candidate_scored": False,
            },
            "unpaired_speech": {
                "status": "not_applicable",
                "reason": "No licensed unpaired speech, predictive screen or authorized listening was run.",
            },
            "alignment_state_memory_timing": {
                "status": "documented_boundary_only",
                "alignment": "SDK delay 235 samples and native 704 samples are transcribed, not measured.",
                "state": "Harness admission and lifecycle rejection are recorded.",
                "memory": "No installed or target-device memory result exists.",
                "timing": "No content/availability timing, pacing or deadline measurement exists.",
            },
        },
        "not_reported": [
            "candidate SI-SDR or STOI",
            "human listening or MOS",
            "target-device pacing or deadline",
            "installed runtime memory",
            "real model inference",
            "release qualification",
        ],
    }


def required_results() -> Dict[str, str]:
    return {
        "identity_noisy_control": "harness_identity_only",
        "established_task_matched_baseline": "source_reported_only_not_run",
        "paired_si_sdr_stoi": "blocked_no_candidate_output",
        "clean_speech_preservation": "blocked_no_candidate_output",
        "peaks_and_invalid_outputs": "admission_rejections_only",
        "unpaired_speech": "not_applicable",
        "alignment_first_output_and_delay": "documented_not_measured",
        "state_reset_drain_and_modes": "documented_not_exercised",
        "target_runtime_timing_memory_deadline": "blocked",
        "provider_intake_and_public_surface": "blocked",
    }


def gates() -> List[Dict[str, str]]:
    return [
        {
            "id": "RG-01",
            "name": "exact_source_and_weight_identity",
            "status": "blocked",
            "evidence": (
                "Source and fe.q8 identities are pinned from merged Pro evidence, "
                "but the weights exist only as a private audio-pro evaluation asset."
            ),
            "reopen": (
                "Record an immutable source revision and the exact fe.q8 byte "
                "count/SHA-256 in a caller-owned retrieval record."
            ),
        },
        {
            "id": "RG-02",
            "name": "rights_and_redistribution_clearance",
            "status": "blocked",
            "evidence": (
                "audio-pro/docs/rights-register.md records FastEnhancer Medium48 "
                "q8 evaluation and redistribution as unknown; the Pro handoff grant "
                "covers private evaluation only and excludes public redistribution."
            ),
            "reopen": (
                "Record written weight, derived-asset and runtime terms plus an "
                "approved redistribution and product-use scope."
            ),
        },
        {
            "id": "RG-03",
            "name": "sdk_consumable_runtime_and_toolchain",
            "status": "blocked",
            "evidence": (
                "The exact backend is native SIMD faster-enhancer.c with mandatory "
                "fe_qgemm_init() admission and no scalar tier; it is absent from "
                "this SDK worktree and no SDK-consumable model runtime exists."
            ),
            "reopen": (
                "Provide a pinned, hash-verified runtime that builds and runs in the "
                "intended SDK environment, with documented CPU admission and no scalar fallback."
            ),
        },
        {
            "id": "RG-04",
            "name": "exact_reference_parity_oracle",
            "status": "blocked",
            "evidence": (
                "The 104-key frozen oracle is pinned (cdde3ca7...), but it was not "
                "regenerated or compared here; no exact output vector exists."
            ),
            "reopen": (
                "Regenerate the pinned oracle from hash-verified blobs with three "
                "byte-identical passes and compare exact candidate output without tolerance widening."
            ),
        },
        {
            "id": "RG-05",
            "name": "rights_cleared_paired_cohort",
            "status": "blocked",
            "evidence": "No rights-cleared real paired cohort with clean references is available.",
            "reopen": (
                "Freeze a permitted held-out paired cohort and paired SI-SDR/STOI "
                "protocol with matched identity and noisy controls."
            ),
        },
        {
            "id": "RG-06",
            "name": "independent_listening_or_screen",
            "status": "blocked",
            "evidence": "No independent listening or separately labeled predictive screen was run.",
            "reopen": (
                "Run authorized listening or an independently labeled predictive "
                "screen without presenting it as a measured model result."
            ),
        },
        {
            "id": "RG-07",
            "name": "target_runtime_timing_memory_and_deadline",
            "status": "blocked",
            "evidence": (
                "Declared delay and drain bounds are transcribed only; no target "
                "content/availability timing, memory, pacing or deadline was measured."
            ),
            "reopen": (
                "Measure content delay, availability, memory, drain and deadline on "
                "the exact admitted target runtime independently of compute speed."
            ),
        },
        {
            "id": "RG-08",
            "name": "provider_intake_public_surface_release_review",
            "status": "blocked",
            "evidence": (
                "No provider intake, descriptor/catalog entry, default decision, "
                "independent exact-head review or release approval exists."
            ),
            "reopen": (
                "Complete provider intake and an explicit default decision, then "
                "obtain independent exact-head review and release approval."
            ),
        },
    ]


def independent_timing_evidence() -> Dict[str, Any]:
    return {
        "status": "source_reported_proposal_only",
        "measured_here": False,
        "target_device": False,
        "used_for_qualification": False,
        "sources": [
            {
                "path": "audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/README.md",
                "sha256": SOURCE_PINS[
                    "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/README.md"
                ],
                "statement": (
                    "Declared SDK delay 235 samples, native delay 704 samples at "
                    "48 kHz, native hop 320 and a one-call drain within a bound of 3."
                ),
            },
            {
                "path": "audio-benchmark-platform/audio-pro/docs/task-evidence/PRO-FASTENHANCER-MEDIUM-NATIVE-SIMD.md",
                "sha256": SOURCE_PINS[
                    "source:audio-benchmark-platform/audio-pro/docs/task-evidence/PRO-FASTENHANCER-MEDIUM-NATIVE-SIMD.md"
                ],
                "statement": (
                    "This host resolved tier=20 path=dotprod; the evidence makes no "
                    "quality, pacing, device or release claim."
                ),
            },
            {
                "path": "REALTIME_COMPONENT_CANDIDATES.md",
                "sha256": SOURCE_PINS["source:REALTIME_COMPONENT_CANDIDATES.md"],
                "statement": (
                    "Preset Tiny/Small RTF values are cross-model provenance, not a "
                    "Medium measurement and not a controlled hardware comparison."
                ),
            },
        ],
        "note": (
            "Provenance only. These values are not reproduced, pooled, treated as "
            "a controlled benchmark, assigned to this task or used as a threshold."
        ),
    }


def rights_gap() -> Dict[str, Any]:
    return {
        "blocked": True,
        "exact_source_present": True,
        "exact_source_pinned": True,
        "model_weight_terms_verified": False,
        "redistribution_cleared": False,
        "public_packaging_permitted": False,
        "evaluation_permission_recorded": True,
        "evaluation_scope": "private pinned-asset evaluation only",
        "rights_register_pin": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
        "rights_register_sha256": SOURCE_PINS[
            "source:audio-benchmark-platform/audio-pro/docs/rights-register.md"
        ],
        "rights_register_statement": (
            "FastEnhancer Medium48 q8 weights: acquisition unknown, evaluation "
            "unknown, redistribution unknown, customer deployment unknown, public playback unknown."
        ),
        "pro_handoff_pin": "audio-benchmark-platform/plan/swarm/handoffs/PRO-FASTENHANCER-MEDIUM-NATIVE-SIMD.md",
        "pro_handoff_sha256": SOURCE_PINS[
            "source:audio-benchmark-platform/plan/swarm/handoffs/PRO-FASTENHANCER-MEDIUM-NATIVE-SIMD.md"
        ],
        "pro_handoff_statement": (
            "User confirmed required rights for private evaluation; model bytes, "
            "derived assets, audio and build output remain private and no public "
            "redistribution, deployment or playback claim is implied."
        ),
        "consequence": (
            "No weight, derived asset, native source, installed provider, registry "
            "entry, packaged artifact or release claim is permitted until exact "
            "redistribution terms are recorded."
        ),
    }


def missing_evidence() -> List[str]:
    return [
        "exact fe.q8 bytes admitted from caller storage in this SDK worktree",
        "pinned SDK-consumable FastEnhancer Medium runtime and toolchain",
        "written weight, derived-asset and runtime redistribution terms",
        "regenerated exact reference parity vectors for the frozen inputs",
        "rights-cleared paired real cohort with clean references",
        "independent listening or separately labeled predictive screen",
        "target-runtime content/availability timing, memory and deadline evidence",
        "provider intake, descriptor/catalog review and explicit default decision",
    ]


def negative_claims() -> Dict[str, bool]:
    return {
        "real_model_weights": False,
        "real_media": False,
        "real_model_inference": False,
        "device_timing": False,
        "listening_result": False,
        "quality_metric": False,
        "benchmark_claim": False,
        "release_claim": False,
        "provider_registration": False,
        "public_default_selection": False,
        "vendor_runtime_invoked": False,
        "download_attempted": False,
    }


def non_claims() -> List[str]:
    return [
        "No FastEnhancer Medium weight, model, runtime or real corpus is included.",
        "No FastEnhancer Medium inference is implemented, approximated or simulated.",
        "No SI-SDR, STOI, MOS or listening result is reported.",
        "No installed v0, public API, C ABI, descriptor, registry or default change.",
        "No provider is registered or enabled by default.",
        "No device timing, memory, callback, benchmark or release claim is made.",
        "No missing, rejected, source-reported or synthetic result qualifies the candidate.",
    ]


def qualification() -> Dict[str, Any]:
    return {
        "status": QUALIFICATION_STATUS,
        "qualifies": False,
        "qualifies_candidate": False,
        "proposal_only": True,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "real_runtime_used": False,
        "candidate_output": False,
        "processor_exposure": False,
        "missing_result_promoted": False,
        "all_required_results_present": False,
    }


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    return {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "reference_family": REFERENCE_FAMILY,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": (
            "Task-local feasibility evidence for a FastEnhancer Medium SDK "
            "reference. Exact source/weight identities are pinned from merged Pro "
            "evidence; no model, weight, runtime or real media is used. The task "
            "defers with an explicit artifact and rights blocker."
        ),
        "deliverable": (
            "Verify runnable source, exact assets, permitted scope, task geometry "
            "and matched evidence; record a concrete blocker because the exact "
            "SDK-consumable runtime and redistribution rights are absent."
        ),
        "qualification": qualification(),
        "boundary": boundary(),
        "format": FORMAT,
        "task_geometry": TASK_GEOMETRY,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(REPORT_ARTIFACTS),
        "board_link_fields": list(LINK_FIELDS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "acceptance_profile": acceptance_profile(),
        "required_results": required_results(),
        "asset": dict(ASSET),
        "asset_identity": {
            "upstream_manifest_sha256": UPSTREAM_MANIFEST_SHA256,
            "frozen_oracle_sha256": ORACLE_SHA256,
            "configuration_schema_sha256": CONFIG_SCHEMA_SHA256,
            "upstream_license": "MIT",
            "upstream_license_pin": SOURCE_PINS[
                "source:audio-benchmark-platform/audio-pro/processors/fastenhancer_medium_native_simd/upstream/LICENSE"
            ],
        },
        "asset_admission": asset_admission(),
        "sdk_worktree_asset_probe": probe_sdk_worktree_asset(),
        "runtime": runtime_record(),
        "feasibility": feasibility(),
        "reference": reference_record(),
        "candidates": candidates(),
        "controls": controls(),
        "harness": {
            "stimuli": stimuli(),
            "identity_control": identity_control(),
        },
        "adverse": {
            "invalid_requests": admission_cases(),
            "invalid_json": admission_json_cases(),
            "lifecycle": lifecycle_cases(),
        },
        "missing_result": missing_result(),
        "repeatability": repeatability(),
        "regressions": [],
        "gates": gates(),
        "remaining_gates": [gate["id"] for gate in gates()],
        "independent_timing_evidence": independent_timing_evidence(),
        "rights_gap": rights_gap(),
        "missing_evidence": missing_evidence(),
        "non_claims": non_claims(),
        "negative_claims": negative_claims(),
        "evidence_classes": [
            "pinned_source_review",
            "asset_identity_record",
            "runtime_absence_probe",
            "rights_blocker",
            "deterministic_admission_fixture",
            "proposal_only",
        ],
    }


def _blockers() -> List[str]:
    return [
        (
            "The exact fe.q8 asset is 565108 bytes with SHA-256 "
            "d6f98e186bee6ed655b52a2edf5f707ccf761c755bb69de8de7f68cad42d7837 "
            "(git blob ab6f8c71...), but it is absent from this SDK worktree and "
            "exists only as a private audio-pro evaluation asset."
        ),
        (
            "audio-pro/docs/rights-register.md records FastEnhancer Medium48 q8 "
            "evaluation and redistribution as unknown, so the SDK cannot package, "
            "vendor or redistribute the weights or a derived asset."
        ),
        (
            "The exact runtime is the native faster-enhancer.c SIMD backend with "
            "mandatory fe_qgemm_init() admission, ARM NEON or x86 AVX2+FMA3+F16C "
            "and no scalar tier; it is not present in the SDK worktree and no "
            "SDK-consumable ONNX or pure-Python Medium runtime exists."
        ),
        (
            "The 104-key frozen oracle (cdde3ca7...) cannot be regenerated here "
            "without that runtime, and no exact candidate output or reference "
            "parity vector exists."
        ),
        (
            "No rights-cleared paired cohort, independent listening, target "
            "timing/memory/deadline measurement, provider intake or release review exists."
        ),
    ]


def build_contract() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "reference_family": REFERENCE_FAMILY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": qualification(),
        "verification_profile": PROFILE,
        "scope": (
            "Feasibility and pinned-identity evidence only; no model, weight, "
            "runtime, public surface, registry, default, board or handoff change."
        ),
        "boundary": boundary(),
        "public_surface": {
            "api_or_abi_change": False,
            "c_public_boundary": False,
            "default_selection": False,
            "descriptor_or_registry_change": False,
            "installed_v0_geometry_change": False,
            "provider_registration": False,
            "shared_build_or_ci_change": False,
            "task_board_or_handoff_change": False,
        },
        "frontend_contract": {
            "identity": "audio-sdk/v0-f32-16k-mono-160",
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "hop_samples": 160,
            "content_delay_samples": 0,
            "public_api_abi_changed": False,
            "installed_v0_behavior_changed": False,
            "provider_registration": False,
            "enabled_by_default": False,
            "default_selected": False,
            "descriptor_settings": {},
        },
        "format": FORMAT,
        "task_geometry": TASK_GEOMETRY,
        "asset": dict(ASSET),
        "asset_identity": {
            "upstream_manifest_sha256": UPSTREAM_MANIFEST_SHA256,
            "frozen_oracle_sha256": ORACLE_SHA256,
            "configuration_schema_sha256": CONFIG_SCHEMA_SHA256,
        },
        "runtime": runtime_record(),
        "feasibility": feasibility(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(STATIC_ARTIFACTS),
        "board_link_fields": list(LINK_FIELDS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "acceptance_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md"
            ],
            "mapped_cases": [
                "identity and harness control",
                "established task-matched baseline",
                "paired SI-SDR and STOI",
                "clean-speech preservation",
                "peaks and invalid outputs",
                "unpaired-speech screen or listening",
                "alignment, state, memory and timing",
            ],
            "not_applicable": [
                "candidate quality metrics: no candidate output exists",
                "listening: no authorized result",
                "target timing/memory: no exact runtime measurement",
            ],
        },
        "gates": [gate["id"] for gate in gates()],
        "rights_gap": rights_gap(),
        "exact_blockers": _blockers(),
        "reopening_conditions": [
            "Admit exact fe.q8 bytes from caller-owned storage with the pinned 565108-byte size and SHA-256.",
            "Record written weight, derived-asset and runtime redistribution terms before packaging.",
            "Provide a pinned SDK-consumable runtime with documented CPU admission and no scalar fallback.",
            "Regenerate the frozen oracle with three byte-identical passes and compare exact output without tolerance widening.",
            "Run a rights-cleared paired cohort and independent listening or authorized screen.",
            "Measure target timing, memory, drain and deadline on the exact admitted runtime.",
            "Complete provider intake, an explicit default decision and independent exact-head release review.",
        ],
        "invariants": [
            "Only this task directory is written; no public header, contract, CMake, registry, default, board, handoff, CI or installed behavior changes.",
            "The mutable full plan/swarm/TASKS.json is never hashed; only the stable linked-row identity is projected.",
            "No model, weight, runtime, real corpus or listening result is included or claimed.",
            "Missing, invalid and nonfinite admissions fail closed without creating a controller.",
            "No synthetic, source-reported or missing result qualifies the candidate.",
        ],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
