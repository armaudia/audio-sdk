import ctypes
import unittest

from audio_sdk import Error, FRAME_SAMPLES, Frame, Registry, Result


class SDKTests(unittest.TestCase):
    def test_ctypes_layouts(self):
        self.assertEqual(ctypes.sizeof(ctypes.c_uint64), 8)
        self.assertEqual(Frame.first_input_sample.offset % 8, 0)
        self.assertEqual(Result.source_first_sample.offset % 8, 0)
        self.assertGreater(ctypes.sizeof(Error), ctypes.sizeof(Result))

    def test_switch_and_timing_metadata(self):
        registry = Registry()
        try:
            for provider, delay in (
                ("speex.ns.v0", 160),
                ("dsp.highpass80.v0", 0),
            ):
                with registry.session(provider) as session:
                    output, result = session.process([0.0] * FRAME_SAMPLES)
                    self.assertEqual(len(output), FRAME_SAMPLES)
                    self.assertEqual(result.source_first_sample, -delay)
                    self.assertEqual(result.produced_count, FRAME_SAMPLES)
                    self.assertEqual(result.epoch, 1)
        finally:
            registry.close()

    def test_reset_increments_epoch(self):
        registry = Registry()
        try:
            with registry.session("dsp.highpass80.v0") as session:
                session.reset(2, 123456)
                _, result = session.process([0.0] * FRAME_SAMPLES)
                self.assertEqual(result.epoch, 2)
                self.assertEqual(result.source_first_sample, 123456)
        finally:
            registry.close()

    def test_process_errors_and_finite_drain(self):
        registry = Registry()
        try:
            with registry.session("dsp.highpass80.v0") as session:
                with self.assertRaises(ValueError):
                    session.process([0.0] * (FRAME_SAMPLES - 1))
                output, result = session.process([0.25] * FRAME_SAMPLES)
                self.assertEqual(len(output), FRAME_SAMPLES)
                self.assertEqual(result.produced_count, FRAME_SAMPLES)
                drained = session.drain()
                self.assertLessEqual(len(drained), 2)
                self.assertTrue(all(r.produced_count <= FRAME_SAMPLES
                                    for _, r in drained))
                session.close()
                session.close()
        finally:
            registry.close()
            registry.close()


if __name__ == "__main__":
    unittest.main()
