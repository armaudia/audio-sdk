# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

from fractions import Fraction
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from reference import BLOCK, CAPACITY, LIMIT, SLEW, TARGET, UNITY, rate_ppm
from report import CASES, adverse, report, summarize, trace
from run import canonical, dispatch_json, request


def run(values, policy="controller"):
    return dispatch_json(canonical(request(values, policy)))


class ReferenceTest(unittest.TestCase):
    def test_law_direction_clamp_and_slew(self):
        self.assertEqual(rate_ppm(TARGET * UNITY, UNITY), UNITY)
        for queued, sign in ((0, -1), (CAPACITY * UNITY, 1)):
            self.assertEqual(rate_ppm(queued, UNITY), UNITY + sign * SLEW)
            rate = UNITY
            for _ in range(LIMIT // SLEW + 2):
                rate = rate_ppm(queued, rate)
            self.assertEqual(rate, UNITY + sign * LIMIT)
            self.assertEqual(rate_ppm(TARGET * UNITY, rate), rate - sign * SLEW)

    def test_exact_timeline_accounting_and_bounds(self):
        for name, values in CASES.items():
            for policy in ("controller", "fixed_1x"):
                with self.subTest(case=name, policy=policy):
                    result = run(values, policy)
                    self.assertFalse(result["candidate_qualified"])
                    self.assertEqual(result["paced_device"], "not_run")
                    consumed = accepted = 0
                    previous_rate = UNITY
                    last_state = None
                    for tick, row in enumerate(result["timeline"]):
                        self.assertEqual(row["playout_start"], tick * BLOCK)
                        self.assertEqual(row["source_start_usamples"], consumed)
                        state = row["state"]
                        scheduled = min(values["source_samples"], (tick + 1) * BLOCK
                                        * (UNITY + values["source_drift_ppm"]) // UNITY)
                        hold_start = values["hold_start_tick"]
                        visible = (accepted if hold_start <= tick < hold_start + values["hold_ticks"]
                                   else scheduled)
                        if state == "overflow":
                            self.assertEqual(row["arrivals"], visible - accepted)
                            self.assertGreater((accepted + row["arrivals"]) * UNITY - consumed,
                                               CAPACITY * UNITY)
                            self.assertEqual(row["arrivals"], result["rejected_arrival_samples"])
                            self.assertEqual(tick, len(result["timeline"]) - 1)
                            break
                        self.assertGreaterEqual(row["accepted_samples"], accepted)
                        self.assertEqual(row["accepted_samples"], visible)
                        accepted = row["accepted_samples"]
                        queued = accepted * UNITY - consumed
                        self.assertTrue(0 <= queued <= CAPACITY * UNITY)
                        self.assertEqual(row["queued_usamples"], queued)
                        if state == "play":
                            rate = row["rate_ppm"]
                            self.assertLessEqual(abs(rate - UNITY), LIMIT)
                            self.assertLessEqual(abs(rate - previous_rate), SLEW)
                            if policy == "fixed_1x":
                                self.assertEqual(rate, UNITY)
                            duration = Fraction(row["playout_duration"])
                            count = row["source_end_usamples"] - consumed
                            self.assertTrue(0 < count <= queued)
                            self.assertEqual(duration * rate, count)
                            if duration != BLOCK:
                                self.assertTrue(0 < duration < BLOCK)
                                self.assertEqual(tick, len(result["timeline"]) - 1)
                            if last_state in ("prefill", "rebuffer"):
                                self.assertTrue(queued >= TARGET * UNITY
                                                or accepted == values["source_samples"])
                            consumed += count
                            previous_rate = rate
                        last_state = state
                    self.assertEqual(consumed, result["consumed_usamples"])
                    self.assertEqual(accepted, result["accepted_samples"])
                    if result["status"] in ("complete", "rebuffered"):
                        self.assertEqual(consumed, values["source_samples"] * UNITY)
                    else:
                        self.assertEqual(result["status"], "overflow")
                        self.assertLess(accepted, values["source_samples"])

    def test_fixed_identity_and_final_tail(self):
        values = CASES["nominal_final_partial"]
        baseline = summarize(run(values, "fixed_1x"))
        self.assertEqual(baseline["status"], "complete")
        self.assertEqual(baseline["rate_changes"], 0)
        self.assertEqual(baseline["active_playout_samples"], str(values["source_samples"]))
        self.assertEqual(baseline["prefill_samples"], 3040)
        self.assertEqual(baseline["last_play_interval"]["playout_duration"], "17")
        for policy in ("controller", "fixed_1x"):
            short = run(trace(samples=1), policy)
            self.assertEqual(short["status"], "complete")
            self.assertEqual(short["consumed_usamples"], UNITY)
            self.assertEqual(len(short["timeline"]), 1)

    def test_matched_positive_and_negative_drift(self):
        for name, sign in (("source_fast_1000ppm", 1), ("source_slow_1000ppm", -1)):
            values = CASES[name]
            candidate = run(values)
            control = run(values, "fixed_1x")
            self.assertEqual(candidate["status"], "complete")
            rate = candidate["timeline"][1000]["rate_ppm"]
            self.assertGreater(sign * (rate - UNITY), 0)
            metric = "average_live_abs_target_error_samples"
            self.assertLess(Fraction(summarize(candidate)[metric]),
                            Fraction(summarize(control)[metric]) / 4)

    def test_rebuffer_is_gap_not_content_and_overflow_rejects_batch(self):
        for policy in ("controller", "fixed_1x"):
            result = run(CASES["hold_then_release"], policy)
            self.assertEqual(result["status"], "rebuffered")
            self.assertEqual(result["rebuffer_count"], 1)
            self.assertEqual(summarize(result)["rebuffer_samples"], 3360)
            self.assertEqual(result["timeline"][240]["state"], "play")
            for name in ("beyond_control_range", "overflow_on_release"):
                failed = run(CASES[name], policy)
                self.assertEqual(failed["status"], "overflow")
                self.assertGreater(failed["rejected_arrival_samples"], 0)
                self.assertFalse(failed["candidate_qualified"])
        result = run(CASES["beyond_control_range"])
        self.assertEqual(summarize(result)["rate_bounds_ppm"][1], UNITY + LIMIT)

    def test_rejections_and_fresh_replay(self):
        before = run(CASES["nominal_final_partial"])
        for name, text in adverse().items():
            with self.subTest(name=name):
                result = dispatch_json(text)
                self.assertEqual(result["status"], "missing" if name == "missing_trace" else "invalid")
                self.assertNotIn("timeline", result)
                self.assertFalse(result["candidate_qualified"])
        self.assertEqual(run(CASES["nominal_final_partial"]), before)

    def test_adapter_cli(self):
        with TemporaryDirectory() as scratch:
            src, dst = (Path(scratch) / f"{name}.json" for name in ("request", "result"))
            cli = [sys.executable, str(Path(__file__).with_name("run.py")),
                   "--request", str(src), "--result", str(dst)]
            for value, status, code in (
                (None, "missing", 1), (request(), "complete", 0),
                (request(CASES["nominal_final_partial"]), "complete", 0),
                (request(CASES["hold_then_release"]), "rebuffered", 1),
            ):
                if value is not None:
                    src.write_text(canonical(value), encoding="utf-8")
                self.assertEqual(subprocess.run(cli, check=False).returncode, code)
                self.assertIn(f'"status":"{status}"', dst.read_text(encoding="utf-8"))
                self.assertIn('"candidate_qualified":false', dst.read_text(encoding="utf-8"))

    def test_frozen_report(self):
        expected = Path(__file__).with_name("report.json").read_bytes()
        self.assertEqual(canonical(report()).encode(), expected)


if __name__ == "__main__":
    unittest.main()
