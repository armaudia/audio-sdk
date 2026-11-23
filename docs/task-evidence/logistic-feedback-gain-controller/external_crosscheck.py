# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""External-only source cross-check for the dependency-free reference.

Run with an interpreter that has the pinned numpy/scipy stack and access to the
SHA-256-pinned working sources under /Users/htsakanyan/workspace/audio/audioml.
This script is NOT imported by run.py, report.json or the unit tests.  It writes
crosscheck_vectors.json, which the report embeds as provenance only.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as local  # noqa: E402

SOURCE_EXPECTED = {
    "scripts/evaluate_feedback_control_ml.py":
        "e6cd1903cce7724a15c6ef162b59b8fc27dbf1a80ba5e47ebaa66a3845276d04",
    "src/audioml_eval/feedback_control.py":
        "a708b085320bc493fe975616bb2f9bb13d78745ec4df6c313c705f45f67e5cb3",
    "scripts/evaluate_feedback_control.py":
        "cde956dd584fc560063ac91e2725f36869cb3508c0a1e4fac00aa9fa3fd99e0c",
    "scripts/evaluate_feedback_control_smard.py":
        "c570ce9f33f0631864e10acc4d11ce02f1b4a7d6bc7c5fda167e3ae6fadcd28c",
}


def find_source_root() -> Path:
    for parent in HERE.parents:
        if (parent / "scripts/evaluate_feedback_control_ml.py").is_file():
            return parent
    raise RuntimeError("pinned source root not found")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_source_functions(path: Path, names: set[str], namespace: dict):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    selected = [node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in selected} != names:
        raise RuntimeError(f"missing source functions in {path}")
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(path), "exec"), namespace)  # noqa: S102 - pinned local source
    return namespace


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maximum_absolute_delta(left, right) -> float:
    return max(abs(float(a) - float(b)) for a, b in zip(left, right))


def round_vector(values, digits: int = 12) -> list[float]:
    return [round(float(value), digits) for value in values]


def main() -> None:
    root = find_source_root()
    pins = {}
    for relative, expected in SOURCE_EXPECTED.items():
        actual = sha256(root / relative)
        if actual != expected:
            raise RuntimeError(f"source pin mismatch: {relative}: {actual}")
        pins[relative] = actual

    feedback = load_module(
        root / "src/audioml_eval/feedback_control.py", "pinned_feedback_control")
    namespace = {"np": np}
    load_source_functions(
        root / "scripts/evaluate_feedback_control_ml.py",
        {"fit_logistic", "model_probability", "summarize_detection"}, namespace)
    source_frame_features = feedback.feedback_frame_features
    source_fit = namespace["fit_logistic"]
    source_probability = namespace["model_probability"]
    source_summary = namespace["summarize_detection"]

    fixture = local.build_fixture()
    clip = fixture["clips"][0]
    train_path = fixture["train_paths"][0]
    heldout_path = fixture["heldout_paths"][0]
    target = local.make_target(clip)

    def feature_rows(path):
        simulation = local.simulate_closed_loop(
            target, local.IdentityController(), path["impulse"], 1.05)
        local_features, labels = local.frame_dataset(
            target, simulation["output"], simulation["feedback"])
        source_features = []
        source_states = []
        previous_peak = previous_rms = None
        for frame_start in range(0, len(target) - local.FRAME + 1, local.FRAME):
            microphone = simulation["output"][frame_start:frame_start + local.FRAME]
            values, previous_peak, previous_rms = source_frame_features(
                np.asarray(microphone, dtype=np.float64), local.RATE,
                previous_peak, previous_rms)
            source_features.append([float(value) for value in values])
            source_states.append((int(previous_peak), float(previous_rms)))
        return local_features, source_features, labels, source_states, simulation

    train_local, train_source, train_labels, train_states, _ = feature_rows(train_path)
    held_local, held_source, held_labels, held_states, _ = feature_rows(heldout_path)

    local_states = []
    previous_peak = previous_rms = None
    for microphone in [
        local.simulate_closed_loop(target, local.IdentityController(),
                                   train_path["impulse"], 1.05)["output"][
                                       start:start + local.FRAME]
        for start in range(0, len(target) - local.FRAME + 1, local.FRAME)
    ]:
        _, previous_peak, previous_rms = local.feedback_frame_features(
            microphone, local.RATE, previous_peak, previous_rms)
        local_states.append((previous_peak, previous_rms))

    feature_delta = maximum_absolute_delta(
        [value for row in train_local for value in row],
        [value for row in train_source for value in row])
    state_delta = maximum_absolute_delta(
        [value for state in local_states for value in state],
        [value for state in train_states for value in state])

    source_fit = source_fit(np.asarray(train_source, dtype=np.float64),
                           np.asarray(train_labels, dtype=np.float64))
    local_fit = local.fit_logistic(train_local, train_labels)
    weight_delta = maximum_absolute_delta(local_fit["weights"], source_fit[0])
    mean_delta = maximum_absolute_delta(local_fit["mean"], source_fit[2])
    scale_delta = maximum_absolute_delta(local_fit["scale"], source_fit[3])
    threshold_delta = abs(local_fit["threshold"] - float(source_fit[4]))
    intercept_delta = abs(local_fit["intercept"] - float(source_fit[1]))

    source_probabilities = source_probability(
        np.asarray(held_source, dtype=np.float64), source_fit[0], source_fit[1],
        source_fit[2], source_fit[3])
    local_probabilities = [local.model_probability(row, local_fit)
                           for row in held_local]
    probability_delta = maximum_absolute_delta(local_probabilities,
                                               source_probabilities)
    source_detection = source_summary(np.asarray(held_labels, dtype=np.float64),
                                      source_probabilities, float(source_fit[4]))
    local_detection = local.summarize_detection(held_labels, local_probabilities,
                                                local_fit["threshold"])
    detection_equal = all(
        int(local_detection[key]) == int(source_detection[key])
        for key in ("frames", "positive_frames", "true_positive", "false_positive",
                    "false_negative", "true_negative"))

    vector = {
        "purpose": ("External-only formula cross-check; report path uses no numpy, "
                    "scipy or pinned source imports"),
        "source_pins": pins,
        "environment": {"numpy_version": np.__version__,
                        "python_version": sys.version.split()[0],
                        "scipy_version": scipy.__version__},
        "fixture_digest": fixture["digest"],
        "frames_compared": len(train_source),
        "heldout_frames_compared": len(held_source),
        "feature_names": local.FEATURE_NAMES,
        "feature_sample_source": round_vector(train_source[0]),
        "feature_sample_local": round_vector(train_local[0]),
        "source_training": {
            "weights": round_vector(source_fit[0]),
            "intercept": float(source_fit[1]),
            "mean": round_vector(source_fit[2]),
            "scale": round_vector(source_fit[3]),
            "threshold": float(source_fit[4]),
            "precision": float(source_fit[5]["precision_at_selected_threshold_training"]),
            "recall": float(source_fit[5]["recall_at_selected_threshold_training"]),
            "f1": float(source_fit[5]["f1_at_selected_threshold_training"]),
        },
        "local_training": {
            "weights": round_vector(local_fit["weights"]),
            "intercept": local_fit["intercept"],
            "mean": round_vector(local_fit["mean"]),
            "scale": round_vector(local_fit["scale"]),
            "threshold": local_fit["threshold"],
            "precision": local_fit["training_precision"],
            "recall": local_fit["training_recall"],
            "f1": local_fit["training_f1"],
        },
        "source_detection": source_detection,
        "local_detection": local_detection,
        "max_absolute_deltas": {
            "features": feature_delta,
            "peak_bin_and_rms_states": state_delta,
            "weights": weight_delta,
            "intercept": intercept_delta,
            "mean": mean_delta,
            "scale": scale_delta,
            "selected_threshold": threshold_delta,
            "model_probabilities": probability_delta,
        },
        "detection_counts_equal": detection_equal,
    }
    tolerances = {
        "features": 1e-8, "peak_bin_and_rms_states": 1e-8, "weights": 1e-7,
        "intercept": 1e-7, "mean": 1e-9, "scale": 1e-9,
        "selected_threshold": 1e-12, "model_probabilities": 1e-7,
    }
    for key, tolerance in tolerances.items():
        if vector["max_absolute_deltas"][key] > tolerance:
            raise RuntimeError(f"cross-check delta too large for {key}: "
                               f"{vector['max_absolute_deltas'][key]}")
    if not detection_equal:
        raise RuntimeError("heldout detection counts differ from pinned source")
    if not all(math.isfinite(value) for value in vector["max_absolute_deltas"].values()):
        raise RuntimeError("nonfinite cross-check delta")
    out = HERE / "crosscheck_vectors.json"
    out.write_text(json.dumps(vector, indent=2, sort_keys=True, allow_nan=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"crosscheck": str(out),
                      "max_absolute_deltas": vector["max_absolute_deltas"],
                      "detection_counts_equal": detection_equal}, indent=2))


if __name__ == "__main__":
    main()
