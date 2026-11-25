# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest acceptance suite for the task-local ENG category evidence map."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_json_path(HERE / "report.json")
        cls.inventory = reference.strict_json_path(
            reference.SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
        cls.board = reference.strict_json_path(
            reference.SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json")
        cls.tasks = reference._index_by_id(cls.board.get("tasks"), "tasks")

    def test_pins_are_exact_and_present(self) -> None:
        verified = reference.validate_pins()
        self.assertEqual(len(verified),
                         len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS))
        self.assertTrue(all(verified.values()))
        self.assertEqual(self.report["source_pin_verification"], verified)
        self.assertEqual(self.report["source_pin_selectors"],
                         reference.SOURCE_PIN_SELECTORS)
        self.assertTrue(self.report["board_status_is_observation_only"])

    def test_strict_json_rejects_duplicate_keys_and_nonfinite(self) -> None:
        with self.assertRaises(reference.Rejected) as duplicate:
            reference.strict_json_bytes(b'{"ENG-01":1,"ENG-01":2}')
        self.assertIn("duplicate_json_key", duplicate.exception.reason)
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(reference.Rejected) as nonfinite:
                    reference.strict_json_bytes(
                        ('{"x":' + token + "}").encode("ascii"))
                self.assertIn("nonfinite_json_constant", nonfinite.exception.reason)

    def test_strict_json_rejects_missing_file(self) -> None:
        with self.assertRaises(reference.Rejected) as missing:
            reference.strict_json_path(HERE / "definitely-absent.json")
        self.assertIn("missing_file", missing.exception.reason)

    def test_disposition_and_release_boundary(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertTrue(self.report["profile_application"]["no_cohort_or_scorer_claim"])
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            else:
                self.assertIs(value, False, key)
        for key in ("real_corpus", "real_weights", "audio_runtime_executed",
                    "model_runtime_executed", "vendor_runtime_executed", "listening",
                    "device_timing", "benchmark", "release_claim", "registered_provider"):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertEqual(self.report["format"]["sample_rate_hz"], 16000)
        self.assertEqual(self.report["format"]["channels"], 1)
        self.assertEqual(self.report["format"]["sample_format"], "f32")
        self.assertEqual(self.report["format"]["frame_samples"], 160)
        self.assertIs(self.report["format"]["sdk_callback_invoked"], False)

    def test_category_scope_is_engineering_not_language(self) -> None:
        scope = self.report["category_scope"]
        self.assertEqual(scope["code"], "ENG")
        self.assertTrue(scope["not_a_language_scope"])
        self.assertEqual(scope["category_ids"], reference.CATEGORY_IDS)
        self.assertTrue(any(value.startswith("REC-02")
                            for value in scope["excluded_examples"]))

    def test_method_families_and_source_leads_match_inventory(self) -> None:
        taxonomy = reference._index_by_id(self.inventory["taxonomy"], "taxonomy")
        sources = reference._index_by_id(self.inventory["taxonomy_sources"],
                                         "taxonomy_sources")
        self.assertEqual(set(self.report["categories"]), set(reference.CATEGORY_IDS))
        for category_id in reference.CATEGORY_IDS:
            row = taxonomy[category_id]
            entry = self.report["categories"][category_id]
            self.assertEqual(entry["name"], row["name"])
            self.assertEqual(entry["method_families"]["classic"],
                             row["method_families"]["classic"])
            self.assertEqual(entry["method_families"]["ml"],
                             row["method_families"]["ml"])
            self.assertEqual(entry["source_ids"], row["source_ids"])
            self.assertEqual([lead["id"] for lead in entry["source_leads"]],
                             row["source_ids"])
            for lead in entry["source_leads"]:
                self.assertEqual(lead["url"], sources[lead["id"]]["url"])

    def test_follow_ups_are_board_linked_and_not_invented(self) -> None:
        for task_id in reference.FOLLOW_UP_POLICY["existing_feasibility_task_ids"]:
            self.assertEqual(self.tasks[task_id]["mode"], "feasibility")
        seen_gaps = set()
        for entry in self.report["categories"].values():
            for gap in entry["gaps"]:
                self.assertNotIn(gap["id"], seen_gaps)
                seen_gaps.add(gap["id"])
                self.assertIs(gap["invented"], False)
                self.assertIs(gap["actionable"], True)
                task_id = gap["follow_up_task_id"]
                if task_id is None:
                    self.assertTrue(gap["no_task_reason"])
                    self.assertEqual(gap["follow_up_status"], "no_board_task")
                else:
                    self.assertEqual(self.tasks[task_id]["mode"], "feasibility")
                    self.assertEqual(gap["follow_up_mode"], "feasibility")
                    self.assertEqual(gap["follow_up_status"],
                                     reference.BOARD_STATUS_SNAPSHOT[task_id])
        self.assertTrue(seen_gaps)

    def test_all_gates_blocked(self) -> None:
        self.assertEqual([gate["name"] for gate in self.report["gates"]],
                         reference.GATE_NAMES)
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])

    def test_adverse_cases_reject_without_state_change(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["state_unchanged"])
        self.assertTrue(adverse["valid_map_accepted"])
        for name, case in adverse["cases"].items():
            self.assertEqual(case["status"], "rejected", name)
            self.assertTrue(case["state_unchanged"], name)
            self.assertTrue(case["reason"], name)
        state = reference.MapState(reference.core_report()["categories"], self.tasks)
        before = state.digest()
        invalid = [
            b'{"ENG-01":{},"ENG-01":{}}',
            b'{"ENG-01":{"x":NaN}}',
            b'{"ENG-01":{"x":Infinity}}',
            reference.canonical_bytes({"ENG-04": {}}),
        ]
        for raw in invalid:
            with self.assertRaises(reference.Rejected):
                state.apply(raw)
            self.assertEqual(state.digest(), before)
        accepted = state.apply(reference.canonical_bytes(
            reference.core_report()["categories"]))
        self.assertEqual(accepted["status"], "accepted")

    def test_canonical_report_and_digest_sidecar(self) -> None:
        raw = (HERE / "report.json").read_bytes()
        self.assertEqual(raw, reference.canonical_report_bytes(self.report))
        self.assertEqual((HERE / "report.json.sha256").read_bytes(),
                         f"{reference.sha256(raw)}  report.json\n".encode("ascii"))
        contract = reference.strict_json_path(HERE / "contract.json")
        self.assertEqual(self.report["contract_sha256"],
                         reference.sha256((HERE / "contract.json").read_bytes()))
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")

    def test_sources_manifest_is_deterministic(self) -> None:
        raw = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(raw, reference.sources_bytes())
        lines = [line for line in raw.decode("ascii").splitlines()
                 if line and not line.startswith("#")]
        self.assertEqual(len(lines),
                         len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS)
                         + len(reference.LOCAL_PIN_PATHS))
        self.assertEqual(len({line.split("  ", 1)[1] for line in lines}), len(lines))

    def test_three_cold_start_regeneration_is_byte_identical(self) -> None:
        repeat = reference.repeatability()
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(repeat, self.report["repeatability"])

    def test_verify_is_read_only_and_passes(self) -> None:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "verify.py"], cwd=HERE,
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0,
                         result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
