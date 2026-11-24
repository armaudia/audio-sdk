# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest coverage for the task-local STOI/ESTOI evidence adapter."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import fixture
import reference
import run as adapter
import scorer
import verify

ROOT = Path(__file__).resolve().parent
CANONICAL_SHA256 = "1557ea1b0079f4ad5856e15f54add1af5d4fb09f5a0a863ede7f346369598ead"


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.read_strict_json(ROOT / "report.json")
        cls.items, cls.pinned = fixture.cohort()

    def test_01_pins_and_defer_decision(self):
        self.assertEqual(self.report["base_commit"], "a64e1096905f0d05a46303fc0167b6f356027765")
        self.assertEqual(self.report["protocol"], reference.PROTOCOL)
        self.assertEqual(self.report["decision"]["promotion"], "defer")
        for key in ("expose_as_processor", "registered", "default_enabled"):
            self.assertIs(self.report["decision"][key], False)
        self.assertEqual(self.report["scorer"]["pystoi_version"], scorer.PYSTOI_VERSION)
        self.assertEqual(self.report["scorer"]["source_sha256"], scorer.PYSTOI_SOURCE_SHA256)
        self.assertEqual(self.report["fixture"], self.pinned)
        self.assertEqual(self.report["aggregation"]["failed_items"], [])

    def test_02_fixture_digest_pins(self):
        self.assertEqual(fixture.digest(fixture.target()), self.pinned["clean_digest"])
        for kind, expected in self.pinned["masker_digests"].items():
            self.assertEqual(fixture.digest(fixture.masker(kind)), expected)
        self.assertEqual(len(self.items), 6)
        for item in self.items:
            self.assertEqual(item["clean_digest"], self.pinned["clean_digest"])
            self.assertEqual(item["masker_digest"], self.pinned["masker_digests"][item["masker_kind"]])
            self.assertEqual(set(item["variants"]), set(fixture.VARIANTS))

    def test_03_scorer_identity_and_silence_controls(self):
        clean = fixture.target()
        identity = scorer.scores(clean, clean)
        for metric in reference.METRICS:
            self.assertIsNone(identity[metric][1])
            self.assertAlmostEqual(identity[metric][0], 1.0, places=12)
        silence = scorer.scores(clean, [0.0] * fixture.SAMPLES)
        self.assertEqual(silence["stoi"][0], 0.0)
        self.assertEqual(silence["estoi"][1], "degenerate_extended_normalization")

    def test_04_missing_nonfinite_and_short_controls(self):
        expected = {
            "missing": ("blocked", "missing_input"),
            "nonfinite": ("invalid", "nonfinite_input"),
            "short": ("failed", "invalid_geometry"),
        }
        for item in self.report["items"]:
            for variant, (status, reason) in expected.items():
                row = item["variants"][variant]
                self.assertEqual((row["status"], row["reason"]), (status, reason))
                self.assertIsNone(row["metrics"])

    def test_05_paired_deltas_and_metric_difference(self):
        for variant, expected_sign in (
            ("less_masker", 1), ("more_masker", -1), ("tilt", 1), ("gain_only", -1)
        ):
            for metric in reference.METRICS:
                summary = self.report["summaries"][variant][metric]
                self.assertEqual(summary["coverage"], "complete")
                self.assertEqual(summary["paired"], 6)
                self.assertEqual(summary["excluded"], {})
                self.assertGreater(summary["mean_delta"] * expected_sign, 0.0)
        by_kind = self.report["metric_difference"]["identity_noisy_mean_by_masker_kind"]
        self.assertLess(by_kind["steady"], 0.0)
        self.assertGreater(by_kind["modulated"], 0.0)

    def test_06_external_crosscheck_is_recorded_only(self):
        vectors = reference.read_strict_json(ROOT / "crosscheck_vectors.json")
        self.assertEqual(vectors["pystoi_version"], scorer.PYSTOI_VERSION)
        self.assertEqual(vectors["source_sha256"], scorer.PYSTOI_SOURCE_SHA256)
        self.assertEqual(len(vectors["vectors"]), 12)
        for row in vectors["vectors"]:
            self.assertEqual(abs(row["port_stoi"] - row["pystoi_stoi"]), row["abs_delta_stoi"])
            self.assertEqual(abs(row["port_estoi"] - row["pystoi_estoi"]), row["abs_delta_estoi"])
        self.assertEqual(self.report["crosscheck"]["max_abs_delta"], verify.RECORDED_ABS_DELTA)
        self.assertEqual(self.report["crosscheck"]["vectors_sha256"],
                         self._sha256(ROOT / "crosscheck_vectors.json"))

    def test_07_adapter_boundary_validation(self):
        inspect = adapter.inspect(adapter._request("inspect"))
        self.assertIs(inspect["expose_as_processor"], False)
        self.assertIn("unregistered developer-only", inspect["registration"])
        valid = adapter.run(adapter._request("run", "steady-snr+0", "identity_noisy"))
        missing = adapter.run(adapter._request("run", "steady-snr-5", "missing"))
        self.assertEqual(valid["status"], "scored")
        self.assertEqual(missing["status"], "blocked")
        self.assertIs(valid["registered"], False)
        bad_requests = [
            adapter._request("inspect") | {"unexpected": 1},
            adapter._request("inspect") | {"configuration": {"metric_set": "other"}},
            adapter._request("run", "not-an-item", "identity_noisy"),
            adapter._request("run", "steady-snr-5", "identity_noisy", samples=[0.0]),
        ]
        for request in bad_requests:
            with self.assertRaises(adapter.RequestError):
                adapter.inspect(request) if request["operation"] == "inspect" else adapter.run(request)

    def test_08_strict_json_rejects_duplicates_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
            path.write_text('{"a": NaN}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
            path.write_text('[1, 2]\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_09_three_cold_report_repeats(self):
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        outputs = []
        for _ in range(3):
            completed = subprocess.run(
                [sys.executable, str(ROOT / "run.py"), "--report"],
                cwd=ROOT, env=env, check=True, capture_output=True, text=True,
            )
            self.assertEqual(completed.stdout.strip(), CANONICAL_SHA256)
            outputs.append((ROOT / "report.json").read_bytes())
            self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii"),
                             CANONICAL_SHA256 + "\n")
        self.assertEqual(outputs, [outputs[0]] * 3)
        self.assertEqual(self._sha256(ROOT / "report.json"),
                         "a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82")

    @staticmethod
    def _sha256(path: Path) -> str:
        import hashlib
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
