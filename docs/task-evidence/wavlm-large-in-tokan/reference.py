# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence for SDK-WAVLM-LARGE-IN-TOKAN.

Research-control, proposal-only, incomplete, not_qualified. No upstream source,
checkpoint, runtime, audio, listening, device timing, benchmark, provider,
registry, default, ABI, CONTRACTS, shared build or CI change is made.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
WORKSPACE_ROOT = SDK_ROOT.parents[2]

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/wavlm-large-in-tokan/caller-supplied/0.1"
TASK_ID = "SDK-WAVLM-LARGE-IN-TOKAN"
TITLE = "WavLM-Large in TokAN"
COMPONENT = "wavlm-large-in-tokan"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-WAVLM-LARGE-IN-TOKAN"
PROFILE = "Voice"
DECISION = "DEFER"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_research_control_incomplete"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
TASK_PREFIX = "docs/task-evidence/wavlm-large-in-tokan/"
SCOPE_BASE_REFS = ("origin/main", "main")
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"

TOKAN_REPO = "https://github.com/P1ping/TokAN.git"
TOKAN_COMMIT = "cbfc09a2716003463a0501ceae04ee62809c3822"
WAVLM_REPO = "microsoft/wavlm-large"
WAVLM_LAYER = 22

SOURCE_PINS: Dict[str, str] = {
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/repos/TokAN/README.md":
        "e1686415f5cb77ed570f0284322fa67883663d52bed081c0f1287fff42fb2700",
    "research/accent-conversion-20261101/repos/TokAN/infer_wav.py":
        "85ccde2fca4e2d8dc34c686c5a9c4ee2a80fa666e1e8d5c7a9b50c6b4fd82bd5",
    "research/accent-conversion-20261101/repos/TokAN/configs/tokan.model-only.yaml":
        "63280ebc0d0ad68730e780a11cca927e0890e2164ba966424caf9a4580fc8f45",
    "research/accent-conversion-20261101/repos/TokAN/requirements.txt":
        "31baee3dc62a6a5b68130b158a9ff3ec0702203cce9f753dc3febd822cf95c7f",
    "research/accent-conversion-20261101/repos/TokAN/tokan/model/ssl_wrapper/wavlm_extractor.py":
        "e11d07fb6269834443ee33ecdc21dba0357d1e748ffe99f2a6f7033027cb34e4",
    "research/accent-conversion-20261101/repos/TokAN/tokan/model/ssl_quant/vq_joint.py":
        "504097caf3fdad4911fa5e6643af853072959935bd3430335d21becc789d6a13",
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
}

LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "README.md",
    "LICENSES.md",
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

BOARD_STABLE_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
BOARD_STABLE_ROW = {
    "component": "wavlm-large-in-tokan",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "id": "SDK-WAVLM-LARGE-IN-TOKAN",
    "mode": "research-control",
    "repository": "audio-sdk",
    "title": "WavLM-Large in TokAN",
}
MUTABLE_BOARD_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "write_scope", "deliverable", "acceptance", "evidence",
)

NEGATIVE_CLAIMS = [
    "No TokAN or WavLM source, checkpoint, weight, config bundle, or runtime is downloaded, vendored, loaded, imported, or executed.",
    "No real audio, accent-conversion output, listening result, device timing, benchmark, or release claim is made.",
    "No provider, adapter, descriptor, registry, default, public API/ABI, CONTRACTS, shared build, or CI change is made.",
    "Source-reported TokAN accent-conversion smoke results are not WavLM-Large encoder isolation evidence and do not qualify this task.",
    "Missing, blocked, invalid, or synthetic controls do not qualify the candidate.",
]

GATES = [
    {"id": "RG-01", "title": "exact_source_and_license_provenance", "status": "blocked", "qualifies": False,
     "statement": "Exact TokAN source revision, license/NOTICE, and redistribution/product-use terms must be pinned and reviewed.",
     "reopen_condition": "Pin immutable TokAN source/license artifacts and obtain reviewed redistribution/product-use clearance."},
    {"id": "RG-02", "title": "exact_wavlm_large_checkpoint_identity", "status": "blocked", "qualifies": False,
     "statement": "Exact WavLM-Large checkpoint/config/preprocessor identity with immutable digests and reviewed terms must be pinned.",
     "reopen_condition": "Stage exact WavLM-Large assets with byte counts, SHA-256, revision, and reviewed license/terms."},
    {"id": "RG-03", "title": "pinned_runtime_and_offline_reproduction", "status": "blocked", "qualifies": False,
     "statement": "A locked offline runtime must reproduce the TokAN/WavLM-Large encoder path deterministically.",
     "reopen_condition": "Provide pinned environment, deterministic load/inference logs, and offline reproduction without network."},
    {"id": "RG-04", "title": "rights_cleared_voice_cohort_and_labels", "status": "blocked", "qualifies": False,
     "statement": "A rights-cleared, task-matched Voice cohort with labels/consent/reference availability must be frozen.",
     "reopen_condition": "Stage reviewed cohort manifest with consent, reference availability, output-use, and task labels."},
    {"id": "RG-05", "title": "isolated_encoder_latency_and_feature_parity", "status": "blocked", "qualifies": False,
     "statement": "WavLM-Large encoder latency and feature parity must be isolated from the full TokAN pipeline.",
     "reopen_condition": "Measure encoder-only latency/memory and parity against the pinned TokAN feature contract on target hardware."},
    {"id": "RG-06", "title": "voice_profile_controls_and_preservation", "status": "blocked", "qualifies": False,
     "statement": "Voice profile must cover identity/similarity, content preservation, naturalness, alignment, and timing controls separately.",
     "reopen_condition": "Run frozen Voice-profile evaluation with controls, stratification, and reviewed human/predictive evidence as allowed."},
    {"id": "RG-07", "title": "target_device_timing_and_availability", "status": "blocked", "qualifies": False,
     "statement": "Target-device pacing, first-output/tail timing, availability, and resource limits must be measured for the exact runtime.",
     "reopen_condition": "Collect paced on-target timing/resources with explicit clock domain and deadline budget."},
    {"id": "RG-08", "title": "opt_in_sdk_intake_and_release", "status": "blocked", "qualifies": False,
     "statement": "Any SDK processor exposure requires separate opt-in intake, independent review, and default-OFF release approval.",
     "reopen_condition": "Pass separate opt-in intake with exact-head independent review; keep adapter/provider OFF by default."},
]

EXACT_BLOCKERS = [
    {"id": "XB-01", "gate": "RG-01", "title": "tokan_source_license_unreviewed",
     "detail": "TokAN source is pinned at cbfc09a but repository declares no LICENSE file and paper metadata is placeholder; redistribution/product-use rights are unreviewed.",
     "reopen": "Obtain reviewed license/NOTICE and redistribution/product-use decision for the exact TokAN revision."},
    {"id": "XB-02", "gate": "RG-02", "title": "wavlm_large_assets_absent",
     "detail": "No WavLM-Large checkpoint/config/preprocessor assets are present; only model id microsoft/wavlm-large and layer 22 are source-reported.",
     "reopen": "Stage exact WavLM-Large assets with immutable digests and reviewed terms."},
    {"id": "XB-03", "gate": "RG-03", "title": "runtime_and_offline_reproduction_absent",
     "detail": "No pinned offline TokAN/WavLM runtime is present in this package; historical run needed Transformers pinning and local compatibility fixes.",
     "reopen": "Provide locked offline runtime and deterministic reproduction logs for the exact encoder path."},
    {"id": "XB-04", "gate": "RG-04", "title": "rights_cleared_voice_cohort_absent",
     "detail": "No rights-cleared task-matched Voice cohort with consent/reference/output-use labels is staged; sample L2-ARCTIC clips are source-reported research context only.",
     "reopen": "Stage reviewed rights-cleared cohort manifest and labels before any quality claim."},
    {"id": "XB-05", "gate": "RG-05", "title": "encoder_isolation_unmeasured",
     "detail": "No encoder-only latency or feature-parity measurement exists; existing TokAN metrics are full-pipeline CPU smoke tests including load/extraction/decoding.",
     "reopen": "Run isolated WavLM-Large encoder latency/parity measurements on pinned hardware/runtime."},
    {"id": "XB-06", "gate": "RG-06", "title": "voice_profile_evidence_absent",
     "detail": "No Voice-profile quality/control evidence exists: no identity/similarity, content, naturalness, alignment, or timing result for an isolated encoder change.",
     "reopen": "Execute Voice profile with frozen controls and separate outcome reporting."},
    {"id": "XB-07", "gate": "RG-07", "title": "target_timing_absent",
     "detail": "No target-device first-output/tail/availability/resource measurement exists; historical RTF was CPU full-pipeline, not encoder isolation.",
     "reopen": "Collect paced target-device timing/resources under explicit deadline budget."},
    {"id": "XB-08", "gate": "RG-08", "title": "sdk_intake_not_started",
     "detail": "No opt-in SDK adapter/provider intake exists; SDK adapter/provider remain OFF/unregistered by task constraints.",
     "reopen": "Open separate opt-in intake only after all evidence gates pass."},
]

BOUNDARY = {
    "benchmark_claim": False,
    "board_or_handoff_changed": False,
    "ci_changed": False,
    "contracts_changed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "listening_claim": False,
    "model_executed": False,
    "network_used": False,
    "processor_exposure": False,
    "provider_registered": False,
    "public_api_abi_changed": False,
    "real_audio_processed": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "timing_claim": False,
    "weights_downloaded": False,
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
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "model_executed": False,
    "checkpoint_loaded": False,
    "network_used": False,
    "provider_registered": False,
}

SOURCE_REPORTED = {
    "qualifies": False,
    "status": "context_only_not_evidence",
    "tokan": {
        "repo": TOKAN_REPO,
        "commit": TOKAN_COMMIT,
        "license_file_present": False,
        "inference_only": True,
        "streaming_implemented": False,
        "wavlm_model": WAVLM_REPO,
        "wavlm_layer": WAVLM_LAYER,
        "sample_rate_hz": 16000,
        "flow_steps_default": 32,
    },
    "historical_cpu_smoke": [
        {"l1_accent": "Arabic", "utterance": "ABA_a0046", "runtime_s_str": "78.89", "rtf_str": "17.38", "speaker_cosine_str": "0.838"},
        {"l1_accent": "Hindi", "utterance": "RRBI_a0391", "runtime_s_str": "63.74", "rtf_str": "18.26", "speaker_cosine_str": "0.798"},
        {"l1_accent": "Korean", "utterance": "HJK_a0103", "runtime_s_str": "62.55", "rtf_str": "20.56", "speaker_cosine_str": "0.874"},
    ],
    "exclusions": [
        "Full-pipeline TokAN CPU smoke is not WavLM-Large encoder isolation.",
        "No accent reduction, identity, naturalness, or product claim is qualified.",
        "No target-device/streaming latency claim is qualified.",
    ],
}

VOICE_PROFILE = {
    "profile": "Voice",
    "satisfied": False,
    "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "required_items": {
        "frozen_input_and_target_references": {"status": "blocked", "evidence": "No rights-cleared frozen input/reference cohort staged."},
        "content_and_semantic_preservation": {"status": "blocked", "evidence": "No content preservation result; source-reported WER proxy is not qualifying."},
        "identity_similarity_and_naturalness": {"status": "blocked", "evidence": "No identity/similarity/naturalness evaluation; no listening/predictive protocol."},
        "alignment_and_timing": {"status": "blocked", "evidence": "No alignment, first-output, or tail timing measurement."},
        "consent_reference_availability_output_use": {"status": "blocked", "evidence": "No consent/reference/output-use review records."},
        "encoder_isolation_for_wavlm_large": {"status": "blocked", "evidence": "No encoder-only latency/feature-parity measurement isolated from TokAN pipeline."},
    },
}

ABSENCE_PROBES: Tuple[Dict[str, str], ...] = (
    {"id": "tokan_weights", "root": "workspace", "path": "research/accent-conversion-20261101/repos/TokAN/checkpoints"},
    {"id": "tokan_local_checkpoints", "root": "workspace", "path": "research/accent-conversion-20261101/repos/TokAN/checkpoints"},
    {"id": "wavlm_large_model_dir", "root": "workspace", "path": "data/models/wavlm-large"},
    {"id": "wavlm_large_cache", "root": "home", "path": ".cache/huggingface/hub/models--microsoft--wavlm-large"},
    {"id": "tokan_adapter", "root": "worktree", "path": "adapters/wavlm_large_in_tokan"},
    {"id": "provider_descriptor", "root": "worktree", "path": "schemas/providers/wavlm_large_in_tokan"},
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


class ReferenceError(ValueError):
    pass


def strict_loads(text: str) -> Any:
    def const(x: str) -> Any:
        raise ReferenceError("nonfinite_or_constant:" + x)

    def obj_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                raise ReferenceError("duplicate_key:" + k)
            out[k] = v
        return out

    obj = json.loads(text, parse_constant=const, object_pairs_hook=obj_hook)

    def walk(x: Any) -> None:
        if isinstance(x, float):
            raise ReferenceError("float_not_allowed")
        if isinstance(x, dict):
            for k, v in x.items():
                if not isinstance(k, str):
                    raise ReferenceError("non_string_key")
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, (str, int, bool)) or x is None:
            return
        else:
            raise ReferenceError("unsupported_type:" + type(x).__name__)

    walk(obj)
    return obj


def load_strict_json(path: Path) -> Any:
    try:
        return strict_loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ReferenceError(f"invalid_json:{path}:{e}") from e


def resolve_source(rel: str) -> Path:
    return WORKSPACE_ROOT / rel


def resolve_worktree(rel: str) -> Path:
    return SDK_ROOT / rel


def resolve_probe(probe: Dict[str, str]) -> Path:
    root = {"workspace": WORKSPACE_ROOT, "worktree": SDK_ROOT, "home": Path.home()}[probe["root"]]
    return root / probe["path"]


def absence_probes() -> List[Dict[str, Any]]:
    rows = []
    for p in ABSENCE_PROBES:
        path = resolve_probe(p)
        rows.append({
            "id": p["id"],
            "root": p["root"],
            "path": p["path"],
            "exists": path.exists(),
            "resolved": str(path),
        })
    return rows


def absence_summary() -> Dict[str, Any]:
    probes = absence_probes()
    present = [p["id"] for p in probes if p["exists"]]
    return {
        "all_absent": len(present) == 0,
        "present_count": len(present),
        "present_ids": present,
        "probe_count": len(probes),
        "probes": probes,
    }


MANIFEST_FIELDS = [
    "schema_id", "adapter", "configuration_id", "tokan_repo", "tokan_revision", "tokan_sha256",
    "wavlm_repo", "wavlm_revision", "wavlm_sha256", "license_id", "runtime_path", "runtime_sha256",
    "runtime_byte_count", "sample_rate_hz", "channels", "frame_samples", "sample_format",
    "cohort_path", "cohort_sha256", "cohort_byte_count", "rights_review_id",
]


def _is_hex64(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _is_pos_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceError("manifest:not_object")
    keys = list(manifest.keys())
    if keys != MANIFEST_FIELDS:
        missing = [k for k in MANIFEST_FIELDS if k not in manifest]
        extra = [k for k in keys if k not in MANIFEST_FIELDS]
        raise ReferenceError(f"manifest:keys:missing={missing},extra={extra}")
    if manifest["schema_id"] != SCHEMA_MANIFEST:
        raise ReferenceError("manifest:schema_id")
    if manifest["adapter"] != COMPONENT:
        raise ReferenceError("manifest:adapter")
    if manifest["configuration_id"] != "wavlm-large-l22-16k-mono-f32-160":
        raise ReferenceError("manifest:configuration_id")
    if manifest["tokan_repo"] != TOKAN_REPO:
        raise ReferenceError("manifest:tokan_repo")
    if manifest["tokan_revision"] != TOKAN_COMMIT:
        raise ReferenceError("manifest:tokan_revision")
    if not _is_hex64(manifest["tokan_sha256"]):
        raise ReferenceError("manifest:tokan_sha256")
    if manifest["wavlm_repo"] != WAVLM_REPO:
        raise ReferenceError("manifest:wavlm_repo")
    if not isinstance(manifest["wavlm_revision"], str) or len(manifest["wavlm_revision"]) < 40:
        raise ReferenceError("manifest:wavlm_revision")
    if not _is_hex64(manifest["wavlm_sha256"]):
        raise ReferenceError("manifest:wavlm_sha256")
    if not isinstance(manifest["license_id"], str) or not manifest["license_id"]:
        raise ReferenceError("manifest:license_id")
    for pkey in ("runtime_path", "cohort_path"):
        v = manifest[pkey]
        if not isinstance(v, str) or not v.startswith("/"):
            raise ReferenceError(f"manifest:{pkey}")
    for hkey in ("runtime_sha256", "cohort_sha256"):
        if not _is_hex64(manifest[hkey]):
            raise ReferenceError(f"manifest:{hkey}")
    for bkey in ("runtime_byte_count", "cohort_byte_count"):
        if not _is_pos_int(manifest[bkey]):
            raise ReferenceError(f"manifest:{bkey}")
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ReferenceError("manifest:sample_rate_hz")
    if manifest["channels"] != CHANNELS:
        raise ReferenceError("manifest:channels")
    if manifest["frame_samples"] != FRAME_SAMPLES:
        raise ReferenceError("manifest:frame_samples")
    if manifest["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceError("manifest:sample_format")
    if not isinstance(manifest["rights_review_id"], str) or not manifest["rights_review_id"]:
        raise ReferenceError("manifest:rights_review_id")
    for p in (manifest["runtime_path"], manifest["cohort_path"]):
        if Path(p).exists():
            raise ReferenceError("manifest:asset_present_requires_external_review")
    raise ReferenceError("manifest:assets_absent_or_unpinned_runtime")


def valid_manifest() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_MANIFEST,
        "adapter": COMPONENT,
        "configuration_id": "wavlm-large-l22-16k-mono-f32-160",
        "tokan_repo": TOKAN_REPO,
        "tokan_revision": TOKAN_COMMIT,
        "tokan_sha256": "0" * 64,
        "wavlm_repo": WAVLM_REPO,
        "wavlm_revision": "0" * 40,
        "wavlm_sha256": "1" * 64,
        "license_id": "Apache-2.0",
        "runtime_path": "/absent/wavlm-large-in-tokan-runtime",
        "runtime_sha256": "2" * 64,
        "runtime_byte_count": 1,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "cohort_path": "/absent/voice-cohort",
        "cohort_sha256": "3" * 64,
        "cohort_byte_count": 1,
        "rights_review_id": "review-absent",
    }


def adverse_cases() -> Dict[str, Any]:
    cases = []
    base = valid_manifest()

    def add(cid: str, desc: str, obj: Any, code: str = None) -> None:
        try:
            validate_caller_manifest(obj)
            cases.append({"id": cid, "description": desc, "status": "accepted", "qualifies": False})
        except Exception as e:
            msg = str(e)
            cases.append({"id": cid, "description": desc, "status": "rejected", "code": code or msg.split(":")[0], "qualifies": False, "detail": msg})

    add("ADV-01", "Reject non-object manifest.", [], "manifest:not_object")
    m = base.copy(); del m["rights_review_id"]; add("ADV-02", "Reject missing field.", m)
    m = base.copy(); m["extra"] = 1; add("ADV-03", "Reject extra field.", m)
    m = base.copy(); m["schema_id"] = "wrong"; add("ADV-04", "Reject wrong schema id.", m, "manifest:schema_id")
    m = base.copy(); m["adapter"] = "other"; add("ADV-05", "Reject wrong adapter.", m, "manifest:adapter")
    m = base.copy(); m["tokan_revision"] = "short"; add("ADV-06", "Reject wrong TokAN revision.", m, "manifest:tokan_revision")
    m = base.copy(); m["wavlm_repo"] = "other/model"; add("ADV-07", "Reject wrong WavLM repo.", m, "manifest:wavlm_repo")
    m = base.copy(); m["wavlm_sha256"] = "abc"; add("ADV-08", "Reject short digest.", m, "manifest:wavlm_sha256")
    m = base.copy(); m["runtime_path"] = "relative/path"; add("ADV-09", "Reject relative runtime path.", m, "manifest:runtime_path")
    m = base.copy(); m["sample_rate_hz"] = 8000; add("ADV-10", "Reject wrong sample rate.", m, "manifest:sample_rate_hz")
    m = base.copy(); m["channels"] = 2; add("ADV-11", "Reject wrong channels.", m, "manifest:channels")
    m = base.copy(); m["frame_samples"] = 320; add("ADV-12", "Reject wrong frame samples.", m, "manifest:frame_samples")
    m = base.copy(); m["sample_format"] = "int16"; add("ADV-13", "Reject wrong sample format.", m, "manifest:sample_format")
    m = base.copy(); m["runtime_byte_count"] = 0; add("ADV-14", "Reject zero byte count.", m, "manifest:runtime_byte_count")
    m = base.copy(); m["runtime_byte_count"] = True; add("ADV-15", "Reject bool byte count.", m, "manifest:runtime_byte_count")
    m = base.copy(); m["rights_review_id"] = ""; add("ADV-16", "Reject empty rights review.", m, "manifest:rights_review_id")
    # valid shape but absent assets -> terminal rejection
    add("ADV-17", "Reject hash-matched/absent assets as unpinned runtime.", base.copy(), "manifest:assets_absent_or_unpinned_runtime")

    json_cases = []
    for jid, text in [("JSON-01", '{"a":1,"a":2}'), ("JSON-02", '{"a":NaN}'), ("JSON-03", '[1.5]'), ("JSON-04", '{"a":1e2}')]:
        try:
            strict_loads(text)
            json_cases.append({"id": jid, "status": "accepted", "qualifies": False})
        except Exception as e:
            json_cases.append({"id": jid, "status": "rejected", "qualifies": False, "detail": str(e)})

    return {
        "manifest_cases": cases,
        "json_cases": json_cases,
        "all_rejected": all(c["status"] == "rejected" for c in cases) and all(c["status"] == "rejected" for c in json_cases),
        "metrics": None,
    }


def board_link() -> Dict[str, Any]:
    payload = json.dumps(BOARD_STABLE_ROW, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "task": TASK_ID,
        "stable_fields": list(BOARD_STABLE_FIELDS),
        "stable_row": BOARD_STABLE_ROW,
        "stable_sha256": sha256_bytes(payload),
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_BOARD_FIELDS_EXCLUDED),
    }


def source_provenance() -> Dict[str, Any]:
    files = []
    for rel in SOURCE_PINS:
        p = resolve_source(rel)
        files.append({
            "path": rel,
            "exists": p.is_file(),
            "sha256": sha256_file(p) if p.is_file() else None,
        })
    return {
        "tokan_repo": TOKAN_REPO,
        "tokan_commit": TOKAN_COMMIT,
        "tokan_license_file_present": False,
        "wavlm_repo": WAVLM_REPO,
        "wavlm_layer": WAVLM_LAYER,
        "source_files": files,
    }


def build_report() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_link": board_link(),
        "source_provenance": source_provenance(),
        "source_reported": SOURCE_REPORTED,
        "absence_summary": absence_summary(),
        "adverse": adverse_cases(),
        "voice_profile": VOICE_PROFILE,
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
            "real_model_output": False,
        },
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-WAVLM-LARGE-IN-TOKAN.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Mutable TASKS.json is never pinned; only stable row identity is gated.",
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


def contract_bytes(report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        artifact_pins[TASK_PREFIX + name] = sha256_bytes(payload)
    contract = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins,
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "board_link": board_link(),
        "source_reported": SOURCE_REPORTED,
        "voice_profile": VOICE_PROFILE,
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "No provider, adapter, descriptor, registry, default, ABI, CONTRACTS, shared build, or CI change is made.",
            "Only this task-local evidence directory is written.",
            "No source, checkpoint, runtime, audio, or generated artifact is downloaded or vendored.",
            "Source-reported full-pipeline results cannot qualify encoder isolation.",
            "Missing, blocked, invalid, or synthetic results never qualify.",
            "Only stable board-row identity enters canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(worktree), *args], capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    r = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    c = r.stdout.strip()
    return c if r.returncode == 0 and c else None


def scope_base(worktree: Path, refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    best = None
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
        raise ReferenceError("git_scope_diff_failed:" + r.stderr.strip())
    return [line for line in r.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [p for p in paths if p and not p.startswith(prefix)]
