# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for rate-controlled HiFi-GAN speech TSM evidence.

No network, no downloads, no weights, no skips. Every check runs against the
synthetic boundary surrogate only; nothing here qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_GATES = {
    "exact_asset_identity",
    "runtime_admission",
    "artifact_rights",
    "exact_reference_parity",
    "rights_cleared_rate_cohort",
    "independent_scoring_and_listening",
    "target_runtime_timing",
    "provider_intake_and_default_selection",
}


def _no_duplicates(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise ValueError("duplicate key: " + k)
        seen.add(k)
    return dict(pairs)


def load_strict(name: str):
    return json.loads((HERE / name).read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)


class TestCanonical(unittest.TestCase):
    def test_canonical_sorted(self):
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_negative_zero(self):
        self.assertEqual(reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}')

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference.canonical_bytes({"x": bad})


class TestReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()

    def test_decision_status(self):
        r = self.report
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "proposal_only_incomplete")
        self.assertEqual(r["evidence_status"], "incomplete")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertEqual(r["release_gate_count"], 8)
        self.assertEqual(r["release_gates_blocked"], 8)

    def test_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual({g["name"] for g in gates}, EXPECTED_GATES)
        for g in gates:
            self.assertEqual(g["status"], "blocked")
            self.assertTrue(g["evidence"])
            self.assertTrue(g["reopen"])

    def test_contract_gates_blocked(self):
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual({g["name"] for g in gates}, EXPECTED_GATES)
        for g in gates:
            self.assertEqual(g["status"], "blocked")

    def test_claims_false(self):
        for k, v in self.report["claims"].items():
            self.assertIs(v, False, k)
        for k, v in self.report["boundary"].items():
            if k == "installed_v0_geometry_preserved":
                self.assertIs(v, True)
            else:
                self.assertIs(v, False, k)

    def test_no_asset_bytes(self):
        a = self.report["asset"]
        self.assertIsNone(a["byte_count"])
        self.assertIsNone(a["sha256"])
        self.assertFalse(a["pinned"])
        self.assertFalse(a["asset_bytes_read"])
        self.assertFalse(a["digest_recomputed"])
        self.assertFalse(any(a["workspace_probes"].values()))

    def test_absence(self):
        self.assertTrue(self.report["absence_audit"]["all_absence_probes_absent"])
        self.assertFalse(self.report["absence_audit"]["download_performed"])

    def test_admission_blocked(self):
        adm = self.report["asset_admission"]
        self.assertEqual(adm["status"], "blocked")
        self.assertTrue(adm["reason_codes"])
        self.assertEqual(adm["qualification_effect"], "none")
        syn = self.report["synthetic_admission_control"]
        self.assertEqual(syn["status"], "admitted_synthetic_control")
        self.assertFalse(syn["candidate_asset"])
        self.assertEqual(syn["qualification_effect"], "none")

    def test_board_not_hashed(self):
        ident = self.report["task_identity"]
        self.assertFalse(ident["board_full_file_hashed"])
        self.assertIn("mutable_fields_excluded", ident)
        self.assertNotIn("status", ident)
        self.assertEqual(self.contract["board_policy"]["full_file_hashed"], False)


class TestSurrogate(unittest.TestCase):
    def test_deterministic_controls(self):
        controls = reference.synthetic_control_checks()
        for key, c in controls.items():
            self.assertTrue(c["deterministic"], key)
            self.assertTrue(c["chunk_matches_stream"], key)
            self.assertTrue(c["all_ok"], key)

    def test_rate_profile_rows(self):
        rp = reference.build_report()["rate_profile"]
        self.assertEqual(rp["profile"], "rate")
        self.assertTrue(rp["profile_applied"])
        self.assertFalse(rp["source_output_mapping_present"])
        self.assertFalse(rp["duration_measured_on_candidate"])
        self.assertEqual(len(rp["synthetic_rows"]), 20)
        for row in rp["synthetic_rows"]:
            self.assertFalse(row["qualifies_candidate"])
            self.assertTrue(row["synthetic_surrogate_only"])

    def test_adverse(self):
        adv = reference.adverse_cases()
        for k, v in adv["asset_metadata_cases"].items():
            self.assertIn(v["status"], {"rejected", "admitted_synthetic_control"}, k)
        self.assertEqual(adv["opt_in_cases"]["surrogate_without_opt_in"]["status"], "rejected")
        for k, v in adv["stream_cases"].items():
            self.assertTrue(str(v["status"]).startswith("rejected:"), k)


class TestFiles(unittest.TestCase):
    def test_sidecars(self):
        for name in SIDECAR_FILES:
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), SIDECAR)

    def test_spdx_headers(self):
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
            self.assertEqual(head, ["# " + SPDX_C, "# " + SPDX_L])
        md = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
        self.assertEqual(md, ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"])

    def test_no_forbidden_tokens(self):
        tokens = ("import " + "requests", "import " + "urllib", "import " + "socket", "url" + "open")
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for t in tokens:
                self.assertNotIn(t, text)

    def test_report_sidecar(self):
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_canonical_regen(self):
        self.assertEqual(cli.report_bytes(), (HERE / "report.json").read_bytes())
        self.assertEqual(cli.contract_bytes(cli.contract_pins()), (HERE / "contract.json").read_bytes())
        self.assertEqual(cli.manifest_bytes(), (HERE / "SOURCES.sha256").read_bytes())


if __name__ == "__main__":
    unittest.main()
