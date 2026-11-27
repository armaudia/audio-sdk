# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-WHISPER-TRANSCRIPTION evidence package."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
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

    def test_rejects_nonfinite_and_float(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"a":' + token + '}')
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1.5}')

    def test_rejects_trailing_bom_non_object(self) -> None:
        for payload in ('{"a":1}x', '\ufeff{"a":1}', '[1]', '  '):
            with self.assertRaises(ValueError):
                reference.loads_strict(payload)

    def test_canonical_digest(self) -> None:
        doc = {"b": [1, True, None], "a": "x"}
        payload = reference.canonical_bytes(doc)
        self.assertEqual(payload, b'{"a":"x","b":[1,true,null]}')
        self.assertEqual(reference.object_digest(doc), hashlib.sha256(payload).hexdigest())


class PinTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        for rel, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / rel
            self.assertTrue(path.is_file(), rel)
            self.assertEqual(reference.sha256_file(path), expected, rel)

    def test_boundary_pins_match(self) -> None:
        for rel, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / rel
            self.assertTrue(path.is_file(), rel)
            self.assertEqual(reference.sha256_file(path), expected, rel)

    def test_evidence_snippets_present(self) -> None:
        result = reference.evidence_snippet_check()
        self.assertTrue(result["all_present"], result["checks"])
        self.assertGreaterEqual(result["count"], 8)


class ReportTests(unittest.TestCase):
    def test_contract_and_report_policy(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report(contract)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertFalse(report["claim_eligible"])
        self.assertFalse(report["release_claim_eligible"])
        self.assertEqual(len(report["gates"]), 5)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in report["gates"]))
        self.assertEqual(len(report["blockers"]), 5)
        self.assertTrue(all(b["status"] == "open" and b["qualifies"] is False for b in report["blockers"]))

    def test_absence_all_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertTrue(summary["all_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertEqual(summary["probe_count"], len(reference.all_probes()))

    def test_linked_row_identity_only(self) -> None:
        row = reference.board_row_projection()
        self.assertEqual(row["id"], reference.TASK)
        self.assertNotIn("status", row)
        self.assertEqual(len(reference.board_row_digest(row)), 64)

    def test_readme_digest_tables(self) -> None:
        readme = (reference.HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(readme)
        self.assertEqual(counts.get("source"), len(reference.SOURCE_PINS))
        self.assertEqual(counts.get("boundary"), len(reference.BOUNDARY_PINS))


class ScopeTests(unittest.TestCase):
    def _git(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)

    def _init_repo(self, root: Path) -> None:
        self._git(root, "init")
        self._git(root, "config", "user.email", "test@example.com")
        self._git(root, "config", "user.name", "Test")
        (root / "README.md").write_text("base\n", encoding="utf-8")
        self._git(root, "add", "README.md")
        self._git(root, "commit", "-m", "base")
        self._git(root, "branch", "-M", "main")

    def test_scope_base_newest_merge_base_and_out_of_scope_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            self._git(root, "checkout", "-b", "feature")
            (root / reference.TASK_PREFIX).mkdir(parents=True)
            (root / reference.TASK_PREFIX / "ok.txt").write_text("ok\n", encoding="utf-8")
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "task")
            self._git(root, "checkout", "main")
            (root / "shared.txt").write_text("main\n", encoding="utf-8")
            self._git(root, "add", "shared.txt")
            self._git(root, "commit", "-m", "main advance")
            self._git(root, "checkout", "feature")
            base = reference.scope_base(root, refs=("main",))
            self.assertIsNotNone(base)
            paths = reference.scope_changed_paths(root, base)
            self.assertEqual(reference.scope_violations(paths), [])

    def test_scope_base_falls_back_to_main(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            base = reference.scope_base(root, refs=("origin/main", "main"))
            self.assertIsNotNone(base)

    def test_scope_base_unavailable_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._init_repo(root)
            base = reference.scope_base(root, refs=("origin/missing", "missing"))
            self.assertIsNone(base)


if __name__ == "__main__":
    unittest.main()
