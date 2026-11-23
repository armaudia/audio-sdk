# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local deterministic tests for the SDK-PIPE-DUPLEX frozen host example.

Run with:
    python3 -m unittest discover -s docs/task-evidence/pipe-duplex -p 'test_*.py' -v

Set PIPE_DUPLEX_MDF_CLI to the merged, opt-in mdf_reference_cli to include the
native CLI checks. No fixture, output or build byte is written into the
worktree by these tests.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import unittest
from pathlib import Path

import host


HERE = Path(__file__).resolve().parent
CLI = Path(os.environ.get("PIPE_DUPLEX_MDF_CLI", "")).resolve() if os.environ.get("PIPE_DUPLEX_MDF_CLI") else None
SCRATCH = Path(os.environ.get("PIPE_DUPLEX_TEST_WORK",
                              "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/pipe-duplex/tests"))


class FrozenFilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recipe = host.load_json("recipe.json")
        cls.fixtures = host.load_json("fixtures.json")
        cls.report = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
        cls.sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii").split()[0]

    def test_recipe_and_fixture_schemas(self) -> None:
        self.assertEqual(self.recipe["schema_id"], host.SCHEMA)
        self.assertEqual(self.fixtures["schema_id"], "audio-sdk/pipe-duplex/fixtures/0.1")
        self.assertEqual(self.recipe["task"], "SDK-PIPE-DUPLEX")

    def test_recipe_validates_against_fixtures(self) -> None:
        self.assertEqual(host.validate_recipe(self.recipe, self.fixtures), (True, "ok"))

    def test_default_on_recipe_rejected(self) -> None:
        changed = json.loads(json.dumps(self.recipe))
        changed["activation"]["default_enabled"] = True
        self.assertEqual(host.validate_recipe(changed, self.fixtures)[0], False)

    def test_unknown_provider_rejected(self) -> None:
        changed = json.loads(json.dumps(self.recipe))
        changed["variants"]["duplex_base"]["nodes"][0]["provider_id"] = "unknown.v0"
        self.assertFalse(host.validate_recipe(changed, self.fixtures)[0])

    def test_all_source_pins_verified(self) -> None:
        pins = host.check_pins(self.fixtures)
        self.assertGreaterEqual(len(pins), 25)
        self.assertTrue(all(pin["verified"] for pin in pins))

    def test_dependency_and_oracle_pins_verified(self) -> None:
        deps = host.check_dependency_pins(self.fixtures)
        for key, value in deps.items():
            if key.endswith("_verified"):
                self.assertTrue(value, key)
        self.assertEqual(deps["version"], "1.2.1")
        self.assertEqual(deps["revision"], "7a158783df74efe7c2d1c6ee8363c1e695c71226")

    def test_tampered_pin_manifest_rejected(self) -> None:
        changed = json.loads(json.dumps(self.fixtures))
        changed["source_pins"][0]["sha256"] = self.fixtures["controls"]["tampered_pin_prefix"]
        self.assertFalse(all(pin["verified"] for pin in host.check_pins(changed)))

    def test_frozen_report_sidecar_and_digests(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), self.sidecar)
        self.assertEqual(self.report["recipe_digest"], host.canonical_digest(self.recipe))
        self.assertEqual(self.report["fixtures_digest"], host.canonical_digest(self.fixtures))

    def test_frozen_report_all_checks_pass(self) -> None:
        self.assertTrue(self.report["all_checks_pass"])
        for name, passed in self.report["comparisons"].items():
            self.assertTrue(passed, name)
        self.assertTrue(self.report["controls"]["all_expected"])

    def test_frozen_report_three_identical_repeats(self) -> None:
        repeats = self.report["repeat_runs"]
        self.assertEqual(repeats["three_repeats"], 3)
        self.assertEqual(len(set(repeats["canonical_digests"])), 1)
        self.assertTrue(repeats["byte_identical"])

    def test_frozen_report_scope_and_change_counts(self) -> None:
        scope = self.report["change_scope"]
        self.assertTrue(scope["task_local_files_only"])
        self.assertEqual(scope["cmake_ci_edits"], 0)
        self.assertEqual(scope["abi_or_default_changes"], 0)
        self.assertEqual(scope["provider_substitutions"], [])
        self.assertEqual(scope["tolerance_widening"], [])
        self.assertFalse(scope["scratch_audio_and_build_bytes_committed"])


class FixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = host.load_json("fixtures.json")
        cls.streams = host.generate_streams(cls.fixtures)
        cls.expected = cls.fixtures["merged_oracle_expectations"]

    def test_stream_shape_and_finite_range(self) -> None:
        self.assertEqual(len(self.streams), len(self.fixtures["cases"]))
        for case in self.streams.values():
            for key in ("render", "capture", "near"):
                values = case[key]
                self.assertEqual(len(values), 48000)
                self.assertTrue(all(math.isfinite(value) and abs(value) <= 1.0 for value in values))

    def test_baseline_render_and_capture_digests_match_merged_oracle(self) -> None:
        for name in ("echo_only", "content_skew_undetected"):
            case = self.streams[name]
            self.assertEqual(host.digest_samples(case["render"]), self.expected[name]["render_digest"])
            self.assertEqual(host.digest_samples(case["capture"]), self.expected[name]["capture_digest"])

    def test_overlap_and_near_capture_digests_match_merged_oracle(self) -> None:
        for name in ("double_talk_overlap", "near_end_only"):
            self.assertEqual(host.digest_samples(self.streams[name]["capture"]),
                             self.expected[name]["capture_digest"])

    def test_stimulus_is_reproducible(self) -> None:
        again = host.generate_streams(self.fixtures)
        for name in ("echo_only", "double_talk_overlap", "near_end_only"):
            self.assertEqual(host.digest_samples(again[name]["capture"]),
                             host.digest_samples(self.streams[name]["capture"]))

    @unittest.skipUnless(CLI is not None and CLI.is_file(),
                         "set PIPE_DUPLEX_MDF_CLI to an opt-in built merged MDF CLI")
    def test_exact_metric_helpers(self) -> None:
        case = self.streams["echo_only"]
        out, _ = host.run_mdf(CLI,
                              SCRATCH / "metric-helper",
                              "metric", case["render"], case["capture"])
        window = self.fixtures["stimulus"]["converged_window_frames"]
        self.assertEqual(host.erle_db(case["capture"], out, window), 16.453939)

    def test_valid_timeline_does_not_change_render_bytes(self) -> None:
        timeline = host.build_timeline(self.fixtures, "echo_only", self.streams)
        self.assertEqual(timeline["reference_decision"], "duplex")
        self.assertEqual(host.digest_samples(timeline["aligned_render"]),
                         host.digest_samples(self.streams["echo_only"]["render"]))

    def test_reference_starvation_forces_capture_only(self) -> None:
        for name in ("render_dropout", "reference_absent"):
            timeline = host.build_timeline(self.fixtures, name, self.streams)
            self.assertEqual(timeline["reference_decision"], "capture_only")
            self.assertIn("reference_starvation", timeline["reasons"])

    def test_stale_reference_forces_capture_only(self) -> None:
        timeline = host.build_timeline(self.fixtures, "reference_stale", self.streams)
        self.assertEqual(timeline["reference_decision"], "capture_only")
        self.assertIn("stale_reference", timeline["reasons"])

    def test_positive_skew_is_repaired_not_rejected(self) -> None:
        timeline = host.build_timeline(self.fixtures, "skew_timestamp_repair", self.streams)
        self.assertEqual(timeline["reference_decision"], "duplex")
        self.assertEqual(timeline["classification"]["timestamp_skew_repaired_frames"], 200)
        self.assertEqual(host.digest_samples(timeline["aligned_render"]),
                         host.digest_samples(self.streams["echo_only"]["render"]))

    def test_nonmonotonic_timestamps_rejected(self) -> None:
        frames = [
            {"index": 0, "timestamp_ns": host.ORIGIN_NS, "present": True},
            {"index": 1, "timestamp_ns": host.ORIGIN_NS, "present": True},
        ]
        result = host.classify_reference_frames(frames, self.fixtures)
        self.assertIn("nonmonotonic_timestamps", result["reasons"])
        self.assertEqual(result["reference_decision"], "capture_only")


class StageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recipe = host.load_json("recipe.json")
        cls.fixtures = host.load_json("fixtures.json")
        cls.streams = host.generate_streams(cls.fixtures)

    def test_identity_stage_is_bit_exact(self) -> None:
        capture = self.streams["echo_only"]["capture"]
        timeline = host.build_timeline(self.fixtures, "echo_only", self.streams)
        out, _ = host.apply_variant(self.recipe, "identity", capture,
                                    timeline["aligned_render"], timeline["render_activity"],
                                    None, timeline)
        self.assertEqual(host.digest_samples(out), host.digest_samples(capture))

    def test_capture_chain_stages_are_finite_full_length(self) -> None:
        capture = self.streams["echo_only"]["capture"]
        timeline = host.build_timeline(self.fixtures, "echo_only", self.streams)
        for name in ("capture_only", "capture_residual"):
            out, _ = host.apply_variant(self.recipe, name, capture,
                                        timeline["aligned_render"], timeline["render_activity"],
                                        None, timeline)
            self.assertEqual(len(out), 48000)
            self.assertTrue(all(math.isfinite(value) for value in out))

    def test_limiter_never_exceeds_declared_ceiling(self) -> None:
        capture = self.streams["echo_only"]["capture"]
        timeline = host.build_timeline(self.fixtures, "echo_only", self.streams)
        out, _ = host.apply_variant(self.recipe, "capture_only", capture,
                                    timeline["aligned_render"], timeline["render_activity"],
                                    None, timeline)
        self.assertLessEqual(max(abs(value) for value in out), 0.98 + 1e-9)

    def test_residual_surrogate_requires_reference(self) -> None:
        timeline = host.build_timeline(self.fixtures, "reference_absent", self.streams)
        with self.assertRaises(host.ControlError) as raised:
            host.apply_variant(self.recipe, "capture_residual",
                               self.streams["reference_absent"]["capture"],
                               timeline["aligned_render"], timeline["render_activity"],
                               None, timeline)
        self.assertIn("residual_without_reference", str(raised.exception))

    def test_residual_surrogate_toggle_is_independent(self) -> None:
        report = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
        echo = report["cases"]["echo_only"]["variants"]
        self.assertNotEqual(echo["duplex_base"]["output_digest"],
                            echo["duplex_residual"]["output_digest"])
        self.assertGreater(echo["duplex_residual"]["suppressed_frames"], 0)
        self.assertEqual(echo["duplex_base"]["suppressed_frames"], 0)


@unittest.skipUnless(CLI is not None and CLI.is_file(),
                     "set PIPE_DUPLEX_MDF_CLI to an opt-in built merged MDF CLI")
class MdfCliTest(unittest.TestCase):
    def test_cli_self_test(self) -> None:
        import subprocess
        result = subprocess.run([str(CLI), "--self-test"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("SELFTEST OK", result.stdout)

    def test_echo_only_matches_merged_oracle_bytes(self) -> None:
        fixtures = host.load_json("fixtures.json")
        streams = host.generate_streams(fixtures)
        case = streams["echo_only"]
        _, payload = host.run_mdf(CLI, SCRATCH / "oracle-echo", "echo",
                                  case["render"], case["capture"])
        self.assertEqual(host.sha256(payload),
                         fixtures["merged_oracle_expectations"]["echo_only"]["mdf_output_digest"])

    def test_content_skew_matches_merged_oracle_bytes(self) -> None:
        fixtures = host.load_json("fixtures.json")
        streams = host.generate_streams(fixtures)
        case = streams["content_skew_undetected"]
        _, payload = host.run_mdf(CLI, SCRATCH / "oracle-skew", "skew",
                                  case["render"], case["capture"])
        self.assertEqual(host.sha256(payload), fixtures["merged_oracle_expectations"][
            "content_skew_undetected"]["mdf_output_digest"])

    def test_zero_render_is_bit_exact_passthrough(self) -> None:
        fixtures = host.load_json("fixtures.json")
        streams = host.generate_streams(fixtures)
        case = streams["near_end_only"]
        _, payload = host.run_mdf(CLI, SCRATCH / "oracle-zero", "zero",
                                  case["render"], case["capture"])
        self.assertEqual(host.sha256(payload), host.digest_samples(case["capture"]))

    def test_frozen_report_reproduces_exactly(self) -> None:
        import subprocess
        result = subprocess.run(
            ["python3", "generate_report.py", "--cli", str(CLI), "--work",
             str(SCRATCH / "frozen-check")], cwd=HERE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("report_sha256=" + (HERE / "report.json.sha256").read_text(
            encoding="ascii").split()[0], result.stdout)


if __name__ == "__main__":
    unittest.main()
