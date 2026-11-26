# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER evidence for SDK-CAPSC-BUFFER-OCCUPANCY-PACING.

Standard-library only and deterministic. This module never downloads, imports,
builds or executes CAPSC, a playback device, an audio file or a network client.
It pins the provenance that is actually present, proves that no CAPSC paper or
artifact, licensed implementation/runtime, controller geometry, qualified
speech estimator, rights-cleared cohort or matched result exists, and
reproduces only declared integer queue-debt arithmetic and deterministic
synthetic controls. None of it is runtime, device or quality evidence and none
of it can qualify.

The pinned candidate note names CAPSC as an ACM MMSys 2021 paper, gives only a
DOI (the publisher returns HTTP 403 to automated fetches) and calls it prior
art / a control-theory reference. It records no CAPSC code, equations,
parameters, dataset, latency target, queue-debt definition, underrun policy or
measured result. The note's section 8.6 debt-controller formulation is labelled
as research that reads on a pending patent; it is not CAPSC and must not be
shipped without counsel review. Nothing is fabricated or downloaded.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

TASK = "SDK-CAPSC-BUFFER-OCCUPANCY-PACING"
COMPONENT_ID = "capsc-buffer-occupancy-pacing"
TASK_TITLE = "CAPSC / buffer-occupancy pacing"
CONTRACT_ID = "audio-sdk/capsc-buffer-occupancy-pacing/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
MANIFEST_SCHEMA_ID = "audio-sdk/capsc-buffer-occupancy-pacing/qualification/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "feasibility"
BASE_COMMIT = "d45e0f22883021412b4206c77df4e1d8cf89dbd5"
BRANCH = "swarm/SDK-CAPSC-BUFFER-OCCUPANCY-PACING"
REVIEWER = "reviewer-CAPSC-BUFFER-OCCUPANCY-PACING"
TASK_PREFIX = "docs/task-evidence/capsc-buffer-occupancy-pacing/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component",
    "evidence")
BOARD_STATUS_FIELDS = (
    "status", "owner", "review", "handoff", "blocked_reason",
    "dispatch_priority", "claim")

CANDIDATE_NOTE = (
    "cpp-library/pipeline-validation/playback-speed-candidates.md")
CAPSC_DOI = "10.1145/3458305.3478437"
CAPSC_PAPER_MARKERS = (
    "**CAPSC (ACM MMSys 2021)** is the control-theory reference for the debt "
    "side",
    "| CAPSC, ACM MMSys 2021 | latency-aware, content-aware playback-rate "
    "control for live streaming | P, B, C; no predicted-density decision |",
    "CAPSC \u2014 <https://dl.acm.org/doi/10.1145/3458305.3478437>",
    "publisher returns 403 to automated fetches",
)
SECTION_8_6_MARKER = "### 8.6 Semantic-aware adaptive rate"
BUDGET_IDENTITY_MARKER = "**The budget identity.**"
PATENT_NOTE_MARKER = "> **Patent note.**"
SHIPPING_VARIANT_MARKER = "### 14.6.2 Design-around options, strongest first"
DESIGN_D2_MARKER = "**D2** | **Receding-horizon optimiser on buffered audio.**"
NO_SHIP_MARKER = "Do not ship \u00a78.6 as written until counsel has reviewed"

SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    CANDIDATE_NOTE:
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS: dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
}

SIBLING_PINS: dict[str, str] = {
    "docs/task-evidence/buffer-occupancy-controller/report.json":
        "9dc73683b42a47801efcd71449b7d93fbd40a490beae54c46cc29680ebead47c",
    "docs/task-evidence/pipe-playout/report.json":
        "20e934caa8315c5cb9a3fbad619b7f1048e7212cb0ee1588b975e42ad53045cd",
    "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/report.json":
        "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98",
    "docs/task-evidence/duplex-clocks/contract.json":
        "c09f5a45862fda31039be5b7ebccff07be904c606d51a6f3accde9bea6f04cb4",
    "docs/task-evidence/elastic-pcm-packets/contract.json":
        "2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85",
    "docs/task-evidence/adaptive-energy-vad/report.json":
        "88bd3aa18bf9b20bf7f57b80b8031aa0e8b9939fe1316ebf80ae829770b12da7",
    "docs/task-evidence/silero-vad-v5-onnx-reference/report.json":
        "54e24f7069e6e127f66d630f196a5a88573d3a9a581425978aec71fbbf5e9a0d",
    "docs/task-evidence/usc-mrate/report.json":
        "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246",
    "docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/"
    "report.json":
        "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4",
    "docs/task-evidence/avaudiounittimepitch-rate-pitch-overlap/report.json":
        "33f51433da2938a5dae4ad18fd66da17f78882e2b0aa0301de9d7f52f6474bd0",
    "docs/task-evidence/signalsmith-stretch/report.json":
        "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231",
}

LOCAL_PIN_FILES = (
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

PROFILE_PHRASES = (
    "source/output mapping", "duration", "pitch", "transient audibility",
    "playback buffering", "1\u00d7", "rate changes", "unfamiliar speech",
    "music", "silence", "rebuffer", "drift", "final partial window",
    "speech preservation", "source timestamps",
)

LINKED_ROWS: tuple[dict[str, Any], ...] = (
    {"task": "SDK-BUFFER-OCCUPANCY-CONTROLLER",
     "role": "merged synthetic occupancy-only control law; it is not CAPSC "
             "and contains no CAPSC result",
     "report_sha256":
         "9dc73683b42a47801efcd71449b7d93fbd40a490beae54c46cc29680ebead47c"},
    {"task": "SDK-PIPE-PLAYOUT",
     "role": "merged fixed-rate playback readiness blocker; no admitted "
             "playout controller",
     "report_sha256":
         "20e934caa8315c5cb9a3fbad619b7f1048e7212cb0ee1588b975e42ad53045cd"},
    {"task": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER",
     "role": "merged offline whole-clip planner; not live queue-debt pacing",
     "report_sha256":
         "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98"},
    {"task": "SDK-DUPLEX-CLOCKS",
     "role": "merged explicit clock-domain and exact sample-coordinate "
             "contract; no playout device",
     "report_sha256":
         "c09f5a45862fda31039be5b7ebccff07be904c606d51a6f3accde9bea6f04cb4"},
    {"task": "SDK-ELASTIC-PCM-PACKETS",
     "role": "merged variable-count admission and finite-drain contract; no "
             "pacing controller",
     "report_sha256":
         "2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85"},
    {"task": "SDK-ADAPTIVE-ENERGY-VAD",
     "role": "merged synthetic activity estimator on the separate estimation "
             "side; not qualified for pacing",
     "report_sha256":
         "88bd3aa18bf9b20bf7f57b80b8031aa0e8b9939fe1316ebf80ae829770b12da7"},
    {"task": "SDK-SILERO-VAD-V5-ONNX-REFERENCE",
     "role": "merged pinned VAD reference; estimation side only, not CAPSC",
     "report_sha256":
         "54e24f7069e6e127f66d630f196a5a88573d3a9a581425978aec71fbbf5e9a0d"},
    {"task": "SDK-USC-MRATE",
     "role": "merged rate estimator blocker; estimation side only, not a "
             "playout controller",
     "report_sha256":
         "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246"},
    {"task": "SDK-AUDIOBUFFERSOURCENODE-PLAYBACKRATE-PRESERVESPITCH",
     "role": "merged browser playbackRate DEFER blocker; no CAPSC evidence",
     "report_sha256":
         "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4"},
    {"task": "SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP",
     "role": "merged closed Apple time-pitch blocker; no CAPSC evidence",
     "report_sha256":
         "33f51433da2938a5dae4ad18fd66da17f78882e2b0aa0301de9d7f52f6474bd0"},
    {"task": "SDK-SIGNALSMITH-STRETCH",
     "role": "merged synthetic actuator reference; a stretcher is not a "
             "playout controller and is not CAPSC",
     "report_sha256":
         "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231"},
)

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a",
    ".mdl", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus",
    ".pdf", ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wav", ".wasm",
    ".weights", ".zip",
}

CAPSC_PROBES = (
    "adapters/capsc",
    "bindings/capsc",
    "data/checkouts/capsc",
    "data/checkouts/capsc-buffer-occupancy-pacing",
    "data/papers/capsc",
    "data/papers/capsc.pdf",
    "data/runtimes/capsc",
    "docs/capsc",
    "docs/papers/capsc.pdf",
    "lib/capsc",
    "papers/capsc.pdf",
    "research/capsc",
    "src/capsc",
    "third_party/capsc",
    "tools/capsc",
    "vendor/capsc",
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(
    os.environ.get("AUDIOML_ROOT", str(WORKTREE.parents[2]))).resolve()

FRAME_SAMPLES = 160
SYNTHETIC_CLASS = "synthetic_contract_control_not_evidence"
GEOMETRY = {
    "sample_rate_hz": 16000,
    "block_samples": FRAME_SAMPLES,
    "target_samples": 3200,
    "capacity_samples": 9600,
    "rate_min_ppm": 950000,
    "rate_max_ppm": 1050000,
    "slew_ppm_per_block": 50,
    "gain_num": 1,
    "gain_den": 4,
}
DEBT_DEFINITIONS = (
    "queued_minus_target_samples",
    "integral_rate_deficit_samples",
)
UNDERRUN_POLICIES = (
    "pause_until_target_refill",
    "pause_until_one_block_refill",
    "explicit_zero_concealment",
)
RECOVERY_POLICIES = (
    "resume_at_refilled_target",
    "resume_at_last_rate",
    "controlled_ramp_from_last_rate",
)
CONTROLLER_FIELDS = ("queued_samples", "target_samples", "last_rate_ppm")
PLAYOUT_FIELDS = (
    "arrivals", "initial_queued_samples", "target_samples",
    "capacity_samples")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DOI = re.compile(r"^10\.[0-9]{4,9}/[^ ]+$")
GEOMETRY_TEXT = (
    "synthetic queue-debt control geometry; not a CAPSC value, default or "
    "range")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("non_integer_number")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non_string_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def read_strict_json(path: Path) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject_float(_text: str) -> Any:
        raise ValueError("non_integer_number")

    def reject_constant(text: str) -> Any:
        raise ValueError("nonfinite_constant:" + text)

    text = path.read_text(encoding="utf-8")
    value = json.loads(text, object_pairs_hook=no_duplicates,
                       parse_float=reject_float,
                       parse_constant=reject_constant)
    _no_floats(value)
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_int(value: Any, code: str) -> int:
    if not _is_int(value):
        raise ValueError(code)
    return value


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(code)
    return value


def _require_bool(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(code)
    return value


def _require_digest(value: Any, code: str) -> str:
    if not isinstance(value, str) or not HEX64.match(value):
        raise ValueError(code)
    return value


def _require_slug(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise ValueError(code)
    return value


def _require_exact_keys(value: Any, fields: tuple[str, ...]) -> None:
    if not isinstance(value, dict):
        raise ValueError("invalid_type")
    if set(value) - set(fields):
        raise ValueError("unknown_field")
    for field in fields:
        if field not in value:
            raise ValueError("missing_field")


def _object(value: Any, prefix: str, fields: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(prefix + "_invalid")
    if set(value) - set(fields):
        raise ValueError(prefix + "_unknown_field")
    if any(field not in value for field in fields):
        raise ValueError(prefix + "_missing_field")
    return value


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Playout controller arithmetic (synthetic; not CAPSC)
# ---------------------------------------------------------------------------


def queue_debt(queued_samples: Any, target_samples: Any) -> int:
    queued = _require_int(queued_samples, "queued_not_int")
    target = _require_int(target_samples, "target_not_int")
    if queued < 0:
        raise ValueError("queued_negative")
    if target <= 0:
        raise ValueError("target_not_positive")
    return queued - target


def controller_step(request: Any) -> dict[str, Any]:
    """One occupancy-only rate command.

    The controller reads queue occupancy and the previous emitted rate only.
    It never reads a speech/content label. Labels belong to the separate
    estimation side and are not arguments here.
    """
    _require_exact_keys(request, CONTROLLER_FIELDS)
    queued = _require_int(request["queued_samples"], "queued_not_int")
    target = _require_int(request["target_samples"], "target_not_int")
    last = _require_int(request["last_rate_ppm"], "last_rate_not_int")
    if queued < 0:
        raise ValueError("queued_negative")
    if target < FRAME_SAMPLES:
        raise ValueError("target_too_small")
    if target > GEOMETRY["capacity_samples"]:
        raise ValueError("target_above_capacity")
    if last < GEOMETRY["rate_min_ppm"] or last > GEOMETRY["rate_max_ppm"]:
        raise ValueError("last_rate_out_of_range")
    debt = queued - target
    raw = 1000000 + (
        debt * 1000000 * GEOMETRY["gain_num"]
        // (target * GEOMETRY["gain_den"]))
    clamped = min(max(raw, GEOMETRY["rate_min_ppm"]),
                  GEOMETRY["rate_max_ppm"])
    low = max(GEOMETRY["rate_min_ppm"], last - GEOMETRY["slew_ppm_per_block"])
    high = min(GEOMETRY["rate_max_ppm"], last + GEOMETRY["slew_ppm_per_block"])
    commanded = min(max(clamped, low), high)
    return {
        "queued_samples": queued,
        "target_samples": target,
        "debt_samples": debt,
        "raw_ppm": raw,
        "clamped_ppm": clamped,
        "commanded_ppm": commanded,
        "clamped": clamped != raw,
        "slew_limited": commanded != clamped,
        "reads_content_label": False,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


def controller_controls() -> dict[str, Any]:
    target = GEOMETRY["target_samples"]
    cases = [
        ("C01", "nominal", target, 1000000),
        ("C02", "excess", target + 160, 1000000),
        ("C03", "deficit", target - 160, 1000000),
        ("C04", "cap_high", target + 9600, 1000000),
        ("C05", "cap_low", 0, 1000000),
        ("C06", "slew_high_to_low", 0, 1050000),
        ("C07", "slew_low_to_high", target + 9600, 950000),
        ("C08", "at_capacity", GEOMETRY["capacity_samples"], 1000000),
        ("C09", "empty_queue", 0, 1000000),
        ("C10", "one_block_excess", target + FRAME_SAMPLES, 1000000),
    ]
    rows: list[dict[str, Any]] = []
    for case_id, kind, queued, last in cases:
        command = controller_step({
            "queued_samples": queued,
            "target_samples": target,
            "last_rate_ppm": last,
        })
        rows.append({"id": case_id, "kind": kind, **command})
    summary = {
        "case_count": len(rows),
        "qualifying_results": 0,
        "all_rates_in_bounds": all(
            GEOMETRY["rate_min_ppm"] <= row["commanded_ppm"]
            <= GEOMETRY["rate_max_ppm"] for row in rows),
        "all_slew_within_limit": all(
            abs(row["commanded_ppm"] - case[3])
            <= GEOMETRY["slew_ppm_per_block"]
            for row, case in zip(rows, cases)),
        "nominal_rate_is_1x": rows[0]["commanded_ppm"] == 1000000,
        "excess_increases_rate": rows[1]["commanded_ppm"] > 1000000,
        "deficit_decreases_rate": rows[2]["commanded_ppm"] < 1000000,
        "high_clamp_reached": rows[3]["clamped_ppm"]
        == GEOMETRY["rate_max_ppm"],
        "low_clamp_reached": rows[4]["clamped_ppm"]
        == GEOMETRY["rate_min_ppm"],
        "content_label_read": False,
        "audio_read": False,
        "runtime_invoked": False,
        "network_used": False,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }
    return {
        "geometry": dict(GEOMETRY),
        "geometry_label": GEOMETRY_TEXT,
        "cases": rows,
        "summary": summary,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


def _invalid_controller_cases() -> list[tuple[str, str, Any, str]]:
    base = {
        "queued_samples": GEOMETRY["target_samples"],
        "target_samples": GEOMETRY["target_samples"],
        "last_rate_ppm": 1000000,
    }

    def mutated(**changes: Any) -> dict[str, Any]:
        result = dict(base)
        result.update(changes)
        return result

    def dropped(field: str) -> dict[str, Any]:
        result = dict(base)
        del result[field]
        return result

    return [
        ("I01", "missing_queued", dropped("queued_samples"), "missing_field"),
        ("I02", "missing_target", dropped("target_samples"),
         "missing_field"),
        ("I03", "missing_rate", dropped("last_rate_ppm"), "missing_field"),
        ("I04", "unknown_field", mutated(extra=1), "unknown_field"),
        ("I05", "queued_negative", mutated(queued_samples=-1),
         "queued_negative"),
        ("I06", "queued_bool", mutated(queued_samples=True),
         "queued_not_int"),
        ("I07", "queued_float", mutated(queued_samples=1.5),
         "queued_not_int"),
        ("I08", "queued_nan", mutated(queued_samples=float("nan")),
         "queued_not_int"),
        ("I09", "queued_inf", mutated(queued_samples=float("inf")),
         "queued_not_int"),
        ("I10", "target_zero", mutated(target_samples=0), "target_too_small"),
        ("I11", "target_negative", mutated(target_samples=-160),
         "target_too_small"),
        ("I12", "target_too_small", mutated(target_samples=159),
         "target_too_small"),
        ("I13", "target_above_capacity", mutated(target_samples=9601),
         "target_above_capacity"),
        ("I14", "target_float", mutated(target_samples=3200.0),
         "target_not_int"),
        ("I15", "rate_below_min", mutated(last_rate_ppm=949999),
         "last_rate_out_of_range"),
        ("I16", "rate_above_max", mutated(last_rate_ppm=1050001),
         "last_rate_out_of_range"),
        ("I17", "rate_float", mutated(last_rate_ppm=1000000.0),
         "last_rate_not_int"),
        ("I18", "request_not_object", [], "invalid_type"),
    ]


def invalid_controls() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for case_id, kind, request, expected in _invalid_controller_cases():
        if isinstance(request, float):
            state_unchanged = True
        try:
            controller_step(request)
        except ValueError as error:
            observed = str(error)
        else:
            observed = "accepted"
        cases.append({
            "id": case_id,
            "kind": kind,
            "expected_code": expected,
            "observed_code": observed,
            "status": "rejected" if observed == expected else "mismatch",
            "state_unchanged": True,
            "qualifies": False,
        })
    return {
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(
                1 for case in cases if case["status"] == "rejected"),
            "accepted_count": sum(
                1 for case in cases if case["status"] != "rejected"),
            "all_codes_match": all(
                case["observed_code"] == case["expected_code"]
                for case in cases),
            "nonfinite_rejected": sum(
                1 for case in cases
                if case["kind"] in ("queued_nan", "queued_inf")
                and case["status"] == "rejected") == 2,
            "qualifying_results": 0,
            "evidence_class": SYNTHETIC_CLASS,
            "qualifies": False,
        },
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Synthetic playout accounting: queue debt, underrun, recovery
# ---------------------------------------------------------------------------


def playout_trace(request: Any) -> dict[str, Any]:
    _require_exact_keys(request, PLAYOUT_FIELDS)
    arrivals = request["arrivals"]
    if not isinstance(arrivals, list) or not arrivals:
        raise ValueError("arrivals_invalid")
    if len(arrivals) > 200:
        raise ValueError("arrivals_too_long")
    checked: list[int] = []
    for value in arrivals:
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("arrival_nonfinite")
        item = _require_int(value, "arrival_not_int")
        if item < 0:
            raise ValueError("arrival_negative")
        checked.append(item)
    initial = _require_int(
        request["initial_queued_samples"], "initial_not_int")
    if initial < 0:
        raise ValueError("initial_negative")
    target = _require_int(request["target_samples"], "target_not_int")
    capacity = _require_int(request["capacity_samples"], "capacity_not_int")
    if target < FRAME_SAMPLES:
        raise ValueError("target_too_small")
    if capacity <= target:
        raise ValueError("capacity_not_above_target")

    queued = initial
    last_rate = 1000000
    carry = Fraction(0)
    in_underrun = queued == 0
    underruns = 1 if in_underrun else 0
    underrun_samples = 0
    rebuffer_ticks = 0
    recoveries = 0
    consumed_total = 0
    accepted_total = 0
    peak = queued
    debts: list[int] = []
    commands: list[int] = []
    events: list[dict[str, Any]] = []
    status = "completed"

    for tick, arrival in enumerate(checked):
        if queued + arrival > capacity:
            status = "overflow"
            events.append({
                "tick": tick,
                "kind": "overflow",
                "queued_before": queued,
                "arrival": arrival,
                "capacity": capacity,
                "accepted": False,
            })
            break
        accepted_total += arrival
        queued += arrival
        peak = max(peak, queued)
        debts.append(queued - target)

        if in_underrun:
            rebuffer_ticks += 1
            if queued >= target:
                in_underrun = False
                recoveries += 1
                last_rate = 1000000
                events.append({
                    "tick": tick,
                    "kind": "recovery",
                    "queued": queued,
                    "target": target,
                    "rate_ppm": last_rate,
                    "consumed": 0,
                })
            else:
                events.append({
                    "tick": tick,
                    "kind": "rebuffer",
                    "queued": queued,
                    "target": target,
                    "rate_ppm": 0,
                    "consumed": 0,
                })
            commands.append(last_rate)
            continue

        command = controller_step({
            "queued_samples": queued,
            "target_samples": target,
            "last_rate_ppm": last_rate,
        })
        last_rate = command["commanded_ppm"]
        commands.append(last_rate)
        wanted = carry + Fraction(FRAME_SAMPLES * last_rate, 1000000)
        consumed = wanted.numerator // wanted.denominator
        carry = wanted - consumed
        if queued < consumed:
            shortage = consumed - queued
            underruns += 1
            underrun_samples += shortage
            consumed = queued
            queued = 0
            in_underrun = True
            events.append({
                "tick": tick,
                "kind": "underrun",
                "shortage_samples": shortage,
                "rate_ppm": last_rate,
                "consumed": consumed,
                "queued": queued,
            })
        else:
            queued -= consumed
            events.append({
                "tick": tick,
                "kind": "play",
                "rate_ppm": last_rate,
                "consumed": consumed,
                "queued": queued,
                "debt_samples": queued - target,
                "source_position": consumed_total + consumed,
            })
        consumed_total += consumed

    rate_changes = sum(
        1 for previous, current in zip(commands, commands[1:])
        if previous != current)
    return {
        "ticks": len(checked),
        "status": status,
        "accepted_arrivals": accepted_total,
        "consumed_samples": consumed_total,
        "final_queued_samples": queued,
        "peak_queued_samples": peak,
        "target_samples": target,
        "capacity_samples": capacity,
        "queue_debt_samples": _fraction_text(
            Fraction(sum(debts), len(debts))) if debts else "0",
        "max_excess_debt_samples": max(debts) if debts else 0,
        "max_deficit_debt_samples": min(debts) if debts else 0,
        "underrun_count": underruns,
        "underrun_samples": underrun_samples,
        "rebuffer_ticks": rebuffer_ticks,
        "recovery_count": recoveries,
        "rate_changes": rate_changes,
        "rate_bounds_ppm": [
            min(commands) if commands else 1000000,
            max(commands) if commands else 1000000,
        ],
        "events": events,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


def playout_controls() -> dict[str, Any]:
    target = GEOMETRY["target_samples"]
    capacity = GEOMETRY["capacity_samples"]
    traces = [
        ("P01", "steady", [FRAME_SAMPLES] * 20, target),
        ("P02", "excess", [200] * 20, target),
        ("P03", "deficit", [120] * 20, target),
        ("P04", "hold_then_release", [0] * 25 + [4000] + [160] * 10, target),
        ("P05", "slow_drift", [161] * 30, target),
        ("P06", "overflow", [5000] * 5, target),
        ("P07", "empty_start", [0] * 5, 0),
        ("P08", "underrun_recovery", [0] * 20 + [4000] + [160] * 20, target),
        ("P09", "rebuffer_no_recovery", [0] * 30, target),
        ("P10", "at_target", [FRAME_SAMPLES] * 5, target),
    ]
    cases: list[dict[str, Any]] = []
    for case_id, kind, arrivals, initial in traces:
        result = playout_trace({
            "arrivals": arrivals,
            "initial_queued_samples": initial,
            "target_samples": target,
            "capacity_samples": capacity,
        })
        cases.append({"id": case_id, "kind": kind, **result})
    by_id = {case["id"]: case for case in cases}
    summary = {
        "case_count": len(cases),
        "qualifying_results": 0,
        "steady_has_no_underrun":
            by_id["P01"]["underrun_count"] == 0,
        "empty_start_underruns":
            by_id["P07"]["underrun_count"] == 1,
        "hold_then_release_underruns":
            by_id["P04"]["underrun_count"] >= 1,
        "hold_then_release_recovers":
            by_id["P04"]["recovery_count"] >= 1,
        "no_recovery_case_stays_in_rebuffer":
            by_id["P09"]["recovery_count"] == 0
            and by_id["P09"]["rebuffer_ticks"] >= 1,
        "overflow_rejected_whole_arrival":
            by_id["P06"]["status"] == "overflow",
        "queue_debt_recorded": all(
            "queue_debt_samples" in case for case in cases),
        "underruns_recorded": all(
            "underrun_count" in case for case in cases),
        "controller_separate_from_estimator": True,
        "audio_read": False,
        "audio_rendered": False,
        "device_measured": False,
        "runtime_invoked": False,
        "network_used": False,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }
    return {
        "cases": cases,
        "summary": summary,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


def separation_control() -> dict[str, Any]:
    target = GEOMETRY["target_samples"]
    queue_points = [target, target + 160, target + 320, target, target - 160]
    labels = [
        "meaningful_speech", "silence", "filler", "music", "unknown"]
    by_label: dict[str, list[int]] = {}
    for label in labels:
        commands: list[int] = []
        last = 1000000
        for queued in queue_points:
            command = controller_step({
                "queued_samples": queued,
                "target_samples": target,
                "last_rate_ppm": last,
            })
            last = command["commanded_ppm"]
            commands.append(last)
        by_label[label] = commands
    distinct = {tuple(value) for value in by_label.values()}
    return {
        "labels": labels,
        "queue_points_samples": queue_points,
        "commands_by_label": by_label,
        "distinct_command_sequences": len(distinct),
        "labels_affect_command": len(distinct) != 1,
        "controller_reads_label": False,
        "estimator_output_is_advisory": True,
        "estimator_executed": False,
        "estimator_separate": True,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


def final_partial_control() -> dict[str, Any]:
    cases = []
    for source in (16000, 16001, 16165, 16159):
        samples = _require_int(source, "source_not_int")
        if samples <= 0:
            raise ValueError("source_not_positive")
        remainder = samples % FRAME_SAMPLES
        cases.append({
            "source_samples": samples,
            "block_samples": FRAME_SAMPLES,
            "final_window_samples": remainder,
            "partial": remainder != 0,
            "nominal_blocks": (samples + FRAME_SAMPLES - 1) // FRAME_SAMPLES,
            "evidence_class": SYNTHETIC_CLASS,
            "qualifies": False,
        })
    return {
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "partial_detected": sum(1 for case in cases if case["partial"]),
            "qualifying_results": 0,
            "evidence_class": SYNTHETIC_CLASS,
            "qualifies": False,
        },
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed admission manifest
# ---------------------------------------------------------------------------

MANIFEST_TOP = (
    "schema_id", "capsc", "rights", "controller", "estimator", "cohort",
    "result", "scope")
CAPSC_FIELDS = (
    "doi", "paper_sha256", "artifact_version", "artifact_sha256",
    "source_present", "runtime_present")
RIGHTS_FIELDS = (
    "license_grant_id", "terms_sha256", "execution_approved",
    "redistribution_approved", "derivative_output_approved",
    "patent_counsel_reviewed")
CONTROLLER_MANIFEST_FIELDS = (
    "geometry_sha256", "debt_definition", "latency_target_samples",
    "target_samples", "capacity_samples", "rate_min_ppm", "rate_max_ppm",
    "slew_ppm_per_block", "underrun_policy", "recovery_policy")
ESTIMATOR_FIELDS = (
    "provider_id", "asset_sha256", "qualified", "separate_from_controller")
COHORT_FIELDS = (
    "manifest_sha256", "rights_cleared", "source_timestamps", "output_use")
RESULT_FIELDS = (
    "profile", "trace_sha256", "qualified", "listening", "device_timing")
SCOPE_FIELDS = (
    "off_by_default", "provider_registration", "public_abi_change",
    "shared_build_or_ci_change")


def _synthetic_digest(byte: str) -> str:
    return byte * 64


def _base_manifest() -> dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "capsc": {
            "doi": CAPSC_DOI,
            "paper_sha256": _synthetic_digest("a"),
            "artifact_version": "0.0.0-synthetic-schema-control",
            "artifact_sha256": _synthetic_digest("b"),
            "source_present": False,
            "runtime_present": False,
        },
        "rights": {
            "license_grant_id": "synthetic-schema-control",
            "terms_sha256": _synthetic_digest("c"),
            "execution_approved": True,
            "redistribution_approved": True,
            "derivative_output_approved": True,
            "patent_counsel_reviewed": True,
        },
        "controller": {
            "geometry_sha256": _synthetic_digest("d"),
            "debt_definition": "queued_minus_target_samples",
            "latency_target_samples": GEOMETRY["target_samples"],
            "target_samples": GEOMETRY["target_samples"],
            "capacity_samples": GEOMETRY["capacity_samples"],
            "rate_min_ppm": GEOMETRY["rate_min_ppm"],
            "rate_max_ppm": GEOMETRY["rate_max_ppm"],
            "slew_ppm_per_block": GEOMETRY["slew_ppm_per_block"],
            "underrun_policy": "pause_until_target_refill",
            "recovery_policy": "resume_at_refilled_target",
        },
        "estimator": {
            "provider_id": "synthetic-content-gate",
            "asset_sha256": _synthetic_digest("e"),
            "qualified": True,
            "separate_from_controller": True,
        },
        "cohort": {
            "manifest_sha256": _synthetic_digest("f"),
            "rights_cleared": True,
            "source_timestamps": True,
            "output_use": True,
        },
        "result": {
            "profile": "rate",
            "trace_sha256": _synthetic_digest("1"),
            "qualified": False,
            "listening": False,
            "device_timing": False,
        },
        "scope": {
            "off_by_default": True,
            "provider_registration": False,
            "public_abi_change": False,
            "shared_build_or_ci_change": False,
        },
    }


def validate_manifest(manifest: Any) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_invalid")
    if set(manifest) - set(MANIFEST_TOP):
        raise ValueError("manifest_unknown_field")
    for field in MANIFEST_TOP:
        if field not in manifest:
            raise ValueError("manifest_missing_field")
    if manifest["schema_id"] != MANIFEST_SCHEMA_ID:
        raise ValueError("schema_mismatch")
    capsc = _object(manifest["capsc"], "capsc", CAPSC_FIELDS)
    if capsc["doi"] != CAPSC_DOI or not DOI.match(str(capsc["doi"])):
        raise ValueError("capsc_doi_mismatch")
    _require_digest(capsc["paper_sha256"], "capsc_paper_digest_invalid")
    _require_text(capsc["artifact_version"], "capsc_version_missing")
    _require_digest(capsc["artifact_sha256"], "capsc_artifact_digest_invalid")
    _require_bool(capsc["source_present"], "capsc_source_flag_invalid")
    _require_bool(capsc["runtime_present"], "capsc_runtime_flag_invalid")

    rights = _object(manifest["rights"], "rights", RIGHTS_FIELDS)
    _require_text(rights["license_grant_id"], "rights_grant_missing")
    _require_digest(rights["terms_sha256"], "rights_terms_digest_invalid")
    for field in ("execution_approved", "redistribution_approved",
                  "derivative_output_approved", "patent_counsel_reviewed"):
        _require_bool(rights[field], "rights_flag_invalid")
    if rights["execution_approved"] is not True:
        raise ValueError("execution_not_approved")
    if rights["redistribution_approved"] is not True:
        raise ValueError("redistribution_not_approved")
    if rights["derivative_output_approved"] is not True:
        raise ValueError("derivative_output_not_approved")
    if rights["patent_counsel_reviewed"] is not True:
        raise ValueError("patent_counsel_not_reviewed")

    controller = _object(
        manifest["controller"], "controller", CONTROLLER_MANIFEST_FIELDS)
    _require_digest(
        controller["geometry_sha256"], "controller_geometry_digest_invalid")
    if controller["debt_definition"] not in DEBT_DEFINITIONS:
        raise ValueError("controller_debt_definition_unsupported")
    target = _require_int(
        controller["target_samples"], "controller_target_not_int")
    capacity = _require_int(
        controller["capacity_samples"], "controller_capacity_not_int")
    latency = _require_int(
        controller["latency_target_samples"], "controller_latency_not_int")
    rate_min = _require_int(
        controller["rate_min_ppm"], "controller_rate_min_not_int")
    rate_max = _require_int(
        controller["rate_max_ppm"], "controller_rate_max_not_int")
    slew = _require_int(
        controller["slew_ppm_per_block"], "controller_slew_not_int")
    if target < FRAME_SAMPLES:
        raise ValueError("controller_target_too_small")
    if capacity <= target:
        raise ValueError("controller_capacity_not_above_target")
    if latency != target:
        raise ValueError("controller_latency_target_mismatch")
    if rate_min < 500000 or rate_min >= 1000000:
        raise ValueError("controller_rate_min_invalid")
    if rate_max > 2000000 or rate_max <= 1000000:
        raise ValueError("controller_rate_max_invalid")
    if slew <= 0 or slew > 100000:
        raise ValueError("controller_slew_invalid")
    if controller["underrun_policy"] not in UNDERRUN_POLICIES:
        raise ValueError("controller_underrun_policy_unsupported")
    if controller["recovery_policy"] not in RECOVERY_POLICIES:
        raise ValueError("controller_recovery_policy_unsupported")

    estimator = _object(manifest["estimator"], "estimator", ESTIMATOR_FIELDS)
    _require_slug(estimator["provider_id"], "estimator_provider_invalid")
    _require_digest(estimator["asset_sha256"], "estimator_asset_digest_invalid")
    _require_bool(estimator["qualified"], "estimator_qualified_flag_invalid")
    _require_bool(
        estimator["separate_from_controller"],
        "estimator_separate_flag_invalid")
    if estimator["qualified"] is not True:
        raise ValueError("estimator_not_qualified")
    if estimator["separate_from_controller"] is not True:
        raise ValueError("estimator_not_separate")

    cohort = _object(manifest["cohort"], "cohort", COHORT_FIELDS)
    _require_digest(cohort["manifest_sha256"], "cohort_manifest_digest_invalid")
    if cohort["rights_cleared"] is not True:
        raise ValueError("cohort_rights_not_cleared")
    if cohort["source_timestamps"] is not True:
        raise ValueError("cohort_source_timestamps_missing")
    if cohort["output_use"] is not True:
        raise ValueError("cohort_output_use_missing")

    result = _object(manifest["result"], "result", RESULT_FIELDS)
    if result["profile"] != "rate":
        raise ValueError("result_profile_mismatch")
    _require_digest(result["trace_sha256"], "result_trace_digest_invalid")
    _require_bool(result["qualified"], "result_qualified_flag_invalid")
    _require_bool(result["listening"], "result_listening_flag_invalid")
    _require_bool(result["device_timing"], "result_device_flag_invalid")

    scope = _object(manifest["scope"], "scope", SCOPE_FIELDS)
    for field in SCOPE_FIELDS:
        _require_bool(scope[field], "scope_flag_invalid")
    if scope["off_by_default"] is not True:
        raise ValueError("off_default_required")
    if scope["provider_registration"] is not False:
        raise ValueError("provider_registration_forbidden")
    if scope["public_abi_change"] is not False:
        raise ValueError("public_abi_change_forbidden")
    if scope["shared_build_or_ci_change"] is not False:
        raise ValueError("shared_build_or_ci_change_forbidden")


def assess_manifest(manifest: Any) -> dict[str, Any]:
    validate_manifest(manifest)
    capsc = manifest["capsc"]
    result = manifest["result"]
    if not capsc["source_present"] or not capsc["runtime_present"]:
        reason = "capsc_artifact_absent"
    elif not result["qualified"]:
        reason = "qualified_result_absent"
    elif not result["listening"]:
        reason = "listening_result_absent"
    elif not result["device_timing"]:
        reason = "device_timing_absent"
    else:
        reason = "independent_admission_required"
    return {
        "schema_valid": True,
        "accepted": True,
        "admitted": False,
        "qualifies": False,
        "reason": reason,
        "state_unchanged": True,
        "vendor_runtime_loaded": False,
        "vendor_runtime_invoked": False,
        "audio_read": False,
        "network_used": False,
    }


def _mutations() -> list[tuple[str, str, Callable[[dict[str, Any]], None],
                               str]]:
    def setter(path: tuple[str, ...], value: Any):
        def mutate(manifest: dict[str, Any]) -> None:
            node = manifest
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
        return mutate

    def deleter(path: tuple[str, ...]):
        def mutate(manifest: dict[str, Any]) -> None:
            node = manifest
            for key in path[:-1]:
                node = node[key]
            del node[path[-1]]
        return mutate

    def add_unknown(manifest: dict[str, Any]) -> None:
        manifest["unexpected"] = True

    return [
        ("M01", "missing_top_field", deleter(("rights",)),
         "manifest_missing_field"),
        ("M02", "unknown_top_field", add_unknown, "manifest_unknown_field"),
        ("M03", "schema_mismatch", setter(("schema_id",), "other"),
         "schema_mismatch"),
        ("M04", "capsc_not_object", setter(("capsc",), []), "capsc_invalid"),
        ("M05", "capsc_missing_field", deleter(("capsc", "doi")),
         "capsc_missing_field"),
        ("M06", "capsc_unknown_field", setter(("capsc", "extra"), 1),
         "capsc_unknown_field"),
        ("M07", "doi_mismatch", setter(("capsc", "doi"), "10.1145/0/x"),
         "capsc_doi_mismatch"),
        ("M08", "paper_digest_invalid",
         setter(("capsc", "paper_sha256"), "zz"), "capsc_paper_digest_invalid"),
        ("M09", "version_missing", setter(("capsc", "artifact_version"), ""),
         "capsc_version_missing"),
        ("M10", "artifact_digest_invalid",
         setter(("capsc", "artifact_sha256"), "1"),
         "capsc_artifact_digest_invalid"),
        ("M11", "source_flag_invalid",
         setter(("capsc", "source_present"), "no"),
         "capsc_source_flag_invalid"),
        ("M12", "runtime_flag_invalid",
         setter(("capsc", "runtime_present"), 0),
         "capsc_runtime_flag_invalid"),
        ("M13", "rights_not_object", setter(("rights",), 1), "rights_invalid"),
        ("M14", "rights_missing_field", deleter(("rights", "terms_sha256")),
         "rights_missing_field"),
        ("M15", "rights_unknown_field", setter(("rights", "extra"), 1),
         "rights_unknown_field"),
        ("M16", "grant_missing", setter(("rights", "license_grant_id"), ""),
         "rights_grant_missing"),
        ("M17", "terms_digest_invalid",
         setter(("rights", "terms_sha256"), "x"),
         "rights_terms_digest_invalid"),
        ("M18", "execution_not_approved",
         setter(("rights", "execution_approved"), False),
         "execution_not_approved"),
        ("M19", "redistribution_not_approved",
         setter(("rights", "redistribution_approved"), False),
         "redistribution_not_approved"),
        ("M20", "derivative_not_approved",
         setter(("rights", "derivative_output_approved"), False),
         "derivative_output_not_approved"),
        ("M21", "patent_not_reviewed",
         setter(("rights", "patent_counsel_reviewed"), False),
         "patent_counsel_not_reviewed"),
        ("M22", "rights_flag_invalid",
         setter(("rights", "execution_approved"), 1), "rights_flag_invalid"),
        ("M23", "controller_not_object", setter(("controller",), None),
         "controller_invalid"),
        ("M24", "controller_missing_field",
         deleter(("controller", "debt_definition")),
         "controller_missing_field"),
        ("M25", "controller_unknown_field",
         setter(("controller", "extra"), 1), "controller_unknown_field"),
        ("M26", "geometry_digest_invalid",
         setter(("controller", "geometry_sha256"), "q"),
         "controller_geometry_digest_invalid"),
        ("M27", "debt_definition_unsupported",
         setter(("controller", "debt_definition"), "guessed"),
         "controller_debt_definition_unsupported"),
        ("M28", "target_not_int", setter(("controller", "target_samples"), "x"),
         "controller_target_not_int"),
        ("M29", "target_too_small", setter(("controller", "target_samples"), 0),
         "controller_target_too_small"),
        ("M30", "capacity_not_above_target",
         setter(("controller", "capacity_samples"), 3200),
         "controller_capacity_not_above_target"),
        ("M31", "latency_target_mismatch",
         setter(("controller", "latency_target_samples"), 3201),
         "controller_latency_target_mismatch"),
        ("M32", "rate_min_invalid",
         setter(("controller", "rate_min_ppm"), 1000000),
         "controller_rate_min_invalid"),
        ("M33", "rate_max_invalid",
         setter(("controller", "rate_max_ppm"), 1000000),
         "controller_rate_max_invalid"),
        ("M34", "slew_invalid", setter(("controller", "slew_ppm_per_block"), 0),
         "controller_slew_invalid"),
        ("M35", "underrun_policy_unsupported",
         setter(("controller", "underrun_policy"), "drop_samples"),
         "controller_underrun_policy_unsupported"),
        ("M36", "recovery_policy_unsupported",
         setter(("controller", "recovery_policy"), "fast_forward"),
         "controller_recovery_policy_unsupported"),
        ("M37", "estimator_missing_field",
         deleter(("estimator", "provider_id")),
         "estimator_missing_field"),
        ("M38", "provider_invalid",
         setter(("estimator", "provider_id"), "Bad Provider"),
         "estimator_provider_invalid"),
        ("M39", "asset_digest_invalid",
         setter(("estimator", "asset_sha256"), "x"),
         "estimator_asset_digest_invalid"),
        ("M40", "estimator_not_qualified",
         setter(("estimator", "qualified"), False),
         "estimator_not_qualified"),
        ("M41", "estimator_not_separate",
         setter(("estimator", "separate_from_controller"), False),
         "estimator_not_separate"),
        ("M42", "estimator_qualified_flag_invalid",
         setter(("estimator", "qualified"), 1),
         "estimator_qualified_flag_invalid"),
        ("M43", "cohort_missing_field",
         deleter(("cohort", "manifest_sha256")), "cohort_missing_field"),
        ("M44", "cohort_manifest_digest_invalid",
         setter(("cohort", "manifest_sha256"), "x"),
         "cohort_manifest_digest_invalid"),
        ("M45", "cohort_rights_not_cleared",
         setter(("cohort", "rights_cleared"), False),
         "cohort_rights_not_cleared"),
        ("M46", "cohort_source_timestamps_missing",
         setter(("cohort", "source_timestamps"), False),
         "cohort_source_timestamps_missing"),
        ("M47", "cohort_output_use_missing",
         setter(("cohort", "output_use"), False),
         "cohort_output_use_missing"),
        ("M48", "result_profile_mismatch",
         setter(("result", "profile"), "pipeline"),
         "result_profile_mismatch"),
        ("M49", "result_trace_digest_invalid",
         setter(("result", "trace_sha256"), "x"),
         "result_trace_digest_invalid"),
        ("M50", "result_qualified_flag_invalid",
         setter(("result", "qualified"), 0),
         "result_qualified_flag_invalid"),
        ("M51", "result_listening_flag_invalid",
         setter(("result", "listening"), "yes"),
         "result_listening_flag_invalid"),
        ("M52", "result_device_flag_invalid",
         setter(("result", "device_timing"), 1),
         "result_device_flag_invalid"),
        ("M53", "off_default_required",
         setter(("scope", "off_by_default"), False), "off_default_required"),
        ("M54", "provider_registration_forbidden",
         setter(("scope", "provider_registration"), True),
         "provider_registration_forbidden"),
        ("M55", "public_abi_change_forbidden",
         setter(("scope", "public_abi_change"), True),
         "public_abi_change_forbidden"),
        ("M56", "shared_build_or_ci_change_forbidden",
         setter(("scope", "shared_build_or_ci_change"), True),
         "shared_build_or_ci_change_forbidden"),
        ("M57", "scope_flag_invalid",
         setter(("scope", "off_by_default"), 1), "scope_flag_invalid"),
    ]


def admission_controls() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for case_id, kind, mutate, expected in _mutations():
        manifest = _base_manifest()
        mutate(manifest)
        try:
            validate_manifest(manifest)
        except ValueError as error:
            observed = str(error)
        else:
            observed = "accepted"
        cases.append({
            "id": case_id,
            "kind": kind,
            "expected_code": expected,
            "observed_code": observed,
            "status": "rejected" if observed == expected else "mismatch",
            "state_unchanged": True,
            "qualifies": False,
        })
    control = assess_manifest(_base_manifest())
    return {
        "control": control,
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(
                1 for case in cases if case["status"] == "rejected"),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "all_codes_match": all(
                case["observed_code"] == case["expected_code"]
                for case in cases),
            "state_advanced_on_rejection": False,
            "vendor_runtime_loaded": False,
            "vendor_runtime_invoked": False,
            "license_key_used": False,
            "audio_read": False,
            "audio_rendered": False,
            "network_used": False,
            "evidence_class": SYNTHETIC_CLASS,
            "qualifies": False,
        },
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Provenance, presence and plan-row identity
# ---------------------------------------------------------------------------


def candidate_note_probe() -> dict[str, Any]:
    path = AUDIO_ROOT / CANDIDATE_NOTE
    present = path.is_file()
    text = path.read_text(encoding="utf-8") if present else ""
    lines = text.splitlines()
    marker_lines = {}
    for marker in CAPSC_PAPER_MARKERS:
        marker_lines[marker] = next(
            (index + 1 for index, line in enumerate(lines) if marker in line),
            None)
    section_line = next(
        (index + 1 for index, line in enumerate(lines)
         if line.startswith(SECTION_8_6_MARKER)), None)
    budget_line = next(
        (index + 1 for index, line in enumerate(lines)
         if BUDGET_IDENTITY_MARKER in line), None)
    patent_line = next(
        (index + 1 for index, line in enumerate(lines)
         if line.startswith(PATENT_NOTE_MARKER)), None)
    d2_line = next(
        (index + 1 for index, line in enumerate(lines)
         if DESIGN_D2_MARKER in line), None)
    no_ship_line = next(
        (index + 1 for index, line in enumerate(lines)
         if NO_SHIP_MARKER in line), None)
    return {
        "path": CANDIDATE_NOTE,
        "present": present,
        "sha256": sha256_file(path) if present else None,
        "capsc_main_line": marker_lines[CAPSC_PAPER_MARKERS[0]],
        "capsc_prior_art_line": marker_lines[CAPSC_PAPER_MARKERS[1]],
        "capsc_reference_line": marker_lines[CAPSC_PAPER_MARKERS[2]],
        "publisher_403_line": marker_lines[CAPSC_PAPER_MARKERS[3]],
        "section_8_6_line": section_line,
        "budget_identity_line": budget_line,
        "patent_note_line": patent_line,
        "d2_design_line": d2_line,
        "no_ship_line": no_ship_line,
        "records_capsc_doi": marker_lines[CAPSC_PAPER_MARKERS[2]] is not None,
        "records_publisher_403":
            marker_lines[CAPSC_PAPER_MARKERS[3]] is not None,
        "records_content_aware_rate_control":
            marker_lines[CAPSC_PAPER_MARKERS[1]] is not None,
        "records_latency_aware_control":
            marker_lines[CAPSC_PAPER_MARKERS[0]] is not None,
        "records_implementation_source": False,
        "records_numeric_geometry": False,
        "records_dataset_or_result": False,
        "records_debt_controller_as_research": patent_line is not None,
        "records_patent_risk": patent_line is not None,
        "records_d2_shipping_variant": d2_line is not None,
        "records_do_not_ship": no_ship_line is not None,
        "reproduced_here": False,
        "qualifies": False,
        "evidence_class": "source_reported_provenance_not_remeasured",
    }


def documented_parameter_envelope() -> dict[str, Any]:
    return {
        "evidence_class": "source_reported_provenance_not_remeasured",
        "product": "CAPSC (ACM MMSys 2021 paper)",
        "paper_present": False,
        "implementation_source_recorded": False,
        "api_identity_recorded": False,
        "numeric_bounds_recorded_in_candidate_note": False,
        "defaults_recorded": False,
        "dataset_or_result_recorded": False,
        "latency_target": None,
        "queue_debt_definition": None,
        "underrun_policy": None,
        "recovery_policy": None,
        "rate": {"min": None, "max": None, "default": None,
                 "unit": "unrecorded", "numeric_bounds_recorded": False},
        "slew": {"max": None, "unit": "unrecorded",
                 "numeric_bounds_recorded": False},
        "semantics_verified_here": False,
        "qualifies": False,
    }


def synthetic_control_envelope() -> dict[str, Any]:
    return {
        "evidence_class": SYNTHETIC_CLASS,
        "purpose": "control constants used only to exercise the declared "
                   "synthetic controller, queue-debt, underrun and recovery "
                   "arithmetic; they are not CAPSC evidence and assert no "
                   "CAPSC range, default or policy",
        "sample_rate_hz": GEOMETRY["sample_rate_hz"],
        "block_samples": GEOMETRY["block_samples"],
        "target_samples": GEOMETRY["target_samples"],
        "capacity_samples": GEOMETRY["capacity_samples"],
        "rate_min": _fraction_text(
            Fraction(GEOMETRY["rate_min_ppm"], 1000000)),
        "rate_max": _fraction_text(
            Fraction(GEOMETRY["rate_max_ppm"], 1000000)),
        "slew_ppm_per_block": GEOMETRY["slew_ppm_per_block"],
        "gain": _fraction_text(
            Fraction(GEOMETRY["gain_num"], GEOMETRY["gain_den"])),
        "qualifies": False,
    }


def source_presence() -> dict[str, Any]:
    present = []
    for relative in CAPSC_PROBES:
        if (AUDIO_ROOT / relative).exists():
            present.append(relative)
    note = candidate_note_probe()
    return {
        "candidate_note_present": note["present"],
        "candidate_note_records_capsc_doi": note["records_capsc_doi"],
        "candidate_note_records_publisher_403":
            note["records_publisher_403"],
        "candidate_note_records_content_aware_rate_control":
            note["records_content_aware_rate_control"],
        "candidate_note_records_numeric_geometry":
            note["records_numeric_geometry"],
        "candidate_note_records_implementation_source":
            note["records_implementation_source"],
        "candidate_note_records_patent_risk": note["records_patent_risk"],
        "capsc_artifact_present": any(
            relative for relative in present
            if not relative.endswith(".pdf")),
        "capsc_paper_present": any(
            relative for relative in present if relative.endswith(".pdf")),
        "capsc_source_present": False,
        "capsc_runtime_present": False,
        "licensed_implementation_runtime_present": False,
        "exact_licensed_source_runtime_present": False,
        "presence_is_not_admission": True,
        "present_probes": present,
        "probe_scope": "project workspace only; publisher portals, library "
                       "accounts, DOI resolvers, vendor runtimes and host "
                       "device installations are not inspected or invoked",
        "download_attempted": False,
        "network_used": False,
        "runtime_imported": False,
        "runtime_invoked": False,
        "audio_read": False,
        "audio_played": False,
        "device_inspected": False,
        "admitted": False,
        "qualifies": False,
    }


def license_findings() -> dict[str, Any]:
    return {
        "capsc_is_software_license": False,
        "paper_is_acm_copyrighted_publication": True,
        "license_text_present": False,
        "grant_or_permission_present": False,
        "terms_reviewed": False,
        "execution_approved": False,
        "redistribution_approved": False,
        "derivative_output_use_approved": False,
        "commercial_use_approved": False,
        "patent_counsel_reviewed": False,
        "patent_indemnity_reviewed": False,
        "shipping_design_selected": False,
        "qualifies": False,
        "note": "The candidate note gives a DOI and states that the publisher "
                "returns 403 to automated fetches. It supplies no CAPSC "
                "license text, permission, dataset terms or patent review. "
                "The note's own section 8.6 formulation is labelled research "
                "that reads on US20260075269A1 and must not ship without "
                "counsel review.",
    }


def debt_controller_guard() -> dict[str, Any]:
    return {
        "formulation_is_research_not_capsc": True,
        "capsc_source_used": False,
        "capsc_parameters_copied": False,
        "patent_note_present": True,
        "patent_risk_recorded": True,
        "counsel_reviewed": False,
        "shipping_design_selected": False,
        "shipping_options_recorded": ["D1 offline", "D2 receding-horizon"],
        "generic_p_control_is_not_section_8_6": True,
        "used_in_this_package": False,
        "reason": "Section 8.6 is a workspace research formulation with an "
                  "explicit patent warning, not CAPSC source or a CAPSC "
                  "parameter set. This package's occupancy-only proportional "
                  "control has no speech/repair split, integral debt or "
                  "Dmax branch, is not the section 8.6 formulation, and is "
                  "never presented as CAPSC or as a shippable controller.",
        "qualifies": False,
    }


def _pin_map(pins: dict[str, str], root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        result[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return result


def verify_pins() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _pin_map(SOURCE_PINS, AUDIO_ROOT),
        _pin_map(BOUNDARY_PINS, WORKTREE),
        _pin_map(SIBLING_PINS, WORKTREE),
    )


def linked_rows_digest() -> str:
    return object_digest(list(LINKED_ROWS))


def board_row_projection(path: Path) -> dict[str, Any]:
    data = read_strict_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("board_shape_invalid")
    for row in data["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            missing = [field for field in BOARD_ROW_FIELDS if field not in row]
            if missing:
                raise ValueError("board_row_missing_fields")
            return {field: row[field] for field in BOARD_ROW_FIELDS}
    raise ValueError("board_row_missing")


def board_row_digest(projection: Any) -> str:
    return object_digest(projection)


# ---------------------------------------------------------------------------
# Contract and report
# ---------------------------------------------------------------------------


def _required_artifacts() -> list[dict[str, Any]]:
    rows = (
        ("A01", "CAPSC paper and any official implementation artifact with "
                "exact DOI/version and full SHA-256",
         "BLK-01"),
        ("A02", "permission or licence to execute, benchmark, redistribute, "
                "use derivative output and use commercially, plus a patent "
                "counsel memo", "BLK-01"),
        ("A03", "pinned host/toolchain and a public paced-playout adapter "
                "boundary with instrumented source queue and device clock",
         "BLK-02"),
        ("A04", "CAPSC controller geometry: content classes, queue-debt "
                "definition, latency target, rate bounds, slew, underrun and "
                "recovery policy, final-partial semantics", "BLK-02"),
        ("A05", "qualified speech/content estimator and policy, separate from "
                "the playout controller, with pinned assets and accuracy",
         "BLK-03"),
        ("A06", "rights-cleared unfamiliar-speech, music, silence and "
                "transient cohort with source timestamps and output use",
         "BLK-04"),
        ("A07", "matched Rate-profile results and adverse/missing/nonfinite "
                "controls on the admitted runtime", "BLK-05"),
        ("A08", "listening/speech-preservation and target-device timing, "
                "underrun and resource evidence", "BLK-05"),
        ("A09", "OFF-by-default intake with exact descriptor/config, no "
                "registry/ABI/default/shared-build/CI change and independent "
                "review", "BLK-06"),
    )
    return [{
        "id": artifact_id,
        "name": name,
        "blocker": blocker,
        "present": False,
        "verified": False,
        "licensed": False,
        "admitted": False,
        "blocked": True,
        "sha256": None,
    } for artifact_id, name, blocker in rows]


def _exact_blockers() -> list[dict[str, Any]]:
    rows = (
        ("BLK-01", "A01",
         "No CAPSC paper or official implementation artifact is present. The "
         "candidate note supplies only DOI 10.1145/3458305.3478437, records "
         "that the publisher returns 403 to automated fetches, and gives no "
         "code, equations, parameters or measured result. No licence grant, "
         "terms review or patent counsel decision exists.",
         "Supply the permitted CAPSC paper and any official implementation "
         "with exact version/DOI and full SHA-256 of every file, plus a "
         "written grant covering execution, benchmarking, redistribution, "
         "derivative output, commercial use and patent risk."),
        ("BLK-02", "A04",
         "No CAPSC controller geometry or paced-playout host exists. The note "
         "does not record a CAPSC queue-debt definition, latency target, "
         "content classes, rate bounds, slew, underrun/recovery policy or "
         "final-partial semantics, and SDK v0 defines no playout device "
         "adapter.",
         "Supply the exact CAPSC controller/geometry reference and a pinned "
         "public adapter boundary with instrumented source FIFO, playout "
         "device clock, buffer fill/flush and underrun observation."),
        ("BLK-03", "A05",
         "No qualified speech/content estimator is supplied. Merged VAD, "
         "activity and rate estimators are separate synthetic references and "
         "are not qualified for CAPSC pacing. The note's classifier, ASR and "
         "event-model requirements are design inputs only.",
         "Supply a qualified estimator/policy with pinned runtime and assets, "
         "measured coverage and accuracy, confidence/unknown semantics, "
         "source timestamps and proof that it is separate from the playout "
         "controller."),
        ("BLK-04", "A06",
         "No rights-cleared cohort exists. No unfamiliar-speech, music, "
         "silence, transient or rebuffer recording with consent, terms, "
         "source timestamps and an output-use decision is staged. No audio "
         "byte is read by this package.",
         "Freeze an immutable rights-cleared cohort with held-out speech, "
         "music, silence and transients, exact digests, source timestamps, "
         "dataset terms and a recorded output-use decision."),
        ("BLK-05", "A07",
         "No matched CAPSC result, control, listening study or target-device "
         "timing exists. This package only performs synthetic integer "
         "queue-debt/underrun/recovery accounting; it measures no audio, "
         "latency, queue debt, underrun or recovery on a real device.",
         "Run the agreed Rate profile on the admitted runtime and cohort: 1x, "
         "rate changes, drift, rebuffer, final partial window, queue debt, "
         "underruns, recovery, duration/pitch, transient audibility, speech "
         "preservation, listening and device timing/resources."),
        ("BLK-06", "A09",
         "No provider or pipeline intake, descriptor/config, OFF default, "
         "independent review or release decision exists. Nothing is "
         "registered, enabled, built into a shared surface or released.",
         "Open a separate versioned OFF-by-default intake with exact "
         "descriptor/config, clean-install proof, no registry/ABI/default/"
         "shared-build/CI change and independent exact-head review after the "
         "prior gates clear."),
    )
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "missing": missing,
        "required_action": action,
        "status": "open",
        "qualifies": False,
    } for blocker_id, artifact_id, missing, action in rows]


def _release_gates(linked_row: dict[str, Any]) -> list[dict[str, Any]]:
    rows = (
        ("RG-01", "CAPSC artifact and rights identity",
         "No permitted CAPSC paper or official artifact with exact "
         "version/DOI and full SHA-256 exists; no licence grant or patent "
         "decision exists.",
         "Supply the permitted paper and any official implementation with "
         "full digests and a written rights/patent decision."),
        ("RG-02", "patent posture and shipping design",
         "The note labels its section 8.6 debt controller as research that "
         "reads on US20260075269A1 and says not to ship it without counsel; "
         "no counsel memo or D1/D2 selection exists.",
         "Record a counsel-reviewed patent decision and select an approved "
         "offline or receding-horizon design before any product path."),
        ("RG-03", "qualified separate speech/content estimator",
         "No qualified estimator, model, asset, accuracy result or "
         "confidence/unknown policy exists; the controller must stay "
         "separate from estimation.",
         "Admit a pinned estimator with measured accuracy and prove command "
         "separation from the playout controller."),
        ("RG-04", "controller geometry: queue debt, underruns and recovery",
         "No CAPSC queue-debt definition, latency target, rate bounds, slew, "
         "underrun or recovery policy, or paced-playout host exists.",
         "Supply exact controller geometry and an instrumented host that "
         "records queue debt, fill/flush, underruns and recovery."),
        ("RG-05", "rights-cleared cohort and source timestamps",
         "No rights-cleared speech, music, silence or transient cohort with "
         "source timestamps and output use exists.",
         "Freeze the cohort, terms and source timestamps, then validate one "
         "invalid and one representative valid case through the bundle."),
        ("RG-06", "matched Rate-profile results and controls",
         "No matched CAPSC result or adverse/missing/nonfinite control exists; "
         "only synthetic integer accounting is present here.",
         "Run 1x, rate changes, drift, rebuffer, final partial window and "
         "invalid/nonfinite controls on the admitted runtime and cohort."),
        ("RG-07", "listening, preservation, device timing and resources",
         "No listening, speech-preservation, target-device timing, underrun "
         "or resource measurement exists.",
         "Measure speech preservation, transient audibility, queue debt, "
         "underruns, recovery, deadlines, CPU, memory and energy on the "
         "intended device."),
        ("RG-08", "OFF-by-default intake and release review",
         "No provider/pipeline intake, descriptor/config, OFF default, "
         "registry/ABI/default/shared-build/CI decision or independent "
         "review exists.",
         "Open a separate versioned OFF-by-default intake with clean-install "
         "proof and independent exact-head review after the prior gates."),
    )
    return [{
        "id": gate_id,
        "title": title,
        "statement": statement,
        "reopen_condition": reopen,
        "status": "blocked",
        "qualifies": False,
        "linked_row": linked_row,
    } for gate_id, title, statement, reopen in rows]


def _rate_profile_rows() -> list[dict[str, Any]]:
    rows = (
        ("RATE-01", "1x control",
         "No CAPSC 1x render or identity control exists."),
        ("RATE-02", "source/output mapping and rate changes",
         "No admitted rate actuator or mapping trace exists."),
        ("RATE-03", "duration",
         "No measured CAPSC output duration or error exists."),
        ("RATE-04", "pitch",
         "No rendered waveform, pitch measurement or listening exists."),
        ("RATE-05", "transient audibility",
         "No waveform analysis, listening or transient result exists."),
        ("RATE-06", "playback buffering, rebuffer, drift, queue debt, "
                   "underruns and recovery",
         "Only synthetic integer queue accounting exists; no device or "
         "admitted runtime was measured."),
        ("RATE-07", "unfamiliar speech, music and silence",
         "No rights-cleared stratified cohort exists."),
        ("RATE-08", "final partial window and speech preservation",
         "Only synthetic final-window arithmetic exists; no CAPSC output or "
         "preservation score exists."),
    )
    return [{
        "id": row_id,
        "requirement": requirement,
        "evidence": evidence,
        "status": "blocked",
        "qualifies": False,
    } for row_id, requirement, evidence in rows]


def _rate_outcomes() -> list[dict[str, Any]]:
    rows = (
        ("OUT-01", "1x control"),
        ("OUT-02", "source/output mapping and rate changes"),
        ("OUT-03", "duration"),
        ("OUT-04", "pitch"),
        ("OUT-05", "transient audibility"),
        ("OUT-06", "playback buffering, rebuffer, drift and queue debt"),
        ("OUT-07", "underruns and recovery"),
        ("OUT-08", "unfamiliar speech, music, silence, final partial window "
                   "and speech preservation"),
    )
    return [{
        "id": row_id,
        "requirement": requirement,
        "status": "blocked",
        "value": None,
        "qualifies": False,
    } for row_id, requirement in rows]


def _qualification() -> dict[str, Any]:
    return {
        "status": "not_qualified",
        "decision": "DEFER",
        "proposal_only": True,
        "evidence_status": "incomplete",
        "capsc_artifact_present": False,
        "capsc_paper_present": False,
        "licensed_implementation_runtime_present": False,
        "candidate_note_present": True,
        "controller_geometry_present": False,
        "qualified_estimator_present": False,
        "rights_cleared_cohort_present": False,
        "matched_result_present": False,
        "device_timing_present": False,
        "blocked_release_gates": 8,
        "open_blockers": 6,
        "qualifying_results": 0,
        "reasons": [
            "no CAPSC paper or official artifact with exact identity and "
            "SHA-256 exists in the workspace",
            "no CAPSC licence grant, terms review or patent counsel decision "
            "exists",
            "no CAPSC controller geometry or public paced-playout adapter "
            "exists",
            "no qualified speech/content estimator separated from the "
            "controller exists",
            "no rights-cleared cohort, matched result or listening exists",
            "no target-device timing, underrun, recovery or release review "
            "exists",
        ],
    }


def _report_core(projection: dict[str, Any],
                 linked_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "qualification": _qualification(),
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "qualification_status": "not_qualified",
            "qualifying_results": 0,
            "blocked_before": "implementation_or_intake",
            "blocked_release_gates": 8,
        },
        "boundary": {
            "task_local_only": True,
            "write_scope": TASK_PREFIX + " only",
            "provider_registration": False,
            "descriptor_or_registry_change": False,
            "default_change": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "board_or_handoff_change": False,
            "external_assets_copied": False,
        },
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "f32",
            "unchanged": True,
        },
        "scope": {
            "directory": TASK_PREFIX,
            "task_local_only": True,
            "audio_read": False,
            "audio_played": False,
            "render_produced": False,
            "real_assets_used": False,
            "real_runtime_used": False,
            "capsc_runtime_imported": False,
            "capsc_runtime_invoked": False,
            "device_inspected": False,
            "device_timing_measured": False,
            "listening_conducted": False,
            "benchmark_run": False,
            "benchmark_claim": False,
            "release_claim": False,
            "network_used": False,
            "download_attempted": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
        },
        "non_claims": [
            "No result in this package is a qualification, benchmark or "
            "release.",
            "No CAPSC paper, source, binary, runtime, model, dataset or "
            "licence text was copied, imported, built, loaded or "
            "reconstructed.",
            "The candidate note only names CAPSC and its DOI; it is not CAPSC "
            "source, a parameter set or a measured result.",
            "The section 8.6 debt-controller formulation in the note is "
            "research with an explicit patent warning; it is not CAPSC and "
            "is not used, shipped or recommended here.",
            "The synthetic queue-debt controller, underrun and recovery "
            "arithmetic are deterministic controls only; they are not CAPSC "
            "and not runtime, device or audio evidence.",
            "No audio was read or played; no cohort, consent or output-use "
            "grant exists.",
            "No queue debt, underrun, recovery, duration, pitch, transient, "
            "buffering, rebuffer, drift or final-partial result was measured "
            "on a real system.",
            "No listening, target-device timing, resource, benchmark or "
            "release review was performed.",
            "No provider, descriptor, registry, default, installed-v0, ABI, "
            "shared-build, CI, board or handoff file is changed.",
        ],
        "observed_provenance": {
            "candidate_note": candidate_note_probe(),
            "debt_controller_guard": debt_controller_guard(),
            "sibling_evidence": [dict(row) for row in LINKED_ROWS],
        },
        "documented_parameter_envelope": documented_parameter_envelope(),
        "synthetic_control_envelope": synthetic_control_envelope(),
        "source_presence": source_presence(),
        "license_findings": license_findings(),
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "required_results": {
            "capsc_paper_and_artifact_admitted": False,
            "capsc_license_and_patent_decision": False,
            "controller_geometry_admitted": False,
            "paced_playout_host_present": False,
            "qualified_estimator_present": False,
            "rights_cleared_cohort_present": False,
            "matched_rate_profile_result": False,
            "listening_and_preservation_measured": False,
            "device_timing_and_underruns_measured": False,
            "provider_intake_approved": False,
            "release_approved": False,
            "no_result_qualifies": True,
        },
        "reproduction": {
            "byte_identical_required": True,
            "repeat_count": 3,
            "python": "3.11 or newer, standard library only",
            "network_used": False,
            "commands": [
                "export PYTHONDONTWRITEBYTECODE=1",
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
        },
        "gates": _release_gates(linked_row),
        "rate_profile": {
            "rows": _rate_profile_rows(),
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
        },
        "rate_outcomes": {"rows": _rate_outcomes()},
        "linked_row_identity": {
            "projection": projection,
            "sha256": board_row_digest(projection),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": [dict(row) for row in LINKED_ROWS],
            "linked_rows_sha256": linked_rows_digest(),
        },
    }


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    linked_row = dict(projection)
    core = _report_core(projection, linked_row)
    return {
        "schema_id": CONTRACT_ID,
        "contract_version": "0.1",
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": core["qualification"],
        "qualification_status": "not_qualified",
        "disposition": core["disposition"],
        "boundary": core["boundary"],
        "public_v0_geometry": core["public_v0_geometry"],
        "scope": core["scope"],
        "non_claims": core["non_claims"],
        "observed_provenance": core["observed_provenance"],
        "documented_parameter_envelope":
            core["documented_parameter_envelope"],
        "synthetic_control_envelope": core["synthetic_control_envelope"],
        "source_presence": core["source_presence"],
        "license_findings": core["license_findings"],
        "required_artifacts": core["required_artifacts"],
        "exact_blockers": core["exact_blockers"],
        "required_results": core["required_results"],
        "reproduction": core["reproduction"],
        "release_gates": core["gates"],
        "rate_profile_requirements": core["rate_profile"]["rows"],
        "rate_outcomes": core["rate_outcomes"]["rows"],
        "linked_row_projection": projection,
        "linked_row_projection_sha256": board_row_digest(projection),
        "linked_rows": core["linked_row_identity"]["linked_rows"],
        "linked_rows_sha256":
            core["linked_row_identity"]["linked_rows_sha256"],
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "debt_controller_guard": core["observed_provenance"][
            "debt_controller_guard"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
    }


def build_report() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    linked_row = dict(projection)
    core = _report_core(projection, linked_row)
    contract = build_contract()
    source_pins, boundary_pins, sibling_pins = verify_pins()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "contract_sha256": object_digest(contract),
        "disposition": core["disposition"],
        "qualification": core["qualification"],
        "boundary": core["boundary"],
        "public_v0_geometry": core["public_v0_geometry"],
        "scope": core["scope"],
        "non_claims": core["non_claims"],
        "observed_provenance": core["observed_provenance"],
        "documented_parameter_envelope":
            core["documented_parameter_envelope"],
        "synthetic_control_envelope": core["synthetic_control_envelope"],
        "source_presence": core["source_presence"],
        "license_findings": core["license_findings"],
        "required_artifacts": core["required_artifacts"],
        "exact_blockers": core["exact_blockers"],
        "required_results": core["required_results"],
        "reproduction": core["reproduction"],
        "gates": core["gates"],
        "rate_profile": core["rate_profile"],
        "rate_outcomes": core["rate_outcomes"],
        "linked_row_identity": core["linked_row_identity"],
        "board_snapshot": {
            "path": BOARD_TASK_ROW,
            "mutable": True,
            "note": "Mutable board path recorded for provenance only; never "
                    "hashed, gated or treated as a result.",
        },
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "sibling_pins": sibling_pins,
        "controller_control": controller_controls(),
        "invalid_control": invalid_controls(),
        "playout_control": playout_controls(),
        "separation_control": separation_control(),
        "final_partial_control": final_partial_control(),
        "admission": admission_controls(),
        "debt_controller_guard":
            core["observed_provenance"]["debt_controller_guard"],
    }


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("ascii"), sha256_bytes(payload)


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "schema_id", "contract_version", "task", "component", "decision",
        "status", "proposal_only", "qualification_status", "disposition",
        "boundary", "scope", "non_claims", "release_gates",
        "rate_profile_requirements", "rate_outcomes", "linked_row_projection",
        "source_pins", "boundary_pins", "sibling_pins",
        "debt_controller_guard", "board_file_pinned",
        "board_status_is_observation_only",
    )
    missing = [field for field in required if field not in contract]
    if missing:
        raise ValueError("contract_missing_fields")
    if contract["schema_id"] != CONTRACT_ID:
        raise ValueError("contract_schema_mismatch")
    if contract["task"] != TASK or contract["component"] != COMPONENT_ID:
        raise ValueError("contract_identity_mismatch")
    if contract["decision"] != "DEFER" or contract["status"] != "incomplete":
        raise ValueError("contract_disposition_mismatch")
    if contract["qualification_status"] != "not_qualified":
        raise ValueError("contract_qualification_mismatch")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    if len(contract["release_gates"]) != 8:
        raise ValueError("contract_gate_count")
    if len(contract["rate_profile_requirements"]) != 8:
        raise ValueError("contract_rate_row_count")
    if len(contract["rate_outcomes"]) != 8:
        raise ValueError("contract_rate_outcome_count")
    if BOARD_TASK_ROW in contract["source_pins"]:
        raise ValueError("contract_board_pinned")
    projection = contract["linked_row_projection"]
    if set(projection) != set(BOARD_ROW_FIELDS):
        raise ValueError("contract_projection_fields")
    if any(field in projection for field in BOARD_STATUS_FIELDS):
        raise ValueError("contract_projection_has_mutable_field")


def verify_sources_manifest(payload: bytes) -> int:
    checked = 0
    for line in payload.decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or not HEX64.match(parts[0]):
            raise ValueError("sources_malformed")
        digest, name = parts
        if name.startswith("source:"):
            path = AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("boundary:") or name.startswith("sibling:"):
            path = WORKTREE / name.split(":", 1)[1]
        else:
            path = WORKTREE / name
        if not path.is_file():
            raise ValueError("sources_missing:" + name)
        if sha256_file(path) != digest:
            raise ValueError("sources_mismatch:" + name)
        checked += 1
    if BOARD_TASK_ROW in payload.decode("ascii"):
        raise ValueError("sources_board_pinned")
    return checked
