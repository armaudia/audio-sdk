# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-11 evidence map."""

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
        self.assertEqual(self.report["qualification"]["qualification_status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")
        self.assertIs(self.report["qualification"]["qualifies"], False)
        self.assertIs(self.report["qualification"]["physical_loop_execution_present"], False)
        self.assertIs(self.report["qualification"]["neural_howling_execution_present"], False)
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
            "real_loop_audio",
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
        taxonomy = self.report["taxonomy"]
        self.assertEqual(taxonomy["id"], "CLN-11")
        self.assertEqual(taxonomy["name"], "Feedback and howling control")
        self.assertEqual(taxonomy["group"], "Acoustic cleanup and spatial processing")
        self.assertEqual(taxonomy["scope"], "discovered_extension")
        self.assertEqual(taxonomy["output_kind"], "waveform/control")
        self.assertEqual(taxonomy["source_ids"], ["S48", "S49"])
        self.assertEqual(taxonomy["discovery_status"], "catalogued")
        self.assertEqual(taxonomy["candidate_census_status"], "not_started")
        self.assertEqual(taxonomy["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F08")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-11")
        self.assertEqual(self.report["category_scope"]["not_ordinary_acoustic_echo_cancellation_category"], "CLN-05")
        self.assertEqual(self.report["category_scope"]["not_tonal_correction_or_interference_filtering_category"], "CLN-10")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        for keyword in (
            "gain reduction",
            "adaptive notch",
            "feedback cancellation",
            "kalman",
            "hybrid",
            "neural direct",
            "learned feedback-risk",
        ):
            self.assertIn(keyword, families)

    def test_both_source_leads_are_pinned(self):
        leads = {lead["source_id"]: lead for lead in self.report["source_leads"]}
        self.assertEqual(set(leads), {"S48", "S49"})
        self.assertEqual(leads["S48"]["title"], "Acoustic howling suppression vendor documentation")
        self.assertEqual(leads["S48"]["access_scope"], "direct")
        self.assertEqual(leads["S49"]["title"], "Hybrid acoustic howling suppression paper")
        self.assertEqual(leads["S49"]["access_scope"], "search excerpt")
        for lead in leads.values():
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_feedback_is_not_ordinary_aec(self):
        boundary = self.report["feedback_boundary"]
        self.assertIs(boundary["feedback_loop_only"], True)
        self.assertIs(boundary["not_interchangeable_with_ordinary_aec"], True)
        self.assertIs(boundary["requires_recursive_loop_or_explicit_reference_facet"], True)
        self.assertIs(boundary["closed_loop_stability_is_first_order"], True)
        self.assertIs(boundary["fixed_gain_margin_is_a_baseline_not_a_selection"], True)

    def test_adjacent_categories_are_boundaries_only(self):
        for row in self.report["adjacent_boundaries"]:
            self.assertIs(row["not_howling_control_evidence"], True, row["component_id"])
            self.assertTrue(row["relation"])
        ids = {row["component_id"] for row in self.report["adjacent_boundaries"]}
        self.assertIn("nlms-aec", ids)
        self.assertIn("webrtc-aec3", ids)
        self.assertIn("narrow-biquad-notch", ids)

    def test_local_synthetic_execution_is_claimed_but_not_physical_or_neural(self):
        coverage = self.report["execution_coverage"]
        self.assertEqual(coverage["dedicated_howling_control_component_count"], 13)
        self.assertEqual(coverage["locally_evaluated_howling_control_component_count"], 6)
        self.assertEqual(coverage["classical_local_execution_count"], 5)
        self.assertEqual(coverage["ml_adjacent_local_execution_count"], 1)
        self.assertEqual(coverage["neural_howling_execution_count"], 0)
        self.assertEqual(coverage["physical_loop_execution_count"], 0)
        self.assertEqual(coverage["measured_physical_path_execution_count"], 0)
        self.assertEqual(coverage["labelled_howl_benchmark_execution_count"], 0)
        self.assertIs(self.report["evidence_classes"]["local_classical_howling_control_execution"], True)
        self.assertIs(self.report["evidence_classes"]["local_ml_adjacent_baseline_execution"], True)
        self.assertIs(self.report["evidence_classes"]["neural_howling_execution"], False)
        self.assertIs(self.report["evidence_classes"]["physical_loop_execution"], False)

    def test_real_loop_corpus_and_weights_are_not_claimed(self):
        boundary = self.report["feedback_boundary"]
        self.assertIs(boundary["measured_physical_loop_staged"], False)
        self.assertIs(boundary["physical_gain_before_feedback_measured"], False)
        self.assertIs(boundary["labelled_howl_corpus_staged"], False)
        self.assertIs(boundary["neural_checkpoint_or_weights_staged"], False)
        self.assertIs(boundary["device_timing_or_drift_measured"], False)
        self.assertIs(boundary["listening_or_human_validation_result"], False)
        self.assertIs(boundary["benchmark_or_release_qualification_present"], False)
        discovery = self.report["discovery"]
        for key in (
            "physical_loop_present",
            "calibrated_gain_before_feedback_present",
            "licensed_howl_corpus_present",
            "ml_howling_candidate_selected",
            "neural_checkpoint_or_weights_present",
            "independent_heldout_howl_split_present",
            "runnable_host_adapter_present",
        ):
            self.assertIs(discovery[key], False, key)
        self.assertIs(discovery["local_synthetic_fixture_present"], True)

    def test_no_human_device_benchmark_or_release_claim(self):
        self.assertIs(self.report["evidence_classes"]["human_validation_result"], False)
        self.assertIs(self.report["evidence_classes"]["listening_result"], False)
        self.assertIs(self.report["evidence_classes"]["device_timing_or_drift"], False)
        self.assertIs(self.report["evidence_classes"]["labelled_heldout_howl_benchmark"], False)
        self.assertIs(self.report["evidence_classes"]["release_claim"], False)

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        for name in (
            "historical_local_component_fixture",
            "historical_local_survey_pilot",
            "source_only_frozen_protocol",
            "missing_measured_physical_loop",
            "missing_labelled_howl_corpus",
            "missing_neural_checkpoint",
            "missing_benchmark_protocol",
        ):
            self.assertIn(name, classes)
        self.assertNotIn("human_validation", classes)
        self.assertNotIn("device_clock", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["local_synthetic_component_fixture"], True)
        self.assertIs(classes["historical_local_survey_pilot"], True)
        self.assertIs(classes["source_only_frozen_protocol"], True)
        self.assertIs(classes["source_reported_candidate_gap"], True)
        self.assertIs(classes["missing_measured_physical_loop"], True)
        self.assertIs(classes["missing_labelled_howl_corpus"], True)
        self.assertIs(classes["missing_neural_checkpoint"], True)
        self.assertIs(classes["missing_benchmark_protocol"], True)
        self.assertIs(classes["new_execution_in_this_survey"], False)

    def test_mutable_board_file_is_not_pinned_or_gated(self):
        self.assertNotIn(reference.BOARD_PATH, self.report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, self.report["boundary_pins"])
        self.assertIs(self.report["mutable_provenance"]["gate"], False)
        self.assertEqual(self.report["mutable_provenance"]["path"], reference.BOARD_PATH)
        self.assertNotIn("sha256_at_read", self.report["mutable_provenance"])
        raw = (HERE / "SOURCES.sha256").read_text(encoding="ascii") if (HERE / "SOURCES.sha256").exists() else ""
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

    def test_historical_executions_are_local_and_censused(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        executions = self.report["historical_executions"]
        self.assertEqual(len(executions), 8)
        self.assertEqual([row["id"] for row in executions], ["HE-%d" % n for n in range(1, 9)])
        for row in executions:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertIn(row["outcome_class"], ("historical_local_component_fixture", "historical_local_survey_pilot"))
            self.assertIn("not a physical-loop result", row["scope"])
            self.assertIn("not rerun by this survey", row["scope"])
            self.assertTrue(row["values"])

    def test_survey_pilot_values_are_transcribed(self):
        executions = {row["id"]: row for row in self.report["historical_executions"]}
        ami = executions["HE-1"]["values"]
        self.assertEqual(ami["n_candidates"], 6)
        self.assertEqual(ami["runs_per_candidate"], 36)
        self.assertEqual(ami["total_runs"], 216)
        self.assertEqual(ami["fixed_margin_minus_5db_median_sdr_db"], 5.193)
        self.assertEqual(ami["adaptive_notch_median_sdr_db"], -6.377)
        self.assertEqual(ami["adaptive_notch_no_loop_false_notch_events"], 19)
        smard = executions["HE-2"]["values"]
        self.assertEqual(smard["runs_per_candidate"], 144)
        self.assertEqual(smard["afc_plus_3db_margin_median_sdr_db"], 8.429)
        ml = executions["HE-3"]["values"]
        self.assertEqual(ml["heldout_precision"], 0.6443)
        self.assertEqual(ml["heldout_recall"], 0.652)
        self.assertEqual(ml["clean_speech_detection_events"], 38)

    def test_component_fixture_values_are_transcribed(self):
        executions = {row["id"]: row for row in self.report["historical_executions"]}
        notch = executions["HE-4"]["values"]
        self.assertEqual(notch["attack_frames"], 3)
        self.assertEqual(notch["release_frames"], 23)
        self.assertEqual(notch["clean_speech_false_activations"], 0)
        fixed = executions["HE-6"]["values"]
        self.assertEqual(fixed["clean_speech_minus5_program_sdr_db"], 7.177)
        self.assertIs(fixed["qualification_selected_is_null"], True)
        afc = executions["HE-7"]["values"]
        self.assertEqual(afc["afc_only_g1_15_dual_paths_stability_class"], "sustained_feedback")
        self.assertIs(afc["missing_results_qualify_candidate"], False)
        ml = executions["HE-8"]["values"]
        self.assertEqual(ml["heldout_precision"], 0.9731)
        self.assertEqual(ml["static_fallback_gain_db"], -5.0)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertTrue(all(row["class"] == "source_reported" for row in self.report["reported_outcomes"]))

    def test_author_reported_numbers_are_not_local(self):
        rows = {row["id"]: row for row in self.report["reported_outcomes"]}
        self.assertIn("2.65", rows["RO-3"]["claim"])
        self.assertIn("Author-reported", rows["RO-3"]["boundary"])
        self.assertIs(self.report["feedback_boundary"]["author_reported_numbers_are_not_local"], True)
        self.assertIs(self.report["evidence_classes"]["local_classical_howling_control_execution"], True)
        self.assertIs(self.report["evidence_classes"]["neural_howling_execution"], False)

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
            self.assertIn(link["mode"], reference.ALLOWED_LINK_MODES)
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
        self.assertIn("source:research/feedback_control_20261028.md", labels)
        self.assertIn("worktree:docs/task-evidence/fixed-feedback-gain-margin/report.json", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_acceptance_profile_maps_dsp_boundaries(self):
        mapped = self.report["acceptance_profile"]["mapped"]
        self.assertEqual(self.report["acceptance_profile"]["profile"], "DSP")
        self.assertIn("sweeps_steps_impulses", mapped)
        self.assertIn("attack_release", mapped)
        self.assertIn("headroom_and_nonlinearity", mapped)
        self.assertIn("closed_loop_conditions", mapped)
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
            "physical_loop_claim_without_physical_loop_execution",
            "open_loop_overlay_promoted_to_closed_loop",
            "synthetic_fixture_relabelled_physical",
            "fixed_margin_baseline_promoted_to_selection",
            "author_reported_promoted_to_local_execution",
            "notch_without_detector_claimed_as_howling_control",
            "heldout_benchmark_claim_without_labelled_split",
            "release_claim_without_closed_gates",
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

    def test_synthetic_relabel_rejected_without_state_change(self):
        bad = dict(
            reference.HISTORICAL_EXECUTIONS[0],
            id="HX",
            outcome_class="historical_local_physical_loop",
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

    def test_component_fixture_with_source_pin_rejected(self):
        bad = dict(
            reference.HISTORICAL_EXECUTIONS[3],
            id="HX",
            source_pin="reports/feedback-control/ami-closed-loop-screen.json",
        )
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"labelled_heldout_howl_benchmark": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_physical_loop_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"physical_loop_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_neural_execution_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"neural_howling_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_listening_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"listening_result": True}):
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

    def test_feedback_to_aec_collapse_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.FEEDBACK_BOUNDARY,
            {"not_interchangeable_with_ordinary_aec": False},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_physical_loop_staged_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.FEEDBACK_BOUNDARY,
            {"measured_physical_loop_staged": True},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_neural_weights_claim_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.FEEDBACK_BOUNDARY,
            {"neural_checkpoint_or_weights_staged": True},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_baseline_selection_claim_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.FEEDBACK_BOUNDARY,
            {"fixed_gain_margin_is_a_baseline_not_a_selection": False},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_coverage_count_change_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.EXECUTION_COVERAGE,
            {"physical_loop_execution_count": 1},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_neural_count_change_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.EXECUTION_COVERAGE,
            {"neural_howling_execution_count": 1},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
