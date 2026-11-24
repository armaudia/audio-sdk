# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the synthetic FastVAD analysis evidence."""

from __future__ import annotations

import json
import math
from pathlib import Path
import unittest

import fixture
import reference
import run as cli
import scorer

TASK_DIR = Path(__file__).resolve().parent
SPDX_TAG = "SPDX" "-License-Identifier:"
EXPECTED_FIXTURE_DIGEST = "dc723fab2334cedf1342fbe1a8726ef488f011a786be466c5588a1128a874dda"


class SourcePinTests(unittest.TestCase):
    def test_all_pinned_sources_exist_and_match(self) -> None:
        self.assertGreaterEqual(len(fixture.SOURCE_PINS), 4)
        for name, expected in fixture.SOURCE_PINS.items():
            path = fixture.resolve_pin_path(name)
            self.assertTrue(path.is_file(), "missing pinned source " + name)
            self.assertEqual(fixture.sha256_file(path), expected, name)

    def test_required_task_sources_are_pinned(self) -> None:
        for name in (
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "reports/vad-research/chaining-evaluation.md",
            "adapters/fast-vad/adapter.json",
            "REALTIME_COMPONENT_CANDIDATES.md",
        ):
            self.assertIn(name, fixture.SOURCE_PINS)

    def test_mutable_board_is_provenance_only(self) -> None:
        board = fixture.resolve_pin_path(fixture.MUTABLE_BOARD)
        self.assertTrue(board.is_file())
        self.assertEqual(len(fixture.MUTABLE_BOARD_SHA256_AT_READ), 64)

    def test_source_cli_output_is_byte_identical(self) -> None:
        payloads = [fixture.canonical_bytes(cli.sources_payload()) for _ in range(3)]
        self.assertEqual(len(set(payloads)), 1)


class FixtureTests(unittest.TestCase):
    def test_pcm_generation_is_deterministic(self) -> None:
        self.assertEqual(fixture.build_pcm_int(), fixture.build_pcm_int())
        self.assertEqual(len(fixture.build_pcm()), fixture.TOTAL_SAMPLES)

    def test_fixture_spec_digest_is_frozen(self) -> None:
        self.assertEqual(fixture.FIXTURE_SPEC_DIGEST, EXPECTED_FIXTURE_DIGEST)

    def test_pcm_is_finite_f32_scaled_and_mono(self) -> None:
        pcm = fixture.build_pcm()
        self.assertTrue(all(math.isfinite(value) for value in pcm))
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in pcm))
        self.assertEqual(fixture.CONFIG["channels"], 1)
        self.assertEqual(fixture.CONFIG["sample_format"], "f32")

    def test_frame_intervals_cover_source_exactly(self) -> None:
        boundaries = [index * fixture.FRAME_SAMPLES for index in range(fixture.TOTAL_FRAMES)]
        boundaries.append(fixture.TOTAL_SAMPLES)
        self.assertEqual(boundaries[-1], 16000)
        self.assertEqual(len(boundaries), fixture.TOTAL_FRAMES + 1)

    def test_truth_segments_partition_all_samples(self) -> None:
        covered = []
        for segment in fixture.SEGMENTS:
            covered.extend(range(segment["start"], segment["end"]))
        self.assertEqual(covered, list(range(fixture.TOTAL_SAMPLES)))

    def test_truth_intervals(self) -> None:
        self.assertEqual(fixture.truth_intervals("speech"),
                         [(960, 2560), (3520, 6080), (7040, 7840)])
        self.assertEqual(fixture.truth_intervals("unknown"), [(8640, 9920)])

    def test_real_runtime_flags_are_false(self) -> None:
        self.assertFalse(fixture.CONFIG["real_runtime"])
        self.assertFalse(fixture.CONFIG["wheel_or_licensed_runtime_used"])


class SessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frames = fixture.build_frames()
        cls.session = reference.Session(fixture.CONFIG, "primary", 1)
        reference.drive(cls.session, cls.frames)
        cls.session.drain()
        cls.events = cls.session.events
        cls.runs = cls.session.speech_events

    def test_probability_events_cover_exact_intervals(self) -> None:
        starts = [event["start_sample"] for event in self.events]
        ends = [event["end_sample"] for event in self.events]
        self.assertEqual(starts[0], 0)
        self.assertEqual(ends[-1], fixture.TOTAL_SAMPLES)
        self.assertEqual(starts[1:], ends[:-1])
        self.assertEqual(len(self.events), 100)

    def test_probabilities_are_finite_and_bounded(self) -> None:
        for event in self.events:
            self.assertTrue(math.isfinite(event["probability"]))
            self.assertGreaterEqual(event["probability"], 0.0)
            self.assertLessEqual(event["probability"], 1.0)

    def test_availability_formula_and_monotonicity(self) -> None:
        known = [event for event in self.events if event["validity"] == "known"]
        values = [event["available_ns"] for event in known]
        self.assertTrue(all(right > left for left, right in zip(values, values[1:])))
        for event in known:
            expected = (fixture.ORIGIN_NS + event["end_sample"] * fixture.SAMPLE_NS
                        + fixture.PROCESSING_DELAY_NS)
            self.assertEqual(event["available_ns"], expected)

    def test_unknown_events_have_no_availability_or_decision(self) -> None:
        unknown = [event for event in self.events if event["validity"] == "unknown"]
        self.assertEqual(len(unknown), 8)
        self.assertTrue(all(event["available_ns"] is None for event in unknown))
        self.assertTrue(all(event["decision"] is None for event in unknown))

    def test_speech_events_have_exact_source_intervals(self) -> None:
        self.assertEqual([(run["start_sample"], run["end_sample"]) for run in self.runs],
                         [(2240, 2560), (3520, 6080), (6720, 7040)])
        for run in self.runs:
            self.assertLess(run["start_sample"], run["end_sample"])
            self.assertEqual(run["clock"], fixture.CLOCK)

    def test_session_summary_digests(self) -> None:
        summary = self.session.summary()
        self.assertEqual(summary["probability_events"], 100)
        self.assertEqual(summary["speech_events"], 3)
        self.assertEqual(summary["probability_event_digest"],
                         "acff6c1e2b6a30262267e4a81f6a25497de3fdeb47f3e241315d2d8e57c93d63")
        self.assertEqual(summary["speech_event_digest"],
                         "a98fc27467eb23bea2e9f9e5713c6361d63cbac1a9d75a9764543879c7107c7c")

    def test_rejection_does_not_mutate_state(self) -> None:
        session = reference.Session(fixture.CONFIG, "reject", 1)
        session.process_frame(self.frames[0], validity="known", start_sample=0,
                              end_sample=fixture.FRAME_SAMPLES)
        before = session.summary()["state_digest"]
        record = session.process_frame(self.frames[1], epoch=0, validity="known",
                                       start_sample=fixture.FRAME_SAMPLES,
                                       end_sample=2 * fixture.FRAME_SAMPLES)
        self.assertEqual(record["reason"], "stale_epoch")
        self.assertEqual(session.summary()["state_digest"], before)

    def test_nonfinite_frame_rejected(self) -> None:
        session = reference.Session(fixture.CONFIG, "nonfinite", 1)
        record = session.process_frame([float("nan")] * fixture.FRAME_SAMPLES,
                                       validity="known", start_sample=0,
                                       end_sample=fixture.FRAME_SAMPLES)
        self.assertEqual(record["reason"], "nonfinite_frame")

    def test_wrong_interval_rejected(self) -> None:
        session = reference.Session(fixture.CONFIG, "interval", 1)
        record = session.process_frame(self.frames[0], validity="known", start_sample=1,
                                       end_sample=fixture.FRAME_SAMPLES + 1)
        self.assertEqual(record["reason"], "wrong_source_interval")

    def test_duplicate_sequence_rejected(self) -> None:
        session = reference.Session(fixture.CONFIG, "sequence", 1)
        session.process_frame(self.frames[0], validity="known", start_sample=0,
                              end_sample=fixture.FRAME_SAMPLES)
        record = session.process_frame(self.frames[1], validity="known", sequence=1,
                                       start_sample=fixture.FRAME_SAMPLES,
                                       end_sample=2 * fixture.FRAME_SAMPLES)
        self.assertEqual(record["reason"], "duplicate_or_out_of_order_sequence")

    def test_missing_and_nonfinite_probability_rejected(self) -> None:
        session = reference.Session(fixture.CONFIG, "probability", 1)
        for token, expected in ((reference.EXPLICIT_MISSING, "missing_probability"),
                                (float("nan"), "nonfinite_probability"),
                                (1.5, "probability_out_of_range")):
            record = session.process_frame(self.frames[0], validity="known", start_sample=0,
                                           end_sample=fixture.FRAME_SAMPLES, probability=token)
            self.assertEqual(record["reason"], expected)

    def test_final_partial_frame_is_accepted_with_exact_coordinates(self) -> None:
        session = reference.Session(fixture.CONFIG, "partial", 1)
        record = session.process_frame([0.0] * 80, validity="known", start_sample=0,
                                       end_sample=80, probability=0.1,
                                       is_final=True, valid_samples=80)
        self.assertEqual(record["status"], "ok")
        self.assertEqual(record["probability_event"]["end_sample"], 80)
        self.assertEqual(record["probability_event"]["available_ns"],
                         fixture.ORIGIN_NS + 80 * fixture.SAMPLE_NS
                         + fixture.PROCESSING_DELAY_NS)

    def test_invalid_configuration_rejected(self) -> None:
        for key, value in (("sample_rate_hz", 48000), ("frame_samples", 320),
                           ("real_runtime", True)):
            config = dict(fixture.CONFIG)
            config[key] = value
            with self.assertRaises(ValueError):
                fixture.validate_config(config)


class ScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frames = fixture.build_frames()
        cls.session = reference.Session(fixture.CONFIG, "primary", 1)
        reference.drive(cls.session, cls.frames)
        cls.session.drain()
        cls.result = scorer.score_stream(cls.session.events, cls.session.speech_events)

    def test_overall_confusion_exact(self) -> None:
        self.assertEqual(self.result["detections"]["overall"],
                         {"TP": 2880, "FN": 2080, "FP": 320, "TN": 9440})

    def test_denominators_and_rates_exact(self) -> None:
        detections = self.result["detections"]
        self.assertEqual(detections["speech_samples"], 4960)
        self.assertEqual(detections["nonspeech_samples"], 9760)
        self.assertEqual(detections["speech_miss_rate"], 0.41935483871)
        self.assertEqual(detections["false_alarm_rate"], 0.032786885246)
        self.assertEqual(detections["unknown_excluded_samples"], 1280)

    def test_probability_scores_exact(self) -> None:
        probabilities = self.result["probabilities"]
        self.assertEqual(probabilities["known_events"], 92)
        self.assertEqual(probabilities["scored_samples"], 14720)
        self.assertEqual(probabilities["brier_score"], 0.089213865607)
        self.assertEqual(probabilities["log_loss"], 0.239116188343)

    def test_stratified_fn_fp_exact(self) -> None:
        strata = self.result["detections"]["strata"]
        self.assertEqual(strata["quiet-a"]["FN"], 1280)
        self.assertEqual(strata["quiet-a"]["TP"], 320)
        self.assertEqual(strata["active-a"]["TP"], 2560)
        self.assertEqual(strata["quiet-b"]["FN"], 800)
        self.assertEqual(strata["noise-burst"]["FP"], 320)
        self.assertEqual(strata["noise-burst"]["TN"], 640)
        for name in ("idle-a", "idle-b", "idle-c", "idle-d"):
            self.assertEqual(strata[name]["TN"], fixture.SEGMENTS[
                [segment["id"] for segment in fixture.SEGMENTS].index(name)]["end"]
                - fixture.SEGMENTS[
                    [segment["id"] for segment in fixture.SEGMENTS].index(name)]["start"])

    def test_boundary_delays_exact(self) -> None:
        matches = self.result["boundaries"]["matches"]
        self.assertEqual(matches[0]["onset_delay_samples"], 1280)
        self.assertEqual(matches[0]["offset_delay_samples"], 0)
        self.assertEqual(matches[1]["onset_delay_samples"], 0)
        self.assertEqual(matches[1]["offset_delay_samples"], 0)
        self.assertFalse(matches[2]["matched"])
        self.assertEqual(self.result["boundaries"]["false_detected_runs"], [[6720, 7040]])

    def test_invalid_vs_nonspeech_separated(self) -> None:
        control = scorer.invalid_vs_nonspeech_control()
        self.assertEqual(len(control["rejected_cases"]), 4)
        self.assertTrue(all(case["status"] == "rejected"
                            for case in control["rejected_cases"].values()))
        self.assertEqual(control["unknown_excluded_samples"], 160)
        self.assertEqual(control["known_nonspeech_tn"], 160)
        self.assertFalse(control["invalid_counted_as_nonspeech"])

    def test_scorer_rejects_invalid_event(self) -> None:
        bad = dict(self.session.events[0], validity="invalid")
        with self.assertRaises(ValueError):
            scorer.score_stream([bad], [])

    def test_scorer_rejects_empty_known_denominator(self) -> None:
        unknown = dict(self.session.events[0], validity="unknown", decision=None)
        with self.assertRaises(ValueError):
            scorer.score_stream([unknown], [])

    def test_cross_hop_projection_exact(self) -> None:
        control = reference.cross_hop_control()
        self.assertEqual(control["frames"], [[0, 10], [1, 160], [2, 10]])
        self.assertEqual(control["overlap_samples"], 180)
        self.assertEqual(control["truth_hops"], 10)
        self.assertEqual(control["truth_overlap_samples"], 1600)

    def test_crosscheck_matches_scorer(self) -> None:
        payload = reference.crosscheck_payload()
        self.assertEqual(payload["independent_confusion"], payload["scorer_confusion"])
        self.assertEqual(payload["independent_confusion"]["TP"], 2880)
        self.assertTrue(payload["no_tolerance"])


class ReportAndScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.text, cls.digest = reference.canonical_report(cls.report)

    def test_report_key_set(self) -> None:
        self.assertEqual(set(self.report), reference.REPORT_KEYS)

    def test_report_status_and_defer(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["qualification_status"], "incomplete")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertFalse(self.report["processor_exposure"])
        self.assertFalse(self.report["public_surface_changed"])
        self.assertFalse(self.report["installed_v0_changed"])

    def test_report_contains_no_nonfinite_numbers(self) -> None:
        def walk(value: object) -> None:
            if isinstance(value, float):
                self.assertTrue(math.isfinite(value))
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(self.report)

    def test_report_repeats_are_byte_identical(self) -> None:
        payloads = [reference.canonical_report(reference.build_report())[0]
                    for _ in range(3)]
        self.assertEqual(len(set(payloads)), 1)

    def test_report_repeat_digests_match(self) -> None:
        repeat = self.report["repeat_runs"]
        self.assertEqual(repeat["three_repeats"], 3)
        self.assertTrue(repeat["byte_identical"])
        core = dict(self.report)
        core.pop("repeat_runs")
        self.assertEqual(repeat["canonical_digests"],
                         [fixture.sha256_bytes(fixture.canonical_bytes(core))] * 3)

    def test_report_file_and_sidecar_match(self) -> None:
        raw = (TASK_DIR / "report.json").read_bytes()
        self.assertEqual(raw, (self.text + "\n").encode("utf-8") if not self.text.endswith("\n")
                         else self.text.encode("utf-8"))
        sidecar = (TASK_DIR / "report.json.sha256").read_text(encoding="ascii").strip()
        self.assertEqual(sidecar, fixture.sha256_bytes(raw))

    def test_source_manifest_covers_every_local_file(self) -> None:
        manifest = cli.read_manifest()
        names = set(manifest)
        self.assertNotIn("SOURCES.sha256", names)
        for path in TASK_DIR.rglob("*"):
            if path.is_file() and path.name != "SOURCES.sha256" and "__pycache__" not in path.parts:
                name = path.relative_to(TASK_DIR).as_posix()
                self.assertIn(name, names, name)
                self.assertEqual(manifest[name], fixture.sha256_file(path), name)

    def test_contract_is_proposal_only(self) -> None:
        contract = json.loads((TASK_DIR / "contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertEqual(contract["qualification"]["status"], "incomplete")
        self.assertEqual(contract["qualification"]["decision"], "DEFER")
        self.assertFalse(contract["public_surface"]["changed"])
        self.assertFalse(contract["public_surface"]["processor_exposure"])
        self.assertFalse(contract["qualification"]["missing_result_promoted"])

    def test_adapter_and_provider_are_unregistered(self) -> None:
        adapter = json.loads((TASK_DIR / "adapter.json").read_text(encoding="utf-8"))
        provider = json.loads((TASK_DIR / "provider.json").read_text(encoding="utf-8"))
        self.assertFalse(adapter["processor_exposure"])
        self.assertEqual(adapter["decision"], "DEFER")
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["processor_exposure"])
        self.assertEqual(provider["decision"], "DEFER")

    def test_no_native_or_public_surface_files(self) -> None:
        names = {path.relative_to(TASK_DIR).as_posix() for path in TASK_DIR.rglob("*")}
        self.assertFalse(any(name.endswith((".c", ".h", "CMakeLists.txt")) for name in names))

    def test_python_files_carry_split_spdx_tag(self) -> None:
        for path in sorted(TASK_DIR.glob("*.py")):
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertTrue(lines[0].startswith("# SPDX-FileCopyrightText:"), path.name)
            self.assertEqual(lines[1], "# " + SPDX_TAG + " Apache-2.0", path.name)
            self.assertEqual(path.read_text(encoding="utf-8").count(SPDX_TAG), 1, path.name)

    def test_all_markdown_and_json_carry_spdx(self) -> None:
        for path in list(TASK_DIR.glob("*.md")) + list(TASK_DIR.glob("*.json")):
            annotation = TASK_DIR / "report.json.license" if path.name == "report.json" else path
            text = annotation.read_text(encoding="utf-8")
            self.assertIn("SPDX-FileCopyrightText", text, annotation.name)
            self.assertIn("SPDX-License-Identifier", text, annotation.name)

    def test_crosscheck_cli_is_byte_identical(self) -> None:
        payloads = [fixture.canonical_bytes(cli.crosscheck_payload()) for _ in range(3)]
        self.assertEqual(len(set(payloads)), 1)


if __name__ == "__main__":
    unittest.main()
