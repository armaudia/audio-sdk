# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for synthetic distil-wav2vec2 adult/child ridge fixture."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
sys.path.insert(0, str(HERE))

import reference as ref  # noqa: E402

REPORT = HERE / "report.json"
PINS = HERE / "SOURCES.sha256"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def strict_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


class TestPins(unittest.TestCase):
    def test_source_pins(self):
        for pin in ref.SOURCE_PINS:
            root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
            p = root / pin["path"]
            self.assertTrue(p.is_file(), p)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), pin["sha256"])

    def test_sha_manifest_format(self):
        for line in PINS.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            self.assertTrue(name)

    def test_spdx(self):
        for p in HERE.glob("*.py"):
            head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_L, head)
            self.assertIn(SPDX_C, head)


class TestDeterminism(unittest.TestCase):
    def test_report_bytes_stable(self):
        b1 = ref.canonical_report_bytes(ref.build_report())
        b2 = ref.canonical_report_bytes(ref.build_report())
        self.assertEqual(b1, b2)

    def test_cohort_digest_stable(self):
        a = ref.build_report()["cohort"]["held_out_digest"]
        b = ref.build_report()["cohort"]["held_out_digest"]
        self.assertEqual(a, b)


class TestReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = strict_json(REPORT)

    def test_status_and_gates(self):
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertTrue(all(g["status"] == "blocked" for g in self.report["gates"]))

    def test_boundary(self):
        b = self.report["boundary"]
        self.assertFalse(b["registered"])
        self.assertFalse(b["enabled_by_default"])
        self.assertEqual(b["descriptor_settings"], {})
        self.assertEqual((b["sample_rate_hz"], b["channels"], b["frame_samples"]), (16000, 1, 160))

    def test_cohort_and_split(self):
        c = self.report["cohort"]
        self.assertEqual(c["train_clips"], 120)
        self.assertEqual(c["held_out_clips"], 60)
        self.assertEqual(self.report["training"]["n_train"], 120)
        self.assertEqual(self.report["training"]["n_held_out"], 60)

    def test_confusion_and_strata(self):
        conf = self.report["held_out"]["confusion"]
        for k in ["tp","fp","tn","fn","fn_rate","fp_rate"]:
            self.assertIn(k, conf)
        strat = self.report["held_out"]["stratified"]
        self.assertIn("by_stratum", strat)
        self.assertIn("by_ground_truth_label", strat)
        self.assertTrue(strat["by_stratum"])

    def test_onset_offset(self):
        d = self.report["held_out"]["onset_offset_delay"]
        self.assertIn("onset_delay_samples", d)
        self.assertIn("offset_delay_samples", d)
        self.assertIn("ground_truth_child_runs", d)
        self.assertIn("predicted_child_runs", d)

    def test_controls(self):
        self.assertIn("always_adult", self.report["controls"])
        self.assertIn("always_child", self.report["controls"])

    def test_validity(self):
        v = self.report["validity"]
        self.assertTrue(v["all_invalid_rejected"])
        self.assertTrue(v["unknown_not_counted_as_nonspeech"])

    def test_state_cross_hop(self):
        s = self.report["state_and_cross_hop"]
        self.assertTrue(s["session_independence"])
        self.assertTrue(s["stale_epoch_rejected"])
        self.assertTrue(s["reset_epoch_accepted"])
        self.assertTrue(s["cross_hop"])

    def test_missing_evidence_recorded(self):
        paths = [m["path"] for m in self.report["missing_evidence"]]
        self.assertIn("ml-audio-research-experience.md", paths)
        self.assertIn("research/speech_intelligence_20261028.md", paths)

    def test_no_real_model(self):
        m = self.report["model"]
        self.assertFalse(m["weights_downloaded"])
        self.assertFalse(m["weights_executed"])


class TestValidityUnit(unittest.TestCase):
    def test_reject_bad_prob(self):
        e = {"event_id":"e","producer_id":"p","tap_id":"t","epoch":"1","source_first_sample":"0","source_last_sample_exclusive":"160","available_ns":"1","clock_id":"c","validity":"known","prob_child":1.5,"prob_adult":-0.5,"predicted_label":"child"}
        with self.assertRaises(ValueError):
            ref.validate_event(e)

    def test_reject_empty_interval(self):
        e = {"event_id":"e","producer_id":"p","tap_id":"t","epoch":"1","source_first_sample":"160","source_last_sample_exclusive":"160","available_ns":"1","clock_id":"c","validity":"unknown"}
        with self.assertRaises(ValueError):
            ref.validate_event(e)


if __name__ == "__main__":
    unittest.main()
