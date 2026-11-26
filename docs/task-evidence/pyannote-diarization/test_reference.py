# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-PYANNOTE-DIARIZATION evidence package."""

from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_rejects_nonfinite_constants(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"a":' + token + "}")

    def test_rejects_trailing_data_bom_and_non_object(self) -> None:
        for payload in ('{"a":1}x', '\ufeff{"a":1}', "[1,2]", "  "):
            with self.assertRaises(ValueError):
                reference.loads_strict(payload)

    def test_canonical_roundtrip_and_digest(self) -> None:
        document = {"b": [1, True, None], "a": {"z": "x"}}
        payload = reference.canonical_bytes(document)
        self.assertEqual(payload, b'{"a":{"z":"x"},"b":[1,true,null]}')
        self.assertEqual(reference.object_digest(document), hashlib.sha256(payload).hexdigest())

    def test_rejects_floats_in_canonical_evidence(self) -> None:
        with self.assertRaises(TypeError):
            reference._reject_floats({"value": 0.5})


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_boundary_pins_match(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_evidence_snippets_are_present(self) -> None:
        result = reference.evidence_snippet_check()
        self.assertTrue(result["all_present"], result["checks"])

    def test_linked_row_identity_only(self) -> None:
        boundary = reference.boundary_block()
        self.assertFalse(boundary["board_file_pinned"])
        self.assertTrue(boundary["linked_row_identity_only"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertNotIn("status", boundary["linked_row"])
        self.assertEqual(boundary["linked_row_sha256"], reference.board_row_digest(boundary["linked_row"]))


class AbsenceTests(unittest.TestCase):
    def test_all_candidate_artifacts_are_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_absent"])

    def test_no_runtime_is_available(self) -> None:
        readiness = reference.runtime_readiness()
        self.assertFalse(readiness["runtime_present"])
        self.assertFalse(readiness["runtime_pinned"])
        self.assertFalse(readiness["any_module_available"])


class EnvelopeTests(unittest.TestCase):
    def test_envelope_cases_are_deterministic(self) -> None:
        a = reference.protocol_envelope()
        b = reference.protocol_envelope()
        self.assertEqual(a, b)
        self.assertEqual(a["case_count"], 4)
        self.assertTrue(all(case["accepted"] for case in a["cases"]))
        self.assertTrue(all(case["anonymous_only"] for case in a["cases"]))

    def test_valid_manifest_is_accepted(self) -> None:
        accepted = reference.validate_manifest(reference.envelope_manifest("two_speakers"))
        self.assertEqual(accepted["segment_count"], 2)
        self.assertFalse(accepted["overlap_allowed"])
        self.assertFalse(accepted["qualified"])

    def test_overlap_case_is_marked(self) -> None:
        accepted = reference.validate_manifest(reference.envelope_manifest("overlap"))
        self.assertTrue(accepted["overlap_allowed"])


class AdmissionTests(unittest.TestCase):
    def test_candidate_claim_is_rejected(self) -> None:
        manifest = reference.envelope_manifest("single_speaker")
        manifest["candidate"]["weights_present"] = True
        with self.assertRaises(reference.AdmissionError) as caught:
            reference.validate_manifest(manifest)
        self.assertEqual(caught.exception.code, "weights_present_must_be_false")

    def test_mutation_suite_rejects_every_case(self) -> None:
        result = reference.admission_rejections()
        self.assertGreaterEqual(result["cases"], 40)
        self.assertTrue(result["all_rejected"], result["rejections"])

    def test_strict_json_suite_rejects_every_case(self) -> None:
        result = reference.strict_json_rejections()
        self.assertEqual(result["cases"], 9)
        self.assertTrue(result["all_rejected"])

    def test_no_mutable_controller_state_after_rejection(self) -> None:
        manifest = reference.envelope_manifest("two_speakers")
        before = copy.deepcopy(manifest)
        manifest["timeline"]["segment_count"] = 1
        with self.assertRaises(reference.AdmissionError):
            reference.validate_manifest(manifest)
        self.assertEqual(reference.validate_manifest(before)["segment_count"], 2)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_state(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"], "not_qualified")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(len(self.contract["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in self.contract["release_gates"]))

    def test_report_state(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["qualification"]["not_qualified"])
        self.assertTrue(self.report["qualification"]["all_release_gates_blocked"])
        self.assertEqual(len(self.report["gates"]), 8)

    def test_canonical_report_is_stable(self) -> None:
        a, da = reference.canonical_report(self.report)
        b, db = reference.canonical_report(self.report)
        self.assertEqual(a, b)
        self.assertEqual(da, db)
        self.assertEqual(len(da), 64)


if __name__ == "__main__":
    unittest.main()
