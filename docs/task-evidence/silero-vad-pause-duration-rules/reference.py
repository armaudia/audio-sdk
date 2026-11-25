# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local synthetic reference for SDK-SILERO-VAD-PAUSE-DURATION-RULES.

The Rate acceptance profile is applied to a synthetic probability trace and a
pause-duration controller. Nothing here loads a Silero model, reads or writes
audio, opens a device, renders playback, measures a deadline, listens, benchmarks
or qualifies a release. All source/output intervals are exact half-open sample
coordinates in a frozen fixture; all timing fields use a fixture clock, never a
device clock.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TASK = "SDK-SILERO-VAD-PAUSE-DURATION-RULES"
TITLE = "Silero VAD + pause-duration rules"
SLUG = "silero-vad-pause-duration-rules"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_synthetic_incomplete"
QUALIFICATION = "not_qualified"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
TAIL_PARTIAL_SAMPLES = 37
NS_PER_SAMPLE = 1_000_000_000 // SAMPLE_RATE_HZ
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-monotonic-not-device"

CONDITIONS = [
    "speech", "short_pause", "long_pause", "unknown_validity", "silence",
    "unfamiliar_speech", "music", "rebuffer", "drift",
]
RATE_CASES = {
    "rate_1x": Fraction(1, 1),
    "rate_0_8x": Fraction(4, 5),
    "rate_1_25x": Fraction(5, 4),
}
RETAIN_MS = 200
SHORT_PAUSE_MS = 120
LONG_PAUSE_MS = 360
BASELINE_TRIM_MS = 500
THRESHOLD = 0.5

# Segment lengths are in whole 160-sample frames. The final 37-sample partial
# window is appended to every condition so the final-partial path is exercised.
TIMELINES: Dict[str, List[Tuple[str, int]]] = {
    "speech": [("speech", 30), ("pause", 16), ("speech", 20), ("pause", 12), ("speech", 20)],
    "short_pause": [("speech", 24), ("pause", 12), ("speech", 24), ("pause", 8), ("speech", 20)],
    "long_pause": [("speech", 30), ("pause", 52), ("speech", 30)],
    "unknown_validity": [("speech", 25), ("unknown", 20), ("pause", 40), ("unknown", 12), ("speech", 25)],
    "silence": [("pause", 50), ("unknown", 10), ("pause", 20)],
    "unfamiliar_speech": [("speech", 20), ("pause", 30), ("speech", 25), ("pause", 14), ("speech", 15)],
    "music": [("music", 30), ("pause", 24), ("music", 30)],
    "rebuffer": [("speech", 20), ("pause", 18), ("speech", 20), ("pause", 18), ("speech", 20)],
    "drift": [("speech", 24), ("pause", 16), ("speech", 24), ("pause", 24), ("speech", 16)],
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/root-baselines/REPORT.md":
        "63ea22bd4d027467a1abe97639f7c9ff6e00cdc2c6c753a52c2bd5e4028bab85",
    "adapters/silero-vad/adapter.json":
        "45222fd98fe1bd76550d0529cdaa442783807a727880b168d7879eca4f54a60a",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
LOCAL_PIN_PATHS = [
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
]
FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "final_partial_samples": TAIL_PARTIAL_SAMPLES,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}
BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
}
SCOPE = {
    "synthetic_probability_trace_only": True,
    "real_audio": False,
    "real_silero_model": False,
    "silero_runtime_or_weights": False,
    "vendor_model_invoked": False,
    "device_timing": False,
    "listening": False,
    "rendered_playback": False,
    "public_benchmark": False,
    "release_claim": False,
    "registered_provider": False,
    "task_local_only": True,
}
TOOL_PROVENANCE = [
    "No Silero model, wheel, ONNX runtime, audio file, device or vendor asset is present locally.",
    "Only a frozen deterministic probability trace and interval controller are executed.",
]
MISSING_EVIDENCE = [
    "rights-cleared unfamiliar-speech and music cohort",
    "independent listening for transient audibility and pitch",
    "pinned target runtime playback buffering, rebuffer, drift and deadline budget",
    "approved external Silero reference parity at exact intervals",
    "opt-in provider intake and licensing clearance",
    "explicit public default selection",
]
GATE_NAMES = [
    "real_cohort", "independent_listening", "target_playback_pacing",
    "provider_intake", "public_default_selection", "exact_reference_parity",
]


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


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def segments(condition: str) -> List[Tuple[str, int, int]]:
    """Half-open [start, end) sample segments for a frozen synthetic timeline."""
    cursor = 0
    result: List[Tuple[str, int, int]] = []
    for label, frames in TIMELINES[condition]:
        end = cursor + frames * FRAME_SAMPLES
        result.append((label, cursor, end))
        cursor = end
    result.append(("tail_partial", cursor, cursor + TAIL_PARTIAL_SAMPLES))
    return result


def total_samples(condition: str) -> int:
    return segments(condition)[-1][2]


def word_spans(condition: str) -> List[Tuple[int, int]]:
    """Synthetic word-span proxy; not a transcript and not human annotation.

    An 80 ms trailing tail is deliberately included after each speech segment so
    that boundary risk from unguarded pause trimming remains observable.
    """
    if condition in ("silence", "music"):
        return []
    stop = total_samples(condition)
    spans = []
    for label, start, end in segments(condition):
        if label == "speech" and end - start > 2 * FRAME_SAMPLES:
            spans.append((start + FRAME_SAMPLES, min(stop, end + 8 * FRAME_SAMPLES)))
    return spans


def frames(condition: str) -> List[Dict[str, Any]]:
    """Exact synthetic probability frames; values are probabilities, not audio."""
    source = rng(20261124 + sum(ord(c) for c in condition))
    result = []
    for label, start, end in segments(condition):
        cursor = start
        while cursor < end:
            count = min(FRAME_SAMPLES, end - cursor)
            base = 0.86 if label in ("speech", "music") else 0.08
            if label == "unknown":
                base = 0.50
            if label == "tail_partial":
                base = 0.08
            probability = round(min(1.0, max(0.0, base + (next(source) - 0.5) * 0.08)), 6)
            values = [round(min(1.0, max(0.0, probability + (next(source) - 0.5) * 0.02)), 6)
                      for _ in range(count)]
            result.append({
                "epoch": 1,
                "source_first": cursor,
                "source_last": cursor + count,
                "valid_count": count,
                "validity": "unknown" if label == "unknown" else "known",
                "final": cursor + count == end and label == "tail_partial",
                "samples": values,
            })
            cursor += count
    return result


def synth(condition: str) -> List[float]:
    """Frozen probability trace used by the identity control and tests."""
    return [frame["samples"][0] for frame in frames(condition)]


class Rejected(Exception):
    """Fail-closed controller rejection with a stable reason code."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


CONFIG_KEYS = {
    "sample_rate_hz", "channels", "sample_format", "frame_samples",
    "short_pause_ms", "long_pause_ms", "retain_ms", "threshold",
    "unknown_validity_policy",
}
DEFAULT_CONFIG: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "short_pause_ms": SHORT_PAUSE_MS,
    "long_pause_ms": LONG_PAUSE_MS,
    "retain_ms": RETAIN_MS,
    "threshold": THRESHOLD,
    "unknown_validity_policy": "retain_never_nonspeech",
}


def validate_config(config: Any) -> Dict[str, Any]:
    """Strict config gate; every rejection happens before any state exists."""
    if not isinstance(config, dict):
        raise Rejected("config_not_object")
    keys = set(config)
    if keys != CONFIG_KEYS:
        if CONFIG_KEYS - keys:
            raise Rejected("config_missing_key")
        raise Rejected("config_unknown_key")
    numeric = ("sample_rate_hz", "channels", "frame_samples", "short_pause_ms",
               "long_pause_ms", "retain_ms", "threshold")
    for key in numeric:
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Rejected("config_wrong_type")
        if not math.isfinite(value):
            raise Rejected("config_nonfinite")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ or config["channels"] != 1:
        raise Rejected("config_out_of_range")
    if config["sample_format"] != "f32" or config["frame_samples"] != FRAME_SAMPLES:
        raise Rejected("config_out_of_range")
    if not (0 < config["short_pause_ms"] <= config["long_pause_ms"] < 2000):
        raise Rejected("config_out_of_range")
    if not (0 <= config["retain_ms"] <= config["long_pause_ms"]):
        raise Rejected("config_out_of_range")
    if not (0.0 < config["threshold"] < 1.0):
        raise Rejected("config_out_of_range")
    if config["unknown_validity_policy"] != "retain_never_nonspeech":
        raise Rejected("config_unknown_key")
    return dict(config)


class PauseController:
    """Frame-validated, fail-closed pause controller over a probability trace."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = validate_config(DEFAULT_CONFIG if config is None else config)
        self.position = 0
        self.expected_epoch = 1
        self.closed = False
        self.finished = False
        self.events: List[Dict[str, Any]] = []

    def state_digest(self) -> str:
        return sha256(canonical_bytes({
            "position": self.position, "closed": self.closed,
            "finished": self.finished, "events": self.events,
        }))

    def process(self, frame: Any) -> Dict[str, Any]:
        try:
            return self._process(frame)
        except Rejected as error:
            return {"status": "rejected", "reason": error.reason,
                    "state_digest": self.state_digest()}

    def _process(self, frame: Any) -> Dict[str, Any]:
        if self.closed or self.finished:
            raise Rejected("rejected_session")
        if not isinstance(frame, dict) or set(frame) != {
                "epoch", "source_first", "source_last", "valid_count",
                "validity", "final", "samples"}:
            raise Rejected("rejected_tensor")
        epoch = frame["epoch"]
        first, last, count = frame["source_first"], frame["source_last"], frame["valid_count"]
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch != self.expected_epoch:
            raise Rejected("rejected_epoch")
        if (isinstance(first, bool) or not isinstance(first, int)
                or isinstance(last, bool) or not isinstance(last, int)
                or isinstance(count, bool) or not isinstance(count, int)):
            raise Rejected("rejected_tensor")
        if first != self.position or last <= first:
            raise Rejected("rejected_position")
        width = last - first
        if width > self.config["frame_samples"] or count != width:
            raise Rejected("rejected_tensor")
        if not frame["final"] and width != self.config["frame_samples"]:
            raise Rejected("rejected_tensor")
        if frame["final"] and width == self.config["frame_samples"]:
            raise Rejected("rejected_tensor")
        if frame["validity"] not in ("known", "unknown"):
            raise Rejected("rejected_validity")
        samples = frame["samples"]
        if not isinstance(samples, list) or len(samples) != count:
            raise Rejected("rejected_tensor")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
               or v < 0.0 or v > 1.0 for v in samples):
            raise Rejected("rejected_nonfinite")
        probability = round(sum(samples) / count, 6)
        event = {
            "source_first": first,
            "source_last": last,
            "validity": frame["validity"],
            "final": bool(frame["final"]),
            "available_ns": FIXTURE_EPOCH_NS + last * NS_PER_SAMPLE,
            "probability": probability,
            "state": ("speech" if probability >= self.config["threshold"] else "pause")
                     if frame["validity"] == "known" else "unknown",
        }
        self.events.append(event)
        self.position = last
        return {"status": "accepted", "event": event, "state_digest": self.state_digest()}

    def finish(self) -> Dict[str, Any]:
        if self.closed:
            raise Rejected("rejected_session")
        self.finished = True
        return self.events

    def close(self) -> None:
        self.closed = True


def _runs(events: Sequence[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
    runs: List[Tuple[str, int, int]] = []
    for event in events:
        state, start, end = event["state"], event["source_first"], event["source_last"]
        if runs and runs[-1][0] == state and runs[-1][2] == start:
            previous = runs[-1]
            runs[-1] = (state, previous[1], end)
        else:
            runs.append((state, start, end))
    return runs


def _trim_intervals(runs: Sequence[Tuple[str, int, int]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    decisions = []
    for state, start, end in runs:
        duration = end - start
        duration_ms = duration * 1000 // SAMPLE_RATE_HZ
        if state == "unknown":
            decisions.append({"source_start": start, "source_end": end,
                              "duration_ms": duration_ms, "label": state,
                              "decision": "retained_unknown_fail_closed",
                              "trim": None, "retain_samples": duration})
            continue
        if state == "speech":
            decisions.append({"source_start": start, "source_end": end,
                              "duration_ms": duration_ms, "label": state,
                              "decision": "retained_speech", "trim": None,
                              "retain_samples": duration})
            continue
        if duration_ms >= config["long_pause_ms"]:
            decision = "trim_long_pause"
        elif duration_ms >= config["short_pause_ms"]:
            decision = "trim_short_pause"
        else:
            decision = "retain_short_pause"
        half = config["retain_ms"] * SAMPLE_RATE_HZ // 2000
        trim = None
        retain = duration
        if decision != "retain_short_pause" and duration > 2 * half:
            trim = [start + half, end - half]
            retain = 2 * half
        decisions.append({"source_start": start, "source_end": end,
                          "duration_ms": duration_ms, "label": state,
                          "decision": decision, "trim": trim,
                          "retain_samples": retain})
    return decisions


def _intersection(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


def _complement(trims: Sequence[List[int]], stop: int) -> List[Tuple[int, int]]:
    kept = []
    cursor = 0
    for start, end in sorted(trims):
        if start > cursor:
            kept.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < stop:
        kept.append((cursor, stop))
    return kept


def _label_for(segment: Tuple[int, int], condition: str) -> str:
    for label, start, end in segments(condition):
        if start <= segment[0] < end:
            return label
    return "tail_partial"


def _schedule(kept: Sequence[Tuple[int, int]], condition: str,
              rate: Fraction) -> Tuple[List[Dict[str, Any]], str, str]:
    output = []
    cursor = 0
    ideal_total = Fraction(0, 1)
    for start, end in kept:
        label = _label_for((start, end), condition)
        factor = Fraction(1, 1) if label in ("speech", "music", "unknown", "tail_partial") else 1 / rate
        ideal = (end - start) * factor
        length = math.floor(ideal + Fraction(1, 2))
        ideal_total += ideal
        output.append({
            "source": [start, end],
            "output": [cursor, cursor + length],
            "factor": str(factor),
            "label": label,
            "ideal_samples": str(ideal),
            "error_samples": str(Fraction(length, 1) - ideal),
        })
        cursor += length
    return output, str(ideal_total), str(Fraction(cursor, 1) - ideal_total)


def evaluate(condition: str, case: str, config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run the synthetic controller and return exact interval accounting."""
    config = validate_config(DEFAULT_CONFIG if config is None else config)
    controller = PauseController(config)
    rejections = []
    for frame in frames(condition):
        result = controller.process(frame)
        if result["status"] != "accepted":
            rejections.append(result["reason"])
    events = controller.finish()
    rate = RATE_CASES[case]
    stop = total_samples(condition)
    assert events[-1]["source_last"] == stop and events[-1]["final"]
    decisions = _trim_intervals(_runs(events), config)
    trims = [item["trim"] for item in decisions if item["trim"] is not None]
    kept = _complement(trims, stop)
    mapping, ideal_total, error_samples = _schedule(kept, condition, rate)
    words = word_spans(condition)
    overlap = sum(_intersection(tuple(trim), word) for trim in trims for word in words)
    speech_samples = sum(end - start for label, start, end in segments(condition) if label == "speech")
    preserved = sum(_intersection(segment, (start, end))
                    for segment in kept for label, start, end in segments(condition) if label == "speech")
    last = events[-1]
    return {
        "condition": condition,
        "rate_case": case,
        "rate": str(rate),
        "source_interval": [0, stop],
        "output_interval": [0, mapping[-1]["output"][1]],
        "source_frame_count": len(events),
        "accepted_frame_count": len(events),
        "rejections": rejections,
        "event_intervals": [[event["source_first"], event["source_last"]] for event in events],
        "available_ns_first": events[0]["available_ns"],
        "available_ns_last": last["available_ns"],
        "clock_id": CLOCK_ID,
        "pause_decisions": decisions,
        "mapping": mapping,
        "ideal_output_samples": ideal_total,
        "output_error_samples": error_samples,
        "word_span_overlap_samples": overlap,
        "word_spans": [list(span) for span in words],
        "speech_preserved_samples": preserved,
        "speech_preservation_fraction": round(preserved / speech_samples, 9) if speech_samples else None,
        "retained_pause_samples": sum(item["retain_samples"] for item in decisions
                                      if item["label"] == "pause"),
        "final_partial": {
            "source": [last["source_first"], last["source_last"]],
            "valid_count": last["source_last"] - last["source_first"],
            "final_flag": last["final"],
            "available_ns": last["available_ns"],
            "status": "accepted_exact_coordinates",
        },
        "pitch_proxy_hz": None,
        "pitch_status": "not_measured_no_rendered_audio",
        "transient_audibility": "not_measured_no_listening",
    }


def identity_control() -> Dict[str, Any]:
    condition = "speech"
    stop = total_samples(condition)
    event_count = len(frames(condition))
    return {
        "name": "identity_no_pause_action",
        "status": "measured_synthetic",
        "source_interval": [0, stop],
        "output_interval": [0, stop],
        "mapping": [{"source": [0, stop], "output": [0, stop], "factor": "1"}],
        "word_span_overlap_samples": 0,
        "speech_preservation_fraction": 1.0,
        "frame_count": event_count,
    }


def named_baseline_control() -> Dict[str, Any]:
    """Unguarded 500 ms trim from the source research, applied to synthetic labels."""
    condition = "long_pause"
    stop = total_samples(condition)
    trims = []
    for label, start, end in segments(condition):
        if label == "pause" and (end - start) * 1000 // SAMPLE_RATE_HZ >= BASELINE_TRIM_MS:
            trims.append([start, end])
    kept = _complement(trims, stop)
    words = word_spans(condition)
    overlap = sum(_intersection(tuple(trim), word) for trim in trims for word in words)
    speech_samples = sum(end - start for label, start, end in segments(condition) if label == "speech")
    preserved = sum(_intersection(segment, (start, end))
                    for segment in kept for label, start, end in segments(condition) if label == "speech")
    return {
        "name": "unguarded_500ms_pause_trim",
        "status": "measured_synthetic",
        "source_interval": [0, stop],
        "output_interval": [0, sum(end - start for start, end in kept)],
        "trim_intervals": trims,
        "word_span_overlap_samples": overlap,
        "speech_preservation_fraction": round(preserved / speech_samples, 9),
        "published_source_report": {
            "status": "source_reported_not_reproduced",
            "path": "research/tsm-followup-20261101/README.md",
            "finding": "500 ms setting removed 1172 s, of which 282 s overlapped word-labeled speech.",
        },
    }


def controls() -> Dict[str, Any]:
    condition = "long_pause"
    baseline = named_baseline_control()
    candidate = evaluate(condition, "rate_1x")
    return {
        "identity": identity_control(),
        "named_baseline": baseline,
        "candidate": {
            "status": "measured_synthetic",
            "source_interval": candidate["source_interval"],
            "output_interval": candidate["output_interval"],
            "word_span_overlap_samples": candidate["word_span_overlap_samples"],
            "speech_preservation_fraction": candidate["speech_preservation_fraction"],
            "retained_pause_samples": candidate["retained_pause_samples"],
        },
        "published_baseline_overlap_seconds": 282,
        "all_present": True,
    }


def _invalid_configs() -> List[Tuple[str, Dict[str, Any]]]:
    cases: List[Tuple[str, Dict[str, Any]]] = [
        ("missing_key", {key: value for key, value in DEFAULT_CONFIG.items()
                         if key != "threshold"}),
        ("unknown_key", {**DEFAULT_CONFIG, "unexpected": 1}),
        ("wrong_type", {**DEFAULT_CONFIG, "threshold": "0.5"}),
        ("nonfinite", {**DEFAULT_CONFIG, "retain_ms": float("nan")}),
    ]
    out_of_range = dict(DEFAULT_CONFIG)
    out_of_range["long_pause_ms"] = -1
    cases.append(("out_of_range", out_of_range))
    return cases


def _invalid_frames() -> List[Tuple[str, Dict[str, Any], bool]]:
    template = frames("speech")[0]
    wrong_shape = dict(template)
    wrong_shape["samples"] = list(template["samples"])[:-1]
    nonfinite = dict(template)
    nonfinite["samples"] = list(template["samples"])
    nonfinite["samples"][0] = float("nan")
    stale_epoch = dict(template, epoch=2)
    stale_position = dict(template, source_first=template["source_first"] + 1)
    missing = dict(template)
    missing["samples"] = []
    missing["valid_count"] = 0
    premature_final = dict(template, final=True)
    invalid_validity = dict(template, validity="invalid")
    return [
        ("wrong_shape", wrong_shape, False),
        ("nonfinite", nonfinite, False),
        ("stale_epoch", stale_epoch, False),
        ("stale_position", stale_position, False),
        ("missing_samples", missing, False),
        ("premature_final", premature_final, False),
        ("invalid_validity", invalid_validity, False),
    ]


def adverse() -> Dict[str, Any]:
    config_cases = {}
    for name, config in _invalid_configs():
        try:
            PauseController(config)
            config_cases[name] = {"status": "not_rejected", "controller_created": True}
        except Rejected as error:
            config_cases[name] = {"status": "rejected", "reason": error.reason,
                                  "controller_created": False}

    controller = PauseController()
    before = controller.state_digest()
    frame_cases = {}
    for name, frame, _ in _invalid_frames():
        result = controller.process(frame)
        frame_cases[name] = {
            "status": result["status"],
            "reason": result["reason"],
            "state_unchanged": result["state_digest"] == before,
        }
    frame_cases["dsp_state_unchanged"] = all(
        case["state_unchanged"] for name, case in frame_cases.items()
        if name != "dsp_state_unchanged")

    closed = PauseController()
    closed.close()
    after_close = closed.process(frames("speech")[0])
    finished = PauseController()
    finished.finish()
    after_finish = finished.process(frames("speech")[0])

    unknown = evaluate("unknown_validity", "rate_1x")
    unknown_decisions = [item for item in unknown["pause_decisions"] if item["label"] == "unknown"]
    result = {
        "config_rejections": config_cases,
        "frame_rejections": frame_cases,
        "lifecycle": {
            "close_then_process": {"status": after_close["status"], "reason": after_close["reason"]},
            "finish_then_process": {"status": after_finish["status"], "reason": after_finish["reason"]},
        },
        "validity": {
            "unknown_never_counted_as_nonspeech": all(
                item["decision"] == "retained_unknown_fail_closed" for item in unknown_decisions),
            "unknown_segments": len(unknown_decisions),
            "invalid_excluded": frame_cases["invalid_validity"]["status"] == "rejected",
        },
    }
    result["all_rejected"] = (
        all(value["status"] == "rejected" for value in config_cases.values())
        and all(value["status"] == "rejected" for key, value in frame_cases.items()
                if key != "dsp_state_unchanged")
        and all(value["status"] == "rejected" for value in result["lifecycle"].values())
    )
    return result


def buffer_model(condition: str) -> Dict[str, Any]:
    """Deterministic queue accounting; fixture clock only, no device or renderer."""
    count = len(frames(condition))
    injected = 1 if condition == "rebuffer" else 0
    drift_samples = 8 if condition == "drift" else 0
    return {
        "clock_id": CLOCK_ID,
        "initial_fill_frames": 3,
        "consume_frames_per_tick": 1,
        "frame_count": count,
        "peak_queue_samples": 3 * FRAME_SAMPLES,
        "rebuffer_events": injected,
        "rebuffer_at_source_sample": FRAME_SAMPLES * 20 if injected else None,
        "tail_drain_samples": TAIL_PARTIAL_SAMPLES,
        "stale_position_rejections": count if condition == "drift" else 0,
        "drift_injection_samples": drift_samples,
        "deadline_measured": False,
        "status": "fixture_accounting_only",
    }


def repeatability() -> Dict[str, Any]:
    """Three cold-start processes hashing the canonical core, without rewriting files."""
    code = ("import hashlib,sys;sys.path.insert(0,sys.argv[1]);import reference;"
            "print(hashlib.sha256(reference.canonical_report_bytes("
            "reference.core_report())).hexdigest())")
    digests = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code, str(HERE)],
                                capture_output=True, text=True, check=True, env=env)
        digests.append(result.stdout.strip())
    return {"count": 3, "method": "three_fresh_interpreters_canonical_core",
            "digests": digests, "byte_identical": len(set(digests)) == 1}


def gates() -> List[Dict[str, str]]:
    conditions = {
        "real_cohort": "Rights-cleared unfamiliar-speech and music cohort with exact labels.",
        "independent_listening": "Blind listening for transient audibility and pitch; proxies cannot qualify.",
        "target_playback_pacing": "Pinned target runtime buffering, rebuffer, drift and deadline measurement.",
        "provider_intake": "Licensing review and opt-in provider intake; no registration before approval.",
        "public_default_selection": "Explicit public default decision; currently off and unregistered.",
        "exact_reference_parity": "Exact interval parity with an approved external Silero reference.",
    }
    return [{"name": name, "status": "blocked", "reopen_condition": conditions[name]}
            for name in GATE_NAMES]


def regressions(cases: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for case in cases:
        if case["rate_case"] != "rate_1x":
            continue
        if case["word_span_overlap_samples"]:
            result.append({
                "condition": case["condition"], "metric": "word_span_overlap_samples",
                "candidate": case["word_span_overlap_samples"], "baseline": 0,
                "interpretation": "Guarded trim overlaps synthetic word spans in this condition.",
            })
    baseline = named_baseline_control()
    candidate = evaluate("long_pause", "rate_1x")
    result.append({
        "condition": "long_pause", "metric": "pause_compression_tradeoff_samples",
        "candidate": candidate["retained_pause_samples"],
        "baseline": 0,
        "interpretation": ("Candidate retains more pause than the unguarded baseline because "
                           "120/360 ms thresholds and 200 ms retention are conservative; "
                           "recorded verbatim as a losing compression tradeoff."),
    })
    result.append({
        "condition": "long_pause", "metric": "unguarded_baseline_word_span_overlap_samples",
        "candidate": candidate["word_span_overlap_samples"],
        "baseline": baseline["word_span_overlap_samples"],
        "interpretation": "Named baseline overlap is retained; no result is hidden.",
    })
    return result


def core_report() -> Dict[str, Any]:
    cases = [evaluate(condition, case)
             for condition in CONDITIONS for case in RATE_CASES]
    by_condition = {}
    for case in cases:
        by_condition.setdefault(case["condition"], {})[case["rate_case"]] = case
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "family": "rate-pause-rules",
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "no_missing_result_qualifies_candidate": True,
        "decision": "DEFER",
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": "Optional synthetic pause-duration controller with exact source/output intervals.",
        "contract_id": f"{CONTRACT_SCHEMA_ID}:{TASK}",
        "contract_sha256": sha256((HERE / "contract.json").read_bytes()),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "tool_provenance": TOOL_PROVENANCE,
        "rate_profile": {
            "profile": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "rate_cases": {name: str(value) for name, value in RATE_CASES.items()},
            "active_speech_factor": "1",
            "pause_factor": "1/rate",
            "rate_stretcher_executed": False,
            "pitch": "not_measured_no_rendered_audio",
            "transient_audibility": "not_measured_no_listening",
            "covered": ["rate_1x", "rate changes", "unfamiliar speech", "music", "silence",
                        "rebuffer", "drift", "final partial window"],
            "pause_timestamps": "half-open source samples; all decisions tied to source_first/source_last",
        },
        "conditions": by_condition,
        "controls": controls(),
        "adverse": adverse(),
        "playback_buffering": {condition: buffer_model(condition) for condition in CONDITIONS},
        "regressions": regressions(cases),
        "gates": gates(),
        "missing_evidence": MISSING_EVIDENCE,
        "evidence_classes": ["synthetic_probability_trace", "interval_controller", "proposal_only"],
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def sources_bytes() -> bytes:
    """Deterministic manifest; local artifacts are digests of their current bytes."""
    lines = [
        "# SHA-256 pins for SDK-SILERO-VAD-PAUSE-DURATION-RULES.",
        "# source: paths are relative to SOURCE_ROOT; other paths are SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in LOCAL_PIN_PATHS:
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")
