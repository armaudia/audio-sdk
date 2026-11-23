"""Opt-in, offline adapter for the band-limited POCS declipping reference.

The request/result envelope follows the public harness-controls adapter
(``adapters/controls/adapter.json``, protocol_version 1): inspect/run
operations, candidate_ref/adapter_ref revisions and a configuration object.
This task-local adapter is NOT registered in audio-bench and its result is NOT
a Bench bundle.  It processes fixed 2048-sample offline blocks; the installed
v0 path (16 kHz mono float32, 160-sample frames, realtime claim) is untouched.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys

import fixtures
import reference

ROOT = Path(__file__).resolve().parent
ADAPTER_ID = "band-limited-pocs-declipping"
IDENTITY = "band-limited-pocs-declipping-v1"
CONTROLS = ("identity", "clipped_input", "linear_interp", "pocs_declip")
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref",
                 "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id"}


class RequestError(ValueError):
    """Raised for a rejected adapter request."""


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key")
            result[key] = value
        return result

    def constant(token):
        raise RequestError("nonfinite_json_constant:" + token)

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def validate_ref(ref, name):
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise RequestError("invalid_" + name)
    if (isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int)
            or ref["revision"] < 1):
        raise RequestError("invalid_" + name)


def validate_request(request, operation):
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    allowed = required if operation == "inspect" else (RUN_FIELDS | {"stimulus_samples",
                                                                     "extensions"})
    if set(request) - allowed or not required <= set(request):
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != 1 or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    for name in ("candidate_ref", "adapter_ref"):
        validate_ref(request[name], name)
    config = request["configuration"]
    if not isinstance(config, dict):
        raise RequestError("configuration_not_object")
    control = config.get("control")
    if control not in CONTROLS:
        raise RequestError("unknown_control")
    if control == "identity":
        if set(config) != {"control"}:
            raise RequestError("unexpected_identity_configuration")
    else:
        try:
            validated = reference.validate_controls(
                {key: value for key, value in config.items() if key != "control"})
        except reference.ControlError as error:
            raise RequestError(str(error)) from error
        if not validated:
            raise RequestError("invalid_configuration")
    if operation == "run":
        if not isinstance(request["attempt_id"], str) or not request["attempt_id"]:
            raise RequestError("invalid_attempt_id")
        if not isinstance(request["stimulus_id"], str) or not request["stimulus_id"]:
            raise RequestError("invalid_stimulus_id")
        if request.get("stimulus_samples") is None and request["stimulus_id"] not in fixtures.STIMULI:
            raise RequestError("unknown_stimulus:" + request["stimulus_id"])
        override = request.get("stimulus_samples")
        if override is not None:
            if (not isinstance(override, list)
                    or len(override) != reference.OFFLINE_BLOCK_SAMPLES
                    or any(isinstance(value, bool) or not isinstance(value, (int, float))
                           for value in override)):
                raise RequestError("invalid_stimulus_samples")
    return config, control


def inspect(request):
    _, control = validate_request(request, "inspect")
    return {
        "protocol_version": 1,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": request["configuration"],
        "requested_control": control,
        "supported_controls": list(CONTROLS),
        "supported_tasks": [],
        "supported_modes": ["offline"],
        "supported_formats": ["mono 16 kHz float32, 2048-sample offline blocks; "
                              "not the installed 160-sample realtime v0 frame"],
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an audio-bench result",
    }


def _round(value, places=9):
    return round(float(value), places)


def run(request):
    config, control = validate_request(request, "run")
    override = request.get("stimulus_samples")
    clean = None if override is not None else fixtures.build_samples(request["stimulus_id"])
    samples = ([reference.f32(value) for value in override]
               if override is not None else list(clean))
    input_nonfinite = sum(1 for value in samples if not math.isfinite(value))
    threshold = float(config["threshold"]) if control != "identity" else None
    clipped = (reference.hard_clip(samples, threshold) if threshold is not None else None)
    mask = reference.clip_mask(clipped, threshold) if clipped is not None else []
    occupancy = sum(mask) / len(mask) if mask else 0.0
    trace = []
    metadata = {}
    errors = []

    if input_nonfinite:
        output = None
        status = "adverse_numerical"
        errors.append({"kind": "adverse_numerical",
                       "reason": "nonfinite_input_not_processed_or_serialized"})
    elif control == "identity":
        output = list(samples)
        status = "complete"
    elif control == "clipped_input":
        output = clipped
        status = "complete"
    elif control == "linear_interp":
        output = reference.linear_interpolate(clipped, mask)
        status = "complete"
    else:
        try:
            processed = reference.pocs_declip(
                clipped, mask, float(config["cutoff_hz"]), int(config["iterations"]))
        except (ValueError, OverflowError) as error:
            output = None
            status = "adverse_numerical"
            errors.append({"kind": "adverse_numerical", "reason": str(error)})
        else:
            output = processed["samples"]
            trace = [{"projection": item["projection"],
                      "max_delta": _round(item["max_delta"]),
                      "rms_delta": _round(item["rms_delta"]),
                      "clipped_pre_constraint_delta":
                          _round(item["clipped_pre_constraint_delta"]),
                      "peak_abs": _round(item["peak_abs"])} for item in processed["trace"]]
            metadata = {
                "projection_count": processed["projection_count"],
                "iterations": processed["iterations"],
                "cutoff_hz": processed["cutoff_hz"],
                "kept_bins": processed["kept_bins"],
            }
            status = "complete"

    result = {
        "protocol_version": 1,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "control": control,
        "stimulus_id": request["stimulus_id"],
        "status": status,
        "errors": errors,
        "input": {
            "sample_count": len(samples),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "f32",
            "samples_sha256": reference.digest_samples(samples),
            "clean_sha256": reference.digest_samples(clean) if clean is not None else None,
            "peak_abs": _round(max((abs(value) for value in samples
                                    if math.isfinite(value)), default=0.0)),
            "nonfinite_count": input_nonfinite,
            "clipped_samples": sum(mask),
            "clipping_occupancy": _round(occupancy, 6),
        },
        "output": {
            "sample_count": len(samples),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "byte_count": len(samples) * 4,
            "sdk_160_sample_frames": len(samples) // reference.SDK_FRAME_SAMPLES,
            "offline_blocks": len(samples) // reference.OFFLINE_BLOCK_SAMPLES,
            "samples_sha256": reference.digest_samples(output) if output is not None else None,
            "nonfinite_count": (sum(1 for value in output if not math.isfinite(value))
                                if output is not None else input_nonfinite),
            "peak_abs": (_round(max((abs(value) for value in output
                                     if math.isfinite(value)), default=0.0))
                         if output is not None else None),
        },
        "iteration_trace": trace,
        "projection_metadata": metadata,
        "scoring": {"status": "not_applicable"},
    }
    if output is not None:
        result["output"]["samples"] = output
        finite_output = all(math.isfinite(value) for value in output)
        result["output"]["finite_count"] = (len(output) if finite_output else
                                            len(output) - result["output"]["nonfinite_count"])
        if clean is not None:
            indices = [index for index, bad in enumerate(mask) if bad]
            result["scoring"] = {
                "status": "ok",
                "clean_reference_sha256": result["input"]["clean_sha256"],
                "si_sdr_db": _round(reference.si_sdr_db(clean, output), 6),
                "rmse": _round(reference.rmse(clean, output), 9),
                "damaged_region_rmse": _round(reference.rmse(clean, output, indices), 9),
                "damaged_region_samples": len(indices),
                "max_abs_diff": _round(reference.max_abs_diff(clean, output), 9),
            }
    else:
        result["output"]["preview"] = [
            None if not math.isfinite(value) else value for value in samples[:16]
        ]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    try:
        request = read_json(args.request)
        if not isinstance(request, dict) or request.get("operation") not in ("inspect", "run"):
            raise RequestError("unknown_operation")
        result = inspect(request) if request["operation"] == "inspect" else run(request)
        path = Path(args.result)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_bytes(canonical_bytes(result))
        os.replace(temp, path)
    except (RequestError, reference.ControlError, ValueError, KeyError, TypeError) as error:
        print(str(error) or error.__class__.__name__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
