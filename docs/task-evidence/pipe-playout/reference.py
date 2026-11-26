# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-PIPE-PLAYOUT.

This module is standard-library only and deterministic. It models the admitted
shape of the buffered fixed-rate playback recipe:

    timestamped PCM -> optional advisory annotation -> explicit fixed-rate
    Bungee Basic -> peak limiter

The Bungee Basic source checkout and a local static build are present outside
this worktree and are pinned as provenance, but no admitted runtime artifact,
rights-cleared playback cohort, qualified annotation provider, qualified
limiter integration, listening result or target-device timing is supplied.
Consequently the Bungee stage is never admitted or invoked. The only executed
path is an explicit 1x bypass over small synthetic fixed-point fixtures. It
verifies admission, sample conservation, finite input/output, no unintended
gap and zero delay for the bypass. It produces no Bungee rate result and no
result here qualifies the candidate.

No real audio, corpus, model, weight, native library or runtime is read,
linked, built, loaded or executed. The report is canonical JSON with no floats.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
from pathlib import Path
from typing import Any

TASK = "SDK-PIPE-PLAYOUT"
COMPONENT_ID = "pipe-playout"
TASK_TITLE = "Buffered fixed-rate playback"
CONTRACT_ID = "audio-sdk/pipe-playout-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "pipeline"
PROFILE_LABEL = "Pipeline"
MODE = "pipeline"
BASE_COMMIT = "82c0a6e6ee5811190588fe5d17254b494d42cd2c"
BRANCH = "swarm/SDK-PIPE-PLAYOUT"
WRITE_SCOPE = "docs/task-evidence/pipe-playout/ only"
TASK_PREFIX = "docs/task-evidence/pipe-playout/"
DISPOSITION = (
    "Bounded buffered fixed-rate playback readiness blocker; no admitted "
    "Bungee Basic runtime, rights-cleared playback cohort, listening or "
    "device-timing result, and no qualifying pipeline result.")

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
RATE_MIN_PPM = 500000
RATE_MAX_PPM = 2500000
BYPASS_RATE_PPM = 1000000
ANNOTATION_KINDS = ("speech", "music", "silence", "transition", "unknown")

BUNGEE_SOURCE_REVISION = "61f52bf34be577d189d388772ddfa3696dee77d8"
BUNGEE_SOURCE_TREE = "c8edb5f21ad58472d8ce6f635fa3e6c707474ca6"
BUNGEE_LICENSE = "MPL-2.0"
BUNGEE_STATIC_LIBRARY_BYTES = 88880
BUNGEE_STATIC_LIBRARY_SHA256 = (
    "bd217d069a458436ed8444bf6cb83a3d79889b4a32bff768b9015f956452fae1")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
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

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/audio-sdk/PIPELINES.md":
        "4d950978277dff9c562059d25d43ad5d2a85a46bb7a97aabb8518edaa0faea47",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-stretchers/REPORT.md":
        "8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb",
    "cpp-library/pipeline-validation/playback-speed/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "data/checkouts/tsm-engines-20261101/bungee/LICENSE":
        "86cf9656479f1edb82245b985f4a2cc0d503b945766ebeda4269c60b307699ae",
    "data/checkouts/tsm-engines-20261101/bungee/bungee/Bungee.h":
        "91ac529c35f527401add72030290ab65639d28f3a0cedd3c85ca361692b3d514",
    "data/checkouts/tsm-engines-20261101/bungee/bungee/Stream.h":
        "88e68f39fca48671fbccf6f376b8527215608cbc3ac5de117361d4c014c257d9",
    "data/checkouts/tsm-engines-20261101/bungee/CMakeLists.txt":
        "72e48f2f6e6d90430a10710d03d0baf24c2d719e24c936aec0c802e0280ae268",
    "data/checkouts/tsm-engines-20261101/bungee/.gitmodules":
        "65c8a5ee9a24ab50ca67a0811bf697a63ad8d171f89af26fe917713a2627eed3",
    "data/checkouts/tsm-engines-20261101/bungee/build-rel/libbungee.a":
        BUNGEE_STATIC_LIBRARY_SHA256,
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/bungee-basic/report.json":
        "bb434059ae6c3d07e247d7568d1dad3aab9441194f3b57c54851df4298447f8b",
    "docs/task-evidence/bungee-basic/native_report.json":
        "f3293f15aa12a56e1c377f56ca93f0284221e1c5dde825ba893de4bfe37a3a42",
    "docs/task-evidence/buffer-occupancy-controller/report.json":
        "9dc73683b42a47801efcd71449b7d93fbd40a490beae54c46cc29680ebead47c",
    "docs/task-evidence/pipe-control/report.json":
        "64428914ee08309ab0bb3e18eec739d59f543711f342e488673ddd6246fe21ec",
    "docs/task-evidence/pipe-capture/report.json":
        "30734c321a8150cc2adea332e3b2c8daeeea24eb64b733fdfc0d0efd00609a37",
    "docs/task-evidence/pipe-duplex/report.json":
        "ff69e229d35fa6cff3729f1ed66dfb277b9319e050adc7aa0e485337476986f4",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "BENCH-FND-CHECK", "SDK-BUNGEE-BASIC",
                  "SDK-FND-ANALYSIS", "SDK-FND-ELASTIC",
                  "SDK-PEAK-LIMITER-REFERENCE")

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "sample_format": SAMPLE_FORMAT,
    "changed": False,
}

SCOPE = {
    "task_local_only": True,
    "write_scope": WRITE_SCOPE,
    "provider_registered": False,
    "public_abi_changed": False,
    "registry_or_default_changed": False,
    "shared_build_or_ci_changed": False,
    "real_assets_used": False,
    "real_runtime_used": False,
    "audio_read": False,
    "listening_performed": False,
    "device_timing_measured": False,
    "benchmark_run": False,
    "network_used": False,
    "release_claim": False,
}

NON_CLAIMS = [
    "No Bungee Basic source, header, object, static library, binary, provider "
    "or adapter is linked, imported, built, loaded or executed by this package.",
    "No real audio, corpus, model, weight, annotation asset or runtime is "
    "read, downloaded, decoded or scored.",
    "No rate change, time stretch, pitch preservation or duration result on "
    "Bungee Basic or the installed SDK is measured.",
    "The synthetic fixed-point 1x bypass is an admission and conservation "
    "control only; it is not an installed float32 SDK passthrough result.",
    "No listening, naturalness, transient-audibility or speech-preservation "
    "result exists.",
    "No target-device timing, callback deadline, buffering, rebuffer, drift, "
    "underrun, CPU, memory, energy or thermal measurement exists.",
    "No benchmark, provider, registry, descriptor, default, shared build, "
    "installed v0 or CI change exists.",
    "No release or qualification claim is made; the decision is DEFER.",
    "The unknown-annotation/no-mutation policy is modelled, not validated on "
    "real audio.",
    "A 1x bypass is not a substitute for Bungee Basic or a rate-change result.",
]

REQUIRED_RESULTS = [
    "Admitted Bungee Basic runtime with exact source revision/tree, build "
    "recipe, toolchain, binary digest and MPL-2.0 distribution decision.",
    "Rights-cleared playback cohort with natural speech, music, transitions, "
    "silence and independently tagged impulses, source timestamps and terms.",
    "Qualified advisory speech/rate annotation provider and explicit "
    "unknown/missing annotation policy.",
    "Qualified peak limiter integration for this exact chain with finite-output "
    "and peak/recovery evidence.",
    "Deterministic end-to-end pipeline host and real-audio result for 1x, "
    "fixed rates, rate steps, finite flush and impulse-tagged delay.",
    "Separate speech, music and transition scoring with adverse, missing and "
    "nonfinite controls.",
    "Permitted listening and paced target-device timing/resource evidence.",
    "Separate OFF-by-default provider intake and independent exact-head review.",
]

QUALIFICATION = {
    "status": "not_qualified",
    "readiness": "incomplete",
    "not_qualified": True,
    "all_release_gates_blocked": True,
    "real_result_present": False,
    "pipeline_result_present": False,
    "admitted_runtime_present": False,
    "bungee_source_present": True,
    "bungee_build_present": True,
    "rights_cleared_assets_present": False,
    "qualified_annotation_present": False,
    "qualified_limiter_integration_present": False,
    "listening_result": False,
    "device_timing_result": False,
    "benchmark_result": False,
    "release_claim": False,
    "missing_result_promoted": False,
}


def _project_row(row: dict) -> dict:
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def _board_tasks(path: Path) -> list[dict]:
    document = read_strict_json(path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    return tasks


def board_row_projection(path: Path) -> dict:
    for row in _board_tasks(path):
        if isinstance(row, dict) and row.get("id") == TASK:
            return _project_row(row)
    raise ValueError("board_row_missing:" + TASK)


def linked_rows(path: Path | None = None) -> list[dict]:
    source = path or (AUDIO_ROOT / BOARD_TASK_ROW)
    by_id = {
        row.get("id"): row
        for row in _board_tasks(source)
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    rows: list[dict] = []
    for identifier in LINKED_ROW_IDS:
        row = by_id.get(identifier)
        if row is None:
            raise ValueError("linked_row_missing:" + identifier)
        rows.append(_project_row(row))
    return rows


def board_row_digest(projection: dict | None = None) -> str:
    row = projection if projection is not None else board_row_projection(
        AUDIO_ROOT / BOARD_TASK_ROW)
    return object_digest(row)


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reject_constant(value: str) -> Any:
    raise ValueError("nonfinite_json:" + value)


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    document: dict = {}
    for key, value in pairs:
        if key in document:
            raise ValueError("duplicate_json_key:" + key)
        document[key] = value
    return document


def loads_strict(text: str) -> dict:
    if text.startswith("\ufeff"):
        raise ValueError("json_bom")
    value = json.loads(text, object_pairs_hook=_pairs,
                       parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def read_strict_json(path: Path) -> dict:
    return loads_strict(path.read_text(encoding="utf-8"))


def canonical_text(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False) + "\n"


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: Any) -> str:
    return sha256_bytes(canonical_bytes(document))


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("json_float")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("json_nonstring_key")
            _no_floats(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _no_floats(item)


# ---------------------------------------------------------------------------
# Deterministic synthetic fixed-point fixtures and the admitted bypass model.
# Samples are integer parts-per-million (ppm) of full scale. They are not real
# audio and are not float32 SDK buffers. No float enters the canonical report.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, amplitude: int) -> int:
    half = period // 2
    phase = index % period
    if phase < half:
        return -amplitude + (2 * amplitude * phase) // half
    return amplitude - (2 * amplitude * (phase - half)) // (period - half)


def _envelope(index: int, length: int, attack: int, release: int) -> int:
    if index < attack:
        return (1_000_000 * index) // attack
    if index >= length - release:
        return (1_000_000 * (length - 1 - index)) // release
    return 1_000_000


def _mix(index: int, length: int, partials: tuple[tuple[int, int], ...],
         attack: int, release: int) -> int:
    gain = _envelope(index, length, attack, release)
    value = sum(_triangle(index, period, amplitude)
                for period, amplitude in partials)
    value = (value * gain) // 1_000_000
    return max(-900000, min(900000, value))


def _frame(flat: list[int], start: int, count: int) -> list[int]:
    return flat[start:start + count]


def impulse_fixture() -> tuple[list[list[int]], list[int]]:
    flat = [0] * (6 * FRAME_SAMPLES)
    tagged = [5, 165, 325, 485, 645, 805]
    amplitudes = [250000, 500000, 750000, -250000, -500000, -750000]
    for position, amplitude in zip(tagged, amplitudes):
        flat[position] = amplitude
    return [flat[i:i + FRAME_SAMPLES]
            for i in range(0, len(flat), FRAME_SAMPLES)], tagged


def speech_proxy_fixture() -> list[list[int]]:
    length = 10 * FRAME_SAMPLES
    flat = [_mix(i, length, ((80, 180000), (53, 120000), (37, 90000)),
                 80, 160) for i in range(length)]
    return [flat[i:i + FRAME_SAMPLES]
            for i in range(0, length, FRAME_SAMPLES)]


def music_proxy_fixture() -> list[list[int]]:
    length = 10 * FRAME_SAMPLES
    flat = [_mix(i, length, ((100, 200000), (75, 160000), (60, 120000),
                             (50, 80000)), 40, 120) for i in range(length)]
    return [flat[i:i + FRAME_SAMPLES]
            for i in range(0, length, FRAME_SAMPLES)]


def transition_fixture() -> list[list[int]]:
    frames: list[list[int]] = [[] for _ in range(8)]
    for index in range(len(frames)):
        if index in (2, 3):
            frames[index] = speech_proxy_fixture()[index]
        elif index in (5, 6):
            frames[index] = music_proxy_fixture()[index]
        elif index == 7:
            frames[index] = [
                (speech_proxy_fixture()[7][i] * (FRAME_SAMPLES - 1 - i))
                // (FRAME_SAMPLES - 1)
                for i in range(FRAME_SAMPLES)]
        else:
            frames[index] = [0] * FRAME_SAMPLES
    return frames


def final_partial_fixture() -> tuple[list[list[int]], int]:
    total = 3 * FRAME_SAMPLES + 37
    flat = [_mix(i, total, ((80, 180000), (53, 120000)), 40, 80)
            for i in range(total)]
    frames = [flat[i:i + FRAME_SAMPLES] for i in range(0, total,
                                                       FRAME_SAMPLES)]
    return frames, total


def request(case_id: str, frames: list[list[int]], rate_ppm: int = BYPASS_RATE_PPM,
            annotation: dict | None = None, capacity: int = 64,
            final: bool = False, tagged: list[int] | None = None,
            sample_rate_hz: int = SAMPLE_RATE_HZ) -> dict:
    return {
        "case_id": case_id,
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "frames": frames,
        "final": final,
        "requested_rate_ppm": rate_ppm,
        "annotation": annotation,
        "buffer_capacity_frames": capacity,
        "tagged_impulse_positions": tagged or [],
    }


def _nice_annotation(kind: str = "speech", start: int = 0,
                     end: int = FRAME_SAMPLES) -> dict:
    return {"kind": kind, "start_sample": start, "end_sample": end,
            "confidence_ppm": 900000}


def _to_ppm(value: Any) -> tuple[int, bool]:
    """Return (ppm, finite). Raises on a nonfinite or invalid value."""
    if isinstance(value, bool):
        raise ValueError("bool_sample")
    if isinstance(value, int):
        ppm = value
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite_sample")
        ppm = round(value * 1_000_000)
    else:
        raise ValueError("sample_type")
    if ppm < -2_000_000 or ppm > 2_000_000:
        raise ValueError("sample_range")
    return ppm, True


def _rejected(case_id: str, code: str, message: str, input_samples: int | None,
              finite_input: bool, requested_rate: Any) -> dict:
    return {
        "case_id": case_id,
        "status": "rejected",
        "code": code,
        "message": message,
        "input_samples": input_samples,
        "delivered_samples": 0,
        "input_sha256": None,
        "output_sha256": None,
        "bit_exact": False,
        "duration_error_samples": None,
        "gap_count": None,
        "peak_ppm": None,
        "finite_input": finite_input,
        "finite_output": True,
        "state_advanced": False,
        "annotation_effect": "none",
        "requested_rate_ppm": requested_rate,
        "applied_rate_ppm": None,
        "bypass": False,
        "bypass_reason": None,
        "bungee_invoked": False,
        "limiter_changed": False,
        "tagged_impulse_positions": [],
        "tagged_impulse_delay_samples": None,
        "real_rate_path_delay_samples": None,
        "qualifies": False,
    }


def _accepted(case_id: str, samples: list[int], annotation_effect: str,
              requested_rate: int, bypass_reason: str,
              tagged: list[int]) -> dict:
    output = list(samples)
    packed = b"".join(struct.pack("<i", value) for value in output)
    return {
        "case_id": case_id,
        "status": "accepted_bypass",
        "code": "accepted_bypass",
        "message": "explicit 1x bypass; synthetic fixed-point control only",
        "input_samples": len(samples),
        "delivered_samples": len(output),
        "input_sha256": sha256_bytes(packed),
        "output_sha256": sha256_bytes(packed),
        "bit_exact": output == samples,
        "duration_error_samples": len(output) - len(samples),
        "gap_count": 0,
        "peak_ppm": max((abs(value) for value in output), default=0),
        "finite_input": True,
        "finite_output": True,
        "state_advanced": True,
        "annotation_effect": annotation_effect,
        "requested_rate_ppm": requested_rate,
        "applied_rate_ppm": BYPASS_RATE_PPM,
        "bypass": True,
        "bypass_reason": bypass_reason,
        "bungee_invoked": False,
        "limiter_changed": False,
        "tagged_impulse_positions": list(tagged),
        "tagged_impulse_delay_samples": 0,
        "real_rate_path_delay_samples": None,
        "qualifies": False,
    }


def run_pipeline(specification: dict) -> dict:
    """Validate and execute only the admitted 1x bypass path."""
    case_id = str(specification.get("case_id", "unnamed"))
    requested_rate = specification.get("requested_rate_ppm")

    if specification.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        return _rejected(case_id, "rejected_geometry",
                         "sample_rate_hz must be 16000", None, True,
                         requested_rate)
    if specification.get("channels") != CHANNELS:
        return _rejected(case_id, "rejected_geometry",
                         "channels must be 1", None, True, requested_rate)
    if specification.get("frame_samples") != FRAME_SAMPLES:
        return _rejected(case_id, "rejected_geometry",
                         "frame_samples must be 160", None, True,
                         requested_rate)

    frames = specification.get("frames")
    if not isinstance(frames, list) or not frames:
        return _rejected(case_id, "rejected_frame_count",
                         "at least one frame is required", 0, True,
                         requested_rate)
    final = specification.get("final") is True
    for index, frame in enumerate(frames):
        if not isinstance(frame, list):
            return _rejected(case_id, "rejected_frame_type",
                             "frames must be lists", None, True,
                             requested_rate)
        if index < len(frames) - 1 or not final:
            if len(frame) != FRAME_SAMPLES:
                return _rejected(case_id, "rejected_frame_length",
                                 "nonfinal frames must have 160 samples",
                                 None, True, requested_rate)
        else:
            if not 1 <= len(frame) <= FRAME_SAMPLES:
                return _rejected(case_id, "rejected_frame_length",
                                 "final partial frame must have 1..160 samples",
                                 None, True, requested_rate)

    total = sum(len(frame) for frame in frames)

    capacity = specification.get("buffer_capacity_frames")
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        return _rejected(case_id, "rejected_buffer_capacity",
                         "buffer_capacity_frames must be a positive integer",
                         total, True, requested_rate)
    buffer_unavailable = capacity < len(frames)

    if not isinstance(requested_rate, int) or isinstance(requested_rate, bool):
        return _rejected(case_id, "rejected_rate_type",
                         "requested_rate_ppm must be an integer", total, True,
                         requested_rate)
    if not RATE_MIN_PPM <= requested_rate <= RATE_MAX_PPM:
        return _rejected(case_id, "rejected_rate_range",
                         "requested_rate_ppm outside 0.5x..2.5x", total, True,
                         requested_rate)

    annotation = specification.get("annotation")
    if annotation is None:
        annotation_kind = "unknown"
        annotation_effect = "missing_annotation_unchanged"
    elif not isinstance(annotation, dict):
        return _rejected(case_id, "rejected_invalid_annotation",
                         "annotation must be an object or null", total, True,
                         requested_rate)
    else:
        annotation_kind = annotation.get("kind", "unknown")
        if annotation_kind not in ANNOTATION_KINDS:
            return _rejected(case_id, "rejected_unsupported_annotation",
                             "unsupported annotation kind", total, True,
                             requested_rate)
        start = annotation.get("start_sample")
        end = annotation.get("end_sample")
        confidence = annotation.get("confidence_ppm")
        if not isinstance(start, int) or isinstance(start, bool) \
                or not isinstance(end, int) or isinstance(end, bool):
            return _rejected(case_id, "rejected_invalid_annotation",
                             "annotation interval must be integers", total,
                             True, requested_rate)
        if not 0 <= start < end <= total:
            return _rejected(case_id, "rejected_invalid_annotation",
                             "annotation interval outside source", total, True,
                             requested_rate)
        if not isinstance(confidence, int) or isinstance(confidence, bool) \
                or not 0 <= confidence <= 1_000_000:
            return _rejected(case_id, "rejected_invalid_annotation",
                             "confidence_ppm must be 0..1000000", total, True,
                             requested_rate)
        annotation_effect = (
            "unknown_annotation_unchanged" if annotation_kind == "unknown"
            else "known_annotation_no_runtime_mutation")

    samples: list[int] = []
    for frame in frames:
        for value in frame:
            try:
                ppm, _ = _to_ppm(value)
            except ValueError as error:
                nonfinite = "nonfinite" in str(error)
                return _rejected(
                    case_id,
                    "rejected_nonfinite_sample" if nonfinite
                    else "rejected_sample_value",
                    str(error), total, not nonfinite, requested_rate)
            samples.append(ppm)

    if buffer_unavailable:
        return _accepted(case_id, samples, annotation_effect, requested_rate,
                         "buffer_unavailable",
                         specification.get("tagged_impulse_positions", []))
    if requested_rate != BYPASS_RATE_PPM:
        return _accepted(case_id, samples, annotation_effect, requested_rate,
                         "bungee_runtime_not_admitted",
                         specification.get("tagged_impulse_positions", []))
    return _accepted(case_id, samples, annotation_effect, requested_rate,
                     "1x_passthrough",
                     specification.get("tagged_impulse_positions", []))


def _control_specs() -> list[dict]:
    impulse, tagged = impulse_fixture()
    speech = speech_proxy_fixture()
    music = music_proxy_fixture()
    transition = transition_fixture()
    partial, partial_total = final_partial_fixture()

    nonfinite = [list(frame) for frame in speech]
    nonfinite[0][0] = float("nan")
    wrong_length = [list(frame) for frame in speech]
    wrong_length[0] = wrong_length[0][:-1]

    return [
        {"id": "identity_impulse_1x",
         "request": request("identity_impulse_1x", impulse,
                            annotation=_nice_annotation("speech", 0, 960),
                            tagged=tagged),
         "expected": "accepted_bypass"},
        {"id": "unknown_annotation_1_5x",
         "request": request("unknown_annotation_1_5x", impulse,
                            rate_ppm=1_500_000,
                            annotation=_nice_annotation("unknown", 0, 960),
                            tagged=tagged),
         "expected": "accepted_bypass"},
        {"id": "missing_annotation_1_5x",
         "request": request("missing_annotation_1_5x", speech,
                            rate_ppm=1_500_000),
         "expected": "accepted_bypass"},
        {"id": "rate_1_25x_blocked",
         "request": request("rate_1_25x_blocked", speech,
                            rate_ppm=1_250_000,
                            annotation=_nice_annotation("speech", 0, 1600)),
         "expected": "accepted_bypass"},
        {"id": "speech_proxy_1x",
         "request": request("speech_proxy_1x", speech,
                            annotation=_nice_annotation("speech", 0, 1600)),
         "expected": "accepted_bypass"},
        {"id": "music_proxy_1x",
         "request": request("music_proxy_1x", music,
                            annotation=_nice_annotation("music", 0, 1600)),
         "expected": "accepted_bypass"},
        {"id": "transition_proxy_1x",
         "request": request("transition_proxy_1x", transition,
                            annotation=_nice_annotation("transition", 0, 1280)),
         "expected": "accepted_bypass"},
        {"id": "final_partial_1x",
         "request": request("final_partial_1x", partial,
                            annotation=_nice_annotation("speech", 0,
                                                        partial_total),
                            capacity=8, final=True),
         "expected": "accepted_bypass"},
        {"id": "buffer_unavailable_bypass",
         "request": request("buffer_unavailable_bypass", speech,
                            rate_ppm=1_500_000, capacity=2),
         "expected": "accepted_bypass"},
        {"id": "invalid_annotation_rejected",
         "request": request("invalid_annotation_rejected", speech,
                            annotation=_nice_annotation("speech", -1, 160)),
         "expected": "rejected"},
        {"id": "unsupported_annotation_rejected",
         "request": request("unsupported_annotation_rejected", speech,
                            annotation=_nice_annotation("phoneme", 0, 160)),
         "expected": "rejected"},
        {"id": "nonfinite_rejected",
         "request": request("nonfinite_rejected", nonfinite),
         "expected": "rejected"},
        {"id": "missing_frames_rejected",
         "request": request("missing_frames_rejected", []),
         "expected": "rejected"},
        {"id": "missing_rate_rejected",
         "request": {**request("missing_rate_rejected", speech),
                     "requested_rate_ppm": None},
         "expected": "rejected"},
        {"id": "wrong_frame_length_rejected",
         "request": request("wrong_frame_length_rejected", wrong_length),
         "expected": "rejected"},
        {"id": "bad_geometry_rejected",
         "request": request("bad_geometry_rejected", speech,
                            sample_rate_hz=48000),
         "expected": "rejected"},
        {"id": "bad_rate_rejected",
         "request": request("bad_rate_rejected", speech, rate_ppm=250000),
         "expected": "rejected"},
    ]


def control_cases() -> list[dict]:
    cases: list[dict] = []
    for specification in _control_specs():
        result = run_pipeline(specification["request"])
        row = {
            "id": specification["id"],
            "expected_status": specification["expected"],
            "synthetic_only": True,
            "qualifies": False,
        }
        row.update(result)
        cases.append(row)
    return cases


def control_summary(cases: list[dict]) -> dict:
    accepted = [case for case in cases
                if case.get("status") == "accepted_bypass"]
    rejected = [case for case in cases if case.get("status") == "rejected"]
    return {
        "case_count": len(cases),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "bypass_count": sum(1 for case in cases if case.get("bypass") is True),
        "qualifying_count": 0,
        "bungee_invoked_count": 0,
        "limiter_changed_count": 0,
        "real_audio_read": False,
        "listening_performed": False,
        "device_timing_measured": False,
        "synthetic_only": True,
        "all_accepted_are_bypass": all(
            case.get("bypass") is True and case.get("bungee_invoked") is False
            for case in accepted),
        "all_rejected_state_unchanged": all(
            case.get("state_advanced") is False for case in rejected),
        "expected_status_matches": all(
            case.get("status") == case.get("expected_status") for case in cases),
    }


def source_presence() -> dict:
    return {
        "bungee_source_present": True,
        "bungee_source_revision": BUNGEE_SOURCE_REVISION,
        "bungee_source_tree": BUNGEE_SOURCE_TREE,
        "bungee_license": BUNGEE_LICENSE,
        "bungee_static_library_present": True,
        "bungee_static_library_bytes": BUNGEE_STATIC_LIBRARY_BYTES,
        "bungee_static_library_sha256": BUNGEE_STATIC_LIBRARY_SHA256,
        "bungee_runtime_admitted": False,
        "bungee_runtime_invoked": False,
        "qualified_runtime_present": False,
        "rights_cleared_speech_music_present": False,
        "pipeline_host_present": False,
        "qualified_annotation_provider_present": False,
        "qualified_limiter_integration_present": False,
        "listening_study_present": False,
        "target_device_timing_present": False,
        "real_pipeline_result_present": False,
        "audio_read": False,
        "runtime_invoked": False,
        "network_used": False,
        "download_attempted": False,
    }


def historical_context() -> dict:
    return {
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "bungee_native_evidence": {
            "source": "docs/task-evidence/bungee-basic/NATIVE.md",
            "source_revision": BUNGEE_SOURCE_REVISION,
            "input": "deterministic synthetic PCM",
            "rates": ["0.5", "0.75", "1.0", "1.25", "1.5", "2.5"],
            "duration_error_max_samples": "2",
            "listening_performed": False,
            "target_device_measured": False,
            "real_ami_audio_used": False,
        },
        "research_pilot_context": {
            "source": "research/tsm-followup-20261101/README.md",
            "input": "ten four-second AMI EN2003a clips",
            "rates": ["0.5", "0.8", "1.0", "1.25", "1.5", "2.5"],
            "duration_error_max_samples": "2",
            "first_output_ms": "100",
            "reported_internal_latency_ms": "147",
            "paired_whisper_wer_delta_pp": {
                "0.5": "+12.5", "1.25": "+0.0", "1.5": "+2.9",
                "2.5": "+42.7"},
            "ami_terms_reviewed_here": False,
            "listening_performed": False,
            "target_device_measured": False,
        },
        "why_not_reproduced": [
            "No admitted Bungee Basic runtime artifact exists for this chain.",
            "No rights-cleared natural-speech, music or transition cohort is "
            "staged.",
            "No qualified annotation provider or limiter integration exists.",
            "No real pipeline host, listening study or target device is "
            "available.",
        ],
    }


def _gate(identifier: str, title: str, statement: str,
          reopen_condition: str, linked_row: dict) -> dict:
    return {
        "id": identifier,
        "title": title,
        "status": "blocked",
        "qualifies": False,
        "statement": statement,
        "reopen_condition": reopen_condition,
        "linked_row": linked_row,
    }


def _release_gates(linked_row: dict) -> list[dict]:
    return [
        _gate(
            "RG-01", "source_runtime_license_and_provenance",
            "Bungee Basic source and a local static build are pinned as "
            "provenance, but no admitted runtime artifact, build recipe, "
            "binary digest, MPL-2.0 distribution decision or product-use "
            "review exists for this pipeline.",
            "Stage the exact source revision/tree, build recipe and toolchain, "
            "binary digest and byte count, MPL-2.0 notice/source-availability/"
            "relink decision and a recorded product-use review.",
            linked_row),
        _gate(
            "RG-02", "rights_cleared_pipeline_assets_and_recipe",
            "No rights-cleared playback cohort, annotation manifest, tagged "
            "impulse set or recipe identity with per-file terms and digests is "
            "staged. AMI research clips are unreviewed and are not read here.",
            "Freeze natural speech, music, transitions, silence and tagged "
            "impulses with source timestamps, exact digests, dataset terms and "
            "an output-use decision.",
            linked_row),
        _gate(
            "RG-03", "qualified_bungee_basic_and_limiter_runtime",
            "The Bungee stage is not admitted and is never invoked. The peak "
            "limiter integration is not qualified for this chain.",
            "Admit an exact Bungee Basic build and limiter descriptor/config "
            "with offline clean-install proof and finite-output checks.",
            linked_row),
        _gate(
            "RG-04", "fixed_rate_pipeline_contract_duration_flush_delay",
            "The package models only admission and synthetic 1x bypass. It "
            "does not measure fixed-rate duration/pitch, rate steps, finite "
            "flush, unintended gaps or impulse-tagged rate-path delay.",
            "Run 1x, fixed rates and step/ramp schedules on the admitted "
            "runtime; record duration/pitch, flush, gap and tagged-impulse "
            "delay with independent references.",
            linked_row),
        _gate(
            "RG-05", "natural_speech_music_transition_cohort_and_controls",
            "Synthetic fixed-point proxies are not natural speech, music or "
            "transitions. No separate cohort scoring or adverse/missing/"
            "nonfinite control on a real pipeline exists.",
            "Score natural speech, music and transitions separately on the "
            "rights-cleared cohort, including missing, adverse and nonfinite "
            "controls.",
            linked_row),
        _gate(
            "RG-06", "listening_naturalness_transient_and_unknown_policy",
            "No permitted listening study, naturalness/transient result or "
            "real-audio validation of the unknown-annotation no-mutation "
            "policy exists.",
            "Run a permitted listening/transition study and prove on real "
            "audio that unknown or missing annotation leaves audio unedited.",
            linked_row),
        _gate(
            "RG-07", "paced_playback_device_timing_buffering_resources",
            "No paced playback, buffering, rebuffer, drift, underrun, "
            "callback/deadline, CPU, memory, energy or thermal measurement "
            "exists on an intended device.",
            "Measure paced playback and target-device timing/resources with "
            "explicit buffers, deadlines and drift schedules.",
            linked_row),
        _gate(
            "RG-08", "provider_intake_public_surface_and_release",
            "No provider/pipeline intake, descriptor, registry, default, "
            "shared build, CI or release decision exists; nothing is "
            "registered or enabled.",
            "Open a separate versioned OFF-by-default intake with exact "
            "descriptor/config, no shared-surface change, clean-install proof "
            "and independent exact-head review after the prior gates clear.",
            linked_row),
    ]


REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "linked_plan_and_merged_sibling_evidence",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The exact task row identity, plan/pipeline profile, contract and "
            "merged sibling buffer-occupancy, rate, playout and Bungee "
            "packages pinned by SHA-256; provenance only."),
        "revision": BASE_COMMIT,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "bungee_basic_admitted_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A reviewed, admitted Bungee Basic runtime artifact for this "
            "pipeline: exact source revision/tree, build recipe/toolchain, "
            "binary SHA-256 and byte count, MPL-2.0 notice/source-availability/"
            "relink decision and product-use approval. The local source "
            "checkout and static build are present but are not an admitted "
            "pipeline artifact."),
        "revision": BUNGEE_SOURCE_REVISION,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "rights_cleared_playback_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A rights-cleared, task-matched playback cohort with natural "
            "speech, music, transitions, silence and independently tagged "
            "impulses, source timestamps, exact digests, terms and "
            "product-use decision."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "qualified_advisory_annotation_provider",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A qualified advisory speech/rate annotation provider and policy: "
            "pinned model/runtime/assets, measured coverage/accuracy, "
            "confidence and unknown semantics, source timestamps and proof "
            "that unknown/missing annotation leaves audio unedited."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "qualified_peak_limiter_integration",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A qualified peak limiter integration for this exact chain: "
            "pinned build/descriptor/config, transparency, peak protection, "
            "recovery and finite-output measurements after the rate stage."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "deterministic_pipeline_host_and_result",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A deterministic end-to-end pipeline host and result on the "
            "qualified runtime/assets: 1x bit-exact passthrough, fixed-rate "
            "Bungee, duration/pitch, no unintended gaps, finite flush, rate "
            "steps/ramp and impulse-tagged output delay."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "listening_and_transition_study",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A permitted listening study on the qualified cohort: "
            "naturalness, transient audibility and speech/music/transition "
            "preservation, with panel, instructions, labels and rights."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-08",
        "kind": "paced_device_timing_and_resources",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "Paced playback and target-device measurement: buffering, "
            "rebuffer, drift, underruns, queue fill/flush, callback/deadline "
            "p95/p99, CPU/memory/energy and thermal behavior."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-09",
        "kind": "provider_intake_and_release_decision",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A separate OFF-by-default versioned provider/pipeline intake "
            "with exact descriptor/config, no registry/default/shared-build/"
            "CI change, clean-install proof and independent exact-head review."),
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "linked_gates": ["RG-01", "RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "Bungee Basic source revision 61f52bf3.../tree c8edb5f2... and a "
            "local static libbungee.a are present outside this worktree, but "
            "no admitted runtime artifact, exact build recipe/toolchain, "
            "binary digest approval, MPL-2.0 distribution decision or "
            "product-use review is supplied. No Bungee code is linked or "
            "executed by this package."),
        "required_action": (
            "Supply the admitted runtime artifact with exact source revision, "
            "tree, build commands, toolchain, binary SHA-256/byte count, "
            "MPL-2.0 notice/source-availability/relink decision and recorded "
            "product-use approval."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "linked_gates": ["RG-02", "RG-05"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared playback cohort is staged. The research pilot "
            "used ten AMI EN2003a clips, but AMI terms were not reviewed here "
            "and no audio byte is read. No cleared music, transition, silence "
            "or tagged-impulse set exists."),
        "required_action": (
            "Freeze a rights-cleared natural speech, music, transition and "
            "silence cohort with tagged impulses, source timestamps, exact "
            "digests, dataset terms and an output-use decision."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "linked_gates": ["RG-02", "RG-04"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "SDK-FND-ANALYSIS defines typed event shapes only. No qualified "
            "speech/rate annotation provider, model, asset, accuracy result "
            "or confidence policy is supplied. The unknown-annotation "
            "no-mutation rule is modelled but not validated on real audio."),
        "required_action": (
            "Supply a qualified advisory annotation provider and policy with "
            "pinned assets, measured coverage/accuracy, source timestamps, "
            "confidence/unknown semantics and no-mutation proof."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "linked_gates": ["RG-03", "RG-04"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "SDK-PEAK-LIMITER-REFERENCE is a separate approved component. No "
            "qualified limiter integration, descriptor/config or chain-stage "
            "measurement after the Bungee stage exists."),
        "required_action": (
            "Supply the exact limiter integration for this chain with pinned "
            "build/config, transparency, peak, recovery and finite-output "
            "evidence."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "linked_gates": ["RG-03", "RG-04"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No deterministic end-to-end pipeline host or real result exists. "
            "This task-local reference models admission and 1x bypass only on "
            "synthetic fixed-point fixtures; it does not enter the Bungee "
            "stage or measure duration/pitch, flush, rate steps or real rate-"
            "path delay."),
        "required_action": (
            "Supply the end-to-end host and result for 1x, fixed rates and "
            "step/ramp schedules, including duration/pitch, finite flush, gap "
            "and tagged-impulse delay measurements."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "linked_gates": ["RG-06"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No listening study or natural-audio scoring exists. Synthetic "
            "speech, music and transition proxies exercise finite integer "
            "bypass only; they are not audio-quality or naturalness evidence."),
        "required_action": (
            "Run a permitted listening/transition study on the cleared cohort "
            "and validate the unknown-annotation no-mutation policy on real "
            "audio."),
    },
    {
        "id": "BLK-07",
        "artifact_id": "ART-08",
        "linked_gates": ["RG-07"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No paced playback or target-device measurement exists: no "
            "buffering, rebuffer, drift, underrun, deadline, CPU, memory, "
            "energy or thermal result."),
        "required_action": (
            "Measure paced playback on the intended device with explicit "
            "buffers, fill/flush, rebuffer/drift schedules, deadlines and "
            "resource/energy data."),
    },
    {
        "id": "BLK-08",
        "artifact_id": "ART-09",
        "linked_gates": ["RG-08"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider/pipeline intake, descriptor, registry, default, "
            "shared build, CI or release decision exists. Nothing is "
            "registered, enabled or reviewed for release."),
        "required_action": (
            "Open a separate versioned OFF-by-default intake with exact "
            "descriptor/config, no shared-surface change, clean-install proof "
            "and independent exact-head review after the prior gates clear."),
    },
)

RATE_PROFILE_ROWS = (
    ("RATE-01", "Measure source/output mapping and duration.",
     "No admitted Bungee runtime or real pipeline result exists."),
    ("RATE-02", "Measure pitch and transient audibility.",
     "No rendered rate output, pitch metric or listening result exists."),
    ("RATE-03", "Verify no unintended gaps and finite flush.",
     "The synthetic bypass has no gaps, but no rate path or real flush was "
     "measured."),
    ("RATE-04", "Verify 1x bit-exact passthrough.",
     "Only a synthetic fixed-point bypass control exists; no installed "
     "float32 SDK or real-audio 1x result exists."),
    ("RATE-05", "Include rate changes and step/ramp schedules.",
     "The Bungee stage is not admitted, so every non-1x request is an "
     "explicit bypass and no rate step executes."),
    ("RATE-06", "Measure output delay by independently tagged impulses.",
     "The bypass reports zero synthetic delay only; no tagged-impulse rate-"
     "path delay exists."),
    ("RATE-07", "Score natural speech, music and transitions separately.",
     "Synthetic proxies are not natural audio; no rights-cleared cohort or "
     "separate scoring exists."),
    ("RATE-08", "Keep unknown annotation free of audio mutation.",
     "The no-mutation rule is modelled on synthetic fixtures and is not "
     "validated on real audio."),
)

QUALITY_ROWS = (
    ("QUAL-01", "1x bit-exact passthrough",
     "Synthetic integer bypass only; not a real pipeline result."),
    ("QUAL-02", "Duration and pitch on fixed-rate Bungee",
     "No Bungee invocation or rate output exists."),
    ("QUAL-03", "Naturalness, transitions and listening",
     "No permitted listening or real-audio scoring exists."),
    ("QUAL-04", "Adverse, missing and nonfinite controls on the real pipeline",
     "Only synthetic admission controls exist; no real pipeline control run "
     "exists."),
)

TIMING_ROWS = (
    ("TIME-01", "stage_latency_p95_p99",
     "No Bungee or limiter stage timing was measured."),
    ("TIME-02", "end_to_end_output_delay",
     "Only a synthetic bypass zero-delay control exists; no real impulse-"
     "tagged end-to-end delay exists."),
    ("TIME-03", "buffering_rebuffer_drift_underruns",
     "No paced playback or queue/device observation exists."),
    ("TIME-04", "device_deadline_cpu_memory_energy",
     "No target device or resource measurement exists."),
)


def _blocked_rows(rows: tuple[tuple[str, str, str], ...],
                  prefix: str) -> list[dict]:
    return [
        {"id": identifier, "requirement": requirement, "status": "blocked",
         "value": None, "evidence": evidence}
        for identifier, requirement, evidence in rows
    ]


def build_contract() -> dict:
    linked = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "boundary": {
            "recipe": (
                "timestamped PCM -> optional advisory speech/rate annotation "
                "-> explicit fixed-rate Bungee Basic -> peak limiter"),
            "stages": ["timestamped_pcm", "optional_advisory_annotation",
                       "fixed_rate_bungee_basic", "peak_limiter", "output"],
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "sdk_callback_invoked": False,
            "bungee_stage": {
                "admitted": False,
                "invoked": False,
                "requested_only": True,
                "reason": "admitted_runtime_artifact_absent",
                "source_revision": BUNGEE_SOURCE_REVISION,
                "license": BUNGEE_LICENSE,
            },
            "limiter_stage": {
                "qualified": False,
                "mode": "transparent_reference_only",
                "changed": False,
            },
            "fallback_policy": (
                "1x_bypass_when_required_capability_or_buffer_unavailable"),
            "unknown_annotation_policy": "leave_audio_unedited",
            "write_scope": WRITE_SCOPE,
        },
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "scope": dict(SCOPE),
        "qualification": dict(QUALIFICATION),
        "release_gates": _release_gates(linked),
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "required_results": list(REQUIRED_RESULTS),
        "rate_profile_requirements": _blocked_rows(RATE_PROFILE_ROWS,
                                                    "RATE"),
        "quality_outcomes": _blocked_rows(QUALITY_ROWS, "QUAL"),
        "timing_requirements": _blocked_rows(TIMING_ROWS, "TIME"),
        "corpus": {
            "rights_cleared": False,
            "natural_speech": False,
            "music": False,
            "transitions": False,
            "silence": False,
            "tagged_impulses": False,
            "audio_read": False,
            "status": "absent",
            "requirement": (
                "A rights-cleared natural speech, music, transition and "
                "silence cohort with tagged impulses, source timestamps, "
                "digests, terms and output-use decision."),
        },
        "listening": {
            "performed": False,
            "panel": None,
            "cohort": None,
            "permissions": None,
            "status": "blocked",
            "qualifies": False,
        },
        "source_presence": source_presence(),
        "historical_context": historical_context(),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    contract = build_contract()
    linked = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    cases = control_cases()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": contract["disposition"],
        "contract_sha256": object_digest(contract),
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "scope": contract["scope"],
        "qualification": contract["qualification"],
        "release_gates": contract["release_gates"],
        "exact_blockers": contract["exact_blockers"],
        "required_artifacts": contract["required_artifacts"],
        "required_results": contract["required_results"],
        "rate_profile": {
            "rows": contract["rate_profile_requirements"],
            "blocked_rows": len(contract["rate_profile_requirements"]),
        },
        "quality_outcomes": {
            "rows": contract["quality_outcomes"],
            "blocked_rows": len(contract["quality_outcomes"]),
        },
        "timing": {
            "rows": contract["timing_requirements"],
            "blocked_rows": len(contract["timing_requirements"]),
        },
        "corpus": contract["corpus"],
        "listening": contract["listening"],
        "source_presence": contract["source_presence"],
        "historical_context": contract["historical_context"],
        "controls": {
            "cases": cases,
            "summary": control_summary(cases),
        },
        "linked_row_identity": {
            "projection": linked,
            "sha256": board_row_digest(linked),
            "linked_rows": rows,
            "linked_rows_sha256": linked_rows_digest(rows),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": contract["non_claims"],
        "reproduction": {
            "regeneration": "run.py --output <dir> (repeat=3, byte-identical)",
            "tests": "python3 -m unittest -v test_reference.py",
            "verifier": "python3 verify.py",
            "stdlib_only": True,
            "network_used": False,
            "cold_starts": 3,
        },
    }


def canonical_report(document: dict) -> tuple[str, str]:
    _no_floats(document)
    text = canonical_text(document)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    gates = contract.get("release_gates", [])
    if len(gates) != 8:
        raise ValueError("contract_gate_count")
    linked = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("contract_gate_reopen")
        if gate.get("linked_row") != linked:
            raise ValueError("contract_gate_linked_row")
    artifacts = contract.get("required_artifacts", [])
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if artifacts[0].get("present") is not True \
            or artifacts[0].get("verified") is not True \
            or artifacts[0].get("blocked") is not False:
        raise ValueError("contract_artifact_source")
    for row in artifacts[1:]:
        if row.get("present") is not False or row.get("blocked") is not True \
                or row.get("verified") is not False:
            raise ValueError("contract_artifact_not_blocked")
    blockers = contract.get("exact_blockers", [])
    if len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    gate_ids = {row.get("id") for row in gates}
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
        if row.get("artifact_id") not in artifact_ids:
            raise ValueError("contract_blocker_artifact")
        for gate in row.get("linked_gates", []):
            if gate not in gate_ids:
                raise ValueError("contract_blocker_gate")
    for section, expected in (
            ("rate_profile_requirements", RATE_PROFILE_ROWS),
            ("quality_outcomes", QUALITY_ROWS),
            ("timing_requirements", TIMING_ROWS)):
        rows = contract.get(section, [])
        if len(rows) != len(expected):
            raise ValueError("contract_section_count:" + section)
        for row in rows:
            if row.get("status") != "blocked" or row.get("value") is not None:
                raise ValueError("contract_section_not_blocked:" + section)
    qualification = contract.get("qualification", {})
    for key in ("not_qualified", "all_release_gates_blocked"):
        if qualification.get(key) is not True:
            raise ValueError("contract_qualification_flag:" + key)
    for key in ("real_result_present", "pipeline_result_present",
                "admitted_runtime_present", "rights_cleared_assets_present",
                "qualified_annotation_present",
                "qualified_limiter_integration_present", "listening_result",
                "device_timing_result", "benchmark_result", "release_claim",
                "missing_result_promoted"):
        if qualification.get(key) is not False:
            raise ValueError("contract_qualification_false:" + key)
    if qualification.get("bungee_source_present") is not True \
            or qualification.get("bungee_build_present") is not True:
        raise ValueError("contract_bungee_presence")
    _no_floats(contract)
