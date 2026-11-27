# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION blocker evidence."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402


class WaveformOnlyFillerStutterDeletionReferenceTests(unittest.TestCase):
    def test_canonical_bytes_stable(self) -> None:
        c1 = reference.canonical_bytes(reference.build_contract())
        c2 = reference.canonical_bytes(reference.build_contract())
        r1 = reference.canonical_bytes(reference.build_report())
        r2 = reference.canonical_bytes(reference.build_report())
        self.assertEqual(c1, c2)
        self.assertEqual(r1, r2)
        self.assertTrue(c1.endswith(b"\n"))
        self.assertTrue(r1.endswith(b"\n"))

    def test_strict_json_rejects_adverse(self) -> None:
        bad = [
            '{\n  "a": 1,\n  "a": 2\n}\n',
            '{"a": 1.0}\n',
            '{"a": NaN}\n',
            '{"a": Infinity}\n',
            '{"a": -Infinity}\n',
            '\ufeff{"a": 1}\n',
            '{"a": 1}\n{}\n',
        ]
        for s in bad:
            with self.assertRaises(reference.ReferenceError):
                reference.loads_strict(s)

    def test_load_strict_json_rejects_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "missing.json"
            with self.assertRaises((reference.ReferenceError, OSError, FileNotFoundError)):
                reference.load_strict_json(p)

    def test_policy_blocked_defer_not_qualified(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(contract["proposal_only"])
        self.assertTrue(report["proposal_only"])
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(contract["qualification"]["qualified"])
        self.assertTrue(contract["qualification"]["not_qualified"])
        self.assertEqual(len(report["release_gates"]), 8)
        for g in report["release_gates"]:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
        self.assertEqual(len(report["rate_profile_requirements"]), 8)
        for v in report["rate_profile_requirements"]:
            self.assertEqual(v["status"], "blocked")

    def test_linked_row_identity_no_mutable_board_hash(self) -> None:
        contract = reference.build_contract()
        ident = contract["linked_row_identity"]
        self.assertFalse(ident["mutable_board_hash_used"])
        self.assertEqual(ident["task"], "SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION")
        proj = ident["projection"]
        self.assertEqual(proj["id"], "SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION")
        self.assertEqual(proj["component"], "waveform-only-filler-stutter-deletion")
        self.assertEqual(proj["mode"], "research-control")
        self.assertNotIn("status", proj)
        self.assertNotIn("owner", proj)
        self.assertNotIn("claim", proj)
        self.assertEqual(
            ident["projection_sha256"],
            reference.sha256_bytes(reference.canonical_bytes(proj).rstrip(b"\n")),
        )

    def test_absence_probes_reported(self) -> None:
        report = reference.build_report()
        summary = report["absence_summary"]
        self.assertGreater(summary["probe_count"], 0)
        self.assertIn("all_absent", summary)
        self.assertIn("present_paths", summary)

    def test_run_three_regens_identical(self) -> None:
        before_r = (HERE / "report.json").read_bytes()
        before_c = (HERE / "contract.json").read_bytes()
        before_s = (HERE / "SOURCES.sha256").read_bytes()
        before_d = (HERE / "report.json.sha256").read_bytes()
        for _ in range(3):
            rc = run.main(["all"])
            self.assertEqual(rc, 0)
            self.assertEqual(before_r, (HERE / "report.json").read_bytes())
            self.assertEqual(before_c, (HERE / "contract.json").read_bytes())
            self.assertEqual(before_s, (HERE / "SOURCES.sha256").read_bytes())
            self.assertEqual(before_d, (HERE / "report.json.sha256").read_bytes())

    def test_report_digest_sidecar(self) -> None:
        report = reference.build_report()
        digest = reference.report_digest(report)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
        self.assertEqual(sidecar, digest + "  report.json")

    def test_sources_manifest_covers_local_and_pins(self) -> None:
        manifest = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for name in ["reference.py", "report.json", "contract.json", "verify.py", "run.py", "test_reference.py", "README.md"]:
            self.assertIn("  " + name, manifest)
        self.assertIn("source:linked-row:SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION", manifest)
        self.assertIn("boundary:CONTRACTS.md", manifest)

    def test_scope_helper_detects_task_prefix(self) -> None:
        out = subprocess.check_output(["git", "-C", str(reference.WORKTREE), "status", "--porcelain"], text=True)
        for line in out.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(reference.TASK_PREFIX), path)


if __name__ == "__main__":
    unittest.main()
