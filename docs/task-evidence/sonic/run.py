# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in task-local adapter, canonical report and source-pin generator.

The adapter is protocol-shaped, unregistered and disabled by default. With
``provider_enabled=false`` it returns caller samples unchanged. Only an
explicit opt-in runs the deterministic synthetic Sonic-style reference. No C
provider, installed target, descriptor, registry or public ABI is involved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping

import fixture
import reference
import scorer

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"
CONTRACT_PATH = ROOT / "contract.json"
ADAPTER_PATH = ROOT / "adapter.json"
PROVIDER_PATH = ROOT / "provider.json"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref",
                 "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "rate", "samples"}
CONFIG_KEYS = {"provider_enabled", "stimulus_id"}
MAX_REQUEST_SAMPLES = 32768
SOURCE_ARTIFACT_NAMES = tuple(sorted(
    set(reference.ARTIFACT_FILES) | {
        "README.md", "adapter.json", "provider.json", "report.json",
        "report.json.sha256",
    }))


class RequestError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def strict_load(path: Path) -> Dict[str, Any]:
    def pairs(items: List[Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key")
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise RequestError("nonfinite_json_constant:" + token)

    payload = json.loads(path.read_text(encoding="utf-8"),
                         object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(payload, dict):
        raise RequestError("root_not_object")
    return payload


def _validate_ref(value: Any, name: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(value["id"], str) or not value["id"]:
        raise RequestError("invalid_" + name)
    if isinstance(value["revision"], bool) or not isinstance(value["revision"], int) \
            or value["revision"] < 1:
        raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, Mapping):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if set(request) != required:
        raise RequestError("invalid_request_fields")
    version = request["protocol_version"]
    if type(version) is not int or version != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    _validate_ref(request["candidate_ref"], "candidate_ref")
    _validate_ref(request["adapter_ref"], "adapter_ref")
    config = request["configuration"]
    if not isinstance(config, Mapping) or set(config) != CONFIG_KEYS:
        raise RequestError("invalid_configuration")
    if not isinstance(config["provider_enabled"], bool):
        raise RequestError("invalid_provider_switch")
    if config["stimulus_id"] is not None \
            and config["stimulus_id"] not in reference.FIXTURE_GENERATORS:
        raise RequestError("unknown_stimulus")
    if operation == "inspect":
        return dict(config)
    if not isinstance(request["attempt_id"], str) or not request["attempt_id"]:
        raise RequestError("invalid_attempt_id")
    return dict(config)


def inspect(request: Mapping[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "candidate_ref": dict(request["candidate_ref"]),
        "adapter_ref": dict(request["adapter_ref"]),
        "identity": reference.ADAPTER_ID,
        "configuration": config,
        "supported_rates": list(reference.RATES),
        "supported_fixtures": sorted(reference.FIXTURE_GENERATORS),
        "supported_tasks": [reference.TASK],
        "supported_formats": ["mono 16 kHz float32; 160-sample installed grid"],
        "installed_v0_unchanged": True,
        "real_time_v0_provider": False,
        "default_enabled": False,
        "registered": False,
        "public_c_boundary": "not used: task-local Python reference only",
        "disclosure": "synthetic proposal evidence; not a listening, device or release result",
    }


def run(request: Mapping[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    rate = reference.validate_rate(request["rate"])
    if config["stimulus_id"] is None and request["samples"] is None:
        raise RequestError("missing_stimulus")
    if request["samples"] is not None:
        raw = request["samples"]
        if (not isinstance(raw, list) or not raw
                or len(raw) > MAX_REQUEST_SAMPLES):
            raise RequestError("invalid_samples")
        samples = scorer.validate_vector(raw, "samples")
        source_label = "caller_supplied"
    else:
        samples = reference.FIXTURE_GENERATORS[config["stimulus_id"]]()
        source_label = config["stimulus_id"]
    if not config["provider_enabled"]:
        output = samples
        status = "complete"
        applied = "identity_provider_off"
    else:
        try:
            result = reference.stretch(samples, rate)
        except (scorer.ScorerError, reference.ConfigError) as error:
            return {
                "protocol_version": PROTOCOL_VERSION,
                "operation": "run",
                "attempt_id": request["attempt_id"],
                "status": "rejected",
                "errors": [str(error)],
                "metrics": None,
                "output": None,
                "disclosure": "synthetic failure control; no result qualifies a candidate",
            }
        output = result["samples"]
        status = "complete"
        applied = "pitch_synchronous_ola_reference"
    metrics: Dict[str, Any] = {
        "source_samples": len(samples),
        "output_samples": len(output),
        "source_digest": scorer.tensor_digest(samples),
        "output_digest": scorer.tensor_digest(output),
        "nonfinite_count": scorer.nonfinite_count(output),
        "peak_abs": scorer.r6(scorer.peak_abs(output)),
    }
    if config["provider_enabled"]:
        metrics["duration"] = scorer.duration_metrics(len(samples), len(output), rate)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": dict(request["candidate_ref"]),
        "adapter_ref": dict(request["adapter_ref"]),
        "configuration": config,
        "stimulus": source_label,
        "provider_enabled": config["provider_enabled"],
        "applied_control": applied,
        "status": status,
        "errors": [],
        "metrics": metrics,
        "disclosure": ("synthetic-only developer result; opt-in unregistered "
                       "task-local reference, not a Bench bundle, listening "
                       "score, quality claim or release gate"),
    }


def process_file(request_path: Path, result_path: Path) -> Dict[str, Any]:
    request = strict_load(request_path)
    operation = request.get("operation")
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
    text, canonical_digest = reference.canonical_report(report)
    payload = text.encode("utf-8") + b"\n"
    REPORT_PATH.write_bytes(payload)
    file_digest = hashlib.sha256(payload).hexdigest()
    DIGEST_PATH.write_text(file_digest + "\n", encoding="ascii", newline="\n")
    print("canonical_digest=" + canonical_digest)
    print("report_file_digest=" + file_digest)
    return file_digest


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adapter_manifest() -> Dict[str, Any]:
    return {
        "adapter_id": reference.ADAPTER_ID,
        "protocol_version": PROTOCOL_VERSION,
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "registered": False,
        "default_enabled": False,
        "real_time_v0_provider": False,
        "public_c_boundary_used": False,
        "supported_operations": ["inspect", "run"],
        "supported_rates": list(reference.RATES),
        "supported_fixtures": sorted(reference.FIXTURE_GENERATORS),
        "installed_v0_unchanged": True,
        "registration": "unregistered developer-only reference; no SDK default, registry or Bench result",
        "disclosure": "synthetic-only; no listening, device timing, real corpus or release claim",
    }


def provider_manifest() -> Dict[str, Any]:
    return {
        "provider_id": reference.PROVIDER_ID,
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "implementation": "task-local Python pitch-synchronous OLA reference",
        "enabled_by_default": False,
        "opt_in_required": True,
        "registered": False,
        "descriptor_registration": False,
        "descriptor_settings": {},
        "public_abi_change": False,
        "sdk_default_change": False,
        "installed_v0_behavior_change": False,
        "required_assets": [],
        "format": {
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": reference.FRAME_SAMPLES,
        },
        "integration_status": "deferred_until_independent_review",
        "disclosure": "opt-in proposal manifest only; no installed provider is built, linked or exposed",
    }


def contract_manifest() -> Dict[str, Any]:
    report = strict_load(REPORT_PATH)
    _text, canonical_digest = reference.canonical_report(report)
    return {
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "contract_version": "0.1",
        "base_commit": reference.BASE_COMMIT,
        "rebase_base_commit": reference.REBASE_BASE_COMMIT,
        "branch": reference.BRANCH,
        "profile": {"name": "rate", "source": report["profile"]["source"]},
        "source_pins": reference.SOURCE_PINS,
        "boundary_pins": reference.BOUNDARY_PINS,
        "board_snapshot": reference.BOARD_SNAPSHOT,
        "boundary": report["boundary"],
        "artifact_pins": {name: _sha256_file(ROOT / name)
                          for name in SOURCE_ARTIFACT_NAMES},
        "canonical_report": {
            "canonical_digest": canonical_digest,
            "file_sha256": _sha256_file(REPORT_PATH),
            "sidecar_sha256": _sha256_file(DIGEST_PATH),
            "format": ("canonical JSON: sort_keys=True, compact separators, "
                       "allow_nan=False, one trailing newline"),
        },
        "invariants": list(report["non_claims"]),
        "qualification": report["qualification"],
        "decision": "DEFER",
    }


def generate_sources() -> str:
    adapter = adapter_manifest()
    provider = provider_manifest()
    ADAPTER_PATH.write_bytes(canonical_bytes(adapter) + b"\n")
    PROVIDER_PATH.write_bytes(canonical_bytes(provider) + b"\n")
    contract = contract_manifest()
    CONTRACT_PATH.write_bytes(canonical_bytes(contract) + b"\n")
    rows: List[str] = [
        "# SHA-256 pins for SDK-SONIC; source: paths are workspace-relative, "
        "others SDK-worktree-relative.\n",
        "# board snapshot (mutable, provenance only): "
        + reference.BOARD_SNAPSHOT["sha256_at_read"] + " "
        + reference.BOARD_SNAPSHOT["path"] + "\n",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        rows.append(digest + "  source:" + path + "\n")
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        rows.append(digest + "  " + path + "\n")
    names = sorted(set(SOURCE_ARTIFACT_NAMES) | {"contract.json"})
    for name in names:
        rows.append(_sha256_file(ROOT / name) + "  "
                    + reference.TASK_PREFIX + name + "\n")
    payload_text = "".join(rows)
    SOURCES_PATH.write_text(payload_text, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    print("sources_manifest_digest=" + digest)
    return digest


def crosscheck() -> Dict[str, Any]:
    first = fixture.canonical_report_bytes(reference.build_report())
    second = fixture.canonical_report_bytes(reference.build_report())
    cases = [reference.crosscheck_stretch(reference.tonal(), rate)
             for rate in reference.RATES]
    result = {
        "report_byte_identical": first == second,
        "report_sha256": hashlib.sha256(first).hexdigest(),
        "cases": cases,
        "all_renderers_byte_identical": all(case["byte_identical"] for case in cases),
    }
    print("report_sha256=" + result["report_sha256"])
    for case in cases:
        print("rate=" + str(case["rate"]) + " digest=" + case["independent_digest"]
              + " primary_digest=" + case["primary_digest"]
              + " byte_identical=" + str(case["byte_identical"]))
    if not result["report_byte_identical"] or not result["all_renderers_byte_identical"]:
        raise SystemExit(1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json and its SHA-256 sidecar")
    parser.add_argument("--sources", action="store_true",
                        help="regenerate manifests and SOURCES.sha256")
    parser.add_argument("--crosscheck", action="store_true",
                        help="compare independent OLA renderers and report regeneration")
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    options = parser.parse_args()
    generation_flags = sum(bool(value) for value in (
        options.report, options.sources, options.crosscheck))
    if options.request or options.result:
        if not (options.request and options.result):
            parser.error("--request and --result must be used together")
        if generation_flags:
            parser.error("--request cannot be combined with generation flags")
    elif generation_flags != 1:
        parser.error("select exactly one of --report, --sources, --crosscheck or --request/--result")
    if options.report:
        generate_report()
        return 0
    if options.sources:
        generate_sources()
        return 0
    if options.crosscheck:
        crosscheck()
        return 0
    try:
        process_file(options.request, options.result)
    except (RequestError, scorer.ScorerError, reference.ConfigError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
