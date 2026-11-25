# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE package.

No network, no Opus/libopus/codec runtime, no audio asset, no skips. Every check
is task-local and stdlib-only.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as reference  # noqa: E402

GATE_IDS = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
ARTIFACT_IDS = ("ART-01", "ART-02", "ART-03", "ART-04", "ART-05", "ART-06")
BLOCKER_IDS = ("BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05", "BLK-06")
TOOL_IDS = ("TOOL-01", "TOOL-02", "TOOL-03", "TOOL-04", "TOOL-05", "TOOL-06",
            "TOOL-07")


def walk_numbers(value: object):
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_numbers(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_numbers(item)
    else:
        yield value


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":NaN}')

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":Infinity}')

    def test_root_must_be_object(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict("[]")

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"a":1}')

    def test_canonical_bytes_sorted_and_compact(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        self.assertEqual(payload, b'{"a":[2,3],"b":1}\n')

    def test_canonical_rejects_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})

    def test_object_digest_matches_bytes(self) -> None:
        document = {"x": "y"}
        expected = hashlib.sha256(reference.canonical_bytes(document)).hexdigest()
        self.assertEqual(reference.object_digest(document), expected)


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertTrue(all(row["verified"] for row in rows.values()))
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))

    def test_boundary_pins_match(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS, reference.WORKTREE)
        self.assertTrue(all(row["verified"] for row in rows.values()))
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))

    def test_pin_mismatch_fails_closed(self) -> None:
        pins = {next(iter(reference.SOURCE_PINS)): "0" * 64}
        with self.assertRaises(ValueError):
            reference.pin_rows(pins, reference.AUDIO_ROOT)

    def test_board_projection_matches_embedded_row(self) -> None:
        path = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
        projection = reference.board_row_projection(path)
        self.assertEqual(projection, reference.BOARD_ROW_PROJECTION)
        self.assertEqual(reference.board_row_digest(projection),
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))

    def test_board_projection_has_no_mutable_fields(self) -> None:
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, reference.BOARD_ROW_FIELDS)

    def test_absence_probes_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(not row["present"] for row in rows))


class PacketContractTests(unittest.TestCase):
    def test_packet_contract_is_not_opus(self) -> None:
        contract = reference.PACKET_CONTRACT
        self.assertTrue(contract["not_opus"])
        self.assertTrue(contract["distinct_from_pcm"])
        self.assertFalse(contract["rfc6716_toc_used"])
        self.assertFalse(contract["codec_operation"])
        self.assertIn("fields", contract["transmit_packet"])
        self.assertIn("fields", contract["receive_packet"])

    def test_payload_roundtrip_is_exact(self) -> None:
        frames = reference.synthetic_frames(6)
        for frame in frames:
            encoded = reference.encode_frame(frame)
            self.assertEqual(reference.decode_frame(encoded), frame)

    def test_payload_roundtrip_handles_negative_and_zero(self) -> None:
        for frame in ((0,) * 160, (-1,) * 160, (32767,) * 160,
                      (-32768,) * 160):
            self.assertEqual(
                reference.decode_frame(reference.encode_frame(frame)), frame)

    def test_tag_layout_frame_count_and_kind(self) -> None:
        frames = reference.synthetic_frames(4)
        labels = reference.frame_labels(4)
        packets = reference.packetize(frames, labels, packet_frames=2,
                                      dtx="off", fec=False)
        self.assertEqual([packet["frame_count"] for packet in packets], [2, 2])
        self.assertTrue(all(packet["kind"] == "audio" for packet in packets))
        parsed = reference.parse_payload(bytes.fromhex(packets[0]["payload_hex"]))
        self.assertEqual(parsed["frame_count"], 2)
        self.assertEqual(parsed["kind"], "audio")
        self.assertFalse(parsed["fec_present"])

    def test_reserved_tag_bits_rejected(self) -> None:
        with self.assertRaises(reference.ContractError):
            reference.parse_payload(b"\xe0")

    def test_truncated_payload_rejected(self) -> None:
        frames = reference.synthetic_frames(2)
        labels = reference.frame_labels(2)
        payload = bytes.fromhex(
            reference.packetize(frames, labels, packet_frames=1,
                                dtx="off", fec=False)[0]["payload_hex"])
        for length in range(1, 4):
            with self.assertRaises(reference.ContractError):
                reference.parse_payload(payload[:length])

    def test_trailing_payload_bytes_rejected(self) -> None:
        frames = reference.synthetic_frames(2)
        labels = reference.frame_labels(2)
        payload = bytes.fromhex(
            reference.packetize(frames, labels, packet_frames=1,
                                dtx="off", fec=False)[0]["payload_hex"])
        with self.assertRaises(reference.ContractError):
            reference.parse_payload(payload + b"\x00")

    def test_frame_length_validation(self) -> None:
        with self.assertRaises(reference.ContractError):
            reference.encode_frame((0,) * 159)

    def test_comfort_noise_is_bounded(self) -> None:
        frame = reference.comfort_noise_frame(3)
        self.assertEqual(len(frame), 160)
        self.assertLessEqual(max(abs(sample) for sample in frame),
                             reference.COMFORT_NOISE_LEVEL)


class SignalAndDtxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frames = reference.synthetic_frames(100)
        self.labels = reference.frame_labels(100)

    def test_labels_contain_pause_and_voiced(self) -> None:
        self.assertIn("pause", self.labels)
        self.assertIn("voiced", self.labels)
        self.assertEqual(self.labels.count("pause"), 20)

    def test_energy_gate_separates_pause_and_voiced(self) -> None:
        for frame, label in zip(self.frames, self.labels):
            if label == "pause":
                self.assertTrue(reference.frame_is_silent(frame))
            else:
                self.assertFalse(reference.frame_is_silent(frame))

    def test_dtx_off_transmits_every_source_frame(self) -> None:
        packets = reference.packetize(self.frames, self.labels,
                                      packet_frames=2, dtx="off", fec=False)
        transmitted = sum(packet["frame_count"] for packet in packets)
        self.assertEqual(transmitted, 100)

    def test_dtx_omit_suppresses_pause_frames(self) -> None:
        packets = reference.packetize(self.frames, self.labels,
                                      packet_frames=2, dtx="omit", fec=False)
        transmitted = sum(packet["frame_count"] for packet in packets)
        self.assertEqual(transmitted, 80)
        self.assertEqual(sum(1 for packet in packets
                             if packet["kind"] == "comfort_noise"), 0)

    def test_dtx_cn_emits_one_packet_per_silent_run(self) -> None:
        packets = reference.packetize(self.frames, self.labels,
                                      packet_frames=2, dtx="cn", fec=False)
        self.assertEqual(sum(1 for packet in packets
                             if packet["kind"] == "comfort_noise"), 2)
        self.assertEqual(sum(packet["frame_count"] for packet in packets
                             if packet["kind"] == "audio"), 80)

    def test_dtx_cn_reconstruction_accounts_for_all_frames(self) -> None:
        packets = reference.packetize(self.frames, self.labels,
                                      packet_frames=2, dtx="cn", fec=False)
        result = reference.receive(self.frames, self.labels, packets, set())
        self.assertEqual(result["accounting_total"], 100)
        self.assertEqual(result["missing_frames"], 0)
        self.assertGreater(result["comfort_noise_frames"], 0)

    def test_packetization_grid_counts(self) -> None:
        expected = {1: 100, 2: 50, 3: 34}
        for packet_frames, count in expected.items():
            packets = reference.packetize(self.frames, self.labels,
                                          packet_frames=packet_frames,
                                          dtx="off", fec=False)
            self.assertEqual(len(packets), count)


class FecAndLossTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frames = reference.synthetic_frames(100)
        self.labels = reference.frame_labels(100)

    def _trace(self, fec: bool) -> list:
        return reference.packetize(self.frames, self.labels, packet_frames=2,
                                   dtx="off", fec=fec)

    def test_fec_copy_references_previous_packet(self) -> None:
        packets = self._trace(True)
        self.assertIsNone(packets[0]["fec_copy_of"])
        for index, packet in enumerate(packets[1:], start=1):
            self.assertEqual(packet["fec_copy_of"], index - 1)

    def test_fec_off_has_no_copies(self) -> None:
        packets = self._trace(False)
        self.assertTrue(all(packet["fec_copy_of"] is None
                            for packet in packets))

    def test_single_loss_fec_recovery_is_exact(self) -> None:
        packets = self._trace(True)
        result = reference.receive(self.frames, self.labels, packets, {2})
        self.assertEqual(result["fec_recovered_frames"], 1)
        self.assertEqual(result["plc_frames"], 1)
        self.assertTrue(result["transmitted_frames_exact"])

    def test_single_loss_without_fec_has_no_recovery(self) -> None:
        packets = self._trace(False)
        result = reference.receive(self.frames, self.labels, packets, {2})
        self.assertEqual(result["fec_recovered_frames"], 0)
        self.assertEqual(result["plc_frames"], 2)

    def test_burst_of_two_recovers_only_one(self) -> None:
        packets = self._trace(True)
        result = reference.receive(self.frames, self.labels, packets, {5, 6})
        self.assertEqual(result["fec_recovered_frames"], 1)
        self.assertGreaterEqual(result["plc_frames"], 1)
        self.assertEqual(result["accounting_total"], 100)

    def test_fec_overhead_is_positive(self) -> None:
        off = sum(packet["payload_bytes"] for packet in self._trace(False))
        on = sum(packet["payload_bytes"] for packet in self._trace(True))
        self.assertGreater(on, off)

    def test_fec_does_not_cross_a_dtx_gap(self) -> None:
        packets = reference.packetize(self.frames, self.labels,
                                      packet_frames=2, dtx="cn", fec=True)
        for packet in packets:
            if packet["fec_copy_of"] is None:
                continue
            previous = packets[packet["fec_copy_of"]]
            self.assertEqual(previous["kind"], "audio")
            self.assertEqual(previous["timestamp"] // reference.FRAME_SAMPLES
                             + previous["frame_count"],
                             packet["timestamp"] // reference.FRAME_SAMPLES)

    def test_loss_accounting_is_complete(self) -> None:
        packets = self._trace(True)
        for lost in ({2}, {5, 6}, {0}, {49}):
            result = reference.receive(self.frames, self.labels, packets, lost)
            self.assertEqual(result["accounting_total"], 100)
            self.assertEqual(sum(result["counts"].values()), 100)


class ManifestAdmissionTests(unittest.TestCase):
    def test_manifest_control_is_admitted_without_probing(self) -> None:
        result = reference.validate_manifest(reference._manifest_control(),
                                             probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertGreater(result["checks"], 0)

    def test_manifest_requires_absolute_normalized_paths(self) -> None:
        document = reference._manifest_control()
        document["source_path"] = "opus"
        self.assertFalse(reference.validate_manifest(
            document, probe_paths=False)["accepted"])

    def test_manifest_rejects_unknown_fields(self) -> None:
        document = reference._manifest_control()
        document["extra"] = 1
        self.assertEqual(reference.validate_manifest(
            document, probe_paths=False)["code"], "unexpected_field")

    def test_manifest_rejects_nonfinite_digest_length(self) -> None:
        document = reference._manifest_control()
        document["runtime_sha256"] = "0" * 63
        self.assertEqual(reference.validate_manifest(
            document, probe_paths=False)["code"], "digest_not_lower_hex64")

    def test_manifest_rejects_bool_integer(self) -> None:
        document = reference._manifest_control()
        document["packet_duration_ms"] = True
        self.assertEqual(reference.validate_manifest(
            document, probe_paths=False)["code"], "not_integer")

    def test_manifest_rejects_unsupported_packet_duration(self) -> None:
        document = reference._manifest_control()
        document["packet_duration_ms"] = 15
        self.assertEqual(reference.validate_manifest(
            document, probe_paths=False)["code"],
            "packet_duration_unsupported")

    def test_manifest_probes_absent_artifacts(self) -> None:
        result = reference.validate_manifest(reference._manifest_control())
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "artifact_absent")

    def test_manifest_rejects_wrong_sdk_geometry(self) -> None:
        for field, value in (("sdk_sample_rate_hz", 48000),
                             ("sdk_channels", 2),
                             ("sdk_frame_samples", 480)):
            document = reference._manifest_control()
            document[field] = value
            self.assertEqual(reference.validate_manifest(
                document, probe_paths=False)["code"],
                "sdk_geometry_unsupported")


class PacketAdmissionTests(unittest.TestCase):
    def test_packet_control_is_admitted(self) -> None:
        result = reference.validate_packet(reference._packet_control())
        self.assertTrue(result["accepted"])
        self.assertGreater(result["checks"], 0)

    def test_packet_rejects_bool_integer(self) -> None:
        document = reference._packet_control()
        document["seq"] = True
        self.assertEqual(reference.validate_packet(document)["code"],
                         "not_integer")

    def test_packet_rejects_float_integer(self) -> None:
        document = reference._packet_control()
        document["timestamp"] = 160.0
        self.assertEqual(reference.validate_packet(document)["code"],
                         "not_integer")

    def test_packet_rejects_digest_mismatch(self) -> None:
        document = reference._packet_control()
        document["payload_sha256"] = "0" * 64
        self.assertEqual(reference.validate_packet(document)["code"],
                         "payload_digest_mismatch")

    def test_packet_rejects_odd_hex(self) -> None:
        document = reference._packet_control()
        document["payload_hex"] = "0"
        self.assertEqual(reference.validate_packet(document)["code"],
                         "payload_hex_invalid")

    def test_packet_rejects_frame_count_out_of_range(self) -> None:
        document = reference._packet_control()
        document["frame_count"] = 4
        self.assertEqual(reference.validate_packet(document)["code"],
                         "frame_count_out_of_range")

    def test_packet_rejects_unknown_kind(self) -> None:
        document = reference._packet_control()
        document["kind"] = "opus"
        self.assertEqual(reference.validate_packet(document)["code"],
                         "kind_invalid")

    def test_packet_rejects_bad_fec_reference(self) -> None:
        document = reference._packet_control()
        document["fec_copy_of"] = document["seq"]
        self.assertEqual(reference.validate_packet(document)["code"],
                         "fec_copy_invalid")

    def test_packet_rejects_corrupt_payload_after_consistent_digest(self) -> None:
        document = reference._packet_control()
        payload = b"\xff\xe0"
        document["payload_hex"] = payload.hex()
        document["payload_bytes"] = len(payload)
        document["payload_sha256"] = hashlib.sha256(payload).hexdigest()
        self.assertIn("payload_parse_failed",
                      reference.validate_packet(document)["code"])


class TraceAdmissionTests(unittest.TestCase):
    def test_trace_control_is_admitted(self) -> None:
        result = reference.validate_trace(reference._trace_control())
        self.assertTrue(result["accepted"])

    def test_trace_rejects_empty_packets(self) -> None:
        document = reference._trace_control()
        document["packets"] = []
        self.assertEqual(reference.validate_trace(document)["code"],
                         "packet_count_out_of_range")

    def test_trace_rejects_duplicate_sequence(self) -> None:
        document = reference._trace_control()
        document["packets"][0]["seq"] = 1
        self.assertEqual(reference.validate_trace(document)["code"],
                         "seq_not_contiguous")

    def test_trace_rejects_non_increasing_timestamp(self) -> None:
        document = reference._trace_control()
        document["packets"][1]["timestamp"] = document["packets"][0]["timestamp"]
        self.assertEqual(reference.validate_trace(document)["code"],
                         "timestamp_not_increasing")

    def test_trace_rejects_unaligned_timestamp(self) -> None:
        document = reference._trace_control()
        document["packets"][1]["timestamp"] = 161
        self.assertEqual(reference.validate_trace(document)["code"],
                         "timestamp_not_frame_aligned")

    def test_trace_rejects_wrong_duration(self) -> None:
        document = reference._trace_control()
        document["packets"][1]["duration_samples"] = 160
        self.assertEqual(reference.validate_trace(document)["code"],
                         "duration_mismatch")

    def test_trace_rejects_bad_fec_copy(self) -> None:
        document = reference._trace_control()
        document["packets"][2]["fec_copy_of"] = 0
        self.assertEqual(reference.validate_trace(document)["code"],
                         "fec_copy_not_previous")

    def test_trace_rejects_unknown_dtx(self) -> None:
        document = reference._trace_control()
        document["dtx"] = "maybe"
        self.assertEqual(reference.validate_trace(document)["code"],
                         "dtx_mode_invalid")

    def test_trace_rejects_bool_fec(self) -> None:
        document = reference._trace_control()
        document["fec"] = 1
        self.assertEqual(reference.validate_trace(document)["code"],
                         "fec_not_boolean")


class AdmissionMatrixTests(unittest.TestCase):
    def test_all_adverse_cases_are_rejected_with_state_unchanged(self) -> None:
        matrix = reference.admission_controls()
        self.assertGreaterEqual(len(matrix["cases"]), 45)
        for case in matrix["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertFalse(case["qualifies"], case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertTrue(case["code"], case["id"])

    def test_three_schema_controls_are_accepted_but_not_evidence(self) -> None:
        matrix = reference.admission_controls()
        self.assertEqual([control["id"] for control in matrix["controls"]],
                         ["CTL-01", "CTL-02", "CTL-03"])
        for control in matrix["controls"]:
            self.assertEqual(control["status"], "accepted_schema_control")
            self.assertEqual(control["evidence_class"],
                             "synthetic_schema_control_not_evidence")
            self.assertFalse(control["qualifies"])

    def test_json_controls_match_expected_codes(self) -> None:
        matrix = reference.admission_controls()
        json_cases = [case for case in matrix["cases"]
                      if case["kind"] == "strict_json"]
        self.assertEqual([case["id"] for case in json_cases],
                         ["JSON-01", "JSON-02", "JSON-03", "JSON-04"])
        self.assertTrue(all(case["message_matches"] for case in json_cases))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_report_is_canonical_and_deterministic(self) -> None:
        first = reference.canonical_bytes(self.report)
        second = reference.canonical_bytes(reference.build_report())
        self.assertEqual(first, second)

    def test_report_bytes_match_committed_file(self) -> None:
        self.assertEqual((HERE / "report.json").read_bytes(),
                         reference.canonical_bytes(self.report))

    def test_report_sidecar_matches(self) -> None:
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")

    def test_report_contains_no_floats(self) -> None:
        for value in walk_numbers(self.report):
            self.assertNotIsInstance(value, float)

    def test_report_decision_and_status(self) -> None:
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["candidate_status"],
                         "proposal_only_not_qualified")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["no_missing_result_qualifies"])

    def test_qualification_is_not_qualified(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertEqual(qualification["decision"], "DEFER")
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["all_required_results_present"])
        self.assertFalse(qualification["candidate_qualified"])
        self.assertFalse(qualification["missing_result_promoted"])

    def test_all_required_results_true(self) -> None:
        self.assertTrue(all(self.report["required_results"].values()))

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(tuple(gate["id"] for gate in gates), GATE_IDS)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])

    def test_six_open_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(tuple(row["id"] for row in blockers), BLOCKER_IDS)
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])

    def test_six_absent_artifacts(self) -> None:
        artifacts = self.report["required_artifacts"]
        self.assertEqual(tuple(row["id"] for row in artifacts), ARTIFACT_IDS)
        for row in artifacts:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_no_public_boundary_change(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "descriptor_registry_change", "shared_cmakelists_change",
                    "shared_ci_change", "build_option_change",
                    "installed_v0_behavior_change", "board_or_handoff_changed",
                    "processor_exposure", "files_outside_task_directory_written"):
            self.assertFalse(boundary[key], key)
        self.assertTrue(boundary["task_local_only"])
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_claims_no_runtime_or_result(self) -> None:
        scope = self.report["scope"]
        for key in ("source_present", "runtime_present", "runtime_executed",
                    "codec_runtime_linked", "codec_runtime_executed",
                    "real_packet_trace", "real_audio", "network_capture",
                    "dtx_fec_cn_codec_operation", "listening",
                    "device_timing", "benchmark", "release_claim",
                    "network_used", "download_attempted"):
            self.assertFalse(scope[key], key)
        self.assertTrue(scope["task_local_contract_model_executed"])

    def test_public_geometry_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sdk_callback_invoked"])

    def test_absence_summary(self) -> None:
        evidence = self.report["absence_evidence"]
        self.assertTrue(evidence["summary"]["all_probes_absent"])
        self.assertEqual(evidence["summary"]["present_count"], 0)
        self.assertFalse(evidence["summary"]["download_attempted"])
        self.assertEqual(len(evidence["probes"]),
                         len(reference.ABSENCE_PROBES))

    def test_observed_binary_is_never_admitted(self) -> None:
        observed = self.report["absence_evidence"][
            "observed_unqualified_binaries"]
        self.assertEqual(len(observed), 1)
        row = observed[0]
        self.assertFalse(row["admitted"])
        self.assertFalse(row["used_for_evidence"])
        self.assertFalse(row["linked"])
        self.assertFalse(row["executed_by_package"])
        self.assertFalse(row["opus_license_text_present"])
        self.assertIsNone(row["source_revision"])
        self.assertEqual(len(row["sha256"]), 64)

    def test_tool_profile_is_blocked_except_malformed_inputs(self) -> None:
        profile = self.report["tool_profile"]
        self.assertEqual(profile["status"], "blocked")
        self.assertIsNone(profile["runtime_version"])
        self.assertIsNone(profile["install_location"])
        self.assertIsNone(profile["provenance"])
        self.assertTrue(profile["malformed_inputs_checked"])
        for key in ("clean_checkout_verified", "typical_use_performed",
                    "caller_owned_inputs_admitted",
                    "missing_optional_selection_exercised",
                    "compile_build_evidence",
                    "codec_synthetic_runtime_evidence",
                    "measured_workload_support"):
            self.assertFalse(profile[key], key)
        self.assertTrue(profile["task_local_contract_model_executed"])
        self.assertFalse(profile["task_local_contract_model_is_runtime_evidence"])
        self.assertEqual(tuple(row["id"] for row in profile["rows"]), TOOL_IDS)

    def test_prohibited_claims_present(self) -> None:
        claims = self.report["prohibited_claims"]
        self.assertEqual(len(claims), 6)
        joined = " ".join(claims)
        self.assertIn("No Opus", joined)
        self.assertIn("No real packet trace", joined)
        self.assertIn("No benchmark", joined)

    def test_conditions_complete(self) -> None:
        conditions = self.report["conditions"]
        self.assertEqual(sorted(conditions["packetization_grid"]),
                         ["10ms", "20ms", "30ms"])
        self.assertEqual(sorted(conditions["dtx"]), ["cn", "off", "omit"])
        self.assertGreater(conditions["fec"]["overhead_bytes"], 0)
        self.assertEqual(conditions["fec"]["recovery_depth_packets"], 1)
        self.assertIn("single_fec_on", conditions["loss"])
        self.assertIn("burst_two_fec_on", conditions["loss"])

    def test_dtx_and_fec_behavior(self) -> None:
        conditions = self.report["conditions"]
        self.assertLess(conditions["dtx"]["cn"]["packet_count"],
                        conditions["dtx"]["off"]["packet_count"])
        self.assertEqual(conditions["dtx"]["omit"][
            "comfort_noise_packets"], 0)
        self.assertEqual(conditions["dtx"]["cn"][
            "comfort_noise_packets"], 2)
        self.assertEqual(conditions["loss"]["single_fec_on"][
            "reconstruction"]["fec_recovered_frames"], 1)
        self.assertEqual(conditions["loss"]["burst_two_fec_on"][
            "reconstruction"]["fec_recovered_frames"], 1)
        self.assertGreater(conditions["loss"]["burst_two_fec_on"][
            "reconstruction"]["plc_frames"], 0)

    def test_primary_trace_is_distinct_from_pcm(self) -> None:
        trace = self.report["packet_trace"]
        self.assertTrue(trace["packets_are_not_pcm"])
        self.assertTrue(trace["payload_hex_included"])
        self.assertFalse(trace["codec_runtime_used"])
        self.assertTrue(trace["validation"]["accepted"])
        self.assertGreater(trace["packet_count"], 0)
        self.assertEqual(trace["reconstruction"]["accounting_total"],
                         trace["signal_frames"])
        self.assertTrue(all("payload_hex" in packet for packet in trace["packets"]))
        self.assertTrue(any(packet["kind"] == "comfort_noise"
                            for packet in trace["packets"]))

    def test_admission_summary(self) -> None:
        summary = self.report["admission"]["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertEqual(summary["accepted_schema_controls"], 3)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["runtime_invoked"])
        self.assertFalse(summary["codec_invoked"])
        self.assertFalse(summary["replay_performed"])

    def test_linked_row_identity_is_stable_only(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertIn("status", identity["mutable_fields_excluded"])

    def test_regeneration_declaration(self) -> None:
        self.assertEqual(self.report["regeneration"]["runs"], 3)
        self.assertTrue(self.report["regeneration"]["byte_identical"])


class ContractTests(unittest.TestCase):
    def test_contract_is_canonical(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        self.assertEqual(reference.canonical_bytes(contract),
                         (HERE / "contract.json").read_bytes())

    def test_contract_validates(self) -> None:
        reference.validate_contract(
            reference.read_strict_json(HERE / "contract.json"))

    def test_contract_matches_generator(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        self.assertEqual(contract, reference.contract_document())

    def test_contract_pin_tables_and_counts(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        self.assertEqual(contract["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(contract["boundary_pins"], reference.BOUNDARY_PINS)
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertEqual(len(contract["required_artifacts"]), 6)
        self.assertEqual(len(contract["exact_blockers"]), 6)
        self.assertTrue(contract["no_missing_result_qualifies"])
        self.assertTrue(contract["board_status_is_observation_only"])
        self.assertFalse(contract["board_file_pinned"])

    def test_contract_rejects_wrong_gate_count(self) -> None:
        contract = reference.contract_document()
        contract["release_gates"] = contract["release_gates"][:7]
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_rejects_promotion(self) -> None:
        contract = reference.contract_document()
        contract["decision"] = "PROMOTE"
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_rejects_mutable_board_projection(self) -> None:
        contract = reference.contract_document()
        contract["board_row_projection"] = dict(
            contract["board_row_projection"], status="in_progress")
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_rejects_packet_model_claim(self) -> None:
        contract = reference.contract_document()
        contract["packet_contract"] = dict(contract["packet_contract"],
                                           not_opus=False)
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_admission_ids_match_matrix(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        cases = [case["id"] for case in
                 reference.admission_controls()["cases"]]
        self.assertEqual(contract["admission_contract"]["case_ids"], cases)


class SourcesManifestTests(unittest.TestCase):
    def test_sources_manifest_is_deterministic(self) -> None:
        import run  # noqa: PLC0415 - deterministic task-local module
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         run.sources_bytes())

    def test_every_local_file_is_pinned(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        for path in sorted(HERE.iterdir()):
            if not path.is_file() or path.name == "SOURCES.sha256":
                continue
            self.assertIn(reference.TASK_PREFIX + path.name, text,
                          path.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
