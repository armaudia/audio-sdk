# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the SDK-OPUS-DEEP-PLC package."""

from __future__ import annotations

import copy
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
        self.assertEqual(len(reference.LINKED_ROWS), 4)
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
        self.assertEqual(len(reference.ABSENCE_PROBES), 29)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertIn("dnn/osce.c", reference.ABSENCE_PROBES)
        self.assertIn("dnn/plc_data.c", reference.ABSENCE_PROBES)
        self.assertIn("src/opus_decoder.c", reference.ABSENCE_PROBES)
        self.assertIn("include/opus_deep_plc.h",
                      reference.ABSENCE_PROBES)

    def test_unqualified_runtime_is_never_admitted(self) -> None:
        row = reference.UNQUALIFIED_RUNTIME
        self.assertFalse(row["admitted"])
        self.assertFalse(row["linked"])
        self.assertFalse(row["executed_by_package"])
        self.assertFalse(row["used_for_evidence"])
        self.assertFalse(row["license_text_present"])
        self.assertFalse(row["deep_plc_capability_verified"])
        self.assertEqual(row["deep_plc_selector_symbols_observed"], [])
        self.assertEqual(len(row["sha256"]), 64)
        self.assertGreater(len(row["dred_symbols_observed"]), 0)


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
        del document["source_sha256"]
        self.assertRejected(document, "missing_field", "source_sha256")

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
        document["source_revision"] = "A" * 40
        self.assertRejected(document, "invalid_value", "source_revision")

    def test_relative_path_rejected(self) -> None:
        document = control()
        document["source_path"] = "relative/src"
        self.assertRejected(document, "invalid_path", "source_path")

    def test_path_traversal_rejected(self) -> None:
        document = control()
        document["license_path"] = "/caller/../COPYING"
        self.assertRejected(document, "invalid_path", "license_path")

    def test_null_byte_path_rejected(self) -> None:
        document = control()
        document["runtime_path"] = "/caller/lib\x00/libopus.dylib"
        self.assertRejected(document, "invalid_path", "runtime_path")

    def test_selector_float_rejected(self) -> None:
        document = control()
        document["deep_plc_api"]["selector_value"] = 1.5
        self.assertRejected(document, "invalid_value",
                            "deep_plc_api.selector_value")

    def test_selector_bool_rejected(self) -> None:
        document = control()
        document["deep_plc_api"]["selector_value"] = True
        self.assertRejected(document, "invalid_value",
                            "deep_plc_api.selector_value")

    def test_selector_negative_rejected(self) -> None:
        document = control()
        document["deep_plc_api"]["selector_value"] = -1
        self.assertRejected(document, "invalid_value",
                            "deep_plc_api.selector_value")

    def test_default_state_rejected(self) -> None:
        document = control()
        document["deep_plc_api"]["default_state"] = "auto"
        self.assertRejected(document, "invalid_value",
                            "deep_plc_api.default_state")

    def test_codec_version_14_rejected(self) -> None:
        document = control()
        document["restoration"]["codec_version"] = "1.4"
        self.assertRejected(document, "invalid_value",
                            "restoration.codec_version")

    def test_sample_rate_rejected(self) -> None:
        document = control()
        document["restoration"]["sample_rate_hz"] = 48000
        self.assertRejected(document, "invalid_value",
                            "restoration.sample_rate_hz")

    def test_channels_rejected(self) -> None:
        document = control()
        document["restoration"]["channels"] = 2
        self.assertRejected(document, "invalid_value",
                            "restoration.channels")

    def test_packet_duration_not_multiple_rejected(self) -> None:
        document = control()
        document["restoration"]["packet_duration_us"] = 12345
        self.assertRejected(document, "invalid_value",
                            "restoration.packet_duration_us")

    def test_bitrate_below_bound_rejected(self) -> None:
        document = control()
        document["restoration"]["bitrate_bps"] = 1000
        self.assertRejected(document, "invalid_value",
                            "restoration.bitrate_bps")

    def test_bitrate_nan_rejected(self) -> None:
        document = control()
        document["restoration"]["bitrate_bps"] = float("nan")
        self.assertRejected(document, "nonfinite_value",
                            "restoration.bitrate_bps")

    def test_concealment_mode_rejected(self) -> None:
        document = control()
        document["restoration"]["concealment_mode"] = "zero_fill"
        self.assertRejected(document, "invalid_value",
                            "restoration.concealment_mode")

    def test_delay_infinite_rejected(self) -> None:
        document = control()
        document["restoration"]["expected_delay_samples"] = float("inf")
        self.assertRejected(document, "nonfinite_value",
                            "restoration.expected_delay_samples")

    def test_baseline_control_rejected(self) -> None:
        document = control()
        document["restoration"]["baseline_control"] = "identity"
        self.assertRejected(document, "invalid_value",
                            "restoration.baseline_control")

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

    def test_empty_strata_rejected(self) -> None:
        document = control()
        document["strata"] = []
        self.assertRejected(document, "invalid_value", "strata")

    def test_duplicate_strata_rejected(self) -> None:
        document = control()
        document["strata"] = [dict(document["strata"][0]),
                              dict(document["strata"][0])]
        self.assertRejected(document, "invalid_value", "strata.id")

    def test_empty_missing_events_rejected(self) -> None:
        document = control()
        document["missing_events"] = []
        self.assertRejected(document, "invalid_value", "missing_events")

    def test_duplicate_event_id_rejected(self) -> None:
        document = control()
        document["missing_events"][1]["event_id"] = "e1"
        self.assertRejected(document, "invalid_value",
                            "missing_events.event_id")

    def test_event_not_reported_to_decoder_rejected(self) -> None:
        document = control()
        document["missing_events"][0]["reported_to_decoder"] = False
        self.assertRejected(document, "invalid_value",
                            "missing_events.reported_to_decoder")

    def test_event_reported_non_bool_rejected(self) -> None:
        document = control()
        document["missing_events"][0]["reported_to_decoder"] = 1
        self.assertRejected(document, "invalid_value",
                            "missing_events.reported_to_decoder")

    def test_event_out_of_order_rejected(self) -> None:
        document = control()
        document["missing_events"][0]["first_packet_index"] = 4
        self.assertRejected(document, "invalid_value",
                            "missing_events.order")

    def test_event_overlap_rejected(self) -> None:
        document = control()
        document["missing_events"][1]["first_packet_index"] = 2
        self.assertRejected(document, "invalid_value",
                            "missing_events.order")

    def test_event_covering_received_packet_rejected(self) -> None:
        document = control()
        document["missing_events"][0]["first_packet_index"] = 1
        self.assertRejected(document, "invalid_value",
                            "missing_events.coverage")

    def test_missing_packet_without_event_rejected(self) -> None:
        document = control()
        document["packets"][2]["missing_event_id"] = ""
        self.assertRejected(document, "invalid_value", "packets.missing")

    def test_missing_packet_unknown_event_rejected(self) -> None:
        document = control()
        document["packets"][2]["missing_event_id"] = "e9"
        self.assertRejected(document, "invalid_value",
                            "missing_events.coverage")

    def test_inferred_gap_loss_without_event_rejected(self) -> None:
        document = control()
        document["missing_events"] = [document["missing_events"][0]]
        document["concealment_outputs"] = [
            document["concealment_outputs"][0]]
        self.assertRejected(document, "invalid_value",
                            "missing_events.coverage")

    def test_received_zero_samples_rejected(self) -> None:
        document = control()
        document["packets"][0]["valid_samples"] = 0
        self.assertRejected(document, "invalid_value", "packets.received")

    def test_received_produced_mismatch_rejected(self) -> None:
        document = control()
        document["packets"][0]["produced_samples"] = 321
        self.assertRejected(document, "invalid_value", "packets.received")

    def test_missing_packet_payload_rejected(self) -> None:
        document = control()
        document["packets"][2]["payload_bytes"] = 1
        self.assertRejected(document, "invalid_value", "packets.missing")

    def test_packet_sample_bound_rejected(self) -> None:
        document = control()
        document["packets"][0]["valid_samples"] = 99999
        self.assertRejected(document, "invalid_value", "packets.samples")

    def test_packet_nan_rejected(self) -> None:
        document = control()
        document["packets"][0]["valid_samples"] = float("nan")
        self.assertRejected(document, "nonfinite_value",
                            "packets[0].valid_samples")

    def test_output_sample_mismatch_rejected(self) -> None:
        document = control()
        document["concealment_outputs"][0]["concealed_samples"] = 321
        self.assertRejected(document, "invalid_value",
                            "concealment_outputs.concealed_samples")

    def test_output_valid_samples_rejected(self) -> None:
        document = control()
        document["concealment_outputs"][0]["valid_samples"] = 1
        self.assertRejected(document, "invalid_value",
                            "concealment_outputs.valid_samples")

    def test_output_peak_out_of_range_rejected(self) -> None:
        document = control()
        document["concealment_outputs"][0]["peak_q15"] = 32768
        self.assertRejected(document, "invalid_value",
                            "concealment_outputs.peak_q15")

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
        document["score_protocol"]["metrics"] = ["mos"]
        self.assertRejected(document, "invalid_value",
                            "score_protocol.metrics")

    def test_score_control_rejected(self) -> None:
        document = control()
        document["score_protocol"]["control"] = "identity"
        self.assertRejected(document, "invalid_value",
                            "score_protocol.control")

    def test_paired_reference_false_rejected(self) -> None:
        document = control()
        document["score_protocol"]["paired_clean_reference"] = False
        self.assertRejected(document, "invalid_value",
                            "score_protocol.paired_clean_reference")

    def test_admission_matrix_is_all_rejected(self) -> None:
        built = reference.admission_controls()
        self.assertEqual(len(built["cases"]), 88)
        self.assertTrue(all(case["status"] == "rejected"
                            for case in built["cases"]))
        self.assertTrue(all(case["qualifies"] is False
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

    def test_explicit_missing_event_policy_is_blocked(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        policy = report["explicit_missing_event_policy"]
        self.assertEqual(policy["policy"],
                         "explicit_missing_packet_events_only")
        self.assertIs(policy["inferred_loss_from_sequence_gaps"], False)
        self.assertEqual(policy["status"], "blocked")
        self.assertIsNone(policy["event_count_observed"])
        self.assertIs(policy["events_recorded"], False)
        self.assertIs(policy["concealment_intervals_recorded"], False)

    def test_deep_plc_measurements_are_blocked(self) -> None:
        report = reference.read_strict_json(HERE / "report.json")
        rows = report["deep_plc_measurements"]["rows"]
        self.assertEqual([row["id"] for row in rows],
                         [f"MR-0{i}" for i in range(1, 6)])
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])

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
                         "59469bca84c63b9fc71a3a3b115567df92170df0")
        self.assertEqual(reference.BRANCH, "swarm/SDK-OPUS-DEEP-PLC")


if __name__ == "__main__":
    unittest.main()
