# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the Stream.FM dereverberation blocker package.

No network, no source import, no checkpoint, no runtime, no real audio and no
skips.  Run after ``run.py`` so the generated artifacts exist::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""

from __future__ import annotations

import hashlib
import math
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
REPORT_CACHE = None

def report() -> dict:
    global REPORT_CACHE
    if REPORT_CACHE is None:
        REPORT_CACHE = reference.build_report()
    return REPORT_CACHE

class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_sorted_and_newline(self):
        data = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertTrue(data.endswith(b"\n"))
        self.assertLess(data.index(b'"a"'), data.index(b'"b"'))

    def test_strict_loads_accepts_object(self):
        self.assertEqual(reference.strict_loads('{"a": 1}'), {"a": 1})

    def test_strict_loads_rejects_duplicate(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1, "a": 2}')

    def test_strict_loads_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": NaN}')

    def test_strict_loads_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": Infinity}')

    def test_strict_loads_rejects_non_object(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('[1, 2]')

    def test_strict_loads_rejects_trailing(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1} trailing')

    def test_negative_zero_detection(self):
        self.assertTrue(reference.has_negative_zero({"a": -0.0}))
        self.assertFalse(reference.has_negative_zero({"a": 0.0}))

    def test_metric_normalises_zero(self):
        self.assertEqual(reference._metric(-0.0), 0.0)

    def test_metric_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            reference._metric(math.inf)

class FixtureTests(unittest.TestCase):
    def test_total_samples(self):
        self.assertEqual(len(reference.FIXTURE_COMPONENTS["reverb"]), reference.TOTAL_SAMPLES)

    def test_segments_cover_window(self):
        covered = sum((s["end_frame"] - s["start_frame"]) * reference.FRAME_SAMPLES
                      for s in reference.SEGMENTS)
        self.assertEqual(covered, reference.TOTAL_SAMPLES)

    def test_digests_present(self):
        for k in ("clean", "early", "late", "noise", "reverb"):
            self.assertIn(k, reference.FIXTURE_DIGESTS)
            self.assertRegex(reference.FIXTURE_DIGESTS[k], r"^[0-9a-f]{64}$")

class SurrogateTests(unittest.TestCase):
    def test_silence_exact_zero(self):
        out = reference.run_offline([0.0] * 512)["output"]
        self.assertTrue(all(v == 0.0 for v in out))
        self.assertEqual(len(out), 512)

    def test_impulse_delay(self):
        samples = [0.0] * 4096
        samples[2000] = 1.0
        out = reference.run_offline(samples)["output"]
        peak = max(range(len(out)), key=lambda i: abs(out[i]))
        self.assertEqual(peak, 2256)

    def test_partial_tail(self):
        full = reference.run_offline(reference.as_float(reference.FIXTURE_COMPONENTS["reverb"]))
        partial = reference.run_offline(reference.as_float(reference.FIXTURE_COMPONENTS["reverb"][:1000]))
        self.assertEqual(len(partial["output"]), 1000)
        self.assertEqual(partial["output"], full["output"][:1000])
        self.assertEqual(partial["tail_valid"], 232)

    def test_streaming_parity(self):
        samples = reference.as_float(reference.FIXTURE_COMPONENTS["reverb"])
        ref = reference.run_offline(samples)["output"]
        for chunk in (160, 256, 320, 480, 137, 641):
            got = reference.drive_streaming(samples, chunk)["output"]
            self.assertEqual(got, ref, f"chunk={chunk}")

    def test_reset_fresh_session_parity(self):
        samples = reference.as_float(reference.FIXTURE_COMPONENTS["reverb"][:reference.FRAME_SAMPLES * 3])
        def run(epoch):
            s = reference.Session(dict(reference.CONFIG), "r", epoch)
            for i in range(3):
                s.process_frame(samples[i*256:(i+1)*256], final=(i == 2))
            s.drain()
            return s.state_digest()
        self.assertEqual(run(1), run(1))

    def test_stale_epoch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG), "s", 0)
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG), "s", -1)

    def test_max_abs_finite_and_bounded(self):
        out = reference.run_offline(reference.as_float(reference.FIXTURE_COMPONENTS["reverb"]))["output"]
        self.assertTrue(all(math.isfinite(v) for v in out))
        self.assertLessEqual(max(abs(v) for v in out), 1.0)

    def test_silence_stratum_exact_zero(self):
        out = reference.run_offline(reference.as_float(reference.FIXTURE_COMPONENTS["reverb"]))["output"]
        self.assertTrue(all(v == 0.0 for v in out[:50 * reference.FRAME_SAMPLES]))

class AdverseControlTests(unittest.TestCase):
    def test_config_rejections(self):
        ctrl = report()["controls"]["config"]
        self.assertTrue(ctrl["rejected_all"])
        self.assertTrue(ctrl["state_unchanged"])

    def test_frame_rejections(self):
        ctrl = report()["controls"]["frame"]
        self.assertTrue(ctrl["rejected_all"])
        self.assertTrue(ctrl["accepted_after_rejections"])

    def test_nonfinite_counter(self):
        ctrl = report()["controls"]["nonfinite_counter"]
        self.assertEqual(ctrl["reason"], "mic_nonfinite")
        self.assertTrue(ctrl["accepted_counter_unchanged"])
        self.assertTrue(ctrl["state_digest_unchanged"])

    def test_asset_rejections(self):
        ctrl = report()["controls"]["asset"]
        self.assertTrue(ctrl["rejected_all"])
        self.assertFalse(ctrl["generic_admission"]["pinned_asset"])

    def test_delay_control(self):
        ctrl = report()["controls"]["delay"]
        self.assertTrue(ctrl["matches"])
        self.assertEqual(ctrl["observed_output_index"], 2256)

    def test_partial_tail_control(self):
        ctrl = report()["controls"]["partial_tail"]
        self.assertTrue(ctrl["length_preserved"])
        self.assertTrue(ctrl["prefix_matches_full"])
        self.assertEqual(ctrl["tail_valid"], 232)

    def test_streaming_parity_control(self):
        ctrl = report()["controls"]["streaming_parity"]
        self.assertTrue(ctrl["all_identical"])

    def test_reset_control(self):
        ctrl = report()["controls"]["reset"]
        self.assertTrue(ctrl["fresh_session_matches"])
        self.assertTrue(ctrl["stale_epoch_rejected_all"])

class ReportTests(unittest.TestCase):
    def test_disposition(self):
        r = report()
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "proposal_only_blocked_incomplete")
        self.assertEqual(r["evidence_status"], "incomplete")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertTrue(r["proposal_only"])
        self.assertEqual(r["qualification"]["status"], "not_qualified")
        self.assertTrue(r["qualification"]["not_qualified"])
        self.assertFalse(r["qualification"]["missing_result_promoted"])

    def test_board_row_not_full_hash(self):
        r = report()
        self.assertFalse(r["board_row"]["full_tasks_json_hashed"])
        self.assertEqual(r["board_row"]["stable_sha256"], reference.BOARD_ROW_STABLE_SHA256)

    def test_gates_blocked(self):
        gates = report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in gates))
        self.assertTrue(all(g["qualifies"] is False for g in gates))

    def test_no_missing_result_qualifies(self):
        self.assertTrue(report()["no_missing_result_qualifies_candidate"])

    def test_required_keys(self):
        self.assertEqual(set(report().keys()), reference.REQUIRED_REPORT_KEYS)
        self.assertEqual(set(reference.contract_payload().keys()), reference.REQUIRED_CONTRACT_KEYS)

    def test_report_deterministic(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())

    def test_contract_deterministic(self):
        self.assertEqual(reference.contract_bytes(), reference.contract_bytes())

    def test_upstream_present_but_blocked(self):
        u = report()["upstream"]
        self.assertTrue(u["source_present"])
        self.assertEqual(u["commit"], reference.UPSTREAM_COMMIT)
        self.assertEqual(u["license"], "AGPL-3.0-only")
        self.assertIsNone(u["checkpoint_identity"])

    def test_boundary(self):
        for k, v in report()["boundary"].items():
            if k == "descriptor_settings":
                self.assertEqual(v, {})
            else:
                self.assertFalse(v, k)

    def test_scope(self):
        s = report()["scope"]
        self.assertFalse(s["downloaded"])
        self.assertFalse(s["weights_loaded"])
        self.assertFalse(s["runtime_executed"])
        self.assertFalse(s["provider_registered"])
        self.assertTrue(s["task_local_only"])

class ArtifactTests(unittest.TestCase):
    def test_report_file_matches(self):
        if not (HERE / "report.json").exists():
            self.fail("report.json missing; run run.py")
        self.assertEqual((HERE / "report.json").read_bytes(), reference.canonical_report_bytes())

    def test_contract_file_matches(self):
        if not (HERE / "contract.json").exists():
            self.fail("contract.json missing; run run.py")
        self.assertEqual((HERE / "contract.json").read_bytes(), reference.contract_bytes())

    def test_report_sha_sidecar(self):
        p = HERE / "report.json.sha256"
        if not p.exists():
            self.fail("report.json.sha256 missing; run run.py")
        expected = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual(p.read_text().strip(), f"{expected}  report.json")

if __name__ == "__main__":
    unittest.main()
