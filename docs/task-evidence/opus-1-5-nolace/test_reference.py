# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit and evidence-bundle tests for the Opus 1.5 NoLACE blocker package."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import reference
import run
import verify

ROOT = Path(__file__).resolve().parent


class ConstantsTests(unittest.TestCase):
    def test_task_row_identity(self):
        row = reference.TASK_ROW_IDENTITY
        self.assertEqual(row["id"], "SDK-OPUS-1-5-NOLACE")
        self.assertEqual(row["title"], "Opus 1.5 NoLACE")
        self.assertEqual(row["repository"], "audio-sdk")
        self.assertEqual(row["mode"], "feasibility")
        self.assertEqual(row["component"], "opus-1-5-nolace")
        self.assertEqual(row["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(row["branch"], reference.BRANCH)

    def test_source_pins_exclude_mutable_board(self):
        self.assertNotIn("audio-benchmark-platform/plan/swarm/TASKS.json",
                         reference.SOURCE_PINS)
        self.assertGreaterEqual(len(reference.SOURCE_PINS), 6)
        for digest in reference.SOURCE_PINS.values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_boundary_and_sibling_pins_are_sha256(self):
        for pins in (reference.BOUNDARY_PINS, reference.SIBLING_PINS):
            self.assertTrue(pins)
            for digest in pins.values():
                self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_mutable_provenance_is_not_hashed(self):
        provenance = reference.MUTABLE_PROVENANCE
        self.assertFalse(provenance["gate"])
        self.assertFalse(provenance["hashed"])
        self.assertNotIn("sha256_at_read", provenance)

    def test_eight_release_gates_blocked(self):
        gates = reference.RELEASE_GATES
        self.assertEqual(len(gates), 8)
        self.assertEqual(len({gate["id"] for gate in gates}), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertIsNone(gate["evidence"])

    def test_status_and_qualification(self):
        self.assertEqual(reference.STATUS, "proposal_only_not_qualified")
        self.assertEqual(reference.COMPLETENESS, "incomplete")
        self.assertEqual(reference.DECISION, "DEFER")
        self.assertEqual(reference.QUALIFICATION["status"], "not_qualified")
        self.assertFalse(reference.QUALIFICATION["qualifies"])
        self.assertTrue(reference.QUALIFICATION["incomplete"])

    def test_public_surface_all_false(self):
        self.assertTrue(reference.PUBLIC_SURFACE)
        self.assertTrue(all(value is False for value in reference.PUBLIC_SURFACE.values()))

    def test_scope_rejects_real_assets(self):
        for key in ("real_runtime", "licensed_source_or_binary", "weights_or_assets",
                    "real_speech_or_corpus", "real_packet_trace", "downloads",
                    "listening", "device_timing", "benchmark_claim", "release_claim"):
            self.assertFalse(reference.SCOPE[key])

    def test_category_fit_is_codec_integrated(self):
        self.assertTrue(reference.CATEGORY_FIT["is_codec"])
        self.assertTrue(reference.CATEGORY_FIT["is_decoder_postfilter_mode"])
        self.assertFalse(reference.CATEGORY_FIT["is_standalone_postfilter"])
        self.assertFalse(reference.CATEGORY_FIT["is_packet_loss_concealment"])
        self.assertEqual(reference.CATEGORY_FIT["evaluated_category"], "restoration")


class StrictJsonTests(unittest.TestCase):
    def test_contract_and_report_are_strict_json(self):
        reference.read_strict_object(ROOT / "contract.json")
        reference.read_strict_object(ROOT / "report.json")

    def test_duplicate_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_nonfinite_constant_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nan.json"
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_non_object_root_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "array.json"
            path.write_text('[1,2,3]', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_object(path)

    def test_canonical_bytes_sorted_and_newline(self):
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": 2}),
                         b'{"a":2,"b":1}\n')

    def test_canonical_report_digest_matches_bytes(self):
        text, digest = reference.canonical_report({"z": 1, "a": [1, 2]})
        self.assertEqual(digest, hashlib.sha256(text.encode("utf-8")).hexdigest())


class FixtureTests(unittest.TestCase):
    def test_fixture_deterministic(self):
        self.assertEqual(reference.synthetic_samples(), reference.synthetic_samples())

    def test_fixture_lengths(self):
        self.assertEqual(len(reference.synthetic_samples()), reference.FULL_FIXTURE_SAMPLES)
        self.assertEqual(len(reference.probe_samples()), reference.PROBE_SAMPLES)

    def test_fixture_finite_and_bounded(self):
        values = reference.probe_samples()
        self.assertTrue(all(math.isfinite(value) for value in values))
        self.assertLessEqual(max(abs(value) for value in values), reference.MAX_ABS_INPUT)

    def test_frame_view(self):
        frames = reference.frame_view(reference.probe_samples())
        self.assertEqual(len(frames), 3)
        self.assertTrue(all(len(frame) == reference.FRAME_SAMPLES for frame in frames))

    def test_frame_view_rejects_partial(self):
        with self.assertRaises(reference.ReferenceError):
            reference.frame_view(reference.probe_samples()[:161])

    def test_fixture_digests_are_sha256(self):
        record = reference.pcm_fixture_record()
        self.assertRegex(record["full_digest"], r"^[0-9a-f]{64}$")
        self.assertRegex(record["probe_digest"], r"^[0-9a-f]{64}$")

    def test_packet_schedule_geometry(self):
        schedule = reference.packet_schedule()
        self.assertEqual([item["index"] for item in schedule], list(range(len(schedule))))
        self.assertTrue(all(item["duration_samples"] in reference.PACKET_DURATIONS
                            for item in schedule))
        self.assertTrue(any(not item["present"] for item in schedule))
        self.assertEqual(sum(item["duration_samples"] for item in schedule) % 160, 0)

    def test_packet_fixture_record(self):
        record = reference.packet_fixture_record()
        self.assertEqual(record["sample_rate_hz"], 16000)
        self.assertEqual(record["packet_count"], len(reference.packet_schedule()))
        self.assertEqual(record["total_scheduled_samples"],
                         record["present_samples"] + record["missing_samples"])
        self.assertRegex(record["schedule_digest"], r"^[0-9a-f]{64}$")


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.samples = list(reference.probe_samples())
        self.schedule = reference.packet_schedule()

    def request(self, operation, **fields):
        return reference.make_request(operation, **fields)

    def test_boundary_accounting_identity(self):
        result = reference.probe(self.request("boundary_accounting", samples=self.samples))
        self.assertEqual(result["status"], "analytic_identity_only")
        self.assertEqual(result["input_samples"], result["output_samples"])
        self.assertEqual(result["frames"], 3)
        self.assertEqual(result["duration_error_samples"], 0)
        self.assertFalse(result["qualifies"])

    def test_packet_accounting_analytic_only(self):
        result = reference.probe(self.request("packet_accounting", packets=self.schedule))
        self.assertEqual(result["status"], "analytic_packet_geometry_only")
        self.assertFalse(result["codec_decode"])
        self.assertFalse(result["decoder_compatibility_verified"])
        self.assertEqual(result["packet_count"], len(self.schedule))
        self.assertEqual(result["missing_packets"], 1)
        self.assertFalse(result["qualifies"])

    def test_postfilter_nolace_blocked(self):
        result = reference.probe(self.request("postfilter", packets=self.schedule,
                                              postfilter_mode="nolace"))
        self.assertEqual(result["status"], "blocked_missing_licensed_runtime")
        self.assertEqual(result["reason"], "no_licensed_opus_1_5_decoder_for_nolace")
        self.assertIsNone(result["output_samples"])
        self.assertFalse(result["postfilter_isolation_verified"])

    def test_postfilter_lace_contrast_blocked(self):
        result = reference.probe(self.request("postfilter", packets=self.schedule,
                                              postfilter_mode="lace"))
        self.assertEqual(result["status"], "blocked_missing_licensed_runtime")
        self.assertEqual(result["reason"], "no_licensed_opus_1_5_decoder_for_lace_contrast")
        self.assertIsNone(result["decoded_intervals"])

    def test_compatibility_opus_1_5_blocked(self):
        result = reference.probe(self.request("compatibility", packets=self.schedule,
                                              decoder_revision="opus-1.5"))
        self.assertEqual(result["status"], "blocked_missing_licensed_runtime")
        self.assertFalse(result["compatibility_verified"])

    def test_compatibility_opus_1_4_adverse(self):
        result = reference.probe(self.request("compatibility", packets=self.schedule,
                                              decoder_revision="opus-1.4"))
        self.assertEqual(result["status"], "blocked_decoder_revision_mismatch")
        self.assertEqual(result["classification"],
                         "adverse_cross_version_compatibility_retained_not_validated")
        self.assertFalse(result["qualifies"])

    def test_missing_input_rejected(self):
        result = reference.probe(self.request("boundary_accounting"))
        self.assertEqual(result["status"], "rejected_missing_input")

    def test_partial_frame_rejected(self):
        result = reference.probe(self.request("boundary_accounting",
                                              samples=self.samples[:161]))
        self.assertEqual(result["status"], "rejected_partial_frame")

    def test_wrong_type_sample_rejected(self):
        result = reference.probe(self.request("boundary_accounting",
                                              samples=["x"] + self.samples[1:]))
        self.assertEqual(result["status"], "rejected_wrong_type")

    def test_nonfinite_sample_rejected(self):
        result = reference.probe(self.request("boundary_accounting",
                                              samples=[float("nan")] + self.samples[1:]))
        self.assertEqual(result["status"], "rejected_nonfinite")

    def test_out_of_range_sample_rejected(self):
        result = reference.probe(self.request("boundary_accounting",
                                              samples=[99.0] + self.samples[1:]))
        self.assertEqual(result["status"], "rejected_out_of_range")

    def test_missing_packets_rejected(self):
        result = reference.probe(self.request("packet_accounting"))
        self.assertEqual(result["status"], "rejected_missing_packets")

    def test_empty_packets_rejected(self):
        result = reference.probe(self.request("packet_accounting", packets=[]))
        self.assertEqual(result["status"], "rejected_empty_packets")

    def test_partial_packet_duration_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], duration_samples=240)]))
        self.assertEqual(result["status"], "rejected_partial_frame")

    def test_unsupported_packet_duration_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], duration_samples=640)]))
        self.assertEqual(result["status"], "rejected_unsupported_duration")

    def test_packet_order_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], index=1), dict(self.schedule[1], index=0)]))
        self.assertEqual(result["status"], "rejected_packet_order")

    def test_wrong_packet_fields_rejected(self):
        result = reference.probe(self.request("packet_accounting", packets=[{"index": 0}]))
        self.assertEqual(result["status"], "rejected_invalid_packet_fields")

    def test_nonfinite_packet_bytes_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], payload_bytes=float("inf"))]))
        self.assertEqual(result["status"], "rejected_nonfinite")

    def test_wrong_type_packet_bytes_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], payload_bytes="40")]))
        self.assertEqual(result["status"], "rejected_wrong_type")

    def test_fractional_packet_bytes_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], payload_bytes=40.5)]))
        self.assertEqual(result["status"], "rejected_wrong_type")

    def test_out_of_range_packet_bytes_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], payload_bytes=4096)]))
        self.assertEqual(result["status"], "rejected_out_of_range")

    def test_negative_packet_bytes_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], payload_bytes=-1)]))
        self.assertEqual(result["status"], "rejected_out_of_range")

    def test_wrong_present_type_rejected(self):
        result = reference.probe(self.request(
            "packet_accounting",
            packets=[dict(self.schedule[0], present=1)]))
        self.assertEqual(result["status"], "rejected_wrong_type")

    def test_missing_postfilter_mode_rejected(self):
        result = reference.probe(self.request("postfilter", packets=self.schedule))
        self.assertEqual(result["status"], "rejected_missing_postfilter_mode")

    def test_unknown_postfilter_mode_rejected(self):
        result = reference.probe(self.request("postfilter", packets=self.schedule,
                                              postfilter_mode="neural"))
        self.assertEqual(result["status"], "rejected_unknown_postfilter_mode")

    def test_wrong_postfilter_type_rejected(self):
        result = reference.probe(self.request("postfilter", packets=self.schedule,
                                              postfilter_mode=5))
        self.assertEqual(result["status"], "rejected_wrong_type")

    def test_unknown_decoder_revision_rejected(self):
        result = reference.probe(self.request("compatibility", packets=self.schedule,
                                              decoder_revision="opus-9"))
        self.assertEqual(result["status"], "rejected_unknown_decoder_revision")

    def test_missing_decoder_revision_rejected(self):
        result = reference.probe(self.request("compatibility", packets=self.schedule))
        self.assertEqual(result["status"], "rejected_missing_decoder_revision")

    def test_runtime_claim_blocked(self):
        result = reference.probe(self.request("runtime", runtime="opus-1.5-nolace"))
        self.assertEqual(result["status"], "blocked_missing_licensed_runtime")
        self.assertFalse(result["runtime_presence"]["present"])

    def test_unknown_runtime_rejected(self):
        result = reference.probe(self.request("runtime", runtime="other"))
        self.assertEqual(result["status"], "rejected_unknown_runtime")

    def test_missing_runtime_rejected(self):
        result = reference.probe(self.request("runtime"))
        self.assertEqual(result["status"], "rejected_missing_runtime")

    def test_cohort_claim_blocked(self):
        result = reference.probe(self.request(
            "cohort", cohort="rights_cleared_low_bitrate_opus_packets"))
        self.assertEqual(result["status"], "blocked_missing_rights_cleared_packet_corpus")

    def test_unknown_cohort_rejected(self):
        result = reference.probe(self.request("cohort", cohort="other"))
        self.assertEqual(result["status"], "rejected_unknown_cohort")

    def test_missing_cohort_rejected(self):
        result = reference.probe(self.request("cohort"))
        self.assertEqual(result["status"], "rejected_missing_cohort")

    def test_structural_request_errors(self):
        with self.assertRaises(reference.RequestError):
            reference.validate_request({"protocol_version": 1})
        bad_ref = dict(reference.make_request("runtime", runtime="opus-1.5-nolace"),
                       candidate_ref={"kind": "wrong"})
        with self.assertRaises(reference.RequestError):
            reference.validate_request(bad_ref)
        bad_adapter = dict(reference.make_request("runtime", runtime="opus-1.5-nolace"),
                           adapter_ref={"kind": "wrong"})
        with self.assertRaises(reference.RequestError):
            reference.validate_request(bad_adapter)
        bad_config = dict(reference.make_request("runtime", runtime="opus-1.5-nolace"),
                          configuration={"profile": "other"})
        with self.assertRaises(reference.RequestError):
            reference.validate_request(bad_config)
        bad_version = dict(reference.make_request("runtime", runtime="opus-1.5-nolace"),
                           protocol_version=2)
        with self.assertRaises(reference.RequestError):
            reference.validate_request(bad_version)
        bad_operation = dict(reference.make_request("runtime", runtime="opus-1.5-nolace"),
                             operation="other")
        with self.assertRaises(reference.RequestError):
            reference.validate_request(bad_operation)

    def test_all_representative_results_do_not_qualify(self):
        for result in reference.representative_probes():
            self.assertFalse(result["qualifies"], result["case_id"])

    def test_failure_controls_complete(self):
        controls = reference.failure_controls()
        self.assertTrue(controls["all_explicit"])
        self.assertTrue(all(controls["checks"].values()))
        self.assertGreater(controls["rejected_count"], 0)
        self.assertGreater(controls["blocked_count"], 0)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.read_strict_object(ROOT / "report.json")
        cls.contract = reference.read_strict_object(ROOT / "contract.json")

    def test_report_disposition(self):
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["completeness"], "incomplete")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")

    def test_report_eight_blocked_gates(self):
        self.assertEqual(len(self.report["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in self.report["release_gates"]))
        self.assertTrue(all(gate["qualifies"] is False for gate in self.report["release_gates"]))

    def test_restoration_profile_application(self):
        profile = self.report["restoration_profile_application"]
        self.assertEqual(profile["profile"], "restoration")
        self.assertTrue(profile["all_blocked_or_analytic"])
        self.assertFalse(profile["qualifies"])
        self.assertFalse(profile["missing_result_promoted"])
        self.assertTrue(profile["required_elements"])

    def test_probe_cases_present(self):
        cases = {row["case_id"] for row in self.report["probe_results"]}
        self.assertIn("packet_geometry_accounting", cases)
        self.assertIn("postfilter_nolace", cases)
        self.assertIn("nonfinite_sample", cases)
        self.assertIn("missing_runtime", cases)

    def test_failure_controls(self):
        self.assertTrue(self.report["failure_controls"]["all_explicit"])
        self.assertTrue(all(self.report["failure_controls"]["checks"].values()))

    def test_adverse_and_missing_results(self):
        self.assertTrue(self.report["adverse_results"])
        self.assertTrue(self.report["missing_results"])
        self.assertTrue(all(row["qualifies"] is False for row in self.report["adverse_results"]))
        for row in self.report["missing_results"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["metrics"])
            self.assertFalse(row["qualifies"])

    def test_artifact_assessment_blocked(self):
        assessment = self.report["artifact_assessment"]
        self.assertTrue(assessment["all_required_absent"])
        self.assertFalse(assessment["runtime_presence"]["present"])
        self.assertFalse(assessment["package_assets"]["present"])
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))

    def test_pcm_fixture_record(self):
        fixture = self.report["pcm_fixture"]
        self.assertEqual(fixture["sample_rate_hz"], 16000)
        self.assertEqual(fixture["frame_samples"], 160)
        self.assertEqual(fixture["frames"], 3)
        self.assertEqual(len(fixture["full_digest"]), 64)

    def test_packet_fixture_record(self):
        fixture = self.report["packet_fixture"]
        self.assertEqual(fixture["sample_rate_hz"], 16000)
        self.assertEqual(fixture["packet_durations_samples"], [160, 320, 480])
        self.assertEqual(fixture["max_packet_bytes"], 1275)
        self.assertEqual(fixture["missing_packets"], 1)

    def test_report_canonical_bytes(self):
        text, digest = reference.canonical_report(self.report)
        self.assertEqual((ROOT / "report.json").read_bytes(), text.encode("utf-8"))
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii").strip(),
                         digest)

    def test_regeneration_byte_identical(self):
        original = (ROOT / "report.json").read_bytes()
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        completed = subprocess.run([sys.executable, "run.py", "--report"], cwd=ROOT,
                                   env=environment, capture_output=True, text=True, check=True)
        self.assertRegex(completed.stdout.strip(), r"^[0-9a-f]{64}$")
        self.assertEqual((ROOT / "report.json").read_bytes(), original)

    def test_sources_manifest_matches(self):
        self.assertEqual((ROOT / "SOURCES.sha256").read_text(encoding="utf-8"),
                         run.source_manifest())

    def test_artifact_pins(self):
        for name, digest in self.contract["artifact_pins"].items():
            self.assertEqual(reference.digest_file(ROOT / name), digest)

    def test_no_board_hash(self):
        text = json.dumps(self.report, sort_keys=True) + json.dumps(self.contract, sort_keys=True)
        self.assertNotIn("sha256_at_read", text)
        self.assertNotIn("sha256_now", text)
        self.assertNotIn("TASKS.json", (ROOT / "SOURCES.sha256").read_text(encoding="utf-8"))

    def test_linked_row_identity(self):
        verify.check_linked_row(self.contract, self.report)

    def test_report_key_set(self):
        self.assertEqual(set(self.report), reference.REPORT_KEYS)

    def test_contract_key_set(self):
        self.assertEqual(set(self.contract), verify.CONTRACT_KEYS)

    def test_contract_qualification(self):
        self.assertEqual(self.contract["qualification"]["status"], "not_qualified")
        self.assertFalse(self.contract["qualification"]["qualifies"])
        self.assertEqual(len(self.contract["release_gates"]), 8)


class CliTests(unittest.TestCase):
    def invoke(self, *arguments, timeout=30):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "run.py", *arguments], cwd=ROOT,
                              env=environment, capture_output=True, text=True,
                              timeout=timeout)

    def test_inspect_deterministic(self):
        first = self.invoke("--inspect")
        second = self.invoke("--inspect")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        payload = json.loads(first.stdout)
        self.assertEqual(payload["decision"], "DEFER")
        self.assertEqual(payload["qualification"]["status"], "not_qualified")
        self.assertEqual(payload["release_gate_statuses"], ["blocked"] * 8)

    def test_sources_output(self):
        completed = self.invoke("--sources")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, (ROOT / "SOURCES.sha256").read_text(encoding="utf-8"))

    def test_request_packet_accounting(self):
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "request.json"
            result = Path(directory) / "result.json"
            request.write_text(json.dumps(reference.make_request(
                "packet_accounting", packets=reference.packet_schedule())),
                encoding="utf-8")
            completed = self.invoke("--request", str(request), "--result", str(result))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "analytic_packet_geometry_only")
            self.assertFalse(payload["qualifies"])

    def test_request_rejects_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "request.json"
            result = Path(directory) / "result.json"
            samples = list(reference.probe_samples())
            samples[0] = 1e308
            text = json.dumps(reference.make_request(
                "boundary_accounting", samples=samples))
            needle = json.dumps(1e308)
            self.assertIn(needle, text)
            request.write_text(text.replace(needle, "1e999", 1), encoding="utf-8")
            completed = self.invoke("--request", str(request), "--result", str(result))
            self.assertEqual(completed.returncode, 2)
            self.assertIn("nonfinite_json_number", completed.stderr)
            self.assertFalse(result.exists())

    def test_request_rejects_structural_error(self):
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "request.json"
            result = Path(directory) / "result.json"
            request.write_text('{"protocol_version":1}', encoding="utf-8")
            completed = self.invoke("--request", str(request), "--result", str(result))
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertFalse(result.exists())

    def test_request_rejects_non_object(self):
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "request.json"
            result = Path(directory) / "result.json"
            request.write_text('[1,2,3]', encoding="utf-8")
            completed = self.invoke("--request", str(request), "--result", str(result))
            self.assertEqual(completed.returncode, 2)
            self.assertIn("json_root_not_object", completed.stderr)


class HygieneTests(unittest.TestCase):
    def test_spdx_headers_and_sidecars(self):
        for name in ("contract.json", "report.json", "report.json.sha256", "SOURCES.sha256"):
            text = (ROOT / (name + ".license")).read_text(encoding="utf-8")
            self.assertIn("SPDX" + "-FileCopyrightText", text)
            self.assertIn("SPDX" + "-License-Identifier", text)
        for path in ROOT.glob("*.py"):
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertTrue(lines[0].startswith("# SPDX" "-FileCopyrightText:"))
            self.assertTrue(lines[1].startswith("# SPDX" "-License-Identifier:"))

    def test_no_forbidden_artifacts(self):
        suffixes = {".wav", ".flac", ".mp3", ".m4a", ".opus", ".ogg", ".onnx",
                    ".tflite", ".bin", ".whl", ".so", ".dylib", ".dll", ".a"}
        found = [path.name for path in ROOT.rglob("*")
                 if path.is_file() and path.suffix.lower() in suffixes]
        self.assertEqual(found, [])

    def test_minimum_test_count(self):
        tests = (ROOT / "test_reference.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(len(re.findall(r"^    def test_", tests, flags=re.MULTILINE)), 30)

    def test_verify_script_green(self):
        self.assertEqual(verify.main(), 0)


if __name__ == "__main__":
    unittest.main()
