# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for pyannote segmentation/VAD evidence package."""

from __future__ import annotations

import copy
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

    def test_missing_file_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.strict_load(HERE / "missing.json")


class SyntheticControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.control = cls.report["synthetic_control"]

    def test_control_non_qualifying(self):
        self.assertIs(self.control["qualifies_candidate"], False)
        self.assertIs(self.control["not_pyannote"], True)
        self.assertIs(self.control["not_real_audio_corpus"], True)
        self.assertEqual(self.control["metric_scope"], "synthetic_signal_domain_not_a_pyannote_or_corpus_result")

    def test_control_deterministic(self):
        a = reference.synthetic_control()
        b = reference.synthetic_control()
        self.assertEqual(a["probability_digest"], b["probability_digest"])
        self.assertEqual(a["detected_speech_events"], b["detected_speech_events"])
        self.assertEqual(a["counts"], b["counts"])

    def test_control_has_events_and_counts(self):
        self.assertGreaterEqual(len(self.control["detected_speech_events"]), 1)
        counts = self.control["counts"]
        self.assertEqual(counts["tp"] + counts["fp"] + counts["fn"] + counts["tn"], 100)


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
            self.assertIsInstance(v, dict, k)
            self.assertIs(v["measured"], False, k)
            self.assertIsNone(v["value"], k)


class ManifestTests(unittest.TestCase):
    def base(self):
        return reference._base_manifest()

    def test_valid_manifest_normalizes(self):
        m = self.base()
        n = reference.validate_manifest(m)
        self.assertEqual(n["variant"], reference.REQUIRED_VARIANT)
        self.assertEqual(n["channels"], 1)

    def test_missing_field_rejected(self):
        m = self.base(); del m["model_asset_sha256"]
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_extra_field_rejected(self):
        m = self.base(); m["extra"] = 1
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_relative_path_rejected(self):
        m = self.base(); m["model_asset_path"] = "rel/model.bin"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_traversal_rejected(self):
        m = self.base(); m["model_asset_path"] = "/opt/../x.bin"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_bad_sha_rejected(self):
        m = self.base(); m["model_asset_sha256"] = "ZZZ"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_short_revision_rejected(self):
        m = self.base(); m["source_revision"] = "abc"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_nonhex_revision_rejected(self):
        m = self.base(); m["source_revision"] = "g" * 40
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_zero_revision_rejected(self):
        m = self.base(); m["source_revision"] = "0" * 40
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_variant_rejected(self):
        m = self.base(); m["variant"] = "nope"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_capability_false_rejected(self):
        m = self.base(); m["claimed_pyannote_segmentation_vad_capability"] = False
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_channels_rejected(self):
        m = self.base(); m["channels"] = 2
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_sample_rate_rejected(self):
        m = self.base(); m["sample_rate_hz"] = 8000
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_frame_samples_rejected(self):
        m = self.base(); m["frame_samples"] = 320
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_negative_hangover_rejected(self):
        m = self.base(); m["onset_hangover_frames"] = -1
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_threshold_exponent_rejected(self):
        m = self.base(); m["threshold"] = "1e-3"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_threshold_negative_rejected(self):
        m = self.base(); m["threshold"] = "-0.1"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)

    def test_wrong_geometry_rejected(self):
        m = self.base(); m["task_geometry"] = "diarization"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(m)


class FrameAdverseTests(unittest.TestCase):
    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(reference.Reject):
                reference.frame_rms_dbfs([0.0] * 159 + [bad])

    def test_short_long_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([0.0] * 10)
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([0.0] * 161)

    def test_bool_string_out_of_range_rejected(self):
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

    def test_eight_blocked_gates(self):
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(g["blocked"] is True for g in gates))
        self.assertTrue(all(g["status"] == "blocked" for g in gates))

    def test_eight_blockers(self):
        self.assertEqual(len(self.report["exact_blockers"]), 8)

    def test_adverse_all_rejected(self):
        adverse = self.report["controls"]["adverse"]
        self.assertGreaterEqual(len(adverse), 20)
        self.assertTrue(all(a["result"] == "rejected" for a in adverse))
        self.assertTrue(self.report["controls"]["all_adverse_rejected"])

    def test_task_row_identity_stable_and_no_board_hash(self):
        tri = self.report["task_row_identity"]
        self.assertFalse(tri["whole_file_hashed"])
        self.assertNotIn(reference.BOARD_PATH, self.report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, self.report["boundary_pins"])
        self.assertIn("id", tri["stable_fields"])
        self.assertEqual(tri["stable_fields"]["id"], reference.TASK)
        for f in reference.MUTABLE_TASK_FIELDS:
            self.assertIn(f, tri["excluded_mutable_fields"])

    def test_scope_boundary_all_false_except_controlled(self):
        for k, v in self.report["scope"].items():
            if k in ("feature_domain_synthetic_control", "proposal_only", "task_local_only"):
                self.assertIs(v, True, k)
            else:
                self.assertIs(v, False, k)
        for k, v in self.report["boundary"].items():
            self.assertIs(v, False, k)

    def test_no_forbidden_tokens(self):
        text = self.raw.decode("utf-8").lower()
        for tok in ["qualified_success", "release_ready", "production_ready"]:
            self.assertNotIn(tok, text)
        self.assertIn('"candidate_qualified":false', self.raw.decode("utf-8").replace(" ", ""))

    def test_candidate_metrics_null(self):
        cm = self.report["candidate_metrics"]
        self.assertIs(cm["derived_from_synthetic_control"], False)
        for k, v in cm.items():
            if k == "derived_from_synthetic_control":
                continue
            self.assertIsNone(v["value"], k)
            self.assertIs(v["measured"], False, k)

    def test_report_deterministic(self):
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
        self.assertIsNotNone(holder.snapshot())


class RunTests(unittest.TestCase):
    def test_run_check(self):
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run([sys.executable, str(HERE / "run.py"), "check"], cwd=str(HERE), capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertRegex(proc.stdout.strip().splitlines()[-1], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
