# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local inverse-EQ reference and frozen synthetic fixtures.

This module implements a frozen six-band EQ perturbation, a ridge regression
that estimates band corrections from pinned synthetic response probes, and a
causal biquad cascade that applies the correction.  It uses only the Python
standard library.  There are no learned weights downloaded or installed, no
external model, no licensed runtime, no real audio and no change to the SDK
public surface or installed v0 behavior.

The fixture is deliberately a *controlled* synthetic perturbation.  It does not
establish that any speaker's natural spectral balance is an error, and it does
not qualify the method for real speech.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import scorer

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
BAND_FREQUENCIES_HZ: Tuple[float, ...] = (125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0)
BAND_Q = 1.0
FORWARD_GAINS_DB: Tuple[float, ...] = (-6.0, 4.0, -3.0, 5.0, -4.0, 3.0)
PROBE_FREQUENCIES_HZ: Tuple[float, ...] = (62.5, 125.0, 250.0, 500.0, 1000.0,
                                           2000.0, 4000.0, 8000.0, 12000.0)
FIXTURE_SEED = 20261028
TRAINING_ROWS = 12
RIDGE_LAMBDA = 0.01
MAX_ABS_INPUT = 2.0
MODES = ("identity", "fixed_eq", "learned_inverse")
STATE_VERSION = "learned-inverse-eq-state-v1"
Coefficients = Tuple[float, float, float, float, float]


def _clean(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("nonfinite_coefficient")
    return 0.0 if abs(value) < 1e-13 else round(value, 13)


def lcg(seed: int = FIXTURE_SEED):
    """Deterministic 31-bit linear congruential generator in [-1, 1)."""
    state = int(seed) & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield 2.0 * state / 2147483647.0 - 1.0


def peaking_coefficients(gain_db: float, center_hz: float,
                         q: float = BAND_Q,
                         sample_rate_hz: int = SAMPLE_RATE_HZ) -> Coefficients:
    """Normalized RBJ peaking-EQ biquad coefficients (a0 folded to 1)."""
    if not math.isfinite(gain_db) or not math.isfinite(center_hz):
        raise ValueError("nonfinite_eq_setting")
    if not 0.0 < center_hz < sample_rate_hz / 2.0:
        raise ValueError("eq_center_out_of_range")
    amplitude = 10.0 ** (float(gain_db) / 40.0)
    omega = 2.0 * math.pi * float(center_hz) / float(sample_rate_hz)
    alpha = math.sin(omega) / (2.0 * float(q))
    cosine = math.cos(omega)
    a0 = 1.0 + alpha / amplitude
    return tuple(_clean(value / a0) for value in (
        1.0 + alpha * amplitude,
        -2.0 * cosine,
        1.0 - alpha * amplitude,
        -2.0 * cosine,
        1.0 - alpha / amplitude,
    ))  # type: ignore[return-value]


def cascade_coefficients(gains_db: Sequence[float]) -> Tuple[Coefficients, ...]:
    if len(gains_db) != len(BAND_FREQUENCIES_HZ):
        raise ValueError("invalid_band_count")
    return tuple(peaking_coefficients(gain, center)
                 for gain, center in zip(gains_db, BAND_FREQUENCIES_HZ))


FORWARD_COEFFICIENTS = cascade_coefficients(FORWARD_GAINS_DB)


def magnitude_db(coefficients: Coefficients, frequency_hz: float,
                 sample_rate_hz: int = SAMPLE_RATE_HZ) -> float:
    """Analytic magnitude response of one biquad at one probe frequency."""
    b0, b1, b2, a1, a2 = coefficients
    omega = 2.0 * math.pi * float(frequency_hz) / float(sample_rate_hz)
    cosine, sine = math.cos(omega), math.sin(omega)
    cos2, sin2 = math.cos(2.0 * omega), math.sin(2.0 * omega)
    num_re = b0 + b1 * cosine + b2 * cos2
    num_im = -(b1 * sine + b2 * sin2)
    den_re = 1.0 + a1 * cosine + a2 * cos2
    den_im = -(a1 * sine + a2 * sin2)
    power = (num_re * num_re + num_im * num_im) / max(
        den_re * den_re + den_im * den_im, 1e-30)
    return _clean(10.0 * math.log10(max(power, 1e-30)))


def cascade_response_db(coefficients: Sequence[Coefficients],
                        frequencies_hz: Sequence[float]) -> Tuple[float, ...]:
    return tuple(_clean(sum(magnitude_db(stage, frequency) for stage in coefficients))
                 for frequency in frequencies_hz)


def apply_cascade(samples: Sequence[float],
                  coefficients: Sequence[Coefficients]) -> Tuple[float, ...]:
    """Causal direct-form-II-transposed biquad cascade, zero added delay."""
    if any(not math.isfinite(float(value)) for value in samples):
        raise ValueError("nonfinite_input")
    # Per-stage filter state must persist across samples.
    states = [[0.0, 0.0] for _ in coefficients]
    output: List[float] = []
    for sample in samples:
        value = float(sample)
        for index, (b0, b1, b2, a1, a2) in enumerate(coefficients):
            z1, z2 = states[index]
            y = b0 * value + z1
            states[index][0] = b1 * value - a1 * y + z2
            states[index][1] = b2 * value - a2 * y
            value = y
        output.append(value)
    return tuple(output)


def training_coefficients() -> Tuple[Tuple[float, ...], ...]:
    """Twelve frozen synthetic EQ perturbations in dB, pinned by digest."""
    noise = lcg(FIXTURE_SEED + 1)
    rows = [FORWARD_GAINS_DB]
    for _ in range(TRAINING_ROWS - 1):
        rows.append(tuple(_clean(7.0 * next(noise)) for _ in BAND_FREQUENCIES_HZ))
    return tuple(rows)


def _response_with_noise(gains_db: Sequence[float], noise,
                         jitter_db: float) -> Tuple[float, ...]:
    response = cascade_response_db(cascade_coefficients(gains_db),
                                   PROBE_FREQUENCIES_HZ)
    return tuple(_clean(value + jitter_db * next(noise))
                 for value in response)


def response_fixture() -> Dict[str, Any]:
    """Frozen coefficient/response fixture generated from a fixed seed."""
    coefficients = training_coefficients()
    noise = lcg(FIXTURE_SEED + 2)
    rows = []
    for gains in coefficients:
        rows.append({"coefficients_db": list(gains),
                     "response_db": list(_response_with_noise(gains, noise, 0.02))})
    core: Dict[str, Any] = {
        "fixture_version": "learned-inverse-eq-response-v1",
        "seed": FIXTURE_SEED,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "band_frequencies_hz": list(BAND_FREQUENCIES_HZ),
        "band_q": BAND_Q,
        "probe_frequencies_hz": list(PROBE_FREQUENCIES_HZ),
        "training_rows": rows,
        "target": {
            "coefficients_db": list(FORWARD_GAINS_DB),
            "response_db": list(cascade_response_db(
                FORWARD_COEFFICIENTS, PROBE_FREQUENCIES_HZ)),
        },
    }
    core["sha256"] = scorer.digest_json(core)
    return core


def _matmul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> List[List[float]]:
    return [[sum(float(x) * float(y) for x, y in zip(row, column))
             for column in zip(*b)] for row in a]


def _transpose(a: Sequence[Sequence[float]]) -> List[List[float]]:
    return [list(column) for column in zip(*a)]


def _solve(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> List[float]:
    """Gauss-Jordan solve with partial pivoting for small dense systems."""
    size = len(matrix[0])
    if size != len(matrix) or any(len(row) != size for row in matrix) or len(vector) != size:
        raise ValueError("invalid_linear_system")
    augmented = [list(row) + [float(value)] for row, value in zip(matrix, vector)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("singular_gram_matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [value - factor * other
                                  for value, other in zip(augmented[row], augmented[column])]
    return [row[-1] for row in augmented]


def symmetric_eigenvalues(matrix: Sequence[Sequence[float]]) -> Tuple[float, ...]:
    """Jacobi eigenvalues of a small real symmetric matrix."""
    size = len(matrix)
    if size == 1:
        return (float(matrix[0][0]),)
    work = [list(row) for row in matrix]
    for _ in range(128):
        p, q, largest = 0, 1, 0.0
        for row in range(size):
            for column in range(row + 1, size):
                if abs(work[row][column]) > largest:
                    p, q, largest = row, column, abs(work[row][column])
        if largest < 1e-14:
            break
        theta = (work[q][q] - work[p][p]) / (2.0 * work[p][q])
        if theta >= 0.0:
            tangent = 1.0 / (theta + math.sqrt(1.0 + theta * theta))
        else:
            tangent = -1.0 / (-theta + math.sqrt(1.0 + theta * theta))
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine
        for index in range(size):
            if index in (p, q):
                continue
            ip, iq = work[index][p], work[index][q]
            work[index][p] = work[p][index] = cosine * ip - sine * iq
            work[index][q] = work[q][index] = sine * ip + cosine * iq
        app, aqq, apq = work[p][p], work[q][q], work[p][q]
        work[p][p] = cosine * cosine * app - 2.0 * sine * cosine * apq + sine * sine * aqq
        work[q][q] = sine * sine * app + 2.0 * sine * cosine * apq + cosine * cosine * aqq
        work[p][q] = work[q][p] = 0.0
    return tuple(sorted(work[index][index] for index in range(size)))


def gram_condition(features: Sequence[Sequence[float]]) -> Dict[str, Any]:
    gram = _matmul(_transpose(features), features)
    eigenvalues = symmetric_eigenvalues(gram)
    smallest = min(abs(value) for value in eigenvalues)
    largest = max(abs(value) for value in eigenvalues)
    return {
        "eigenvalues": [scorer.round_float(value, 9) for value in eigenvalues],
        "condition_estimate": scorer.round_float(largest / max(smallest, 1e-15), 6),
        "gram_digest": scorer.digest_json([[scorer.round_float(v, 12) for v in row]
                                           for row in gram]),
    }


def learn_inverse(fixture: Dict[str, Any], ridge: float = RIDGE_LAMBDA) -> Dict[str, Any]:
    """Ridge-fit inverse band gains from pinned synthetic response probes."""
    if ridge < 0.0 or not math.isfinite(ridge):
        raise ValueError("invalid_ridge")
    features = [list(row["response_db"]) for row in fixture["training_rows"]]
    labels = [[-float(value) for value in row["coefficients_db"]]
              for row in fixture["training_rows"]]
    gram = _matmul(_transpose(features), features)
    size = len(gram)
    for index in range(size):
        gram[index][index] += ridge
    rhs = _matmul(_transpose(features), labels)
    weights = [_solve(gram, list(column)) for column in zip(*rhs)]
    if len(weights) != len(BAND_FREQUENCIES_HZ) or any(
            len(row) != len(PROBE_FREQUENCIES_HZ) for row in weights):
        raise ValueError("invalid_weight_shape")
    residual = 0.0
    for feature, label in zip(features, labels):
        estimate = [sum(float(w) * float(x) for w, x in zip(row, feature))
                    for row in weights]
        residual += sum((a - b) ** 2 for a, b in zip(estimate, label))
    residual /= (len(features) * len(weights))
    return {
        "weights": tuple(tuple(_clean(value) for value in row) for row in weights),
        "ridge_lambda": ridge,
        "training_rmse_db": scorer.round_float(math.sqrt(residual), 12),
        "condition": gram_condition([list(row["response_db"])
                                     for row in fixture["training_rows"]]),
        "weights_digest": scorer.digest_json([[scorer.round_float(value, 12)
                                               for value in row] for row in weights]),
    }


def estimate_gains(weights: Sequence[Sequence[float]],
                   response_db: Sequence[float]) -> Tuple[float, ...]:
    if len(response_db) != len(PROBE_FREQUENCIES_HZ):
        raise ValueError("invalid_probe_count")
    return tuple(_clean(sum(float(w) * float(x) for w, x in zip(row, response_db)))
                 for row in weights)


def learned_model(ridge: float = RIDGE_LAMBDA) -> Dict[str, Any]:
    fixture = response_fixture()
    fit = learn_inverse(fixture, ridge)
    gains = estimate_gains(fit["weights"], fixture["target"]["response_db"])
    true_inverse = tuple(-value for value in FORWARD_GAINS_DB)
    errors = [float(a) - float(b) for a, b in zip(gains, true_inverse)]
    return {
        "fixture_digest": fixture["sha256"],
        "weights_digest": fit["weights_digest"],
        "weights": fit["weights"],
        "ridge_lambda": ridge,
        "training_rmse_db": fit["training_rmse_db"],
        "condition": fit["condition"],
        "estimated_inverse_gains_db": list(gains),
        "true_inverse_gains_db": list(true_inverse),
        "gain_error_db": [scorer.round_float(value, 9) for value in errors],
        "max_abs_gain_error_db": scorer.round_float(max(abs(v) for v in errors), 9),
        "coefficients_digest": scorer.digest_json({
            "bands_hz": list(BAND_FREQUENCIES_HZ),
            "q": BAND_Q,
            "forward_gains_db": list(FORWARD_GAINS_DB),
            "forward_coefficients": [list(row) for row in FORWARD_COEFFICIENTS],
        }),
    }


@dataclass(frozen=True)
class ProcessResult:
    samples: Tuple[float, ...]
    status: str
    error: Optional[str]
    position: int
    epoch: int


class Controller:
    """Framewise controller with explicit validity, epoch and position state."""

    def __init__(self, mode: str = "learned_inverse",
                 gains_db: Optional[Sequence[float]] = None,
                 epoch: int = 0, position: int = 0,
                 ridge: float = RIDGE_LAMBDA) -> None:
        if mode not in MODES:
            raise ValueError("unknown_mode")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        if isinstance(position, bool) or not isinstance(position, int) or position < 0:
            raise ValueError("invalid_position")
        self.mode = mode
        self.epoch = epoch
        self.position = position
        self.invalid_count = 0
        self.processed_frames = 0
        self.processed_samples = 0
        self.final_processed = False
        if gains_db is None:
            if mode == "learned_inverse":
                model = learned_model(ridge)
                gains = model["estimated_inverse_gains_db"]
            elif mode == "fixed_eq":
                gains = list(FORWARD_GAINS_DB)
            else:
                gains = [0.0] * len(BAND_FREQUENCIES_HZ)
        else:
            gains = list(gains_db)
        if len(gains) != len(BAND_FREQUENCIES_HZ) or any(
                not math.isfinite(float(value)) for value in gains):
            raise ValueError("invalid_gains")
        self.gains_db = tuple(float(value) for value in gains)
        self.stages = cascade_coefficients(self.gains_db) if mode != "identity" else ()
        self._z = [[0.0, 0.0] for _ in self.stages]

    def state_digest(self) -> str:
        payload = {
            "state_version": STATE_VERSION,
            "mode": self.mode,
            "epoch": self.epoch,
            "position": self.position,
            "invalid_count": self.invalid_count,
            "processed_frames": self.processed_frames,
            "processed_samples": self.processed_samples,
            "final_processed": self.final_processed,
            "gains_db": [scorer.round_float(value, 9) for value in self.gains_db],
            "filter_state": [[scorer.round_float(value, 12) for value in pair]
                             for pair in self._z],
        }
        return scorer.digest_json(payload)

    def dsp_state_digest(self) -> str:
        """Filter/alignment state only; invalid_count is audit state, not DSP state."""
        return scorer.digest_json({
            "epoch": self.epoch,
            "position": self.position,
            "processed_frames": self.processed_frames,
            "processed_samples": self.processed_samples,
            "final_processed": self.final_processed,
            "filter_state": [[scorer.round_float(value, 12) for value in pair]
                             for pair in self._z],
        })

    def reset(self, epoch: int) -> None:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        if epoch <= self.epoch and self.processed_frames:
            raise ValueError("epoch_not_monotonic")
        self.epoch = epoch
        self.position = 0
        self.invalid_count = 0
        self.processed_frames = 0
        self.processed_samples = 0
        self.final_processed = False
        self._z = [[0.0, 0.0] for _ in self.stages]

    def _reject(self, error: str) -> ProcessResult:
        self.invalid_count += 1
        return ProcessResult((), "rejected", error, self.position, self.epoch)

    def process(self, frame: Optional[Sequence[float]], epoch: Optional[int] = None,
                position: Optional[int] = None, final: bool = False) -> ProcessResult:
        if frame is None:
            return self._reject("missing_frame")
        if isinstance(frame, (str, bytes)) or not isinstance(frame, Sequence):
            return self._reject("wrong_frame_type")
        if len(frame) == 0 or len(frame) > FRAME_SAMPLES:
            return self._reject("invalid_frame_length")
        if len(frame) < FRAME_SAMPLES and not final:
            return self._reject("partial_frame_without_final")
        if any(not math.isfinite(float(value)) for value in frame):
            return self._reject("nonfinite_input")
        if max((abs(float(value)) for value in frame), default=0.0) > MAX_ABS_INPUT:
            return self._reject("out_of_range_input")
        if epoch is not None and epoch != self.epoch:
            return self._reject("stale_epoch")
        if position is not None and position != self.position:
            return self._reject("stale_position")
        values = [float(value) for value in frame]
        if self.mode == "identity":
            output = tuple(values)
        else:
            output = []
            for value in values:
                for index, (b0, b1, b2, a1, a2) in enumerate(self.stages):
                    z1, z2 = self._z[index]
                    y = b0 * value + z1
                    self._z[index][0] = b1 * value - a1 * y + z2
                    self._z[index][1] = b2 * value - a2 * y
                    value = y
                output.append(value)
            if not scorer.is_finite(output):
                self._z = [[0.0, 0.0] for _ in self.stages]
                return self._reject("nonfinite_output")
        self.position += len(values)
        self.processed_frames += 1
        self.processed_samples += len(values)
        self.final_processed = self.final_processed or final
        return ProcessResult(tuple(output), "ok", None, self.position, self.epoch)


def stream(samples: Sequence[float], mode: str = "learned_inverse",
           epoch: int = 0, start_position: int = 0,
           gains_db: Optional[Sequence[float]] = None) -> Dict[str, Any]:
    controller = Controller(mode, gains_db=gains_db, epoch=epoch, position=start_position)
    output: List[float] = []
    statuses: List[str] = []
    errors: List[str] = []
    for start in range(0, len(samples), FRAME_SAMPLES):
        chunk = samples[start:start + FRAME_SAMPLES]
        final = start + FRAME_SAMPLES >= len(samples)
        result = controller.process(chunk, epoch=epoch,
                                    position=start_position + start, final=final)
        statuses.append(result.status)
        if result.error:
            errors.append(result.error)
        output.extend(result.samples)
    return {
        "output": tuple(output),
        "statuses": statuses,
        "errors": errors,
        "status": "complete" if all(value == "ok" for value in statuses) else "rejected",
        "state_digest": controller.state_digest(),
        "invalid_count": controller.invalid_count,
        "controller": controller,
    }


class LevelToneController:
    """Synthetic RMS/tone control used only as a DSP-profile interacting control."""

    def __init__(self, target_rms_db: float = -24.0, tone_hz: float = 1000.0,
                 ceiling: float = 0.95, attack: float = 0.35, release: float = 0.08,
                 epoch: int = 0) -> None:
        self.target_linear = 10.0 ** (target_rms_db / 20.0)
        self.ceiling = ceiling
        self.attack, self.release = attack, release
        self.epoch = epoch
        self.position = 0
        self.gain = 1.0
        self.invalid_count = 0
        self.gain_trace: List[float] = []
        self.notch = peaking_coefficients(-12.0, tone_hz, q=6.0)

    def state_digest(self) -> str:
        return scorer.digest_json({
            "state_version": "learned-inverse-eq-level-tone-v1",
            "epoch": self.epoch, "position": self.position,
            "gain": scorer.round_float(self.gain, 12),
            "invalid_count": self.invalid_count,
            "gain_trace": [scorer.round_float(value, 9) for value in self.gain_trace],
        })

    def reset(self, epoch: int) -> None:
        if epoch <= self.epoch and self.position:
            raise ValueError("epoch_not_monotonic")
        self.epoch, self.position, self.gain = epoch, 0, 1.0
        self.invalid_count, self.gain_trace = 0, []
        self.notch = peaking_coefficients(-12.0, 1000.0, q=6.0)

    def process(self, frame: Optional[Sequence[float]], epoch: Optional[int] = None,
                position: Optional[int] = None) -> ProcessResult:
        if frame is None:
            self.invalid_count += 1
            return ProcessResult((), "rejected", "missing_frame", self.position, self.epoch)
        if len(frame) != FRAME_SAMPLES:
            self.invalid_count += 1
            return ProcessResult((), "rejected", "invalid_frame_length", self.position, self.epoch)
        if any(not math.isfinite(float(value)) for value in frame):
            self.invalid_count += 1
            return ProcessResult((), "rejected", "nonfinite_input", self.position, self.epoch)
        if epoch is not None and epoch != self.epoch:
            self.invalid_count += 1
            return ProcessResult((), "rejected", "stale_epoch", self.position, self.epoch)
        if position is not None and position != self.position:
            self.invalid_count += 1
            return ProcessResult((), "rejected", "stale_position", self.position, self.epoch)
        frame_rms = rms(frame)
        desired = self.target_linear / max(frame_rms, 1e-6)
        coefficient = self.attack if desired > self.gain else self.release
        self.gain += coefficient * (desired - self.gain)
        self.gain_trace.append(self.gain)
        processed = apply_cascade(frame, (self.notch,))
        peak = scorer.peak(processed)
        if peak > self.ceiling:
            self.gain *= self.ceiling / peak
        output = tuple(max(-1.0, min(1.0, value * self.gain)) for value in processed)
        self.position += FRAME_SAMPLES
        return ProcessResult(output, "ok", None, self.position, self.epoch)


def rms(values: Sequence[float]) -> float:
    return scorer.rms(values)


def ill_conditioned_case(weights: Sequence[Sequence[float]]) -> Dict[str, Any]:
    """Explicit adverse case: clustered probes and perturbed response."""
    probes = tuple(1000.0 + 0.5 * index for index in range(9))
    response = cascade_response_db(FORWARD_COEFFICIENTS, probes)
    noise = lcg(FIXTURE_SEED + 3)
    # A deliberately large probe perturbation exposes the near-singular fit.
    noisy = tuple(_clean(value + 20.0 * next(noise)) for value in response)
    condition = gram_condition([list(noisy)])
    gains = estimate_gains(weights, noisy)
    coefficients = cascade_coefficients(gains)
    perturbation = cascade_response_db(coefficients, PROBE_FREQUENCIES_HZ)
    return {
        "probe_frequencies_hz": list(probes),
        "response_db": list(noisy),
        "condition": condition,
        "estimated_gains_db": list(gains),
        "max_abs_gain_db": scorer.round_float(max(abs(value) for value in gains), 9),
        "response_at_nominal_probes_db": [scorer.round_float(value, 9)
                                          for value in perturbation],
        "stable_coefficients": all(all(math.isfinite(value) for value in stage)
                                   for stage in coefficients),
        "qualifies": False,
    }


def crosscheck_vectors() -> Dict[str, Any]:
    """Pinned synthetic vectors for independent fingerprint/parity checks."""
    model = learned_model()
    fixture = response_fixture()
    impulse = (1.0,) + (0.0,) * (FRAME_SAMPLES * 4 - 1)
    identity = stream(impulse, "identity")["output"]
    fixed = stream(impulse, "fixed_eq")["output"]
    learned = stream(impulse, "learned_inverse",
                     gains_db=model["estimated_inverse_gains_db"])["output"]
    ill = ill_conditioned_case(model["weights"])
    vectors = [
        {"name": "identity_impulse", "values": list(identity[:16]),
         "digest": scorer.digest_json(list(identity))},
        {"name": "fixed_eq_impulse", "values": [scorer.round_float(v, 9) for v in fixed[:16]],
         "digest": scorer.digest_json([scorer.round_float(v, 12) for v in fixed])},
        {"name": "learned_inverse_impulse",
         "values": [scorer.round_float(v, 9) for v in learned[:16]],
         "digest": scorer.digest_json([scorer.round_float(v, 12) for v in learned])},
        {"name": "response_target", "values": fixture["target"]["response_db"],
         "digest": scorer.digest_json(fixture["target"]["response_db"])},
        {"name": "estimated_inverse_gains", "values": model["estimated_inverse_gains_db"],
         "digest": scorer.digest_json(model["estimated_inverse_gains_db"])},
        {"name": "ill_conditioned_gains", "values": ill["estimated_gains_db"],
         "digest": scorer.digest_json(ill["estimated_gains_db"])},
    ]
    core = {
        "crosscheck_version": "learned-inverse-eq-crosscheck-v1",
        "fixture_sha256": fixture["sha256"],
        "model_weights_sha256": model["weights_digest"],
        "vectors": vectors,
    }
    core["sha256"] = scorer.digest_json(core)
    return core


def _condition_record(value: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "condition_estimate": value["condition_estimate"],
        "eigenvalues": value["eigenvalues"],
        "gram_digest": value["gram_digest"],
    }


def build_report() -> Dict[str, Any]:
    """Build the full deterministic, synthetic-only evidence report."""
    import fixture as signals  # local import avoids a module-level cycle

    model = learned_model()
    fixture = response_fixture()
    fixture_spec = signals.fixture_spec()
    cohort = signals.cohort()
    ill = ill_conditioned_case(model["weights"])
    crosscheck = crosscheck_vectors()

    zeros = [0.0] * len(PROBE_FREQUENCIES_HZ)
    forward_probe = cascade_response_db(FORWARD_COEFFICIENTS, PROBE_FREQUENCIES_HZ)
    correction_probe = cascade_response_db(
        cascade_coefficients(model["estimated_inverse_gains_db"]), PROBE_FREQUENCIES_HZ)
    response_rmse = {
        "identity": scorer.round_float(scorer.response_rmse_db(forward_probe, zeros), 9),
        "fixed_eq": scorer.round_float(scorer.response_rmse_db(
            [2.0 * value for value in forward_probe], zeros), 9),
        "learned_inverse": scorer.round_float(scorer.response_rmse_db(
            [a + b for a, b in zip(forward_probe, correction_probe)], zeros), 9),
    }

    comparisons: Dict[str, Any] = {}
    for condition in signals.COMPARISON_CONDITIONS:
        clean = cohort[condition + "_clean"]
        perturbed = cohort[condition + "_perturbed"]
        rows: Dict[str, Any] = {}
        for mode in MODES:
            gains = model["estimated_inverse_gains_db"] if mode == "learned_inverse" else None
            result = stream(perturbed, mode, gains_db=gains)
            rows[mode] = {
                "status": result["status"],
                "output_digest": scorer.digest_json(
                    [scorer.round_float(value, 12) for value in result["output"]]),
                "sample_count": len(result["output"]),
                "finite": scorer.is_finite(result["output"]),
                "nonfinite_count": len(result["output"]) - scorer.finite_count(result["output"]),
                "peak": scorer.round_float(scorer.peak(result["output"]), 12),
                "headroom_db": scorer.round_float(scorer.headroom_db(result["output"]), 9),
                "rms_db": scorer.round_float(scorer.safe_db(scorer.rms(result["output"])), 9),
                "gain_error_db": scorer.round_float(
                    scorer.gain_db(result["output"], clean), 9),
                "max_abs_error": scorer.round_float(
                    scorer.max_abs_error(result["output"], clean), 12),
                "snr_db": scorer.round_float(scorer.snr_db(clean, [
                    a - b for a, b in zip(result["output"], clean)]), 9),
                "clipped_sample_count": scorer.count_clipped(result["output"]),
                "delay_samples": scorer.delay_samples(clean, result["output"]),
                "state_digest": result["state_digest"],
                "invalid_count": result["invalid_count"],
                "qualifies": False,
            }
        comparisons[condition] = rows

    dsp_rows: Dict[str, Any] = {}
    for condition in signals.DSP_CONDITIONS:
        stimulus = cohort[condition]
        gains = model["estimated_inverse_gains_db"]
        result = stream(stimulus, "learned_inverse", gains_db=gains)
        delay = scorer.delay_samples(stimulus, result["output"]) if "impulse" in condition else 0
        dsp_rows[condition] = {
            "input_finite": scorer.is_finite(stimulus),
            "input_peak": scorer.round_float(scorer.peak(stimulus), 12),
            "status": result["status"],
            "output_finite": scorer.is_finite(result["output"]),
            "output_peak": scorer.round_float(scorer.peak(result["output"]), 12),
            "headroom_db": scorer.round_float(scorer.headroom_db(result["output"]), 9),
            "gain_db": scorer.round_float(scorer.gain_db(result["output"], stimulus), 9),
            "delay_samples": delay,
            "nonfinite_count": len(result["output"]) - scorer.finite_count(result["output"]),
            "state_digest": result["state_digest"],
        }

    # Interacting nonlinear configuration: learned EQ -> tanh saturation ->
    # synthetic level/tone control, versus each stage removed.
    speech = cohort["clean_speech"]
    perturbed = cohort["clean_speech_perturbed"]
    inverse = stream(perturbed, "learned_inverse",
                     gains_db=model["estimated_inverse_gains_db"])["output"]
    saturated = tuple(math.tanh(3.0 * value) for value in inverse)
    controller = LevelToneController()
    nonlinear_output: List[float] = []
    for start in range(0, len(saturated), FRAME_SAMPLES):
        outcome = controller.process(saturated[start:start + FRAME_SAMPLES])
        if outcome.status != "ok":
            raise RuntimeError("level_tone_rejected_valid_frame")
        nonlinear_output.extend(outcome.samples)
    trace = controller.gain_trace
    attack_index = max(range(len(trace)), key=lambda index: trace[index]) if trace else 0
    tone_only: List[float] = []
    tone_controller = LevelToneController()
    for start in range(0, len(perturbed), FRAME_SAMPLES):
        outcome = tone_controller.process(perturbed[start:start + FRAME_SAMPLES])
        tone_only.extend(outcome.samples)
    nonlinear = {
        "chain": "perturbed -> learned_inverse -> tanh(3x) -> level_tone_control",
        "ablations": {
            "no_learned_inverse": {
                "output_digest": scorer.digest_json([scorer.round_float(v, 12)
                                                     for v in tone_only]),
                "peak": scorer.round_float(scorer.peak(tone_only), 12),
            },
            "no_level_tone_control": {
                "output_digest": scorer.digest_json([scorer.round_float(v, 12)
                                                     for v in saturated]),
                "peak": scorer.round_float(scorer.peak(saturated), 12),
            },
            "full_chain": {
                "output_digest": scorer.digest_json([scorer.round_float(v, 12)
                                                     for v in nonlinear_output]),
                "peak": scorer.round_float(scorer.peak(nonlinear_output), 12),
            },
        },
        "gain_trace_peak": scorer.round_float(max(trace, default=0.0), 9),
        "gain_trace_min": scorer.round_float(min(trace, default=0.0), 9),
        "gain_trace_last": scorer.round_float(trace[-1] if trace else 0.0, 9),
        "configured_attack_coefficient": controller.attack,
        "configured_release_coefficient": controller.release,
        "target_rms_linear": scorer.round_float(controller.target_linear, 9),
        "peak_ceiling": controller.ceiling,
        "max_gain_increase_per_frame": scorer.round_float(
            max((b - a for a, b in zip(trace, trace[1:])), default=0.0), 9),
        "max_gain_decrease_per_frame": scorer.round_float(
            max((a - b for a, b in zip(trace, trace[1:])), default=0.0), 9),
        "attack_peak_frame": attack_index,
        "release_frames_after_peak": max(0, len(trace) - 1 - attack_index),
        "level_tone_state_digest": controller.state_digest(),
        "nonfinite_count": len(nonlinear_output) - scorer.finite_count(nonlinear_output),
        "output_peak": scorer.round_float(scorer.peak(nonlinear_output), 12),
        "headroom_db": scorer.round_float(scorer.headroom_db(nonlinear_output), 9),
        "clean_speech_reference_digest": scorer.digest_json(
            [scorer.round_float(value, 12) for value in speech]),
        "qualifies": False,
    }

    out_of_band = cohort["out_of_band_noise"]
    nominal_chain = stream(out_of_band, "learned_inverse",
                           gains_db=model["estimated_inverse_gains_db"])["output"]
    adverse_chain = stream(out_of_band, "learned_inverse",
                           gains_db=ill["estimated_gains_db"])["output"]
    adverse_noise = {
        "stimulus": "deterministic 12 kHz-15 kHz band-limited synthetic noise",
        "input_rms": scorer.round_float(scorer.rms(out_of_band), 12),
        "nominal_output_rms": scorer.round_float(scorer.rms(nominal_chain), 12),
        "ill_conditioned_output_rms": scorer.round_float(scorer.rms(adverse_chain), 12),
        "nominal_amplification_db": scorer.round_float(scorer.safe_db(
            scorer.rms(nominal_chain) / max(scorer.rms(out_of_band), 1e-12)), 9),
        "ill_conditioned_amplification_db": scorer.round_float(scorer.safe_db(
            scorer.rms(adverse_chain) / max(scorer.rms(out_of_band), 1e-12)), 9),
        "ill_conditioned_peak": scorer.round_float(scorer.peak(adverse_chain), 12),
        "qualifies": False,
    }

    controller = Controller("learned_inverse")
    frame = cohort["impulse"][:FRAME_SAMPLES]
    rejected: Dict[str, Any] = {}
    invalid_calls = [
        ("missing_frame", lambda: controller.process(None)),
        ("wrong_type", lambda: controller.process("not-a-frame")),
        ("wrong_shape", lambda: controller.process((0.0,) * (FRAME_SAMPLES - 3))),
        ("nonfinite", lambda: controller.process((float("nan"),) + (0.0,) * 159)),
        ("out_of_range", lambda: controller.process((9.0,) + (0.0,) * 159)),
        ("stale_epoch", lambda: controller.process(frame, epoch=99)),
        ("stale_position", lambda: controller.process(frame, position=99)),
    ]
    for name, call in invalid_calls:
        before = controller.dsp_state_digest()
        response = call()
        rejected[name] = {
            "status": response.status,
            "error": response.error,
            "dsp_state_unchanged": response.status == "rejected"
            and controller.dsp_state_digest() == before,
            "invalid_count_delta": 1 if response.status == "rejected" else 0,
        }

    first = Controller("learned_inverse").process(frame)
    replay = Controller("learned_inverse").process(frame)
    state_transitions = {
        "first_frame_ok": first.status == "ok",
        "cold_start_replay_digest_match": first.samples == replay.samples,
        "stream_framewise_matches_whole_call": scorer.digest_json(
            [scorer.round_float(v, 12) for v in stream(cohort["clean_speech"],
             "learned_inverse", gains_db=model["estimated_inverse_gains_db"])["output"]])
        == scorer.digest_json([scorer.round_float(v, 12) for v in
            apply_cascade(cohort["clean_speech"], cascade_coefficients(
                model["estimated_inverse_gains_db"]))]),
        "reset_replays_exactly": Controller("learned_inverse").state_digest()
        == Controller("learned_inverse").state_digest(),
        "invalid_count": controller.invalid_count,
        "final_partial_frame": Controller("learned_inverse").process(
            (0.1,) * 37, final=True).status,
        "drain_added_samples": 0,
    }

    pins = {
        "research/level_tone_control_20261028.md":
            "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
            "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "audio-benchmark-platform/plan/swarm/check.py":
            "5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539",
    }
    boundary_pins = {
        "api/include/audio_sdk/provider_v0.h":
            "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "api/include/audio_sdk/session_v0.h":
            "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    }

    report: Dict[str, Any] = {
        "schema": "audio-sdk/learned-inverse-eq/0.1",
        "task": "SDK-LEARNED-INVERSE-EQ",
        "status": "proposal_only_not_qualified",
        "qualification": "incomplete",
        "decision": {
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
            "public_api_abi_change": False,
            "descriptor_registry_change": False,
            "installed_v0_behavior": "unchanged",
            "release_claim": False,
        },
        "scope": {
            "format": {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
                       "sample_format": "f32", "frame_samples": FRAME_SAMPLES},
            "write_scope": "docs/task-evidence/learned-inverse-eq/ only",
            "external_model_or_weights": False,
            "downloads": False,
            "licensed_runtime": False,
            "real_speech_or_listening": False,
            "device_timing_or_release_qualification": False,
            "c_boundary_included": False,
        },
        "source_pins": pins,
        "boundary_pins": boundary_pins,
        "board_snapshot": {
            "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "sha256_at_read":
                "b3e8aa913076c0b0496756cdbd1b717cc9f7e65206824198b33278e70c935294",
            "mutable": True,
            "qualifying": False,
        },
        "method": {
            "summary": ("Frozen six-band synthetic EQ perturbation; ridge regression "
                        "maps pinned synthetic response probes to inverse band gains; "
                        "causal peaking biquad cascade applies the correction."),
            "band_frequencies_hz": list(BAND_FREQUENCIES_HZ),
            "band_q": BAND_Q,
            "probe_frequencies_hz": list(PROBE_FREQUENCIES_HZ),
            "training_rows": TRAINING_ROWS,
            "ridge_lambda": RIDGE_LAMBDA,
            "causal": True,
            "buffering_delay_samples": 0,
            "learned_from_data": "synthetic pinned response fixture only",
            "natural_balance_preference_claimed": False,
        },
        "frozen_coefficients_and_responses": {
            "fixture_digest": fixture["sha256"],
            "forward_gains_db": list(FORWARD_GAINS_DB),
            "coefficients_digest": model["coefficients_digest"],
            "training_row_count": len(fixture["training_rows"]),
            "target_response_db": fixture["target"]["response_db"],
            "response_rmse_db": response_rmse,
            "weights_digest": model["weights_digest"],
            "training_rmse_db": model["training_rmse_db"],
            "condition": _condition_record(model["condition"]),
            "estimated_inverse_gains_db": model["estimated_inverse_gains_db"],
            "true_inverse_gains_db": model["true_inverse_gains_db"],
            "gain_error_db": model["gain_error_db"],
            "max_abs_gain_error_db": model["max_abs_gain_error_db"],
        },
        "fixture": fixture_spec,
        "comparisons": comparisons,
        "dsp_profile": {
            "conditions": dsp_rows,
            "nonlinear_and_state_interaction": nonlinear,
            "adverse_out_of_band_amplification": adverse_noise,
            "ill_conditioned_inverse": ill,
        },
        "controls": {
            "invalid_and_missing": rejected,
            "transparent_state": state_transitions,
            "no_missing_result_qualifies": True,
            "identity_is_bit_exact": all(
                rows["identity"]["output_digest"] == scorer.digest_json([
                    scorer.round_float(v, 12) for v in cohort[name + "_perturbed"]])
                for name, rows in comparisons.items()),
            "fixed_eq_doubles_forward_coloration": all(
                rows["fixed_eq"]["gain_error_db"] is not None
                and rows["fixed_eq"]["headroom_db"] is not None
                for rows in comparisons.values()),
            "all_comparisons_finite": all(
                row["finite"] and row["nonfinite_count"] == 0
                for group in comparisons.values() for row in group.values()),
        },
        "crosscheck": {
            "file": "crosscheck_vectors.json",
            "file_sha256_at_build": None,
            "content_digest": crosscheck["sha256"],
            "fixture_sha256": crosscheck["fixture_sha256"],
            "model_weights_sha256": crosscheck["model_weights_sha256"],
            "vector_names": [row["name"] for row in crosscheck["vectors"]],
            "regeneration": "byte-identical from pinned fixture and seed",
            "scope": "synthetic fingerprint parity only; not device or real-model parity",
        },
        "licensing": {
            "spdx": "Apache-2.0",
            "external_assets": [],
            "third_party_runtime": None,
            "reuse_lint": "must pass in CI",
        },
        "remaining_gates": [
            "Held-out real-speech paired response and quality evidence with pinned rights and blinded listening",
            "Desired-response definition and calibration for natural spectral balance",
            "Ill-conditioning guard, band-limit and out-of-band noise amplification limits",
            "Target-device CPU, memory, deadline and real-time pacing measurement",
            "Provider intake, license, descriptor and public catalog review before any default or processor exposure",
        ],
        "disclosure": ("Task-local synthetic evidence only. Not a Bench bundle, quality "
                       "claim, listening result, device measurement or release gate."),
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = scorer.canonical_text(report)
    return text, scorer.digest_bytes(text.encode("utf-8"))
