# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in protocol-v1-shaped inspect/run CLI for integer-only synthetic traces."""

import argparse
import json
from pathlib import Path

from reference import BLOCK, CAPACITY, GAIN, HZ, LIMIT, SLEW, TARGET, TRACE_FIELDS, replay

TASK = "SDK-BUFFER-OCCUPANCY-CONTROLLER"
IDENTITY = "buffer-occupancy-controller-reference-v1"
CANDIDATE = {"kind": "reference", "id": "rate.buffer-occupancy.ref", "revision": 1}
ADAPTER = {"kind": "adapter", "id": IDENTITY, "revision": 1}
BOUNDARY = {
    "protocol_version": 1, "identity": IDENTITY, "tasks": [TASK],
    "input_kind": "synthetic_fifo_trace", "output_kinds": ["rate_commands", "timeline"],
    "modes": ["synthetic_virtual_clock"], "entrypoint": ["python3", "run.py"],
    "configuration": {"policy": ["controller", "fixed_1x"]},
    "clock_geometry": {
        "source": "synthetic-source", "playout": "virtual-playout",
        "nominal_sample_rate_hz": HZ, "playout_block_samples": BLOCK,
        "target_source_samples": TARGET, "capacity_source_samples": CAPACITY,
        "proportional_gain_ppm": GAIN, "max_rate_offset_ppm": LIMIT,
        "max_slew_ppm_per_block": SLEW,
    },
    "asset_readiness": [], "registration": "none", "paced_device": "not_run",
    "candidate_qualified": False,
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def request(trace=None, policy="controller"):
    value = {"protocol_version": 1, "operation": "inspect" if trace is None else "run",
             "candidate_ref": dict(CANDIDATE), "adapter_ref": dict(ADAPTER),
             "configuration": {"policy": policy}}
    if trace is not None:
        value.update(attempt_id="synthetic-replay", trace=trace)
    return value


def reject(reason, status="invalid"):
    return {"protocol_version": 1, "status": status, "error": reason,
            "candidate_qualified": False}


def dispatch(value):
    if not isinstance(value, dict):
        return reject("request_not_object")
    operation = value.get("operation")
    expected = set(request({} if operation == "run" else None))
    if expected - value.keys():
        return reject("missing_request_fields", "missing")
    if (set(value) != expected or operation not in ("inspect", "run")
            or type(value["protocol_version"]) is not int or value["protocol_version"] != 1):
        return reject("request_fields_or_version")
    for key, ref in (("candidate_ref", CANDIDATE), ("adapter_ref", ADAPTER)):
        supplied = value[key]
        if (not isinstance(supplied, dict) or supplied != ref
                or type(supplied["revision"]) is not int):
            return reject("invalid_" + key)
    config = value["configuration"]
    if not isinstance(config, dict) or set(config) != {"policy"} or config["policy"] not in (
            "controller", "fixed_1x"):
        return reject("invalid_configuration")
    base = {k: value[k] for k in request()}
    if operation == "inspect":
        return {**BOUNDARY, **base, "configuration": config,
                "supported_policies": BOUNDARY["configuration"]["policy"], "status": "complete"}
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        return reject("invalid_attempt_id")
    trace = value["trace"]
    if trace is None or (isinstance(trace, dict) and TRACE_FIELDS - trace.keys()):
        return reject("missing_trace_values", "missing")
    try:
        result = replay(trace, config["policy"] == "controller")
    except ValueError as error:
        return reject(str(error))
    return {**base, **result, "attempt_id": value["attempt_id"], "trace": trace,
            "mode": "synthetic_virtual_clock", "paced_device": "not_run",
            "candidate_qualified": False}


def dispatch_json(text):
    def unique(items):
        values = dict(items)
        if len(values) != len(items):
            raise ValueError("duplicate_json_key")
        return values

    def invalid_number(_):
        raise ValueError("integer_json_numbers_only")

    try:
        value = json.loads(text, object_pairs_hook=unique, parse_float=invalid_number,
                           parse_constant=invalid_number)
    except (ValueError, RecursionError):
        return reject("malformed_or_noninteger_json")
    return dispatch(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = dispatch_json(args.request.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result = reject("request_file_missing", "missing")
    except (OSError, UnicodeError):
        result = reject("request_file_unreadable")
    args.result.write_text(canonical(result), encoding="utf-8")
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
