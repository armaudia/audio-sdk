# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the ROSE-CD EARS-Reverb task.

This package is feasibility evidence only. It models a caller-supplied-asset
tool boundary and synthetic room/reverb controls, but it does not implement,
download, load or execute ROSE-CD. No EARS-Reverb checkpoint, measured RIR,
real audio, listening result, device timing or benchmark result is included.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/rose-cd-ears-reverb/caller-supplied/0.1"
TASK_ID = "SDK-ROSE-CD-EARS-REVERB-CONFIGURATION"
TITLE = "ROSE-CD EARS-Reverb configuration"
COMPONENT = "rose-cd-ears-reverb-configuration"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "56eeb134b740d41d770940bf47bd0f035d73f097"
BRANCH = "swarm/SDK-ROSE-CD-EARS-REVERB-CONFIGURATION"
REVIEWER = "reviewer-ROSE-CD-EARS-REVERB-CONFIGURATION"
PROFILE = "room"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_synthetic_incomplete"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500

EVIDENCE_PATH = "research/dereverberation_candidates_20261028.md"
EVIDENCE_LINE = 24
EVIDENCE_TEXT = (
    "- **ROSE-CD one-step consistency model**: upstream reports an "
    "EARS-Reverb dereverberation comparison (PESQ 2.69, ESTOI .82, "
    "WER 15.78%) for a one-step model. The local checkpoint is from "
    "VoiceBank-DEMAND; the EARS-Reverb values are cross-domain upstream "
    "evidence, not evidence from this exact checkpoint. It is a large "
    "utterance-level model and the local CPU screen was too slow to "
    "qualify for real-time use."
)

SOURCE_PINS: Dict[str, str] = {
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/voice-enhancement-20261101/evaluation_records.md":
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "adapters/rose-cd/README.md":
        "988d1d87847910e13f65ce8e5380c3f76ed9f4be924789be6b9e80ab14719b72",
    "data/checkouts/ROSE-CD/README.md":
        "8ebab9ccee56cac770a3e36a4c8ade1b812a3f6b9736e093b5bf2a9596509fa3",
    "data/checkouts/ROSE-CD/LICENSE":
        "1065d138be7bfe31684e9f1c0bf8446ce7178299a7681746c50d2315f96b0ebd",
    "data/checkouts/ROSE-CD/config.json":
        "815d6cec4ea0c9492db0b477af30397b92ce577f1823faf43b82d1e7acb2c22a",
    "data/checkouts/ROSE-CD/scripts/eval_CT.sh":
        "3e422ef8f5e8610def9ab59b530f1534cdad534b92b05d1fac946d08f81c069c",
    "data/checkouts/ROSE-CD/sgmse/data_module.py":
        "fbe913c9fad0b68bebe29058a6943b8115d74dfa2532e7856d890cd87987eb0b",
    "data/checkouts/ROSE-CD/sgmse/util/other.py":
        "092efb6e7da82d11c0afa555e5b124dd950e1216237e1c165a3aea8d4551ffd0",
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/rose-cd-one-step/README.md":
        "a8d8c9face90e0ff6827331a12ba3ea7f7ebe2186b67df10d9813457fe286629",
    "docs/task-evidence/rose-cd-one-step/report.json":
        "b27062d674d20673fb9b4b917fb323491b11965ada474246def23585ccd94e25",
    "docs/task-evidence/rose-cd-rms-matched/README.md":
        "12922d21b8d90a3d6761c04c8ca8013ec42435d5a6b7331bc31a2c2d5c1e7dd4",
    "docs/task-evidence/rose-cd-rms-matched/report.json":
        "bc40973710ccd9d5e462ce20ebc75027a93d4effe72ce8de4ce54885bf854b90",
    "docs/task-evidence/localvqe-dereverberation-probe/README.md":
        "ad9706a7eddb0d73945c9944cf4cca90c6e245d13ad5d23c567f64e9a648048f",
    "docs/task-evidence/localvqe-dereverberation-probe/report.json":
        "8ce127dd2e3ac1982d0d6b7426facb2d5f4cbf26b937ae4ec5940301708ee9d8",
}

BOARD_STABLE_SHA256 = (
    "b376bc56299b2d4db72c50a43f00cc71da59ee58f668c64d724af67465b4b37f"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)

TASK_PREFIX = "docs/task-evidence/rose-cd-ears-reverb-configuration/"
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

VOICEBANK_CHECKPOINT = {
    "artifact": "logs/CT_pesq5e-4_L2/8ar2h6zv/last.ckpt",
    "revision": "1c80e0863c1a8682f52a8e5be2efdf58a130eb62",
    "byte_count": 1313064415,
    "sha256": "5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4",
    "training_condition": "VoiceBank-DEMAND",
    "present_locally": False,
    "note": "Pinned additive-noise checkpoint; not EARS-Reverb matched evidence.",
}
SOURCE_CHECKOUT = {
    "path": "data/checkouts/ROSE-CD",
    "revision": "8a7477f046a133737d6f1744b643fbe3f3ea96cd",
    "license": "MIT",
    "present_locally": True,
    "note": "Pinned source files are read-only pins; no source is imported or executed.",
}
ASSET_LEDGER = {
    "status": "absent_exact_ears_reverb_checkpoint_unidentified",
    "source_checkout": SOURCE_CHECKOUT,
    "voicebank_checkpoint": VOICEBANK_CHECKPOINT,
    "ears_reverb_checkpoint": {
        "artifact": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": (
            "Linked evidence reports EARS-Reverb scores but does not pin an "
            "EARS-Reverb checkpoint identity, revision or digest."
        ),
    },
    "measured_rir": {
        "status": "absent",
        "byte_count": None,
        "sha256": None,
        "note": "No real or measured RIR is staged; synthetic taps are generated in memory.",
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": "No Python/PyTorch/PyTorch-Lightning lockfile or offline loader is staged.",
    },
    "rights": {
        "status": "unreviewed",
        "note": (
            "MIT source text does not clear checkpoint, EARS CC BY-NC 4.0, "
            "RIR terms, product-use or derivative-output rights."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
}

BOUNDARY = {
    "benchmark_claim": False,
    "board_or_handoff_changed": False,
    "ci_changed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "processor_exposure": False,
    "provider_registered": False,
    "public_api_abi_changed": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
    "format": {
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
    },
}

SCOPE = {
    "synthetic_only": True,
    "task_local_only": True,
    "real_rir": False,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "model_executed": False,
    "checkpoint_loaded": False,
    "network_used": False,
}

NEGATIVE_CLAIMS = [
    "No ROSE-CD source is imported, built or executed by this package.",
    "No EARS-Reverb checkpoint or VoiceBank checkpoint bytes are present or loaded.",
    "No measured RIR, EARS-Reverb split, real recording or listening result is present.",
    "Synthetic RIR/reverb controls are not real room or listening evidence.",
    "Upstream EARS-Reverb scores are source-reported and not local measurements.",
    "No device timing, benchmark result, release claim or provider exposure is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES = [
    {
        "id": "RG-01",
        "title": "exact_source_checkpoint_runtime_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "The exact EARS-Reverb source revision, checkpoint path, byte count, SHA-256 and runtime lockfile must be pinned.",
        "reopen_condition": "Stage and review the immutable EARS-Reverb checkpoint identity and locked offline runtime.",
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Caller asset identity, configuration, rate, channels, frame, hop, STFT, delay and drain geometry must be verified without loading an asset.",
        "reopen_condition": "Pass a hash-matched caller manifest against the exact pinned EARS-Reverb geometry and reproduce byte-level output.",
    },
    {
        "id": "RG-03",
        "title": "rights_and_terms",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Code, checkpoint, EARS corpus, RIR and output-use rights require explicit review.",
        "reopen_condition": "Reviewed rights records clear code, weights, data, RIR terms and product use.",
    },
    {
        "id": "RG-04",
        "title": "frozen_room_geometry_and_conditions",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Freeze render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise and reset schedule for the exact task.",
        "reopen_condition": "A rights-cleared pinned RIR/render cohort with declared geometry and reset schedule is staged.",
    },
    {
        "id": "RG-05",
        "title": "room_profile_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Measure echo attenuation, near-end damage, nonfinite failures, alignment and delayed/missing render on matched conditions with an independent no-reference comparison.",
        "reopen_condition": "Matched room outcomes are produced with pinned scorers and independent controls.",
    },
    {
        "id": "RG-06",
        "title": "matched_cohort_scorer_and_listening",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "A rights-cleared EARS-Reverb cohort, pinned ASR/STOI/PESQ/SI-SDR scorers and blinded listening must be separate from the VoiceBank screen.",
        "reopen_condition": "Held-out task-matched qualitative and quantitative evidence is reviewed independently.",
    },
    {
        "id": "RG-07",
        "title": "timing_resources_and_state",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Availability, algorithmic delay, whole-clip finalization, paced runtime, peak/memory and reset behavior require measurement on the exact runtime.",
        "reopen_condition": "Target-runtime pacing, state, memory and content-delay evidence is collected and reviewed.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Opt-in provider intake, independent exact-head review and release approval are required before any exposure.",
        "reopen_condition": "A separate versioned intake passes independent review with OFF default and explicit approval.",
    },
]

EXACT_BLOCKERS = [
    {
        "id": "XB-01",
        "title": "ears_reverb_checkpoint_identity_absent",
        "detail": (
            "The linked research reports upstream EARS-Reverb scores but pins no "
            "EARS-Reverb checkpoint path, revision, byte count or SHA-256. The only "
            "pinned checkpoint is the absent VoiceBank-DEMAND CT checkpoint."
        ),
        "reopen": (
            "Stage the exact licensed EARS-Reverb checkpoint with immutable "
            "revision, byte count and SHA-256, then verify it against the cited upstream artifact."
        ),
    },
    {
        "id": "XB-02",
        "title": "matched_runtime_and_geometry_unpinned",
        "detail": (
            "No Python/PyTorch/PyTorch-Lightning lockfile, offline loader or "
            "EARS-Reverb-specific STFT, hop, delay, frame and finalization geometry is pinned."
        ),
        "reopen": "Pin the exact runtime and EARS-Reverb geometry, then reproduce byte-level output.",
    },
    {
        "id": "XB-03",
        "title": "matched_room_assets_and_rights_absent",
        "detail": (
            "No EARS-Reverb split, clean/reference pair, measured RIR, ASR transcript "
            "scorer or rights review is staged. The local EARS archive lacks split provenance."
        ),
        "reopen": "Stage rights-cleared matched room assets with pinned scorers and a reviewed protocol.",
    },
    {
        "id": "XB-04",
        "title": "room_profile_and_release_gates_unmet",
        "detail": (
            "No real room evidence, device timing, listening, benchmark, opt-in "
            "intake or independent release review exists."
        ),
        "reopen": "Complete the room profile on the exact runtime and pass independent opt-in review.",
    },
]

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "checkpoint_path", "checkpoint_sha256",
    "checkpoint_byte_count", "checkpoint_revision", "source_dir",
    "source_revision", "sample_rate_hz", "channels", "frame_samples",
    "hop_samples", "stft_n_fft", "sampler_type", "steps", "runtime_lock_digest",
)

SINE64: Tuple[int, ...] = (
    0, 3212, 6393, 9512, 12539, 15446, 18204, 20787,
    23170, 25329, 27245, 28898, 30273, 31356, 32137, 32609,
    32767, 32609, 32137, 31356, 30273, 28898, 27245, 25329,
    23170, 20787, 18204, 15446, 12539, 9512, 6393, 3212,
    0, -3212, -6393, -9512, -12539, -15446, -18204, -20787,
    -23170, -25329, -27245, -28898, -30273, -31356, -32137, -32609,
    -32767, -32609, -32137, -31356, -30273, -28898, -27245, -25329,
    -23170, -20787, -18204, -15446, -12539, -9512, -6393, -3212,
)
CLIP_SAMPLES = 1600
RIR_TAPS = 1600
EARLY_END_SAMPLE = 800
RENDER_DELAY_SAMPLES = 160
SYNTH_SEED = 20261126
SYNTH_SCALE = 32768


class ReferenceRejection(ValueError):
    """Deterministic machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
    """Reject duplicate keys, nonfinite constants and unsupported values."""

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


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Strict SHA-256 manifest parser; rejects duplicate or unsafe keys."""

    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: Dict[str, str] = {}
    result: List[Tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        if key.startswith("source:"):
            relative = key.split(":", 1)[1]
        else:
            relative = key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(
        sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    """Parse the two fenced digest tables in README.md."""

    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0],
                  text.split(middle, 1)[1].split(end, 1)[0]):
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
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
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


def evidence_entry() -> Dict[str, Any]:
    path = SOURCE_ROOT / EVIDENCE_PATH
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines[EVIDENCE_LINE - 1].strip() != EVIDENCE_TEXT:
        raise ValueError("evidence_line_mismatch")
    return {
        "path": EVIDENCE_PATH,
        "line": EVIDENCE_LINE,
        "sha256": sha256_file(path),
        "text": EVIDENCE_TEXT,
        "note": (
            "Cross-domain upstream report only; not a local measurement and "
            "not produced by the locally pinned VoiceBank checkpoint."
        ),
    }


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file():
            raise ValueError("missing_source_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            raise ValueError("missing_boundary_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate caller-supplied metadata only; never load or execute an asset."""

    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST", "manifest must be object")
    keys = set(manifest)
    expected = set(CALLER_MANIFEST_FIELDS)
    if keys != expected:
        if keys - expected:
            raise ReferenceRejection("UNKNOWN_FIELD", "extra manifest fields")
        raise ReferenceRejection("MISSING_FIELD", "missing manifest fields")
    if manifest["adapter"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("UNKNOWN_ADAPTER", "unsupported adapter ID")
    if manifest["configuration_id"] != "ears-reverb-one-step":
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported configuration")
    if manifest["source_revision"] != SOURCE_CHECKOUT["revision"]:
        raise ReferenceRejection("SOURCE_REVISION_MISMATCH", "source revision mismatch")
    if (manifest["sample_rate_hz"] != SAMPLE_RATE_HZ
            or manifest["channels"] != CHANNELS
            or manifest["frame_samples"] != FRAME_SAMPLES):
        raise ReferenceRejection("FORMAT_MISMATCH", "installed v0 format mismatch")
    if manifest["hop_samples"] != 128 or manifest["stft_n_fft"] != 510:
        raise ReferenceRejection("GEOMETRY_UNPINNED", "source-derived STFT geometry mismatch")
    if manifest["sampler_type"] != "stochastic" or manifest["steps"] != 1:
        raise ReferenceRejection("SAMPLER_MISMATCH", "sampler settings mismatch")
    if not isinstance(manifest["checkpoint_path"], str) or not Path(
            manifest["checkpoint_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_CHECKPOINT", "checkpoint path must be absolute")
    if not isinstance(manifest["source_dir"], str) or not Path(
            manifest["source_dir"]).is_absolute():
        raise ReferenceRejection("RELATIVE_SOURCE", "source directory must be absolute")
    if not isinstance(manifest["checkpoint_sha256"], str) or not re.fullmatch(
            r"[0-9a-f]{64}", manifest["checkpoint_sha256"]):
        raise ReferenceRejection("BAD_CHECKPOINT_DIGEST", "checkpoint SHA-256 malformed")
    if (not isinstance(manifest["checkpoint_byte_count"], int)
            or isinstance(manifest["checkpoint_byte_count"], bool)
            or manifest["checkpoint_byte_count"] <= 0):
        raise ReferenceRejection("BAD_BYTE_COUNT", "checkpoint byte count malformed")
    if (not isinstance(manifest["checkpoint_revision"], str)
            or not manifest["checkpoint_revision"].strip()):
        raise ReferenceRejection("MISSING_CHECKPOINT_REVISION", "revision required")
    if (not isinstance(manifest["runtime_lock_digest"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", manifest["runtime_lock_digest"])):
        raise ReferenceRejection("BAD_RUNTIME_DIGEST", "runtime lock digest malformed")

    checkpoint = Path(manifest["checkpoint_path"])
    if not checkpoint.is_file():
        raise ReferenceRejection("ASSET_ABSENT", "declared checkpoint is absent")
    if sha256_file(checkpoint) != manifest["checkpoint_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "checkpoint SHA-256 mismatch")
    if checkpoint.stat().st_size != manifest["checkpoint_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "checkpoint byte count mismatch")
    if not Path(manifest["source_dir"]).is_dir():
        raise ReferenceRejection("SOURCE_ABSENT", "declared source directory is absent")
    raise ReferenceRejection(
        "EARS_CHECKPOINT_IDENTITY_UNPINNED",
        "hash-matched caller asset is still not the pinned EARS-Reverb checkpoint")


def valid_manifest(checkpoint_path: str = "/absent/checkpoint.ckpt") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": "ears-reverb-one-step",
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": VOICEBANK_CHECKPOINT["sha256"],
        "checkpoint_byte_count": VOICEBANK_CHECKPOINT["byte_count"],
        "checkpoint_revision": VOICEBANK_CHECKPOINT["revision"],
        "source_dir": str(SOURCE_ROOT / "data/checkouts/ROSE-CD"),
        "source_revision": SOURCE_CHECKOUT["revision"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "hop_samples": 128,
        "stft_n_fft": 510,
        "sampler_type": "stochastic",
        "steps": 1,
        "runtime_lock_digest": "0" * 64,
    }


def validate_reset(new_epoch: Any, first_sample: Any, current_epoch: int) -> Dict[str, Any]:
    if not isinstance(new_epoch, int) or isinstance(new_epoch, bool) or new_epoch < 0:
        raise ReferenceRejection("BAD_EPOCH", "invalid epoch")
    if (not isinstance(first_sample, int) or isinstance(first_sample, bool)
            or first_sample < 0):
        raise ReferenceRejection("BAD_POSITION", "invalid first input sample")
    if new_epoch <= current_epoch:
        raise ReferenceRejection("EPOCH_NOT_INCREASING", "epoch must increase")
    return {"accepted": True, "epoch": new_epoch, "first_input_sample": first_sample}


def _lcg(seed: int) -> Iterable[int]:
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state


def synthetic_rir_q15() -> List[int]:
    taps = [0] * RIR_TAPS
    taps[0] = 16384
    for index in (160, 320, 480, 640):
        taps[index] = 8192 // (index // 160)
    rng = _lcg(SYNTH_SEED)
    for index in range(1, RIR_TAPS):
        if taps[index]:
            continue
        value = next(rng) % 2001 - 1000
        decay = 1 << (index // 200)
        taps[index] = value // decay
    return taps


def synthetic_dry_q15() -> List[int]:
    dry: List[int] = []
    for index in range(CLIP_SAMPLES):
        envelope = 12000 if (index // 160) % 4 in (0, 1) else 1800
        tone = 3 * SINE64[index % 64] + SINE64[(2 * index) % 64]
        dry.append((envelope * tone) // (4 * SYNTH_SCALE))
    return dry


def convolve_q15(signal: Sequence[int], taps: Sequence[int]) -> List[int]:
    output = [0] * len(signal)
    for index in range(len(signal)):
        total = 0
        limit = min(index + 1, len(taps))
        for tap in range(limit):
            total += signal[index - tap] * taps[tap]
        output[index] = max(-32768, min(32767, total // SYNTH_SCALE))
    return output


def _stats(values: Sequence[int]) -> Dict[str, Any]:
    if not values:
        raise ValueError("empty_synthetic_signal")
    peak = max(abs(value) for value in values) / SYNTH_SCALE
    rms = math.sqrt(sum(value * value for value in values) / len(values)) / SYNTH_SCALE
    return {
        "sample_count": len(values),
        "digest": object_digest([int(value) for value in values]),
        "peak_abs": round(peak, 9),
        "rms": round(rms, 9),
        "nonfinite_count": 0,
        "out_of_range_count": sum(1 for value in values if not -32768 <= value <= 32767),
    }


def _oracle_gate(values: Sequence[int]) -> List[int]:
    gated = list(values)
    for index in range(EARLY_END_SAMPLE, CLIP_SAMPLES):
        if (index // 160) % 4 in (2, 3):
            gated[index] = (gated[index] * 250) // 1000
    return gated


def synthetic_room() -> Dict[str, Any]:
    taps = synthetic_rir_q15()
    dry = synthetic_dry_q15()
    early_taps = list(taps[:EARLY_END_SAMPLE])
    late_taps = [0] * EARLY_END_SAMPLE + list(taps[EARLY_END_SAMPLE:])
    early = convolve_q15(dry, early_taps)
    echo_only = convolve_q15(dry, late_taps)
    overlap = [max(-32768, min(32767, early[index] + echo_only[index]))
               for index in range(CLIP_SAMPLES)]
    gated = _oracle_gate(overlap)
    late_energy = sum(value * value for value in echo_only[EARLY_END_SAMPLE:])
    overlap_late_energy = sum(value * value for value in overlap[EARLY_END_SAMPLE:])
    attenuation = 0.0 if late_energy == 0 else 20 * math.log10(
        max(1, late_energy) / max(1, overlap_late_energy))
    conditions = {
        "dry_only_near_end": _stats(dry),
        "echo_only": _stats(echo_only),
        "overlap": _stats(overlap),
        "early_target": _stats(early),
        "no_reference": _stats(overlap),
        "oracle_late_gate": _stats(gated),
    }
    return {
        "label": "synthetic room/reverb controls; not real RIR or listening evidence",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "clip_samples": CLIP_SAMPLES,
        "rir_taps": RIR_TAPS,
        "early_window_samples": EARLY_END_SAMPLE,
        "early_window_ms": 50.0,
        "seed": SYNTH_SEED,
        "render_delay_samples": RENDER_DELAY_SAMPLES,
        "excitation": "integer three-tone syllable envelope",
        "movement": "none; fixed synthetic source and receiver",
        "noise": "none in synthetic room controls",
        "reset_schedule": "epoch strictly increasing; state is model-free",
        "rir_digest": object_digest(taps),
        "conditions": conditions,
        "oracle_late_attenuation_db": round(attenuation, 9),
        "oracle_note": (
            "Oracle gate uses the known synthetic speech activity pattern; "
            "it is not a dereverberation model and cannot qualify ROSE-CD."
        ),
        "identity_control": {
            "early_target_byte_identical": True,
            "dry_only_byte_identical": True,
        },
    }


def alignment_probe() -> Dict[str, Any]:
    return {
        "label": "synthetic interval mapping only; no measured content delay",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_SAMPLES * SAMPLE_NS,
        "render_delay_samples": RENDER_DELAY_SAMPLES,
        "source_first_sample_example": -RENDER_DELAY_SAMPLES,
        "direct_peak_output_offset": RENDER_DELAY_SAMPLES,
        "early_window": [0, EARLY_END_SAMPLE],
        "late_window": [EARLY_END_SAMPLE, CLIP_SAMPLES],
        "shift_probes": [
            {"shift_samples": 0, "accepted": True},
            {"shift_samples": -RENDER_DELAY_SAMPLES, "accepted": False},
            {"shift_samples": RENDER_DELAY_SAMPLES, "accepted": False},
        ],
        "delayed_render": "modelled as fixed integer offset; not measured",
        "missing_render": "blocked; no render signal available in this package",
    }


def state_probe() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    checks = (
        ("fresh_epoch_2", (2, 0, 1), True),
        ("equal_epoch", (1, 0, 1), False),
        ("lower_epoch", (0, 0, 1), False),
        ("negative_epoch", (-1, 0, 1), False),
        ("negative_position", (2, -1, 1), False),
        ("bool_epoch", (True, 0, 1), False),
    )
    for name, args, expected in checks:
        try:
            validate_reset(*args)
            accepted = True
        except ReferenceRejection:
            accepted = False
        cases.append({"id": name, "accepted": accepted, "expected": expected})
    dry = synthetic_dry_q15()
    joined = [value for frame in range(0, CLIP_SAMPLES, FRAME_SAMPLES)
              for value in dry[frame:frame + FRAME_SAMPLES]]
    return {
        "cases": cases,
        "matches_expectation": all(item["accepted"] == item["expected"] for item in cases),
        "state_owned": False,
        "chunk_invariance_digest": object_digest(joined),
        "chunk_invariance_exact": joined == dry,
        "note": "Model-free fixture state only; no provider state or checkpoint state exists.",
    }


def adverse_cases() -> Dict[str, Any]:
    base = valid_manifest()
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, mutate: Any, code: str) -> None:
        manifest = dict(base)
        try:
            mutate(manifest)
            validate_caller_manifest(manifest)
            observed = "UNEXPECTED_ACCEPT"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"id": case_id, "expected": code, "observed": observed,
                      "accepted": observed == "UNEXPECTED_ACCEPT"})

    add("missing_field", lambda m: m.pop("steps"), "MISSING_FIELD")
    add("unknown_field", lambda m: m.update(extra=1), "UNKNOWN_FIELD")
    add("wrong_adapter", lambda m: m.update(adapter="other"), "UNKNOWN_ADAPTER")
    add("wrong_configuration", lambda m: m.update(configuration_id="raw"),
        "UNKNOWN_CONFIGURATION")
    add("wrong_source_revision", lambda m: m.update(source_revision="deadbeef"),
        "SOURCE_REVISION_MISMATCH")
    add("wrong_rate", lambda m: m.update(sample_rate_hz=48000), "FORMAT_MISMATCH")
    add("wrong_channels", lambda m: m.update(channels=2), "FORMAT_MISMATCH")
    add("wrong_frame", lambda m: m.update(frame_samples=320), "FORMAT_MISMATCH")
    add("wrong_hop", lambda m: m.update(hop_samples=256), "GEOMETRY_UNPINNED")
    add("wrong_n_fft", lambda m: m.update(stft_n_fft=512), "GEOMETRY_UNPINNED")
    add("wrong_sampler", lambda m: m.update(sampler_type="teacher"), "SAMPLER_MISMATCH")
    add("wrong_steps", lambda m: m.update(steps=30), "SAMPLER_MISMATCH")
    add("relative_checkpoint", lambda m: m.update(checkpoint_path="last.ckpt"),
        "RELATIVE_CHECKPOINT")
    add("absent_checkpoint", lambda m: None, "ASSET_ABSENT")
    add("bad_checkpoint_digest", lambda m: m.update(checkpoint_sha256="abc"),
        "BAD_CHECKPOINT_DIGEST")
    add("bad_byte_count", lambda m: m.update(checkpoint_byte_count=True),
        "BAD_BYTE_COUNT")
    add("bad_runtime_digest", lambda m: m.update(runtime_lock_digest="xyz"),
        "BAD_RUNTIME_DIGEST")
    try:
        validate_caller_manifest([])
        observed = "UNEXPECTED_ACCEPT"
    except ReferenceRejection as error:
        observed = error.code
    cases.append({"id": "manifest_not_object", "expected": "INVALID_MANIFEST",
                  "observed": observed, "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {
        "case_count": len(cases),
        "accepted_count": good,
        "all_rejected": good == 0,
        "cases": cases,
        "metrics": None,
        "note": "All caller manifests fail closed before any asset load or execution.",
    }


def invalid_json_cases() -> Dict[str, Any]:
    texts = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_constant": '{"a":NaN}',
        "infinity_constant": '{"a":Infinity}',
        "negative_infinity_constant": '{"a":-Infinity}',
        "trailing_data": '{"a":1} extra',
        "invalid_syntax": '{"a":}',
        "empty_text": "",
    }
    cases: List[Dict[str, Any]] = []
    for name, text in texts.items():
        try:
            strict_loads(text)
            observed = "UNEXPECTED_ACCEPT"
        except ValueError:
            observed = "INVALID_JSON"
        cases.append({"id": name, "observed": observed,
                      "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good,
            "all_rejected": good == 0, "cases": cases, "metrics": None}


def invalid_pin_cases() -> Dict[str, Any]:
    texts = {
        "duplicate_key": "a" * 64 + "  source:duplicate\n" + "a" * 64 + "  source:duplicate\n",
        "short_digest": "abc  source:short\n",
        "missing_separator": "a" * 64 + " source:missing\n",
        "absolute_path": "a" * 64 + "  /absolute/path\n",
        "traversal": "a" * 64 + "  source:../escape\n",
    }
    cases: List[Dict[str, Any]] = []
    for name, text in texts.items():
        try:
            parse_pin_lines(text)
            observed = "UNEXPECTED_ACCEPT"
        except ValueError:
            observed = "INVALID_PIN"
        cases.append({"id": name, "observed": observed,
                      "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good,
            "all_rejected": good == 0, "cases": cases}


def absent_artifact_probe() -> Dict[str, Any]:
    candidates = (
        "data/models/rose-cd-ears-reverb/last.ckpt",
        "data/checkpoints/rose-cd-ears-reverb",
        "data/rirs/ears-reverb",
        "data/corpora/ears-reverb",
        "data/envs/rose-cd-ears-reverb",
        "adapters/rose-cd-ears-reverb",
    )
    found = [path for path in candidates if (SOURCE_ROOT / path).exists()]
    sdk_found = [path for path in candidates if (SDK_ROOT / path).exists()]
    return {
        "workspace_candidates": list(candidates),
        "workspace_found": found,
        "sdk_worktree_found": sdk_found,
        "present": bool(found or sdk_found),
        "note": "Bounded read-only path probes; no download, import or load was attempted.",
    }


def source_reported() -> Dict[str, Any]:
    return {
        "evidence": evidence_entry(),
        "ears_reverb_upstream": {
            "model": "ROSE-CD one-step consistency model",
            "parameters_million": 59.62,
            "gmacs_per_second": 132.88,
            "steps": 1,
            "wer_percent": 15.78,
            "pesq": 2.69,
            "si_sdr_db": -13.9,
            "estoi": 0.82,
            "dimos": 3.75,
            "wvmos": 2.70,
            "nisqa": 3.14,
            "scoreq": 2.66,
        },
        "voicebank_checkpoint": dict(VOICEBANK_CHECKPOINT),
        "separation": (
            "Upstream EARS-Reverb predictions are cross-domain source-reported "
            "evidence. They are not local outputs and are not evidence from the "
            "pinned VoiceBank-DEMAND checkpoint."
        ),
        "qualifies": False,
        "listening_performed_here": False,
    }


def room_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "frozen_render_or_measured_rir": {
                "status": "blocked",
                "evidence": "No pinned real render/reference or measured RIR is staged.",
            },
            "channel_rate_hop_excitation_delay_movement_noise_reset": {
                "status": "synthetic_only",
                "evidence": "Frozen integer fixture; no device or room measurement.",
            },
            "echo_only": {"status": "synthetic_only", "evidence": "Late-tap-only synthetic case."},
            "near_end_only": {"status": "synthetic_only", "evidence": "Dry-only synthetic case."},
            "overlap": {"status": "synthetic_only", "evidence": "Dry plus synthetic early/late taps."},
            "no_reference": {
                "status": "synthetic_only_no_score",
                "evidence": "No-reference case is recorded without a quality score.",
            },
            "echo_attenuation": {
                "status": "synthetic_oracle_only",
                "evidence": "Oracle gate on known synthetic activity; not ROSE-CD.",
            },
            "near_end_damage": {
                "status": "synthetic_oracle_only",
                "evidence": "Dry-region peak/RMS controls only.",
            },
            "nonfinite_failures": {
                "status": "synthetic_only",
                "evidence": "Integer fixture and strict adverse cases only.",
            },
            "alignment": {"status": "synthetic_only", "evidence": "Fixed integer render offset."},
            "delayed_or_missing_render": {
                "status": "synthetic_only",
                "evidence": "Fixed offset modelled; missing render is explicitly blocked.",
            },
            "no_reference_suppressor_independent_comparison": {
                "status": "blocked",
                "evidence": "No no-reference suppressor checkpoint or scorer is pinned.",
            },
            "matched_heldout_room_qualification": {
                "status": "blocked",
                "evidence": "No rights-cleared EARS-Reverb split, RIR cohort or scorer is staged.",
            },
        },
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    room = synthetic_room()
    align = alignment_probe()
    state = state_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    probe = absent_artifact_probe()
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(BOUNDARY["format"]),
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "configuration_id": "ears-reverb-one-step",
            "source_revision": SOURCE_CHECKOUT["revision"],
            "source_derived_stft": {"n_fft": 510, "hop_samples": 128, "window": "hann"},
            "sampler": {"type": "stochastic", "steps": 1},
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata-only reference. A hash-matched caller asset still "
                "fails as EARS_CHECKPOINT_IDENTITY_UNPINNED."
            ),
        },
        "asset_resolution": probe,
        "synthetic_room": room,
        "room_profile": room_profile(),
        "availability": {
            "status": "modelled_not_measured",
            "clock": "fixture-monotonic-not-device",
            "whole_clip_available_after_final_sample": True,
            "device_timing": False,
            "streaming_result": False,
            "content_delay_claim": False,
        },
        "alignment": align,
        "state": state,
        "controls": {
            "identity": {"status": "bit_exact_synthetic_only", "qualifies": False},
            "no_reference": {"status": "recorded_without_score", "qualifies": False},
            "oracle_late_gate": {"status": "synthetic_oracle_only", "qualifies": False},
            "independent_instances": {"status": "model_free", "qualifies": False},
        },
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (manifest_adverse["all_rejected"]
                             and json_adverse["all_rejected"]
                             and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_matched_ears_reverb_checkpoint_or_rir",
            "identity_control": "synthetic only",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "model_provenance": {
            "source_revision": SOURCE_CHECKOUT["revision"],
            "source_license": SOURCE_CHECKOUT["license"],
            "voicebank_checkpoint": dict(VOICEBANK_CHECKPOINT),
            "ears_reverb_checkpoint": dict(ASSET_LEDGER["ears_reverb_checkpoint"]),
            "runtime": dict(ASSET_LEDGER["runtime"]),
        },
        "licensing_analysis": {
            "source_license": "MIT (pinned LICENSE text)",
            "checkpoint_terms": "unreviewed",
            "ears_corpus_terms": "CC BY-NC 4.0 research-only per linked evidence",
            "rir_terms": "unclear upstream; not redistributed",
            "product_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact EARS-Reverb checkpoint identity, bytes and runtime",
            "rights-cleared matched EARS-Reverb split, RIR and references",
            "matched room outcomes on the exact runtime",
            "independent listening and device timing",
            "opt-in provider intake and release approval",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "real_local_model_output": False,
            "real_rir": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
        },
        "board_link": board_link(),
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-ROSE-CD-EARS-REVERB-CONFIGURATION.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
        "# The mutable full plan/swarm/TASKS.json is never pinned; only stable row identity is gated.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(SOURCE_PINS[path] + "  source:" + path)
    for path in sorted(BOUNDARY_PINS):
        lines.append(BOUNDARY_PINS[path] + "  " + path)
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes,
                   sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        artifact_pins[TASK_PREFIX + name] = sha256_bytes(payload)
    contract: Dict[str, Any] = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "contract_version": "0.1",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "artifact_pins": artifact_pins,
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "board_link": board_link(),
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Only the task-local evidence directory is written.",
            "No source, checkpoint, RIR, audio or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "Synthetic room controls are labelled and cannot qualify the candidate.",
            "Only stable board-row identity enters canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base of HEAD with an available PR base ref."""

    best: str | None = None
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
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
