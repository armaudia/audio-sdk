#!/usr/bin/env python3
"""Deterministic DSP control of the installed dsp.highpass80.v0 provider.

This is task-local evidence for SDK-SDK-HIGH-PASS-80-HZ. It drives an installed
audio-sdk package through the public v0 session API using harness.c, compares
the captured output with an analytic reference built from the pinned source
constants, and writes canonical JSON. It is not an audio-bench bundle, a
listening test, a workload qualification or a new frequency/rate qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import struct
import subprocess
import sys
import tempfile
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
AUDIOML_ROOT = SDK_ROOT.parents[2]
STIMULI_PATH = HERE / "stimuli.json"
VERIFICATION_PATH = AUDIOML_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
TASKS_PATH = AUDIOML_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"

PROTOCOL = "sdk.highpass80.installed-control/0.1"
TASK_ID = "SDK-SDK-HIGH-PASS-80-HZ"
PROVIDER_ID = "dsp.highpass80.v0"
BASE_COMMIT = "3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41"
BRANCH = "swarm/SDK-SDK-HIGH-PASS-80-HZ"
REVIEWER = "reviewer-sdk-highpass"

SOURCE_PINS = {
    "audio-benchmark-platform/audio-sdk/core/providers/highpass/highpass_provider.c": (
        SDK_ROOT / "core/providers/highpass/highpass_provider.c",
        "051b423d078835ff1ab23d7303c8e0c8f876d3d4211339682f366797ef7fffef",
        "Frozen fixed-rate built-in: 80 Hz, Q=0.7071067811865476, 16 kHz, "
        "double filter state, float32 output, no buffering delay.",
    ),
    "REALTIME_COMPONENT_CANDIDATES.md": (
        AUDIOML_ROOT / "REALTIME_COMPONENT_CANDIDATES.md",
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
        "Source report: two-pole high-pass code exists locally, rumble/DC "
        "removal use, and no dedicated quality benchmark.",
    ),
}

CONTROL_EXPECTED: dict[str, dict[str, Any]] = {
    "create_bad_rate": {"status": "unsupported", "field": "format"},
    "create_bad_channels": {"status": "unsupported", "field": "format"},
    "create_bad_frame": {"status": "unsupported", "field": "format"},
    "create_bad_mode": {"status": "unsupported", "field": "execution_mode"},
    "create_null_config": {"status": "invalid_argument", "field": "config"},
    "create_null_out": {"status": "invalid_argument", "field": "out"},
    "create_null_id": {"status": "invalid_argument", "field": "provider_id"},
    "process_null_frame": {"status": "invalid_argument"},
    "process_null_input": {"status": "invalid_argument"},
    "process_null_output": {"status": "invalid_argument"},
    "process_null_samples": {"status": "invalid_argument"},
    "process_small_capacity": {"status": "invalid_argument"},
    "process_null_result": {"status": "invalid_argument"},
    "process_bad_position": {"status": "invalid_argument", "reset_status": 6, "recovered_status": 6},
    "recover_after_bad_position": {"status": "invalid_argument", "reset_status": 0, "recovered_status": 0},
    "reset_negative_first": {"status": "invalid_argument", "field": "first_input_sample"},
    "drain_null_output": {"status": "invalid_argument", "begin_status": 0},
    "drain_null_result": {"status": "invalid_argument", "begin_status": 0},
    "nonfinite_nan": {"status": "invalid_argument"},
    "nonfinite_inf": {"status": "invalid_argument"},
}

CANON = {"sort_keys": True, "separators": (",", ":"), "ensure_ascii": True, "allow_nan": False}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, **CANON) + "\n").encode("utf-8")


def write_canonical(path: pathlib.Path, obj: Any) -> str:
    payload = canonical_bytes(obj)
    path.write_bytes(payload)
    return digest(payload)


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0


def mean_abs(values: list[float]) -> float:
    return sum(abs(value) for value in values) / len(values) if values else 0.0


def max_abs_error(actual: list[float], expected: list[float]) -> float:
    if len(actual) != len(expected):
        return float("inf")
    return max((abs(a - b) for a, b in zip(actual, expected)), default=0.0)


def design(coeff_cfg: dict[str, Any]) -> tuple[float, float, float, float, float]:
    fixed = coeff_cfg["fixed_v0"]
    rate = float(fixed["sample_rate_hz"])
    cutoff = float(fixed["cutoff_hz"])
    q = float(fixed["q"])
    w0 = 2.0 * math.pi * cutoff / rate
    cosine = math.cos(w0)
    alpha = math.sin(w0) / (2.0 * q)
    a0 = 1.0 + alpha
    b0 = ((1.0 + cosine) * 0.5) / a0
    b1 = (-(1.0 + cosine)) / a0
    return b0, b1, b0, (-2.0 * cosine) / a0, (1.0 - alpha) / a0


def reference_filter(values: list[float], coeffs: tuple[float, float, float, float, float]) -> list[float]:
    b0, b1, b2, a1, a2 = coeffs
    z1 = z2 = 0.0
    output: list[float] = []
    for value in values:
        x = f32(value)
        y = b0 * x + z1
        z1 = b1 * x - a1 * y + z2
        z2 = b2 * x - a2 * y
        output.append(y)
    return output


def magnitude_response(frequency_hz: float, stimuli: dict[str, Any],
                       coeffs: tuple[float, float, float, float, float]) -> float:
    rate = float(stimuli["fixed_v0"]["sample_rate_hz"])
    b0, b1, b2, a1, a2 = coeffs
    w = 2.0 * math.pi * frequency_hz / rate
    n1 = complex(math.cos(-w), math.sin(-w))
    n2 = n1 * n1
    numerator = b0 + b1 * n1 + b2 * n2
    denominator = 1.0 + a1 * n1 + a2 * n2
    return abs(numerator / denominator)


def sine(frequency_hz: float, amplitude: float, samples: int,
         rate: int = 16000, phase: float = 0.0) -> list[float]:
    return [
        amplitude * math.sin(2.0 * math.pi * frequency_hz * index / rate + phase)
        for index in range(samples)
    ]


def chirp_values(config: dict[str, Any], rate: int) -> list[float]:
    count = int(config["samples"])
    start = float(config["start_hz"])
    end = float(config["end_hz"])
    amplitude = float(config["amplitude"])
    phase = 0.0
    output = []
    for index in range(count):
        fraction = index / max(count - 1, 1)
        frequency = start * (end / start) ** fraction
        phase += 2.0 * math.pi * frequency / rate
        output.append(amplitude * math.sin(phase))
    return output


def speech_values(config: dict[str, Any], rate: int) -> list[float]:
    count = int(config["frames"]) * 160
    f0 = float(config["f0_hz"])
    harmonics = int(config["harmonics"])
    period = int(config["syllable_period_samples"])
    formants = [float(value) for value in config["formants_hz"]]
    width = float(config["formant_width_hz"])
    formant_gain = float(config["formant_gain"])
    output = []
    for index in range(count):
        position = index % period
        envelope = 0.5 - 0.5 * math.cos(2.0 * math.pi * position / period)
        sample = 0.0
        for harmonic in range(1, harmonics + 1):
            frequency = f0 * harmonic
            emphasis = 1.0
            for formant in formants:
                emphasis += formant_gain / (1.0 + ((frequency - formant) / width) ** 2)
            amplitude = emphasis / (harmonic ** 1.25)
            sample += amplitude * math.sin(2.0 * math.pi * frequency * index / rate + 0.31 * harmonic)
        output.append(0.12 * envelope * sample / harmonics)
    return output


def goertzel_power(values: list[float], frequency_hz: float, rate: int) -> float:
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency_hz / rate)
    s1 = s2 = 0.0
    for value in values:
        s0 = value + coefficient * s1 - s2
        s2 = s1
        s1 = s0
    return (s1 * s1 + s2 * s2 - coefficient * s1 * s2) / (len(values) ** 2)


def band_power(values: list[float], low_hz: float, high_hz: float, rate: int) -> float:
    bins = 48
    total = 0.0
    for index in range(bins):
        frequency = low_hz * (high_hz / low_hz) ** (index / (bins - 1))
        total += goertzel_power(values, frequency, rate)
    return total


def envelope_correlation(left: list[float], right: list[float]) -> float:
    def envelopes(values: list[float]) -> list[float]:
        return [rms(values[i:i + 160]) for i in range(0, len(values), 160)]
    a, b = envelopes(left), envelopes(right)
    if len(a) != len(b) or len(a) < 2:
        return 0.0
    mean_a, mean_b = sum(a) / len(a), sum(b) / len(b)
    numerator = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    denominator = math.sqrt(sum((x - mean_a) ** 2 for x in a) * sum((y - mean_b) ** 2 for y in b))
    return numerator / denominator if denominator else 0.0


def frame_lines(signal: list[float], epoch: int = 1, first: int = 0,
                frame_samples: int = 160) -> list[str]:
    lines = []
    for offset in range(0, len(signal), frame_samples):
        chunk = signal[offset:offset + frame_samples]
        valid = len(chunk)
        flags = 1 if valid < frame_samples else 0
        padded = list(chunk) + [0.0] * (frame_samples - valid)
        text = " ".join("%.9g" % value for value in padded)
        lines.append(f"frame {valid} {flags} {first + offset} {epoch} {text}")
    return lines


class InstalledRunner:
    def __init__(self, prefix: pathlib.Path, harness: pathlib.Path) -> None:
        self.prefix = prefix
        self.harness = harness
        if not harness.is_file():
            raise SystemExit(f"harness not found: {harness}")
        conformance = prefix / "bin/audio_sdk_conformance"
        if not conformance.is_file():
            raise SystemExit(f"installed conformance runner not found: {conformance}")

    def stream(self, commands: list[str]) -> list[dict[str, Any]]:
        completed = subprocess.run(
            [str(self.harness), "stream"], input="\n".join(commands) + "\n",
            text=True, capture_output=True, check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"stream failed: {completed.stderr.strip()}")
        events = []
        for line in completed.stdout.splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise RuntimeError("non-object event from harness")
            events.append(event)
        return events

    def control(self, name: str) -> dict[str, Any]:
        completed = subprocess.run(
            [str(self.harness), "control", name], text=True, capture_output=True, check=False,
        )
        if completed.returncode != 0 or len(completed.stdout.splitlines()) != 1:
            raise RuntimeError(f"control {name} failed: {completed.stderr.strip()}")
        return json.loads(completed.stdout)

    def conformance(self, scratch: pathlib.Path) -> dict[str, Any]:
        report_path = scratch / "conformance.json"
        completed = subprocess.run(
            [str(self.prefix / "bin/audio_sdk_conformance"), "--provider", PROVIDER_ID,
             "--report", str(report_path)], text=True, capture_output=True, check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"installed conformance failed: {completed.stderr.strip()}")
        return json.loads(report_path.read_text(encoding="utf-8"))


def compact_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep metadata and drop bulk PCM; flattened output is stored once."""
    return [{key: value for key, value in event.items()
             if key not in {"samples", "sample"}} for event in events]


def frames_of(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in events if "samples" in event and event.get("status") == 0]


def samples_of(events: list[dict[str, Any]]) -> list[float]:
    output: list[float] = []
    for event in frames_of(events):
        output.extend(float(value) for value in event["samples"])
    return output


def build_report(prefix: pathlib.Path, harness: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    stimuli_bytes = STIMULI_PATH.read_bytes()
    stimuli = json.loads(stimuli_bytes)
    stimuli_digest = digest(stimuli_bytes)
    pins: dict[str, Any] = {}
    for label, (path, expected, summary) in SOURCE_PINS.items():
        actual = digest(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"source pin mismatch for {label}: {actual}")
        pins[label] = {"sha256": actual, "summary": summary}
    verification_digest = digest(VERIFICATION_PATH.read_bytes())
    task_profile_digest = digest(TASKS_PATH.read_bytes())

    runner = InstalledRunner(prefix, harness)
    rate = int(stimuli["fixed_v0"]["sample_rate_hz"])
    frame_samples = int(stimuli["fixed_v0"]["frame_samples"])
    coeffs = design(stimuli)
    tolerance = stimuli["tolerances"]
    capture: dict[str, Any] = {
        "schema": "sdk.highpass80.installed-capture/0.1",
        "protocol": PROTOCOL,
        "stimuli_sha256": stimuli_digest,
        "scenarios": {},
        "controls": {},
    }
    checks: list[dict[str, Any]] = []
    measurements: dict[str, Any] = {}
    scenario_count = 0
    frame_count = 0
    sample_count = 0

    def check(check_id: str, ok: bool, expected: Any, observed: Any) -> None:
        checks.append({"id": check_id, "status": "pass" if ok else "fail",
                       "expected": expected, "observed": observed})

    def scenario(name: str, commands: list[str], signal: list[float],
                 reference: list[float] | None = None) -> tuple[list[dict[str, Any]], list[float]]:
        nonlocal scenario_count, frame_count, sample_count
        events = runner.stream(commands)
        output = samples_of(events)
        if reference is None:
            reference = reference_filter(signal, coeffs)
        capture["scenarios"][name] = {
            "events": compact_events(events),
            "output_samples": output,
        }
        scenario_count += 1
        frame_count += len(frames_of(events))
        sample_count += len(output)
        error = max_abs_error(output, [f32(value) for value in reference])
        check(f"{name}.reference_match", error <= 2e-5, "<=2e-5 max abs error", error)
        check(f"{name}.alignment",
              all(frame["result"]["source_first"] == frame["first"]
                  and frame["result"]["consumed"] == frame_samples
                  and frame["result"]["produced"] == frame_samples
                  for frame in frames_of(events)),
              "source_first equals submitted first; consumed=produced=160",
              [frame["result"]["source_first"] for frame in frames_of(events)])
        check(f"{name}.finite", all(math.isfinite(value) for value in output),
              "all output finite", all(math.isfinite(value) for value in output))
        return events, output

    # Steady-state tone sweep: measured gain against the analytic pinned design.
    tone_config = stimuli["tones"]
    rate_hz = rate
    settle = int(tone_config["settle_samples"])
    tones: dict[str, Any] = {}
    for frequency in tone_config["frequencies_hz"]:
        signal = sine(float(frequency), float(tone_config["amplitude"]),
                      int(tone_config["frames"]) * frame_samples, rate_hz)
        name = f"tone_{frequency}hz"
        _, output = scenario(name, ["create 1 0 2"] + frame_lines(signal) + ["drain", "close"], signal)
        gain = rms(output[settle:]) / rms([f32(value) for value in signal[settle:]])
        expected = magnitude_response(float(frequency), stimuli, coeffs)
        tones[str(frequency)] = {
            "measured_gain": gain,
            "analytic_gain": expected,
            "gain_error": gain - expected,
            "peak": max(abs(value) for value in output),
        }
        check(f"{name}.gain", abs(gain - expected) <= float(tolerance["gain_abs"]),
              f"analytic gain {expected:.6f} +/- {tolerance['gain_abs']}", gain)
    measurements["tone_sweep"] = tones
    check("tone_sweep.coverage", len(tones) == len(tone_config["frequencies_hz"]),
          len(tone_config["frequencies_hz"]), len(tones))
    check("tone_sweep.cutoff_minus_3db",
          abs(tones["80"]["analytic_gain"] - 2 ** -0.5) < 1e-3,
          "-3 dB at 80 Hz", tones["80"]["analytic_gain"])
    check("tone_sweep.no_resonant_peaking",
          all(row["analytic_gain"] <= 1.0 + 1e-6 and row["peak"] <= float(tolerance["peak_headroom"])
              for row in tones.values()),
          "all gains <= 1; all peaks <= 1+1e-6",
          max(row["peak"] for row in tones.values()))

    # Log chirp across the same fixed-rate band.
    chirp_signal = chirp_values(stimuli["chirp"], rate)
    scenario("chirp", ["create 1 0 2"] + frame_lines(chirp_signal) + ["drain", "close"], chirp_signal)
    measurements["chirp"] = {
        "start_hz": stimuli["chirp"]["start_hz"],
        "end_hz": stimuli["chirp"]["end_hz"],
        "samples": len(chirp_signal),
        "peak": max(abs(value) for value in capture["scenarios"]["chirp"]["output_samples"]),
    }

    # Positive and negative steps: DC rejection and no added delay.
    step_config = stimuli["step"]
    steps: dict[str, Any] = {}
    for amplitude in step_config["amplitudes"]:
        signal = [0.0] * (int(step_config["pre_frames"]) * frame_samples) + [
            float(amplitude)
        ] * (int(step_config["frames"]) * frame_samples)
        name = f"step_{'pos' if amplitude > 0 else 'neg'}"
        _, output = scenario(name, ["create 1 0 2"] + frame_lines(signal) + ["drain", "close"], signal)
        settled = mean_abs(output[-32:])
        steps[name] = {"amplitude": amplitude, "settled_mean_abs_last_32": settled,
                       "first_response": output[int(step_config["pre_frames"]) * frame_samples]}
        check(f"{name}.dc_rejection", settled <= float(tolerance["dc_final_abs"]),
              f"<= {tolerance['dc_final_abs']}", settled)
    measurements["steps"] = steps

    # Impulse: content delay and first-sample response.
    impulse_config = stimuli["impulse"]
    impulse_signal = [0.0] * (int(impulse_config["frames"]) * frame_samples)
    impulse_signal[int(impulse_config["position"])] = float(impulse_config["amplitude"])
    _, impulse_output = scenario(
        "impulse", ["create 1 0 2"] + frame_lines(impulse_signal) + ["drain", "close"],
        impulse_signal,
    )
    peak_index = max(range(len(impulse_output)), key=lambda index: abs(impulse_output[index]))
    expected_first = coeffs[0] * float(impulse_config["amplitude"])
    measurements["impulse"] = {
        "peak_index": peak_index,
        "measured_content_delay_samples": peak_index,
        "first_sample": impulse_output[0],
        "analytic_first_sample": expected_first,
    }
    check("impulse.zero_content_delay", peak_index == 0, 0, peak_index)
    check("impulse.first_sample", abs(impulse_output[0] - expected_first) <= 2e-5,
          expected_first, impulse_output[0])

    # Silence and constant DC.
    silence_signal = [0.0] * (int(stimuli["silence_frames"]) * frame_samples)
    _, silence_output = scenario(
        "silence", ["create 1 0 2"] + frame_lines(silence_signal) + ["drain", "close"],
        silence_signal,
    )
    check("silence.exact_zero", all(value == 0.0 for value in silence_output),
          "all exact +0.0/-0.0", sum(1 for value in silence_output if value != 0.0))
    dc_config = stimuli["dc"]
    dc_signal = [float(dc_config["amplitude"])] * (int(dc_config["frames"]) * frame_samples)
    _, dc_output = scenario("dc", ["create 1 0 2"] + frame_lines(dc_signal) + ["drain", "close"], dc_signal)
    measurements["dc"] = {
        "amplitude": dc_config["amplitude"],
        "settled_mean_abs_last_32": mean_abs(dc_output[-32:]),
        "peak": max(abs(value) for value in dc_output),
    }
    check("dc.rejection", measurements["dc"]["settled_mean_abs_last_32"] <= float(tolerance["dc_final_abs"]),
          f"<= {tolerance['dc_final_abs']}", measurements["dc"]["settled_mean_abs_last_32"])

    # Synthetic speech-like harmonic signal: band preservation, not STOI.
    speech_signal = speech_values(stimuli["speech"], rate)
    _, speech_output = scenario(
        "speech", ["create 1 0 2"] + frame_lines(speech_signal) + ["drain", "close"],
        speech_signal,
    )
    speech_reference = [f32(value) for value in reference_filter(speech_signal, coeffs)]
    input_band = band_power([f32(value) for value in speech_signal], 300, 3400, rate)
    output_band = band_power(speech_output, 300, 3400, rate)
    reference_band = band_power(speech_reference, 300, 3400, rate)
    speech_band_gain = 10.0 * math.log10(output_band / input_band)
    reference_band_gain = 10.0 * math.log10(reference_band / input_band)
    envelope = envelope_correlation(speech_signal, speech_output)
    measurements["speech_proxy"] = {
        "kind": "synthetic_harmonic_formant_proxy",
        "speech_band_gain_db": speech_band_gain,
        "analytic_band_gain_db": reference_band_gain,
        "envelope_correlation": envelope,
        "not_stoi_or_real_speech": True,
    }
    check("speech.band_preservation", abs(speech_band_gain - reference_band_gain) <=
          float(tolerance["speech_band_loss_db"]), reference_band_gain, speech_band_gain)
    check("speech.envelope_control", envelope >= float(tolerance["envelope_correlation_min"]),
          f">= {tolerance['envelope_correlation_min']}", envelope)

    # Rumble + speech: low-frequency attenuation and speech-band preservation.
    rumble_config = stimuli["rumble"]
    rumble = sine(float(rumble_config["frequency_hz"]), float(rumble_config["amplitude"]),
                  len(speech_signal), rate, float(rumble_config["phase_rad"]))
    mixture = [left + right for left, right in zip(speech_signal, rumble)]
    _, mixture_output = scenario(
        "speech_plus_rumble", ["create 1 0 2"] + frame_lines(mixture) + ["drain", "close"],
        mixture,
    )
    rumble_hz = float(rumble_config["frequency_hz"])
    input_tone_power = goertzel_power([f32(value) for value in rumble], rumble_hz, rate)
    output_tone_power = goertzel_power(mixture_output, rumble_hz, rate)
    attenuation_db = -10.0 * math.log10(output_tone_power / input_tone_power)
    expected_attenuation_db = -20.0 * math.log10(magnitude_response(rumble_hz, stimuli, coeffs))
    rumble_reference = [f32(value) for value in reference_filter(rumble, coeffs)]
    speech_component = [output - low for output, low in zip(mixture_output, rumble_reference)]
    mix_in_band = band_power([f32(value) for value in speech_signal], 300, 3400, rate)
    mix_out_band = band_power(speech_component, 300, 3400, rate)
    mix_band_db = 10.0 * math.log10(mix_out_band / mix_in_band)
    measurements["rumble_control"] = {
        "rumble_hz": rumble_hz,
        "rumble_attenuation_db": attenuation_db,
        "analytic_attenuation_db": expected_attenuation_db,
        "speech_band_gain_db": mix_band_db,
    }
    check("rumble.attenuation", attenuation_db >= float(tolerance["rumble_attenuation_db"]),
          f">= {tolerance['rumble_attenuation_db']} dB", attenuation_db)
    check("rumble.speech_band_preserved", abs(mix_band_db - reference_band_gain) <=
          float(tolerance["speech_band_loss_db"]), reference_band_gain, mix_band_db)

    # Full-scale headroom.
    full_config = stimuli["full_scale"]
    full_signal = sine(float(full_config["frequency_hz"]), float(full_config["amplitude"]),
                       int(full_config["frames"]) * frame_samples, rate)
    _, full_output = scenario(
        "full_scale", ["create 1 0 2"] + frame_lines(full_signal) + ["drain", "close"], full_signal,
    )
    startup_peak = max(abs(value) for value in full_output[:settle])
    full_peak = max(abs(value) for value in full_output[settle:])
    measurements["headroom"] = {
        "input_peak": 1.0,
        "startup_transient_peak": startup_peak,
        "steady_state_output_peak": full_peak,
        "ceiling": tolerance["peak_headroom"],
        "note": "finite startup overshoot is analytic filter transient, not clipping",
    }
    check("headroom.steady_state_no_gain_above_full_scale",
          full_peak <= float(tolerance["peak_headroom"]),
          f"<= {tolerance['peak_headroom']}", full_peak)
    check("headroom.startup_finite", math.isfinite(startup_peak), "finite", startup_peak)

    # Framing/epoch/reset/drain state transitions with a final partial frame.
    partial = stimuli["partial"]
    before = [0.1] * (int(partial["frames_before"]) * frame_samples)
    tail = [0.2] * int(partial["valid_count"])
    after = [-0.1] * (int(partial["frames_after"]) * frame_samples)
    commands = ["create 1 0 2"] + frame_lines(before)
    valid = len(tail)
    padded = tail + [0.0] * (frame_samples - valid)
    commands.append("frame %d 1 320 1 %s" % (valid, " ".join("%.9g" % value for value in padded)))
    commands.extend(["drain", "reset %d %d" % (int(partial["epoch"]), int(partial["first_input_sample"]))])
    commands.extend(frame_lines(after, epoch=int(partial["epoch"]),
                                first=int(partial["first_input_sample"])))
    commands.extend(["drain", "close"])
    partial_events = runner.stream(commands)
    partial_frames = frames_of(partial_events)
    partial_output = samples_of(partial_events)
    partial_reference = reference_filter(before + padded, coeffs) + reference_filter(after, coeffs)
    capture["scenarios"]["partial_reset_drain"] = {
        "events": compact_events(partial_events),
        "output_samples": partial_output,
    }
    scenario_count += 1
    frame_count += len(partial_frames)
    sample_count += len(partial_output)
    final_frame = [event for event in partial_frames if event.get("valid_input") == valid][0]
    reset_event = [event for event in partial_events if event.get("event") == "reset"][0]
    check("partial.valid_count", final_frame["result"]["valid_count"] == valid,
          valid, final_frame["result"]["valid_count"])
    check("partial.source_first", final_frame["result"]["source_first"] == 320,
          320, final_frame["result"]["source_first"])
    check("partial.reference_match", max_abs_error(partial_output, [f32(v) for v in partial_reference]) <= 2e-5,
          "<=2e-5 after reset", max_abs_error(partial_output, [f32(v) for v in partial_reference]))
    check("reset.status", reset_event["status_name"] == "ok", "ok", reset_event["status_name"])
    check("reset.epoch_and_origin",
          all(frame["result"]["epoch"] == int(partial["epoch"]) and
              frame["result"]["source_first"] >= int(partial["first_input_sample"])
              for frame in partial_frames[-int(partial["frames_after"]):]),
          f"epoch {partial['epoch']} and origin {partial['first_input_sample']}",
          [(frame["result"]["epoch"], frame["result"]["source_first"])
           for frame in partial_frames[-int(partial["frames_after"]):]])
    eos_events = [event for event in partial_events if event.get("status_name") == "end_of_stream"]
    check("drain.two_end_of_stream", len(eos_events) == 2 and
          all(event["result"]["produced"] == 0 for event in eos_events),
          "two EOS with zero produced", len(eos_events))
    stats_events = [json.loads(event["json"]) for event in partial_events
                    if isinstance(event.get("json"), str) and event["json"]]
    check("drain.stats_coverage", len(stats_events) == 2, 2, len(stats_events))
    first_stats, second_stats = (stats_events + [{}, {}])[:2]
    padding = int(first_stats.get("final_padding_samples", -1))
    delivered = int(first_stats.get("delivered_valid_samples", -1))
    accepted = int(first_stats.get("accepted_valid_samples", -1))
    check("partial.exact_padding_accounting",
          padding == frame_samples - valid and delivered == accepted == 357,
          {"final_padding_samples": frame_samples - valid, "accepted": 357, "delivered": 357},
          {"final_padding_samples": padding, "accepted": accepted, "delivered": delivered})
    check("reset.clean_second_drain",
          int(second_stats.get("final_padding_samples", -1)) == 0 and
          int(second_stats.get("accepted_valid_samples", -1)) ==
          int(second_stats.get("delivered_valid_samples", -1)) == 320,
          {"final_padding_samples": 0, "accepted": 320, "delivered": 320},
          {key: second_stats.get(key) for key in
           ("final_padding_samples", "accepted_valid_samples", "delivered_valid_samples")})
    measurements["state_transitions"] = {
        "final_partial_valid_count": final_frame["result"]["valid_count"],
        "final_partial_source_first": final_frame["result"]["source_first"],
        "reset_status": reset_event["status_name"],
        "end_of_stream_events": len(eos_events),
        "partial_epoch_stats": first_stats,
        "post_reset_epoch_stats": second_stats,
    }

    # Two independent sessions in one registry, same stimulus, distinct coordinates.
    dual_config = stimuli["dual"]
    dual_events = runner.stream(["create 1 0 2",
                                 "dual %d" % int(dual_config["frames"]), "close"])
    dual_frames = [event for event in dual_events if event.get("event") == "dual"]
    session_zero = [value for event in dual_frames if event["session"] == 0
                    for value in event["sample"]]
    session_one = [value for event in dual_frames if event["session"] == 1
                    for value in event["sample"]]
    capture["scenarios"]["independent_sessions"] = {
        "events": compact_events(dual_events),
        "session_0_samples": session_zero,
        "session_1_samples": session_one,
    }
    scenario_count += 1
    frame_count += len(dual_frames)
    sample_count += len(session_zero) + len(session_one)
    first_tone_events = runner.stream([
        "create 1 0 2",
        *frame_lines(sine(float(dual_config["frequency_hz"]), float(dual_config["amplitude"]),
                          int(dual_config["frames"]) * frame_samples, rate)),
        "drain", "close",
    ])
    standalone = samples_of(first_tone_events)
    check("dual.same_transformation", session_zero == standalone and session_one == standalone,
          "both sessions identical to standalone tone", session_zero == standalone and session_one == standalone)
    check("dual.distinct_coordinates",
          all(event["result"]["epoch"] == 1 for event in dual_frames if event["session"] == 0) and
          all(event["result"]["epoch"] == 9 for event in dual_frames if event["session"] == 1),
          "epochs 1 and 9", sorted({event["result"]["epoch"] for event in dual_frames}))
    measurements["independent_sessions"] = {
        "frames_per_session": int(dual_config["frames"]),
        "samples_compared": len(standalone),
        "bit_identical_to_standalone": session_zero == standalone and session_one == standalone,
    }

    # Unpaced single-stream load control; raw timing stays out of canonical files.
    load_events = runner.stream(["create 1 0 2",
                                 "load %d" % int(stimuli["load"]["frames"]), "close"])
    load_event = [event for event in load_events if event.get("event") == "load"][0]
    expected_finite = int(stimuli["load"]["frames"]) * frame_samples
    check("load.all_finite", load_event["finite"] == expected_finite,
          expected_finite, load_event["finite"])
    check("load.below_realtime", load_event["rtf"] < 1.0, "<1 unpaced RTF", load_event["rtf"] < 1.0)
    capture["scenarios"]["load_control"] = {
        "frames": load_event["frames"],
        "finite": load_event["finite"],
        "peak": load_event["peak"],
        "rtf_below_one": load_event["rtf"] < 1.0,
    }
    scenario_count += 1
    frame_count += int(load_event["frames"])
    sample_count += expected_finite
    measurements["load_control"] = {
        "frames": load_event["frames"],
        "finite": load_event["finite"],
        "peak": load_event["peak"],
        "rtf_below_one": load_event["rtf"] < 1.0,
        "raw_timing_excluded_from_digest": True,
    }

    # Invalid, missing and nonfinite controls.
    control_rows: dict[str, Any] = {}
    for name, expected in CONTROL_EXPECTED.items():
        observed = runner.control(name)
        capture["controls"][name] = observed
        normalized = dict(observed)
        normalized["status"] = observed.get("status_name")
        normalized["field"] = observed.get("detail")
        row = {"expected": expected,
               "observed": {key: normalized.get(key) for key in expected},
               "status": "pass"}
        for key, value in expected.items():
            if normalized.get(key) != value:
                row["status"] = "fail"
        if name in {"nonfinite_nan", "nonfinite_inf"}:
            finite = all(isinstance(value, (int, float)) and math.isfinite(value)
                         for value in observed["samples"])
            row["all_output_finite"] = finite
            if not finite:
                row["status"] = "fail"
        if name == "recover_after_bad_position":
            first = observed["samples"][0]
            expected_first = coeffs[0] * 0.25
            row["first_sample_after_reset"] = first
            if abs(first - expected_first) > 2e-5:
                row["status"] = "fail"
        control_rows[name] = row
        check(f"control.{name}", row["status"] == "pass", expected, row["observed"])
    measurements["controls"] = {
        "count": len(control_rows),
        "passed": sum(row["status"] == "pass" for row in control_rows.values()),
        "rows": control_rows,
    }

    with tempfile.TemporaryDirectory(prefix="sdk-highpass-evidence-") as scratch:
        conformance = runner.conformance(pathlib.Path(scratch))
    installed = {
        "provider_id": PROVIDER_ID,
        "build_id": conformance["build_id"],
        "descriptor_digest": conformance["descriptor_digest"],
        "conformance_result": conformance["result"],
        "conformance_checks": len(conformance["checks"]),
        "conformance_checks_passed": sum(check_row["result"] == "pass"
                                         for check_row in conformance["checks"]),
    }
    check("installed.conformance",
          installed["conformance_result"] == "pass" and
          installed["conformance_checks_passed"] == installed["conformance_checks"],
          "pass, all checks", installed)

    adverse = [
        "Nonfinite NaN/inf input is rejected with invalid_argument; no nonfinite DSP output is qualified.",
        "Null or undersized process/drain arguments and unsupported create configs fail closed.",
        "Non-contiguous source position is invalid_argument and leaves the session not_ready until reset.",
        "Load control is unpaced single-stream compute only; no deadline, availability, queue or device claim.",
        "Synthetic harmonic speech proxy is not STOI, human listening, real speech or a corpus result.",
        "Fixed 80 Hz / 16 kHz only; no alternate cutoff, sample rate or frame size is qualified.",
        "No clipping, limiter or VAD exists in this provider; nonlinear interaction evidence is limited to framing/epoch/reset/drain.",
    ]
    report: dict[str, Any] = {
        "protocol": PROTOCOL,
        "task_id": TASK_ID,
        "mode": "reference-verification",
        "acceptance_profile": "DSP",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "provider_id": PROVIDER_ID,
        "fixed_v0": stimuli["fixed_v0"],
        "source_pins": pins,
        "verification_profile_sha256": verification_digest,
        "task_profile_sha256": task_profile_digest,
        "stimuli_sha256": stimuli_digest,
        "installed_capture_sha256": digest(canonical_bytes(capture)),
        "installed": installed,
        "measurements": measurements,
        "controls": control_rows,
        "adverse_cases": adverse,
        "checks": checks,
        "counts": {
            "scenarios": scenario_count,
            "frames": frame_count,
            "samples": sample_count,
            "controls": len(control_rows),
            "checks": len(checks),
            "checks_passed": sum(row["status"] == "pass" for row in checks),
            "checks_failed": sum(row["status"] == "fail" for row in checks),
        },
        "limitations": [
            "Synthetic, asset-free control for an already installed fixed-rate provider.",
            "No audio-bench bundle, listening result, corpus score or production workload qualification.",
            "No public API, descriptor, registry, default provider or installed behavior change.",
        ],
    }
    return report, capture


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True, type=pathlib.Path,
                        help="installed audio-sdk prefix built from the pinned base")
    parser.add_argument("--harness", required=True, type=pathlib.Path,
                        help="compiled task-local harness binary")
    parser.add_argument("--output", type=pathlib.Path, default=HERE / "report.json")
    parser.add_argument("--capture-output", type=pathlib.Path,
                        default=HERE / "installed-capture.json")
    options = parser.parse_args()
    report, capture = build_report(options.prefix.resolve(), options.harness.resolve())
    report_digest = write_canonical(options.output, report)
    capture_digest = write_canonical(options.capture_output, capture)
    if capture_digest != report["installed_capture_sha256"]:
        raise SystemExit("capture digest disagrees with report")
    print(json.dumps({
        "report": str(options.output),
        "report_sha256": report_digest,
        "capture": str(options.capture_output),
        "capture_sha256": capture_digest,
        "counts": report["counts"],
        "build_id": report["installed"]["build_id"],
    }, sort_keys=True))
    return 0 if report["counts"]["checks_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
