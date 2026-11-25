# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-DET-05 evidence map."""

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

    def test_non_object_json_rejected_as_payload_mapping(self):
        with self.assertRaises(reference.MapError):
            reference.EvidenceMap().build(payload=[("a", 1)])


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["readiness"], "incomplete")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertEqual(self.report["qualification"]["survey_status"], "incomplete")
        self.assertIs(self.report["qualification"]["proposal_only"], True)
        self.assertIs(self.report["qualification"]["qualifies"], False)

    def test_all_release_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates], ["RG-0%d" % k for k in range(1, 9)])
        self.assertTrue(all(gate["blocked"] is True for gate in gates))

    def test_no_public_or_release_change(self):
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        for key in (
            "real_speech",
            "real_corpus",
            "weights",
            "runtime_invocation",
            "enrollment_cue",
            "listening",
            "device_timing",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["scope"]["task_local_only"], True)
        self.assertIs(self.report["scope"]["no_new_execution"], True)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        taxonomy = self.report["taxonomy"]
        self.assertEqual(taxonomy["id"], "DET-05")
        self.assertEqual(taxonomy["name"], "Target-speaker / personalized VAD")
        self.assertEqual(taxonomy["scope"], "discovered_extension")
        self.assertEqual(taxonomy["output_kind"], "annotation/control")
        self.assertEqual(taxonomy["source_ids"], ["S52", "S53"])
        self.assertEqual(taxonomy["related_category_ids"], ["DET-01", "SPK-02", "SPK-05"])
        self.assertEqual(taxonomy["discovery_status"], "catalogued")
        self.assertEqual(taxonomy["candidate_census_status"], "not_started")
        self.assertEqual(taxonomy["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F05")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"] for row in self.report["method_families"])
        for term in (
            "Standard VAD plus independent speaker-scoring",
            "Statistical speaker segmentation",
            "Speaker-conditioned neural activity classification",
            "Speaker-conditioned neural extraction",
            "diarization",
        ):
            self.assertIn(term, families)

    def test_source_leads_cover_s52_s53(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S52", "S53"})
        by_id = {lead["source_id"]: lead for lead in self.report["source_leads"]}
        self.assertEqual(by_id["S52"]["access_scope"], "direct")
        self.assertEqual(by_id["S53"]["access_scope"], "direct README; no execution/checkpoint access")
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_any_speaker_vad_baseline", classes)
        self.assertIn("historical_local_adjacent_speaker_dominant_suppression", classes)
        self.assertIn("historical_local_in_model_speaker_similarity_diagnostic", classes)
        self.assertIn("source_only_personal_vad_protocol", classes)
        self.assertIn("missing_enrollment_conditioned_corpus", classes)
        self.assertNotIn("personal_vad_local_execution", classes)
        self.assertNotIn("human_listening_result", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["historical_local_any_speaker_vad_baseline"], True)
        self.assertIs(classes["historical_local_adjacent_speaker_dominant_suppression"], True)
        self.assertIs(classes["source_only_personal_vad_protocol"], True)
        self.assertIs(classes["missing_enrollment_conditioned_execution"], True)
        self.assertIs(classes["personal_vad_local_execution"], False)
        self.assertIs(classes["speaker_conditioned_neural_execution"], False)
        self.assertIs(classes["target_label_accuracy_claim"], False)
        self.assertIs(classes["source_separation_or_enhancement_claim"], False)
        text = " ".join(row["label"].lower() for row in self.report["historical_executions"])
        text += " " + " ".join(row["class"] for row in self.report["comparison_inputs"])
        self.assertNotIn("listening", text)
        self.assertNotIn("accuracy_claim", text)

    def test_execution_coverage_is_nonpromoting(self):
        coverage = self.report["execution_coverage"]
        self.assertEqual(coverage["personal_vad_local_execution_count"], 0)
        self.assertEqual(coverage["speaker_conditioned_neural_execution_count"], 0)
        self.assertEqual(coverage["enrollment_conditioned_execution_count"], 0)
        self.assertEqual(coverage["target_label_benchmark_execution_count"], 0)
        self.assertEqual(coverage["locally_evaluated_personal_vad_component_count"], 0)
        self.assertTrue(coverage["missing_enrollment_conditioned_corpus"])
        self.assertTrue(coverage["missing_checkpoint_or_weights"])

    def test_personal_vad_boundary_is_not_widened(self):
        boundary = self.report["personal_vad_boundary"]
        self.assertTrue(boundary["target_speaker_activity_only"])
        self.assertTrue(boundary["three_way_classes_required"])
        self.assertTrue(boundary["enrollment_or_reference_cue_required"])
        self.assertTrue(boundary["not_source_separation"])
        self.assertTrue(boundary["not_mute_or_gate_mandate"])
        self.assertTrue(boundary["not_speaker_identification_or_verification"])
        self.assertTrue(boundary["not_general_any_speaker_vad"])
        self.assertFalse(boundary["personal_vad_local_execution_present"])
        self.assertFalse(boundary["compatible_checkpoint_or_weights_staged"])
        self.assertFalse(boundary["enrolled_mixture_or_clean_target_reference_staged"])

    def test_adjacent_rows_are_not_promoted_to_personal_vad(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        self.assertEqual(
            by_id["HE-1"]["outcome_class"],
            "historical_local_adjacent_speaker_dominant_suppression",
        )
        self.assertEqual(
            by_id["HE-2"]["outcome_class"],
            "historical_local_adjacent_speaker_dominant_suppression",
        )
        self.assertEqual(by_id["HE-3"]["outcome_class"], "historical_local_any_speaker_vad_baseline")
        for row in by_id.values():
            self.assertNotIn("personal", row["outcome_class"])
            self.assertIn("not", row["scope"])
            self.assertIn("not rerun by this survey", row["scope"])
        self.assertIn("no enrollment prompt", by_id["HE-1"]["scope"])
        self.assertIn("no enrollment prompt", by_id["HE-2"]["scope"])
        self.assertIn("no enrollment cue", by_id["HE-3"]["scope"])

    def test_historical_numbers_are_transcribed(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        self.assertEqual(by_id["HE-1"]["values"]["mixtures"], 90)
        self.assertEqual(by_id["HE-1"]["values"]["hush_target_si_sdr_delta_db"][0], -9.33)
        self.assertEqual(by_id["HE-2"]["values"]["directed_speaker_pairs"], 7)
        self.assertIs(by_id["HE-2"]["values"]["ratio_gain_ci_includes_zero"], True)
        self.assertEqual(by_id["HE-3"]["values"]["web_rtc_fp_percent"], 49.54)
        self.assertEqual(by_id["HE-3"]["values"]["silero_fn_percent"], 19.43)

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

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])

    def test_controls_and_assets_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"] + self.report["historical_executions"]:
            self.assertIn(row["source_pin"], pins)

    def test_personal_vad_boundary_rows_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["adjacent_boundaries"]:
            self.assertIn(row["source_pin"], pins)

    def test_all_gaps_link_existing_board_tasks(self):
        board = reference.strict_json_load(reference.find_workspace() / reference.BOARD_PATH)
        ids = {task["id"] for task in board["tasks"]}
        links = {link["task_id"] for link in self.report["board_links"]}
        self.assertTrue(links)
        for gap in self.report["gaps"]:
            self.assertTrue(gap["follow_up_ids"])
            self.assertTrue(set(gap["follow_up_ids"]) <= links)
            self.assertTrue(set(gap["follow_up_ids"]) <= ids)
            self.assertTrue(gap["owner_note"])
            if not gap["feasibility_task_exists"]:
                self.assertTrue("no" in gap["owner_note"].lower())

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
        self.assertIn("source:research/category_registry.json", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)


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

    def test_tampered_pin_rejected_without_state_change(self):
        with mock.patch.dict(reference.SOURCE_PINS, {"audio_categories.md": "0" * 64}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_tampered_worktree_pin_rejected_without_state_change(self):
        with mock.patch.dict(reference.WORKTREE_PINS, {"CONTRACTS.md": "0" * 64}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_document_anchor_rejected_without_state_change(self):
        with mock.patch.dict(reference.DOC_ANCHORS, {"audio_categories.md": ["not in the document"]}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_worktree_anchor_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.WORKTREE_DOC_ANCHORS,
            {"docs/task-evidence/survey-det-01/README.md": ["not in the document"]},
        ):
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

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.EVIDENCE_CLASSES, {"new_execution_in_this_survey": True}
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_accuracy_claim_class_is_rejected(self):
        with mock.patch.dict(
            reference.EVIDENCE_CLASSES, {"target_label_accuracy_claim": True}
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_personal_execution_claim_is_rejected(self):
        with mock.patch.dict(
            reference.EVIDENCE_CLASSES, {"personal_vad_local_execution": True}
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_open_boundary_flag_is_rejected(self):
        with mock.patch.dict(
            reference.PERSONAL_VAD_BOUNDARY, {"compatible_checkpoint_or_weights_staged": True}
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_coverage_flag_cannot_be_cleared(self):
        with mock.patch.dict(
            reference.EXECUTION_COVERAGE, {"missing_checkpoint_or_weights": False}
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_nonconforming_family_cannot_drop_classic_baseline(self):
        families = [row for row in reference.METHOD_FAMILIES if row["family_id"] != "MF-C1"]
        with mock.patch.object(reference, "METHOD_FAMILIES", families):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_vad_boundary_keeps_separation_and_muting_out(self):
        report = reference.build_report()
        boundary = report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("Not source separation", boundary)
        self.assertIn("mandate to mute", boundary)
        self.assertIn("target false rejection", boundary)
        self.assertIn("changing speakers", boundary)

    def test_local_and_reported_outcomes_stay_distinct(self):
        report = reference.build_report()
        local = {row["id"] for row in report["historical_executions"]}
        reported = {row["id"] for row in report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        for row in report["historical_executions"]:
            self.assertIn("not rerun by this survey", row["scope"])
        for row in report["reported_outcomes"]:
            self.assertIn("source_reported", row["class"])

    def test_adverse_adjacent_outcomes_are_recorded(self):
        report = reference.build_report()
        by_id = {row["id"]: row for row in report["historical_executions"]}
        self.assertLess(by_id["HE-1"]["values"]["hush_target_si_sdr_delta_db"][0], 0)
        self.assertLess(by_id["HE-2"]["values"]["hush_target_stoi_delta"][0], 0)
        self.assertTrue(by_id["HE-2"]["values"]["ratio_gain_ci_includes_zero"])
        self.assertIn("damaging the designated target", by_id["HE-1"]["scope"])

    def test_gaps_without_component_owner_are_bounded(self):
        report = reference.build_report()
        for gap in report["gaps"]:
            if not gap["feasibility_task_exists"]:
                note = gap["owner_note"].lower()
                self.assertIn("no", note, gap["id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
