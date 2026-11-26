# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-05 evidence map."""

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
            "real_echo_audio",
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
        self.assertEqual(self.report["taxonomy"]["id"], "CLN-05")
        self.assertEqual(
            self.report["taxonomy"]["name"],
            "Reference-based acoustic echo cancellation (AEC)",
        )
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S21", "S22"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F04")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-05")
        self.assertEqual(self.report["category_scope"]["not_residual_echo_suppression_category"], "CLN-06")
        self.assertEqual(self.report["category_scope"]["not_feedback_or_howling_category"], "CLN-11")
        self.assertEqual(self.report["category_scope"]["not_dereverberation_category"], "CLN-04")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        self.assertIn("nlms", families)
        self.assertIn("frequency-domain", families)
        self.assertIn("neural-assisted", families)
        self.assertIn("reference-conditioned", families)

    def test_source_leads_are_s21_and_s22(self):
        leads = self.report["source_leads"]
        self.assertEqual([lead["source_id"] for lead in leads], ["S21", "S22"])
        self.assertEqual(leads[0]["title"], "NKF acoustic echo cancellation implementation")
        self.assertEqual(leads[1]["title"], "Speex echo cancellation documentation")
        self.assertTrue(all(lead["finding"] for lead in leads))
        self.assertTrue(all(lead["gap_ids"] for lead in leads))

    def test_reference_timing_and_drift_stay_in_contract(self):
        self.assertIs(self.report["aec_boundary"]["explicit_playback_reference_required"], True)
        self.assertIs(self.report["aec_boundary"]["reference_timing_and_drift_in_contract"], True)
        self.assertIs(self.report["aec_boundary"]["changing_echo_path_is_a_material_stratum"], True)
        self.assertIs(self.report["aec_boundary"]["double_talk_preservation_is_separate_from_echo_attenuation"], True)

    def test_real_provider_runtime_and_corpus_are_not_claimed(self):
        self.assertIs(self.report["aec_boundary"]["real_webrtc_aec3_source_or_runtime_staged"], False)
        self.assertIs(self.report["aec_boundary"]["independent_licensed_dev_or_test_corpus_staged"], False)
        self.assertIs(self.report["aec_boundary"]["neural_reference_weights_staged"], False)
        self.assertIs(self.report["aec_boundary"]["device_clock_drift_or_loop_timing_measured"], False)
        self.assertIs(self.report["aec_boundary"]["human_listening_result"], False)
        for key in (
            "independent_heldout_test_split_present",
            "licensed_public_corpus_staged",
            "neural_reference_weights_present",
            "real_provider_runtime_parity_present",
        ):
            self.assertIs(self.report["discovery"][key], False, key)

    def test_blind_suppression_and_cln06_are_boundary_only(self):
        self.assertIs(self.report["aec_boundary"]["blind_one_input_suppression_is_not_reference_aec"], True)
        self.assertIs(self.report["aec_boundary"]["residual_echo_suppression_belongs_to_cln_06"], True)
        family = next(row for row in self.report["method_families"] if row["family_id"] == "MF-M3")
        self.assertIn("cln-06", family["family"].lower())
        self.assertIn("adjacent", family["status"])

    def test_no_human_listening_or_independent_benchmark(self):
        self.assertIs(self.report["evidence_classes"]["human_listening_result"], False)
        self.assertIs(self.report["evidence_classes"]["independent_heldout_benchmark"], False)
        self.assertIs(self.report["evidence_classes"]["clock_drift_or_device_timing"], False)
        self.assertIs(self.report["evidence_classes"]["device_loop_or_loudspeaker_measurement"], False)
        self.assertIs(self.report["evidence_classes"]["release_claim"], False)

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_paired_synthetic", classes)
        self.assertIn("historical_local_training_split", classes)
        self.assertIn("historical_local_predicted_metric", classes)
        self.assertIn("source_only_frozen_protocol", classes)
        self.assertIn("missing_no_local_cohort", classes)
        self.assertNotIn("human_listening_result", classes)
        self.assertNotIn("independent_heldout_benchmark", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["paired_synthetic_historical_local"], True)
        self.assertIs(classes["recorded_training_split_historical_local"], True)
        self.assertIs(classes["predicted_metric_not_human"], True)
        self.assertIs(classes["neural_reference_model_execution"], True)
        self.assertIs(classes["source_reported_upstream_claim"], True)
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

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        self.assertEqual(len(self.report["historical_executions"]), 9)
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
        self.assertIn("source:research/aec_research_20261028.md", labels)
        self.assertIn("worktree:docs/task-evidence/nlms-aec/report.json", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertTrue(all(row["class"] == "source_reported" for row in self.report["reported_outcomes"]))

    def test_aecmos_is_predicted_not_human(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-8")
        self.assertIn("not human", execution["scope"])
        control = next(row for row in self.report["controls"] if row["id"] == "CT-9")
        self.assertIn("predicted", control["role"])
        self.assertIs(self.report["evidence_classes"]["human_listening_result"], False)

    def test_webrtc_row_is_synthetic_not_real_runtime(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-6")
        self.assertIn("not real WebRTC AEC3", execution["label"])
        self.assertIn("no pinned WebRTC source", execution["scope"])
        self.assertIs(self.report["aec_boundary"]["real_webrtc_aec3_source_or_runtime_staged"], False)

    def test_residual_suppressor_stays_off(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-5")
        self.assertIn("residual postfilter stays OFF", execution["scope"])
        self.assertLess(
            execution["values"]["overlap_near_ratio_postfilter"],
            execution["values"]["overlap_near_ratio_mdf_only"],
        )

    def test_acceptance_profile_maps_duplex_and_timing_gaps(self):
        mapped = self.report["acceptance_profile"]["mapped"]
        self.assertIn("clean_preservation", mapped)
        self.assertIn("synthetic near-end preservation", mapped["clean_preservation"])
        self.assertIn("alignment_state_memory_timing", mapped)
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

    def test_missing_reference_requirement_rejected_without_state_change(self):
        with mock.patch.dict(reference.AEC_BOUNDARY, {"explicit_playback_reference_required": False}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_real_runtime_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.AEC_BOUNDARY, {"real_webrtc_aec3_source_or_runtime_staged": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
