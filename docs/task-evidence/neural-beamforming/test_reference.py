# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the SDK-NEURAL-BEAMFORMING evidence package.

Run from this directory::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py

The tests exercise exact fixture arithmetic, the fixed absence probe,
structural mask/plan validation, every bounded rejection and the
DEFER/not-qualified invariants.  No neural beamformer is executed and no
network, model, runtime or audio file is used.
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402

CONTROLS = ("identity", "delay_and_sum")


class GeometryTests(unittest.TestCase):
    def test_fixture_geometry_is_exact(self) -> None:
        geometry = reference.fixture_geometry()
        self.assertEqual(geometry["reference_mic_id"], "m0")
        self.assertEqual(len(geometry["microphones"]), 4)
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        delays = reference.steering_delays(geometry)
        by_id = {item["mic_id"]: item["relative_q16"] for item in delays}
        self.assertEqual(by_id, {"m0": 0, "m1": -196608,
                                 "m2": -65536, "m3": -262144})
        for item in delays:
            self.assertTrue(item["exact_integer_sample"])
            self.assertEqual(item["relative_q16"] % reference.Q16, 0)

    def test_fixture_is_byte_deterministic(self) -> None:
        first = reference.build_fixture()
        second = reference.build_fixture()
        self.assertEqual(first["fixture_digest"], second["fixture_digest"])
        for key in ("identity_control", "delay_and_sum_control"):
            self.assertEqual(reference.canonical_text(first[key]),
                             reference.canonical_text(second[key]))

    def test_controls_recover_the_click_and_do_not_qualify(self) -> None:
        built = reference.build_fixture()
        identity = built["identity_control"]
        delay_and_sum = built["delay_and_sum_control"]
        self.assertEqual(identity["peak_value_exact"], "1548/1")
        self.assertEqual(delay_and_sum["peak_value_exact"], "3049/2")
        for control in (identity, delay_and_sum):
            self.assertFalse(control["is_neural_beamformer"])
            self.assertFalse(control["model_weights"])
            self.assertFalse(control["mask_applied"])
            self.assertFalse(control["spatial_loss_used"])
            self.assertEqual(control["status"],
                             "control_only_not_qualified")
            self.assertEqual(control["qualification_status"],
                             "not_qualified")
            self.assertEqual(control["peak_index"],
                             reference.fixture_click_index())
            self.assertEqual(len(control["output_exact"]),
                             reference.FRAME_SAMPLES)
            self.assertEqual(reference.object_digest(control["output_exact"]),
                             control["output_digest"])

    def test_neural_output_is_absent(self) -> None:
        built = reference.build_fixture()
        output = built["neural_output"]
        self.assertFalse(output["present"])
        self.assertFalse(output["executed"])
        self.assertIsNone(output["result"])
        self.assertEqual(output["status"], "blocked")


class MaskTests(unittest.TestCase):
    def test_fixture_mask_is_structural_only(self) -> None:
        mask = reference.fixture_mask_manifest()
        self.assertEqual(mask["frames"], 2)
        self.assertEqual(mask["bins"], 3)
        self.assertEqual(mask["mask_group"], "oracle")

    def test_mask_rejects_mixed_group(self) -> None:
        document = reference.fixture_mask_manifest()
        document["mask_group"] = "oracle+estimated"
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_mask_manifest(document)
        self.assertEqual(str(caught.exception),
                         "mixed_mask_group_not_permitted")

    def test_mask_rejects_out_of_range(self) -> None:
        for value in (-0.01, 1.01):
            document = reference.fixture_mask_manifest()
            document["values"][0][0] = value
            with self.assertRaises(reference.Reject) as caught:
                reference.parse_mask_manifest(document)
            self.assertEqual(str(caught.exception), "invalid_mask_value")

    def test_mask_rejects_nonfinite_and_shape(self) -> None:
        document = reference.fixture_mask_manifest()
        document["values"][0][0] = float("nan")
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_mask_manifest(document)
        self.assertEqual(str(caught.exception), "nonfinite_mask_value")

        document = reference.fixture_mask_manifest()
        document["values"][0] = document["values"][0][:-1]
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_mask_manifest(document)
        self.assertEqual(str(caught.exception), "mask_shape_mismatch")


class PlanTests(unittest.TestCase):
    def test_no_plan_is_present_in_the_package(self) -> None:
        readiness = reference.plan_readiness(None)
        self.assertFalse(readiness["present"])
        self.assertFalse(readiness["executed"])
        self.assertEqual(readiness["status"], "blocked")
        self.assertEqual(readiness["qualification_status"], "not_qualified")
        self.assertIn("licensed_neural_beamformer_source_and_weights",
                      readiness["missing"])

    def test_structural_plan_never_qualifies(self) -> None:
        plan = reference._structure_sample_plan()
        readiness = reference.plan_readiness(plan)
        self.assertTrue(readiness["present"])
        self.assertFalse(readiness["executed"])
        self.assertEqual(readiness["status"],
                         "structurally_complete_not_executed")
        self.assertEqual(readiness["qualification_status"], "not_qualified")
        self.assertIn("staged_licensed_source_asset_and_weights",
                      readiness["missing"])

    def test_plan_rejects_invalid_source_weights_and_target(self) -> None:
        plan = reference._structure_sample_plan()
        plan["source_sha256"] = "not-a-digest"
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_neural_plan(plan)
        self.assertEqual(str(caught.exception),
                         "invalid_plan_source_digest")

        plan = reference._structure_sample_plan()
        plan["weights_sha256"] = "not-a-digest"
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_neural_plan(plan)
        self.assertEqual(str(caught.exception),
                         "invalid_plan_weights_digest")

        plan = reference._structure_sample_plan()
        plan["target_definition"] = "undeclared"
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_neural_plan(plan)
        self.assertEqual(str(caught.exception),
                         "invalid_plan_target_definition")

    def test_plan_rejects_inconsistent_mask(self) -> None:
        plan = reference._structure_sample_plan()
        plan["beamformer_kind"] = "end_to_end"
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_neural_plan(plan)
        self.assertEqual(str(caught.exception),
                         "inconsistent_plan_mask_group")


class AbsenceTests(unittest.TestCase):
    def test_fixed_absence_probe_is_all_absent(self) -> None:
        evidence = reference.absence_evidence()
        self.assertTrue(evidence["fixed_probe_list_only"])
        self.assertGreaterEqual(evidence["probe_count"], 20)
        self.assertEqual(evidence["present_count"], 0)
        self.assertTrue(evidence["all_absent"])
        self.assertFalse(evidence["network_used"])
        self.assertFalse(evidence["download_attempted"])
        for probe in evidence["probes"]:
            self.assertFalse(probe["present"])
            self.assertIn(probe["scope"],
                          {"workspace", "sdk_worktree", "home_cache"})


class RejectionTests(unittest.TestCase):
    def test_every_adverse_case_is_rejected(self) -> None:
        records = reference.adverse_rejections()
        self.assertGreaterEqual(len(records), 40)
        for record in records:
            self.assertEqual(record["status"], "rejected")
            self.assertTrue(record["state_unchanged"])

    def test_strict_json_rejections(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.parse_strict_json('{"a":1,"a":2}')
        with self.assertRaises(reference.Reject):
            reference.parse_strict_json('{"a":NaN}')
        with self.assertRaises(reference.Reject):
            reference.parse_strict_json('{"a":}')


class ReportTests(unittest.TestCase):
    def test_report_disposition(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualifies"])
        self.assertFalse(report["qualification"]["neural_output_present"])
        self.assertFalse(report["candidate_execution"]["present"])
        self.assertFalse(report["candidate_execution"]["executed"])
        self.assertEqual(report["distortion_comparison"]["status"], "blocked")
        self.assertIsNone(report["distortion_comparison"]["value"])
        self.assertEqual(set(report["control_baselines"]), set(CONTROLS))
        for label in CONTROLS:
            body = report["control_baselines"][label]["control"]
            self.assertFalse(body["is_neural_beamformer"])
            self.assertEqual(body["qualification_status"], "not_qualified")

    def test_eight_blocked_release_gates(self) -> None:
        gates = reference.build_report()["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(len(reference.build_report()["exact_blockers"]), 8)

    def test_report_is_repeatable(self) -> None:
        first = reference.build_report()
        second = reference.build_report()
        self.assertEqual(reference.canonical_report(first),
                         reference.canonical_report(second))

    def test_board_row_excludes_mutable_fields(self) -> None:
        row = reference.board_row()
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertNotIn("status", row["stable_fields"])
        self.assertNotIn("owner", row["stable_fields"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])

    def test_source_and_boundary_pins_are_live(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            self.assertEqual(
                reference.file_digest(reference.SOURCE_ROOT / path), digest)
        for path, digest in reference.BOUNDARY_PINS.items():
            self.assertEqual(
                reference.file_digest(reference.SDK_ROOT / path), digest)


if __name__ == "__main__":
    unittest.main()
