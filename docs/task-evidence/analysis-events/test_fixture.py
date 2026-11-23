import unittest

from fixture import (
    CONTRACT_ID,
    AnalysisBus,
    AnalysisEvent,
    EventKind,
    Status,
    Validity,
    canonical_report,
    place_events,
    vad_accuracy,
)

DIGEST = "a" * 64
CLOCK = "monotonic-reference-v0"


def probability(event_id, epoch, start, end, value=0.5, validity=Validity.KNOWN):
    return AnalysisEvent(
        event_id=event_id,
        kind=EventKind.SPEECH_PROBABILITY,
        producer_id="speex-side-output.v0",
        tap_id="capture",
        epoch=epoch,
        source_start=start,
        source_end=end,
        value=value,
        validity=validity,
        available_ns=1000,
        availability_clock_id=CLOCK,
        config_digest=DIGEST,
        decision_resolution_samples=160,
        lookahead_samples=160,
    )


class AnalysisFixtureTest(unittest.TestCase):
    def test_cross_hop_placement_is_exact(self):
        event = probability("speech-1", 1, 150, 330)
        placed = place_events([event], total_samples=480)
        self.assertEqual(
            [(item.frame_index, item.overlap_samples) for item in placed["speech-1"]],
            [(0, 10), (1, 160), (2, 10)],
        )

    def test_stale_epoch_and_invalid_validity_are_rejected(self):
        bus = AnalysisBus(epoch=3, first_sample=320, audio=[0.0] * 480)
        self.assertEqual(bus.publish(probability("old", 2, 400, 480)),
                         Status.REJECTED_STALE_EPOCH)
        self.assertEqual(bus.publish(probability("before-start", 3, 100, 200)),
                         Status.REJECTED_STALE_EPOCH)
        self.assertEqual(bus.publish(probability("unknown", 3, 400, 480,
                                                 validity=Validity.UNKNOWN)),
                         Status.OK)
        self.assertEqual(bus.publish(probability("invalid", 3, 400, 480,
                                                 validity=Validity.INVALID)),
                         Status.REJECTED_INVALID_EVENT)
        self.assertEqual(bus.publish(AnalysisEvent(
            "bad-prob", EventKind.SPEECH_PROBABILITY, "p", "capture", 3,
            400, 480, 1.5, Validity.KNOWN, 1000, CLOCK, DIGEST)),
            Status.REJECTED_INVALID_EVENT)
        self.assertEqual([event.event_id for event in bus.events], ["unknown"])

    def test_availability_must_be_monotonic_per_clock(self):
        bus = AnalysisBus(1, 0, [0.0] * 480)
        self.assertEqual(bus.publish(probability("first", 1, 0, 160)), Status.OK)
        late = AnalysisEvent(
            "late", EventKind.SPEECH_PROBABILITY, "speex-side-output.v0",
            "capture", 1, 160, 320, 0.5, Validity.KNOWN, 999, CLOCK, DIGEST)
        self.assertEqual(bus.publish(late), Status.REJECTED_BAD_CLOCK)
        self.assertEqual([event.event_id for event in bus.events], ["first"])

    def test_analysis_never_mutates_audio(self):
        audio = [float(i % 7) / 7 for i in range(480)]
        bus = AnalysisBus(epoch=1, first_sample=0, audio=audio)
        before = (bus.audio_snapshot(), bus.audio_digest)
        bus.publish(probability("speech", 1, 150, 330))
        bus.publish(probability("rate", 1, 0, 160))
        self.assertEqual((bus.audio_snapshot(), bus.audio_digest), before)
        self.assertIsInstance(bus.audio_snapshot(), tuple)

    def test_vad_scores_only_fully_known_scored_regions(self):
        result = vad_accuracy(
            reference_speech=[(100, 220), (300, 400)],
            scored_regions=[(0, 480)],
            hypothesis=[(0, 160, False), (160, 320, True), (320, 480, False)],
            total_samples=480,
        )
        self.assertEqual(result.status, Status.OK)
        self.assertEqual((result.tp, result.fn, result.fp, result.tn),
                         (80, 140, 80, 180))
        self.assertAlmostEqual(result.speech_miss_rate, 7 / 11)
        self.assertAlmostEqual(result.false_alarm_rate, 4 / 13)
        self.assertEqual(result.unknown_samples, 0)

    def test_unknown_gaps_and_missing_hypothesis_are_rejected(self):
        missing = vad_accuracy([(100, 220)], [(0, 480)],
                               [(0, 160, False), (320, 480, False)], 480)
        self.assertEqual(missing.reason, "gap_or_outside_scored_region")
        self.assertIsNone(missing.speech_miss_rate)
        empty = vad_accuracy([(100, 220)], [(0, 480)], [], 480)
        self.assertEqual(empty.reason, "gap_or_outside_scored_region")
        unknown = vad_accuracy([(100, 220)], [(0, 160), (320, 480)],
                               [(0, 480, False)], 480)
        self.assertEqual(unknown.reason, "gap_or_outside_scored_region")
        self.assertEqual(unknown.unknown_samples, 160)

    def test_zero_denominators_are_null_with_reasons(self):
        no_speech = vad_accuracy([], [(0, 160)], [(0, 160, False)], 160)
        self.assertEqual((no_speech.tp, no_speech.fn), (0, 0))
        self.assertIsNone(no_speech.speech_miss_rate)
        self.assertEqual(no_speech.reason, "no_scored_speech")
        no_nonspeech = vad_accuracy([(0, 160)], [(0, 160)], [(0, 160, True)], 160)
        self.assertAlmostEqual(no_nonspeech.speech_miss_rate, 0.0)
        self.assertIsNone(no_nonspeech.false_alarm_rate)
        self.assertEqual(no_nonspeech.reason, "no_scored_nonspeech")

    def test_report_is_canonical_and_versioned(self):
        def make():
            bus = AnalysisBus(1, 0, [0.0] * 480)
            bus.publish(probability("speech", 1, 150, 330))
            result = vad_accuracy([(150, 330)], [(0, 480)],
                                  [(0, 480, False)], 480)
            return canonical_report(bus, result)

        text_a, hash_a = make()
        text_b, hash_b = make()
        self.assertEqual((text_a, hash_a), (text_b, hash_b))
        self.assertIn(CONTRACT_ID, text_a)
        self.assertEqual(len(hash_a), 64)


if __name__ == "__main__":
    unittest.main()
