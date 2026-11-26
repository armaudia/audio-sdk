# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-TRN-05 evidence map."""

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
            "real_speech_used_here",
            "real_corpus_used_here",
            "weights_loaded_here",
            "runtime_invoked_here",
            "model_inference_here",
            "streaming_inference_here",
            "listening_here",
            "device_timing_here",
            "latency_claim",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
            "tts_quality_claim",
            "voice_cloning_claim",
            "reference_similarity_claim",
            "naturalness_claim",
            "content_preservation_claim",
            "network_access",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "TRN-05")
        self.assertEqual(self.report["taxonomy"]["scope"], "requested_optional_adjacent")
        self.assertEqual(self.report["taxonomy"]["output_kind"], "waveform")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S40"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F14")
        self.assertEqual(self.report["legacy_backlog"]["state"], "catalogued")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        classic = " ".join(
            row["family"] for row in self.report["method_families"] if row["branch"] == "classic"
        ).lower()
        ml = " ".join(
            row["family"] for row in self.report["method_families"] if row["branch"] == "ml"
        ).lower()
        self.assertIn("open", classic)
        for term in ("flow", "codec", "whole-utterance", "vits", "gated", "fixed-voice"):
            self.assertIn(term, ml)
        statuses = {row["status"] for row in self.report["method_families"]}
        self.assertIn("no_local_component_or_execution_in_reviewed_records", statuses)
        self.assertIn("adjacent_local_generation_only_no_reference_similarity", statuses)
        self.assertIn("blocked_gated_checkpoint_no_inference", statuses)

    def test_source_lead_is_s40(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S40"})
        lead = self.report["source_leads"][0]
        self.assertEqual(lead["title"], "F5-TTS official implementation")
        self.assertEqual(lead["mapped_components"], ["f5-tts"])
        self.assertEqual(lead["gap_ids"], ["G01", "G02"])
        self.assertTrue(lead["finding"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("source_only_reference_tts_protocol", classes)
        self.assertIn("source_reported_reference_tts_candidate", classes)
        self.assertIn("source_reported_blocked_candidate", classes)
        self.assertIn("historical_research_zero_shot_streaming_tts", classes)
        self.assertIn("historical_research_reference_conditioned_whole_utterance_tts", classes)
        self.assertIn("historical_research_fixed_voice_tts_control", classes)
        self.assertIn("adjacent_vocoder_component_boundary", classes)
        self.assertIn("missing_required_cohort", classes)
        self.assertNotIn("human_listening_result", classes)
        self.assertNotIn("reference_similarity_measured", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        for key in (
            "historical_research_zero_shot_streaming_tts",
            "historical_research_reference_conditioned_whole_utterance_tts",
            "historical_research_fixed_voice_tts_control",
            "source_only_reference_tts_protocol",
            "source_reported_reference_tts_candidate",
            "source_reported_blocked_candidate",
            "source_reported_candidate_documentation",
            "adjacent_vocoder_component_boundary",
        ):
            self.assertIs(classes[key], True, key)
        for key in (
            "reference_cloning_execution",
            "reference_similarity_measured",
            "naturalness_measured",
            "human_listening_result",
            "content_preservation_gold",
            "multi_utterance_or_multi_speaker_cohort",
            "rights_qualified_reference_voice_corpus",
            "streaming_first_audio_claim",
            "device_timing",
            "cpu_accelerator_parity",
            "tts_quality_claim",
            "new_execution_in_this_survey",
            "parity_or_qualification_claim",
            "provider_enablement",
            "release_approval",
        ):
            self.assertIs(classes[key], False, key)

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
        self.assertIs(rebuilt["provenance"]["board_claim_edited"], False)

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        self.assertEqual(
            {row["id"] for row in self.report["historical_executions"]},
            {"HE-1", "HE-2", "HE-3"},
        )
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertEqual(row["scope_class"], "historical_research_execution", row["id"])
            self.assertIs(row["merged_task_evidence"], False, row["id"])
            self.assertIs(row["not_rerun"], True, row["id"])
            self.assertIn("not rerun by this survey", row["scope"])

    def test_controls_and_assets_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"] + self.report["historical_executions"]:
            self.assertIn(row["source_pin"], pins)
            if "wer_source_pin" in row:
                self.assertIn(row["wer_source_pin"], pins)

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
        outputs = run.cold_start_bytes()
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
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_historical_values_are_exact(self):
        he1 = self.report["historical_executions"][0]["values"]
        self.assertEqual(he1["text_prompts"], 1)
        self.assertEqual(he1["chunk_count"], 4)
        self.assertEqual(he1["audio_seconds"], 10.0)
        self.assertEqual(he1["first_chunk_seconds_from_inference_call"], 23.810076208028477)
        self.assertEqual(he1["file_rtf"], 8.066152424999746)
        self.assertIs(he1["reference_similarity_measured"], False)
        self.assertIs(he1["first_audio_latency_claim"], False)
        he2 = self.report["historical_executions"][1]["values"]
        self.assertEqual(he2["audio_seconds"], 8.92)
        self.assertEqual(he2["generation_wall_seconds"], 11.46746112499386)
        self.assertEqual(he2["file_rtf"], 1.2855898122190428)
        self.assertIs(he2["streaming_chunks_exposed"], False)
        self.assertIsNone(he2["first_audio_latency_seconds"])
        he3 = self.report["historical_executions"][2]["values"]
        self.assertEqual(he3["preset_voice"], "af_heart")
        self.assertEqual(he3["audio_seconds"], 9.025)
        self.assertEqual(he3["first_chunk_after_start_seconds"], 57.297223249974195)
        self.assertIs(he3["reference_voice_cloning"], False)
        self.assertEqual(he3["reference_audio_seconds"], 0.0)

    def test_tts_is_not_conversion_or_asr(self):
        scope = self.report["category_scope"]
        self.assertIs(scope["cloning_via_conversion_is_not_tts"], True)
        self.assertIs(scope["tts_is_optional_not_required_call_replacement"], True)
        self.assertIs(scope["content_identity_and_naturalness_are_separate_outcomes"], True)
        self.assertIs(scope["consent_and_reference_availability_are_independent_gates"], True)
        self.assertIs(scope["streaming_label_is_not_low_conversational_delay"], True)
        self.assertEqual(scope["not_voice_conversion"], "TRN-04")
        self.assertEqual(scope["not_accent_conversion"], "TRN-03")
        self.assertEqual(scope["not_asr_or_transcription"], "REC-01")
        self.assertEqual(scope["not_speaker_identification_or_verification"], "SPK-05")
        boundary = self.report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("Cloning via conversion belongs to TRN-04", boundary)
        self.assertIn("optional branch", boundary)

    def test_missing_reference_cohort_is_explicit(self):
        missing = [
            row for row in self.report["comparison_inputs"] if row["class"] == "missing_required_cohort"
        ]
        self.assertEqual(len(missing), 1)
        self.assertIn("missing", missing[0]["boundary"].lower())
        assets = [row for row in self.report["assets"] if row["class"] == "missing_asset"]
        self.assertTrue(assets)
        for row in assets:
            self.assertIn("not present", row["status"].lower())

    def test_fixed_voice_and_vocoders_are_not_cloning(self):
        families = {row["family_id"]: row for row in self.report["method_families"]}
        self.assertIn("kokoro-82m", families["MF-M6"]["components"])
        self.assertIn("hifi-gan-vocoder", families["MF-M6"]["components"])
        self.assertIn("vocos-vocoder", families["MF-M6"]["components"])
        self.assertIn("world-vocoder", families["MF-M6"]["components"])
        self.assertNotIn("kokoro-82m", families["MF-M1"]["components"])
        self.assertNotIn("hifi-gan-vocoder", families["MF-M1"]["components"])
        kokoro = self.report["historical_executions"][2]
        self.assertEqual(kokoro["component_ids"], ["kokoro-82m"])
        self.assertIs(kokoro["values"]["reference_voice_cloning"], False)


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

    def test_merged_task_evidence_promotion_is_rejected(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HY", merged_task_evidence=True)
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

    def test_quality_claim_class_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"tts_quality_claim": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_human_listening_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"human_listening_result": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_reference_similarity_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"reference_similarity_measured": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_cloning_execution_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"reference_cloning_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_streaming_first_audio_claim_is_rejected(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"streaming_first_audio_claim": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_required_cohort_cannot_be_promoted(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"rights_qualified_reference_voice_corpus": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_open_release_gate_is_rejected(self):
        bad = list(reference.RELEASE_GATES)
        bad[0] = dict(bad[0], blocked=False)
        with mock.patch.object(reference, "RELEASE_GATES", bad):
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
            self.assertTrue(row["class"].startswith("source_reported_"))

    def test_gaps_without_component_owner_are_bounded(self):
        report = reference.build_report()
        for gap in report["gaps"]:
            if not gap["feasibility_task_exists"]:
                self.assertIn("no", gap["owner_note"].lower(), gap["id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
