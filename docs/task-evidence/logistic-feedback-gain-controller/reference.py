# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, dependency-free logistic feedback gain reference.

The feature formulas, label rule, logistic fit, threshold grid and controller
state machine are transcribed from the SHA-256-pinned sources recorded in
``contract.json``.  This module deliberately uses only the Python standard
library: the report and tests never import numpy, scipy, audio data, weights or
downloaded assets.

The source screen uses 256-sample frames.  This reference uses exactly 160
samples because that is the frozen public v0 frame size; all formulas are
frame-length parametric.  The difference is explicit in the report.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

RATE = 16000
FRAME = 160
SOURCE_FRAME = 256
EXTRA_DELAY_SAMPLES = 1280
LOOP_GAINS = (0.95, 1.05, 1.15)
LABEL_FEEDBACK_RATIO = 0.65
LABEL_MIN_PROMINENCE_DB = 4.0
PERSISTENCE = 2
REDUCTION_DB = -3.0
FLOOR_DB = -12.0
RECOVERY_DB = 0.25
HOLD_FRAMES = 75  # int(0.75 * 16000 / 160)
FEATURE_NAMES = [
    "peak_prominence_db",
    "spectral_flatness",
    "peak_fraction_db",
    "crest_db",
    "frame_rms_growth_db",
    "peak_bin_persistence",
    "normalized_peak_bin",
]
TASK_DIR = Path(__file__).resolve().parent

_TABLES: dict[int, dict] = {}


def _clamp(value: float, low: float, high: float) -> float:
    return low if value < low else high if value > high else value


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values) + 1e-18)


def _tables(length: int) -> dict:
    cached = _TABLES.get(length)
    if cached is not None:
        return cached
    if length < 8:
        raise ValueError("frame length must be at least 8 samples")
    spectrum_bins = length // 2 + 1
    low = max(2, int(180 * length / RATE))
    high = min(spectrum_bins - 2, int(4000 * length / RATE))
    if high <= low:
        raise ValueError("analysis band is empty for this frame length")
    window = [
        0.5 - 0.5 * math.cos(2.0 * math.pi * index / (length - 1))
        for index in range(length)
    ]
    cosine = []
    sine = []
    for bin_index in range(low, high):
        column_cos = []
        column_sin = []
        for sample_index in range(length):
            phase = 2.0 * math.pi * bin_index * sample_index / length
            column_cos.append(math.cos(phase))
            column_sin.append(math.sin(phase))
        cosine.append(column_cos)
        sine.append(column_sin)
    cached = {
        "low": low,
        "high": high,
        "window": window,
        "cosine": cosine,
        "sine": sine,
        "spectrum_bins": spectrum_bins,
    }
    _TABLES[length] = cached
    return cached


def feedback_frame_features(frame, sample_rate: int = RATE,
                            previous_peak_bin: int | None = None,
                            previous_rms: float | None = None) -> tuple[list[float], int, float]:
    """Exact formula-level port of audioml_eval.feedback_control.feedback_frame_features."""
    if sample_rate != RATE:
        raise ValueError("this reference is pinned to 16000 Hz")
    values = [float(value) for value in frame]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("nonfinite sample in feature frame")
    tables = _tables(len(values))
    low, high = tables["low"], tables["high"]
    rms = _rms(values)
    windowed = [value * window for value, window in zip(values, tables["window"])]
    power = []
    for row_cos, row_sin in zip(tables["cosine"], tables["sine"]):
        real = 0.0
        imag = 0.0
        for sample, cosine, sine in zip(windowed, row_cos, row_sin):
            real += sample * cosine
            imag -= sample * sine
        power.append(real * real + imag * imag)
    peak_offset = max(range(len(power)), key=power.__getitem__)
    peak_bin = low + peak_offset
    peak_power = power[peak_offset]
    shoulder_values = []
    left_start = max(low, peak_bin - 4) - low
    left_stop = max(low, peak_bin - 1) - low
    right_start = min(high, peak_bin + 2) - low
    right_stop = min(high, peak_bin + 5) - low
    shoulder_values.extend(power[left_start:left_stop])
    shoulder_values.extend(power[right_start:right_stop])
    shoulder_mean = sum(shoulder_values) / len(shoulder_values) if shoulder_values else 1e-18
    prominence_db = 10.0 * math.log10((peak_power + 1e-18) / (shoulder_mean + 1e-18))
    band = [max(value, 1e-18) for value in power]
    band_mean = sum(band) / len(band)
    flatness = math.exp(sum(math.log(value) for value in band) / len(band)) / (
        band_mean + 1e-18)
    peak_fraction_db = 10.0 * math.log10(
        (peak_power + 1e-18) / (sum(band) + 1e-18))
    crest_db = 20.0 * math.log10(
        (max(abs(value) for value in values) + 1e-9) / (rms + 1e-9))
    growth_db = 20.0 * math.log10(
        (rms + 1e-9) / (previous_rms + 1e-9)) if previous_rms is not None else 0.0
    persistent = float(previous_peak_bin is not None and
                       abs(peak_bin - previous_peak_bin) <= 1)
    features = [
        prominence_db,
        flatness,
        peak_fraction_db,
        crest_db,
        growth_db,
        persistent,
        peak_bin / max(1, tables["spectrum_bins"] - 1),
    ]
    return features, peak_bin, rms


def frame_dataset(speech: list[float], microphone: list[float],
                  feedback: list[float]) -> tuple[list[list[float]], list[float]]:
    """Label exactly as scripts/evaluate_feedback_control_ml.py:frame_dataset."""
    features, labels = [], []
    previous_peak, previous_rms = None, None
    overall_speech_rms = _rms(speech)
    for start in range(0, len(microphone) - FRAME + 1, FRAME):
        stop = start + FRAME
        frame, previous_peak, previous_rms = feedback_frame_features(
            microphone[start:stop], RATE, previous_peak, previous_rms)
        speech_rms = max(_rms(speech[start:stop]), overall_speech_rms * 0.03)
        feedback_rms = _rms(feedback[start:stop])
        positive = (feedback_rms >= LABEL_FEEDBACK_RATIO * speech_rms and
                    frame[0] >= LABEL_MIN_PROMINENCE_DB)
        features.append(frame)
        labels.append(float(positive))
    return features, labels


def fit_logistic(features: list[list[float]], labels: list[float]) -> dict:
    """Formula-level port of scripts/evaluate_feedback_control_ml.py:fit_logistic."""
    if not features or len(features) != len(labels):
        raise ValueError("empty or mismatched training data")
    dimension = len(features[0])
    if any(len(row) != dimension for row in features):
        raise ValueError("ragged feature matrix")
    count = len(features)
    mean = [sum(row[index] for row in features) / count for index in range(dimension)]
    scale = [math.sqrt(sum((row[index] - mean[index]) ** 2 for row in features) / count)
             for index in range(dimension)]
    scale = [1.0 if value < 1e-8 else value for value in scale]
    normalized = [[_clamp((row[index] - mean[index]) / scale[index], -8.0, 8.0)
                   for index in range(dimension)] for row in features]
    positives = max(float(sum(labels)), 1.0)
    negatives = max(float(len(labels) - sum(labels)), 1.0)
    sample_weights = [0.5 / positives if label > 0.5 else 0.5 / negatives
                      for label in labels]
    weights = [0.0] * dimension
    intercept = 0.0
    for _ in range(600):
        errors = []
        for row, label, sample_weight in zip(normalized, labels, sample_weights):
            z = _clamp(sum(value * weight for value, weight in zip(row, weights)) +
                       intercept, -30.0, 30.0)
            errors.append((_sigmoid(z) - label) * sample_weight)
        next_weights = []
        for index in range(dimension):
            gradient = sum(row[index] * error for row, error in zip(normalized, errors))
            next_weights.append(weights[index] - 0.25 * (gradient + 1e-3 * weights[index]))
        weights = next_weights
        intercept -= 0.25 * sum(errors)
    scores = [_sigmoid(_clamp(sum(value * weight for value, weight in zip(row, weights)) +
                              intercept, -40.0, 40.0)) for row in normalized]
    best = None
    for step in range(97):
        threshold = 0.02 + step * 0.01
        predicted = [score >= threshold for score in scores]
        tp = sum(1 for flag, label in zip(predicted, labels) if flag and label > 0.5)
        fp = sum(1 for flag, label in zip(predicted, labels) if flag and label <= 0.5)
        fn = sum(1 for flag, label in zip(predicted, labels) if not flag and label > 0.5)
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * precision * recall / max(1e-12, precision + recall)
        score = (int(precision >= 0.90), recall if precision >= 0.90 else f1, threshold)
        if best is None or score > best[0]:
            best = (score, threshold, precision, recall, f1)
    return {
        "weights": weights,
        "intercept": intercept,
        "mean": mean,
        "scale": scale,
        "threshold": best[1],
        "training_precision": best[2],
        "training_recall": best[3],
        "training_f1": best[4],
        "training_frames": count,
        "training_positive_frames": int(sum(labels)),
    }


def model_probability(features: list[float], model: dict) -> float:
    z = sum((value - mean) / scale * weight
            for value, mean, scale, weight in zip(
                features, model["mean"], model["scale"], model["weights"]))
    return _sigmoid(_clamp(z + model["intercept"], -40.0, 40.0))


def summarize_detection(labels: list[float], probabilities: list[float],
                        threshold: float) -> dict:
    predicted = [probability >= threshold for probability in probabilities]
    positive = [label > 0.5 for label in labels]
    tp = sum(1 for p, t in zip(predicted, positive) if p and t)
    fp = sum(1 for p, t in zip(predicted, positive) if p and not t)
    fn = sum(1 for p, t in zip(predicted, positive) if not p and t)
    tn = sum(1 for p, t in zip(predicted, positive) if not p and not t)
    return {
        "frames": len(labels),
        "positive_frames": int(sum(positive)),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": round(tp / max(1, tp + fp), 4),
        "recall": round(tp / max(1, tp + fn), 4),
        "false_positive_rate": round(fp / max(1, fp + tn), 4),
    }


def model_is_valid(model: dict | None) -> bool:
    if not isinstance(model, dict):
        return False
    try:
        if any(len(model[key]) != len(FEATURE_NAMES) for key in ("weights", "mean", "scale")):
            return False
        values = model["weights"] + model["mean"] + model["scale"]
        values += [model["intercept"], model["threshold"]]
        if not all(math.isfinite(float(value)) for value in values):
            return False
        if any(float(value) <= 0.0 for value in model["scale"]):
            return False
        return 0.0 <= float(model["threshold"]) <= 1.0
    except (KeyError, TypeError, ValueError):
        return False


class IdentityController:
    name = "identity"
    profile = "identity"

    def __init__(self, model: dict | None = None):
        self.detection_events = 0
        self.gain_actions = 0
        self.mode = "passthrough"

    def process(self, frame):
        return [float(value) for value in frame]


class FixedMarginController:
    """The static fallback: fixed -5 dB, no detection or stateful gain."""
    name = "fixed_gain_minus_5db"
    profile = "static_fallback"

    def __init__(self, model: dict | None = None):
        self.gain = 10.0 ** (-5.0 / 20.0)
        self.detection_events = 0
        self.gain_actions = 0
        self.mode = "static_fallback"

    def process(self, frame):
        return [float(value) * self.gain for value in frame]


class LogisticGainController:
    """Source-equivalent detector with bounded gain reduction and slow recovery."""
    name = "logistic_reference"
    profile = "logistic"

    def __init__(self, model: dict | None = None, *, gain_action: bool = True):
        self.fallback_reason = None
        if not model_is_valid(model):
            self.mode = "static_fallback"
            self.fallback_reason = "missing_or_invalid_model"
            self.static_gain = 10.0 ** (-5.0 / 20.0)
        else:
            self.mode = "logistic"
            self.weights = [float(value) for value in model["weights"]]
            self.intercept = float(model["intercept"])
            self.mean = [float(value) for value in model["mean"]]
            self.scale = [float(value) for value in model["scale"]]
            self.threshold = float(model["threshold"])
        self.gain_action = gain_action
        self.previous_peak_bin = None
        self.previous_rms = None
        self.consecutive_detections = 0
        self.hold = 0
        self.gain = 1.0
        self.detection_events = 0
        self.gain_actions = 0
        self.last_probability = 0.0
        self.frames = 0
        self.first_detection_frame = None
        self.first_recovery_frame = None
        self.min_gain = 1.0

    def process(self, frame):
        values = [float(value) for value in frame]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("nonfinite input frame")
        if self.mode == "static_fallback":
            self.frames += 1
            return [value * self.static_gain for value in values]
        features, peak_bin, rms = feedback_frame_features(
            values, RATE, self.previous_peak_bin, self.previous_rms)
        self.previous_peak_bin, self.previous_rms = peak_bin, rms
        self.last_probability = model_probability(features, {
            "mean": self.mean, "scale": self.scale,
            "weights": self.weights, "intercept": self.intercept})
        self.frames += 1
        if self.last_probability >= self.threshold:
            self.consecutive_detections += 1
        else:
            self.consecutive_detections = 0
        if self.consecutive_detections >= PERSISTENCE:
            if self.gain_action:
                self.gain = max(self.gain * 10.0 ** (REDUCTION_DB / 20.0),
                                10.0 ** (FLOOR_DB / 20.0))
                self.hold = HOLD_FRAMES
                self.gain_actions += 1
                self.min_gain = min(self.min_gain, self.gain)
            if self.first_detection_frame is None:
                self.first_detection_frame = self.frames
            self.detection_events += 1
            self.consecutive_detections = 0
        elif self.hold:
            self.hold -= 1
        else:
            previous = self.gain
            self.gain = min(1.0, self.gain * 10.0 ** (RECOVERY_DB / 20.0))
            if previous < 0.995 and self.gain >= 0.995 and self.first_recovery_frame is None:
                self.first_recovery_frame = self.frames
        return [value * self.gain for value in values]


def clone_controller(controller):
    if isinstance(controller, LogisticGainController):
        return LogisticGainController(
            {"weights": controller.weights, "intercept": controller.intercept,
             "mean": controller.mean, "scale": controller.scale,
             "threshold": controller.threshold} if controller.mode == "logistic" else None,
            gain_action=controller.gain_action)
    return controller.__class__()


def simulate_closed_loop(speech: list[float], controller, path_ir: list[float],
                         loop_gain: float, *, delay: int = EXTRA_DELAY_SAMPLES,
                         frame_size: int = FRAME,
                         saturation: float = 4.0) -> dict:
    """Sample-exact finite-IR form of the pinned block simulator with tanh playback."""
    if delay < frame_size or not path_ir or loop_gain < 0:
        raise ValueError("invalid loop configuration")
    length = len(speech)
    playback = [0.0] * length
    output = [0.0] * length
    feedback = [0.0] * length
    peak_output = 0.0
    nonfinite = 0
    for start in range(0, length, frame_size):
        stop = min(length, start + frame_size)
        microphone = []
        for index in range(start, stop):
            source = index - delay
            accumulated = 0.0
            if source >= 0:
                for tap, coefficient in enumerate(path_ir):
                    position = source - tap
                    if position >= 0:
                        accumulated += coefficient * playback[position]
            value = loop_gain * accumulated
            feedback[index] = value
            microphone.append(speech[index] + value)
        controlled = controller.process(microphone)
        if len(controlled) != len(microphone):
            raise ValueError("controller changed frame length")
        for offset, value in enumerate(controlled):
            if not math.isfinite(value):
                nonfinite += 1
                value = 0.0
            output[start + offset] = value
            peak_output = max(peak_output, abs(value))
            playback[start + offset] = math.tanh(saturation * value) / saturation
    return {
        "output": output,
        "feedback": feedback,
        "peak_output": peak_output,
        "nonfinite": nonfinite,
    }


def sdr_db(reference: list[float], estimate: list[float]) -> float | None:
    length = min(len(reference), len(estimate))
    error = [reference[index] - estimate[index] for index in range(length)]
    if max(abs(value) for value in error) < 1e-10:
        return None
    signal = sum(value * value for value in reference[:length]) + 1e-20
    noise = sum(value * value for value in error) + 1e-20
    return 10.0 * math.log10(signal / noise)


def median_or_none(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return round(statistics.median(present), 3) if present else None


def _digest(value) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class LCG:
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return 2.0 * self.state / 0x7FFFFFFF - 1.0


def synthetic_speech(clip_id: int, speaker: str, seed: int,
                     samples: int = 8000) -> dict:
    """Analytic voiced source plus seeded noise; no recordings or assets."""
    random = LCG(seed)
    phase = 0.0
    values = []
    for index in range(samples):
        seconds = index / RATE
        pitch = 125.0 + 8.0 * speaker_offset(speaker) + 18.0 * math.sin(2.0 * math.pi * 0.7 * seconds)
        phase += 2.0 * math.pi * pitch / RATE
        voiced = 0.0
        for harmonic in range(1, 11):
            frequency = harmonic * pitch
            formant = (math.exp(-((frequency - 720.0) / 320.0) ** 2) +
                       0.7 * math.exp(-((frequency - 1220.0) / 380.0) ** 2))
            voiced += formant * math.sin(harmonic * phase) / harmonic
        gate = 1.0 if math.sin(2.0 * math.pi * 1.3 * seconds) > -0.45 else 0.15
        envelope = gate * (0.55 + 0.45 * math.sin(2.0 * math.pi * 3.1 * seconds) ** 2)
        noise = 0.035 * random.uniform()
        values.append(envelope * (0.16 * voiced + noise))
    peak = max(abs(value) for value in values)
    values = [value * (0.18 / peak) for value in values]
    return {"id": clip_id, "speaker": speaker, "seed": seed, "speech": values,
            "digest": _digest([round(value, 12) for value in values])}


def speaker_offset(speaker: str) -> float:
    return {"S1": -1.0, "S2": 0.0, "S3": 1.0}[speaker]


def synthetic_path(id: str, configuration: str, condition: str,
                   frequency_hz: float, decay_ms: float, seed: int,
                   taps: int = 128) -> dict:
    """Finite causal resonator; response at the resonance is normalized to ~1."""
    random = LCG(seed)
    impulse = []
    for index in range(taps):
        envelope = math.exp(-index / (decay_ms * 0.001 * RATE))
        ripple = 0.9 + 0.1 * random.uniform()
        impulse.append(envelope * math.cos(2.0 * math.pi * frequency_hz * index / RATE) * ripple)
    response = sum(value * math.cos(2.0 * math.pi * frequency_hz * index / RATE)
                   for index, value in enumerate(impulse))
    scale = 1.0 / abs(response)
    impulse = [value * scale for value in impulse]
    return {
        "id": id,
        "configuration": configuration,
        "condition": condition,
        "resonance_hz": frequency_hz,
        "decay_ms": decay_ms,
        "seed": seed,
        "taps": taps,
        "impulse": impulse,
        "digest": _digest([round(value, 12) for value in impulse]),
    }


def fixture_spec() -> dict:
    return {
        "format": {"rate": RATE, "channels": 1, "sample_format": "f32", "frame": FRAME},
        "source_frame": SOURCE_FRAME,
        "delay_samples": EXTRA_DELAY_SAMPLES,
        "loop_gains": list(LOOP_GAINS),
        "label": {"feedback_ratio": LABEL_FEEDBACK_RATIO,
                  "min_prominence_db": LABEL_MIN_PROMINENCE_DB,
                  "speech_floor_ratio": 0.03},
        "controller": {"persistence": PERSISTENCE, "reduction_db": REDUCTION_DB,
                       "floor_db": FLOOR_DB, "recovery_db": RECOVERY_DB,
                       "hold_frames": HOLD_FRAMES},
        "clips": [
            {"clip_id": 0, "speaker": "S1", "seed": 101, "samples": 8000},
            {"clip_id": 1, "speaker": "S2", "seed": 202, "samples": 8000},
            {"clip_id": 2, "speaker": "S3", "seed": 303, "samples": 8000},
        ],
        "training_paths": [
            {"id": "TRAIN-A", "configuration": "TRAIN", "condition": "resonant_low",
             "frequency_hz": 1000.0, "decay_ms": 6.0, "seed": 11, "taps": 128},
            {"id": "TRAIN-B", "configuration": "TRAIN", "condition": "resonant_high",
             "frequency_hz": 2200.0, "decay_ms": 4.0, "seed": 12, "taps": 128},
        ],
        "heldout_paths": [
            {"id": "HOLD-X", "configuration": "HELD-A", "condition": "resonant_low",
             "frequency_hz": 1200.0, "decay_ms": 5.0, "seed": 21, "taps": 128},
            {"id": "HOLD-Y", "configuration": "HELD-B", "condition": "resonant_high",
             "frequency_hz": 2600.0, "decay_ms": 3.0, "seed": 22, "taps": 128},
            {"id": "HOLD-Z", "configuration": "HELD-C", "condition": "resonant_mid",
             "frequency_hz": 1700.0, "decay_ms": 8.0, "seed": 23, "taps": 128},
        ],
        "candidates": ["identity", "fixed_gain_minus_5db",
                       "logistic_reference", "logistic_detection_only"],
        "saturation": 4.0,
    }


def build_fixture() -> dict:
    spec = fixture_spec()
    clips = [synthetic_speech(**clip) for clip in spec["clips"]]
    train_paths = [synthetic_path(**path) for path in spec["training_paths"]]
    heldout_paths = [synthetic_path(**path) for path in spec["heldout_paths"]]
    return {"spec": spec, "clips": clips, "train_paths": train_paths,
            "heldout_paths": heldout_paths,
            "digest": _digest({"spec": spec,
                               "clips": [clip["digest"] for clip in clips],
                               "train_paths": [path["digest"] for path in train_paths],
                               "heldout_paths": [path["digest"] for path in heldout_paths]})}


def make_target(clip: dict) -> list[float]:
    return clip["speech"] + [0.0] * RATE


def controller_factories(model: dict | None) -> dict:
    return {
        "identity": lambda: IdentityController(),
        "fixed_gain_minus_5db": lambda: FixedMarginController(),
        "logistic_reference": lambda: LogisticGainController(model),
        "logistic_detection_only": lambda: LogisticGainController(model, gain_action=False),
    }


def _run_simulation(target: list[float], path: dict, gain: float,
                    controller) -> dict:
    result = simulate_closed_loop(target, controller, path["impulse"], gain)
    tail_start = len(target) - RATE
    tail_feedback_rms = _rms(result["feedback"][tail_start:])
    tail_output_rms = _rms(result["output"][tail_start:])
    speech_rms = _rms(target[:tail_start])
    return {
        "simulation": result,
        "tail_feedback_db": 20.0 * math.log10(max(tail_feedback_rms, 1e-12) /
                                              max(speech_rms, 1e-12)),
        "tail_output_db": 20.0 * math.log10(max(tail_output_rms, 1e-12) /
                                            max(speech_rms, 1e-12)),
    }


def build_report(crosscheck: dict | None = None) -> tuple[dict, dict]:
    fixture = build_fixture()
    model_features, model_labels = [], []
    for clip in fixture["clips"]:
        target = make_target(clip)
        for path in fixture["train_paths"]:
            for gain in LOOP_GAINS:
                simulation = simulate_closed_loop(
                    target, IdentityController(), path["impulse"], gain)
                features, labels = frame_dataset(
                    target, simulation["output"], simulation["feedback"])
                model_features.extend(features)
                model_labels.extend(labels)
    model = fit_logistic(model_features, model_labels)
    if model["training_positive_frames"] < 20:
        raise ValueError("insufficient positive synthetic training frames")

    heldout_features, heldout_labels = [], []
    heldout_runs = []
    for clip in fixture["clips"]:
        target = make_target(clip)
        for path in fixture["heldout_paths"]:
            for gain in LOOP_GAINS:
                simulation = simulate_closed_loop(
                    target, IdentityController(), path["impulse"], gain)
                features, labels = frame_dataset(
                    target, simulation["output"], simulation["feedback"])
                heldout_features.extend(features)
                heldout_labels.extend(labels)
                heldout_runs.append({
                    "clip_id": clip["id"], "speaker": clip["speaker"],
                    "path_id": path["id"], "condition": path["condition"],
                    "loop_gain": gain, "frames": len(features),
                    "positive_frames": int(sum(labels)),
                    "digest": _digest({"features": features, "labels": labels}),
                })
    heldout_detection = summarize_detection(
        heldout_labels,
        [model_probability(row, model) for row in heldout_features],
        model["threshold"])

    factories = controller_factories(model)
    clean = {name: {"sdr": [], "events": 0, "actions": 0, "frames": 0,
                    "peak": 0.0, "nonfinite": 0} for name in factories}
    for clip in fixture["clips"]:
        for name, factory in factories.items():
            controller = factory()
            output = controller.process(clip["speech"])
            clean[name]["sdr"].append(sdr_db(clip["speech"], output))
            clean[name]["events"] += controller.detection_events
            clean[name]["actions"] += controller.gain_actions
            clean[name]["frames"] += len(output)
            clean[name]["peak"] = max(clean[name]["peak"],
                                      max(abs(value) for value in output))
            clean[name]["nonfinite"] += sum(1 for value in output
                                            if not math.isfinite(value))

    rows = []
    for clip in fixture["clips"]:
        target = make_target(clip)
        for path in fixture["heldout_paths"]:
            for gain in LOOP_GAINS:
                for name, factory in factories.items():
                    controller = factory()
                    run = _run_simulation(target, path, gain, controller)
                    simulation = run["simulation"]
                    output = simulation["output"]
                    clipped = sum(1 for value in output if abs(value) >= 1.0)
                    tail_start = len(target) - RATE
                    final_gain = (controller.gain if hasattr(controller, "gain")
                                  else getattr(controller, "static_gain", 1.0))
                    rows.append({
                        "clip_id": clip["id"], "speaker": clip["speaker"],
                        "path_id": path["id"], "condition": path["condition"],
                        "loop_gain": gain, "candidate": name,
                        "sdr_db": None if sdr_db(target, output) is None
                                  else round(sdr_db(target, output), 3),
                        "tail_feedback_to_speech_db": round(run["tail_feedback_db"], 3),
                        "tail_output_to_speech_db": round(run["tail_output_db"], 3),
                        "output_peak": round(simulation["peak_output"], 6),
                        "headroom_db": round(20.0 * math.log10(
                            max(simulation["peak_output"], 1e-12)), 3),
                        "clipped_samples": clipped,
                        "nonfinite_samples": simulation["nonfinite"],
                        "detection_events": controller.detection_events,
                        "gain_actions": controller.gain_actions,
                        "final_gain_db": round(20.0 * math.log10(final_gain), 3),
                        "first_detection_frame": getattr(controller, "first_detection_frame", None),
                        "first_recovery_frame": getattr(controller, "first_recovery_frame", None),
                    })

    summaries = {}
    for name in factories:
        subset = [row for row in rows if row["candidate"] == name]
        summaries[name] = {
            "n_runs": len(subset),
            "median_sdr_db": median_or_none([row["sdr_db"] for row in subset]),
            "median_tail_feedback_to_speech_db": round(statistics.median(
                row["tail_feedback_to_speech_db"] for row in subset), 3),
            "median_tail_output_to_speech_db": round(statistics.median(
                row["tail_output_to_speech_db"] for row in subset), 3),
            "max_output_peak": round(max(row["output_peak"] for row in subset), 6),
            "clipped_runs": sum(1 for row in subset if row["clipped_samples"] > 0),
            "nonfinite_runs": sum(1 for row in subset if row["nonfinite_samples"] > 0),
            "median_detection_events": round(statistics.median(
                row["detection_events"] for row in subset), 3),
            "clean_speech_median_sdr_db": median_or_none(clean[name]["sdr"]),
            "clean_speech_detection_events": clean[name]["events"],
            "clean_speech_peak": round(clean[name]["peak"], 6),
        }

    stratified = {}
    for condition in sorted({row["condition"] for row in rows}):
        for gain in LOOP_GAINS:
            key = f"{condition}|{gain}"
            subset = [row for row in rows
                      if row["condition"] == condition and row["loop_gain"] == gain]
            stratified[key] = {
                "n_runs": len(subset),
                "tail_output_db_by_candidate": {
                    name: round(statistics.median(row["tail_output_to_speech_db"]
                                                  for row in subset
                                                  if row["candidate"] == name), 3)
                    for name in factories
                },
                "clipped_runs": sum(1 for row in subset if row["clipped_samples"] > 0),
                "nonfinite_runs": sum(1 for row in subset if row["nonfinite_samples"] > 0),
            }

    controls = adverse_controls(model)
    model_json = {
        "feature_names": FEATURE_NAMES,
        "weights": model["weights"],
        "intercept": model["intercept"],
        "mean": model["mean"],
        "scale": model["scale"],
        "threshold": model["threshold"],
        "training_frames": model["training_frames"],
        "training_positive_frames": model["training_positive_frames"],
        "fixture_digest": fixture["digest"],
    }
    model_digest = hashlib.sha256(canonical_bytes(model_json)).hexdigest()
    crosscheck_digest = _digest(crosscheck) if crosscheck is not None else None
    report = {
        "protocol": ("Synthetic, dependency-free port of the pinned logistic howl-risk "
                     "screen: train on two generated resonant paths, evaluate exact "
                     "features/thresholds on three disjoint generated held-out paths, "
                     "compare identity, static fallback and logistic gain control."),
        "verification_profile": "dsp",
        "scope": {
            "optional_reference_only": True,
            "fixed_v0_format": {"sample_rate_hz": RATE, "channels": 1,
                                "sample_format": "f32", "frame_samples": FRAME},
            "source_uses_256_sample_frames": SOURCE_FRAME,
            "frame_size_deviation_reason": "public v0 is fixed at 160 samples",
            "real_model_weights": False,
            "downloads": False,
            "device_timing": False,
            "release_claim": False,
        },
        "fixture": {
            "digest": fixture["digest"],
            "spec": fixture["spec"],
            "clips": [{"id": clip["id"], "speaker": clip["speaker"],
                       "seed": clip["seed"], "digest": clip["digest"]} for clip in fixture["clips"]],
            "training_paths": [{key: value for key, value in path.items() if key != "impulse"}
                               for path in fixture["train_paths"]],
            "heldout_paths": [{key: value for key, value in path.items() if key != "impulse"}
                              for path in fixture["heldout_paths"]],
            "heldout_runs": heldout_runs,
        },
        "training": {
            "positive_label": ("feedback RMS >= 0.65 x target-frame RMS (floored at 3% "
                               "utterance RMS) and local peak prominence >= 4 dB"),
            "feature_names": FEATURE_NAMES,
            "model": ("class-balanced logistic regression with L2 penalty, 600 gradient "
                      "steps, 97-point threshold grid; 2-frame persistence, -3 dB per "
                      "event, -12 dB floor, slow +0.25 dB recovery"),
            "training_paths": "TRAIN-A and TRAIN-B only (synthetic)",
            "training_frames": model["training_frames"],
            "positive_training_frames": model["training_positive_frames"],
            "weights": model["weights"],
            "intercept": model["intercept"],
            "mean": model["mean"],
            "scale": model["scale"],
            "selected_threshold": model["threshold"],
            "precision_at_selected_threshold_training": model["training_precision"],
            "recall_at_selected_threshold_training": model["training_recall"],
            "f1_at_selected_threshold_training": model["training_f1"],
            "model_digest": model_digest,
        },
        "heldout_detection_metrics": heldout_detection,
        "candidate_summaries": summaries,
        "stratified_heldout": stratified,
        "per_run": rows,
        "static_fallback": {
            "profile": "fixed_gain_minus_5db",
            "trigger": "missing_or_invalid_model",
            "gain_db": -5.0,
            "clean_speech_detection_events": clean["fixed_gain_minus_5db"]["events"],
            "clean_speech_median_sdr_db": median_or_none(clean["fixed_gain_minus_5db"]["sdr"]),
        },
        "controls": controls,
        "crosscheck": crosscheck,
        "crosscheck_digest": crosscheck_digest,
        "limitations": [
            "All speech and feedback paths are analytic synthetic fixtures; no real recordings, loudspeakers or measured IRs.",
            "The pinned source trains on AMI/SMARD data; this evidence substitutes deterministic synthetic paths and does not reproduce its reported numbers.",
            "The logistic coefficients are trained on this fixture only; they are not real ML model weights and are not a production asset.",
            "No real-model inference, licensed runtime, listening test, device timing, CPU/deadline measurement or release qualification is claimed.",
            "The source screen uses 256-sample frames; this v0-boundary reference uses 160-sample frames with the same formulas.",
        ],
    }
    return report, model_json


def adverse_controls(model: dict) -> dict:
    """Numerical, state, reset, adverse and missing-model controls."""
    controller = LogisticGainController(model)
    tone = [0.1 * math.sin(2.0 * math.pi * 1000.0 * index / RATE)
            for index in range(FRAME)]
    for _ in range(12):
        controller.process(tone)
    snapshot = (controller.gain, controller.hold, controller.consecutive_detections,
                controller.detection_events, controller.previous_peak_bin,
                controller.previous_rms)
    rejected = 0
    for bad in ([float("nan")] * FRAME, [float("inf")] * FRAME):
        try:
            controller.process(bad)
        except ValueError:
            rejected += 1
    unchanged = snapshot == (controller.gain, controller.hold,
                             controller.consecutive_detections,
                             controller.detection_events, controller.previous_peak_bin,
                             controller.previous_rms)
    reset_controller = LogisticGainController(model)
    first = reset_controller.process(tone)
    reset_controller.__init__(model)
    replay = reset_controller.process(tone)
    reset_exact = first == replay
    independent = LogisticGainController(model)
    independent.process([value * 0.5 for value in tone])
    independence = independent.gain != controller.gain or independent.previous_rms != controller.previous_rms
    invalid_model_cases = {
        "none": None,
        "nonfinite_weight": dict(model, weights=[float("nan")] + model["weights"][1:]),
        "wrong_dimension": dict(model, weights=model["weights"][:-1]),
        "bad_threshold": dict(model, threshold=1.5),
        "nonpositive_scale": dict(model, scale=[0.0] + model["scale"][1:]),
    }
    fallback_modes = {}
    for name, candidate in invalid_model_cases.items():
        fallback = LogisticGainController(candidate)
        output = fallback.process(tone)
        fallback_modes[name] = {
            "mode": fallback.mode,
            "reason": fallback.fallback_reason,
            "gain": round(output[1] / tone[1], 6),
        }
    silent = LogisticGainController(model)
    silent_output = silent.process([0.0] * FRAME)
    impulse = LogisticGainController(model)
    impulse_output = impulse.process([0.0] * 80 + [0.5] + [0.0] * 79)
    peak_index = max(range(len(impulse_output)), key=lambda index: abs(impulse_output[index]))
    return {
        "nonfinite_frames_rejected": rejected,
        "state_unchanged_after_rejection": unchanged,
        "reset_replays_exactly": reset_exact,
        "sessions_independent": independence,
        "silent_output_peak": max(abs(value) for value in silent_output),
        "impulse_peak_index": peak_index,
        "impulse_added_delay_samples": peak_index - 80,
        "invalid_model_fallbacks": fallback_modes,
        "partial_frame_length_preserved": len(LogisticGainController(model).process(tone[:37])) == 37,
    }


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n").encode("utf-8")


def write_outputs(model: dict | None = None, crosscheck: dict | None = None) -> dict:
    if crosscheck is None:
        path = TASK_DIR / "crosscheck_vectors.json"
        if path.is_file():
            crosscheck = json.loads(path.read_text(encoding="utf-8"))
    report, model_json = build_report(crosscheck)
    if model is not None and model != model_json:
        raise ValueError("supplied model does not match regenerated model")
    (TASK_DIR / "report.json").write_bytes(canonical_bytes(report))
    digest = hashlib.sha256(canonical_bytes(report)).hexdigest()
    (TASK_DIR / "report.json.sha256").write_text(digest + "\n", encoding="utf-8")
    (TASK_DIR / "model.json").write_bytes(canonical_bytes(model_json))
    return report
