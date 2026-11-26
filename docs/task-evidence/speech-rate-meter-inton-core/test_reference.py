# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the SDK-SPEECH-RATE-METER-INTON-CORE blocker package."""

from __future__ import annotations

import hashlib
import json
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
SIDECAR_FILES = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)


def load_strict(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=lambda pairs: {k: v for k, v in pairs})


class TestReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.contract = reference.contract_payload()

    def test_board_digest_stable(self):
        self.assertEqual(reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)

    def test_decision_status(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_blocked_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")

    def test_gates_blocked(self):
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertEqual(len(self.contract["gates"]), 8)
        for gate in self.report["gates"] + self.contract["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])

    def test_no_missing_promoted(self):
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertTrue(self.report["qualification"]["not_qualified"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_boundary_false(self):
        for k, v in self.report["boundary"].items():
            self.assertFalse(v, k)
        for k, v in self.report["scope"].items():
            if k == "write_scope":
                continue
            self.assertTrue(v is False or v is True)
            if isinstance(v, bool) and k != "task_local_only":
                self.assertFalse(v, k)
        self.assertTrue(self.report["scope"]["task_local_only"])

    def test_upstream_unverified(self):
        up = self.report["upstream"]
        self.assertIsNone(up["commit"])
        self.assertFalse(up["source_present"])
        self.assertEqual(up["license_status"], "reported_unverified")

    def test_surrogate_not_qualified(self):
        run = self.report["controls"]["surrogate_run"]
        self.assertFalse(run["qualified"])
        self.assertTrue(run["surrogate"])
        self.assertFalse(self.report["controls"]["adverse"]["valid_control"]["qualified"])

    def test_adverse_rejections(self):
        adv = self.report["controls"]["adverse"]
        for name in ("missing_config_key", "bad_geometry", "nan", "inf", "bool", "out_of_range", "wrong_length", "bad_frames_container"):
            self.assertTrue(adv[name]["rejected"], name)
        asset = self.report["controls"]["asset"]
        for name in ("missing_field", "unknown_field", "nonfinite", "float_field", "bad_sha", "missing_path", "relative_path", "bad_geometry"):
            self.assertTrue(asset[name]["rejected"], name)
        self.assertEqual(asset["schema_control"]["accepted"], False)
        self.assertTrue(asset["schema_control"]["validated_identity_only"])

    def test_report_determinism(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        c = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(b, c)

    def test_contract_determinism(self):
        self.assertEqual(reference.contract_bytes(), reference.contract_bytes())

    def test_negative_zero(self):
        self.assertFalse(reference.has_negative_zero(self.report))
        self.assertFalse(reference.has_negative_zero(self.contract))

    def test_strict_parsers(self):
        res = reference.strict_rejection_examples()
        self.assertEqual(res["bad_json_rejected"], res["bad_json_total"])
        self.assertEqual(res["bad_pins_rejected"], res["bad_pins_total"])
        self.assertEqual(res["bad_readme_rejected"], res["bad_readme_total"])

    def test_sidecars(self):
        for name in SIDECAR_FILES:
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), SIDECAR)

    def test_spdx_headers(self):
        for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
            head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_C, head)
            self.assertIn(SPDX_L, head)
        md = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn("<!-- " + SPDX_C + " -->", md)
        self.assertIn("<!-- " + SPDX_L + " -->", md)

    def test_no_forbidden_tokens(self):
        token = "SPDX-License" + "-Identifier: Apache-2.0"
        allowed = '"SPDX-License-" "Identifier: Apache-2.0"'
        for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            # header lines are allowed; flag contiguous token elsewhere
            lines = text.splitlines()
            body = "\n".join(lines[2:])
            self.assertNotIn(token, body.replace(allowed, ""))

    def test_report_sidecar_digest(self):
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="ascii"), f"{digest}  report.json\n")

    def test_readme_tables(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertGreaterEqual(counts["source"], 4)
        self.assertGreaterEqual(counts["boundary"], 9)
        self.assertGreaterEqual(counts["artifacts"], 8)

    def test_pins_cover_local_files(self):
        allowed = reference.allowed_pin_keys()
        for name in reference._local_manifest_paths():
            self.assertIn(reference.TASK_PREFIX + name, allowed)

    def test_task_identity(self):
        self.assertEqual(self.report["task_id"], reference.TASK)
        self.assertEqual(self.report["component_id"], reference.COMPONENT)
        self.assertEqual(self.report["profile"], "rate")

    def test_verify_script_runs(self):
        result = subprocess.run([sys.executable, str(HERE / "verify.py")], cwd=str(HERE.parents[2]), capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
