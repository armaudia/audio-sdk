# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local unit checks for the synthetic MDF residual postfilter evidence."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import fixture
import reference
import run as adapter
import scorer

TASK = Path(__file__).resolve().parent
CLI = os.environ.get("MDF_POSTFILTER_CLI")
REPORT_KEYS = {
    "schema_id", "task", "component", "mode", "verification_profile",
    "disposition", "decision", "format", "fixture_digest", "fixture_spec",
    "fixture_digests", "configurations", "source_pins", "boundary_pins",
    "legacy_blob_count", "mutable_provenance", "conditions", "results",
    "controls", "near_end_preservation", "acceptance_profile",
    "mdf_limitation_disclosure", "invalid_and_missing_cases", "qualification",
    "release_gates", "non_claims", "repeat_runs",
}
ADAPTER_KEYS = {
    "protocol_version", "identity", "input_kind", "output_kinds", "tasks",
    "modes", "configuration_keys", "registration", "processor_exposure",
    "supported_formats", "provider_option", "qualification",
}


def request(operation: str, condition: str | None = None) -> dict:
    payload = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "component", "id": reference.COMPONENT, "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": reference.COMPONENT, "revision": 1},
        "configuration": {"variant": "mdf_postfilter"},
    }
    if condition is not None:
        payload["condition"] = condition
    return payload


class FixtureTests(unittest.TestCase):
    def test_generate_is_deterministic(self):
        first = fixture.generate()
        second = fixture.generate()
        self.assertEqual(first, second)

    def test_fixture_digest_is_stable(self):
        self.assertEqual(fixture.fixture_digest(), fixture.fixture_digest())
        self.assertEqual(len(fixture.fixture_digest()), 64)

    def test_spec_is_frozen(self):
        spec = fixture.spec()
        self.assertEqual(spec["sample_rate_hz"], 16000)
        self.assertEqual(spec["frame_samples"], 160)
        self.assertEqual(spec["frames"], 300)
        self.assertEqual(spec["filter_length_samples"], 3200)
        self.assertEqual(spec["echo_path_movement"],
                         "none; frozen three-tap delay/gain")

    def test_all_streams_have_expected_length(self):
        for streams in fixture.generate().values():
            for values in streams.values():
                self.assertEqual(len(values), fixture.SAMPLE_COUNT)

    def test_all_streams_are_finite_and_in_range(self):
        for streams in fixture.generate().values():
            for values in streams.values():
                self.assertTrue(all(math.isfinite(value) and abs(value) <= 1.0
                                    for value in values))

    def test_conditions_are_frozen(self):
        self.assertEqual(list(fixture.CONDITIONS), [
            "echo_only", "near_end_only", "overlap_20ms", "no_reference",
            "misaligned_render"])

    def test_no_reference_render_is_silent(self):
        streams = fixture.generate()
        self.assertTrue(all(value == 0.0
                            for value in streams["no_reference"]["render"]))

    def test_misaligned_render_is_shifted_one_frame(self):
        streams = fixture.generate()
        shift = fixture.MISALIGNMENT_SHIFT_SAMPLES
        shifted = streams["misaligned_render"]["render"]
        original = streams["echo_only"]["render"]
        self.assertEqual(shifted[:shift], [0.0] * shift)
        self.assertEqual(shifted[shift:], original[:-shift])

    def test_near_burst_is_twenty_milliseconds(self):
        start, end = fixture.window(fixture.NEAR_BURST_FRAMES)
        self.assertEqual(end - start, 320)

    def test_pack_f32_is_little_endian(self):
        payload = fixture.pack_f32([1.0, -2.0])
        self.assertEqual(len(payload), 8)
        self.assertEqual(payload[:4], b"\x00\x00\x80\x3f")


class ScorerTests(unittest.TestCase):
    def test_erle_db_positive_for_attenuation(self):
        capture = [1.0] * 100
        output = [0.1] * 100
        self.assertEqual(round(fixture.erle_db(capture, output, 0, 100), 6), 20.0)

    def test_rms_ratio_is_exact(self):
        output = [2.0] * 100
        near = [1.0] * 100
        self.assertEqual(round(fixture.rms_ratio(output, near, 0, 100), 6), 2.0)

    def test_attenuation_db_is_exact(self):
        output = [0.5] * 100
        near = [1.0] * 100
        self.assertEqual(round(fixture.attenuation_db(output, near, 0, 100), 6),
                         -6.0206)

    def test_delta_rounds_to_six_places(self):
        self.assertEqual(scorer.delta(1.0, 1.2345678), 0.234568)

    def test_metadata_declares_withhold_policy(self):
        self.assertEqual(scorer.metadata()["missing_result_policy"],
                         "withhold; never impute or tolerance-widen")


class AdapterValidationTests(unittest.TestCase):
    def test_inspect_response_is_unregistered(self):
        response = adapter.inspect(request("inspect"))
        self.assertEqual(response["registration"],
                         "unregistered developer-only; no installed SDK provider")
        self.assertEqual(response["processor_exposure"], "none")
        self.assertEqual(response["fixture_digest"], fixture.fixture_digest())

    def test_inspect_rejects_extra_field(self):
        payload = request("inspect")
        payload["extra"] = 1
        with self.assertRaises(adapter.RequestError):
            adapter.inspect(payload)

    def test_inspect_rejects_bad_variant(self):
        payload = request("inspect")
        payload["configuration"]["variant"] = "tiny16"
        with self.assertRaises(adapter.RequestError):
            adapter.inspect(payload)

    def test_run_rejects_unknown_condition(self):
        with self.assertRaises(adapter.RequestError):
            adapter.validate_request(request("run", "unknown"), "run")

    def test_request_reader_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"a":1,"a":2}\n', encoding="utf-8")
            with self.assertRaises(adapter.RequestError):
                adapter.read_json(path)

    def test_request_reader_rejects_nonfinite_constant(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"a":NaN}\n', encoding="utf-8")
            with self.assertRaises(adapter.RequestError):
                adapter.read_json(path)


class StaticArtifactTests(unittest.TestCase):
    def test_report_is_canonical_and_finite(self):
        raw = (TASK / "report.json").read_bytes()
        report = json.loads(raw)
        self.assertEqual(raw, fixture.canonical_bytes(report))
        self.assertTrue(all(math.isfinite(value) for value in
                            [report["near_end_preservation"]["near_only_attenuation_db"]["delta"]]))

    def test_report_key_set_matches(self):
        self.assertEqual(set(json.loads((TASK / "report.json").read_text())),
                         REPORT_KEYS)

    def test_adapter_key_set_matches(self):
        self.assertEqual(set(json.loads((TASK / "adapter.json").read_text())),
                         ADAPTER_KEYS)

    def test_disclosure_values_are_exact(self):
        report = json.loads((TASK / "report.json").read_text())
        disclosure = report["mdf_limitation_disclosure"]
        self.assertEqual(disclosure["aligned_erle_db"], 16.453939)
        self.assertEqual(disclosure["misaligned_erle_db"], 16.888932)
        self.assertEqual(disclosure["overlap_near_ratio"], 0.985161)

    def test_decision_flags_are_exact(self):
        report = json.loads((TASK / "report.json").read_text())
        qualification = report["qualification"]
        for key in ("no_tolerance_widening", "no_provider_substitution",
                    "three_byte_identical_repeats", "no_tiny16_comparison",
                    "no_default_or_abi_change", "no_missing_result_may_qualify"):
            self.assertIs(qualification[key], True)
        self.assertIs(report["decision"]["postfilter_enabled"], False)
        self.assertEqual(qualification["postfilter_registration"], "unregistered")
        self.assertEqual(qualification["postfilter_default"], "OFF")

    def test_postfilter_is_not_reported_as_recovered(self):
        report = json.loads((TASK / "report.json").read_text())
        preservation = report["near_end_preservation"]
        self.assertIs(preservation["recovered_against_mdf_only"], False)
        self.assertLess(preservation["overlap_near_ratio"]["delta"], 0.0)

    def test_no_provider_or_top_level_cmake_in_evidence(self):
        self.assertFalse((TASK / "provider").exists())
        self.assertFalse((TASK / "CMakeLists.txt").exists())


@unittest.skipUnless(CLI, "set MDF_POSTFILTER_CLI to include adapter CLI tests")
class AdapterCLITests(unittest.TestCase):
    def setUp(self):
        self.cli = Path(CLI).resolve()

    def test_self_tests_pass(self):
        for flag in ("--self-test", "--self-test-postfilter"):
            completed = __import__("subprocess").run([str(self.cli), flag],
                                                      capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_postfilter_changes_overlap_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = reference.build_core(self.cli, root / "core")
            digests = [report["results"]["overlap_20ms"][variant]["output_digests"][0]
                       for variant in reference.VARIANTS]
            self.assertNotEqual(*digests)

    def test_default_off_matches_mdf_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = reference.build_core(self.cli, root / "core")
            self.assertIs(report["controls"]["postfilter_off_by_default"]["passed"], True)

    def test_controls_reject_bad_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = reference.build_core(self.cli, root / "core")
            for name, control in report["controls"].items():
                self.assertIs(control["passed"], True, name)

    def test_single_case_matches_report_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = reference.single_case(self.cli, root / "one", "echo_only",
                                           "mdf_only")
            report = json.loads((TASK / "report.json").read_text())
            self.assertEqual(
                result["output_digest"],
                report["results"]["echo_only"]["mdf_only"]["output_digests"][0])


if __name__ == "__main__":
    unittest.main()
