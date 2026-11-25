import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from replay import parse_trace, replay


HERE = Path(__file__).resolve().parent
CAPTURE = json.loads((HERE / "capture.json").read_text())
RENDER = json.loads((HERE / "render.json").read_text())


def run(capture=CAPTURE, render=RENDER):
    return replay(parse_trace(capture), None if render is None else parse_trace(render))


class ReplayTest(unittest.TestCase):
    def test_variable_capture_slices_and_independent_clock_alignment(self):
        report = run()
        frames = report["frames"]
        self.assertEqual([row["status"] for row in frames], ["paired"] * 3)
        self.assertEqual([row["capture_interval"] for row in frames],
                         [["0", "480"], ["480", "960"], ["960", "1440"]])
        self.assertEqual([row["capture_ready_ns"] for row in frames], ["31000000", "52000000", "52000000"])
        self.assertEqual(report["capture_tail_samples"], 73)
        first = Fraction(60003, 250000)  # 5 us phase at 48,002.4 samples/s
        last = first + 1439 * Fraction(20001, 19999)
        self.assertEqual(Fraction(frames[0]["render_positions"][0]), first)
        self.assertEqual(Fraction(frames[-1]["render_positions"][1]), last)
        expected = "\n".join(str((first + i * Fraction(20001, 19999) - 1024) / 1024)
                             for i in range(480))
        self.assertEqual(frames[0]["reference_sha256"], hashlib.sha256(expected.encode("ascii")).hexdigest())
        nominal = run(render=dict(RENDER, rate_ppm=-50))["frames"]
        self.assertNotEqual(nominal[-1]["reference_sha256"], frames[-1]["reference_sha256"])

    def test_late_reference_never_patches_an_earlier_capture_frame(self):
        render = copy.deepcopy(RENDER)
        render["slices"][1][2] = 31_000_001
        frames = run(render=render)["frames"]
        self.assertEqual([row["status"] for row in frames], ["late_reference", "paired", "paired"])
        self.assertEqual(frames[0]["reference_ready_ns"], "31000001")
        self.assertNotIn("reference_sha256", frames[0])
        self.assertEqual(frames[1:], run()["frames"][1:])
        render["slices"][1][2] -= 1
        self.assertEqual(run(render=render)["frames"][0]["reference_sha256"],
                         run()["frames"][0]["reference_sha256"])

    def test_missing_reference_does_not_pad_or_clamp(self):
        for render in (None, dict(RENDER, slices=[])):
            frames = run(render=render)["frames"]
            self.assertEqual([row["status"] for row in frames], ["missing_reference"] * 3)
            self.assertTrue(all("reference_sha256" not in row for row in frames))
        frames = run(render=dict(RENDER, slices=RENDER["slices"][:2]))["frames"]
        self.assertEqual([row["status"] for row in frames], ["paired", "missing_reference", "missing_reference"])
        frames = run(render=dict(RENDER, origin_ns=5001))["frames"]
        self.assertEqual(frames[0]["status"], "missing_reference")
        self.assertTrue(all(row["status"] == "paired" for row in frames[1:]))

    def test_fractional_endpoint_requires_the_next_render_sample(self):
        render = dict(RENDER, slices=[[0, 480, 12_000_000, 0]])
        self.assertEqual(run(render=render)["frames"][0]["status"], "missing_reference")
        aligned_capture = dict(CAPTURE, origin_ns=20_000_000, rate_ppm=50)
        self.assertEqual(run(capture=aligned_capture, render=render)["frames"][0]["status"], "paired")

    def test_discontinuous_render_fails_closed(self):
        for column, value, reason in ((0, 192, "gap"), (0, 190, "overlap"),
                                      (3, 100_000, "timestamp_jump"), (3, -100_000, "timestamp_jump"),
                                      (2, 3_999_999, "arrival_regression")):
            with self.subTest(reason=reason, value=value):
                render = copy.deepcopy(RENDER)
                render["slices"][1][column] = value
                report = run(render=render)
                self.assertEqual(report["render_fault"], {"slice": 1, "reason": reason})
                self.assertTrue(all(row["status"] == "discontinuous_reference"
                                    and "reference_sha256" not in row for row in report["frames"]))

    def test_discontinuous_or_missing_capture_never_forms_a_frame(self):
        capture = copy.deepcopy(CAPTURE)
        capture["slices"][1][0] += 1
        report = run(capture=capture)
        self.assertEqual(report["frames"], [])
        self.assertEqual(report["capture_fault"], {"slice": 1, "reason": "gap"})
        report = run(capture=dict(CAPTURE, slices=[]))
        self.assertEqual(report["frames"], [])
        self.assertEqual(report["capture_fault"], {"reason": "missing_capture"})

    def test_bad_slice_bounds_and_types_are_rejected(self):
        for count in (0, 4097, True, 1.0):
            with self.subTest(count=count), self.assertRaises(ValueError):
                parse_trace(dict(CAPTURE, slices=[[0, count, 0, 0]]))
        parse_trace(dict(CAPTURE, slices=[[0, 4096, 0, 0]]))
        with self.assertRaises(ValueError):
            parse_trace(dict(RENDER, rate_ppm=1001))

    def test_cli_uses_caller_files_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            capture, render = path / "cap.json", path / "ref.json"
            capture.write_bytes((HERE / "capture.json").read_bytes())
            render.write_bytes((HERE / "render.json").read_bytes())
            cli = [sys.executable, "-B", str(HERE / "replay.py"), "--capture", str(capture)]
            both = [*cli, "--render", str(render)]
            matched = subprocess.check_output(both, cwd=path)
            self.assertEqual(matched, subprocess.check_output(both, cwd=path))
            self.assertEqual(hashlib.sha256(matched).hexdigest(),
                             "fea1bf7ed00768c515b2dd5bbc77dd6a640893148dbc3611e4609e3e6be473b2")
            omitted = json.loads(subprocess.check_output(cli, cwd=path))
            self.assertTrue(all(row["status"] == "missing_reference" for row in omitted["frames"]))
            for bad in (b"not json", b'{"slices": [], "slices": []}', b" " * 65_537, None):
                if bad is None:
                    render.unlink()
                else:
                    render.write_bytes(bad)
                result = subprocess.run(both, cwd=path, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"render trace:", result.stderr)


if __name__ == "__main__":
    unittest.main()
