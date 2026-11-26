# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the NVIDIA BNR v2.1 boundary evidence."""

from __future__ import annotations

import copy
import unittest

import reference as ref


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ref.JsonError):
            ref.strict_json_loads('{"a":1,"a":2}')

    def test_rejects_nonfinite_constants(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(ref.JsonError):
                ref.strict_json_loads(text)

    def test_rejects_trailing_data(self) -> None:
        with self.assertRaises(ref.JsonError):
            ref.strict_json_loads('{"a":1} extra')

    def test_json_array_is_not_rejected_but_is_not_an_object(self) -> None:
        self.assertIsInstance(ref.strict_json_loads('[1,2,3]'), list)

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": [1, 2], "a": {"d": 3, "c": 4}}
        self.assertEqual(ref.canonical_bytes(value),
                         ref.canonical_bytes(copy.deepcopy(value)))


class RequestTests(unittest.TestCase):
    def test_valid_request_is_accepted_then_deferred(self) -> None:
        result = ref.admit(ref._base_request())
        self.assertEqual(result["status"], "DEFER")
        self.assertTrue(result["input_validated"])
        self.assertFalse(result["admissible"])
        self.assertFalse(result["candidate_processing"])
        self.assertIsNone(result["result"])
        self.assertFalse(result["qualifies_candidate"])

    def test_adverse_requests_are_all_rejected(self) -> None:
        cases = ref._adverse_cases()
        self.assertTrue(cases["all_requests_rejected"])
        self.assertGreater(cases["request_case_count"], 0)
        self.assertIsNone(cases["metrics"])

    def test_probe_candidate_fails_closed(self) -> None:
        with self.assertRaises(ref.ArtifactsAbsent):
            ref.probe_candidate(ref._base_request())

    def test_geometry_matches_installed_v0(self) -> None:
        geometry = ref.geometry()["local_harness_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["installed_v0_only"])


class AssetTests(unittest.TestCase):
    def test_valid_manifest_is_accepted_then_deferred(self) -> None:
        result = ref.admit_asset(ref._base_manifest())
        self.assertEqual(result["status"], "DEFER")
        self.assertTrue(result["manifest_validated"])
        self.assertFalse(result["artifact_opened"])
        self.assertFalse(result["artifact_hashed"])
        self.assertFalse(result["artifact_loaded"])
        self.assertTrue(result["caller_declaration_is_not_review"])

    def test_adverse_manifests_are_all_rejected(self) -> None:
        cases = ref._adverse_cases()
        self.assertTrue(cases["all_manifests_rejected"])
        self.assertGreater(cases["manifest_case_count"], 0)

    def test_source_probe_finds_no_checkout(self) -> None:
        probe = ref.source_probe()
        self.assertFalse(probe.get("present", False))

    def test_weights_probe_finds_no_artifact(self) -> None:
        probe = ref.weights_probe()
        self.assertFalse(probe.get("present", False))


class ReportTests(unittest.TestCase):
    def test_report_is_deferred_and_not_qualified(self) -> None:
        report = ref.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["candidate_qualified"])

    def test_report_has_eight_blocked_gates(self) -> None:
        report = ref.build_report()
        gates = report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_no_candidate_result_exists(self) -> None:
        report = ref.build_report()
        candidate = report["candidates"][ref.CANDIDATE]
        self.assertIsNone(candidate["result"])
        self.assertFalse(candidate["qualifies_candidate"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertFalse(ref.qualification()["all_required_results_present"])

    def test_boundary_makes_no_installed_change(self) -> None:
        boundary = ref.boundary()
        self.assertFalse(boundary["descriptor_registration"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertFalse(boundary["public_api_abi_changed"])
        self.assertFalse(boundary["ci_changed"])

    def test_report_bytes_are_strict_json(self) -> None:
        payload = ref.report_bytes()
        value = ref.strict_json_loads(payload.decode("utf-8"))
        self.assertEqual(value["task"], ref.TASK)

    def test_artifact_pins_cover_four_python_files(self) -> None:
        pins = ref.artifact_pins()
        self.assertEqual(set(pins), set(ref.SOURCE_ARTIFACT_FILES))
        self.assertTrue(all(len(digest) == 64 for digest in pins.values()))


if __name__ == "__main__":
    unittest.main()
