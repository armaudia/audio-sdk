import unittest

from fixture import (
    CONTRACT_ID,
    ElasticStream,
    PcmChunk,
    Status,
    canonical_report,
    make_block,
)


def chunk(start, values):
    return PcmChunk(start, tuple(values))


class ElasticFixtureTest(unittest.TestCase):
    def test_identity_with_variable_frame_counts(self):
        stream = ElasticStream("a")
        self.assertEqual(stream.push(chunk(0, [0.1] * 80)), Status.OK)
        self.assertEqual(stream.push(chunk(80, [0.2] * 160)), Status.OK)
        self.assertEqual(stream.push(chunk(240, [0.3] * 240)), Status.OK)
        result = stream.pull(1024)
        self.assertEqual(result.status, Status.OK)
        self.assertEqual(result.samples, (0.1,) * 80 + (0.2,) * 160 + (0.3,) * 240)
        self.assertEqual(result.source_indices, tuple(range(480)))
        self.assertEqual((result.consumed_count, result.produced_count), (480, 480))

    def test_ratio_update_affects_only_later_chunks(self):
        stream = ElasticStream("ratio")
        stream.push(chunk(0, [1.0] * 160))
        self.assertEqual(stream.set_ratio("2"), Status.OK)
        stream.push(chunk(160, [2.0] * 160))
        result = stream.pull(1024)
        self.assertEqual(result.status, Status.OK)
        self.assertEqual(result.source_indices[:160], tuple(range(160)))
        self.assertEqual(result.source_indices[160:], tuple(range(160, 320, 2)))
        self.assertEqual(list(result.source_indices), sorted(result.source_indices))
        self.assertEqual((result.consumed_count, result.produced_count), (320, 240))
        self.assertEqual(stream.ratio, 2)

    def test_invalid_ratio_and_source_gap_are_rejected(self):
        stream = ElasticStream("negative")
        self.assertEqual(stream.set_ratio("0"), Status.REJECTED_RATIO)
        self.assertEqual(stream.set_ratio("abc"), Status.REJECTED_RATIO)
        self.assertEqual(stream.ratio, 1)
        self.assertEqual(stream.push(chunk(10, [0.0] * 10)), Status.REJECTED_SOURCE_GAP)
        self.assertEqual(stream.consumed_count, 0)

    def test_bounded_buffering_rejects_new_input_without_drop(self):
        stream = ElasticStream("bounded", max_queued_samples=160)
        self.assertEqual(stream.push(chunk(0, [1.0] * 160)), Status.OK)
        rejected = stream.push(chunk(160, [2.0] * 160))
        self.assertEqual(rejected, Status.REJECTED_BACKPRESSURE)
        self.assertEqual((stream.consumed_count, stream.available_output), (160, 160))
        self.assertEqual(stream.pull(160).status, Status.OK)
        self.assertEqual(stream.push(chunk(160, [2.0] * 160)), Status.OK)

    def test_finite_flush_and_end_of_stream(self):
        stream = ElasticStream("slow", ratio="0.5")
        stream.push(chunk(0, [0.25] * 160))
        self.assertEqual(stream.flush(), Status.OK)
        first = stream.pull(200)
        second = stream.pull(200)
        self.assertEqual((len(first.samples), len(second.samples)), (200, 120))
        self.assertEqual(first.source_indices[1], 0)
        self.assertEqual(first.source_indices[2], 1)
        self.assertEqual(second.source_indices[-1], 159)
        self.assertEqual(stream.pull(10).status, Status.END_OF_STREAM)
        self.assertEqual(stream.produced_count, 320)

    def test_streams_are_independent(self):
        fast = ElasticStream("fast", ratio="2")
        normal = ElasticStream("normal")
        fast.push(chunk(0, [1.0] * 160))
        normal.push(chunk(0, [2.0] * 160))
        fast_result = fast.pull(1024)
        normal_result = normal.pull(1024)
        self.assertEqual((len(fast_result.samples), len(normal_result.samples)), (80, 160))
        self.assertEqual(fast_result.samples, (1.0,) * 80)
        self.assertEqual(normal_result.samples, (2.0,) * 160)

    def test_packet_fec_recovers_one_erasure_and_rejects_burst(self):
        status, block = make_block(1, 10,
                                   [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]],
                                   0)
        self.assertEqual(status, Status.OK)
        self.assertEqual(block.parity.payload, (8, 4, 0))
        recovered_status, recovered = block.recover([12])
        self.assertEqual(recovered_status, Status.OK)
        self.assertEqual((recovered[0].seq, recovered[0].timestamp_ns), (12, 2 * 62500))
        self.assertEqual(recovered[0].payload, (7, 8, 9))
        burst_status, burst = block.recover([12, 13])
        self.assertEqual(burst_status, Status.REJECTED_UNRECOVERABLE)
        self.assertEqual(burst, ())
        wrong_status, wrong = block.recover([99])
        self.assertEqual(wrong_status, Status.REJECTED_PACKET)
        self.assertEqual(wrong, ())

    def test_packet_and_pcm_boundaries_stay_separate(self):
        stream = ElasticStream("separate")
        status, block = make_block(2, 0, [[255, 1]], 0)
        self.assertEqual(status, Status.OK)
        recovered_status, recovered = block.recover([0])
        self.assertEqual(recovered_status, Status.OK)
        self.assertEqual(block.packets[0].payload, (255, 1))
        self.assertEqual(stream.available_output, 0)
        self.assertEqual(stream.consumed_count, 0)

    def test_report_is_canonical_and_versioned(self):
        stream = ElasticStream("report")
        stream.push(chunk(0, [0.5] * 160))
        result = stream.pull(160)
        report = canonical_report(stream, result, ())
        self.assertEqual(report, canonical_report(stream, result, ()))
        self.assertIn(CONTRACT_ID, report[0])
        self.assertEqual(len(report[1]), 64)


if __name__ == "__main__":
    unittest.main()
