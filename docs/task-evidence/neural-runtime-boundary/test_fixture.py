import unittest

from fixture import (
    CONTRACT_ID,
    FRAME_SAMPLES,
    GRAPH,
    RUNTIME_IDS,
    STATE_SAMPLES,
    STREAMING,
    OFFLINE,
    AssetStub,
    ModelId,
    ModelRegistry,
    NeuralRunner,
    REQUIRED_HOOKS,
    RuntimeRegistry,
    Status,
    canonical_report,
    tensor_digest,
)

DIGEST = "a" * 64
REFERENCE_FRAME = tuple((index % 17) / 17 for index in range(FRAME_SAMPLES))
REFERENCE_OUTPUT_DIGEST = (
    "42990c3122a8873462194c3b89ee3194011cba38dc050edf480c3f442b8bd19e"
)


def model():
    return ModelId("stub.stream.v0", "0.1.0", DIGEST, GRAPH.digest)


def asset(provided=True, changed=False):
    provided_digest = DIGEST if provided and not changed else "b" * 64
    provided_bytes = 128 if provided else None
    return AssetStub("stub.weights.external", DIGEST, 128,
                     provided_digest if provided else None, provided_bytes)


def runner(mode=STREAMING, runtime=RUNTIME_IDS[0]):
    status, instance = NeuralRunner.create(model(), asset(), runtime, mode)
    assert status is Status.OK and instance is not None
    return instance


class NeuralFixtureTest(unittest.TestCase):
    def test_runtime_registry_loads_only_declared_stubs(self):
        registry = RuntimeRegistry()
        for runtime_id in RUNTIME_IDS:
            status, stub = registry.load(runtime_id)
            self.assertEqual(status, Status.OK)
            self.assertEqual(stub.hooks, REQUIRED_HOOKS)
        status, stub = registry.load("unlisted-runtime/0.1")
        self.assertEqual(status, Status.REJECTED_RUNTIME)
        self.assertIsNone(stub)

    def test_model_registry_rejects_changed_identity(self):
        registry = ModelRegistry()
        self.assertEqual(registry.register(model()), Status.OK)
        self.assertEqual(registry.register(model()), Status.OK)
        changed = ModelId("stub.stream.v0", "0.2.0", DIGEST, GRAPH.digest)
        self.assertEqual(registry.register(changed), Status.REJECTED_MODEL)
        bad_graph = ModelId("stub.bad.v0", "0.1.0", DIGEST, "c" * 64)
        self.assertEqual(registry.register(bad_graph), Status.REJECTED_MODEL)

    def test_missing_and_changed_assets_fail_before_tensor_calls(self):
        status, instance = NeuralRunner.create(model(), asset(provided=False),
                                               RUNTIME_IDS[0], STREAMING)
        self.assertEqual(status, Status.REJECTED_ASSET_MISSING)
        self.assertIsNone(instance)
        status, instance = NeuralRunner.create(model(), asset(changed=True),
                                               RUNTIME_IDS[0], STREAMING)
        self.assertEqual(status, Status.REJECTED_ASSET_CHANGED)
        self.assertIsNone(instance)

    def test_capability_query_freezes_shapes_and_hooks(self):
        capability = runner().capability_query()
        self.assertEqual(capability["hooks"], list(REQUIRED_HOOKS))
        self.assertEqual(capability["tensors"][0]["shape"], [1, FRAME_SAMPLES])
        self.assertEqual(capability["tensors"][1]["shape"], [1, STATE_SAMPLES])
        self.assertEqual(capability["state_length"], STATE_SAMPLES)

    def test_pinned_model_free_reference_is_exact(self):
        result = runner().run_stream(REFERENCE_FRAME)
        self.assertEqual(result.status, Status.OK)
        self.assertEqual(tensor_digest(result.samples), REFERENCE_OUTPUT_DIGEST)

    def test_streaming_state_is_fixed_size_finite_and_advances(self):
        instance = runner()
        result = instance.run_stream((0.0,) * FRAME_SAMPLES)
        self.assertEqual(result.status, Status.OK)
        self.assertEqual(len(result.state), STATE_SAMPLES)
        second = instance.run_stream((0.0,) * FRAME_SAMPLES)
        self.assertEqual(second.state[0], 2.0)
        bad = instance.run_stream((0.0,) * FRAME_SAMPLES,
                                  (float("nan"),) * STATE_SAMPLES)
        self.assertEqual(bad.status, Status.REJECTED_STATE)
        self.assertEqual(instance.state[0], 2.0)

    def test_tensor_shape_and_nonfinite_input_are_rejected(self):
        instance = runner()
        self.assertEqual(instance.run_stream((0.0,) * 159).status,
                         Status.REJECTED_TENSOR)
        self.assertEqual(instance.run_stream((float("inf"),) * FRAME_SAMPLES).status,
                         Status.REJECTED_TENSOR)

    def test_offline_and_streaming_entry_points_are_distinct(self):
        streaming = runner(STREAMING)
        offline = runner(OFFLINE)
        self.assertEqual(streaming.run_offline((0.0,) * 320).status,
                         Status.REJECTED_MODE)
        self.assertEqual(offline.run_stream((0.0,) * FRAME_SAMPLES).status,
                         Status.REJECTED_MODE)
        result = offline.run_offline((0.5,) * 320)
        self.assertEqual(result.status, Status.OK)
        self.assertEqual(result.entrypoint, OFFLINE)
        self.assertEqual(len(result.samples), 320)

    def test_hooks_reject_unsupported_modes_and_bad_history(self):
        instance = runner()
        self.assertEqual(instance.process_mode((0.0,) * FRAME_SAMPLES,
                                               "full").status, Status.OK)
        self.assertEqual(instance.process_mode((0.0,) * FRAME_SAMPLES,
                                               "cheap").status, Status.REJECTED_MODE)
        self.assertEqual(instance.resume_prepare((0.0,) * STATE_SAMPLES),
                         (Status.OK, 0))
        self.assertEqual(instance.resume_prepare((0.0,) * 8),
                         (Status.REJECTED_STATE, 0))

    def test_close_is_idempotent(self):
        instance = runner()
        instance.close()
        instance.close()
        self.assertEqual(instance.run_stream((0.0,) * FRAME_SAMPLES).status,
                         Status.CLOSED)
        self.assertEqual(instance.run_offline((0.0,) * 320).status, Status.CLOSED)
        self.assertEqual(instance.resume_prepare((0.0,) * STATE_SAMPLES)[0],
                         Status.CLOSED)

    def test_report_is_canonical_and_versioned(self):
        instance = runner()
        result = instance.run_stream(REFERENCE_FRAME)
        report = canonical_report(instance, result)
        self.assertEqual(report, canonical_report(instance, result))
        self.assertIn(CONTRACT_ID, report[0])
        self.assertEqual(len(report[1]), 64)


if __name__ == "__main__":
    unittest.main()
