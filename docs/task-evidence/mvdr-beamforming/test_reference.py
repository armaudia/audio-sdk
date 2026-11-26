# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the SDK-MVDR-BEAMFORMING evidence package.

Run from this directory::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py

The tests exercise exact fixture arithmetic, structural mask/plan validation,
every bounded rejection and the DEFER/not-qualified invariants.  No MVDR
beamformer is executed and no network, model, runtime or audio file is used.
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402


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
        self.assertEqual(reference.canonical_text(first["control"]),
                         reference.canonical_text(second["control"]))

    def test_control_is_not_mvdr(self) -> None:
        built = reference.build_fixture()
        control = built["control"]
        self.assertFalse(control["is_mvdr"])
        self.assertFalse(control["mask_applied"])
        self.assertFalse(control["covariance_used"])
        self.assertEqual(control["status"], "control_only_not_qualified")
        self.assertEqual(control["qualification_status"], "not_qualified")
        self.assertEqual(control["peak_index"],
                         reference.fixture_click_index())
        self.assertEqual(len(control["output_exact"]), reference.FRAME_SAMPLES)
        self.assertEqual(reference.object_digest(control["output_exact"]),
                         control["output_digest"])

    def test_mvdr_output_is_absent(self) -> None:
        built = reference.build_fixture()
        output = built["mvdr_output"]
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
        self.assertIn("licensed_mvdr_source_and_runtime",
                      readiness["missing"])

    def test_structural_plan_never_qualifies(self) -> None:
        plan = reference._structure_sample_plan()
        readiness = reference.plan_readiness(plan)
        self.assertTrue(readiness["present"])
        self.assertFalse(readiness["executed"])
        self.assertEqual(readiness["status"],
                         "structurally_complete_not_executed")
        self.assertEqual(readiness["qualification_status"], "not_qualified")
        self.assertIn("staged_licensed_source_asset", readiness["missing"])

    def test_plan_rejects_invalid_source_and_covariance(self) -> None:
        plan = reference._structure_sample_plan()
        plan["source_sha256"] = "not-a-digest"
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_mvdr_plan(plan)
        self.assertEqual(str(caught.exception),
                         "invalid_plan_source_digest")

        plan = reference._structure_sample_plan()
        plan["covariance"]["rank"] = 0
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_mvdr_plan(plan)
        self.assertEqual(str(caught.exception), "invalid_plan_rank")


class RejectionTests(unittest.TestCase):
    def test_every_adverse_case_is_rejected(self) -> None:
        records = reference.adverse_rejections()
        self.assertGreaterEqual(len(records), 30)
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
        self.assertFalse(report["qualification"]["mvdr_output_present"])
        self.assertFalse(report["candidate_execution"]["present"])
        self.assertFalse(report["candidate_execution"]["executed"])
        self.assertEqual(report["distortion_comparison"]["status"], "blocked")
        self.assertIsNone(report["distortion_comparison"]["value"])

    def test_eight_blocked_release_gates(self) -> None:
        gates = reference.build_report()["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

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


if __name__ == "__main__":
    unittest.main()
