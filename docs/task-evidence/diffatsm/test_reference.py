# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-DIFFATSM evidence package."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_rejects_nonfinite_constants(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"a":' + token + "}")

    def test_rejects_trailing_data_bom_and_non_object(self) -> None:
        for payload in ('{"a":1}x', '\ufeff{"a":1}', "[1,2]", "  "):
            with self.assertRaises(ValueError):
                reference.loads_strict(payload)

    def test_canonical_roundtrip_and_digest(self) -> None:
        document = {"b": [1, True, None], "a": {"z": "x"}}
        payload = reference.canonical_bytes(document)
        self.assertEqual(payload, b'{"a":{"z":"x"},"b":[1,true,null]}')
        self.assertEqual(
            reference.object_digest(document), hashlib.sha256(payload).hexdigest())

    def test_rejects_floats_in_canonical_evidence(self) -> None:
        with self.assertRaises(TypeError):
            reference._assert_no_floats({"value": 0.5})


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_boundary_pins_match(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_evidence_snippets_are_present(self) -> None:
        result = reference.evidence_snippet_check()
        self.assertEqual(result["count"], 7)
        self.assertTrue(result["all_present"], result["checks"])

    def test_inventory_record_is_the_linked_row(self) -> None:
        record = reference.inventory_record()
        self.assertEqual(record["id"], "diffatsm")
        self.assertEqual(record["name"], "DiffATSM")
        self.assertEqual(record["area"], "Rate and content")
        self.assertEqual(record["evidence_status"], "blocked")
        self.assertEqual(record["repository"], "audio-sdk")
        self.assertEqual(record["disposition"], "sdk-model")
        self.assertEqual(record["verification_profile"], "rate")
        self.assertEqual(record["task"], reference.TASK)
        self.assertEqual(record["evidence"][0]["line"], 36)

    def test_linked_row_identity_only(self) -> None:
        boundary = reference.boundary_block()
        self.assertFalse(boundary["board_file_pinned"])
        self.assertTrue(boundary["linked_row_identity_only"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertNotIn("status", boundary["linked_row"])
        self.assertEqual(
            boundary["linked_row_sha256"],
            reference.board_row_digest(boundary["linked_row"]))
        self.assertEqual(len(boundary["linked_row_sha256"]), 64)
        self.assertNotEqual(
            boundary["linked_rows_sha256"],
            reference.sha256_file(
                reference.AUDIO_ROOT / reference.BOARD_TASK_ROW))


class AbsenceTests(unittest.TestCase):
    def test_all_candidate_artifacts_are_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 14)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_absent"])

    def test_no_diffusion_runtime_is_available(self) -> None:
        readiness = reference.runtime_readiness()
        self.assertFalse(readiness["runtime_present"])
        self.assertFalse(readiness["runtime_pinned"])
        self.assertFalse(readiness["any_diffusion_module_available"])


class MappingTests(unittest.TestCase):
    def test_exact_target_durations(self) -> None:
        cases = {
            (1, 1): 19200,
            (5, 4): 15360,
            (3, 2): 12800,
            (4, 5): 24000,
            (9, 10): 21333,
        }
        for (numerator, denominator), target in cases.items():
            record = reference.mapping_record(
                19200, numerator, denominator)
            self.assertEqual(record["target_samples"], target)
            self.assertEqual(record["duration_error_samples"], 0)
            self.assertTrue(record["monotone"])
            self.assertTrue(record["bounded"])

    def test_identity_mapping_is_exact(self) -> None:
        record = reference.mapping_record(19200, 1, 1)
        self.assertTrue(record["identity_exact"])
        self.assertEqual(record["last_source"], 19199)

    def test_mapping_is_deterministic(self) -> None:
        first = reference.mapping_record(19200, 5, 4)
        second = reference.mapping_record(19200, 5, 4)
        self.assertEqual(first, second)

    def test_mapping_rejects_bad_rates(self) -> None:
        for numerator, denominator, code in (
                (0, 1, "rate_not_positive"),
                (1, 0, "rate_not_positive"),
                (5, 10, "rate_not_reduced"),
                (1, 3, "rate_out_of_bounds"),
                (3, 1, "rate_out_of_bounds"),
        ):
            with self.assertRaises(reference.AdmissionError) as caught:
                reference.mapping_record(19200, numerator, denominator)
            self.assertEqual(caught.exception.code, code)

    def test_canonical_decimal_rejects_adverse_values(self) -> None:
        for text in ("0.50", "1.0", "NaN", "Infinity", "-0.5", "1.5", " 0.5"):
            with self.assertRaises(reference.AdmissionError):
                reference.canonical_decimal(text, "test")
        self.assertEqual(reference.canonical_decimal("0.78125", "test"),
                         Fraction(25, 32))

    def test_frame_metrics_are_deterministic_and_bounded(self) -> None:
        values = reference.synthetic_frame()
        metrics = reference.frame_metrics(values)
        self.assertEqual(metrics["sample_count"], 160)
        self.assertEqual(metrics["peak"], "0.78125")
        self.assertEqual(metrics, reference.frame_metrics(
            reference.synthetic_frame()))

    def test_frame_metrics_reject_invalid_samples(self) -> None:
        for values in ([], [Fraction(0)] * (reference.MAX_SAMPLE_COUNT + 1),
                       [float("nan")], [float("inf")], [Fraction(2)]):
            with self.assertRaises(ValueError):
                reference.frame_metrics(values)


class AdmissionTests(unittest.TestCase):
    def test_valid_manifest_is_accepted(self) -> None:
        accepted = reference.validate_manifest(
            reference.envelope_manifest("identity_1x", 1, 1))
        self.assertEqual(accepted["target_samples"], 19200)
        self.assertEqual(accepted["speed_ratio"], "1/1")

    def test_candidate_claim_is_rejected(self) -> None:
        manifest = reference.envelope_manifest("identity_1x", 1, 1)
        manifest["candidate"]["weights_present"] = True
        with self.assertRaises(reference.AdmissionError) as caught:
            reference.validate_manifest(manifest)
        self.assertEqual(caught.exception.code, "weights_present_must_be_false")

    def test_nonfinite_input_is_rejected(self) -> None:
        manifest = reference.envelope_manifest("identity_1x", 1, 1)
        manifest["input"]["peak"] = "NaN"
        with self.assertRaises(reference.AdmissionError):
            reference.validate_manifest(manifest)

    def test_mutation_suite_rejects_every_case(self) -> None:
        result = reference.admission_rejections()
        self.assertGreaterEqual(result["cases"], 40)
        self.assertTrue(result["all_rejected"])
        self.assertEqual(len({row["id"] for row in result["rejections"]}),
                         result["cases"])

    def test_strict_json_suite_rejects_every_case(self) -> None:
        result = reference.strict_json_rejections()
        self.assertEqual(result["cases"], 9)
        self.assertTrue(result["all_rejected"])

    def test_no_mutable_controller_state_after_rejection(self) -> None:
        manifest = reference.envelope_manifest("speed_up_125", 5, 4)
        before = copy.deepcopy(manifest)
        manifest["output"]["sample_count"] = 1
        with self.assertRaises(reference.AdmissionError):
            reference.validate_manifest(manifest)
        self.assertEqual(
            reference.validate_manifest(before)["target_samples"], 15360)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_state(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"], "not_qualified")
        self.assertEqual(self.contract["profile"], "rate")
        self.assertEqual(self.contract["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(len(self.contract["release_gates"]), 8)
        self.assertTrue(all(
            gate["status"] == "blocked" and gate["qualifies"] is False
            for gate in self.contract["release_gates"]))
        self.assertFalse(self.contract["source_reported_identity"][
            "runnable_as_released"])
        self.assertFalse(self.contract["source_reported_identity"][
            "rate_only_estimator"])

    def test_report_state(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))
        self.assertTrue(self.report["qualification"]["not_qualified"])
        self.assertTrue(
            self.report["qualification"]["all_release_gates_blocked"])
        for key, value in self.report["qualification"].items():
            if key in ("status", "readiness", "not_qualified",
                       "all_release_gates_blocked"):
                continue
            self.assertIs(value, False, key)

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        self.assertEqual(len({gate["title"] for gate in gates}), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["boundary"]["linked_row"])

    def test_blockers_artifacts_and_results(self) -> None:
        self.assertEqual(len(self.report["exact_blockers"]), 6)
        self.assertEqual(len(self.report["required_artifacts"]), 7)
        self.assertEqual(len(self.report["required_results"]), 8)
        self.assertEqual(len(self.report["reopening_conditions"]), 6)
        self.assertEqual(len(self.report["non_claims"]), 7)
        for blocker in self.report["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
        for artifact in self.report["required_artifacts"][1:]:
            self.assertFalse(artifact["present"])
            self.assertTrue(artifact["blocked"])

    def test_rate_profile_is_not_satisfied(self) -> None:
        profile = self.report["rate_profile"]
        self.assertEqual(profile["profile"], "rate")
        self.assertFalse(profile["profile_satisfied"])
        self.assertEqual(profile["real_results"], 0)
        self.assertTrue(profile["synthetic_envelope_only"])
        self.assertIsNone(profile["candidate_geometry"])
        self.assertEqual(len(profile["requirement_rows"]), 13)
        blocked = [row for row in profile["requirement_rows"]
                   if row["status"] == "blocked"]
        self.assertGreaterEqual(len(blocked), 10)

    def test_envelope_is_protocol_only(self) -> None:
        envelope = self.report["protocol_envelope"]
        self.assertEqual(envelope["case_count"], 5)
        self.assertTrue(envelope["identity_exact"])
        self.assertFalse(envelope["synthesizes_audio"])
        self.assertFalse(envelope["loads_model"])
        self.assertTrue(envelope["not_candidate"])
        for case in envelope["cases"]:
            self.assertTrue(case["monotone"])
            self.assertTrue(case["bounded"])
            self.assertEqual(case["duration_error_samples"], 0)

    def test_admission_and_absence(self) -> None:
        admission = self.report["admission"]
        self.assertGreaterEqual(admission["manifest_cases"], 40)
        self.assertTrue(admission["all_rejected"])
        self.assertTrue(admission["strict_json_all_rejected"])
        self.assertTrue(admission["assets_never_loaded"])
        self.assertTrue(self.report["absence_evidence"]["all_absent"])
        self.assertEqual(
            self.report["absence_evidence"]["present_count"], 0)

    def test_scope_and_geometry(self) -> None:
        scope = self.report["scope"]
        self.assertTrue(scope["task_local_only"])
        self.assertEqual(scope["write_scope"], reference.WRITE_SCOPE)
        for key, value in scope.items():
            if key in ("task_local_only", "write_scope"):
                continue
            self.assertIs(value, False, key)
        self.assertEqual(self.report["public_v0_geometry"], {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
            "unchanged": True,
        })

    def test_report_has_no_floats_and_is_deterministic(self) -> None:
        reference._assert_no_floats(self.report)
        first = reference.canonical_report(self.report)
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(len(first[1]), 64)


class CommittedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report_bytes = (HERE / "report.json").read_bytes()
        cls.contract_bytes = (HERE / "contract.json").read_bytes()

    def test_committed_contract_and_report_are_canonical(self) -> None:
        self.assertEqual(self.contract_bytes,
                         reference.canonical_bytes(reference.build_contract()))
        payload, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(self.report_bytes, payload.encode("ascii"))
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n")

    def test_sources_manifest_covers_every_file(self) -> None:
        rows = {}
        for line in (HERE / "SOURCES.sha256").read_text(
                encoding="ascii").splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            rows[name] = digest
        self.assertNotIn("audio-benchmark-platform/plan/swarm/TASKS.json", rows)
        for name in ("README.md", "LICENSES.md", "reference.py", "run.py",
                     "verify.py", "test_reference.py", "contract.json",
                     "report.json", "report.json.sha256"):
            key = reference.TASK_PREFIX + name
            self.assertIn(key, rows)
            self.assertEqual(reference.sha256_file(HERE / name), rows[key])

    def test_spdx_sidecars_and_headers(self) -> None:
        expected = (
            "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
            "SPDX-License-Identifier: Apache-2.0\n")
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"),
                             expected)
        for name in ("reference.py", "run.py", "verify.py",
                     "test_reference.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:5])
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head)
            self.assertIn("SPDX-FileCopyrightText: 2026", head)

    def test_json_artifacts_are_strict(self) -> None:
        for path in (HERE / "contract.json", HERE / "report.json"):
            document = reference.read_strict_json(path)
            self.assertIsInstance(document, dict)
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
