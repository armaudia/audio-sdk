# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-RST-04 evidence map."""

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
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")
        self.assertIs(self.report["qualification"]["qualifies"], False)
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")

    def test_all_release_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
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
            "processor_exposure",
            "public_default",
            "network_access",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)
        self.assertIs(self.report["evidence_classes"]["human_listening_result"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "RST-04")
        self.assertEqual(self.report["taxonomy"]["name"], "Packet-loss concealment and gap recovery")
        self.assertEqual(self.report["taxonomy"]["group"], "Distortion restoration")
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S30", "S41"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F10")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        self.assertIn("zero-fill", families)
        self.assertIn("pitch-period", families)
        self.assertIn("autoregressive", families)
        self.assertIn("decoder concealment", families)
        self.assertIn("redundancy-assisted", families)
        self.assertIn("neural", families)

    def test_source_leads_cover_s30_s41(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S30", "S41"})
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])
        by_id = {lead["source_id"]: lead for lead in self.report["source_leads"]}
        self.assertIn("DRED", by_id["S30"]["finding"])
        self.assertIn("NetEq", by_id["S41"]["finding"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_real_audio_screen_not_reproduced", classes)
        self.assertIn("historical_local_paired_synthetic", classes)
        self.assertIn("historical_local_paired_synthetic_clean_transparency", classes)
        self.assertIn("historical_local_packet_parity_synthetic", classes)
        self.assertIn("historical_local_pilot_not_reproduced", classes)
        self.assertIn("source_reported_only", classes)
        self.assertIn("source_reported_not_run", classes)
        self.assertNotIn("human_listening_result", classes)
        self.assertNotIn("unpaired_predictive_historical_local", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["paired_synthetic_historical_local"], True)
        self.assertIs(classes["historical_local_real_audio_screen_not_reproduced"], True)
        self.assertIs(classes["historical_pilot_means_not_reproduced"], True)
        self.assertIs(classes["clean_transparency_diagnostic_historical_local"], True)
        self.assertIs(classes["packet_parity_synthetic_historical_local"], True)
        self.assertIs(classes["vendor_or_source_reported"], True)
        self.assertIs(classes["unpaired_predictive_historical_local"], False)
        self.assertIs(classes["prepared_listening_without_ratings"], False)

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

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
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
            if not gap["feasibility_task_exists"]:
                self.assertIn("no", gap["owner_note"].lower() + gap["id"].lower())

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
        self.assertIn("source:research/distortion_restoration_20261028.md", labels)
        self.assertIn("source:research/voice-enhancement-20261101/agent-opus-plc/REPORT.md", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertIn("worktree:docs/task-evidence/zero-fill-plc/README.md", labels)
        self.assertIn("worktree:docs/task-evidence/elastic-pcm-packets/README.md", labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)

    def test_plausible_fill_is_not_word_recovery(self):
        boundary = self.report["taxonomy"]["live_or_comparison_boundary"]
        self.assertIn("Plausible gap filling does not prove recovery of the original words", boundary)
        families = {row["family_id"]: row for row in self.report["method_families"]}
        self.assertIn("redundancy-assisted", families["MF-C5"]["family"].lower())
        self.assertIn("opus-dred", families["MF-C5"]["components"])
        note = {row["id"]: row for row in self.report["gaps"]}["G06"]["evidence_gap"]
        self.assertIn("not recovery of the original words", note)

    def test_no_opus_claim_for_synthetic_surrogate(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        surrogate = by_id["HE-7"]
        self.assertIs(surrogate["values"]["opus_runtime_invoked"], False)
        self.assertIn("not Opus", surrogate["scope"])
        controls = {row["id"]: row for row in self.report["controls"]}
        self.assertIn("deliberately not Opus", controls["CT-6"]["role"])

    def test_codec_screen_values_are_transcribed_not_rerun(self):
        by_id = {row["id"]: row for row in self.report["historical_executions"]}
        screen = by_id["HE-1"]
        self.assertEqual(screen["outcome_class"], "historical_local_real_audio_screen_not_reproduced")
        self.assertEqual(screen["values"]["isolated_opus_plc_si_sdr_db"], 2.39)
        self.assertEqual(screen["values"]["burst_opus_plc_si_sdr_db"], 0.92)
        self.assertEqual(screen["values"]["intact_opus_si_sdr_db"], 5.44)
        self.assertIn("not rerun by this survey", screen["scope"])

    def test_packet_parity_is_bounded(self):
        control = {row["id"]: row for row in self.report["controls"]}["CT-8"]
        self.assertIn("single packet is recovered", control["role"])
        self.assertIn("two-packet burst is rejected", control["role"])
        comparison = {row["id"]: row for row in self.report["comparison_inputs"]}["CI-7"]
        self.assertIn("two-packet burst is rejected", comparison["input"])
        self.assertIn("no codec", comparison["boundary"].lower())

    def test_gaps_without_component_owner_are_bounded(self):
        by_id = {gap["id"]: gap for gap in self.report["gaps"]}
        for gap_id in ("G06", "G07", "G08", "G09"):
            self.assertIs(by_id[gap_id]["feasibility_task_exists"], False, gap_id)
            note = by_id[gap_id]["owner_note"].lower()
            self.assertIn("component owner", note, gap_id)
            self.assertIn("no", note, gap_id)
        for gap_id in ("G01", "G02", "G03", "G04", "G05"):
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

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.EVIDENCE_CLASSES, {"unpaired_predictive_historical_local": True}
        ):
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
        with mock.patch.object(reference, "CATEGORY_ID", "RST-99"):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
