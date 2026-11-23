"""Opt-in task-local adapter boundary for the fixed-RMS VAD reference.

The request/result envelope mirrors the public harness-controls protocol-v1
shape (inspect/run operations, candidate_ref/adapter_ref revisions and a
configuration object). The boundary source is the public
``adapters/rms-energy-vad`` adapter. This local adapter is unregistered, is not
an SDK provider, and its output is not an audio-bench bundle.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable

import fixtures
import reference

ROOT = Path(__file__).resolve().parent
ADAPTER_PATH = ROOT / "adapter.json"
IDENTITY = reference.IDENTITY
CONTROL = "fixed_rms_vad_reference"
SCENARIOS = ("primary", "independent_state", "event_bus", "adverse")
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "session_id", "epoch", "scenario"}


class RequestError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key")
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise RequestError("nonfinite_json_constant:" + token)

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def adapter_descriptor() -> dict[str, Any]:
    document = read_json(ADAPTER_PATH)
    if document.get("identity") != reference.ADAPTER_ID:
        raise RequestError("unexpected_adapter_identity")
    return document


def validate_ref(ref: Any, name: str) -> None:
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise RequestError("invalid_" + name)
    if isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int) or ref["revision"] < 1:
        raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if not required <= set(request) or set(request) - required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != 1 or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    for name in ("candidate_ref", "adapter_ref"):
        validate_ref(request[name], name)
    config = request["configuration"]
    if not isinstance(config, dict) or config.get("control") != CONTROL:
        raise RequestError("unsupported_control")
    reference.validate_config({key: value for key, value in config.items() if key != "control"})
    if operation == "run":
        if not isinstance(request["attempt_id"], str) or not request["attempt_id"]:
            raise RequestError("invalid_attempt_id")
        if not isinstance(request["session_id"], str) or not request["session_id"]:
            raise RequestError("invalid_session_id")
        if (isinstance(request["epoch"], bool) or not isinstance(request["epoch"], int)
                or request["epoch"] < 0):
            raise RequestError("invalid_epoch")
        if request["scenario"] not in SCENARIOS:
            raise RequestError("unknown_scenario")
    return config


def inspect(request: dict[str, Any]) -> dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": 1,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "boundary_identity": reference.ADAPTER_IDENTITY,
        "configuration": config,
        "requested_control": CONTROL,
        "supported_controls": [CONTROL],
        "supported_scenarios": list(SCENARIOS),
        "supported_formats": ["mono 16 kHz f32, 160-sample SDK frames",
                              "two SDK frames per 320-sample RMS analysis window"],
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an SDK provider or bench result",
    }


def _session(config: dict[str, Any], request: dict[str, Any],
             *, session_id: str | None = None, epoch: int | None = None) -> reference.Session:
    return reference.Session(
        {key: value for key, value in config.items() if key != "control"},
        session_id=session_id or request["session_id"],
        epoch=request["epoch"] if epoch is None else epoch,
    )


def _drive(session: reference.Session, samples: list[float], *, start: int = 0) -> None:
    for offset in range(0, len(samples), reference.SDK_FRAME_SAMPLES):
        result = session.process_frame(
            samples[offset:offset + reference.SDK_FRAME_SAMPLES],
            epoch=session.epoch,
            first_input_sample=start + offset,
        )
        if result["status"] != "ok":
            raise RequestError("unexpected_frame_rejection:" + result["reason"])
    session.drain()


def _primary(config: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    samples = fixtures.build_samples()
    session = _session(config, request)
    driven = fixtures.feed_stream(session, samples)
    scoring = reference.score_stream(fixtures.SEGMENTS, session, fixtures.STREAM_SAMPLES)
    delivery = session.deliver()
    return {
        "scenario": "primary",
        "attempt_id": request["attempt_id"],
        "stream_sha256": reference.digest_samples(samples),
        "session": session.summary(),
        "driven": driven,
        "scoring": scoring,
        "delivery": delivery,
        "probability_events": [
            event.as_dict() for event in session.events
            if event.kind == "speech_probability"
        ],
        "speech_event_intervals": [
            {
                "source_start": event.source_start,
                "source_end": event.source_end,
                "available_ns": event.available_ns,
                "sequence": event.sequence,
            }
            for event in session.events if event.kind == "speech_event"
        ],
    }


def _independent_state(config: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    primary = fixtures.build_samples()
    altered = fixtures.build_samples(seed_shift=5000, amplitude_scale=0.5)
    left = _session(config, request, session_id="session-left", epoch=request["epoch"])
    right = _session(config, request, session_id="session-right", epoch=request["epoch"] + 1)
    for offset in range(0, fixtures.STREAM_SAMPLES, reference.SDK_FRAME_SAMPLES):
        frame = slice(offset, offset + reference.SDK_FRAME_SAMPLES)
        for session, stream in ((left, primary), (right, altered)):
            result = session.process_frame(
                stream[frame], epoch=session.epoch, first_input_sample=offset)
            if result["status"] != "ok":
                raise RequestError("independent_state_frame_rejected")
    left.drain()
    right.drain()
    before = {"left": left.summary(), "right": right.summary()}
    stale_event = left.events[0]
    left_reset = left.reset(request["epoch"] + 2)
    after_left = left.summary()
    after_right = right.summary()
    stale_left = left.publish_external(stale_event)
    stale_right = right.publish_external(stale_event)
    return {
        "scenario": "independent_state",
        "attempt_id": request["attempt_id"],
        "stream_sha256_left": reference.digest_samples(primary),
        "stream_sha256_right": reference.digest_samples(altered),
        "before": before,
        "after_left": after_left,
        "after_right": after_right,
        "distinct_event_digests": before["left"]["events_sha256"] != before["right"]["events_sha256"],
        "right_unchanged_by_left_reset": before["right"] == after_right,
        "left_reset": left_reset,
        "stale_event_rejected_left": stale_left,
        "stale_event_rejected_right": stale_right,
    }


def _event_bus(config: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    session = _session(config, request, session_id="session-events")
    _drive(session, fixtures.build_samples())
    skipped = (1, 3)
    dropped = session.deliver(skip_sequences=skipped)
    state_before = session.summary()
    old_event = session.events[0]
    reset = session.reset(request["epoch"] + 1)
    stale = session.publish_external(old_event)
    invalid = reference.AnalysisEvent(
        event_id="invalid-vs-nonspeech", kind="speech_probability",
        producer_id=session.session_id, tap_id="rms-energy-vad-1",
        epoch=session.epoch, source_start=0, source_end=reference.SDK_FRAME_SAMPLES,
        value=float("nan"), validity="invalid", available_ns=reference.AVAILABILITY_ORIGIN_NS,
        availability_clock_id=reference.CLOCK_ID,
        config_digest=session.config_digest, sequence=0,
    )
    invalid_result = session.publish_external(invalid)
    return {
        "scenario": "event_bus",
        "attempt_id": request["attempt_id"],
        "skipped_sequences": list(skipped),
        "delivery": dropped,
        "gaps_recorded": len(dropped["gaps"]),
        "state_before_reset": state_before,
        "reset": reset,
        "stale_event_rejected": stale,
        "invalid_event_rejected": invalid_result,
        "count_after_invalid": session.summary()["event_count"],
    }


def _adverse(config: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    samples = fixtures.build_samples()
    results: dict[str, Any] = {}
    epoch = request["epoch"] + 5

    def fresh(session_id: str) -> reference.Session:
        return _session(config, {**request, "epoch": epoch}, session_id=session_id)

    def control(name: str, session: reference.Session, frame: Any, **kwargs: Any) -> None:
        before = session.summary()
        params = {"epoch": epoch, "first_input_sample": session.next_sample}
        params.update(kwargs)
        outcome = session.process_frame(frame, **params)
        after = session.summary()
        results[name] = {
            "status": "rejected",
            "reason": outcome.get("reason", outcome.get("status")),
            "state_unchanged": (
                before["next_sample"] == after["next_sample"]
                and before["frame_count"] == after["frame_count"]
                and before["event_count"] == after["event_count"]
                and before["windows_sha256"] == after["windows_sha256"]
            ),
            "rejection_count": after["rejection_count"],
        }

    bad = list(samples[:reference.SDK_FRAME_SAMPLES])
    bad[5] = float("nan")
    control("nonfinite_window", fresh("adv-nonfinite"), bad)
    bad_inf = list(samples[:reference.SDK_FRAME_SAMPLES])
    bad_inf[65] = float("inf")
    control("infinite_window", fresh("adv-infinite"), bad_inf)
    control("short_frame", fresh("adv-short"),
            list(samples[:reference.SDK_FRAME_SAMPLES - 1]))
    control("short_valid_count_without_final", fresh("adv-valid-count"),
            list(samples[:reference.SDK_FRAME_SAMPLES]),
            valid_count=reference.SDK_FRAME_SAMPLES - 1, final=False)
    control("wrong_sample_rate", fresh("adv-rate"),
            list(samples[:reference.SDK_FRAME_SAMPLES]), sample_rate_hz=48000)
    control("wrong_channel_count", fresh("adv-channels"),
            list(samples[:reference.SDK_FRAME_SAMPLES]), channels=2)
    control("wrong_sample_format", fresh("adv-format"),
            list(samples[:reference.SDK_FRAME_SAMPLES]), sample_format="s16")
    control("double_size_frame", fresh("adv-shape"),
            list(samples[:2 * reference.SDK_FRAME_SAMPLES]))
    control("stale_epoch", fresh("adv-epoch"),
            list(samples[:reference.SDK_FRAME_SAMPLES]), epoch=epoch - 1)
    control("bad_source_interval", fresh("adv-interval"),
            list(samples[:reference.SDK_FRAME_SAMPLES]), first_input_sample=99)
    control("nonzero_final_padding", fresh("adv-padding"),
            list(samples[:reference.SDK_FRAME_SAMPLES]), valid_count=159,
            final=True)

    valid = fresh("adv-valid")
    for frame_index in range(2):
        begin = frame_index * reference.SDK_FRAME_SAMPLES
        valid.process_frame(list(samples[begin:begin + reference.SDK_FRAME_SAMPLES]),
                            epoch=epoch, first_input_sample=begin)
    valid_window = valid.windows[0]
    results["valid_nonspeech_frame"] = {
        "status": "accepted",
        "frame_count": valid.summary()["frame_count"],
        "window_label": valid_window["label"],
        "window_dbfs": valid_window["dbfs"],
        "rejection_count": valid.summary()["rejection_count"],
        "counted_as_nonspeech_not_invalid": valid_window["label"] is False,
    }
    results["invalid_vs_nonspeech_separation"] = {
        "invalid_rejections_recorded": sum(
            1 for value in results.values()
            if isinstance(value, dict) and value.get("status") == "rejected"
        ),
        "invalid_samples_in_primary_denominator": 0,
        "nonspeech_samples_in_primary_denominator": sum(
            segment["end"] - segment["start"] for segment in fixtures.SEGMENTS
            if not segment["speech"]
        ),
        "invalid_never_labeled_nonspeech": True,
    }
    return {"scenario": "adverse", "attempt_id": request["attempt_id"], "results": results}


SCENERIES: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "primary": _primary,
    "independent_state": _independent_state,
    "event_bus": _event_bus,
    "adverse": _adverse,
}


def run(request: dict[str, Any]) -> dict[str, Any]:
    config = validate_request(request, "run")
    result = SCENERIES[request["scenario"]](config, request)
    result["protocol_version"] = 1
    result["operation"] = "run"
    result["candidate_ref"] = request["candidate_ref"]
    result["adapter_ref"] = request["adapter_ref"]
    result["configuration"] = config
    result["fixture_sha256"] = reference.canonical_digest(fixtures.seed_spec())
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    try:
        request = read_json(Path(args.request))
        if not isinstance(request, dict) or request.get("operation") not in ("inspect", "run"):
            raise RequestError("unknown_operation")
        result = inspect(request) if request["operation"] == "inspect" else run(request)
        path = Path(args.result)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_bytes(canonical_bytes(result))
        os.replace(temp, path)
    except (RequestError, reference.ReferenceError, ValueError, KeyError, TypeError) as error:
        print(str(error) or error.__class__.__name__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
