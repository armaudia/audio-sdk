# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the ONNX Runtime reference-runtime evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
ADAPTER = HERE / "adapter.json"
PROVIDER = HERE / "provider.json"
MODEL = HERE / "synthetic_model.json"
REQUIRED_KEYS = {
    "schema_id", "task_id", "component_id", "reference_family", "base_commit", "profile",
    "status", "qualification_status", "decision", "evidence_status", "scope", "boundary",
    "format", "adapter_contract", "model_asset", "runtime_readiness", "conditions",
    "tool_profile", "boundary_checks", "adverse", "repeatability", "gates", "rights_gap",
    "negative_claims", "source_pins", "boundary_pins", "artifact_pins", "missing_evidence",
    "evidence_classes", "invariants",
}


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_json_file(REPORT)
        cls.contract = reference.strict_json_file(CONTRACT)
        cls.adapter = reference.strict_json_file(ADAPTER)
        cls.provider = reference.strict_json_file(PROVIDER)
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_03_status_and_qualification(self) -> None:
        self.assertEqual(self.report["status"], "synthetic_boundary_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["defer_before"], "runtime_integration")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_04_boundary_is_opt_in_and_unregistered(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration", "processor_exposure",
                    "c_public_boundary"):
            self.assertIs(boundary[key], False)
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertIs(self.provider["registered"], False)
        self.assertIs(self.provider["default_enabled"], False)
        self.assertIs(self.adapter["registered"], False)

    def test_05_public_v0_geometry_untouched(self) -> None:
        fmt = self.report["format"]
        expected = {"sample_rate_hz": 16000, "channels": 1, "sample_format": "f32",
                    "frame_samples": 160, "hop_samples": 160, "content_delay_samples": 0}
        for key, value in expected.items():
            self.assertEqual(fmt[key], value)
        self.assertIs(fmt["installed_v0_geometry_preserved"], True)

    def test_06_required_keys_present(self) -> None:
        self.assertFalse(REQUIRED_KEYS - set(self.report))
        self.assertFalse({"schema_id", "task", "decision"} - set(self.contract))
        self.assertFalse({"adapter_id", "runtime_id", "registered"} - set(self.adapter))

    def test_07_base_commit_and_runtime_identity(self) -> None:
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["reference_family"], "onnxruntime")
        self.assertEqual(self.report["component_id"], reference.COMPONENT_ID)
        self.assertEqual(self.report["adapter_contract"]["runtime_id"], reference.RUNTIME_ID)
        source_pin = reference.SOURCE_PINS["source:cpp-library/src/stages/onnx_common.cpp"]
        self.assertEqual(self.contract["source_identity"]["sha256"], source_pin)
        self.assertEqual(self.report["source_pins"]["source:cpp-library/src/stages/onnx_common.cpp"],
                         source_pin)

    def test_08_model_fixture_is_exact_and_synthetic(self) -> None:
        self.assertEqual(MODEL.read_bytes(), reference.model_bytes())
        asset = self.report["model_asset"]
        self.assertEqual(asset["sha256"], reference.sha256(reference.model_bytes()))
        self.assertEqual(asset["byte_count"], len(reference.model_bytes()))
        self.assertIs(asset["real_onnx_graph"], False)
        self.assertIs(asset["real_model_weights"], False)
        self.assertEqual(asset["asset_kind"], "synthetic_non_onnx_descriptor")
        self.assertEqual(asset["storage"], "external_caller_supplied")
        self.assertEqual(self.adapter["model_digest"], asset["sha256"])
        self.assertEqual(self.adapter["model_byte_count"], asset["byte_count"])

    def test_09_runtime_readiness_is_blocked(self) -> None:
        readiness = self.report["runtime_readiness"]
        self.assertIs(readiness["blocked"], True)
        self.assertIs(readiness["module_spec_found"], False)
        self.assertIs(readiness["importable"], False)
        self.assertEqual(readiness["interpreter"], "3.12.16")
        self.assertEqual(readiness["exact_error"],
                         "ModuleNotFoundError: No module named 'onnxruntime'")
        self.assertIs(readiness["sdk_runtime_pin_present"], False)
        self.assertIs(readiness["candidate_used"], False)
        self.assertGreaterEqual(len(readiness["reopen_conditions"]), 4)
        self.assertTrue(readiness["blocker"])

    def test_10_capability_is_declared_not_queried(self) -> None:
        capability = reference.ReferenceBoundary().capability()
        self.assertEqual(capability["runtime_id"], reference.RUNTIME_ID)
        self.assertEqual(capability["capability_source"], "declared_fixture_not_runtime_query")
        self.assertIs(capability["runtime_available"], False)
        self.assertIs(capability["runtime_invoked"], False)
        self.assertEqual(capability["tensors"], reference.TENSORS)
        self.assertEqual(capability["session_options"], reference.SESSION_OPTIONS)
        self.assertTrue(capability["io_binding"]["input_output_alias_rejected"])

    def test_11_impulse_golden_vector(self) -> None:
        waveform = [0.0] * 160
        waveform[0] = 1.0
        adapter = reference.ReferenceBoundary()
        result = adapter.run({"waveform_in": waveform})
        self.assertEqual(result["waveform_out"][0], 0.75)
        self.assertTrue(all(value == 0.0 for value in result["waveform_out"][1:]))
        self.assertEqual(result["state_out"][0], 0.125)
        self.assertTrue(all(value == 0.0 for value in result["state_out"][1:]))
        self.assertEqual(self.report["conditions"]["impulse"]["waveform_out_sha256"],
                         reference.f32_digest(result["waveform_out"]))
        self.assertTrue(all(self.report["conditions"]["impulse"]["exact_checks"].values()))
        adapter.close()

    def test_12_constant_vectors(self) -> None:
        adapter = reference.ReferenceBoundary()
        positive = adapter.run({"waveform_in": [1.0] * 160})
        self.assertTrue(all(value == 0.75 for value in positive["waveform_out"]))
        self.assertTrue(all(value == 0.0 for value in positive["state_out"]))
        adapter.reset()
        negative = adapter.run({"waveform_in": [-1.0] * 160})
        self.assertTrue(all(value == -0.75 for value in negative["waveform_out"]))
        self.assertTrue(all(value == 0.0 for value in negative["state_out"]))
        adapter.reset()
        silence = adapter.run({"waveform_in": [0.0] * 160})
        self.assertTrue(all(value == 0.0 for value in silence["waveform_out"]))
        self.assertTrue(all(value == 0.0 for value in silence["state_out"]))
        adapter.close()

    def test_13_state_advances_and_reset_replays(self) -> None:
        adapter = reference.ReferenceBoundary()
        first = reference._condition_frame(20261125)
        a = adapter.run({"waveform_in": first})
        b = adapter.run({"waveform_in": first})
        self.assertNotEqual(a["state_out"], b["state_out"])
        adapter.reset()
        replay = adapter.run({"waveform_in": first})
        self.assertEqual(reference.f32_digest(replay["waveform_out"]),
                         reference.f32_digest(a["waveform_out"]))
        self.assertEqual(reference.f32_digest(replay["state_out"]),
                         reference.f32_digest(a["state_out"]))
        self.assertEqual(adapter.frames, 1)
        adapter.close()

    def test_14_explicit_state_and_io_binding(self) -> None:
        condition = self.report["conditions"]["explicit_state_and_bindings"]
        self.assertTrue(condition["binding_path_matches"])
        adapter = reference.ReferenceBoundary()
        waveform = reference._condition_frame(20261201)
        state = reference._condition_frame(20261202)[:16]
        waveform_out = [0.0] * 160
        state_out = [0.0] * 16
        result = adapter.run({"waveform_in": waveform, "state_in": state},
                             {"waveform_out": waveform_out, "state_out": state_out})
        self.assertEqual(result["waveform_out"], waveform_out)
        self.assertEqual(result["state_out"], state_out)
        self.assertNotEqual(state_out, [0.0] * 16)
        adapter.close()

    def test_15_closed_lifecycle_idempotent(self) -> None:
        adapter = reference.ReferenceBoundary()
        adapter.close()
        adapter.close()
        with self.assertRaises(reference.Rejected) as caught:
            adapter.run({"waveform_in": [0.0] * 160})
        self.assertEqual(caught.exception.code, "closed")
        with self.assertRaises(reference.Rejected) as caught:
            adapter.capability()
        self.assertEqual(caught.exception.code, "closed")

    def test_16_model_rejections_fail_closed(self) -> None:
        cases = reference.adverse()["model_rejections"]
        self.assertGreaterEqual(len(cases), 15)
        for name, value in cases.items():
            self.assertNotEqual(value["code"], "accepted", name)
        self.assertEqual(reference.adverse()["counts"]["failed_open"], 0)

    def test_17_config_rejections_fail_closed(self) -> None:
        cases = reference.adverse()["config_rejections"]
        self.assertEqual(cases["missing_selection"]["code"], "missing_config_key")
        self.assertEqual(cases["unknown_key"]["code"], "unexpected_config_key")
        self.assertEqual(cases["nondeterministic_threading"]["code"],
                         "nondeterministic_threading")
        self.assertEqual(cases["nondeterministic_compute"]["code"],
                         "nondeterministic_compute")
        for name, value in cases.items():
            self.assertNotEqual(value["code"], "accepted", name)

    def test_18_feed_rejections_preserve_state(self) -> None:
        cases = reference.adverse()["feed_rejections"]
        self.assertEqual(cases["missing_waveform"]["code"], "missing_feed")
        self.assertEqual(cases["waveform_nonfinite"]["code"], "nonfinite_feed")
        self.assertEqual(cases["waveform_range"]["code"], "feed_range")
        self.assertEqual(cases["state_nonfinite"]["code"], "nonfinite_feed")
        for name, value in cases.items():
            self.assertTrue(value["state_unchanged"], name)

    def test_19_binding_rejections_fail_closed(self) -> None:
        cases = reference.adverse()["binding_rejections"]
        self.assertEqual(cases["missing_output"]["code"], "missing_binding")
        self.assertEqual(cases["waveform_binding_shape"]["code"], "binding_shape")
        self.assertEqual(cases["tuple_not_writable"]["code"],
                         "binding_not_writable_list")
        self.assertEqual(cases["binding_aliases_input"]["code"],
                         "binding_aliases_input")
        for name, value in cases.items():
            self.assertNotEqual(value["code"], "accepted", name)

    def test_20_rights_and_runtime_rejections(self) -> None:
        cases = reference.adverse()
        self.assertEqual(cases["rights_rejections"]["packaging_requested"]["code"],
                         "packaging_not_permitted")
        self.assertEqual(cases["rights_rejections"]["download_requested"]["code"],
                         "download_not_permitted")
        self.assertEqual(cases["rights_rejections"]["real_model_requested"]["code"],
                         "real_model_not_permitted")
        for value in cases["runtime_rejections"].values():
            self.assertEqual(value["code"], "unsupported_runtime")

    def test_21_tool_profile_is_honest(self) -> None:
        profile = self.report["tool_profile"]
        self.assertEqual(profile["profile"], "tool")
        mapped = profile["mapped_cases"]
        self.assertEqual(mapped["version_install_and_provenance"]["status"], "blocked")
        self.assertEqual(mapped["typical_cli_or_api_use"]["status"], "passed_synthetic")
        self.assertEqual(mapped["malformed_inputs"]["status"], "passed_synthetic")
        self.assertEqual(mapped["compile_and_build_evidence"]["status"], "not_run")
        self.assertEqual(mapped["measured_workload_support"]["status"], "not_reported")

    def test_22_all_gates_blocked_and_claims_false(self) -> None:
        self.assertTrue(self.report["gates"])
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen"])
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)
        self.assertIs(self.report["rights_gap"]["blocked"], True)

    def test_23_repeatability_and_report_pins(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertIs(repeat["byte_identical"], True)
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(self.report["artifact_pins"], reference.artifact_pins())

    def test_24_strict_json_rejects_duplicates_and_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.strict_json(b'{"a":NaN}')
        with self.assertRaises(ValueError):
            reference.strict_json(b"not-json")

    def test_25_pin_parser_rejects_malformed_scope(self) -> None:
        for bad in ("not-a-line", "Z" * 64 + "  docs/x",
                    "a" * 64 + "  ../escape", "a" * 64 + "  unknown/x",
                    "a" * 64 + "  /tmp/absolute"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(bad)
        duplicate = "\n".join([f"{'a' * 64}  docs/x", f"{'a' * 64}  docs/x"])
        with self.assertRaises(ValueError):
            reference.parse_pin_lines(duplicate)

    def test_26_source_manifest_matches_files(self) -> None:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="utf-8"))
        self.assertGreater(len(pins), 15)
        for digest, raw in pins:
            path = reference.pin_path(raw)
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256(path.read_bytes()), digest, raw)
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())

    def test_27_adapter_and_provider_are_canonical(self) -> None:
        self.assertEqual(ADAPTER.read_bytes(), reference.adapter_bytes())
        self.assertEqual(PROVIDER.read_bytes(), reference.provider_bytes())
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertEqual(json.loads(ADAPTER.read_bytes())["runtime_invoked"], False)
        self.assertEqual(json.loads(PROVIDER.read_bytes())["vendor_runtime_invoked"], False)

    def test_28_counts_match_enumerated_cases(self) -> None:
        adverse = reference.adverse()
        counts = adverse["counts"]
        expected_groups = {
            "model_rejections": 18,
            "config_rejections": 8,
            "feed_rejections": 9,
            "binding_rejections": 6,
            "rights_rejections": 3,
            "runtime_rejections": 2,
        }
        self.assertEqual(counts["rejection_groups"], expected_groups)
        for group, expected in expected_groups.items():
            self.assertEqual(len(adverse[group]), expected, group)
        self.assertEqual(counts["rejection_cases"], 46)
        self.assertEqual(counts["lifecycle_checks"], 5)
        self.assertEqual(len(adverse["lifecycle"]), 5)
        self.assertEqual(counts["lifecycle_rejected"], 3)
        self.assertEqual(counts["lifecycle_accepted"], 2)
        self.assertEqual(counts["total_checks"], 51)
        self.assertEqual(counts["failed_open"], 0)
        self.assertIs(counts["all_rejections_closed"], True)
        malformed = self.report["boundary_checks"]["malformed_inputs"]
        self.assertEqual(malformed["cases"], 46)
        self.assertEqual(malformed["rejection_cases"], 46)
        self.assertEqual(malformed["lifecycle_checks"], 5)
        self.assertEqual(malformed["total_checks"], 51)

    def test_29_typical_probe_calls_capability_and_reset(self) -> None:
        probe = reference.typical_probe()
        self.assertEqual(probe["sequence"], list(reference.TYPICAL_PROBE_SEQUENCE))
        self.assertEqual(probe["steps_completed"], 9)
        self.assertIs(probe["capability"]["called"], True)
        self.assertEqual(probe["capability"]["runtime_id"], reference.RUNTIME_ID)
        self.assertIs(probe["capability"]["runtime_invoked"], False)
        self.assertIs(probe["capability"]["tensors_match"], True)
        self.assertIs(probe["reset"]["called"], True)
        self.assertIs(probe["reset"]["zero_state"], True)
        self.assertIs(probe["run_after_reset"]["replay_matches_first_frame"], True)
        self.assertIs(probe["close"]["run_after_close_rejected"], True)
        self.assertIs(probe["create_capability_run_reset_close"], True)
        self.assertIs(probe["all_steps_passed"], True)
        self.assertEqual(self.report["boundary_checks"]["typical_api_use"], probe)

    def test_30_readme_counts_match_report(self) -> None:
        counts = self.report["adverse"]["counts"]
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        lines = [
            f"model_rejections={counts['rejection_groups']['model_rejections']}",
            f"config_rejections={counts['rejection_groups']['config_rejections']}",
            f"feed_rejections={counts['rejection_groups']['feed_rejections']}",
            f"binding_rejections={counts['rejection_groups']['binding_rejections']}",
            f"rights_rejections={counts['rejection_groups']['rights_rejections']}",
            f"runtime_rejections={counts['rejection_groups']['runtime_rejections']}",
            f"rejection_cases={counts['rejection_cases']}",
            f"lifecycle_checks={counts['lifecycle_checks']} "
            f"({counts['lifecycle_rejected']} rejected, {counts['lifecycle_accepted']} accepted)",
            f"total_checks={counts['total_checks']}",
        ]
        for line in lines:
            self.assertIn(line, readme)


if __name__ == "__main__":
    unittest.main()
