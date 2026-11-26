# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local SDK-AUBIO evidence package."""

from __future__ import annotations

import copy
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
FIXTURES = HERE / "fixtures.json"
VERIFICATION = (reference.AUDIO_ROOT
                / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility "
    "and playback buffering.",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window.",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation.",
)
EXPECTED_CHECK_IDS = (
    "identity_1x_bpm", "rate_0_8_bpm", "rate_1_2_bpm", "rate_duration_error",
    "speech_no_stable_tempo", "silence_no_onsets", "music_stable",
    "tempo_out_of_range", "low_snr_adverse_nonqualifying",
    "rebuffer_gap_suppressed", "drift_recorded", "final_partial_valid",
    "mapping_nonnegative", "transient_proxy", "all_cases_explicit",
    "all_gates_blocked",
)


def prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-AUBIO"
    target = sdk / "docs/task-evidence/aubio"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


class ContractAndFixturesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = reference.read_strict_json(CONTRACT)
        cls.fixtures = reference.read_strict_json(FIXTURES)

    def test_contract_validates(self):
        reference.validate_contract(self.contract)

    def test_contract_mutations_rejected(self):
        mutations = (
            lambda value: value["decision"].update(registered=True),
            lambda value: value["decision"].update(production_exposure="SHIP"),
            lambda value: value["exact_scope"].update(provider_registration_changed=True),
            lambda value: value["installed_v0"].update(frame_samples=512),
            lambda value: value["installed_v0"].update(changed=True),
            lambda value: value["licensing"].update(relicensed=True),
            lambda value: value["licensing"].update(review="cleared"),
            lambda value: value.update(verification_profile="Analysis"),
            lambda value: value.update(base_commit="0" * 40),
            lambda value: value["decision"].pop("incomplete"),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.contract)
            mutate(value)
            with self.assertRaises(ValueError, msg=str(mutate)):
                reference.validate_contract(value)

    def test_fixtures_validate(self):
        reference.validate_fixtures(self.fixtures)

    def test_fixture_mutations_rejected(self):
        mutations = (
            lambda value: value["stimuli"]["music_like_1x"].update(kind="unknown"),
            lambda value: value["stimuli"]["music_like_1x"].update(extra=1),
            lambda value: value["stimuli"]["music_like_1x"].pop("period_samples"),
            lambda value: value["stimuli"]["music_like_1x"].update(length_samples=64136),
            lambda value: value["stimuli"]["low_snr_adverse"].update(
                amplitude_milli=900),
            lambda value: value["stimuli"]["speech_like_unfamiliar"].update(
                starts_frames=[4, 10] + value["stimuli"]["speech_like_unfamiliar"]["starts_frames"][2:]),
            lambda value: value["stimuli"].update(unexpected={"kind": "silence", "length_samples": 160}),
            lambda value: value.update(task="SDK-OTHER"),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.fixtures)
            mutate(value)
            with self.assertRaises(ValueError, msg=str(mutate)):
                reference.validate_fixtures(value)

    def test_strict_json_rejects_duplicates_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            duplicate = directory / "duplicate.json"
            duplicate.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(duplicate)
            nonfinite = directory / "nonfinite.json"
            nonfinite.write_text('{"a": NaN}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(nonfinite)
            array = directory / "array.json"
            array.write_text('[1, 2]\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(array)


class AnalyzerTests(unittest.TestCase):
    def test_frame_state_advances_only_on_valid_frames(self):
        analyzer = reference.Analyzer()
        before = analyzer.state_digest
        record = analyzer.process_frame([0.0] * 160, epoch=1, input_count=160,
                                        valid_count=160)
        self.assertEqual(record["frame_index"], "0")
        self.assertEqual(record["source_start"], "0")
        self.assertEqual(record["valid_count"], "160")
        self.assertEqual(record["input_count"], "160")
        self.assertIs(record["onset"], False)
        self.assertEqual(analyzer.frame_index, 1)
        self.assertNotEqual(analyzer.state_digest, before)
        self.assertEqual(len(analyzer.frame_records), 1)

    def test_onset_event_is_source_anchored(self):
        signal, _ = reference.generate_signal(
            reference.read_strict_json(FIXTURES)["stimuli"]["music_like_1x"])
        analyzer = reference.Analyzer()
        record = analyzer.process_frame(signal[:160], epoch=1, input_count=160,
                                        valid_count=160)
        self.assertIs(record["onset"], True)
        self.assertEqual(len(analyzer.events), 1)
        event = analyzer.events[0].as_dict()
        self.assertEqual(event["source_start"], "0")
        self.assertEqual(event["source_end"], "160")
        self.assertEqual(event["frame_index"], "0")
        self.assertEqual(event["epoch"], "1")
        self.assertEqual(int(event["available_monotonic_ns"])
                         - int(event["capture_first_ns"]), 10000000)

    def test_final_partial_frame_is_explicit(self):
        analyzer = reference.Analyzer()
        record = analyzer.process_frame([0.5] * 137 + [0.0] * 23, epoch=1,
                                        input_count=160, valid_count=137)
        self.assertEqual(record["valid_count"], "137")
        self.assertEqual(analyzer.frame_index, 1)
        self.assertEqual(analyzer.rejections, [])

    def test_frame_rejections_do_not_advance_state(self):
        def missing(analyzer):
            analyzer.process_frame(None)

        def short(analyzer):
            analyzer.process_frame([0.0] * 159)

        def count(analyzer):
            analyzer.process_frame([0.0] * 160, input_count=159)

        def nan(analyzer):
            analyzer.process_frame([0.0] * 80 + [float("nan")] + [0.0] * 79)

        def infinite(analyzer):
            analyzer.process_frame([float("inf")] + [0.0] * 159)

        def epoch(analyzer):
            analyzer.process_frame([0.0] * 160, epoch=0)

        def valid(analyzer):
            analyzer.process_frame([0.0] * 160, valid_count=0)

        def padding(analyzer):
            analyzer.process_frame([0.0] * 137 + [0.5] + [0.0] * 22,
                                   valid_count=137)

        for call, code in ((missing, "missing_input"), (short, "frame_count_mismatch"),
                           (count, "frame_count_mismatch"), (nan, "nonfinite_input"),
                           (infinite, "nonfinite_input"), (epoch, "epoch_mismatch"),
                           (valid, "invalid_valid_count"),
                           (padding, "padding_not_zero")):
            analyzer = reference.Analyzer()
            before = analyzer.state_digest
            with self.assertRaises(reference.ReferenceRejection) as context:
                call(analyzer)
            self.assertEqual(context.exception.code, code)
            self.assertEqual(analyzer.state_digest, before)
            self.assertEqual(analyzer.frame_index, 0)
            self.assertEqual(analyzer.rejections, [code])

    def test_config_rejections(self):
        for kwargs in ({"sample_rate_hz": 44100}, {"channels": 2},
                       {"frame_samples": 512}, {"sample_format": "float64"},
                       {"epoch": -1}):
            with self.assertRaises(reference.ReferenceRejection):
                reference.Analyzer(**kwargs)

    def test_adverse_cases_are_real_rejections(self):
        fixtures = reference.read_strict_json(FIXTURES)
        cases = reference._adverse_cases(fixtures)
        self.assertEqual(cases, reference.build_report()["adverse_cases"])
        rejected = [case for case in cases if case["status"] == "rejected"]
        self.assertEqual(len(rejected), 12)
        for case in cases:
            self.assertIs(case["qualifies"], False)
            if case["status"] == "rejected":
                self.assertIs(case["state_unchanged"], True)
                self.assertEqual(case["onset_count"], "0")


class RateProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.read_strict_json(REPORT)
        cls.rate = cls.report["rate_profile"]

    def test_profile_scoring_has_exact_check_ids(self):
        scoring = self.report["profile_scoring"]
        self.assertEqual(tuple(row["id"] for row in scoring["checks"]),
                         EXPECTED_CHECK_IDS)
        self.assertTrue(all(row["passed"] is True for row in scoring["checks"]))
        self.assertEqual(scoring["failed_checks"], [])
        self.assertIs(scoring["passed"], True)

    def test_identity_and_rate_changes(self):
        self.assertEqual(self.rate["identity_1x"],
                         {"stimulus": "music_like_1x", "bpm_x100": "10000"})
        self.assertEqual(self.rate["rate_changes"], [
            {"stimulus": "rate_0_8", "expected_bpm_x100": "8000",
             "observed_bpm_x100": "8000"},
            {"stimulus": "music_like_1x", "expected_bpm_x100": "10000",
             "observed_bpm_x100": "10000"},
            {"stimulus": "rate_1_2", "expected_bpm_x100": "12000",
             "observed_bpm_x100": "12000"}])

    def test_duration_mapping_is_exact(self):
        self.assertEqual(self.rate["duration"]["max_error_samples"], 0)
        for case in self.rate["duration"]["cases"].values():
            self.assertEqual(case["error_samples"], "0")

    def test_source_output_mapping_and_buffering(self):
        mapping = self.rate["source_output_mapping"]
        self.assertIs(mapping["audio_output_produced"], False)
        self.assertIs(mapping["analysis_event_source_anchor"], True)
        self.assertEqual(mapping["frame_hop_samples"], "160")
        self.assertEqual(mapping["available_ns_per_frame"], "10000000")
        self.assertGreaterEqual(mapping["min_availability_margin_ns"], 0)
        buffering = self.rate["playback_buffering"]
        self.assertIs(buffering["device_buffer_measured"], False)
        self.assertEqual(buffering["sdk_worker_count"], "0")
        self.assertEqual(buffering["sdk_queue_depth"], "0")
        self.assertEqual(buffering["final_partial_valid_count"], "137")
        self.assertIs(buffering["final_padding_zero_verified"], True)

    def test_pitch_and_transient_are_not_promoted(self):
        self.assertEqual(self.rate["pitch"]["status"],
                         "not_measurable_analysis_only")
        self.assertIs(self.rate["pitch"]["qualifies"], False)
        self.assertEqual(self.rate["transient_proxy"]["final_partial_error_samples"],
                         -50)

    def test_speech_music_silence_rebuffer_drift_and_partial(self):
        self.assertNotEqual(self.rate["speech_unfamiliar"]["status"], "stable")
        self.assertIs(self.rate["speech_unfamiliar"]["qualifies"], False)
        self.assertEqual(self.rate["music"]["status"], "stable")
        self.assertEqual(self.rate["silence"]["status"], "no_onsets")
        self.assertIs(self.rate["rebuffer"]["cross_gap_ioi_suppressed"], True)
        self.assertEqual(self.rate["rebuffer"]["excluded_ioi_count"], "1")
        self.assertIs(self.rate["drift"]["monotonic_ioi_decrease"], True)
        final = self.rate["final_partial_window"]
        self.assertEqual(final["valid_count"], "137")
        self.assertEqual(final["event_source_end"], "64137")
        self.assertIs(final["event_beyond_source_end"], False)
        self.assertIs(self.rate["low_snr_adverse"]["qualifies"], False)

    def test_acceptance_profile_matches_pinned_source(self):
        expected = reference.SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"]
        self.assertEqual(reference.sha256_file(VERIFICATION), expected)
        rate_rows = [line for line in VERIFICATION.read_text(encoding="utf-8").splitlines()
                     if line.startswith("| Rate |")]
        self.assertEqual(len(rate_rows), 1)
        for phrase in PROFILE_PHRASES:
            self.assertIn(phrase, rate_rows[0])
        acceptance = self.report["acceptance_profile"]
        self.assertEqual(acceptance["profile"], "Rate")
        for key in ("source_output_mapping", "duration", "pitch", "transient",
                    "playback_buffering", "rate_1x", "rate_changes",
                    "unfamiliar_speech", "music", "silence", "rebuffer",
                    "drift", "final_partial_window"):
            self.assertTrue(acceptance[key], key)

    def test_disposition_and_gates(self):
        decision = self.report["decision"]
        self.assertEqual(decision["status"], "incomplete")
        self.assertEqual(decision["promotion"], "defer")
        self.assertEqual(decision["production_exposure"], "DEFER")
        for key in ("expose_as_processor", "registered", "default_enabled"):
            self.assertIs(decision[key], False)
        qualification = self.report["qualification"]
        self.assertIs(qualification["synthetic_profile_checks_passed"], True)
        self.assertIs(qualification["all_release_gates_blocked"], True)
        for key in ("release_results_present", "missing_result_promoted",
                    "real_source_or_runtime_used", "listening_or_device_timing_claim"):
            self.assertIs(qualification[key], False)
        self.assertEqual(len(self.report["blockers"]), 7)
        for blocker in self.report["blockers"]:
            self.assertEqual(blocker["status"], "blocked")
            self.assertIs(blocker["qualifies"], False)


class DeterminismAndPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bytes = REPORT.read_bytes()
        cls.manifest = PINS.read_bytes()
        cls.sidecar = SIDECAR.read_bytes()

    def test_report_is_canonical_and_sidecar_matches(self):
        report = reference.read_strict_json(REPORT)
        text, digest = reference.canonical_report(report)
        self.assertEqual(self.bytes, text.encode("utf-8"))
        self.assertEqual(self.sidecar, f"{digest}  report.json\n".encode("ascii"))
        self.assertEqual(hashlib.sha256(self.bytes).hexdigest(), digest)

    def test_in_process_three_rebuilds_are_byte_identical(self):
        payloads = []
        for _ in range(3):
            text, _ = reference.canonical_report(reference.build_report())
            payloads.append(text.encode("utf-8"))
        self.assertEqual(len(set(payloads)), 1)
        self.assertEqual(payloads[0], self.bytes)

    def test_cold_start_three_rebuilds_are_byte_identical(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
        observed = []
        with tempfile.TemporaryDirectory(prefix="sdk-aubio-test-") as temporary:
            root = Path(temporary)
            for index in range(1, 4):
                target = prepare_scratch(root, index)
                process = subprocess.run([sys.executable, "run.py", "all"], cwd=target,
                                         capture_output=True, text=True, env=env)
                self.assertEqual(process.returncode, 0, process.stderr)
                observed.append(((target / "report.json").read_bytes(),
                                 (target / "report.json.sha256").read_bytes(),
                                 (target / "SOURCES.sha256").read_bytes()))
        self.assertEqual(len(set(observed)), 1)
        self.assertEqual(observed[0], (self.bytes, self.sidecar, self.manifest))

    def test_manifest_is_complete_and_deterministic(self):
        self.assertEqual(self.manifest, run.sources_bytes())
        lines = [line for line in self.manifest.decode("ascii").splitlines()
                 if line and not line.startswith("#")]
        names = {line.split("  ", 1)[1] for line in lines}
        expected = {run.TASK_PREFIX + name for name in run.LOCAL_PIN_FILES}
        for relative in reference.SOURCE_PINS:
            expected.add("source:" + relative)
        expected.update(reference.BOUNDARY_PINS)
        self.assertEqual(names, expected)
        self.assertEqual(len(lines), len(expected))

    def test_licensing_sidecars_and_python_headers(self):
        # REUSE-IgnoreStart
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head, path.name)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head, path.name)
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "fixtures.json.license", "report.json.license",
                     "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("SPDX-License-Identifier: Apache-2.0", text, name)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes", text, name)
        # REUSE-IgnoreEnd

    def test_scope_is_task_local(self):
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
             "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(run.TASK_PREFIX), path)


if __name__ == "__main__":
    unittest.main()
