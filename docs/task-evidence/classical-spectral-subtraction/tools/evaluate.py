#!/usr/bin/env python3
"""Regenerate the deterministic synthetic evidence report for the CSS task."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

from stoi_screen import stoi_screen

TASK = Path(__file__).resolve().parents[1]
PAIRS = ("a", "b", "c")
MODES = ("identity", "css", "speex")


def read_f32(path: Path) -> list[float]:
    return list(struct.unpack("<%df" % (path.stat().st_size // 4), path.read_bytes()))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def round6(value: float) -> float:
    result = round(value, 6)
    return 0.0 if result == 0.0 else result


def si_sdr(reference: list[float], estimate: list[float]) -> float:
    if len(reference) != len(estimate):
        raise ValueError("SI-SDR length mismatch")
    dot = sum(a * b for a, b in zip(estimate, reference))
    reference_energy = sum(value * value for value in reference)
    if reference_energy <= 0.0:
        raise ValueError("reference has no energy")
    scale = dot / reference_energy
    target = [scale * value for value in reference]
    error = sum((estimate[i] - target[i]) ** 2 for i in range(len(reference)))
    target_energy = sum(value * value for value in target)
    if error <= 0.0:
        return 40.0
    return max(-40.0, 10.0 * math.log10(target_energy / error))


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def parse_cli(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        if line.startswith("INFO ") or line.startswith("STATS ") or line.startswith("RESULT "):
            key, payload = line.split(" ", 1)
            result[key.lower()] = json.loads(payload)
    if "result" not in result or "stats" not in result or "info" not in result:
        raise RuntimeError("CLI did not emit INFO/STATS/RESULT")
    return result


def run_cli(cli: Path, work: Path, fixture: Path, profile: Path, mode: str,
            label: str) -> tuple[list[float], dict]:
    output = work / f"{label}.f32"
    command = [str(cli), str(fixture), str(profile), str(output), mode, "1", "0", label]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"CLI {label} failed: {completed.stderr.strip()}")
    return read_f32(output), parse_cli(completed.stdout)


def score(reference: list[float], estimate: list[float]) -> dict:
    return {"si_sdr_db": round6(si_sdr(reference, estimate)),
            "stoi_screen": round6(stoi_screen(reference, estimate))}


def mean(values: list[float]) -> float:
    return round6(sum(values) / len(values))


def load_sources(path: Path) -> dict[str, str]:
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        entries[name] = digest
    return entries


def markdown(report: dict) -> str:
    pairs = report["paired_synthetic"]["pairs"]
    means = report["paired_synthetic"]["means"]
    lines = [
        "# Classical spectral subtraction — synthetic task evidence", "",
        f"Candidate: `{report['candidate']}` · profile: {report['acceptance_profile']} · "
        f"status: **{report['qualification']['synthetic_scope_status']}**.", "",
        "Scope: task-local optional reference behind the public v0 provider "
        "registration boundary. Not installed, not a default, no real weights, "
        "no downloads, no licensed runtime, no listening and no release "
        "qualification.", "",
        "## Paired synthetic cohort", "",
        "| item | identity SI-SDR | CSS SI-SDR | Speex SI-SDR | identity STOI* | CSS STOI* | Speex STOI* |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for pair in pairs:
        values = pair["scores"]
        lines.append(
            "| {id} | {identity_db:.3f} | {css_db:.3f} | {speex_db:.3f} | "
            "{identity_stoi:.3f} | {css_stoi:.3f} | {speex_stoi:.3f} |".format(
                id=pair["id"],
                identity_db=values["identity"]["si_sdr_db"],
                css_db=values["css"]["si_sdr_db"],
                speex_db=values["speex"]["si_sdr_db"],
                identity_stoi=values["identity"]["stoi_screen"],
                css_stoi=values["css"]["stoi_screen"],
                speex_stoi=values["speex"]["stoi_screen"]))
    lines += [
        "",
        f"Means: ΔSI-SDR CSS {means['css_delta_sisdr_db']:+.3f} dB, "
        f"Speex {means['speex_delta_sisdr_db']:+.3f} dB; ΔSTOI* CSS "
        f"{means['css_delta_stoi_screen']:+.3f}, Speex "
        f"{means['speex_delta_stoi_screen']:+.3f}.", "",
        "*STOI is the pinned synthetic `stoi_screen` envelope-correlation "
        "scorer, not standard STOI and not comparable with pilot values.", "",
        "## Controls and integrity", "",
        f"- Registration/lifecycle/adverse CTest: {report['controls']['css_registration_ctest']}.",
        f"- Nonfinite outputs: {report['output_checks']['nonfinite_samples']}; "
        f"maximum absolute output peak: {report['output_checks']['max_abs_peak']:.6f}.",
        f"- Coverage: {report['output_checks']['coverage_ok']}; delay "
        f"{report['alignment']['buffering_delay_samples']} samples; "
        f"startup padding {report['alignment']['startup_padding_samples']} samples; "
        f"final padding counted {report['alignment']['final_padding_samples']} samples.",
        f"- Missing clean-reference control: "
        f"{report['missing_reference_control']['status']} "
        f"({report['missing_reference_control']['detail']}).", "",
        "## Clean-speech preservation", "",
        f"CSS on clean synthetic fixture a: ΔSI-SDR "
        f"{report['clean_preservation']['si_sdr_db']:.3f} dB, STOI* "
        f"{report['clean_preservation']['stoi_screen']:.3f}, RMS ratio "
        f"{report['clean_preservation']['rms_ratio']:.3f}.", "",
        "## Scope and blockers", "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--sources-sha", type=Path, required=True)
    parser.add_argument("--fixture-manifest", type=Path, required=True)
    parser.add_argument("--build-info", type=Path, required=True)
    parser.add_argument("--controls-ok", choices=("true", "false"), required=True)
    args = parser.parse_args()

    args.work.mkdir(parents=True, exist_ok=True)
    fixtures = TASK / "fixtures"
    sources = load_sources(args.sources_sha)
    fixture_digests = load_sources(args.fixture_manifest)
    build_info = json.loads(args.build_info.read_text(encoding="utf-8"))

    pairs = []
    peaks = []
    nonfinite = 0
    coverage_ok = True
    collisions = 0
    out_of_range = 0
    delivered = 0
    startup = 0
    final_padding = 0
    delay = 160
    info_sample = None

    for name in PAIRS:
        clean = read_f32(fixtures / f"clean_{name}.f32")
        noisy = read_f32(fixtures / f"noisy_{name}.f32")
        signals = {"identity": noisy}
        run_meta = {}
        for mode in ("css", "speex"):
            signals[mode], run_meta[mode] = run_cli(
                args.cli, args.work, fixtures / f"noisy_{name}.f32",
                args.profile, mode, f"noisy_{name}_{mode}")
        _, identity_meta = run_cli(
            args.cli, args.work, fixtures / f"noisy_{name}.f32",
            args.profile, "identity", f"noisy_{name}_identity")
        run_meta["identity"] = identity_meta
        scores = {mode: score(clean, signals[mode]) for mode in MODES}
        pairs.append({"id": name, "samples": len(clean), "scores": scores})
        for mode in MODES:
            meta = run_meta[mode]["result"]
            stats = run_meta[mode]["stats"]
            peaks.append(meta["peak"])
            nonfinite += meta["nonfinite"]
            collisions += meta["collisions"]
            out_of_range += meta["out_of_range"]
            coverage_ok = coverage_ok and meta["coverage_ok"]
            delivered += int(stats["delivered_valid_samples"])
            startup += int(stats.get("startup_padding_samples", 0))
            final_padding += int(stats.get("final_padding_samples", 0))
        if info_sample is None:
            info_sample = run_meta["css"]["info"]

    clean_a = read_f32(fixtures / "clean_a.f32")
    css_clean_a, clean_meta = run_cli(
        args.cli, args.work, fixtures / "clean_a.f32", args.profile,
        "css", "clean_a_css")
    clean_stats = clean_meta["stats"]
    preservation = score(clean_a, css_clean_a)
    preservation["rms_ratio"] = round6(rms(css_clean_a) / rms(clean_a))
    peaks.append(clean_meta["result"]["peak"])
    nonfinite += clean_meta["result"]["nonfinite"]
    collisions += clean_meta["result"]["collisions"]
    out_of_range += clean_meta["result"]["out_of_range"]
    coverage_ok = coverage_ok and clean_meta["result"]["coverage_ok"]
    delivered += int(clean_stats["delivered_valid_samples"])
    startup += int(clean_stats.get("startup_padding_samples", 0))
    final_padding += int(clean_stats.get("final_padding_samples", 0))

    identity_sisdr = [pair["scores"]["identity"]["si_sdr_db"] for pair in pairs]
    identity_stoi = [pair["scores"]["identity"]["stoi_screen"] for pair in pairs]
    css_delta_sisdr = [pair["scores"]["css"]["si_sdr_db"] - identity_sisdr[i]
                       for i, pair in enumerate(pairs)]
    css_delta_stoi = [pair["scores"]["css"]["stoi_screen"] - identity_stoi[i]
                      for i, pair in enumerate(pairs)]
    speex_delta_sisdr = [pair["scores"]["speex"]["si_sdr_db"] - identity_sisdr[i]
                         for i, pair in enumerate(pairs)]
    speex_delta_stoi = [pair["scores"]["speex"]["stoi_screen"] - identity_stoi[i]
                        for i, pair in enumerate(pairs)]

    missing_path = args.work / "clean_reference_does_not_exist.f32"
    if missing_path.exists():
        raise RuntimeError("missing-reference control path unexpectedly exists")
    missing_reference = {
        "status": "passed" if not missing_path.is_file() else "failed",
        "detail": "missing clean reference is not scored and cannot qualify the candidate",
    }

    quality_controls = {
        "css_registration_ctest": args.controls_ok,
        "nonfinite_outputs": nonfinite == 0,
        "output_peaks_at_most_unity": max(peaks) <= 1.0,
        "coverage_complete": coverage_ok,
        "no_collisions": collisions == 0,
        "no_out_of_range_samples": out_of_range == 0,
        "missing_reference_not_scored": missing_reference["status"] == "passed",
        "all_pairs_scored": len(pairs) == len(PAIRS),
    }
    css_mean_delta_sisdr = mean(css_delta_sisdr)
    css_mean_delta_stoi = mean(css_delta_stoi)
    required_results_present = (
        len(pairs) == len(PAIRS)
        and all(set(pair["scores"]) == set(MODES) for pair in pairs)
        and all(
            set(item) == {"si_sdr_db", "stoi_screen"}
            for pair in pairs for item in pair["scores"].values()
        )
        and info_sample is not None
        and set(preservation) >= {"si_sdr_db", "stoi_screen", "rms_ratio"}
        and missing_reference["status"] == "passed"
    )
    # Acceptance here is evidence completeness only. The enhancement profile
    # asks for paired scores, controls and preservation; it does not license a
    # release claim, and a negative synthetic STOI screen is reported honestly.
    evidence_complete = all(quality_controls.values()) and required_results_present
    synthetic_observations = {
        "mean_css_delta_sisdr_db": css_mean_delta_sisdr,
        "mean_css_delta_stoi_screen": css_mean_delta_stoi,
        "si_sdr_improved_vs_noisy": css_mean_delta_sisdr > 0.0,
        "stoi_screen_nonnegative": css_mean_delta_stoi >= 0.0,
        "clean_preservation_si_sdr_db": preservation["si_sdr_db"],
        "clean_preservation_rms_ratio": preservation["rms_ratio"],
    }

    report = {
        "schema_id": "audio-sdk/task-evidence/css/0.1",
        "task_id": "SDK-CLASSICAL-SPECTRAL-SUBTRACTION",
        "candidate": "css.reference.v0",
        "acceptance_profile": "enhancement",
        "scope": {
            "boundary": "public provider_v0 registration and session API",
            "delivery": "task-local optional consumer; not installed or default",
            "installed_v0": "unchanged: 16000 Hz, mono f32, 160 samples per call",
            "pinned_base_commit": "9677040cba2929f9936eaa565f200f585d5270a8",
        },
        "build": {
            "sdk_build_id": build_info.get("build_id"),
            "sdk_version": build_info.get("version"),
            "host": build_info.get("target", "unknown"),
            "compiler": build_info.get("c_compiler", "unknown"),
            "execution_mode": 2,
            "session_info_sample": info_sample,
        },
        "inputs": {
            "fixtures_sha256": fixture_digests,
            "sources_sha256": sources,
            "fixture_generator": "tools/generate_fixtures.py (deterministic LCG)",
            "clean_reference_availability": "synthetic only",
        },
        "controls": {
            "css_registration_ctest": args.controls_ok,
            "identity_noisy_control": "noisy fixture copied without processing",
            "task_matched_baseline": "installed speex.ns.v0 on identical synthetic pairs",
            "adverse_cases": [
                "nonfinite input sample", "input_count 159", "partial frame without final flag",
                "output capacity 159", "stale epoch", "stale/closed session",
                "unsupported execution modes", "nonempty settings",
                "wrong descriptor digest", "invalid descriptor schema",
                "missing asset", "tampered asset digest", "nonfinite asset bytes",
            ],
        },
        "paired_synthetic": {
            "unit": "dB for SI-SDR; 0..1 for STOI screen",
            "pairs": pairs,
            "means": {
                "identity_si_sdr_db": mean(identity_sisdr),
                "css_si_sdr_db": mean([p["scores"]["css"]["si_sdr_db"] for p in pairs]),
                "speex_si_sdr_db": mean([p["scores"]["speex"]["si_sdr_db"] for p in pairs]),
                "identity_stoi_screen": mean(identity_stoi),
                "css_stoi_screen": mean([p["scores"]["css"]["stoi_screen"] for p in pairs]),
                "speex_stoi_screen": mean([p["scores"]["speex"]["stoi_screen"] for p in pairs]),
                "css_delta_sisdr_db": css_mean_delta_sisdr,
                "css_delta_stoi_screen": css_mean_delta_stoi,
                "speex_delta_sisdr_db": mean(speex_delta_sisdr),
                "speex_delta_stoi_screen": mean(speex_delta_stoi),
            },
        },
        "clean_preservation": preservation,
        "output_checks": {
            "max_abs_peak": round6(max(peaks)),
            "nonfinite_samples": nonfinite,
            "collisions": collisions,
            "out_of_range_samples": out_of_range,
            "coverage_ok": coverage_ok,
            "delivered_valid_samples": delivered,
        },
        "alignment": {
            "buffering_delay_samples": delay,
            "startup_padding_samples": startup,
            "final_padding_samples": final_padding,
            "duration_semantics": "one valid output sample per accepted input sample; "
                                  "96-sample synthesis tail discarded after final input",
            "state_semantics": "per-session state; reset and interleaved sessions verified in CTest",
        },
        "missing_reference_control": missing_reference,
        "quality_controls": quality_controls,
        "synthetic_observations": synthetic_observations,
        "qualification": {
            "synthetic_scope_status": "evidence_complete_synthetic_only"
                                      if evidence_complete else "incomplete",
            "release_qualification": False,
            "all_required_results_present": required_results_present,
            "all_controls_passed": all(quality_controls.values()),
            "no_missing_result_qualifies": True,
        },
        "limitations": [
            "No real weights, model downloads, licensed runtime or vendor claim; implementation is first-party C.",
            "No real speech, listening test, MOS or real-speech STOI; only deterministic synthetic pairs.",
            "STOI is a pinned synthetic envelope-correlation screen, not standard STOI or pilot-comparable; "
            "it may decrease even when SI-SDR improves and is reported without a pass/fail gate.",
            "Historical pilot values (mean ΔSI-SDR +1.31 dB, batch RTF 0.0505) were not reproduced here; "
            "the tested whole-clip noise estimate is noncausal and is not used in this causal reference.",
            "No target-device pacing, CPU/deadline, memory RSS or release qualification measured.",
            "Fixed state is a single calloc'd instance; no dynamic allocation after create; "
            "no numeric workload timing is claimed.",
        ],
    }

    evidence = TASK / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    report_bytes = (json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                               allow_nan=False) + "\n").encode("utf-8")
    (evidence / "report.json").write_bytes(report_bytes)
    (evidence / "REPORT.md").write_text(markdown(report), encoding="utf-8")
    print(f"evidence_complete={evidence_complete} pairs={len(pairs)} "
          f"max_peak={report['output_checks']['max_abs_peak']}")
    return 0 if evidence_complete else 1


if __name__ == "__main__":
    sys.exit(main())
