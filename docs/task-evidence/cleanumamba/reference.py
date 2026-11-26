# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-CLEANUMAMBA.

Standard-library only and deterministic. This module never clones, downloads,
copies, imports, builds or executes the upstream CleanUMamba source, a
checkpoint, a Mamba runtime or audio. It pins the publicly observable upstream
commit/tree and the Git blob SHA-1 identity of every repository file at that
commit, records the exact licensing and runtime blockers, and reproduces only
declared metadata, manifest-schema, checkpoint-ledger, geometry and frame
arithmetic controls.

The candidate cannot be admitted: the official repository has no LICENSE file
at the pinned commit (the GitHub license field is null and LICENSE returns 404),
and no checkpoint-specific terms, published checkpoint SHA-256, CPU runtime or
matched cohort exists. Every result is non-qualifying. Nothing here is a
runtime, quality, latency, benchmark or release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Callable

TASK = "SDK-CLEANUMAMBA"
COMPONENT_ID = "cleanumamba"
TASK_TITLE = "CleanUMamba"
CONTRACT_ID = "audio-sdk/cleanumamba/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
OBSERVATION_SCHEMA_ID = "audio-sdk/cleanumamba/upstream-observation/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/cleanumamba/caller-supplied-asset/0.1"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
MODE = "feasibility"
BASE_COMMIT = "d45e0f22883021412b4206c77df4e1d8cf89dbd5"
BRANCH = "swarm/SDK-CLEANUMAMBA"
REVIEWER = "reviewer-CLEANUMAMBA"
TASK_PREFIX = "docs/task-evidence/cleanumamba/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component", "evidence")

UPSTREAM_REPOSITORY = "https://github.com/lab-emi/CleanUMamba"
UPSTREAM_HEAD = "d5810219a534116df1d2e03eaacd517b7ec0a2fa"
UPSTREAM_TREE = "8e9abac4d880a673d249bbb6de0999566138a1f9"
UPSTREAM_COMMIT_DATE = "2025-06-12T06:20:39Z"
UPSTREAM_COMMIT_SIGNATURE = "unsigned"
UPSTREAM_OBSERVED_AT = "2026-11-26"
UPSTREAM_LICENSE_METADATA = None
UPSTREAM_LICENSE_HTTP_STATUS = 404
UPSTREAM_README_SHA256 = (
    "a2728b41258a1683b7910b1e04a1fa02100f7dc15e25ce59610a44da14bf2db0")
UPSTREAM_README_GIT_BLOB_SHA1 = (
    "7b94c2d32b96523af42dea3845d0c1bb274264c5")
UPSTREAM_README_BYTES = 14550

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(
    os.environ.get("AUDIOML_ROOT", str(WORKTREE.parents[2]))).resolve()

SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/agent-cleanumamba-eval/REPORT.md":
        "381029c5e50aff2916b6eb15b021f5fe923f7807ba71dab7dbebab65896b9cc2",
    "research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md":
        "c00e26847c119928f068cb5da00ba88106a2d977b67bf8b325ec27093eca8f4e",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

BOUNDARY_PINS: dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

SIBLING_PINS: dict[str, str] = {
    "docs/task-evidence/clearvoice-frcrn-16khz/report.json":
        "a1c41721ba3866ae4bec22d71494ff235699c2887f10d813cdd834e0a97f8aba",
    "docs/task-evidence/dpdfnet-2-streaming/report.json":
        "8c9f651f00e26b4be550fd53585cda94d68a4f2903ccfdff94440891ae9a8101",
    "docs/task-evidence/gtcrn-dns3-offline/report.json":
        "b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd",
    "docs/task-evidence/rt-semamba-kd1/report.json":
        "81872b32223f6100c20c9e66e992baa6e4938fe52c01292d86360268f9c29283",
}

LOCAL_PIN_FILES = (
    "README.md",
    "SOURCES.sha256.license",
    "UPSTREAM_MANIFEST.json",
    "UPSTREAM_MANIFEST.json.license",
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

ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
FORBIDDEN_SUFFIXES = frozenset({
    ".bin", ".dylib", ".gguf", ".h5", ".hdf5", ".m4a", ".mlmodel", ".mp3",
    ".mp4", ".npy", ".npz", ".onnx", ".otf", ".pkl", ".pt", ".pth", ".safetensors",
    ".so", ".tar", ".tgz", ".ttf", ".wav", ".whl", ".zip"})

README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: end -->"),
    "upstream": ("<!-- digest-table: upstream -->", "<!-- digest-table: end -->"),
    "artifacts": ("<!-- digest-table: artifacts -->",
                  "<!-- digest-table: end -->"),
}

PROFILE_PHRASES = (
    "identity/noisy control", "task-matched baseline", "SI-SDR", "STOI",
    "clean-speech preservation", "peaks", "invalid outputs", "unpaired speech",
    "listening", "alignment", "state", "memory",
    "content/availability timing")

MANIFEST_FIELDS = (
    "schema_id", "task", "source_repository", "source_commit", "source_tree_sha1",
    "checkpoint_path", "checkpoint_size_bytes", "checkpoint_git_blob_sha1",
    "checkpoint_sha256", "sample_rate_hz", "channels", "caller_attestation",
    "license_evidence")
LICENSE_FIELDS = ("status", "spdx", "terms_sha256")
SYNTHETIC_SHA256 = hashlib.sha256(
    b"SDK-CLEANUMAMBA synthetic schema control; no checkpoint bytes\n").hexdigest()

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_float(_text: str) -> Any:
    raise ValueError("non_integer_number")


def _reject_constant(text: str) -> Any:
    raise ValueError("nonfinite_constant:" + text)


def parse_strict_json_text(text: str) -> Any:
    try:
        value = json.loads(
            text, object_pairs_hook=_no_duplicates, parse_float=_reject_float,
            parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("malformed_json") from error
    _no_floats(value)
    return value


def read_strict_json(path: Path) -> Any:
    try:
        return parse_strict_json_text(path.read_text(encoding="utf-8"))
    except ValueError:
        raise
    except OSError as error:
        raise ValueError("read_failed") from error


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_value")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non_string_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_exact_keys(value: Any, fields: tuple[str, ...]) -> None:
    if not isinstance(value, dict):
        raise ValueError("invalid_type")
    if set(value) - set(fields):
        raise ValueError("unknown_field")
    for field in fields:
        if field not in value:
            raise ValueError("missing_field")


def _require_digest(value: Any, length: int, code: str) -> str:
    pattern = HEX64 if length == 64 else HEX40
    if not isinstance(value, str) or not pattern.match(value):
        raise ValueError(code)
    return value


def board_row_projection(path: Path) -> dict[str, Any]:
    data = read_strict_json(path)
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    for row in tasks:
        if isinstance(row, dict) and row.get("id") == TASK:
            return {field: row.get(field) for field in BOARD_ROW_FIELDS}
    raise ValueError("task_row_missing")


def load_upstream_manifest() -> dict[str, Any]:
    value = read_strict_json(HERE / "UPSTREAM_MANIFEST.json")
    _require_exact_keys(value, (
        "blob_count", "blobs", "commit", "commit_date", "commit_signature",
        "default_branch", "directory_count", "license_metadata_field",
        "license_path_http_status", "manifest_note", "observed_at",
        "readme_bytes", "readme_git_blob_sha1", "readme_sha256", "repository",
        "schema_id", "tree_entry_count", "tree_sha1"))
    if value["schema_id"] != OBSERVATION_SCHEMA_ID:
        raise ValueError("observation_schema")
    if value["repository"] != UPSTREAM_REPOSITORY:
        raise ValueError("observation_repository")
    if value["commit"] != UPSTREAM_HEAD:
        raise ValueError("observation_commit")
    if value["tree_sha1"] != UPSTREAM_TREE:
        raise ValueError("observation_tree")
    if value["commit_date"] != UPSTREAM_COMMIT_DATE:
        raise ValueError("observation_date")
    if value["commit_signature"] != UPSTREAM_COMMIT_SIGNATURE:
        raise ValueError("observation_signature")
    if value["readme_sha256"] != UPSTREAM_README_SHA256:
        raise ValueError("observation_readme_sha256")
    if value["readme_git_blob_sha1"] != UPSTREAM_README_GIT_BLOB_SHA1:
        raise ValueError("observation_readme_blob")
    if value["readme_bytes"] != UPSTREAM_README_BYTES:
        raise ValueError("observation_readme_bytes")
    if value["license_metadata_field"] is not None:
        raise ValueError("observation_license_field")
    if value["license_path_http_status"] != UPSTREAM_LICENSE_HTTP_STATUS:
        raise ValueError("observation_license_status")
    blobs = value["blobs"]
    if not isinstance(blobs, list) or len(blobs) != value["blob_count"]:
        raise ValueError("observation_blob_count")
    previous = ""
    seen: set[str] = set()
    for row in blobs:
        _require_exact_keys(row, ("bytes", "git_blob_sha1", "path"))
        path = row["path"]
        if not isinstance(path, str) or not SLUG.match(path):
            raise ValueError("observation_blob_path")
        if path in seen or path < previous:
            raise ValueError("observation_blob_order")
        seen.add(path)
        previous = path
        if not _is_int(row["bytes"]) or row["bytes"] < 0:
            raise ValueError("observation_blob_bytes")
        _require_digest(row["git_blob_sha1"], 40, "observation_blob_sha")
    if value["blob_count"] + value["directory_count"] != value["tree_entry_count"]:
        raise ValueError("observation_tree_arithmetic")
    return value


def _checkpoint_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in manifest["blobs"]:
        path = row["path"]
        if not path.startswith("checkpoints/") or not path.endswith(".pkl"):
            continue
        if "/experiments/" in path:
            family = "experiments"
        elif "-E6" in path:
            family = "E6"
        elif "-E8" in path:
            family = "E8"
        else:
            raise ValueError("checkpoint_family_unknown")
        rows.append({
            "path": path,
            "bytes": row["bytes"],
            "git_blob_sha1": row["git_blob_sha1"],
            "family": family,
            "present": False,
            "published_sha256": None,
            "licensed": False,
            "admitted": False,
            "qualifies": False,
        })
    rows.sort(key=lambda item: item["path"])
    return rows


def checkpoint_ledger_control() -> dict[str, Any]:
    manifest = load_upstream_manifest()
    rows = _checkpoint_rows(manifest)
    families = {"E6": 0, "E8": 0, "experiments": 0}
    for row in rows:
        families[row["family"]] += 1
    by_size: dict[int, list[str]] = {}
    for row in rows:
        by_size.setdefault(row["bytes"], []).append(row["path"])
    duplicate_sizes = [
        {"bytes": size, "paths": sorted(paths),
         "distinct_blob_shas":
             len({next(r["git_blob_sha1"] for r in rows if r["path"] == p)
                  for p in paths}) == len(paths)}
        for size, paths in sorted(by_size.items()) if len(paths) > 1]
    return {
        "evidence_class": "metadata_observation_not_runtime_evidence",
        "qualifies": False,
        "observer": "public GitHub tree metadata at the pinned commit",
        "manifest_entries": manifest["tree_entry_count"],
        "blob_entries": manifest["blob_count"],
        "directory_entries": manifest["directory_count"],
        "checkpoint_count": len(rows),
        "checkpoint_bytes": sum(row["bytes"] for row in rows),
        "family_counts": families,
        "all_checkpoints_have_git_blob_sha1": all(
            bool(HEX40.match(row["git_blob_sha1"])) for row in rows),
        "checkpoints_with_published_sha256": 0,
        "all_checkpoints_have_published_sha256": False,
        "license_metadata_field": manifest["license_metadata_field"],
        "license_path_http_status_observed":
            manifest["license_path_http_status"],
        "license_blob_present": any(
            row["path"].split("/")[-1] in {
                "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "NOTICE"}
            for row in manifest["blobs"]),
        "readme_license_badge_claimed": True,
        "readme_file_tree_lists_license": True,
        "license_claim_contradiction": True,
        "duplicate_size_pairs": duplicate_sizes,
        "checkpoint_rows": rows,
        "note": (
            "Git blob SHA-1 plus commit/tree is an exact content address, but "
            "the package publishes no checkpoint SHA-256, no checkpoint "
            "license and no caller-supplied bytes. No checkpoint was "
            "downloaded."),
    }


def upstream_observation() -> dict[str, Any]:
    manifest = load_upstream_manifest()
    rows = _checkpoint_rows(manifest)
    source_blobs = []
    wanted = (
        "README.md", "environment.yml", "configs/config.json",
        "configs/exp/models/DNS-CleanUMamba-3N-E6.json",
        "configs/exp/models/DNS-CleanUMamba-3N-E8.json",
        "src/examples/denoise.py", "src/examples/loading_pretrained_models.py",
        "src/examples/streaming_demo.py", "src/network/CleanUMamba.py",
        "src/network/network.py")
    by_path = {row["path"]: row for row in manifest["blobs"]}
    for path in wanted:
        if path not in by_path:
            raise ValueError("source_blob_missing:" + path)
        source_blobs.append({
            "path": path,
            "bytes": by_path[path]["bytes"],
            "git_blob_sha1": by_path[path]["git_blob_sha1"],
        })
    return {
        "repository": UPSTREAM_REPOSITORY,
        "default_branch": manifest["default_branch"],
        "observed_at": manifest["observed_at"],
        "observation_method": (
            "public GitHub repository metadata and raw text reads at the "
            "pinned commit; no clone, archive, checkpoint or weight download"),
        "head_commit": manifest["commit"],
        "commit_date": manifest["commit_date"],
        "commit_signature": manifest["commit_signature"],
        "root_tree_sha1": manifest["tree_sha1"],
        "tree_entry_count": manifest["tree_entry_count"],
        "blob_count": manifest["blob_count"],
        "directory_count": manifest["directory_count"],
        "readme_bytes": manifest["readme_bytes"],
        "readme_git_blob_sha1": manifest["readme_git_blob_sha1"],
        "readme_sha256": manifest["readme_sha256"],
        "license_metadata_field": manifest["license_metadata_field"],
        "license_path_http_status": manifest["license_path_http_status"],
        "license_blob_in_tree": any(
            row["path"].split("/")[-1] in {
                "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "NOTICE"}
            for row in manifest["blobs"]),
        "readme_license_badge": "MIT",
        "readme_license_badge_target": "LICENSE",
        "readme_file_tree_lists_license": True,
        "manifest_sha256": sha256_file(HERE / "UPSTREAM_MANIFEST.json"),
        "manifest_file": "UPSTREAM_MANIFEST.json",
        "source_blobs": source_blobs,
        "checkpoint_rows": rows,
        "declared_audio": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "float32",
            "input": "raw waveform",
            "training_crop_length_seconds": 10,
            "streaming_demo_chunk_samples": 4096,
            "streaming_demo_chunk_seconds": "256 ms",
            "e6_declared_lookahead_ms": 12,
            "e8_declared_lookahead_ms": 48,
            "source": "upstream README table, configs/config.json and "
                      "src/examples/streaming_demo.py at the pinned commit",
        },
        "declared_runtime": {
            "python": "3.11",
            "pytorch": "2.2.2",
            "cuda": "11.8",
            "mamba_ssm": "1.2.2",
            "causal_conv1d": "1.1.0",
            "platform": "Ubuntu 22 (README); streaming demo is the stated "
                        "platform exception",
            "loader_device": "cuda (src/examples/loading_pretrained_models.py "
                             "sets config['device']='cuda' and calls .cuda())",
            "cpu_path_verified": False,
            "environment_digest_present": False,
        },
        "source_reported_metrics": {
            "evidence_class": "source_reported_not_remeasured",
            "model": "Mamba (E8 pruned family; README comparison row)",
            "parameters": "442K",
            "macs": "468M",
            "pesq_wb": "2.42",
            "pesq_nb": "2.95",
            "stoi_percent": "95.1",
            "dataset": "DNS no-reverb test set",
            "qualifies": False,
        },
    }


def license_findings() -> dict[str, Any]:
    return {
        "repository_public": True,
        "license_metadata_field_present": False,
        "license_file_present_at_pinned_commit": False,
        "license_path_http_status_observed": 404,
        "readme_license_badge_claims_mit": True,
        "readme_file_tree_lists_license": True,
        "claim_is_a_badge_and_a_diagram_not_a_license_grant": True,
        "license_text_staged": False,
        "checkpoint_specific_terms_present": False,
        "training_data_statement_present": False,
        "redistribution_approved": False,
        "product_use_approved": False,
        "legal_review_present": False,
        "qualifies": False,
    }


def _base_manifest() -> dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "task": TASK,
        "source_repository": UPSTREAM_REPOSITORY,
        "source_commit": UPSTREAM_HEAD,
        "source_tree_sha1": UPSTREAM_TREE,
        "checkpoint_path":
            "checkpoints/pruned/CleanUMamba-3N-E8_pruned-5M.pkl",
        "checkpoint_size_bytes": 9744896,
        "checkpoint_git_blob_sha1":
            "f6ab36ccf56f6ac411178b36ca222f45ec04825f",
        "checkpoint_sha256": SYNTHETIC_SHA256,
        "sample_rate_hz": 16000,
        "channels": 1,
        "caller_attestation": False,
        "license_evidence": {
            "status": "absent",
            "spdx": None,
            "terms_sha256": None,
        },
    }


def validate_asset_manifest(value: Any) -> dict[str, Any]:
    _require_exact_keys(value, MANIFEST_FIELDS)
    if value["schema_id"] != MANIFEST_SCHEMA_ID:
        raise ValueError("schema_id_mismatch")
    if value["task"] != TASK:
        raise ValueError("task_mismatch")
    if value["source_repository"] != UPSTREAM_REPOSITORY:
        raise ValueError("repository_mismatch")
    if value["source_commit"] != UPSTREAM_HEAD:
        raise ValueError("source_commit_mismatch")
    if value["source_tree_sha1"] != UPSTREAM_TREE:
        raise ValueError("source_tree_mismatch")
    ledger = {row["path"]: row for row in
              _checkpoint_rows(load_upstream_manifest())}
    path = value["checkpoint_path"]
    if not isinstance(path, str) or path not in ledger:
        raise ValueError("checkpoint_unknown")
    row = ledger[path]
    if not _is_int(value["checkpoint_size_bytes"]):
        raise ValueError("checkpoint_size_not_integer")
    if value["checkpoint_size_bytes"] != row["bytes"]:
        raise ValueError("checkpoint_size_mismatch")
    if not isinstance(value["checkpoint_git_blob_sha1"], str) or \
            value["checkpoint_git_blob_sha1"] != row["git_blob_sha1"]:
        raise ValueError("checkpoint_blob_mismatch")
    _require_digest(value["checkpoint_sha256"], 64, "checkpoint_sha256_invalid")
    if not _is_int(value["sample_rate_hz"]):
        raise ValueError("sample_rate_not_integer")
    if value["sample_rate_hz"] != 16000:
        raise ValueError("sample_rate_mismatch")
    if not _is_int(value["channels"]):
        raise ValueError("channels_not_integer")
    if value["channels"] != 1:
        raise ValueError("channels_mismatch")
    if not isinstance(value["caller_attestation"], bool):
        raise ValueError("caller_attestation_not_bool")
    license_value = value["license_evidence"]
    if not isinstance(license_value, dict):
        raise ValueError("license_evidence_type")
    _require_exact_keys(license_value, LICENSE_FIELDS)
    status = license_value["status"]
    if status not in {"present", "absent"}:
        raise ValueError("license_status_invalid")
    if status == "absent":
        if license_value["spdx"] is not None or \
                license_value["terms_sha256"] is not None:
            raise ValueError("license_absent_fields")
        licensed = False
    else:
        spdx = license_value["spdx"]
        if not isinstance(spdx, str) or not spdx.strip():
            raise ValueError("license_spdx_missing")
        _require_digest(license_value["terms_sha256"], 64,
                        "license_terms_invalid")
        licensed = True
    attested = value["caller_attestation"]
    real_digest = value["checkpoint_sha256"] != SYNTHETIC_SHA256
    admissible = bool(licensed and attested and real_digest)
    return {
        "schema_valid": True,
        "licensed": licensed,
        "attested": attested,
        "checkpoint_digest_is_real_and_not_the_synthetic_control": real_digest,
        "admissible_for_intake": admissible,
        "admitted": False,
        "qualifies": False,
        "status": ("schema_valid_admissible_metadata_not_admitted" if admissible
                   else "schema_valid_not_admissible"),
    }


def _mutations() -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    def remove(key: str) -> Callable[[dict[str, Any]], None]:
        return lambda value: value.pop(key)

    def set_value(key: str, item: Any) -> Callable[[dict[str, Any]], None]:
        return lambda value: value.__setitem__(key, item)

    return [
        ("channels_mismatch", "channels_mismatch",
         set_value("channels", 2)),
        ("channels_string", "channels_not_integer",
         set_value("channels", "1")),
        ("checkpoint_blob_mismatch", "checkpoint_blob_mismatch",
         set_value("checkpoint_git_blob_sha1", "0" * 40)),
        ("checkpoint_size_bool", "checkpoint_size_not_integer",
         set_value("checkpoint_size_bytes", True)),
        ("checkpoint_size_mismatch", "checkpoint_size_mismatch",
         set_value("checkpoint_size_bytes", 1)),
        ("checkpoint_size_string", "checkpoint_size_not_integer",
         set_value("checkpoint_size_bytes", "9744896")),
        ("checkpoint_unknown", "checkpoint_unknown",
         set_value("checkpoint_path", "checkpoints/models/not-present.pkl")),
        ("commit_mismatch", "source_commit_mismatch",
         set_value("source_commit", "0" * 40)),
        ("commit_short", "source_commit_mismatch",
         set_value("source_commit", "d" * 39)),
        ("duplicate_json_key", "duplicate_json_key:schema_id", None),  # sentinel
        ("empty_object", "missing_field", lambda value: value.clear()),
        ("license_absent_with_spdx", "license_absent_fields",
         lambda value: value["license_evidence"].__setitem__("spdx", "MIT")),
        ("license_bad_status", "license_status_invalid",
         lambda value: value["license_evidence"].__setitem__(
             "status", "maybe")),
        ("license_missing_field", "missing_field",
         lambda value: value["license_evidence"].pop("status")),
        ("license_not_object", "license_evidence_type",
         set_value("license_evidence", None)),
        ("license_present_bad_terms", "license_terms_invalid",
         lambda value: value["license_evidence"].update(
             {"status": "present", "spdx": "MIT", "terms_sha256": "x"})),
        ("license_present_no_spdx", "license_spdx_missing",
         lambda value: value["license_evidence"].update(
             {"status": "present", "spdx": None,
              "terms_sha256": "0" * 64})),
        ("malformed_json", "malformed_json", None),  # sentinel
        ("missing_schema", "missing_field", remove("schema_id")),
        ("repository_mismatch", "repository_mismatch",
         set_value("source_repository", "https://github.com/other/repo")),
        ("root_array", "invalid_type", None),  # sentinel
        ("sample_rate_mismatch", "sample_rate_mismatch",
         set_value("sample_rate_hz", 48000)),
        ("sample_rate_string", "sample_rate_not_integer",
         set_value("sample_rate_hz", "16000")),
        ("schema_mismatch", "schema_id_mismatch",
         set_value("schema_id", "audio-sdk/cleanumamba/other/0.1")),
        ("sha_nonhex", "checkpoint_sha256_invalid",
         set_value("checkpoint_sha256", "z" * 64)),
        ("sha_short", "checkpoint_sha256_invalid",
         set_value("checkpoint_sha256", "abc")),
        ("task_mismatch", "task_mismatch", set_value("task", "SDK-OTHER")),
        ("tree_mismatch", "source_tree_mismatch",
         set_value("source_tree_sha1", "0" * 40)),
        ("unknown_field", "unknown_field",
         set_value("note", "not part of the schema")),
        ("attestation_string", "caller_attestation_not_bool",
         set_value("caller_attestation", "true")),
    ]


def _run_rejection_case(case_id: str, expected: str, mutator: Any) -> dict:
    observed = None
    state_unchanged = True
    try:
        if case_id == "duplicate_json_key":
            base = canonical_bytes(_base_manifest()).decode("ascii")
            duplicate = base.replace(
                '"schema_id":', '"schema_id":"x","schema_id":', 1)
            parse_strict_json_text(duplicate)
        elif case_id == "malformed_json":
            parse_strict_json_text("{")
        elif case_id == "root_array":
            validate_asset_manifest([])
        else:
            value = json.loads(canonical_bytes(_base_manifest()))
            mutator(value)
            validate_asset_manifest(value)
    except ValueError as error:
        observed = str(error)
    return {
        "id": case_id,
        "expected_code": expected,
        "observed_code": observed,
        "status": "rejected" if observed == expected else "unexpected_result",
        "state_unchanged": state_unchanged,
        "qualifies": False,
    }


def manifest_control() -> dict[str, Any]:
    control = validate_asset_manifest(_base_manifest())
    cases = [_run_rejection_case(*case) for case in _mutations()]
    cases.sort(key=lambda item: item["id"])
    rejected = sum(1 for case in cases if case["status"] == "rejected")
    return {
        "control_id": MANIFEST_SCHEMA_ID,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "qualifies": False,
        "purpose": (
            "Fail-closed validation of a caller-supplied asset manifest. It "
            "models metadata admission only: no asset is loaded, opened, "
            "hashed from bytes or executed, and no manifest is supplied here."),
        "control": {
            **control,
            "synthetic_checkpoint_sha256": SYNTHETIC_SHA256,
            "note": "The control digest is a hash of a synthetic note, not a "
                    "checkpoint digest.",
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": rejected,
            "accepted_schema_controls": 1,
            "admitted_count": 0,
            "qualifying_results": 0,
            "all_codes_match": rejected == len(cases),
            "state_advanced_on_rejection": False,
            "asset_loaded": False,
            "asset_executed": False,
            "network_used": False,
            "audio_read": False,
        },
    }


def geometry_control() -> dict[str, Any]:
    return {
        "evidence_class": "declared_arithmetic_control_not_measurement",
        "qualifies": False,
        "sdk_v0": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "f32",
            "frame_ns": 10000000,
        },
        "candidate_declared": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "float32",
            "input": "raw waveform",
            "e6_lookahead_ms": 12,
            "e8_lookahead_ms": 48,
            "streaming_demo_chunk_samples": 4096,
            "source": "upstream README, configs/config.json and "
                      "src/examples/streaming_demo.py; not verified by execution",
        },
        "arithmetic": {
            "e6_lookahead_samples": 192,
            "e8_lookahead_samples": 768,
            "sdk_frame_ms": 10,
            "demo_chunk_samples": 4096,
            "demo_chunk_ms": 256,
            "demo_chunk_mod_frame_samples": 96,
            "demo_chunk_frames": "25.6",
            "e6_lookahead_mod_frame_samples": 32,
            "e8_lookahead_mod_frame_samples": 128,
        },
        "checks": {
            "sample_rate_match": True,
            "channels_match": True,
            "exact_16k_integer_millisecond_lookahead": True,
            "v0_frame_aligned_chunk": False,
            "v0_frame_aligned_lookahead": False,
            "requires_rechunking_or_rebasing": True,
            "lookahead_measured": False,
            "device_timing_measured": False,
        },
        "note": (
            "16 kHz mono matches installed v0, but neither the 4096-sample demo "
            "chunk nor the declared 12/48 ms lookahead is aligned to the v0 "
            "160-sample frame. Alignment, state and latency are unmeasured."),
    }


def _validate_frame(value: Any) -> str:
    if not isinstance(value, list):
        return "invalid_type"
    if len(value) != 160:
        return "wrong_length"
    for sample in value:
        if isinstance(sample, bool) or not isinstance(sample, int):
            if isinstance(sample, float) and not math.isfinite(sample):
                return "nonfinite"
            return "non_integer"
        if sample < -1000 or sample > 1000:
            return "out_of_range"
    return "accepted"


def frame_control() -> dict[str, Any]:
    silent = [0] * 160
    ramp = [((index * 13) % 2001) - 1000 for index in range(160)]
    cases = [
        ("valid_ramp", ramp, "accepted"),
        ("valid_silence", silent, "accepted"),
        ("too_long", [0] * 161, "wrong_length"),
        ("too_short", [0] * 159, "wrong_length"),
        ("not_list", {"samples": silent}, "invalid_type"),
        ("bool_sample", [True] + [0] * 159, "non_integer"),
        ("null_sample", [None] + [0] * 159, "non_integer"),
        ("string_sample", ["0"] + [0] * 159, "non_integer"),
        ("float_sample", [0.5] + [0] * 159, "non_integer"),
        ("nan_sample", [float("nan")] + [0] * 159, "nonfinite"),
        ("inf_sample", [float("inf")] + [0] * 159, "nonfinite"),
        ("low_out_of_range", [-1001] + [0] * 159, "out_of_range"),
        ("high_out_of_range", [1001] + [0] * 159, "out_of_range"),
    ]
    rows = []
    for case_id, payload, expected in cases:
        observed = _validate_frame(payload)
        rows.append({
            "id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "status": "accepted" if observed == "accepted" else "rejected",
            "qualifies": False,
        })
    accepted = sum(1 for row in rows if row["status"] == "accepted")
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "qualifies": False,
        "cases": rows,
        "summary": {
            "case_count": len(rows),
            "accepted_count": accepted,
            "rejected_count": len(rows) - accepted,
            "all_codes_match": all(
                row["expected_code"] == row["observed_code"] for row in rows),
            "audio_read": False,
            "runtime_invoked": False,
            "qualifying_results": 0,
        },
    }


def enhancement_profile_requirements() -> list[dict[str, Any]]:
    return [
        {"id": "ENH-01", "requirement": "identity/noisy control",
         "status": "blocked", "evidence": "No CleanUMamba runtime exists; no "
         "identity or noisy output was rendered.", "qualifies": False},
        {"id": "ENH-02", "requirement": "established task-matched baseline",
         "status": "blocked", "evidence": "FastEnhancer and DeepFilterNet3 are "
         "named in the candidate matrix but no matched baseline output for this "
         "cohort exists.", "qualifies": False},
        {"id": "ENH-03", "requirement": "paired SI-SDR and STOI with clean "
         "references", "status": "blocked", "evidence": "No rights-cleared "
         "paired clean/noisy cohort and no installed or approved scorer.",
         "qualifies": False},
        {"id": "ENH-04", "requirement": "clean-speech preservation",
         "status": "blocked", "evidence": "No clean-reference preservation "
         "measurement and no listening.", "qualifies": False},
        {"id": "ENH-05", "requirement": "peaks and invalid outputs",
         "status": "blocked", "evidence": "No output waveform exists to check "
         "for peaks, clipping or nonfinite values.", "qualifies": False},
        {"id": "ENH-06", "requirement": "unpaired speech predictive screen or "
         "authorized listening", "status": "blocked", "evidence": "No "
         "predictive scorer applied and no listening permission or result.",
         "qualifies": False},
        {"id": "ENH-07", "requirement": "alignment", "status": "blocked",
         "evidence": "Only declared 12/48 ms lookahead arithmetic; no measured "
         "content delay or compensation.", "qualifies": False},
        {"id": "ENH-08", "requirement": "state and memory", "status": "blocked",
         "evidence": "No streaming session, reset schedule or memory "
         "measurement.", "qualifies": False},
        {"id": "ENH-09", "requirement": "measured content/availability timing "
         "for the exact runtime", "status": "blocked", "evidence": "No device "
         "clock, callback deadline or paced workload.", "qualifies": False},
    ]


def exact_blockers() -> list[dict[str, Any]]:
    return [
        {"id": "BLK-01", "artifact_id": "A01",
         "missing": "No source license exists at the pinned upstream commit. "
         "The GitHub license field is null, no LICENSE blob is present in tree "
         "8e9abac4d880a673d249bbb6de0999566138a1f9, and LICENSE returns HTTP "
         "404. The README shows an MIT badge and a file-tree diagram entry; "
         "neither is a license grant or terms text.",
         "required_action": "Obtain an explicit upstream license at an "
         "immutable commit (SPDX identifier plus terms bytes hash) or written "
         "permission covering source use, modification, redistribution, "
         "product use and derivative outputs.",
         "status": "open", "qualifies": False},
        {"id": "BLK-02", "artifact_id": "A03",
         "missing": "Checkpoint files and Git blob SHA-1 identities exist at "
         "the pinned commit, but there is no checkpoint-specific license or "
         "terms, no published SHA-256, no retrieval record and no "
         "caller-supplied bytes. Filename and byte count alone are not "
         "identity; two E8 checkpoints share 82,788,482 bytes.",
         "required_action": "Supply one exact checkpoint path and its caller-"
         "computed SHA-256 plus byte count, immutable source commit/tree, "
         "checkpoint-specific terms and a rights decision for local execution "
         "and output use.",
         "status": "open", "qualifies": False},
        {"id": "BLK-03", "artifact_id": "A04",
         "missing": "No runtime exists in the workspace. Upstream declares "
         "Python 3.11, PyTorch 2.2.2, CUDA 11.8, mamba-ssm 1.2.2 and "
         "causal-conv1d 1.1.0 with no wheel/sdist digests; the loader sets "
         "device='cuda' and calls .cuda(). CPU and Mamba-SSM compatibility on "
         "this host is unknown.",
         "required_action": "Pin an exact runtime lock with artifact digests, "
         "a CPU-capable Mamba path and a bounded isolated-worker smoke that "
         "loads one admitted checkpoint without network access.",
         "status": "open", "qualifies": False},
        {"id": "BLK-04", "artifact_id": "A06",
         "missing": "The exact checkpoint/config to evaluate is not selected "
         "and the streaming contract is unverified. README reports 12 ms E6 "
         "and 48 ms E8 lookahead, the demo uses 4096-sample chunks; neither is "
         "aligned to the installed v0 160-sample frame and no state/reset/"
         "normalization contract is admitted.",
         "required_action": "Pin one exact model config and checkpoint, declare "
         "chunk/hop, state reset, normalization, lookahead and resampling, and "
         "verify alignment and state behaviour against the v0 160-sample "
         "boundary.",
         "status": "open", "qualifies": False},
        {"id": "BLK-05", "artifact_id": "A07",
         "missing": "No rights-cleared paired real cohort, clean references, "
         "approved SI-SDR/STOI scorer, matched FastEnhancer or DeepFilterNet3 "
         "baseline outputs, predictive screen or authorized listening result.",
         "required_action": "Supply an immutable consented cohort with clean "
         "references and output-use terms, an approved scorer, matched "
         "baseline outputs and either a predictive screen or permitted "
         "listening.",
         "status": "open", "qualifies": False},
        {"id": "BLK-06", "artifact_id": "A08",
         "missing": "No measured alignment, state, memory, content or "
         "availability timing, device-clock result, independent exact-head "
         "review, opt-in intake or release approval.",
         "required_action": "Measure the Enhancement profile on the exact "
         "runtime, record target-device timing and resources, complete "
         "independent exact-head review and approve an OFF-by-default opt-in "
         "intake.",
         "status": "open", "qualifies": False},
    ]


def required_artifacts() -> list[dict[str, Any]]:
    rows = [
        ("A01", "BLK-01", "licensed source checkout at an immutable commit"),
        ("A02", "BLK-01", "source license text and terms decision"),
        ("A03", "BLK-02", "exact checkpoint bytes with caller SHA-256 and "
                          "checkpoint terms"),
        ("A04", "BLK-03", "pinned Python/PyTorch/Mamba runtime environment"),
        ("A05", "BLK-03", "CPU-compatible runtime build and smoke record"),
        ("A06", "BLK-04", "exact model config, streaming geometry and "
                          "caller asset manifest"),
        ("A07", "BLK-05", "rights-cleared paired cohort, scorer and matched "
                          "baseline outputs"),
        ("A08", "BLK-06", "measured timing, listening/review and opt-in "
                          "intake approval"),
    ]
    return [{
        "id": artifact_id,
        "blocker": blocker,
        "name": name,
        "present": False,
        "verified": False,
        "licensed": False,
        "admitted": False,
        "blocked": True,
        "sha256": None,
    } for artifact_id, blocker, name in rows]


def release_gates() -> list[dict[str, Any]]:
    titles = (
        ("Exact source identity and license",
         "Reproduce the exact source commit/tree and a LICENSE blob with "
         "explicit terms."),
        ("Exact checkpoint identity and terms",
         "Supply the selected checkpoint path, byte count, caller SHA-256, "
         "immutable retrieval record and checkpoint-specific terms."),
        ("Runtime and CPU admission",
         "Pin the runtime artifacts and show a CPU-capable load and bounded "
         "smoke on the exact checkpoint."),
        ("Task geometry and streaming contract",
         "Admit chunk/hop, lookahead, state reset, normalization and the "
         "160-sample v0 boundary."),
        ("Rights-cleared cohort and scoring",
         "Supply paired clean/noisy references, consent/output-use terms, an "
         "approved SI-SDR/STOI scorer and matched baseline outputs."),
        ("Enhancement profile results",
         "Measure identity/noisy control, clean preservation, peaks, invalid "
         "outputs, alignment, state and memory."),
        ("Listening and timing",
         "Complete permitted listening or a predictive screen plus measured "
         "content/availability timing on a target device."),
        ("Independent review and release",
         "Complete exact-head review, opt-in intake with OFF default and "
         "release approval."),
    )
    return [{
        "id": f"RG-{index:02d}",
        "title": title,
        "requirement": requirement,
        "status": "blocked",
        "qualifies": False,
        "reopen_condition": requirement,
    } for index, (title, requirement) in enumerate(titles, start=1)]


def required_results() -> dict[str, bool]:
    return {
        "exact_source_revision_admitted": False,
        "source_license_and_terms_admitted": False,
        "checkpoint_bytes_and_sha256_admitted": False,
        "checkpoint_terms_admitted": False,
        "runtime_and_cpu_admitted": False,
        "caller_asset_manifest_admitted": False,
        "rights_cleared_cohort_present": False,
        "matched_baseline_outputs_present": False,
        "measured_enhancement_profile_present": False,
        "speech_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def source_presence() -> dict[str, Any]:
    probes = (
        "adapters/cleanumamba",
        "data/checkouts/CleanUMamba",
        "data/checkouts/cleanumamba",
        "data/envs/cleanumamba",
        "data/models/CleanUMamba",
        "data/models/cleanumamba",
        "docs/cleanumamba",
        "research/voice-enhancement-20261101/agent-cleanumamba-eval/checkpoints",
        "third_party/cleanumamba",
        "vendor/cleanumamba",
    )
    present = [path for path in probes if (AUDIO_ROOT / path).exists()]
    task_license = HERE / "LICENSE"
    return {
        "probe_scope": "project workspace only; browser caches, user profiles, "
                       "package caches and external model stores are not "
                       "inspected",
        "presence_probes": list(probes),
        "present_probes": present,
        "any_probe_present": bool(present),
        "upstream_metadata_observed": True,
        "upstream_source_bytes_present": False,
        "checkpoint_bytes_present": False,
        "runtime_environment_present": False,
        "caller_asset_manifest_present": False,
        "license_text_present": False,
        "task_license_file_present": task_license.exists(),
        "rights_cleared_cohort_present": False,
        "scorer_present": False,
        "listening_record_present": False,
        "device_timing_record_present": False,
        "admitted": False,
        "presence_is_not_admission": True,
        "network_used": False,
        "download_attempted": False,
        "runtime_imported": False,
        "runtime_invoked": False,
        "audio_read": False,
        "audio_played": False,
        "qualifies": False,
    }


def non_claims() -> list[str]:
    return [
        "No result in this package is a qualification, benchmark or release.",
        "CleanUMamba source, checkpoint bytes, a Mamba/PyTorch runtime and "
        "audio are absent; nothing was cloned, downloaded, copied, imported, "
        "built, loaded or executed.",
        "The upstream commit/tree and Git blob SHA-1 identities are public "
        "metadata observations, not checkpoint SHA-256 values and not "
        "permission to use the source or weights.",
        "The README MIT badge and file-tree LICENSE entry are not a license "
        "grant; no LICENSE blob exists at the pinned commit and LICENSE "
        "returns 404.",
        "The 12 ms E6 and 48 ms E8 lookahead values are source-reported "
        "declarations, not measured content delay or device timing.",
        "No paired SI-SDR, STOI, PESQ, clean-preservation, peak, invalid-output, "
        "state, memory, listening or timing result was produced.",
        "No FastEnhancer or DeepFilterNet3 baseline was run or compared.",
        "No provider, descriptor, registry, default, installed-v0 behaviour, "
        "public API/ABI, shared build, CI, board or handoff file is changed.",
    ]


def _rich_pins(pins: dict[str, str], root: Path) -> dict[str, Any]:
    result = {}
    for path, digest in sorted(pins.items()):
        full = root / path
        actual = sha256_file(full) if full.is_file() else None
        result[path] = {
            "sha256": digest,
            "actual": actual,
            "verified": actual == digest,
        }
    return result


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    gates = release_gates()
    for gate in gates:
        gate["linked_row"] = projection
    artifacts = required_artifacts()
    blockers = exact_blockers()
    artifact_ids = {row["id"] for row in artifacts}
    for blocker in blockers:
        if blocker["artifact_id"] not in artifact_ids:
            raise ValueError("blocker_artifact_unknown")
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_version": "0.1",
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": (
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"),
        "profile_phrases": list(PROFILE_PHRASES),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "task_local_only": True,
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "qualification_status": "not_qualified",
            "proposal_only": True,
            "blocked_before": "implementation_or_intake",
            "qualifying_results": 0,
            "blocked_release_gates": len(gates),
            "open_blockers": len(blockers),
        },
        "qualification": {
            "decision": "DEFER",
            "status": "not_qualified",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifying_results": 0,
            "open_blockers": len(blockers),
            "blocked_release_gates": len(gates),
            "exact_upstream_metadata_observed": True,
            "licensed_source_present": False,
            "checkpoint_bytes_present": False,
            "checkpoint_sha256_present": False,
            "runtime_present": False,
            "matched_evidence_present": False,
            "reasons": [
                "no LICENSE blob at the pinned upstream commit; badge and "
                "diagram are not terms",
                "no checkpoint-specific terms or published SHA-256; only Git "
                "blob SHA-1 metadata is observable",
                "no admitted CPU/Mamba runtime; upstream loader defaults to CUDA",
                "no exact selected model config or verified streaming contract",
                "no rights-cleared paired cohort, matched baseline, scorer or "
                "listening",
                "no measured alignment, state, memory or device timing",
            ],
        },
        "scope": {
            "directory": TASK_PREFIX,
            "task_local_only": True,
            "network_used": False,
            "download_attempted": False,
            "source_copied": False,
            "checkpoint_downloaded": False,
            "runtime_imported": False,
            "runtime_invoked": False,
            "audio_read": False,
            "audio_played": False,
            "real_audio": False,
            "real_corpus": False,
            "listening_conducted": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "benchmark_claim": False,
            "release_claim": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
        },
        "boundary": {
            "task_local_only": True,
            "provider_registration": False,
            "descriptor_or_registry_change": False,
            "default_change": False,
            "installed_v0_behavior_change": False,
            "installed_v0_geometry": {
                "sample_rate_hz": 16000,
                "channels": 1,
                "frame_samples": 160,
                "sample_format": "f32",
                "unchanged": True,
            },
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "external_assets_copied": False,
            "board_or_handoff_change": False,
        },
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "f32",
        },
        "source_pins": dict(sorted(SOURCE_PINS.items())),
        "boundary_pins": dict(sorted(BOUNDARY_PINS.items())),
        "sibling_pins": dict(sorted(SIBLING_PINS.items())),
        "license_findings": license_findings(),
        "upstream_observation": upstream_observation(),
        "checkpoint_ledger": checkpoint_ledger_control(),
        "geometry_control": geometry_control(),
        "enhancement_profile_requirements": enhancement_profile_requirements(),
        "caller_asset": {
            "contract_id": MANIFEST_SCHEMA_ID,
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "status": "blocked",
            "manifest_present": False,
            "workspace_manifest": "data/manifests/cleanumamba.json (absent)",
            "executed": False,
            "imported": False,
            "loaded": False,
            "asset_is_candidate": False,
            "present_behavior": "validate_schema_geometry_and_license_metadata_"
                                "only; do_not_load_or_execute",
            "absent_behavior": "reject_before_processing",
            "required_fields": list(MANIFEST_FIELDS),
            "required_geometry": {
                "sample_rate_hz": 16000,
                "channels": 1,
                "frame_samples": 160,
                "status": "v0_caller_boundary",
            },
            "required_source_commit": UPSTREAM_HEAD,
            "required_source_tree_sha1": UPSTREAM_TREE,
            "checkpoint_sha256_required_from_caller": True,
            "synthetic_schema_control_only": True,
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "required_artifacts": artifacts,
        "required_results": required_results(),
        "non_claims": non_claims(),
        "reproduction": {
            "python": "3.12.16, standard library only",
            "repeat_count": 3,
            "byte_identical_required": True,
            "network_used": False,
            "commands": [
                "export PYTHONDONTWRITEBYTECODE=1",
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
        },
        "linked_row_identity": {
            "projection": projection,
            "sha256": object_digest(projection),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
    }


def build_report(contract: dict[str, Any]) -> dict[str, Any]:
    copy_keys = (
        "disposition", "qualification", "scope", "boundary",
        "public_v0_geometry", "non_claims", "license_findings",
        "exact_blockers", "required_artifacts", "required_results",
        "upstream_observation", "checkpoint_ledger", "geometry_control",
        "enhancement_profile_requirements", "caller_asset", "reproduction",
        "linked_row_identity",
    )
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "report_version": "0.1.0",
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "contract_sha256": object_digest(contract),
        "gates": contract["release_gates"],
        "enhancement_outcomes": [{
            "id": row["id"],
            "requirement": row["requirement"],
            "status": "blocked",
            "value": None,
            "qualifies": False,
        } for row in contract["enhancement_profile_requirements"]],
        "manifest_control": manifest_control(),
        "frame_control": frame_control(),
        "source_presence": source_presence(),
        "source_pins": _rich_pins(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": _rich_pins(BOUNDARY_PINS, WORKTREE),
        "sibling_pins": _rich_pins(SIBLING_PINS, WORKTREE),
        "board_snapshot": {
            "path": BOARD_TASK_ROW,
            "mutable": True,
            "note": "Mutable board path recorded for provenance only; never "
                    "hashed, gated or treated as a result.",
        },
        "readme_digest_sections": ["source", "boundary", "upstream",
                                   "artifacts"],
        "readme_digest_files": sorted(
            name for name in artifact_table_names()),
    }
    for key in copy_keys:
        report[key] = contract[key]
    return report


def contract_bytes() -> bytes:
    return canonical_bytes(build_contract())


def report_bytes(contract: dict[str, Any]) -> bytes:
    return canonical_bytes(build_report(contract))


# ---------------------------------------------------------------------------
# README digest tables

def _table_rows(text: str, section: str) -> list[list[str]]:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    body = text.split(start, 1)[1]
    if end not in body:
        raise ValueError("readme_end_missing:" + section)
    body = body.split(end, 1)[0]
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def expected_upstream_fields() -> dict[str, str]:
    ledger = checkpoint_ledger_control()
    return {
        "commit": UPSTREAM_HEAD,
        "tree_sha1": UPSTREAM_TREE,
        "readme_sha256": UPSTREAM_README_SHA256,
        "readme_git_blob_sha1": UPSTREAM_README_GIT_BLOB_SHA1,
        "license_metadata_field": "absent",
        "license_path_http_status": "404",
        "checkpoint_count": str(ledger["checkpoint_count"]),
        "checkpoint_bytes": str(ledger["checkpoint_bytes"]),
        "published_checkpoint_sha256": "0",
    }


def artifact_table_names() -> list[str]:
    return sorted(
        path.name for path in HERE.iterdir()
        if path.is_file() and path.name not in ARTIFACT_TABLE_EXCLUDED
        and path.name in LOCAL_PIN_FILES)


def render_artifact_table() -> str:
    rows = [
        "<!-- digest-table: artifacts -->",
        "| File | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in artifact_table_names():
        path = HERE / name
        rows.append(
            f"| `{name}` | `{sha256_file(path)}` | {path.stat().st_size} |")
    rows.append("<!-- digest-table: end -->")
    return "\n".join(rows)


def render_readme(text: str) -> str:
    start, end = README_MARKERS["artifacts"]
    if text.count(start) != 1 or text.count(end) < 1:
        raise ValueError("readme_artifacts_marker")
    head, rest = text.split(start, 1)
    tail = rest.split(end, 1)[1]
    return head + render_artifact_table() + tail


def verify_readme_digests(text: str) -> dict[str, int]:
    counts = {}
    source_rows = _table_rows(text, "source")
    expected_source = {f"source:{key}": digest
                       for key, digest in SOURCE_PINS.items()}
    actual_source = {row[0]: row[1] for row in source_rows}
    if set(actual_source) != set(expected_source):
        raise ValueError("readme_source_keys")
    for key, digest in actual_source.items():
        relative = key[len("source:"):]
        if digest != expected_source[key]:
            raise ValueError("readme_source_digest:" + key)
        if sha256_file(AUDIO_ROOT / relative) != digest:
            raise ValueError("readme_source_live:" + key)
    counts["source"] = len(source_rows)

    boundary_rows = _table_rows(text, "boundary")
    expected_boundary = {f"sdk:{key}": digest
                         for key, digest in BOUNDARY_PINS.items()}
    actual_boundary = {row[0]: row[1] for row in boundary_rows}
    if set(actual_boundary) != set(expected_boundary):
        raise ValueError("readme_boundary_keys")
    for key, digest in actual_boundary.items():
        relative = key[len("sdk:"):]
        if digest != expected_boundary[key]:
            raise ValueError("readme_boundary_digest:" + key)
        if sha256_file(WORKTREE / relative) != digest:
            raise ValueError("readme_boundary_live:" + key)
    counts["boundary"] = len(boundary_rows)

    upstream_rows = _table_rows(text, "upstream")
    actual_upstream = {row[0]: row[1] for row in upstream_rows}
    expected_upstream = expected_upstream_fields()
    if actual_upstream != expected_upstream:
        raise ValueError("readme_upstream_fields")
    counts["upstream"] = len(upstream_rows)

    artifact_rows = _table_rows(text, "artifacts")
    expected_artifacts = set(artifact_table_names())
    actual_artifacts = {row[0] for row in artifact_rows}
    if actual_artifacts != expected_artifacts:
        raise ValueError("readme_artifact_keys")
    for row in artifact_rows:
        name, digest, size = row
        path = HERE / name
        if digest != sha256_file(path):
            raise ValueError("readme_artifact_digest:" + name)
        if size != str(path.stat().st_size):
            raise ValueError("readme_artifact_size:" + name)
    counts["artifacts"] = len(artifact_rows)
    return counts


# ---------------------------------------------------------------------------
# SOURCES.sha256

def _source_manifest_rows() -> list[tuple[str, Path]]:
    rows = []
    for path in sorted(SOURCE_PINS):
        rows.append(("source:" + path, AUDIO_ROOT / path))
    for path in sorted(BOUNDARY_PINS):
        rows.append(("boundary:" + path, WORKTREE / path))
    for path in sorted(SIBLING_PINS):
        rows.append(("sibling:" + path, WORKTREE / path))
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name != "SOURCES.sha256":
            rows.append((path.name, path))
    return rows


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-CLEANUMAMBA task-local evidence.",
        "# source: paths are relative to AUDIO_ROOT; boundary: and sibling: "
        "paths are SDK-worktree relative.",
        "# The mutable full plan/swarm/TASKS.json is not pinned; only its "
        "stable linked-row projection is read and gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    for key, path in _source_manifest_rows():
        if not path.is_file():
            raise ValueError("manifest_file_missing:" + key)
        lines.append(f"{sha256_file(path)}  {key}")
    return ("\n".join(lines) + "\n").encode("ascii")


def verify_sources_manifest(data: bytes) -> int:
    text = data.decode("ascii")
    expected = {key for key, _ in _source_manifest_rows()}
    seen: set[str] = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or not HEX64.match(parts[0]):
            raise ValueError("source_line_malformed")
        digest, key = parts
        if key in seen:
            raise ValueError("source_duplicate:" + key)
        seen.add(key)
        if key == "SOURCES.sha256":
            raise ValueError("source_self_pin")
        if key not in expected:
            raise ValueError("source_unknown:" + key)
        path = _resolve_manifest_key(key)
        if sha256_file(path) != digest:
            raise ValueError("source_mismatch:" + key)
    if seen != expected:
        raise ValueError("source_missing")
    return len(seen)


def _resolve_manifest_key(key: str) -> Path:
    if key.startswith("source:"):
        return AUDIO_ROOT / key[len("source:"):]
    if key.startswith("boundary:"):
        return WORKTREE / key[len("boundary:"):]
    if key.startswith("sibling:"):
        return WORKTREE / key[len("sibling:"):]
    return HERE / key
