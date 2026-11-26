# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library acceptance suite for the task-local Speex resampler evidence."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import unittest

import reference
import run
import verify

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SOURCES = HERE / "SOURCES.sha256"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.report_text, cls.report_canonical = reference.canonical_report(
            cls.report)

    def test_task_identity(self) -> None:
        self.assertEqual(reference.TASK, "SDK-SPEEX-RESAMPLER")
        self.assertEqual(reference.COMPONENT, "speex-resampler")
        self.assertEqual(reference.BASE_COMMIT,
                         "8defcae2b153b52668c93791463497ea261b7fb1")

    def test_decision_is_defer_and_not_qualified(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(self.report["remaining_gate_count"], 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reason"])
            self.assertTrue(gate["reopen"])

    def test_required_results_present(self) -> None:
        required = self.report["qualification"]["required_results"]
        self.assertTrue(required)
        self.assertTrue(all(required.values()))
        self.assertTrue(self.report["qualification"]["all_required_results_present"])

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = reference.linked_row_identity()
        self.assertEqual(len(identity), 64)
        payload = {
            field: reference.LINKED_ROW[field]
            for field in reference.LINKED_ROW["identity_fields"]
        }
        self.assertNotIn("line_at_read", payload)
        self.assertEqual(
            identity,
            hashlib.sha256(reference.canonical_bytes(payload)).hexdigest())

    def test_validate_speed_accepts_declared(self) -> None:
        for case in reference.SPEED_CASES:
            speed = reference.validate_speed(int(case["num"]), int(case["den"]))
            self.assertEqual(float(speed), int(case["num"]) / int(case["den"]))

    def test_validate_speed_rejects_out_of_range(self) -> None:
        with self.assertRaises(reference.InvalidSpeed):
            reference.validate_speed(1, 4)
        with self.assertRaises(reference.InvalidSpeed):
            reference.validate_speed(3, 1)
        with self.assertRaises(reference.InvalidSpeed):
            reference.validate_speed(0, 1)

    def test_validate_speed_rejects_bool(self) -> None:
        with self.assertRaises(reference.InvalidSpeed):
            reference.validate_speed(True, 1)

    def test_validate_quality(self) -> None:
        self.assertEqual(reference.validate_quality(4), 4)
        with self.assertRaises(reference.InvalidQuality):
            reference.validate_quality(11)
        with self.assertRaises(reference.InvalidQuality):
            reference.validate_quality(True)

    def test_validate_samples_rejects_empty(self) -> None:
        with self.assertRaises(reference.MissingStimulus):
            reference.validate_samples([])

    def test_validate_samples_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.NonfiniteInput):
            reference.validate_samples([0.0, float("nan")])

    def test_validate_samples_rejects_range(self) -> None:
        with self.assertRaises(reference.OutOfRangeInput):
            reference.validate_samples([reference.MAX_ABS_INPUT + 1.0])

    def test_fixtures_are_deterministic(self) -> None:
        for name, generator in reference.fixture_generators().items():
            self.assertEqual(reference.tensor_digest(generator()),
                             reference.tensor_digest(generator()), name)

    def test_fixture_digest_matches_report(self) -> None:
        self.assertEqual(self.report["fixture_digest"], reference.fixture_digest())

    def test_expected_output_samples(self) -> None:
        self.assertEqual(reference.expected_output_samples(9600, 3, 4), 12800)
        self.assertEqual(reference.expected_output_samples(9600, 1, 1), 9600)
        self.assertEqual(reference.expected_output_samples(9600, 5, 4), 7680)
        self.assertEqual(reference.expected_output_samples(9600, 3, 2), 6400)
        self.assertEqual(reference.expected_output_samples(8075, 5, 4), 6460)

    def test_expected_anchor(self) -> None:
        self.assertEqual(reference.expected_anchor(1600, 1, 1, 32), 1632)
        self.assertEqual(reference.expected_anchor(1600, 5, 4, 40), 1320)
        self.assertEqual(reference.expected_anchor(1600, 3, 4, 33), 2166)

    def test_harness_compiles(self) -> None:
        binary = reference.build_harness()
        self.assertTrue(binary.is_file())

    def test_speed_one_duration(self) -> None:
        result = reference.resample(reference.synthetic_speech(1600), 1, 1)
        self.assertEqual(result["output_samples"], 1600)
        self.assertEqual(result["consumed"], 1600)

    def test_all_speeds_duration_exact(self) -> None:
        signal = reference.synthetic_speech(1600)
        for case in reference.SPEED_CASES:
            num, den = int(case["num"]), int(case["den"])
            result = reference.resample(signal, num, den)
            self.assertEqual(
                result["output_samples"],
                reference.expected_output_samples(len(signal), num, den),
                case["label"])

    def test_source_anchor_mapping_is_exact(self) -> None:
        positions = (0, 1600, 4000, 6400)
        signal = reference.impulse_train(8000, positions)
        for case in reference.SPEED_CASES:
            num, den = int(case["num"]), int(case["den"])
            result = reference.resample(signal, num, den)
            proxy = reference.transient_proxy(
                result["output"], positions, num, den,
                result["output_latency"])
            self.assertEqual(proxy["max_abs_residual_samples"], 0, case["label"])

    def test_pitch_shift_matches_speed(self) -> None:
        tone = reference.tonal_220hz()
        for case in reference.SPEED_CASES:
            num, den = int(case["num"]), int(case["den"])
            result = reference.resample(tone, num, den)
            proxy = reference.pitch_proxy(tone, result["output"])
            self.assertAlmostEqual(proxy["ratio"], num / den, delta=0.03)

    def test_silence_produces_no_energy(self) -> None:
        result = reference.resample(reference.silence(), 5, 4)
        self.assertEqual(reference.peak_abs(result["output"]), 0.0)

    def test_final_partial_window_is_exact(self) -> None:
        partial = reference.resample(reference.synthetic_speech(8075), 5, 4)
        self.assertEqual(partial["output_samples"], 6460)

    def test_nonfinite_input_is_rejected(self) -> None:
        with self.assertRaises(reference.NonfiniteInput):
            reference.resample([0.0, float("inf")], 1, 1)

    def test_missing_stimulus_is_blocked(self) -> None:
        with self.assertRaises(reference.MissingStimulus):
            reference.resample([], 1, 1)

    def test_invalid_quality_is_rejected(self) -> None:
        with self.assertRaises(reference.InvalidQuality):
            reference.resample([0.1], 1, 1, 11)

    def test_adverse_controls_have_no_metrics(self) -> None:
        adverse = self.report["adverse"]
        for name in ("nonfinite_input", "out_of_range_speed_low",
                     "out_of_range_speed_high", "invalid_quality",
                     "missing_result"):
            self.assertEqual(adverse[name]["status"], "rejected", name)
            self.assertIsNone(adverse[name]["metrics"], name)
        self.assertEqual(adverse["nonfinite_output_guard"]["status"], "checked")

    def test_rate_case_durations_and_anchors(self) -> None:
        for label, case in self.report["rate_cases"].items():
            self.assertTrue(case["duration_exact"], label)
            self.assertEqual(case["expected_output_samples"],
                             case["observed_output_samples"], label)
            self.assertEqual(case["transient_max_abs_residual_samples"], 0, label)
            self.assertTrue(case["speech_preservation_proxy"]["contrast_preserved"],
                            label)

    def test_pitch_is_varispeed(self) -> None:
        self.assertEqual(self.report["pitch"]["identity_1x"]["ratio"], 1.0)
        adverse = self.report["pitch"]["varispeed_adverse_control"]
        self.assertTrue(adverse["pitch_shifted"])
        self.assertGreaterEqual(abs(adverse["ratio"] - 1.0), 0.10)

    def test_rebuffer_and_drift(self) -> None:
        drift = self.report["drift_and_rebuffer"]["drift"]
        self.assertEqual(drift["observed_output_samples"],
                         drift["expected_output_samples"])
        self.assertEqual(drift["anchors"]["max_abs_residual_samples"], 0)
        fifo = self.report["drift_and_rebuffer"]["rebuffer"]["synthetic_fifo"]
        self.assertTrue(fifo["stall_refill_resume_observed"])
        self.assertEqual(fifo["played_samples"], fifo["expected_output_samples"])

    def test_report_has_no_nonfinite_numbers(self) -> None:
        self.assertNotIn("NaN", self.report_text)
        self.assertNotIn("Infinity", self.report_text)

    def test_report_is_byte_reproducible(self) -> None:
        again, _ = reference.canonical_report(reference.build_report())
        self.assertEqual(again, self.report_text)

    def test_report_file_and_sidecar_match(self) -> None:
        payload = REPORT.read_bytes()
        self.assertEqual(payload,
                         (self.report_text + "\n").encode("utf-8"))
        self.assertEqual(SIDECAR.read_text(encoding="ascii").strip(),
                         hashlib.sha256(payload).hexdigest())

    def test_contract_matches_report(self) -> None:
        contract = load(CONTRACT)
        self.assertEqual(contract["task"], reference.TASK)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["canonical_report"]["file_sha256"],
                         hashlib.sha256(REPORT.read_bytes()).hexdigest())
        self.assertEqual(contract["linked_row_identity"],
                         self.report["linked_row_identity"])
        self.assertEqual(len(contract["gates"]), 8)

    def test_sources_pins_recompute(self) -> None:
        lines = [line for line in SOURCES.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        parsed = {}
        for line in lines:
            digest, path = line.split("  ", 1)
            parsed[path] = digest
        for name in reference.ARTIFACT_FILES:
            path = reference.TASK_PREFIX + name
            self.assertEqual(parsed[path],
                             hashlib.sha256((HERE / name).read_bytes()).hexdigest())
        for path, digest in reference.VENDORED_PINS.items():
            self.assertEqual(parsed[path], digest)

    def test_verify_scope_and_pins(self) -> None:
        errors: list[str] = []
        verify.check_pins(errors)
        verify.check_json(errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
