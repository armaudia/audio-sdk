# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


class TestReference(unittest.TestCase):
    def test_contract_shape(self):
        c = reference.build_contract()
        self.assertEqual(c["task"], reference.TASK)
        self.assertEqual(c["decision"], "DEFER")
        self.assertEqual(c["qualification_status"], "not_qualified")
        self.assertEqual(c["status"], "proposal_only_incomplete")
        self.assertEqual(len(c["gates"]), 5)
        self.assertTrue(all(g["status"] == "blocked" for g in c["gates"]))

    def test_report_shape(self):
        r = reference.build_report()
        self.assertEqual(r["schema_id"], reference.REPORT_SCHEMA)
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["controls"]["missing_result_qualifies"], False)
        self.assertTrue(r["controls"]["adverse_manifest_all_rejected"])

    def test_board_projection_stable(self):
        p = reference.board_row_projection()
        self.assertEqual(tuple(p.keys()), reference.BOARD_ROW_FIELDS)
        self.assertEqual(p["id"], reference.TASK)
        self.assertEqual(p["component"], reference.COMPONENT)

    def test_absence_probes(self):
        rows = reference.absence_rows()
        self.assertGreaterEqual(len(rows), 10)
        self.assertTrue(all("present" in r for r in rows))

    def test_manifest_accepts_control(self):
        a = reference.validate_manifest({
            "schema_id": reference.MANIFEST_SCHEMA,
            "candidate": reference.COMPONENT,
            "language": "en",
            "transcript_normalization": "norm",
            "aligned_subset_id": "subset",
            "whisper": {"model":"tiny.en","package":"openai-whisper==20250625","weight_sha256":"d"*64,"license":"MIT"},
            "mfa": {"version":"3.4.3","acoustic_model":"english_us_arpa","dictionary":"english_us_arpa","acoustic_sha256":"a"*64,"dictionary_sha256":"b"*64,"license":"CC-BY-4.0"},
            "cohort": {"id":"c","audio_sha256":"c"*64,"annotation_sha256":"e"*64,"sample_rate_hz":16000,"channels":1,"sample_count":1},
            "rights_reviewed": True,
            "claims_qualified": False,
        })
        self.assertTrue(a["accepted"])
        self.assertFalse(a["qualifies"])

    def test_adverse_manifest_cases_rejected(self):
        cases = reference.adverse_manifest_results()
        self.assertGreaterEqual(len(cases), 12)
        self.assertTrue(all(c["rejected"] for c in cases))

    def test_strict_json_rejects_duplicate(self):
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_nan(self):
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":NaN}')

    def test_scope_function(self):
        scope = reference.check_scope()
        self.assertIn(scope["status"], {"ok","scope_base_unavailable"})
        self.assertIn("violations", scope)

    def test_canonical_deterministic(self):
        c = reference.build_contract()
        self.assertEqual(reference.canonical_bytes(c), reference.canonical_bytes(json.loads(reference.canonical_text(c))))


if __name__ == "__main__":
    unittest.main()
