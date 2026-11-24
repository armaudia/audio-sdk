# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local causal waveform adapter and canonical report regeneration.

The adapter is opt-in, unregistered and disabled by default. It is not an
installed SDK realtime v0 provider, produces no Bench bundle and changes no
descriptor, default, registry entry or public ABI. The only DSP mode is a
frame-causal 16 kHz/mono/f32/160-sample online mono WPE reference.
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
IDENTITY = "online-mono-wpe-reference-v1"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples"}
CONTROLS = ("online_wpe", "identity")
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
    if (not isinstance(config, dict) or set(config) != {"control", "provider_enabled"}):
        raise RequestError("invalid_configuration")
    if config["control"] not in CONTROLS:
        raise RequestError("unknown_control")
    if not isinstance(config["provider_enabled"], bool):
        raise RequestError("invalid_provider_switch")
    if operation == "inspect":
        return config
    if (not isinstance(request["attempt_id"], str) or not request["attempt_id"]
            or not isinstance(request["stimulus_id"], str)):
        raise RequestError("invalid_run_identity")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or not samples
                or len(samples) > reference.MAX_CHUNK_SAMPLES
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       for value in samples)
                or any(not math.isfinite(float(value)) for value in samples)):
            raise RequestError("invalid_samples")
    elif request["stimulus_id"] not in FIXTURES:
        raise RequestError("unknown_stimulus")
    return config


def _condition_samples(name: str):
    source = reference.clean_source()
    spec = reference.ROOM_SPECS[name]
    rir = reference.synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
    unscaled = reference._fft_convolve(source, rir)
    peak = max(abs(value) for value in unscaled)
    gain = min(1.0, 0.9 / peak)
    return tuple(value * gain for value in unscaled)


def fixture_samples(name: str):
    if name in reference.ROOM_SPECS:
        return _condition_samples(name)
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
        "supported_tasks": ["SDK-ONLINE-MONO-WPE-REFERENCE"],
        "supported_modes": ["causal_frame_streaming"],
        "supported_formats": ["mono 16 kHz float32 160-sample frames; installed v0 grid"],
        "content_delay_samples": reference.CONTENT_DELAY_SAMPLES,
        "realtime_v0_provider": False,
        "default_enabled": False,
        "provider_manifest": {
            "path": "provider.json",
            "default_enabled": False,
            "opt_in_required": True,
            "registered": False,
            "descriptor_settings": {},
        },
        "registration": "unregistered developer-only fixture; no SDK default or Bench result",
        "public_c_boundary": (
            "not used: task-local Python reference only; the installed v0 "
            "160-sample provider path is unchanged"),
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    samples = (tuple(float(value) for value in request["samples"])
               if request["samples"] is not None
               else fixture_samples(request["stimulus_id"]))
    enabled = config["provider_enabled"]
    if enabled and config["control"] == "online_wpe":
        status, output = reference.process_whole_clip(samples)
        applied = "online_wpe"
    else:
        status, output = reference.Status.OK, samples
        applied = "identity_provider_off" if not enabled else "identity_control"
    finite = [math.isfinite(value) for value in output]
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "provider_enabled": enabled,
        "applied_control": applied,
        "stimulus_id": request["stimulus_id"],
        "status": "complete" if status is reference.Status.OK else "rejected",
        "errors": [] if status is reference.Status.OK else [status.value],
        "output": {
            "sample_count": len(output),
            "frames_consumed": (len(samples) + reference.FRAME_SAMPLES - 1)
                               // reference.FRAME_SAMPLES,
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.tensor_digest(output),
            "finite_count": sum(finite),
            "nonfinite_count": len(finite) - sum(finite),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)),
                            default=0.0),
        },
        "disclosure": (
            "synthetic-only developer result; opt-in unregistered task-local "
            "reference, not a Bench bundle, quality claim or release gate"),
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
    report = reference.build_report()
    text, digest = reference.canonical_report(report)
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
