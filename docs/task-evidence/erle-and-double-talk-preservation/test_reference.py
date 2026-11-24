# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local unittest suite for the ERLE/double-talk preservation evidence adapter."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

import fixture
import reference
import run as adapter
import scorer

ROOT = Path(__file__).resolve().parent


class FixtureTests(unittest.TestCase):
    def test_fixture_is_byte_deterministic(self):
        left = fixture.fixture("overlap_50")
        right = fixture.fixture("overlap_50")
        self.assertEqual(left["streams_sha256"], right["streams_sha256"])
        self.assertEqual(len(left["microphone"]), fixture.TOTAL_SAMPLES)
        self.assertEqual(len(left["near"]), fixture.TOTAL_SAMPLES)
        self.assertEqual(len(left["echo"]), fixture.TOTAL_SAMPLES)
        self.assertEqual(fixture.fixture_digest(), fixture.fixture_digest())

    def test_fixture_spec_pins_room_parameters(self):
        spec = fixture.fixture_spec()
        self.assertEqual(spec["seed"], 20261124)
        self.assertEqual(spec["render_latency_samples"], 32)
        self.assertEqual(spec["delay_change_samples"], 16)
        self.assertEqual(spec["switch_at_sample"], 76800)
        self.assertEqual(spec["overlap_ratios"]["overlap_25"], 0.25)
        self.assertTrue(spec["reset_schedule"]["stale_epoch_rejected"])
        self.assertFalse(spec["room_acoustics_measured"])

    def test_all_conditions_are_seeded_and_finite(self):
        for name in fixture.CONDITIONS:
            data = fixture.fixture(name)
            self.assertTrue(all(math.isfinite(value) for value in data["microphone"]), name)
            self.assertTrue(all(math.isfinite(value) for value in data["echo"]), name)
            if name != "no_reference":
                self.assertEqual(len(data["reference"]), fixture.TOTAL_SAMPLES)


class MetricTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture.fixture("overlap_50")

    def test_erle_is_withheld_when_near_speech_enters_window(self):
        output = [value * 0.5 for value in self.data["microphone"]]
        result = reference.erle_windows(self.data, output)
        self.assertTrue(result["windows"]["early"]["value_db"] is not None)
        tampered = fixture.fixture("overlap_50")
        start, end = fixture.ERLE_WINDOWS["early"]
        tampered["near"][start:end] = [0.1] * (end - start)
        blocked = reference.erle_windows(tampered, output)
        self.assertIsNone(blocked["windows"]["early"]["value_db"])
        self.assertIn("far_end_only_window_violated",
                      blocked["windows"]["early"]["withheld_reasons"])

    def test_erle_withheld_for_silent_render(self):
        data = fixture.fixture("near_only")
        result = reference.erle_windows(data, data["microphone"])
        self.assertFalse(result["applicable"])
        self.assertTrue(all(entry["value_db"] is None for entry in result["windows"].values()))

    def test_erle_withheld_for_render_gap_and_transition(self):
        data = fixture.fixture("reference_dropout")
        result = reference.erle_windows(data, data["microphone"])
        reasons = result["windows"]["post_change"]["withheld_reasons"]
        self.assertIn("render_gap", reasons)

    def test_near_preservation_is_separate_from_erle(self):
        output = list(self.data["microphone"])
        result = reference.near_preservation(self.data, output, fixture.NEAR_WINDOW)
        self.assertTrue(result["applicable"])
        self.assertIsNotNone(result["near_stoi"])
        self.assertIsNotNone(result["near_si_sdr_db"])
        self.assertIsNotNone(result["residual_echo_db"])
        self.assertLess(abs(result["near_attenuation_db"]), 0.1)

    def test_near_metrics_withheld_without_near_speech(self):
        data = fixture.fixture("echo_only")
        result = reference.near_preservation(data, data["microphone"], fixture.NEAR_WINDOW)
        self.assertFalse(result["applicable"])
        self.assertIsNone(result["near_si_sdr_db"])
        self.assertIn("no_near_speech_in_window", result["withheld_reasons"])

    def test_scorer_rejects_invalid_pairs(self):
        self.assertEqual(scorer.si_sdr([1.0], [1.0, 2.0])[1], "invalid_input")
        self.assertEqual(scorer.si_sdr([0.0, 0.0], [1.0, 2.0])[1], "zero_reference_energy")
        self.assertEqual(scorer.si_sdr([1.0, 2.0], [1.0, 2.0])[1], "perfect_reconstruction")

    def test_qualification_gate_blocks_injected_missing_result(self):
        report = self._report()
        row = copy.deepcopy(report["results"]["overlap_50"][reference.CANDIDATE])
        self.assertEqual(row["missing_results"], [])
        self.assertTrue(row["qualifies"])
        row["near_preservation"]["near_stoi"] = None
        missing = reference.qualification_gate(row)
        self.assertIn("near:near_stoi", missing)
        self.assertTrue(missing)

    def test_no_reference_row_never_qualifies(self):
        report = self._report()
        row = report["results"]["no_reference"][reference.CANDIDATE]
        self.assertEqual(row["status"], "blocked_no_reference")
        self.assertFalse(row["qualifies"])
        self.assertIsNone(row["near_preservation"]["near_si_sdr_db"])

    def _report(self):
        return json.loads((ROOT / "report.json").read_text(encoding="utf-8"))


class ProcessorTests(unittest.TestCase):
    def test_no_reference_is_passthrough_without_adaptation(self):
        data = fixture.fixture("no_reference")
        result = reference.run_stream(data, reference.CANDIDATE)
        self.assertEqual(fixture.tensor_digest(result["output"]),
                         data["streams_sha256"]["microphone"])
        self.assertEqual(result["adapted_frames"], 0)
        self.assertTrue(all(status == "no_reference_passthrough"
                            for status in result["statuses"]))

    def test_invalid_frames_are_rejected_with_unchanged_state(self):
        cases = reference.invalid_and_missing_cases()
        self.assertGreaterEqual(len(cases), 8)
        allowed = {"rejected", "withheld_missing_reference",
                   "withheld_no_valid_far_end_only_window"}
        for name, case in cases.items():
            with self.subTest(name=name):
                self.assertIn(case["status"], allowed)
                self.assertIsNone(case["metrics"])
                self.assertFalse(case["qualifies"])
        self.assertTrue(cases["stale_epoch"]["state_unchanged"])
        self.assertTrue(cases["stale_position"]["state_unchanged"])
        self.assertTrue(cases["nonfinite_microphone"]["state_unchanged"])

    def test_reset_schedule_is_epoch_ordered(self):
        processor = reference.Processor(reference.CANDIDATE)
        with self.assertRaises(reference.FrameError):
            processor.reset(2, 100)
        processor.reset(2, 0)
        with self.assertRaises(reference.FrameError):
            processor.reset(2, 0)

    def test_fixed_hybrid_replay_damages_near_preservation(self):
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        rows = report["results"]["overlap_50"]
        identity = rows["identity"]["near_preservation"]
        hybrid = rows["fixed_hybrid_damage_replay"]["near_preservation"]
        self.assertLess(hybrid["near_stoi"], identity["near_stoi"])
        self.assertLess(hybrid["near_si_sdr_db"], identity["near_si_sdr_db"])
        self.assertLess(hybrid["near_attenuation_db"], 0.0)
        self.assertFalse(rows["fixed_hybrid_damage_replay"]["qualifies"])

    def test_candidate_erle_is_measured_on_far_end_only_windows(self):
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        row = report["results"]["echo_only"][reference.CANDIDATE]
        self.assertTrue(row["far_end_erle"]["applicable"])
        for entry in row["far_end_erle"]["windows"].values():
            self.assertTrue(entry["far_end_only"])
            self.assertIsNotNone(entry["value_db"])


class AdapterTests(unittest.TestCase):
    def test_inspect_request(self):
        request = {
            "protocol_version": 1, "operation": "inspect",
            "candidate_ref": {"kind": "component", "id": "erle-and-double-talk-preservation", "revision": 1},
            "adapter_ref": {"kind": "adapter", "id": "erle-and-double-talk-preservation", "revision": 1},
            "configuration": {"variant": reference.CANDIDATE},
        }
        result = adapter.inspect(request)
        self.assertEqual(result["registration"], "unregistered developer-only; no installed SDK provider")
        self.assertEqual(result["processor_exposure"], "none")

    def test_run_request_never_qualifies_no_reference(self):
        request = {
            "protocol_version": 1, "operation": "run",
            "candidate_ref": {"kind": "component", "id": "erle-and-double-talk-preservation", "revision": 1},
            "adapter_ref": {"kind": "adapter", "id": "erle-and-double-talk-preservation", "revision": 1},
            "configuration": {"variant": reference.CANDIDATE},
            "condition": "no_reference",
        }
        result = adapter.run(request)
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["status"], "blocked_no_reference")

    def test_run_response_matches_report_row(self):
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        for condition in ("overlap_50", "no_reference"):
            request = {
                "protocol_version": 1, "operation": "run",
                "candidate_ref": {"kind": "component", "id": "erle-and-double-talk-preservation", "revision": 1},
                "adapter_ref": {"kind": "adapter", "id": "erle-and-double-talk-preservation", "revision": 1},
                "configuration": {"variant": reference.CANDIDATE},
                "condition": condition,
            }
            response = adapter.run(request)
            row = report["results"][condition][reference.CANDIDATE]
            for key in ("status", "qualifies", "missing_results"):
                self.assertEqual(response[key], row[key], condition + "/" + key)
            for group in ("far_end_erle", "near_preservation"):
                self.assertEqual(response["metrics"][group], row[group], condition + "/" + group)

    def test_request_validation_rejects_unknown_condition(self):
        request = {
            "protocol_version": 1, "operation": "run",
            "candidate_ref": {"kind": "component", "id": "x", "revision": 1},
            "adapter_ref": {"kind": "adapter", "id": "x", "revision": 1},
            "configuration": {"variant": reference.CANDIDATE},
            "condition": "unknown",
        }
        with self.assertRaises(adapter.RequestError):
            adapter.run(request)


class ArtifactTests(unittest.TestCase):
    def test_report_is_canonical_and_byte_identical(self):
        report_path = ROOT / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report, reference.build_report())
        self.assertEqual(report_path.read_bytes(), fixture.canonical_bytes(report))
        digest = fixture.sha256_bytes(report_path.read_bytes())
        self.assertEqual(
            (ROOT / "report.json.sha256").read_text(encoding="utf-8").splitlines(),
            ["%s  report.json" % fixture.sha256_bytes(fixture.canonical_bytes(report))],
        )
        self.assertEqual(digest, fixture.sha256_bytes(fixture.canonical_bytes(report)))

    def test_three_internal_canonical_repeats_are_exact(self):
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        core = dict(report)
        core.pop("repeat_runs")
        expected = fixture.sha256_bytes(fixture.canonical_bytes(core))
        repeat = report["repeat_runs"]
        self.assertEqual(repeat["three_repeats"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(repeat["canonical_digests"], [expected] * 3)

    def test_evidence_acceptance_profile_is_applied(self):
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        profile = report["acceptance_profile"]
        self.assertEqual(profile["profile"], "evidence")
        self.assertTrue(profile["room_controls_applied"])
        self.assertEqual(profile["scorer_pin_sha256"],
                         fixture.sha256_bytes((ROOT / "scorer.py").read_bytes()))
        self.assertEqual(profile["cohort"], list(fixture.CONDITIONS))
        self.assertEqual(profile["failed_items"], sorted(report["invalid_and_missing_cases"]))
        bundle = report["bundle_validation"]
        self.assertEqual(bundle["representative_valid_result"]["condition"], "overlap_50")
        self.assertEqual(bundle["invalid_or_missing_case"]["condition"], "no_reference")

    def test_mdf_and_tiny16_disclosures_are_present(self):
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        disclosure = report["mdf_limitation_disclosure"]
        self.assertEqual(disclosure["aligned_erle_db"], 16.453939)
        self.assertEqual(disclosure["misaligned_erle_db"], 16.888932)
        self.assertGreater(disclosure["misaligned_erle_db"], disclosure["aligned_erle_db"])
        self.assertIn("ERLE does not validate render alignment", " ".join(report["non_claims"]))
        self.assertIn("No Tiny16 comparison", " ".join(report["non_claims"]))

    def test_strict_json_rejects_duplicate_keys_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / "duplicate.json"
            duplicate.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaises(adapter.RequestError):
                adapter.read_json(duplicate)
            nonfinite = Path(directory) / "nonfinite.json"
            nonfinite.write_text('{"a": NaN}', encoding="utf-8")
            with self.assertRaises(adapter.RequestError):
                adapter.read_json(nonfinite)

    def test_scope_has_no_provider_or_shared_build_file(self):
        self.assertFalse((ROOT / "provider").exists())
        self.assertFalse((ROOT / "CMakeLists.txt").exists())

    def test_historical_control_is_source_reported_only(self):
        contract = json.loads((ROOT / "contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["historical_control"]["status"],
                         "source_reported_not_reproduced_here")
        self.assertAlmostEqual(contract["historical_control"]["double_talk_degradation_delta"],
                               -1.793)

    def test_no_generated_c_header_or_spdx_string_split(self):
        # No C headers are generated here; this guards accidental string splits.
        self.assertFalse(list(ROOT.rglob("*.h")))
        for path in ROOT.glob("*.py"):
            if path.name == "test_reference.py":
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn('SPDX" "-License-Identifier', text)


if __name__ == "__main__":
    unittest.main()
