# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-WSOLA-REFERENCE blocker evidence package."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys_nonfinite_and_trailing(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1}x', '[1]', '\ufeff{"a":1}'):
            with self.assertRaises(reference.ReferenceError):
                reference.loads_strict(payload)

    def test_canonical_bytes_stable(self) -> None:
        value = {"b": [1, True, None], "a": "x"}
        payload = reference.canonical_bytes(value)
        self.assertEqual(payload, b'{"a":"x","b":[1,true,null]}')
        self.assertEqual(reference.object_digest(value), hashlib.sha256(payload).hexdigest())

    def test_no_floats(self) -> None:
        with self.assertRaises(TypeError):
            reference.assert_no_float({"v": 1.5})


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        for rel, digest in reference.SOURCE_PINS.items():
            p = reference.AUDIO_ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(reference.sha256_file(p), digest, rel)

    def test_boundary_pins_match(self) -> None:
        for rel, digest in reference.BOUNDARY_PINS.items():
            p = reference.SDK_ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(reference.sha256_file(p), digest, rel)

    def test_board_stable_identity_only(self) -> None:
        proj = reference.board_row_projection()
        self.assertEqual(proj["id"], reference.TASK)
        self.assertEqual(tuple(proj["depends_on"]), reference.DEPENDS_ON)
        digest = reference.board_row_digest(proj)
        self.assertEqual(len(digest), 64)
        report = reference.build_report()
        ident = report["task_row_identity"]
        self.assertFalse(ident["whole_file_hashed"])
        self.assertEqual(set(ident["excluded_mutable_fields"]), set(reference.MUTABLE_TASK_FIELDS))
        self.assertEqual(ident["stable_sha256"], digest)

    def test_snippets_present(self) -> None:
        result = reference.evidence_snippet_check()
        self.assertTrue(result["all_present"], result["checks"])
        self.assertGreaterEqual(result["count"], 6)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract(cls.report)

    def test_decision_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"], "incomplete")
        q = self.report["qualification"]
        self.assertTrue(q["not_qualified"])
        self.assertFalse(q["candidate_qualified"])
        self.assertTrue(q["all_release_gates_blocked"])
        self.assertTrue(q["no_missing_result_qualifies_candidate"])

    def test_gates_and_blockers(self) -> None:
        gates = self.report["gates"]
        self.assertEqual([g["id"] for g in gates], [f"RG-0{i}" for i in range(1, 9)])
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in gates))
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 4)
        self.assertEqual([b["id"] for b in blockers], [
            "elastic_output_contract_absent",
            "isolated_reference_runtime_absent",
            "rights_and_license_uncleared",
            "matched_rate_evidence_absent",
        ])
        for b in blockers:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])

    def test_boundary_scope_nonclaims(self) -> None:
        b = self.report["boundary"]
        for k in ("provider_registration", "default_selected", "public_api_abi_change", "installed_v0_behavior_change", "shared_build_or_ci_change", "network_used"):
            self.assertFalse(b[k], k)
        s = self.report["scope"]
        for k in ("real_audio", "listening", "device_timing", "benchmark_claim", "release_claim", "network_access", "download_attempted"):
            self.assertFalse(s[k], k)
        self.assertTrue(any("No missing results" in n or "Missing results" in n for n in self.report["non_claims"]))

    def test_rate_profile_blocked(self) -> None:
        rp = self.report["rate_profile"]
        self.assertFalse(rp["profile_satisfied"])
        self.assertEqual(rp["real_results"], 0)
        self.assertEqual(rp["synthetic_results"], 0)
        self.assertTrue(all(r["qualifies"] is False for r in rp["rows"]))
        self.assertTrue(rp["profile_source_check"]["all_phrases_present"])

    def test_contract_matches_report(self) -> None:
        self.assertEqual(self.contract["task"], reference.TASK)
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["qualification_status"], "not_qualified")
        self.assertEqual(self.contract["task_row_identity"]["stable_sha256"], self.report["task_row_identity"]["stable_sha256"])
        self.assertEqual(self.contract["gates"], self.report["gates"])
        self.assertEqual(self.contract["source_pins"], reference.SOURCE_PINS)

    def test_report_deterministic_and_no_floats(self) -> None:
        reference.assert_no_float(self.report)
        a = reference.canonical_report(self.report)
        b = reference.canonical_report(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(len(a[1]), 64)


class ArtifactTests(unittest.TestCase):
    def test_sources_bytes_cover_expected_files(self) -> None:
        payload = reference.sources_bytes().decode("ascii")
        self.assertIn("source:cpp-library/pipeline-validation/playback-speed-candidates.md", payload)
        self.assertIn("sdk:CONTRACTS.md", payload)
        self.assertIn("docs/task-evidence/wsola-reference/reference.py", payload)
        self.assertNotIn("plan/swarm/TASKS.json\"", payload)

    def test_spdx_headers(self) -> None:
        for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
            head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:5])
            self.assertIn(SPDX_LICENSE, head)
            self.assertIn("SPDX-FileCopyrightText:", head)
        for name in ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE, text)


class ScopeRegressionTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def _repo(self) -> Path:
        td = tempfile.TemporaryDirectory(prefix="wsola-ref-scope-")
        self.addCleanup(td.cleanup)
        repo = Path(td.name)
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "test")
        self._git(repo, "config", "user.email", "t@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        (repo / "README.md").write_text("base\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "base")
        return repo

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        repo = self._repo()
        self._git(repo, "switch", "-q", "-c", reference.BRANCH)
        f = repo / reference.TASK_PREFIX / "report.json"
        f.parent.mkdir(parents=True)
        f.write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "task")
        self._git(repo, "switch", "-q", "main")
        sib = repo / "docs/task-evidence/other/report.json"
        sib.parent.mkdir(parents=True)
        sib.write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "sibling")
        self._git(repo, "switch", "-q", reference.BRANCH)
        base = reference.scope_base(repo)
        self.assertIsNotNone(base)
        paths = reference.scope_changed_paths(repo, base)
        self.assertEqual(reference.scope_violations(paths), [])
        self.assertEqual(paths, [reference.TASK_PREFIX + "report.json"])

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        repo = self._repo()
        self._git(repo, "switch", "-q", "-c", reference.BRANCH)
        f = repo / reference.TASK_PREFIX / "report.json"
        f.parent.mkdir(parents=True)
        f.write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "task")
        (repo / "CMakeLists.txt").write_text("bad\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "bad")
        base = reference.scope_base(repo)
        self.assertIsNotNone(base)
        paths = reference.scope_changed_paths(repo, base)
        self.assertEqual(reference.scope_violations(paths), ["CMakeLists.txt"])

    def test_unresolved_base_and_outside_prefix_flagged(self) -> None:
        repo = self._repo()
        self._git(repo, "switch", "-q", "-c", "detached-work")
        self._git(repo, "branch", "-D", "main")
        self.assertIsNone(reference.scope_base(repo))
        self.assertEqual(reference.scope_violations([
            reference.TASK_PREFIX + "report.json",
            "docs/task-evidence/other/report.json",
        ]), ["docs/task-evidence/other/report.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
