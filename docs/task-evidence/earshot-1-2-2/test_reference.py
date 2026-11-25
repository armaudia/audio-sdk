# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local SDK-EARSHOT-1-2-2 evidence package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

import fixture
import reference
import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
READINESS = HERE / "readiness.json"
ADAPTER = HERE / "adapter.json"


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_loads(REPORT.read_text(encoding="utf-8"))
        cls.contract = reference.strict_loads(CONTRACT.read_text(encoding="utf-8"))
        cls.readiness = reference.strict_loads(
            READINESS.read_text(encoding="utf-8"))
        cls.adapter = reference.strict_loads(ADAPTER.read_text(encoding="utf-8"))
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_bytes(),
                         f"{digest}  report.json\n".encode("ascii"))

    def test_03_report_is_canonical_strict_json(self) -> None:
        self.assertEqual(REPORT.read_bytes(),
                         reference.canonical_report_bytes(self.report))
        self.assertFalse(reference.has_negative_zero(self.report))

    def test_04_disposition_is_defer_incomplete_not_qualified(self) -> None:
        for key, expected in (
                ("status", "proposal_only_synthetic_incomplete"),
                ("evidence_status", "incomplete"),
                ("qualification_status", "not_qualified"),
                ("decision", "DEFER"),
                ("defer_before", "opt_in_adapter_exposure"),
                ("profile", "analysis")):
            self.assertEqual(self.report[key], expected, key)
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_05_boundary_is_opt_in_unregistered_and_unchanged(self) -> None:
        keys = ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "installed_v0_behavior_change", "processor_exposure", "ci_change")
        for key in keys:
            self.assertIs(self.report["boundary"][key], False, key)
            self.assertIs(self.contract["boundary"][key], False, key)
        self.assertEqual(self.report["boundary"]["descriptor_settings"], {})

    def test_06_public_and_asset_geometry_pinned(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["sdk_v0_sample_rate_hz"], 16000)
        self.assertEqual(fmt["sdk_v0_channels"], 1)
        self.assertEqual(fmt["sdk_v0_sample_format"], "f32")
        self.assertEqual(fmt["sdk_v0_frame_samples"], 160)
        self.assertEqual(fmt["asset_sample_rate_hz"], 16000)
        self.assertEqual(fmt["asset_channels"], 1)
        self.assertEqual(fmt["asset_sample_format"], "float32")
        self.assertEqual(fmt["asset_frame_samples"], 256)
        self.assertEqual(fmt["asset_frame_duration_ms"], 16)
        self.assertEqual(fmt["decision_threshold"], 0.5)
        self.assertEqual(fmt["window_samples"], 32000)
        self.assertEqual(fmt["window_frames"], 125)
        self.assertTrue(fmt["sdk_v0_geometry_preserved"])
        self.assertFalse(fmt["sdk_callback_invoked"])
        self.assertFalse(fmt["frame_cadence_parity_with_real_runtime_claimed"])

    def test_07_caller_supplied_asset_contract_is_exact(self) -> None:
        contract = self.report["caller_supplied_asset_contract"]
        self.assertEqual(contract, reference.CALLER_ASSET_CONTRACT)
        self.assertEqual(set(contract["required_fields"]),
                         reference.REQUIRED_ASSET_FIELDS)
        self.assertEqual(contract["pinned_values"]["sample_rate_hz"], 16000)
        self.assertEqual(contract["pinned_values"]["frame_samples"], 256)
        self.assertEqual(contract["pinned_values"]["threshold"], 0.5)
        self.assertEqual(contract["pinned_values"]["source_commit"],
                         reference.UPSTREAM_COMMIT)
        self.assertTrue(contract["weights_embedded_in_wheel"])
        self.assertFalse(contract["separate_model_asset_required"])
        self.assertFalse(contract["asset_is_vendored"])

    def test_08_asset_is_absent_and_not_loaded(self) -> None:
        resolution = self.report["asset_resolution"]
        for key in ("requested", "manifest_present", "wheel_present_in_sdk_worktree",
                    "wheel_present_in_research_workspace", "environment_present",
                    "source_archive_present", "runtime_library_present", "verified",
                    "loaded", "executed", "imported"):
            self.assertIs(resolution[key], False, key)
        self.assertTrue(resolution["surrogate_used"])
        self.assertTrue(resolution["weights_embedded_in_wheel"])
        self.assertFalse((fixture.workspace_root()
                          / reference.WHEEL_PATH).exists())
        self.assertFalse((fixture.workspace_root()
                          / reference.RUNTIME_ENV_PATH).exists())
        self.assertFalse((SDK_ROOT / "adapters/earshot-vad").exists())

    def test_09_surrogate_is_not_earshot(self) -> None:
        surrogate = self.report["surrogate"]
        self.assertEqual(surrogate["identity"],
                         "earshot-1-2-2-boundary-surrogate-v1")
        for key in ("is_earshot", "is_neural_network", "weights", "checkpoint",
                    "model_archive", "quality_claim"):
            self.assertIs(surrogate[key], False, key)
        self.assertEqual(surrogate["frame_samples"], 256)
        self.assertEqual(surrogate["decision_threshold"], 0.5)
        self.assertTrue(surrogate["deterministic"])
        self.assertTrue(surrogate["pure_synthetic"])

    def test_10_strata_cover_every_truth_segment(self) -> None:
        self.assertEqual(set(self.report["strata"]),
                         {segment["id"] for segment in fixture.SEGMENTS})
        totals = fixture.truth_totals()
        self.assertEqual(totals, {"speech": 15360, "nonspeech": 13312,
                                  "unknown": 3328})
        for name, row in self.report["strata"].items():
            segment = next(segment for segment in fixture.SEGMENTS
                           if segment["id"] == name)
            self.assertEqual(row["start_sample"], segment["start"])
            self.assertEqual(row["end_sample"], segment["end"])
            self.assertEqual(row["samples"], segment["end"] - segment["start"])
            self.assertEqual(row["truth"], segment["truth"])
        self.assertFalse(self.report["strata"]["unknown-tail"]["scored"])

    def test_11_detections_are_sample_weighted_and_complete(self) -> None:
        detections = self.report["detections"]
        overall = detections["overall"]
        self.assertEqual(sum(overall.values()),
                         detections["speech_samples"] + detections["nonspeech_samples"])
        self.assertEqual(overall["TP"] + overall["FN"], 15360)
        self.assertEqual(overall["FP"] + overall["TN"], 13312)
        self.assertEqual(detections["unknown_excluded_samples"], 3328)
        self.assertEqual(detections["invalid_excluded_samples"], 0)
        self.assertAlmostEqual(detections["speech_miss_rate"],
                               overall["FN"] / 15360, places=12)
        self.assertAlmostEqual(detections["false_alarm_rate"],
                               overall["FP"] / 13312, places=12)
        self.assertEqual(detections["frame_resolution_samples"], 256)

    def test_12_stratified_fn_fp_and_quiet_active_controls(self) -> None:
        strata = self.report["strata"]
        self.assertEqual(strata["active-a"]["truth"], "speech")
        self.assertEqual(strata["active-a"]["FN"], 0)
        self.assertEqual(strata["active-a"]["TP"], 7936)
        self.assertGreater(strata["quiet-a"]["FN"], 0)
        self.assertEqual(strata["quiet-b"]["FN"], 3328)
        self.assertEqual(strata["quiet-b"]["TP"], 0)
        self.assertGreater(strata["noise-burst"]["FP"], 0)
        self.assertEqual(strata["noise-burst"]["FP"], 1280)
        for name in ("idle-a", "idle-b", "idle-c", "idle-d"):
            self.assertEqual(strata[name]["FP"], 0, name)
            self.assertEqual(strata[name]["TP"], 0, name)
            self.assertEqual(strata[name]["truth"], "nonspeech")

    def test_13_probabilities_and_calibration_are_finite(self) -> None:
        probabilities = self.report["probabilities"]
        for key in ("brier_score", "log_loss", "mean_probability",
                    "min_probability", "max_probability"):
            self.assertIsInstance(probabilities[key], float, key)
        self.assertGreaterEqual(probabilities["brier_score"], 0.0)
        self.assertGreaterEqual(probabilities["log_loss"], 0.0)
        self.assertLessEqual(probabilities["min_probability"],
                             probabilities["max_probability"])
        self.assertEqual(probabilities["known_events"], 112)
        self.assertEqual(probabilities["unknown_events"], 13)
        bins = probabilities["calibration_bins"]
        self.assertEqual(len(bins), 5)
        self.assertEqual(sum(item["events"] for item in bins), 112)
        self.assertEqual(sum(item["samples"] for item in bins), 28672)

    def test_14_boundaries_match_and_report_onset_offset_delay(self) -> None:
        boundaries = self.report["boundaries"]
        self.assertEqual(boundaries["truth_runs"],
                         [[2048, 6144], [8192, 16128], [18688, 22016]])
        self.assertEqual(boundaries["detected_runs"],
                         [[3584, 6144], [8192, 16128], [17408, 18688]])
        self.assertEqual(boundaries["matched_count"], 2)
        quiet, active, missed = boundaries["matches"]
        self.assertEqual(quiet["onset_delay_samples"], 1536)
        self.assertEqual(quiet["onset_delay_ms"], 96.0)
        self.assertEqual(quiet["offset_delay_samples"], 0)
        self.assertEqual(active["onset_delay_samples"], 0)
        self.assertEqual(active["offset_delay_samples"], 0)
        self.assertFalse(missed["matched"])
        self.assertEqual(boundaries["missed_truth_runs"], [[18688, 22016]])
        self.assertEqual(boundaries["false_detected_runs"], [[17408, 18688]])
        self.assertEqual(boundaries["tolerance_samples"], 0)

    def test_15_always_baselines_expose_metric_behavior(self) -> None:
        baselines = self.report["baselines"]
        self.assertEqual(baselines["always_speech"],
                         {"TP": 15360, "FN": 0, "FP": 13312, "TN": 0,
                          "speech_miss_rate": 0.0, "false_alarm_rate": 1.0})
        self.assertEqual(baselines["always_nonspeech"],
                         {"TP": 0, "FN": 15360, "FP": 0, "TN": 13312,
                          "speech_miss_rate": 1.0, "false_alarm_rate": 0.0})
        self.assertTrue(baselines["diagnostic_only"])
        self.assertFalse(baselines["used_for_qualification"])

    def test_16_alignment_is_frame_cadence_not_device_timing(self) -> None:
        alignment = self.report["alignment"]
        self.assertTrue(alignment["frame_grid_exact"])
        self.assertEqual(alignment["frame_samples"], 256)
        self.assertEqual(alignment["frame_duration_ms"], 16)
        self.assertEqual(alignment["declared_analysis_delay_samples"], 0)
        self.assertEqual(alignment["matched_boundary_count"], 2)
        self.assertEqual(alignment["source_interval_mapping"], "identity")
        self.assertFalse(alignment["measured"])

    def test_17_state_controls_pass(self) -> None:
        for key, value in self.report["state"].items():
            self.assertTrue(value, key)
        parity = self.report["controls"]["streaming_parity"]
        self.assertTrue(parity["events_identical"])
        self.assertTrue(parity["fresh_session_identical"])
        self.assertEqual(parity["offline_digest"], parity["streaming_digest"])
        self.assertEqual(parity["offline_events"], 125)

    def test_18_caller_asset_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["caller_asset"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        self.assertEqual(controls["valid_manifest"],
                         {"status": "validated", "verified": True,
                          "loaded": False, "executed": False, "imported": False})
        for name in ("missing_manifest", "absent_file", "relative_path",
                     "hash_mismatch", "wrong_source_commit", "wrong_sample_rate",
                     "wrong_channels", "wrong_frame_size", "wrong_threshold",
                     "wrong_input_format", "unexpected_field"):
            self.assertEqual(controls[name]["status"], "rejected", name)

    def test_19_frame_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["frame"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        for name in ("nan", "infinite", "short", "long", "empty", "boolean",
                     "zero_final", "long_final"):
            self.assertEqual(controls["cases"][name]["reason"],
                             controls["cases"][name]["expected"], name)
            self.assertTrue(controls["cases"][name]["state_unchanged"], name)
        self.assertEqual(controls["final_partial_status"], "ok")
        self.assertEqual(controls["final_partial_end_sample"], 384)
        self.assertEqual(controls["final_partial_padded_samples"], 128)
        self.assertTrue(controls["state_unchanged_after_rejections"])

    def test_20_config_adverse_controls_reject(self) -> None:
        cases = self.report["controls"]["config_adverse"]
        for name in ("sample_rate_hz", "channels", "sample_format",
                     "frame_samples", "decision_threshold", "real_runtime",
                     "wheel_or_licensed_runtime_used", "missing_session_id"):
            self.assertEqual(cases[name]["status"], "rejected", name)

    def test_21_event_bus_records_drops_and_rejections(self) -> None:
        bus = self.report["controls"]["event_bus"]
        self.assertEqual(bus["dropped_sequences"], [2, 5, 17])
        self.assertEqual(bus["gaps"], [[2, 2], [5, 5], [17, 17]])
        self.assertEqual(bus["fabricated_events"], 0)
        self.assertTrue(bus["all_rejected_without_state_change"])
        for name, case in bus["adverse_cases"].items():
            self.assertTrue(case["state_unchanged"], name)
            self.assertFalse(case["accepted"], name)

    def test_22_adverse_matches_controls(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["all_invalid_cases_rejected"])
        self.assertTrue(adverse["caller_asset_fail_closed"])
        self.assertTrue(adverse["frame_fail_closed"])
        self.assertTrue(adverse["event_bus_fail_closed"])
        self.assertEqual(adverse["config_rejections"],
                         self.report["controls"]["config_adverse"])
        self.assertEqual(adverse["frame_rejections"],
                         self.report["controls"]["frame"]["cases"])
        self.assertEqual(adverse["caller_asset_rejections"],
                         self.report["controls"]["caller_asset"])

    def test_23_invalid_is_not_nonspeech(self) -> None:
        control = self.report["controls"]["invalid_vs_nonspeech"]
        for name in ("invalid_validity", "missing_validity",
                     "nonfinite_probability", "out_of_range_probability"):
            self.assertEqual(control["rejected_cases"][name]["status"], "rejected")
        self.assertTrue(control["unknown_event_admitted"])
        self.assertEqual(control["unknown_excluded_samples"], 256)
        self.assertEqual(control["false_positives"], 0)
        self.assertFalse(control["invalid_counted_as_nonspeech"])

    def test_24_partial_tail_pads_for_inference_and_clips(self) -> None:
        control = self.report["controls"]["partial_tail"]
        self.assertEqual(control["stream_samples"], 384)
        self.assertEqual(control["full_frames"], 1)
        self.assertEqual(control["final_valid_samples"], 128)
        self.assertEqual(control["final_padded_samples"], 128)
        self.assertEqual(control["final_end_sample"], 384)
        self.assertEqual(control["final_available_ns"],
                         fixture.ORIGIN_NS + 384 * fixture.SAMPLE_NS
                         + fixture.PROCESSING_DELAY_NS)
        self.assertTrue(control["frame_interval_clipped_to_real_samples"])

    def test_25_cross_hop_projection_is_exact(self) -> None:
        control = self.report["controls"]["cross_hop"]
        self.assertEqual(control["frames"], [[0, 106], [1, 74]])
        self.assertEqual(control["overlap_samples"], 180)
        self.assertEqual(control["truth_interval"], [2048, 6144])
        self.assertEqual(control["truth_hops"], 16)
        self.assertEqual(control["truth_overlap_samples"], 4096)
        self.assertEqual(control["source_time_mapping"], "identity")

    def test_26_intervals_and_availability_are_exact(self) -> None:
        control = self.report["controls"]["interval_and_availability"]
        self.assertTrue(control["frame_boundaries_exact"])
        self.assertEqual(control["probability_events_cover_samples"],
                         [0, 32000])
        self.assertTrue(control["known_availability_strictly_increasing"])
        self.assertTrue(control["unknown_events_have_no_availability"])
        self.assertFalse(control["measured"])
        availability = self.report["availability"]
        self.assertFalse(availability["measured"])
        self.assertFalse(availability["device_timing"])
        self.assertTrue(availability["signal_timestamp_is_not_availability"])
        self.assertEqual(availability["frame_samples"], 256)

    def test_27_source_pins_match_research_files(self) -> None:
        self.assertEqual(self.report["source_pins"], fixture.SOURCE_PINS)
        self.assertEqual(self.contract["source_pins"], fixture.SOURCE_PINS)
        for path, digest in fixture.SOURCE_PINS.items():
            actual = hashlib.sha256(
                (fixture.resolve_source_path(path)).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_28_boundary_pins_match_worktree(self) -> None:
        self.assertEqual(self.report["boundary_pins"], fixture.BOUNDARY_PINS)
        for path, digest in fixture.BOUNDARY_PINS.items():
            actual = hashlib.sha256((SDK_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_29_contract_digest_matches(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertEqual(self.report["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
        self.assertEqual(self.readiness["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())

    def test_30_readiness_is_strict_and_blocked(self) -> None:
        self.assertEqual(READINESS.read_bytes(), reference.readiness_bytes())
        self.assertEqual(self.readiness["report_sha256"],
                         hashlib.sha256(REPORT.read_bytes()).hexdigest())
        for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                    "ready_for_release", "quality_pass"):
            self.assertIs(self.readiness[key], False, key)
        self.assertEqual(self.readiness["blocked_gates"],
                         [name for name, _ in reference.GATE_DEFINITIONS])
        self.assertEqual(self.readiness["exact_blocker"],
                         reference.EXACT_BLOCKERS[0])
        self.assertEqual(self.readiness["reopen_condition"],
                         reference.REOPENING_CONDITIONS[0])
        self.assertFalse(self.readiness["external_asset"]["present"])
        self.assertTrue(self.readiness["external_asset"]["required"])
        self.assertTrue(self.readiness["external_asset"]["weights_embedded_in_wheel"])

    def test_31_adapter_is_task_local_and_not_implemented(self) -> None:
        self.assertEqual(ADAPTER.read_bytes(), reference.adapter_bytes())
        self.assertEqual(self.adapter["task_id"], reference.TASK)
        self.assertTrue(self.adapter["task_local"])
        for key in ("implemented", "registered", "enabled_by_default",
                    "default_selected", "public_api_abi_change",
                    "provider_registration", "descriptor_registry_change",
                    "installed_v0_behavior_change", "asset_present"):
            self.assertIs(self.adapter[key], False, key)
        self.assertTrue(self.adapter["caller_supplied_asset_required"])
        self.assertEqual(self.adapter["activation"], "deferred_until_gates_clear")
        self.assertIsNone(self.adapter["entrypoint"])

    def test_32_all_gates_blocked_with_reopen_conditions(self) -> None:
        self.assertEqual(len(self.report["gates"]),
                         len(reference.GATE_DEFINITIONS))
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])
        self.assertEqual(self.report["exact_blockers"],
                         reference.EXACT_BLOCKERS)
        self.assertEqual(self.report["missing_evidence"],
                         reference.MISSING_EVIDENCE)
        self.assertEqual(self.report["reopening_conditions"],
                         reference.REOPENING_CONDITIONS)

    def test_33_repeatability_is_three_identical_cold_starts(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        core = {key: value for key, value in self.report.items()
                if key != "repeatability"}
        self.assertEqual(repeat["digests"][0],
                         hashlib.sha256(reference.canonical_bytes(core)).hexdigest())

    def test_34_source_reported_values_are_provenance_only(self) -> None:
        source = self.report["source_reported"]
        self.assertEqual(source["status"], "source_reported_not_reproduced")
        self.assertFalse(source["used_for_qualification"])
        findings = {item["metric"]: item["value"] for item in source["findings"]}
        self.assertEqual(findings["false_negative_rate"], 0.2432)
        self.assertEqual(findings["false_positive_rate"], 0.1030)
        self.assertEqual(findings["average_cost_per_20ms_frame"], 13.41)
        self.assertEqual(findings["integration_offline_streaming_parity"], "exact")
        self.assertEqual(self.report["timing"]["source_reported_cost_us_per_20ms_frame"],
                         13.41)
        self.assertFalse(
            self.report["timing"]["source_reported_cost_used_for_qualification"])

    def test_35_licensing_rights_remain_blocked(self) -> None:
        licensing = self.report["licensing_analysis"]
        self.assertEqual(licensing["upstream_package_license_expression"],
                         "MIT OR Apache-2.0")
        for key in ("standalone_license_file_in_wheel",
                    "source_archive_redistribution_clearance",
                    "wheel_redistribution_clearance", "product_use_clearance",
                    "training_data_provenance_established",
                    "legal_review_completed",
                    "asset_copied_vendored_built_or_downloaded"):
            self.assertIs(licensing[key], False, key)
        self.assertEqual(licensing["blocked_gate"],
                         "wheel_and_embedded_weight_rights")

    def test_36_strict_parsers_reject_bad_inputs(self) -> None:
        result = reference.strict_rejection_examples()
        self.assertEqual(result["bad_json_rejected"], result["bad_json_total"])
        self.assertEqual(result["bad_pins_rejected"], result["bad_pins_total"])
        self.assertEqual(result["bad_readme_rejected"],
                         result["bad_readme_total"])

    def test_37_sources_manifest_is_complete_and_deterministic(self) -> None:
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
        self.assertEqual({raw for _, raw in pins}, reference.allowed_pin_keys())
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))
        for path in reference.LOCAL_PIN_PATHS:
            self.assertTrue((HERE / path).is_file(), path)

    def test_38_base_commit_and_branch_are_pinned(self) -> None:
        self.assertEqual(self.report["base_commit"],
                         "d5b11912cd09e87296cd9d4654f1917c9cb94258")
        self.assertEqual(self.report["branch"], "swarm/SDK-EARSHOT-1-2-2")

    def test_39_readme_digest_tables_verify(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        expected = reference.expected_readme_keys()
        self.assertEqual(counts["source"], len(expected["source"]))
        self.assertEqual(counts["boundary"], len(expected["boundary"]))
        self.assertEqual(counts["artifacts"], len(expected["artifacts"]))
        self.assertEqual(counts["external-absent"],
                         len(expected["external-absent"]))

    def test_40_no_prohibited_real_model_audio_device_or_release_claim(self) -> None:
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)
        for key in ("caller_supplied_asset_present", "earshot_source_executed",
                    "earshot_runtime_executed", "earshot_wheel_imported",
                    "wheel_downloaded", "wheel_loaded", "model_weights_loaded",
                    "real_audio", "real_labels", "network_used", "device_timing",
                    "listening_result", "benchmark_claim", "release_claim",
                    "registered_provider"):
            self.assertIs(self.report["scope"][key], False, key)

    def test_41_analysis_profile_checklist_is_complete(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "analysis")
        for item in reference.ACCEPTANCE_PROFILE_ITEMS:
            self.assertIs(profile[item], True, item)
        self.assertEqual(profile["scorer_sha256"],
                         fixture.sha256_file(HERE / "scorer.py"))
        self.assertEqual(profile["fixture_sha256"],
                         fixture.sha256_file(HERE / "fixture.py"))

    def test_42_report_and_fixture_keys_are_exact(self) -> None:
        self.assertEqual(set(self.report), reference.REPORT_KEYS)
        self.assertEqual(fixture.FIXTURE_SPEC_DIGEST,
                         fixture.sha256_bytes(fixture.canonical_bytes(
                             fixture.fixture_spec())))

    def test_43_scorer_rejects_invalid_records_independently(self) -> None:
        with self.assertRaises(ValueError):
            scorer.score_stream([], [])
        event = {"validity": "known", "probability": 0.5, "decision": True,
                 "start_sample": 0, "end_sample": 256}
        with self.assertRaises(ValueError):
            scorer.score_stream([event], [])
        bad = dict(event, probability=float("nan"))
        with self.assertRaises(ValueError):
            scorer.score_stream([bad], [])

    def test_44_caller_asset_validator_is_strict(self) -> None:
        with self.assertRaises(ValueError):
            reference.validate_caller_asset({})
        manifest = {
            "wheel_path": "/nonexistent/earshot.whl",
            "wheel_sha256": "0" * 64,
            "source_commit": reference.UPSTREAM_COMMIT,
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 256,
            "threshold": 0.5,
            "input_format": "float32",
        }
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)
        manifest["wheel_path"] = "relative.whl"
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
