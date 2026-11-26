# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the task-local Spiking-FullSubNet readiness package.

Standard library only. No source, checkpoint, runtime, audio or result is
loaded. Tests exercise canonicalisation, stable board projection, scope
regressions, absence probes, fail-closed declaration and committed DEFER bytes.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

PIN_LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)


def _init_repo(repo: Path, branch: str = "main") -> None:
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", branch, str(repo)], check=True)
    _git(repo, "config", "user.email", "evidence@example.invalid")
    _git(repo, "config", "user.name", "Evidence Test")


def _commit(repo: Path, relative: str, text: str) -> str:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(repo, "add", relative)
    result = _git(repo, "commit", "-q", "-m", "test: " + relative)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


class CanonicalTests(unittest.TestCase):
    def test_canonical_bytes_sorted_ascii(self):
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": [2, 3]}), b'{"a":[2,3],"b":1}')

    def test_canonical_rejects_float(self):
        with self.assertRaises(TypeError):
            reference.assert_no_float({"a": 1.5})

    def test_strict_json_rejections(self):
        result = reference.strict_json_rejections()
        self.assertEqual(result["case_count"], 10)
        self.assertTrue(all(case["rejected"] for case in result["cases"]))
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":NaN}')

    def test_canonical_round_trip(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        again, digest2 = reference.canonical_report(reference.loads_strict(text))
        self.assertEqual(text, again)
        self.assertEqual(digest, digest2)
        self.assertEqual(digest, hashlib.sha256(text.encode("ascii")).hexdigest())


class BoardIdentityTests(unittest.TestCase):
    def _rows(self, mutable: bool = False) -> dict:
        target = {
            "id": reference.TASK, "title": reference.TASK_TITLE, "component": reference.COMPONENT_ID,
            "mode": "feasibility", "repository": "audio-sdk", "depends_on": list(reference.DEPENDS_ON),
        }
        if mutable:
            target.update({"status": "in_progress", "owner": "someone", "claim": {"base_commit": "f" * 40}, "review": {}, "handoff": {}, "blocked_reason": "x", "dispatch_priority": 9})
        rows = [target]
        for i, rid in enumerate(reference.LINKED_ROW_IDS[1:]):
            rows.append({"id": rid, "title": "F%d" % i, "component": None, "mode": "foundation", "repository": "audio-sdk", "depends_on": []})
        return {"schema_version": 1, "tasks": rows}

    def _write(self, doc: dict) -> Path:
        d = Path(tempfile.mkdtemp(prefix="spiking-board-"))
        p = d / "TASKS.json"
        p.write_text(json.dumps(doc), encoding="utf-8")
        return p

    def test_projection_ignores_mutable_fields(self):
        stable = self._write(self._rows())
        mutable = self._write(self._rows(mutable=True))
        self.assertEqual(reference.board_row_projection(stable), reference.board_row_projection(mutable))
        self.assertEqual(reference.board_row_digest(reference.board_row_projection(stable)), reference.board_row_digest(reference.board_row_projection(mutable)))

    def test_projection_detects_stable_change(self):
        base = reference.board_row_projection(self._write(self._rows()))
        doc = self._rows()
        doc["tasks"][0]["title"] = "different"
        changed = reference.board_row_projection(self._write(doc))
        self.assertNotEqual(reference.board_row_digest(base), reference.board_row_digest(changed))

    def test_projection_rejects_component_mismatch(self):
        doc = self._rows()
        doc["tasks"][0]["component"] = "other"
        with self.assertRaises(ValueError):
            reference.board_row_projection(self._write(doc))

    def test_linked_rows_ordered(self):
        rows = reference.linked_rows(self._write(self._rows()))
        self.assertEqual(tuple(r["id"] for r in rows), reference.LINKED_ROW_IDS)

    def test_board_file_never_pinned(self):
        self.assertFalse(reference.build_report()["board_file_pinned"])
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW, reference.SOURCE_PINS)


class ScopeTests(unittest.TestCase):
    def test_newest_base_selects_sibling_merge(self):
        with tempfile.TemporaryDirectory(prefix="spiking-scope-") as raw:
            repo = Path(raw)
            _init_repo(repo)
            _commit(repo, "base.txt", "base\n")
            old_main = _git(repo, "rev-parse", "HEAD").stdout.strip()
            _git(repo, "checkout", "-q", "-b", "sibling")
            _commit(repo, "docs/task-evidence/other/README.md", "sibling\n")
            new_base = _git(repo, "rev-parse", "HEAD").stdout.strip()
            _git(repo, "update-ref", "refs/remotes/origin/main", new_base)
            _git(repo, "checkout", "-q", "-b", "feature", new_base)
            _commit(repo, reference.TASK_PREFIX + "README.md", "task\n")
            base = reference.scope_base(repo)
            self.assertEqual(base, new_base)
            self.assertNotEqual(base, old_main)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, [reference.TASK_PREFIX + "README.md"])
            self.assertEqual(reference.scope_violations(paths), [])

    def test_out_of_scope_branch_edit_reported(self):
        with tempfile.TemporaryDirectory(prefix="spiking-scope-") as raw:
            repo = Path(raw)
            _init_repo(repo)
            _commit(repo, "docs/task-evidence/other/README.md", "sibling\n")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "README.md", "task\n")
            _commit(repo, "docs/provider-intake.md", "out\n")
            base = reference.scope_base(repo)
            self.assertIsNotNone(base)
            self.assertEqual(reference.scope_violations(reference.scope_changed_paths(repo, base)), ["docs/provider-intake.md"])

    def test_missing_base_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="spiking-scope-") as raw:
            repo = Path(raw)
            _init_repo(repo, branch="feature")
            _commit(repo, "README.md", "no base\n")
            self.assertIsNone(reference.scope_base(repo))


class AbsenceTests(unittest.TestCase):
    def test_all_probes_absent(self):
        summary = reference.absence_summary()
        self.assertGreaterEqual(summary["probe_count"], 10)
        self.assertTrue(summary["all_absent"])

    def test_absence_detects_present_probe(self):
        probes = [{"kind": "home", "label": "fake", "path": "/fake", "present": True}]
        self.assertFalse(reference.absence_summary(probes)["all_absent"])


class DeclarationTests(unittest.TestCase):
    def test_control_accepted_not_qualifying(self):
        result = reference.declaration_control()
        self.assertTrue(result["accepted"])
        self.assertTrue(result["synthetic_schema_control"])
        self.assertFalse(result["qualifies"])
        self.assertFalse(result["opens_asset_bytes"])
        self.assertFalse(result["runtime_or_weights_invoked"])

    def test_rejections_all_rejected(self):
        result = reference.declaration_rejections()
        self.assertGreaterEqual(result["case_count"], 30)
        self.assertTrue(result["all_rejected"])

    def test_unknown_and_missing_fields(self):
        doc = reference._control_document()
        doc["extra"] = 1
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(doc)
        doc = reference._control_document()
        doc.pop("rights")
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(doc)

    def test_admission_not_admissible(self):
        adm = reference.admission()
        self.assertEqual(adm["status"], "DEFER")
        self.assertFalse(adm["admissible"])
        self.assertFalse(adm["runtime_or_weights_invoked"])


class EvidenceTests(unittest.TestCase):
    def test_snippets_present(self):
        presence = reference.evidence_presence()
        self.assertEqual(presence["snippet_count"], 4)
        self.assertTrue(presence["all_present"])

    def test_no_forbidden_payload_files(self):
        for path in HERE.iterdir():
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), reference.FORBIDDEN_SUFFIXES, path.name)


class ArtifactTests(unittest.TestCase):
    def test_contract_disposition(self):
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertTrue(contract["incomplete"])
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in contract["release_gates"]))
        self.assertFalse(contract["boundary"]["provider_registration"])
        self.assertFalse(contract["scope"]["weights_vendored"])
        self.assertEqual(contract["public_v0_geometry"]["sample_rate_hz"], 16000)
        self.assertEqual(contract["public_v0_geometry"]["frame_samples"], 160)

    def test_report_profile_and_qualification(self):
        report = reference.build_report()
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertFalse(report["qualification"]["real_result_present"])
        profile = report["enhancement_profile"]
        self.assertEqual(profile["row_summary"]["requirement_count"], 8)
        self.assertEqual(profile["row_summary"]["blocked_count"], 7)
        self.assertEqual(profile["row_summary"]["documented_count"], 1)
        self.assertFalse(profile["row_summary"]["profile_satisfied"])
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertTrue(all(not r["present"] and r["blocked"] for r in report["required_artifacts"]))
        self.assertFalse(report["candidate"]["locally_present"])

    def test_no_metric_promoted(self):
        report = reference.build_report()
        metrics = report["reported_metrics"]
        self.assertFalse(metrics["admitted_as_result"])
        self.assertFalse(metrics["qualifies"])
        self.assertIsNone(metrics["local_si_sdr"])
        self.assertIsNone(metrics["local_stoi"])

    def test_readme_digests(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"], len(reference.SOURCE_ARTIFACT_FILES))

    def test_committed_report_matches_canonical(self):
        report_path = HERE / "report.json"
        if not report_path.is_file():
            self.skipTest("report.json not generated yet")
        expected = reference.canonical_bytes(reference.build_report())
        self.assertEqual(report_path.read_bytes(), expected)
        digest = hashlib.sha256(expected).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, "%s  report.json\n" % digest)

    def test_committed_contract_matches_canonical(self):
        path = HERE / "contract.json"
        if not path.is_file():
            self.skipTest("contract.json not generated yet")
        self.assertEqual(path.read_bytes(), reference.canonical_bytes(reference.build_contract()))

    def test_sources_manifest(self):
        path = HERE / "SOURCES.sha256"
        if not path.is_file():
            self.skipTest("SOURCES.sha256 not generated yet")
        observed = {}
        for line in path.read_text(encoding="ascii").splitlines():
            if not line or line.startswith("#"):
                continue
            m = PIN_LINE.match(line)
            self.assertIsNotNone(m, line)
            observed[m.group(2)] = m.group(1)
        expected = {"source:" + k for k in reference.SOURCE_PINS}
        expected |= {"sdk:" + k for k in reference.BOUNDARY_PINS}
        expected |= {reference.TASK_PREFIX + name for name in reference.LOCAL_FILES if name != "SOURCES.sha256"}
        self.assertEqual(set(observed), expected)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", observed)
        for key, digest in observed.items():
            if key.startswith("source:"):
                actual = reference.sha256_file(reference.AUDIO_ROOT / key[len("source:"):])
            elif key.startswith("sdk:"):
                actual = reference.sha256_file(reference.WORKTREE / key[len("sdk:"):])
            else:
                actual = reference.sha256_file(HERE / key[len(reference.TASK_PREFIX):])
            self.assertEqual(actual, digest, key)


if __name__ == "__main__":
    unittest.main()
