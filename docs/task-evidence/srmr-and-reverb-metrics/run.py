# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local opt-in adapter protocol and canonical report regeneration.

The adapter is unregistered, disabled by default and has no public API, ABI,
descriptor, default or provider-registration effect. It exposes only SRMR and
a synthetic RIR C50-style proxy for developer evidence; it is not a processor.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import reference
import scorer

PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "adapter_ref", "configuration"}
SCORE_FIELDS = COMMON_FIELDS | {"case_id", "samples"}
MAX_REQUEST_SAMPLES = 65536
REPORT_PATH = reference.REPORT_FILE
DIGEST_PATH = reference.SIDECAR_FILE


class RequestError(ValueError):
    pass


def _pairs(items: List[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise RequestError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise RequestError("nonfinite_json_constant:" + token)


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"),
                         object_pairs_hook=_pairs, parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise RequestError("request_not_object")
    return payload


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def validate_ref(value: Any) -> None:
    if (not isinstance(value, dict) or set(value) != {"kind", "id", "revision"}
            or not isinstance(value["kind"], str) or not value["kind"]
            or not isinstance(value["id"], str) or not value["id"]
            or isinstance(value["revision"], bool)
            or not isinstance(value["revision"], int) or value["revision"] < 1):
        raise RequestError("invalid_adapter_ref")


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else SCORE_FIELDS
    if set(request) != required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["adapter_ref"])
    config = request["configuration"]
    expected_config = ({"opt_in"} if operation == "inspect"
                       else {"opt_in", "sample_rate_hz"})
    if not isinstance(config, dict) or set(config) != expected_config:
        raise RequestError("invalid_configuration")
    if config["opt_in"] is not True:
        raise RequestError("adapter_not_opted_in")
    if operation == "inspect":
        return config
    if (isinstance(config["sample_rate_hz"], bool)
            or config["sample_rate_hz"] != scorer.SAMPLE_RATE_HZ):
        raise RequestError("unsupported_sample_rate")
    if not isinstance(request["case_id"], str) or not request["case_id"]:
        raise RequestError("invalid_case_id")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or not samples
                or len(samples) > MAX_REQUEST_SAMPLES
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       for value in samples)
                or any(not math.isfinite(float(value)) for value in samples)):
            raise RequestError("invalid_samples")
    return config


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "identity": reference.CONTRACT_ID,
        "default_enabled": False,
        "opt_in_required": True,
        "registration": "unregistered-developer-only",
        "operations": ["inspect", "score"],
        "supported_sample_rate_hz": scorer.SAMPLE_RATE_HZ,
        "supported_metrics": ["srmr", "c50_early_to_late_db_proxy"],
        "fixture_cases": ["dry_source"] + [
            name + suffix for name in reference.ROOM_SPECS
            for suffix in ("_input", "_early_target")
        ],
        "public_api_abi_changed": False,
        "processor_exposure": False,
        "disclosure": "synthetic evidence only; no processor, quality or release claim",
    }


def score(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "score")
    case_id = request["case_id"]
    if request["samples"] is None:
        try:
            samples = reference.fixture_samples(case_id)
        except reference.RequestError:
            return {
                "protocol_version": PROTOCOL_VERSION,
                "operation": "score",
                "adapter_ref": request["adapter_ref"],
                "configuration": config,
                "case_id": case_id,
                "status": "rejected",
                "reason": "unknown_fixture_case",
                "score": None,
                "input_f32_sha256": None,
                "disclosure": "no score; invalid or missing fixture is never a result",
            }
    else:
        samples = [float(value) for value in request["samples"]]
    value, reason = scorer.srmr(samples, config["sample_rate_hz"])
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "score",
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "case_id": case_id,
        "status": "scored" if reason is None else "rejected",
        "reason": reason,
        "score": value,
        "input_f32_sha256": reference.tensor_digest(samples),
        "sample_count": len(samples),
        "disclosure": (
            "synthetic evidence only; opt-in unregistered adapter, not a "
            "processor, quality claim, listening result or release gate"
        ),
    }


def process_file(request_path: Path, result_path: Path) -> Dict[str, Any]:
    request = read_json(request_path)
    operation = request.get("operation")
    if operation == "inspect":
        result = inspect(request)
    elif operation == "score":
        result = score(request)
    else:
        raise RequestError("unsupported_operation")
    result_path.write_bytes(canonical_bytes(result) + b"\n")
    return result


def build_report_bytes() -> Tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("utf-8") + b"\n", digest


def generate_report(report_path: Optional[Path] = None,
                    digest_path: Optional[Path] = None) -> str:
    payload, digest = build_report_bytes()
    (report_path or REPORT_PATH).write_bytes(payload)
    (digest_path or DIGEST_PATH).write_text(digest + "\n", encoding="ascii")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json and its SHA-256 sidecar")
    options = parser.parse_args()
    if options.report:
        print(generate_report())
        return 0
    if bool(options.request) != bool(options.result):
        parser.error("--request and --result must be used together")
    if options.request:
        try:
            process_file(options.request, options.result)
        except (RequestError, OSError, ValueError) as error:
            print(str(error), file=sys.stderr)
            return 2
        return 0
    parser.error("select --report or --request/--result")


if __name__ == "__main__":
    sys.exit(main())
