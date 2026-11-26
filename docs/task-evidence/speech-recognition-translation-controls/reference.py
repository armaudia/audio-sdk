# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence for SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS.

Feasibility/DEFER package only. No ASR/translation runtime, weights, corpus,
network, device timing, listening, benchmark, provider registration, or
release claim is made. Caller manifests are metadata-only and fail closed.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_PREFIX = "docs/task-evidence/speech-recognition-translation-controls/"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/speech-recognition-translation-controls/caller-supplied/0.1"
TASK_ID = "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS"
TITLE = "Speech recognition / translation controls"
COMPONENT = "speech-recognition-translation-controls"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = "swarm/SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS"
REVIEWER = "reviewer-SPEECH-RECOGNITION-TRANSLATION-CONTROLS"
PROFILE = "tool"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_incomplete"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"

BOARD_LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)
INVENTORY_COMPONENT_FIELDS = (
    "id", "name", "area", "evidence_status", "repository", "disposition",
    "verification_profile", "task",
)
SCOPE_BASE_REFS = ("origin/main", "main")

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/TASKS.json": "adbbda3fb9708d41f7d3d75a2d2c1d6433666a2823be50b03fab4628794ab392",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_STABLE_SHA256 = "2dbd125fb0ee6425959db51dd2772e385fd968a6450e5b181242c69452fd90ff"
INVENTORY_STABLE_SHA256 = "597efdd515a4decd605f8568f7e38b6271c2808441e5b96bc5c1a37cea8cfcfd"

LOCAL_PIN_PATHS: Tuple[str, ...] = (
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

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_asr_translation_runtime_and_rights",
    "source_checkout": {"status": "absent", "revision": None, "license": None,
                        "note": "No ASR/translation source checkout is staged at a fixed probe path."},
    "artifact": {"path": None, "revision": None, "byte_count": None, "sha256": None,
                 "present_locally": False,
                 "note": "No exact model/runtime artifact, byte count, or SHA-256 is staged."},
    "runtime": {"status": "absent_unpinned", "lockfile": None, "sha256": None,
                "note": "No locked runtime, decoder, tokenizer, translation model, or endpoint contract is staged."},
    "rights": {"status": "absent_unreviewed",
               "note": "No reviewed license, data rights, or output-use grant is staged."},
    "downloaded": False, "vendored": False, "loaded": False, "executed": False,
    "network_used": False,
}

BOUNDARY: Dict[str, Any] = {
    "benchmark_claim": False,
    "board_or_handoff_changed": False,
    "ci_changed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "format": {"channels": CHANNELS, "frame_samples": FRAME_SAMPLES,
               "sample_format": SAMPLE_FORMAT, "sample_rate_hz": SAMPLE_RATE_HZ},
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "processor_exposure": False,
    "provider_registered": False,
    "public_api_abi_changed": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}
SCOPE: Dict[str, Any] = {
    "benchmark": False, "device_timing": False, "listening": False,
    "model_executed": False, "network_used": False, "provider_registered": False,
    "real_audio": False, "asr_runtime_loaded": False, "synthetic_only": True,
    "task_local_only": True,
}

NEGATIVE_CLAIMS: List[str] = [
    "No ASR, STT, translation, diarization, alignment, or endpoint runtime is imported, downloaded, loaded, or executed.",
    "No model weights, tokenizer, language pack, corpus, transcript, audio, or translation artifact is vendored or used.",
    "No real transcription, translation, timestamp, confidence, language ID, or endpoint result is present.",
    "Synthetic control probes are structural only and cannot qualify recognition, translation, timing, or release readiness.",
    "No device timing, listening, benchmark, provider registration, default selection, or release claim is made.",
    "No missing, blocked, source-reported, or synthetic result qualifies the candidate.",
]

EXACT_BLOCKERS: List[Dict[str, str]] = [
    {"id": "XB-01", "title": "exact_asr_translation_runtime_absent",
     "detail": "No exact runnable ASR/translation source, runtime, or pinned artifact with immutable revision, bytes, SHA-256, and reviewed rights is staged.",
     "reopen": "Provide an exactly pinned runnable ASR/translation runtime or separately licensed artifact with immutable revision, bytes, SHA-256, and a reviewed rights record."},
    {"id": "XB-02", "title": "typed_transcript_segmentation_language_contract_unpinned",
     "detail": "No typed transcript, segmentation clock, unknown-language behavior, or versioned normalization contract is pinned for deterministic SDK-facing adapter output.",
     "reopen": "Pin typed transcript/segment/language/normalization schemas and deterministic fail-closed validation on the exact runtime."},
    {"id": "XB-03", "title": "matched_cohort_controls_and_scorers_absent",
     "detail": "No rights-cleared matched cohort, transcript/translation references, controls, or pinned scorers are staged for recognition, translation, or timing quality.",
     "reopen": "Freeze a rights-cleared cohort with references, controls, and pinned scoring for recognition, translation, segmentation, and unknown-language behavior."},
    {"id": "XB-04", "title": "release_timing_rights_and_review_gates_unmet",
     "detail": "No target-device timing, rights/output-use review, opt-in intake, independent review, or release approval exists.",
     "reopen": "Measure paced target-runtime behavior, clear rights/output use, and pass independent opt-in review with default OFF before any exposure."},
]

GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "exact_runtime_artifact_and_rights_identity",
     "statement": "An exact runnable ASR/translation runtime or artifact revision, immutable bytes, SHA-256, and reviewed rights/output-use terms must be pinned.",
     "reopen_condition": "Stage a reviewed, exactly pinned runtime/artifact with immutable revision, byte count, SHA-256, and rights record."},
    {"id": "RG-02", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "typed_transcript_and_normalization_contract",
     "statement": "Typed transcript, segment timing, confidence, unknown-language, and versioned normalization contracts must be deterministic and fail closed.",
     "reopen_condition": "Pin schemas and pass deterministic validation/adverse cases on the exact runtime without guessing missing fields."},
    {"id": "RG-03", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "segmentation_clock_and_endpoint_semantics",
     "statement": "Segmentation clock, partial/final endpoint semantics, and source timestamp mapping must be exact and independently verifiable.",
     "reopen_condition": "Provide exact clock mapping, partial/final/end-of-stream semantics, and deterministic timestamp tests on the target runtime."},
    {"id": "RG-04", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "unknown_language_and_translation_scope",
     "statement": "Unknown language, unsupported language, and translation scope must be explicit typed outcomes, never silent fallback or fabricated text.",
     "reopen_condition": "Freeze language/translation scope and prove fail-closed unknown/unsupported behavior with reviewed references."},
    {"id": "RG-05", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "frozen_cohort_controls_and_scorers",
     "statement": "A rights-cleared matched cohort with references, controls, and pinned scorers is required for recognition, translation, and timing quality.",
     "reopen_condition": "Freeze cohort/splits/references/scorers and produce matched evidence on the exact runtime."},
    {"id": "RG-06", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "adverse_invalid_nonfinite_and_missing_input_handling",
     "statement": "Missing, invalid, malformed, nonfinite, out-of-range, and rights-missing inputs must fail closed with no partial qualifying result.",
     "reopen_condition": "Pass deterministic adverse coverage with no state mutation or qualifying output on rejection."},
    {"id": "RG-07", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "paced_timing_and_target_runtime",
     "statement": "Paced target-runtime availability, latency, memory, and endpoint timing must be measured on the exact runtime and device class.",
     "reopen_condition": "Measure paced availability/latency/resource behavior on target hardware with explicit deadline accounting."},
    {"id": "RG-08", "linked_row": TASK_ID, "qualifies": False, "status": "blocked",
     "title": "opt_in_intake_review_and_release",
     "statement": "An opt-in, default-OFF provider/tool intake, independent exact-head review, and release approval are required before exposure.",
     "reopen_condition": "Pass a separate versioned intake and independent review with no default registration and no release claim."},
]

MANIFEST_REQUIRED = {
    "schema_id": str, "adapter": str, "configuration_id": str,
    "runtime_path": str, "runtime_sha256": str, "runtime_byte_count": int,
    "runtime_revision": str, "runtime_license_digest": str, "rights_digest": str,
    "sample_rate_hz": int, "channels": int, "frame_samples": int, "sample_format": str,
}
MANIFEST_ALLOWED_ADAPTERS = {"speech-recognition-translation-controls"}
MANIFEST_ALLOWED_CONFIGS = {"asr-translation-offline-first"}


class DuplicateKey(ValueError):
    pass


def strict_loads(text: str) -> Any:
    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise DuplicateKey("duplicate_key:" + key)
            obj[key] = value
        return obj

    value = json.loads(text, object_pairs_hook=object_pairs_hook, parse_constant=_reject_constant)
    return value


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_constant:" + token)


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(worktree: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(worktree), *args], capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    r = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    c = r.stdout.strip()
    return c if r.returncode == 0 and c else None


def scope_base(worktree: Path, refs: Sequence[str] = SCOPE_BASE_REFS) -> str | None:
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        r = _git(worktree, "merge-base", "HEAD", ref)
        base = r.stdout.strip()
        if r.returncode != 0 or not base:
            continue
        if best is None or (best != base and _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0):
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    r = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if r.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + r.stderr.strip())
    return [line for line in r.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [p for p in paths if p and not p.startswith(prefix)]


def _read_source_pin(path: str) -> str:
    abs_path = SOURCE_ROOT / path
    if not abs_path.is_file():
        raise FileNotFoundError("missing_source_pin:" + path)
    return sha256_file(abs_path)


def verify_source_pins() -> Dict[str, Any]:
    mismatches = []
    actual: Dict[str, str] = {}
    for path, expected in SOURCE_PINS.items():
        got = _read_source_pin(path)
        actual[path] = got
        if got != expected:
            mismatches.append({"path": path, "expected": expected, "actual": got})
    return {"ok": not mismatches, "actual": actual, "mismatches": mismatches}


def verify_boundary_pins() -> Dict[str, Any]:
    mismatches = []
    actual: Dict[str, str] = {}
    for path, expected in BOUNDARY_PINS.items():
        abs_path = SDK_ROOT / path
        if not abs_path.is_file():
            mismatches.append({"path": path, "expected": expected, "actual": None, "error": "missing"})
            continue
        got = sha256_file(abs_path)
        actual[path] = got
        if got != expected:
            mismatches.append({"path": path, "expected": expected, "actual": got})
    return {"ok": not mismatches, "actual": actual, "mismatches": mismatches}


def _load_board_row() -> Dict[str, Any]:
    board = strict_loads((SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json").read_text(encoding="utf-8"))
    for task in board.get("tasks", []):
        if task.get("id") == TASK_ID:
            return {k: task[k] for k in BOARD_LINK_FIELDS}
    raise KeyError("board_row_missing:" + TASK_ID)


def _load_inventory_row() -> Dict[str, Any]:
    inv = strict_loads((SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json").read_text(encoding="utf-8"))
    for row in inv.get("components", []):
        if row.get("id") == COMPONENT or row.get("task") == TASK_ID:
            return {k: row[k] for k in INVENTORY_COMPONENT_FIELDS if k in row}
    raise KeyError("inventory_row_missing:" + COMPONENT)


def board_link() -> Dict[str, Any]:
    row = _load_board_row()
    digest = sha256_bytes(canonical_bytes(row))
    return {
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "stable_fields": row,
        "stable_sha256": digest,
    }


def inventory_link() -> Dict[str, Any]:
    row = _load_inventory_row()
    digest = sha256_bytes(canonical_bytes(row))
    return {
        "full_inventory_hashed": False,
        "stable_fields": row,
        "stable_sha256": digest,
    }


def _is_hex64(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        return {"ok": False, "error": "INVALID_MANIFEST", "metrics": None}
    extra = sorted(set(manifest.keys()) - set(MANIFEST_REQUIRED.keys()))
    if extra:
        return {"ok": False, "error": "UNKNOWN_FIELD:" + extra[0], "metrics": None}
    missing = sorted(set(MANIFEST_REQUIRED.keys()) - set(manifest.keys()))
    if missing:
        return {"ok": False, "error": "MISSING_FIELD:" + missing[0], "metrics": None}
    for key, typ in MANIFEST_REQUIRED.items():
        if typ is int:
            if not isinstance(manifest[key], int) or isinstance(manifest[key], bool):
                return {"ok": False, "error": "BAD_TYPE:" + key, "metrics": None}
        elif not isinstance(manifest[key], typ):
            return {"ok": False, "error": "BAD_TYPE:" + key, "metrics": None}
    if manifest["schema_id"] != SCHEMA_MANIFEST:
        return {"ok": False, "error": "UNKNOWN_SCHEMA", "metrics": None}
    if manifest["adapter"] not in MANIFEST_ALLOWED_ADAPTERS:
        return {"ok": False, "error": "UNKNOWN_ADAPTER", "metrics": None}
    if manifest["configuration_id"] not in MANIFEST_ALLOWED_CONFIGS:
        return {"ok": False, "error": "UNKNOWN_CONFIGURATION", "metrics": None}
    for key in ("runtime_sha256", "runtime_license_digest", "rights_digest"):
        if not _is_hex64(manifest[key]):
            return {"ok": False, "error": "BAD_DIGEST:" + key, "metrics": None}
    if not manifest["runtime_revision"] or "\n" in manifest["runtime_revision"]:
        return {"ok": False, "error": "BAD_RUNTIME_REVISION", "metrics": None}
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ or manifest["channels"] != CHANNELS or manifest["frame_samples"] != FRAME_SAMPLES or manifest["sample_format"] != SAMPLE_FORMAT:
        return {"ok": False, "error": "FORMAT_MISMATCH", "metrics": None}
    if manifest["runtime_byte_count"] <= 0:
        return {"ok": False, "error": "BAD_BYTE_COUNT", "metrics": None}
    runtime_path = Path(manifest["runtime_path"])
    if not runtime_path.is_absolute():
        return {"ok": False, "error": "RELATIVE_RUNTIME", "metrics": None}
    if not runtime_path.is_file():
        return {"ok": False, "error": "ASSET_ABSENT", "metrics": None}
    payload = runtime_path.read_bytes()
    if len(payload) != manifest["runtime_byte_count"]:
        return {"ok": False, "error": "BAD_BYTE_COUNT", "metrics": None}
    if sha256_bytes(payload) != manifest["runtime_sha256"]:
        return {"ok": False, "error": "BAD_RUNTIME_DIGEST", "metrics": None}
    return {"ok": False, "error": "ASR_TRANSLATION_RUNTIME_IDENTITY_UNPINNED", "metrics": None}

def valid_manifest(runtime_path: Path) -> Dict[str, Any]:
    payload = runtime_path.read_bytes()
    return {
        "schema_id": SCHEMA_MANIFEST,
        "adapter": "speech-recognition-translation-controls",
        "configuration_id": "asr-translation-offline-first",
        "runtime_path": str(runtime_path),
        "runtime_sha256": sha256_bytes(payload),
        "runtime_byte_count": len(payload),
        "runtime_revision": "deadbeef",
        "runtime_license_digest": "0" * 64,
        "rights_digest": "1" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    }


def adverse_cases(runtime_path: Path) -> Dict[str, Any]:
    cases = []
    base = valid_manifest(runtime_path)

    def add(name: str, manifest: Any, expected: str) -> None:
        r = validate_manifest(manifest)
        cases.append({"id": name, "expected": expected, "observed": r["error"], "accepted": r["ok"]})

    add("manifest_not_object", [], "INVALID_MANIFEST")
    bad = dict(base); bad["extra"] = 1; add("unknown_field", bad, "UNKNOWN_FIELD:extra")
    bad = dict(base); del bad["adapter"]; add("missing_field", bad, "MISSING_FIELD:adapter")
    bad = dict(base); bad["schema_id"] = "wrong"; add("unknown_schema", bad, "UNKNOWN_SCHEMA")
    bad = dict(base); bad["adapter"] = "other"; add("unknown_adapter", bad, "UNKNOWN_ADAPTER")
    bad = dict(base); bad["configuration_id"] = "other"; add("unknown_configuration", bad, "UNKNOWN_CONFIGURATION")
    bad = dict(base); bad["runtime_sha256"] = "abc"; add("bad_digest", bad, "BAD_DIGEST:runtime_sha256")
    bad = dict(base); bad["runtime_revision"] = ""; add("bad_revision", bad, "BAD_RUNTIME_REVISION")
    bad = dict(base); bad["sample_rate_hz"] = 8000; add("format_mismatch", bad, "FORMAT_MISMATCH")
    bad = dict(base); bad["runtime_byte_count"] = 0; add("bad_byte_count_zero", bad, "BAD_BYTE_COUNT")
    bad = dict(base); bad["runtime_byte_count"] = True; add("bad_type_bool", bad, "BAD_TYPE:runtime_byte_count")
    bad = dict(base); bad["runtime_path"] = "relative.bin"; add("relative_runtime", bad, "RELATIVE_RUNTIME")
    bad = dict(base); bad["runtime_path"] = str(runtime_path.parent / "missing.bin"); add("asset_absent", bad, "ASSET_ABSENT")
    bad = dict(base); bad["runtime_sha256"] = "f" * 64; add("bad_runtime_digest", bad, "BAD_RUNTIME_DIGEST")
    bad = dict(base); bad["runtime_byte_count"] = base["runtime_byte_count"] + 1; add("bad_byte_count_mismatch", bad, "BAD_BYTE_COUNT")
    add("hash_matched_still_unpinned", base, "ASR_TRANSLATION_RUNTIME_IDENTITY_UNPINNED")

    invalid_json_cases = []
    for idx, text in enumerate(["{", '{"a":1,', '{"a": NaN}', '{"a": Infinity}', '{"a":1}x', '{"a":1,"a":2}', "[1,2,]"]):
        try:
            strict_loads(text)
            invalid_json_cases.append({"id": f"json-{idx}", "accepted": True, "observed": "ACCEPTED"})
        except Exception as exc:  # noqa: BLE001
            invalid_json_cases.append({"id": f"json-{idx}", "accepted": False, "observed": exc.__class__.__name__})

    invalid_pin_cases = []
    for idx, item in enumerate([("", "sha"), ("a", "nothex" * 8), ("a", "0" * 63), ("a", "0" * 65), ("/abs", "0" * 64)]):
        path, digest = item
        ok = bool(path) and not path.startswith("/") and ".." not in Path(path).parts and _is_hex64(digest)
        invalid_pin_cases.append({"id": f"pin-{idx}", "accepted": ok, "observed": "ACCEPTED" if ok else "INVALID_PIN"})

    return {
        "all_rejected": all(not c["accepted"] for c in cases),
        "case_count": len(cases),
        "cases": cases,
        "invalid_json": {
            "all_rejected": all(not c["accepted"] for c in invalid_json_cases),
            "case_count": len(invalid_json_cases),
            "cases": invalid_json_cases,
            "accepted_count": sum(1 for c in invalid_json_cases if c["accepted"]),
        },
        "invalid_pins": {
            "all_rejected": all(not c["accepted"] for c in invalid_pin_cases),
            "case_count": len(invalid_pin_cases),
            "cases": invalid_pin_cases,
            "accepted_count": sum(1 for c in invalid_pin_cases if c["accepted"]),
        },
    }


def synthetic_controls() -> Dict[str, Any]:
    # Structural only: verifies deterministic timestamp math and fail-closed normalization.
    samples = [0, 159, 160, 321]
    offsets = []
    for n in samples:
        offsets.append({"input_samples": n, "start_ms": int(n * 1000 / SAMPLE_RATE_HZ), "end_frame_samples": ((n + FRAME_SAMPLES - 1) // FRAME_SAMPLES) * FRAME_SAMPLES})
    bad = []
    for name, text in [("nan", "NaN"), ("inf", "Infinity"), ("unknown_lang", "xx-fake"), ("empty", "")]:
        try:
            if text in ("NaN", "Infinity"):
                v = float(text)
                if not math.isfinite(v):
                    raise ValueError("nonfinite")
                bad.append({"id": name, "accepted": True, "observed": "ACCEPTED"})
            elif text == "":
                raise ValueError("empty")
            elif text == "xx-fake":
                raise ValueError("unknown_language")
            else:
                bad.append({"id": name, "accepted": True, "observed": "ACCEPTED"})
        except Exception as exc:  # noqa: BLE001
            bad.append({"id": name, "accepted": False, "observed": exc.__class__.__name__ + ":" + str(exc)})
    return {
        "qualifies_candidate": False,
        "note": "Synthetic structural controls only; not ASR/translation output, not quality, not timing evidence.",
        "timestamp_mapping": {"sample_rate_hz": SAMPLE_RATE_HZ, "frame_samples": FRAME_SAMPLES, "cases": offsets},
        "normalization_rejections": {"all_rejected": all(not c["accepted"] for c in bad), "cases": bad},
    }

def _local_artifact_pins(report_payload: bytes | None = None, sidecar_payload: bytes | None = None, sources_payload: bytes | None = None) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        p = TASK_DIR / name
        if p.is_file():
            pins[TASK_PREFIX + name] = sha256_file(p)
    if report_payload is not None:
        pins[TASK_PREFIX + "report.json.sha256"] = sha256_bytes(sidecar_payload or b"")
        pins[TASK_PREFIX + "SOURCES.sha256"] = sha256_bytes(sources_payload or b"")
    return dict(sorted(pins.items()))


def build_report(runtime_probe: Path | None = None) -> Dict[str, Any]:
    probe_path = runtime_probe or (TASK_DIR / "_probe_runtime.bin")
    created = False
    if not probe_path.exists():
        probe_path.write_bytes(b"probe-runtime")
        created = True
    try:
        adverse = adverse_cases(probe_path)
        controls = synthetic_controls()
    finally:
        if created and probe_path.exists():
            probe_path.unlink()

    board = board_link()
    inv = inventory_link()
    source_pin_check = verify_source_pins()
    boundary_pin_check = verify_boundary_pins()
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
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
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "source_pin_check": source_pin_check,
        "boundary_pins": dict(BOUNDARY_PINS),
        "boundary_pin_check": boundary_pin_check,
        "asset_ledger": dict(ASSET_LEDGER),
        "board_link": board,
        "inventory_link": inv,
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "configurations": sorted(MANIFEST_ALLOWED_CONFIGS),
            "required_fields": sorted(MANIFEST_REQUIRED.keys()),
            "format": dict(BOUNDARY["format"]),
            "executed": False, "loaded": False,
            "note": "Metadata-only. Hash-matched runtime still fails as ASR_TRANSLATION_RUNTIME_IDENTITY_UNPINNED; no runtime is loaded or executed.",
        },
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "adverse": adverse,
        "synthetic_controls": controls,
        "comparison": {"qualifies_candidate": False, "status": "blocked_no_exact_runtime_contract_cohort_or_timing", "task_matched_baseline": "blocked", "source_reported_parity": "not_claimed"},
        "evidence_classes": {"real_local_model_output": False, "real_audio": False, "source_reported": False, "synthetic": True, "listening": False, "device_timing": False, "benchmark": False},
        "no_missing_result_qualifies_candidate": True,
        "reopening_conditions": [b["reopen"] for b in EXACT_BLOCKERS],
    }
    return report


def report_bytes(runtime_probe: Path | None = None) -> bytes:
    return canonical_bytes(build_report(runtime_probe))


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("utf-8")


def sources_entries(report_payload: bytes, sidecar_payload: bytes, contract_payload: bytes | None = None) -> List[Tuple[str, str]]:
    entries: List[Tuple[str, str]] = []
    for name in LOCAL_PIN_PATHS:
        p = TASK_DIR / name
        if p.is_file():
            entries.append((TASK_PREFIX + name, sha256_file(p)))
    for path, digest in sorted(SOURCE_PINS.items()):
        entries.append(("source:" + path, digest))
    for path, digest in sorted(BOUNDARY_PINS.items()):
        entries.append((path, digest))
    return sorted(entries)


def sources_bytes(report_payload: bytes, sidecar_payload: bytes, contract_payload: bytes | None = None) -> bytes:
    lines = [f"{digest}  {path}" for path, digest in sources_entries(report_payload, sidecar_payload, contract_payload)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_contract(report: Dict[str, Any], report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes) -> Dict[str, Any]:
    contract = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
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
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "board_link": report["board_link"],
        "inventory_link": report["inventory_link"],
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "artifact_pins": _local_artifact_pins(report_payload, sidecar_payload, sources_payload),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Only the task-local evidence directory is written.",
            "No ASR/translation runtime, weights, audio, or corpus artifact is bundled.",
            "Caller manifests are metadata-only and never loaded or executed.",
            "Synthetic controls are structural only and cannot qualify the candidate.",
            "Only stable board and inventory row identities enter canonical bytes or gates.",
        ],
    }
    return contract


def contract_bytes(report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any] | None = None) -> bytes:
    rep = report if report is not None else strict_loads(report_payload.decode("utf-8"))
    return canonical_bytes(build_contract(rep, report_payload, sidecar_payload, sources_payload))
