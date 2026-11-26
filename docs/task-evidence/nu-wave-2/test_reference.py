# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the NU-Wave 2 task-local evidence model."""

from __future__ import annotations

import copy
import json
import unittest

import reference as ref


class StrictJsonTests(unittest.TestCase):
    def test_rejects_nonfinite_constant(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.strict_loads('{"a": NaN}')

    def test_rejects_duplicate_key(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.strict_loads('{"a": 1, "a": 2}')

    def test_rejects_non_object(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.strict_loads('[1, 2, 3]')

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": 1, "a": [2, 3]}
        self.assertEqual(ref.canonical_bytes(value),
                         ref.canonical_bytes(copy.deepcopy(value)))


class ReportTests(unittest.TestCase):
    def test_report_is_deferred_and_not_qualified(self) -> None:
        report = ref.build_report()
        self.assertEqual(report["decision"], ref.DECISION)
        self.assertEqual(report["qualification"]["status"], ref.QUALIFICATION)
        self.assertEqual(report["profile"], ref.PROFILE)
        self.assertEqual(report["mode"], ref.MODE)

    def test_report_gates_are_all_blocked(self) -> None:
        report = ref.build_report()
        gates = report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_report_task_geometry_is_not_asserted(self) -> None:
        report = ref.build_report()
        self.assertEqual(report["task_row_identity"]["stable_fields"]["id"],
                         ref.TASK)
        self.assertFalse(report["format"]["task_geometry_asserted"])
        self.assertEqual(report["format"]["task_geometry_status"],
                         "unestablished")

    def test_report_serializes_to_strict_json(self) -> None:
        payload = ref.canonical_report_bytes(ref.build_report())
        parsed = ref.strict_loads(payload.decode("utf-8"))
        self.assertEqual(parsed["task_id"], ref.TASK)


class PcmTests(unittest.TestCase):
    def test_synthetic_control_is_valid(self) -> None:
        signal = ref.synthetic_input_pcm()
        self.assertEqual(len(signal), ref.CONTROL_SOURCE_SAMPLES)
        summary = ref.pcm_summary(signal, ref.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(summary["channels"], 1)
        self.assertEqual(summary["nonfinite_samples"], 0)
        self.assertEqual(summary["duration_s"], "3")

    def test_nonfinite_sample_rejected(self) -> None:
        signal = [0.0, float("nan"), 0.0]
        with self.assertRaises(ref.Reject):
            ref.validate_pcm(signal)

    def test_out_of_range_sample_rejected(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.validate_pcm([0.0, 1.5, 0.0])

    def test_empty_signal_rejected(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.validate_pcm([])


class ControlTests(unittest.TestCase):
    def test_bandwidth_ledger_is_declaration_only(self) -> None:
        ledger = ref.bandwidth_ledger(16000, 48000, 3500)
        self.assertEqual(ledger["missing_band_hz"], [3500, 8000])
        self.assertEqual(ledger["declared_extended_band_hz"], [8000, 24000])
        self.assertTrue(ledger["generated_band_is_estimate"])
        self.assertFalse(ledger["signal_reconstructed"])
        self.assertFalse(ledger["artifact_latency_measured"])

    def test_cutoff_above_input_nyquist_rejected(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.bandwidth_ledger(16000, 48000, 8000)

    def test_duration_is_conserved(self) -> None:
        result = ref.duration_conservation(
            ref.CONTROL_SOURCE_SAMPLES, 16000,
            ref.CONTROL_OUTPUT_SAMPLES, 48000)
        self.assertTrue(result["duration_conserved"])
        self.assertEqual(result["duration_ratio"], "1")

    def test_duration_mismatch_is_reported(self) -> None:
        result = ref.duration_conservation(16000, 16000, 96000, 48000)
        self.assertFalse(result["duration_conserved"])
        self.assertEqual(result["duration_ratio"], "2")

    def test_adverse_controls_are_all_rejected(self) -> None:
        cases = ref.run_adverse_controls()
        self.assertTrue(cases)
        for case in cases:
            self.assertEqual(case["result"], "rejected")
            self.assertTrue(case["reason"])


class CallerManifestTests(unittest.TestCase):
    def test_shape_only_manifest_rejected(self) -> None:
        with self.assertRaises(ref.Reject):
            ref.validate_caller_manifest(ref._shape_only_manifest())

    def test_exact_file_manifest_is_admitted_without_execution(self) -> None:
        manifest = ref._existing_file_manifest()
        result = ref.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["model_executed"])
        self.assertEqual(result["files_checked"], 9)

    def test_corrupted_digest_rejected(self) -> None:
        manifest = ref._existing_file_manifest()
        manifest["checkpoint_sha256"] = "0" * 64
        with self.assertRaises(ref.Reject):
            ref.validate_caller_manifest(manifest)

    def test_non_absolute_path_rejected(self) -> None:
        manifest = ref._existing_file_manifest()
        manifest["checkpoint_path"] = "relative/reference.py"
        with self.assertRaises(ref.Reject):
            ref.validate_caller_manifest(manifest)


class PinTests(unittest.TestCase):
    def test_source_pin_never_hashes_mutable_board(self) -> None:
        for path in ref.SOURCE_PINS:
            self.assertFalse(path.endswith("plan/swarm/TASKS.json"))
        self.assertNotIn(json.dumps({"tasks": []}), ref.SOURCE_PINS)


if __name__ == "__main__":
    unittest.main()
