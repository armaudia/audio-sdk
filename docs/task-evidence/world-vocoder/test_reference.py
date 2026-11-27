# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-WORLD-VOCODER evidence package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": NaN}')

    def test_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": Infinity}')

    def test_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"x": 1, "x": 2}')

    def test_rejects_bom(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"x": 1}')

    def test_rejects_non_object_root(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('[1]')

    def test_canonical(self):
        self.assertEqual(reference.canonical_text({"b": 2, "a": 1}), '{"a":1,"b":2}\n')

    def test_canonical_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.canonical_text({"x": float("nan")})

    def test_no_floats(self):
        with self.assertRaises(ValueError):
            reference._no_floats({"a": 1.5})
        reference._no_floats({"a": [1, None, True, "x"]})


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = reference.build_contract()

    def test_identity(self):
        c = self.contract
        self.assertEqual(c["task"], "SDK-WORLD-VOCODER")
        self.assertEqual(c["component"], "world-vocoder")
        self.assertEqual(c["mode"], "feasibility")
        self.assertEqual(c["decision"], "DEFER")
        self.assertEqual(c["status"], "incomplete")
        self.assertEqual(c["qualification_status"], "not_qualified")
        self.assertTrue(c["proposal_only"])

    def test_board_not_pinned(self):
        self.assertFalse(self.contract["board_file_pinned"])
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)
        self.assertEqual(self.contract["board_row_sha256"], reference.board_row_digest(reference.BOARD_ROW_PROJECTION))

    def test_gates_blockers_artifacts(self):
        gates = self.contract["release_gates"]
        self.assertEqual([g["id"] for g in gates], [f"RG-{i:02d}" for i in range(1, 9)])
        for g in gates:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
            self.assertEqual(g["linked_row"], reference.BOARD_ROW_PROJECTION)
            self.assertTrue(g["reopen_condition"])
        arts = self.contract["required_artifacts"]
        self.assertEqual(len(arts), 6)
        self.assertTrue(arts[0]["present"] and arts[0]["verified"] and not arts[0]["blocked"])
        for a in arts[1:]:
            self.assertFalse(a["present"])
            self.assertFalse(a["verified"])
            self.assertTrue(a["blocked"])
            self.assertIsNone(a["sha256"])
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 5)
        for b in blockers:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])
            self.assertTrue(b["required_action"])

    def test_voice_and_scope(self):
        self.assertEqual(len(self.contract["voice_profile_requirements"]), 8)
        self.assertEqual(len(self.contract["quality_outcomes"]), 4)
        self.assertEqual(len(self.contract["timing_requirements"]), 4)
        for r in self.contract["voice_profile_requirements"]:
            self.assertEqual(r["status"], "blocked")
        for k, v in self.contract["scope"].items():
            self.assertIs(v, True if k == "task_local_only" else False, k)
        for k, v in self.contract["boundary"].items():
            self.assertIs(v, True if k == "task_local_only" else False, k)

    def test_validate_contract(self):
        reference.validate_contract(self.contract)
        bad = dict(self.contract, decision="PASS")
        with self.assertRaises(ValueError):
            reference.validate_contract(bad)


class AdmissionTests(unittest.TestCase):
    def test_control_accepted(self):
        r = reference.validate_manifest(reference._manifest_control(), probe_paths=False)
        self.assertTrue(r["accepted"])
        self.assertFalse(r["qualifies"])

    def test_adverse_matrix(self):
        matrix = reference.admission_controls()
        self.assertTrue(matrix["control"]["accepted"])
        self.assertFalse(matrix["control"]["qualifies"])
        self.assertEqual(matrix["control"]["evidence_class"], "synthetic_schema_control_not_evidence")
        self.assertGreaterEqual(len(matrix["cases"]), 100)
        ids = [c["id"] for c in matrix["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        for c in matrix["cases"]:
            self.assertEqual(c["status"], "rejected", c["id"])
            self.assertFalse(c["qualifies"])
            self.assertTrue(c["state_unchanged"])
            self.assertTrue(c["code"])
        s = matrix["summary"]
        self.assertEqual(s["rejected_count"], s["case_count"])
        self.assertEqual(s["qualifying_results"], 0)
        self.assertEqual(s["accepted_schema_controls"], 1)
        for k in ("state_advanced_on_rejection", "runtime_invoked", "audio_read", "feature_input_read", "weights_loaded", "model_executed", "network_used"):
            self.assertFalse(s[k])

    def test_root_and_nonfinite(self):
        for payload in ([], None, "x", 7, True):
            self.assertFalse(reference.validate_manifest(payload, probe_paths=False)["accepted"])
        d = reference._manifest_control(); d["outcomes"]["intelligibility_wer"] = float("nan")
        r = reference.validate_manifest(d, probe_paths=False)
        self.assertFalse(r["accepted"])

    def test_key_rejections(self):
        checks = [
            ("missing-rights", lambda d: d.pop("rights"), "missing_field"),
            ("unknown-top", lambda d: d.__setitem__("extra", 1), "unknown_field"),
            ("wrong-rev", lambda d: d["source"].__setitem__("revision", "A" * 40), "invalid_value"),
            ("path-trav", lambda d: d["features"][0].__setitem__("path", "/a/../b.npy"), "invalid_path"),
            ("dup-feature", lambda d: d["features"].append(dict(d["features"][0])), "invalid_value"),
            ("bad-kind", lambda d: d["features"][0].__setitem__("feature_kind", "bad"), "invalid_value"),
            ("controls-missing-kind", lambda d: d.__setitem__("controls", [r for r in d["controls"] if r["kind"] != "zero_features"]), "invalid_value"),
            ("matched-unknown", lambda d: d["controls"][0].__setitem__("feature_id", "feat-missing"), "invalid_value"),
            ("zero-with-id", lambda d: d["controls"][2].__setitem__("feature_id", "feat-a"), "invalid_value"),
            ("wer-high", lambda d: d["outcomes"].__setitem__("intelligibility_wer", 1.1), "invalid_value"),
            ("nonfinite-count", lambda d: d["outcomes"].__setitem__("nonfinite_count", 1), "invalid_value"),
            ("panel-bool", lambda d: d["rights"].__setitem__("listening_panel_size", True), "invalid_value"),
        ]
        for name, fn, code in checks:
            d = reference._manifest_control(); fn(d)
            r = reference.validate_manifest(d, probe_paths=False)
            self.assertEqual(r["code"], code, name)
            self.assertFalse(r["accepted"], name)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = reference.build_report()

    def test_deterministic_no_floats(self):
        again = reference.build_report()
        self.assertEqual(reference.canonical_bytes(self.report), reference.canonical_bytes(again))
        reference._no_floats(self.report)

    def test_disposition_and_contract(self):
        r = self.report
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertTrue(r["proposal_only"])
        self.assertEqual(r["contract_sha256"], reference.object_digest(reference.build_contract()))

    def test_absence(self):
        s = self.report["absence_evidence"]["summary"]
        self.assertEqual(s["present_count"], 0)
        self.assertTrue(s["all_probes_absent"])
        for k in ("download_attempted", "network_used", "recursive_workspace_walk", "source_or_runtime_imported", "weights_loaded", "model_executed", "audio_read", "feature_input_read"):
            self.assertFalse(s[k], k)


class ScopeBaseTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        import subprocess
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def _commit(self, repo: Path, rel: str, content: str, msg: str) -> str:
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self._git(repo, "add", rel)
        self._git(repo, "commit", "-q", "-m", msg)
        return self._git(repo, "rev-parse", "HEAD")

    def _repo(self, path: Path) -> None:
        self._git(path, "init", "-q", "-b", "main")
        self._git(path, "config", "user.email", "test@example.invalid")
        self._git(path, "config", "user.name", "Test User")
        self._commit(path, "seed.txt", "seed\n", "seed")

    def test_scope_prefers_newest_merge_base_origin_main(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base_a = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "checkout", "-q", "-b", "base-b")
            base_b = self._commit(repo, "base-b.txt", "b\n", "newer base")
            self._git(repo, "update-ref", "refs/remotes/origin/main", base_b)
            self._git(repo, "branch", "-f", "main", base_a)
            self._git(repo, "checkout", "-q", "-b", "feature")
            self._commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base_b)
            changed = reference.scope_changed_paths(repo, base_b)
            self.assertEqual(reference.scope_violations(changed), [])

    def test_scope_falls_back_to_main_when_origin_main_unavailable(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "checkout", "-q", "-b", "feature")
            self._commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base)
            self.assertIsNone(reference.scope_base(repo, ("origin/main",)))

    def test_scope_out_of_scope_and_missing_base_fail_closed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._repo(repo)
            base = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "checkout", "-q", "-b", "feature")
            self._commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task only")
            self._commit(repo, "CONTRACTS.md", "changed\n", "out of scope")
            changed = reference.scope_changed_paths(repo, base)
            self.assertEqual(reference.scope_violations(changed), ["CONTRACTS.md"])
            self.assertIsNone(reference.scope_base(repo, ("missing-one", "missing-two")))


if __name__ == "__main__":
    unittest.main()
