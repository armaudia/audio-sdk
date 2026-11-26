# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local deterministic tests for the librosa beat/tempo evidence package.

The suite is standard-library only, uses no network, no real audio and no
librosa runtime, and includes the three merge-base scope regression tests.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

MATRIX = reference._case_matrix()
REPORT = reference.build_report()
CONTRACT = reference.build_contract()


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text(b'{"a":1,"a":2}')

    def test_nonfinite_rejected(self) -> None:
        for token in (b'{"a":NaN}', b'{"a":Infinity}',
                      b'{"a":-Infinity}'):
            with self.assertRaises(ValueError):
                reference.parse_strict_json_text(token)

    def test_malformed_and_nonobject_rejected(self) -> None:
        for token in (b"{", b"[]", b"null", b"1"):
            with self.assertRaises(ValueError):
                reference.parse_strict_json_text(token)

    def test_float_rejected_and_canonical_roundtrip(self) -> None:
        with self.assertRaises(ValueError):
            reference.assert_no_float({"value": 1.0})
        text = reference.canonical_text({"b": 1, "a": [True, None]})
        self.assertEqual(text, '{"a":[true,null],"b":1}')
        self.assertEqual(reference.parse_strict_json_text(text.encode()),
                         {"a": [True, None], "b": 1})


class PinTests(unittest.TestCase):
    def test_source_and_boundary_pins_match_live_bytes(self) -> None:
        for relative, digest in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)

    def test_sources_manifest_matches_generated_bytes(self) -> None:
        path = HERE / "SOURCES.sha256"
        self.assertEqual(path.read_bytes(), reference.sources_bytes())

    def test_pin_manifest_has_no_mutable_board_and_known_prefixes(self) -> None:
        rows = reference.parse_pin_lines(
            (HERE / "SOURCES.sha256").read_text(encoding="ascii"))
        self.assertTrue(rows)
        for _, path in rows:
            self.assertNotIn("TASKS.json", path)
            self.assertTrue(path.startswith(("source:", "sdk:",
                                             reference.TASK_PREFIX)))


class FixtureTests(unittest.TestCase):
    def test_stimulus_set_is_exact(self) -> None:
        self.assertEqual(len(reference.STIMULI), 10)
        self.assertEqual(
            [item["name"] for item in reference.STIMULI],
            ["steady_music_1x", "rate_0_8", "rate_1_2", "tempo_step",
             "syncopated_offbeat", "speech_like_unfamiliar", "rebuffer_gap",
             "drift_decreasing", "silence", "final_partial"])

    def test_signal_length_equals_valid_samples(self) -> None:
        for stimulus in reference.STIMULI:
            signal = reference._build_signal(stimulus)
            self.assertEqual(len(signal), stimulus["valid_samples"])

    def test_final_partial_has_137_samples_and_offset_click(self) -> None:
        stimulus = reference.STIMULUS_BY_NAME["final_partial"]
        self.assertEqual(stimulus["valid_samples"], 300 * 160 + 137)
        self.assertEqual(stimulus["beats"][-1], (300, 1000, 10))

    def test_silence_is_all_zero(self) -> None:
        stimulus = reference.STIMULUS_BY_NAME["silence"]
        self.assertTrue(all(sample == 0 for sample in
                            reference._build_signal(stimulus)))


class TempoTests(unittest.TestCase):
    def test_expected_tempo_status_and_bpm(self) -> None:
        expected = {
            "steady_music_1x": ("stable", 10000),
            "rate_0_8": ("stable", 8000),
            "rate_1_2": ("stable", 12000),
            "syncopated_offbeat": ("stable", 12000),
            "speech_like_unfamiliar": ("unstable", None),
            "rebuffer_gap": ("stable", 12000),
            "drift_decreasing": ("unstable", None),
            "silence": ("no_onsets", None),
            "final_partial": ("stable", 10000),
        }
        for name, (status, bpm) in expected.items():
            tempo = MATRIX[name]["tempo"]
            self.assertEqual(tempo["status"], status, name)
            self.assertEqual(tempo["bpm_x100"], bpm, name)

    def test_tempo_step_is_unstable_locally_exact(self) -> None:
        step = REPORT["tempo_tracking"]["tempo_step"]
        self.assertEqual(step["observed_segments"], [10000, 15000])
        self.assertTrue(step["exact"])
        self.assertEqual(step["global_status"], "unstable")
        self.assertIsNone(step["global_bpm_x100"])

    def test_rebuffer_excludes_one_cross_gap_interval(self) -> None:
        tempo = MATRIX["rebuffer_gap"]["tempo"]
        self.assertEqual(tempo["excluded_ioi_count"], 1)
        self.assertEqual(tempo["bpm_x100"], 12000)

    def test_drift_is_monotonic_without_global_bpm(self) -> None:
        self.assertTrue(REPORT["rate_profile"]["drift"]
                        ["monotonic_decreasing"])
        self.assertIsNone(REPORT["rate_profile"]["drift"]["bpm_x100"])


class BeatMeterTests(unittest.TestCase):
    def test_all_non_silence_beats_are_exact(self) -> None:
        for name, case in MATRIX.items():
            match = case["match"]
            if name == "silence":
                self.assertEqual(match["detected"], 0)
                continue
            self.assertEqual(match["false_positives"], 0, name)
            self.assertEqual(match["false_negatives"], 0, name)
            self.assertEqual(match["f1_x1000"], 1000, name)

    def test_silence_has_no_beats(self) -> None:
        self.assertEqual(MATRIX["silence"]["match"]["detected"], 0)
        self.assertEqual(MATRIX["silence"]["match"]["f1_x1000"], 1000)

    def test_meter_is_4_for_the_three_4_4_music_cases(self) -> None:
        for name in ("steady_music_1x", "rate_0_8", "rate_1_2"):
            meter = MATRIX[name]["meter"]
            self.assertEqual(meter["status"], "stable", name)
            self.assertEqual(meter["meter"], 4, name)
            self.assertTrue(meter["correct"], name)

    def test_syncopated_meter_is_ambiguous_and_labels_absent(self) -> None:
        self.assertEqual(MATRIX["syncopated_offbeat"]["meter"]["status"],
                         "ambiguous")
        self.assertIsNone(MATRIX["syncopated_offbeat"]["meter"]["meter"])
        self.assertFalse(REPORT["downbeat_meter"]["truth_available"])


class RateProfileTests(unittest.TestCase):
    def test_identity_and_exact_duration_mapping(self) -> None:
        self.assertEqual(REPORT["rate_profile"]["identity_1x"]["bpm_x100"],
                         10000)
        self.assertEqual(REPORT["rate_profile"]["identity_1x"]
                         ["detected_beats"], 10)
        self.assertEqual(REPORT["rate_profile"]["duration"]
                         ["max_error_samples"], 0)
        self.assertTrue(REPORT["rate_profile"]["duration"]["exact"])

    def test_rate_change_rows_match_expected_bpm(self) -> None:
        for row in REPORT["rate_profile"]["rate_changes"]:
            self.assertEqual(row["observed_bpm_x100"],
                             row["expected_bpm_x100"])
            self.assertTrue(row["exact"])

    def test_final_partial_error_is_minus_ten_samples(self) -> None:
        final = REPORT["rate_profile"]["final_partial"]
        self.assertEqual(final["valid_count"], 137)
        self.assertTrue(final["padding_zero"])
        self.assertEqual(final["error_samples"], -10)
        self.assertEqual(REPORT["rate_profile"]["transient_proxy"]
                         ["final_partial_error_samples"], -10)

    def test_blocked_and_synthetic_items_never_qualify(self) -> None:
        self.assertFalse(REPORT["rate_profile"]["pitch"]["qualifies"])
        self.assertFalse(REPORT["rate_profile"]["speech_unfamiliar"]
                         ["qualifies"])
        self.assertIsNone(REPORT["rate_profile"]["speech_unfamiliar"]
                          ["bpm_x100"])
        self.assertEqual(REPORT["rate_profile"]["silence"]["status"],
                         "no_onsets")
        self.assertFalse(REPORT["rate_profile"]["playback_buffering"]
                         ["device_buffer_measured"])
        self.assertFalse(REPORT["rate_profile"]["source_output_mapping"]
                         ["audio_output_produced"])


class StreamingResetTests(unittest.TestCase):
    def test_chunk_schedules_match_offline(self) -> None:
        streaming = REPORT["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertEqual(streaming["chunk_schedules"],
                         [160, 480, 800, 137, 641])
        self.assertEqual(streaming["accepted_samples"], 48137)
        self.assertFalse(streaming["scheduler_measured"])

    def test_reset_matches_fresh_and_rejects_nonpositive_epochs(self) -> None:
        reset = REPORT["reset"]
        self.assertTrue(reset["matches_fresh"])
        self.assertEqual([row["epoch"] for row in reset["rejected_epochs"]],
                         [0, -1])

    def test_every_chunk_match_is_true(self) -> None:
        self.assertTrue(all(REPORT["streaming"]["matches"].values()))


class AdverseTests(unittest.TestCase):
    def test_exactly_forty_adverse_cases_are_rejected(self) -> None:
        adverse = REPORT["adverse_rejections"]
        self.assertEqual(len(adverse), 40)
        self.assertTrue(REPORT["adverse_all_rejected"])
        for item in adverse:
            self.assertEqual(item["status"], "rejected")
            self.assertTrue(item["state_unchanged"])

    def test_required_adverse_case_ids_are_present(self) -> None:
        ids = {item["case_id"] for item in REPORT["adverse_rejections"]}
        for case_id in ("duplicate_json_key", "nan_constant",
                        "sample_rate_22050", "stereo", "nonzero_padding",
                        "misaligned_final_partial", "length_mismatch",
                        "bad_manifest_hash"):
            self.assertIn(case_id, ids)

    def test_base_request_and_manifest_validate(self) -> None:
        request = reference.base_request()
        self.assertIs(reference.validate_request(request), request)
        manifest = reference.base_manifest()
        self.assertIs(reference.validate_manifest(manifest), manifest)

    def test_manifest_identity_only_rejects_unsafe_values(self) -> None:
        for key, value in (("tool", "other"), ("python", "3.12.14"),
                           ("wheel_sha256", "main"),
                           ("sample_rate_hz", 22050),
                           ("channels", 2), ("hop_length", 512),
                           ("byte_count", 0)):
            manifest = reference.base_manifest()
            manifest[key] = value
            with self.assertRaises(ValueError):
                reference.validate_manifest(manifest)


class ReportContractTests(unittest.TestCase):
    def test_report_is_canonical_and_sidecar_matches(self) -> None:
        expected, digest = reference.canonical_report(REPORT)
        self.assertEqual((HERE / "report.json").read_bytes(),
                         expected.encode("ascii"))
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")

    def test_contract_is_canonical(self) -> None:
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         reference.canonical_bytes(CONTRACT))

    def test_defer_incomplete_not_qualified(self) -> None:
        self.assertEqual(REPORT["decision"], "DEFER")
        self.assertEqual(REPORT["status"], "proposal_only_incomplete")
        self.assertEqual(REPORT["evidence_status"], "incomplete")
        self.assertEqual(REPORT["qualification_status"], "not_qualified")
        self.assertFalse(REPORT["qualification"]["qualifies"])
        self.assertEqual(CONTRACT["decision"], "DEFER")
        self.assertEqual(CONTRACT["qualification_status"],
                         "not_qualified")

    def test_eight_gates_six_blockers_all_blocked(self) -> None:
        self.assertEqual([gate["id"] for gate in REPORT["release_gates"]],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in REPORT["release_gates"]))
        self.assertEqual([blocker["id"] for blocker in
                          REPORT["exact_blockers"]],
                         [f"BLK-{index:02d}" for index in range(1, 7)])

    def test_boundary_and_scope_claim_no_change(self) -> None:
        for value in REPORT["boundary"].values():
            self.assertFalse(value)
        scope = REPORT["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertFalse(value, key)
        self.assertNotIn('"qualifies":true', reference.canonical_text(REPORT))
        self.assertNotIn("TASKS.json", reference.canonical_text(
            REPORT["source_pins"]))

    def test_candidate_runtime_and_librosa_output_are_absent(self) -> None:
        self.assertFalse(REPORT["candidate"]["runtime_present"])
        self.assertFalse(REPORT["candidate"]["source_present"])
        self.assertFalse(REPORT["reference"]["exact_librosa_executed"])
        self.assertFalse(REPORT["reference"]["implementation_present"])
        self.assertTrue(REPORT["reference"]["surrogate_present"])
        self.assertFalse(REPORT["caller_tool_reference"]["admitted"])
        self.assertFalse(REPORT["caller_tool_reference"]["reproduced"])
        self.assertFalse(REPORT["environment"]["librosa_present"])


class ReadmeDigestTests(unittest.TestCase):
    def test_readme_digest_tables_validate(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertGreater(counts["artifacts"], 0)

    def test_stale_digest_is_rejected(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        key = next(iter(reference.SOURCE_PINS))
        digest = reference.SOURCE_PINS[key]
        stale = text.replace(f"| `source:{key}` | `{digest}` |",
                             f"| `source:{key}` | `{'0' * 64}` |", 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(stale)

    def test_malformed_digest_is_rejected(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        key = next(iter(reference.SOURCE_PINS))
        digest = reference.SOURCE_PINS[key]
        malformed = text.replace(f"| `source:{key}` | `{digest}` |",
                                 f"| `source:{key}` | `short` |", 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(malformed)


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
            historic = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          historic)
            self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-LIBROSA-BEAT-TRACK-TEMPO-scope")
            (repo / "CMakeLists.txt").write_text("changed\n",
                                                 encoding="utf-8")
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
    def test_expected_files_exactly(self) -> None:
        actual = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertEqual(actual, reference.EXPECTED_DIR_FILES)
        self.assertEqual([path.name for path in HERE.iterdir()
                          if path.is_dir()], [])
        self.assertFalse(any(HERE.rglob("__pycache__")))
        self.assertFalse(any(HERE.rglob("*.pyc")))

    def test_no_forbidden_artifacts_or_symlinks(self) -> None:
        for path in HERE.iterdir():
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertNotIn(path.name, {"provider.json", "adapter.json",
                                         "asset.json", "LICENSE",
                                         "LICENSE.txt", "COPYING",
                                         "NOTICE"})

    def test_readme_states_the_decision_and_pins(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for token in ("DEFER", "incomplete", "not_qualified", "RG-01",
                      "RG-08", "not librosa", "ISC", "3.12.16",
                      "scope_base_unavailable", "base_out_of_scope_change",
                      reference.BASE_COMMIT):
            self.assertIn(token, text)

    def test_license_sidecars_exist(self) -> None:
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            content = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("SPDX" "-License-Identifier: Apache-2.0", content)
            self.assertIn("SPDX" "-FileCopyrightText: 2026 Tsakanyan "
                          "Hovhannes", content)


if __name__ == "__main__":
    unittest.main()
