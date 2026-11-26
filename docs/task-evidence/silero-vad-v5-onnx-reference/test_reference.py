# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local Silero VAD v5 readiness bundle."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import reference as ref


class ModelTests(unittest.TestCase):
    def test_present_model_is_pinned_and_structural(self) -> None:
        model = ref.model_provenance()
        self.assertTrue(model["present"])
        self.assertEqual(model["sha256"], ref.MODEL_SHA256)
        self.assertEqual(model["byte_count"], ref.MODEL_BYTE_COUNT)
        self.assertEqual(model["structural_sha256"], ref.STRUCTURAL_SHA256)
        self.assertTrue(model["structural_match"])
        self.assertFalse(model["version_proven"])
        self.assertTrue(model["provenance_conflict"])
        self.assertFalse(model["weights_decoded"])
        self.assertFalse(model["model_executed"])

    def test_branch_parameter_counts(self) -> None:
        structure = ref.structural_graph()
        self.assertEqual(structure["sample_rate_guard"], 16000)
        self.assertEqual(structure["state_shape"], list(ref.STATE_SHAPE))
        self.assertEqual(
            structure["branches"]["16000"]["parameter_count"],
            ref.PARAMETERS_16K)
        self.assertEqual(
            structure["branches"]["8000"]["parameter_count"],
            ref.PARAMETERS_8K)
        self.assertEqual(
            sum(row["parameter_count"]
                for row in structure["branches"].values()),
            ref.PARAMETERS_TOTAL)

    def test_malformed_protobuf_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ref._fields(b"\x12\x05ab")
        with self.assertRaises(ValueError):
            ref._tensor_meta(b"\x08\x00")

    def test_truncated_model_reader_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            ref._tensor_meta(b"\x0a\x02\x02\x02")


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ref.loads_strict('{"a":1,"a":2}')

    def test_nonfinite_literals_rejected(self) -> None:
        for literal in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                ref.loads_strict('{"a":' + literal + "}")

    def test_bom_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ref.loads_strict('\ufeff{"a":1}')

    def test_canonical_floats_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ref._no_floats({"a": 0.5})
        with self.assertRaises(ValueError):
            ref.canonical_bytes({"a": 0.5})


class ContractAndReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = ref.build_contract()
        cls.report = ref.build_report(cls.contract)

    def test_contract_status(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.contract["profile"], "analysis")
        ref.validate_contract(self.contract)

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual([row["id"] for row in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"], ref.board_row_projection())

    def test_artifacts_and_blockers(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 8)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertTrue(artifact["blocked"])
            self.assertFalse(artifact["present"])
            self.assertIsNone(artifact["sha256"])
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in artifacts}
        gate_ids = {row["id"] for row in self.contract["release_gates"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            for gate in blocker["linked_gates"]:
                self.assertIn(gate, gate_ids)

    def test_analysis_quality_and_timing_blocked(self) -> None:
        analysis = self.contract["analysis_profile_requirements"]
        self.assertEqual(len(analysis), 8)
        for row in analysis:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
        for key, count in (("quality_outcomes", 4), ("timing_requirements", 4)):
            rows = self.contract[key]
            self.assertEqual(len(rows), count)
            for row in rows:
                self.assertEqual(row["status"], "blocked")
                self.assertIsNone(row["value"])

    def test_report_copies_contract(self) -> None:
        report = self.report
        self.assertEqual(report["schema_id"], ref.REPORT_SCHEMA_ID)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["contract_sha256"],
                         ref.object_digest(self.contract))
        for source, target in (
                ("qualification", "qualification"),
                ("required_artifacts", "required_artifacts"),
                ("exact_blockers", "exact_blockers"),
                ("scope", "scope"),
                ("boundary", "boundary"),
                ("model_provenance", "model_provenance"),
                ("cadence_reference", "cadence_reference"),
                ("runtime_recorded", "runtime_recorded"),
                ("source_presence", "source_presence")):
            self.assertEqual(report[target], self.contract[source])
        self.assertEqual(report["gates"], self.contract["release_gates"])
        self.assertEqual(report["analysis_profile"]["rows"],
                         self.contract["analysis_profile_requirements"])
        self.assertEqual(report["quality_outcomes"]["rows"],
                         self.contract["quality_outcomes"])
        self.assertEqual(report["timing"]["rows"],
                         self.contract["timing_requirements"])

    def test_qualification_flags(self) -> None:
        qualification = self.report["qualification"]
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["model_artifact_present"])
        for key in ("exact_model_version_proven", "exact_runtime_present",
                    "license_present", "upstream_source_present",
                    "reference_outputs_present", "corpus_present",
                    "real_result_present", "analysis_result",
                    "device_timing_result", "listening_result",
                    "benchmark_result", "release_claim",
                    "missing_result_promoted", "weights_used"):
            self.assertFalse(qualification[key], key)

    def test_canonical_is_stable(self) -> None:
        first = ref.canonical_report(ref.build_report(ref.build_contract()))
        second = ref.canonical_report(ref.build_report(ref.build_contract()))
        self.assertEqual(first, second)
        self.assertEqual(len(first[1]), 64)

    def test_no_floats_and_strict_bytes(self) -> None:
        payload = ref.canonical_bytes(self.report)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(json.loads(payload.decode("ascii")), self.report)


class CadenceTests(unittest.TestCase):
    def test_rates_and_cross_hop(self) -> None:
        cadence = ref.cadence_reference()
        rows = {row["sample_rate_hz"]: row for row in cadence["rates"]}
        self.assertEqual(rows[16000]["model_window_samples"], 512)
        self.assertEqual(rows[16000]["context_samples"], 64)
        self.assertEqual(rows[16000]["v0_frames_per_model_window"], "16/5")
        self.assertEqual(rows[16000]["cross_hop_v0_frames"], 16)
        self.assertEqual(rows[16000]["cross_hop_model_windows"], 5)
        self.assertEqual(rows[8000]["model_window_samples"], 256)
        self.assertEqual(rows[8000]["context_samples"], 32)
        self.assertEqual(rows[8000]["v0_frames_per_model_window"], "8/5")
        self.assertEqual(rows[8000]["cross_hop_v0_frames"], 8)
        self.assertEqual(rows[8000]["cross_hop_model_windows"], 5)
        self.assertEqual(cadence["availability"]["model_quantization_ms"], 32)
        self.assertFalse(cadence["availability"]["exact_10ms_alignment"])

    def test_warmup_not_verified(self) -> None:
        warmup = ref.cadence_reference()["warmup"]
        self.assertFalse(warmup["verified_against_upstream_v5_wrapper"])
        self.assertFalse(warmup["exact_warmup_parity"])
        self.assertFalse(warmup["upstream_v5_wrapper_source_present"])
        self.assertEqual(warmup["local_cpp_stage_silent_shortcut_windows"], 3)


class AdmissionTests(unittest.TestCase):
    def test_control_accepted_for_schema_only(self) -> None:
        result = ref.admit_bundle(ref.admission_control())
        self.assertTrue(result["accepted"])
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["code"], "admitted_schema_only")

    def test_valid_8k_branch_accepted(self) -> None:
        bundle = copy.deepcopy(ref.admission_control())
        bundle["cadence"]["sample_rate_hz"] = 8000
        bundle["cadence"]["window_samples"] = 256
        bundle["cadence"]["context_samples"] = 32
        result = ref.admit_bundle(bundle)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["qualifies"])

    def test_all_adverse_cases_rejected(self) -> None:
        cases = ref.admission_cases()
        self.assertEqual(len(cases), 24)
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])

    def test_nonfinite_bundle_rejected(self) -> None:
        bundle = copy.deepcopy(ref.admission_control())
        bundle["source"]["wrapper_sha256"] = float("nan")
        with self.assertRaises(ValueError):
            ref.admit_bundle(bundle)

    def test_duplicate_keys_rejected_before_admission(self) -> None:
        with self.assertRaises(ValueError):
            ref.loads_strict('{"schema_id":"x","schema_id":"y"}')

    def test_admission_summary_never_qualifies(self) -> None:
        report = ref.admission_report()
        self.assertEqual(report["summary"]["qualifying_results"], 0)
        self.assertEqual(report["summary"]["accepted_schema_controls"], 1)
        self.assertTrue(report["control"]["synthetic_schema_control_not_evidence"])
        self.assertFalse(report["control"]["qualifies"])


class BoundaryTests(unittest.TestCase):
    def test_absence_probes(self) -> None:
        contract = ref.build_contract()
        summary = contract["absence_evidence"]["summary"]
        self.assertEqual(summary["probe_count"], 16)
        self.assertEqual(summary["workspace_probe_count"], 12)
        self.assertEqual(summary["home_probe_count"], 4)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "weights_decoded", "model_executed",
                    "audio_read"):
            self.assertFalse(summary[key], key)

    def test_source_presence_conjunction_absent(self) -> None:
        presence = ref.build_contract()["source_presence"]
        self.assertTrue(presence["model_artifact_present"])
        for key in ("exact_model_version_proven", "exact_runtime_present",
                    "license_files_present", "upstream_source_present",
                    "reference_outputs_present", "corpus_present",
                    "exact_source_weights_runtime_conjunction_present",
                    "weights_used", "weights_decoded", "model_executed",
                    "runtime_imported", "audio_read", "network_used"):
            self.assertFalse(presence[key], key)

    def test_board_identity_only(self) -> None:
        contract = ref.build_contract()
        row = contract["boundary"]["linked_row"]
        self.assertEqual(set(row), set(ref.BOARD_ROW_FIELDS))
        self.assertNotIn("status", row)
        self.assertNotIn("owner", row)
        self.assertFalse(contract["boundary"]["board_file_pinned"])
        self.assertFalse(contract["boundary"]["mutable_board_fields_gate"])
        self.assertEqual(len(contract["boundary"]["linked_rows"]), 6)
        self.assertNotIn("TASKS.json",
                         " ".join(contract["source_pins"]))
        self.assertEqual(contract["boundary"]["linked_row_sha256"],
                         ref.object_digest(row))

    def test_pins_resolve(self) -> None:
        for relative, digest in ref.SOURCE_PINS.items():
            self.assertEqual(ref.sha256_file(ref.AUDIO_ROOT / relative), digest)
        for relative, digest in ref.BOUNDARY_PINS.items():
            self.assertEqual(ref.sha256_file(ref.WORKTREE / relative), digest)

    def test_no_model_or_audio_artifact_in_task_dir(self) -> None:
        forbidden = {".onnx", ".wav", ".flac", ".pt", ".pth", ".so", ".dylib"}
        for path in ref.HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)


if __name__ == "__main__":
    unittest.main()
