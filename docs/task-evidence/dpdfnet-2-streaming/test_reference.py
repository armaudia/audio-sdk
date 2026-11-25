# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the DPDFNet-2 streaming evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import unittest
from pathlib import Path

import reference
import run as cli
import verify

HERE = Path(__file__).resolve().parent
SDK_ROOT = reference.SDK_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
TASK_PREFIX = reference.TASK_PREFIX


def strict_json(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise AssertionError(f"duplicate JSON key in {path.name}: {key}")
            result[key] = value
        return result

    def constant(token):
        raise AssertionError(f"nonfinite JSON constant in {path.name}: {token}")

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = strict_json(REPORT)
        cls.contract = strict_json(HERE / "contract.json")
        cls.adapter = strict_json(HERE / "adapter.json")
        cls.readiness = strict_json(HERE / "readiness.json")
        cls.generated = reference.canonical_report_bytes(reference.build_report())
        cls.digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()

    def test_01_report_regenerates_byte_identically(self):
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self):
        self.assertEqual(SIDECAR.read_text(encoding="utf-8").strip(),
                         f"{self.digest}  report.json")

    def test_03_manifest_regenerates_byte_identically(self):
        self.assertEqual(PINS.read_bytes(), cli.manifest_bytes())

    def test_04_manifest_is_fail_closed(self):
        manifest = verify.read_manifest()
        self.assertEqual(set(manifest), verify.manifest_expected_paths())
        self.assertNotIn(f"worktree:{TASK_PREFIX}SOURCES.sha256", manifest)

    def test_05_all_json_is_strict(self):
        for path in sorted(HERE.glob("*.json")):
            self.assertIsInstance(strict_json(path), dict)

    def test_06_status_qualification_and_decision(self):
        self.assertEqual(self.report["status"], reference.STATUS)
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_07_boundary_is_unregistered_and_default_off(self):
        self.assertEqual(self.report["boundary"], reference.BOUNDARY)
        self.assertFalse(self.report["boundary"]["registered"])
        self.assertFalse(self.report["boundary"]["enabled_by_default"])
        self.assertFalse(self.report["boundary"]["processor_exposure"])

    def test_08_public_v0_geometry_is_unchanged(self):
        self.assertEqual(self.report["format"], reference.FORMAT)
        self.assertEqual(self.report["format"]["sample_rate_hz"], 16000)
        self.assertEqual(self.report["format"]["channels"], 1)
        self.assertEqual(self.report["format"]["sample_format"], "f32")
        self.assertEqual(self.report["format"]["frame_samples"], 160)

    def test_09_report_has_required_sections(self):
        for key in ("schema_id", "task_id", "base_commit", "branch", "profile",
                    "conditions", "controls", "regressions", "streaming_boundary",
                    "asset_boundary", "enhancement_profile", "adverse",
                    "repeatability", "gates", "exact_blockers",
                    "reopen_conditions", "missing_evidence", "claims"):
            self.assertIn(key, self.report)

    def test_10_base_commit_and_branch_pinned(self):
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["branch"], reference.BRANCH)
        self.assertEqual(self.report["task_id"], "SDK-DPDFNET-2-STREAMING")

    def test_11_all_conditions_scored(self):
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, block in self.report["conditions"].items():
            self.assertEqual(block["scored_samples"], 32000)
            self.assertEqual(block["tail_validity"]["raw_output_samples"], 32640)
            for variant in block["variants"].values():
                self.assertEqual(variant["nonfinite_samples"], 0)
                self.assertEqual(variant["clipped_samples"], 0)
                self.assertTrue(math.isfinite(variant["peak_abs_output"]))

    def test_12_identity_and_noisy_controls_match(self):
        for block in self.report["conditions"].values():
            identity = block["variants"]["identity_passthrough"]
            noisy = block["variants"]["noisy_control"]
            self.assertTrue(identity["exact_passthrough"])
            self.assertEqual(identity["snr_db"], noisy["snr_db"])
            self.assertEqual(identity["si_sdr_db"], noisy["si_sdr_db"])

    def test_13_chunk_size_invariance(self):
        cross = self.report["streaming_boundary"]["chunk_invariance"]
        self.assertTrue(cross["raw_chunk_invariant"])
        self.assertTrue(cross["compensated_chunk_invariant"])
        self.assertTrue(cross["whole_call_matches_chunked"])
        self.assertEqual(set(cross["chunk_sizes_tested"]), set(reference.CHUNK_SIZES))
        for record in cross["records"].values():
            self.assertEqual(record["raw_length"], 32640)
            self.assertEqual(record["valid_samples"], 32000)
            self.assertEqual(record["emitted_before_flush"] + record["flush_emitted"],
                             record["raw_length"])

    def test_14_modelled_lag_alignment(self):
        probe = self.report["streaming_boundary"]["alignment_probe"]
        self.assertEqual(probe["declared_lag_samples"], 640)
        self.assertEqual(probe["raw_peak_sample"], 4640)
        self.assertEqual(probe["raw_lag_samples"], 640)
        self.assertEqual(probe["compensated_peak_sample"], 4000)
        self.assertEqual(probe["residual_lag_samples"], 0)
        self.assertFalse(probe["measured_latency"])

    def test_15_output_accounting_exact(self):
        for block in self.report["conditions"].values():
            tail = block["tail_validity"]
            self.assertEqual(tail["raw_output_samples"],
                             tail["input_samples"] + 640
                             + tail["internal_frame_padding_samples"])
            self.assertEqual(tail["valid_samples"], tail["input_samples"])
            self.assertEqual(tail["startup_padding_samples"], 640)
            self.assertEqual(tail["truncated_tail_padding_samples"], 640)

    def test_16_stream_state_and_reset(self):
        state = self.report["streaming_boundary"]["state"]
        self.assertEqual(state["frames_processed"], 200)
        self.assertTrue(state["reset_replay_identical"])
        self.assertTrue(state["independent_session_identical"])
        self.assertTrue(state["cross_stream_reset_identical"])
        self.assertFalse(state["real_recurrent_state_loaded"])
        self.assertTrue(state["state_is_synthetic"])

    def test_17_config_adverse_cases_fail_closed(self):
        cases = self.report["adverse"]["config_rejections"]
        self.assertEqual(cases["caller_asset_admission_control"]["status"], "created")
        for name, case in cases.items():
            if name == "caller_asset_admission_control":
                continue
            self.assertEqual(case["status"], "rejected", name)
            self.assertFalse(case["session_created"], name)
            self.assertTrue(case["reason_codes"], name)

    def test_18_frame_cases_fail_closed_without_state_change(self):
        cases = self.report["adverse"]["frame_cases"]["cases"]
        self.assertTrue(cases)
        for name, case in cases.items():
            self.assertTrue(case["status"].startswith("rejected"), name)
            self.assertTrue(case["state_unchanged"], name)
        self.assertTrue(self.report["adverse"]["frame_cases"]["flush_idempotent"])
        self.assertTrue(self.report["adverse"]["frame_cases"][
            "state_after_close_unchanged_by_rejected_calls"])

    def test_19_lifecycle_fail_closed(self):
        lifecycle = self.report["adverse"]["lifecycle"]
        self.assertTrue(lifecycle["flush_returns_samples"])
        self.assertTrue(lifecycle["second_flush_empty"])
        self.assertTrue(lifecycle["close_idempotent"])
        self.assertTrue(lifecycle["zero_length_stream_flush"])
        for key in ("process_after_flush", "process_after_close",
                    "flush_after_close", "reset_after_close"):
            self.assertTrue(lifecycle[key].startswith("rejected"), key)

    def test_20_asset_admission_blocked_with_exact_reasons(self):
        admission = self.report["asset_admission"]
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(admission["reason_codes"], verify.EXPECTED_REASONS)
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vendor_runtime_invoked"])
        self.assertFalse(admission["asset_bytes_read"])
        control = self.report["asset_boundary"]["synthetic_admission_control"]
        self.assertEqual(control["status"], "admitted")
        self.assertTrue(control["not_the_pinned_candidate"])

    def test_21_exact_asset_identity(self):
        asset = self.report["asset_boundary"]["asset"]
        self.assertEqual(asset["sha256"], reference.MODEL_SHA256)
        self.assertEqual(asset["byte_count"], reference.MODEL_BYTES)
        self.assertEqual(asset["source_revision"], reference.SOURCE_REVISION)
        self.assertIsNone(asset["model_revision"])
        self.assertIn("mutable", asset["model_download_revision"])

    def test_22_no_real_world_claims(self):
        self.assertTrue(all(value is False for value in self.report["claims"].values()))
        profile = self.report["enhancement_profile"]
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["real_clean_references"])
        self.assertEqual(profile["listening"]["status"], "not_run")
        self.assertFalse(profile["content_and_availability_timing"]["measured"])
        self.assertEqual(self.report["streaming_boundary"]["clock_id"],
                         reference.CLOCK_ID)

    def test_23_all_gates_blocked(self):
        gates = self.report["gates"]
        self.assertEqual({gate["name"] for gate in gates}, verify.EXPECTED_GATES)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])

    def test_24_exact_blockers_and_reopen_conditions(self):
        blockers = " ".join(self.report["exact_blockers"])
        for token in ("model_revision is null", "dpdfnet 0.6.0",
                      "Apache-2.0", "No rights-cleared"):
            self.assertIn(token, blockers)
        reopen = " ".join(self.report["reopen_conditions"])
        for token in ("immutable artifact revision",
                      "pinned dpdfnet 0.6.0 runtime",
                      "written artifact-specific"):
            self.assertIn(token, reopen)

    def test_25_regressions_are_honest(self):
        self.assertTrue(self.report["regressions"])
        for item in self.report["regressions"]:
            self.assertIn(item["metric"], ("snr_db", "si_sdr_db"))
            self.assertLess(item["surrogate_streamed_160"], item["noisy_control"])

    def test_26_repeatability_is_byte_identical(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_27_source_context_is_separated(self):
        context = self.report["source_reported_context"]
        self.assertIn("not reproduced", context["scope"])
        self.assertIn("not reproduced", context["disclaimer"])
        self.assertEqual(context["measured_package_stream_lag_samples"], 640)
        self.assertEqual(context["scheduled_cpp_reported_content_delay_samples"], 800)

    def test_28_disposition_files_are_defer_and_off(self):
        for document in (self.contract, self.adapter, self.readiness):
            self.assertEqual(document["decision"], "DEFER")
        self.assertFalse(self.adapter["registration"]["registered"])
        self.assertFalse(self.adapter["registration"]["enabled_by_default"])
        self.assertFalse(self.contract["qualification"]["qualifies"])
        self.assertEqual(self.readiness["status"], "blocked")
        self.assertFalse(self.readiness["qualified"])

    def test_29_contract_pins_match_manifest(self):
        manifest = verify.read_manifest()
        source_pins = {key: value for key, value in manifest.items()
                       if key.startswith("source:")}
        boundary_pins = {key: value for key, value in manifest.items()
                         if key in {f"worktree:{name}" for name in reference.BOUNDARY_PINS}}
        self.assertEqual(self.contract["source_pins"], source_pins)
        self.assertEqual(self.contract["boundary_pins"], boundary_pins)
        self.assertEqual(self.contract["artifact_pins"], cli.contract_pins())

    def test_30_synth_is_deterministic_and_finite(self):
        for condition in reference.CONDITIONS:
            clean, observed = reference.synth(condition)
            again = reference.synth(condition)
            self.assertEqual(clean, again[0])
            self.assertEqual(observed, again[1])
            self.assertEqual(len(observed), 32000)
            self.assertTrue(all(math.isfinite(value) for value in observed))
        self.assertEqual(reference.asset_admission(reference.asset_ref())["status"], "blocked")

    def test_31_no_negative_zero_or_trailing_whitespace(self):
        self.assertNotIn(b"-0.0", self.generated)
        for path in sorted(HERE.iterdir()):
            if not path.is_file() or path.suffix not in {
                    ".py", ".json", ".md", ".sha256", ".license"}:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_32_three_cold_starts_are_byte_identical(self):
        code = ("import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(set(digests), {self.digest})

    def test_33_licensing_check_passes(self):
        result = subprocess.run([sys.executable, "check_licensing.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_34_verify_passes(self):
        result = subprocess.run([sys.executable, "verify.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_35_scope_is_task_local(self):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(TASK_PREFIX), path)


if __name__ == "__main__":
    unittest.main()
