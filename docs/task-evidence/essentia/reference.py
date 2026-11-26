# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for the SDK-ESSENTIA row.

The candidate is the Essentia music-analysis library, reported by the pinned
note as a BPM/beat/rhythm factor provider under AGPL-3.0 ("strong copyleft,
including network use"). No Essentia source, Python module, model, weight,
corpus, license text or runtime is present, downloaded or executed here.

This module is an original admission gate plus a small onset/factor harness.
The harness only exercises the Rate acceptance profile and the fail-closed
rejection paths. It is NOT Essentia, does not reproduce Essentia, and never
produces candidate output. Every result is proposal-only and non-qualifying.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = "audio-sdk/essentia-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/essentia-contract/0.1"
TASK = "SDK-ESSENTIA"
COMPONENT = "essentia"
MODE = "feasibility"
VERIFICATION_PROFILE = "Rate"
BRANCH = "swarm/SDK-ESSENTIA"
BASE_COMMIT = "23526250a3a0a66c1f93089ff6fb697b5e776965"
TASK_PREFIX = "docs/task-evidence/essentia/"
STATUS = "proposal_only_not_qualified"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS

# Reported by the pinned provenance note only. Nothing here is a local
# measurement and no version, URL or model name is invented.
REPORTED_UPSTREAM_LICENSE = "AGPL-3.0"
REPORTED_LICENSE_RESTRICTION = (
    "Strong copyleft, including network use; reported as not usable in a "
    "closed-source product."
)
REPORTED_ROLE = "BPM, beat and rhythm factor provider"
REPORTED_ONLINE_CAPABILITY = "some"

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "Essentia",
    "mode": MODE,
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

# Bounded, read-only probes. Paths are labels; no absolute local path is
# exported. Home-relative labels are expanded for the probe only.
SOURCE_CANDIDATE_PATHS = (
    "third_party/essentia",
    "third_party/essentia-2.1",
    "deps/essentia",
    "adapters/essentia",
    "research/essentia",
    "research/repos/essentia",
    "data/models/essentia",
    "~/essentia",
    "~/.essentia",
    "~/code/essentia",
)
SOURCE_MARKERS = (
    "essentia.conf", "src", "COPYING", "COPYING.txt", "README.md",
    "wscript", "CMakeLists.txt",
)
RUNTIME_CANDIDATE_PATHS = (
    "data/envs/essentia",
    "data/runtime/essentia",
    "data/runtime/essentia-python",
    "~/essentia-venv",
    "~/.essentia-runtime",
)
RUNTIME_CLI = ("essentia", "essentia_extractor")
FIXTURE_CANDIDATE_PATHS = (
    "data/corpora/essentia",
    "data/fixtures/essentia",
    "research/essentia/fixture",
    "research/essentia-beats",
)
FIXTURE_MARKERS = (".wav", ".flac", ".npy", ".json", ".csv")

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "exact Essentia source checkout",
        "required": (
            "A local Essentia checkout at a recorded full revision with a "
            "read-only tree digest, file count and the upstream license file"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "AGPL-3.0 text and outbound rights decision",
        "required": (
            "The byte-identical upstream license text with SHA-256 plus a "
            "written decision that explicitly permits AGPL-3.0 network-use "
            "obligations inside this Apache-2.0/MPL-2.0 SDK distribution and "
            "any adapter output"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "pinned runtime and Python bindings",
        "required": (
            "A hash-pinned C++/Python runtime or binding build with a "
            "dependency lock, reproducible build record and an install/import "
            "parity record on this macOS/Python host"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "pinned configuration, algorithms and models",
        "required": (
            "The exact extractor configuration and any model or weight files "
            "with their own immutable digests and separate model-license "
            "review"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "rights-cleared matched tempo/beat corpus",
        "required": (
            "A permitted held-out speech and music cohort with beat, tempo "
            "and onset annotations, matched controls and an authorized "
            "scoring protocol"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "independent review and release package",
        "required": (
            "An independent exact-head review of the rights decision, adapter "
            "boundary, factor mapping and workload evidence, plus release "
            "approval before any support claim"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
)

GATES = (
    {
        "id": "RG-01",
        "gate": "exact_upstream_source_revision_and_license_pin",
        "status": "blocked",
        "reason": (
            "No local Essentia checkout exists; the revision, tree digest, "
            "file count and upstream license file are absent and no source "
            "path is pinned."),
        "reopen": (
            "Stage the exact Essentia revision with a read-only tree digest "
            "and license file, pin every required path, and record the "
            "extractor configuration before reading source."),
    },
    {
        "id": "RG-02",
        "gate": "agpl_network_use_and_outbound_compatibility_decision",
        "status": "blocked",
        "reason": (
            "The pinned note reports AGPL-3.0 with strong copyleft including "
            "network use. No local license text and no written decision "
            "permitting those obligations in this Apache-2.0/MPL-2.0 SDK "
            "distribution or adapter output exists."),
        "reopen": (
            "Obtain the exact license text, record its SHA-256, and secure a "
            "written rights decision that states whether and how AGPL-3.0 "
            "source, network-use and redistribution obligations are met, or "
            "record a final rejection and close the task."),
    },
    {
        "id": "RG-03",
        "gate": "pinned_runtime_and_python_bindings",
        "status": "blocked",
        "reason": (
            "No Essentia Python module, CLI, C++ runtime, dependency lock or "
            "reproducible binding build exists on this host, so no "
            "install/import parity can be shown."),
        "reopen": (
            "Provide a hash-pinned, reproducible runtime or binding build "
            "with a dependency lock and an install/import parity record on "
            "the target host."),
    },
    {
        "id": "RG-04",
        "gate": "pinned_models_configuration_and_model_license",
        "status": "blocked",
        "reason": (
            "No extractor configuration, model name, weight file or "
            "model-license review is present. Model and code terms are "
            "separate gates and neither is recorded locally."),
        "reopen": (
            "Pin the exact extractor configuration and every model or weight "
            "digest, review model-specific terms independently, and reject "
            "any non-commercial or unverified asset."),
    },
    {
        "id": "RG-05",
        "gate": "beat_tempo_onset_reproduction_with_reset_and_drain",
        "status": "blocked",
        "reason": (
            "No candidate instance exists, so beat, tempo and onset outputs, "
            "parameter identity, source intervals, reset and finite drain "
            "were not reproduced."),
        "reopen": (
            "With pinned source, configuration and runtime, reproduce factor "
            "outputs, source intervals, parameter identity, reset and finite "
            "drain against a matched cohort."),
    },
    {
        "id": "RG-06",
        "gate": "rate_acceptance_matrix",
        "status": "blocked",
        "reason": (
            "The Rate profile requires source/output mapping, duration, "
            "pitch, transient audibility, playback buffering, 1x and rate "
            "changes, unfamiliar speech, music, silence, rebuffer, drift and "
            "the final partial window; only a local synthetic harness "
            "control ran, with no candidate output."),
        "reopen": (
            "Run the full Rate matrix with the candidate runtime, retain every "
            "failure and nonfinite case, and record duration, factor mapping, "
            "pitch, transient audibility, buffering and final-window behavior "
            "with tolerances agreed before scoring."),
    },
    {
        "id": "RG-07",
        "gate": "paced_device_timing_memory_and_callback",
        "status": "blocked",
        "reason": (
            "No paced workload, callback suitability, device timing, memory, "
            "CPU, availability or deadline measurement exists."),
        "reopen": (
            "Measure paced target-host availability, deadline misses, memory, "
            "CPU and callback suitability with an exact runtime and telemetry "
            "record."),
    },
    {
        "id": "RG-08",
        "gate": "adapter_intake_benchmark_and_release",
        "status": "blocked",
        "reason": (
            "No approved factor/analysis adapter, provider intake, optional "
            "registration, public-surface decision, benchmark validation, "
            "authorized listening, independent exact-head review or release "
            "approval exists."),
        "reopen": (
            "Complete the rights, runtime and corpus decisions, implement any "
            "adapter only behind explicit caller opt-in with no default or "
            "fallback registration, validate a benchmark bundle, run "
            "authorized listening where permitted, and obtain independent "
            "review and release approval."),
    },
)

RELEASE_GATE_COUNT = 8  # exactly eight blocked release gates

UPSTREAM_BLOCKER = {
    "status": "blocked_source_rights_runtime_models_and_fixtures_absent",
    "artifact": (
        "Essentia source, AGPL-3.0 rights decision, pinned runtime or Python "
        "bindings, configuration and models, and a rights-cleared matched "
        "tempo/beat corpus"),
    "source": {
        "status": "absent",
        "repository": None,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
    },
    "license": {
        "status": "blocked_agpl_network_use_and_outbound_not_approved",
        "reported_name": REPORTED_UPSTREAM_LICENSE,
        "reported_restriction": REPORTED_LICENSE_RESTRICTION,
        "license_text_present": False,
        "license_text_sha256": None,
        "network_use_approved": False,
        "outbound_compatibility_approved": False,
        "redistribution_approved": False,
        "review": "blocked",
    },
    "runtime": {
        "status": "absent",
        "python_module": None,
        "cli": None,
        "build_lock": None,
        "sha256": None,
        "required": [
            "hash-pinned runtime or Python binding build",
            "dependency lock",
            "reproducible build record",
            "install and import parity record",
        ],
    },
    "models": {
        "status": "absent",
        "names": None,
        "license": None,
        "sha256": None,
        "rights_reviewed": False,
        "required": [
            "exact extractor configuration",
            "model and weight digests",
            "separate model-license review",
        ],
    },
    "fixture": {
        "status": "absent",
        "corpus_rights": False,
        "annotations_present": False,
        "sha256": None,
        "required": (
            "Permitted held-out speech and music audio with beat, tempo and "
            "onset labels plus matched controls"),
    },
    "source_digest": None,
    "license_digest": None,
    "runtime_digest": None,
    "models_digest": None,
    "fixture_digest": None,
    "pinned_revision": None,
    "rights_requirement": (
        "AGPL-3.0 is a strong-copyleft license with network-use obligations. "
        "Use in this Apache-2.0/MPL-2.0 SDK distribution, in any optional "
        "adapter and in any served output requires an explicit written "
        "rights decision. A reported license name is not a rights grant."),
    "workspace_search": (
        "A bounded, read-only probe of named workspace and home paths plus "
        "the Python module registry and CLI PATH found no Essentia source, "
        "license text, runtime, CLI, model, weight or corpus. Nothing was "
        "cloned, downloaded, extracted, ported or reconstructed."),
    "not_attempted": [
        "clone or download any Essentia source or package",
        "install Essentia or any Python binding",
        "read or port any extractor, model or weight",
        "run any candidate beat, tempo or onset extraction",
        "read any real speech or music corpus",
        "produce, modify or play any audio",
    ],
    "reopen": (
        "To reopen, supply A1-A6: the exact pinned source and license text, a "
        "written AGPL-3.0 compatibility decision for this distribution, a "
        "hash-pinned runtime or binding build, pinned configuration and model "
        "rights, a rights-cleared matched corpus, and independent review."),
    "no_upstream_parity_claim": True,
}

EXTERNAL_BOUNDARY = {
    "vendor": "Essentia project",
    "component": "Essentia",
    "component_version": None,
    "distribution_model": "C++ analysis library with Python bindings",
    "eligible_target": None,
    "host_target": "macOS / Python 3 workspace",
    "host_target_eligible": False,
    "license_reported": REPORTED_UPSTREAM_LICENSE,
    "reported_restriction": REPORTED_LICENSE_RESTRICTION,
    "license_text_present": False,
    "local_runtime_present": False,
    "documented": True,
    "adapter_implemented": False,
    "adapter_default_registration": False,
    "automatic_discovery": False,
    "fallback": "none",
    "vendor_output_present": False,
    "vendor_claims_separate_from_local_measurements": True,
    "note": (
        "Only the pinned note's factor role, license finding and 'some' "
        "online capability are recorded. No version, rate, frame, channel, "
        "model, threshold or vendor measurement is inferred or generalized."),
}

INVARIANTS = [
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/essentia/ is touched.",
    "The reference is a task-local admission gate and harness, not Essentia.",
    "Installed v0 has no analysis, event or audio-derived factor output type.",
    "All harness stimuli are analytic or seeded synthetic; no candidate runtime is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
]

NON_CLAIMS = [
    "No Essentia source, header, configuration, Python module, binary, model or license text is included.",
    "No Essentia beat, tempo, onset or factor extraction is implemented, approximated, simulated or run.",
    "No vendor score, rate, frame, channel, model or platform claim is reproduced or generalized.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, fixture, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No source-reported characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
]

# ---------------------------------------------------------------------------
# Harness constants. These describe the local synthetic harness only.
# ---------------------------------------------------------------------------
LOG_FLOOR = 1.0e-12
ONSET_THRESHOLD = 0.35
BASELINE_ALPHA = 0.20
MIN_ONSET_GAP_FRAMES = 7
FACTOR_MIN_BPM_X100 = 6000
FACTOR_MAX_BPM_X100 = 18000
FACTOR_STABILITY_SPREAD_X100 = 100
MIN_IOIS_FOR_FACTOR = 4
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 1.0
FINAL_VALID_SAMPLES = 137
UINT64_MAX = 2**64 - 1
INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
})
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)


class EvidenceError(ValueError):
    """Deterministic evidence failure carrying a machine-readable code."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code or self.__class__.__name__


class ConfigError(EvidenceError):
    """Strict contract or board configuration is not as expected."""


class InputError(EvidenceError):
    """A request or frame is invalid; no state is advanced."""


class JsonError(EvidenceError):
    """Strict JSON parsing rejected the input."""


class ArtifactsAbsent(EvidenceError):
    """The licensed candidate artifacts and rights are absent."""


# ---------------------------------------------------------------------------
# Canonical JSON and digests
# ---------------------------------------------------------------------------
def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON: sorted keys, compact separators, no NaN/Infinity."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("duplicate JSON key: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("nonfinite JSON constant: " + token, "NONFINITE_JSON")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except JsonError:
        raise
    except (ValueError, TypeError) as error:
        raise JsonError("invalid JSON: " + str(error), "INVALID_JSON")


def strict_json_object_loads(text: str) -> Dict[str, Any]:
    value = strict_json_loads(text)
    if not isinstance(value, dict):
        raise JsonError("JSON root is not an object", "JSON_NOT_OBJECT")
    return value


def strict_json_load(path: Path) -> Dict[str, Any]:
    return strict_json_object_loads(Path(path).read_text(encoding="utf-8"))


def finite_json(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(finite_json(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and finite_json(item)
                   for key, item in value.items())
    return False


def tensor_digest(samples: Iterable[float]) -> str:
    return sha256_bytes(b"".join(
        _float32_bytes(float(value)) for value in samples))


def _float32_bytes(value: float) -> bytes:
    import struct
    return struct.pack("<f", value)


def peak_abs(samples: Sequence[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(float(value) ** 2 for value in samples) /
                     len(samples))


def _r(value: float, places: int = 9) -> float:
    return round(float(value), places)


def llround(value: float) -> int:
    """C llround semantics: halves away from zero."""
    return (int(math.floor(value + 0.5)) if value >= 0.0
            else int(math.ceil(value - 0.5)))


# ---------------------------------------------------------------------------
# Bounded read-only probes
# ---------------------------------------------------------------------------
def _probe_path(label: str) -> Path:
    if label.startswith("~"):
        return Path(label).expanduser()
    return WORKSPACE / label


def _exists(label: str) -> bool:
    try:
        return _probe_path(label).exists()
    except OSError:
        return False


def _found_paths(labels: Sequence[str]) -> List[str]:
    return [label for label in labels if _exists(label)]


def _module_present(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _marker_names(label: str) -> List[str]:
    base = _probe_path(label)
    if not base.is_dir():
        return []
    try:
        entries = sorted(path.name for path in base.iterdir())
    except OSError:
        return []
    return [name for name in entries if name in SOURCE_MARKERS][:32]


def source_probe() -> Dict[str, Any]:
    found = _found_paths(SOURCE_CANDIDATE_PATHS)
    markers: List[str] = []
    for label in found:
        markers.extend(_marker_names(label))
    present = bool(found)
    return {
        "status": "present_unpinned" if present else "absent",
        "component": COMPONENT,
        "present": present,
        "pinned": False,
        "found": found,
        "checked_paths": list(SOURCE_CANDIDATE_PATHS),
        "markers_found": sorted(set(markers)),
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "note": (
            "Bounded read-only path probe. No clone, download, extraction, "
            "port or reverse engineering occurred."),
    }


def runtime_probe() -> Dict[str, Any]:
    labels = _found_paths(RUNTIME_CANDIDATE_PATHS)
    module_found = _module_present("essentia")
    cli_found = {}
    for name in RUNTIME_CLI:
        try:
            cli_found[name] = shutil.which(name) is not None
        except OSError:
            cli_found[name] = False
    present = module_found or any(cli_found.values()) or bool(labels)
    return {
        "status": "present_unpinned" if present else "absent",
        "present": present,
        "python_module_found": module_found,
        "cli_found": cli_found,
        "found": labels,
        "checked_paths": list(RUNTIME_CANDIDATE_PATHS),
        "build_lock": None,
        "sha256": None,
        "pinned": False,
        "note": (
            "The Python module registry and CLI PATH were queried without "
            "importing any candidate module; nothing was installed or run."),
    }


def license_probe(source: Dict[str, Any] | None = None) -> Dict[str, Any]:
    block = source if source is not None else source_probe()
    markers = block.get("markers_found", [])
    text_present = any(name.startswith("COPYING") or name.startswith("LICENSE")
                       for name in markers)
    return {
        "status": "absent_and_unapproved",
        "reported_name": REPORTED_UPSTREAM_LICENSE,
        "reported_restriction": REPORTED_LICENSE_RESTRICTION,
        "license_text_present": text_present,
        "license_text_sha256": None,
        "network_use_approved": False,
        "outbound_compatibility_approved": False,
        "redistribution_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": (
            "Only a source-reported license name exists; no byte-identical "
            "license text, digest or written decision is present."),
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_outbound_incompatible",
        "sdk_outbound_licenses": ["Apache-2.0", "MPL-2.0"],
        "reported_upstream_license": REPORTED_UPSTREAM_LICENSE,
        "license_text_present": False,
        "license_text_sha256": None,
        "network_use_approved": False,
        "outbound_compatibility_approved": False,
        "redistribution_approved": False,
        "input_corpus_rights": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": (
            "The SDK outbound map is Apache-2.0/MPL-2.0 per LICENSE.md. A "
            "reported AGPL-3.0 dependency with network-use obligations has "
            "no recorded compatibility decision, so adapter work is blocked."),
    }


def fixture_probe() -> Dict[str, Any]:
    found = _found_paths(FIXTURE_CANDIDATE_PATHS)
    return {
        "status": "present_unpinned" if found else "absent",
        "present": bool(found),
        "found": found,
        "checked_paths": list(FIXTURE_CANDIDATE_PATHS),
        "markers": list(FIXTURE_MARKERS),
        "corpus_rights": False,
        "annotations_present": False,
        "sha256": None,
        "note": (
            "No permitted tempo, beat or onset corpus with provenance and "
            "annotations was found or read."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "component": COMPONENT,
        "candidate_output": False,
        "measured_here": False,
        "verified_here": False,
        "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
        "installed_v0_channels": CHANNELS,
        "installed_v0_frame_samples": FRAME_SAMPLES,
        "installed_v0_sample_format": SAMPLE_FORMAT,
        "declared_sample_rate_hz": None,
        "declared_frame_samples": None,
        "declared_channels": None,
        "declared_offline_or_online": None,
        "source_reported_role": REPORTED_ROLE,
        "source_reported_license": REPORTED_UPSTREAM_LICENSE,
        "source_reported_online_capability": REPORTED_ONLINE_CAPABILITY,
        "analysis_surface_exists_in_v0": False,
        "factor_or_event_surface_exists_in_v0": False,
        "v0_can_represent_declared_input": False,
        "note": (
            "The pinned note records only a BPM/beat/rhythm factor role and "
            "a reported online capability. It records no rate, frame, "
            "channel, model or threshold; none was invented. Installed v0 "
            "produces only 160-sample audio frames and has no analysis or "
            "factor output type."),
    }


def boundary() -> Dict[str, Any]:
    return {
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "abi_major": ABI_MAJOR,
            "abi_minor": ABI_MINOR,
        },
        "installed_v0_unchanged": True,
        "public_api_abi_changed": False,
        "headers_changed": False,
        "descriptor_registry_changed": False,
        "descriptor_registration": False,
        "descriptor_default_changed": False,
        "provider_registered": False,
        "enabled_by_default": False,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "shared_cmake_changed": False,
        "ci_changed": False,
        "board_or_handoff_changed": False,
        "real_corpus_or_weights": False,
        "benchmark_claim": False,
        "release_claim": False,
        "public_c_boundary": (
            "not used: no C provider, header or installed target"),
    }


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": DECISION,
        "processor_exposure": "deferred_until_rights_and_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": QUALIFICATION_STATUS,
        "upstream_parity": False,
    }


def source_evidence_statements() -> List[str]:
    return [
        (
            "cpp-library/pipeline-validation/playback-speed-candidates.md "
            "records Essentia as a BPM, beat and rhythm factor provider with "
            "AGPL-3.0 licensing, strong copyleft including network use, and "
            "no closed-source use."),
        (
            "the same note records only 'some' online capability for the "
            "candidate and does not state a version, sample rate, frame size, "
            "channel count, model, threshold or vendor measurement."),
        (
            "plan/INVENTORY.json assigns essentia to 'Rate and content', the "
            "rate verification profile, disposition sdk-reference and an "
            "evidence status of considered."),
        (
            "plan/INVENTORY.json records the same finding for essentia: "
            "strong copyleft, including network use."),
        (
            "plan/audio-sdk/README.md requires runnable source, exact assets, "
            "permitted scope and matched evidence before a caller-supplied "
            "reference or opt-in factor adapter is added."),
        (
            "plan/swarm/VERIFICATION.md requires source/output mapping, "
            "duration, pitch, transient audibility and playback buffering "
            "across 1x, rate changes, unfamiliar speech, music, silence, "
            "rebuffer, drift and the final partial window."),
        (
            "No local Essentia source, license text, runtime, Python module, "
            "CLI, model, weight or matched corpus exists; nothing was cloned, "
            "downloaded, installed, ported or reconstructed."),
    ]


# ---------------------------------------------------------------------------
# Strict request validation and the fail-closed candidate gate
# ---------------------------------------------------------------------------
def _require_int(value: Any, code: str, low: int, high: int) -> int:
    if (not isinstance(value, int) or isinstance(value, bool)
            or not low <= value <= high):
        raise InputError("invalid integer field: " + code, "INVALID_INTEGER")
    return value


def _validate_samples(samples: Any) -> List[float]:
    if not isinstance(samples, list):
        raise InputError("samples must be a JSON array", "INVALID_SAMPLES")
    if len(samples) != FRAME_SAMPLES:
        raise InputError("samples must contain exactly 160 values",
                         "FRAME_COUNT_MISMATCH")
    result: List[float] = []
    for value in samples:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("samples must be numeric", "NON_NUMERIC_SAMPLE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("samples must be finite", "NONFINITE_SAMPLE")
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("sample exceeds the harness input bound",
                             "SAMPLE_OUT_OF_BOUNDS")
        result.append(number)
    return result


def validate_request(request: Any) -> Dict[str, Any]:
    """Validate a factor-boundary request strictly; no implicit defaults."""
    if not isinstance(request, dict):
        raise InputError("request must be a JSON object", "REQUEST_NOT_OBJECT")
    keys = set(request)
    if keys != REQUEST_KEYS:
        missing = sorted(REQUEST_KEYS - keys)
        extra = sorted(keys - REQUEST_KEYS)
        raise InputError("strict key mismatch: missing=" + ",".join(missing)
                         + " extra=" + ",".join(extra), "STRICT_KEYS")
    if request["candidate"] != COMPONENT:
        raise InputError("unknown candidate", "UNKNOWN_CANDIDATE")
    _require_int(request["sample_rate_hz"], "sample_rate_hz",
                 SAMPLE_RATE_HZ, SAMPLE_RATE_HZ)
    _require_int(request["channels"], "channels", CHANNELS, CHANNELS)
    _require_int(request["frame_samples"], "frame_samples",
                 FRAME_SAMPLES, FRAME_SAMPLES)
    _require_int(request["epoch"], "epoch", 0, UINT64_MAX)
    _require_int(request["first_input_sample"], "first_input_sample",
                 INT64_MIN, INT64_MAX)
    if request["lifecycle"] not in LIFECYCLES:
        raise InputError("invalid lifecycle", "INVALID_LIFECYCLE")
    mode = request["execution_mode"]
    if (not isinstance(mode, int) or isinstance(mode, bool)
            or mode not in EXECUTION_MODES):
        raise InputError("invalid execution mode", "INVALID_EXECUTION_MODE")
    samples = _validate_samples(request["samples"])
    return {
        "candidate": COMPONENT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "samples": samples,
        "epoch": request["epoch"],
        "first_input_sample": request["first_input_sample"],
        "lifecycle": request["lifecycle"],
        "execution_mode": mode,
    }


def probe_candidate(request: Any) -> None:
    """Validate, then fail closed: the licensed candidate is absent."""
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: Essentia source, an approved AGPL-3.0 rights "
        "decision, a pinned runtime, configuration and models, and a "
        "rights-cleared matched corpus are not present; no processing is "
        "performed", "ARTIFACTS_ABSENT")


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": COMPONENT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def _adverse_request_specs() -> List[Tuple[str, str, Dict[str, Any]]]:
    base = _base_request()

    def mutate(**changes: Any) -> Dict[str, Any]:
        request = dict(base)
        request.update(changes)
        return request

    specs: List[Tuple[str, str, Dict[str, Any]]] = [
        ("REQ-01", "candidate=other", mutate(candidate="other")),
        ("REQ-02", "sample_rate_hz=44100", mutate(sample_rate_hz=44100)),
        ("REQ-03", "sample_rate_hz=48000", mutate(sample_rate_hz=48000)),
        ("REQ-04", "sample_rate_hz=0", mutate(sample_rate_hz=0)),
        ("REQ-05", "channels=2", mutate(channels=2)),
        ("REQ-06", "channels=0", mutate(channels=0)),
        ("REQ-07", "frame_samples=159", mutate(frame_samples=159)),
        ("REQ-08", "frame_samples=512", mutate(frame_samples=512)),
        ("REQ-09", "samples short (159)", mutate(samples=[0.0] * 159)),
        ("REQ-10", "samples long (161)", mutate(samples=[0.0] * 161)),
        ("REQ-11", "samples not an array", mutate(samples="0" * 160)),
        ("REQ-12", "samples contain NaN",
         mutate(samples=[float("nan")] + [0.0] * 159)),
        ("REQ-13", "samples contain +Infinity",
         mutate(samples=[float("inf")] + [0.0] * 159)),
        ("REQ-14", "samples contain -Infinity",
         mutate(samples=[float("-inf")] + [0.0] * 159)),
        ("REQ-15", "sample exceeds bound",
         mutate(samples=[4.0001] + [0.0] * 159)),
        ("REQ-16", "sample is a string",
         mutate(samples=["0"] + [0.0] * 159)),
        ("REQ-17", "sample is a bool",
         mutate(samples=[True] + [0.0] * 159)),
        ("REQ-18", "epoch is a float", mutate(epoch=1.0)),
        ("REQ-19", "epoch is a bool", mutate(epoch=True)),
        ("REQ-20", "epoch is negative", mutate(epoch=-1)),
        ("REQ-21", "epoch exceeds uint64", mutate(epoch=UINT64_MAX + 1)),
        ("REQ-22", "first_input_sample is a float",
         mutate(first_input_sample=0.5)),
        ("REQ-23", "first_input_sample below int64",
         mutate(first_input_sample=INT64_MIN - 1)),
        ("REQ-24", "first_input_sample above int64",
         mutate(first_input_sample=INT64_MAX + 1)),
        ("REQ-25", "lifecycle=closed", mutate(lifecycle="closed")),
        ("REQ-26", "lifecycle missing", mutate(lifecycle=None)),
        ("REQ-27", "execution_mode=0", mutate(execution_mode=0)),
        ("REQ-28", "execution_mode=4", mutate(execution_mode=4)),
        ("REQ-29", "execution_mode is a string", mutate(execution_mode="1")),
        ("REQ-30", "execution_mode is a bool", mutate(execution_mode=True)),
    ]
    extra = dict(base)
    extra["unexpected"] = 1
    specs.append(("REQ-31", "unexpected extra key", extra))
    missing = dict(base)
    del missing["epoch"]
    specs.append(("REQ-32", "missing required key", missing))
    specs.append(("REQ-33", "request is not an object", "not-an-object"))
    return specs


def adverse_requests() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    accepted = 0
    for case_id, label, request in _adverse_request_specs():
        try:
            validate_request(request)
        except InputError as error:
            cases.append({
                "id": case_id,
                "input": label,
                "status": "rejected",
                "code": error.code,
                "accepted": False,
                "qualifies_candidate": False,
            })
        else:
            accepted += 1
            cases.append({
                "id": case_id,
                "input": label,
                "status": "accepted_in_candidate_gate",
                "code": None,
                "accepted": True,
                "qualifies_candidate": False,
            })
    return {
        "case_count": len(cases),
        "accepted_count": accepted,
        "all_rejected": accepted == 0,
        "cases": cases,
        "metrics": None,
        "note": (
            "Every invalid request is rejected before any artifact check; a "
            "structurally valid request still reaches the fail-closed "
            "ARTIFACTS_ABSENT gate."),
    }


def adverse_json() -> Dict[str, Any]:
    samples = [
        ("JSN-01", "duplicate JSON key",
         '{"a":1,"a":2}'),
        ("JSN-02", "NaN JSON constant",
         '{"value":NaN}'),
        ("JSN-03", "Infinity JSON constant",
         '{"value":Infinity}'),
        ("JSN-04", "top-level array",
         '[{"a":1}]'),
        ("JSN-05", "trailing garbage",
         '{"a":1} trailing'),
        ("JSN-06", "unquoted key",
         '{a:1}'),
        ("JSN-07", "single-quoted string",
         "{'a':'b'}"),
    ]
    cases: List[Dict[str, Any]] = []
    accepted = 0
    for case_id, label, payload in samples:
        try:
            value = strict_json_object_loads(payload)
        except JsonError as error:
            cases.append({
                "id": case_id,
                "input": label,
                "status": "rejected",
                "code": error.code,
                "accepted": False,
                "qualifies_candidate": False,
            })
        else:
            accepted += 1
            cases.append({
                "id": case_id,
                "input": label,
                "status": "accepted",
                "code": None,
                "accepted": True,
                "value_type": type(value).__name__,
                "qualifies_candidate": False,
            })
    return {
        "case_count": len(cases),
        "accepted_count": accepted,
        "all_rejected": accepted == 0,
        "cases": cases,
        "metrics": None,
    }


def missing_result(fixture: str) -> Dict[str, Any]:
    return {
        "fixture": fixture,
        "status": "blocked",
        "reason": "no candidate runtime or rights decision; no result exists",
        "metrics": None,
        "qualifies_candidate": False,
    }


# ---------------------------------------------------------------------------
# Synthetic stimulus harness (not the candidate)
# ---------------------------------------------------------------------------
class _Lcg:
    def __init__(self, seed: int):
        self.state = seed & 0x7FFFFFFF

    def next(self) -> float:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return (2.0 * self.state / 0x7FFFFFFF) - 1.0


def _tone_burst(length: int, amplitude: float,
                frequency_hz: float = 150.0) -> List[float]:
    return [amplitude * (1.0 - index / length)
            * math.sin(2.0 * math.pi * frequency_hz * index / SAMPLE_RATE_HZ)
            for index in range(length)]


def _add_burst(signal: List[float], start: int, burst: Sequence[float]) -> None:
    for offset, value in enumerate(burst):
        position = start + offset
        if position >= len(signal):
            break
        signal[position] += value


def stimulus_specs() -> Dict[str, Dict[str, Any]]:
    return {
        "music_1x": {
            "kind": "periodic", "length_samples": 9 * 9600 + 160,
            "period_samples": 9600, "beats": 9, "amplitude_milli": 500,
            "noise_milli": 40, "noise_seed": 11,
        },
        "rate_0_8": {
            "kind": "periodic", "length_samples": 7 * 12000 + 160,
            "period_samples": 12000, "beats": 7, "amplitude_milli": 500,
            "noise_milli": 40, "noise_seed": 23,
        },
        "rate_1_2": {
            "kind": "periodic", "length_samples": 11 * 8000 + 160,
            "period_samples": 8000, "beats": 11, "amplitude_milli": 500,
            "noise_milli": 40, "noise_seed": 37,
        },
        "speech_like": {
            "kind": "irregular", "length_samples": 80000,
            "starts_frames": [4, 26, 67, 93, 150, 181, 249, 273, 321, 382,
                              411, 463, 492],
            "amplitude_milli": 400, "noise_milli": 30, "noise_seed": 41,
        },
        "silence": {"kind": "silence", "length_samples": 16000},
        "rebuffer": {
            "kind": "rebuffer", "period_samples": 9600,
            "beats_before_gap": 5, "beats_after_gap": 5,
            "gap_samples": 24000, "amplitude_milli": 500,
        },
        "drift": {
            "kind": "drift", "periods_frames": [95, 90, 85, 80, 75, 70, 65],
            "amplitude_milli": 500,
        },
        "final_partial": {
            "kind": "final_partial", "length_samples": 400 * 160 + 137,
            "onset_sample": 62000, "amplitude_milli": 500,
        },
    }


def generate_stimulus(spec: Dict[str, Any]) -> Tuple[List[float], List[Tuple[int, int]]]:
    kind = spec["kind"]
    gaps: List[Tuple[int, int]] = []
    if kind == "silence":
        length = int(spec["length_samples"])
        return [0.0] * length, gaps
    if kind == "periodic":
        length = int(spec["length_samples"])
        signal = [0.0] * length
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        for beat in range(int(spec["beats"])):
            _add_burst(signal, beat * int(spec["period_samples"]), burst)
        noise = _Lcg(int(spec["noise_seed"]))
        amplitude = spec["noise_milli"] / 1000.0
        if amplitude:
            for index in range(length):
                signal[index] += noise.next() * amplitude
    elif kind == "irregular":
        length = int(spec["length_samples"])
        signal = [0.0] * length
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        for frame in spec["starts_frames"]:
            _add_burst(signal, int(frame) * FRAME_SAMPLES, burst)
        noise = _Lcg(int(spec["noise_seed"]))
        amplitude = spec["noise_milli"] / 1000.0
        if amplitude:
            for index in range(length):
                signal[index] += noise.next() * amplitude
    elif kind == "rebuffer":
        period = int(spec["period_samples"])
        before = int(spec["beats_before_gap"])
        after = int(spec["beats_after_gap"])
        gap = int(spec["gap_samples"])
        gap_start = before * period
        gap_end = gap_start + gap
        gaps.append((gap_start, gap_end))
        length = gap_end + after * period + FRAME_SAMPLES
        signal = [0.0] * length
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        for beat in range(before):
            _add_burst(signal, beat * period, burst)
        for beat in range(after):
            _add_burst(signal, gap_end + beat * period, burst)
    elif kind == "drift":
        periods = [int(value) for value in spec["periods_frames"]]
        length = sum(periods) * FRAME_SAMPLES + FRAME_SAMPLES
        signal = [0.0] * length
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        position = 0
        for period in periods:
            _add_burst(signal, position, burst)
            position += period * FRAME_SAMPLES
        _add_burst(signal, position, burst)
    elif kind == "final_partial":
        length = int(spec["length_samples"])
        if length % FRAME_SAMPLES != FINAL_VALID_SAMPLES:
            raise ConfigError("final partial stimulus has the wrong length")
        signal = [0.0] * length
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        _add_burst(signal, int(spec["onset_sample"]), burst)
    else:
        raise ConfigError("unknown stimulus kind: " + str(kind))
    if not finite_json(signal):
        raise ConfigError("generated stimulus is nonfinite")
    if peak_abs(signal) > MAX_ABS_STIMULUS + 1e-12:
        raise ConfigError("generated stimulus exceeds the amplitude bound")
    return signal, gaps


class FactorEvent:
    """Source-anchored analysis event in exact integer coordinates."""

    __slots__ = ("source_start", "source_end", "frame_index", "epoch",
                 "strength_milli", "available_monotonic_ns", "capture_first_ns")

    def __init__(self, source_start: int, source_end: int, frame_index: int,
                 epoch: int, strength_milli: int, available_monotonic_ns: int,
                 capture_first_ns: int):
        self.source_start = source_start
        self.source_end = source_end
        self.frame_index = frame_index
        self.epoch = epoch
        self.strength_milli = strength_milli
        self.available_monotonic_ns = available_monotonic_ns
        self.capture_first_ns = capture_first_ns

    def as_dict(self) -> Dict[str, Any]:
        return {
            "source_start": str(self.source_start),
            "source_end": str(self.source_end),
            "frame_index": str(self.frame_index),
            "epoch": str(self.epoch),
            "strength_milli": str(self.strength_milli),
            "available_monotonic_ns": str(self.available_monotonic_ns),
            "capture_first_ns": str(self.capture_first_ns),
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FactorEvent) and self.as_dict() == other.as_dict()


class OnsetAnalyzer:
    """Causal, frame-clocked harness analyzer with explicit rejection."""

    def __init__(self, epoch: int = 1):
        _require_int(epoch, "epoch", 0, UINT64_MAX)
        self.epoch = epoch
        self.frame_index = 0
        self.baseline = math.log(LOG_FLOOR)
        self.last_onset_frame: int | None = None
        self.events: List[FactorEvent] = []
        self.rejections: List[str] = []

    @property
    def state_digest(self) -> str:
        return sha256_bytes(canonical_bytes({
            "frame_index": str(self.frame_index),
            "baseline_milli": str(llround(self.baseline * 1000)),
            "last_onset_frame": (
                None if self.last_onset_frame is None
                else str(self.last_onset_frame)),
            "event_count": str(len(self.events)),
        }))

    def _reject(self, code: str, message: str) -> None:
        self.rejections.append(code)
        raise InputError(message, code)

    def process(self, samples: Any, epoch: int | None = None,
                valid_count: int | None = None) -> Dict[str, Any]:
        if samples is None:
            self._reject("MISSING_INPUT", "missing frame buffer")
        if epoch is not None and epoch != self.epoch:
            self._reject("EPOCH_MISMATCH", "stale epoch")
        if not isinstance(samples, list):
            self._reject("INVALID_SAMPLES", "samples must be a list")
        if len(samples) != FRAME_SAMPLES:
            self._reject("FRAME_COUNT_MISMATCH", "frame must have 160 samples")
        values: List[float] = []
        for value in samples:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                self._reject("NON_NUMERIC_SAMPLE", "non-numeric sample")
            number = float(value)
            if not math.isfinite(number):
                self._reject("NONFINITE_SAMPLE", "nonfinite sample")
            values.append(number)
        valid = FRAME_SAMPLES if valid_count is None else valid_count
        if (not isinstance(valid, int) or isinstance(valid, bool)
                or not 1 <= valid <= FRAME_SAMPLES):
            self._reject("INVALID_VALID_COUNT", "invalid valid_count")
        if any(value != 0.0 for value in values[valid:]):
            self._reject("PADDING_NOT_ZERO", "final padding is not zero")

        energy = sum(value ** 2 for value in values[:valid]) / valid
        log_energy = math.log(max(energy, LOG_FLOOR))
        strength = max(0.0, log_energy - self.baseline - ONSET_THRESHOLD)
        frame = self.frame_index
        source_start = frame * FRAME_SAMPLES
        # The first validated frame initializes the envelope baseline and is
        # never reported as an onset; this removes start-up transient bias.
        onset = (frame > 0 and strength > 0.0 and
                 (self.last_onset_frame is None or
                  frame - self.last_onset_frame >= MIN_ONSET_GAP_FRAMES))
        if frame == 0:
            self.baseline = log_energy
        strength_milli = llround(strength * 1000)
        if onset:
            self.events.append(FactorEvent(
                source_start=source_start,
                source_end=source_start + valid,
                frame_index=frame,
                epoch=self.epoch,
                strength_milli=strength_milli,
                available_monotonic_ns=(frame + 1) * FRAME_NS,
                capture_first_ns=source_start * SAMPLE_NS,
            ))
            self.last_onset_frame = frame
        # Only a fully validated frame advances recurrent state.
        self.baseline = ((1.0 - BASELINE_ALPHA) * self.baseline
                         + BASELINE_ALPHA * log_energy)
        self.frame_index += 1
        return {
            "frame_index": str(frame),
            "source_start": str(source_start),
            "valid_count": str(valid),
            "input_count": str(len(values)),
            "strength_milli": str(strength_milli),
            "onset": onset,
        }


def estimate_factor(events: Sequence[FactorEvent],
                    gap_intervals: Sequence[Tuple[int, int]] = ()
                    ) -> Dict[str, Any]:
    """Estimate a tempo factor from source-anchored IOIs; fail closed."""
    frames = [event.frame_index for event in events]
    if not frames:
        return {"status": "no_onsets", "onset_count": "0", "ioi_frames": [],
                "factor_bpm_x100_values": [], "spread_x100": "0",
                "factor_bpm_x100": None, "excluded_ioi_count": "0"}
    iois: List[int] = []
    excluded = 0
    for first, second in zip(frames, frames[1:]):
        midpoint = ((first + second) * FRAME_SAMPLES) // 2
        if any(start <= midpoint < end for start, end in gap_intervals):
            excluded += 1
            continue
        iois.append(second - first)
    base = {"onset_count": str(len(frames)),
            "ioi_frames": [str(value) for value in iois],
            "excluded_ioi_count": str(excluded)}
    if len(iois) < MIN_IOIS_FOR_FACTOR:
        return dict(base, status="insufficient_onsets",
                    factor_bpm_x100_values=[], spread_x100="0",
                    factor_bpm_x100=None)
    bpms = [llround(600000 / ioi) for ioi in iois]
    spread = max(bpms) - min(bpms)
    base["factor_bpm_x100_values"] = [str(value) for value in bpms]
    base["spread_x100"] = str(spread)
    if any(value < FACTOR_MIN_BPM_X100 or value > FACTOR_MAX_BPM_X100
           for value in bpms):
        return dict(base, status="factor_out_of_range", factor_bpm_x100=None)
    if spread > FACTOR_STABILITY_SPREAD_X100:
        return dict(base, status="no_stable_factor", factor_bpm_x100=None)
    return dict(base, status="stable",
                factor_bpm_x100=str(llround(sum(bpms) / len(bpms))))


def analyze_signal(signal: Sequence[float],
                   gaps: Sequence[Tuple[int, int]] = (),
                   epoch: int = 1) -> Dict[str, Any]:
    analyzer = OnsetAnalyzer(epoch=epoch)
    records: List[Dict[str, Any]] = []
    for start in range(0, len(signal), FRAME_SAMPLES):
        block = list(signal[start:start + FRAME_SAMPLES])
        valid = len(block)
        padded = block + [0.0] * (FRAME_SAMPLES - valid)
        records.append(analyzer.process(padded, epoch=epoch,
                                        valid_count=valid))
    return {
        "events": analyzer.events,
        "records": records,
        "factor": estimate_factor(analyzer.events, gaps),
    }


def stimulus_probe() -> Dict[str, Any]:
    specs = stimulus_specs()
    stimuli: Dict[str, Dict[str, Any]] = {}
    analyses: Dict[str, Dict[str, Any]] = {}
    deterministic = True
    for name, spec in sorted(specs.items()):
        signal, gaps = generate_stimulus(spec)
        duplicate, duplicate_gaps = generate_stimulus(spec)
        digest = tensor_digest(signal)
        if (digest != tensor_digest(duplicate) or gaps != duplicate_gaps):
            deterministic = False
        analysis = analyze_signal(signal, gaps)
        analyses[name] = analysis
        stimuli[name] = {
            "kind": spec["kind"],
            "length_samples": str(len(signal)),
            "frames": str((len(signal) + FRAME_SAMPLES - 1) // FRAME_SAMPLES),
            "final_valid_count": str(len(signal) % FRAME_SAMPLES
                                     or FRAME_SAMPLES),
            "float32_sha256": digest,
            "finite": True,
            "bounded": peak_abs(signal) <= MAX_ABS_STIMULUS,
            "peak_abs": _r(peak_abs(signal)),
            "rms": _r(rms(signal)),
            "excluded_gap_samples": [[str(start), str(end)]
                                     for start, end in gaps],
        }

    durations: Dict[str, Dict[str, Any]] = {}
    for name in ("music_1x", "rate_0_8", "rate_1_2"):
        frames = [event.frame_index for event in analyses[name]["events"]]
        period = int(specs[name]["period_samples"])
        expected = (len(frames) - 1) * period
        observed = (frames[-1] - frames[0]) * FRAME_SAMPLES
        durations[name] = {
            "onset_count": str(len(frames)),
            "period_samples": str(period),
            "expected_span_samples": str(expected),
            "observed_span_samples": str(observed),
            "error_samples": str(observed - expected),
        }

    margins = [event.available_monotonic_ns - event.capture_first_ns
               for analysis in analyses.values()
               for event in analysis["events"]]
    rebuffer_gap = analyses["rebuffer"]["events"]
    gap = generate_stimulus(specs["rebuffer"])[1][0]
    rebuffer_onsets = [event.frame_index for event in rebuffer_gap]
    cross_gap = [(first, second)
                 for first, second in zip(rebuffer_onsets, rebuffer_onsets[1:])
                 if gap[0] <= (first + second) * FRAME_SAMPLES // 2 < gap[1]]
    drift_iois = [int(value) for value in
                  analyses["drift"]["factor"]["ioi_frames"]]
    drift_decreasing = len(drift_iois) >= 4 and all(
        later < earlier for earlier, later in zip(drift_iois, drift_iois[1:]))
    final_events = analyses["final_partial"]["events"]
    final_error = (final_events[0].source_start
                   - int(specs["final_partial"]["onset_sample"])
                   if final_events else None)
    factor = {name: value["factor"] for name, value in sorted(analyses.items())}

    rate_profile = {
        "identity_1x": {"stimulus": "music_1x",
                        "factor_bpm_x100": factor["music_1x"]["factor_bpm_x100"]},
        "rate_changes": [
            {"stimulus": "rate_0_8", "expected_bpm_x100": "8000",
             "observed_bpm_x100": factor["rate_0_8"]["factor_bpm_x100"]},
            {"stimulus": "music_1x", "expected_bpm_x100": "10000",
             "observed_bpm_x100": factor["music_1x"]["factor_bpm_x100"]},
            {"stimulus": "rate_1_2", "expected_bpm_x100": "12000",
             "observed_bpm_x100": factor["rate_1_2"]["factor_bpm_x100"]},
        ],
        "duration": {
            "cases": durations,
            "max_error_samples": max(abs(int(row["error_samples"]))
                                     for row in durations.values()),
        },
        "source_output_mapping": {
            "audio_output_produced": False,
            "factor_output_produced": False,
            "analysis_event_source_anchor": True,
            "frame_hop_samples": str(FRAME_SAMPLES),
            "available_ns_per_frame": str(FRAME_NS),
            "min_availability_margin_ns": min(margins) if margins else 0,
            "note": (
                "Harness events carry source intervals and a synthetic "
                "monotonic availability; no audio, device clock or real "
                "factor output is claimed."),
        },
        "pitch": {
            "status": "not_measurable_factor_analysis_only",
            "qualifies": False,
            "note": (
                "A tempo-factor analysis does not alter pitch; no pitch or "
                "pitch-preservation claim is made."),
        },
        "transient_proxy": {
            "final_partial_error_samples": final_error,
            "frame_quantized": True,
            "note": (
                "Frame-quantized onset timing proxy only; not transient "
                "audibility or listening."),
        },
        "playback_buffering": {
            "device_buffer_measured": False,
            "sdk_worker_count": "0",
            "sdk_queue_depth": "0",
            "analysis_frame_aggregation_samples": str(FRAME_SAMPLES),
            "final_partial_valid_count": str(FINAL_VALID_SAMPLES),
            "final_padding_zero_verified": True,
        },
        "speech_unfamiliar": {
            "stimulus": "speech_like",
            "status": factor["speech_like"]["status"],
            "qualifies": False,
        },
        "music": {"stimulus": "music_1x", "status": factor["music_1x"]["status"],
                  "factor_bpm_x100": factor["music_1x"]["factor_bpm_x100"]},
        "silence": {"stimulus": "silence", "status": factor["silence"]["status"]},
        "rebuffer": {
            "gap_samples": [[str(gap[0]), str(gap[1])]],
            "excluded_ioi_count": factor["rebuffer"]["excluded_ioi_count"],
            "cross_gap_ioi_suppressed": (
                bool(cross_gap) and
                int(factor["rebuffer"]["excluded_ioi_count"]) == len(cross_gap)),
            "status": factor["rebuffer"]["status"],
        },
        "drift": {
            "ioi_frames": factor["drift"]["ioi_frames"],
            "monotonic_ioi_decrease": drift_decreasing,
            "status": factor["drift"]["status"],
            "note": (
                "Source-anchored IOI sequence, not a fixed global tempo claim."),
        },
        "final_partial_window": {
            "length_samples": stimuli["final_partial"]["length_samples"],
            "valid_count": stimuli["final_partial"]["final_valid_count"],
            "event_source_end": (str(final_events[0].source_end)
                                 if final_events else None),
            "event_beyond_source_end": (
                bool(final_events and
                     final_events[0].source_end
                     > int(stimuli["final_partial"]["length_samples"]))),
            "event_digest": sha256_bytes(canonical_bytes(
                [event.as_dict() for event in final_events])),
        },
        "factor_is_candidate_output": False,
    }

    return {
        "purpose": (
            "Exercise the Rate harness and rejection paths; never candidate "
            "output or candidate parity."),
        "candidate_processing": False,
        "not_upstream_essentia": True,
        "deterministic": deterministic,
        "frame_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "verified_model_geometry": False,
            "note": (
                "Installed v0 geometry only. No Essentia rate or frame size "
                "is assumed."),
        },
        "stimuli": stimuli,
        "factor": factor,
        "rate_profile": rate_profile,
        "metrics": None,
        "qualifies_candidate": False,
    }


# ---------------------------------------------------------------------------
# Local harness scoring
# ---------------------------------------------------------------------------
def _local_checks(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []

    def check(check_id: str, expected: Any, observed: Any, note: str) -> None:
        checks.append({"id": check_id, "expected": expected,
                       "observed": observed, "passed": expected == observed,
                       "note": note})

    probe = report["harness_probe"]
    rate = probe["rate_profile"]
    factor = probe["factor"]
    check("identity_1x_factor", "10000", rate["identity_1x"]["factor_bpm_x100"],
          "100 BPM at 1x from a 9600-sample synthetic period")
    check("rate_0_8_factor", "8000", factor["rate_0_8"]["factor_bpm_x100"],
          "event-time scaling by 0.8 gives 80 BPM")
    check("rate_1_2_factor", "12000", factor["rate_1_2"]["factor_bpm_x100"],
          "event-time scaling by 1.2 gives 120 BPM")
    check("duration_mapping_exact", 0, rate["duration"]["max_error_samples"],
          "exact source-sample span under each synthetic rate")
    check("speech_no_stable_factor", True,
          factor["speech_like"]["factor_bpm_x100"] is None
          and factor["speech_like"]["status"] != "stable",
          "irregular speech surrogate has no stable factor")
    check("silence_no_onsets", "no_onsets", factor["silence"]["status"],
          "silence produces no onset event")
    check("music_stable_factor", "stable", factor["music_1x"]["status"],
          "music surrogate produces a stable factor")
    check("rebuffer_gap_suppressed", True,
          rate["rebuffer"]["cross_gap_ioi_suppressed"],
          "no factor is estimated across the synthetic rebuffer gap")
    check("drift_recorded", True, rate["drift"]["monotonic_ioi_decrease"],
          "drift is recorded as a source-anchored IOI sequence")
    check("final_partial_valid", "137",
          rate["final_partial_window"]["valid_count"],
          "the final partial frame is explicit")
    check("final_partial_event_in_window", False,
          rate["final_partial_window"]["event_beyond_source_end"],
          "no event extends past the source end")
    check("availability_nonnegative", True,
          rate["source_output_mapping"]["min_availability_margin_ns"] >= 0,
          "no synthetic event is available before its source capture")
    check("pitch_unmeasured", False, rate["pitch"]["qualifies"],
          "pitch is not measured and is never claimed")
    check("device_buffer_unmeasured", False,
          rate["playback_buffering"]["device_buffer_measured"],
          "no device buffer, worker or queue is claimed")
    check("factor_not_audio_output", False,
          rate["source_output_mapping"]["audio_output_produced"],
          "the harness produces no audio output")
    check("candidate_processing_false", False, probe["candidate_processing"],
          "the harness never processes candidate audio")
    adverse = report["adverse"]
    check("all_requests_rejected", True,
          adverse["invalid_requests"]["all_rejected"],
          "every invalid request is rejected before any artifact check")
    check("all_json_rejected", True,
          adverse["invalid_json_numeric_fields"]["all_rejected"],
          "duplicate, nonfinite and malformed JSON is rejected")
    check("missing_result_blocked", False,
          adverse["missing_result"]["qualifies_candidate"],
          "a missing result is blocked and never promoted")
    check("all_gates_blocked", True,
          len(report["release_gates"]) == RELEASE_GATE_COUNT and all(
              gate["status"] == "blocked"
              for gate in report["release_gates"]),
          "no release gate is opened by synthetic evidence")
    check("no_result_qualifies", True,
          report["candidates"][COMPONENT]["qualifies_candidate"] is False,
          "the candidate is never qualified")
    return checks


# ---------------------------------------------------------------------------
# Board projection and report builder
# ---------------------------------------------------------------------------
def _board_projection(board: Any) -> Tuple[List[Dict[str, Any]], str]:
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    rows = [row for row in board["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ConfigError("linked task row is missing or duplicated",
                          "BOARD_ROW_MISSING")
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    projected = [stable]
    return projected, sha256_bytes(canonical_bytes(projected))


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    return _board_projection(board)


def _pin_rows() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    source: Dict[str, Any] = {}
    for relative, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(WORKSPACE / relative)
        source[relative] = {"sha256": expected, "actual": actual,
                            "verified": actual == expected}
    boundary: Dict[str, Any] = {}
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(SDK_ROOT / relative)
        boundary[relative] = {"sha256": expected, "actual": actual,
                              "verified": actual == expected}
    if any(not row["verified"]
           for rows in (source, boundary) for row in rows.values()):
        raise ConfigError("a pinned input changed", "PIN_MISMATCH")
    return source, boundary


def _required_results() -> Dict[str, str]:
    return {
        "exact_upstream_source_revision_and_license": "blocked",
        "agpl_network_use_and_outbound_compatibility_decision": "blocked",
        "pinned_runtime_and_python_bindings": "blocked",
        "pinned_models_configuration_and_model_license": "blocked",
        "beat_tempo_and_onset_reproduction_with_reset_and_drain": "blocked",
        "rate_source_output_mapping_and_duration": "blocked",
        "pitch_and_transient_qualification": "blocked",
        "unfamiliar_speech_and_music_cohorts": "blocked",
        "paced_device_timing_memory_and_callback": "blocked",
        "external_adapter_provider_intake": "blocked",
        "authorized_listening_and_benchmark_validation": "blocked",
        "release_qualification": "blocked",
    }


def _profile_mapping() -> Dict[str, str]:
    return {
        "source_output_mapping": "blocked_no_candidate_output",
        "duration": "blocked_no_candidate_output",
        "pitch": "blocked_no_candidate_output",
        "transient_audibility": "blocked_no_candidate_output",
        "playback_buffering": "blocked_no_candidate_output",
        "identity_1x_and_rate_changes": "blocked_no_candidate_output",
        "unfamiliar_speech": "blocked_no_candidate_output",
        "music_and_silence": "blocked_no_candidate_output",
        "rebuffer_and_drift": "blocked_no_candidate_output",
        "final_partial_window": "blocked_no_candidate_output",
        "candidate_output": (
            "blocked_source_rights_runtime_models_and_fixtures_absent"),
    }


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    license_block = license_probe(source)
    runtime = runtime_probe()
    fixture = fixture_probe()
    rights = rights_probe()
    geom = geometry()
    harness = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    required = [dict(row) for row in REQUIRED_ARTIFACTS]
    source_pins, boundary_pins = _pin_rows()
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "source_absent": source["present"] is False,
        "license_text_absent": license_block["license_text_present"] is False,
        "agpl_not_approved":
            license_block["outbound_compatibility_approved"] is False,
        "runtime_unpinned": runtime["pinned"] is False,
        "matched_fixture_absent": fixture["present"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "invalid_requests_rejected":
            adverse_requests()["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_requests()["cases"]
            if case["id"] in {"REQ-12", "REQ-13", "REQ-14"}),
        "invalid_json_rejected": adverse_json()["all_rejected"],
        "missing_result_blocked":
            missing_result("essentia_placeholder")["status"] == "blocked",
        "identity_control_absent": harness["candidate_processing"] is False,
        "eight_release_gates_blocked": (
            len(gates) == RELEASE_GATE_COUNT and
            all(gate["status"] == "blocked" for gate in gates)),
        "external_boundary_closed": (
            EXTERNAL_BOUNDARY["adapter_implemented"] is False and
            EXTERNAL_BOUNDARY["adapter_default_registration"] is False and
            EXTERNAL_BOUNDARY["automatic_discovery"] is False),
        "no_result_qualifies_candidate": True,
    }
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "mode": MODE,
        "verification_profile": VERIFICATION_PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "generated_by": "reference.py",
        "status": STATUS,
        "decision": DECISION,
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": qualification(),
        "comparison_status":
            "blocked_source_rights_runtime_models_and_fixtures_absent",
        "board_full_file_hashed": False,
        "board_link_fields": list(LINK_FIELDS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "source_evidence_statements": source_evidence_statements(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "source_probe": source,
        "license_probe": license_block,
        "rights_probe": rights,
        "runtime_probe": runtime,
        "fixture_probe": fixture,
        "geometry": geom,
        "external_boundary": dict(EXTERNAL_BOUNDARY),
        "required_artifacts": required,
        "missing_artifacts": [row["artifact"] for row in required
                              if row["status"] == "absent"],
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "required_results": _required_results(),
        "profile_mapping": _profile_mapping(),
        "boundary": boundary(),
        "profile": {
            "name": VERIFICATION_PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        },
        "reference": {
            "implementation": (
                "task-local rate-factor admission gate and independent "
                "onset/factor harness"),
            "not_upstream_essentia": True,
            "real_component_source_present": False,
            "pinned_runtime_present": False,
            "rights_approved": False,
            "real_corpus_read": False,
            "model_weights": False,
            "downloads": False,
            "candidate_processing": False,
            "synthetic_only": True,
            "deterministic": True,
            "upstream_parity": False,
            "note": (
                "The harness is original and never produces candidate "
                "output; the candidate path always raises ARTIFACTS_ABSENT."),
        },
        "candidates": {
            COMPONENT: {
                "status":
                    "blocked_source_rights_runtime_models_and_fixtures_absent",
                "result": None,
                "metrics": None,
                "qualifies_candidate": False,
                "reason": (
                    "No Essentia source, AGPL-3.0 rights decision, pinned "
                    "runtime, configuration, model or matched corpus is "
                    "present; nothing was fabricated or downloaded."),
            },
        },
        "controls": {
            "identity_control": {
                "status": "unavailable_no_candidate_runtime",
                "candidate_processing": False,
                "metrics": None,
                "qualifies_candidate": False,
            },
            "source_reported_characteristics": {
                "status": "source_reported_only",
                "metrics": None,
                "qualifies_candidate": False,
            },
            "external_fallback": {
                "status": "no_fallback_or_default_path",
                "automatic_discovery": False,
                "default_registration": False,
                "fallback": "none",
                "metrics": None,
                "qualifies_candidate": False,
            },
        },
        "harness_probe": harness,
        "adverse": {
            "invalid_requests": adverse_requests(),
            "invalid_json_numeric_fields": adverse_json(),
            "missing_result": missing_result("essentia_placeholder"),
        },
        "local_harness_checks": local_checks,
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "regression_count": 0,
        "regressions": [],
    }
    checks = _local_checks(report)
    failed = [row["id"] for row in checks if row["passed"] is not True]
    report["local_harness_check_rows"] = checks
    report["local_harness_score"] = {
        "checks": len(checks),
        "failed_checks": failed,
        "passed": not failed,
        "scope": "synthetic harness only; not release qualification",
    }
    report["local_harness_checks"]["synthetic_harness_checks_passed"] = (
        not failed)
    if failed:
        raise ConfigError("local harness checks failed: " + ",".join(failed),
                          "HARNESS_CHECK_FAILED")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
