# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest acceptance suite for the TRN-01 category evidence map."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_json_keys_rejected(self) -> None:
        with self.assertRaises(reference.ValidationError) as caught:
            reference.strict_json_text('{"decision":"DEFER","decision":"ALLOW"}')
        self.assertIn("duplicate_json_key:decision", str(caught.exception))

    def test_nonfinite_json_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(reference.ValidationError) as caught:
                    reference.strict_json_text('{"value":' + token + '}')
                self.assertIn("nonfinite_json_constant", str(caught.exception))

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(reference.ValidationError):
            reference.strict_json_text("[1,2,3]")

    def test_canonical_bytes_are_sorted_and_finite(self) -> None:
        first = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        second = reference.canonical_bytes({"a": [2, 3], "b": 1})
        self.assertEqual(first, second)
        self.assertEqual(first, b'{"a":[2,3],"b":1}')
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"bad": float("nan")})


class PinTests(unittest.TestCase):
    def test_source_pins_match_pinned_bytes(self) -> None:
        reference.verify_pins()

    def test_evidence_pins_match_pinned_bytes(self) -> None:
        for relative, digest in reference.EVIDENCE_PINS.items():
            path = reference.SDK_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_boundary_pins_match_pinned_bytes(self) -> None:
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_pin_line_validation_rejects_stale_and_unknown(self) -> None:
        allowed = {}
        for path, digest in reference.SOURCE_PINS.items():
            allowed["source:" + path] = digest
        good = next(iter(allowed.items()))
        key, digest = reference.verify_pin_line(f"{good[1]}  {good[0]}", allowed)
        self.assertEqual((key, digest), good)
        with self.assertRaises(reference.ValidationError):
            reference.verify_pin_line("0" * 64 + "  source:not-pinned", allowed)
        with self.assertRaises(reference.ValidationError):
            reference.verify_pin_line("zz" + "0" * 62 + "  source:" + good[0].split(":", 1)[1],
                                      allowed)

    def test_board_snapshot_is_pinned_and_strict(self) -> None:
        path = HERE / reference.BOARD_SNAPSHOT
        self.assertTrue(path.is_file())
        self.assertEqual(reference.sha256(path.read_bytes()),
                         reference.BOARD_SNAPSHOT_SHA256)
        snapshot = reference.strict_json(path)
        self.assertEqual(snapshot["source_sha256"],
                         reference.BOARD_SNAPSHOT_SOURCE_SHA256)
        self.assertGreaterEqual(len(snapshot["tasks"]), 1)

    def test_sources_manifest_is_deterministic(self) -> None:
        first = reference.sources_bytes()
        second = reference.sources_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.startswith(b"# SHA-256 pins for SDK-SURVEY-TRN-01."))
        for path in reference.LOCAL_PIN_PATHS:
            self.assertIn((reference.TASK_PREFIX + path).encode("ascii"), first)


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = reference.load_inputs()
        cls.state = reference.state_snapshot(cls.inputs)

    def test_category_crosscheck_is_identical(self) -> None:
        crosscheck = reference.category_crosscheck(self.inputs)
        self.assertTrue(crosscheck["identical"])
        self.assertEqual(crosscheck["task"], reference.TASK)
        self.assertEqual(crosscheck["inventory"]["source_ids"], ["S32", "S33", "S51"])

    def test_family_map_covers_all_curated_components(self) -> None:
        families = reference.family_map(self.inputs)
        self.assertEqual([item["id"] for item in families],
                         [item["id"] for item in reference.FAMILIES])
        mapped = set()
        for family in families:
            mapped.update(item["component_id"] for item in family["components"])
        for lead in reference.source_lead_map(self.inputs):
            mapped.update(lead["mapped_component_ids"])
        self.assertEqual(mapped, set(reference.mapped_component_ids()))
        self.assertTrue(self.inputs["components"])

    def test_source_leads_are_pinned_text_only(self) -> None:
        leads = reference.source_lead_map(self.inputs)
        self.assertEqual([item["source_id"] for item in leads], ["S32", "S33", "S51"])
        for lead in leads:
            self.assertFalse(lead["url_fetched"])
            self.assertEqual(lead["classification"], "source_text_only_not_reproduced")

    def test_every_gap_links_to_existing_feasibility_task(self) -> None:
        gaps = reference.gap_map(self.inputs)
        self.assertEqual(len(gaps), len(reference.GAPS))
        for gap in gaps:
            self.assertEqual(gap["followup_mode"], "feasibility")
            self.assertTrue(gap["linked_on_board"])
            self.assertFalse(gap["new_task_created"])
            self.assertIn(gap["followup_task_id"], self.inputs["tasks"])

    def test_valid_payload_is_accepted_without_state_change(self) -> None:
        payload = reference.validation_payload()
        before = reference.state_digest(self.state)
        self.assertEqual(reference.validate_map(payload, self.state), [])
        self.assertEqual(reference.state_digest(self.state), before)

    def test_forbidden_claims_and_open_gates_are_rejected(self) -> None:
        base = reference.validation_payload()
        before = reference.state_digest(self.state)
        with_scope = copy.deepcopy(base)
        with_scope["scope"]["release_claim"] = True
        self.assertIn("forbidden_scope_claim:release_claim",
                      reference.validate_map(with_scope, self.state))
        with_boundary = copy.deepcopy(base)
        with_boundary["boundary"]["registered"] = True
        self.assertIn("boundary_claim_not_false:registered",
                      reference.validate_map(with_boundary, self.state))
        with_gates = copy.deepcopy(base)
        with_gates["gates"][0]["status"] = "open"
        self.assertIn("release_gate_not_blocked",
                      reference.validate_map(with_gates, self.state))
        self.assertEqual(reference.state_digest(self.state), before)

    def test_nonfeasibility_followup_link_is_rejected(self) -> None:
        payload = copy.deepcopy(reference.validation_payload())
        payload["gaps"][0]["followup_task_id"] = "SDK-FND-AUDIT"
        errors = reference.validate_map(payload, self.state)
        self.assertIn("followup_not_feasibility:SDK-FND-AUDIT", errors)

    def test_adverse_cases_are_rejected_with_state_unchanged(self) -> None:
        result = reference.adverse(self.state)
        self.assertTrue(result["all_rejected"])
        self.assertTrue(result["all_state_unchanged"])
        self.assertEqual(result["state_sha256"], reference.state_digest(self.state))
        names = {case["name"] for case in result["cases"]}
        self.assertIn("duplicate_json_key", names)
        self.assertIn("nonfinite_nan", names)
        self.assertIn("nonfinite_infinity", names)
        self.assertIn("missing_required_key", names)
        for case in result["cases"]:
            self.assertEqual(case["status"], "rejected", case["name"])
            self.assertTrue(case["state_unchanged"], case["name"])

    def test_core_report_disposition_and_gates(self) -> None:
        report = reference.core_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertEqual(len(report["gates"]), 6)
        self.assertTrue(all(gate["status"] == "blocked" for gate in report["gates"]))

    def test_three_cold_starts_are_byte_identical(self) -> None:
        result = reference.repeatability()
        self.assertEqual(result["count"], 3)
        self.assertTrue(result["byte_identical"])
        self.assertEqual(len(set(result["digests"])), 1)
        for digest in result["digests"]:
            self.assertEqual(len(digest), 64)

    def test_written_report_is_canonical_and_sidecar_matches(self) -> None:
        report_path = HERE / "report.json"
        sidecar_path = HERE / "report.json.sha256"
        self.assertTrue(report_path.is_file())
        self.assertTrue(sidecar_path.is_file())
        raw = report_path.read_bytes()
        self.assertEqual(raw, reference.canonical_report_bytes(reference.strict_json(report_path)))
        self.assertEqual(sidecar_path.read_bytes(),
                         (hashlib.sha256(raw).hexdigest() + "  report.json\n").encode("ascii"))


if __name__ == "__main__":
    unittest.main()
