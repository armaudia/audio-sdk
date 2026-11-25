# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-TRN-04 evidence map."""

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
        self.assertEqual(
            self.report["release_boundary"]["blocked_gates"],
            [gate["id"] for gate in gates],
        )

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
            "voice_conversion_quality_claim",
            "target_similarity_claim",
            "content_preservation_claim",
            "identity_preservation_claim",
            "network_access",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["scope"]["no_new_execution"], True)
        self.assertIs(self.report["scope"]["historical_citations_include_real_speech"], True)
        self.assertIs(self.report["scope"]["historical_citations_include_research_outputs"], True)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)
        release = self.report["release_boundary"]
        self.assertIs(release["release_allowed"], False)
        self.assertIs(release["release_claim"], False)
        self.assertEqual(release["installed_v0_geometry"], reference.FORMAT)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "TRN-04")
        self.assertEqual(self.report["taxonomy"]["name"], "Speech-to-speech voice conversion")
        self.assertEqual(self.report["taxonomy"]["group"], "Playback and voice transformations")
        self.assertEqual(self.report["taxonomy"]["scope"], "requested_optional")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S38", "S39"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F14")
        self.assertEqual(self.report["legacy_backlog"]["activation_state"], "catalogued")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertIn("classic", branches)
        self.assertIn("ml", branches)
        families = " ".join(row["family"] for row in self.report["method_families"])
        self.assertIn("Statistical spectral mapping", families)
        self.assertIn("GMM", families)
        self.assertIn("Content/speaker-disentangled", families)
        self.assertIn("Streaming and flow/diffusion", families)

    def test_source_leads_are_s38_s39(self):
        self.assertEqual(
            [lead["source_id"] for lead in self.report["source_leads"]],
            ["S38", "S39"],
        )
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_fixed_source_target_pair", classes)
        self.assertIn("historical_local_meanvc2_file_conversion", classes)
        self.assertIn("historical_local_seedvc_file_conversion", classes)
        self.assertIn("historical_local_llvc_streaming_simulation", classes)
        self.assertIn("historical_local_offline_vc_conversion", classes)
        self.assertIn("historical_local_rvc_target_conversion", classes)
        self.assertIn("historical_local_seedvc_single_block", classes)
        self.assertIn("historical_local_vocos_decoder_timing", classes)
        self.assertIn("source_reported_streamvc_lead", classes)
        self.assertIn("missing_rights_cleared_vc_cohort", classes)
        self.assertNotIn("human_listening_result", classes)
        self.assertNotIn("real_vc_benchmark", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["historical_local_meanvc2_file_conversion"], True)
        self.assertIs(classes["historical_local_seedvc_file_conversion"], True)
        self.assertIs(classes["historical_local_llvc_streaming_simulation"], True)
        self.assertIs(classes["historical_local_offline_vc_conversion"], True)
        self.assertIs(classes["historical_local_rvc_target_conversion"], True)
        self.assertIs(classes["historical_local_seedvc_single_block"], True)
        self.assertIs(classes["historical_local_vocos_decoder_timing"], True)
        self.assertIs(classes["source_reported_streamvc_lead"], True)
        self.assertIs(classes["source_reported_seedvc_upstream"], True)
        self.assertIs(classes["missing_rights_cleared_vc_cohort"], True)
        self.assertIs(classes["real_vc_benchmark"], False)
        self.assertIs(classes["human_listening_result"], False)
        self.assertIs(classes["independent_speaker_identity_gold"], False)
        self.assertIs(classes["target_similarity_gold"], False)
        self.assertIs(classes["content_preservation_certificate"], False)
        self.assertIs(classes["sustained_stream_latency"], False)
        self.assertIs(classes["device_timing"], False)
        self.assertIs(classes["quality_claim"], False)

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
            self.assertTrue(row["component_ids"], row["id"])

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

    def test_gaps_without_component_owner_are_bounded(self):
        by_id = {gap["id"]: gap for gap in self.report["gaps"]}
        for gap_id in ("G01", "G02", "G03", "G04", "G05", "G06", "G08", "G12", "G13"):
            self.assertIs(by_id[gap_id]["feasibility_task_exists"], False, gap_id)
            note = by_id[gap_id]["owner_note"].lower()
            self.assertIn("component", note, gap_id)
        for gap_id in ("G07", "G09", "G10", "G11"):
            self.assertIs(by_id[gap_id]["feasibility_task_exists"], True, gap_id)

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
        self.assertIn("source:research/voice-conversion-eval-20261101/README.md", labels)
        self.assertIn("source:research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertIn("worktree:docs/task-evidence/survey-trn-01/README.md", labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        combined = self.report["local_vs_reported_outcomes"]
        self.assertEqual(combined["local"]["classification"], "historical_local_not_rerun")
        self.assertEqual(combined["reported"]["classification"], "source_reported_not_reproduced")
        self.assertFalse(combined["cross_comparison"]["performed"])
        self.assertFalse(combined["cross_comparison"]["numeric_parity_claimed"])
        self.assertTrue(all(not item["qualifies_candidate"] for item in combined["ledger"]))

    def test_category_boundary_is_explicit(self):
        boundary = self.report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("Evaluate target similarity separately from words, prosody and delay", boundary)
        self.assertIn("available implementation and weights are required", boundary)
        scope = self.report["category_scope"]
        for key in (
            "waveform_transformation_only",
            "designated_speaker_or_timbre_change_only",
            "content_preservation_is_separate_from_target_similarity",
            "target_similarity_is_not_speaker_identity_gold",
            "prosody_and_delay_are_separate_outcomes",
            "streaming_label_is_not_low_conversational_delay",
        ):
            self.assertIs(scope[key], True, key)
        families = {row["family_id"]: row for row in self.report["method_families"]}
        self.assertIn("statistical spectral mapping", families["MF-C1"]["family"].lower())
        self.assertIn("vocoder", families["MF-C2"]["family"].lower())
        self.assertIn("content/speaker-disentangled", families["MF-M1"]["family"].lower())
        self.assertIn("streaming", families["MF-M2"]["family"].lower())
        self.assertIn("trn-05", families["MF-M3"]["family"].lower())
        self.assertIn("trn-03", families["MF-M4"]["family"].lower())

    def test_historical_values_are_transcribed_not_rerun(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        self.assertEqual(by_id["HE-1"]["values"]["file_rtf"], 0.959)
        self.assertEqual(by_id["HE-1"]["values"]["target_encoder_cosine"], 0.669)
        self.assertEqual(by_id["HE-2"]["values"]["file_rtf"], 0.396)
        self.assertEqual(by_id["HE-2"]["values"]["target_encoder_cosine"], 0.702)
        self.assertEqual(by_id["HE-3"]["values"]["warm_file_rtf"], 0.244)
        self.assertEqual(by_id["HE-4"]["values"]["chunk_ms"], 13)
        self.assertIs(by_id["HE-4"]["values"]["target_similarity_scored"], False)
        self.assertEqual(by_id["HE-5"]["values"]["in_model_speaker_cosine"], 0.890)
        self.assertEqual(by_id["HE-6"]["values"]["file_rtf"], 2.63)
        self.assertEqual(by_id["HE-7"]["values"]["speaker_id"], 1)
        self.assertIs(by_id["HE-7"]["values"]["target_mapping_verified"], False)
        self.assertEqual(by_id["HE-8"]["values"]["block_realtime_factor"], 92.55)
        self.assertIs(by_id["HE-9"]["values"]["end_to_end_conversion"], False)


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

    def test_unrerun_execution_flag_is_checked(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], not_rerun=False)
        with mock.patch.object(reference, "HISTORICAL_EXECUTIONS", [bad]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        for key, value in (
            ("real_vc_benchmark", True),
            ("human_listening_result", True),
            ("sustained_stream_latency", True),
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
        with mock.patch.object(reference, "CATEGORY_ID", "TRN-99"):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
