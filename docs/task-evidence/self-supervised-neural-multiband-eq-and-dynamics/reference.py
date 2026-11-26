# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for NDMP AutoEQ feasibility.

This package is feasibility evidence only. It models a caller-supplied-asset
boundary and synthetic DSP controls at the installed 16 kHz mono float32
160-sample geometry. It does not implement, download, load or execute the
DAFx-2025 Neural-Driven Multi-Band Processor, and it contains no model weights,
real audio, listening result, device timing or benchmark result.
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
SCHEMA_MANIFEST = "audio-sdk/ndmp-autoeq/caller-supplied/0.1"
TASK_ID = "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS"
TITLE = "Self-supervised neural multiband EQ and dynamics"
COMPONENT = "self-supervised-neural-multiband-eq-and-dynamics"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "a51e49f718500ec9e81242cf2816f0b576333d00"
BRANCH = "swarm/SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS"
REVIEWER = "reviewer-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS"
PROFILE = "dsp"
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

EVIDENCE_PATH = "research/level_tone_control_20261028.md"
EVIDENCE_LINE = 24
EVIDENCE_TEXT = (
    "- Neural parametric EQ matching with differentiable biquads shows learned "
    "prediction of EQ parameters as a relevant tone-control family. [DAFx 2020 "
    "paper](https://dafx2020.mdw.ac.at/proceedings/papers/DAFx2020_paper_7.pdf). "
    "A later neural multiband processor proposes self-supervised automatic EQ "
    "plus dynamics processing. [DAFx 2025 "
    "paper](https://dafx.de/paper-archive/details/AvUulq3fVM5yMf35-alPvQ)."
)

SOURCE_PINS: Dict[str, str] = {
    "research/level_tone_control_20261028.md":
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/level-tone/20261028-synthetic-evaluation.json":
        "1054a0b6d22dac695e17dfa84ab21f9f2a1677838285fb746834010424b91c34",
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/survey-cln-10/README.md":
        "f63847915ab78d50bccd73bdcffdcbf625faef2b6312024e8ede21bb2635a787",
    "docs/task-evidence/survey-cln-10/report.json":
        "90c1b2472e8547d3ff78d67d6d0db60b912be5befd6ef4fa4e289cf406642bd5",
    "docs/task-evidence/differentiable-biquad-neural-parametric-eq/README.md":
        "3d1959a7a925b6c432460068b3e28af2ff5b91ce6e4b08ea488f488d0e5ae470",
    "docs/task-evidence/differentiable-biquad-neural-parametric-eq/report.json":
        "fd02a76b9a5d2fdef3df69c4603f8dfe96dcde800a20f163abc18d10bce6557b",
    "docs/task-evidence/learned-inverse-eq/README.md":
        "719910254b5399b79e20208cff40ff6920fe12b77813731b70c0c6abd833b20e",
    "docs/task-evidence/learned-inverse-eq/report.json":
        "2ee8271a3b08c989fe037f2753d013b8e6dcafb6881e5b0e59bb6724eff9e0dc",
    "docs/task-evidence/fixed-six-band-spectral-tilt/README.md":
        "70b2edcd154821445a5ff24f430b19fc42dac3cec8273a9baae896e3245f56de",
    "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json":
        "2673433a9db9ac348d3624b73a739196815374ccb68aa4427aee53b94702826c",
}

BOARD_STABLE_SHA256 = (
    "5a2ce264fd3ab23c408b111a2d58ceb1f45449bede0b9e5af01a4599764352a3"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)

TASK_PREFIX = "docs/task-evidence/self-supervised-neural-multiband-eq-and-dynamics/"
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

PAPER = {
    "record_id": "dafx2025-paper-81",
    "archive_detail_id": "AvUulq3fVM5yMf35-alPvQ",
    "title": (
        "Neural-Driven Multi-Band Processing for Automatic Equalization and "
        "Style Transfer"
    ),
    "authors": ["Parakrant Sarkar", "Permagnus Lindborg"],
    "venue": "DAFx-2025, Ancona",
    "archive_url": "https://dafx.de/paper-archive/details/AvUulq3fVM5yMf35-alPvQ",
    "pdf_url": "https://dafx.de/paper-archive/2025/DAFx25_paper_81.pdf",
    "architecture_claim": (
        "Six-band static parametric EQ plus per-band dynamic-range compression; "
        "processor parameters are predicted once per input segment and trained "
        "self-supervised by recovering clean audio from randomly degraded inputs."
    ),
    "evaluation_claim": (
        "MUSDB18 objective metrics (SI-SDR, PESQ, STFT loss and related scores) "
        "and a listening test; source reports NDMP above PEQ and PEQ+DRC baselines."
    ),
    "pdf_downloaded_here": False,
    "pdf_sha256": None,
    "code_revision": None,
    "checkpoint_sha256": None,
    "license": "unreviewed; a paper copyright statement is not a source or weight licence",
    "local_execution": False,
    "task_match": (
        "Music-production style transfer on MUSDB18; not the installed 16 kHz "
        "mono float32 160-sample v0 format and not a rights-cleared speech cohort."
    ),
    "separation": (
        "Paper and archive statements are source-reported. No PDF bytes, source, "
        "checkpoint or output is staged here; no upstream score qualifies this task."
    ),
}

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_unpinned_ndmp_source_and_weights",
    "paper": dict(PAPER),
    "source_tree": {
        "revision": None,
        "license": None,
        "path": None,
        "present_locally": False,
        "note": (
            "The paper archive and author page provide no pinned immutable "
            "runnable source revision staged for this task."
        ),
    },
    "checkpoint": {
        "artifact": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": "No AutoEQ or style-transfer weight file is pinned or staged.",
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": "No locked offline loader, dependency lock or exact runtime is staged.",
    },
    "geometry": {
        "status": "source_reported_only_not_pinned",
        "band_count": 6,
        "eq_stage": "static six-band parametric EQ (source-reported)",
        "dynamics_stage": "per-band dynamic-range compression (source-reported)",
        "control_scope": "one parameter prediction per input segment (length unpinned)",
        "native_delay_samples": None,
        "max_drain_calls": None,
        "installed_v0": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "note": (
            "Installed v0 geometry is verified by pins; NDMP analysis/hop/delay/"
            "finalization geometry is not pinned and is not inferred from the paper."
        ),
    },
    "rights": {
        "status": "unreviewed",
        "note": (
            "No source licence, weight licence, MUSDB18 terms, listening consent "
            "or product-use review is staged."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
}

BOUNDARY: Dict[str, Any] = {
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

SCOPE: Dict[str, Any] = {
    "synthetic_only": True,
    "task_local_only": True,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "model_executed": False,
    "checkpoint_loaded": False,
    "network_used": False,
    "dynamics_claim": False,
    "musdb18_audio": False,
}

NEGATIVE_CLAIMS: List[str] = [
    "No NDMP source is imported, built or executed by this package.",
    "No NDMP checkpoint, weights or MUSDB18 audio bytes are present or loaded.",
    "Synthetic sweeps, steps, impulses, silence and harmonic proxies are not real audio.",
    "Upstream MUSDB18 scores and listening claims are source-reported, not local results.",
    "No six-band EQ or per-band dynamics output is attributed to NDMP.",
    "The dynamics half is a CLN-09 boundary and is never pooled into a CLN-10 claim.",
    "No device timing, benchmark result, release claim or provider exposure is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES: List[Dict[str, Any]] = [
    {
        "id": "RG-01",
        "title": "exact_source_runtime_and_asset_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "The immutable NDMP source revision, checkpoint path, byte count, "
            "SHA-256, licence and locked runtime must be pinned."
        ),
        "reopen_condition": (
            "Stage and review the exact licensed source, weights and offline runtime."
        ),
    },
    {
        "id": "RG-02",
        "title": "installed_geometry_and_caller_asset_boundary",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Caller metadata, byte counts, hashes and native analysis/hop/delay/"
            "finalization geometry must be verified without loading an asset at "
            "16 kHz mono float32 with 160-sample frames."
        ),
        "reopen_condition": (
            "Pass a hash-matched caller manifest against the exact pinned NDMP "
            "geometry and reproduce byte-level output."
        ),
    },
    {
        "id": "RG-03",
        "title": "rights_and_terms",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Source, checkpoint, MUSDB18, task-matched corpus, listening consent "
            "and product-use rights require explicit review."
        ),
        "reopen_condition": "Reviewed rights records clear code, weights, data and product use.",
    },
    {
        "id": "RG-04",
        "title": "frozen_dsp_conditions_and_controls",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Freeze sweeps, steps, impulses, silence, clean speech proxy, "
            "intelligibility or load control, six-band response and state "
            "transitions for the exact runtime."
        ),
        "reopen_condition": (
            "A rights-cleared task-matched cohort with a frozen DSP protocol is staged."
        ),
    },
    {
        "id": "RG-05",
        "title": "dsp_profile_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Measure gain, response, attack/release, headroom, delay, numerical "
            "behavior and interacting nonlinear configurations with an identity "
            "control and a task-matched baseline."
        ),
        "reopen_condition": "Matched DSP outcomes are produced with pinned scorers and controls.",
    },
    {
        "id": "RG-06",
        "title": "matched_cohort_scorer_and_listening",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "A task-matched held-out cohort, pinned scorers and blinded listening "
            "must remain separate from source-reported MUSDB18 claims and from "
            "historical synthetic tone screens."
        ),
        "reopen_condition": "Held-out task-matched quality and preservation evidence is reviewed.",
    },
    {
        "id": "RG-07",
        "title": "timing_resources_and_state",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Availability, algorithmic delay, whole-segment finalization, paced "
            "runtime, peak/memory and reset behavior require measurement on the "
            "exact runtime."
        ),
        "reopen_condition": "Target-runtime pacing, state, memory and content-delay evidence is collected.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Opt-in provider intake, independent exact-head review and release "
            "approval are required before any exposure."
        ),
        "reopen_condition": (
            "A separate versioned intake passes independent review with OFF default "
            "and explicit approval."
        ),
    },
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {
        "id": "XB-01",
        "title": "runnable_ndmp_source_revision_absent",
        "detail": (
            "The linked research names a DAFx-2025 neural multiband processor, "
            "but no immutable source tree, revision, licence or build recipe is "
            "staged. The paper archive provides a paper record and PDF link only."
        ),
        "reopen": (
            "Stage the exact licensed NDMP source at an immutable revision with a "
            "deterministic offline build recipe and review it."
        ),
    },
    {
        "id": "XB-02",
        "title": "checkpoint_runtime_and_native_geometry_unpinned",
        "detail": (
            "No AutoEQ checkpoint path, revision, byte count or SHA-256, and no "
            "locked runtime or exact six-band analysis/hop/delay/finalization "
            "geometry is staged. The installed 16 kHz mono float32 160-sample "
            "geometry does not establish NDMP's native geometry."
        ),
        "reopen": (
            "Pin the exact weights, runtime and native geometry, then reproduce "
            "byte-level output on the installed format."
        ),
    },
    {
        "id": "XB-03",
        "title": "task_matched_assets_rights_and_scorers_absent",
        "detail": (
            "No rights-cleared task-matched clean/perturbed cohort, calibrated "
            "desired response, desired-response definition, held-out split, "
            "pinned scorer or listening protocol is staged. Upstream MUSDB18 "
            "music results are neither local nor task-matched speech evidence."
        ),
        "reopen": (
            "Stage rights-cleared matched assets with frozen DSP controls, pinned "
            "scorers and an approved preservation protocol."
        ),
    },
    {
        "id": "XB-04",
        "title": "dsp_profile_timing_and_release_gates_unmet",
        "detail": (
            "No real DSP outcome, device timing, availability, listening, "
            "benchmark, opt-in intake or independent release review exists. "
            "Historical synthetic tone and inverse-EQ screens cannot qualify it."
        ),
        "reopen": "Complete the DSP profile on the exact runtime and pass independent opt-in review.",
    },
]

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "paper_record_id", "source_revision",
    "checkpoint_path", "checkpoint_sha256", "checkpoint_byte_count",
    "checkpoint_revision", "runtime_lock_digest", "sample_rate_hz", "channels",
    "frame_samples", "sample_format", "band_count", "eq_stage",
    "dynamics_stage", "control_scope", "native_delay_samples", "max_drain_calls",
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
SYNTH_SCALE = 32768
SYNTH_SEED = 20261126
TONE_FREQUENCIES_HZ: Tuple[int, ...] = (50, 100, 200, 500, 1000, 2000, 4000, 7000)
BAND_EDGES_HZ: Tuple[int, ...] = (0, 200, 500, 1000, 2000, 4000, 8000)


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
            "Paper lead only: no runnable source, checkpoint, execution, "
            "licence review or task-matched outcome is supplied by this line."
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
    if manifest["configuration_id"] != "ndmp-autoeq-six-band-drc":
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported configuration")
    if manifest["paper_record_id"] != PAPER["record_id"]:
        raise ReferenceRejection("UNKNOWN_PAPER_RECORD", "paper record mismatch")
    if manifest["source_revision"] != PAPER["archive_detail_id"]:
        raise ReferenceRejection("SOURCE_REVISION_MISMATCH", "paper revision mismatch")
    if (manifest["sample_rate_hz"] != SAMPLE_RATE_HZ
            or manifest["channels"] != CHANNELS
            or manifest["frame_samples"] != FRAME_SAMPLES
            or manifest["sample_format"] != SAMPLE_FORMAT):
        raise ReferenceRejection("FORMAT_MISMATCH", "installed v0 format mismatch")
    if (manifest["band_count"] != 6
            or manifest["eq_stage"] != "static_six_band_peq"
            or manifest["dynamics_stage"] != "per_band_compressor"
            or manifest["control_scope"] != "per_segment"):
        raise ReferenceRejection("GEOMETRY_UNPINNED", "NDMP geometry mismatch")
    if (not isinstance(manifest["native_delay_samples"], int)
            or isinstance(manifest["native_delay_samples"], bool)
            or not 0 <= manifest["native_delay_samples"] <= 16000):
        raise ReferenceRejection("BAD_DELAY", "native delay must be 0..16000")
    if (not isinstance(manifest["max_drain_calls"], int)
            or isinstance(manifest["max_drain_calls"], bool)
            or not 1 <= manifest["max_drain_calls"] <= 1024):
        raise ReferenceRejection("BAD_DRAIN_LIMIT", "max drain calls must be 1..1024")
    if not isinstance(manifest["checkpoint_path"], str) or not Path(
            manifest["checkpoint_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_CHECKPOINT", "checkpoint path must be absolute")
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
    if checkpoint.stat().st_size != manifest["checkpoint_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "checkpoint byte count mismatch")
    if sha256_file(checkpoint) != manifest["checkpoint_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "checkpoint SHA-256 mismatch")
    raise ReferenceRejection(
        "NDMP_ASSET_IDENTITY_UNPINNED",
        "hash-matched caller asset is still not the exact NDMP AutoEQ checkpoint")


def valid_manifest(checkpoint_path: str = "/absent/ndmp-autoeq.ckpt") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": "ndmp-autoeq-six-band-drc",
        "paper_record_id": PAPER["record_id"],
        "source_revision": PAPER["archive_detail_id"],
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": "0" * 64,
        "checkpoint_byte_count": 1,
        "checkpoint_revision": "unpinned",
        "runtime_lock_digest": "0" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "band_count": 6,
        "eq_stage": "static_six_band_peq",
        "dynamics_stage": "per_band_compressor",
        "control_scope": "per_segment",
        "native_delay_samples": 0,
        "max_drain_calls": 1,
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


def tone_q15(frequency_hz: int, sample_count: int = CLIP_SAMPLES) -> List[int]:
    increment = (frequency_hz * 65536) // SAMPLE_RATE_HZ
    return [SINE64[((index * increment) * 64 // 65536) % 64]
            for index in range(sample_count)]


def impulse_q15() -> List[int]:
    values = [0] * CLIP_SAMPLES
    values[0] = 32767
    return values


def step_q15() -> List[int]:
    return [-8192] * (CLIP_SAMPLES // 2) + [8192] * (CLIP_SAMPLES // 2)


def silence_q15() -> List[int]:
    return [0] * CLIP_SAMPLES


def harmonic_proxy_q15() -> List[int]:
    values: List[int] = []
    rng = _lcg(SYNTH_SEED)
    for index in range(CLIP_SAMPLES):
        envelope = 12000 if (index // FRAME_SAMPLES) % 4 in (0, 1) else 1800
        jitter = next(rng) % 33 - 16
        tone = 3 * SINE64[index % 64] + SINE64[(2 * index) % 64] + jitter
        values.append(max(-32768, min(32767, (envelope * tone) // (4 * SYNTH_SCALE))))
    return values


def saturating_cascade_q15(values: Sequence[int]) -> List[int]:
    return [max(-32768, min(32767, value * 2)) for value in values]


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
        "out_of_range_count": sum(1 for value in values
                                  if not -32768 <= value <= 32767),
    }


def _band_for_frequency(frequency_hz: int) -> int:
    for band in range(len(BAND_EDGES_HZ) - 1):
        if BAND_EDGES_HZ[band] <= frequency_hz < BAND_EDGES_HZ[band + 1]:
            return band
    return len(BAND_EDGES_HZ) - 2


def synthetic_dsp() -> Dict[str, Any]:
    tones = {str(frequency): _stats(tone_q15(frequency))
             for frequency in TONE_FREQUENCIES_HZ}
    proxy = harmonic_proxy_q15()
    cascade = saturating_cascade_q15(proxy)
    joined = [value for frame in range(0, CLIP_SAMPLES, FRAME_SAMPLES)
              for value in proxy[frame:frame + FRAME_SAMPLES]]
    return {
        "label": (
            "Synthetic deterministic DSP controls only; no real audio, NDMP "
            "weights or NDMP output."
        ),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": "integer fixture; installed runtime format is float32",
        "clip_samples": CLIP_SAMPLES,
        "seed": SYNTH_SEED,
        "tone_hz": list(TONE_FREQUENCIES_HZ),
        "six_band_edges_hz": list(BAND_EDGES_HZ),
        "tone_probes": tones,
        "six_band_probe": [
            {"frequency_hz": frequency, "band_index": _band_for_frequency(frequency),
             "rms": tones[str(frequency)]["rms"]}
            for frequency in TONE_FREQUENCIES_HZ
        ],
        "conditions": {
            "sweep_tones": {"status": "synthetic_only", "qualifies": False},
            "impulse": dict(_stats(impulse_q15()), status="synthetic_only", qualifies=False),
            "step": dict(_stats(step_q15()), status="synthetic_only", qualifies=False),
            "silence": dict(_stats(silence_q15()), status="synthetic_only", qualifies=False),
            "harmonic_proxy_not_real_speech": dict(
                _stats(proxy), status="synthetic_only", qualifies=False),
            "nonlinear_interaction": dict(
                _stats(cascade), status="synthetic_control_only", qualifies=False),
        },
        "identity_control": {
            "byte_identical": joined == proxy,
            "digest": object_digest(proxy),
            "status": "bit_exact_synthetic_only",
            "qualifies": False,
        },
        "numerics": {
            "nonfinite_count": 0,
            "out_of_range_count": sum(
                item["out_of_range_count"]
                for item in (_stats(impulse_q15()), _stats(step_q15()),
                             _stats(silence_q15()), _stats(proxy), _stats(cascade))),
            "note": "Integer fixtures only; no NDMP numerical result is claimed.",
        },
        "note": (
            "Six-band edges and tone probes are a task-local analytic fixture. "
            "They are not NDMP band edges, not a measured device response and "
            "not a speech intelligibility or listening result."
        ),
    }


def alignment_probe() -> Dict[str, Any]:
    return {
        "label": "Installed-format interval mapping only; no measured content delay",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_SAMPLES * SAMPLE_NS,
        "native_delay_samples": None,
        "content_delay_claim": False,
        "source_first_sample_example": None,
        "shift_probes": [
            {"shift_samples": 0, "accepted": True},
            {"shift_samples": -FRAME_SAMPLES, "accepted": False},
            {"shift_samples": FRAME_SAMPLES, "accepted": False},
        ],
        "delayed_render": "not applicable; no measured NDMP render path",
        "missing_render": "blocked; no NDMP output or finalization recipe is staged",
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
    return {
        "cases": cases,
        "matches_expectation": all(item["accepted"] == item["expected"] for item in cases),
        "state_owned": False,
        "note": "Model-free fixture state only; no NDMP or provider state exists.",
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

    add("missing_field", lambda m: m.pop("steps") if "steps" in m else m.pop("band_count"),
        "MISSING_FIELD")
    add("unknown_field", lambda m: m.update(extra=1), "UNKNOWN_FIELD")
    add("wrong_adapter", lambda m: m.update(adapter="other"), "UNKNOWN_ADAPTER")
    add("wrong_configuration", lambda m: m.update(configuration_id="raw"),
        "UNKNOWN_CONFIGURATION")
    add("wrong_paper_record", lambda m: m.update(paper_record_id="other"),
        "UNKNOWN_PAPER_RECORD")
    add("wrong_source_revision", lambda m: m.update(source_revision="deadbeef"),
        "SOURCE_REVISION_MISMATCH")
    add("wrong_rate", lambda m: m.update(sample_rate_hz=48000), "FORMAT_MISMATCH")
    add("wrong_channels", lambda m: m.update(channels=2), "FORMAT_MISMATCH")
    add("wrong_frame", lambda m: m.update(frame_samples=320), "FORMAT_MISMATCH")
    add("wrong_format", lambda m: m.update(sample_format="int16"), "FORMAT_MISMATCH")
    add("wrong_band_count", lambda m: m.update(band_count=8), "GEOMETRY_UNPINNED")
    add("wrong_eq_stage", lambda m: m.update(eq_stage="dynamic"), "GEOMETRY_UNPINNED")
    add("wrong_dynamics_stage", lambda m: m.update(dynamics_stage="single_band"),
        "GEOMETRY_UNPINNED")
    add("wrong_control_scope", lambda m: m.update(control_scope="per_sample"),
        "GEOMETRY_UNPINNED")
    add("bad_delay", lambda m: m.update(native_delay_samples=-1), "BAD_DELAY")
    add("bad_drain_limit", lambda m: m.update(max_drain_calls=2048), "BAD_DRAIN_LIMIT")
    add("relative_checkpoint", lambda m: m.update(checkpoint_path="last.ckpt"),
        "RELATIVE_CHECKPOINT")
    add("absent_checkpoint", lambda m: None, "ASSET_ABSENT")
    add("bad_checkpoint_digest", lambda m: m.update(checkpoint_sha256="abc"),
        "BAD_CHECKPOINT_DIGEST")
    add("bad_byte_count", lambda m: m.update(checkpoint_byte_count=True), "BAD_BYTE_COUNT")
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
        "data/models/ndmp-autoeq",
        "data/checkpoints/ndmp",
        "data/checkouts/ndmp",
        "adapters/ndmp",
        "data/corpora/musdb18",
        "data/corpora/level-tone-matched",
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
        "paper": dict(PAPER),
        "historical_synthetic_screen": {
            "source": "reports/level-tone/20261028-synthetic-evaluation.json",
            "clips": 240,
            "train": 180,
            "heldout": 60,
            "learned_inverse_eq_rmse_db": 2.577,
            "identity_eq_rmse_db": 4.414,
            "note": (
                "Transcribed from the pinned level/tone study. It is a ridge "
                "synthetic screen, not NDMP and not a real-speech result."
            ),
        },
        "separation": (
            "The DAFx paper claim and the historical synthetic screen are "
            "source-reported. Neither is a local NDMP output, a matched cohort "
            "result or a release qualification."
        ),
        "qualifies": False,
        "listening_performed_here": False,
    }


def dsp_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "sweeps_steps_impulses_silence": {
                "status": "synthetic_only",
                "evidence": "Deterministic integer fixtures; no real audio or device loop.",
            },
            "clean_speech_and_intelligibility_control": {
                "status": "blocked",
                "evidence": "No rights-cleared clean speech, token or scorer is staged.",
            },
            "gain_and_response": {
                "status": "synthetic_analytic_only",
                "evidence": "Tone probes and band edges are task-local, not NDMP output.",
            },
            "attack_release_headroom": {
                "status": "blocked",
                "evidence": "Per-band compression parameters and runtime are unpinned.",
            },
            "delay_and_numerical_behavior": {
                "status": "synthetic_only",
                "evidence": "Installed-format mapping and integer numerics only.",
            },
            "state_transitions": {
                "status": "synthetic_model_free_only",
                "evidence": "Epoch validator only; no NDMP state exists here.",
            },
            "interacting_nonlinear_configurations": {
                "status": "synthetic_control_only",
                "evidence": "Saturating cascade fixture; not PEQ+DRC or NDMP.",
            },
            "matched_identity_and_task_baseline": {
                "status": "blocked",
                "evidence": "Identity bit-exactness is synthetic only; no task-matched baseline.",
            },
            "matched_heldout_qualification": {
                "status": "blocked",
                "evidence": "No pinned task-matched cohort, scorer or listening result.",
            },
        },
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    dsp = synthetic_dsp()
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
            "configuration_id": "ndmp-autoeq-six-band-drc",
            "paper_record_id": PAPER["record_id"],
            "installed_format": dict(BOUNDARY["format"]),
            "source_reported_structure": {
                "band_count": 6,
                "eq_stage": "static six-band parametric EQ",
                "dynamics_stage": "per-band dynamic-range compression",
                "control_scope": "one parameter prediction per input segment",
            },
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata-only reference. A hash-matched caller asset still "
                "fails as NDMP_ASSET_IDENTITY_UNPINNED."
            ),
        },
        "asset_resolution": probe,
        "synthetic_dsp": dsp,
        "dsp_profile": dsp_profile(),
        "availability": {
            "status": "modelled_not_measured",
            "clock": "fixture-monotonic-not-device",
            "whole_segment_available_after_final_sample": None,
            "segment_samples": None,
            "device_timing": False,
            "streaming_result": False,
            "content_delay_claim": False,
        },
        "alignment": align,
        "state": state,
        "controls": {
            "identity": {"status": "bit_exact_synthetic_only", "qualifies": False},
            "matched_baseline": {"status": "blocked", "qualifies": False},
            "nonlinear_interaction": {"status": "synthetic_control_only", "qualifies": False},
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
            "status": "blocked_no_matched_ndmp_checkpoint_or_cohort",
            "identity_control": "synthetic only",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "model_provenance": {
            "paper": dict(PAPER),
            "source_tree": dict(ASSET_LEDGER["source_tree"]),
            "checkpoint": dict(ASSET_LEDGER["checkpoint"]),
            "runtime": dict(ASSET_LEDGER["runtime"]),
            "geometry": dict(ASSET_LEDGER["geometry"]),
        },
        "licensing_analysis": {
            "paper": "source-reported; not a source or weight licence",
            "source_terms": "unreviewed",
            "checkpoint_terms": "unreviewed",
            "musdb18_terms": "unreviewed; no MUSDB18 audio staged",
            "product_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact NDMP source revision, licence and offline runtime",
            "exact checkpoint identity, bytes and native geometry",
            "rights-cleared task-matched cohort with desired-response definition",
            "matched DSP outcomes and device timing on the exact runtime",
            "independent listening and opt-in provider intake",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "real_local_model_output": False,
            "real_audio": False,
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
        "# SHA-256 pins for SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS.",
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
            "No source, checkpoint, audio or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "Synthetic DSP controls are labelled and cannot qualify the candidate.",
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
