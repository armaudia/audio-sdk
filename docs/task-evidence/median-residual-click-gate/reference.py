"""Deterministic opt-in model of the fixed median-residual click gate.

Developer-only reference for SDK-MEDIAN-RESIDUAL-CLICK-GATE. This module is not
an SDK provider, does not alter the installed v0 ABI and does not assert any
quality or release result. It reproduces the detector/repair documented in
research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md:

    baseline = median_filter(x, size=7, mode="reflect")
    detected = abs(x - baseline) >= threshold  (threshold 0.35)
    detected interior samples -> 0.5 * (x[i-1] + x[i+1]) simultaneously

The adapter exposes a 160-sample frame boundary with an explicit 3-sample
lookahead (buffering_delay_samples=3), source-coordinate mapping and strict
rejection of invalid epoch/session/frame/config inputs. All arithmetic is
stdlib double precision with float32 quantization of sample payloads.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Any, Iterable

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
NS_PER_SAMPLE = 62500
DEFAULT_THRESHOLD = 0.35
DEFAULT_MEDIAN_WIDTH = 7
CONTROL = "median_residual_click_gate_reference"
IDENTITY = "median-residual-click-gate-reference"
ADAPTER_IDENTITY = "median-residual-click-gate-protocol-v1-local"

FLAG_STARTUP_PADDING = 1
FLAG_FINAL_PADDING = 2
FLAG_FINAL_INPUT = 1

_F32 = struct.Struct("<f")


class ControlError(ValueError):
    """Raised for a rejected reference control or frame."""


def f32(value: float) -> float:
    """Round a Python double to IEEE-754 binary32."""
    return _F32.unpack(_F32.pack(float(value)))[0]


def f32_bytes(samples: Iterable[float]) -> bytes:
    return b"".join(_F32.pack(f32(value)) for value in samples)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_samples(samples: Iterable[float]) -> str:
    return sha256_bytes(f32_bytes(samples))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def validate_config(config: Any) -> dict[str, Any]:
    """Fail-closed validation; absent controls never silently select defaults."""
    if not isinstance(config, dict):
        raise ControlError("config_not_object")
    required = {
        "control", "sample_rate_hz", "channels", "sample_format",
        "sdk_frame_samples", "median_width_samples", "threshold",
    }
    if set(config) != required:
        missing = sorted(required - set(config))
        unknown = sorted(set(config) - required)
        if missing:
            raise ControlError("missing_control:" + ",".join(missing))
        raise ControlError("unknown_control:" + ",".join(unknown))
    if config["control"] != CONTROL:
        raise ControlError("unsupported_control")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ControlError("invalid_sample_rate")
    if config["channels"] != CHANNELS:
        raise ControlError("invalid_channels")
    if config["sample_format"] != SAMPLE_FORMAT:
        raise ControlError("invalid_sample_format")
    if config["sdk_frame_samples"] != SDK_FRAME_SAMPLES:
        raise ControlError("invalid_frame_samples")
    width = config["median_width_samples"]
    if isinstance(width, bool) or not isinstance(width, int) or width % 2 == 0 or not 3 <= width <= 15:
        raise ControlError("invalid_median_width")
    threshold = config["threshold"]
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ControlError("nonnumeric_threshold")
    if not math.isfinite(float(threshold)):
        raise ControlError("nonfinite_threshold")
    if not 0.0 < float(threshold) <= 1.0:
        raise ControlError("threshold_out_of_range")
    return {
        "control": CONTROL,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "sdk_frame_samples": SDK_FRAME_SAMPLES,
        "median_width_samples": width,
        "threshold": float(threshold),
    }


def reflect_index(index: int, length: int) -> int:
    """scipy.ndimage 'reflect' index: edge value is not duplicated."""
    if length <= 1:
        return 0
    period = 2 * (length - 1)
    if index < 0:
        index = -index
        if index >= length:
            index = period - index
        return index
    if index >= length:
        index = period - index
        if index < 0:
            index = -index
        return index
    return index


def median_residual(x: list[float], index: int, width: int, threshold: float) -> dict[str, Any]:
    """One source-sample decision; no mutation of the caller's samples."""
    radius = width // 2
    length = len(x)
    window = [x[reflect_index(index + delta, length)]
              for delta in range(-radius, radius + 1)]
    baseline = sorted(window)[radius]
    value = x[index]
    residual = value - baseline
    detected = abs(residual) >= threshold
    repaired = False
    output = value
    if detected and 0 < index < length - 1:
        output = 0.5 * (x[index - 1] + x[index + 1])
        repaired = True
    reason = "threshold_exceeded" if repaired else (
        "threshold_exceeded_endpoint_not_repaired" if detected else "below_threshold")
    return {
        "source_index": index,
        "source_start_ns": index * NS_PER_SAMPLE,
        "source_end_ns": (index + 1) * NS_PER_SAMPLE,
        "input_f32": f32(value),
        "baseline_f32": f32(baseline),
        "residual_abs": round(abs(residual), 12),
        "detected": detected,
        "repaired": repaired,
        "output_f32": f32(output),
        "reason": reason,
    }


class Session:
    """Source-coordinate frame session with explicit 3-sample buffering delay."""

    def __init__(self, config: dict[str, Any], *, session_id: str, epoch: int,
                 first_input_sample: int = 0) -> None:
        self.config = validate_config(config)
        self.config_digest = canonical_digest(self.config)
        if not isinstance(session_id, str) or not session_id:
            raise ControlError("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ControlError("invalid_epoch")
        if first_input_sample != 0:
            raise ControlError("unsupported_start_position")
        self.session_id = session_id
        self.epoch = epoch
        self.first_input_sample = first_input_sample
        self.samples: list[float] = []
        self.next_input_sample = first_input_sample
        self.output_cursor = first_input_sample - self.config["median_width_samples"] // 2
        self.frames: list[dict[str, Any]] = []
        self.decisions: dict[int, dict[str, Any]] = {}
        self.rejections: list[dict[str, Any]] = []
        self.closed = False
        self.drained = False
        self.reset_count = 0

    def summary(self) -> dict[str, Any]:
        valid_count = sum(frame["valid_count"] for frame in self.frames)
        produced = len(self.frames) * SDK_FRAME_SAMPLES
        return {
            "epoch": self.epoch,
            "session_id": self.session_id,
            "state": "drained" if self.drained else ("closed" if self.closed else "processing"),
            "accepted_samples": len(self.samples),
            "next_input_sample": self.next_input_sample,
            "output_frames": len(self.frames),
            "produced_samples": produced,
            "valid_samples": valid_count,
            "startup_padding_samples": sum(f["valid_offset"] for f in self.frames),
            "final_padding_samples": produced - valid_count - sum(f["valid_offset"] for f in self.frames),
            "decision_count": len(self.decisions),
            "rejection_count": len(self.rejections),
            "reset_count": self.reset_count,
            "input_sha256": digest_samples(self.samples),
            "output_sha256": digest_samples(self.output_payload()),
            "frame_map_sha256": canonical_digest(
                [{key: value for key, value in frame.items() if key != "samples"}
                 for frame in self.frames]),
            "decisions_sha256": canonical_digest(
                [self.decisions[key] for key in sorted(self.decisions)]),
        }

    def output_payload(self) -> list[float]:
        result: list[float] = []
        for frame in self.frames:
            begin = frame["valid_offset"]
            result.extend(frame["samples"][begin:begin + frame["valid_count"]])
        return result

    def _reject(self, reason: str) -> dict[str, Any]:
        record = {"reason": reason, "epoch": self.epoch,
                  "next_input_sample": self.next_input_sample}
        self.rejections.append(record)
        return {"status": "rejected", "reason": reason}

    def process_frame(self, samples: Any, *, epoch: int, session_id: str,
                      first_input_sample: int, valid_count: int = SDK_FRAME_SAMPLES,
                      flags: int = 0) -> dict[str, Any]:
        before = self.summary()
        if self.drained:
            return self._reject("process_after_drain")
        if self.closed:
            return self._reject("process_after_final_input")
        if epoch != self.epoch:
            return self._reject("stale_epoch")
        if session_id != self.session_id:
            return self._reject("stale_session")
        if first_input_sample != self.next_input_sample:
            return self._reject("stale_source_position")
        if not isinstance(samples, (list, tuple)) or len(samples) != SDK_FRAME_SAMPLES:
            return self._reject("frame_samples_mismatch")
        if isinstance(valid_count, bool) or not isinstance(valid_count, int) or not 1 <= valid_count <= SDK_FRAME_SAMPLES:
            return self._reject("invalid_valid_count")
        if flags not in (0, FLAG_FINAL_INPUT):
            return self._reject("invalid_frame_flags")
        values = []
        for index, sample in enumerate(samples):
            if isinstance(sample, bool) or not isinstance(sample, (int, float)):
                return self._reject("nonnumeric_input")
            value = float(sample)
            if not math.isfinite(value):
                return self._reject("nonfinite_input")
            if index >= valid_count and value != 0.0:
                return self._reject("nonzero_final_padding")
            values.append(f32(value))
        self.samples.extend(values[:valid_count])
        self.next_input_sample += valid_count
        if flags & FLAG_FINAL_INPUT:
            self.closed = True
        emitted_before = len(self.frames)
        self._emit_available()
        if self.closed:
            self._emit_drain_tail()
        after = self.summary()
        if before["input_sha256"] == after["input_sha256"] and before["frame_map_sha256"] != after["frame_map_sha256"]:
            return self._reject("internal_state_inconsistent")
        return {
            "status": "ok",
            "accepted_samples": valid_count,
            "frames_emitted": len(self.frames) - emitted_before,
            "summary": after,
        }

    def _emit_available(self) -> None:
        radius = self.config["median_width_samples"] // 2
        while len(self.samples) >= self.output_cursor + SDK_FRAME_SAMPLES + radius:
            self._emit_frame(final=False)

    def _emit_drain_tail(self) -> None:
        radius = self.config["median_width_samples"] // 2
        while len(self.samples) >= self.output_cursor + SDK_FRAME_SAMPLES + radius:
            self._emit_frame(final=True)
        if self.output_cursor < len(self.samples):
            self._emit_frame(final=True)
        self.drained = True

    def _emit_frame(self, *, final: bool) -> None:
        p = self.output_cursor
        length = len(self.samples)
        radius = self.config["median_width_samples"] // 2
        valid_lo = max(0, p)
        valid_hi = min(length, p + SDK_FRAME_SAMPLES)
        payload: list[float] = []
        for offset in range(SDK_FRAME_SAMPLES):
            source_index = p + offset
            if 0 <= source_index < length:
                if source_index not in self.decisions:
                    self.decisions[source_index] = median_residual(
                        self.samples, source_index,
                        self.config["median_width_samples"], self.config["threshold"])
                payload.append(self.decisions[source_index]["output_f32"])
            else:
                payload.append(0.0)
        flags = 0
        if p < 0:
            flags |= FLAG_STARTUP_PADDING
        if final and p + SDK_FRAME_SAMPLES > length:
            flags |= FLAG_FINAL_PADDING
        self.frames.append({
            "frame_index": len(self.frames),
            "source_first_sample": p,
            "source_valid_start": valid_lo,
            "source_valid_end": valid_hi,
            "valid_offset": valid_lo - p,
            "valid_count": valid_hi - valid_lo,
            "flags": flags,
            "payload_sha256": digest_samples(payload),
            "samples": payload,
        })
        self.output_cursor += SDK_FRAME_SAMPLES

    def drain(self) -> dict[str, Any]:
        if not self.closed:
            return self._reject("drain_before_final_input")
        if self.drained:
            return {"status": "end_of_stream", "frames_emitted": 0}
        emitted_before = len(self.frames)
        self._emit_drain_tail()
        return {"status": "end_of_stream",
                "frames_emitted": len(self.frames) - emitted_before}

    def reset(self, new_epoch: int, *, session_id: str | None = None) -> dict[str, Any]:
        if isinstance(new_epoch, bool) or not isinstance(new_epoch, int) or new_epoch <= self.epoch:
            return {"status": "rejected", "reason": "nonincreasing_reset_epoch"}
        old = self.summary()
        self.samples = []
        self.next_input_sample = self.first_input_sample
        self.output_cursor = self.first_input_sample - self.config["median_width_samples"] // 2
        self.frames = []
        self.decisions = {}
        self.epoch = new_epoch
        if session_id is not None:
            self.session_id = session_id
        self.closed = False
        self.drained = False
        self.reset_count += 1
        return {"status": "ok", "before": old, "after": self.summary()}

    def publish_decision(self, decision: dict[str, Any], *, epoch: int,
                         session_id: str) -> dict[str, Any]:
        if not decision or "source_index" not in decision:
            return {"status": "rejected", "reason": "invalid_decision"}
        if epoch != self.epoch:
            return {"status": "rejected", "reason": "stale_epoch_decision"}
        if session_id != self.session_id:
            return {"status": "rejected", "reason": "stale_session_decision"}
        return {"status": "accepted"}


def frame_map(session: Session) -> list[dict[str, Any]]:
    return [{key: value for key, value in frame.items() if key != "samples"}
            for frame in session.frames]


def mapping_integrity(session: Session) -> dict[str, Any]:
    intervals = [(f["source_valid_start"], f["source_valid_end"]) for f in session.frames
                 if f["valid_count"] > 0]
    expected = len(session.samples)
    cursor = 0
    gaps: list[list[int]] = []
    overlaps: list[list[int]] = []
    for start, end in intervals:
        if start > cursor:
            gaps.append([cursor, start])
        if start < cursor:
            overlaps.append([start, cursor])
        cursor = max(cursor, end)
    if cursor < expected:
        gaps.append([cursor, expected])
    return {
        "source_interval": [0, expected],
        "valid_intervals": [list(item) for item in intervals],
        "union_equals_source": not gaps and not overlaps and cursor == expected,
        "gap_count": len(gaps),
        "overlap_count": len(overlaps),
        "gaps": gaps,
        "overlaps": overlaps,
        "delivered_valid_samples": sum(end - start for start, end in intervals),
        "startup_padding_samples": sum(f["valid_offset"] for f in session.frames),
        "final_padding_samples": sum(
            SDK_FRAME_SAMPLES - f["valid_offset"] - f["valid_count"] for f in session.frames),
        "frame_map": frame_map(session),
    }


def _pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    ml = sum(left) / len(left)
    mr = sum(right) / len(right)
    num = sum((a - ml) * (b - mr) for a, b in zip(left, right))
    dl = math.sqrt(sum((a - ml) ** 2 for a in left))
    dr = math.sqrt(sum((b - mr) ** 2 for b in right))
    return num / (dl * dr) if dl > 0 and dr > 0 else 0.0


def _envelope(samples: list[float], block: int = 40) -> list[float]:
    return [math.sqrt(sum(value * value for value in samples[i:i + block]) / len(samples[i:i + block]))
            for i in range(0, len(samples) - block + 1, block)]


def _pitch_window(labels: list[bool], length: int) -> list[int]:
    """Pick a deterministic click-free interior window for the pitch proxy."""
    if not any(labels):
        start = length // 4
        size = min(384, max(128, length // 2))
        return [start, start + size]
    best_start, best_size = None, 0
    cursor = 0
    while cursor < length:
        if labels[cursor]:
            cursor += 1
            continue
        start = cursor
        while cursor < length and not labels[cursor]:
            cursor += 1
        size = cursor - start
        if size > best_size and size >= 128 and start >= 32 and cursor + 32 <= length:
            best_start, best_size = start, size
    if best_start is None:
        return [length // 4, min(length, length // 4 + 128)]
    size = min(384, best_size)
    start = best_start + (best_size - size) // 2
    return [start, start + size]


def _pitch_period(samples: list[float], analysis_window: list[int]) -> dict[str, Any]:
    """Autocorrelation period proxy on a deterministic click-free window."""
    start, end = analysis_window
    window = samples[start:end]
    if len(window) < 128:
        return {"applicable": False, "reason": "window_too_short", "period_samples": None}
    mean = sum(window) / len(window)
    centered = [value - mean for value in window]
    energy = sum(value * value for value in centered)
    if energy <= 1e-18:
        return {"applicable": False, "reason": "silence", "period_samples": None}
    best_lag, best_score = None, -2.0
    for lag in range(60, min(181, len(window) // 2)):
        numerator = sum(centered[i] * centered[i + lag]
                        for i in range(len(window) - lag))
        denominator = sum(centered[i] * centered[i] for i in range(len(window) - lag))
        score = numerator / denominator if denominator > 0 else 0.0
        if score > best_score:
            best_lag, best_score = lag, score
    return {"applicable": True, "period_samples": best_lag,
            "autocorrelation": round(best_score, 9),
            "analysis_window": [start, start + len(window)]}


def _si_sdr(reference: list[float], output: list[float]) -> float:
    ref = [value - sum(reference) / len(reference) for value in reference]
    out = [value - sum(output) / len(output) for value in output]
    dot = sum(a * b for a, b in zip(ref, out))
    energy = sum(value * value for value in ref)
    scale = dot / energy if energy > 0 else 0.0
    target = [scale * value for value in ref]
    num = sum(value * value for value in target)
    den = sum((a - b) ** 2 for a, b in zip(out, target))
    return 10.0 * math.log10(max(num, 1e-30) / max(den, 1e-30))


def _runs(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []
    ordered = sorted(indices)
    result = [[ordered[0], ordered[0] + 1]]
    for value in ordered[1:]:
        if value == result[-1][1]:
            result[-1][1] = value + 1
        else:
            result.append([value, value + 1])
    return result


def score_case(session: Session, case: dict[str, Any]) -> dict[str, Any]:
    """Score one completed fixture using only adapter-produced output."""
    if not session.drained:
        raise ControlError("session_not_drained")
    clean = case["clean"]
    labels = case["labels"]
    transients = case.get("transient_labels", [False] * len(clean))
    output = session.output_payload()
    if len(output) != len(clean):
        raise ControlError("output_length_mismatch")
    detected = {index for index, decision in session.decisions.items() if decision["detected"]}
    repaired = {index for index, decision in session.decisions.items() if decision["repaired"]}
    labeled = {index for index, value in enumerate(labels) if value}
    tp = len(detected & labeled)
    fp = len(detected - labeled)
    fn = len(labeled - detected)
    non_click_changed = sum(1 for i in range(len(clean))
                            if not labels[i] and output[i] != f32(clean[i]))
    transient_preserved = sum(1 for i in range(len(clean))
                              if transients[i] and output[i] == f32(clean[i]))
    transient_total = sum(1 for value in transients if value)
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(clean, output)) / len(clean))
    pitch_window = _pitch_window(labels, len(clean))
    pitch_clean = _pitch_period(clean, pitch_window)
    pitch_output = _pitch_period(output, pitch_window)
    mapping = mapping_integrity(session)
    plan = case["rate_plan"]
    segments = [{key: seg[key] for key in
                 ("start", "end", "rate_num", "rate_den", "origin_ns", "rebuffer_ns_before")}
                for seg in plan["segments"]]
    return {
        "case_id": case["case_id"],
        "material": case["material"],
        "seed": case["seed"],
        "note": case["note"],
        "config_digest": session.config_digest,
        "session": session.summary(),
        "source": {
            "sample_count": len(clean),
            "duration_seconds": round(len(clean) / SAMPLE_RATE_HZ, 9),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "sha256": digest_samples(clean),
        },
        "output": {
            "valid_sample_count": len(output),
            "duration_seconds": round(len(output) / SAMPLE_RATE_HZ, 9),
            "sha256": digest_samples(output),
            "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        },
        "playback": {
            "clock_id": plan["clock_id"],
            "ns_per_source_sample_at_1x": NS_PER_SAMPLE,
            "playback_start_ns": plan["segments"][0]["origin_ns"],
            "playback_end_ns": case.get("playback_end_ns"),
            "playback_duration_ns": case.get("playback_end_ns", 0) - plan["segments"][0]["origin_ns"],
            "playback_duration_seconds": round(
                (case.get("playback_end_ns", 0) - plan["segments"][0]["origin_ns"]) / 1e9, 9),
            "rate_segments": segments,
            "rate_change_boundaries": case.get("rate_change_boundaries", []),
            "total_rebuffer_ns": sum(seg["rebuffer_ns_before"] for seg in plan["segments"]),
            "buffering_delay_samples": session.config["median_width_samples"] // 2,
            "buffering_semantics": (
                "160-sample f32 frames in source coordinates; 3 trailing samples of lookahead; "
                "source_first_sample=frame_start-3; startup and final padding flagged and excluded "
                "from valid content; no resampling, time stretch, pause or filler insertion"),
        },
        "detections": {
            "labeled_click_samples": len(labeled),
            "detected_click_samples": len(detected),
            "repaired_samples": len(repaired),
            "tp_samples": tp,
            "fp_samples": fp,
            "fn_samples": fn,
            "precision": round(tp / (tp + fp), 9) if tp + fp else None,
            "recall": round(tp / len(labeled), 9) if labeled else None,
            "click_run_sources": [[start, end] for start, end in _runs(sorted(labeled))],
            "detected_run_sources": [[start, end] for start, end in _runs(sorted(detected))],
            "suppressed_run_sources": [[start, end] for start, end in _runs(sorted(repaired))],
            "first_detection_source_ns": min(session.decisions[i]["source_start_ns"]
                                             for i in detected) if detected else None,
            "last_detection_source_ns": max(session.decisions[i]["source_end_ns"]
                                            for i in detected) if detected else None,
            "decisions_tied_to_source_timestamps": all(
                decision["source_start_ns"] == decision["source_index"] * NS_PER_SAMPLE
                for decision in session.decisions.values()),
        },
        "preservation": {
            "non_click_samples_changed": non_click_changed,
            "non_click_equality_fraction": round(1.0 - non_click_changed / max(1, len(clean) - len(labeled)), 9),
            "transient_samples_preserved": transient_preserved,
            "transient_samples_total": transient_total,
            "transient_preservation_fraction": round(transient_preserved / transient_total, 9)
                                              if transient_total else None,
            "envelope_correlation_clean_vs_output": round(_pearson(_envelope(clean), _envelope(output)), 9),
            "si_sdr_db_vs_clean": round(_si_sdr(clean, output), 9),
            "rmse_vs_clean": round(rmse, 9),
            "pitch_clean": pitch_clean,
            "pitch_output": pitch_output,
            "pitch_delta_samples": (pitch_output["period_samples"] - pitch_clean["period_samples"]
                                    if pitch_clean["applicable"] and pitch_output["applicable"] else None),
        },
        "source_output_mapping": mapping,
        "qualification": {
            "candidate_qualified": False,
            "missing_result_qualifies": False,
            "reason": "synthetic opt-in reference; no natural events, listening, target device or release gate",
        },
    }
