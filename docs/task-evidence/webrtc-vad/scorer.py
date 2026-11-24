# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Analysis-profile scorer for the synthetic VAD reference.

Scores timestamped probabilities, detection decisions on exact source
intervals, and speech-event boundaries.  Invalid records are rejected rather
than relabeled as nonspeech; unknown records are admitted to the audit but
excluded from every scoring denominator.
"""

from __future__ import annotations

import math
from typing import Any

import fixture


def project_interval(start: int, end: int, frame_samples: int = fixture.FRAME_SAMPLES
                     ) -> list[tuple[int, int]]:
    """Exact half-open source interval projected onto 160-sample hops."""
    if (isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int)
            or not isinstance(end, int) or start < 0 or end <= start
            or isinstance(frame_samples, bool) or not isinstance(frame_samples, int)
            or frame_samples <= 0):
        raise ValueError("invalid_projection_interval")
    first = start // frame_samples
    last = (end - 1) // frame_samples
    return [
        (index, min(end, (index + 1) * frame_samples) - max(start, index * frame_samples))
        for index in range(first, last + 1)
    ]


def _validate(events: list[dict[str, Any]]) -> None:
    for event in events:
        if event.get("validity") not in ("known", "unknown"):
            raise ValueError("invalid_event_not_scoreable:" + str(event.get("validity")))
        probability = event.get("probability")
        if isinstance(probability, bool) or not isinstance(probability, (int, float)) \
                or not math.isfinite(float(probability)) or not 0.0 <= float(probability) <= 1.0:
            raise ValueError("nonfinite_or_out_of_range_probability")
        start, end = event.get("start_sample"), event.get("end_sample")
        if (isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int)
                or not isinstance(end, int) or start < 0 or end <= start
                or end > fixture.TOTAL_SAMPLES):
            raise ValueError("invalid_event_interval")
        if event.get("decision") not in (True, False, None):
            raise ValueError("invalid_event_decision")
        if event["validity"] == "known" and event.get("decision") is None:
            raise ValueError("missing_known_decision")


def _weighted_mean(values: list[tuple[float, int]]) -> float:
    total_weight = sum(weight for _, weight in values)
    if total_weight == 0:
        raise ValueError("empty_denominator")
    return round(sum(value * weight for value, weight in values) / total_weight, 12)


def _merge_runs(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _boundary_result(truth_runs: list[tuple[int, int]],
                     detected_runs: list[tuple[int, int]]) -> dict[str, Any]:
    used: set[int] = set()
    matches: list[dict[str, Any]] = []
    for truth in truth_runs:
        scored = []
        for index, detected in enumerate(detected_runs):
            if index in used:
                continue
            overlap = min(truth[1], detected[1]) - max(truth[0], detected[0])
            scored.append((max(0, overlap), index, detected))
        overlap, index, detected = max(scored, default=(0, -1, None))
        if overlap == 0 or detected is None:
            matches.append({"truth": list(truth), "detected": None, "overlap_samples": 0,
                            "onset_delay_samples": None, "offset_delay_samples": None,
                            "onset_delay_ms": None, "offset_delay_ms": None,
                            "matched": False})
            continue
        used.add(index)
        onset = detected[0] - truth[0]
        offset = detected[1] - truth[1]
        matches.append({
            "truth": list(truth), "detected": list(detected), "overlap_samples": overlap,
            "onset_delay_samples": onset, "offset_delay_samples": offset,
            "onset_delay_ms": round(onset / 16.0, 6),
            "offset_delay_ms": round(offset / 16.0, 6),
            "matched": True,
        })
    missed = [list(truth) for index, truth in enumerate(truth_runs)
              if not matches[index]["matched"]]
    false_runs = [list(detected) for index, detected in enumerate(detected_runs)
                  if index not in used]
    return {
        "truth_runs": [list(run) for run in truth_runs],
        "detected_runs": [list(run) for run in detected_runs],
        "matches": matches,
        "missed_truth_runs": missed,
        "false_detected_runs": false_runs,
        "matched_count": sum(1 for match in matches if match["matched"]),
        "sign_convention": "positive onset delay = late start; negative offset delay = early stop",
    }


def score_stream(events: list[dict[str, Any]], runs: list[dict[str, Any]]) -> dict[str, Any]:
    _validate(events)
    known = [event for event in events if event["validity"] == "known"]
    unknown = [event for event in events if event["validity"] == "unknown"]
    if not known:
        raise ValueError("empty_known_denominator")
    scored_samples = sum(event["end_sample"] - event["start_sample"] for event in known)
    unknown_samples = sum(event["end_sample"] - event["start_sample"] for event in unknown)

    brier_terms: list[tuple[float, int]] = []
    log_terms: list[tuple[float, int]] = []
    probability_terms: list[tuple[float, int]] = []
    confusion = {"TP": 0, "FN": 0, "FP": 0, "TN": 0}
    strata: dict[str, dict[str, Any]] = {}
    for event in known:
        segment = fixture.segment_for_sample(event["start_sample"])
        truth = segment["truth"]
        probability = float(event["probability"])
        weight = event["end_sample"] - event["start_sample"]
        label = 1.0 if truth == "speech" else 0.0
        brier_terms.append(((probability - label) ** 2, weight))
        clipped = min(max(probability, 1e-12), 1.0 - 1e-12)
        log_terms.append((-(label * math.log(clipped) + (1.0 - label) * math.log(1.0 - clipped)),
                          weight))
        probability_terms.append((probability, weight))
        key = ("TP" if event["decision"] else "FN") if truth == "speech" \
            else ("FP" if event["decision"] else "TN")
        confusion[key] += weight
        row = strata.setdefault(segment["id"], {
            "condition": segment["condition"], "truth": truth, "events": 0, "samples": 0,
            "TP": 0, "FN": 0, "FP": 0, "TN": 0, "_probability_terms": [],
        })
        row["events"] += 1
        row["samples"] += weight
        row[key] += weight
        row["_probability_terms"].append((probability, weight))
    for row in strata.values():
        row["mean_probability"] = _weighted_mean(row.pop("_probability_terms"))

    speech = confusion["TP"] + confusion["FN"]
    nonspeech = confusion["FP"] + confusion["TN"]
    if speech == 0 or nonspeech == 0:
        raise ValueError("missing_known_denominator")
    truth_runs = _merge_runs(fixture.truth_intervals("speech"))
    detected_runs = _merge_runs([(run["start_sample"], run["end_sample"]) for run in runs])
    return {
        "probabilities": {
            "known_events": len(known),
            "scored_samples": scored_samples,
            "brier_score": _weighted_mean(brier_terms),
            "log_loss": _weighted_mean(log_terms),
            "mean_probability": _weighted_mean(probability_terms),
            "by_condition": strata,
        },
        "detections": {
            "overall": confusion,
            "speech_samples": speech,
            "nonspeech_samples": nonspeech,
            "speech_miss_rate": round(confusion["FN"] / speech, 12),
            "false_alarm_rate": round(confusion["FP"] / nonspeech, 12),
            "strata": strata,
            "unknown_excluded_samples": unknown_samples,
            "invalid_excluded_samples": 0,
        },
        "boundaries": _boundary_result(truth_runs, detected_runs),
        "validity": {
            "known_events": len(known),
            "unknown_events": len(unknown),
            "invalid_events_admitted": 0,
            "invalid_never_relabeled_nonspeech": True,
            "scored_samples_plus_unknown": scored_samples + unknown_samples,
        },
    }


def invalid_vs_nonspeech_control() -> dict[str, Any]:
    """Invalid records are rejected; unknown records are excluded, not negative."""
    base = {"event_type": "speech_probability", "session_id": "validity-control", "epoch": 1,
            "sequence": 1, "start_sample": 0, "end_sample": fixture.FRAME_SAMPLES,
            "probability": 0.9, "decision": True, "available_ns": fixture.ORIGIN_NS,
            "clock": fixture.CLOCK}
    nonspeech = dict(base, probability=0.1, decision=False, validity="known")
    unknown = dict(base, sequence=2, validity="unknown", decision=None, available_ns=None)
    speech = dict(base, sequence=7, validity="known", probability=0.9, decision=True,
                  start_sample=800, end_sample=960)
    cases: dict[str, Any] = {}
    for name, event in (
        ("invalid_validity", dict(base, sequence=3, validity="invalid")),
        ("missing_validity", dict(base, sequence=4, validity="missing")),
        ("nonfinite_probability", dict(base, sequence=5, validity="known",
                                       probability=float("nan"))),
        ("out_of_range_probability", dict(base, sequence=6, validity="known",
                                          probability=2.0)),
    ):
        try:
            score_stream([nonspeech, event], [])
        except ValueError as error:
            cases[name] = {"status": "rejected", "reason": str(error)}
        else:
            raise AssertionError("scorer_admitted_invalid:" + name)
    result = score_stream([nonspeech, speech, unknown], [])
    if result["detections"]["overall"]["FP"] != 0 \
            or result["detections"]["overall"]["TP"] != fixture.FRAME_SAMPLES \
            or result["detections"]["unknown_excluded_samples"] != fixture.FRAME_SAMPLES \
            or result["detections"]["overall"]["TN"] != fixture.FRAME_SAMPLES:
        raise AssertionError("unknown_was_scored_as_nonspeech")
    return {
        "rejected_cases": cases,
        "unknown_event_admitted": True,
        "unknown_excluded_samples": fixture.FRAME_SAMPLES,
        "known_nonspeech_tn": fixture.FRAME_SAMPLES,
        "known_speech_tp": fixture.FRAME_SAMPLES,
        "false_positives": 0,
        "invalid_counted_as_nonspeech": False,
    }
