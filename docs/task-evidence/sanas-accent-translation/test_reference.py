# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local unit and scope regression tests for the Sanas evidence package."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StaticEvidenceTests(unittest.TestCase):
    def test_identity_and_interpreter_are_pinned(self) -> None:
        self.assertEqual(reference.TASK, "SDK-SANAS-ACCENT-TRANSLATION")
        self.assertEqual(reference.COMPONENT, "sanas-accent-translation")
        self.assertEqual(reference.MODE, "external-adapter")
        self.assertEqual(reference.BASE_COMMIT,
                         "56eeb134b740d41d770940bf47bd0f035d73f097")
        self.assertEqual(reference.REQUIRED_INTERPRETER, "3.12.16")
        self.assertEqual(reference.TASK_PREFIX,
                         "docs/task-evidence/sanas-accent-translation/")

    def test_strict_json_rejects_duplicate_keys_and_nonfinite(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1,"b":[2]}'),
                         {"a": 1, "b": [2]})
        with self.assertRaises(ValueError):
            reference.strict_json_loads('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.strict_json_loads('{"a":NaN}')

    def test_canonical_report_is_finite_and_byte_stable(self) -> None:
        payload = reference.report_bytes()
        report = reference.strict_json_loads(payload.decode("utf-8"))
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        self.assertEqual(payload, reference.canonical_bytes(report) + b"\n")
        self.assertTrue(reference.finite_json(report))

    def test_profile_and_evidence_rows_are_exact(self) -> None:
        profile = reference.voice_profile_check()
        self.assertTrue(profile["phrases_all_present"])
        self.assertEqual(profile["row"], reference.PROFILE_ROW)
        self.assertEqual(profile["source"], reference.PROFILE_SOURCE)
        entry = reference.evidence_entry()
        self.assertEqual(entry["text"], reference.EVIDENCE_TEXT)
        self.assertEqual(entry["line"], 180)
        self.assertEqual(entry["sha256"],
                         reference.SOURCE_PINS[reference.EVIDENCE_PATH])

    def test_blockers_artifacts_and_gates_fail_closed(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(len(contract["exact_blockers"]), 6)
        self.assertTrue(all(row["status"] == "open"
                            for row in contract["exact_blockers"]))
        self.assertEqual(len(contract["required_artifacts"]), 6)
        self.assertTrue(all(row["present"] is False
                            and row["verified"] is False
                            for row in contract["required_artifacts"]))
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertTrue(all(row["status"] == "blocked"
                            and row["qualifies"] is False
                            for row in contract["release_gates"]))
        self.assertFalse(contract["tool_manifest_reference"]["caller_supplied"])
        self.assertEqual(contract["external_assets"]["declared_count"], 0)

    def test_board_projection_excludes_mutable_fields(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(len(links), 3)
        self.assertEqual(links[0]["id"], reference.TASK)
        self.assertEqual(links[0]["mode"], "external-adapter")
        for row in links:
            self.assertEqual(set(row), set(reference.LINK_FIELDS))
        self.assertEqual(digest, reference.object_digest(links))
        for field in reference.MUTABLE_FIELDS_EXCLUDED:
            self.assertNotIn(field, reference.LINK_FIELDS)

    def test_absence_probes_are_all_absent(self) -> None:
        probes = reference.probe_rows()
        summary = reference.absence_summary(probes)
        self.assertEqual(summary["probe_count"], 14)
        self.assertTrue(summary["all_absent"])
        self.assertFalse(summary["recursive_walk_performed"])

    def test_sources_manifest_has_no_self_pin_and_no_vendor_asset(self) -> None:
        text = reference.sources_bytes().decode("ascii")
        rows = reference.parse_pin_lines(text)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256",
                         {path for _, path in rows})
        self.assertIn(reference.TASK_PREFIX + "README.md",
                      {path for _, path in rows})
        self.assertFalse(any("sanas." in path.lower() and "source:" in path
                             for _, path in rows))


class ReadmeTableTests(unittest.TestCase):
    def test_rendered_tables_round_trip(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        updated = reference.update_readme_tables(text)
        self.assertEqual(text, updated)
        counts = reference.verify_readme_digests(updated)
        expected = reference.expected_readme_keys()
        for section in reference.README_SECTIONS:
            self.assertEqual(counts[section], len(expected[section]))

    def test_stale_digest_is_rejected(self) -> None:
        text = reference.update_readme_tables(
            (HERE / "README.md").read_text(encoding="utf-8"))
        marker = "<!-- digest-table: source -->"
        index = text.index(marker) + len(marker)
        stale = text[:index] + "\n| `source:audio-benchmark-platform/plan/INVENTORY.json` | `" + "0" * 64 + "` |" + text[index:]
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(stale)


class ScopeTests(unittest.TestCase):
    """Three regressions for newest-merge-base branch-diff scope enforcement."""

    def _git(self, repo: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *arguments],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def _repository(self, root: Path) -> Path:
        repo = root / "audio-sdk"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-fixture")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("task", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-q", "-m", "base")
        return repo

    def _commit_task_change(self, repo: Path, label: str) -> None:
        path = repo / reference.TASK_PREFIX / "evidence.txt"
        path.write_text(label, encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-q", "-m", label)

    def test_sibling_merge_excluded_from_newest_merge_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            sibling = repo / "docs/task-evidence/laco-senet/README.md"
            sibling.parent.mkdir(parents=True)
            sibling.write_text("sibling", encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "sibling merge")
            self._git(repo, "checkout", "-q", "-b", "swarm-task")
            self._commit_task_change(repo, "task evidence")
            base = reference.scope_base(repo, ("main",))
            self.assertEqual(base, self._git(repo, "rev-parse", "main"))
            self.assertNotEqual(base, self._git(repo, "rev-parse", "main~1"))
            self.assertEqual(reference.scope_changed_paths(repo, base),
                             [reference.TASK_PREFIX + "evidence.txt"])
            self.assertEqual(reference.scope_violations(
                reference.scope_changed_paths(repo, base)), [])

    def test_out_of_scope_branch_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "checkout", "-q", "-b", "swarm-task")
            self._commit_task_change(repo, "task evidence")
            outside = repo / "docs/task-evidence/other/README.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("outside", encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "outside change")
            base = reference.scope_base(repo, ("main",))
            violations = reference.scope_violations(
                reference.scope_changed_paths(repo, base))
            self.assertEqual(violations,
                             ["docs/task-evidence/other/README.md"])
            self.assertTrue(all(not path.startswith(reference.TASK_PREFIX)
                                for path in violations))
            verifier = (HERE / "verify.py").read_text(encoding="utf-8")
            self.assertIn("base_out_of_scope_change", verifier)

    def test_missing_base_ref_emits_scope_base_unavailable_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "checkout", "-q", "-b", "swarm-task")
            self._commit_task_change(repo, "task evidence")
            self._git(repo, "branch", "-D", "main")
            self.assertIsNone(reference.scope_base(
                repo, ("origin/main", "main")))
            self.assertIsNone(reference.git_commit(repo, "origin/main"))
            verifier = (HERE / "verify.py").read_text(encoding="utf-8")
            self.assertIn("scope_base_unavailable", verifier)


if __name__ == "__main__":
    unittest.main()
