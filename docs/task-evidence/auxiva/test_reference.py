# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the SDK-AUXIVA blocker package.

Run with::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py

No test skips, uses the network, reads audio, loads a model or executes a
runtime.
"""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json('{"a":1,"a":2}')
        self.assertEqual(caught.exception.code, "duplicate_json_key:a")

    def test_nan_constant_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json('{"a":NaN}')
        self.assertTrue(caught.exception.code.startswith("nonfinite_json_constant"))

    def test_infinity_constant_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.parse_strict_json('{"a":-Infinity}')

    def test_malformed_json_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.parse_strict_json("{")
        self.assertEqual(caught.exception.code, "invalid_json")

    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": 2}),
                         '{"a":2,"b":1}')

    def test_canonical_report_has_one_trailing_newline(self) -> None:
        text, digest = reference.canonical_report({"b": 1, "a": 2})
        self.assertEqual(text, '{"a":2,"b":1}\n')
        self.assertEqual(digest, reference.sha256_bytes(text.encode("utf-8")))


class ConfigTests(unittest.TestCase):
    def test_default_config_valid(self) -> None:
        self.assertEqual(reference.validate_config(reference.DEFAULT_CONFIG),
                         reference.DEFAULT_CONFIG)

    def test_missing_field_rejected(self) -> None:
        config = {key: value for key, value in reference.DEFAULT_CONFIG.items()
                  if key != "clock_ppm"}
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_config(config)
        self.assertEqual(caught.exception.code, "config_fields_mismatch")

    def test_extra_field_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_config({**reference.DEFAULT_CONFIG, "x": 1})

    def test_rate_and_channels_rejected(self) -> None:
        for key, value in (("sample_rate_hz", 8000), ("channels", 1),
                           ("frame_samples", 256), ("hop_samples", 80),
                           ("sample_format", "int16"), ("clock_ppm", 1),
                           ("sample_rate_hz", True)):
            with self.subTest(key=key, value=value):
                with self.assertRaises(reference.Reject):
                    reference.validate_config({**reference.DEFAULT_CONFIG, key: value})


class GeometryTests(unittest.TestCase):
    def test_record_is_exact(self) -> None:
        record = reference.geometry_record()
        self.assertEqual(record["tdoa_ns"], [0, -62_500, 0])
        self.assertEqual(record["relative_q16"], [0, -65_536, 0])
        self.assertEqual(record["relative_samples"], [0, -1, 0])
        self.assertTrue(record["exact_integer_samples"])
        self.assertEqual(record["microphone_count"], 3)
        self.assertEqual(record["clock_ppm"], 0)

    def test_duplicate_microphone_rejected(self) -> None:
        geometry = {**reference.GEOMETRY, "microphones": [
            {"id": "m0", "position_nm": [0, 0, 0]},
            {"id": "m0", "position_nm": [1, 0, 0]},
        ]}
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_geometry(geometry)
        self.assertEqual(caught.exception.code, "duplicate_mic_id")

    def test_non_integer_position_rejected(self) -> None:
        geometry = {**reference.GEOMETRY, "microphones": [
            {"id": "m0", "position_nm": [0, 0, 0]},
            {"id": "m1", "position_nm": [1.5, 0, 0]},
        ]}
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_geometry(geometry)
        self.assertEqual(caught.exception.code, "invalid_position")

    def test_out_of_range_position_rejected(self) -> None:
        geometry = {**reference.GEOMETRY, "microphones": [
            {"id": "m0", "position_nm": [0, 0, 0]},
            {"id": "m1", "position_nm": [reference.MAX_POSITION_NM + 1, 0, 0]},
        ]}
        with self.assertRaises(reference.Reject):
            reference.validate_geometry(geometry)

    def test_non_normalizable_direction_rejected(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_geometry({**reference.GEOMETRY,
                                         "source_direction": [1, 1, 0]})
        self.assertEqual(caught.exception.code,
                         "direction_not_exactly_normalizable")

    def test_unknown_reference_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_geometry({**reference.GEOMETRY,
                                         "reference_mic_id": "m9"})


class MatrixAndChannelTests(unittest.TestCase):
    def test_inverse_matrix_valid(self) -> None:
        self.assertEqual(reference.validate_matrix(reference.INVERSE_MATRIX),
                         [[3.0, -1.0], [-2.0, 3.0]])

    def test_shape_singular_nonfinite_bool_rejected(self) -> None:
        for matrix, code in (
            ([[1, 0]], "invalid_matrix_shape"),
            ([[1, 1], [1, 1]], "singular_matrix"),
            ([[1, 0], [0, "NaN"]], "invalid_matrix_entry"),
            ([[True, 0], [0, 1]], "invalid_matrix_entry"),
            ([[100, 0], [0, 1]], "invalid_matrix_entry"),
        ):
            with self.subTest(matrix=matrix):
                with self.assertRaises(reference.Reject) as caught:
                    reference.validate_matrix(matrix)
                self.assertEqual(caught.exception.code, code)

    def test_channel_rejections(self) -> None:
        cases = (
            ([[0.0, 1.0], [0.0]], "channel_length_mismatch"),
            ([[], []], "empty_channel"),
            ([[0.0, float("nan")], [0.0, 1.0]], "nonfinite_sample"),
            ([[0.0, reference.MAX_ABS_SAMPLE + 1], [0.0, 1.0]],
             "sample_out_of_range"),
            ([[0.0, "1"], [0.0, 1.0]], "invalid_sample"),
            ([[0.0, True], [0.0, 1.0]], "invalid_sample"),
            ([[0.0], [0.0], [0.0]], "invalid_channel_count"),
        )
        for channels, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(reference.Reject) as caught:
                    reference.validate_channels(channels)
                self.assertEqual(caught.exception.code, code)


class FixtureTests(unittest.TestCase):
    def test_sources_are_deterministic(self) -> None:
        first = reference.source_signals()
        second = reference.source_signals()
        self.assertEqual(first, second)
        self.assertEqual(len(first[0]), reference.TOTAL_SAMPLES)
        self.assertEqual(len(first[1]), reference.TOTAL_SAMPLES)

    def test_exact_inverse_recovers_sources(self) -> None:
        first, second = reference.source_signals()
        mixture = reference.mix_sources(first, second)
        left, right = reference.apply_matrix(reference.INVERSE_MATRIX,
                                             [mixture[0], mixture[1]])
        self.assertEqual(left, [reference.EXACT_GAIN * value for value in first])
        self.assertEqual(right, [reference.EXACT_GAIN * value for value in second])

    def test_fixture_statistics_are_stable(self) -> None:
        first, second = reference.source_signals()
        self.assertEqual(sum(value * value for value in first), 294_886_277_056)
        self.assertEqual(sum(value * value for value in second), 73_722_206_144)
        self.assertEqual(reference.correlation(first, second),
                         -2.1747897e-05)

    def test_si_sdr_none_for_exact_or_zero(self) -> None:
        self.assertIsNone(reference.si_sdr_db([1.0, 2.0], [1.0, 2.0]))
        self.assertIsNone(reference.si_sdr_db([1.0], [0.0]))
        self.assertGreater(reference.si_sdr_db([1.0, 2.0], [1.0, 1.0]), 0.0)


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.controls = {case["case_id"]: case
                        for case in reference.control_cases()}

    def test_all_cases_are_synthetic_and_nonfinite_free(self) -> None:
        self.assertEqual(len(self.controls), 4)
        for case in self.controls.values():
            self.assertEqual(case["nonfinite_samples"], 0)
            self.assertFalse(case["scale_pinned"])
            self.assertEqual(case["status"],
                             "synthetic_surrogate_only_not_qualified")

    def test_matched_inverse_is_exact(self) -> None:
        case = self.controls["matched_inverse_control"]
        self.assertTrue(case["exact"])
        self.assertEqual(case["max_abs_residual"], 0.0)
        self.assertEqual(case["expected_sources"], [0, 1])
        self.assertEqual(case["expected_gain"], 7)
        self.assertEqual(case["permutation"]["assignment"], [0, 1])
        self.assertEqual(case["permutation"]["exact_output_count"], 2)

    def test_permuted_inverse_is_exact_but_swapped(self) -> None:
        case = self.controls["permuted_inverse_control"]
        self.assertTrue(case["exact"])
        self.assertEqual(case["permutation"]["assignment"], [1, 0])
        self.assertEqual(case["expected_sources"], [1, 0])
        self.assertEqual(case["output_rms"],
                         self.controls["matched_inverse_control"]["output_rms"][::-1])

    def test_scaled_inverse_is_exact_up_to_gain(self) -> None:
        case = self.controls["scaled_inverse_control"]
        self.assertTrue(case["exact"])
        self.assertEqual(case["expected_gain"], 14)
        self.assertEqual(case["permutation"]["assignment"], [0, 1])

    def test_identity_control_is_raw_mixture(self) -> None:
        case = self.controls["identity_control"]
        self.assertTrue(case["exact"])
        self.assertEqual(case["max_abs_residual"], 0.0)
        self.assertIsNone(case["expected_sources"])
        self.assertIsNone(case["expected_gain"])

    def test_controls_are_deterministic(self) -> None:
        self.assertEqual(reference.control_cases(), reference.control_cases())


class BlindControlTests(unittest.TestCase):
    def test_blind_control_is_bounded_and_not_auxiva(self) -> None:
        first, second = reference.source_signals()
        first_run = reference.blind_decorrelation((first, second))
        second_run = reference.blind_decorrelation((first, second))
        self.assertEqual(first_run, second_run)
        self.assertIn("not AuxIVA", first_run["limitation"])
        self.assertEqual(first_run["outputs"]["nonfinite_samples"], 0)
        self.assertEqual(first_run["outputs"]["permutation"]["assignment"], [0, 1])
        for row in first_run["matrix"]:
            for value in row:
                self.assertLessEqual(abs(value), reference.BLIND_CLAMP)

    def test_blind_control_is_poorer_than_exact(self) -> None:
        first, second = reference.source_signals()
        blind = reference.blind_decorrelation((first, second))
        table = blind["outputs"]["permutation"]["si_sdr_table_db"]
        self.assertGreater(table[0][0], 0.0)
        self.assertLess(table[1][1], 2.0)


class SessionTests(unittest.TestCase):
    def test_streaming_is_block_invariant(self) -> None:
        first, second = reference.source_signals()
        result = reference.streaming_check((first, second))
        self.assertTrue(result["all_match"])
        self.assertEqual(result["accepted_samples"], reference.TOTAL_SAMPLES)
        self.assertEqual(result["chunks"], [160, 480, 800, 137, 641])

    def test_reset_matches_fresh(self) -> None:
        result = reference.reset_check()
        self.assertTrue(result["matches_fresh"])
        self.assertEqual(result["epoch"], 1)
        self.assertEqual(result["accepted_samples"], 160)

    def test_invalid_reset_leaves_state_unchanged(self) -> None:
        session = reference.DemixSession()
        session.process([[0.0] * 8, [0.0] * 8])
        before = session.snapshot()
        for epoch in (0, -1, True, "1"):
            with self.subTest(epoch=epoch):
                with self.assertRaises(reference.Reject):
                    session.reset(epoch)
                self.assertEqual(session.snapshot(), before)


class AdverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = reference.adverse_rejections()

    def test_all_adverse_cases_are_rejected_immutably(self) -> None:
        self.assertEqual(len(self.records), 36)
        for record in self.records:
            self.assertEqual(record["status"], "rejected", record["case_id"])
            self.assertTrue(record["state_unchanged"], record["case_id"])
            self.assertNotEqual(record["code"], "ACCEPTED", record["case_id"])

    def test_expected_codes_are_present(self) -> None:
        codes = {record["case_id"]: record["code"] for record in self.records}
        self.assertEqual(codes["duplicate_json_key"], "duplicate_json_key:a")
        self.assertEqual(codes["matrix_singular"], "singular_matrix")
        self.assertEqual(codes["channels_nonfinite"], "nonfinite_sample")
        self.assertEqual(codes["reset_epoch_zero"], "invalid_epoch")
        self.assertEqual(codes["caller_manifest_bad_hash"],
                         "asset_hash_mismatch:source_path")


class CallerAssetTests(unittest.TestCase):
    def _manifest(self, root: Path) -> dict:
        source = root / "source.bin"
        runtime = root / "runtime.bin"
        source.write_bytes(b"source")
        runtime.write_bytes(b"runtime")
        return {
            "adapter": "auxiva",
            "channels": 2,
            "frame_samples": 160,
            "license_id": "caller-declared",
            "permutation_reference": "caller_labels",
            "runtime_path": str(runtime),
            "runtime_sha256": reference.file_digest(runtime),
            "sample_format": "float32",
            "sample_rate_hz": 16000,
            "source_commit": "0" * 40,
            "source_path": str(source),
            "source_sha256": reference.file_digest(source),
        }

    def test_valid_manifest_is_identity_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._manifest(Path(temporary))
            result = reference.validate_caller_asset(manifest)
        self.assertTrue(result["verified_without_execution"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["imported"])
        self.assertEqual(result["status"],
                         "identity_validated_only_do_not_qualify")

    def test_bad_hash_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._manifest(Path(temporary))
            manifest["source_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject) as caught:
                reference.validate_caller_asset(manifest)
        self.assertEqual(caught.exception.code,
                         "asset_hash_mismatch:source_path")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualifies"])
        self.assertFalse(report["qualification"]["missing_result_promoted"])
        self.assertFalse(report["qualification"]["all_required_results_present"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_spatial_profile_items(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "spatial")
        self.assertEqual(len(profile["required_items"]), 6)
        self.assertEqual(self.report["profile_blockers"], [
            "leakage_target_damage_channel_loss",
            "room_reference_changes",
            "source_target_reference_conditions_and_permissions",
            "task_matched_heldout_localization_activity_extraction",
        ])
        for item in profile["required_items"].values():
            self.assertIn(item["status"], {"synthetic_only", "blocked"})

    def test_reference_and_blockers_are_absent(self) -> None:
        self.assertFalse(self.report["reference"]["source_present"])
        self.assertFalse(self.report["reference"]["runtime_present"])
        self.assertFalse(self.report["reference"]["implementation_present"])
        self.assertFalse(self.report["reference"]["exact_numeric_output_present"])
        self.assertEqual(len(self.report["exact_blockers"]), 4)

    def test_permutation_and_scale_are_blocked(self) -> None:
        self.assertEqual(
            self.report["permutation_qualification"]["status"], "blocked")
        self.assertFalse(self.report["permutation_qualification"]
                         ["observed_on_synthetic"]
                         ["score_alone_resolves_permutation"])
        self.assertEqual(
            self.report["scale_qualification"]["status"], "blocked")
        self.assertFalse(self.report["scale_qualification"]
                         ["synthetic_observation"]["scale_resolved"])

    def test_h_gtcrn_is_not_pooled(self) -> None:
        section = self.report["h_gtcrn_separation"]
        self.assertFalse(section["this_package_uses_h_gtcrn"])
        self.assertFalse(section["h_gtcrn_evidence_pooled"])
        self.assertFalse(section["h_gtcrn_source_pinned"])

    def test_boundary_flags_are_false(self) -> None:
        self.assertTrue(self.report["boundary"])
        self.assertTrue(all(value is False
                            for value in self.report["boundary"].values()))

    def test_board_identity_is_stable_and_not_hashed(self) -> None:
        board = self.report["board_row"]
        self.assertEqual(board["stable_fields"]["id"], "SDK-AUXIVA")
        self.assertEqual(board["stable_sha256"],
                         reference.BOARD_ROW_STABLE_SHA256)
        self.assertFalse(board["full_tasks_json_hashed"])
        for section in ("source_pins", "boundary_pins"):
            self.assertNotIn("TASKS.json", json.dumps(self.report[section]))

    def test_repeatability(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["runs"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["case_matrix_digests"])), 1)

    def test_report_is_three_times_deterministic(self) -> None:
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)

    def test_no_nonfinite_numbers(self) -> None:
        def check(value: object) -> None:
            if isinstance(value, float):
                self.assertTrue(math.isfinite(value))
            elif isinstance(value, dict):
                for item in value.values():
                    check(item)
            elif isinstance(value, list):
                for item in value:
                    check(item)

        check(self.report)
        text = reference.canonical_text(self.report)
        self.assertNotIn('"qualified"', text)

    def test_streaming_and_reset(self) -> None:
        self.assertTrue(self.report["streaming"]["all_match"])
        self.assertTrue(self.report["reset"]["matches_fresh"])

    def test_external_paths_are_absent(self) -> None:
        external = self.report["external_artifacts"]
        self.assertEqual(external["status"], "blocked")
        self.assertEqual(set(external["present"]),
                         {"source_checkout", "runtime_env", "weights", "adapter"})
        self.assertFalse(external["any_present"])


class ContractTests(unittest.TestCase):
    def test_contract_matches_report(self) -> None:
        report = reference.build_report()
        _, digest = reference.canonical_report(report)
        contract = reference.build_contract(digest)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertEqual(contract["artifact_pins"][
                             "docs/task-evidence/auxiva/report.json"], digest)
        self.assertNotIn("docs/task-evidence/auxiva/contract.json",
                         contract["artifact_pins"])
        self.assertNotIn("docs/task-evidence/auxiva/SOURCES.sha256",
                         contract["artifact_pins"])

    def test_required_contract_sections(self) -> None:
        _, digest = reference.canonical_report(reference.build_report())
        contract = reference.build_contract(digest)
        for key in ("acceptance_profile", "artifact_pins", "board_row",
                    "boundary", "boundary_pins", "caller_asset_contract",
                    "exact_blockers", "format", "h_gtcrn_separation",
                    "invariants", "negative_claims", "permutation_qualification",
                    "qualification_status", "reference", "release_gates",
                    "reopen_condition", "scale_qualification", "scope",
                    "source_pins", "verification_profile"):
            self.assertIn(key, contract)


class PinsAndFilesTests(unittest.TestCase):
    def test_source_and_boundary_pins_match_disk(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            full = reference.SOURCE_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)
        for path, digest in reference.BOUNDARY_PINS.items():
            full = reference.SDK_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), digest, path)

    def test_sources_bytes_are_well_formed(self) -> None:
        payload = reference.sources_bytes().decode("utf-8")
        lines = [line for line in payload.splitlines()
                 if line and not line.startswith("#")]
        self.assertTrue(lines)
        paths = []
        for line in lines:
            digest, path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            paths.append(path)
        self.assertNotIn("docs/task-evidence/auxiva/SOURCES.sha256", paths)
        self.assertIn("docs/task-evidence/auxiva/report.json", paths)
        self.assertIn("docs/task-evidence/auxiva/contract.json", paths)
        self.assertIn("docs/task-evidence/auxiva/README.md", paths)

    def test_generated_files_are_canonical_and_pinned(self) -> None:
        report = reference.load_strict_json(HERE / "report.json")
        contract = reference.load_strict_json(HERE / "contract.json")
        report_text, report_digest = reference.canonical_report(report)
        self.assertEqual((HERE / "report.json").read_text(encoding="utf-8"),
                         report_text)
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="ascii"),
                         report_digest + "\n")
        self.assertEqual((HERE / "contract.json").read_text(encoding="utf-8"),
                         reference.canonical_text(contract) + "\n")
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         reference.sources_bytes())

    def test_readme_names_decision_and_gates(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for token in ("DEFER", "incomplete", "not_qualified",
                      "RG-01", "RG-08", "not AuxIVA", "H-GTCRN",
                      "permutation"):
            self.assertIn(token, text)
        for digest in list(reference.SOURCE_PINS.values()) + \
                list(reference.BOUNDARY_PINS.values()):
            self.assertIn(digest, text)


if __name__ == "__main__":
    unittest.main()
