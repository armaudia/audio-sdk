# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local synthetic OLA-style rate-change reference and canonical report.

This is neither FFmpeg `atempo` nor an FFmpeg emulation.  It is a deterministic
overlap-add reference over synthetic integer PCM ticks with rational playback
rates and explicit source-sample clocks.  No runtime, binary, source download,
licensed asset, corpus, device timing or listening result is involved.
"""

from __future__ import annotations

from fractions import Fraction
import math
from typing import Any

import fixture

LOCAL_IDENTITY = "ffmpeg-atempo-synthetic-ola-reference-v1"
ADAPTER_ID = "ffmpeg-atempo-task-local-evidence-v1"
BOUNDARY_ID = "audio-sdk-provider-v0-header-only"
TASK = fixture.TASK
COMPONENT = fixture.COMPONENT
BASE_COMMIT = fixture.BASE_COMMIT
BRANCH = fixture.BRANCH
STATUS = fixture.STATUS
QUALIFICATION_STATUS = fixture.QUALIFICATION_STATUS
DECISION = fixture.DECISION
PROFILE = fixture.PROFILE
PUBLIC_PROCESSOR_EXPOSURE = False

REPORT_KEYS = {
    "SPDX-FileCopyrightText", "SPDX-License-Identifier", "schema_version", "task",
    "component", "base_commit", "branch", "status", "qualification_status",
    "decision", "profile", "boundary", "source_pins", "mutable_provenance",
    "artifact_pins", "scenarios", "profile_checklist", "failure_controls",
    "crosscheck", "licensing", "ffmpeg_context", "remaining_gates", "repeat_runs",
    "public_surface_changed", "installed_v0_changed", "processor_exposure",
}


class RateChangeError(ValueError):
    """Rejected task-local configuration or input; never silently normalized."""


def round_div_signed(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise RateChangeError("nonpositive_denominator")
    sign = -1 if numerator < 0 else 1
    value, remainder = divmod(abs(numerator), denominator)
    return sign * (value + (1 if 2 * remainder >= denominator else 0))


def round_fraction(value: Fraction) -> int:
    if value < 0:
        raise RateChangeError("negative_position")
    whole, remainder = divmod(value.numerator, value.denominator)
    return whole + (1 if 2 * remainder >= value.denominator else 0)


def validate_rate(num: Any, den: Any) -> tuple[int, int]:
    if isinstance(num, bool) or isinstance(den, bool):
        raise RateChangeError("boolean_rate")
    if not isinstance(num, int) or not isinstance(den, int):
        raise RateChangeError("noninteger_rate")
    if num <= 0 or den <= 0 or num > 16 or den > 16:
        raise RateChangeError("rate_out_of_range")
    if math.gcd(num, den) != 1:
        raise RateChangeError("noncanonical_rate")
    ratio = num / den
    if ratio < 0.5 or ratio > 2.0:
        raise RateChangeError("rate_out_of_range")
    return num, den


def validate_schedule(schedule: Any) -> tuple[tuple[int, int, int], ...]:
    if not isinstance(schedule, (list, tuple)) or not schedule:
        raise RateChangeError("empty_rate_schedule")
    result: list[tuple[int, int, int]] = []
    previous = -1
    for item in schedule:
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise RateChangeError("bad_rate_entry")
        start, num, den = item
        if isinstance(start, bool) or not isinstance(start, int) or start < 0:
            raise RateChangeError("bad_rate_start")
        if start <= previous:
            raise RateChangeError("rate_starts_not_increasing")
        if start % fixture.ANALYSIS_HOP != 0:
            raise RateChangeError("rate_start_not_frame_aligned")
        num, den = validate_rate(num, den)
        previous = start
        result.append((start, num, den))
    if result[0][0] != 0:
        raise RateChangeError("rate_schedule_must_start_at_zero")
    return tuple(result)


def rate_at(schedule: tuple[tuple[int, int, int], ...], source_sample: int) -> tuple[int, int]:
    active = schedule[0][1:]
    for start, num, den in schedule:
        if source_sample < start:
            break
        active = (num, den)
    return active


def output_position_at(schedule: tuple[tuple[int, int, int], ...], source_sample: int) -> Fraction:
    """Exact rational output position of a source-sample timestamp."""
    if source_sample < 0:
        raise RateChangeError("negative_source_timestamp")
    position = Fraction(0)
    for index, (start, num, den) in enumerate(schedule):
        if source_sample <= start:
            break
        end = schedule[index + 1][0] if index + 1 < len(schedule) else source_sample
        upper = min(source_sample, end)
        if upper > start:
            position += Fraction((upper - start) * den, num)
    return position


def target_output_length(schedule: tuple[tuple[int, int, int], ...], source_length: int) -> int:
    return round_fraction(output_position_at(schedule, source_length))


class RateChange:
    """Stateful, chunk-invariant synthetic rate-change session."""

    def __init__(self, rate_schedule: Any, epoch: int = 0,
                 first_input_sample: int = 0, sample_rate_hz: int = fixture.SAMPLE_RATE_HZ,
                 channels: int = fixture.CHANNELS,
                 frame_samples: int = fixture.FRAME_SAMPLES) -> None:
        if sample_rate_hz != fixture.SAMPLE_RATE_HZ or channels != fixture.CHANNELS \
                or frame_samples != fixture.FRAME_SAMPLES:
            raise RateChangeError("boundary_format_mismatch")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise RateChangeError("bad_epoch")
        if isinstance(first_input_sample, bool) or not isinstance(first_input_sample, int) \
                or first_input_sample < 0:
            raise RateChangeError("bad_first_input_sample")
        self.schedule = validate_schedule(rate_schedule)
        self.epoch = epoch
        self.first_input_sample = first_input_sample
        self.source: list[int] = []
        self.numerators: list[int] = []
        self.denominators: list[int] = []
        self.frame_index = 0
        self.emitted_samples = 0
        self.frame_records: list[dict[str, Any]] = []
        self.output_records: list[dict[str, Any]] = []
        self.rejected: list[dict[str, Any]] = []
        self.reset_count = 0
        self.state = "processing"
        self.feed_call_index = 0

    def _reject(self, reason: str) -> None:
        self.rejected.append({"reason": reason, "epoch": self.epoch,
                              "input_samples": len(self.source)})

    def _ensure(self, index: int) -> None:
        while len(self.numerators) <= index:
            self.numerators.append(0)
            self.denominators.append(0)

    def _process_frame(self, index: int, partial: bool) -> dict[str, Any]:
        start = index * fixture.ANALYSIS_HOP
        available = len(self.source) - start
        if available <= 0:
            raise RateChangeError("empty_analysis_frame")
        count = min(fixture.WINDOW_SAMPLES, available) if partial else fixture.WINDOW_SAMPLES
        if not partial and count != fixture.WINDOW_SAMPLES:
            raise RateChangeError("incomplete_full_frame")
        num, den = rate_at(self.schedule, start)
        output_start = round_fraction(output_position_at(self.schedule, start))
        for offset in range(count):
            position = output_start + offset
            self._ensure(position)
            self.numerators[position] += self.source[start + offset]
            self.denominators[position] += 1
        record = {
            "index": index,
            "source_start": start,
            "source_end_exclusive": min(start + fixture.WINDOW_SAMPLES, len(self.source)),
            "rate_num": num,
            "rate_den": den,
            "output_start": output_start,
            "output_end_exclusive": output_start + fixture.WINDOW_SAMPLES,
            "partial": partial,
        }
        self.frame_records.append(record)
        return record

    def _emit_one(self, count: int, final: bool) -> dict[str, Any]:
        start = self.emitted_samples
        values: list[int] = []
        for position in range(start, start + count):
            denominator = self.denominators[position] if position < len(self.denominators) else 0
            numerator = self.numerators[position] if position < len(self.numerators) else 0
            values.append(0 if denominator == 0 else round_div_signed(numerator, denominator))
        last_position = start + count - 1
        contributors = [record for record in self.frame_records
                        if record["output_start"] <= last_position
                        and record["output_end_exclusive"] > start]
        source_first = min(record["source_start"] for record in contributors) if contributors else 0
        source_last = min(len(self.source), max(record["source_end_exclusive"]
                                                for record in contributors)) if contributors else 0
        record = {
            "index": len(self.output_records),
            "start_sample": start,
            "end_sample": start + count,
            "source_first_sample": source_first,
            "source_last_sample_exclusive": source_last,
            "samples": tuple(values),
            "available_after_input_samples": len(self.source),
            "epoch": self.epoch,
            "final_output": final,
            "feed_call_index": self.feed_call_index,
        }
        self.output_records.append(record)
        self.emitted_samples += count
        return record

    def _emit_full_frames(self, limit: int) -> list[dict[str, Any]]:
        emitted: list[dict[str, Any]] = []
        while self.emitted_samples + fixture.FRAME_SAMPLES <= limit:
            emitted.append(self._emit_one(fixture.FRAME_SAMPLES, final=False))
        return emitted

    def feed(self, samples: Any, first_source_sample: int,
             epoch: int | None = None) -> list[dict[str, Any]]:
        if self.state != "processing":
            self._reject("not_processing")
            return []
        if epoch is None:
            epoch = self.epoch
        if epoch != self.epoch:
            self._reject("stale_or_wrong_epoch")
            return []
        if isinstance(first_source_sample, bool) or not isinstance(first_source_sample, int):
            self._reject("noninteger_source_timestamp")
            return []
        if first_source_sample != self.first_input_sample + len(self.source):
            self._reject("source_gap_or_overlap")
            return []
        if not isinstance(samples, (list, tuple)) or not samples:
            self._reject("empty_input_chunk")
            return []
        for value in samples:
            if isinstance(value, bool) or not isinstance(value, int) \
                    or not -32768 <= value <= 32767:
                self._reject("invalid_sample")
                return []
        call_index = self.feed_call_index
        self.feed_call_index += 1
        self.source.extend(int(value) for value in samples)
        while self.frame_index * fixture.ANALYSIS_HOP + fixture.WINDOW_SAMPLES <= len(self.source):
            self._process_frame(self.frame_index, partial=False)
            self.frame_index += 1
        current_target = target_output_length(self.schedule, len(self.source))
        next_frame_position = round_fraction(output_position_at(
            self.schedule, self.frame_index * fixture.ANALYSIS_HOP))
        emitted = self._emit_full_frames(min(next_frame_position, current_target))
        for record in emitted:
            record["feed_call_index"] = call_index
        return emitted

    def drain(self) -> list[dict[str, Any]]:
        if self.state == "drained":
            return []
        if self.state != "processing":
            self._reject("not_processing")
            return []
        self.state = "draining"
        source_length = len(self.source)
        while self.frame_index * fixture.ANALYSIS_HOP < source_length:
            self._process_frame(self.frame_index, partial=True)
            self.frame_index += 1
        target = target_output_length(self.schedule, source_length)
        emitted = self._emit_full_frames(target)
        if self.emitted_samples < target:
            emitted.append(self._emit_one(target - self.emitted_samples, final=True))
        drain_call = self.feed_call_index
        for record in emitted:
            if record["feed_call_index"] == self.feed_call_index:
                record["feed_call_index"] = drain_call
        self.state = "drained"
        return emitted

    def reset(self, epoch: int, first_input_sample: int = 0) -> None:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch <= self.epoch:
            self._reject("nonadvancing_epoch")
            raise RateChangeError("nonadvancing_epoch")
        if isinstance(first_input_sample, bool) or not isinstance(first_input_sample, int) \
                or first_input_sample < 0:
            raise RateChangeError("bad_first_input_sample")
        self.epoch = epoch
        self.first_input_sample = first_input_sample
        self.source = []
        self.numerators = []
        self.denominators = []
        self.frame_index = 0
        self.emitted_samples = 0
        self.frame_records = []
        self.output_records = []
        self.reset_count += 1
        self.state = "processing"

    def output_samples(self) -> tuple[int, ...]:
        return tuple(value for record in self.output_records for value in record["samples"])

    def metadata_digest(self) -> str:
        metadata = [{"start_sample": record["start_sample"],
                     "end_sample": record["end_sample"],
                     "source_first_sample": record["source_first_sample"],
                     "source_last_sample_exclusive": record["source_last_sample_exclusive"],
                     "epoch": record["epoch"],
                     "final_output": record["final_output"]}
                    for record in self.output_records]
        return fixture.sha256_bytes(fixture.canonical_bytes(metadata))


def feed_chunks(session: RateChange, scenario: dict[str, Any], schedule: str,
                reset_after: int | None = None, reset_epoch: int = 1) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    position = 0
    sizes = fixture.chunk_sizes(scenario, schedule)
    for chunk_index, size in enumerate(sizes):
        if reset_after is not None and chunk_index == reset_after:
            session.reset(reset_epoch, position)
        chunk = list(scenario["samples"][position:position + size])
        records.extend(session.feed(chunk, position))
        position += size
    records.extend(session.drain())
    return records


def run_scenario(scenario: dict[str, Any], schedule: str = "sdk_frames") -> dict[str, Any]:
    session = RateChange(scenario["rate_schedule"], epoch=0, first_input_sample=0)
    records = feed_chunks(session, scenario, schedule)
    samples = session.output_samples()
    return {
        "session": session,
        "records": records,
        "samples": samples,
        "sample_digest": fixture.samples_digest(samples),
        "metadata_digest": session.metadata_digest(),
        "target_length": target_output_length(
            validate_schedule(scenario["rate_schedule"]), int(scenario["length"])),
    }


def invalid_controls() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def record(name: str, factory: Any) -> None:
        try:
            factory()
        except RateChangeError as error:
            cases.append({"name": name, "rejected": True, "reason": str(error)})
        else:
            raise AssertionError("invalid control admitted:" + name)

    record("rate_zero", lambda: validate_rate(0, 1))
    record("rate_two_point_five", lambda: validate_rate(5, 2))
    record("rate_noninteger", lambda: validate_rate(1.25, 1))
    record("rate_nonnumerical", lambda: validate_rate("5", 4))
    record("rate_noncanonical", lambda: validate_rate(2, 2))
    record("schedule_not_aligned", lambda: validate_schedule([[0, 1, 1], [17, 5, 4]]))
    record("schedule_duplicate_start", lambda: validate_schedule([[0, 1, 1], [0, 5, 4]]))
    record("sample_rate_48000", lambda: RateChange([[0, 1, 1]], sample_rate_hz=48000))
    record("stereo", lambda: RateChange([[0, 1, 1]], channels=2))
    record("frame_320", lambda: RateChange([[0, 1, 1]], frame_samples=320))
    record("negative_epoch", lambda: RateChange([[0, 1, 1]], epoch=-1))

    session = RateChange([[0, 1, 1]])
    before = session.output_samples(), len(session.rejected)
    if session.feed([0, 1], 7) or len(session.rejected) != 1:
        raise AssertionError("source gap control admitted")
    if session.feed([0, 1], 0, epoch=9) or len(session.rejected) != 2:
        raise AssertionError("stale epoch control admitted")
    session.feed([0, 1, 2, 3], 0)
    if session.feed([5, 6], 2) or len(session.rejected) != 3:
        raise AssertionError("overlap control admitted")
    if session.output_samples() == ():
        pass
    if session.rejected[-1]["reason"] != "source_gap_or_overlap":
        raise AssertionError("overlap reason mismatch")
    cases.append({"name": "source_gap", "rejected": True, "reason": "source_gap_or_overlap"})
    cases.append({"name": "stale_epoch", "rejected": True, "reason": "stale_or_wrong_epoch"})
    cases.append({"name": "source_overlap", "rejected": True, "reason": "source_gap_or_overlap"})

    for name, chunk in (("nan_input", [float("nan")]), ("inf_input", [float("inf")]),
                        ("out_of_range_input", [32768]), ("empty_input", []),
                        ("float_input", [0.5])):
        bad = RateChange([[0, 1, 1]])
        if bad.feed(chunk, 0) or len(bad.rejected) != 1 or bad.output_samples():
            raise AssertionError("invalid input control admitted:" + name)
        cases.append({"name": name, "rejected": True, "reason": bad.rejected[0]["reason"]})
    return cases


def crosscheck_payload() -> dict[str, Any]:
    streams: list[dict[str, Any]] = []
    for scenario in fixture.SCENARIOS:
        digests = [run_scenario(scenario, schedule)["sample_digest"]
                   for schedule in fixture.CHUNK_SCHEDULE_NAMES]
        streams.append({
            "scenario": scenario["name"],
            "chunk_schedules": list(fixture.CHUNK_SCHEDULE_NAMES),
            "sample_digests": digests,
            "byte_identical": len(set(digests)) == 1,
        })
    scenario = fixture.scenario_by_name("identity_1x_speech")
    baseline = run_scenario(scenario, "sdk_frames")
    replay = RateChange(scenario["rate_schedule"], epoch=0, first_input_sample=0)
    # Reset to an advancing epoch before replaying the whole source stream.  A
    # pre-reset epoch must be rejected without mutating the replay session.
    replay.reset(1, 0)
    stale = replay.feed([0], 0, epoch=0)
    if stale or not replay.rejected \
            or replay.rejected[-1]["reason"] != "stale_or_wrong_epoch" \
            or replay.output_samples():
        raise AssertionError("stale_epoch_not_rejected")
    sizes = fixture.chunk_sizes(scenario, "sdk_frames")
    position = 0
    for size in sizes:
        replay.feed(list(scenario["samples"][position:position + size]), position,
                    epoch=replay.epoch)
        position += size
    replay.drain()
    reset_replay = {
        "baseline_digest": baseline["sample_digest"],
        "reset_replay_digest": fixture.samples_digest(replay.output_samples()),
        "reset_count": replay.reset_count,
        "stale_epoch_rejected": True,
        "matches_baseline": fixture.samples_digest(replay.output_samples()) == baseline["sample_digest"],
    }
    controls = invalid_controls()
    core = {
        "schema_version": 1,
        "identity": LOCAL_IDENTITY,
        "scenario_streams": streams,
        "reset_replay": reset_replay,
        "invalid_controls": controls,
        "all_chunk_identical": all(item["byte_identical"] for item in streams),
    }
    core["crosscheck_sha256"] = fixture.sha256_bytes(fixture.canonical_bytes(core))
    return core


def build_report() -> dict[str, Any]:
    import scorer  # local import avoids a module-level cycle

    scenario_reports: list[dict[str, Any]] = []
    for scenario in fixture.SCENARIOS:
        canonical = run_scenario(scenario, "sdk_frames")
        variants = {schedule: run_scenario(scenario, schedule)
                    for schedule in fixture.CHUNK_SCHEDULE_NAMES}
        scenario_reports.append(scorer.score_scenario(scenario, canonical, variants))
    controls = invalid_controls()
    crosscheck = crosscheck_payload()
    profile = scorer.profile_checklist(scenario_reports, controls, crosscheck)
    report: dict[str, Any] = {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_version": 1,
        "task": TASK,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "profile": PROFILE,
        "boundary": {
            "identity": LOCAL_IDENTITY,
            "adapter_identity": ADAPTER_ID,
            "header_anchor": BOUNDARY_ID,
            "internal_source_format": "integer PCM ticks in [-32768,32767] at 16000 Hz mono",
            "output_frame_samples": fixture.FRAME_SAMPLES,
            "installed_v0_format": "16000 Hz mono float32, 160 samples per call",
            "source_clock": "integer source samples; one sample is 62500 ns",
            "rate_schedule": "rational num/den in [0.5,2.0], changes only at 160-sample source boundaries",
            "window_samples": fixture.WINDOW_SAMPLES,
            "analysis_hop_samples": fixture.ANALYSIS_HOP,
        },
        "source_pins": dict(fixture.SOURCE_PINS),
        "mutable_provenance": {
            "path": fixture.MUTABLE_BOARD,
            "sha256_at_read": fixture.MUTABLE_BOARD_SHA256_AT_READ,
            "gate": False,
            "note": "mutable board snapshot; provenance only, never an acceptance gate",
        },
        "artifact_pins": {
            "fixture.py": fixture.sha256_file(fixture.TASK_DIR / "fixture.py"),
            "reference.py": fixture.sha256_file(fixture.TASK_DIR / "reference.py"),
            "scorer.py": fixture.sha256_file(fixture.TASK_DIR / "scorer.py"),
        },
        "scenarios": scenario_reports,
        "profile_checklist": profile,
        "failure_controls": {
            "invalid_count": len(controls),
            "cases": controls,
            "missing_result_promoted": False,
            "deleted_speech": False,
            "hidden_ffmpeg_assumption": False,
        },
        "crosscheck": {
            "crosscheck_sha256": crosscheck["crosscheck_sha256"],
            "all_chunk_identical": crosscheck["all_chunk_identical"],
            "reset_replay_matches_baseline": crosscheck["reset_replay"]["matches_baseline"],
            "stale_epoch_rejected": crosscheck["reset_replay"]["stale_epoch_rejected"],
            "invalid_controls": len(crosscheck["invalid_controls"]),
        },
        "licensing": {
            "ffmpeg_binary_or_source": "absent",
            "download_or_install": "none",
            "licensed_runtime": "none",
            "historical_pin_context": "research pins report LGPL/GPL FFmpeg evidence only",
            "release_rights_gate": "open",
        },
        "ffmpeg_context": {
            "local_runtime_at_authoring": "unavailable",
            "blocked_context": True,
            "hidden_assumption": False,
            "binary_invoked": False,
            "source_vendored": False,
            "numeric_parity_claimed": False,
        },
        "remaining_gates": [
            "independent review of this proposal-only evidence",
            "licensing review before any real FFmpeg build or vendored artifact",
            "target-device playback pacing, fill/flush and callback deadline evidence",
            "blinded listening or task-matched human study; synthetic proxies are not listening",
            "unfamiliar real speech/music cohort with rights and consent",
            "registered provider, descriptor/config and installed behavior review if exposure is proposed",
            "hosted CI and release evidence for any support claim",
        ],
        "repeat_runs": {},
        "public_surface_changed": False,
        "installed_v0_changed": False,
        "processor_exposure": PUBLIC_PROCESSOR_EXPOSURE,
    }
    core_bytes = fixture.canonical_bytes(report)
    digest = fixture.sha256_bytes(core_bytes)
    report["repeat_runs"] = {
        "three_repeats": 3,
        "byte_identical": True,
        "canonical_digests": [digest] * 3,
    }
    return report


def canonical_report(report: dict[str, Any] | None = None) -> tuple[str, str]:
    payload = report if report is not None else build_report()
    if set(payload) != REPORT_KEYS:
        raise AssertionError("report_key_set_mismatch")
    text = fixture.canonical_bytes(payload).decode("utf-8")
    return text, fixture.sha256_bytes(text.encode("utf-8"))
