# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local USC mrate evidence package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import reference


class JsonTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_nan_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":NaN}')

    def test_strict_json_rejects_non_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")

    def test_canonical_json_normalizes_negative_zero(self) -> None:
        self.assertEqual(reference.canonical_bytes({"v": -0.0}),
                         b'{"v":0.0}')


class IdentityTests(unittest.TestCase):
    def test_identity_is_linked_row_only(self) -> None:
        identity = reference.task_row_identity()
        self.assertIs(identity["whole_file_hashed"], False)
        self.assertEqual(identity["source"],
                         "audio-benchmark-platform/plan/swarm/TASKS.json")
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(
            identity["stable_sha256"],
            reference.sha256(
                reference.canonical_bytes(identity["stable_fields"])))

    def test_identity_matches_contract(self) -> None:
        identity = reference.task_row_identity()
        contract = json.loads((reference.HERE / "contract.json").read_text())
        self.assertEqual(contract["task_row_identity"]["stable_sha256"],
                         identity["stable_sha256"])
        self.assertIs(contract["task_row_identity"]["whole_file_hashed"], False)

    def test_mutable_fields_are_excluded(self) -> None:
        identity = reference.task_row_identity()
        for field in ("owner", "status", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, identity["stable_fields"])
            self.assertIn(field, identity["excluded_mutable_fields"])

    def test_claim_matches_pinned_base(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["claim"]["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        self.assertEqual(identity["claim"]["reviewer"], reference.REVIEWER)

    def test_no_tasks_json_pin(self) -> None:
        report = reference.build_report()
        labels = set(report["source_pins"]) | set(report["boundary_pins"])
        self.assertFalse(any(label.endswith("TASKS.json") for label in labels))


class SourceAuditTests(unittest.TestCase):
    def test_pinned_source_tree_digest(self) -> None:
        root = reference.SOURCE_ROOT / reference.SOURCE_RATE_REL
        if not root.is_dir():
            self.skipTest("extracted source tree is absent")
        self.assertEqual(reference.source_tree_digest(root),
                         reference.SOURCE_TREE_SHA256)

    def test_observed_file_pins_match_tree(self) -> None:
        root = reference.SOURCE_ROOT / reference.SOURCE_RATE_REL
        if not root.is_dir():
            self.skipTest("extracted source tree is absent")
        for relative, digest in reference.OBSERVED_SOURCE_FILES:
            path = root / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256(path.read_bytes()), digest)

    def test_source_pins_cover_the_observed_tree(self) -> None:
        pinned = {
            path for path in reference.SOURCE_PINS
            if path.startswith(reference.SOURCE_RATE_REL + "/")}
        expected = {
            reference.SOURCE_RATE_REL + "/" + relative
            for relative, _ in reference.OBSERVED_SOURCE_FILES}
        self.assertEqual(pinned, expected)

    def test_audit_is_consistent(self) -> None:
        audit = reference.audit_assets()
        self.assertIs(audit["archive_present"], False)
        self.assertIs(audit["source_checkout_present"], True)
        self.assertIs(audit["source_tree_matches_pins"], True)
        self.assertIs(audit["rights_record_present"], False)
        self.assertIs(audit["runtime_present"], False)
        self.assertIs(audit["observed_source_files_match_pins"], True)
        self.assertEqual(audit["observed_source_file_count"], 21)

    def test_source_readme_has_no_license_grant(self) -> None:
        readme = (reference.SOURCE_ROOT / reference.SOURCE_RATE_REL
                  / "doc/README")
        if not readme.is_file():
            self.skipTest("source README is absent")
        text = readme.read_text(encoding="utf-8", errors="replace").lower()
        for token in ("license", "copyright", "redistribution"):
            self.assertNotIn(token, text)
        self.assertIn("windows xp", text)
        self.assertIn("matlab 7.01", text)


class GeometryTests(unittest.TestCase):
    def test_geometry_accepts_v0(self) -> None:
        self.assertEqual(
            reference.validate_geometry(16000, 1, 160),
            {"sample_rate_hz": 16000, "channels": 1,
             "frame_samples": 160})

    def test_geometry_rejects_wrong_rate(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_geometry(44100, 1, 160)

    def test_geometry_rejects_stereo(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_geometry(16000, 2, 160)

    def test_geometry_rejects_wrong_frame(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_geometry(16000, 1, 512)

    def test_frame_plan_partial_tail(self) -> None:
        plan = reference.map_frames(reference.CONTROL_TOTAL_SAMPLES)
        self.assertEqual(plan["frame_count"], 401)
        self.assertEqual(plan["partial_samples"], 77)
        self.assertEqual(plan["last_frame"]["start_sample"], 64000)
        self.assertEqual(plan["last_frame"]["end_sample"], 64077)
        self.assertEqual(plan["last_frame"]["samples"], 77)

    def test_frame_plan_rejects_zero(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.map_frames(0)

    def test_frame_plan_rejects_float(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.map_frames(64077.0)

    def test_frame_plan_rejects_boolean(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.map_frames(True)

    def test_frame_plan_rejects_over_cap(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.map_frames(reference.MAX_TOTAL_SAMPLES + 1)


class TraceTests(unittest.TestCase):
    def test_control_trace_length(self) -> None:
        self.assertEqual(len(reference.synthetic_trace()),
                         reference.CONTROL_FRAME_COUNT)

    def test_exact_events_and_rate(self) -> None:
        mapped = reference.detect_nuclei(
            reference.synthetic_trace(), reference.CONTROL_TOTAL_SAMPLES,
            active_samples=reference.CONTROL_ACTIVE_SAMPLES)
        self.assertEqual(mapped["nucleus_count"], 12)
        self.assertEqual(mapped["syllables_per_second_fraction"], "4")
        self.assertEqual(mapped["syllables_per_second"], 4.0)
        self.assertEqual(mapped["events"][0],
                         {"index": 5, "start_sample": 800,
                          "end_sample": 960, "time_ms": 50, "score": 0.9})
        self.assertEqual(mapped["events"][-1]["start_sample"], 64000)
        self.assertEqual(mapped["events"][-1]["end_sample"], 64077)

    def test_subthreshold_spikes_never_count(self) -> None:
        mapped = reference.detect_nuclei(
            reference.synthetic_trace(), reference.CONTROL_TOTAL_SAMPLES)
        indices = {event["index"] for event in mapped["events"]}
        for index in reference.CONTROL_SUBTHRESHOLD_FRAMES:
            self.assertNotIn(index, indices)

    def test_silence_yields_zero_events(self) -> None:
        mapped = reference.detect_nuclei(
            [0.0] * reference.CONTROL_FRAME_COUNT,
            reference.CONTROL_TOTAL_SAMPLES)
        self.assertEqual(mapped["nucleus_count"], 0)
        self.assertEqual(mapped["syllables_per_second"], 0.0)

    def test_minimum_separation_suppresses_second_peak(self) -> None:
        mapped = reference.detect_nuclei(
            reference._refractory_trace(), reference.CONTROL_TOTAL_SAMPLES)
        self.assertEqual(mapped["nucleus_count"], 1)
        self.assertEqual(mapped["events"][0]["index"], 100)

    def test_missing_trace_value_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                reference._trace_with_missing(),
                reference.CONTROL_TOTAL_SAMPLES)

    def test_nan_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                [math.nan] * reference.CONTROL_FRAME_COUNT,
                reference.CONTROL_TOTAL_SAMPLES)

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                [math.inf] * reference.CONTROL_FRAME_COUNT,
                reference.CONTROL_TOTAL_SAMPLES)

    def test_out_of_range_rejected(self) -> None:
        for value in (-0.1, 1.1):
            with self.assertRaises(reference.Reject):
                reference.detect_nuclei(
                    [value] * reference.CONTROL_FRAME_COUNT,
                    reference.CONTROL_TOTAL_SAMPLES)

    def test_boolean_and_string_rejected(self) -> None:
        for value in (True, "0.5"):
            with self.assertRaises(reference.Reject):
                reference.detect_nuclei(
                    [value] * reference.CONTROL_FRAME_COUNT,
                    reference.CONTROL_TOTAL_SAMPLES)

    def test_count_mismatch_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                [0.1] * 3, reference.CONTROL_TOTAL_SAMPLES)

    def test_active_samples_above_total_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                reference.synthetic_trace(), reference.CONTROL_TOTAL_SAMPLES,
                active_samples=reference.CONTROL_TOTAL_SAMPLES + 1)

    def test_wrong_threshold_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                reference.synthetic_trace(), reference.CONTROL_TOTAL_SAMPLES,
                threshold=0.4)

    def test_wrong_separation_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.detect_nuclei(
                reference.synthetic_trace(), reference.CONTROL_TOTAL_SAMPLES,
                min_separation_frames=0)


class ScoringTests(unittest.TestCase):
    def test_exact_match_scores_zero(self) -> None:
        score = reference.score_rate(12, 12, reference.CONTROL_ACTIVE_SAMPLES)
        self.assertEqual(score["absolute_count_error"], 0)
        self.assertEqual(score["absolute_rate_error"], 0.0)
        self.assertEqual(score["absolute_rate_error_fraction"], "0")

    def test_count_error_is_exact(self) -> None:
        score = reference.score_rate(10, 12, reference.CONTROL_ACTIVE_SAMPLES)
        self.assertEqual(score["absolute_count_error"], 2)
        self.assertEqual(score["predicted_rate_fraction"], "10/3")
        self.assertEqual(score["truth_rate_fraction"], "4")
        self.assertEqual(score["absolute_rate_error_fraction"], "2/3")

    def test_missing_truth_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.score_rate(12, None, reference.CONTROL_ACTIVE_SAMPLES)

    def test_negative_truth_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.score_rate(12, -1, reference.CONTROL_ACTIVE_SAMPLES)

    def test_boolean_prediction_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.score_rate(True, 12, reference.CONTROL_ACTIVE_SAMPLES)


class ControlTests(unittest.TestCase):
    def test_control_never_claims_execution(self) -> None:
        control = reference.build_control()
        self.assertIs(control["source_executed"], False)
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(
            control["trace_source"],
            "caller_supplied_synthetic_control_trace_not_usc_output")

    def test_control_final_partial_window(self) -> None:
        window = reference.build_control()["final_partial_window"]
        self.assertEqual(window["start_sample"], 64000)
        self.assertEqual(window["end_sample"], 64077)
        self.assertEqual(window["samples"], 77)
        self.assertIs(window["hosts_nucleus"], True)

    def test_control_silence_and_refractory(self) -> None:
        control = reference.build_control()
        self.assertEqual(control["silence_control"]["event_count"], 0)
        self.assertEqual(control["refractory_control"]["accepted_events"], 1)
        self.assertEqual(
            control["refractory_control"]["accepted_frames"], [100])

    def test_control_missing_result_never_qualifies(self) -> None:
        missing = reference.build_control()["missing_result"]
        self.assertIs(missing["truth_missing_rejected"], True)
        self.assertIs(missing["missing_trace_value_rejected"], True)
        self.assertIs(missing["produced_result_for_missing"], False)

    def test_adverse_all_rejected(self) -> None:
        adverse = reference.run_adverse_controls()
        self.assertEqual(len(adverse), 29)
        self.assertTrue(all(item["result"] == "rejected"
                            for item in adverse))


class CallerManifestTests(unittest.TestCase):
    def _manifest(self, root: Path) -> dict:
        archive = root / "SAIL-speechrate.zip"
        archive.write_bytes(b"archive-fixture")
        source = root / "source"
        (source / "src").mkdir(parents=True)
        (source / "doc").mkdir()
        (source / "doc/README").write_text("source fixture\n")
        (source / "src/set_para.m").write_text("twin=5;\n")
        license_path = root / "LICENSE"
        license_path.write_text("explicit fixture grant\n")
        matlab = root / "matlab"
        (matlab / "bin").mkdir(parents=True)
        sfs = root / "sfs"
        sfs.mkdir()
        esps = root / "esps"
        esps.mkdir()
        frontend = root / "frontend.json"
        frontend.write_text("{}\n")
        parity = root / "parity.json"
        parity.write_text("{}\n")
        return {
            "approved_parity_path": str(parity),
            "approved_parity_sha256":
                reference.sha256(parity.read_bytes()),
            "archive_sha256": reference.sha256(archive.read_bytes()),
            "archive_zip_path": str(archive),
            "esps_get_f0_path": str(esps),
            "frontend_record_path": str(frontend),
            "frontend_record_sha256":
                reference.sha256(frontend.read_bytes()),
            "license_record_path": str(license_path),
            "license_record_sha256":
                reference.sha256(license_path.read_bytes()),
            "matlab_runtime_path": str(matlab),
            "matlab_version": reference.MATLAB_VERSION,
            "sfs_voc19_path": str(sfs),
            "source_identity": "archive-sha256-plus-tree",
            "source_root_path": str(source),
            "source_tree_sha256": reference.source_tree_digest(source),
        }

    def test_complete_manifest_validates_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            with mock.patch.multiple(
                    reference,
                    ARCHIVE_SHA256=manifest["archive_sha256"],
                    SOURCE_TREE_SHA256=manifest["source_tree_sha256"]):
                result = reference.validate_caller_manifest(manifest)
            self.assertTrue(result["accepted"])
            self.assertFalse(result["executed"])
            self.assertFalse(result["extracted"])
            self.assertFalse(result["loaded"])

    def test_missing_field_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest({})

    def test_relative_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["archive_zip_path"] = "archive.zip"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_wrong_matlab_version_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["matlab_version"] = "R2024a"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_wrong_archive_hash_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["archive_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_extra_field_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["extra"] = True
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class ContractTests(unittest.TestCase):
    def test_contract_invariants(self) -> None:
        contract = json.loads(
            (reference.HERE / "contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["task"], reference.TASK)
        self.assertEqual(contract["profile"], "rate")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertEqual(contract["evidence_status"], "incomplete")
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(contract["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(contract["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["gates"]))
        self.assertEqual(len(contract["exact_blockers"]), 8)
        self.assertEqual(contract["write_scope"], reference.TASK_PREFIX)
        self.assertEqual(contract["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(contract["boundary_pins"], reference.BOUNDARY_PINS)
        self.assertIs(contract["boundary"]["registered"], False)
        self.assertIs(contract["boundary"]["enabled_by_default"], False)
        self.assertEqual(contract["boundary"]["descriptor_settings"], {})
        self.assertEqual(contract["reproduction"][
            "cold_start_regenerations"], 3)
        self.assertEqual(contract["task_row_identity"]["stable_sha256"],
                         reference.task_row_identity()["stable_sha256"])


class ReportTests(unittest.TestCase):
    def test_report_invariants(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["profile"], "rate")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertIs(report["qualification"]["candidate_qualified"], False)
        self.assertIs(
            report["qualification"][
                "no_missing_result_qualifies_candidate"], True)
        self.assertIsNone(report["candidate_metrics"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["gates"]))
        self.assertEqual(len({gate["id"] for gate in report["gates"]}), 8)
        self.assertEqual(len(report["exact_blockers"]), 8)
        self.assertEqual(
            report["rate_profile"]["satisfied_for_qualification"], [])
        self.assertIs(report["asset_audit"]["qualified"], False)
        self.assertIs(report["asset_audit"]["archive_present"], False)
        self.assertIs(report["asset_audit"]["rights_record_present"], False)
        self.assertIs(report["asset_audit"]["runtime_present"], False)
        self.assertIs(
            report["asset_audit"]["source_tree_matches_pins"], True)
        self.assertIs(report["reference_protocol"]["source_executed"], False)
        self.assertTrue(report["controls"]["adverse_all_rejected"])
        self.assertIs(report["boundary"]["registered"], False)
        self.assertIs(report["boundary"]["enabled_by_default"], False)
        self.assertEqual(report["boundary"]["descriptor_settings"], {})
        self.assertIs(report["scope"]["real_rate_estimate"], False)
        self.assertIs(report["scope"]["network_used"], False)
        self.assertIs(report["task_row_identity"]["whole_file_hashed"], False)
        self.assertEqual(
            report["source_reported_context"]["label"],
            "source_reported_not_measured_here")
        self.assertIn(reference.ARCHIVE_REL,
                      report["missing_historical_artifacts"])

    def test_report_is_byte_stable(self) -> None:
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_no_tasks_json_digest_in_report(self) -> None:
        payload = reference.canonical_report_bytes(reference.build_report())
        text = payload.decode("utf-8")
        self.assertNotIn('"plan/swarm/TASKS.json":', text)
        self.assertNotIn('TASKS.json": "', text)


if __name__ == "__main__":
    unittest.main()
