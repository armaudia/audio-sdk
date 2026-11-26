# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the SDK-WEBRTC-NETEQ blocker package.

No network, no WebRTC/NetEq/codec runtime, no audio, no skips. Every check is
task-local and stdlib-only.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as reference  # noqa: E402

MANIFEST_ADVERSE_IDS = (
    "MISS-01", "INV-01", "INV-02", "INV-03", "INV-04", "INV-05", "INV-06",
    "INV-07", "INV-08", "INV-09", "INV-10", "INV-11", "INV-12", "INV-13",
    "INV-14", "INV-15", "INV-16", "PRS-01",
)
TRACE_ADVERSE_IDS = (
    "TRC-01", "TRC-02", "TRC-03", "TRC-04", "TRC-05", "TRC-06", "TRC-07",
    "TRC-08", "TRC-09", "TRC-10", "TRC-11", "TRC-12", "TRC-13", "TRC-14",
    "TRC-15", "TRC-16", "TRC-17", "TRC-18", "TRC-19",
)
JSON_ADVERSE_IDS = ("JSON-01", "JSON-02", "JSON-03", "JSON-04")
GATE_IDS = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")


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

    def test_contract_is_canonical(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        self.assertEqual(reference.canonical_bytes(contract),
                         (HERE / "contract.json").read_bytes())

    def test_contract_validates(self) -> None:
        reference.validate_contract(reference.read_strict_json(HERE / "contract.json"))

    def test_sha256_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "blob"
            path.write_bytes(b"neteq")
            self.assertEqual(reference.sha256_file(path),
                             hashlib.sha256(b"neteq").hexdigest())


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
                         reference.board_row_digest(reference.BOARD_ROW_PROJECTION))

    def test_board_projection_ignores_mutable_fields(self) -> None:
        board = reference.read_strict_json(reference.AUDIO_ROOT
                                           / reference.BOARD_TASK_ROW)
        mutated = copy.deepcopy(board)
        for row in mutated["tasks"]:
            if row.get("id") == reference.TASK:
                row["status"] = "blocked"
                row["owner"] = "someone-else"
                row["blocked_reason"] = "mutable"
                row["review"] = "changes_requested"
                row["claim"] = None
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TASKS.json"
            path.write_bytes(reference.canonical_bytes(mutated))
            projection = reference.board_row_projection(path)
        self.assertEqual(projection, reference.BOARD_ROW_PROJECTION)

    def test_board_duplicate_row_rejected(self) -> None:
        board = reference.read_strict_json(reference.AUDIO_ROOT
                                           / reference.BOARD_TASK_ROW)
        duplicated = copy.deepcopy(board)
        duplicated["tasks"].append(copy.deepcopy(reference.BOARD_ROW_PROJECTION))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TASKS.json"
            path.write_bytes(reference.canonical_bytes(duplicated))
            with self.assertRaises(ValueError):
                reference.board_row_projection(path)

    def test_absence_probes_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(row["present"] is False for row in rows))

    def test_absence_guard_raises_when_artifact_appears(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data/checkouts/webrtc").mkdir(parents=True)
            with self.assertRaises(ValueError):
                reference.absence_probes(root, ("data/checkouts/webrtc",),
                                         worktree=root)

    def test_absence_summary(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        summary = reference.absence_summary(rows)
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])


class ManifestAdmissionTests(unittest.TestCase):
    def test_schema_control_admitted(self) -> None:
        result = reference.validate_manifest(reference._manifest_control(),
                                             probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "manifest_admitted")
        self.assertGreaterEqual(result["checks"], 1)

    def test_schema_control_without_artifacts_is_rejected(self) -> None:
        result = reference.validate_manifest(reference._manifest_control(),
                                             probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "artifact_absent")
        self.assertEqual(result["field"], "source_path")

    def test_valid_manifest_probes_real_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = reference._manifest_control()
            for field in reference.MANIFEST_PATH_FIELDS:
                payload = (field + "-bytes").encode("ascii")
                path = root / field.replace("_path", "")
                path.write_bytes(payload)
                document[field] = str(path)
                document[field.replace("_path", "_sha256")] = hashlib.sha256(
                    payload).hexdigest()
            result = reference.validate_manifest(document, probe_paths=True)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "manifest_admitted")

    def test_valid_manifest_detects_wrong_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = reference._manifest_control()
            for field in reference.MANIFEST_PATH_FIELDS:
                path = root / field.replace("_path", "")
                path.write_bytes(b"payload")
                document[field] = str(path)
                document[field.replace("_path", "_sha256")] = "a" * 64
            result = reference.validate_manifest(document, probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "artifact_digest_mismatch")

    def test_manifest_adverse_matrix(self) -> None:
        cases = {case["id"]: case for case in
                 reference.admission_controls()["cases"]}
        for case_id in MANIFEST_ADVERSE_IDS:
            with self.subTest(case=case_id):
                case = cases[case_id]
                self.assertEqual(case["status"], "rejected")
                self.assertTrue(case["code"])
                self.assertFalse(case["qualifies"])
                self.assertTrue(case["state_unchanged"])

    def test_manifest_missing_field_is_first_required_field(self) -> None:
        document = reference._manifest_control()
        del document["source_path"]
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertEqual(result["code"], "missing_field")
        self.assertEqual(result["field"], "source_path")

    def test_manifest_bool_is_not_integer(self) -> None:
        document = reference._manifest_control()
        document["sdk_channels"] = True
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertEqual(result["code"], "not_integer")
        self.assertEqual(result["field"], "sdk_channels")

    def test_manifest_nonfinite_float_rejected(self) -> None:
        document = reference._manifest_control()
        document["internal_sample_rate_hz"] = float("inf")
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertEqual(result["code"], "not_integer")

    def test_manifest_edge_exact_geometry(self) -> None:
        document = reference._manifest_control()
        document["internal_sample_rate_hz"] = 16000
        document["packet_duration_ms"] = 120
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(16000 * 120 % 1000, 0)


class TraceAdmissionTests(unittest.TestCase):
    def test_schema_control_admitted_with_reordering(self) -> None:
        document = reference._trace_control()
        result = reference.validate_trace(document)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "trace_admitted")
        self.assertNotEqual([packet["seq"] for packet in document["packets"]],
                            sorted(packet["seq"] for packet in document["packets"]))

    def test_trace_adverse_matrix(self) -> None:
        cases = {case["id"]: case for case in
                 reference.admission_controls()["cases"]}
        for case_id in TRACE_ADVERSE_IDS:
            with self.subTest(case=case_id):
                case = cases[case_id]
                self.assertEqual(case["status"], "rejected")
                self.assertTrue(case["code"])
                self.assertFalse(case["qualifies"])
                self.assertTrue(case["state_unchanged"])

    def test_trace_rejects_nonfinite_float_field(self) -> None:
        document = reference._trace_control()
        document["packets"][0]["rtp_timestamp"] = float("nan")
        self.assertEqual(reference.validate_trace(document)["code"],
                         "not_integer")

    def test_trace_rejects_unknown_packet_field(self) -> None:
        document = reference._trace_control()
        document["packets"][0]["jitter_ms"] = 4.0
        result = reference.validate_trace(document)
        self.assertEqual(result["code"], "unexpected_field")
        self.assertEqual(result["field"], "packets[0].jitter_ms")

    def test_trace_rejects_empty_trace(self) -> None:
        document = reference._trace_control()
        document["packets"] = []
        self.assertEqual(reference.validate_trace(document)["code"],
                         "packet_count_out_of_range")

    def test_trace_digest_relation_to_sequence(self) -> None:
        document = reference._trace_control()
        document["packets"][1]["rtp_timestamp"] = 1440
        self.assertEqual(reference.validate_trace(document)["code"],
                         "timestamp_seq_mismatch")

    def test_trace_wraparound_arithmetic(self) -> None:
        document = reference._trace_control()
        document["packets"] = [
            {"seq": 65534, "rtp_timestamp": 4294966320, "arrival_us": 0,
             "duration_samples": 480, "payload_bytes": 4,
             "payload_sha256": "a" * 64, "status": "received"},
            {"seq": 65535, "rtp_timestamp": 4294966800, "arrival_us": 100,
             "duration_samples": 480, "payload_bytes": 4,
             "payload_sha256": "b" * 64, "status": "received"},
            {"seq": 0, "rtp_timestamp": 4294967280, "arrival_us": 200,
             "duration_samples": 480, "payload_bytes": 4,
             "payload_sha256": "c" * 64, "status": "received"},
        ]
        self.assertTrue(reference.validate_trace(document)["accepted"])


class AdmissionControlTests(unittest.TestCase):
    def test_case_matrix_is_complete(self) -> None:
        controls = reference.admission_controls()
        ids = [case["id"] for case in controls["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        expected = set(MANIFEST_ADVERSE_IDS) | set(TRACE_ADVERSE_IDS) | set(
            JSON_ADVERSE_IDS)
        self.assertEqual(set(ids), expected)

    def test_every_case_is_nonqualifying(self) -> None:
        for case in reference.admission_controls()["cases"]:
            self.assertFalse(case["qualifies"])
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["evidence_class"],
                             "synthetic_admission_control")

    def test_json_cases_are_rejected_by_loader(self) -> None:
        cases = [case for case in reference.admission_controls()["cases"]
                 if case["kind"] == "strict_json"]
        self.assertEqual(len(cases), 4)
        self.assertTrue(all(case["message_matches"] for case in cases))

    def test_schema_controls_are_explicitly_not_evidence(self) -> None:
        controls = reference.admission_controls()["controls"]
        self.assertEqual([row["id"] for row in controls], ["CTL-01", "CTL-02"])
        for row in controls:
            self.assertFalse(row["qualifies"])
            self.assertEqual(row["status"], "accepted_schema_control")
            self.assertEqual(row["evidence_class"],
                             "synthetic_schema_control_not_evidence")
        self.assertFalse(controls[1]["reordering_performed"])
        self.assertFalse(controls[1]["playout_performed"])
        self.assertFalse(controls[1]["timing_analysis_performed"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.read_strict_json(HERE / "contract.json")
        cls.report = reference.build_report()

    def test_identity_and_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component_id"], reference.COMPONENT_ID)
        self.assertEqual(report["mode"], "feasibility")
        self.assertEqual(report["profile"], "tool")
        self.assertEqual(report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["disposition"]["promotion"], "defer")
        self.assertEqual(report["disposition"]["production_exposure"], "DEFER")
        self.assertTrue(report["disposition"]["proposal_only"])
        self.assertTrue(report["disposition"]["incomplete"])
        self.assertTrue(report["disposition"]["not_qualified"])
        for key in ("expose_as_processor", "registered", "default_enabled",
                    "missing_result_qualifies"):
            self.assertFalse(report["disposition"][key])

    def test_no_scope_or_claim_is_true_outside_write_scope(self) -> None:
        for section in ("boundary", "scope", "qualification"):
            for key, value in self.report[section].items():
                if key == "task_local_only":
                    self.assertTrue(value)
                    continue
                if key == "not_qualified":
                    self.assertTrue(value)
                    continue
                if key == "all_release_gates_blocked":
                    self.assertTrue(value)
                    continue
                self.assertFalse(value, section + "." + key)

    def test_eight_blocked_gates_with_stable_linked_row(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(tuple(gate["id"] for gate in gates), GATE_IDS)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"]["task_id"], reference.TASK)
            self.assertEqual(gate["linked_row"]["component_id"],
                             reference.COMPONENT_ID)
            self.assertNotIn("status", gate["linked_row"])

    def test_linked_row_identity_is_stable_identity_only(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"], reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(reference.BOARD_ROW_PROJECTION))

    def test_required_artifacts_all_absent(self) -> None:
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 6)
        for artifact in artifacts:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
            self.assertTrue(artifact["requirement"])

    def test_exact_blockers_link_existing_artifacts_and_gates(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in self.report["required_artifacts"]}
        gate_ids = {row["id"] for row in self.report["gates"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(set(blocker["linked_gates"]) <= gate_ids)

    def test_absence_evidence(self) -> None:
        evidence = self.report["absence_evidence"]
        self.assertEqual(len(evidence["probes"]), len(reference.ABSENCE_PROBES))
        self.assertTrue(evidence["summary"]["all_probes_absent"])
        self.assertEqual(evidence["summary"]["present_count"], 0)

    def test_tool_profile_applied_and_blocked(self) -> None:
        profile = self.report["tool_profile"]
        self.assertEqual(profile["profile"], "tool")
        self.assertEqual(profile["status"], "blocked")
        self.assertIsNone(profile["runtime_version"])
        self.assertIsNone(profile["install_location"])
        self.assertFalse(profile["clean_checkout_verified"])
        self.assertFalse(profile["typical_use_performed"])
        self.assertFalse(profile["caller_owned_inputs_admitted"])
        self.assertTrue(profile["malformed_inputs_checked"])
        self.assertFalse(profile["compile_build_evidence"])
        self.assertFalse(profile["synthetic_runtime_evidence"])
        self.assertFalse(profile["measured_workload_support"])
        self.assertEqual([row["id"] for row in profile["rows"]],
                         ["TOOL-01", "TOOL-02", "TOOL-03", "TOOL-04", "TOOL-05",
                          "TOOL-06"])

    def test_admission_summary(self) -> None:
        admission = self.report["admission"]
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 41)
        self.assertEqual(summary["rejected_count"], 41)
        self.assertEqual(summary["accepted_schema_controls"], 2)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["runtime_invoked"])
        self.assertFalse(summary["replay_performed"])

    def test_report_matches_contract_sections(self) -> None:
        for key in ("disposition", "boundary", "scope", "public_v0_geometry",
                    "exact_scope", "qualification", "linked_row_identity",
                    "required_artifacts", "exact_blockers",
                    "prohibited_claims", "regeneration", "reproduction"):
            self.assertEqual(self.report[key], self.contract[key], key)
        self.assertEqual(self.report["gates"], self.contract["release_gates"])
        self.assertEqual(self.report["source_pins"],
                         {row: {"sha256": digest, "actual": digest,
                                "verified": True}
                          for row, digest in reference.SOURCE_PINS.items()})
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_bytes(self.report)
        second = reference.canonical_bytes(reference.build_report())
        self.assertEqual(first, second)

    def test_report_contains_no_floats_or_booleans_in_numbers(self) -> None:
        for value in walk_numbers(self.report):
            self.assertNotIsInstance(value, float)

    def test_report_claims_no_runtime_or_playout(self) -> None:
        text = reference.canonical_text(self.report)
        self.assertNotIn('"playout_performed":true', text)
        self.assertNotIn('"runtime_executed":true', text)
        self.assertNotIn('"listening":true', text)
        self.assertNotIn('"device_timing":true', text)
        self.assertNotIn('"benchmark":true', text)
        self.assertNotIn('"release_claim":true', text)

    def test_prohibited_claims_present(self) -> None:
        claims = self.report["prohibited_claims"]
        self.assertEqual(len(claims), 6)
        joined = " ".join(claims)
        self.assertIn("No NetEq", joined)
        self.assertIn("No jitter", joined)
        self.assertIn("No audio", joined)

    def test_regeneration_declaration(self) -> None:
        self.assertEqual(self.report["regeneration"]["runs"], 3)
        self.assertTrue(self.report["regeneration"]["byte_identical"])

    def test_public_geometry_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sdk_callback_invoked"])


class ContractTests(unittest.TestCase):
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
        contract = reference.read_strict_json(HERE / "contract.json")
        broken = dict(contract)
        broken["release_gates"] = contract["release_gates"][:7]
        with self.assertRaises(ValueError):
            reference.validate_contract(broken)

    def test_contract_rejects_promotion(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        broken = dict(contract)
        broken["decision"] = "PROMOTE"
        with self.assertRaises(ValueError):
            reference.validate_contract(broken)

    def test_contract_rejects_mutable_board_projection(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        broken = dict(contract)
        broken["board_row_projection"] = dict(contract["board_row_projection"],
                                               mode="implementation")
        with self.assertRaises(ValueError):
            reference.validate_contract(broken)

    def test_contract_admission_ids_match_matrix(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        cases = [case["id"] for case in
                 reference.admission_controls()["cases"]]
        self.assertEqual(contract["admission_contract"]["case_ids"], cases)


if __name__ == "__main__":
    unittest.main(verbosity=2)
