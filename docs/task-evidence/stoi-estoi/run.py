# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in, unregistered developer adapter and canonical report regeneration.

This is a protocol-v1-shaped evidence adapter only.  It is not an SDK provider,
not registered anywhere, not default-enabled, not an audio-bench metric and
produces no Bench bundle.  ``run.py --report`` regenerates the frozen canonical
report byte-identically; ``--request/--result`` exercises the same boundary on
one item/variant at a time.  No adapter result qualifies a processor.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import fixture
import reference
import scorer

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
IDENTITY = "stoi-estoi-evidence-v1"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"item_id", "variant", "samples"}
VALID_VARIANTS = tuple(fixture.VARIANTS)


class RequestError(ValueError):
    pass


def read_json(path: Path) -> Dict[str, Any]:
    return reference.read_strict_json(path)


def validate_ref(value: Any, name: str) -> None:
    if (not isinstance(value, dict) or set(value) != {"kind", "id", "revision"}
            or not isinstance(value["id"], str) or not value["id"]
            or isinstance(value["revision"], bool)
            or not isinstance(value["revision"], int) or value["revision"] < 1):
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
    if not isinstance(config, dict) or set(config) != {"metric_set"}:
        raise RequestError("invalid_configuration")
    if config["metric_set"] != "stoi_estoi_pinned":
        raise RequestError("unknown_metric_set")
    if operation == "inspect":
        return config
    if (not isinstance(request["item_id"], str) or not request["item_id"]
            or request["item_id"] not in {item["item_id"] for item in fixture.cohort()[0]}):
        raise RequestError("unknown_item")
    if request["variant"] not in VALID_VARIANTS:
        raise RequestError("unknown_variant")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or len(samples) != fixture.SAMPLES
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       or not math.isfinite(value) for value in samples)):
            raise RequestError("invalid_samples")
    return config


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": config,
        "supported_items": [
            item["item_id"] for item in fixture.cohort()[0]
        ],
        "supported_variants": list(VALID_VARIANTS),
        "supported_metrics": list(reference.METRICS),
        "scorer_id": scorer.SCORER_ID,
        "pystoi_version": scorer.PYSTOI_VERSION,
        "registration": "unregistered developer-only fixture; no SDK default or Bench result",
        "expose_as_processor": False,
        "promotion": "defer",
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    clean = fixture.target()
    items, _ = fixture.cohort()
    item = next(row for row in items if row["item_id"] == request["item_id"])
    variant = request["variant"]
    if request["samples"] is None:
        row = item["variants"][variant]
    else:
        row = {
            "values": [float(value) for value in request["samples"]],
            "digest": fixture.digest(request["samples"]),
            "samples": len(request["samples"]),
        }
    scored = reference.score_variant(clean, row)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": config,
        "item_id": request["item_id"],
        "variant": variant,
        "status": scored["status"],
        "reason": scored["reason"],
        "metrics": scored["metrics"],
        "digest": scored["digest"],
        "expose_as_processor": False,
        "registered": False,
    }


def _request(operation: str, item_id: str = "", variant: str = "",
             samples: Optional[List[float]] = None) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "operation": operation,
        "candidate_ref": {"kind": "synthetic-item", "id": "stoi-estoi-cohort-v1", "revision": 1},
        "adapter_ref": {"kind": "developer-adapter", "id": IDENTITY, "revision": 1},
        "configuration": {"metric_set": "stoi_estoi_pinned"},
    }
    if operation == "run":
        request.update({"item_id": item_id, "variant": variant, "samples": samples})
    return request


def bundle_validation() -> Dict[str, Any]:
    """One representative valid result and one missing case through the adapter."""
    valid = run(_request("run", "steady-snr+0", "identity_noisy"))
    missing = run(_request("run", "steady-snr-5", "missing"))
    return {
        "representative_valid": valid,
        "missing_case": missing,
        "checks": {
            "valid_scored": valid["status"] == "scored" and valid["metrics"] is not None,
            "missing_blocked": missing["status"] == "blocked"
                               and missing["reason"] == "missing_input"
                               and missing["metrics"] is None,
            "inspect_is_dev_only": inspect(_request("inspect"))["expose_as_processor"] is False,
        },
    }


def generate_report() -> str:
    report = reference.build_report()
    validation = bundle_validation()
    if not all(validation["checks"].values()):
        raise ValueError("bundle_validation_failed")
    report["bundle_validation"] = validation
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
            request = read_json(options.request)
            result = inspect(request) if request.get("operation") == "inspect" else run(request)
        except (RequestError, ValueError) as error:
            print(str(error), file=sys.stderr)
            return 2
        options.result.write_text(json.dumps(result, sort_keys=True, separators=(",", ":"),
                                             allow_nan=False) + "\n", encoding="utf-8")
        return 0
    parser.error("select --report or --request/--result")


if __name__ == "__main__":
    sys.exit(main())
