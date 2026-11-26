# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic regression tests for spectrum-copy BWE DEFER evidence."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

import reference


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _commit(repo: Path, rel: str, content: str, msg: str) -> str:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


class TestCanonical(unittest.TestCase):
    def test_report_repeatable(self) -> None:
        first = reference.report_bytes()
        self.assertEqual(first, reference.report_bytes())
        self.assertTrue(first.endswith(b"\n"))
        report = reference.strict_loads(first.decode("utf-8"))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["adverse"]["all_rejected"])
        self.assertFalse(report["evidence_classes"]["real_local_model_output"])

    def test_contract_and_sidecar(self) -> None:
        report_payload = reference.report_bytes()
        sidecar = reference.sidecar_bytes(report_payload)
        report = reference.strict_loads(report_payload.decode("utf-8"))
        sources = reference.sources_bytes(report_payload, sidecar)
        contract = reference.contract_bytes(report_payload, sidecar, sources, report)
        self.assertEqual(contract, reference.contract_bytes(report_payload, sidecar, sources, report))
        self.assertEqual(sidecar.decode("ascii").split("  ")[0], reference.sha256_bytes(report_payload))
        rows = reference.parse_pin_lines(sources.decode("utf-8"))
        self.assertEqual({k for _, k in rows}, set(reference.allowed_pin_keys()))

    def test_stable_identities(self) -> None:
        self.assertEqual(reference.board_link()["stable_sha256"], reference.BOARD_STABLE_SHA256)
        self.assertFalse(reference.board_link()["full_tasks_json_hashed"])
        self.assertEqual(reference.inventory_link()["stable_sha256"], reference.INVENTORY_STABLE_SHA256)


class TestStrict(unittest.TestCase):
    def test_bad_json(self) -> None:
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', ""):
            with self.assertRaises(ValueError):
                reference.strict_loads(text)

    def test_bad_pins(self) -> None:
        digest = "a" * 64
        for line in (digest + "  source:dup\n" + digest + "  source:dup\n", "abc  source:short\n", digest + "  /abs\n", digest + "  source:../x\n"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(line)


class TestBoundary(unittest.TestCase):
    def test_probe_adverse(self) -> None:
        adv = reference.probe_adverse_cases()
        self.assertEqual(adv["accepted_count"], 0)
        self.assertTrue(adv["all_rejected"])
        self.assertIsNone(adv["metrics"])
        probe = reference.validate_probe(reference.valid_probe())
        self.assertFalse(probe["qualifies"])

    def test_manifest_adverse(self) -> None:
        adv = reference.manifest_adverse_cases()
        self.assertEqual(adv["accepted_count"], 0)
        self.assertTrue(adv["all_rejected"])
        self.assertEqual(adv["asset_checks"]["absent_code"], "ASSET_ABSENT")
        self.assertFalse(adv["asset_checks"]["hash_matched_qualifies"])

    def test_unknown_span_not_needed_but_negative_control_retained(self) -> None:
        report = reference.build_report()
        self.assertTrue(any("negative" in c.lower() or "spectrum-copy" in c.lower() for c in report["negative_claims"]))
        self.assertEqual(report["source_reported"]["qualifies"], False)
        self.assertFalse(report["identity_control"]["qualifies"])

    def test_absent_assets(self) -> None:
        reference.validate_asset_pins()
        probe = reference.absent_artifact_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["workspace_found"], [])
        self.assertEqual(probe["sdk_worktree_found"], [])


class TestScope(unittest.TestCase):
    def _repo(self, path: Path) -> None:
        _git(path, "init", "-q", "-b", "main")
        _git(path, "config", "user.email", "test@example.invalid")
        _git(path, "config", "user.name", "Test User")
        _commit(path, "seed.txt", "seed\n", "seed")

    def test_newest_merge_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base_a = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "base-b")
            base_b = _commit(repo, "base-b.txt", "b\n", "newer")
            _git(repo, "update-ref", "refs/remotes/origin/main", base_b)
            _git(repo, "branch", "-f", "main", base_a)
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base_b)
            changed = reference.scope_changed_paths(repo, base_b)
            self.assertEqual(reference.scope_violations(changed), [])

    def test_out_of_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task")
            _commit(repo, "CONTRACTS.md", "x\n", "bad")
            changed = reference.scope_changed_paths(repo, base)
            self.assertEqual(reference.scope_violations(changed), ["CONTRACTS.md"])
            self.assertIsNone(reference.scope_base(repo, ("missing",)))


if __name__ == "__main__":
    unittest.main()
