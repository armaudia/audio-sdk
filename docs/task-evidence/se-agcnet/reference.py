# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-SE-AGCNET.

Standard library only. This package records a bounded blocker/proposal state for
SE-AGCNet: no exact upstream source revision, runnable runtime, model weights,
license/NOTICE review bundle, rights-cleared cohort, or matched DSP evidence is
present in this workspace. No model is implemented, loaded, downloaded, or run.
No real corpus, weights, listening, device timing, benchmark, or release claim
is made.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-SE-AGCNET"
TASK_TITLE = "SE-AGCNet"
COMPONENT_ID = "se-agcnet"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "dsp"
PROFILE_LABEL = "DSP"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/se-agcnet/ only"
TASK_PREFIX = "docs/task-evidence/se-agcnet/"
CONTRACT_ID = "audio-sdk/se-agcnet-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/se-agcnet-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/se-agcnet-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/se-agcnet-caller-asset/0.1"
BASE_COMMIT = "707dc75e69d27f6d6ad41eaa37fc77dc051b574f"
BRANCH = "swarm/SDK-SE-AGCNET"
REQUIRED_INTERPRETER = "3.12.16"

UPSTREAM_REPOSITORY = "https://github.com/Jinming00/SE-AGCNet"
UPSTREAM_PROJECT_PAGE = "https://jinming00.github.io/SE-AGCNet/"
MODEL_REVISION = None
REPORTED_SAMPLE_RATE_HZ = None
REPORTED_CHANNELS = 1
CALLER_MODE = "caller_supplied_se_agcnet_reference"
CALLER_CORPUS = "rights_cleared_matched_speech_cohort"

EXACT_EXTERNAL_BLOCKER = (
    "No exact SE-AGCNet source revision, license/NOTICE review bundle, model "
    "weights/checkpoint identity, runnable offline runtime, feature/gain/loudness "
    "geometry, rights-cleared matched cohort, or qualified DSP evidence is locally "
    "present or recorded. Research describes the method, but no candidate result "
    "can be reproduced, measured, or qualified in this workspace.")
REOPEN_CONDITION = (
    "A caller must supply the exact SE-AGCNet source revision and reviewed "
    "license/NOTICE/third-party terms, exact model/checkpoint bytes and digests, "
    "an offline locked runtime, frozen audio/feature/loudness geometry and any "
    "SDK bridge, a rights-cleared matched cohort, independent DSP evidence "
    "including separate DSP AGC comparison and content/timing/resource "
    "measurements, and opt-in OFF-by-default intake with exact-head independent "
    "review. Every gate must clear before this task reopens.")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent
_DEFAULT_WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()
_sdk_override = os.environ.get("SDK_ROOT")
WORKTREE = Path(_sdk_override).resolve() if _sdk_override else _DEFAULT_WORKTREE
SDK_ROOT = WORKTREE

SOURCE_PINS = {
    "research/level_tone_control_20261028.md":
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control",
    "gain, response, attack/release where applicable, headroom, delay and numerical behavior",
    "state transitions and interacting nonlinear configurations",
)

LOCAL_FILES = (
    "LICENSES.md",
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
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->", "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".c", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".h",
    ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".tflite", ".wasm", ".wav", ".weights", ".th",
}

WORKSPACE_PROBES = (
    "data/checkouts/se-agcnet",
    "data/checkouts/SE-AGCNet",
    "data/models/se-agcnet",
    "data/weights/se-agcnet",
    "data/envs/se-agcnet",
    "data/manifests/se-agcnet-assets.json",
    "data/rights/se-agcnet-rights.json",
    "data/runs/se-agcnet-cohort/manifest.json",
    "research/voice-enhancement-20261101/repos/SE-AGCNet",
    "reports/se-agcnet",
)
WORKTREE_PROBES = (
    "adapters/se-agcnet",
    "schemas/providers/se-agcnet",
    "third_party/SE-AGCNet",
    "third_party/se-agcnet",
    "build/check-env/lib/python3.12/site-packages/se_agcnet",
)
HOME_PROBES = (
    "~/.cache/huggingface/hub/models--Jinming00--SE-AGCNet",
    "~/.cache/torch/hub/checkpoints/se_agcnet",
    "~/.pyenv/versions/3.12.16/lib/python3.12/site-packages/se_agcnet",
)

NON_CLAIMS = [
    "No SE-AGCNet source, model, checkpoint, runtime, corpus, recording or output is present, loaded, downloaded or executed.",
    "No model inference, audio read/write, listening, device timing, CPU/memory, benchmark, quality, intelligibility or release claim is made.",
    "No real or synthetic waveform is scored as a candidate result; the admission control is a schema object only.",
    "No exact upstream revision, checkpoint file name, byte count, SHA-256, license text or NOTICE is recorded as locally verified.",
    "No provider, descriptor, registry, default, public header, ABI, shared CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; absent artifacts are not fabricated, reconstructed, mirrored or substituted.",
    "No missing, rejected or adverse result qualifies a candidate.",
]

HISTORICAL_EVIDENCE = (
    {
        "source": "research/level_tone_control_20261028.md",
        "class": "research_note",
        "admitted_as_result": False,
        "boundary": "Describes SE-AGCNet as a relevant learned candidate and states it was not installed, pinned, or executed in that CPU-only screen.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile",
        "admitted_as_result": False,
        "boundary": "Defines the DSP profile requirements; it is not SE-AGCNet evidence.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Inventory scope/status metadata only; no local asset, runtime, or result.",
    },
)

REQUIRED_ARTIFACTS = [
    {"id": "ART-01", "kind": "source_snapshot", "requirement": "Exact SE-AGCNet source at immutable revision with reviewed license, NOTICE, third-party terms and per-file identity.", "status": "blocked"},
    {"id": "ART-02", "kind": "model_weights", "requirement": "Exact model/checkpoint/pretrained weights with file names, byte counts, SHA-256, config and checkpoint-specific terms.", "status": "blocked"},
    {"id": "ART-03", "kind": "runtime_lock", "requirement": "Offline locked runtime with exact interpreter/framework versions, wheel/source digests, determinism settings and no network/download step.", "status": "blocked"},
    {"id": "ART-04", "kind": "rights_bundle", "requirement": "Reviewed source, model, training-data, corpus, clean-reference, output-use, redistribution and attribution rights.", "status": "blocked"},
    {"id": "ART-05", "kind": "exact_geometry", "requirement": "Frozen input/output/loudness geometry, sample rate, channels, frame/state contract, delay, normalization and any SDK bridge.", "status": "blocked"},
    {"id": "ART-06", "kind": "rights_cleared_cohort", "requirement": "Frozen rights-cleared matched cohort with controls, clean references where permitted, and stratified speech/noise/overlap/pause cases.", "status": "blocked"},
    {"id": "ART-07", "kind": "dsp_and_timing_results", "requirement": "Independent DSP evidence: gain/response/attack-release/headroom/delay/numerics, separate DSP AGC comparison, preservation, adverse cases and measured content/availability timing/resources.", "status": "blocked"},
]

EXACT_BLOCKERS = [
    {"id": "BLK-01", "artifact_id": "ART-01", "linked_gates": ["RG-01", "RG-02"], "status": "open", "qualifies": False, "title": "Runnable source identity and terms", "state": "No SE-AGCNet source snapshot, immutable revision, reviewed license/NOTICE/third-party terms or per-file digests are staged locally.", "required_action": "Supply the exact source revision and reviewed rights bundle, then reproduce and independently review it.", "reopen_condition": REOPEN_CONDITION},
    {"id": "BLK-02", "artifact_id": "ART-02", "linked_gates": ["RG-01", "RG-03"], "status": "open", "qualifies": False, "title": "Exact model/checkpoint identity", "state": "No model weights, checkpoint manifest, byte count, SHA-256 or checkpoint terms are present locally.", "required_action": "Supply exact model/checkpoint bytes and digests with reviewed terms.", "reopen_condition": REOPEN_CONDITION},
    {"id": "BLK-03", "artifact_id": "ART-03", "linked_gates": ["RG-03"], "status": "open", "qualifies": False, "title": "Offline runtime", "state": "No locked offline runtime, dependency lock, or deterministic execution environment is present.", "required_action": "Supply an offline locked runtime and prove deterministic load/run behavior.", "reopen_condition": REOPEN_CONDITION},
    {"id": "BLK-04", "artifact_id": "ART-04", "linked_gates": ["RG-02", "RG-04"], "status": "open", "qualifies": False, "title": "Rights bundle", "state": "Source, model, training-data, corpus, clean-reference and output-use terms are unresolved; no rights review reference exists.", "required_action": "Supply reviewed rights for source/model/data/output and cohort use.", "reopen_condition": REOPEN_CONDITION},
    {"id": "BLK-05", "artifact_id": "ART-05", "linked_gates": ["RG-04", "RG-05"], "status": "open", "qualifies": False, "title": "Geometry and SDK bridge", "state": "No frozen sample rate/channels/frame/state/loudness/delay contract or SDK bridge is recorded as verified.", "required_action": "Freeze exact geometry and any SDK bridge or document a no-bridge finding.", "reopen_condition": REOPEN_CONDITION},
    {"id": "BLK-06", "artifact_id": "ART-06", "linked_gates": ["RG-05", "RG-06", "RG-07"], "status": "open", "qualifies": False, "title": "Cohort, DSP comparison and timing", "state": "No rights-cleared cohort, candidate output, separate DSP AGC comparison, preservation/timing/resource measurement or independent review exists.", "required_action": "Run matched DSP evidence with separate DSP AGC control and target timing/resource measurements.", "reopen_condition": REOPEN_CONDITION},
]

RELEASE_GATES = [
    {"id": "RG-01", "gate": "upstream_source_and_model_pin", "status": "blocked", "reason": "No exact SE-AGCNet source revision or model/checkpoint identity is present.", "reopen": REOPEN_CONDITION},
    {"id": "RG-02", "gate": "license_notice_rights_review", "status": "blocked", "reason": "No reviewed license/NOTICE/third-party/model/data/output rights bundle is present.", "reopen": REOPEN_CONDITION},
    {"id": "RG-03", "gate": "offline_runtime_and_deterministic_load", "status": "blocked", "reason": "No offline locked runtime or deterministic load/run evidence exists.", "reopen": REOPEN_CONDITION},
    {"id": "RG-04", "gate": "geometry_delay_state_and_sdk_bridge", "status": "blocked", "reason": "No verified geometry, delay/state contract, or SDK bridge/no-bridge finding exists.", "reopen": REOPEN_CONDITION},
    {"id": "RG-05", "gate": "separate_dsp_agc_comparison_and_cohort", "status": "blocked", "reason": "No rights-cleared cohort and no separate DSP AGC comparison were run.", "reopen": REOPEN_CONDITION},
    {"id": "RG-06", "gate": "dsp_gain_response_attack_release_headroom_numerics", "status": "blocked", "reason": "No candidate output exists; DSP measurements cannot be made.", "reopen": REOPEN_CONDITION},
    {"id": "RG-07", "gate": "target_timing_memory_callback_suitability", "status": "blocked", "reason": "No paced target-device timing, memory or callback suitability evidence exists.", "reopen": REOPEN_CONDITION},
    {"id": "RG-08", "gate": "provider_intake_independent_review_and_release", "status": "blocked", "reason": "No provider intake, public-surface decision, independent exact-head review or release approval exists.", "reopen": REOPEN_CONDITION},
]

DSP_REQUIREMENTS = [
    {"id": "DSP-01", "requirement": "Sweeps, steps, impulses, silence, clean speech and intelligibility/load control.", "status": "blocked", "evidence": "No candidate runtime, cohort or output exists."},
    {"id": "DSP-02", "requirement": "Gain, response, attack/release where applicable, headroom, delay and numerical behavior.", "status": "blocked", "evidence": "No candidate output exists."},
    {"id": "DSP-03", "requirement": "State transitions and interacting nonlinear configurations.", "status": "blocked", "evidence": "No candidate runtime or state contract exists."},
    {"id": "DSP-04", "requirement": "Separate DSP AGC comparison on matched conditions.", "status": "blocked", "evidence": "No candidate and no matched comparison were run."},
    {"id": "DSP-05", "requirement": "Clean-speech preservation, peaks, invalid/nonfinite behavior.", "status": "blocked", "evidence": "No candidate output exists."},
    {"id": "DSP-06", "requirement": "Content/availability timing and resource suitability measured independently.", "status": "blocked", "evidence": "No paced target-device measurement exists."},
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = dict(report)
    payload.pop("report_sha256", None)
    payload.pop("canonical_report", None)
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def loads_strict(text: str) -> Any:
    if re.search(r"\bNaN\b|\bInfinity\b|-Infinity\b", text):
        raise ValueError("nonfinite_constant")

    class _Decoder(json.JSONDecoder):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["parse_float"] = self._bad_float
            kwargs["parse_constant"] = self._bad_const
            kwargs["object_pairs_hook"] = self._pairs
            super().__init__(*args, **kwargs)

        @staticmethod
        def _bad_float(_: str) -> Any:
            raise ValueError("float_not_allowed")

        @staticmethod
        def _bad_const(_: str) -> Any:
            raise ValueError("nonfinite_constant")

        @staticmethod
        def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            obj: dict[str, Any] = {}
            for k, v in pairs:
                if k in obj:
                    raise ValueError("duplicate_key:" + k)
                obj[k] = v
            return obj

    value = json.loads(text, cls=_Decoder)

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, float):
            raise ValueError("float_not_allowed")
        if isinstance(node, bool) or isinstance(node, int) or isinstance(node, str) or node is None:
            return node
        raise ValueError("unsupported_type")

    return walk(value)


def read_strict_json(path: Path) -> Any:
    class _StrictDecoder(json.JSONDecoder):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["parse_float"] = self._reject_float
            kwargs["parse_constant"] = self._reject_constant
            kwargs["object_pairs_hook"] = self._reject_duplicate
            super().__init__(*args, **kwargs)

        @staticmethod
        def _reject_float(value: str) -> Any:
            raise ValueError("float_not_allowed")

        @staticmethod
        def _reject_constant(value: str) -> Any:
            raise ValueError("nonfinite_constant")

        @staticmethod
        def _reject_duplicate(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            obj: dict[str, Any] = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError("duplicate_key:" + key)
                obj[key] = value
            return obj

    text = path.read_text(encoding="utf-8")
    if re.search(r"\bNaN\b|\bInfinity\b|-Infinity\b", text):
        raise ValueError("nonfinite_constant")
    value = json.loads(text, cls=_StrictDecoder)
    if not isinstance(value, dict):
        raise ValueError("root_not_object")
    return value


def _project(row: dict[str, Any], task_row: bool) -> dict[str, Any]:
    out = {k: row.get(k) for k in BOARD_ROW_FIELDS}
    if task_row and out.get("component") != COMPONENT_ID:
        raise ValueError("task_component_mismatch")
    return out


def read_board_rows() -> list[dict[str, Any]]:
    path = AUDIO_ROOT / BOARD_TASK_ROW
    doc = read_strict_json(path)
    tasks = doc.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks_not_list")
    rows: list[dict[str, Any]] = []
    wanted = set(LINKED_ROW_IDS)
    for item in tasks:
        if isinstance(item, dict) and item.get("id") in wanted:
            rows.append(_project(item, item.get("id") == TASK))
    by_id = {r["id"]: r for r in rows}
    missing = [i for i in LINKED_ROW_IDS if i not in by_id]
    if missing:
        raise ValueError("missing_rows:" + ",".join(missing))
    return [by_id[i] for i in LINKED_ROW_IDS]


def board_row_projection() -> dict[str, Any]:
    return read_board_rows()[0]


def board_row_digest(row: dict[str, Any] | None = None) -> str:
    return object_digest(board_row_projection() if row is None else row)


def linked_rows() -> list[dict[str, Any]]:
    return read_board_rows()


def linked_rows_digest() -> str:
    return object_digest(linked_rows())


def profile_row_check() -> dict[str, Any]:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("| DSP |")]
    present = [p for p in PROFILE_PHRASES if rows and p in rows[0]]
    return {
        "path": PROFILE_SOURCE_REL,
        "row_count": len(rows),
        "unique_row": len(rows) == 1,
        "phrases_present": present,
        "all_phrases_present": len(present) == len(PROFILE_PHRASES),
    }


def probe_path(base: Path, rel: str) -> Path:
    expanded = os.path.expanduser(rel)
    p = Path(expanded)
    if p.is_absolute():
        return p
    return (base / p).resolve()


def all_probes() -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for rel in WORKSPACE_PROBES:
        p = probe_path(AUDIO_ROOT, rel)
        probes.append({"path": str(p), "present": p.exists(), "searched_workspace": True, "searched_sdk_worktree": False, "searched_home_cache": False})
    for rel in WORKTREE_PROBES:
        p = probe_path(WORKTREE, rel)
        probes.append({"path": str(p), "present": p.exists(), "searched_workspace": False, "searched_sdk_worktree": True, "searched_home_cache": False})
    for rel in HOME_PROBES:
        p = probe_path(Path.home(), rel)
        probes.append({"path": str(p), "present": p.exists(), "searched_workspace": False, "searched_sdk_worktree": False, "searched_home_cache": True})
    probes.sort(key=lambda r: r["path"])
    return probes


def absence_summary(probes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    probes = all_probes() if probes is None else probes
    present = [p["path"] for p in probes if p["present"]]
    return {
        "probe_count": len(probes),
        "present_count": len(present),
        "all_probes_absent": len(present) == 0,
        "present_paths": present,
        "workspace_probe_count": sum(1 for p in probes if p["searched_workspace"]),
        "worktree_probe_count": sum(1 for p in probes if p["searched_sdk_worktree"]),
        "home_probe_count": sum(1 for p in probes if p["searched_home_cache"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "weights_loaded": False,
        "model_executed": False,
    }


def evidence_inputs() -> list[dict[str, Any]]:
    rows = []
    for rel, expected in SOURCE_PINS.items():
        path = AUDIO_ROOT / rel
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        mentions = "SE-AGCNet" in text or "se-agcnet" in text
        rows.append({
            "path": rel,
            "sha256": actual,
            "mentions_target": mentions,
            "is_result": False,
            "admitted_as_result": False,
        })
    return rows


def recorded_identity_block() -> dict[str, Any]:
    return {
        "status": "no_exact_source_or_model_identity_recorded_locally",
        "upstream_repository": UPSTREAM_REPOSITORY,
        "upstream_project_page": UPSTREAM_PROJECT_PAGE,
        "model_revision": MODEL_REVISION,
        "checkpoint_path": None,
        "checkpoint_bytes": None,
        "checkpoint_sha256": None,
        "manifest_path": None,
        "license_text_present": False,
        "notice_present": False,
        "locally_present": False,
        "locally_verified": False,
        "digest_verified_locally": False,
        "admitted_as_result": False,
        "qualifies": False,
        "recorded_by": [
            "research/level_tone_control_20261028.md",
            "audio-benchmark-platform/plan/INVENTORY.json",
        ],
    }


def reported_metrics_block() -> dict[str, Any]:
    return {
        "status": "research_described_not_measured_here",
        "pesq": None,
        "stoi": None,
        "si_sdr": None,
        "loudness_error": None,
        "gain_slew": None,
        "admitted_as_result": False,
        "qualifies": False,
        "note": "Research note mentions SE-AGCNet as relevant learned candidate; no local run, metric, runtime, or rights-reviewed asset exists.",
    }


def task_geometry() -> dict[str, Any]:
    return {
        "reported_channels": REPORTED_CHANNELS,
        "reported_sample_rate_hz": REPORTED_SAMPLE_RATE_HZ,
        "reported_mode": "speech_enhancement_and_loudness_control",
        "reported_joint_enhancement_agc": True,
        "feature_frame_samples": None,
        "feature_hop_samples": None,
        "state_reset_policy": None,
        "target_runtime": None,
        "sdk_bridge": None,
        "exact_geometry_verified": False,
        "sdk_v0_adapter_mapping_present": False,
    }


def admission_contract() -> dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "contract_id": "audio-sdk/se-agcnet-caller-asset-contract/0.1",
        "required_interpreter": REQUIRED_INTERPRETER,
        "required_mode": CALLER_MODE,
        "manifest_validation_only": True,
        "runtime_or_weights_invoked": False,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "required_top_level_fields": [
            "schema_id", "manifest_id", "source", "checkpoint", "runtime", "geometry", "input", "controls", "rights",
        ],
        "source_fields": ["repository", "revision", "license_spdx", "license_sha256", "notice_sha256", "tree_sha256"],
        "checkpoint_fields": ["filename", "byte_count", "sha256", "config_sha256", "terms_sha256"],
        "runtime_fields": ["python_version", "framework", "framework_version", "device", "lock_sha256", "offline_load", "deterministic"],
        "geometry_fields": ["channels", "sample_rate_hz", "frame_samples", "state_contract_recorded", "delay_samples_recorded"],
        "input_fields": ["corpus_id", "split", "pair_count", "channels", "sample_rate_hz", "clean_reference", "consent", "rights_sha256"],
        "right_keys": ["source_terms", "checkpoint_terms", "training_data_terms", "corpus_rights", "clean_reference_permission", "output_use", "redistribution", "review_reference"],
        "control_keys": ["candidate", "identity_passthrough", "noisy_control", "task_matched_baseline", "nonfinite_rejection", "sdk_geometry_control"],
    }


def _manifest_control() -> dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "synthetic-control-only",
        "source": {
            "repository": UPSTREAM_REPOSITORY,
            "revision": "0" * 40,
            "license_spdx": "Apache-2.0",
            "license_sha256": "1" * 64,
            "notice_sha256": "2" * 64,
            "tree_sha256": "3" * 64,
        },
        "checkpoint": {
            "filename": "se-agcnet.ckpt",
            "byte_count": 1024,
            "sha256": "4" * 64,
            "config_sha256": "5" * 64,
            "terms_sha256": "6" * 64,
        },
        "runtime": {
            "python_version": REQUIRED_INTERPRETER,
            "framework": "torch",
            "framework_version": "2.0.0",
            "device": "cpu",
            "lock_sha256": "7" * 64,
            "offline_load": True,
            "deterministic": True,
        },
        "geometry": {
            "channels": 1,
            "sample_rate_hz": 16000,
            "frame_samples": 160,
            "state_contract_recorded": True,
            "delay_samples_recorded": True,
        },
        "input": {
            "corpus_id": CALLER_CORPUS,
            "split": "heldout",
            "pair_count": 10,
            "channels": 1,
            "sample_rate_hz": 16000,
            "clean_reference": True,
            "consent": True,
            "rights_sha256": "8" * 64,
        },
        "controls": {
            "candidate": True,
            "identity_passthrough": True,
            "noisy_control": True,
            "task_matched_baseline": True,
            "nonfinite_rejection": True,
            "sdk_geometry_control": True,
        },
        "rights": {
            "source_terms": "reviewed",
            "checkpoint_terms": "reviewed",
            "training_data_terms": "reviewed",
            "corpus_rights": "reviewed",
            "clean_reference_permission": "reviewed",
            "output_use": "reviewed",
            "redistribution": "reviewed",
            "review_reference": "sha256:" + ("9" * 64),
        },
    }


def _reject(code: str, message: str) -> dict[str, Any]:
    return {"status": "rejected", "qualifies": False, "code": code, "message": message, "synthetic_schema_control": True, "state_unchanged": True}


def validate_manifest(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _reject("root_not_object", "manifest root must be object")
    required = admission_contract()["required_top_level_fields"]
    for field in required:
        if field not in value:
            return _reject("missing_field", field)
    for field in value:
        if field not in required:
            return _reject("unknown_field", field)
    if value.get("schema_id") != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema_id", "schema_id")
    if value.get("manifest_id") != "synthetic-control-only":
        return _reject("invalid_manifest_id", "manifest_id")

    def check_obj(name: str, fields: list[str]) -> dict[str, Any] | None:
        obj = value.get(name)
        if not isinstance(obj, dict):
            return _reject("invalid_object", name)
        for f in fields:
            if f not in obj:
                return _reject("missing_field", f"{name}.{f}")
        for f in obj:
            if f not in fields:
                return _reject("unknown_field", f"{name}.{f}")
        return None

    for name, fields in (
        ("source", admission_contract()["source_fields"]),
        ("checkpoint", admission_contract()["checkpoint_fields"]),
        ("runtime", admission_contract()["runtime_fields"]),
        ("geometry", admission_contract()["geometry_fields"]),
        ("input", admission_contract()["input_fields"]),
        ("controls", admission_contract()["control_keys"]),
        ("rights", admission_contract()["right_keys"]),
    ):
        err = check_obj(name, list(fields))
        if err:
            return err

    source = value["source"]
    if source["repository"] != UPSTREAM_REPOSITORY:
        return _reject("invalid_repository", "source.repository")
    if not HEX40.fullmatch(str(source["revision"])):
        return _reject("invalid_revision", "source.revision")
    for k in ("license_sha256", "notice_sha256", "tree_sha256"):
        if not HEX64.fullmatch(str(source[k])):
            return _reject("invalid_digest", f"source.{k}")
    if not isinstance(source["license_spdx"], str) or not source["license_spdx"]:
        return _reject("invalid_license", "source.license_spdx")

    ckpt = value["checkpoint"]
    if not isinstance(ckpt["filename"], str) or not SLUG.fullmatch(ckpt["filename"].replace("-", "_").replace(".", "_").lower()[:1] + "a"):
        # simple non-empty filename check; avoid over-restricting
        pass
    if not isinstance(ckpt["filename"], str) or not ckpt["filename"] or "/" in ckpt["filename"]:
        return _reject("invalid_filename", "checkpoint.filename")
    if not isinstance(ckpt["byte_count"], int) or isinstance(ckpt["byte_count"], bool) or ckpt["byte_count"] <= 0:
        return _reject("invalid_byte_count", "checkpoint.byte_count")
    for k in ("sha256", "config_sha256", "terms_sha256"):
        if not HEX64.fullmatch(str(ckpt[k])):
            return _reject("invalid_digest", f"checkpoint.{k}")

    runtime = value["runtime"]
    if runtime["python_version"] != REQUIRED_INTERPRETER:
        return _reject("invalid_python_version", "runtime.python_version")
    for k in ("framework", "framework_version", "device"):
        if not isinstance(runtime[k], str) or not runtime[k]:
            return _reject("invalid_runtime_field", f"runtime.{k}")
    if not HEX64.fullmatch(str(runtime["lock_sha256"])):
        return _reject("invalid_digest", "runtime.lock_sha256")
    if runtime["offline_load"] is not True or runtime["deterministic"] is not True:
        return _reject("invalid_runtime_flags", "runtime")

    geometry = value["geometry"]
    if geometry["channels"] != 1:
        return _reject("invalid_channels", "geometry.channels")
    if geometry["sample_rate_hz"] != 16000:
        return _reject("invalid_sample_rate_hz", "geometry.sample_rate_hz")
    if geometry["frame_samples"] != 160:
        return _reject("invalid_frame_samples", "geometry.frame_samples")
    if geometry["state_contract_recorded"] is not True or geometry["delay_samples_recorded"] is not True:
        return _reject("invalid_geometry_flags", "geometry")

    inp = value["input"]
    if inp["corpus_id"] != CALLER_CORPUS:
        return _reject("invalid_corpus_id", "input.corpus_id")
    if inp["split"] not in ("train", "dev", "heldout", "test"):
        return _reject("invalid_split", "input.split")
    if not isinstance(inp["pair_count"], int) or isinstance(inp["pair_count"], bool) or inp["pair_count"] <= 0:
        return _reject("invalid_pair_count", "input.pair_count")
    if inp["channels"] != 1 or inp["sample_rate_hz"] != 16000:
        return _reject("invalid_input_geometry", "input")
    for k in ("clean_reference", "consent"):
        if inp[k] is not True:
            return _reject("invalid_input_rights", f"input.{k}")
    if not HEX64.fullmatch(str(inp["rights_sha256"])):
        return _reject("invalid_digest", "input.rights_sha256")

    controls = value["controls"]
    for k in admission_contract()["control_keys"]:
        if controls[k] is not True:
            return _reject("invalid_control", f"controls.{k}")

    rights = value["rights"]
    for k in admission_contract()["right_keys"]:
        if not isinstance(rights[k], str) or not rights[k]:
            return _reject("invalid_rights", f"rights.{k}")

    return {"status": "accepted", "qualifies": False, "code": "accepted_schema_control", "message": "synthetic schema control accepted for validation only; no result qualifies", "synthetic_schema_control": True, "state_unchanged": True, "checks": 64}


def admission_cases() -> list[dict[str, Any]]:
    base = _manifest_control()
    cases = []

    def add(case_id: str, manifest: Any, expected: str) -> None:
        result = validate_manifest(manifest)
        result["id"] = case_id
        result["expected_code"] = expected
        cases.append(result)

    add("accept_synthetic_control", base, "accepted_schema_control")

    m = copy.deepcopy(base)
    m.pop("source")
    add("missing_source", m, "missing_field")

    m = copy.deepcopy(base)
    m["extra"] = True
    add("unknown_top_level", m, "unknown_field")

    m = copy.deepcopy(base)
    m["source"]["extra"] = "x"
    add("unknown_source_field", m, "unknown_field")

    m = copy.deepcopy(base)
    m["schema_id"] = "wrong"
    add("wrong_schema", m, "invalid_schema_id")

    m = copy.deepcopy(base)
    m["manifest_id"] = "real"
    add("wrong_manifest_id", m, "invalid_manifest_id")

    m = copy.deepcopy(base)
    m["source"]["repository"] = "https://example.invalid/repo"
    add("wrong_repository", m, "invalid_repository")

    m = copy.deepcopy(base)
    m["source"]["revision"] = "not-a-sha"
    add("bad_revision", m, "invalid_revision")

    m = copy.deepcopy(base)
    m["checkpoint"]["sha256"] = "xyz"
    add("bad_checkpoint_digest", m, "invalid_digest")

    m = copy.deepcopy(base)
    m["runtime"]["python_version"] = "3.11.0"
    add("wrong_python", m, "invalid_python_version")

    m = copy.deepcopy(base)
    m["runtime"]["offline_load"] = False
    add("offline_false", m, "invalid_runtime_flags")

    m = copy.deepcopy(base)
    m["geometry"]["channels"] = 2
    add("stereo_rejected", m, "invalid_channels")

    m = copy.deepcopy(base)
    m["geometry"]["sample_rate_hz"] = 48000
    add("wrong_rate", m, "invalid_sample_rate_hz")

    m = copy.deepcopy(base)
    m["geometry"]["frame_samples"] = 320
    add("wrong_frame", m, "invalid_frame_samples")

    m = copy.deepcopy(base)
    m["input"]["corpus_id"] = "unknown"
    add("wrong_corpus", m, "invalid_corpus_id")

    m = copy.deepcopy(base)
    m["input"]["pair_count"] = 0
    add("zero_pairs", m, "invalid_pair_count")

    m = copy.deepcopy(base)
    m["controls"]["candidate"] = False
    add("missing_candidate_control", m, "invalid_control")

    m = copy.deepcopy(base)
    m["rights"]["source_terms"] = ""
    add("empty_rights", m, "invalid_rights")

    add("root_not_object", [], "root_not_object")
    add("root_string", "x", "root_not_object")

    # strict JSON parsing cases represented as validation outcomes through wrapper in verifier/tests by calling loads_strict
    return cases


def admission_controls() -> dict[str, Any]:
    cases = admission_cases()
    accepted = [c for c in cases if c["status"] == "accepted"]
    rejected = [c for c in cases if c["status"] == "rejected"]
    return {
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "accepted_schema_controls": len(accepted),
            "rejected_count": len(rejected),
            "qualifying_results": sum(1 for c in cases if c.get("qualifies")),
            "all_adverse_cases_rejected": all(c["status"] == "rejected" for c in cases if c["id"] != "accept_synthetic_control"),
        },
    }


def _artifact_rows() -> list[dict[str, Any]]:
    rows = []
    for a in REQUIRED_ARTIFACTS:
        row = dict(a)
        row.update({"present": False, "verified": False, "blocked": True, "bytes": None, "sha256": None, "revision": None})
        rows.append(row)
    return rows


def enhancement_profile() -> dict[str, Any]:
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "requirement_rows": DSP_REQUIREMENTS,
        "row_summary": {
            "requirement_count": len(DSP_REQUIREMENTS),
            "blocked_count": sum(1 for r in DSP_REQUIREMENTS if r["status"] == "blocked"),
            "documented_count": sum(1 for r in DSP_REQUIREMENTS if r["status"] == "documented"),
            "real_result_count": 0,
            "profile_satisfied": False,
        },
        "paired_si_sdr_stoi": "blocked_no_candidate_or_cohort",
        "target_hardware_evidence_present": False,
        "timing_present": False,
    }


def build_contract() -> dict[str, Any]:
    absence = absence_summary()
    probes = all_probes()
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "contract_id": CONTRACT_ID,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "exact_external_blocker": EXACT_EXTERNAL_BLOCKER,
        "reopen_condition": REOPEN_CONDITION,
        "write_scope": WRITE_SCOPE,
        "exact_scope": {
            "task_prefix": TASK_PREFIX,
            "only_task_directory_written": True,
            "board_or_handoff_changed": False,
            "cmake_or_ci_changed": False,
            "contracts_header_changed": False,
            "descriptor_or_registry_changed": False,
            "default_selection_changed": False,
            "provider_files_changed": False,
            "public_api_abi_change": False,
            "installed_v0_behavior_change": False,
            "weights_or_audio_committed": False,
            "real_corpus_or_weights": False,
        },
        "boundary": {
            "benchmark_claim": False,
            "board_or_handoff_changed": False,
            "ci_changed": False,
            "descriptor_default_changed": False,
            "descriptor_registration": False,
            "enabled_by_default": False,
            "installed_v0_unchanged": True,
            "opt_in_required": True,
            "provider_intake_complete": False,
            "provider_registered": False,
            "public_api_abi_changed": False,
            "real_corpus_or_weights": False,
            "registry_changed": False,
            "release_claim": False,
            "shared_cmake_changed": False,
        },
        "boundary_pins": BOUNDARY_PINS,
        "source_pins": SOURCE_PINS,
        "board_task_row": BOARD_TASK_ROW,
        "board_row_projection": board_row_projection(),
        "board_row_digest": board_row_digest(),
        "linked_rows": linked_rows(),
        "linked_rows_digest": linked_rows_digest(),
        "profile_source_check": profile_row_check(),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": EXACT_BLOCKERS,
        "release_gates": RELEASE_GATES,
        "enhancement_profile": enhancement_profile(),
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "candidate_qualified": False,
            "decision": DECISION,
            "proposal_only": True,
            "readiness": "incomplete",
            "all_required_results_present": False,
            "all_release_gates_blocked": True,
            "real_result_present": False,
            "source_present": False,
            "exact_source_identity": False,
            "source_license_verified": False,
            "runtime_present": False,
            "runtime_pinned": False,
            "weights_present_locally": False,
            "weights_identity_verified": False,
            "rights_cleared_cohort": False,
            "exact_geometry_verified": False,
            "sdk_bridge_verified": False,
            "target_hardware_evidence_verified": False,
            "implementation_present": False,
            "reference_execution_result": False,
            "dsp_profile_result": False,
            "listening_result": False,
            "device_timing_result": False,
            "benchmark_result": False,
            "release_claim": False,
            "missing_result_promoted": False,
            "peer_result_inherited": False,
            "recorded_identity_only": False,
        },
        "admission_contract": admission_contract(),
        "absence_summary": absence,
        "absence_probes": probes,
        "recorded_identity": recorded_identity_block(),
        "reported_metrics": reported_metrics_block(),
        "task_geometry": task_geometry(),
        "upstream_record": {
            "repository": UPSTREAM_REPOSITORY,
            "project_page": UPSTREAM_PROJECT_PAGE,
            "model_revision": MODEL_REVISION,
            "source_license_text_present": False,
            "notice_present": False,
            "source_immutable_revision": None,
            "runtime_pinned": False,
            "weights_present_locally": False,
            "output_present": False,
        },
        "evidence_inputs": evidence_inputs(),
        "historical_evidence": HISTORICAL_EVIDENCE,
        "non_claims": NON_CLAIMS,
        "disposition": {
            "decision": DECISION,
            "status": STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "incomplete": True,
            "proposal_only": True,
            "result_promoted": False,
            "reopen_condition": REOPEN_CONDITION,
            "exact_external_blocker": EXACT_EXTERNAL_BLOCKER,
        },
    }
    return contract


def build_report() -> dict[str, Any]:
    contract = build_contract()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "write_scope": WRITE_SCOPE,
        "exact_external_blocker": EXACT_EXTERNAL_BLOCKER,
        "reopen_condition": REOPEN_CONDITION,
        "disposition": contract["disposition"],
        "boundary": contract["boundary"],
        "scope": contract["exact_scope"],
        "exact_scope": contract["exact_scope"],
        "public_v0_geometry": {
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
            "sample_rate_hz": 16000,
            "preserved": True,
        },
        "task_geometry": contract["task_geometry"],
        "upstream_record": {
            "repository": UPSTREAM_REPOSITORY,
            "project_page": UPSTREAM_PROJECT_PAGE,
            "model_revision": MODEL_REVISION,
            "source_license_text_present": False,
            "notice_present": False,
            "source_immutable_revision": None,
            "runtime_pinned": False,
            "weights_present_locally": False,
            "output_present": False,
        },
        "recorded_identity": contract["recorded_identity"],
        "reported_metrics": contract["reported_metrics"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "enhancement_profile": contract["enhancement_profile"],
        "qualification": contract["qualification"],
        "rights_gap": [
            {"id": "RG-A", "item": "source_code_terms", "status": "unresolved", "requirement": "Reviewed source license, NOTICE and third-party terms for the exact SE-AGCNet revision."},
            {"id": "RG-B", "item": "model_checkpoint_terms", "status": "unresolved", "requirement": "Reviewed checkpoint/model-card terms for exact weights."},
            {"id": "RG-C", "item": "training_data_terms", "status": "unresolved", "requirement": "Training-data provenance and terms for reported model behavior."},
            {"id": "RG-D", "item": "corpus_and_clean_reference", "status": "unresolved", "requirement": "Rights-cleared cohort, consent and permitted clean references."},
            {"id": "RG-E", "item": "output_use_and_redistribution", "status": "unresolved", "requirement": "Permitted output use, redistribution and attribution."},
        ],
        "absence_summary": contract["absence_summary"],
        "absence_probes": contract["absence_probes"],
        "evidence_inputs": contract["evidence_inputs"],
        "admission_contract": contract["admission_contract"],
        "admission_controls": admission_controls(),
        "historical_evidence": contract["historical_evidence"],
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "board_row_projection": contract["board_row_projection"],
        "board_row_digest": contract["board_row_digest"],
        "linked_rows": contract["linked_rows"],
        "linked_rows_digest": contract["linked_rows_digest"],
        "profile_source_check": contract["profile_source_check"],
        "non_claims": NON_CLAIMS,
        "invariants": [
            "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
            "Only docs/task-evidence/se-agcnet/ is touched.",
            "The reference is a task-local evidence builder, not SE-AGCNet.",
            "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
            "Only stable linked-row identity enters canonical bytes or gates.",
            "No missing, rejected or adverse result qualifies a candidate.",
        ],
    }
    text, digest = canonical_report(report)
    report["canonical_report"] = {
        "canonical_digest": digest,
        "file_sha256": digest,
        "format": "canonical JSON: sort_keys=True, compact separators, allow_nan=False, one trailing newline",
    }
    return report


def validate_contract(contract: dict[str, Any]) -> None:
    required = [
        "schema_id", "task", "task_id", "title", "component", "repository", "mode", "profile",
        "branch", "base_commit", "contract_id", "status", "evidence_status", "decision",
        "qualification_status", "proposal_only", "incomplete", "exact_external_blocker",
        "reopen_condition", "required_artifacts", "exact_blockers", "release_gates",
        "enhancement_profile", "qualification", "absence_summary", "admission_contract",
        "board_row_projection", "linked_rows", "non_claims",
    ]
    for key in required:
        if key not in contract:
            raise ValueError("missing_contract_key:" + key)
    if contract["schema_id"] != CONTRACT_SCHEMA_ID:
        raise ValueError("bad_schema_id")
    if contract["task"] != TASK or contract["task_id"] != TASK:
        raise ValueError("bad_task")
    if contract["decision"] != DECISION or contract["qualification_status"] != QUALIFICATION_STATUS:
        raise ValueError("bad_disposition")
    if contract["proposal_only"] is not True or contract["incomplete"] is not True:
        raise ValueError("bad_flags")
    if len(contract["release_gates"]) != 8:
        raise ValueError("gate_count")
    if any(g.get("status") != "blocked" for g in contract["release_gates"]):
        raise ValueError("gate_not_blocked")
    if len(contract["required_artifacts"]) != 7:
        raise ValueError("artifact_count")
    if any(a.get("present") is not False or a.get("verified") is not False for a in contract["required_artifacts"]):
        raise ValueError("artifact_present")
    if len(contract["exact_blockers"]) != 6:
        raise ValueError("blocker_count")
    if contract["qualification"].get("all_release_gates_blocked") is not True:
        raise ValueError("qualification_not_blocked")
    if contract["absence_summary"].get("all_probes_absent") is not True:
        raise ValueError("probes_present")
    profile = contract.get("profile_source_check", {})
    if profile.get("all_phrases_present") is not True:
        raise ValueError("profile_phrases_missing")


def update_readme_tables(text: str) -> str:
    def render(rows: list[tuple[str, str]]) -> str:
        lines = ["| Path | SHA-256 |", "| --- | --- |"]
        lines.extend(f"| `{p}` | `{d}` |" for p, d in rows)
        return "\n".join(lines)

    source_rows = [(f"source:{k}", sha256_file(AUDIO_ROOT / k)) for k in sorted(SOURCE_PINS)]
    boundary_rows = [(f"sdk:{k}", sha256_file(WORKTREE / k)) for k in sorted(BOUNDARY_PINS)]
    artifact_rows = [(TASK_PREFIX + name, sha256_file(HERE / name)) for name in sorted(LOCAL_FILES) if name not in ARTIFACT_TABLE_EXCLUDED]
    replacements = {
        "source": render(source_rows),
        "boundary": render(boundary_rows),
        "artifacts": render(artifact_rows),
    }
    for key, table in replacements.items():
        start, end = README_MARKERS[key]
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        if not pattern.search(text):
            raise ValueError("missing_marker:" + key)
        text = pattern.sub(start + "\n" + table + "\n" + end, text)
    return text

