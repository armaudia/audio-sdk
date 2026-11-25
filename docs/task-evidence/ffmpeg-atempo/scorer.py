# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Scoring for the synthetic rate acceptance profile.

Every metric is an exact integer or integer-derived proxy over synthetic
waveforms and source-sample clocks.  No metric here is a listening result, a
target-device timing result, or an FFmpeg comparison.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import fixture
import reference

CONSUMER_SAMPLES_PER_TICK = fixture.FRAME_SAMPLES
STALL_TICKS_PER_SOURCE_FRAME = 1


def round_div_signed(numerator: int, denominator: int) -> int:
    return reference.round_div_signed(numerator, denominator)


def mapping_segments(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    schedule = reference.validate_schedule(scenario["rate_schedule"])
    length = int(scenario["length"])
    rows: list[dict[str, Any]] = []
    for index, (start, num, den) in enumerate(schedule):
        end = schedule[index + 1][0] if index + 1 < len(schedule) else length
        out_start = reference.round_fraction(reference.output_position_at(schedule, start))
        out_end = reference.round_fraction(reference.output_position_at(schedule, end))
        rows.append({
            "source_start_sample": start,
            "source_end_sample": end,
            "rate_num": num,
            "rate_den": den,
            "output_start_sample": out_start,
            "output_end_sample": out_end,
            "source_samples": end - start,
            "output_samples": out_end - out_start,
            "duration_error_samples": (out_end - out_start) * num - (end - start) * den,
        })
    return rows


def zero_crossings(samples: list[int] | tuple[int, ...]) -> int:
    return sum(1 for left, right in zip(samples, samples[1:]) if (left < 0) != (right < 0))


def best_lag(samples: list[int] | tuple[int, ...]) -> int:
    """Integer autocorrelation-like lag proxy; no frequency or pitch claim."""
    if len(samples) < 256:
        return 0
    best = -1
    best_cost = None
    for lag in range(48, min(200, len(samples) // 2)):
        cost = 0
        for index in range(0, len(samples) - lag, 4):
            difference = samples[index] - samples[index + lag]
            cost += difference * difference
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = lag
    return best


def pitch_proxy(scenario: dict[str, Any], samples: tuple[int, ...]) -> dict[str, Any]:
    schedule = reference.validate_schedule(scenario["rate_schedule"])
    rows: list[dict[str, Any]] = []
    for segment in scenario["segments"]:
        if not segment["kind"].startswith(("speech", "music")):
            continue
        length = segment["end"] - segment["start"]
        if length < 512:
            continue
        source_start = segment["start"] + (length - 640) // 2
        source_window = list(scenario["samples"][source_start:source_start + 640])
        output_start = reference.round_fraction(
            reference.output_position_at(schedule, source_start))
        output_window = list(samples[output_start:output_start + len(source_window)])
        if len(output_window) < 256:
            continue
        rows.append({
            "kind": segment["kind"],
            "source_start_sample": source_start,
            "output_start_sample": output_start,
            "source_window_samples": len(source_window),
            "output_window_samples": len(output_window),
            "source_zero_crossings": zero_crossings(source_window),
            "output_zero_crossings": zero_crossings(output_window),
            "source_lag_proxy": best_lag(source_window),
            "output_lag_proxy": best_lag(output_window),
        })
    if not rows:
        raise AssertionError("no_pitch_proxy_windows")
    return {
        "method": "integer zero-crossing and lag proxies only; not a pitch measurement",
        "windows": rows,
        "scored": True,
    }


def transient_proxies(scenario: dict[str, Any], samples: tuple[int, ...]) -> dict[str, Any]:
    schedule = reference.validate_schedule(scenario["rate_schedule"])
    rows: list[dict[str, Any]] = []
    for source_position in scenario["transients"]:
        center = reference.round_fraction(reference.output_position_at(schedule, source_position))
        start = max(1, center - 16)
        end = min(len(samples) - 1, center + 16)
        local = max(abs(samples[index + 1] - samples[index]) for index in range(start, end))
        baseline_start = max(1, center - 160)
        baseline_end = min(len(samples) - 1, center + 160)
        jumps = [abs(samples[index + 1] - samples[index])
                 for index in range(baseline_start, baseline_end)
                 if index + 1 < start or index >= end]
        if not jumps:
            raise AssertionError("empty_transient_baseline")
        ordered = sorted(jumps)
        baseline = ordered[len(ordered) // 2]
        rows.append({
            "source_sample": source_position,
            "expected_output_sample": center,
            "local_peak_jump": local,
            "baseline_peak_jump": baseline,
            "jump_ratio_x1000": local * 1000 // max(1, baseline),
        })
    return {
        "method": "integer sample-jump proxy around source-timestamped transients; not audibility",
        "events": rows,
        "scored": True,
    }


def policy_decisions(scenario: dict[str, Any]) -> dict[str, Any]:
    decisions: list[dict[str, Any]] = []
    for segment in scenario["segments"]:
        kind = segment["kind"]
        if kind.startswith(("speech", "music")):
            decision = "retain"
        elif kind == "filler":
            decision = "review_only_filler"
        elif kind == "pause":
            decision = "review_only_pause"
        elif kind == "silence":
            decision = "retain_zero"
        else:
            raise AssertionError("unknown_segment_kind:" + kind)
        decisions.append({
            "source_start_sample": segment["start"],
            "source_end_sample": segment["end"],
            "kind": kind,
            "decision": decision,
            "audio_modified": False,
        })
    previous_end = 0
    honored = True
    for item in decisions:
        if item["source_start_sample"] != previous_end \
                or item["source_end_sample"] <= item["source_start_sample"] \
                or item["source_end_sample"] > int(scenario["length"]):
            honored = False
        if item["kind"].startswith(("speech", "music")) and item["decision"] != "retain":
            honored = False
        previous_end = item["source_end_sample"]
    return {
        "decisions": decisions,
        "source_timestamps_honored": honored and previous_end == int(scenario["length"]),
        "audio_removed_samples": 0,
        "scored": True,
    }


def speech_preservation(scenario: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    schedule = reference.validate_schedule(scenario["rate_schedule"])
    session: reference.RateChange = canonical["session"]
    samples = canonical["samples"]
    rows: list[dict[str, Any]] = []
    for segment in scenario["segments"]:
        if not segment["kind"].startswith(("speech", "music")):
            continue
        start = segment["start"]
        end = segment["end"]
        out_start = reference.round_fraction(reference.output_position_at(schedule, start))
        out_end = reference.round_fraction(reference.output_position_at(schedule, end))
        out_end = min(out_end, len(samples))
        covered = 0
        zero = 0
        for position in range(out_start, out_end):
            if position < len(session.denominators) and session.denominators[position] > 0:
                covered += 1
                if samples[position] == 0:
                    zero += 1
        length = max(1, out_end - out_start)
        exact_1x = None
        if schedule == ((0, 1, 1),):
            exact_1x = list(samples[start:end]) == list(scenario["samples"][start:end])
        rows.append({
            "kind": segment["kind"],
            "source_start_sample": start,
            "source_end_sample": end,
            "output_start_sample": out_start,
            "output_end_sample": out_end,
            "covered_output_samples": covered,
            "coverage_per_mille": covered * 1000 // length,
            "zero_output_samples": zero,
            "exact_at_1x": exact_1x,
        })
    if not rows:
        raise AssertionError("no_speech_segments")
    return {
        "method": "structural coverage and zero-output counts over source-timestamped segments; not listening",
        "segments": rows,
        "no_deleted_speech": all(row["covered_output_samples"] > 0 for row in rows),
        "scored": True,
    }


def playback_buffering(canonical: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = canonical["records"]
    stalls = scenario["stalls"]
    stall_start_call = stalls[0][0] // fixture.FRAME_SAMPLES if stalls else None
    stall_added_ticks = ((stalls[0][1] - stalls[0][0]) // fixture.FRAME_SAMPLES) if stalls else 0

    def emission_tick(record: dict[str, Any]) -> int:
        call = int(record["feed_call_index"])
        if stall_start_call is not None and call >= stall_start_call:
            return call + stall_added_ticks
        return call

    by_tick: dict[int, int] = {}
    for record in records:
        by_tick[emission_tick(record)] = by_tick.get(emission_tick(record), 0) + \
            len(record["samples"])
    last_tick = max(by_tick) if by_tick else 0
    total = sum(by_tick.values())
    occupancy = 0
    underruns = 0
    delivered = 0
    first_output_tick = min(by_tick) if by_tick else None
    max_occupancy = 0
    for tick in range(last_tick + 1):
        occupancy += by_tick.get(tick, 0)
        max_occupancy = max(max_occupancy, occupancy)
        if occupancy == 0:
            underruns += 1
        take = min(CONSUMER_SAMPLES_PER_TICK, occupancy)
        occupancy -= take
        delivered += take
    while occupancy > 0:
        take = min(CONSUMER_SAMPLES_PER_TICK, occupancy)
        occupancy -= take
        delivered += take
    return {
        "model": "synthetic tick model: 160 output samples drained per tick, monotonic source clock",
        "consumer_samples_per_tick": CONSUMER_SAMPLES_PER_TICK,
        "initial_fill_samples": 0,
        "stall_source_interval": stalls[0] if stalls else [],
        "stall_added_ticks": stall_added_ticks,
        "first_output_tick": first_output_tick,
        "underrun_ticks": underruns,
        "max_occupancy_samples": max_occupancy,
        "delivered_samples": delivered,
        "total_output_samples": total,
        "all_output_delivered": delivered == total,
        "scored": True,
    }


def mapping_scenario(scenario: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = canonical["records"]
    firsts = [int(record["source_first_sample"]) for record in records]
    lasts = [int(record["source_last_sample_exclusive"]) for record in records]
    monotonic = all(left <= right for left, right in zip(firsts, firsts[1:]))
    bounded = all(0 <= first <= last <= int(scenario["length"])
                  for first, last in zip(firsts, lasts))
    return {
        "segments": mapping_segments(scenario),
        "first_source_sample": firsts[0] if firsts else 0,
        "last_source_sample_exclusive": lasts[-1] if lasts else 0,
        "frame_source_starts_monotonic": monotonic,
        "frame_source_intervals_in_bounds": bounded,
        "scored": True,
    }


def final_partial_window(scenario: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    session: reference.RateChange = canonical["session"]
    length = int(scenario["length"])
    last_start = ((length - 1) // fixture.ANALYSIS_HOP) * fixture.ANALYSIS_HOP
    partial = [row for row in session.frame_records if row["partial"]]
    final_records = [row for row in canonical["records"] if row["final_output"]]
    return {
        "input_samples": length,
        "last_analysis_frame_source_start": last_start,
        "last_analysis_frame_input_samples": length - last_start,
        "partial_analysis_frames": len(partial),
        "final_output_frames": len(final_records),
        "final_output_frame_samples": sum(len(row["samples"]) for row in final_records),
        "output_samples": len(canonical["samples"]),
        "target_output_samples": canonical["target_length"],
        "has_partial_input_window": bool(length % fixture.ANALYSIS_HOP),
        "scored": True,
    }


def score_scenario(scenario: dict[str, Any], canonical: dict[str, Any],
                   variants: dict[str, dict[str, Any]]) -> dict[str, Any]:
    samples = canonical["samples"]
    target = int(canonical["target_length"])
    error = len(samples) - target
    digests = {name: variants[name]["sample_digest"] for name in fixture.CHUNK_SCHEDULE_NAMES}
    return {
        "name": scenario["name"],
        "source_samples": int(scenario["length"]),
        "source_digest": fixture.samples_digest(scenario["samples"]),
        "target_output_samples": target,
        "actual_output_samples": len(samples),
        "duration_error_samples": error,
        "duration_error_us": round_div_signed(error * 1000, 16),
        "output_digest": fixture.samples_digest(samples),
        "rate_schedule": scenario["rate_schedule"],
        "source_output_mapping": mapping_scenario(scenario, canonical),
        "pitch_preservation_proxy": pitch_proxy(scenario, samples),
        "transient_audibility_proxy": transient_proxies(scenario, samples),
        "pause_filler_policy": policy_decisions(scenario),
        "speech_preservation": speech_preservation(scenario, canonical),
        "playback_buffering": playback_buffering(canonical, scenario),
        "final_partial_window": final_partial_window(scenario, canonical),
        "chunked_vs_single_identity": {
            "schedules": list(fixture.CHUNK_SCHEDULE_NAMES),
            "sample_digests": [digests[name] for name in fixture.CHUNK_SCHEDULE_NAMES],
            "byte_identical": len(set(digests.values())) == 1,
            "scored": True,
        },
    }


def profile_checklist(scenarios: list[dict[str, Any]], controls: list[dict[str, Any]],
                      crosscheck: dict[str, Any]) -> dict[str, Any]:
    by_name = {row["name"]: row for row in scenarios}
    names = set(by_name)
    return {
        "profile": fixture.PROFILE,
        "source_output_mapping_scored": all(
            row["source_output_mapping"]["scored"] for row in scenarios),
        "duration_scored": all(row["duration_error_samples"] == 0 for row in scenarios),
        "pitch_preservation_proxy_scored": all(
            row["pitch_preservation_proxy"]["scored"] for row in scenarios),
        "transient_audibility_proxy_scored": all(
            row["transient_audibility_proxy"]["scored"] for row in scenarios),
        "playback_buffering_scored": all(
            row["playback_buffering"]["scored"] and row["playback_buffering"]["all_output_delivered"]
            for row in scenarios),
        "identity_1x": all(by_name[name]["chunked_vs_single_identity"]["byte_identical"]
                           and all(segment["exact_at_1x"] is not False
                                   for segment in by_name[name]["speech_preservation"]["segments"])
                           for name in ("identity_1x_speech", "silence_filler_1x")),
        "rate_changes": any(any(segment["rate_num"] != segment["rate_den"]
                                for segment in row["source_output_mapping"]["segments"])
                            for row in scenarios),
        "unfamiliar_speech": any(kind.startswith("speech")
                                 for scenario in fixture.SCENARIOS
                                 for kind in (item["kind"] for item in scenario["segments"])),
        "unfamiliar_music": "unfamiliar_music_1_5" in names and "music_slow_0_75" in names,
        "silence": any(item["kind"] == "silence" for scenario in fixture.SCENARIOS
                       for item in scenario["segments"]),
        "rebuffer": "rebuffer_step" in names
        and by_name["rebuffer_step"]["playback_buffering"]["underrun_ticks"] > 0,
        "drift": any(len(scenario["rate_schedule"]) > 1 for scenario in fixture.SCENARIOS),
        "final_partial_window": any(row["final_partial_window"]["has_partial_input_window"]
                                    and row["final_partial_window"]["partial_analysis_frames"] > 0
                                    for row in scenarios),
        "pause_filler_source_timestamps": all(
            row["pause_filler_policy"]["source_timestamps_honored"] for row in scenarios),
        "speech_preservation": all(row["speech_preservation"]["no_deleted_speech"]
                                   for row in scenarios),
        "chunked_vs_single_identity": all(
            row["chunked_vs_single_identity"]["byte_identical"] for row in scenarios)
        and crosscheck["all_chunk_identical"],
        "reset_replay_behavior": crosscheck["reset_replay"]["matches_baseline"]
        and crosscheck["reset_replay"]["stale_epoch_rejected"],
        "validity_controls": len(controls) > 0
        and all(item["rejected"] for item in controls),
        "missing_result_promoted": False,
        "scorer_sha256": fixture.sha256_file(fixture.TASK_DIR / "scorer.py"),
    }
