import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from check_fixture import order, replay


HERE = Path(__file__).resolve().parent


class ListeningFixtureTest(unittest.TestCase):
    def test_report_preserves_valid_controls_and_failures(self):
        cmd = [sys.executable, str(HERE / "check_fixture.py")]
        raw = subprocess.check_output(cmd)
        self.assertEqual(raw, subprocess.check_output(cmd))
        report = json.loads(raw)
        for name in ("check_fixture.py", "fixture.json", "registration.json"):
            digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            self.assertEqual(report["sha256"][name], digest)
        self.assertEqual(report["kind"], "synthetic_metadata_only")
        self.assertFalse(report["release_qualified"])
        self.assertEqual(report["cleared_playback"], {"status": "not_cleared", "items": 0})
        self.assertEqual(report["ratings"]["human_status"], "not_collected")
        self.assertEqual(report["aggregation"], "per_trial_only_no_pooled_score")

        prepared = report["prepared_listening_sets"]
        self.assertEqual(prepared["media_prepared"], 0)
        plans = prepared["trial_plans"]
        rows = report["ratings"]["mock_only"]
        self.assertEqual({k: (r["status"], r["reason"]) for k, r in rows.items()}, {
            "ab-fan": ("valid", None), "ab-room": ("missing", "missing_response"),
            "ms-fan": ("valid", None), "ms-clean": ("invalid", "invalid_response"),
            "ms-room": ("not_run", "stimuli_not_ready"),
            "ms-reverb": ("not_run", "stimuli_not_ready"),
        })
        self.assertEqual(plans["ms-room"]["status"], "missing")
        self.assertEqual(plans["ms-room"]["missing_conditions"], ["anchor"])
        self.assertEqual(plans["ms-reverb"]["status"], "invalid")
        self.assertEqual(plans["ms-reverb"]["invalid_intervals"], ["candidate"])
        self.assertEqual(plans["ms-clean"]["status"], "metadata_ready")
        for trial in ("ab-room", "ms-clean", "ms-reverb", "ms-room"):
            self.assertIsNone(rows[trial]["result"])

        key = report["fixture_only_unblinding_key"]
        self.assertEqual(key["ab-fan"], {"A": "candidate", "B": "raw"})
        self.assertEqual(key["ms-fan"], {
            "A": "raw", "B": "candidate", "C": "anchor", "D": "baseline", "E": "reference",
        })
        self.assertEqual(set(key), {"ab-fan", "ab-room", "ms-clean", "ms-fan"})
        projection = report["listener_projection_example"]
        self.assertEqual(projection, {
            "ab-fan": ["A", "B"], "ab-room": ["A", "B"],
            "ms-clean": list("ABCDE"), "ms-fan": list("ABCDE"),
        })
        self.assertEqual(rows["ab-fan"]["result"], {"candidate_preferred": 1})
        self.assertEqual(rows["ms-fan"]["result"], {
            "raw": 40, "candidate": 70, "anchor": 20, "baseline": 60, "reference": 95,
        })

    def test_order_is_seeded_and_independent_of_input_order(self):
        conditions = ["raw", "candidate", "baseline", "reference", "anchor"]
        rank = order(20261123, "mushra_style", "ms-fan", conditions)
        self.assertEqual(rank, order(20261123, "mushra_style", "ms-fan", conditions[::-1]))
        self.assertNotEqual(rank, order(20261124, "mushra_style", "ms-fan", conditions))
        with self.assertRaisesRegex(ValueError, "unsupported_ordering"):
            replay({"ordering": "not-registered"}, {})

    def test_tie_and_invalid_responses_are_distinct(self):
        registration = json.loads((HERE / "registration.json").read_bytes())
        fixture = json.loads((HERE / "fixture.json").read_bytes())
        fixture["mock_responses"]["ab-fan"] = "tie"
        fixture["mock_responses"]["ab-room"] = None
        fixture["mock_responses"]["ms-fan"]["E"] = True
        rows = replay(registration, fixture)["ratings"]["mock_only"]
        self.assertEqual(rows["ab-fan"]["result"], {"candidate_preferred": 0})
        self.assertEqual(rows["ab-room"]["status"], "invalid")
        self.assertEqual(rows["ms-fan"]["status"], "invalid")

    def test_cannot_add_an_unregistered_trial_or_swap_a_condition(self):
        registration = json.loads((HERE / "registration.json").read_bytes())
        fixture = json.loads((HERE / "fixture.json").read_bytes())
        fixture["stimulus_metadata"]["ms-room"]["replacement"] = [160, 320]
        row = replay(registration, fixture)["prepared_listening_sets"]["trial_plans"]["ms-room"]
        self.assertEqual((row["status"], row["missing_conditions"], row["unregistered_conditions"]),
                         ("invalid", ["anchor"], ["replacement"]))
        fixture["mock_responses"]["unregistered"] = "A"
        with self.assertRaisesRegex(ValueError, "unregistered_trial"):
            replay(registration, fixture)
