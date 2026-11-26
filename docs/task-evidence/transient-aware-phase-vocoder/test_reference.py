# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for transient-aware-phase-vocoder evidence."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class RefTest(unittest.TestCase):
    def test_canonical_stable(self):
        a, da = reference.canonical_report()
        b, db = reference.canonical_report()
        self.assertEqual(a, b)
        self.assertEqual(da, db)
        self.assertEqual(len(da), 64)

    def test_contract_report(self):
        c = reference.build_contract()
        r = reference.build_report()
        self.assertEqual(c["decision"], reference.DECISION)
        self.assertEqual(r["decision"], reference.DECISION)
        self.assertEqual(r["qualification_status"], reference.QUALIFICATION)
        self.assertTrue(r["proposal_only"])
        self.assertTrue(r["incomplete"])
        self.assertEqual(r["contract_sha256"], reference.object_digest(c))

    def test_gates_blockers(self):
        r = reference.build_report()
        self.assertEqual([g["id"] for g in r["release_gates"]], [f"RG-{i:02d}" for i in range(1, 9)])
        self.assertEqual([b["id"] for b in r["exact_blockers"]], [f"BLK-{i:02d}" for i in range(1, 6)])
        for g in r["release_gates"]:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
        for b in r["exact_blockers"]:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])

    def test_absence(self):
        a = reference.absence_probes()
        self.assertTrue(a["all_absent"])
        self.assertEqual(a["present_count"], 0)

    def test_declaration(self):
        s = reference.asset_declaration_schema()
        self.assertTrue(s["all_rejected"])
        self.assertTrue(s["strict_json_all_rejected"])
        reference.validate_asset_declaration(reference.unpopulated_asset_declaration())
        bad = reference.unpopulated_asset_declaration()
        bad["source"]["declared_present"] = True
        with self.assertRaises(ValueError):
            reference.validate_asset_declaration(bad)

    def test_scope(self):
        base, paths = reference.committed_paths_since_base(reference.SDK_ROOT)
        self.assertTrue(base is None or isinstance(base, str))
        self.assertIsInstance(paths, list)

    def test_strict_json(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_run_regen(self):
        with tempfile.TemporaryDirectory(prefix="tapv-test-") as tmp:
            td = Path(tmp) / HERE.name
            import shutil
            shutil.copytree(HERE, td)
            proc = subprocess.run([sys.executable, str(td / "run.py"), "all"], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("byte_identical=true", proc.stdout)
            for name in sorted(reference.EXPECTED_DIR_FILES):
                self.assertEqual((HERE / name).read_bytes(), (td / name).read_bytes(), name)


if __name__ == "__main__":
    unittest.main()
