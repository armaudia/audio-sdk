# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-REC-02 evidence map."""

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

    def test_invalid_json_payload_type_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_loads(b'{"a":1}')


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()
        self.snapshot = self.builder.snapshot()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertIs(self.report["qualification"]["proposal_only"], True)
        self.assertIs(self.report["qualification"]["qualifies"], False)

    def test_all_release_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([g["id"] for g in gates], ["RG-0%d" % k for k in range(1, 9)])
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
            "language_identification_claim",
            "code_switch_handling_claim",
            "asr_transcription_claim",
            "accent_conversion_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "REC-02")
        self.assertEqual(self.report["taxonomy"]["name"], "Language identification and code-switch handling")
        self.assertEqual(self.report["taxonomy"]["group"], "Recognition and language")
        self.assertEqual(self.report["taxonomy"]["scope"], "support")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S10", "S11"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F11")
        self.assertEqual(self.report["legacy_backlog"]["state"], "catalogued")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        self.assertIn("phonotactic", families)
        self.assertIn("language encoder", families)
        self.assertIn("multilingual", families)
        self.assertIn("streaming", families)
        self.assertIn("code-switch", families)

    def test_source_leads_cover_s10_s11(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S10", "S11"})
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("source_reported_lid_study", classes)
        self.assertIn("source_reported_code_switch_study", classes)
        self.assertIn("source_reported_neural_language_encoder_candidate", classes)
        self.assertIn("source_reported_multilingual_asr_candidate", classes)
        self.assertIn("blocked_streaming_asr_candidate", classes)
        self.assertIn("source_reported_language_corpus_intake", classes)
        self.assertIn("adjacent_english_asr_historical_local", classes)
        self.assertIn("adjacent_english_encoder_historical_local", classes)
        self.assertIn("missing_rec02_cohort", classes)
        self.assertNotIn("lid_accuracy_result", classes)
        self.assertNotIn("code_switch_corpus", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["source_reported_lid_study"], True)
        self.assertIs(classes["source_reported_code_switch_study"], True)
        self.assertIs(classes["source_reported_neural_language_encoder_candidate"], True)
        self.assertIs(classes["source_reported_multilingual_asr_candidate"], True)
        self.assertIs(classes["blocked_streaming_asr_candidate"], True)
        self.assertIs(classes["source_reported_language_corpus_intake"], True)
        self.assertIs(classes["adjacent_english_asr_historical_local"], True)
        self.assertIs(classes["adjacent_english_encoder_historical_local"], True)
        self.assertIs(classes["adjacent_english_tsm_asr_proxy"], True)
        self.assertIs(classes["rec02_language_identification_execution"], False)
        self.assertIs(classes["rec02_code_switch_execution"], False)
        self.assertIs(classes["multilingual_language_labels"], False)
        self.assertIs(classes["code_switch_corpus"], False)
        self.assertIs(classes["lid_accuracy_result"], False)
        self.assertIs(classes["human_listening_result"], False)
        text = " ".join(row["class"] for row in self.report["comparison_inputs"])
        text += " " + " ".join(row["outcome_class"] for row in self.report["historical_executions"])
        self.assertNotIn("lid_accuracy", text)
        self.assertNotIn("code_switch_corpus", text)

    def test_acceptance_profile_absence_is_recorded(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "Recognition")
        self.assertIs(profile["profile_row_present"], False)
        self.assertIn("no Recognition/language profile", profile["profile_note"])
        self.assertTrue(profile["blocked"])

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
        self.assertEqual(
            reference.canonical_bytes(rebuilt), reference.canonical_bytes(self.report)
        )
        self.assertNotIn("sha256_at_read", rebuilt["mutable_provenance"])

    def test_historical_executions_are_adjacent_and_censused(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertIs(row["adjacent"], True, row["id"])
            self.assertIs(row["not_component_evidence"], True, row["id"])
            self.assertIn("not rerun by this survey", row["scope"])
            self.assertTrue(row["values"])

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
        self.assertIn("source:research/tsm-followup-20261101/README.md", labels)
        self.assertIn("source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertIn("worktree:docs/task-evidence/survey-det-02/README.md", labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)

    def test_category_boundary_is_explicit(self):
        boundary = self.report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("One language label per clip is different", boundary)
        self.assertIn("detecting switches within an utterance", boundary)
        scope = self.report["category_scope"]
        self.assertIs(scope["per_clip_label_and_switch_detection_are_distinct"], True)
        self.assertIs(scope["unknown_language_is_not_a_known_language"], True)
        families = {row["family_id"]: row for row in self.report["method_families"]}
        self.assertIn("phonotactic", families["MF-C1"]["family"])
        self.assertIn("language-identification head", families["MF-M1"]["family"])
        self.assertIn("code-switch", families["MF-M2"]["family"].lower() + families["MF-M2"]["boundary"].lower())
        self.assertIn("cannot identify a language", families["MF-M4"]["boundary"])

    def test_adjacent_values_are_transcribed_not_rerun(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        asr = by_id["HE-1"]
        self.assertEqual(asr["outcome_class"], "adjacent_english_asr_historical_local")
        self.assertEqual(asr["values"]["whisper_cpu_inference_seconds"], 1.45)
        self.assertEqual(asr["values"]["rtf_excluding_load"], 0.096)
        self.assertEqual(asr["values"]["wer_percent"], 11.8)
        self.assertEqual(asr["values"]["wer_word_errors"], 4)
        self.assertEqual(asr["values"]["wer_words"], 34)
        self.assertEqual(asr["values"]["asr_boundary_mae_ms"], 23.2)
        self.assertEqual(asr["values"]["asr_within_50_ms_percent"], 91.7)
        self.assertIn("not rerun by this survey", asr["scope"])
        self.assertIn("English-only", asr["scope"])
        tsm = by_id["HE-2"]
        self.assertEqual(tsm["values"]["source_wer_percent"], 30.15)
        self.assertEqual(tsm["values"]["reference_words"], 136)
        rate = by_id["HE-3"]
        self.assertEqual(rate["values"]["wav2vec2_base_rate_mae_syll_s"], 0.593)
        self.assertEqual(rate["values"]["meetings"], 1)

    def test_adjacent_evidence_is_not_promoted_to_language_identification(self):
        text = " ".join(
            row["scope"] for row in self.report["historical_executions"]
        ).lower()
        self.assertNotIn("lid accuracy", text)
        self.assertIn("not language identification", text)
        self.assertIn("english-only", text)

    def test_gaps_without_component_owner_are_bounded(self):
        by_id = {gap["id"]: gap for gap in self.report["gaps"]}
        for gap_id in ("G01", "G05", "G06", "G07", "G08", "G09", "G10", "G11"):
            self.assertIs(by_id[gap_id]["feasibility_task_exists"], False, gap_id)
            note = by_id[gap_id]["owner_note"].lower()
            self.assertIn("no", note, gap_id)
        for gap_id in ("G02", "G03", "G04"):
            self.assertIs(by_id[gap_id]["feasibility_task_exists"], True, gap_id)


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
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(reference.MapError):
                reference.build_report(workspace=tmp)
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

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        for key, value in (
            ("rec02_language_identification_execution", True),
            ("code_switch_corpus", True),
            ("lid_accuracy_result", True),
        ):
            with self.subTest(key=key):
                with mock.patch.dict(reference.EVIDENCE_CLASSES, {key: value}):
                    with self.assertRaises(reference.MapError):
                        self.builder.build()
                self._assert_unchanged()

    def test_open_release_gate_rejected_without_state_change(self):
        gates = [dict(gate) for gate in reference.RELEASE_GATES]
        gates[0]["blocked"] = False
        with mock.patch.object(reference, "RELEASE_GATES", gates):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_taxonomy_record_rejected_without_state_change(self):
        with mock.patch.object(reference, "CATEGORY_ID", "REC-99"):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_language_identification_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.SCOPE, {"language_identification_claim": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_conflated_clip_label_and_switch_detection_rejected(self):
        with mock.patch.dict(
            reference.CATEGORY_SCOPE,
            {"per_clip_label_and_switch_detection_are_distinct": False},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
