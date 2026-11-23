"""Offline acceptance tests for the typed-frame/resample/drift tool fixture.

Run from this directory with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import fixture

ROOT = Path(__file__).resolve().parent
REPORT = json.loads((ROOT / "report.json").read_text(encoding="ascii"))
CONTRACT_BYTES = (ROOT / "contract.json").read_bytes()


def control(case_id: str) -> dict:
    rows = [row for row in REPORT["controls"] if row["id"] == case_id]
    assert len(rows) == 1, f"control {case_id!r} must appear exactly once"
    return rows[0]


def fresh_adapter(**changes):
    raw = fixture.base_config()
    raw.update(changes)
    cfg, status, reason = fixture.parse_config(raw)
    assert status == fixture.Status.OK, f"{status.value}:{reason}"
    return fixture.TypedFrameAdapter(cfg)


class FixtureArtifactTests(unittest.TestCase):
    def test_contract_and_report_artifacts_match_generator(self):
        self.assertEqual(CONTRACT_BYTES, fixture.canonical_bytes(fixture.CONTRACT))
        contract_digest = hashlib.sha256(CONTRACT_BYTES).hexdigest()
        self.assertEqual(REPORT["digests"]["contract_json"], contract_digest)
        self.assertEqual(REPORT["contract_digest"], contract_digest)
        self.assertEqual(REPORT["contract"], fixture.CONTRACT_ID)
        self.assertEqual(REPORT["v0_format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160,
        })

    def test_report_determinism_and_sidecar(self):
        first = fixture.build_report()
        second = fixture.build_report()
        self.assertEqual(first, second)
        self.assertEqual((ROOT / "report.json").read_bytes(), first)
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii"),
                         hashlib.sha256(first).hexdigest() + "\n")

    def test_source_pins_are_recorded_and_reverified(self):
        pins = REPORT["source_pin_verification"]
        self.assertEqual(set(pins), set(fixture.SOURCE_PINS))
        for label, row in pins.items():
            self.assertEqual(row["expected_sha256"], fixture.SOURCE_PINS[label][1])
            path = fixture.WORKSPACE_ROOT / fixture.SOURCE_PINS[label][0]
            if path.is_file():
                self.assertEqual(row["observed_sha256"],
                                 hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertTrue(row["verified"], label)
                self.assertEqual(row["reason"], "")
            else:
                self.assertFalse(row["verified"], label)
                self.assertEqual(row["reason"], "path_unavailable")

    def test_clean_checkout_extracted_package_regeneration(self):
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary)
            for name in ("fixture.py", "generator.py"):
                shutil.copy2(ROOT / name, staged / name)
            environment = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
            completed = subprocess.run(
                [sys.executable, str(staged / "generator.py"),
                 "--output-dir", str(staged), "--install-location", str(ROOT)],
                capture_output=True, text=True, env=environment, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            for name in ("contract.json", "report.json", "report.json.sha256"):
                self.assertEqual((staged / name).read_bytes(), (ROOT / name).read_bytes(),
                                 name)


class WorkedExampleTests(unittest.TestCase):
    def test_typical_api_use_counts_and_clock_map(self):
        counts = REPORT["counts"]
        self.assertEqual(counts["source_frames"], 4)
        self.assertEqual(counts["source_valid_samples"], 1485)
        self.assertEqual(counts["v0_input_frames"], 4)
        self.assertEqual(counts["produced_samples"], 800)
        self.assertEqual(counts["accepted_samples"], 495)
        self.assertEqual(counts["delivered_valid_samples"], 495)
        self.assertEqual(counts["drain_calls"], 1)
        self.assertEqual(counts["rejected_frames"], 0)
        rows = REPORT["clock"]["map"]
        self.assertEqual([row["mapped_target_sample"] for row in rows], [0, 160, 320, 480])
        self.assertEqual([row["v0_first_input_sample"] for row in rows], [0, 160, 320, 480])
        self.assertEqual([row["source_timestamp_ns"] for row in rows],
                         [1_000_000_000, 1_010_000_000, 1_020_000_000, 1_030_000_000])
        self.assertEqual([row["v0_valid_samples"] for row in rows], [160, 160, 160, 15])

    def test_caller_owned_inputs_are_copied(self):
        frame = fixture.make_source_frame(0, 480)
        adapter = fresh_adapter()
        converted = adapter.convert(frame)
        self.assertEqual(converted.status, fixture.Status.OK)
        original = tuple(converted.frame.samples)
        self.assertIsNot(converted.frame.samples, frame.values)
        frame.values[0] = 32000
        frame.values[-1] = -32000
        self.assertEqual(tuple(converted.frame.samples), original)

    def test_measured_delay_matches_declared(self):
        probe = REPORT["delay"]
        self.assertEqual(probe["status"], fixture.Status.OK.value)
        self.assertEqual(probe["method"], "synthetic_impulse_source_coordinate_probe")
        self.assertEqual(probe["declared_delay_samples"], fixture.DELAY_SAMPLES)
        self.assertEqual(probe["measured_delay_samples"], fixture.DELAY_SAMPLES)
        self.assertEqual(probe["first_valid_global_output_index"], 173)
        self.assertEqual(probe["valid_offset_within_frame"], 13)
        self.assertEqual(probe["observed_impulse_amplitude"], 1.0)

    def test_partial_final_and_interval_conservation(self):
        intervals = [tuple(pair) for pair in REPORT["source_intervals"]]
        self.assertEqual(intervals, [(0, 147), (147, 307), (307, 467), (467, 495)])
        cursor = 0
        for start, end in intervals:
            self.assertEqual(start, cursor, "valid intervals must be gapless and non-overlapping")
            self.assertLess(start, end)
            cursor = end
        self.assertEqual(cursor, REPORT["counts"]["delivered_valid_samples"])

    def test_finite_tail_accounting_and_non_content(self):
        tail = REPORT["finite_tail"]
        self.assertEqual(tail["startup_non_content_samples"], 173)
        self.assertEqual(tail["tail_non_content_samples"], 132)
        self.assertLessEqual(tail["tail_non_content_samples"], tail["tail_budget_samples"])
        self.assertEqual(tail["concealment_frames"], 0)
        self.assertEqual(
            REPORT["counts"]["produced_samples"],
            REPORT["counts"]["delivered_valid_samples"]
            + tail["startup_non_content_samples"] + tail["tail_non_content_samples"],
        )
        self.assertEqual(control("finite_tail_accounting")["observed"], "ok")

    def test_output_digest_is_stable(self):
        run = fixture.run_worked_example()
        self.assertEqual(run.final_result.status, fixture.Status.END_OF_STREAM)
        self.assertEqual(run.session.digest(), REPORT["digests"]["v0_output_f32_le"])
        self.assertEqual(run.source_digest, REPORT["digests"]["source_pcm_s16_le"])

    def test_reset_and_repeated_drain(self):
        run = fixture.run_worked_example()
        self.assertEqual(run.session.drain_next().status, fixture.Status.END_OF_STREAM)
        self.assertEqual(run.session.reset(2, 0), fixture.Status.OK)
        stale = run.session.process(fixture.V0Frame((0.0,) * 160, 0, 1, 160))
        self.assertEqual(stale.status, fixture.Status.REJECTED_STALE_EPOCH)
        accepted = run.session.process(fixture.V0Frame((0.0,) * 160, 0, 2, 160))
        self.assertEqual(accepted.status, fixture.Status.OK)


class AdverseControlTests(unittest.TestCase):
    def test_wrong_sample_rate_control(self):
        row = control("wrong_sample_rate")
        self.assertEqual(row["observed"], "rejected_sample_rate")
        self.assertTrue(row["pass"])

    def test_wrong_channel_control(self):
        row = control("wrong_channel")
        self.assertEqual(row["observed"], "rejected_channels")
        self.assertTrue(row["pass"])

    def test_wrong_frame_shape_control(self):
        self.assertEqual(control("wrong_frame_shape")["observed"], "rejected_bad_frame_shape")

    def test_nonfinite_input_control(self):
        self.assertEqual(control("nonfinite_input")["observed"], "rejected_nonfinite_input")

    def test_wrong_clock_domain_and_timestamp_controls(self):
        self.assertEqual(control("wrong_clock_domain")["observed"], "rejected_clock_domain")
        self.assertEqual(control("wrong_clock_timestamp")["observed"], "rejected_clock_domain")

    def test_missing_optional_selection_control(self):
        self.assertEqual(control("missing_optional_selection")["observed"],
                         "rejected_missing_selection")

    def test_malformed_config_control(self):
        self.assertEqual(control("malformed_config")["observed"], "rejected_bad_config")

    def test_stale_epoch_control(self):
        self.assertEqual(control("stale_epoch")["observed"], "rejected_stale_epoch")

    def test_duplicate_source_timestamp_control(self):
        self.assertEqual(control("duplicate_source_timestamp")["observed"],
                         "rejected_duplicate_timestamp")

    def test_drift_beyond_declared_bound_control(self):
        self.assertEqual(control("drift_beyond_declared_bound")["observed"],
                         "rejected_drift_bound")

    def test_tail_overrun_control(self):
        self.assertEqual(control("finite_tail_noncontent_overrun")["observed"],
                         "rejected_tail_overrun")

    def test_no_missing_or_unrun_controls(self):
        required = {
            "wrong_sample_rate", "wrong_channel", "wrong_frame_shape", "nonfinite_input",
            "wrong_clock_domain", "wrong_clock_timestamp", "missing_optional_selection",
            "malformed_config", "stale_epoch", "duplicate_source_timestamp",
            "drift_beyond_declared_bound", "finite_tail_noncontent_overrun",
            "finite_tail_accounting",
        }
        observed = {row["id"] for row in REPORT["controls"]}
        self.assertEqual(observed, required)
        forbidden = {"missing", "not_run", "skipped", "untested", "unknown"}
        for row in REPORT["controls"]:
            self.assertNotIn(row["observed"], forbidden, row["id"])
            self.assertTrue(row["pass"], f"{row['id']}: {row['detail']}")
        self.assertEqual(REPORT["counts"]["controls_total"], len(required))
        self.assertEqual(REPORT["counts"]["controls_passed"], len(required))
        self.assertEqual(REPORT["counts"]["controls_missing"], 0)


class ProfileAndBoundaryTests(unittest.TestCase):
    def test_evidence_layers_and_explicit_non_claims(self):
        layers = REPORT["evidence_layers"]
        self.assertEqual(layers["compile_build"]["status"], "not_applicable_model_free")
        self.assertEqual(layers["synthetic_runtime"]["status"], "complete")
        self.assertEqual(layers["measured_workload"]["status"], "blocked_not_run")
        self.assertEqual(REPORT["status"], "proposal_only_synthetic")
        self.assertEqual(REPORT["qualification"], "incomplete")
        self.assertTrue(REPORT["blockers"])
        self.assertTrue(REPORT["non_claims"])
        tool = REPORT["tool_profile"]
        self.assertEqual(tool["acceptance_profile"], "Tool")
        self.assertEqual(tool["version"], fixture.TOOL_VERSION)
        self.assertEqual(tool["provenance"]["base_commit"], fixture.BASE_COMMIT)
        self.assertTrue(tool["typical_api_use"]["verified"])
        self.assertTrue(tool["caller_owned_inputs"]["verified"])
        self.assertTrue(tool["clean_checkout_or_extracted_package"]["verified"])


if __name__ == "__main__":
    unittest.main()
