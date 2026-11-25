# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the SDK-OPUS-DRED package."""

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
                reference.absence_probes(root, probes=("probe",), worktree=root)
            self.assertEqual(str(caught.exception),
                             "artifact_present_reopen_required:probe")

    def test_probe_list_is_fixed_and_bounded(self) -> None:
        self.assertEqual(len(reference.ABSENCE_PROBES), 27)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertIn("src/dred_decoder.c", reference.ABSENCE_PROBES)
        self.assertIn("src/dred_encoder.c", reference.ABSENCE_PROBES)
        self.assertIn("dnn/dred_rdovae_dec_data.h",
                      reference.ABSENCE_PROBES)

    def test_unqualified_runtime_is_never_admitted(self) -> None:
        row = reference.UNQUALIFIED_RUNTIME
        self.assertFalse(row["admitted"])
        self.assertFalse(row["linked"])
        self.assertFalse(row["executed_by_package"])
        self.assertFalse(row["used_for_evidence"])
        self.assertFalse(row["license_text_present"])
        self.assertFalse(row["separate_encoder_symbol_observed"])
        self.assertFalse(row["dred_encoder_capability_verified"])
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

    def test_float_dred_control_rejected(self) -> None:
        document = control()
        document["dred_api"]["encoder_ctl_value"] = 1.5
        self.assertRejected(document, "invalid_value",
                            "dred_api.encoder_ctl_value")

    def test_boolean_dred_control_rejected(self) -> None:
        document = control()
        document["dred_api"]["encoder_ctl_value"] = True
        self.assertRejected(document, "invalid_value",
                            "dred_api.encoder_ctl_value")

    def test_wrong_codec_rejected(self) -> None:
        document = control()
        document["traffic"]["codec"] = "aac"
        self.assertRejected(document, "invalid_value", "traffic.codec")

    def test_opus_14_rejected(self) -> None:
        document = control()
        document["traffic"]["codec_version"] = "1.4"
        self.assertRejected(document, "invalid_value",
                            "traffic.codec_version")

    def test_opus_15_accepted_in_schema(self) -> None:
        document = control()
        document["traffic"]["codec_version"] = "1.5"
        self.assertTrue(reference.validate_manifest(
            document, probe_paths=False)["accepted"])

    def test_wrong_sample_rate_rejected(self) -> None:
        document = control()
        document["traffic"]["sample_rate_hz"] = 48000
        self.assertRejected(document, "invalid_value",
                            "traffic.sample_rate_hz")

    def test_wrong_channels_rejected(self) -> None:
        document = control()
        document["traffic"]["channels"] = 2
        self.assertRejected(document, "invalid_value", "traffic.channels")

    def test_zero_packet_duration_rejected(self) -> None:
        document = control()
        document["traffic"]["packet_duration_us"] = 0
        self.assertRejected(document, "invalid_value",
                            "traffic.packet_duration_us")

    def test_non_multiple_packet_duration_rejected(self) -> None:
        document = control()
        document["traffic"]["packet_duration_us"] = 12345
        self.assertRejected(document, "invalid_value",
                            "traffic.packet_duration_us")

    def test_low_bitrate_rejected(self) -> None:
        document = control()
        document["traffic"]["bitrate_bps"] = 1000
        self.assertRejected(document, "invalid_value", "traffic.bitrate_bps")

    def test_boolean_bitrate_rejected(self) -> None:
        document = control()
        document["traffic"]["bitrate_bps"] = True
        self.assertRejected(document, "invalid_value", "traffic.bitrate_bps")

    def test_negative_redundancy_rejected(self) -> None:
        document = control()
        document["traffic"]["redundancy_bps"] = -1
        self.assertRejected(document, "invalid_value",
                            "traffic.redundancy_bps")

    def test_nonfinite_jitter_rejected(self) -> None:
        document = control()
        document["traffic"]["jitter_ms"] = float("nan")
        self.assertRejected(document, "nonfinite_value", "traffic.jitter_ms")

    def test_infinite_jitter_rejected(self) -> None:
        document = control()
        document["traffic"]["jitter_ms"] = float("inf")
        self.assertRejected(document, "nonfinite_value", "traffic.jitter_ms")

    def test_negative_delay_rejected(self) -> None:
        document = control()
        document["traffic"]["expected_delay_samples"] = -1
        self.assertRejected(document, "invalid_value",
                            "traffic.expected_delay_samples")

    def test_unknown_alignment_rejected(self) -> None:
        document = control()
        document["clean_reference"]["alignment"] = "guess"
        self.assertRejected(document, "invalid_value",
                            "clean_reference.alignment")

    def test_sample_exact_offset_rejected(self) -> None:
        document = control()
        document["clean_reference"]["offset_samples"] = 5
        self.assertRejected(document, "invalid_value",
                            "clean_reference.offset_samples")

    def test_empty_strata_rejected(self) -> None:
        document = control()
        document["strata"] = []
        self.assertRejected(document, "invalid_value", "strata")

    def test_duplicate_stratum_id_rejected(self) -> None:
        document = control()
        document["strata"] = [dict(document["strata"][0]),
                              dict(document["strata"][0])]
        self.assertRejected(document, "invalid_value", "strata.id")

    def test_unknown_degradation_rejected(self) -> None:
        document = control()
        document["strata"][0]["degradation"] = "clean"
        self.assertRejected(document, "invalid_value", "strata.degradation")

    def test_out_of_range_bandwidth_rejected(self) -> None:
        document = control()
        document["strata"][0]["bandwidth_hz"] = 24000
        self.assertRejected(document, "invalid_value", "strata.bandwidth_hz")

    def test_loss_plan_total_rejected(self) -> None:
        document = control()
        document["loss_plan"]["total_packets"] = 7
        self.assertRejected(document, "invalid_value",
                            "loss_plan.total_packets")

    def test_loss_plan_order_rejected(self) -> None:
        document = control()
        document["loss_plan"]["lost_indices"] = [4, 3, 2]
        self.assertRejected(document, "invalid_value",
                            "loss_plan.lost_indices")

    def test_loss_plan_burst_rejected(self) -> None:
        document = control()
        document["loss_plan"]["max_burst"] = 2
        self.assertRejected(document, "invalid_value", "loss_plan.max_burst")

    def test_empty_packets_rejected(self) -> None:
        document = control()
        document["packets"] = []
        self.assertRejected(document, "invalid_value", "packets")

    def test_packet_order_rejected(self) -> None:
        document = control()
        document["packets"] = list(reversed(document["packets"]))
        self.assertRejected(document, "invalid_value", "packets.index")

    def test_unknown_packet_status_rejected(self) -> None:
        document = control()
        document["packets"][0]["status"] = "missing"
        self.assertRejected(document, "invalid_value", "packets.status")

    def test_received_packet_with_zero_samples_rejected(self) -> None:
        document = control()
        document["packets"][0]["valid_samples"] = 0
        self.assertRejected(document, "invalid_value", "packets.received")

    def test_lost_packet_with_content_rejected(self) -> None:
        document = control()
        document["packets"][2]["valid_samples"] = 1
        self.assertRejected(document, "invalid_value", "packets.lost")

    def test_received_packet_with_empty_payload_rejected(self) -> None:
        document = control()
        document["packets"][0]["payload_sha256"] = reference.EMPTY_SHA256
        self.assertRejected(document, "invalid_value", "packets.received")

    def test_recovered_packet_without_decoded_samples_rejected(self) -> None:
        document = control()
        document["packets"][3]["decoded_samples"] = 0
        self.assertRejected(document, "invalid_value", "packets.recovered")

    def test_dred_bytes_without_digest_rejected(self) -> None:
        document = control()
        document["packets"][0]["dred_sha256"] = reference.EMPTY_SHA256
        self.assertRejected(document, "invalid_value", "packets.dred_sha256")

    def test_no_recovered_packet_rejected(self) -> None:
        document = control()
        for packet in document["packets"]:
            if packet["status"] == "recovered":
                packet["status"] = "lost"
                packet["decoded_samples"] = 0
        self.assertRejected(document, "invalid_value", "packets.recovered")

    def test_no_redundancy_rejected(self) -> None:
        document = control()
        for packet in document["packets"]:
            packet["dred_bytes"] = 0
            packet["dred_sha256"] = reference.EMPTY_SHA256
        self.assertRejected(document, "invalid_value",
                            "packets.dred_redundancy")

    def test_packets_not_list_rejected(self) -> None:
        document = control()
        document["packets"] = {}
        self.assertRejected(document, "invalid_value", "packets")

    def test_adverse_matrix_is_frozen_and_all_rejected(self) -> None:
        built = reference.admission_controls()
        self.assertEqual(len(built["cases"]), 66)
        self.assertEqual(len(built["controls"]), 1)
        for case in built["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])
        for case in built["controls"]:
            self.assertEqual(case["status"], "accepted_schema_control")
            self.assertFalse(case["qualifies"])


class ContractAndReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.read_strict_json(HERE / "contract.json")
        cls.report = reference.read_strict_json(HERE / "report.json")

    def test_contract_validation(self) -> None:
        reference.validate_contract(self.contract)

    def test_contract_is_canonical_bytes(self) -> None:
        self.assertEqual(
            (HERE / "contract.json").read_bytes(),
            reference.canonical_bytes(reference.build_contract()))

    def test_report_decision_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.report["proposal_only"])

    def test_disposition_is_proposal_only_not_qualified(self) -> None:
        disposition = self.report["disposition"]
        self.assertEqual(disposition["decision"], "DEFER")
        self.assertEqual(disposition["status"], "incomplete")
        self.assertEqual(disposition["qualification_status"],
                         "not_qualified")
        self.assertEqual(disposition["promotion"], "defer")
        self.assertEqual(disposition["production_exposure"], "DEFER")
        for key in ("proposal_only", "incomplete", "not_qualified"):
            self.assertTrue(disposition[key])
        for key in ("expose_as_processor", "registered", "default_enabled",
                    "missing_result_qualifies"):
            self.assertFalse(disposition[key])

    def test_eight_release_gates_are_blocked(self) -> None:
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertEqual([row["id"] for row in self.report["gates"]],
                         ["RG-0%d" % index for index in range(1, 9)])
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
        self.assertEqual(self.report["remaining_gates"],
                         [gate["id"] for gate in self.report["gates"]])

    def test_required_artifacts_are_absent(self) -> None:
        self.assertEqual(len(self.report["required_artifacts"]), 6)
        for row in self.report["required_artifacts"]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_exact_blockers_are_open(self) -> None:
        self.assertEqual(len(self.report["exact_blockers"]), 6)
        artifact_ids = {row["id"]
                        for row in self.report["required_artifacts"]}
        for row in self.report["exact_blockers"]:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])
            self.assertIn(row["artifact_id"], artifact_ids)
            self.assertTrue(row["required_action"])

    def test_qualification_has_no_true_result(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["not_qualified"])
        for key, value in qualification.items():
            if key in ("status", "readiness", "all_release_gates_blocked",
                       "not_qualified"):
                continue
            self.assertFalse(value, key)

    def test_boundary_and_scope_claims_are_false(self) -> None:
        for section in ("boundary", "scope"):
            for key, value in self.report[section].items():
                if key == "task_local_only":
                    self.assertTrue(value)
                else:
                    self.assertFalse(value, section + "." + key)

    def test_public_geometry_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sdk_callback_invoked"])

    def test_absence_summary_blocks_shipping(self) -> None:
        evidence = self.report["absence_evidence"]
        self.assertEqual(evidence["summary"]["present_count"], 0)
        self.assertTrue(evidence["summary"]["all_probes_absent"])
        self.assertFalse(evidence["summary"]["download_attempted"])
        self.assertFalse(evidence["summary"]["recursive_workspace_walk"])
        self.assertFalse(evidence["summary"]["source_or_runtime_imported"])
        self.assertEqual(len(evidence["probes"]), 27)
        observed = evidence["observed_unqualified_binaries"]
        self.assertEqual(len(observed), 1)
        self.assertFalse(observed[0]["admitted"])
        self.assertFalse(observed[0]["used_for_evidence"])

    def test_admission_summary_has_no_qualifying_result(self) -> None:
        summary = self.report["admission"]["summary"]
        self.assertEqual(summary["case_count"], 66)
        self.assertEqual(summary["rejected_count"], 66)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["runtime_invoked"])
        self.assertFalse(summary["audio_read"])
        self.assertFalse(summary["decoding_performed"])
        self.assertFalse(summary["redundancy_generated"])

    def test_restoration_profile_is_blocked(self) -> None:
        profile = self.report["restoration_profile"]
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual([row["id"] for row in profile["rows"]],
                         ["RST-01", "RST-02", "RST-03", "RST-04", "RST-05"])
        for row in profile["rows"]:
            self.assertEqual(row["status"], "blocked")
        for key, value in profile.items():
            if key in ("profile", "rows", "status"):
                continue
            self.assertFalse(value, key)

    def test_dred_measurements_are_blocked(self) -> None:
        measurements = self.report["dred_measurements"]
        self.assertEqual(measurements["status"], "blocked")
        self.assertEqual([row["id"] for row in measurements["rows"]],
                         ["MR-01", "MR-02", "MR-03", "MR-04"])
        for row in measurements["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
        for key in ("bitrate_measured", "redundancy_measured",
                    "jitter_measured", "delay_measured"):
            self.assertFalse(measurements[key])

    def test_required_results_do_not_qualify(self) -> None:
        required = self.report["required_results"]
        self.assertTrue(required["no_result_qualifies"])
        for key, value in required.items():
            if key == "no_result_qualifies":
                continue
            self.assertFalse(value, key)

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        for mutable in identity["mutable_fields_excluded"]:
            self.assertNotIn(mutable, identity["projection"])
        self.assertEqual(identity["linked_rows"],
                         [dict(row) for row in reference.LINKED_ROWS])

    def test_contract_digest_matches_report(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_has_no_floats(self) -> None:
        def walk(value):
            if isinstance(value, dict):
                for item in value.values():
                    yield from walk(item)
            elif isinstance(value, list):
                for item in value:
                    yield from walk(item)
            else:
                yield value

        self.assertFalse(any(isinstance(value, float)
                             for value in walk(self.report)))

    def test_report_canonical_regeneration_is_byte_identical(self) -> None:
        first, digest = reference.canonical_report(reference.build_report())
        second, second_digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(digest, second_digest)
        self.assertEqual(first.encode("utf-8"),
                         (HERE / "report.json").read_bytes())
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_profile_phrases_are_exact(self) -> None:
        source = (reference.AUDIO_ROOT
                  / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
        text = source.read_text(encoding="utf-8")
        rows = [line for line in text.splitlines()
                if line.startswith("| Restoration |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])

    def test_pinned_sources_and_boundary_exist(self) -> None:
        for relative, digest in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest)
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest)

    def test_no_dred_result_keys_are_claimed(self) -> None:
        text = (HERE / "report.json").read_text(encoding="utf-8")
        for forbidden in ('"bitrate_bps":', '"redundancy_bps":',
                          '"jitter_ms":', '"delay_samples":'):
            self.assertNotIn(forbidden, text)


class PackageArtifactTests(unittest.TestCase):
    def test_python_spdx_headers(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE_LINE, head, path.name)
            self.assertIn(SPDX_COPYRIGHT_LINE, head, path.name)

    def test_license_sidecars(self) -> None:
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE_LINE, text)
            self.assertIn(SPDX_COPYRIGHT_LINE, text)

    def test_no_binary_or_vendored_license_artifacts(self) -> None:
        forbidden = {".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib",
                     ".m4a", ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus",
                     ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".so", ".wasm",
                     ".wav", ".weights"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json", "COPYING", "NOTICE", "LICENSE",
                              "LICENSE.txt"})

    def test_deliverables_exist(self) -> None:
        for name in ("README.md", "LICENSES.md", "contract.json",
                     "reference.py", "report.json", "report.json.sha256",
                     "SOURCES.sha256", "verify.py", "test_reference.py",
                     "run.py"):
            self.assertTrue((HERE / name).is_file(), name)

    def test_report_sidecar_digest_matches_bytes(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")


if __name__ == "__main__":
    unittest.main()
