# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest acceptance suite for the SDK-ESSENTIA evidence package.

The suite runs against task-local strict JSON, the fail-closed candidate gate,
the synthetic Rate harness and the generated canonical artifacts. It asserts
that nothing in the package qualifies the candidate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import unittest
from functools import lru_cache

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"


@lru_cache(maxsize=1)
def build_report() -> dict:
    return reference.build_report()


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_object_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for payload in ('{"v":NaN}', '{"v":Infinity}', '{"v":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_object_loads(payload)

    def test_malformed_text_rejected(self) -> None:
        for payload in ('{"a":1} trailing', "{a:1}", "{'a':'b'}", ""):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_object_loads(payload)

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_object_loads('[{"a":1}]')

    def test_canonical_bytes_are_compact_and_sorted(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        self.assertEqual(payload, b'{"a":[2,3],"b":1}')

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"v": float("nan")})


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        request = reference.validate_request(reference._base_request())
        self.assertEqual(request["sample_rate_hz"], 16000)
        self.assertEqual(len(request["samples"]), 160)

    def test_all_adverse_requests_rejected(self) -> None:
        adverse = reference.adverse_requests()
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["case_count"], 33)
        for case in adverse["cases"]:
            self.assertFalse(case["accepted"])
            self.assertFalse(case["qualifies_candidate"])
            self.assertEqual(case["status"], "rejected")

    def test_unknown_extra_key_rejected(self) -> None:
        request = reference._base_request()
        request["extra"] = 1
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_nonfinite_sample_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            request = reference._base_request()
            request["samples"] = [value] + [0.0] * 159
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_candidate_gate_always_defers(self) -> None:
        with self.assertRaises(reference.ArtifactsAbsent) as context:
            reference.probe_candidate(reference._base_request())
        self.assertEqual(context.exception.code, "ARTIFACTS_ABSENT")

    def test_candidate_gate_validates_before_blocking(self) -> None:
        request = reference._base_request()
        request["sample_rate_hz"] = 44100
        with self.assertRaises(reference.InputError):
            reference.probe_candidate(request)

    def test_all_adverse_json_rejected(self) -> None:
        adverse = reference.adverse_json()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)


class AnalyzerTests(unittest.TestCase):
    def test_valid_frame_advances_state(self) -> None:
        analyzer = reference.OnsetAnalyzer()
        before = analyzer.state_digest
        analyzer.process([0.0] * 160)
        self.assertNotEqual(analyzer.state_digest, before)
        self.assertEqual(len(analyzer.events), 0)

    def test_rejections_do_not_advance_state(self) -> None:
        analyzer = reference.OnsetAnalyzer()
        analyzer.process([0.0] * 160)
        before = analyzer.state_digest
        cases = (
            ("missing", None, {}),
            ("short", [0.0] * 159, {}),
            ("nonfinite", [float("nan")] + [0.0] * 159, {}),
            ("epoch", [0.0] * 160, {"epoch": 0}),
            ("valid_count", [0.0] * 160, {"valid_count": 0}),
            ("padding", [0.0] * 137 + [0.5] + [0.0] * 22,
             {"valid_count": 137}),
        )
        for label, samples, kwargs in cases:
            with self.subTest(label=label):
                with self.assertRaises(reference.InputError):
                    analyzer.process(samples, **kwargs)
                self.assertEqual(analyzer.state_digest, before)

    def test_final_padding_must_be_zero(self) -> None:
        analyzer = reference.OnsetAnalyzer()
        with self.assertRaises(reference.InputError):
            analyzer.process([0.0] * 137 + [0.0] * 22, valid_count=137)
        # Trailing zero padding of the right length is accepted.
        record = analyzer.process([0.0] * 137 + [0.0] * 23, valid_count=137)
        self.assertEqual(record["valid_count"], "137")


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report()
        cls.probe = cls.report["harness_probe"]
        cls.factor = cls.probe["factor"]
        cls.rate = cls.probe["rate_profile"]

    def test_identity_and_rate_factors(self) -> None:
        self.assertEqual(self.factor["music_1x"]["factor_bpm_x100"], "10000")
        self.assertEqual(self.factor["rate_0_8"]["factor_bpm_x100"], "8000")
        self.assertEqual(self.factor["rate_1_2"]["factor_bpm_x100"], "12000")

    def test_duration_spans_are_exact(self) -> None:
        self.assertEqual(self.rate["duration"]["max_error_samples"], 0)

    def test_unfamiliar_speech_has_no_stable_factor(self) -> None:
        self.assertNotEqual(self.factor["speech_like"]["status"], "stable")
        self.assertIsNone(self.factor["speech_like"]["factor_bpm_x100"])
        self.assertFalse(self.rate["speech_unfamiliar"]["qualifies"])

    def test_silence_has_no_onsets(self) -> None:
        self.assertEqual(self.factor["silence"]["status"], "no_onsets")

    def test_rebuffer_gap_is_suppressed(self) -> None:
        self.assertEqual(self.rate["rebuffer"]["excluded_ioi_count"], "1")
        self.assertTrue(self.rate["rebuffer"]["cross_gap_ioi_suppressed"])

    def test_drift_is_source_anchored(self) -> None:
        self.assertTrue(self.rate["drift"]["monotonic_ioi_decrease"])

    def test_final_partial_window(self) -> None:
        final = self.rate["final_partial_window"]
        self.assertEqual(final["valid_count"], "137")
        self.assertEqual(final["length_samples"], "64137")
        self.assertFalse(final["event_beyond_source_end"])
        self.assertEqual(len(final["event_digest"]), 64)

    def test_no_audio_or_candidate_output(self) -> None:
        mapping = self.rate["source_output_mapping"]
        self.assertFalse(mapping["audio_output_produced"])
        self.assertFalse(mapping["factor_output_produced"])
        self.assertFalse(self.probe["candidate_processing"])
        self.assertGreaterEqual(mapping["min_availability_margin_ns"], 0)

    def test_pitch_and_device_buffer_unmeasured(self) -> None:
        self.assertFalse(self.rate["pitch"]["qualifies"])
        self.assertFalse(self.rate["playback_buffering"]["device_buffer_measured"])

    def test_stimuli_are_deterministic_and_bounded(self) -> None:
        self.assertTrue(self.probe["deterministic"])
        for name, stimulus in self.probe["stimuli"].items():
            with self.subTest(name=name):
                self.assertTrue(stimulus["finite"])
                self.assertTrue(stimulus["bounded"])
                self.assertEqual(len(stimulus["float32_sha256"]), 64)


class ReportDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report()

    def test_identity_and_status(self) -> None:
        self.assertEqual(self.report["task"], "SDK-ESSENTIA")
        self.assertEqual(self.report["component"], "essentia")
        self.assertEqual(self.report["mode"], "feasibility")
        self.assertEqual(self.report["verification_profile"], "Rate")
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertTrue(self.report["incomplete"])
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["qualification_status"], "not_qualified")

    def test_qualification_is_not_qualified(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["decision"], "DEFER")
        self.assertTrue(qualification["proposal_only"])
        self.assertEqual(qualification["readiness"], "incomplete")
        for key in ("all_required_results_present", "candidate_qualified",
                    "upstream_parity"):
            self.assertFalse(qualification[key])

    def test_eight_release_gates_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(number) for number in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reason"])
            self.assertTrue(gate["reopen"])
        self.assertEqual(self.report["remaining_gates"],
                         [gate["id"] for gate in gates])

    def test_required_artifacts_absent(self) -> None:
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 6)
        for artifact in artifacts:
            self.assertEqual(artifact["status"], "absent")
            self.assertFalse(artifact["rights_reviewed"])
            self.assertIsNone(artifact["sha256"])
        self.assertEqual(len(self.report["missing_artifacts"]), 6)

    def test_required_results_blocked(self) -> None:
        for key, value in self.report["required_results"].items():
            self.assertEqual(value, "blocked", key)
        self.assertEqual(
            self.report["profile_mapping"]["candidate_output"],
            "blocked_source_rights_runtime_models_and_fixtures_absent")

    def test_no_result_qualifies(self) -> None:
        candidate = self.report["candidates"]["essentia"]
        self.assertFalse(candidate["qualifies_candidate"])
        self.assertIsNone(candidate["result"])
        self.assertIsNone(candidate["metrics"])
        for control in self.report["controls"].values():
            self.assertFalse(control["qualifies_candidate"])
        self.assertFalse(
            self.report["adverse"]["missing_result"]["qualifies_candidate"])

    def test_local_harness_checks_pass(self) -> None:
        score = self.report["local_harness_score"]
        self.assertTrue(score["passed"])
        self.assertEqual(score["failed_checks"], [])
        self.assertEqual(score["checks"], 21)
        for value in self.report["local_harness_checks"].values():
            self.assertTrue(value)

    def test_external_boundary_closed(self) -> None:
        boundary = self.report["external_boundary"]
        self.assertFalse(boundary["adapter_implemented"])
        self.assertFalse(boundary["adapter_default_registration"])
        self.assertFalse(boundary["automatic_discovery"])
        self.assertFalse(boundary["host_target_eligible"])
        self.assertEqual(boundary["fallback"], "none")

    def test_installed_boundary_unchanged(self) -> None:
        boundary = self.report["boundary"]
        self.assertTrue(boundary["installed_v0_unchanged"])
        for key in ("public_api_abi_changed", "headers_changed",
                    "descriptor_registry_changed", "provider_registered",
                    "enabled_by_default", "shared_cmake_changed",
                    "ci_changed", "board_or_handoff_changed",
                    "real_corpus_or_weights", "benchmark_claim",
                    "release_claim"):
            self.assertFalse(boundary[key], key)
        self.assertEqual(boundary["format"]["sample_rate_hz"], 16000)
        self.assertEqual(boundary["format"]["frame_samples"], 160)

    def test_pins_verified(self) -> None:
        for rows in (self.report["source_pins"], self.report["boundary_pins"]):
            for path, row in rows.items():
                self.assertTrue(row["verified"], path)
                self.assertEqual(row["sha256"], row["actual"])

    def test_report_is_deterministic_and_canonical(self) -> None:
        first = reference.report_bytes()
        second = reference.report_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertFalse(first.endswith(b"\n\n"))
        parsed = reference.strict_json_object_loads(first.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(parsed) + b"\n", first)


class BoardAndScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report()
        cls.contract = reference.strict_json_load(HERE / "contract.json")

    def test_board_projection_is_stable_identity_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(digest, self.report["board_link_projection_sha256"])
        self.assertEqual(self.report["board_links"], links)
        self.assertFalse(self.report["board_full_file_hashed"])

    def test_full_board_is_not_hashed(self) -> None:
        full_digest = reference.sha256_file(reference.BOARD_PATH)
        blob = ((HERE / "report.json").read_text(encoding="utf-8")
                + (HERE / "contract.json").read_text(encoding="utf-8")
                + (HERE / "SOURCES.sha256").read_text(encoding="utf-8"))
        self.assertNotIn(full_digest, blob)

    def test_mutable_fields_are_excluded(self) -> None:
        excluded = self.report["board_mutable_fields_excluded"]
        for name in ("status", "owner", "history", "claim", "review",
                     "handoff", "blocked_reason", "dispatch_priority"):
            self.assertIn(name, excluded)

    def test_contract_copy_matches(self) -> None:
        self.assertEqual(self.contract["status"], "proposal_only_not_qualified")
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertTrue(self.contract["incomplete"])
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertEqual(len(self.contract["release_gates"]), 8)
        self.assertEqual(self.contract["board_links"],
                         self.report["board_links"])

    def test_committed_bundle_matches_regeneration(self) -> None:
        bundle = run.build_bundle()
        for name, payload in bundle.items():
            with self.subTest(name=name):
                self.assertEqual((HERE / name).read_bytes(), payload)


class LicensingAndPackageTests(unittest.TestCase):
    def test_python_spdx_headers(self) -> None:
        for name in ("reference.py", "run.py", "test_reference.py",
                     "verify.py"):
            head = "\n".join((HERE / name).read_text(encoding="utf-8")
                             .splitlines()[:4])
            self.assertIn(SPDX_NEEDLE, head, name)
            self.assertIn(SPDX_COPYRIGHT, head, name)

    def test_spdx_sidecars(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license", "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_NEEDLE, text)
            self.assertIn(SPDX_COPYRIGHT, text)

    def test_readme_spdx_header(self) -> None:
        head = "\n".join((HERE / "README.md").read_text(encoding="utf-8")
                         .splitlines()[:4])
        self.assertIn(SPDX_NEEDLE, head)
        self.assertIn(SPDX_COPYRIGHT, head)

    def test_report_sidecar_matches(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        expected = (reference.sha256_bytes(payload) + "  report.json\n")
        self.assertEqual((HERE / "report.json.sha256").read_text("ascii"),
                         expected)

    def test_all_manifest_files_exist(self) -> None:
        for name in run.MANIFEST_FILES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_no_forbidden_artifacts(self) -> None:
        forbidden = {".wav", ".flac", ".mp3", ".onnx", ".pt", ".pth",
                     ".bin", ".so", ".dylib", ".whl", ".npy", ".pyc"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertFalse(path.name.startswith("LICENSE"), path.name)

    def test_no_absolute_local_paths_in_report(self) -> None:
        payload = (HERE / "report.json").read_text(encoding="utf-8")
        for needle in ("/Users/", "/home/", "\\\\Users\\\\"):
            self.assertNotIn(needle, payload)

    def test_source_and_runtime_are_absent(self) -> None:
        self.assertFalse(reference.source_probe()["present"])
        self.assertFalse(reference.runtime_probe()["present"])
        self.assertFalse(reference.fixture_probe()["present"])
        self.assertEqual(reference.rights_probe()["review"], "blocked")


if __name__ == "__main__":
    unittest.main()
