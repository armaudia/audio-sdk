# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the offline multichannel WPE evidence package.

Run with the pinned Python 3.12 interpreter and no network:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import unittest

import reference as fx
import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
DIGEST = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"


def strict_json(path: Path):
    def reject(value: str) -> None:
        raise ValueError("nonfinite JSON " + value)

    payload = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(payload, (dict, list)):
        raise ValueError("expected JSON object or array")
    return payload


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)
        cls.generated, cls.digest = fx.canonical_report(fx.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_text(encoding="utf-8"))
        self.assertEqual(self.digest, hashlib.sha256(REPORT.read_bytes()).hexdigest())
        self.assertEqual(DIGEST.read_text(encoding="utf-8").strip(), self.digest)

    def test_02_status_profile_and_opt_in_boundary(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        provider = self.report["provider"]
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["default_enabled"])
        self.assertFalse(provider["c_abi_or_sdk_default_change"])
        self.assertEqual(provider["descriptor_settings"], {})
        fmt = self.report["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"]),
                         (16000, 2, "f32", 160))
        self.assertFalse(fmt["realtime_v0_provider"])
        self.assertEqual(fmt["content_delay_samples"], 0)

    def test_03_all_required_results_present(self) -> None:
        required = self.report["qualification"]["required_results"]
        self.assertTrue(required, f"missing: {[k for k, v in required.items() if not v]}")
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertTrue(self.report["qualification"]["no_missing_result_may_qualify"])

    def test_04_source_and_boundary_pins_match_committed_bytes(self) -> None:
        for relative, expected in {**fx.SOURCE_PINS, **fx.BOUNDARY_PINS}.items():
            with self.subTest(path=relative):
                path = SOURCE_ROOT / relative
                if not path.is_file():
                    path = SDK_ROOT / relative
                self.assertTrue(path.is_file(), f"missing {relative}")
                self.assertEqual(fx.file_digest(path), expected)

    def test_05_manifest_covers_every_task_artifact_and_pin(self) -> None:
        lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        paths = set()
        for line in lines:
            digest, raw_path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            paths.add(raw_path)
        for name in fx.LOCAL_ARTIFACTS + fx.GENERATED_ARTIFACTS:
            self.assertIn(name, paths)
        for name in fx.SOURCE_PINS:
            self.assertIn("source:" + name, paths)
        for name in fx.BOUNDARY_PINS:
            self.assertIn("worktree:" + name, paths)
        for line in lines:
            digest, raw_path = line.split("  ", 1)
            if ":" in raw_path:
                kind, relative = raw_path.split(":", 1)
                root = SOURCE_ROOT if kind == "source" else SDK_ROOT
            else:
                relative, root = raw_path, HERE
            path = root / relative
            self.assertTrue(path.is_file(), f"missing {raw_path}")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_06_scorer_crosscheck_vectors_are_finite_and_close(self) -> None:
        vectors = fx.load_crosscheck_vectors()
        self.assertEqual(len(vectors), 6)
        for vector in vectors:
            with self.subTest(name=vector["name"]):
                self.assertLess(vector["stoi_abs_delta"], 1e-12)
                self.assertLess(vector["si_sdr_abs_delta"], 1e-12)
        self.assertEqual(self.report["scorer"]["crosscheck_vectors_digest"],
                         fx.object_digest(vectors))

    def test_07_spdx_headers_and_scope(self) -> None:
        for name in ("reference.py", "scorer.py", "run.py", "verify.py", "test_reference.py"):
            with self.subTest(path=name):
                head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:4])
                self.assertIn("SPDX" "-License-Identifier: Apache-2.0", head)
                self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes", head)
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
            capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if line[:2].strip() else line
            self.assertTrue(path.startswith("docs/task-evidence/offline-multichannel-wpe/"))

    def test_08_no_trailing_whitespace_in_new_files(self) -> None:
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".sha256"}:
                with self.subTest(path=path.name):
                    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                        self.assertEqual(line, line.rstrip(),
                                         f"trailing whitespace {path.name}:{number}")


class DeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_09_generators_are_repeatable(self) -> None:
        first = fx.clean_source()
        self.assertEqual(fx.tensor_digest(first), fx.tensor_digest(fx.clean_source()))
        rir = fx.room_rirs("medium_rt60")[0]
        self.assertEqual(fx.tensor_digest(rir), fx.tensor_digest(fx.room_rirs("medium_rt60")[0]))
        self.assertEqual(len(rir), 551)

    def test_10_whole_clip_processing_is_byte_repeatable(self) -> None:
        probe = fx.probe_channels()
        digests = {fx.channels_digest(fx.process_whole_clip(probe)[1]) for _ in range(3)}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), self.report["repeatability"]["output_digests"][0])

    def test_11_whole_clip_and_chunked_are_identical(self) -> None:
        state = self.report["alignment_and_state"]["chunking_equivalence"]
        self.assertTrue(state["equal"])
        self.assertEqual(state["stream_digest"], state["chunked_digest"])
        self.assertEqual(state["status"], "ok")

    def test_12_synthetic_geometry_is_frozen(self) -> None:
        self.assertEqual(fx.channel_delays(fx.ROOM_SPECS["short_rt60"]), (0, 2))
        self.assertEqual(fx.ROOM_SPECS["short_rt60"]["rt60_ms"], 250)
        self.assertEqual(fx.ROOM_SPECS["long_rt60"]["rt60_ms"], 900)
        self.assertEqual(fx.EARLY_WINDOW_MS, 50)
        self.assertEqual((fx.FFT_SIZE, fx.HOP_SAMPLES, fx.WPE_DELAY_FRAMES, fx.WPE_TAPS),
                         (512, 160, 2, 3))


class BoundaryAndFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_13_config_validation_rejects_bad_inputs(self) -> None:
        errors = self.report["adverse"]["config_rejections"]
        self.assertEqual(errors["missing_key"]["status"], "rejected_missing")
        self.assertEqual(errors["none"]["status"], "rejected_missing")
        for label in ("unknown_key", "out_of_range", "wrong_type", "bad_stft_geometry",
                      "bad_iterations", "wrong_channel_count"):
            self.assertEqual(errors[label]["status"], "rejected_invalid")
            self.assertFalse(errors[label]["controller_created"])
        self.assertEqual(errors["nonfinite"]["status"], "rejected_nonfinite")

    def test_14_frame_rejections_do_not_change_dsp_state(self) -> None:
        frames = self.report["adverse"]["frame_rejections"]
        self.assertTrue(frames["dsp_state_unchanged"])
        self.assertEqual(frames["invalid_count_delta"], 6)
        self.assertEqual(frames["nonfinite"], "rejected_nonfinite")
        self.assertEqual(frames["wrong_shape"], "rejected_tensor")
        self.assertEqual(frames["stale_session"], "rejected_session")
        self.assertEqual(frames["stale_epoch"], "rejected_epoch")
        self.assertEqual(frames["stale_position"], "rejected_position")
        self.assertEqual(frames["finalize_status"], "ok")
        self.assertEqual(frames["finished_reuse"], "rejected_session")
        self.assertEqual(frames["process_after_finish"], "rejected_session")

    def test_15_lifecycle_rejections_are_explicit(self) -> None:
        controller = fx.OfflineController()
        chunk = fx._chunks_of(fx.probe_channels(), [160] * 6)[0]
        self.assertEqual(controller.process(chunk).status, fx.Status.OK)
        controller.close()
        self.assertEqual(controller.process(chunk).status, fx.Status.CLOSED)
        self.assertEqual(controller.finish().status, fx.Status.CLOSED)
        self.assertEqual(controller.reset(2, 0).status, fx.Status.CLOSED)

    def test_16_missing_nonfinite_and_zero_reference_are_blocked(self) -> None:
        adverse = self.report["adverse"]
        self.assertEqual(adverse["missing_reference"]["reason"], "missing_reference")
        self.assertIsNone(adverse["missing_reference"]["metrics"])
        self.assertEqual(adverse["nonfinite_reference"]["reason"], "shape_mismatch")
        self.assertEqual(adverse["zero_reference"]["reason"], "shape_mismatch")

    def test_17_nonfinite_wpe_input_is_rejected(self) -> None:
        channels = fx.probe_channels()
        bad = tuple(tuple(float("nan") for _ in row) for row in channels)
        status, output = fx.process_whole_clip(bad)
        self.assertEqual(status, fx.Status.REJECTED_NONFINITE)
        self.assertEqual(output, ())
        with self.assertRaises(ArithmeticError):
            fx.no_reference_suppressor(bad)
        self.assertEqual(self.report["adverse"]["silent_input"]["status"], "ok")


class RoomProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_18_all_frozen_room_conditions_scored(self) -> None:
        for name, condition in self.report["conditions"].items():
            with self.subTest(condition=name):
                for label in ("identity_control", "mc_wpe_candidate",
                              "noisy_identity_control", "mc_wpe_on_noisy"):
                    self.assertEqual(condition["variants"][label]["status"], "scored")
                self.assertGreater(condition["early_target_window_samples"], 0)
                self.assertEqual(len(condition["rir_digests"]), 2)
                self.assertEqual(len(condition["channel_delays_samples"]), 2)

    def test_19_echo_and_near_end_damage_reported(self) -> None:
        for name, condition in self.report["conditions"].items():
            with self.subTest(condition=name):
                candidate = condition["variants"]["mc_wpe_candidate"]["metrics"]
                self.assertIsInstance(candidate["delta_si_sdr_db"], (int, float))
                self.assertIsInstance(candidate["delta_stoi"], (int, float))
        preservation = self.report["clean_near_end_preservation"]
        self.assertEqual(preservation["mc_wpe_candidate"]["status"], "scored")
        self.assertFalse(preservation["mc_wpe_candidate"]["identity_is_bit_exact"])

    def test_20_movement_and_overlap_cases_scored(self) -> None:
        special = self.report["special_conditions"]
        for name in ("movement_long", "overlap_long"):
            with self.subTest(condition=name):
                for row in special[name]["variants"].values():
                    self.assertEqual(row["status"], "scored")
        self.assertEqual(self.report["special_conditions"]["overlap_long"][
            "second_source_delay_samples"], fx.SECOND_SOURCE_DELAY_SAMPLES)

    def test_21_no_reference_suppressor_has_independent_comparison(self) -> None:
        section = self.report["no_reference_suppressor"]
        self.assertFalse(section["algorithm_uses_reference"])
        self.assertFalse(section["algorithm_uses_rir"])
        self.assertFalse(section["algorithm_uses_wpe_output"])
        for name, row in section["conditions"].items():
            with self.subTest(condition=name):
                self.assertEqual(row["variants"]["identity_control"]["status"], "scored")
                score = row["variants"]["no_ref_suppressor"]
                self.assertEqual(score["status"], "scored")
                self.assertNotEqual(row["output_digest"], row["input_digest"])
                comparison = section["comparisons"][name]
                self.assertEqual(comparison[
                    "suppressor_minus_identity_delta_si_sdr_db"], score["metrics"][
                        "delta_si_sdr_db"])
                self.assertIn("separately_reported_wpe_delta_si_sdr_db", comparison)
        self.assertIsInstance(section["regressions"], list)

    def test_22_delayed_and_missing_render_gate_is_blocked(self) -> None:
        adverse = self.report["adverse"]["delayed_or_missing_render"]
        self.assertEqual(adverse["status"], "blocked")
        self.assertIn("no separate render", adverse["reason"])
        self.assertTrue(adverse["reopen"])
        gates = self.report["qualification"]["remaining_gates"]
        self.assertTrue(any("delayed/missing" in gate.lower() or "render" in gate.lower()
                            for gate in gates))

    def test_23_alignment_impulse_silence_and_partial_frame(self) -> None:
        state = self.report["alignment_and_state"]
        self.assertEqual(state["impulse"]["status"], "ok")
        self.assertEqual(state["impulse"]["content_delay_samples"], 0)
        self.assertEqual(state["silence"]["status"], "ok")
        self.assertTrue(state["duration"]["equal"])
        partial = state["partial_final_frame"]
        self.assertEqual(partial["status"], "ok")
        self.assertEqual(partial["input_samples"], partial["output_samples"])
        self.assertEqual(partial["chunk_sizes"][-1], 37)

    def test_24_state_isolation_reset_and_off_on_probe(self) -> None:
        state = self.report["alignment_and_state"]
        self.assertTrue(state["session_independence"]["independent"])
        reset = state["reset"]
        self.assertEqual(reset["status"], "ok")
        self.assertEqual(reset["stale_epoch_status"], "rejected_epoch")
        self.assertEqual(reset["stale_position_status"], "rejected_position")
        self.assertTrue(reset["replay_matches_original"])
        probe = self.report["provider"]["off_on_probe"]
        self.assertTrue(probe["off_is_bit_exact_identity"])
        self.assertTrue(probe["on_differs_from_off"])

    def test_25_outputs_finite_and_bounded(self) -> None:
        for name, condition in self.report["conditions"].items():
            for label, variant in condition["variants"].items():
                with self.subTest(condition=name, variant=label):
                    self.assertEqual(variant["nonfinite_count"], 0)
                    self.assertEqual(variant["clipping_count"], 0)
                    self.assertLess(variant["peak_abs"], 1.0)
        for row in self.report["no_reference_suppressor"]["conditions"].values():
            self.assertEqual(row["variants"]["no_ref_suppressor"]["nonfinite_count"], 0)

    def test_26_noncausal_disclosure_and_no_oracle(self) -> None:
        control = self.report["noncausal_control"]
        self.assertTrue(control["whole_clip_noncausal"])
        self.assertFalse(control["real_time_claim"])
        self.assertFalse(control["used_as_candidate_oracle"])
        self.assertFalse(control["online_acceptance_threshold"])
        self.assertFalse(control["provider_substitution"])
        for row in self.report["scope_comparison"].values():
            self.assertIn("no row is an oracle", row["note"])

    def test_27_all_json_files_strict_and_finite(self) -> None:
        for name in ("contract.json", "adapter.json", "provider.json",
                     "crosscheck_vectors.json", "report.json"):
            with self.subTest(path=name):
                payload = strict_json(HERE / name)
                self.assertTrue(isinstance(payload, (dict, list)))
        for name in ("contract.json", "adapter.json", "provider.json"):
            payload = strict_json(HERE / name)
            self.assertIn("schema_id", payload)


if __name__ == "__main__":
    unittest.main()
