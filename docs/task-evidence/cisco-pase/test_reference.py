# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the SDK-CISCO-PASE task-local surrogate."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_round_trip_is_canonical(self) -> None:
        value = {"b": [1, 2], "a": {"c": True}}
        self.assertEqual(reference.canonical_text(value), '{"a":{"c":true},"b":[1,2]}')

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json('{"a":1,"a":2}')
        self.assertEqual(caught.exception.code, "duplicate_json_key:a")

    def test_nonfinite_constant_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json('{"a":NaN}')
        self.assertEqual(caught.exception.code, "nonfinite_json_constant:NaN")

    def test_malformed_json_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json("{")
        self.assertEqual(caught.exception.code, "invalid_json")

    def test_nested_duplicate_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.parse_strict_json('{"a":{"x":1,"x":2}}')


class ManifestTests(unittest.TestCase):
    def manifest(self, **overrides):
        return reference._manifest(**overrides)

    def test_admits_external_assets_in_order(self) -> None:
        result = reference.validate_manifest(self.manifest(assets=[
            reference._asset(id="first", sha256="0" * 64, byte_count=10),
            reference._asset(id="second", sha256="1" * 64, byte_count=20),
        ]))
        self.assertEqual(result["asset_ids_in_order"], ["first", "second"])
        self.assertEqual(result["total_bytes"], 30)
        self.assertTrue(all(asset["storage"] == "external"
                            for asset in result["assets"]))

    def test_order_changes_digest(self) -> None:
        first = reference.validate_manifest(self.manifest(assets=[
            reference._asset(id="a", sha256="0" * 64),
            reference._asset(id="b", sha256="1" * 64),
        ]))
        second = reference.validate_manifest(self.manifest(assets=[
            reference._asset(id="b", sha256="1" * 64),
            reference._asset(id="a", sha256="0" * 64),
        ]))
        self.assertNotEqual(first["manifest_digest"], second["manifest_digest"])

    def test_duplicate_id_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest(self.manifest(assets=[
                reference._asset(), reference._asset(),
            ]))
        self.assertEqual(caught.exception.code, "duplicate_asset_id")

    def test_uppercase_id_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(self.manifest(
                assets=[reference._asset(id="Weights")]))

    def test_path_like_id_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(self.manifest(
                assets=[reference._asset(id="a/b")]))

    def test_sha256_rules(self) -> None:
        for digest, code in (("0" * 63, "invalid_sha256"),
                             ("A" * 64, "invalid_sha256"),
                             ("g" * 64, "invalid_sha256")):
            with self.subTest(digest=digest):
                with self.assertRaises(reference.Reject) as caught:
                    reference.validate_manifest(self.manifest(
                        assets=[reference._asset(sha256=digest)]))
                self.assertEqual(caught.exception.code, code)

    def test_byte_count_rules(self) -> None:
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(reference.Reject):
                    reference.validate_manifest(self.manifest(
                        assets=[reference._asset(byte_count=value)]))

    def test_embedded_storage_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest(self.manifest(
                assets=[reference._asset(storage="embedded")]))
        self.assertEqual(caught.exception.code, "unsupported_asset_storage")

    def test_extra_asset_field_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest(self.manifest(
                assets=[reference._asset(path="/tmp/w")]))
        self.assertEqual(caught.exception.code, "invalid_asset_fields")

    def test_missing_field_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(self.manifest(assets=[
                {"id": "a", "byte_count": 1, "storage": "external"}]))

    def test_asset_count_bounded(self) -> None:
        assets = [reference._asset(id="asset-%02d" % index,
                                   sha256="%064x" % (index + 1))
                  for index in range(reference.MAX_ASSETS + 1)]
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest(self.manifest(assets=assets))
        self.assertEqual(caught.exception.code, "invalid_asset_count")

    def test_total_size_bounded(self) -> None:
        assets = [reference._asset(
            id="asset-%02d" % index,
            sha256="%064x" % (index + 1),
            byte_count=reference.MAX_TOTAL_ASSET_BYTES // reference.MAX_ASSETS + 1)
            for index in range(reference.MAX_ASSETS)]
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_manifest(self.manifest(assets=assets))
        self.assertEqual(caught.exception.code, "asset_total_exceeds_limit")

    def test_empty_assets_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(self.manifest(assets=[]))


class AdapterTests(unittest.TestCase):
    def test_base_adapter_admits(self) -> None:
        adapter = reference.validate_adapter(reference._case_adapter())
        self.assertEqual(adapter["frame_samples"], 160)
        self.assertEqual(adapter["anchor_hop_samples"], 320)
        self.assertEqual(adapter["anchor_blocks_per_frame"], 2)
        self.assertEqual(adapter["execution_modes"], [2])

    def test_non_frame_multiple_hop_rejected(self) -> None:
        adapter = reference._case_adapter()
        adapter["anchor_hop_samples"] = 330
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_adapter(adapter)
        self.assertEqual(caught.exception.code, "anchor_hop_not_frame_multiple")

    def test_callback_mode_rejected(self) -> None:
        adapter = reference._case_adapter()
        adapter["execution_modes"] = [1]
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_adapter(adapter)
        self.assertEqual(caught.exception.code, "unsupported_execution_modes")

    def test_delay_bounds(self) -> None:
        for value in (-1, reference.MAX_DELAY_SAMPLES + 1):
            adapter = reference._case_adapter()
            adapter["buffering_delay_samples"] = value
            with self.assertRaises(reference.Reject) as caught:
                reference.validate_adapter(adapter)
            self.assertEqual(caught.exception.code, "delay_out_of_range")

    def test_drain_bounds(self) -> None:
        for value in (0, reference.MAX_DRAIN_CALLS + 1):
            adapter = reference._case_adapter()
            adapter["max_drain_calls"] = value
            with self.assertRaises(reference.Reject):
                reference.validate_adapter(adapter)

    def test_extra_field_rejected(self) -> None:
        adapter = reference._case_adapter()
        adapter["descriptor"] = {}
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_adapter(adapter)
        self.assertEqual(caught.exception.code, "invalid_adapter_fields")

    def test_edge_exclusion_bound(self) -> None:
        adapter = reference._case_adapter(start=100, end=100)
        with self.assertRaises(reference.Reject):
            reference.validate_adapter(adapter)


class FramePlanTests(unittest.TestCase):
    def plan(self, accepted, delay=160, start=0, end=0):
        return reference.frame_plan(
            accepted, reference._case_adapter(delay, start, end))

    def test_contract_example_320(self) -> None:
        plan = self.plan(320)
        self.assertEqual(plan["process_calls"], 2)
        self.assertEqual(plan["drain_audio_calls"], 1)
        self.assertEqual(plan["valid_intervals"], [[0, 160], [160, 320]])
        self.assertEqual(plan["valid_samples"], 320)

    def test_contract_example_165(self) -> None:
        plan = self.plan(165)
        self.assertEqual(plan["process_calls"], 2)
        self.assertEqual(plan["valid_from_process"], 160)
        self.assertEqual(plan["valid_from_drain"], 5)
        self.assertEqual(plan["zero_padding_samples"], 155)
        self.assertEqual(plan["valid_samples"], 165)

    def test_every_final_length_conserves(self) -> None:
        for length in range(1, 160):
            for delay in (0, 1, 100, 159):
                plan = self.plan(length, delay)
                self.assertTrue(plan["overlap_free"])
                self.assertTrue(plan["union_equals_content"])
                self.assertEqual(plan["valid_samples"], length)

    def test_zero_input_drains_immediately(self) -> None:
        plan = self.plan(0)
        self.assertEqual(plan["process_calls"], 0)
        self.assertEqual(plan["drain_audio_calls"], 0)
        self.assertEqual(plan["valid_samples"], 0)
        self.assertIsNone(plan["first_valid_source_sample"])

    def test_delay_not_multiple_of_frame(self) -> None:
        plan = self.plan(250, 100)
        self.assertEqual(plan["valid_intervals"],
                         [[0, 60], [60, 220], [220, 250]])
        self.assertEqual(plan["valid_from_process"], 220)
        self.assertEqual(plan["valid_from_drain"], 30)
        self.assertEqual(plan["drain_audio_calls"], 1)
        self.assertTrue(plan["union_equals_content"])

    def test_max_delay_uses_declared_budget(self) -> None:
        plan = self.plan(400, 16000)
        self.assertEqual(plan["drain_audio_calls"], 100)
        self.assertTrue(plan["drain_within_budget"])
        self.assertEqual(plan["valid_samples"], 400)

    def test_edge_exclusions(self) -> None:
        plan = self.plan(320, 160, 8, 8)
        self.assertEqual(plan["content_interval"], [8, 312])
        self.assertEqual(plan["valid_samples"], 304)
        self.assertEqual(plan["valid_intervals"][0][0], 8)

    def test_drain_budget_exceeded(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.frame_plan(1000, reference._case_adapter(16000, max_drain=1))
        self.assertEqual(caught.exception.code, "drain_budget_exceeded")

    def test_invalid_accepted(self) -> None:
        for value in (-1, reference.MAX_ACCEPTED_SAMPLES + 1, True, 1.0):
            with self.assertRaises(reference.Reject):
                reference.frame_plan(value, reference._case_adapter())

    def test_valid_offsets_fit_frame(self) -> None:
        for length in (1, 159, 160, 161, 320, 321, 1000):
            plan = self.plan(length, 161)
            for interval in plan["valid_intervals"]:
                self.assertLessEqual(interval[1] - interval[0], 160)
                self.assertGreaterEqual(interval[0], 0)
                self.assertLessEqual(interval[1], length)

    def test_output_calls_within_contract_bound(self) -> None:
        plan = self.plan(1000, 16000)
        self.assertLessEqual(plan["output_calls"], reference.MAX_DRAIN_CALLS)
        self.assertTrue(plan["eos_after_last_output"])


class CoverageSweepTests(unittest.TestCase):
    def test_sweep_conserves(self) -> None:
        sweep = reference.coverage_sweep()
        self.assertTrue(sweep["all_conserved"])
        self.assertEqual(sweep["checks"], 4105)


class FrameValidationTests(unittest.TestCase):
    def frame(self, valid=160, flags=0, samples=None, capacity=160,
              count=160):
        if samples is None:
            samples = [0.0] * count
        return reference.validate_frame(count, valid, flags, samples, capacity)

    def test_full_frame_admits(self) -> None:
        result = self.frame(samples=[0.5] * 160)
        self.assertEqual(result["input_valid_count"], 160)
        self.assertFalse(result["final_input"])

    def test_final_partial_admits_zero_padding(self) -> None:
        samples = [0.25] * 8 + [0.0] * 152
        result = self.frame(valid=8, flags=1, samples=samples)
        self.assertTrue(result["final_input"])
        self.assertEqual(result["zero_padding_samples"], 152)

    def test_partial_without_final_rejected(self) -> None:
        samples = [0.25] * 8 + [0.0] * 152
        with self.assertRaises(reference.Reject) as caught:
            self.frame(valid=8, samples=samples)
        self.assertEqual(caught.exception.code, "partial_without_final")

    def test_nonzero_padding_rejected(self) -> None:
        samples = [0.25] * 8 + [0.0] * 151 + [0.125]
        with self.assertRaises(reference.Reject) as caught:
            self.frame(valid=8, flags=1, samples=samples)
        self.assertEqual(caught.exception.code, "final_padding_not_zero")

    def test_unknown_flags_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            self.frame(flags=4)
        self.assertEqual(caught.exception.code, "unknown_flag_bits")

    def test_nonfinite_and_type_rejected(self) -> None:
        for value, code in ((math.inf, "nonfinite_sample"),
                            ("0", "invalid_sample_type")):
            samples = [value] + [0.0] * 159
            with self.assertRaises(reference.Reject) as caught:
                self.frame(samples=samples)
            self.assertEqual(caught.exception.code, code)

    def test_out_of_range_rejected(self) -> None:
        samples = [reference.MAX_ABS_SAMPLE + 1.0] + [0.0] * 159
        with self.assertRaises(reference.Reject) as caught:
            self.frame(samples=samples)
        self.assertEqual(caught.exception.code, "sample_out_of_range")

    def test_count_and_capacity_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            self.frame(capacity=159)
        self.assertEqual(caught.exception.code, "output_capacity_too_small")


class RecombineTests(unittest.TestCase):
    def test_exact_anchor_hold(self) -> None:
        case = reference.dual_stream_case()
        self.assertTrue(case["exact"])
        self.assertEqual(case["anchor_blocks_per_frame"], 2)
        self.assertEqual(case["frame_count"], 16)
        self.assertEqual(case["status"], "synthetic_only_not_qualified")

    def test_identity_is_bit_exact(self) -> None:
        control = reference.identity_control()
        self.assertTrue(control["bit_identical"])
        self.assertEqual(control["input_digest"], control["output_digest"])

    def test_preservation_control_is_negative(self) -> None:
        control = reference.preservation_control()
        self.assertLess(control["si_sdr_db"], 0.0)
        self.assertFalse(control["bit_identical"])
        self.assertFalse(control["clean_speech_preserved"])
        self.assertEqual(control["status"], "surrogate_only_not_qualified")

    def test_hop_must_be_frame_multiple(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.recombine([0.0], [0.0] * 160, 170)
        self.assertEqual(caught.exception.code, "anchor_hop_not_frame_multiple")

    def test_residual_misalignment_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.recombine([0.0, 0.0], [0.0] * 161, 160)
        self.assertEqual(caught.exception.code, "residual_not_block_aligned")

    def test_anchor_count_mismatch_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.recombine([0.0], [0.0] * 320, 160)
        self.assertEqual(caught.exception.code, "anchor_block_count_mismatch")

    def test_nonfinite_values_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.recombine([math.nan], [0.0] * 160, 160)
        self.assertEqual(caught.exception.code, "nonfinite_anchor")
        with self.assertRaises(reference.Reject) as caught:
            reference.recombine([0.0], [math.inf] + [0.0] * 159, 160)
        self.assertEqual(caught.exception.code, "nonfinite_residual")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_identity_and_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["task"], reference.TASK_ID)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["defer_before"], "opt_in_adapter_exposure")

    def test_qualification_never_passes(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["qualifies"])
        self.assertFalse(qualification["all_required_results_present"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertFalse(qualification["asset_manifest_admitted"])
        self.assertFalse(qualification["candidate_weights_present"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_enhancement_profile(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "enhancement")
        self.assertEqual(len(profile["required_items"]), 9)
        for name, item in profile["required_items"].items():
            self.assertIn(item["status"], {"synthetic_only", "blocked"}, name)

    def test_conservation_cases(self) -> None:
        cases = self.report["conservation_cases"]
        self.assertEqual(len(cases), 11)
        for case in cases:
            self.assertTrue(case["overlap_free"], case["case_id"])
            self.assertTrue(case["union_equals_content"], case["case_id"])
            self.assertTrue(case["drain_within_budget"], case["case_id"])

    def test_adverse_rejections(self) -> None:
        adverse = self.report["adverse_rejections"]
        self.assertEqual(len(adverse), 52)
        self.assertTrue(self.report["adverse_all_rejected"])
        for item in adverse:
            self.assertEqual(item["status"], "rejected")
            self.assertTrue(item["state_unchanged"])
            self.assertNotEqual(item["code"], "")

    def test_asset_admission_blocked(self) -> None:
        admission = self.report["asset_admission"]
        self.assertEqual(admission["asset_readiness"], "blocked")
        self.assertEqual(admission["required_assets"], [])
        self.assertEqual(admission["candidate_artifact_pins"], [])
        self.assertFalse(admission["upstream_artifact_names_known"])
        self.assertEqual(admission["bytes_read"], 0)
        self.assertEqual(admission["downloads_attempted"], 0)

    def test_boundary_flags_all_false(self) -> None:
        boundary = self.report["boundary"]
        self.assertTrue(boundary)
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_repeatability_three_runs(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["runs"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(repeat["case_matrix_digests"]), 3)
        self.assertEqual(len(set(repeat["case_matrix_digests"])), 1)

    def test_board_row_identity_not_full_hash(self) -> None:
        row = self.report["board_row"]
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])

    def test_no_mutable_board_pin(self) -> None:
        for path in self.report["source_pins"]:
            self.assertFalse(path.endswith("TASKS.json"))
        for path in self.report["boundary_pins"]:
            self.assertFalse(path.endswith("TASKS.json"))

    def test_exact_blockers_present(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 5)
        ids = {blocker["id"] for blocker in blockers}
        self.assertIn("candidate_artifacts_absent", ids)
        self.assertIn("pinned_runtime_absent", ids)
        self.assertIn("artifact_rights_and_training_data_unclear", ids)


class PinTests(unittest.TestCase):
    def test_source_and_boundary_pins_resolve(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            full = reference.SOURCE_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)
        for path, digest in reference.BOUNDARY_PINS.items():
            full = reference.SDK_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)

    def test_artifact_pins_exist(self) -> None:
        for name in reference.ARTIFACT_FILES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_report_file_matches_build(self) -> None:
        path = HERE / "report.json"
        if not path.is_file():
            self.skipTest("report.json not regenerated yet")
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(path.read_bytes(), text.encode("utf-8"))
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="ascii"),
                         digest + "\n")


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()

    def test_contract_disposition(self) -> None:
        contract = self.contract
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["evidence_status"], "incomplete")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["verification_profile"], "enhancement")
        self.assertEqual(contract["base_commit"], reference.BASE_COMMIT)

    def test_public_boundary_unchanged(self) -> None:
        boundary = self.contract["public_boundary"]
        for key in ("c_provider_added", "public_api_abi_changed",
                    "installed_v0_behavior_changed",
                    "shared_build_or_ci_changed", "processor_exposure"):
            self.assertFalse(boundary[key], key)

    def test_scope_is_synthetic_and_local(self) -> None:
        scope = self.contract["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key in {"synthetic_only", "task_local_only"}:
                continue
            self.assertFalse(value, key)

    def test_contract_gates_and_blockers_match_report(self) -> None:
        report = reference.build_report()
        self.assertEqual(self.contract["release_gates"], report["release_gates"])
        self.assertEqual(self.contract["exact_blockers"],
                         report["exact_blockers"])

    def test_artifact_pins_cover_package(self) -> None:
        pins = self.contract["artifact_pins"]
        self.assertEqual(
            set(pins),
            {reference.TASK_PREFIX + name for name in reference.ARTIFACT_FILES})
        self.assertNotIn(reference.TASK_PREFIX + "contract.json", pins)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", pins)


if __name__ == "__main__":
    unittest.main(verbosity=2)
