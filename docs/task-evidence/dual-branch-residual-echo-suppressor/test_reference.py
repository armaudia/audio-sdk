# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
fixture arithmetic, paired echo/near-end processing, block invariance, reset,
caller-asset identity validation and the exact adverse rejection matrix.
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

    def test_room_profile_items_are_synthetic_or_blocked(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "room")
        self.assertEqual(len(profile["required_items"]), 11)
        statuses = {row["status"] for row in profile["required_items"].values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in profile["required_items"].items()
                         if row["status"] == "blocked")
        self.assertEqual(self.report["profile_blockers"], blocked)

    def test_candidate_geometry_is_not_fabricated(self):
        candidate = self.report["candidate"]
        self.assertIsNone(candidate["reported_input_sample_rate_hz"])
        self.assertIsNone(candidate["reported_hop_samples"])
        self.assertIsNone(candidate["reported_render_delay_samples"])
        self.assertFalse(candidate["geometry_documented"])
        self.assertIsNone(candidate["reported_parameter_count"])
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
        for section in ("echo_attenuation", "near_end_preservation",
                        "overlap_double_talk", "double_talk_preservation",
                        "paired_reference_attachment",
                        "no_reference_comparison", "alignment", "nonfinite",
                        "movement_path_change", "final_partial", "streaming",
                        "reset"):
            self.assertIs(self.report[section]["qualifies"], False, section)
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_six_exact_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        identifiers = {row["id"] for row in blockers}
        self.assertIn("pinned_candidate_source_weights_runtime_absent",
                      identifiers)
        self.assertIn("dual_branch_architecture_and_residual_geometry_unverified",
                      identifiers)
        self.assertIn("rights_cleared_paired_cohort_and_double_talk_absent",
                      identifiers)


class EchoNearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_echo_only_attenuation(self):
        attenuation = self.report["echo_attenuation"]
        self.assertEqual(len(attenuation["regions"]), 2)
        for region in attenuation["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertGreater(region["erle_millidb"], 20000)
            self.assertGreater(region["aec_only_erle_millidb"], 20000)
            self.assertGreaterEqual(region["erle_millidb"],
                                    region["aec_only_erle_millidb"])
        self.assertEqual(attenuation["min_erle_millidb"],
                         min(row["erle_millidb"]
                             for row in attenuation["regions"]))

    def test_near_end_preservation(self):
        near = self.report["near_end_preservation"]
        self.assertEqual(len(near["regions"]), 2)
        for region in near["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertGreater(region["near_reference_snr_millidb"], 15000)
            self.assertLess(abs(region["level_change_millidb"]), 500)
            self.assertLess(region["peak_milli"], 1000)
        self.assertEqual(near["nonfinite_output_count"], 0)

    def test_overlap_double_talk(self):
        overlap = self.report["overlap_double_talk"]
        self.assertIs(overlap["qualifies"], False)
        self.assertGreater(overlap["near_reference_snr_millidb"], 0)
        self.assertLess(overlap["peak_milli"], 1000)

    def test_no_reference_control_is_independent(self):
        control = self.report["no_reference_comparison"]
        self.assertIs(control["qualifies"], False)
        self.assertGreater(control["aec_echo_gain_over_control_millidb"],
                           10000)
        self.assertGreater(control["aec_near_reference_snr_millidb"],
                           control["control_near_reference_snr_millidb"])
        self.assertEqual(control["nonfinite_output_count"], 0)

    def test_delayed_and_missing_render_are_detected(self):
        alignment = self.report["alignment"]
        self.assertIs(alignment["qualifies"], False)
        self.assertTrue(alignment["delayed_render_detected"])
        self.assertTrue(alignment["missing_render_detected"])
        self.assertFalse(alignment["missing_render_rejected_before_processing"])
        self.assertTrue(alignment["missing_render_frame_rejected"])
        self.assertFalse(alignment["candidate_alignment_verified"])
        self.assertGreater(alignment["aligned_erle_millidb"],
                           alignment["delayed_render_erle_millidb"] + 6000)
        self.assertGreater(alignment["aligned_erle_millidb"],
                           alignment["missing_render_erle_millidb"] + 6000)

    def test_final_partial_frame(self):
        partial = self.report["final_partial"]
        self.assertEqual(partial["valid_count"], 137)
        self.assertEqual(partial["output_samples"], 160)
        self.assertEqual(partial["advanced_samples"], 137)
        self.assertTrue(partial["padding_zero"])
        self.assertTrue(partial["tail_zero"])
        self.assertEqual(partial["nonfinite_output_count"], 0)

    def test_streaming_and_reset(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertEqual(streaming["accepted_samples"], 16000)
        self.assertEqual(sum(streaming["chunks"]), 16000)
        self.assertFalse(streaming["scheduler_measured"])
        self.assertTrue(self.report["reset"]["matches_fresh"])
        self.assertEqual(self.report["reset"]["epoch"], 2)


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

    def test_config_rejects_wrong_geometry(self):
        config = {"sample_rate_hz": 8000, "channels": 1,
                  "frame_samples": 160, "sample_format": "float32",
                  "clock_ppm": 0, "resampling": "none",
                  "render_delay_samples": 32,
                  "algorithmic_latency_samples": 0}
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_config(config)
        self.assertEqual(caught.exception.code, "unsupported_sample_rate")

    def test_nonfinite_frame_is_rejected_without_state_change(self):
        suppressor = reference.PairedReferenceResidualChain()
        signals = reference.build_fixture()
        suppressor.process_frame(list(signals["mic"][:160]),
                                 list(signals["render"][:160]))
        before = suppressor.state_digest
        with self.assertRaises(reference.ReferenceRejection):
            suppressor.process_frame(
                [float("nan")] + list(signals["mic"][161:320]),
                list(signals["render"][160:320]))
        self.assertEqual(before, suppressor.state_digest)

    def test_nonzero_padding_is_rejected(self):
        suppressor = reference.PairedReferenceResidualChain()
        signals = reference.build_fixture()
        mic = list(signals["mic"][:137]) + [1.0] + list(signals["mic"][138:159])
        render = list(signals["render"][:160])
        with self.assertRaises(reference.ReferenceRejection):
            suppressor.process_frame(mic, render, valid_count=137)

    def test_missing_render_is_rejected(self):
        suppressor = reference.PairedReferenceResidualChain()
        signals = reference.build_fixture()
        with self.assertRaises(reference.ReferenceRejection) as caught:
            suppressor.process_frame(list(signals["mic"][:160]), None)
        self.assertEqual(caught.exception.code, "missing_render")

    def test_epoch_zero_and_negative_are_rejected(self):
        suppressor = reference.PairedReferenceResidualChain(epoch=1)
        for epoch in (0, -1):
            with self.assertRaises(reference.ReferenceRejection):
                suppressor.reset(epoch, 0)

    def test_adverse_matrix_is_complete(self):
        cases = reference.adverse_rejections()
        self.assertEqual(len(cases), 47)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        identifiers = {case["case_id"] for case in cases}
        self.assertIn("config_stereo", identifiers)
        self.assertIn("frame_nonfinite_render", identifiers)
        self.assertIn("frame_missing_render", identifiers)
        self.assertIn("caller_manifest_bad_model_hash", identifiers)

    def test_fixture_validation_rejects_bad_specs(self):
        spec = reference.fixture_spec()
        spec["length_samples"] = 15999
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["echo_taps_before"] = [[4, 1], [0, 1]]
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)

    def test_caller_manifest_is_identity_only(self):
        manifest = {
            "adapter": "dual-branch-residual-echo-suppressor-reference",
            "algorithmic_latency_samples": 0,
            "channels": 1,
            "frame_samples": 160,
            "input_format": "float32",
            "library_path": "/caller/dual-branch-residual-echo-suppressor/lib",
            "library_sha256": "3" * 64,
            "model_path": "/caller/dual-branch-residual-echo-suppressor/model",
            "model_sha256": "0" * 64,
            "render_delay_samples": 32,
            "sample_rate_hz": 16000,
            "source_commit": "0" * 40,
            "source_sha256": "1" * 64,
            "variant": "dual-branch-residual",
            "weights_sha256": "2" * 64,
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertEqual(result, {"validated": True, "loaded": False,
                                  "executed": False, "imported": False})

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
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertIn(reference.TASK_PREFIX + "reference.py",
                      contract["artifact_pins"])


if __name__ == "__main__":
    unittest.main()
