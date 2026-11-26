# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for SDK-NVIDIA-RE-USE task-local blocker evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run as generator  # noqa: E402


class ReferenceTests(unittest.TestCase):
    def test_base_request_and_manifest_validate(self):
        req = reference.validate_request(reference._base_request())
        self.assertEqual(req["candidate"], reference.CANDIDATE)
        self.assertFalse(req["candidate_processing"])
        man = reference.validate_asset_manifest(reference._base_manifest())
        self.assertEqual(man.report_variant if False else man["variant"], reference.TARGET_VARIANT)

    def test_adverse_requests_rejected(self):
        for name, request in reference._adverse_request_specs():
            with self.subTest(name=name):
                with self.assertRaises(reference.EvidenceError):
                    reference.validate_request(request)

    def test_adverse_manifests_rejected(self):
        for name, manifest in reference._adverse_manifest_specs():
            with self.subTest(name=name):
                with self.assertRaises(reference.EvidenceError):
                    reference.validate_asset_manifest(manifest)

    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        for name, text in (
            ("dup", '{"a":1,"a":2}'),
            ("nan", '{"a":NaN}'),
            ("inf", '{"a":Infinity}'),
            ("ninf", '{"a":-Infinity}'),
            ("trail", '{"a":1} 2'),
        ):
            with self.subTest(name=name):
                with self.assertRaises(reference.JsonError):
                    reference.strict_json_loads(text)

    def test_admit_fails_closed(self):
        result = reference.admit(reference._base_request())
        self.assertEqual(result["status"], "DEFER")
        self.assertFalse(result["admissible"])
        self.assertFalse(result["qualifies_candidate"])
        self.assertFalse(result["candidate_processing"])
        self.assertIsNone(result["metrics"])
        self.assertIn("artifact_absent", result["blockers"])

    def test_admit_asset_fails_closed_without_open(self):
        result = reference.admit_asset(reference._base_manifest())
        self.assertEqual(result["status"], "DEFER")
        self.assertFalse(result["admissible"])
        self.assertTrue(result["manifest_validated"])
        self.assertFalse(result["artifact_opened"])
        self.assertFalse(result["artifact_hashed"])
        self.assertFalse(result["artifact_loaded"])
        self.assertFalse(result["qualifies_candidate"])

    def test_probe_candidate_raises_absent(self):
        with self.assertRaises(reference.ArtifactsAbsent):
            reference.probe_candidate(reference._base_request())

    def test_missing_result_never_qualifies(self):
        missing = reference.missing_result("x")
        self.assertEqual(missing["status"], "blocked")
        self.assertFalse(missing["qualifies_candidate"])
        self.assertIsNone(missing["metrics"])

    def test_stimulus_and_paired_controls(self):
        stimuli = reference.stimulus_probe()
        self.assertFalse(stimuli["candidate_processing"])
        self.assertTrue(all(v["byte_identical"] for v in stimuli["identity_control"].values()))
        paired = reference.paired_harness_control()
        self.assertFalse(paired["candidate_processing"])
        self.assertFalse(paired["qualifies_candidate"])
        self.assertTrue(paired["identity_si_sdr_db"] > 10.0)
        self.assertLess(abs(paired["shift_si_sdr_db"]["0"] - paired["identity_si_sdr_db"]), 1e-6)

    def test_board_projection_ignores_mutable_fields(self):
        board = {"tasks": [{
            "id": reference.TASK, "title": "NVIDIA RE-USE", "mode": "feasibility",
            "repository": "audio-sdk", "component": "nvidia-re-use",
            "status": "in_progress", "owner": "x", "history": [{"a": 1}],
        }]}
        links1, digest1 = reference._board_projection(board)
        board["tasks"][0]["status"] = "done"
        board["tasks"][0]["owner"] = "y"
        board["tasks"][0]["history"].append({"b": 2})
        links2, digest2 = reference._board_projection(board)
        self.assertEqual(links1, links2)
        self.assertEqual(digest1, digest2)
        self.assertNotIn("status", links1[0])
        self.assertNotIn("history", links1[0])

    def test_report_core_contract(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertTrue(report["incomplete"])
        self.assertTrue(report["proposal_only"])
        self.assertFalse(report["board_full_file_hashed"])
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["release_gates"]))
        self.assertFalse(report["no_missing_result_qualifies_candidate"] is False)
        self.assertTrue(report["local_harness_checks"]["no_full_board_hash"])
        self.assertTrue(report["local_harness_checks"]["external_boundary_closed"])

    def test_report_bytes_deterministic(self):
        a = reference.report_bytes()
        b = reference.report_bytes()
        self.assertEqual(a, b)
        obj = json.loads(a.decode("utf-8"))
        self.assertEqual(obj["task"], reference.TASK)

    def test_build_bundle_contains_required_files(self):
        bundle = generator.build_bundle()
        self.assertEqual(set(bundle), {"report.json", "report.json.sha256", "SOURCES.sha256", "contract.json"})
        for payload in bundle.values():
            self.assertTrue(payload.endswith(b"\n"))
