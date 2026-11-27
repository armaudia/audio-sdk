# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for SDK-XLSTM-SENET2 blocker evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402
import verify  # noqa: E402


class XlstmSenet2EvidenceTests(unittest.TestCase):
    def test_contract_and_report_schema(self):
        contract = reference.build_contract()
        reference.validate_contract(contract)
        report = reference.build_report()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA_ID)
        self.assertEqual(report["contract_sha256"], reference.object_digest(contract))
        self.assertFalse(contract["board_file_pinned"])

    def test_stable_linked_row_identity_not_board_status(self):
        identity = reference.board_row_identity()
        self.assertEqual(identity["projection"]["id"], reference.TASK)
        self.assertEqual(identity["projection"]["depends_on"], ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"])
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        board = reference.read_strict_json(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        row = next(item for item in board["tasks"] if item.get("id") == reference.TASK)
        row = dict(row)
        row["status"] = "done"
        row["owner"] = "someone-else"
        projection = {field: row.get(field) for field in reference.BOARD_ROW_FIELDS}
        self.assertEqual(projection, identity["projection"])

    def test_absence_probes_all_absent(self):
        absence = reference.probe_absence()
        self.assertTrue(absence["summary"]["all_probes_absent"])
        self.assertEqual(absence["summary"]["present_count"], 0)
        self.assertFalse(absence["summary"]["download_attempted"])
        self.assertFalse(absence["summary"]["network_used"])
        self.assertFalse(absence["summary"]["recursive_workspace_walk"])

    def test_admission_fail_closed_and_control(self):
        summary = reference.admission_summary()
        self.assertGreater(summary["summary"]["case_count"], 50)
        self.assertEqual(summary["summary"]["qualifying_results"], 0)
        self.assertEqual(summary["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(summary["summary"]["case_count"], summary["summary"]["rejected_count"] + 1)
        control = summary["control"]
        self.assertTrue(control["accepted"])
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["evidence_class"], "synthetic_schema_control_not_evidence")
        bad = reference.valid_manifest()
        bad["weights"][0]["byte_count"] = True
        ok, code, _ = reference.validate_manifest(bad)
        self.assertFalse(ok)
        self.assertEqual(code, "invalid_value")
        bad = reference.valid_manifest(); bad["outcomes"]["stoi"] = float("nan")
        ok, code, _ = reference.validate_manifest(bad)
        self.assertFalse(ok)
        self.assertEqual(code, "nonfinite_value")

    def test_gates_blocked_not_qualified(self):
        report = reference.build_report()
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in report["gates"]))
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertTrue(all(b["status"] == "open" and b["qualifies"] is False for b in report["exact_blockers"]))
        self.assertTrue(report["qualification"]["not_qualified"])
        self.assertTrue(report["qualification"]["all_release_gates_blocked"])
        self.assertFalse(report["qualification"]["missing_result_promoted"])
        self.assertEqual(report["enhancement_profile"]["profile"], "Enhancement")
        self.assertEqual(len(report["enhancement_profile"]["rows"]), 5)

    def test_canonical_report_and_sidecar(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), digest)
        body = json.loads(text)
        self.assertNotIn("report_sha256", body)

    def test_run_all_byte_identical(self):
        digest1 = run.write_once({"report.json", "sources"})
        b1 = (HERE / "report.json").read_bytes(), (HERE / "report.json.sha256").read_bytes(), (HERE / "contract.json").read_bytes(), (HERE / "SOURCES.sha256").read_bytes()
        digest2 = run.write_once({"report.json", "sources"})
        b2 = (HERE / "report.json").read_bytes(), (HERE / "report.json.sha256").read_bytes(), (HERE / "contract.json").read_bytes(), (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(digest1, digest2)
        self.assertEqual(b1, b2)

    def test_sources_manifest_excludes_self(self):
        data = run.sources_bytes().decode("ascii")
        self.assertNotIn("SOURCES.sha256  ", data)
        self.assertIn("source:research/noise_suppression_candidate_census.md", data)
        self.assertIn(reference.TASK_PREFIX + "reference.py", data)

    def test_scope_base_prefers_origin_main(self):
        with mock.patch.object(reference, "git_commit", side_effect=lambda _w, ref: {"origin/main": "a", "main": "b"}.get(ref)):
            with mock.patch.object(reference, "_git") as git:
                def fake_git(_w, *args):
                    if args[:3] == ("merge-base", "HEAD", "origin/main"):
                        return subprocess.CompletedProcess(args, 0, stdout="base-origin\n", stderr="")
                    if args[:3] == ("merge-base", "HEAD", "main"):
                        return subprocess.CompletedProcess(args, 0, stdout="base-main\n", stderr="")
                    if args[:4] == ("merge-base", "--is-ancestor", "base-origin", "base-main"):
                        return subprocess.CompletedProcess(args, 1, stdout="", stderr="")
                    if args[:4] == ("merge-base", "--is-ancestor", "base-main", "base-origin"):
                        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
                    raise AssertionError(args)
                git.side_effect = fake_git
                self.assertEqual(reference.scope_base(Path(".")), "base-origin")

    def test_scope_base_unavailable_fails_closed(self):
        with mock.patch.object(reference, "scope_base", return_value=None):
            errors: list[str] = []
            changed, base_checked = verify.check_scope(errors)
            self.assertIn("scope_base_unavailable", errors)
            self.assertFalse(base_checked)

    def test_base_out_of_scope_change_fails_closed(self):
        with mock.patch.object(reference, "scope_base", return_value="deadbeef"):
            with mock.patch.object(reference, "scope_changed_paths", return_value=[reference.TASK_PREFIX + "ok.py", "README.md"]):
                errors: list[str] = []
                verify.check_scope(errors)
                self.assertIn("base_out_of_scope_change:README.md", errors)
                self.assertNotIn("base_out_of_scope_change:" + reference.TASK_PREFIX + "ok.py", errors)

    def test_verify_passes(self):
        proc = subprocess.run([sys.executable, str(HERE / "verify.py")], cwd=reference.WORKTREE, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
