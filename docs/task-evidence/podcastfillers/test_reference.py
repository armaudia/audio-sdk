# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the PodcastFillers readiness package.

No dataset, audio, model, runtime, network or download is used.
"""

from __future__ import annotations

import copy
import hashlib
import json
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


class PodcastFillersReferenceTest(unittest.TestCase):
    def test_canonical_report_stable(self) -> None:
        report_a = reference.build_report()
        report_b = reference.build_report()
        text_a, digest_a = reference.canonical_report(report_a)
        text_b, digest_b = reference.canonical_report(report_b)
        self.assertEqual(text_a, text_b)
        self.assertEqual(digest_a, digest_b)
        self.assertTrue(text_a.endswith("\n"))
        json.loads(text_a)

    def test_contract_and_report_invariants(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        report = reference.build_report()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertTrue(report["qualification"]["not_qualified"])
        self.assertTrue(report["qualification"]["all_release_gates_blocked"])
        self.assertFalse(report["qualification"]["missing_result_promoted"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(len(report["required_artifacts"]), 7)
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertTrue(all(g["qualifies"] is False for g in report["gates"]))
        self.assertTrue(all(b["status"] == "open" for b in report["exact_blockers"]))

    def test_rate_profile_phrases_present(self) -> None:
        text = (reference.AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md").read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
        self.assertEqual(len(rows), 1)
        for phrase in ("Measure source/output mapping, duration", "pitch, transient audibility",
                       "playback buffering", "1×, rate changes", "music, silence",
                       "rebuffer, drift", "final partial window", "source timestamps",
                       "speech preservation"):
            self.assertIn(phrase, rows[0])

    def test_source_and_boundary_pins(self) -> None:
        for pins, root in ((reference.SOURCE_PINS, reference.AUDIO_ROOT),
                           (reference.BOUNDARY_PINS, reference.WORKTREE)):
            for relative, expected in pins.items():
                self.assertEqual(reference.sha256_file(root / relative), expected, relative)

    def test_absence_probes_all_absent(self) -> None:
        report = reference.build_report()
        summary = report["absence_evidence"]["summary"]
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["dataset_loaded"])
        self.assertFalse(summary["model_executed"])
        self.assertFalse(summary["audio_read"])

    def test_admission_rejects_invalid_and_accepts_control(self) -> None:
        admission = reference.build_admission()
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(admission["summary"]["rejected_count"], admission["summary"]["case_count"])
        self.assertFalse(admission["summary"]["state_advanced_on_rejection"])
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])

    def test_scorer_control_synthetic(self) -> None:
        control = reference.scorer_control()
        self.assertTrue(control["synthetic"])
        self.assertFalse(control["qualifies"])
        self.assertFalse(control["audio_read"])
        self.assertFalse(control["model_invoked"])
        self.assertEqual(control["result"]["f1"], "0.666667")
        self.assertEqual(control["result"]["precision"], "0.666667")
        self.assertEqual(control["result"]["recall"], "0.666667")

    def test_report_has_no_floats(self) -> None:
        report = reference.build_report()
        reference._no_floats(report)

    def test_linked_row_identity_only(self) -> None:
        identity = reference.build_report()["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["projection"]["id"], reference.TASK)
        self.assertEqual(sorted(identity["projection"].keys()), sorted(reference.BOARD_ROW_FIELDS))

    def test_non_claims_and_scope(self) -> None:
        report = reference.build_report()
        for phrase in ("No PodcastFillers dataset", "No provider, registry, descriptor",
                       "Non-commercial annotations are not", "Source-reported pipeline ideas are not evidence"):
            self.assertTrue(any(phrase in c for c in report["non_claims"]), phrase)
        self.assertTrue(report["scope"]["task_local_only"])
        self.assertFalse(report["scope"]["dataset_acquired"])
        self.assertFalse(report["scope"]["public_abi_changed"])
        self.assertFalse(report["scope"]["shared_build_or_ci_changed"])

    def test_admission_rejects_nonfinite_and_missing(self) -> None:
        base = reference.control_manifest()
        bad = copy.deepcopy(base)
        bad["outcomes"]["precision"] = float("inf")
        with self.assertRaises(ValueError):
            reference.validate_manifest(bad)
        bad2 = copy.deepcopy(base)
        del bad2["dataset"]
        with self.assertRaises(ValueError):
            reference.validate_manifest(bad2)

    def test_three_regenerations_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Regenerate from module into HERE is destructive; instead verify run.write_once logic by
            # running run.py in subprocess in temp copy? Simpler: call canonical builders repeatedly.
            a1, d1 = reference.canonical_report(reference.build_report())
            a2, d2 = reference.canonical_report(reference.build_report())
            a3, d3 = reference.canonical_report(reference.build_report())
            self.assertEqual(d1, d2)
            self.assertEqual(d2, d3)
            self.assertEqual(a1, a2)
            self.assertEqual(a2, a3)
            c1 = reference.canonical_bytes(reference.build_contract())
            c2 = reference.canonical_bytes(reference.build_contract())
            c3 = reference.canonical_bytes(reference.build_contract())
            self.assertEqual(c1, c2)
            self.assertEqual(c2, c3)
            (tmp_path / "report.json").write_text(a1, encoding="utf-8")
            self.assertEqual(hashlib.sha256((tmp_path / "report.json").read_bytes()).hexdigest(), d1)


if __name__ == "__main__":
    unittest.main()
