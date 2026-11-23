"""Task-local protocol-v1-shaped boundary for the median-residual click gate.

The envelope mirrors the public harness-controls adapter (inspect/run,
candidate_ref/adapter_ref revisions, strict JSON and a configuration object).
This adapter is unregistered, optional and developer-only. It is not an SDK
provider, descriptor, ABI or audio-bench bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import fixtures
import reference

ROOT = Path(__file__).resolve().parent
ADAPTER_PATH = ROOT / "adapter.json"
IDENTITY = reference.IDENTITY
CONTROL = reference.CONTROL
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "session_id", "epoch", "scenario"}
ALLOWED_RUN_FIELDS = RUN_FIELDS | {"case_id", "stimulus"}
SCENARIOS = ("case", "manual", "adverse", "state")
STIMULUS_FIELDS = {"case_id", "samples", "clean", "labels", "rate_plan"}
OPTIONAL_STIMULUS_FIELDS = {"transient_labels", "material", "note", "seed"}


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


def canonical_bytes(value: Any) -> bytes:
    return reference.canonical_bytes(value)


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
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    allowed = COMMON_FIELDS if operation == "inspect" else ALLOWED_RUN_FIELDS
    if not required <= set(request) or set(request) - allowed:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != 1 or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    for name in ("candidate_ref", "adapter_ref"):
        validate_ref(request[name], name)
    config = request["configuration"]
    if not isinstance(config, dict) or config.get("control") != CONTROL:
        raise RequestError("unsupported_control")
    reference.validate_config(config)
    if operation == "run":
        for name in ("attempt_id", "session_id"):
            if not isinstance(request[name], str) or not request[name]:
                raise RequestError("invalid_" + name)
        epoch = request["epoch"]
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise RequestError("invalid_epoch")
        if request["scenario"] not in SCENARIOS:
            raise RequestError("unknown_scenario")
        if request["scenario"] == "case":
            if request.get("case_id") not in fixtures.CASE_IDS or "stimulus" in request:
                raise RequestError("invalid_case_selection")
        elif request["scenario"] == "manual":
            if "case_id" in request or "stimulus" not in request:
                raise RequestError("invalid_manual_selection")
        elif "case_id" in request or "stimulus" in request:
            raise RequestError("unexpected_scenario_field")
    return config


def inspect(request: dict[str, Any]) -> dict[str, Any]:
    config = validate_request(request, "inspect")
    descriptor = adapter_descriptor()
    return {
        "protocol_version": 1,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "boundary_identity": reference.ADAPTER_IDENTITY,
        "descriptor_sha256": hashlib.sha256(ADAPTER_PATH.read_bytes()).hexdigest(),
        "configuration": config,
        "supported_controls": [CONTROL],
        "supported_scenarios": list(SCENARIOS),
        "supported_formats": ["mono 16 kHz f32, 160-sample SDK frames"],
        "buffering_delay_samples": 3,
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an SDK provider or bench result",
        "descriptor_summary": {
            key: descriptor[key] for key in (
                "protocol_version", "identity", "input_kind", "output_kinds",
                "modes", "entrypoint", "weights", "registration", "boundary_source")
        },
    }


def _config_without_control(config: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in config.items() if key != "control"}


def _session(config: dict[str, Any], *, session_id: str, epoch: int) -> reference.Session:
    return reference.Session(config, session_id=session_id, epoch=epoch)


def _drive(config: dict[str, Any], case: dict[str, Any], *, session_id: str,
           epoch: int) -> tuple[reference.Session, dict[str, Any]]:
    session = _session(config, session_id=session_id, epoch=epoch)
    samples = case["samples"]
    for offset in range(0, len(samples), reference.SDK_FRAME_SAMPLES):
        chunk = samples[offset:offset + reference.SDK_FRAME_SAMPLES]
        valid_count = len(chunk)
        padded = chunk + [0.0] * (reference.SDK_FRAME_SAMPLES - valid_count)
        final = offset + valid_count == len(samples)
        outcome = session.process_frame(
            padded, epoch=epoch, session_id=session_id, first_input_sample=offset,
            valid_count=valid_count,
            flags=reference.FLAG_FINAL_INPUT if final else 0)
        if outcome["status"] != "ok":
            raise RequestError("unexpected_frame_rejection:" + outcome["reason"])
    drain = session.drain()
    if drain["status"] != "end_of_stream":
        raise RequestError("unexpected_drain_result")
    return session, reference.score_case(session, case)


def _manual_case(stimulus: Any) -> dict[str, Any]:
    if not isinstance(stimulus, dict):
        raise RequestError("invalid_stimulus")
    allowed = STIMULUS_FIELDS | OPTIONAL_STIMULUS_FIELDS
    if not STIMULUS_FIELDS <= set(stimulus) or set(stimulus) - allowed:
        raise RequestError("invalid_stimulus_fields")
    samples = stimulus["samples"]
    clean = stimulus["clean"]
    labels = stimulus["labels"]
    if not isinstance(samples, list) or not isinstance(clean, list) or not isinstance(labels, list):
        raise RequestError("invalid_stimulus_arrays")
    if not (0 < len(samples) == len(clean) == len(labels)):
        raise RequestError("stimulus_length_mismatch")
    for value in samples + clean:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise RequestError("nonfinite_stimulus_input")
    if any(not isinstance(value, bool) for value in labels):
        raise RequestError("invalid_stimulus_labels")
    try:
        plan = fixtures.validate_rate_plan(stimulus["rate_plan"], len(samples))
    except ValueError as error:
        raise RequestError(str(error)) from error
    transients = stimulus.get("transient_labels", [False] * len(samples))
    if not isinstance(transients, list) or len(transients) != len(samples) or \
            any(not isinstance(value, bool) for value in transients):
        raise RequestError("invalid_stimulus_transients")
    return {
        "case_id": stimulus["case_id"],
        "material": stimulus.get("material", "caller-owned synthetic stimulus"),
        "seed": stimulus.get("seed", 0),
        "note": stimulus.get("note", "caller-owned input; copied into session state"),
        "clean": list(clean), "samples": list(samples), "labels": list(labels),
        "transient_labels": list(transients), "rate_plan": plan,
        "playback_end_ns": fixtures.playback_end_ns(plan),
        "rate_change_boundaries": fixtures.rate_change_boundaries(plan),
    }


def _add_control(rows: list[dict[str, Any]], name: str, outcome: str, reason: str,
                 *, state_unchanged: bool | None = None, detail: dict[str, Any] | None = None) -> None:
    rows.append({
        "id": name,
        "status": "observed",
        "outcome": outcome,
        "reason": reason,
        "state_unchanged": state_unchanged,
        "detail": detail or {},
    })


def functional_state(session: reference.Session) -> dict[str, Any]:
    """State that must not change on rejection; the rejection counter may change."""
    state = session.summary()
    state.pop("rejection_count")
    return state


def adverse(config: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    epoch = request["epoch"] + 5

    def frame_control(name: str, frame: Any, **kwargs: Any) -> None:
        session = _session(config, session_id="session-" + name, epoch=epoch)
        before = functional_state(session)
        params: dict[str, Any] = {"epoch": epoch, "session_id": session.session_id,
                                  "first_input_sample": 0}
        params.update(kwargs)
        outcome = session.process_frame(frame, **params)
        after = functional_state(session)
        _add_control(rows, name, outcome.get("status", "unknown"),
                     outcome.get("reason", outcome.get("status", "unknown")),
                     state_unchanged=before == after)

    base = [0.0] * reference.SDK_FRAME_SAMPLES
    nonfinite = list(base)
    nonfinite[5] = float("nan")
    nonfinite[159] = float("inf")
    frame_control("nonfinite_input", nonfinite)
    frame_control("wrong_frame_length", [0.0] * 159)
    frame_control("invalid_valid_count_zero", base, valid_count=0)
    frame_control("invalid_valid_count_over", base, valid_count=161)
    padded = list(base)
    padded[7] = 1.0
    frame_control("nonzero_final_padding", padded, valid_count=5,
                  flags=reference.FLAG_FINAL_INPUT)
    frame_control("unknown_frame_flags", base, flags=4)
    frame_control("stale_epoch", base, epoch=epoch - 1)
    frame_control("stale_session", base, session_id="session-other")
    frame_control("stale_source_position", base, first_input_sample=160)

    drain_session = _session(config, session_id="session-early-drain", epoch=epoch)
    before_drain = functional_state(drain_session)
    early_drain = drain_session.drain()
    _add_control(rows, "drain_before_final_input", early_drain["status"],
                 early_drain.get("reason", early_drain["status"]),
                 state_unchanged=before_drain == functional_state(drain_session))

    session = _session(config, session_id="session-after-final", epoch=epoch)
    first = session.process_frame(base, epoch=epoch, session_id=session.session_id,
                                  first_input_sample=0,
                                  flags=reference.FLAG_FINAL_INPUT)
    before_second = functional_state(session)
    second = session.process_frame(base, epoch=epoch, session_id=session.session_id,
                                   first_input_sample=160)
    _add_control(rows, "process_after_final_input", second["status"],
                 second.get("reason", second["status"]),
                 state_unchanged=first["status"] == "ok"
                 and before_second == functional_state(session))

    for name, mutate in (
        ("config_missing_control", lambda c: dict(c)),
        ("config_unknown_control", lambda c: {**c, "unexpected": 1}),
        ("config_even_median_width", lambda c: {**c, "median_width_samples": 8}),
        ("config_threshold_out_of_range", lambda c: {**c, "threshold": 1.5}),
        ("config_nonnumeric_threshold", lambda c: {**c, "threshold": "nan"}),
        ("config_wrong_sample_rate", lambda c: {**c, "sample_rate_hz": 44100}),
        ("config_wrong_channels", lambda c: {**c, "channels": 2}),
        ("config_wrong_sample_format", lambda c: {**c, "sample_format": "s16"}),
    ):
        candidate = mutate(_config_without_control(config))
        if name != "config_missing_control":
            candidate = {"control": CONTROL, **candidate}
        try:
            reference.validate_config(candidate)
            outcome, reason = "accepted", "none"
        except reference.ControlError as error:
            outcome, reason = "rejected", str(error)
        _add_control(rows, name, outcome, reason, state_unchanged=True)

    bad_plans: list[tuple[str, dict[str, Any], int]] = []
    clock_id = fixtures.make_rate_plan("constant_1x", 320)["clock_id"]
    overlapping = {"clock_id": clock_id, "segments": [
        {"start": 0, "end": 200, "rate_num": 1, "rate_den": 1,
         "origin_ns": 0, "rebuffer_ns_before": 0, "segment_index": 0},
        {"start": 100, "end": 320, "rate_num": 1, "rate_den": 1,
         "origin_ns": 200 * reference.NS_PER_SAMPLE,
         "rebuffer_ns_before": 0, "segment_index": 1},
    ]}
    drift = fixtures.make_rate_plan("constant_1x", 320)
    drift["segments"][0]["rate_num"] = 2
    origin = fixtures.make_rate_plan("constant_1x", 320)
    origin["segments"][0]["origin_ns"] = "nan"
    length = fixtures.make_rate_plan("constant_1x", 319)
    bad_plans.extend((("rate_plan_overlap", overlapping, 320),
                      ("rate_drift_bound_exceeded", drift, 320),
                      ("rate_plan_nonfinite_origin", origin, 320),
                      ("rate_plan_length_mismatch", length, 320)))
    for name, candidate, expected_length in bad_plans:
        try:
            fixtures.validate_rate_plan(candidate, expected_length)
            outcome, reason = "accepted", "none"
        except (ValueError, TypeError) as error:
            outcome, reason = "rejected", str(error)
        _add_control(rows, name, outcome, reason, state_unchanged=True)

    bad_requests: list[tuple[str, dict[str, Any]]] = [
        ("request_missing_attempt_id", {key: value for key, value in request.items()
                                        if key != "attempt_id"}),
        ("request_unknown_field", {**request, "unexpected": 1}),
    ]
    for name, candidate in bad_requests:
        try:
            validate_request(candidate, "run")
            outcome, reason = "accepted", "none"
        except RequestError as error:
            outcome, reason = "rejected", str(error)
        _add_control(rows, name, outcome, reason, state_unchanged=True)

    return {
        "scenario": "adverse",
        "attempt_id": request["attempt_id"],
        "controls": rows,
        "control_count": len(rows),
        "all_observed": all(row["status"] == "observed" for row in rows),
        "all_rejected_or_expected": all(row["outcome"] == "rejected" for row in rows),
        "missing_results": [row["id"] for row in rows if row["status"] != "observed"],
    }


def state_controls(config: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    epoch = request["epoch"] + 11
    case_a = fixtures.build_case("speech_1x")
    clean_b, transients_b = fixtures.speech_like(reference.SDK_FRAME_SAMPLES * 3, 990011)
    case_b = {
        "case_id": "state-b", "material": "independent synthetic speech-like material",
        "seed": 990011, "note": "independent session state", "clean": clean_b,
        "samples": clean_b, "labels": [False] * len(clean_b),
        "transient_labels": transients_b,
        "rate_plan": fixtures.make_rate_plan("constant_1x", len(clean_b)),
        "playback_end_ns": fixtures.playback_end_ns(
            fixtures.make_rate_plan("constant_1x", len(clean_b))),
        "rate_change_boundaries": [],
    }
    left = _session(config, session_id="session-left", epoch=epoch)
    right = _session(config, session_id="session-right", epoch=epoch + 1)
    for index in range(3):
        for session, case in ((left, case_a), (right, case_b)):
            offset = index * reference.SDK_FRAME_SAMPLES
            frame = case["samples"][offset:offset + reference.SDK_FRAME_SAMPLES]
            outcome = session.process_frame(
                frame, epoch=session.epoch, session_id=session.session_id,
                first_input_sample=offset,
                flags=reference.FLAG_FINAL_INPUT if index == 2 else 0)
            if outcome["status"] != "ok":
                raise RequestError("state_control_frame_rejected")
    before_left = left.summary()
    before_right = right.summary()
    old_decision = next(iter(left.decisions.values()))
    stale_epoch = right.publish_decision(old_decision, epoch=epoch,
                                         session_id=right.session_id)
    stale_session = right.publish_decision(old_decision, epoch=right.epoch,
                                           session_id=left.session_id)
    reset = left.reset(epoch + 2)
    stale_frame = left.process_frame([0.0] * reference.SDK_FRAME_SAMPLES,
                                     epoch=epoch, session_id=left.session_id,
                                     first_input_sample=0)
    after_right = right.summary()
    drain = left.drain()
    return {
        "scenario": "state",
        "attempt_id": request["attempt_id"],
        "left_digest_before": before_left["output_sha256"],
        "right_digest_before": before_right["output_sha256"],
        "digests_distinct": before_left["output_sha256"] != before_right["output_sha256"],
        "right_unchanged_by_left_reset": before_right == after_right,
        "stale_epoch_decision": stale_epoch,
        "stale_session_decision": stale_session,
        "stale_epoch_frame": stale_frame,
        "reset": reset,
        "drain_after_reset_without_final_input": drain,
        "missing_results": [],
    }


def dispatch(request: dict[str, Any]) -> dict[str, Any]:
    operation = request.get("operation") if isinstance(request, dict) else None
    if operation == "inspect":
        return inspect(request)
    if operation == "run":
        config = validate_request(request, "run")
        scenario = request["scenario"]
        if scenario == "case":
            case = fixtures.build_case(request["case_id"])
            _, scored = _drive(config, case, session_id=request["session_id"],
                               epoch=request["epoch"])
            return {"scenario": "case", "attempt_id": request["attempt_id"], **scored}
        if scenario == "manual":
            case = _manual_case(request["stimulus"])
            _, scored = _drive(config, case, session_id=request["session_id"],
                               epoch=request["epoch"])
            return {"scenario": "manual", "attempt_id": request["attempt_id"], **scored}
        if scenario == "adverse":
            return adverse(config, request)
        return state_controls(config, request)
    raise RequestError("unknown_operation")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args(argv)
    result = dispatch(read_json(args.request))
    args.result.write_bytes(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
