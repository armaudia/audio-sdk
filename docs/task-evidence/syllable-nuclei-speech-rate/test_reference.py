# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-SYLLABLE-NUCLEI-SPEECH-RATE blocker package."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"


class TestReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.contract = reference.contract_payload()

    def test_board_digest_stable(self):
        self.assertEqual(reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)

    def test_decision_status(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_blocked_incomplete_not_qualified")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["proposal_only"])

    def test_gates_blocked(self):
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertEqual(len(self.contract["gates"]), 8)
        for gate in self.report["gates"] + self.contract["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])

    def test_no_missing_promoted(self):
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_boundary_scope(self):
        for k, v in self.report["boundary"].items():
            if isinstance(v, bool):
                self.assertFalse(v, k)
        self.assertFalse(self.report["scope"]["release_claim"])
        self.assertFalse(self.report["scope"]["device_timing"])
        self.assertFalse(self.report["scope"]["real_audio"])
        self.assertTrue(self.report["scope"]["task_local_only"])

    def test_surrogate_not_qualified(self):
        s = self.report["controls"]["synthetic_surrogate"]
        self.assertTrue(s["surrogate"])
        self.assertFalse(s["qualified"])
        self.assertFalse(s["candidate_is_syllable_nuclei"])

    def test_adverse_all_rejected(self):
        adv = self.report["controls"]["adverse"]
        self.assertTrue(adv["all_rejected"])
        self.assertEqual(adv["rejected_count"], adv["case_count"])

    def test_source_reported_not_promoted(self):
        sr = self.report["candidate_source_reported"]
        self.assertFalse(sr["qualifies"])
        self.assertFalse(sr["reproduced"])

    def test_determinism(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        c = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(b, c)
        self.assertEqual(reference.contract_bytes(), reference.contract_bytes())

    def test_no_negative_zero(self):
        self.assertFalse(reference.has_negative_zero(self.report))
        self.assertFalse(reference.has_negative_zero(self.contract))

    def test_strict_rejections(self):
        res = reference.strict_rejection_examples()
        self.assertEqual(res["bad_json_rejected"], res["bad_json_total"])
        self.assertEqual(res["bad_pins_rejected"], res["bad_pins_total"])
        self.assertEqual(res["bad_readme_rejected"], res["bad_readme_total"])

    def test_sidecars(self):
        for name in reference.LICENSE_SIDECARS:
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), SIDECAR)

    def test_spdx_headers(self):
        for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
            head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_C, head)
            self.assertIn(SPDX_L, head)
        md = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn("<!-- " + SPDX_C + " -->", md)
        self.assertIn("<!-- " + SPDX_L + " -->", md)

    def test_no_contiguous_spdx_in_python_body(self):
        token = "SPDX-License" + "-Identifier: Apache-2.0"
        allowed = '"SPDX-License-" "Identifier: Apache-2.0"'
        for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
            body = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[2:])
            self.assertNotIn(token, body.replace(allowed, ""))

    def test_report_sidecar_digest(self):
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="ascii"), f"{digest}  report.json\n")

    def test_readme_tables(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertGreaterEqual(counts["source"], 5)
        self.assertGreaterEqual(counts["boundary"], 10)
        self.assertGreaterEqual(counts["artifacts"], 10)

    def test_pins_cover_local_files(self):
        allowed = reference.allowed_pin_keys()
        for name in reference.PINNED_LOCAL_FILES:
            self.assertIn(reference.TASK_PREFIX + name, allowed)

    def test_verify_script(self):
        result = subprocess.run([sys.executable, str(HERE / "verify.py")], cwd=str(HERE.parents[2]), capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
