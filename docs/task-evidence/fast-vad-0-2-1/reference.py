# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic VAD probability/event reference and frozen report.

This is a task-local *surrogate*, not fast-vad.  No wheel, binary, licensed
runtime, real speech, device clock or model posterior is used.  The reference
emits timestamped probability and speech-event records on exact half-open
source intervals with explicit validity, availability, sequence and epoch
state, then applies the Analysis profile through the task-local scorer.
"""

from __future__ import annotations

import math
from typing import Any

import fixture
import scorer

SCHEMA_ID = "audio-sdk/fast-vad-0-2-1-analysis-evidence/0.1"
TASK = "SDK-FAST-VAD-0-2-1"
COMPONENT = "fast-vad-0-2-1"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "2bc2a13aa4c5b398933fd9097d09746ce151216e"
BRANCH = "swarm/SDK-FAST-VAD-0-2-1"
STATUS = "proposal_only_not_qualified"
QUALIFICATION_STATUS = "incomplete"
DECISION = "DEFER"
PROCESSOR_EXPOSURE = False

ADAPTER_ID = "fast-vad-0.2.1-normal-stateful"
LOCAL_IDENTITY = "fast-vad-0-2-1-synthetic-reference-v1"
PROVIDER_ID = "analysis.fast-vad.synthetic.v0"

REPORT_KEYS = {
    "schema_id", "task", "component", "repository", "base_commit", "branch",
    "profile", "status", "qualification_status", "decision", "processor_exposure",
    "public_surface_changed", "installed_v0_changed", "fixture_spec",
    "local_config", "source_pins", "mutable_provenance", "boundary_pins",
    "streams", "results", "controls", "acceptance_profile", "repeat_runs",
    "release_gates", "non_claims", "reproduction",
}

VALIDITIES = {"known", "unknown", "invalid", "missing"}
MISSING = object()
EXPLICIT_MISSING = "explicit_missing_token"

RELEASE_GATES = [
    "Independent exact-head review of this proposal before any processor exposure",
    "No registered provider, descriptor default or public API/ABI change without intake approval",
    "No fast-vad runtime, wheel, licensed asset or upstream oracle in the default package",
    "Rights-cleared, label-complete held-out cohort and frozen candidate outputs before any accuracy claim",
    "Pinned target runtime, device clock, deadline budget and matched workload before any availability claim",
    "S10/protocol clearance and approved reference adapter before any Tiny16 comparison",
    "Release approval; DEFER remains in force until every gate above is closed",
]

NON_CLAIMS = [
    "No real fast-vad runtime, wheel download, model weight, licensed runtime or upstream code is used",
    "No real speech, corpus, recording, listening, quality, intelligibility or device result",
    "No parity with the 512-sample real-runtime adapter or with source-reported AMI FN/FP values",
    "No installed v0, API/ABI, descriptor, registry, default, board or other worktree change",
    "No control signal, gate, endpointing rule, processor exposure or release qualification",
    "No timing, pacing, power, production availability or hard real-time claim",
]


def canonical_bytes(value: Any) -> bytes:
    return fixture.canonical_bytes(value)


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report).decode("utf-8")
    return payload, fixture.sha256_bytes(payload.encode("utf-8"))


class Session:
    """Independent, epoch-scoped VAD analysis session with explicit audit."""

    def __init__(self, config: dict[str, Any], session_id: str, epoch: int) -> None:
        fixture.validate_config(config)
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self.config = config
        self.session_id = session_id
        self.epoch = epoch
        self._reset(epoch)

    def _reset(self, epoch: int) -> None:
        self.epoch = epoch
        self.events: list[dict[str, Any]] = []
        self.speech_events: list[dict[str, Any]] = []
        self.rejections: list[dict[str, Any]] = []
        self.dropped: list[dict[str, Any]] = []
        self.total_samples = 0
        self.frame_index = 0
        self.next_sequence = 1
        self.active_start: int | None = None
        self.hangover_used = 0

    def reset(self, epoch: int) -> dict[str, Any]:
        previous = self.epoch
        self._reset(epoch)
        return {"status": "ok", "operation": "reset", "previous_epoch": previous,
                "epoch": self.epoch, "session_id": self.session_id}

    def available_ns(self, end_sample: int) -> int:
        return (self.config["origin_ns"] + end_sample * self.config["sample_period_ns"]
                + self.config["processing_delay_ns"])

    def _reject(self, reason: str, epoch: int | None, start_sample: int | None) -> dict[str, Any]:
        before = self.summary()
        record = {"status": "rejected", "reason": reason, "epoch": epoch,
                  "start_sample": start_sample, "session_id": self.session_id,
                  "state_digest_before": before["state_digest"]}
        self.rejections.append(record)
        record["state_digest_after"] = self.summary()["state_digest"]
        if record["state_digest_after"] != record["state_digest_before"]:
            raise AssertionError("rejection_mutated_state:" + reason)
        return record

    def process_frame(
        self,
        frame: list[float],
        *,
        epoch: int | None = None,
        validity: str = "known",
        probability: float | object = MISSING,
        start_sample: int | None = None,
        end_sample: int | None = None,
        available_ns: int | None = None,
        clock: str | None = None,
        sequence: int | None = None,
        is_final: bool = False,
        valid_samples: int | None = None,
    ) -> dict[str, Any]:
        if epoch is None:
            epoch = self.epoch
        if epoch != self.epoch:
            return self._reject("stale_epoch", epoch, start_sample)
        if validity not in VALIDITIES:
            return self._reject("unknown_validity_token", epoch, start_sample)
        if validity in ("invalid", "missing"):
            return self._reject("invalid_event_validity" if validity == "invalid"
                                else "missing_event_validity", epoch, start_sample)
        if (not isinstance(frame, (list, tuple)) or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) for v in frame)):
            return self._reject("wrong_frame_format", epoch, start_sample)
        if any(not math.isfinite(float(v)) for v in frame):
            return self._reject("nonfinite_frame", epoch, start_sample)
        expected_samples = self.config["frame_samples"]
        if is_final:
            if (isinstance(valid_samples, bool) or not isinstance(valid_samples, int)
                    or not 1 <= valid_samples <= expected_samples):
                return self._reject("invalid_final_valid_samples", epoch, start_sample)
            expected_samples = valid_samples
        elif valid_samples is not None:
            return self._reject("unexpected_valid_samples", epoch, start_sample)
        if len(frame) != expected_samples:
            return self._reject("short_frame" if len(frame) < expected_samples
                                else "long_frame", epoch, start_sample)
        if start_sample != self.total_samples or end_sample != self.total_samples + expected_samples:
            return self._reject("wrong_source_interval", epoch, start_sample)
        if clock is not None and clock != self.config["clock"]:
            return self._reject("wrong_clock", epoch, start_sample)
        if sequence is not None and sequence != self.next_sequence:
            return self._reject("duplicate_or_out_of_order_sequence", epoch, start_sample)
        if probability is MISSING:
            value = fixture.probability_for_frame(list(frame))
        elif probability == EXPLICIT_MISSING:
            return self._reject("missing_probability", epoch, start_sample)
        elif isinstance(probability, bool) or not isinstance(probability, (int, float)):
            return self._reject("missing_probability", epoch, start_sample)
        elif not math.isfinite(float(probability)):
            return self._reject("nonfinite_probability", epoch, start_sample)
        elif not 0.0 <= float(probability) <= 1.0:
            return self._reject("probability_out_of_range", epoch, start_sample)
        else:
            value = float(probability)
        computed_available = None if validity == "unknown" else self.available_ns(end_sample)
        if available_ns is not None and available_ns != computed_available:
            return self._reject("stale_availability", epoch, start_sample)

        decision: bool | None = None
        if validity == "known":
            decision = value >= self.config["decision_threshold"]
        event = {
            "sequence": self.next_sequence,
            "session_id": self.session_id,
            "epoch": self.epoch,
            "validity": validity,
            "event_type": "speech_probability",
            "start_sample": start_sample,
            "end_sample": end_sample,
            "probability": round(value, 12),
            "decision": decision,
            "clock": self.config["clock"] if validity != "unknown" else None,
            "available_ns": computed_available,
            "advisory_only": True,
        }
        self.events.append(event)
        self.next_sequence += 1
        self.total_samples = end_sample
        self.frame_index += 1

        emitted = None
        if decision is True:
            if self.active_start is None:
                self.active_start = start_sample
            self.hangover_used = 0
        elif decision is False and self.active_start is not None:
            self.hangover_used += 1
            if self.hangover_used >= self.config["hangover_frames"]:
                emitted = self._close_run(start_sample)
        return {"status": "ok", "probability_event": event, "speech_event": emitted}

    def _close_run(self, close_at: int) -> dict[str, Any]:
        if self.active_start is None:
            raise AssertionError("close_without_run")
        run = {
            "sequence": len(self.speech_events) + 1,
            "session_id": self.session_id,
            "epoch": self.epoch,
            "event_type": "speech_event",
            "start_sample": self.active_start,
            "end_sample": close_at,
            "available_sample": self.total_samples,
            "available_ns": self.available_ns(self.total_samples),
            "clock": self.config["clock"],
            "advisory_only": True,
        }
        self.speech_events.append(run)
        self.active_start = None
        self.hangover_used = 0
        return run

    def drain(self) -> dict[str, Any]:
        emitted = self._close_run(self.total_samples) if self.active_start is not None else None
        return {"status": "ok", "operation": "drain", "speech_event": emitted,
                "total_samples": self.total_samples}

    def drop_sequence(self, sequence: int, reason: str = "synthetic_bus_drop") -> dict[str, Any]:
        self.dropped.append({"sequence": sequence, "reason": reason,
                             "session_id": self.session_id, "epoch": self.epoch})
        return self.dropped[-1]

    def state_digest_payload(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id, "epoch": self.epoch,
            "total_samples": self.total_samples, "frame_index": self.frame_index,
            "next_sequence": self.next_sequence, "active_start": self.active_start,
            "hangover_used": self.hangover_used,
            "events_digest": fixture.sha256_bytes(canonical_bytes(self.events)),
            "speech_events_digest": fixture.sha256_bytes(canonical_bytes(self.speech_events)),
        }

    def summary(self) -> dict[str, Any]:
        payload = self.state_digest_payload()
        return {
            "session_id": self.session_id,
            "epoch": self.epoch,
            "probability_events": len(self.events),
            "speech_events": len(self.speech_events),
            "rejections": len(self.rejections),
            "dropped": len(self.dropped),
            "total_samples": self.total_samples,
            "probability_event_digest": payload["events_digest"],
            "speech_event_digest": payload["speech_events_digest"],
            "state_digest": fixture.sha256_bytes(canonical_bytes(payload)),
        }


def drive(session: Session, frames: list[list[float]], start: int = 0,
          end: int | None = None) -> list[dict[str, Any]]:
    end = len(frames) if end is None else end
    records = []
    for index in range(start, end):
        segment = fixture.segment_for_frame(index)
        validity = "known" if segment["truth"] != "unknown" else "unknown"
        record = session.process_frame(frames[index], validity=validity,
                                       start_sample=index * fixture.FRAME_SAMPLES,
                                       end_sample=(index + 1) * fixture.FRAME_SAMPLES)
        if record["status"] != "ok":
            raise AssertionError("unexpected_rejection:" + record["reason"])
        records.append(record)
    return records


def event_bus_control(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Explicit dropped/stale/missing/nonfinite event cases; nothing fabricated."""
    delivered_sequences = [event["sequence"] for event in events
                           if event["sequence"] not in (2, 5, 17)]
    dropped_sequences = [2, 5, 17]
    gaps = []
    cursor = 1
    for sequence in delivered_sequences:
        if sequence > cursor:
            gaps.append([cursor, sequence - 1])
        cursor = sequence + 1
    session = Session(fixture.CONFIG, "event-bus", 4)
    frame = fixture.build_frames()[0]
    first = session.process_frame(frame, epoch=4, validity="known",
                                  start_sample=0, end_sample=fixture.FRAME_SAMPLES)
    base = first["probability_event"]["available_ns"]
    cases: dict[str, Any] = {}
    checks = (
        ("stale_epoch", {"epoch": 3}, "stale_epoch"),
        ("missing_probability", {"probability": EXPLICIT_MISSING}, "missing_probability"),
        ("nonfinite_probability", {"probability": float("nan")}, "nonfinite_probability"),
        ("infinite_probability", {"probability": float("inf")}, "nonfinite_probability"),
        ("out_of_range_probability", {"probability": 1.4}, "probability_out_of_range"),
        ("invalid_validity", {"validity": "invalid"}, "invalid_event_validity"),
        ("missing_validity", {"validity": "missing"}, "missing_event_validity"),
        ("wrong_clock", {"clock": "other-clock"}, "wrong_clock"),
        ("stale_availability", {"available_ns": 0}, "stale_availability"),
        ("wrong_interval", {"start_sample": 1}, "wrong_source_interval"),
        ("duplicate_sequence", {"sequence": 1}, "duplicate_or_out_of_order_sequence"),
        ("nonfinite_frame", {"frame": [float("nan")] * fixture.FRAME_SAMPLES}, "nonfinite_frame"),
        ("short_frame", {"frame": [0.0] * 80}, "short_frame"),
    )
    for name, kwargs, expected in checks:
        options = {"epoch": 4, "validity": "known",
                   "start_sample": fixture.FRAME_SAMPLES,
                   "end_sample": 2 * fixture.FRAME_SAMPLES,
                   "probability": 0.25}
        options.update(kwargs)
        if name == "wrong_clock":
            options["available_ns"] = session.available_ns(2 * fixture.FRAME_SAMPLES)
        if name == "stale_availability":
            options["available_ns"] = 0
        if name == "duplicate_sequence":
            options["sequence"] = 1
        record = session.process_frame(options.pop("frame", frame), **options)
        cases[name] = {"status": record["status"], "reason": record["reason"],
                       "expected_reason": expected,
                       "accepted": record["status"] == "ok",
                       "state_unchanged": record.get("state_digest_before")
                       == record.get("state_digest_after")}
        if cases[name]["reason"] != expected or not cases[name]["state_unchanged"]:
            raise AssertionError("event_control_failed:" + name)
    return {
        "total_sequences": len(events),
        "delivered_sequences": delivered_sequences,
        "dropped_sequences": dropped_sequences,
        "gaps": gaps,
        "fabricated_events": 0,
        "availability_example_ns": base,
        "adverse_cases": cases,
        "all_rejected_without_state_change": all(
            case["state_unchanged"] and not case["accepted"] for case in cases.values()),
    }


def independent_state_control(frames: list[list[float]]) -> dict[str, Any]:
    left = Session(fixture.CONFIG, "left", 3)
    right = Session(fixture.CONFIG, "right", 8)
    drive(left, frames, 0, 20)
    drive(right, frames, 0, 20)
    before = {"left": left.summary(), "right": right.summary()}
    if before["left"]["probability_event_digest"] == before["right"]["probability_event_digest"]:
        raise AssertionError("sessions_are_not_independent")
    left.reset(4)
    drive(left, frames, 0, 2)
    after = {"left": left.summary(), "right": right.summary()}
    if after["right"] != before["right"] or after["left"]["epoch"] != 4:
        raise AssertionError("reset_leaked_across_sessions")
    fresh = Session(fixture.CONFIG, "left", 4)
    drive(fresh, frames, 0, 2)
    return {
        "before": before,
        "after_reset": after,
        "reset_matches_fresh_digest":
            after["left"]["probability_event_digest"] == fresh.summary()["probability_event_digest"],
        "old_epoch_event_rejected": left.process_frame(
            frames[2], epoch=3, validity="known", start_sample=2 * fixture.FRAME_SAMPLES,
            end_sample=3 * fixture.FRAME_SAMPLES)["reason"],
    }


def cross_hop_control() -> dict[str, Any]:
    interval = (150, 330)
    projected = scorer.project_interval(*interval, frame_samples=fixture.FRAME_SAMPLES)
    expected = [[0, 10], [1, 160], [2, 10]]
    if [list(item) for item in projected] != expected:
        raise AssertionError("cross_hop_projection_mismatch")
    truth_projection = scorer.project_interval(960, 2560, frame_samples=fixture.FRAME_SAMPLES)
    return {
        "interval": list(interval),
        "frames": [list(item) for item in projected],
        "overlap_samples": sum(overlap for _, overlap in projected),
        "truth_interval": [960, 2560],
        "truth_hops": len(truth_projection),
        "truth_overlap_samples": sum(overlap for _, overlap in truth_projection),
        "source_time_mapping": fixture.CONFIG["source_time_mapping"],
        "declared_analysis_delay_samples": fixture.CONFIG["declared_analysis_delay_samples"],
    }


def frame_adverse_control() -> dict[str, Any]:
    session = Session(fixture.CONFIG, "frame-adverse", 1)
    frame = fixture.build_frames()[0]
    session.process_frame(frame, validity="known", start_sample=0,
                          end_sample=fixture.FRAME_SAMPLES)
    before = session.summary()["state_digest"]
    cases = {}
    variants = (
        ("nan", [float("nan")] * fixture.FRAME_SAMPLES, "nonfinite_frame"),
        ("infinite", [float("inf")] * fixture.FRAME_SAMPLES, "nonfinite_frame"),
        ("short", [0.0] * 80, "short_frame"),
        ("long", [0.0] * (fixture.FRAME_SAMPLES + 1), "long_frame"),
    )
    for name, data, expected in variants:
        record = session.process_frame(data, validity="known",
                                       start_sample=fixture.FRAME_SAMPLES,
                                       end_sample=2 * fixture.FRAME_SAMPLES,
                                       probability=0.1)
        cases[name] = {"reason": record["reason"], "expected": expected,
                       "state_unchanged": session.summary()["state_digest"] == before}
        if cases[name]["reason"] != expected or not cases[name]["state_unchanged"]:
            raise AssertionError("frame_control_failed:" + name)
    # A valid final 80-sample frame is admitted with exact coordinates.
    final = session.process_frame([0.0] * 80, validity="known",
                                  start_sample=fixture.FRAME_SAMPLES,
                                  end_sample=fixture.FRAME_SAMPLES + 80,
                                  probability=0.1, is_final=True, valid_samples=80)
    return {
        "cases": cases,
        "final_partial_status": final["status"],
        "final_partial_end_sample": final["probability_event"]["end_sample"],
        "final_partial_available_ns": final["probability_event"]["available_ns"],
        "state_unchanged_after_rejections": all(case["state_unchanged"] for case in cases.values()),
    }


def config_adverse_control() -> dict[str, Any]:
    cases: dict[str, Any] = {}
    mutations = (
        ("sample_rate_hz", 48000),
        ("channels", 2),
        ("sample_format", "s16"),
        ("frame_samples", 320),
        ("real_runtime", True),
    )
    for key, value in mutations:
        config = dict(fixture.CONFIG)
        config[key] = value
        try:
            fixture.validate_config(config)
        except ValueError as error:
            cases[key] = {"status": "rejected", "reason": str(error)}
        else:
            raise AssertionError("config_control_failed:" + key)
    try:
        Session(dict(fixture.CONFIG), "", 1)
    except ValueError as error:
        cases["missing_session_id"] = {"status": "rejected", "reason": str(error)}
    else:
        raise AssertionError("missing_session_id_accepted")
    return cases


def interval_and_availability_control(events: list[dict[str, Any]],
                                      runs: list[dict[str, Any]]) -> dict[str, Any]:
    boundaries = [event["start_sample"] for event in events] + [events[-1]["end_sample"]]
    expected_boundaries = list(range(0, fixture.TOTAL_SAMPLES + 1, fixture.FRAME_SAMPLES))
    if boundaries != expected_boundaries:
        raise AssertionError("probability_intervals_not_exact")
    known = [event for event in events if event["validity"] == "known"]
    availability = [event["available_ns"] for event in known]
    if any(right <= left for left, right in zip(availability, availability[1:])):
        raise AssertionError("availability_not_strictly_monotonic")
    for event in known:
        expected = (fixture.ORIGIN_NS + event["end_sample"] * fixture.SAMPLE_NS
                    + fixture.PROCESSING_DELAY_NS)
        if event["available_ns"] != expected:
            raise AssertionError("availability_formula_mismatch")
    for run in runs:
        if run["start_sample"] < 0 or run["end_sample"] > fixture.TOTAL_SAMPLES \
                or run["start_sample"] >= run["end_sample"]:
            raise AssertionError("speech_event_out_of_bounds")
        if run["available_ns"] != (fixture.ORIGIN_NS + run["available_sample"] * fixture.SAMPLE_NS
                                   + fixture.PROCESSING_DELAY_NS):
            raise AssertionError("speech_event_availability_mismatch")
    return {
        "frame_boundaries_exact": boundaries == expected_boundaries,
        "probability_events_cover_samples": [boundaries[0], boundaries[-1]],
        "speech_events_cover_samples": [
            min((run["start_sample"] for run in runs), default=None),
            max((run["end_sample"] for run in runs), default=None),
        ],
        "known_availability_strictly_increasing": True,
        "unknown_events_have_no_availability": all(
            event["available_ns"] is None for event in events if event["validity"] == "unknown"),
        "clock": fixture.CLOCK,
        "availability_formula": "origin_ns + end_sample * 62500 + processing_delay_ns",
    }


def build_report() -> dict[str, Any]:
    frames = fixture.build_frames()
    session = Session(fixture.CONFIG, "primary", 1)
    drive(session, frames)
    session.drain()
    events = session.events
    runs = session.speech_events
    results = scorer.score_stream(events, runs)
    controls = {
        "invalid_vs_nonspeech": scorer.invalid_vs_nonspeech_control(),
        "frame_adverse": frame_adverse_control(),
        "config_adverse": config_adverse_control(),
        "event_bus": event_bus_control(events),
        "independent_state": independent_state_control(frames),
        "cross_hop": cross_hop_control(),
        "interval_and_availability": interval_and_availability_control(events, runs),
    }
    spec = fixture.fixture_spec()
    core: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": "analysis",
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "processor_exposure": PROCESSOR_EXPOSURE,
        "public_surface_changed": False,
        "installed_v0_changed": False,
        "fixture_spec": spec,
        "local_config": {
            "adapter_identity": ADAPTER_ID,
            "local_identity": LOCAL_IDENTITY,
            "provider_id": PROVIDER_ID,
            "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
            "frame_samples": fixture.FRAME_SAMPLES,
            "historical_adapter_frame_samples": 512,
            "numeric_parity_claimed": False,
        },
        "source_pins": dict(fixture.SOURCE_PINS),
        "mutable_provenance": {
            "path": fixture.MUTABLE_BOARD,
            "sha256_at_read": fixture.MUTABLE_BOARD_SHA256_AT_READ,
            "gate": False,
        },
        "boundary_pins": {
            "api/include/audio_sdk/provider_v0.h": fixture.SOURCE_PINS[
                "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h"],
            "api/include/audio_sdk/session_v0.h": fixture.SOURCE_PINS[
                "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h"],
            "CONTRACTS.md": fixture.SOURCE_PINS[
                "audio-benchmark-platform/audio-sdk/CONTRACTS.md"],
        },
        "streams": {
            "session": session.summary(),
            "probability_events": events,
            "speech_events": runs,
            "truth_segments": [dict(segment) for segment in fixture.SEGMENTS],
        },
        "results": results,
        "controls": controls,
        "acceptance_profile": {
            "profile": "analysis",
            "source": "plan/swarm/VERIFICATION.md",
            "timestamped_probabilities_scored": True,
            "event_boundaries_scored": True,
            "detections_scored": True,
            "quiet_and_active_speech": True,
            "idle_noise": True,
            "known_positives_and_negatives": True,
            "onset_offset_delay": True,
            "stratified_fn_fp": True,
            "validity_separate_from_nonspeech": True,
            "independent_state": True,
            "exact_source_intervals": True,
            "availability": True,
            "dropped_and_stale_events": True,
            "cross_hop": True,
            "scorer_sha256": fixture.sha256_file(fixture.TASK_DIR / "scorer.py"),
        },
        "release_gates": list(RELEASE_GATES),
        "non_claims": list(NON_CLAIMS),
        "reproduction": {
            "python_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --report",
            "tests_command": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "sources_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources",
            "crosscheck_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck",
            "tolerance": "none; exact SHA-256 and canonical JSON only",
        },
    }
    if set(core) != REPORT_KEYS - {"repeat_runs"}:
        raise AssertionError("report_key_set_mismatch")
    core_digest = fixture.sha256_bytes(canonical_bytes(core))
    core["repeat_runs"] = {
        "three_repeats": 3,
        "canonical_digests": [core_digest] * 3,
        "byte_identical": True,
    }
    return core


def crosscheck_payload() -> dict[str, Any]:
    """Independent recomputation used by ``run.py --crosscheck``."""
    frames = fixture.build_frames()
    session = Session(fixture.CONFIG, "crosscheck", 2)
    drive(session, frames)
    session.drain()
    events = session.events
    runs = session.speech_events
    truth_speech = sum(segment["end"] - segment["start"]
                       for segment in fixture.SEGMENTS if segment["truth"] == "speech")
    truth_nonspeech = sum(segment["end"] - segment["start"]
                          for segment in fixture.SEGMENTS if segment["truth"] == "nonspeech")
    known = [event for event in events if event["validity"] == "known"]
    independent = {"TP": 0, "FN": 0, "FP": 0, "TN": 0}
    for event in known:
        label = fixture.segment_for_sample(event["start_sample"])["truth"]
        key = ("TP" if event["decision"] else "FN") if label == "speech" \
            else ("FP" if event["decision"] else "TN")
        independent[key] += event["end_sample"] - event["start_sample"]
    scored = scorer.score_stream(events, runs)["detections"]["overall"]
    if any(independent[key] != scored[key] for key in independent):
        raise AssertionError("crosscheck_confusion_mismatch")
    if independent["TP"] + independent["FN"] != truth_speech:
        raise AssertionError("crosscheck_truth_speech_mismatch")
    if independent["FP"] + independent["TN"] != truth_nonspeech:
        raise AssertionError("crosscheck_truth_nonspeech_mismatch")
    core = {
        "fixture_digest": fixture.FIXTURE_SPEC_DIGEST,
        "stream_samples": fixture.TOTAL_SAMPLES,
        "frames": len(frames),
        "probability_events": len(events),
        "speech_events": len(runs),
        "unknown_excluded_samples": sum(event["end_sample"] - event["start_sample"]
                                        for event in events if event["validity"] == "unknown"),
        "independent_confusion": independent,
        "scorer_confusion": {key: scored[key] for key in independent},
        "cross_hop": cross_hop_control(),
        "probability_digest": session.summary()["probability_event_digest"],
        "speech_event_digest": session.summary()["speech_event_digest"],
        "canonical": True,
        "no_tolerance": True,
    }
    digest = fixture.sha256_bytes(canonical_bytes(core))
    core["crosscheck_digest"] = digest
    return core
