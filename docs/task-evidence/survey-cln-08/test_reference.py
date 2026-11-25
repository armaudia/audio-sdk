# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-08 evidence map."""

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

    def test_invalid_payload_type_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.EvidenceMap().build(payload={"x": object()})

    def test_non_mapping_payload_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.EvidenceMap().build(payload=["not", "a", "mapping"])


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()
        self.snapshot = self.builder.snapshot()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["readiness"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")
        self.assertIs(self.report["qualification"]["localization_execution_present"], False)
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
            "real_array_audio",
            "weights",
            "runtime_invocation",
            "listening",
            "device_timing",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "CLN-08")
        self.assertEqual(self.report["taxonomy"]["name"], "Source localization and tracking")
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["output_kind"], "annotation/control")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S26"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F07")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-08")
        self.assertEqual(self.report["category_scope"]["not_beamforming_or_spatial_filtering_category"], "CLN-07")
        self.assertEqual(self.report["category_scope"]["not_generic_separation_category"], "SPK-01")
        self.assertEqual(self.report["category_scope"]["not_target_speaker_extraction_category"], "SPK-02")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        self.assertIn("srp-phat", families)
        self.assertIn("music", families)
        self.assertIn("normmusic", families)
        self.assertIn("learned spatial-feature", families)
        self.assertIn("candidate search pending", families)

    def test_source_lead_is_s26(self):
        leads = self.report["source_leads"]
        self.assertEqual([lead["source_id"] for lead in leads], ["S26"])
        self.assertEqual(leads[0]["title"], "Pyroomacoustics direction-of-arrival methods")
        self.assertEqual(leads[0]["access_scope"], "search excerpt")
        self.assertTrue(leads[0]["finding"])
        self.assertTrue(leads[0]["gap_ids"])

    def test_localization_is_metadata_not_a_cleaned_signal(self):
        boundary = self.report["localization_boundary"]
        self.assertIs(boundary["localization_output_is_metadata_not_waveform"], True)
        self.assertIs(boundary["direction_or_track_is_not_a_cleaned_signal"], True)
        self.assertIs(boundary["direction_is_not_intended_speaker_identity"], True)
        self.assertIs(boundary["requires_synchronized_array_geometry_and_timestamps"], True)
        self.assertIs(boundary["front_back_or_mirror_ambiguity_is_a_material_stratum"], True)
        self.assertIs(boundary["moving_source_and_track_continuity_in_contract"], True)

    def test_adjacent_categories_are_boundaries_only(self):
        boundary = self.report["localization_boundary"]
        self.assertIs(boundary["beamforming_and_spatial_filtering_belongs_to_cln_07"], True)
        self.assertIs(boundary["generic_separation_belongs_to_spk_01"], True)
        self.assertIs(boundary["target_speaker_extraction_belongs_to_spk_02"], True)
        self.assertIs(boundary["diarization_and_identity_belongs_to_spk_04_spk_05"], True)
        self.assertIs(boundary["clock_alignment_belongs_to_eng_02"], True)
        for row in self.report["adjacent_boundaries"]:
            self.assertIs(row["not_localization_evidence"], True, row["component_id"])
            self.assertTrue(row["relation"])

    def test_no_classical_or_ml_execution_is_claimed(self):
        coverage = self.report["execution_coverage"]
        self.assertEqual(coverage["localization_component_count"], 1)
        self.assertEqual(coverage["classical_localization_implementation_count"], 0)
        self.assertEqual(coverage["ml_localization_execution_count"], 0)
        self.assertEqual(coverage["labelled_localization_execution_count"], 0)
        self.assertEqual(coverage["adjacent_spatial_execution_count"], 2)
        self.assertIs(self.report["evidence_classes"]["localization_execution_historical_local"], False)
        self.assertIs(self.report["evidence_classes"]["classical_localization_implementation"], False)
        self.assertIs(self.report["evidence_classes"]["ml_localization_execution"], False)

    def test_real_array_corpus_and_weights_are_not_claimed(self):
        boundary = self.report["localization_boundary"]
        self.assertIs(boundary["classical_srp_phat_or_music_implementation_staged"], False)
        self.assertIs(boundary["ml_spatial_estimator_weights_staged"], False)
        self.assertIs(boundary["real_array_geometry_or_calibration_staged"], False)
        self.assertIs(boundary["labelled_localization_corpus_staged"], False)
        self.assertIs(boundary["device_timing_or_drift_measured"], False)
        self.assertIs(boundary["steering_or_extraction_executed"], False)
        self.assertIs(boundary["human_validation_result"], False)
        for key in (
            "independent_heldout_localization_split_present",
            "licensed_localization_corpus_staged",
            "ml_localization_candidate_selected",
            "ml_spatial_estimator_weights_present",
            "real_array_geometry_or_calibration_present",
            "classical_localization_implementation_present",
        ):
            self.assertIs(self.report["discovery"][key], False, key)

    def test_no_human_or_device_or_benchmark_claim(self):
        self.assertIs(self.report["evidence_classes"]["human_validation_result"], False)
        self.assertIs(self.report["evidence_classes"]["device_array_or_clock_timing"], False)
        self.assertIs(self.report["evidence_classes"]["labelled_heldout_localization_benchmark"], False)
        self.assertIs(self.report["evidence_classes"]["steering_or_extraction_execution"], False)
        self.assertIs(self.report["evidence_classes"]["release_claim"], False)

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_adjacent_spatial_fixture", classes)
        self.assertIn("source_only_frozen_protocol", classes)
        self.assertIn("source_reported_candidate_gap", classes)
        self.assertIn("missing_no_local_cohort", classes)
        self.assertIn("missing_array_metadata", classes)
        self.assertNotIn("human_validation", classes)
        self.assertNotIn("steering_execution", classes)
        self.assertNotIn("device_clock", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["adjacent_multichannel_fixture_historical_local"], True)
        self.assertIs(classes["source_only_frozen_protocol"], True)
        self.assertIs(classes["source_reported_candidate_gap"], True)
        self.assertIs(classes["missing_localization_cohort"], True)
        self.assertIs(classes["new_execution_in_this_survey"], False)
        self.assertIs(classes["parity_or_qualification_claim"], False)

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

    def test_historical_executions_are_adjacent_and_censused(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        executions = self.report["historical_executions"]
        self.assertEqual(len(executions), 2)
        self.assertEqual([row["id"] for row in executions], ["HE-1", "HE-2"])
        for row in executions:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertEqual(row["outcome_class"], "historical_local_adjacent_spatial_fixture")
            self.assertIn("not a localization result", row["scope"])
            self.assertIn("not rerun by this survey", row["scope"])
            self.assertTrue(row["values"])

    def test_adjacent_geometry_values_are_transcribed(self):
        offline = self.report["historical_executions"][0]["values"]
        self.assertEqual(offline["channels"], 2)
        self.assertEqual(offline["mic_spacing_m"], 0.06)
        self.assertEqual(offline["source_angle_deg"], 35.0)
        self.assertEqual(offline["second_source_angle_deg"], -50.0)
        self.assertLess(offline["short_rt60_delta_si_sdr_db"], 0.0)
        online = self.report["historical_executions"][1]["values"]
        self.assertEqual(online["input_channels"], 2)
        self.assertEqual(online["mic_spacing_m"], 0.04)
        self.assertEqual(online["source_azimuth_deg"], 30.0)
        self.assertEqual(online["content_delay_samples"], 480)

    def test_historical_rows_do_not_emit_a_direction(self):
        for row in self.report["historical_executions"]:
            self.assertIn("emits no direction", row["scope"])
            self.assertNotIn("direction_deg", row["values"])
            self.assertNotIn("track", row["values"])

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
        self.assertEqual(len(self.report["gaps"]), 10)
        for gap in self.report["gaps"]:
            self.assertTrue(gap["follow_up_ids"])
            self.assertTrue(set(gap["follow_up_ids"]) <= links)
            self.assertTrue(set(gap["follow_up_ids"]) <= ids)
            self.assertTrue(gap["owner_note"])
            if not gap["feasibility_task_exists"]:
                self.assertIn("no", gap["owner_note"].lower())

    def test_feasibility_links_exist_where_claimed(self):
        modes = {link["task_id"]: link["mode"] for link in self.report["board_links"]}
        for gap in self.report["gaps"]:
            if gap["feasibility_task_exists"]:
                self.assertIn("feasibility", {modes[tid] for tid in gap["follow_up_ids"]})

    def test_no_follow_up_task_invented(self):
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
        self.assertIn("source:research/category_survey/sources.md", labels)
        self.assertIn("worktree:docs/task-evidence/offline-multichannel-wpe/report.json", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertTrue(all(row["class"] == "source_reported" for row in self.report["reported_outcomes"]))

    def test_blocked_ml_candidates_are_not_localization_estimators(self):
        rows = {row["id"]: row for row in self.report["reported_outcomes"]}
        self.assertIn("SpatialNet", rows["RO-3"]["claim"])
        self.assertIn("no direction output", rows["RO-3"]["boundary"].lower())
        self.assertIn("candidate search remains pending", rows["RO-2"]["boundary"])

    def test_source_documentation_is_not_an_execution(self):
        self.assertEqual(self.report["source_leads"][0]["access_scope"], "search excerpt")
        self.assertIs(self.report["evidence_classes"]["classical_localization_implementation"], False)
        self.assertIs(self.report["evidence_classes"]["localization_execution_historical_local"], False)

    def test_acceptance_profile_maps_spatial_boundaries(self):
        mapped = self.report["acceptance_profile"]["mapped"]
        self.assertEqual(self.report["acceptance_profile"]["profile"], "Spatial")
        self.assertIn("geometry_and_layout", mapped)
        self.assertIn("timestamp_calibration", mapped)
        self.assertIn("held_out_localization_labels", mapped)
        self.assertIn("human_validation", mapped)
        self.assertEqual(len(self.report["acceptance_profile"]["blocked"]), 8)

    def test_adverse_rejections_cover_required_classes(self):
        keys = set(self.report["adverse_rejections"])
        for key in (
            "duplicate_json_key",
            "nonfinite_json_number",
            "missing_pinned_file",
            "tampered_pin",
            "unknown_board_task",
            "gap_without_link_or_reason",
            "invalid_payload_type",
            "unknown_component",
            "localization_claim_without_localization_execution",
            "steering_claim_without_steering_execution",
            "heldout_benchmark_claim_without_test_split",
            "metadata_promoted_to_clean_signal",
            "identity_claim_without_speaker_labels",
        ):
            self.assertIn(key, keys)


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
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(reference.MapError):
                    self.builder.build(payload={"bad": value})
                self._assert_unchanged()

    def test_missing_workspace_rejected_without_state_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(reference, "find_workspace", return_value=Path(tmp)):
                with self.assertRaises(reference.MapError):
                    self.builder.build()
        self._assert_unchanged()

    def test_missing_pinned_file_rejected_without_state_change(self):
        with mock.patch.dict(reference.WORKTREE_PINS, {"CONTRACTS.md.missing": "0" * 64}):
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

    def test_unlisted_board_task_rejected_without_state_change(self):
        bad_gap = {
            "id": "GZ",
            "follow_up_ids": ["SDK-NOT-A-REAL-TASK"],
            "feasibility_task_exists": False,
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

    def test_localization_relabel_rejected_without_state_change(self):
        bad = dict(
            reference.HISTORICAL_EXECUTIONS[0],
            id="HX",
            outcome_class="historical_local_localization",
        )
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
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"labelled_heldout_localization_benchmark": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_localization_execution_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"localization_execution_historical_local": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_human_validation_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"human_validation_result": True}):
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

    def test_metadata_to_waveform_claim_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.LOCALIZATION_BOUNDARY,
            {"localization_output_is_metadata_not_waveform": False},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_classical_implementation_claim_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.LOCALIZATION_BOUNDARY,
            {"classical_srp_phat_or_music_implementation_staged": True},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_ml_weights_claim_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.LOCALIZATION_BOUNDARY,
            {"ml_spatial_estimator_weights_staged": True},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_steering_claim_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.LOCALIZATION_BOUNDARY,
            {"steering_or_extraction_executed": True},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_coverage_count_change_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.EXECUTION_COVERAGE,
            {"classical_localization_implementation_count": 1},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
