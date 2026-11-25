# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Rate-profile fixture: caller-supplied frozen features plus a ridge head.

Task-local, proposal-only, incomplete and not qualified. The named model is
used only as a *caller-supplied frozen feature extractor*: this fixture never
loads, downloads or executes its weights. A small ridge regressor maps the
caller's vectors to a measured syllable rate in syllables/second. The model's
adult/child classification head is explicitly unused, and neither age nor
listener-preferred speed is claimed.

No real audio, labels, device timing or listening test is used. The installed
v0 geometry is untouched: 16 kHz, mono, float32, 160 samples per call.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass
from typing import Any, Callable, Sequence

CONTRACT_ID = "audio-sdk/distil-wav2vec2-frozen-rate-ridge/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/distil-wav2vec2-frozen-rate-ridge/report/0.1"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
PROVIDER_ID = "analysis.distil-wav2vec2-frozen-rate-ridge.v0"
MODEL_ID = "bookbot/distil-wav2vec2-adult-child-cls-37m"
TASK_ID = "SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
WINDOW_FRAMES = 400  # four-second analysis window, v0-shaped cadence
WINDOW_SAMPLES = WINDOW_FRAMES * FRAME_SAMPLES
SAMPLE_FORMAT = "f32"
SAMPLE_NS = 62500
CLOCK_ID = "fixture-monotonic-v0"
ORIGIN_NS = 1767225600000000000

SEED = 20261124
TOTAL_WINDOWS = 210
FOLDS = 5
FOLD_SIZE = TOTAL_WINDOWS // FOLDS
CALIBRATION_FOLDS = (0, 1, 2, 3)  # alpha is fixed a priori; fold 4 is never tuned on
EVALUATION_FOLD = 4
EMBED_DIM = 16
RIDGE_ALPHA = 10.0
CANONICAL_FLOAT_DIGITS = 9  # portable canonical bytes across Python 3.10-3.12
MIN_CANONICAL_PYTHON = (3, 10)
EXACT_REGENERATION_PYTHON = (3, 12, 16)
EXTRACTOR_REVISION_CLAIM = "caller-pinned-not-verified"

STRATA = ("clean", "short_active", "overlap", "quiet_boundary")
ACTIVE_SECONDS = {
    "clean": 3.8,
    "short_active": 2.0,
    "overlap": 3.2,
    "quiet_boundary": 3.6,
}

SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 geometry, exact source intervals, decimal-string sample/time serialization and analysis-event validity.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Analysis acceptance profile: timestamped events, validity, state isolation and cross-hop interval coverage.",
    },
    {
        "path": "research/tsm-followup-20261101/README.md",
        "root": "source",
        "sha256": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
        "summary": "Line 31 documents the prior external experiment (MAE .741, RMSE .929, r .768, 157 ms/4 s, Apache-2.0, 37.9M/151.5MB). Context only; not reproduced here.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary mirrored by this Python model; unchanged.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary; unchanged. No analysis hook is added.",
    },
)

MISSING_EVIDENCE = (
    {
        "path": "ml-audio-research-experience.md",
        "status": "missing_in_workspace",
        "reason": "Referenced by the original task prompt but absent from the accessible workspace; no bytes pinned or reused.",
    },
    {
        "path": "research/speech_intelligence_20261028.md",
        "status": "missing_in_workspace",
        "reason": "Referenced by the original task prompt but absent from the accessible workspace; no bytes pinned or reused.",
    },
)

GATES: tuple[dict[str, str], ...] = (
    {
        "id": "model_revision_and_rights",
        "status": "blocked",
        "reason": "No exact checkpoint revision, file hashes, license confirmation or permission to redistribute/execute the named weights is established here.",
        "reopen": "Pin the exact revision and hashes, confirm Apache-2.0 terms and obtain authorized access on an approved runner.",
    },
    {
        "id": "real_frozen_extractor_and_head",
        "status": "blocked",
        "reason": "No real feature extractor was invoked. Caller vectors are deterministic synthetic stand-ins and the head is fitted to synthetic labels.",
        "reopen": "Run the caller-supplied frozen extractor and a fitted head on cleared audio; keep the classification head unused.",
    },
    {
        "id": "rights_qualified_labeled_audio",
        "status": "blocked",
        "reason": "No real speech, transcript-derived syllable labels, consent or rights-qualified corpus is used. Synthetic labels are not human syllable judgements.",
        "reopen": "Freeze a permitted, speaker-disjoint labeled rate cohort with independent scoring.",
    },
    {
        "id": "external_accuracy_generalization",
        "status": "blocked",
        "reason": "Synthetic five-fold results only. The pinned research reports one external pilot; this fixture does not reproduce or extend it.",
        "reopen": "Evaluate the exact pinned extractor/head on an independently reviewed corpus and report MAE/RMSE/r with baselines.",
    },
    {
        "id": "preferred_speed_claim",
        "status": "blocked",
        "reason": "Measured syllables/second is not a listener-preferred speed factor. No preference labels or rate-to-speed policy exist here.",
        "reopen": "Collect preference/acceptability judgments and define a separately reviewed rate-to-speed policy.",
    },
    {
        "id": "target_runtime_timing",
        "status": "blocked",
        "reason": "No paced target-device timing, CPU, memory or deadline measurement. The 157 ms/4 s figure is quoted research context, not a local measurement.",
        "reopen": "Measure the exact installed build on the target with pacing, load and deadline budgets.",
    },
    {
        "id": "rate_profile_condition_coverage",
        "status": "blocked",
        "reason": "No measured 1x/rate-change/unfamiliar-speech/music/silence/rebuffer/drift/final-partial-window coverage; synthetic 4 s windows only.",
        "reopen": "Score the exact rate policy on the full Rate-profile condition matrix with separate source-reference conditions.",
    },
    {
        "id": "source_output_mapping_and_preservation",
        "status": "blocked",
        "reason": "No pitch/transient audibility, playback buffering, speech-preservation or timestamp-tied pause/filler decision evidence; this fixture predicts a rate, it does not apply a rate change.",
        "reopen": "Measure source/output mapping, duration, quality and buffer behavior for a reviewed rate policy on permitted audio.",
    },
    {
        "id": "provider_intake",
        "status": "blocked",
        "reason": "Conceptual boundary is unregistered, OFF by default, with empty descriptor settings; no public API/ABI/default/registry/build change.",
        "reopen": "Complete opt-in provider intake with independent review after the model/data/runtime gates clear.",
    },
)

EXCLUDED_CLAIMS = (
    "adult_child_classification",
    "age_or_preferred_speed_prediction",
    "reproduction_of_pinned_research_metrics",
    "real_model_or_audio_evaluation",
    "target_device_runtime_qualification",
    "provider_registration_or_default",
)


class LCG:
    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def uniform(self) -> float:
        return 2.0 * (self.next_u32() / 4294967296.0) - 1.0

    def unit(self) -> float:
        return 0.5 * (self.uniform() + 1.0)


def require_supported_runtime() -> tuple[int, int, int]:
    """Guard canonical regeneration against runtimes older than the pinned family."""
    version = tuple(sys.version_info[:3])
    if version < MIN_CANONICAL_PYTHON:
        raise RuntimeError(f"unsupported_runtime: {version} < {MIN_CANONICAL_PYTHON}")
    return version  # type: ignore[return-value]


def canonical_value(value: Any) -> Any:
    """Quantize floats so canonical bytes do not drift between supported CPython builds."""
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite_canonical_float")
        rounded = round(value, CANONICAL_FLOAT_DIGITS)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, dict):
        return {str(key): canonical_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical_value(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(canonical_value(value), sort_keys=True, indent=2,
                       separators=(",", ": "), allow_nan=False).encode("utf-8") + b"\n")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    return hashlib.sha256(b"".join(struct.pack("<f", float(v)) for v in values)).hexdigest()


def dec(value: int) -> str:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("decimal_field_requires_int")
    return str(value)


@dataclass(frozen=True)
class Window:
    window_id: str
    fold: int
    stratum: str
    latent_rate: float
    syllable_count: int
    active_seconds: float
    label_rate: float
    features: tuple[float, ...]
    source_first: int


def stratum_for(index: int) -> str:
    if index % 11 == 0:
        return "quiet_boundary"
    if index % 7 == 0:
        return "overlap"
    if index % 5 == 0:
        return "short_active"
    return "clean"


def build_windows() -> list[Window]:
    """Matched deterministic latent, labels and caller vectors; no audio."""
    windows: list[Window] = []
    cursor = 0
    for index in range(TOTAL_WINDOWS):
        rng = LCG(SEED + index * 131)
        latent = 2.0 + 4.5 * rng.unit()
        stratum = stratum_for(index)
        active = ACTIVE_SECONDS[stratum]
        # Label follows the research convention: CMUdict-style syllable count
        # divided by annotated active speech duration, quantized to whole
        # syllables before division. Features are drawn from the same latent
        # rate with an independent deterministic noise stream.
        count = max(1, round(latent * active))
        label = count / active
        axis = (latent - 4.0) / 2.5
        mix = (1.0, 0.85, -0.7, 0.55, -0.45, 0.35, 0.25, -0.2)
        features = tuple(
            axis * mix[i % len(mix)] + 0.5 * rng.uniform()
            for i in range(EMBED_DIM)
        )
        windows.append(Window(
            window_id=f"win-{index:03d}",
            fold=index // FOLD_SIZE,
            stratum=stratum,
            latent_rate=latent,
            syllable_count=count,
            active_seconds=active,
            label_rate=label,
            features=features,
            source_first=cursor,
        ))
        cursor += WINDOW_SAMPLES
    return windows


class IdentityExtractor:
    """Caller-owned frozen extractor stand-in; returns supplied vectors as-is."""

    def __init__(self, model_id: str = MODEL_ID, revision: str = EXTRACTOR_REVISION_CLAIM) -> None:
        self.model_id = model_id
        self.revision = revision
        self.frozen = True
        # (caller vector digest, returned vector digest) for every invocation.
        self.calls: list[tuple[str, str]] = []

    def __call__(self, features: Sequence[float]) -> tuple[float, ...]:
        if not self.frozen:
            raise ValueError("extractor_not_frozen")
        supplied = validate_features(features)
        returned = tuple(float(v) for v in supplied)
        self.calls.append((tensor_digest(supplied), tensor_digest(returned)))
        return returned


class ReversedExtractor(IdentityExtractor):
    """Adverse control: same claimed identity, permuted returned vector."""

    def __call__(self, features: Sequence[float]) -> tuple[float, ...]:
        result = super().__call__(features)
        return tuple(reversed(result))


def validate_features(value: Any, expected_dim: int = EMBED_DIM) -> tuple[float, ...]:
    if value is None:
        raise ValueError("missing_features")
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError("bad_feature_type")
    if len(value) != expected_dim:
        raise ValueError("bad_feature_dimension")
    out: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError("non_numeric_feature")
        number = float(item)
        if not math.isfinite(number):
            raise ValueError("nonfinite_feature")
        out.append(number)
    return tuple(out)


def validate_label(value: Any) -> float:
    if value is None:
        raise ValueError("missing_label")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("bad_label_type")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite_label")
    if number <= 0.0:
        raise ValueError("nonpositive_label")
    return number


def extract_features(extractor: Any, features: Sequence[float],
                     expected_digest: str | None = None) -> tuple[float, ...]:
    """Accept vectors only from the claimed frozen caller with unchanged identity."""
    if extractor is None:
        raise ValueError("missing_feature_extractor")
    supplied = validate_features(features)
    if not getattr(extractor, "frozen", False):
        raise ValueError("extractor_not_frozen")
    if getattr(extractor, "model_id", None) != MODEL_ID:
        raise ValueError("extractor_identity_mismatch")
    if getattr(extractor, "revision", None) != EXTRACTOR_REVISION_CLAIM:
        raise ValueError("extractor_revision_mismatch")
    try:
        returned = validate_features(extractor(supplied))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("feature_extractor_failed") from exc
    supplied_digest, returned_digest = tensor_digest(supplied), tensor_digest(returned)
    if supplied_digest != returned_digest:
        raise ValueError("caller_vector_identity_mismatch")
    if expected_digest is not None and returned_digest != expected_digest:
        raise ValueError("caller_vector_digest_mismatch")
    return returned


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def transpose(m: Sequence[Sequence[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*m)]


def mat_mul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[float]]:
    bt = transpose(b)
    return [[dot(row, col) for col in bt] for row in a]


def mat_vec(m: Sequence[Sequence[float]], v: Sequence[float]) -> list[float]:
    return [dot(row, v) for row in m]


def solve(matrix: Sequence[Sequence[float]], rhs: Sequence[float]) -> list[float]:
    n = len(matrix)
    a = [list(row) + [float(rhs[i])] for i, row in enumerate(matrix)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[pivot][i]) < 1e-12:
            raise ValueError("singular_ridge_system")
        a[i], a[pivot] = a[pivot], a[i]
        divisor = a[i][i]
        for j in range(i, n + 1):
            a[i][j] /= divisor
        for r in range(n):
            if r == i or a[r][i] == 0.0:
                continue
            factor = a[r][i]
            for j in range(i, n + 1):
                a[r][j] -= factor * a[i][j]
    return [a[i][n] for i in range(n)]


class RidgeHead:
    """Standardized ridge regressor with an unregularized intercept."""

    def __init__(self, alpha: float = RIDGE_ALPHA) -> None:
        self.alpha = alpha
        self.mean: tuple[float, ...] = ()
        self.scale: tuple[float, ...] = ()
        self.weights: tuple[float, ...] = ()
        self.bias = 0.0

    def fit(self, features: Sequence[Sequence[float]], labels: Sequence[float]) -> "RidgeHead":
        if not features or len(features) != len(labels):
            raise ValueError("bad_training_set")
        rows = [list(row) for row in features]
        self.mean = tuple(sum(row[i] for row in rows) / len(rows) for i in range(len(rows[0])))
        self.scale = tuple(
            math.sqrt(sum((row[i] - self.mean[i]) ** 2 for row in rows) / len(rows)) or 1.0
            for i in range(len(self.mean))
        )
        z = [[(row[i] - self.mean[i]) / self.scale[i] for i in range(len(self.mean))]
             for row in rows]
        design = [row + [1.0] for row in z]
        transposed = transpose(design)
        xtx = mat_mul(transposed, design)
        for i in range(len(self.mean)):  # intercept is unregularized
            xtx[i][i] += self.alpha
        solution = solve(xtx, mat_vec(transposed, list(labels)))
        self.weights = tuple(solution[:-1])
        self.bias = solution[-1]
        return self

    def predict(self, features: Sequence[float]) -> float:
        validated = validate_features(features)
        z = [(validated[i] - self.mean[i]) / self.scale[i] for i in range(len(self.mean))]
        return dot(self.weights, z) + self.bias

    def state(self) -> dict[str, Any]:
        return {
            "type": "standardized_ridge",
            "alpha": self.alpha,
            "feature_dim": len(self.mean),
            "weights": [float(v) for v in self.weights],
            "bias": float(self.bias),
            "mean": [float(v) for v in self.mean],
            "scale": [float(v) for v in self.scale],
        }


def pearson(a: Sequence[float], b: Sequence[float]) -> float | None:
    if len(a) != len(b) or len(a) < 2:
        return None
    # Quantize first: a constant predictor must have zero variance on every
    # supported runtime, not a runtime-dependent 0 or a tiny nonzero variance.
    left = [round(float(x), CANONICAL_FLOAT_DIGITS) for x in a]
    right = [round(float(y), CANONICAL_FLOAT_DIGITS) for y in b]
    if len(set(left)) == 1 or len(set(right)) == 1:
        return None
    ma, mb = sum(left) / len(left), sum(right) / len(right)
    cov = sum((x - ma) * (y - mb) for x, y in zip(left, right))
    va = sum((x - ma) ** 2 for x in left)
    vb = sum((y - mb) ** 2 for y in right)
    if va <= 0.0 or vb <= 0.0:
        return None
    return cov / math.sqrt(va * vb)


def regression_metrics(predictions: Sequence[float], labels: Sequence[float]) -> dict[str, Any]:
    if len(predictions) != len(labels) or not predictions:
        raise ValueError("bad_metric_input")
    errors = [p - y for p, y in zip(predictions, labels)]
    mae = sum(abs(e) for e in errors) / len(errors)
    rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
    r = pearson(predictions, labels)
    return {
        "count": len(errors),
        "mae_syllables_per_second": round(mae, 6),
        "rmse_syllables_per_second": round(rmse, 6),
        "bias_syllables_per_second": round(sum(errors) / len(errors), 6),
        "pearson_r": None if r is None else round(r, 6),
        "negative_predictions": sum(p < 0.0 for p in predictions),
    }


def clipped_metrics(predictions: Sequence[float], labels: Sequence[float]) -> dict[str, Any]:
    return regression_metrics([max(0.0, p) for p in predictions], labels)


def build_event(window: Window, prediction: float, epoch: int = 1) -> dict[str, Any]:
    if not math.isfinite(prediction):
        raise ValueError("nonfinite_rate")
    # A physical rate cannot be negative. Raw head outputs are retained in the
    # metrics; only the emitted event is floored at zero.
    prediction = max(0.0, prediction)
    start = window.source_first
    end = start + WINDOW_SAMPLES
    return {
        "event_id": f"evt-{epoch}-{window.window_id}",
        "producer_id": PROVIDER_ID,
        "tap_id": "rate.measured_syllables_per_second.v0",
        "epoch": dec(epoch),
        "source_first_sample": dec(start),
        "source_last_sample_exclusive": dec(end),
        "available_ns": dec(ORIGIN_NS + end * SAMPLE_NS),
        "clock_id": CLOCK_ID,
        "validity": "known",
        "rate_syllables_per_second": float(prediction),
        "label_syllables_per_second": float(window.label_rate),
        "syllable_count": window.syllable_count,
        "active_seconds": window.active_seconds,
        "stratum": window.stratum,
        "window_id": window.window_id,
        "feature_digest": tensor_digest(window.features),
    }


def validate_event(event: dict[str, Any]) -> None:
    required = (
        "event_id", "producer_id", "tap_id", "epoch", "source_first_sample",
        "source_last_sample_exclusive", "available_ns", "clock_id", "validity",
    )
    for key in required:
        if key not in event:
            raise ValueError(f"missing_{key}")
    if event["validity"] not in {"known", "unknown", "invalid"}:
        raise ValueError("invalid_validity")
    for key in ("epoch", "source_first_sample", "source_last_sample_exclusive", "available_ns"):
        raw = event[key]
        if (not isinstance(raw, str) or not raw.isdigit()
                or (len(raw) > 1 and raw.startswith("0")) or str(int(raw)) != raw):
            raise ValueError(f"non_decimal_{key}")
    epoch = int(event["epoch"])
    first = int(event["source_first_sample"])
    last = int(event["source_last_sample_exclusive"])
    available_ns = int(event["available_ns"])
    if epoch < 1:
        raise ValueError("stale_epoch")
    if last <= first:
        raise ValueError("empty_interval")
    if first % FRAME_SAMPLES or last % FRAME_SAMPLES:
        raise ValueError("misaligned_interval")
    if last - first != WINDOW_SAMPLES:
        raise ValueError("wrong_window_samples")
    if available_ns != ORIGIN_NS + last * SAMPLE_NS:
        raise ValueError("available_ns_mismatch")
    if event["validity"] == "known":
        rate = event.get("rate_syllables_per_second")
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(float(rate)) or rate < 0.0:
            raise ValueError("bad_rate")
        label = event.get("label_syllables_per_second")
        if isinstance(label, bool) or not isinstance(label, (int, float)) or not math.isfinite(float(label)) or label <= 0.0:
            raise ValueError("bad_label_rate")


def cross_validate(windows: Sequence[Window], extractor: IdentityExtractor) -> dict[str, Any]:
    """Four blocked calibration folds; the fifth fold is reserved for evaluation."""
    folds: list[dict[str, Any]] = []
    oof: list[float] = []
    labels: list[float] = []
    per_fold = []
    for fold in CALIBRATION_FOLDS:
        test = [w for w in windows if w.fold == fold]
        train = [w for w in windows if w.fold in CALIBRATION_FOLDS and w.fold != fold]
        train_features = [
            extract_features(extractor, w.features, tensor_digest(w.features)) for w in train
        ]
        train_labels = [validate_label(w.label_rate) for w in train]
        head = RidgeHead().fit(train_features, train_labels)
        test_features = [
            extract_features(extractor, w.features, tensor_digest(w.features)) for w in test
        ]
        predictions = [head.predict(f) for f in test_features]
        truth = [validate_label(w.label_rate) for w in test]
        constant = [sum(train_labels) / len(train_labels)] * len(test)
        fold_record = {
            "fold": fold,
            "train_windows": len(train),
            "test_windows": len(test),
            "raw": regression_metrics(predictions, truth),
            "nonnegative": clipped_metrics(predictions, truth),
            "constant_train_mean": regression_metrics(constant, truth),
            "head": head.state(),
        }
        folds.append(fold_record)
        oof.extend(predictions)
        labels.extend(truth)
        per_fold.append(fold_record["nonnegative"]["mae_syllables_per_second"])
    calibration = [w for w in windows if w.fold in CALIBRATION_FOLDS]
    constant_all = [sum(validate_label(w.label_rate) for w in calibration) / len(calibration)] * len(labels)
    return {
        "protocol": "four_contiguous_chronological_calibration_folds_evaluation_fold_reserved",
        "note": ("Synthetic matched features/labels are wiring/regression evidence only; "
                 "alpha is fixed before any split and no accuracy or research reproduction is claimed."),
        "calibration_folds": list(CALIBRATION_FOLDS),
        "evaluation_fold": EVALUATION_FOLD,
        "evaluation_fold_used_for_alpha_selection": False,
        "alpha": RIDGE_ALPHA,
        "folds": folds,
        "oof_raw": regression_metrics(oof, labels),
        "oof_nonnegative": clipped_metrics(oof, labels),
        "oof_constant_train_mean": regression_metrics(constant_all, labels),
        "fold_nonnegative_mae": per_fold,
    }


def rejection_cases(windows: Sequence[Window]) -> dict[str, Any]:
    base = build_event(windows[0], 3.0)
    cases: list[dict[str, str]] = []

    def reject(name: str, thunk: Callable[[], Any], reason: str) -> None:
        try:
            thunk()
        except ValueError as exc:
            cases.append({"name": name, "status": "rejected", "reason": reason, "error": str(exc)})
        else:
            cases.append({"name": name, "status": "accepted_unexpected", "reason": reason, "error": ""})

    good = windows[0].features
    reject("missing_feature_extractor", lambda: extract_features(None, good), "caller must supply a frozen extractor")
    class Unfrozen:
        frozen = False
        model_id = MODEL_ID

        def __call__(self, value: Sequence[float]) -> Sequence[float]:
            return value

    reject("unfrozen_extractor", lambda: extract_features(Unfrozen(), good), "extractor must be frozen")
    nan_vector = [float("nan")] + list(good[1:])
    inf_vector = [float("inf")] + list(good[1:])
    reject("extractor_none", lambda: extract_features(IdentityExtractor(), None), "missing feature vector")
    reject("extractor_nan", lambda: extract_features(IdentityExtractor(), nan_vector), "nonfinite feature")
    reject("extractor_inf", lambda: extract_features(IdentityExtractor(), inf_vector), "nonfinite feature")
    reject("extractor_short_vector", lambda: extract_features(IdentityExtractor(), good[:8]), "wrong feature dimension")
    reject("extractor_non_numeric", lambda: extract_features(IdentityExtractor(), ["x"] * EMBED_DIM), "non-numeric feature")

    class WrongModel(IdentityExtractor):
        def __init__(self) -> None:
            super().__init__(model_id="other-model")

    class WrongRevision(IdentityExtractor):
        def __init__(self) -> None:
            super().__init__(revision="unpinned")

    reject("extractor_identity_mismatch", lambda: extract_features(WrongModel(), good), "claimed model id must match")
    reject("extractor_revision_mismatch", lambda: extract_features(WrongRevision(), good), "claimed revision must match")
    reject("caller_vector_identity_mismatch",
           lambda: extract_features(ReversedExtractor(), good, tensor_digest(good)),
           "returned vector must equal the caller vector bitwise")
    reject("caller_vector_digest_mismatch",
           lambda: extract_features(IdentityExtractor(), tuple(reversed(good)), tensor_digest(good)),
           "caller vector must match the pinned cohort digest")
    reject("missing_label", lambda: validate_label(None), "label required")
    reject("label_nan", lambda: validate_label(float("nan")), "nonfinite label")
    reject("label_nonpositive", lambda: validate_label(0.0), "positive label required")
    reject("label_string", lambda: validate_label("3.0"), "numeric label required")
    reject("nonfinite_rate", lambda: build_event(windows[0], float("nan")), "rate must be finite")
    bad = dict(base)
    bad["source_first_sample"] = 1.5
    reject("non_decimal_sample", lambda: validate_event(bad), "decimal-string sample field required")
    bad = dict(base, source_first_sample="+" + str(int(base["source_first_sample"])))
    reject("plus_sign_interval", lambda: validate_event(bad), "unsigned decimal-string required")
    bad = dict(base, source_first_sample=dec(160), source_last_sample_exclusive=dec(160))
    reject("empty_interval", lambda: validate_event(bad), "nonempty interval required")
    bad = dict(base, source_last_sample_exclusive=dec(int(base["source_last_sample_exclusive"]) + 1))
    reject("misaligned_interval", lambda: validate_event(bad), "frame-aligned interval required")
    bad = dict(base, source_last_sample_exclusive=dec(
        int(base["source_first_sample"]) + WINDOW_SAMPLES - FRAME_SAMPLES))
    reject("short_window", lambda: validate_event(bad), "exactly 64,000 samples required")
    bad = dict(base, available_ns=dec(int(base["available_ns"]) + 1))
    reject("available_ns_mismatch", lambda: validate_event(bad), "availability must match exclusive source end")
    bad = dict(base, epoch=dec(0))
    reject("stale_epoch", lambda: validate_event(bad), "epoch must be positive")
    bad = dict(base, validity="adult_child_label")
    reject("invalid_validity", lambda: validate_event(bad), "validity tag restricted")

    known = dict(base)
    validate_event(known)
    unknown = dict(base, validity="unknown", rate_syllables_per_second=None)
    validate_event(unknown)
    return {
        "cases": cases,
        "all_rejected": all(c["status"] == "rejected" for c in cases),
        "unknown_retained": unknown["validity"] == "unknown",
        "known_event": known,
        "unknown_event": unknown,
    }


def hop_chain(events: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Measure a chain of consecutive hops; gaps and overlaps are failures."""
    ordered = sorted(events, key=lambda e: int(e["source_first_sample"]))
    for event in ordered:
        validate_event(event)
    spans = [int(e["source_last_sample_exclusive"]) - int(e["source_first_sample"]) for e in ordered]
    transitions = [int(cur["source_first_sample"]) - int(prev["source_last_sample_exclusive"])
                   for prev, cur in zip(ordered, ordered[1:])]
    gaps = sum(delta > 0 for delta in transitions)
    overlaps = sum(delta < 0 for delta in transitions)
    exact = all(span == WINDOW_SAMPLES for span in spans)
    return {
        "windows": len(ordered),
        "frames_covered": [span // FRAME_SAMPLES for span in spans],
        "exact_window_samples": exact,
        "contiguous_transitions": sum(delta == 0 for delta in transitions),
        "gap_count": gaps,
        "overlap_count": overlaps,
        "total_source_samples": sum(spans),
        "first_sample": dec(int(ordered[0]["source_first_sample"])),
        "last_sample_exclusive": dec(int(ordered[-1]["source_last_sample_exclusive"])),
        "exact_half_open_interval": exact and gaps == 0 and overlaps == 0,
    }


def state_and_cross_hop(windows: Sequence[Window]) -> dict[str, Any]:
    a = [build_event(windows[i], 3.0) for i in range(3)]
    b = [build_event(windows[i + 3], 3.5) for i in range(3)]
    for event in a:
        event["producer_id"] = "session-A"
    for event in b:
        event["producer_id"] = "session-B"
    keys_a = {(e["producer_id"], e["tap_id"], e["epoch"], e["event_id"]) for e in a}
    keys_b = {(e["producer_id"], e["tap_id"], e["epoch"], e["event_id"]) for e in b}
    stale = dict(a[0], event_id="evt-stale", epoch=dec(0))
    stale_rejected = False
    try:
        validate_event(stale)
    except ValueError:
        stale_rejected = True
    reset = dict(a[0], event_id="evt-reset", epoch=dec(2))
    validate_event(reset)
    return {
        "session_keys_disjoint": keys_a.isdisjoint(keys_b),
        "session_a_keys": len(keys_a),
        "session_b_keys": len(keys_b),
        "cross_hop": {"session_a": hop_chain(a), "session_b": hop_chain(b)},
        "stale_epoch_rejected": stale_rejected,
        "reset_epoch_accepted": True,
    }


def build_report() -> dict[str, Any]:
    windows = build_windows()
    extractor = IdentityExtractor()
    cv = cross_validate(windows, extractor)
    held = [w for w in windows if w.fold == EVALUATION_FOLD]
    train = [w for w in windows if w.fold in CALIBRATION_FOLDS]
    train_features = [
        extract_features(extractor, w.features, tensor_digest(w.features)) for w in train
    ]
    train_labels = [validate_label(w.label_rate) for w in train]
    head = RidgeHead().fit(train_features, train_labels)
    held_features = [
        extract_features(extractor, w.features, tensor_digest(w.features)) for w in held
    ]
    predictions = [head.predict(f) for f in held_features]
    truth = [validate_label(w.label_rate) for w in held]
    events = [build_event(w, p) for w, p in zip(held, predictions)]
    for event in events:
        validate_event(event)

    # Baseline uses calibration labels only; evaluation labels never enter a fit,
    # alpha choice or control.
    train_mean = sum(train_labels) / len(train_labels)
    constant = [train_mean] * len(held)
    adverse = ReversedExtractor()
    # A strict caller pass rejects this control; unaccepted vectors are scored
    # directly only to show the expected regression failure.
    try:
        extract_features(adverse, held[0].features, tensor_digest(held[0].features))
        adverse_rejected = False
    except ValueError:
        adverse_rejected = True
    adverse_features = [validate_features(tuple(reversed(w.features))) for w in held]
    adverse_predictions = [head.predict(f) for f in adverse_features]
    by_stratum = {
        stratum: clipped_metrics(
            [p for w, p in zip(held, predictions) if w.stratum == stratum],
            [y for w, y in zip(held, truth) if w.stratum == stratum],
        )
        for stratum in STRATA
    }

    report = {
        "schema_id": SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task_id": TASK_ID,
        "title": "Distil-Wav2Vec2 frozen caller features + ridge syllable-rate head",
        "profile": "rate",
        "status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "base_commit": BASE_COMMIT,
        "task": {
            "kind": "measured_syllable_rate_regression",
            "target_unit": "syllables_per_second",
            "excluded_claims": list(EXCLUDED_CLAIMS),
            "rate_to_speed_factor_policy": None,
        },
        "model": {
            "requested_model_id": MODEL_ID,
            "role": "caller_supplied_frozen_feature_extractor",
            "classifier_head_used": False,
            "weights_downloaded": False,
            "weights_executed": False,
            "license_from_model_card": "Apache-2.0",
            "documented_context_not_reproduced": {
                "source_pin": "research/tsm-followup-20261101/README.md line 31",
                "mae_syllables_per_second": 0.741,
                "rmse_syllables_per_second": 0.929,
                "pearson_r": 0.768,
                "mean_encoder_ms_per_4s_clip": 157.0,
                "p95_encoder_ms_per_4s_clip": 222.0,
                "rtf": 0.0393,
                "parameters": 37_900_000,
                "weight_bytes_approx": 151_500_000,
                "reproduced_here": False,
                "note": "External prior result quoted as context only. No exact weights, revision, permission or local execution; these numbers are not claimed by this fixture.",
            },
            "identity_control": {
                "extractor_model_id": extractor.model_id,
                "revision": extractor.revision,
                "frozen": extractor.frozen,
                "calls": len(extractor.calls),
                "distinct_caller_vectors": len({supplied for supplied, _ in extractor.calls}),
                "identity_pairs_checked": len(extractor.calls),
                "all_caller_vectors_returned_unchanged": all(
                    supplied == returned for supplied, returned in extractor.calls
                ),
                "all_caller_vectors_match_pinned_digests": (
                    {supplied for supplied, _ in extractor.calls}
                    == {tensor_digest(w.features) for w in windows}
                ),
                "internal_model": False,
            },
        },
        "boundary": {
            "provider_id": PROVIDER_ID,
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "public_api_abi_change": False,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "window_frames": WINDOW_FRAMES,
            "window_samples": WINDOW_SAMPLES,
            "clock_id": CLOCK_ID,
            "origin_ns": dec(ORIGIN_NS),
        },
        "cohort": {
            "type": "deterministic_synthetic",
            "seed": SEED,
            "windows": len(windows),
            "folds": FOLDS,
            "windows_per_fold": FOLD_SIZE,
            "strata": list(STRATA),
            "active_seconds_by_stratum": ACTIVE_SECONDS,
            "label_definition": "round(latent_rate * active_seconds) / active_seconds",
            "labels_matched_to_caller_features_by_latent": True,
            "real_audio": False,
            "human_syllable_labels": False,
            "label_digest": object_digest([w.label_rate for w in windows]),
            "feature_digest": object_digest([w.features for w in windows]),
            "examples": [
                {
                    "window_id": w.window_id,
                    "stratum": w.stratum,
                    "syllable_count": w.syllable_count,
                    "active_seconds": w.active_seconds,
                    "label_syllables_per_second": w.label_rate,
                    "feature_digest": tensor_digest(w.features),
                }
                for w in windows[:5]
            ],
        },
        "training": cv,
        "held_out": {
            "fold": EVALUATION_FOLD,
            "windows": len(held),
            "calibration_folds": list(CALIBRATION_FOLDS),
            "calibration_windows": len(train),
            "evaluation_labels_used_in_fit": False,
            "evaluation_labels_used_for_alpha_selection": False,
            "train_mean_label_syllables_per_second": train_mean,
            "raw": regression_metrics(predictions, truth),
            "nonnegative": clipped_metrics(predictions, truth),
            "constant_train_mean": regression_metrics(constant, truth),
            "by_stratum_nonnegative": by_stratum,
            "events_digest": object_digest(events),
            "events": events[:3],
            "head": head.state(),
        },
        "controls": {
            "identity_caller_features": {
                "status": "pass",
                "note": "Caller vectors returned bitwise unchanged; only the ridge head is fitted locally.",
                "embedding_digest": object_digest([w.features for w in held]),
            },
            "permutation_adverse": {
                "status": "expected_failure",
                "description": "Same claimed model identity, deterministically reversed caller vectors.",
                "strict_gate_rejected": adverse_rejected,
                "metrics_are_unaccepted": True,
                "raw": regression_metrics(adverse_predictions, truth),
                "nonnegative": clipped_metrics(adverse_predictions, truth),
                "worse_than_identity": (
                    clipped_metrics(adverse_predictions, truth)["mae_syllables_per_second"]
                    > clipped_metrics(predictions, truth)["mae_syllables_per_second"]
                ),
            },
            "constant_train_mean": {
                "status": "reference_failure",
                "metrics": regression_metrics(constant, truth),
            },
            "nonnegative_clipping": {
                "raw_negative_count": sum(p < 0.0 for p in predictions),
                "clipped_mae": clipped_metrics(predictions, truth)["mae_syllables_per_second"],
                "raw_mae": regression_metrics(predictions, truth)["mae_syllables_per_second"],
            },
        },
        "validation": rejection_cases(windows),
        "state_and_cross_hop": state_and_cross_hop(windows),
        "missing_evidence": list(MISSING_EVIDENCE),
        "source_pins": list(SOURCE_PINS),
        "gates": list(GATES),
        "evidence_classes": {
            "synthetic_deterministic": "used",
            "synthetic_wiring_mae_rmse_r": "wiring_only_not_accuracy",
            "real_audio": "none",
            "real_model_weights": "none",
            "caller_supplied_real_features": "none",
            "human_rate_labels": "none",
            "target_runtime_timing": "none",
            "rate_policy_conditions": "none",
            "speech_preservation": "none",
        },
    }
    return report


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return canonical_bytes(report)
