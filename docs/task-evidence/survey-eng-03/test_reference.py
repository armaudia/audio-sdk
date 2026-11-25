# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest acceptance suite for the task-local ENG-03 evidence map."""

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
            reference.SOURCE_ROOT /
            "audio-benchmark-platform/plan/INVENTORY.json")
        cls.board = reference.strict_json_path(
            reference.SOURCE_ROOT /
            "audio-benchmark-platform/plan/swarm/TASKS.json")
        cls.registry = reference.strict_json_path(
            reference.SOURCE_ROOT / "research/category_registry.json")
        cls.backlog = reference.strict_json_path(
            reference.SOURCE_ROOT / "research/task_backlog.json")
        cls.tasks = reference._index_by_id(cls.board.get("tasks"), "tasks")

    def test_pins_and_quotes_are_exact_and_present(self) -> None:
        verified = reference.validate_pins()
        self.assertEqual(len(verified),
                         len(reference.SOURCE_PINS)
                         + len(reference.BOUNDARY_PINS))
        self.assertTrue(all(verified.values()))
        self.assertEqual(self.report["source_pin_verification"], verified)
        self.assertEqual(self.report["source_pin_selectors"],
                         reference.SOURCE_PIN_SELECTORS)
        quotes = reference.validate_quotes()
        self.assertEqual(set(quotes), set(reference.QUOTE_CHECKS))
        self.assertTrue(all(quotes.values()))
        self.assertEqual(self.report["quote_verification"], quotes)
        self.assertTrue(self.report["board_status_is_observation_only"])

    def test_strict_json_rejects_duplicate_keys_and_nonfinite(self) -> None:
        with self.assertRaises(reference.Rejected) as duplicate:
            reference.strict_json_bytes(b'{"ENG-03":1,"ENG-03":2}')
        self.assertIn("duplicate_json_key", duplicate.exception.reason)
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(reference.Rejected) as nonfinite:
                    reference.strict_json_bytes(
                        ('{"x":' + token + "}").encode("ascii"))
                self.assertIn("nonfinite_json_constant",
                              nonfinite.exception.reason)

    def test_strict_json_rejects_missing_file(self) -> None:
        with self.assertRaises(reference.Rejected) as missing:
            reference.strict_json_path(HERE / "definitely-absent.json")
        self.assertIn("missing_file", missing.exception.reason)

    def test_disposition_and_release_boundary(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertTrue(
            self.report["profile_application"]["no_cohort_or_scorer_claim"])
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            else:
                self.assertIs(value, False, key)
        for key in ("real_corpus", "real_weights", "audio_runtime_executed",
                    "model_runtime_executed", "codec_runtime_executed",
                    "vendor_runtime_executed", "network_trace_used",
                    "jitter_buffer_executed",
                    "adaptive_playout_executed", "listening",
                    "device_timing", "benchmark", "release_claim",
                    "registered_provider"):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertEqual(self.report["scope"]["category_ids"], ["ENG-03"])
        self.assertEqual(self.report["format"]["sample_rate_hz"], 16000)
        self.assertEqual(self.report["format"]["channels"], 1)
        self.assertEqual(self.report["format"]["sample_format"], "f32")
        self.assertEqual(self.report["format"]["frame_samples"], 160)
        self.assertIs(self.report["format"]["sdk_callback_invoked"], False)
        for value in self.report["prohibited_claims"].values():
            self.assertEqual(value, "not_made")

    def test_category_is_eng_03_only(self) -> None:
        self.assertNotIn("categories", self.report)
        self.assertNotIn("category_scope", self.report)
        self.assertEqual(self.report["map"]["category_id"], "ENG-03")
        for forbidden in ("ENG-01", "ENG-02", "ENG-04", "categories"):
            self.assertNotIn(forbidden, self.report["map"])
        self.assertEqual(self.report["catalogue"]["category"]["id"], "ENG-03")
        self.assertEqual(self.report["catalogue"]["category"]["name"],
                         "Jitter buffering and adaptive playout")

    def test_catalogue_matches_registry_companion_and_backlog(self) -> None:
        categories = reference._index_by_id(self.registry["categories"],
                                            "categories")
        row = categories["ENG-03"]
        entry = None
        for item in self.backlog["entries"]:
            if item.get("category_id") == "ENG-03":
                entry = item
                break
        self.assertIsNotNone(entry)
        catalogue = self.report["catalogue"]
        self.assertEqual(catalogue["category"], row)
        self.assertEqual(catalogue["legacy_backlog_entry"], entry)
        self.assertEqual(catalogue["legacy_backlog_snapshot"],
                         self.backlog["snapshot"])
        self.assertEqual(catalogue["taxonomy_revision"],
                         self.registry["taxonomy_revision"])
        self.assertIn("| **ENG-03 — Jitter buffering and adaptive playout**",
                      catalogue["companion_row"])
        self.assertIn("Adaptive buffers; acceleration/deceleration; "
                      "PLC integration", catalogue["companion_row"])

    def test_method_families_cover_classic_and_ml(self) -> None:
        families = self.report["map"]["method_families"]
        self.assertEqual(set(families), {"classic", "ml"})
        entries = families["classic"]["entries"]
        self.assertEqual([entry["family"] for entry in entries],
                         ["Adaptive buffers",
                          "Acceleration/deceleration", "PLC integration"])
        self.assertEqual(families["classic"]["catalogued_text"],
                         "Adaptive buffers; acceleration/deceleration; "
                         "PLC integration")
        for entry in entries:
            self.assertTrue(entry["component_ids"], entry["family"])
            self.assertTrue(entry["comparison_inputs"], entry["family"])
            self.assertTrue(entry["controls"], entry["family"])
            self.assertTrue(entry["assets"], entry["family"])
            self.assertTrue(entry["local_outcomes"], entry["family"])
            self.assertTrue(entry["reported_outcomes"], entry["family"])
            self.assertTrue(entry["limits"], entry["family"])
            for outcome in entry["local_outcomes"]:
                self.assertIn(outcome["status"],
                              {"local_historical",
                               "local_historical_synthetic",
                               "local_historical_model"})
                self.assertTrue(outcome["finding"])
                self.assertTrue(outcome["pin"])
        ml = families["ml"]
        self.assertEqual(ml["catalogued_text"], "No ML requirement")
        self.assertIs(ml["audited"], True)
        self.assertEqual(ml["result"], "no_ml_family_catalogued")
        self.assertTrue(ml["missing_evidence"])

    def test_components_and_adjacent_speed_controls_are_separate(self) -> None:
        payload = self.report["map"]
        components = {item["component_id"]: item
                      for item in payload["component_matches"]}
        for required in ("buffer-occupancy-controller", "webrtc-neteq",
                         "rubber-band-r3-offline",
                         "rubber-band-r3-streaming", "ffmpeg-atempo",
                         "linear-interpolation-plc",
                         "pitch-period-repeat-plc", "zero-fill-plc",
                         "opus-1-4-standard-decoder-plc"):
            self.assertIn(required, components)
        self.assertIn("elastic-pcm-packets",
                      {item["component_id"]
                       for item in payload["foundation_matches"]})
        adjacent = payload["adjacent_speed_controls"]
        self.assertTrue(adjacent)
        for item in adjacent:
            self.assertIs(item["counted_as_jitter_buffer"], False)
            self.assertIs(item["counted_as_adaptive_playout"], False)
            self.assertEqual(item["relationship"],
                             "adjacent_user_selected_speed_control")
        for item in components.values():
            self.assertIs(item["qualifies_candidate"], False)

    def test_follow_ups_are_board_linked_and_not_invented(self) -> None:
        for task_id in reference.FOLLOW_UP_POLICY[
                "existing_feasibility_task_ids"]:
            self.assertEqual(self.tasks[task_id]["mode"], "feasibility")
        seen_gaps = set()
        for gap in self.report["map"]["gaps"]:
            self.assertNotIn(gap["id"], seen_gaps)
            seen_gaps.add(gap["id"])
            self.assertIs(gap["invented"], False)
            self.assertIs(gap["actionable"], True)
            task_id = gap["follow_up_task_id"]
            if task_id is None:
                self.assertTrue(gap["no_task_reason"])
                self.assertEqual(gap["follow_up_status_observed"],
                                 "no_board_task")
            else:
                self.assertEqual(self.tasks[task_id]["mode"], "feasibility")
                self.assertEqual(gap["follow_up_mode"], "feasibility")
                self.assertEqual(
                    gap["follow_up_status_observed"],
                    reference.BOARD_STATUS_SNAPSHOT[task_id])
        self.assertTrue(seen_gaps)

    def test_all_gates_blocked(self) -> None:
        self.assertEqual([gate["name"] for gate in self.report["gates"]],
                         [name for name, _ in reference.GATES])
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])

    def test_map_matches_pinned_inputs(self) -> None:
        expected = reference.build_map(
            reference._catalogue(), self.inventory, self.board)
        self.assertEqual(reference.canonical_bytes(self.report["map"]),
                         reference.canonical_bytes(expected))

    def test_adverse_cases_reject_without_state_change(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["state_unchanged"])
        self.assertTrue(adverse["valid_map_accepted"])
        for name, case in adverse["cases"].items():
            self.assertEqual(case["status"], "rejected", name)
            self.assertTrue(case["state_unchanged"], name)
            self.assertTrue(case["reason"], name)
        state = reference.MapState(
            reference.core_report()["map"], self.tasks)
        before = state.digest()
        invalid = [
            b'{"category_id":"ENG-03","category_id":"ENG-03"}',
            b'{"category_id":"ENG-03","x":NaN}',
            b'{"category_id":"ENG-03","x":Infinity}',
            reference.canonical_bytes({"category_id": "ENG-01"}),
        ]
        for raw in invalid:
            with self.assertRaises(reference.Rejected):
                state.apply(raw)
            self.assertEqual(state.digest(), before)
        accepted = state.apply(reference.canonical_bytes(
            reference.core_report()["map"]))
        self.assertEqual(accepted["status"], "accepted")

    def test_canonical_report_and_digest_sidecar(self) -> None:
        raw = (HERE / "report.json").read_bytes()
        self.assertEqual(raw, reference.canonical_report_bytes(self.report))
        self.assertEqual((HERE / "report.json.sha256").read_bytes(),
                         f"{reference.sha256(raw)}  report.json\n".encode(
                             "ascii"))
        contract = reference.strict_json_path(HERE / "contract.json")
        self.assertEqual(self.report["contract_sha256"],
                         reference.sha256(
                             (HERE / "contract.json").read_bytes()))
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertEqual(contract["category_scope"]["category_id"], "ENG-03")

    def test_sources_manifest_is_deterministic(self) -> None:
        raw = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(raw, reference.sources_bytes())
        lines = [line for line in raw.decode("ascii").splitlines()
                 if line and not line.startswith("#")]
        self.assertEqual(len(lines),
                         len(reference.SOURCE_PINS)
                         + len(reference.BOUNDARY_PINS)
                         + len(reference.LOCAL_PIN_PATHS))
        self.assertEqual(len({line.split("  ", 1)[1] for line in lines}),
                         len(lines))

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
