# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local adapter, deterministic report/crosscheck/source regeneration.

This is an opt-in developer boundary.  It is not an SDK provider, is not
registered in any catalog and produces no Bench bundle or result qualification.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import reference
import scorer

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"
CROSSCHECK_PATH = ROOT / "crosscheck_vectors.json"
IDENTITY = "learned-inverse-eq-reference-v1"
PROTOCOL_VERSION = 1
CONTROLS = ("identity", "fixed_eq", "learned_inverse")
STIMULI = ("impulse", "silence", "clean_speech_perturbed")
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples"}


class RequestError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (scorer.canonical_text(value) + "\n").encode("utf-8")


def validate_ref(value: Any, name: str) -> None:
    if (not isinstance(value, dict) or set(value) != {"kind", "id", "revision"}
            or not isinstance(value.get("id"), str) or not value["id"]
            or not isinstance(value.get("kind"), str) or not value["kind"]
            or isinstance(value.get("revision"), bool)
            or not isinstance(value.get("revision"), int) or value["revision"] < 1):
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
    if not isinstance(config, dict) or set(config) != {"control"}:
        raise RequestError("invalid_configuration")
    if config["control"] not in CONTROLS:
        raise RequestError("unknown_control")
    if operation == "inspect":
        return config
    if (not isinstance(request["attempt_id"], str) or not request["attempt_id"]
            or not isinstance(request["stimulus_id"], str)):
        raise RequestError("invalid_run_identity")
    if request["stimulus_id"] not in STIMULI and request["samples"] is None:
        raise RequestError("unknown_stimulus")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or not samples
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       for value in samples)):
            raise RequestError("invalid_samples")
    return config


def fixture_samples(name: str) -> tuple:
    import fixture
    cohort = fixture.cohort()
    if name == "impulse":
        return cohort["impulse"][:reference.FRAME_SAMPLES * 4]
    if name == "silence":
        return (0.0,) * (reference.FRAME_SAMPLES * 4)
    return cohort["clean_speech_perturbed"][:reference.FRAME_SAMPLES * 4]


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": config,
        "supported_controls": list(CONTROLS),
        "supported_fixtures": list(STIMULI),
        "supported_tasks": ["CLN-10"],
        "supported_modes": ["offline", "causal_framewise"],
        "supported_formats": ["mono 16 kHz float32, 160-sample frames"],
        "asset_readiness": [],
        "registration": "unregistered developer-only evidence; no SDK default or Bench result",
        "public_c_boundary": "not included in this task-local Python-only package",
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    samples = (tuple(float(value) for value in request["samples"])
               if request["samples"] is not None
               else fixture_samples(request["stimulus_id"]))
    model = reference.learned_model()
    gains = model["estimated_inverse_gains_db"] if config["control"] == "learned_inverse" else None
    result = reference.stream(samples, config["control"], gains_db=gains)
    output = result["output"]
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "stimulus_id": request["stimulus_id"],
        "status": result["status"],
        "errors": result["errors"],
        "output": {
            "sample_count": len(output),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": reference.CHANNELS,
            "byte_count": len(output) * 4,
            "samples_sha256": scorer.digest_json([scorer.round_float(v, 12) for v in output]),
            "finite_count": scorer.finite_count(output),
            "nonfinite_count": len(output) - scorer.finite_count(output),
            "peak_abs": scorer.round_float(scorer.peak(output), 12),
            "delay_samples": scorer.delay_samples(samples, output),
            "frame_statuses": result["statuses"],
            "state_digest": result["state_digest"],
        },
        "disclosure": "synthetic-only developer result; not a Bench bundle, quality claim or gate",
    }


def process_file(request_path: Path, result_path: Path) -> Dict[str, Any]:
    request = scorer.read_strict_json(request_path)
    operation = request.get("operation") if isinstance(request, dict) else None
    if operation == "inspect":
        result = inspect(request)
    elif operation == "run":
        result = run(request)
    else:
        raise RequestError("unsupported_operation")
    result_path.write_bytes(canonical_bytes(result))
    return result


def generate_crosscheck() -> str:
    vector = reference.crosscheck_vectors()
    CROSSCHECK_PATH.write_bytes(canonical_bytes(vector))
    return vector["sha256"]


def report_with_pins() -> Dict[str, Any]:
    report = reference.build_report()
    report["crosscheck"]["file_sha256_at_build"] = scorer.digest_bytes(
        CROSSCHECK_PATH.read_bytes())
    return report


def generate_report() -> str:
    report = report_with_pins()
    text, digest = reference.canonical_report(report)
    REPORT_PATH.write_bytes(text.encode("utf-8") + b"\n")
    DIGEST_PATH.write_text(digest + "\n", encoding="ascii", newline="\n")
    return digest


def generate_sources() -> str:
    rows: List[str] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == SOURCES_PATH.name:
            continue
        rows.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + relative + "\n")
    payload = "".join(rows)
    SOURCES_PATH.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json and report.json.sha256")
    parser.add_argument("--sources", action="store_true", help="regenerate SOURCES.sha256")
    parser.add_argument("--crosscheck", action="store_true",
                        help="regenerate crosscheck_vectors.json")
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    options = parser.parse_args()
    selected = sum(bool(value) for value in (options.report, options.sources,
                                             options.crosscheck, options.request))
    if selected != 1 and not (options.request and options.result):
        parser.error("select exactly one generation mode or --request with --result")
    if options.report:
        print(generate_report())
        return 0
    if options.sources:
        print(generate_sources())
        return 0
    if options.crosscheck:
        print(generate_crosscheck())
        return 0
    if bool(options.request) != bool(options.result):
        parser.error("--request and --result must be used together")
    try:
        process_file(options.request, options.result)
    except (RequestError, scorer.StrictJSONError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
