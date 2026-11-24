# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic offline tests for the sanitizer/fuzz qualification fixture."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixture  # noqa: E402 - task-local deterministic module


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = fixture.load_adapter()
        cls.report = fixture.build_report()
        cls.report_bytes = fixture.canonical_report_bytes(cls.report)

    def test_adapter_schema_and_digests(self) -> None:
        self.assertEqual(self.adapter["tool_version"], "0.1.0")
        self.assertEqual(self.adapter["base_commit"], fixture.BASE_COMMIT)
        self.assertEqual(self.adapter["task_id"],
                         "SDK-CLANG-SANITIZERS-FUZZING-AND-QUALIFICATION-MATRIX")
        self.assertEqual(fixture.file_digest(fixture.ADAPTER_PATH),
                         self.report["digests"]["adapter"])

    def test_source_pins_match_frozen_bytes(self) -> None:
        pins = self.report["source_pins"]
        self.assertTrue(self.report["source_pins_ok"])
        self.assertEqual(len(pins), self.report["counts"]["source_pins"])
        for pin in pins:
            self.assertTrue(pin["verified"], pin["path"])
            self.assertEqual(pin["observed_sha256"], pin["sha256"])
        qualification = next(pin for pin in pins
                             if pin["id"] == "qualification-readme")
        self.assertEqual(qualification["path"],
                         "cpp-library/qualification/README.md")
        self.assertEqual(
            qualification["sha256"],
            "f2ab2c4bd874c0147dcfbc98638564dcce1202a4468b557b81a3ed8df6a44871")

    def test_report_is_byte_reproducible(self) -> None:
        again = fixture.canonical_report_bytes(fixture.build_report())
        self.assertEqual(self.report_bytes, again)
        self.assertTrue(self.report_bytes.endswith(b"\n"))
        self.assertNotIn(b"\r", self.report_bytes)

    def test_strict_json_shape_and_status(self) -> None:
        parsed = json.loads(self.report_bytes,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                ValueError(value)))
        self.assertEqual(parsed["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(parsed["qualification_status"], "not_qualified")
        self.assertTrue(parsed["no_missing_result_qualifies_candidate"])
        self.assertEqual(parsed["profile"], "Tool")
        self.assertEqual(parsed["base_commit"], fixture.BASE_COMMIT)
        self.assertTrue(parsed["spdx"]["license"].endswith("Apache-2.0"))

    def test_validity_overflow_exact_cases(self) -> None:
        self.assertTrue(self.report["overflow"]["all_pass"])
        self.assertFalse(self.report["overflow"]["failures"])
        for case in self.report["overflow"]["exact_cases"]:
            self.assertTrue(case["passed"], case["id"])
        self.assertEqual(self.report["counts"]["overflow_exact_cases"], 6)

    def test_validity_sweeps_and_boundaries(self) -> None:
        overflow = self.report["overflow"]
        self.assertEqual(len(overflow["delay_boundaries"]), 7)
        self.assertEqual(len(overflow["final_remainders"]), 1113)
        self.assertEqual(overflow["conformance_lengths"]["count"], 166)
        self.assertEqual(
            overflow["conformance_lengths"]["expected_count"], 166)
        self.assertTrue(overflow["conformance_lengths"]["all_admitted"])
        self.assertTrue(all(case["passed"]
                            for case in overflow["delay_boundaries"]))
        self.assertTrue(all(case["passed"]
                            for case in overflow["final_remainders"]))

    def test_saturating_arithmetic_edges(self) -> None:
        self.assertEqual(
            fixture.add_u32_saturating(fixture.I64_MAX - 10, 256),
            fixture.I64_MAX)
        self.assertEqual(
            fixture.subtract_u32_saturating(fixture.I64_MIN, 512),
            fixture.I64_MIN)
        self.assertEqual(fixture.local_offset(0, -256, 160), 160)
        self.assertEqual(fixture.local_offset(-257, -256, 160), 0)

    def test_above_2_53_coordinates_are_exact_strings(self) -> None:
        coordinates = self.report["overflow"]["coordinates"]
        self.assertTrue(all(case["passed"] for case in coordinates))
        timing = next(case for case in coordinates if case["id"] == "OV-07")
        self.assertTrue(timing["admitted"])
        self.assertEqual(fixture.decimal_string(fixture.TWO53_PLUS_1),
                         "9007199254740993")
        self.assertEqual(fixture.decimal_string(0), "0")
        self.assertEqual(fixture.decimal_string(-7), "-7")

    def test_out_of_range_coordinates_are_rejected(self) -> None:
        admitted, reason = fixture.admit_coordinates(2**64, 0)
        self.assertFalse(admitted)
        self.assertEqual(reason, "epoch_out_of_uint64")
        admitted, reason = fixture.admit_coordinates(1, 2**63)
        self.assertFalse(admitted)
        self.assertEqual(reason, "first_out_of_int64_frame_range")

    def test_state_reset_requires_strictly_greater_epoch(self) -> None:
        state = self.report["state"]
        self.assertTrue(state["all_pass"])
        reset = next(case for case in state["scenarios"]
                     if case["id"] == "ST-01")
        self.assertEqual(reset["observed"]["status"], fixture.AS_INVALID_ARGUMENT)
        accepted = next(case for case in state["scenarios"]
                        if case["id"] == "ST-02")
        self.assertEqual(accepted["observed"]["process"]["source_first_sample"],
                         123456)

    def test_state_drain_and_lifecycle(self) -> None:
        eos = next(case for case in self.report["state"]["scenarios"]
                   if case["id"] == "ST-03")
        self.assertEqual(eos["observed"]["first_drain"]["status"],
                         fixture.AS_END_OF_STREAM)
        self.assertEqual(eos["observed"]["second_drain"]["status"],
                         fixture.AS_END_OF_STREAM)
        self.assertEqual(eos["observed"]["process"]["status"],
                         fixture.AS_INVALID_ARGUMENT)
        needs_reset = next(case for case in self.report["state"]["scenarios"]
                           if case["id"] == "ST-05")
        self.assertEqual(needs_reset["observed"]["blocked"]["status"],
                         fixture.AS_NEEDS_RESET)
        closed = next(case for case in self.report["state"]["scenarios"]
                      if case["id"] == "ST-06")
        self.assertEqual(closed["observed"]["status"], fixture.AS_CLOSED)

    def test_sessions_are_uncoupled(self) -> None:
        self.assertTrue(self.report["state"]["sessions_uncoupled"])

    def test_typical_use_and_caller_owned_inputs(self) -> None:
        control = self.report["controls"]["typical_use"]
        self.assertTrue(control["passed"])
        self.assertEqual(control["consumed_count"], 160)
        self.assertEqual(control["produced_count"], 160)
        self.assertEqual(control["valid_count"], 160)
        self.assertEqual(control["drain_status"], fixture.AS_END_OF_STREAM)
        caller = self.report["controls"]["caller_owned_inputs"]
        self.assertFalse(caller["model_retains_caller_pointer"])

    def test_eight_malformed_probes(self) -> None:
        malformed = self.report["malformed"]
        self.assertTrue(malformed["all_pass"])
        self.assertEqual(len(malformed["malformed_probes"]), 8)
        for case in malformed["malformed_probes"]:
            self.assertEqual(case["observed_status"],
                             fixture.AS_INVALID_ARGUMENT, case["id"])
            self.assertEqual(case["valid_count"], 0, case["id"])

    def test_missing_optional_selections_fail_explicitly(self) -> None:
        selections = self.report["malformed"]["missing_selections"]
        self.assertEqual(len(selections), 6)
        for case in selections:
            self.assertTrue(case["passed"], case["id"])
        self.assertTrue(self.report["controls"]["missing_optional_selection"][
            "no_inferred_fallback"])

    def test_deterministic_fuzz_corpus(self) -> None:
        corpus = self.report["fuzz_corpus"]
        again = fixture.build_fuzz_corpus(self.adapter)
        self.assertEqual(corpus["corpus_digest"], again["corpus_digest"])
        self.assertEqual(corpus["case_count"], 256)
        self.assertEqual(len(corpus["cases"]), 256)
        self.assertEqual(corpus["seed"], 20261124)
        self.assertFalse(corpus["qualifying_fuzz_run"])

    def test_fuzz_corpus_rejects_every_case(self) -> None:
        corpus = self.report["fuzz_corpus"]
        self.assertTrue(corpus["all_rejected"])
        self.assertEqual(len(corpus["by_mutation"]), 16)
        self.assertTrue(all(count == 16 for count
                            in corpus["by_mutation"].values()))
        for case in corpus["cases"]:
            self.assertNotEqual(case["status"], fixture.AS_OK)
            self.assertEqual(case["valid_count"], 0)

    def test_installed_consumer_payload_and_pcm_digests(self) -> None:
        installed = self.report["installed_consumer"]
        self.assertTrue(installed["payload_digest_match"])
        self.assertTrue(installed["pcm_digest_match"])
        self.assertEqual(installed["observed_canonical_payload_bytes"], 4074)
        self.assertEqual(
            installed["observed_canonical_payload_sha256"],
            "4e5255802e2be73b84599979855d59d03a4f06eff8e439d23ab7ee09e95be459")
        self.assertEqual(
            installed["observed_pcm_f32_sha256"],
            "9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2")

    def test_installed_consumer_model_and_pinned_skips(self) -> None:
        installed = self.report["installed_consumer"]
        self.assertTrue(installed["all_match"])
        self.assertFalse(installed["rerun_in_this_task"])
        self.assertEqual(installed["frame_lengths"], [160, 160, 37])
        self.assertEqual(installed["sample_count"], 357)
        self.assertEqual(installed["produced_valid_samples"], 357)
        self.assertEqual(installed["first_input_sample_string"],
                         "9007199254740993")
        self.assertTrue(installed["bit_identical_valid_content"])
        self.assertEqual(installed["drain_status"], fixture.AS_END_OF_STREAM)
        self.assertEqual(installed["installed_conformance_pass"], 35)
        self.assertEqual(installed["installed_conformance_skip"], 2)
        self.assertEqual(installed["skipped_checks"],
                         ["registry.busy", "buffered.flow"])

    def test_synthetic_samples_are_finite(self) -> None:
        values = fixture.installed_samples()
        self.assertEqual(len(values), 357)
        self.assertTrue(all(math.isfinite(value) for value in values))
        self.assertTrue(all(abs(value) < 1.0 for value in values))

    def test_evidence_layers_separated(self) -> None:
        self.assertTrue(self.report["controls"]["layers_separated"])
        self.assertEqual(self.report["compile_build_evidence"][
            "sdk_instrumented_build"], "not_run")
        self.assertFalse(self.report["compile_build_evidence"][
            "build_files_changed"])
        self.assertFalse(self.report["compile_build_evidence"]["ci_changed"])
        self.assertTrue(self.report["synthetic_runtime_evidence"][
            "no_sdk_binary_instrumented"])
        self.assertEqual(self.report["measured_workload_support"]["status"],
                         "blocked")
        self.assertIsNone(self.report["measured_workload_support"]["deadline"])

    def test_matrix_status_vocabulary_and_zero_qualified(self) -> None:
        matrix = self.report["qualification_matrix"]
        allowed = {"qualified", "experimental", "unavailable", "not-run"}
        for row in matrix["rows"]:
            self.assertIn(row["status"], allowed, row["id"])
            self.assertEqual(row["date"], "2026-11-24", row["id"])
            self.assertEqual(row["version"], "0.1.0", row["id"])
            self.assertIn("evidence", row, row["id"])
            self.assertIn("notes", row, row["id"])
        self.assertEqual(matrix["qualified_rows"], [])
        self.assertTrue(matrix["zero_qualified_rows"])
        self.assertEqual(matrix["status_counts"].get("qualified", 0), 0)

    def test_matrix_axes_are_frozen(self) -> None:
        axes = self.report["qualification_matrix"]["axes"]
        self.assertEqual(axes["platform"], ["macos-arm64"])
        self.assertIn("address+undefined", axes["sanitizer"])
        self.assertIn("deterministic-corpus", axes["fuzz_engine"])
        self.assertEqual(len(self.report["qualification_matrix"]["rows"]), 12)

    def test_toolchain_probe_is_non_qualifying(self) -> None:
        probe = self.report["toolchain_probe"]
        self.assertEqual(probe["status"], "probe_only_non_qualifying")
        self.assertFalse(probe["qualifying"])
        outcomes = {item["id"]: item["outcome"] for item in probe["results"]}
        self.assertEqual(outcomes["TP-MSAN"], "unsupported_option_for_target")
        self.assertEqual(outcomes["TP-LIBFUZZER"], "runtime_library_absent")
        self.assertEqual(outcomes["TP-AFL"], "tool_absent")

    def test_gates_and_adverse_observations(self) -> None:
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertEqual(len(self.report["gates"]), 7)
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked", gate["id"])
            self.assertTrue(gate["reopen"], gate["id"])
        self.assertEqual(len(self.report["adverse_observations"]), 5)
        self.assertEqual(self.report["regressions"], [])

    def test_artifact_pins_are_present(self) -> None:
        paths = {item["path"] for item in self.report["artifact_pins"]}
        self.assertEqual(paths, {"adapter.json", "fixture.py", "run.py",
                                 "test_fixture.py", "verify.py"})
        for item in self.report["artifact_pins"]:
            self.assertEqual(fixture.file_digest(HERE / item["path"]),
                             item["sha256"])

    def test_spdx_headers_on_new_python_files(self) -> None:
        for name in ("fixture.py", "run.py", "verify.py", "test_fixture.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:4])
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head, name)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head, name)

    def test_no_trailing_whitespace_in_task_files(self) -> None:
        for path in sorted(HERE.iterdir()):
            if path.suffix in (".py", ".json", ".md", ".sha256"):
                for number, line in enumerate(
                        path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(),
                                     f"{path.name}:{number}")


if __name__ == "__main__":
    unittest.main()
