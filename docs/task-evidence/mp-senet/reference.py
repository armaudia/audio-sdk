# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-MP-SENET.

Standard library only. The merged evidence records MP-SENet as an offline
16 kHz phase-aware enhancer that estimates magnitude and phase spectra in
parallel, with an MIT-labelled upstream repository, a pretrained
VoiceBank+DEMAND checkpoint and an author-reported PESQ of 3.50. It records no
immutable revision, checkpoint file name, byte count, SHA-256, runtime lock,
inference geometry, rights bundle, cohort or local output. This module pins
the evidence that does exist, proves a fixed absence inventory, exercises a
fail-closed caller-supplied-asset manifest without loading or executing a
model, and builds canonical DEFER bytes. Nothing here is a model, inference,
audio, quality, timing, listening, benchmark or release result.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-MP-SENET"
TASK_TITLE = "MP-SENet"
COMPONENT_ID = "mp-senet"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/mp-senet/ only"
TASK_PREFIX = "docs/task-evidence/mp-senet/"
CONTRACT_ID = "audio-sdk/mp-senet-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/mp-senet-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/mp-senet-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/mp-senet-caller-asset/0.1"
BASE_COMMIT = "d2eae1246561fe11c5a3d17733ddd46db53e7803"
BRANCH = "swarm/SDK-MP-SENET"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-MP-SENET")
REVIEWER = "reviewer-MP-SENET"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
UPSTREAM_REPOSITORY = "https://github.com/yxlu-0102/MP-SENet"
MODEL_REPOSITORY = "https://github.com/yxlu-0102/MP-SENet"
MODEL_REVISION = None
REPORTED_SAMPLE_RATE_HZ = 16000
REPORTED_CHANNELS = 1
REPORTED_CHECKPOINT_COUNT = None
REPORTED_PARAMETER_COUNT = None
RECORDED_CHECKPOINT_VARIANT = "mp-senet-voicebank-demand"
RECORDED_CHECKPOINT_VARIANT_LABEL = "pretrained VoiceBank+DEMAND checkpoint"
RECORDED_CHECKPOINT_DIR = None
RECORDED_CHECKPOINT_PATH = None
RECORDED_CHECKPOINT_BYTES = None
RECORDED_CHECKPOINT_SHA256 = None
RECORDED_CONFIG_PATH = None
RECORDED_OVERRIDES_PATH = None
RECORDED_MANIFEST_PATH = None
RECORDED_READINESS_REPORT = (
    "research/evidence/pilot-discovery-20261027/source.txt")
REPORTED_PESQ = "3.50"
REPORTED_PAPER = (
    "https://www.isca-archive.org/interspeech_2023/lu23e_interspeech.html")
CALLER_MODE = "offline_whole_utterance"
CALLER_CORPUS = "voicebank-demand"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml root without a recursive walk or network use."""
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
SDK_ROOT = WORKTREE

# Read-only inputs. source: paths are workspace-relative; sdk: paths are
# SDK-worktree-relative. The mutable shared board is never pinned.
SOURCE_PINS = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/pilot_evaluation_progress.md":
        "7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf",
    "research/evidence/pilot-discovery-20261027/source.txt":
        "3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590",
    "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/candidate_accounting.csv":
        "3ab7b404129737666c1e74c7e9a7107f45c8c0575018d2591bef75d3782473c5",
    "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/manifest.json":
        "6c745b13486b92ec7f1e4db868f3109ce246cac6c944968d22bfd9cb01ae397f",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
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
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
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
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".th",
}

# Fixed probes only; no recursive walk. All must remain absent.
WORKSPACE_PROBES = (
    "data/checkouts/mp-senet",
    "data/checkouts/MP-SENet",
    "data/checkouts/mpsenet",
    "data/models/mp-senet",
    "data/models/MP-SENet",
    "data/models/mpsenet",
    "data/weights/mp-senet",
    "data/envs/mp-senet",
    "data/envs/mp-senet/requirements.lock",
    "data/manifests/mp-senet-assets.json",
    "data/rights/mp-senet-rights.json",
    "data/runs/mp-senet-cohort/manifest.json",
    "research/voice-enhancement-20261101/repos/mp-senet",
    "research/voice-enhancement-20261101/models/mp-senet",
    "reports/mp-senet",
)
WORKTREE_PROBES = (
    "adapters/mp-senet",
    "schemas/providers/mp-senet",
    "third_party/MP-SENet",
    "third_party/mp-senet",
    "build/check-env/lib/python3.12/site-packages/mp_senet",
)
HOME_PROBES = (
    "~/.cache/huggingface/hub/models--mp-senet",
    "~/.cache/huggingface/hub/models--mpsenet",
    "~/.cache/torch/hub/checkpoints/mp_senet",
    "~/.pyenv/versions/3.12.16/lib/python3.12/site-packages/mp_senet",
)

NON_CLAIMS = [
    "No MP-SENet source copy, repository snapshot, checkpoint, weight "
    "fragment, inference configuration, runtime, corpus, recording, output "
    "or vendor result is present, loaded or executed.",
    "No model inference, audio read or write, listening, paired SI-SDR or "
    "STOI scoring, clean-speech preservation, peak, alignment, content-delay "
    "or device-timing measurement is performed.",
    "No real or synthetic waveform is scored; the admission control is a "
    "schema object only.",
    "No checkpoint file name, byte count or SHA-256 is recorded for MP-SENet; "
    "the upstream PESQ 3.50 is a source claim, not a local measurement.",
    "No local DNS result, VoiceBank score, FastEnhancer, DeepFilterNet3, "
    "DTLN, GTCRN, LaCo-SENet, ConvFSENet or other peer result is inherited "
    "or pooled.",
    "No benchmark, quality, latency, resource, streaming, provider or release "
    "claim is made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "fastenhancer-small-reference",
        "path": "docs/task-evidence/fastenhancer-small-reference/report.json",
        "class": "separate_offline_cpu_denoiser",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "FastEnhancer Small is a separate offline CPU comparator; "
                    "its local DNS metrics, runtime and assets do not "
                    "establish MP-SENet phase-aware quality.",
    },
    {
        "component": "laco-senet",
        "path": "docs/task-evidence/laco-senet/report.json",
        "class": "separate_streaming_senet",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "LaCo-SENet is a different streaming SENet family with its "
                    "own checkpoint identities, latency settings and source "
                    "license blocker; no architecture, metric or timing "
                    "transfers to MP-SENet.",
    },
    {
        "component": "gtcrn-streaming-onnx",
        "path": "docs/task-evidence/gtcrn-streaming-onnx/report.json",
        "class": "separate_streaming_component",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Base GTCRN streaming ONNX has its own lookahead and "
                    "state contract; it is not MP-SENet offline inference.",
    },
    {
        "component": "convfsenet",
        "path": "docs/task-evidence/convfsenet/report.json",
        "class": "separate_causal_enhancer",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "ConvFSENet is a separate causal enhancer with its own "
                    "checkpoint, quantization and geometry blockers.",
    },
)

HISTORICAL_EVIDENCE = (
    {
        "source": "research/noise_suppression_candidate_census.md",
        "class": "census_source_lead",
        "admitted_as_result": False,
        "boundary": "Names MP-SENet as a parallel magnitude/phase estimator "
                    "with an offline 16 kHz quality role, an MIT-labelled "
                    "repository, a pretrained VoiceBank+DEMAND checkpoint and "
                    "author-reported PESQ 3.50; no local score.",
    },
    {
        "source": "research/evidence/pilot-discovery-20261027/source.txt",
        "class": "discovery_source_lead",
        "admitted_as_result": False,
        "boundary": "Records MIT code, an inference script, a pretrained "
                    "checkpoint and PESQ 3.50 as source leads; explicitly "
                    "says the paper/checkpoint are not directly comparable to "
                    "DNS2020 and need overlap/hash checks.",
    },
    {
        "source": "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/candidate_accounting.csv",
        "class": "candidate_accounting_absence",
        "admitted_as_result": False,
        "boundary": "Marks candidate-mp-senet blocked with code available and "
                    "weights located_unverified; requires pinning/hashing the "
                    "artifact, resolving training/test overlap and measuring "
                    "CPU/RAM.",
    },
    {
        "source": RECORDED_READINESS_REPORT,
        "class": "readiness_absence",
        "admitted_as_result": False,
        "boundary": "The discovery log records no immutable revision, "
                    "checkpoint file, byte count, digest, runtime lock or "
                    "inference geometry; no inference ran.",
    },
    {
        "source": "research/noise_suppression_assets_20261027.json",
        "class": "asset_register_absence",
        "admitted_as_result": False,
        "boundary": "The 20-row register contains no MP-SENet entry, so no "
                    "local asset identity is available.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Marks mp-senet as considered, disposition sdk-model and "
                    "verification_profile enhancement; it is not a result.",
    },
)


# ---------------------------------------------------------------------------
# Strict JSON, canonical bytes and hashing.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Stable board identity. The mutable board file is read, never pinned.
# ---------------------------------------------------------------------------


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    depends_on = row.get("depends_on")
    if not isinstance(depends_on, list):
        raise ValueError("board_depends_on_not_list")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(depends_on),
    }


def _board_tasks(path: Path | None = None) -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [row for row in _board_tasks(path)
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0], require_component=True)
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    if tuple(projection["depends_on"]) != DEPENDS_ON:
        raise ValueError("board_depends_on_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    result: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_absent:" + row_id)
        result.append(_project(row, require_component=row_id == TASK))
    if result[0]["component"] != COMPONENT_ID:
        raise ValueError("linked_component_mismatch")
    return tuple(result)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None
                         else board_row_projection())


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


# ---------------------------------------------------------------------------
# Fixed evidence probes. No recursive walk and no network.
# ---------------------------------------------------------------------------


def _probe(path: Path, label: str, workspace: bool, worktree: bool,
           home: bool) -> dict:
    return {
        "path": label,
        "present": path.exists(),
        "searched_workspace": workspace,
        "searched_sdk_worktree": worktree,
        "searched_home_cache": home,
    }


def workspace_probes() -> list[dict]:
    return [_probe(AUDIO_ROOT / path, path, True, False, False)
            for path in WORKSPACE_PROBES]


def worktree_probes() -> list[dict]:
    return [_probe(WORKTREE / path, path, False, True, False)
            for path in WORKTREE_PROBES]


def home_probes() -> list[dict]:
    return [_probe(Path(path).expanduser(), path, False, False, True)
            for path in HOME_PROBES]


def all_probes() -> list[dict]:
    return workspace_probes() + worktree_probes() + home_probes()


def absence_summary(probes: list[dict] | None = None) -> dict:
    rows = all_probes() if probes is None else probes
    return {
        "probe_count": len(rows),
        "workspace_probe_count": sum(1 for row in rows
                                     if row["searched_workspace"]),
        "worktree_probe_count": sum(1 for row in rows
                                    if row["searched_sdk_worktree"]),
        "home_probe_count": sum(1 for row in rows
                                if row["searched_home_cache"]),
        "present_count": sum(1 for row in rows if row["present"] is not False),
        "all_probes_absent": all(row["present"] is False for row in rows),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
    }


def asset_registry() -> dict:
    """Summarize the local asset register without inventing an MP-SENet entry."""
    path = AUDIO_ROOT / "research/noise_suppression_assets_20261027.json"
    document = read_strict_json(path)
    candidates = document.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("asset_register_candidates_not_list")
    ids = sorted(row.get("id") for row in candidates
                 if isinstance(row, dict) and isinstance(row.get("id"), str))
    if len(ids) != len(set(ids)):
        raise ValueError("asset_register_duplicate_id")
    mp_ids = [row_id for row_id in ids
              if "mp-senet" in row_id.lower() or "mpsenet" in row_id.lower()]
    return {
        "path": "research/noise_suppression_assets_20261027.json",
        "candidate_count": len(ids),
        "candidate_ids_sha256": object_digest(ids),
        "mp_entry_present": bool(mp_ids),
        "mp_candidate_ids": mp_ids,
        "asset_identity_available_for_mp": False,
        "note": "The register contains 20 separate denoising assets and no "
                "MP-SENet candidate, checkpoint name, revision, byte count, "
                "SHA-256 or checkpoint terms.",
    }


EVIDENCE_INPUT_PATHS = (
    "research/noise_suppression_candidate_census.md",
    "research/noise_suppression_assets_20261027.json",
    "research/voice-enhancement-20261101/candidate_matrix.csv",
    "research/pilot_evaluation_progress.md",
    "research/evidence/pilot-discovery-20261027/source.txt",
    "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/candidate_accounting.csv",
    "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/manifest.json",
    "audio-benchmark-platform/plan/INVENTORY.json",
)


def evidence_inputs() -> list[dict]:
    rows: list[dict] = []
    for relative in EVIDENCE_INPUT_PATHS:
        path = AUDIO_ROOT / relative
        payload = path.read_bytes()
        rows.append({
            "path": relative,
            "sha256": sha256_bytes(payload),
            "mentions_mp_senet": (b"MP-SENet" in payload
                                  or b"mp-senet" in payload
                                  or b"mpsenet" in payload),
            "is_result": False,
        })
    return rows


# ---------------------------------------------------------------------------
# Pins, README digest tables and SOURCES.sha256.
# ---------------------------------------------------------------------------


def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows: list[dict] = []
    for relative in sorted(pins):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        rows.append({
            "path": relative,
            "sha256": pins[relative],
            "actual": actual,
            "verified": actual == pins[relative],
        })
    return rows


def _local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + relative))
    for relative, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + relative))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable "
        "linked-row projection is gated.",
    ]
    lines.extend(f"{digest}  {path}" for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError("malformed_pin_line:" + str(number))
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:")
                or path.startswith(TASK_PREFIX)):
            raise ValueError("unknown_pin_prefix:" + str(number))
        if path in seen:
            raise ValueError("duplicate_pin:" + str(number))
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def expected_readme_keys() -> dict[str, set[str]]:
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


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: list[tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:"
                f"extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                relative = key[len("source:"):]
                expected_digest = SOURCE_PINS[relative]
                path = AUDIO_ROOT / relative
            elif section == "boundary":
                relative = key[len("sdk:"):]
                expected_digest = BOUNDARY_PINS[relative]
                path = SDK_ROOT / relative
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if not path.is_file() or sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = [f"| `source:{name}` | `{digest}` |"
                for name, digest in sorted(SOURCE_PINS.items())]
    elif section == "boundary":
        rows = [f"| `sdk:{name}` | `{digest}` |"
                for name, digest in sorted(BOUNDARY_PINS.items())]
    elif section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in _local_manifest_paths():
            if name in ARTIFACT_TABLE_EXCLUDED:
                continue
            path = HERE / name
            rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                        f"{path.stat().st_size} |")
    else:
        raise ValueError("unknown_readme_section:" + section)
    return "\n".join(rows)


def update_readme_table(text: str, section: str) -> str:
    block = render_digest_table(section)
    start, end = README_MARKERS[section]
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[:start_index] + start + "\n" + block + "\n" + end + \
        text[end_index:]


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Task and upstream records.
# ---------------------------------------------------------------------------


def upstream_record() -> dict:
    return {
        "source_repository": UPSTREAM_REPOSITORY,
        "source_repository_source": "census_and_discovery_source_lead",
        "source_license_spdx": None,
        "source_license_reported": "MIT",
        "source_license_status": "reported_mit_not_locally_verified",
        "source_license_text_present": False,
        "source_immutable_revision": None,
        "source_revision_pin_available": False,
        "source_files_present": False,
        "model_repository": MODEL_REPOSITORY,
        "model_revision": MODEL_REVISION,
        "model_revision_recorded": False,
        "model_revision_locally_verified": False,
        "model_card_license_reported": "MIT",
        "model_card_license_verified_locally": False,
        "checkpoint_count_reported": REPORTED_CHECKPOINT_COUNT,
        "parameter_count_reported": REPORTED_PARAMETER_COUNT,
        "reported_approach": "parallel magnitude and phase spectrum "
                             "estimation",
        "reported_mode": "offline_whole_utterance_non_streaming",
        "runtime_pinned": False,
        "cohort_present": False,
        "output_present": False,
        "note": "The census labels the upstream repository MIT and describes a "
                "pretrained VoiceBank+DEMAND checkpoint and inference script, "
                "but no commit, checkpoint file name, byte count, SHA-256, "
                "model-card text or license text is recorded locally. The "
                "author-reported PESQ 3.50 and the paper URL are leads only.",
    }


def recorded_identity_block() -> dict:
    return {
        "status": "no_checkpoint_identity_recorded_in_merged_evidence",
        "model_repository": MODEL_REPOSITORY,
        "model_revision": MODEL_REVISION,
        "checkpoint_variant": None,
        "checkpoint_dir": RECORDED_CHECKPOINT_DIR,
        "checkpoint_path": RECORDED_CHECKPOINT_PATH,
        "checkpoint_bytes": RECORDED_CHECKPOINT_BYTES,
        "checkpoint_sha256": RECORDED_CHECKPOINT_SHA256,
        "config_path": RECORDED_CONFIG_PATH,
        "overrides_path": RECORDED_OVERRIDES_PATH,
        "manifest_path": RECORDED_MANIFEST_PATH,
        "recorded_by": [
            "research/noise_suppression_candidate_census.md",
            "research/evidence/pilot-discovery-20261027/source.txt",
            "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/candidate_accounting.csv",
            "audio-benchmark-platform/plan/INVENTORY.json",
        ],
        "locally_present": False,
        "locally_verified": False,
        "digest_verified_locally": False,
        "byte_count_verified_locally": False,
        "admitted_as_result": False,
        "qualifies": False,
    }


def reported_metrics_block() -> dict:
    return {
        "status": "source_reported_not_measured_here",
        "admitted_as_result": False,
        "qualifies": False,
        "checkpoint_variant": None,
        "cohort": "VoiceBank+DEMAND test (upstream)",
        "pesq": REPORTED_PESQ,
        "stoi": None,
        "csig": None,
        "cbak": None,
        "covl": None,
        "paper": REPORTED_PAPER,
        "parameter_count": REPORTED_PARAMETER_COUNT,
        "note": "Only the census/discovery PESQ 3.50 is recorded. No upstream "
                "table, checkpoint manifest or local run was read. The value "
                "is not reproduced, not a local measurement and not "
                "comparable to the project DNS2020 subset.",
    }


def task_geometry() -> dict:
    return {
        "reported_task": "single-channel speech enhancement / noise "
                         "suppression",
        "reported_domain": "VoiceBank+DEMAND, 16 kHz",
        "reported_channels": REPORTED_CHANNELS,
        "reported_sample_rate_hz": REPORTED_SAMPLE_RATE_HZ,
        "reported_mode": "offline_whole_utterance_non_streaming",
        "reported_approach": "parallel magnitude and phase spectrum "
                             "estimation",
        "reported_phase_aware": True,
        "reported_latency_setting_count": None,
        "reported_latency_range_ms": None,
        "reported_latency_settings_ms": None,
        "reported_seed_count": None,
        "reported_checkpoint_count": REPORTED_CHECKPOINT_COUNT,
        "reported_parameter_count": REPORTED_PARAMETER_COUNT,
        "reported_checkpoint_variant_recorded": None,
        "frame_samples": None,
        "hop_samples": None,
        "chunk_samples": None,
        "stft_window_samples": None,
        "lookahead_samples": None,
        "state_reset_policy": None,
        "pacing_policy": None,
        "exact_geometry_verified": False,
        "sdk_v0_rate_matches_reported": True,
        "sdk_v0_mono_matches_reported": True,
        "sdk_v0_adapter_mapping_present": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "sample_format": "f32",
        "preserved": True,
        "mp_mapping_present": False,
    }


def disposition_block() -> dict:
    return {
        "task_mode": MODE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "source_present": False,
        "checkpoint_present_locally": False,
        "checkpoint_identity_recorded_only": False,
        "runtime_present": False,
        "adapter_present": False,
        "rights_cleared_cohort_present": False,
        "output_present": False,
        "result_promoted": False,
        "summary": "MP-SENet is an offline, phase-aware 16 kHz enhancer. The "
                   "census and discovery log name an MIT-labelled repository, "
                   "a pretrained VoiceBank+DEMAND checkpoint and an "
                   "author-reported PESQ 3.50, but no immutable revision, "
                   "checkpoint identity, runtime, offline inference contract, "
                   "rights-cleared cohort or local result is present.",
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "network_access": False,
        "weights_downloaded": False,
        "weights_vendored": False,
        "source_vendored": False,
        "runtime_invoked": False,
        "model_executed": False,
        "real_audio": False,
        "real_corpus": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_default": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "peer_evidence_inherited": False,
    }


def exact_scope_block() -> dict:
    return {
        "write_scope": WRITE_SCOPE,
        "task_prefix": TASK_PREFIX,
        "only_task_directory_written": True,
        "provider_files_changed": False,
        "adapter_files_changed": False,
        "descriptor_or_registry_changed": False,
        "contracts_header_changed": False,
        "cmake_or_ci_changed": False,
        "board_or_handoff_changed": False,
        "default_selection_changed": False,
        "weights_or_audio_committed": False,
    }


def boundary_block() -> dict:
    return {
        "provider_registration": False,
        "adapter_json_added": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "native_engine_built": False,
        "runtime_imported": False,
        "weights_vendored": False,
        "audio_added": False,
        "corpus_added": False,
    }


def rights_gap() -> list[dict]:
    return [
        {"id": "RG-A", "item": "source_code_terms",
         "status": "unverified",
         "requirement": "Reviewed MIT source license text, notice and "
                        "per-file identity for the exact source revision. The "
                        "census labels the repository MIT, but no license "
                        "text, commit or file list is staged."},
        {"id": "RG-B", "item": "model_card_and_checkpoint_terms",
         "status": "unresolved",
         "requirement": "A repository MIT label does not by itself prove "
                        "checkpoint-specific terms; record them separately "
                        "for the exact weight file."},
        {"id": "RG-C", "item": "training_data_terms",
         "status": "unresolved",
         "requirement": "Training-data provenance and terms for the exact "
                        "VoiceBank+DEMAND checkpoint, including the "
                        "training/test overlap flagged by the census."},
        {"id": "RG-D", "item": "corpus_and_clean_reference",
         "status": "unresolved",
         "requirement": "Rights-cleared 16 kHz recordings, speaker consent "
                        "and permitted clean references for paired scores."},
        {"id": "RG-E", "item": "output_use_and_redistribution",
         "status": "unresolved",
         "requirement": "Permitted output use, redistribution and "
                        "attribution for any reproduced or enhanced signal."},
    ]


ENHANCEMENT_REQUIREMENTS = (
    {
        "id": "ENH-01",
        "requirement": "Identity/noisy control and an established "
                       "task-matched baseline.",
        "status": "blocked",
        "evidence": "No control or baseline output exists on exact MP-SENet "
                    "assets, and no phase-aware comparator is run; separate "
                    "FastEnhancer, LaCo-SENet and DeepFilterNet3 results are "
                    "not inherited.",
    },
    {
        "id": "ENH-02",
        "requirement": "Paired SI-SDR and STOI where permitted clean "
                       "references exist.",
        "status": "blocked",
        "evidence": "No rights-cleared 16 kHz paired cohort and no score.",
    },
    {
        "id": "ENH-03",
        "requirement": "Clean-speech preservation, peaks and invalid outputs.",
        "status": "blocked",
        "evidence": "No preservation, peak, clipping or nonfinite record; "
                    "the phase branch is not exercised.",
    },
    {
        "id": "ENH-04",
        "requirement": "Separately labeled predictive screen or authorized "
                       "listening.",
        "status": "blocked",
        "evidence": "No screen, listening protocol, panel or permission.",
    },
    {
        "id": "ENH-05",
        "requirement": "Alignment, state, memory and measured "
                       "content/availability timing.",
        "status": "blocked",
        "evidence": "No runtime, alignment, state, memory, chunk timing or "
                    "measured content delay.",
    },
    {
        "id": "ENH-06",
        "requirement": "Offline whole-utterance geometry: rate, channels, "
                       "FFT/STFT window and hop, magnitude/phase branch "
                       "layout, padding, output length and no streaming "
                       "lookahead.",
        "status": "blocked",
        "evidence": "The evidence records an offline 16 kHz phase-aware "
                    "approach but no FFT/STFT window, hop, padding, branch "
                    "layout, output-length or normalization contract.",
    },
    {
        "id": "ENH-07",
        "requirement": "Quiet/active speech, idle noise and onset/offset "
                       "strata.",
        "status": "blocked",
        "evidence": "No cohort or stratum definition exists.",
    },
    {
        "id": "ENH-08",
        "requirement": "Keep paired, unpaired, synthetic, human and "
                       "source-reported evidence separate.",
        "status": "documented",
        "evidence": "The package records absence and separation only; the "
                    "upstream VoiceBank metrics are labelled source-reported "
                    "and no result of any class is promoted.",
    },
)


def enhancement_profile_block() -> dict:
    rows = [dict(row) for row in ENHANCEMENT_REQUIREMENTS]
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "requirement_rows": rows,
        "row_summary": {
            "requirement_count": len(rows),
            "blocked_count": sum(1 for row in rows
                                 if row["status"] == "blocked"),
            "documented_count": sum(1 for row in rows
                                    if row["status"] == "documented"),
            "real_result_count": 0,
            "profile_satisfied": False,
        },
        "paired_si_sdr_stoi":
            "blocked_no_rights_cleared_16khz_clean_references",
        "identity_control_present": False,
        "task_matched_baseline_present": False,
        "clean_speech_preservation_present": False,
        "peaks_and_invalid_present": False,
        "listening_present": False,
        "timing_present": False,
        "rights_independent_gates_present": False,
    }


def profile_row_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Enhancement |")]
    return {
        "path": PROFILE_SOURCE_REL,
        "row_count": len(rows),
        "unique_row": len(rows) == 1,
        "phrases_present": [phrase for phrase in PROFILE_PHRASES
                            if len(rows) == 1 and phrase in rows[0]],
        "all_phrases_present": len(rows) == 1 and all(
            phrase in rows[0] for phrase in PROFILE_PHRASES),
    }


# ---------------------------------------------------------------------------
# Required artifacts, blockers and gates.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "source_snapshot",
         "The yxlu-0102/MP-SENet source at an immutable 40-hex commit with "
         "reviewed MIT license text, notice, per-file SHA-256 and a map from "
         "the model, inference script and configuration to source files."),
        ("ART-02", "checkpoint_bundle",
         "The exact pretrained VoiceBank+DEMAND checkpoint at immutable "
         "identity with file name, byte count, SHA-256, tensor schema, "
         "inference-script revision and checkpoint-specific terms."),
        ("ART-03", "runtime_lock",
         "A locked offline runtime with exact interpreter, PyTorch and "
         "package versions, byte counts, SHA-256 values, CPU/MPS device, "
         "determinism settings and a recorded supported platform."),
        ("ART-04", "rights_bundle",
         "Reviewed source, checkpoint and VoiceBank+DEMAND training-data "
         "terms; corpus and clean-reference permission; output use, "
         "redistribution and attribution."),
        ("ART-05", "offline_geometry",
         "Frozen offline whole-utterance contract: sample rate, channels, "
         "FFT/STFT window and hop, magnitude and phase branch layout, "
         "padding, output length, normalization, no streaming lookahead and "
         "fresh state per call."),
        ("ART-06", "rights_cleared_cohort",
         "A frozen rights-cleared 16 kHz mono cohort with paired clean "
         "references where permitted, quiet/active and idle-noise strata, "
         "onset/offset cases and held-out splits."),
        ("ART-07", "enhancement_results",
         "Independent Enhancement results: identity/noisy control, "
         "task-matched baseline, paired SI-SDR/STOI, preservation, peaks, "
         "invalid outputs, phase-branch validity, alignment, memory, timing, "
         "listening or labeled predictive screen and uncertainty."),
    ]
    return [{
        "id": artifact_id,
        "kind": kind,
        "requirement": requirement,
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "bytes": None,
    } for artifact_id, kind, requirement in rows]


def exact_blockers() -> list[dict]:
    rows = [
        ("BLK-01", "ART-01", ["RG-01", "RG-04"],
         "Source identity and code license",
         "No MP-SENet source snapshot, immutable revision, reviewed MIT "
         "license text, notice or per-file digest is staged. The census and "
         "discovery log name the repository and an MIT label only."),
        ("BLK-02", "ART-02", ["RG-01", "RG-03"],
         "Checkpoint identity, terms and local bytes",
         "The census records that a pretrained VoiceBank+DEMAND checkpoint "
         "exists, but no file name, revision, byte count or SHA-256 is "
         "recorded; checkpoint-specific terms and training/test overlap are "
         "unresolved."),
        ("BLK-03", "ART-03", ["RG-02"],
         "Pinned offline runtime",
         "No MP-SENet runtime, interpreter lock, PyTorch package, wheel, "
         "device profile, determinism setting or importable module exists."),
        ("BLK-04", "ART-04", ["RG-03"],
         "Rights bundle",
         "Source, checkpoint, VoiceBank+DEMAND training-data, corpus, "
         "clean-reference and output-use terms are unresolved; no rights "
         "review reference exists."),
        ("BLK-05", "ART-05", ["RG-04", "RG-05"],
         "Offline geometry and phase contract",
         "The evidence records an offline phase-aware approach but no "
         "FFT/STFT window, hop, magnitude/phase branch layout, padding, "
         "output length, normalization or fresh-state contract."),
        ("BLK-06", "ART-06", ["RG-04", "RG-06"],
         "Rights-cleared cohort and matched results",
         "No 16 kHz recording, speaker consent, permitted clean reference, "
         "quiet/active or idle-noise stratum, held-out split, control, "
         "baseline, score, timing or memory exists."),
    ]
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": linked_gates,
        "title": title,
        "state": state,
        "status": "open",
        "qualifies": False,
        "required_action": "Supply the named artifact and rights evidence, "
                           "then reproduce and independently review it.",
        "reopen_condition": "Only a caller-supplied exact artifact with "
                            "verified identity and rights can reopen this "
                            "blocker.",
    } for blocker_id, artifact_id, linked_gates, title, state in rows]


def release_gates() -> list[dict]:
    requirements = (
        ("Exact pinned MP-SENet source with immutable revision, reviewed "
         "MIT license text and per-file identity."),
        ("Exact pretrained VoiceBank+DEMAND checkpoint, byte count, "
         "SHA-256, tensor schema and checkpoint-specific terms."),
        ("Locked offline runtime and a recorded supported CPU/MPS platform."),
        ("Rights-cleared 16 kHz cohort with consent and permitted clean "
         "references."),
        ("Frozen offline whole-utterance geometry: FFT/STFT window/hop, "
         "magnitude and phase branch layout, padding, output length and no "
         "streaming lookahead."),
        ("Enhancement result set: controls, baseline, paired metrics, "
         "preservation, peaks and invalid outputs."),
        ("Independent listening or labeled predictive screen plus measured "
         "content/availability timing, memory and resources."),
        ("Opt-in OFF-by-default provider intake, descriptor/default review, "
         "exact-head independent review and release approval."),
    )
    return [{
        "id": "RG-%02d" % index,
        "requirement": requirement,
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK,
        "reopen_condition": "The requirement is independently reproduced "
                            "with exact assets, rights and matched evidence.",
    } for index, requirement in enumerate(requirements, 1)]


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "all_release_gates_blocked": True,
        "real_result_present": False,
        "source_present": False,
        "exact_source_identity": False,
        "source_license_verified": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "weights_present_locally": False,
        "weights_identity_verified": False,
        "recorded_identity_only": False,
        "asset_registry_entry_present": False,
        "rights_cleared_cohort": False,
        "offline_geometry_verified": False,
        "phase_aware_geometry_verified": False,
        "implementation_present": False,
        "reference_execution_result": False,
        "output_validity_result": False,
        "enhancement_profile_result": False,
        "listening_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "peer_result_inherited": False,
        "reason": "Exact source and its license, local checkpoint bytes, "
                  "runtime, offline phase-aware geometry, rights-cleared "
                  "cohort, matched evidence and independent review are all "
                  "absent. No checkpoint identity is recorded.",
    }


def linked_identity_block() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied asset manifest. It validates shape only; it
# never resolves a path, loads a checkpoint or invokes a runtime.
# ---------------------------------------------------------------------------

MANIFEST_TOP_KEYS = ("schema_id", "manifest_id", "source", "checkpoint",
                     "runtime", "geometry", "input", "controls", "rights")
SOURCE_KEYS = ("repository", "revision", "license_spdx", "license_sha256",
               "tree_sha256")
CHECKPOINT_KEYS = ("variant", "filename", "revision", "byte_count", "sha256",
                   "terms_sha256", "license_spdx", "inference_script_path",
                   "inference_script_sha256", "config_path", "config_sha256",
                   "manifest_sha256")
RUNTIME_KEYS = ("python_version", "framework", "framework_version", "device",
                "lock_sha256", "offline_load", "deterministic", "packages")
GEOMETRY_KEYS = ("mode", "channels", "sample_rate_hz", "frame_samples",
                 "hop_samples", "sample_format", "stft_window_samples",
                 "lookahead_samples", "phase_branch", "whole_utterance",
                 "state_reset")
INPUT_KEYS = ("corpus_id", "split", "pair_count", "channels",
              "sample_rate_hz", "clean_reference", "consent",
              "rights_sha256")
CONTROL_KEYS = ("candidate", "identity_passthrough", "noisy_control",
                "task_matched_baseline", "nonfinite_rejection")
RIGHTS_KEYS = ("source_terms", "checkpoint_terms", "training_data_terms",
               "corpus_rights", "clean_reference_permission", "output_use",
               "redistribution", "review_reference")
UNRESOLVED_VALUES = {
    "unknown", "pending", "unspecified", "not specified", "not-specified",
    "tbd", "none", "null", "n/a", "noassertion",
}
MAX_PACKAGES = 128
MAX_CHECKPOINT_BYTES = 8 * 1024 * 1024 * 1024
MAX_PAIRS = 100_000


class _Invalid(Exception):
    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _field(prefix: str, name: str) -> str:
    return prefix + "." + name if prefix else name


def _exact_object(value: Any, fields: tuple[str, ...], prefix: str) -> dict:
    if not isinstance(value, dict):
        raise _Invalid("not_object", prefix or "root")
    missing = [name for name in fields if name not in value]
    if missing:
        raise _Invalid("missing_field", _field(prefix, missing[0]))
    unknown = sorted(name for name in value if name not in fields)
    if unknown:
        raise _Invalid("unknown_field", _field(prefix, unknown[0]))
    return value


def _text(value: Any, field: str, limit: int = 240) -> None:
    if not isinstance(value, str):
        raise _Invalid("invalid_text", field)
    if not value.strip():
        raise _Invalid("empty_text", field)
    if len(value) > limit:
        raise _Invalid("out_of_range", field)
    if any(ord(character) < 32 for character in value):
        raise _Invalid("invalid_text", field)
    if value.strip().lower() in UNRESOLVED_VALUES:
        raise _Invalid("unresolved_value", field)


def _slug(value: Any, field: str) -> None:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise _Invalid("invalid_slug", field)


def _sha(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise _Invalid("invalid_sha256", field)


def _hex40(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise _Invalid("invalid_revision", field)


def _version(value: Any, field: str) -> None:
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise _Invalid("invalid_version", field)


def _safe_relative(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise _Invalid("unsafe_path", field)
    if value.startswith("/") or "\\" in value or ":" in value:
        raise _Invalid("unsafe_path", field)
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise _Invalid("unsafe_path", field)


def _bounded_int(value: Any, low: int, high: int, field: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _Invalid("invalid_integer", field)
    if value < low or value > high:
        raise _Invalid("out_of_range", field)


def _boolean(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise _Invalid("invalid_boolean", field)


def _list(value: Any, field: str, low: int, high: int) -> list:
    if not isinstance(value, list):
        raise _Invalid("not_list", field)
    if len(value) < low:
        raise _Invalid("missing_required_value", field)
    if len(value) > high:
        raise _Invalid("out_of_range", field)
    return value


def _sorted_unique(items: list[dict], key: str, field: str) -> None:
    keys = [item[key] for item in items]
    if len(set(keys)) != len(keys):
        raise _Invalid("duplicate_value", field)
    if keys != sorted(keys):
        raise _Invalid("noncanonical_order", field)


def _reject(code: str, field: str = "") -> dict:
    return {"status": "rejected", "code": code, "field": field}


def _accept(checks: int) -> dict:
    return {"status": "accepted", "checks": checks, "qualifies": False}


def _require_true_map(document: Any, keys: tuple[str, ...],
                      prefix: str) -> int:
    value = _exact_object(document, keys, prefix)
    checks = 0
    for name in keys:
        _boolean(value[name], prefix + "." + name)
        if not value[name]:
            code = "rights_not_cleared" if prefix == "rights" else \
                "missing_required_value"
            raise _Invalid(code, prefix + "." + name)
        checks += 1
    return checks


def validate_manifest(document: Any) -> dict:
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object", "")
    try:
        assert_no_float(document)
    except ValueError:
        return _reject("float_not_allowed", "")
    try:
        _exact_object(document, MANIFEST_TOP_KEYS, "")
        checks += 1
        if document["schema_id"] != MANIFEST_SCHEMA_ID:
            raise _Invalid("invalid_schema_id", "schema_id")
        checks += 1
        _slug(document["manifest_id"], "manifest_id")
        checks += 1

        source = _exact_object(document["source"], SOURCE_KEYS, "source")
        if source["repository"] != UPSTREAM_REPOSITORY:
            raise _Invalid("invalid_repository", "source.repository")
        _hex40(source["revision"], "source.revision")
        _text(source["license_spdx"], "source.license_spdx", 80)
        _sha(source["license_sha256"], "source.license_sha256")
        _sha(source["tree_sha256"], "source.tree_sha256")
        checks += 6

        checkpoint = _exact_object(document["checkpoint"], CHECKPOINT_KEYS,
                                   "checkpoint")
        _slug(checkpoint["variant"], "checkpoint.variant")
        _safe_relative(checkpoint["filename"], "checkpoint.filename")
        _hex40(checkpoint["revision"], "checkpoint.revision")
        _bounded_int(checkpoint["byte_count"], 1, MAX_CHECKPOINT_BYTES,
                     "checkpoint.byte_count")
        _sha(checkpoint["sha256"], "checkpoint.sha256")
        _sha(checkpoint["terms_sha256"], "checkpoint.terms_sha256")
        _text(checkpoint["license_spdx"], "checkpoint.license_spdx", 80)
        _safe_relative(checkpoint["inference_script_path"],
                       "checkpoint.inference_script_path")
        _sha(checkpoint["inference_script_sha256"],
             "checkpoint.inference_script_sha256")
        _safe_relative(checkpoint["config_path"], "checkpoint.config_path")
        _sha(checkpoint["config_sha256"], "checkpoint.config_sha256")
        _sha(checkpoint["manifest_sha256"], "checkpoint.manifest_sha256")
        checks += 13

        runtime = _exact_object(document["runtime"], RUNTIME_KEYS, "runtime")
        if runtime["python_version"] != REQUIRED_INTERPRETER:
            raise _Invalid("wrong_python_version", "runtime.python_version")
        _text(runtime["framework"], "runtime.framework", 120)
        _version(runtime["framework_version"], "runtime.framework_version")
        _text(runtime["device"], "runtime.device", 120)
        _sha(runtime["lock_sha256"], "runtime.lock_sha256")
        _boolean(runtime["offline_load"], "runtime.offline_load")
        _boolean(runtime["deterministic"], "runtime.deterministic")
        packages = _list(runtime["packages"], "runtime.packages", 1,
                         MAX_PACKAGES)
        for index, item in enumerate(packages):
            prefix = "runtime.packages[" + str(index) + "]"
            _exact_object(item, ("name", "version"), prefix)
            _text(item["name"], prefix + ".name", 120)
            _text(item["version"], prefix + ".version", 120)
            checks += 2
        _sorted_unique(packages, "name", "runtime.packages")
        checks += 9
        if not runtime["offline_load"]:
            raise _Invalid("non_offline_runtime", "runtime.offline_load")
        if not runtime["deterministic"]:
            raise _Invalid("nondeterministic_runtime", "runtime.deterministic")

        geometry = _exact_object(document["geometry"], GEOMETRY_KEYS,
                                 "geometry")
        if geometry["mode"] != CALLER_MODE:
            raise _Invalid("scope_mismatch", "geometry.mode")
        _bounded_int(geometry["channels"], 1, 32, "geometry.channels")
        if geometry["channels"] != REPORTED_CHANNELS:
            raise _Invalid("invalid_channels", "geometry.channels")
        _bounded_int(geometry["sample_rate_hz"], 8000, 192000,
                     "geometry.sample_rate_hz")
        if geometry["sample_rate_hz"] != REPORTED_SAMPLE_RATE_HZ:
            raise _Invalid("invalid_sample_rate", "geometry.sample_rate_hz")
        _bounded_int(geometry["frame_samples"], 1, 65536,
                     "geometry.frame_samples")
        _bounded_int(geometry["hop_samples"], 1, 65536,
                     "geometry.hop_samples")
        if geometry["hop_samples"] > geometry["frame_samples"]:
            raise _Invalid("hop_exceeds_frame", "geometry.hop_samples")
        if geometry["sample_format"] != "f32":
            raise _Invalid("invalid_sample_format", "geometry.sample_format")
        _bounded_int(geometry["stft_window_samples"], 1, 65536,
                     "geometry.stft_window_samples")
        _bounded_int(geometry["lookahead_samples"], 0, 65536,
                     "geometry.lookahead_samples")
        if geometry["lookahead_samples"] != 0:
            raise _Invalid("streaming_lookahead_not_allowed",
                           "geometry.lookahead_samples")
        _text(geometry["phase_branch"], "geometry.phase_branch", 80)
        if geometry["phase_branch"] != "explicit_phase":
            raise _Invalid("phase_branch_required", "geometry.phase_branch")
        _boolean(geometry["whole_utterance"], "geometry.whole_utterance")
        _boolean(geometry["state_reset"], "geometry.state_reset")
        checks += 13
        if not geometry["whole_utterance"]:
            raise _Invalid("not_offline_whole_utterance",
                           "geometry.whole_utterance")
        if not geometry["state_reset"]:
            raise _Invalid("missing_state_reset", "geometry.state_reset")

        payload = _exact_object(document["input"], INPUT_KEYS, "input")
        _slug(payload["corpus_id"], "input.corpus_id")
        if payload["split"] not in ("dev", "test", "heldout"):
            raise _Invalid("invalid_split", "input.split")
        _bounded_int(payload["pair_count"], 1, MAX_PAIRS, "input.pair_count")
        _bounded_int(payload["channels"], 1, 32, "input.channels")
        if payload["channels"] != REPORTED_CHANNELS:
            raise _Invalid("invalid_channels", "input.channels")
        _bounded_int(payload["sample_rate_hz"], 8000, 192000,
                     "input.sample_rate_hz")
        if payload["sample_rate_hz"] != geometry["sample_rate_hz"]:
            raise _Invalid("rate_mismatch", "input.sample_rate_hz")
        _boolean(payload["clean_reference"], "input.clean_reference")
        _boolean(payload["consent"], "input.consent")
        _sha(payload["rights_sha256"], "input.rights_sha256")
        checks += 9
        if not payload["clean_reference"]:
            raise _Invalid("clean_reference_not_permitted",
                           "input.clean_reference")
        if not payload["consent"]:
            raise _Invalid("rights_not_cleared", "input.consent")

        checks += _require_true_map(document["controls"], CONTROL_KEYS,
                                    "controls")
        rights = _exact_object(document["rights"], RIGHTS_KEYS, "rights")
        checks += 1
        for name in RIGHTS_KEYS[:-1]:
            _boolean(rights[name], "rights." + name)
            if not rights[name]:
                raise _Invalid("rights_not_cleared", "rights." + name)
            checks += 1
        _text(rights["review_reference"], "rights.review_reference", 240)
        checks += 1
    except _Invalid as error:
        return _reject(error.code, error.field)
    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "mp-senet-synthetic-schema-control",
        "source": {
            "repository": UPSTREAM_REPOSITORY,
            "revision": "0" * 40,
            "license_spdx": "Apache-2.0",
            "license_sha256": "1" * 64,
            "tree_sha256": "2" * 64,
        },
        "checkpoint": {
            "variant": RECORDED_CHECKPOINT_VARIANT,
            "filename": "synthetic/checkpoint.pth",
            "revision": "0" * 40,
            "byte_count": 1024,
            "sha256": "3" * 64,
            "terms_sha256": "5" * 64,
            "license_spdx": "MIT",
            "inference_script_path": "synthetic/inference.py",
            "inference_script_sha256": "4" * 64,
            "config_path": "synthetic/config.yaml",
            "config_sha256": "6" * 64,
            "manifest_sha256": "8" * 64,
        },
        "runtime": {
            "python_version": "3.12.16",
            "framework": "synthetic-framework",
            "framework_version": "1.0.0",
            "device": "synthetic-cpu-control",
            "lock_sha256": "9" * 64,
            "offline_load": True,
            "deterministic": True,
            "packages": [{"name": "synthetic-runtime", "version": "1.0.0"}],
        },
        "geometry": {
            "mode": CALLER_MODE,
            "channels": 1,
            "sample_rate_hz": 16000,
            "frame_samples": 320,
            "hop_samples": 160,
            "sample_format": "f32",
            "stft_window_samples": 512,
            "lookahead_samples": 0,
            "phase_branch": "explicit_phase",
            "whole_utterance": True,
            "state_reset": True,
        },
        "input": {
            "corpus_id": "synthetic-schema-control",
            "split": "dev",
            "pair_count": 1,
            "channels": 1,
            "sample_rate_hz": 16000,
            "clean_reference": True,
            "consent": True,
            "rights_sha256": "a" * 64,
        },
        "controls": {name: True for name in CONTROL_KEYS},
        "rights": {
            **{name: True for name in RIGHTS_KEYS[:-1]},
            "review_reference": "synthetic-schema-control-no-review",
        },
    }


def _mutation_case(case_id: str, mutate: Any, code: str) -> dict:
    manifest = _manifest_control()
    mutate(manifest)
    result = validate_manifest(manifest)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("mutation_case_did_not_reject:" + case_id + ":" +
                         str(result))
    return _case_row(case_id, result, True)


def _raw_case(case_id: str, raw: str, code: str) -> dict:
    try:
        loads_strict(raw)
    except ValueError as error:
        observed = str(error).split(":", 1)[0]
        if observed != code:
            raise ValueError("raw_case_code_mismatch:" + case_id + ":" +
                             observed) from error
        return _case_row(case_id, _reject(observed), True)
    raise ValueError("raw_case_did_not_reject:" + case_id)


def _case_row(case_id: str, result: dict, synthetic: bool,
              accepted: bool = False) -> dict:
    return {
        "id": case_id,
        "status": "accepted" if accepted else result["status"],
        "code": "none" if accepted else result.get("code", ""),
        "field": "" if accepted else result.get("field", ""),
        "qualifies": False,
        "state_unchanged": not accepted,
        "synthetic_schema_control": synthetic,
    }


def admission_controls() -> dict:
    accepted = _case_row("accepted-schema-control",
                         validate_manifest(_manifest_control()), True,
                         accepted=True)
    cases = [accepted]
    cases.append(_case_row("root-list",
                           validate_manifest(["not", "a", "manifest"]),
                           True))
    cases.append(_case_row("root-null", validate_manifest(None), True))
    cases.append(_raw_case(
        "duplicate-json-key",
        '{"schema_id":"audio-sdk/mp-senet-caller-asset/0.1",'
        '"schema_id":"duplicate"}',
        "duplicate_json_key"))
    cases.append(_raw_case(
        "nonfinite-nan",
        '{"schema_id":"audio-sdk/mp-senet-caller-asset/0.1","value":NaN}',
        "nonfinite_json"))
    cases.append(_raw_case(
        "nonfinite-infinity",
        '{"schema_id":"audio-sdk/mp-senet-caller-asset/0.1",'
        '"value":Infinity}',
        "nonfinite_json"))
    cases.append(_mutation_case(
        "float-value", lambda m: m["geometry"].update(
            {"lookahead_samples": 200.0}), "float_not_allowed"))
    cases.append(_mutation_case(
        "missing-source", lambda m: m.pop("source"), "missing_field"))
    cases.append(_mutation_case(
        "unknown-top-key", lambda m: m.update({"extra": True}),
        "unknown_field"))
    cases.append(_mutation_case(
        "unknown-geometry-key",
        lambda m: m["geometry"].update({"extra": 1}), "unknown_field"))
    cases.append(_mutation_case(
        "invalid-source-repository",
        lambda m: m["source"].update({"repository": "https://example.invalid"}),
        "invalid_repository"))
    cases.append(_mutation_case(
        "invalid-source-revision",
        lambda m: m["source"].update({"revision": "abc"}),
        "invalid_revision"))
    cases.append(_mutation_case(
        "unresolved-source-license",
        lambda m: m["source"].update({"license_spdx": "NOASSERTION"}),
        "unresolved_value"))
    cases.append(_mutation_case(
        "invalid-license-sha",
        lambda m: m["source"].update({"license_sha256": "xyz"}),
        "invalid_sha256"))
    cases.append(_mutation_case(
        "missing-checkpoint", lambda m: m.pop("checkpoint"),
        "missing_field"))
    cases.append(_mutation_case(
        "traversal-checkpoint-path",
        lambda m: m["checkpoint"].update({"filename": "../checkpoint.pth"}),
        "unsafe_path"))
    cases.append(_mutation_case(
        "unsafe-inference-script-path",
        lambda m: m["checkpoint"].update(
            {"inference_script_path": "/abs/inference.py"}),
        "unsafe_path"))
    cases.append(_mutation_case(
        "boolean-byte-count",
        lambda m: m["checkpoint"].update({"byte_count": True}),
        "invalid_integer"))
    cases.append(_mutation_case(
        "zero-byte-count",
        lambda m: m["checkpoint"].update({"byte_count": 0}),
        "out_of_range"))
    cases.append(_mutation_case(
        "invalid-checkpoint-sha",
        lambda m: m["checkpoint"].update({"sha256": "nothex"}),
        "invalid_sha256"))
    cases.append(_mutation_case(
        "missing-config-sha",
        lambda m: m["checkpoint"].pop("config_sha256"), "missing_field"))
    cases.append(_mutation_case(
        "unsafe-config-path",
        lambda m: m["checkpoint"].update({"config_path": "/abs/config.yaml"}),
        "unsafe_path"))
    cases.append(_mutation_case(
        "wrong-python-version",
        lambda m: m["runtime"].update({"python_version": "3.11.0"}),
        "wrong_python_version"))
    cases.append(_mutation_case(
        "non-offline-runtime",
        lambda m: m["runtime"].update({"offline_load": False}),
        "non_offline_runtime"))
    cases.append(_mutation_case(
        "nondeterministic-runtime",
        lambda m: m["runtime"].update({"deterministic": False}),
        "nondeterministic_runtime"))
    cases.append(_mutation_case(
        "empty-runtime-packages",
        lambda m: m["runtime"].update({"packages": []}),
        "missing_required_value"))
    cases.append(_mutation_case(
        "duplicate-package-name",
        lambda m: m["runtime"]["packages"].append(
            {"name": "synthetic-runtime", "version": "1.0.1"}),
        "duplicate_value"))
    cases.append(_mutation_case(
        "unsorted-packages",
        lambda m: m["runtime"]["packages"].append(
            {"name": "aaa-runtime", "version": "1.0.0"}),
        "noncanonical_order"))
    cases.append(_mutation_case(
        "stereo-geometry",
        lambda m: m["geometry"].update({"channels": 2}),
        "invalid_channels"))
    cases.append(_mutation_case(
        "wrong-sample-rate",
        lambda m: m["geometry"].update({"sample_rate_hz": 48000}),
        "invalid_sample_rate"))
    cases.append(_mutation_case(
        "integer-sample-format",
        lambda m: m["geometry"].update({"sample_format": "s16"}),
        "invalid_sample_format"))
    cases.append(_mutation_case(
        "hop-exceeds-frame",
        lambda m: m["geometry"].update({"hop_samples": 640}),
        "hop_exceeds_frame"))
    cases.append(_mutation_case(
        "negative-lookahead",
        lambda m: m["geometry"].update({"lookahead_samples": -1}),
        "out_of_range"))
    cases.append(_mutation_case(
        "streaming-lookahead-scope",
        lambda m: m["geometry"].update({"lookahead_samples": 200}),
        "streaming_lookahead_not_allowed"))
    cases.append(_mutation_case(
        "streaming-mode-scope",
        lambda m: m["geometry"].update({"mode": "streaming_lookahead"}),
        "scope_mismatch"))
    cases.append(_mutation_case(
        "missing-phase-branch",
        lambda m: m["geometry"].update({"phase_branch": "magnitude_only"}),
        "phase_branch_required"))
    cases.append(_mutation_case(
        "not-whole-utterance",
        lambda m: m["geometry"].update({"whole_utterance": False}),
        "not_offline_whole_utterance"))
    cases.append(_mutation_case(
        "missing-state-reset",
        lambda m: m["geometry"].update({"state_reset": False}),
        "missing_state_reset"))
    cases.append(_mutation_case(
        "invalid-corpus-split",
        lambda m: m["input"].update({"split": "train"}), "invalid_split"))
    cases.append(_mutation_case(
        "zero-pair-count",
        lambda m: m["input"].update({"pair_count": 0}), "out_of_range"))
    cases.append(_mutation_case(
        "input-rate-mismatch",
        lambda m: m["input"].update({"sample_rate_hz": 48000}),
        "rate_mismatch"))
    cases.append(_mutation_case(
        "missing-clean-reference",
        lambda m: m["input"].update({"clean_reference": False}),
        "clean_reference_not_permitted"))
    cases.append(_mutation_case(
        "unconsented-input",
        lambda m: m["input"].update({"consent": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "missing-control",
        lambda m: m["controls"].pop("identity_passthrough"),
        "missing_field"))
    cases.append(_mutation_case(
        "false-control",
        lambda m: m["controls"].update({"task_matched_baseline": False}),
        "missing_required_value"))
    cases.append(_mutation_case(
        "missing-right",
        lambda m: m["rights"].pop("output_use"), "missing_field"))
    cases.append(_mutation_case(
        "false-right",
        lambda m: m["rights"].update({"redistribution": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "unresolved-review-reference",
        lambda m: m["rights"].update({"review_reference": "unknown"}),
        "unresolved_value"))

    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted_cases = [case for case in cases if case["status"] == "accepted"]
    return {
        "cases": cases,
        "controls": admission_contract_block(),
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(rejected),
            "accepted_schema_controls": len(accepted_cases),
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "accepted_control_qualifies": False,
            "all_adverse_cases_rejected": len(rejected) == len(cases) - len(
                accepted_cases),
            "runtime_invoked": False,
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
    }


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "contract_id": "audio-sdk/mp-senet-caller-asset-contract/0.1",
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "source_fields": list(SOURCE_KEYS),
        "checkpoint_fields": list(CHECKPOINT_KEYS),
        "runtime_fields": list(RUNTIME_KEYS),
        "geometry_fields": list(GEOMETRY_KEYS),
        "input_fields": list(INPUT_KEYS),
        "control_keys": list(CONTROL_KEYS),
        "right_keys": list(RIGHTS_KEYS),
        "exact_interpreter": REQUIRED_INTERPRETER,
        "required_channels": REPORTED_CHANNELS,
        "required_sample_rate_hz": REPORTED_SAMPLE_RATE_HZ,
        "required_mode": CALLER_MODE,
        "required_phase_branch": "explicit_phase",
        "required_whole_utterance": True,
        "required_lookahead_samples": 0,
        "max_checkpoint_bytes": MAX_CHECKPOINT_BYTES,
        "max_pairs": MAX_PAIRS,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "runtime_or_weights_invoked": False,
        "manifest_validation_only": True,
    }


# ---------------------------------------------------------------------------
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "task_geometry": task_geometry(),
        "upstream_record": upstream_record(),
        "recorded_identity": recorded_identity_block(),
        "reported_metrics": reported_metrics_block(),
        "asset_registry": asset_registry(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "enhancement_profile": enhancement_profile_block(),
        "rights_gap": rights_gap(),
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "board_row_projection": projection,
        "board_row_sha256": board_row_digest(projection),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "admission_contract": admission_contract_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "local_files": list(LOCAL_FILES),
        "non_claims": list(NON_CLAIMS),
        "write_scope": WRITE_SCOPE,
        "qualification": qualification_block(),
    }


def build_report() -> dict:
    contract = build_contract()
    probes = all_probes()
    summary = absence_summary(probes)
    if summary["present_count"] != 0:
        raise ValueError("absence_probe_present_reopen_required")
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "component_id": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "task_geometry": task_geometry(),
        "upstream_record": upstream_record(),
        "recorded_identity": recorded_identity_block(),
        "reported_metrics": reported_metrics_block(),
        "asset_registry": asset_registry(),
        "evidence_inputs": evidence_inputs(),
        "absence_evidence": {
            "workspace_probes": workspace_probes(),
            "worktree_probes": worktree_probes(),
            "home_probes": home_probes(),
            "summary": summary,
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": [row["id"] for row in release_gates()],
        "linked_row_identity": linked_identity_block(),
        "enhancement_profile": enhancement_profile_block(),
        "enhancement_profile_requirements":
            [dict(row) for row in ENHANCEMENT_REQUIREMENTS],
        "qualification": qualification_block(),
        "historical_evidence": [dict(row) for row in HISTORICAL_EVIDENCE],
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": REQUIRED_INTERPRETER,
            "standard_library_only": True,
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                "test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            ],
        },
        "write_scope": WRITE_SCOPE,
    }


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    expected = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise ValueError("contract_field_mismatch:" + key)
    if contract.get("proposal_only") is not True \
            or contract.get("incomplete") is not True:
        raise ValueError("contract_disposition_flags")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    if contract.get("source_pins") != SOURCE_PINS:
        raise ValueError("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != BOUNDARY_PINS:
        raise ValueError("contract_boundary_pins_mismatch")
    if contract.get("local_files") != list(LOCAL_FILES):
        raise ValueError("contract_local_files_mismatch")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, row in enumerate(gates, 1):
        if row.get("id") != "RG-%02d" % index:
            raise ValueError("contract_gate_id")
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if row.get("linked_row") != TASK:
            raise ValueError("contract_gate_link")
    blockers = contract.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 7:
        raise ValueError("contract_artifact_count")
    for row in artifacts:
        if row.get("present") is not False or row.get("verified") is not False \
                or row.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
    qualification = contract.get("qualification", {})
    if qualification.get("status") != QUALIFICATION_STATUS \
            or qualification.get("all_release_gates_blocked") is not True:
        raise ValueError("contract_qualification_invalid")
    recorded = contract.get("recorded_identity", {})
    if recorded.get("status") != \
            "no_checkpoint_identity_recorded_in_merged_evidence":
        raise ValueError("contract_recorded_identity_status")
    if recorded.get("locally_verified") is not False \
            or recorded.get("admitted_as_result") is not False \
            or recorded.get("qualifies") is not False:
        raise ValueError("contract_recorded_identity_promoted")
    if recorded.get("checkpoint_bytes") is not None \
            or recorded.get("checkpoint_sha256") is not None \
            or recorded.get("checkpoint_path") is not None:
        raise ValueError("contract_recorded_identity_invented")
    assert_no_float(contract)


# ---------------------------------------------------------------------------
# Task-local git scope. The base is the newest merge-base between HEAD and the
# available PR base refs, not a fixed historical commit. This keeps later
# sibling merges out of the comparison while still failing closed on any edit
# outside TASK_PREFIX.
# ---------------------------------------------------------------------------

SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref."""
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
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]
