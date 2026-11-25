# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the frozen-feature rate-profile fixture."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5])))
sys.path.insert(0, str(HERE))

import reference as ref  # noqa: E402

REPORT = HERE / "report.json"
PINS = HERE / "SOURCES.sha256"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
FORBIDDEN_FIELDS = (
    "prob_child", "prob_adult", "predicted_label", "ground_truth_label",
    "fn_rate", "fp_rate", "balanced_error", "threshold_grid",
)


def strict_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


class TestPins(unittest.TestCase):
    def test_source_pins(self):
        for pin in ref.SOURCE_PINS:
            root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
            path = root / pin["path"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin["sha256"])

    def test_research_pin_is_present(self):
        paths = [pin["path"] for pin in ref.SOURCE_PINS]
        self.assertIn("research/tsm-followup-20261101/README.md", paths)

    def test_sha_manifest_format(self):
        for line in PINS.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            self.assertTrue(name)

    def test_spdx(self):
        for path in HERE.glob("*.py"):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_L, head)
            self.assertIn(SPDX_C, head)


class TestDeterminism(unittest.TestCase):
    def test_report_bytes_stable(self):
        first = ref.canonical_report_bytes(ref.build_report())
        second = ref.canonical_report_bytes(ref.build_report())
        self.assertEqual(first, second)

    def test_digests_stable(self):
        report = ref.build_report()
        self.assertEqual(report["cohort"]["label_digest"], ref.build_report()["cohort"]["label_digest"])
        self.assertEqual(report["held_out"]["events_digest"], ref.build_report()["held_out"]["events_digest"])

    def test_three_cold_starts_match_report_and_sidecar(self):
        expected = REPORT.read_bytes()
        command = [sys.executable, "-B", "-c",
                   "import sys, reference as r; "
                   "sys.stdout.buffer.write(r.canonical_report_bytes(r.build_report()))"]
        for _ in range(3):
            self.assertEqual(subprocess.check_output(command, cwd=HERE, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}), expected)
        self.assertEqual((HERE / "report.json.sha256").read_text(),
                         hashlib.sha256(expected).hexdigest() + "  report.json\n")

    def test_runner_writes_to_scratch_without_touching_tracked_files(self):
        tracked = [HERE / "report.json", HERE / "report.json.sha256"]
        before = [(path.read_bytes(), path.stat().st_mtime_ns) for path in tracked]
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch) / "report.json"
            result = subprocess.run([sys.executable, "-B", str(HERE / "run.py"), str(output)],
                                    cwd=HERE, capture_output=True, text=True,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), before[0][0])
            self.assertEqual(output.with_suffix(".json.sha256").read_bytes(), before[1][0])
        self.assertEqual([(path.read_bytes(), path.stat().st_mtime_ns) for path in tracked], before)


class TestReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = strict_json(REPORT)

    def test_status_and_gates(self):
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertTrue(all(g["status"] == "blocked" for g in self.report["gates"]))

    def test_rate_task_and_no_classification_fields(self):
        self.assertEqual(self.report["task"]["kind"], "measured_syllable_rate_regression")
        self.assertEqual(self.report["task"]["target_unit"], "syllables_per_second")
        self.assertIsNone(self.report["task"]["rate_to_speed_factor_policy"])
        for claim in ("adult_child_classification", "age_or_preferred_speed_prediction"):
            self.assertIn(claim, self.report["task"]["excluded_claims"])
        text = REPORT.read_text(encoding="utf-8")
        for field in FORBIDDEN_FIELDS:
            self.assertNotIn(field, text)
        self.assertFalse(self.report["model"]["classifier_head_used"])

    def test_documented_context_is_not_a_local_claim(self):
        context = self.report["model"]["documented_context_not_reproduced"]
        self.assertFalse(context["reproduced_here"])
        self.assertEqual((context["mae_syllables_per_second"], context["rmse_syllables_per_second"],
                          context["pearson_r"]), (0.741, 0.929, 0.768))
        self.assertEqual(context["mean_encoder_ms_per_4s_clip"], 157.0)
        self.assertFalse(self.report["model"]["weights_downloaded"])
        self.assertFalse(self.report["model"]["weights_executed"])

    def test_boundary(self):
        boundary = self.report["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertFalse(boundary["public_api_abi_change"])
        self.assertEqual((boundary["sample_rate_hz"], boundary["channels"], boundary["frame_samples"]),
                         (16000, 1, 160))
        self.assertEqual(boundary["window_samples"], 64000)

    def test_cohort_and_folds(self):
        cohort = self.report["cohort"]
        self.assertEqual(cohort["windows"], 210)
        self.assertEqual(cohort["folds"], 5)
        self.assertEqual(cohort["windows_per_fold"], 42)
        self.assertTrue(cohort["labels_matched_to_caller_features_by_latent"])
        self.assertFalse(cohort["real_audio"])
        self.assertEqual(self.report["training"]["oof_nonnegative"]["count"], 168)
        self.assertEqual(len(self.report["training"]["folds"]), 4)

    def test_profile_and_fold_separation(self):
        self.assertEqual(self.report["profile"], "rate")
        training = self.report["training"]
        self.assertEqual(training["calibration_folds"], [0, 1, 2, 3])
        self.assertEqual(training["evaluation_fold"], self.report["held_out"]["fold"])
        self.assertEqual(training["evaluation_fold"], 4)
        self.assertFalse(training["evaluation_fold_used_for_alpha_selection"])
        self.assertNotIn(4, [fold["fold"] for fold in training["folds"]])
        self.assertFalse(self.report["held_out"]["evaluation_labels_used_in_fit"])
        self.assertFalse(self.report["held_out"]["evaluation_labels_used_for_alpha_selection"])
        train = [w for w in ref.build_windows() if w.fold in (0, 1, 2, 3)]
        expected_mean = sum(w.label_rate for w in train) / len(train)
        self.assertAlmostEqual(self.report["held_out"]["train_mean_label_syllables_per_second"],
                               expected_mean, places=8)
        # A baseline fitted on evaluation truth would reproduce its mean exactly.
        held_mean = sum(w.label_rate for w in ref.build_windows() if w.fold == 4) / 42
        self.assertNotAlmostEqual(expected_mean, held_mean, places=3)

    def test_exact_decimal_intervals(self):
        for event in self.report["held_out"]["events"]:
            for field in ("epoch", "source_first_sample", "source_last_sample_exclusive", "available_ns"):
                raw = event[field]
                self.assertIsInstance(raw, str)
                self.assertTrue(raw.isdigit())
                self.assertEqual(str(int(raw)), raw)
            ref.validate_event(event)
            first = int(event["source_first_sample"])
            last = int(event["source_last_sample_exclusive"])
            self.assertEqual(last - first, 64000)
            self.assertEqual(int(event["available_ns"]), ref.ORIGIN_NS + last * ref.SAMPLE_NS)

    def test_cross_hop_coverage_is_contiguous(self):
        chains = self.report["state_and_cross_hop"]["cross_hop"]
        self.assertEqual(set(chains), {"session_a", "session_b"})
        for chain in chains.values():
            self.assertTrue(chain["exact_half_open_interval"])
            self.assertTrue(chain["exact_window_samples"])
            self.assertEqual(chain["frames_covered"], [400, 400, 400])
            self.assertEqual(chain["contiguous_transitions"], 2)
            self.assertEqual(chain["gap_count"], 0)
            self.assertEqual(chain["overlap_count"], 0)
            self.assertEqual(chain["total_source_samples"], 3 * 64000)
        self.assertEqual(chains["session_b"]["first_sample"],
                         chains["session_a"]["last_sample_exclusive"])

    def test_caller_identity_and_mismatch_controls(self):
        identity = self.report["model"]["identity_control"]
        self.assertEqual(identity["calls"], 882)
        self.assertEqual(identity["identity_pairs_checked"], 882)
        self.assertEqual(identity["distinct_caller_vectors"], 210)
        self.assertTrue(identity["all_caller_vectors_returned_unchanged"])
        self.assertTrue(identity["all_caller_vectors_match_pinned_digests"])
        adverse = self.report["controls"]["permutation_adverse"]
        self.assertTrue(adverse["strict_gate_rejected"])
        self.assertTrue(adverse["metrics_are_unaccepted"])
        self.assertTrue(adverse["worse_than_identity"])

    def test_identity_flag_tracks_actual_returned_vectors(self):
        windows = ref.build_windows()
        identity = ref.IdentityExtractor()
        reversed_extractor = ref.ReversedExtractor()
        for window in windows:
            identity(window.features)
            reversed_extractor(window.features)
        good = ref.identity_control_record(identity, windows)
        bad = ref.identity_control_record(reversed_extractor, windows)
        self.assertTrue(good["all_caller_vectors_returned_unchanged"])
        self.assertFalse(bad["all_caller_vectors_returned_unchanged"])
        self.assertEqual(bad["identity_pairs_checked"], len(windows))
        self.assertEqual(bad["calls"], len(windows))

    def test_metrics_are_wiring_evidence_only(self):
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["synthetic_wiring_mae_rmse_r"], "wiring_only_not_accuracy")
        self.assertEqual(classes["rate_policy_conditions"], "none")
        self.assertEqual(classes["speech_preservation"], "none")
        self.assertIn("wiring", self.report["training"]["note"].lower())

    def test_all_required_gates_blocked(self):
        gate_ids = {gate["id"] for gate in self.report["gates"]}
        for gate_id in ("model_revision_and_rights", "real_frozen_extractor_and_head",
                        "rights_qualified_labeled_audio", "external_accuracy_generalization",
                        "preferred_speed_claim", "target_runtime_timing",
                        "rate_profile_condition_coverage", "source_output_mapping_and_preservation",
                        "provider_intake"):
            self.assertIn(gate_id, gate_ids)

    def test_regression_metrics(self):
        for section in (self.report["training"]["oof_raw"], self.report["held_out"]["nonnegative"]):
            for key in ("mae_syllables_per_second", "rmse_syllables_per_second",
                        "bias_syllables_per_second", "pearson_r"):
                self.assertIn(key, section)
        self.assertLess(self.report["held_out"]["nonnegative"]["mae_syllables_per_second"],
                        self.report["held_out"]["constant_train_mean"]["mae_syllables_per_second"])

    def test_events_are_exact_and_finite(self):
        events = self.report["held_out"]["events"]
        self.assertEqual(len(events), 3)
        for event in events:
            ref.validate_event(event)
            start = int(event["source_first_sample"])
            end = int(event["source_last_sample_exclusive"])
            self.assertEqual(end - start, 64000)
            self.assertGreaterEqual(event["rate_syllables_per_second"], 0.0)

    def test_controls(self):
        controls = self.report["controls"]
        self.assertEqual(controls["identity_caller_features"]["status"], "pass")
        self.assertTrue(self.report["model"]["identity_control"]["all_caller_vectors_returned_unchanged"])
        self.assertEqual(controls["permutation_adverse"]["status"], "expected_failure")
        self.assertTrue(controls["permutation_adverse"]["worse_than_identity"])
        self.assertEqual(controls["constant_train_mean"]["status"], "reference_failure")
        self.assertGreater(controls["permutation_adverse"]["nonnegative"]["mae_syllables_per_second"],
                           self.report["held_out"]["nonnegative"]["mae_syllables_per_second"])

    def test_validation_rejections(self):
        validation = self.report["validation"]
        self.assertTrue(validation["all_rejected"])
        self.assertTrue(validation["unknown_retained"])
        names = {case["name"] for case in validation["cases"]}
        for expected in ("missing_feature_extractor", "extractor_nan", "extractor_inf",
                         "missing_label", "label_nan", "nonfinite_rate", "empty_interval",
                         "misaligned_interval", "stale_epoch", "invalid_validity"):
            self.assertIn(expected, names)

    def test_state_cross_hop(self):
        state = self.report["state_and_cross_hop"]
        self.assertTrue(state["session_keys_disjoint"])
        self.assertTrue(state["stale_epoch_rejected"])
        self.assertTrue(state["reset_epoch_accepted"])
        self.assertTrue(state["cross_hop"])

    def test_missing_evidence_recorded(self):
        paths = [entry["path"] for entry in self.report["missing_evidence"]]
        self.assertIn("ml-audio-research-experience.md", paths)
        self.assertIn("research/speech_intelligence_20261028.md", paths)


class TestValidationUnits(unittest.TestCase):
    def test_reject_missing_and_nonfinite_features(self):
        extractor = ref.IdentityExtractor()
        with self.assertRaisesRegex(ValueError, "missing_features"):
            ref.extract_features(extractor, None)
        with self.assertRaisesRegex(ValueError, "nonfinite_feature"):
            ref.extract_features(extractor, [float("nan")] + [0.0] * (ref.EMBED_DIM - 1))
        with self.assertRaisesRegex(ValueError, "bad_feature_dimension"):
            ref.extract_features(extractor, [0.0] * (ref.EMBED_DIM - 1))

    def test_reject_nonfinite_label_and_rate(self):
        window = ref.build_windows()[0]
        with self.assertRaisesRegex(ValueError, "nonfinite_label"):
            ref.validate_label(float("nan"))
        with self.assertRaisesRegex(ValueError, "nonfinite_rate"):
            ref.build_event(window, float("inf"))
        event = ref.build_event(window, 3.0)
        bad = dict(event, rate_syllables_per_second=float("nan"))
        with self.assertRaisesRegex(ValueError, "bad_rate"):
            ref.validate_event(bad)

    def test_unknown_validity_is_not_scored(self):
        window = ref.build_windows()[0]
        known = ref.build_event(window, 3.0)
        unknown = dict(known, validity="unknown", rate_syllables_per_second=None)
        ref.validate_event(unknown)
        self.assertEqual(unknown["validity"], "unknown")
        self.assertIsNone(unknown["rate_syllables_per_second"])

    def test_reject_wrong_window_and_availability(self):
        window = ref.build_windows()[0]
        event = ref.build_event(window, 3.0)
        short = dict(event, source_last_sample_exclusive=ref.dec(
            int(event["source_first_sample"]) + ref.WINDOW_SAMPLES - ref.FRAME_SAMPLES))
        with self.assertRaisesRegex(ValueError, "wrong_window_samples"):
            ref.validate_event(short)
        late = dict(event, available_ns=ref.dec(int(event["available_ns"]) + 1))
        with self.assertRaisesRegex(ValueError, "available_ns_mismatch"):
            ref.validate_event(late)
        signed = dict(event, source_first_sample="+" + str(int(event["source_first_sample"])))
        with self.assertRaisesRegex(ValueError, "non_decimal_source_first_sample"):
            ref.validate_event(signed)

    def test_reject_caller_vector_mismatches(self):
        window = ref.build_windows()[0]
        good = window.features
        digest = ref.tensor_digest(good)

        class WrongModel(ref.IdentityExtractor):
            def __init__(self) -> None:
                super().__init__(model_id="other-model")

        class WrongRevision(ref.IdentityExtractor):
            def __init__(self) -> None:
                super().__init__(revision="unpinned")

        with self.assertRaisesRegex(ValueError, "extractor_identity_mismatch"):
            ref.extract_features(WrongModel(), good, digest)
        with self.assertRaisesRegex(ValueError, "extractor_revision_mismatch"):
            ref.extract_features(WrongRevision(), good, digest)
        with self.assertRaisesRegex(ValueError, "caller_vector_identity_mismatch"):
            ref.extract_features(ref.ReversedExtractor(), good, digest)
        with self.assertRaisesRegex(ValueError, "caller_vector_digest_mismatch"):
            ref.extract_features(ref.IdentityExtractor(), tuple(reversed(good)), digest)

    def test_hop_chain_detects_gaps_and_overlaps(self):
        windows = ref.build_windows()
        first, third = ref.build_event(windows[0], 3.0), ref.build_event(windows[2], 3.0)
        gapped = ref.hop_chain([first, third])
        self.assertFalse(gapped["exact_half_open_interval"])
        self.assertEqual(gapped["gap_count"], 1)
        overlap_first = int(first["source_last_sample_exclusive"]) - ref.FRAME_SAMPLES
        overlap_last = overlap_first + ref.WINDOW_SAMPLES
        overlap = dict(third, source_first_sample=ref.dec(overlap_first),
                       source_last_sample_exclusive=ref.dec(overlap_last),
                       available_ns=ref.dec(ref.ORIGIN_NS + overlap_last * ref.SAMPLE_NS))
        overlapped = ref.hop_chain([first, overlap])
        self.assertEqual(overlapped["overlap_count"], 1)


class TestPortability(unittest.TestCase):
    def test_canonical_bytes_quantize_floats(self):
        self.assertEqual(ref.canonical_bytes({"v": 1.0000000004}), b'{\n  "v": 1.0\n}\n')
        self.assertEqual(ref.canonical_bytes({"v": -0.0}), b'{\n  "v": 0.0\n}\n')

    def test_runtime_guard(self):
        with mock.patch.object(ref, "sys", SimpleNamespace(version_info=(3, 9, 0))):
            with self.assertRaisesRegex(RuntimeError, "unsupported_runtime"):
                ref.require_supported_runtime()
        with mock.patch.object(ref, "sys", SimpleNamespace(version_info=(3, 10, 0))):
            self.assertEqual(ref.require_supported_runtime(), (3, 10, 0))

    def test_cross_version_canonical_bytes(self):
        candidates = [Path(f"/Users/htsakanyan/.pyenv/versions/{tag}/bin/python3")
                      for tag in ("3.10.13", "3.11.5", "3.12.16")]
        found = [path for path in candidates if path.is_file()]
        if len(found) < 2:
            self.assertIn("3.10.13/3.11.5/3.12.16",
                          (HERE / "README.md").read_text(encoding="utf-8"))
            return
        command = ("import sys, reference as r; "
                   "sys.stdout.buffer.write(r.canonical_report_bytes(r.build_report()))")
        for path in found:
            output = subprocess.check_output(
                [str(path), "-B", "-c", command], cwd=HERE,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(output, REPORT.read_bytes(), path)


if __name__ == "__main__":
    unittest.main()
