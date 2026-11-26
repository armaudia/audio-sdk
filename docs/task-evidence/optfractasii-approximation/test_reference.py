# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-OPTFRACTASII-APPROXIMATION blocker evidence."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import reference as ref
import run

HERE = Path(__file__).resolve().parent


class ReferenceEvidenceTest(unittest.TestCase):
    def test_board_identity(self):
        proj = ref.board_row_projection()
        self.assertEqual(proj["id"], ref.TASK)
        self.assertEqual(proj["component"], ref.COMPONENT_ID)
        self.assertEqual(proj["mode"], ref.MODE)
        self.assertEqual(tuple(proj["depends_on"]), ref.DEPENDS_ON)
        rows = ref.linked_rows()
        self.assertEqual([r["id"] for r in rows], list(ref.LINKED_ROW_IDS))
        self.assertTrue(ref.board_row_digest(proj))
        self.assertTrue(ref.linked_rows_digest(rows))

    def test_contract_and_report_deterministic(self):
        c1 = ref.canonical_bytes(ref.build_contract())
        c2 = ref.canonical_bytes(ref.build_contract())
        self.assertEqual(c1, c2)
        r1, d1 = ref.canonical_report()
        r2, d2 = ref.canonical_report()
        self.assertEqual(r1, r2)
        self.assertEqual(d1, d2)
        report = json.loads(r1)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertTrue(report["qualification"]["not_qualified"])
        self.assertTrue(report["disposition"]["proposal_only"])
        self.assertTrue(report["disposition"]["incomplete"])

    def test_release_gates_blocked(self):
        report = ref.build_report()
        gates = report["release_gates"]
        self.assertEqual(len(gates), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertIn("reopen_condition", gate)

    def test_blockers_and_artifacts(self):
        report = ref.build_report()
        self.assertEqual(len(report["exact_blockers"]), 5)
        for blk in report["exact_blockers"]:
            self.assertEqual(blk["status"], "open")
            self.assertFalse(blk["qualifies"])
        arts = report["required_artifacts"]
        self.assertEqual(len(arts), 6)
        self.assertTrue(arts[0]["present"])
        for art in arts[1:]:
            self.assertFalse(art["present"])
            self.assertTrue(art["blocked"])

    def test_dsp_profile_not_satisfied(self):
        report = ref.build_report()
        dsp = report["dsp_profile"]
        self.assertEqual(dsp["profile"], "dsp")
        self.assertFalse(dsp["profile_satisfied"])
        self.assertEqual(dsp["real_results"], 0)
        self.assertEqual(dsp["synthetic_results"], 0)
        self.assertFalse(dsp["qualified_result_present"])
        self.assertTrue(dsp["profile_source_check"]["all_phrases_present"])
        for row in dsp["requirement_rows"]:
            self.assertFalse(row["qualifies"])
        blocked = [r for r in dsp["requirement_rows"] if r["status"] == "blocked"]
        self.assertGreaterEqual(len(blocked), 4)

    def test_asset_declaration_fail_closed(self):
        summary = ref.asset_declaration_summary()
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["strict_json_all_rejected"])
        self.assertFalse(summary["accepted_control_qualifies"])
        self.assertGreaterEqual(summary["rejection_cases"], 20)
        self.assertGreaterEqual(summary["strict_json_cases"], 9)
        # accepted control must be exactly the unpopulated shape
        accepted = ref.accepted_unpopulated_declaration()
        self.assertEqual(ref.validate_asset_declaration(accepted)["status"], "accepted_unpopulated")
        with self.assertRaises(ValueError):
            ref.validate_asset_declaration([])
        bad = ref.accepted_unpopulated_declaration()
        bad["disposition"]["qualifies"] = True
        with self.assertRaises(ValueError):
            ref.validate_asset_declaration(bad)

    def test_strict_json_rejections(self):
        for case_id, payload in ref.STRICT_JSON_REJECTIONS:
            with self.subTest(case=case_id):
                with self.assertRaises(ValueError):
                    ref.parse_strict_json_text(payload)

    def test_absence_probes_fixed(self):
        summary = ref.absence_summary()
        self.assertTrue(summary["all_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["fixed_probe_list_only"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["network_used"])
        self.assertGreaterEqual(summary["probe_count"], 10)

    def test_pins_verified(self):
        for label, pins, root in [("source", ref.SOURCE_PINS, ref.AUDIO_ROOT), ("boundary", ref.BOUNDARY_PINS, ref.SDK_ROOT)]:
            for rel, expected in pins.items():
                p = root / rel
                self.assertTrue(p.is_file(), f"{label} missing {rel}")
                self.assertEqual(ref.sha256_file(p), expected, f"{label} mismatch {rel}")

    def test_sources_and_readme_digests(self):
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        counts = ref.verify_readme_digests(readme)
        self.assertEqual(set(counts.keys()), set(ref.README_SECTIONS))
        for v in counts.values():
            self.assertGreater(v, 0)
        sources = ref.sources_bytes()
        self.assertIn(b"reference.py", sources)
        self.assertNotIn(b"plan/swarm/TASKS.json", sources)

    def test_run_repeatability(self):
        # run all in temp dir
        import tempfile, shutil, subprocess, sys
        with tempfile.TemporaryDirectory(prefix="optfractasii-test-") as tmp:
            tmp_dir = Path(tmp)
            cmd = [sys.executable, str(HERE / "run.py"), "all", "--repeats", "3", "--output-dir", str(tmp_dir)]
            proc = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            for name in ["contract.json", "report.json", "report.json.sha256", "SOURCES.sha256", "README.md"]:
                self.assertEqual((tmp_dir / name).read_bytes(), (HERE / name).read_bytes(), name)

    def test_no_forbidden_suffixes(self):
        for p in HERE.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                self.assertNotIn(p.suffix.lower(), ref.FORBIDDEN_SUFFIXES, p.name)


if __name__ == "__main__":
    unittest.main()
