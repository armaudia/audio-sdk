# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in, unregistered task-local adapter and canonical report regeneration.

This is a protocol-v1-shaped evidence adapter: it is not an SDK provider, not
registered, not default-enabled and produces no installed-behavior change.
``--report`` rewrites ``report.json`` and its digest byte-identically;
``--sources`` prints the pinned SHA-256 manifest. No adapter result qualifies
a processor or a release.
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
SOURCES_PATH = ROOT / "SOURCES.sha256"
IDENTITY = reference.ADAPTER_ID
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"item_id", "variant", "samples"}
VALID_VARIANTS = set(reference.PROCESS_VARIANTS)


class RequestError(ValueError):
    pass


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
    if set(request) != required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], "candidate_ref")
    validate_ref(request["adapter_ref"], "adapter_ref")
    config = request["configuration"]
    if (not isinstance(config, dict) or set(config) != {"profile"}
            or config["profile"] != reference.TASK_ID):
        raise RequestError("invalid_configuration")
    if operation == "inspect":
        return config
    items, _ = fixture.cohort()
    item_ids = {str(item["item_id"]) for item in items}
    if not isinstance(request["item_id"], str) or request["item_id"] not in item_ids:
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
        "identity": IDENTITY,
        "configuration": config,
        "supported_variants": list(reference.PROCESS_VARIANTS),
        "supported_metrics": [scorer.SCORER_ID],
        "candidate": reference.CANDIDATE_VARIANT,
        "baseline": reference.BASELINE_VARIANT,
        "control": reference.CONTROL_VARIANT,
        "registration": "unregistered developer-only synthetic evidence",
        "expose_as_processor": False,
        "promotion": "DEFER",
        "installed_behavior": "unchanged",
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    items, _ = fixture.cohort()
    item = next(row for row in items if row["item_id"] == request["item_id"])
    variant = request["variant"]
    samples = request["samples"]
    rendered = reference.render(variant, samples)
    scored = reference.score_variant(item["clean"], item["noisy"], rendered)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "identity": IDENTITY,
        "configuration": config,
        "item_id": request["item_id"],
        "variant": variant,
        "status": scored["status"],
        "reason": scored["reason"],
        "metrics": scored["metrics"],
        "digest": rendered["digest"],
        "expose_as_processor": False,
        "registered": False,
    }


def _request(operation: str, item_id: str = "", variant: str = reference.CANDIDATE_VARIANT,
             samples: Optional[List[float]] = None) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "operation": operation,
        "candidate_ref": {"kind": "synthetic-candidate", "id": "webrtc-apm-ns-synthetic-v1", "revision": 1},
        "adapter_ref": {"kind": "developer-adapter", "id": IDENTITY, "revision": 1},
        "configuration": {"profile": reference.TASK_ID},
    }
    if operation == "run":
        request.update({"item_id": item_id, "variant": variant, "samples": samples})
    return request


def bundle_validation() -> Dict[str, Any]:
    """One representative valid result plus explicit missing/invalid controls."""
    items, _ = fixture.cohort()
    valid_request = _request("run", str(items[0]["item_id"]), reference.CANDIDATE_VARIANT,
                             list(items[0]["noisy"]))
    valid = run(valid_request)
    missing = run(_request("run", str(items[0]["item_id"]), reference.CANDIDATE_VARIANT, None))
    try:
        run(_request("run", str(items[0]["item_id"]), reference.CANDIDATE_VARIANT,
                     [float("nan")] + [0.0] * (fixture.SAMPLES - 1)))
        invalid_rejected = False
    except RequestError:
        invalid_rejected = True
    control = run(_request("run", str(items[0]["item_id"]), reference.CONTROL_VARIANT,
                           list(items[0]["noisy"])))
    checks = {
        "representative_valid_scored": valid["status"] == "scored" and valid["metrics"] is not None,
        "missing_case_blocked": missing["status"] == "blocked" and missing["metrics"] is None,
        "invalid_samples_rejected": invalid_rejected,
        "identity_control_bit_exact": control["digest"] == reference.digest_values(items[0]["noisy"]),
        "inspect_is_dev_only": inspect(_request("inspect"))["expose_as_processor"] is False,
    }
    return {
        "representative_valid": valid,
        "missing_case": missing,
        "invalid_case": {"status": "rejected_invalid_samples", "metrics": None},
        "identity_control": {"status": control["status"], "digest": control["digest"]},
        "checks": checks,
        "all_explicit": all(checks.values()),
    }


def source_manifest() -> str:
    lines: List[str] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or path == SOURCES_PATH or "__pycache__" in path.parts:
            continue
        lines.append(reference.digest_file(path) + "  " + path.relative_to(ROOT).as_posix())
    return "\n".join(lines) + "\n"


def generate_report() -> str:
    report = reference.build_report()
    validation = bundle_validation()
    if not validation["all_explicit"]:
        raise ValueError("bundle_validation_failed")
    report["bundle_validation"] = validation
    text, digest = reference.canonical_report(report)
    REPORT_PATH.write_bytes(text.encode("utf-8") + b"\n")
    DIGEST_PATH.write_text(digest + "\n", encoding="ascii")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="regenerate canonical report.json and digest")
    parser.add_argument("--sources", action="store_true", help="print the SHA-256 manifest of package files")
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    options = parser.parse_args()
    selected = sum(bool(value) for value in (options.report, options.sources, options.request))
    if selected != 1 or (options.result and not options.request):
        parser.error("choose exactly one of --report, --sources or --request/--result")
    if options.report:
        print(generate_report())
        return 0
    if options.sources:
        sys.stdout.write(source_manifest())
        return 0
    try:
        request = reference.read_strict_json(options.request)
        result = inspect(request) if request.get("operation") == "inspect" else run(request)
    except (RequestError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2
    options.result.write_text(json.dumps(result, sort_keys=True, separators=(",", ":"),
                                         allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
