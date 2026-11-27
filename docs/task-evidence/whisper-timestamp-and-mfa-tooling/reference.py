# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local blocker evidence for SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING.

Stdlib-only. No Whisper/MFA/PyTorch/runtime download, import, load, execution,
audio read, listening, device timing, benchmark, or release claim. This package
records exact historical provenance pins, absence probes, fail-closed admission
controls, and a DEFER/not_qualified decision for the comparison tooling row.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

TASK = "SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING"
TITLE = "Whisper-timestamp and MFA tooling"
COMPONENT = "whisper-timestamp-and-mfa-tooling"
REPOSITORY = "audio-sdk"
MODE = "research-control"
PROFILE = "evidence"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING"
WRITE_SCOPE = "docs/task-evidence/whisper-timestamp-and-mfa-tooling/ only"
TASK_PREFIX = "docs/task-evidence/whisper-timestamp-and-mfa-tooling/"
CONTRACT_SCHEMA = "audio-sdk/whisper-timestamp-and-mfa-tooling-contract/0.1"
REPORT_SCHEMA = "audio-sdk/whisper-timestamp-and-mfa-tooling-report/0.1"
MANIFEST_SCHEMA = "audio-sdk/whisper-timestamp-and-mfa-tooling-manifest/0.1"

HERE = Path(__file__).resolve().parent
WORKTREE = Path(os.environ.get("WORKTREE_ROOT", str(HERE.parents[2]))).resolve()


def _find_audio_root() -> Path:
    env = os.environ.get("SOURCE_ROOT")
    candidates = [Path(env)] if env else []
    candidates.extend(HERE.parents)
    for c in candidates:
        if (c / "audio-benchmark-platform/plan/swarm/TASKS.json").is_file() and (c / "research").is_dir():
            return c.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-text/REPORT.md": "86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93",
    "research/tsm-followup-20261101/agent-text/run_mfa_alignment_smoke.py": "245f05c557cb7b93ba14887b71fa93ef8098d94478fee4cd9baa1910dac7fa66",
    "research/tsm-followup-20261101/agent-text/run_whisper_asr.py": "7fb7a94b6117b7694ec04d3bb1f6491527c802651135fcf5f05eae8b0782bbd4",
    "research/tsm-followup-20261101/agent-text/score_asr_alignment.py": "0294e7681af9b6491bed6501bd1d7154b6809a9231101209187412c6f5b9c6bf",
    "research/tsm-followup-20261101/agent-text/score_mfa_alignment_smoke.py": "f6b99e3fb0864eea4dab999b875e88a7214fda1142f40e7cc8118c303225bd0a",
    "research/tsm-followup-20261101/agent-text/score_whisper_asr.py": "624558e2835dfb25f2321c6ba3b505107536539164159e461a7c250bee6a27a8",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
}

# Stable board projection only; never hash/pin mutable TASKS.json bytes.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")

ABSENCE_PROBES = [
    {"scope": "workspace", "path": "data/runs/tsm-followup-20261101-mfa"},
    {"scope": "workspace", "path": "data/runs/tsm-followup-20261101-mfa/manifest.json"},
    {"scope": "workspace", "path": "data/runs/tsm-followup-20261101-mfa/asr/whisper_tiny_en_wer.json"},
    {"scope": "workspace", "path": "data/runs/tsm-followup-20261101-mfa/asr/whisper_mfa_alignment_score.json"},
    {"scope": "workspace", "path": "data/tmp/ami/vad-verified-ami-archive/words/EN2003a.A.words.xml"},
    {"scope": "external", "path": "/private/tmp/whisper-model/tiny.en.pt"},
    {"scope": "external", "path": "/private/tmp/asr-mfa-env"},
    {"scope": "external", "path": "/private/tmp/mfa-env"},
    {"scope": "external", "path": "/private/tmp/mfa-root"},
    {"scope": "external", "path": "/private/tmp/EN2003a.Headset-0.wav"},
]


GATES = [
    {"id":"RG-01","status":"blocked","title":"exact_source_runtime_asset_identity","detail":"Exact Whisper/MFA source revisions, package archives, model/acoustic/dictionary assets, hashes, byte counts, and complete license/notice bundles are not staged or verified in-worktree."},
    {"id":"RG-02","status":"blocked","title":"pinned_offline_runtime_and_reproduction","detail":"Pinned offline Whisper+MFA environments with lockfiles/install/import digests, deterministic settings, and clean-room reproduction are absent."},
    {"id":"RG-03","status":"blocked","title":"rights_terms_and_cohort","detail":"AMI crop/annotations, transcript normalization, language/subset pins, and reviewed Whisper/MFA/AMI terms are not locally staged/reviewed for this task package."},
    {"id":"RG-04","status":"blocked","title":"scoring_controls_and_validity","detail":"No fresh WER/boundary/rate scoring with frozen normalizer, matched aligned subset, finite-output checks, and negative controls was produced."},
    {"id":"RG-05","status":"blocked","title":"tool_boundary_and_release","detail":"No opt-in developer/evidence adapter boundary, installed-v0 isolation proof, or independent release review exists; default/shared build/CI/registry remain untouched."},
]

BLOCKERS = [
    {"id":"BLK-01","gate":"RG-01","status":"open","summary":"Exact Whisper tiny.en weight/package/license and MFA 3.4.3 acoustic/dictionary/source/license artifacts are absent or unverified locally.","required":"Stage exact artifacts with immutable digests, byte counts, provenance, and reviewed rights/notice bundles."},
    {"id":"BLK-02","gate":"RG-02","status":"open","summary":"Pinned offline Whisper/MFA runtimes and reproducible execution traces are absent.","required":"Provide locked offline environments, deterministic thread/algorithm settings, install/import digests, and clean-room reproduction logs."},
    {"id":"BLK-03","gate":"RG-03","status":"open","summary":"Exact AMI crop/annotations/language/transcript-normalization subset and rights review are not staged.","required":"Pin exact cohort, normalization, language/subset, source/annotation digests, and reviewed AMI/Whisper/MFA terms."},
    {"id":"BLK-04","gate":"RG-04","status":"open","summary":"No fresh controlled WER/boundary/rate evidence exists; historical report is provenance only.","required":"Run frozen scorers with matched aligned subset, controls, finite/nonfinite checks, and machine-readable outputs."},
    {"id":"BLK-05","gate":"RG-05","status":"open","summary":"No opt-in SDK developer/evidence adapter/tooling boundary has been reviewed; exposure before gates clear is blocked.","required":"Keep adapter/provider OFF/unregistered; after gates clear, separate opt-in intake with independent exact-head review."},
]

HISTORICAL = {
    "provenance_only": True,
    "reproduced_here": False,
    "used_for_evidence": False,
    "qualifies": False,
    "source_report": "research/tsm-followup-20261101/agent-text/REPORT.md",
    "recorded": {
        "whisper_model": "tiny.en",
        "whisper_package": "openai-whisper==20250625",
        "whisper_weight_sha256": "d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03",
        "mfa_version": "3.4.3",
        "mfa_acoustic_sha256": "d35ce271ded357d833d2f4b8d1041dc3748b9538567ba13f2c697f4e4126711b",
        "mfa_dictionary_sha256": "e8c6c7b036ae2b7c78d2768b8dc6b1f9359175b842956d00b48c53c9c332e6b0",
        "ami_crop_sha256": "a8fcab8547e24376367f97ce5967318e18cc6e052fe3f89934ff037dc90bd9ca",
        "wer": "11.76% (4/34)",
        "oracle_boundary_mae_ms": "23.79",
        "asr_boundary_mae_ms": "23.17",
    },
    "caveats": [
        "single 15s AMI crop; not general accuracy/timing/device evidence",
        "AMI timings are forced alignment, not independent timing gold",
        "Whisper/MFA environments and assets absent locally; no rerun performed",
    ],
}

MANIFEST_REQUIRED = {
    "schema_id": str,
    "candidate": str,
    "language": str,
    "transcript_normalization": str,
    "aligned_subset_id": str,
    "whisper": dict,
    "mfa": dict,
    "cohort": dict,
    "rights_reviewed": bool,
    "claims_qualified": bool,
}


class EvidenceError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def canonical_text(obj: Any) -> str:
    return canonical_bytes(obj).decode("utf-8")


def _reject_const(x: str) -> Any:
    raise EvidenceError(f"nonfinite_json:{x}")


def _dup_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise EvidenceError(f"duplicate_key:{k}")
        out[k] = v
    return out


def strict_loads(text: str) -> Any:
    obj = json.loads(text, parse_constant=_reject_const, object_pairs_hook=_dup_hook)
    if isinstance(obj, float):
        raise EvidenceError("float_not_allowed")
    _walk(obj)
    return obj


def strict_load(path: Path) -> Any:
    try:
        return strict_loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise EvidenceError(f"strict_json:{path.name}:{e}") from e


def _walk(x: Any) -> None:
    if isinstance(x, float):
        raise EvidenceError("float_not_allowed")
    if isinstance(x, dict):
        for k, v in x.items():
            if not isinstance(k, str):
                raise EvidenceError("non_string_key")
            _walk(v)
    elif isinstance(x, list):
        for v in x:
            _walk(v)
    elif isinstance(x, (str, int, bool)) or x is None:
        return
    else:
        raise EvidenceError(f"unsupported_type:{type(x).__name__}")


def _pin_rows(pins: dict[str, str], root: Path) -> list[dict[str, Any]]:
    rows = []
    for rel, expected in sorted(pins.items()):
        p = root / rel
        if not p.is_file():
            raise EvidenceError(f"missing_pin:{rel}")
        actual = sha256_file(p)
        if actual != expected:
            raise EvidenceError(f"pin_mismatch:{rel}:{actual}")
        rows.append({"path": rel, "sha256": expected, "bytes": p.stat().st_size})
    return rows


def board_row_projection() -> dict[str, Any]:
    board = strict_load(AUDIO_ROOT / BOARD_TASK_ROW)
    tasks = board.get("tasks")
    if not isinstance(tasks, list):
        raise EvidenceError("board_tasks_invalid")
    row = None
    for t in tasks:
        if isinstance(t, dict) and t.get("id") == TASK:
            row = t
            break
    if row is None:
        raise EvidenceError("board_row_missing")
    proj = {k: row.get(k) for k in BOARD_ROW_FIELDS}
    if proj.get("id") != TASK or proj.get("component") != COMPONENT:
        raise EvidenceError("board_row_identity_mismatch")
    return proj


def absence_rows() -> list[dict[str, Any]]:
    rows = []
    for probe in ABSENCE_PROBES:
        p = Path(probe["path"])
        if probe["scope"] == "workspace":
            p = AUDIO_ROOT / probe["path"]
        rows.append({"scope": probe["scope"], "path": probe["path"], "present": p.exists()})
    return rows


def validate_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise EvidenceError("manifest_not_object")
    extra = sorted(set(manifest) - set(MANIFEST_REQUIRED))
    missing = sorted(set(MANIFEST_REQUIRED) - set(manifest))
    if extra:
        raise EvidenceError("manifest_unknown_field:" + ",".join(extra))
    if missing:
        raise EvidenceError("manifest_missing_field:" + ",".join(missing))
    for k, t in MANIFEST_REQUIRED.items():
        if not isinstance(manifest[k], t):
            raise EvidenceError(f"manifest_type:{k}")
    if manifest["schema_id"] != MANIFEST_SCHEMA:
        raise EvidenceError("manifest_schema_id")
    if manifest["candidate"] != COMPONENT:
        raise EvidenceError("manifest_candidate")
    if not manifest["language"] or not isinstance(manifest["language"], str):
        raise EvidenceError("manifest_language")
    if not manifest["transcript_normalization"].strip():
        raise EvidenceError("manifest_normalization")
    if not manifest["aligned_subset_id"].strip():
        raise EvidenceError("manifest_subset")
    if manifest["claims_qualified"] is not False:
        raise EvidenceError("manifest_claims_qualified")
    if manifest["rights_reviewed"] is not True:
        raise EvidenceError("manifest_rights_reviewed")
    for section, fields in {
        "whisper": ["model","package","weight_sha256","license"],
        "mfa": ["version","acoustic_model","dictionary","acoustic_sha256","dictionary_sha256","license"],
        "cohort": ["id","audio_sha256","annotation_sha256","sample_rate_hz","channels","sample_count"],
    }.items():
        obj = manifest[section]
        extra_s = sorted(set(obj) - set(fields))
        missing_s = sorted(set(fields) - set(obj))
        if extra_s or missing_s:
            raise EvidenceError(f"manifest_{section}_fields")
        for f in fields:
            v = obj[f]
            if f in ("sample_rate_hz","channels","sample_count"):
                if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                    raise EvidenceError(f"manifest_{section}_{f}")
            else:
                if not isinstance(v, str) or not v.strip():
                    raise EvidenceError(f"manifest_{section}_{f}")
    if manifest["cohort"]["channels"] != 1:
        raise EvidenceError("manifest_channels")
    return {"accepted": True, "schema_id": MANIFEST_SCHEMA, "qualifies": False, "label": "synthetic_schema_control_not_evidence"}


ADVERSE_MANIFEST_CASES = [
    ("missing_schema", lambda m: m.pop("schema_id")),
    ("unknown_field", lambda m: m.__setitem__("extra", True)),
    ("wrong_schema", lambda m: m.__setitem__("schema_id", "wrong")),
    ("wrong_candidate", lambda m: m.__setitem__("candidate", "other")),
    ("empty_language", lambda m: m.__setitem__("language", "")),
    ("claims_qualified_true", lambda m: m.__setitem__("claims_qualified", True)),
    ("rights_not_reviewed", lambda m: m.__setitem__("rights_reviewed", False)),
    ("bad_whisper_type", lambda m: m.__setitem__("whisper", [])),
    ("missing_cohort_field", lambda m: m["cohort"].pop("audio_sha256")),
    ("bad_channels", lambda m: m["cohort"].__setitem__("channels", 2)),
    ("bad_sample_rate", lambda m: m["cohort"].__setitem__("sample_rate_hz", 0)),
    ("nonint_sample_count", lambda m: m["cohort"].__setitem__("sample_count", "240000")),
]


def adverse_manifest_results() -> list[dict[str, Any]]:
    base = {
        "schema_id": MANIFEST_SCHEMA,
        "candidate": COMPONENT,
        "language": "en",
        "transcript_normalization": "lowercase_punct_strip_whitespace_collapse",
        "aligned_subset_id": "ami-en2003a-16s31s-headset0",
        "whisper": {"model":"tiny.en","package":"openai-whisper==20250625","weight_sha256":"d"*64,"license":"MIT"},
        "mfa": {"version":"3.4.3","acoustic_model":"english_us_arpa","dictionary":"english_us_arpa","acoustic_sha256":"a"*64,"dictionary_sha256":"b"*64,"license":"CC-BY-4.0"},
        "cohort": {"id":"EN2003a-16-31","audio_sha256":"c"*64,"annotation_sha256":"e"*64,"sample_rate_hz":16000,"channels":1,"sample_count":240000},
        "rights_reviewed": True,
        "claims_qualified": False,
    }
    out = []
    for name, mutate in ADVERSE_MANIFEST_CASES:
        m = json.loads(json.dumps(base))
        mutate(m)
        try:
            validate_manifest(m)
            out.append({"case": name, "rejected": False, "error": "accepted"})
        except Exception as e:
            out.append({"case": name, "rejected": True, "error": str(e).split(":")[0]})
    return out


def boundary_state() -> dict[str, bool]:
    return {
        "adapter_registered": False,
        "provider_registered": False,
        "default_enabled": False,
        "installed_v0_changed": False,
        "public_abi_changed": False,
        "contracts_changed": False,
        "registry_changed": False,
        "shared_build_changed": False,
        "ci_changed": False,
        "network_used": False,
        "real_audio_used": False,
        "model_executed": False,
        "listening_performed": False,
        "device_timing_measured": False,
        "benchmark_claimed": False,
        "release_claimed": False,
    }


def build_contract() -> dict[str, Any]:
    proj = board_row_projection()
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "deliverable": "Retain or reproduce the comparison as an optional SDK developer/evidence adapter alongside audio-bench, with a documented proceed/defer decision before exposing it as a processor. Keep language, transcript normalization and actual aligned subset pinned for WER and rate evidence.",
        "acceptance": "Apply the evidence acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates.",
        "board_row_projection": proj,
        "board_row_projection_sha256": sha256_bytes(canonical_bytes(proj)),
        "gates": GATES,
        "blockers": BLOCKERS,
        "historical": HISTORICAL,
        "boundary": boundary_state(),
        "absence_probes": absence_rows(),
        "source_pins": _pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": _pin_rows(BOUNDARY_PINS, WORKTREE),
        "admission": {
            "schema_id": MANIFEST_SCHEMA,
            "control_accept": validate_manifest({
                "schema_id": MANIFEST_SCHEMA,
                "candidate": COMPONENT,
                "language": "en",
                "transcript_normalization": "lowercase_punct_strip_whitespace_collapse",
                "aligned_subset_id": "ami-en2003a-16s31s-headset0",
                "whisper": {"model":"tiny.en","package":"openai-whisper==20250625","weight_sha256":"d"*64,"license":"MIT"},
                "mfa": {"version":"3.4.3","acoustic_model":"english_us_arpa","dictionary":"english_us_arpa","acoustic_sha256":"a"*64,"dictionary_sha256":"b"*64,"license":"CC-BY-4.0"},
                "cohort": {"id":"EN2003a-16-31","audio_sha256":"c"*64,"annotation_sha256":"e"*64,"sample_rate_hz":16000,"channels":1,"sample_count":240000},
                "rights_reviewed": True,
                "claims_qualified": False,
            }),
            "adverse_cases": adverse_manifest_results(),
        },
        "non_claims": [
            "No Whisper/MFA/PyTorch/runtime downloaded, imported, loaded, or executed.",
            "No real audio, transcript, TextGrid, listening, device timing, benchmark, or release claim.",
            "Historical report numbers are provenance only, not reproduced or qualifying.",
            "No provider/adapter registered or enabled by default; no public ABI/CONTRACTS/registry/shared build/CI change.",
        ],
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    adverse = contract["admission"]["adverse_cases"]
    return {
        "schema_id": REPORT_SCHEMA,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "board_row_projection": contract["board_row_projection"],
        "board_row_projection_sha256": contract["board_row_projection_sha256"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "absence_probes": contract["absence_probes"],
        "gates": contract["gates"],
        "blockers": contract["blockers"],
        "historical": contract["historical"],
        "admission": contract["admission"],
        "boundary": contract["boundary"],
        "controls": {
            "adverse_manifest_cases": len(adverse),
            "adverse_manifest_all_rejected": all(c["rejected"] for c in adverse),
            "control_manifest_accepted": contract["admission"]["control_accept"]["accepted"],
            "missing_result_qualifies": False,
        },
        "non_claims": contract["non_claims"],
        "contract_sha256": sha256_bytes(canonical_bytes(contract)),
    }


def check_scope(worktree: Path = WORKTREE, task_prefix: str = TASK_PREFIX) -> dict[str, Any]:
    result = {"status": "ok", "base": None, "changed": [], "violations": []}
    try:
        proc = subprocess.run(["git","-C",str(worktree),"remote","get-url","origin"], capture_output=True, text=True, check=False)
        has_origin = proc.returncode == 0
        base = None
        if has_origin:
            for ref in ("origin/main","main"):
                p = subprocess.run(["git","-C",str(worktree),"rev-parse","--verify",ref], capture_output=True, text=True, check=False)
                if p.returncode == 0:
                    base = ref
                    break
        if base is None:
            result["status"] = "scope_base_unavailable"
            return result
        result["base"] = base
        mb = subprocess.run(["git","-C",str(worktree),"merge-base",base,"HEAD"], capture_output=True, text=True, check=False)
        if mb.returncode != 0:
            result["status"] = "scope_base_unavailable"
            return result
        base_commit = mb.stdout.strip()
        diff = subprocess.run(["git","-C",str(worktree),"diff","--name-only",base_commit,"HEAD"], capture_output=True, text=True, check=False)
        if diff.returncode != 0:
            result["status"] = "scope_base_unavailable"
            return result
        changed = [x for x in diff.stdout.splitlines() if x.strip()]
        result["changed"] = changed
        result["violations"] = [p for p in changed if not p.startswith(task_prefix)]
    except Exception:
        result["status"] = "scope_base_unavailable"
    return result
