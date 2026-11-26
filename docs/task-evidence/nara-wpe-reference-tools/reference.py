# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only feasibility package for SDK-NARA-WPE-REFERENCE-TOOLS.

The upstream NARA-WPE implementation is represented in this workspace only by
two provenance records: the category source register entry
``research/category_survey/sources.md`` (source ``S20``) and the
``research/category_registry.json`` source map. Both record the repository URL
``https://github.com/fgnt/nara_wpe`` and the access scope ``search excerpt``.
They record no immutable revision, package metadata, source file, licence text,
default STFT/taps geometry, runtime or output vector, and no NARA-WPE checkout
exists under any fixed workspace probe.

This module therefore does not import, download, vendor, load or execute
NARA-WPE, NumPy, SciPy or any runtime. It provides four bounded pieces:

* a fail-closed absence audit over fixed workspace probes;
* a strict, caller-supplied tool-manifest contract that validates the metadata
  and hashes a caller would need before NARA-WPE could be admitted, while never
  loading, importing or executing the package;
* an original synthetic *geometry control* that checks the pinned project WPE
  frame grid, early-target window, declared algorithmic latency, config
  matching and fail-closed input rejection. It is not NARA-WPE, performs no
  dereverberation and cannot qualify the candidate; and
* deterministic contract/report/pin/README builders plus the task-local git
  scope comparison.

Disposition: ``DEFER`` / ``incomplete`` / ``not_qualified``. All eight release
gates stay blocked; no missing, absent or adverse result is promoted.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
AUDIO_ROOT = SDK_ROOT.parents[2]

TASK = "SDK-NARA-WPE-REFERENCE-TOOLS"
TITLE = "NARA-WPE reference tools"
SLUG = "nara-wpe-reference-tools"
COMPONENT = SLUG
TASK_PREFIX = "docs/task-evidence/nara-wpe-reference-tools/"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence/nara-wpe-reference-tools/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROTOCOL = "audio-sdk/nara-wpe-reference-tools-evidence/0.1"
CALLER_MANIFEST_SCHEMA_ID = (
    "audio-sdk/nara-wpe-reference-tools/caller-manifest/0.1")
PROFILE = "Room"
MODE = "feasibility"
BASE_COMMIT = "d2eae1246561fe11c5a3d17733ddd46db53e7803"
BRANCH = "swarm/SDK-NARA-WPE-REFERENCE-TOOLS"
OWNER = "agent-NARA-WPE-REFERENCE-TOOLS"
REVIEWER = "reviewer-NARA-WPE-REFERENCE-TOOLS"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-NARA-WPE-REFERENCE-TOOLS"
)
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "exact_source_and_asset_identity"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "float32"
FRAME_SAMPLES = 160
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS

# Project WPE reference geometry, pinned from adapters/wpe/README.md and the
# sibling docs/task-evidence/offline-mono-wpe/report.json.  These are *project*
# defaults; the upstream NARA-WPE defaults are not established anywhere here.
PROJECT_FFT_SIZE = 512
PROJECT_HOP_SIZE = 128
PROJECT_TAPS = 5
PROJECT_PREDICTION_DELAY_FRAMES = 8
PROJECT_ITERATIONS = 3
PROJECT_EARLY_WINDOW_MS = 50
PROJECT_EARLY_WINDOW_SAMPLES = (
    PROJECT_EARLY_WINDOW_MS * SAMPLE_RATE_HZ // 1000)
PROJECT_STFT_LOOKAHEAD_SAMPLES = PROJECT_FFT_SIZE // 2
PROJECT_STFT_LOOKAHEAD_MS = (
    PROJECT_STFT_LOOKAHEAD_SAMPLES * 1000 // SAMPLE_RATE_HZ)
PROJECT_PREDICTOR_DELAY_SAMPLES = (
    PROJECT_PREDICTION_DELAY_FRAMES * PROJECT_HOP_SIZE)
PROJECT_PREDICTOR_DELAY_MS = (
    PROJECT_PREDICTOR_DELAY_SAMPLES * 1000 // SAMPLE_RATE_HZ)
PROJECT_ALGORITHMIC_LATENCY_SAMPLES = (
    PROJECT_STFT_LOOKAHEAD_SAMPLES + PROJECT_PREDICTOR_DELAY_SAMPLES)
PROJECT_ALGORITHMIC_LATENCY_MS = (
    PROJECT_ALGORITHMIC_LATENCY_SAMPLES * 1000 // SAMPLE_RATE_HZ)

CONTROL_SOURCE_SAMPLES = 64037
CONTROL_FINAL_PARTIAL_SAMPLES = CONTROL_SOURCE_SAMPLES % PROJECT_HOP_SIZE

UPSTREAM_NAME = "NARA-WPE"
UPSTREAM_REPOSITORY_URL = "https://github.com/fgnt/nara_wpe"
UPSTREAM_ACCESS_SCOPE = "search excerpt"
UPSTREAM_REVISION: Optional[str] = None
UPSTREAM_LICENSE: Optional[str] = None
UPSTREAM_LICENSE_STATUS = "not_established"
SOURCE_REVISION_PIN_AVAILABLE = False
SOURCE_CHECKOUT_PRESENT = False
UPSTREAM_GEOMETRY_STATUS = "unestablished"
TASK_GEOMETRY_STATUS = "declared_project_geometry_only"
SOURCE_CHECKOUT_PATH = "data/checkouts/nara_wpe"
SOURCE_ADAPTER_PATH = "adapters/nara-wpe"
RUNTIME_ENV_PATH = "data/envs/nara-wpe"

# Source pins are relative to AUDIO_ROOT (the audioml workspace root).
SOURCE_PINS: Dict[str, str] = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/category_survey/search_log.jsonl":
        "61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09",
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "adapters/wpe/README.md":
        "b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

# Boundary pins are relative to SDK_ROOT.  Sibling WPE packages are pinned as
# separate evidence only; their results are never pooled into this package.
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
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    "docs/task-evidence/offline-mono-wpe/README.md":
        "c57df3412bd9e491e5bb4a32b20cf834ecee41da25ce68130d728b48b8877819",
    "docs/task-evidence/offline-mono-wpe/report.json":
        "2b9be2488c4b0f82f417abd3e131c840729856937ed8239f2645beeaa30d7e61",
    "docs/task-evidence/offline-multichannel-wpe/README.md":
        "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/offline-multichannel-wpe/report.json":
        "4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba",
}

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "id": TASK,
    "mode": MODE,
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "f041a4088f26fadfe7ed77d73f7d06c31c35954a7d71ec08f0d08cba2abc1d46")
BOARD_ROW_CLAIM = {
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
    "worktree": CLAIM_WORKTREE,
    "reviewer": REVIEWER,
}
MUTABLE_TASK_FIELDS = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history",
)

ABSENCE_PROBES: Tuple[str, ...] = (
    "adapters/nara-wpe",
    "adapters/nara_wpe",
    "data/checkouts/nara-wpe",
    "data/checkouts/nara_wpe",
    "data/checkouts/nara_wpe_reference",
    "data/envs/nara-wpe",
    "data/envs/nara-wpe/requirements.lock",
    "data/rights/nara-wpe-license.json",
    "data/rights/nara-wpe-rights.json",
    "data/runs/nara-wpe-cohort/manifest.json",
    "data/runs/nara-wpe-parity/manifest.json",
    "data/runs/nara-wpe-parity/vector.json",
    "research/voice-enhancement-20261101/repos/nara_wpe",
)

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
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}

GEOMETRY_FIELDS = (
    "sample_rate_hz", "channels", "fft_size", "hop_size", "taps",
    "prediction_delay_frames", "stft_window", "early_window_ms",
)
PROJECT_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "fft_size": PROJECT_FFT_SIZE,
    "hop_size": PROJECT_HOP_SIZE,
    "taps": PROJECT_TAPS,
    "prediction_delay_frames": PROJECT_PREDICTION_DELAY_FRAMES,
    "early_window_ms": PROJECT_EARLY_WINDOW_MS,
}
MATCHED_GEOMETRY_FIELDS = (
    "sample_rate_hz", "channels", "fft_size", "hop_size", "taps",
    "prediction_delay_frames", "early_window_ms",
)
STFT_WINDOWS = frozenset({"hann", "sqrt_hann", "rectangular", "hamming"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.+\-][A-Za-z0-9.+\-]+)?$")

GATE_IDS = (
    "exact_source_and_asset_identity",
    "runtime_admission",
    "artifact_rights_and_licence",
    "exact_reference_parity",
    "matched_room_policy",
    "task_scope_and_geometry",
    "opt_in_provider_intake",
    "public_default_and_release",
)
BLOCKER_IDS = (
    "source_checkout_absent",
    "upstream_revision_unpinned",
    "package_metadata_and_license_absent",
    "runtime_and_lock_absent",
    "matched_parity_vector_absent",
    "task_geometry_unestablished",
    "matched_room_cohort_and_rights_absent",
    "opt_in_provider_and_release_absent",
)


# ---------------------------------------------------------------------------
# Strict JSON and hashing helpers
# ---------------------------------------------------------------------------


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, indent=2)
    return (text + "\n").encode("utf-8")


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(token: str) -> None:
        raise ValueError("non_finite:" + token)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def object_digest(value: Any) -> str:
    return sha256(canonical_bytes(value))


def _nonzero_float(value: float) -> float:
    return 0.0 if value == 0.0 else value


def _exact_keys(value: Any, expected: Iterable[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(label + ":not_object")
    actual = set(value)
    expected_set = set(expected)
    if actual != expected_set:
        missing = sorted(expected_set - actual)
        extra = sorted(actual - expected_set)
        raise ValueError(
            f"{label}:key_mismatch:missing={missing}:extra={extra}")


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError(label)


def _require_text(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(value), label + ":not_text")
    _require("\x00" not in value, label + ":nul")
    return value


def _require_sha(value: Any, label: str) -> str:
    text = _require_text(value, label)
    _require(SHA256_RE.fullmatch(text) is not None, label + ":not_sha256")
    return text


def _require_relative_path(value: Any, label: str) -> str:
    text = _require_text(value, label)
    _require("\\" not in text, label + ":backslash")
    _require(not text.startswith("/"), label + ":absolute")
    parts = text.split("/")
    _require(all(part not in ("", ".", "..") for part in parts),
             label + ":unsafe")
    return text


# ---------------------------------------------------------------------------
# Synthetic geometry control (not NARA-WPE)
# ---------------------------------------------------------------------------


def frame_count(source_samples: int, hop_size: int) -> int:
    """Count non-empty half-open frame intervals on the declared grid."""
    _require(_is_int(source_samples) and source_samples > 0,
             "frame_count:samples")
    _require(_is_int(hop_size) and hop_size > 0, "frame_count:hop")
    return (source_samples + hop_size - 1) // hop_size


def frame_intervals(source_samples: int, hop_size: int) -> List[Tuple[int, int]]:
    count = frame_count(source_samples, hop_size)
    return [(index * hop_size,
             min((index + 1) * hop_size, source_samples))
            for index in range(count)]


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def control_signal(source_samples: int = CONTROL_SOURCE_SAMPLES) -> List[float]:
    """Deterministic integer-derived f32 signal; no audio file is read."""
    return [_f32(((index * 37) % 4001 - 2000) / 2048.0)
            for index in range(source_samples)]


def signal_digest(signal: Sequence[float]) -> str:
    packed = b"".join(struct.pack("<f", float(value)) for value in signal)
    return sha256(packed)


def identity_control(signal: Sequence[float]) -> List[float]:
    """Bit-exact identity path; the mandatory control, not a dereverberator."""
    output: List[float] = []
    for value in signal:
        if not isinstance(value, float) or not math.isfinite(value):
            raise ValueError("control_nonfinite")
        output.append(_f32(value))
    return output


def _validate_geometry(config: Any) -> Dict[str, Any]:
    _exact_keys(config, GEOMETRY_FIELDS, "geometry")
    for key in ("sample_rate_hz", "channels", "fft_size", "hop_size", "taps",
                "prediction_delay_frames", "early_window_ms"):
        _require(_is_int(config[key]), "geometry:" + key + ":not_int")
    window = config["stft_window"]
    _require(isinstance(window, str) and window in STFT_WINDOWS,
             "geometry:stft_window:invalid")
    return config


def validate_matched_geometry(config: Any) -> Dict[str, Any]:
    """Accept only the pinned project WPE geometry used for a future parity run."""
    _validate_geometry(config)
    for key in MATCHED_GEOMETRY_FIELDS:
        _require(config[key] == PROJECT_GEOMETRY[key],
                 "geometry_mismatch:" + key)
    return config


def geometry_control() -> Dict[str, Any]:
    """Check the declared project grid; no STFT, audio or filter is executed."""
    signal = control_signal()
    intervals = frame_intervals(len(signal), PROJECT_HOP_SIZE)
    contiguous = all(
        start == index * PROJECT_HOP_SIZE and end > start
        for index, (start, end) in enumerate(intervals))
    covered = sum(end - start for start, end in intervals) == len(signal)
    identity = identity_control(signal)
    identity_ok = identity == signal and signal_digest(identity) == \
        signal_digest(signal)
    partial = (len(signal) % PROJECT_HOP_SIZE)
    prefix = signal[:480]
    partial_input = signal[:1000]
    partial_output = identity_control(partial_input)
    partial_ok = partial_output == partial_input and \
        partial_output[:len(prefix)] == prefix

    accepted = validate_matched_geometry(dict(PROJECT_GEOMETRY,
                                              stft_window="hann"))
    rejections = 0
    bad_configs: List[Dict[str, Any]] = []
    for key, value in (
        ("sample_rate_hz", 48000), ("sample_rate_hz", 8000),
        ("channels", 2), ("channels", 3), ("channels", 0),
        ("fft_size", 256), ("fft_size", 1024),
        ("hop_size", 256), ("hop_size", 0),
        ("taps", 0), ("taps", 10),
        ("prediction_delay_frames", 0), ("prediction_delay_frames", 3),
        ("early_window_ms", 0), ("early_window_ms", 100),
        ("stft_window", "kaiser"),
    ):
        bad = dict(PROJECT_GEOMETRY, stft_window="hann")
        bad[key] = value
        bad_configs.append(bad)
    for bad in bad_configs:
        try:
            validate_matched_geometry(bad)
        except ValueError:
            rejections += 1
    for bad in (
        dict(PROJECT_GEOMETRY, stft_window="hann", extra=1),
        {key: value for key, value in PROJECT_GEOMETRY.items()
         if key != "taps"} | {"stft_window": "hann"},
        dict(PROJECT_GEOMETRY, stft_window="hann", taps=True),
        dict(PROJECT_GEOMETRY, stft_window="hann", channels=False),
    ):
        try:
            validate_matched_geometry(bad)
        except ValueError:
            rejections += 1
    nonfinite = 0
    for value in (math.nan, math.inf, -math.inf):
        try:
            identity_control([value])
        except ValueError:
            nonfinite += 1

    return {
        "kind": "synthetic_geometry_control_not_nara_wpe",
        "source_samples": len(signal),
        "frame_hop_samples": PROJECT_HOP_SIZE,
        "frame_count": len(intervals),
        "final_frame_source_valid": partial,
        "early_target_window_samples": PROJECT_EARLY_WINDOW_SAMPLES,
        "stft_lookahead_samples": PROJECT_STFT_LOOKAHEAD_SAMPLES,
        "predictor_delay_samples": PROJECT_PREDICTOR_DELAY_SAMPLES,
        "declared_algorithmic_latency_samples":
            PROJECT_ALGORITHMIC_LATENCY_SAMPLES,
        "declared_algorithmic_latency_ms": PROJECT_ALGORITHMIC_LATENCY_MS,
        "covered_source_samples": len(signal),
        "contiguous_half_open_intervals": contiguous and covered,
        "identity_bit_exact": identity_ok,
        "identity_digest": signal_digest(identity),
        "partial_tail_matches_prefix": partial_ok,
        "partial_tail_valid_samples": len(partial_output),
        "config_accepted": accepted == dict(PROJECT_GEOMETRY,
                                            stft_window="hann"),
        "config_rejections": rejections,
        "nonfinite_rejections": nonfinite,
        "not_nara_wpe": True,
        "dereverberation_performed": False,
        "real_audio_used": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Strict caller-supplied tool manifest
# ---------------------------------------------------------------------------

MANIFEST_TOP_KEYS = (
    "schema_id", "source", "package", "runtime", "geometry", "parity",
    "rights", "qualification_claim",
)
MANIFEST_SOURCE_KEYS = (
    "checkout_path", "revision", "license_id", "license_text_path",
    "license_text_sha256", "file_manifest_path", "file_manifest_sha256",
)
MANIFEST_PACKAGE_KEYS = (
    "name", "version", "wheel_path", "wheel_sha256", "import_name",
)
MANIFEST_RUNTIME_KEYS = (
    "lock_path", "lock_sha256", "python_version", "platform",
)
MANIFEST_GEOMETRY_KEYS = (
    "sample_rate_hz", "channels", "fft_size", "hop_size", "taps",
    "prediction_delay_frames", "stft_window", "early_window_ms",
)
MANIFEST_PARITY_KEYS = (
    "output_vector_path", "output_vector_sha256", "cohort_manifest_path",
    "cohort_manifest_sha256", "item_count",
)
MANIFEST_RIGHTS_KEYS = (
    "record_path", "record_sha256", "commercial_use_permitted",
    "output_use_permitted",
)


def _validate_manifest_structure(manifest: Any) -> Dict[str, Any]:
    _exact_keys(manifest, MANIFEST_TOP_KEYS, "manifest")
    _require(manifest["schema_id"] == CALLER_MANIFEST_SCHEMA_ID,
             "manifest:schema_id")
    _require(manifest["qualification_claim"] is False,
             "manifest:qualification_claim")

    source = manifest["source"]
    _exact_keys(source, MANIFEST_SOURCE_KEYS, "manifest.source")
    _require_relative_path(source["checkout_path"], "manifest.source.checkout")
    revision = _require_text(source["revision"], "manifest.source.revision")
    _require(REVISION_RE.fullmatch(revision) is not None,
             "manifest.source.revision:not_40_hex")
    _require_text(source["license_id"], "manifest.source.license_id")
    _require_relative_path(source["license_text_path"],
                           "manifest.source.license_text_path")
    _require_sha(source["license_text_sha256"],
                 "manifest.source.license_text_sha256")
    _require_relative_path(source["file_manifest_path"],
                           "manifest.source.file_manifest_path")
    _require_sha(source["file_manifest_sha256"],
                 "manifest.source.file_manifest_sha256")

    package = manifest["package"]
    _exact_keys(package, MANIFEST_PACKAGE_KEYS, "manifest.package")
    _require(package["name"] == "nara_wpe", "manifest.package.name")
    _require(package["import_name"] == "nara_wpe", "manifest.package.import")
    _require(isinstance(package["version"], str)
             and VERSION_RE.fullmatch(package["version"]) is not None,
             "manifest.package.version")
    _require_relative_path(package["wheel_path"], "manifest.package.wheel_path")
    _require_sha(package["wheel_sha256"], "manifest.package.wheel_sha256")

    runtime = manifest["runtime"]
    _exact_keys(runtime, MANIFEST_RUNTIME_KEYS, "manifest.runtime")
    _require_relative_path(runtime["lock_path"], "manifest.runtime.lock_path")
    _require_sha(runtime["lock_sha256"], "manifest.runtime.lock_sha256")
    _require(runtime["python_version"] == "3.12.16",
             "manifest.runtime.python_version")
    platform = _require_text(runtime["platform"], "manifest.runtime.platform")
    _require(re.fullmatch(r"[a-z0-9]+-[a-z0-9]+", platform) is not None,
             "manifest.runtime.platform:shape")

    geometry = manifest["geometry"]
    _exact_keys(geometry, MANIFEST_GEOMETRY_KEYS, "manifest.geometry")
    validate_matched_geometry(geometry)

    parity = manifest["parity"]
    _exact_keys(parity, MANIFEST_PARITY_KEYS, "manifest.parity")
    _require_relative_path(parity["output_vector_path"],
                           "manifest.parity.output_vector_path")
    _require_sha(parity["output_vector_sha256"],
                 "manifest.parity.output_vector_sha256")
    _require_relative_path(parity["cohort_manifest_path"],
                           "manifest.parity.cohort_manifest_path")
    _require_sha(parity["cohort_manifest_sha256"],
                 "manifest.parity.cohort_manifest_sha256")
    _require(_is_int(parity["item_count"]) and
             0 < parity["item_count"] <= 100000,
             "manifest.parity.item_count")

    rights = manifest["rights"]
    _exact_keys(rights, MANIFEST_RIGHTS_KEYS, "manifest.rights")
    _require_relative_path(rights["record_path"], "manifest.rights.record_path")
    _require_sha(rights["record_sha256"], "manifest.rights.record_sha256")
    _require(isinstance(rights["commercial_use_permitted"], bool),
             "manifest.rights.commercial_use_permitted")
    _require(isinstance(rights["output_use_permitted"], bool),
             "manifest.rights.output_use_permitted")
    return manifest


def _resolve_caller_path(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = (root / relative).resolve()
    if root not in path.parents and path != root:
        raise ValueError("manifest_path_escape:" + relative)
    return path


def validate_caller_manifest(manifest: Any, *,
                             caller_root: Optional[Path] = None,
                             require_files: bool = False) -> Dict[str, Any]:
    """Validate a caller-owned NARA-WPE manifest; never loads the package."""
    _validate_manifest_structure(manifest)
    if not require_files:
        return manifest
    if caller_root is None:
        raise ValueError("manifest:caller_root_required")
    checked = 0
    for relative in (
        manifest["source"]["checkout_path"],
        manifest["source"]["license_text_path"],
        manifest["source"]["file_manifest_path"],
        manifest["package"]["wheel_path"],
        manifest["runtime"]["lock_path"],
        manifest["parity"]["output_vector_path"],
        manifest["parity"]["cohort_manifest_path"],
        manifest["rights"]["record_path"],
    ):
        _resolve_caller_path(caller_root, relative)
    source_root = _resolve_caller_path(
        caller_root, manifest["source"]["checkout_path"])
    if not source_root.is_dir():
        raise ValueError("manifest:source_not_directory")
    for relative, expected in (
        (manifest["source"]["license_text_path"],
         manifest["source"]["license_text_sha256"]),
        (manifest["source"]["file_manifest_path"],
         manifest["source"]["file_manifest_sha256"]),
        (manifest["package"]["wheel_path"],
         manifest["package"]["wheel_sha256"]),
        (manifest["runtime"]["lock_path"], manifest["runtime"]["lock_sha256"]),
        (manifest["parity"]["output_vector_path"],
         manifest["parity"]["output_vector_sha256"]),
        (manifest["parity"]["cohort_manifest_path"],
         manifest["parity"]["cohort_manifest_sha256"]),
        (manifest["rights"]["record_path"], manifest["rights"]["record_sha256"]),
    ):
        path = _resolve_caller_path(caller_root, relative)
        if not path.is_file():
            raise ValueError("manifest:file_missing:" + relative)
        if sha256_file(path) != expected:
            raise ValueError("manifest:file_digest:" + relative)
        checked += 1
    return manifest


def _synthetic_manifest(root: Path) -> Dict[str, Any]:
    """Build a caller-owned structural control; labelled non-evidence."""
    files = {
        "nara_wpe/LICENSE": b"caller-supplied license text; synthetic control\n",
        "nara_wpe/files.sha256": b"0" * 64 + b"  synthetic\n",
        "nara_wpe/pkg.whl": b"synthetic wheel bytes\n",
        "nara_wpe/requirements.lock": b"numpy==0.0.0\n",
        "nara_wpe/parity.json": b'{"synthetic":true}\n',
        "nara_wpe/cohort.json": b'{"synthetic":true}\n',
        "nara_wpe/rights.json": b'{"synthetic":true}\n',
    }
    for relative, payload in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    (root / "nara_wpe").mkdir(exist_ok=True)

    def digest(relative: str) -> str:
        return sha256_file(root / relative)

    return {
        "schema_id": CALLER_MANIFEST_SCHEMA_ID,
        "source": {
            "checkout_path": "nara_wpe",
            "revision": "0" * 40,
            "license_id": "caller-declared",
            "license_text_path": "nara_wpe/LICENSE",
            "license_text_sha256": digest("nara_wpe/LICENSE"),
            "file_manifest_path": "nara_wpe/files.sha256",
            "file_manifest_sha256": digest("nara_wpe/files.sha256"),
        },
        "package": {
            "name": "nara_wpe",
            "version": "0.0.0",
            "wheel_path": "nara_wpe/pkg.whl",
            "wheel_sha256": digest("nara_wpe/pkg.whl"),
            "import_name": "nara_wpe",
        },
        "runtime": {
            "lock_path": "nara_wpe/requirements.lock",
            "lock_sha256": digest("nara_wpe/requirements.lock"),
            "python_version": "3.12.16",
            "platform": "darwin-arm64",
        },
        "geometry": dict(PROJECT_GEOMETRY, stft_window="hann"),
        "parity": {
            "output_vector_path": "nara_wpe/parity.json",
            "output_vector_sha256": digest("nara_wpe/parity.json"),
            "cohort_manifest_path": "nara_wpe/cohort.json",
            "cohort_manifest_sha256": digest("nara_wpe/cohort.json"),
            "item_count": 1,
        },
        "rights": {
            "record_path": "nara_wpe/rights.json",
            "record_sha256": digest("nara_wpe/rights.json"),
            "commercial_use_permitted": False,
            "output_use_permitted": False,
        },
        "qualification_claim": False,
    }


def _mutate(manifest: Dict[str, Any], path: Tuple[str, ...],
            value: Any) -> Dict[str, Any]:
    clone = json.loads(json.dumps(manifest))
    cursor: Dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


def _drop(manifest: Dict[str, Any], path: Tuple[str, ...]) -> Dict[str, Any]:
    clone = json.loads(json.dumps(manifest))
    cursor: Dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    del cursor[path[-1]]
    return clone


def manifest_rejection_examples() -> Dict[str, Any]:
    """Prove the caller-manifest validator is strict, not blanket-rejecting."""
    with tempfile.TemporaryDirectory(prefix="nara-wpe-manifest-") as temporary:
        root = Path(temporary)
        manifest = _synthetic_manifest(root)
        validate_caller_manifest(manifest, caller_root=root,
                                 require_files=True)
        accepted = 1
        rejected = 0
        mutations: List[Dict[str, Any]] = [
            _drop(manifest, ("schema_id",)),
            _mutate(manifest, ("schema_id",), "wrong"),
            _mutate(manifest, ("source", "revision"), "abc"),
            _mutate(manifest, ("source", "revision"), "G" * 40),
            _mutate(manifest, ("source", "checkout_path"), "/abs/path"),
            _mutate(manifest, ("source", "checkout_path"), "../escape"),
            _mutate(manifest, ("source", "checkout_path"), "a/./b"),
            _mutate(manifest, ("source", "license_text_sha256"), "0" * 63),
            _mutate(manifest, ("source", "license_text_sha256"), 0),
            _mutate(manifest, ("package", "name"), "nara-wpe"),
            _mutate(manifest, ("package", "import_name"), "nara"),
            _mutate(manifest, ("package", "version"), "v0"),
            _mutate(manifest, ("package", "wheel_path"), "..\\pkg.whl"),
            _mutate(manifest, ("runtime", "python_version"), "3.11.5"),
            _mutate(manifest, ("runtime", "platform"), "Darwin arm64"),
            _mutate(manifest, ("runtime", "lock_sha256"), "a" * 64),
            _mutate(manifest, ("geometry", "sample_rate_hz"), 48000),
            _mutate(manifest, ("geometry", "channels"), 2),
            _mutate(manifest, ("geometry", "fft_size"), 256),
            _mutate(manifest, ("geometry", "hop_size"), 256),
            _mutate(manifest, ("geometry", "taps"), 10),
            _mutate(manifest, ("geometry", "prediction_delay_frames"), 3),
            _mutate(manifest, ("geometry", "stft_window"), "kaiser"),
            _mutate(manifest, ("geometry", "early_window_ms"), 100),
            _mutate(manifest, ("geometry", "taps"), True),
            _mutate(manifest, ("parity", "item_count"), 0),
            _mutate(manifest, ("parity", "item_count"), True),
            _mutate(manifest, ("parity", "output_vector_path"), "../x"),
            _mutate(manifest, ("rights", "commercial_use_permitted"), "yes"),
            _mutate(manifest, ("rights", "output_use_permitted"), 1),
            _mutate(manifest, ("qualification_claim",), True),
            _mutate(manifest, ("extra",), True),
        ]
        for bad in mutations:
            try:
                validate_caller_manifest(bad, caller_root=root,
                                         require_files=True)
            except (ValueError, TypeError):
                rejected += 1
        pinned_blocked = 0
        try:
            local_pinned_admission(manifest)
        except ValueError as error:
            pinned_blocked = 1 if "upstream_source_absent" in str(error) else 0
        return {
            "accepted": accepted,
            "accepted_is_synthetic_not_evidence": True,
            "rejected": rejected,
            "rejected_total": len(mutations),
            "all_rejections_fail_closed": rejected == len(mutations),
            "pinned_admission_status": "blocked",
            "pinned_admission_reason": "upstream_source_absent",
            "pinned_admission_blocked": bool(pinned_blocked),
            "loaded": False,
            "executed": False,
            "imported": False,
            "qualifies": False,
        }


def local_pinned_admission(manifest: Any) -> Dict[str, Any]:
    """Fail closed unless the exact upstream checkout exists in this workspace."""
    validate_caller_manifest(manifest)
    source = AUDIO_ROOT / SOURCE_CHECKOUT_PATH
    if not source.is_dir():
        raise ValueError("upstream_source_absent:" + SOURCE_CHECKOUT_PATH)
    return {"pinned_asset": False, "qualifies": False,
            "reason": "runtime_not_admitted"}


# ---------------------------------------------------------------------------
# Absence audit and board identity
# ---------------------------------------------------------------------------


def audit_assets() -> Dict[str, Any]:
    probes = [{"path": path, "present": (AUDIO_ROOT / path).exists()}
              for path in ABSENCE_PROBES]
    return {
        "probe_count": len(probes),
        "probes": probes,
        "all_absence_probes_absent": all(not row["present"] for row in probes),
        "source_checkout_path": SOURCE_CHECKOUT_PATH,
        "source_adapter_path": SOURCE_ADAPTER_PATH,
        "runtime_env_path": RUNTIME_ENV_PATH,
    }


def board_row_digest() -> str:
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return sha256(raw)


# ---------------------------------------------------------------------------
# Contract and report builders
# ---------------------------------------------------------------------------


def _exact_scope() -> Dict[str, Any]:
    return {
        "write_scope": TASK_PREFIX + " only",
        "task_local_only": True,
        "provider_registered": False,
        "default_selected": False,
        "installed_v0_behavior_changed": False,
        "public_api_abi_changed": False,
        "contracts_changed": False,
        "registry_or_descriptor_changed": False,
        "shared_build_or_ci_changed": False,
        "board_or_handoff_changed": False,
        "downloads_performed": False,
        "real_audio_used": False,
        "listening_or_device_timing": False,
        "benchmark_or_release_claim": False,
    }


SCOPE_FALSE_FLAGS = tuple(key for key in _exact_scope()
                          if key not in ("write_scope", "task_local_only"))


def _installed_v0() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "frame_ns": FRAME_NS,
        "unchanged": True,
    }


def _upstream_identity() -> Dict[str, Any]:
    return {
        "name": UPSTREAM_NAME,
        "repository_url": UPSTREAM_REPOSITORY_URL,
        "access_scope": UPSTREAM_ACCESS_SCOPE,
        "revision": UPSTREAM_REVISION,
        "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "source_checkout_present": SOURCE_CHECKOUT_PRESENT,
        "license": UPSTREAM_LICENSE,
        "license_status": UPSTREAM_LICENSE_STATUS,
        "license_verified": False,
        "license_file_present": False,
        "package_metadata_present": False,
        "task_geometry_status": UPSTREAM_GEOMETRY_STATUS,
        "reported_geometry_asserted": False,
        "reported_sample_rate_hz": None,
        "reported_channels": None,
        "source_reported_description": (
            "Weighted-prediction-error dereverberation implementation URL "
            "recorded in the category source register under access scope "
            "'search excerpt'. No excerpt text, revision, licence, package "
            "metadata or default geometry is recorded locally."
        ),
    }


def _task_geometry() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "project_reference": {
            "source_paths": [
                "adapters/wpe/README.md",
                "docs/task-evidence/offline-mono-wpe/report.json",
            ],
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "fft_size": PROJECT_FFT_SIZE,
            "hop_size": PROJECT_HOP_SIZE,
            "taps": PROJECT_TAPS,
            "prediction_delay_frames": PROJECT_PREDICTION_DELAY_FRAMES,
            "iterations": PROJECT_ITERATIONS,
            "early_target_window_ms": PROJECT_EARLY_WINDOW_MS,
            "early_target_window_samples": PROJECT_EARLY_WINDOW_SAMPLES,
            "stft_lookahead_ms": PROJECT_STFT_LOOKAHEAD_MS,
            "stft_lookahead_samples": PROJECT_STFT_LOOKAHEAD_SAMPLES,
            "predictor_delay_ms": PROJECT_PREDICTOR_DELAY_MS,
            "predictor_delay_samples": PROJECT_PREDICTOR_DELAY_SAMPLES,
            "declared_algorithmic_latency_ms":
                PROJECT_ALGORITHMIC_LATENCY_MS,
            "declared_algorithmic_latency_samples":
                PROJECT_ALGORITHMIC_LATENCY_SAMPLES,
            "processing_modes": ["offline_whole_clip", "frame_causal_rls"],
            "note": (
                "Pinned project WPE defaults. They are not asserted as "
                "NARA-WPE defaults."
            ),
        },
        "upstream_matched_geometry": {
            "status": UPSTREAM_GEOMETRY_STATUS,
            "fft_size": None,
            "hop_size": None,
            "taps": None,
            "prediction_delay_frames": None,
            "iterations": None,
            "stft_window": None,
            "note": (
                "No upstream source, package metadata or excerpt text is "
                "present, so no NARA-WPE default is asserted."
            ),
        },
        "matched_configuration": {
            "required_for_parity": True,
            "must_equal_project_reference": True,
            "fields": list(MATCHED_GEOMETRY_FIELDS),
            "observed_upstream": None,
            "status": "blocked",
        },
    }


def _matched_evidence() -> Dict[str, Any]:
    return {
        "upstream_nara_wpe_outputs_present": False,
        "project_wpe_functions_present": True,
        "project_wpe_evidence": [
            {
                "path": "docs/task-evidence/offline-mono-wpe/report.json",
                "sha256": BOUNDARY_PINS[
                    "docs/task-evidence/offline-mono-wpe/report.json"],
                "role": (
                    "Separate mono project WPE evidence; context only, not "
                    "NARA-WPE output."
                ),
            },
            {
                "path": (
                    "docs/task-evidence/offline-multichannel-wpe/report.json"
                ),
                "sha256": BOUNDARY_PINS[
                    "docs/task-evidence/offline-multichannel-wpe/report.json"],
                "role": (
                    "Separate multichannel project WPE evidence; context "
                    "only, not NARA-WPE output."
                ),
            },
        ],
        "matched_comparison_status": "blocked",
        "pooling_allowed": False,
        "note": (
            "No NARA-WPE output exists, so no SI-SDR, STOI, SRMR or RTF "
            "comparison is claimed. Sibling WPE results are separate "
            "evidence and are never pooled or substituted."
        ),
    }


def _caller_asset_contract() -> Dict[str, Any]:
    result = manifest_rejection_examples()
    return {
        "schema_id": CALLER_MANIFEST_SCHEMA_ID,
        "accepted": result["accepted"],
        "accepted_is_synthetic_not_evidence":
            result["accepted_is_synthetic_not_evidence"],
        "rejected": result["rejected"],
        "rejected_total": result["rejected_total"],
        "all_rejections_fail_closed": result["all_rejections_fail_closed"],
        "pinned_admission_status": result["pinned_admission_status"],
        "pinned_admission_reason": result["pinned_admission_reason"],
        "pinned_admission_blocked": result["pinned_admission_blocked"],
        "loaded": False,
        "executed": False,
        "imported": False,
        "qualifies": False,
    }


def _licensing() -> Dict[str, Any]:
    return {
        "source_license": None,
        "source_license_status": UPSTREAM_LICENSE_STATUS,
        "license_text_present": False,
        "license_verified": False,
        "commercial_use_permitted": None,
        "commercial_use_status": "not_established",
        "redistribution_permitted": None,
        "output_use_status": "not_established",
        "note": (
            "No upstream licence text or package metadata is present. No "
            "term is assumed from the repository URL; commercial and output "
            "use remain unresolved."
        ),
    }


def _gates() -> List[Dict[str, str]]:
    return [
        {
            "id": "exact_source_and_asset_identity",
            "requirement": (
                "NARA-WPE source checkout at an immutable 40-hex revision "
                "with package metadata, a per-file SHA-256 manifest and the "
                "reviewed licence text pinned."
            ),
            "status": "blocked",
        },
        {
            "id": "runtime_admission",
            "requirement": (
                "Isolated hash-pinned Python 3.12.16 runtime with exact "
                "NumPy/SciPy versions, platform lock and offline load path."
            ),
            "status": "blocked",
        },
        {
            "id": "artifact_rights_and_licence",
            "requirement": (
                "Source, package, redistribution, derivative-output and "
                "product-use rights cleared by a reviewed rights record."
            ),
            "status": "blocked",
        },
        {
            "id": "exact_reference_parity",
            "requirement": (
                "Upstream WPE output at the matched 512/128/5/8 geometry, "
                "16 kHz mono and 3 iterations frozen as exact caller-supplied "
                "parity vectors against project wpe_offline."
            ),
            "status": "blocked",
        },
        {
            "id": "matched_room_policy",
            "requirement": (
                "Rights-cleared paired room fixtures with a frozen 50 ms "
                "early-reflection target, identity control and matched "
                "STFT/taps/room policy scoring."
            ),
            "status": "blocked",
        },
        {
            "id": "task_scope_and_geometry",
            "requirement": (
                "Upstream sample rate, channels, FFT, hop, window, taps, "
                "predictor delay, iterations, offline/online mode, reset and "
                "partial-tail behaviour established."
            ),
            "status": "blocked",
        },
        {
            "id": "opt_in_provider_intake",
            "requirement": (
                "Explicit opt-in tool-reference intake with licence review, "
                "descriptor review and no default registration."
            ),
            "status": "blocked",
        },
        {
            "id": "public_default_and_release",
            "requirement": (
                "Target timing, resource limits, listening, exact-head review "
                "and explicit release or benchmark approval."
            ),
            "status": "blocked",
        },
    ]


def _blockers() -> List[Dict[str, Any]]:
    return [
        {
            "id": "source_checkout_absent",
            "gate": "exact_source_and_asset_identity",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "A NARA-WPE checkout at data/checkouts/nara_wpe or an "
                "equivalent pinned caller path, with every source file hashed."
            ),
        },
        {
            "id": "upstream_revision_unpinned",
            "gate": "exact_source_and_asset_identity",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "The immutable 40-hex upstream revision named by the source "
                "register or an exact caller pin; no revision is recorded."
            ),
        },
        {
            "id": "package_metadata_and_license_absent",
            "gate": "artifact_rights_and_licence",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "Package name/version/wheel hash and reviewed licence text; "
                "the register records only the repository URL."
            ),
        },
        {
            "id": "runtime_and_lock_absent",
            "gate": "runtime_admission",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "A hash-pinned offline Python runtime and dependency lock "
                "capable of importing the exact NARA-WPE package."
            ),
        },
        {
            "id": "matched_parity_vector_absent",
            "gate": "exact_reference_parity",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "Frozen caller input, matched configuration and exact "
                "upstream output vector for parity against project WPE."
            ),
        },
        {
            "id": "task_geometry_unestablished",
            "gate": "task_scope_and_geometry",
            "state": "unestablished",
            "qualifies": False,
            "requirement": (
                "Upstream FFT/hop/window/taps/delay/iterations and "
                "offline-versus-online behaviour; only project defaults are "
                "pinned here."
            ),
        },
        {
            "id": "matched_room_cohort_and_rights_absent",
            "gate": "matched_room_policy",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "Rights-cleared paired room fixtures, measured or synthetic "
                "RIR provenance and a frozen 50 ms early target."
            ),
        },
        {
            "id": "opt_in_provider_and_release_absent",
            "gate": "public_default_and_release",
            "state": "absent",
            "qualifies": False,
            "requirement": (
                "Opt-in intake, target-device timing, listening protocol and "
                "explicit release approval; no default or registration."
            ),
        },
    ]


def _room_profile(control: Dict[str, Any]) -> Dict[str, Any]:
    checks = [
        {
            "id": "frozen_render_reference",
            "status": "blocked",
            "evidence": "No NARA-WPE output and no frozen room render exists.",
        },
        {
            "id": "channel_rate_hop",
            "status": "control_only",
            "evidence": (
                "Project grid 16 kHz mono, 512/128/5/8 is pinned; upstream "
                "channel/rate/hop are unestablished."
            ),
        },
        {
            "id": "excitation",
            "status": "not_applicable",
            "evidence": "No dereverberation is run, so no excitation exists.",
        },
        {
            "id": "delay",
            "status": "control_only",
            "evidence": (
                f"Declared project latency {control['declared_algorithmic_latency_samples']} "
                f"samples/{control['declared_algorithmic_latency_ms']} ms; "
                "upstream delay unestablished."
            ),
        },
        {
            "id": "movement",
            "status": "not_applicable",
            "evidence": "No render path or measured room movement exists.",
        },
        {
            "id": "noise",
            "status": "blocked",
            "evidence": "No rights-cleared noisy-speech stratum exists.",
        },
        {
            "id": "reset_schedule",
            "status": "blocked",
            "evidence": "No upstream runtime or candidate state exists.",
        },
        {
            "id": "echo_only",
            "status": "not_applicable",
            "evidence": (
                "Dereverberation is not playback echo cancellation; no "
                "far-end echo path is claimed."
            ),
        },
        {
            "id": "near_end_only",
            "status": "not_applicable",
            "evidence": "No near-end/render decomposition is claimed.",
        },
        {
            "id": "overlap",
            "status": "not_applicable",
            "evidence": "No double-talk condition is evaluated.",
        },
        {
            "id": "no_reference",
            "status": "blocked",
            "evidence": "No candidate output exists to compare.",
        },
        {
            "id": "echo_attenuation",
            "status": "not_measured",
            "evidence": "No echo cancellation is attempted.",
        },
        {
            "id": "near_end_damage",
            "status": "blocked",
            "evidence": "No real candidate output or early-target score exists.",
        },
        {
            "id": "nonfinite_failures",
            "status": "control_only",
            "evidence": (
                f"{control['nonfinite_rejections']} injected nonfinite values "
                "were rejected before state change; no candidate output exists."
            ),
        },
        {
            "id": "alignment",
            "status": "control_only",
            "evidence": (
                "Half-open source-frame grid is exact; no candidate alignment "
                "or upstream latency is claimed."
            ),
        },
        {
            "id": "delayed_or_missing_render",
            "status": "not_applicable",
            "evidence": (
                "No separate render/echo-return channel exists in a "
                "dereverberation reference."
            ),
        },
        {
            "id": "no_reference_independent_comparison",
            "status": "blocked",
            "evidence": "No independent comparison, corpus or listener exists.",
        },
    ]
    return {
        "profile": PROFILE,
        "status": "applied_with_all_qualification_items_blocked",
        "checks": checks,
        "not_applicable": ["delayed_or_missing_render", "echo_only",
                          "near_end_only", "overlap", "movement",
                          "excitation"],
        "qualifies": False,
    }


def _profile_checks(control: Dict[str, Any],
                    contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    audit = contract["asset_audit"]
    caller = contract["caller_asset_contract"]
    upstream = contract["upstream_identity"]
    rows = [
        ("source_absence_audited", audit["all_absence_probes_absent"]),
        ("upstream_revision_not_fabricated",
         upstream["revision"] is None and
         upstream["revision_pin_available"] is False),
        ("upstream_license_not_fabricated",
         upstream["license"] is None and
         upstream["license_verified"] is False),
        ("upstream_geometry_not_asserted",
         upstream["task_geometry_status"] == "unestablished" and
         upstream["reported_geometry_asserted"] is False),
        ("project_geometry_pinned",
         contract["task_geometry"]["project_reference"]["fft_size"] == 512 and
         contract["task_geometry"]["project_reference"]["hop_size"] == 128),
        ("matched_config_required",
         contract["task_geometry"]["matched_configuration"][
             "must_equal_project_reference"] is True),
        ("caller_schema_accepts_structural_control",
         caller["accepted"] == 1 and
         caller["accepted_is_synthetic_not_evidence"] is True),
        ("caller_manifest_rejections_fail_closed",
         caller["all_rejections_fail_closed"] is True and
         caller["rejected"] == caller["rejected_total"]),
        ("pinned_admission_blocked",
         caller["pinned_admission_blocked"] is True and
         caller["pinned_admission_reason"] == "upstream_source_absent"),
        ("identity_control_bit_exact", control["identity_bit_exact"] is True),
        ("frame_grid_half_open",
         control["contiguous_half_open_intervals"] is True and
         control["covered_source_samples"] == control["source_samples"]),
        ("early_window_50ms_exact",
         control["early_target_window_samples"] == 800),
        ("declared_latency_80ms_exact",
         control["declared_algorithmic_latency_samples"] == 1280 and
         control["declared_algorithmic_latency_ms"] == 80),
        ("final_partial_37",
         control["final_frame_source_valid"] == 37 and
         control["partial_tail_matches_prefix"] is True),
        ("nonfinite_rejected", control["nonfinite_rejections"] == 3),
        ("config_mismatch_rejected",
         control["config_rejections"] >= 20),
        ("no_real_audio", control["real_audio_used"] is False),
        ("no_listening_or_device_timing",
         contract["exact_scope"]["listening_or_device_timing"] is False),
        ("no_benchmark_or_release_claim",
         contract["exact_scope"]["benchmark_or_release_claim"] is False),
        ("no_downloads", contract["exact_scope"]["downloads_performed"] is False),
        ("no_provider_or_default_change",
         contract["exact_scope"]["provider_registered"] is False and
         contract["exact_scope"]["default_selected"] is False),
        ("sibling_evidence_not_pooled",
         contract["matched_evidence"]["pooling_allowed"] is False),
        ("room_profile_applied",
         contract["room_profile"]["profile"] == PROFILE),
        ("all_eight_gates_blocked",
         len(contract["gates"]) == 8 and
         all(row["status"] == "blocked" for row in contract["gates"])),
        ("candidate_not_qualified",
         contract["qualification"]["candidate_qualified"] is False),
    ]
    return [{"id": key, "passed": bool(value)} for key, value in rows]


def build_contract() -> Dict[str, Any]:
    control = geometry_control()
    caller = _caller_asset_contract()
    contract: Dict[str, Any] = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "protocol": PROTOCOL,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": MODE,
        "verification_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "owner": OWNER,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "exact_scope": _exact_scope(),
        "installed_v0": _installed_v0(),
        "installed_v0_unchanged": True,
        "upstream_identity": _upstream_identity(),
        "task_geometry": _task_geometry(),
        "geometry_control": control,
        "caller_asset_contract": caller,
        "asset_audit": audit_assets(),
        "matched_evidence": _matched_evidence(),
        "room_profile": _room_profile(control),
        "licensing": _licensing(),
        "gates": _gates(),
        "exact_blockers": _blockers(),
        "remaining_gates": list(GATE_IDS),
        "non_claims": [
            "No NARA-WPE source, wheel, revision, licence or output exists.",
            "No NARA-WPE import, execution or dereverberation was performed.",
            "No real audio, RIR, corpus, listening or device timing was used.",
            "No SI-SDR, STOI, SRMR, PESQ, RTF or latency is claimed.",
            "No provider, default, public ABI, CONTRACTS, registry, "
            "descriptor, shared build, CI, board or handoff change is made.",
            "No benchmark, qualification or release claim is made.",
        ],
        "reproduction": {
            "interpreter": "Python 3.12.16",
            "environment": "PYTHONDONTWRITEBYTECODE=1",
            "commands": [
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
                "python3 -m reuse lint",
                "git diff --check",
                "python3 scripts/ci.py",
            ],
            "note": (
                "scripts/ci.py is run from the SDK worktree root after the "
                "task-local commands; it packages the installed SDK and does "
                "not execute NARA-WPE."
            ),
        },
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "decision": DECISION,
            "evidence_status": EVIDENCE_STATUS,
            "blocked_gate_count": 8,
            "blocked_gate_ids": list(GATE_IDS),
            "all_release_gates_blocked": True,
            "synthetic_profile_checks_passed": True,
            "no_missing_result_qualifies_candidate": True,
            "release_results_present": False,
            "missing_result_promoted": False,
            "real_source_or_runtime_used": False,
            "listening_or_device_timing_claim": False,
        },
    }
    checks = _profile_checks(control, contract)
    contract["profile_scoring"] = {
        "scope": "synthetic geometry control only; not release qualification",
        "checks": checks,
        "passed": all(row["passed"] for row in checks),
        "failed_checks": [row["id"] for row in checks if not row["passed"]],
    }
    validate_contract(contract)
    return contract


def validate_contract(contract: Any) -> None:
    _exact_keys(contract, (
        "schema_id", "protocol", "task", "title", "component", "mode",
        "verification_profile", "base_commit", "branch", "owner", "reviewer",
        "worktree", "status", "evidence_status", "decision", "defer_before",
        "exact_scope", "installed_v0", "installed_v0_unchanged",
        "upstream_identity", "task_geometry", "geometry_control",
        "caller_asset_contract", "asset_audit", "matched_evidence",
        "room_profile", "licensing", "gates", "exact_blockers",
        "remaining_gates", "non_claims", "reproduction", "qualification",
        "profile_scoring",
    ), "contract")
    if contract["schema_id"] != CONTRACT_SCHEMA_ID:
        raise ValueError("contract:schema_id")
    if contract["task"] != TASK or contract["component"] != COMPONENT:
        raise ValueError("contract:identity")
    if contract["verification_profile"] != PROFILE:
        raise ValueError("contract:profile")
    if contract["base_commit"] != BASE_COMMIT:
        raise ValueError("contract:base_commit")
    if contract["decision"] != DECISION or contract["status"] != STATUS:
        raise ValueError("contract:disposition")
    if contract["qualification"]["status"] != QUALIFICATION:
        raise ValueError("contract:qualification")
    if contract["exact_scope"]["write_scope"] != TASK_PREFIX + " only":
        raise ValueError("contract:write_scope")
    for key in SCOPE_FALSE_FLAGS:
        if contract["exact_scope"][key] is not False:
            raise ValueError("contract:scope_flag:" + key)
    if contract["installed_v0_unchanged"] is not True:
        raise ValueError("contract:installed_v0")
    if len(contract["gates"]) != 8 or len(contract["exact_blockers"]) != 8:
        raise ValueError("contract:gate_count")
    if tuple(row["id"] for row in contract["gates"]) != GATE_IDS:
        raise ValueError("contract:gate_ids")
    if tuple(row["id"] for row in contract["exact_blockers"]) != BLOCKER_IDS:
        raise ValueError("contract:blocker_ids")
    if any(row["status"] != "blocked" for row in contract["gates"]):
        raise ValueError("contract:gate_not_blocked")
    if any(row["qualifies"] is not False for row in
           contract["exact_blockers"]):
        raise ValueError("contract:blocker_qualifies")
    if contract["caller_asset_contract"]["all_rejections_fail_closed"] is not True:
        raise ValueError("contract:caller_contract")
    if contract["asset_audit"]["all_absence_probes_absent"] is not True:
        raise ValueError("contract:asset_present")
    if contract["profile_scoring"]["passed"] is not True:
        raise ValueError("contract:profile_scoring")


def build_report() -> Dict[str, Any]:
    contract = build_contract()
    report: Dict[str, Any] = {
        "schema_id": REPORT_SCHEMA_ID,
        "protocol": PROTOCOL,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": MODE,
        "verification_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "owner": OWNER,
        "reviewer": REVIEWER,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "contract_sha256": object_digest(contract),
        "exact_scope": contract["exact_scope"],
        "scope": {key: contract["exact_scope"][key]
                  for key in ("task_local_only",)},
        "installed_v0": contract["installed_v0"],
        "board_row": {
            "source": f"plan/swarm/TASKS.json#tasks[id={TASK}]",
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
            "whole_file_hashed": False,
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
            "claim": BOARD_ROW_CLAIM,
        },
        "upstream_identity": contract["upstream_identity"],
        "task_geometry": contract["task_geometry"],
        "geometry_control": contract["geometry_control"],
        "caller_asset_contract": contract["caller_asset_contract"],
        "absence_audit": contract["asset_audit"],
        "matched_evidence": contract["matched_evidence"],
        "room_profile": contract["room_profile"],
        "licensing": contract["licensing"],
        "gates": contract["gates"],
        "blockers": contract["exact_blockers"],
        "remaining_gates": contract["remaining_gates"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "profile_scoring": contract["profile_scoring"],
        "qualification": contract["qualification"],
        "source_pins": {
            path: {"sha256": digest, "verified": True}
            for path, digest in SOURCE_PINS.items()
        },
        "boundary_pins": {
            path: {"sha256": digest, "verified": True}
            for path, digest in BOUNDARY_PINS.items()
        },
    }
    report["scope"].update({key: contract["exact_scope"][key]
                            for key in SCOPE_FALSE_FLAGS})
    validate_report(report, contract)
    return report


def validate_report(report: Any, contract: Optional[Dict[str, Any]] = None) -> None:
    if contract is None:
        contract = build_contract()
    _exact_keys(report, (
        "schema_id", "protocol", "task", "title", "component", "mode",
        "verification_profile", "base_commit", "branch", "worktree", "owner",
        "reviewer", "status", "evidence_status", "decision", "defer_before",
        "proposal_only", "contract_sha256", "exact_scope", "scope",
        "installed_v0", "board_row", "upstream_identity", "task_geometry",
        "geometry_control", "caller_asset_contract", "absence_audit",
        "matched_evidence", "room_profile", "licensing", "gates", "blockers",
        "remaining_gates", "non_claims", "reproduction", "profile_scoring",
        "qualification", "source_pins", "boundary_pins",
    ), "report")
    if report["schema_id"] != REPORT_SCHEMA_ID:
        raise ValueError("report:schema_id")
    if report["status"] != STATUS or report["decision"] != DECISION:
        raise ValueError("report:disposition")
    if report["evidence_status"] != EVIDENCE_STATUS:
        raise ValueError("report:evidence_status")
    if report["proposal_only"] is not True:
        raise ValueError("report:proposal_only")
    if report["contract_sha256"] != object_digest(contract):
        raise ValueError("report:contract_digest")
    if report["qualification"]["status"] != QUALIFICATION:
        raise ValueError("report:qualification")
    for key in ("exact_scope", "installed_v0", "upstream_identity",
                "task_geometry", "geometry_control", "caller_asset_contract",
                "matched_evidence", "room_profile", "licensing", "gates",
                "remaining_gates", "non_claims", "reproduction",
                "profile_scoring", "qualification"):
        if report[key] != contract[key]:
            raise ValueError("report:copy_mismatch:" + key)
    if report["blockers"] != contract["exact_blockers"]:
        raise ValueError("report:copy_mismatch:blockers")
    if report["absence_audit"] != contract["asset_audit"]:
        raise ValueError("report:copy_mismatch:absence")
    for key in ("provider_registered", "default_selected",
                "installed_v0_behavior_changed", "public_api_abi_changed",
                "contracts_changed", "registry_or_descriptor_changed",
                "shared_build_or_ci_changed", "board_or_handoff_changed",
                "downloads_performed", "real_audio_used",
                "listening_or_device_timing", "benchmark_or_release_claim"):
        if report["scope"][key] is not False:
            raise ValueError("report:scope_overclaim:" + key)
    if report["scope"]["task_local_only"] is not True:
        raise ValueError("report:scope_not_local")
    board = report["board_row"]
    if board["stable_sha256"] != BOARD_ROW_STABLE_SHA256:
        raise ValueError("report:board_digest")
    if board["whole_file_hashed"] is not False:
        raise ValueError("report:board_whole_file")
    if board["claim"] != BOARD_ROW_CLAIM:
        raise ValueError("report:board_claim")
    if board_row_digest() != BOARD_ROW_STABLE_SHA256:
        raise ValueError("report:board_digest_drift")
    if report["source_pins"] != {
            path: {"sha256": digest, "verified": True}
            for path, digest in SOURCE_PINS.items()}:
        raise ValueError("report:source_pins")
    if report["boundary_pins"] != {
            path: {"sha256": digest, "verified": True}
            for path, digest in BOUNDARY_PINS.items()}:
        raise ValueError("report:boundary_pins")


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract())


def canonical_report_bytes() -> bytes:
    return canonical_bytes(build_report())


# ---------------------------------------------------------------------------
# SOURCES.sha256 and README digest tables
# ---------------------------------------------------------------------------


def _local_manifest_paths() -> List[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


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
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        f"# Full mutable task board (TASKS.json) is never hashed; only "
        f"board_row.stable_sha256={BOARD_ROW_STABLE_SHA256} is gated.",
    ]
    lines.extend(f"{digest}  {name}" for digest, name in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError(f"malformed_pin_line:{number}")
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:") or
                path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{number}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{number}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS} |
            {"sdk:" + name for name in BOUNDARY_PINS} |
            {TASK_PREFIX + name for name in _local_manifest_paths()})


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in _local_manifest_paths()
                      if name not in ARTIFACT_TABLE_EXCLUDED},
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
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or \
                        re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if SHA256_RE.fullmatch(digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def _resolve_source_path(relative: str) -> Path:
    return AUDIO_ROOT / relative


def verify_readme_digests(text: str) -> Dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = _resolve_source_path(key[len("source:"):])
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = SDK_ROOT / key[len("sdk:"):]
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if path.is_file() and sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        path = HERE / key
        line = f"| `{key}` | `{sha256_file(path)}` | {path.stat().st_size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


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
        rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                    f"{path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start = text.index(README_MARKERS["artifacts"][0])
    end = text.index(README_MARKERS["artifacts"][1], start) + \
        len(README_MARKERS["artifacts"][1])
    return text[:start] + block + text[end:]


# ---------------------------------------------------------------------------
# Strict rejection self-checks
# ---------------------------------------------------------------------------


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = [
        '{"a":1,"a":2}',
        '{"a": NaN}',
        '{"a": Infinity}',
        '[]',
        '{"a":1} trailing',
    ]
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except ValueError:
            rejected_json += 1
    bad_pins = [
        "not-a-pin",
        "0" * 64 + " source:one",
        "0" * 63 + "  source:one",
        "\n".join(["0" * 64 + "  source:one", "0" * 64 + "  source:one"]),
        "0" * 64 + "  other:one",
    ]
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected_pins += 1
    bad_readme = [
        "# no tables",
        "<!-- digest-table: source -->\n| `source:x` | `zz` |\n"
        "<!-- digest-table: end -->",
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
        "| `a` | `" + "0" * 64 + "` |\n<!-- DIGEST_TABLE_ARTIFACTS_END -->",
    ]
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except ValueError:
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }


# ---------------------------------------------------------------------------
# Task-local git scope
# ---------------------------------------------------------------------------
# The merge-base comparison contains exactly this branch's commits. A fixed
# historical base would report later sibling merges on main as out-of-scope.
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> Optional[str]:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> Optional[str]:
    """Newest merge-base between HEAD and an available PR base ref."""
    best: Optional[str] = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


if board_row_digest() != BOARD_ROW_STABLE_SHA256:
    raise RuntimeError("stable linked-row identity drift")
