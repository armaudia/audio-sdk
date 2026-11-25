# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-10 evidence map."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


class StrictJsonTests(unittest.TestCase):
    def test_canonical_bytes_are_order_independent(self):
        left = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        right = reference.canonical_bytes({"a": [2, 3], "b": 1})
        self.assertEqual(left, right)
        self.assertTrue(left.endswith(b"\n"))

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_loads('{"a":NaN}')

    def test_infinity_rejected(self):
        for token in ("Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(reference.MapError):
                    reference.strict_json_loads('{"a":%s}' % token)

    def test_noncanonical_python_value_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.canonical_bytes({"a": float("nan")})


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()
        self.snapshot = self.builder.snapshot()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["readiness"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")

    def test_all_eight_release_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates], ["RG-0%d" % n for n in range(1, 9)])
        self.assertTrue(all(gate["blocked"] is True for gate in gates))

    def test_no_public_or_release_change(self):
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        for key in (
            "real_speech",
            "real_corpus",
            "real_device_response",
            "weights",
            "runtime_invocation",
            "listening",
            "device_timing",
            "bandwidth_extension",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "CLN-10")
        self.assertEqual(self.report["taxonomy"]["name"], "Tonal correction and interference filtering")
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S19", "S46"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F08")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-10")
        self.assertEqual(self.report["profile"], "DSP")

    def test_category_boundaries_are_named(self):
        scope = self.report["category_scope"]
        self.assertEqual(scope["not_background_noise_suppression_category"], "CLN-01")
        self.assertEqual(scope["not_transient_click_repair_category"], "CLN-02")
        self.assertEqual(scope["not_wind_or_microphone_disturbance_category"], "CLN-03")
        self.assertEqual(scope["not_level_or_loudness_control_category"], "CLN-09")
        self.assertEqual(scope["not_feedback_or_howling_category"], "CLN-11")
        self.assertEqual(scope["not_bandwidth_extension_category"], "RST-02")
        self.assertEqual(scope["not_codec_artifact_restoration_category"], "RST-03")
        self.assertIs(scope["tonal_correction_only"], True)

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        for token in ("high-pass", "notch", "equalization", "inverse-eq", "differentiable biquads", "multiband"):
            self.assertIn(token, families)

    def test_source_leads_are_s19_and_s46(self):
        leads = self.report["source_leads"]
        self.assertEqual([lead["source_id"] for lead in leads], ["S19", "S46"])
        self.assertEqual(leads[0]["title"], "FFmpeg audio filters")
        self.assertEqual(leads[1]["title"], "Speech Signal Improvement challenge findings")
        self.assertTrue(all(lead["finding"] for lead in leads))
        self.assertTrue(all(lead["gap_ids"] for lead in leads))

    def test_response_correction_is_not_bandwidth_generation(self):
        boundary = self.report["tonal_boundary"]
        self.assertIs(boundary["frequency_response_correction_is_not_bandwidth_generation"], True)
        self.assertIs(boundary["boosts_and_filtering_can_alter_speech"], True)
        self.assertIs(boundary["response_accuracy_is_separate_from_speech_preservation"], True)
        self.assertIs(boundary["hum_rumble_and_dc_are_not_broadband_noise"], True)
        self.assertIs(boundary["bandwidth_extension_claim"], False)

    def test_feedback_notch_and_dynamics_stay_adjacent(self):
        boundary = self.report["tonal_boundary"]
        self.assertIs(boundary["adaptive_feedback_notch_belongs_to_cln_11"], True)
        self.assertIs(boundary["level_and_dynamics_belong_to_cln_09"], True)
        family = next(row for row in self.report["method_families"] if row["family_id"] == "MF-M3")
        self.assertIn("cln-09", family["family"].lower())
        self.assertIn("adjacent", family["status"])

    def test_real_speech_device_and_weights_are_not_claimed(self):
        boundary = self.report["tonal_boundary"]
        self.assertIs(boundary["real_speech_or_device_response_staged"], False)
        self.assertIs(boundary["independent_licensed_speech_cohort_staged"], False)
        self.assertIs(boundary["neural_eq_weights_staged"], False)
        self.assertIs(boundary["real_device_response_calibration_measured"], False)
        self.assertIs(boundary["human_listening_result"], False)
        self.assertIs(boundary["device_timing_measured"], False)
        for key in (
            "real_speech_cohort_present",
            "device_response_calibration_present",
            "neural_eq_weights_present",
            "independent_heldout_real_benchmark_present",
        ):
            self.assertIs(self.report["discovery"][key], False, key)

    def test_no_human_listening_or_independent_benchmark(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["human_listening_result"], False)
        self.assertIs(classes["independent_heldout_benchmark"], False)
        self.assertIs(classes["clock_drift_or_device_timing"], False)
        self.assertIs(classes["device_loop_or_loudspeaker_measurement"], False)
        self.assertIs(classes["real_speech_result"], False)
        self.assertIs(classes["release_claim"], False)

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_paired_synthetic", classes)
        self.assertIn("historical_local_synthetic_holdout", classes)
        self.assertIn("source_only_conventional_reference", classes)
        self.assertIn("source_only_challenge_protocol", classes)
        self.assertIn("missing_no_local_cohort", classes)
        self.assertNotIn("human_listening_result", classes)
        self.assertNotIn("independent_heldout_benchmark", classes)
        self.assertNotIn("historical_local_predicted_metric", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["paired_synthetic_historical_local"], True)
        self.assertIs(classes["historical_local_synthetic_holdout"], True)
        self.assertIs(classes["learned_static_correction_execution"], True)
        self.assertIs(classes["source_reported_upstream_claim"], True)
        self.assertIs(classes["predicted_metric_not_human"], False)
        self.assertIs(classes["neural_reference_model_execution"], False)
        self.assertIs(classes["new_execution_in_this_survey"], False)

    def test_mutable_board_file_is_not_pinned_or_gated(self):
        self.assertNotIn(reference.BOARD_PATH, self.report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, self.report["boundary_pins"])
        self.assertIs(self.report["mutable_provenance"]["gate"], False)
        self.assertEqual(self.report["mutable_provenance"]["path"], reference.BOARD_PATH)
        self.assertNotIn("sha256_at_read", self.report["mutable_provenance"])
        raw = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn("source:" + reference.BOARD_PATH, raw)
        self.assertNotIn("worktree:" + reference.BOARD_PATH, raw)

    def test_board_status_edits_do_not_change_canonical_bytes(self):
        original = reference.strict_json_load

        def mutated(path):
            data = original(path)
            if Path(path).name == "TASKS.json":
                data = copy.deepcopy(data)
                for task in data["tasks"]:
                    task["status"] = "blocked"
                    task["owner"] = "another-agent"
                    task["notes"] = "mutable"
            return data

        with mock.patch.object(reference, "strict_json_load", mutated):
            rebuilt = reference.build_report()
        self.assertEqual(reference.canonical_bytes(rebuilt), reference.canonical_bytes(self.report))
        self.assertNotIn("sha256_at_read", rebuilt["mutable_provenance"])

    def test_board_projection_contains_only_linked_id_title_mode(self):
        board = reference.strict_json_load(reference.find_workspace() / reference.BOARD_PATH)
        projection = reference._board_projection(board)
        self.assertEqual(len(projection), 64)
        mutated = copy.deepcopy(board)
        for task in mutated["tasks"]:
            task["status"] = "done"
            task["owner"] = "somebody"
            task["notes"] = "mutable"
        self.assertEqual(reference._board_projection(mutated), projection)

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        self.assertEqual(len(self.report["historical_executions"]), 6)
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertIn("not rerun by this survey", row["scope"])

    def test_controls_and_assets_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"] + self.report["historical_executions"]:
            self.assertIn(row["source_pin"], pins)
        for row in self.report["comparison_inputs"] + self.report["reported_outcomes"]:
            self.assertIn(row["source_pin"], pins)

    def test_all_gaps_link_existing_board_tasks(self):
        board = reference.strict_json_load(reference.find_workspace() / reference.BOARD_PATH)
        ids = {task["id"] for task in board["tasks"]}
        links = {link["task_id"] for link in self.report["board_links"]}
        self.assertTrue(links)
        self.assertEqual(len(self.report["gaps"]), 11)
        for gap in self.report["gaps"]:
            self.assertTrue(gap["follow_up_ids"])
            self.assertTrue(set(gap["follow_up_ids"]) <= links)
            self.assertTrue(set(gap["follow_up_ids"]) <= ids)
            self.assertTrue(gap["owner_note"])

    def test_feasibility_links_exist_where_claimed(self):
        modes = {link["task_id"]: link["mode"] for link in self.report["board_links"]}
        for gap in self.report["gaps"]:
            if gap["feasibility_task_exists"]:
                self.assertIn("feasibility", {modes[tid] for tid in gap["follow_up_ids"]})

    def test_every_board_link_owns_at_least_one_gap(self):
        for link in self.report["board_links"]:
            self.assertIn(link["mode"], ("feasibility", "research-control", "foundation", "external-adapter"))
            self.assertTrue(link["title"])
            self.assertTrue(link["linked_gaps"])

    def test_board_projection_is_stable_across_builds(self):
        second = reference.build_report()
        self.assertEqual(
            self.report["board_link_projection_sha256"],
            second["board_link_projection_sha256"],
        )
        self.assertEqual(len(self.report["board_link_projection_sha256"]), 64)

    def test_three_fresh_process_builds_are_byte_identical(self):
        script = (
            "import sys; sys.path.insert(0, %r); import reference; "
            "sys.stdout.buffer.write(reference.canonical_bytes(reference.build_report()))" % str(HERE)
        )
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        outputs = []
        for _ in range(3):
            process = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                env=env,
                check=True,
            )
            outputs.append(process.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])
        self.assertEqual(outputs[0], reference.canonical_bytes(self.report))

    def test_report_file_and_sidecars_match_recomputed_bytes(self):
        raw = run.report_bytes()
        self.assertEqual((HERE / "report.json").read_bytes(), raw)
        digest = reference.sha256_bytes(raw)
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n",
        )

    def test_sources_manifest_is_sorted_and_complete(self):
        raw = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(raw, run.sources_bytes())
        labels = [line.split("  ", 1)[1] for line in raw.decode("ascii").splitlines()]
        self.assertEqual(labels, sorted(labels))
        self.assertEqual(len(labels), len(set(labels)))
        self.assertNotIn("local:SOURCES.sha256", labels)
        self.assertIn("local:contract.json", labels)
        self.assertIn("source:research/level_tone_control_20261028.md", labels)
        self.assertIn("worktree:docs/task-evidence/narrow-biquad-notch/report.json", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertTrue(all(row["class"] == "source_reported" for row in self.report["reported_outcomes"]))

    def test_source_study_and_local_replay_are_distinct(self):
        replay = next(row for row in self.report["historical_executions"] if row["id"] == "HE-4")
        study = next(row for row in self.report["historical_executions"] if row["id"] == "HE-6")
        self.assertEqual(replay["outcome_class"], "historical_local_paired_synthetic")
        self.assertEqual(study["outcome_class"], "historical_local_synthetic_holdout")
        self.assertAlmostEqual(study["values"]["learned_inverse_eq_rmse_db"], 2.577)
        self.assertAlmostEqual(study["values"]["identity_eq_rmse_db"], 4.414)
        self.assertIn("not rerun by this survey", study["scope"])

    def test_high_pass_row_is_installed_fixed_80hz(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-1")
        self.assertGreater(execution["values"]["rumble_attenuation_db"], 20.0)
        self.assertEqual(execution["values"]["content_delay_samples"], 0)
        self.assertIn("fixed 16 kHz", execution["scope"])
        component = next(row for row in self.report["component_census"] if row["component_id"] == "sdk-high-pass-80-hz")
        self.assertEqual(component["evidence_status"], "integrated")

    def test_notch_row_has_no_real_hum_result(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-2")
        self.assertIn("no mains-hum tracking", execution["scope"])
        self.assertLessEqual(execution["values"]["max_sweep_gain_error_db"], 0.01)

    def test_tilt_result_is_band_energy_not_listening(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-3")
        self.assertIn("not STOI/ESTOI", execution["scope"])
        self.assertGreater(execution["values"]["unity_peak_exceedances"], 0)
        self.assertIn("band-energy redistribution", execution["scope"])

    def test_inverse_eq_adverse_amplification_is_non_qualifying(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-4")
        self.assertGreater(execution["values"]["ill_conditioned_out_of_band_amplification_db"], 0.0)
        self.assertIn("non-qualifying", execution["scope"])
        self.assertIs(self.report["tonal_boundary"]["neural_eq_weights_staged"], False)

    def test_de_esser_preserves_low_band_only_synthetically(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-5")
        self.assertLess(
            execution["values"]["split_band_low_attenuation_db"],
            execution["values"]["split_band_high_attenuation_db"],
        )
        self.assertIn("exact synthetic identity only", execution["scope"])

    def test_acceptance_profile_maps_dsp_requirements(self):
        mapped = self.report["acceptance_profile"]["mapped"]
        self.assertEqual(self.report["acceptance_profile"]["profile"], "DSP")
        for key in ("spectral_response", "clean_preservation", "peaks_and_invalid_outputs", "state_and_delay"):
            self.assertIn(key, mapped)
        self.assertIn("no calibrated device", mapped["spectral_response"])
        self.assertEqual(len(self.report["acceptance_profile"]["blocked"]), 8)


class AtomicRejectionTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.builder.build()
        self.snapshot = self.builder.snapshot()

    def _assert_unchanged(self):
        self.assertEqual(self.builder.snapshot(), self.snapshot)

    def test_invalid_payload_type_rejected_without_state_change(self):
        with self.assertRaises(reference.MapError):
            self.builder.build(payload={"bad": object()})
        self._assert_unchanged()

    def test_nonfinite_payload_rejected_without_state_change(self):
        with self.assertRaises(reference.MapError):
            self.builder.build(payload={"bad": float("nan")})
        self._assert_unchanged()

    def test_missing_workspace_rejected_without_state_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(reference, "find_workspace", return_value=Path(tmp)):
                with self.assertRaises(reference.MapError):
                    self.builder.build()
        self._assert_unchanged()

    def test_tampered_pin_rejected_without_state_change(self):
        with mock.patch.dict(reference.WORKTREE_PINS, {"CONTRACTS.md": "0" * 64}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_document_anchor_rejected_without_state_change(self):
        with mock.patch.dict(reference.DOC_ANCHORS, {"audio_categories.md": ["not in the document"]}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unknown_board_link_rejected_without_state_change(self):
        invented = {"task_id": "SDK-NOT-ON-THE-BOARD", "title": "Invented", "mode": "feasibility"}
        with mock.patch.object(reference, "BOARD_LINKS", reference.BOARD_LINKS + [invented]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unlinked_gap_rejected_without_state_change(self):
        bad_gap = {"id": "GX", "follow_up_ids": [], "owner_note": "none"}
        with mock.patch.object(reference, "GAPS", reference.GAPS + [bad_gap]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_nonfeasibility_claim_rejected_without_state_change(self):
        bad_gap = {
            "id": "GY",
            "follow_up_ids": ["SDK-FND-TIMING"],
            "feasibility_task_exists": True,
            "owner_note": "none",
        }
        with mock.patch.object(reference, "GAPS", reference.GAPS + [bad_gap]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_execution_component_link_is_checked(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HX", component_ids=["not-a-component"])
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unlabelled_execution_rejected_without_state_change(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HX", scope="unlabelled")
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"independent_heldout_benchmark": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_human_listening_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"human_listening_result": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_real_speech_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"real_speech_result": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_board_identity_change_rejected_without_state_change(self):
        changed = dict(reference.BOARD_LINKS[0], title="Renamed task")
        with mock.patch.object(reference, "BOARD_LINKS", [changed] + reference.BOARD_LINKS[1:]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_pinning_mutable_board_rejected_without_state_change(self):
        with mock.patch.dict(reference.SOURCE_PINS, {reference.BOARD_PATH: "0" * 64}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unknown_source_lead_rejected_without_state_change(self):
        bad = dict(reference.SOURCE_LEADS[0], source_id="S99")
        with mock.patch.object(reference, "SOURCE_LEADS", [bad]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_bandwidth_separation_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.TONAL_BOUNDARY,
            {"frequency_response_correction_is_not_bandwidth_generation": False},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_real_device_response_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.TONAL_BOUNDARY, {"real_device_response_calibration_measured": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_real_speech_staging_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.TONAL_BOUNDARY, {"independent_licensed_speech_cohort_staged": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
