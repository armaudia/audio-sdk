# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for the task-local EARS preservation-screen harness."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json('{"a":1,"a":2}')
        self.assertEqual(caught.exception.code, "duplicate_json_key:a")

    def test_nonfinite_constants_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.Reject) as caught:
                reference.parse_strict_json('{"a":%s}' % token)
            self.assertEqual(caught.exception.code,
                             "nonfinite_json_constant:" + token)

    def test_malformed_json_rejected(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json('{"a":')
        self.assertEqual(caught.exception.code, "invalid_json")

    def test_canonical_bytes_are_sorted_and_compact(self):
        value = {"b": [1, 2], "a": {"z": "x"}}
        self.assertEqual(reference.canonical_text(value),
                         '{"a":{"z":"x"},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         reference.sha256_bytes(
                             reference.canonical_bytes(value)))


class MetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = reference.build_fixture()
        cls.mic = cls.fixture["mic"]

    def test_identity_is_exact_and_capped(self):
        metrics = reference.score_pair(self.mic, self.mic, max_lag=0)
        self.assertEqual(metrics["si_sdr_millidb"],
                         reference.MAX_MILLIDB)
        self.assertEqual(metrics["snr_millidb"], reference.MAX_MILLIDB)
        self.assertEqual(metrics["rmse_millisample"], 0)
        self.assertEqual(metrics["lag_samples"], 0)
        self.assertEqual(metrics["clipped_samples"], 0)

    def test_si_sdr_is_scale_invariant_and_gain_control_detects_level(self):
        half = [value // 2 for value in self.mic]
        metrics = reference.score_pair(self.mic, half, max_lag=0)
        self.assertGreater(metrics["si_sdr_millidb"], 80000)
        self.assertLess(metrics["snr_millidb"], 7000)
        self.assertLess(metrics["level_change_millidb"], -5900)
        self.assertGreater(metrics["level_change_millidb"], -6100)
        self.assertGreater(metrics["rmse_millisample"], 0)

    def test_si_sdr_ignores_constant_offset_but_snr_does_not(self):
        offset = [max(reference.Q15_MIN,
                      min(reference.Q15_MAX, value + 500))
                  for value in self.mic]
        metrics = reference.score_pair(self.mic, offset, max_lag=0)
        self.assertEqual(metrics["si_sdr_millidb"], reference.MAX_MILLIDB)
        self.assertLess(metrics["snr_millidb"], 30000)
        self.assertGreater(metrics["rmse_millisample"], 0)

    def test_region_metrics_detect_speech_damage(self):
        damaged = list(self.mic)
        for index in range(0, 1920):
            damaged[index] = damaged[index] // 10
        metrics = reference.score_pair(self.mic[:1920], damaged[:1920],
                                       max_lag=0)
        # SI-SDR is scale invariant, so per-region attenuation stays high;
        # SNR and level change are the gain-sensitive preservation signals.
        self.assertGreater(metrics["si_sdr_millidb"], 60000)
        self.assertLess(metrics["snr_millidb"], 12000)
        self.assertLess(metrics["level_change_millidb"], -18000)

    def test_alignment_tie_break_and_probes(self):
        probes = reference.alignment_probes()
        self.assertTrue(probes["zero_shift_best"])
        zero = [row for row in probes["probes"]
                if row["shift_samples"] == 0][0]
        self.assertEqual(zero["si_sdr_millidb"], reference.MAX_MILLIDB)
        self.assertTrue(all(row["si_sdr_millidb"] < zero["si_sdr_millidb"]
                            for row in probes["probes"]
                            if row["shift_samples"] != 0))

    def test_fixture_is_stable_and_not_ears(self):
        spec = self.fixture["spec"]
        self.assertTrue(spec["synthetic_only"])
        self.assertFalse(spec["is_ears_recording"])
        self.assertEqual(len(self.mic), reference.FIXTURE_LENGTH)
        self.assertEqual(spec["signal_digests"]["mic"],
                         reference.signal_digest(self.mic))
        self.assertEqual(reference.validate_fixture(spec)["validated"], True)

    def test_fixture_validation_rejects_bad_specs(self):
        spec = reference.fixture_spec()
        spec["length_samples"] = 9601
        with self.assertRaises(reference.Reject):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["segments"] = spec["segments"][:-1]
        with self.assertRaises(reference.Reject):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["segments"] = [dict(segment) for segment in spec["segments"]]
        spec["segments"][0]["noise_amplitude"] = 5000
        with self.assertRaises(reference.Reject):
            reference.validate_fixture(spec)

    def test_signal_rejection_matrix(self):
        frame = self.mic[:320]
        with self.assertRaises(reference.Reject) as caught:
            reference.score_pair(None, frame)
        self.assertEqual(caught.exception.code, "missing_input")
        with self.assertRaises(reference.Reject) as caught:
            reference.score_pair(frame, None)
        self.assertEqual(caught.exception.code, "missing_estimate")
        with self.assertRaises(reference.Reject) as caught:
            reference.score_pair([], [])
        self.assertEqual(caught.exception.code, "empty_signal:reference")
        with self.assertRaises(reference.Reject) as caught:
            reference.score_pair(frame, frame[:-1])
        self.assertEqual(caught.exception.code, "length_mismatch")
        for bad, code in ((float("nan"), "nonfinite_input:reference"),
                          (float("inf"), "nonfinite_input:reference"),
                          (40000, "sample_out_of_range:reference"),
                          ("x", "invalid_sample:reference"),
                          (True, "invalid_sample:reference")):
            with self.assertRaises(reference.Reject) as caught:
                reference.score_pair([bad] + frame[1:], frame)
            self.assertEqual(caught.exception.code, code)
        for max_lag in (-1, reference.MAX_LAG_SAMPLES + 1):
            with self.assertRaises(reference.Reject) as caught:
                reference.score_pair(frame, frame, max_lag=max_lag)
            self.assertEqual(caught.exception.code, "invalid_integer:max_lag")
        for threshold in (0, 40000):
            with self.assertRaises(reference.Reject) as caught:
                reference.score_pair(frame, frame, clip_threshold=threshold)
            self.assertEqual(caught.exception.code,
                             "invalid_integer:clip_threshold")


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.controls = {row["control_id"]: row
                        for row in cls.report["preservation_controls"]}

    def test_six_controls_are_unqualified(self):
        self.assertEqual(len(self.controls), 6)
        for control in self.controls.values():
            self.assertIs(control["is_candidate"], False)
            self.assertIs(control["is_ears_candidate_output"], False)
            self.assertIs(control["qualifies"], False)
            self.assertIs(control["is_scorer_qualified"], False)
            self.assertEqual(len(control["regions"]), 6)

    def test_identity_control(self):
        identity = self.controls["identity_input"]
        self.assertTrue(identity["bit_identical"])
        self.assertEqual(identity["global"]["si_sdr_millidb"],
                         reference.MAX_MILLIDB)
        self.assertEqual(self.report["identity_control"]["bit_identical"],
                         True)
        self.assertIs(self.report["identity_control"]["qualifies"], False)

    def test_noise_attenuation_keeps_speech(self):
        control = self.controls["noise_only_quarter"]
        pause = [row for row in control["regions"]
                 if row["segment"] == "speech_pause_noise_only"][0]
        before = [row for row in control["regions"]
                  if row["segment"] == "noisy_speech"][0]
        self.assertLess(pause["level_change_millidb"], -10000)
        self.assertGreater(before["level_change_millidb"], -10)

    def test_speech_damage_is_detected(self):
        control = self.controls["speech_initial_tenth"]
        initial = [row for row in control["regions"]
                   if row["segment"] == "clean_only_initial"][0]
        later = [row for row in control["regions"]
                 if row["segment"] == "clean_only_final"][0]
        self.assertLess(initial["snr_millidb"], 12000)
        self.assertLess(initial["level_change_millidb"], -18000)
        self.assertGreater(later["si_sdr_millidb"], 90000)
        self.assertGreater(later["level_change_millidb"], -10)

    def test_half_gain_is_flagged_by_snr_and_level(self):
        control = self.controls["half_gain"]
        self.assertGreater(control["global"]["si_sdr_millidb"], 80000)
        self.assertLess(control["global"]["snr_millidb"], 7000)
        self.assertLess(control["global"]["level_change_millidb"], -5900)

    def test_bounded_control_counts_saturation(self):
        control = self.controls["bounded_8000"]
        self.assertGreater(control["bounded_samples"], 0)
        self.assertLess(control["global"]["si_sdr_millidb"], 20000)
        self.assertEqual(control["global"]["clipped_samples"], 0)


class ManifestTests(unittest.TestCase):
    def test_valid_synthetic_manifest(self):
        result = reference.validate_manifest(reference._base_manifest(),
                                             expected_items=2)
        self.assertEqual(result["validated"], True)
        self.assertEqual(result["items"], 2)
        self.assertEqual(result["outputs"], 2)
        self.assertIs(result["audio_read"], False)
        self.assertIs(result["scorer_executed"], False)
        self.assertEqual(result["scorer_status"],
                         {"stoi": "blocked", "dnsmos_p835": "blocked"})

    def test_real_expected_count_is_743(self):
        self.assertEqual(reference.screen_manifest_spec()["real_expected_items"],
                         743)
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest(reference._base_manifest(),
                                        expected_items=743)
        self.assertEqual(caught.exception.code,
                         "expected_item_count_mismatch:743:2")

    def test_manifest_rejects_wrong_geometry(self):
        for key, value, code in (
            ("sample_rate_hz", 8000, "unsupported_sample_rate"),
            ("original_sample_rate_hz", 16000,
             "unsupported_original_sample_rate"),
            ("frame_samples", 256, "unsupported_frame_samples"),
        ):
            manifest = reference._base_manifest()
            manifest[key] = value
            with self.assertRaises(reference.Reject) as caught:
                reference.validate_manifest(manifest)
            self.assertEqual(caught.exception.code, code)

    def test_manifest_files_missing_fail_closed(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest_files(reference._base_manifest(),
                                              reference.SOURCE_ROOT)
        self.assertEqual(caught.exception.code,
                         "missing_input_file:synthetic-0001")

    def test_adverse_matrix_is_complete(self):
        cases = reference.adverse_rejections()
        self.assertEqual(len(cases), 60)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["expected_code"] == case["observed_code"]
                            for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        identifiers = {case["case_id"] for case in cases}
        for required in ("duplicate_json_key", "signal_nan",
                         "signal_out_of_range", "scorer_absent",
                         "real_screen_blocked"):
            self.assertIn(required, identifiers)


class ScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = reference.scorer_registry()
        cls.gate = reference.real_screen_gate()

    def test_both_exact_scorers_are_blocked(self):
        self.assertEqual(self.registry["stoi"]["status"], "blocked")
        self.assertEqual(self.registry["dnsmos_p835"]["status"], "blocked")
        for row in self.registry.values():
            self.assertIs(row["executed"], False)
            self.assertIsNone(row["result"])
            self.assertIs(row["qualifies"], False)

    def test_scorer_admission_rejects_absent(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.admit_scorer("stoi")
        self.assertEqual(caught.exception.code,
                         "missing_scorer_artifact:stoi")
        with self.assertRaises(reference.Reject) as caught:
            reference.admit_scorer("bogus")
        self.assertEqual(caught.exception.code,
                         "unsupported_scorer:bogus")

    def test_real_screen_gate_is_blocked_and_empty(self):
        self.assertEqual(self.gate["status"], "blocked")
        self.assertEqual(self.gate["items_scored"], 0)
        self.assertIs(self.gate["scoring_invoked"], False)
        self.assertIs(self.gate["audio_read"], False)
        self.assertIs(self.gate["qualifies"], False)
        self.assertIn("inputs/manifest.json", self.gate["missing"])
        with self.assertRaises(reference.Reject) as caught:
            reference.require_real_screen()
        self.assertEqual(caught.exception.code,
                         "blocked_real_screen:inputs/manifest.json")


class AggregateTests(unittest.TestCase):
    def test_valid_aggregate_is_deterministic_and_unqualified(self):
        rows = [{
            "sample_id": "synthetic-%04d" % (index + 1),
            "candidate_id": "identity-control",
            "si_sdr_millidb": 999000,
            "snr_millidb": 999000,
            "rmse_millisample": 0,
            "peak_milli": 226,
            "clipped_samples": 0,
            "lag_samples": 0,
        } for index in range(2)]
        first = reference.aggregate_preservation(rows, expected_items=2)
        second = reference.aggregate_preservation(copy.deepcopy(rows),
                                                  expected_items=2)
        self.assertEqual(first, second)
        self.assertEqual(first["n_items"], 2)
        self.assertEqual(first["metrics"]["si_sdr_millidb"]["mean"],
                         reference.MAX_MILLIDB)
        self.assertIs(first["qualifies"], False)
        self.assertIs(first["population_inference"], False)

    def test_aggregate_rejects_duplicates_and_nonfinite(self):
        rows = [{
            "sample_id": "synthetic-%04d" % (index + 1),
            "candidate_id": "identity-control",
            "si_sdr_millidb": 999000,
            "snr_millidb": 999000,
            "rmse_millisample": 0,
            "peak_milli": 226,
            "clipped_samples": 0,
            "lag_samples": 0,
        } for index in range(2)]
        duplicate = copy.deepcopy(rows)
        duplicate[1]["sample_id"] = "synthetic-0001"
        with self.assertRaises(reference.Reject) as caught:
            reference.aggregate_preservation(duplicate, expected_items=2)
        self.assertEqual(caught.exception.code, "duplicate_screen_sample")
        bad = copy.deepcopy(rows)
        bad[0]["si_sdr_millidb"] = float("nan")
        with self.assertRaises(reference.Reject) as caught:
            reference.aggregate_preservation(bad, expected_items=2)
        self.assertEqual(caught.exception.code,
                         "nonfinite_metric:si_sdr_millidb")
        with self.assertRaises(reference.Reject) as caught:
            reference.aggregate_preservation(rows, expected_items=3)
        self.assertEqual(caught.exception.code,
                         "screen_item_count_mismatch:3:2")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.text, cls.digest = reference.canonical_report(cls.report)

    def test_disposition_and_boundary(self):
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(report["defer_before"], "processor_exposure")
        self.assertEqual(report["qualification"]["status"],
                         "not_qualified")
        self.assertIs(report["qualification"]["qualifies"], False)
        self.assertIs(report["qualification"]["missing_result_promoted"],
                      False)
        self.assertTrue(all(value is False
                            for value in report["boundary"].values()))
        self.assertIs(report["scope"]["synthetic_only"], True)
        self.assertIs(report["scope"]["task_local_only"], True)

    def test_profile_items_are_only_synthetic_or_blocked(self):
        items = self.report["acceptance_profile"]["required_items"]
        self.assertEqual(len(items), 6)
        for name, item in items.items():
            self.assertIn(item["status"], {"synthetic_only", "blocked"}, name)
            self.assertNotEqual(item["status"], "qualified", name)

    def test_eight_release_gates_are_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_real_screen_is_empty(self):
        gate = self.report["real_screen"]
        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(gate["items_scored"], 0)
        self.assertIs(gate["scoring_invoked"], False)
        self.assertIs(gate["audio_read"], False)
        self.assertFalse(gate["corpus_root_present"])

    def test_historical_values_are_not_reproduced(self):
        history = self.report["historical_screen"]
        self.assertTrue(history["retained"])
        self.assertIs(history["reproduced"], False)
        self.assertIs(history["values_imported"], False)
        self.assertIs(history["qualified"], False)
        self.assertFalse(history["corpus"]["staged"])
        self.assertEqual(history["corpus"]["items"], 743)

    def test_contract_matches_report(self):
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["release_gates"],
                         self.report["release_gates"])
        self.assertEqual(contract["exact_blockers"],
                         self.report["exact_blockers"])
        self.assertEqual(contract["source_pins"],
                         self.report["source_pins"])
        self.assertEqual(contract["boundary_pins"],
                         self.report["boundary_pins"])
        self.assertIn(reference.TASK_PREFIX + "reference.py",
                      contract["artifact_pins"])
        self.assertNotIn(reference.TASK_PREFIX + "contract.json",
                         contract["artifact_pins"])
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256",
                         contract["artifact_pins"])

    def test_stable_board_identity(self):
        row = self.report["board_row"]
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         reference.BOARD_ROW_STABLE_SHA256)
        self.assertNotIn("TASKS.json",
                         reference.canonical_text(self.report["source_pins"]))
        self.assertNotIn("TASKS.json",
                         reference.canonical_text(self.report["boundary_pins"]))

    def test_three_builds_are_byte_identical(self):
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)
        self.assertEqual(self.text, texts[0])

    def test_no_qualified_claim_in_canonical_report(self):
        self.assertNotIn('"qualifies":true', self.text)
        self.assertNotIn('"status":"qualified"', self.text)
        self.assertNotIn('"real_scorer_executed":true', self.text)
        self.assertNotIn('"items_scored":743', self.text)


if __name__ == "__main__":
    unittest.main()
