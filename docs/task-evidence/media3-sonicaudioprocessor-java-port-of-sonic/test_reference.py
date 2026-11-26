# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the Media3 Sonic DEFER package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import reference

ROOT = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_strict_json_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"value": NaN}')

    def test_strict_json_rejects_infinity(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"value": Infinity}')

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"a": 1, "a": 2}')

    def test_strict_json_rejects_non_object_root(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text("[1, 2, 3]")

    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertEqual(payload, b'{"a":2,"b":1}')


class RequestTests(unittest.TestCase):
    def test_valid_request_is_accepted(self) -> None:
        parsed = reference.parse_rate_request(reference.valid_request())
        self.assertEqual(parsed["speed"], "5/4")
        self.assertFalse(parsed["is_candidate_result"])
        self.assertFalse(parsed["qualifies"])

    def test_all_adverse_requests_are_rejected(self) -> None:
        for result_id, vector, expected in reference._adverse_vectors():
            with self.subTest(result_id=result_id):
                with self.assertRaises(reference.ReferenceError) as caught:
                    reference.parse_rate_request(vector)
                self.assertTrue(
                    str(caught.exception) == expected
                    or str(caught.exception).startswith(expected + ":"))

    def test_candidate_claim_is_rejected(self) -> None:
        request = reference.valid_request() | {"is_candidate_result": True}
        with self.assertRaises(reference.ReferenceError):
            reference.parse_rate_request(request)

    def test_nonfinite_speed_is_rejected(self) -> None:
        request = reference.valid_request() | {
            "speed_numerator": float("nan")}
        with self.assertRaises(reference.ReferenceError):
            reference.parse_rate_request(request)

    def test_wrong_host_grid_is_rejected(self) -> None:
        for key, value in (("sample_rate_hz", 48000), ("channels", 2),
                           ("frame_samples", 320)):
            with self.subTest(key=key):
                request = reference.valid_request() | {key: value}
                with self.assertRaises(reference.ReferenceError):
                    reference.parse_rate_request(request)


class MappingTests(unittest.TestCase):
    def test_identity_mapping_is_exact(self) -> None:
        mapped = reference.map_source_to_output(
            reference.Fraction(1, 1), reference.CONTROL_TOTAL_SAMPLES)
        self.assertEqual(mapped["output_frames"], "16000")
        self.assertEqual(mapped["duration_error_samples_exact"], "0")

    def test_rate_mapping_values(self) -> None:
        expected = [
            ("1", "16000", "0"),
            ("3/4", "21333", "-1/3"),
            ("5/4", "12800", "0"),
            ("3/2", "10666", "-2/3"),
        ]
        actual = []
        for numerator, denominator in reference.CONTROL_SPEEDS:
            mapped = reference.map_source_to_output(
                reference.Fraction(numerator, denominator),
                reference.CONTROL_TOTAL_SAMPLES)
            actual.append((mapped["speed"], mapped["output_frames"],
                           mapped["duration_error_samples_exact"]))
        self.assertEqual(actual, expected)

    def test_chunk_sum_matches_total(self) -> None:
        for numerator, denominator in reference.CONTROL_SPEEDS:
            mapped = reference.map_source_to_output(
                reference.Fraction(numerator, denominator),
                reference.CONTROL_TOTAL_SAMPLES)
            self.assertTrue(mapped["chunk_sum_matches_total"])

    def test_final_partial_window(self) -> None:
        mapped = reference.map_source_to_output(
            reference.Fraction(5, 4),
            reference.CONTROL_FINAL_WINDOW_SOURCE_FRAMES)
        self.assertEqual(mapped["output_frames"], "132")
        self.assertEqual(mapped["chunk_count"], 2)
        self.assertEqual(mapped["chunks"][-1]["source_end_exclusive"], "165")
        self.assertEqual(
            mapped["chunks"][-1]["output_end_exclusive"], "132")

    def test_long_run_is_closed_form(self) -> None:
        mapped = reference.map_source_to_output(
            reference.LONG_RUN_SPEED, reference.LONG_RUN_SOURCE_FRAMES,
            include_chunks=False)
        self.assertEqual(mapped["output_frames"], "46080000")
        self.assertEqual(mapped["duration_error_samples_exact"], "0")
        self.assertTrue(mapped["chunk_sum_matches_total"])

    def test_all_mapping_adverse_vectors_are_rejected(self) -> None:
        for result_id, speed, frames, expected in reference._mapping_vectors():
            with self.subTest(result_id=result_id):
                with self.assertRaises(reference.ReferenceError) as caught:
                    reference.map_source_to_output(speed, frames)
                self.assertTrue(
                    str(caught.exception) == expected
                    or str(caught.exception).startswith(expected + ":"))


class EnvelopeTests(unittest.TestCase):
    def test_control_is_explicitly_synthetic(self) -> None:
        control = reference.control_envelope_payload()
        self.assertFalse(control["design"]["is_media3_sonic"])
        self.assertFalse(control["design"]["is_candidate_result"])
        self.assertTrue(control["design"]["is_synthetic_control"])
        self.assertFalse(control["qualifies"])

    def test_blocked_measurement_sections_are_null(self) -> None:
        control = reference.control_envelope_payload()
        pairs = (
            ("media3_runtime", "output_sample_rate_hz"),
            ("pitch_measurement", "pitch_error_cents"),
            ("transient_measurement", "transient_audibility"),
            ("playback_buffer", "fill_ms"),
            ("device_timing", "output_latency_ms"),
            ("speech_preservation", "preservation_metric"),
            ("listening", "protocol_id"),
        )
        for section, key in pairs:
            with self.subTest(section=section):
                self.assertIsNone(control[section][key])
                self.assertEqual(control[section]["status"], "blocked")

    def test_separation_is_explicit(self) -> None:
        separation = reference.control_envelope_payload()["separation"]
        self.assertTrue(separation["candidate_and_control_separate"])
        self.assertFalse(separation["control_is_candidate"])
        self.assertFalse(separation["device_timing_is_listening"])
        self.assertFalse(separation["native_c_is_media3_java"])
        self.assertIsNone(separation["pooled_metric"])

    def test_candidate_record_claims_nothing(self) -> None:
        record = reference.candidate_record()
        for key, value in record.items():
            if key.endswith("_present") or key in (
                    "artifact_present", "license_reviewed",
                    "public_implementation_found", "reproduced_here",
                    "source_reported_only"):
                if key == "source_reported_only":
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)
        self.assertFalse(record["qualifies"])

    def test_declared_contract_is_not_verified(self) -> None:
        contract = reference.declared_contract()
        self.assertFalse(contract["media3_runtime_verified"])
        self.assertFalse(contract["speed_range_is_a_measurement"])
        self.assertFalse(contract["pitch_is_a_measurement"])
        self.assertTrue(contract["installed_v0_unchanged"])
        self.assertFalse(contract["qualifies"])


class QualificationTests(unittest.TestCase):
    def test_qualification_is_not_qualified(self) -> None:
        qualification = reference.qualification_payload()
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertTrue(qualification["incomplete"])
        self.assertTrue(qualification["proposal_only"])
        self.assertFalse(qualification["qualifies"])
        self.assertFalse(qualification["missing_result_promoted"])

    def test_eight_release_gates_are_blocked(self) -> None:
        self.assertEqual(len(reference.RELEASE_GATES), 8)
        for gate in reference.RELEASE_GATES:
            self.assertEqual(gate["status"], "blocked")
            self.assertIsNone(gate["evidence"])
            self.assertFalse(gate["qualifies"])

    def test_required_artifacts_are_absent(self) -> None:
        self.assertEqual(len(reference.REQUIRED_ARTIFACTS), 8)
        for item in reference.REQUIRED_ARTIFACTS:
            self.assertFalse(item["present"])
            self.assertTrue(item["rights_requirement"])
            self.assertTrue(item["why_blocked"])

    def test_exact_blockers_are_present(self) -> None:
        self.assertGreaterEqual(len(reference.EXACT_BLOCKERS), 7)
        joined = " ".join(reference.EXACT_BLOCKERS)
        self.assertIn("Media3", joined)
        self.assertIn("native Sonic C", joined)

    def test_missing_results_are_null(self) -> None:
        for row in reference.missing_results():
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_qualification_slots_are_null(self) -> None:
        slots = reference.qualification_slots()
        self.assertEqual(len(slots), 9)
        for slot in slots.values():
            self.assertIsNone(slot["value"])
            self.assertFalse(slot["qualifies"])

    def test_acceptance_profile_is_nonqualifying(self) -> None:
        profile = reference.acceptance_profile()
        self.assertEqual(profile["profile"], "rate")
        self.assertEqual(len(profile["items"]), 18)
        for item in profile["items"]:
            self.assertIn(item["status"], reference.ALLOWED_PROFILE_STATUS)
            self.assertFalse(item["qualifies"])


class ManifestTests(unittest.TestCase):
    def test_valid_manifest_shape_is_accepted(self) -> None:
        parsed = reference.parse_manifest(reference.valid_manifest())
        self.assertFalse(parsed["files_verified"])
        self.assertFalse(parsed["official_identity"])
        self.assertFalse(parsed["qualifies"])

    def test_all_adverse_manifests_are_rejected(self) -> None:
        for control_id, document, expected in reference._manifest_controls()[1:]:
            with self.subTest(control_id=control_id):
                with self.assertRaises(reference.ReferenceError) as caught:
                    reference.parse_manifest(document)
                self.assertTrue(
                    str(caught.exception) == expected
                    or str(caught.exception).startswith(expected + ":"))

    def _materialize(self, directory: Path) -> dict:
        manifest = reference.valid_manifest()
        names = {
            "sonic_audio_processor_path": "SonicAudioProcessor.java",
            "sonic_pitch_shifter_path": "Sonic.java",
            "media3_license_path": "LICENSE",
            "build_toolchain_lock_path": "toolchain.lock",
            "runtime_manifest_path": "runtime-manifest.json",
            "rights_approval_path": "media3-approval.txt",
            "measurement_manifest_path": "measurements.json",
        }
        for path_key, filename in names.items():
            path = directory / filename
            path.write_bytes(("evidence:" + filename).encode("ascii"))
            manifest[path_key] = str(path)
            manifest[path_key[:-5] + "_sha256"] = hashlib.sha256(
                path.read_bytes()).hexdigest()
        return manifest

    def test_manifest_files_are_hashed_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._materialize(Path(temporary))
            checked = reference.verify_manifest_files(manifest)
            self.assertTrue(checked["files_verified"])
            self.assertTrue(checked["all_match"])
            self.assertFalse(checked["official_identity"])
            self.assertFalse(checked["executed"])
            self.assertFalse(checked["loaded"])

    def test_manifest_file_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._materialize(Path(temporary))
            manifest["sonic_pitch_shifter_sha256"] = "0" * 64
            with self.assertRaises(reference.ReferenceError):
                reference.verify_manifest_files(manifest)

    def test_manifest_missing_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._materialize(Path(temporary))
            Path(manifest["measurement_manifest_path"]).unlink()
            with self.assertRaises(reference.ReferenceError):
                reference.verify_manifest_files(manifest)


class ReportTests(unittest.TestCase):
    def test_failure_controls_all_true(self) -> None:
        report = reference.build_report_core()
        controls = report["failure_controls"]
        self.assertTrue(controls["all_explicit"])
        self.assertEqual(set(controls["checks"]),
                         set(reference.FAILURE_CHECK_IDS))
        self.assertTrue(all(controls["checks"].values()))
        self.assertFalse(controls["qualifies"])

    def test_report_key_set(self) -> None:
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(set(report), reference.REPORT_KEYS)

    def test_report_canonical_digest(self) -> None:
        raw = (ROOT / "report.json").read_bytes()
        report = reference.read_strict_json(ROOT / "report.json")
        text, digest = reference.canonical_report(report)
        self.assertEqual(raw, (text + "\n").encode("utf-8"))
        sidecar = (ROOT / "report.json.sha256").read_text(
            encoding="ascii").strip()
        self.assertEqual(sidecar, digest)
        self.assertEqual(sidecar, hashlib.sha256(raw).hexdigest())

    def test_report_is_deterministic_in_process(self) -> None:
        digests = {
            reference.sha256_bytes(
                reference.canonical_bytes(reference.build_report_core()))
            for _ in range(3)
        }
        self.assertEqual(len(digests), 1)

    def test_no_qualifying_value_recurses(self) -> None:
        self.assertFalse(
            reference._contains_qualifying(reference.build_report_core()))

    def test_absence_audit_is_all_absent(self) -> None:
        audit = reference.absence_audit()
        self.assertTrue(audit["all_candidate_artifacts_absent"])
        self.assertFalse(audit["media3_source_present"])
        self.assertFalse(audit["media3_artifact_present"])
        self.assertFalse(any(audit["checked_paths"].values()))
        self.assertFalse(any(audit["host_probes"].values()))

    def test_artifact_assessment_conclusion_is_blocked(self) -> None:
        assessment = reference.artifact_assessment()
        self.assertTrue(assessment["all_required_absent"])
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))

    def test_native_sonic_c_provenance_is_not_candidate(self) -> None:
        provenance = reference.native_sonic_c_provenance()
        self.assertTrue(provenance["present"])
        self.assertTrue(provenance["digests_match"])
        self.assertFalse(provenance["exact_media3_java_port"])
        self.assertFalse(provenance["admitted_for_candidate"])
        self.assertFalse(provenance["used_for_qualification"])
        self.assertFalse(provenance["executed"])
        self.assertFalse(provenance["qualifies"])

    def test_native_sonic_pins_are_source_pins(self) -> None:
        for name, digest in reference.NATIVE_SONIC_PINS.items():
            self.assertEqual(reference.SOURCE_PINS[name], digest)

    def test_task_row_identity_has_no_mutable_fields(self) -> None:
        row = reference.TASK_ROW_IDENTITY
        for key in ("status", "owner", "claim", "review", "handoff",
                    "blocked_reason"):
            self.assertNotIn(key, row)
        self.assertFalse(reference.MUTABLE_PROVENANCE["hashed"])
        self.assertFalse(reference.MUTABLE_PROVENANCE["gate"])

    def test_no_mutable_board_digest_in_report(self) -> None:
        text = json.dumps(reference.build_report_core(), sort_keys=True)
        self.assertNotIn("sha256_at_read", text)
        self.assertNotIn("sha256_now", text)

    def test_observed_provenance_is_source_reported(self) -> None:
        provenance = reference.observed_provenance()
        self.assertFalse(provenance["reproduced_here"])
        self.assertFalse(provenance["device_timing_is_listening"])
        self.assertEqual(len(provenance["documented_context"]), 9)
        for row in provenance["documented_context"]:
            self.assertTrue(row["is_source_reported"])
            self.assertFalse(row["is_measurement"])
            self.assertFalse(row["is_human_rating"])
            self.assertFalse(row["reproduced_here"])
            self.assertFalse(row["qualifies"])

    def test_ranking_is_withheld(self) -> None:
        ranking = reference.ranking_payload()
        self.assertEqual(ranking["order"], "not_ranked")
        self.assertIsNone(ranking["recommendation"])
        self.assertFalse(ranking["qualifies"])


class FileTests(unittest.TestCase):
    def test_readme_states_decision_and_scope(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for token in ("DEFER", "not_qualified", "eight", "Media3",
                      "SonicAudioProcessor", "Sonic.java", "Apache-2.0",
                      "incomplete", "proposal"):
            self.assertIn(token, readme)

    def test_local_file_set_matches_contract(self) -> None:
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix != ".pyc"
            and "__pycache__" not in path.parts
        }
        self.assertEqual(actual, set(reference.LOCAL_FILES))

    def test_sources_manifest_does_not_pin_the_board(self) -> None:
        text = (ROOT / "SOURCES.sha256").read_text(encoding="utf-8")
        self.assertNotIn("TASKS.json", text)


if __name__ == "__main__":
    unittest.main()
