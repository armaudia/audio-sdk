# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-CONV-TASNET package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
fixture arithmetic, mono band-split processing, permutation-pinned SI-SDR,
independent leakage, block invariance, reset, caller-asset identity validation
and the exact adverse rejection matrix.
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402


class ReportIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_disposition_is_defer_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(self.report["qualification"]["qualifies"])

    def test_eight_blocked_release_gates(self):
        gates = self.report["release_gates"]
        self.assertEqual([row["id"] for row in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked" for row in gates))

    def test_spatial_profile_items_are_synthetic_or_blocked(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "spatial")
        self.assertEqual(len(profile["required_items"]), 11)
        statuses = {row["status"] for row in profile["required_items"].values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in profile["required_items"].items()
                         if row["status"] == "blocked")
        self.assertEqual(self.report["profile_blockers"], blocked)
        self.assertIn("task_matched_heldout_labels", blocked)
        self.assertIn("permissions", blocked)

    def test_candidate_geometry_is_not_fabricated(self):
        candidate = self.report["candidate"]
        self.assertIsNone(candidate["reported_parameter_count"])
        self.assertIsNone(candidate["reported_input_sample_rate_hz"])
        self.assertIsNone(candidate["reported_hop_samples"])
        self.assertIsNone(candidate["reported_window_samples"])
        self.assertIsNone(candidate["reported_source_count"])
        self.assertFalse(candidate["geometry_documented"])
        self.assertEqual(candidate["paper_reference"],
                         "https://arxiv.org/abs/1809.07454")
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["runtime_present"])
        self.assertFalse(candidate["exact_numeric_output_present"])

    def test_all_boundary_and_scope_flags_are_false(self):
        self.assertTrue(all(value is False
                            for value in self.report["boundary"].values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_no_result_is_promoted(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        for case in self.report["adverse_rejections"]:
            self.assertEqual(case["status"], "rejected")
            self.assertTrue(case["state_unchanged"])
        for section in ("separation", "permutation", "control", "alignment",
                        "source_order_change", "channel_loss",
                        "final_partial", "streaming", "reset", "nonfinite",
                        "separation_model", "scoring"):
            self.assertIs(self.report[section]["qualifies"], False, section)
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_six_exact_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        identifiers = {row["id"] for row in blockers}
        self.assertIn("pinned_conv_tasnet_source_weights_runtime_absent",
                      identifiers)
        self.assertIn("candidate_io_geometry_and_permutation_unverified",
                      identifiers)
        self.assertIn("rights_cleared_two_speaker_cohort_absent",
                      identifiers)
        self.assertIn("mono_separation_contract_and_sdk_integration_absent",
                      identifiers)


class SeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_two_source_separation_is_bounded(self):
        rows = self.report["separation"]["sources"]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertIs(row["qualifies"], False)
            self.assertGreater(row["evaluation_si_sdr_millidb"], 5000)
            self.assertGreater(row["improvement_millidb"], 5000)
            self.assertLess(row["interference_leakage_millidb"], -10000)
            self.assertLess(abs(row["target_level_change_millidb"]), 1000)
            self.assertLess(row["peak_milli"], 1000)
        self.assertEqual(self.report["separation"]["nonfinite_output_count"], 0)

    def test_mixture_control_is_independent(self):
        control = self.report["control"]
        self.assertEqual(control["name"], "mixture_passthrough")
        self.assertIs(control["qualifies"], False)
        self.assertEqual(len(control["evaluation_si_sdr_millidb"]), 2)

    def test_permutation_is_pinned_on_calibration_only(self):
        permutation = self.report["permutation"]
        self.assertIs(permutation["qualifies"], False)
        self.assertTrue(permutation["score_uses_calibration_permutation"])
        self.assertFalse(permutation["oracle_used_for_score"])
        self.assertTrue(permutation["independently_pinned"])
        self.assertTrue(permutation["matches_oracle"])
        self.assertEqual(permutation["chosen_assignment"],
                         permutation["oracle_evaluation_assignment"])
        self.assertEqual(permutation["chosen_evaluation_sum_millidb"],
                         permutation["oracle_evaluation_sum_millidb"])
        self.assertGreater(permutation["margin_millidb"], 10000)
        self.assertGreater(permutation["chosen_evaluation_sum_millidb"],
                           permutation["swapped_evaluation_sum_millidb"])

    def test_leakage_is_scored_independently_of_permutation(self):
        scoring = self.report["scoring"]
        self.assertEqual(scoring["spec"]["leakage_measure"],
                         "orthogonal_projection_energy_ratio")
        self.assertEqual(scoring["spec"]["permutation_rule"],
                         "max_calibration_integer_correlation_sum")
        self.assertEqual(len(scoring["spec"]["calibration_region"]), 2)
        for row in self.report["separation"]["sources"]:
            self.assertNotEqual(row["interference_leakage_millidb"],
                                row["evaluation_si_sdr_millidb"])

    def test_separation_model_and_scoring_are_pinned_separately(self):
        model = self.report["separation_model"]
        scoring = self.report["scoring"]
        self.assertEqual(model["sha256"],
                         reference.SEPARATION_MODEL_SHA256)
        self.assertEqual(scoring["sha256"],
                         reference.SCORING_PROTOCOL_SHA256)
        self.assertNotEqual(model["sha256"], scoring["sha256"])
        self.assertEqual(
            reference.object_digest(reference.separation_model_spec()),
            model["sha256"])
        self.assertEqual(
            reference.object_digest(reference.scoring_protocol_spec()),
            scoring["sha256"])
        self.assertFalse(model["is_conv_tasnet"])
        self.assertFalse(model["is_learned"])
        self.assertFalse(model["uses_encoder_mask_decoder"])

    def test_alignment_and_source_order_probes(self):
        alignment = self.report["alignment"]
        self.assertEqual(alignment["declared_content_delay_samples"], 12)
        self.assertEqual(alignment["estimated_peak_lag_samples"], 12)
        self.assertTrue(alignment["declared_lag_detected"])
        self.assertTrue(alignment["one_sample_shift_detected"])
        self.assertFalse(alignment["device_timing_measured"])
        order = self.report["source_order_change"]
        self.assertTrue(order["assignment_flips"])
        self.assertFalse(order["room_change_measured"])
        channel = self.report["channel_loss"]
        self.assertFalse(channel["applicable"])
        self.assertFalse(channel["channel_substitution_performed"])

    def test_streaming_reset_and_partial(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertTrue(streaming["low_all_match"])
        self.assertTrue(streaming["high_all_match"])
        self.assertEqual(streaming["accepted_samples"],
                         reference.FIXTURE_LENGTH)
        self.assertEqual(sum(streaming["chunks"]),
                         reference.FIXTURE_LENGTH)
        self.assertFalse(streaming["scheduler_measured"])
        self.assertTrue(self.report["reset"]["matches_fresh"])
        self.assertEqual(self.report["reset"]["epoch"], 2)
        partial = self.report["final_partial"]
        self.assertEqual(partial["valid_count"], 137)
        self.assertEqual(partial["output_samples"], 160)
        self.assertEqual(partial["advanced_samples"], 137)
        self.assertTrue(partial["low_tail_zero"])
        self.assertTrue(partial["high_tail_zero"])

    def test_nonfinite_is_not_promoted(self):
        nonfinite = self.report["nonfinite"]
        self.assertEqual(nonfinite["output_nonfinite_count"], 0)
        self.assertTrue(nonfinite["output_finite"])
        self.assertGreaterEqual(nonfinite["rejected_nonfinite_inputs"], 2)
        self.assertIs(nonfinite["qualifies"], False)


class StrictInputTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":NaN}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":Infinity}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('[1,2]')

    def test_config_rejects_wrong_geometry(self):
        config = {"sample_rate_hz": 8000, "channels": 1,
                  "frame_samples": 160, "sample_format": "float32",
                  "separated_source_count": 2, "clock_ppm": 0,
                  "resampling": "none"}
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_config(config)
        self.assertEqual(caught.exception.code, "unsupported_sample_rate")

    def test_nonfinite_frame_is_rejected_without_state_change(self):
        separator = reference.BandSplitSeparator()
        fixture = reference.build_fixture()
        frame = [float(value) for value in fixture["mixture"][:160]]
        separator.process_frame(frame)
        before = separator.state_digest
        with self.assertRaises(reference.ReferenceRejection):
            separator.process_frame([float("nan")] + frame[1:])
        self.assertEqual(before, separator.state_digest)

    def test_nonzero_padding_is_rejected(self):
        separator = reference.BandSplitSeparator()
        fixture = reference.build_fixture()
        frame = [float(value) for value in fixture["mixture"][:137]]
        frame += [1.0] + [0.0] * (160 - 138)
        with self.assertRaises(reference.ReferenceRejection):
            separator.process_frame(frame, valid_count=137)

    def test_missing_input_is_rejected(self):
        separator = reference.BandSplitSeparator()
        with self.assertRaises(reference.ReferenceRejection) as caught:
            separator.process_frame(None)
        self.assertEqual(caught.exception.code, "missing_input")

    def test_epoch_zero_and_negative_are_rejected(self):
        separator = reference.BandSplitSeparator(epoch=1)
        for epoch in (0, -1):
            with self.assertRaises(reference.ReferenceRejection):
                separator.reset(epoch, 0)

    def test_adverse_matrix_is_complete(self):
        cases = reference.adverse_rejections()
        self.assertEqual(len(cases), 60)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        identifiers = {case["case_id"] for case in cases}
        self.assertIn("config_stereo", identifiers)
        self.assertIn("frame_nonfinite_input", identifiers)
        self.assertIn("caller_manifest_bad_model_hash", identifiers)
        self.assertIn("model_learned_claim", identifiers)
        self.assertIn("scoring_oracle_claim", identifiers)
        self.assertIn("chunk_sum_mismatch", identifiers)

    def test_fixture_validation_rejects_bad_specs(self):
        spec = reference.fixture_spec()
        spec["length_samples"] = 7999
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["filter_taps"] = [0] * len(reference.FILTER_TAPS)
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["evaluation_region"] = [1000, 8000]
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)

    def test_caller_manifest_is_identity_only(self):
        manifest = {
            "adapter": "conv-tasnet-reference",
            "algorithmic_latency_samples": 0,
            "channels": 1,
            "frame_samples": 160,
            "input_format": "float32",
            "library_path": "/caller/conv-tasnet/lib",
            "library_sha256": "3" * 64,
            "model_path": "/caller/conv-tasnet/model",
            "model_sha256": "0" * 64,
            "sample_rate_hz": 16000,
            "separated_source_count": 2,
            "source_commit": "0" * 40,
            "source_sha256": "1" * 64,
            "variant": "conv-tasnet-2spk",
            "weights_sha256": "2" * 64,
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertEqual(result, {"validated": True, "loaded": False,
                                  "executed": False, "imported": False,
                                  "declaration_only": True,
                                  "candidate_geometry_verified": False})

    def test_canonical_json_is_stable(self):
        value = {"b": [1, 2], "a": {"z": "x"}}
        text = reference.canonical_text(value)
        self.assertEqual(text, '{"a":{"z":"x"},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         reference.sha256_bytes(text.encode("utf-8")))


class DeterminismTests(unittest.TestCase):
    def test_three_builds_are_byte_identical(self):
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)
        self.assertEqual(reference.sha256_bytes(texts[0].encode("utf-8")),
                         reference.sha256_bytes(texts[1].encode("utf-8")))

    def test_stable_board_identity(self):
        row = reference.board_row()
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         reference.BOARD_ROW_STABLE_SHA256)

    def test_contract_matches_report(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["verification_profile"], "spatial")
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertEqual(contract["separation_model"],
                         report["separation_model"])
        self.assertEqual(contract["scoring"], report["scoring"])
        self.assertIn(reference.TASK_PREFIX + "reference.py",
                      contract["artifact_pins"])


if __name__ == "__main__":
    unittest.main()
