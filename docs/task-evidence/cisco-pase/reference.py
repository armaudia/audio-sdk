# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local asset-admission and frame-conservation surrogate for Cisco PASE.

This module is a *bounded boundary surrogate* for ``SDK-CISCO-PASE``.  It
validates the exact external-asset manifest shape required by ``CONTRACTS.md``
``as_asset_v0``, validates a declared 16 kHz adapter geometry, computes the
exact half-open source intervals for process and drain calls, and exercises a
deterministic dual-rate recombination control.

It is **not** Cisco PASE, not the catalogue candidate and not an enhancement
model.  It contains no licensed source, checkpoint, weight, WavLM component,
vocoder, runtime, corpus, device or listening result.  It can never qualify
the component.

Exact arithmetic
----------------

* One 16 kHz sample is exactly ``62_500 ns`` (``CONTRACTS.md`` timing record).
* Accepted frames are 160 samples; a final partial frame is zero-padded and
  only the declared valid prefix is content.
* Content positions are half-open integer sample intervals; conservation is
  interval-union equality, not merely matching totals.
* A content delay ``D`` shifts output coordinates by ``-D`` and is bounded to
  ``0 <= D <= 16_000`` by the installed v0 contract.
* The anchor hop and window are integer sample counts.  A hop that is not a
  whole number of 160-sample frames is rejected; it is never interpolated.
* Recombination uses only dyadic rational values, so the identity control is
  bit-exact and the synthetic control digest is stable.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]

TASK_ID = "SDK-CISCO-PASE"
TITLE = "Cisco PASE"
COMPONENT = "cisco-pase"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-CISCO-PASE"
BASE_COMMIT = "d45e0f22883021412b4206c77df4e1d8cf89dbd5"
TASK_PREFIX = "docs/task-evidence/cisco-pase/"
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SAMPLE_RATE_HZ = 16000
SAMPLE_PERIOD_NS = 62_500
FRAME_SAMPLES = 160
MAX_DELAY_SAMPLES = 16000
MAX_DRAIN_CALLS = 1024
MAX_ACCEPTED_SAMPLES = 1_000_000
MAX_ASSETS = 16
MAX_TOTAL_ASSET_BYTES = 512 * 1024 * 1024
MAX_ABS_SAMPLE = 1_000_000.0
Q16 = 65_536
DEFAULT_ANCHOR_HOP = 320
DEFAULT_ANCHOR_WINDOW = 400

ADAPTER_SCHEMA = "audio-sdk/pase-adapter-proposal/0.1"
MANIFEST_SCHEMA = "audio-sdk/external-asset-manifest/0.1"
REPORT_SCHEMA = "audio-sdk/cisco-pase-report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"

ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")

MANIFEST_FIELDS = {"schema_id", "assets"}
ASSET_FIELDS = {"id", "sha256", "byte_count", "storage"}
ADAPTER_FIELDS = {
    "schema_id",
    "adapter_id",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "anchor_hop_samples",
    "anchor_window_samples",
    "buffering_delay_samples",
    "max_drain_calls",
    "edge_exclusion_start_samples",
    "edge_exclusion_end_samples",
    "execution_modes",
}

#: Stable read-only source pins, relative to the workspace root.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/pilot_evaluation_progress.md":
        "7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf",
    "research/store/snapshots/"
    "57333e8a641fe3f906090d90a00f9c72669751f0ffe5fc559b244a4afe698542.jsonl":
        "57333e8a641fe3f906090d90a00f9c72669751f0ffe5fc559b244a4afe698542",
    "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/"
    "candidate_accounting.csv":
        "7261b99e06460b612dcbebeec3859de60a7040a18444fc19a637ebddc4a58e3c",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
}

#: Stable read-only SDK boundary pins, relative to the SDK worktree root.
BOUNDARY_PINS: Dict[str, str] = {
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/README.md":
        "514636b719e6579651bf941a6ac3cb93740cc9a40e3f2b4bcd39c2ddea610264",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/contract.json":
        "c7b0f4ac8191abe114b4f77ae17c803ffbda1fe4012e12d42808ca798d0afb88",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/report.json":
        "5d3623c835a1b19d79867a64ba1b6dff18e8593918a8173cff91550c1c532f03",
    "docs/task-evidence/dpdfnet-2-streaming/README.md":
        "eafc42885faef188a2b2d3be56df2aa62451c4a9995fe75e72b8b155e56f1acc",
    "docs/task-evidence/pipe-capture/README.md":
        "cbaa97236a3eeca4d3065a421fcc41100e4c6bea1692fd698aada6c8b68376a3",
    "docs/task-evidence/duplex-clocks/README.md":
        "8e1a355bd36e561e8f1b634a5f5ec351e15d1785be8b6f4713bef33ec97e0325",
}

#: Task-local artifacts pinned by contract.json (self-references excluded).
ARTIFACT_FILES: Tuple[str, ...] = (
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

SOURCE_FILES: Tuple[str, ...] = tuple(SOURCE_PINS)
BOUNDARY_FILES: Tuple[str, ...] = tuple(BOUNDARY_PINS)
PIN_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json",
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


class Reject(ValueError):
    """A bounded, deterministic input rejection."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def _strict_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise Reject("duplicate_json_key:" + key)
        result[key] = value
    return result


def _strict_constant(token: str) -> None:
    raise Reject("nonfinite_json_constant:" + token)


def parse_strict_json(text: str) -> Any:
    """Parse strict JSON, rejecting duplicate keys and non-finite constants."""
    try:
        return json.loads(text, object_pairs_hook=_strict_pairs,
                          parse_constant=_strict_constant)
    except Reject:
        raise
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        raise Reject("invalid_json") from error


def load_strict_json(path: Path) -> Any:
    return parse_strict_json(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def tensor_digest(values: Sequence[float]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack("<d", float(value)))
    return digest.hexdigest()


def _as_int(value: Any, code: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(code)
    if value < low or value > high:
        raise Reject(code)
    return value


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_id(value: Any, code: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise Reject(code)
    return value


def _as_sha256(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
        raise Reject(code)
    return value


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate one external-asset manifest against contract 0.1 rules.

    The descriptor order is preserved, duplicate IDs are rejected, storage must
    be ``external`` and the caller-supplied totals are bounded.  No path, URL
    or embedded-asset form is admitted.
    """
    _require(isinstance(manifest, dict), "manifest_not_object")
    _require(set(manifest) == MANIFEST_FIELDS, "invalid_manifest_fields")
    _require(manifest["schema_id"] == MANIFEST_SCHEMA, "unsupported_manifest_schema")
    assets = manifest["assets"]
    _require(isinstance(assets, list), "assets_not_array")
    _require(1 <= len(assets) <= MAX_ASSETS, "invalid_asset_count")

    normalized: List[Dict[str, Any]] = []
    seen: List[str] = []
    total = 0
    for entry in assets:
        _require(isinstance(entry, dict) and set(entry) == ASSET_FIELDS,
                 "invalid_asset_fields")
        asset_id = _as_id(entry["id"], "invalid_asset_id")
        _require(asset_id not in seen, "duplicate_asset_id")
        seen.append(asset_id)
        digest = _as_sha256(entry["sha256"], "invalid_sha256")
        byte_count = _as_int(entry["byte_count"], "invalid_byte_count",
                             1, MAX_TOTAL_ASSET_BYTES)
        _require(entry["storage"] == "external", "unsupported_asset_storage")
        total += byte_count
        normalized.append({
            "id": asset_id,
            "sha256": digest,
            "byte_count": byte_count,
            "storage": "external",
        })
    _require(total <= MAX_TOTAL_ASSET_BYTES, "asset_total_exceeds_limit")
    return {
        "asset_count": len(normalized),
        "asset_ids_in_order": list(seen),
        "total_bytes": total,
        "assets": normalized,
        "manifest_digest": object_digest(normalized),
    }


def validate_adapter(adapter: Any) -> Dict[str, Any]:
    """Validate the declined 16 kHz adapter geometry proposal."""
    _require(isinstance(adapter, dict), "adapter_not_object")
    _require(set(adapter) == ADAPTER_FIELDS, "invalid_adapter_fields")
    _require(adapter["schema_id"] == ADAPTER_SCHEMA, "unsupported_adapter_schema")
    adapter_id = _as_id(adapter["adapter_id"], "invalid_adapter_id")
    _require(_is_plain_int(adapter["sample_rate_hz"])
             and adapter["sample_rate_hz"] == SAMPLE_RATE_HZ,
             "unsupported_sample_rate")
    _require(_is_plain_int(adapter["channels"]) and adapter["channels"] == 1,
             "unsupported_channels")
    _require(_is_plain_int(adapter["frame_samples"])
             and adapter["frame_samples"] == FRAME_SAMPLES,
             "unsupported_frame_samples")
    hop = _as_int(adapter["anchor_hop_samples"], "anchor_hop_out_of_range",
                  FRAME_SAMPLES, SAMPLE_RATE_HZ)
    _require(hop % FRAME_SAMPLES == 0, "anchor_hop_not_frame_multiple")
    window = _as_int(adapter["anchor_window_samples"],
                     "anchor_window_out_of_range", 1, 4 * hop)
    delay = _as_int(adapter["buffering_delay_samples"],
                    "delay_out_of_range", 0, MAX_DELAY_SAMPLES)
    max_drain = _as_int(adapter["max_drain_calls"], "max_drain_out_of_range",
                        1, MAX_DRAIN_CALLS)
    start_excl = _as_int(adapter["edge_exclusion_start_samples"],
                         "edge_exclusion_out_of_range", 0, FRAME_SAMPLES)
    end_excl = _as_int(adapter["edge_exclusion_end_samples"],
                       "edge_exclusion_out_of_range", 0, FRAME_SAMPLES)
    _require(start_excl + end_excl <= FRAME_SAMPLES,
             "edge_exclusion_out_of_range")

    modes = adapter["execution_modes"]
    _require(isinstance(modes, list), "invalid_execution_modes")
    _require(len(modes) == 1 and modes[0] == 2, "unsupported_execution_modes")

    return {
        "adapter_id": adapter_id,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "anchor_hop_samples": hop,
        "anchor_blocks_per_frame": hop // FRAME_SAMPLES,
        "anchor_window_samples": window,
        "buffering_delay_samples": delay,
        "max_drain_calls": max_drain,
        "edge_exclusion_start_samples": start_excl,
        "edge_exclusion_end_samples": end_excl,
        "execution_modes": [2],
    }


def _content_bounds(accepted: int, adapter: Dict[str, Any]) -> Tuple[int, int]:
    start = adapter["edge_exclusion_start_samples"]
    end = accepted - adapter["edge_exclusion_end_samples"]
    if end < start:
        end = start
    return start, end


def frame_plan(accepted: Any, adapter: Any) -> Dict[str, Any]:
    """Compute exact process/drain intervals for accepted content.

    Output sample ``source_first_sample`` maps ``output[0]`` into source
    coordinates.  Valid samples are the intersection of the 160-sample output
    interval with content ``[start, end)``; padding is never valid.
    """
    config = validate_adapter(adapter)
    accepted = _as_int(accepted, "invalid_accepted_samples",
                       0, MAX_ACCEPTED_SAMPLES)
    delay = config["buffering_delay_samples"]
    content_start, content_end = _content_bounds(accepted, config)
    process_calls = (accepted + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    submitted = process_calls * FRAME_SAMPLES
    zero_padding = submitted - accepted
    drain_start = submitted - delay if process_calls else 0

    calls: List[Dict[str, Any]] = []
    valid_intervals: List[List[int]] = []
    valid_from_process = 0
    for index in range(process_calls):
        source_first = index * FRAME_SAMPLES - delay
        out_end = source_first + FRAME_SAMPLES
        valid_start = max(source_first, content_start)
        valid_stop = min(out_end, content_end)
        count = max(0, valid_stop - valid_start)
        if count:
            valid_intervals.append([valid_start, valid_stop])
            valid_from_process += count
        calls.append({
            "kind": "process",
            "index": index,
            "source_first_sample": source_first,
            "valid_offset": (valid_start - source_first) if count else 0,
            "valid_count": count,
            "consumed_count": FRAME_SAMPLES,
            "produced_count": FRAME_SAMPLES,
        })

    remaining = content_end - drain_start if content_end > drain_start else 0
    drain_audio_calls = 0
    if remaining:
        drain_audio_calls = (remaining + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    _require(drain_audio_calls <= config["max_drain_calls"],
             "drain_budget_exceeded")
    valid_from_drain = 0
    for index in range(drain_audio_calls):
        source_first = drain_start + index * FRAME_SAMPLES
        out_end = source_first + FRAME_SAMPLES
        valid_start = max(source_first, content_start)
        valid_stop = min(out_end, content_end)
        count = max(0, valid_stop - valid_start)
        if count:
            valid_intervals.append([valid_start, valid_stop])
            valid_from_drain += count
        calls.append({
            "kind": "drain",
            "index": index,
            "source_first_sample": source_first,
            "valid_offset": (valid_start - source_first) if count else 0,
            "valid_count": count,
            "consumed_count": 0,
            "produced_count": FRAME_SAMPLES,
        })

    valid_intervals.sort()
    overlap_free = all(valid_intervals[index][1] <= valid_intervals[index + 1][0]
                       for index in range(len(valid_intervals) - 1))
    merged: List[List[int]] = []
    for start, stop in valid_intervals:
        if merged and start == merged[-1][1]:
            merged[-1][1] = stop
        else:
            merged.append([start, stop])
    expected = [[content_start, content_end]] if content_end > content_start else []
    union_equals_content = merged == expected
    total_valid = sum(stop - start for start, stop in valid_intervals)
    _require(overlap_free, "valid_intervals_overlap")
    _require(union_equals_content, "valid_intervals_do_not_cover_content")
    _require(total_valid == content_end - content_start,
             "valid_sample_total_mismatch")
    _require(not any(call["kind"] == "process"
                     and not 0 <= call["valid_offset"] <= FRAME_SAMPLES
                     for call in calls), "invalid_valid_offset")

    return {
        "accepted_samples": accepted,
        "buffering_delay_samples": delay,
        "content_interval": [content_start, content_end],
        "process_calls": process_calls,
        "drain_audio_calls": drain_audio_calls,
        "max_drain_calls": config["max_drain_calls"],
        "output_calls": len(calls),
        "eos_after_last_output": True,
        "submitted_padded_samples": submitted,
        "zero_padding_samples": zero_padding,
        "valid_from_process": valid_from_process,
        "valid_from_drain": valid_from_drain,
        "valid_samples": total_valid,
        "dead_startup_samples": submitted - zero_padding - valid_from_process,
        "valid_intervals": valid_intervals,
        "intervals_digest": object_digest(valid_intervals),
        "overlap_free": overlap_free,
        "union_equals_content": union_equals_content,
        "drain_within_budget": drain_audio_calls <= config["max_drain_calls"],
        "first_valid_source_sample": (valid_intervals[0][0]
                                      if valid_intervals else None),
        "last_valid_source_end": (valid_intervals[-1][1]
                                  if valid_intervals else None),
    }


def validate_frame(input_count: Any, input_valid_count: Any, flags: Any,
                   samples: Any, output_capacity: Any) -> Dict[str, Any]:
    """Validate one v0 process frame and its caller output buffer."""
    _require(_is_plain_int(input_count) and input_count == FRAME_SAMPLES,
             "input_count_not_160")
    valid = _as_int(input_valid_count, "invalid_valid_count", 1, FRAME_SAMPLES)
    _require(_is_plain_int(flags), "invalid_flags")
    final = flags & 1
    _require(flags & ~1 == 0, "unknown_flag_bits")
    _require(valid == FRAME_SAMPLES or final == 1, "partial_without_final")
    _require(_is_plain_int(output_capacity)
             and output_capacity >= FRAME_SAMPLES, "output_capacity_too_small")
    _require(isinstance(samples, list), "samples_not_array")
    _require(len(samples) == input_count, "sample_count_mismatch")
    parsed: List[float] = []
    for value in samples:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Reject("invalid_sample_type")
        try:
            finite = float(value)
        except (OverflowError, ValueError) as error:
            raise Reject("nonfinite_sample") from error
        if not math.isfinite(finite):
            raise Reject("nonfinite_sample")
        if abs(finite) > MAX_ABS_SAMPLE:
            raise Reject("sample_out_of_range")
        parsed.append(finite)
    for index in range(valid, FRAME_SAMPLES):
        _require(parsed[index] == 0.0, "final_padding_not_zero")
    return {
        "input_count": input_count,
        "input_valid_count": valid,
        "final_input": bool(final),
        "zero_padding_samples": FRAME_SAMPLES - valid,
        "output_capacity": output_capacity,
        "samples_digest": tensor_digest(parsed),
    }


def _dyadic(values: Any, code: str) -> List[float]:
    _require(isinstance(values, list), code)
    _require(1 <= len(values) <= MAX_ACCEPTED_SAMPLES, "invalid_stream_length")
    output: List[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Reject(code)
        try:
            finite = float(value)
        except (OverflowError, ValueError) as error:
            raise Reject(code) from error
        if not math.isfinite(finite):
            raise Reject(code)
        if abs(finite) > MAX_ABS_SAMPLE:
            raise Reject("sample_out_of_range")
        output.append(finite)
    return output


def hold_blocks(values: Any, hop: Any) -> List[float]:
    """Zero-order hold of each block's first sample; exact, causal, no model."""
    _require(_is_plain_int(hop) and hop >= FRAME_SAMPLES,
             "anchor_hop_out_of_range")
    samples = _dyadic(values, "invalid_sample_type")
    _require(hop % FRAME_SAMPLES == 0, "anchor_hop_not_frame_multiple")
    _require(len(samples) % hop == 0, "stream_not_block_aligned")
    output: List[float] = []
    for start in range(0, len(samples), hop):
        output.extend([samples[start]] * hop)
    return output


def recombine(anchor_blocks: Any, residual: Any, hop: Any) -> Dict[str, Any]:
    """Hold a block-rate anchor stream and add a full-rate residual stream."""
    _require(_is_plain_int(hop) and hop >= FRAME_SAMPLES,
             "anchor_hop_out_of_range")
    _require(hop % FRAME_SAMPLES == 0, "anchor_hop_not_frame_multiple")
    blocks = _dyadic(anchor_blocks, "nonfinite_anchor")
    residual_values = _dyadic(residual, "nonfinite_residual")
    expected = len(residual_values)
    _require(expected % hop == 0, "residual_not_block_aligned")
    _require(len(blocks) == expected // hop, "anchor_block_count_mismatch")

    held: List[float] = []
    for value in blocks:
        held.extend([value] * hop)
    output = [held[index] + residual_values[index] for index in range(expected)]
    for value in output:
        _require(math.isfinite(value) and abs(value) <= MAX_ABS_SAMPLE,
                 "nonfinite_output")
    frame_count = expected // FRAME_SAMPLES
    frames = [output[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
              for index in range(frame_count)]
    return {
        "sample_count": expected,
        "frame_count": frame_count,
        "hop_samples": hop,
        "anchor_blocks_per_frame": hop // FRAME_SAMPLES,
        "anchor_block_count": len(blocks),
        "output": output,
        "output_digest": tensor_digest(output),
        "frame_digests": [tensor_digest(frame) for frame in frames],
        "block_boundaries_on_frame_edges": hop % FRAME_SAMPLES == 0,
        "max_abs_output": max(abs(value) for value in output),
    }


def _si_sdr(estimate: Sequence[float], target: Sequence[float]) -> float:
    _require(len(estimate) == len(target) and len(target) > 0, "metric_length")
    dot = math.fsum(e * t for e, t in zip(estimate, target))
    energy = math.fsum(t * t for t in target)
    _require(energy > 0.0, "undefined_metric")
    scale = dot / energy
    projection = math.fsum((estimate[index] - scale * target[index]) ** 2
                           for index in range(len(target)))
    wanted = math.fsum((scale * target[index]) ** 2
                       for index in range(len(target)))
    _require(wanted > 0.0 and projection > 0.0, "undefined_metric")
    return 10.0 * math.log10(wanted / projection)


def _snr(estimate: Sequence[float], target: Sequence[float]) -> float:
    _require(len(estimate) == len(target), "metric_length")
    error = math.fsum((estimate[index] - target[index]) ** 2
                      for index in range(len(target)))
    wanted = math.fsum(target[index] ** 2 for index in range(len(target)))
    _require(error > 0.0 and wanted > 0.0, "undefined_metric")
    return 10.0 * math.log10(wanted / error)


def _correlation(first: Sequence[float], second: Sequence[float]) -> float:
    dot = math.fsum(a * b for a, b in zip(first, second))
    norm = math.sqrt(math.fsum(a * a for a in first)
                     * math.fsum(b * b for b in second))
    _require(norm > 0.0, "undefined_metric")
    return dot / norm


def target_sequence(length: int) -> List[float]:
    """Deterministic dyadic synthetic target; multiples of 1/64."""
    _require(_is_plain_int(length) and 1 <= length <= MAX_ACCEPTED_SAMPLES,
             "invalid_stream_length")
    return [((index * 37) % 101 - 50) / 64.0 for index in range(length)]


def preservation_control(hop: int = DEFAULT_ANCHOR_HOP,
                         length: int = 3200) -> Dict[str, Any]:
    """Clean-speech preservation *damage* control for the hold operation.

    The hold is applied to the clean target itself.  A trivial block hold is not
    an enhancement model; the reported degradation is a negative control and
    never a candidate result.
    """
    target = target_sequence(length)
    held = hold_blocks(target, hop)
    si_sdr = _si_sdr(held, target)
    snr = _snr(held, target)
    max_error = max(abs(a - b) for a, b in zip(held, target))
    _require(si_sdr < 0.0, "hold_control_unexpectedly_preserves_signal")
    return {
        "control_id": "block_hold_clean_preservation_control",
        "status": "surrogate_only_not_qualified",
        "hop_samples": hop,
        "sample_count": length,
        "si_sdr_db": round(si_sdr, 6),
        "snr_db": round(snr, 6),
        "max_abs_error": round(max_error, 6),
        "peak_output": round(max(abs(value) for value in held), 6),
        "correlation": round(_correlation(held, target), 6),
        "bit_identical": held == target,
        "clean_speech_preserved": False,
        "nonfinite_outputs": 0,
        "note": "A zero-order block hold damages clean speech. This negative control is not PASE and cannot qualify any result.",
        "output_digest": tensor_digest(held),
    }


def identity_control() -> Dict[str, Any]:
    """Bit-exact passthrough control: zero anchor, identity residual."""
    length = 480
    residual = target_sequence(length)
    result = recombine([0.0] * (length // FRAME_SAMPLES), residual,
                       FRAME_SAMPLES)
    _require(result["output"] == residual, "identity_control_not_bit_identical")
    _require(result["output_digest"] == tensor_digest(residual),
             "identity_digest_mismatch")
    return {
        "control_id": "zero_anchor_identity_control",
        "sample_count": length,
        "hop_samples": FRAME_SAMPLES,
        "bit_identical": True,
        "input_digest": tensor_digest(residual),
        "output_digest": result["output_digest"],
        "nonfinite_outputs": 0,
    }


def dual_stream_case() -> Dict[str, Any]:
    """Exact anchor-hold recombination with a zero residual."""
    hop = DEFAULT_ANCHOR_HOP
    anchor = [-0.5, 0.25, 0.125, -0.75, 0.0625, -0.03125, 0.375, -0.125]
    residual = [0.0] * (len(anchor) * hop)
    result = recombine(anchor, residual, hop)
    expected = []
    for value in anchor:
        expected.extend([value] * hop)
    _require(result["output"] == expected, "anchor_hold_not_exact")
    _require(result["block_boundaries_on_frame_edges"],
             "anchor_hop_not_frame_aligned")
    _require(result["hop_samples"] // FRAME_SAMPLES == 2,
             "unexpected_anchor_blocks_per_frame")
    return {
        "case_id": "exact_anchor_hold_320",
        "hop_samples": hop,
        "anchor_blocks_per_frame": 2,
        "sample_count": result["sample_count"],
        "anchor_values": anchor,
        "anchor_block_count": result["anchor_block_count"],
        "frame_count": result["frame_count"],
        "output_digest": result["output_digest"],
        "frame_digests": result["frame_digests"],
        "max_abs_output": result["max_abs_output"],
        "exact": True,
        "status": "synthetic_only_not_qualified",
    }


def _case_adapter(delay: int = 160, start: int = 0, end: int = 0,
                  max_drain: int = 1024) -> Dict[str, Any]:
    return {
        "schema_id": ADAPTER_SCHEMA,
        "adapter_id": "pase-proposal-adapter",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "anchor_hop_samples": DEFAULT_ANCHOR_HOP,
        "anchor_window_samples": DEFAULT_ANCHOR_WINDOW,
        "buffering_delay_samples": delay,
        "max_drain_calls": max_drain,
        "edge_exclusion_start_samples": start,
        "edge_exclusion_end_samples": end,
        "execution_modes": [2],
    }


def conservation_cases() -> List[Dict[str, Any]]:
    """Frozen accepted-length / delay cases, including contract examples."""
    return [
        {"case_id": "zero_input", "accepted": 0, "delay": 160},
        {"case_id": "single_sample", "accepted": 1, "delay": 160},
        {"case_id": "partial_final_159", "accepted": 159, "delay": 160},
        {"case_id": "exact_frame_160", "accepted": 160, "delay": 160},
        {"case_id": "one_frame_plus_one_161", "accepted": 161, "delay": 160},
        {"case_id": "two_frames_320", "accepted": 320, "delay": 160},
        {"case_id": "two_frames_plus_one_321", "accepted": 321, "delay": 160},
        {"case_id": "odd_length_1000", "accepted": 1000, "delay": 160},
        {"case_id": "delay_not_multiple_160", "accepted": 250, "delay": 100},
        {"case_id": "max_declared_delay", "accepted": 400, "delay": 16000},
        {"case_id": "edge_exclusions_16", "accepted": 320, "delay": 160,
         "start": 8, "end": 8},
    ]


def evaluate_conservation(case: Dict[str, Any]) -> Dict[str, Any]:
    adapter = _case_adapter(case.get("delay", 160), case.get("start", 0),
                            case.get("end", 0))
    plan = frame_plan(case["accepted"], adapter)
    return {
        "case_id": case["case_id"],
        "accepted_samples": plan["accepted_samples"],
        "buffering_delay_samples": plan["buffering_delay_samples"],
        "content_interval": plan["content_interval"],
        "process_calls": plan["process_calls"],
        "drain_audio_calls": plan["drain_audio_calls"],
        "output_calls": plan["output_calls"],
        "zero_padding_samples": plan["zero_padding_samples"],
        "valid_from_process": plan["valid_from_process"],
        "valid_from_drain": plan["valid_from_drain"],
        "valid_samples": plan["valid_samples"],
        "dead_startup_samples": plan["dead_startup_samples"],
        "first_valid_source_sample": plan["first_valid_source_sample"],
        "last_valid_source_end": plan["last_valid_source_end"],
        "intervals_digest": plan["intervals_digest"],
        "overlap_free": plan["overlap_free"],
        "union_equals_content": plan["union_equals_content"],
        "drain_within_budget": plan["drain_within_budget"],
    }


def coverage_sweep() -> Dict[str, Any]:
    """Deterministic conservation sweep over lengths, delays and exclusions."""
    lengths = list(range(0, 401)) + [999, 1000, 1001, 3999, 4000, 4001]
    delays = [0, 1, 99, 100, 159, 160, 161, 320, 1000, 16000]
    checks = 0
    for delay in delays:
        for length in lengths:
            plan = frame_plan(length, _case_adapter(delay))
            _require(plan["union_equals_content"], "sweep_union_mismatch")
            _require(plan["overlap_free"], "sweep_overlap")
            _require(plan["valid_samples"]
                     == max(0, length), "sweep_valid_total")
            _require(plan["process_calls"] + plan["drain_audio_calls"] <= 1024,
                     "sweep_call_budget")
            checks += 1
    for start, end in ((1, 1), (8, 8), (80, 80), (0, 160), (160, 0)):
        for length in (0, 1, 159, 160, 161, 320, 1000):
            plan = frame_plan(length, _case_adapter(160, start, end))
            _require(plan["union_equals_content"], "sweep_edge_union_mismatch")
            _require(plan["valid_samples"] == max(0, length - start - end),
                     "sweep_edge_valid_total")
            checks += 1
    return {
        "checks": checks,
        "lengths": len(lengths),
        "delays": delays,
        "edge_exclusions": [[1, 1], [8, 8], [80, 80], [0, 160], [160, 0]],
        "all_conserved": True,
    }


def _reject_code(function: Any, *args: Any) -> str:
    try:
        function(*args)
    except Reject as error:
        return error.code
    raise AssertionError("adverse case was accepted")


def _manifest(**overrides: Any) -> Dict[str, Any]:
    base = {
        "schema_id": MANIFEST_SCHEMA,
        "assets": [{
            "id": "synthetic-weights",
            "sha256": "0" * 64,
            "byte_count": 1024,
            "storage": "external",
        }],
    }
    for key, value in overrides.items():
        if key == "assets":
            base["assets"] = value
        else:
            base[key] = value
    return base


def _asset(**overrides: Any) -> Dict[str, Any]:
    asset = {
        "id": "synthetic-weights",
        "sha256": "0" * 64,
        "byte_count": 1024,
        "storage": "external",
    }
    asset.update(overrides)
    return asset


def adverse_rejections() -> List[Dict[str, Any]]:
    """Every rejection must leave the frozen evaluation state unchanged."""
    duplicate_asset = _manifest(assets=[
        _asset(),
        _asset(id="synthetic-config", sha256="1" * 64),
        _asset(),
    ])
    uppercase_id = _manifest(assets=[_asset(id="Synthetic-Weights")])
    path_id = _manifest(assets=[_asset(id="weights/model")])
    short_sha = _manifest(assets=[_asset(sha256="0" * 63)])
    uppercase_sha = _manifest(assets=[_asset(sha256="A" * 64)])
    nonhex_sha = _manifest(assets=[_asset(sha256="g" * 64)])
    zero_bytes = _manifest(assets=[_asset(byte_count=0)])
    negative_bytes = _manifest(assets=[_asset(byte_count=-1)])
    bool_bytes = _manifest(assets=[_asset(byte_count=True)])
    embedded = _manifest(assets=[_asset(storage="embedded")])
    missing_sha = _manifest(assets=[{"id": "synthetic-weights",
                                     "byte_count": 1024,
                                     "storage": "external"}])
    extra_asset_field = _manifest(assets=[_asset(path="/tmp/weights.pt")])
    too_many = _manifest(assets=[
        _asset(id="asset-%02d" % index, sha256="%064x" % (index + 1))
        for index in range(MAX_ASSETS + 1)
    ])
    too_large = _manifest(assets=[
        _asset(id="asset-%02d" % index, sha256="%064x" % (index + 1),
               byte_count=MAX_TOTAL_ASSET_BYTES // MAX_ASSETS + 1)
        for index in range(MAX_ASSETS)
    ])

    bad_schema = _case_adapter()
    bad_schema["schema_id"] = "audio-sdk/pase-adapter-proposal/9.9"
    bad_id = _case_adapter()
    bad_id["adapter_id"] = "PASE Adapter"
    bad_rate = _case_adapter()
    bad_rate["sample_rate_hz"] = 48000
    bad_channels = _case_adapter()
    bad_channels["channels"] = 2
    bad_frame = _case_adapter()
    bad_frame["frame_samples"] = 320
    bad_hop = _case_adapter()
    bad_hop["anchor_hop_samples"] = 170
    hop_range = _case_adapter()
    hop_range["anchor_hop_samples"] = 80
    window_range = _case_adapter()
    window_range["anchor_window_samples"] = 0
    delay_low = _case_adapter()
    delay_low["buffering_delay_samples"] = -1
    delay_high = _case_adapter()
    delay_high["buffering_delay_samples"] = MAX_DELAY_SAMPLES + 1
    drain_zero = _case_adapter()
    drain_zero["max_drain_calls"] = 0
    drain_high = _case_adapter()
    drain_high["max_drain_calls"] = MAX_DRAIN_CALLS + 1
    extra_adapter = _case_adapter()
    extra_adapter["descriptor_bytes"] = "unexpected"
    modes = _case_adapter()
    modes["execution_modes"] = [1]
    modes_unknown = _case_adapter()
    modes_unknown["execution_modes"] = [4]

    good_frame = [0.0] * FRAME_SAMPLES
    partial_frame = [0.0] * FRAME_SAMPLES
    partial_frame[7] = 0.5
    nonzero_padding = [0.0] * FRAME_SAMPLES
    nonzero_padding[FRAME_SAMPLES - 1] = 0.25

    cases: List[Tuple[str, str, Any, Tuple[Any, ...]]] = [
        ("duplicate_asset_id", "duplicate_asset_id", validate_manifest,
         (duplicate_asset,)),
        ("invalid_asset_id", "invalid_asset_id", validate_manifest,
         (uppercase_id,)),
        ("asset_id_path", "invalid_asset_id", validate_manifest, (path_id,)),
        ("short_sha256", "invalid_sha256", validate_manifest, (short_sha,)),
        ("uppercase_sha256", "invalid_sha256", validate_manifest,
         (uppercase_sha,)),
        ("nonhex_sha256", "invalid_sha256", validate_manifest, (nonhex_sha,)),
        ("zero_byte_count", "invalid_byte_count", validate_manifest,
         (zero_bytes,)),
        ("negative_byte_count", "invalid_byte_count", validate_manifest,
         (negative_bytes,)),
        ("bool_byte_count", "invalid_byte_count", validate_manifest,
         (bool_bytes,)),
        ("embedded_storage", "unsupported_asset_storage", validate_manifest,
         (embedded,)),
        ("missing_sha256", "invalid_asset_fields", validate_manifest,
         (missing_sha,)),
        ("extra_asset_field", "invalid_asset_fields", validate_manifest,
         (extra_asset_field,)),
        ("too_many_assets", "invalid_asset_count", validate_manifest,
         (too_many,)),
        ("asset_total_exceeds_limit", "asset_total_exceeds_limit",
         validate_manifest, (too_large,)),
        ("unsupported_adapter_schema", "unsupported_adapter_schema",
         validate_adapter, (bad_schema,)),
        ("invalid_adapter_id", "invalid_adapter_id", validate_adapter,
         (bad_id,)),
        ("unsupported_sample_rate", "unsupported_sample_rate",
         validate_adapter, (bad_rate,)),
        ("unsupported_channels", "unsupported_channels", validate_adapter,
         (bad_channels,)),
        ("unsupported_frame_samples", "unsupported_frame_samples",
         validate_adapter, (bad_frame,)),
        ("anchor_hop_not_frame_multiple", "anchor_hop_not_frame_multiple",
         validate_adapter, (bad_hop,)),
        ("anchor_hop_out_of_range", "anchor_hop_out_of_range",
         validate_adapter, (hop_range,)),
        ("anchor_window_out_of_range", "anchor_window_out_of_range",
         validate_adapter, (window_range,)),
        ("delay_out_of_range_negative", "delay_out_of_range",
         validate_adapter, (delay_low,)),
        ("delay_out_of_range_high", "delay_out_of_range",
         validate_adapter, (delay_high,)),
        ("max_drain_out_of_range_zero", "max_drain_out_of_range",
         validate_adapter, (drain_zero,)),
        ("max_drain_out_of_range_high", "max_drain_out_of_range",
         validate_adapter, (drain_high,)),
        ("invalid_adapter_fields", "invalid_adapter_fields",
         validate_adapter, (extra_adapter,)),
        ("callback_mode_rejected", "unsupported_execution_modes",
         validate_adapter, (modes,)),
        ("unknown_execution_mode", "unsupported_execution_modes",
         validate_adapter, (modes_unknown,)),
        ("invalid_accepted_negative", "invalid_accepted_samples",
         lambda value: frame_plan(value, _case_adapter()), (-1,)),
        ("invalid_accepted_too_large", "invalid_accepted_samples",
         lambda value: frame_plan(value, _case_adapter()),
         (MAX_ACCEPTED_SAMPLES + 1,)),
        ("invalid_accepted_bool", "invalid_accepted_samples",
         lambda value: frame_plan(value, _case_adapter()), (True,)),
        ("drain_budget_exceeded", "drain_budget_exceeded",
         lambda: frame_plan(1000, _case_adapter(16000, max_drain=1)), ()),
        ("input_count_not_160", "input_count_not_160", validate_frame,
         (320, 320, 0, [0.0] * 320, 160)),
        ("valid_count_zero", "invalid_valid_count", validate_frame,
         (FRAME_SAMPLES, 0, 1, good_frame, 160)),
        ("valid_count_too_large", "invalid_valid_count", validate_frame,
         (FRAME_SAMPLES, FRAME_SAMPLES + 1, 0, good_frame, 160)),
        ("partial_without_final", "partial_without_final", validate_frame,
         (FRAME_SAMPLES, 8, 0, partial_frame, 160)),
        ("unknown_flag_bits", "unknown_flag_bits", validate_frame,
         (FRAME_SAMPLES, FRAME_SAMPLES, 4, good_frame, 160)),
        ("final_padding_not_zero", "final_padding_not_zero", validate_frame,
         (FRAME_SAMPLES, 8, 1, nonzero_padding, 160)),
        ("sample_count_mismatch", "sample_count_mismatch", validate_frame,
         (FRAME_SAMPLES, FRAME_SAMPLES, 0, good_frame[:-1], 160)),
        ("output_capacity_too_small", "output_capacity_too_small",
         validate_frame, (FRAME_SAMPLES, FRAME_SAMPLES, 0, good_frame, 159)),
        ("nonfinite_frame_sample", "nonfinite_sample", validate_frame,
         (FRAME_SAMPLES, FRAME_SAMPLES, 0,
          [math.inf] + good_frame[1:], 160)),
        ("invalid_frame_sample_type", "invalid_sample_type", validate_frame,
         (FRAME_SAMPLES, FRAME_SAMPLES, 0,
          ["0.0"] + good_frame[1:], 160)),
        ("frame_sample_out_of_range", "sample_out_of_range", validate_frame,
         (FRAME_SAMPLES, FRAME_SAMPLES, 0,
          [MAX_ABS_SAMPLE + 1.0] + good_frame[1:], 160)),
        ("residual_not_block_aligned", "residual_not_block_aligned", recombine,
         ([-0.5, 0.25], [0.0] * (DEFAULT_ANCHOR_HOP + 1), DEFAULT_ANCHOR_HOP)),
        ("anchor_block_count_mismatch", "anchor_block_count_mismatch", recombine,
         ([-0.5, 0.25], [0.0] * DEFAULT_ANCHOR_HOP, DEFAULT_ANCHOR_HOP)),
        ("nonfinite_anchor", "nonfinite_anchor", recombine,
         ([math.nan] + [0.0], [0.0] * (DEFAULT_ANCHOR_HOP * 2),
          DEFAULT_ANCHOR_HOP)),
        ("nonfinite_residual", "nonfinite_residual", recombine,
         ([0.0, 0.0],
          [math.inf] + [0.0] * (DEFAULT_ANCHOR_HOP * 2 - 1),
          DEFAULT_ANCHOR_HOP)),
        ("empty_recombine_stream", "invalid_stream_length", recombine,
         ([], [], DEFAULT_ANCHOR_HOP)),
        ("duplicate_json_key", "duplicate_json_key:a", parse_strict_json,
         ('{"a":1,"a":2}',)),
        ("nonfinite_json_constant", "nonfinite_json_constant:NaN",
         parse_strict_json, ('{"a":NaN}',)),
        ("invalid_json", "invalid_json", parse_strict_json, ("{",)),
    ]

    before = object_digest({
        "conservation": [evaluate_conservation(case)
                         for case in conservation_cases()],
        "dual": dual_stream_case(),
        "preservation": preservation_control(),
        "identity": identity_control(),
    })
    records: List[Dict[str, Any]] = []
    for case_id, expected, function, arguments in cases:
        actual = _reject_code(function, *arguments)
        _require(actual == expected, "adverse_code_mismatch:" + case_id)
        records.append({
            "case_id": case_id,
            "status": "rejected",
            "code": actual,
            "state_unchanged": True,
        })
    after = object_digest({
        "conservation": [evaluate_conservation(case)
                         for case in conservation_cases()],
        "dual": dual_stream_case(),
        "preservation": preservation_control(),
        "identity": identity_control(),
    })
    _require(before == after, "adverse_state_mutation")
    return records


def exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "candidate_artifacts_absent",
            "requirement": (
                "Stage the exact PASE inference artifacts (enhancer checkpoint, "
                "feature-extractor/WavLM component, vocoder, and inference config) "
                "with immutable upstream revisions, exact filenames, byte counts "
                "and SHA-256 values."
            ),
            "state": (
                "No PASE source tree, checkpoint, safetensors/pickle file, config, "
                "vocoder or feature-extractor artifact is present in this "
                "workspace. The census records only that a checkpoint is "
                "published; no filename, byte count, digest or immutable revision "
                "is recorded, so no manifest can be admitted."
            ),
        },
        {
            "id": "pinned_runtime_absent",
            "requirement": (
                "Pin one exact inference runtime and toolchain (framework "
                "version, wheel/sdist digest, accelerator/CUDA or CPU build, "
                "hardware and deterministic settings) and prove it installs "
                "without the artifacts."
            ),
            "state": (
                "No PyTorch, transformers, torchaudio, ONNX Runtime or PASE "
                "package is installed or staged. No runtime digest, device, "
                "precision or deterministic setting exists, so no exact-runtime "
                "parity can be produced."
            ),
        },
        {
            "id": "artifact_rights_and_training_data_unclear",
            "requirement": (
                "Obtain written artifact-specific terms for code, weights, "
                "third-party components and training data, plus a redistribution "
                "and product-use decision."
            ),
            "state": (
                "Only a research-census claim of Apache-2.0 for the model card "
                "and repository is recorded. Weight-specific terms, WavLM/"
                "feature-extractor and vocoder component terms, training-corpus "
                "provenance (DNS-style noise, public speech, RIRs), "
                "redistribution and product-use clearance are unverified. No "
                "upstream portion may be copied, downloaded or redistributed."
            ),
        },
        {
            "id": "real_corpus_scoring_and_timing_absent",
            "requirement": (
                "Supply a rights-cleared paired 16 kHz noisy/clean cohort, an "
                "independent SI-SDR/STOI scorer pin, an authorized listening or "
                "predictive content-preservation screen, and target-host "
                "content/availability timing."
            ),
            "state": (
                "No corpus, clean reference, scorer pin, listening result, WER or "
                "speaker-similarity model, real output, RTF, deadline, memory "
                "measurement or independent review exists. No result may "
                "qualify."
            ),
        },
        {
            "id": "task_geometry_and_scope_unverified",
            "requirement": (
                "Verify PASE's exact task scope, noise-only versus joint "
                "noise/reverberation behavior, segment geometry, content delay, "
                "stochastic sampler, and linguistic-anchor objective against the "
                "pinned configuration."
            ),
            "state": (
                "The census describes a joint noise/reverberation generative "
                "enhancer with a WavLM denoising representation and dual-stream "
                "vocoder, but no exact task geometry, delay, sampler, seed, "
                "vocoder rate or 'phonologically anchored' evaluation protocol "
                "is staged. The proposal geometry in this package is not a "
                "verified PASE setting."
            ),
        },
    ]


def release_gates() -> List[Dict[str, Any]]:
    return [
        {
            "id": "RG-01",
            "requirement": "Exact licensed PASE source revision and every inference artifact pinned by immutable revision, filename, byte count and SHA-256.",
            "status": "blocked",
        },
        {
            "id": "RG-02",
            "requirement": "Pinned inference runtime/toolchain with install digests, accelerator or CPU build, precision and deterministic settings that installs without the artifacts.",
            "status": "blocked",
        },
        {
            "id": "RG-03",
            "requirement": "Artifact-specific rights for code, weights, third-party components and training data, including redistribution and product-use clearance.",
            "status": "blocked",
        },
        {
            "id": "RG-04",
            "requirement": "Exact-runtime parity on frozen synthetic inputs: segment geometry, content delay, final padding, drain calls and finite output.",
            "status": "blocked",
        },
        {
            "id": "RG-05",
            "requirement": "Rights-cleared paired 16 kHz noisy/clean cohort with an independent SI-SDR/STOI scorer pin and stratified held-out scoring.",
            "status": "blocked",
        },
        {
            "id": "RG-06",
            "requirement": "Clean-speech preservation, peaks, invalid outputs, authorized listening or predictive content screen, and measured content/availability timing, RTF and memory on the target.",
            "status": "blocked",
        },
        {
            "id": "RG-07",
            "requirement": "Opt-in provider intake, descriptor/effective-config review and independent exact-head review; no registration or default change before this gate.",
            "status": "blocked",
        },
        {
            "id": "RG-08",
            "requirement": "Explicit public default selection and release approval; DEFER remains in force until RG-01 through RG-07 close.",
            "status": "blocked",
        },
    ]


def enhancement_profile() -> Dict[str, Any]:
    return {
        "profile": "enhancement",
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "identity_and_noisy_control": {
                "status": "synthetic_only",
                "evidence": "Bit-exact zero-anchor identity control and a deterministic clean-target damage control; no noisy real recording.",
            },
            "established_task_matched_baseline": {
                "status": "blocked",
                "evidence": "No installed task-matched baseline or pinned candidate output exists for this host.",
            },
            "paired_si_sdr": {
                "status": "blocked",
                "evidence": "No rights-cleared paired clean reference; the synthetic SI-SDR is a labelled control only.",
            },
            "paired_stoi": {
                "status": "blocked",
                "evidence": "No clean-reference cohort and no pinned independent STOI scorer.",
            },
            "clean_speech_preservation": {
                "status": "synthetic_only",
                "evidence": "The block-hold negative control measurably damages synthetic clean speech; no real clean comparison.",
            },
            "peaks_and_invalid_outputs": {
                "status": "synthetic_only",
                "evidence": "Deterministic bounds and nonfinite rejection on synthetic values only; no candidate output was produced.",
            },
            "unpaired_screen_or_authorized_listening": {
                "status": "blocked",
                "evidence": "No predictive content-preservation model, authorized listening test or listener result.",
            },
            "alignment_state_memory": {
                "status": "synthetic_only",
                "evidence": "Exact integer source-interval mapping and deterministic block state only; no runtime state or memory measurement.",
            },
            "content_and_availability_timing": {
                "status": "blocked",
                "evidence": "No device clock, deadline, callback, RTF or availability measurement exists.",
            },
        },
        "not_applicable": [
            "candidate speech quality, intelligibility or listening score",
            "real noise/reverberation benefit, WER or speaker-similarity result",
            "benchmark, release or public-default claim",
        ],
    }


def board_row() -> Dict[str, Any]:
    """Read only the stable linked-row identity; never hash the full board."""
    payload = load_strict_json(SOURCE_ROOT / TASK_BOARD)
    _require(isinstance(payload, dict) and isinstance(payload.get("tasks"), list),
             "invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    _require(len(rows) == 1, "task_row_not_unique")
    row = rows[0]
    stable_fields = {
        "id": row["id"],
        "title": row["title"],
        "repository": row["repository"],
        "mode": row["mode"],
        "depends_on": row["depends_on"],
        "component": row["component"],
    }
    return {
        "stable_fields": stable_fields,
        "stable_sha256": object_digest(stable_fields),
        "full_tasks_json_hashed": False,
        "note": "Only the stable linked-row identity is gated. The mutable full plan/swarm/TASKS.json is never read into, hashed by or pinned to this package.",
    }


def _verify_pins() -> None:
    for path, expected in SOURCE_PINS.items():
        full = SOURCE_ROOT / path
        _require(full.is_file(), "missing_source_pin:" + path)
        _require(file_digest(full) == expected, "stale_source_pin:" + path)
    for path, expected in BOUNDARY_PINS.items():
        full = SDK_ROOT / path
        _require(full.is_file(), "missing_boundary_pin:" + path)
        _require(file_digest(full) == expected, "stale_boundary_pin:" + path)


def asset_admission() -> Dict[str, Any]:
    """Model the external-asset boundary without reading any bytes."""
    synthetic = validate_manifest(_manifest(assets=[
        _asset(id="synthetic-weights", sha256="0" * 64, byte_count=1024),
        _asset(id="synthetic-config", sha256="1" * 64, byte_count=64),
    ]))
    ordered = validate_manifest(_manifest(assets=[
        _asset(id="synthetic-config", sha256="1" * 64, byte_count=64),
        _asset(id="synthetic-weights", sha256="0" * 64, byte_count=1024),
    ]))
    _require(synthetic["asset_ids_in_order"]
             != ordered["asset_ids_in_order"], "asset_order_not_preserved")
    _require(synthetic["total_bytes"] == 1088, "asset_total_mismatch")
    return {
        "asset_readiness": "blocked",
        "required_assets": [],
        "candidate_artifact_pins": [],
        "admitted_synthetic_manifests": 2,
        "synthetic_manifest_digest": synthetic["manifest_digest"],
        "order_sensitive": True,
        "max_assets": MAX_ASSETS,
        "max_total_bytes": MAX_TOTAL_ASSET_BYTES,
        "storage": "external",
        "manifest_schema": MANIFEST_SCHEMA,
        "upstream_artifact_names_known": False,
        "bytes_read": 0,
        "downloads_attempted": 0,
        "note": "Synthetic manifests prove validator mechanics only. They are not upstream PASE artifacts and contain no candidate hash or byte count.",
    }


def _dual_stream_record() -> Dict[str, Any]:
    control = dual_stream_case()
    rejected_hop = _reject_code(recombine, [0.0], [0.0] * 160, 170)
    _require(rejected_hop == "anchor_hop_not_frame_multiple",
             "unexpected_hop_rejection")
    return {
        "case_id": control["case_id"],
        "hop_samples": control["hop_samples"],
        "anchor_window_samples": DEFAULT_ANCHOR_WINDOW,
        "anchor_blocks_per_frame": control["anchor_blocks_per_frame"],
        "anchor_block_count": control["anchor_block_count"],
        "sample_count": control["sample_count"],
        "frame_count": control["frame_count"],
        "anchor_values": control["anchor_values"],
        "output_digest": control["output_digest"],
        "frame_digests": control["frame_digests"],
        "max_abs_output": control["max_abs_output"],
        "block_boundaries_on_frame_edges": True,
        "exact": True,
        "unsupported_hop_rejection": rejected_hop,
        "vocoder_invoked": False,
        "status": "synthetic_only_not_qualified",
        "note": "The anchor hold models rate geometry and recombination bookkeeping only. No semantics, vocoder or model is present.",
    }


def _case_matrix(conservation: Sequence[Dict[str, Any]],
                 dual: Dict[str, Any], identity: Dict[str, Any],
                 preservation: Dict[str, Any],
                 adverse: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return list(conservation) + [
        {"case_id": dual["case_id"], "output_digest": dual["output_digest"],
         "frame_digests": dual["frame_digests"]},
        {"case_id": identity["control_id"],
         "output_digest": identity["output_digest"],
         "bit_identical": identity["bit_identical"]},
        {"case_id": preservation["control_id"],
         "output_digest": preservation["output_digest"],
         "si_sdr_db": preservation["si_sdr_db"],
         "snr_db": preservation["snr_db"]},
        {"case_id": "adverse", "codes": [item["code"] for item in adverse]},
    ]


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()

    conservation = [evaluate_conservation(case) for case in conservation_cases()]
    dual = _dual_stream_record()
    identity = identity_control()
    preservation = preservation_control()
    adverse = adverse_rejections()
    sweep = coverage_sweep()
    _require(sweep["all_conserved"], "coverage_sweep_failed")
    _require(not preservation["bit_identical"], "preservation_control_promoted")
    _require(all(item["state_unchanged"] for item in adverse),
             "adverse_state_changed")

    matrix = _case_matrix(conservation, dual, identity, preservation, adverse)
    repeat_digests: List[str] = []
    for _ in range(3):
        repeated_conservation = [evaluate_conservation(case)
                                 for case in conservation_cases()]
        repeated_dual = _dual_stream_record()
        repeated_identity = identity_control()
        repeated_preservation = preservation_control()
        repeated_adverse = adverse_rejections()
        repeat_digests.append(object_digest(_case_matrix(
            repeated_conservation, repeated_dual, repeated_identity,
            repeated_preservation, repeated_adverse)))
    repeat_digests.append(object_digest(matrix))
    _require(len(set(repeat_digests)) == 1, "case_matrix_not_repeatable")

    report = {
        "schema_id": REPORT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "scope": (
            "Task-local deterministic external-asset admission, frame/drain "
            "conservation and dual-rate recombination surrogate on synthetic "
            "values. No licensed PASE source, checkpoint, weight, WavLM "
            "component, vocoder, runtime, corpus, device, listening, benchmark "
            "or release result is present."
        ),
        "acceptance_profile": enhancement_profile(),
        "format": {
            "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "installed_v0_channels": 1,
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "installed_v0_sample_format": "f32",
            "installed_v0_geometry_preserved": True,
            "declared_intake_sample_rate_hz": SAMPLE_RATE_HZ,
            "declared_intake_channels": 1,
            "declared_intake_frame_samples": FRAME_SAMPLES,
            "declared_anchor_hop_samples": DEFAULT_ANCHOR_HOP,
            "declared_anchor_window_samples": DEFAULT_ANCHOR_WINDOW,
            "sample_period_ns": SAMPLE_PERIOD_NS,
            "max_buffering_delay_samples": MAX_DELAY_SAMPLES,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "content_delay_is_declared_not_verified": True,
        },
        "reference": {
            "reference_id": "pase-boundary-surrogate-v1",
            "modes": [
                "external_asset_manifest_admission",
                "frame_drain_conservation",
                "dual_rate_recombination_control",
                "clean_preservation_damage_control",
            ],
            "candidate": "not_present",
            "model_weights": False,
            "licensed_runtime": False,
            "downloads": False,
            "real_speech": False,
            "vocoder_invoked": False,
            "registered": False,
            "default_enabled": False,
            "numeric_parity_claim": False,
        },
        "asset_admission": asset_admission(),
        "stream_geometry": {
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "declared_anchor_hop_samples": DEFAULT_ANCHOR_HOP,
            "declared_anchor_window_samples": DEFAULT_ANCHOR_WINDOW,
            "anchor_hop_multiple_of_frame": True,
            "non_integral_hop_is_rejected_not_interpolated": True,
            "buffering_delay_domain": "0..16000 integer samples",
            "drain_budget_domain": "1..1024 audio-producing calls",
            "verified_against_candidate": False,
            "note": "Declared proposal geometry only; no candidate configuration was inspected or reproduced.",
        },
        "conservation_cases": conservation,
        "coverage_sweep": sweep,
        "identity_control": identity,
        "dual_stream_control": dual,
        "clean_preservation_control": preservation,
        "adverse_rejections": adverse,
        "adverse_all_rejected": True,
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "qualification": {
            "status": "not_qualified",
            "decision": "DEFER",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "candidate_source_present": False,
            "candidate_weights_present": False,
            "candidate_runtime_present": False,
            "asset_manifest_admitted": False,
            "real_recording_evidence": False,
            "exact_runtime_parity": False,
            "paired_scoring": False,
            "device_timing": False,
            "listening": False,
            "provider_intake": False,
        },
        "boundary": {
            "provider_registration": False,
            "descriptor_registry_change": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "default_selected": False,
            "enabled_by_default": False,
            "processor_exposure": False,
            "shared_build_or_ci_change": False,
            "sdk_data_dir_added": False,
            "asset_bundled": False,
            "weights_vendored": False,
            "board_or_handoff_changed": False,
            "network_access": False,
        },
        "board_row": board_row(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "repeatability": {
            "runs": 3,
            "case_matrix_digests": repeat_digests[:3],
            "byte_identical": True,
            "comparison": "exact SHA-256 over canonical case-matrix JSON; no tolerance",
        },
        "negative_claims": [
            "No licensed PASE source, checkpoint, weight, WavLM component, vocoder, runtime, corpus, device or listener was used.",
            "The asset-admission and frame-conservation model is not the catalogue candidate and produces no enhancement result.",
            "The dual-rate anchor hold is a labelled synthetic control; it invokes no vocoder and is not phonologically anchored.",
            "The clean-preservation block hold is a negative control that damages clean speech; it cannot qualify.",
            "No SI-SDR, STOI, WER, speaker-similarity, listening, RTF or benchmark claim about PASE is made.",
            "No provider, descriptor, registry, installed v0 default, shared build or CI was changed.",
        ],
        "reopen_condition": (
            "Close RG-01 through RG-08: pin exact PASE artifacts and an "
            "immutable source revision, pin an installing runtime, clear "
            "artifact and training-data rights, reproduce exact-runtime parity "
            "on frozen synthetic inputs, score a rights-cleared paired cohort "
            "with independent scorers, measure clean preservation and target "
            "timing, and complete opt-in provider intake with independent "
            "review before any default selection."
        ),
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def artifact_pins() -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        path = HERE / name
        _require(path.is_file(), "missing_artifact:" + name)
        pins[TASK_PREFIX + name] = file_digest(path)
    return pins


def build_contract() -> Dict[str, Any]:
    """Build contract.json after report.json and its sidecar are written."""
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "qualification_status": "not_qualified",
        "verification_profile": "enhancement",
        "scope": {
            "benchmark_claim": False,
            "device_timing": False,
            "listening": False,
            "network_access": False,
            "numeric_parity_claim": False,
            "processor_exposure": False,
            "public_default": False,
            "real_corpus": False,
            "real_speech": False,
            "release_claim": False,
            "runtime_invocation": False,
            "synthetic_only": True,
            "task_local_only": True,
            "weights": False,
        },
        "format": {
            "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "installed_v0_channels": 1,
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "installed_v0_geometry_preserved": True,
            "declared_anchor_hop_samples": DEFAULT_ANCHOR_HOP,
            "declared_anchor_window_samples": DEFAULT_ANCHOR_WINDOW,
            "sample_period_ns": SAMPLE_PERIOD_NS,
            "max_buffering_delay_samples": MAX_DELAY_SAMPLES,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "added_content_delay_samples": 0,
        },
        "public_boundary": {
            "header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "abi_major": 0,
            "abi_minor": 1,
            "registration": "none; no provider, descriptor, registry entry or installed default is added",
            "c_provider_added": False,
            "public_api_abi_changed": False,
            "installed_v0_behavior_changed": False,
            "shared_build_or_ci_changed": False,
            "processor_exposure": False,
        },
        "reference": {
            "reference_id": "pase-boundary-surrogate-v1",
            "modes": [
                "external_asset_manifest_admission",
                "frame_drain_conservation",
                "dual_rate_recombination_control",
                "clean_preservation_damage_control",
            ],
            "model_weights": False,
            "downloads": False,
            "licensed_runtime": False,
            "registered": False,
            "default_enabled": False,
            "numeric_parity_claim": False,
        },
        "asset_admission": {
            "asset_readiness": "blocked",
            "required_assets": [],
            "candidate_artifact_pins": [],
            "upstream_artifact_names_known": False,
            "storage": "external",
            "max_assets": MAX_ASSETS,
            "max_total_bytes": MAX_TOTAL_ASSET_BYTES,
            "manifest_schema": MANIFEST_SCHEMA,
            "bytes_read": 0,
            "downloads_attempted": 0,
        },
        "board_row": board_row(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(),
        "negative_claims": [
            "No licensed PASE source, checkpoint, weight, runtime or corpus was used.",
            "No qualified enhancement, preservation, timing or release result exists.",
            "No provider registration, installed v0, ABI, registry, default, shared build or CI change exists.",
        ],
        "reopen_condition": (
            "Close RG-01 through RG-08 with pinned PASE artifacts and runtime, "
            "cleared artifact and training-data rights, exact-runtime parity on "
            "frozen synthetic inputs, rights-cleared paired scoring, measured "
            "preservation and target timing, and independent opt-in provider "
            "review."
        ),
    }


def sources_bytes() -> bytes:
    """Regenerate SOURCES.sha256 bytes from hard pins plus live artifacts."""
    for path, expected in SOURCE_PINS.items():
        full = SOURCE_ROOT / path
        _require(full.is_file(), "missing_source_pin:" + path)
        _require(file_digest(full) == expected, "stale_source_pin:" + path)
    for path, expected in BOUNDARY_PINS.items():
        full = SDK_ROOT / path
        _require(full.is_file(), "missing_boundary_pin:" + path)
        _require(file_digest(full) == expected, "stale_boundary_pin:" + path)
    for name in PIN_FILES:
        _require((HERE / name).is_file(), "missing_artifact:" + name)

    lines = [
        "# SHA-256 pins for " + TASK_ID
        + "; source: paths are workspace-relative, others SDK-worktree-relative."
    ]
    for path in SOURCE_FILES:
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in BOUNDARY_FILES:
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in PIN_FILES:
        lines.append(f"{file_digest(HERE / name)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
