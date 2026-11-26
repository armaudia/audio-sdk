# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for the AIx Speed ASR-guided planner DEFER package."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
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
        self.assertEqual(row["id"], "SDK-AIX-SPEED-ASR-GUIDED-PLANNER")
        self.assertEqual(row["component"], "aix-speed-asr-guided-planner")
        self.assertEqual(row["mode"], "research-control")
        self.assertEqual(row["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(row["branch"], reference.BRANCH)
        self.assertEqual(row["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"])

    def test_mutable_board_is_not_gated_or_hashed(self) -> None:
        provenance = reference.MUTABLE_PROVENANCE
        self.assertFalse(provenance["hashed"])
        self.assertFalse(provenance["gate"])
        self.assertTrue(provenance["mutable"])
        self.assertNotIn("sha256_at_read", provenance)
        self.assertNotIn("sha256_now", provenance)

    def test_scope_is_local_and_synthetic(self) -> None:
        self.assertTrue(reference.SCOPE["task_local_only"])
        self.assertTrue(reference.SCOPE["synthetic_only"])
        for key in ("aix_speed_source", "licensed_source_or_binary",
                    "trained_weights", "model_runtime_executed",
                    "asr_runtime_executed", "heldout_transcripts",
                    "real_speech_or_corpus", "audio_processed",
                    "asr_proxy_result", "listening", "downloads",
                    "network_used", "provider_registered", "device_timing",
                    "benchmark_claim", "release_claim"):
            self.assertIs(reference.SCOPE[key], False, key)

    def test_public_surface_is_unchanged(self) -> None:
        self.assertTrue(reference.PUBLIC_SURFACE)
        for key, value in reference.PUBLIC_SURFACE.items():
            self.assertIs(value, False, key)

    def test_task_local_file_set(self) -> None:
        actual = {path.name for path in ROOT.iterdir() if path.is_file()}
        self.assertEqual(actual, set(reference.LOCAL_FILES))


class CandidateTests(unittest.TestCase):
    def test_candidate_record_is_source_reported_only(self) -> None:
        record = reference.candidate_record()
        self.assertEqual(record["candidate"], "AIx Speed")
        self.assertEqual(record["family"], "AIx Speed")
        self.assertEqual(record["component"], reference.COMPONENT)
        self.assertEqual(record["locator"], "https://arxiv.org/abs/2403.02938")
        self.assertFalse(record["public_implementation_found"])
        self.assertFalse(record["artifact_present"])
        self.assertFalse(record["weights_present"])
        self.assertFalse(record["runtime_present"])
        self.assertFalse(record["license_reviewed"])
        self.assertTrue(record["source_reported_only"])
        self.assertFalse(record["reproduced_here"])
        self.assertFalse(record["qualifies"])

    def test_declared_contract_is_unverified(self) -> None:
        contract = reference.declared_contract()
        self.assertEqual(contract["declared_rate_range"], ["3/4", "3/2"])
        self.assertEqual(contract["declared_protected_speech_ceiling"], "1")
        self.assertEqual(contract["declared_lookahead_ms_range"], [200, 1000])
        self.assertFalse(contract["rate_range_is_a_measurement"])
        self.assertFalse(contract["lookahead_is_a_measurement"])
        for key in ("per_phoneme_alignment_contract",
                    "rate_application_contract", "content_delay_contract",
                    "availability_contract", "buffering_contract",
                    "reset_contract", "drain_contract",
                    "final_partial_window_contract"):
            self.assertEqual(contract[key], "not_established", key)
        self.assertFalse(contract["official_geometry_verified"])
        self.assertFalse(contract["aix_speed_runtime_verified"])
        self.assertTrue(contract["installed_v0_unchanged"])
        self.assertFalse(contract["qualifies"])

    def test_v0_grid_is_preserved(self) -> None:
        grid = reference.declared_contract()["host_grid"]
        self.assertEqual(grid, {"sample_rate_hz": 16000, "channels": 1,
                                "frame_samples": 160, "sample_format": "f32"})


class RateTests(unittest.TestCase):
    def test_rate_floor_and_ceiling(self) -> None:
        self.assertEqual(reference.parse_rate(3, 4), Fraction(3, 4))
        self.assertEqual(reference.parse_rate(3, 2), Fraction(3, 2))
        for numerator, denominator in ((1, 2), (2, 1)):
            with self.assertRaises(reference.ReferenceError):
                reference.parse_rate(numerator, denominator)

    def test_rate_rejects_non_integers(self) -> None:
        for numerator, denominator in (
                (float("nan"), 2), (float("inf"), 2), (True, 2),
                ("3", 2), (3, True), (3, 0), (-3, 2)):
            with self.assertRaises(reference.ReferenceError):
                reference.parse_rate(numerator, denominator)

    def test_content_guard(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference._check_content_guard("speech", Fraction(6, 5))
        with self.assertRaises(reference.ReferenceError):
            reference._check_content_guard("silence", Fraction(4, 5))
        with self.assertRaises(reference.ReferenceError):
            reference._check_content_guard("music", Fraction(6, 5))
        with self.assertRaises(reference.ReferenceError):
            reference._check_content_guard("tone", Fraction(1, 1))


class EnvelopeTests(unittest.TestCase):
    def test_control_envelope_geometry(self) -> None:
        payload = reference.control_envelope_payload()
        guided = payload["guided"]
        self.assertEqual(guided["total_input_samples"], 16000)
        self.assertEqual(guided["total_output_samples"], "16000")
        self.assertTrue(guided["output_samples_is_integer"])
        self.assertEqual(guided["average_rate"], "1")
        self.assertEqual(guided["duration_delta_samples"], "0")
        self.assertEqual(guided["duration_delta_ms"], 0.0)
        self.assertEqual(guided["min_rate"], "4/5")
        self.assertEqual(guided["max_rate"], "3/2")
        self.assertTrue(guided["source_output_mapping_exact"])
        self.assertFalse(guided["qualifies"])

    def test_control_segments_cover_source_exactly(self) -> None:
        segments = reference.control_envelope_payload()["guided"]["segments"]
        cursor = 0
        for segment in segments:
            self.assertEqual(segment["start_sample"], cursor)
            cursor = segment["end_sample_exclusive"]
        self.assertEqual(cursor, reference.CONTROL_TOTAL_SAMPLES)

    def test_control_output_mapping_is_exact(self) -> None:
        rows = reference.control_envelope_payload()["guided"]["segments"]
        expected = [("0", "1600"), ("1600", "2600"),
                    ("2600", "7600"), ("7600", "16000")]
        self.assertEqual(
            [(row["output_start_sample"], row["output_end_sample"])
             for row in rows], expected)

    def test_control_rates_are_guarded(self) -> None:
        rows = reference.control_envelope_payload()["guided"]["segments"]
        for row in rows:
            rate = Fraction(row["rate"])
            if row["content_class"] == "speech":
                self.assertLessEqual(rate, 1, row["segment_id"])
            if row["content_class"] in ("silence", "filler"):
                self.assertGreaterEqual(rate, 1, row["segment_id"])

    def test_identity_control_is_exact_1x(self) -> None:
        identity = reference.control_envelope_payload()["identity"]
        self.assertEqual(identity["min_rate"], "1")
        self.assertEqual(identity["max_rate"], "1")
        self.assertEqual(identity["total_output_samples"], "16000")
        self.assertEqual(identity["duration_delta_samples"], "0")
        self.assertEqual(identity["segments"][0]["output_start_sample"], "0")
        self.assertEqual(identity["segments"][0]["output_end_sample"], "16000")

    def test_control_is_not_aix_speed_or_candidate(self) -> None:
        payload = reference.control_envelope_payload()
        self.assertFalse(payload["design"]["policy_is_aix_speed"])
        self.assertFalse(payload["design"]["is_candidate_result"])
        self.assertFalse(payload["qualifies"])
        for key in ("guided", "identity"):
            self.assertFalse(payload[key]["is_aix_speed"], key)
            self.assertFalse(payload[key]["is_candidate_result"], key)
            self.assertFalse(payload[key]["qualifies"], key)

    def test_asr_proxy_and_listening_are_separate_and_blocked(self) -> None:
        payload = reference.control_envelope_payload()
        self.assertEqual(payload["asr_proxy"]["status"], "blocked")
        self.assertEqual(payload["listening"]["status"], "blocked")
        self.assertIsNone(payload["asr_proxy"]["wer_delta_pp"])
        self.assertIsNone(payload["asr_proxy"]["cer_delta_pp"])
        self.assertIsNone(payload["listening"]["comprehension"])
        self.assertFalse(payload["separation"]["asr_proxy_is_listening"])
        self.assertIsNone(payload["separation"]["pooled_metric"])
        self.assertFalse(payload["separation"]["qualifies"])

    def test_control_is_deterministic_and_digest_shaped(self) -> None:
        first = reference.control_envelope_payload()
        second = reference.control_envelope_payload()
        self.assertEqual(first, second)
        self.assertEqual(
            len(first["guided"]["mapping_sha256"]), 64)
        int(first["guided"]["mapping_sha256"], 16)

    def test_valid_envelope_is_accepted(self) -> None:
        self.assertEqual(
            len(reference.validate_envelope(
                reference._control_segment_documents())), 4)

    def test_envelope_rejects_bad_coverage_and_claims(self) -> None:
        cases = (
            reference._mutated_control_segments(1, "start_sample", 2401),
            reference._mutated_control_segments(1, "start_sample", 2399),
            reference._mutated_control_segments(
                3, "end_sample_exclusive", 15999),
            reference._mutated_control_segments(
                2, "is_candidate_result", True),
            reference._mutated_control_segments(
                2, "asr_proxy_score", float("inf")),
            [],
            {"segments": []},
        )
        for value in cases:
            with self.assertRaises(reference.ReferenceError):
                reference.validate_envelope(value)

    def test_envelope_rejects_speech_speedup_and_silence_slowdown(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_envelope(reference._rate_case(3, 6, 5))
        with self.assertRaises(reference.ReferenceError):
            reference.validate_envelope(reference._rate_case(0, 4, 5))

    def test_nonfinite_never_becomes_a_score(self) -> None:
        segments = reference._control_segment_documents()
        segments[2]["asr_proxy_score"] = float("nan")
        with self.assertRaises(reference.ReferenceError):
            reference.validate_envelope(segments)


class ManifestTests(unittest.TestCase):
    def test_valid_document_is_shape_only(self) -> None:
        manifest = reference.parse_manifest(
            reference._valid_manifest_document())
        self.assertTrue(manifest["shape_valid"])
        self.assertFalse(manifest["files_verified"])
        self.assertFalse(manifest["loaded"])
        self.assertFalse(manifest["executed"])
        self.assertFalse(manifest["official_identity"])
        self.assertFalse(manifest["asr_proxy_is_listening"])
        self.assertFalse(manifest["qualifies"])

    def test_manifest_controls_reject_every_adverse_document(self) -> None:
        controls = reference.manifest_controls()
        self.assertEqual(controls[0]["control_id"], "valid_shape")
        self.assertTrue(controls[0]["accepted"])
        self.assertEqual(len(controls), 18)
        for row in controls[1:]:
            self.assertFalse(row["accepted"], row["control_id"])
            self.assertFalse(row["qualifies"])
        ids = {row["control_id"] for row in controls}
        for required in ("missing_artifact_id", "extra_field", "wrong_candidate",
                         "wrong_family", "relative_weights_path",
                         "parent_traversal", "bad_source_revision",
                         "uppercase_source_hash", "bad_weights_hash_length",
                         "duplicate_paths", "terms_not_accepted",
                         "wrong_attestation", "empty_transcript_cohort",
                         "missing_asr_proxy_scorer", "listening_not_separate",
                         "listening_not_established", "empty_artifact_id"):
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

    def test_manifest_enforces_asr_listening_separation(self) -> None:
        document = reference._valid_manifest_document()
        document["listening_protocol_id"] = document["asr_proxy_scorer_id"]
        with self.assertRaises(reference.ReferenceError):
            reference.parse_manifest(document)
        document = reference._valid_manifest_document()
        document["listening_protocol_id"] = "not_established"
        with self.assertRaises(reference.ReferenceError):
            reference.parse_manifest(document)

    def test_manifest_files_hash_only(self) -> None:
        document = reference._valid_manifest_document()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            payloads = {
                ("source_path", "source_sha256"): b"source",
                ("weights_path", "weights_sha256"): b"weights",
                ("runtime_path", "runtime_sha256"): b"runtime",
                ("license_path", "license_sha256"): b"license",
                ("rights_approval_path", "rights_approval_sha256"): b"approval",
                ("transcript_manifest_path",
                 "transcript_manifest_sha256"): b"transcripts",
            }
            for index, ((path_key, sha_key), payload) in enumerate(
                    payloads.items()):
                path = base / ("file%d.bin" % index)
                path.write_bytes(payload)
                document[path_key] = str(path)
                document[sha_key] = reference.sha256_bytes(payload)
            manifest = reference.parse_manifest(document)
            result = reference.verify_manifest_files(manifest)
            self.assertTrue(result["files_verified"])
            self.assertTrue(result["bytes_hashed_only"])
            self.assertFalse(result["loaded"])
            self.assertFalse(result["executed"])
            self.assertFalse(result["official_identity"])
            self.assertFalse(result["asr_proxy_is_listening"])
            self.assertFalse(result["qualifies"])

    def test_manifest_file_hash_mismatch_is_rejected(self) -> None:
        document = reference._valid_manifest_document()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for index, (path_key, sha_key) in enumerate((
                    ("source_path", "source_sha256"),
                    ("weights_path", "weights_sha256"),
                    ("runtime_path", "runtime_sha256"),
                    ("license_path", "license_sha256"),
                    ("rights_approval_path", "rights_approval_sha256"),
                    ("transcript_manifest_path",
                     "transcript_manifest_sha256"))):
                path = base / ("file%d.bin" % index)
                path.write_bytes(b"payload%d" % index)
                document[path_key] = str(path)
                document[sha_key] = reference.sha256_bytes(b"payload%d" % index)
            document["weights_sha256"] = "8" * 64
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
            document["weights_path"] = value
            with self.assertRaises(reference.ReferenceError):
                reference.parse_manifest(document)


class AdverseTests(unittest.TestCase):
    def test_adverse_envelopes_are_rejected_exactly(self) -> None:
        rows = reference.adverse_results()
        self.assertEqual(len(rows), 24)
        for row in rows:
            self.assertEqual(row["status"], "rejected", row["result_id"])
            self.assertTrue(row["matches_expected"], row["result_id"])
            self.assertFalse(row["qualifies"])
        ids = {row["result_id"] for row in rows}
        for required in ("nan_rate_numerator", "infinity_rate_denominator",
                         "boolean_rate_numerator", "string_rate_numerator",
                         "zero_denominator", "negative_numerator",
                         "rate_below_floor", "rate_above_ceiling",
                         "speech_speedup", "silence_slowing", "interval_gap",
                         "interval_overlap", "reversed_interval",
                         "uncovered_tail", "duplicate_segment_id",
                         "nonfinite_asr_score", "boolean_asr_score",
                         "asr_score_out_of_range", "candidate_claim",
                         "non_object_segment", "empty_envelope",
                         "mapping_container", "extra_segment_field",
                         "unsupported_content_class"):
            self.assertIn(required, ids)

    def test_failure_controls_are_all_explicit(self) -> None:
        rows = reference.failure_controls()
        self.assertTrue(rows["all_explicit"])
        self.assertEqual(rows["rejected_envelope_documents"], 24)
        self.assertEqual(rows["rejected_manifest_documents"], 17)
        self.assertEqual(rows["blocked_release_gates"], 8)
        self.assertFalse(rows["qualifies"])
        for key, value in rows["checks"].items():
            self.assertIs(value, True, key)


class QualificationTests(unittest.TestCase):
    def test_missing_results_are_blocked_and_null(self) -> None:
        rows = reference.missing_results()
        self.assertEqual(len(rows), 13)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_qualification_slots_are_null(self) -> None:
        slots = reference.qualification_slots()
        self.assertEqual(len(slots), 9)
        for key, slot in slots.items():
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
        self.assertFalse(reference.QUALIFICATION["asr_proxy_is_listening"])
        self.assertTrue(reference.QUALIFICATION["all_release_gates_blocked"])

    def test_acceptance_profile_is_rate_and_non_qualifying(self) -> None:
        profile = reference.acceptance_profile()
        self.assertEqual(profile["profile"], "rate")
        self.assertFalse(profile["all_qualify"])
        self.assertFalse(profile["qualifies"])
        self.assertFalse(profile["missing_result_promoted"])
        allowed = {"synthetic_control_only", "blocked", "proposal_only"}
        for item in profile["items"]:
            self.assertIn(item["status"], allowed)
            self.assertFalse(item["qualifies"])
        items = {item["item"] for item in profile["items"]}
        for required in ("source_output_mapping", "duration_identity",
                         "pitch_preservation", "transient_audibility",
                         "playback_buffering_and_rebuffer", "unity_1x_control",
                         "rate_changes_step_and_ramp", "unfamiliar_speech_and_music",
                         "final_partial_window", "speech_preservation",
                         "asr_proxy_separate_from_listening",
                         "listening_or_comprehension"):
            self.assertIn(required, items)

    def test_observed_provenance_is_not_measurement(self) -> None:
        provenance = reference.observed_provenance()
        self.assertFalse(provenance["reproduced_here"])
        self.assertFalse(provenance["asr_proxy_is_listening"])
        for row in provenance["documented_context"]:
            self.assertFalse(row["reproduced_here"])
            self.assertFalse(row["is_measurement"])
            self.assertFalse(row["is_human_rating"])
            self.assertFalse(row["qualifies"])

    def test_artifact_assessment_records_absence(self) -> None:
        assessment = reference.artifact_assessment()
        self.assertTrue(assessment["all_required_absent"])
        for key in ("aix_speed_source_present", "weights_present",
                    "runtime_present", "license_approved",
                    "heldout_transcripts_present", "adapter_present",
                    "package_assets_present"):
            self.assertFalse(assessment[key], key)
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
        self.assertEqual(report["profile"], "rate")
        self.assertEqual(
            report["status"], "proposal_only_incomplete_not_qualified")

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
        self.assertEqual(contract["profile"], "rate")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertNotIn("contract.json", contract["artifact_pins"])
        self.assertNotIn("SOURCES.sha256", contract["artifact_pins"])
        self.assertEqual(contract["local_files"],
                         list(reference.LOCAL_FILES))
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
        self.assertEqual(inspect["control_envelope"]["guided_average_rate"],
                         "1")
        self.assertFalse(
            inspect["control_envelope"]["asr_proxy_is_listening"])
        self.assertEqual(len(inspect["release_gates"]), 8)
        self.assertTrue(all(not gate["qualifies"]
                            for gate in inspect["release_gates"]))
        self.assertTrue(all(not item["present"]
                            for item in inspect["required_artifacts"]))

    def test_render_report_digest_matches_bytes(self) -> None:
        payload, digest, _canonical = reference.render_report()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), digest)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        json.loads(payload.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
