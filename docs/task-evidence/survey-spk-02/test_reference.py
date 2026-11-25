# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-SPK-02 evidence map."""

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
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertEqual(self.report["qualification"]["survey_status"], "incomplete")
        self.assertIs(self.report["qualification"]["proposal_only"], True)
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")

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
            "listening",
            "device_timing",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
            "audio_mutation_or_deletion",
            "target_speaker_extraction_claim",
            "source_separation_claim",
            "identity_or_verification_claim",
            "personalized_vad_claim",
            "enrollment_conditioning_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "SPK-02")
        self.assertEqual(self.report["taxonomy"]["scope"], "requested")
        self.assertEqual(self.report["taxonomy"]["output_kind"], "waveform")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S07", "S50"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F05")
        self.assertEqual(self.report["legacy_backlog"]["state"], "catalogued")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        classic_families = " ".join(
            row["family"] for row in self.report["method_families"] if row["branch"] == "classic"
        ).lower()
        ml_families = " ".join(
            row["family"] for row in self.report["method_families"] if row["branch"] == "ml"
        ).lower()
        for term in ("cue-based", "statistical"):
            self.assertIn(term, classic_families)
        for term in ("speaker-conditioned", "cue-conditioned"):
            self.assertIn(term, ml_families)
        statuses = {row["status"] for row in self.report["method_families"]}
        self.assertIn("no_local_component_or_execution_in_reviewed_records", statuses)
        self.assertIn("candidate_only_blocked_no_local_execution", statuses)
        self.assertIn("adjacent_local_suppression_only", statuses)

    def test_source_leads_cover_s07_s50(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S07", "S50"})
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])
        s50 = next(lead for lead in self.report["source_leads"] if lead["source_id"] == "S50")
        self.assertEqual(s50["access_scope"], "search excerpt in prior brainstorm")

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("source_only_tse_protocol", classes)
        self.assertIn("source_excerpt_audiovisual_tse_protocol", classes)
        self.assertIn("source_reported_tse_candidate", classes)
        self.assertIn("adjacent_local_primary_background_suppression", classes)
        self.assertIn("adjacent_local_speaker_dominant_suppression", classes)
        self.assertIn("adjacent_local_in_model_speaker_similarity_diagnostic", classes)
        self.assertIn("source_reported_vendor_voice_isolation_benchmark", classes)
        self.assertIn("missing_spk02_enrollment_cohort", classes)
        self.assertNotIn("human_listening_result", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["source_only_tse_protocol"], True)
        self.assertIs(classes["source_reported_tse_candidate"], True)
        self.assertIs(classes["adjacent_primary_background_suppression_local"], True)
        self.assertIs(classes["adjacent_speaker_dominant_suppression_local"], True)
        self.assertIs(classes["adjacent_in_model_speaker_similarity_diagnostic"], True)
        self.assertIs(classes["source_reported_vendor_voice_isolation_benchmark"], True)
        self.assertIs(classes["spk02_local_extraction_execution"], False)
        self.assertIs(classes["enrollment_conditioned_execution"], False)
        self.assertIs(classes["target_speaker_extraction_accuracy_claim"], False)
        self.assertIs(classes["clean_target_reference_accuracy_claim"], False)
        self.assertIs(classes["real_enrolled_corpus"], False)
        self.assertIs(classes["impostor_or_target_absent_negative_set"], False)
        self.assertIs(classes["human_listening_result"], False)
        self.assertIs(classes["device_timing"], False)
        self.assertIs(classes["release_claim"], False)

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

    def test_historical_executions_are_adjacent_and_censused(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        self.assertEqual({row["id"] for row in self.report["historical_executions"]}, {"HE-1", "HE-2"})
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertIs(row["adjacent"], True, row["id"])
            self.assertIs(row["not_component_evidence"], True, row["id"])
            self.assertIn("not rerun by this survey", row["scope"])
            self.assertIn("adjacent", row["outcome_class"])
            self.assertIn("hush", row["component_ids"])

    def test_historical_values_are_transcribed_with_strata(self):
        he1 = self.report["historical_executions"][0]["values"]
        self.assertEqual(he1["target_source_pairs"], 30)
        self.assertEqual(he1["mixtures"], 90)
        self.assertEqual(he1["delta_target_si_sdr_db"], [-9.33, -14.54, -20.23])
        self.assertEqual(he1["delta_target_stoi"], [-0.141, -0.176, -0.197])
        self.assertEqual(he1["observed_delay_ms"], 10.0)
        he2 = self.report["historical_executions"][1]["values"]
        self.assertEqual(he2["directed_speaker_pairs"], 7)
        self.assertEqual(he2["mixtures"], 21)
        self.assertEqual(he2["delta_target_si_sdr_db"], [-13.17, -18.41, -24.18])
        self.assertIs(he2["ratio_interval_includes_zero"], True)

    def test_controls_and_assets_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"] + self.report["historical_executions"]:
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
        self.assertIn("source:research/category_registry.json", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_category_boundary_keeps_identity_and_cues_separate(self):
        boundary = self.report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("Enrollment, spatial or visual cues are input facets", boundary)
        self.assertIn("Identity matching does not define who the user wants to hear", boundary)
        scope = self.report["category_scope"]
        self.assertIs(scope["enrollment_spatial_and_visual_cues_are_input_facets"], True)
        self.assertIs(scope["identity_match_does_not_define_desired_speaker"], True)
        self.assertIs(self.report["tse_boundary"]["generic_separation_is_not_target_selection"], True)
        self.assertIs(
            self.report["tse_boundary"]["competing_speaker_suppression_is_not_target_extraction"],
            True,
        )
        self.assertIs(self.report["tse_boundary"]["personal_vad_activity_is_not_a_waveform"], True)

    def test_no_extraction_execution_is_claimed(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["spk02_local_extraction_execution"], False)
        self.assertIs(classes["enrollment_conditioned_execution"], False)
        self.assertIs(classes["target_speaker_extraction_accuracy_claim"], False)
        self.assertIs(classes["clean_target_reference_accuracy_claim"], False)
        self.assertIs(classes["real_enrolled_corpus"], False)
        self.assertIs(classes["real_overlap_corpus"], False)
        for row in self.report["historical_executions"]:
            self.assertIs(row["not_component_evidence"], True)
            self.assertIn("adjacent", row["outcome_class"])
        tse = self.report["tse_boundary"]
        self.assertIs(tse["enrollment_conditioned_execution_present"], False)
        self.assertIs(tse["target_selected_output_measured"], False)
        self.assertIs(tse["ml_weights_present"], False)

    def test_missing_enrollment_cohort_is_explicit(self):
        missing = [
            row for row in self.report["comparison_inputs"] if row["class"] == "missing_spk02_enrollment_cohort"
        ]
        self.assertEqual(len(missing), 1)
        self.assertIn("missing", missing[0]["boundary"].lower())
        assets = [row for row in self.report["assets"] if row["class"] == "missing"]
        self.assertTrue(assets)
        for row in assets:
            self.assertIn("not present", row["status"].lower())


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

    def test_nonadjacent_execution_is_rejected(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HY", adjacent=False)
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"new_execution_in_this_survey": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_accuracy_claim_class_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"clean_target_reference_accuracy_claim": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_suppression_promoted_to_extraction_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"spk02_local_extraction_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_enrollment_conditioning_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"enrollment_conditioned_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

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
            self.assertIn("source", row["class"])

    def test_gaps_without_component_owner_are_bounded(self):
        report = reference.build_report()
        for gap in report["gaps"]:
            if not gap["feasibility_task_exists"]:
                note = gap["owner_note"].lower()
                self.assertIn("no", note, gap["id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
