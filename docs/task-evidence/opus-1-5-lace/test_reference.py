# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the SDK-OPUS-1-5-LACE package."""

from __future__ import annotations

import copy
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
        self.assertEqual(set(reference.BOARD_ROW_PROJECTION),
                         {"id", "title", "component", "mode", "repository",
                          "depends_on"})

    def test_board_projection_digest_is_deterministic(self) -> None:
        digest = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        self.assertEqual(digest,
                         reference.board_row_digest(
                             dict(reference.BOARD_ROW_PROJECTION)))
        self.assertEqual(len(digest), 64)

    def test_board_file_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_linked_rows_are_stable_identity_only(self) -> None:
        self.assertEqual(len(reference.LINKED_ROWS), 4)
        for row in reference.LINKED_ROWS:
            self.assertEqual(set(row), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(reference.linked_rows_digest(),
                         reference.linked_rows_digest(
                             tuple(dict(row) for row in reference.LINKED_ROWS)))


class AbsenceTests(unittest.TestCase):
    def test_fixed_probes_are_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(row["present"] is False for row in rows))
        summary = reference.absence_summary(rows)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "present").write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                reference.absence_probes(root, probes=("present",),
                                         worktree=root)
            self.assertIn("artifact_present_reopen_required", str(caught.exception))

    def test_probe_list_is_fixed_and_bounded(self) -> None:
        self.assertGreaterEqual(len(reference.ABSENCE_PROBES), 15)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertNotIn("**", reference.ABSENCE_PROBES)


class AdmissionTests(unittest.TestCase):
    def assert_rejected(self, result: dict, code: str, field: str = "") -> None:
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], code)
        if field:
            self.assertEqual(result["field"], field)
        self.assertTrue(result["state_unchanged"])

    def test_schema_control_is_accepted_without_qualifying(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "ok")
        self.assertGreater(result["checks"], 0)
        self.assertTrue(result["state_unchanged"])
        controls = reference.admission_controls()["controls"]
        self.assertEqual(len(controls), 1)
        self.assertFalse(controls[0]["qualifies"])
        self.assertEqual(controls[0]["evidence_class"],
                         "synthetic_schema_control_not_evidence")

    def test_path_probe_rejects_missing_artifacts(self) -> None:
        self.assert_rejected(
            reference.validate_manifest(control(), probe_paths=True),
            "probe_missing", "source_path")

    def test_missing_root_rejected(self) -> None:
        self.assert_rejected(reference.validate_manifest(None),
                             "manifest_not_object")

    def test_missing_field_rejected(self) -> None:
        document = control()
        del document["source_sha256"]
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "missing_field", "source_sha256")

    def test_unknown_field_rejected(self) -> None:
        document = control()
        document["extra"] = "value"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "unknown_field", "extra")

    def test_wrong_schema_rejected(self) -> None:
        document = control()
        document["schema_id"] = "wrong"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_schema", "schema_id")

    def test_uppercase_revision_rejected(self) -> None:
        document = control()
        document["source_revision"] = "A" * 40
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "source_revision")

    def test_relative_path_rejected(self) -> None:
        document = control()
        document["source_path"] = "relative/src"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_path", "source_path")

    def test_path_traversal_rejected(self) -> None:
        document = control()
        document["license_path"] = "/caller/../COPYING"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_path", "license_path")

    def test_float_decoder_option_rejected(self) -> None:
        document = control()
        document["decoder_option"]["value"] = 1.5
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_type",
            "decoder_option.value")

    def test_none_decoder_option_rejected(self) -> None:
        document = control()
        document["decoder_option"]["value"] = None
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_type",
            "decoder_option.value")

    def test_wrong_codec_rejected(self) -> None:
        document = control()
        document["traffic"]["codec"] = "aac"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "traffic.codec")

    def test_wrong_codec_version_rejected(self) -> None:
        document = control()
        document["traffic"]["codec_version"] = "1.4"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "traffic.codec_version")

    def test_wrong_sample_rate_rejected(self) -> None:
        document = control()
        document["traffic"]["sample_rate_hz"] = 44100
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "traffic.sample_rate_hz")

    def test_wrong_channels_rejected(self) -> None:
        document = control()
        document["traffic"]["channels"] = 0
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "traffic.channels")

    def test_zero_packet_duration_rejected(self) -> None:
        document = control()
        document["traffic"]["packet_duration_us"] = 0
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "traffic.packet_duration_us")

    def test_non_multiple_packet_duration_rejected(self) -> None:
        document = control()
        document["traffic"]["packet_duration_us"] = 1001
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "traffic.packet_duration_us")

    def test_low_bitrate_rejected(self) -> None:
        document = control()
        document["traffic"]["bitrate_bps"] = 1000
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "traffic.bitrate_bps")

    def test_boolean_bitrate_rejected(self) -> None:
        document = control()
        document["traffic"]["bitrate_bps"] = True
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "traffic.bitrate_bps")

    def test_unknown_alignment_rejected(self) -> None:
        document = control()
        document["clean_reference"]["alignment"] = "guess"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "clean_reference.alignment")

    def test_sample_exact_offset_rejected(self) -> None:
        document = control()
        document["clean_reference"]["offset_samples"] = 5
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "clean_reference.offset_samples")

    def test_empty_strata_rejected(self) -> None:
        document = control()
        document["strata"] = []
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "strata")

    def test_duplicate_stratum_id_rejected(self) -> None:
        document = control()
        document["strata"].append(dict(document["strata"][0]))
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "strata.id")

    def test_negative_burst_rejected(self) -> None:
        document = control()
        document["strata"][0]["burst_frames"] = -1
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value",
            "strata.burst_frames")

    def test_empty_packets_rejected(self) -> None:
        document = control()
        document["packets"] = []
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets")

    def test_packet_order_rejected(self) -> None:
        document = control()
        document["packets"] = list(reversed(document["packets"]))
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets.index")

    def test_unknown_packet_status_rejected(self) -> None:
        document = control()
        document["packets"][0]["status"] = "missing"
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets.status")

    def test_lost_packet_with_content_rejected(self) -> None:
        document = control()
        document["packets"][1]["valid_samples"] = 1
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets.lost")

    def test_received_packet_with_empty_payload_rejected(self) -> None:
        document = control()
        document["packets"][0]["payload_sha256"] = reference.EMPTY_SHA256
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets.received")

    def test_decoded_sample_mismatch_rejected(self) -> None:
        document = control()
        document["packets"][0]["decoded_samples"] = 480
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets.received")

    def test_boolean_sample_count_rejected(self) -> None:
        document = control()
        document["packets"][0]["valid_samples"] = True
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_type",
            "packets.valid_samples")

    def test_nonfinite_sample_count_rejected(self) -> None:
        document = control()
        document["packets"][0]["valid_samples"] = float("nan")
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_type",
            "packets.valid_samples")

    def test_packets_not_list_rejected(self) -> None:
        document = control()
        document["packets"] = {}
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False), "invalid_value", "packets")

    def test_adverse_matrix_is_frozen_and_all_rejected(self) -> None:
        matrix = reference.admission_controls()
        ids = [case["id"] for case in matrix["cases"]]
        self.assertGreaterEqual(len(ids), 40)
        self.assertEqual(len(ids), len(set(ids)))
        for case in matrix["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])
        self.assertIn("PRS-01", ids)
        self.assertIn("JSON-04", ids)


class ContractAndReportTests(unittest.TestCase):
    def test_contract_validation(self) -> None:
        reference.validate_contract(reference.build_contract())

    def test_contract_is_canonical_bytes(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(reference.canonical_bytes(contract),
                         reference.canonical_bytes(reference.build_contract()))

    def test_report_decision_and_qualification(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["profile"], "restoration")
        self.assertEqual(report["mode"], "feasibility")

    def test_disposition_is_proposal_only_not_qualified(self) -> None:
        disposition = reference.build_report()["disposition"]
        self.assertTrue(disposition["proposal_only"])
        self.assertTrue(disposition["incomplete"])
        self.assertTrue(disposition["not_qualified"])
        self.assertFalse(disposition["missing_result_qualifies"])
        self.assertFalse(disposition["registered"])
        self.assertFalse(disposition["default_enabled"])
        self.assertEqual(disposition["production_exposure"], "DEFER")

    def test_eight_release_gates_are_blocked(self) -> None:
        gates = reference.build_report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(index) for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])

    def test_required_artifacts_are_absent(self) -> None:
        artifacts = reference.build_report()["required_artifacts"]
        self.assertEqual(len(artifacts), 6)
        for artifact in artifacts:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])

    def test_exact_blockers_are_open(self) -> None:
        blockers = reference.build_report()["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in
                        reference.build_report()["required_artifacts"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])

    def test_qualification_has_no_true_result(self) -> None:
        qualification = reference.build_report()["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        for key, value in qualification.items():
            if key in ("status", "readiness"):
                continue
            if key in ("not_qualified", "all_release_gates_blocked"):
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_boundary_and_scope_claims_are_false(self) -> None:
        report = reference.build_report()
        for section in ("boundary", "scope"):
            for key, value in report[section].items():
                if key == "task_local_only":
                    self.assertTrue(value)
                else:
                    self.assertFalse(value, section + "." + key)

    def test_public_geometry_preserved(self) -> None:
        geometry = reference.build_report()["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sdk_callback_invoked"])

    def test_absence_summary_blocks_shipping(self) -> None:
        absence = reference.build_report()["absence_evidence"]
        self.assertEqual(absence["summary"]["present_count"], 0)
        self.assertTrue(absence["summary"]["all_probes_absent"])
        self.assertFalse(absence["summary"]["download_attempted"])

    def test_admission_summary_has_no_qualifying_result(self) -> None:
        summary = reference.build_report()["admission"]["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["runtime_invoked"])
        self.assertFalse(summary["audio_read"])
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertEqual(summary["accepted_schema_controls"], 1)

    def test_restoration_profile_is_blocked(self) -> None:
        profile = reference.build_report()["restoration_profile"]
        self.assertEqual(len(profile["rows"]), 5)
        for row in profile["rows"]:
            self.assertEqual(row["status"], "blocked")
        self.assertEqual(profile["status"], "blocked")
        for key, value in profile.items():
            if key in ("rows", "status", "profile"):
                continue
            self.assertFalse(value, key)

    def test_remaining_gates_match_gate_rows(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["remaining_gates"],
                         [gate["id"] for gate in report["gates"]])

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = reference.build_report()["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertIn("status", identity["mutable_fields_excluded"])
        self.assertIn("owner", identity["mutable_fields_excluded"])

    def test_contract_digest_matches_report(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))

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

        for value in walk(reference.build_report()):
            self.assertNotIsInstance(value, float)

    def test_report_canonical_regeneration_is_byte_identical(self) -> None:
        first_text, first_digest = reference.canonical_report(
            reference.build_report())
        second_text, second_digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(first_text, second_text)
        self.assertEqual(first_digest, second_digest)
        self.assertTrue(first_text.endswith("\n"))

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
            self.assertEqual(reference.sha256_file(path), digest, relative)
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)

    def test_no_lace_result_keys_are_claimed(self) -> None:
        report = reference.build_report()
        self.assertNotIn("metrics", report)
        self.assertNotIn("scores", report)
        self.assertNotIn("quality", report)
        self.assertFalse(report["scope"]["quality_scored"])
        self.assertFalse(report["scope"]["decoding_performed"])


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
        forbidden = {
            ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
            ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap",
            ".pcapng", ".pt", ".pth", ".so", ".wav", ".weights",
        }
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertNotIn(path.name, {"LICENSE", "LICENSE.txt", "COPYING",
                                         "NOTICE"})
            self.assertFalse(path.is_symlink(), path.name)

    def test_deliverables_exist(self) -> None:
        expected = {
            "README.md", "LICENSES.md", "contract.json", "reference.py",
            "report.json", "report.json.sha256", "SOURCES.sha256", "run.py",
            "test_reference.py", "verify.py", "SOURCES.sha256.license",
            "contract.json.license", "report.json.license",
            "report.json.sha256.license",
        }
        present = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertTrue(expected <= present, expected - present)


if __name__ == "__main__":
    unittest.main()
