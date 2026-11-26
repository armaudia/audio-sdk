# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the task-local adapter readiness bundle."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nan_constant_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonfinite_json_constant"):
            reference.loads_strict('{"a":NaN}')

    def test_infinity_constant_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonfinite_json_constant"):
            reference.loads_strict('{"a":Infinity}')

    def test_root_array_rejected(self):
        with self.assertRaisesRegex(ValueError, "json_root_not_object"):
            reference.loads_strict("[]")

    def test_byte_order_mark_rejected(self):
        with self.assertRaisesRegex(ValueError, "json_byte_order_mark"):
            reference.loads_strict('\ufeff{"a":1}')

    def test_canonical_is_sorted_compact_and_newline_terminated(self):
        text = reference.canonical_text({"b": 1, "a": [2, 3]})
        self.assertEqual(text, '{"a":[2,3],"b":1}\n')
        self.assertNotIn(" ", text)


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self):
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_boundary_pins_match(self):
        rows = reference.pin_rows(reference.BOUNDARY_PINS, reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_board_projection_has_only_stable_fields(self):
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(sorted(row)), tuple(sorted(
            reference.BOARD_ROW_FIELDS)))
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(row["component"], reference.COMPONENT_ID)
        for mutable in ("status", "owner", "claim", "review", "handoff",
                        "blocked_reason", "dispatch_priority"):
            self.assertNotIn(mutable, row)

    def test_board_row_digest_is_projection_digest(self):
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        expected = hashlib.sha256(reference.canonical_bytes(row)).hexdigest()
        self.assertEqual(reference.board_row_digest(row), expected)

    def test_linked_rows_are_declared_dependencies(self):
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        self.assertEqual(rows[0]["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                          "SDK-FND-PROVIDER"])


class AbsenceTests(unittest.TestCase):
    def test_workspace_probes_absent(self):
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_worktree_probes_absent(self):
        rows = reference.worktree_absence_probes()
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_home_probes_absent(self):
        rows = reference.home_absence_probes()
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_absence_summary_totals(self):
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.worktree_absence_probes(),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 24)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertFalse(summary[key])

    def test_runtime_modules_are_absent(self):
        readiness = reference.runtime_readiness()
        self.assertFalse(readiness["importable"])
        self.assertFalse(readiness["module_spec_found"])
        self.assertTrue(readiness["blocked"])
        self.assertFalse(readiness["runtime_imported"])
        self.assertEqual(readiness["exact_error"],
                         "ModuleNotFoundError: No module named 'torch'")
        self.assertEqual(len(readiness["modules"]),
                         len(reference.RUNTIME_MODULES))
        self.assertTrue(all(not row["module_spec_found"]
                            for row in readiness["modules"]))

    def test_runtime_interpreter_matches_pinned_verifier(self):
        if reference.platform.python_version() == \
                reference.REQUIRED_INTERPRETER:
            self.assertTrue(reference.runtime_readiness()
                            ["interpreter_matches"])

    def test_adapter_sources_present_and_pinned(self):
        presence = reference.source_presence()
        self.assertTrue(presence["adapter_sources_present"])
        self.assertFalse(presence["runtime_present"])
        self.assertFalse(presence["weights_present"])
        self.assertFalse(
            presence["exact_source_runtime_weights_conjunction_present"])
        self.assertEqual(set(presence["adapter_profiles"]),
                         set(reference.ADAPTER_PROFILES))
        for rows in presence["adapter_profiles"].values():
            self.assertTrue(all(row["verified"] for row in rows.values()))
            self.assertTrue(all(not row["executed_here"]
                                for row in rows.values()))

    def test_protocol_snippets_present(self):
        rows = reference.protocol_snippet_check()
        self.assertEqual(set(rows), set(reference.PROTOCOL_SNIPPETS))
        for row in rows.values():
            self.assertTrue(row["verified"])
            self.assertEqual(row["snippets_required"],
                             row["snippets_found"])


class AdmissionTests(unittest.TestCase):
    def test_control_manifest_is_accepted_without_mutation(self):
        manifest = reference.control_manifest()
        before = copy.deepcopy(manifest)
        reference.validate_manifest(manifest)
        self.assertEqual(manifest, before)

    def test_all_rejection_cases_reject(self):
        cases = reference.admission_cases()
        self.assertEqual(len(cases), 83)
        self.assertEqual(len({case["id"] for case in cases}), 83)
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])

    def test_representative_rejection_codes(self):
        codes = {case["id"]: case["code"]
                 for case in reference.admission_cases()}
        self.assertEqual(codes["DOC-01"], "duplicate_json_key")
        self.assertEqual(codes["DOC-02"], "nonfinite_json_constant")
        self.assertEqual(codes["AD-01"], "adapter_identity_not_allowed")
        self.assertEqual(codes["RT-02"], "runtime_torch_mismatch")
        self.assertEqual(codes["AS-05"], "assets_byte_count_mismatch")
        self.assertEqual(codes["RI-01"],
                         "rights_claims_qualified_wrong_value")
        self.assertEqual(codes["NF-01"], "output_peak_nonfinite")

    def test_admission_summary_never_qualifies(self):
        admission = reference.build_admission()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 83)
        self.assertEqual(summary["rejected_count"], 83)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(admission["control"]["label"],
                         "synthetic_schema_control_not_evidence")
        self.assertFalse(admission["control"]["qualifies"])

    def test_unknown_runtime_and_streaming_mode_rejected(self):
        for mutate, pattern in (
                (lambda row: row["runtime"].update(python="3.12.16"),
                 "runtime_python_mismatch"),
                (lambda row: row["adapter"].update(mode="streaming"),
                 "adapter_mode"),
                (lambda row: row["command"].update(network="allowed"),
                 "command_network"),
                (lambda row: row["rights"].update(claims_qualified=True),
                 "rights_claims_qualified_wrong_value")):
            manifest = reference.control_manifest()
            mutate(manifest)
            with self.assertRaisesRegex(reference.AdmissionError, pattern):
                reference.validate_manifest(manifest)

    def test_sepformer_profile_is_accepted_when_exact(self):
        profile = reference.ADAPTER_PROFILES[reference.SEPFORMER_ID]
        manifest = reference.control_manifest()
        manifest["adapter"].update(
            identity=reference.SEPFORMER_ID,
            adapter_sha256=profile["adapter_source"]["sha256"],
            descriptor_sha256=profile["adapter_descriptor"]["sha256"])
        manifest["assets"] = [
            {
                "asset_id": "sep-asset-%02d" % index,
                "name": name,
                "byte_count": 1024,
                "sha256": pinned["sha256"],
                "terms_sha256": "%064x" % index,
                "present_at_review": True,
            }
            for index, (name, pinned) in
            enumerate(sorted(profile["assets"].items()), start=1)
        ]
        reference.validate_manifest(manifest)


class EnvelopeTests(unittest.TestCase):
    def test_request_round_trip_and_identity(self):
        payload = reference.validate_protocol_request(
            reference.protocol_request())
        self.assertEqual(len(payload), reference.FRAME_BYTES)
        adapter = reference.SyntheticEnvelopeAdapter()
        result = adapter.process(reference.protocol_request())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["sha256"],
                         hashlib.sha256(payload).hexdigest())
        self.assertEqual(bytes.fromhex(result["output"]["payload_hex"]),
                         payload)
        self.assertFalse(result["runtime_invoked"])

    def test_probe_is_deterministic(self):
        first = reference.synthetic_envelope_probe()
        second = reference.synthetic_envelope_probe()
        self.assertEqual(first, second)
        self.assertEqual(first["summary"]["case_count"], 15)
        self.assertEqual(first["summary"]["rejected_count"], 15)
        self.assertFalse(first["qualifies"])
        use = first["typical_api_use"]
        self.assertTrue(use["identity_exact"])
        self.assertTrue(use["replay_identical"])
        self.assertTrue(use["reset_replay_identical"])
        self.assertTrue(use["close_idempotent"])
        self.assertTrue(use["run_after_close_rejected"])
        self.assertFalse(use["timing_measured"])

    def test_lifecycle_close_is_idempotent_and_fails_closed(self):
        adapter = reference.SyntheticEnvelopeAdapter()
        request = reference.protocol_request()
        adapter.process(request)
        adapter.close()
        adapter.close()
        with self.assertRaisesRegex(reference.AdmissionError,
                                    "adapter_closed"):
            adapter.process(request)

    def test_envelope_cases_leave_state_unchanged(self):
        for case in reference.envelope_cases():
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["calls_after_rejection"], 0)
            self.assertTrue(case["state_unchanged"])
            self.assertFalse(case["qualifies"])

    def test_nonfinite_payload_rejected(self):
        request = reference.protocol_request()
        raw = bytearray(bytes.fromhex(request["input"]["payload_hex"]))
        raw[0:4] = reference.struct.pack("<f", math.inf)
        request["input"]["payload_hex"] = raw.hex()
        request["input"]["sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(reference.AdmissionError,
                                    "payload_nonfinite"):
            reference.validate_protocol_request(request)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()
        cls.text, cls.digest = reference.canonical_report(cls.report)

    def test_decision_and_qualification(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        qualification = self.report["qualification"]
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertFalse(qualification["release_claim"])

    def test_eight_blocked_gates(self):
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], "RG-%02d" % index)
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["boundary"]["linked_row"])

    def test_six_open_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["required_action"])

    def test_one_present_artifact_and_six_blocked(self):
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])

    def test_tool_profile_statuses(self):
        rows = self.report["tool_profile"]["requirements"]
        self.assertEqual(len(rows), 9)
        statuses = {row["id"]: row["status"] for row in rows}
        self.assertEqual(statuses, reference.TOOL_EXPECTED_STATUS)
        self.assertFalse(self.report["tool_profile"]["summary"]
                         ["tool_profile_satisfied"])

    def test_mode_and_platform_separate(self):
        mode = self.report["mode_platform"]
        self.assertEqual(len(mode["rows"]), 3)
        self.assertFalse(mode["streaming_mode_present"])
        self.assertEqual(mode["modes_measured"], [])
        self.assertEqual(mode["platforms_measured"], [])
        self.assertFalse(mode["device_timing_measured"])

    def test_historical_execution_is_provenance_only(self):
        historical = self.report["historical_execution"]
        self.assertTrue(historical["provenance_only"])
        self.assertFalse(historical["reproduced_here"])
        self.assertFalse(historical["used_for_evidence"])
        self.assertFalse(historical["qualifies"])
        self.assertEqual(len(historical["runs"]), 2)

    def test_contract_digest_matches(self):
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_contract_validation(self):
        reference.validate_contract(self.contract)

    def test_report_is_canonical_and_float_free(self):
        self.assertEqual(self.text, reference.canonical_text(self.report))
        reference._no_floats(self.report)
        self.assertEqual(self.digest,
                         hashlib.sha256(self.text.encode("utf-8")).hexdigest())

    def test_report_build_is_repeatable(self):
        again = reference.build_report()
        self.assertEqual(reference.object_digest(again), self.digest)

    def test_pins_are_embedded_and_verified(self):
        self.assertEqual(set(self.report["source_pins"]),
                         set(reference.SOURCE_PINS))
        self.assertEqual(set(self.report["boundary_pins"]),
                         set(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"]
                            for row in self.report["source_pins"].values()))
        self.assertTrue(all(row["verified"]
                            for row in self.report["boundary_pins"].values()))

    def test_absence_evidence_totals(self):
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["probe_count"], 24)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])

    def test_runtime_and_source_presence_flags(self):
        presence = self.report["source_presence"]
        readiness = self.report["runtime_readiness"]
        self.assertTrue(presence["adapter_sources_present"])
        self.assertFalse(presence["runtime_present"])
        self.assertFalse(presence["weights_present"])
        self.assertFalse(
            presence["exact_source_runtime_weights_conjunction_present"])
        self.assertFalse(readiness["importable"])
        self.assertTrue(readiness["blocked"])
        self.assertFalse(readiness["weights_loaded"])
        self.assertFalse(readiness["model_executed"])

    def test_linked_row_identity_only(self):
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         self.report["boundary"]["linked_row"])
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(identity["projection"]))

    def test_scope_flags_are_false(self):
        scope = self.report["scope"]
        for key in ("provider_registered", "adapter_implemented",
                    "adapter_executed", "public_abi_changed",
                    "registry_or_default_changed", "shared_build_or_ci_changed",
                    "real_assets_used", "network_used", "listening_performed",
                    "device_timing_measured", "benchmark_run", "release_claim"):
            self.assertFalse(scope[key], key)
        self.assertTrue(scope["task_local_only"])

    def test_public_v0_geometry_preserved(self):
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "float32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertFalse(geometry["changed"])


if __name__ == "__main__":
    unittest.main()
