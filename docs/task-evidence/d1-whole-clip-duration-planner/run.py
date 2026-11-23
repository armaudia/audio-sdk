"""Task-local protocol-v1-shaped boundary for the D1 whole-clip planner.

The envelope mirrors the public harness-controls adapter (inspect/run,
candidate_ref/adapter_ref revisions, strict JSON and a configuration object).
This adapter is unregistered, optional and developer-only. It is not an SDK
provider, descriptor, ABI, default or audio-bench bundle.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import fixtures
import reference

ROOT = Path(__file__).resolve().parent
ADAPTER_PATH = ROOT / "adapter.json"
IDENTITY = reference.IDENTITY
CONTROL = reference.CONTROL
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {
    "attempt_id", "session_id", "epoch", "scenario", "case_id", "variant",
    "adverse_id", "case_data",
}
SCENARIOS = ("case", "manual", "adverse")
CANDIDATE_REF = {"kind": "reference", "id": "rate.d1-whole-clip.ref", "revision": 1}
ADAPTER_REF = {"kind": "adapter", "id": IDENTITY, "revision": 1}
DEFAULT_CONFIG = {
    "control": CONTROL,
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "sdk_frame_samples": 160,
    "block_samples": 1600,
    "speech_floor": "4/5",
    "speech_ceiling": "1",
    "flex_ceiling": "3/2",
}

ADVERSE_IDS = (
    "missing_case_id", "unknown_case", "unknown_variant", "wrong_config_control",
    "wrong_sample_rate", "invalid_rate_bounds", "nonfinite_block_samples",
    "zero_block_samples", "noncontiguous_blocks", "unknown_label",
    "drift_unaligned", "drift_nonpositive_scale", "rebuffer_negative_gap",
    "rebuffer_unaligned", "overlapping_drift", "final_partial_oversize",
    "duplicate_json_key", "nonfinite_json_constant", "missing_required_request_field",
    "invalid_ref_revision", "oracle_infeasible_gap",
)


class RequestError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key:" + str(key))
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise RequestError("nonfinite_json_constant:" + token)

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


def validate_ref(ref: Any, name: str) -> None:
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise RequestError("invalid_" + name)
    if isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int) or ref["revision"] < 1:
        raise RequestError("invalid_" + name)


def adapter_descriptor() -> dict[str, Any]:
    document = read_json(ADAPTER_PATH)
    if document.get("identity") != IDENTITY:
        raise RequestError("unexpected_adapter_identity")
    return document


def validate_request(request: Any, operation: str) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS - {
        "case_id", "variant", "adverse_id", "case_data",
    }
    if not required <= set(request) or set(request) - (COMMON_FIELDS if operation == "inspect" else RUN_FIELDS):
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != 1 or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    for name in ("candidate_ref", "adapter_ref"):
        validate_ref(request[name], name)
    try:
        config = reference.validate_config(request["configuration"])
    except ValueError as error:
        raise RequestError(str(error)) from error
    if operation == "inspect":
        return config
    for name in ("attempt_id", "session_id"):
        if not isinstance(request[name], str) or not request[name]:
            raise RequestError("invalid_" + name)
    if isinstance(request["epoch"], bool) or not isinstance(request["epoch"], int) or request["epoch"] < 0:
        raise RequestError("invalid_epoch")
    if request["scenario"] not in SCENARIOS:
        raise RequestError("unknown_scenario")
    scenario = request["scenario"]
    if scenario == "case":
        if not isinstance(request.get("case_id"), str) or not request["case_id"] or \
                request.get("variant") not in reference.VARIANTS or \
                "adverse_id" in request or "case_data" in request:
            raise RequestError("invalid_case_selection")
    elif scenario == "manual":
        if "case_data" not in request or request.get("variant") not in reference.VARIANTS or \
                "case_id" in request or "adverse_id" in request:
            raise RequestError("invalid_manual_selection")
    else:
        if request.get("adverse_id") not in ADVERSE_IDS or \
                "case_id" in request or "variant" in request or "case_data" in request:
            raise RequestError("invalid_adverse_selection")
    return config


def inspect(request: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    descriptor = adapter_descriptor()
    return {
        "protocol_version": 1,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "boundary_identity": reference.BOUNDARY_IDENTITY,
        "descriptor_sha256": reference.sha256_hex(ADAPTER_PATH.read_bytes()),
        "configuration": {key: (reference.frac_json(value) if isinstance(value, type(reference.FLOOR))
                                else value) for key, value in config.items()},
        "supported_controls": [CONTROL],
        "supported_variants": list(reference.VARIANTS),
        "supported_scenarios": list(SCENARIOS),
        "supported_formats": ["16 kHz mono f32, 160-sample SDK frames, 1600-sample source blocks"],
        "buffering": dict(reference.BUFFERING_SEMANTICS),
        "asset_readiness": [],
        "registration": descriptor["registration"],
        "descriptor_summary": {
            key: descriptor[key] for key in (
                "protocol_version", "identity", "input_kind", "output_kinds",
                "modes", "entrypoint", "buffering", "weights", "registration",
                "boundary_source", "boundary_identity", "scope")
        },
        "candidate_qualified": False,
    }


def _select_case(request: dict[str, Any]) -> tuple[dict[str, Any], str, dict[str, Any]]:
    stimuli = fixtures.load_stimuli()
    case_id = request["case_id"]
    if case_id not in stimuli["cases"]:
        raise RequestError("unknown_case")
    variant = request["variant"]
    if variant not in stimuli["case_variants"][case_id]:
        raise RequestError("variant_not_declared_for_case")
    return stimuli["cases"][case_id], variant, stimuli


def _base_run_request(**overrides: Any) -> dict[str, Any]:
    request = {
        "protocol_version": 1,
        "operation": "run",
        "candidate_ref": dict(CANDIDATE_REF),
        "adapter_ref": dict(ADAPTER_REF),
        "configuration": dict(DEFAULT_CONFIG),
        "attempt_id": "adverse-control",
        "session_id": "adverse-session",
        "epoch": 1,
        "scenario": "case",
        "case_id": "identity_all_speech",
        "variant": "d1",
    }
    request.update(overrides)
    return request


def _manual_case(stimuli: dict[str, Any], case_id: str = "identity_all_speech") -> dict[str, Any]:
    return copy.deepcopy(stimuli["cases"][case_id])


def _adverse_thunks(stimuli: dict[str, Any]) -> dict[str, Any]:
    def duplicate_json_key() -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"protocol_version":1,"protocol_version":1}\n', encoding="utf-8")
            read_json(path)

    def nonfinite_json_constant() -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"value":NaN}\n', encoding="utf-8")
            read_json(path)

    def overlapping_drift() -> None:
        case = _manual_case(stimuli, "drift_interval")
        case["events"].append({
            "kind": "drift", "start_sample": 12 * reference.BLOCK_SAMPLES,
            "end_sample": 15 * reference.BLOCK_SAMPLES,
            "scale_num": 1, "scale_den": 1, "note": "overlap control",
        })
        reference.validate_case(case)

    def oracle_infeasible() -> None:
        case = stimuli["cases"]["oracle_infeasible_gap"]
        result = reference.evaluate_case(case, "oracle_compensated", DEFAULT_CONFIG)
        if result["oracle_compensation"]["feasible"] or result["candidate_qualified"]:
            raise ValueError("infeasible_oracle_qualified")
        if not result["profile_checks"]["source_output_mapping"]["union_equals_source"]:
            raise ValueError("infeasible_oracle_lost_source_mapping")

    return {
        "missing_case_id": lambda: validate_request(
            {key: value for key, value in _base_run_request().items() if key != "case_id"}, "run"),
        "unknown_case": lambda: _select_case(_base_run_request(case_id="no_such_case")),
        "unknown_variant": lambda: _select_case(_base_run_request(variant="no_such_variant")),
        "wrong_config_control": lambda: reference.validate_config(
            {**DEFAULT_CONFIG, "control": "other_control"}),
        "wrong_sample_rate": lambda: reference.validate_config(
            {**DEFAULT_CONFIG, "sample_rate_hz": 48000}),
        "invalid_rate_bounds": lambda: reference.validate_config(
            {**DEFAULT_CONFIG, "flex_ceiling": "2"}),
        "nonfinite_block_samples": lambda: reference.validate_case(
            _mutate_block(stimuli, lambda block: block.update(source_end_sample=float("nan")))),
        "zero_block_samples": lambda: reference.validate_case(
            _mutate_block(stimuli, lambda block: block.update(source_end_sample=block["source_first_sample"]))),
        "noncontiguous_blocks": lambda: reference.validate_case(
            _mutate_block(stimuli, lambda block: block.update(source_first_sample=block["source_first_sample"] + 1))),
        "unknown_label": lambda: reference.validate_case(
            _mutate_block(stimuli, lambda block: block.update(label="unknown"))),
        "drift_unaligned": lambda: reference.validate_case(
            _mutate_event(stimuli, "drift_interval", lambda event: event.update(start_sample=1))),
        "drift_nonpositive_scale": lambda: reference.validate_case(
            _mutate_event(stimuli, "drift_interval", lambda event: event.update(scale_den=0))),
        "rebuffer_negative_gap": lambda: reference.validate_case(
            _mutate_event(stimuli, "rebuffer_gap", lambda event: event.update(gap_ns=-1))),
        "rebuffer_unaligned": lambda: reference.validate_case(
            _mutate_event(stimuli, "rebuffer_gap", lambda event: event.update(at_sample=1))),
        "overlapping_drift": overlapping_drift,
        "final_partial_oversize": lambda: reference.validate_case(
            _oversize_final_block(stimuli)),
        "duplicate_json_key": duplicate_json_key,
        "nonfinite_json_constant": nonfinite_json_constant,
        "missing_required_request_field": lambda: validate_request(
            {key: value for key, value in _base_run_request().items() if key != "operation"}, "run"),
        "invalid_ref_revision": lambda: validate_request(
            _base_run_request(candidate_ref={"kind": "reference", "id": "x", "revision": 0}), "run"),
        "oracle_infeasible_gap": oracle_infeasible,
    }


def _mutate_block(stimuli: dict[str, Any], mutate: Any) -> dict[str, Any]:
    case = _manual_case(stimuli)
    mutate(case["blocks"][0])
    return case


def _mutate_event(stimuli: dict[str, Any], case_id: str, mutate: Any) -> dict[str, Any]:
    case = _manual_case(stimuli, case_id)
    mutate(case["events"][0])
    return case


def _oversize_final_block(stimuli: dict[str, Any]) -> dict[str, Any]:
    case = _manual_case(stimuli, "final_partial_window")
    case["blocks"][-1]["source_end_sample"] += reference.BLOCK_SAMPLES + 1
    return case


def adverse(adverse_id: str, config: dict[str, Any]) -> dict[str, Any]:
    stimuli = fixtures.load_stimuli()
    before = reference.sha256_hex(reference.canonical_bytes(stimuli["cases"]))
    thunks = _adverse_thunks(stimuli)
    if adverse_id not in thunks:
        raise RequestError("unknown_adverse_id")
    try:
        thunks[adverse_id]()
    except (RequestError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
        outcome = "reported_infeasible" if adverse_id == "oracle_infeasible_gap" else "rejected"
        reason = str(error)
    else:
        outcome = "unexpected_accept"
        reason = "control did not fail as required"
    after = reference.sha256_hex(reference.canonical_bytes(stimuli["cases"]))
    return {
        "id": adverse_id,
        "status": "observed",
        "outcome": outcome,
        "reason": reason,
        "fixture_unchanged": before == after,
        "fixture_digest": before,
        "candidate_qualified": False,
        "missing_result": False,
        "detail": {
            "scenario": "adverse",
            "offline_only": True,
            "oracle_infeasible_is_reported_not_qualified": adverse_id == "oracle_infeasible_gap",
        },
    }


def dispatch(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict) or request.get("operation") not in ("inspect", "run"):
        raise RequestError("unsupported_operation")
    config = validate_request(request, request["operation"])
    if request["operation"] == "inspect":
        return inspect(request, config)
    try:
        if request["scenario"] == "case":
            case, variant, _ = _select_case(request)
            result = reference.evaluate_case(case, variant, config)
        elif request["scenario"] == "manual":
            result = reference.evaluate_case(request["case_data"], request["variant"], config)
        else:
            result = adverse(request["adverse_id"], config)
    except (RequestError, ValueError, KeyError, TypeError) as error:
        result = {
            "status": "rejected",
            "reason": str(error),
            "candidate_qualified": False,
            "missing_result": False,
        }
    return {
        "protocol_version": 1,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "session_id": request["session_id"],
        "epoch": request["epoch"],
        "scenario": request["scenario"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "result": result,
        "errors": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, help="strict JSON request file")
    parser.add_argument("--result", required=True, help="canonical JSON result file")
    options = parser.parse_args()
    try:
        response = dispatch(read_json(Path(options.request)))
    except RequestError as error:
        raise SystemExit("request rejected: " + str(error)) from error
    payload = reference.canonical_bytes(response) + b"\n"
    target = Path(options.result).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    temp.write_bytes(payload)
    os.replace(temp, target)
    print("result_sha256=" + reference.sha256_hex(payload))


if __name__ == "__main__":
    main()
