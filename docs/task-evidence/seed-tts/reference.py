# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the Seed-TTS feasibility row.

This package is feasibility evidence only. It models a caller-supplied-asset
boundary with synthetic, integer-only structural controls. It does not
implement, download, load, import or execute Seed-TTS. No checkpoint, real
audio, listening result, device timing, benchmark result or release claim is
included, and no result here qualifies the candidate.
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
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/seed-tts/caller-supplied/0.1"
TASK_ID = "SDK-SEED-TTS"
TITLE = "Seed-TTS"
COMPONENT = "seed-tts"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "a51e49f718500ec9e81242cf2816f0b576333d00"
BRANCH = "swarm/SDK-SEED-TTS"
REVIEWER = "reviewer-SEED-TTS"
PROFILE = "voice"
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

MATRIX_PATH = "research/voice-enhancement-20261101/candidate_matrix.csv"
TRANSFORM_PATH = "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"
REAUDIT_PATH = "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md"
FINDINGS_PATH = "research/voice-enhancement-20261101/findings.md"
CENSUS_PATH = "research/voice-conversion-eval-20261101/README.md"

MATRIX_LINE = (
    "Voice transformation,Seed-TTS,unavailable/blocked,"
    "No accessible licensed checkpoint and input-conversion runtime verified,"
    "Identity; locally runnable TTS/VC,"
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"
)
TRANSFORM_LINE = (
    "| Seed-TTS | unavailable/blocked | No weights, adapter or evaluation found. | "
    "The authors' technical report describes a large autoregressive TTS family "
    "and a non-autoregressive diffusion variant; the public report/demo does "
    "not establish a locally downloadable, licensed streaming input-conversion "
    "model. [Author technical report](https://arxiv.org/abs/2406.02430), "
    "[author demo/report](https://bytedancespeech.github.io/seedtts_tech_report). "
    "| Exact open checkpoint, redistribution terms, runtime contract and target "
    "device footprint remain unverified; no substitution with another TTS model."
)
REAUDIT_LINE = (
    "- **Seed-TTS:** the matrix's external licensed checkpoint/access gate is "
    "unchanged; no usable checkpoint or source-speech conversion runtime is staged."
)
EVIDENCE_ENTRIES: Tuple[Dict[str, Any], ...] = (
    {
        "path": MATRIX_PATH,
        "line": 51,
        "text": MATRIX_LINE,
        "class": "candidate_census_row",
        "note": "Structured voice census row; unavailable/blocked, not a local result.",
    },
    {
        "path": TRANSFORM_PATH,
        "line": 19,
        "text": TRANSFORM_LINE,
        "class": "voice_transformation_audit_row",
        "note": "Primary-source audit: no weights, adapter, evaluation or licensed streaming conversion model established.",
    },
    {
        "path": REAUDIT_PATH,
        "line": 36,
        "text": REAUDIT_LINE,
        "class": "blocked_reaudit_row",
        "note": "Reaudit confirms the external licensed checkpoint/access gate is unchanged.",
    },
)

SOURCE_PINS: Dict[str, str] = {
    MATRIX_PATH:
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    TRANSFORM_PATH:
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    REAUDIT_PATH:
        "5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14",
    FINDINGS_PATH:
        "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
    "research/voice-enhancement-20261101/agent-matrix-audit/REPORT.md":
        "865b0031d357b7009c2876f997ca188440451fb65d5cef3561e9848f34eaf1d0",
    CENSUS_PATH:
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    INVENTORY_PATH:
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
    "docs/task-evidence/f5-tts/README.md":
        "31ffbd70d9a6976509c492398bf17a0d43b0c4b2a5d98f0c4df320ac1489a0b8",
    "docs/task-evidence/cosyvoice-family/README.md":
        "41ab92e27ed62d9379627be8714579ab168e16125c5496d99dc25b77fb20de67",
    "docs/task-evidence/survey-trn-05/README.md":
        "81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b",
}

BOARD_STABLE_SHA256 = (
    "b616ff242b23a1a1f1d9dc2c53da26cb002dac04a5ebd793c9a5cb4837a74181"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)
INVENTORY_COMPONENT_FIELDS = (
    "id", "name", "area", "evidence_status", "repository", "disposition",
    "verification_profile", "task",
)

TASK_PREFIX = "docs/task-evidence/seed-tts/"
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

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_licensed_checkpoint_and_runtime_identity_unpinned",
    "source_checkout": {
        "status": "absent",
        "revision": None,
        "license": None,
        "note": "No Seed-TTS source checkout is staged at any fixed probe path.",
    },
    "checkpoint": {
        "artifact": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": (
            "The pinned census and audits do not name a downloadable licensed "
            "Seed-TTS checkpoint, immutable revision, byte count or SHA-256."
        ),
    },
    "diffusion_variant": {
        "artifact": None,
        "present_locally": False,
        "note": "The public report describes a variant but pins no runnable asset here.",
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": "No locked Python/PyTorch runtime, tokenizer, vocoder or offline loader is staged.",
    },
    "cohort_and_rights": {
        "status": "absent_unreviewed",
        "note": (
            "No consented reference-voice corpus, manual transcripts, language/speaker "
            "groups, held-out text split, output-use grant or pinned scorer is staged."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
    "network_used": False,
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
    "provider_registered": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No Seed-TTS source, checkpoint, tokenizer, vocoder or runtime is imported, built, downloaded, loaded or executed.",
    "No TTS or voice-conversion waveform, reference voice, consent record, listening result or quality score is present.",
    "Integer token/text controls are synthetic structural fixtures and cannot qualify voice quality or identity preservation.",
    "Source-reported Seed-TTS descriptions and other TTS test-set uses are provenance only and are not local measurements.",
    "No device timing, first-audio measurement, benchmark result, release claim or provider exposure is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
)

GATES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "RG-01",
        "title": "exact_source_checkpoint_and_runtime_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "The exact Seed-TTS source revision, checkpoint path, byte count, SHA-256, immutable runtime lock and variant must be pinned.",
        "reopen_condition": "Stage and review an exact licensed Seed-TTS artifact identity and locked offline runtime.",
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Caller asset identity, configuration, rate, channels, frame, sample format, token/vocoder contract and final geometry must be verified without loading an asset.",
        "reopen_condition": "Pass a hash-matched caller manifest against the exact pinned Seed-TTS geometry and reproduce an exact run.",
    },
    {
        "id": "RG-03",
        "title": "rights_consent_and_output_use",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Code, checkpoint, training data, reference-voice consent, reference availability and output-use terms require explicit independent review.",
        "reopen_condition": "Reviewed rights records clear code, weights, data, consent, availability and product use.",
    },
    {
        "id": "RG-04",
        "title": "frozen_permitted_cohort_and_target_condition",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Freeze permitted input/target references, task, language/speaker groups, manual transcripts, held-out text split and exact target condition.",
        "reopen_condition": "Stage a rights-cleared frozen voice cohort with declared target conditions and splits.",
    },
    {
        "id": "RG-05",
        "title": "text_and_semantic_content_preservation",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Preserve text and semantic content with fixed-voice, mismatched-reference, ignore-reference and content-preservation controls and pinned ASR scoring.",
        "reopen_condition": "Produce matched content-preservation outcomes with pinned scorers and uncertainty.",
    },
    {
        "id": "RG-06",
        "title": "identity_similarity_and_naturalness",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Identity/similarity and naturalness must be separate outcomes with independent blinded listening and reference-voice comparison.",
        "reopen_condition": "Collect independent identity and naturalness results on the exact pinned bundle.",
    },
    {
        "id": "RG-07",
        "title": "alignment_timing_resources_and_state",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Alignment, first-output/tail timing, sample conservation, nonfinite behavior, peak/memory and reset state require measurement on the exact runtime.",
        "reopen_condition": "Measure target-runtime chunking, content delay, availability, memory and state behavior.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Opt-in provider intake, independent exact-head review and release approval are required before any exposure.",
        "reopen_condition": "A separate versioned intake passes independent review with the default OFF and explicit approval.",
    },
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "XB-01",
        "title": "licensed_checkpoint_identity_absent",
        "detail": (
            "The pinned census marks Seed-TTS unavailable/blocked. The voice audit "
            "finds no weights, adapter or evaluation and states that the public "
            "report/demo does not establish a locally downloadable licensed "
            "streaming input-conversion model. No exact checkpoint path, revision, "
            "byte count or SHA-256 exists to pin."
        ),
        "reopen": (
            "Provide the exact licensed Seed-TTS artifact with immutable revision, "
            "byte count and SHA-256, plus its reviewed source and redistribution terms."
        ),
    },
    {
        "id": "XB-02",
        "title": "exact_runtime_and_task_contract_unpinned",
        "detail": (
            "No locked Python/PyTorch runtime, tokenizer/vocoder bundle, offline "
            "loader, autoregressive-versus-diffusion variant selection, chunking, "
            "alignment or finalization geometry is staged. Adjacent TTS test-set "
            "uses are different models and tasks and cannot be substituted."
        ),
        "reopen": (
            "Pin the exact runtime and task geometry, then reproduce exact outputs "
            "with a hash-matched caller-supplied asset."
        ),
    },
    {
        "id": "XB-03",
        "title": "rights_cleared_cohort_and_scorers_absent",
        "detail": (
            "No consented reference voices, manual transcripts, speaker/language "
            "groups, held-out text split, target condition, reference availability, "
            "output-use grant or pinned content/identity/naturalness scorer is staged."
        ),
        "reopen": (
            "Stage a rights-cleared, consented, frozen voice cohort with pinned "
            "scorers and independent controls."
        ),
    },
    {
        "id": "XB-04",
        "title": "voice_profile_and_release_gates_unmet",
        "detail": (
            "No local Seed-TTS output, content-preservation result, identity or "
            "naturalness score, blinded listening, first-output/tail measurement, "
            "device timing, benchmark, opt-in intake or independent release review exists."
        ),
        "reopen": (
            "Complete the voice profile on the exact runtime and pass independent "
            "opt-in review with the default OFF."
        ),
    },
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "checkpoint_path", "checkpoint_sha256",
    "checkpoint_byte_count", "checkpoint_revision", "source_revision",
    "runtime_lock_digest", "rights_digest", "sample_rate_hz", "channels",
    "frame_samples", "sample_format", "text_cohort_digest",
    "reference_consent_digest",
)
CONFIGURATIONS: Tuple[str, ...] = (
    "seed-tts-autoregressive-text-conditioned",
    "seed-tts-non-autoregressive-diffusion",
)
SYNTH_SEED = 20261126
TOKEN_COUNT = 48
TOKEN_BASE = 256


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
        elif key.startswith("sdk:"):
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
    if key.startswith("sdk:"):
        return SDK_ROOT / key.split(":", 1)[1]
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


def inventory_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / INVENTORY_PATH)
    if not isinstance(payload, dict) or not isinstance(payload.get("components"), list):
        raise ValueError("invalid_inventory")
    rows = [row for row in payload["components"]
            if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise ValueError("inventory_row_not_unique")
    row = rows[0]
    expected = {
        "id": COMPONENT,
        "name": TITLE,
        "evidence_status": "blocked",
        "repository": REPOSITORY,
        "verification_profile": PROFILE,
        "task": TASK_ID,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise ValueError("inventory_field_mismatch:" + key)
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("inventory_evidence_absent")
    first = evidence[0]
    for key, value in (
        ("path", MATRIX_PATH),
        ("record", 50),
        ("record_name", "Seed-TTS"),
        ("record_status", "unavailable/blocked"),
        ("finding", "No accessible licensed checkpoint and input-conversion runtime verified"),
    ):
        if first.get(key) != value:
            raise ValueError("inventory_evidence_mismatch:" + key)
    stable = {field: row[field] for field in INVENTORY_COMPONENT_FIELDS}
    return {
        "stable_fields": stable,
        "stable_sha256": object_digest(stable),
        "evidence_path": first["path"],
        "evidence_record": first["record"],
        "evidence_status": first["record_status"],
        "full_inventory_hashed": False,
        "note": "Inventory row and census record are provenance only; never a result.",
    }


def evidence_entries() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for entry in EVIDENCE_ENTRIES:
        path = SOURCE_ROOT / entry["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines[entry["line"] - 1].strip() != entry["text"]:
            raise ValueError("evidence_line_mismatch:" + entry["path"])
        entries.append({
            "path": entry["path"],
            "line": entry["line"],
            "sha256": sha256_file(path),
            "text": entry["text"],
            "class": entry["class"],
            "note": entry["note"],
        })
    return entries


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


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


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
    if manifest["configuration_id"] not in CONFIGURATIONS:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported family configuration")
    if (not isinstance(manifest["source_revision"], str)
            or re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]) is None):
        raise ReferenceRejection("BAD_SOURCE_REVISION", "source revision malformed")
    if (manifest["sample_rate_hz"] != SAMPLE_RATE_HZ
            or manifest["channels"] != CHANNELS
            or manifest["frame_samples"] != FRAME_SAMPLES
            or manifest["sample_format"] != SAMPLE_FORMAT):
        raise ReferenceRejection("FORMAT_MISMATCH", "installed v0 format mismatch")
    if not isinstance(manifest["checkpoint_path"], str) or not Path(
            manifest["checkpoint_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_CHECKPOINT", "checkpoint path must be absolute")
    if not _is_sha256(manifest["checkpoint_sha256"]):
        raise ReferenceRejection("BAD_CHECKPOINT_DIGEST", "checkpoint SHA-256 malformed")
    if (not isinstance(manifest["checkpoint_byte_count"], int)
            or isinstance(manifest["checkpoint_byte_count"], bool)
            or manifest["checkpoint_byte_count"] <= 0):
        raise ReferenceRejection("BAD_BYTE_COUNT", "checkpoint byte count malformed")
    if (not isinstance(manifest["checkpoint_revision"], str)
            or not manifest["checkpoint_revision"].strip()):
        raise ReferenceRejection("MISSING_CHECKPOINT_REVISION", "revision required")
    for field, code in (
        ("runtime_lock_digest", "BAD_RUNTIME_DIGEST"),
        ("rights_digest", "BAD_RIGHTS_DIGEST"),
        ("text_cohort_digest", "BAD_COHORT_DIGEST"),
        ("reference_consent_digest", "BAD_CONSENT_DIGEST"),
    ):
        if not _is_sha256(manifest[field]):
            raise ReferenceRejection(code, field + " malformed")

    checkpoint = Path(manifest["checkpoint_path"])
    if not checkpoint.is_file():
        raise ReferenceRejection("ASSET_ABSENT", "declared checkpoint is absent")
    if sha256_file(checkpoint) != manifest["checkpoint_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "checkpoint SHA-256 mismatch")
    if checkpoint.stat().st_size != manifest["checkpoint_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "checkpoint byte count mismatch")
    raise ReferenceRejection(
        "SEED_TTS_CHECKPOINT_IDENTITY_UNPINNED",
        "hash-matched caller asset is still not an exact licensed Seed-TTS checkpoint",
    )


def valid_manifest(checkpoint_path: str = "/absent/seed-tts-checkpoint.safetensors") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": CONFIGURATIONS[0],
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": "0" * 64,
        "checkpoint_byte_count": 1,
        "checkpoint_revision": "caller-declared-revision",
        "source_revision": "0" * 40,
        "runtime_lock_digest": "0" * 64,
        "rights_digest": "0" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "text_cohort_digest": "0" * 64,
        "reference_consent_digest": "0" * 64,
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


def synthetic_tokens() -> List[int]:
    rng = _lcg(SYNTH_SEED)
    return [next(rng) % TOKEN_BASE for _ in range(TOKEN_COUNT)]


def frame_tokens(tokens: Sequence[int]) -> List[List[int]]:
    return [list(tokens[index:index + FRAME_SAMPLES])
            for index in range(0, len(tokens), FRAME_SAMPLES)]


def synthetic_voice() -> Dict[str, Any]:
    tokens = synthetic_tokens()
    rejoined = [token for frame in frame_tokens(tokens) for token in frame]
    swapped = list(tokens)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    inserted = list(tokens) + [0]
    truncated = list(tokens[:-1])
    return {
        "label": "synthetic integer token/text controls; not real text, audio, TTS output or listening evidence",
        "seed": SYNTH_SEED,
        "token_base": TOKEN_BASE,
        "token_count": TOKEN_COUNT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "canonical_tokens_sha256": object_digest(tokens),
        "frame_count": len(frame_tokens(tokens)),
        "final_partial_frame_tokens": len(tokens) % FRAME_SAMPLES,
        "identity_control": {
            "canonical_transcript_byte_identical": rejoined == tokens,
            "rejoined_tokens_sha256": object_digest(rejoined),
            "qualifies_candidate": False,
        },
        "content_controls": [
            {"id": "exact", "tokens_sha256": object_digest(tokens),
             "preserved": True, "qualifies_candidate": False},
            {"id": "swap", "tokens_sha256": object_digest(swapped),
             "preserved": swapped == tokens, "qualifies_candidate": False},
            {"id": "insert", "tokens_sha256": object_digest(inserted),
             "preserved": inserted == tokens, "qualifies_candidate": False},
            {"id": "truncate", "tokens_sha256": object_digest(truncated),
             "preserved": truncated == tokens, "qualifies_candidate": False},
        ],
        "note": (
            "Only deterministic integer token framing is exercised. No text semantics, "
            "ASR transcript, identity or naturalness result is produced or scored."
        ),
    }


def alignment_probe() -> Dict[str, Any]:
    return {
        "label": "synthetic interval mapping only; no measured first-output or tail timing",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_SAMPLES * SAMPLE_NS,
        "token_count": TOKEN_COUNT,
        "modelled_content_offset_samples": 0,
        "first_audio_ns": None,
        "tail_audio_ns": None,
        "measured": False,
        "shift_probes": [
            {"shift_samples": 0, "accepted": True},
            {"shift_samples": -FRAME_SAMPLES, "accepted": False},
            {"shift_samples": FRAME_SAMPLES, "accepted": False},
        ],
        "first_output": "blocked; no pinned runtime or causal output path",
        "tail": "blocked; no finalization geometry or measured tail",
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
    tokens = synthetic_tokens()
    joined = [token for frame in frame_tokens(tokens) for token in frame]
    return {
        "cases": cases,
        "matches_expectation": all(item["accepted"] == item["expected"] for item in cases),
        "state_owned": False,
        "chunk_invariance_digest": object_digest(joined),
        "chunk_invariance_exact": joined == tokens,
        "note": "Model-free fixture state only; no provider, tokenizer or model state exists.",
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

    add("missing_field", lambda m: m.pop("steps", None) or m.pop("frame_samples"),
        "MISSING_FIELD")
    add("unknown_field", lambda m: m.update(extra=1), "UNKNOWN_FIELD")
    add("wrong_adapter", lambda m: m.update(adapter="other"), "UNKNOWN_ADAPTER")
    add("wrong_configuration", lambda m: m.update(configuration_id="raw"),
        "UNKNOWN_CONFIGURATION")
    add("bad_source_revision", lambda m: m.update(source_revision="deadbeef"),
        "BAD_SOURCE_REVISION")
    add("wrong_rate", lambda m: m.update(sample_rate_hz=48000), "FORMAT_MISMATCH")
    add("wrong_channels", lambda m: m.update(channels=2), "FORMAT_MISMATCH")
    add("wrong_frame", lambda m: m.update(frame_samples=320), "FORMAT_MISMATCH")
    add("wrong_format", lambda m: m.update(sample_format="int16"), "FORMAT_MISMATCH")
    add("relative_checkpoint", lambda m: m.update(checkpoint_path="last.ckpt"),
        "RELATIVE_CHECKPOINT")
    add("absent_checkpoint", lambda m: None, "ASSET_ABSENT")
    add("bad_checkpoint_digest", lambda m: m.update(checkpoint_sha256="abc"),
        "BAD_CHECKPOINT_DIGEST")
    add("bad_byte_count", lambda m: m.update(checkpoint_byte_count=True),
        "BAD_BYTE_COUNT")
    add("bad_runtime_digest", lambda m: m.update(runtime_lock_digest="xyz"),
        "BAD_RUNTIME_DIGEST")
    add("bad_rights_digest", lambda m: m.update(rights_digest="xyz"),
        "BAD_RIGHTS_DIGEST")
    add("bad_cohort_digest", lambda m: m.update(text_cohort_digest="xyz"),
        "BAD_COHORT_DIGEST")
    add("bad_consent_digest", lambda m: m.update(reference_consent_digest="xyz"),
        "BAD_CONSENT_DIGEST")
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


WORKSPACE_PROBE_PATHS: Tuple[str, ...] = (
    "data/checkouts/Seed-TTS",
    "data/checkouts/seed-tts",
    "research/voice-enhancement-20261101/repos/Seed-TTS",
    "research/voice-enhancement-20261101/repos/seed-tts",
    "data/models/seed-tts",
    "data/models/seed-tts-ar",
    "data/models/seed-tts-diffusion",
    "data/envs/seed-tts",
    "data/licenses/seed-tts",
    "data/rights/seed-tts.json",
    "adapters/seed-tts",
    "docs/task-evidence/seed-tts/checkpoint",
)
HOME_PROBE_PATHS: Tuple[str, ...] = (
    ".cache/huggingface/hub/models--ByteDance--Seed-TTS",
    ".cache/huggingface/hub/models--ByteDance-Seed--Seed-TTS",
    ".cache/huggingface/hub/models--seed-tts",
    ".cache/huggingface/hub/datasets--yuekai--seed_tts",
)


def absent_artifact_probe() -> Dict[str, Any]:
    workspace = [
        {"path": path, "present": (SOURCE_ROOT / path).exists()}
        for path in WORKSPACE_PROBE_PATHS
    ]
    worktree = [
        {"path": path, "present": (SDK_ROOT / path).exists()}
        for path in WORKSPACE_PROBE_PATHS
    ]
    home = Path.home()
    home_rows = [
        {"path": "~/" + path, "present": (home / path).exists()}
        for path in HOME_PROBE_PATHS
    ]
    present = [row["path"] for row in workspace + worktree + home_rows if row["present"]]
    return {
        "workspace_probes": workspace,
        "sdk_worktree_probes": worktree,
        "home_cache_probes": home_rows,
        "workspace_probe_count": len(workspace),
        "sdk_worktree_probe_count": len(worktree),
        "home_cache_probe_count": len(home_rows),
        "present": bool(present),
        "present_paths": present,
        "recursive_workspace_walk": False,
        "note": "Bounded read-only path probes; no download, import, load or audio read was attempted.",
    }


def source_reported() -> Dict[str, Any]:
    return {
        "entries": evidence_entries(),
        "census_status": "unavailable/blocked",
        "audit_status": "No weights, adapter or evaluation found",
        "reaudit_status": "licensed checkpoint/access gate unchanged",
        "separation": (
            "Pinned records are provenance only. Technical report and demo descriptions "
            "are source-reported and are not local outputs or measurements. Other TTS "
            "test-set uses belong to different models and tasks and are not substituted."
        ),
        "qualifies": False,
        "listening_performed_here": False,
        "inference_performed_here": False,
    }


def voice_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "permitted_input_and_target_references": {
                "status": "blocked",
                "evidence": "No permitted source/reference pair, consent record or target-specification review is staged.",
            },
            "task_and_language_speaker_groups": {
                "status": "blocked",
                "evidence": "No frozen task, language group or speaker group definition is staged.",
            },
            "text_and_semantic_content_preservation": {
                "status": "synthetic_structural_only",
                "evidence": "Integer token framing control only; no transcript score or semantic adjudication.",
            },
            "identity_and_similarity_separate": {
                "status": "blocked",
                "evidence": "No independent speaker-similarity encoder, score or human rating is staged.",
            },
            "naturalness_separate": {
                "status": "blocked",
                "evidence": "No naturalness rating or blinded listening panel is staged.",
            },
            "alignment": {
                "status": "synthetic_only",
                "evidence": "Integer sample/frame mapping only; no word, phoneme or output alignment.",
            },
            "first_output_and_tail_timing": {
                "status": "blocked",
                "evidence": "No pinned runtime, causal output path or finalization geometry was measured.",
            },
            "exact_target_condition": {
                "status": "blocked",
                "evidence": "No reference-voice specification, reference-text policy or cleared condition exists.",
            },
            "consent_reference_availability_output_use": {
                "status": "blocked",
                "evidence": "Consent, availability and output-use rights are independent unresolved gates.",
            },
            "matched_heldout_voice_qualification": {
                "status": "blocked",
                "evidence": "No rights-cleared frozen cohort, scorer or held-out matched result is staged.",
            },
            "matched_fixed_voice_and_reference_controls": {
                "status": "blocked",
                "evidence": "No fixed-voice, mismatched-reference, ignore-reference or content-preservation control output exists.",
            },
        },
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    voice = synthetic_voice()
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
            "family_configurations": list(CONFIGURATIONS),
            "configuration_pinned": False,
            "format": dict(BOUNDARY["format"]),
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata-only reference. A hash-matched caller asset still fails as "
                "SEED_TTS_CHECKPOINT_IDENTITY_UNPINNED; no variant or checkpoint is promoted."
            ),
        },
        "asset_resolution": probe,
        "synthetic_voice": voice,
        "voice_profile": voice_profile(),
        "availability": {
            "status": "modelled_not_measured",
            "clock": "fixture-monotonic-not-device",
            "whole_response_available_after_final_token": True,
            "device_timing": False,
            "streaming_result": False,
            "first_audio_claim": False,
            "content_delay_claim": False,
        },
        "alignment": align,
        "state": state,
        "controls": {
            "identity": {"status": "bit_exact_synthetic_token_only", "qualifies": False},
            "content_mismatch": {"status": "integer_token_control_only", "qualifies": False},
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
            "status": "blocked_no_exact_seed_tts_asset_or_cohort",
            "identity_control": "synthetic token only",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "inventory_link": inventory_link(),
        "model_provenance": {
            "source_revision": None,
            "source_license": None,
            "checkpoint": dict(ASSET_LEDGER["checkpoint"]),
            "runtime": dict(ASSET_LEDGER["runtime"]),
            "identity_pinned": False,
        },
        "licensing_analysis": {
            "source_terms": "unreviewed; no staged source checkout",
            "checkpoint_terms": "unavailable and unreviewed",
            "training_data_terms": "unreviewed",
            "reference_voice_consent": "unreviewed",
            "output_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact licensed Seed-TTS source, checkpoint, variant, revision, bytes and runtime",
            "rights-cleared consented reference cohort, transcripts and pinned scorers",
            "matched text/semantic, identity and naturalness outcomes on the exact runtime",
            "independent listening, first-output/tail timing and device evidence",
            "opt-in provider intake and release approval",
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
        "# SHA-256 pins for SDK-SEED-TTS.",
        "# source: paths are workspace-relative; other paths are SDK-worktree-relative.",
        "# Local task paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
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
            "No source, checkpoint, audio, cohort or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "Synthetic token controls are labelled and cannot qualify the candidate.",
            "Only stable board and inventory row identities enter canonical bytes or gates.",
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
