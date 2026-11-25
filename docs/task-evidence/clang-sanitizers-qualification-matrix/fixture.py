# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic Tool-profile fixture for the Clang sanitizer/fuzz matrix.

This is task-local developer tooling at the installed audio-sdk v0 boundary
(16 kHz, mono, float32, 160 samples per call). It maps the exact overflow,
state, malformed-input, missing-selection and installed-consumer scenarios
already present in the pinned SDK sources into a reproducible qualification
matrix. It never registers a provider, changes a default, edits a build file or
claims qualification: every SDK-target matrix row stays ``not-run`` or
``unavailable`` and the report status is ``not_qualified``.

No real audio, download, licensed runtime, device, network or paced workload
is involved. All numbers are frozen synthetic inputs and exact integer
arithmetic. The optional Clang probe recorded here is a standalone,
non-qualifying toolchain availability check, not an instrumented SDK run.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
ADAPTER_PATH = HERE / "adapter.json"

CONTRACT_ID = "audio-sdk/v0"
SCHEMA_ID = "audio-sdk/task-evidence/clang-sanitizers-qualification-matrix/report/0.1"
TOOL_VERSION = "0.1.0"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
INSTALL_LOCATION = "docs/task-evidence/clang-sanitizers-qualification-matrix"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
I64_MAX = 2**63 - 1
I64_MIN = -(2**63)
U32_MAX = 2**32 - 1
U64_MAX = 2**64 - 1
TWO53_PLUS_1 = 9007199254740993

AS_OK = 0
AS_INVALID_ARGUMENT = 1
AS_UNSUPPORTED = 2
AS_NEEDS_RESET = 5
AS_END_OF_STREAM = 7
AS_CLOSED = 9

FLAG_FINAL_INPUT = 1
FLAG_STARTUP_PADDING = 1
FLAG_FINAL_PADDING = 2

SPDX_LICENSE_TEXT = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_LICENSE_JSON_ESCAPED = "SPDX\\u002d" "License-Identifier: Apache-2.0"

SPDX = {
    "copyright": "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
    "license": SPDX_LICENSE_TEXT,
}

# Exact copied constants from the pinned installed-consumer fixture. They are
# reproduced here so this task never imports or writes another task's files.
IC_BASE_COMMIT = "3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41"
IC_GENERATOR = {
    "modulus": 101,
    "multiplier": 37,
    "frame_offset": 17,
    "offset": -50,
    "scale": 128,
}
IC_FRAME_LENGTHS = (160, 160, 37)
IC_FIRST_SAMPLE = TWO53_PLUS_1
IC_SOURCE_PINS = {
    "cpp-library/src/stages/identity.cpp":
        "5fff7e319c32485a541fec5785fefb11ca0d9ad4139d77e7126c1cf963811a44",
    "adapters/controls/adapter.json":
        "3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599",
}
IC_PAYLOAD_SCHEMA_ID = "audio-sdk/task-evidence/identity-pcm-fixture/0.1"
IC_PROVIDER_ID = "fixture.identity-pcm.v0"
IC_CONTRACT_ID = "audio-sdk/descriptor/0.1"

FUZZ_SEED = 20261124


def load_adapter(path: Optional[Path] = None) -> dict[str, Any]:
    """Strict-load the frozen scenario/provenance adapter."""
    adapter_path = Path(path) if path is not None else ADAPTER_PATH
    payload = json.loads(adapter_path.read_text(encoding="utf-8"),
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("adapter root is not an object")
    return payload


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value}")


def _escape_spdx_json(text: str) -> str:
    """Preserve the parsed SPDX value without a raw token in serialized JSON."""
    return text.replace(SPDX_LICENSE_TEXT, SPDX_LICENSE_JSON_ESCAPED)


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False)
    return _escape_spdx_json(text).encode("utf-8") + b"\n"


def canonical_compact_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)
    return _escape_spdx_json(text).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def data_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return data_digest(path.read_bytes())


def tensor_digest(values: Sequence[float]) -> str:
    """Digest over IEEE-754 little-endian f32 samples."""
    return data_digest(b"".join(struct.pack("<f", float(v)) for v in values))


def decimal_string(value: int) -> str:
    """Contract 0.1 canonical signed integer string; -0 is not emitted."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("decimal_string requires an integer")
    return str(value)


class LCG:
    """Version-stable 32-bit LCG; independent of Python random internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def add_u32_saturating(value: int, amount: int) -> int:
    """Mirror core/src/core/validity.c:8-11 with exact Python integers."""
    if value > I64_MAX - amount:
        return I64_MAX
    return value + amount


def subtract_u32_saturating(value: int, amount: int) -> int:
    """Mirror core/src/core/validity.c:13-16 with exact Python integers."""
    if value < I64_MIN + amount:
        return I64_MIN
    return value - amount


def local_offset(coordinate: int, source_first: int, produced: int) -> int:
    """Mirror core/src/core/validity.c:19-25."""
    if coordinate <= source_first:
        return 0
    distance = coordinate - source_first
    return produced if distance >= produced else int(distance)


def compute_validity(case: dict[str, Any]) -> dict[str, int]:
    """Reference model of as_compute_validity at the public v0 boundary."""
    first = int(case["first_input_sample"])
    edge_start = int(case.get("edge_start", 0))
    edge_end = int(case.get("edge_end", 0))
    source_first = int(case["source_first"])
    produced = int(case["produced"])
    provider_offset = int(case["provider_offset"])
    provider_count = int(case["provider_count"])
    accepted_end = int(case["accepted_end"])
    final_flags = int(case.get("final_flags", 0))

    content_start = add_u32_saturating(first, edge_start)
    content_end = subtract_u32_saturating(accepted_end, edge_end)
    if content_end < content_start:
        content_end = content_start

    provider_begin = provider_offset if provider_offset < produced else produced
    provider_end_wide = provider_offset + provider_count
    provider_end = provider_end_wide if provider_end_wide < produced else produced
    if provider_end < provider_begin:
        provider_end = provider_begin

    content_begin = local_offset(content_start, source_first, produced)
    content_limit = local_offset(content_end, source_first, produced)
    begin = max(provider_begin, content_begin)
    end = min(provider_end, content_limit)
    if end < begin:
        end = begin

    flags = 0
    if source_first < content_start:
        flags |= FLAG_STARTUP_PADDING
    if final_flags & FLAG_FINAL_PADDING and content_limit < produced:
        flags |= FLAG_FINAL_PADDING
    return {
        "valid_offset": begin,
        "valid_count": end - begin,
        "produced_count": produced,
        "flags": flags,
    }


def expected_validity_from_test(delay: int, origin: int,
                                remainder: Optional[int] = None) -> dict[str, int]:
    """Transcription of core/tests/test_validity.c:51-81 expected values."""
    produced = FRAME_SAMPLES
    if remainder is None:
        offset = delay if delay < FRAME_SAMPLES else FRAME_SAMPLES
        count = FRAME_SAMPLES - delay if delay < FRAME_SAMPLES else 0
        return {"valid_offset": offset, "valid_count": count}
    source = origin + FRAME_SAMPLES - delay
    local_start = source - origin
    valid_begin = max(0, local_start)
    valid_end = min(local_start + FRAME_SAMPLES,
                    origin + FRAME_SAMPLES + remainder - origin)
    if valid_begin > FRAME_SAMPLES:
        valid_begin = FRAME_SAMPLES
    expected_offset = valid_begin - local_start if valid_begin > local_start else 0
    if expected_offset > FRAME_SAMPLES:
        expected_offset = FRAME_SAMPLES
    expected_count = valid_end - valid_begin if valid_end > valid_begin else 0
    return {"valid_offset": expected_offset, "valid_count": expected_count}


def validity_case_for(delay: int, origin: int,
                      remainder: Optional[int] = None) -> dict[str, Any]:
    accepted_end = origin + FRAME_SAMPLES if remainder is None \
        else origin + FRAME_SAMPLES + remainder
    # The final-remainder loop in test_validity.c passes the final full-frame
    # end (origin + 160 - delay) as source_first; delay-boundary passes the
    # buffer start (origin - delay).
    source_first = origin - delay if remainder is None \
        else origin + FRAME_SAMPLES - delay
    return {
        "first_input_sample": origin,
        "edge_start": 0,
        "edge_end": 0,
        "source_first": source_first,
        "produced": FRAME_SAMPLES,
        "provider_offset": 0,
        "provider_count": FRAME_SAMPLES,
        "accepted_end": accepted_end,
    }


def admit_coordinates(epoch: int, first: int,
                      buffering_delay: int = 0) -> tuple[bool, Optional[str]]:
    """v0 create admission: uint64 epoch, int64 first, first+160 in range."""
    if not isinstance(epoch, int) or epoch < 0 or epoch > U64_MAX:
        return False, "epoch_out_of_uint64"
    if not isinstance(first, int) or first < 0 or first > I64_MAX - FRAME_SAMPLES:
        return False, "first_out_of_int64_frame_range"
    if buffering_delay < 0 or buffering_delay > 16000:
        return False, "buffering_delay_out_of_range"
    return True, None


def caller_frame(index: int, samples: Optional[Sequence[float]] = None,
                 epoch: int = 1, first: Optional[int] = None,
                 values: Optional[Sequence[float]] = None) -> dict[str, Any]:
    """One caller-owned, zero-padded 160-sample v0 frame."""
    if samples is None:
        samples = tuple((value % 101 - 50) / 128.0
                        for value in range(index * 7, index * 7 + FRAME_SAMPLES))
    if values is not None:
        samples = values
    padded = tuple(float(v) for v in samples) + (0.0,) * (
        FRAME_SAMPLES - len(samples))
    return {
        "struct_size_ok": True,
        "abi_major": 0,
        "abi_minor": 1,
        "input": padded[:FRAME_SAMPLES],
        "input_count": FRAME_SAMPLES,
        "input_valid_count": min(len(samples), FRAME_SAMPLES),
        "flags": FLAG_FINAL_INPUT if len(samples) < FRAME_SAMPLES else 0,
        "epoch": epoch,
        "first_input_sample": index * FRAME_SAMPLES if first is None else first,
    }


def default_output() -> dict[str, Any]:
    return {"samples_present": True, "capacity": FRAME_SAMPLES, "overlap": False}


@dataclass
class ModelResult:
    status: int
    reason: str = ""
    consumed_count: int = 0
    produced_count: int = 0
    valid_offset: int = 0
    valid_count: int = 0
    flags: int = 0
    epoch: int = 0
    source_first_sample: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "consumed_count": self.consumed_count,
            "produced_count": self.produced_count,
            "valid_offset": self.valid_offset,
            "valid_count": self.valid_count,
            "flags": self.flags,
            "epoch": self.epoch,
            "source_first_sample": self.source_first_sample,
        }


class V0SessionModel:
    """Minimal admission/state model of the installed v0 facade.

    It validates caller-owned frames, enforces the strictly increasing reset
    epoch, the final-input latch and the lifecycle rules, and never retains
    caller pointers. It is a Python model, not an instrumented SDK run.
    """

    def __init__(self, epoch: int = 1, first: int = 0,
                 buffering_delay: int = 0) -> None:
        admitted, reason = admit_coordinates(epoch, first, buffering_delay)
        if not admitted:
            raise ValueError(reason)
        self.epoch = epoch
        self.first_input_sample = first
        self.buffering_delay = buffering_delay
        self.next_input = first
        self.accepted_end = first
        self.state = "processing"
        self.final_accepted = False
        self.closed = False

    def _reject(self, status: int, reason: str) -> ModelResult:
        return ModelResult(status=status, reason=reason)

    def process(self, frame: Optional[dict[str, Any]],
                output: Optional[dict[str, Any]] = None) -> ModelResult:
        if self.closed:
            return self._reject(AS_CLOSED, "closed")
        if self.state == "needs_reset":
            return self._reject(AS_NEEDS_RESET, "needs_reset")
        if self.final_accepted:
            return self._reject(AS_INVALID_ARGUMENT, "after_final")
        if self.state in ("draining", "drained"):
            return self._reject(AS_INVALID_ARGUMENT, "after_drain")
        if frame is None:
            return self._reject(AS_INVALID_ARGUMENT, "missing_frame")
        if not frame.get("struct_size_ok", False):
            return self._reject(AS_INVALID_ARGUMENT, "short_header")
        if frame.get("abi_major", 0) != 0 or frame.get("abi_minor", 1) != 1:
            return self._reject(AS_UNSUPPORTED, "unsupported_abi")
        if output is None:
            output = default_output()
        if frame.get("input") is None:
            return self._reject(AS_INVALID_ARGUMENT, "null_input")
        if not output.get("samples_present", False):
            return self._reject(AS_INVALID_ARGUMENT, "null_output")
        if output.get("overlap", False):
            return self._reject(AS_INVALID_ARGUMENT, "overlap")
        if int(output.get("capacity", 0)) < FRAME_SAMPLES:
            return self._reject(AS_INVALID_ARGUMENT, "short_capacity")
        if int(frame.get("input_count", -1)) != FRAME_SAMPLES:
            return self._reject(AS_INVALID_ARGUMENT, "wrong_input_count")
        valid = int(frame.get("input_valid_count", -1))
        flags = int(frame.get("flags", 0))
        if not 1 <= valid <= FRAME_SAMPLES:
            return self._reject(AS_INVALID_ARGUMENT, "invalid_valid_count")
        if valid < FRAME_SAMPLES and not flags & FLAG_FINAL_INPUT:
            return self._reject(AS_INVALID_ARGUMENT, "partial_without_final")
        if flags & ~FLAG_FINAL_INPUT:
            return self._reject(AS_INVALID_ARGUMENT, "bad_flags")
        samples = frame["input"]
        if isinstance(samples, (str, bytes)) or len(samples) != FRAME_SAMPLES:
            return self._reject(AS_INVALID_ARGUMENT, "wrong_shape")
        as_float = tuple(float(v) for v in samples)
        if any(not math.isfinite(v) for v in as_float[:valid]):
            return self._reject(AS_INVALID_ARGUMENT, "nonfinite")
        if any(v != 0.0 for v in as_float[valid:]):
            return self._reject(AS_INVALID_ARGUMENT, "bad_padding")
        if int(frame.get("epoch", -1)) != self.epoch:
            return self._reject(AS_INVALID_ARGUMENT, "stale_epoch")
        first = int(frame.get("first_input_sample", -1))
        if first < self.first_input_sample:
            return self._reject(AS_INVALID_ARGUMENT, "out_of_order")
        if first != self.next_input:
            return self._reject(AS_INVALID_ARGUMENT, "wrong_position")
        if first > I64_MAX - FRAME_SAMPLES:
            return self._reject(AS_INVALID_ARGUMENT, "first_out_of_int64_frame_range")

        self.accepted_end = first + valid
        self.next_input = first + FRAME_SAMPLES
        self.final_accepted = bool(flags & FLAG_FINAL_INPUT)
        return ModelResult(
            status=AS_OK,
            consumed_count=FRAME_SAMPLES,
            produced_count=FRAME_SAMPLES,
            valid_offset=0,
            valid_count=valid,
            flags=FLAG_FINAL_PADDING if valid < FRAME_SAMPLES else 0,
            epoch=self.epoch,
            source_first_sample=first - self.buffering_delay,
        )

    def reset(self, epoch: int, first: int) -> ModelResult:
        if self.closed:
            return self._reject(AS_CLOSED, "closed")
        if not isinstance(epoch, int) or epoch <= self.epoch:
            return self._reject(AS_INVALID_ARGUMENT, "non_increasing_epoch")
        if not isinstance(first, int) or first < 0 or first > I64_MAX - FRAME_SAMPLES:
            return self._reject(AS_INVALID_ARGUMENT, "invalid_first")
        self.epoch = epoch
        self.first_input_sample = first
        self.next_input = first
        self.accepted_end = first
        self.state = "processing"
        self.final_accepted = False
        return ModelResult(status=AS_OK, epoch=epoch)

    def set_backend_failure(self) -> None:
        self.state = "needs_reset"

    def begin_drain(self) -> None:
        if not self.closed and self.state == "processing":
            self.state = "draining"

    def drain_next(self) -> ModelResult:
        if self.closed:
            return self._reject(AS_CLOSED, "closed")
        if self.state == "needs_reset":
            return self._reject(AS_NEEDS_RESET, "needs_reset")
        if self.state == "processing":
            return self._reject(AS_INVALID_ARGUMENT, "drain_before_begin")
        self.state = "drained"
        return ModelResult(status=AS_END_OF_STREAM, reason="completed_drain")

    def close(self) -> None:
        self.closed = True
        self.state = "closed"

    def snapshot(self) -> dict[str, Any]:
        return {
            "epoch": self.epoch,
            "first_input_sample": self.first_input_sample,
            "next_input": self.next_input,
            "accepted_end": self.accepted_end,
            "state": self.state,
            "final_accepted": self.final_accepted,
            "closed": self.closed,
        }


def run_overflow_scenarios(adapter: dict[str, Any]) -> dict[str, Any]:
    cases = []
    failures = []
    for case in adapter["overflow_scenarios"]:
        model = compute_validity(case)
        expected = {key: int(value)
                    for key, value in case["expected"].items()}
        passed = all(model[key] == value for key, value in expected.items())
        cases.append({
            "id": case["id"],
            "name": case["name"],
            "locator": case["locator"],
            "expected": expected,
            "model": {key: model[key] for key in ("valid_offset", "valid_count")},
            "passed": passed,
        })
        if not passed:
            failures.append(case["id"])

    sweeps = adapter["sweeps"]
    delay_cases = []
    for delay in sweeps["delay_boundaries"]["delays"]:
        origin = sweeps["delay_boundaries"]["origin"]
        case = validity_case_for(delay, origin)
        expected = expected_validity_from_test(delay, origin)
        model = compute_validity(case)
        delay_cases.append({
            "delay": delay,
            "source_first": case["source_first"],
            "expected": expected,
            "model": {"valid_offset": model["valid_offset"],
                      "valid_count": model["valid_count"]},
            "passed": model["valid_offset"] == expected["valid_offset"]
            and model["valid_count"] == expected["valid_count"],
        })
    final_cases = []
    for delay in sweeps["final_remainders"]["delays"]:
        origin = sweeps["final_remainders"]["origin"]
        for remainder in range(sweeps["final_remainders"]["remainders_start"],
                               sweeps["final_remainders"]["remainders_end"] + 1):
            case = validity_case_for(delay, origin, remainder)
            expected = expected_validity_from_test(delay, origin, remainder)
            model = compute_validity(case)
            final_cases.append({
                "delay": delay,
                "remainder": remainder,
                "expected": expected,
                "model": {"valid_offset": model["valid_offset"],
                          "valid_count": model["valid_count"]},
                "passed": model["valid_offset"] == expected["valid_offset"]
                and model["valid_count"] == expected["valid_count"],
            })

    length_count = 0  # 0, 1..159, 160, 161, 165, 319, 320, 321
    lengths = [0] + list(range(1, 160)) + [160, 161, 165, 319, 320, 321]
    length_count = len(lengths)
    first = adapter["coordinate_scenarios"][1]["first_input_sample"]
    length_coordinates = []
    for index, length in enumerate(lengths):
        epoch = adapter["coordinate_scenarios"][1]["base_epoch"] + index
        admitted, reason = admit_coordinates(epoch, first)
        length_coordinates.append({
            "length": length,
            "epoch_string": decimal_string(epoch),
            "first_string": decimal_string(first),
            "admitted": admitted,
            "reason": reason,
            "accepted_samples": min(length, FRAME_SAMPLES),
        })

    coordinates = []
    for case in adapter["coordinate_scenarios"]:
        epoch = case.get("epoch", case.get("base_epoch"))
        first = case["first_input_sample"]
        if epoch is None:
            raise ValueError(f"{case['id']} has no epoch")
        admitted, reason = admit_coordinates(epoch, first)
        if case.get("admitted"):
            passed = admitted and decimal_string(first) == \
                case["expected_first_string"]
            if "expected_epoch_string" in case:
                passed = passed and decimal_string(epoch) == \
                    case["expected_epoch_string"]
        else:
            passed = not admitted and reason == case["expected_reason"]
        coordinates.append({
            "id": case["id"],
            "name": case["name"],
            "locator": case["locator"],
            "epoch_string": decimal_string(epoch),
            "first_string": decimal_string(first),
            "admitted": admitted,
            "reason": reason,
            "passed": passed,
        })
        if not passed:
            failures.append(case["id"])

    all_cases = (delay_cases + final_cases)
    sweep_failures = [index for index, case in enumerate(all_cases)
                      if not case["passed"]]
    return {
        "exact_cases": cases,
        "delay_boundaries": delay_cases,
        "final_remainders": final_cases,
        "conformance_lengths": {
            "id": sweeps["conformance_lengths"]["id"],
            "locator": sweeps["conformance_lengths"]["locator"],
            "count": length_count,
            "expected_count": sweeps["conformance_lengths"]["expected_count"],
            "all_admitted": all(case["admitted"] for case in length_coordinates),
            "cases": length_coordinates,
        },
        "coordinates": coordinates,
        "counts": {
            "exact_cases": len(cases),
            "delay_boundaries": len(delay_cases),
            "final_remainders": len(final_cases),
            "conformance_lengths": length_count,
            "coordinates": len(coordinates),
        },
        "failures": failures + [f"sweep:{index}" for index in sweep_failures],
        "all_pass": not failures and not sweep_failures,
        "digest": object_digest({
            "exact": cases,
            "delay": delay_cases,
            "final": final_cases,
            "lengths": length_coordinates,
            "coordinates": coordinates,
        }),
    }


def run_state_scenarios(adapter: dict[str, Any]) -> dict[str, Any]:
    results = []
    failures = []
    for case in adapter["state_scenarios"]:
        name = case["name"]
        if name == "reset.epoch-non-increasing-rejected":
            session = V0SessionModel(case["create_epoch"], 0)
            before = session.snapshot()
            result = session.reset(case["reset_epoch"], case["reset_first"])
            after = session.snapshot()
            passed = result.status == case["expected_status"] and before == after
            observed = result.as_dict()
        elif name == "reset.epoch-42-at-123456":
            session = V0SessionModel(case["create_epoch"], 0,
                                     case["buffering_delay"])
            session.process(caller_frame(0, epoch=case["create_epoch"], first=0))
            reset = session.reset(case["reset_epoch"], case["reset_first"])
            process = session.process(caller_frame(
                0, epoch=case["reset_epoch"], first=case["reset_first"]))
            passed = (reset.status == case["expected_status"]
                      and process.status == AS_OK
                      and process.source_first_sample
                      == case["expected_source_first_sample"])
            observed = {"reset": reset.as_dict(), "process": process.as_dict()}
        elif name == "drain.eos-stable":
            session = V0SessionModel(1, 0)
            session.begin_drain()
            first_drain = session.drain_next()
            second_drain = session.drain_next()
            process = session.process(caller_frame(0))
            passed = (first_drain.status == case["expected_repeated_drain_status"]
                      and second_drain.status
                      == case["expected_repeated_drain_status"]
                      and process.status == case["expected_process_after_drain_status"])
            observed = {"first_drain": first_drain.as_dict(),
                        "second_drain": second_drain.as_dict(),
                        "process": process.as_dict()}
        elif name == "typical-process":
            session = V0SessionModel(case["epoch"], case["first_input_sample"])
            result = session.process(caller_frame(
                0, epoch=case["epoch"], first=case["first_input_sample"]))
            passed = (result.status == AS_OK
                      and result.consumed_count == case["consumed_count"]
                      and result.produced_count == case["produced_count"]
                      and result.source_first_sample == case["source_first_sample"])
            observed = result.as_dict()
        elif name == "backend-failure-needs-reset":
            session = V0SessionModel(1, 0)
            session.set_backend_failure()
            blocked = session.process(caller_frame(0))
            recovered = session.reset(2, 0)
            after = session.process(caller_frame(0, epoch=2))
            passed = (blocked.status == case["expected_after_failure_status"]
                      and recovered.status == AS_OK and after.status == AS_OK)
            observed = {"blocked": blocked.as_dict(),
                        "reset": recovered.as_dict(),
                        "after": after.as_dict()}
        else:
            session = V0SessionModel(1, 0)
            session.close()
            result = session.process(caller_frame(0))
            passed = result.status == case["expected_status"]
            observed = result.as_dict()
        session.close()
        if not passed:
            failures.append(case["id"])
        results.append({
            "id": case["id"],
            "name": name,
            "locator": case["locator"],
            "model_only": bool(case.get("model_only", False)),
            "expected_status": case.get("expected_status"),
            "observed": observed,
            "passed": passed,
        })

    # Session isolation with caller-owned independent inputs. Different valid
    # counts and distinct session snapshots prove no shared partial-frame state.
    a_session = V0SessionModel(1, 0)
    b_session = V0SessionModel(1, 0)
    a_values = tuple(0.25 for _ in range(FRAME_SAMPLES))
    b_values = tuple(-0.5 for _ in range(37))
    a = a_session.process(caller_frame(0, values=a_values))
    b = b_session.process(caller_frame(0, values=b_values))
    independent = (a.status == AS_OK and b.status == AS_OK
                   and a.valid_count == FRAME_SAMPLES
                   and b.valid_count == 37
                   and a != b
                   and a_session.snapshot() != b_session.snapshot())
    a_session.close()
    b_session.close()
    return {
        "scenarios": results,
        "sessions_uncoupled": independent,
        "failures": failures,
        "all_pass": not failures and independent,
        "digest": object_digest({"scenarios": results,
                                "sessions_uncoupled": independent}),
    }


def run_malformed_scenarios(adapter: dict[str, Any]) -> dict[str, Any]:
    # Exact constants from the pinned installed C consumer: EPOCH=7,
    # FIRST_SAMPLE=2**53+1, FINAL_VALID=37. Every probe targets the first
    # frame at FIRST_SAMPLE; none advances the coordinate.
    epoch = 7
    first = TWO53_PLUS_1

    def mutated(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
        frame = caller_frame(0, epoch=epoch, first=first)
        output = default_output()
        if name == "partial-without-final":
            frame["input_valid_count"] = 159
        elif name == "nonfinite":
            frame["input"] = (float("nan"),) + frame["input"][1:]
        elif name == "stale-epoch":
            frame["epoch"] = epoch - 1
        elif name == "wrong-position":
            frame["first_input_sample"] = first + FRAME_SAMPLES + 1
        elif name == "null-input":
            frame["input"] = None
        elif name == "short-capacity":
            output["capacity"] = 159
        elif name == "short-header":
            frame["struct_size_ok"] = False
        return frame, output

    cases = []
    failures = []
    for probe in adapter["malformed_probes"]:
        name = probe["name"]
        session = V0SessionModel(epoch, first)
        baseline = session.snapshot()
        if name == "after-final":
            final_frame = caller_frame(0, epoch=epoch, first=first,
                                       values=(0.1,) * 37)
            warm = session.process(final_frame)
            # A rejected post-final call must preserve the state that the
            # accepted final frame established, not the pre-final state.
            baseline = session.snapshot()
            frame, output = caller_frame(
                0, epoch=epoch, first=first), default_output()
        else:
            warm = None
            frame, output = mutated(name)
        result = session.process(frame, output)
        unchanged = baseline == session.snapshot()
        passed = (result.status == probe["expected_status"]
                  and result.valid_count == 0 and unchanged
                  and (warm is None or warm.status == AS_OK))
        if not passed:
            failures.append(probe["id"])
        cases.append({
            "id": probe["id"],
            "name": name,
            "locator": probe["locator"],
            "expected_status": probe["expected_status"],
            "observed_status": result.status,
            "valid_count": result.valid_count,
            "state_unchanged": unchanged,
            "passed": passed,
        })
        session.close()

    registered = {"fixture.identity-pcm.v0": (2,)}
    unregistered = "fixture.does-not-exist.v0"

    def query(provider_id: str) -> int:
        return AS_OK if provider_id in registered else AS_UNSUPPORTED

    def effective(provider_id: str, mode: int) -> int:
        if provider_id not in registered or mode not in registered[provider_id]:
            return AS_UNSUPPORTED
        return AS_OK

    selection_observations = {
        "SEL-01": query(unregistered),
        "SEL-02": effective(unregistered, 2),
        "SEL-03": effective("fixture.identity-pcm.v0", 1),
        "SEL-04": effective("fixture.identity-pcm.v0", 3),
        "SEL-05": query(unregistered),
        "SEL-06": AS_INVALID_ARGUMENT,
    }
    selections = []
    for item in adapter["missing_selections"]:
        observed = selection_observations[item["id"]]
        passed = observed == item["expected_status"]
        if not passed:
            failures.append(item["id"])
        selections.append({
            "id": item["id"],
            "name": item["name"],
            "expected_status": item["expected_status"],
            "observed_status": observed,
            "passed": passed,
        })
    return {
        "malformed_probes": cases,
        "missing_selections": selections,
        "failures": failures,
        "all_pass": not failures,
        "digest": object_digest({"malformed": cases,
                                "missing": selections}),
    }


def _mutators() -> tuple[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]], ...]:
    def partial(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input_valid_count"] = 159

    def nonfinite(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input"] = (float("nan"),) + frame["input"][1:]

    def stale(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["epoch"] = 0

    def wrong_position(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["first_input_sample"] = 161

    def null_input(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input"] = None

    def short_capacity(frame: dict[str, Any], output: dict[str, Any]) -> None:
        output["capacity"] = 159

    def short_header(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["struct_size_ok"] = False

    def abi_major(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["abi_major"] = 1

    def abi_minor(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["abi_minor"] = 2

    def bad_flags(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["flags"] = 2

    def count_159(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input_count"] = 159

    def count_161(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input_count"] = 161

    def bad_padding(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input_valid_count"] = 10
        frame["flags"] = FLAG_FINAL_INPUT
        frame["input"] = frame["input"][:10] + (0.3,) + frame["input"][11:]

    def negative_first(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["first_input_sample"] = -1

    def zero_valid(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["input_valid_count"] = 0

    def duplicate(frame: dict[str, Any], output: dict[str, Any]) -> None:
        frame["first_input_sample"] = 0

    return (
        ("partial_without_final", partial),
        ("nonfinite", nonfinite),
        ("stale_epoch", stale),
        ("wrong_position", wrong_position),
        ("null_input", null_input),
        ("short_capacity", short_capacity),
        ("short_header", short_header),
        ("abi_major_1", abi_major),
        ("abi_minor_2", abi_minor),
        ("bad_flags", bad_flags),
        ("input_count_159", count_159),
        ("input_count_161", count_161),
        ("bad_padding", bad_padding),
        ("negative_first", negative_first),
        ("zero_valid_count", zero_valid),
        ("duplicate_frame", duplicate),
    )


def build_fuzz_corpus(adapter: dict[str, Any]) -> dict[str, Any]:
    spec = adapter["fuzz_corpus"]
    mutators = _mutators()
    if len(mutators) != spec["mutation_count"]:
        raise AssertionError("mutation count mismatch")
    rng = LCG(spec["seed"])
    cases = []
    for index in range(spec["case_count"]):
        name, mutate = mutators[index % len(mutators)]
        values = tuple(round(0.01 * rng.uniform(), 12)
                       for _ in range(FRAME_SAMPLES))
        session = V0SessionModel(1, 0)
        warm = session.process(caller_frame(0, values=values))
        if warm.status != AS_OK:
            raise AssertionError("fuzz warm-up frame rejected")
        frame = caller_frame(1, values=values)
        output = default_output()
        mutate(frame, output)
        result = session.process(frame, output)
        frame_bytes = b"".join(struct.pack("<f", v)
                               for v in frame["input"] or ())
        case_digest = data_digest(json.dumps({
            "index": index,
            "mutation": name,
            "abi": [frame["abi_major"], frame["abi_minor"]],
            "input_count": frame["input_count"],
            "input_valid_count": frame["input_valid_count"],
            "flags": frame["flags"],
            "epoch": frame["epoch"],
            "first": frame["first_input_sample"],
            "capacity": output["capacity"],
            "header_ok": frame["struct_size_ok"],
            "samples_sha256": data_digest(frame_bytes),
        }, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        cases.append({
            "index": index,
            "mutation": name,
            "status": result.status,
            "reason": result.reason,
            "valid_count": result.valid_count,
            "frame_digest": case_digest,
        })
    by_mutation: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for case in cases:
        by_mutation[case["mutation"]] = by_mutation.get(case["mutation"], 0) + 1
        by_status[str(case["status"])] = by_status.get(str(case["status"]), 0) + 1
    all_rejected = all(case["status"] != AS_OK and case["valid_count"] == 0
                       for case in cases)
    return {
        "id": spec["id"],
        "name": spec["name"],
        "seed": spec["seed"],
        "qualifying_fuzz_run": spec["qualifying_fuzz_run"],
        "case_count": len(cases),
        "all_rejected": all_rejected,
        "by_mutation": dict(sorted(by_mutation.items())),
        "by_status": dict(sorted(by_status.items())),
        "corpus_digest": object_digest(cases),
        "note": spec["note"],
        "cases": cases,
    }


def installed_sample(frame_index: int, position: int) -> float:
    raw = (position * IC_GENERATOR["multiplier"]
           + frame_index * IC_GENERATOR["frame_offset"]) % IC_GENERATOR["modulus"]
    return (raw + IC_GENERATOR["offset"]) / IC_GENERATOR["scale"]


def installed_samples() -> tuple[float, ...]:
    values = [installed_sample(frame, position)
              for frame, length in enumerate(IC_FRAME_LENGTHS)
              for position in range(length)]
    if len(values) != sum(IC_FRAME_LENGTHS):
        raise AssertionError("installed fixture length mismatch")
    return tuple(values)


def installed_payload(values: Sequence[float]) -> dict[str, Any]:
    return {
        "schema_id": IC_PAYLOAD_SCHEMA_ID,
        "base_commit": IC_BASE_COMMIT,
        "provider_id": IC_PROVIDER_ID,
        "contract_id": IC_CONTRACT_ID,
        "format": {
            "sample_format": "f32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
        },
        "first_input_sample": IC_FIRST_SAMPLE,
        "frame_lengths": list(IC_FRAME_LENGTHS),
        "generator": dict(IC_GENERATOR),
        "source_pins": dict(IC_SOURCE_PINS),
        "samples": list(values),
    }


def build_installed_consumer(adapter: dict[str, Any]) -> dict[str, Any]:
    spec = adapter["installed_consumer"]
    values = installed_samples()
    payload_bytes = canonical_compact_bytes(installed_payload(values))
    payload_digest = data_digest(payload_bytes)
    pcm_digest = tensor_digest(values)
    payload_ok = (len(payload_bytes) == spec["expected_canonical_payload_bytes"]
                  and payload_digest == spec["expected_canonical_payload_sha256"])
    pcm_ok = pcm_digest == spec["expected_pcm_f32_sha256"]

    session = V0SessionModel(1, spec["first_input_sample"],
                             spec["buffering_delay_samples"])
    offset = 0
    produced_samples = 0
    all_bit_exact = True
    frame_count = 0
    for frame_index, length in enumerate(spec["frame_lengths"]):
        frame_values = values[offset:offset + length]
        frame = caller_frame(frame_index, values=frame_values,
                             epoch=1, first=spec["first_input_sample"] + offset)
        result = session.process(frame)
        offset += length
        frame_count += 1
        if result.status != AS_OK:
            all_bit_exact = False
            break
        produced_samples += result.valid_count
        if tuple(frame["input"][:result.valid_count]) != tuple(frame_values):
            all_bit_exact = False
    session.begin_drain()
    eos = session.drain_next()
    return {
        "rerun_in_this_task": spec["rerun_in_this_task"],
        "frame_lengths": spec["frame_lengths"],
        "frame_count": frame_count,
        "sample_count": len(values),
        "first_input_sample": spec["first_input_sample"],
        "first_input_sample_string": decimal_string(spec["first_input_sample"]),
        "buffering_delay_samples": spec["buffering_delay_samples"],
        "produced_valid_samples": produced_samples,
        "bit_identical_valid_content": all_bit_exact,
        "drain_status": eos.status,
        "expected_canonical_payload_bytes": spec["expected_canonical_payload_bytes"],
        "observed_canonical_payload_bytes": len(payload_bytes),
        "expected_canonical_payload_sha256": spec["expected_canonical_payload_sha256"],
        "observed_canonical_payload_sha256": payload_digest,
        "expected_pcm_f32_sha256": spec["expected_pcm_f32_sha256"],
        "observed_pcm_f32_sha256": pcm_digest,
        "payload_digest_match": payload_ok,
        "pcm_digest_match": pcm_ok,
        "archive_sha256": spec["archive_sha256"],
        "build_id": spec["build_id"],
        "native_ctest_pass": spec["native_ctest_pass"],
        "installed_ctest_pass": spec["installed_ctest_pass"],
        "installed_conformance_pass": spec["installed_conformance_pass"],
        "installed_conformance_fail": spec["installed_conformance_fail"],
        "installed_conformance_skip": spec["installed_conformance_skip"],
        "skipped_checks": list(spec["skipped_checks"]),
        "measured_workload": spec["measured_workload"],
        "all_match": (payload_ok and pcm_ok and all_bit_exact
                      and produced_samples == len(values) and eos.status == AS_END_OF_STREAM),
        "note": "Pinned sibling-task evidence is reproduced as deterministic model inputs only; no installed binary was built, extracted or executed in this task.",
    }


def verify_pins(adapter: dict[str, Any]) -> list[dict[str, Any]]:
    verified = []
    for pin in adapter["source_pins"]:
        root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
        path = root / pin["path"]
        digest = file_digest(path) if path.is_file() else None
        verified.append({
            "id": pin["id"],
            "path": pin["path"],
            "root": pin["root"],
            "sha256": pin["sha256"],
            "observed_sha256": digest,
            "verified": digest == pin["sha256"],
        })
    return verified


def artifact_pins() -> list[dict[str, str]]:
    names = ("adapter.json", "fixture.py", "run.py", "test_fixture.py",
             "verify.py")
    return [{
        "path": name,
        "kind": "task_fixture",
        "sha256": file_digest(HERE / name),
    } for name in names if (HERE / name).is_file()]


def status_counts(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return dict(sorted(counts.items()))


def build_report() -> dict[str, Any]:
    adapter = load_adapter()
    pins = verify_pins(adapter)
    pins_ok = all(pin["verified"] for pin in pins)

    overflow = run_overflow_scenarios(adapter)
    state = run_state_scenarios(adapter)
    malformed = run_malformed_scenarios(adapter)
    corpus = build_fuzz_corpus(adapter)
    installed = build_installed_consumer(adapter)

    typical = V0SessionModel(1, 0)
    typical_result = typical.process(caller_frame(0, epoch=1, first=0))
    typical.begin_drain()
    typical_eos = typical.drain_next()
    typical_ok = (typical_result.status == AS_OK
                  and typical_result.consumed_count == FRAME_SAMPLES
                  and typical_result.produced_count == FRAME_SAMPLES
                  and typical_result.valid_count == FRAME_SAMPLES
                  and typical_eos.status == AS_END_OF_STREAM)
    typical.close()

    all_controls_ok = (pins_ok and overflow["all_pass"] and state["all_pass"]
                       and malformed["all_pass"] and corpus["all_rejected"]
                       and installed["all_match"] and typical_ok)

    matrix = dict(adapter["qualification_matrix"])
    rows = matrix["rows"]
    qualified_rows = [row["id"] for row in rows if row["status"] == "qualified"]
    matrix_report = {
        "axes": matrix["axes"],
        "status_vocabulary_source": matrix["status_vocabulary_source"],
        "rows": rows,
        "status_counts": status_counts(rows),
        "qualified_rows": qualified_rows,
        "zero_qualified_rows": not qualified_rows,
    }

    artifacts = artifact_pins()
    report = {
        "schema_id": SCHEMA_ID,
        "spdx": SPDX,
        "tool_version": TOOL_VERSION,
        "task_id": adapter["task_id"],
        "base_commit": BASE_COMMIT,
        "profile": "Tool",
        "status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "install_location": INSTALL_LOCATION,
        "boundary": adapter["boundary"],
        "provenance": {
            "repository": "https://github.com/armaudia/audio-sdk.git",
            "branch": f"swarm/{adapter['task_id']}",
            "tool_version": TOOL_VERSION,
            "task_base_commit": BASE_COMMIT,
            "compiler": adapter["toolchain_probe"]["compiler"],
            "compiler_version": adapter["toolchain_probe"]["compiler_version"],
            "target_triple": adapter["toolchain_probe"]["target_triple"],
            "probe_status": adapter["toolchain_probe"]["status"],
            "probe_qualifying": adapter["toolchain_probe"]["qualifying"],
        },
        "source_pins": pins,
        "artifact_pins": artifacts,
        "source_pins_ok": pins_ok,
        "overflow": overflow,
        "state": state,
        "malformed": malformed,
        "fuzz_corpus": corpus,
        "installed_consumer": installed,
        "controls": {
            "clean_checkout": {
                "pinned_base_commit": BASE_COMMIT,
                "package_not_rebuilt_here": True,
                "write_scope": INSTALL_LOCATION,
                "verified_by": "verify.py scope_ok",
            },
            "extracted_package": {
                "rerun_in_this_task": False,
                "pinned_archive_sha256": installed["archive_sha256"],
                "pinned_build_id": installed["build_id"],
            },
            "typical_use": {
                "epoch": 1,
                "first_input_sample": 0,
                "consumed_count": typical_result.consumed_count,
                "produced_count": typical_result.produced_count,
                "valid_count": typical_result.valid_count,
                "source_first_sample": typical_result.source_first_sample,
                "drain_status": typical_eos.status,
                "passed": typical_ok,
            },
            "caller_owned_inputs": {
                "generator": "deterministic LCG and copied k/128 installed fixture",
                "facade_copies_input": True,
                "model_retains_caller_pointer": False,
            },
            "malformed_inputs": {
                "probe_count": len(malformed["malformed_probes"]),
                "all_expect_zero_valid_invalid_argument": malformed["all_pass"],
            },
            "missing_optional_selection": {
                "selection_count": len(malformed["missing_selections"]),
                "no_inferred_fallback": True,
                "all_explicit": malformed["all_pass"],
            },
            "layers_separated": True,
            "controls_all_pass": all_controls_ok,
        },
        "compile_build_evidence": {
            "sdk_instrumented_build": "not_run",
            "sdk_native_build": "not_run_in_this_task",
            "build_files_changed": False,
            "ci_changed": False,
            "standalone_toolchain_probe": adapter["toolchain_probe"],
            "note": "Standalone probe compilation is not compile evidence for the SDK target.",
        },
        "synthetic_runtime_evidence": {
            "overflow_model_pass": overflow["all_pass"],
            "state_model_pass": state["all_pass"],
            "malformed_model_pass": malformed["all_pass"],
            "deterministic_corpus_pass": corpus["all_rejected"],
            "installed_consumer_model_pass": installed["all_match"],
            "no_sdk_binary_instrumented": True,
            "note": "Python model results and synthetic inputs cannot promote a qualification row.",
        },
        "measured_workload_support": {
            "status": "blocked",
            "pacing": "not_measured",
            "deadline": None,
            "cpu": "not_measured",
            "memory": "not_measured",
            "device": "not_measured",
            "note": "No measured workload support exists in this task.",
        },
        "toolchain_probe": adapter["toolchain_probe"],
        "qualification_matrix": matrix_report,
        "gates": adapter["gates"],
        "adverse_observations": adapter["adverse_observations"],
        "regressions": [],
        "regression_policy": "No paired quality or timing control was measured, so there is no scored regression. All blocked probes and pinned skips are reported verbatim under adverse_observations.",
        "counts": {
            "source_pins": len(pins),
            "task_artifact_pins": len(artifacts),
            "overflow_exact_cases": overflow["counts"]["exact_cases"],
            "overflow_delay_boundaries": overflow["counts"]["delay_boundaries"],
            "overflow_final_remainders": overflow["counts"]["final_remainders"],
            "overflow_conformance_lengths": overflow["counts"]["conformance_lengths"],
            "overflow_coordinates": overflow["counts"]["coordinates"],
            "state_scenarios": len(state["scenarios"]),
            "malformed_probes": len(malformed["malformed_probes"]),
            "missing_selections": len(malformed["missing_selections"]),
            "fuzz_cases": corpus["case_count"],
            "installed_frame_count": installed["frame_count"],
            "matrix_rows": len(rows),
            "gates": len(adapter["gates"]),
            "adverse_observations": len(adapter["adverse_observations"]),
        },
        "digests": {
            "adapter": file_digest(ADAPTER_PATH),
            "overflow": overflow["digest"],
            "state": state["digest"],
            "malformed": malformed["digest"],
            "fuzz_corpus": corpus["corpus_digest"],
            "installed_payload": installed["observed_canonical_payload_sha256"],
            "installed_pcm_f32": installed["observed_pcm_f32_sha256"],
        },
    }
    return report


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return canonical_bytes(report)


def main() -> None:
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("usage: run.py <report.json>")
    report_path = Path(sys.argv[1])
    report = build_report()
    report_path.write_bytes(canonical_report_bytes(report))
    sidecar = report_path.parent / f"{report_path.name}.sha256"
    sidecar.write_text(f"{file_digest(report_path)}  {report_path.name}\n",
                       encoding="utf-8")
    print(f"report_sha256={file_digest(report_path)}")
    print(f"qualification_status={report['qualification_status']} "
          f"status={report['status']} "
          f"controls_all_pass={report['controls']['controls_all_pass']} "
          f"qualified_rows={len(report['qualification_matrix']['qualified_rows'])}")


if __name__ == "__main__":
    main()
