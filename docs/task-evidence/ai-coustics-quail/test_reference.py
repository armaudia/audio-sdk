# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for the ai-coustics Quail boundary DEFER package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

import reference

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]


class PinTests(unittest.TestCase):
    def test_source_pins_are_exact(self) -> None:
        for name, expected in reference.SOURCE_PINS.items():
            self.assertEqual(reference.digest_file(WORKSPACE / name), expected,
                             name)

    def test_boundary_pins_are_exact(self) -> None:
        for name, expected in reference.BOUNDARY_PINS.items():
            self.assertEqual(reference.digest_file(WORKTREE / name), expected,
                             name)

    def test_sibling_pins_are_exact(self) -> None:
        for name, expected in reference.SIBLING_PINS.items():
            self.assertEqual(reference.digest_file(WORKTREE / name), expected,
                             name)

    def test_task_row_identity(self) -> None:
        row = reference.TASK_ROW_IDENTITY
        self.assertEqual(row["id"], "SDK-AI-COUSTICS-QUAIL")
        self.assertEqual(row["component"], "ai-coustics-quail")
        self.assertEqual(row["mode"], "external-adapter")
        self.assertEqual(row["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(row["branch"], reference.BRANCH)

    def test_mutable_board_is_not_gated(self) -> None:
        provenance = reference.MUTABLE_PROVENANCE
        self.assertFalse(provenance["hashed"])
        self.assertFalse(provenance["gate"])
        self.assertTrue(provenance["mutable"])
        self.assertNotIn("sha256_at_read", provenance)

    def test_scope_is_local_and_synthetic(self) -> None:
        self.assertTrue(reference.SCOPE["task_local_only"])
        self.assertTrue(reference.SCOPE["synthetic_only"])
        for key in ("vendor_artifact", "vendor_sdk_runtime",
                    "licensed_source_or_binary", "model_runtime_executed",
                    "weights_or_assets", "real_speech_or_corpus", "downloads",
                    "network_used", "provider_registered", "device_timing",
                    "listening", "benchmark_claim", "release_claim"):
            self.assertIs(reference.SCOPE[key], False, key)

    def test_public_surface_is_unchanged(self) -> None:
        self.assertTrue(reference.PUBLIC_SURFACE)
        for key, value in reference.PUBLIC_SURFACE.items():
            self.assertIs(value, False, key)


class DeclarationTests(unittest.TestCase):
    def test_vendor_family_and_rates(self) -> None:
        vendor = reference.vendor_record()
        self.assertEqual(vendor["family"], "Quail")
        self.assertEqual(vendor["component"], "ai-coustics-quail")
        self.assertEqual(vendor["sample_rates_hz"], [8000, 16000, 48000])
        self.assertEqual(vendor["claimed_latency_ms"], 30)
        self.assertTrue(vendor["source_reported_only"])
        self.assertFalse(vendor["reproduced_here"])
        self.assertFalse(vendor["qualifies"])

    def test_latency_arithmetic_is_not_a_measurement(self) -> None:
        self.assertEqual(reference.declared_latency_samples(8000), 240)
        self.assertEqual(reference.declared_latency_samples(16000), 480)
        self.assertEqual(reference.declared_latency_samples(48000), 1440)
        contract = reference.declared_contract()
        self.assertFalse(contract["declared_latency_is_measured"])
        self.assertEqual(contract["declared_latency_samples_by_rate"],
                         {"8000": 240, "16000": 480, "48000": 1440})

    def test_latency_rejects_unsupported_rate(self) -> None:
        for value in (44100, 0, -16000, True, 16000.0, "16000"):
            with self.assertRaises(reference.ReferenceError):
                reference.declared_latency_samples(value)

    def test_declared_contract_is_unverified(self) -> None:
        contract = reference.declared_contract()
        self.assertFalse(contract["official_geometry_verified"])
        self.assertFalse(contract["vendor_runtime_verified"])
        self.assertEqual(contract["process_contract"], "not_established")
        self.assertEqual(contract["reset_contract"], "not_established")
        self.assertEqual(contract["drain_contract"], "not_established")
        self.assertFalse(contract["qualifies"])

    def test_v0_grid_is_preserved(self) -> None:
        contract = reference.declared_contract()
        self.assertEqual(contract["host_grid"],
                         {"sample_rate_hz": 16000, "channels": 1,
                          "frame_samples": 160, "sample_format": "f32"})
        self.assertTrue(contract["installed_v0_unchanged"])


class GeometryTests(unittest.TestCase):
    def test_16k_160_is_v0_compatible(self) -> None:
        row = reference.validate_geometry(16000, 1, 160, "f32")
        self.assertTrue(row["v0_compatible"])
        self.assertFalse(row["resampling_required"])
        self.assertEqual(row["declared_latency_samples"], 480)
        self.assertFalse(row["qualifies"])

    def test_rate_variants_require_resampling(self) -> None:
        for rate, latency in ((8000, 240), (48000, 1440)):
            row = reference.validate_geometry(rate, 1, 160, "f32")
            self.assertFalse(row["v0_compatible"])
            self.assertTrue(row["resampling_required"])
            self.assertEqual(row["declared_latency_samples"], latency)

    def test_geometry_rejects_bad_inputs(self) -> None:
        cases = (
            (44100, 1, 160, "f32"),
            (16000, 2, 160, "f32"),
            (16000, 1, 320, "f32"),
            (16000, 1, 160, "int16"),
            (True, 1, 160, "f32"),
            (16000, 0, 160, "f32"),
            (16000, 1, 0, "f32"),
        )
        for case in cases:
            with self.assertRaises(reference.ReferenceError):
                reference.validate_geometry(*case)


class FixtureTests(unittest.TestCase):
    def test_fixture_geometry(self) -> None:
        fixture = reference.fixture_payload()
        self.assertEqual(fixture["samples"], 32000)
        self.assertEqual(fixture["frames"], 200)
        self.assertEqual(fixture["sample_rate_hz"], 16000)
        self.assertEqual(fixture["channels"], 1)
        self.assertFalse(fixture["is_speech"])
        self.assertFalse(fixture["is_corpus"])
        self.assertFalse(fixture["qualifies"])

    def test_segments_cover_the_fixture_exactly(self) -> None:
        fixture = reference.fixture_payload()
        cursor = 0
        for segment in fixture["segments"]:
            self.assertEqual(segment["start_sample"], cursor)
            cursor = segment["end_sample_exclusive"]
        self.assertEqual(cursor, fixture["samples"])

    def test_fixture_is_deterministic(self) -> None:
        first = reference.fixture_payload()
        second = reference.fixture_payload()
        self.assertEqual(first, second)
        self.assertEqual(first["clean_sha256"], second["clean_sha256"])
        self.assertEqual(first["mixture_sha256"], second["mixture_sha256"])

    def test_clean_and_mixture_differ(self) -> None:
        fixture = reference.fixture_payload()
        self.assertNotEqual(fixture["clean_sha256"],
                            fixture["mixture_sha256"])
        self.assertNotEqual(fixture["clean_sha256"], fixture["noise_sha256"])

    def test_clean_silence_is_exact(self) -> None:
        clean = reference.build_clean()
        self.assertTrue(all(value == 0.0 for value in clean[:3200]))
        self.assertTrue(all(value == 0.0 for value in clean[27200:]))

    def test_samples_are_quantized_finite_and_bounded(self) -> None:
        for values in (reference.build_clean(), reference.build_noise(),
                       reference.build_mixture()):
            self.assertEqual(len(values), reference.FIXTURE_SAMPLES)
            for value in values:
                self.assertTrue(math.isfinite(value))
                self.assertLessEqual(abs(value), 1.0)
                self.assertEqual(value, round(value * 32768.0) / 32768.0)


class ControlTests(unittest.TestCase):
    def test_identity_is_exact_passthrough(self) -> None:
        controls = reference.controls_payload()
        fixture = reference.fixture_payload()
        row = controls["rows"]["identity_noisy"]
        self.assertEqual(row["output_sha256"], fixture["mixture_sha256"])
        self.assertTrue(math.isfinite(row["si_sdr_db_vs_synthetic_clean"]))
        self.assertTrue(math.isfinite(row["snr_db_vs_synthetic_clean"]))

    def test_controls_are_not_candidate_results(self) -> None:
        controls = reference.controls_payload()
        self.assertFalse(controls["design"]["is_ai_coustics_quail"])
        self.assertFalse(controls["design"]["is_candidate_result"])
        for row in controls["rows"].values():
            self.assertFalse(row["is_candidate_result"])
            self.assertFalse(row["qualifies"])
            self.assertEqual(row["samples"], 32000)
            self.assertEqual(row["nonfinite_samples"], 0)
            for key in ("rms", "peak_abs"):
                self.assertTrue(math.isfinite(row[key]))

    def test_fixed_highpass_is_finite_and_bounded(self) -> None:
        controls = reference.controls_payload()
        row = controls["rows"]["fixed_highpass_noisy"]
        self.assertLessEqual(row["peak_abs"], 1.0)
        self.assertEqual(row["clipped_samples"], 0)
        self.assertTrue(math.isfinite(row["si_sdr_db_vs_synthetic_clean"]))
        self.assertLess(row["si_sdr_db_vs_synthetic_clean"],
                        controls["rows"]["identity_noisy"]
                        ["si_sdr_db_vs_synthetic_clean"])

    def test_silence_controls_are_exact_zero(self) -> None:
        controls = reference.controls_payload()
        self.assertTrue(controls["silence"]["identity_exact_zero"])
        self.assertTrue(controls["silence"]["fixed_highpass_exact_zero"])
        self.assertFalse(controls["silence"]["qualifies"])
        self.assertEqual(
            controls["rows"]["fixed_highpass_silence"]["peak_abs"], 0.0)

    def test_controls_are_deterministic(self) -> None:
        self.assertEqual(reference.controls_payload(),
                         reference.controls_payload())


class ManifestTests(unittest.TestCase):
    def test_valid_document_is_shape_only(self) -> None:
        manifest = reference.parse_manifest(
            reference._valid_manifest_document())
        self.assertTrue(manifest["shape_valid"])
        self.assertFalse(manifest["files_verified"])
        self.assertFalse(manifest["loaded"])
        self.assertFalse(manifest["executed"])
        self.assertFalse(manifest["official_identity"])
        self.assertFalse(manifest["qualifies"])

    def test_manifest_controls_reject_every_adverse_document(self) -> None:
        controls = reference.manifest_controls()
        self.assertEqual(controls[0]["control_id"], "valid_shape")
        self.assertTrue(controls[0]["accepted"])
        self.assertEqual(len(controls), 17)
        for row in controls[1:]:
            self.assertFalse(row["accepted"], row["control_id"])
            self.assertFalse(row["qualifies"])
        ids = {row["control_id"] for row in controls}
        for required in ("missing_artifact_id", "extra_field", "wrong_candidate",
                         "wrong_family", "relative_artifact_path",
                         "parent_traversal", "bad_hash_length",
                         "uppercase_hash", "checksum_prefix_mismatch",
                         "unsupported_rate", "boolean_rate", "stereo",
                         "terms_not_accepted", "wrong_attestation",
                         "duplicate_paths", "empty_sdk_version"):
            self.assertIn(required, ids)

    def test_manifest_rejects_missing_and_extra_fields(self) -> None:
        document = reference._valid_manifest_document()
        document.pop("artifact_id")
        with self.assertRaises(reference.ReferenceError):
            reference.parse_manifest(document)
        document = reference._valid_manifest_document()
        document["extra"] = True
        with self.assertRaises(reference.ReferenceError):
            reference.parse_manifest(document)

    def test_manifest_rejects_prefix_mismatch(self) -> None:
        document = reference._valid_manifest_document()
        document["provider_checksum_prefix"] = "b" * 12
        with self.assertRaises(reference.ReferenceError):
            reference.parse_manifest(document)

    def test_manifest_does_not_accept_a_prefix_as_full_hash(self) -> None:
        document = reference._valid_manifest_document()
        document["artifact_sha256"] = "a" * 12
        with self.assertRaises(reference.ReferenceError):
            reference.parse_manifest(document)

    def test_manifest_files_hash_only(self) -> None:
        document = reference._valid_manifest_document()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            payloads = {
                ("artifact_path", "artifact_sha256"): b"artifact",
                ("license_path", "license_sha256"): b"license",
                ("rights_approval_path", "rights_approval_sha256"): b"approval",
                ("runtime_path", "runtime_sha256"): b"runtime",
            }
            for index, ((path_key, sha_key), payload) in enumerate(
                    payloads.items()):
                path = base / ("file%d.bin" % index)
                path.write_bytes(payload)
                document[path_key] = str(path)
                document[sha_key] = reference.sha256_bytes(payload)
            document["provider_checksum_prefix"] = \
                document["artifact_sha256"][:12]
            manifest = reference.parse_manifest(document)
            result = reference.verify_manifest_files(manifest)
            self.assertTrue(result["files_verified"])
            self.assertTrue(result["bytes_hashed_only"])
            self.assertFalse(result["loaded"])
            self.assertFalse(result["executed"])
            self.assertFalse(result["official_identity"])
            self.assertFalse(result["qualifies"])

    def test_manifest_file_hash_mismatch_is_rejected(self) -> None:
        document = reference._valid_manifest_document()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            paths = {}
            for index, (path_key, sha_key) in enumerate((
                    ("artifact_path", "artifact_sha256"),
                    ("license_path", "license_sha256"),
                    ("rights_approval_path", "rights_approval_sha256"),
                    ("runtime_path", "runtime_sha256"))):
                path = base / ("file%d.bin" % index)
                path.write_bytes(b"payload%d" % index)
                document[path_key] = str(path)
                document[sha_key] = reference.sha256_bytes(b"payload%d" % index)
                paths[path_key] = str(path)
            document["artifact_sha256"] = "a" * 64
            document["provider_checksum_prefix"] = "a" * 12
            manifest = reference.parse_manifest(document)
            with self.assertRaises(reference.ReferenceError):
                reference.verify_manifest_files(manifest)

    def test_manifest_missing_files_are_rejected(self) -> None:
        manifest = reference.parse_manifest(
            reference._valid_manifest_document())
        with self.assertRaises(reference.ReferenceError):
            reference.verify_manifest_files(manifest)

    def test_manifest_path_rules(self) -> None:
        document = reference._valid_manifest_document()
        for value in ("relative.bin", "/caller/../escape.bin",
                      "/caller/./same.bin", "C:\\caller\\file.bin", "", 7):
            document["artifact_path"] = value
            with self.assertRaises(reference.ReferenceError):
                reference.parse_manifest(document)


class AdverseTests(unittest.TestCase):
    def test_adverse_audio_is_rejected_exactly(self) -> None:
        rows = reference.adverse_results()
        self.assertEqual(len(rows), 10)
        for row in rows:
            self.assertEqual(row["status"], "rejected", row["result_id"])
            self.assertTrue(row["matches_expected"], row["result_id"])
            self.assertFalse(row["qualifies"])
        ids = {row["result_id"] for row in rows}
        for required in ("nan_sample", "positive_infinity_sample",
                         "boolean_sample", "string_sample", "nested_sample",
                         "short_frame_159", "long_frame_161", "empty_frame",
                         "out_of_range_sample", "mapping_container"):
            self.assertIn(required, ids)

    def test_valid_frame_is_accepted(self) -> None:
        self.assertEqual(reference.validate_audio([0.0] * 160), 160)

    def test_nonfinite_never_silences(self) -> None:
        frame = [0.0] * 160
        frame[0] = float("nan")
        with self.assertRaises(reference.ReferenceError):
            reference.validate_audio(frame)

    def test_failure_controls_are_all_explicit(self) -> None:
        rows = reference.failure_controls()
        self.assertTrue(rows["all_explicit"])
        self.assertEqual(rows["rejected_audio_vectors"], 10)
        self.assertEqual(rows["rejected_manifest_documents"], 16)
        self.assertEqual(rows["blocked_release_gates"], 8)
        self.assertFalse(rows["qualifies"])
        for key, value in rows["checks"].items():
            self.assertIs(value, True, key)


class QualificationTests(unittest.TestCase):
    def test_missing_results_are_blocked_and_null(self) -> None:
        rows = reference.missing_results()
        self.assertGreaterEqual(len(rows), 10)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_qualification_slots_are_null(self) -> None:
        slots = reference.qualification_slots()
        for key, slot in slots.items():
            if key == "release":
                self.assertIsNone(slot["value"])
            else:
                self.assertIsNone(slot["value"], key)
            self.assertFalse(slot["qualifies"], key)

    def test_eight_gates_are_blocked(self) -> None:
        self.assertEqual(len(reference.RELEASE_GATES), 8)
        for gate in reference.RELEASE_GATES:
            self.assertEqual(gate["status"], "blocked")
            self.assertIsNone(gate["evidence"])
            self.assertFalse(gate["qualifies"])

    def test_qualification_is_not_qualified(self) -> None:
        self.assertEqual(reference.QUALIFICATION["status"], "not_qualified")
        self.assertEqual(reference.QUALIFICATION_STATUS, "not_qualified")
        self.assertTrue(reference.QUALIFICATION["incomplete"])
        self.assertTrue(reference.QUALIFICATION["proposal_only"])
        self.assertFalse(reference.QUALIFICATION["qualifies"])
        self.assertFalse(reference.QUALIFICATION["missing_result_promoted"])

    def test_acceptance_profile_is_non_qualifying(self) -> None:
        profile = reference.acceptance_profile()
        self.assertEqual(profile["profile"], "enhancement")
        self.assertFalse(profile["all_qualify"])
        self.assertFalse(profile["qualifies"])
        self.assertFalse(profile["missing_result_promoted"])
        allowed = {"synthetic_control_only", "blocked", "proposal_only"}
        for item in profile["items"]:
            self.assertIn(item["status"], allowed)
            self.assertFalse(item["qualifies"])

    def test_observed_provenance_is_not_measurement(self) -> None:
        provenance = reference.observed_provenance()
        self.assertFalse(provenance["reproduced_here"])
        for row in provenance["documented_context"]:
            self.assertFalse(row["reproduced_here"])
            self.assertFalse(row["is_measurement"])
            self.assertFalse(row["is_human_rating"])
            self.assertFalse(row["qualifies"])

    def test_artifact_assessment_records_absence(self) -> None:
        assessment = reference.artifact_assessment()
        self.assertTrue(assessment["all_required_absent"])
        self.assertFalse(assessment["vendor_artifact_present"])
        self.assertFalse(assessment["vendor_runtime_present"])
        self.assertFalse(assessment["rights_approval_present"])
        self.assertFalse(assessment["corpus_present"])
        self.assertFalse(assessment["package_assets_present"])
        self.assertFalse(assessment["qualifies"])
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))

    def test_ranking_is_withheld(self) -> None:
        ranking = reference.ranking_payload()
        self.assertEqual(ranking["order"], "not_ranked")
        self.assertIsNone(ranking["recommendation"])
        self.assertFalse(ranking["qualifies"])

    def test_required_artifacts_are_absent(self) -> None:
        self.assertEqual(len(reference.REQUIRED_ARTIFACTS), 8)
        for item in reference.REQUIRED_ARTIFACTS:
            self.assertFalse(item["present"], item["id"])
            self.assertTrue(item["rights_requirement"])
            self.assertTrue(item["why_blocked"])


class ReportTests(unittest.TestCase):
    def test_report_keys_are_exact(self) -> None:
        report = reference.build_report()
        self.assertEqual(set(report), reference.REPORT_KEYS)
        self.assertEqual(report["decision"], "DEFER")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["completeness"], "incomplete")
        self.assertEqual(report["profile"], "enhancement")

    def test_report_is_deterministic_and_three_runs(self) -> None:
        report = reference.build_report()
        regeneration = report["regeneration"]
        self.assertEqual(regeneration["runs"], 3)
        self.assertTrue(regeneration["byte_identical"])
        self.assertEqual(len(set(regeneration["canonical_digests"])), 1)
        payload, digest, canonical = reference.render_report()
        self.assertEqual(payload, reference.render_report()[0])
        self.assertEqual(digest, reference.sha256_bytes(payload))
        self.assertNotEqual(digest, canonical)

    def test_no_qualifying_value_anywhere(self) -> None:
        def walk(value: object) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "qualifies":
                        self.assertIs(item, False, key)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(reference.build_report())

    def test_contract_keys_and_pins(self) -> None:
        contract = reference.contract_payload()
        self.assertEqual(set(contract), reference.CONTRACT_KEYS)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertNotIn("contract.json", contract["artifact_pins"])
        self.assertNotIn("SOURCES.sha256", contract["artifact_pins"])
        for name in contract["local_files"]:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_strict_json_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            duplicate = base / "duplicate.json"
            duplicate.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(duplicate)
            nan = base / "nan.json"
            nan.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(nan)
            scalar = base / "scalar.json"
            scalar.write_text('1', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(scalar)
            valid = base / "valid.json"
            valid.write_text('{"b":2,"a":1}', encoding="utf-8")
            self.assertEqual(reference.read_strict_json(valid), {"b": 2, "a": 1})
        payload = reference.canonical_bytes({"b": 2, "a": 1})
        self.assertEqual(payload, b'{"a":1,"b":2}')

    def test_inspect_payload_is_non_qualifying(self) -> None:
        inspect = reference.inspect_payload()
        self.assertEqual(inspect["decision"], "DEFER")
        self.assertFalse(inspect["qualifies"])
        self.assertEqual(len(inspect["release_gates"]), 8)
        self.assertTrue(all(not gate["qualifies"]
                            for gate in inspect["release_gates"]))
        self.assertTrue(all(not item["present"]
                            for item in inspect["required_artifacts"]))


if __name__ == "__main__":
    unittest.main()
