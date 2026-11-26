# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for SDK-STREAMING-CONFORMER-TED evidence package."""

from __future__ import annotations

import json
import unittest

import reference
import run


class ReferenceTest(unittest.TestCase):
    def test_build_deterministic(self) -> None:
        a = reference.report_bytes()
        b = reference.report_bytes()
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))

    def test_decision_and_status(self) -> None:
        report = reference.strict_loads(reference.report_bytes().decode("utf-8"))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["profile"], "Rate")
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(len(report["exact_blockers"]), 4)
        for gate in report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
        for blocker in report["exact_blockers"]:
            self.assertFalse(blocker["qualifies"])

    def test_adverse_all_rejected(self) -> None:
        report = reference.strict_loads(reference.report_bytes().decode("utf-8"))
        adverse = report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["caller_manifest"]["all_rejected"])
        self.assertTrue(adverse["invalid_json"]["all_rejected"])
        self.assertTrue(adverse["invalid_pins"]["all_rejected"])

    def test_geometry_probe(self) -> None:
        report = reference.strict_loads(reference.report_bytes().decode("utf-8"))
        g = report["geometry_probe"]
        self.assertTrue(g["partition_ok"])
        self.assertEqual(g["accepted_samples"], 325)
        self.assertEqual(g["frame_count"], 3)
        self.assertEqual(g["final_valid_samples"], 5)
        self.assertEqual(g["final_zero_padding_samples"], 155)
        self.assertEqual(g["nonfinite_count"], 0)
        self.assertFalse(g["content_delay_claimed"])

    def test_board_link_stable_only(self) -> None:
        report = reference.strict_loads(reference.report_bytes().decode("utf-8"))
        link = report["board_link"]
        self.assertFalse(link["full_tasks_json_hashed"])
        self.assertEqual(link["stable_sha256"], reference.BOARD_STABLE_SHA256)

    def test_sources_contract_match(self) -> None:
        report = reference.report_bytes()
        sidecar = reference.sidecar_bytes(report)
        sources = reference.sources_bytes(report, sidecar)
        contract = reference.contract_bytes(report, sidecar, sources, reference.strict_loads(report.decode("utf-8")))
        self.assertIn(b"report.json", sources)
        self.assertIn(b"contract.json", sources)
        c = reference.strict_loads(contract.decode("utf-8"))
        self.assertEqual(c["report_sha256"], reference.sha256_bytes(report))
        self.assertEqual(c["sidecar_sha256"], reference.sha256_bytes(sidecar))
        self.assertEqual(c["sources_sha256"], reference.sha256_bytes(sources))

    def test_caller_manifest_terminal_rejection(self) -> None:
        manifest = reference.valid_manifest()
        manifest["source_sha256"] = reference.sha256_bytes(b"synthetic-source")
        manifest["source_byte_count"] = len(b"synthetic-source")
        manifest["checkpoint_sha256"] = reference.sha256_bytes(b"synthetic-checkpoint")
        manifest["checkpoint_byte_count"] = len(b"synthetic-checkpoint")
        manifest["streaming_config_sha256"] = reference.sha256_bytes(b"synthetic-config")
        with self.assertRaises(reference.ReferenceRejection) as ctx:
            reference.validate_caller_manifest(manifest, b"synthetic-source", b"synthetic-checkpoint", b"synthetic-config")
        self.assertEqual(ctx.exception.code, "CANDIDATE_IDENTITY_UNPINNED")

    def test_run_check_after_build(self) -> None:
        built = run.build()
        self.assertEqual(set(built.keys()), set(run.FILES))


if __name__ == "__main__":
    unittest.main()
