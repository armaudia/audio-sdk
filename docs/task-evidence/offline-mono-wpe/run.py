# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local offline waveform adapter and canonical report regeneration.

This is an opt-in developer boundary. It is not registered in audio-bench, is
not an installed SDK realtime v0 provider, and produces no Bench bundle. The
only DSP mode exposed here is offline whole-clip WPE; it is explicitly outside
the installed 16 kHz/mono/f32/160-sample realtime v0 provider path.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import reference

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
IDENTITY = "offline-mono-wpe-reference-v1"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples"}
CONTROLS = ("offline_wpe", "identity")
FIXTURES = ("short_rt60", "medium_rt60", "long_rt60", "clean", "impulse", "silence")


class RequestError(ValueError):
    pass


def _pairs(items: List[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise RequestError("duplicate_json_key")
        result[key] = value
    return result


def _constant(token: str) -> None:
    raise RequestError("nonfinite_json_constant:" + token)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_pairs, parse_constant=_constant)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def validate_ref(ref: Any, name: str) -> None:
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if (not isinstance(ref["id"], str) or not ref["id"]
            or isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int)
            or ref["revision"] < 1):
        raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if not required <= set(request) or set(request) - required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], "candidate_ref")
    validate_ref(request["adapter_ref"], "adapter_ref")
    config = request["configuration"]
    if not isinstance(config, dict) or set(config) != {"control"}:
        raise RequestError("invalid_configuration")
    if config["control"] not in CONTROLS:
        raise RequestError("unknown_control")
    if operation == "inspect":
        return config
    if (not isinstance(request["attempt_id"], str) or not request["attempt_id"]
            or not isinstance(request["stimulus_id"], str)):
        raise RequestError("invalid_run_identity")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or not samples
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       for value in samples)):
            raise RequestError("invalid_samples")
    elif request["stimulus_id"] not in FIXTURES:
        raise RequestError("unknown_stimulus")
    return config


def _condition_signals(name: str):
    source = reference.clean_source()
    spec = reference.ROOM_SPECS[name]
    rir = reference.synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
    unscaled = reference._fft_convolve(source, rir)
    peak = max(abs(value) for value in unscaled)
    gain = min(1.0, 0.9 / peak)
    return tuple(value * gain for value in unscaled)


def fixture_samples(name: str):
    if name in reference.ROOM_SPECS:
        return _condition_signals(name)
    if name == "clean":
        return reference.clean_source()
    if name == "impulse":
        return reference.impulse()
    if name == "silence":
        return reference.silence()
    raise RequestError("unknown_stimulus")


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": config,
        "requested_control": config["control"],
        "supported_controls": list(CONTROLS),
        "supported_fixtures": list(FIXTURES),
        "supported_tasks": ["CLN-04"],
        "supported_modes": ["offline_whole_clip"],
        "supported_formats": ["mono 16 kHz float32 whole clip; installed v0 grid is 160 samples"],
        "realtime_v0_provider": False,
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; no SDK default or Bench result",
        "public_c_boundary": (
            "not used: offline whole-clip WPE is outside the 160-sample causal v0 provider path"),
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    samples = (tuple(float(value) for value in request["samples"])
               if request["samples"] is not None
               else fixture_samples(request["stimulus_id"]))
    controller = reference.OfflineController()
    buffered: List[float] = []
    statuses: List[str] = []
    for start in range(0, len(samples), reference.CHUNK_SAMPLES):
        chunk = samples[start:start + reference.CHUNK_SAMPLES]
        result = controller.process(chunk)
        statuses.append(result.status.value)
        if result.status is not reference.Status.OK:
            break
        buffered.extend(chunk)
    if statuses and statuses[-1] == "ok" and config["control"] == "offline_wpe":
        final = controller.finish()
        statuses.append(final.status.value)
        output = list(final.samples)
    else:
        output = buffered
    finite = [math.isfinite(value) for value in output]
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "control": config["control"],
        "stimulus_id": request["stimulus_id"],
        "status": "complete" if statuses and all(status == "ok" for status in statuses) else "rejected",
        "errors": [] if statuses and all(status == "ok" for status in statuses) else statuses,
        "output": {
            "sample_count": len(output),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.tensor_digest(output),
            "finite_count": sum(finite),
            "nonfinite_count": len(finite) - sum(finite),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)), default=0.0),
            "frame_statuses": statuses,
            "state_digest": controller.state.digest(),
        },
        "disclosure": (
            "synthetic-only developer result; offline whole-clip mode is outside realtime "
            "v0, not a Bench bundle, quality claim or release gate"),
    }


def process_file(request_path: Path, result_path: Path) -> Dict[str, Any]:
    request = read_json(request_path)
    operation = request.get("operation") if isinstance(request, dict) else None
    if operation == "inspect":
        result = inspect(request)
    elif operation == "run":
        result = run(request)
    else:
        raise RequestError("unsupported_operation")
    result_path.write_bytes(canonical_bytes(result) + b"\n")
    return result


def generate_report() -> str:
    text, digest = reference.canonical_report(reference.build_report())
    REPORT_PATH.write_bytes(text.encode("utf-8") + b"\n")
    DIGEST_PATH.write_text(digest + "\n", encoding="ascii")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    parser.add_argument("--report", action="store_true", help="regenerate report.json and its SHA-256")
    options = parser.parse_args()
    if options.report:
        print(generate_report())
        return 0
    if bool(options.request) != bool(options.result):
        parser.error("--request and --result must be used together")
    if options.request:
        try:
            process_file(options.request, options.result)
        except RequestError as error:
            print(str(error), file=sys.stderr)
            return 2
        return 0
    parser.error("select --report or --request/--result")


if __name__ == "__main__":
    sys.exit(main())
