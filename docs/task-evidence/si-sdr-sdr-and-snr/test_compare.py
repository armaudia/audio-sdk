import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

import compare


class SyntheticComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Exercise the developer entry point, including the emitted strict JSON.
        cls.report = json.loads(subprocess.check_output([
            sys.executable, str(Path(compare.__file__)),
        ]))
        cls.cases = cls.report["cases"]

    def test_delay_and_valid_regions(self):
        self.assertEqual(self.report["synthetic_measured_content_delay_samples"], 160)
        for item, interval, raw in (
            ("long", [0, 340], [160, 500]), ("short", [1, 161], [161, 321]),
        ):
            self.assertEqual(self.cases[item]["source_interval"], interval)
            self.assertEqual(self.cases[item]["raw_interval"], raw)
            self.assertEqual(self.cases[item]["valid_samples"], interval[1] - interval[0])
            self.assertEqual(self.cases[item]["variants"]["identity"]["status"], "scored")

        trace = json.loads(compare.SDK_FIXTURE.read_bytes())["trace"]
        for delay, reason in ((None, "unverified"), (0, "mismatch"), (320, "mismatch")):
            with self.assertRaisesRegex(ValueError, "timing_mapping_" + reason):
                compare.map_interval(trace, (0, 340), delay)
        with self.assertRaisesRegex(ValueError, "incomplete_valid_region"):
            compare.map_interval(trace, (0, 341), 160)
        trace["entries"][2]["valid_count"] = "159"
        with self.assertRaisesRegex(ValueError, "incomplete_valid_region"):
            compare.map_interval(trace, (0, 340), 160)
        self.assertIsNone(compare.impulse_delay([1, 0], [0, 1, 1]))
        self.assertIsNone(compare.impulse_delay([1, 0], [0, 0, 2]))

    def test_analytical_scores_and_aggregation(self):
        for name, amp, reduction in (("long", 0.5, 0.25), ("short", 0.25, 0.5)):
            rows = self.cases[name]["variants"]
            for metric in compare.METRIC_IDS:
                baseline = rows["identity"]["metrics"][metric]["value_db"]
                self.assertAlmostEqual(baseline, -20 * math.log10(amp), places=10)
                less = rows["less_noise"]["metrics"][metric]["value_db"]
                self.assertAlmostEqual(less - baseline, -20 * math.log10(reduction), places=10)
                more = rows["more_noise"]["metrics"][metric]["value_db"]
                self.assertAlmostEqual(more - baseline, -20 * math.log10(2), places=10)
            self.assertAlmostEqual(rows["less_noise"]["metrics"]["si_sdr_improvement_db"]["value_db"],
                                   -20 * math.log10(reduction), places=10)
            self.assertAlmostEqual(rows["half_gain"]["rms_gain_ratio"]["value"], 0.5, places=10)
            gain_snr = -10 * math.log10(0.25 + (0.5 * amp)**2)
            self.assertAlmostEqual(rows["half_gain"]["metrics"]["local_snr_db"]["value_db"], gain_snr)
            self.assertAlmostEqual(rows["half_gain"]["metrics"]["local_sd_sdr_db"]["value_db"],
                                   gain_snr + 20 * math.log10(0.5))
        def mean(variant, metric):
            return self.report["summaries"][variant][metric]["mean_delta_db"]

        self.assertAlmostEqual(mean("less_noise", "si_sdr_db"), 10 * math.log10(8), places=10)
        self.assertEqual(mean("half_gain", "si_sdr_db"), 0)
        self.assertEqual(mean("dc_offset", "si_sdr_db"), 0)
        self.assertEqual(mean("dc_offset", "local_sd_sdr_db"), 0)
        self.assertAlmostEqual(mean("dc_offset", "local_snr_db"), -5, places=10)

    def test_missing_invalid_and_undefined_are_not_scores(self):
        for variant, case, status, reason in (
            ("missing", "short", "blocked", "missing_output"),
            ("nonfinite", "long", "invalid", "nonfinite_valid_output"),
        ):
            self.assertEqual(self.cases[case]["variants"][variant],
                             {"status": status, "reason": reason, "metrics": None})
            for summary in self.report["summaries"][variant].values():
                self.assertEqual((summary["paired"], summary["eligible"]), (1, 2))
                self.assertEqual(summary["coverage"], "partial_diagnostic")
                self.assertEqual(summary["excluded"], {case: {"candidate": reason, "identity": None}})
                self.assertNotIn(case, summary["paired_delta_db"])

        ref = np.array([0.25, -0.25, 0.25, -0.25])
        mapped = slice(0, 4), 4
        self.assertEqual(compare.score(None, ref, ref, mapped)["reason"], "missing_reference")
        self.assertEqual(compare.score(ref, ref, ref[:-1], mapped),
                         {"status": "failed", "reason": "incomplete_output", "metrics": None})
        perfect = compare.score(ref, ref, ref, mapped)["metrics"]
        self.assertTrue(all(item == {"value_db": None, "reason": "perfect_reconstruction"}
                            for item in perfect.values()))
        zero_ref = compare.score(ref * 0, ref, ref, mapped)["metrics"]
        self.assertTrue(all(item["reason"] == "zero_reference_energy" for item in zero_ref.values()))
        silenced = compare.score(ref, ref, ref * 0, mapped)["metrics"]
        self.assertEqual(silenced["si_sdr_db"]["reason"], "zero_output_energy")
        self.assertEqual(silenced["local_sd_sdr_db"]["reason"], "zero_projected_energy")
        self.assertEqual(silenced["local_snr_db"], {"value_db": 0.0, "reason": None})


if __name__ == "__main__":
    unittest.main()
