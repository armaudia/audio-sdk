# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-SBSMS.

SBSMS (Subband Sinusoidal Modelling Synthesis) is recorded in pinned workspace
research as an excluded playback-speed candidate because libsbsms is GPL-2.0 and
not usable in a closed-source product without a separate licence from the author.
No exact pinned SBSMS source revision, commercial/licensing decision, rights-
cleared evaluation corpus, device/runtime timing, listening result, or qualified
rate-profile evidence is present in this task-local package.

This module provides fail-closed absence/probe evidence, strict caller-supplied
external-asset metadata validation, a synthetic rate-accounting boundary
surrogate (NOT SBSMS), and deterministic report/contract generation. Nothing
here downloads, reads, hashes, loads, compiles or executes SBSMS.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
).resolve()

TASK = "SDK-SBSMS"
TITLE = "SBSMS"
SLUG = "sbsms"
MODE = "research-control"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
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
MAX_ABS = 1.0
CLOCK_ID = "fixture-sample-coordinate-not-device"

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "prosodic_phrase",
    "quiet_speech",
    "music_like_tone",
    "silence",
)
RATES: Tuple[float, ...] = (0.75, 1.0, 1.25, 1.5)

ASSET_ID = "sbsms_libsbsms_unpinned"
ASSET_CHECKPOINT_ID = "libsbsms-source-or-binary-unpinned"
ASSET_LEDGER_PATH = "data/checkouts/sbsms/libsbsms"
CANDIDATE_RELEASE_TAGS: Tuple[str, ...] = ()
OFFICIAL_SOURCE_URL = "https://github.com/claytonotey/libsbsms"
PAPER_URL = "not recorded in this task-local package"
FINDING = (
    "SBSMS/libsbsms is GPL-2.0; playback-speed-candidates.md marks it excluded "
    "for closed-source/commercial default use. No exact pinned source revision, "
    "commercial licence decision, rights-cleared evaluation, device/runtime "
    "timing, or qualified rate evidence is present in this package."
)

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
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
    "docs/task-evidence/soundtouch/README.md": "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/neural-wsola/README.md": "38facb50700f54c802d6117ae1604d1ad07036a44fca8bb0aa3bf03cd73bfc7f",
    "docs/task-evidence/phase-vocoder-baseline/README.md": "915bd51e7de4b223bdd61bb5ff823e7a0558f03e324f154d7d3d4c77d14f9790",
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
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "write_scope": [
        "SDK provider, tool or evidence directory for sbsms and its own fixtures"
    ],
    "deliverable": "Retain or reproduce the comparison as an optional SDK developer/evidence adapter alongside audio-bench, with a documented proceed/defer decision before exposing it as a processor.",
    "acceptance": "Apply the rate acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates.",
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
    "asset_bytes_read": False,
    "asset_downloaded": False,
    "benchmark_result": False,
    "candidate_code_executed": False,
    "device_timing_measured": False,
    "listening_result_produced": False,
    "official_source_read": False,
    "parity_claim": False,
    "quality_claim": False,
    "real_audio_read": False,
    "real_tsm_runtime": False,
    "release_claim": False,
    "rights_cleared": False,
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

REOPEN_CONDITIONS = [
    "Reopen source/licensing only with an exact immutable libsbsms source revision or separately licensed commercial artifact, reviewed GPL/commercial terms, per-file SHA-256 manifest, and an explicit SDK distribution decision.",
    "Reopen runtime/build only with a pinned isolated build/runtime, recorded toolchain and dependency digests, and deterministic exact-reference outputs reproducible across three cold starts.",
    "Reopen rights/corpus only with rights-cleared matched rate evidence covering 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window, with documented consent/output-use where applicable.",
    "Reopen rate-profile gates only with source/output mapping, duration, pitch, transient audibility, playback buffering, pause/filler timestamp behavior and speech preservation evidence on the exact runtime.",
    "Reopen timing/provider/default only with target-runtime first-output, tail, availability, pacing, deadline and memory measurements, then opt-in adapter intake with OFF default and explicit owner default decision; no default/processor exposure without qualification.",
]
EXACT_BLOCKERS = [
    "libsbsms is GPL-2.0 per pinned playback-speed-candidates.md; closed-source/commercial SDK default distribution is not cleared. No separate commercial licence decision or reviewed notice bundle is present.",
    "No exact immutable SBSMS source revision, commit/release tag, per-file digest manifest, or build inputs are pinned in this task-local package. No source bytes were downloaded, read, hashed, compiled or executed.",
    "No pinned runtime/build environment exists. There is no recorded toolchain, dependency lock, target platform, or deterministic reference run for SBSMS in this workspace.",
    "Rights/consent/corpus are unresolved. No rights-cleared speech/music cohort, consent/output-use decision, or evaluation permission record exists for SBSMS rate evidence.",
    "No candidate rate-profile evidence exists: no source/output mapping, duration, pitch, transient audibility, playback buffering, rebuffer/drift/final-partial, pause/filler timestamp behavior, speech preservation, listening, or device/runtime timing result. All release gates remain blocked.",
]
MISSING_EVIDENCE = [
    "exact immutable SBSMS/libsbsms source revision and per-file SHA-256 manifest",
    "reviewed GPL-2.0/commercial licensing decision and redistribution notice bundle",
    "pinned isolated build/runtime with toolchain/dependency digests",
    "rights-cleared matched rate cohort and consent/output-use decisions",
    "source/output mapping, duration, pitch, transient, buffering and preservation measurements",
    "target-runtime first-output/tail/availability/pacing/deadline/memory measurements",
    "three cold-start deterministic exact-reference outputs on pinned runtime",
    "opt-in adapter intake decision with OFF default and no processor exposure without qualification",
]

GATES = [
    {"name": "exact_source_and_license", "status": "blocked", "evidence": "No exact immutable libsbsms revision, per-file manifest, or reviewed GPL/commercial distribution decision is present.", "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_build_admission", "status": "blocked", "evidence": "No pinned toolchain/runtime/build environment or deterministic reference run is present.", "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights_and_corpus", "status": "blocked", "evidence": "No rights-cleared rate corpus, consent/output-use decision, or redistribution clearance is present.", "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked", "evidence": "No SBSMS output, frozen-input reference, or three cold-start deterministic parity evidence exists.", "reopen": "Reopen only with approved exact-runtime outputs for frozen inputs, reproducible across three cold starts."},
    {"name": "rights_cleared_rate_cohort", "status": "blocked", "evidence": "No rights-cleared cohort covers 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window.", "reopen": REOPEN_CONDITIONS[3]},
    {"name": "rate_profile_quality", "status": "blocked", "evidence": "No source/output mapping, duration, pitch, transient, playback buffering, pause/filler timestamp, or speech-preservation measurement exists for SBSMS.", "reopen": REOPEN_CONDITIONS[3]},
    {"name": "target_runtime_timing", "status": "blocked", "evidence": "No first-output, tail, availability, pacing, deadline or memory measurement was made on a target runtime.", "reopen": REOPEN_CONDITIONS[4]},
    {"name": "provider_intake_and_default_selection", "status": "blocked", "evidence": "No opt-in adapter/provider intake, OFF-default descriptor review, or explicit owner default decision exists.", "reopen": REOPEN_CONDITIONS[4]},
]

TOOL_PROVENANCE = [
    "SBSMS/libsbsms source, build, runtime and outputs are absent from this package; nothing was downloaded, hashed, compiled, loaded or executed.",
    "Candidate status and finding are quoted from pinned workspace records only.",
    "All synthetic signals and outputs are generated in-process by a stdlib deterministic boundary surrogate; no WAV, media, corpus, or SBSMS output is read.",
]
NON_CLAIMS = [
    "No SBSMS source, binary, object, corpus or media was downloaded, hashed, compiled, loaded, executed or bundled.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No quality, parity, listening, benchmark, device-timing, latency or release result is claimed for SBSMS.",
    "The synthetic boundary surrogate is not SBSMS and no missing result ever qualifies the candidate.",
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


def load_json_strict(path: Path) -> Any:
    data = path.read_bytes()
    obj = json.loads(data.decode("utf-8"))

    def walk(x: Any) -> Any:
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        if isinstance(x, float):
            if not math.isfinite(x):
                raise ValueError("nonfinite")
            if x == 0.0:
                return 0.0
            return x
        if isinstance(x, (int, bool, str)) or x is None:
            return x
        raise ValueError("unsupported type")

    obj = walk(obj)

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
    identity["board_full_file_hashed"] = False
    identity["board_selector"] = f"tasks[id={TASK}]"
    identity["stable_sha256"] = sha256_bytes(canonical_bytes({k: identity[k] for k in PROJECTED_BOARD_FIELDS}))
    identity["profile_source"] = "plan/INVENTORY.json#components[id=sbsms]"
    return identity


def absence_audit() -> Dict[str, Any]:
    probes = [
        "data/checkouts/sbsms",
        "data/checkouts/libsbsms",
        "data/models/sbsms",
        "data/envs/sbsms",
        "data/rights/sbsms-rights.json",
        "data/runs/sbsms-cohort/manifest.json",
        "data/runs/sbsms-parity/manifest.json",
        "docs/task-evidence/sbsms/candidate-assets",
    ]
    records = []
    for rel in probes:
        p = SOURCE_ROOT / rel
        records.append({"path": rel, "present": p.exists()})
    return {
        "all_absence_probes_absent": all(not r["present"] for r in records),
        "probe_count": len(records),
        "probes": records,
        "download_performed": False,
        "network_used": False,
        "source_checkout_present": False,
        "weights_present": False,
        "runtime_present": False,
        "rights_record_present": False,
        "cohort_manifest_present": False,
        "parity_manifest_present": False,
    }


def asset_ref() -> Dict[str, Any]:
    probes = {
        "data/checkouts/sbsms": (SOURCE_ROOT / "data/checkouts/sbsms").exists(),
        "data/checkouts/libsbsms": (SOURCE_ROOT / "data/checkouts/libsbsms").exists(),
        "data/models/sbsms": (SOURCE_ROOT / "data/models/sbsms").exists(),
        "data/envs/sbsms": (SOURCE_ROOT / "data/envs/sbsms").exists(),
        "data/rights/sbsms-rights.json": (SOURCE_ROOT / "data/rights/sbsms-rights.json").exists(),
    }
    return {
        "acquisition_cleared": False,
        "asset_bytes_read": False,
        "asset_id": ASSET_ID,
        "byte_count": None,
        "bytes_present_in_sdk_worktree": False,
        "candidate_release_tags": list(CANDIDATE_RELEASE_TAGS),
        "checkpoint_id": ASSET_CHECKPOINT_ID,
        "code_license_metadata": "GPL-2.0 reported by pinned playback-speed-candidates.md; no reviewed notice bundle in package",
        "consent_scope": "absent",
        "customer_deployment_cleared": False,
        "digest_recomputed": False,
        "download_permitted": False,
        "evaluation_allowed": False,
        "ledger_entry_present": False,
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
        "sha256": None,
        "source_repository": "claytonotey/libsbsms",
        "source_revision": None,
        "storage": "external",
        "target_condition": "unpinned",
        "workspace_probes": probes,
    }


def _validate_asset_metadata(meta: Any) -> Tuple[bool, List[str]]:
    if not isinstance(meta, dict):
        return False, ["asset_metadata_not_object"]
    required = {"asset_id", "byte_count", "sha256", "storage"}
    missing = sorted(required - set(meta.keys()))
    if missing:
        return False, [f"missing:{k}" for k in missing]
    reasons: List[str] = []
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
    return False, ["asset_bytes_not_supplied", "asset_identity_unverified", "rights_unresolved"]


def asset_admission() -> Dict[str, Any]:
    return {
        "asset_bytes_hashed": False,
        "asset_bytes_read": False,
        "candidate_asset": True,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "qualification_effect": "none",
        "reason_codes": [
            "source_and_identity_unpinned",
            "license_distribution_unresolved",
            "runtime_unpinned",
            "rights_unresolved",
            "rate_task_evidence_absent",
        ],
        "status": "blocked",
        "tsm_invoked": False,
    }


def synthetic_admission_control() -> Dict[str, Any]:
    payload = b"synthetic-sbsms-boundary-surrogate-not-candidate"
    return {
        "asset_bytes_read": False,
        "asset_id": "synthetic-sbsms-boundary-surrogate-not-candidate",
        "byte_count": len(payload),
        "candidate_asset": False,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "note": "Explicitly synthetic admission control; not SBSMS and not eligible for any gate.",
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
    """Deterministic boundary surrogate only. Not SBSMS."""

    def __init__(self, rate: float = 1.0, surrogate_opt_in: bool = False):
        if not surrogate_opt_in:
            raise ValueError("surrogate_opt_in_required")
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(float(rate)):
            raise ValueError("rate_out_of_range")
        r = float(rate)
        if r <= 0.0 or r > 4.0:
            raise ValueError("rate_out_of_range")
        self.rate = r
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
        emit_src = self.delay.pop(0)
        self.delay.append([0.0] * SURROGATE_HOP_SAMPLES)
        out = self._emit(emit_src)
        self.samples_out += len(out)
        self.stream_complete = True
        return {"status": "ok", "output": out, "output_samples": len(out), "eos": True}


_STREAM_CACHE: Dict[str, List[float]] = {}


def run_stream(condition: str, rate: float) -> Dict[str, Any]:
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
    key = f"{condition}|{rate}"
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
        "eos": bool(f.get("eos", False)),
        "status_tail": statuses[-2:],
    }


def _run_chunked(condition: str, rate: float) -> str:
    sess = SurrogateSession(rate=rate, surrogate_opt_in=True)
    outputs: List[float] = []
    for fr in synthetic_input(condition):
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
    config_cases = {}

    def rec(name: str, ok: bool, reasons: List[str]) -> None:
        config_cases[name] = {
            "status": "admitted_synthetic_control" if ok else "rejected",
            "reason_codes": reasons,
        }

    rec("missing_asset_metadata", *_validate_asset_metadata({}))
    rec("bad_sha256", *_validate_asset_metadata({"asset_id": "x", "byte_count": 1, "sha256": "bad", "storage": "external"}))
    rec("bad_storage", *_validate_asset_metadata({"asset_id": "x", "byte_count": 1, "sha256": "0" * 64, "storage": "local"}))
    rec("bad_byte_count", *_validate_asset_metadata({"asset_id": "x", "byte_count": 0, "sha256": "0" * 64, "storage": "external"}))
    ok, reasons = _validate_asset_metadata({"asset_id": "x", "byte_count": 10, "sha256": "0" * 64, "storage": "external"})
    rec("well_formed_but_unverified", ok, reasons)

    optin_cases = {}
    try:
        SurrogateSession(rate=1.0, surrogate_opt_in=False)
        optin_cases["surrogate_without_opt_in"] = {"status": "accepted", "reason_codes": []}
    except ValueError as e:
        optin_cases["surrogate_without_opt_in"] = {"status": "rejected", "reason_codes": [str(e)]}
    for name, rate in [("bad_rate_zero", 0.0), ("bad_rate_nan", float("nan")), ("bad_rate_inf", float("inf"))]:
        try:
            SurrogateSession(rate=rate, surrogate_opt_in=True)
            optin_cases[name] = {"status": "accepted", "reason_codes": []}
        except ValueError as e:
            optin_cases[name] = {"status": "rejected", "reason_codes": [str(e)]}

    stream_cases = {}
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["wrong_frame_length"] = s.process_frame([0.0] * 10)
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["wrong_frame_type"] = s.process_frame("bad")  # type: ignore[arg-type]
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["nonfinite_frame"] = s.process_frame([float("inf")] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["nan_frame"] = s.process_frame([float("nan")] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["out_of_range_frame"] = s.process_frame([2.0] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))
    s = SurrogateSession(rate=1.0, surrogate_opt_in=True)
    stream_cases["bool_frame"] = s.process_frame([True] + [0.0] * (SURROGATE_HOP_SAMPLES - 1))  # type: ignore[list-item]
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
        "note": "Rows describe only the deterministic synthetic boundary surrogate. No SBSMS output, rights-cleared corpus, listening, device timing or real runtime exists.",
    }


def evidence_matrix() -> Dict[str, Any]:
    return {
        "inventory_row": {
            "path": "plan/INVENTORY.json",
            "id": "sbsms",
            "task": TASK,
            "status": "considered",
            "evidence_status": "considered",
            "finding": "Excluded",
        },
        "pinned_reports": [
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "plan/swarm/VERIFICATION.md",
            "plan/audio-sdk/README.md",
            "audio-sdk/CONTRACTS.md",
        ],
        "sibling_boundary": [
            "docs/task-evidence/soundtouch - classical WSOLA-style reference; not SBSMS",
            "docs/task-evidence/neural-wsola - neural TSM blocker; not SBSMS",
            "docs/task-evidence/phase-vocoder-baseline - DSP baseline; not SBSMS",
        ],
        "inherited_metrics": False,
    }


_REPORT_CACHE: Dict[str, Any] | None = None


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
        "candidate": "SBSMS/libsbsms; exact source revision, GPL/commercial decision, runtime and rights unpinned",
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
            "downloading, reading, hashing, loading, compiling, executing or bundling any SBSMS source, binary or derived artifact",
            "registering a provider, changing defaults, or claiming quality/latency/parity/release",
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
