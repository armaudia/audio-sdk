# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SpeexDSP VAD analysis fixture."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import fixtures
import reference
import run

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"


def strict_json(path: Path) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise AssertionError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token):
        raise AssertionError("nonfinite_json_constant:" + token)

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


class SpeexdspVadReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)
        cls.generated = reference.build_report()
        cls.generated_text, cls.generated_digest = reference.canonical_report(cls.generated)

    def test_01_stimuli_are_deterministic_and_pinned(self) -> None:
        first, digest = fixtures.build_frames()
        second, digest_two = fixtures.build_frames()
        self.assertEqual(first, second)
        self.assertEqual(digest, digest_two)
        self.assertEqual(digest, self.report["digests"]["pcm_f32_sha256"])
        self.assertEqual(len(first), fixtures.TOTAL_FRAMES)
        self.assertEqual(len(first[0]), fixtures.SDK_FRAME_SAMPLES)

    def test_02_source_pins_exact_and_complete(self) -> None:
        self.assertEqual(fixtures.verify_pins(), self.report["source_pins"])
        self.assertEqual(len(self.report["source_pins"]), 12)
        self.assertEqual(self.report["source_pins"][
            "adapters/speexdsp-vad/adapter.json"],
            "ded307574ef9531e4e9232fec82f55e013daf19c931f62dfda07e1e3b070fcc9")

    def test_03_adapter_boundary_identity_and_divergence(self) -> None:
        adapter = reference.adapter_descriptor()
        self.assertEqual(adapter["identity"], reference.ADAPTER_ID)
        self.assertEqual(adapter["configuration"]["frame_samples"], 320)
        boundary = self.report["boundary"]
        self.assertEqual(boundary["sdk_frame_samples"], 160)
        self.assertEqual(boundary["adapter_frame_samples"], 320)
        self.assertIn("No numeric parity is claimed", boundary["frame_divergence"])
        self.assertFalse(boundary["public_abi_changed"])
        self.assertEqual(boundary["provider_default"], "off_unregistered")

    def test_04_canonical_report_is_byte_identical(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual((text + "\n").encode("utf-8"), REPORT.read_bytes())
        self.assertEqual(digest, self.generated_digest)
        self.assertEqual(digest, SIDECAR.read_text(encoding="ascii").strip())
        self.assertEqual(self.generated, self.report)
        self.assertEqual(reference.sha256_bytes(REPORT.read_bytes()),
                         "23330682d0dd4b90bcade45b24651409672e9bef1b6ead304457bd21368fd057")

    def test_05_three_repeats_are_byte_identical(self) -> None:
        payloads = set()
        digests = set()
        for _ in range(3):
            report = reference.build_report()
            text, digest = reference.canonical_report(report)
            payloads.add((text + "\n").encode("utf-8"))
            digests.add(digest)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(len(digests), 1)
        self.assertEqual(payloads.pop(), REPORT.read_bytes())
        self.assertEqual(self.report["regeneration"]["required_repeats"], 3)
        self.assertEqual(self.report["regeneration"]["comparison"], "byte_identical")
        self.assertEqual(self.report["regeneration"]["tolerance"], "none")

    def test_06_report_cli_regenerates_identical_bytes(self) -> None:
        outputs = []
        for _ in range(2):
            proc = subprocess.run(
                [sys.executable, str(HERE / "run.py"), "--report"],
                capture_output=True, text=True, check=True)
            outputs.append(proc.stdout)
            self.assertIn("repeats=3 byte_identical=true", proc.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(REPORT.read_bytes(),
                         (self.generated_text + "\n").encode("utf-8"))
        self.assertEqual(SIDECAR.read_text(encoding="ascii").strip(),
                         self.generated_digest)

    def test_07_counts_and_stream_digests_exact(self) -> None:
        counts = self.report["counts"]
        self.assertEqual(counts["sdk_frames"], 330)
        self.assertEqual(counts["probability_events_known"], 300)
        self.assertEqual(counts["probability_events_unknown"], 30)
        self.assertEqual(counts["speech_events"], 1)
        self.assertEqual(counts["bus_events"], 331)
        self.assertEqual(counts["bus_dropped_events"], 0)
        self.assertEqual((counts["tp"], counts["fn"], counts["fp"], counts["tn"]),
                         (61, 89, 30, 120))
        self.assertEqual(sum(counts[key] for key in ("tp", "fn", "fp", "tn")), 300)
        self.assertEqual(counts["pcm16_clipped_samples"], 279)
        self.assertEqual(self.report["digests"]["probability_stream_sha256"],
                         "53a9a560e94c3e7d95c654d2915d542a18f8f6c7e50c6e0976409982f218e7a2")
        self.assertEqual(self.report["digests"]["speech_events_sha256"],
                         "dab7f5c28986c4f2e791c4bb150e5cc164a4961f330d245391d83cad30307fd5")

    def test_08_analysis_scoring_is_exact(self) -> None:
        score = self.report["scoring"]
        self.assertEqual(score["totals"], {"tp": 61, "fn": 89, "fp": 30, "tn": 120})
        self.assertEqual(score["speech_miss_rate"], 0.593333333)
        self.assertEqual(score["false_alarm_rate"], 0.2)
        self.assertEqual(score["scored_samples"], 48000)
        self.assertEqual(score["unknown_samples"], 4800)
        self.assertEqual(score["known_positive_samples"], 24000)
        self.assertEqual(score["known_negative_samples"], 24000)
        self.assertEqual(score["invalid_samples"], 0)
        self.assertIsNone(score["no_scored_speech_reason"])
        self.assertIsNone(score["no_scored_nonspeech_reason"])

    def test_09_stratified_false_negative_and_false_alarm(self) -> None:
        strata = self.report["scoring"]["stratified"]
        self.assertEqual(strata["quiet-a"], {"tp": 0, "fn": 60, "fp": 0, "tn": 0})
        self.assertEqual(strata["active-a"], {"tp": 59, "fn": 1, "fp": 0, "tn": 0})
        self.assertEqual(strata["quiet-b"], {"tp": 2, "fn": 28, "fp": 0, "tn": 0})
        self.assertEqual(strata["noise-burst"], {"tp": 0, "fn": 0, "fp": 30, "tn": 0})
        self.assertEqual(strata["idle-a"]["tn"], 60)
        self.assertEqual(strata["idle-b"]["tn"], 30)
        self.assertEqual(strata["idle-c"]["tn"], 30)
        self.assertNotIn("unknown-tail", strata)

    def test_10_event_boundaries_and_delays_exact(self) -> None:
        timings = {row["segment"]: row for row in self.report["scoring"]["timings"]}
        self.assertEqual(timings["quiet-a"], {"segment": "quiet-a", "status": "missed"})
        self.assertEqual(timings["quiet-b"], {"segment": "quiet-b", "status": "missed"})
        active = timings["active-a"]
        self.assertEqual(active["onset_frame"], 151)
        self.assertEqual(active["offset_frame"], 242)
        self.assertEqual(active["onset_delay_samples"], 160)
        self.assertEqual(active["offset_delay_samples"], 5120)
        self.assertEqual(self.report["speech_events"][0]["source_start"], 24160)
        self.assertEqual(self.report["speech_events"][0]["source_end"], 38720)

    def test_11_validity_is_not_nonspeech(self) -> None:
        control = self.report["adverse_controls"]["invalid_vs_nonspeech"]
        self.assertEqual(control["statuses"], {
            "known_zero": "ok",
            "nan_probability": "rejected_invalid_event",
            "out_of_range_probability": "rejected_invalid_event",
            "invalid_validity": "rejected_invalid_event",
            "unknown_probability": "ok",
        })
        self.assertEqual(control["admitted_event_ids"], ["known-zero", "unknown"])
        self.assertEqual(control["known_nonspeech_events"], 1)
        self.assertFalse(control["invalid_counted_as_nonspeech"])

    def test_12_frame_adverse_controls(self) -> None:
        control = self.report["adverse_controls"]["frame_adverse"]
        self.assertEqual(control["missing"], "rejected_missing_frame")
        self.assertEqual(control["nonfinite"], "rejected_nonfinite")
        self.assertEqual(control["infinite"], "rejected_nonfinite")
        self.assertEqual(control["short"], "rejected_short_frame")
        self.assertEqual(control["long"], "rejected_tensor")
        self.assertEqual(control["wrong_shape"], "rejected_tensor")
        self.assertEqual(control["stale_epoch"], "rejected_epoch")
        self.assertEqual(control["wrong_interval"], "rejected_interval")
        self.assertTrue(control["state_unchanged"])
        self.assertEqual(control["short_final_status"], "ok")
        self.assertEqual(control["short_final_valid_count"], 80)
        self.assertEqual(control["short_final_source_end"], 80)

    def test_13_event_adverse_controls(self) -> None:
        control = self.report["adverse_controls"]["event_adverse"]
        self.assertEqual(control["statuses"], {
            "stale_epoch": "rejected_stale_epoch",
            "before_first_sample": "rejected_stale_epoch",
            "stale_availability": "rejected_bad_clock",
            "wrong_clock": "rejected_bad_clock",
        })
        self.assertTrue(control["events_unchanged"])
        self.assertEqual(control["dropped_reasons"], [
            "rejected_stale_epoch", "rejected_stale_epoch",
            "rejected_bad_clock", "rejected_bad_clock"])

    def test_14_independent_state_and_reset(self) -> None:
        control = self.report["adverse_controls"]["independent_state"]
        self.assertTrue(control["distinct_event_digests"])
        self.assertTrue(control["reset_matches_fresh_run"])
        self.assertTrue(control["right_unchanged"])
        self.assertEqual(control["left_epoch"], 2)
        self.assertEqual(control["right_epoch"], 7)

    def test_15_overlapping_sessions_and_cross_hop(self) -> None:
        overlap = self.report["adverse_controls"]["overlapping_sessions"]
        self.assertEqual(overlap["first_accept"], "ok")
        self.assertEqual(overlap["second_reject"], "rejected_stale_epoch")
        self.assertTrue(overlap["distinct_audio"])
        self.assertEqual((overlap["first_events"], overlap["second_events"]), (1, 0))
        hop = self.report["adverse_controls"]["cross_hop"]
        self.assertTrue(hop["exact"])
        self.assertEqual(hop["placement"], [[0, 10], [1, 160], [2, 10]])
        self.assertEqual(hop["total_overlap"], 180)

    def test_16_exact_intervals_and_availability(self) -> None:
        controls = self.report["adverse_controls"]
        self.assertTrue(all(controls["source_intervals"].values()))
        availability = controls["availability"]
        self.assertTrue(availability["probability_availability_monotonic"])
        self.assertTrue(availability["unknown_events_have_no_availability"])
        self.assertEqual(availability["nanoseconds_per_sample"], 62500)
        for row in self.report["probabilities"]:
            self.assertEqual(row["source_end"] - row["source_start"], 160)
            if row["validity"] == "known":
                self.assertEqual(row["available_ns"],
                                 row["source_end"] * 62500 + 5000000)
            else:
                self.assertIsNone(row["available_ns"])
                self.assertIsInstance(row["value"], float)
                self.assertTrue(0.0 <= row["value"] <= 1.0)

    def test_17_strict_json_schema_fields(self) -> None:
        required = {
            "schema_id", "contract", "task", "base_commit", "status", "boundary",
            "acceptance_profile", "source_pins", "fixture", "digests", "counts",
            "scoring", "adverse_controls", "probabilities", "speech_events",
            "regeneration", "blockers", "non_claims",
        }
        self.assertTrue(required <= set(self.report))
        self.assertEqual(self.report["schema_id"],
                         "audio-sdk/task-evidence/speexdsp-vad/0.1")
        self.assertEqual(self.report["acceptance_profile"], "Analysis")
        self.assertEqual(self.report["base_commit"], fixtures.BASE_COMMIT)
        self.assertEqual(self.report["task"], fixtures.TASK_ID)

    def test_18_non_claims_and_remaining_gates(self) -> None:
        status = self.report["status"]
        self.assertEqual(status["qualification"], "incomplete")
        self.assertEqual(status["release_decision"], "not_qualified")
        self.assertEqual(status["activity_decision"], "advisory_only_no_gating_claim")
        self.assertFalse(status["installed_sdk_changed"])
        blockers = " ".join(self.report["blockers"])
        self.assertIn("No adverse Tiny16 comparison was run", blockers)
        self.assertIn("S10/protocol clearance", blockers)
        self.assertIn("rights-cleared", blockers)
        self.assertIn("target-runtime", blockers)

    def test_19_protocol_inspect_is_strict(self) -> None:
        base = {
            "protocol_version": 1,
            "operation": "inspect",
            "candidate_ref": {"kind": "reference", "id": "speexdsp-vad.synthetic.v1", "revision": 1},
            "adapter_ref": {"kind": "adapter", "id": reference.ADAPTER_ID, "revision": 1},
            "configuration": dict(reference.adapter_descriptor()["configuration"]),
        }
        base["configuration"]["control"] = run.CONTROL
        response = run.inspect(base)
        self.assertEqual(response["identity"], "speexdsp-vad-reference-v1")
        self.assertEqual(response["supported_scenarios"], list(run.SCENARIOS))
        bad = json.loads(json.dumps(base))
        del bad["adapter_ref"]
        with self.assertRaises(run.RequestError):
            run.inspect(bad)
        bad = json.loads(json.dumps(base))
        bad["configuration"]["frame_samples"] = 160
        with self.assertRaises(run.RequestError):
            run.inspect(bad)

    def test_20_protocol_run_scenarios_match_report(self) -> None:
        base = {
            "protocol_version": 1,
            "operation": "run",
            "candidate_ref": {"kind": "reference", "id": "speexdsp-vad.synthetic.v1", "revision": 1},
            "adapter_ref": {"kind": "adapter", "id": reference.ADAPTER_ID, "revision": 1},
            "configuration": dict(reference.adapter_descriptor()["configuration"]),
            "attempt_id": "speexdsp-vad-analysis-20261124",
            "session_id": "session-primary",
            "epoch": 1,
        }
        base["configuration"]["control"] = run.CONTROL
        primary = run.run({**base, "scenario": "primary"})
        self.assertEqual(primary["stream_sha256"], self.report["digests"]["pcm_f32_sha256"])
        self.assertEqual(primary["scoring"], self.report["scoring"])
        self.assertEqual(primary["speech_intervals"], [[24160, 38720]])
        for scenario in run.SCENARIOS:
            response = run.run({**base, "scenario": scenario, "session_id": "session-" + scenario})
            self.assertEqual(response["scenario"], scenario)
            self.assertEqual(response["attempt_id"], base["attempt_id"])

    def test_21_optional_provider_is_off_by_default(self) -> None:
        cmake = (HERE / "provider" / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn('option(AS_ENABLE_SPEEXDSP_VAD', cmake)
        self.assertIn('"Compile and register the task-local SpeexDSP VAD reference provider" OFF',
                      cmake)
        self.assertNotIn("add_subdirectory", cmake)
        source = (HERE / "provider" / "speexdsp_vad_provider.c").read_text(encoding="utf-8")
        self.assertIn("SPEEX_PREPROCESS_SET_VAD", source)
        self.assertIn("SPEEX_PREPROCESS_GET_VAD", source)
        self.assertIn("SPEEX_PREPROCESS_SET_DENOISE", source)
        self.assertIn("output->samples[index] = frame->input[index]", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
