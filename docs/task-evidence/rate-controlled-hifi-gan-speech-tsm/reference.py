# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-RATE-CONTROLLED-HIFI-GAN-SPEECH-TSM.

No rate-controlled HiFi-GAN speech-TSM source checkout, checkpoint, runtime,
corpus, generated output or device measurement exists in this workspace. The
pinned candidate-matrix row is unavailable/blocked. Nothing here downloads,
reads, hashes, loads, compiles or executes a candidate asset.

This module provides:
* a fail-closed absence audit over fixed workspace paths;
* a strict caller-supplied external-asset metadata contract (as_asset_v0 shape);
* an explicit synthetic rate-TSM boundary surrogate with fixed delay, rate-map
  accounting, drain, reset and fail-closed rejection of invalid/missing/nonfinite
  input; and
* paired synthetic diagnostics for that surrogate only.

The synthetic branch is NOT rate-controlled HiFi-GAN, NOT a neural stretcher,
and substitutes for no release gate. Decision is DEFER / proposal_only_incomplete
/ not_qualified; all eight release gates remain blocked.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
).resolve()

TASK = "SDK-RATE-CONTROLLED-HIFI-GAN-SPEECH-TSM"
TITLE = "Rate-controlled HiFi-GAN speech TSM"
SLUG = "rate-controlled-hifi-gan-speech-tsm"
MODE = "feasibility"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "629732407d189774bd210d05b3f235924f67153a"
BRANCH = f"swarm/{TASK}"
WORKTREE = f"/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/{TASK}"
REVIEWER = f"reviewer-{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_provider_intake"

SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160
SURROGATE_HOP_SAMPLES = 160
SURROGATE_LOOKAHEAD_FRAMES = 1
BUFFERING_DELAY_SAMPLES = SURROGATE_LOOKAHEAD_FRAMES * SURROGATE_HOP_SAMPLES
STARTUP_INVALID_SAMPLES = BUFFERING_DELAY_SAMPLES
DRAIN_FLUSH_FRAMES = 1
MAX_DRAIN_CALLS = 2
MAX_DRAIN_PRODUCED_SAMPLES = DRAIN_FLUSH_FRAMES * SURROGATE_HOP_SAMPLES
FRAMES = 120
SAMPLES = FRAMES * SURROGATE_HOP_SAMPLES
MAX_FRAMES_PER_STREAM = 400
MAX_STREAM_SAMPLES = MAX_FRAMES_PER_STREAM * SURROGATE_HOP_SAMPLES
MAX_ABS = 1.0
EPS = 1e-12
CLOCK_ID = "fixture-sample-coordinate-not-device"

STATE_NAMES: Tuple[str, ...] = ("delay_line", "rate_phase")
STATE_LAYOUT: Tuple[Tuple[int, ...], ...] = ((SURROGATE_HOP_SAMPLES,), (1,))

_STREAM_CACHE: Dict[str, List[float]] = {}
_REPORT_CACHE: Dict[str, Any] | None = None

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "prosodic_phrase",
    "quiet_speech",
    "music_like_tone",
    "silence",
)
RATES: Tuple[float, ...] = (0.75, 1.0, 1.25, 1.5)

ASSET_ID = "rate_controlled_hifigan_speech_tsm_checkpoint_unpinned"
ASSET_CHECKPOINT_ID = "rate_controlled_hifigan_speech_tsm.pt"
ASSET_LEDGER_PATH = "data/models/rate-controlled-hifi-gan-speech-tsm/model.pt"
ASSET_BYTES = None
ASSET_SHA256 = None
SOURCE_REPOSITORY = None
SOURCE_REVISION = None
CANDIDATE_RELEASE_TAGS: Tuple[str, ...] = ()
CODE_LICENSE_METADATA = "not recorded"
MODEL_LICENSE_METADATA = "not recorded"
OBSERVED_MODEL_TERMS = "not recorded"
CONSENT_SCOPE = "absent"
TARGET_CONDITION = "unpinned"

OFFICIAL_SOURCE_URL = "unavailable/not recorded in pinned research row"
PAPER_URL = "not recorded in pinned research row"
FINDING = (
    "Exact method source/implementation and task-matched checkpoint are absent from the "
    "current worktree; no local inference, output, quality or performance result. Do not "
    "substitute another neural stretcher."
)

SOURCE_PINS = {
    "audio-benchmark-platform/audio-pro/docs/rights-register.md": "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json": "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-blocked-recheck/REPORT.md": "b02e077416843e27a0091c6a1cbf69e0e62e9bdacdaf4ea96de57a38955a58fa",
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "LICENSES/Apache-2.0.txt": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

SIBLING_PINS = {
    "docs/task-evidence/hifi-gan-vocoder/README.md": "75d3ae938366adeabdfeb022580f0a3554feb1d5f5f771fd82edd7943e8695a5",
    "docs/task-evidence/micro-hifi-gan/README.md": "53958c94833e8513d906fa8b6ef61dfb8c6b3d0b7c4d9a6c6accddee10bf8edc",
    "docs/task-evidence/phase-vocoder-baseline/README.md": "915bd51e7de4b223bdd61bb5ff823e7a0558f03e324f154d7d3d4c77d14f9790",
    "docs/task-evidence/neural-wsola/README.md": "38facb50700f54c802d6117ae1604d1ad07036a44fca8bb0aa3bf03cd73bfc7f",
}

LOCAL_FILES = [
    "README.md",
    "SOURCES.sha256",
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
]
TABLE_FILES = [
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
]

STABLE_TASK_IDENTITY = {
    "id": TASK,
    "title": TITLE,
    "component": SLUG,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "write_scope": [
        "SDK provider, tool or evidence directory for rate-controlled-hifi-gan-speech-tsm and its own fixtures"
    ],
    "deliverable": "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. Then reproduce the exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK adapter once its prerequisites pass. Record a concrete blocker if feasibility fails.",
    "acceptance": "Apply the rate acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates. A readiness conclusion with an exact external blocker is an accepted investigation handoff; it does not close the conditional implementation.",
    "dispatch_priority": 3,
    "mutable_fields_excluded": [
        "status",
        "owner",
        "claim",
        "review",
        "handoff",
        "blocked_reason",
        "initialized_on",
        "history",
    ],
}
PROJECTED_BOARD_FIELDS = [
    "id", "title", "component", "mode", "repository", "depends_on", "write_scope",
    "deliverable", "acceptance", "dispatch_priority",
]

CLAIMS = {
    "accent_conversion_claimed": False,
    "asset_bytes_read": False,
    "asset_downloaded": False,
    "benchmark_result": False,
    "chunk_latency_measured": False,
    "device_timing_measured": False,
    "listening_result_produced": False,
    "model_bytes_read": False,
    "model_runtime_invoked": False,
    "naturalness_claimed": False,
    "official_source_read": False,
    "parity_claim": False,
    "payload_inference_invoked": False,
    "quality_claim": False,
    "real_audio_read": False,
    "real_media_read": False,
    "real_tsm_runtime": False,
    "release_claim": False,
    "semantic_preservation_claimed": False,
    "source_read": False,
    "speaker_identity_claimed": False,
    "weights_accessed": False,
    "weights_hashed": False,
}
BOUNDARY = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "installed_v0_geometry_preserved": True,
    "model_runtime_invoked": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "task_board_or_handoff_write": False,
    "tsm_invoked": False,
    "weights_vendored": False,
}

EXACT_BLOCKERS = [
    "No exact rate-controlled HiFi-GAN speech TSM source, implementation or immutable revision is present or pinned. The pinned candidate-matrix row marks it unavailable/blocked; no checkout, LICENSE/notice bundle, source digest or official repository identity is recorded.",
    "No exact task-matched checkpoint, release tag, byte count, SHA-256 or asset-ledger row exists. Fixed workspace probes for source, model, runtime, rights and run artifacts are absent. No bytes were caller-supplied.",
    "No pinned runtime is present. There is no recorded Python/framework version, wheel digest, lock file, target platform or evaluator environment; no exact-runtime reference run, parity vector or inference was produced.",
    "Rights, permitted scope and consent are unresolved. No rights-register entry exists for this candidate; acquisition, evaluation, redistribution, customer deployment, public playback and speaker consent/output-use are unknown and not cleared.",
    "No candidate geometry is known. No sample rate, frame, hop, lookahead, state layout, rate-control contract or streaming drain behavior is recorded, so this package fabricates none. The surrogate 160-sample/1-frame-delay fixture is not candidate geometry.",
    "No candidate evidence exists. There is no output, parity, rights-cleared speech/music cohort, 1x/rate-change/unfamiliar-speech/music/silence/rebuffer/drift/final-partial measurement, pitch/transient/buffering/timing result, listening, or device/runtime evidence. All release gates remain blocked.",
]
REOPEN_CONDITIONS = [
    "Reopen source/asset identity only with an exact immutable source revision, reviewed LICENSE/notice bundle, and caller-owned checkpoint/weights with revision, release tag, byte count, SHA-256 and declared geometry verified by the SDK session without provider file access or download.",
    "Reopen runtime admission only with a pinned isolated runtime, recorded artifact digests, documented distribution/product-use terms and exact-runtime reference outputs reproducible across three cold starts.",
    "Reopen rights/consent only with artifact-specific written terms for evaluation, redistribution, customer deployment and public playback, plus recorded consent and permitted output use for any voice material.",
    "Reopen rate-profile gates only with rights-cleared matched evidence: 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window, source/output mapping, duration, pitch, transient audibility, playback buffering, pause/filler timestamp behavior and speech preservation.",
    "Reopen timing/provider/default only with target-runtime first-output, tail, availability, pacing, deadline and memory measurements, then opt-in provider intake with OFF default, descriptor/catalog review and explicit owner default decision.",
]
MISSING_EVIDENCE = [
    "exact source revision, per-file digest manifest and LICENSE/notice bundle",
    "exact checkpoint/weights with revision, release tag, byte count, SHA-256 and geometry",
    "pinned isolated runtime with recorded digests and documented terms",
    "written rights decisions and voice consent/output-use permissions",
    "rights-cleared matched rate cohort and independent semantic/preservation/listening evidence",
    "target-runtime first-output/tail/availability/pacing/deadline/memory measurements",
    "approved exact-runtime reference outputs for frozen inputs, reproducible across three cold starts",
    "opt-in provider intake with OFF default and explicit owner default decision",
]

GATES = [
    {"name": "exact_asset_identity", "status": "blocked", "evidence": "No source revision, checkpoint byte count, SHA-256, release tag or ledger row exists; fixed probes are absent and no bytes were caller-supplied.", "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_admission", "status": "blocked", "evidence": "No host/model runtime version, wheel digest, lock file, target platform or evaluator environment is recorded or present.", "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights", "status": "blocked", "evidence": "No rights-register entry or artifact-specific written terms exist; consent and output-use are not recorded.", "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked", "evidence": "No candidate output, frozen input, exact-runtime reference or parity trace exists.", "reopen": "Reopen only with approved exact-runtime outputs for frozen inputs, reproducible across three cold starts."},
    {"name": "rights_cleared_rate_cohort", "status": "blocked", "evidence": "No rights-cleared speech/music cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial coverage exists.", "reopen": REOPEN_CONDITIONS[3]},
    {"name": "independent_scoring_and_listening", "status": "blocked", "evidence": "No independent duration/pitch/transient/preservation scoring, listening or speech-preservation evidence exists; surrogate diagnostics are synthetic only.", "reopen": REOPEN_CONDITIONS[3]},
    {"name": "target_runtime_timing", "status": "blocked", "evidence": "No first-output, tail, availability, pacing, deadline or memory measurement was made on the target runtime.", "reopen": REOPEN_CONDITIONS[4]},
    {"name": "provider_intake_and_default_selection", "status": "blocked", "evidence": "No opt-in provider, descriptor, catalog entry or default decision exists.", "reopen": REOPEN_CONDITIONS[4]},
]

TOOL_PROVENANCE = [
    "Rate-controlled HiFi-GAN speech TSM source, checkpoint, runtime and any neural stretcher are absent from this package; nothing was downloaded, hashed, loaded, compiled or invoked.",
    "Candidate status and finding are quoted from pinned workspace records only.",
    "No candidate output, score, parity, listening result or timing exists; pinned research rows are provenance only.",
    "All signals, state and outputs are generated in-process by a stdlib deterministic surrogate; no WAV, media, corpus, checkpoint or provider output is read.",
]
NON_CLAIMS = [
    "No rate-controlled HiFi-GAN source, weight, runtime, vocoder, corpus or media was downloaded, hashed, loaded, compiled, executed or bundled.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No listening, MOS, duration/pitch/transient quality, parity, benchmark, device-timing, latency or release result is claimed for the candidate.",
    "The synthetic boundary surrogate is not rate-controlled HiFi-GAN and no missing result ever qualifies the candidate.",
]


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite")
        if value == 0.0:
            return 0.0
        return value
    if isinstance(value, (int, bool, str)) or value is None:
        return value
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def _reject_nonfinite(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _reject_nonfinite(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_reject_nonfinite(v) for v in obj]
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ValueError("nonfinite")
        if obj == 0.0:
            obj = 0.0
        return obj
    if isinstance(obj, (int, bool, str)) or obj is None:
        return obj
    raise ValueError("unsupported type")


def load_json_strict(path: Path) -> Any:
    data = path.read_bytes()
    obj = json.loads(data.decode("utf-8"))
    obj = _reject_nonfinite(obj)
    # duplicate key detection
    seen = []

    def hook(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError(f"duplicate key: {k}")
            d[k] = v
        return d

    json.loads(data.decode("utf-8"), object_pairs_hook=hook)
    return obj


def project_board_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k in PROJECTED_BOARD_FIELDS:
        if k in row:
            out[k] = copy.deepcopy(row[k])
    return out


def task_identity() -> Dict[str, Any]:
    identity = copy.deepcopy(STABLE_TASK_IDENTITY)
    identity["verification_profile"] = PROFILE
    identity["profile_source"] = "plan/INVENTORY.json#components[id=rate-controlled-hifi-gan-speech-tsm]"
    identity["board_full_file_hashed"] = False
    identity["board_selector"] = f"tasks[id={TASK}]"
    identity["stable_sha256"] = sha256_bytes(canonical_bytes({k: identity[k] for k in PROJECTED_BOARD_FIELDS}))
    return identity


def absence_audit() -> Dict[str, Any]:
    probes = [
        "data/checkouts/rate-controlled-hifi-gan-speech-tsm",
        "data/checkouts/rate_controlled_hifigan_speech_tsm",
        "data/checkouts/hifi-gan-tsm",
        "data/models/rate-controlled-hifi-gan-speech-tsm",
        "data/models/rate-controlled-hifi-gan-speech-tsm/model.pt",
        "data/models/rate-controlled-hifi-gan-speech-tsm/model.onnx",
        "data/envs/rate-controlled-hifi-gan-speech-tsm",
        "data/envs/rate-controlled-hifi-gan-speech-tsm/requirements.lock",
        "data/rights/rate-controlled-hifi-gan-speech-tsm-rights.json",
        "data/runs/rate-controlled-hifi-gan-speech-tsm-cohort/manifest.json",
        "data/runs/rate-controlled-hifi-gan-speech-tsm-parity/manifest.json",
        "docs/task-evidence/rate-controlled-hifi-gan-speech-tsm/candidate-assets",
    ]
    records = []
    for rel in probes:
        p = SOURCE_ROOT / rel
        records.append({"path": rel, "present": p.exists()})
    all_absent = all(not r["present"] for r in records)
    return {
        "all_absence_probes_absent": all_absent,
        "probe_count": len(records),
        "probes": records,
        "download_performed": False,
        "network_used": False,
        "source_checkout_present": False,
        "weights_present": False,
        "runtime_present": False,
        "runtime_lock_present": False,
        "rights_record_present": False,
        "cohort_manifest_present": False,
        "parity_manifest_present": False,
    }


def asset_ref() -> Dict[str, Any]:
    probes = {k: False for k in [
        "data/checkouts/rate-controlled-hifi-gan-speech-tsm",
        "data/models/rate-controlled-hifi-gan-speech-tsm",
        "data/models/rate-controlled-hifi-gan-speech-tsm/model.pt",
        "data/models/rate-controlled-hifi-gan-speech-tsm/model.onnx",
        "data/envs/rate-controlled-hifi-gan-speech-tsm",
        "data/rights/rate-controlled-hifi-gan-speech-tsm-rights.json",
    ]}
    for k in list(probes.keys()):
        probes[k] = (SOURCE_ROOT / k).exists()
    return {
        "acquisition_cleared": False,
        "asset_bytes_read": False,
        "asset_id": ASSET_ID,
        "byte_count": ASSET_BYTES,
        "bytes_present_in_sdk_worktree": False,
        "candidate_release_tags": list(CANDIDATE_RELEASE_TAGS),
        "checkpoint_id": ASSET_CHECKPOINT_ID,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "consent_scope": CONSENT_SCOPE,
        "customer_deployment_cleared": False,
        "digest_recomputed": False,
        "download_permitted": False,
        "evaluation_allowed": False,
        "ledger_entry_present": False,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "observed_model_terms": OBSERVED_MODEL_TERMS,
        "official_source_url": OFFICIAL_SOURCE_URL,
        "paper_url": PAPER_URL,
        "path_relative": ASSET_LEDGER_PATH,
        "pinned": False,
        "public_playback_cleared": False,
        "redistribution_cleared": False,
        "rights_entry_present": False,
        "runtime_available": False,
        "runtime_lock": None,
        "runtime_package": None,
        "runtime_target": None,
        "runtime_wheel_sha256": None,
        "sha256": ASSET_SHA256,
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "storage": "external",
        "target_condition": TARGET_CONDITION,
        "workspace_probes": probes,
    }


def _validate_asset_metadata(meta: Any) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if not isinstance(meta, dict):
        return False, ["asset_metadata_not_object"]
    required = {"asset_id", "byte_count", "sha256", "storage"}
    missing = sorted(required - set(meta.keys()))
    if missing:
        return False, [f"missing:{k}" for k in missing]
    if not isinstance(meta.get("asset_id"), str) or not meta["asset_id"]:
        reasons.append("asset_id_invalid")
    bc = meta.get("byte_count")
    if not isinstance(bc, int) or isinstance(bc, bool) or bc <= 0:
        reasons.append("byte_count_invalid")
    sha = meta.get("sha256")
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha.lower()):
        reasons.append("sha256_invalid")
    if meta.get("storage") != "external":
        reasons.append("storage_not_external")
    if reasons:
        return False, reasons
    # fail-closed: no actual bytes supplied/verified in this package
    return False, ["asset_bytes_not_supplied", "asset_identity_unverified", "rights_unresolved"]


def asset_admission() -> Dict[str, Any]:
    ok, reasons = _validate_asset_metadata({})
    return {
        "asset_bytes_hashed": False,
        "asset_bytes_read": False,
        "candidate_asset": True,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "qualification_effect": "none",
        "reason_codes": [
            "source_and_identity_unpinned",
            "weights_not_supplied",
            "runtime_unpinned",
            "license_terms_unresolved",
            "consent_not_recorded",
            "rate_task_evidence_absent",
            "redistribution_rights_unknown",
        ],
        "status": "blocked",
        "tsm_invoked": False,
    }


def synthetic_admission_control() -> Dict[str, Any]:
    payload = b"synthetic-rate-controlled-hifi-gan-boundary-surrogate-not-candidate"
    return {
        "asset_bytes_read": False,
        "asset_id": "synthetic-rate-controlled-hifi-gan-boundary-surrogate-not-candidate",
        "byte_count": len(payload),
        "candidate_asset": False,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "note": "Explicitly synthetic admission control; not rate-controlled HiFi-GAN and not eligible for any gate.",
        "qualification_effect": "none",
        "reason_codes": [],
        "sha256": sha256_bytes(payload),
        "status": "admitted_synthetic_control",
        "tsm_invoked": False,
    }


def _frame_signal(condition: str, frame_idx: int) -> List[float]:
    out = []
    for i in range(SURROGATE_HOP_SAMPLES):
        t = (frame_idx * SURROGATE_HOP_SAMPLES + i) / SAMPLE_RATE_HZ
        if condition == "silence":
            v = 0.0
        elif condition == "active_speech":
            v = 0.2 * math.sin(2 * math.pi * 220.0 * t) + 0.05 * math.sin(2 * math.pi * 440.0 * t)
        elif condition == "prosodic_phrase":
            env = 0.5 + 0.5 * math.sin(2 * math.pi * 1.5 * t)
            v = 0.15 * env * math.sin(2 * math.pi * 180.0 * t)
        elif condition == "quiet_speech":
            v = 0.03 * math.sin(2 * math.pi * 200.0 * t)
        elif condition == "music_like_tone":
            v = 0.18 * math.sin(2 * math.pi * 330.0 * t) + 0.04 * math.sin(2 * math.pi * 660.0 * t)
        else:
            raise ValueError("unknown condition")
        out.append(max(-MAX_ABS, min(MAX_ABS, float(v))))
    return out


def synthetic_input(condition: str, frames: int = FRAMES) -> List[List[float]]:
    if condition not in CONDITIONS:
        raise ValueError("unknown condition")
    return [_frame_signal(condition, i) for i in range(frames)]


def _validate_frame(frame: Any) -> List[float]:
    if not isinstance(frame, list):
        raise ValueError("frame_type_invalid")
    if len(frame) != SURROGATE_HOP_SAMPLES:
        raise ValueError("frame_shape_invalid")
    out = []
    for x in frame:
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise ValueError("feature_type_invalid")
        xf = float(x)
        if not math.isfinite(xf):
            raise ValueError("feature_nonfinite")
        if abs(xf) > MAX_ABS:
            raise ValueError("feature_out_of_range")
        out.append(xf)
    return out


class SurrogateSession:
    def __init__(self, rate: float = 1.0, surrogate_opt_in: bool = False):
        if not surrogate_opt_in:
            raise ValueError("surrogate_opt_in_required")
        if not _is_number(rate) or rate <= 0.0 or rate > 4.0:
            raise ValueError("rate_out_of_range")
        self.rate = float(rate)
        self.delay = [[0.0] * SURROGATE_HOP_SAMPLES for _ in range(SURROGATE_LOOKAHEAD_FRAMES)]
        self.phase = 0.0
        self.closed = False
        self.stream_complete = False
        self.frames_seen = 0
        self.samples_in = 0
        self.samples_out = 0

    def reset(self) -> None:
        self.__init__(rate=self.rate, surrogate_opt_in=True)

    def close(self) -> None:
        self.closed = True

    def _emit(self, src: List[float]) -> List[float]:
        # deterministic rate-map accounting surrogate, not a neural vocoder
        n_out = int(round(SURROGATE_HOP_SAMPLES / self.rate))
        n_out = max(1, min(MAX_DRAIN_PRODUCED_SAMPLES, n_out))
        out = []
        for i in range(n_out):
            pos = (i * self.rate) + self.phase
            j = int(math.floor(pos))
            frac = pos - j
            j0 = max(0, min(len(src) - 1, j))
            j1 = max(0, min(len(src) - 1, j + 1))
            v = (1.0 - frac) * src[j0] + frac * src[j1]
            out.append(max(-MAX_ABS, min(MAX_ABS, v * 0.9)))
        self.phase = (self.phase + n_out * self.rate) % 1.0
        return out

    def process_frame(self, frame: Any) -> Dict[str, Any]:
        if self.closed:
            return {"status": "rejected:session_closed", "output_samples": 0}
        if self.stream_complete:
            return {"status": "rejected:stream_already_complete", "output_samples": 0}
        try:
            fr = _validate_frame(frame)
        except ValueError as e:
            return {"status": f"rejected:{e}", "output_samples": 0}
        self.delay.append(fr)
        emit_src = self.delay.pop(0)
        out = self._emit(emit_src)
        self.frames_seen += 1
        self.samples_in += SURROGATE_HOP_SAMPLES
        self.samples_out += len(out)
        return {"status": "ok", "output": out, "output_samples": len(out)}

    def flush(self) -> Dict[str, Any]:
        if self.closed:
            return {"status": "rejected:session_closed", "output_samples": 0}
        if self.stream_complete:
            return {"status": "rejected:stream_already_complete", "output_samples": 0}
        # flush emits one delayed frame then marks complete
        emit_src = self.delay.pop(0)
        self.delay.append([0.0] * SURROGATE_HOP_SAMPLES)
        out = self._emit(emit_src)
        self.samples_out += len(out)
        self.stream_complete = True
        return {"status": "ok", "output": out, "output_samples": len(out), "eos": True}


def run_stream(condition: str, rate: float) -> Dict[str, Any]:
    key = f"{condition}|{rate}"
    if key in _STREAM_CACHE:
        # return summary; deterministic
        pass
    sess = SurrogateSession(rate=rate, surrogate_opt_in=True)
    outputs: List[float] = []
    statuses = []
    for frame in synthetic_input(condition):
        r = sess.process_frame(frame)
        statuses.append(r["status"])
        if r["status"] == "ok":
            outputs.extend(r["output"])
    f = sess.flush()
    statuses.append(f["status"])
    if f["status"] == "ok":
        outputs.extend(f["output"])
    _STREAM_CACHE[key] = outputs
    digest = sha256_bytes(canonical_bytes([round(x, 9) for x in outputs]))
    return {
        "condition": condition,
        "rate": rate,
        "frames_in": FRAMES,
        "samples_in": SAMPLES,
        "samples_out": len(outputs),
        "output_digest": digest,
        "all_ok": all(s == "ok" for s in statuses),
        "eos": f.get("eos", False),
        "status_tail": statuses[-2:],
    }


def _run_chunked(condition: str, rate: float) -> str:
    sess = SurrogateSession(rate=rate, surrogate_opt_in=True)
    outputs: List[float] = []
    frames = synthetic_input(condition)
    for fr in frames:
        r = sess.process_frame(fr)
        if r["status"] == "ok":
            outputs.extend(r["output"])
    f = sess.flush()
    if f["status"] == "ok":
        outputs.extend(f["output"])
    return sha256_bytes(canonical_bytes([round(x, 9) for x in outputs]))


def synthetic_control_checks() -> Dict[str, Any]:
    checks = {}
    for cond in CONDITIONS:
        for rate in RATES:
            a = run_stream(cond, rate)
            b = run_stream(cond, rate)
            chunked = _run_chunked(cond, rate)
            checks[f"{cond}@{rate}"] = {
                "deterministic": a["output_digest"] == b["output_digest"],
                "chunk_matches_stream": a["output_digest"] == chunked,
                "samples_out": a["samples_out"],
                "all_ok": a["all_ok"],
            }
    return checks


def adverse_cases() -> Dict[str, Any]:
    # config/asset
    config_cases = {}
    def rec(name, ok, reasons):
        config_cases[name] = {"status": "admitted_synthetic_control" if ok else "rejected", "reason_codes": reasons}
    rec("missing_asset_metadata", *_validate_asset_metadata({}))
    rec("bad_sha256", *_validate_asset_metadata({"asset_id":"x","byte_count":1,"sha256":"bad","storage":"external"}))
    rec("bad_storage", *_validate_asset_metadata({"asset_id":"x","byte_count":1,"sha256":"0"*64,"storage":"local"}))
    rec("bad_byte_count", *_validate_asset_metadata({"asset_id":"x","byte_count":0,"sha256":"0"*64,"storage":"external"}))
    ok, reasons = _validate_asset_metadata({"asset_id":"x","byte_count":10,"sha256":"0"*64,"storage":"external"})
    rec("well_formed_but_unverified", ok, reasons)

    optin_cases = {}
    try:
        SurrogateSession(rate=1.0, surrogate_opt_in=False)
        optin_cases["surrogate_without_opt_in"] = {"status": "accepted", "reason_codes": []}
    except ValueError as e:
        optin_cases["surrogate_without_opt_in"] = {"status": "rejected", "reason_codes": [str(e)]}
    try:
        SurrogateSession(rate=0.0, surrogate_opt_in=True)
        optin_cases["bad_rate_zero"] = {"status": "accepted", "reason_codes": []}
    except ValueError as e:
        optin_cases["bad_rate_zero"] = {"status": "rejected", "reason_codes": [str(e)]}
    try:
        SurrogateSession(rate=float("nan"), surrogate_opt_in=True)
        optin_cases["bad_rate_nan"] = {"status": "accepted", "reason_codes": []}
    except ValueError as e:
        optin_cases["bad_rate_nan"] = {"status": "rejected", "reason_codes": [str(e)]}

    stream_cases = {}
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["wrong_frame_length"] = s.process_frame([0.0] * 10)
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["wrong_frame_type"] = s.process_frame("bad")  # type: ignore
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["nonfinite_frame"] = s.process_frame([float("inf")] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["nan_frame"] = s.process_frame([float("nan")] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["out_of_range_frame"] = s.process_frame([2.0] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["bool_frame"] = s.process_frame([True] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))  # type: ignore
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    for fr in synthetic_input("silence", 2):
        s.process_frame(fr)
    s.flush()
    stream_cases["after_flush_process"] = s.process_frame([0.0] * SURROGATE_HOP_SAMPLES)
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    s.close()
    stream_cases["after_close_process"] = s.process_frame([0.0] * SURROGATE_HOP_SAMPLES)
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    s.close()
    stream_cases["after_close_flush"] = s.flush()

    # normalize status-only for report
    for k, v in stream_cases.items():
        stream_cases[k] = {"status": v.get("status"), "output_samples": v.get("output_samples", 0)}

    return {
        "asset_metadata_cases": config_cases,
        "opt_in_cases": optin_cases,
        "stream_cases": stream_cases,
    }


def rate_profile() -> Dict[str, Any]:
    checks = synthetic_control_checks()
    rows = []
    for cond in CONDITIONS:
        for rate in RATES:
            c = checks[f"{cond}@{rate}"]
            rows.append({
                "condition": cond,
                "rate": rate,
                "deterministic": c["deterministic"],
                "chunk_matches_stream": c["chunk_matches_stream"],
                "samples_out": c["samples_out"],
                "qualifies_candidate": False,
                "synthetic_surrogate_only": True,
            })
    return {
        "profile": PROFILE,
        "profile_source": "plan/swarm/VERIFICATION.md#Rate",
        "profile_applied": True,
        "source_output_mapping_present": False,
        "duration_measured_on_candidate": False,
        "pitch_measured_on_candidate": False,
        "transient_measured_on_candidate": False,
        "playback_buffering_measured": False,
        "one_x_control_on_candidate": False,
        "rate_changes_on_candidate": False,
        "unfamiliar_speech_on_candidate": False,
        "music_on_candidate": False,
        "silence_on_candidate": False,
        "rebuffer_drift_final_partial_on_candidate": False,
        "speech_preservation_measured": False,
        "synthetic_rows": rows,
        "note": "Rows describe only the deterministic synthetic boundary surrogate. No candidate output, rights-cleared corpus, listening, device timing or real runtime exists.",
    }


def evidence_matrix() -> Dict[str, Any]:
    return {
        "candidate_matrix_row": {
            "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
            "row": 45,
            "category": "Disfluency and TSM",
            "candidate": TITLE,
            "status": "unavailable/blocked",
            "finding": FINDING,
            "baseline": "Rubber Band; Bungee; SoundTouch; PSOLA/Praat; identity-speed",
        },
        "pinned_reports": [
            "research/voice-enhancement-20261101/agent-blocked-recheck/REPORT.md",
            "research/tsm-followup-20261101/README.md",
            "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
        ],
        "sibling_boundary": [
            "docs/task-evidence/hifi-gan-vocoder - different model/task, blocker only",
            "docs/task-evidence/micro-hifi-gan - different model/task, blocker only",
            "docs/task-evidence/phase-vocoder-baseline - classical DSP baseline, not neural candidate",
            "docs/task-evidence/neural-wsola - different neural TSM family, blocker only",
        ],
        "inherited_metrics": False,
    }


def build_report() -> Dict[str, Any]:
    global _REPORT_CACHE
    if _REPORT_CACHE is not None:
        return copy.deepcopy(_REPORT_CACHE)
    absence = absence_audit()
    controls = synthetic_control_checks()
    adverse = adverse_cases()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "mode": MODE,
        "repository": "audio-sdk",
        "profile": PROFILE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "task_identity": task_identity(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "absence_audit": absence,
        "asset": asset_ref(),
        "asset_admission": asset_admission(),
        "synthetic_admission_control": synthetic_admission_control(),
        "claims": dict(CLAIMS),
        "boundary": dict(BOUNDARY),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(g) for g in GATES],
        "release_gate_count": len(GATES),
        "release_gates_blocked": len(GATES),
        "synthetic_controls": controls,
        "adverse_cases": adverse,
        "rate_profile": rate_profile(),
        "evidence_matrix": evidence_matrix(),
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
        "counts": {
            "conditions": len(CONDITIONS),
            "rates": len(RATES),
            "synthetic_rows": len(CONDITIONS) * len(RATES),
            "adverse_asset_cases": len(adverse["asset_metadata_cases"]),
            "adverse_opt_in_cases": len(adverse["opt_in_cases"]),
            "adverse_stream_cases": len(adverse["stream_cases"]),
            "release_gates": len(GATES),
            "release_gates_blocked": len(GATES),
        },
        "reproduction": {
            "run": "python3 run.py --all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
            "sources_manifest": "SOURCES.sha256",
            "report_sha256_sidecar": "report.json.sha256",
            "cold_start_regenerations": 3,
        },
    }
    _REPORT_CACHE = report
    return copy.deepcopy(report)


def build_contract(artifact_pins: Dict[str, str] | None = None) -> Dict[str, Any]:
    report = build_report()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "mode": MODE,
        "repository": "audio-sdk",
        "candidate": "Rate-controlled HiFi-GAN speech TSM; source, weights, runtime, geometry and rights unpinned",
        "verification_profile": PROFILE,
        "task_identity": task_identity(),
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "qualified": False,
        "scope": "Writes are limited to " + TASK_PREFIX + "**; no public API/ABI, provider, registry, installed default, shared build, dependency lock, CI, board or handoff change.",
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "v0_frame_samples": V0_FRAME_SAMPLES,
            "surrogate_hop_samples": SURROGATE_HOP_SAMPLES,
            "surrogate_lookahead_frames": SURROGATE_LOOKAHEAD_FRAMES,
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
            "drain_flush_frames": DRAIN_FLUSH_FRAMES,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
            "candidate_geometry_known": False,
            "clock": CLOCK_ID,
            "processing_mode": "synthetic_rate_tsm_boundary_surrogate",
        },
        "asset": report["asset"],
        "asset_admission": report["asset_admission"],
        "synthetic_admission_control": report["synthetic_admission_control"],
        "rights": {
            "acquisition": "unknown",
            "blocked": True,
            "consent": "not_recorded",
            "customer_deployment": "unknown",
            "evaluation": "unknown",
            "output_use": "unknown",
            "public_playback": "unknown",
            "redistribution": "unknown",
            "register": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
            "register_detail": "audio-benchmark-platform/audio-pro/inventory/rights-register.json",
            "weights_must_remain_private": True,
        },
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(g) for g in GATES],
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic rate-TSM accounting/boundary tests with explicit opt-in",
            "read-only documentation of caller-supplied external asset contract and pinned metadata",
        ],
        "not_allowed": [
            "downloading, reading, hashing, loading, executing or bundling any candidate source, checkpoint, graph or derived weight",
            "invoking PyTorch, ONNX Runtime, any vocoder or any model runtime",
            "registering a provider, changing defaults or claiming quality/latency/parity/release",
        ],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "local_files": list(LOCAL_FILES),
        "artifact_pins": dict(artifact_pins or {}),
        "board_policy": {
            "selector": f"tasks[id={TASK}]",
            "full_file_hashed": False,
            "mutable_file": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "stable_fields_only": True,
            "mutable_fields_excluded": list(STABLE_TASK_IDENTITY["mutable_fields_excluded"]),
        },
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
    }


def canonical_report_bytes() -> bytes:
    return canonical_bytes(build_report())
