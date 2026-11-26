# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for source localization / DOA.

This package is feasibility evidence only. It models a caller-supplied-asset
tool boundary and model-free synthetic array geometry, but it does not
implement, download, import, load or execute any direction-of-arrival method or
package. The sole source lead (`S26`) is a search excerpt. No microphone
recording, labelled angular/track corpus, calibrated geometry, clock drift
measurement, angle/confidence result, listening result, device timing or
benchmark result is included. Adjacent spatial packages and the CLN-08 taxonomy
survey are recorded as excluded evidence, not as qualification.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/source-localization-direction-of-arrival/caller-supplied/0.1"
TASK_ID = "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"
TITLE = "Source localization / direction-of-arrival"
COMPONENT = "source-localization-direction-of-arrival"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "022a7ad3cedf35aba70ef93b32b71ae51e1e30ca"
BRANCH = "swarm/SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"
REVIEWER = "reviewer-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"
PROFILE = "Spatial"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_geometry_incomplete"

# Installed v0 is unchanged. The synthetic array below is a reference geometry
# only and is not an installed v0 format.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"

SOURCE_REFERENCE: Dict[str, Any] = {
    "id": "S26",
    "title": "Pyroomacoustics direction-of-arrival methods",
    "url": "https://pyroomacoustics.readthedocs.io/en/pypi-release/pyroomacoustics.doa.html",
    "researcher": "acoustics",
    "access_scope": "search excerpt",
    "package_revision": None,
    "local_checkout": None,
    "note": "Catalogued search excerpt; no source, package, runtime or result is staged.",
}

SOURCE_PINS: Dict[str, str] = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/category_survey/search_log.jsonl":
        "61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-SURVEY-CLN-08.md":
        "e009dd94a26cbc3dca5bef8183fa4b0a55415449a2b4aab218189fab80ab2836",
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
    "docs/task-evidence/survey-cln-08/README.md":
        "33730b2bc2a34b05bb7392d8877c498a1b9112a2d41b9e83d31fa6853f8850e7",
    "docs/task-evidence/survey-cln-08/report.json":
        "5d88cea01296895fd275d867cc80a67590187a9255125bbf947a38197cf89fbe",
    "docs/task-evidence/survey-cln-08/SOURCES.sha256":
        "94c38bc39aacaa7f64b81fe02172e2ba167ac90b019974f6d581e39a1462c7a0",
    "docs/task-evidence/hush/README.md":
        "0426a592204381138e7fa7ba04f37f4aff92eee6ac75b6bda31f0861c485e76f",
    "docs/task-evidence/hush/report.json":
        "deaa6ff7bf89bb2727619e69cd41ce40b481ae7db93d25a007cb04b3a218cac4",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/README.md":
        "514636b719e6579651bf941a6ac3cb93740cc9a40e3f2b4bcd39c2ddea610264",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/report.json":
        "5d3623c835a1b19d79867a64ba1b6dff18e8593918a8173cff91550c1c532f03",
    "docs/task-evidence/offline-multichannel-wpe/README.md":
        "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/offline-multichannel-wpe/report.json":
        "4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba",
}

BOARD_STABLE_SHA256 = (
    "359d422c87f32d0b69b14dab79c077bc73fc0219b3e87fee3c150ad98174b14d"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)

TASK_PREFIX = "docs/task-evidence/source-localization-direction-of-arrival/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "README.md",
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
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

# Synthetic, source-independent geometry control. Integer TDOA arithmetic only;
# no array recording, impulse response, DFT, beamformer or DOA estimator runs.
SYNTHETIC_ARRAY: Dict[str, Any] = {
    "configuration_id": "ula-broadside-srp-phat-reference",
    "layout": "ula",
    "microphone_count": 4,
    "spacing_m": 0.05,
    "axis": "x",
    "origin_m": [0.0, 0.0, 0.0],
    "sample_rate_hz": 16000,
    "speed_of_sound_m_s": 343,
    "target_angle_deg": 30,
    "mirror_angle_deg": 150,
    "grid_resolution_deg": 1,
    "grid_max_deg": 90,
    "ambiguity_mode": "report",
    "confidence_threshold": 0.5,
    "note": (
        "Model-free synthetic geometry. It is not an installed v0 format and "
        "cannot produce or qualify an angle or confidence result."
    ),
}

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_s26_search_excerpt_only",
    "source_reference": dict(SOURCE_REFERENCE),
    "required_assets": [
        {
            "id": "doa_source_archive",
            "artifact": "pyroomacoustics source distribution at an immutable revision",
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "present_locally": False,
            "note": "S26 is a documentation search excerpt; no archive is staged.",
        },
        {
            "id": "runtime_lock",
            "artifact": "locked Python/numerical runtime with offline loader",
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "present_locally": False,
            "note": "No runtime lockfile or offline loader is staged.",
        },
        {
            "id": "labelled_spatial_corpus",
            "artifact": "calibrated multichannel array recording with held-out angle/track labels",
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "present_locally": False,
            "note": "No permitted, calibrated, labelled array corpus is staged.",
        },
    ],
    "calibration": {
        "status": "absent",
        "geometry_revision": None,
        "timestamp_calibration_digest": None,
        "clock_offset_samples": None,
        "clock_drift_ppm": None,
        "note": "No measured channel positions, timestamps, offset or drift exists.",
    },
    "rights": {
        "status": "unreviewed",
        "note": (
            "No corpus consent, array-recording permission, package redistribution "
            "grant or product-use review is staged."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
}

BOUNDARY = {
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
    "doa_estimation_executed": False,
    "provider_registered": False,
}

NEGATIVE_CLAIMS = [
    "No direction-of-arrival source, package or runtime is imported, built or executed by this package.",
    "No S26 package, source archive, checkpoint, runtime lock or labelled corpus is downloaded, vendored, present or loaded.",
    "No microphone recording, real array geometry, room capture or calibrated timestamp is present.",
    "The model-free integer TDOA probe is not an angle, confidence or localization result.",
    "The S26 search excerpt names methods but supplies no numeric result, package revision, geometry or label.",
    "The CLN-08 taxonomy survey and adjacent spatial packages cannot qualify this component.",
    "Mirror ambiguity, single-channel and zero-information controls are abstention checks, not successful estimates.",
    "No device timing, held-out label score, benchmark, release claim or provider exposure is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES = [
    {
        "id": "RG-01",
        "title": "exact_source_runtime_and_package_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "The exact DOA source revision, package archive, runtime lockfile and "
            "offline loader must be pinned; the S26 search excerpt alone is insufficient."
        ),
        "reopen_condition": (
            "Stage immutable source/package revision, byte count, SHA-256 and "
            "locked offline runtime, then reproduce the exact method."
        ),
    },
    {
        "id": "RG-02",
        "title": "array_geometry_layout_and_timestamp_calibration",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Microphone positions, orientation, layout, channel timestamps, "
            "clock offset, drift and synchronization must be recorded and verified."
        ),
        "reopen_condition": (
            "Provide measured geometry and timestamp calibration with immutable "
            "digests and a documented drift envelope."
        ),
    },
    {
        "id": "RG-03",
        "title": "caller_asset_boundary_and_advertised_modes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Caller asset identity, advertised modes, angle/confidence output "
            "contract, ambiguity reporting and runtime digest must be verified "
            "without loading or executing an asset."
        ),
        "reopen_condition": (
            "Pass a hash-matched caller manifest and demonstrate the advertised "
            "angle/confidence and abstention modes on the pinned source."
        ),
    },
    {
        "id": "RG-04",
        "title": "permitted_source_target_reference_and_room_conditions",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Source, target and reference directions, movement, room condition, "
            "consent, usage grant and reference permissions must be frozen."
        ),
        "reopen_condition": (
            "Stage a rights-cleared spatial corpus with frozen source/target/"
            "reference and room-condition records."
        ),
    },
    {
        "id": "RG-05",
        "title": "task_matched_held_out_labels_and_separated_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Held-out angular and track labels must score localization, activity "
            "and extraction as separate outcomes with calibrated confidence."
        ),
        "reopen_condition": (
            "Report separated angular error, track, activity, extraction and "
            "confidence-calibration results on frozen held-out labels."
        ),
    },
    {
        "id": "RG-06",
        "title": "leakage_target_damage_channel_loss_and_condition_shift",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Leakage, target damage, channel loss and changed room/reference "
            "conditions must be reported with their failure envelopes."
        ),
        "reopen_condition": (
            "Run pinned channel-loss, room-shift and reference-change controls "
            "with quantified leakage and target-damage outcomes."
        ),
    },
    {
        "id": "RG-07",
        "title": "failure_controls_and_abstention",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Silence, single-channel, mirror-ambiguity, drift, out-of-range-angle "
            "and invalid-manifest controls must abstain or fail closed."
        ),
        "reopen_condition": (
            "Execute the pinned control matrix against the exact source and "
            "record abstention and failure behavior."
        ),
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Opt-in provider intake, independent exact-head review and release "
            "approval are required before any exposure."
        ),
        "reopen_condition": (
            "A separate versioned intake passes independent review with OFF "
            "default and explicit approval."
        ),
    },
]

EXACT_BLOCKERS = [
    {
        "id": "XB-01",
        "title": "no_runnable_local_doa_source_or_runtime",
        "detail": (
            "The only named lead is S26, a Pyroomacoustics DOA documentation "
            "search excerpt. No package revision, source archive, runtime "
            "lockfile or offline loader is staged, and no method is executable."
        ),
        "reopen": (
            "Stage the exact licensed source/package revision and locked offline "
            "runtime with byte counts and SHA-256 values, then reproduce it."
        ),
    },
    {
        "id": "XB-02",
        "title": "calibrated_array_geometry_and_clock_absent",
        "detail": (
            "No microphone positions, orientation, room layout, channel "
            "timestamps, measured clock offset or drift envelope exists. The "
            "4-mic 0.05 m ULA here is a synthetic reference only."
        ),
        "reopen": (
            "Provide immutable measured geometry and timestamp calibration for "
            "a rights-cleared array recording."
        ),
    },
    {
        "id": "XB-03",
        "title": "permitted_task_matched_spatial_labels_absent",
        "detail": (
            "No source/target/reference direction, movement, room condition, "
            "held-out angle/track label, consent or usage grant is staged. "
            "Adjacent spatial packages are not this component."
        ),
        "reopen": (
            "Stage a permitted, calibrated corpus with frozen conditions and "
            "held-out angular/track labels."
        ),
    },
    {
        "id": "XB-04",
        "title": "angle_confidence_controls_and_release_gates_unmet",
        "detail": (
            "No executed angle or confidence result, separated localization/"
            "activity/extraction score, calibration, ambiguity report, "
            "leakage/channel-loss control, device timing, benchmark or opt-in "
            "review exists."
        ),
        "reopen": (
            "Complete the Spatial profile on the exact runtime and pass "
            "independent opt-in review with the default OFF."
        ),
    },
]

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "s26_doa_source_lead",
        "path": "research/category_registry.json",
        "line": 1002,
        "text": '"title": "Pyroomacoustics direction-of-arrival methods",',
    },
    {
        "id": "s26_excerpt_only",
        "path": "research/category_registry.json",
        "line": 1005,
        "text": '"access_scope": "search excerpt"',
    },
    {
        "id": "cln08_source_link",
        "path": "research/category_registry.json",
        "line": 286,
        "text": '"S26"',
    },
    {
        "id": "cln08_input_output_boundary",
        "path": "research/category_registry.json",
        "line": 284,
        "text": (
            '"live_or_comparison_boundary": "Localization is metadata, not a '
            'cleaned signal or proof of intended-speaker identity.",'
        ),
    },
    {
        "id": "cln08_benchmark_not_started",
        "path": "research/category_registry.json",
        "line": 290,
        "text": '"benchmark_status": "not_started"',
    },
    {
        "id": "s26_sources_table_row",
        "path": "research/category_survey/sources.md",
        "line": 36,
        "text": (
            "| S26 | [Pyroomacoustics direction-of-arrival methods](https://pyroomacoustics.readthedocs.io/en/pypi-release/pyroomacoustics.doa.html) | acoustics | search excerpt |"
        ),
    },
    {
        "id": "spatial_acceptance_profile",
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "line": 20,
        "text": (
            "| Spatial | Record geometry, layout, timestamp calibration, "
            "source/target/reference conditions and permissions. Compare "
            "localization/activity/extraction with task-matched held-out "
            "labels. Report leakage, target damage, channel loss, and changes "
            "in room/reference conditions. |"
        ),
    },
    {
        "id": "inventory_considered_sdk_reference",
        "path": "audio-benchmark-platform/plan/INVENTORY.json",
        "line": 9850,
        "text": '"disposition": "sdk-reference",',
    },
    {
        "id": "survey_classic_method_catalogued_only",
        "path": "docs/task-evidence/survey-cln-08/README.md",
        "line": 56,
        "text": (
            "| Classic: steered response power with phase transform (SRP-PHAT) | `source-localization-direction-of-arrival` (considered) | Catalogued method only; no local implementation, geometry check, ambiguity handling or abstention behavior |"
        ),
    },
    {
        "id": "survey_source_only_frozen_protocol",
        "path": "docs/task-evidence/survey-cln-08/README.md",
        "line": 93,
        "text": "- **Source-only frozen protocol:** the `S26` documentation excerpt names",
    },
    {
        "id": "survey_missing_evidence",
        "path": "docs/task-evidence/survey-cln-08/README.md",
        "line": 99,
        "text": "- **Missing:** any CLN-08 implementation or execution, labelled angular/track",
    },
    {
        "id": "survey_forced_angle_not_a_pass",
        "path": "docs/task-evidence/survey-cln-08/README.md",
        "line": 106,
        "text": "The failure envelope is explicit: a forced angle on silence, noise or a single",
    },
)

ABSENT_CANDIDATES: Tuple[str, ...] = (
    "data/models/source-localization-direction-of-arrival",
    "data/checkpoints/source-localization-direction-of-arrival",
    "research/pyroomacoustics",
    "research/category_survey/repos/pyroomacoustics",
    "adapters/source-localization-direction-of-arrival",
)


class ReferenceRejection(ValueError):
    """Deterministic machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
    """Reject duplicate keys, nonfinite constants and unsupported values."""

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
    return strict_loads(path.read_text(encoding="utf-8"))


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Strict SHA-256 manifest parser; rejects duplicate or unsafe keys."""

    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: Dict[str, str] = {}
    result: List[Tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        if key.startswith("source:"):
            relative = key.split(":", 1)[1]
        else:
            relative = key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(
        sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    """Parse the two fenced digest tables in README.md."""

    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0],
                  text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            if not line.startswith("| `") or not line.endswith("` |"):
                raise ValueError("digest_table_row_malformed")
            key, digest = [part.strip() for part in line.strip("|").split("|")]
            if not (key.startswith("`") and key.endswith("`")):
                raise ValueError("digest_table_key_malformed")
            if not (digest.startswith("`") and digest.endswith("`")):
                raise ValueError("digest_table_digest_malformed")
            rows.append((key[1:-1], digest[1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
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


def source_lines() -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for item in SOURCE_LINES:
        root = SDK_ROOT if item["path"].startswith("docs/") else SOURCE_ROOT
        path = root / item["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines[item["line"] - 1].strip() != item["text"]:
            raise ValueError("source_line_mismatch:" + item["id"])
        entries.append({
            "id": item["id"],
            "path": item["path"],
            "root": "sdk_worktree" if item["path"].startswith("docs/") else "workspace",
            "line": item["line"],
            "sha256": sha256_file(path),
            "text": item["text"],
        })
    return {"entries": entries, "line_count": len(entries)}


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file():
            raise ValueError("missing_source_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            raise ValueError("missing_boundary_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "source_url", "source_revision",
    "package_revision", "runtime_lock_digest", "array_geometry_digest",
    "channel_count", "sample_rate_hz", "mic_spacing_m", "speed_of_sound_m_s",
    "target_angle_deg", "mirror_angle_deg", "grid_resolution_deg",
    "ambiguity_mode", "confidence_threshold", "timestamp_calibration_digest",
    "drift_ppm", "label_manifest_path", "label_manifest_sha256",
    "permissions_ref", "room_condition_id", "asset",
)


def _hex_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate caller-supplied metadata only; never load or execute an asset."""

    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST", "manifest must be object")
    keys = set(manifest)
    expected = set(CALLER_MANIFEST_FIELDS)
    if keys != expected:
        if keys - expected:
            raise ReferenceRejection("UNKNOWN_FIELD", "extra manifest fields")
        raise ReferenceRejection("MISSING_FIELD", "missing manifest fields")
    if manifest["adapter"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("UNKNOWN_ADAPTER", "unsupported adapter ID")
    if manifest["configuration_id"] != SYNTHETIC_ARRAY["configuration_id"]:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported configuration")
    if manifest["source_url"] != SOURCE_REFERENCE["url"]:
        raise ReferenceRejection("SOURCE_URL_MISMATCH", "source URL mismatch")
    for field in ("source_revision", "package_revision", "permissions_ref",
                  "room_condition_id"):
        if not _nonempty_str(manifest[field]):
            raise ReferenceRejection("MISSING_FIELD", field + " required")
    if (manifest["channel_count"] != SYNTHETIC_ARRAY["microphone_count"]
            or manifest["sample_rate_hz"] != SYNTHETIC_ARRAY["sample_rate_hz"]
            or manifest["mic_spacing_m"] != SYNTHETIC_ARRAY["spacing_m"]
            or manifest["speed_of_sound_m_s"] != SYNTHETIC_ARRAY[
                "speed_of_sound_m_s"]
            or manifest["target_angle_deg"] != SYNTHETIC_ARRAY["target_angle_deg"]
            or manifest["mirror_angle_deg"] != SYNTHETIC_ARRAY["mirror_angle_deg"]
            or manifest["grid_resolution_deg"] != SYNTHETIC_ARRAY[
                "grid_resolution_deg"]):
        raise ReferenceRejection("GEOMETRY_MISMATCH", "array geometry mismatch")
    if manifest["ambiguity_mode"] != SYNTHETIC_ARRAY["ambiguity_mode"]:
        raise ReferenceRejection("FORCED_AMBIGUITY", "forced ambiguity mode rejected")
    if not isinstance(manifest["confidence_threshold"], (int, float)) \
            or isinstance(manifest["confidence_threshold"], bool) \
            or not 0.0 <= manifest["confidence_threshold"] <= 1.0:
        raise ReferenceRejection("BAD_CONFIDENCE_THRESHOLD", "threshold out of range")
    if (not isinstance(manifest["drift_ppm"], int)
            or isinstance(manifest["drift_ppm"], bool)
            or manifest["drift_ppm"] < 0):
        raise ReferenceRejection("BAD_DRIFT", "drift ppm malformed")
    for field in ("runtime_lock_digest", "array_geometry_digest",
                  "timestamp_calibration_digest", "label_manifest_sha256"):
        if not _hex_digest(manifest[field]):
            raise ReferenceRejection("BAD_DIGEST", field + " malformed")
    if not isinstance(manifest["label_manifest_path"], str) or not Path(
            manifest["label_manifest_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_LABEL_MANIFEST", "absolute label path required")
    asset = manifest["asset"]
    if not isinstance(asset, dict) or set(asset) != {
            "id", "path", "sha256", "byte_count", "revision"}:
        raise ReferenceRejection("BAD_ASSET_FIELDS", "asset fields mismatch")
    if asset["id"] != "doa_source_archive":
        raise ReferenceRejection("ASSET_ID_MISMATCH", "asset ID mismatch")
    if not isinstance(asset["path"], str) or not Path(asset["path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_ASSET_PATH", "asset path must be absolute")
    if not _hex_digest(asset["sha256"]):
        raise ReferenceRejection("BAD_ASSET_DIGEST", "asset digest malformed")
    if not _positive_int(asset["byte_count"]):
        raise ReferenceRejection("BAD_BYTE_COUNT", "asset byte count malformed")
    if not _nonempty_str(asset["revision"]):
        raise ReferenceRejection("MISSING_ASSET_REVISION", "asset revision required")
    source_asset = Path(asset["path"])
    if not source_asset.is_file():
        raise ReferenceRejection("ASSET_ABSENT", "declared asset is absent")
    if sha256_file(source_asset) != asset["sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "asset SHA-256 mismatch")
    if source_asset.stat().st_size != asset["byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "asset byte count mismatch")
    raise ReferenceRejection(
        "DOA_SOURCE_REVISION_UNPINNED",
        "hash-matched caller assets still have no pinned S26 package revision")


def valid_manifest(asset_path: str = "/absent/doa_source_archive.tar.gz") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": SYNTHETIC_ARRAY["configuration_id"],
        "source_url": SOURCE_REFERENCE["url"],
        "source_revision": "caller-declared-unverified",
        "package_revision": "caller-declared-unverified",
        "runtime_lock_digest": "0" * 64,
        "array_geometry_digest": "0" * 64,
        "channel_count": SYNTHETIC_ARRAY["microphone_count"],
        "sample_rate_hz": SYNTHETIC_ARRAY["sample_rate_hz"],
        "mic_spacing_m": SYNTHETIC_ARRAY["spacing_m"],
        "speed_of_sound_m_s": SYNTHETIC_ARRAY["speed_of_sound_m_s"],
        "target_angle_deg": SYNTHETIC_ARRAY["target_angle_deg"],
        "mirror_angle_deg": SYNTHETIC_ARRAY["mirror_angle_deg"],
        "grid_resolution_deg": SYNTHETIC_ARRAY["grid_resolution_deg"],
        "ambiguity_mode": SYNTHETIC_ARRAY["ambiguity_mode"],
        "confidence_threshold": SYNTHETIC_ARRAY["confidence_threshold"],
        "timestamp_calibration_digest": "0" * 64,
        "drift_ppm": 0,
        "label_manifest_path": "/absent/label_manifest.json",
        "label_manifest_sha256": "0" * 64,
        "permissions_ref": "caller-declared-permissions",
        "room_condition_id": "caller-declared-room",
        "asset": {
            "id": "doa_source_archive",
            "path": asset_path,
            "sha256": "0" * 64,
            "byte_count": 1,
            "revision": "caller-declared-unverified",
        },
    }


def integer_tdoa_samples(angle_deg: int) -> Tuple[int, ...]:
    """Deterministic integer-sample TDOA for a broadside ULA; no audio."""

    if not isinstance(angle_deg, int) or isinstance(angle_deg, bool):
        raise ReferenceRejection("BAD_ANGLE", "angle must be an integer")
    sine = math.sin(math.radians(angle_deg))
    samples_per_mic = (SYNTHETIC_ARRAY["sample_rate_hz"]
                       * SYNTHETIC_ARRAY["spacing_m"] * sine
                       / SYNTHETIC_ARRAY["speed_of_sound_m_s"])
    return tuple(int(math.floor(mic * samples_per_mic + 0.5))
                 for mic in range(SYNTHETIC_ARRAY["microphone_count"]))


def geometry_probe() -> Dict[str, Any]:
    target = integer_tdoa_samples(SYNTHETIC_ARRAY["target_angle_deg"])
    mirror = integer_tdoa_samples(SYNTHETIC_ARRAY["mirror_angle_deg"])
    grid = tuple(integer_tdoa_samples(angle) for angle in range(
        SYNTHETIC_ARRAY["grid_max_deg"] + 1))
    distinct = tuple(sorted(set(grid)))
    return {
        "label": "model-free integer TDOA geometry; not DOA output",
        "source_reference": SOURCE_REFERENCE["id"],
        "configuration_id": SYNTHETIC_ARRAY["configuration_id"],
        "array": dict(SYNTHETIC_ARRAY),
        "target_integer_tdoa_samples": list(target),
        "mirror_integer_tdoa_samples": list(mirror),
        "mirror_identical": target == mirror,
        "mirror_is_qualified": False,
        "grid_angles_tested": len(grid),
        "distinct_integer_delay_tuples": len(distinct),
        "grid_collision_count": len(grid) - len(distinct),
        "single_channel_delay_samples": [0],
        "single_channel_angle_identifiable": False,
        "zero_information_abstains": True,
        "confidence_calibrated": False,
        "identity_control": {
            "mirror_integer_tdoa_identical": target == mirror,
            "qualifies": False,
        },
        "nonfinite_count": 0,
        "out_of_range_count": 0,
        "note": (
            "Integer-sample delays from fixed synthetic constants only. No "
            "microphone signal, transform, beamformer, angle search or "
            "confidence estimator is executed."
        ),
    }


def invalid_json_cases() -> Dict[str, Any]:
    cases = []
    for case_id, text in (
            ("duplicate_key", '{"a":1,"a":2}'),
            ("nan_constant", '{"a":NaN}'),
            ("infinity_constant", '{"a":Infinity}'),
            ("negative_infinity_constant", '{"a":-Infinity}'),
            ("trailing_data", '{"a":1} extra'),
            ("invalid_syntax", '{"a":'),
            ("empty_text", "")):
        try:
            strict_loads(text)
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_JSON"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
    }


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        ("duplicate_key", digest + "  source:dup\n" + digest + "  source:dup\n"),
        ("short_digest", "abc  source:short\n"),
        ("missing_separator", digest + " source:missing\n"),
        ("absolute_path", digest + "  /absolute\n"),
        ("traversal", digest + "  source:../escape\n"),
    )
    cases = []
    for case_id, text in samples:
        try:
            parse_pin_lines(text)
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_PIN"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
    }


def adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []

    def probe(case_id: str, mutate: Any, candidate: Any = None) -> None:
        manifest = valid_manifest() if candidate is None else candidate
        mutate(manifest)
        try:
            validate_caller_manifest(manifest)
            observed = "ACCEPTED"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"accepted": observed == "ACCEPTED", "id": case_id,
                      "observed": observed})

    probe("missing_field", lambda m: m.pop("source_revision"))
    probe("unknown_field", lambda m: m.update({"unexpected": 1}))
    probe("wrong_adapter", lambda m: m.update({"adapter": "other"}))
    probe("wrong_configuration", lambda m: m.update({"configuration_id": "other"}))
    probe("wrong_source_url", lambda m: m.update({"source_url": "https://example.invalid"}))
    probe("wrong_channel_count", lambda m: m.update({"channel_count": 1}))
    probe("wrong_rate", lambda m: m.update({"sample_rate_hz": 48000}))
    probe("wrong_spacing", lambda m: m.update({"mic_spacing_m": 0.1}))
    probe("wrong_target_angle", lambda m: m.update({"target_angle_deg": 45}))
    probe("forced_ambiguity", lambda m: m.update({"ambiguity_mode": "forced"}))
    probe("bad_confidence_threshold", lambda m: m.update({"confidence_threshold": 1.5}))
    probe("bad_drift", lambda m: m.update({"drift_ppm": -1}))
    probe("bad_geometry_digest", lambda m: m.update({"array_geometry_digest": "z" * 64}))
    probe("relative_label_manifest",
          lambda m: m.update({"label_manifest_path": "relative/labels.json"}))
    probe("relative_asset_path",
          lambda m: m["asset"].update({"path": "relative/archive.tar.gz"}))
    probe("absent_asset", lambda m: None)
    probe("bad_asset_digest", lambda m: m["asset"].update({"sha256": "f" * 64}))
    probe("bad_asset_byte_count", lambda m: m["asset"].update({"byte_count": 0}))
    probe("manifest_not_object", lambda m: None, candidate=["not", "an", "object"])
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "note": "All caller manifests fail closed before any asset load or execution.",
    }


def asset_pins_absent() -> bool:
    """No exact DOA asset identity may be present in the ledger."""

    if any(asset[key] is not None for asset in ASSET_LEDGER["required_assets"]
           for key in ("revision", "byte_count", "sha256")):
        return False
    for key in ("geometry_revision", "timestamp_calibration_digest",
                "clock_offset_samples", "clock_drift_ppm"):
        if ASSET_LEDGER["calibration"][key] is not None:
            return False
    return not any(ASSET_LEDGER[key] for key in
                   ("downloaded", "vendored", "loaded", "executed"))


def absent_artifact_probe() -> Dict[str, Any]:
    workspace_found = [path for path in ABSENT_CANDIDATES
                       if (SOURCE_ROOT / path).exists()]
    sdk_found: List[str] = []
    return {
        "note": "Bounded read-only path probes; no download, import or load attempted.",
        "present": False,
        "workspace_candidates": list(ABSENT_CANDIDATES),
        "workspace_found": workspace_found,
        "sdk_worktree_found": sdk_found,
        "method": "explicit candidate paths only; no recursive filesystem walk",
    }


def spatial_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "geometry_and_layout": {
                "status": "model_free_only",
                "evidence": "4-mic 0.05 m ULA is synthetic; no measured array exists.",
            },
            "timestamp_calibration": {
                "status": "blocked",
                "evidence": "No channel timestamps, clock offset or drift measurement.",
            },
            "source_target_reference_conditions": {
                "status": "blocked",
                "evidence": "No source/target/reference direction or movement record.",
            },
            "permissions": {
                "status": "blocked",
                "evidence": "No consent, usage grant or redistribution permission.",
            },
            "localization": {
                "status": "blocked",
                "evidence": "No held-out angular label or executed estimator.",
            },
            "activity": {
                "status": "blocked",
                "evidence": "No voice-activity or source-presence label is staged.",
            },
            "extraction": {
                "status": "blocked",
                "evidence": "Localization metadata is not a cleaned signal or target extraction.",
            },
            "confidence_calibration": {
                "status": "blocked",
                "evidence": "Threshold is modeled; no calibrated confidence result exists.",
            },
            "leakage_target_damage_channel_loss_condition_shift": {
                "status": "blocked",
                "evidence": "No channel-loss, room-shift or leakage/target-damage result.",
            },
        },
        "spatial_acceptance_cleared": False,
    }


def source_reported() -> Dict[str, Any]:
    lines = source_lines()
    return {
        "entries": lines["entries"],
        "line_count": lines["line_count"],
        "source_lead": dict(SOURCE_REFERENCE),
        "catalogued_method_families": {
            "classic": "SRP-PHAT; MUSIC/NormMUSIC (catalogued, not executed)",
            "ml": "Learned spatial-feature estimators; candidate search pending",
        },
        "category_status": {
            "discovery_status": "catalogued",
            "candidate_census_status": "not_started",
            "benchmark_status": "not_started",
            "qualifies": False,
        },
        "survey_gap": {
            "no_dedicated_cln08_execution": True,
            "no_labelled_angular_track_corpus": True,
            "no_calibrated_array_or_drift": True,
            "no_metric_implementation": True,
            "forced_angle_on_silence_or_single_channel_is_error": True,
            "mirror_without_ambiguity_report_is_not_a_pass": True,
        },
        "excluded_from_doa_evidence": [
            "CLN-08 taxonomy survey (`survey-cln-08`)",
            "3D microphone spatial/time-alignment package",
            "Hush caller-supplied spatial package",
            "Offline multichannel WPE package",
            "Delay-and-sum / MVDR / neural beamforming packages",
        ],
        "listening_performed_here": False,
        "qualifies": False,
        "separation": (
            "All catalogued families and adjacent packages are source or "
            "task-local evidence for other components. None is an executed "
            "DOA result for this task."
        ),
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    probe = absent_artifact_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    geometry = geometry_probe()
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(BOUNDARY["format"]),
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "configuration_id": SYNTHETIC_ARRAY["configuration_id"],
            "source_url": SOURCE_REFERENCE["url"],
            "required_assets": [dict(item)
                                for item in ASSET_LEDGER["required_assets"]],
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata-only reference. A hash-matched caller asset set still "
                "fails as DOA_SOURCE_REVISION_UNPINNED."
            ),
        },
        "synthetic_array": dict(SYNTHETIC_ARRAY),
        "geometry_probe": geometry,
        "spatial_profile": spatial_profile(),
        "available_evidence": {
            "status": "source_reported_only",
            "clock": "no runtime clock",
            "device_timing": False,
            "streaming_result": False,
            "angle_claim": False,
            "confidence_calibration": False,
            "first_output_or_tail": "blocked_not_measured",
        },
        "asset_resolution": probe,
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (manifest_adverse["all_rejected"]
                             and json_adverse["all_rejected"]
                             and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_matched_doa_source_or_labels",
            "identity_control": "integer TDOA mirror control only; not DOA output",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "model_provenance": {
            "source_reference": dict(SOURCE_REFERENCE),
            "required_assets": [dict(item) for item in ASSET_LEDGER["required_assets"]],
            "calibration": dict(ASSET_LEDGER["calibration"]),
            "rights": dict(ASSET_LEDGER["rights"]),
        },
        "licensing_analysis": {
            "source_license": "unreviewed; S26 is a search excerpt",
            "package_terms": "unreviewed",
            "corpus_and_array_permissions": "unreviewed",
            "product_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "immutable S26 source/package revision and locked offline runtime",
            "measured array geometry, timestamps, clock offset and drift",
            "permitted source/target/reference and room-condition records",
            "held-out angular/track labels and separated outcome scores",
            "ambiguity, channel-loss, leakage and opt-in review",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "model_free_geometry": True,
            "real_local_model_output": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
        },
        "board_link": board_link(),
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
        "# The mutable full plan/swarm/TASKS.json is never pinned; only stable row identity is gated.",
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


def contract_bytes(report_payload: bytes, sidecar_payload: bytes,
                   sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        artifact_pins[TASK_PREFIX + name] = sha256_bytes(payload)
    contract: Dict[str, Any] = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "contract_version": "0.1",
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
        "artifact_pins": artifact_pins,
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "board_link": board_link(),
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "The synthetic 4-mic ULA geometry is reference-only and not installable in v0.",
            "Only the task-local evidence directory is written.",
            "No source, package, asset, audio, label or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "Integer TDOA mirror and zero-information controls cannot qualify the candidate.",
            "CLN-08 survey and adjacent spatial packages are excluded from DOA evidence.",
            "Only stable board-row identity enters canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base of HEAD with an available PR base ref."""

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
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
