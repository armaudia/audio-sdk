"""Deterministic acceptance tests for the D1 whole-clip planner evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import fixtures
import reference
import report
import run

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
TASK_PREFIX = "docs/task-evidence/d1-whole-clip-duration-planner/"
EXPECTED_REPORT_SHA256 = "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98"


def result_for(case_id: str, variant: str) -> dict:
    response = run.dispatch(run_request(scenario="case", case_id=case_id, variant=variant,
                                        attempt_id="test-" + case_id + "-" + variant))
    return response["result"]


def run_request(**fields) -> dict:
    return report.standard_request("run", **fields)


def rate(result: dict) -> reference.Fraction:
    return reference.read_frac_json(result["budget"]["speech_rate"])


def flex_rate(result: dict) -> reference.Fraction:
    return reference.read_frac_json(result["budget"]["flex_rate"])


def rational(field: dict) -> reference.Fraction:
    return reference.read_frac_json(field)


class D1PlannerEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stimuli = fixtures.load_stimuli()
        cls.pins = fixtures.verify_source_pins(cls.stimuli)
        cls.inspect = run.dispatch(report.standard_request("inspect"))
        cls.case_rows = []
        for case_id in cls.stimuli["cases"]:
            for variant in cls.stimuli["case_variants"][case_id]:
                cls.case_rows.append((case_id, variant, result_for(case_id, variant)))
        cls.lookup = {(case_id, variant): result
                      for case_id, variant, result in cls.case_rows}

    def test_01_source_pins_verify(self) -> None:
        self.assertEqual(len(self.pins), 4)
        self.assertTrue(all(pin["verified"] for pin in self.pins))
        paths = [pin["path"] for pin in self.pins]
        self.assertIn("cpp-library/pipeline-validation/playback-speed/README.md", paths)
        self.assertIn("audio-benchmark-platform/plan/swarm/VERIFICATION.md", paths)

    def test_02_stimuli_fixture_is_pinned(self) -> None:
        self.assertEqual(len(self.stimuli["cases"]), 10)
        self.assertEqual(fixtures.stimuli_digest(),
                         hashlib.sha256(fixtures.STIMULI_PATH.read_bytes()).hexdigest())
        for case_id, case in self.stimuli["cases"].items():
            self.assertEqual(reference.case_digest(case), self.stimuli["case_digests"][case_id])

    def test_03_adapter_descriptor_is_unregistered(self) -> None:
        descriptor = run.adapter_descriptor()
        self.assertEqual(descriptor["identity"], reference.IDENTITY)
        self.assertEqual(descriptor["protocol_version"], 1)
        self.assertIn("unregistered", descriptor["registration"])
        self.assertEqual(descriptor["configuration"]["sample_rate_hz"], 16000)
        self.assertEqual(descriptor["configuration"]["sdk_frame_samples"], 160)

    def test_04_inspect_boundary(self) -> None:
        self.assertEqual(self.inspect["operation"], "inspect")
        self.assertEqual(self.inspect["identity"], reference.IDENTITY)
        self.assertEqual(self.inspect["boundary_identity"], reference.BOUNDARY_IDENTITY)
        self.assertIn("oracle_compensated", self.inspect["supported_variants"])
        self.assertEqual(self.inspect["buffering"]["mode"], "offline_whole_clip")
        self.assertFalse(self.inspect["candidate_qualified"])

    def test_05_duplicate_json_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"protocol_version":1,"protocol_version":1}\n', encoding="utf-8")
            with self.assertRaises(run.RequestError):
                run.read_json(path)

    def test_06_nonfinite_json_constant_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"value":NaN}\n', encoding="utf-8")
            with self.assertRaises(run.RequestError):
                run.read_json(path)

    def test_07_unknown_request_field_rejected(self) -> None:
        with self.assertRaises(run.RequestError):
            run.validate_request(run_request(unexpected_field=True), "run")

    def test_08_invalid_reference_revision_rejected(self) -> None:
        bad = run_request(candidate_ref={"kind": "reference", "id": "x", "revision": 0})
        with self.assertRaises(run.RequestError):
            run.validate_request(bad, "run")

    def test_09_unsupported_control_rejected(self) -> None:
        config = dict(run.DEFAULT_CONFIG, control="other")
        with self.assertRaises(ValueError):
            run.validate_request(run_request(configuration=config), "run")

    def test_10_wrong_sample_rate_rejected(self) -> None:
        config = dict(run.DEFAULT_CONFIG, sample_rate_hz=48000)
        with self.assertRaises(ValueError):
            run.validate_request(run_request(configuration=config), "run")

    def test_11_unknown_case_rejected(self) -> None:
        response = run.dispatch(run_request(scenario="case", case_id="missing", variant="d1"))
        self.assertEqual(response["result"]["status"], "rejected")
        self.assertEqual(response["result"]["reason"], "unknown_case")

    def test_12_undeclared_variant_rejected(self) -> None:
        response = run.dispatch(run_request(scenario="case", case_id="identity_all_speech",
                                            variant="oracle_compensated"))
        self.assertEqual(response["result"]["status"], "rejected")
        self.assertEqual(response["result"]["reason"], "variant_not_declared_for_case")

    def test_13_manual_caller_owned_case_boundary(self) -> None:
        case = json.loads(json.dumps(self.stimuli["cases"]["identity_all_speech"]))
        response = run.dispatch(run_request(scenario="manual", variant="d1", case_data=case))
        self.assertNotIn("reason", response["result"])
        self.assertEqual(response["result"]["case_digest"], reference.case_digest(case))
        self.assertTrue(response["result"]["duration_identity"])

    def test_14_manual_nonfinite_block_rejected(self) -> None:
        case = json.loads(json.dumps(self.stimuli["cases"]["identity_all_speech"]))
        case["blocks"][0]["source_end_sample"] = float("nan")
        with self.assertRaises(ValueError):
            reference.validate_case(case)

    def test_15_one_x_control_identity(self) -> None:
        result = self.lookup[("identity_all_speech", "1x")]
        self.assertTrue(result["duration_identity"])
        self.assertEqual(result["rate_change_count"], 0)
        self.assertEqual(result["initial_rate"], {"num": 1, "den": 1})

    def test_16_no_budget_falls_back_to_one_x(self) -> None:
        result = self.lookup[("identity_all_speech", "d1")]
        self.assertEqual(result["budget"]["fallback_reason"], "insufficient_pause_budget")
        self.assertEqual(rate(result), 1)
        self.assertEqual(flex_rate(result), 1)
        self.assertTrue(result["duration_identity"])

    def test_17_recorded_fast_budget_floor(self) -> None:
        result = self.lookup[("recorded_fast_budget", "d1")]
        self.assertEqual(rate(result), reference.Fraction(19, 20))
        self.assertEqual(flex_rate(result), reference.Fraction(3, 2))
        self.assertTrue(result["budget"]["matches_recorded_slow_floor"])
        self.assertTrue(result["duration_identity"])

    def test_18_recorded_filler_budget_floor(self) -> None:
        result = self.lookup[("recorded_filler_budget", "d1")]
        self.assertEqual(rate(result), reference.Fraction(43, 50))
        self.assertEqual(flex_rate(result), reference.Fraction(3, 2))
        self.assertTrue(result["budget"]["matches_recorded_slow_floor"])
        self.assertTrue(result["duration_identity"])

    def test_19_floor_limited_budget(self) -> None:
        result = self.lookup[("floor_limited_budget", "d1")]
        self.assertTrue(result["budget"]["floor_limited"])
        self.assertEqual(rate(result), reference.Fraction(4, 5))
        self.assertEqual(flex_rate(result), reference.Fraction(28, 19))
        self.assertTrue(result["duration_identity"])

    def test_20_final_partial_window(self) -> None:
        result = self.lookup[("final_partial_window", "d1")]
        window = result["profile_checks"]["final_partial_window"]
        self.assertEqual(window["source_first_sample"], 4800)
        self.assertEqual(window["source_end_sample"], 4965)
        self.assertEqual(window["valid_samples"], 165)
        self.assertEqual(window["sdk_full_frames"], 1)
        self.assertEqual(window["sdk_partial_frame_valid_samples"], 5)
        self.assertTrue(result["blocks"][-1]["final_partial"])
        self.assertTrue(result["duration_identity"])

    def test_21_oracle_labels_change_rate_at_source_timestamp(self) -> None:
        gate = self.lookup[("gate_label_error", "d1")]
        oracle = self.lookup[("gate_label_error", "oracle_labels")]
        gate_at = [change for change in gate["rate_changes"]
                   if change["source_first_sample"] == 16000]
        oracle_at = [change for change in oracle["rate_changes"]
                     if change["source_first_sample"] == 16000]
        self.assertNotEqual(gate_at, oracle_at)
        self.assertTrue(gate["duration_identity"] and oracle["duration_identity"])
        self.assertTrue(oracle["profile_checks"]["rate_bounds"])

    def test_22_material_transitions_respect_bounds(self) -> None:
        result = self.lookup[("material_transitions", "d1")]
        for block in result["blocks"]:
            value = rational(block["rate"])
            upper = reference.FLEX_CEILING if block["label"] in reference.FLEX_LABELS else reference.SPEECH_CEILING
            self.assertLessEqual(value, upper)
        self.assertEqual(result["source_samples"], 16000)
        self.assertTrue(result["duration_identity"])

    def test_23_drift_uncompensated_and_oracle(self) -> None:
        uncompensated = self.lookup[("drift_interval", "drift_uncompensated")]
        oracle = self.lookup[("drift_interval", "oracle_compensated")]
        self.assertFalse(uncompensated["duration_identity"])
        self.assertEqual(rational(uncompensated["duration_error_ns"]), reference.Fraction(93750))
        self.assertTrue(oracle["duration_identity"])
        self.assertTrue(oracle["oracle_compensation"]["feasible"])
        self.assertTrue(oracle["oracle_compensation"]["changed"])

    def test_24_rebuffer_uncompensated_and_oracle(self) -> None:
        uncompensated = self.lookup[("rebuffer_gap", "rebuffer_uncompensated")]
        oracle = self.lookup[("rebuffer_gap", "oracle_compensated")]
        self.assertFalse(uncompensated["duration_identity"])
        self.assertEqual(rational(uncompensated["duration_error_ns"]), reference.Fraction(80_000_000))
        self.assertEqual(uncompensated["playback_events"][0]["source_sample"], 6400)
        self.assertTrue(oracle["duration_identity"])
        self.assertTrue(oracle["oracle_compensation"]["feasible"])

    def test_25_oracle_infeasible_is_reported_not_qualified(self) -> None:
        result = self.lookup[("oracle_infeasible_gap", "oracle_compensated")]
        self.assertFalse(result["oracle_compensation"]["feasible"])
        self.assertIn(result["oracle_compensation"]["reason"],
                      ("nonpositive_compensation_target", "oracle_compensation_out_of_bounds"))
        self.assertFalse(result["duration_identity"])
        self.assertFalse(result["profile_checks"]["candidate_qualified"])

    def test_26_explicit_duration_controls_miss_target(self) -> None:
        fixed = self.lookup[("recorded_fast_budget", "fixed_125")]
        slow = self.lookup[("recorded_fast_budget", "slow_only")]
        self.assertLess(rational(fixed["duration_error_ns"]), 0)
        self.assertGreater(rational(slow["duration_error_ns"]), 0)
        self.assertFalse(fixed["profile_checks"]["rate_bounds"])
        self.assertTrue(slow["profile_checks"]["rate_bounds"])

    def test_27_all_case_results_are_complete_and_unqualified(self) -> None:
        self.assertEqual(len(self.case_rows), 23)
        for _, _, result in self.case_rows:
            self.assertNotIn("reason", result)
            self.assertFalse(result["profile_checks"]["missing_result"])
            checks = result["profile_checks"]
            self.assertFalse(checks["candidate_qualified"])
            self.assertTrue(checks["source_output_mapping"]["union_equals_source"])
            self.assertTrue(checks["source_timestamp_ties"])
            self.assertEqual(checks["pitch_audibility"]["status"], "not_measured")
            self.assertEqual(checks["transient_audibility"]["status"], "not_measured")
            self.assertEqual(checks["buffering"]["mode"], "offline_whole_clip")
            self.assertTrue(result["schedule_digest"])
            self.assertTrue(result["result_digest"])

    def test_28_rate_changes_tied_to_source_timestamps(self) -> None:
        for _, _, result in self.case_rows:
            for change in result["rate_changes"]:
                self.assertEqual(change["source_ns"],
                                 change["source_first_sample"] * reference.NS_PER_SAMPLE)

    def test_29_all_adverse_controls_observed(self) -> None:
        payload = report.build_report()
        document = json.loads(payload)
        rows = document["adverse_controls"]
        self.assertEqual(len(rows), len(run.ADVERSE_IDS))
        for row in rows:
            result = row["response"]["result"]
            self.assertEqual(result["status"], "observed")
            self.assertIn(result["outcome"], ("rejected", "reported_infeasible"))
            self.assertTrue(result["fixture_unchanged"])
            self.assertFalse(result["missing_result"])
            self.assertFalse(result["candidate_qualified"])

    def test_30_report_regeneration_byte_identical(self) -> None:
        payload = report.build_report()
        self.assertEqual(payload, report.REPORT_PATH.read_bytes())
        self.assertEqual(hashlib.sha256(payload).hexdigest(), EXPECTED_REPORT_SHA256)
        sidecar = report.REPORT_PATH.with_name("report.json.sha256").read_text(encoding="utf-8")
        self.assertEqual(sidecar, EXPECTED_REPORT_SHA256 + "  report.json\n")

    def test_31_report_scope_and_coverage(self) -> None:
        document = json.loads(report.build_report())
        self.assertFalse(document["candidate_qualified"])
        self.assertEqual(document["summary"]["missing_result_count"], 0)
        self.assertFalse(document["rate_profile_coverage"]["missing_results_qualify"])
        self.assertTrue(all(document["rate_profile_coverage"][key]["status"] == "observed"
                            for key in ("source_output_duration_mapping", "one_x_control",
                                        "planned_rate_changes_with_recorded_budget",
                                        "oracle_variants", "final_partial_window",
                                        "drift", "rebuffer", "explicit_adverse_controls")))
        scope = document["scope_assertions"]
        for key in ("playback_actuator_installed", "target_device_pacing_measured",
                    "fill_flush_measured", "cpu_or_deadline_measured",
                    "listening_or_quality_score", "real_weights_or_assets",
                    "release_claim", "shared_files_modified"):
            self.assertFalse(scope[key])
        self.assertEqual(document["base_commit"], "dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc")

    def test_32_report_artifact_digests_current(self) -> None:
        document = json.loads(report.build_report())
        for name, digest in document["artifact_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_33_changes_are_task_local(self) -> None:
        output = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"], cwd=WORKTREE)
        lines = output.decode("utf-8").splitlines()
        offenders = []
        for line in lines:
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if not path.startswith(TASK_PREFIX):
                offenders.append(path)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
