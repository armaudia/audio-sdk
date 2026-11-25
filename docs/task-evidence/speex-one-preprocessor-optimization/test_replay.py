# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

import ctypes as c
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import run


class ReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = cls.enterClassContext(tempfile.TemporaryDirectory())
        cls.speex, _ = run.build(Path(scratch))

    def test_delay_and_partial_flush(self):
        # Disable nonlinear features to tag WOLA position independently of the
        # declared mapping. Probe both one and two audio states, with a raw tap.
        for hop in (160, 320):
            samples = [0] * (3 * hop + 73)
            samples[29], samples[-1] = 12000, -10000
            for count in (1, 2):
                stages = tuple((str(i), 0, 0, False) for i in range(count))
                with patch.dict(run.VARIANTS, tag=(stages + (("raw_tap", 0, 0, True),), False)):
                    out, trace, delay = run.replay(self.speex, samples, hop, "tag")
                self.assertEqual(delay, count * hop)
                self.assertEqual(len(out), len(samples))
                self.assertEqual(max(range(len(out)), key=lambda i: abs(out[i])), 29)
                self.assertLess(out[-1], -9000)
                self.assertEqual(trace[-1]["accepted_samples"], 0)
                self.assertEqual(trace[-1]["valid_interval"], [3 * hop, len(samples)])
                self.assertEqual(trace[count]["valid_interval"], [0, hop])
                self.assertTrue(all(f["valid_interval"] is None for f in trace[:count]))
                self.assertIsNone(trace[0]["advisory"])
                self.assertEqual(trace[1]["advisory"]["window"], [0, 2 * hop])
                self.assertIsNone(trace[3]["advisory"])

    def test_advisory_ablation_and_failure_do_not_change_audio(self):
        _, samples, _ = run.fixture(True)
        for hop in (160, 320):
            common, trace, _ = run.replay(self.speex, samples, hop, "common")
            self.assertTrue(any(f["advisory"] is not None for f in trace))
            self.assertEqual(common, run.replay(self.speex, samples, hop, "no_advisory")[0])
            real_control = self.speex.control

            def invalid(state, name, value):
                if name == "GET_PROB":
                    value.value = 101
                    return True
                return real_control(state, name, value)

            with patch.object(self.speex, "control", side_effect=invalid):
                out, bad, _ = run.replay(self.speex, samples, hop, "common")
            self.assertEqual(out, common)
            for f in bad:
                if f["advisory"]:
                    self.assertIsNone(f["advisory"]["prob_pct"])
                    self.assertIsNone(f["advisory"]["advisory_active"])
            self.assertEqual(run.replay(self.speex, samples, hop, "no_agc")[0],
                             run.replay(self.speex, samples, hop, "fallback")[0])

    def test_state_isolation_and_fresh_epoch(self):
        with ExitStack() as stack:
            state = self.speex.state(stack, 160, 1, 1, True)
            untouched = self.speex.state(stack, 160, 1, 1, True)
            for _ in range(15):
                self.speex.run(state, (c.c_int16 * 160)(*([2000, -2000] * 80)))
            fresh = self.speex.state(stack, 160, 1, 1, True)
            a, b = (c.c_int16 * 160)(4000), (c.c_int16 * 160)(4000)
            self.assertEqual(self.speex.run(untouched, a), self.speex.run(fresh, b))
            self.assertEqual(self.speex.probability(untouched), self.speex.probability(fresh))
            self.assertEqual(a[:], b[:])

    def test_backend_failure_aborts_and_releases(self):
        destroy = self.speex.destroy
        with (patch.object(self.speex, "run", return_value=-1),
              patch.object(self.speex, "destroy", wraps=destroy) as release):
            with self.assertRaisesRegex(RuntimeError, "discard epoch"):
                run.replay(self.speex, [42], 160, "separate")
            self.assertEqual(release.call_count, 3)

    def test_empty_and_limiter_controls(self):
        self.assertEqual(run.replay(self.speex, [], 160, "common"), ([], [], 160))
        with patch.dict(run.VARIANTS, limited=((), True)):
            out, trace, _ = run.replay(self.speex, [-32768, 1000], 160, "limited")
        self.assertEqual(out, [-run.PEAK, 980])
        self.assertTrue(trace[0]["limited"])

    def test_pin_mismatch_fails_before_build(self):
        with (patch.object(run, "SOURCE_PIN", "mismatch"), patch.object(run.subprocess, "run") as compile_):
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                run.build(Path("."))
            compile_.assert_not_called()
