"""Acceptance tests for the model-free engine_v1 fixture.

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

CONTRACT_FILE_DIGEST = "1e45f0b48696365264115a9c697b009c9e2b1c4db2158feca2b479732dd0db11"
DOMAIN_FILE_DIGEST = "80fdce8e8fdebd46b19861fee782769234f908856e44f49ca86c7f73d15d5895"
GRAPH_FILE_DIGEST = "47ad272c8f4911af3e99c17e5947775f590e72b02b513cfbaa7fa0dbee51ff75"
SCHEMA_FILE_DIGEST = "0aae8d60ad252cf24952c29ebb3cb40ae97efc853279b2a338c56f311bea8e0e"
DOMAIN_DIGEST = "190dbf721bd18295ec835a34a463cff4232dc1db209e848de320c8aa1518b9ef"
GRAPH_DIGEST = "91604256df7f75b72a20c3633a9cf775117a1882ab74be72fb895e6009db9f5f"
REPORT_DIGEST = "5bee590bd662aa09517ae9e6302e410ee6e55745894fcd2dacdf33fa19d4d724"
OUTPUT_DIGEST = "571ae035f4f5f2069b79ba5afa71d9620fadcf8b8b6b73fe3e375ffc9a8e7538"
WHEEL_DIGEST = "f440793f8bff3e1e0e658d03424a34aacdcdf1e831a5c8d15452830a02935807"
THIRD_PARTY_SOURCE_DIGEST = "8f84f364ad0ff962e61353e75bbecbb94a671b7808566f4d3e1a5df5cf5efa93"
FIXTURE_SOURCE = HERE / "third_party" / "src" / "engine_v1_fixture"
HOOKS_NONE = {"policy_query": False, "process_mode": False,
              "resume_prepare": False, "process_batch": False}
HOOKS_TRANSITION = {"policy_query": True, "process_mode": True,
                    "resume_prepare": True, "process_batch": False}
HOOKS_BATCH = {"policy_query": False, "process_mode": False,
               "resume_prepare": False, "process_batch": True}


def load_config():
    return json.loads((HERE / "domain.json").read_text(encoding="ascii"))


def load_graph():
    return json.loads((HERE / "graph.json").read_text(encoding="ascii"))


def make_domain(factories=None, config=None):
    return ref.Domain(load_config() if config is None else config, factories)


def admit(domain, raw=None, epoch=1, first=0, assets=None):
    return domain.admit(
        load_graph() if raw is None else raw,
        {"epoch": epoch, "first_input_sample": first,
         "assets": [] if assets is None else assets},
    )


def frame(start, values, count, epoch=1, flags=0):
    samples = list(values[:count]) + [0.0] * (ref.FRAME_SAMPLES - count)
    return ref.Frame(tuple(samples), count, epoch, start, flags)


def full_frame(start, seed=0, flags=0, epoch=1):
    return frame(start, tuple((i + seed % 7) / 11 for i in range(ref.FRAME_SAMPLES)),
                 ref.FRAME_SAMPLES, epoch=epoch, flags=flags)


def single_node_graph(provider_id, settings, graph_id="probe.graph.v1",
                      node_id="node", hooks=None, delay=0):
    return {
        "schema_id": ref.CONTRACT_ID,
        "graph_id": graph_id,
        "contract_version": ref.CONTRACT_VERSION,
        "engine": ref.ENGINE,
        "format": {"sample_rate_hz": 16000, "channels": 1,
                   "sample_format": "f32", "frame_samples": 160},
        "audio_path": [node_id],
        "nodes": [{
            "id": node_id,
            "provider_id": provider_id,
            "descriptor_digest": ref.descriptor_digest(provider_id),
            "role": "audio",
            "delay_samples": delay,
            "settings": settings,
            "depends_on": [],
            "input_port": "pcm.in",
            "output_port": "pcm.node.out",
            "hooks": HOOKS_NONE if hooks is None else hooks,
        }],
    }


def enqueue_and_step(domain, stream, incoming, deadline_ns=None):
    capture = domain.clock.origin_ns + (len(stream.sequence_ids) + 1) * ref.NS_PER_FRAME
    acceptance = stream.enqueue(incoming, capture,
                                capture + 60_000_000 if deadline_ns is None else deadline_ns)
    return acceptance, (domain.scheduler.step() if acceptance.status is ref.Status.OK else None)


def pull_and_release(stream):
    pulled = stream.pull()
    if pulled.status is ref.Status.OK and pulled.lease is not None:
        return pulled, stream.release(pulled.lease.lease_id), pulled.lease
    return pulled, None, None


def standard_run():
    domain = make_domain()
    stream, status, reason, _ = admit(domain)
    assert status is ref.Status.OK and stream is not None, (status, reason)
    for index, (first, values, count, flags) in enumerate((
            (0, tuple((i % 11) / 11 for i in range(160)), 160, 0),
            (160, tuple(((i + 3) % 13) / 13 for i in range(160)), 160, 0),
            (320, (0.5, -0.25, 0.75, 0.0, 1.0), 5, ref.FINAL_INPUT))):
        capture = domain.clock.origin_ns + (index + 1) * ref.NS_PER_FRAME
        assert stream.enqueue(frame(first, values, count, flags=flags), capture,
                              capture + 60_000_000).status is ref.Status.OK
        assert domain.scheduler.step() is ref.Status.OK
        pulled, released, lease = pull_and_release(stream)
        assert pulled.status is ref.Status.OK and released is ref.Status.OK
        assert isinstance(lease, ref.Lease)
    assert stream.end_input(325) is ref.Status.OK
    for _ in range(4):
        domain.scheduler.step()
        if stream.pull().status is ref.Status.END_OF_STREAM:
            break
    assert stream.pull().status is ref.Status.END_OF_STREAM
    return domain, stream


class EngineV1FixtureTest(unittest.TestCase):
    def test_artifacts_are_valid_json_with_pinned_identities(self):
        contract = json.loads((HERE / "contract.json").read_text(encoding="ascii"))
        schema = json.loads((HERE / "graph.schema.json").read_text(encoding="ascii"))
        config = load_config()
        graph = load_graph()
        report = json.loads((HERE / "report.json").read_text(encoding="ascii"))
        self.assertEqual(contract["schema_id"], ref.CONTRACT_ID)
        self.assertEqual(contract["status"], "proposal-only")
        self.assertEqual(schema["$id"], "audio-sdk/engine-v1/graph/0.1")
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(report["contract"], ref.CONTRACT_ID)
        self.assertEqual(report["abi_version"], ref.ABI_VERSION)
        for name, expected in (("contract.json", CONTRACT_FILE_DIGEST),
                               ("domain.json", DOMAIN_FILE_DIGEST),
                               ("graph.json", GRAPH_FILE_DIGEST),
                               ("graph.schema.json", SCHEMA_FILE_DIGEST)):
            self.assertEqual(hashlib.sha256((HERE / name).read_bytes()).hexdigest(), expected)
        self.assertEqual(hashlib.sha256(ref.canonical_bytes(config)).hexdigest(), DOMAIN_DIGEST)
        self.assertEqual(hashlib.sha256(ref.canonical_bytes(graph)).hexdigest(), GRAPH_DIGEST)
        text = (HERE / "report.json").read_text(encoding="ascii")
        self.assertEqual(ref.sha256_hex(text.encode("ascii")), REPORT_DIGEST)
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="ascii").strip(),
                         f"{REPORT_DIGEST}  report.json")
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)

    def test_domain_control_validation_and_single_scheduler_owner(self):
        for key, value, reason in (("worker_count", 2, "single_scheduler_owner"),
                                   ("max_streams", 3, "max_streams"),
                                   ("policy_digest", "0" * 64, "policy_digest")):
            config = load_config()
            config[key] = value
            with self.assertRaises(ValueError) as caught:
                ref.Domain(config)
            self.assertIn(reason, str(caught.exception))
        domain = make_domain()
        with self.assertRaises(ValueError):
            domain.create_scheduler()
        stream, status, reason, _ = admit(domain)
        self.assertEqual((status, reason), (ref.Status.OK, ""))
        self.assertEqual(stream.scheduler_id, domain.scheduler.owner)
        self.assertEqual(stream.enqueue(full_frame(0), 0, 1, owner="wrong").status,
                         ref.Status.INVALID_ARGUMENT)
        self.assertEqual(stream.pull(owner="wrong").status, ref.Status.INVALID_ARGUMENT)
        self.assertEqual(domain.remove_stream(stream.stream_id, owner="wrong"),
                         ref.Status.INVALID_ARGUMENT)
        self.assertEqual(stream.quiesce(ref.QUIESCE_CANCEL, owner="wrong")[0],
                         ref.Status.INVALID_ARGUMENT)
        self.assertEqual(stream.reset(2, 0, owner="wrong"), ref.Status.INVALID_ARGUMENT)
        self.assertEqual(domain.close(), ref.Status.BUSY)

    def test_graph_validation_rejects_unsupported_topology_and_metadata(self):
        cycle = load_graph()
        cycle["nodes"][1]["depends_on"] = ["activity"]
        cycle["nodes"][2]["depends_on"] = ["delay"]
        self.assertEqual(admit(make_domain(), cycle)[1], ref.Status.INVALID_ARGUMENT)
        fan_in = load_graph()
        fan_in["nodes"][1]["depends_on"] = ["gain", "gain"]
        self.assertEqual(admit(make_domain(), fan_in)[2], "audio_fan_in")
        extra = load_graph()
        extra["unsupported"] = True
        self.assertEqual(admit(make_domain(), extra)[2], "graph_keys")
        bad_format = load_graph()
        bad_format["format"]["frame_samples"] = 192
        self.assertEqual(admit(make_domain(), bad_format)[2], "graph_version_or_format")
        bad_digest = load_graph()
        bad_digest["nodes"][0]["descriptor_digest"] = "0" * 64
        self.assertEqual(admit(make_domain(), bad_digest)[2], "descriptor_digest")
        bad_hook = load_graph()
        bad_hook["nodes"][0]["hooks"]["process_mode"] = True
        self.assertEqual(admit(make_domain(), bad_hook)[2], "hook_mismatch:process_mode")
        bad_signal = load_graph()
        bad_signal["nodes"][2]["settings"]["signal_kind"] = "energy"
        self.assertEqual(admit(make_domain(), bad_signal)[2], "unknown_signal")
        bad_delay = load_graph()
        bad_delay["nodes"][1]["settings"]["delay_samples"] = 81
        self.assertEqual(admit(make_domain(), bad_delay)[2], "delay_mismatch")

    def test_admission_rejects_existing_resources_and_enforces_max_streams(self):
        domain = make_domain()
        first, status, reason, _ = admit(domain)
        self.assertEqual((status, reason), (ref.Status.OK, ""))
        self.assertEqual(first.stream_id, 1)
        duplicate, status, reason, acceptance = admit(domain)
        self.assertIsNone(duplicate)
        self.assertEqual((status, reason), (ref.Status.RESOURCE_EXHAUSTED,
                                            "resource_already_admitted"))
        self.assertEqual((acceptance.status, acceptance.accepted_samples),
                         (ref.Status.RESOURCE_EXHAUSTED, 0))
        second_graph = load_graph()
        second_graph["graph_id"] = "canonical.engine.fixture.v2"
        second, status, reason, _ = admit(domain, second_graph)
        self.assertEqual((status, reason), (ref.Status.OK, ""))
        self.assertEqual(second.stream_id, 2)
        self.assertIsNot(first.providers["gain"], second.providers["gain"])
        third_graph = load_graph()
        third_graph["graph_id"] = "canonical.engine.fixture.v3"
        third, status, reason, acceptance = admit(domain, third_graph)
        self.assertIsNone(third)
        self.assertEqual((status, reason), (ref.Status.RESOURCE_EXHAUSTED, "max_streams"))
        self.assertEqual(acceptance.accepted_samples, 0)
        self.assertEqual(domain.counters["admissions"], 2)

    def test_input_capacity_full_is_explicit_zero_acceptance(self):
        domain = make_domain()
        stream, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        for index in range(3):
            capture = domain.clock.origin_ns + (index + 1) * ref.NS_PER_FRAME
            acceptance = stream.enqueue(full_frame(index * 160, index), capture,
                                        capture + 60_000_000)
            self.assertEqual(acceptance.status, ref.Status.OK)
        self.assertEqual([item.sequence for item in stream.input_queue], [1, 2, 3])
        capture = domain.clock.origin_ns + 4 * ref.NS_PER_FRAME
        full = stream.enqueue(full_frame(480), capture, capture + 60_000_000)
        self.assertEqual((full.status, full.accepted_samples, full.reason),
                         (ref.Status.RESOURCE_EXHAUSTED, 0, "input_queue_full"))
        self.assertEqual([item.sequence for item in stream.input_queue], [1, 2, 3])
        self.assertEqual(stream.counters["rejected_frames"], 1)
        self.assertEqual(stream.counters["input_high_water"], 3)
        self.assertEqual(domain.scheduler.step(), ref.Status.OK)
        self.assertEqual([item.sequence for item in stream.input_queue], [2, 3])

    def test_leases_are_single_owner_fifo_with_explicit_misuse(self):
        domain = make_domain()
        stream, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(stream.pull().status, ref.Status.NOT_READY)
        acceptance, step_status = enqueue_and_step(domain, stream, full_frame(0))
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        pulled = stream.pull()
        self.assertEqual(pulled.status, ref.Status.OK)
        lease = pulled.lease
        self.assertIsNotNone(lease)
        self.assertEqual((lease.lease_id, lease.domain_id, lease.stream_id, lease.epoch),
                         ("L1-1", ref_domain_id(domain), 1, 1))
        self.assertEqual(stream.pull().status, ref.Status.BUSY)
        self.assertEqual(stream.release("wrong-lease"), ref.Status.INVALID_ARGUMENT)
        self.assertIs(stream.active_lease, lease)
        self.assertEqual(stream.release(lease.lease_id), ref.Status.OK)
        self.assertEqual(stream.release(lease.lease_id), ref.Status.INVALID_ARGUMENT)
        self.assertIsNone(stream.active_lease)
        self.assertEqual(stream.counters["bad_lease_releases"], 2)
        self.assertEqual(stream.counters["lease_acquires"], 1)
        self.assertEqual(stream.counters["lease_releases"], 1)

    def test_partial_frame_conservation_and_eos_after_drain(self):
        config = load_config()
        config["max_drain_calls"] = 4
        domain = make_domain(config=config)
        delayed = load_graph()
        delayed["nodes"][1]["delay_samples"] = 480
        delayed["nodes"][1]["settings"]["delay_samples"] = 480
        stream, status, reason, _ = admit(domain, delayed)
        self.assertEqual((status, reason), (ref.Status.OK, ""))
        for first, flags in ((0, 0), (160, ref.FINAL_INPUT)):
            acceptance, step_status = enqueue_and_step(domain, stream, full_frame(first, flags=flags))
            self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
            pulled, released, lease = pull_and_release(stream)
            self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        self.assertFalse(stream.drain_complete)
        for _ in range(8):
            if stream.drain_complete:
                break
            step_status = domain.scheduler.step()
            self.assertEqual(step_status, ref.Status.OK)
            pulled, released, lease = pull_and_release(stream)
            if stream.drain_complete:
                self.assertEqual((pulled.status, released), (ref.Status.END_OF_STREAM, None))
            else:
                self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        self.assertTrue(stream.drain_complete)
        self.assertEqual(stream.drain_calls, 3)
        self.assertEqual(stream.pull().status, ref.Status.END_OF_STREAM)
        self.assertEqual([lease.valid_count for lease in stream.delivered_leases], [0, 0, 0, 0, 0])

    def test_output_backpressure_is_explicit_and_input_is_not_discarded(self):
        domain = make_domain()
        stream, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        for index in range(3):
            acceptance, step_status = enqueue_and_step(domain, stream, full_frame(index * 160, index))
            self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
            pulled, released, lease = pull_and_release(stream)
            self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        for index in range(3):
            acceptance, step_status = enqueue_and_step(
                domain, stream, full_frame((index + 3) * 160, index + 3))
            self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(len(stream.output_queue), 3)
        acceptance, step_status = enqueue_and_step(domain, stream, full_frame(960, 6))
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.NOT_READY))
        self.assertEqual([item.sequence for item in stream.input_queue], [7])
        steps = domain.scheduler.steps
        self.assertEqual(domain.scheduler.step(), ref.Status.NOT_READY)
        self.assertEqual(domain.scheduler.steps, steps)
        self.assertEqual(len(stream.output_queue), 3)
        self.assertEqual([item.sequence for item in stream.input_queue], [7])
        pulled, released, lease = pull_and_release(stream)
        self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(domain.scheduler.step(), ref.Status.OK)
        self.assertEqual(len(stream.output_queue), 3)
        self.assertEqual(stream.input_queue, [])
        self.assertEqual(stream.counters["produced_frames"], 7)

    def test_slow_stream_deadline_and_failing_stream_requires_reset(self):
        slow_graph = load_graph()
        slow_graph["nodes"][0]["settings"]["work_ns"] = 80_000_000
        domain = make_domain()
        stream, status, _, _ = admit(domain, slow_graph)
        self.assertEqual(status, ref.Status.OK)
        capture = domain.clock.origin_ns + ref.NS_PER_FRAME
        acceptance, step_status = enqueue_and_step(
            domain, stream, full_frame(0), deadline_ns=capture + 1_000_000)
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        pulled, released, lease = pull_and_release(stream)
        self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        self.assertTrue(lease.deadline_miss)
        self.assertEqual(stream.counters["deadline_misses"], 1)
        self.assertEqual(domain.counters["deadline_misses"], 1)

        failing = single_node_graph("fixture.failing.v0",
                                    {"fail_at_frame": 1, "reason": "control_failure",
                                     "work_ns": 1_000_000},
                                    graph_id="failing.graph.v1")
        failing_domain = make_domain()
        failing_stream, status, _, _ = admit(failing_domain, failing)
        self.assertEqual(status, ref.Status.OK)
        first, step_status = enqueue_and_step(failing_domain, failing_stream, full_frame(0))
        self.assertEqual((first.status, step_status), (ref.Status.OK, ref.Status.OK))
        released = pull_and_release(failing_stream)[1]
        self.assertEqual(released, ref.Status.OK)
        second, step_status = enqueue_and_step(failing_domain, failing_stream, full_frame(160))
        self.assertEqual(second.status, ref.Status.OK)
        self.assertEqual(step_status, ref.Status.BACKEND_FAILURE)
        self.assertEqual(failing_stream.lifecycle, ref.Lifecycle.NEEDS_RESET)
        self.assertEqual(failing_stream.failures[0].reason, "control_failure")
        self.assertEqual(enqueue_and_step(failing_domain, failing_stream, full_frame(320))[0].status,
                         ref.Status.NEEDS_RESET)
        self.assertEqual(failing_stream.reset(2, 0), ref.Status.OK)

    def test_quiesce_drain_timeout_and_cancel_accounting(self):
        domain = make_domain()
        stream, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        for index, (first, values, count, flags) in enumerate((
                (0, tuple((i % 11) / 11 for i in range(160)), 160, 0),
                (160, tuple(((i + 3) % 13) / 13 for i in range(160)), 160, 0),
                (320, (0.5, -0.25, 0.75, 0.0, 1.0), 5, ref.FINAL_INPUT))):
            capture = domain.clock.origin_ns + (index + 1) * ref.NS_PER_FRAME
            self.assertEqual(stream.enqueue(frame(first, values, count, flags=flags), capture,
                                            capture + 60_000_000).status, ref.Status.OK)
        self.assertEqual(stream.quiesce(ref.QUIESCE_DRAIN), (ref.Status.OK, ""))
        self.assertTrue(stream.drain_complete)
        self.assertEqual(stream.pull().status, ref.Status.END_OF_STREAM)
        self.assertEqual(stream.counters["delivered_valid_samples"], 325)

        blocked = make_domain()
        blocked_stream, status, _, _ = admit(blocked)
        self.assertEqual(status, ref.Status.OK)
        for index in range(3):
            acceptance, step_status = enqueue_and_step(
                blocked, blocked_stream, full_frame(index * 160, index))
            self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(blocked_stream.end_input(480), ref.Status.OK)
        self.assertEqual(len(blocked_stream.output_queue), 3)
        self.assertEqual(blocked_stream.quiesce(ref.QUIESCE_DRAIN),
                         (ref.Status.QUIESCE_TIMEOUT, "quiesce_timeout"))
        self.assertEqual(blocked_stream.counters["quiesce_timeouts"], 1)
        for index in range(3):
            pulled, released, lease = pull_and_release(blocked_stream)
            self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(blocked_stream.output_queue, [])
        self.assertEqual(blocked_stream.quiesce(ref.QUIESCE_DRAIN), (ref.Status.OK, ""))

        cancel_domain = make_domain()
        cancel_stream, status, _, _ = admit(cancel_domain)
        self.assertEqual(status, ref.Status.OK)
        acceptance, step_status = enqueue_and_step(cancel_domain, cancel_stream, full_frame(0))
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        pulled, released, lease = pull_and_release(cancel_stream)
        self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(enqueue_and_step(cancel_domain, cancel_stream, full_frame(160))[0].status,
                         ref.Status.OK)
        self.assertEqual(cancel_stream.quiesce(ref.QUIESCE_CANCEL), (ref.Status.OK, ""))
        record = cancel_stream.cancellations[-1]
        self.assertEqual((record.reason, record.abandoned_start, record.abandoned_end,
                          record.abandoned_samples),
                         ("quiesce_cancel", 80, 320, 240))
        self.assertEqual(cancel_domain.counters["cancelled_samples"], 240)

    def test_reset_requires_higher_epoch_quiescence_and_no_lease(self):
        domain = make_domain()
        stream, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(enqueue_and_step(domain, stream, full_frame(0))[0].status, ref.Status.OK)
        self.assertEqual(stream.reset(2, 0), ref.Status.BUSY)
        pulled = stream.pull()
        self.assertEqual(pulled.status, ref.Status.OK)
        self.assertEqual(stream.reset(2, 0), ref.Status.BUSY)
        self.assertEqual(stream.release(pulled.lease.lease_id), ref.Status.OK)
        self.assertEqual(stream.quiesce(ref.QUIESCE_CANCEL), (ref.Status.OK, ""))
        self.assertEqual(stream.reset(1, 0), ref.Status.INVALID_ARGUMENT)
        self.assertEqual(stream.reset(2, 0), ref.Status.OK)
        self.assertEqual(stream.epoch, 2)
        self.assertEqual(stream.counters["submitted_frames"], 0)
        self.assertEqual(stream.analysis_records, [])
        old = analysis_template(domain)
        old["epoch"] = 1
        self.assertEqual(stream.submit_analysis(old)["status"], "rejected_stale_analysis")
        self.assertEqual(stream.counters["analysis_accepted"], 0)

    def test_cancelled_in_flight_output_is_discarded_not_cross_stream_delivered(self):
        domain = make_domain()
        first, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        second_graph = load_graph()
        second_graph["graph_id"] = "canonical.engine.fixture.v2"
        second, status, _, _ = admit(domain, second_graph)
        self.assertEqual(status, ref.Status.OK)
        capture = domain.clock.origin_ns + ref.NS_PER_FRAME
        acceptance = first.enqueue(full_frame(0), capture, capture + 60_000_000)
        self.assertEqual(acceptance.status, ref.Status.OK)
        item = domain.scheduler.begin_step()
        self.assertIsNotNone(item)
        first.epoch = 2  # obsolete epoch at the control barrier
        self.assertIsNotNone(domain.scheduler._in_flight)
        self.assertEqual(domain.scheduler.finish_step(), ref.Status.OK)
        record = first.cancellations[-1]
        self.assertEqual((record.reason, record.in_flight_sequence, record.discarded_output),
                         ("obsolete_epoch", 1, True))
        self.assertEqual(first.output_queue, [])
        self.assertEqual(first.counters["discarded_frames"], 1)
        self.assertEqual(second.output_queue, [])
        self.assertEqual(second.pull().status, ref.Status.NOT_READY)

    def test_fifo_is_single_scheduler_sequence_order(self):
        domain = make_domain()
        first, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        second_graph = load_graph()
        second_graph["graph_id"] = "canonical.engine.fixture.v2"
        second, status, _, _ = admit(domain, second_graph)
        self.assertEqual(status, ref.Status.OK)
        for stream, start, seed in ((first, 0, 0), (second, 0, 1), (first, 160, 2)):
            acceptance, step_status = enqueue_and_step(domain, stream, full_frame(start, seed))
            self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        observed = []
        for stream in (first, second, first):
            pulled, released, lease = pull_and_release(stream)
            self.assertEqual((pulled.status, released), (ref.Status.OK, ref.Status.OK))
            observed.append(lease.lease_id)
        self.assertEqual(observed, ["L1-1", "L2-2", "L1-3"])
        self.assertEqual(domain.scheduler.steps, 3)

    def test_transition_hooks_require_proof_and_observe_does_not_commit(self):
        transition = single_node_graph("fixture.transition.v0", {"work_ns": 1_000_000},
                                       graph_id="transition.graph.v1", hooks=HOOKS_TRANSITION)
        outputs = []
        for mode in ("full", "cheap"):
            domain = make_domain()
            stream, status, _, _ = admit(domain, transition)
            self.assertEqual(status, ref.Status.OK)
            self.assertEqual(stream.set_mode(mode), ref.Status.OK)
            for index in range(2):
                acceptance, step_status = enqueue_and_step(domain, stream, full_frame(index * 160, index))
                self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
                self.assertEqual(pull_and_release(stream)[1], ref.Status.OK)
            outputs.append(stream.output_digest())
            if mode == "cheap":
                self.assertEqual(stream.counters["transition_cheap_calls"], 2)
                prepared = stream.resume_prepare("node", [0.0] * 8, 2)
                self.assertEqual((prepared["warm_frames"], len(prepared["buffer"])),
                                 (2, ref.FRAME_SAMPLES))
                self.assertEqual(len(prepared["prepared_digest"]), 64)
        self.assertEqual(outputs[0], outputs[1])

        single_full_domain = make_domain()
        single_full, status, _, _ = admit(single_full_domain, transition)
        self.assertEqual(status, ref.Status.OK)
        acceptance, step_status = enqueue_and_step(single_full_domain, single_full, full_frame(0))
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(pull_and_release(single_full)[1], ref.Status.OK)
        single_full_digest = single_full.output_digest()

        observe_domain = make_domain()
        observe, status, _, _ = admit(observe_domain, transition)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(observe.set_mode("observe"), ref.Status.OK)
        acceptance, step_status = enqueue_and_step(observe_domain, observe, full_frame(0))
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(pull_and_release(observe)[1], ref.Status.OK)
        self.assertEqual(observe.providers["node"].state, 0.0)
        self.assertEqual(observe.output_digest(), single_full_digest)

        public = single_node_graph("fixture.public.v0", {"gain": 1.0, "work_ns": 1_000_000},
                                   graph_id="public.graph.v1")
        public_domain = make_domain()
        public_stream, status, _, _ = admit(public_domain, public)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(public_stream.set_mode("cheap"), ref.Status.INVALID_ARGUMENT)
        self.assertEqual(enqueue_and_step(public_domain, public_stream, full_frame(0))[0].status,
                         ref.Status.OK)

        reset_graph = single_node_graph("fixture.reset_required.v0", {"work_ns": 1_000_000},
                                        graph_id="reset.graph.v1", hooks=HOOKS_TRANSITION)
        reset_domain = make_domain()
        reset_stream, status, _, _ = admit(reset_domain, reset_graph)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(reset_stream.set_mode("cheap"), ref.Status.INVALID_ARGUMENT)
        self.assertEqual(reset_stream.set_mode("observe"), ref.Status.OK)

    def test_batch_lanes_have_per_lane_validity_and_preflight(self):
        batch_graph = single_node_graph("fixture.batch.v0", {"max_batch": 2, "work_ns": 1_000_000},
                                        graph_id="batch.graph.v1", hooks=HOOKS_BATCH)
        domain = make_domain()
        stream, status, _, _ = admit(domain, batch_graph)
        self.assertEqual(status, ref.Status.OK)
        provider = stream.providers["node"]
        config_digest = "a" * 64

        def lane(state_id, valid_count, fail_lane=-1, deadline_ns=None, work_ns=1_000_000):
            return {
                "state_id": state_id, "config_digest": config_digest,
                "samples": tuple((i % 9) / 9 for i in range(ref.FRAME_SAMPLES)),
                "valid_count": valid_count, "first_sample": 0, "accepted_end": 160,
                "deadline_ns": domain.clock.now_ns + 60_000_000 if deadline_ns is None else deadline_ns,
                "work_ns": work_ns, "gain": 1.0, "fail_lane": fail_lane,
                "failure_reason": "lane_failure",
            }

        results = domain.process_batch(stream, "node", [lane("a", 160), lane("b", 0)])
        self.assertEqual([(item.status.value, item.validity) for item in results],
                         [("ok", "known"), ("ok", "unknown")])
        before = dict(provider.lane_states)
        aliased = domain.process_batch(stream, "node", [lane("same", 160), lane("same", 160)])
        self.assertEqual([item.reason for item in aliased],
                         ["aliased_lane_state", "aliased_lane_state"])
        self.assertTrue(all(item.status is ref.Status.INVALID_ARGUMENT for item in aliased))
        incompatible_lane = lane("other", 160)
        incompatible_lane["config_digest"] = "b" * 64
        incompatible = domain.process_batch(stream, "node", [lane("c", 160), incompatible_lane])
        self.assertEqual([item.reason for item in incompatible],
                         ["incompatible_lane_state", "incompatible_lane_state"])
        self.assertEqual(provider.lane_states, before)
        self.assertEqual(stream.counters["batch_lanes"], 2)

        failures = domain.process_batch(
            stream, "node", [lane("failed", 160, fail_lane=0), lane("d", 160)])
        self.assertEqual([item.status for item in failures],
                         [ref.Status.BACKEND_FAILURE, ref.Status.OK])
        self.assertEqual(failures[0].reason, "lane_failure")
        self.assertNotIn("failed", provider.lane_states)

        clock_before = domain.clock.now_ns
        deadline = clock_before + 1_000_000 - 1
        missed = domain.process_batch(stream, "node",
                                      [lane("e", 160, deadline_ns=deadline),
                                       lane("f", 160, deadline_ns=deadline)])
        self.assertTrue(all(item.deadline_miss for item in missed))
        self.assertEqual(domain.clock.now_ns, clock_before + 1_000_000)

        provider.in_batch = True
        with self.assertRaises(ref.ProviderFailure):
            provider.process((0.0,) * ref.FRAME_SAMPLES, {}, {})
        provider.in_batch = False

    def test_analysis_identity_invalid_probability_and_no_revival(self):
        domain, stream = standard_run()
        self.assertEqual([record.status for record in stream.analysis_records], ["ok", "ok"])
        template = analysis_template(domain)
        rejected = []
        for key, value in (("producer_id", "other.producer.v0"),
                           ("tap_id", "pcm.delay.out"),
                           ("signal_kind", "energy"),
                           ("calibration_digest", "0" * 64)):
            event = dict(template, **{key: value})
            rejected.append(stream.submit_analysis(event)["status"])
        stale = dict(template, epoch=0)
        out_of_range = dict(template, source_start=0, source_end=400)
        nonfinite = dict(template, value=float("nan"))
        out_of_probability = dict(template, value=1.5)
        unknown_with_value = dict(template, validity="unknown")
        bad_clock = dict(template, available_ns=1_000_000_000)
        rejected.extend([
            stream.submit_analysis(event)["status"] for event in (
                stale, out_of_range, nonfinite, out_of_probability, unknown_with_value, bad_clock)
        ])
        self.assertEqual(rejected, [
            "rejected_unselected_source", "rejected_unselected_source",
            "rejected_unselected_source", "rejected_unselected_source",
            "rejected_stale_analysis", "rejected_out_of_range_analysis",
            "rejected_invalid_analysis", "rejected_invalid_analysis",
            "rejected_invalid_analysis", "rejected_bad_analysis_clock",
        ])
        self.assertEqual(stream.counters["analysis_rejected"], 10)
        self.assertEqual(stream.reset(2, 0), ref.Status.OK)
        self.assertEqual(stream.analysis_records, [])
        old = analysis_template(domain)
        old["epoch"] = 1
        self.assertEqual(stream.submit_analysis(old)["status"], "rejected_stale_analysis")
        self.assertEqual(stream.counters["analysis_accepted"], 0)

    def test_stats_use_caller_buffer_and_decimal_strings(self):
        domain = make_domain()
        stream, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        acceptance, step_status = enqueue_and_step(domain, stream, full_frame(0))
        self.assertEqual((acceptance.status, step_status), (ref.Status.OK, ref.Status.OK))
        self.assertEqual(pull_and_release(stream)[1], ref.Status.OK)
        early, required, text = domain.query_stats(stream.stream_id, capacity=8)
        self.assertEqual((early, text), (ref.Status.RESOURCE_EXHAUSTED, None))
        self.assertGreater(required, 8)
        overall, overall_required, overall_text = domain.query_stats(capacity=1 << 20)
        self.assertEqual(overall, ref.Status.OK)
        self.assertEqual(overall_required, len(overall_text.encode("ascii")) + 1)
        status, required, text = domain.query_stats(stream.stream_id, capacity=1 << 20)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(required, len(text.encode("ascii")) + 1)
        payload = json.loads(text)
        self.assertEqual(payload["schema_id"], ref.STATS_ID)
        self.assertEqual(payload["contract"], ref.CONTRACT_ID)
        self.assertEqual(payload["worker_count"], "1")
        self.assertEqual(payload["stream_id"], "1")
        self.assertEqual(payload["epoch"], "1")
        self.assertEqual(payload["accepted_samples"], "160")
        self.assertEqual(payload["lease_releases"], "1")
        self.assertEqual(payload["scheduler_owner"], domain.scheduler.owner)
        self.assertFalse(any("ptr" in key or "path" in key or "wall" in key for key in payload))
        self.assertFalse(any("0x" in value for value in payload.values() if isinstance(value, str)))
        self.assertEqual(json.loads(overall_text)["active_streams"], "1")

    def test_fatal_worker_failure_closes_admission_and_reports_each_stream(self):
        domain = make_domain()
        first, status, _, _ = admit(domain)
        self.assertEqual(status, ref.Status.OK)
        second_graph = load_graph()
        second_graph["graph_id"] = "canonical.engine.fixture.v2"
        second, status, _, _ = admit(domain, second_graph)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(domain.inject_fatal_worker_failure("worker_fatal"), ref.Status.NEEDS_RESET)
        self.assertEqual([first.lifecycle, second.lifecycle],
                         [ref.Lifecycle.NEEDS_RESET, ref.Lifecycle.NEEDS_RESET])
        self.assertEqual([failure.stream_id for failure in domain.failures], [1, 2])
        self.assertTrue(domain.admission_closed)
        self.assertEqual(admit(domain)[1], ref.Status.NEEDS_RESET)
        payload = json.loads(domain.query_stats(capacity=1 << 20)[2])
        self.assertEqual(payload["fatal_worker_failures"], "1")
        self.assertEqual(payload["admission_closed"], True)
        self.assertEqual(domain.remove_stream(1), ref.Status.OK)
        self.assertEqual(domain.remove_stream(2), ref.Status.OK)
        self.assertEqual(domain.close(), ref.Status.OK)
        self.assertEqual(domain.close(), ref.Status.INVALID_ARGUMENT)

    def test_canonical_report_digest_is_stable_and_checked_in(self):
        _, first = standard_run()
        _, second = standard_run()
        text_a, digest_a = ref.canonical_report(first.domain, first)
        text_b, digest_b = ref.canonical_report(second.domain, second)
        self.assertEqual((text_a, digest_a), (text_b, digest_b))
        self.assertEqual(digest_a, REPORT_DIGEST)
        self.assertEqual(first.output_digest(), OUTPUT_DIGEST)
        self.assertEqual((HERE / "report.json").read_text(encoding="ascii"), text_a)
        self.assertIn(GRAPH_DIGEST, text_a)
        self.assertIn(DOMAIN_DIGEST, text_a)
        self.assertNotIn("NaN", text_a)
        self.assertNotIn("Infinity", text_a)

    def test_installed_external_fixture(self):
        with tempfile.TemporaryDirectory(prefix="sdk-engine-") as temp:
            root = Path(temp)
            dist_a = build_wheel.build_wheel(root / "dist-a")
            dist_b = build_wheel.build_wheel(root / "dist-b")
            self.assertEqual(dist_a.read_bytes(), dist_b.read_bytes())
            self.assertEqual(hashlib.sha256(dist_a.read_bytes()).hexdigest(), WHEEL_DIGEST)
            payload = b"".join(path.read_bytes() for path in sorted(FIXTURE_SOURCE.glob("*.py")))
            self.assertEqual(hashlib.sha256(payload).hexdigest(), THIRD_PARTY_SOURCE_DIGEST)

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
            self.assertEqual(record["contract"], ref.CONTRACT_ID)
            self.assertEqual(record["fixture_id"], "third-party/engine-v1-fixture/0.1")
            self.assertTrue(record["installed"])
            self.assertEqual(record["fixture_source_digest"], THIRD_PARTY_SOURCE_DIGEST)
            self.assertEqual(record["domain_digest"], DOMAIN_DIGEST)
            self.assertEqual(record["graph_digest"], GRAPH_DIGEST)
            self.assertEqual(record["report_digest"], REPORT_DIGEST)


def ref_domain_id(domain):
    return domain.config.domain_id


def analysis_template(domain):
    policy = domain.config.policy
    return {
        "producer_id": policy["chosen_producer"],
        "tap_id": policy["chosen_tap"],
        "stream_id": 1,
        "epoch": 1,
        "source_start": 0,
        "source_end": 160,
        "available_ns": 1_100_000_000,
        "signal_kind": policy["signal_kind"],
        "value": 0.5,
        "validity": "known",
        "calibration_digest": policy["calibration_digest"],
    }


if __name__ == "__main__":
    unittest.main()
