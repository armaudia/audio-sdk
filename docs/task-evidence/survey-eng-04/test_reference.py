# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the deterministic ENG-04 coverage evidence map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import verify  # noqa: E402


class SurveyEng04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = verify.strict_json(HERE / "report.json")
        cls.contract = verify.strict_json(HERE / "contract.json")

    def test_01_claim_pins(self) -> None:
        self.assertEqual(self.report["task_id"], reference.TASK)
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["branch"], reference.BRANCH)
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_02_catalog_matches_pinned_sources(self) -> None:
        entry = reference.catalog_entry()
        backlog = reference.backlog_entry()
        catalog = self.report["catalog"]
        self.assertEqual(catalog["method_families"], entry["method_families"])
        self.assertEqual(catalog["source_ids"], entry["source_ids"])
        self.assertEqual(catalog["input_output"], entry["input_output"])
        self.assertEqual(catalog["live_or_comparison_boundary"], entry["live_or_comparison_boundary"])
        self.assertEqual(catalog["scope"], entry["scope"])
        self.assertEqual(catalog["benchmark_status"], entry["benchmark_status"])
        self.assertEqual(catalog["backlog_family_id"], backlog["family_id"])
        self.assertEqual(catalog["backlog_state"], backlog["state"])

    def test_03_source_leads_match_pinned_ledger(self) -> None:
        lines = reference.source_lead_lines()
        self.assertEqual(len(lines), 3)
        by_id = {item["id"]: item for item in self.report["named_source_leads"]}
        self.assertEqual(set(by_id), {"S43", "S44", "S30"})
        for lead_id, lead in by_id.items():
            line = next(line for line in lines if line.startswith(f"| {lead_id} "))
            self.assertIn(lead["url"], line)
            self.assertEqual(lead["outcome_class"], "source_reported_not_reproduced")

    def test_04_original_method_families_preserved(self) -> None:
        families = self.report["catalog"]["method_families"]
        self.assertEqual(families["classic"],
                         "Codec negotiation; packet duration; FEC; silence suppression/comfort noise")
        self.assertEqual(families["ml"],
                         "Neural codec/redundancy variants are conditional leads")

    def test_05_named_leads_mapped_to_components(self) -> None:
        component_ids = {item["id"] for item in self.report["component_matches"]}
        for lead in self.report["named_source_leads"]:
            self.assertTrue(lead["component_ids"])
            self.assertTrue(set(lead["component_ids"]) <= component_ids)
            self.assertTrue(lead["match_basis"])

    def test_06_family_audit_has_outcomes_and_gaps(self) -> None:
        audit = {item["family_id"]: item for item in self.report["method_family_audit"]}
        self.assertEqual(len(audit), 5)
        for item in audit.values():
            self.assertTrue(item["catalog_text"])
            self.assertTrue(item["status"])
            self.assertTrue(item["local_outcome"])
            self.assertTrue(item["reported_outcome"])
            self.assertTrue(item["missing_evidence"])
        self.assertEqual(audit["ml.neural_codec_redundancy_variants"]["status"],
                         "conditional_leads_researched_not_run")

    def test_07_unowned_gap_has_bounded_followup(self) -> None:
        audit = {item["family_id"]: item for item in self.report["method_family_audit"]}
        negotiation = audit["classic.codec_negotiation"]
        self.assertEqual(negotiation["component_ids"], [])
        self.assertIsNone(negotiation["component_owner"])
        self.assertEqual(negotiation["status"], "missing_component_owner")
        followup = self.report["followups"][0]
        self.assertEqual(followup["id"], negotiation["followup_id"])
        self.assertIsNone(followup["component_owner"])
        self.assertFalse(followup["implemented"])
        self.assertEqual(followup["status"], "open_bounded_feasibility_followup")

    def test_08_historical_executions_separate_outcome_classes(self) -> None:
        for item in self.report["historical_executions"]:
            self.assertIn(item["evidence_class"], {
                "existing_local_fixture_recorded_in_repo_not_rerun",
                "recorded_blocked_attempt_not_rerun",
                "source_reported_not_reproduced",
            })
            if item["evidence_class"] == "source_reported_not_reproduced":
                self.assertIsNone(item["local_outcome"])
        ids = {item["id"] for item in self.report["historical_executions"]}
        self.assertIn("SDK-FND-ELASTIC", ids)
        self.assertIn("SDK-PIPE-RECEIVE", ids)

    def test_09_comparison_inputs_and_controls_are_separated(self) -> None:
        inputs = self.report["comparison_inputs"]
        self.assertIn("PCM/session controls are distinct from encoded packets and playback state.",
                      inputs["separation_rules"])
        self.assertIn("Redundancy-assisted recovery and blind recovery are recorded in different groups.",
                      inputs["separation_rules"])
        controls = {item["id"] for item in self.report["controls"]}
        self.assertEqual(controls, {
            "identity_no_loss", "blind_plc", "redundancy_assisted_fec",
            "silence_cng_transition", "invalid_state_rejection",
        })

    def test_10_no_assets(self) -> None:
        assets = self.report["assets"]
        for key in ("audio_files", "codec_runtime", "model_weights",
                    "captured_network_traces", "generated_binary_assets"):
            self.assertEqual(assets[key], [])

    def test_11_release_boundary_all_false(self) -> None:
        for section in ("scope", "boundary", "release_boundary"):
            for key, value in self.report[section].items():
                if key in verify.FORBIDDEN_SCOPE_KEYS | verify.FORBIDDEN_BOUNDARY_KEYS:
                    self.assertIs(value, False, f"{section}.{key}")
        self.assertEqual(self.report["boundary"]["descriptor_settings"], {})
        self.assertEqual(self.report["boundary"]["public_v0_geometry"]["frame_samples"], 160)

    def test_12_report_is_canonical_and_sidecar_matches(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual(payload, reference.canonical_report_bytes(self.report))
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(),
                         f"{digest}  report.json\n")

    def test_13_pins_match_bytes_and_contract(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            self.assertEqual(hashlib.sha256(
                (reference.SOURCE_ROOT / path).read_bytes()).hexdigest(), digest)
        for mapping in (reference.BOUNDARY_PINS, reference.COMPONENT_EVIDENCE_PINS):
            for path, digest in mapping.items():
                self.assertEqual(hashlib.sha256(
                    (reference.SDK_ROOT / path).read_bytes()).hexdigest(), digest)
        self.assertEqual(self.contract["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["contract_sha256"], hashlib.sha256(
            (HERE / "contract.json").read_bytes()).hexdigest())

    def test_14_repeatability_three_cold_digests(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertEqual(len(repeat["digests"]), 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(repeat["digests"], reference.repeatability()["digests"])

    def test_15_readme_and_followup_links(self) -> None:
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        followup = (HERE / "followups/FEASIBILITY-ENG-04-01.md").read_text(encoding="utf-8")
        self.assertIn("FEASIBILITY-ENG-04-01.md", readme)
        self.assertIn("classic.codec_negotiation", followup)
        self.assertIn("Not implemented", followup)
        self.assertIn("unassigned", followup)

    def test_16_no_forbidden_assets_or_unpinned_files(self) -> None:
        errors: list[str] = []
        verify.check_scope(errors)
        self.assertEqual(errors, [])

    def test_17_verifier_accepts_package(self) -> None:
        errors: list[str] = []
        report = verify.check_report(errors)
        verify.check_followup(errors)
        self.assertTrue(report)
        self.assertEqual(errors, [])

    def test_18_historical_execution_paths_are_pinned_or_present(self) -> None:
        component_ids = {item["id"] for item in self.report["component_matches"]}
        for item in self.report["historical_executions"]:
            self.assertIn("component_ids", item)
            self.assertTrue(item["match_basis"])
            self.assertTrue(set(item["component_ids"]) <= component_ids)
            path = item["path"]
            if path in reference.SOURCE_PINS:
                target = reference.SOURCE_ROOT / path
                self.assertTrue(target.is_file(), path)
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                                 reference.SOURCE_PINS[path], path)
            else:
                self.assertTrue((reference.SDK_ROOT / path).exists(), path)
        pipe = next(item for item in self.report["historical_executions"]
                    if item["id"] == "SDK-PIPE-RECEIVE")
        self.assertEqual(pipe["path"],
                         "audio-benchmark-platform/plan/swarm/handoffs/SDK-PIPE-RECEIVE.md")
        self.assertIn(pipe["path"], reference.SOURCE_PINS)

    def test_19_ml_family_does_not_overreach_named_leads(self) -> None:
        leads = {item["id"]: item for item in self.report["named_source_leads"]}
        self.assertNotIn("se-nac-codec-latent-enhancement-family",
                         leads["S30"]["component_ids"])
        lead_ids = set(leads)
        for item in self.report["component_matches"]:
            self.assertTrue(set(item["matched_source_ids"]) <= lead_ids)
        classic = next(item for item in self.report["component_matches"]
                       if item["id"] == "opus-1-4-standard-decoder-plc")
        self.assertEqual(classic["matched_families"], ["classic.fec"])
        self.assertEqual(classic["matched_source_ids"], [])

    def test_20_candidate_matrix_rows_follow_the_csv(self) -> None:
        import csv
        rows = {}
        with (reference.SOURCE_ROOT /
              "research/voice-enhancement-20261101/candidate_matrix.csv").open(
                newline="", encoding="utf-8") as handle:
            for index, row in enumerate(csv.reader(handle), start=1):
                if index == 1:
                    continue
                rows[index] = row[1]
        self.assertEqual(rows[26], "WaveFit PLC claim")
        self.assertEqual(rows[27], "Lyra II / Lyra V2 codec PLC")
        self.assertEqual(rows[28], "Generative PLC / Complex-Bin2bin")
        self.assertEqual(rows[29], "Conventional waveform PLC controls")
        self.assertEqual(rows[30], "Opus 1.4 standard decoder PLC")
        matrix = next(item for item in self.report["historical_executions"]
                      if item["id"] == "research-candidate-matrix-26-30")
        self.assertIn("rows 26-30", matrix["comparison_inputs"][0])
        self.assertIsNone(matrix["local_outcome"])


if __name__ == "__main__":
    unittest.main()
