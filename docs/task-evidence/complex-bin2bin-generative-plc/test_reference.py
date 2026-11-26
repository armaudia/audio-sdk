# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the Complex-Bin2bin package."""

from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

# REUSE-IgnoreStart
SPDX_LICENSE_LINE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd


def control() -> dict:
    return copy.deepcopy(reference._manifest_control())


class StrictJsonTests(unittest.TestCase):
    def test_canonical_text_is_sorted_compact_and_newline_terminated(self) -> None:
        text = reference.canonical_text({"b": 2, "a": 1})
        self.assertEqual(text, '{"a":1,"b":2}\n')
        self.assertTrue(text.endswith("\n"))

    def test_canonical_bytes_round_trip(self) -> None:
        value = {"z": [1, 2], "a": "x"}
        self.assertEqual(reference.loads_strict(reference.canonical_text(value)),
                         value)

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":1,"a":2}')
        self.assertEqual(str(caught.exception), "duplicate_json_key:a")

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":NaN}')
        self.assertEqual(str(caught.exception),
                         "nonfinite_json_constant:NaN")

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":Infinity}')
        self.assertEqual(str(caught.exception),
                         "nonfinite_json_constant:Infinity")

    def test_negative_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":-Infinity}')
        self.assertEqual(str(caught.exception),
                         "nonfinite_json_constant:-Infinity")

    def test_root_array_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict("[]")
        self.assertEqual(str(caught.exception), "json_root_not_object")

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict("\ufeff{}")
        self.assertEqual(str(caught.exception), "json_byte_order_mark")

    def test_object_digest_is_stable(self) -> None:
        first = reference.object_digest({"a": 1})
        second = reference.object_digest({"a": 1})
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)


class BoardIdentityTests(unittest.TestCase):
    def test_board_row_projection_matches_stable_identity(self) -> None:
        board = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
        self.assertTrue(board.is_file(), "shared board task row is missing")
        self.assertEqual(reference.board_row_projection(board),
                         reference.BOARD_ROW_PROJECTION)

    def test_board_projection_contains_only_stable_fields(self) -> None:
        self.assertEqual(set(reference.BOARD_ROW_PROJECTION),
                         set(reference.BOARD_ROW_FIELDS))
        for mutable in ("status", "owner", "claim", "review", "handoff",
                        "blocked_reason", "dispatch_priority"):
            self.assertNotIn(mutable, reference.BOARD_ROW_PROJECTION)

    def test_board_projection_digest_is_deterministic(self) -> None:
        first = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        second = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        self.assertEqual(first, second)

    def test_board_file_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)
        self.assertFalse(reference.BOARD_ROW_PROJECTION.get("status"))

    def test_linked_rows_are_stable_identity_only(self) -> None:
        self.assertEqual(len(reference.LINKED_ROWS), 7)
        for row in reference.LINKED_ROWS:
            self.assertEqual(set(row), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(reference.LINKED_ROWS[0],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(reference.linked_rows_digest(),
                         reference.object_digest(
                             [dict(row) for row in reference.LINKED_ROWS]))


class AbsenceTests(unittest.TestCase):
    def test_fixed_probes_are_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(not row["present"] for row in rows))
        summary = reference.absence_summary(rows)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["recursive_workspace_walk"])

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "probe").write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                reference.absence_probes(root, probes=("probe",),
                                         worktree=root)
            self.assertEqual(str(caught.exception),
                             "artifact_present_reopen_required:probe")

    def test_probe_list_is_fixed_and_bounded(self) -> None:
        self.assertEqual(len(reference.ABSENCE_PROBES), 27)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertIn("data/checkouts/cplx-bin2bin",
                      reference.ABSENCE_PROBES)
        self.assertIn("third_party/cplx-bin2bin",
                      reference.ABSENCE_PROBES)
        self.assertIn("checkpoints/cplx-bin2bin",
                      reference.ABSENCE_PROBES)
        self.assertIn("data/traces/complex-bin2bin",
                      reference.ABSENCE_PROBES)

    def test_no_unqualified_runtime_is_recorded(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        self.assertEqual(
            report["absence_evidence"]["observed_unqualified_binaries"], [])


class AdmissionTests(unittest.TestCase):
    def assertRejected(self, document: dict, code: str | None = None,
                       field: str | None = None) -> None:
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertFalse(result["accepted"])
        if code is not None:
            self.assertEqual(result["code"], code)
        if field is not None:
            self.assertEqual(result["field"], field)
        self.assertTrue(result["state_unchanged"])

    def test_schema_control_is_accepted_without_qualifying(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertGreater(result["checks"], 0)
        built = reference.admission_controls()
        self.assertEqual(len(built["controls"]), 1)
        self.assertEqual(built["controls"][0]["status"],
                         "accepted_schema_control")
        self.assertFalse(built["controls"][0]["qualifies"])
        self.assertEqual(built["controls"][0]["evidence_class"],
                         "synthetic_schema_control_not_evidence")

    def test_path_probe_rejects_missing_artifacts(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "probe_missing")

    def test_missing_root_rejected(self) -> None:
        self.assertRejected(None, "manifest_not_object")  # type: ignore[arg-type]

    def test_missing_field_rejected(self) -> None:
        document = control()
        del document["model"]
        self.assertRejected(document, "missing_field", "model")

    def test_unknown_field_rejected(self) -> None:
        document = control()
        document["extra"] = "value"
        self.assertRejected(document, "unknown_field", "extra")

    def test_wrong_schema_rejected(self) -> None:
        document = control()
        document["schema_id"] = "wrong"
        self.assertRejected(document, "invalid_schema", "schema_id")

    def test_uppercase_revision_rejected(self) -> None:
        document = control()
        document["model"]["source_revision"] = "A" * 40
        self.assertRejected(document, "invalid_value",
                            "model.source_revision")

    def test_relative_path_rejected(self) -> None:
        document = control()
        document["model"]["source_path"] = "relative/src"
        self.assertRejected(document, "invalid_path", "model.source_path")

    def test_path_traversal_rejected(self) -> None:
        document = control()
        document["model"]["license_path"] = "/caller/../COPYING"
        self.assertRejected(document, "invalid_path", "model.license_path")

    def test_null_byte_path_rejected(self) -> None:
        document = control()
        document["model"]["runtime_path"] = "/caller/lib\x00/runtime"
        self.assertRejected(document, "invalid_path", "model.runtime_path")

    def test_checkpoint_bytes_float_rejected(self) -> None:
        document = control()
        document["model"]["checkpoint_bytes"] = 1.5
        self.assertRejected(document, "invalid_value",
                            "model.checkpoint_bytes")

    def test_checkpoint_bytes_bool_rejected(self) -> None:
        document = control()
        document["model"]["checkpoint_bytes"] = True
        self.assertRejected(document, "invalid_value",
                            "model.checkpoint_bytes")

    def test_rights_denied_rejected(self) -> None:
        document = control()
        document["model"]["rights_decision"] = "denied"
        self.assertRejected(document, "rights_denied",
                            "model.rights_decision")

    def test_sample_rate_rejected(self) -> None:
        document = control()
        document["geometry"]["sample_rate_hz"] = 48000
        self.assertRejected(document, "invalid_value",
                            "geometry.sample_rate_hz")

    def test_channels_rejected(self) -> None:
        document = control()
        document["geometry"]["channels"] = 2
        self.assertRejected(document, "invalid_value", "geometry.channels")

    def test_loss_block_over_frame_rejected(self) -> None:
        document = control()
        document["geometry"]["loss_block_samples"] = \
            document["geometry"]["frame_samples"] + 1
        self.assertRejected(document, "invalid_value",
                            "geometry.loss_block_samples")

    def test_delay_infinite_rejected(self) -> None:
        document = control()
        document["geometry"]["expected_delay_samples"] = float("inf")
        self.assertRejected(document, "nonfinite_value",
                            "geometry.expected_delay_samples")

    def test_empty_intervals_rejected(self) -> None:
        document = control()
        document["loss_trace"]["intervals"] = []
        self.assertRejected(document, "invalid_value",
                            "loss_trace.intervals")

    def test_overlapping_intervals_rejected(self) -> None:
        document = control()
        document["loss_trace"]["intervals"] = [
            {"first_sample": 100, "sample_count": 100},
            {"first_sample": 150, "sample_count": 10},
        ]
        self.assertRejected(document, "invalid_value",
                            "loss_trace.intervals.order")

    def test_adjacent_intervals_accepted(self) -> None:
        document = control()
        document["loss_trace"]["intervals"] = [
            {"first_sample": 100, "sample_count": 100},
            {"first_sample": 200, "sample_count": 10},
        ]
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertTrue(result["accepted"])

    def test_interval_nan_rejected(self) -> None:
        document = control()
        document["loss_trace"]["intervals"][0]["sample_count"] = float("nan")
        self.assertRejected(document, "nonfinite_value",
                            "loss_trace.intervals[0].sample_count")

    def test_clean_alignment_rejected(self) -> None:
        document = control()
        document["clean_reference"]["alignment"] = "guess"
        self.assertRejected(document, "invalid_value",
                            "clean_reference.alignment")

    def test_clean_offset_rejected(self) -> None:
        document = control()
        document["clean_reference"]["offset_samples"] = 5
        self.assertRejected(document, "invalid_value",
                            "clean_reference.offset_samples")

    def test_metrics_empty_rejected(self) -> None:
        document = control()
        document["score_protocol"]["metrics"] = []
        self.assertRejected(document, "invalid_value",
                            "score_protocol.metrics")

    def test_metrics_duplicate_rejected(self) -> None:
        document = control()
        document["score_protocol"]["metrics"] = ["stoi", "stoi"]
        self.assertRejected(document, "invalid_value",
                            "score_protocol.metrics")

    def test_metric_unknown_rejected(self) -> None:
        document = control()
        document["score_protocol"]["metrics"] = ["mos", "stoi"]
        self.assertRejected(document, "invalid_value",
                            "score_protocol.metrics")

    def test_score_baseline_rejected(self) -> None:
        document = control()
        document["score_protocol"]["baseline"] = "identity"
        self.assertRejected(document, "invalid_value",
                            "score_protocol.baseline")

    def test_paired_reference_false_rejected(self) -> None:
        document = control()
        document["score_protocol"]["paired_clean_reference"] = False
        self.assertRejected(document, "invalid_value",
                            "score_protocol.paired_clean_reference")

    def test_minimum_items_bool_rejected(self) -> None:
        document = control()
        document["score_protocol"]["minimum_items"] = True
        self.assertRejected(document, "invalid_value",
                            "score_protocol.minimum_items")

    def test_admission_matrix_is_all_rejected(self) -> None:
        built = reference.admission_controls()
        self.assertEqual(len(built["cases"]), 75)
        self.assertTrue(all(case["status"] == "rejected"
                            for case in built["cases"]))
        self.assertTrue(all(case["qualifies"] is False
                            for case in built["cases"]))
        self.assertTrue(all(case["state_unchanged"] is True
                            for case in built["cases"]))
        ids = [case["id"] for case in built["cases"]]
        self.assertEqual(len(set(ids)), len(ids))


class ReportTests(unittest.TestCase):
    def test_contract_committed_matches_recomputed(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        reference.validate_contract(contract)
        self.assertEqual(contract, reference.build_contract())

    def test_report_committed_bytes_are_canonical(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        report = reference.read_strict_json(HERE / "report.json")
        self.assertEqual(payload, reference.canonical_bytes(report))
        self.assertEqual(payload, reference.canonical_bytes(
            reference.build_report()))

    def test_report_digest_sidecar_matches(self) -> None:
        digest = hashlib.sha256(
            (HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")

    def test_contract_reference_fields(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        contract = reference.read_strict_json(HERE / "contract.json")
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component_id"], reference.COMPONENT_ID)

    def test_decision_and_qualification_are_fail_closed(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIs(report["proposal_only"], True)
        self.assertEqual(report["qualification"]["status"],
                         "not_qualified")
        self.assertIs(report["qualification"]["not_qualified"], True)
        self.assertIs(report["qualification"]["missing_result_promoted"],
                      False)

    def test_eight_gates_are_blocked(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        self.assertEqual([gate["id"] for gate in report["gates"]],
                         [f"RG-0{i}" for i in range(1, 9)])
        for gate in report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertIs(gate["qualifies"], False)

    def test_required_results_never_qualify(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        required = report["required_results"]
        self.assertIs(required["no_result_qualifies"], True)
        for key, value in required.items():
            if key != "no_result_qualifies":
                self.assertIs(value, False, key)

    def test_explicit_loss_policy_is_blocked(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        policy = report["explicit_loss_policy"]
        self.assertEqual(policy["policy"],
                         "explicit_packet_loss_intervals_only")
        self.assertIs(policy["inferred_loss_from_silence_or_sequence_gap"],
                      False)
        self.assertEqual(policy["status"], "blocked")
        self.assertIsNone(policy["event_count_observed"])
        self.assertIs(policy["intervals_recorded"], False)
        self.assertIs(policy["concealment_outputs_recorded"], False)

    def test_measurements_are_blocked(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        rows = report["measurements"]["rows"]
        self.assertEqual([row["id"] for row in rows],
                         [f"MR-0{i}" for i in range(1, 9)])
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])

    def test_enhancement_rows_are_blocked(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        rows = report["enhancement_profile"]["rows"]
        self.assertEqual([row["id"] for row in rows],
                         [f"ENH-0{i}" for i in range(1, 7)])
        for row in rows:
            self.assertEqual(row["status"], "blocked")

    def test_no_report_float_or_nonfinite(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")

        def walk(value):
            if isinstance(value, float):
                self.fail("report contains a float")
            if isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(report)

    def test_sources_manifest_is_deterministic_and_complete(self) -> None:
        import run
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         run.sources_bytes())

    def test_in_process_regeneration_is_byte_identical(self) -> None:
        first = reference.canonical_bytes(reference.build_report())
        second = reference.canonical_bytes(reference.build_report())
        third = reference.canonical_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(second, third)


class BoundaryTests(unittest.TestCase):
    def test_boundary_files_are_pinned_and_unchanged(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS, reference.WORKTREE)
        self.assertEqual(set(rows), set(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_source_files_are_pinned_and_unchanged(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertEqual(set(rows), set(reference.SOURCE_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_public_v0_geometry_is_unchanged(self) -> None:
        geometry = reference.public_v0_geometry()
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertIs(geometry["preserved"], True)
        self.assertIs(geometry["sdk_callback_invoked"], False)

    def test_base_commit_matches_claim(self) -> None:
        self.assertEqual(reference.BASE_COMMIT,
                         "6967a728b5c4048fb01ed4522a76a6906fbcffe2")
        self.assertEqual(reference.BRANCH,
                         "swarm/SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC")

    def test_enhancement_profile_phrases(self) -> None:
        text = (reference.AUDIO_ROOT /
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
                ).read_text(encoding="utf-8")
        rows = [line for line in text.splitlines()
                if line.startswith("| Enhancement |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])


if __name__ == "__main__":
    unittest.main()
