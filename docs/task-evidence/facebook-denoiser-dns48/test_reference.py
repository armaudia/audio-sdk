# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, offline unittest suite for the DNS48 evidence package.

No network, no model, no weights, no runtime and no real audio. Every test is
task-local and must pass without skips.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"x":1,"x":2}')

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"x":NaN}')

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"x":Infinity}')

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.load_strict_json_text("[1]")

    def test_canonical_text_is_sorted_and_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": 2}),
                         '{"a":2,"b":1}')


class PinTests(unittest.TestCase):
    def test_source_pins_match_workspace(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            full = reference.SOURCE_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)

    def test_boundary_pins_match_worktree(self) -> None:
        for path, digest in reference.BOUNDARY_PINS.items():
            full = reference.SDK_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)

    def test_no_mutable_task_board_pin(self) -> None:
        every = list(reference.SOURCE_PINS) + list(reference.BOUNDARY_PINS)
        self.assertFalse(any(path.endswith("TASKS.json") for path in every))

    def test_board_row_stable_identity_only(self) -> None:
        row = reference.board_row()
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         reference.BOARD_ROW_STABLE_SHA256)


class FixtureTests(unittest.TestCase):
    def test_fixture_is_repeatable(self) -> None:
        first = reference.build_fixture()
        second = reference.build_fixture()
        self.assertEqual(first, second)

    def test_fixture_geometry(self) -> None:
        spec = reference.fixture_spec()
        self.assertEqual(spec["length_samples"], reference.FIXTURE_LENGTH)
        self.assertEqual(spec["segments"][0]["start"], 0)
        self.assertEqual(spec["segments"][-1]["end"],
                         reference.FIXTURE_LENGTH)
        reference.validate_fixture(spec)

    def test_fixture_is_bounded_q15(self) -> None:
        signals = reference.build_fixture()
        for name in ("clean", "noise", "mic"):
            self.assertTrue(all(-32768 <= value <= 32767
                                for value in signals[name]), name)

    def test_bad_fixture_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture({"length_samples": 16000,
                                        "segments": []})


class SurrogateTests(unittest.TestCase):
    def test_surrogate_is_not_candidate(self) -> None:
        report = reference.build_report()
        surrogate = report["surrogate"]
        for key in ("is_facebook_denoiser", "is_demucs", "is_learned",
                    "uses_network", "uses_weight_file", "uses_convolution",
                    "uses_quantization", "is_generative",
                    "qualifies_candidate"):
            self.assertFalse(surrogate[key], key)

    def test_state_size_and_determinism(self) -> None:
        gate = reference.CausalTwoWindowGateSurrogate(epoch=1)
        self.assertEqual(gate.state_bytes, 28)
        frame = [0.25] * reference.FRAME_SAMPLES
        _, first = gate.process_frame(frame)
        fresh = reference.CausalTwoWindowGateSurrogate(epoch=1)
        _, second = fresh.process_frame(frame)
        self.assertEqual(first, second)
        self.assertEqual(gate.state_digest, fresh.state_digest)

    def test_zero_state_is_monotonic(self) -> None:
        gate = reference.CausalTwoWindowGateSurrogate(epoch=1)
        before = gate.state_digest
        gate.process_frame([0.0] * reference.FRAME_SAMPLES)
        self.assertNotEqual(before, gate.state_digest)
        self.assertEqual(gate.position, reference.FRAME_SAMPLES)

    def test_chunked_stream_matches_offline(self) -> None:
        offline = reference.fixture_run()
        streamed = reference.streaming_check(offline)
        self.assertTrue(streamed["all_match"])
        self.assertEqual(streamed["offline_state_digest"],
                         streamed["streamed_state_digest"])

    def test_reset_matches_fresh(self) -> None:
        self.assertTrue(reference.reset_check()["matches_fresh"])

    def test_final_partial_padding(self) -> None:
        partial = reference.final_partial_check()
        self.assertTrue(partial["padding_zero"])
        self.assertTrue(partial["tail_zero"])
        self.assertEqual(partial["advanced_samples"],
                         reference.FINAL_PARTIAL_VALID)
        self.assertEqual(partial["output_samples"], reference.FRAME_SAMPLES)

    def test_nonfinite_input_rejected_without_state_change(self) -> None:
        gate = reference.CausalTwoWindowGateSurrogate(epoch=1)
        before = gate.state_digest
        frame = [0.0] * reference.FRAME_SAMPLES
        frame[3] = float("nan")
        with self.assertRaises(reference.ReferenceRejection):
            gate.process_frame(frame)
        self.assertEqual(before, gate.state_digest)


class MetricTests(unittest.TestCase):
    def test_si_sdr_identical_is_ceiling(self) -> None:
        values = [100, -200, 300, -400]
        self.assertEqual(reference.si_sdr_millidb(values, values, 0,
                                                  len(values)),
                         reference.MAX_MILLIDB)

    def test_si_sdr_scaled_is_high(self) -> None:
        values = [100, -200, 300, -400]
        scaled = [value * 2 for value in values]
        self.assertGreater(reference.si_sdr_millidb(values, scaled, 0,
                                                    len(values)), 60000)

    def test_snr_identical_is_ceiling(self) -> None:
        values = [100, -200, 300, -400]
        self.assertEqual(reference.snr_millidb(values, values, 0, len(values)),
                         reference.MAX_MILLIDB)

    def test_metrics_are_exact_integers(self) -> None:
        signals = reference.build_fixture()
        start, end = 0, 2400
        value = reference.si_sdr_millidb(signals["clean"], signals["mic"],
                                         start, end)
        self.assertIsInstance(value, int)


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = reference.build_report()

    def test_identity_and_status(self) -> None:
        report = self.report
        self.assertEqual(report["task"], reference.TASK_ID)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(report["branch"], reference.BRANCH)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")

    def test_eight_release_gates_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_qualification_never_true(self) -> None:
        qualification = self.report["qualification"]
        self.assertFalse(qualification["qualifies"])
        self.assertFalse(qualification["all_required_results_present"])
        self.assertFalse(qualification["missing_result_promoted"])
        for key, value in qualification.items():
            if key in {"status", "reason"}:
                continue
            self.assertIs(value, False, key)

    def test_profile_items_are_not_promoted(self) -> None:
        items = self.report["acceptance_profile"]["required_items"]
        self.assertEqual(set(items), {
            "identity_noisy_control", "task_matched_baseline",
            "paired_si_sdr", "paired_stoi", "clean_speech_preservation",
            "peaks_and_invalid_outputs",
            "unpaired_predictive_screen_or_listening",
            "alignment_content_mapping", "runtime_availability_timing",
            "streaming_state_and_reset", "runtime_memory",
            "task_matched_heldout_qualification",
        })
        for name, item in items.items():
            self.assertIn(item["status"], {"synthetic_only", "blocked"}, name)
        self.assertIn("task_matched_heldout_qualification",
                      self.report["profile_blockers"])

    def test_stoi_baseline_listening_are_blocked(self) -> None:
        self.assertEqual(self.report["stoi"]["status"], "blocked")
        self.assertIsNone(self.report["stoi"]["value_millis"])
        self.assertEqual(self.report["baseline"]["status"], "blocked")
        self.assertIsNone(self.report["baseline"]["baseline_id"])
        self.assertEqual(self.report["listening"]["status"], "not_run")
        self.assertFalse(self.report["listening"]["authorized"])

    def test_candidate_facts_come_from_census(self) -> None:
        candidate = self.report["candidate"]
        self.assertEqual(candidate["reported_hidden_channels"], 48)
        self.assertEqual(candidate["reported_input_sample_rate_hz"], 16000)
        self.assertEqual(candidate["reported_license"], "CC-BY-NC-4.0")
        self.assertTrue(candidate["reported_streaming"])
        self.assertIsNone(candidate["reported_parameter_count"])
        self.assertIsNone(candidate["reported_hop_samples"])
        self.assertIsNone(candidate["reported_algorithmic_latency_samples"])
        self.assertIsNone(candidate["reported_upstream_metrics"]["values"])
        for key in ("source_present", "weights_present", "runtime_present",
                    "geometry_documented", "checkpoint_lineage_verified"):
            self.assertFalse(candidate[key], key)

    def test_licence_scope_blocks_product_use(self) -> None:
        self.assertEqual(self.report["licensing"]["reported_upstream_license"],
                         "CC-BY-NC-4.0")
        self.assertEqual(self.report["licensing"]["review_status"], "blocked")
        self.assertFalse(self.report["licensing"]["commercial_use_permitted"])
        scope = self.report["license_scope"]
        self.assertEqual(scope["permitted_scope"], "research_evaluation_only")
        self.assertFalse(scope["commercial_or_product_use_permitted"])
        self.assertFalse(scope["redistribution_permitted"])
        self.assertFalse(scope["qualifies"])

    def test_paired_arithmetic_and_no_degradation(self) -> None:
        paired = self.report["paired_metrics"]
        for region in paired["regions"]:
            self.assertEqual(
                region["surrogate_si_sdr_millidb"],
                region["identity_si_sdr_millidb"]
                + region["delta_si_sdr_millidb"], region["segment"])
            self.assertFalse(region["qualifies"])
        self.assertTrue(paired["no_noisy_region_degraded"])
        self.assertFalse(paired["qualifies"])

    def test_peak_and_clean_bounds(self) -> None:
        peaks = self.report["peaks_and_invalid"]
        self.assertLess(peaks["max_peak_milli"], peaks["peak_bound_milli"])
        self.assertEqual(peaks["clipped_samples"], 0)
        self.assertEqual(peaks["invalid_output_count"], 0)
        self.assertEqual(peaks["nonfinite_output_count"], 0)
        clean = self.report["clean_preservation"]
        self.assertGreater(clean["min_si_sdr_millidb"], 30000)
        self.assertLess(clean["max_abs_level_change_millidb"], 500)

    def test_alignment_zero_shift(self) -> None:
        alignment = self.report["alignment"]
        self.assertEqual(alignment["surrogate_content_delay_samples"], 0)
        self.assertEqual(alignment["best_shift_samples"], 0)
        self.assertTrue(alignment["zero_shift_best"])
        self.assertFalse(alignment["qualifies"])

    def test_adverse_all_rejected(self) -> None:
        cases = self.report["adverse_rejections"]
        self.assertGreaterEqual(len(cases), 50)
        self.assertTrue(self.report["adverse_all_rejected"])
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["case_id"])
            self.assertTrue(case["state_unchanged"], case["case_id"])
        codes = {case["observed_code"] for case in cases}
        self.assertIn("nonfinite_input:input", codes)
        self.assertIn("padding_not_zero:input", codes)
        self.assertIn("license_scope_not_permitted", codes)

    def test_valid_controls_accepted(self) -> None:
        controls = self.report["valid_controls"]
        self.assertTrue(controls["all_accepted"])
        self.assertEqual([case["status"] for case in controls["cases"]],
                         ["accepted", "accepted", "accepted"])
        self.assertFalse(controls["cases"][1]["loaded"])
        self.assertFalse(controls["cases"][1]["executed"])

    def test_boundary_and_scope_are_closed(self) -> None:
        boundary = self.report["boundary"]
        for key, value in boundary.items():
            self.assertIs(value, False, "boundary." + key)
        scope = self.report["scope"]
        allowed_true = {"synthetic_only", "task_local_only"}
        for key, value in scope.items():
            if key in allowed_true:
                self.assertIs(value, True, "scope." + key)
            else:
                self.assertIs(value, False, "scope." + key)

    def test_external_artifacts_absent(self) -> None:
        external = self.report["external_artifacts"]
        self.assertFalse(external["any_present"])
        self.assertFalse(any(external["present"].values()))

    def test_exact_blockers_cover_licence(self) -> None:
        ids = {blocker["id"] for blocker in self.report["exact_blockers"]}
        self.assertIn("license_cc_by_nc_4_0_research_only", ids)
        self.assertIn("pinned_facebook_denoiser_source_weights_runtime_absent",
                      ids)

    def test_report_is_canonical_and_repeatable(self) -> None:
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)


class ArtifactTests(unittest.TestCase):
    def test_report_bytes_and_sidecar(self) -> None:
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        self.assertEqual((HERE / "report.json").read_text(encoding="utf-8"),
                         text)
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), digest + "\n")

    def test_contract_pins_artifacts(self) -> None:
        contract = reference.load_strict_json(HERE / "contract.json")
        pins = contract["artifact_pins"]
        self.assertIn(reference.TASK_PREFIX + "reference.py", pins)
        self.assertNotIn(reference.TASK_PREFIX + "contract.json", pins)
        for path, digest in pins.items():
            full = reference.SDK_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)

    def test_sources_manifest_is_generated_bytes(self) -> None:
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         reference.sources_bytes())

    def test_no_network_or_model_imports(self) -> None:
        text = (HERE / "reference.py").read_text(encoding="utf-8")
        for token in ("import torch", "import urllib", "import requests",
                      "import socket", "import http"):
            self.assertNotIn(token, text)
        self.assertNotIn("torch.hub", text)
        self.assertNotIn("from_pretrained", text)

    def test_contract_invariants(self) -> None:
        contract = reference.load_strict_json(HERE / "contract.json")
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(len(contract["invariants"]), 10)
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["release_gates"]))


if __name__ == "__main__":
    unittest.main()
