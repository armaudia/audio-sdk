# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library acceptance tests for SDK-LIBSOXR evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import reference

HERE = Path(__file__).resolve().parent
REPORT = reference.build_report()
REPORT_BYTES = reference.report_bytes()


def artifact(name: str) -> Path:
    return HERE / name


def _finite_json(value):
    if isinstance(value, float):
        return value == value and value not in (float("inf"), float("-inf"))
    if isinstance(value, dict):
        return all(_finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite_json(item) for item in value)
    return True


class InvariantTests(unittest.TestCase):
    def test_identity_status_and_decision(self) -> None:
        self.assertEqual(REPORT["task"], "SDK-LIBSOXR")
        self.assertEqual(REPORT["component"], "libsoxr")
        self.assertEqual(REPORT["decision"], "DEFER")
        self.assertEqual(REPORT["status"], "proposal_only_not_qualified")
        self.assertEqual(REPORT["qualification"]["status"], "not_qualified")
        self.assertEqual(REPORT["qualification"]["readiness"], "incomplete")
        self.assertFalse(REPORT["qualification"]["candidate_qualified"])
        self.assertFalse(REPORT["qualification"]["upstream_parity"])

    def test_all_eight_release_gates_blocked(self) -> None:
        gates = REPORT["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(number) for number in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["reason"] and gate["reopen"] for gate in gates))

    def test_upstream_blocker_is_explicit_not_fabricated(self) -> None:
        blocker = REPORT["upstream_blocker"]
        self.assertEqual(blocker["status"], "blocked_upstream_absent")
        self.assertIsNone(blocker["pinned_revision"])
        self.assertIsNone(blocker["source_digest"])
        self.assertTrue(blocker["no_upstream_parity_claim"])
        self.assertIn("LGPL-2.1-or-later", blocker["expected_license"])
        self.assertIn("rights_requirement", blocker)

    def test_installed_v0_boundary_is_unchanged(self) -> None:
        boundary = REPORT["boundary"]
        self.assertEqual(boundary["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
        })
        self.assertTrue(boundary["installed_v0_unchanged"])
        for key in ("public_api_abi_changed", "provider_registered",
                    "descriptor_registration", "enabled_by_default",
                    "registry_changed", "shared_cmake_changed", "ci_changed",
                    "board_or_handoff_changed", "real_corpus_or_weights",
                    "benchmark_claim", "release_claim"):
            self.assertFalse(boundary[key], key)


class RatioAndMappingTests(unittest.TestCase):
    def test_exact_ratio_terms(self) -> None:
        self.assertEqual(reference.ratio_terms(0.5)[:2], (1, 2))
        self.assertEqual(reference.ratio_terms(0.75)[:2], (3, 4))
        self.assertEqual(reference.ratio_terms(1.0)[:2], (1, 1))
        self.assertEqual(reference.ratio_terms(1.25)[:2], (5, 4))
        self.assertEqual(reference.ratio_terms(1.5)[:2], (3, 2))
        self.assertEqual(reference.ratio_terms(2.0)[:2], (2, 1))

    def test_exact_lengths_on_all_rate_cases(self) -> None:
        for name, case in REPORT["rate_cases"].items():
            with self.subTest(case=name):
                self.assertEqual(case["output_samples"],
                                 case["expected_output_samples"])
                self.assertTrue(case["duration_exact"])
                self.assertTrue(case["map_monotonic"])
                self.assertTrue(case["partition_ok"])
                self.assertEqual(case["nonfinite_count"], 0)

    def test_identity_is_bit_exact_on_every_fixture(self) -> None:
        for name in reference.RATE_FIXTURES:
            source = reference.FIXTURE_GENERATORS[name]()
            result = reference.resample(source, 1.0)
            self.assertEqual(tuple(result["samples"]), tuple(source))
            self.assertTrue(result["identity_fast_path"])
            self.assertEqual(result["mapping"], tuple(range(len(source))))

    def test_silence_stays_exactly_zero(self) -> None:
        for ratio in reference.RATIOS:
            result = reference.resample(reference.silence(320), ratio)
            self.assertEqual(reference.peak_abs(result["samples"]), 0.0)
            self.assertEqual(result["nonfinite_count"], 0)

    def test_partition_covers_every_source_sample(self) -> None:
        source = reference.tonal_220hz(800)
        for ratio in reference.RATIOS:
            result = reference.resample(source, ratio)
            self.assertTrue(reference.partition_covers(result["mapping"], len(source)))
            self.assertEqual(result["mapping"][0], 0)
            self.assertLess(result["mapping"][-1], len(source))

    def test_round_half_up_expected_lengths(self) -> None:
        self.assertEqual(reference.expected_output_samples(12737, 1.25), 15921)
        self.assertEqual(reference.expected_output_samples(10, 0.5), 5)
        self.assertEqual(reference.expected_output_samples(11, 0.5), 6)


class RejectionTests(unittest.TestCase):
    def test_nonfinite_input_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(reference.InputError):
                reference.resample([0.0, value], 1.0)

    def test_out_of_range_input_rejected(self) -> None:
        for value in (4.0001, -4.0001, 1e9):
            with self.assertRaises(reference.InputError):
                reference.resample([0.0, value], 1.0)

    def test_invalid_sample_types_rejected(self) -> None:
        for samples in ([True], ["0.1"], [[0.1]], [], (0.0, object())):
            with self.assertRaises(reference.InputError):
                reference.resample(samples, 1.0)

    def test_invalid_ratios_rejected(self) -> None:
        for ratio in (0.0, -1.0, 5.0, float("nan"), float("inf"), True, "1.0",
                      None, [1.0]):
            with self.assertRaises(reference.ConfigError):
                reference.ratio_terms(ratio)

    def test_invalid_configuration_rejected(self) -> None:
        for config in ({"unexpected": 1}, {"sample_rate_hz": 48000},
                       {"frame_samples": 320}, {"half_width": 1},
                       {"half_width": 65}, {"min_ratio": 5.0}):
            with self.assertRaises(reference.ConfigError):
                reference.validate_config(config)

    def test_missing_result_is_blocked_without_metrics(self) -> None:
        missing = reference.missing_result("unknown_stimulus")
        self.assertEqual(missing["status"], "blocked")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies_candidate"])

    def test_adverse_cases_fail_closed(self) -> None:
        adverse = REPORT["adverse"]["invalid_config_and_input"]
        self.assertTrue(adverse["all_rejected"])
        self.assertIsNone(adverse["metrics"])
        for case in adverse["cases"]:
            self.assertNotEqual(case["error"], "NOT_REJECTED")

    def test_strict_json_rejects_duplicate_and_nonfinite(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                        '[]', '{"a":1} extra'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(payload)

    def test_strict_json_accepts_clean_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})


class SignalProxyTests(unittest.TestCase):
    def test_crosscheck_is_byte_identical(self) -> None:
        for ratio in (0.5, 1.0, 1.25, 2.0):
            check = reference.crosscheck(reference.tonal_220hz(1200), ratio)
            self.assertTrue(check["byte_identical"], ratio)

    def test_alias_suppression_beats_naive_decimation(self) -> None:
        alias = REPORT["alias_suppression"]
        self.assertLess(alias["filtered_suppression_db"], -40.0)
        self.assertGreater(alias["filtered_suppression_db"],
                           alias["unfiltered_suppression_db"] - 100.0)
        self.assertGreater(alias["unfiltered_suppression_db"], -12.0)

    def test_image_rejection_beats_linear_interpolation(self) -> None:
        image = REPORT["image_rejection"]
        self.assertLess(image["filtered_suppression_db"], -40.0)
        self.assertGreater(image["filtered_suppression_db"],
                           image["unfiltered_suppression_db"] - 100.0)
        self.assertLess(image["unfiltered_suppression_db"], -5.0)

    def test_pitch_is_preserved_at_each_output_rate(self) -> None:
        pitch = REPORT["src_pitch"]
        for label in ("identity_1x", "decimate_0_5x", "interpolate_2x"):
            self.assertAlmostEqual(pitch[label]["pitch_ratio_at_output_rate"],
                                   1.0, delta=0.01)

    def test_varispeed_is_recorded_as_adverse(self) -> None:
        pitch = REPORT["src_pitch"]
        self.assertAlmostEqual(
            pitch["decimate_0_5x"]["varispeed_pitch_factor"], 2.0, delta=0.02)
        self.assertAlmostEqual(
            pitch["interpolate_2x"]["varispeed_pitch_factor"], 0.5, delta=0.02)

    def test_transient_timing_within_one_output_sample(self) -> None:
        for case in REPORT["transient_proxies"].values():
            for event in case["events"]:
                self.assertLessEqual(event["timing_error_samples"], 1)

    def test_drift_is_zero_in_the_reference_and_visible_in_the_control(self) -> None:
        drift = REPORT["drift"]
        self.assertEqual(
            drift["naive_float_accumulator"]["reference_position_error_samples"], 0.0)
        self.assertGreater(
            drift["naive_float_accumulator"]["max_position_error_samples"], 0.0)

    def test_rebuffer_plays_every_sample_without_skip(self) -> None:
        rebuffer = REPORT["rebuffer"]
        self.assertEqual(rebuffer["played_samples"], 9600)
        self.assertEqual(rebuffer["skipped_audio_samples"], 0)
        self.assertGreaterEqual(rebuffer["underrun_ticks"], 1)

    def test_variable_rate_segments_are_exact_but_not_api_parity(self) -> None:
        variable = REPORT["variable_rate"]
        self.assertTrue(variable["duration_exact"])
        self.assertEqual(len(variable["segments"]), 3)
        self.assertFalse(variable["smooth_soxr_set_io_ratio_behavior_claimed"])

    def test_final_partial_window_is_exact(self) -> None:
        partial = REPORT["final_partial_window"]
        self.assertEqual(partial["source_samples"], 12737)
        self.assertEqual(partial["output_samples"], 15921)
        self.assertEqual(partial["output_samples"],
                         partial["expected_output_samples"])
        self.assertEqual(partial["nonfinite_count"], 0)

    def test_speech_proxy_has_voiced_pause_contrast(self) -> None:
        speech = REPORT["speech_preservation"]
        self.assertGreaterEqual(speech["voiced_to_pause_db"], 10.0)
        self.assertEqual(speech["output_samples"],
                         speech["expected_output_samples"])


class ReportIntegrityTests(unittest.TestCase):
    def test_report_has_one_trailing_newline(self) -> None:
        self.assertTrue(REPORT_BYTES.endswith(b"\n"))
        self.assertFalse(REPORT_BYTES.endswith(b"\n\n"))

    def test_report_is_canonical_and_reproducible(self) -> None:
        first = reference.report_bytes()
        second = reference.report_bytes()
        self.assertEqual(first, second)
        value = reference.strict_json_loads(first.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(value),
                         first[:-1])

    def test_required_results_are_all_true_but_unqualified(self) -> None:
        required = REPORT["required_results"]
        self.assertTrue(required)
        self.assertTrue(all(value is True for value in required.values()))
        self.assertFalse(REPORT["qualification"]["candidate_qualified"])

    def test_artifact_pins_match_files(self) -> None:
        for name, digest in REPORT["artifact_pins"].items():
            data = artifact(name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest, name)

    def test_sidecar_matches_report(self) -> None:
        sidecar = artifact("report.json.sha256").read_text(encoding="ascii").strip()
        self.assertEqual(sidecar,
                         hashlib.sha256(artifact("report.json").read_bytes()).hexdigest()
                         + "  report.json")

    def test_contract_matches_report_and_artifacts(self) -> None:
        contract = reference.strict_json_loads(
            artifact("contract.json").read_text(encoding="utf-8"))
        report_value = reference.strict_json_loads(
            artifact("report.json").read_text(encoding="utf-8"))
        canonical = reference.canonical_bytes(report_value)
        self.assertEqual(contract["canonical_report"]["canonical_digest"],
                         hashlib.sha256(canonical).hexdigest())
        self.assertEqual(contract["canonical_report"]["file_sha256"],
                         hashlib.sha256(artifact("report.json").read_bytes()).hexdigest())
        for name, digest in contract["artifact_pins"].items():
            self.assertEqual(hashlib.sha256(artifact(name).read_bytes()).hexdigest(),
                             digest, name)

    def test_sources_pins_resolve(self) -> None:
        workspace = HERE.parents[5]
        sdk_root = HERE.parents[2]
        for line in artifact("SOURCES.sha256").read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            if name.startswith("source:"):
                target = workspace / name[len("source:"):]
            else:
                target = sdk_root / name
            self.assertTrue(target.is_file(), name)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                             digest, name)

    def test_board_projection_excludes_mutable_fields(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(digest, REPORT["board_link_projection_sha256"])
        for row in links:
            self.assertEqual(set(row), {"task_id", "title", "mode",
                                        "repository", "component"})
        self.assertIn("SDK-LIBSOXR",
                      [row["task_id"] for row in links])

    def test_no_upstream_artifact_is_present(self) -> None:
        prohibited = {"soxr.h", "soxr.c", "rate.c", "fft4g64.c", "COPYING",
                      "COPYING.LGPL", "LGPL-2.1.txt"}
        for path in HERE.iterdir():
            self.assertNotIn(path.name, prohibited)
        for path in HERE.glob("*"):
            self.assertNotIn(path.suffix.lower(),
                             {".wav", ".flac", ".onnx", ".so", ".dylib", ".a"})

    def test_report_and_contract_are_strict_json(self) -> None:
        for name in ("report.json", "contract.json"):
            text = artifact(name).read_text(encoding="utf-8")
            value = reference.strict_json_loads(text)
            self.assertIsInstance(value, dict)
            self.assertTrue(_finite_json(value), name)


class SourceAbsenceTests(unittest.TestCase):
    def test_workspace_contains_no_libsoxr_source(self) -> None:
        workspace = HERE.parents[5]
        matches = list(workspace.rglob("soxr.h")) + list(workspace.rglob("soxr.c"))
        self.assertEqual(matches, [])

    def test_upstream_blocker_lists_required_rights_and_files(self) -> None:
        blocker = REPORT["upstream_blocker"]
        self.assertTrue(blocker["required_files"])
        self.assertIn("LICENCE", blocker["required_files"])
        self.assertIn("LGPL-2.1-or-later", blocker["rights_requirement"])
        self.assertTrue(blocker["workspace_search"])

    def test_missing_result_does_not_qualify(self) -> None:
        adverse = REPORT["adverse"]
        self.assertIsNone(adverse["missing_result"]["metrics"])
        self.assertFalse(adverse["missing_result"]["qualifies_candidate"])
        self.assertTrue(REPORT["no_missing_result_qualifies_candidate"])


if __name__ == "__main__":
    unittest.main()
