"""Deterministic unittest suite for the linear-interpolation declipping fixture."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixtures  # noqa: E402
import reference  # noqa: E402
import report  # noqa: E402
import run  # noqa: E402

REPORT_PATH = HERE / "report.json"
AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))


class LinearDeclippingFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bytes = REPORT_PATH.read_bytes()
        cls.document = json.loads(cls.bytes)
        cls.rebuilt = report.build_report()
        cls.cases = {case["id"]: case for case in cls.document["cases"]}

    def test_report_is_canonical_byte_identical_and_parseable(self):
        regenerated = reference.canonical_bytes(self.rebuilt)
        self.assertEqual(self.bytes, regenerated)
        self.assertTrue(self.bytes.endswith(b"\n"))
        self.assertEqual(self.document, self.rebuilt)
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="utf-8").strip(),
                         hashlib.sha256(self.bytes).hexdigest())
        self.assertEqual(self.document["protocol"],
                         "sdk.linear-interpolation-declipping.restoration.v1")
        self.assertEqual(self.document["base_commit"], report.BASE_COMMIT)
        self.assertEqual(self.document["status"], "proposal_only_synthetic")

    def test_source_pins_are_present_and_exact(self):
        pins = self.document["source_pins"]
        self.assertEqual(len(pins), 6)
        self.assertEqual(set(pins), set(fixtures.SOURCE_PINS))
        for relative, digest in pins.items():
            path = AUDIOML_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(report.sha256_path(path), digest, relative)

    def test_geometry_keeps_installed_v0_out_of_scope(self):
        geometry = self.document["geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["sdk_frame_samples"], 160)
        self.assertEqual(geometry["offline_block_samples"], 2048)
        self.assertEqual(geometry["execution_profile"], "offline_only")
        self.assertFalse(geometry["realtime_claim"])
        self.assertFalse(geometry["installed_v0_changed"])
        for key, value in self.document["scope"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.document["scope"]["opt_in_provider_added"])
        self.assertFalse(self.document["scope"]["generated_headers_added"])

    def test_counts_and_missing_policy_are_explicit(self):
        counts = self.document["counts"]
        expected = {"cases": 21, "complete_cases": 20, "adverse_cases": 1,
                    "rejection_checks": 22, "rejections_observed": 22,
                    "missing_results": 8, "source_pins": 6,
                    "exact_mask_verified_cases": 19}
        self.assertEqual(counts, expected)
        qualification = self.document["qualification"]
        self.assertEqual(qualification["status"], "incomplete")
        self.assertEqual(qualification["release_decision"], "not_qualified")
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        for item in self.document["adverse_and_skipped"]["missing_results"]:
            self.assertEqual(item["status"], "not_run", item["item"])
            self.assertTrue(item["reason"])

    def test_local_digests(self):
        digests = self.document["digests"]
        self.assertEqual(digests["fixture_spec"],
                         reference.canonical_digest(fixtures.seed_spec()))
        self.assertEqual(digests["adapter_descriptor"],
                         report.sha256_path(report.ADAPTER_PATH))
        clean = fixtures.build_samples("clean_bandlimited")
        self.assertEqual(digests["clean_bandlimited_f32"],
                         reference.digest_samples(clean))
        self.assertEqual(digests["identity_output_f32"], reference.digest_samples(clean))
        self.assertEqual(digests["linear_no_occupancy_output_f32"],
                         reference.digest_samples(clean))

    def test_clipping_occupancy_strata_are_frozen_and_ordered(self):
        strata = self.document["strata"]["clipping_occupancy_percent"]
        self.assertEqual(strata, {
            "occupancy_very_low": 0.4883,
            "occupancy_low": 1.9531,
            "occupancy_mid": 9.5703,
            "occupancy_high": 42.1875,
            "occupancy_saturated": 98.6816,
        })
        ordered = ["occupancy_very_low", "occupancy_low", "occupancy_mid",
                   "occupancy_high", "occupancy_saturated"]
        self.assertEqual(sorted(strata, key=strata.get), ordered)

    def test_exact_clipping_mask_is_verified_for_every_finite_source(self):
        for case in report.CASES:
            config = case["configuration"]
            if case["id"] == "nonfinite_input" or config["control"] == "identity":
                continue
            clean = fixtures.build_samples(case["stimulus_id"])
            clipped = reference.hard_clip(clean, config["threshold"])
            mask = reference.clip_mask(clipped, config["threshold"])
            reference.assert_exact_mask(clean, clipped, mask, config["threshold"])
            summary = self.cases[case["id"]]
            self.assertEqual(sum(mask), summary["mask"]["clipped_samples"], case["id"])
            self.assertTrue(summary["mask"]["exact_saturation_verified"], case["id"])
        contract = self.document["exact_clipping_mask"]
        self.assertEqual(contract["binary32_abs_tolerance"], 1e-7)
        self.assertEqual(contract["float64_pilot_rule"], "abs(clipped) >= threshold - 1e-10")
        self.assertTrue(contract["caller_mask_mismatch_rejected"])
        self.assertEqual(contract["caller_mask_exact_case"],
                         "caller_exact_mask_verified_against_clean")

    def test_clean_transparency_is_measured_not_assumed(self):
        transparency = self.document["clean_transparency"]
        self.assertTrue(transparency["identity_exact"])
        self.assertEqual(transparency["identity_max_abs_diff"], 0.0)
        self.assertEqual(transparency["clipped_input_no_occupancy_occupancy"], 0.0)
        self.assertTrue(transparency["clipped_input_no_occupancy_exact"])
        self.assertEqual(transparency["linear_interp_no_occupancy_occupancy"], 0.0)
        self.assertTrue(transparency["linear_interp_no_occupancy_exact"])

    def test_linear_interpolation_formula_and_endpoint_hold(self):
        expected = [reference.f32(value) for value in (-0.5, -0.2, 0.0, 0.2, 0.5)]
        clipped = reference.hard_clip([-1.0, -0.2, 0.0, 0.2, 1.0], 0.5)
        self.assertEqual(clipped, expected)
        processed = reference.linear_interpolate(clipped, [False, True, False,
                                                           False, True])
        self.assertEqual(processed["samples"],
                         [reference.f32(value) for value in (-0.5, -0.25, 0.0, 0.2, 0.2)])
        interior = reference.linear_interpolate(
            [-0.5, -0.9, 0.5], [False, True, False])["samples"]
        self.assertEqual(interior, [reference.f32(-0.5), 0.0, reference.f32(0.5)])
        leading = reference.linear_interpolate(
            [0.8, 0.7, 0.1, -0.1], [True, True, False, False])["samples"]
        self.assertEqual(leading, [reference.f32(0.1)] * 3 + [reference.f32(-0.1)])
        trailing = reference.linear_interpolate(
            [0.1, -0.1, 0.8, 0.9], [False, False, True, True])["samples"]
        self.assertEqual(trailing, [reference.f32(0.1), reference.f32(-0.1),
                                    reference.f32(-0.1), reference.f32(-0.1)])

    def test_boundary_hold_and_interior_ramp_rules(self):
        boundary = self.document["linear_interpolation"]["boundary"]
        self.assertTrue(boundary["boundary_leading"]["leading_hold_exact"])
        self.assertFalse(boundary["boundary_leading"]["trailing_hold_exact"])
        self.assertTrue(boundary["boundary_trailing"]["trailing_hold_exact"])
        self.assertFalse(boundary["boundary_trailing"]["leading_hold_exact"])
        self.assertTrue(boundary["boundary_single_interior"]["interior_ramp_valid"])
        self.assertTrue(boundary["boundary_two_anchors"]["interior_ramp_valid"])
        self.assertEqual(boundary["boundary_two_anchors"]["run_count"], 2)
        minimal = boundary["boundary_minimal_anchors"]
        self.assertEqual(minimal["kinds"], ["leading", "interior", "trailing"])
        self.assertTrue(minimal["leading_hold_exact"])
        self.assertTrue(minimal["trailing_hold_exact"])
        self.assertTrue(minimal["interior_ramp_valid"])
        for item in boundary.values():
            self.assertTrue(item["reliable_samples_preserved"], item)
            self.assertEqual(item["max_output_deviation_from_anchor_or_ramp"], 0.0)
        anchors = self.document["linear_interpolation"]["single_interior_anchors"]
        self.assertEqual((anchors["left"], anchors["right"]), (1023, 1025))
        expected = 0.5 * (anchors["left_anchor_value"] + anchors["right_anchor_value"])
        self.assertAlmostEqual(anchors["reconstructed_value"], expected, places=6)

    def test_no_reliable_anchor_fixture_is_unchanged(self):
        case = self.cases["boundary_all_clipped"]
        self.assertEqual(case["mask"]["clipping_occupancy"], 1.0)
        self.assertEqual(case["reconstruction"]["replacement_mode"],
                         "no_reliable_anchor_unchanged")
        self.assertEqual(case["reconstruction"]["reliable_count"], 0)
        self.assertEqual(case["reconstruction"]["replaced_count"], 0)
        clean = fixtures.build_samples("all_clipped")
        clipped = reference.hard_clip(clean, 0.35)
        self.assertEqual(case["output"]["samples_sha256"],
                         reference.digest_samples(clipped))

    def test_unmasked_samples_preserved_in_all_complete_cases(self):
        self.assertTrue(self.document["linear_interpolation"][
            "reliable_samples_preserved_in_all_complete_cases"])
        for case in self.document["cases"]:
            if case["status"] != "complete":
                continue
            self.assertTrue(case["reconstruction"].get("reliable_samples_preserved", True),
                            case["id"])

    def test_output_peaks_are_finite_and_cohort_bounded(self):
        peaks = self.document["peak_behavior"]
        self.assertEqual(peaks["complete_cases_with_finite_output"], 20)
        self.assertTrue(peaks["outputs_within_input_peak"])
        self.assertEqual(peaks["max_output_peak_observed"], 0.899999976)
        for case in self.document["cases"]:
            if case["status"] == "complete":
                self.assertGreaterEqual(case["output"]["peak_abs"], 0.0)
                self.assertEqual(case["output"]["nonfinite_count"], 0)
                self.assertIsNotNone(case["output"]["samples_sha256"])

    def test_nonfinite_input_is_an_adverse_result_not_a_pass(self):
        adverse = self.document["adverse_and_skipped"]["numerical"]
        self.assertEqual(adverse["case"], "nonfinite_input")
        self.assertEqual(adverse["status"], "adverse_numerical")
        self.assertEqual(adverse["input_nonfinite_count"], 2)
        self.assertFalse(adverse["output_samples_serialized"])
        self.assertTrue(adverse["errors"])
        self.assertIsNone(self.cases["nonfinite_input"]["output"]["samples_sha256"])
        self.assertEqual(self.cases["nonfinite_input"]["scoring"]["status"],
                         "not_applicable")

    def test_all_invalid_controls_are_rejected(self):
        rejections = self.document["adverse_and_skipped"]["control_rejections"]
        self.assertEqual(len(rejections), 22)
        self.assertEqual({item["status"] for item in rejections}, {"rejected"})
        self.assertTrue(all(item["reason"] for item in rejections))
        self.assertEqual({item["case"] for item in rejections}, {
            "missing_threshold", "unknown_control", "threshold_zero",
            "threshold_above_one", "threshold_not_numeric", "threshold_nonfinite",
            "mask_source_invalid", "missing_clip_mask", "clip_mask_wrong_length",
            "clip_mask_not_boolean", "clip_mask_nonfinite", "clip_mask_mismatch",
            "unexpected_clip_mask", "unknown_control_key", "invalid_candidate_ref",
            "wrong_protocol_version", "override_wrong_block_length",
            "missing_attempt_id", "missing_configuration", "unknown_stimulus_id",
            "duplicate_json_key", "nonfinite_json_constant",
        })
        missing_mask = next(item for item in rejections
                            if item["case"] == "missing_clip_mask")
        self.assertEqual(missing_mask["reason"], "missing_clip_mask")

    def test_candidate_harms_every_synthetic_stratum(self):
        comparisons = self.document["controls"]["by_occupancy"]
        self.assertEqual(set(comparisons), {"very_low", "low", "mid", "high", "saturated"})
        for name, values in comparisons.items():
            self.assertLess(values["linear_interp_delta_db"], 0.0, name)
            self.assertEqual(values["linear_interp_delta_db"],
                             round(values["linear_interp_si_sdr_db"]
                                   - values["clipped_si_sdr_db"], 6), name)

    def test_processor_decision_is_defer_before_exposure(self):
        decision = self.document["processor_decision"]
        self.assertEqual(decision["decision"], "defer")
        self.assertTrue(decision["recorded_before_processor_exposure"])
        self.assertFalse(decision["public_processor_exposed"])
        self.assertTrue(decision["conditions_to_reopen"])
        self.assertEqual(json.loads((HERE / "adapter.json").read_text())[
            "processor_decision"], "defer")

    def test_adapter_inspect_boundary(self):
        request = {
            "protocol_version": 1,
            "operation": "inspect",
            "candidate_ref": dict(report.CANDIDATE_REF),
            "adapter_ref": dict(report.ADAPTER_REF),
            "configuration": {"control": "linear_interp", **report.base_config()},
        }
        inspected = run.inspect(request)
        self.assertEqual(inspected["identity"], run.IDENTITY)
        self.assertEqual(inspected["supported_modes"], ["offline"])
        self.assertEqual(inspected["supported_tasks"], [])
        self.assertEqual(inspected["supported_controls"], list(run.CONTROLS))
        self.assertIn("unregistered", inspected["registration"])
        self.assertTrue(inspected["processor_decision"].startswith("defer"))

    def test_run_cli_writes_the_same_canonical_result(self):
        case = report.CASES[5]
        request = report.request_for(case)
        with tempfile.TemporaryDirectory(prefix="linear-declip-cli-") as scratch:
            request_path = Path(scratch) / "request.json"
            result_path = Path(scratch) / "result.json"
            request_path.write_bytes(run.canonical_bytes(request))
            completed = subprocess.run(
                [sys.executable, str(HERE / "run.py"),
                 "--request", str(request_path), "--result", str(result_path)],
                cwd=str(HERE), capture_output=True, text=True, check=False,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(result_path.read_bytes(),
                             run.canonical_bytes(run.run(request)))

    def test_caller_owned_stimulus_boundary_and_nonfinite_override(self):
        samples = fixtures.build_samples("clean_quiet")
        request = report.request_for(report.CASES[0])
        request["stimulus_samples"] = samples
        result = run.run(request)
        self.assertEqual(result["input"]["samples_sha256"],
                         reference.digest_samples(samples))
        self.assertEqual(result["scoring"]["status"], "not_applicable")
        self.assertEqual(result["output"]["samples_sha256"],
                         reference.digest_samples(samples))
        request["stimulus_samples"][3] = float("nan")
        adverse = run.run(request)
        self.assertEqual(adverse["status"], "adverse_numerical")
        self.assertNotIn("samples", adverse["output"])
        self.assertEqual(adverse["input"]["nonfinite_count"], 1)

    def test_request_field_validation_is_strict(self):
        valid = report.request_for(report.CASES[5])
        for mutation in (
            lambda item: item.pop("attempt_id"),
            lambda item: item.update(unexpected=1),
            lambda item: item["candidate_ref"].update(revision=0),
            lambda item: item.update(clip_mask=[True] * 16),
        ):
            request = json.loads(json.dumps(valid))
            mutation(request)
            with self.assertRaises(run.RequestError):
                run.run(request)

    def test_report_regeneration_from_clean_copy_is_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="linear-declip-report-") as scratch:
            target = Path(scratch)
            for name in ("adapter.json", "fixtures.py", "reference.py", "report.py",
                         "run.py"):
                (target / name).write_bytes((HERE / name).read_bytes())
            completed = subprocess.run(
                [sys.executable, str(target / "report.py")], cwd=str(target),
                capture_output=True, text=True, check=False,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                     "AUDIOML_ROOT": str(AUDIOML_ROOT)})
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual((target / "report.json").read_bytes(), self.bytes)

    def test_fixture_generation_is_deterministic(self):
        for stimulus_id in fixtures.STIMULI:
            first = fixtures.build_samples(stimulus_id)
            second = fixtures.build_samples(stimulus_id)
            if stimulus_id == "nonfinite":
                self.assertEqual(sum(1 for value in first if not math.isfinite(value)), 2)
                self.assertEqual(sum(1 for value in second if not math.isfinite(value)), 2)
            else:
                self.assertEqual(reference.digest_samples(first),
                                 reference.digest_samples(second), stimulus_id)
                self.assertEqual(len(first), reference.OFFLINE_BLOCK_SAMPLES)


if __name__ == "__main__":
    unittest.main()
