# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the SDK-CRNN-VAD evidence package.

No network, no skips and no candidate asset. The tests exercise strict JSON,
exact fixture arithmetic, the integer surrogate, Analysis-profile mechanics,
adverse rejection, determinism and the non-qualification invariants.
"""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_canonical_text_sorted_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": [True, None]}),
                         '{"a":[true,null],"b":1}')

    def test_canonical_rejects_float(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.canonical_text({"value": 0.5})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.load_strict_json_text('{"a":1,"a":2}')
        self.assertTrue(caught.exception.code.startswith("duplicate_json_key"))

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.ReferenceRejection):
                reference.load_strict_json_text('{"a":' + token + "}")

    def test_malformed_and_trailing_rejected(self) -> None:
        for text in ('{"a":', '{"a":1}{"b":2}', "\ufeff{\"a\":1}"):
            with self.assertRaises(reference.ReferenceRejection):
                reference.load_strict_json_text(text)

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_object_text("[1,2]")

    def test_object_root_accepted(self) -> None:
        self.assertEqual(reference.load_strict_json_object_text('{"a":1}'),
                         {"a": 1})


class ConfigTests(unittest.TestCase):
    def test_default_config_valid(self) -> None:
        config = reference.default_config()
        self.assertEqual(reference.validate_config(config), config)

    def test_bad_configs_rejected(self) -> None:
        base = reference.default_config()
        cases = (
            {"sample_rate_hz": 8000},
            {"channels": 2},
            {"frame_samples": 256},
            {"sample_format": "int16"},
            {"epoch": -1},
            {"execution_mode": "processing_thread"},
            {"resampling": "linear"},
            {"clock_ppm": 1001},
            {"origin_ns": -1},
            {"first_input_sample": -1},
        )
        for update in cases:
            config = dict(base)
            config.update(update)
            with self.assertRaises(reference.ReferenceRejection, msg=update):
                reference.validate_config(config)

    def test_bool_rate_and_float_epoch_rejected(self) -> None:
        for update in ({"sample_rate_hz": True}, {"epoch": 0.0}):
            config = dict(reference.default_config())
            config.update(update)
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_config(config)

    def test_missing_and_extra_keys_rejected(self) -> None:
        for mutate in (lambda c: c.pop("clock_ppm"),
                       lambda c: c.update({"extra": 1})):
            config = reference.default_config()
            mutate(config)
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_config(config)


class FixtureTests(unittest.TestCase):
    def test_fixture_geometry(self) -> None:
        fixture = reference.build_fixture()
        self.assertEqual(fixture["length_samples"], reference.STREAM_SAMPLES)
        self.assertEqual(fixture["frame_count"], 260)
        self.assertEqual(fixture["length_samples"] % reference.FRAME_SAMPLES, 0)
        self.assertEqual(len(fixture["truth_runs"]), 3)
        self.assertEqual(len(fixture["truth_frames"]), 170)

    def test_fixture_deterministic(self) -> None:
        first = reference.build_fixture()
        second = reference.build_fixture()
        self.assertEqual(first["signal_sha256"], second["signal_sha256"])
        self.assertEqual(first["samples_int"], second["samples_int"])
        self.assertEqual(first["signal_sha256"],
                         "878c40a0674885f39010a97a121bc5ebe5883eb95e557e2d8a0d90f1fc81862a")

    def test_fixture_segments_frame_aligned(self) -> None:
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start"] % reference.FRAME_SAMPLES, 0)
            self.assertEqual(segment["end"] % reference.FRAME_SAMPLES, 0)

    def test_fixture_is_not_candidate_audio(self) -> None:
        spec = reference.fixture_spec(reference.build_fixture())
        self.assertTrue(spec["synthetic"])
        self.assertFalse(spec["real_speech"])
        self.assertFalse(spec["candidate_audio"])


class FeatureTests(unittest.TestCase):
    def test_silence_features(self) -> None:
        features = reference.frame_features([0.0] * 160, 160)
        self.assertEqual(features["rms"], 0)
        self.assertEqual(features["zcr"], 0)
        self.assertEqual(reference.probability_micro(0, 0), 0)

    def test_probability_bounds_and_monotonicity(self) -> None:
        previous = -1
        for rms in (0, 100, 250, 500, 900, 1500, 4000, 20000):
            probability = reference.probability_micro(rms, 10)
            self.assertTrue(0 <= probability <= reference.PROBABILITY_SCALE)
            self.assertGreaterEqual(probability, previous)
            previous = probability
        self.assertGreater(reference.probability_micro(5000, 10), 500000)

    def test_high_zcr_reduces_probability(self) -> None:
        low_zcr = reference.probability_micro(5000, 5)
        high_zcr = reference.probability_micro(5000, 150)
        self.assertLess(high_zcr, low_zcr)

    def test_nonfinite_input_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            frame = [0.0] * 159 + [value]
            with self.assertRaises(reference.ReferenceRejection):
                reference.frame_features(frame, 160)

    def test_bool_and_string_samples_rejected(self) -> None:
        for value in (True, "0.0"):
            frame = [0.0] * 159 + [value]
            with self.assertRaises(reference.ReferenceRejection):
                reference.frame_features(frame, 160)


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = reference.build_fixture()
        cls.stream = reference.run_stream(cls.fixture["samples"],
                                       session_id="tests")

    def test_event_count_and_intervals(self) -> None:
        self.assertEqual(len(self.stream["events"]), 260)
        self.assertEqual(self.stream["events"][0]["source_start"], 0)
        self.assertEqual(self.stream["events"][-1]["source_end"],
                         reference.STREAM_SAMPLES)
        for previous, current in zip(self.stream["events"],
                                     self.stream["events"][1:]):
            self.assertEqual(previous["source_end"], current["source_start"])

    def test_sequences_contiguous(self) -> None:
        self.assertEqual([event["sequence"] for event in self.stream["events"]],
                         list(range(1, 261)))

    def test_three_detected_runs_and_zero_delay(self) -> None:
        boundaries = reference.boundary_report(self.stream["events"],
                                               self.fixture)
        self.assertEqual(boundaries["detected_runs"], 3)
        self.assertTrue(boundaries["all_matched"])
        self.assertEqual(boundaries["max_abs_onset_delay_frames"], 0)
        self.assertEqual(boundaries["max_abs_offset_delay_frames"], 0)
        self.assertFalse(boundaries["candidate_boundary_parity"])

    def test_detection_counts(self) -> None:
        score = reference.score_events(self.stream["events"], self.fixture)
        self.assertEqual(score["scored_frames"], 260)
        self.assertEqual(score["positives"], 170)
        self.assertEqual(score["negatives"], 90)
        self.assertEqual(score["true_positives"], 170)
        self.assertEqual(score["true_negatives"], 90)
        self.assertEqual(score["false_positives"], 0)
        self.assertEqual(score["false_negatives"], 0)
        self.assertEqual(score["accuracy_ppm"], 1000000)
        self.assertEqual(score["brier_micro"], 9879)
        self.assertFalse(score["qualifies"])

    def test_threshold_sensitivity_is_stratified(self) -> None:
        sweep = reference.threshold_sensitivity_check(self.stream["events"],
                                                      self.fixture)
        self.assertTrue(sweep["strata_respond_to_threshold"])
        high = sweep["thresholds"][-1]
        self.assertGreater(high["fn_ppm"], 0)
        self.assertEqual(high["fp_ppm"], 0)

    def test_availability_formula(self) -> None:
        availability = reference.availability_report(self.stream["events"])
        self.assertTrue(availability["monotone"])
        self.assertTrue(availability["formula_matches"])
        self.assertTrue(availability["exact_half_open_intervals"])
        self.assertFalse(availability["device_timing_measured"])
        self.assertFalse(availability["qualifies"])

    def test_cross_hop_identity(self) -> None:
        check = reference.cross_hop_check(self.fixture)
        self.assertTrue(check["all_match"])
        self.assertEqual(check["accepted_samples"],
                         reference.STREAM_SAMPLES)
        self.assertFalse(check["scheduler_measured"])

    def test_reset_matches_fresh(self) -> None:
        check = reference.reset_check(self.fixture)
        self.assertTrue(check["matches_fresh"])
        self.assertTrue(check["previous_events_cleared"])
        self.assertEqual(check["reset_epoch"], 2)

    def test_independent_state(self) -> None:
        check = reference.independent_state_check(self.fixture)
        self.assertTrue(check["speech_digest_matches_solo"])
        self.assertTrue(check["quiet_digest_matches_solo"])

    def test_invalid_and_missing_are_not_nonspeech(self) -> None:
        check = reference.invalid_vs_nonspeech_check(self.fixture)
        self.assertEqual(check["known_events"], 2)
        self.assertEqual(check["invalid_events"], 1)
        self.assertEqual(check["missing_events"], 1)
        self.assertTrue(check["invalid_probability_is_null"])
        self.assertTrue(check["missing_probability_is_null"])
        self.assertFalse(check["invalid_counted_as_nonspeech"])
        self.assertTrue(check["denominator_excludes_invalid"])

    def test_final_partial_137(self) -> None:
        check = reference.final_partial_check(self.fixture["samples"])
        self.assertEqual(check["valid_count"], 137)
        self.assertEqual(check["padding_samples"], 23)
        self.assertTrue(check["advanced_by_valid_count"])
        self.assertTrue(check["interval_exact"])
        self.assertTrue(check["post_final_rejected"])

    def test_event_bus_drops_stale_and_overflow(self) -> None:
        check = reference.event_bus_check(self.stream["events"])
        self.assertEqual(check["overflow_accepted"], 4)
        self.assertEqual(check["overflow_dropped"], 2)
        self.assertEqual(check["overflow_reasons"], ["queue_full"])
        self.assertTrue(check["stale_epoch_dropped"])
        self.assertTrue(check["stale_sequence_dropped"])

    def test_invalid_chunk_plan_rejected(self) -> None:
        for plan in ([160, 160], [0] * 260):
            with self.assertRaises(reference.ReferenceRejection):
                reference.run_stream(self.fixture["samples"],
                                     chunk_sizes=plan)


class RejectionTests(unittest.TestCase):
    def test_all_adverse_cases_rejected_immutably(self) -> None:
        fixture = reference.build_fixture()
        records = reference.adverse_rejections(fixture)
        self.assertGreaterEqual(len(records), 40)
        self.assertEqual(len(records), 73)
        for record in records:
            self.assertEqual(record["status"], "rejected")
            self.assertTrue(record["state_unchanged"], record["case_id"])
            self.assertEqual(record["state_digest_before"],
                             record["state_digest_after"], record["case_id"])
            self.assertTrue(record["code"])

    def test_state_unchanged_is_measured_not_forced(self) -> None:
        fixture = reference.build_fixture()
        records = reference.adverse_rejections(fixture)
        digests = {(record["state_digest_before"],
                    record["state_digest_after"]) for record in records}
        self.assertGreater(len(digests), 1)
        for record in records:
            measured = (record["state_digest_after"]
                        == record["state_digest_before"])
            self.assertEqual(record["state_unchanged"], measured,
                             record["case_id"])

    def test_mutation_probe_is_caught(self) -> None:
        fixture = reference.build_fixture()
        session = reference.AnalysisSession(
            reference.default_config(), "mutation-probe", 0)
        frame = list(fixture["samples"][:reference.FRAME_SAMPLES])
        session.process_frame(frame)

        def mutating_action() -> None:
            session.process_frame(frame)
            raise reference.ReferenceRejection("deliberate_probe")

        records = []
        reference._run_rejection(records, "mutation_probe",
                                 session.state_digest, mutating_action)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertFalse(record["state_unchanged"])
        self.assertNotEqual(record["state_digest_before"],
                            record["state_digest_after"])
        self.assertFalse(record["state_digest_before"]
                         == record["state_digest_after"])

    def test_required_adverse_cases_present(self) -> None:
        records = reference.adverse_rejections(reference.build_fixture())
        ids = {record["case_id"] for record in records}
        required = {
            "duplicate_json_key", "nan_json_constant", "malformed_json",
            "config_8000_hz", "config_stereo", "frame_nonfinite_nan",
            "frame_nonfinite_inf", "frame_nonzero_padding",
            "frame_after_final", "manifest_bad_hash", "event_bad_validity",
        }
        self.assertTrue(required <= ids)

    def test_caller_manifest_shape_only(self) -> None:
        manifest = {
            "asset_storage": "external",
            "candidate_id": "crnn-vad",
            "license_id": "caller-declared",
            "runtime_id": "caller.runtime.v0",
            "source_revision": "0" * 40,
            "source_sha256": "1" * 64,
            "weights_byte_count": 1024,
            "weights_sha256": "2" * 64,
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["verified"])

    def test_caller_manifest_adverse(self) -> None:
        manifest = {
            "asset_storage": "external",
            "candidate_id": "crnn-vad",
            "license_id": "caller-declared",
            "runtime_id": "caller.runtime.v0",
            "source_revision": "0" * 40,
            "source_sha256": "1" * 64,
            "weights_byte_count": 1024,
            "weights_sha256": "2" * 64,
        }
        for update in ({"weights_sha256": "zz"},
                       {"asset_storage": "vendored"},
                       {"candidate_id": "crnn"},
                       {"weights_byte_count": 0},
                       {"license_id": "unknown"},
                       {"extra": 1}):
            candidate = dict(manifest)
            candidate.update(update)
            with self.assertRaises(reference.ReferenceRejection, msg=update):
                reference.validate_caller_manifest(candidate)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract_text = reference.canonical_text(
            reference.build_contract(
                cls.report,
                reference.canonical_report(cls.report)[1])) + "\n"

    def test_report_invariants(self) -> None:
        report = self.report
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA)
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["defer_before"], "opt_in_adapter_exposure")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["profile"], "analysis")

    def test_qualification_not_promoted(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        for key, value in qualification.items():
            if key == "status":
                continue
            self.assertIs(value, False, key)

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(index) for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_eight_blocked_exact_requirements(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertTrue(all(blocker["status"] == "blocked"
                            and blocker["present"] is False
                            for blocker in blockers))

    def test_candidate_is_absent(self) -> None:
        candidate = self.report["candidate"]
        for key in ("architecture", "checkpoint", "source_revision",
                    "source_sha256", "weights_sha256", "parameter_count",
                    "reported_sample_rate_hz", "reported_hop_samples",
                    "reported_window_samples", "reported_output_geometry",
                    "license", "paper_reference"):
            self.assertIsNone(candidate[key], key)
        for key in ("source_present", "weights_present", "runtime_present",
                    "adapter_present", "geometry_documented",
                    "exact_numeric_output_present", "implemented_here"):
            self.assertIs(candidate[key], False, key)

    def test_profile_items_synthetic_only(self) -> None:
        items = self.report["acceptance_profile"]["required_items"]
        self.assertEqual(len(items), 13)
        self.assertTrue(all(item["status"] == "synthetic_only"
                            for item in items.values()))
        self.assertEqual(self.report["profile_blockers"], [])

    def test_surrogate_and_scorer_independent(self) -> None:
        model = self.report["surrogate_model"]
        scorer = self.report["scorer"]
        self.assertNotEqual(model["sha256"], scorer["sha256"])
        self.assertEqual(model["sha256"],
                         reference.object_digest(model["spec"]))
        self.assertEqual(scorer["sha256"],
                         reference.object_digest(scorer["spec"]))
        for key in ("is_crnn", "is_learned", "has_convolution",
                    "has_recurrence", "uses_weights", "uses_checkpoint"):
            self.assertIs(model["spec"][key], False, key)
        self.assertFalse(model["qualifies"])
        self.assertFalse(scorer["qualifies"])

    def test_results_are_unqualified(self) -> None:
        results = self.report["results"]
        for section in ("probabilities", "boundaries", "detections",
                        "validity", "availability", "events", "cross_hop"):
            self.assertFalse(results[section]["qualifies"], section)
        self.assertFalse(results["probabilities"]["candidate_probability_parity"])
        self.assertFalse(results["detections"]["heldout"])

    def test_board_row_stable_only(self) -> None:
        row = self.report["board_row"]
        self.assertIs(row["full_tasks_json_hashed"], False)
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(row["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])
        for section in ("source_pins", "boundary_pins"):
            for path in self.report[section]:
                self.assertFalse(path.endswith("TASKS.json"))

    def test_scope_and_boundary_are_closed(self) -> None:
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        scope = self.report["scope"]
        for key, value in scope.items():
            if key == "write_scope":
                self.assertEqual(value, "docs/task-evidence/crnn-vad/ only")
            else:
                self.assertIs(value, False, key)

    def test_adverse_records_all_rejected(self) -> None:
        records = self.report["adverse_rejections"]
        self.assertTrue(self.report["adverse_all_rejected"])
        self.assertTrue(records)
        for record in records:
            self.assertEqual(record["status"], "rejected")
            self.assertTrue(record["state_unchanged"])

    def test_three_rounds_byte_identical(self) -> None:
        payloads = []
        for _ in range(3):
            report = reference.build_report()
            text, digest = reference.canonical_report(report)
            contract = reference.canonical_text(
                reference.build_contract(report, digest)) + "\n"
            payloads.append((text, digest, contract))
        self.assertEqual(payloads[0], payloads[1])
        self.assertEqual(payloads[1], payloads[2])

    def test_generated_files_match_builder(self) -> None:
        report_text, report_digest = reference.canonical_report(self.report)
        report_path = HERE / "report.json"
        sidecar_path = HERE / "report.json.sha256"
        contract_path = HERE / "contract.json"
        self.assertTrue(report_path.is_file())
        self.assertEqual(report_path.read_bytes(),
                         report_text.encode("utf-8"))
        self.assertEqual(sidecar_path.read_text(encoding="ascii"),
                         report_digest + "\n")
        self.assertEqual(contract_path.read_text(encoding="utf-8"),
                         self.contract_text)

    def test_sources_manifest(self) -> None:
        payload = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        lines = [line for line in payload.splitlines()
                 if line and not line.startswith("#")]
        self.assertGreaterEqual(len(lines), 20)
        for path in reference.SOURCE_PINS:
            self.assertIn("source:" + path, payload)
        for path in reference.BOUNDARY_PINS:
            self.assertIn("  " + path, payload)
        self.assertNotIn("TASKS.json", payload)
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         reference.sources_bytes())


class LicensingTests(unittest.TestCase):
    ALLOWED = {
        "README.md", "contract.json", "contract.json.license", "reference.py",
        "report.json", "report.json.license", "report.json.sha256",
        "report.json.sha256.license", "run.py", "SOURCES.sha256",
        "SOURCES.sha256.license", "test_reference.py", "verify.py",
    }

    def test_directory_has_only_allowed_files(self) -> None:
        present = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertEqual(present, self.ALLOWED)

    def test_license_sidecars(self) -> None:
        expected = (b"SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
                    b"SPDX-License-" b"Identifier: Apache-2.0\n")
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license", "SOURCES.sha256.license"):
            self.assertEqual((HERE / name).read_bytes(), expected, name)

    def test_python_and_readme_headers(self) -> None:
        for name in ("reference.py", "run.py", "test_reference.py",
                     "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertTrue(text.startswith(
                "# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
                "# SPDX-License-" "Identifier: Apache-2.0\n"), name)
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith(
            "<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->\n"
            "<!-- SPDX-License-" "Identifier: Apache-2.0 -->\n"))


class DigestTests(unittest.TestCase):
    def test_sha256_helper(self) -> None:
        self.assertEqual(reference.sha256_bytes(b"abc"),
                         hashlib.sha256(b"abc").hexdigest())

    def test_round_ratio(self) -> None:
        self.assertEqual(reference.round_ratio(1, 2), 1)
        self.assertEqual(reference.round_ratio(1, 3), 0)
        self.assertEqual(reference.round_ratio(2, 3), 1)
        with self.assertRaises(reference.ReferenceRejection):
            reference.round_ratio(1, 0)

    def test_math_is_deterministic(self) -> None:
        self.assertEqual(math.isqrt(160 * 160), 160)
        self.assertEqual(json.loads('{"a":1}'), {"a": 1})


if __name__ == "__main__":
    unittest.main()
