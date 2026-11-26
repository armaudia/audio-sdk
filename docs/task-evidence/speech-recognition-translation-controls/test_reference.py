# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib tests for speech-recognition-translation-controls DEFER evidence.

No network, no ASR/translation runtime/model/audio, no device timing, no listening.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import reference
import run

SPDX_ID = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPY = "SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan"
REQUIRED_FILES = [
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
]


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":1,"a":2}')

    def test_rejects_nan_inf(self) -> None:
        for token in ["NaN", "Infinity", "-Infinity"]:
            with self.assertRaises(Exception):
                reference.strict_loads(token)

    def test_canonical_bytes_stable(self) -> None:
        obj = {"b": 1, "a": [2, 3], "c": {"y": False, "x": None}}
        b1 = reference.canonical_bytes(obj)
        b2 = reference.canonical_bytes(copy.deepcopy(obj))
        self.assertEqual(b1, b2)
        self.assertTrue(b1.endswith(b"\n"))


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.report_bytes = reference.report_bytes()
        cls.sidecar = reference.sidecar_bytes(cls.report_bytes)
        cls.contract = reference.build_contract(cls.report, cls.report_bytes, cls.sidecar, b"")

    def test_decision_status(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([g["id"] for g in gates], [f"RG-0{i}" for i in range(1, 9)])
        for g in gates:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
            self.assertTrue(g["reopen_condition"])
            self.assertEqual(g["linked_row"], reference.TASK_ID)
        self.assertEqual(self.contract["gates"], gates)

    def test_exact_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 4)
        for b in blockers:
            self.assertTrue(b["id"].startswith("XB-"))
            self.assertTrue(b["detail"])
            self.assertTrue(b["reopen"])

    def test_negative_claims_and_scope(self) -> None:
        self.assertGreaterEqual(len(self.report["negative_claims"]), 5)
        for k, v in self.report["boundary"].items():
            if k == "format":
                continue
            self.assertFalse(v, k)
        self.assertTrue(self.report["scope"]["task_local_only"])
        self.assertTrue(self.report["scope"]["synthetic_only"])
        for k in ("benchmark", "device_timing", "listening", "model_executed", "network_used", "provider_registered", "real_audio", "asr_runtime_loaded"):
            self.assertFalse(self.report["scope"][k], k)

    def test_evidence_classes(self) -> None:
        ec = self.report["evidence_classes"]
        for k in ("real_local_model_output", "real_audio", "source_reported", "listening", "device_timing", "benchmark"):
            self.assertFalse(ec[k], k)
        self.assertTrue(ec["synthetic"])

    def test_board_inventory_links_stable(self) -> None:
        bl = self.report["board_link"]
        il = self.report["inventory_link"]
        self.assertFalse(bl["full_tasks_json_hashed"])
        self.assertFalse(il["full_inventory_hashed"])
        self.assertEqual(bl["stable_sha256"], reference.BOARD_STABLE_SHA256)
        self.assertEqual(il["stable_sha256"], reference.INVENTORY_STABLE_SHA256)
        for f in reference.MUTABLE_FIELDS_EXCLUDED:
            self.assertNotIn(f, bl["stable_fields"])
        self.assertEqual(bl["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(il["stable_fields"]["id"], reference.COMPONENT)

    def test_contract_matches_report_keys(self) -> None:
        for key in ("task_id", "title", "component_id", "repository", "base_commit", "branch", "profile", "decision", "defer_before", "evidence_status", "qualification_status", "status", "format", "boundary", "scope", "gates", "exact_blockers", "negative_claims", "board_link", "inventory_link", "caller_supplied_asset_contract", "asset_ledger"):
            self.assertEqual(self.contract[key], self.report[key], key)

    def test_report_sidecar(self) -> None:
        expected = hashlib.sha256(self.report_bytes).hexdigest() + "  report.json\n"
        self.assertEqual(self.sidecar.decode("utf-8"), expected)

    def test_no_spdx_token_literal_in_python_string_literals(self) -> None:
        # contiguous SPDX-License-Identifier token forbidden in Python string literals;
        # comments may contain it for REUSE/tooling.
        token = "SPDX-" + "License-Identifier:"
        for name in ("reference.py", "run.py", "verify.py"):
            for i, line in enumerate((reference.TASK_DIR / name).read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                self.assertNotIn(token, line, f"{name}:{i}")


class AdverseTests(unittest.TestCase):
    def test_adverse_cases_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "probe.bin"
            p.write_bytes(b"probe-runtime")
            adverse = reference.adverse_cases(p)
        self.assertTrue(adverse["all_rejected"])
        self.assertGreaterEqual(adverse["case_count"], 15)
        self.assertTrue(adverse["invalid_json"]["all_rejected"])
        self.assertTrue(adverse["invalid_pins"]["all_rejected"])
        observed = {c["id"]: c["observed"] for c in adverse["cases"]}
        self.assertEqual(observed["hash_matched_still_unpinned"], "ASR_TRANSLATION_RUNTIME_IDENTITY_UNPINNED")

    def test_synthetic_controls_not_qualifying(self) -> None:
        controls = reference.synthetic_controls()
        self.assertFalse(controls["qualifies_candidate"])
        self.assertTrue(controls["normalization_rejections"]["all_rejected"])


class CanonicalArtifactTests(unittest.TestCase):
    def test_required_files_present(self) -> None:
        for name in REQUIRED_FILES:
            self.assertTrue((reference.TASK_DIR / name).is_file(), name)

    def test_license_sidecars(self) -> None:
        for name in ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"):
            text = (reference.TASK_DIR / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_ID, text)
            self.assertIn(SPDX_COPY, text)

    def test_run_check_passes(self) -> None:
        proc = subprocess.run(["python3", str(reference.TASK_DIR / "run.py"), "--check"], cwd=reference.SDK_ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_regen_3x_byte_identical(self) -> None:
        before = {n: (reference.TASK_DIR / n).read_bytes() for n in ("report.json", "report.json.sha256", "contract.json", "SOURCES.sha256")}
        for _ in range(3):
            proc = subprocess.run(["python3", str(reference.TASK_DIR / "run.py"), "--all"], cwd=reference.SDK_ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            after = {n: (reference.TASK_DIR / n).read_bytes() for n in before}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
