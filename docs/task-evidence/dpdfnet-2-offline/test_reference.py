# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, network-free tests for the offline evidence fixture."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import reference
import run as cli
import verify

HERE = Path(__file__).resolve().parent


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_bytes_are_compact_sorted_and_stable(self) -> None:
        value = {"b": [1, 2], "a": {"d": 4, "c": 3}}
        first = reference.canonical_bytes(value)
        second = reference.canonical_bytes({"a": {"c": 3, "d": 4}, "b": [1, 2]})
        self.assertEqual(first, second)
        self.assertEqual(first, b'{"a":{"c":3,"d":4},"b":[1,2]}')

    def test_negative_zero_is_normalized(self) -> None:
        self.assertEqual(reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}')

    def test_nonfinite_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"x": float("nan")})
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"x": float("inf")})


class SyntheticSignalTests(unittest.TestCase):
    def test_every_condition_is_deterministic_and_full_length(self) -> None:
        for condition in reference.CONDITIONS:
            with self.subTest(condition=condition):
                clean_a, observed_a = reference.synth(condition)
                clean_b, observed_b = reference.synth(condition)
                self.assertEqual(len(clean_a), reference.SAMPLES)
                self.assertEqual(len(observed_a), reference.SAMPLES)
                self.assertEqual(clean_a, clean_b)
                self.assertEqual(observed_a, observed_b)
                self.assertTrue(all(math.isfinite(value) for value in observed_a))

    def test_idle_noise_has_no_target(self) -> None:
        clean, observed = reference.synth("idle_noise")
        self.assertTrue(all(value == 0.0 for value in clean))
        self.assertTrue(any(value != 0.0 for value in observed))

    def test_signal_peaks_stay_below_unit(self) -> None:
        for condition in reference.CONDITIONS:
            with self.subTest(condition=condition):
                _, observed = reference.synth(condition)
                self.assertLess(max(abs(value) for value in observed), 1.0)


class AssetAdmissionTests(unittest.TestCase):
    def test_asset_reference_is_the_pinned_candidate(self) -> None:
        ref = reference.asset_ref()
        self.assertEqual(ref["asset_id"], "dpdfnet2.onnx")
        self.assertEqual(ref["byte_count"], 10_178_747)
        self.assertEqual(ref["sha256"], reference.MODEL_SHA256)
        self.assertEqual(ref["storage"], "external")
        self.assertIsNone(ref["model_revision"])
        self.assertFalse(ref["bytes_present"])
        self.assertFalse(ref["rights_cleared"])

    def test_admission_blocks_with_exact_reasons(self) -> None:
        result = reference.asset_admission(reference.asset_ref())
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_codes"], [
            "model_revision_unpinned",
            "download_revision_mutable",
            "asset_bytes_absent",
            "runtime_unavailable",
            "rights_not_cleared",
        ])
        self.assertFalse(result["download_attempted"])
        self.assertFalse(result["vendor_runtime_invoked"])
        self.assertFalse(result["asset_bytes_read"])

    def test_synthetic_admission_control_is_admitted(self) -> None:
        ref = dict(reference.asset_ref())
        ref.update({
            "model_revision": "artifact:dpdfnet2@sha256:" + reference.MODEL_SHA256,
            "model_download_revision": "artifact:dpdfnet2@sha256:" + reference.MODEL_SHA256,
            "rights_cleared": True,
            "bytes_present": True,
            "runtime_available": True,
        })
        result = reference.asset_admission(ref)
        self.assertEqual(result["status"], "admitted")
        self.assertEqual(result["reason_codes"], [])

    def test_admission_rejects_mismatched_identity(self) -> None:
        ref = dict(reference.asset_ref())
        ref["sha256"] = "0" * 64
        result = reference.asset_admission(ref)
        self.assertIn("sha256_mismatch", result["reason_codes"])
        self.assertIn("model_revision_unpinned", result["reason_codes"])


class ConfigTests(unittest.TestCase):
    def test_default_config_is_valid(self) -> None:
        self.assertEqual(reference.validate_config(reference.default_config()), [])

    def test_config_rejections_fail_closed(self) -> None:
        cases = reference.config_adverse_cases()
        expected = {
            "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
            "wrong_frame_samples", "wrong_max_clip_samples", "streaming_mode_unsupported",
            "surrogate_without_opt_in", "caller_asset_unavailable",
            "caller_asset_admission_control",
        }
        self.assertEqual(set(cases), expected)
        for name, case in cases.items():
            with self.subTest(name=name):
                if name == "caller_asset_admission_control":
                    self.assertEqual(case["status"], "created")
                    self.assertTrue(case["session_created"])
                else:
                    self.assertEqual(case["status"], "rejected")
                    self.assertFalse(case["session_created"])

    def test_streaming_mode_is_unsupported(self) -> None:
        config = reference.default_config()
        config["mode"] = "streaming"
        self.assertEqual(reference.validate_config(config), ["mode_unsupported"])

    def test_surrogate_requires_opt_in(self) -> None:
        config = reference.default_config()
        config["synthetic_surrogate_opt_in"] = False
        self.assertEqual(reference.validate_config(config), ["surrogate_opt_in_required"])


class SurrogateTests(unittest.TestCase):
    def test_output_length_equals_input_for_every_condition(self) -> None:
        for condition in reference.CONDITIONS:
            with self.subTest(condition=condition):
                _, observed = reference.synth(condition)
                result = reference.surrogate_offline(observed)
                self.assertEqual(result["input_samples"], reference.SAMPLES)
                self.assertEqual(result["output_samples"], reference.SAMPLES)
                self.assertEqual(len(result["output"]), reference.SAMPLES)
                self.assertEqual(result["internal_frame_padding_samples"], 0)
                self.assertTrue(all(math.isfinite(value) for value in result["output"]))

    def test_surrogate_is_deterministic(self) -> None:
        _, observed = reference.synth("active_speech")
        first = reference.surrogate_offline(observed)
        second = reference.surrogate_offline(list(observed))
        self.assertEqual(first["output_digest"], second["output_digest"])
        self.assertEqual(first["output"], second["output"])

    def test_frame_loop_matches_whole_clip(self) -> None:
        _, observed = reference.synth("low_snr_speech")
        whole = reference.surrogate_offline(observed)
        loop = reference.surrogate_frame_loop_control(observed)
        self.assertEqual(whole["output_digest"], loop["output_digest"])
        self.assertEqual(whole["output"], loop["output"])

    def test_split_halves_differ_from_whole_clip(self) -> None:
        _, observed = reference.synth("active_speech")
        whole = reference.surrogate_offline(observed)["output"]
        split = reference.surrogate_split_halves(observed)["output"]
        self.assertEqual(len(whole), len(split))
        self.assertNotEqual(whole, split)

    def test_future_audio_changes_the_prefix(self) -> None:
        evidence = reference.future_context_evidence()
        self.assertTrue(evidence["requires_complete_clip"])
        self.assertGreater(evidence["prefix_samples_changed_by_future_audio"], 0)
        self.assertFalse(evidence["prefix_available_before_full_clip"])

    def test_partial_final_frame_is_padded_internally_only(self) -> None:
        tail = reference.tail_control()
        self.assertEqual(tail["input_samples"], 32_123)
        self.assertEqual(tail["output_samples"], 32_123)
        self.assertEqual(tail["internal_frame_padding_samples"], 37)
        self.assertFalse(tail["padding_emitted_as_audio"])

    def test_alignment_probe_preserves_the_peak_index(self) -> None:
        probe = reference.alignment_probe()
        self.assertEqual(probe["input_peak_sample"], 4000)
        self.assertEqual(probe["output_peak_sample"], 4000)
        self.assertTrue(probe["peak_index_preserved"])
        self.assertEqual(probe["algorithmic_lag_samples"], 0)
        self.assertFalse(probe["measured_latency"])

    def test_surrogate_gains_are_bounded(self) -> None:
        _, observed = reference.synth("onset_offset")
        result = reference.surrogate_offline(observed)
        self.assertGreaterEqual(result["gain_min"], reference.GAIN_FLOOR - 1e-12)
        self.assertLessEqual(result["gain_max"], 1.0 + 1e-12)


class SessionTests(unittest.TestCase):
    def test_one_clip_is_accepted(self) -> None:
        _, observed = reference.synth("quiet_speech")
        session = reference.OfflineSession()
        output = session.process_clip(observed)
        self.assertEqual(len(output), len(observed))
        self.assertTrue(session.completed)
        self.assertEqual(session.calls, 1)

    def test_second_clip_is_rejected(self) -> None:
        _, observed = reference.synth("quiet_speech")
        session = reference.OfflineSession()
        session.process_clip(observed)
        with self.assertRaises(ValueError) as caught:
            session.process_clip(observed)
        self.assertIn("offline_clip_already_complete", str(caught.exception))

    def test_adverse_clip_cases_fail_closed(self) -> None:
        cases = reference.clip_adverse_cases()
        expected = {
            "second_clip", "empty_clip", "oversized_clip", "nonfinite_sample",
            "infinite_sample", "string_clip", "boolean_sample", "out_of_range_sample",
            "after_close",
        }
        self.assertEqual(set(cases["cases"]), expected)
        for name, case in cases["cases"].items():
            with self.subTest(name=name):
                self.assertTrue(case["status"].startswith("rejected"))
                self.assertTrue(case["state_unchanged"])
        self.assertTrue(cases["state_after_close_unchanged_by_rejected_call"])

    def test_lifecycle_has_no_streaming_api(self) -> None:
        lifecycle = reference.lifecycle_evidence()
        self.assertTrue(lifecycle["one_clip_completed"])
        self.assertTrue(lifecycle["one_call_only"])
        self.assertTrue(lifecycle["close_idempotent"])
        self.assertTrue(lifecycle["incremental_process_api_absent"])
        self.assertTrue(lifecycle["flush_api_absent"])
        self.assertTrue(lifecycle["reset_api_absent"])
        self.assertTrue(lifecycle["zero_length_clip_rejected"])
        self.assertTrue(lifecycle["process_after_close"].startswith("rejected"))

    def test_statelessness_is_reported(self) -> None:
        state = reference.statelessness_evidence()
        self.assertTrue(state["clip_b_independent_of_prior_clip"])
        self.assertTrue(state["clip_a_replay_identical"])
        self.assertFalse(state["state_carried_between_clips"])
        self.assertFalse(state["shared_mutable_state"])
        self.assertFalse(state["real_recurrent_state_loaded"])

    def test_run_offline_reports_one_call(self) -> None:
        _, observed = reference.synth("onset_offset")
        result = reference.run_offline(observed)
        self.assertEqual(result["calls"], 1)
        self.assertEqual(result["input_samples"], result["output_samples"])


class ScoringTests(unittest.TestCase):
    def test_identity_scores_against_itself(self) -> None:
        clean, _ = reference.synth("active_speech")
        scored = reference.score(clean, clean)
        self.assertGreater(scored["snr_db"], 100.0)
        self.assertGreater(scored["si_sdr_db"], 100.0)
        self.assertEqual(scored["output_rms"], reference._rms(clean))

    def test_score_rejects_length_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            reference.score([0.0, 1.0], [0.0])

    def test_idle_noise_has_no_snr_or_si_sdr(self) -> None:
        _, observed = reference.synth("idle_noise")
        scored = reference.score([0.0] * len(observed), observed)
        self.assertIsNone(scored["snr_db"])
        self.assertIsNone(scored["si_sdr_db"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_report_identity_and_disposition(self) -> None:
        self.assertEqual(self.report["task_id"], reference.TASK)
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["branch"], reference.BRANCH)
        self.assertEqual(self.report["status"], reference.STATUS)
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_report_claims_are_all_false(self) -> None:
        self.assertTrue(all(value is False for value in self.report["claims"].values()))
        skipped = {"descriptor_settings", "installed_v0_geometry_preserved"}
        self.assertTrue(all(value is False for key, value in self.report["boundary"].items()
                            if key not in skipped))

    def test_conditions_have_exact_offline_accounting(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, block in self.report["conditions"].items():
            with self.subTest(name=name):
                accounting = block["output_accounting"]
                self.assertEqual(accounting["input_samples"], reference.SAMPLES)
                self.assertEqual(accounting["output_samples"], reference.SAMPLES)
                self.assertEqual(accounting["startup_padding_samples"], 0)
                self.assertEqual(accounting["tail_padding_emitted_samples"], 0)
                self.assertEqual(accounting["algorithmic_lag_samples"], 0)
                self.assertFalse(accounting["flush_required"])
                self.assertTrue(block["frame_loop_matches_whole"])
                self.assertFalse(block["split_halves_matches_whole"])

    def test_identity_control_is_exact(self) -> None:
        for name, block in self.report["conditions"].items():
            with self.subTest(name=name):
                identity = block["variants"]["identity_passthrough"]
                noisy = block["variants"]["noisy_control"]
                self.assertEqual(identity["snr_db"], noisy["snr_db"])
                self.assertEqual(identity["si_sdr_db"], noisy["si_sdr_db"])

    def test_no_invalid_outputs(self) -> None:
        for name, block in self.report["conditions"].items():
            for variant, scored in block["variants"].items():
                with self.subTest(condition=name, variant=variant):
                    self.assertEqual(scored["nonfinite_samples"], 0)
                    self.assertEqual(scored["clipped_samples"], 0)

    def test_regressions_are_negative(self) -> None:
        self.assertTrue(self.report["regression_assessment"]["performed"])
        for item in self.report["regressions"]:
            self.assertLess(item["surrogate_whole_clip"], item["noisy_control"])

    def test_offline_boundary_is_not_streaming(self) -> None:
        boundary = self.report["offline_boundary"]
        self.assertEqual(boundary["processing_mode"], "offline_whole_clip")
        self.assertFalse(boundary["incremental_calls_supported"])
        self.assertFalse(boundary["streaming_supported"])
        self.assertFalse(boundary["flush_required"])
        self.assertEqual(boundary["algorithmic_lag_samples"], 0)
        self.assertFalse(boundary["lag_modelled"])
        self.assertFalse(boundary["lag_measured"])
        self.assertFalse(boundary["device_clock_used"])
        self.assertFalse(boundary["deadline_measured"])

    def test_partial_tail_and_alignment(self) -> None:
        boundary = self.report["offline_boundary"]
        self.assertEqual(boundary["tail_control"]["internal_frame_padding_samples"], 37)
        self.assertEqual(boundary["tail_control"]["output_samples"], 32_123)
        self.assertTrue(boundary["alignment_probe"]["peak_index_preserved"])
        self.assertFalse(boundary["alignment_probe"]["measured_latency"])

    def test_complete_clip_is_required(self) -> None:
        causality = self.report["offline_boundary"]["causality"]
        self.assertTrue(causality["requires_complete_clip"])
        self.assertGreater(causality["prefix_samples_changed_by_future_audio"], 0)
        self.assertFalse(causality["prefix_available_before_full_clip"])

    def test_all_gates_are_blocked(self) -> None:
        for gate in self.report["gates"]:
            with self.subTest(gate=gate["name"]):
                self.assertEqual(gate["status"], "blocked")
                self.assertTrue(gate["evidence"])
                self.assertTrue(gate["reopen"])

    def test_exact_blockers_and_reopen_conditions(self) -> None:
        blockers = " ".join(self.report["exact_blockers"])
        self.assertIn("model_revision is null", blockers)
        self.assertIn("dpdfnet 0.6.0", blockers)
        self.assertIn("Apache-2.0", blockers)
        self.assertIn("No rights-cleared", blockers)
        reopen = " ".join(self.report["reopen_conditions"])
        self.assertIn("immutable artifact revision", reopen)
        self.assertIn("pinned dpdfnet 0.6.0 runtime", reopen)
        self.assertIn("written artifact-specific", reopen)
        self.assertIn("whole-clip offline reference outputs", reopen)

    def test_source_context_is_provenance_only(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["pilot_offline_mean_delta_si_sdr_db"], 7.7973)
        self.assertEqual(context["pilot_offline_mean_delta_snr_db"], 7.8522)
        self.assertEqual(context["pilot_offline_mean_delta_stoi"], 0.0329)
        self.assertEqual(context["pilot_offline_batch_rtf"], 0.0989)
        self.assertIsNone(context["offline_content_delay_samples"])
        self.assertEqual(context["streaming_only_cpp_content_delay_samples"], 800)
        self.assertIn("not reproduced", context["disclaimer"])

    def test_repeatability_is_byte_identical(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_canonical_report_has_no_negative_zero(self) -> None:
        self.assertNotIn(b"-0.0", reference.canonical_report_bytes(self.report))

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)


class StaticArtifactTests(unittest.TestCase):
    def test_adapter_is_offline_and_unregistered(self) -> None:
        adapter = reference.build_adapter()
        self.assertEqual(adapter["modes"], ["offline"])
        self.assertEqual(adapter["asset_readiness"], "blocked")
        self.assertTrue(adapter["configuration"]["whole_clip_only"])
        self.assertFalse(adapter["configuration"]["streaming_supported"])
        self.assertFalse(adapter["real_runtime_used"])
        self.assertFalse(adapter["weights_accessed"])
        self.assertFalse(adapter["registration"]["registered"])

    def test_readiness_is_blocked(self) -> None:
        readiness = reference.build_readiness()
        self.assertEqual(readiness["status"], "blocked")
        self.assertFalse(readiness["qualified"])
        self.assertEqual(readiness["decision"], "DEFER")
        self.assertEqual(readiness["admission"]["reason_codes"], [
            "model_revision_unpinned",
            "download_revision_mutable",
            "asset_bytes_absent",
            "runtime_unavailable",
            "rights_not_cleared",
        ])

    def test_contract_is_fail_closed(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertFalse(contract["qualification"]["qualifies"])
        self.assertFalse(contract["qualification"]["missing_result_promoted"])
        self.assertTrue(all(value is False for value in contract["public_surface"].values()))
        self.assertTrue(all(value is False for value in contract["claims"].values()))

    def test_source_pin_sets_are_complete(self) -> None:
        self.assertIn("research/voice-enhancement-20261101/candidate_matrix.csv",
                      reference.SOURCE_PINS)
        self.assertIn("adapters/dpdfnet/adapter.json", reference.SOURCE_PINS)
        self.assertIn("research/noise_suppression_assets_20261027.json",
                      reference.SOURCE_PINS)
        self.assertIn("CONTRACTS.md", reference.BOUNDARY_PINS)


class GeneratedArtifactTests(unittest.TestCase):
    def test_report_on_disk_matches_regeneration_and_sidecar(self) -> None:
        report_path = HERE / "report.json"
        sidecar_path = HERE / "report.json.sha256"
        self.assertTrue(report_path.is_file())
        payload = report_path.read_bytes()
        self.assertEqual(payload, cli.report_bytes())
        digest = reference.sha256(payload)
        self.assertEqual(sidecar_path.read_text(encoding="utf-8").strip(),
                         digest + "  report.json")

    def test_generated_json_files_are_canonical(self) -> None:
        self.assertEqual((HERE / "adapter.json").read_bytes(),
                         reference.canonical_bytes(reference.build_adapter()) + b"\n")
        self.assertEqual((HERE / "readiness.json").read_bytes(),
                         reference.canonical_bytes(reference.build_readiness()) + b"\n")
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         cli.contract_bytes(cli.contract_pins()))

    def test_readme_digest_table_is_current(self) -> None:
        rows = verify.readme_digest_pins()
        self.assertEqual(set(rows), set(verify.README_DIGEST_FILES))
        for name, (digest, size) in rows.items():
            path = HERE / name
            self.assertEqual(reference.sha256_file(path), digest)
            self.assertEqual(path.stat().st_size, size)

    def test_license_sidecars_cover_generated_artifacts(self) -> None:
        expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
        present = {path.relative_to(HERE).as_posix()
                   for path in HERE.rglob("*") if path.is_file()}
        self.assertEqual(present, expected)
        for name in expected:
            if name.endswith((".py", ".md")) or name.endswith(".license"):
                continue
            if name == "SOURCES.sha256":
                sidecar = HERE / "SOURCES.sha256.license"
            else:
                sidecar = HERE / (name + ".license")
            self.assertTrue(sidecar.is_file(), sidecar.name)

    def test_manifest_is_byte_reproducible(self) -> None:
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(), cli.manifest_bytes())


if __name__ == "__main__":
    unittest.main()
