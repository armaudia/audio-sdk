# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the ClearVoice MossFormerGAN package."""

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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402
import verify  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
ADAPTER = HERE / "adapter.json"
READINESS = HERE / "readiness.json"
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
        cls.contract = strict_json(CONTRACT)
        cls.adapter = strict_json(ADAPTER)
        cls.readiness = strict_json(READINESS)
        cls.generated = reference.canonical_report_bytes(reference.build_report())
        cls.digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()

    def test_01_report_regenerates_byte_identically(self):
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self):
        self.assertEqual(SIDECAR.read_text(encoding="ascii").strip(),
                         f"{self.digest}  report.json")

    def test_03_manifest_regenerates_byte_identically(self):
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())

    def test_04_manifest_is_fail_closed(self):
        manifest = verify.read_manifest()
        self.assertEqual(set(manifest), reference.allowed_pin_keys())
        self.assertNotIn(f"worktree:{TASK_PREFIX}SOURCES.sha256", manifest)

    def test_05_all_json_is_strict(self):
        for path in sorted(HERE.glob("*.json")):
            self.assertIsInstance(strict_json(path), dict, path.name)

    def test_06_status_qualification_and_decision(self):
        self.assertEqual(self.report["status"], reference.STATUS)
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_07_boundary_is_unregistered_and_default_off(self):
        self.assertEqual(self.report["boundary"], reference.BOUNDARY)
        self.assertEqual(self.report["offline_boundary"],
                         reference.OFFLINE_BOUNDARY)
        self.assertFalse(self.report["boundary"]["registered"])
        self.assertFalse(self.report["boundary"]["enabled_by_default"])
        self.assertFalse(self.report["boundary"]["processor_exposure"])
        self.assertFalse(self.report["boundary"]["task_board_or_handoff_write"])

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
                    "enhancement_profile", "adverse", "repeatability", "gates",
                    "exact_blockers", "reopen_conditions", "missing_evidence",
                    "claims", "scope", "readme_digest_files"):
            self.assertIn(key, self.report)

    def test_10_base_commit_branch_and_component(self):
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["base_commit"],
                         "c7cb12877fb8dce8620ba4963f0496a8061d9f7b")
        self.assertEqual(self.report["branch"], reference.BRANCH)
        self.assertEqual(self.report["task_id"],
                         "SDK-CLEARVOICE-MOSSFORMERGAN")
        self.assertEqual(self.report["component"], "clearvoice-mossformergan")
        self.assertEqual(self.report["slug"], "clearvoice-mossformergan")

    def test_11_all_conditions_scored(self):
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, block in self.report["conditions"].items():
            self.assertEqual(block["scored_samples"], 32000)
            self.assertEqual(block["tail_validity"]["output_samples"], 32000)
            for variant in block["variants"].values():
                self.assertEqual(variant["nonfinite_samples"], 0)
                self.assertEqual(variant["clipped_samples"], 0)
                self.assertTrue(math.isfinite(variant["peak_abs_output"]))
                self.assertLessEqual(variant["peak_abs_output"],
                                     reference.PEAK_LIMIT)

    def test_12_identity_and_noisy_controls_match(self):
        for name, block in self.report["conditions"].items():
            identity = block["variants"]["identity_passthrough"]
            noisy = block["variants"]["noisy_control"]
            self.assertTrue(identity["exact_passthrough"], name)
            self.assertEqual(identity["snr_db"], noisy["snr_db"], name)
            self.assertEqual(identity["si_sdr_db"], noisy["si_sdr_db"], name)
            self.assertEqual(identity["stoi"], noisy["stoi"], name)

    def test_13_chunk_size_invariance(self):
        cross = self.report["offline_processing"]["chunk_invariance"]
        self.assertTrue(cross["output_chunk_invariant"])
        self.assertTrue(cross["whole_call_matches_chunked"])
        self.assertEqual(set(cross["chunk_sizes_tested"]),
                         set(reference.CHUNK_SIZES))
        for record in cross["records"].values():
            self.assertEqual(record["output_length"], 32000)
            self.assertEqual(record["valid_samples"], 32000)
            self.assertEqual(record["emitted_before_finish"], 0)
            self.assertEqual(record["finish_emitted"], record["output_length"])

    def test_14_modelled_zero_lag_alignment(self):
        probe = self.report["offline_processing"]["alignment_probe"]
        self.assertEqual(probe["declared_lag_samples"], 0)
        self.assertEqual(probe["output_peak_sample"], 4000)
        self.assertEqual(probe["output_lag_samples"], 0)
        self.assertEqual(probe["residual_lag_samples"], 0)
        self.assertFalse(probe["measured_latency"])

    def test_15_output_accounting_exact(self):
        for name, block in self.report["conditions"].items():
            tail = block["tail_validity"]
            self.assertEqual(tail["output_samples"], tail["input_samples"], name)
            self.assertEqual(tail["valid_samples"], tail["input_samples"], name)
            self.assertEqual(tail["internal_frame_padding_samples"],
                             (-tail["input_samples"]) % reference.FRAME_SAMPLES)
            self.assertEqual(tail["padded_samples_emitted"], 0)
            self.assertEqual(tail["delay_compensation_samples"], 0)
            self.assertEqual(tail["source_time_mapping"], "identity")

    def test_16_offline_state_and_reset(self):
        state = self.report["offline_processing"]["state"]
        self.assertEqual(state["chunks_processed"], 200)
        self.assertTrue(state["reset_replay_identical"])
        self.assertTrue(state["independent_session_identical"])
        self.assertTrue(state["cross_stream_reset_identical"])
        self.assertTrue(state["state_is_synthetic"])
        self.assertFalse(state["real_recurrent_state_loaded"])

    def test_17_partial_final_frame_probe(self):
        probe = self.report["offline_processing"]["tail_probe"]
        self.assertEqual(probe["input_samples"], 32123)
        self.assertEqual(probe["output_samples"], 32123)
        self.assertEqual(probe["internal_frame_padding_samples"], 37)
        self.assertEqual(probe["padded_samples_emitted"], 0)
        self.assertTrue(probe["exact_length"])

    def test_18_config_adverse_cases_fail_closed(self):
        cases = self.report["adverse"]["config_rejections"]
        self.assertEqual(set(cases), verify.EXPECTED_CONFIG_CASES)
        self.assertEqual(cases["caller_asset_admission_control"]["status"],
                         "created")
        for name, case in cases.items():
            if name == "caller_asset_admission_control":
                continue
            self.assertEqual(case["status"], "rejected", name)
            self.assertFalse(case["session_created"], name)
            self.assertTrue(case["reason_codes"], name)

    def test_19_frame_cases_fail_closed_without_state_change(self):
        cases = self.report["adverse"]["frame_cases"]["cases"]
        self.assertEqual(set(cases), verify.EXPECTED_FRAME_CASES)
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
        self.assertEqual(asset["sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(asset["byte_count"], 38_845_593)
        self.assertEqual(asset["source_revision"], reference.SOURCE_REVISION)
        self.assertEqual(asset["package"], "clearvoice==0.1.2")
        self.assertIsNone(asset["model_revision"])
        self.assertIsNone(asset["model_download_revision"])
        pointer = self.report["asset_boundary"]["auxiliary_assets"][0]
        self.assertEqual(pointer["sha256"], reference.POINTER_SHA256)
        self.assertEqual(pointer["byte_count"], 24)
        self.assertFalse(pointer["content_verified"])

    def test_23_no_real_world_claims(self):
        self.assertTrue(all(value is False
                            for value in self.report["claims"].values()))
        self.assertTrue(all(value is False
                            for key, value in self.report["scope"].items()
                            if key not in ("task_local_only",
                                           "synthetic_boundary_surrogate_only",
                                           "caller_supplied_asset_contract_modeled")))
        profile = self.report["enhancement_profile"]
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["real_clean_references"])
        self.assertEqual(profile["listening"]["status"], "not_run")
        self.assertFalse(profile["content_and_availability_timing"]["measured"])
        self.assertEqual(self.report["offline_processing"]["clock_id"],
                         reference.CLOCK_ID)

    def test_24_all_gates_blocked(self):
        gates = self.report["gates"]
        self.assertEqual({gate["name"] for gate in gates}, verify.EXPECTED_GATES)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])

    def test_25_exact_blockers_and_reopen_conditions(self):
        blockers = " ".join(self.report["exact_blockers"])
        for token in ("38,845,593", reference.CHECKPOINT_SHA256,
                      "model_revision is absent", "clearvoice 0.1.2",
                      "Apache-2.0", "open and private", "No rights-cleared"):
            self.assertIn(token, blockers)
        reopen = " ".join(self.report["reopen_conditions"])
        for token in ("immutable model artifact revision",
                      "pinned clearvoice 0.1.2 runtime",
                      "written artifact-specific", "rights-cleared"):
            self.assertIn(token, reopen)

    def test_26_regressions_are_honest(self):
        self.assertTrue(self.report["regressions"])
        for item in self.report["regressions"]:
            self.assertIn(item["metric"], ("snr_db", "si_sdr_db", "stoi"))
            self.assertLess(item["surrogate_value"], item["control_value"])
        conditions = {item["condition"] for item in self.report["regressions"]}
        self.assertIn("clean_speech", conditions)

    def test_27_repeatability_is_byte_identical(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_28_source_context_is_separated(self):
        context = self.report["source_reported_context"]
        self.assertIn("not reproduced", context["scope"])
        self.assertIn("not reproduced", context["disclaimer"])
        full30 = context["full30"]
        self.assertEqual(full30["requested_pairs"], 30)
        self.assertEqual(full30["valid_outputs"], 30)
        self.assertEqual(full30["quality_means"]["mossformer"]["si_sdr_db"],
                         20.687954)
        self.assertEqual(full30["paired_deltas"]["vs_identity"]["si_sdr_db"],
                         10.618209)
        self.assertEqual(context["census_five_clip_screen"]["mean_delta_snr_db"],
                         7.91)
        self.assertEqual(
            context["upstream_author_reported_dns2020"]["PESQ"], 3.57)

    def test_29_disposition_files_are_defer_and_off(self):
        for document in (self.contract, self.adapter, self.readiness):
            self.assertEqual(document["decision"], "DEFER")
        self.assertFalse(self.adapter["registration"]["registered"])
        self.assertFalse(self.adapter["registration"]["enabled_by_default"])
        self.assertFalse(self.contract["qualification"]["qualifies"])
        self.assertEqual(self.readiness["status"], "blocked")
        self.assertFalse(self.readiness["qualified"])
        self.assertEqual(self.adapter["modes"], ["offline"])

    def test_30_contract_pins_match_manifest(self):
        manifest = verify.read_manifest()
        source_pins = {key: value for key, value in manifest.items()
                       if key.startswith("source:")}
        boundary_pins = {key: value for key, value in manifest.items()
                         if key.startswith("worktree:")
                         and key.split(":", 1)[1] in reference.BOUNDARY_PINS}
        self.assertEqual(self.contract["source_pins"], source_pins)
        self.assertEqual(self.contract["boundary_pins"], boundary_pins)

    def test_31_synth_is_deterministic_finite_and_in_range(self):
        for condition in reference.CONDITIONS:
            clean, observed = reference.synth(condition)
            again = reference.synth(condition)
            self.assertEqual(clean, again[0])
            self.assertEqual(observed, again[1])
            self.assertEqual(len(observed), 32000)
            self.assertTrue(all(math.isfinite(value) for value in observed))
            self.assertTrue(all(abs(value) <= 1.0 for value in observed))
        self.assertEqual(reference.asset_admission(reference.asset_ref())["status"],
                         "blocked")

    def test_32_no_negative_zero_or_trailing_whitespace(self):
        self.assertIsNone(re.search(rb"-0\.0(?=[,}\]])", self.generated))
        for path in sorted(HERE.iterdir()):
            if not path.is_file() or path.suffix not in {
                    ".py", ".json", ".md", ".sha256", ".license", ".lock"}:
                continue
            for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1):
                self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_33_three_cold_starts_are_byte_identical(self):
        code = "import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())"
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE,
                                    env=env, capture_output=True, text=True,
                                    check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(set(digests), {self.digest})

    def test_34_verify_passes(self):
        result = subprocess.run([sys.executable, "verify.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_35_scope_is_task_local(self):
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
             "--untracked-files=all"],
            capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(TASK_PREFIX), path)

    def test_36_readme_digest_table_and_test_count(self):
        rows = dict(reference.readme_pin_rows())
        self.assertEqual(set(rows), set(reference.SOURCE_PINS))
        for path, digest in rows.items():
            self.assertEqual(digest, reference.SOURCE_PINS[path], path)
            target = reference.qualify_pin_path(path)
            self.assertEqual(reference.sha256_file(target), digest, path)
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn(reference.readme_test_count_token(), text)
        suite = unittest.defaultTestLoader.loadTestsFromModule(
            sys.modules[__name__])
        self.assertEqual(suite.countTestCases(), reference.EXPECTED_TEST_COUNT)

    def test_37_upstream_boundary_contract(self):
        self.assertEqual(list(reference.CALLER_CONFIG_FIELDS), [
            "model_name", "package_version", "model_revision", "checkpoint_dir",
            "checkpoint_file", "checkpoint_sha256", "sample_rate"])
        config = reference.caller_asset_config()
        self.assertEqual(config["mode"], "caller-asset")
        self.assertEqual(config["model_name"], "MossFormerGAN_SE_16K")
        self.assertEqual(config["checkpoint_file"], reference.CHECKPOINT_FILE)
        self.assertEqual(config["checkpoint_sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(config["sample_rate"], 16000)
        self.assertEqual(reference.validate_config(config),
                         ["asset_not_admitted"])
        boundary = self.report["offline_processing"]
        self.assertEqual(boundary["upstream_config_fields"],
                         list(reference.CALLER_CONFIG_FIELDS))
        self.assertEqual(boundary["pointer_requirement"]["required_content"],
                         reference.CHECKPOINT_FILE)
        self.assertFalse(boundary["pointer_requirement"]["content_verified_here"])

    def test_38_ledger_record_matches_constants(self):
        record = reference.asset_ledger_record()
        self.assertEqual(record["id"], reference.CANDIDATE_ID)
        self.assertEqual(record["source"], reference.PACKAGE_SOURCE)
        self.assertEqual(record["source_revision"], reference.SOURCE_REVISION)
        self.assertEqual(record["code_license"], "Apache-2.0")
        self.assertEqual(record["model_license"], "Apache-2.0")
        self.assertEqual(record["training_data_note"],
                         reference.TRAINING_DATA_NOTE)
        artifacts = {item["path"]: item for item in record["artifacts"]}
        checkpoint = artifacts[
            reference.CHECKPOINT_DIR + "/" + reference.CHECKPOINT_FILE]
        pointer = artifacts[reference.CHECKPOINT_DIR + "/last_best_checkpoint"]
        self.assertEqual(checkpoint["bytes"], reference.CHECKPOINT_BYTES)
        self.assertEqual(checkpoint["sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(pointer["bytes"], reference.POINTER_BYTES)
        self.assertEqual(pointer["sha256"], reference.POINTER_SHA256)

    def test_39_research_results_match_context(self):
        results = reference.mossformer_results()
        self.assertIn("MossFormerGAN_SE_16K", results["candidate"])
        self.assertEqual(results["source_commit"], reference.SOURCE_REVISION)
        self.assertEqual(results["checkpoint_sha256"],
                         reference.CHECKPOINT_SHA256)
        self.assertEqual(results["requested_pairs"], 30)
        self.assertEqual(results["valid_outputs"], 30)
        self.assertEqual(results["missing_outputs"], 0)
        context = reference.SOURCE_REPORTED_CONTEXT["full30"]
        self.assertAlmostEqual(
            results["quality_aggregate"]["mossformer"]["snr_db"]["mean"],
            context["quality_means"]["mossformer"]["snr_db"], places=6)
        self.assertAlmostEqual(
            results["paired_comparisons"]["identity"][
                "si_sdr_db_mossformer_minus_identity"]["mean"],
            context["paired_deltas"]["vs_identity"]["si_sdr_db"], places=6)

    def test_40_no_vendored_assets_and_or_gan_not_executed(self):
        self.assertEqual(reference.vendored_binary_files(), [])
        surrogate = self.report["surrogate"]
        for key in ("is_candidate", "is_neural_network", "attention_blocks",
                    "gan_generator_or_discriminator", "weights", "checkpoint",
                    "vendor_runtime", "quality_claim"):
            self.assertIs(surrogate[key], False, key)
        self.assertFalse((SDK_ROOT / reference.CHECKPOINT_DIR).exists())
        self.assertFalse((SDK_ROOT / "adapters/clearvoice").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
