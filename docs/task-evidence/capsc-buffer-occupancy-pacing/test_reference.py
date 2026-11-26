# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library tests for the CAPSC DEFER evidence package.

These tests exercise the deterministic synthetic controls, the fail-closed
admission manifest, exact provenance pins, the task-local contract/report
disposition and the canonical report bytes. They are not CAPSC, audio, device,
benchmark or release evidence.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_bytes_sorted_and_ascii(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": "\u00d7"})
        self.assertEqual(payload, b'{"a":"\\u00d7","b":1}\n')

    def test_strict_json_rejects_duplicate_and_nonfinite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "x.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
            path.write_text('{"a":1.5}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)


class ControllerTests(unittest.TestCase):
    def step(self, queued: int, last: int = 1000000) -> dict:
        return reference.controller_step({
            "queued_samples": queued,
            "target_samples": reference.GEOMETRY["target_samples"],
            "last_rate_ppm": last,
        })

    def test_nominal_is_exactly_1x(self) -> None:
        command = self.step(reference.GEOMETRY["target_samples"])
        self.assertEqual(command["debt_samples"], 0)
        self.assertEqual(command["commanded_ppm"], 1000000)
        self.assertFalse(command["clamped"])
        self.assertFalse(command["slew_limited"])
        self.assertFalse(command["qualifies"])

    def test_excess_increases_and_deficit_decreases(self) -> None:
        self.assertGreater(self.step(3360)["commanded_ppm"], 1000000)
        self.assertLess(self.step(3040)["commanded_ppm"], 1000000)

    def test_rate_bounds_and_slew(self) -> None:
        high = reference.controller_step({
            "queued_samples": 12800,
            "target_samples": 3200,
            "last_rate_ppm": 1000000,
        })
        self.assertLessEqual(high["commanded_ppm"],
                             reference.GEOMETRY["rate_max_ppm"])
        self.assertLessEqual(high["commanded_ppm"] - 1000000, 50)
        low = reference.controller_step({
            "queued_samples": 0,
            "target_samples": 3200,
            "last_rate_ppm": 1050000,
        })
        self.assertGreaterEqual(low["commanded_ppm"],
                                reference.GEOMETRY["rate_min_ppm"])
        self.assertEqual(low["commanded_ppm"], 1049950)
        self.assertTrue(low["slew_limited"])

    def test_queue_debt_identity(self) -> None:
        self.assertEqual(reference.queue_debt(3360, 3200), 160)
        self.assertEqual(reference.queue_debt(0, 3200), -3200)
        with self.assertRaises(ValueError):
            reference.queue_debt(-1, 3200)
        with self.assertRaises(ValueError):
            reference.queue_debt(0, 0)

    def test_invalid_controls_are_all_rejected(self) -> None:
        controls = reference.invalid_controls()
        summary = controls["summary"]
        self.assertGreaterEqual(summary["case_count"], 18)
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertEqual(summary["accepted_count"], 0)
        self.assertTrue(summary["all_codes_match"])
        self.assertTrue(summary["nonfinite_rejected"])
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["qualifies"])
        for case in controls["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["observed_code"], case["expected_code"])
            self.assertTrue(case["state_unchanged"])
            self.assertFalse(case["qualifies"])


class PlayoutTests(unittest.TestCase):
    def test_steady_has_no_underrun_or_overflow(self) -> None:
        result = reference.playout_trace({
            "arrivals": [160] * 20,
            "initial_queued_samples": 3200,
            "target_samples": 3200,
            "capacity_samples": 9600,
        })
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["underrun_count"], 0)
        self.assertEqual(result["recovery_count"], 0)
        self.assertGreater(result["peak_queued_samples"], 0)

    def test_underrun_and_recovery_are_recorded(self) -> None:
        result = reference.playout_trace({
            "arrivals": [0] * 25 + [4000] + [160] * 10,
            "initial_queued_samples": 3200,
            "target_samples": 3200,
            "capacity_samples": 9600,
        })
        self.assertGreaterEqual(result["underrun_count"], 1)
        self.assertGreaterEqual(result["recovery_count"], 1)
        self.assertGreaterEqual(result["rebuffer_ticks"], 1)
        self.assertNotEqual(result["queue_debt_samples"], "")
        kinds = {event["kind"] for event in result["events"]}
        self.assertIn("underrun", kinds)
        self.assertIn("recovery", kinds)
        self.assertFalse(result["qualifies"])

    def test_overflow_rejects_whole_arrival(self) -> None:
        result = reference.playout_trace({
            "arrivals": [5000] * 5,
            "initial_queued_samples": 3200,
            "target_samples": 3200,
            "capacity_samples": 9600,
        })
        self.assertEqual(result["status"], "overflow")
        overflow = [event for event in result["events"]
                    if event["kind"] == "overflow"]
        self.assertEqual(len(overflow), 1)
        self.assertFalse(overflow[0]["accepted"])

    def test_nonfinite_arrival_rejected(self) -> None:
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(ValueError):
                reference.playout_trace({
                    "arrivals": [160, value],
                    "initial_queued_samples": 3200,
                    "target_samples": 3200,
                    "capacity_samples": 9600,
                })

    def test_separation_control(self) -> None:
        result = reference.separation_control()
        self.assertEqual(result["distinct_command_sequences"], 1)
        self.assertFalse(result["labels_affect_command"])
        self.assertFalse(result["controller_reads_label"])
        self.assertTrue(result["estimator_separate"])
        self.assertFalse(result["estimator_executed"])
        self.assertFalse(result["qualifies"])

    def test_final_partial_window(self) -> None:
        result = reference.final_partial_control()
        cases = {case["source_samples"]: case for case in result["cases"]}
        self.assertFalse(cases[16000]["partial"])
        self.assertTrue(cases[16001]["partial"])
        self.assertEqual(cases[16165]["final_window_samples"], 5)


class AdmissionTests(unittest.TestCase):
    def test_all_mutations_rejected(self) -> None:
        controls = reference.admission_controls()
        summary = controls["summary"]
        self.assertGreaterEqual(summary["case_count"], 50)
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertTrue(summary["all_codes_match"])
        self.assertFalse(summary["state_advanced_on_rejection"])
        for case in controls["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["observed_code"], case["expected_code"])
            self.assertFalse(case["qualifies"])

    def test_control_schema_valid_but_never_admitted(self) -> None:
        control = reference.admission_controls()["control"]
        self.assertTrue(control["schema_valid"])
        self.assertTrue(control["accepted"])
        self.assertFalse(control["admitted"])
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["reason"], "capsc_artifact_absent")
        self.assertFalse(control["vendor_runtime_loaded"])
        self.assertFalse(control["audio_read"])

    def test_unknown_scope_registration_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["scope"]["provider_registration"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)


class ProvenanceTests(unittest.TestCase):
    def test_presence_is_absent(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["candidate_note_present"])
        self.assertEqual(presence["present_probes"], [])
        self.assertFalse(presence["capsc_artifact_present"])
        self.assertFalse(presence["capsc_paper_present"])
        self.assertFalse(
            presence["exact_licensed_source_runtime_present"])
        self.assertFalse(presence["network_used"])
        self.assertFalse(presence["download_attempted"])
        self.assertTrue(presence["presence_is_not_admission"])

    def test_candidate_note_records_only_provenance(self) -> None:
        note = reference.candidate_note_probe()
        self.assertTrue(note["present"])
        self.assertTrue(note["records_capsc_doi"])
        self.assertTrue(note["records_publisher_403"])
        self.assertFalse(note["records_implementation_source"])
        self.assertFalse(note["records_numeric_geometry"])
        self.assertFalse(note["reproduced_here"])
        self.assertFalse(note["qualifies"])
        self.assertEqual(note["capsc_main_line"], 922)
        self.assertEqual(note["capsc_prior_art_line"], 981)
        self.assertEqual(note["capsc_reference_line"], 1046)

    def test_debt_controller_is_research_not_capsc(self) -> None:
        guard = reference.debt_controller_guard()
        self.assertTrue(guard["formulation_is_research_not_capsc"])
        self.assertTrue(guard["generic_p_control_is_not_section_8_6"])
        self.assertFalse(guard["capsc_source_used"])
        self.assertFalse(guard["used_in_this_package"])
        self.assertTrue(guard["patent_risk_recorded"])
        self.assertFalse(guard["qualifies"])

    def test_pins_verify(self) -> None:
        source, boundary, sibling = reference.verify_pins()
        for group in (source, boundary, sibling):
            for relative, row in group.items():
                self.assertTrue(row["verified"], relative)
                self.assertNotEqual(reference.BOARD_TASK_ROW, relative)

    def test_board_projection_has_only_stable_fields(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(set(projection), set(reference.BOARD_ROW_FIELDS))
        for field in reference.BOARD_STATUS_FIELDS:
            self.assertNotIn(field, projection)
        self.assertEqual(reference.board_row_digest(projection),
                         reference.object_digest(projection))


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_disposition_and_gates(self) -> None:
        reference.validate_contract(self.contract)
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertEqual(len(self.contract["release_gates"]), 8)
        for gate in self.contract["release_gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
        self.assertEqual(
            self.contract["qualification"]["status"], "not_qualified")
        self.assertEqual(
            self.contract["qualification"]["qualifying_results"], 0)

    def test_report_identity_and_copies(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))
        for key in ("disposition", "qualification", "scope", "boundary",
                    "public_v0_geometry", "non_claims", "observed_provenance",
                    "documented_parameter_envelope",
                    "synthetic_control_envelope", "required_artifacts",
                    "exact_blockers", "required_results", "reproduction",
                    "debt_controller_guard"):
            self.assertEqual(self.report[key], self.contract[key], key)
        self.assertEqual(self.report["gates"],
                         self.contract["release_gates"])
        self.assertEqual(self.report["rate_profile"]["rows"],
                         self.contract["rate_profile_requirements"])
        self.assertEqual(self.report["rate_outcomes"]["rows"],
                         self.contract["rate_outcomes"])

    def test_report_is_integer_only_and_canonical(self) -> None:
        reference._no_floats(self.report)
        payload = reference.canonical_bytes(self.report)
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(payload.decode("ascii"), text)
        self.assertEqual(reference.sha256_bytes(payload), digest)
        self.assertNotIn(b"NaN", payload)
        self.assertNotIn(b"Infinity", payload)

    def test_required_artifacts_and_blockers(self) -> None:
        self.assertEqual(len(self.report["required_artifacts"]), 9)
        for row in self.report["required_artifacts"]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertFalse(row["admitted"])
            self.assertTrue(row["blocked"])
        self.assertEqual(len(self.report["exact_blockers"]), 6)
        artifact_ids = {row["id"] for row in self.report["required_artifacts"]}
        for blocker in self.report["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)

    def test_committed_report_matches(self) -> None:
        report_path = HERE / "report.json"
        sidecar = HERE / "report.json.sha256"
        if not report_path.is_file() or not sidecar.is_file():
            self.skipTest("report not generated yet")
        payload = report_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(sidecar.read_text(encoding="ascii"),
                         f"{digest}  report.json\n")
        self.assertEqual(payload, reference.canonical_bytes(self.report))
        self.assertEqual(report_path.read_bytes(),
                         reference.canonical_bytes(
                             reference.read_strict_json(report_path)))


if __name__ == "__main__":
    unittest.main()
