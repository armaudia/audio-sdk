import unittest

from fixture import (
    CONTRACT_ID,
    DuplexSession,
    Layout,
    ReferenceTrace,
    Status,
    TraceSegment,
    canonical_report,
    mono_trace,
)


def impulse(length, at, value=1.0):
    values = [0.0] * length
    values[at] = value
    return values


class DuplexFixtureTest(unittest.TestCase):
    def test_known_impulses_align_after_resampling(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1),
                                render_rate_hz=48000)
        self.assertEqual(session.submit(
            mono_trace("render", impulse(1440, 960), rate_hz=48000)), Status.OK)
        self.assertEqual(session.submit(
            mono_trace("capture", impulse(480, 320))), Status.OK)
        render = session.frame("render", 2)
        capture = session.frame("capture", 2)
        self.assertEqual(render[0], (Status.OK,))
        self.assertEqual(capture[0], (Status.OK,))
        self.assertEqual(render[1][0][0], 1.0)
        self.assertEqual(capture[1][0][0], 1.0)

    def test_declared_drift_maps_known_impulse(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1),
                                max_drift_ppm=10000)
        self.assertEqual(session.submit(mono_trace("render", [0.0] * 480)), Status.OK)
        self.assertEqual(session.submit(mono_trace(
            "capture", impulse(490, 322, 0.75), drift_ppm=6250)), Status.OK)
        result = session.frame("capture", 2)
        self.assertEqual(result[1][0][0], 0.75)
        negative = DuplexSession(Layout("mono", 1), Layout("mono", 1),
                                 max_drift_ppm=2000000)
        negative.submit(mono_trace("capture", [0.0] * 480,
                                   drift_ppm=-2000000))
        self.assertEqual(negative.frame("capture", 1), Status.REJECTED_GAP)

    def test_missing_reference_is_explicit(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1))
        session.submit(mono_trace("render", [0.0] * 480))
        self.assertEqual(session.frame("capture", 0), Status.REJECTED_MISSING)

    def test_gap_and_overlap_are_rejected_without_interpolation(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1))
        gapped = ReferenceTrace(
            "capture", Layout("mono", 1), 16000,
            (TraceSegment(0, ((0.0,) * 160,)),
             TraceSegment(200, ((1.0,) * 160,))))
        overlapping = ReferenceTrace(
            "capture", Layout("mono", 1), 16000,
            (TraceSegment(0, ((0.0,) * 160,)),
             TraceSegment(100, ((1.0,) * 160,))))
        empty = ReferenceTrace("capture", Layout("mono", 1), 16000,
                               (TraceSegment(0, ()),))
        self.assertEqual(session.submit(gapped), Status.REJECTED_GAP)
        self.assertEqual(session.submit(overlapping), Status.REJECTED_GAP)
        self.assertEqual(session.submit(empty), Status.REJECTED_GAP)
        self.assertEqual(session.frame("capture", 0), Status.REJECTED_MISSING)

    def test_layout_and_rate_mismatch_are_rejected(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1))
        stereo = ReferenceTrace(
            "capture", Layout("stereo_interleaved", 2), 16000,
            (TraceSegment(0, ((0.0,) * 160, (0.0,) * 160)),))
        wrong_rate = mono_trace("capture", [0.0] * 480, rate_hz=48000)
        self.assertEqual(session.submit(stereo), Status.REJECTED_LAYOUT)
        self.assertEqual(session.submit(wrong_rate), Status.REJECTED_RATE)

    def test_multichannel_trace_keeps_channel_order(self):
        left = impulse(320, 160, 0.25)
        right = impulse(320, 160, 0.75)
        trace = ReferenceTrace(
            "capture", Layout("stereo_interleaved", 2), 16000,
            (TraceSegment(0, (tuple(left), tuple(right))),))
        session = DuplexSession(Layout("stereo_interleaved", 2),
                                Layout("stereo_interleaved", 2))
        self.assertEqual(session.submit(trace), Status.OK)
        result = session.frame("capture", 1)
        self.assertEqual((result[1][0][0], result[1][1][0]), (0.25, 0.75))

    def test_teardown_is_idempotent_and_closes_admission(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1))
        session.submit(mono_trace("render", [0.0] * 160))
        session.close()
        session.close()
        self.assertEqual(session.submit(mono_trace("render", [0.0] * 160)), Status.CLOSED)
        self.assertEqual(session.frame("render", 0), Status.CLOSED)
        self.assertEqual(session._traces, {})

    def test_report_is_canonical_and_versioned(self):
        session = DuplexSession(Layout("mono", 1), Layout("mono", 1))
        session.submit(mono_trace("render", [0.0] * 160))
        result = session.frame("render", 0)
        report = canonical_report(session, {"render": result[1]})
        self.assertEqual(report, canonical_report(session, {"render": result[1]}))
        self.assertIn(CONTRACT_ID, report[0])
        self.assertEqual(len(report[1]), 64)


if __name__ == "__main__":
    unittest.main()
