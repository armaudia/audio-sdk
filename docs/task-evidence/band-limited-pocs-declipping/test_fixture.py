"""Deterministic unittest suite for the band-limited POCS restoration fixture."""

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


class PocsDeclippingFixtureTests(unittest.TestCase):
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
                         "sdk.band-limited-pocs-declipping.restoration.v1")
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
        scope = self.document["scope"]
        for key, value in scope.items():
            self.assertFalse(value, key)

    def test_counts_are_complete_and_missing_policy_is_explicit(self):
        counts = self.document["counts"]
        expected = {"cases": 18, "complete_cases": 17, "adverse_cases": 1,
                    "pocs_cases": 9, "rejection_checks": 17,
                    "rejections_observed": 17, "missing_results": 7,
                    "source_pins": 6}
        self.assertEqual(counts, expected)
        qualification = self.document["qualification"]
        self.assertEqual(qualification["status"], "incomplete")
        self.assertEqual(qualification["release_decision"], "not_qualified")
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
        self.assertEqual(digests["identity_output_f32"],
                         reference.digest_samples(clean))
        self.assertEqual(digests["pocs_clean_output_f32"], digests["identity_output_f32"])

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
        self.assertEqual(self.document["strata"]["bandwidth_cutoff_hz"],
                         {"bandwidth_narrow": 2000.0, "bandwidth_mid": 3500.0})

    def test_clip_mask_and_saturation_constraints_hold(self):
        for case in report.CASES:
            if case["control"] != "pocs_declip" or case["id"] == "nonfinite_input":
                continue
            clean = fixtures.build_samples(case["stimulus_id"])
            config = case["configuration"]
            clipped = reference.hard_clip(clean, config["threshold"])
            mask = reference.clip_mask(clipped, config["threshold"])
            self.assertEqual(sum(mask), self.cases[case["id"]]["input"]["clipped_samples"])
            f32_threshold = abs(reference.f32(config["threshold"]))
            for index, bad in enumerate(mask):
                self.assertLessEqual(abs(clipped[index]), f32_threshold + 1e-9)
                if not bad:
                    self.assertEqual(clipped[index], clean[index])
                elif clean[index] > config["threshold"]:
                    self.assertAlmostEqual(clipped[index], config["threshold"], places=6)
                elif clean[index] < -config["threshold"]:
                    self.assertAlmostEqual(clipped[index], -config["threshold"], places=6)

    def test_clean_transparency_is_measured_not_assumed(self):
        transparency = self.document["clean_transparency"]
        self.assertTrue(transparency["identity_exact"])
        self.assertEqual(transparency["identity_max_abs_diff"], 0.0)
        self.assertEqual(transparency["clip_control_no_occupancy_occupancy"], 0.0)
        self.assertTrue(transparency["clip_control_no_occupancy_exact"])
        self.assertEqual(transparency["pocs_bandlimited_max_abs_diff"], 0.0)
        self.assertEqual(transparency["pocs_bandlimited_si_sdr_db"], 120.0)
        self.assertEqual(transparency["pocs_bandlimited_output_peak"], 0.899999976)

    def test_bounded_iterations_trace_and_cap(self):
        behavior = self.document["iteration_behavior"]
        for case_id in ("iterations_min", "occupancy_mid"):
            item = behavior[case_id]
            self.assertEqual(item["trace_length"], item["configured_iterations"] + 1)
            self.assertEqual(item["projection_count"], item["configured_iterations"] + 1)
            self.assertTrue(item["max_delta_nonincreasing"], case_id)
            self.assertTrue(item["all_deltas_finite"], case_id)
            self.assertLess(item["last_max_delta"], item["first_max_delta"])
            projections = [step["projection"] for step in item["projections"]]
            self.assertEqual(projections, list(range(1, item["trace_length"] + 1)))
        self.assertEqual(behavior["iterations_min"]["configured_iterations"], 1)
        self.assertEqual(behavior["occupancy_mid"]["configured_iterations"], 60)
        self.assertIn("iterations_above_cap",
                      [item["case"] for item in
                       self.document["adverse_and_skipped"]["control_rejections"]])

    def test_pocs_output_respects_known_sample_constraints(self):
        clean = fixtures.build_samples("speech_like")
        config = report.CASES[5]["configuration"]
        clipped = reference.hard_clip(clean, config["threshold"])
        mask = reference.clip_mask(clipped, config["threshold"])
        processed = reference.pocs_declip(clipped, mask, config["cutoff_hz"],
                                          config["iterations"])
        for index, bad in enumerate(mask):
            if not bad:
                self.assertEqual(processed["samples"][index], clipped[index])
            elif clipped[index] > 0.0:
                self.assertGreaterEqual(processed["samples"][index],
                                        config["threshold"] - 1e-6)
            elif clipped[index] < 0.0:
                self.assertLessEqual(processed["samples"][index],
                                     -config["threshold"] + 1e-6)
        self.assertEqual(processed["projection_count"], 61)
        self.assertEqual(reference.digest_samples(processed["samples"]),
                         self.cases["occupancy_mid"]["output"]["samples_sha256"])

    def test_output_peaks_are_finite_and_cohort_bounded(self):
        peaks = self.document["peak_behavior"]
        self.assertEqual(peaks["complete_cases_with_finite_output"], 17)
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

    def test_all_adverse_controls_are_rejected(self):
        rejections = self.document["adverse_and_skipped"]["control_rejections"]
        self.assertEqual(len(rejections), 17)
        self.assertEqual({item["status"] for item in rejections}, {"rejected"})
        self.assertTrue(all(item["reason"] for item in rejections))
        self.assertEqual({item["case"] for item in rejections}, {
            "missing_threshold", "unknown_control", "threshold_zero",
            "threshold_above_one", "cutoff_below_min", "cutoff_above_nyquist_margin",
            "iterations_zero", "iterations_above_cap", "iterations_not_integer",
            "threshold_not_numeric", "threshold_nonfinite", "unknown_control_key",
            "invalid_candidate_ref", "wrong_protocol_version",
            "override_wrong_block_length", "duplicate_json_key",
            "nonfinite_json_constant",
        })

    def test_pocs_beats_clipped_input_on_this_synthetic_cohort(self):
        comparisons = self.document["controls"]["by_occupancy_si_sdr_db"]
        for name, values in comparisons.items():
            self.assertGreaterEqual(values["pocs"], values["clipped"], name)
        self.assertLess(self.document["controls"]["linear_interp_si_sdr_db"],
                        self.document["controls"]["clipped_anchor_si_sdr_db"])
        self.assertGreater(self.document["controls"]["pocs_mid_occupancy_si_sdr_db"],
                           self.document["controls"]["linear_interp_si_sdr_db"])

    def test_fft_roundtrip_and_impulse_response(self):
        count = 64
        values = [math.sin(2.0 * math.pi * 5 * index / count) + 0.3 *
                  math.cos(2.0 * math.pi * 11 * index / count) for index in range(count)]
        restored = reference.irfft(reference.rfft(values), count)
        self.assertLess(reference.max_abs_diff(values, restored), 1e-9)
        impulse = [0.0] * count
        impulse[7] = 1.0
        spectrum = reference.rfft(impulse)
        self.assertTrue(all(abs(abs(bin_value) - 1.0) < 1e-9 for bin_value in spectrum))
        self.assertLess(reference.max_abs_diff(
            impulse, reference.irfft(spectrum, count)), 1e-9)

    def test_linear_interpolation_and_clip_mask_helpers(self):
        expected = [reference.f32(value) for value in (-0.5, -0.2, 0.0, 0.2, 0.5)]
        clipped = reference.hard_clip([-1.0, -0.2, 0.0, 0.2, 1.0], 0.5)
        self.assertEqual(clipped, expected)
        self.assertEqual(reference.clip_mask(clipped, 0.5), [True, False, False,
                                                             False, True])
        three = reference.hard_clip([-0.5, -0.9, 0.5], 0.5)
        self.assertEqual(reference.linear_interpolate(three, [False, True, False]),
                         [reference.f32(value) for value in (-0.5, 0.0, 0.5)])

    def test_adapter_inspect_boundary(self):
        request = {
            "protocol_version": 1,
            "operation": "inspect",
            "candidate_ref": dict(report.CANDIDATE_REF),
            "adapter_ref": dict(report.ADAPTER_REF),
            "configuration": {"control": "pocs_declip",
                              **report.base_config()},
        }
        inspected = run.inspect(request)
        self.assertEqual(inspected["identity"], run.IDENTITY)
        self.assertEqual(inspected["supported_modes"], ["offline"])
        self.assertEqual(inspected["supported_tasks"], [])
        self.assertEqual(inspected["supported_controls"], list(run.CONTROLS))
        self.assertIn("unregistered", inspected["registration"])

    def test_run_cli_writes_the_same_canonical_result(self):
        case = report.CASES[5]
        request = report.request_for(case)
        with tempfile.TemporaryDirectory(prefix="pocs-cli-") as scratch:
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
            lambda item: item.update(stimulus_id="missing_stimulus"),
            lambda item: item["candidate_ref"].update(revision=0),
        ):
            request = json.loads(json.dumps(valid))
            mutation(request)
            with self.assertRaises(run.RequestError):
                run.run(request)

    def test_report_regeneration_from_clean_copy_is_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="pocs-report-") as scratch:
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
