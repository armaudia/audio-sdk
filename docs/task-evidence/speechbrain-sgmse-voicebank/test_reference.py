# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SpeechBrain SGMSE-VoiceBank evidence package."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

import reference


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *arguments],
                            capture_output=True, text=True, check=True)
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
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["adverse"]["all_rejected"])

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

    def test_stable_identities_are_pinned(self) -> None:
        self.assertEqual(reference.board_link()["stable_sha256"], reference.BOARD_STABLE_SHA256)
        self.assertEqual(reference.inventory_link()["stable_sha256"], reference.INVENTORY_STABLE_SHA256)


class TestStrictParsers(unittest.TestCase):
    def test_duplicate_and_nonfinite_json_rejected(self) -> None:
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', ""):
            with self.assertRaises(ValueError):
                reference.strict_loads(text)

    def test_pin_parser_rejects_unsafe_keys(self) -> None:
        digest = "a" * 64
        for line in (digest + "  source:duplicate\n" + digest + "  source:duplicate\n",
                     "abc  source:short\n", digest + "  /absolute\n", digest + "  source:../escape\n"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(line)


class TestAssetBoundary(unittest.TestCase):
    def test_caller_manifest_fails_closed(self) -> None:
        manifest = reference.valid_manifest()
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_caller_manifest(manifest)
        self.assertEqual(caught.exception.code, "ASSET_ABSENT")
        adverse = reference.adverse_cases()
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertTrue(adverse["all_rejected"])

    def test_hash_matched_caller_asset_still_fails_closed(self) -> None:
        payload = b"metadata-only fixture, not an SGMSE checkpoint"
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "caller.ckpt"
            checkpoint.write_bytes(payload)
            manifest = reference.valid_manifest(str(checkpoint))
            manifest["checkpoint_sha256"] = reference.sha256_bytes(payload)
            manifest["checkpoint_byte_count"] = len(payload)
            with self.assertRaises(reference.ReferenceRejection) as caught:
                reference.validate_caller_manifest(manifest)
        self.assertEqual(caught.exception.code, "SGMSE_VOICEBANK_ASSET_IDENTITY_UNPINNED")

    def test_synthetic_controls_are_labelled_and_bit_exact(self) -> None:
        fixture = reference.synthetic_enhancement_fixture()
        self.assertIn("not audio, not enhancement output", fixture["label"])
        self.assertTrue(fixture["identity_control"]["source_interval_union_exact"])
        self.assertFalse(fixture["identity_control"]["qualifies_candidate"])
        self.assertEqual(fixture["canonical_samples_sha256"], fixture["content_controls"][0]["samples_sha256"])
        self.assertEqual(fixture["sample_ns"], 62500)
        self.assertEqual(fixture["frame_ns"], 10000000)
        self.assertEqual(fixture["final_partial_frame_samples"], 5)
        self.assertEqual(fixture["final_frame_zero_padding"], 155)
        align = reference.alignment_probe()
        self.assertIsNone(align["first_output_ns"])
        self.assertFalse(align["measured"])
        state = reference.state_probe()
        self.assertTrue(state["matches_expectation"])
        self.assertFalse(state["state_owned"])
        self.assertTrue(state["chunk_invariance_exact"])


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
