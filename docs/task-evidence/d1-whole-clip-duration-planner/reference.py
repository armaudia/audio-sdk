"""Offline D1 whole-clip duration planner reference (proposal only).

This module models the D1 rule reported in
``cpp-library/pipeline-validation/playback-speed/README.md``: protected speech
blocks are slowed uniformly, silence/filler blocks pay for the slowdown at no
more than 1.5x, and the planned playback duration must equal the source
duration exactly. It emits rational source-to-playback maps, not audio. It is
not a provider, actuator, resampler, device measurement or qualification
result.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

IDENTITY = "d1-whole-clip-duration-planner-reference"
CONTROL = "d1_whole_clip_duration_planner_reference"
BOUNDARY_IDENTITY = "harness-controls-v1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
BLOCK_SAMPLES = 1600
NS_PER_SAMPLE = 62500

PROTECTED_LABELS = ("speech", "speech_like", "music")
FLEX_LABELS = ("silence", "filler")
LABELS = PROTECTED_LABELS + FLEX_LABELS

FLOOR = Fraction(4, 5)
SPEECH_CEILING = Fraction(1, 1)
FLEX_CEILING = Fraction(3, 2)
FIXED_CONTROL_RATE = Fraction(5, 4)

VARIANTS = (
    "d1",
    "1x",
    "fixed_125",
    "slow_only",
    "oracle_labels",
    "drift_uncompensated",
    "rebuffer_uncompensated",
    "oracle_compensated",
)

CONFIG_KEYS = {
    "control", "sample_rate_hz", "channels", "sample_format", "sdk_frame_samples",
    "block_samples", "speech_floor", "speech_ceiling", "flex_ceiling",
}
BLOCK_KEYS = {"source_first_sample", "source_end_sample", "label", "material"}
CASE_KEYS = {
    "case_id", "material", "blocks", "events", "note",
    "recorded_slow_floor", "recorded_note", "variants",
}
DRIFT_KEYS = {"kind", "start_sample", "end_sample", "scale_num", "scale_den", "note"}
REBUFFER_KEYS = {"kind", "at_sample", "gap_ns", "note"}

PITCH_NOT_MEASURED = {
    "status": "not_measured",
    "qualifies": False,
    "reason": "offline rate schedule only; no stretched waveform or actuator is produced",
}
TRANSIENT_NOT_MEASURED = {
    "status": "not_measured",
    "qualifies": False,
    "reason": "offline rate schedule only; no time-stretched transient audio is produced",
}
BUFFERING_SEMANTICS = {
    "mode": "offline_whole_clip",
    "plan_available_after_source_samples": "total_samples",
    "first_output_before_full_clip": False,
    "fill_flush_measured": False,
    "device_pacing_measured": False,
    "actuator_installed": False,
    "note": "whole-clip lookahead is a planning dependency, not a measured streaming latency",
}


def canonical_bytes(value: Any) -> bytes:
    """Canonical UTF-8 JSON used for every digest in this evidence bundle."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_int(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int)


def frac(value: Any) -> Fraction:
    """Parse an exact rational supplied as an integer or canonical string."""
    if isinstance(value, bool):
        raise ValueError("invalid_rational")
    if is_int(value) or isinstance(value, Fraction):
        result = Fraction(value)
    elif isinstance(value, str) and value.strip():
        try:
            result = Fraction(value.strip())
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError("invalid_rational") from error
    else:
        raise ValueError("invalid_rational")
    if result.denominator <= 0:
        raise ValueError("invalid_rational")
    return result


def frac_json(value: Fraction) -> dict[str, int]:
    value = Fraction(value)
    return {"num": value.numerator, "den": value.denominator}


def read_frac_json(value: Any) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"num", "den"}:
        raise ValueError("invalid_rational_json")
    if not is_int(value["num"]) or not is_int(value["den"]) or value["den"] <= 0:
        raise ValueError("invalid_rational_json")
    return Fraction(value["num"], value["den"])


def validate_config(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise ValueError("invalid_config_fields")
    if config["control"] != CONTROL:
        raise ValueError("unsupported_control")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ or config["channels"] != CHANNELS:
        raise ValueError("unsupported_format")
    if config["sample_format"] != "f32" or config["sdk_frame_samples"] != SDK_FRAME_SAMPLES:
        raise ValueError("unsupported_format")
    if config["block_samples"] != BLOCK_SAMPLES:
        raise ValueError("unsupported_block_samples")
    if frac(config["speech_floor"]) != FLOOR:
        raise ValueError("unsupported_speech_floor")
    if frac(config["speech_ceiling"]) != SPEECH_CEILING:
        raise ValueError("unsupported_speech_ceiling")
    if frac(config["flex_ceiling"]) != FLEX_CEILING:
        raise ValueError("unsupported_flex_ceiling")
    return {
        "control": CONTROL,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": "f32",
        "sdk_frame_samples": SDK_FRAME_SAMPLES,
        "block_samples": BLOCK_SAMPLES,
        "speech_floor": FLOOR,
        "speech_ceiling": SPEECH_CEILING,
        "flex_ceiling": FLEX_CEILING,
    }


def validate_case(case: Any) -> dict[str, Any]:
    """Validate a whole-clip source timeline without modifying the caller copy."""
    if not isinstance(case, dict) or set(case) - CASE_KEYS:
        raise ValueError("invalid_case_fields")
    for field in ("case_id", "material", "blocks", "events", "note"):
        if field not in case:
            raise ValueError("missing_case_field:" + field)
    if not isinstance(case["case_id"], str) or not case["case_id"].strip():
        raise ValueError("invalid_case_id")
    if not isinstance(case["material"], str) or not case["material"].strip():
        raise ValueError("invalid_material")
    if not isinstance(case["note"], str):
        raise ValueError("invalid_case_note")
    blocks = case["blocks"]
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("empty_blocks")
    normalized_blocks = []
    expected_start = 0
    boundaries = {0}
    for index, block in enumerate(blocks):
        if not isinstance(block, dict) or set(block) - (BLOCK_KEYS | {"oracle_label"}):
            raise ValueError("invalid_block_fields")
        if not BLOCK_KEYS <= set(block):
            raise ValueError("missing_block_fields")
        first, end = block["source_first_sample"], block["source_end_sample"]
        if not is_int(first) or not is_int(end) or first != expected_start or end <= first:
            raise ValueError("noncontiguous_blocks")
        length = end - first
        final = index == len(blocks) - 1
        if length > BLOCK_SAMPLES or (not final and length != BLOCK_SAMPLES):
            raise ValueError("invalid_block_length")
        if block["label"] not in LABELS:
            raise ValueError("unknown_label")
        if "oracle_label" in block and block["oracle_label"] not in LABELS:
            raise ValueError("unknown_oracle_label")
        if not isinstance(block["material"], str) or not block["material"].strip():
            raise ValueError("invalid_block_material")
        normalized_blocks.append(dict(block))
        boundaries.add(end)
        expected_start = end

    events = case["events"]
    if not isinstance(events, list):
        raise ValueError("invalid_events")
    normalized_events = []
    drift_ranges = []
    rebuffers = set()
    for event in events:
        if not isinstance(event, dict) or event.get("kind") not in ("drift", "rebuffer"):
            raise ValueError("unknown_event_kind")
        if not isinstance(event.get("note"), str):
            raise ValueError("invalid_event_note")
        if event["kind"] == "drift":
            if set(event) != DRIFT_KEYS:
                raise ValueError("invalid_drift_fields")
            start, end = event["start_sample"], event["end_sample"]
            num, den = event["scale_num"], event["scale_den"]
            if not all(is_int(value) for value in (start, end, num, den)):
                raise ValueError("invalid_drift_values")
            if start not in boundaries or end not in boundaries or not start < end:
                raise ValueError("drift_unaligned")
            if num <= 0 or den <= 0:
                raise ValueError("invalid_drift_scale")
            drift_ranges.append((start, end))
            normalized_events.append(dict(event))
        else:
            if set(event) != REBUFFER_KEYS:
                raise ValueError("invalid_rebuffer_fields")
            at, gap = event["at_sample"], event["gap_ns"]
            if not is_int(at) or not is_int(gap) or at not in boundaries:
                raise ValueError("rebuffer_unaligned")
            if gap <= 0:
                raise ValueError("invalid_rebuffer_gap")
            if any(start < at < end for start, end in drift_ranges):
                raise ValueError("rebuffer_inside_drift")
            if at in rebuffers:
                raise ValueError("duplicate_rebuffer")
            rebuffers.add(at)
            normalized_events.append(dict(event))
    drift_ranges.sort()
    for previous, current in zip(drift_ranges, drift_ranges[1:]):
        if current[0] < previous[1]:
            raise ValueError("overlapping_drift_events")

    recorded_floor = None
    if "recorded_slow_floor" in case:
        try:
            recorded_floor = frac(case["recorded_slow_floor"])
        except ValueError as error:
            raise ValueError("invalid_recorded_slow_floor") from error
        if not 0 < recorded_floor <= 1:
            raise ValueError("invalid_recorded_slow_floor")
    if "recorded_note" in case and not isinstance(case["recorded_note"], str):
        raise ValueError("invalid_recorded_note")
    if "variants" in case and (not isinstance(case["variants"], list) or
                               any(value not in VARIANTS for value in case["variants"])):
        raise ValueError("invalid_variant_list")

    result = dict(case)
    result["blocks"] = normalized_blocks
    result["events"] = normalized_events
    return result


def case_digest(case: dict[str, Any]) -> str:
    return sha256_hex(canonical_bytes(validate_case(case)))


def block_ns(block: dict[str, Any]) -> int:
    return (block["source_end_sample"] - block["source_first_sample"]) * NS_PER_SAMPLE


def plan_rates(case: dict[str, Any], config: dict[str, Any],
               label_field: str = "label") -> tuple[list[Fraction], dict[str, Any]]:
    """D1 whole-clip budget: uniform speech slowdown paid by flex compression."""
    protected_ns = 0
    flex_ns = 0
    for block in case["blocks"]:
        label = block[label_field] if label_field in block else block["label"]
        if label in PROTECTED_LABELS:
            protected_ns += block_ns(block)
        else:
            flex_ns += block_ns(block)
    source_ns = protected_ns + flex_ns
    savings = flex_ns - flex_ns / config["flex_ceiling"]
    fallback_reason = None
    if protected_ns == 0:
        speech_rate = Fraction(1)
        flex_rate = Fraction(1)
        fallback_reason = "no_protected_blocks"
    elif flex_ns == 0:
        speech_rate = Fraction(1)
        flex_rate = Fraction(1)
        fallback_reason = "insufficient_pause_budget"
    else:
        computed = protected_ns / (protected_ns + savings)
        speech_rate = max(config["speech_floor"], computed)
        required = protected_ns * (1 / speech_rate - 1)
        if required > savings:
            speech_rate = computed
            required = savings
        flex_rate = flex_ns / (flex_ns - required)
        if flex_rate > config["flex_ceiling"]:
            flex_rate = config["flex_ceiling"]
            required = savings
            speech_rate = protected_ns / (protected_ns + required)
        if not (config["speech_floor"] <= speech_rate <= config["speech_ceiling"]):
            raise ValueError("planner_rate_out_of_bounds")
        if not (1 <= flex_rate <= config["flex_ceiling"]):
            raise ValueError("planner_rate_out_of_bounds")
    rates = []
    for block in case["blocks"]:
        label = block[label_field] if label_field in block else block["label"]
        rates.append(speech_rate if label in PROTECTED_LABELS else flex_rate)
    recorded_floor = None
    matches_recorded = None
    if "recorded_slow_floor" in case:
        recorded_floor = frac(case["recorded_slow_floor"])
        matches_recorded = (protected_ns > 0 and speech_rate == recorded_floor)
    budget = {
        "label_field": label_field,
        "protected_samples": protected_ns // NS_PER_SAMPLE,
        "flex_samples": flex_ns // NS_PER_SAMPLE,
        "source_ns": source_ns,
        "protected_ns": protected_ns,
        "flex_ns": flex_ns,
        "max_flex_savings_ns": frac_json(savings),
        "speech_rate_from_full_budget": frac_json(
            protected_ns / (protected_ns + savings) if protected_ns and savings else Fraction(1)),
        "speech_rate": frac_json(speech_rate),
        "flex_rate": frac_json(flex_rate),
        "required_slow_ns": frac_json(
            protected_ns * (1 / speech_rate - 1) if speech_rate else Fraction(0)),
        "floor_limited": bool(protected_ns and flex_ns and
                              speech_rate == config["speech_floor"] and
                              protected_ns / (protected_ns + savings) < config["speech_floor"]),
        "fallback_reason": fallback_reason,
        "recorded_slow_floor": frac_json(recorded_floor) if recorded_floor is not None else None,
        "matches_recorded_slow_floor": matches_recorded,
        "recorded_note": case.get("recorded_note"),
    }
    return rates, budget


def _apply_events(case: dict[str, Any], variant: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if variant == "drift_uncompensated":
        return [event for event in case["events"] if event["kind"] == "drift"], []
    if variant == "rebuffer_uncompensated":
        return [], [event for event in case["events"] if event["kind"] == "rebuffer"]
    if variant == "oracle_compensated":
        return ([event for event in case["events"] if event["kind"] == "drift"],
                [event for event in case["events"] if event["kind"] == "rebuffer"])
    return [], []


def _drift_scale(block: dict[str, Any], drift_events: list[dict[str, Any]]) -> Fraction:
    scale = Fraction(1)
    for event in drift_events:
        if event["start_sample"] <= block["source_first_sample"] and \
                block["source_end_sample"] <= event["end_sample"]:
            scale *= Fraction(event["scale_num"], event["scale_den"])
    return scale


def _schedule(case: dict[str, Any], rates: list[Fraction],
              drift_events: list[dict[str, Any]],
              rebuffer_events: list[dict[str, Any]],
              label_field: str = "label") -> tuple[list[dict[str, Any]], Fraction, list[dict[str, Any]]]:
    gaps_by_start: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in rebuffer_events:
        gaps_by_start[event["at_sample"]].append(event)
    timeline = Fraction(0)
    schedule: list[dict[str, Any]] = []
    gap_records: list[dict[str, Any]] = []

    def insert_gaps(at_sample: int) -> None:
        nonlocal timeline
        for event in sorted(gaps_by_start.get(at_sample, []), key=lambda item: item["gap_ns"]):
            before = timeline
            timeline += Fraction(event["gap_ns"])
            gap_records.append({
                "kind": "rebuffer",
                "source_sample": at_sample,
                "source_ns": at_sample * NS_PER_SAMPLE,
                "gap_ns": event["gap_ns"],
                "playback_start_ns": before,
                "playback_end_ns": timeline,
            })

    for index, block in enumerate(case["blocks"]):
        insert_gaps(block["source_first_sample"])
        source_ns = block_ns(block)
        scale = _drift_scale(block, drift_events)
        playback = (Fraction(source_ns) / rates[index]) * scale
        start = timeline
        timeline += playback
        schedule.append({
            "index": index,
            "source_first_sample": block["source_first_sample"],
            "source_end_sample": block["source_end_sample"],
            "source_duration_ns": source_ns,
            "label": block[label_field] if label_field in block else block["label"],
            "source_label": block["label"],
            "material": block["material"],
            "rate": rates[index],
            "drift_scale": scale,
            "playback_duration_ns": playback,
            "playback_start_ns": start,
            "playback_end_ns": timeline,
        })
    insert_gaps(case["blocks"][-1]["source_end_sample"])
    return schedule, timeline, gap_records


def _compensate(case: dict[str, Any], rates: list[Fraction], schedule: list[dict[str, Any]],
                config: dict[str, Any], total_ns: Fraction, playback_ns: Fraction
                ) -> tuple[list[Fraction], dict[str, Any]]:
    delta = playback_ns - total_ns
    info: dict[str, Any] = {
        "feasible": True,
        "changed": False,
        "delta_ns": frac_json(delta),
        "adjustment_group": None,
        "adjusted_rate": None,
        "reason": None,
    }
    if delta == 0:
        return rates, info
    if delta > 0:
        group, lower, upper = FLEX_LABELS, Fraction(1), config["flex_ceiling"]
    else:
        group, lower, upper = PROTECTED_LABELS, config["speech_floor"], config["speech_ceiling"]
    weighted_in = Fraction(0)
    current_out = Fraction(0)
    for entry in schedule:
        if entry["label"] in group:
            weighted_in += Fraction(entry["source_duration_ns"]) * entry["drift_scale"]
            current_out += entry["playback_duration_ns"]
    target_out = current_out - delta
    info["adjustment_group"] = list(group)
    if target_out <= 0 or weighted_in <= 0:
        info.update({"feasible": False, "reason": "nonpositive_compensation_target"})
        return rates, info
    adjusted = weighted_in / target_out
    info["adjusted_rate"] = frac_json(adjusted)
    if not lower <= adjusted <= upper:
        info.update({
            "feasible": False,
            "reason": "oracle_compensation_out_of_bounds",
            "allowed_range": {"min": frac_json(lower), "max": frac_json(upper)},
        })
        return rates, info
    new_rates = [
        adjusted if entry["label"] in group else rates[index]
        for index, entry in enumerate(schedule)
    ]
    info["changed"] = adjusted != rates[0] or any(
        new_rates[index] != rates[index] for index in range(len(rates)))
    info["allowed_range"] = {"min": frac_json(lower), "max": frac_json(upper)}
    return new_rates, info


def _project_blocks(schedule: list[dict[str, Any]], rates: list[Fraction]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blocks = []
    changes = []
    previous = None
    for entry in schedule:
        if previous is not None and entry["rate"] != previous:
            changes.append({
                "source_first_sample": entry["source_first_sample"],
                "source_ns": entry["source_first_sample"] * NS_PER_SAMPLE,
                "from": frac_json(previous),
                "to": frac_json(entry["rate"]),
            })
        previous = entry["rate"]
        blocks.append({
            "index": entry["index"],
            "source_first_sample": entry["source_first_sample"],
            "source_end_sample": entry["source_end_sample"],
            "source_start_ns": entry["source_first_sample"] * NS_PER_SAMPLE,
            "source_end_ns": entry["source_end_sample"] * NS_PER_SAMPLE,
            "source_duration_ns": entry["source_duration_ns"],
            "label": entry["label"],
            "source_label": entry["source_label"],
            "material": entry["material"],
            "rate": frac_json(entry["rate"]),
            "drift_scale_applied": frac_json(entry["drift_scale"]),
            "playback_start_ns": frac_json(entry["playback_start_ns"]),
            "playback_end_ns": frac_json(entry["playback_end_ns"]),
            "playback_duration_ns": frac_json(entry["playback_duration_ns"]),
            "final_partial": entry["source_end_sample"] - entry["source_first_sample"] < BLOCK_SAMPLES,
        })
    return blocks, changes


def _final_partial(case: dict[str, Any], schedule: list[dict[str, Any]]) -> dict[str, Any] | None:
    last = case["blocks"][-1]
    length = last["source_end_sample"] - last["source_first_sample"]
    if length >= BLOCK_SAMPLES:
        return None
    return {
        "source_first_sample": last["source_first_sample"],
        "source_end_sample": last["source_end_sample"],
        "valid_samples": length,
        "sdk_full_frames": length // SDK_FRAME_SAMPLES,
        "sdk_partial_frame_valid_samples": length % SDK_FRAME_SAMPLES,
        "playback_duration_ns": frac_json(schedule[-1]["playback_duration_ns"]),
    }


def evaluate_case(case: dict[str, Any], variant: str, config: dict[str, Any]) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise ValueError("unknown_variant")
    case = validate_case(case)
    config = validate_config(config)
    source_ns = Fraction(case["blocks"][-1]["source_end_sample"] * NS_PER_SAMPLE)
    label_field = "oracle_label" if variant in ("oracle_labels", "oracle_compensated") else "label"
    rates, budget = plan_rates(case, config, label_field)

    if variant == "1x":
        rates = [Fraction(1)] * len(case["blocks"])
        budget["applied_plan"] = "1x_control"
    elif variant == "fixed_125":
        rates = [FIXED_CONTROL_RATE] * len(case["blocks"])
        budget["applied_plan"] = "fixed_1.25_control"
    elif variant == "slow_only":
        rates = [
            config["speech_floor"] if block[label_field] in PROTECTED_LABELS else Fraction(1)
            for block in case["blocks"]
        ]
        budget["applied_plan"] = "slow_only_control"

    drift_events, rebuffer_events = _apply_events(case, variant)
    schedule, playback_ns, gaps = _schedule(case, rates, drift_events, rebuffer_events, label_field)
    compensation = {
        "feasible": True, "changed": False, "delta_ns": frac_json(Fraction(0)),
        "adjustment_group": None, "adjusted_rate": None, "reason": None,
    }
    if variant == "oracle_compensated":
        rates, compensation = _compensate(case, rates, schedule, config, source_ns, playback_ns)
        if compensation["feasible"]:
            schedule, playback_ns, gaps = _schedule(case, rates, drift_events, rebuffer_events, label_field)

    blocks, changes = _project_blocks(schedule, rates)
    rate_bounds_pass = all(
        (config["speech_floor"] <= rate <= config["speech_ceiling"]
         if block["label"] in PROTECTED_LABELS
         else Fraction(1) <= rate <= config["flex_ceiling"])
        for block, rate in zip(blocks, rates)
    )
    boundaries = {0} | {block["source_end_sample"] for block in case["blocks"]}
    timestamp_ties = all(
        block["source_start_ns"] == block["source_first_sample"] * NS_PER_SAMPLE and
        block["source_end_ns"] == block["source_end_sample"] * NS_PER_SAMPLE
        for block in blocks
    ) and all(
        event.get("start_sample", event.get("at_sample")) in boundaries
        for event in case["events"]
    )
    duration_identity = playback_ns == source_ns
    gap_record = [{
        "kind": item["kind"],
        "source_sample": item["source_sample"],
        "source_ns": item["source_ns"],
        "gap_ns": item["gap_ns"],
        "playback_start_ns": frac_json(item["playback_start_ns"]),
        "playback_end_ns": frac_json(item["playback_end_ns"]),
    } for item in gaps]
    schedule_payload = [{
        "s": block["source_first_sample"], "e": block["source_end_sample"],
        "l": block["label"], "r": block["rate"],
        "p0": block["playback_start_ns"], "p1": block["playback_end_ns"],
    } for block in blocks]
    result: dict[str, Any] = {
        "variant": variant,
        "case_id": case["case_id"],
        "material": case["material"],
        "case_digest": case_digest(case),
        "source_samples": case["blocks"][-1]["source_end_sample"],
        "source_duration_ns": int(source_ns),
        "playback_duration_ns": frac_json(playback_ns),
        "duration_error_ns": frac_json(playback_ns - source_ns),
        "duration_identity": duration_identity,
        "budget": budget,
        "initial_rate": frac_json(rates[0]),
        "rate_changes": changes,
        "rate_change_count": len(changes),
        "blocks": blocks,
        "playback_events": gap_record + [{
            "kind": "drift",
            "source_start_sample": event["start_sample"],
            "source_end_sample": event["end_sample"],
            "source_start_ns": event["start_sample"] * NS_PER_SAMPLE,
            "source_end_ns": event["end_sample"] * NS_PER_SAMPLE,
            "scale": {"num": event["scale_num"], "den": event["scale_den"]},
        } for event in drift_events],
        "oracle_compensation": compensation,
        "profile_checks": {
            "source_output_mapping": {
                "union_equals_source": True,
                "gap_count": len(gap_record),
                "overlap_count": 0,
                "block_count": len(blocks),
            },
            "duration_identity": duration_identity,
            "rate_bounds": rate_bounds_pass,
            "source_timestamp_ties": timestamp_ties,
            "final_partial_window": _final_partial(case, schedule),
            "silence_filler_material_labels": list(FLEX_LABELS),
            "protected_material_labels": list(PROTECTED_LABELS),
            "pitch_audibility": dict(PITCH_NOT_MEASURED),
            "transient_audibility": dict(TRANSIENT_NOT_MEASURED),
            "buffering": dict(BUFFERING_SEMANTICS),
            "state_model": "stateless offline whole-clip plan; no cross-case state",
            "missing_result": False,
            "candidate_qualified": False,
        },
        "schedule_digest": sha256_hex(canonical_bytes(schedule_payload)),
    }
    result["result_digest"] = sha256_hex(canonical_bytes(result))
    return result
