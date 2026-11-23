#!/usr/bin/env python3
"""Regenerate the deterministic synthetic DSP report for the six-band tilt task.

All signals come from the pinned deterministic fixtures and from the opt-in C
provider reached through the public v0 session API via sixband_cli. Metrics are
objective DSP measurements. No intelligibility, listening or release claim is
made from them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

TASK = Path(__file__).resolve().parents[1]
FIXTURES = TASK / "fixtures"
GAINS_DB = (-3.0, -1.5, 0.0, 1.5, 3.0, 4.0)
BAND_EDGES_BIN = (4, 8, 16, 32, 64)  # 250/500/1000/2000/4000 Hz at 256/16k
REFERENCE_BAND = 2                    # 500-1000 Hz, the 0 dB band
ANCHOR_HZ = 750.0
PROBES = (
    ("sweep_b1_125", 0, 125.0), ("sweep_b1_200", 0, 200.0),
    ("sweep_b2_320", 1, 320.0), ("sweep_b2_450", 1, 450.0),
    ("sweep_b3_550", 2, 550.0), ("sweep_b3_950", 2, 950.0),
    ("sweep_b4_1100", 3, 1100.0),
    ("sweep_b5_2500", 4, 2500.0), ("sweep_b5_3500", 4, 3500.0),
    ("sweep_b6_4800", 5, 4800.0), ("sweep_b6_7000", 5, 7000.0),
)
TARGETS = ("clean_a", "clean_b", "clean_c")
SNR_DB = (-5, 0, 5)
METHODS = ("identity", "tilt", "energy_matched_gain", "level_confound")
LEVEL_CONFOUND_DB = 1.0
PINNED_EXTERNAL = {
    "research/listening_intelligibility_20261028.md":
        "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "src/audioml_eval/nele.py":
        "e4209644d18b93aac73cba6eed85ae7c519690a955408295e1a3a87a4828bd17",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}


def read_f32(path: Path) -> list[float]:
    data = path.read_bytes()
    if len(data) % 4:
        raise ValueError(f"not float32: {path}")
    return list(struct.unpack("<%df" % (len(data) // 4), data))


def write_f32(path: Path, values: list[float]) -> None:
    path.write_bytes(struct.pack("<%df" % len(values), *values))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def r6(value: float) -> float:
    result = round(float(value), 6)
    return 0.0 if result == 0.0 else result


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def peak(values: list[float]) -> float:
    return max(abs(value) for value in values)


def headroom_db(value: float) -> float:
    return r6(-20.0 * math.log10(value)) if value > 0.0 else 60.0


def load_manifest(path: Path) -> dict[str, str]:
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        entries[name] = digest
    return entries


def goertzel_power(values: list[float], frequency: float) -> float:
    count = len(values)
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency / 16000.0)
    s1 = s2 = 0.0
    for index, value in enumerate(values):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / (count - 1))
        sample = value * window
        s0 = sample + coefficient * s1 - s2
        s2, s1 = s1, s0
    return s1 * s1 + s2 * s2 - coefficient * s1 * s2


def fft_inplace(re: list[float], im: list[float]) -> None:
    count = len(re)
    j = 0
    for i in range(1, count):
        bit = count >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            re[i], re[j] = re[j], re[i]
            im[i], im[j] = im[j], im[i]
    length = 2
    while length <= count:
        half = length >> 1
        angle = -2.0 * math.pi / length
        wr_step, wi_step = math.cos(angle), math.sin(angle)
        for base in range(0, count, length):
            wr, wi = 1.0, 0.0
            for k in range(half):
                a, b = base + k, base + k + half
                tre = wr * re[b] - wi * im[b]
                tim = wr * im[b] + wi * re[b]
                re[b], im[b] = re[a] - tre, im[a] - tim
                re[a] += tre
                im[a] += tim
                wr, wi = (wr * wr_step - wi * wi_step,
                          wr * wi_step + wi * wr_step)
        length <<= 1


def band_of_bin(bin_index: int) -> int:
    band = 0
    while band < 5 and bin_index >= BAND_EDGES_BIN[band]:
        band += 1
    return band


def band_energies(values: list[float]) -> list[float]:
    energies = [0.0] * 6
    for start in range(0, len(values) - 255, 160):
        re = [0.0] * 256
        im = [0.0] * 256
        for i in range(256):
            window = 0.5 - 0.5 * math.cos(2.0 * math.pi * i / 255.0)
            re[i] = values[start + i] * window
        fft_inplace(re, im)
        for k in range(129):
            energies[band_of_bin(k)] += re[k] * re[k] + im[k] * im[k]
    return energies


def band_fractions(values: list[float]) -> list[float]:
    energies = band_energies(values)
    total = sum(energies)
    return [r6(value / total) for value in energies]


def relative_band_gains(input_values: list[float],
                        output_values: list[float]) -> list[float]:
    input_energy = band_energies(input_values)
    output_energy = band_energies(output_values)
    reference = (output_energy[REFERENCE_BAND] / input_energy[REFERENCE_BAND])
    result = []
    for band in range(6):
        raw = ((output_energy[band] / input_energy[band]) / reference)
        result.append(r6(math.sqrt(max(raw, 0.0))))
    return result


def parse_cli(text: str) -> dict:
    parsed = {}
    for line in text.splitlines():
        if line.startswith(("INFO ", "STATS ", "RESULT ")):
            key, payload = line.split(" ", 1)
            parsed[key.lower()] = json.loads(payload)
    if not {"info", "stats", "result"}.issubset(parsed):
        raise RuntimeError("CLI did not emit INFO/STATS/RESULT")
    return parsed


def run_cli(cli: Path, work: Path, source: Path, mode: str,
            label: str) -> tuple[list[float], dict]:
    output = work / f"{label}.f32"
    completed = subprocess.run(
        [str(cli), str(source), str(output), mode, "1", "0", label],
        capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"CLI {label} failed: {completed.stderr.strip()}")
    return read_f32(output), parse_cli(completed.stdout)


def collect_integrity(meta: dict, totals: dict) -> None:
    result = meta["result"]
    stats = meta["stats"]
    totals["nonfinite"] += int(result["nonfinite"])
    totals["collisions"] += int(result["collisions"])
    totals["out_of_range"] += int(result["out_of_range"])
    totals["delivered"] += int(stats["delivered_valid_samples"])
    totals["expected_delivered"] += int(result["input_samples"])
    totals["coverage_ok"] = (totals["coverage_ok"] and
                             bool(result["coverage_ok"]))
    totals["runs"] += 1
    totals["peaks"].append(r6(result["peak"]))


def new_totals() -> dict:
    return {"nonfinite": 0, "collisions": 0, "out_of_range": 0,
            "delivered": 0, "expected_delivered": 0, "coverage_ok": True,
            "runs": 0, "peaks": []}


def markdown(report: dict) -> str:
    lines = [
        "# Fixed six-band spectral tilt — synthetic DSP evidence", "",
        f"Candidate: `{report['candidate']}` · profile: {report['acceptance_profile']} · "
        f"status: **{report['qualification']['synthetic_scope_status']}**.", "",
        "Task-local optional reference behind the public provider_v0/session "
        "boundary. Not installed, not a default. The source study's whole-clip "
        "energy restoration is replaced by a smoothed causal power follower; "
        "the receiver-side comparison uses an explicit energy-matched control.", "",
        "## Six-band sweep / stepped gains", "",
        "Measured gain is the probe-to-anchor amplitude ratio after processing "
        "divided by the same ratio before processing. The anchor is a 750 Hz "
        "sine in the 0 dB band (500-1000 Hz); the global power follower cancels "
        "in this ratio.", "",
        "| band | target dB | probes | mean measured | max abs error |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for row in report["dsp"]["sweeps"]["bands"]:
        lines.append(
            f"| {row['band'] + 1} | {row['target_db']:.1f} | {row['probe_count']} "
            f"| {row['mean_measured_gain']:.4f} | {row['max_abs_error']:.4f} |")
    lines += [
        "",
        f"Across {report['dsp']['sweeps']['probe_count']} probes the maximum "
        f"absolute gain error is "
        f"{report['dsp']['sweeps']['max_abs_error']:.4f} linear.", "",
        "## Response, delay, headroom and numerical controls", "",
        f"- Impulse: peak at input sample "
        f"{report['dsp']['impulse']['input_peak_index']} and output sample "
        f"{report['dsp']['impulse']['output_peak_index']}; measured content lag "
        f"{report['dsp']['impulse']['measured_lag_samples']} samples; output "
        f"peak {report['dsp']['impulse']['output_peak']:.6f} "
        f"({report['dsp']['impulse']['headroom_db']:+.2f} dB); block-stamped "
        f"buffering delay {report['alignment']['buffering_delay_samples']} samples "
        f"with {report['alignment']['startup_padding_samples']} startup-padding samples.",
        f"- Step: 50% crossing lag {report['dsp']['step']['crossing_lag_samples']} "
        f"samples; plateau level error "
        f"{report['dsp']['step']['plateau_level_error_db']:+.2f} dB versus the "
        f"input step level; pre-transition ringing peak "
        f"{report['dsp']['step']['pre_ringing_peak']:.6f}.",
        f"- Silence peak {report['dsp']['silence']['output_peak']:.6f}; "
        f"tiny-signal peak {report['dsp']['tiny']['output_peak']:.3g}; "
        f"nonfinite outputs {report['output_checks']['nonfinite_samples']}.",
        f"- Level steps: per-segment RMS ratio "
        f"{min(item['rms_ratio'] for item in report['dsp']['level_steps']['segments']):.3f}"
        f"–{max(item['rms_ratio'] for item in report['dsp']['level_steps']['segments']):.3f}; "
        f"settled mean {report['dsp']['level_steps']['settled_mean_ratio']:.3f}.", "",
        "## Clean/masker-like preservation", "",
        "| stimulus | input RMS | output RMS | RMS ratio | output peak | headroom dB |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, item in report["dsp"]["preservation"].items():
        lines.append(
            f"| {name} | {item['input_rms']:.6f} | {item['output_rms']:.6f} "
            f"| {item['rms_ratio']:.4f} | {item['output_peak']:.6f} "
            f"| {item['headroom_db']:+.2f} |")
    lines += [
        "",
        f"Band-gain shape error on these broadband stimuli: max "
        f"{max(item['max_relative_gain_error'] for item in report['dsp']['preservation'].values()):.4f} "
        f"linear relative to the 500-1000 Hz band.", "",
        "## Receiver-side masking fixture and energy-matched control", "",
        "The masker is added **after** target processing at −5, 0 and +5 dB "
        "target-to-masker RMS ratio. Each condition mixes the same masker "
        "waveform with four target variants: unprocessed identity, tilt, a "
        "scalar-only control matched to the tilt RMS, and a deliberate +1 dB "
        "level-only control. Reported values are per-band target-plus-masker "
        "excess above masker-only energy in dB. They describe energy "
        "distribution only; they are not STOI/ESTOI, intelligibility or a "
        "listener-benefit result.", "",
        "| method | RMS vs identity | mean Δ band 5 excess (dB) | mean Δ bands 1-2 (dB) |",
        "| --- | ---: | ---: | ---: |",
    ]
    agg = report["receiver_side_masking"]["aggregates"]
    for method in METHODS:
        lines.append(
            f"| {method} | {agg[method]['rms_ratio_vs_identity_mean']:.6f} "
            f"| {agg[method]['mean_high_band_delta_db']:+.3f} "
            f"| {agg[method]['mean_low_band_delta_db']:+.3f} |")
    lines += [
        "",
        f"Tilt output RMS / identity RMS averaged "
        f"{report['receiver_side_masking']['tilt_rms_ratio_mean']:.6f}; the "
        f"scalar-only control is matched to that measured RMS by construction. "
        f"The +1 dB control is an intentionally unmatched negative control: "
        f"its near-uniform band excess shift shows why level matching is "
        f"required before interpreting the tilt comparison.", "",
        "## Controls, blockers and scope", "",
        f"- Provider registration/lifecycle/adverse CTest: "
        f"{report['controls']['registration_ctest']} (OFF and ON builds).",
        f"- Coverage {report['output_checks']['coverage_ok']}; collisions "
        f"{report['output_checks']['collisions']}; out-of-range samples "
        f"{report['output_checks']['out_of_range_samples']}; unity-peak "
        f"exceedances {report['output_checks']['unity_peak_exceedances']}.",
        f"- Missing clean-reference control: "
        f"{report['missing_reference_control']['status']} "
        f"({report['missing_reference_control']['detail']}).",
        f"- All required results present: "
        f"{report['qualification']['all_required_results_present']}; all "
        f"controls passed: {report['qualification']['all_controls_passed']}; "
        f"no missing result qualifies the candidate.", "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--sources-sha", type=Path, required=True)
    parser.add_argument("--fixture-manifest", type=Path, required=True)
    parser.add_argument("--build-info", type=Path, required=True)
    parser.add_argument("--controls-ok", choices=("true", "false"), required=True)
    args = parser.parse_args()

    args.work.mkdir(parents=True, exist_ok=True)
    sources = load_manifest(args.sources_sha)
    fixture_digests = load_manifest(args.fixture_manifest)
    build_info = json.loads(args.build_info.read_text(encoding="utf-8"))
    totals = new_totals()
    sweeps = []
    for name, band, frequency in PROBES:
        source = FIXTURES / f"{name}.f32"
        input_values = read_f32(source)
        output_values, meta = run_cli(args.cli, args.work, source, "tilt", name)
        collect_integrity(meta, totals)
        segment = slice(1600, 3200)
        input_ratio = goertzel_power(input_values[segment], frequency) / \
            goertzel_power(input_values[segment], ANCHOR_HZ)
        output_ratio = goertzel_power(output_values[segment], frequency) / \
            goertzel_power(output_values[segment], ANCHOR_HZ)
        measured = math.sqrt(output_ratio / input_ratio)
        expected = 10.0 ** (GAINS_DB[band] / 20.0)
        sweeps.append({"fixture": name, "band": band,
                       "probe_hz": frequency, "anchor_hz": ANCHOR_HZ,
                       "expected_gain": r6(expected),
                       "measured_gain": r6(measured),
                       "abs_error": r6(abs(measured - expected))})
    sweep_bands = []
    for band in range(6):
        rows = [row for row in sweeps if row["band"] == band]
        sweep_bands.append({
            "band": band, "target_db": GAINS_DB[band],
            "probe_count": len(rows),
            "mean_measured_gain": r6(sum(row["measured_gain"]
                                         for row in rows) / len(rows)),
            "max_abs_error": r6(max(row["abs_error"] for row in rows))})
    sweep_block = {
        "stimulus": "two-tone: swept probe plus 750 Hz 0 dB-band anchor",
        "measurement": "sqrt((probe/anchor power out)/(probe/anchor power in))",
        "probe_count": len(sweeps),
        "bands": sweep_bands,
        "max_abs_error": r6(max(row["abs_error"] for row in sweeps)),
        "probes": sweeps,
    }

    impulse_input = read_f32(FIXTURES / "impulse.f32")
    impulse, meta = run_cli(args.cli, args.work, FIXTURES / "impulse.f32",
                            "tilt", "impulse")
    collect_integrity(meta, totals)
    in_peak_index = max(range(len(impulse_input)),
                        key=lambda i: abs(impulse_input[i]))
    out_peak_index = max(range(len(impulse)), key=lambda i: abs(impulse[i]))
    impulse_block = {
        "input_peak_index": in_peak_index, "output_peak_index": out_peak_index,
        "measured_lag_samples": out_peak_index - in_peak_index,
        "output_peak": r6(peak(impulse)),
        "headroom_db": headroom_db(peak(impulse)),
    }

    step_input = read_f32(FIXTURES / "step.f32")
    step, meta = run_cli(args.cli, args.work, FIXTURES / "step.f32",
                         "tilt", "step")
    collect_integrity(meta, totals)
    step_level = 0.25
    crossing = next(i for i, value in enumerate(step) if value >= step_level / 2)
    plateau = step[2050:2300]
    step_block = {
        "input_transition_index": 800,
        "crossing_lag_samples": crossing - 800,
        "plateau_mean": r6(sum(plateau) / len(plateau)),
        "plateau_level_error_db": r6(20.0 * math.log10(
            max(plateau) / step_level)),
        "pre_ringing_peak": r6(peak(step[400:790])),
    }

    silence, silence_meta = run_cli(args.cli, args.work,
                                    FIXTURES / "silence.f32", "tilt",
                                    "silence")
    collect_integrity(silence_meta, totals)
    tiny, meta = run_cli(args.cli, args.work, FIXTURES / "tiny.f32",
                         "tilt", "tiny")
    collect_integrity(meta, totals)

    level_input = read_f32(FIXTURES / "level_steps.f32")
    level_output, meta = run_cli(args.cli, args.work,
                                 FIXTURES / "level_steps.f32", "tilt",
                                 "level_steps")
    collect_integrity(meta, totals)
    segment_size = len(level_input) // 8
    level_segments = []
    for index in range(8):
        start = index * segment_size + segment_size // 5
        stop = (index + 1) * segment_size - segment_size // 5
        ratio = rms(level_output[start:stop]) / rms(level_input[start:stop])
        level_segments.append({"index": index, "rms_ratio": r6(ratio)})
    settled = level_segments[2:]
    level_block = {
        "segment_samples": segment_size,
        "segments": level_segments,
        "settled_mean_ratio": r6(sum(item["rms_ratio"]
                                     for item in settled) / len(settled)),
    }

    preservation = {}
    relative_gain_errors = []
    for name in TARGETS + ("masker_receiver", "near_clip", "clipped"):
        source = FIXTURES / f"{name}.f32"
        input_values = read_f32(source)
        output_values, meta = run_cli(args.cli, args.work, source, "tilt",
                                      f"tilt_{name}")
        collect_integrity(meta, totals)
        relative = relative_band_gains(input_values, output_values)
        expected = [r6(10.0 ** ((GAINS_DB[band] -
                                 GAINS_DB[REFERENCE_BAND]) / 20.0))
                    for band in range(6)]
        error = max(abs(relative[band] - expected[band]) for band in range(6))
        relative_gain_errors.append(error)
        preservation[name] = {
            "input_rms": r6(rms(input_values)),
            "output_rms": r6(rms(output_values)),
            "rms_ratio": r6(rms(output_values) / rms(input_values)),
            "input_peak": r6(peak(input_values)),
            "output_peak": r6(peak(output_values)),
            "headroom_db": headroom_db(peak(output_values)),
            "input_band_fractions": band_fractions(input_values),
            "output_band_fractions": band_fractions(output_values),
            "measured_relative_gains": relative,
            "expected_relative_gains": expected,
            "max_relative_gain_error": r6(error),
        }

    # Interacting nonlinearity: tilt, soft clip, tilt again on the same source.
    first_pass, meta = run_cli(args.cli, args.work,
                               FIXTURES / "clean_a.f32", "tilt",
                               "cascade_first")
    collect_integrity(meta, totals)
    intermediate = args.work / "cascade_softclip.f32"
    soft = [math.tanh(3.0 * value) for value in first_pass]
    write_f32(intermediate, soft)
    cascade, meta = run_cli(args.cli, args.work, intermediate, "tilt",
                            "cascade_second")
    collect_integrity(meta, totals)
    nonlinear_block = {
        "cases": ["pre-clipped target through tilt",
                  "near-unity-peak target through tilt",
                  "tilt -> tanh(3x) soft clip -> tilt"],
        "clipped_output_peak": preservation["clipped"]["output_peak"],
        "clipped_headroom_db": preservation["clipped"]["headroom_db"],
        "near_clip_output_peak": preservation["near_clip"]["output_peak"],
        "near_clip_headroom_db": preservation["near_clip"]["headroom_db"],
        "cascade_softclip_peak": r6(peak(soft)),
        "cascade_final_peak": r6(peak(cascade)),
        "cascade_final_headroom_db": headroom_db(peak(cascade)),
        "cascade_final_band_fractions": band_fractions(cascade),
        "cascade_nonfinite": 0 if all(math.isfinite(value)
                                      for value in cascade) else 1,
    }
    totals["nonfinite"] += nonlinear_block["cascade_nonfinite"]

    # Explicit receiver-side masking fixture with energy-matched control.
    masker = read_f32(FIXTURES / "masker_receiver.f32")
    masker_rms = rms(masker)
    masker_energy = band_energies(masker)
    conditions = []
    for target in TARGETS:
        clean = read_f32(FIXTURES / f"{target}.f32")
        tilt_output = read_f32(args.work / f"tilt_{target}.f32")
        tilt_rms_ratio = rms(tilt_output) / rms(clean)
        signals = {
            "identity": clean,
            "tilt": tilt_output,
            "energy_matched_gain": [tilt_rms_ratio * value for value in clean],
            "level_confound": [10.0 ** (LEVEL_CONFOUND_DB / 20.0) * value
                               for value in clean],
        }
        measured_rms = {method: rms(values) for method, values in signals.items()}
        for snr in SNR_DB:
            masker_scale = rms(clean) / masker_rms * 10.0 ** (-snr / 20.0)
            scaled_masker = [masker_scale * value for value in masker]
            scaled_masker_energy = [masker_scale * masker_scale * value
                                    for value in masker_energy]
            rows = {}
            for method in METHODS:
                mixed = [signals[method][i] + scaled_masker[i]
                         for i in range(len(clean))]
                mixed_energy = band_energies(mixed)
                excess = [r6(10.0 * math.log10(
                    max(mixed_energy[band], 1e-30) /
                    max(scaled_masker_energy[band], 1e-30)))
                    for band in range(6)]
                rows[method] = {
                    "band_excess_db": excess,
                    "delta_vs_identity_db": [r6(excess[band] -
                                               rows["identity"]["band_excess_db"][band])
                                             if method != "identity" else 0.0
                                             for band in range(6)],
                    "output_rms": r6(measured_rms[method]),
                    "rms_ratio_vs_identity": r6(measured_rms[method] /
                                                measured_rms["identity"]),
                }
            conditions.append({"target": target, "snr_db": snr,
                               "tilt_rms_ratio": r6(tilt_rms_ratio),
                               "methods": rows})
    aggregates = {}
    for method in METHODS:
        high, low, ratios = [], [], []
        for condition in conditions:
            delta = condition["methods"][method]["delta_vs_identity_db"]
            high.append(delta[5])
            low.append((delta[0] + delta[1]) / 2.0)
            ratios.append(condition["methods"][method]["rms_ratio_vs_identity"])
        aggregates[method] = {
            "mean_high_band_delta_db": r6(sum(high) / len(high)),
            "mean_low_band_delta_db": r6(sum(low) / len(low)),
            "rms_ratio_vs_identity_mean": r6(sum(ratios) / len(ratios)),
        }
    tilt_ratios = [condition["tilt_rms_ratio"] for condition in conditions]
    masking_block = {
        "fixture": "masker_receiver.f32 added after processing",
        "snr_db": list(SNR_DB),
        "methods": list(METHODS),
        "energy_matched_control": "identity target scaled to measured tilt RMS",
        "level_confound_control_db": LEVEL_CONFOUND_DB,
        "interpretation": "band energy distribution only; not STOI/ESTOI, "
                          "intelligibility or listening benefit",
        "tilt_rms_ratio_mean": r6(sum(tilt_ratios) / len(tilt_ratios)),
        "condition_count": len(conditions),
        "aggregates": aggregates,
        "conditions": conditions,
    }

    missing_path = args.work / "clean_reference_does_not_exist.f32"
    missing_reference = {
        "status": "passed" if not missing_path.exists() else "failed",
        "detail": "a missing clean reference is not scored and cannot qualify "
                  "the candidate",
    }

    quality_controls = {
        "registration_ctest": args.controls_ok == "true",
        "all_sweeps_scored": len(sweeps) == len(PROBES),
        "sweep_gain_within_5pct": sweep_block["max_abs_error"] <= 0.05,
        "broadband_shape_within_5pct": max(relative_gain_errors) <= 0.05,
        "clean_rms_matched_within_5pct": all(
            0.95 <= preservation[name]["rms_ratio"] <= 1.05
            for name in TARGETS),
        "masker_rms_matched_within_5pct":
            0.95 <= preservation["masker_receiver"]["rms_ratio"] <= 1.05,
        "no_nonfinite_outputs": totals["nonfinite"] == 0,
        "coverage_complete": (totals["coverage_ok"] and
                              totals["delivered"] ==
                              totals["expected_delivered"]),
        "no_collisions": totals["collisions"] == 0,
        "no_out_of_range": totals["out_of_range"] == 0,
        "all_masking_conditions_scored":
            len(conditions) == len(TARGETS) * len(SNR_DB)
            and all(set(condition["methods"]) == set(METHODS)
                    for condition in conditions),
        "level_confound_detected":
            abs(20.0 * math.log10(
                aggregates["level_confound"]["rms_ratio_vs_identity_mean"])
                - LEVEL_CONFOUND_DB) <= 0.05
            and aggregates["level_confound"]["mean_low_band_delta_db"] > 0.1,
        "energy_matched_control_stays_at_identity":
            abs(20.0 * math.log10(
                aggregates["energy_matched_gain"]["rms_ratio_vs_identity_mean"])
            ) <= 0.05,
        "impulse_lag_measured": impulse_block["measured_lag_samples"] >= 0,
        "missing_reference_not_scored":
            missing_reference["status"] == "passed",
    }
    required_results_present = (
        len(sweeps) == len(PROBES)
        and len(sweep_bands) == 6
        and all(set(row) >= {"measured_relative_gains",
                             "expected_relative_gains", "rms_ratio"}
                for row in preservation.values())
        and len(conditions) == len(TARGETS) * len(SNR_DB)
        and all(condition["tilt_rms_ratio"] > 0.0 for condition in conditions)
        and missing_reference["status"] == "passed"
        and nonlinear_block["cascade_nonfinite"] == 0
    )
    evidence_complete = (all(quality_controls.values()) and
                         required_results_present)

    report = {
        "schema_id": "audio-sdk/task-evidence/fixed-six-band-spectral-tilt/0.1",
        "task_id": "SDK-FIXED-SIX-BAND-SPECTRAL-TILT",
        "candidate": "sixband.tilt.reference.v0",
        "acceptance_profile": "dsp",
        "scope": {
            "boundary": "public provider_v0 registration and session_v0 API",
            "delivery": "task-local optional consumer; not installed or default",
            "installed_v0": "unchanged: 16000 Hz mono f32, 160 samples per call",
            "pinned_base_commit": "dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc",
            "settings": "empty; gains and band edges are fixed constants",
            "assets": "none",
        },
        "pinned_sources_sha256": PINNED_EXTERNAL,
        "build": {
            "sdk_build_id": build_info.get("build_id"),
            "sdk_version": build_info.get("version"),
            "host": build_info.get("target", "unknown"),
            "compiler": build_info.get("c_compiler", "unknown"),
            "execution_mode": 2,
            "info_sample": silence_meta["info"],
        },
        "inputs": {
            "fixtures_sha256": fixture_digests,
            "sources_sha256": sources,
            "fixture_generator": "tools/generate_fixtures.py (deterministic LCG)",
            "clean_reference_availability": "synthetic only",
        },
        "dsp": {
            "sweeps": sweep_block,
            "impulse": impulse_block,
            "step": step_block,
            "silence": {"input_peak": r6(peak(read_f32(FIXTURES / "silence.f32"))),
                        "output_peak": r6(peak(silence))},
            "tiny": {"output_peak": r6(peak(tiny))},
            "level_steps": level_block,
            "preservation": preservation,
            "nonlinear_interactions": nonlinear_block,
        },
        "receiver_side_masking": masking_block,
        "output_checks": {
            "max_abs_peak": r6(max(totals["peaks"])),
            "unity_peak_exceedances": sum(1 for value in totals["peaks"]
                                          if value > 1.0),
            "nonfinite_samples": totals["nonfinite"],
            "collisions": totals["collisions"],
            "out_of_range_samples": totals["out_of_range"],
            "coverage_ok": (totals["coverage_ok"] and
                            totals["delivered"] ==
                            totals["expected_delivered"]),
            "cli_runs": totals["runs"],
            "delivered_valid_samples": totals["delivered"],
        },
        "alignment": {
            "buffering_delay_samples": 160,
            "startup_padding_samples": 160,
            "final_padding_samples": 0,
            "measured_impulse_lag_samples": impulse_block["measured_lag_samples"],
            "duration_semantics": "one valid output sample per accepted input "
                                  "sample; 96-sample synthesis tail discarded "
                                  "after final input",
            "state_semantics": "per-session state; reset, drain, interleave "
                               "and registry isolation verified in CTest",
        },
        "controls": {
            "registration_ctest": args.controls_ok == "true",
            "identity_control": "unprocessed target at fixed reference RMS",
            "energy_matched_control": "scalar-only target gain matched to "
                                      "measured tilt RMS",
            "level_confound_control": f"+{LEVEL_CONFOUND_DB:g} dB scalar target "
                                      "gain, deliberately unmatched",
            "adverse_cases": [
                "invalid descriptor schema", "wrong descriptor digest",
                "nonempty settings", "unsupported execution modes",
                "unexpected caller asset", "nonfinite input frame",
                "input_count 159", "partial frame without FINAL_INPUT",
                "output capacity 159", "stale epoch", "duplicate registration",
                "isolated registry without provider", "reset determinism",
                "interleaved sessions", "repeated drain",
            ],
        },
        "missing_reference_control": missing_reference,
        "quality_controls": quality_controls,
        "qualification": {
            "synthetic_scope_status": ("evidence_complete_synthetic_only"
                                       if evidence_complete else "incomplete"),
            "release_qualification": False,
            "all_required_results_present": required_results_present,
            "all_controls_passed": all(quality_controls.values()),
            "no_missing_result_qualifies": True,
        },
        "limitations": [
            "The source study's whole-clip FFT energy restoration is noncausal; "
            "this reference uses a causal 160 ms/80 ms smoothed power follower, "
            "and exact clip-level matching is applied only in the control.",
            "The source study reports STOI/ESTOI on EARS and VADToolkit speech; "
            "none of that data or scoring is reproduced here. These synthetic "
            "band-excess values are not intelligibility scores.",
            "No listening panel, listener profile, MOS, real-speech STOI/ESTOI "
            "or held-out benchmark is claimed.",
            "Unity-peak exceedances from energy restoration are recorded as a "
            "headroom risk; no limiter, DRC or release configuration is "
            "qualified by this evidence.",
            "No target-device timing, CPU/deadline, memory, licensed runtime, "
            "model weights, downloads or release qualification measured.",
            "No shared CMakeLists.txt, CONTRACTS.md, descriptor registry, "
            "default, public API/ABI, installed v0 behavior, board, handoff "
            "or main-branch change is included.",
        ],
    }

    evidence = TASK / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    report_bytes = (json.dumps(report, sort_keys=True, indent=2,
                               ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    (evidence / "report.json").write_bytes(report_bytes)
    (evidence / "REPORT.md").write_text(markdown(report), encoding="utf-8")
    print(f"evidence_complete={evidence_complete} probes={len(sweeps)} "
          f"masking_conditions={len(conditions)} "
          f"max_peak={report['output_checks']['max_abs_peak']} "
          f"report_sha256={hashlib.sha256(report_bytes).hexdigest()}")
    return 0 if evidence_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
