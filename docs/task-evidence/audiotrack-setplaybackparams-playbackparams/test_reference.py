# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, no-network unittest checks for the DEFER package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import reference


class StrictJsonTests(unittest.TestCase):
    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"value": NaN}')

    def test_rejects_infinity(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"value": Infinity}')

    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"a": 1, "a": 2}')

    def test_rejects_non_object_root(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text("[1, 2]")

    def test_canonical_bytes_are_sorted(self) -> None:
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": 2}),
                         b'{"a":2,"b":1}')


class RequestTests(unittest.TestCase):
    def assertReject(self, request: object, expected: str) -> None:
        with self.assertRaises(reference.ReferenceError) as caught:
            reference.parse_playback_params(request)
        actual = str(caught.exception)
        self.assertTrue(actual == expected or actual.startswith(expected + ":"),
                        actual)

    def test_valid_request(self) -> None:
        parsed = reference.parse_playback_params(reference.valid_request())
        self.assertEqual(parsed["speed"], "5/4")
        self.assertEqual(parsed["pitch"], "1")
        self.assertFalse(parsed["is_candidate_result"])
        self.assertFalse(parsed["qualifies"])

    def test_floor_speed_accepted(self) -> None:
        request = reference.valid_request() | {
            "speed_numerator": 3, "speed_denominator": 4}
        self.assertEqual(
            reference.parse_playback_params(request)["speed"], "3/4")

    def test_ceiling_speed_accepted(self) -> None:
        request = reference.valid_request() | {
            "speed_numerator": 3, "speed_denominator": 2}
        self.assertEqual(
            reference.parse_playback_params(request)["speed"], "3/2")

    def test_missing_field(self) -> None:
        request = dict(reference.valid_request())
        del request["api_level"]
        self.assertReject(request, "request_missing_fields")

    def test_extra_field(self) -> None:
        self.assertReject(reference.valid_request() | {"extra": 1},
                          "request_extra_fields")

    def test_wrong_schema(self) -> None:
        self.assertReject(
            reference.valid_request() | {"schema_id": "other/0.1"},
            "request_schema_id_invalid")

    def test_nan_speed_numerator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"speed_numerator": float("nan")},
            "request_speed_numerator_not_integer")

    def test_infinity_speed_denominator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"speed_denominator": float("inf")},
            "request_speed_denominator_not_integer")

    def test_boolean_speed_numerator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"speed_numerator": True},
            "request_speed_numerator_not_integer")

    def test_string_speed_numerator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"speed_numerator": "5"},
            "request_speed_numerator_not_integer")

    def test_zero_speed_denominator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"speed_denominator": 0},
            "request_speed_denominator_not_positive")

    def test_negative_speed_numerator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"speed_numerator": -5},
            "request_speed_numerator_not_positive")

    def test_speed_below_floor(self) -> None:
        self.assertReject(
            reference.valid_request() | {
                "speed_numerator": 1, "speed_denominator": 2},
            "request_speed_below_declared_floor")

    def test_speed_above_ceiling(self) -> None:
        self.assertReject(
            reference.valid_request() | {
                "speed_numerator": 2, "speed_denominator": 1},
            "request_speed_above_declared_ceiling")

    def test_pitch_not_unity(self) -> None:
        self.assertReject(
            reference.valid_request() | {
                "pitch_numerator": 6, "pitch_denominator": 5},
            "request_pitch_not_unity")

    def test_zero_pitch_denominator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"pitch_denominator": 0},
            "request_pitch_denominator_not_positive")

    def test_negative_pitch_denominator(self) -> None:
        self.assertReject(
            reference.valid_request() | {"pitch_denominator": -1},
            "request_pitch_denominator_not_positive")

    def test_boolean_api_level(self) -> None:
        self.assertReject(
            reference.valid_request() | {"api_level": True},
            "request_api_level_not_integer")

    def test_api_level_below_23(self) -> None:
        self.assertReject(
            reference.valid_request() | {"api_level": 22},
            "request_api_level_below_minimum")

    def test_api_level_above_declared(self) -> None:
        self.assertReject(
            reference.valid_request() | {"api_level": 37},
            "request_api_level_above_declared")

    def test_unsupported_fallback_mode(self) -> None:
        self.assertReject(
            reference.valid_request() | {"fallback_mode": "bypass"},
            "request_fallback_mode_unsupported")

    def test_candidate_claim(self) -> None:
        self.assertReject(
            reference.valid_request() | {"is_candidate_result": True},
            "request_candidate_claim")

    def test_candidate_claim_string(self) -> None:
        self.assertReject(
            reference.valid_request() | {"is_candidate_result": "false"},
            "request_candidate_claim")

    def test_non_object_request(self) -> None:
        self.assertReject(["not", "a", "request"], "request_not_an_object")

    def test_empty_request(self) -> None:
        self.assertReject({}, "request_missing_fields")


class MappingTests(unittest.TestCase):
    def test_identity(self) -> None:
        mapping = reference.map_source_to_output(
            reference.Fraction(1, 1), 16000)
        self.assertEqual(mapping["output_frames"], "16000")
        self.assertEqual(mapping["duration_error_samples_exact"], "0")

    def test_three_quarters(self) -> None:
        mapping = reference.map_source_to_output(
            reference.Fraction(3, 4), 16000)
        self.assertEqual(mapping["output_frames"], "21333")
        self.assertEqual(mapping["duration_error_samples_exact"], "-1/3")

    def test_five_quarters(self) -> None:
        mapping = reference.map_source_to_output(
            reference.Fraction(5, 4), 16000)
        self.assertEqual(mapping["output_frames"], "12800")
        self.assertEqual(mapping["duration_error_samples_exact"], "0")

    def test_three_halves(self) -> None:
        mapping = reference.map_source_to_output(
            reference.Fraction(3, 2), 16000)
        self.assertEqual(mapping["output_frames"], "10666")
        self.assertEqual(mapping["duration_error_samples_exact"], "-2/3")

    def test_chunk_sum_matches_total(self) -> None:
        for numerator, denominator in reference.CONTROL_SPEEDS:
            mapping = reference.map_source_to_output(
                reference.Fraction(numerator, denominator), 16000)
            self.assertTrue(mapping["chunk_sum_matches_total"])

    def test_final_partial_window(self) -> None:
        mapping = reference.map_source_to_output(
            reference.Fraction(5, 4), 165)
        self.assertEqual(mapping["chunk_count"], 2)
        self.assertEqual(mapping["output_frames"], "132")
        self.assertEqual(mapping["chunks"][1]["source_end_exclusive"], "165")
        self.assertEqual(
            mapping["chunks"][1]["output_end_exclusive"], "132")

    def test_long_run_is_exact(self) -> None:
        mapping = reference.map_source_to_output(
            reference.LONG_RUN_SPEED, reference.LONG_RUN_SOURCE_FRAMES,
            include_chunks=False)
        self.assertEqual(mapping["output_frames"], "46080000")
        self.assertEqual(mapping["duration_error_samples_exact"], "0")
        self.assertTrue(mapping["chunk_sum_matches_total"])

    def test_nonfinite_speed_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.map_source_to_output(float("nan"), 160)

    def test_boolean_speed_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.map_source_to_output(True, 160)

    def test_boolean_source_frames_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.map_source_to_output(reference.Fraction(1, 1), True)

    def test_negative_source_frames_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.map_source_to_output(reference.Fraction(1, 1), -1)

    def test_huge_source_frames_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.map_source_to_output(
                reference.Fraction(1, 1), reference.MAX_SOURCE_FRAMES + 1)

    def test_out_of_range_speed_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.map_source_to_output(reference.Fraction(1, 2), 160)


class ManifestTests(unittest.TestCase):
    def assertReject(self, document: object, expected: str) -> None:
        with self.assertRaises(reference.ReferenceError) as caught:
            reference.parse_manifest(document)
        actual = str(caught.exception)
        self.assertTrue(actual == expected or actual.startswith(expected + ":"),
                        actual)

    def test_valid_manifest_shape(self) -> None:
        parsed = reference.parse_manifest(reference.valid_manifest())
        self.assertFalse(parsed["files_verified"])
        self.assertFalse(parsed["official_identity"])
        self.assertFalse(parsed["qualifies"])

    def test_missing_field(self) -> None:
        document = dict(reference.valid_manifest())
        del document["artifact_id"]
        self.assertReject(document, "manifest_missing_fields")

    def test_extra_field(self) -> None:
        self.assertReject(reference.valid_manifest() | {"extra": 1},
                          "manifest_extra_fields")

    def test_wrong_platform(self) -> None:
        self.assertReject(reference.valid_manifest() | {"platform": "ios"},
                          "manifest_platform_not_android")

    def test_boolean_api_level(self) -> None:
        self.assertReject(reference.valid_manifest() | {"api_level": True},
                          "manifest_api_level_not_integer")

    def test_api_level_below_23(self) -> None:
        self.assertReject(reference.valid_manifest() | {"api_level": 22},
                          "manifest_api_level_below_minimum")

    def test_relative_path(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {"sdk_stub_path": "android.jar"},
            "manifest_path_not_absolute")

    def test_parent_traversal(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {
                "runtime_image_path": "/caller/../system.img"},
            "manifest_path_traversal")

    def test_duplicate_paths(self) -> None:
        document = reference.valid_manifest()
        document["license_path"] = document["sdk_stub_path"]
        self.assertReject(document, "manifest_paths_not_unique")

    def test_uppercase_hash(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {"sdk_stub_sha256": "E" * 64},
            "manifest_hash_invalid")

    def test_bad_hash_length(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {"platform_impl_sha256": "9" * 63},
            "manifest_hash_invalid")

    def test_stub_equals_implementation(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {
                "sdk_stub_sha256":
                    reference.valid_manifest()["platform_impl_sha256"]},
            "manifest_stub_equals_platform_implementation")

    def test_terms_not_accepted(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {"terms_accepted": False},
            "manifest_terms_not_accepted")

    def test_wrong_attestation(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {"caller_attestation": "trust_me"},
            "manifest_attestation_invalid")

    def test_empty_artifact_id(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {"artifact_id": ""},
            "manifest_artifact_id_invalid")

    def test_listening_not_established(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {
                "listening_protocol_id": "not_established"},
            "manifest_listening_protocol_invalid")

    def test_non_ascii_build_fingerprint(self) -> None:
        self.assertReject(
            reference.valid_manifest() | {
                "build_fingerprint": "gphone-\u00e9-14"},
            "manifest_build_fingerprint_invalid")

    def test_manifest_files_match(self) -> None:
        document = reference.valid_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, key in enumerate(reference.MANIFEST_PATH_FIELDS):
                path = root / ("file-%d.bin" % index)
                path.write_bytes(b"caller-owned-%d" % index)
                document[key] = str(path)
                hash_key = key[:-5] + "_sha256"
                document[hash_key] = hashlib.sha256(
                    path.read_bytes()).hexdigest()
            result = reference.verify_manifest_files(document)
        self.assertTrue(result["all_match"])
        self.assertTrue(result["files_verified"])
        self.assertFalse(result["official_identity"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["qualifies"])

    def test_manifest_missing_file(self) -> None:
        document = reference.valid_manifest()
        document["sdk_stub_path"] = "/nonexistent/android.jar"
        with self.assertRaises(reference.ReferenceError):
            reference.verify_manifest_files(document)

    def test_manifest_digest_mismatch(self) -> None:
        document = reference.valid_manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, key in enumerate(reference.MANIFEST_PATH_FIELDS):
                path = root / ("file-%d.bin" % index)
                path.write_bytes(b"one")
                document[key] = str(path)
                document[key[:-5] + "_sha256"] = hashlib.sha256(
                    path.read_bytes()).hexdigest()
            Path(document["license_path"]).write_bytes(b"two")
            with self.assertRaises(reference.ReferenceError):
                reference.verify_manifest_files(document)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.report_payload()

    def test_control_envelope_rates(self) -> None:
        rates = self.report["control_envelope"]["rates"]
        self.assertEqual([row["speed"] for row in rates],
                         ["1", "3/4", "5/4", "3/2"])
        self.assertTrue(all(row["chunk_sum_matches_total"]
                            for row in rates))
        self.assertTrue(all(row["qualifies"] is False for row in rates))

    def test_control_is_not_candidate(self) -> None:
        design = self.report["control_envelope"]["design"]
        self.assertFalse(design["is_android_audiotrack"])
        self.assertFalse(design["is_candidate_result"])
        self.assertTrue(design["is_synthetic_control"])
        self.assertFalse(design["speed_range_is_a_measurement"])

    def test_blocked_measurements_are_null(self) -> None:
        envelope = self.report["control_envelope"]
        self.assertIsNone(envelope["pitch_measurement"]["pitch_error_cents"])
        self.assertIsNone(envelope["playback_buffer"]["fill_ms"])
        self.assertIsNone(envelope["device_timing"]["output_latency_ms"])
        self.assertIsNone(
            envelope["speech_preservation"]["preservation_metric"])
        self.assertIsNone(envelope["listening"]["protocol_id"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            and gate["evidence"] is None
                            and gate["qualifies"] is False
                            for gate in gates))

    def test_required_artifacts_absent(self) -> None:
        items = self.report["required_artifacts"]
        self.assertEqual(len(items), 8)
        self.assertTrue(all(item["present"] is False for item in items))

    def test_profile_items_nonqualifying(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "rate")
        self.assertEqual(len(profile["items"]),
                         len(reference.PROFILE_ITEMS))
        self.assertTrue(all(item["qualifies"] is False
                            for item in profile["items"]))
        self.assertTrue(all(item["status"]
                            in reference.ALLOWED_PROFILE_STATUS
                            for item in profile["items"]))

    def test_missing_results_blocked(self) -> None:
        rows = self.report["missing_results"]
        self.assertEqual(len(rows), len(reference.MISSING_RESULTS))
        self.assertTrue(all(row["status"] == "blocked"
                            and row["value"] is None
                            and row["qualifies"] is False for row in rows))

    def test_qualification_slots_null(self) -> None:
        slots = self.report["qualification_slots"]
        self.assertEqual(len(slots), 9)
        self.assertTrue(all(slot["value"] is None
                            and slot["qualifies"] is False
                            for slot in slots.values()))

    def test_adverse_request_rejections(self) -> None:
        rows = self.report["adverse_results"]
        self.assertEqual(len(rows), len(reference._adverse_vectors()))
        self.assertTrue(all(row["status"] == "rejected"
                            and row["matches_expected"] is True
                            and row["qualifies"] is False for row in rows))

    def test_adverse_mapping_rejections(self) -> None:
        rows = self.report["mapping_adverse_results"]
        self.assertEqual(len(rows), len(reference._mapping_vectors()))
        self.assertTrue(all(row["status"] == "rejected"
                            and row["matches_expected"] is True
                            and row["qualifies"] is False for row in rows))

    def test_manifest_controls(self) -> None:
        rows = self.report["manifest_controls"]
        self.assertEqual(len(rows), len(reference._manifest_controls()))
        self.assertEqual(rows[0]["control_id"], "valid_shape")
        self.assertTrue(rows[0]["accepted"])
        self.assertTrue(all(row["accepted"] is False
                            and row["matches_expected"] is True
                            and row["qualifies"] is False
                            for row in rows[1:]))

    def test_failure_controls_explicit(self) -> None:
        controls = self.report["failure_controls"]
        self.assertTrue(controls["all_explicit"])
        self.assertTrue(all(controls["checks"].values()))
        self.assertEqual(controls["blocked_release_gates"], 8)
        self.assertFalse(controls["qualifies"])

    def test_no_qualifying_result(self) -> None:
        self.assertFalse(reference._contains_qualifying(self.report))

    def test_report_key_set(self) -> None:
        self.assertEqual(set(self.report), reference.REPORT_KEYS)

    def test_regeneration_three_runs(self) -> None:
        regeneration = self.report["regeneration"]
        self.assertEqual(regeneration["runs"], 3)
        self.assertTrue(regeneration["byte_identical"])
        core = dict(self.report)
        core.pop("regeneration")
        digest = hashlib.sha256(
            reference.canonical_bytes(core)).hexdigest()
        self.assertEqual(regeneration["canonical_digests"], [digest] * 3)

    def test_report_digest_matches_file(self) -> None:
        report_path = reference.ROOT / "report.json"
        self.assertTrue(report_path.is_file())
        raw = report_path.read_bytes()
        sidecar = (reference.ROOT / "report.json.sha256").read_text(
            encoding="ascii").strip()
        self.assertEqual(sidecar, hashlib.sha256(raw).hexdigest())
        self.assertEqual(raw, reference.render_report()[0])

    def test_artifact_assessment_absent(self) -> None:
        assessment = self.report["artifact_assessment"]
        self.assertTrue(assessment["all_required_absent"])
        self.assertFalse(any(assessment["checked_paths"].values()))
        self.assertFalse(any(assessment["host_probes"].values()))
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))


class PinAndContractTests(unittest.TestCase):
    def test_source_pins(self) -> None:
        for name, expected in reference.SOURCE_PINS.items():
            path = reference.WORKSPACE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_boundary_pins(self) -> None:
        for name, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_sibling_pins(self) -> None:
        for name, expected in reference.SIBLING_PINS.items():
            path = reference.WORKTREE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_contract_matches_files(self) -> None:
        contract = reference.contract_payload()
        self.assertEqual(set(contract), reference.CONTRACT_KEYS)
        for name, digest in contract["artifact_pins"].items():
            path = reference.ROOT / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        raw = (reference.ROOT / "contract.json").read_bytes()
        self.assertEqual(
            raw, reference.canonical_bytes(contract) + b"\n")

    def test_sources_manifest_matches_files(self) -> None:
        import run
        manifest = run.render_sources()
        self.assertEqual(
            manifest, (reference.ROOT / "SOURCES.sha256").read_bytes())
        self.assertNotIn(b"SOURCES.sha256  SOURCES.sha256", manifest)
        self.assertNotIn(b"TASKS.json", manifest)

    def test_readme_states_decision_and_gates(self) -> None:
        text = (reference.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("DEFER", text)
        self.assertIn("not_qualified", text)
        self.assertIn("eight", text.lower())
        self.assertIn("Android", text)


if __name__ == "__main__":
    unittest.main()
