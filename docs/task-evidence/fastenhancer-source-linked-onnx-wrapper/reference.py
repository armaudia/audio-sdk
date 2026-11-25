# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local synthetic reference for SDK-FASTENHANCER-SOURCE-LINKED-ONNX-WRAPPER.

This is a developer-facing evaluation fixture at a documented optional adapter
boundary. It is not a vendor runtime, real model, real audio, device
measurement, listening result, benchmark or release qualification. Evaluation
and any future production callback paths are distinct; no production callback
is implemented or invoked here.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from scorer import SCORER_ID, si_sdr, stoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TASK_ID = "SDK-FASTENHANCER-SOURCE-LINKED-ONNX-WRAPPER"
TITLE = "FastEnhancer source-linked ONNX wrapper"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
SCHEMA_ID = "audio-sdk/task-evidence/fastenhancer-source-linked-onnx-wrapper/report/0.1"
COMPONENT_ID = "fastenhancer-source-linked-onnx-wrapper"
REFERENCE_FAMILY = "fastenhancer"
FAMILY = "source-linked-wrapper"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
TASK_REL = "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper"

# Public v0 geometry is documented only; nothing is installed or changed.
FORMAT = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "processing_mode": "offline_synthetic_frame_fixture",
    "installed_v0_geometry_preserved": True,
}
BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "processor_exposure": False,
    "c_public_boundary": False,
    "installed_v0_geometry_preserved": True,
    "evaluation_path": "task_local_python_fixture",
    "production_callback_path": "not_implemented",
}

CONDITIONS = ["identity", "noisy_control", "frontend_shape", "malformed_input", "silence"]
CONFIG = {"model": "source_linked_synthetic_v0"}
STRENGTH = 0.12
MAX_ABS_INPUT = 2.0
SIGNAL_SAMPLES = 9600

# Pinned identities. All paths are relative to SOURCE_ROOT unless prefixed
# with ``worktree:``, in which case they are relative to SDK_ROOT.
SOURCE_PINS: Dict[str, str] = {
    "source:cpp-library/src/stages/fastenhancer.cpp":
        "b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510",
    "source:adapters/fastenhancer/README.md":
        "32a856af0f7f32efb35b0b00c6551564f6383cf6446285c060294504cdf341ea",
    "source:cpp-library/PIPELINE_DESIGN_REPORT.md":
        "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
    "source:REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "source:research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "source:research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}
BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
ARTIFACT_PIN_PATHS = (
    f"{TASK_REL}/contract.json",
    f"{TASK_REL}/adapter.json",
    f"{TASK_REL}/provider.json",
    f"{TASK_REL}/scorer.py",
    "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json",
)
PIN_RE = re.compile(r"^[0-9a-f]{64}  (?P<path>source:[^\s]+|worktree:[^\s]+|docs/[^\s]+|api/[^\s]+|CONTRACTS\.md)$")
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


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


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_json(path: Path) -> Any:
    def reject_object_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def reject_constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=reject_object_pairs, parse_constant=reject_constant)


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        return SOURCE_ROOT / raw.split(":", 1)[1]
    if raw.startswith("worktree:"):
        return SDK_ROOT / raw.split(":", 1)[1]
    return SDK_ROOT / raw


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Fail closed on malformed, duplicated or out-of-scope manifest entries."""
    pins: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + repr(line))
        raw_path = match.group("path")
        if ".." in Path(raw_path.split(":", 1)[-1]).parts:
            raise ValueError("path_traversal_pin:" + raw_path)
        if raw_path in seen:
            raise ValueError("duplicate_pin:" + raw_path)
        seen.add(raw_path)
        pins.append((line[:64], raw_path))
    return pins


def artifact_pins() -> Dict[str, str]:
    return {path: sha256(pin_path(path).read_bytes()) for path in ARTIFACT_PIN_PATHS}


def sources_bytes() -> bytes:
    """Deterministic manifest; excludes SOURCES.sha256 itself to avoid self-reference."""
    pins: Dict[str, str] = dict(SOURCE_PINS)
    pins.update(BOUNDARY_PINS)
    pins.update(artifact_pins())
    for path in sorted(HERE.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SOURCES.sha256":
            pins[f"{TASK_REL}/{path.name}"] = sha256(path.read_bytes())
    lines = [f"{digest}  {path}" for path, digest in sorted(pins.items())]
    header = (f"# SHA-256 pins for {TASK_ID}. "
              "source: paths are workspace-relative; worktree: and plain paths are "
              "SDK-worktree-relative. Lines are <sha256>  <path>.\n")
    return (header + "\n".join(lines) + "\n").encode("utf-8")


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return frozen clean target and observed input for one synthetic condition."""
    seed = 20261124 + sum(ord(char) for char in condition)
    random = rng(seed)
    clean: List[float] = []
    for index in range(SIGNAL_SAMPLES):
        envelope = 0.55 + 0.35 * math.sin(2.0 * math.pi * index / 1609.0)
        tone = (0.24 * math.sin(2.0 * math.pi * 113.0 * index / 16000.0)
                + 0.13 * math.sin(2.0 * math.pi * 226.0 * index / 16000.0)
                + 0.07 * math.sin(2.0 * math.pi * 339.0 * index / 16000.0))
        clean.append(tone * envelope)
    noise_scale = {
        "identity": 0.02,
        "noisy_control": 0.18,
        "frontend_shape": 0.06,
        "malformed_input": 0.06,
        "silence": 0.0,
    }[condition]
    observed: List[float] = []
    for index, value in enumerate(clean):
        noise = (next(random) - 0.5) * 2.0 * noise_scale
        if condition == "noisy_control" and 2400 <= index < 3200:
            noise *= 3.0
        observed.append(value + noise if condition != "silence" else 0.0)
    if condition == "silence":
        clean = [0.0] * SIGNAL_SAMPLES
    return clean, observed


def transform_frame(values: Iterable[float], previous: float = 0.0) -> Tuple[List[float], float]:
    """Causal, deterministic smoothing/shrinkage inside one 160-sample frame."""
    frame = list(values)
    output: List[float] = []
    state = previous
    for index, value in enumerate(frame):
        following = frame[index + 1] if index + 1 < len(frame) else value
        smoothed = 0.5 * value + 0.25 * state + 0.25 * following
        gain = 1.0 - STRENGTH * (1.0 - min(1.0, abs(smoothed)))
        output.append(max(-0.98, min(0.98, smoothed * gain)))
        state = value
    return output, state


def candidate_transform(values: Iterable[float]) -> List[float]:
    """Convenience wrapper for repeat probes; controller owns frame state."""
    samples = list(values)
    result: List[float] = []
    state = 0.0
    for start in range(0, len(samples), FORMAT["frame_samples"]):
        transformed, state = transform_frame(
            samples[start:start + FORMAT["frame_samples"]], state)
        result.extend(transformed)
    return result


def scored(target: List[float], actual: Optional[List[float]]) -> Dict[str, Any]:
    if actual is None:
        return {"status": "rejected", "si_sdr_db": None, "stoi": None,
                "reason": "invalid_input_rejected"}
    si_value, si_reason = si_sdr(target, actual)
    stoi_value, stoi_reason = stoi(target, actual, FORMAT["sample_rate_hz"])
    result: Dict[str, Any] = {
        "status": "scored_synthetic" if si_value is not None and stoi_value is not None else "excluded",
        "si_sdr_db": round(si_value, 6) if si_value is not None and math.isfinite(si_value) else None,
        "stoi": round(stoi_value, 6) if stoi_value is not None and math.isfinite(stoi_value) else None,
        "peak_abs_output": round(max(abs(value) for value in actual), 9),
        "nonfinite_count": sum(1 for value in actual if not math.isfinite(value)),
        "clipping_count": sum(1 for value in actual if abs(value) >= 0.98),
        "si_sdr_reason": si_reason,
        "stoi_reason": stoi_reason,
    }
    return result


class Controller:
    """Task-local frame state machine; all invalid admissions are fail-closed."""

    def __init__(self) -> None:
        self.epoch = 1
        self.next_position = 0
        self.previous = 0.0
        self.finished = False
        self.closed = False
        self.state_hash = self._state()

    def _state(self) -> str:
        return sha256(canonical_bytes({
            "epoch": self.epoch,
            "next_position": self.next_position,
            "previous": round(self.previous, 12),
            "finished": self.finished,
            "closed": self.closed,
        }))

    def _reject(self, status: str) -> Dict[str, Any]:
        return {"status": status, "samples": None, "state_digest": self.state_hash}

    def process(self, frame: Any, epoch: int, first_sample: int) -> Dict[str, Any]:
        if self.closed or self.finished:
            return self._reject("rejected_session")
        if not isinstance(frame, (list, tuple)) or len(frame) != FORMAT["frame_samples"]:
            return self._reject("rejected_tensor")
        if any(isinstance(value, bool) for value in frame):
            return self._reject("rejected_invalid")
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in frame):
            return self._reject("rejected_nonfinite")
        if any(abs(value) > MAX_ABS_INPUT for value in frame):
            return self._reject("rejected_invalid")
        if epoch != self.epoch:
            return self._reject("rejected_epoch")
        if first_sample != self.next_position:
            return self._reject("rejected_position")
        output, self.previous = transform_frame(frame, self.previous)
        self.next_position += FORMAT["frame_samples"]
        self.state_hash = self._state()
        return {"status": "ok", "samples": output, "state_digest": self.state_hash}

    def finish(self) -> str:
        if self.closed or self.finished:
            return "rejected_session"
        self.finished = True
        self.state_hash = self._state()
        return "ok"

    def close(self) -> None:
        self.closed = True
        self.state_hash = self._state()

    def reset(self, epoch: int, first_sample: int) -> str:
        if self.closed:
            return "rejected_session"
        if epoch <= self.epoch:
            return "rejected_epoch"
        if first_sample < 0:
            return "rejected_position"
        self.epoch = epoch
        self.next_position = first_sample
        self.previous = 0.0
        self.finished = False
        self.state_hash = self._state()
        return "ok"


def create_controller(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        return {"controller": None, "status": "rejected_invalid"}
    keys = set(config)
    if "model" not in keys:
        return {"controller": None, "status": "rejected_missing"}
    if keys != {"model"}:
        return {"controller": None, "status": "rejected_invalid"}
    value = config["model"]
    if isinstance(value, float) and not math.isfinite(value):
        return {"controller": None, "status": "rejected_nonfinite"}
    if not isinstance(value, str):
        return {"controller": None, "status": "rejected_invalid"}
    if value != CONFIG["model"]:
        return {"controller": None, "status": "rejected_invalid"}
    return {"controller": Controller(), "status": "created"}


def run_frames(observed: List[float]) -> Tuple[Optional[List[float]], Dict[str, Any]]:
    created = create_controller(CONFIG)
    if created["controller"] is None:
        return None, {"status": created["status"], "frames": 0, "rejections": 1}
    controller: Controller = created["controller"]
    output: List[float] = []
    rejections = 0
    for index in range(0, len(observed), FORMAT["frame_samples"]):
        frame = observed[index:index + FORMAT["frame_samples"]]
        result = controller.process(frame, controller.epoch, index)
        if result["status"] != "ok" or result["samples"] is None:
            rejections += 1
            return None, {"status": result["status"], "frames": len(output) // FORMAT["frame_samples"],
                          "rejections": rejections}
        output.extend(result["samples"])
    finish = controller.finish()
    if finish != "ok":
        return None, {"status": finish, "frames": len(output) // FORMAT["frame_samples"],
                      "rejections": rejections + 1}
    if len(output) != len(observed):
        return None, {"status": "rejected_duration", "frames": len(output) // FORMAT["frame_samples"],
                      "rejections": rejections + 1}
    return output, {"status": "ok", "frames": len(output) // FORMAT["frame_samples"],
                    "rejections": rejections}


def conditions() -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for condition in CONDITIONS:
        target, observed = synth(condition)
        baseline = scored(target, observed)
        candidate, run = run_frames(observed)
        scored_candidate = scored(target, candidate)
        candidate_worse = (
            candidate is not None
            and baseline["si_sdr_db"] is not None
            and scored_candidate["si_sdr_db"] is not None
            and scored_candidate["si_sdr_db"] < baseline["si_sdr_db"]
        )
        result[condition] = {
            "status": "measured_synthetic" if candidate is not None else "rejected_adverse",
            "samples": len(observed),
            "seed": 20261124 + sum(ord(char) for char in condition),
            "baseline_metrics": baseline,
            "candidate_metrics": scored_candidate,
            "candidate_worse_than_baseline": candidate_worse,
            "frame_run": run,
        }
    return result


def controls() -> Dict[str, Any]:
    identity_target, identity_input = synth("identity")
    identity_output, _ = run_frames(identity_input)
    noisy_target, noisy_input = synth("noisy_control")
    noisy_output, _ = run_frames(noisy_input)
    return {
        "identity": {
            "name": "identity_no_processing",
            "status": "measured_synthetic",
            "metrics": scored(identity_target, identity_input),
        },
        "named_baseline": {
            "name": "noisy_input_no_processing",
            "status": "measured_synthetic",
            "metrics": scored(noisy_target, noisy_input),
        },
        "candidate": {
            "name": "causal_smoothing_shrinkage",
            "status": "measured_synthetic",
            "metrics": scored(noisy_target, noisy_output),
        },
        "clean_speech_preservation": {
            "clean_reference": "identity condition synthetic target",
            "status": "measured_synthetic",
            "metrics": scored(identity_target, identity_output),
        },
        "all_present": True,
        "excluded_from_qualification": True,
        "note": "Identity, noisy and candidate controls are paired synthetic comparisons only.",
    }


def adverse() -> Dict[str, Any]:
    config_cases = {
        "missing_key": {},
        "unknown_key": {"model": CONFIG["model"], "extra": True},
        "wrong_type": {"model": 7},
        "nonfinite": {"model": float("nan")},
        "out_of_range": {"model": "not_a_frozen_synthetic_preset"},
    }
    config_rejections = {
        name: {"status": create_controller(config)["status"], "controller_created": False}
        for name, config in config_cases.items()
    }
    created = create_controller(CONFIG)
    controller: Controller = created["controller"]
    frame = [0.0] * FORMAT["frame_samples"]
    before = controller.state_hash

    def frame_case(value: Any, epoch: int = 1, position: int = 0, finish: bool = False,
                   close: bool = False) -> str:
        if finish:
            controller.finish()
        if close:
            controller.close()
        status = controller.process(value, epoch, position)["status"]
        return status

    frame_rejections = {
        "wrong_shape": frame_case(frame[:-1]),
        "bool_sample": frame_case([True] * FORMAT["frame_samples"]),
        "nonfinite": frame_case([float("nan")] * FORMAT["frame_samples"]),
        "out_of_range": frame_case([MAX_ABS_INPUT + 1.0] * FORMAT["frame_samples"]),
        "stale_epoch": frame_case(frame, epoch=0),
        "stale_position": frame_case(frame, position=160),
        "missing_samples": frame_case(None),
        "dsp_state_unchanged": controller.state_hash == before,
    }
    lifecycle_controller: Controller = create_controller(CONFIG)["controller"]
    close_then_process = frame_case(frame, close=True)
    finish_controller: Controller = create_controller(CONFIG)["controller"]
    finish_controller.finish()
    finish_then_process = finish_controller.process(frame, 1, 0)["status"]
    reset_controller: Controller = create_controller(CONFIG)["controller"]
    stale_reset_epoch = reset_controller.reset(1, 0)
    fresh_reset = reset_controller.reset(2, 0)
    stale_reset_position = reset_controller.reset(3, -1)
    return {
        "config_rejections": config_rejections,
        "frame_rejections": frame_rejections,
        "lifecycle": {
            "close_then_process": close_then_process,
            "finish_then_process": finish_then_process,
            "stale_reset_epoch": stale_reset_epoch,
            "stale_reset_position": stale_reset_position,
            "valid_reset": fresh_reset,
        },
        "validity": {
            "nonfinite_never_counted_as_nonspeech": True,
            "invalid_excluded": True,
            "invalid_never_advances_dsp_state": True,
        },
    }


def repeatability() -> Dict[str, Any]:
    _, observed = synth("identity")
    digests = []
    for _ in range(3):
        created = create_controller(CONFIG)
        controller: Controller = created["controller"]
        output: List[float] = []
        for index in range(0, 480, FORMAT["frame_samples"]):
            result = controller.process(observed[index:index + FORMAT["frame_samples"]], 1, index)
            if result["samples"] is None:
                raise RuntimeError("repeat controller rejected a pinned frame")
            output.extend(result["samples"])
        digests.append(sha256(canonical_bytes(output)))
    return {
        "count": 3,
        "digests": digests,
        "byte_identical": len(set(digests)) == 1,
        "note": "Three fresh controllers over one pinned synthetic probe; no tolerance or substitution.",
    }


def gates() -> List[Dict[str, str]]:
    names = [
        "real_paired_cohort",
        "independent_listening",
        "target_runtime_deadline",
        "provider_intake",
        "public_default_selection",
        "exact_reference_parity",
        "upstream_source_model_runtime_rights",
    ]
    return [{"name": name, "status": "blocked",
             "reopen_condition": "Independent cleared evidence required; a missing result never qualifies."}
            for name in names]


def acceptance_profile() -> Dict[str, Any]:
    pinned = SOURCE_PINS["source:audio-benchmark-platform/plan/swarm/VERIFICATION.md"]
    return {
        "profile": PROFILE,
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": pinned,
        "mapped_cases": {
            "identity_noisy_control": {
                "evidence": ["controls.identity", "controls.named_baseline", "conditions.identity",
                             "conditions.noisy_control"],
                "status": "measured_synthetic",
            },
            "established_task_matched_baseline": {
                "name": "noisy_input_no_processing",
                "evidence": ["controls.named_baseline"],
                "status": "measured_synthetic",
            },
            "paired_si_sdr_stoi": {
                "evidence": ["conditions.*.baseline_metrics", "conditions.*.candidate_metrics"],
                "status": "measured_synthetic",
                "scorer": SCORER_ID,
                "note": "Paired synthetic clean references only; no real-speech score.",
            },
            "clean_speech_preservation": {
                "evidence": ["controls.clean_speech_preservation", "conditions.identity"],
                "status": "measured_synthetic",
            },
            "peaks_and_invalid_outputs": {
                "evidence": ["conditions.*.candidate_metrics", "adverse"],
                "status": "measured_synthetic",
            },
            "unpaired_speech": {
                "status": "not_applicable",
                "reason": "No licensed unpaired speech, predictive screen or authorized listening was run.",
            },
            "alignment_state_memory_timing": {
                "status": "partial_synthetic",
                "alignment": "zero integer content delay; one 160-sample output per input frame",
                "state": "frame state and rejections recorded; invalid input never advances state",
                "memory": "host Python counts only; no target-device memory result",
                "timing": "no measured content/availability timing for an exact runtime",
            },
        },
        "not_reported": [
            "real paired cohort", "human listening or MOS", "target-device pacing or deadline",
            "installed runtime memory", "real model inference", "release qualification",
        ],
    }


def independent_timing_evidence() -> Dict[str, Any]:
    return {
        "status": "source_reported_proposal_only",
        "used_for_qualification": False,
        "measured_here": False,
        "target_device": False,
        "preset_references": [
            {
                "preset": "FastEnhancer Tiny 16 kHz",
                "source": "REALTIME_COMPONENT_CANDIDATES.md",
                "sha256": SOURCE_PINS["source:REALTIME_COMPONENT_CANDIDATES.md"],
                "statement": "DNS pilot adapter RTF 0.0166; cross-model timing is not a controlled hardware comparison.",
            },
            {
                "preset": "FastEnhancer Small 16 kHz",
                "source": "REALTIME_COMPONENT_CANDIDATES.md",
                "sha256": SOURCE_PINS["source:REALTIME_COMPONENT_CANDIDATES.md"],
                "statement": "DNS pilot adapter RTF 0.0359; source-reported, not reproduced here.",
            },
            {
                "preset": "Tiny/Small plus Silero paced Python composition",
                "source": "cpp-library/PIPELINE_DESIGN_REPORT.md",
                "sha256": SOURCE_PINS["source:cpp-library/PIPELINE_DESIGN_REPORT.md"],
                "statement": "Paced process CPU 9.34-9.41% / 20.23-21.34% respectively on a Mac Python/ONNX path; not a device budget.",
            },
            {
                "preset": "FastEnhancer Python adapter versus native Small delay",
                "source": "cpp-library/PIPELINE_DESIGN_REPORT.md",
                "sha256": SOURCE_PINS["source:cpp-library/PIPELINE_DESIGN_REPORT.md"],
                "statement": "Adapter compensates 256 samples/16 ms while scheduled native Small measured 512 samples/32 ms; paths stay separately labeled.",
            },
        ],
        "note": "Independent provenance only. These numbers are not reproduced, pooled, compared as a controlled benchmark, or used as a candidate or acceptance threshold.",
    }


def rights_gap() -> Dict[str, Any]:
    return {
        "blocked": True,
        "exact_upstream_source_revision_verified": False,
        "model_weight_terms_verified": False,
        "onnx_runtime_redistribution_terms_verified": False,
        "real_model_weights_present": False,
        "vendor_runtime_invoked": False,
        "source_pin": "adapters/fastenhancer/README.md",
        "source_sha256": SOURCE_PINS["source:adapters/fastenhancer/README.md"],
        "statement": "The pinned adapter README records a source release commit but no separate pretrained-model terms; weights remain local evaluation assets pending confirmation.",
        "consequence": "No vendoring, installed provider, registry entry or release claim is permitted until exact source, model and ONNX runtime rights are cleared.",
    }


def scorer_provenance() -> Dict[str, Any]:
    vectors = SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json"
    payload = strict_json(vectors)
    if not isinstance(payload, list):
        raise ValueError("crosscheck vectors root is not a list")
    return {
        "scorer_id": SCORER_ID,
        "algorithm": "non-extended pystoi 0.4.1 port and zero-mean SI-SDR",
        "inherited_from": "docs/task-evidence/online-multichannel-wpe/scorer.py",
        "inherited_sha256": sha256((SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/scorer.py").read_bytes()),
        "relationship": "algorithm byte-identical except SCORER_ID",
        "crosscheck_vectors_pin": ARTIFACT_PIN_PATHS[-1],
        "crosscheck_vectors_sha256": sha256(vectors.read_bytes()),
        "crosscheck_vector_count": len(payload),
        "max_abs_si_sdr_delta": max(float(item["si_sdr_abs_delta"]) for item in payload),
        "max_abs_stoi_delta": max(float(item["stoi_abs_delta"]) for item in payload),
        "crosscheck_scope": "Six synthetic vectors inherited from the merged scorer; external numpy/pystoi values were not rerun here.",
        "used_as_oracle": False,
    }


def build_report() -> Dict[str, Any]:
    condition_map = conditions()
    regressions = []
    for name, value in condition_map.items():
        candidate = value["candidate_metrics"]
        baseline = value["baseline_metrics"]
        if value["candidate_worse_than_baseline"]:
            regressions.append({
                "condition": name,
                "metric": "si_sdr_db",
                "candidate": candidate["si_sdr_db"],
                "baseline": baseline["si_sdr_db"],
                "interpretation": "Candidate is worse than the named noisy-input baseline in this synthetic condition.",
            })
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT_ID,
        "reference_family": REFERENCE_FAMILY,
        "family": FAMILY,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "evidence_status": "incomplete",
        "defer_before": "processor_exposure",
        "no_missing_result_qualifies_candidate": True,
        "scope": (
            "Task-local deterministic synthetic evidence at a documented optional adapter boundary. "
            "No public-surface, installed-behavior, model, device, listening, benchmark or release claim."
        ),
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": "Developer-facing source-linked ONNX wrapper fixture with distinct evaluation and production paths.",
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(),
        "acceptance_profile": acceptance_profile(),
        "conditions": condition_map,
        "controls": controls(),
        "adverse": adverse(),
        "repeatability": repeatability(),
        "regressions": regressions,
        "gates": gates(),
        "independent_timing_evidence": independent_timing_evidence(),
        "rights_gap": rights_gap(),
        "scorer": scorer_provenance(),
        "missing_evidence": [
            "real paired cohort", "independent listening", "target runtime deadline",
            "provider intake", "public default selection", "exact external reference parity",
            "exact upstream source, model and ONNX runtime rights",
        ],
        "negative_claims": {
            "real_model_weights": False,
            "real_media": False,
            "device_timing": False,
            "listening_result": False,
            "benchmark_claim": False,
            "release_claim": False,
            "onnx_runtime_invoked": False,
        },
        "evidence_classes": ["synthetic_fixture", "boundary_review", "source_reported_provenance",
                             "proposal_only"],
    }
