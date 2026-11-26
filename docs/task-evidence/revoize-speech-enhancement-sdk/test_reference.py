# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for Revoize speech enhancement SDK evidence package."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


class StrictJsonTests(unittest.TestCase):
    def test_canonical_bytes_order_independent(self):
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": [2, 3]}), reference.canonical_bytes({"a": [2, 3], "b": 1}))

    def test_duplicate_key_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_nonfinite_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.Reject):
                reference.strict_loads('{"a":%s}' % token)


class SyntheticControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.control = cls.report["synthetic_control"]

    def test_control_non_qualifying(self):
        self.assertIs(self.control["qualifies_candidate"], False)
        self.assertIs(self.control["not_revoize"], True)
        self.assertIs(self.control["not_real_audio_corpus"], True)

    def test_control_deterministic(self):
        a = reference.synthetic_control()
        b = reference.synthetic_control()
        self.assertEqual(a["decision_digest"], b["decision_digest"])
        self.assertEqual(a["detected_activity_events"], b["detected_activity_events"])
        self.assertEqual(a["counts"], b["counts"])


class CandidateMetricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_all_candidate_metrics_null(self):
        cm = self.report["candidate_metrics"]
        self.assertIs(cm["derived_from_synthetic_control"], False)
        for k, v in cm.items():
            if k == "derived_from_synthetic_control":
                continue
            self.assertIs(v["measured"], False, k)
            self.assertIsNone(v["value"], k)


class ManifestTests(unittest.TestCase):
    def base(self):
        return reference._base_manifest()

    def test_valid_manifest_normalizes(self):
        n = reference.validate_manifest(self.base())
        self.assertEqual(n["variant"], reference.REQUIRED_VARIANT)

    def test_missing_field_rejected(self):
        m = self.base(); del m["runtime_package_sha256"]
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_extra_field_rejected(self):
        m = self.base(); m["extra"] = 1
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_relative_path_rejected(self):
        m = self.base(); m["sdk_package_path"] = "rel/sdk.tar"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_traversal_rejected(self):
        m = self.base(); m["runtime_package_path"] = "/opt/../x.tar"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_bad_sha_rejected(self):
        m = self.base(); m["sdk_package_sha256"] = "ZZZ"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_bad_pin_rejected(self):
        m = self.base(); m["source_revision_or_release"] = "latest"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_variant_rejected(self):
        m = self.base(); m["variant"] = "nope"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_capability_false_rejected(self):
        m = self.base(); m["claimed_revoize_capability"] = False
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_channels_rejected(self):
        m = self.base(); m["channels"] = 2
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_sample_rate_rejected(self):
        m = self.base(); m["sample_rate_hz"] = 44100
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_bad_frame_samples_rejected(self):
        m = self.base(); m["frame_samples"] = 0
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)


class FrameAdverseTests(unittest.TestCase):
    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(reference.Reject):
                reference.frame_rms_dbfs([0.0] * 159 + [bad])

    def test_length_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([0.0] * 10)
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([0.0] * 161)

    def test_type_range_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([True] + [0.0] * 159)
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs(["0"] + [0.0] * 159)
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([2.0] + [0.0] * 159)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.raw = reference.canonical_report_bytes(cls.report)

    def test_disposition(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertIs(self.report["proposal_only"], True)
        q = self.report["qualification"]
        self.assertIs(q["candidate_qualified"], False)
        self.assertEqual(q["status"], "not_qualified")
        self.assertEqual(q["qualification_status"], "not_qualified")
        self.assertIs(q["no_missing_result_qualifies_candidate"], True)
        self.assertIs(q["synthetic_control_is_not_candidate_evidence"], True)

    def test_gates_and_blockers(self):
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertTrue(all(g["blocked"] is True and g["status"] == "blocked" for g in self.report["gates"]))
        self.assertEqual(len(self.report["exact_blockers"]), 8)

    def test_adverse_all_rejected(self):
        adverse = self.report["controls"]["adverse"]
        self.assertGreaterEqual(len(adverse), 20)
        self.assertTrue(all(a["result"] == "rejected" for a in adverse))

    def test_task_row_identity(self):
        tri = self.report["task_row_identity"]
        self.assertFalse(tri["whole_file_hashed"])
        self.assertNotIn(reference.BOARD_PATH, self.report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, self.report["boundary_pins"])
        self.assertEqual(tri["stable_fields"]["id"], reference.TASK)
        for f in reference.MUTABLE_TASK_FIELDS:
            self.assertIn(f, tri["excluded_mutable_fields"])

    def test_scope_boundary(self):
        for k, v in self.report["scope"].items():
            if k in ("feature_domain_synthetic_control", "proposal_only", "task_local_only"):
                self.assertIs(v, True, k)
            else:
                self.assertIs(v, False, k)
        for k, v in self.report["boundary"].items():
            self.assertIs(v, False, k)

    def test_no_qualification_claim(self):
        text = self.raw.decode("utf-8").replace(" ", "")
        self.assertIn('"candidate_qualified":false', text)
        self.assertIn('"decision":"DEFER"', text)

    def test_candidate_metrics_null(self):
        cm = self.report["candidate_metrics"]
        self.assertIs(cm["derived_from_synthetic_control"], False)
        for k, v in cm.items():
            if k == "derived_from_synthetic_control":
                continue
            self.assertIsNone(v["value"], k)
            self.assertIs(v["measured"], False, k)

    def test_deterministic(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)


class AtomicStateTests(unittest.TestCase):
    def test_invalid_payload_does_not_mutate(self):
        holder = reference.EvidenceReport()
        before = holder.snapshot()
        with self.assertRaises(reference.Reject):
            holder.build({"bad": float("nan")})
        self.assertEqual(holder.snapshot(), before)
        report = holder.build({})
        self.assertEqual(report["decision"], "DEFER")


class RunTests(unittest.TestCase):
    def test_run_check(self):
        env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run([sys.executable, str(HERE / "run.py"), "check"], cwd=str(HERE), capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertRegex(proc.stdout.strip().splitlines()[-1], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
