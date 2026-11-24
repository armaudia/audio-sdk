# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in task-local adapter boundary for the SpeexDSP VAD reference.

The request/result envelope mirrors the public harness-controls protocol-v1
shape used by ``adapters/speexdsp-vad`` (inspect/run operations,
candidate_ref/adapter_ref revisions and a configuration object). This local
adapter is unregistered, is not an SDK provider and its output is not a bench
result. ``--report`` regenerates the canonical evidence with three byte-
identical repeats and no tolerance.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import fixtures
import reference

ROOT = Path(__file__).resolve().parent
REPORT_FILE = ROOT / "report.json"
SIDECAR_FILE = ROOT / "report.json.sha256"
IDENTITY = "speexdsp-vad-reference-v1"
CONTROL = reference.CONTROL
SCENARIOS = reference.SCENARIOS
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
    return (reference.canonical_json(value) + "\n").encode("utf-8")


def validate_ref(ref: Any, name: str) -> None:
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise RequestError("invalid_" + name)
    if (isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int)
            or ref["revision"] < 1):
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
    try:
        reference.validate_config({key: value for key, value in config.items() if key != "control"})
    except ValueError as error:
        raise RequestError(str(error)) from error
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
        "boundary_identity": reference.ADAPTER_ID,
        "configuration": config,
        "requested_control": CONTROL,
        "supported_controls": [CONTROL],
        "supported_scenarios": list(SCENARIOS),
        "supported_formats": [
            "mono 16 kHz f32, 160-sample SDK frames",
            "historical adapter declares 320-sample frames; no parity claim",
        ],
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an SDK provider or bench result",
    }


def _session(config: dict[str, Any], request: dict[str, Any]) -> reference.Session:
    return reference.Session(
        {key: value for key, value in config.items() if key != "control"},
        session_id=request["session_id"], epoch=request["epoch"])


def _drive(session: reference.Session, frames: list[tuple[float, ...]]) -> list[dict[str, Any]]:
    records = []
    for index, frame in enumerate(frames):
        segment = fixtures.segment_for_frame(index)
        record = session.process_frame(list(frame), epoch=session.epoch,
                                       validity=segment.validity)
        if record["status"] != "ok":
            raise RequestError("unexpected_frame_rejection:" + record["status"])
        records.append(record)
    session.drain()
    return records


def run(request: dict[str, Any]) -> dict[str, Any]:
    config = validate_request(request, "run")
    frames, pcm_digest = fixtures.build_frames()
    if request["scenario"] == "primary":
        session = _session(config, request)
        records = _drive(session, frames)
        runs = reference.detection_runs(records)
        return {
            "scenario": "primary",
            "attempt_id": request["attempt_id"],
            "stream_sha256": pcm_digest,
            "session": session.summary(),
            "scoring": reference.score_stream(records, runs),
            "speech_intervals": [[start * fixtures.SDK_FRAME_SAMPLES,
                                  end * fixtures.SDK_FRAME_SAMPLES] for start, end in runs],
        }
    if request["scenario"] == "independent_state":
        return {
            "scenario": "independent_state",
            "attempt_id": request["attempt_id"],
            "control": reference.independent_state_control(frames),
        }
    if request["scenario"] == "event_bus":
        return {
            "scenario": "event_bus",
            "attempt_id": request["attempt_id"],
            "control": reference.event_adverse_control(),
            "cross_hop": reference.cross_hop_control(),
        }
    return {
        "scenario": "adverse",
        "attempt_id": request["attempt_id"],
        "frame_control": reference.frame_adverse_control(),
        "validity_control": reference.invalid_vs_nonspeech_control(),
        "overlapping_sessions": reference.overlapping_session_control(frames),
    }


def regenerate_report() -> tuple[str, str, str]:
    """Generate three reports; write only if all three are byte-identical."""
    payloads: list[tuple[bytes, str]] = []
    for _ in range(3):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        payloads.append(((text + "\n").encode("utf-8"), digest))
    if len({payload for payload, _ in payloads}) != 1 or len({digest for _, digest in payloads}) != 1:
        raise AssertionError("report_regeneration_not_byte_identical")
    payload, digest = payloads[0]
    REPORT_FILE.write_bytes(payload)
    SIDECAR_FILE.write_text(digest + "\n", encoding="ascii")
    return digest, reference.sha256_bytes(payload), report["task"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="write report.json and report.json.sha256 from three identical runs")
    parser.add_argument("--request", type=Path, default=None,
                        help="process a protocol-v1 inspect/run request file")
    options = parser.parse_args()
    if options.report and options.request is not None:
        parser.error("--report and --request are mutually exclusive")
    if options.report:
        digest, file_digest, task = regenerate_report()
        print(f"task={task}")
        print(f"repeats=3 byte_identical=true")
        print(f"canonical_report_sha256={digest}")
        print(f"report_file_sha256={file_digest}")
        return 0
    if options.request is None:
        parser.print_help()
        return 0
    request = read_json(options.request)
    operation = request.get("operation") if isinstance(request, dict) else None
    if operation == "inspect":
        response = inspect(request)
    elif operation == "run":
        response = run(request)
    else:
        raise RequestError("invalid_operation")
    sys.stdout.buffer.write(canonical_bytes(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
