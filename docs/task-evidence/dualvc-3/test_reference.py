# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-DUALVC-3 blocker evidence package."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import reference


def valid_request() -> dict:
    return {
        "candidate": "dualvc-3",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "target_condition": "streaming_generic_target_unspecified",
    }


class StrictJsonTests(unittest.TestCase):
    def test_valid_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)

    def test_trailing_and_syntax_rejected(self) -> None:
        for text in ('{"a":1} extra', '{"a":}', ""):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        validated = reference.validate_request(valid_request())
        self.assertEqual(validated["candidate"], "dualvc-3")
        self.assertEqual(validated["target_condition"],
                         "streaming_generic_target_unspecified")
        self.assertEqual(len(validated["samples"]), 160)

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = valid_request()
        request["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)
        request = valid_request()
        del request["epoch"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)

    def test_nonfinite_and_out_of_range_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            request = valid_request()
            request["samples"][3] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)
        request = valid_request()
        request["samples"][0] = 4.5
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_bool_string_and_null_samples_rejected(self) -> None:
        for value in (True, "0.0", None):
            request = valid_request()
            request["samples"][0] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_geometry_lifecycle_and_target_rejected(self) -> None:
        cases = (
            ("sample_rate_hz", 48000),
            ("channels", 2),
            ("frame_samples", 320),
            ("epoch", -1),
            ("epoch", True),
            ("epoch", 1.0),
            ("first_input_sample", -160),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("execution_mode", 0),
            ("target_condition", "p360"),
            ("target_condition", "streaming_generic"),
            ("candidate", "dualvc3"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=key):
                reference.validate_request(request)

    def test_short_and_empty_sample_lists_rejected(self) -> None:
        for samples in ([0.0] * 159, []):
            request = valid_request()
            request["samples"] = samples
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 20)
        self.assertTrue(all(not case["accepted"] for case in data["cases"]))

    def test_valid_request_fails_closed_without_candidate(self) -> None:
        with self.assertRaises(reference.CandidateAbsent) as context:
            reference.probe_candidate(valid_request())
        self.assertEqual(context.exception.code,
                         "SOURCE_WEIGHTS_RUNTIME_ABSENT")
        self.assertIn("SOURCE_WEIGHTS_RUNTIME_ABSENT",
                      str(context.exception))


class ResetValidationTests(unittest.TestCase):
    def test_reset_cases_match_expectation(self) -> None:
        data = reference._reset_cases()
        self.assertTrue(data["matches_expectation"])
        self.assertFalse(data["state_owned"])
        self.assertEqual(data["accepted_count"],
                         data["expected_accepted_count"])
        self.assertEqual(data["accepted_count"], 1)
        self.assertIsNone(data["metrics"])

    def test_reset_accepts_only_strictly_increasing_epoch(self) -> None:
        accepted = reference.validate_reset(2, 0, 1)
        self.assertEqual(accepted["epoch"], 2)
        for args in ((1, 0, 1), (0, 0, 1), (-1, 0, 1), (2, -160, 1),
                     (True, 0, 1), (2, True, 1), (2.0, 0, 1)):
            with self.assertRaises(reference.EvidenceError, msg=str(args)):
                reference.validate_reset(*args)


class ProbeTests(unittest.TestCase):
    def test_source_is_absent(self) -> None:
        probe = reference.source_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_source_absent")
        self.assertIsNone(probe["revision"])
        self.assertIsNone(probe["tree_digest"])
        self.assertEqual(probe["found"], [])
        self.assertEqual(probe["name_search"]["match_count"], 0)
        self.assertFalse(probe["name_search"]["truncated"])
        self.assertGreater(probe["name_search"]["entries_scanned"], 0)

    def test_weights_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_weights_absent")
        self.assertIsNone(probe["sha256"])
        self.assertIsNone(probe["byte_count"])
        self.assertEqual(probe["found"], [])
        self.assertEqual(probe["home_cache"]["dualvc_matches"], [])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertFalse(probe["importable_modules"]["torch"])

    def test_geometry_is_deterministic_and_not_candidate(self) -> None:
        geometry = reference.geometry()
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["frame_ms"], 10.0)
        self.assertEqual(geometry["frames_per_second"], 100.0)
        self.assertFalse(geometry["candidate_geometry_documented"])
        self.assertIsNone(geometry["candidate_buffering_delay_samples"])
        self.assertFalse(geometry["measured_here"])
        self.assertFalse(geometry["candidate_output"])

    def test_historical_evidence_is_absent(self) -> None:
        history = reference.historical_evidence()
        self.assertEqual(history["status"],
                         "no_local_dualvc3_execution_record")
        self.assertEqual(history["records_found"], 0)
        self.assertIsNone(history["source_reported_results"])
        self.assertEqual(history["audio_artifacts"], [])
        self.assertFalse(history["reproduced_here"])
        self.assertFalse(history["qualifies_candidate"])

    def test_inventory_and_evidence_rows_are_exact(self) -> None:
        self.assertEqual(reference.inventory_link(),
                         reference.EXPECTED_INVENTORY)
        entry = reference.evidence_entry()
        self.assertEqual(entry["line"], 178)
        self.assertIn("no official runnable checkpoint found", entry["text"])
        self.assertIn("Streaming generic VC", entry["text"])
        self.assertIn("2406.07846", entry["text"])

    def test_stimulus_identity_is_bit_exact(self) -> None:
        probe = reference.stimulus_probe()
        self.assertFalse(probe["candidate_processing"])
        for block in probe["identity_control"].values():
            self.assertTrue(block["byte_identical"])
        for metrics in probe["stimuli"].values():
            self.assertEqual(metrics["nonfinite_count"], 0)
            self.assertLessEqual(metrics["peak_abs"],
                                 reference.MAX_ABS_STIMULUS)


class ReportTests(unittest.TestCase):
    def test_report_is_canonical_finite_and_stable(self) -> None:
        first = reference.report_bytes()
        second = reference.report_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertFalse(first.endswith(b"\n\n"))
        report = reference.strict_json_loads(first.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(report) + b"\n", first)
        self.assertTrue(reference.finite_json(report))

    def test_decision_and_qualification(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertEqual(report["qualification"]["readiness"], "incomplete")
        self.assertTrue(report["qualification"]["proposal_only"])
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertFalse(report["qualification"]["upstream_parity"])
        self.assertFalse(
            report["qualification"]["all_required_results_present"])

    def test_eight_release_gates_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["remaining_gates"], reference_gate_ids())
        self.assertEqual(report["gates"], reference_gate_ids())
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["release_gates"]))
        self.assertTrue(all(gate["reason"] and gate["reopen"]
                            for gate in report["release_gates"]))

    def test_candidate_and_required_results_do_not_qualify(self) -> None:
        report = reference.build_report()
        candidate = report["candidates"]["dualvc-3"]
        self.assertIsNone(candidate["metrics"])
        self.assertFalse(candidate["qualifies_candidate"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        for value in report["required_results"].values():
            self.assertNotIn(value, ("passed", "qualified", "measured"))

    def test_boundary_is_closed(self) -> None:
        boundary = reference.build_report()["boundary"]
        for key in (
            "benchmark_claim", "board_or_handoff_changed", "ci_changed",
            "descriptor_default_changed", "descriptor_registration",
            "enabled_by_default", "provider_registered",
            "public_api_abi_changed", "real_corpus_or_weights",
            "release_claim", "shared_cmake_changed",
        ):
            self.assertFalse(boundary[key], key)
        self.assertTrue(boundary["installed_v0_unchanged"])
        self.assertEqual(boundary["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
        })

    def test_voice_profile_mapping_is_blocked(self) -> None:
        mapping = reference.voice_profile_mapping()
        self.assertEqual(mapping["identity_and_similarity"],
                         "blocked_not_scored")
        self.assertEqual(mapping["naturalness"], "blocked_no_listening_or_mos")
        self.assertEqual(mapping["candidate_output"],
                         "blocked_source_weights_runtime_absent")
        self.assertEqual(mapping["exact_target_condition"],
                         "blocked_no_documented_target_voice_or_condition")
        for key, value in mapping.items():
            if key == "numerical_and_nonfinite":
                self.assertEqual(value, "partial_local_harness_only")
            else:
                self.assertTrue(value.startswith("blocked"), key)

    def test_board_projection_is_stable_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(digest,
                         reference.sha256_bytes(
                             reference.canonical_bytes(links)))
        self.assertNotIn(
            "audio-benchmark-platform/plan/swarm/TASKS.json",
            reference.SOURCE_PINS)

    def test_no_fabricated_artifact_digests(self) -> None:
        report = reference.build_report()
        blocker = report["upstream_blocker"]
        self.assertIsNone(blocker["source_digest"])
        self.assertIsNone(blocker["runtime_digest"])
        self.assertIsNone(blocker["pinned_revision"])
        self.assertIsNone(blocker["weights"]["sha256"])
        self.assertIsNone(blocker["weights"]["byte_count"])

    def test_missing_result_never_qualifies(self) -> None:
        missing = reference.missing_result("fixture")
        self.assertEqual(missing["status"], "blocked")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies_candidate"])


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

    def test_sibling_additions_after_base_pass_scope(self):
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

    def test_branch_out_of_scope_edit_fails_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-DUALVC-3-scope")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "out of scope edit")

            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))


def reference_gate_ids() -> list:
    return ["RG-0" + str(number) for number in range(1, 9)]


if __name__ == "__main__":
    unittest.main()
