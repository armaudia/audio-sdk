"""Build the canonical, machine-readable fixed-RMS VAD analysis report."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import fixtures
import reference
import run

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
ADAPTER_PATH = ROOT / "adapter.json"
AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
BASE_COMMIT = "0673cb354cceb66f2f71faf9af7703b5a5d2fcfa"
TASK_ID = "SDK-FIXED-RMS-VAD"

REQUESTS: dict[str, dict[str, Any]] = {
    scenario: {
        "protocol_version": 1,
        "operation": "run",
        "candidate_ref": {"kind": "reference", "id": "fixed-rms-vad.synthetic.v1", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": reference.ADAPTER_ID, "revision": 1},
        "configuration": dict(run.adapter_descriptor()["configuration"]),
        "attempt_id": "fixed-rms-vad-analysis-20261124",
        "session_id": "session-" + scenario,
        "epoch": 1,
        "scenario": scenario,
    }
    for scenario in run.SCENARIOS
}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in fixtures.SOURCE_PINS.items():
        path = AUDIOML_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("required pinned source missing: " + relative)
        digest = sha256_path(path)
        if digest != expected:
            raise ValueError("pinned source digest mismatch: " + relative)
        observed[relative] = digest
    return observed


def build_report() -> dict[str, Any]:
    pins = verify_pins()
    results = {name: run.run(request) for name, request in REQUESTS.items()}
    primary = results["primary"]
    independent = results["independent_state"]
    events = results["event_bus"]
    adverse = results["adverse"]
    scoring = primary["scoring"]
    delivery = primary["delivery"]
    segments = fixtures.SEGMENTS

    positive_segments = [segment for segment in segments if segment["speech"]]
    negative_segments = [segment for segment in segments if not segment["speech"]]
    counts = {
        "stream_samples": fixtures.STREAM_SAMPLES,
        "sdk_frames": primary["driven"]["frame_count"],
        "analysis_windows": primary["session"]["window_count"],
        "timestamped_probability_events": primary["session"]["probability_event_count"],
        "speech_events": primary["session"]["speech_event_count"],
        "total_events": primary["session"]["event_count"],
        "known_positive_segments": len(positive_segments),
        "known_negative_segments": len(negative_segments),
        "known_positive_samples": sum(segment["end"] - segment["start"]
                                      for segment in positive_segments),
        "known_negative_samples": sum(segment["end"] - segment["start"]
                                      for segment in negative_segments),
        "scored_samples": scoring["known_samples"],
        "unknown_samples": scoring["unknown_samples"],
        "invalid_samples": scoring["invalid_samples"],
        "delivered_events": delivery["delivered_count"],
        "dropped_events": events["delivery"]["dropped_sequence_count"],
        "adverse_rejections": adverse["results"]["invalid_vs_nonspeech_separation"][
            "invalid_rejections_recorded"],
        "source_pins": len(pins),
    }

    local_digests = {
        "fixture_spec": reference.canonical_digest(fixtures.seed_spec()),
        "adapter_descriptor": sha256_path(ADAPTER_PATH),
        "stream_f32": primary["stream_sha256"],
        "primary_events": primary["session"]["events_sha256"],
        "primary_windows": primary["session"]["windows_sha256"],
        "primary_delivered_events": delivery["delivered_digest"],
        "independent_left_events": independent["before"]["left"]["events_sha256"],
        "independent_right_events": independent["before"]["right"]["events_sha256"],
    }

    return {
        "protocol": "sdk.fixed-rms-vad.analysis.v1",
        "contract": reference.CONTRACT_ID,
        "task": TASK_ID,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic",
        "qualification": {
            "status": "incomplete",
            "release_decision": "not_qualified",
            "reason": "Deterministic synthetic boundary fixture only; no matched cohort, "
                      "installed native runtime, target device or listening evidence.",
            "missing_result_policy": "Missing, rejected, unrun or blocked results are recorded "
                                     "as failures/incomplete and never counted as passes.",
        },
        "geometry": {
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": reference.CHANNELS,
            "sample_format": "f32",
            "sdk_frame_samples": reference.SDK_FRAME_SAMPLES,
            "adapter_analysis_window_samples": reference.ADAPTER_FRAME_SAMPLES,
            "sdk_frames_per_analysis_window": 2,
            "source_time_mapping": "identity",
            "analysis_content_delay_samples": 0,
        },
        "config": run.adapter_descriptor()["configuration"],
        "source_pins": pins,
        "digests": local_digests,
        "counts": counts,
        "scoring": scoring,
        "boundaries_and_availability": {
            "availability_origin_ns": reference.AVAILABILITY_ORIGIN_NS,
            "nanoseconds_per_sample": reference.NS_PER_SAMPLE,
            "clock_id": reference.CLOCK_ID,
            "probability_intervals_exact": scoring["probability_coverage_ok"],
            "frame_intervals_exact": scoring["coverage_ok"],
            "availability_formula_ok": scoring["availability_ok"],
            "speech_event_intervals": primary["speech_event_intervals"],
        },
        "independent_state": {
            "distinct_event_digests": independent["distinct_event_digests"],
            "right_unchanged_by_left_reset": independent["right_unchanged_by_left_reset"],
            "stale_event_rejected_left": independent["stale_event_rejected_left"],
            "stale_event_rejected_right": independent["stale_event_rejected_right"],
        },
        "event_delivery": {
            "primary": primary["delivery"],
            "dropped_and_stale": {
                "skipped_sequences": events["skipped_sequences"],
                "gaps_recorded": events["gaps_recorded"],
                "dropped_sequence_count": events["delivery"]["dropped_sequence_count"],
                "delivered_digest": events["delivery"]["delivered_digest"],
                "stale_event_rejected": events["stale_event_rejected"],
                "invalid_event_rejected": events["invalid_event_rejected"],
                "event_count_after_invalid": events["count_after_invalid"],
            },
        },
        "adverse_controls": adverse["results"],
        "validity_separation": {
            "known_samples": scoring["known_samples"],
            "unknown_samples": scoring["unknown_samples"],
            "invalid_samples_in_primary_denominator": scoring["invalid_samples"],
            "nonspeech_samples": scoring["nonspeech_samples"],
            "invalid_control_rejections": counts["adverse_rejections"],
            "invalid_never_counted_as_nonspeech": True,
        },
        "blocked": {
            "matched_cohort": {
                "status": "blocked",
                "reason": "No rights-cleared held-out AMI cohort, label partition, frozen "
                          "candidate configuration or historical heldout-results.json asset "
                          "is available in this task scope.",
                "missing_artifact": "data/runs/vad-chaining-ami-20261031-01/heldout-results.json",
                "reopen_when": "A pinned, rights-cleared cohort and exact candidate outputs "
                               "are supplied with an independent scorer.",
            },
            "intended_execution_profile": {
                "status": "blocked",
                "reason": "No installed native SDK provider, pinned runtime, target device, "
                          "deadline budget or matched workload is available; this fixture "
                          "runs only a stdlib Python reference.",
                "reopen_when": "An installed provider and agreed availability/deadline budget "
                               "are available with independent timing and state evidence.",
            },
        },
        "non_claims": [
            "No public API, ABI, CONTRACTS.md, CMakeLists.txt, descriptor, registry default "
            "or installed SDK behavior is changed.",
            "No real weights, downloads, corpora, licensed runtimes, target-device results or "
            "listening tests are used or claimed.",
            "The logistic score is an uncalibrated deterministic transform of window RMS; it "
            "is not a model posterior or a calibrated speech probability.",
            "The historical AMI FN 62.95% / FP 25.35% figures are source-reported desktop "
            "baseline values and are not reproduced or confirmed here.",
            "No throughput, CPU, memory, deadline or physical availability measurement is made.",
        ],
    }


def main() -> int:
    text = json.dumps(build_report(), sort_keys=True, separators=(",", ":"),
                      allow_nan=False) + "\n"
    REPORT_PATH.write_bytes(text.encode("ascii"))
    print(f"wrote {REPORT_PATH} ({len(text.encode('ascii'))} bytes, "
          f"sha256={hashlib.sha256(text.encode('ascii')).hexdigest()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
