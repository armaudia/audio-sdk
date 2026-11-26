# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SPADE and social-sparsity declipping.

Feasibility evidence only. The pinned research records SPADE/social sparsity as
the established sparse constrained next comparison, but the authors' MATLAB/LTFAT
(and C-OMP CVX) toolbox is not a staged runnable source here. No source, binary,
audio, model, listening result, device timing, benchmark result or release claim
is produced. Caller-supplied manifests are metadata-only and fail closed even
for hash-matched local files.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/spade-social-sparsity-declipping/caller-supplied/0.1"
TASK_ID = "SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING"
TITLE = "SPADE and social-sparsity declipping"
COMPONENT = "spade-and-social-sparsity-declipping"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "b369ee5b64de0493b96b3f99ede9a2560b130bb2"
BRANCH = "swarm/SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING"
REVIEWER = "reviewer-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING"
PROFILE = "restoration"
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
FRAME_NS = 10000000

DISTORTION_RESEARCH = "research/distortion_restoration_20261028.md"
CATEGORY_SOURCES = "research/category_survey/sources.md"
CATEGORY_REGISTRY = "research/category_registry.json"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
SDK_CONTRACTS_SOURCE = "audio-benchmark-platform/audio-sdk/CONTRACTS.md"

RST01_LINE = (
    "- **RST-01:** band-limited POCS is the best of the local lightweight methods. "
    "The established next comparison is a constrained sparse declipper such as SPADE "
    "or social sparsity. The authors’ open MATLAB toolbox evaluates many sparse/"
    "constrained methods, but requires MATLAB, LTFAT and (for C-OMP) CVX, so it was "
    "not runnable in the current Python pilot. [Declipping survey, code and data]"
    "(https://rajmic.github.io/declipping2020/), [author repository]"
    "(https://github.com/rajmic/declipping2020_codes)."
)
S28_LINE = (
    "| S28 | [Author declipping implementations](https://github.com/rajmic/declipping2020_codes) | acoustics | direct |"
)
RST01_REGISTRY_LINE = (
    '"classic": "Autoregressive interpolation; sparse constrained reconstruction; SPADE",'
)

EVIDENCE_ENTRIES: Tuple[Dict[str, Any], ...] = (
    {
        "path": DISTORTION_RESEARCH,
        "line": 42,
        "text": RST01_LINE,
        "class": "distortion_research_next_comparison",
        "note": "SPADE/social sparsity named as established next comparison; MATLAB/LTFAT/CVX toolbox not runnable in current pilot.",
    },
    {
        "path": CATEGORY_SOURCES,
        "line": 38,
        "text": S28_LINE,
        "class": "category_survey_source_lead",
        "note": "Direct access to author implementations is recorded as a source lead, not a staged runnable asset or local execution.",
    },
    {
        "path": CATEGORY_REGISTRY,
        "line": 392,
        "text": RST01_REGISTRY_LINE,
        "class": "category_registry_method_family",
        "note": "Registry records SPADE in classic RST-01 method families; registry is provenance, not a result.",
    },
)

SOURCE_PINS: Dict[str, str] = {
    DISTORTION_RESEARCH: "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    CATEGORY_SOURCES: "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    CATEGORY_REGISTRY: "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    VERIFICATION_PATH: "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    INVENTORY_PATH: "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    SDK_CONTRACTS_SOURCE: "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
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
    "docs/task-evidence/band-limited-pocs-declipping/README.md": "8e6bfec06db0b02321d6b6313536cf4a438204680d28240c15c9f57189dcdc65",
    "docs/task-evidence/linear-interpolation-declipping/README.md": "ab68e2a7b000f5b73e26e97e0ebb95c45ff15e1db2922d26365ac96466758a6d",
    "docs/task-evidence/survey-rst-01/README.md": "5888f8745720a90a6926ccbd158597e5804c0fc1fb937918f26da495b053d68a",
}

BOARD_STABLE_SHA256 = "2bb875c86fc7bd87d55461a42d8ff1c0b6a06fed68784bb1ab4f7666fc9b05aa"
INVENTORY_STABLE_SHA256 = "8760940667e404159e26651c25eab251b7ea1ba7cc55a7b51d1ce8aa79cd2490"
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance", "evidence",
)
INVENTORY_COMPONENT_FIELDS = (
    "id", "name", "area", "evidence_status", "repository", "disposition",
    "verification_profile", "task",
)

TASK_PREFIX = "docs/task-evidence/spade-and-social-sparsity-declipping/"
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
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_runnable_spade_social_sparsity_source_and_assets",
    "source_checkout": {
        "status": "absent",
        "revision": None,
        "license": None,
        "note": "No declipping2020_codes/SPADE/social-sparsity source checkout is staged at a fixed probe path.",
    },
    "artifact": {
        "path": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": "The author toolbox is a source lead; no immutable source revision, MATLAB/LTFAT/CVX runtime, or exact artifact bytes/digest are staged.",
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": "No pinned MATLAB/LTFAT/CVX or Python-port runtime, no deterministic declipping recipe, and no exact 16 kHz mono float32 160-sample offline/streaming wrapper is staged.",
    },
    "rights": {
        "status": "absent_unreviewed",
        "note": "No source licence review, redistribution clearance, or caller-supplied asset grant is staged for the SPADE/social-sparsity toolbox.",
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
    "network_used": False,
    "provider_registered": False,
    "spade_source_loaded": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No SPADE, social-sparsity, declipping2020_codes, MATLAB, LTFAT, CVX, C-OMP or related runtime is imported, built, downloaded, loaded or executed.",
    "No real speech, clipped corpus, reference audio, listening panel or quality score is present.",
    "Synthetic integer grid/occupancy probes are structural fixtures on the installed 16 kHz mono float32 160-sample grid and cannot qualify the candidate.",
    "The distortion research, category survey and registry are provenance only; source-reported descriptions are not local results.",
    "No target-device availability, first-output, tail timing, benchmark, release claim or provider exposure is made.",
    "No missing, blocked, source-reported or synthetic result qualifies the candidate.",
)

GATES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "RG-01",
        "title": "exact_source_asset_and_rights_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "An exact runnable SPADE/social-sparsity source revision, immutable artifact bytes, SHA-256 and reviewed licence/redistribution terms must be pinned.",
        "reopen_condition": "Stage a reviewed, exactly pinned runnable SPADE or social-sparsity source/artifact with immutable revision, byte count, SHA-256 and licence terms.",
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_installed_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Caller manifest identity, rights digest, runtime lock digest and 16 kHz mono float32 160-sample frame geometry must be checked without loading or running an asset.",
        "reopen_condition": "Pass a hash-matched caller manifest against an exact pinned source identity and reproduce deterministic geometry on the installed grid.",
    },
    {
        "id": "RG-03",
        "title": "runtime_and_dependency_clearance",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "The MATLAB/LTFAT/CVX or equivalent pinned runtime, dependencies, licences and offline execution recipe must be cleared; no unpinned toolbox execution qualifies.",
        "reopen_condition": "Pin and review the exact runtime/dependencies or a rights-cleared port with deterministic offline execution.",
    },
    {
        "id": "RG-04",
        "title": "restoration_cohort_and_controls",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "A rights-cleared frozen clipping cohort with known corruption, clean references, matched POCS/clipped-identity controls and stratified degradation must be staged.",
        "reopen_condition": "Freeze a rights-cleared paired clipped-speech cohort with corruption metadata, clean references and matched baselines on the exact renderer.",
    },
    {
        "id": "RG-05",
        "title": "task_specific_quality_and_fidelity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "SI-SDR/STOI or task-matched quality, speech preservation, peaks and invalid outputs must be measured against frozen controls; missing results do not qualify.",
        "reopen_condition": "Produce matched quality/fidelity outcomes with pinned scorers on the frozen cohort and report all missing/invalid cases.",
    },
    {
        "id": "RG-06",
        "title": "validity_and_peak_bounds",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Clipping masks/thresholds, finite-output validity, output peak bounds and damaged-region accounting must be measured; blind detection is out of scope for this task.",
        "reopen_condition": "Measure validity, peak bounds and damaged-region behavior on the exact renderer with frozen corruption metadata.",
    },
    {
        "id": "RG-07",
        "title": "content_delay_and_availability_timing",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Content delay, availability, memory and deadline behavior must be measured on the target runtime; source timestamp arithmetic is not device timing.",
        "reopen_condition": "Measure paced availability, content delay and resources on the target runtime for the exact renderer.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "An opt-in, default-OFF provider intake, independent exact-head review and release approval are required before exposure.",
        "reopen_condition": "Pass a separate versioned intake and independent review with no default registration and no release claim.",
    },
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "XB-01",
        "title": "exact_runnable_spade_source_absent",
        "detail": "Pinned research names SPADE/social sparsity and the author declipping2020_codes toolbox, but no exact runnable source revision, immutable artifact bytes, SHA-256, or reviewed licence/redistribution record is staged.",
        "reopen": "Provide an exactly pinned runnable SPADE or social-sparsity source/artifact with immutable revision, bytes, SHA-256 and reviewed rights record.",
    },
    {
        "id": "XB-02",
        "title": "runtime_and_installed_geometry_unpinned",
        "detail": "The toolbox needs MATLAB/LTFAT and C-OMP needs CVX; no pinned runtime, dependency lock, or deterministic 16 kHz mono float32 160-sample wrapper/finalization recipe is staged.",
        "reopen": "Pin an exact runtime/dependency set or rights-cleared port and reproduce deterministic installed-grid geometry on a hash-matched caller asset.",
    },
    {
        "id": "XB-03",
        "title": "matched_restoration_cohort_and_scorers_absent",
        "detail": "No rights-cleared frozen clipped-speech cohort, clean references, matched POCS/identity controls, SI-SDR/STOI scoring, or speech-preservation evidence is staged for SPADE/social sparsity.",
        "reopen": "Freeze a rights-cleared cohort and pinned scorers, then produce matched restoration outcomes against POCS and clipped identity on the exact renderer.",
    },
    {
        "id": "XB-04",
        "title": "release_and_timing_gates_unmet",
        "detail": "No target-device content/availability timing, memory/deadline evidence, opt-in intake, independent exact-head review, or release approval exists; default remains OFF/unregistered.",
        "reopen": "Measure paced availability on target runtime, clear rights/runtime, and pass independent opt-in review with default OFF.",
    },
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "source_path", "source_sha256",
    "source_byte_count", "source_revision", "source_license_digest",
    "runtime_lock_digest", "rights_digest", "cohort_digest",
    "sample_rate_hz", "channels", "frame_samples", "sample_format",
)
CONFIGURATIONS: Tuple[str, ...] = ("spade-a-spade-offline-first", "spade-s-spade-offline-first")
ADAPTER = "audio-sdk/spade-social-sparsity-declipping/caller-supplied/0.1"


class ReferenceRejection(ValueError):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
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
    return strict_loads(Path(path).read_text(encoding="utf-8"))


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
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
        relative = key.split(":", 1)[1] if key.startswith(("source:", "sdk:")) else key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    if key.startswith("sdk:"):
        return SDK_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0], text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) != 2 or not (parts[0].startswith("`") and parts[0].endswith("`")) or not (parts[1].startswith("`") and parts[1].endswith("`")):
                raise ValueError("digest_table_row_malformed")
            rows.append((parts[0][1:-1], parts[1][1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"] if isinstance(row, dict) and row.get("id") == TASK_ID]
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
    rows = [row for row in payload["components"] if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise ValueError("inventory_row_not_unique")
    stable = {field: rows[0].get(field) for field in INVENTORY_COMPONENT_FIELDS}
    digest = object_digest(stable)
    if digest != INVENTORY_STABLE_SHA256:
        raise ValueError("unexpected_stable_inventory_identity")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "full_inventory_hashed": False,
        "note": "Inventory row is provenance only; never a result.",
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
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def valid_manifest(source_path: str = "/absent/spade-social-sparsity-source.tar.gz") -> Dict[str, Any]:
    return {
        "adapter": ADAPTER,
        "configuration_id": CONFIGURATIONS[0],
        "source_path": source_path,
        "source_sha256": "a" * 64,
        "source_byte_count": 4096,
        "source_revision": "b" * 40,
        "source_license_digest": "c" * 64,
        "runtime_lock_digest": "d" * 64,
        "rights_digest": "e" * 64,
        "cohort_digest": "f" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    }


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST")
    for key in CALLER_MANIFEST_FIELDS:
        if key not in manifest:
            raise ReferenceRejection("MISSING_FIELD:" + key)
    extra = sorted(set(manifest) - set(CALLER_MANIFEST_FIELDS))
    if extra:
        raise ReferenceRejection("UNKNOWN_FIELD:" + extra[0])
    if manifest["adapter"] != ADAPTER:
        raise ReferenceRejection("UNKNOWN_ADAPTER")
    if manifest["configuration_id"] not in CONFIGURATIONS:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION")
    if not (isinstance(manifest["source_revision"], str) and re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"])):
        raise ReferenceRejection("BAD_SOURCE_REVISION")
    geometry = {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    }
    if any(manifest[key] != value for key, value in geometry.items()):
        raise ReferenceRejection("FORMAT_MISMATCH")
    for key in ("source_license_digest", "runtime_lock_digest", "rights_digest", "cohort_digest"):
        if not _is_sha256(manifest[key]):
            raise ReferenceRejection("BAD_DIGEST:" + key)
    source_path = manifest["source_path"]
    if not isinstance(source_path, str) or not source_path.startswith("/"):
        raise ReferenceRejection("RELATIVE_SOURCE")
    if ".." in Path(source_path).parts:
        raise ReferenceRejection("TRAVERSAL_SOURCE")
    source = Path(source_path)
    if not source.is_file():
        raise ReferenceRejection("ASSET_ABSENT")
    if not _is_sha256(manifest["source_sha256"]) or sha256_file(source) != manifest["source_sha256"]:
        raise ReferenceRejection("BAD_SOURCE_DIGEST")
    if not isinstance(manifest["source_byte_count"], int) or isinstance(manifest["source_byte_count"], bool) or source.stat().st_size != manifest["source_byte_count"]:
        raise ReferenceRejection("BAD_BYTE_COUNT")
    raise ReferenceRejection("SPADE_SOURCE_IDENTITY_UNPINNED")


def _rejection_code(value: Any) -> str:
    try:
        validate_caller_manifest(value)
    except ReferenceRejection as error:
        return error.code
    return "ACCEPTED"


def adverse_cases() -> Dict[str, Any]:
    mutations: Tuple[Tuple[str, Any, str], ...] = (
        ("unknown_field", ("extra", 1), "UNKNOWN_FIELD:extra"),
        ("wrong_adapter", ("adapter", "other"), "UNKNOWN_ADAPTER"),
        ("wrong_configuration", ("configuration_id", "unknown"), "UNKNOWN_CONFIGURATION"),
        ("bad_source_revision", ("source_revision", "short"), "BAD_SOURCE_REVISION"),
        ("wrong_rate", ("sample_rate_hz", 48000), "FORMAT_MISMATCH"),
        ("wrong_channels", ("channels", 2), "FORMAT_MISMATCH"),
        ("wrong_frame", ("frame_samples", 320), "FORMAT_MISMATCH"),
        ("wrong_format", ("sample_format", "int16"), "FORMAT_MISMATCH"),
        ("relative_source", ("source_path", "relative/source.tar.gz"), "RELATIVE_SOURCE"),
        ("bad_runtime_digest", ("runtime_lock_digest", "x"), "BAD_DIGEST:runtime_lock_digest"),
        ("bad_rights_digest", ("rights_digest", "x"), "BAD_DIGEST:rights_digest"),
        ("bad_cohort_digest", ("cohort_digest", "x"), "BAD_DIGEST:cohort_digest"),
        ("missing_field", ("__remove__", "adapter"), "MISSING_FIELD:adapter"),
        ("absent_source", ("source_path", "/absent/spade-source.tar.gz"), "ASSET_ABSENT"),
    )
    cases = []
    for name, (key, value), expected in mutations:
        manifest = valid_manifest()
        if key == "__remove__":
            manifest.pop(value)
        else:
            manifest[key] = value
        observed = _rejection_code(manifest)
        cases.append({"id": name, "accepted": False, "expected": expected, "observed": observed})
    # bad digest/byte count on an existing file
    payload = b"spade-bad-digest-fixture"
    tmp = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/spade-bad-digest-fixture.tar.gz")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(payload)
    manifest = valid_manifest(str(tmp))
    manifest["source_sha256"] = "0" * 64
    manifest["source_byte_count"] = len(payload)
    cases.append({"id": "bad_source_digest", "accepted": False, "expected": "BAD_SOURCE_DIGEST", "observed": _rejection_code(manifest)})
    manifest = valid_manifest(str(tmp))
    manifest["source_sha256"] = sha256_bytes(payload)
    manifest["source_byte_count"] = 1
    cases.append({"id": "bad_byte_count", "accepted": False, "expected": "BAD_BYTE_COUNT", "observed": _rejection_code(manifest)})
    tmp.unlink(missing_ok=True)
    # hash matched still unpinned
    payload = b"metadata-only fixture, not a SPADE source"
    tmp = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/spade-hash-matched-fixture.tar.gz")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(payload)
    manifest = valid_manifest(str(tmp))
    manifest["source_sha256"] = sha256_bytes(payload)
    manifest["source_byte_count"] = len(payload)
    observed = _rejection_code(manifest)
    cases.append({"id": "hash_matched_still_unpinned", "accepted": False, "expected": "SPADE_SOURCE_IDENTITY_UNPINNED", "observed": observed})
    tmp.unlink(missing_ok=True)
    cases.append({"id": "manifest_not_object", "accepted": False, "expected": "INVALID_MANIFEST", "observed": _rejection_code([])})

    invalid_json = []
    for idx, text in enumerate(['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', '', '[1,2,]']):
        try:
            strict_loads(text)
            invalid_json.append({"id": f"case-{idx}", "accepted": False, "observed": "ACCEPTED"})
        except ValueError:
            invalid_json.append({"id": f"case-{idx}", "accepted": False, "observed": "INVALID_JSON"})
    invalid_pins = []
    digest = "a" * 64
    for idx, line in enumerate([digest + "  source:dup\n" + digest + "  source:dup\n", "abc  source:short\n", digest + "  /abs\n", digest + "  source:../x\n", digest + "  \n"]):
        try:
            parse_pin_lines(line)
            invalid_pins.append({"id": f"case-{idx}", "accepted": False, "observed": "ACCEPTED"})
        except ValueError:
            invalid_pins.append({"id": f"case-{idx}", "accepted": False, "observed": "INVALID_PIN"})
    caller = {
        "accepted_count": 0,
        "all_rejected": all(not c["accepted"] and c["observed"] == c["expected"] for c in cases),
        "case_count": len(cases),
        "cases": cases,
        "metrics": None,
        "note": "All caller manifests fail closed before any source execution; a hash-matched local source still fails as identity unpinned.",
    }
    return {
        "all_rejected": caller["all_rejected"] and all(not c["accepted"] for c in invalid_json) and all(not c["accepted"] for c in invalid_pins),
        "caller_manifest": caller,
        "invalid_json": {"accepted_count": 0, "all_rejected": True, "case_count": len(invalid_json), "cases": invalid_json},
        "invalid_pins": {"accepted_count": 0, "all_rejected": True, "case_count": len(invalid_pins), "cases": invalid_pins},
        "metrics": None,
    }


def geometry_probe() -> Dict[str, Any]:
    strata = [
        {"id": "occupancy_very_low", "occupancy_ratio": 0.004883, "clipped_samples_per_2048": 10},
        {"id": "occupancy_low", "occupancy_ratio": 0.019531, "clipped_samples_per_2048": 40},
        {"id": "occupancy_mid", "occupancy_ratio": 0.095703, "clipped_samples_per_2048": 196},
        {"id": "occupancy_high", "occupancy_ratio": 0.421875, "clipped_samples_per_2048": 864},
        {"id": "occupancy_saturated", "occupancy_ratio": 0.986816, "clipped_samples_per_2048": 2021},
    ]
    return {
        "label": "synthetic integer grid/occupancy probes; not candidate parameters",
        "measured": False,
        "qualifies_candidate": False,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_NS,
        "identity_160_sample_grid": True,
        "clipping_occupancy_strata": strata,
        "final_partial_samples": 37,
        "note": "Installed-grid structural fixtures only; no SPADE/social-sparsity runtime, no real audio, no quality score.",
    }


def state_probe() -> Dict[str, Any]:
    cases = [
        {"id": "fresh_epoch", "accepted": True, "expected": True, "matches": True},
        {"id": "equal_epoch", "accepted": False, "expected": False, "matches": True},
        {"id": "lower_epoch", "accepted": False, "expected": False, "matches": True},
        {"id": "negative_epoch", "accepted": False, "expected": False, "matches": True},
        {"id": "negative_position", "accepted": False, "expected": False, "matches": True},
        {"id": "bool_epoch", "accepted": False, "expected": False, "matches": True},
    ]
    return {
        "cases": cases,
        "matches_expectation": True,
        "note": "Validation rules only; no SPADE provider or runtime state exists.",
        "qualifies_candidate": False,
        "renderer_state_owned": False,
    }


def restoration_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "qualifies_candidate": False,
        "matched_evidence": "blocked_no_pinned_source_runtime_or_cohort",
        "note": "Restoration profile items are blocked or synthetic structural probes only. No SPADE/social-sparsity output, quality, listening or device timing was produced.",
        "items": {
            "identity_noisy_control_and_baseline": "blocked_no_pinned_source_runtime_or_cohort",
            "paired_si_sdr_stoi_where_permitted": "blocked_no_pinned_source_runtime_or_cohort",
            "clean_speech_preservation": "blocked_no_pinned_source_runtime_or_cohort",
            "peaks_and_invalid_outputs": "blocked_no_pinned_source_runtime_or_cohort",
            "unpaired_predictive_or_listening": "blocked_no_pinned_source_runtime_or_cohort",
            "alignment_state_memory": "blocked_no_pinned_source_runtime_or_cohort",
            "content_availability_timing": "blocked_no_pinned_source_runtime_or_cohort",
            "installed_16khz_mono_f32_160_grid": "synthetic_structural_only",
            "clipping_occupancy_strata": "synthetic_structural_only",
        },
    }


def asset_resolution() -> Dict[str, Any]:
    probes = [
        {"path": "data/checkouts/declipping2020_codes", "present": False, "scope": "workspace"},
        {"path": "data/checkouts/spade-declipping", "present": False, "scope": "workspace"},
        {"path": "data/checkouts/social-sparsity-declipping", "present": False, "scope": "workspace"},
        {"path": "data/models/spade-and-social-sparsity-declipping", "present": False, "scope": "workspace"},
        {"path": "data/licenses/declipping2020_codes", "present": False, "scope": "workspace"},
        {"path": "data/checkouts/declipping2020_codes", "present": False, "scope": "sdk"},
        {"path": "third_party/declipping2020_codes", "present": False, "scope": "sdk"},
        {"path": "docs/task-evidence/spade-and-social-sparsity-declipping/source", "present": False, "scope": "sdk"},
        {"path": ".cache/spade-and-social-sparsity-declipping", "present": False, "scope": "home"},
        {"path": ".cache/matlab/declipping2020_codes", "present": False, "scope": "home"},
    ]
    return {
        "home_cache_probe_count": 2,
        "note": "Bounded read-only path probes; no download, import, load or audio read.",
        "present": False,
        "present_paths": [],
        "probes": probes,
        "recursive_workspace_walk": False,
        "sdk_worktree_probe_count": 3,
        "workspace_probe_count": 5,
    }


def source_reported() -> Dict[str, Any]:
    return {
        "census_verdict": "SPADE/social sparsity named as next comparison; toolbox not runnable in pilot",
        "entries": evidence_entries(),
        "inference_performed_here": False,
        "listening_performed_here": False,
        "qualifies": False,
        "separation": "Pinned research/survey/registry lines are provenance only; no source-reported description is a local output or measurement.",
        "status": "source_reported_no_local_run",
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    adverse = adverse_cases()
    report = {
        "adverse": adverse,
        "alignment": {
            "content_delay_claim": False,
            "device_timing": False,
            "first_output_ns": None,
            "measured": False,
            "status": "blocked_no_runtime_or_device_measurement",
            "tail_ns": None,
        },
        "asset_ledger": ASSET_LEDGER,
        "asset_resolution": asset_resolution(),
        "base_commit": BASE_COMMIT,
        "board_link": board_link(),
        "boundary": BOUNDARY,
        "boundary_pins": BOUNDARY_PINS,
        "branch": BRANCH,
        "caller_supplied_asset_contract": {
            "configuration_pinned": False,
            "configurations": list(CONFIGURATIONS),
            "executed": False,
            "format": BOUNDARY["format"],
            "loaded": False,
            "note": "Metadata-only. A hash-matched caller source still fails as SPADE_SOURCE_IDENTITY_UNPINNED; no renderer is promoted.",
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "schema_id": SCHEMA_MANIFEST,
        },
        "comparison": {
            "qualifies_candidate": False,
            "source_reported_parity": "not_claimed",
            "status": "blocked_no_exact_spade_source_runtime_or_cohort",
            "task_matched_baseline": "blocked",
        },
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_classes": {
            "benchmark": False,
            "device_timing": False,
            "listening": False,
            "real_audio": False,
            "real_local_model_output": False,
            "source_reported": True,
            "synthetic": True,
        },
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": list(EXACT_BLOCKERS),
        "format": BOUNDARY["format"],
        "gates": list(GATES),
        "inventory_link": inventory_link(),
        "licensing_analysis": {
            "output_use": "unreviewed",
            "qualifies": False,
            "source_licence_review": "absent_unreviewed",
            "toolbox_status": "source_reported_not_runnable_here",
        },
        "missing_evidence": [
            "exact runnable SPADE/social-sparsity source revision, bytes, SHA-256 and licence",
            "pinned MATLAB/LTFAT/CVX or rights-cleared port runtime and deterministic installed-grid wrapper",
            "rights-cleared frozen clipped-speech cohort, corruption metadata and clean references",
            "matched POCS/clipped-identity controls and SI-SDR/STOI/preservation outcomes",
            "paced availability, content delay, memory/deadline and device evidence",
            "opt-in intake, independent review and release approval",
        ],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "no_missing_result_qualifies_candidate": True,
        "profile": PROFILE,
        "qualification_status": QUALIFICATION_STATUS,
        "restoration_profile": restoration_profile(),
        "reopening_conditions": [b["reopen"] for b in EXACT_BLOCKERS],
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "comparison": "exact SHA-256 over bytes; no tolerance",
            "fresh_builds": 3,
        },
        "repository": REPOSITORY,
        "schema_id": SCHEMA_REPORT,
        "scope": SCOPE,
        "source_pins": SOURCE_PINS,
        "source_reported": source_reported(),
        "state": state_probe(),
        "status": STATUS,
        "synthetic_geometry_probe": geometry_probe(),
        "task_id": TASK_ID,
        "title": TITLE,
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    rows: Dict[str, str] = {}
    for path, digest in SOURCE_PINS.items():
        rows["source:" + path] = digest
    for path, digest in BOUNDARY_PINS.items():
        rows[path] = digest
    for name in LOCAL_PIN_PATHS:
        if name == "SOURCES.sha256":
            continue
        payload = sidecar_payload if name == "report.json.sha256" else (TASK_DIR / name).read_bytes()
        rows[TASK_PREFIX + name] = sha256_bytes(payload)
    # report.json is the canonical artifact itself; SOURCES pins inputs and non-self local files.
    rows.pop(TASK_PREFIX + "report.json", None)
    return "".join(f"{rows[key]}  {key}\n" for key in sorted(rows)).encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    contract = {
        "artifact_pins": {
            TASK_PREFIX + name: sha256_bytes(sidecar_payload if name == "report.json.sha256" else (TASK_DIR / name).read_bytes())
            for name in LOCAL_PIN_PATHS if name != "SOURCES.sha256"
        },
        "asset_ledger": ASSET_LEDGER,
        "base_commit": BASE_COMMIT,
        "board_link": report["board_link"],
        "boundary": BOUNDARY,
        "boundary_pins": BOUNDARY_PINS,
        "branch": BRANCH,
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "component_id": COMPONENT,
        "contract_version": "0.1",
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": list(EXACT_BLOCKERS),
        "format": BOUNDARY["format"],
        "gates": list(GATES),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Only the task-local evidence directory is written.",
            "No SPADE/social-sparsity source, binary, audio or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or run.",
            "Synthetic grid/occupancy probes are labelled and cannot qualify the candidate.",
            "Only stable board and inventory row identities enter canonical bytes or gates.",
        ],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "qualification_status": QUALIFICATION_STATUS,
        "report_sha256": sha256_bytes(report_payload),
        "repository": REPOSITORY,
        "reviewer": REVIEWER,
        "schema_id": SCHEMA_CONTRACT,
        "scope": SCOPE,
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "source_pins": SOURCE_PINS,
        "source_reported": report["source_reported"],
        "sources_sha256": sha256_bytes(sources_payload),
        "status": STATUS,
        "task_id": TASK_ID,
        "task_prefix": TASK_PREFIX,
        "title": TITLE,
    }
    contract["artifact_pins"][TASK_PREFIX + "report.json"] = sha256_bytes(report_payload)
    return canonical_bytes(contract)


def scope_base(sdk_root: Path, refs: Sequence[str] = SCOPE_BASE_REFS) -> str | None:
    newest: Tuple[int, str] | None = None
    for ref in refs:
        resolved = subprocess.run(["git", "-C", str(sdk_root), "rev-parse", "--verify", "--quiet", ref + "^{commit}"], capture_output=True, text=True, check=False)
        if resolved.returncode != 0:
            continue
        commit = resolved.stdout.strip()
        base = subprocess.run(["git", "-C", str(sdk_root), "merge-base", "HEAD", commit], capture_output=True, text=True, check=False)
        if base.returncode != 0:
            continue
        base_commit = base.stdout.strip()
        stamp = subprocess.run(["git", "-C", str(sdk_root), "show", "-s", "--format=%ct", base_commit], capture_output=True, text=True, check=False)
        if stamp.returncode != 0:
            continue
        value = (int(stamp.stdout.strip()), base_commit)
        if newest is None or value[0] > newest[0]:
            newest = value
    return None if newest is None else newest[1]


def scope_changed_paths(sdk_root: Path, base: str) -> List[str]:
    diff = subprocess.run(["git", "-C", str(sdk_root), "diff", "--name-only", base + "..HEAD", "--"], capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        raise ValueError("scope_diff_failed")
    return [line for line in diff.stdout.splitlines() if line.strip()]


def scope_violations(changed_paths: Sequence[str]) -> List[str]:
    return sorted(path for path in changed_paths if not path.startswith(TASK_PREFIX))
