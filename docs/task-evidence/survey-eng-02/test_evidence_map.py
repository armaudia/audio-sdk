#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-SURVEY-ENG-02 evidence map.

The suite is read-only. It rebuilds the canonical report in memory, rechecks the
pins and sidecars, and asserts that the survey keeps historical, reported,
proposal and not-run outcomes behind the release boundary.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import build

HERE = Path(__file__).resolve().parent
WORKSPACE = build.find_workspace(build.SDK_ROOT)
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
SOURCES = HERE / "SOURCES.sha256"
README = HERE / "README.md"

ALLOWED_STATUSES = {
    "local_historical",
    "local_historical_model",
    "reported_only",
    "proposal_only",
    "not_run",
}


def strict_json(path: Path) -> dict:
    def reject(value: str) -> None:
        raise ValueError(f"nonfinite JSON constant: {value}")

    payload = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path.name}")
    return payload


class EvidenceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)
        cls.expected_bytes, cls.digests = build.build_report(WORKSPACE)

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(REPORT.read_bytes(), self.expected_bytes)

    def test_02_report_is_canonical(self) -> None:
        raw = REPORT.read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        self.assertEqual(build.canonical(json.loads(raw)), raw)

    def test_03_report_sidecar_matches(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_04_source_sidecar_matches_every_pin(self) -> None:
        expected = "".join(f"{self.digests[path]}  {path}\n" for path in sorted(self.digests))
        self.assertEqual(SOURCES.read_text(encoding="utf-8"), expected)
        for path, digest in self.digests.items():
            self.assertEqual(hashlib.sha256((WORKSPACE / path).read_bytes()).hexdigest(), digest)
        self.assertEqual(set(self.digests), set(build.PINS))

    def test_05_quotes_are_verbatim_in_pins(self) -> None:
        for path, quote in build.QUOTES:
            self.assertIn(quote, build.read_text(WORKSPACE, path), f"quote drifted in {path}")

    def test_06_sdk_pins_match_this_worktree(self) -> None:
        for sdk_path in (
            "CONTRACTS.md",
            "docs/evidence-handoff.md",
            "docs/task-evidence/duplex-clocks/README.md",
            "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md",
        ):
            pinned = WORKSPACE / "audio-benchmark-platform" / "audio-sdk" / sdk_path
            self.assertEqual(pinned.read_bytes(), (build.SDK_ROOT / sdk_path).read_bytes())

    def test_07_catalogue_matches_registry(self) -> None:
        registry = json.loads(build.read_text(WORKSPACE, "research/category_registry.json"))
        category = next(item for item in registry["categories"] if item["id"] == "ENG-02")
        self.assertEqual(self.report["catalogue"]["category"], category)
        self.assertEqual(category["scope"], "support")
        self.assertEqual(category["discovery_status"], "catalogued")
        self.assertEqual(category["candidate_census_status"], "not_started")
        self.assertEqual(category["benchmark_status"], "not_started")
        self.assertEqual(category["source_ids"], ["S27", "S41"])

    def test_08_source_leads_cover_registry_and_components(self) -> None:
        registry = json.loads(build.read_text(WORKSPACE, "research/category_registry.json"))
        sources = {item["id"]: item for item in registry["sources"]}
        inventory = json.loads(build.read_text(WORKSPACE, "audio-benchmark-platform/plan/INVENTORY.json"))
        components = {item["id"]: item for item in inventory["components"]}
        leads = self.report["source_leads"]
        self.assertEqual([lead["id"] for lead in leads], ["S27", "S41"])
        mapped: set[str] = set()
        for lead in leads:
            source = sources[lead["id"]]
            for key in ("title", "url", "researcher", "access_scope"):
                self.assertEqual(lead[key], source[key])
            self.assertTrue(lead["historical_executions"])
            self.assertTrue(lead["limits"])
            for component_id in lead["mapped_components"]:
                self.assertIn(component_id, components)
                mapped.add(component_id)
        recorded = {item["component_id"] for item in self.report["component_matches"]}
        self.assertEqual(recorded, set(build.COMPONENTS))
        self.assertTrue(mapped <= recorded | {"webrtc-apm-ns", "speex-resampler"})

    def test_09_component_matches_mirror_inventory(self) -> None:
        inventory = json.loads(build.read_text(WORKSPACE, "audio-benchmark-platform/plan/INVENTORY.json"))
        components = {item["id"]: item for item in inventory["components"]}
        for item in self.report["component_matches"]:
            record = components[item["component_id"]]
            for key in ("name", "task", "evidence_status", "verification_profile",
                        "repository", "disposition"):
                self.assertEqual(item[key], record[key])

    def test_10_classical_families_are_complete(self) -> None:
        classic = self.report["method_families"]["classic"]
        self.assertEqual(
            [entry["family"] for entry in classic["entries"]],
            ["Delay estimation", "Rate adjustment", "Drift compensation"],
        )
        for entry in classic["entries"]:
            for key in ("comparison_inputs", "controls", "assets",
                        "local_outcomes", "reported_outcomes", "limits",
                        "component_ids"):
                self.assertTrue(entry[key], f"{entry['family']} lacks {key}")
            for outcome in entry["local_outcomes"] + entry["reported_outcomes"]:
                self.assertIn(outcome["status"], ALLOWED_STATUSES)
                self.assertIn(outcome["pin"], build.PINS)

    def test_11_ml_family_is_audited_and_unowned(self) -> None:
        ml = self.report["method_families"]["ml"]
        self.assertTrue(ml["audited"])
        self.assertIn("Learned estimation is optional research, not required",
                      ml["catalogued_text"])
        self.assertEqual(ml["result"], "no_owned_estimator_component")
        self.assertEqual(ml["component_ids"], ["cagcrn-joint-aec-and-ns", "aecmos"])
        self.assertGreaterEqual(len(ml["missing_evidence"]), 3)
        self.assertTrue(any("No pinned ML source revision" in item for item in ml["missing_evidence"]))

    def test_12_coverage_audit_explains_missing_evidence(self) -> None:
        audit = self.report["coverage_audit"]
        self.assertTrue(audit["ml_family_audited"])
        self.assertTrue(audit["historical_executions_covered"])
        self.assertEqual(audit["source_leads_covered"], ["S27", "S41"])
        self.assertEqual(
            audit["classical_families_audited"],
            [entry["family"] for entry in self.report["method_families"]["classic"]["entries"]],
        )
        self.assertGreaterEqual(len(audit["missing_evidence_reasons"]), 5)

    def test_13_gap_is_feasibility_only_and_not_boarded(self) -> None:
        board = json.loads(build.read_text(WORKSPACE, "audio-benchmark-platform/plan/swarm/TASKS.json"))
        gap = self.report["gap"]
        self.assertEqual(gap["id"], build.GAP_ID)
        self.assertEqual(gap["status"], "proposed_unassigned_not_run")
        self.assertIsNone(gap["owner"])
        self.assertFalse(gap["board_entry"])
        self.assertFalse(any(item.get("id") == build.GAP_ID for item in board["tasks"]))
        self.assertIn("No real audio", gap["smallest_check"]["exclusions"])

    def test_14_prohibited_claims_stay_unmade(self) -> None:
        claims = self.report["prohibited_claims"]
        self.assertTrue(claims)
        self.assertEqual(set(claims.values()), {"not_made"})
        readme = README.read_text(encoding="utf-8").lower()
        for phrase in (
            "device qualification passed",
            "listening test passed",
            "release approved",
            "live clock drift implemented",
            "provider enabled by this survey",
            "abi changed by this survey",
        ):
            self.assertNotIn(phrase, readme)

    def test_15_readme_pins_current_digest(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertIn(digest, README.read_text(encoding="utf-8"))
        self.assertEqual(self.report["reproduction"]["python"], "3.12.16")
        self.assertEqual(self.report["reproduction"]["env"], "PYTHONDONTWRITEBYTECODE=1")

    def test_16_task_files_are_confined_to_scope(self) -> None:
        proc = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=build.SDK_ROOT, capture_output=True, text=True, check=True,
        )
        for line in proc.stdout.splitlines():
            if not line:
                continue
            path = line[3:]
            self.assertTrue(
                path == "docs/task-evidence/survey-eng-02" or
                path.startswith("docs/task-evidence/survey-eng-02/"),
                f"worktree change outside task scope: {path}",
            )

    def test_17_verifier_passes_end_to_end(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(HERE / "verify.py")],
            cwd=HERE, capture_output=True, text=True, check=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_18_disposition_is_machine_readable(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertFalse(self.report["qualification"]["qualifies"])
        self.assertEqual(len(self.report["release_gates"]), 8)
        self.assertTrue(all(gate["blocked"] for gate in self.report["release_gates"]))

    def test_19_mutable_board_is_not_a_full_file_pin(self) -> None:
        self.assertNotIn(build.BOARD_PATH, build.PINS)
        self.assertFalse(self.report["mutable_provenance"]["gate"])
        board = json.loads(build.read_text(WORKSPACE, build.BOARD_PATH))
        task = next(item for item in board["tasks"] if item["id"] == "SDK-SURVEY-ENG-02")
        projection = {field: task[field] for field in build.BOARD_PROJECTION_FIELDS}
        self.assertEqual(
            self.report["board_projection"],
            {
                "fields": list(build.BOARD_PROJECTION_FIELDS),
                "sha256": build.sha256_bytes(build.canonical(projection)),
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
