"""Regenerate the canonical rate-profile evidence report for the click gate.

Every numeric result is obtained through the task-local inspect/run adapter in
run.py. No corpus, model, download, device, listening or timing result is used.
The report and its sidecar are canonical single-line JSON with a terminal LF.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import fixtures
import reference
import run

ROOT = Path(__file__).resolve().parent
TOOL_VERSION = "0.1.0"
BASE_COMMIT = "9677040cba2929f9936eaa565f200f585d5270a8"
BRANCH = "swarm/SDK-MEDIAN-RESIDUAL-CLICK-GATE"
RUNNER_PYTHON = "3.11.5"
RUNNER_PLATFORM = "macOS-27.2.1-arm64-arm-64bit"


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def standard_request(*, operation: str, scenario: str | None = None,
                     case_id: str | None = None, stimulus: dict[str, Any] | None = None,
                     attempt_id: str = "rate-profile-001") -> dict[str, Any]:
    request: dict[str, Any] = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "reference", "id": "dsp.median-residual-click-gate.ref", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": "median-residual-click-gate", "revision": 1},
        "configuration": {
            "control": reference.CONTROL,
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": reference.CHANNELS,
            "sample_format": reference.SAMPLE_FORMAT,
            "sdk_frame_samples": reference.SDK_FRAME_SAMPLES,
            "median_width_samples": reference.DEFAULT_MEDIAN_WIDTH,
            "threshold": reference.DEFAULT_THRESHOLD,
        },
    }
    if operation == "run":
        request.update({"attempt_id": attempt_id, "session_id": "session-" + attempt_id,
                        "epoch": 17, "scenario": scenario})
        if case_id is not None:
            request["case_id"] = case_id
        if stimulus is not None:
            request["stimulus"] = stimulus
    return request


def compact_mapping(result: dict[str, Any]) -> dict[str, Any]:
    mapping = result["source_output_mapping"]
    return {
        "case_id": result["case_id"],
        "source_interval": mapping["source_interval"],
        "valid_interval_count": len(mapping["valid_intervals"]),
        "gap_count": mapping["gap_count"],
        "overlap_count": mapping["overlap_count"],
        "union_equals_source": mapping["union_equals_source"],
        "delivered_valid_samples": mapping["delivered_valid_samples"],
        "startup_padding_samples": mapping["startup_padding_samples"],
        "final_padding_samples": mapping["final_padding_samples"],
        "output_sha256": result["output"]["sha256"],
        "input_sha256": result["source"]["sha256"],
    }


def compact_rate(result: dict[str, Any]) -> dict[str, Any]:
    playback = result["playback"]
    return {
        "case_id": result["case_id"],
        "material": result["material"],
        "source_samples": result["source"]["sample_count"],
        "source_duration_seconds": result["source"]["duration_seconds"],
        "playback_start_ns": playback["playback_start_ns"],
        "playback_end_ns": playback["playback_end_ns"],
        "playback_duration_ns": playback["playback_duration_ns"],
        "playback_duration_seconds": playback["playback_duration_seconds"],
        "rate_segments": playback["rate_segments"],
        "rate_change_boundaries": playback["rate_change_boundaries"],
        "total_rebuffer_ns": playback["total_rebuffer_ns"],
        "buffering_delay_samples": playback["buffering_delay_samples"],
        "decisions_tied_to_source_timestamps":
            result["detections"]["decisions_tied_to_source_timestamps"],
    }


def caller_owned_stimulus() -> dict[str, Any]:
    clean, transients = fixtures.speech_like(320, 424242)
    samples, labels = fixtures.inject_clicks(clean, 424242, 1, 0.75,
                                             event_count=2, spacing=128, start_offset=33)
    plan = fixtures.make_rate_plan("constant_1x", len(samples))
    return {
        "case_id": "caller-owned-320",
        "samples": [float(value) for value in samples],
        "clean": [float(value) for value in clean],
        "labels": list(labels),
        "transient_labels": list(transients),
        "rate_plan": plan,
        "material": "caller-owned synthetic speech-like stimulus",
        "note": "caller-owned array; session copies values",
        "seed": 424242,
    }


def build_report() -> dict[str, Any]:
    inspect_result = run.dispatch(standard_request(operation="inspect"))
    config = standard_request(operation="inspect")["configuration"]
    config_digest = reference.canonical_digest(config)

    cases: list[dict[str, Any]] = []
    for case_id in fixtures.CASE_IDS:
        request = standard_request(operation="run", scenario="case", case_id=case_id)
        result = run.dispatch(request)
        if result.get("case_id") != case_id:
            raise RuntimeError("adapter returned wrong case:" + case_id)
        cases.append(result)

    adverse = run.dispatch(standard_request(operation="run", scenario="adverse"))
    state = run.dispatch(standard_request(operation="run", scenario="state"))
    stimulus = caller_owned_stimulus()
    stimulus_digest = reference.digest_samples(stimulus["samples"])
    manual = run.dispatch(standard_request(operation="run", scenario="manual",
                                           stimulus=stimulus, attempt_id="caller-owned-001"))

    click_counts = fixtures.aggregate_click_counts(cases)
    by_id = {case["case_id"]: case for case in cases}
    clean_cases = ("speech_1x", "music_1x", "silence_1x", "silence_drift")
    preservation = [
        {"case_id": case_id,
         "non_click_samples_changed":
             by_id[case_id]["preservation"]["non_click_samples_changed"],
         "envelope_correlation":
             by_id[case_id]["preservation"]["envelope_correlation_clean_vs_output"],
         "si_sdr_db": by_id[case_id]["preservation"]["si_sdr_db_vs_clean"]}
        for case_id in clean_cases
    ]
    pitch_cases = ("speech_1x", "speech_rate_125_080", "rebuffer_speech",
                   "final_partial_speech", "rate_change_partial")
    pitch = [
        {"case_id": case_id,
         "clean_period_samples": by_id[case_id]["preservation"]["pitch_clean"]["period_samples"],
         "output_period_samples": by_id[case_id]["preservation"]["pitch_output"]["period_samples"],
         "delta_samples": by_id[case_id]["preservation"]["pitch_delta_samples"],
         "applicable": by_id[case_id]["preservation"]["pitch_clean"]["applicable"]
                       and by_id[case_id]["preservation"]["pitch_output"]["applicable"]}
        for case_id in pitch_cases
    ]
    final = by_id["final_partial_speech"]
    final_frames = final["source_output_mapping"]["frame_map"]
    partial_frame = next(frame for frame in final_frames
                         if frame["flags"] & reference.FLAG_FINAL_PADDING
                         and frame["valid_count"] < reference.SDK_FRAME_SAMPLES)

    blockers = [
        "No natural click, breath, consonant or disfluency labels; synthetic square pulses only.",
        "No listening test or authorized human preservation score; envelope/SI-SDR proxies only.",
        "No real weights, downloads, licensed runtime or model asset in this package.",
        "No target-device, paced-callback, CPU/deadline, memory or availability measurement; "
        "the pinned research RTF 0.000290 is source-reported, not reproduced here.",
        "No registered SDK provider, descriptor, ABI, default or installed-archive consumer run.",
        "No STOI or intelligibility measurement; no pystoi dependency installed.",
        "No release qualification, benchmark bundle or board transition; independent review required.",
    ]
    reopen = [
        "Agree click/breath target definitions, rate margins, preservation thresholds, "
        "pitch/transient controls and deadline budget before qualification.",
        "Collect rights-cleared natural events and speech-like material with independent labels "
        "and listener or authorized quality scores.",
        "Build the exact native provider through public registration, verify an installed "
        "consumer and compare frame-by-frame on a frozen cohort.",
        "Run the paced target profile with buffering/fill/flush and resource evidence.",
        "Pass independent review and separate contract/release work before any default promotion.",
    ]

    return {
        "report_id": "sdk-median-residual-click-gate-rate-evidence",
        "report_version": TOOL_VERSION,
        "protocol_version": 1,
        "status": "synthetic_opt_in_not_qualified",
        "scope": {
            "task": "SDK-MEDIAN-RESIDUAL-CLICK-GATE",
            "component": "median-residual-click-gate",
            "repository": "audio-sdk",
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "write_scope": "docs/task-evidence/median-residual-click-gate/ only",
            "installed_v0": "unchanged: 16 kHz mono float32, 160 samples",
            "delivery": "optional, unregistered, developer-only reference",
        },
        "tool_profile": {
            "version": TOOL_VERSION,
            "install_location": "docs/task-evidence/median-residual-click-gate",
            "provenance": "https://github.com/armaudia/audio-sdk.git task-local evidence subtree",
            "runner_python": RUNNER_PYTHON,
            "runner_platform": RUNNER_PLATFORM,
            "stdlib_only": True,
            "compile_build_evidence": "not_applicable_model_free",
            "measured_workload_support": "blocked_not_run",
        },
        "source_pins": fixtures.SOURCE_PINS,
        "source_pin_policy": (
            "Pins are constants in fixtures.py and are verified against AUDIOML_ROOT by "
            "tests; a missing or altered pinned file is a failure, not a skip. The shared "
            "board is mutable provenance and is not a frozen pin."),
        "boundary": {
            "protocol_shape": inspect_result,
            "adapter_descriptor_sha256": file_digest(ROOT / "adapter.json"),
            "reference_py_sha256": file_digest(ROOT / "reference.py"),
            "fixtures_py_sha256": file_digest(ROOT / "fixtures.py"),
            "run_py_sha256": file_digest(ROOT / "run.py"),
            "report_py_sha256": file_digest(ROOT / "report.py"),
            "not_an_audio_bench_bundle": True,
        },
        "method": {
            "detector": "abs(f32 - median of 7 reflected-tap samples) >= 0.35",
            "repair": "simultaneous midpoint interpolation of detected interior samples",
            "endpoint_policy": "detections at sequence endpoints are counted but not repaired",
            "configuration": config,
            "configuration_digest": config_digest,
            "source_coordinate_map": "sample index i -> i*62500 ns in one monotonic domain",
            "frame_semantics": (
                "160-sample frames; output frame p covers source payload positions "
                "[p,p+160); p starts at -3 and advances by 160; valid source intervals "
                "are clipped to accepted content and padding is flagged"),
            "no_sample_rate_conversion": True,
            "no_pause_or_filler_insertion": True,
        },
        "fixtures": {
            "generator": "stdlib hash-derived deterministic streams; no corpus or asset",
            "seed_scheme": "blake2b of median-click-gate:<seed>:<index>, 64-bit uniform",
            "case_ids": list(fixtures.CASE_IDS),
            "case_count": len(fixtures.CASE_IDS),
            "click_widths_samples": list(fixtures.CLICK_WIDTHS),
            "click_amplitudes": list(fixtures.CLICK_AMPLITUDES),
            "case_input_digests": {case_id: fixtures.case_inputs_digest(case_id)
                                   for case_id in fixtures.CASE_IDS},
        },
        "rate_profile": {
            "source_output_mapping": [compact_mapping(case) for case in cases],
            "duration_and_rate_change": [compact_rate(case) for case in cases],
            "pitch_controls": pitch,
            "transient_audibility_controls": [
                {"case_id": case_id,
                 "labeled_click_samples": by_id[case_id]["detections"]["labeled_click_samples"],
                 "detected_click_samples": by_id[case_id]["detections"]["detected_click_samples"],
                 "repaired_samples": by_id[case_id]["detections"]["repaired_samples"],
                 "false_positive_samples": by_id[case_id]["detections"]["fp_samples"],
                 "first_detection_source_ns":
                     by_id[case_id]["detections"]["first_detection_source_ns"],
                 "last_detection_source_ns":
                     by_id[case_id]["detections"]["last_detection_source_ns"],
                 "non_click_samples_changed":
                     by_id[case_id]["preservation"]["non_click_samples_changed"],
                 "transient_samples_preserved":
                     by_id[case_id]["preservation"]["transient_samples_preserved"],
                 "transient_samples_total":
                     by_id[case_id]["preservation"]["transient_samples_total"]}
                for case_id in ("click_w1_a750", "click_w2_a750", "click_w3_a750",
                                "click_w5_a750", "music_1x", "music_rate_08",
                                "speech_rate_125_080", "rebuffer_speech", "silence_1x")
            ],
            "playback_buffering_semantics": {
                "fixed_delay_samples": 3,
                "frame_samples": reference.SDK_FRAME_SAMPLES,
                "first_frame": {"source_first_sample": -3, "valid_offset": 3},
                "final_partial_case": {
                    "case_id": final["case_id"],
                    "source_samples": final["source"]["sample_count"],
                    "partial_frame": {key: partial_frame[key] for key in (
                        "frame_index", "source_first_sample", "source_valid_start",
                        "source_valid_end", "valid_offset", "valid_count", "flags",
                        "payload_sha256")},
                },
                "semantics": cases[0]["playback"]["buffering_semantics"],
                "playback_rate_is_a_schedule_only": (
                    "rate changes, rebuffer gaps and drift alter the playback timeline map; "
                    "they do not resample, stretch, add or drop source samples and do not "
                    "change source-domain pitch proxies"),
            },
            "decision_timestamps": {
                "all_cases_tied_to_source_index": all(
                    case["detections"]["decisions_tied_to_source_timestamps"] for case in cases),
                "ns_per_source_sample": reference.NS_PER_SAMPLE,
                "pause_or_filler_decisions": "none; suppression is per source sample only",
            },
        },
        "click_and_suppression_counts": click_counts,
        "speech_preservation_proxy": {
            "definition": (
                "Non-click sample equality, 40-sample RMS envelope Pearson correlation and "
                "scale-corrected SI-SDR versus the deterministic clean synthetic source; "
                "these are developer proxies, not STOI or listening."),
            "clean_control_cases": preservation,
            "music_transient_preservation_fraction":
                by_id["music_1x"]["preservation"]["transient_preservation_fraction"],
            "all_non_click_samples_unchanged_on_clean_cases": all(
                row["non_click_samples_changed"] == 0 for row in preservation),
        },
        "cases": cases,
        "adverse_controls": adverse,
        "state_controls": state,
        "caller_owned_control": {
            "input_sha256": stimulus_digest,
            "input_samples": len(stimulus["samples"]),
            "output_sha256": manual["output"]["sha256"],
            "case_id": manual["case_id"],
            "source_interval": manual["source_output_mapping"]["source_interval"],
            "copy_semantics": "session appends f32 values; caller arrays are never retained",
        },
        "missing_results_and_qualification": {
            "all_fixture_cases_have_results": len(cases) == len(fixtures.CASE_IDS),
            "all_adverse_controls_observed": adverse["all_observed"],
            "all_adverse_controls_rejected": adverse["all_rejected_or_expected"],
            "missing_adverse_results": adverse["missing_results"],
            "missing_state_results": state["missing_results"],
            "candidate_qualified": False,
            "missing_result_qualifies": False,
            "blockers": blockers,
            "reopen_conditions": reopen,
        },
        "non_claims": [
            "No real weights, model, download or licensed runtime is included.",
            "No corpus, recorded speech, natural click or breath event was used.",
            "No listening, STOI, intelligibility or target-speaker quality result is claimed.",
            "No target-device pacing, CPU, deadline, memory, availability or fill/flush result.",
            "No source-reported RTF is reproduced as local timing evidence.",
            "No public API/ABI, descriptor registry, default, installed v0 behavior or release.",
        ],
        "digests": {
            "adapter_json": file_digest(ROOT / "adapter.json"),
            "reference_py": file_digest(ROOT / "reference.py"),
            "fixtures_py": file_digest(ROOT / "fixtures.py"),
            "run_py": file_digest(ROOT / "run.py"),
            "report_py": file_digest(ROOT / "report.py"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = build_report()
    payload = run.canonical_bytes(report)
    (args.output_dir / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (args.output_dir / "report.json.sha256").write_text(digest + "  report.json\n",
                                                        encoding="ascii")
    print(digest)
    print(hashlib.sha256((args.output_dir / "report.json.sha256").read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
