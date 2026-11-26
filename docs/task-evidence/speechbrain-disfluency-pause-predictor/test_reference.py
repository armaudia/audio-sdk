# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic regression tests for SpeechBrain disfluency/pause predictor evidence."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

import reference


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _commit(repo: Path, relative: str, content: str, message: str) -> str:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", relative)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


class TestCanonical(unittest.TestCase):
    def test_report_bytes_repeatable(self) -> None:
        first = reference.report_bytes()
        self.assertEqual(first, reference.report_bytes())
        self.assertTrue(first.endswith(b"\n"))
        report = reference.strict_loads(first.decode("utf-8"))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["adverse"]["all_rejected"])
        self.assertFalse(report["evidence_classes"]["real_local_model_output"])

    def test_contract_sidecar_sources_stable(self) -> None:
        report_payload = reference.report_bytes()
        sidecar = reference.sidecar_bytes(report_payload)
        report = reference.strict_loads(report_payload.decode("utf-8"))
        sources = reference.sources_bytes(report_payload, sidecar)
        contract = reference.contract_bytes(report_payload, sidecar, sources, report)
        self.assertEqual(contract, reference.contract_bytes(report_payload, sidecar, sources, report))
        self.assertEqual(sidecar.decode("ascii").split("  ")[0], reference.sha256_bytes(report_payload))
        rows = reference.parse_pin_lines(sources.decode("utf-8"))
        self.assertEqual({k for _, k in rows}, set(reference.allowed_pin_keys()))
        self.assertNotIn("SOURCES.sha256", {k for _, k in rows})

    def test_board_link_stable_only(self) -> None:
        link = reference.board_link()
        self.assertEqual(link["stable_sha256"], reference.BOARD_STABLE_SHA256)
        self.assertFalse(link["full_tasks_json_hashed"])
        self.assertEqual(set(link["stable_fields"].keys()), set(reference.LINK_FIELDS))


class TestStrict(unittest.TestCase):
    def test_duplicate_nonfinite_rejected(self) -> None:
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', ""):
            with self.assertRaises(ValueError):
                reference.strict_loads(text)

    def test_pin_parser_rejects_unsafe(self) -> None:
        digest = "a" * 64
        for line in (digest + "  source:dup\n" + digest + "  source:dup\n", "abc  source:short\n", digest + "  /abs\n", digest + "  source:../escape\n"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(line)


class TestEnvelopeAndManifest(unittest.TestCase):
    def test_envelope_adverse_all_rejected(self) -> None:
        adverse = reference.envelope_adverse_cases()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)
        mapping = reference.validate_envelope(reference.valid_envelope())
        self.assertEqual(mapping["source_end"], 16000)
        self.assertEqual(mapping["output_end"], 16000)

    def test_manifest_adverse_and_shape_only(self) -> None:
        adverse = reference.manifest_adverse_cases()
        self.assertTrue(adverse["all_rejected"])
        manifest = reference.valid_manifest()
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.verify_assets(manifest, {})
        self.assertEqual(caught.exception.code, "ASSET_ABSENT")
        supplied = {a["path"]: f"placeholder:{a['asset_id']}".encode("utf-8") for a in manifest["assets"]}
        accepted = reference.verify_assets(manifest, supplied)
        self.assertTrue(accepted["accepted"])
        self.assertFalse(accepted["qualifies"])
        bad = dict(supplied)
        first = manifest["assets"][0]
        bad[first["path"]] = b"x" * first["byte_count"]
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.verify_assets(manifest, bad)
        self.assertEqual(caught.exception.code, "ASSET_HASH_MISMATCH")


class TestAbsenceAndPins(unittest.TestCase):
    def test_absence_probe_no_qualifying_artifact(self) -> None:
        probe = reference.absent_artifact_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["workspace_found"], [])
        self.assertEqual(probe["sdk_worktree_found"], [])
        self.assertEqual(probe["home_found"], [])
        self.assertTrue(reference.asset_pins_absent())

    def test_source_boundary_pins_valid(self) -> None:
        self.assertEqual(set(reference.validate_source_pins().keys()), {f"source:{k}" for k in reference.SOURCE_PINS})
        self.assertEqual(set(reference.validate_boundary_pins().keys()), {f"sdk:{k}" for k in reference.BOUNDARY_PINS})


class TestScopeRegression(unittest.TestCase):
    def _repo(self, path: Path) -> None:
        _git(path, "init", "-q", "-b", "main")
        _git(path, "config", "user.email", "test@example.invalid")
        _git(path, "config", "user.name", "Test User")
        _commit(path, "seed.txt", "seed\n", "seed")

    def test_newest_merge_base_preferred(self) -> None:
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
            self.assertEqual(reference.scope_violations(reference.scope_changed_paths(repo, base_b)), [])

    def test_main_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base)
            self.assertIsNone(reference.scope_base(repo, ("origin/main",)))

    def test_out_of_scope_and_missing_base_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            _commit(repo, "CONTRACTS.md", "changed\n", "out of scope")
            self.assertEqual(reference.scope_violations(reference.scope_changed_paths(repo, base)), ["CONTRACTS.md"])
            self.assertIsNone(reference.scope_base(repo, ("missing-one", "missing-two")))


if __name__ == "__main__":
    unittest.main()
