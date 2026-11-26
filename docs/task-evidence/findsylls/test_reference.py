# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the findsylls blocker package.

No network, no candidate source, no audio, no runtime and no skips.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import reference as r
import run as cli

HERE = Path(__file__).resolve().parent


def strict_load(payload: bytes):
    def no_duplicates(pairs):
        seen = set()
        for key, _value in pairs:
            if key in seen:
                raise ValueError("duplicate key: " + key)
            seen.add(key)
        return dict(pairs)

    def reject_constant(token):
        raise ValueError("nonfinite constant: " + token)

    return json.loads(payload.decode("ascii"), object_pairs_hook=no_duplicates, parse_constant=reject_constant)


class CanonicalJsonTests(unittest.TestCase):
    def test_sorted_ascii_and_newline(self) -> None:
        payload = r.canonical_bytes({"b": 1, "a": "x"})
        self.assertEqual(payload, b'{"a":"x","b":1}')
        self.assertEqual(r.canonical_report_bytes({"a": 1}), b'{"a":1}\n')

    def test_rejects_nonfinite_float(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                r.canonical_bytes({"value": value})

    def test_negative_zero_normalized(self) -> None:
        self.assertEqual(r.canonical_bytes({"v": -0.0}), b'{"v":0.0}')

    def test_duplicate_key_rejected_by_strict_loader(self) -> None:
        with self.assertRaises(ValueError):
            strict_load(b'{"a":1,"a":2}\n')

    def test_nonfinite_constant_rejected_by_strict_loader(self) -> None:
        with self.assertRaises(ValueError):
            strict_load(b'{"a":NaN}\n')


class BoardIdentityTests(unittest.TestCase):
    def test_digest_stable_and_mutable_fields_excluded(self) -> None:
        digest = r.stable_identity_digest()
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, r.stable_identity_digest())
        for field in ("status", "owner", "claim", "review", "handoff", "blocked_reason"):
            self.assertNotIn(field, r.STABLE_TASK_IDENTITY)
        self.assertNotIn("plan/swarm/TASKS.json", r.canonical_bytes(r.STABLE_TASK_IDENTITY).decode("ascii"))

    def test_identity_task_fields_match_row(self) -> None:
        identity = r.task_identity()
        self.assertEqual(identity["id"], "SDK-FINDSYLLS")
        self.assertEqual(identity["title"], "findsylls")
        self.assertEqual(identity["component"], "findsylls")
        self.assertEqual(identity["verification_profile"], "rate")
        self.assertFalse(identity["board_full_file_hashed"])
        self.assertEqual(
            identity["depends_on"],
            ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        )


class FixtureTests(unittest.TestCase):
    def test_fixture_deterministic_and_bounded(self) -> None:
        first = r.fixture("speech")
        second = r.fixture("speech")
        self.assertEqual(first, second)
        self.assertEqual(len(first), r.FIXTURE_SLOTS)
        self.assertTrue(all(0 <= value <= r.Q15_MAX for value in first))

    def test_tail_partial_geometry(self) -> None:
        self.assertEqual(r.source_samples("tail_partial"), 64_037)
        self.assertEqual(r.slot_count("tail_partial"), 401)
        self.assertEqual(r.source_samples("tail_partial") % r.FRAME_SAMPLES, 37)
        self.assertEqual(len(r.fixture("tail_partial")), 401)

    def test_fixture_digest_stable(self) -> None:
        self.assertEqual(r.fixture_digest("speech"), r.fixture_digest("speech"))
        self.assertEqual(len(r.fixture_digest("speech")), 64)

    def test_unknown_condition_rejected(self) -> None:
        with self.assertRaises(ValueError):
            r.fixture("noise")


class NucleiTests(unittest.TestCase):
    def test_speech_like_counts(self) -> None:
        self.assertEqual(len(r.detect_nuclei(r.fixture("speech"))), 20)
        self.assertEqual(len(r.detect_nuclei(r.fixture("unfamiliar_speech"))), 25)
        self.assertEqual(len(r.detect_nuclei(r.fixture("music"))), 40)
        self.assertEqual(len(r.detect_nuclei(r.fixture("rebuffer"))), 19)
        self.assertEqual(len(r.detect_nuclei(r.fixture("tail_partial"))), 20)

    def test_silence_zero(self) -> None:
        self.assertEqual(r.detect_nuclei(r.fixture("silence")), [])

    def test_peak_picker_rejects_bad_types(self) -> None:
        for bad in ([True], ["1"], [1.0], [-1], [r.Q15_MAX + 1]):
            with self.assertRaises(ValueError):
                r.detect_nuclei(bad)

    def test_minimum_separation_respected(self) -> None:
        peaks = r.detect_nuclei(r.fixture("music"))
        self.assertTrue(all(b - a >= r.NUCLEI_MIN_SEPARATION for a, b in zip(peaks, peaks[1:])))


class MappingTests(unittest.TestCase):
    def test_exact_full_window_mapping(self) -> None:
        self.assertEqual(r.map_duration(64_000, 1, 1), (64_000, 0))
        self.assertEqual(r.map_duration(64_000, 4, 5), (80_000, 0))
        self.assertEqual(r.map_duration(64_000, 5, 4), (51_200, 0))

    def test_tail_partial_mapping_records_remainder(self) -> None:
        self.assertEqual(r.map_duration(64_037, 1, 1), (64_037, 0))
        self.assertEqual(r.map_duration(64_037, 4, 5), (80_046, 1))
        self.assertEqual(r.map_duration(64_037, 5, 4), (51_229, 3))

    def test_invalid_mapping_rejected(self) -> None:
        for args in ((0, 1, 1), (10, 0, 1), (10, 1, 0), (True, 1, 1), (10, True, 1)):
            with self.assertRaises(ValueError):
                r.map_duration(*args)


class RateResultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.results = r.rate_results()

    def test_case_counts(self) -> None:
        self.assertEqual(self.results["condition_count"], 7)
        self.assertEqual(self.results["rate_case_count"], 21)
        self.assertEqual(len(self.results["conditions"]), 7)

    def test_all_targets_match_computed(self) -> None:
        for condition in self.results["conditions"].values():
            for case in condition["rates"].values():
                self.assertEqual(case["target_output_samples"], case["computed_output_samples"])

    def test_identity_rate_is_exact(self) -> None:
        for condition in self.results["conditions"].values():
            self.assertEqual(
                condition["rates"]["1/1"]["computed_output_samples"],
                condition["source_samples"],
            )
            self.assertEqual(condition["rates"]["1/1"]["mapping_remainder"], 0)

    def test_silence_has_zero_count_and_undefined_rate(self) -> None:
        for case in self.results["conditions"]["silence"]["rates"].values():
            self.assertEqual(case["nuclei_proxy_count"], 0)
            self.assertIsNone(case["nuclei_proxy_per_second_milli"])

    def test_unmeasured_fields_are_false(self) -> None:
        for condition in self.results["conditions"].values():
            for case in condition["rates"].values():
                for field in (
                    "renderer_executed",
                    "duration_measured",
                    "pitch_measured",
                    "transient_audibility_measured",
                    "playback_buffering_measured",
                    "device_timing_measured",
                    "listening",
                ):
                    self.assertFalse(case[field], field)

    def test_controls(self) -> None:
        controls = r.controls(self.results)
        self.assertTrue(controls["identity_echo_exact"])
        self.assertTrue(controls["target_duration_exact"])
        self.assertTrue(controls["silence_zero_nuclei"])
        self.assertEqual(controls["constant_count_control"]["absolute_errors"]["speech"], 0)
        self.assertEqual(
            controls["nonzero_mapping_remainders"],
            {"tail_partial:4/5": 1, "tail_partial:5/4": 3},
        )


class ConfigAdmissionTests(unittest.TestCase):
    def test_valid_config_admitted_without_processing(self) -> None:
        case = r.admit_config(r.default_config())
        self.assertEqual(case["status"], "admitted_synthetic_control")
        self.assertFalse(case["processing_attempted"])
        self.assertEqual(case["qualification_effect"], "none")

    def test_every_adverse_config_rejected(self) -> None:
        cases = r.config_rejection_matrix()
        for name, case in cases.items():
            if name == "valid_control":
                self.assertEqual(case["status"], "admitted_synthetic_control")
            else:
                self.assertEqual(case["status"], "rejected", name)
                self.assertTrue(case["reason_codes"], name)
                self.assertFalse(case["processing_attempted"], name)

    def test_nonfinite_and_string_thresholds_rejected(self) -> None:
        cases = r.config_rejection_matrix()
        self.assertEqual(cases["nonfinite_threshold"]["status"], "rejected")
        self.assertEqual(cases["string_threshold"]["status"], "rejected")

    def test_candidate_asset_never_admitted(self) -> None:
        self.assertEqual(r.artifact_admission(None)["status"], "blocked")


class SlotValidationTests(unittest.TestCase):
    def test_valid_slot_control_accepted(self) -> None:
        cases = r.slot_rejection_matrix()
        self.assertEqual(cases["valid_control"]["status"], "accepted_synthetic_control")
        self.assertEqual(cases["valid_control"]["processed_slots"], 0)

    def test_all_adverse_slots_rejected_without_processing(self) -> None:
        cases = r.slot_rejection_matrix()
        for name, case in cases.items():
            if name == "valid_control":
                continue
            self.assertEqual(case["status"], "rejected", name)
            self.assertEqual(case["processed_slots"], 0, name)
            self.assertTrue(case["state_unchanged"], name)
            self.assertTrue(case["reason_codes"], name)

    def test_nonfinite_slot_rejected(self) -> None:
        self.assertEqual(r.slot_rejection_matrix()["nonfinite_slot"]["reason_codes"], ["slot_type_invalid"])


class ArtifactBoundaryTests(unittest.TestCase):
    def test_absent_source_blocked(self) -> None:
        case = r.artifact_admission(None)
        self.assertEqual(case["status"], "blocked")
        self.assertIn("source_tree_absent", case["reason_codes"])
        self.assertFalse(case["imported"])
        self.assertFalse(case["executed"])
        self.assertFalse(case["download_attempted"])
        self.assertEqual(case["qualification_effect"], "none")

    def test_synthetic_metadata_control_never_imported(self) -> None:
        case = r.artifact_admission(r.synthetic_artifact_manifest())
        self.assertEqual(case["status"], "validated_metadata_only")
        self.assertFalse(case["imported"])
        self.assertFalse(case["executed"])
        self.assertEqual(case["qualification_effect"], "none")

    def test_malformed_artifacts_blocked(self) -> None:
        cases = r.artifact_cases()
        for name, case in cases.items():
            if name == "synthetic_metadata_control":
                continue
            self.assertEqual(case["status"], "blocked", name)
            self.assertTrue(case["reason_codes"], name)

    def test_only_research_scope_accepted(self) -> None:
        cases = r.use_scope_cases()
        self.assertEqual(cases["research_evaluation"]["status"], "accepted_research_evaluation_control")
        for name in ("commercial_product", "redistribution", "public_playback", "customer_deployment", "unknown_scope"):
            self.assertEqual(cases[name]["status"], "rejected", name)


class ReportContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = r.build_report()
        self.contract = r.build_contract()

    def test_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertTrue(self.report["incomplete"])
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertFalse(self.report["qualification"]["qualified"])
        self.assertFalse(self.report["qualification"]["missing_result_may_qualify"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(self.report["release_gate_count"], 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["evidence"] and gate["reopen"] for gate in gates))
        self.assertEqual(self.report["counts"]["release_gates_blocked"], 8)
        self.assertEqual(self.contract["release_gate_count"], 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in self.contract["release_gates"]))

    def test_all_claims_false(self) -> None:
        self.assertTrue(all(value is False for value in self.report["claims"].values()))
        for key, value in self.report["boundary"].items():
            if key == "installed_v0_geometry_preserved":
                self.assertTrue(value, key)
            else:
                self.assertFalse(value, key)
        for key in (
            "real_findsylls_runtime",
            "candidate_source_imported",
            "candidate_source_executed",
            "duration_measured",
            "pitch_measured",
            "playback_buffering_measured",
            "device_timing_measured",
            "listening_result_produced",
            "benchmark_result",
            "release_claim",
        ):
            self.assertFalse(self.report["claims"][key], key)

    def test_candidate_and_rights_status(self) -> None:
        candidate = self.report["candidate_status"]
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["implementation_present"])
        self.assertIsNone(candidate["pinned_revision"])
        self.assertTrue(candidate["reported_offline_whole_utterance"])
        self.assertFalse(candidate["reported_streaming"])
        reference = self.report["reference_evidence"]
        self.assertEqual(reference["status"], "blocked")
        self.assertFalse(reference["surrogate_is_candidate"])
        rights = self.report["rights"]
        self.assertFalse(rights["license_text_staged"])
        self.assertFalse(rights["commercial_use_permitted"])
        self.assertFalse(rights["qualifies"])
        self.assertEqual(rights["status"], "unverified")

    def test_rate_profile_summary(self) -> None:
        profile = self.report["rate_profile"]
        self.assertEqual(profile["profile"], "rate")
        self.assertFalse(profile["qualifies"])
        self.assertEqual(profile["rate_case_count"], 21)
        self.assertFalse(any(profile["measured"].values()))
        self.assertEqual(profile["requirements"]["pitch"]["status"], "blocked")
        self.assertEqual(profile["requirements"]["source_output_mapping"]["status"], "synthetic_only")

    def test_contract_has_no_self_pin(self) -> None:
        contract = r.build_contract({"reference.py": "0" * 64})
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertFalse(contract["qualified"])
        self.assertTrue(contract["proposal_only"])
        self.assertTrue(contract["incomplete"])
        self.assertNotIn("contract.json", contract["artifact_pins"])
        self.assertFalse(contract["board_policy"]["full_file_hashed"])
        self.assertTrue(contract["board_policy"]["stable_fields_only"])

    def test_report_round_trips_strict_json(self) -> None:
        payload = r.canonical_report_bytes(self.report)
        loaded = strict_load(payload)
        self.assertEqual(loaded["task"], "SDK-FINDSYLLS")
        self.assertTrue(payload.endswith(b"\n") and not payload.endswith(b"\n\n"))


class PinAndGenerationTests(unittest.TestCase):
    def test_source_pins_match_disk(self) -> None:
        for name, digest in r.SOURCE_PINS.items():
            path = r.SOURCE_ROOT / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(r.sha256_file(path), digest, name)

    def test_boundary_pins_match_disk(self) -> None:
        for name, digest in r.BOUNDARY_PINS.items():
            path = r.SDK_ROOT / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(r.sha256_file(path), digest, name)

    def test_three_generations_identical(self) -> None:
        payloads = cli.generate_thrice()
        self.assertEqual(set(payloads), {"README.md", "contract.json", "report.json", "report.json.sha256", "SOURCES.sha256"})
        digest = hashlib.sha256(payloads["report.json"]).hexdigest()
        self.assertEqual(payloads["report.json.sha256"], f"{digest}  report.json\n".encode("ascii"))
        self.assertEqual(payloads["README.md"].count(b"<!-- DIGEST_TABLE_START -->"), 1)
        for name in cli.TABLE_FILES:
            payload = payloads.get(name)
            if payload is None:
                payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            self.assertIn(row.encode("ascii"), payloads["README.md"])

    def test_manifest_has_no_tasks_json(self) -> None:
        payload = cli.generate_thrice()["SOURCES.sha256"].decode("ascii")
        self.assertNotIn("TASKS.json", payload)
        self.assertNotIn("plan/swarm/TASKS.json", payload)
        self.assertIn("source:cpp-library/pipeline-validation/playback-speed-candidates.md", payload)

    def test_readme_required_phrases(self) -> None:
        text = cli.generate_thrice()["README.md"].decode("utf-8")
        for phrase in ("DEFER", "not_qualified", "incomplete", "eight", "blocked", "no candidate", "evaluation"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
