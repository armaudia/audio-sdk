# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-SB-UFOGEN blocker evidence package."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import reference


def valid_request() -> dict:
    return {
        "candidate": "sb-ufogen",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
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
        self.assertEqual(validated["candidate"], "sb-ufogen")
        self.assertEqual(len(validated["samples"]), 160)

    def test_unknown_and_missing_fields_rejected(self) -> None:
        req = valid_request(); req["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(req)
        req = valid_request(); del req["epoch"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(req)

    def test_nonfinite_out_of_range_and_bad_types_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf"), 8.0, True, "0", None):
            req = valid_request(); req["samples"][0] = value
            with self.assertRaises((reference.InputError, reference.ConfigError)):
                reference.validate_request(req)

    def test_geometry_lifecycle_mode_rejected(self) -> None:
        cases = [
            ("sample_rate_hz", 48000), ("channels", 2), ("frame_samples", 320),
            ("epoch", -1), ("epoch", True), ("epoch", 1.0), ("first_input_sample", -1),
            ("lifecycle", "drained"), ("execution_mode", 4), ("candidate", "other"),
        ]
        for key, value in cases:
            req = valid_request(); req[key] = value
            with self.assertRaises(reference.EvidenceError, msg=key):
                reference.validate_request(req)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 20)

    def test_valid_request_fails_closed_without_candidate(self) -> None:
        with self.assertRaises(reference.CandidateAbsent) as ctx:
            reference.probe_candidate(valid_request())
        self.assertEqual(ctx.exception.code, "SOURCE_WEIGHTS_RUNTIME_ABSENT")


class ResetValidationTests(unittest.TestCase):
    def test_reset_cases_match_expectation(self) -> None:
        data = reference._reset_cases()
        self.assertTrue(data["matches_expectation"])
        self.assertFalse(data["state_owned"])
        self.assertEqual(data["accepted_count"], 1)

    def test_reset_accepts_only_strictly_increasing_epoch(self) -> None:
        self.assertEqual(reference.validate_reset(2, 0, 1)["epoch"], 2)
        for args in ((1, 0, 1), (0, 0, 1), (-1, 0, 1), (2, -1, 1), (True, 0, 1), (2, False, 1), (1.5, 0, 1)):
            with self.assertRaises(reference.EvidenceError):
                reference.validate_reset(*args)


class ProbeTests(unittest.TestCase):
    def test_source_weights_runtime_blocked(self) -> None:
        self.assertEqual(reference.source_probe()["status"], "blocked_source_absent")
        self.assertFalse(reference.source_probe()["official_repo_identified"])
        self.assertEqual(reference.weights_probe()["status"], "blocked_weights_absent")
        self.assertEqual(reference.runtime_probe()["status"], "blocked_runtime_unpinned")

    def test_geometry_and_inventory(self) -> None:
        g = reference.geometry()
        self.assertEqual((g["sample_rate_hz"], g["channels"], g["frame_samples"]), (16000, 1, 160))
        self.assertFalse(g["candidate_geometry_documented"])
        self.assertEqual(reference.inventory_link(), reference.EXPECTED_INVENTORY)

    def test_evidence_rows_are_exact(self) -> None:
        e = reference.evidence_entry()
        self.assertEqual(e["path"], reference.EVIDENCE_PATH)
        self.assertEqual([r["line"] for r in e["rows"]], [29, 85, 96])
        joined = "\n".join(r["text"] for r in e["rows"])
        self.assertIn("no usable official checkpoint/inference path was verified", joined)
        self.assertIn("han25b_interspeech.pdf", joined)

    def test_stimulus_identity(self) -> None:
        probe = reference.stimulus_probe()
        self.assertFalse(probe["candidate_processing"])
        for block in probe["identity_control"].values():
            self.assertTrue(block["byte_identical"])


class ReportTests(unittest.TestCase):
    def test_report_is_canonical_finite_and_stable(self) -> None:
        first = reference.report_bytes()
        second = reference.report_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        report = reference.strict_json_loads(first.decode("utf-8"))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertEqual(report["profile"]["name"], "room")

    def test_board_projection_excludes_mutable_fields(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(len(links), len(reference.LINKED_ROWS))
        self.assertTrue(all(set(row.keys()) == set(reference.LINK_FIELDS) for row in links))
        self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_blocker_semantics(self) -> None:
        report = reference.strict_json_loads(reference.report_bytes().decode("utf-8"))
        blocker = report["upstream_blocker"]
        self.assertEqual(blocker["status"], "blocked_source_weights_runtime_rights_absent")
        self.assertTrue(blocker["no_upstream_parity_claim"])
        self.assertEqual(blocker["source"]["status"], "absent")
        self.assertEqual(blocker["weights"]["status"], "absent")
        self.assertEqual(blocker["runtime"]["status"], "blocked_runtime_unpinned")


class ScopeTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def _repo(self, root: Path) -> Path:
        repo = root / "audio-sdk"; repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-fixture")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX; task.mkdir(parents=True)
        (task / "README.md").write_text("x\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "task")
        return repo

    def test_sibling_additions_after_base_pass_scope(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            historical = self._git(repo, "rev-parse", "HEAD")
            sib = repo / "docs/task-evidence/sibling"; sib.mkdir(parents=True)
            (sib / "x.txt").write_text("x\n", encoding="utf-8")
            self._git(repo, "add", "-A"); self._git(repo, "commit", "-qm", "sib")
            head = self._git(repo, "rev-parse", "HEAD")
            self.assertEqual(reference.scope_changed_paths(repo, head), [])
            self.assertEqual(reference.scope_violations([]), [])
            historic_paths = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling/x.txt", historic_paths)
            self.assertTrue(reference.scope_violations(historic_paths))

    def test_branch_out_of_scope_edit_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            base = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "checkout", "-q", "-b", "swarm/SDK-SB-UFOGEN-scope")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt"); self._git(repo, "commit", "-qm", "oos")
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths), ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))


if __name__ == "__main__":
    unittest.main()
