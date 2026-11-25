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
CANDIDATE_REF = {"kind": "synthetic-candidate", "id": "webrtc-apm-ns-synthetic-v1", "revision": 1}
ADAPTER_REF = {"kind": "developer-adapter", "id": IDENTITY, "revision": 1}


class RequestError(ValueError):
    pass


def validate_ref(value: Any, expected: Dict[str, Any], name: str) -> None:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise RequestError("invalid_" + name)
    for key, wanted in expected.items():
        got = value[key]
        if type(got) is not type(wanted) or got != wanted:
            raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if set(request) != required:
        raise RequestError("invalid_request_fields")
    if (type(request["protocol_version"]) is not int or request["protocol_version"] != PROTOCOL_VERSION
            or request["operation"] != operation):
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], CANDIDATE_REF, "candidate_ref")
    validate_ref(request["adapter_ref"], ADAPTER_REF, "adapter_ref")
    config = request["configuration"]
    if (not isinstance(config, dict) or set(config) != {"profile"}
            or config["profile"] != reference.TASK_ID):
        raise RequestError("invalid_configuration")
    if operation == "inspect":
        return config
    item_id = request["item_id"]
    if not isinstance(item_id, str) or item_id not in fixture.NOISY_DIGESTS:
        raise RequestError("unknown_item")
    variant = request["variant"]
    if not isinstance(variant, str) or variant not in VALID_VARIANTS:
        raise RequestError("unknown_variant")
    samples = request["samples"]
    if samples is not None:
        # A caller's vector must be the frozen noisy vector of the selected
        # condition; otherwise paired scoring could mix two fixtures.
        try:
            valid_samples = (isinstance(samples, list) and len(samples) == fixture.SAMPLES
                             and all(type(value) in (int, float) and math.isfinite(value)
                                     for value in samples))
            matches = valid_samples and fixture.digest(samples) == fixture.NOISY_DIGESTS[item_id]
        except OverflowError:
            raise RequestError("invalid_samples") from None
        if not valid_samples:
            raise RequestError("invalid_samples")
        if not matches:
            raise RequestError("sample_digest_mismatch")
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
        "candidate_ref": dict(CANDIDATE_REF),
        "adapter_ref": dict(ADAPTER_REF),
        "configuration": {"profile": reference.TASK_ID},
    }
    if operation == "run":
        request.update({"item_id": item_id, "variant": variant, "samples": samples})
    return request


def bundle_validation() -> Dict[str, Any]:
    """One representative valid result plus explicit missing and rejection controls."""
    items, _ = fixture.cohort()
    valid_request = _request("run", str(items[0]["item_id"]), reference.CANDIDATE_VARIANT,
                             list(items[0]["noisy"]))
    valid = run(valid_request)
    missing = run(_request("run", str(items[0]["item_id"]), reference.CANDIDATE_VARIANT, None))
    def rejection(samples: List[float]) -> Dict[str, Any]:
        try:
            run(dict(valid_request, samples=samples))
        except RequestError as error:
            return {"status": "rejected_" + str(error), "metrics": None}
        raise ValueError("expected_bundle_rejection")

    invalid = rejection([float("nan")] + [0.0] * (fixture.SAMPLES - 1))
    mismatch = rejection(list(items[1]["noisy"]))
    control = run(_request("run", str(items[0]["item_id"]), reference.CONTROL_VARIANT,
                           list(items[0]["noisy"])))
    checks = {
        "representative_valid_scored": valid["status"] == "scored" and valid["metrics"] is not None,
        "missing_case_blocked": missing["status"] == "blocked" and missing["metrics"] is None,
        "invalid_samples_rejected": invalid["status"] == "rejected_invalid_samples",
        "mismatched_fixture_rejected": mismatch["status"] == "rejected_sample_digest_mismatch",
        "identity_control_bit_exact": control["digest"] == reference.digest_values(items[0]["noisy"]),
        "inspect_is_dev_only": inspect(_request("inspect"))["expose_as_processor"] is False,
    }
    return {
        "representative_valid": valid,
        "missing_case": missing,
        "invalid_case": invalid,
        "mismatched_fixture_case": mismatch,
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
    if selected != 1 or bool(options.result) != bool(options.request):
        parser.error("choose exactly one of --report, --sources or --request/--result")
    if options.report:
        print(generate_report())
        return 0
    if options.sources:
        sys.stdout.write(source_manifest())
        return 0
    try:
        request = reference.read_strict_json(options.request)
        if not isinstance(request, dict):
            raise RequestError("request_not_object")
        result = inspect(request) if request.get("operation") == "inspect" else run(request)
        options.result.write_text(json.dumps(result, sort_keys=True, separators=(",", ":"),
                                             allow_nan=False) + "\n", encoding="utf-8")
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
