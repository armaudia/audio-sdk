# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the task-local DiffSE readiness package.

Standard library only. No DiffSE source, checkpoint, input-SNR estimator,
runtime, audio or result is loaded. The tests exercise canonicalisation, the
stable board projection, three scope regression cases, absence probes, the
fail-closed caller declaration and the committed DEFER bytes.
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


def _git(repo: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *arguments],
                          capture_output=True, text=True, check=False)


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
    def test_canonical_bytes_are_ascii_and_sorted(self):
        payload = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        self.assertEqual(payload, b'{"a":[2,3],"b":1}')
        self.assertIsInstance(payload, bytes)

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
        document = reference.build_report()
        text, digest = reference.canonical_report(document)
        again, again_digest = reference.canonical_report(
            reference.loads_strict(text))
        self.assertEqual(text, again)
        self.assertEqual(digest, again_digest)
        self.assertEqual(digest, hashlib.sha256(text.encode("ascii")).hexdigest())


class BoardIdentityTests(unittest.TestCase):
    def _rows(self, mutable: bool = False) -> dict:
        target = {
            "id": reference.TASK,
            "title": reference.TASK_TITLE,
            "component": reference.COMPONENT_ID,
            "mode": "feasibility",
            "repository": "audio-sdk",
            "depends_on": list(reference.DEPENDS_ON),
        }
        if mutable:
            target.update({
                "status": "in_progress",
                "owner": "someone-else",
                "claim": {"base_commit": "f" * 40},
                "review": {"status": "requested"},
                "handoff": {"path": "x"},
                "blocked_reason": "mutable",
                "dispatch_priority": 99,
            })
        rows = {reference.TASK: target}
        for index, identifier in enumerate(reference.LINKED_ROW_IDS[1:]):
            rows[identifier] = {
                "id": identifier,
                "title": "Foundation %d" % index,
                "component": None,
                "mode": "foundation",
                "repository": "audio-sdk",
                "depends_on": [],
            }
        return {"schema_version": 1, "tasks": list(rows.values())}

    def _write(self, document: dict) -> Path:
        directory = Path(tempfile.mkdtemp(prefix="diffse-board-"))
        path = directory / "TASKS.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_projection_ignores_mutable_fields(self):
        stable = self._write(self._rows())
        mutable = self._write(self._rows(mutable=True))
        self.assertEqual(reference.board_row_projection(stable),
                         reference.board_row_projection(mutable))
        self.assertEqual(reference.board_row_digest(
            reference.board_row_projection(stable)),
            reference.board_row_digest(
                reference.board_row_projection(mutable)))

    def test_projection_detects_stable_change(self):
        baseline = reference.board_row_projection(self._write(self._rows()))
        document = self._rows()
        document["tasks"][0]["title"] = "different title"
        changed = reference.board_row_projection(self._write(document))
        self.assertNotEqual(reference.board_row_digest(baseline),
                            reference.board_row_digest(changed))

    def test_projection_rejects_component_mismatch(self):
        document = self._rows()
        document["tasks"][0]["component"] = "other-component"
        with self.assertRaises(ValueError):
            reference.board_row_projection(self._write(document))

    def test_linked_rows_are_stable_and_ordered(self):
        rows = reference.linked_rows(self._write(self._rows()))
        self.assertEqual(tuple(row["id"] for row in rows),
                         reference.LINKED_ROW_IDS)
        self.assertEqual(reference.linked_rows_digest(rows),
                         reference.object_digest(list(rows)))

    def test_board_file_is_never_pinned(self):
        self.assertFalse(reference.build_report()["board_file_pinned"])
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW,
                         reference.SOURCE_PINS)


class ScopeTests(unittest.TestCase):
    def test_newest_base_selects_sibling_merge(self):
        with tempfile.TemporaryDirectory(prefix="diffse-scope-") as raw:
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

    def test_out_of_scope_branch_edit_is_reported(self):
        with tempfile.TemporaryDirectory(prefix="diffse-scope-") as raw:
            repo = Path(raw)
            _init_repo(repo)
            _commit(repo, "docs/task-evidence/other/README.md", "sibling\n")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "README.md", "task\n")
            _commit(repo, "docs/provider-intake.md", "out of scope\n")
            base = reference.scope_base(repo)
            self.assertIsNotNone(base)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(reference.scope_violations(paths),
                             ["docs/provider-intake.md"])

    def test_missing_base_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="diffse-scope-") as raw:
            repo = Path(raw)
            _init_repo(repo, branch="feature")
            _commit(repo, "README.md", "no base\n")
            self.assertIsNone(reference.scope_base(repo))


class AbsenceTests(unittest.TestCase):
    def test_all_probes_absent(self):
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 19)
        self.assertTrue(summary["all_absent"])
        self.assertEqual(summary["present"], [])

    def test_absence_detects_present_probe(self):
        probes = [{"kind": "home", "label": "fake", "path": "/fake",
                   "present": True}]
        self.assertFalse(reference.absence_summary(probes)["all_absent"])


class DeclarationTests(unittest.TestCase):
    def test_control_accepted_but_not_qualifying(self):
        result = reference.declaration_control()
        self.assertTrue(result["accepted"])
        self.assertTrue(result["synthetic_schema_control"])
        self.assertFalse(result["qualifies"])
        self.assertFalse(result["opens_asset_bytes"])
        self.assertFalse(result["runtime_or_weights_invoked"])

    def test_every_mutation_is_rejected(self):
        result = reference.declaration_rejections()
        self.assertGreaterEqual(result["case_count"], 30)
        self.assertTrue(all(case["rejected"] for case in result["cases"]))

    def test_geometry_and_runtime_rejections(self):
        for identifier in ("geometry_rate_mismatch", "geometry_frame_mismatch",
                           "runtime_python_mismatch", "sampler_kind_mismatch",
                           "snr_estimator_name_mismatch"):
            with self.subTest(identifier=identifier):
                case = next(item for item in reference.declaration_rejections()[
                    "cases"] if item["id"] == identifier)
                self.assertTrue(case["rejected"])

    def test_nonfinite_and_float_rejected(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":NaN}')
        with self.assertRaises(TypeError):
            reference.assert_no_float({"a": 1.25})

    def test_unknown_and_missing_fields_rejected(self):
        document = reference._control_document()
        document["extra"] = 1
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(document)
        document = reference._control_document()
        document.pop("rights")
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(document)

    def test_admission_has_no_admitting_branch(self):
        result = reference.admission()
        self.assertEqual(result["status"], "DEFER")
        self.assertFalse(result["admissible"])
        self.assertTrue(result["blockers"])


class EvidenceTests(unittest.TestCase):
    def test_source_pins_match(self):
        for relative, expected in reference.SOURCE_PINS.items():
            self.assertEqual(
                reference.sha256_file(reference.AUDIO_ROOT / relative),
                expected, relative)
        for relative, expected in reference.BOUNDARY_PINS.items():
            self.assertEqual(
                reference.sha256_file(reference.WORKTREE / relative),
                expected, relative)

    def test_inventory_record(self):
        record = reference.inventory_record()
        self.assertEqual(record["id"], reference.COMPONENT_ID)
        self.assertEqual(record["verification_profile"], "enhancement")
        self.assertEqual(record["evidence_status"], "considered")
        self.assertEqual(record["evidence_line"], 36)
        self.assertEqual(record["evidence_record_name"],
                         reference.CANDIDATE_NAME)

    def test_profile_row(self):
        check = reference.profile_row_check()
        self.assertTrue(check["unique_row"])
        self.assertTrue(check["all_phrases_present"])
        self.assertEqual(check["row_count"], 1)

    def test_snippets_are_present(self):
        presence = reference.evidence_presence()
        self.assertEqual(presence["snippet_count"], 4)
        for snippet in presence["snippets"]:
            self.assertTrue(snippet["contains"])

    def test_no_forbidden_payload_files(self):
        for path in HERE.iterdir():
            if path.is_file():
                self.assertNotIn(path.suffix.lower(),
                                 reference.FORBIDDEN_SUFFIXES, path.name)


class ArtifactTests(unittest.TestCase):
    def test_contract_disposition(self):
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertTrue(contract["incomplete"])
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["release_gates"]))
        self.assertFalse(contract["boundary"]["provider_registration"])
        self.assertFalse(contract["scope"]["weights_vendored"])
        self.assertEqual(contract["public_v0_geometry"]["sample_rate_hz"],
                         16000)
        self.assertEqual(contract["public_v0_geometry"]["frame_samples"], 160)

    def test_report_profile_and_qualification(self):
        report = reference.build_report()
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["real_result_present"])
        profile = report["enhancement_profile"]
        self.assertEqual(profile["row_summary"]["requirement_count"], 8)
        self.assertEqual(profile["row_summary"]["blocked_count"], 7)
        self.assertEqual(profile["row_summary"]["documented_count"], 1)
        self.assertFalse(profile["row_summary"]["profile_satisfied"])
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertEqual(len(report["required_artifacts"]), 7)
        self.assertTrue(all(not row["present"] and row["blocked"]
                            for row in report["required_artifacts"]))
        self.assertFalse(report["recorded_identity"]["locally_present"])

    def test_no_metric_promoted(self):
        report = reference.build_report()
        metrics = report["reported_metrics"]
        self.assertIn("+0.12 PESQ", metrics["source_reported_pesq_delta"])
        self.assertFalse(metrics["admitted_as_result"])
        self.assertFalse(metrics["qualifies"])
        self.assertIsNone(metrics["local_pesq"])
        self.assertIsNone(metrics["local_stoi"])
        for key in ("candidate", "upstream_record"):
            self.assertFalse(report[key]["admitted_as_result"])
            self.assertIsNone(report[key]["checkpoint_sha256"])
            self.assertIsNone(report[key]["reported_sample_rate_hz"])

    def test_readme_digests(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"],
                         len(reference.SOURCE_ARTIFACT_FILES))

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
        self.assertEqual(path.read_bytes(),
                         reference.canonical_bytes(
                             reference.build_contract()))

    def test_sources_manifest(self):
        path = HERE / "SOURCES.sha256"
        if not path.is_file():
            self.skipTest("SOURCES.sha256 not generated yet")
        observed: dict[str, str] = {}
        for line in path.read_text(encoding="ascii").splitlines():
            if not line or line.startswith("#"):
                continue
            match = PIN_LINE.match(line)
            self.assertIsNotNone(match, line)
            observed[match.group(2)] = match.group(1)
        expected = {"source:" + key for key in reference.SOURCE_PINS}
        expected |= {"sdk:" + key for key in reference.BOUNDARY_PINS}
        expected |= {reference.TASK_PREFIX + name
                     for name in reference.LOCAL_FILES
                     if name != "SOURCES.sha256"}
        self.assertEqual(set(observed), expected)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", observed)
        for key, digest in observed.items():
            if key.startswith("source:"):
                actual = reference.sha256_file(
                    reference.AUDIO_ROOT / key[len("source:"):])
            elif key.startswith("sdk:"):
                actual = reference.sha256_file(
                    reference.WORKTREE / key[len("sdk:"):])
            else:
                actual = reference.sha256_file(
                    HERE / key[len(reference.TASK_PREFIX):])
            self.assertEqual(actual, digest, key)


if __name__ == "__main__":
    unittest.main()
