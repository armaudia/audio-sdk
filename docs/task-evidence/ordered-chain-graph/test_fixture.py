"""Acceptance tests for the model-free ordered-chain fixture.

All tests are local, offline and deterministic. The installed-fixture test
builds a byte-reproducible wheel with stdlib tools, installs it with pip and
runs an external consumer from a temporary working directory.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_wheel  # noqa: E402
import fixture as ref  # noqa: E402

RECIPE_FILE_DIGEST = "bcdc1e4a63dc8f84a76e52b8e749948d7d8aca63ac7ad80c625e8a2cf14a1ec2"
RECIPE_DIGEST = "554a4daef1e7db10bee334a9b90cf7331a42703a952ab3136b83318469676a85"
REPORT_DIGEST = "a496d36fdfaae4796ab620065d424e0c03c4738da47875f2b26b84b3c4c013aa"
WHEEL_DIGEST = "40fd7dac81f739189ab60d68877e8075ca5146ceb6a1513ed53a40789095cabb"
FIXTURE_SOURCE_DIGEST = "e35d055d2d9f8446781e8752f2c6bc61672b2c385e9a10d93bdc3fa24ec35859"
ORIGIN_NS = 1_000_000_000


def load_recipe():
    return json.loads((HERE / "recipe.json").read_text(encoding="ascii"))


def builtin_stages():
    stages = ref.builtin_available()
    stages.update({
        "third_party.gain.v0": ref.GainStage(),
        "third_party.limiter.v0": ref.LimiterStage(),
        "third_party.activity.v0": ref.ActivityStage(),
    })
    return stages


def validate(raw=None, stages=None):
    return ref.validate_recipe(load_recipe() if raw is None else raw,
                               builtin_stages() if stages is None else stages)


def frame(start, values, count, epoch=1, flags=0):
    samples = list(values[:count]) + [0.0] * (ref.FRAME_SAMPLES - count)
    return ref.Frame(tuple(samples), count, epoch, start, flags)


def full_frame(start, seed=0, flags=0, epoch=1):
    return frame(start, tuple((i + seed % 7) / 11 for i in range(ref.FRAME_SAMPLES)),
                 ref.FRAME_SAMPLES, epoch=epoch, flags=flags)


def two_stage_recipe(order=("gain", "limiter"), costs=(1000, 2000)):
    definitions = {
        "gain": ("fixture.gain.v0", {"gain": 0.5}),
        "limiter": ("fixture.limiter.v0", {"peak": 0.25}),
    }
    nodes = []
    for index, node_id in enumerate(order):
        provider, settings = definitions[node_id]
        nodes.append({
            "id": node_id, "provider_id": provider, "role": "audio",
            "delay_samples": 0, "availability_cost_ns": costs[index],
            "settings": settings,
            "depends_on": [order[index - 1]] if index else [],
            "input_port": "pcm.in" if index == 0 else f"pcm.{order[index - 1]}.out",
            "output_port": f"pcm.{node_id}.out",
        })
    return {
        "schema_id": ref.CONTRACT_ID,
        "recipe_id": "two.stage.probe.v1",
        "contract_version": ref.CONTRACT_VERSION,
        "engine": ref.ENGINE,
        "format": {"sample_rate_hz": 16000, "channels": 1,
                   "sample_format": "f32", "frame_samples": 160},
        "audio_path": list(order),
        "nodes": nodes,
    }


def standard_run():
    recipe, status, _ = validate()
    assert status is ref.Status.OK
    executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
    for first, values, count, flags in (
        (0, tuple((i % 11) / 11 for i in range(160)), 160, 0),
        (160, tuple(((i + 3) % 13) / 13 for i in range(160)), 160, 0),
        (320, (0.5, -0.25, 0.75, 0.0, 1.0), 5, ref.FINAL_INPUT),
    ):
        result = executor.process(frame(first, values, count, flags=flags))
        assert result.lease is not None
        assert executor.release(result.lease.lease_id) is ref.Status.OK
    assert executor.begin_drain() is ref.Status.OK
    assert executor.drain_next().status is ref.Status.END_OF_STREAM
    return recipe, executor


class StaleEventStage(ref.Stage):
    role = "analysis"

    def transform(self, samples, settings, ctx):
        return tuple(samples), ({
            "source_start": max(0, int(ctx["source_first"])),
            "source_end": int(ctx["source_first"]) + 160,
            "value": 0.5,
            "validity": "known",
            "available_ns": int(ctx["availability_ns"]),
            "epoch": int(ctx["epoch"]) - 1,
        },)


class OrderedChainFixtureTest(unittest.TestCase):
    def test_artifacts_are_valid_json_with_pinned_identities(self):
        contract = json.loads((HERE / "contract.json").read_text(encoding="ascii"))
        schema = json.loads((HERE / "recipe.schema.json").read_text(encoding="ascii"))
        raw = load_recipe()
        self.assertEqual(contract["schema_id"], ref.CONTRACT_ID)
        self.assertEqual(schema["$id"], ref.CONTRACT_ID)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["additionalProperties"], False)
        self.assertEqual(
            hashlib.sha256((HERE / "recipe.json").read_bytes()).hexdigest(),
            RECIPE_FILE_DIGEST,
        )
        self.assertEqual(hashlib.sha256(ref.canonical_bytes(raw)).hexdigest(), RECIPE_DIGEST)

    def test_recipe_identity_is_frozen(self):
        recipe, status, reason = validate()
        self.assertEqual((status, reason), (ref.Status.OK, ""))
        self.assertEqual(recipe.digest, RECIPE_DIGEST)
        self.assertEqual(recipe.digest, ref.recipe_digest(load_recipe()))
        changed = load_recipe()
        changed["audio_path"] = ["limiter", "delay", "gain"]
        self.assertNotEqual(ref.recipe_digest(changed), RECIPE_DIGEST)
        changed = load_recipe()
        changed["nodes"][1]["availability_cost_ns"] += 1
        self.assertNotEqual(ref.recipe_digest(changed), RECIPE_DIGEST)
        changed = load_recipe()
        changed["nodes"][0]["settings"]["gain"] = 0.6
        self.assertNotEqual(ref.recipe_digest(changed), RECIPE_DIGEST)
        changed = load_recipe()
        changed["unexpected"] = True
        self.assertEqual(validate(changed)[1], ref.Status.REJECTED_BAD_SHAPE)

    def test_cycles_are_rejected(self):
        cycle = load_recipe()
        cycle["nodes"][0]["depends_on"] = ["limiter"]
        self.assertEqual(validate(cycle)[1], ref.Status.REJECTED_CYCLE)
        self_cycle = load_recipe()
        self_cycle["nodes"][0]["depends_on"] = ["gain"]
        self.assertEqual(validate(self_cycle)[1], ref.Status.REJECTED_CYCLE)

    def test_unavailable_stage_and_metadata_mismatch_rejected(self):
        stages = builtin_stages()
        del stages["third_party.limiter.v0"]
        self.assertEqual(validate(stages=stages)[1], ref.Status.REJECTED_UNAVAILABLE_STAGE)
        mismatch = load_recipe()
        mismatch["nodes"][1]["delay_samples"] = 81
        self.assertEqual(validate(mismatch)[1], ref.Status.REJECTED_BAD_SHAPE)

    def test_ambiguous_and_unknown_ports_rejected(self):
        duplicate = load_recipe()
        duplicate["nodes"][2]["output_port"] = "pcm.delay.out"
        self.assertEqual(validate(duplicate)[1], ref.Status.REJECTED_AMBIGUOUS_PORT)
        rewired = load_recipe()
        rewired["nodes"][1]["input_port"] = "pcm.wrong.out"
        self.assertEqual(validate(rewired)[1], ref.Status.REJECTED_AMBIGUOUS_PORT)
        unknown_tap = load_recipe()
        unknown_tap["nodes"][3]["tap_port"] = "pcm.missing.out"
        self.assertEqual(validate(unknown_tap)[1], ref.Status.REJECTED_UNKNOWN_PORT)

    def test_missing_nonfinite_and_bad_shape_controls_rejected(self):
        missing = load_recipe()
        del missing["engine"]
        self.assertEqual(validate(missing)[1], ref.Status.REJECTED_BAD_SHAPE)
        nonfinite = load_recipe()
        nonfinite["nodes"][0]["settings"]["gain"] = float("nan")
        self.assertEqual(validate(nonfinite)[1], ref.Status.REJECTED_NONFINITE)
        non_ascii = load_recipe()
        non_ascii["nodes"][0]["settings"]["é"] = 1
        self.assertEqual(validate(non_ascii)[1], ref.Status.REJECTED_NONFINITE)

    def test_stage_order_distinct_from_delay_and_availability(self):
        recipe_a, status_a, _ = validate(two_stage_recipe(("gain", "limiter"), (1000, 2000)))
        recipe_b, status_b, _ = validate(two_stage_recipe(("limiter", "gain"), (1000, 2000)))
        self.assertEqual((status_a, status_b), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(recipe_a.total_delay, recipe_b.total_delay)
        self.assertEqual(recipe_a.audio_cost_ns, recipe_b.audio_cost_ns)
        results = []
        for recipe in (recipe_a, recipe_b):
            executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
            result = executor.process(frame(0, (1.0,) * ref.FRAME_SAMPLES, ref.FRAME_SAMPLES))
            self.assertIsNotNone(result.lease)
            results.append(result.lease)
            executor.release(result.lease.lease_id)
        self.assertNotEqual(results[0].stage_order, results[1].stage_order)
        self.assertNotEqual(results[0].samples[0], results[1].samples[0])
        self.assertEqual(results[0].samples[0], 0.25)
        self.assertEqual(results[1].samples[0], 0.125)
        self.assertEqual(results[0].availability_ns, results[1].availability_ns)
        self.assertEqual(results[0].availability_ns, ORIGIN_NS + 3000)

    def test_delay_distinct_from_availability(self):
        base = load_recipe()
        wide = copy.deepcopy(base)
        wide["nodes"][1]["delay_samples"] = 100
        wide["nodes"][1]["settings"]["delay_samples"] = 100
        observations = []
        for raw in (base, wide):
            recipe, status, _ = validate(raw)
            self.assertEqual(status, ref.Status.OK)
            executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
            result = executor.process(full_frame(0))
            self.assertIsNotNone(result.lease)
            observations.append((recipe.total_delay, result.lease.valid_offset,
                                 result.lease.availability_ns, recipe.analysis_cost_ns))
            executor.release(result.lease.lease_id)
        self.assertEqual(observations[0][0], 80)
        self.assertEqual(observations[1][0], 100)
        self.assertEqual(observations[0][1], 80)
        self.assertEqual(observations[1][1], 100)
        self.assertEqual(observations[0][2], observations[1][2])
        self.assertEqual(observations[0][2], ORIGIN_NS + 675000)
        self.assertEqual(observations[0][3], 40000)

    def test_partial_frame_conservation_and_input_controls(self):
        recipe, _, _ = validate()
        executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
        expected = [(-80, 80, 80), (80, 0, 160), (240, 0, 85)]
        inputs = [
            full_frame(0),
            full_frame(160, 3),
            frame(320, (0.5, -0.25, 0.75, 0.0, 1.0), 5, flags=ref.FINAL_INPUT),
        ]
        for index, incoming in enumerate(inputs):
            result = executor.process(incoming)
            self.assertEqual(result.status, ref.Status.OK)
            lease = result.lease
            self.assertIsNotNone(lease)
            observed = (lease.source_first_sample, lease.valid_offset, lease.valid_count)
            self.assertEqual(observed, expected[index])
            self.assertEqual(executor.release(lease.lease_id), ref.Status.OK)
        self.assertEqual(executor.valid_intervals, [(0, 80), (80, 240), (240, 325)])
        self.assertEqual(executor.counters["delivered_valid_samples"], 325)

        self.assertEqual(executor.process(full_frame(480)).status, ref.Status.REJECTED_BAD_FRAME)
        bad_epoch = frame(480, (1.0,) * 160, 160, epoch=2)
        self.assertEqual(executor.process(bad_epoch).status, ref.Status.REJECTED_STALE_EPOCH)
        values = [1.0] * 160
        values[10] = float("nan")
        self.assertEqual(executor.process(frame(480, values, 160)).status,
                         ref.Status.REJECTED_BAD_FRAME)

        fresh, _, _ = validate()
        ex = ref.SequentialExecutor(fresh, builtin_stages())
        nonfinite = frame(0, [float("inf")] + [0.0] * 159, 160)
        self.assertEqual(ex.process(nonfinite).status, ref.Status.REJECTED_NONFINITE_INPUT)
        padded = frame(0, [1.0] * 160, 5)
        padded = ref.Frame(tuple([1.0] * 5 + [0.9] * 155), 5, 1, 0, 0)
        self.assertEqual(ex.process(padded).status, ref.Status.REJECTED_BAD_PADDING)
        wrong_flags = ref.Frame(tuple([0.0] * 160), 160, 1, 0, 2)
        self.assertEqual(ex.process(wrong_flags).status, ref.Status.REJECTED_BAD_FRAME)

    def test_outstanding_lease_blocks_next_process(self):
        recipe, _, _ = validate()
        executor = ref.SequentialExecutor(recipe, builtin_stages())
        result = executor.process(full_frame(0))
        self.assertIsNotNone(result.lease)
        self.assertEqual(executor.process(full_frame(160)).status, ref.Status.REJECTED_BUSY)
        self.assertEqual(executor.release(result.lease.lease_id), ref.Status.OK)

    def test_drain_releases_tail_then_eos_and_cap_control(self):
        delayed = load_recipe()
        delayed["nodes"][1]["delay_samples"] = 160
        delayed["nodes"][1]["settings"]["delay_samples"] = 160
        recipe, status, _ = validate(delayed)
        self.assertEqual(status, ref.Status.OK)
        executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
        for index, start in enumerate((0, 160)):
            flags = ref.FINAL_INPUT if index == 1 else 0
            result = executor.process(full_frame(start, flags=flags))
            self.assertEqual(result.status, ref.Status.OK)
            self.assertEqual(executor.release(result.lease.lease_id), ref.Status.OK)
        self.assertEqual(executor.begin_drain(), ref.Status.OK)
        tail = executor.drain_next()
        self.assertEqual(tail.status, ref.Status.OK)
        self.assertIsNotNone(tail.lease)
        self.assertEqual(tail.lease.source_first_sample, 160)
        self.assertEqual(tail.lease.valid_count, 160)
        self.assertEqual(executor.release(tail.lease.lease_id), ref.Status.OK)
        self.assertEqual(executor.drain_next().status, ref.Status.END_OF_STREAM)
        self.assertEqual(executor.drain_next().status, ref.Status.END_OF_STREAM)

        long_delay = load_recipe()
        long_delay["nodes"][1]["delay_samples"] = 480
        long_delay["nodes"][1]["settings"]["delay_samples"] = 480
        capped_recipe, status, _ = validate(long_delay)
        self.assertEqual(status, ref.Status.OK)
        capped = ref.SequentialExecutor(capped_recipe, builtin_stages(), max_drain_calls=1)
        result = capped.process(full_frame(0, flags=ref.FINAL_INPUT))
        self.assertEqual(result.status, ref.Status.OK)
        self.assertEqual(capped.release(result.lease.lease_id), ref.Status.OK)
        self.assertEqual(capped.begin_drain(), ref.Status.OK)
        first_drain = capped.drain_next()
        self.assertEqual(first_drain.status, ref.Status.OK)
        self.assertEqual(capped.release(first_drain.lease.lease_id), ref.Status.OK)
        self.assertEqual(capped.drain_next().status, ref.Status.REJECTED_DRAIN_CAP)

    def test_reset_requires_higher_epoch_and_clears_side_state(self):
        recipe, _, _ = validate()
        executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
        result = executor.process(full_frame(0))
        self.assertEqual(executor.reset(1, 0), ref.Status.REJECTED_STALE_EPOCH)
        self.assertEqual(executor.reset(2, 0), ref.Status.REJECTED_BUSY)
        self.assertEqual(executor.release(result.lease.lease_id), ref.Status.OK)
        self.assertEqual(executor.hold_last["pcm.gain.out"], 0.75)
        record = executor.cancel("reset_preparation")
        self.assertEqual(record.reason, "reset_preparation")
        self.assertEqual(executor.reset(2, 0), ref.Status.OK)
        self.assertEqual(executor.hold_last["pcm.gain.out"], None)
        self.assertEqual(executor.events, [])
        restarted = executor.process(full_frame(0, epoch=2))
        self.assertEqual(restarted.status, ref.Status.OK)
        self.assertEqual(executor.release(restarted.lease.lease_id), ref.Status.OK)
        self.assertEqual(executor.process(frame(160, (0.0,) * 160, 160, epoch=1)).status,
                         ref.Status.REJECTED_STALE_EPOCH)

    def test_cancellation_records_abandoned_interval_and_blocks_reuse(self):
        recipe, _, _ = validate()
        executor = ref.SequentialExecutor(recipe, builtin_stages())
        result = executor.process(full_frame(0))
        self.assertIsNotNone(result.lease)
        record = executor.cancel("caller_cancel")
        self.assertEqual(record.lease_id, result.lease.lease_id)
        self.assertEqual((record.abandoned_start, record.abandoned_end), (-80, 80))
        self.assertEqual(record.abandoned_valid_samples, 80)
        self.assertEqual(executor.process(full_frame(160)).status, ref.Status.REJECTED_CANCELLED)
        self.assertEqual(executor.begin_drain(), ref.Status.REJECTED_CANCELLED)
        self.assertEqual(executor.drain_next().status, ref.Status.REJECTED_CANCELLED)
        self.assertEqual(executor.reset(2, 0), ref.Status.OK)
        self.assertEqual(executor.counters["rejected_frames"], 0)
        self.assertEqual(len(executor.cancellations), 1)

    def test_hold_last_unknown_nonfinite_and_stale_side_events(self):
        recipe, _, _ = validate()
        executor = ref.SequentialExecutor(recipe, builtin_stages(), stream_origin_ns=ORIGIN_NS)
        for start in (0, 160, 320, 480):
            result = executor.process(full_frame(start))
            self.assertEqual(result.status, ref.Status.OK)
            self.assertEqual(executor.release(result.lease.lease_id), ref.Status.OK)
        statuses = [event.status for event in executor.events]
        self.assertEqual(statuses, [
            ref.Status.OK.value, ref.Status.OK.value, ref.Status.REJECTED_INVALID_EVENT.value,
        ])
        self.assertEqual([event.validity for event in executor.events],
                         ["known", "unknown", "known"])
        self.assertEqual(executor.hold_last["pcm.gain.out"], 0.75)
        self.assertIsNone(executor.events[2].value)
        self.assertEqual(executor.counters["known_events"], 1)
        self.assertEqual(executor.counters["unknown_events"], 1)
        self.assertEqual(executor.counters["invalid_events"], 1)

        stale_recipe = copy.deepcopy(load_recipe())
        stale_recipe["nodes"][3]["provider_id"] = "fixture.stale.v0"
        stages = builtin_stages()
        stages["fixture.stale.v0"] = StaleEventStage()
        parsed, status, _ = ref.validate_recipe(stale_recipe, stages)
        self.assertEqual(status, ref.Status.OK)
        stale_executor = ref.SequentialExecutor(parsed, stages, stream_origin_ns=ORIGIN_NS)
        result = stale_executor.process(full_frame(0))
        self.assertEqual(stale_executor.counters["stale_events"], 1)
        self.assertEqual(stale_executor.hold_last["pcm.gain.out"], None)
        self.assertEqual(result.lease.events[0].status, ref.Status.REJECTED_STALE_EVENT.value)
        self.assertEqual(stale_executor.release(result.lease.lease_id), ref.Status.OK)
        self.assertEqual(stale_executor.reset(2, 0), ref.Status.OK)
        self.assertEqual(stale_executor.process(frame(0, (0.0,) * 160, 160, epoch=1)).status,
                         ref.Status.REJECTED_STALE_EPOCH)

    def test_failing_port_is_explicit_and_requires_reset(self):
        raw = two_stage_recipe(("gain",))
        raw["recipe_id"] = "failing.port.v1"
        raw["nodes"][0]["provider_id"] = "fixture.failing.v0"
        raw["nodes"][0]["settings"] = {"fail_at_frame": 1, "reason": "control_failure"}
        stages = builtin_stages()
        recipe, status, _ = ref.validate_recipe(raw, stages)
        self.assertEqual(status, ref.Status.OK)
        executor = ref.SequentialExecutor(recipe, stages)
        first = executor.process(full_frame(0))
        self.assertEqual(first.status, ref.Status.OK)
        self.assertEqual(executor.release(first.lease.lease_id), ref.Status.OK)
        failed = executor.process(full_frame(160))
        self.assertEqual(failed.status, ref.Status.REJECTED_FAILING_PORT)
        self.assertEqual(failed.failed_interval, (160, 320))
        self.assertEqual(failed.port, "pcm.gain.out")
        self.assertEqual(executor.failed_ports[0]["reason"], "control_failure")
        self.assertEqual(executor.process(full_frame(320)).status, ref.Status.REJECTED_NEEDS_RESET)
        self.assertEqual(executor.reset(2, 0), ref.Status.OK)

    def test_canonical_report_digest_is_stable(self):
        first_recipe, first_executor = standard_run()
        second_recipe, second_executor = standard_run()
        text_a, digest_a = ref.canonical_report(first_recipe, first_executor, ref.Status.END_OF_STREAM)
        text_b, digest_b = ref.canonical_report(second_recipe, second_executor, ref.Status.END_OF_STREAM)
        self.assertEqual((text_a, digest_a), (text_b, digest_b))
        self.assertEqual(digest_a, REPORT_DIGEST)
        self.assertIn(ref.CONTRACT_ID, text_a)
        self.assertIn(RECIPE_DIGEST, text_a)
        self.assertNotIn("NaN", text_a)
        self.assertNotIn("Infinity", text_a)
        checked_in = (HERE / "report.json").read_text(encoding="ascii")
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii").strip()
        self.assertEqual(checked_in, text_a)
        self.assertEqual(sidecar, f"{digest_a}  report.json")
        self.assertEqual(hashlib.sha256(checked_in.encode("ascii")).hexdigest(), digest_a)

    def test_installed_external_fixture(self):
        with tempfile.TemporaryDirectory(prefix="sdk-graph-") as temp:
            root = Path(temp)
            dist_a = build_wheel.build_wheel(root / "dist-a")
            dist_b = build_wheel.build_wheel(root / "dist-b")
            self.assertEqual(dist_a.read_bytes(), dist_b.read_bytes())
            self.assertEqual(hashlib.sha256(dist_a.read_bytes()).hexdigest(), WHEEL_DIGEST)

            install = root / "install"
            pip = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps",
                 "--disable-pip-version-check", "--target", str(install), str(dist_a)],
                cwd=root, capture_output=True, text=True, timeout=180,
            )
            self.assertEqual(pip.returncode, 0, pip.stderr)
            probe = HERE / "third_party" / "consumer_probe.py"
            env = os.environ.copy()
            env.update({
                "PYTHONPATH": os.pathsep.join((str(install), str(HERE))),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            })
            outputs = []
            for _ in range(2):
                completed = subprocess.run(
                    [sys.executable, str(probe), str(install), str(HERE)],
                    cwd=root, env=env, capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                outputs.append(completed.stdout)
            self.assertEqual(outputs[0], outputs[1])
            record = json.loads(outputs[0])
            self.assertTrue(record["installed"])
            self.assertEqual(record["fixture_id"], "third-party/ordered-chain-fixture/0.1")
            self.assertEqual(record["fixture_source_digest"], FIXTURE_SOURCE_DIGEST)
            self.assertEqual(record["recipe_digest"], RECIPE_DIGEST)
            self.assertEqual(record["report_digest"], REPORT_DIGEST)


if __name__ == "__main__":
    unittest.main()
