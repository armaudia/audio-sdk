# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local SDK-RT-VC evidence package."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.dont_write_bytecode = True

import reference  # noqa: E402
import verify  # noqa: E402

HERE = Path(__file__).resolve().parent


def _ok(stdout: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=0, stdout=stdout, stderr="")


class DeterministicEvidenceTests(unittest.TestCase):
    def test_report_is_fail_closed_incomplete_defer(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["task_id"], reference.TASK_ID)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["profile"], reference.PROFILE)
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["defer_before"], "opt_in_adapter_exposure")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertIsNone(report["candidate_metrics"])

    def test_gates_and_blockers_exact(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual([gate["id"] for gate in report["gates"]],
                         ["B" + str(index) for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["gates"]))
        self.assertEqual(report["exact_blockers"],
                         [dict(item) for item in reference.EXACT_BLOCKERS])
        self.assertEqual(len(report["reopen_conditions"]), 8)
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)

    def test_voice_profile_not_satisfied(self) -> None:
        report = reference.build_report()
        profile = report["voice_profile"]
        self.assertEqual([item["id"] for item in profile["required_items"]],
                         [item[0] for item in reference.VOICE_REQUIREMENTS])
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertTrue(all(
            item["satisfied_for_qualification"] is False
            for item in profile["required_items"]))
        self.assertTrue(all(
            outcome["measured"] is False
            for outcome in report["reference_protocol"]["acceptance_outcomes"]))

    def test_caller_asset_contract_is_shape_only(self) -> None:
        contract = reference.CALLER_ASSET_CONTRACT
        self.assertEqual(contract["schema_id"], reference.CALLER_SCHEMA)
        self.assertEqual(contract["asset_storage"], "external")
        self.assertEqual(contract["comparison_baseline"], "identity_source")
        self.assertFalse(contract["candidate_executed"])
        self.assertFalse(contract["model_executed"])
        self.assertEqual(contract["qualification_effect"], "none")

    def test_manifest_validation_accepts_and_rejects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rtvc-test-") as raw:
            root = Path(raw)
            manifest = reference.synthetic_caller_manifest(root)
            accepted = reference.validate_caller_manifest(manifest)
            self.assertTrue(accepted["accepted"])
            self.assertFalse(accepted["model_executed"])
            bad = dict(manifest)
            bad["weight_setup_sha256"] = "0" * 64
            with self.assertRaises(reference.ReferenceRejection) as caught:
                reference.validate_caller_manifest(bad)
            self.assertTrue(
                caught.exception.code.startswith("manifest_hash_mismatch")
                or caught.exception.code.startswith("manifest_bad_sha"),
                caught.exception.code)
            missing = dict(manifest)
            missing.pop("runtime_lock_path")
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(missing)

    def test_request_admission_only_identity_control(self) -> None:
        accepted = reference.admit_request(reference.identity_request())
        self.assertTrue(accepted["accepted"])
        self.assertTrue(accepted["identity_control"])
        self.assertFalse(accepted["candidate_executed"])
        for target, code in ((reference.CANDIDATE_TARGET,
                              "absent_rt_vc_checkpoint"),
                             (reference.TARGET_TARGET,
                              "unconfirmed_p360_reference_rights")):
            request = reference.identity_request()
            request["target"] = target
            with self.assertRaises(reference.ReferenceRejection) as caught:
                reference.admit_request(request)
            self.assertEqual(caught.exception.code, code)

    def test_pcm_validation_rejects_bad_values(self) -> None:
        for values in ([], [0.0, float("nan")], [float("inf")], [True], [1.5],
                       b"\x00"):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_pcm(values)
        source = reference.synthetic_source_pcm()
        self.assertEqual(len(source), reference.CONTROL_SAMPLES)
        self.assertEqual(reference.identity_transform(source), source)

    def test_adverse_controls_all_rejected(self) -> None:
        adverse = reference.run_adverse_controls()
        self.assertEqual([item["case"] for item in adverse],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected" for item in adverse))

    def test_absence_probes_all_absent(self) -> None:
        report = reference.build_report()
        self.assertTrue(report["asset_audit"]["all_absence_probes_absent"])
        self.assertEqual(report["absence_probes"],
                         [dict(item) for item in reference.probe_absence()])
        for item in report["missing_historical_artifacts"]:
            self.assertFalse((reference.SOURCE_ROOT / item).exists())

    def test_task_row_identity_exact_without_hashing_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(identity["stable_fields"]["title"], reference.TITLE)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertFalse(identity["full_tasks_json_hashed"])
        self.assertFalse(identity["whole_file_hashed"])

    def test_canonical_report_is_byte_deterministic(self) -> None:
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(texts[0], texts[1])
        self.assertEqual(texts[1], texts[2])
        self.assertTrue(texts[0].endswith("\n"))
        self.assertNotRegex(texts[0], r"-0\.0(?=[,}\]])")

    def test_contract_boundary_and_artifact_pins(self) -> None:
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["boundary"], reference.BOUNDARY)
        self.assertEqual(contract["scope"], reference.SCOPE)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["artifact_pins"],
                         reference.artifact_pins(
                             digest,
                             reference.sha256_bytes((digest + "\n").encode())))
        self.assertNotIn("docs/task-evidence/rt-vc/contract.json",
                         contract["artifact_pins"])
        self.assertIn("docs/task-evidence/rt-vc/report.json",
                      contract["artifact_pins"])
        self.assertTrue(text.endswith("\n"))

    def test_sources_manifest_has_expected_shape(self) -> None:
        data = reference.sources_bytes().decode("utf-8")
        lines = data.splitlines()
        self.assertEqual(lines[:5], reference.SOURCES_HEADER.splitlines())
        labels = [line.split("  ", 1)[1] for line in lines[5:]]
        expected = ([f"source:{name}" for name in sorted(reference.SOURCE_PINS)]
                    + [f"worktree:{name}"
                       for name in sorted(reference.BOUNDARY_PINS)]
                    + [f"pkg:{name}" for name in sorted(reference.PIN_FILES)])
        self.assertEqual(labels, expected)
        self.assertNotIn("pkg:SOURCES.sha256", labels)
        self.assertFalse(any("TASKS.json" in line for line in lines[5:]))

    def test_readme_digest_table_matches_files(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(reference.README_TABLE_START), 1)
        self.assertEqual(text.count(reference.README_TABLE_END), 1)
        block = text.split(reference.README_TABLE_START, 1)[1].split(
            reference.README_TABLE_END, 1)[0].strip().splitlines()
        self.assertEqual(block[:2], ["| Artifact | SHA-256 | Bytes |",
                                     "| --- | --- | ---: |"])
        pattern = re.compile(
            r"\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|")
        rows = []
        for line in block[2:]:
            match = pattern.fullmatch(line)
            self.assertIsNotNone(match, line)
            rows.append((match.group(1), match.group(2), int(match.group(3))))
        expected = [(name, reference.file_digest(HERE / name),
                     (HERE / name).stat().st_size)
                    for name in reference.README_DIGEST_FILES]
        self.assertEqual(rows, expected)

    def test_report_sidecar_matches_canonical_digest(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        digest = reference.sha256_bytes(payload)
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="utf-8"), digest + "\n")


class ScopeRegressionTests(unittest.TestCase):
    """Three fail-closed regression checks for the newest-merge-base scope."""

    def test_scope_base_refs_and_newest_merge_base(self) -> None:
        self.assertEqual(reference.SCOPE_BASE_REFS, ("origin/main", "main"))
        old = "1" * 40
        new = "2" * 40
        with mock.patch.object(reference, "git_commit",
                               side_effect=lambda _worktree, ref:
                               old if ref == "origin/main" else new), \
                mock.patch.object(reference, "_git",
                                  side_effect=lambda _worktree, *args:
                                  _ok(old) if args[:2] == ("merge-base", "HEAD")
                                  and args[2] == "origin/main" else
                                  _ok(new) if args[:2] == ("merge-base", "HEAD")
                                  and args[2] == "main" else _ok()):
            self.assertEqual(reference.scope_base(Path("/unused")), new)

    def test_scope_base_unavailable_is_reported(self) -> None:
        fake_run = mock.Mock(side_effect=lambda *_args, **_kwargs: _ok())
        with tempfile.TemporaryDirectory(prefix="rtvc-scope-") as raw, \
                mock.patch.object(reference, "scope_base", return_value=None), \
                mock.patch.object(verify.subprocess, "run", fake_run):
            worktree = Path(raw)
            (worktree / ".git").write_text("gitdir: .\n", encoding="utf-8")
            findings = verify.scope_findings(worktree)
        self.assertIn("scope_base_unavailable", findings)

    def test_base_out_of_scope_change_fails_closed(self) -> None:
        fake_run = mock.Mock(side_effect=lambda *_args, **_kwargs: _ok())
        with tempfile.TemporaryDirectory(prefix="rtvc-scope-") as raw, \
                mock.patch.object(reference, "scope_base",
                                  return_value="3" * 40), \
                mock.patch.object(
                    reference, "scope_changed_paths",
                    return_value=["docs/task-evidence/rt-vc/run.py",
                                  "CONTRACTS.md"]), \
                mock.patch.object(verify.subprocess, "run", fake_run):
            worktree = Path(raw)
            (worktree / ".git").write_text("gitdir: .\n", encoding="utf-8")
            findings = verify.scope_findings(worktree)
        self.assertIn("base_out_of_scope_change: CONTRACTS.md", findings)
        self.assertNotIn(
            "base_out_of_scope_change: docs/task-evidence/rt-vc/run.py",
            findings)

    def test_scope_base_falls_back_to_main(self) -> None:
        base = "4" * 40
        with mock.patch.object(reference, "git_commit",
                               side_effect=lambda _worktree, ref:
                               None if ref == "origin/main" else base), \
                mock.patch.object(reference, "_git",
                                  side_effect=lambda _worktree, *args: _ok(base)):
            self.assertEqual(reference.scope_base(Path("/unused")), base)

    def test_scope_violations_keep_only_task_local_paths(self) -> None:
        self.assertEqual(reference.scope_violations([
            "docs/task-evidence/rt-vc/report.json",
            "docs/task-evidence/rt-vc/test_reference.py",
            "CONTRACTS.md",
            "docs/task-evidence/meanvc/report.json",
        ]), ["CONTRACTS.md", "docs/task-evidence/meanvc/report.json"])


if __name__ == "__main__":
    unittest.main()
