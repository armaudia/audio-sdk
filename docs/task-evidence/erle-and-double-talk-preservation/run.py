# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in developer adapter and byte-identical canonical report regeneration.

No SDK provider, descriptor, registry entry, catalog submission or Bench bundle
is produced.  ``--report`` prints the canonical report bytes to stdout so the
checked-in artifact can be verified with ``cmp`` and SHA-256.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict

import fixture
import reference

ROOT = Path(__file__).resolve().parent
PROTOCOL_VERSION = 1
IDENTITY = "erle-and-double-talk-preservation-v1"
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref",
                 "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"condition"}


class RequestError(ValueError):
    pass


def read_json(path: Path) -> Dict[str, Any]:
    def pairs(items: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key")
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise RequestError("nonfinite_json_constant:" + token)

    data = json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(data, dict):
        raise RequestError("request_not_object")
    return data


def validate_ref(value: Any, name: str) -> None:
    if (not isinstance(value, dict) or set(value) != {"kind", "id", "revision"}
            or not isinstance(value["id"], str) or not value["id"]
            or isinstance(value["revision"], bool)
            or not isinstance(value["revision"], int) or value["revision"] < 1):
        raise RequestError("invalid_" + name)


def validate_request(request: Dict[str, Any], operation: str) -> Dict[str, Any]:
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if set(request) != required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], "candidate_ref")
    validate_ref(request["adapter_ref"], "adapter_ref")
    config = request["configuration"]
    if (not isinstance(config, dict) or set(config) != {"variant"}
            or config["variant"] not in reference.VARIANTS):
        raise RequestError("invalid_configuration")
    if operation == "run" and request["condition"] not in fixture.CONDITIONS:
        raise RequestError("unknown_condition")
    return config


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "identity": IDENTITY,
        "supported_conditions": list(fixture.CONDITIONS),
        "supported_variants": list(reference.VARIANTS),
        "supported_formats": ["mono 16 kHz float32, 160-sample frames"],
        "supported_tasks": ["duplex-erle-preservation-evidence"],
        "supported_modes": ["causal_framewise", "paired_render_reference"],
        "asset_readiness": [],
        "registration": "unregistered developer-only; no installed SDK provider",
        "processor_exposure": "none",
        "fixture_digest": fixture.fixture_digest(),
        "disclosure": "synthetic proposal-only evidence; not qualified for processor exposure",
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    data = fixture.fixture(request["condition"])
    # Mirror build_report(): cross-variant damage fields are attached only when
    # an identity control exists for that condition.
    identity_metrics = None
    if config["variant"] != "identity" and request["condition"] != "no_reference":
        identity_metrics = reference._result(data, "identity")["near_preservation"]
    result = reference._result(data, config["variant"], identity_metrics)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "identity": IDENTITY,
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "condition": request["condition"],
        "status": result["status"],
        "metrics": {
            "far_end_erle": result["far_end_erle"],
            "near_preservation": result["near_preservation"],
        },
        "qualifies": result["qualifies"],
        "missing_results": result["missing_results"],
        "output": result["output"],
        "disclosure": "synthetic-only developer result; no quality, device or release claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="write canonical report bytes to stdout")
    parser.add_argument("--request", type=Path, help="JSON request path")
    options = parser.parse_args()
    if options.report:
        if options.request:
            parser.error("--report and --request are mutually exclusive")
        sys.stdout.buffer.write(fixture.canonical_bytes(reference.build_report()))
        return 0
    if options.request is None:
        parser.error("one of --report or --request is required")
    try:
        request = read_json(options.request)
        operation = request.get("operation")
        response = inspect(request) if operation == "inspect" else run(request)
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.stderr.write("request_error: %s\n" % error)
        return 2
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":"),
                                allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
