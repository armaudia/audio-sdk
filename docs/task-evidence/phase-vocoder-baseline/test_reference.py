# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from reference import CAPACITY, OfflineComparison, Status, elastic
from run import render, verify_pins


class ComparisonTest(unittest.TestCase):
    def test_invalid_admissions_preserve_expected_source_cursor(self):
        stream = OfflineComparison("phase-vocoder")
        for chunk, rate, expected in (
            (None, "1", Status.REJECTED_SOURCE_GAP),
            (elastic.PcmChunk(0, ()), "1", Status.REJECTED_SOURCE_GAP),
            (elastic.PcmChunk(1, (0,)), "1", Status.REJECTED_SOURCE_GAP),
            (elastic.PcmChunk(0, (0,) * (CAPACITY + 1)), "1", Status.REJECTED_BACKPRESSURE),
            *((elastic.PcmChunk(0, (x,)), "1", Status.REJECTED_SOURCE_GAP)
              for x in (float("nan"), float("inf"), -float("inf"), 2, "bad")),
            *((elastic.PcmChunk(0, (0,)), rate, Status.REJECTED_RATIO)
              for rate in (None, float("nan"), "nan", "0", "1/0", "2", "-1")),
        ):
            with self.subTest(rate=rate, expected=expected):
                self.assertEqual(stream.push(chunk, rate), expected)
                self.assertEqual(stream.pull(160), elastic.PullResult(Status.NOT_READY, (), (), 0, 0))
        self.assertEqual(stream.push(elastic.PcmChunk(0, (0.25,)), "1"), Status.OK)
        self.assertEqual(stream.flush(), Status.OK)
        self.assertEqual(stream.pull(1).samples, (0.25,))
        self.assertEqual(stream.push(elastic.PcmChunk(1, (0,)), "1"), Status.CLOSED)
        for limit in (0, -1, False, None):
            with self.assertRaises(ValueError):
                stream.pull(limit)
        self.assertEqual(stream.pull(1).status, Status.END_OF_STREAM)

    def test_empty_and_subsample_eos(self):
        stream = OfflineComparison("phase-vocoder")
        self.assertEqual(stream.flush(), Status.OK)
        self.assertEqual(stream.pull(1), elastic.PullResult(Status.END_OF_STREAM, (), (), 0, 0))
        out, counts = render("phase-vocoder", (0.25,), [(1, "3/2")])
        self.assertEqual(out, [])
        self.assertEqual(counts["duration_error_samples"], "-2/3")

    def test_drain_accounting_for_awkward_regions(self):
        out, timing = render("phase-vocoder", (0.0,) * 483, [(161, "3/4"), (322, "5/4"), (483, "3/2")])
        self.assertEqual(out, [0.0] * 449)
        self.assertEqual(timing["duration_error_samples"], "-9/5")
        self.assertEqual(timing["final_pull_samples"], 129)

    def test_missing_input_or_evidence_is_not_a_pass(self):
        for samples, schedule in (((), [(1, "1")]), ((0.0,), []), ((0.0, 0.0), [(1, "1")])):
            with self.assertRaisesRegex(ValueError, "missing"):
                render("phase-vocoder", samples, schedule)
        with TemporaryDirectory() as root:
            with self.assertRaises(FileNotFoundError):
                verify_pins("EVIDENCE.sha256", Path(root))

    def test_bad_backend_result_closes_without_partial_output(self):
        for bad in ((), (float("nan"),), (float("inf"),), (1.01,)):
            with self.subTest(bad=bad):
                stream = OfflineComparison("phase-vocoder")
                chunk = elastic.PcmChunk
                self.assertEqual(stream.push(chunk(0, (0.25,)), "1"), Status.OK)
                self.assertEqual(stream.push(chunk(1, (0.25,)), "1"), Status.OK)
                with patch("reference.phase_vocoder", side_effect=[(0.25,), bad]):
                    with self.assertRaisesRegex(ValueError, "invalid render"):
                        stream.flush()
                self.assertEqual(stream.pull(1), elastic.PullResult(Status.CLOSED, (), (), 2, 0))
                self.assertEqual(stream.flush(), Status.CLOSED)
                self.assertEqual(stream.push(chunk(2, (0,)), "1"), Status.CLOSED)


if __name__ == "__main__":
    unittest.main()
