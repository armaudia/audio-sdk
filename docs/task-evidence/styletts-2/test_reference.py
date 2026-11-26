# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic regression tests for the StyleTTS 2 task-local evidence package."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

import reference


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *arguments], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _commit(repo: Path, relative: str, content: str, message: str) -> str:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", relative)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


class TestCanonical(unittest.TestCase):
    def test_report_bytes_are_repeatable_and_canonical(self) -> None:
        first = reference.report_bytes()
        self.assertEqual(first, reference.report_bytes())
        self.assertTrue(first.endswith(b"\n"))
        report = reference.strict_loads(first.decode("utf-8"))
        self.assertEqual(report["decision"], reference.DECISION)
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["adverse"]["all_rejected"])
        self.assertFalse(report["evidence_classes"]["real_local_model_output"])

    def test_contract_and_sidecar_are_stable(self) -> None:
        report_payload = reference.report_bytes()
        sidecar = reference.sidecar_bytes(report_payload)
        report = reference.strict_loads(report_payload.decode("utf-8"))
        sources = reference.sources_bytes(report_payload, sidecar)
        contract = reference.contract_bytes(report_payload, sidecar, sources, report)
        self.assertEqual(contract, reference.contract_bytes(report_payload, sidecar, sources, report))
        self.assertEqual(sidecar.decode("ascii").split("  ")[0], reference.sha256_bytes(report_payload))
        rows = reference.parse_pin_lines(sources.decode("utf-8"))
        self.assertEqual({key for _, key in rows}, set(reference.allowed_pin_keys()))

    def test_stable_board_identity_is_pinned(self) -> None:
        self.assertEqual(reference.board_link()["stable_sha256"], reference.BOARD_STABLE_SHA256)
        self.assertFalse(reference.board_link()["full_tasks_json_hashed"])


class TestStrictParsers(unittest.TestCase):
    def test_duplicate_and_nonfinite_json_rejected(self) -> None:
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', ""):
            with self.assertRaises(ValueError):
                reference.strict_loads(text)

    def test_pin_parser_rejects_unsafe_keys(self) -> None:
        digest = "a" * 64
        for line in (digest + "  source:duplicate\n" + digest + "  source:duplicate\n", "abc  source:short\n", digest + "  /absolute\n", digest + "  source:../escape\n"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(line)


class TestPlanAndAssetBoundary(unittest.TestCase):
    def test_plan_rejects_unsafe_controls(self) -> None:
        adverse = reference.plan_adverse_cases()
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertTrue(adverse["all_rejected"])
        self.assertIsNone(adverse["metrics"])
        self.assertTrue(all(row["actual_code"] == row["expected_code"] for row in adverse["cases"]))
        mapping = reference.validate_plan(reference.valid_plan())
        self.assertEqual(mapping["source_end"], reference.FIXTURE_SAMPLES)
        self.assertEqual(mapping["output_end"], reference.FIXTURE_SAMPLES)
        self.assertFalse(mapping["qualifies"])

    def test_caller_manifest_fails_closed(self) -> None:
        manifest = reference.valid_manifest()
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.verify_assets(manifest, {})
        self.assertEqual(caught.exception.code, "ASSET_ABSENT")
        matched = {asset["path"]: ("caller-supplied synthetic placeholder for " + asset["asset_id"]).encode("utf-8") for asset in manifest["assets"]}
        accepted = reference.verify_assets(manifest, matched)
        self.assertEqual(accepted["count"], len(reference.REQUIRED_ASSETS))
        self.assertFalse(accepted["qualifies"])
        bad = dict(matched)
        bad[manifest["assets"][0]["path"]] = b"x" * manifest["assets"][0]["byte_count"]
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.verify_assets(manifest, bad)
        self.assertEqual(caught.exception.code, "ASSET_HASH_MISMATCH")

    def test_identity_control_not_candidate_result(self) -> None:
        control = reference.identity_control()
        self.assertTrue(control["alternating_or_fixed_integer_sequence_byte_identical"])
        self.assertEqual(control["sample_count"], reference.FIXTURE_SAMPLES)
        self.assertEqual(control["duration_ratio"], "1")
        self.assertFalse(control["qualifies"])

    def test_source_pins_and_asset_absence(self) -> None:
        reference.validate_asset_pins()
        probe = reference.absent_artifact_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["workspace_found"], [])
        self.assertEqual(probe["sdk_worktree_found"], [])
        self.assertTrue(reference.asset_pins_absent())


class TestScopeRegression(unittest.TestCase):
    def _repo(self, path: Path) -> None:
        _git(path, "init", "-q", "-b", "main")
        _git(path, "config", "user.email", "test@example.invalid")
        _git(path, "config", "user.name", "Test User")
        _commit(path, "seed.txt", "seed\n", "seed")

    def test_newest_merge_base_is_preferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base_a = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "base-b")
            base_b = _commit(repo, "base-b.txt", "b\n", "newer base")
            _git(repo, "update-ref", "refs/remotes/origin/main", base_b)
            _git(repo, "branch", "-f", "main", base_a)
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base_b)
            changed = reference.scope_changed_paths(repo, base_b)
            self.assertEqual(changed, [reference.TASK_PREFIX + "report.json"])
            self.assertEqual(reference.scope_violations(changed), [])

    def test_main_fallback_when_origin_main_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base)
            self.assertIsNone(reference.scope_base(repo, ("origin/main",)))

    def test_out_of_scope_change_and_missing_base_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            _commit(repo, "CONTRACTS.md", "changed\n", "out of scope")
            changed = reference.scope_changed_paths(repo, base)
            self.assertEqual(reference.scope_violations(changed), ["CONTRACTS.md"])
            self.assertIsNone(reference.scope_base(repo, ("missing-one", "missing-two")))


if __name__ == "__main__":
    unittest.main()
