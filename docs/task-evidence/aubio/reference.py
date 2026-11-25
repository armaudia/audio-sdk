# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local aubio-style tempo/onset reference evidence.

This is an original, stdlib-only surrogate written for this task. It is NOT
aubio source, a vendored aubio build, a licensed aubio runtime or an aubio
result. No upstream code, binary, model, corpus or asset is present here. The
model consumes caller-owned 16 kHz mono float32 160-sample frames, derives a
log-energy onset envelope and estimates tempo from source-anchored inter-onset
intervals. It is proposal-only synthetic evidence at the SDK boundary: no
provider is registered, no installed behavior changes and no release claim is
made.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]

VERSION = "0.1.0"
CONTRACT_ID = "audio-sdk/aubio-evidence/0.1"
TASK = "SDK-AUBIO"
COMPONENT = "aubio"
BASE_COMMIT = "caa0bba3643834885135a3a62c97034af4124802"
BRANCH = "swarm/SDK-AUBIO"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1
SAMPLE_NS = 62500  # exactly 1/16000 s
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS  # exactly 10 ms
DEFAULT_LENGTH_SAMPLES = 64137  # 400 full frames plus a 137-sample final frame
FINAL_VALID_SAMPLES = 137

LOG_FLOOR = 1.0e-12
ONSET_THRESHOLD = 0.35
BASELINE_ALPHA = 0.20
MIN_ONSET_GAP_FRAMES = 7  # 70 ms, below the shortest admissible beat interval
TEMPO_MIN_BPM_X100 = 6000
TEMPO_MAX_BPM_X100 = 18000
TEMPO_STABILITY_SPREAD_X100 = 100
MIN_IOIS_FOR_TEMPO = 4

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md": (
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3"
    ),
    "REALTIME_COMPONENT_CANDIDATES.md": (
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d"
    ),
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": (
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
    ),
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "audio-benchmark-platform/audio-sdk/README.md": (
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35"
    ),
}

BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h": (
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766"
    ),
    "api/include/audio_sdk/session_v0.h": (
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1"
    ),
    "REUSE.toml": (
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8"
    ),
}

SPDX = {
    "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
    "SPDX-License-Identifier": "Apache-2.0",
}


class ReferenceRejection(ValueError):
    """Deterministic, machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def read_strict_json(path: Path) -> dict:
    """Read a JSON object; reject duplicate keys, NaN/Infinity and non-objects."""
    value = json.loads(Path(path).read_text(encoding="utf-8"),
                       object_pairs_hook=_unique_json_object,
                       parse_constant=_reject_json_constant)
    if not isinstance(value, dict):
        raise ValueError("json_not_object:" + str(path))
    return value


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_json(report)
    return text, sha256_bytes(text.encode("utf-8"))


def object_digest(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def signal_digest(samples: Sequence[float]) -> str:
    return sha256_bytes(b"".join(struct.pack("<f", float(value))
                                 for value in samples))


def llround(value: float) -> int:
    """C llround semantics: halves away from zero."""
    return (int(math.floor(value + 0.5)) if value >= 0.0
            else int(math.ceil(value - 0.5)))


def _exact_keys(value: dict, keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise ValueError("strict_keys_mismatch:" + label + ":"
                         + ",".join(sorted(set(value) ^ keys)))


def _integer(value: object, label: str, low: int, high: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise ValueError("invalid_integer:" + label)
    return value


def validate_contract(contract: dict) -> None:
    """Validate the strict JSON contract before any report is generated."""
    _exact_keys(contract, {"spdx", "protocol", "task", "component",
                           "verification_profile", "base_commit", "branch",
                           "status", "decision", "exact_scope", "installed_v0",
                           "licensing", "remaining_gates"}, "contract")
    if contract["spdx"] != SPDX or contract["protocol"] != CONTRACT_ID:
        raise ValueError("contract_identity_mismatch")
    if (contract["task"] != TASK or contract["component"] != COMPONENT
            or contract["verification_profile"] != "Rate"
            or contract["base_commit"] != BASE_COMMIT
            or contract["branch"] != BRANCH
            or contract["status"] != "proposal_only_not_qualified"):
        raise ValueError("contract_task_mismatch")
    decision = contract["decision"]
    _exact_keys(decision, {"status", "promotion", "production_exposure",
                           "incomplete", "proposal_only_not_qualified",
                           "expose_as_processor", "registered",
                           "default_enabled"}, "contract.decision")
    if (decision["status"] != "incomplete" or decision["promotion"] != "defer"
            or decision["production_exposure"] != "DEFER"
            or decision["incomplete"] is not True
            or decision["proposal_only_not_qualified"] is not True
            or any(decision[key] is not False for key in
                   ("expose_as_processor", "registered", "default_enabled"))):
        raise ValueError("contract_decision_mismatch")
    scope = contract["exact_scope"]
    _exact_keys(scope, {"write_scope", "shared_files_changed",
                        "public_api_or_abi_changed", "headers_changed",
                        "descriptor_registry_changed", "descriptor_default_changed",
                        "provider_registration_changed", "installed_v0_changed",
                        "board_handoff_ruleset_or_main_changed", "other_task_changed"},
                "contract.exact_scope")
    if scope["write_scope"] != "docs/task-evidence/aubio/ only":
        raise ValueError("contract_write_scope_mismatch")
    if any(scope[key] is not False for key in scope if key != "write_scope"):
        raise ValueError("contract_scope_mismatch")
    installed = contract["installed_v0"]
    _exact_keys(installed, {"sample_rate_hz", "channels", "frame_samples",
                            "sample_format", "abi_major", "abi_minor", "changed"},
                "contract.installed_v0")
    if (installed["sample_rate_hz"] != SAMPLE_RATE_HZ
            or installed["channels"] != CHANNELS
            or installed["frame_samples"] != FRAME_SAMPLES
            or installed["sample_format"] != SAMPLE_FORMAT
            or installed["abi_major"] != ABI_MAJOR
            or installed["abi_minor"] != ABI_MINOR
            or installed["changed"] is not False):
        raise ValueError("contract_installed_v0_mismatch")
    licensing = contract["licensing"]
    _exact_keys(licensing, {"reported_upstream_license", "upstream_source_present",
                            "upstream_runtime_present", "relicensed", "review",
                            "proprietary_release_permitted", "vendored_license_file"},
                "contract.licensing")
    if (licensing["reported_upstream_license"] != "GPL-3.0"
            or licensing["review"] != "blocked"
            or any(licensing[key] is not False for key in
                   ("upstream_source_present", "upstream_runtime_present",
                    "relicensed", "proprietary_release_permitted",
                    "vendored_license_file"))):
        raise ValueError("contract_licensing_mismatch")
    if not isinstance(contract["remaining_gates"], list) or not contract["remaining_gates"]:
        raise ValueError("contract_gates_mismatch")


_STIMULUS_KEYS = {
    "periodic": {"kind", "length_samples", "period_samples", "beats",
                 "accent_every", "amplitude_milli", "accent_amplitude_milli",
                 "noise_amplitude_milli", "noise_seed"},
    "irregular": {"kind", "length_samples", "starts_frames", "durations_frames",
                  "amplitudes_milli"},
    "silence": {"kind", "length_samples"},
    "drift": {"kind", "length_samples", "periods_frames", "amplitude_milli"},
    "periodic_with_gap": {"kind", "length_samples", "period_samples",
                          "beats_before_gap", "beats_after_gap", "gap_samples",
                          "amplitude_milli"},
    "final_partial": {"kind", "length_samples", "onset_sample", "amplitude_milli"},
}


def validate_fixtures(fixtures: dict) -> None:
    """Validate the strict JSON stimulus manifest; no implicit defaults."""
    _exact_keys(fixtures, {"spdx", "protocol", "task", "stimuli"}, "fixtures")
    if (fixtures["spdx"] != SPDX or fixtures["protocol"] != CONTRACT_ID
            or fixtures["task"] != TASK):
        raise ValueError("fixtures_identity_mismatch")
    stimuli = fixtures["stimuli"]
    if not isinstance(stimuli, dict) or len(stimuli) != 10:
        raise ValueError("fixtures_stimuli_mismatch")
    for name, spec in sorted(stimuli.items()):
        if not isinstance(spec, dict) or "kind" not in spec:
            raise ValueError("invalid_stimulus:" + name)
        kind = spec["kind"]
        if kind not in _STIMULUS_KEYS:
            raise ValueError("unknown_stimulus_kind:" + kind)
        _exact_keys(spec, _STIMULUS_KEYS[kind], "stimulus:" + name)
        length = _integer(spec["length_samples"], "length_samples", 160, 200000)
        if length % FRAME_SAMPLES not in (0, FINAL_VALID_SAMPLES):
            raise ValueError("invalid_stimulus_length:" + name)
        if kind == "periodic":
            _integer(spec["period_samples"], "period_samples", FRAME_SAMPLES, 20000)
            _integer(spec["beats"], "beats", 1, 100)
            _integer(spec["accent_every"], "accent_every", 1, 16)
            for key in ("amplitude_milli", "accent_amplitude_milli",
                        "noise_amplitude_milli"):
                _integer(spec[key], key, 0, 1000)
            _integer(spec["noise_seed"], "noise_seed", 0, 2**31 - 1)
            if spec["amplitude_milli"] + spec["noise_amplitude_milli"] > 1000:
                raise ValueError("stimulus_not_bounded:" + name)
        elif kind == "irregular":
            starts = spec["starts_frames"]
            durations = spec["durations_frames"]
            amplitudes = spec["amplitudes_milli"]
            if not (isinstance(starts, list) and isinstance(durations, list)
                    and isinstance(amplitudes, list)
                    and len(starts) == len(durations) == len(amplitudes)
                    and 8 <= len(starts) <= 40):
                raise ValueError("irregular_lists_mismatch:" + name)
            previous = -MIN_ONSET_GAP_FRAMES
            for frame, duration, amplitude in zip(starts, durations, amplitudes):
                frame = _integer(frame, "starts_frames", 0, length // FRAME_SAMPLES)
                duration = _integer(duration, "durations_frames", 1, 16)
                _integer(amplitude, "amplitudes_milli", 1, 1000)
                if frame - previous < MIN_ONSET_GAP_FRAMES:
                    raise ValueError("irregular_onset_too_close:" + name)
                previous = frame
        elif kind == "drift":
            periods = spec["periods_frames"]
            if not isinstance(periods, list) or not 4 <= len(periods) <= 32:
                raise ValueError("drift_periods_mismatch:" + name)
            for period in periods:
                _integer(period, "periods_frames", MIN_ONSET_GAP_FRAMES, 200)
            _integer(spec["amplitude_milli"], "amplitude_milli", 1, 1000)
        elif kind == "periodic_with_gap":
            _integer(spec["period_samples"], "period_samples", FRAME_SAMPLES, 20000)
            _integer(spec["beats_before_gap"], "beats_before_gap", 2, 16)
            _integer(spec["beats_after_gap"], "beats_after_gap", 2, 16)
            _integer(spec["gap_samples"], "gap_samples", FRAME_SAMPLES, 40000)
            _integer(spec["amplitude_milli"], "amplitude_milli", 1, 1000)
        elif kind == "final_partial":
            onset = _integer(spec["onset_sample"], "onset_sample", 0, length - 1)
            if length % FRAME_SAMPLES != FINAL_VALID_SAMPLES or onset < length - FRAME_SAMPLES:
                raise ValueError("final_partial_onset_mismatch:" + name)
            _integer(spec["amplitude_milli"], "amplitude_milli", 1, 1000)
        else:  # silence
            if any(spec[key] != 0 for key in spec if key != "kind" and key != "length_samples"):
                raise ValueError("silence_spec_mismatch:" + name)


@dataclass(frozen=True)
class OnsetEvent:
    """Source-anchored analysis event in exact integer coordinates."""

    source_start: int
    source_end: int
    frame_index: int
    epoch: int
    strength_milli: int
    available_monotonic_ns: int
    capture_first_ns: int

    def as_dict(self) -> dict:
        return {
            "source_start": str(self.source_start),
            "source_end": str(self.source_end),
            "frame_index": str(self.frame_index),
            "epoch": str(self.epoch),
            "strength_milli": str(self.strength_milli),
            "available_monotonic_ns": str(self.available_monotonic_ns),
            "capture_first_ns": str(self.capture_first_ns),
        }


class Analyzer:
    """Causal, frame-clocked onset analyzer with explicit rejection behavior."""

    def __init__(self, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS, frame_samples: int = FRAME_SAMPLES,
                 sample_format: str = SAMPLE_FORMAT, epoch: int = 1):
        if (sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS
                or frame_samples != FRAME_SAMPLES or sample_format != SAMPLE_FORMAT):
            raise ReferenceRejection("unsupported_config", "v0 accepts only "
                                     "16000/1/160/float32")
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
            raise ReferenceRejection("invalid_epoch", "epoch must be a nonnegative integer")
        self.sample_rate_hz = sample_rate_hz
        self.channels = channels
        self.frame_samples = frame_samples
        self.sample_format = sample_format
        self.epoch = epoch
        self.frame_index = 0
        self.baseline = math.log(LOG_FLOOR)
        self.last_onset_frame: int | None = None
        self.events: list[OnsetEvent] = []
        self.rejections: list[str] = []
        self.frame_records: list[dict] = []

    @property
    def state_digest(self) -> str:
        return object_digest({
            "frame_index": str(self.frame_index),
            "baseline_milli": str(llround(self.baseline * 1000)),
            "last_onset_frame": (None if self.last_onset_frame is None
                                 else str(self.last_onset_frame)),
            "event_count": str(len(self.events)),
        })

    def _reject(self, code: str) -> None:
        self.rejections.append(code)
        raise ReferenceRejection(code, code)

    def process_frame(self, samples: Sequence[float] | None,
                      epoch: int | None = None, input_count: int | None = None,
                      valid_count: int | None = None) -> dict:
        if samples is None:
            self._reject("missing_input")
        if epoch is not None and epoch != self.epoch:
            self._reject("epoch_mismatch")
        count = len(samples)
        if input_count is not None and input_count != count:
            self._reject("frame_count_mismatch")
        if count != FRAME_SAMPLES:
            self._reject("frame_count_mismatch")
        valid = FRAME_SAMPLES if valid_count is None else valid_count
        if not isinstance(valid, int) or isinstance(valid, bool) or not 1 <= valid <= FRAME_SAMPLES:
            self._reject("invalid_valid_count")
        if any(not math.isfinite(float(value)) for value in samples):
            self._reject("nonfinite_input")
        if any(float(value) != 0.0 for value in samples[valid:]):
            self._reject("padding_not_zero")

        energy = sum(float(value) ** 2 for value in samples[:valid]) / valid
        log_energy = math.log(max(energy, LOG_FLOOR))
        strength = max(0.0, log_energy - self.baseline - ONSET_THRESHOLD)
        frame = self.frame_index
        source_start = frame * FRAME_SAMPLES
        onset = strength > 0.0 and (self.last_onset_frame is None
                                    or frame - self.last_onset_frame >= MIN_ONSET_GAP_FRAMES)
        strength_milli = llround(strength * 1000)
        record = {
            "frame_index": str(frame),
            "source_start": str(source_start),
            "valid_count": str(valid),
            "input_count": str(count),
            "strength_milli": str(strength_milli),
            "onset": onset,
        }
        if onset:
            self.events.append(OnsetEvent(
                source_start=source_start,
                source_end=source_start + valid,
                frame_index=frame,
                epoch=self.epoch,
                strength_milli=strength_milli,
                available_monotonic_ns=(frame + 1) * FRAME_NS,
                capture_first_ns=source_start * SAMPLE_NS,
            ))
            self.last_onset_frame = frame
        # Only a fully validated frame advances recurrent state.
        self.baseline = (1.0 - BASELINE_ALPHA) * self.baseline + BASELINE_ALPHA * log_energy
        self.frame_index += 1
        self.frame_records.append(record)
        return record


def _tone_burst(length: int, amplitude: float, frequency_hz: float = 150.0) -> list[float]:
    return [amplitude * (1.0 - index / length) * math.sin(2.0 * math.pi * frequency_hz * index / SAMPLE_RATE_HZ)
            for index in range(length)]


def _noise(length: int, amplitude: float, seed: int) -> list[float]:
    state = seed
    values: list[float] = []
    for _ in range(length):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(((2.0 * state / 0x7FFFFFFF) - 1.0) * amplitude)
    return values


def _add_burst(signal: list[float], start: int, burst: Sequence[float],
               length_samples: int) -> None:
    for offset, value in enumerate(burst):
        position = start + offset
        if position >= length_samples:
            break
        signal[position] += value


def generate_signal(spec: dict) -> tuple[list[float], list[tuple[int, int]]]:
    """Return a bounded synthetic signal and half-open excluded gap intervals."""
    length = spec["length_samples"]
    kind = spec["kind"]
    signal = [0.0] * length
    gaps: list[tuple[int, int]] = []
    if kind == "silence":
        return signal, gaps
    if kind == "periodic":
        period = spec["period_samples"]
        accent = spec["accent_every"]
        for beat in range(spec["beats"]):
            amplitude = (spec["accent_amplitude_milli"] if beat % accent == 0
                         else spec["amplitude_milli"]) / 1000.0
            burst = _tone_burst(96, amplitude)
            _add_burst(signal, beat * period, burst, length)
        noise = spec["noise_amplitude_milli"] / 1000.0
        if noise:
            for index, value in enumerate(_noise(length, noise, spec["noise_seed"])):
                signal[index] += value
    elif kind == "periodic_with_gap":
        period = spec["period_samples"]
        before = spec["beats_before_gap"]
        gap_start = before * period
        gap_end = gap_start + spec["gap_samples"]
        gaps.append((gap_start, gap_end))
        positions = [beat * period for beat in range(before)]
        positions.extend(gap_end + beat * period
                         for beat in range(spec["beats_after_gap"]))
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        for position in positions:
            _add_burst(signal, position, burst, length)
    elif kind == "irregular":
        for start_frame, duration_frames, amplitude in zip(
                spec["starts_frames"], spec["durations_frames"],
                spec["amplitudes_milli"]):
            burst_length = duration_frames * FRAME_SAMPLES
            burst = _tone_burst(burst_length, amplitude / 1000.0, 135.0)
            _add_burst(signal, start_frame * FRAME_SAMPLES, burst, length)
    elif kind == "drift":
        position = 0
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        for period in spec["periods_frames"]:
            _add_burst(signal, position, burst, length)
            position += period * FRAME_SAMPLES
        _add_burst(signal, position, burst, length)
    elif kind == "final_partial":
        burst = _tone_burst(96, spec["amplitude_milli"] / 1000.0)
        _add_burst(signal, spec["onset_sample"], burst, length)
    else:
        raise ValueError("unknown_stimulus_kind:" + kind)
    for value in signal:
        if not math.isfinite(value) or abs(value) > 1.0 + 1e-12:
            raise ValueError("generated_signal_out_of_bounds")
    return signal, gaps


def estimate_tempo(events: Sequence[OnsetEvent],
                   gap_intervals: Sequence[tuple[int, int]] = ()) -> dict:
    """Estimate tempo from source-anchored IOIs; fail closed on instability."""
    frames = [event.frame_index for event in events]
    if not frames:
        return {"status": "no_onsets", "onset_count": "0", "ioi_frames": [],
                "bpm_x100_values": [], "spread_x100": "0", "bpm_x100": None,
                "excluded_ioi_count": "0"}
    iois: list[int] = []
    excluded = 0
    for first, second in zip(frames, frames[1:]):
        midpoint = ((first + second) * FRAME_SAMPLES) // 2
        if any(start <= midpoint < end for start, end in gap_intervals):
            excluded += 1
            continue
        iois.append(second - first)
    if len(iois) < MIN_IOIS_FOR_TEMPO:
        return {"status": "insufficient_onsets", "onset_count": str(len(frames)),
                "ioi_frames": [str(value) for value in iois],
                "bpm_x100_values": [], "spread_x100": "0", "bpm_x100": None,
                "excluded_ioi_count": str(excluded)}
    bpms = [llround(600000 / ioi) for ioi in iois]
    spread = max(bpms) - min(bpms)
    base = {"onset_count": str(len(frames)),
            "ioi_frames": [str(value) for value in iois],
            "bpm_x100_values": [str(value) for value in bpms],
            "spread_x100": str(spread),
            "excluded_ioi_count": str(excluded)}
    if any(value < TEMPO_MIN_BPM_X100 or value > TEMPO_MAX_BPM_X100 for value in bpms):
        return dict(base, status="tempo_out_of_range", bpm_x100=None)
    if spread > TEMPO_STABILITY_SPREAD_X100:
        return dict(base, status="no_stable_tempo", bpm_x100=None)
    return dict(base, status="stable", bpm_x100=str(llround(sum(bpms) / len(bpms))))


def analyze(spec: dict, epoch: int = 1) -> dict:
    """Run one strict-fixture stimulus through the analyzer and tempo scorer."""
    signal, gaps = generate_signal(spec)
    analyzer = Analyzer(epoch=epoch)
    for start in range(0, len(signal), FRAME_SAMPLES):
        block = signal[start:start + FRAME_SAMPLES]
        valid = len(block)
        padded = block + [0.0] * (FRAME_SAMPLES - valid)
        analyzer.process_frame(padded, epoch=epoch, input_count=FRAME_SAMPLES,
                               valid_count=valid)
    tempo = estimate_tempo(analyzer.events, gaps)
    onset_frames = [event.frame_index for event in analyzer.events]
    return {
        "signal": signal,
        "gaps": gaps,
        "analyzer": analyzer,
        "tempo": tempo,
        "onset_frames": onset_frames,
        "events": analyzer.events,
        "source_end": len(signal),
        "final_valid_count": len(signal) % FRAME_SAMPLES or FRAME_SAMPLES,
    }


def fixture_catalog(fixtures: dict) -> dict:
    """Describe each strict fixture without running it (report identity only)."""
    catalog: dict[str, dict] = {}
    for name, spec in sorted(fixtures["stimuli"].items()):
        catalog[name] = {
            "kind": spec["kind"],
            "length_samples": str(spec["length_samples"]),
            "full_frames": str(spec["length_samples"] // FRAME_SAMPLES),
            "final_valid_count": str(spec["length_samples"] % FRAME_SAMPLES
                                     or FRAME_SAMPLES),
        }
    return catalog


def _pin_rows() -> tuple[dict, dict]:
    source_pins: dict[str, dict] = {}
    for relative, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(AUDIO_ROOT / relative)
        source_pins[relative] = {"sha256": expected, "actual": actual,
                                 "verified": actual == expected}
    boundary_pins: dict[str, dict] = {}
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(WORKTREE / relative)
        boundary_pins[relative] = {"sha256": expected, "actual": actual,
                                   "verified": actual == expected}
    for rows in (source_pins, boundary_pins):
        if any(not row["verified"] for row in rows.values()):
            raise ValueError("pin_mismatch")
    return source_pins, boundary_pins


def _adverse_cases(fixtures: dict) -> list[dict]:
    """All rejection/nonfinite/missing/adverse outcomes remain explicit."""
    cases: list[dict] = []

    def reject_case(case_id: str, description: str, call) -> None:
        analyzer = Analyzer()
        before = analyzer.state_digest
        try:
            call(analyzer)
        except ReferenceRejection as error:
            cases.append({
                "id": case_id, "input": description, "status": "rejected",
                "code": error.code, "qualifies": False,
                "state_unchanged": analyzer.state_digest == before,
                "onset_count": str(len(analyzer.events)),
            })
            return
        raise ValueError("adverse_case_not_rejected:" + case_id)

    reject_case("MISS-01", "missing frame buffer (None)",
                lambda analyzer: analyzer.process_frame(None))
    reject_case("INV-01", "input_count=159 for a 160-sample buffer",
                lambda analyzer: analyzer.process_frame([0.0] * FRAME_SAMPLES,
                                                        input_count=159))
    reject_case("INV-02", "nonfinite NaN in one input sample",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * 80 + [float("nan")] + [0.0] * 79))
    reject_case("INV-03", "nonfinite +Infinity in one input sample",
                lambda analyzer: analyzer.process_frame(
                    [float("inf")] + [0.0] * 159))
    reject_case("INV-04", "short frame (159 samples)",
                lambda analyzer: analyzer.process_frame([0.0] * 159))
    reject_case("INV-05", "stale epoch 0 on an epoch-1 analyzer",
                lambda analyzer: analyzer.process_frame([0.0] * FRAME_SAMPLES, epoch=0))
    reject_case("INV-06", "invalid final valid_count=0",
                lambda analyzer: analyzer.process_frame([0.0] * FRAME_SAMPLES,
                                                        valid_count=0))
    reject_case("INV-07", "nonzero final padding byte",
                lambda analyzer: analyzer.process_frame(
                    [0.0] * 137 + [0.5] + [0.0] * 22, valid_count=137))
    for case_id, description, kwargs in (
            ("CFG-01", "sample_rate_hz=44100", {"sample_rate_hz": 44100}),
            ("CFG-02", "channels=2", {"channels": 2}),
            ("CFG-03", "frame_samples=512", {"frame_samples": 512}),
            ("CFG-04", "sample_format=float64", {"sample_format": "float64"})):
        try:
            Analyzer(**kwargs)
        except ReferenceRejection as error:
            cases.append({"id": case_id, "input": description, "status": "rejected",
                          "code": error.code, "qualifies": False,
                          "state_unchanged": True, "onset_count": "0"})
        else:
            raise ValueError("config_case_not_rejected:" + case_id)

    for name in ("low_snr_adverse", "tempo_out_of_range_adverse",
                 "speech_like_unfamiliar", "silence", "drift", "rebuffer"):
        cases.append({
            "id": "ADV-" + name,
            "input": "strict fixture stimulus " + name,
            "status": "recorded",
            "result": fixtures["stimuli"][name]["kind"],
            "qualifies": False,
            "note": "Adverse or control outcome is retained; it never qualifies a candidate.",
        })
    return cases


def _score(report: dict) -> dict:
    """Score the synthetic fixture only; passing here is not release evidence."""
    checks: list[dict] = []

    def check(check_id: str, expected: object, observed: object, note: str) -> None:
        checks.append({"id": check_id, "expected": expected, "observed": observed,
                       "passed": expected == observed, "note": note})

    tempo = report["tempo"]
    rate = report["rate_profile"]
    check("identity_1x_bpm", "10000", tempo["music_like_1x"]["bpm_x100"],
          "100 BPM at 1x, exactly 60 frames per beat")
    check("rate_0_8_bpm", "8000", tempo["rate_0_8"]["bpm_x100"],
          "event-time scaling by 0.8 gives 80 BPM")
    check("rate_1_2_bpm", "12000", tempo["rate_1_2"]["bpm_x100"],
          "event-time scaling by 1.2 gives 120 BPM")
    check("rate_duration_error", "0", str(rate["duration"]["max_error_samples"]),
          "exact source-sample span under each rate")
    check("speech_no_stable_tempo", True,
          tempo["speech_like_unfamiliar"]["bpm_x100"] is None
          and tempo["speech_like_unfamiliar"]["status"] != "stable",
          "unfamiliar speech surrogate has no stable beat period")
    check("silence_no_onsets", "no_onsets", tempo["silence"]["status"],
          "silence produces no onset event")
    check("music_stable", "stable", tempo["music_like_1x"]["status"],
          "music surrogate produces a stable tempo")
    check("tempo_out_of_range", "tempo_out_of_range",
          tempo["tempo_out_of_range_adverse"]["status"],
          "300 BPM surrogate is rejected by the 60-180 BPM window")
    check("low_snr_adverse_nonqualifying", False,
          rate["low_snr_adverse"]["qualifies"],
          "adverse low-SNR result is recorded but never promoted")
    check("rebuffer_gap_suppressed", True,
          rate["rebuffer"]["cross_gap_ioi_suppressed"],
          "no tempo is estimated across the rebuffer gap")
    check("drift_recorded", True, rate["drift"]["monotonic_ioi_decrease"],
          "drift is recorded as a source-anchored IOI sequence")
    check("final_partial_valid", "137", str(rate["final_partial_window"]["valid_count"]),
          "final partial frame is explicit")
    check("mapping_nonnegative", True,
          rate["source_output_mapping"]["min_availability_margin_ns"] >= 0,
          "no event is available before its source capture time")
    check("transient_proxy", "-50", str(rate["transient_proxy"]["final_partial_error_samples"]),
          "frame-quantized onset error in the final partial frame")
    check("all_cases_explicit", True,
          all(case["qualifies"] is False and case["status"] in ("rejected", "recorded")
              for case in report["adverse_cases"]),
          "every adverse, missing, invalid or nonfinite case is explicit")
    check("all_gates_blocked", True, report["qualification"]["all_release_gates_blocked"],
          "no release gate is opened by synthetic evidence")
    failed = [row["id"] for row in checks if not row["passed"]]
    return {"passed": not failed, "checks": checks, "failed_checks": failed,
            "scope": "synthetic fixture only; not release qualification"}


def build_report() -> dict:
    """Build the canonical, deterministic report from strict JSON inputs."""
    contract = read_strict_json(TASK_DIR / "contract.json")
    fixtures = read_strict_json(TASK_DIR / "fixtures.json")
    validate_contract(contract)
    validate_fixtures(fixtures)
    source_pins, boundary_pins = _pin_rows()
    specs = fixtures["stimuli"]
    analyses = {name: analyze(spec) for name, spec in sorted(specs.items())}
    tempo = {name: value["tempo"] for name, value in sorted(analyses.items())}
    stimuli: dict[str, dict] = {}
    for name, value in sorted(analyses.items()):
        stimuli[name] = {
            "length_samples": str(len(value["signal"])),
            "frames": str((len(value["signal"]) + FRAME_SAMPLES - 1) // FRAME_SAMPLES),
            "final_valid_count": str(value["final_valid_count"]),
            "float32_sha256": signal_digest(value["signal"]),
            "finite": all(math.isfinite(sample) for sample in value["signal"]),
            "bounded": all(abs(sample) <= 1.0 for sample in value["signal"]),
            "excluded_gap_samples": [[str(start), str(end)] for start, end in value["gaps"]],
        }

    durations: dict[str, dict] = {}
    for name in ("music_like_1x", "rate_0_8", "rate_1_2"):
        frames = analyses[name]["onset_frames"]
        period = specs[name]["period_samples"]
        expected_span = (len(frames) - 1) * period
        observed_span = (frames[-1] - frames[0]) * FRAME_SAMPLES
        durations[name] = {
            "onset_count": str(len(frames)),
            "period_samples": str(period),
            "expected_span_samples": str(expected_span),
            "observed_span_samples": str(observed_span),
            "error_samples": str(observed_span - expected_span),
        }
    rate_changes = []
    for name, expected_bpm in (("rate_0_8", "8000"), ("music_like_1x", "10000"),
                               ("rate_1_2", "12000")):
        rate_changes.append({"stimulus": name, "expected_bpm_x100": expected_bpm,
                             "observed_bpm_x100": tempo[name]["bpm_x100"]})
    drift_iois = [int(value) for value in tempo["drift"]["ioi_frames"]]
    drift_decreasing = len(drift_iois) >= 4 and all(
        later < earlier for earlier, later in zip(drift_iois, drift_iois[1:]))
    rebuffer_onsets = analyses["rebuffer"]["onset_frames"]
    rebuffer_gap = analyses["rebuffer"]["gaps"][0]
    cross_gap = [(first, second) for first, second in
                 zip(rebuffer_onsets, rebuffer_onsets[1:])
                 if any(start <= (first + second) * FRAME_SAMPLES // 2 < end
                        for start, end in [rebuffer_gap])]
    final_events = analyses["final_partial"]["events"]
    margins = [event.available_monotonic_ns - event.capture_first_ns
               for events in (value["events"] for value in analyses.values())
               for event in events]
    rate_profile = {
        "identity_1x": {"stimulus": "music_like_1x", "bpm_x100": tempo["music_like_1x"]["bpm_x100"]},
        "rate_changes": rate_changes,
        "duration": {"cases": durations,
                     "max_error_samples": max(abs(int(row["error_samples"]))
                                              for row in durations.values())},
        "source_output_mapping": {
            "audio_output_produced": False,
            "analysis_event_source_anchor": True,
            "frame_hop_samples": str(FRAME_SAMPLES),
            "available_ns_per_frame": str(FRAME_NS),
            "min_availability_margin_ns": min(margins) if margins else 0,
            "note": "No audio output, playback actuator, device clock or wall clock is claimed.",
        },
        "pitch": {
            "status": "not_measurable_analysis_only",
            "qualifies": False,
            "note": "Onset/tempo analysis does not alter pitch; no pitch-shift claim is made.",
        },
        "transient_proxy": {
            "final_partial_error_samples": (final_events[0].source_start
                                            - specs["final_partial"]["onset_sample"]
                                            if final_events else None),
            "note": "Frame-quantized onset timing proxy only; not transient audibility or listening.",
        },
        "playback_buffering": {
            "device_buffer_measured": False,
            "sdk_worker_count": "0",
            "sdk_queue_depth": "0",
            "analysis_frame_aggregation_samples": str(FRAME_SAMPLES),
            "final_partial_valid_count": str(FINAL_VALID_SAMPLES),
            "final_padding_zero_verified": True,
        },
        "speech_unfamiliar": {"stimulus": "speech_like_unfamiliar",
                              "status": tempo["speech_like_unfamiliar"]["status"],
                              "qualifies": False},
        "music": {"stimulus": "music_like_1x", "status": tempo["music_like_1x"]["status"],
                  "bpm_x100": tempo["music_like_1x"]["bpm_x100"]},
        "silence": {"stimulus": "silence", "status": tempo["silence"]["status"]},
        "rebuffer": {
            "gap_samples": [[str(start), str(end)] for start, end in analyses["rebuffer"]["gaps"]],
            "excluded_ioi_count": str(tempo["rebuffer"]["excluded_ioi_count"]),
            "cross_gap_ioi_suppressed": bool(cross_gap)
            and int(tempo["rebuffer"]["excluded_ioi_count"]) == len(cross_gap),
            "status": tempo["rebuffer"]["status"],
        },
        "drift": {
            "ioi_frames": tempo["drift"]["ioi_frames"],
            "monotonic_ioi_decrease": drift_decreasing,
            "status": tempo["drift"]["status"],
            "note": "Source-anchored IOI sequence, not a fixed global BPM claim.",
        },
        "final_partial_window": {
            "length_samples": str(len(analyses["final_partial"]["signal"])),
            "valid_count": str(analyses["final_partial"]["final_valid_count"]),
            "event_source_end": (str(final_events[0].source_end) if final_events else None),
            "event_beyond_source_end": bool(final_events
                                            and final_events[0].source_end
                                            > len(analyses["final_partial"]["signal"])),
            "event_digest": object_digest([event.as_dict() for event in final_events]),
        },
        "low_snr_adverse": {"stimulus": "low_snr_adverse",
                            "status": tempo["low_snr_adverse"]["status"],
                            "qualifies": False},
    }
    blockers = [
        {"id": "BLK-01", "gate": "licensing", "status": "blocked",
         "reason": "Pinned candidate note reports aubio as GPL-3.0 and unusable in a proprietary product without relicensing; no permission, notice review or commercial license is present.",
         "reopen_condition": "Written relicensing or alternative license from the rights holder plus license/notice/REUSE review and a versioned integration decision.",
         "qualifies": False},
        {"id": "BLK-02", "gate": "upstream_provenance", "status": "blocked",
         "reason": "No upstream aubio source, exact release, binary, runtime, model or asset digest is available; downloads are prohibited for this task.",
         "reopen_condition": "Pinned upstream source or licensed runtime with immutable digests, provenance, build record and independent comparison.",
         "qualifies": False},
        {"id": "BLK-03", "gate": "matched_evidence", "status": "blocked",
         "reason": "No real speech, unfamiliar speaker cohort, music, held-out labels, listening test or authorized scoring is present; all stimuli are analytic surrogates.",
         "reopen_condition": "Permitted held-out cohort, matched controls, onset/offset labels, stratified FN/FP and authorized listening or intelligibility scoring.",
         "qualifies": False},
        {"id": "BLK-04", "gate": "runtime_workload", "status": "blocked",
         "reason": "No target-device pacing, fill/flush, queue depth under load, deadline, availability, CPU, memory or service-time measurement was run.",
         "reopen_condition": "Paced target workload with monotonic telemetry, resource limits and explicit dropped/stale event accounting.",
         "qualifies": False},
        {"id": "BLK-05", "gate": "public_surface", "status": "blocked",
         "reason": "No analysis event type, variable-frame playback actuator, descriptor intake or registration exists in installed v0; this model is task-local Python only.",
         "reopen_condition": "Versioned public-surface and descriptor intake decision, implementation under that revision, installed conformance and independent review.",
         "qualifies": False},
        {"id": "BLK-06", "gate": "independent_review", "status": "blocked",
         "reason": "Only a task-local synthetic fixture was executed; no exact-head independent review or hosted CI approval is claimed here.",
         "reopen_condition": "Independent reviewer verification of the exact commit and successful hosted checks on that head.",
         "qualifies": False},
        {"id": "BLK-07", "gate": "pitch_and_transient_audibility", "status": "blocked",
         "reason": "An analysis-only tempo/onset model cannot establish pitch preservation or transient audibility under playback rate changes.",
         "reopen_condition": "Task-matched time-scale modification and playback qualification with authorized listening and pitch controls.",
         "qualifies": False},
    ]
    report = {
        "spdx": dict(SPDX),
        "protocol": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT,
        "verification_profile": "Rate",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": "proposal_only_not_qualified",
        "decision": dict(contract["decision"]),
        "exact_scope": dict(contract["exact_scope"]),
        "installed_v0": dict(contract["installed_v0"]),
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "contract_sha256": object_digest(contract),
        "fixtures_sha256": object_digest(fixtures),
        "licensing": {
            "reported_upstream_license": "GPL-3.0",
            "upstream_source_present": False,
            "upstream_runtime_present": False,
            "relicensed": False,
            "review": "blocked",
            "proprietary_release_permitted": False,
            "vendored_license_file": False,
            "task_file_spdx": "Apache-2.0",
            "reuse_aggregate_path": "docs/**",
            "note": "GPL-3.0 appears only as a pinned provenance/blocker string, never as the license of a task file.",
        },
        "synthetic_reference": {
            "algorithm": "original log-energy onset envelope with EWMA baseline and source-anchored IOI tempo",
            "not_upstream_aubio": True,
            "upstream_source_binary_or_runtime_vendored": False,
            "real_audio_or_corpus_used": False,
            "listening_or_device_timing_claim": False,
            "sample_rate_hz": str(SAMPLE_RATE_HZ),
            "frame_samples": str(FRAME_SAMPLES),
            "onset_threshold": str(ONSET_THRESHOLD),
            "min_onset_gap_frames": str(MIN_ONSET_GAP_FRAMES),
            "tempo_window_bpm": [str(TEMPO_MIN_BPM_X100 // 100),
                                 str(TEMPO_MAX_BPM_X100 // 100)],
        },
        "fixtures": fixture_catalog(fixtures),
        "stimuli": stimuli,
        "tempo": tempo,
        "rate_profile": rate_profile,
        "adverse_cases": _adverse_cases(fixtures),
        "acceptance_profile": {
            "profile": "Rate",
            "source_output_mapping": "analysis_event_source_intervals",
            "duration": "rate_span_mapping",
            "pitch": "not_applicable_analysis_only",
            "transient": "frame_quantized_onset_timing_proxy",
            "playback_buffering": "frame_aggregation_only",
            "rate_1x": "music_like_1x",
            "rate_changes": "event_time_scaling_0_8_and_1_2",
            "unfamiliar_speech": "speech_like_unfamiliar",
            "music": "music_like_1x",
            "silence": "silence",
            "rebuffer": "rebuffer",
            "drift": "drift",
            "final_partial_window": "final_partial",
        },
        "qualification": {
            "synthetic_profile_checks_passed": False,
            "all_release_gates_blocked": True,
            "release_results_present": False,
            "missing_result_promoted": False,
            "real_source_or_runtime_used": False,
            "listening_or_device_timing_claim": False,
        },
        "blockers": blockers,
        "remaining_gates": list(contract["remaining_gates"]),
        "non_claims": [
            "No aubio source, binary, runtime, weights, corpus or asset is used.",
            "No audio is modified, produced or played by this fixture.",
            "No provider is registered and no installed SDK behavior changes.",
            "No listening, device timing, pitch preservation or transient audibility result is claimed.",
            "No release qualification or independent reviewer approval is claimed.",
        ],
    }
    report["profile_scoring"] = _score(report)
    report["qualification"]["synthetic_profile_checks_passed"] = report["profile_scoring"]["passed"]
    if not report["profile_scoring"]["passed"]:
        raise ValueError("profile_scoring_failed:"
                         + ",".join(report["profile_scoring"]["failed_checks"]))
    return report
