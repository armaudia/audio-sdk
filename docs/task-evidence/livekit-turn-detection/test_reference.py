# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for the task-local LiveKit turn-detection evidence package."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import reference

HERE = reference.HERE
LOCAL_PINS = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_text_is_sorted_and_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": 2}),
                         '{"a":2,"b":1}')

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.InvalidInput):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nonfinite_constant_rejected(self) -> None:
        with self.assertRaises(reference.InvalidInput):
            reference.loads_strict('{"a":NaN}')

    def test_float_value_rejected(self) -> None:
        with self.assertRaises(reference.InvalidInput):
            reference.assert_no_float({"a": 1.5})

    def test_fraction_text(self) -> None:
        from fractions import Fraction
        self.assertEqual(reference.fraction_text(Fraction(4, 2)), "2")
        self.assertEqual(reference.fraction_text(Fraction(1, 3)), "1/3")


class FixtureTests(unittest.TestCase):
    def test_segments_partition_the_clip_exactly(self) -> None:
        cursor = 0
        for start, end, _, _ in reference.SEGMENTS:
            self.assertEqual(start, cursor)
            self.assertLess(start, end)
            cursor = end
        self.assertEqual(cursor, reference.TOTAL_FRAMES)

    def test_turn_regions_cover_all_known_frames(self) -> None:
        covered = []
        for turn in reference.TURNS:
            covered.extend(range(turn["start"], turn["region_end"]))
        self.assertEqual(covered, list(range(0, 660)))

    def test_unknown_stratum_is_excluded(self) -> None:
        for frame in range(660, 700):
            self.assertEqual(reference.stratum_of(frame), "unknown")
            self.assertIsNone(reference.vad_state(frame))
            self.assertIsNone(reference.probability_permille(frame))
            self.assertIsNone(reference.truth_complete(frame))

    def test_every_known_frame_has_state_and_probability(self) -> None:
        for frame in range(660):
            self.assertIn(reference.vad_state(frame), ("speech", "nonspeech"))
            value = reference.probability_permille(frame)
            self.assertIsInstance(value, int)
            self.assertTrue(0 <= value <= 1000)

    def test_probability_is_deterministic(self) -> None:
        first = [reference.probability_permille(frame) for frame in range(700)]
        second = [reference.probability_permille(frame) for frame in range(700)]
        self.assertEqual(first, second)

    def test_framewise_counts_are_exact(self) -> None:
        metrics = reference.framewise_metrics()
        self.assertEqual(metrics["tp_samples"], 14400)
        self.assertEqual(metrics["fn_samples"], 3200)
        self.assertEqual(metrics["fp_samples"], 3200)
        self.assertEqual(metrics["tn_samples"], 84800)
        self.assertEqual(metrics["unknown_samples"], 6400)
        self.assertEqual(metrics["speech_miss_rate"], "2/11")
        self.assertEqual(metrics["false_alarm_rate"], "2/55")

    def test_quiet_speech_is_a_false_negative(self) -> None:
        metrics = reference.framewise_metrics()
        self.assertEqual(metrics["per_stratum"]["quiet-speech"],
                         {"speech_samples": 0, "nonspeech_samples": 3200,
                          "unknown_samples": 0})

    def test_false_positives_are_stratified(self) -> None:
        metrics = reference.framewise_metrics()
        self.assertEqual(
            metrics["per_stratum"]["mid-turn-pause"]["speech_samples"], 1600)
        self.assertEqual(
            metrics["per_stratum"]["idle-noise"]["speech_samples"], 1600)

    def test_brier_is_exact(self) -> None:
        brier = reference.brier_control()
        self.assertEqual(brier["scored_frames"], 660)
        self.assertEqual(brier["scaled_permille_squared_brier"], "3/200")
        self.assertEqual(brier["brier_numerator"], 9900000)
        self.assertEqual(brier["brier_denominator"], 660000000)

    def test_cross_hop_projection_conserves_samples(self) -> None:
        rows = reference.cross_hop_project(120, 420)
        self.assertEqual([row["overlap_samples"] for row in rows], [40, 160, 100])
        self.assertEqual(sum(row["overlap_samples"] for row in rows), 300)

    def test_cross_hop_rejects_invalid_spans(self) -> None:
        for start, end in ((-1, 10), (10, 10), (10, 5),
                           (0, reference.TOTAL_SAMPLES + 1)):
            with self.assertRaises(reference.InvalidInput):
                reference.cross_hop_project(start, end)


class PolicyTests(unittest.TestCase):
    def test_vad_only_decisions_are_exact(self) -> None:
        metrics = reference.policy_metrics("vad_only")
        frames = [item["decision_frame"] for item in metrics["decisions"]]
        delays = [item["delay_samples"] for item in metrics["decisions"]]
        self.assertEqual(frames, [69, 189, 319, 369])
        self.assertEqual(delays, [-1600, -3200, 8000, -43200])
        self.assertEqual(metrics["cutoff_count"], 3)
        self.assertEqual(metrics["worst_cutoff_samples"], -43200)
        self.assertEqual(metrics["mean_end_of_turn_delay_samples"], "-10000")
        self.assertEqual(
            metrics["mean_absolute_end_of_turn_delay_samples"], "14000")

    def test_gated_decisions_are_exact(self) -> None:
        metrics = reference.policy_metrics("gated")
        frames = [item["decision_frame"] for item in metrics["decisions"]]
        delays = [item["delay_samples"] for item in metrics["decisions"]]
        self.assertEqual(frames, [80, 239, 319, 589])
        self.assertEqual(delays, [160, 4800, 8000, -8000])
        self.assertEqual(metrics["cutoff_count"], 1)
        self.assertEqual(metrics["max_wait_forced_count"], 1)
        self.assertEqual(metrics["worst_cutoff_samples"], -8000)

    def test_gated_max_wait_is_a_deliberate_cutoff(self) -> None:
        last = reference.policy_metrics("gated")["decisions"][-1]
        self.assertTrue(last["cutoff"])
        self.assertEqual(last["cutoff_cause"], "max_wait_forced")
        self.assertEqual(last["silence_frames"], reference.MAX_DELAY_FRAMES)

    def test_endpoint_decisions_are_separate_from_activity(self) -> None:
        gated = reference.event_stream("gated", 1)
        vad = reference.event_stream("vad_only", 2)
        self.assertEqual(gated["activity_events"], 660)
        self.assertEqual(gated["endpoint_events"], 4)
        self.assertEqual(vad["endpoint_events"], 4)
        self.assertNotEqual(gated["digest"], vad["digest"])

    def test_policy_delta_is_exact(self) -> None:
        delta = reference._policy_delta()
        self.assertEqual(delta["cutoff_count_reduction"], 2)
        self.assertEqual(delta["worst_cutoff_improvement_samples"], 35200)
        self.assertEqual(
            delta["mean_absolute_delay_improvement_samples"], "8760")

    def test_unknown_policy_mode_rejected(self) -> None:
        with self.assertRaises(reference.InvalidInput):
            reference.policy_metrics("oracle")


class SessionTests(unittest.TestCase):
    def _event(self, **overrides: object) -> dict:
        event = reference.activity_event(1, 0, 0, "session-a")
        event.update(overrides)
        return event

    def test_valid_event_is_accepted(self) -> None:
        session = reference.PolicySession("session-a", 1)
        self.assertEqual(session.ingest(self._event()), ("accepted", None))

    def test_unknown_validity_is_audited_not_scored(self) -> None:
        session = reference.PolicySession("session-a", 1)
        event = self._event(validity="unknown")
        self.assertEqual(session.ingest(event),
                         ("audit_unknown", None))
        self.assertEqual(session.known, [])
        self.assertEqual(len(session.unknown), 1)

    def test_invalid_validity_token_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        status, reason = session.ingest(self._event(validity="maybe"))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "validity_token_invalid")

    def test_duplicate_sequence_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        self.assertEqual(session.ingest(self._event())[0], "accepted")
        status, reason = session.ingest(self._event(sequence=0))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "duplicate_or_stale_sequence")

    def test_stale_epoch_rejected(self) -> None:
        session = reference.PolicySession("session-a", 2)
        status, reason = session.ingest(self._event(epoch=1))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "stale_or_wrong_epoch")

    def test_wrong_clock_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        status, reason = session.ingest(self._event(clock="other"))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "wrong_clock")

    def test_wrong_interval_width_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        status, reason = session.ingest(self._event(end_sample=161))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "wrong_interval_width")

    def test_nonfinite_and_out_of_range_probability_rejected(self) -> None:
        for value in (1001, -1, "500", 500.0, True):
            session = reference.PolicySession("session-a", 1)
            status, reason = session.ingest(
                self._event(probability_permille=value))
            self.assertEqual(status, "rejected", value)
            self.assertIn(reason,
                          ("probability_integer_required",
                           "probability_out_of_range"), value)

    def test_stale_availability_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        self.assertEqual(session.ingest(self._event())[0], "accepted")
        status, reason = session.ingest(self._event(
            sequence=1, start_sample=160, end_sample=320, available_ns=1))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "stale_availability")

    def test_missing_key_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        event = self._event()
        event.pop("decision")
        status, reason = session.ingest(event)
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "event_key_set_invalid")

    def test_activity_commit_decision_rejected(self) -> None:
        session = reference.PolicySession("session-a", 1)
        status, reason = session.ingest(self._event(decision="commit"))
        self.assertEqual(status, "rejected")
        self.assertEqual(reason, "activity_decision_invalid")

    def test_bad_configs_rejected(self) -> None:
        base = {
            "session_id": "s", "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
            "real_runtime": False,
        }
        variants = (
            dict(base, sample_rate_hz=48000),
            dict(base, channels=2),
            dict(base, sample_format="s16"),
            dict(base, frame_samples=320),
            dict(base, real_runtime=True),
            dict(base, session_id=""),
        )
        for config in variants:
            with self.assertRaises(reference.InvalidInput):
                reference.validate_session_config(config)

    def test_reset_clears_state_and_changes_digest(self) -> None:
        session = reference.PolicySession("session-a", 1)
        session.ingest(self._event())
        before = session.digest()
        session.reset(9)
        after = session.digest()
        self.assertNotEqual(before, after)
        self.assertEqual(session.epoch, 9)
        self.assertEqual(session.known, [])
        fresh = reference.PolicySession("session-a", 9)
        self.assertEqual(after, fresh.digest())

    def test_independent_sessions_have_distinct_digests(self) -> None:
        first = reference.event_stream("gated", 1)
        second = reference.event_stream("gated", 2)
        self.assertNotEqual(first["digest"], second["digest"])

    def test_endpoint_interval_is_bounded(self) -> None:
        session = reference.PolicySession("session-a", 1)
        decision = reference.policy_decisions("gated")[0]
        event = reference.endpoint_event(decision, 1, 0, "session-a")
        self.assertLess(event["start_sample"], event["end_sample"])
        self.assertEqual(session.ingest(event), ("accepted", None))


class AssetContractTests(unittest.TestCase):
    def test_positive_fixture_is_accepted(self) -> None:
        self.assertEqual(
            reference.validate_asset_manifest(
                reference.positive_asset_fixture()), (True, None))

    def test_all_adverse_cases_are_rejected(self) -> None:
        cases = reference.adverse_asset_cases()
        self.assertEqual(len(cases), len(reference.ADVERSE_ASSET_CASE_IDS))
        self.assertTrue(all(not case["accepted"] for case in cases))

    def test_absent_asset_is_rejected_before_processing(self) -> None:
        self.assertEqual(reference.validate_asset_manifest(None),
                         (False, "asset_manifest_absent"))

    def test_vendored_asset_is_rejected(self) -> None:
        manifest = reference.positive_asset_fixture()
        manifest["vendored_in_package"] = True
        self.assertEqual(reference.validate_asset_manifest(manifest),
                         (False, "asset_vendored"))

    def test_redistribution_is_rejected(self) -> None:
        manifest = reference.positive_asset_fixture()
        manifest["redistribution_permitted"] = True
        self.assertEqual(
            reference.validate_asset_manifest(manifest),
            (False, "asset_redistribution_not_permitted"))

    def test_wrong_geometry_is_rejected(self) -> None:
        manifest = reference.positive_asset_fixture()
        manifest["frame_samples"] = 256
        self.assertEqual(
            reference.validate_asset_manifest(manifest),
            (False, "asset_frame_samples_invalid"))

    def test_absence_probes_are_all_absent(self) -> None:
        probes = reference.absence_probes()
        summary = reference.absence_summary(probes)
        self.assertEqual(summary["probe_count"],
                         len(reference.ABSENCE_PROBE_PATHS))
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = reference.build_report()
        self.contract = reference.build_contract()

    def test_report_disposition_is_defer(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")

    def test_contract_disposition_is_defer(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")

    def test_no_candidate_metrics(self) -> None:
        self.assertIsNone(self.report["candidate_metrics"])

    def test_geometry_is_unestablished(self) -> None:
        geometry = self.report["geometry"]
        self.assertEqual(geometry["model_geometry_status"], "unestablished")
        self.assertIsNone(geometry["sample_rate_hz"])
        self.assertIsNone(geometry["hop_samples"])
        self.assertIsNone(geometry["latency_samples"])
        self.assertFalse(geometry["policy_defaults_measured"])

    def test_all_gates_and_blockers_are_open(self) -> None:
        self.assertEqual([gate["id"] for gate in self.report["gates"]],
                         list(reference.GATE_IDS))
        self.assertTrue(all(gate["blocked"]
                            for gate in self.report["gates"]))
        self.assertEqual(
            [item["id"] for item in self.report["exact_blockers"]],
            list(reference.BLOCKER_IDS))
        self.assertTrue(all(item["state"] == "open"
                            for item in self.report["exact_blockers"]))

    def test_analysis_profile_is_not_satisfied(self) -> None:
        profile = self.report["analysis_profile"]
        self.assertEqual(profile["profile"], "analysis")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertEqual(len(profile["required_items"]),
                         len(reference.ANALYSIS_REQUIREMENTS))
        self.assertTrue(all(item["satisfied_for_qualification"] is False
                            and item["qualification_effect"] == "none"
                            for item in profile["required_items"]))

    def test_boundary_and_scope_flags_are_closed(self) -> None:
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        for key, value in self.report["scope"].items():
            if key in ("task_local_only", "synthetic_only"):
                self.assertIs(value, True, key)
            else:
                self.assertIs(value, False, key)

    def test_caller_asset_contract_is_fail_closed(self) -> None:
        contract = self.report["caller_asset_contract"]
        self.assertEqual(contract["absent_behavior"],
                         "reject_before_processing")
        self.assertTrue(contract["asset_sha256_required"])
        self.assertFalse(contract["asset_is_vendored"])
        self.assertIsNone(contract["required_source_revision"])
        self.assertFalse(contract["revision_pin_available"])
        self.assertTrue(contract["positive_fixture_accepted"])
        self.assertTrue(contract["all_probes_rejected"])

    def test_synthetic_policy_control_separates_streams(self) -> None:
        control = self.report["synthetic_policy_control"]
        self.assertEqual(control["event_streams"]["gated"]["endpoint_events"], 4)
        self.assertEqual(
            control["event_streams"]["gated"]["activity_events"], 660)
        self.assertTrue(control["adverse_controls"]["all_rejected"])
        self.assertTrue(
            control["adverse_controls"]["unknown_never_scored"])

    def test_no_float_in_report_or_contract(self) -> None:
        reference.assert_no_float(self.report)
        reference.assert_no_float(self.contract)

    def test_canonical_report_is_stable(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)

    def test_task_identity_matches_board(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(self.report["task_row_identity"]["stable_sha256"],
                         projection["stable_sha256"])
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_values_are_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertTrue(context["not_reproduced"])
        self.assertTrue(context["facts"])


class ReadmeTests(unittest.TestCase):
    def test_actual_readme_digest_tables_verify(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))

    def test_artifact_table_is_deterministic(self) -> None:
        first = reference.render_artifact_table()
        second = reference.render_artifact_table()
        self.assertEqual(first, second)
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn(first, text)

    def test_malformed_artifact_row_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables(
                "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
                "| `a` | `" + "0" * 64 + "` |\n"
                "<!-- DIGEST_TABLE_ARTIFACTS_END -->")

    def test_changed_digest_rejected(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        name = "reference.py"
        digest = reference.sha256_file(HERE / name)
        tampered = text.replace(f"| `{name}` | `{digest}` |",
                                f"| `{name}` | `{'0' * 64}` |")
        self.assertNotEqual(tampered, text)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(tampered)


class ScopeTests(unittest.TestCase):
    """Regression coverage for the merge-base scope comparison."""

    def _git(self, repo: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *arguments],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def _repository(self, root: Path) -> Path:
        repo = root / "audio-sdk"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-fixture")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("task package\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "task package")
        return repo

    def _add_siblings(self, repo: Path) -> None:
        # Later main merges land unrelated task packages beside this one.
        for name in ("sibling-alpha", "sibling-beta"):
            sibling = repo / "docs/task-evidence" / name
            sibling.mkdir(parents=True)
            (sibling / "report.json").write_text("{}\n", encoding="utf-8")
            (sibling / "verify.py").write_text("# sibling\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "unrelated sibling packages")

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")

            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            self.assertEqual(reference.scope_violations([]), [])

            # The old fixed base would have reported the siblings; the
            # merge-base comparison must not.
            historic = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          historic)
            self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-LIVEKIT-TURN-DETECTION-correction")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "out of scope edit")

            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))


class PackageBoundaryTests(unittest.TestCase):
    def test_local_pins_exist(self) -> None:
        for name in LOCAL_PINS:
            self.assertTrue((HERE / name).is_file(), name)

    def test_pin_manifest_covers_allowed_keys(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        rows = reference.parse_pin_lines(text)
        paths = {path for _, path in rows}
        self.assertEqual(paths, reference.allowed_pin_keys())
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)

    def test_no_forbidden_binary_or_asset_files(self) -> None:
        forbidden = {".onnx", ".pt", ".pth", ".bin", ".wav", ".flac", ".mp3",
                     ".so", ".dylib", ".dll", ".exe", ".model", ".safetensors"}
        for path in HERE.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden, path.name)

    def test_python_files_have_spdx_header(self) -> None:
        license_tag = "SPDX-License-" + "Identifier: Apache-2.0"
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn("SPDX-FileCopyrightText", head, path.name)
            self.assertIn(license_tag, head, path.name)

    def test_report_and_contract_are_strict_json(self) -> None:
        reference.read_strict_json(HERE / "report.json")
        reference.read_strict_json(HERE / "contract.json")

    def test_report_sidecar_matches(self) -> None:
        raw = (HERE / "report.json").read_bytes()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, reference.sha256_bytes(raw) + "  report.json\n")


if __name__ == "__main__":
    unittest.main()
