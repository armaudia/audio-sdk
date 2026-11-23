# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local protocol-v1-shaped adapter and canonical report regeneration.

Opt-in developer boundary only.  It is not registered in audio-bench, is not an
installed SDK provider and produces no Bench bundle.  ``samples`` is the
microphone stream; ``reference_samples`` is the explicit playback/render
stream.  If the reference is withheld the adapter reports ``blocked`` with
``metrics: null`` and passes the microphone through without adapting.
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
IDENTITY = "nlms-aec-reference-v1"
ADAPTER_ID = "nlms-aec"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples",
                              "reference_samples", "reference_mode"}
CONTROLS = ("nlms_adaptive", "fixed_attenuation", "identity", "no_reference_passthrough")
REFERENCE_MODES = ("explicit", "delayed", "withheld")
FIXTURES = ("single_talk", "double_talk", "delay_change", "near_only",
            "impulse", "step", "silence")


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


def _samples(value: Any, name: str) -> Optional[List[float]]:
    if value is None:
        return None
    if (not isinstance(value, list) or not value
            or len(value) % reference.FRAME_SAMPLES
            or any(isinstance(item, bool) or not isinstance(item, (int, float))
                   or not math.isfinite(item) or abs(item) > reference.MAX_ABS_INPUT
                   for item in value)):
        raise RequestError("invalid_" + name)
    return [float(item) for item in value]


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
    if request["reference_mode"] not in REFERENCE_MODES:
        raise RequestError("unknown_reference_mode")
    mic = _samples(request["samples"], "samples")
    ref = _samples(request["reference_samples"], "reference_samples")
    if mic is None:
        if request["stimulus_id"] not in FIXTURES:
            raise RequestError("unknown_stimulus")
    elif ref is not None and len(ref) != len(mic):
        raise RequestError("reference_length_mismatch")
    if request["stimulus_id"] not in FIXTURES and mic is None:
        raise RequestError("unknown_stimulus")
    return config


def _fixture_streams(name: str):
    if name in ("impulse", "step", "silence"):
        data = reference.stimulus(name)
    else:
        data = reference.fixture(name)
    return data["microphone"], data["reference"]


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
        "supported_reference_modes": list(REFERENCE_MODES),
        "supported_fixtures": list(FIXTURES),
        "supported_tasks": ["AEC-01"],
        "supported_modes": ["causal_framewise", "paired_render_reference"],
        "supported_formats": ["mono 16 kHz float32, 160-sample frames"],
        "asset_readiness": [],
        "algorithmic_delay_samples": 0,
        "registration": "unregistered developer-only fixture; no SDK default or Bench result",
        "public_c_boundary": "optional task-local provider v0 source under provider/",
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    if request["samples"] is None:
        microphone, reference_stream = _fixture_streams(request["stimulus_id"])
    else:
        microphone = tuple(request["samples"])
        reference_stream = (tuple(request["reference_samples"])
                            if request["reference_samples"] is not None else None)
    mode = request["reference_mode"]
    if mode == "withheld":
        reference_stream = None
    elif mode == "delayed" and reference_stream is not None:
        reference_stream = reference.shift_signal(reference_stream,
                                                  reference.DELAYED_RENDER_SAMPLES)

    control = config["control"]
    adaptive = control == "nlms_adaptive"
    effective_ref = None if control == "no_reference_passthrough" else reference_stream
    data = {
        "microphone": microphone,
        "reference": effective_ref,
        "reference_mode": mode,
        "near": (0.0,) * len(microphone),
        "active_path": reference.PATH_A,
    }
    result = reference.run_stream(
        data, mode=("adaptive" if adaptive else control), fixed_gain=0.5)
    output = result["output"]
    finite = [math.isfinite(value) for value in output]
    blocked = effective_ref is None
    status = ("blocked_no_reference" if blocked
              else "misaligned_reference" if mode == "delayed" else "ok")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "control": control,
        "stimulus_id": request["stimulus_id"],
        "reference_mode": mode,
        "status": status,
        "metrics": None,  # paired scoring lives in the pinned report, not this transport adapter
        "qualifies": False,
        "errors": [],
        "output": {
            "sample_count": len(output),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.tensor_digest(output),
            "finite_count": sum(finite),
            "nonfinite_count": len(finite) - sum(finite),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)), default=0.0),
            "frame_statuses": result["statuses"],
            "state_digest": result["state_digest"],
            "double_talk_hold_frames": result["double_talk_frames"],
        },
        "disclosure": "synthetic-only developer result; not a Bench bundle, quality claim or release gate",
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
