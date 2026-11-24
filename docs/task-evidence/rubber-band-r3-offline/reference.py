# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, synthetic, whole-clip OLA/WSOLA-style offline TSM reference.

This is a proposal-only model. It has no real Rubber Band source, binary,
weights, runtime, corpus, playback device, listening result or release claim.
The installed SDK remains 16 kHz mono float32 with 160-sample frames.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple

import fixture
import scorer

SEGMENT = 1024
ANALYSIS_HOP = 512
SEARCH_SHIFT = 32
SEARCH_LEN = 128
RAMP_SAMPLES = 800
MIN_RATE = scorer.MIN_RATE
MAX_RATE = scorer.MAX_RATE

BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
REBASED_ONTO = "2bc2a13aa4c5b398933fd9097d09746ce151216e"
BRANCH = "swarm/SDK-RUBBER-BAND-R3-OFFLINE"
TASK_ID = "SDK-RUBBER-BAND-R3-OFFLINE"

HANN = [0.5 - 0.5 * math.cos(2.0 * math.pi * i / (SEGMENT - 1)) for i in range(SEGMENT)]


class ReferenceError(ValueError):
    """Explicit fail-closed rejection of invalid or unsupported inputs."""


def validate_samples(values: Sequence[float], label: str) -> None:
    if not isinstance(values, (list, tuple)) or not values:
        raise ReferenceError(f"{label}: missing or empty samples")
    for index, value in enumerate(values):
        if not scorer.is_finite(value):
            raise ReferenceError(f"{label}: nonfinite sample at {index}")
        if abs(float(value)) > 1.0:
            raise ReferenceError(f"{label}: out-of-range sample at {index}")


def validate_schedule(schedule: Sequence[tuple[int, float]]) -> List[tuple[int, float]]:
    if not schedule:
        raise ReferenceError("missing rate schedule")
    cleaned: List[tuple[int, float]] = []
    previous = -1
    for sample, rate in schedule:
        if not isinstance(sample, int) or isinstance(sample, bool) or sample < 0 or sample <= previous:
            raise ReferenceError(f"invalid schedule source sample {sample!r}")
        if not scorer.is_finite(rate) or not (MIN_RATE <= float(rate) <= MAX_RATE):
            raise ReferenceError(f"rate outside [{MIN_RATE}, {MAX_RATE}]: {rate!r}")
        cleaned.append((sample, float(rate)))
        previous = sample
    if cleaned[0][0] != 0:
        raise ReferenceError("rate schedule must start at source sample 0")
    return cleaned


def rate_at(index: int, schedule: Sequence[tuple[int, float]], ramp: int) -> float:
    current = schedule[0][1]
    current_start = 0
    for sample, rate in schedule[1:]:
        if index < sample:
            break
        current = rate
        current_start = sample
    if ramp <= 0 or index < current_start:
        return current
    previous = current
    for sample, rate in schedule:
        if sample >= current_start:
            break
        previous = rate
    fraction = min(1.0, (index - current_start) / float(ramp))
    return previous + fraction * (current - previous)


def build_prefix(length: int, schedule: Sequence[tuple[int, float]],
                 ramp: int = RAMP_SAMPLES) -> List[float]:
    """Ideal source->output sample map as a monotone cumulative float array."""
    if not isinstance(length, int) or length <= 0:
        raise ReferenceError("invalid source length")
    prefix = [0.0] * (length + 1)
    total = 0.0
    for index in range(length):
        rate = rate_at(index, schedule, ramp)
        if not scorer.is_finite(rate) or rate <= 0.0:
            raise ReferenceError("nonpositive rate in prefix")
        total += 1.0 / rate
        prefix[index + 1] = total
    return prefix


def schedule_for_case(case: Dict[str, Any], stimulus: Sequence[float]):
    if case.get("label_driven_schedule"):
        labels = fixture.DECISION_LABELS.get(case["stimulus"])
        if not labels:
            raise ReferenceError("missing synthetic labels for timestamp policy")
        schedule = [(int(label["source_start"]),
                     0.95 if label["decision"] == "protect" else 1.25)
                    for label in labels]
        return validate_schedule(schedule), RAMP_SAMPLES
    if case.get("control") == "rate_step_unsmoothed":
        return validate_schedule(case["schedule"]), 0
    if "schedule" in case:
        return validate_schedule(case["schedule"]), RAMP_SAMPLES
    if "rate" in case:
        return validate_schedule([(0, case["rate"])]), RAMP_SAMPLES
    raise ReferenceError("missing rate schedule")


def best_shift(source: Sequence[float], numerator: Sequence[float],
               denominator: Sequence[float], source_start: int, out_start: int) -> int:
    """WSOLA-style shift chosen by minimum squared mismatch on already-rendered audio."""
    best = 0
    best_score = float("inf")
    for shift in range(-SEARCH_SHIFT, SEARCH_SHIFT + 1):
        first = source_start + shift
        if first < 0 or first + SEARCH_LEN > len(source):
            continue
        total = 0.0
        count = 0
        for offset in range(SEARCH_LEN):
            position = out_start + offset
            if position < 0 or position >= len(numerator) or denominator[position] <= 0.0:
                continue
            previous = numerator[position] / denominator[position]
            current = source[first + offset]
            total += (current - previous) ** 2
            count += 1
        if count < SEARCH_LEN // 2:
            continue
        score = total / count
        if score < best_score:
            best_score = score
            best = shift
    return best


def ola_wsola(source: Sequence[float], prefix: Sequence[float], target: int,
              do_search: bool = True) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Overlap-add with optional waveform-similarity shift and exact length trim."""
    validate_samples(source, "source")
    if target <= 0:
        raise ReferenceError("nonpositive target length")
    offset = SEGMENT // 2
    buffer_length = target + SEGMENT + 2
    numerator = [0.0] * buffer_length
    denominator = [0.0] * buffer_length
    records: List[Dict[str, Any]] = []

    def place_window(source_start: int, center: int, shift: int, terminal: bool) -> None:
        out_start = center + offset - SEGMENT // 2
        for index, weight in enumerate(HANN):
            position = out_start + index
            if position < 0 or position >= buffer_length or weight <= 0.0:
                continue
            sample_index = source_start + shift + index
            sample = source[sample_index] if 0 <= sample_index < len(source) else 0.0
            numerator[position] += weight * sample
            denominator[position] += weight

    last_start = 0
    for source_start in range(0, len(source), ANALYSIS_HOP):
        center = int(round(prefix[source_start]))
        nominal_end = min(len(source), source_start + ANALYSIS_HOP)
        out_start = center
        shift = 0
        score = None
        if do_search and source_start > 0 and center >= SEARCH_LEN // 2:
            shift = best_shift(source, numerator, denominator, source_start, out_start)
            score = shift
        place_window(source_start, center, shift, False)
        records.append({
            "nominal_source_start": source_start,
            "nominal_source_end": nominal_end,
            "source_start_used": max(0, source_start + shift),
            "source_end_used": min(len(source), source_start + shift + SEGMENT),
            "output_center": center,
            "wsola_shift": shift,
            "similarity_shift_selected": score is not None,
            "terminal_repeat": False,
        })
        last_start = source_start

    # Explicit terminal window covers the final partial output window; the
    # source interval is repeated and excluded from nominal coverage checks.
    last_center = int(round(prefix[last_start]))
    if last_center + SEGMENT // 2 < target - 1:
        terminal_center = target - 1
        terminal_source = max(0, len(source) - SEGMENT)
        place_window(terminal_source, terminal_center, 0, True)
        records.append({
            "nominal_source_start": last_start,
            "nominal_source_end": min(len(source), last_start + ANALYSIS_HOP),
            "source_start_used": terminal_source,
            "source_end_used": min(len(source), terminal_source + SEGMENT),
            "output_center": terminal_center,
            "wsola_shift": 0,
            "similarity_shift_selected": False,
            "terminal_repeat": True,
        })

    output: List[float] = []
    for index in range(target):
        position = index + offset
        value = numerator[position] / denominator[position] if denominator[position] > 0.0 else 0.0
        output.append(max(-1.0, min(1.0, value)))
    return output, records


def identity_reference(source: Sequence[float]) -> Tuple[List[float], List[Dict[str, Any]]]:
    validate_samples(source, "source")
    records = []
    for source_start in range(0, len(source), ANALYSIS_HOP):
        records.append({
            "nominal_source_start": source_start,
            "nominal_source_end": min(len(source), source_start + ANALYSIS_HOP),
            "source_start_used": source_start,
            "source_end_used": min(len(source), source_start + SEGMENT),
            "output_center": source_start,
            "wsola_shift": 0,
            "similarity_shift_selected": False,
            "terminal_repeat": False,
        })
    return list(source), records


def varispeed_reference(source: Sequence[float], rate: float) -> Tuple[List[float], List[Dict[str, Any]]]:
    """Adverse control: linear resampling changes duration and pitch."""
    validate_samples(source, "source")
    target = int(round(len(source) / rate))
    output: List[float] = []
    for index in range(target):
        position = index * rate
        left = int(math.floor(position))
        right = min(len(source) - 1, left + 1)
        fraction = position - left
        output.append(source[left] * (1.0 - fraction) + source[right] * fraction)
    prefix = [min(position / rate, target) for position in range(len(source) + 1)]
    records = [{
        "nominal_source_start": 0,
        "nominal_source_end": len(source),
        "source_start_used": 0,
        "source_end_used": len(source),
        "output_center": target // 2,
        "wsola_shift": 0,
        "similarity_shift_selected": False,
        "terminal_repeat": False,
    }]
    return output, records


def pitch_proxy(source: Sequence[float], output: Sequence[float],
                prefix: Sequence[float], start: int, end: int) -> Dict[str, Any]:
    source_segment = source[start:end]
    out_start = int(round(prefix[start]))
    out_end = min(len(output), int(round(prefix[end])))
    output_segment = output[out_start:out_end]
    source_frequency = scorer.dominant_frequency(source_segment, fixture.SAMPLE_RATE_HZ)
    output_frequency = scorer.dominant_frequency(output_segment, fixture.SAMPLE_RATE_HZ)
    scale = output_frequency / source_frequency if source_frequency and output_frequency else None
    # Autocorrelation on chords can select a different octave. The proxy is
    # octave-equivariant: an octave-equivalent peak is pitch-preserving, while
    # fractional ratios (e.g. 1.25 from varispeed) remain visible.
    octave_scale = None
    if scale is not None and scale > 0.0:
        octave_scale = scale / (2.0 ** round(math.log2(scale)))
    return {
        "source_interval": [start, end],
        "mapped_output_interval": [out_start, out_end],
        "source_frequency_hz": source_frequency,
        "output_frequency_hz": output_frequency,
        "scale": scale,
        "octave_normalized_scale": octave_scale,
        "pitch_preserved_proxy": octave_scale is not None and abs(octave_scale - 1.0) <= 0.08,
        "qualifies_listening": False,
        "missing": scale is None,
    }


def run_case(name: str, stimuli: Dict[str, List[float]] | None = None) -> Dict[str, Any]:
    cases = fixture.CASES
    if name not in cases:
        raise ReferenceError(f"unknown case {name!r}")
    case = cases[name]
    stimuli = stimuli or fixture.build_stimuli()
    stimulus_name = case["stimulus"]
    if stimulus_name not in stimuli:
        raise ReferenceError(f"missing stimulus {stimulus_name!r}")
    source = stimuli[stimulus_name]
    validate_samples(source, stimulus_name)
    schedule, ramp = schedule_for_case(case, source)
    prefix = build_prefix(len(source), schedule, ramp)
    target = int(round(prefix[-1]))
    control = case["control"]
    if control == "identity":
        output, records = identity_reference(source)
    elif control == "ola_wsola":
        output, records = ola_wsola(source, prefix, target)
    elif control == "varispeed":
        output, records = varispeed_reference(source, float(case.get("rate", 1.0)))
    elif control == "rate_step_unsmoothed":
        output, records = ola_wsola(source, prefix, target)
    else:
        raise ReferenceError(f"unknown control {control!r}")

    if len(output) != target:
        raise ReferenceError(f"output length {len(output)} != target {target}")

    mapping = scorer.mapping_check(records, len(source), target)
    duration = {
        "input_samples": len(source),
        "target_output_samples": target,
        "actual_output_samples": len(output),
        "error_samples": len(output) - target,
        "relative_error": (len(output) - target) / float(target),
        "source_to_output_map_end": prefix[-1],
    }
    rate_info = scorer.rate_bounds(schedule)
    finite = scorer.nonfinite_count(output) == 0
    peak = scorer.peak(output)
    clipping = scorer.clip_count(output)

    pitch_applicable = stimulus_name not in ("transient", "silence")
    if pitch_applicable and len(source) > 6000:
        pitch = pitch_proxy(source, output, prefix, 3200, 6000)
    else:
        pitch = {
            "applicable": False,
            "withheld_reason": "stimulus has no stationary tonal reference",
            "scale": None,
            "pitch_preserved_proxy": False,
            "qualifies_listening": False,
            "missing": stimulus_name == "silence",
        }
    transient = None
    transient_comparison = None
    if stimulus_name == "transient":
        clicks = [int(prefix[sample]) for sample in fixture.CLICK_STARTS if sample < len(source)]
        transient = scorer.transient_proxy(output, clicks)
        identity_out, _ = identity_reference(source)
        identity_clicks = [sample for sample in fixture.CLICK_STARTS if sample < len(source)]
        identity_transient = scorer.transient_proxy(identity_out, identity_clicks)
        transient_comparison = {
            "identity_peak_to_rms": identity_transient["mean_peak_to_local_rms"],
            "candidate_peak_to_rms": transient["mean_peak_to_local_rms"],
            "identity_max_width": identity_transient["max_threshold_crossing_width"],
            "candidate_max_width": transient["max_threshold_crossing_width"],
            "candidate": transient,
            "identity": identity_transient,
        }

    labels = fixture.DECISION_LABELS.get(stimulus_name)
    preservation = (scorer.speech_preservation(source, output, prefix, labels)
                    if labels and control != "varispeed" else None)
    buffering = scorer.buffering_metrics(prefix, target, fixture.FRAME_SAMPLES,
                                         case.get("rebuffer"))

    required = {
        "duration": duration["error_samples"] == 0,
        "finite_output": finite,
        "mapping": bool(mapping["qualifies"]),
        "rate_bounds": bool(rate_info["within_proxy_bounds"]),
        "clipping": clipping == 0,
        "peak": peak <= 1.0,
    }
    if pitch_applicable:
        # Missing pitch evidence withholds qualification; it is never a pass.
        required["pitch_proxy"] = bool(pitch.get("pitch_preserved_proxy", False))
    elif pitch.get("missing"):
        required["pitch_proxy_withheld"] = False
    if transient_comparison is not None:
        required["transient_proxy"] = (
            transient_comparison["candidate_max_width"] is not None
            and transient_comparison["identity_max_width"] is not None
            and transient_comparison["candidate_max_width"]
            <= transient_comparison["identity_max_width"] + 40
        )
    if preservation is not None:
        speech_db = [item["rms_ratio_db"] for item in preservation["entries"]
                     if item["decision"] == "protect" and item["rms_ratio_db"] is not None]
        required["speech_preservation"] = bool(speech_db) and all(-3.0 <= value <= 3.0 for value in speech_db)
    if case.get("rebuffer"):
        required["rebuffer_recorded"] = buffering["rebuffer"] is not None

    adverse = control in ("varispeed", "rate_step_unsmoothed")
    all_present = all(required.values())
    qualifies = bool(all_present and not adverse)

    return {
        "stimulus": stimulus_name,
        "control": control,
        "schedule": [{"source_sample": sample, "source_ns": sample * 62500, "rate": rate}
                     for sample, rate in schedule],
        "ramp_samples": ramp,
        "source_digest": fixture.digest_value([round(v, 12) for v in source]),
        "output_digest": fixture.digest_value([round(v, 12) for v in output]),
        "duration": duration,
        "rate_bounds": rate_info,
        "mapping": mapping,
        "mapping_records": [record for record in records if not record["terminal_repeat"]],
        "terminal_record": next((record for record in records if record["terminal_repeat"]), None),
        "signal": {
            "nonfinite": scorer.nonfinite_count(output),
            "peak": peak,
            "clipped_samples": clipping,
        },
        "pitch_proxy": pitch,
        "transient_proxy_comparison": transient_comparison,
        "speech_preservation": preservation,
        "playback_buffering": buffering,
        "adverse_control": adverse,
        "required_results": required,
        "all_required_results_present": bool(all_present),
        "candidate_qualified": qualifies,
        "missing_result_promoted": False,
    }


def invalid_and_missing_cases() -> List[Dict[str, Any]]:
    """Each row is an observed rejection/withholding, never a promoted result."""
    rows: List[Dict[str, Any]] = []

    def record(case_id: str, outcome: str, reason: str, *, qualifies: bool = False) -> None:
        rows.append({
            "case_id": case_id,
            "outcome": outcome,
            "reason": reason,
            "candidate_qualified": qualifies,
            "missing_result_promoted": False,
        })

    for case_id, samples in (
        ("nonfinite_sample", [0.0, float("nan"), 0.5]),
        ("infinite_sample", [0.0, float("inf"), 0.5]),
        ("empty_sample_array", []),
        ("out_of_range_sample", [0.0, 1.7]),
    ):
        try:
            validate_samples(samples, case_id)
        except ReferenceError as error:
            record(case_id, "rejected", str(error))
        else:
            record(case_id, "unexpected_acceptance", "validation failed closed")

    for case_id, schedule in (
        ("missing_schedule", []),
        ("nonfinite_rate", [(0, float("nan"))]),
        ("zero_rate", [(0, 0.0)]),
        ("oversized_rate", [(0, 2.0)]),
        ("nonmonotone_schedule", [(0, 1.0), (0, 1.1)]),
        ("schedule_missing_origin", [(160, 1.0)]),
    ):
        try:
            validate_schedule(schedule)
        except ReferenceError as error:
            record(case_id, "rejected", str(error))
        else:
            record(case_id, "unexpected_acceptance", "validation failed closed")

    try:
        run_case("not_a_registered_case")
    except ReferenceError as error:
        record("unknown_case", "rejected", str(error))
    else:
        record("unknown_case", "unexpected_acceptance", "validation failed closed")

    silence = fixture.build_stimuli()["silence"]
    pitch = pitch_proxy(silence, silence, [float(i) for i in range(len(silence) + 1)], 0, 9600)
    rows.append({
        "case_id": "silence_pitch_withheld",
        "outcome": "metric_withheld",
        "reason": "no stationary tonal reference in silence; pitch must not be imputed",
        "pitch_proxy": pitch,
        "candidate_qualified": False,
        "missing_result_promoted": False,
    })
    rows.append({
        "case_id": "missing_rebuffer_event",
        "outcome": "metric_withheld",
        "reason": "no rebuffer event supplied; no playback gap result is fabricated",
        "candidate_qualified": False,
        "missing_result_promoted": False,
    })
    return rows


def build_core_report() -> Dict[str, Any]:
    stimuli = fixture.build_stimuli()
    cases = {name: run_case(name, stimuli) for name in sorted(fixture.CASES)}
    recipe = fixture.fixture_recipe()
    source_pins = fixture.verify_source_pins()
    boundary_pins = fixture.verify_boundary_pins()
    if not all(item["verified"] for item in source_pins.values()):
        raise ReferenceError("source pin mismatch")
    if not all(item["verified"] for item in boundary_pins.values()):
        raise ReferenceError("boundary pin mismatch")

    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": "audio-sdk/rubber-band-r3-offline/0.1",
        "task": TASK_ID,
        "component": "rubber-band-r3-offline",
        "mode": "implementation",
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "processor_exposure": "none",
        "verification_profile": "rate",
        "base_commit": BASE_COMMIT,
        "rebased_onto": REBASED_ONTO,
        "branch": BRANCH,
        "installed_v0_unchanged": True,
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "board_snapshot": fixture.BOARD_SNAPSHOT,
        "fixture": {
            "digest": fixture.fixture_digest(),
            "recipe_digest": fixture.digest_value(recipe),
            "stimuli": recipe["stimuli"],
            "synthetic_only": True,
        },
        "method": {
            "algorithm": "offline OLA/WSOLA-style waveform-similarity overlap-add with Hann window and overlap-add denominator normalization",
            "segment_samples": SEGMENT,
            "analysis_hop_samples": ANALYSIS_HOP,
            "shift_search_samples": SEARCH_SHIFT,
            "search_length_samples": SEARCH_LEN,
            "rate_ramp_samples": RAMP_SAMPLES,
            "rate_range": [MIN_RATE, MAX_RATE],
            "source_clock_ns_per_sample": fixture.NS_PER_SAMPLE,
            "whole_clip_required": True,
            "real_rubber_band_code_or_binary": False,
            "licensed_runtime": False,
            "real_corpus": False,
            "device_or_listening_claim": False,
            "release_claim": False,
        },
        "rate_profile": {
            "source_output_mapping": "per-window nominal source intervals plus monotone ideal output centers",
            "duration": "exact target length from cumulative source-to-output map",
            "pitch": "autocorrelation proxy on synthetic stationary tones; listening deferred",
            "transient_audibility": "synthetic click peak/width proxy; listening deferred",
            "playback_buffering": "caller-owned FIFO model with source-timestamped checkpoints; no device pacing",
            "coverage": {
                "identity_1x": True,
                "rate_increase": True,
                "rate_decrease": True,
                "unfamiliar_speech": True,
                "music": True,
                "silence": True,
                "rebuffer": True,
                "drift": True,
                "final_partial_window": True,
                "pause_filler_tied_to_source_timestamps": True,
                "speech_preservation_measured": True,
            },
        },
        "cases": cases,
        "controls": {
            "identity": "identity_1x",
            "varispeed_adverse": "varispeed_adverse",
            "unsmoothed_step_adverse": "rate_step_unsmoothed_adverse",
            "adverse_never_qualifies": True,
        },
        "invalid_and_missing_cases": invalid_and_missing_cases(),
        "qualification": {
            "candidate_status": "synthetic_reference_only",
            "overall_decision": "DEFER",
            "processor_exposure": "none",
            "no_missing_result_may_qualify": True,
            "missing_result_promoted": False,
            "qualified_case_count": sum(1 for case in cases.values() if case["candidate_qualified"]),
            "adverse_case_count": sum(1 for case in cases.values() if case["adverse_control"]),
            "total_case_count": len(cases),
            "no_release_claim": True,
        },
        "remaining_gates": [
            "Rights-qualified unfamiliar speech and music material with authorized scoring and listening; synthetic proxies never substitute.",
            "Exact target-device playback path with paced fill/flush, rebuffer recovery, drift correction and final partial window under real load.",
            "Versioned variable-frame actuator or caller-owned TSM FIFO with explicit source/output timestamps outside frozen v0.",
            "Native boundary intake, license review, descriptor/registry decision and independent review before any processor exposure.",
        ],
    }


def cold_core_digest() -> str:
    return fixture.digest_value(build_core_report())


def build_report() -> Dict[str, Any]:
    report = build_core_report()
    digests = [cold_core_digest() for _ in range(3)]
    report["crosscheck"] = {
        "cold_start_core_digests": digests,
        "byte_identical": len(set(digests)) == 1,
        "canonical_core_digest": digests[0],
        "tolerance_widened": False,
        "provider_substituted": False,
    }
    return report
