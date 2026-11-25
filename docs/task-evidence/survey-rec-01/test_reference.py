# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-REC-01 evidence map."""

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
        self.assertEqual(self.report["qualification"]["qualification_status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertEqual(self.report["qualification"]["survey_status"], "incomplete")
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")
        self.assertIs(self.report["qualification"]["proposal_only"], True)
        self.assertIs(self.report["qualification"]["qualifies"], False)
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
            "real_speech_used_here",
            "real_corpus_used_here",
            "weights_loaded_here",
            "runtime_invoked_here",
            "model_inference_here",
            "streaming_inference_here",
            "human_transcript_review_here",
            "confidence_calibration_here",
            "listening_here",
            "device_timing_here",
            "latency_claim",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
            "asr_accuracy_claim",
            "code_switch_claim",
            "meeting_transcription_claim",
            "network_access",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["scope"]["no_new_execution"], True)
        self.assertIs(self.report["scope"]["historical_citations_include_real_speech"], True)
        self.assertIs(self.report["scope"]["historical_citations_include_real_transcripts"], True)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "REC-01")
        self.assertEqual(self.report["taxonomy"]["scope"], "requested_optional")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S09", "S11", "S47"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F11")
        self.assertEqual(self.report["legacy_backlog"]["activation_state"], "catalogued")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"] for row in self.report["method_families"])
        self.assertIn("HMM", families)
        self.assertIn("Encoder-decoder", families)
        self.assertIn("CTC", families)
        self.assertIn("forced alignment", families)
        self.assertIn("Code-switching", families)

    def test_source_leads_are_s09_s11_s47(self):
        self.assertEqual(
            [lead["source_id"] for lead in self.report["source_leads"]],
            ["S09", "S11", "S47"],
        )
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_research_single_crop_asr_alignment", classes)
        self.assertIn("historical_research_fixed_scorer_asr", classes)
        self.assertIn("historical_research_transcript_drift_scorer", classes)
        self.assertIn("historical_research_vosk_gate_boundaries", classes)
        self.assertIn("missing_required_cohort", classes)
        self.assertNotIn("human_listening_result", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["historical_research_single_crop_asr_alignment"], True)
        self.assertIs(classes["historical_research_fixed_scorer_asr"], True)
        self.assertIs(classes["historical_research_transcript_drift_scorer"], True)
        self.assertIs(classes["historical_research_vosk_gate_boundaries"], True)
        self.assertIs(classes["source_reported_model_documentation"], True)
        self.assertIs(classes["real_asr_corpus_benchmark"], False)
        self.assertIs(classes["human_reference_transcript_review"], False)
        self.assertIs(classes["streaming_asr_execution"], False)
        self.assertIs(classes["word_timestamp_gold"], False)
        self.assertIs(classes["confidence_calibration"], False)
        self.assertIs(classes["asr_accuracy_claim"], False)

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
            self.assertEqual(row["scope_class"], "historical_research_execution")
            self.assertIs(row["merged_task_evidence"], False)
            self.assertIs(row["not_rerun"], True)
            self.assertIn("not rerun by this survey", row["scope"])
        for row in self.report["reported_outcomes"]:
            self.assertTrue(row["class"].startswith("source_reported_"), row["id"])

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

    def test_run_check_mode_verifies_three_cold_starts(self):
        run.check_three_cold_starts()

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

    def test_single_crop_values_are_exact(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        he = by_id["HE-1"]["values"]
        self.assertEqual(he["reference_words"], 34)
        self.assertEqual(he["whisper_word_errors"], 4)
        self.assertEqual(he["whisper_wer_percent"], 11.76)
        self.assertEqual(he["oracle_boundary_mae_ms"], 23.79)
        self.assertEqual(he["asr_boundary_mae_ms"], 23.17)
        self.assertEqual(he["asr_within_50ms_percent"], 91.7)
        self.assertEqual(he["crop_duration_s"], 15)

    def test_fixed_scorer_values_are_exact(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        he = by_id["HE-2"]["values"]
        self.assertEqual(he["clips"], 10)
        self.assertEqual(he["reference_words"], 136)
        self.assertEqual(he["paired_conditions"], 90)
        self.assertEqual(he["source_word_errors"], 41)
        self.assertEqual(he["source_wer_percent_tsm_summary"], 30.15)
        self.assertEqual(he["bungee_delta_1_5_pp"], 2.9)
        self.assertEqual(he["soundtouch_delta_1_5_pp"], 7.4)
        self.assertEqual(he["rubber_band_delta_1_25_pp"], 0.7)
        self.assertEqual(he["psola_delta_1_5_pp"], 1.5)

    def test_transcript_drift_and_gate_values_are_exact(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        he3 = by_id["HE-3"]["values"]
        self.assertEqual(he3["clips"], 3)
        self.assertEqual(he3["total_blocks"], 15708)
        self.assertEqual(he3["deadline_misses"], 0)
        self.assertEqual(he3["source_median_wer_percent_low"], 3.5)
        self.assertIs(he3["real_clip_reference_transcript"], False)
        he4 = by_id["HE-4"]["values"]
        self.assertEqual(he4["gate_iou_low"], 0.94)
        self.assertEqual(he4["false_speech_blocks"], 12)
        self.assertEqual(he4["missed_speech_blocks"], 24)
        self.assertIs(he4["production_boundary_source"], False)

    def test_file_transcription_is_not_causal_streaming(self):
        boundary = self.report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("File transcription is not proof of causal streaming", boundary)
        self.assertIn("partial/final timing", boundary)
        self.assertIn("word preservation", boundary)
        self.assertIn("listening quality", boundary)
        self.assertIn("asr", " ".join(
            row["boundary"].lower() for row in self.report["excluded_boundaries"]
        ))

    def test_asr_is_not_endpointing_or_diarization(self):
        reasons = " ".join(row["reason"] for row in self.report["excluded_boundaries"])
        self.assertIn("turn decision", reasons)
        self.assertIn("who spoke", reasons)
        self.assertIn("language label", reasons)
        self.assertIn("comprehension", reasons)


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
        bad = dict(
            reference.HISTORICAL_EXECUTIONS[0],
            id="HX",
            component_ids=["not-a-component"],
        )
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_merged_task_evidence_promotion_is_rejected(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HX", merged_task_evidence=True)
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"streaming_asr_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_asr_accuracy_claim_class_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"asr_accuracy_claim": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_human_reference_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"human_reference_transcript_review": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_word_timestamp_gold_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"word_timestamp_gold": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_required_cohort_cannot_be_promoted(self):
        with mock.patch.dict(reference.SCOPE, {"real_corpus_used_here": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_streaming_claim_cannot_be_promoted(self):
        with mock.patch.dict(reference.SCOPE, {"streaming_inference_here": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_open_release_gate_is_rejected(self):
        bad = dict(reference.RELEASE_GATES[0], blocked=False)
        with mock.patch.object(reference, "RELEASE_GATES", [bad] + reference.RELEASE_GATES[1:]):
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
            self.assertIn("source_reported", row["class"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
