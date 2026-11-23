# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Offline acceptance tests for the synthetic pipe-control fixture.

The installed-consumer test builds a byte-reproducible wheel with stdlib tools,
installs it with pip --no-index --no-deps and runs an external probe from a
temporary directory outside the source tree.
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

REPORT_DIGEST = "64428914ee08309ab0bb3e18eec739d59f543711f342e488673ddd6246fe21ec"
RECIPE_DIGEST = "d9581a6ee806ec5afcae8bad1c99761ca604fcfb2770ab7b0eb9ded03dbed7c3"
FALLBACK_RECIPE_DIGEST = "b7bbfb8d798e0f376b1d05cd0013b6e65ab5e7db89130e2e422d36b185649192"
FIXTURE_SOURCE_DIGEST = "53397ac16064e748a24526bc80fcbacd5d4a5fb30484ee17bb04ed30dbf4f7ee"
WHEEL_DIGEST = "ba7c3a97346fd888628d05c6d862b281573b0f62c8d52312ca44f9bf0a6d91ae"
INPUT_DIGEST = "9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2"
DELIVERED_DIGEST = "9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2"
PADDED_DIGEST = "5778e7cafee61690e49a898ad8f2f0174b5ddef19f6ab23fca642c4411451ebc"
SWITCH_A_DIGEST = "57fbfb33843af2296884066badc29d08e672a41101b527b0c0c3b4b574d535e3"
SWITCH_B_DIGEST = "40ae88f38d85bbb629a3b14d944f12ab345e16012cf07219cd07cfd8655be4a7"
COMBINED_DIGEST = "f815d34666505ecc0d85796145df3dad57a9bcef23b4a813fa0f02537bf39167"


def load_report() -> dict:
    return json.loads((HERE / "report.json").read_text(encoding="ascii"))


def fresh_session(recipe=None, provider_id="third_party.identity.v0",
                  epoch=1, first=0):
    stages = ref.builtin_available()
    raw = recipe if recipe is not None else ref.base_recipe()
    parsed, status, reason = ref.validate_recipe(raw, stages)
    if status is not ref.Status.OK or parsed is None:
        return None, status, reason
    session, admitted = ref.create_session(parsed, stages, provider_id, epoch, first)
    return session, admitted.status, ""


class PipeControlFixtureTest(unittest.TestCase):
    def test_pins_recipe_files_and_report_identity(self):
        for path, expected in ref.SOURCE_PINS.items():
            source = Path(ref.SOURCE_PIN_PATHS[path])
            if not source.is_file():
                self.skipTest(f"source pin not available locally: {path}")
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected)
        for name in ("recipe.json", "fallback_recipe.json", "report.json"):
            json.loads((HERE / name).read_text(encoding="ascii"))
        raw = json.loads((HERE / "recipe.json").read_text(encoding="ascii"))
        fallback = json.loads((HERE / "fallback_recipe.json").read_text(encoding="ascii"))
        self.assertEqual(ref.digest(ref.canonical_bytes(raw)), RECIPE_DIGEST)
        self.assertEqual(ref.digest(ref.canonical_bytes(fallback)), FALLBACK_RECIPE_DIGEST)
        self.assertEqual(ref.recipe_digest(ref.base_recipe()), RECIPE_DIGEST)
        self.assertEqual(ref.recipe_digest(ref.fallback_recipe()), FALLBACK_RECIPE_DIGEST)
        self.assertEqual(hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest(),
                         REPORT_DIGEST)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii").strip()
        self.assertEqual(sidecar, f"{REPORT_DIGEST}  report.json")

    def test_fixed_v0_format_and_admission(self):
        self.assertEqual(ref._FORMAT, {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160,
        })
        for raw in (ref.base_recipe(), ref.fallback_recipe()):
            _, status, reason = ref.validate_recipe(raw, ref.builtin_available())
            self.assertEqual((status, reason), (ref.Status.OK, ""))
        for key, value in (("sample_rate_hz", 48000), ("channels", 2),
                           ("frame_samples", 192), ("sample_format", "s16")):
            raw = ref.base_recipe()
            raw["format"][key] = value
            self.assertEqual(ref.validate_recipe(raw, ref.builtin_available())[1],
                             ref.Status.BAD_FORMAT)
        unknown = ref.base_recipe()
        unknown["stages"][0]["provider_id"] = "third_party.missing.v0"
        self.assertEqual(ref.validate_recipe(unknown, ref.builtin_available())[1],
                         ref.Status.UNAVAILABLE_STAGE)
        mismatch = ref.base_recipe()
        mismatch["stages"][0]["stage_id"] = "other"
        self.assertEqual(ref.validate_recipe(mismatch, ref.builtin_available())[1],
                         ref.Status.UNAVAILABLE_STAGE)
        duplicate = ref.base_recipe()
        duplicate["stages"].append(copy.deepcopy(duplicate["stages"][0]))
        duplicate["stages"][1]["output_port"] = "pcm.second.out"
        duplicate["audio_path"] = ["pcm.in", "pcm.identity.out", "pcm.second.out", "pcm.out"]
        self.assertEqual(ref.validate_recipe(duplicate, ref.builtin_available())[1],
                         ref.Status.DUPLICATE_INSTANCE)
        asset = ref.base_recipe()
        asset["assets"] = [{"id": "weights"}]
        self.assertEqual(ref.validate_recipe(asset, ref.builtin_available())[1],
                         ref.Status.BAD_FORMAT)

    def test_missing_stage_fails_admission_without_a_session(self):
        results = ref.run_ablations()
        self.assertEqual(results["control"]["status"], "ok")
        self.assertEqual(results["control"]["recipe_digest"], RECIPE_DIGEST)
        removed = results["identity_stage_removed"]
        self.assertEqual(removed["status"], "rejected_missing_stage")
        self.assertEqual(removed["reason"], "no_capture_stage")
        self.assertEqual(removed["sessions_created"], 0)
        missing = results["provider_unavailable"]
        self.assertEqual(missing["status"], "rejected_unavailable_stage")
        self.assertEqual(missing["sessions_created"], 0)
        raw = ref.base_recipe()
        raw["stages"] = []
        raw["audio_path"] = ["pcm.in", "pcm.out"]
        self.assertEqual(ref.validate_recipe(raw, ref.builtin_available())[1],
                         ref.Status.MISSING_STAGE)

    def test_bit_exact_baseline_and_partial_final_frame(self):
        run = ref.run_baseline()
        data = run.as_dict()
        self.assertTrue(data["bit_exact"])
        self.assertEqual(data["input_f32_digest"], INPUT_DIGEST)
        self.assertEqual(data["delivered_valid_f32_digest"], DELIVERED_DIGEST)
        self.assertEqual(data["produced_padded_f32_digest"], PADDED_DIGEST)
        self.assertEqual(data["frame_lengths"], ["160", "160", "37"])
        self.assertEqual(data["final_frame_flags"], "2")
        self.assertEqual(data["accepted_intervals"], data["delivered_intervals"])
        self.assertEqual(data["counters"]["accepted_samples"], "357")
        self.assertEqual(data["counters"]["delivered_valid_samples"], "357")
        self.assertEqual(data["counters"]["produced_samples"], "480")
        self.assertEqual(data["counters"]["submitted_frames"], "3")
        self.assertEqual(data["counters"]["eos_calls"], "1")
        self.assertEqual(data["terminal_status"], "closed")
        self.assertTrue(data["availability_monotonic"])

    def test_independent_sessions_and_new_epoch_provider_switch(self):
        run = ref.run_switch()
        data = run.as_dict()
        self.assertEqual(data["epoch_transition"], ["11", "12"])
        self.assertTrue(data["distinct_providers"])
        self.assertTrue(data["intervals_disjoint"])
        self.assertEqual(data["old_epoch_or_duplicate_samples_accepted"], 0)
        self.assertEqual(data["stale_epoch_attempt"], "rejected_stale_epoch")
        self.assertEqual(data["duplicate_frame_attempt"], "rejected_bad_frame")
        self.assertEqual(data["closed_session_attempt"], "rejected_closed")
        self.assertEqual(data["closed_session_pull"], "rejected_closed")
        self.assertEqual(data["session_a"]["delivered_f32_digest"], SWITCH_A_DIGEST)
        self.assertEqual(data["session_b"]["delivered_f32_digest"], SWITCH_B_DIGEST)
        self.assertEqual(data["combined_delivered_f32_digest"], COMBINED_DIGEST)
        self.assertEqual(data["combined_delivered_samples"], "714")
        self.assertEqual(data["session_a"]["recipe_digest"], RECIPE_DIGEST)
        self.assertEqual(data["session_b"]["recipe_digest"], FALLBACK_RECIPE_DIGEST)
        self.assertEqual(data["session_a"]["terminal_status"], "closed")
        self.assertEqual(data["session_b"]["terminal_status"], "closed")
        self.assertEqual(data["session_a"]["delivered_intervals"][2][1], "9007199254741350")
        self.assertEqual(data["session_b"]["delivered_intervals"][0][0], "9007199254741350")
        self.assertNotEqual(data["session_a"]["counters"],
                            data["session_b"]["counters"])

    def test_cancellation_and_fresh_epoch_fallback(self):
        run = ref.run_cancellation_fallback()
        data = run.as_dict()
        cancelled = data["cancelled_session"]
        self.assertEqual(cancelled["epoch"], "31")
        self.assertEqual(cancelled["samples"], "320")
        self.assertEqual(cancelled["intervals"], [["0", "160"], ["160", "320"]])
        for status in data["blocked_after_cancel"].values():
            self.assertEqual(status, "rejected_cancelled")
        fresh = data["fresh_session"]
        self.assertEqual(fresh["epoch"], "32")
        self.assertEqual(fresh["provider_id"], "third_party.fallback_identity.v0")
        self.assertEqual(fresh["delivered_intervals"], [["1000", "1160"]])
        self.assertEqual(fresh["counters"]["delivered_valid_samples"], "160")
        self.assertEqual(data["stale_provider_attempt"], "rejected_stale_epoch")
        self.assertEqual(data["old_epoch_samples_delivered"], 0)
        self.assertEqual(fresh["terminal_status"], "closed")

    def test_drain_close_and_lease_ordering(self):
        session, status, _ = fresh_session(epoch=91, first=0)
        self.assertEqual(status, ref.Status.OK)
        assert session is not None
        nonfinal = ref.make_frame(0, 7, 160, 0, 91)
        self.assertEqual(session.submit(nonfinal).status, ref.Status.OK)
        self.assertEqual(session.begin_drain().status, ref.Status.BAD_FRAME)
        self.assertEqual(session.drain_next().status, ref.Status.BAD_FRAME)
        self.assertEqual(session.close().status, ref.Status.BAD_FRAME)
        final = ref.make_frame(1, 7, 160, 160, 91, final=True)
        self.assertEqual(session.submit(final).status, ref.Status.OK)
        lease = session.pull()
        self.assertEqual(lease.status, ref.Status.OK)
        self.assertEqual(session.begin_drain().status, ref.Status.BUSY)
        self.assertEqual(session.drain_next().status, ref.Status.BUSY)
        assert lease.lease_id is not None
        self.assertEqual(session.release(lease.lease_id).status, ref.Status.OK)
        self.assertEqual(session.begin_drain().status, ref.Status.OK)
        self.assertEqual(session.submit(ref.make_frame(2, 7, 160, 320, 91)).status,
                         ref.Status.BAD_FRAME)
        tail = session.drain_next()
        self.assertEqual(tail.status, ref.Status.OK)
        assert tail.lease_id is not None
        self.assertEqual(session.release(tail.lease_id).status, ref.Status.OK)
        self.assertEqual(session.drain_next().status, ref.Status.END_OF_STREAM)
        self.assertEqual(session.drain_next().status, ref.Status.END_OF_STREAM)
        self.assertEqual(session.close().status, ref.Status.OK)
        self.assertEqual(session.close().status, ref.Status.OK)
        self.assertEqual(session.submit(ref.make_frame(0, 7, 160, 0, 91)).status,
                         ref.Status.CLOSED)

        forced, status, _ = fresh_session(epoch=92, first=0)
        self.assertEqual(status, ref.Status.OK)
        assert forced is not None
        self.assertEqual(forced.submit(ref.make_frame(0, 7, 160, 0, 92)).status,
                         ref.Status.OK)
        self.assertEqual(forced.close(force=True).status, ref.Status.OK)
        self.assertEqual(forced.cancellations[-1].reason, "forced_close_without_drain")
        self.assertEqual(forced.cancellations[-1].samples, 160)

    def test_queue_full_backpressure_and_no_drops(self):
        data = ref.run_buffer_control()
        self.assertEqual(data["queue_capacity"], "3")
        self.assertEqual(data["submit_statuses"], ["ok", "ok", "ok", "rejected_queue_full"])
        self.assertEqual(data["queue_full_rejection"], "rejected_queue_full")
        self.assertEqual(data["queue_depth_on_rejection"], "3")
        self.assertEqual(data["consumed_on_rejection"], "0")
        self.assertEqual(data["queue_high_water"], "3")
        self.assertEqual(data["accepted_frames"], "3")
        self.assertEqual(data["dropped_frames"], 0)
        self.assertEqual(data["forced_close_reason"], "forced_close_without_drain")

    def test_nonfinite_padding_and_invalid_metadata_controls(self):
        outcomes = ref.run_adverse_controls()
        expected = {
            "invalid_metadata_queue": "rejected_bad_format",
            "invalid_metadata_rate": "rejected_bad_format",
            "nonfinite_input": "rejected_nonfinite_input",
            "nonzero_final_padding": "rejected_bad_padding",
            "partial_without_final_input": "rejected_bad_frame",
            "process_after_final": "rejected_bad_frame",
            "short_frame": "rejected_bad_frame",
            "unknown_flags": "rejected_bad_frame",
            "wrong_epoch": "rejected_stale_epoch",
            "wrong_first_sample": "rejected_bad_frame",
        }
        self.assertEqual(outcomes, expected)
        self.assertEqual(load_report()["adverse_controls"], expected)
        self.assertTrue(all(isinstance(value, str) and value for value in outcomes.values()))

    def test_wrong_epoch_and_duplicate_samples_are_not_accepted(self):
        session, status, _ = fresh_session(epoch=101, first=0)
        self.assertEqual(status, ref.Status.OK)
        assert session is not None
        self.assertEqual(session.submit(ref.make_frame(0, 8, 160, 0, 101)).status,
                         ref.Status.OK)
        duplicate = ref.make_frame(0, 8, 160, 0, 101)
        self.assertEqual(session.submit(duplicate).status, ref.Status.BAD_FRAME)
        self.assertEqual(session.counters["accepted_samples"], 160)
        output = session.pull()
        assert output.lease_id is not None
        self.assertEqual(session.release(output.lease_id).status, ref.Status.OK)
        self.assertEqual(session.submit(ref.make_frame(0, 8, 160, 160, 100)).status,
                         ref.Status.STALE_EPOCH)
        self.assertEqual(session.counters["accepted_samples"], 160)

    def test_backend_failure_policy_and_reset(self):
        data = ref.run_failure_policy()
        self.assertEqual(data["failure"], "rejected_failing_port")
        self.assertEqual(data["failed_interval"], [["160", "320"]])
        self.assertEqual(data["failed_port"], "pcm.identity.out")
        self.assertEqual(data["state_after_failure"], "needs_reset")
        self.assertEqual(data["blocked_submit"], "rejected_needs_reset")
        self.assertEqual(data["blocked_drain"], "rejected_needs_reset")
        self.assertEqual(data["reset"], "ok")
        self.assertEqual(data["post_reset_submit"], "ok")
        self.assertEqual(data["epoch_transitions"][0]["to"], "62")

    def test_clock_declared_stage_cost_and_buffer_are_separate(self):
        report = load_report()
        baseline = report["baseline"]
        self.assertEqual(baseline["clock"][0], {
            "availability_ns": "1010025000", "frame_index": "0",
            "source_complete_ns": "1010000000", "stage_cost_ns": "25000",
        })
        self.assertEqual(baseline["clock"][2]["availability_ns"], "1030025000")
        timing = report["clock_and_timing"]
        self.assertEqual(timing["sample_period_ns"], "62500")
        self.assertEqual(timing["frame_period_ns"], "10000000")
        self.assertEqual(timing["declared_stage_cost_ns"], "25000")
        self.assertIsNone(timing["measured_stage_time_ns"])
        self.assertIsNone(timing["measured_end_to_end_availability_ns"])
        self.assertTrue(timing["stage_timing_independent_of_availability"])
        self.assertEqual(report["buffer"]["queue_high_water"], "3")

    def test_asset_scope_and_blocked_real_qualification(self):
        report = load_report()
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["qualification"], "incomplete")
        self.assertEqual(report["asset_scope"], {
            "downloads": False, "external_assets": 0, "licensed_runtimes": False,
            "model_free": True, "model_weights": False, "real_audio": False,
        })
        for name in ("paced_workload", "target_device", "physical_availability",
                     "listening_or_quality"):
            self.assertEqual(report["limits"][name], "blocked_not_measured")
        for section in ("ablations", "failure_policy", "adverse_controls", "buffer"):
            self.assertTrue(report[section])
        self.assertEqual(report["counts"]["baseline_accepted_samples"], "357")
        self.assertEqual(report["counts"]["switch_accepted_samples"], "714")

    def test_report_is_canonical_and_reproducible(self):
        import generate_report

        original = (HERE / "report.json").read_bytes()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii").strip()
        with tempfile.TemporaryDirectory(prefix="sdk-pipe-report-") as temp:
            target = generate_report.write_report(Path(temp))
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual((target.parent / "report.json.sha256").read_text(
                encoding="ascii").strip(), sidecar)
        text = ref.canonical_bytes(ref.build_report()).decode("ascii")
        self.assertEqual(text.encode("ascii"), original)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)

    def test_installed_external_consumer(self):
        with tempfile.TemporaryDirectory(prefix="sdk-pipe-control-") as temp:
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
            env = os.environ.copy()
            env.update({
                "PYTHONPATH": os.pathsep.join((str(install), str(HERE))),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            })
            outputs = []
            for _ in range(2):
                completed = subprocess.run(
                    [sys.executable, str(HERE / "third_party" / "consumer_probe.py"),
                     str(install), str(HERE)],
                    cwd=root, env=env, capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                outputs.append(completed.stdout)
            self.assertEqual(outputs[0], outputs[1])
            record = json.loads(outputs[0])
            self.assertTrue(record["installed"])
            self.assertEqual(record["fixture_id"], "third-party/pipe-control-fixture/0.1")
            self.assertEqual(record["fixture_source_digest"], FIXTURE_SOURCE_DIGEST)
            self.assertEqual(record["recipe_digest"], RECIPE_DIGEST)
            self.assertEqual(record["fallback_recipe_digest"], FALLBACK_RECIPE_DIGEST)
            self.assertEqual(record["input_f32_digest"], INPUT_DIGEST)
            self.assertEqual(record["delivered_valid_f32_digest"], DELIVERED_DIGEST)
            self.assertEqual(record["combined_delivered_f32_digest"], COMBINED_DIGEST)
            self.assertEqual(record["accepted_samples"], "357")
            self.assertEqual(record["delivered_valid_samples"], "357")
            self.assertEqual(record["report_digest"], REPORT_DIGEST)
            self.assertEqual(record["status"], "proposal_only_synthetic_incomplete")


if __name__ == "__main__":
    unittest.main()
