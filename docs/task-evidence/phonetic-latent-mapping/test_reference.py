# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for SDK-PHONETIC-LATENT-MAPPING DEFER evidence package."""

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
import run  # noqa: E402


class TestPhoneticLatentMappingEvidence(unittest.TestCase):
    def test_contract_and_report_shape(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(len(report["exact_blockers"]), 7)
        self.assertEqual(len(report["required_artifacts"]), 9)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in report["gates"]))
        self.assertTrue(all(b["status"] == "open" and b["qualifies"] is False for b in report["exact_blockers"]))

    def test_admission_controls_fail_closed(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["all_codes_match"])
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["network_used"])
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["code"], case["expected_code"])
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])

    def test_gate_control_synthetic(self) -> None:
        control = reference.gate_control()
        self.assertEqual(control["summary"]["qualifying_results"], 0)
        self.assertFalse(control["summary"]["runtime_imported"])
        self.assertFalse(control["summary"]["candidate_executed"])
        frame = control["frame"]
        self.assertTrue(frame["summary"]["all_rejected"])
        self.assertTrue(frame["summary"]["all_codes_match"])
        self.assertEqual(frame["summary"]["rejected_count"], 12)

    def test_presence_and_pins(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["candidate_note_present"])
        self.assertTrue(presence["method_family_underspecified"])
        self.assertFalse(presence["exact_licensed_source_weights_runtime_present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["network_used"])
        source, boundary, sibling = reference.verify_pins()
        self.assertTrue(all(row["verified"] for row in source.values()))
        self.assertTrue(all(row["verified"] for row in boundary.values()))
        self.assertTrue(all(row["verified"] for row in sibling.values()))

    def test_canonical_report_and_sources(self) -> None:
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(len(digest), 64)
        payload, digest2 = run.canonical_report_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), digest2)
        sources = run.sources_bytes().decode("ascii")
        self.assertIn("source:research/voice-enhancement-20261101/candidate_matrix.csv", sources)
        self.assertIn("sibling:docs/task-evidence/hubert-conversion-encoder/report.json", sources)

    def test_regeneration_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="phonetic-latent-test-") as td:
            root = Path(td)
            scratch = root / "audioml/worktrees/audio-sdk/SDK-PHONETIC-LATENT-MAPPING"
            target = scratch / reference.TASK_PREFIX
            target.mkdir(parents=True)
            for path in HERE.iterdir():
                if path.is_file():
                    (target / path.name).write_bytes(path.read_bytes())
            for rel in reference.SOURCE_PINS:
                link = root / "audioml" / rel
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(reference.AUDIO_ROOT / rel)
            board = root / "audioml" / reference.BOARD_TASK_ROW
            board.parent.mkdir(parents=True, exist_ok=True)
            board.symlink_to(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
            for rel in list(reference.BOUNDARY_PINS) + list(reference.SIBLING_PINS):
                link = scratch / rel
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(reference.WORKTREE / rel)
            env = dict(__import__("os").environ, PYTHONDONTWRITEBYTECODE="1")
            env.pop("AUDIOML_ROOT", None)
            digests = []
            for _ in range(3):
                proc = subprocess.run([sys.executable, "run.py", "all"], cwd=target, capture_output=True, text=True, env=env)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                digests.append(hashlib.sha256((target / "report.json").read_bytes()).hexdigest())
            self.assertEqual(len(set(digests)), 1)


if __name__ == "__main__":
    unittest.main()
