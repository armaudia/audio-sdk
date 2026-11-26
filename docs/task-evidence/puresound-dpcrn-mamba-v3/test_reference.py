# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the PureSound DPCRN-Mamba v3 package."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
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
        cls.asset = strict_json(HERE / "asset.json")
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
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_07_boundary_is_unregistered_and_default_off(self):
        self.assertEqual(self.report["boundary"], reference.BOUNDARY)
        self.assertEqual(self.report["offline_boundary"], reference.OFFLINE_BOUNDARY)
        self.assertFalse(self.report["boundary"]["registered"])
        self.assertFalse(self.report["boundary"]["enabled_by_default"])
        self.assertFalse(self.report["boundary"]["processor_exposure"])
        self.assertFalse(self.report["boundary"]["realtime_streaming_exposed"])

    def test_08_public_v0_geometry_is_unchanged(self):
        self.assertEqual(self.report["format"], reference.FORMAT)
        self.assertEqual(self.report["format"]["sample_rate_hz"], 16000)
        self.assertEqual(self.report["format"]["channels"], 1)
        self.assertEqual(self.report["format"]["sample_format"], "f32")
        self.assertEqual(self.report["format"]["frame_samples"], 160)

    def test_09_report_has_required_sections(self):
        for key in ("schema_id", "task_id", "component", "slug", "base_commit",
                    "branch", "profile", "conditions", "controls", "regressions",
                    "offline_boundary", "offline_processing", "asset_boundary",
                    "asset_admission", "enhancement_profile", "adverse",
                    "repeatability", "gates", "exact_blockers", "reopen_conditions",
                    "missing_evidence", "claims", "readme_digest_files"):
            self.assertIn(key, self.report)

    def test_10_base_commit_branch_and_component(self):
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["branch"], reference.BRANCH)
        self.assertEqual(self.report["task_id"], "SDK-PURESOUND-DPCRN-MAMBA-V3")
        self.assertEqual(self.report["component"], "puresound-dpcrn-mamba-v3")
        self.assertEqual(self.report["slug"], "puresound-dpcrn-mamba-v3")

    def test_11_all_conditions_scored(self):
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, block in self.report["conditions"].items():
            self.assertEqual(block["scored_samples"], 32000)
            self.assertEqual(block["tail_validity"]["output_samples"], 32000)
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
        cross = self.report["offline_processing"]["chunk_invariance"]
        self.assertTrue(cross["output_chunk_invariant"])
        self.assertTrue(cross["whole_call_matches_chunked"])
        self.assertEqual(set(cross["chunk_sizes_tested"]), set(reference.CHUNK_SIZES))
        for record in cross["records"].values():
            self.assertEqual(record["output_length"], 32000)
            self.assertEqual(record["valid_samples"], 32000)
            self.assertEqual(record["streamed_samples"], 32480)
            self.assertEqual(record["emitted_before_finish"], 0)
            self.assertEqual(record["finish_emitted"], record["output_length"])

    def test_14_modelled_480_sample_content_delay(self):
        probe = self.report["offline_processing"]["alignment_probe"]
        self.assertEqual(probe["declared_content_delay_samples"], 480)
        self.assertEqual(probe["declared_lookahead_samples"], 480)
        self.assertEqual(probe["streamed_peak_sample"], 4480)
        self.assertEqual(probe["output_peak_sample"], 4000)
        self.assertEqual(probe["output_lag_samples"], 0)
        self.assertEqual(probe["residual_lag_samples"], 0)
        self.assertFalse(probe["measured_latency"])

    def test_15_output_accounting_exact(self):
        for block in self.report["conditions"].values():
            tail = block["tail_validity"]
            self.assertEqual(tail["output_samples"], tail["input_samples"])
            self.assertEqual(tail["valid_samples"], tail["input_samples"])
            self.assertEqual(tail["streamed_samples"],
                             tail["input_samples"] + reference.LOOKAHEAD_SAMPLES)
            self.assertEqual(tail["streamed_hold_samples"], 480)
            self.assertEqual(tail["internal_frame_padding_samples"],
                             (-tail["input_samples"]) % reference.HOP_LENGTH)
            self.assertEqual(tail["padded_samples_emitted"], 0)
            self.assertEqual(tail["delay_compensation_samples"], 480)
            self.assertEqual(tail["source_time_mapping"], "identity")

    def test_16_offline_state_and_reset(self):
        state = self.report["offline_processing"]["state"]
        self.assertEqual(state["chunks_processed"], 200)
        self.assertTrue(state["reset_replay_identical"])
        self.assertTrue(state["independent_session_identical"])
        self.assertTrue(state["cross_stream_reset_identical"])
        self.assertFalse(state["real_recurrent_state_loaded"])
        self.assertTrue(state["state_is_synthetic"])

    def test_17_partial_final_hop_probe(self):
        probe = self.report["offline_processing"]["tail_probe"]
        self.assertEqual(probe["input_samples"], 32123)
        self.assertEqual(probe["output_samples"], 32123)
        self.assertEqual(probe["streamed_samples"], 32603)
        self.assertEqual(probe["streamed_hold_samples"], 480)
        self.assertEqual(probe["internal_frame_padding_samples"], 37)
        self.assertEqual(probe["padded_samples_emitted"], 0)
        self.assertTrue(probe["exact_length"])

    def test_18_config_adverse_cases_fail_closed(self):
        cases = self.report["adverse"]["config_rejections"]
        self.assertEqual(cases["caller_asset_admission_control"]["status"], "created")
        for name, case in cases.items():
            if name == "caller_asset_admission_control":
                continue
            self.assertEqual(case["status"], "rejected", name)
            self.assertFalse(case["session_created"], name)
            self.assertTrue(case["reason_codes"], name)

    def test_19_frame_cases_fail_closed_without_state_change(self):
        cases = self.report["adverse"]["frame_cases"]["cases"]
        self.assertTrue(cases)
        for name, case in cases.items():
            self.assertTrue(case["status"].startswith("rejected"), name)
            self.assertTrue(case["state_unchanged"], name)
        self.assertTrue(self.report["adverse"]["frame_cases"][
            "state_after_close_unchanged_by_rejected_calls"])

    def test_20_lifecycle_fail_closed(self):
        lifecycle = self.report["adverse"]["lifecycle"]
        self.assertTrue(lifecycle["finish_returns_samples"])
        self.assertTrue(lifecycle["second_finish"].startswith("rejected"))
        self.assertTrue(lifecycle["reset_finish_empty"])
        self.assertTrue(lifecycle["close_idempotent"])
        self.assertTrue(lifecycle["zero_length_finish"])
        for key in ("process_after_close", "finish_after_close", "reset_after_close"):
            self.assertTrue(lifecycle[key].startswith("rejected"), key)

    def test_21_asset_admission_blocked_with_exact_reasons(self):
        admission = self.report["asset_admission"]
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(admission["reason_codes"], verify.EXPECTED_REASONS)
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vendor_runtime_invoked"])
        self.assertFalse(admission["asset_bytes_read"])
        control = self.report["asset_boundary"]["synthetic_admission_control"]
        self.assertEqual(control["status"], "admitted")
        self.assertTrue(control["not_the_pinned_candidate"])

    def test_22_exact_asset_identity(self):
        asset = self.report["asset_boundary"]["asset"]
        self.assertEqual(asset["sha256"], reference.ONNX_SHA256)
        self.assertEqual(asset["byte_count"], reference.ONNX_BYTES)
        self.assertEqual(asset["source_revision"], reference.SOURCE_REVISION)
        self.assertEqual(asset["catalog_sha256"], reference.CATALOG_SHA256)
        self.assertEqual(asset["package"], "puresound-streaming==0.1.0")
        self.assertEqual(asset["runtime"], "onnxruntime==1.24.1")
        self.assertEqual(asset["provider"], "cpu")
        self.assertEqual(asset["variant"], "default")
        self.assertIsNone(asset["model_revision"])
        self.assertIsNone(asset["model_download_revision"])
        manifest = self.report["asset_boundary"]["auxiliary_assets"][0]
        self.assertEqual(manifest["sha256"], reference.MANIFEST_SHA256)
        self.assertEqual(manifest["byte_count"], reference.MANIFEST_BYTES)
        self.assertFalse(manifest["content_verified"])

    def test_23_external_checkout_bytes_are_pinned_but_not_admitted(self):
        boundary = self.report["asset_boundary"]
        self.assertTrue(boundary["bytes_present_in_research_checkout"])
        self.assertFalse(boundary["bytes_present_in_sdk_worktree"])
        self.assertTrue(boundary["hashes_verified_against_research_checkout"])
        self.assertFalse(boundary["asset_bytes_read"])
        probe = boundary["runtime_probe"]
        self.assertTrue(probe["source_checkout_head_matches_pin"])
        self.assertTrue(probe["graph_sha256_matches_ledger"])
        self.assertTrue(probe["manifest_sha256_matches_ledger"])
        self.assertFalse(probe["asset_bytes_loaded_for_inference"])

    def test_24_runtime_is_absent_from_pinned_interpreter(self):
        boundary = self.report["asset_boundary"]
        self.assertFalse(boundary["runtime_available_in_evidence_interpreter"])
        probe = boundary["runtime_probe"]
        self.assertFalse(probe["onnxruntime_importable"])
        self.assertFalse(probe["puresound_streaming_importable"])
        self.assertFalse(probe["vendor_runtime_invoked"])
        self.assertEqual(probe["pinned_evidence_interpreter"], "CPython 3.12.16")

    def test_25_no_real_world_claims(self):
        self.assertTrue(all(value is False for value in self.report["claims"].values()))
        profile = self.report["enhancement_profile"]
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["real_clean_references"])
        self.assertEqual(profile["listening"]["status"], "not_run")
        self.assertFalse(profile["content_and_availability_timing"]["measured"])
        self.assertEqual(self.report["offline_processing"]["clock_id"],
                         reference.CLOCK_ID)

    def test_26_all_gates_blocked(self):
        gates = self.report["gates"]
        self.assertEqual({gate["name"] for gate in gates}, verify.EXPECTED_GATES)
        self.assertEqual(len(gates), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])

    def test_27_exact_blockers_and_reopen_conditions(self):
        blockers = " ".join(self.report["exact_blockers"])
        for token in ("4,146,551", reference.ONNX_SHA256, "3,567",
                      reference.MANIFEST_SHA256, reference.SOURCE_REVISION,
                      "no model_revision", "puresound-streaming 0.1.0",
                      "onnxruntime 1.24.1", "ModuleNotFoundError", "Apache-2.0",
                      "NOTICE", "third-party", "No rights-cleared"):
            self.assertIn(token, blockers)
        reopen = " ".join(self.report["reopen_conditions"])
        for token in ("immutable model artifact revision",
                      "pinned puresound-streaming 0.1.0", "onnxruntime 1.24.1",
                      "written artifact-specific", "rights-cleared"):
            self.assertIn(token, reopen)

    def test_28_regressions_are_honest(self):
        self.assertTrue(self.report["regressions"])
        for item in self.report["regressions"]:
            self.assertIn(item["metric"], ("snr_db", "si_sdr_db"))
            self.assertLess(item["surrogate_offline_chunked_160"], item["noisy_control"])
        conditions = {item["condition"] for item in self.report["regressions"]}
        self.assertIn("quiet_speech", conditions)

    def test_29_repeatability_is_byte_identical(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_30_source_context_is_separated(self):
        context = self.report["source_reported_context"]
        self.assertIn("not reproduced", context["scope"])
        self.assertIn("not reproduced", context["disclaimer"])
        self.assertEqual(context["pilot_30_clip_median_output_snr_db"], 16.169)
        self.assertEqual(context["pilot_30_clip_median_delta_snr_db"], 7.268)
        self.assertEqual(context["pilot_30_clip_mean_delta_si_sdr_db"], 6.5894)
        self.assertEqual(context["pilot_30_clip_median_stoi"], 0.9711)
        self.assertEqual(context["pilot_30_clip_median_cpu_rtf"], 0.2542)
        self.assertEqual(context["pilot_30_clip_snr_improve_tie_degrade"], [28, 0, 2])
        self.assertEqual(context["pilot_30_clip_stoi_improve_tie_degrade"], [30, 0, 0])

    def test_31_disposition_files_are_defer_and_off(self):
        for document in (self.contract, self.adapter, self.readiness):
            self.assertEqual(document["decision"], "DEFER")
        self.assertFalse(self.adapter["registration"]["registered"])
        self.assertFalse(self.adapter["registration"]["enabled_by_default"])
        self.assertFalse(self.contract["qualification"]["qualifies"])
        self.assertEqual(self.readiness["status"], "blocked")
        self.assertFalse(self.readiness["qualified"])
        self.assertEqual(self.adapter["modes"], ["offline"])
        self.assertEqual(self.adapter["upstream_modes"], ["offline", "realtime-streaming"])

    def test_32_contract_pins_match_manifest(self):
        manifest = verify.read_manifest()
        source_pins = {key: value for key, value in manifest.items()
                       if key.startswith("source:")}
        boundary_pins = {key: value for key, value in manifest.items()
                         if key in {f"worktree:{name}" for name in reference.BOUNDARY_PINS}}
        self.assertEqual(self.contract["source_pins"], source_pins)
        self.assertEqual(self.contract["boundary_pins"], boundary_pins)
        self.assertEqual(self.contract["artifact_pins"], cli.contract_pins())

    def test_33_synth_is_deterministic_finite_and_in_range(self):
        for condition in reference.CONDITIONS:
            clean, observed = reference.synth(condition)
            again = reference.synth(condition)
            self.assertEqual(clean, again[0])
            self.assertEqual(observed, again[1])
            self.assertEqual(len(observed), 32000)
            self.assertTrue(all(math.isfinite(value) for value in observed))
            self.assertTrue(all(abs(value) <= 1.0 for value in observed))
        self.assertEqual(reference.asset_admission(reference.asset_ref())["status"], "blocked")

    def test_34_no_negative_zero_or_trailing_whitespace(self):
        self.assertIsNone(re.search(rb"-0\.0(?=[,}\]])", self.generated))
        for path in sorted(HERE.iterdir()):
            if not path.is_file() or path.suffix not in {
                    ".py", ".json", ".md", ".sha256", ".license", ".lock"}:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_35_three_cold_starts_are_byte_identical(self):
        code = ("import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(set(digests), {self.digest})

    def test_36_licensing_check_passes(self):
        result = subprocess.run([sys.executable, "check_licensing.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_37_verify_passes(self):
        result = subprocess.run([sys.executable, "verify.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_38_scope_is_task_local(self):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(TASK_PREFIX), path)

    def test_39_readme_digest_table_and_test_count(self):
        rows = verify._readme_table_rows()
        expected = [(name, reference.sha256_file(HERE / name),
                     (HERE / name).stat().st_size)
                    for name in reference.README_DIGEST_FILES]
        self.assertEqual(rows, expected)
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"Tests: **{reference.EXPECTED_TEST_COUNT} passed, "
                      "0 failed, 0 skipped**", text)
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
        self.assertEqual(suite.countTestCases(), reference.EXPECTED_TEST_COUNT)

    def test_40_upstream_boundary_contract(self):
        self.assertEqual(list(reference.CALLER_CONFIG_FIELDS), [
            "repository_dir", "code_revision", "model_id", "model_path",
            "manifest_path", "model_sha256", "sample_rate", "provider", "variant"])
        config = reference.caller_asset_config()
        self.assertEqual(config["mode"], "caller-asset")
        self.assertEqual(config["code_revision"], reference.SOURCE_REVISION)
        self.assertEqual(config["model_id"], reference.MODEL_ID)
        self.assertEqual(config["model_sha256"], reference.ONNX_SHA256)
        self.assertEqual(config["sample_rate"], 16000)
        self.assertEqual(reference.validate_config(config), ["asset_not_admitted"])
        boundary = self.report["offline_processing"]
        self.assertEqual(boundary["upstream_config_fields"],
                         list(reference.CALLER_CONFIG_FIELDS))
        self.assertEqual(boundary["manifest_requirement"]["required_content"],
                         reference.MANIFEST_REQUIRED)
        self.assertFalse(boundary["manifest_requirement"]["content_verified_here"])

    def test_41_asset_json_pins_the_exact_caller_reference(self):
        self.assertEqual(self.asset["asset"]["sha256"], reference.ONNX_SHA256)
        self.assertEqual(self.asset["asset"]["byte_count"], reference.ONNX_BYTES)
        self.assertEqual(self.asset["manifest"]["sha256"], reference.MANIFEST_SHA256)
        self.assertEqual(self.asset["manifest"]["byte_count"], reference.MANIFEST_BYTES)
        self.assertFalse(self.asset["asset"]["present_in_sdk_worktree"])
        self.assertFalse(self.asset["asset"]["loaded_for_inference"])
        self.assertFalse(self.asset["download_permitted"])
        self.assertEqual(self.asset["readiness"], "blocked")
        self.assertEqual(self.asset["reason_codes"], verify.EXPECTED_REASONS)
        self.assertEqual(self.asset["runtime"]["requirements_lock"], {
            "numpy": "2.2.6", "onnxruntime": "1.24.1", "soundfile": "0.13.1"})

    def test_42_requirements_lock_is_the_pinned_runtime(self):
        text = (HERE / "requirements.lock").read_text(encoding="utf-8")
        for line in ("numpy==2.2.6", "onnxruntime==1.24.1", "soundfile==0.13.1"):
            self.assertIn(line, text)
        self.assertIn("not installed", text)

    def test_43_licenses_record_scope_and_exclusions(self):
        text = (HERE / "LICENSES.md").read_text(encoding="utf-8")
        self.assertIn("Apache-2.0", text)
        self.assertIn("NOTICE", text)
        self.assertIn("third-party", text)
        self.assertIn("Datasets and audio recordings", text)
        self.assertIn("rights_cleared=false", text)
        self.assertIn(reference.NOTICE_SHA256, text)

    def test_45_task_link_uses_stable_row_identity_only(self):
        link = self.report["task_link"]
        self.assertEqual(link, reference.task_link())
        self.assertFalse(link["board_hashed"])
        self.assertEqual(link["projection"]["id"], "SDK-PURESOUND-DPCRN-MAMBA-V3")
        self.assertEqual(link["projection"]["component"], "puresound-dpcrn-mamba-v3")
        self.assertEqual(link["projection"]["claim"]["branch"], reference.BRANCH)
        self.assertEqual(link["projection"]["claim"]["base_commit"], reference.BASE_COMMIT)
        self.assertNotIn("plan/swarm/TASKS.json", " ".join(
            key for key in verify.read_manifest()))

    def test_46_manifest_content_rejects_invalid_and_nonfinite(self):
        cases = self.report["adverse"]["manifest_cases"]
        self.assertEqual(cases["complete_control"]["status"], "admitted")
        for name, case in cases.items():
            if name == "complete_control":
                continue
            self.assertEqual(case["status"], "rejected", name)
            self.assertTrue(case["reason_codes"], name)
            self.assertFalse(case["content_admitted"], name)
        for name in ("nonfinite_latency", "infinite_latency"):
            self.assertTrue(any(code.startswith("manifest_field_mismatch:")
                                for code in cases[name]["reason_codes"]), name)

    def test_47_sibling_packages_are_distinct_and_not_promoted(self):
        sibling = self.report["sibling_v1_package"]
        self.assertEqual(sibling["decision"], "DEFER")
        self.assertEqual(sibling["qualification_status"], "not_qualified")
        self.assertTrue(sibling["merged"])
        self.assertNotEqual(sibling["graph_sha256"], reference.ONNX_SHA256)
        self.assertNotEqual(sibling["component"], reference.COMPONENT)
        self.assertIn("No v1 metric", sibling["note"])
        sibling_v2 = self.report["sibling_v2_package"]
        self.assertEqual(sibling_v2["decision"], "DEFER")
        self.assertEqual(sibling_v2["qualification_status"], "not_qualified")
        self.assertFalse(sibling_v2["merged"])
        self.assertNotEqual(sibling_v2["graph_sha256"], reference.ONNX_SHA256)
        self.assertNotEqual(sibling_v2["component"], reference.COMPONENT)
        self.assertIn("No v2 metric", sibling_v2["note"])

    def test_44_manifest_geometry_is_the_pure_sound_streaming_boundary(self):
        geometry = self.report["offline_processing"]["analysis_geometry"]
        self.assertEqual(geometry["fft_length"], 512)
        self.assertEqual(geometry["win_length"], 512)
        self.assertEqual(geometry["hop_length"], 160)
        self.assertEqual(geometry["freq_bins"], 257)
        self.assertEqual(geometry["feature_bins"], 256)
        self.assertEqual(geometry["streaming_delay_frames"], 3)
        self.assertEqual(geometry["lookahead_samples"], 480)
        self.assertEqual(geometry["input_to_output_min_ms"], 52.0)
        self.assertEqual(geometry["input_to_output_max_ms"], 62.0)
        self.assertEqual(geometry["excludes"], [
            "compute time", "additional input chunk buffering",
            "audio device buffering", "transport"])


if __name__ == "__main__":
    unittest.main()
