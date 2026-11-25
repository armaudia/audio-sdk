# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local Rate-profile regression-head evidence."""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import check_licensing
import reference
import verify

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generated = reference.canonical_report_bytes(reference.build_report())
        cls.report = reference.strict_loads(REPORT.read_text(encoding="utf-8"))
        cls.contract = reference.strict_loads(CONTRACT.read_text(encoding="utf-8"))

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_03_strict_json_rejects_nan_and_duplicates(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"x": NaN}')
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"x": 1, "x": 2}')

    def test_04_status_and_qualification(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertFalse(self.report["candidate_qualified"])
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_05_boundary_is_unregistered_and_off(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected", "public_api_abi_change",
                    "provider_registration", "production_callback_registered",
                    "public_variable_frame_actuator"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertTrue(boundary["installed_v0_geometry_preserved"])

    def test_06_public_v0_geometry_unchanged(self) -> None:
        self.assertEqual(self.report["format"], {
            "sample_rate_hz": 16000, "channels": 1, "sample_format": "f32", "frame_samples": 160})

    def test_07_base_commit_and_profile(self) -> None:
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["profile"], "rate")

    def test_08_exact_source_output_intervals(self) -> None:
        for case in self.report["observations"]["constant_rates"].values():
            previous = 0
            for span in case["mapping"]:
                self.assertEqual(span["source_interval"][0], previous)
                previous = span["source_interval"][1]
                self.assertEqual(span["source_interval"][1] - span["source_interval"][0] > 0, True)
            self.assertEqual(previous, case["source_samples"])
        dynamic = self.report["observations"]["dynamic_step"]
        self.assertEqual([span["rate"] for span in dynamic["mapping"]], ["1", "1.25", "0.75", "1.5"])
        self.assertEqual([span["source_interval"][0] for span in dynamic["mapping"]],
                         [0, 3200, 6400, 9600])
        for span in dynamic["mapping"]:
            self.assertEqual(span["source_interval"][0] % reference.HOP, 0)

    def test_09_final_partial_window_and_duration(self) -> None:
        for case in self.report["observations"]["constant_rates"].values():
            self.assertEqual(case["source_samples"] % reference.HOP, 3)
            self.assertEqual(case["final_partial_source_samples"], 3)
            self.assertTrue(case["duration"]["exact_output_samples"])
            self.assertTrue(case["duration"]["error_samples"])
        identity = self.report["observations"]["constant_rates"]["1"]
        self.assertTrue(identity["identity_1x"])
        self.assertEqual(identity["duration"]["output_samples"], identity["source_samples"])
        self.assertEqual(identity["duration"]["exact_output_samples"], "16003")
        for rate in ("0.75", "1.25", "1.5"):
            self.assertIn("/", self.report["observations"]["constant_rates"][rate]["duration"]["error_samples"])

    def test_10_pitch_is_a_proxy_not_a_release_result(self) -> None:
        rates = self.report["observations"]["constant_rates"]
        self.assertAlmostEqual(rates["1"]["pitch_proxy_hz"], 400.0, delta=0.1)
        self.assertLess(rates["0.75"]["pitch_proxy_hz"], rates["1"]["pitch_proxy_hz"])
        self.assertGreater(rates["1.5"]["pitch_proxy_hz"], rates["1"]["pitch_proxy_hz"])
        for case in rates.values():
            self.assertEqual(case["nonfinite_samples"], 0)
            self.assertEqual(case["clipped_samples"], 0)
            self.assertLessEqual(case["peak_abs"], 1.0)

    def test_11_drift_and_silence_are_recorded(self) -> None:
        drift = self.report["observations"]["drift_schedule"]
        self.assertEqual(len(drift["mapping"]), 4)
        self.assertEqual([span["source_interval"] for span in drift["mapping"]],
                         [[0, 3200], [3200, 6400], [6400, 9600], [9600, 16003]])
        self.assertIn("/", drift["duration"]["error_samples"])
        silence = self.report["observations"]["silence"]
        self.assertEqual(silence["peak_abs"], 0.0)
        self.assertEqual(silence["positive_crossings"], {"source": 0, "output": 0})

    def test_12_transient_audibility_not_measured(self) -> None:
        impulse = self.report["observations"]["impulse"]["transient_proxy"]
        self.assertEqual(impulse["source_sample"], 160)
        self.assertEqual(impulse["output_peak_sample"], 128)
        self.assertEqual(impulse["audibility"], "not_measured")

    def test_13_pause_policy_is_source_anchored(self) -> None:
        pause = self.report["observations"]["pause_policy"]
        self.assertEqual([item["label"] for item in pause["timeline"]],
                         ["speech", "pause", "speech", "pause", "speech", "pause", "speech"])
        self.assertEqual([span["rate"] for span in pause["mapping"][::2]], ["1"] * 4)
        self.assertEqual([span["rate"] for span in pause["mapping"][1::2]], ["1.5"] * 3)
        self.assertTrue(pause["speech_preservation_proxy"]["bit_exact_active_speech"])
        self.assertEqual(pause["pause_filler_samples"], 0)
        self.assertEqual(pause["decision_anchor"], "source_sample_interval")

    def test_14_buffer_simulation_is_not_device_timing(self) -> None:
        buffer = self.report["observations"]["buffer_simulation"]
        self.assertEqual(buffer["rendered_samples"], 640)
        self.assertEqual(buffer["rebuffer_samples"], 160)
        self.assertEqual(buffer["peak_queue_samples"], 240)
        self.assertEqual(buffer["final_partial_source_samples"], 3)
        self.assertEqual(buffer["device_timing"], "not_measured")

    def test_15_features_are_frozen_and_caller_supplied(self) -> None:
        features = self.report["caller_supplied_features"]
        self.assertTrue(features["caller_supplied"])
        self.assertTrue(features["frozen"])
        for key in ("extraction_invoked", "silero_invoked", "opensmile_invoked"):
            self.assertFalse(features[key])
        self.assertEqual(features["feature_dim"], reference.FEATURE_DIM)
        self.assertEqual(len(features["digest"]), 64)
        self.assertEqual(features, {key: value for key, value in
                                    reference.build_feature_bundle().items() if key != "records"})

    def test_16_standardized_head_controls(self) -> None:
        head = self.report["regression_head"]
        combined = head["combined_surrogate_features"]
        self.assertEqual(combined["alpha_grid"], list(reference.ALPHA_GRID))
        self.assertIn(combined["grouped_cv"]["selected_alpha"], reference.ALPHA_GRID)
        self.assertIn("constant_fold_mean_cv_mae", combined["grouped_cv"])
        self.assertIn("held_out_constant_dev_mean", combined)
        self.assertEqual(combined["feature_count"], reference.FEATURE_DIM)
        self.assertEqual(head["acoustic_only_ablation"]["feature_count"], reference.EGE_MAPS_DIM)
        self.assertEqual(head["permuted_target_adverse"]["status"], "measured_synthetic_adverse")
        self.assertTrue(all(fold["outcomes"]["constant_fold_mean"]["mae"] >= 0.0
                            for fold in combined["grouped_cv"]["folds"]))

    def test_17_holding_regressions_are_recorded(self) -> None:
        conditions = {item["condition"] for item in self.report["regressions"]}
        self.assertIn("linear_pitch_changing_control", conditions)
        self.assertIn("held_out_surrogate_head", conditions)
        self.assertIn("permuted_target_adverse", conditions)
        combined = self.report["regression_head"]["combined_surrogate_features"]
        held = next(item for item in self.report["regressions"]
                    if item["condition"] == "held_out_surrogate_head")
        self.assertEqual(held["candidate"], combined["held_out"]["mae"])
        self.assertEqual(held["baseline"], combined["held_out_constant_dev_mean"]["mae"])

    def test_18_adverse_cases_are_rejected(self) -> None:
        for section in ("config", "features", "rate_schedule", "frame", "lifecycle"):
            for name, status in self.report["adverse"][section].items():
                if name == "dsp_state_unchanged":
                    self.assertIs(status, True)
                else:
                    self.assertEqual(status, "rejected", f"{section}.{name}")
        self.assertTrue(self.report["adverse"]["validity"]["unknown_never_counted_as_nonspeech"])

    def test_19_invalid_inputs_raise_directly(self) -> None:
        config = {"alpha": 1000, "feature_dim": reference.FEATURE_DIM,
                  "hop_samples": reference.HOP, "rate_min": "0.75", "rate_max": "1.5"}
        with self.assertRaises(reference.Reject):
            reference.validate_config({key: value for key, value in config.items() if key != "alpha"})
        with self.assertRaises(reference.Reject):
            reference.validate_config({**config, "alpha": -1})
        with self.assertRaises(reference.Reject):
            reference.rate_map(16003, [(0, "1"), (161, "1.25")])
        with self.assertRaises(reference.Reject):
            reference.rate_map(16003, [(0, "3")])
        with self.assertRaises(reference.Reject):
            reference.validate_frame({"samples": [0.0] * 160, "epoch": 2, "position": 320}, 1, 320)
        with self.assertRaises(reference.Reject):
            reference.require_open("finished")
        records = reference.build_feature_bundle()["records"]
        with self.assertRaises(reference.Reject):
            reference.validate_feature_coverage(
                [dict(records[0], features=records[0]["features"][:-1]), *records[1:]])

    def test_20_repeatability_is_byte_identical(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_21_gates_remain_blocked(self) -> None:
        gates = self.report["gates"]
        self.assertEqual({gate["name"] for gate in gates}, set(reference.GATE_REOPEN))
        self.assertTrue(all(gate["status"] == "blocked" and gate["reopen_condition"] for gate in gates))
        self.assertEqual(set(self.report["missing_evidence"]), set(reference.GATE_REOPEN))

    def test_22_source_reported_context_and_non_claims(self) -> None:
        self.assertEqual(self.report["source_reported_context"]["label"],
                         "source_reported_not_measured_here")
        self.assertEqual(self.report["source_reported_context"]["Silero_openSMILE_ridge"]["held_out_mae"],
                         0.991)
        joined = " ".join(self.report["non_claims"]).lower()
        for phrase in ("no silero", "no opensmile", "no listening", "no callback pacing"):
            self.assertIn(phrase, joined)

    def test_23_no_negative_zero_and_no_trailing_whitespace(self) -> None:
        self.assertIsNone(re.search(rb"(?<![0-9.eE])-0\.0(?![0-9])", self.generated))
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".sha256"}:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_24_pins_and_contract_are_strict(self) -> None:
        errors: list[str] = []
        pins = verify.parse_pins(errors)
        verified = verify.check_pin_targets(pins, errors)
        self.assertEqual(errors, [])
        self.assertEqual(verified, len(pins))
        self.assertTrue(verify.check_contract(self.contract, pins, errors))
        self.assertTrue(verify.check_report(self.report, errors))
        self.assertEqual(errors, [])

    def test_25_explicit_spdx_tags(self) -> None:
        result = check_licensing.check()
        self.assertEqual(result["problems"], [])
        self.assertEqual(result["status"], "ok")

    def test_26_scope_is_task_local(self) -> None:
        errors: list[str] = []
        self.assertTrue(verify.check_scope(errors))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
