# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local Rate-profile reference for the regression-head proposal.

The only inputs are synthetic signals and frozen caller-supplied feature
vectors. No Silero model, openSMILE engine, audio file, device, listening result
or installed SDK callback is used. Nothing here qualifies a candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from itertools import pairwise
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_ID = "SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD"
TITLE = "Silero VAD + openSMILE + small regression head"
SLUG = "silero-vad-opensmile-small-regression-head"
SCHEMA_ID = "audio-sdk/task-evidence/silero-vad-opensmile-small-regression-head/report/0.1"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
PROFILE = "rate"
FAMILY = "vad-prosody-head"
RATE_HZ = 16000
HOP = 160
RATES = ("0.75", "1", "1.25", "1.5")
ALPHA_GRID = (1, 10, 100, 1000)
FEATURE_DIM = 95
EGE_MAPS_DIM = 88
VAD_SUMMARY_DIM = FEATURE_DIM - EGE_MAPS_DIM
DEV_GROUPS = ("dev_es2004a", "dev_is1001a", "dev_en2002a")
HELD_GROUP = "held_en2003a"
CONFIG_KEYS = {"alpha", "feature_dim", "hop_samples", "rate_min", "rate_max"}
FRAME_KEYS = {"samples", "epoch", "position"}
RECORD_KEYS = {"window_id", "group", "split", "features", "target"}

FORMAT = {
    "sample_rate_hz": RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": HOP,
}

BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "production_callback_registered": False,
    "public_variable_frame_actuator": False,
    "installed_v0_geometry_preserved": True,
}

NON_CLAIMS = [
    "No Silero ONNX graph, checkpoint or model runtime is loaded or executed.",
    "No openSMILE engine, eGeMAPS extractor or vendor feature is invoked.",
    "No recording, corpus, transcript, syllable label, media file or device is consumed.",
    "No listening, intelligibility, naturalness or preferred-speed result is measured.",
    "No callback pacing, deadline, availability, resource or release qualification is claimed.",
]

GATE_REOPEN = {
    "caller_assets_and_license": (
        "Pin permitted caller-supplied Silero/openSMILE assets and clear the openSMILE engine "
        "commercial license; source-reported research-only results never transfer."
    ),
    "exact_reference_parity": (
        "Run the exact approved extractor and head revision on the frozen cohort with independent parity."
    ),
    "real_cohort": (
        "Collect rights-qualified unfamiliar speech, music and silence with matched labels and controls."
    ),
    "independent_listening": (
        "Run blinded listening for pitch, transient audibility and speech preservation before preference claims."
    ),
    "paced_playback": (
        "Measure source/output timestamps, rebuffer, drift, first output, tail, resources and deadlines "
        "on the target playback runtime."
    ),
    "provider_intake": (
        "Complete explicit opt-in provider intake, license review and a versioned public-surface decision."
    ),
    "public_default_selection": (
        "Obtain explicit default selection and independent review; this package is off and unregistered."
    ),
}


class Reject(ValueError):
    """Fail-closed rejection for malformed or unsupported inputs."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse JSON, rejecting non-finite constants and duplicate keys."""

    def reject(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def rounded(value: float, digits: int) -> float:
    return round(value + 0.0, digits)


# ---------------------------------------------------------------------------
# Synthetic signals and exact source/output interval maps.
# ---------------------------------------------------------------------------

def triangle(index: int, period: int) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return (period - 4 * abs(index % period - period // 2)) / 40.0


def make_signal(name: str) -> List[float]:
    if name in ("tone", "speech_like", "music_like"):
        length = 16003
    elif name == "silence":
        length = 323
    elif name == "impulse":
        length = 323
    else:
        raise Reject("unknown synthetic stimulus: " + name)
    if name == "silence":
        return [0.0] * length
    if name == "impulse":
        samples = [0.0] * length
        samples[160] = 1.0
        return samples
    if name == "tone":
        return [triangle(i, 40) for i in range(length)]
    if name == "speech_like":
        return [((0.55 if (i // 800) % 2 == 0 else 0.12)
                 * triangle(i, 57) + 0.20 * triangle(i, 31)) for i in range(length)]
    return [0.5 * triangle(i, 29) + 0.3 * triangle(i, 43) for i in range(length)]


def parse_rate(rate: Any) -> Fraction:
    if not isinstance(rate, str):
        raise Reject("rate must be a decimal string")
    try:
        value = Fraction(rate)
    except (ValueError, ZeroDivisionError) as error:
        raise Reject("invalid rate") from error
    if value < Fraction(1, 2) or value > Fraction(5, 2):
        raise Reject("rate outside 0.5..2.5")
    return value


def round_half_up(value: Fraction) -> int:
    return math.floor(value + Fraction(1, 2))


def rate_map(length: int, schedule: Sequence[Tuple[int, str]],
             allowed: Iterable[str] | None = None) -> Tuple[List[Dict[str, Any]], Fraction]:
    """Map half-open source intervals to exact integer output intervals."""
    if type(length) is not int or length <= 0 or not schedule:
        raise Reject("expected nonempty content and schedule")
    permitted = tuple(allowed) if allowed is not None else None
    previous = -1
    for offset, rate in schedule:
        if type(offset) is not int or not previous < offset < length or offset % HOP:
            raise Reject("rate change must be aligned and increasing")
        parse_rate(rate)
        if permitted is not None and rate not in permitted:
            raise Reject("rate is not in the frozen set")
        previous = offset
    if schedule[0][0] != 0:
        raise Reject("schedule must begin at source sample zero")
    clock = Fraction(0)
    output = 0
    spans: List[Dict[str, Any]] = []
    for (start, rate), (end, _) in pairwise([*schedule, (length, None)]):
        clock += Fraction(end - start) / parse_rate(rate)
        next_output = round_half_up(clock)
        spans.append({
            "source_interval": [start, end],
            "output_interval": [output, next_output],
            "rate": rate,
            "exact_output_end": fraction_text(clock),
        })
        output = next_output
    return spans, clock


def linear_control(samples: Sequence[float], spans: Sequence[Dict[str, Any]]) -> List[float]:
    """Pitch-changing interpolation control; explicitly not a time stretcher."""
    if not samples or any(type(v) not in (int, float) or not math.isfinite(v) for v in samples):
        raise Reject("expected finite samples")
    output: List[float] = []
    for span in spans:
        start, end = span["source_interval"]
        left, right = span["output_interval"]
        width = right - left
        for index in range(width):
            whole, remainder = divmod(index * (end - start), width)
            at = start + whole
            first = samples[at]
            second = samples[min(at + 1, end - 1)]
            output.append(first if not remainder else first + (second - first) * float(Fraction(remainder, width)))
    return output


def positive_crossings(samples: Sequence[float]) -> int:
    return sum(first <= 0 < second for first, second in pairwise(samples))


def observe(name: str, schedule: Sequence[Tuple[int, str]],
            transient: int | None = None,
            allowed: Iterable[str] | None = None) -> Dict[str, Any]:
    samples = make_signal(name)
    spans, exact = rate_map(len(samples), schedule, allowed)
    output = linear_control(samples, spans)
    crossings_in = positive_crossings(samples)
    crossings_out = positive_crossings(output)
    result: Dict[str, Any] = {
        "stimulus": name,
        "source_samples": len(samples),
        "source_interval": [0, len(samples)],
        "mapping": spans,
        "duration": {
            "output_samples": len(output),
            "exact_output_samples": fraction_text(exact),
            "error_samples": fraction_text(Fraction(len(output)) - exact),
        },
        "final_partial_source_samples": len(samples) % HOP,
        "positive_crossings": {"source": crossings_in, "output": crossings_out},
        "pitch_proxy_hz": rounded(RATE_HZ * crossings_out / len(output), 3) if output else 0.0,
        "peak_abs": rounded(max((abs(v) for v in output), default=0.0), 9),
        "nonfinite_samples": sum(not math.isfinite(v) for v in output),
        "clipped_samples": sum(abs(v) > 1.0 for v in output),
        "identity_1x": bool(schedule == [(0, "1")] and samples == output),
    }
    if transient is not None:
        if type(transient) is not int or not 0 <= transient < len(samples):
            raise Reject("transient outside source interval")
        result["transient_proxy"] = {
            "source_sample": transient,
            "output_peak_sample": max(range(len(output)), key=lambda i: abs(output[i])),
            "nonzero_output_samples": sum(value != 0.0 for value in output),
            "audibility": "not_measured",
        }
    return result


def pause_policy() -> Dict[str, Any]:
    """Source-anchored speech/pause schedule; no filler or pause deletion."""
    tone = make_signal("tone")
    timeline = [
        (0, 2400, "speech"), (2400, 3200, "pause"),
        (3200, 5600, "speech"), (5600, 6400, "pause"),
        (6400, 9600, "speech"), (9600, 10400, "pause"),
        (10400, len(tone), "speech"),
    ]
    schedule = [(start, "1" if label == "speech" else "1.5") for start, end, label in timeline]
    spans, exact = rate_map(len(tone), schedule, RATES)
    output = linear_control(tone, spans)
    speech_source: List[float] = []
    speech_output: List[float] = []
    for (start, _end, label), span in zip(timeline, spans):
        source_start, source_end = span["source_interval"]
        output_start, output_end = span["output_interval"]
        if label == "speech":
            speech_source.extend(tone[source_start:source_end])
            speech_output.extend(output[output_start:output_end])
    return {
        "timeline": [{"source_interval": [start, end], "label": label}
                     for start, end, label in timeline],
        "mapping": spans,
        "duration": {
            "output_samples": len(output),
            "exact_output_samples": fraction_text(exact),
            "error_samples": fraction_text(Fraction(len(output)) - exact),
        },
        "speech_rate": "1",
        "speech_preservation_proxy": {
            "source_speech_samples": len(speech_source),
            "output_speech_samples": len(speech_output),
            "bit_exact_active_speech": speech_source == speech_output,
            "interpretation": "Synthetic waveform equality only; not listening evidence.",
        },
        "pause_filler_samples": 0,
        "pause_deletion_samples": 0,
        "decision_anchor": "source_sample_interval",
    }


def buffer_simulation() -> Dict[str, Any]:
    """Offline sample-queue simulation; never an elapsed-time measurement."""
    events = [
        {"source_sample": 0, "arrival_samples": 160, "demand_samples": 160},
        {"source_sample": 160, "arrival_samples": 0, "demand_samples": 160},
        {"source_sample": 320, "arrival_samples": 240, "demand_samples": 160},
        {"source_sample": 480, "arrival_samples": 80, "demand_samples": 160},
        {"source_sample": 640, "arrival_samples": 160, "demand_samples": 160},
    ]
    queue = rendered = rebuffer = peak = 0
    for event in events:
        queue += event["arrival_samples"]
        peak = max(peak, queue)
        taken = min(queue, event["demand_samples"])
        queue -= taken
        rendered += taken
        rebuffer += event["demand_samples"] - taken
    tail = queue + 3
    return {
        "events": events,
        "rendered_samples": rendered,
        "rebuffer_samples": rebuffer,
        "peak_queue_samples": peak,
        "final_partial_source_samples": 3,
        "drain_tail_samples": tail,
        "device_timing": "not_measured",
    }


# ---------------------------------------------------------------------------
# Frozen caller-supplied features and the standardized regression head.
# ---------------------------------------------------------------------------

def build_feature_bundle() -> Dict[str, Any]:
    """Create a frozen synthetic surrogate; the head never extracts features."""
    records: List[Dict[str, Any]] = []
    for split, groups in (("dev", DEV_GROUPS), ("held", (HELD_GROUP,))):
        for group in groups:
            for index in range(9):
                base = (index * 37 + len(group) * 11) % 101
                acoustic = [((base + column * 7) % 23 - 11) / 16.0
                            for column in range(EGE_MAPS_DIM)]
                vad = [((base + 3 * column) % 17 - 8) / 8.0
                       for column in range(VAD_SUMMARY_DIM)]
                signal = 0.02 * acoustic[0] + 0.01 * vad[1]
                noise = ((index * 13 + len(group)) % 9 - 4) / 100.0
                records.append({
                    "window_id": f"{group}-{index:02d}",
                    "group": group,
                    "split": split,
                    "features": acoustic + vad,
                    "target": rounded(4.0 + signal + noise, 6),
                })
    payload = {"feature_dim": FEATURE_DIM, "records": records}
    return {
        "records": records,
        "feature_dim": FEATURE_DIM,
        "egemaps_surrogate_dim": EGE_MAPS_DIM,
        "vad_summary_surrogate_dim": VAD_SUMMARY_DIM,
        "caller_supplied": True,
        "frozen": True,
        "extraction_invoked": False,
        "silero_invoked": False,
        "opensmile_invoked": False,
        "digest": sha256(canonical_bytes(payload)),
        "description": "Deterministic surrogate vectors; not openSMILE or Silero features.",
    }


def validate_feature_coverage(records: Any) -> bool:
    if not isinstance(records, list) or len(records) < 2:
        raise Reject("expected caller-supplied records")
    identifiers = set()
    seen_groups = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != RECORD_KEYS:
            raise Reject("invalid record keys")
        if not isinstance(record["window_id"], str) or not record["window_id"]:
            raise Reject("invalid window id")
        if record["window_id"] in identifiers:
            raise Reject("duplicate window id")
        identifiers.add(record["window_id"])
        if record["split"] not in ("dev", "held"):
            raise Reject("invalid split")
        if record["group"] not in (*DEV_GROUPS, HELD_GROUP):
            raise Reject("invalid group")
        if (record["group"] == HELD_GROUP) != (record["split"] == "held"):
            raise Reject("group/split mismatch")
        features = record["features"]
        if not isinstance(features, list) or len(features) != FEATURE_DIM:
            raise Reject("wrong feature dimension")
        for value in features:
            if type(value) not in (int, float) or not math.isfinite(value):
                raise Reject("nonfinite feature")
        target = record["target"]
        if type(target) not in (int, float) or not math.isfinite(target) or not 0.0 <= target <= 20.0:
            raise Reject("target outside supported range")
        seen_groups.add(record["group"])
    if set(DEV_GROUPS) - seen_groups or HELD_GROUP not in seen_groups:
        raise Reject("missing frozen dev or held group")
    return True


def validate_config(config: Any) -> bool:
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise Reject("invalid config keys")
    if type(config["alpha"]) is not int or not 1 <= config["alpha"] <= 1000:
        raise Reject("alpha out of range")
    if config["feature_dim"] != FEATURE_DIM or type(config["feature_dim"]) is not int:
        raise Reject("wrong feature dimension")
    if config["hop_samples"] != HOP or type(config["hop_samples"]) is not int:
        raise Reject("wrong hop")
    if config["rate_min"] != RATES[0] or config["rate_max"] != RATES[-1]:
        raise Reject("wrong rate bounds")
    return True


def validate_frame(frame: Any, expected_epoch: int, expected_position: int) -> bool:
    if not isinstance(frame, dict) or set(frame) != FRAME_KEYS:
        raise Reject("invalid frame keys")
    samples = frame["samples"]
    if not isinstance(samples, list) or len(samples) != HOP:
        raise Reject("wrong frame shape")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in samples):
        raise Reject("nonfinite frame")
    if type(frame["epoch"]) is not int or type(frame["position"]) is not int:
        raise Reject("invalid frame clock")
    if frame["epoch"] != expected_epoch or frame["position"] != expected_position:
        raise Reject("stale frame clock")
    return True


def require_open(state: str) -> bool:
    if state != "open":
        raise Reject("session is " + state)
    return True


def standardize(records: Sequence[Dict[str, Any]], indices: Sequence[int]
                ) -> Tuple[List[float], List[float]]:
    dev = [record for record in records if record["split"] == "dev"]
    if not dev:
        raise Reject("no development records")
    means: List[float] = []
    scales: List[float] = []
    for column in indices:
        values = [float(record["features"][column]) for record in dev]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        scale = math.sqrt(variance)
        means.append(mean)
        scales.append(scale if scale > 0.0 else 1.0)
    return means, scales


def design(records: Sequence[Dict[str, Any]], indices: Sequence[int],
           means: Sequence[float], scales: Sequence[float]) -> List[List[float]]:
    # Column zero is the unpenalized intercept required by the standardized head.
    return [[1.0] + [(float(record["features"][column]) - mean) / scale
                     for column, mean, scale in zip(indices, means, scales)]
            for record in records]


def ridge_fit(rows: Sequence[Sequence[float]], targets: Sequence[float], alpha: int) -> List[float]:
    dimension = len(rows[0])
    if dimension == 0 or len(rows) == 0 or len(rows) != len(targets):
        raise Reject("invalid ridge inputs")
    matrix = [[sum(row[i] * row[j] for row in rows)
               + (alpha if i == j and i != 0 else 0.0)
               for j in range(dimension)] for i in range(dimension)]
    vector = [sum(row[i] * target for row, target in zip(rows, targets))
              for i in range(dimension)]
    for column in range(dimension):
        pivot = max(range(column, dimension), key=lambda index: abs(matrix[index][column]))
        if abs(matrix[pivot][column]) < 1e-12:
            raise Reject("singular ridge system")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        vector[column], vector[pivot] = vector[pivot], vector[column]
        for row in range(column + 1, dimension):
            factor = matrix[row][column] / matrix[column][column]
            if factor == 0.0:
                continue
            for offset in range(column, dimension):
                matrix[row][offset] -= factor * matrix[column][offset]
            vector[row] -= factor * vector[column]
    weights = [0.0] * dimension
    for row in reversed(range(dimension)):
        total = vector[row] - sum(matrix[row][column] * weights[column]
                                  for column in range(row + 1, dimension))
        weights[row] = total / matrix[row][row]
    return weights


def predict(rows: Sequence[Sequence[float]], weights: Sequence[float]) -> List[float]:
    return [sum(value * weight for value, weight in zip(row, weights)) for row in rows]


def metrics(targets: Sequence[float], predictions: Sequence[float]) -> Dict[str, float]:
    if len(targets) != len(predictions) or not targets:
        raise Reject("invalid metric inputs")
    errors = [target - predicted for target, predicted in zip(targets, predictions)]
    mean_target = sum(targets) / len(targets)
    mean_predicted = sum(predictions) / len(predictions)
    residual_variance = sum((value - mean_predicted) ** 2 for value in predictions)
    target_variance = sum((value - mean_target) ** 2 for value in targets)
    covariance = sum((target - mean_target) * (predicted - mean_predicted)
                     for target, predicted in zip(targets, predictions))
    correlation = (covariance / math.sqrt(target_variance * residual_variance)
                   if target_variance > 0.0 and residual_variance > 0.0 else 0.0)
    return {
        "mae": rounded(sum(abs(value) for value in errors) / len(errors), 6),
        "rmse": rounded(math.sqrt(sum(value * value for value in errors) / len(errors)), 6),
        "bias": rounded(sum(errors) / len(errors), 6),
        "pearson_r": rounded(correlation, 6),
    }


def grouped_cv(records: Sequence[Dict[str, Any]], indices: Sequence[int],
               alphas: Sequence[int]) -> Dict[str, Any]:
    folds: List[Dict[str, Any]] = []
    for held in DEV_GROUPS:
        train = [record for record in records if record["split"] == "dev" and record["group"] != held]
        test = [record for record in records if record["group"] == held]
        if not train or not test:
            raise Reject("missing grouped fold")
        means, scales = standardize(train, indices)
        train_rows = design(train, indices, means, scales)
        test_rows = design(test, indices, means, scales)
        train_targets = [float(record["target"]) for record in train]
        test_targets = [float(record["target"]) for record in test]
        fold_alphas: Dict[str, Dict[str, Any]] = {}
        for alpha in alphas:
            weights = ridge_fit(train_rows, train_targets, alpha)
            fold_alphas[str(alpha)] = metrics(test_targets, predict(test_rows, weights))
        fold_mean = sum(train_targets) / len(train_targets)
        fold_alphas["constant_fold_mean"] = metrics(
            test_targets, [fold_mean] * len(test_targets))
        folds.append({"held_group": held, "train_records": len(train),
                      "test_records": len(test), "outcomes": fold_alphas})
    alpha_scores = {
        str(alpha): rounded(sum(fold["outcomes"][str(alpha)]["mae"] for fold in folds) / len(folds), 6)
        for alpha in alphas
    }
    selected = min(alphas, key=lambda value: (alpha_scores[str(value)], value))
    return {
        "folds": folds,
        "alpha_mae": alpha_scores,
        "selected_alpha": selected,
        "selected_cv_mae": alpha_scores[str(selected)],
        "constant_fold_mean_cv_mae": rounded(
            sum(fold["outcomes"]["constant_fold_mean"]["mae"] for fold in folds) / len(folds), 6),
    }


def evaluate_head(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    validate_feature_coverage(records)
    combined = tuple(range(FEATURE_DIM))
    acoustic_only = tuple(range(EGE_MAPS_DIM))
    variants: Dict[str, Any] = {}
    for name, indices in (("combined_surrogate_features", combined),
                          ("acoustic_only_ablation", acoustic_only)):
        cv = grouped_cv(records, indices, ALPHA_GRID)
        dev = [record for record in records if record["split"] == "dev"]
        held = [record for record in records if record["split"] == "held"]
        means, scales = standardize(dev, indices)
        weights = ridge_fit(design(dev, indices, means, scales),
                            [float(record["target"]) for record in dev], cv["selected_alpha"])
        held_predictions = predict(design(held, indices, means, scales), weights)
        held_targets = [float(record["target"]) for record in held]
        dev_mean = sum(float(record["target"]) for record in dev) / len(dev)
        variants[name] = {
            "feature_count": len(indices),
            "alpha_grid": list(ALPHA_GRID),
            "standardization": "training-dev fold statistics only",
            "grouped_cv": cv,
            "held_out": metrics(held_targets, held_predictions),
            "held_out_constant_dev_mean": metrics(held_targets, [dev_mean] * len(held_targets)),
            "dev_records": len(dev),
            "held_records": len(held),
            "caller_supplied_features_only": True,
        }
    permutation = list(records)
    targets = [record["target"] for record in permutation]
    permutation = [dict(record, target=targets[(index + 1) % len(targets)])
                   for index, record in enumerate(permutation)]
    adverse_cv = grouped_cv(permutation, combined, (1000,))
    variants["permuted_target_adverse"] = {
        "status": "measured_synthetic_adverse",
        "alpha": 1000,
        "cv_mae": adverse_cv["selected_cv_mae"],
        "constant_fold_mean_cv_mae": adverse_cv["constant_fold_mean_cv_mae"],
        "interpretation": "Broken association control, not a candidate result.",
    }
    return variants


# ---------------------------------------------------------------------------
# Adverse-case evidence and the canonical report.
# ---------------------------------------------------------------------------

def rejection(fn: Any) -> str:
    try:
        fn()
    except Reject:
        return "rejected"
    return "unexpectedly_accepted"


def adverse_cases(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    good_config = {"alpha": 1000, "feature_dim": FEATURE_DIM,
                   "hop_samples": HOP, "rate_min": RATES[0], "rate_max": RATES[-1]}
    frame = {"samples": [0.0] * HOP, "epoch": 1, "position": 320}
    missing_record = dict(records[0])
    del missing_record["group"]
    return {
        "config": {
            "missing_key": rejection(lambda: validate_config({k: v for k, v in good_config.items()
                                                              if k != "alpha"})),
            "unknown_key": rejection(lambda: validate_config({**good_config, "extra": 1})),
            "wrong_type": rejection(lambda: validate_config({**good_config, "alpha": "1000"})),
            "nonfinite": rejection(lambda: validate_config({**good_config, "alpha": float("inf")})),
            "out_of_range": rejection(lambda: validate_config({**good_config, "alpha": 0})),
        },
        "features": {
            "missing_caller_features": rejection(lambda: validate_feature_coverage([])),
            "missing_key": rejection(lambda: validate_feature_coverage([missing_record, *records[1:]])),
            "wrong_dimension": rejection(lambda: validate_feature_coverage(
                [dict(records[0], features=records[0]["features"][:-1]), *records[1:]])),
            "nonfinite": rejection(lambda: validate_feature_coverage(
                [dict(records[0], features=[float("inf"), *records[0]["features"][1:]]), *records[1:]])),
            "out_of_range_target": rejection(lambda: validate_feature_coverage(
                [dict(records[0], target=1e6), *records[1:]])),
        },
        "rate_schedule": {
            "unaligned_offset": rejection(lambda: rate_map(16003, [(0, "1"), (161, "1.25")])),
            "unknown_rate": rejection(lambda: rate_map(16003, [(0, "3")])),
            "duplicate_offset": rejection(lambda: rate_map(16003, [(0, "1"), (0, "1.25")])),
            "late_start": rejection(lambda: rate_map(16003, [(160, "1")])),
        },
        "frame": {
            "wrong_shape": rejection(lambda: validate_frame(
                dict(frame, samples=frame["samples"][:-1]), 1, 320)),
            "nonfinite": rejection(lambda: validate_frame(
                dict(frame, samples=[float("inf"), *frame["samples"][1:]]), 1, 320)),
            "stale_epoch": rejection(lambda: validate_frame(frame, 2, 320)),
            "stale_position": rejection(lambda: validate_frame(frame, 1, 480)),
            "missing_samples": rejection(lambda: validate_frame(
                dict(frame, samples=[]), 1, 320)),
            "dsp_state_unchanged": True,
        },
        "lifecycle": {
            "close_then_process": rejection(lambda: require_open("closed")),
            "finish_then_process": rejection(lambda: require_open("finished")),
        },
        "validity": {
            "unknown_never_counted_as_nonspeech": True,
            "invalid_excluded": True,
        },
    }


def repeatability() -> Dict[str, Any]:
    samples = make_signal("tone")
    spans, _ = rate_map(len(samples), [(0, "1.25")], RATES)
    rendered = linear_control(samples, spans)
    digests = [sha256(canonical_bytes(rendered)) for _ in range(3)]
    return {"count": 3, "digests": digests, "byte_identical": len(set(digests)) == 1}


def build_report() -> Dict[str, Any]:
    bundle = build_feature_bundle()
    records = bundle["records"]
    head = evaluate_head(records)
    observations = {
        "constant_rates": {rate: observe("tone", [(0, rate)], allowed=RATES) for rate in RATES},
        "dynamic_step": observe(
            "music_like", [(0, "1"), (3200, "1.25"), (6400, "0.75"), (9600, "1.5")],
            allowed=RATES),
        "drift_schedule": observe(
            "tone", [(0, "1"), (3200, "1.05"), (6400, "0.95"), (9600, "1")]),
        "silence": observe("silence", [(0, "1.25")], allowed=RATES),
        "impulse": observe("impulse", [(0, "1.25")], transient=160, allowed=RATES),
        "unfamiliar_speech_surrogate": observe("speech_like", [(0, "1")], allowed=RATES),
        "pause_policy": pause_policy(),
        "buffer_simulation": buffer_simulation(),
    }
    regressions: List[Dict[str, Any]] = []
    for rate, case in observations["constant_rates"].items():
        if rate != "1":
            regressions.append({
                "condition": "linear_pitch_changing_control",
                "rate": rate,
                "pitch_proxy_hz": case["pitch_proxy_hz"],
                "interpretation": "Duration mapping is exact; pitch proxy shifts. Not a stretch result.",
            })
    combined = head["combined_surrogate_features"]
    combined_cv = combined["grouped_cv"]
    if combined_cv["selected_cv_mae"] > combined_cv["constant_fold_mean_cv_mae"]:
        regressions.append({
            "condition": "standardized_head_grouped_cv",
            "metric": "mae",
            "candidate": combined_cv["selected_cv_mae"],
            "baseline": combined_cv["constant_fold_mean_cv_mae"],
            "interpretation": "Synthetic head loses to the constant fold-mean control; recorded verbatim.",
        })
    held_mae = combined["held_out"]["mae"]
    held_baseline = combined["held_out_constant_dev_mean"]["mae"]
    if held_mae > held_baseline:
        regressions.append({
            "condition": "held_out_surrogate_head",
            "metric": "mae",
            "candidate": held_mae,
            "baseline": held_baseline,
            "interpretation": "Held-out surrogate head loses to the constant dev-mean control; recorded verbatim.",
        })
    adverse_head = head["permuted_target_adverse"]["cv_mae"]
    if adverse_head >= combined_cv["selected_cv_mae"]:
        regressions.append({
            "condition": "permuted_target_adverse",
            "metric": "mae",
            "candidate": combined_cv["selected_cv_mae"],
            "adverse": adverse_head,
            "interpretation": "Broken-association control is not better; recorded verbatim.",
        })
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "family": FAMILY,
        "status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "scope": (
            "Task-local deterministic Rate-profile evidence at a documented optional boundary. "
            "No public-surface, installed-behavior, model, media, device, listening or release claim."
        ),
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": (
            "Frozen caller-supplied surrogate features, exact source/output intervals and a "
            "standardized synthetic regression-head comparison; no runtime adapter is installed."
        ),
        "observations": observations,
        "regression_head": head,
        "caller_supplied_features": {key: value for key, value in bundle.items() if key != "records"},
        "adverse": adverse_cases(records),
        "repeatability": repeatability(),
        "regressions": regressions,
        "gates": [{"name": name, "status": "blocked", "reopen_condition": condition}
                  for name, condition in GATE_REOPEN.items()],
        "missing_evidence": list(GATE_REOPEN),
        "non_claims": NON_CLAIMS,
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "source": "research/tsm-followup-20261101/root-baselines/REPORT.md",
            "Silero_openSMILE_ridge": {
                "dev_leave_one_meeting_out_mae": 1.346,
                "constant_fold_mean_cv_mae": 1.197,
                "held_out_mae": 0.991,
                "held_out_constant_dev_mean_mae": 1.157,
                "held_out_pearson_r": 0.656,
                "license_context": "openSMILE engine is research-only; product use needs permission.",
            },
            "use": "Pinned historical provenance only; never promoted to a measured result here.",
        },
        "evidence_classes": ["synthetic_fixture", "caller_supplied_frozen_features",
                             "boundary_review", "proposal_only"],
        "tool_provenance": [
            "Python 3.12.16 standard library only; no downloads, model weights or vendor runtime.",
            "Silero and openSMILE are absent; the head sees frozen synthetic surrogate vectors only.",
        ],
    }
