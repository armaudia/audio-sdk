# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the fused-batch I/O-binding evidence module."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


def _frame(seed: int, scale: float = 0.5) -> list:
    return reference.condition_frame(seed, scale)


class StrictJsonTests(unittest.TestCase):
    def test_model_bytes_deterministic_and_digest(self) -> None:
        first = reference.model_bytes()
        second = reference.model_bytes()
        self.assertEqual(first, second)
        self.assertEqual(reference.model_digest(), hashlib.sha256(first).hexdigest())
        self.assertTrue(first.endswith(b"\n"))

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(reference.DuplicateKeyError):
            reference.strict_json(b'{"a":1,"a":2}')

    def test_strict_json_rejects_nonfinite_numbers(self) -> None:
        with self.assertRaises(reference.NonFiniteNumberError):
            reference.strict_json(b'{"a":1e999}')

    def test_strict_json_rejects_malformed(self) -> None:
        with self.assertRaises(json.JSONDecodeError):
            reference.strict_json(b"not-json")

    def test_canonical_bytes_are_sorted_and_nan_free(self) -> None:
        payload = reference.canonical_bytes({"b": [1.0, -0.0], "a": 2})
        self.assertEqual(payload, b'{"a":2,"b":[1.0,0.0]}')
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})

    def test_pin_parser_rejects_invalid_lines(self) -> None:
        for bad in ("not-a-line", "Z" * 64 + "  docs/x",
                    "a" * 64 + "  ../escape", "a" * 64 + "  unknown/x"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(bad)
        duplicate = "\n".join([f"{'a' * 64}  docs/x", f"{'a' * 64}  docs/x"])
        with self.assertRaises(ValueError):
            reference.parse_pin_lines(duplicate)


class BoundaryTests(unittest.TestCase):
    def test_open_requires_exact_runtime_and_config(self) -> None:
        with self.assertRaises(reference.Rejected):
            reference.FusedBatchBoundary.open(
                "onnxruntime-osx-arm64-1.31.1", reference._model_asset(),
                reference.CONFIG)
        with self.assertRaises(reference.Rejected):
            reference.FusedBatchBoundary.open(
                reference.RUNTIME_ID, reference._model_asset(),
                {**reference.CONFIG, "intra_op_num_threads": 2})
        boundary = reference.fresh_boundary()
        self.assertFalse(boundary.capabilities()["runtime_available"])
        self.assertFalse(boundary.capabilities()["fused_tensor_kernel"])

    def test_model_asset_rejections_are_closed(self) -> None:
        cases = []
        data = reference.model_bytes()
        cases.append(("wrong-id", ("other", data, hashlib.sha256(data).hexdigest(), len(data))))
        cases.append(("wrong-digest", (reference.MODEL_ID, data, "0" * 64, len(data))))
        cases.append(("wrong-size", (reference.MODEL_ID, data,
                                     reference.model_digest(), len(data) + 1)))
        cases.append(("malformed", (reference.MODEL_ID, b"nope",
                                    hashlib.sha256(b"nope").hexdigest(), 4)))
        cases.append(("real-graph", (reference.MODEL_ID,
                                     reference._mutated_model(real_onnx_graph=True),
                                     hashlib.sha256(reference._mutated_model(
                                         real_onnx_graph=True)).hexdigest(),
                                     len(reference._mutated_model(
                                         real_onnx_graph=True)))))
        for name, asset in cases:
            with self.subTest(name=name):
                with self.assertRaises(reference.Rejected):
                    reference.FusedBatchBoundary.open(
                        reference.RUNTIME_ID, asset, reference.CONFIG)

    def test_impulse_goldens(self) -> None:
        boundary = reference.fresh_boundary()
        result = boundary.run([{
            "instance_id": "impulse",
            "frame": [1.0] + [0.0] * (reference.FRAME_SAMPLES - 1),
        }])
        lane = reference.summarize_run(result)["lanes"][0]
        self.assertEqual(lane["waveform_out_first8"][:3], [0.75, 0.03125, 0.015625])
        self.assertEqual(lane["state_out_first4"], [0.0, 0.0, 0.0, 0.0])
        self.assertTrue(lane["all_finite"])

    def test_constant_one_goldens(self) -> None:
        boundary = reference.fresh_boundary()
        lane = reference.summarize_run(boundary.run([{
            "instance_id": "one",
            "frame": [1.0] * reference.FRAME_SAMPLES,
        }]))["lanes"][0]
        self.assertEqual(lane["waveform_out_first8"][:3],
                         [0.75, 0.78125, 0.796875])

    def test_constant_negative_one_goldens(self) -> None:
        boundary = reference.fresh_boundary()
        lane = reference.summarize_run(boundary.run([{
            "instance_id": "neg",
            "frame": [-1.0] * reference.FRAME_SAMPLES,
        }]))["lanes"][0]
        self.assertEqual(lane["waveform_out_first8"][:2], [-0.75, -0.78125])

    def test_silence_is_zero(self) -> None:
        boundary = reference.fresh_boundary()
        lane = reference.summarize_run(boundary.run([{
            "instance_id": "silence",
            "frame": [0.0] * reference.FRAME_SAMPLES,
        }]))["lanes"][0]
        self.assertTrue(lane["all_finite"])
        self.assertEqual(set(lane["waveform_out_first8"]), {0.0})
        self.assertEqual(set(lane["state_out_first4"]), {0.0})

    def test_batch_sizes_1_to_4_accepted_and_5_rejected(self) -> None:
        for size in (1, 2, 3, 4):
            boundary = reference.fresh_boundary()
            result = boundary.run([
                {"instance_id": f"size-{size}-{index}", "frame": _frame(index + 1)}
                for index in range(size)
            ])
            self.assertEqual(result["batch_size"], size)
        boundary = reference.fresh_boundary()
        with self.assertRaises(reference.Rejected) as context:
            boundary.run([
                {"instance_id": f"too-{index}", "frame": _frame(index + 1)}
                for index in range(5)
            ])
        self.assertEqual(context.exception.code, "batch_too_large")

    def test_batch_scalar_parity_per_lane(self) -> None:
        lanes = [
            {"instance_id": "par-a", "frame": _frame(31)},
            {"instance_id": "par-b", "frame": _frame(32, 0.75)},
            {"instance_id": "par-c", "frame": _frame(33, 1.0)},
            {"instance_id": "par-d", "frame": _frame(34, 0.25),
             "state": [0.25, -0.25] + [0.0] * 14},
        ]
        batched = reference.summarize_run(reference.fresh_boundary().run(lanes))
        scalar_boundary = reference.fresh_boundary()
        scalar = [reference.summarize_run(scalar_boundary.run([lane]))["lanes"][0]
                  for lane in lanes]
        for index, lane in enumerate(batched["lanes"]):
            self.assertEqual(lane["waveform_out_sha256"],
                             scalar[index]["waveform_out_sha256"])
            self.assertEqual(lane["state_out_sha256"],
                             scalar[index]["state_out_sha256"])

    def test_io_binding_matches_unbound_path(self) -> None:
        frames = [_frame(41), _frame(42, 0.75)]
        unbound = reference.summarize_run(reference.fresh_boundary().run(
            [{"instance_id": f"bind-{index}", "frame": frames[index]}
             for index in range(2)]))
        waveform = [[0.0] * reference.FRAME_SAMPLES for _ in range(2)]
        state = [[0.0] * reference.STATE_SAMPLES for _ in range(2)]
        bound = reference.summarize_run(reference.fresh_boundary().run(
            [{"instance_id": f"bind-{index}", "frame": list(frames[index])}
             for index in range(2)],
            bindings=[{"waveform_out": waveform[index], "state_out": state[index]}
                      for index in range(2)]))
        self.assertEqual(bound["lanes"], unbound["lanes"])
        for index in range(2):
            self.assertEqual(reference.f32_digest(waveform[index]),
                             bound["lanes"][index]["waveform_out_sha256"])
            self.assertEqual(reference.f32_digest(state[index]),
                             bound["lanes"][index]["state_out_sha256"])

    def test_binding_alias_and_capacity_rejected_without_writes(self) -> None:
        frame = _frame(43)
        boundary = reference.fresh_boundary()
        with self.assertRaises(reference.Rejected) as alias:
            boundary.run([{"instance_id": "alias", "frame": frame}],
                         bindings=[{"waveform_out": frame,
                                    "state_out": [0.0] * reference.STATE_SAMPLES}])
        self.assertEqual(alias.exception.code, "binding_aliases_input")
        self.assertEqual(frame, _frame(43))
        waveform = [0.0] * reference.FRAME_SAMPLES
        state = [0.0] * reference.STATE_SAMPLES
        with self.assertRaises(reference.Rejected) as capacity:
            boundary.run([{"instance_id": "alias", "frame": _frame(44)}],
                         bindings=[{"waveform_out": waveform[:-1], "state_out": state}])
        self.assertEqual(capacity.exception.code, "binding_capacity")
        self.assertEqual(waveform, [0.0] * reference.FRAME_SAMPLES)
        self.assertEqual(state, [0.0] * reference.STATE_SAMPLES)
        with self.assertRaises(reference.Rejected) as shared:
            boundary.run([{"instance_id": "alias", "frame": _frame(45)}],
                         bindings=[{"waveform_out": waveform, "state_out": waveform}])
        self.assertEqual(shared.exception.code, "binding_outputs_aliased")

    def test_binding_not_writable_rejected(self) -> None:
        with self.assertRaises(reference.Rejected) as context:
            reference.fresh_boundary().run(
                [{"instance_id": "tuple", "frame": _frame(46)}],
                bindings=[{"waveform_out": (0.0,) * reference.FRAME_SAMPLES,
                           "state_out": [0.0] * reference.STATE_SAMPLES}])
        self.assertEqual(context.exception.code, "binding_not_writable_list")

    def test_invalid_lane_rejects_whole_batch_atomically(self) -> None:
        boundary = reference.fresh_boundary()
        boundary.run([{"instance_id": "atomic-a", "frame": _frame(51)}])
        state_before = reference._snapshot(boundary)
        waveform = [0.25] * reference.FRAME_SAMPLES
        state = [0.5] * reference.STATE_SAMPLES
        with self.assertRaises(reference.Rejected):
            boundary.run([
                {"instance_id": "atomic-a", "frame": _frame(52)},
                {"instance_id": "atomic-b", "frame": [2.0] + [0.0] * 159},
            ], bindings=[{"waveform_out": waveform, "state_out": state},
                         {"waveform_out": [0.0] * 160,
                          "state_out": [0.0] * 16}])
        self.assertEqual(reference._snapshot(boundary), state_before)
        self.assertEqual(waveform, [0.25] * reference.FRAME_SAMPLES)
        self.assertEqual(state, [0.5] * reference.STATE_SAMPLES)

    def test_nonfinite_and_out_of_range_feeds_rejected(self) -> None:
        for bad in (float("nan"), float("inf"), 1.5):
            with self.assertRaises(reference.Rejected):
                reference.fresh_boundary().run(
                    [{"instance_id": "bad", "frame": [bad] + [0.0] * 159}])
        for bad in (float("nan"), float("inf"), 5.0):
            with self.assertRaises(reference.Rejected):
                reference.fresh_boundary().run(
                    [{"instance_id": "bad", "frame": [0.0] * 160,
                      "state": [bad] + [0.0] * 15}])

    def test_duplicate_and_invalid_lane_ids_rejected(self) -> None:
        with self.assertRaises(reference.Rejected) as duplicate:
            reference.fresh_boundary().run([
                {"instance_id": "dup", "frame": _frame(61)},
                {"instance_id": "dup", "frame": _frame(62)},
            ])
        self.assertEqual(duplicate.exception.code, "duplicate_instance_id")
        with self.assertRaises(reference.Rejected) as invalid:
            reference.fresh_boundary().run(
                [{"instance_id": "Lane-A", "frame": _frame(63)}])
        self.assertEqual(invalid.exception.code, "invalid_instance_id")

    def test_lane_state_isolation(self) -> None:
        boundary = reference.fresh_boundary()
        batch = reference.summarize_run(boundary.run([
            {"instance_id": "iso-a", "frame": _frame(71)},
            {"instance_id": "iso-b", "frame": _frame(72, 0.75)},
        ]))
        solo = reference.fresh_boundary()
        solo_first = reference.summarize_run(
            solo.run([{"instance_id": "iso-a", "frame": _frame(71)}]))
        self.assertEqual(batch["lanes"][0]["state_out_sha256"],
                         solo_first["lanes"][0]["state_out_sha256"])
        next_batch = reference.summarize_run(boundary.run([
            {"instance_id": "iso-a", "frame": _frame(73)}]))
        next_solo = reference.summarize_run(solo.run([
            {"instance_id": "iso-a", "frame": _frame(73)}]))
        self.assertEqual(next_batch["lanes"][0]["state_out_sha256"],
                         next_solo["lanes"][0]["state_out_sha256"])

    def test_injected_fault_needs_reset_and_recovers(self) -> None:
        boundary = reference.fresh_boundary()
        boundary.run([{"instance_id": "fault-a", "frame": _frame(81)}])
        before = reference._snapshot(boundary)
        waveform = [0.25] * reference.FRAME_SAMPLES
        state = [0.5] * reference.STATE_SAMPLES
        boundary.inject_output_fault(0)
        with self.assertRaises(reference.Rejected) as context:
            boundary.run([
                {"instance_id": "fault-a", "frame": _frame(82)},
            ], bindings=[{"waveform_out": waveform, "state_out": state}])
        self.assertEqual(context.exception.code, "lane_output_nonfinite")
        self.assertTrue(boundary.needs_reset)
        self.assertEqual(reference._snapshot(boundary), before)
        self.assertEqual(waveform, [0.25] * reference.FRAME_SAMPLES)
        self.assertEqual(state, [0.5] * reference.STATE_SAMPLES)
        with self.assertRaises(reference.Rejected) as blocked:
            boundary.run([{"instance_id": "fault-a", "frame": _frame(83)}])
        self.assertEqual(blocked.exception.code, "needs_reset")
        boundary.reset()
        self.assertFalse(boundary.needs_reset)
        boundary.run([{"instance_id": "fault-a", "frame": _frame(84)}])

    def test_reset_all_and_single_lane(self) -> None:
        boundary = reference.fresh_boundary()
        boundary.run([
            {"instance_id": "reset-a", "frame": _frame(91)},
            {"instance_id": "reset-b", "frame": _frame(92)},
        ])
        self.assertEqual(boundary.reset("reset-a")["reset_lanes"], 1)
        self.assertEqual(reference._snapshot(boundary)["reset-a"],
                         reference.f32_digest(reference.STATE_INIT))
        self.assertNotEqual(reference._snapshot(boundary)["reset-b"],
                            reference.f32_digest(reference.STATE_INIT))
        self.assertEqual(boundary.reset()["reset_lanes"], 2)
        for digest in reference._snapshot(boundary).values():
            self.assertEqual(digest, reference.f32_digest(reference.STATE_INIT))

    def test_close_is_idempotent_and_blocks_run_and_reset(self) -> None:
        boundary = reference.fresh_boundary()
        boundary.run([{"instance_id": "close", "frame": _frame(93)}])
        self.assertFalse(boundary.close()["already_closed"])
        self.assertTrue(boundary.close()["already_closed"])
        with self.assertRaises(reference.Rejected) as run:
            boundary.run([{"instance_id": "close", "frame": _frame(94)}])
        self.assertEqual(run.exception.code, "closed")
        with self.assertRaises(reference.Rejected) as reset:
            boundary.reset()
        self.assertEqual(reset.exception.code, "closed")


class EvidenceTests(unittest.TestCase):
    def test_adverse_matrix_counts_and_fail_closed(self) -> None:
        adverse = reference.adverse()
        counts = adverse["counts"]
        self.assertEqual(counts["rejection_groups"], {
            "model_rejections": 19,
            "config_rejections": 8,
            "feed_rejections": 13,
            "batch_rejections": 4,
            "binding_rejections": 11,
            "fault_rejections": 1,
            "rights_rejections": 3,
            "runtime_rejections": 2,
        })
        self.assertEqual(counts["rejection_cases"], 61)
        self.assertEqual(counts["lifecycle_checks"], 5)
        self.assertEqual(counts["lifecycle_rejected"], 3)
        self.assertEqual(counts["lifecycle_accepted"], 2)
        self.assertEqual(counts["total_checks"], 66)
        self.assertEqual(counts["failed_open"], 0)
        self.assertTrue(counts["all_rejections_closed"])
        self.assertTrue(adverse["state"]["unchanged_by_feed_rejections"])
        self.assertTrue(adverse["state"]["unchanged_by_binding_rejections"])
        self.assertTrue(adverse["fault_rejections"][
            "injected_lane_output_nonfinite"]["recovered_after_reset"] == "accepted")

    def test_report_disposition_and_eight_blocked_gates(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertTrue(report["qualification"]["proposal_only"])
        self.assertTrue(report["qualification"]["incomplete"])
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(len(report["gates"]), 8)
        for gate in report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen"])
        self.assertTrue(report["rights_gap"]["blocked"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])

    def test_negative_claims_and_boundary_are_closed(self) -> None:
        report = reference.build_report()
        for key, value in report["negative_claims"].items():
            self.assertIs(value, False, key)
        boundary = report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "descriptor_registry_change", "installed_v0_behavior_change",
                    "shared_build_or_ci_change", "processor_exposure",
                    "c_public_boundary"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertEqual(report["format"]["sample_rate_hz"], 16000)
        self.assertEqual(report["format"]["frame_samples"], 160)

    def test_conditions_match_fresh_execution(self) -> None:
        report = reference.build_report()
        conditions = report["conditions"]
        for name in ("impulse", "constant_one", "constant_negative_one",
                     "silence", "lcg_two_frames", "fused_batch_parity",
                     "io_binding_equivalence", "lane_state_isolation",
                     "atomic_rejection"):
            self.assertIn(name, conditions)
        self.assertTrue(conditions["fused_batch_parity"]["all_lane_parity"])
        self.assertTrue(conditions["io_binding_equivalence"]["binding_path_matches"])
        self.assertTrue(conditions["io_binding_equivalence"]["buffers_match_lanes"])
        self.assertTrue(conditions["lane_state_isolation"]["batch_matches_solo"])
        self.assertTrue(conditions["atomic_rejection"]["state_unchanged"])
        self.assertEqual(conditions, reference.measure_conditions())
        probe = report["boundary_checks"]["typical_api_use"]
        self.assertEqual(probe, reference.typical_probe())
        self.assertTrue(probe["all_steps_passed"])
        self.assertEqual(probe["sequence"], list(reference.TYPICAL_PROBE_SEQUENCE))
        self.assertEqual(report["adverse"], reference.adverse())
        self.assertEqual(report["repeatability"], reference.repeatability())
        self.assertTrue(report["repeatability"]["byte_identical"])

    def test_tool_profile_statuses(self) -> None:
        report = reference.build_report()
        profile = report["tool_profile"]
        self.assertEqual(profile["profile"], "tool")
        expected = {
            "version_install_and_provenance": "blocked",
            "clean_checkout_or_extracted_package": "not_run",
            "typical_cli_or_api_use": "passed_synthetic",
            "caller_owned_inputs": "passed_synthetic",
            "malformed_inputs": "passed_synthetic",
            "missing_optional_selection": "passed_synthetic",
            "compile_and_build_evidence": "not_run",
            "synthetic_runtime_evidence": "passed_synthetic",
            "measured_workload_support": "not_reported",
        }
        self.assertEqual({key: value["status"]
                          for key, value in profile["mapped_cases"].items()},
                         expected)

    def test_runtime_and_batch_readiness_are_blocked(self) -> None:
        report = reference.build_report()
        readiness = report["runtime_readiness"]
        self.assertTrue(readiness["blocked"])
        self.assertFalse(readiness["module_spec_found"])
        self.assertFalse(readiness["importable"])
        self.assertFalse(readiness["candidate_used"])
        self.assertEqual(readiness["exact_error"],
                         "ModuleNotFoundError: No module named 'onnxruntime'")
        self.assertFalse(readiness["sdk_runtime_pin_present"])
        batch = report["dpdfnet_batch_readiness"]
        self.assertTrue(batch["blocked"])
        self.assertFalse(batch["batch_capable_export"]["available"])
        self.assertFalse(batch["fused_tensor_kernel_present"])
        self.assertFalse(batch["scheduler_coalescing_is_batching"])
        self.assertFalse(batch["candidate_bytes_present"])
        for candidate in batch["candidates"]:
            self.assertIsNone(candidate["model_revision"])

    def test_report_is_canonical_and_sidecar_matches(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual(payload, reference.canonical_report_bytes(
            reference.strict_json(payload)))
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8")
        self.assertEqual(sidecar,
                         hashlib.sha256(payload).hexdigest() + "  report.json\n")
        self.assertEqual(reference.strict_json(payload),
                         reference.build_report())

    def test_contract_and_model_are_canonical_generated_bytes(self) -> None:
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         reference.contract_bytes())
        self.assertEqual((HERE / "synthetic_model.json").read_bytes(),
                         reference.synthetic_model_bytes())
        contract = reference.strict_json_file(HERE / "contract.json")
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertFalse(contract["model_fixture"]["real_onnx_graph"])
        self.assertFalse(contract["model_fixture"]["real_model_weights"])
        self.assertTrue(contract["rights_gap"]["blocked"])

    def test_readme_digest_block_matches_report(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        pattern = re.compile(r"<!-- REPORT_SHA256_START -->\n`report\.json` "
                             r"SHA-256: `([0-9a-f]{64})`\n<!-- REPORT_SHA256_END -->")
        match = pattern.search(text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), digest)

    def test_board_reference_is_stable_and_not_full_board(self) -> None:
        report = reference.build_report()
        board = report["board_reference"]
        self.assertEqual(board["task_id"], reference.TASK_ID)
        self.assertEqual(board["component_id"], reference.COMPONENT_ID)
        self.assertFalse(board["full_board_hashed"])
        self.assertFalse(board["mutable_board_path_pinned"])
        manifest = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        self.assertNotIn("plan/swarm/TASKS.json", manifest)

    def test_three_in_process_report_generations_match(self) -> None:
        payloads = {reference.canonical_report_bytes(reference.build_report())
                    for _ in range(3)}
        self.assertEqual(len(payloads), 1)

    def test_three_in_process_sources_generations_match(self) -> None:
        payloads = {reference.sources_bytes() for _ in range(3)}
        self.assertEqual(len(payloads), 1)

    def test_three_cold_start_report_processes_match_file(self) -> None:
        code = (
            "import sys; sys.path.insert(0, " + repr(str(HERE)) + "); "
            "import reference, hashlib; "
            "sys.stdout.write(hashlib.sha256(reference.canonical_report_bytes("
            "reference.build_report())).hexdigest())"
        )
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE,
                                    env=env, capture_output=True, text=True,
                                    check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(digests[0],
                         hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
