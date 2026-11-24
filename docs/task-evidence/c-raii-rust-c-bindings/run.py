# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local report, source manifest, parity crosscheck and header.

Also exposes a small one-item request/result API for a typical developer use.
Nothing here registers a provider, changes installed behavior or qualifies a
candidate. Every generated artifact is deterministic and byte-repeatable.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

sys.dont_write_bytecode = True

import fixture
import reference
import scorer

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
REPORT_DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"
CROSSCHECK_PATH = ROOT / "crosscheck.json"
CROSSCHECK_DIGEST_PATH = ROOT / "crosscheck.json.sha256"
HEADER_PATH = ROOT / "c_boundary/raii_model.h"
HARNESS_OUTPUT_PATH = ROOT / "c_boundary/harness_output.json"
PROTOCOL_VERSION = 1
IDENTITY = "raii-model-evidence-v1"


class RequestError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_canonical(path: Path, digest_path: Path, value: Dict[str, Any]) -> str:
    text, digest = reference.canonical_json(value)
    path.write_bytes(text.encode("utf-8") + b"\n")
    digest_path.write_text(digest + "\n", encoding="ascii")
    return digest


def sources_text() -> str:
    lines: List[str] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or path.name == SOURCES_PATH.name:
            continue
        if "__pycache__" in path.parts:
            continue
        lines.append(sha256_bytes(path.read_bytes()) + "  " + path.relative_to(ROOT).as_posix())
    paths = reference.pin_paths()
    for pin in reference.PINS:
        pin_path = paths[pin["id"]]
        actual = sha256_bytes(pin_path.read_bytes())
        if actual != pin["sha256"]:
            raise ValueError("pin_digest_mismatch:" + pin["id"])
        lines.append("PIN  " + pin["sha256"] + "  " + pin["id"])
    return "\n".join(lines) + "\n"


def generate_sources() -> str:
    text = sources_text()
    SOURCES_PATH.write_text(text, encoding="ascii")
    return sha256_bytes(text.encode("utf-8"))


def generate_header() -> str:
    text = reference.generated_header()
    HEADER_PATH.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode("utf-8"))


def generate_crosscheck() -> str:
    observed = reference.read_strict_json(HARNESS_OUTPUT_PATH)
    expected = reference.model_cases()
    result = scorer.score_all(expected, observed.get("cases", []))
    summary = scorer.summary(result)
    if not summary["passed"]:
        raise ValueError("crosscheck_not_passing:" + ",".join(summary["failed_cases"]))
    payload = {
        "spdx": {
            "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
            "SPDX" "-License-Identifier": "Apache-2.0",
        },
        "protocol": reference.PROTOCOL,
        "task": reference.TASK,
        "base_commit": reference.BASE_COMMIT,
        "kind": "synthetic C harness parity crosscheck; not a workload or Rust build result",
        "expected_model_digest": reference.model_digest(expected),
        "harness_output_sha256": sha256_bytes(HARNESS_OUTPUT_PATH.read_bytes()),
        "result": result,
        "summary": summary,
        "decision": {
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
        },
    }
    return write_canonical(CROSSCHECK_PATH, CROSSCHECK_DIGEST_PATH, payload)


def validate_ref(value: Any, name: str) -> None:
    if (not isinstance(value, dict) or set(value) != {"kind", "id", "revision"}
            or not isinstance(value["kind"], str) or not value["kind"]
            or not isinstance(value["id"], str) or not value["id"]
            or isinstance(value["revision"], bool) or not isinstance(value["revision"], int)
            or value["revision"] < 1):
        raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    common = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
    expected = common | ({"case_id"} if operation == "run" else set())
    if set(request) != expected:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], "candidate_ref")
    validate_ref(request["adapter_ref"], "adapter_ref")
    configuration = request["configuration"]
    if configuration != {"profile": "tool"}:
        raise RequestError("invalid_configuration")
    if operation == "run":
        known = {case["case_id"] for case in fixture.cases()}
        if request["case_id"] not in known:
            raise RequestError("unknown_case")
    return request


def make_request(operation: str, case_id: str = "") -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "operation": operation,
        "candidate_ref": {"kind": "synthetic-fixture", "id": "c-raii-bindings-synthetic-v1", "revision": 1},
        "adapter_ref": {"kind": "developer-adapter", "id": IDENTITY, "revision": 1},
        "configuration": {"profile": "tool"},
    }
    if operation == "run":
        request["case_id"] = case_id
    return request


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "identity": IDENTITY,
        "fixture": fixture.fixture_pins(),
        "supported_case_ids": [case["case_id"] for case in fixture.cases()],
        "registration": "unregistered developer-only fixture",
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "promotion": "defer",
    }


def run_case(request: Dict[str, Any]) -> Dict[str, Any]:
    validate_request(request, "run")
    case = next(row for row in reference.model_cases() if row["case_id"] == request["case_id"])
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "identity": IDENTITY,
        "case": case,
        "status": "contract_model_only",
        "reason": None,
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
    }


def validate(request: Dict[str, Any]) -> Dict[str, Any]:
    validate_request(request, "validate")
    crosscheck = reference.read_strict_json(CROSSCHECK_PATH)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "validate",
        "identity": IDENTITY,
        "passed": crosscheck["summary"]["passed"],
        "case_count": crosscheck["summary"]["case_count"],
        "failed_cases": crosscheck["summary"]["failed_cases"],
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
    }


def bundle_validation() -> Dict[str, Any]:
    valid = run_case(make_request("run", "valid_full_frame"))
    malformed = run_case(make_request("run", "nonfinite_input"))
    missing = run_case(make_request("run", "missing_provider_selection"))
    inspect_result = inspect(make_request("inspect"))
    return {
        "representative_valid": valid["case"]["case_id"],
        "malformed": malformed["case"]["case_id"],
        "missing_optional": missing["case"]["case_id"],
        "checks": {
            "valid_status_ok": valid["case"]["expected_create_status"] == "OK"
                               and valid["case"]["expected_process_status"] == "OK",
            "malformed_rejected": malformed["case"]["expected_process_status"] == "INVALID_ARGUMENT",
            "missing_optional_rejected": missing["case"]["expected_create_status"] == "INVALID_ARGUMENT",
            "inspect_is_dev_only": inspect_result["expose_as_processor"] is False,
        },
    }


def generate_report() -> str:
    report = reference.build_report()
    report["bundle_validation"] = bundle_validation()
    if not all(report["bundle_validation"]["checks"].values()):
        raise ValueError("bundle_validation_failed")
    return write_canonical(REPORT_PATH, REPORT_DIGEST_PATH, report)


def dispatch(value: Dict[str, Any]) -> Dict[str, Any]:
    operation = value.get("operation")
    if operation == "inspect":
        return inspect(value)
    if operation == "run":
        return run_case(value)
    if operation == "validate":
        return validate(value)
    raise RequestError("unknown_operation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="regenerate report.json and its digest")
    parser.add_argument("--sources", action="store_true", help="regenerate SOURCES.sha256")
    parser.add_argument("--crosscheck", action="store_true", help="regenerate crosscheck.json and its digest")
    parser.add_argument("--emit-header", action="store_true", help="regenerate c_boundary/raii_model.h")
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    options = parser.parse_args()
    actions = (options.report, options.sources, options.crosscheck, options.emit_header,
               bool(options.request))
    if sum(bool(action) for action in actions) != 1:
        parser.error("select exactly one action")
    if bool(options.request) != bool(options.result):
        parser.error("--request and --result must be used together")
    try:
        if options.report:
            print(generate_report())
        elif options.sources:
            print(generate_sources())
        elif options.crosscheck:
            print(generate_crosscheck())
        elif options.emit_header:
            print(generate_header())
        else:
            request = reference.read_strict_json(options.request)
            result = dispatch(request)
            write_canonical(options.result, options.result.with_name(options.result.name + ".sha256"), result)
            print(reference.canonical_json(result)[1])
    except (OSError, ValueError, KeyError, TypeError, RequestError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
